"""Geração de relatórios estruturados a partir de :class:`RunResult`.

Exporta dois formatos:

- **JSON**: payload consolidado com metadados, sumário agregado por dimensão,
  e detalhes por cenário (judge score + BERTScore + resposta + flags de
  qualidade do parse). Pensado para consumo programático e pipelines.
- **Markdown**: relatório legível com tabela-resumo, top piores cenários
  por dimensão, e seções com metadados e flags de atenção.

A computação de agregações (média, mediana, desvio padrão por dimensão) é
feita uma única vez via :meth:`ReportGenerator.summary`, e os dois formatos
de exportação consomem esse mesmo dicionário.
"""

from __future__ import annotations

import json
import os
import statistics
import tempfile
from datetime import datetime
from functools import cached_property
from pathlib import Path
from typing import Any

from llm_eval import __version__ as FRAMEWORK_VERSION
from llm_eval.runner import RunResult, ScenarioResult

DIMENSION_LABELS = {
    "factual": "Precisão Factual",
    "consistency": "Consistência Semântica",
    "robustness": "Robustez",
}


class ReportGenerator:
    """Produces structured reports (JSON, Markdown) from a :class:`RunResult`.

    Attributes:
        result: The completed run result to render.
        worst_n: How many lowest-scoring scenarios to highlight per dimension
            in the Markdown report. Defaults to 5.
    """

    def __init__(self, result: RunResult, *, worst_n: int = 5) -> None:
        """Initialize the generator with a completed run result.

        Args:
            result: The :class:`RunResult` produced by :class:`~llm_eval.runner.Runner`.
            worst_n: Number of lowest-scoring scenarios to highlight per
                dimension in the Markdown report. Negative values are clamped
                to zero.
        """
        self.result = result
        self.worst_n = max(0, int(worst_n))

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self) -> dict[str, Any]:
        """Return the aggregated payload used by both export formats.

        The structure is stable and documented as part of the public API:
        downstream consumers (notably the CLI ``report`` command) rely on
        the keys present here.

        The result is cached on the instance via :class:`functools.cached_property`,
        so calling :meth:`to_json` and :meth:`to_markdown` on the same generator
        only computes the aggregations once.
        """
        return self._cached_summary

    @cached_property
    def _cached_summary(self) -> dict[str, Any]:
        """Compute the report payload exactly once per generator instance."""
        scenario_summaries = [_scenario_summary(s) for s in self.result.scenario_results]

        by_dimension: dict[str, dict[str, Any]] = {}
        successful_scores: list[float] = []
        for dimension in _ordered_dimensions(scenario_summaries):
            scores = [
                item["judge_score"]
                for item in scenario_summaries
                if item["dimension"] == dimension and item["judge_score"] is not None
            ]
            failures = [
                item
                for item in scenario_summaries
                if item["dimension"] == dimension and item["error"]
            ]
            count = sum(1 for item in scenario_summaries if item["dimension"] == dimension)

            stats = _stats_for_scores(scores)
            by_dimension[dimension] = {
                **stats,
                "count": count,
                "evaluated": len(scores),
                "failed": len(failures),
            }
            successful_scores.extend(scores)

        overall_mean = round(statistics.mean(successful_scores), 4) if successful_scores else None

        metadata = self._build_metadata(scenario_summaries)
        return {
            "metadata": metadata,
            "summary": {
                "overall_score": overall_mean,
                "by_dimension": by_dimension,
            },
            "details": scenario_summaries,
        }

    # ------------------------------------------------------------------
    # Exporters
    # ------------------------------------------------------------------

    def to_json(self, path: str | Path) -> Path:
        """Render the report as JSON. Returns the resolved output ``Path``."""
        target = Path(path)
        payload = self.summary()
        _atomic_write_text(
            target,
            json.dumps(payload, indent=2, ensure_ascii=False, default=_json_default),
        )
        return target

    def to_markdown(self, path: str | Path) -> Path:
        """Render the report as Markdown. Returns the resolved output ``Path``."""
        target = Path(path)
        payload = self.summary()
        _atomic_write_text(target, _render_markdown(payload, worst_n=self.worst_n))
        return target

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _build_metadata(self, scenario_summaries: list[dict[str, Any]]) -> dict[str, Any]:
        config = self.result.config
        provider_cfg = config.get("provider", {}) if isinstance(config, dict) else {}
        return {
            "framework_version": FRAMEWORK_VERSION,
            "started_at": _isoformat(self.result.started_at),
            "finished_at": _isoformat(self.result.finished_at),
            "duration_seconds": _duration_seconds(self.result.started_at, self.result.finished_at),
            "provider_type": provider_cfg.get("type"),
            "model": provider_cfg.get("model"),
            "seed": provider_cfg.get("seed"),
            "temperature": provider_cfg.get("temperature"),
            "total_scenarios": len(scenario_summaries),
            "scenarios_with_error": sum(1 for s in scenario_summaries if s["error"]),
            "dimensions_evaluated": _ordered_dimensions(scenario_summaries),
        }


# ---------------------------------------------------------------------------
# Per-scenario summary
# ---------------------------------------------------------------------------


def _scenario_summary(scenario: ScenarioResult) -> dict[str, Any]:
    judge_scores = [jr.score for jr in scenario.judge_results]
    judge_score = round(statistics.mean(judge_scores), 4) if judge_scores else None
    judge_justification = (
        scenario.judge_results[0].justification if scenario.judge_results else None
    )
    judge_fallback = any(jr.metadata.get("justification_fallback") for jr in scenario.judge_results)
    parse_methods = sorted(
        {jr.metadata.get("parse_method", "json") for jr in scenario.judge_results}
    )

    bertscore_values = [m.value for m in scenario.metric_results if m.metric_name == "bertscore"]
    consistency_values = [
        m.value for m in scenario.metric_results if m.metric_name == "consistency"
    ]
    bertscore_f1 = round(statistics.mean(bertscore_values), 4) if bertscore_values else None
    consistency_score = (
        round(statistics.mean(consistency_values), 4) if consistency_values else None
    )

    response_text = scenario.responses[0].response_text if scenario.responses else None

    return {
        "scenario_id": scenario.scenario_id,
        "dimension": scenario.dimension,
        "category": scenario.category,
        "prompt": scenario.prompt,
        "judge_score": judge_score,
        "judge_justification": judge_justification,
        "judge_parse_methods": parse_methods,
        "judge_fallback": judge_fallback,
        "bertscore_f1": bertscore_f1,
        "consistency_score": consistency_score,
        "response_text": response_text,
        "error": scenario.error,
    }


# ---------------------------------------------------------------------------
# Statistics helpers
# ---------------------------------------------------------------------------


def _stats_for_scores(scores: list[float]) -> dict[str, float | None]:
    if not scores:
        return {"mean": None, "median": None, "stdev": None, "min": None, "max": None}
    mean = round(statistics.mean(scores), 4)
    median = round(statistics.median(scores), 4)
    stdev = round(statistics.stdev(scores), 4) if len(scores) > 1 else 0.0
    return {
        "mean": mean,
        "median": median,
        "stdev": stdev,
        "min": float(min(scores)),
        "max": float(max(scores)),
    }


def _ordered_dimensions(scenario_summaries: list[dict[str, Any]]) -> list[str]:
    """Return dimensions in canonical order, preserving only those present."""
    seen = {item["dimension"] for item in scenario_summaries}
    canonical = ["factual", "consistency", "robustness"]
    ordered = [dim for dim in canonical if dim in seen]
    extras = sorted(d for d in seen if d not in canonical)
    return ordered + extras


def _isoformat(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _duration_seconds(started_at: datetime, finished_at: datetime | None) -> float | None:
    if finished_at is None:
        return None
    return round((finished_at - started_at).total_seconds(), 3)


def _json_default(value: Any) -> Any:
    """Fallback serializer for objects that ``json`` does not handle natively."""
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def _render_markdown(payload: dict[str, Any], *, worst_n: int) -> str:
    metadata = payload["metadata"]
    summary = payload["summary"]
    details: list[dict[str, Any]] = payload["details"]

    lines: list[str] = []
    lines.append("# Relatório de Avaliação — llm-eval")
    lines.append("")
    lines.append(_render_metadata_section(metadata))
    lines.append("")
    lines.append(_render_summary_section(summary))
    lines.append("")
    lines.append(_render_attention_section(details))
    lines.append("")
    lines.extend(_render_dimension_sections(summary, details, worst_n=worst_n))
    return "\n".join(lines).rstrip() + "\n"


def _render_metadata_section(metadata: dict[str, Any]) -> str:
    lines = ["## Metadados", ""]
    rows = [
        ("Versão do framework", metadata.get("framework_version")),
        ("Iniciado em", metadata.get("started_at")),
        ("Concluído em", metadata.get("finished_at")),
        ("Duração (s)", metadata.get("duration_seconds")),
        ("Provider", metadata.get("provider_type")),
        ("Modelo", metadata.get("model")),
        ("Seed", metadata.get("seed")),
        ("Temperature", metadata.get("temperature")),
        ("Total de cenários", metadata.get("total_scenarios")),
        ("Cenários com erro", metadata.get("scenarios_with_error")),
    ]
    for label, value in rows:
        lines.append(f"- **{label}:** {_fmt(value)}")
    dims = metadata.get("dimensions_evaluated") or []
    pretty_dims = ", ".join(DIMENSION_LABELS.get(d, d) for d in dims) or "—"
    lines.append(f"- **Dimensões avaliadas:** {pretty_dims}")
    return "\n".join(lines)


def _render_summary_section(summary: dict[str, Any]) -> str:
    lines = ["## Resumo", ""]
    lines.append(
        "| Dimensão | Média | Mediana | Desvio Padrão | Min | Max | Cenários | Avaliados | Falhas |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for dim, stats in summary["by_dimension"].items():
        lines.append(
            f"| {DIMENSION_LABELS.get(dim, dim)} "
            f"| {_fmt(stats['mean'])} "
            f"| {_fmt(stats['median'])} "
            f"| {_fmt(stats['stdev'])} "
            f"| {_fmt(stats['min'])} "
            f"| {_fmt(stats['max'])} "
            f"| {stats['count']} "
            f"| {stats['evaluated']} "
            f"| {stats['failed']} |"
        )
    overall = summary.get("overall_score")
    lines.append("")
    lines.append(f"**Score geral (média entre cenários avaliados):** {_fmt(overall)}")
    return "\n".join(lines)


def _render_attention_section(details: list[dict[str, Any]]) -> str:
    failed = [item for item in details if item["error"]]
    fallbacks = [item for item in details if item["judge_fallback"] and not item["error"]]
    if not failed and not fallbacks:
        return ""

    lines = ["## Pontos de atenção", ""]
    if failed:
        lines.append(f"### Cenários com erro ({len(failed)})")
        lines.append("")
        for item in failed:
            lines.append(f"- `{item['scenario_id']}` — {item['error']}")
        lines.append("")
    if fallbacks:
        lines.append(f"### Cenários com justificativa fallback do juiz ({len(fallbacks)})")
        lines.append("")
        lines.append(
            "Estes cenários produziram score, mas o juiz não retornou justificativa "
            "parseable. Considere revisar manualmente:"
        )
        lines.append("")
        for item in fallbacks:
            lines.append(
                f"- `{item['scenario_id']}` ({item['dimension']}) — "
                f"score {_fmt(item['judge_score'])}, "
                f"parse_methods={item['judge_parse_methods']}"
            )
    return "\n".join(lines).rstrip()


def _render_dimension_sections(
    summary: dict[str, Any],
    details: list[dict[str, Any]],
    *,
    worst_n: int,
) -> list[str]:
    lines: list[str] = ["## Detalhes por Dimensão", ""]
    for dim in summary["by_dimension"]:
        label = DIMENSION_LABELS.get(dim, dim)
        scenarios_in_dim = [item for item in details if item["dimension"] == dim]
        if not scenarios_in_dim:
            continue
        lines.append(f"### {label}")
        lines.append("")
        scored = [item for item in scenarios_in_dim if item["judge_score"] is not None]
        if scored:
            scored_sorted = sorted(scored, key=lambda i: i["judge_score"])
            worst = scored_sorted[:worst_n] if worst_n else []
            if worst:
                lines.append(f"**Top {len(worst)} piores cenários:**")
                lines.append("")
                for item in worst:
                    lines.append(_render_scenario_detail(item))
                    lines.append("")
        else:
            lines.append("_Sem cenários avaliados nesta dimensão._")
            lines.append("")
    return lines


def _render_scenario_detail(item: dict[str, Any]) -> str:
    parts = [
        f"- **`{item['scenario_id']}`** (`{item['category']}`)",
        f"  - **Score:** {_fmt(item['judge_score'])}",
    ]
    if item["bertscore_f1"] is not None:
        parts.append(f"  - **BERTScore F1:** {_fmt(item['bertscore_f1'])}")
    if item["consistency_score"] is not None:
        parts.append(
            f"  - **Consistência (BERTScore par-a-par):** {_fmt(item['consistency_score'])}"
        )
    parts.append(f"  - **Prompt:** {_md_escape(item['prompt'])}")
    if item["response_text"] is not None:
        parts.append(f"  - **Resposta:** {_md_escape(_truncate_md(item['response_text'], 300))}")
    if item["judge_justification"]:
        parts.append(
            f"  - **Justificativa do juiz:** {_md_escape(_truncate_md(item['judge_justification'], 300))}"
        )
    if item["judge_fallback"]:
        parts.append("  - ⚠ Justificativa do juiz é fallback (parse incompleto)")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------


def _fmt(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.4f}".rstrip("0").rstrip(".") or "0"
    return str(value)


def _md_escape(text: str) -> str:
    """Escape pipes so values stay inside Markdown table cells."""
    return text.replace("|", "\\|").replace("\n", " ").strip()


def _truncate_md(text: str, limit: int) -> str:
    text = text.replace("\n", " ").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


# ---------------------------------------------------------------------------
# Atomic write (mirrors Runner._save_json)
# ---------------------------------------------------------------------------


def _atomic_write_text(path: Path, content: str) -> None:
    directory = path.parent
    directory.mkdir(parents=True, exist_ok=True)

    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=directory)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(content)
            fh.flush()
            try:
                os.fsync(fh.fileno())
            except OSError:  # pragma: no cover - filesystem-dependent
                pass
        os.replace(tmp_path, path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise
