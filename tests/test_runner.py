"""Testes para runner.py."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from llm_eval.config import Config, JudgeSettings, ProviderSettings
from llm_eval.evaluation.judge import Judge, JudgeResult
from llm_eval.evaluation.metrics import MetricResult
from llm_eval.providers.base import BaseProvider, ProviderConfig, ProviderResponse
from llm_eval.runner import (
    FINAL_FILENAME,
    PARTIAL_FILENAME,
    RunResult,
    Runner,
    ScenarioResult,
    default_provider_factory,
    sanitize_config,
)
from llm_eval.scenarios.loader import (
    Scenario,
    ScenarioBank,
    ScenarioLoader,
    ScenarioVariant,
)


# ---------------------------------------------------------------------------
# Stubs
# ---------------------------------------------------------------------------


class _RecordingProvider(BaseProvider):
    """Provider that returns canned responses keyed by prompt suffix."""

    def __init__(
        self,
        *,
        default_text: str = "resposta",
        prompt_to_text: dict[str, str] | None = None,
        model: str = "stub",
        raise_for: set[str] | None = None,
    ) -> None:
        super().__init__(ProviderConfig(api_key="x", model=model))
        self._default_text = default_text
        self._prompt_to_text = prompt_to_text or {}
        self._raise_for = raise_for or set()
        self.prompts: list[str] = []

    def send(self, prompt: str) -> ProviderResponse:
        self.prompts.append(prompt)
        if prompt in self._raise_for:
            raise RuntimeError(f"boom for {prompt!r}")
        text = self._prompt_to_text.get(prompt, self._default_text)
        return ProviderResponse(
            response_text=text,
            model=self.config.model,
            timestamp=datetime.now(timezone.utc),
            response_time_ms=1.0,
            parameters={},
        )


class _StubJudge(Judge):
    """Judge that returns canned scores per dimension, ignoring the underlying LLM."""

    def __init__(self) -> None:
        provider = _RecordingProvider(default_text='{"score": 5, "justification": "ok"}')
        super().__init__(provider)
        self.factual_calls: list[dict[str, Any]] = []
        self.consistency_calls: list[dict[str, Any]] = []
        self.robustness_calls: list[dict[str, Any]] = []

    def evaluate_factual(  # type: ignore[override]
        self, prompt: str, ground_truth: str, response: str
    ) -> JudgeResult:
        self.factual_calls.append(
            {"prompt": prompt, "ground_truth": ground_truth, "response": response}
        )
        return JudgeResult(dimension="factual", score=5, justification="ok")

    def evaluate_consistency(  # type: ignore[override]
        self, prompt: str, responses: list[str]
    ) -> JudgeResult:
        self.consistency_calls.append({"prompt": prompt, "responses": responses})
        return JudgeResult(dimension="consistency", score=4, justification="ok")

    def evaluate_robustness(  # type: ignore[override]
        self,
        prompt: str,
        original_response: str,
        variant_type: str,
        variant_prompt: str,
        variant_response: str,
    ) -> JudgeResult:
        self.robustness_calls.append(
            {
                "prompt": prompt,
                "original_response": original_response,
                "variant_type": variant_type,
                "variant_prompt": variant_prompt,
                "variant_response": variant_response,
            }
        )
        return JudgeResult(dimension="robustness", score=3, justification="ok")


class _StubLoader(ScenarioLoader):
    def __init__(self, banks: dict[str, ScenarioBank]) -> None:
        self._banks = banks

    def load(self, dimension: str) -> ScenarioBank:  # type: ignore[override]
        return self._banks[dimension]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _factual_scenario(scenario_id: str = "factual-001") -> Scenario:
    return Scenario(
        id=scenario_id,
        dimension="factual",
        category="knowledge",
        prompt=f"prompt-{scenario_id}",
        ground_truth="Brasília",
    )


def _consistency_scenario(scenario_id: str = "consistency-001") -> Scenario:
    return Scenario(
        id=scenario_id,
        dimension="consistency",
        category="knowledge",
        prompt=f"prompt-{scenario_id}",
        ground_truth="Brasília",
        variants=[
            ScenarioVariant(
                id=f"{scenario_id}-v1", variant_type="paraphrase", prompt="paraphrase-1"
            ),
            ScenarioVariant(
                id=f"{scenario_id}-v2", variant_type="paraphrase", prompt="paraphrase-2"
            ),
        ],
    )


def _robustness_scenario(scenario_id: str = "robustness-001") -> Scenario:
    return Scenario(
        id=scenario_id,
        dimension="robustness",
        category="knowledge",
        prompt=f"prompt-{scenario_id}",
        ground_truth="Brasília",
        variants=[
            ScenarioVariant(
                id=f"{scenario_id}-v1",
                variant_type="typo",
                prompt="typo-prompt",
                level="character",
            ),
            ScenarioVariant(
                id=f"{scenario_id}-v2",
                variant_type="adversarial",
                prompt="adversarial-prompt",
                level="semantic",
            ),
        ],
    )


def _make_config(
    *,
    output_dir: Path,
    dimensions: list[str] | None = None,
    repetitions: int = 1,
) -> Config:
    provider = ProviderSettings(
        type="gemini",
        api_key="real-key-should-be-redacted",
        model="gemini-2.0-flash-001",
    )
    return Config(
        provider=provider,
        judge=JudgeSettings(provider=provider),
        dimensions=dimensions or ["factual", "consistency", "robustness"],
        repetitions=repetitions,
        output_dir=str(output_dir),
    )


def _bank(dimension: str, scenarios: list[Scenario]) -> ScenarioBank:
    return ScenarioBank(dimension=dimension, version="0.1.0", scenarios=scenarios)


def _bertscore_stub(reference: str, candidate: str, lang: str = "pt") -> MetricResult:
    return MetricResult(
        metric_name="bertscore",
        value=0.9,
        details={"reference": reference, "candidate": candidate, "lang": lang},
    )


def _consistency_stub(responses: list[str], lang: str = "pt") -> MetricResult:
    return MetricResult(
        metric_name="consistency",
        value=0.85,
        details={"num_responses": len(responses), "lang": lang},
    )


def _make_runner(
    config: Config,
    *,
    provider: BaseProvider,
    judge: Judge,
    loader: ScenarioLoader,
    partial_save_every: int = 1,
) -> Runner:
    return Runner(
        config,
        scenarios_loader=loader,
        provider_factory=lambda _settings: provider,
        judge=judge,
        bertscore_fn=_bertscore_stub,
        consistency_fn=_consistency_stub,
        partial_save_every=partial_save_every,
    )


# ---------------------------------------------------------------------------
# sanitize_config
# ---------------------------------------------------------------------------


def test_sanitize_config_redacts_provider_api_key(tmp_path: Path):
    config = _make_config(output_dir=tmp_path)
    data = sanitize_config(config)
    assert data["provider"]["api_key"] == "***REDACTED***"
    assert data["judge"]["provider"]["api_key"] == "***REDACTED***"


def test_sanitize_config_preserves_other_fields(tmp_path: Path):
    config = _make_config(output_dir=tmp_path, repetitions=4)
    data = sanitize_config(config)
    assert data["repetitions"] == 4
    assert data["provider"]["model"] == "gemini-2.0-flash-001"


def test_sanitize_config_does_not_redact_empty_api_key(tmp_path: Path):
    """An empty/None api_key (e.g. custom provider w/ headers auth) is left untouched."""
    config = _make_config(output_dir=tmp_path)
    config.provider.api_key = None
    data = sanitize_config(config)
    assert data["provider"]["api_key"] is None


# ---------------------------------------------------------------------------
# default_provider_factory
# ---------------------------------------------------------------------------


def test_default_provider_factory_unknown_type_raises():
    with pytest.raises(ValueError, match="Unknown provider type"):
        default_provider_factory(
            ProviderSettings.model_construct(type="bogus", model="x", api_key="x")
        )


def test_default_provider_factory_builds_gemini(monkeypatch: pytest.MonkeyPatch):
    """Gemini branch should call the SDK factory; we intercept the SDK import."""
    import sys

    class _FakeGenAI:
        @staticmethod
        def configure(api_key: str) -> None:  # noqa: ARG004
            pass

        @staticmethod
        def GenerativeModel(model: str) -> object:  # noqa: ARG004, N802
            return object()

    monkeypatch.setitem(sys.modules, "google.generativeai", _FakeGenAI)
    settings = ProviderSettings(type="gemini", api_key="k", model="gemini-2.0-flash-001")

    from llm_eval.providers.gemini import GeminiProvider

    provider = default_provider_factory(settings)
    assert isinstance(provider, GeminiProvider)


def test_default_provider_factory_builds_mistral(monkeypatch: pytest.MonkeyPatch):
    """Mistral branch should call the SDK factory; we intercept the SDK import."""
    import sys
    import types

    class _FakeMistralClient:
        def __init__(self, api_key: str) -> None:  # noqa: ARG002
            self.chat = object()

    fake_module = types.ModuleType("mistralai")
    fake_module.Mistral = _FakeMistralClient  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "mistralai", fake_module)

    settings = ProviderSettings(type="mistral", api_key="k", model="mistral-small-2503")

    from llm_eval.providers.mistral import MistralProvider

    provider = default_provider_factory(settings)
    assert isinstance(provider, MistralProvider)


def test_default_provider_factory_builds_custom():
    """Custom branch goes through build_from_settings; no SDK to patch."""
    settings = ProviderSettings(
        type="custom",
        api_key=None,
        model="m",
        url="https://example.com",
        method="POST",
        headers={"X-Auth": "abc"},
        request_template={"q": "{prompt}"},
        response_path="answer",
    )

    from llm_eval.providers.custom import CustomProvider

    provider = default_provider_factory(settings)
    assert isinstance(provider, CustomProvider)
    assert provider.url == "https://example.com"


def test_settings_to_provider_config_uses_empty_string_for_missing_key():
    """_settings_to_provider_config substitutes None api_key with empty string."""
    from llm_eval.runner import _settings_to_provider_config

    settings = ProviderSettings(
        type="gemini", api_key=None, model="gemini-2.0-flash-001", temperature=0.5, max_tokens=128
    )
    cfg = _settings_to_provider_config(settings)
    assert cfg.api_key == ""
    assert cfg.temperature == 0.5
    assert cfg.max_tokens == 128
    assert cfg.seed is None


def test_settings_to_provider_config_propagates_seed():
    """seed must flow from ProviderSettings into ProviderConfig."""
    from llm_eval.runner import _settings_to_provider_config

    settings = ProviderSettings(type="gemini", api_key="x", model="gemini-2.0-flash-001", seed=1234)
    cfg = _settings_to_provider_config(settings)
    assert cfg.seed == 1234


def test_run_result_records_seed_in_config(tmp_path: Path):
    """The serialized config inside RunResult must include the configured seed."""
    judge = _StubJudge()
    provider = _RecordingProvider(default_text="Brasília")
    loader = _StubLoader({"factual": _bank("factual", [_factual_scenario()])})
    target_settings = ProviderSettings(
        type="gemini", api_key="k", model="gemini-2.0-flash-001", seed=42
    )
    judge_settings = ProviderSettings(
        type="gemini", api_key="k", model="gemini-2.0-flash-001", seed=7
    )
    config = Config(
        provider=target_settings,
        judge=JudgeSettings(provider=judge_settings),
        dimensions=["factual"],
        output_dir=str(tmp_path),
    )
    runner = _make_runner(config, provider=provider, judge=judge, loader=loader)
    result = runner.run()

    assert result.config["provider"]["seed"] == 42
    assert result.config["judge"]["provider"]["seed"] == 7


# ---------------------------------------------------------------------------
# Runner — factual
# ---------------------------------------------------------------------------


def test_runner_factual_basic_flow(tmp_path: Path):
    judge = _StubJudge()
    provider = _RecordingProvider(default_text="Brasília")
    loader = _StubLoader({"factual": _bank("factual", [_factual_scenario()])})
    config = _make_config(output_dir=tmp_path, dimensions=["factual"])
    runner = _make_runner(config, provider=provider, judge=judge, loader=loader)

    result = runner.run()

    assert len(result.scenario_results) == 1
    sr = result.scenario_results[0]
    assert sr.dimension == "factual"
    assert sr.error is None
    assert len(sr.responses) == 1
    assert len(sr.judge_results) == 1
    assert sr.judge_results[0].score == 5
    assert len(sr.metric_results) == 1
    assert sr.metric_results[0].metric_name == "bertscore"
    assert provider.prompts == ["prompt-factual-001"]


def test_runner_factual_repetitions(tmp_path: Path):
    judge = _StubJudge()
    provider = _RecordingProvider(default_text="Brasília")
    loader = _StubLoader({"factual": _bank("factual", [_factual_scenario()])})
    config = _make_config(output_dir=tmp_path, dimensions=["factual"], repetitions=3)
    runner = _make_runner(config, provider=provider, judge=judge, loader=loader)

    result = runner.run()
    sr = result.scenario_results[0]

    assert len(sr.responses) == 3
    assert len(sr.judge_results) == 3
    assert len(sr.metric_results) == 3
    assert provider.prompts == ["prompt-factual-001"] * 3


# ---------------------------------------------------------------------------
# Runner — consistency
# ---------------------------------------------------------------------------


def test_runner_consistency_sends_base_plus_variants(tmp_path: Path):
    judge = _StubJudge()
    provider = _RecordingProvider(default_text="Brasília")
    loader = _StubLoader({"consistency": _bank("consistency", [_consistency_scenario()])})
    config = _make_config(output_dir=tmp_path, dimensions=["consistency"])
    runner = _make_runner(config, provider=provider, judge=judge, loader=loader)

    result = runner.run()
    sr = result.scenario_results[0]

    assert provider.prompts == ["prompt-consistency-001", "paraphrase-1", "paraphrase-2"]
    assert len(sr.responses) == 1
    assert set(sr.variant_responses) == {"consistency-001-v1", "consistency-001-v2"}
    assert len(sr.judge_results) == 1
    assert sr.judge_results[0].dimension == "consistency"
    assert len(sr.metric_results) == 1
    assert sr.metric_results[0].metric_name == "consistency"
    assert sr.metric_results[0].details["num_responses"] == 3


# ---------------------------------------------------------------------------
# Runner — robustness
# ---------------------------------------------------------------------------


def test_runner_robustness_one_judge_per_variant(tmp_path: Path):
    judge = _StubJudge()
    provider = _RecordingProvider(default_text="Brasília")
    loader = _StubLoader({"robustness": _bank("robustness", [_robustness_scenario()])})
    config = _make_config(output_dir=tmp_path, dimensions=["robustness"])
    runner = _make_runner(config, provider=provider, judge=judge, loader=loader)

    result = runner.run()
    sr = result.scenario_results[0]

    assert provider.prompts == ["prompt-robustness-001", "typo-prompt", "adversarial-prompt"]
    assert len(sr.responses) == 1
    assert set(sr.variant_responses) == {"robustness-001-v1", "robustness-001-v2"}
    assert len(sr.judge_results) == 2
    assert all(jr.dimension == "robustness" for jr in sr.judge_results)
    assert len(sr.metric_results) == 2
    assert all(mr.metric_name == "bertscore" for mr in sr.metric_results)
    assert judge.robustness_calls[0]["variant_type"] == "typo"
    assert judge.robustness_calls[1]["variant_type"] == "adversarial"


# ---------------------------------------------------------------------------
# Runner — multiple dimensions and error isolation
# ---------------------------------------------------------------------------


def test_runner_iterates_over_all_dimensions(tmp_path: Path):
    judge = _StubJudge()
    provider = _RecordingProvider(default_text="Brasília")
    loader = _StubLoader(
        {
            "factual": _bank("factual", [_factual_scenario()]),
            "consistency": _bank("consistency", [_consistency_scenario()]),
            "robustness": _bank("robustness", [_robustness_scenario()]),
        }
    )
    config = _make_config(output_dir=tmp_path)
    runner = _make_runner(config, provider=provider, judge=judge, loader=loader)

    result = runner.run()

    dimensions_seen = [sr.dimension for sr in result.scenario_results]
    assert dimensions_seen == ["factual", "consistency", "robustness"]
    assert all(sr.error is None for sr in result.scenario_results)


def test_runner_handles_unsupported_dimension_at_scenario_level(tmp_path: Path):
    """If a Scenario somehow carries a non-standard dimension, the run continues."""
    judge = _StubJudge()
    provider = _RecordingProvider(default_text="ok")
    bogus_scenario = Scenario.model_construct(
        id="bogus-001",
        dimension="unsupported",
        category="knowledge",
        prompt="p",
        ground_truth="gt",
        variants=[],
    )
    bogus_bank = ScenarioBank.model_construct(
        dimension="factual", version="0.1.0", scenarios=[bogus_scenario]
    )
    loader = _StubLoader({"factual": bogus_bank})
    config = _make_config(output_dir=tmp_path, dimensions=["factual"])
    runner = _make_runner(config, provider=provider, judge=judge, loader=loader)

    result = runner.run()

    assert len(result.scenario_results) == 1
    assert result.scenario_results[0].error is not None
    assert "Unsupported dimension" in result.scenario_results[0].error


def test_runner_continues_after_failed_scenario(tmp_path: Path):
    judge = _StubJudge()
    provider = _RecordingProvider(
        default_text="Brasília",
        raise_for={"prompt-factual-002"},
    )
    loader = _StubLoader(
        {
            "factual": _bank(
                "factual",
                [
                    _factual_scenario("factual-001"),
                    _factual_scenario("factual-002"),
                    _factual_scenario("factual-003"),
                ],
            )
        }
    )
    config = _make_config(output_dir=tmp_path, dimensions=["factual"])
    runner = _make_runner(config, provider=provider, judge=judge, loader=loader)

    result = runner.run()

    assert len(result.scenario_results) == 3
    assert result.scenario_results[0].error is None
    assert result.scenario_results[1].error is not None
    assert "RuntimeError" in result.scenario_results[1].error
    assert result.scenario_results[2].error is None


# ---------------------------------------------------------------------------
# Runner — persistence (incremental + final)
# ---------------------------------------------------------------------------


def test_runner_writes_partial_then_final(tmp_path: Path):
    judge = _StubJudge()
    provider = _RecordingProvider(default_text="Brasília")
    loader = _StubLoader(
        {
            "factual": _bank(
                "factual",
                [_factual_scenario("factual-001"), _factual_scenario("factual-002")],
            )
        }
    )
    config = _make_config(output_dir=tmp_path, dimensions=["factual"])
    runner = _make_runner(config, provider=provider, judge=judge, loader=loader)

    runner.run()

    final_path = tmp_path / FINAL_FILENAME
    partial_path = tmp_path / PARTIAL_FILENAME
    assert final_path.exists()
    assert not partial_path.exists()  # cleaned up after success

    payload = json.loads(final_path.read_text(encoding="utf-8"))
    assert len(payload["scenario_results"]) == 2
    assert payload["finished_at"] is not None
    assert payload["config"]["provider"]["api_key"] == "***REDACTED***"


def test_runner_creates_output_dir_if_missing(tmp_path: Path):
    nested = tmp_path / "deeper" / "still" / "nested"
    judge = _StubJudge()
    provider = _RecordingProvider(default_text="Brasília")
    loader = _StubLoader({"factual": _bank("factual", [_factual_scenario()])})
    config = _make_config(output_dir=nested, dimensions=["factual"])
    runner = _make_runner(config, provider=provider, judge=judge, loader=loader)

    runner.run()

    assert (nested / FINAL_FILENAME).exists()


# ---------------------------------------------------------------------------
# RunResult / ScenarioResult model behavior
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Runner — judge.enabled = False
# ---------------------------------------------------------------------------


def test_runner_skips_judge_when_disabled(tmp_path: Path):
    """When config.judge.enabled is False, the judge is neither built nor called."""
    provider = _RecordingProvider(default_text="Brasília")
    loader = _StubLoader(
        {
            "factual": _bank("factual", [_factual_scenario()]),
            "consistency": _bank("consistency", [_consistency_scenario()]),
            "robustness": _bank("robustness", [_robustness_scenario()]),
        }
    )
    config = _make_config(output_dir=tmp_path)
    config.judge.enabled = False

    factory_calls: list[ProviderSettings] = []

    def tracking_factory(settings: ProviderSettings) -> BaseProvider:
        factory_calls.append(settings)
        return provider

    runner = Runner(
        config,
        scenarios_loader=loader,
        provider_factory=tracking_factory,
        bertscore_fn=_bertscore_stub,
        consistency_fn=_consistency_stub,
    )
    result = runner.run()

    # Factory called only once — for the target provider, not the judge.
    assert len(factory_calls) == 1
    # All scenarios still ran with metrics, just no judge evaluations.
    for sr in result.scenario_results:
        assert sr.error is None
        assert sr.judge_results == []
        assert len(sr.metric_results) > 0


def test_runner_uses_injected_judge_only_when_enabled(tmp_path: Path):
    """An injected judge is honored only if config.judge.enabled is True."""
    judge = _StubJudge()
    provider = _RecordingProvider(default_text="Brasília")
    loader = _StubLoader({"factual": _bank("factual", [_factual_scenario()])})
    config = _make_config(output_dir=tmp_path, dimensions=["factual"])
    config.judge.enabled = False
    runner = _make_runner(config, provider=provider, judge=judge, loader=loader)

    result = runner.run()

    assert judge.factual_calls == []
    assert result.scenario_results[0].judge_results == []


# ---------------------------------------------------------------------------
# Runner — Gemini dual-provider safety
# ---------------------------------------------------------------------------


def test_runner_rejects_gemini_with_different_keys(tmp_path: Path):
    """Two Gemini providers with different API keys must fail fast."""
    config = _make_config(output_dir=tmp_path)
    config.judge.provider = ProviderSettings(
        type="gemini", api_key="different-key", model="gemini-2.0-flash-001"
    )
    with pytest.raises(ValueError, match="two Gemini providers with different API keys"):
        Runner(
            config,
            scenarios_loader=_StubLoader({}),
            provider_factory=lambda _s: _RecordingProvider(),
            bertscore_fn=_bertscore_stub,
            consistency_fn=_consistency_stub,
        )


def test_runner_accepts_gemini_with_same_key(tmp_path: Path):
    """Two Gemini providers sharing the same API key are fine."""
    config = _make_config(output_dir=tmp_path)
    # Same provider object — keys match.
    runner = Runner(
        config,
        scenarios_loader=_StubLoader({}),
        provider_factory=lambda _s: _RecordingProvider(),
        bertscore_fn=_bertscore_stub,
        consistency_fn=_consistency_stub,
    )
    assert runner._judge is not None


def test_runner_skips_gemini_check_when_judge_disabled(tmp_path: Path):
    """Different keys are tolerated when the judge is disabled (it won't run)."""
    config = _make_config(output_dir=tmp_path)
    config.judge.enabled = False
    config.judge.provider = ProviderSettings(
        type="gemini", api_key="different-key", model="gemini-2.0-flash-001"
    )
    Runner(
        config,
        scenarios_loader=_StubLoader({}),
        provider_factory=lambda _s: _RecordingProvider(),
        bertscore_fn=_bertscore_stub,
        consistency_fn=_consistency_stub,
    )


def test_runner_allows_mixed_provider_types(tmp_path: Path):
    """Same-key check only triggers when both sides are Gemini."""
    config = _make_config(output_dir=tmp_path)
    config.judge.provider = ProviderSettings(
        type="mistral", api_key="any-key", model="mistral-small-2503"
    )
    Runner(
        config,
        scenarios_loader=_StubLoader({}),
        provider_factory=lambda _s: _RecordingProvider(),
        bertscore_fn=_bertscore_stub,
        consistency_fn=_consistency_stub,
    )


# ---------------------------------------------------------------------------
# Runner — provider close()
# ---------------------------------------------------------------------------


class _ClosableProvider(_RecordingProvider):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.closed = False

    def close(self) -> None:
        self.closed = True


def test_runner_closes_owned_providers_after_run(tmp_path: Path):
    """Both target provider and judge provider receive close() after the run."""
    target = _ClosableProvider(default_text="Brasília")
    judge_provider = _ClosableProvider(default_text='{"score": 5, "justification": "ok"}')
    loader = _StubLoader({"factual": _bank("factual", [_factual_scenario()])})
    config = _make_config(output_dir=tmp_path, dimensions=["factual"])

    factory_calls = {"n": 0}

    def factory(_settings: ProviderSettings) -> BaseProvider:
        factory_calls["n"] += 1
        return target if factory_calls["n"] == 1 else judge_provider

    runner = Runner(
        config,
        scenarios_loader=loader,
        provider_factory=factory,
        bertscore_fn=_bertscore_stub,
        consistency_fn=_consistency_stub,
    )
    runner.run()

    assert target.closed is True
    assert judge_provider.closed is True


def test_runner_closes_providers_even_on_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """If something blows up mid-run, providers are still closed."""
    target = _ClosableProvider(default_text="ok")
    loader = _StubLoader({"factual": _bank("factual", [_factual_scenario()])})

    config = _make_config(output_dir=tmp_path, dimensions=["factual"])
    config.judge.enabled = False
    runner = Runner(
        config,
        scenarios_loader=loader,
        provider_factory=lambda _s: target,
        bertscore_fn=_bertscore_stub,
        consistency_fn=_consistency_stub,
    )

    def boom(*_: Any, **__: Any) -> None:
        raise RuntimeError("collect failed")

    monkeypatch.setattr(runner, "_collect_scenarios", boom)

    with pytest.raises(RuntimeError, match="collect failed"):
        runner.run()
    assert target.closed is True


def test_runner_does_not_close_injected_judge_provider(tmp_path: Path):
    """When the caller provides a Judge directly, the runner does not own the
    judge's underlying provider and must not close it."""
    judge = _StubJudge()
    underlying_provider = judge.provider
    assert isinstance(underlying_provider, _RecordingProvider)
    target = _ClosableProvider(default_text="Brasília")
    loader = _StubLoader({"factual": _bank("factual", [_factual_scenario()])})
    config = _make_config(output_dir=tmp_path, dimensions=["factual"])
    runner = _make_runner(config, provider=target, judge=judge, loader=loader)

    runner.run()

    assert target.closed is True
    # The judge provider isn't a _ClosableProvider, but the key fact is the
    # runner skipped close() on it (no AttributeError on the base `close()`
    # no-op either).


def test_runner_swallows_close_errors(tmp_path: Path, caplog: pytest.LogCaptureFixture):
    """A failing close() is logged but does not interrupt the run.

    We also confirm both providers are still attempted, not just the first.
    """
    import logging as _logging

    class _FailingClose(_RecordingProvider):
        def __init__(self, **kwargs: Any) -> None:
            super().__init__(**kwargs)
            self.close_called = False

        def close(self) -> None:
            self.close_called = True
            raise RuntimeError("close failed")

    target = _FailingClose(default_text="Brasília")
    judge_provider = _FailingClose(default_text='{"score": 5, "justification": "ok"}')
    loader = _StubLoader({"factual": _bank("factual", [_factual_scenario()])})
    config = _make_config(output_dir=tmp_path, dimensions=["factual"])

    factory_calls = {"n": 0}

    def factory(_settings: ProviderSettings) -> BaseProvider:
        factory_calls["n"] += 1
        return target if factory_calls["n"] == 1 else judge_provider

    runner = Runner(
        config,
        scenarios_loader=loader,
        provider_factory=factory,
        bertscore_fn=_bertscore_stub,
        consistency_fn=_consistency_stub,
    )
    with caplog.at_level(_logging.WARNING):
        result = runner.run()

    assert result.scenario_results[0].error is None
    assert target.close_called is True
    assert judge_provider.close_called is True
    warnings = [rec for rec in caplog.records if "Failed to close provider" in rec.message]
    assert len(warnings) == 2


# ---------------------------------------------------------------------------
# Runner — atomic _save_json
# ---------------------------------------------------------------------------


def test_save_json_writes_via_tempfile_and_replace(tmp_path: Path):
    """The final file must contain valid JSON; no leftover .tmp file remains."""
    target = _RecordingProvider(default_text="Brasília")
    loader = _StubLoader({"factual": _bank("factual", [_factual_scenario()])})
    config = _make_config(output_dir=tmp_path, dimensions=["factual"])
    config.judge.enabled = False
    runner = _make_runner(config, provider=target, judge=_StubJudge(), loader=loader)
    runner.run()

    final_path = tmp_path / FINAL_FILENAME
    assert final_path.exists()
    payload = json.loads(final_path.read_text(encoding="utf-8"))
    assert payload["finished_at"] is not None

    leftovers = [p for p in tmp_path.iterdir() if p.name.startswith(f".{FINAL_FILENAME}")]
    assert leftovers == [], f"Stale tempfiles: {leftovers}"


def test_save_json_cleans_tempfile_on_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """If os.replace fails, the temporary file must be cleaned up."""
    import llm_eval.runner as runner_module

    target = _RecordingProvider(default_text="Brasília")
    loader = _StubLoader({"factual": _bank("factual", [_factual_scenario()])})
    config = _make_config(output_dir=tmp_path, dimensions=["factual"])
    config.judge.enabled = False
    runner = _make_runner(config, provider=target, judge=_StubJudge(), loader=loader)

    original_replace = runner_module.os.replace
    call_count = {"n": 0}

    def failing_replace(src: str, dst: str) -> None:
        call_count["n"] += 1
        if call_count["n"] == 1:
            raise OSError("disk full")
        original_replace(src, dst)

    monkeypatch.setattr(runner_module.os, "replace", failing_replace)

    with pytest.raises(OSError, match="disk full"):
        runner.run()

    # tempfile must have been cleaned up — no .partial.json.*.tmp leftover
    leftovers = [p for p in tmp_path.iterdir() if p.suffix == ".tmp"]
    assert leftovers == [], f"Stale tempfiles: {leftovers}"


# ---------------------------------------------------------------------------
# RunResult / ScenarioResult model behavior
# ---------------------------------------------------------------------------


def test_run_result_serializes_with_datetime():
    result = RunResult(
        config={"x": 1},
        started_at=datetime(2026, 5, 3, tzinfo=timezone.utc),
    )
    payload = result.model_dump(mode="json")
    assert payload["started_at"].startswith("2026-05-03")
    assert payload["finished_at"] is None
    assert payload["scenario_results"] == []


def test_scenario_result_rejects_extra_fields():
    with pytest.raises(Exception):
        ScenarioResult(
            scenario_id="x",
            dimension="factual",
            category="knowledge",
            prompt="p",
            unknown="oops",  # type: ignore[call-arg]
        )
