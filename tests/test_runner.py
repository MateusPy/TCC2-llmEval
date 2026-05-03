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
        model="gemini-2.0-flash",
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
    assert data["provider"]["model"] == "gemini-2.0-flash"


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
