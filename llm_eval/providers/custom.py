"""Generic HTTP provider for chatbots without an official SDK.

Reads the request shape (URL, method, headers, body template) from the
:class:`~llm_eval.config.ProviderSettings`, substitutes the prompt into the
template, fires the call via ``httpx``, and extracts the response text using
a dot-notation path. Designed so that an external chatbot can be plugged in
purely via configuration, without any code change.
"""

from __future__ import annotations

import copy
import logging
import time
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

import httpx

from llm_eval.providers._retry import (
    FatalError,
    RateLimitError,
    TransientError,
    retry_with_backoff,
)
from llm_eval.providers._retry import (
    TimeoutError as ProviderTimeoutError,
)
from llm_eval.providers.base import BaseProvider, ProviderConfig, ProviderResponse

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_SECONDS = 30.0


class CustomProvider(BaseProvider):
    """Provider that talks to any chatbot reachable via a configurable HTTP call.

    Differs from the SDK-backed providers in that it does not assume a
    specific request/response shape: callers must supply a ``request_template``
    (with ``{prompt}`` placeholders) and a ``response_path`` to extract the
    answer from the JSON payload returned by the endpoint.

    Attributes:
        url: Endpoint URL.
        method: HTTP verb (defaults to ``POST``).
        headers: Static headers, with ``${VAR}`` already resolved by config.
        request_template: Body template; ``{prompt}`` is replaced before send.
        response_path: Dot-notation path into the JSON response.
    """

    def __init__(
        self,
        config: ProviderConfig,
        *,
        url: str,
        request_template: dict[str, Any] | None = None,
        response_path: str = "response",
        method: str = "POST",
        headers: Mapping[str, str] | None = None,
        http_client: httpx.Client | None = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
    ) -> None:
        """Initialize the custom HTTP provider.

        Args:
            config: Standard provider config (model name, max_tokens, etc.).
            url: Endpoint URL to call.
            request_template: Dict template for the request body. ``{prompt}``
                tokens (anywhere in the structure, including nested values)
                are substituted with the actual prompt at send time.
            response_path: Dot-notation path used to walk the JSON response
                and extract the assistant's answer.
            method: HTTP verb. Defaults to ``"POST"``.
            headers: Optional static headers.
            http_client: Optional pre-built ``httpx.Client``. ``None`` builds
                a fresh client per provider with the supplied ``timeout``.
            timeout: Request timeout in seconds (used only when building the
                default client).
            max_attempts: Retry attempts for transient errors.
            initial_delay: Seconds to wait before the second attempt.
        """
        super().__init__(config)
        if not url:
            raise ValueError("CustomProvider requires a non-empty 'url'")
        self.url = url
        self.method = method.upper()
        self.headers: dict[str, str] = dict(headers or {})
        self.request_template = request_template or {"prompt": "{prompt}"}
        self.response_path = response_path
        self._owns_client = http_client is None
        self._client = http_client or httpx.Client(timeout=timeout)
        self._max_attempts = max_attempts
        self._initial_delay = initial_delay

    def send(self, prompt: str) -> ProviderResponse:
        """Send the prompt to the configured endpoint and return the answer."""
        body = _substitute_prompt(self.request_template, prompt)

        def _call() -> ProviderResponse:
            start = time.perf_counter()
            try:
                response = self._client.request(
                    method=self.method,
                    url=self.url,
                    headers=self.headers or None,
                    json=body,
                )
            except httpx.TimeoutException as exc:
                raise ProviderTimeoutError(f"Custom provider timeout: {exc}") from exc
            except httpx.HTTPError as exc:
                raise TransientError(f"Custom provider HTTP error: {exc}") from exc

            elapsed_ms = (time.perf_counter() - start) * 1000.0

            if response.status_code == 429:
                raise RateLimitError(
                    f"Custom provider rate-limited (HTTP 429): {response.text[:200]}"
                )
            if 500 <= response.status_code < 600:
                raise TransientError(
                    f"Custom provider {response.status_code}: {response.text[:200]}"
                )
            if response.status_code >= 400:
                raise FatalError(f"Custom provider {response.status_code}: {response.text[:200]}")

            try:
                payload = response.json()
            except ValueError as exc:
                raise FatalError(
                    f"Custom provider returned non-JSON response: {response.text[:200]}"
                ) from exc

            text = _extract_by_path(payload, self.response_path)
            return ProviderResponse(
                response_text=text,
                model=self.config.model,
                timestamp=datetime.now(timezone.utc),
                response_time_ms=elapsed_ms,
                parameters={
                    "temperature": self.config.temperature,
                    "max_tokens": self.config.max_tokens,
                    "url": self.url,
                    "method": self.method,
                },
                raw_response=payload if isinstance(payload, dict) else {"value": payload},
            )

        return retry_with_backoff(
            _call,
            max_attempts=self._max_attempts,
            initial_delay=self._initial_delay,
        )

    def close(self) -> None:
        """Close the underlying HTTP client when this provider owns it."""
        if self._owns_client:
            self._client.close()


def build_from_settings(
    *,
    type: str,  # noqa: A002  - mirrors ProviderSettings field name
    api_key: str | None,
    model: str,
    temperature: float,
    max_tokens: int,
    url: str | None,
    method: str,
    headers: Mapping[str, str],
    request_template: dict[str, Any] | None,
    response_path: str | None,
    http_client: httpx.Client | None = None,
) -> CustomProvider:
    """Build a :class:`CustomProvider` from the fields of ``ProviderSettings``.

    Centralizes the validation needed when consuming user-facing config:
    custom providers require ``url`` and ``response_path`` even though those
    are ``Optional`` on the settings model.
    """
    if type != "custom":
        raise ValueError(f"build_from_settings expected type='custom', got '{type}'")
    if not url:
        raise ValueError("Custom provider requires 'url' in configuration")
    if not response_path:
        raise ValueError("Custom provider requires 'response_path' in configuration")

    return CustomProvider(
        ProviderConfig(
            api_key=api_key or "",
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        ),
        url=url,
        request_template=request_template,
        response_path=response_path,
        method=method,
        headers=headers,
        http_client=http_client,
    )


def _substitute_prompt(template: Any, prompt: str) -> Any:
    """Walk ``template`` recursively and replace ``{prompt}`` tokens.

    The template may contain strings (substituted in-place) or nested dicts
    and lists (recursed into). All other types are returned untouched.
    """
    if isinstance(template, str):
        return template.replace("{prompt}", prompt)
    if isinstance(template, dict):
        return {k: _substitute_prompt(v, prompt) for k, v in template.items()}
    if isinstance(template, list):
        return [_substitute_prompt(item, prompt) for item in template]
    return copy.copy(template)


def _extract_by_path(payload: Any, path: str) -> str:
    """Walk a dot-notation path into a JSON payload and return the leaf as str.

    Numeric segments index into lists. Missing keys raise :class:`FatalError`
    so the caller surfaces a clear configuration mistake.
    """
    cursor: Any = payload
    for segment in path.split("."):
        if isinstance(cursor, list):
            try:
                idx = int(segment)
            except ValueError as exc:
                raise FatalError(
                    f"Response path segment '{segment}' is not an int but cursor is a list"
                ) from exc
            try:
                cursor = cursor[idx]
            except IndexError as exc:
                raise FatalError(
                    f"Response path index {idx} out of range at segment '{segment}'"
                ) from exc
        elif isinstance(cursor, dict):
            if segment not in cursor:
                raise FatalError(
                    f"Response path segment '{segment}' not found "
                    f"(available keys: {sorted(cursor.keys())})"
                )
            cursor = cursor[segment]
        else:
            raise FatalError(f"Cannot descend into {type(cursor).__name__} at segment '{segment}'")
    return str(cursor) if cursor is not None else ""
