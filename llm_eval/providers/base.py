"""Base abstractions and shared models for chatbot providers."""

from abc import ABC, abstractmethod
from datetime import datetime

from pydantic import BaseModel


class ProviderResponse(BaseModel):
    """Standardized response returned by any provider implementation.

    This model normalizes the data produced by different chatbot providers so
    the rest of the framework can consume responses through a consistent API.

    Attributes:
        response_text: Text returned by the provider.
        model: Name of the model that generated the response.
        timestamp: Time when the response was received.
        response_time_ms: End-to-end latency in milliseconds.
        parameters: Parameters used to generate the response.
        raw_response: Optional raw API payload kept for debugging purposes.
    """

    response_text: str
    model: str
    timestamp: datetime
    response_time_ms: float
    parameters: dict
    raw_response: dict | None = None


class ProviderConfig(BaseModel):
    """Base configuration shared by provider implementations.

    The default ``temperature`` is ``0.0`` to maximize reproducibility during
    evaluations, reducing output variability across repeated runs.

    Attributes:
        api_key: Authentication token used by the provider.
        model: Name of the target model.
        temperature: Sampling temperature used for generation.
        max_tokens: Maximum number of tokens to request in the response.
    """

    api_key: str
    model: str
    temperature: float = 0.0
    max_tokens: int = 1024


class BaseProvider(ABC):
    """Abstract interface for chatbot providers used by the framework.

    Subclasses must implement :meth:`send` to adapt their concrete API into the
    standardized :class:`ProviderResponse` model.
    """

    def __init__(self, config: ProviderConfig) -> None:
        """Initialize the provider with its validated configuration.

        Args:
            config: Provider configuration used for authentication and request
                defaults.
        """

        self.config = config

    @abstractmethod
    def send(self, prompt: str) -> ProviderResponse:
        """Send a single prompt to the provider.

        Args:
            prompt: Input prompt that will be sent to the underlying chatbot.

        Returns:
            ProviderResponse: Standardized provider response.
        """

    def send_batch(self, prompts: list[str]) -> list[ProviderResponse]:
        """Send multiple prompts sequentially using the default implementation.

        Subclasses may override this method to leverage native batch endpoints
        when supported by the provider API.

        Args:
            prompts: Prompts to be sent to the provider.

        Returns:
            list[ProviderResponse]: Responses in the same order as the input
            prompts.
        """

        return [self.send(prompt) for prompt in prompts]
