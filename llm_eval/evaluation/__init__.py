"""Evaluation modules: LLM-as-a-Judge, metrics, and judge validation."""

from llm_eval.evaluation.judge import Judge, JudgeResult
from llm_eval.evaluation.metrics import (
    MetricResult,
    calculate_bertscore,
    calculate_bertscore_batch,
    calculate_consistency,
    calculate_response_variance,
)
from llm_eval.evaluation.validation import (
    JudgeValidationError,
    JudgeValidator,
    ValidationMetricSummary,
    ValidationReport,
    ValidationScenarioResult,
    interpret_kappa,
)

__all__ = [
    "Judge",
    "JudgeResult",
    "JudgeValidationError",
    "JudgeValidator",
    "MetricResult",
    "ValidationMetricSummary",
    "ValidationReport",
    "ValidationScenarioResult",
    "calculate_bertscore",
    "calculate_bertscore_batch",
    "calculate_consistency",
    "calculate_response_variance",
    "interpret_kappa",
]
