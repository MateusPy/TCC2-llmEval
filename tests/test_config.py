"""Testes para config.py."""

import pytest
import yaml
from pydantic import ValidationError

from llm_eval.config import Config, JudgeSettings, ProviderSettings, _is_pinned_model


# ---------------------------------------------------------------------------
# ProviderSettings
# ---------------------------------------------------------------------------


def test_provider_settings_minimal():
    ps = ProviderSettings(type="gemini", model="gemini-2.0-flash-001")
    assert ps.type == "gemini"
    assert ps.model == "gemini-2.0-flash-001"
    assert ps.api_key is None
    assert ps.temperature == 0.0
    assert ps.max_tokens == 1024
    assert ps.seed is None
    assert ps.url is None
    assert ps.method == "POST"
    assert ps.headers == {}
    assert ps.request_template is None
    assert ps.response_path is None


# ---------------------------------------------------------------------------
# Reproducibility — seed and model pinning
# ---------------------------------------------------------------------------


def test_provider_settings_accepts_seed():
    ps = ProviderSettings(type="gemini", model="gemini-2.0-flash-001", seed=42)
    assert ps.seed == 42


def test_provider_settings_seed_none_default():
    ps = ProviderSettings(type="mistral", model="mistral-small-2503")
    assert ps.seed is None


@pytest.mark.parametrize(
    "model,expected",
    [
        # Pinned identifiers (accepted)
        ("gemini-2.0-flash-001", True),
        ("gemini-1.5-pro-002", True),
        ("mistral-small-2503", True),
        ("mistral-large-2411", True),
        ("model-2024-09", True),
        ("model-09-15", True),
        # Unpinned identifiers (rejected)
        ("gemini-2.0-flash", False),
        ("gemini-1.5-pro", False),
        ("mistral-small", False),
        ("gemini-pro", False),
        ("gemini-1.5-pro-latest", False),
        ("gemini-1.5-pro-stable", False),
        ("", False),
    ],
)
def test_is_pinned_model_classification(model: str, expected: bool):
    assert _is_pinned_model(model) is expected


def test_provider_settings_rejects_unpinned_gemini():
    with pytest.raises(ValidationError, match="not pinned to an explicit version"):
        ProviderSettings(type="gemini", model="gemini-2.0-flash")


def test_provider_settings_rejects_unpinned_mistral():
    with pytest.raises(ValidationError, match="not pinned to an explicit version"):
        ProviderSettings(type="mistral", model="mistral-small")


def test_provider_settings_rejects_latest_alias():
    with pytest.raises(ValidationError, match="not pinned to an explicit version"):
        ProviderSettings(type="gemini", model="gemini-1.5-pro-latest")


def test_provider_settings_custom_provider_skips_pin_validation():
    """Custom providers may use opaque or proprietary model identifiers."""
    ps = ProviderSettings(
        type="custom",
        model="my-internal-bot",
        url="https://example.com/api",
        request_template={"prompt": "{prompt}"},
        response_path="answer",
    )
    assert ps.model == "my-internal-bot"


def test_provider_settings_pin_error_message_is_actionable():
    """The error message must guide the user to fix the config quickly."""
    try:
        ProviderSettings(type="gemini", model="gemini-2.0-flash")
    except ValidationError as exc:
        message = str(exc)
        assert "gemini-2.0-flash-001" in message  # suggests pinned form
        assert "reproducible" in message.lower()


def test_provider_settings_all_fields():
    ps = ProviderSettings(
        type="mistral",
        api_key="key-123",
        model="mistral-small-2503",
        temperature=0.5,
        max_tokens=2048,
    )
    assert ps.api_key == "key-123"
    assert ps.temperature == 0.5
    assert ps.max_tokens == 2048


def test_provider_settings_custom_provider():
    ps = ProviderSettings(
        type="custom",
        model="my-model",
        url="https://example.com/api",
        method="POST",
        headers={"Authorization": "Bearer tok"},
        request_template={"messages": [{"role": "user", "content": "{prompt}"}]},
        response_path="choices.0.message.content",
    )
    assert ps.url == "https://example.com/api"
    assert ps.headers["Authorization"] == "Bearer tok"
    assert ps.response_path == "choices.0.message.content"


def test_provider_settings_missing_required():
    with pytest.raises(ValidationError):
        ProviderSettings(type="gemini")  # model is missing


# ---------------------------------------------------------------------------
# JudgeSettings
# ---------------------------------------------------------------------------


def test_judge_settings_defaults():
    provider = ProviderSettings(type="gemini", model="gemini-2.0-flash-001")
    judge = JudgeSettings(provider=provider)
    assert judge.enabled is True


def test_judge_settings_disabled():
    provider = ProviderSettings(type="gemini", model="gemini-2.0-flash-001")
    judge = JudgeSettings(provider=provider, enabled=False)
    assert judge.enabled is False


# ---------------------------------------------------------------------------
# Config — dimensions validator
# ---------------------------------------------------------------------------


def _make_config(**overrides) -> Config:
    defaults = {
        "provider": ProviderSettings(type="gemini", model="gemini-2.0-flash-001"),
        "judge": JudgeSettings(
            provider=ProviderSettings(type="gemini", model="gemini-2.0-flash-001")
        ),
    }
    defaults.update(overrides)
    return Config(**defaults)


def test_config_defaults():
    cfg = _make_config()
    assert cfg.dimensions == ["factual", "consistency", "robustness"]
    assert cfg.scenarios_path is None
    assert cfg.repetitions == 1
    assert cfg.output_dir == "./results"
    assert cfg.output_format == ["json", "markdown"]


def test_config_custom_values():
    cfg = _make_config(
        dimensions=["factual"],
        repetitions=5,
        output_dir="./out",
        output_format=["json"],
    )
    assert cfg.dimensions == ["factual"]
    assert cfg.repetitions == 5


def test_config_invalid_dimension():
    with pytest.raises(ValidationError, match="Invalid dimensions"):
        _make_config(dimensions=["factual", "banana"])


def test_config_all_valid_dimensions_individually():
    for dim in ("factual", "consistency", "robustness"):
        cfg = _make_config(dimensions=[dim])
        assert cfg.dimensions == [dim]


# ---------------------------------------------------------------------------
# _resolve_env_vars
# ---------------------------------------------------------------------------


def test_resolve_env_vars_simple(monkeypatch):
    monkeypatch.setenv("MY_KEY", "secret")
    result = Config._resolve_env_vars({"api_key": "${MY_KEY}"})
    assert result == {"api_key": "secret"}


def test_resolve_env_vars_partial_string(monkeypatch):
    monkeypatch.setenv("TOKEN", "abc123")
    result = Config._resolve_env_vars({"header": "Bearer ${TOKEN}"})
    assert result == {"header": "Bearer abc123"}


def test_resolve_env_vars_nested_dict(monkeypatch):
    monkeypatch.setenv("INNER", "val")
    data = {"outer": {"inner": "${INNER}"}}
    result = Config._resolve_env_vars(data)
    assert result == {"outer": {"inner": "val"}}


def test_resolve_env_vars_in_list(monkeypatch):
    monkeypatch.setenv("ITEM", "x")
    result = Config._resolve_env_vars({"items": ["${ITEM}", "static"]})
    assert result == {"items": ["x", "static"]}


def test_resolve_env_vars_missing(monkeypatch):
    monkeypatch.delenv("MISSING_VAR", raising=False)
    with pytest.raises(ValueError, match="MISSING_VAR"):
        Config._resolve_env_vars({"key": "${MISSING_VAR}"})


def test_resolve_env_vars_no_placeholders():
    data = {"key": "plain", "num": 42, "flag": True, "empty": None}
    result = Config._resolve_env_vars(data)
    assert result == data


def test_resolve_env_vars_non_string_values():
    data = {"int_val": 10, "float_val": 3.14, "bool_val": False, "none_val": None}
    result = Config._resolve_env_vars(data)
    assert result == data


def test_resolve_env_vars_multiple_in_one_string(monkeypatch):
    monkeypatch.setenv("HOST", "localhost")
    monkeypatch.setenv("PORT", "8080")
    result = Config._resolve_env_vars({"url": "http://${HOST}:${PORT}/api"})
    assert result == {"url": "http://localhost:8080/api"}


# ---------------------------------------------------------------------------
# from_yaml
# ---------------------------------------------------------------------------


def test_from_yaml_valid(tmp_path, monkeypatch):
    monkeypatch.setenv("TEST_API_KEY", "key-123")
    config_data = {
        "provider": {
            "type": "gemini",
            "api_key": "${TEST_API_KEY}",
            "model": "gemini-2.0-flash-001",
        },
        "judge": {
            "provider": {
                "type": "gemini",
                "api_key": "${TEST_API_KEY}",
                "model": "gemini-2.0-flash-001",
            },
        },
        "dimensions": ["factual"],
        "repetitions": 3,
    }
    yaml_path = tmp_path / "config.yaml"
    yaml_path.write_text(yaml.dump(config_data), encoding="utf-8")

    cfg = Config.from_yaml(yaml_path)
    assert cfg.provider.api_key == "key-123"
    assert cfg.provider.model == "gemini-2.0-flash-001"
    assert cfg.dimensions == ["factual"]
    assert cfg.repetitions == 3


def test_from_yaml_config_example(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    cfg = Config.from_yaml("config.example.yaml")
    assert cfg.provider.type == "gemini"
    assert cfg.provider.api_key == "test-key"
    assert cfg.provider.model == "gemini-2.0-flash-001"
    assert cfg.judge.enabled is True
    assert cfg.dimensions == ["factual", "consistency", "robustness"]
    assert cfg.repetitions == 3


def test_from_yaml_invalid_toplevel(tmp_path):
    yaml_path = tmp_path / "bad.yaml"
    yaml_path.write_text("just a string", encoding="utf-8")
    with pytest.raises(ValueError, match="top-level mapping"):
        Config.from_yaml(yaml_path)


def test_from_yaml_file_not_found():
    with pytest.raises(FileNotFoundError):
        Config.from_yaml("/nonexistent/config.yaml")


def test_from_yaml_empty_file(tmp_path):
    yaml_path = tmp_path / "empty.yaml"
    yaml_path.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="Empty configuration file"):
        Config.from_yaml(yaml_path)
