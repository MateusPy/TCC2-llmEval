"""Validation of the LLM-as-a-Judge component against a golden set.

This module compares the judge's 1-5 scores against a human-annotated golden
set and reports agreement metrics that are standard in the evaluation
literature: weighted Cohen's Kappa, Pearson correlation, and mean absolute
error (MAE).

The shipped golden set is intentionally synthetic and exists to exercise the
validation pipeline end-to-end. For scientifically defensible results, replace
it with real human annotations collected under the protocol described in the
README and rerun the validation command.
"""

from __future__ import annotations

import json
import logging
import math
import statistics
from importlib import resources
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from llm_eval.evaluation.judge import ALLOWED_DIMENSIONS, Judge, JudgeResult

logger = logging.getLogger(__name__)

DEFAULT_GOLDEN_SET_PACKAGE = "llm_eval.scenarios.golden"
DEFAULT_GOLDEN_SET_FILE = "golden_set.json"
HIGH_DISAGREEMENT_THRESHOLD = 2.0


class JudgeValidationError(Exception):
    """Raised when the golden set cannot be loaded or fails validation."""


class HumanScore(BaseModel):
    """Single human annotation for a golden-set scenario.

    Attributes:
        annotator_id: Stable identifier for the human annotator.
        score: Ordinal score on the shared 1-5 rubric.
        justification: Short explanation supporting the score.
    """

    model_config = ConfigDict(extra="forbid")

    annotator_id: str
    score: int = Field(ge=1, le=5)
    justification: str


class GoldenScenario(BaseModel):
    """One scenario in the golden validation set.

    The exact fields used depend on the dimension:

    - ``factual``: requires ``ground_truth`` and ``chatbot_response``
    - ``consistency``: requires ``chatbot_response`` plus at least one entry in
      ``comparison_responses``
    - ``robustness``: requires ``original_response``, ``variant_type``,
      ``variant_prompt`` and the variant's ``chatbot_response``

    Attributes:
        id: Unique identifier of the scenario.
        dimension: One of the framework's supported reliability dimensions.
        prompt: Original user prompt.
        category: Optional topical category for analysis.
        ground_truth: Expected answer for factual scenarios.
        chatbot_response: Chatbot answer being judged. For robustness, this is
            the answer to the perturbed prompt.
        comparison_responses: Additional responses used by consistency
            validation.
        original_response: Answer to the original prompt, used by robustness.
        variant_type: Perturbation category for robustness.
        variant_prompt: Perturbed prompt for robustness.
        human_scores: Human annotations for this scenario.
        human_consensus_score: Consensus score derived from the median of the
            human scores.
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    dimension: str
    prompt: str
    category: str | None = None
    ground_truth: str | None = None
    chatbot_response: str
    comparison_responses: list[str] = Field(default_factory=list)
    original_response: str | None = None
    variant_type: str | None = None
    variant_prompt: str | None = None
    human_scores: list[HumanScore]
    human_consensus_score: int = Field(ge=1, le=5)

    @field_validator("dimension")
    @classmethod
    def _validate_dimension(cls, value: str) -> str:
        if value not in ALLOWED_DIMENSIONS:
            raise ValueError(
                f"Invalid dimension '{value}'. Allowed values: {list(ALLOWED_DIMENSIONS)}"
            )
        return value

    @model_validator(mode="after")
    def _validate_structure(self) -> "GoldenScenario":
        n = len(self.human_scores)
        if n < 3:
            raise ValueError(f"Golden scenario '{self.id}' must have at least 3 human annotations")
        if n % 2 == 0:
            raise ValueError(
                f"Golden scenario '{self.id}' must have an odd number of annotations so "
                f"the median consensus is unambiguous (got {n})"
            )

        expected_consensus = _median_score(annotation.score for annotation in self.human_scores)
        if self.human_consensus_score != expected_consensus:
            raise ValueError(
                f"Golden scenario '{self.id}' has consensus {self.human_consensus_score}, "
                f"but the annotations imply {expected_consensus}"
            )

        if self.dimension == "factual":
            if not self.ground_truth:
                raise ValueError(f"Factual golden scenario '{self.id}' requires ground_truth")
        elif self.dimension == "consistency":
            if len([self.chatbot_response, *self.comparison_responses]) < 2:
                raise ValueError(
                    f"Consistency golden scenario '{self.id}' requires at least two responses"
                )
        elif self.dimension == "robustness":
            missing = [
                name
                for name, value in (
                    ("original_response", self.original_response),
                    ("variant_type", self.variant_type),
                    ("variant_prompt", self.variant_prompt),
                )
                if not value
            ]
            if missing:
                raise ValueError(
                    f"Robustness golden scenario '{self.id}' is missing required fields: {missing}"
                )
        return self


class GoldenSet(BaseModel):
    """Container for the validation dataset and its annotation protocol."""

    model_config = ConfigDict(extra="forbid")

    version: str
    annotation_protocol: dict[str, Any] = Field(default_factory=dict)
    scenarios: list[GoldenScenario] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_non_empty(self) -> "GoldenSet":
        if not self.scenarios:
            raise ValueError("Golden set must contain at least one scenario")
        return self


class ValidationMetricSummary(BaseModel):
    """Agreement metrics for one slice of the validation run.

    Attributes:
        kappa: Linearly weighted Cohen's Kappa.
        pearson_correlation: Pearson correlation between judge and consensus.
        mae: Mean absolute error between judge and consensus.
        agreement_label: Human-readable label derived from ``kappa``.
        total_scenarios: Number of scenarios in this slice.
        evaluated_scenarios: Number of scenarios that produced a judge score.
    """

    model_config = ConfigDict(extra="forbid")

    kappa: float
    pearson_correlation: float
    mae: float
    agreement_label: str
    total_scenarios: int
    evaluated_scenarios: int


class ValidationScenarioResult(BaseModel):
    """Validation result for one golden-set scenario."""

    model_config = ConfigDict(extra="forbid")

    scenario_id: str
    dimension: str
    prompt: str
    category: str | None = None
    human_scores: list[int]
    human_consensus_score: int
    judge_score: int | None = None
    judge_justification: str | None = None
    score_difference: int | None = None
    absolute_error: float | None = None
    judge_error: str | None = None


class ValidationReport(BaseModel):
    """Structured output of :class:`JudgeValidator`.

    Attributes:
        cohen_kappa: Overall linearly weighted Cohen's Kappa.
        pearson_correlation: Overall Pearson correlation.
        mae: Overall mean absolute error.
        agreement_label: Human-readable label derived from overall Kappa.
        by_dimension: Per-dimension metric summary.
        high_disagreements: Scenarios where the judge diverged by at least
            two points from the human consensus.
        per_scenario: Full per-scenario breakdown for qualitative analysis.
        total_scenarios: Number of scenarios present in the golden set.
        evaluated_scenarios: Number of scenarios that produced a judge score.
        golden_set_version: Version string from the golden-set file.
        judge_provider: Provider class used by the judge.
        judge_model: Model identifier reported by the provider when available.
    """

    model_config = ConfigDict(extra="forbid")

    cohen_kappa: float
    pearson_correlation: float
    mae: float
    agreement_label: str
    by_dimension: dict[str, ValidationMetricSummary]
    high_disagreements: list[ValidationScenarioResult] = Field(default_factory=list)
    per_scenario: list[ValidationScenarioResult] = Field(default_factory=list)
    total_scenarios: int
    evaluated_scenarios: int
    golden_set_version: str
    judge_provider: str | None = None
    judge_model: str | None = None


class JudgeValidator:
    """Run a judge against a golden set and compute agreement metrics.

    Args:
        judge: Judge implementation that will score the golden set.
        golden_set_path: Optional path to a JSON golden-set file. When omitted,
            the built-in packaged dataset is used.
    """

    def __init__(self, judge: Judge, golden_set_path: str | Path | None = None) -> None:
        """Initialize the validator with a judge and an optional golden set path.

        Args:
            judge: Judge implementation that will score the golden set.
            golden_set_path: Optional path to a JSON golden-set file. When
                ``None``, the built-in packaged dataset is used.
        """
        self.judge = judge
        self.golden_set_path = Path(golden_set_path) if golden_set_path is not None else None

    def run(self) -> ValidationReport:
        """Run the judge on the golden set and compute agreement metrics."""
        golden_set = self._load_golden_set()
        per_scenario: list[ValidationScenarioResult] = []

        for scenario in golden_set.scenarios:
            per_scenario.append(self._evaluate_scenario(scenario))

        overall_summary = _summarize_metrics(per_scenario)
        by_dimension: dict[str, ValidationMetricSummary] = {}
        for dimension in ALLOWED_DIMENSIONS:
            rows = [row for row in per_scenario if row.dimension == dimension]
            if rows:
                by_dimension[dimension] = _summarize_metrics(rows)

        high_disagreements = [
            row
            for row in per_scenario
            if row.absolute_error is not None and row.absolute_error >= HIGH_DISAGREEMENT_THRESHOLD
        ]

        provider = getattr(self.judge, "provider", None)
        provider_config = getattr(provider, "config", None)
        judge_model = getattr(provider_config, "model", None)
        judge_provider = type(provider).__name__ if provider is not None else None

        return ValidationReport(
            cohen_kappa=overall_summary.kappa,
            pearson_correlation=overall_summary.pearson_correlation,
            mae=overall_summary.mae,
            agreement_label=overall_summary.agreement_label,
            by_dimension=by_dimension,
            high_disagreements=high_disagreements,
            per_scenario=per_scenario,
            total_scenarios=len(golden_set.scenarios),
            evaluated_scenarios=overall_summary.evaluated_scenarios,
            golden_set_version=golden_set.version,
            judge_provider=judge_provider,
            judge_model=judge_model,
        )

    def _load_golden_set(self) -> GoldenSet:
        if self.golden_set_path is None:
            try:
                raw = (
                    resources.files(DEFAULT_GOLDEN_SET_PACKAGE)
                    .joinpath(DEFAULT_GOLDEN_SET_FILE)
                    .read_text(encoding="utf-8")
                )
            except (FileNotFoundError, ModuleNotFoundError) as exc:
                raise JudgeValidationError(
                    f"Built-in golden set '{DEFAULT_GOLDEN_SET_FILE}' is missing"
                ) from exc
        else:
            try:
                raw = self.golden_set_path.read_text(encoding="utf-8")
            except FileNotFoundError as exc:
                raise JudgeValidationError(
                    f"Golden set file not found: {self.golden_set_path}"
                ) from exc

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise JudgeValidationError(f"Golden set is not valid JSON: {exc}") from exc

        if not isinstance(payload, dict):
            raise JudgeValidationError(
                f"Golden set must be a JSON object, got {type(payload).__name__}"
            )

        try:
            return GoldenSet.model_validate(payload)
        except Exception as exc:
            raise JudgeValidationError(f"Golden set schema validation failed: {exc}") from exc

    def _evaluate_scenario(self, scenario: GoldenScenario) -> ValidationScenarioResult:
        try:
            judge_result = self._call_judge(scenario)
        except Exception as exc:
            logger.exception("Judge validation failed for scenario %s: %s", scenario.id, exc)
            return ValidationScenarioResult(
                scenario_id=scenario.id,
                dimension=scenario.dimension,
                prompt=scenario.prompt,
                category=scenario.category,
                human_scores=[annotation.score for annotation in scenario.human_scores],
                human_consensus_score=scenario.human_consensus_score,
                judge_error=f"{type(exc).__name__}: {exc}",
            )

        difference = judge_result.score - scenario.human_consensus_score
        return ValidationScenarioResult(
            scenario_id=scenario.id,
            dimension=scenario.dimension,
            prompt=scenario.prompt,
            category=scenario.category,
            human_scores=[annotation.score for annotation in scenario.human_scores],
            human_consensus_score=scenario.human_consensus_score,
            judge_score=judge_result.score,
            judge_justification=judge_result.justification,
            score_difference=difference,
            absolute_error=abs(float(difference)),
        )

    def _call_judge(self, scenario: GoldenScenario) -> JudgeResult:
        if scenario.dimension == "factual":
            return self.judge.evaluate_factual(
                prompt=scenario.prompt,
                ground_truth=scenario.ground_truth or "",
                response=scenario.chatbot_response,
            )
        if scenario.dimension == "consistency":
            return self.judge.evaluate_consistency(
                prompt=scenario.prompt,
                responses=[scenario.chatbot_response, *scenario.comparison_responses],
            )
        if scenario.dimension == "robustness":
            return self.judge.evaluate_robustness(
                prompt=scenario.prompt,
                original_response=scenario.original_response or "",
                variant_type=scenario.variant_type or "unknown",
                variant_prompt=scenario.variant_prompt or scenario.prompt,
                variant_response=scenario.chatbot_response,
            )
        raise JudgeValidationError(f"Unsupported validation dimension: {scenario.dimension}")


def interpret_kappa(kappa: float) -> str:
    """Return a standard qualitative label for a Kappa value."""
    if kappa < 0.0:
        return "poor agreement"
    if kappa < 0.21:
        return "slight agreement"
    if kappa < 0.41:
        return "fair agreement"
    if kappa < 0.61:
        return "moderate agreement"
    if kappa < 0.81:
        return "substantial agreement"
    return "almost perfect agreement"


def _summarize_metrics(results: list[ValidationScenarioResult]) -> ValidationMetricSummary:
    scored = [row for row in results if row.judge_score is not None]
    human_scores = [row.human_consensus_score for row in scored]
    judge_scores = [row.judge_score for row in scored if row.judge_score is not None]

    if scored:
        raw_kappa = _cohen_kappa_linear(human_scores, judge_scores)
        kappa = _round(raw_kappa)
        pearson = _round(_pearson_correlation(human_scores, judge_scores))
        mae = _round(_mean_absolute_error(human_scores, judge_scores))
        label = interpret_kappa(raw_kappa)
    else:
        kappa = 0.0
        pearson = 0.0
        mae = 0.0
        label = interpret_kappa(0.0)

    return ValidationMetricSummary(
        kappa=kappa,
        pearson_correlation=pearson,
        mae=mae,
        agreement_label=label,
        total_scenarios=len(results),
        evaluated_scenarios=len(scored),
    )


def _median_score(scores: Any) -> int:
    """Return the consensus score as an integer median.

    For an even number of annotations, use the lower of the two middle scores
    so the consensus remains an unambiguous member of the 1-5 ordinal scale.
    """
    numeric_scores = sorted(int(score) for score in scores)
    if not numeric_scores:
        raise ValueError("Cannot compute consensus for an empty annotation list")
    return int(statistics.median_low(numeric_scores))


def _cohen_kappa_linear(human_scores: list[int], judge_scores: list[int]) -> float:
    """Compute linearly weighted Cohen's Kappa on the 1-5 ordinal scale.

    The weighting scheme matches the standard linear variant where the
    disagreement between adjacent classes counts less than disagreement across
    the whole scale. Degenerate cases with zero expected disagreement return
    ``0.0`` instead of ``nan`` so callers can report a stable numeric result.
    """

    if len(human_scores) != len(judge_scores):
        raise ValueError("human_scores and judge_scores must have the same length")
    if not human_scores:
        return 0.0

    categories = list(range(1, 6))
    size = len(categories)
    total = len(human_scores)

    observed = [[0.0 for _ in categories] for _ in categories]
    for human, judge in zip(human_scores, judge_scores):
        observed[human - 1][judge - 1] += 1.0

    observed = [[cell / total for cell in row] for row in observed]
    human_distribution = [sum(row) for row in observed]
    judge_distribution = [
        sum(observed[row_idx][col_idx] for row_idx in range(size)) for col_idx in range(size)
    ]

    expected = [
        [human_distribution[i] * judge_distribution[j] for j in range(size)] for i in range(size)
    ]
    if size == 1:
        return 0.0

    weights = [[abs(i - j) / (size - 1) for j in range(size)] for i in range(size)]
    observed_disagreement = sum(
        weights[i][j] * observed[i][j] for i in range(size) for j in range(size)
    )
    expected_disagreement = sum(
        weights[i][j] * expected[i][j] for i in range(size) for j in range(size)
    )

    if expected_disagreement == 0.0:
        return 0.0
    return 1.0 - (observed_disagreement / expected_disagreement)


def _pearson_correlation(human_scores: list[int], judge_scores: list[int]) -> float:
    """Return Pearson's r, falling back to 0.0 on degenerate inputs."""
    if len(human_scores) != len(judge_scores):
        raise ValueError("human_scores and judge_scores must have the same length")
    if len(human_scores) < 2:
        return 0.0

    human_mean = statistics.mean(human_scores)
    judge_mean = statistics.mean(judge_scores)
    human_centered = [score - human_mean for score in human_scores]
    judge_centered = [score - judge_mean for score in judge_scores]

    human_norm = math.sqrt(sum(value * value for value in human_centered))
    judge_norm = math.sqrt(sum(value * value for value in judge_centered))
    if human_norm == 0.0 or judge_norm == 0.0:
        return 0.0

    covariance = sum(a * b for a, b in zip(human_centered, judge_centered))
    return covariance / (human_norm * judge_norm)


def _mean_absolute_error(human_scores: list[int], judge_scores: list[int]) -> float:
    """Return the mean absolute error between consensus and judge scores."""
    if len(human_scores) != len(judge_scores):
        raise ValueError("human_scores and judge_scores must have the same length")
    if not human_scores:
        return 0.0
    return sum(abs(human - judge) for human, judge in zip(human_scores, judge_scores)) / len(
        human_scores
    )


def _round(value: float, ndigits: int = 4) -> float:
    return round(float(value), ndigits)
