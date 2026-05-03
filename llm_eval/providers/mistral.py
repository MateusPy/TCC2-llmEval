"""Mistral AI provider implementation.

Wraps the ``mistralai`` SDK behind the :class:`BaseProvider` contract. Mirrors
the design of :mod:`llm_eval.providers.gemini`: retry helper, injectable
client factory, normalized error translation.
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


class MistralProvider(BaseProvider):
    """Provider for Mistral AI models via the ``mistralai`` SDK."""

    def __init__(
        self,
        config: ProviderConfig,
        *,
        client_factory: Callable[[ProviderConfig], Any] | None = None,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
    ) -> None:
        """Initialize the Mistral provider.

        Args:
            config: Provider configuration.
            client_factory: Callable that builds the underlying SDK client.
                ``None`` uses the default ``mistralai.Mistral`` client. Tests
                inject a stub exposing ``chat.complete``.
            max_attempts: Maximum retry attempts for transient errors.
            initial_delay: Seconds to wait before the second attempt.
        """
        super().__init__(config)
        self._client_factory = client_factory or _default_client_factory
        self._max_attempts = max_attempts
        self._initial_delay = initial_delay
        self._client = self._client_factory(config)

    def send(self, prompt: str) -> ProviderResponse:
        """Send a prompt to Mistral and return a normalized :class:`ProviderResponse`."""

        def _call() -> ProviderResponse:
            start = time.perf_counter()
            try:
                response = self._client.chat.complete(
                    model=self.config.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                )
            except Exception as exc:
                _translate_sdk_error(exc)
                raise FatalError(f"Mistral call failed: {exc}") from exc

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
        )


def _default_client_factory(config: ProviderConfig) -> Any:
    """Default Mistral client builder. Imported lazily to avoid SDK import on tests."""
    from mistralai import Mistral

    return Mistral(api_key=config.api_key)


def _extract_text(response: Any) -> str:
    """Extract the assistant message from a Mistral chat completion response."""
    choices = getattr(response, "choices", None) or []
    if not choices:
        return ""
    message = getattr(choices[0], "message", None)
    if message is None:
        return ""
    content = getattr(message, "content", "")
    return str(content) if content is not None else ""


def _extract_usage(response: Any) -> dict[str, int] | None:
    """Extract token usage from a Mistral response if available."""
    usage = getattr(response, "usage", None)
    if usage is None:
        return None
    prompt = getattr(usage, "prompt_tokens", None)
    completion = getattr(usage, "completion_tokens", None)
    total = getattr(usage, "total_tokens", None)
    if prompt is None and completion is None and total is None:
        return None
    return {
        "prompt_tokens": int(prompt) if prompt is not None else 0,
        "completion_tokens": int(completion) if completion is not None else 0,
        "total_tokens": int(total) if total is not None else 0,
    }


def _translate_sdk_error(exc: BaseException) -> None:
    """Translate a Mistral SDK error into the local provider error hierarchy."""
    name = type(exc).__name__
    message = str(exc)
    lowered = message.lower()

    status_code = getattr(exc, "status_code", None)
    if status_code == 429 or "429" in message or "rate limit" in lowered:
        raise RateLimitError(f"Mistral rate-limited: {message}") from exc
    if name in {"TimeoutError", "ReadTimeout", "ConnectTimeout"} or "timeout" in lowered:
        raise ProviderTimeoutError(f"Mistral timeout: {message}") from exc
    if (status_code is not None and 500 <= int(status_code) < 600) or _is_5xx(message):
        raise TransientError(f"Mistral transient error: {message}") from exc


def _is_5xx(message: str) -> bool:
    return any(code in message for code in ("500", "502", "503", "504"))
