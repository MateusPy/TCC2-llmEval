"""Providers para comunicação com chatbots baseados em LLMs."""

from llm_eval.providers._retry import (
    FatalError,
    ProviderError,
    RateLimitError,
    TimeoutError,
    TransientError,
    retry_with_backoff,
)
from llm_eval.providers.base import BaseProvider, ProviderConfig, ProviderResponse
from llm_eval.providers.custom import CustomProvider, build_from_settings
from llm_eval.providers.gemini import GeminiProvider
from llm_eval.providers.mistral import MistralProvider

__all__ = [
    "BaseProvider",
    "CustomProvider",
    "FatalError",
    "GeminiProvider",
    "MistralProvider",
    "ProviderConfig",
    "ProviderError",
    "ProviderResponse",
    "RateLimitError",
    "TimeoutError",
    "TransientError",
    "build_from_settings",
    "retry_with_backoff",
]
