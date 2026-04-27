"""Carregamento e validação de configurações."""

import os
import re
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, field_validator


class ProviderSettings(BaseModel):
    """User-facing configuration for a chatbot provider.

    Includes fields for built-in providers (Gemini, Mistral) and for custom
    HTTP providers that require explicit endpoint configuration.

    Attributes:
        type: Provider identifier (``"gemini"``, ``"mistral"`` or ``"custom"``).
        api_key: Authentication token. May be ``None`` when the custom provider
            relies on headers for authentication.
        model: Target model name.
        temperature: Sampling temperature for generation.
        max_tokens: Maximum number of tokens to request.
        url: Endpoint URL (custom provider only).
        method: HTTP method (custom provider only).
        headers: Extra HTTP headers (custom provider only).
        request_template: Request body template (custom provider only).
        response_path: Dot-notation path to extract the response text from the
            API JSON payload (custom provider only).
    """

    type: str
    api_key: str | None = None
    model: str
    temperature: float = 0.0
    max_tokens: int = 1024
    url: str | None = None
    method: str = "POST"
    headers: dict[str, str] = Field(default_factory=dict)
    request_template: dict | None = None
    response_path: str | None = None


class JudgeSettings(BaseModel):
    """Configuration for the LLM-as-a-Judge evaluator.

    Attributes:
        provider: Provider used as the judge.
        enabled: Whether judge evaluation is active.
    """

    provider: ProviderSettings
    enabled: bool = True


class Config(BaseModel):
    """Root configuration for the llm-eval framework.

    Supports loading from a YAML file via :meth:`from_yaml` or direct
    programmatic construction.

    Attributes:
        provider: Chatbot provider to be evaluated.
        judge: LLM-as-a-Judge evaluator settings.
        dimensions: Reliability dimensions to evaluate.
        scenarios_path: Path to custom scenarios directory. When ``None`` the
            built-in scenario bank is used.
        repetitions: How many times each prompt is sent (to measure variability).
        output_dir: Directory where results are saved.
        output_format: Output formats to generate.
    """

    provider: ProviderSettings
    judge: JudgeSettings
    dimensions: list[str] = Field(default_factory=lambda: ["factual", "consistency", "robustness"])
    scenarios_path: str | None = None
    repetitions: int = 1
    output_dir: str = "./results"
    output_format: list[str] = Field(default_factory=lambda: ["json", "markdown"])

    @field_validator("dimensions")
    @classmethod
    def validate_dimensions(cls, v: list[str]) -> list[str]:
        """Ensure only supported dimensions are requested."""
        allowed = {"factual", "consistency", "robustness"}
        invalid = [d for d in v if d not in allowed]
        if invalid:
            raise ValueError(
                f"Invalid dimensions: {invalid}. Allowed values: {sorted(allowed)}"
            )
        return v

    @classmethod
    def from_yaml(cls, path: str | Path) -> "Config":
        """Load configuration from a YAML file.

        Environment variable placeholders (``${VAR_NAME}``) in string values
        are resolved automatically.

        Args:
            path: Path to the YAML configuration file.

        Returns:
            Config: Validated configuration instance.
        """
        raw = Path(path).read_text(encoding="utf-8")
        data = yaml.safe_load(raw)
        if data is None:
            raise ValueError("Empty configuration file")
        if not isinstance(data, dict):
            raise ValueError(
                "Configuration file must contain a top-level mapping, "
                f"got {type(data).__name__}"
            )
        data = cls._resolve_env_vars(data)
        return cls(**data)

    @classmethod
    def _resolve_env_vars(cls, data: dict) -> dict:
        """Recursively replace ``${VAR_NAME}`` placeholders with environment variables.

        Args:
            data: Parsed YAML data.

        Returns:
            dict: Data with all placeholders resolved.

        Raises:
            ValueError: If a referenced environment variable is not set.
        """

        def _resolve(value):  # noqa: ANN001, ANN202
            if isinstance(value, str):

                def _replacer(match: re.Match) -> str:
                    var_name = match.group(1)
                    env_value = os.environ.get(var_name)
                    if env_value is None:
                        raise ValueError(
                            f"Environment variable '{var_name}' is not set"
                        )
                    return env_value

                return re.sub(r"\$\{([^}]+)\}", _replacer, value)
            elif isinstance(value, dict):
                return {k: _resolve(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [_resolve(item) for item in value]
            return value

        return _resolve(data)
