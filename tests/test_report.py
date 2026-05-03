"""Testes para ``llm_eval.report.ReportGenerator``."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from llm_eval.evaluation.judge import JudgeResult
from llm_eval.evaluation.metrics import MetricResult
from llm_eval.providers.base import ProviderResponse
from llm_eval.report import (
    DIMENSION_LABELS,
    ReportGenerator,
    _atomic_write_text,
    _md_escape,
    _truncate_md,
)
from llm_eval.runner import RunResult, ScenarioResult


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------


def _provider_response(text: str = "Brasília") -> ProviderResponse:
    return ProviderResponse(
        response_text=text,
        model="gemini-2.0-flash-001",
        timestamp=datetime(2026, 5, 1, tzinfo=timezone.utc),
        response_time_ms=12.5,
        parameters={"temperature": 0.0, "seed": 42},
    )


def _judge(
    score: int, *, justification: str = "ok", parse_method: str = "json", fallback: bool = False
) -> JudgeResult:
    metadata: dict[str, Any] = {"parse_method": parse_method, "judge_model": "gemini-2.0-flash-001"}
    if fallback:
        metadata["justification_fallback"] = True
    return JudgeResult(
        dimension="factual", score=score, justification=justification, metadata=metadata
    )


def _bertscore(value: float = 0.92) -> MetricResult:
    return MetricResult(
        metric_name="bertscore",
        value=value,
        details={"precision": value, "recall": value, "f1": value, "lang": "pt"},
    )


def _consistency_metric(value: float = 0.85) -> MetricResult:
    return MetricResult(metric_name="consistency", value=value, details={"num_responses": 3})


def _factual_scenario(
    scenario_id: str = "fact-001",
    *,
    score: int = 5,
    bertscore: float = 0.92,
    error: str | None = None,
    judge_fallback: bool = False,
) -> ScenarioResult:
    if error is not None:
        return ScenarioResult(
            scenario_id=scenario_id,
            dimension="factual",
            category="knowledge",
            prompt="Qual é a capital do Brasil?",
            error=error,
        )
    judge = _judge(
        score, fallback=judge_fallback, parse_method="default" if judge_fallback else "json"
    )
    return ScenarioResult(
        scenario_id=scenario_id,
        dimension="factual",
        category="knowledge",
        prompt="Qual é a capital do Brasil?",
        responses=[_provider_response()],
        judge_results=[judge],
        metric_results=[_bertscore(bertscore)],
    )


def _consistency_scenario(scenario_id: str = "cons-001", score: int = 4) -> ScenarioResult:
    judge = JudgeResult(
        dimension="consistency",
        score=score,
        justification="boa consistência",
        metadata={"parse_method": "json"},
    )
    return ScenarioResult(
        scenario_id=scenario_id,
        dimension="consistency",
        category="knowledge",
        prompt="Qual é a capital do Brasil?",
        responses=[_provider_response()],
        judge_results=[judge],
        metric_results=[_consistency_metric()],
    )


def _robustness_scenario(scenario_id: str = "rob-001", score: int = 3) -> ScenarioResult:
    judge = JudgeResult(
        dimension="robustness",
        score=score,
        justification="manteve",
        metadata={"parse_method": "json"},
    )
    return ScenarioResult(
        scenario_id=scenario_id,
        dimension="robustness",
        category="knowledge",
        prompt="Qual é a capital do Brasil?",
        responses=[_provider_response()],
        judge_results=[judge],
        metric_results=[_bertscore(0.88)],
    )


def _run_result(scenarios: list[ScenarioResult], *, finished: bool = True) -> RunResult:
    started = datetime(2026, 5, 1, 10, 0, tzinfo=timezone.utc)
    return RunResult(
        config={
            "provider": {
                "type": "gemini",
                "model": "gemini-2.0-flash-001",
                "seed": 42,
                "temperature": 0.0,
                "api_key": "***REDACTED***",
            },
            "judge": {
                "enabled": True,
                "provider": {"type": "gemini", "model": "gemini-2.0-flash-001"},
            },
        },
        started_at=started,
        finished_at=started + timedelta(minutes=15) if finished else None,
        scenario_results=scenarios,
    )


# ---------------------------------------------------------------------------
# summary()
# ---------------------------------------------------------------------------


def test_summary_aggregates_per_dimension():
    result = _run_result(
        [
            _factual_scenario("fact-001", score=5, bertscore=0.95),
            _factual_scenario("fact-002", score=3, bertscore=0.80),
            _consistency_scenario("cons-001", score=4),
            _robustness_scenario("rob-001", score=2),
        ]
    )
    payload = ReportGenerator(result).summary()

    assert payload["metadata"]["total_scenarios"] == 4
    assert payload["metadata"]["scenarios_with_error"] == 0
    assert payload["metadata"]["model"] == "gemini-2.0-flash-001"
    assert payload["metadata"]["seed"] == 42

    by_dim = payload["summary"]["by_dimension"]
    assert by_dim["factual"]["mean"] == 4.0
    assert by_dim["factual"]["median"] == 4.0
    assert by_dim["factual"]["count"] == 2
    assert by_dim["factual"]["evaluated"] == 2
    assert by_dim["factual"]["failed"] == 0
    assert by_dim["consistency"]["mean"] == 4.0
    assert by_dim["consistency"]["stdev"] == 0.0  # single score
    assert by_dim["robustness"]["mean"] == 2.0

    overall = payload["summary"]["overall_score"]
    assert overall == pytest.approx(3.5, abs=0.001)


def test_summary_includes_per_scenario_details():
    result = _run_result([_factual_scenario("fact-001", score=4, bertscore=0.85)])
    payload = ReportGenerator(result).summary()

    detail = payload["details"][0]
    assert detail["scenario_id"] == "fact-001"
    assert detail["dimension"] == "factual"
    assert detail["judge_score"] == 4
    assert detail["bertscore_f1"] == 0.85
    assert detail["judge_parse_methods"] == ["json"]
    assert detail["judge_fallback"] is False
    assert detail["response_text"] == "Brasília"
    assert detail["error"] is None


def test_summary_handles_failed_scenario():
    result = _run_result(
        [
            _factual_scenario("fact-001", score=5),
            _factual_scenario("fact-002", error="RuntimeError: boom"),
        ]
    )
    payload = ReportGenerator(result).summary()
    by_dim = payload["summary"]["by_dimension"]
    assert by_dim["factual"]["count"] == 2
    assert by_dim["factual"]["evaluated"] == 1
    assert by_dim["factual"]["failed"] == 1
    assert by_dim["factual"]["mean"] == 5.0  # only the successful one
    assert payload["metadata"]["scenarios_with_error"] == 1


def test_summary_marks_judge_fallback():
    result = _run_result([_factual_scenario("fact-001", score=3, judge_fallback=True)])
    payload = ReportGenerator(result).summary()
    detail = payload["details"][0]
    assert detail["judge_fallback"] is True
    assert "default" in detail["judge_parse_methods"]


def test_summary_overall_none_when_all_scenarios_failed():
    result = _run_result(
        [
            _factual_scenario("fact-001", error="x"),
            _factual_scenario("fact-002", error="y"),
        ]
    )
    payload = ReportGenerator(result).summary()
    assert payload["summary"]["overall_score"] is None
    assert payload["summary"]["by_dimension"]["factual"]["mean"] is None
    assert payload["summary"]["by_dimension"]["factual"]["evaluated"] == 0


def test_summary_dimensions_in_canonical_order():
    """Even if scenarios arrive in odd order, dimensions are canonicalized."""
    result = _run_result(
        [
            _robustness_scenario("rob-001"),
            _factual_scenario("fact-001", score=5),
            _consistency_scenario("cons-001"),
        ]
    )
    payload = ReportGenerator(result).summary()
    assert list(payload["summary"]["by_dimension"]) == ["factual", "consistency", "robustness"]


def test_summary_empty_run():
    result = _run_result([])
    payload = ReportGenerator(result).summary()
    assert payload["metadata"]["total_scenarios"] == 0
    assert payload["summary"]["overall_score"] is None
    assert payload["summary"]["by_dimension"] == {}


def test_summary_unfinished_run_has_no_duration():
    result = _run_result([_factual_scenario("fact-001", score=5)], finished=False)
    payload = ReportGenerator(result).summary()
    assert payload["metadata"]["finished_at"] is None
    assert payload["metadata"]["duration_seconds"] is None


def test_ordered_dimensions_keeps_canonical_order_and_appends_extras():
    """Direct test of the ordering helper: canonical dims come first, extras
    sort alphabetically. The previous version of this test created a
    ``factual`` scenario and asserted something trivially true — replaced
    here with a real exercise of the helper."""
    from llm_eval.report import _ordered_dimensions

    summaries = [
        {"dimension": "robustness"},
        {"dimension": "zeta"},
        {"dimension": "factual"},
        {"dimension": "alpha"},
        {"dimension": "consistency"},
    ]
    assert _ordered_dimensions(summaries) == [
        "factual",
        "consistency",
        "robustness",
        "alpha",
        "zeta",
    ]


def test_ordered_dimensions_only_canonical():
    from llm_eval.report import _ordered_dimensions

    summaries = [{"dimension": "consistency"}, {"dimension": "factual"}]
    assert _ordered_dimensions(summaries) == ["factual", "consistency"]


def test_summary_is_cached_across_exporters(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """to_json + to_markdown on the same generator must compute the summary
    exactly once. Calling generator.summary() multiple times must also reuse
    the cached value."""
    from llm_eval import report as report_module

    result = _run_result(
        [
            _factual_scenario("fact-001", score=5),
            _factual_scenario("fact-002", score=3),
            _consistency_scenario("cons-001"),
        ]
    )
    call_count = {"n": 0}
    real_scenario_summary = report_module._scenario_summary

    def counting_summary(scenario: ScenarioResult) -> dict[str, Any]:
        call_count["n"] += 1
        return real_scenario_summary(scenario)

    monkeypatch.setattr(report_module, "_scenario_summary", counting_summary)

    generator = ReportGenerator(result)
    generator.to_json(tmp_path / "report.json")
    generator.to_markdown(tmp_path / "report.md")
    generator.summary()

    # 3 scenarios x 1 pass = 3 calls. If the cache were missing it would be
    # 9 (3 scenarios x 3 entry points: to_json, to_markdown, summary).
    assert call_count["n"] == 3


def test_summary_exposes_min_max_per_dimension():
    result = _run_result(
        [
            _factual_scenario("fact-001", score=5),
            _factual_scenario("fact-002", score=2),
            _factual_scenario("fact-003", score=4),
        ]
    )
    payload = ReportGenerator(result).summary()
    stats = payload["summary"]["by_dimension"]["factual"]
    assert stats["min"] == 2.0
    assert stats["max"] == 5.0


# ---------------------------------------------------------------------------
# to_json()
# ---------------------------------------------------------------------------


def test_to_json_writes_valid_payload(tmp_path: Path):
    result = _run_result([_factual_scenario("fact-001", score=5)])
    target = tmp_path / "report.json"
    written = ReportGenerator(result).to_json(target)
    assert written == target

    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload["metadata"]["model"] == "gemini-2.0-flash-001"
    assert payload["details"][0]["scenario_id"] == "fact-001"


def test_to_json_creates_parent_directory(tmp_path: Path):
    result = _run_result([_factual_scenario("fact-001", score=5)])
    target = tmp_path / "nested" / "deep" / "report.json"
    ReportGenerator(result).to_json(target)
    assert target.exists()


def test_to_json_atomic_write_leaves_no_tempfile_on_success(tmp_path: Path):
    result = _run_result([_factual_scenario("fact-001", score=5)])
    target = tmp_path / "report.json"
    ReportGenerator(result).to_json(target)
    leftovers = [p for p in tmp_path.iterdir() if p.suffix == ".tmp"]
    assert leftovers == []


# ---------------------------------------------------------------------------
# to_markdown()
# ---------------------------------------------------------------------------


def test_to_markdown_renders_header_and_summary_table(tmp_path: Path):
    result = _run_result(
        [
            _factual_scenario("fact-001", score=5, bertscore=0.95),
            _factual_scenario("fact-002", score=3, bertscore=0.80),
            _consistency_scenario("cons-001", score=4),
        ]
    )
    target = tmp_path / "report.md"
    ReportGenerator(result).to_markdown(target)

    content = target.read_text(encoding="utf-8")
    assert content.startswith("# Relatório de Avaliação")
    assert "## Metadados" in content
    assert "## Resumo" in content
    assert DIMENSION_LABELS["factual"] in content
    assert DIMENSION_LABELS["consistency"] in content
    assert "**Score geral" in content


def test_to_markdown_includes_attention_section_for_failures(tmp_path: Path):
    result = _run_result(
        [
            _factual_scenario("fact-001", score=5),
            _factual_scenario("fact-002", error="RuntimeError: boom"),
            _factual_scenario("fact-003", score=2, judge_fallback=True),
        ]
    )
    target = tmp_path / "report.md"
    ReportGenerator(result).to_markdown(target)

    content = target.read_text(encoding="utf-8")
    assert "## Pontos de atenção" in content
    assert "fact-002" in content
    assert "RuntimeError: boom" in content
    assert "fallback" in content.lower()
    assert "fact-003" in content


def test_to_markdown_omits_attention_when_clean(tmp_path: Path):
    result = _run_result([_factual_scenario("fact-001", score=5)])
    target = tmp_path / "report.md"
    ReportGenerator(result).to_markdown(target)
    content = target.read_text(encoding="utf-8")
    assert "## Pontos de atenção" not in content


def test_to_markdown_lists_worst_scenarios_per_dimension(tmp_path: Path):
    result = _run_result(
        [
            _factual_scenario("fact-001", score=5),
            _factual_scenario("fact-002", score=2),
            _factual_scenario("fact-003", score=4),
            _factual_scenario("fact-004", score=1),
        ]
    )
    target = tmp_path / "report.md"
    ReportGenerator(result, worst_n=2).to_markdown(target)
    content = target.read_text(encoding="utf-8")
    assert "Top 2 piores cenários" in content
    # Worst (1) should appear before second-worst (2)
    pos_4 = content.index("fact-004")
    pos_2 = content.index("fact-002")
    assert pos_4 < pos_2


def test_to_markdown_handles_dimension_with_no_evaluated_scenarios(tmp_path: Path):
    """Dimension with only failed scenarios still renders a section."""
    result = _run_result(
        [
            _factual_scenario("fact-001", error="boom"),
            _factual_scenario("fact-002", error="boom"),
        ]
    )
    target = tmp_path / "report.md"
    ReportGenerator(result).to_markdown(target)
    content = target.read_text(encoding="utf-8")
    assert DIMENSION_LABELS["factual"] in content
    assert "Sem cenários avaliados" in content


def test_to_markdown_zero_worst_n_disables_listing(tmp_path: Path):
    result = _run_result([_factual_scenario("fact-001", score=2)])
    target = tmp_path / "report.md"
    ReportGenerator(result, worst_n=0).to_markdown(target)
    content = target.read_text(encoding="utf-8")
    assert "piores cenários" not in content


def test_to_markdown_escapes_pipes_in_prompt(tmp_path: Path):
    scenario = ScenarioResult(
        scenario_id="x-001",
        dimension="factual",
        category="knowledge",
        prompt="A | B",
        responses=[_provider_response("R | with | pipes")],
        judge_results=[_judge(2, justification="just|ification")],
        metric_results=[_bertscore()],
    )
    result = _run_result([scenario])
    target = tmp_path / "report.md"
    ReportGenerator(result).to_markdown(target)
    content = target.read_text(encoding="utf-8")
    assert "A \\| B" in content
    assert "R \\| with \\| pipes" in content


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def test_md_escape_newlines_become_space():
    assert _md_escape("foo\nbar") == "foo bar"


def test_md_escape_strips():
    assert _md_escape("  hi  ") == "hi"


def test_truncate_md_short_unchanged():
    assert _truncate_md("hi", 10) == "hi"


def test_truncate_md_long_with_ellipsis():
    out = _truncate_md("a" * 100, 20)
    assert len(out) == 20
    assert out.endswith("…")


def test_atomic_write_text_cleans_tempfile_on_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    import llm_eval.report as report_module

    target = tmp_path / "out.md"

    def failing_replace(src: str, dst: str) -> None:
        raise OSError("disk full")

    monkeypatch.setattr(report_module.os, "replace", failing_replace)
    with pytest.raises(OSError, match="disk full"):
        _atomic_write_text(target, "hello")
    leftovers = [p for p in tmp_path.iterdir() if p.suffix == ".tmp"]
    assert leftovers == []


# ---------------------------------------------------------------------------
# Round-trip via ReportGenerator
# ---------------------------------------------------------------------------


def test_json_export_round_trips_through_runresult(tmp_path: Path):
    """The JSON written by ReportGenerator should be parseable as JSON, regardless
    of source format. (RunResult itself is not the JSON shape — that's report.json.)"""
    result = _run_result([_factual_scenario("fact-001", score=5)])
    target = tmp_path / "report.json"
    ReportGenerator(result).to_json(target)
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert "metadata" in payload
    assert "summary" in payload
    assert "details" in payload
