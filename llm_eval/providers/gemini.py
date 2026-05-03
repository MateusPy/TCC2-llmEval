"""Google Gemini provider implementation.

Wraps the ``google-generativeai`` SDK behind the :class:`BaseProvider`
contract. Network calls are funneled through :func:`retry_with_backoff` so
rate limits (429) and transient 5xx responses are handled consistently with
the other providers.

The SDK client is injected via ``client_factory`` to keep the import side
effects out of unit tests and to allow stubbing in :mod:`tests.test_providers`.

.. warning::

    The ``google-generativeai`` SDK uses **process-global authentication**
    via :func:`genai.configure`. As a consequence, instantiating multiple
    :class:`GeminiProvider` objects with different API keys in the same
    process will cause the most-recently-built client to overwrite the
    credentials of any earlier ones — and subsequent calls on the older
    instances will route through the new key. The default factory logs a
    warning when this happens. If your deployment needs concurrent
    Gemini-backed providers with different keys (e.g. a chatbot under
    test plus a judge), use the same key for both or move one of them
    to a different process.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

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


class GeminiProvider(BaseProvider):
    """Provider for Google Gemini models via ``google-generativeai`` SDK.

    Attributes:
        config: Provider configuration with ``api_key``, ``model`` etc.
    """

    def __init__(
        self,
        config: ProviderConfig,
        *,
        client_factory: Callable[[ProviderConfig], Any] | None = None,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        sleep: Callable[[float], None] | None = None,
    ) -> None:
        """Initialize the Gemini provider.

        Args:
            config: Provider configuration.
            client_factory: Callable that builds the underlying SDK model
                instance. ``None`` uses the default Gemini SDK; tests can
                inject a stub returning an object with ``generate_content``.
            max_attempts: Maximum retry attempts for transient errors.
            initial_delay: Seconds to wait before the second attempt.
            sleep: Sleep function passed to :func:`retry_with_backoff`.
                ``None`` defaults to :func:`time.sleep`. Tests should pass a
                no-op to avoid real waits during retry exercises.
        """
        super().__init__(config)
        self._client_factory = client_factory or _default_client_factory
        self._max_attempts = max_attempts
        self._initial_delay = initial_delay
        self._sleep = sleep
        self._client = self._client_factory(config)

    def send(self, prompt: str) -> ProviderResponse:
        """Send a prompt to Gemini and return a normalized :class:`ProviderResponse`."""

        def _call() -> ProviderResponse:
            start = time.perf_counter()
            try:
                response = self._client.generate_content(
                    prompt,
                    generation_config={
                        "temperature": self.config.temperature,
                        "max_output_tokens": self.config.max_tokens,
                    },
                )
            except Exception as exc:
                _translate_sdk_error(exc)
                raise FatalError(f"Gemini call failed: {exc}") from exc

            elapsed_ms = (time.perf_counter() - start) * 1000.0
            text = _extract_text(response)
            usage = _extract_usage(response)

            parameters: dict[str, Any] = {
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
            }
            if usage:
                parameters["usage"] = usage

            return ProviderResponse(
                response_text=text,
                model=self.config.model,
                timestamp=datetime.now(timezone.utc),
                response_time_ms=elapsed_ms,
                parameters=parameters,
            )

        return retry_with_backoff(
            _call,
            max_attempts=self._max_attempts,
            initial_delay=self._initial_delay,
            sleep=self._sleep,
        )


_last_configured_key: str | None = None


def _default_client_factory(config: ProviderConfig) -> Any:
    """Default Gemini client builder. Imported lazily to avoid SDK import on tests.

    Calls :func:`genai.configure` which mutates process-global SDK state. When
    a different API key is provided to a subsequent invocation, a warning is
    logged because earlier providers will silently start routing through the
    new key. See module docstring for the recommended workaround.
    """
    global _last_configured_key
    import google.generativeai as genai

    if _last_configured_key is not None and _last_configured_key != config.api_key:
        logger.warning(
            "Reconfiguring google-generativeai with a different API key; "
            "previously built GeminiProvider instances will start using the new key. "
            "Use a single API key per process or isolate providers across processes."
        )
    genai.configure(api_key=config.api_key)
    _last_configured_key = config.api_key
    return genai.GenerativeModel(config.model)


def _extract_text(response: Any) -> str:
    """Extract the plain-text response from a Gemini SDK result.

    The SDK returns an object with a ``.text`` property that joins all
    candidate parts. We prefer that, but fall back to manual concatenation
    when the property is unavailable (e.g. test stubs).
    """
    text = getattr(response, "text", None)
    if text is not None:
        return str(text)

    candidates = getattr(response, "candidates", None) or []
    if not candidates:
        return ""
    parts = getattr(candidates[0].content, "parts", []) or []
    return "".join(getattr(part, "text", "") for part in parts)


def _extract_usage(response: Any) -> dict[str, int] | None:
    """Extract token usage from a Gemini response if available."""
    usage = getattr(response, "usage_metadata", None)
    if usage is None:
        return None
    prompt = getattr(usage, "prompt_token_count", None)
    completion = getattr(usage, "candidates_token_count", None)
    total = getattr(usage, "total_token_count", None)
    if prompt is None and completion is None and total is None:
        return None
    return {
        "prompt_tokens": int(prompt) if prompt is not None else 0,
        "completion_tokens": int(completion) if completion is not None else 0,
        "total_tokens": int(total) if total is not None else 0,
    }


def _translate_sdk_error(exc: BaseException) -> None:
    """Translate a Gemini SDK error into the local provider error hierarchy.

    Returns silently if the exception is not a recognized retryable error;
    the caller is then expected to wrap it in :class:`FatalError`. Raises a
    typed :class:`ProviderError` subclass when the error matches a known
    transient case.
    """
    name = type(exc).__name__
    message = str(exc)
    lowered = message.lower()

    if (
        name in {"ResourceExhausted", "TooManyRequests"}
        or "429" in message
        or "rate limit" in lowered
    ):
        raise RateLimitError(f"Gemini rate-limited: {message}") from exc
    if name in {"DeadlineExceeded", "Timeout", "TimeoutError"} or "timeout" in lowered:
        raise ProviderTimeoutError(f"Gemini timeout: {message}") from exc
    if name in {"ServiceUnavailable", "InternalServerError"} or _is_5xx(message):
        raise TransientError(f"Gemini transient error: {message}") from exc


def _is_5xx(message: str) -> bool:
    return any(code in message for code in ("500", "502", "503", "504"))
