"""Métricas computacionais para avaliação de respostas dos chatbots.

Este módulo complementa o LLM-as-a-Judge com medidas quantitativas:

- :func:`calculate_bertscore` — similaridade semântica por embeddings BERT
  (ZHANG et al., 2020), métrica principal para comparar resposta candidata
  contra ``ground_truth`` ou contra outras respostas equivalentes.
- :func:`calculate_consistency` — média e desvio padrão de BERTScore par-a-par
  entre respostas de paráfrases (dimensão de consistência semântica).
- :func:`calculate_response_variance` — variabilidade textual via Jaccard de
  tokens e estatísticas de comprimento, sem custo computacional de embeddings.

A linguagem default é ``"pt"`` por consistência com o domínio do estudo
(chatbots avaliados em português brasileiro).
"""

from __future__ import annotations

import statistics
from itertools import combinations
from typing import TYPE_CHECKING, Any, Protocol

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    pass


class _BertScoreFn(Protocol):
    """Type-shape of the ``bert_score.score`` callable used by this module."""

    def __call__(
        self,
        cands: list[str],
        refs: list[str],
        lang: str,
        verbose: bool = ...,
        **kwargs: Any,
    ) -> tuple[Any, Any, Any]: ...


def _default_bert_score() -> _BertScoreFn:
    """Lazily import ``bert_score.score`` so tests can mock it without the import cost."""
    from bert_score import score as bert_score_fn

    return bert_score_fn  # type: ignore[no-any-return]


class MetricResult(BaseModel):
    """Standardized metric output.

    Attributes:
        metric_name: Identifier of the metric (e.g. ``"bertscore"``).
        value: Primary scalar value summarizing the metric.
        details: Auxiliary breakdown (per-pair scores, components, etc.).
    """

    model_config = ConfigDict(extra="forbid")

    metric_name: str
    value: float
    details: dict[str, Any] = Field(default_factory=dict)


def _round(value: float, ndigits: int = 4) -> float:
    return round(float(value), ndigits)


def calculate_bertscore(
    reference: str,
    candidate: str,
    lang: str = "pt",
    *,
    bert_score_fn: _BertScoreFn | None = None,
) -> MetricResult:
    """Compute BERTScore between a single reference and a single candidate.

    Args:
        reference: Reference text (typically the ground truth).
        candidate: Candidate text (typically the chatbot response).
        lang: Language code passed to BERTScore. Defaults to ``"pt"``.
        bert_score_fn: Optional override for the underlying BERTScore callable.
            When ``None`` (default) the real ``bert_score.score`` is used.
            Tests can inject a stub to avoid downloading model weights.

    Returns:
        MetricResult: ``metric_name="bertscore"`` with ``value`` set to the F1
        score and ``details`` containing precision/recall/F1 (4 decimals).
    """
    fn = bert_score_fn or _default_bert_score()
    p, r, f1 = fn(cands=[candidate], refs=[reference], lang=lang, verbose=False)
    p_val = _round(p[0].item() if hasattr(p, "__getitem__") else p.item())
    r_val = _round(r[0].item() if hasattr(r, "__getitem__") else r.item())
    f1_val = _round(f1[0].item() if hasattr(f1, "__getitem__") else f1.item())

    return MetricResult(
        metric_name="bertscore",
        value=f1_val,
        details={
            "precision": p_val,
            "recall": r_val,
            "f1": f1_val,
            "lang": lang,
        },
    )


def calculate_bertscore_batch(
    references: list[str],
    candidates: list[str],
    lang: str = "pt",
    *,
    bert_score_fn: _BertScoreFn | None = None,
) -> list[MetricResult]:
    """Compute BERTScore for several reference/candidate pairs in a single call.

    Batching is significantly faster than repeated single-pair calls because
    the BERT model is only loaded and forwarded once.

    Args:
        references: Reference texts. Must be the same length as ``candidates``.
        candidates: Candidate texts.
        lang: Language code passed to BERTScore.
        bert_score_fn: Optional override for the underlying BERTScore callable.

    Returns:
        list[MetricResult]: One result per pair, in the same order as the input.

    Raises:
        ValueError: If the input lists have different lengths or are empty.
    """
    if len(references) != len(candidates):
        raise ValueError(
            f"references and candidates must have the same length, "
            f"got {len(references)} and {len(candidates)}"
        )
    if not references:
        raise ValueError("references and candidates must not be empty")

    fn = bert_score_fn or _default_bert_score()
    p, r, f1 = fn(cands=candidates, refs=references, lang=lang, verbose=False)

    results: list[MetricResult] = []
    for i in range(len(references)):
        p_val = _round(p[i].item())
        r_val = _round(r[i].item())
        f1_val = _round(f1[i].item())
        results.append(
            MetricResult(
                metric_name="bertscore",
                value=f1_val,
                details={
                    "precision": p_val,
                    "recall": r_val,
                    "f1": f1_val,
                    "lang": lang,
                },
            )
        )
    return results


def calculate_consistency(
    responses: list[str],
    lang: str = "pt",
    *,
    bert_score_fn: _BertScoreFn | None = None,
) -> MetricResult:
    """Pairwise semantic consistency across multiple responses.

    Computes BERTScore F1 for every unordered pair of responses, then returns
    the mean across pairs as the primary value, with the standard deviation
    and the individual pair scores in ``details``.

    Edge cases:
        - 0 or 1 response → returns ``value=1.0`` with a note in ``details``;
          there is nothing to compare against.

    Args:
        responses: Responses to the same (or paraphrased) prompt.
        lang: Language code passed to BERTScore.
        bert_score_fn: Optional override for the underlying BERTScore callable.

    Returns:
        MetricResult: ``metric_name="consistency"`` with ``value`` = mean F1.
    """
    if len(responses) < 2:
        return MetricResult(
            metric_name="consistency",
            value=1.0,
            details={
                "note": "Less than 2 responses; nothing to compare",
                "num_responses": len(responses),
                "num_pairs": 0,
            },
        )

    pairs = list(combinations(responses, 2))
    refs = [a for a, _ in pairs]
    cands = [b for _, b in pairs]

    pair_results = calculate_bertscore_batch(refs, cands, lang=lang, bert_score_fn=bert_score_fn)
    scores = [result.value for result in pair_results]

    mean = _round(statistics.mean(scores))
    stdev = _round(statistics.stdev(scores)) if len(scores) > 1 else 0.0

    return MetricResult(
        metric_name="consistency",
        value=mean,
        details={
            "mean_f1": mean,
            "stdev_f1": stdev,
            "num_pairs": len(pairs),
            "num_responses": len(responses),
            "pair_scores": [_round(s) for s in scores],
            "lang": lang,
        },
    )


def calculate_response_variance(responses: list[str]) -> MetricResult:
    """Lexical variability across responses, no embeddings required.

    Uses Jaccard similarity over whitespace-tokenized lowercase tokens to
    quantify lexical overlap, plus mean/stdev of response length in tokens.
    This is a cheap proxy useful when BERTScore is too expensive to run on
    every batch.

    The reported ``value`` is ``1 - mean(Jaccard)``: ``0.0`` means responses
    are textually identical, ``1.0`` means they share no tokens.

    Args:
        responses: Texts to compare.

    Returns:
        MetricResult: ``metric_name="response_variance"`` with the variance
        score and supporting details.
    """
    if not responses:
        return MetricResult(
            metric_name="response_variance",
            value=0.0,
            details={"note": "no responses", "num_responses": 0},
        )

    lengths = [len(r.split()) for r in responses]
    length_mean = _round(statistics.mean(lengths), 2)
    length_stdev = _round(statistics.stdev(lengths), 2) if len(lengths) > 1 else 0.0

    pairs = list(combinations(responses, 2))
    jaccard_scores = [_jaccard_tokens(a, b) for a, b in pairs]

    if jaccard_scores:
        jaccard_mean = _round(statistics.mean(jaccard_scores))
        variance_value = _round(1.0 - jaccard_mean)
    else:
        jaccard_mean = 1.0
        variance_value = 0.0

    return MetricResult(
        metric_name="response_variance",
        value=variance_value,
        details={
            "length_mean": length_mean,
            "length_stdev": length_stdev,
            "jaccard_mean": jaccard_mean,
            "num_responses": len(responses),
            "num_pairs": len(pairs),
        },
    )


def _jaccard_tokens(a: str, b: str) -> float:
    """Jaccard similarity over whitespace-tokenized lowercase tokens.

    Returns ``1.0`` when both texts produce empty token sets, treating the
    empty/empty case as fully consistent rather than undefined.
    """
    set_a = set(a.lower().split())
    set_b = set(b.lower().split())
    if not set_a and not set_b:
        return 1.0
    union = set_a | set_b
    if not union:
        return 1.0
    return len(set_a & set_b) / len(union)
