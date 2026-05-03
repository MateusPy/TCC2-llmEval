"""Retry helper with exponential backoff, shared by concrete providers.

Used by Gemini, Mistral and Custom HTTP providers to handle transient errors
(rate limits and 5xx) consistently. Exposes ``retry_with_backoff`` plus a
small ``ProviderError`` hierarchy for callers that prefer a typed exception
over inspecting low-level SDK errors.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ProviderError(Exception):
    """Base class for errors raised by concrete providers."""


class RateLimitError(ProviderError):
    """Raised when the provider returned a rate-limit response (HTTP 429)."""


class TimeoutError(ProviderError):  # noqa: A001  - intentional shadow of builtin
    """Raised when the provider request timed out."""


class TransientError(ProviderError):
    """Raised for transient server-side failures (HTTP 5xx)."""


class FatalError(ProviderError):
    """Raised for non-retryable failures (auth, malformed request, etc.)."""


RETRYABLE = (RateLimitError, TimeoutError, TransientError)


def retry_with_backoff(
    fn: Callable[[], T],
    *,
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    sleep: Callable[[float], None] | None = None,
) -> T:
    """Run ``fn`` retrying on retryable provider errors.

    Args:
        fn: Zero-argument callable that performs the request.
        max_attempts: Total attempts including the first call. Must be >= 1.
        initial_delay: Seconds to wait before the second attempt.
        backoff_factor: Multiplicative growth applied between retries.
        sleep: Sleep function. ``None`` resolves to :func:`time.sleep` at
            call time (so monkeypatching ``time.sleep`` is respected). Tests
            should pass an explicit no-op such as ``lambda _: None``.

    Returns:
        Whatever ``fn`` returned on the first successful attempt.

    Raises:
        ProviderError: The last retryable error if all attempts fail; or any
            :class:`FatalError` raised by ``fn`` (not retried).
    """
    if max_attempts < 1:
        raise ValueError(f"max_attempts must be >= 1, got {max_attempts}")

    sleep_fn: Callable[[float], None] = sleep if sleep is not None else time.sleep

    last_error: ProviderError | None = None
    delay = initial_delay
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except RETRYABLE as exc:
            last_error = exc
            if attempt == max_attempts:
                logger.warning(
                    "Provider call failed after %d attempts: %s",
                    max_attempts,
                    exc,
                )
                raise
            logger.info(
                "Provider call failed (attempt %d/%d), retrying in %.2fs: %s",
                attempt,
                max_attempts,
                delay,
                exc,
            )
            sleep_fn(delay)
            delay *= backoff_factor

    # Defensive: loop above either returns or raises. This line keeps mypy happy.
    raise last_error if last_error is not None else ProviderError("retry exhausted")
