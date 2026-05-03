"""Módulos de avaliação: LLM-as-a-Judge e métricas computacionais."""

from llm_eval.evaluation.metrics import (
    MetricResult,
    calculate_bertscore,
    calculate_bertscore_batch,
    calculate_consistency,
    calculate_response_variance,
)

__all__ = [
    "MetricResult",
    "calculate_bertscore",
    "calculate_bertscore_batch",
    "calculate_consistency",
    "calculate_response_variance",
]
