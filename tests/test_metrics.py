"""Testes para evaluation/metrics.py.

BERTScore real depende do download de pesos (~270MB+) e roda em CPU/GPU,
o que não é viável dentro do CI. Por isso, todos os testes que envolvem
BERTScore injetam um stub via parâmetro ``bert_score_fn``, replicando a
forma de retorno do pacote ``bert_score`` (tuplas de tensores tipo torch
com ``.item()``).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest
from pydantic import ValidationError

from llm_eval.evaluation.metrics import (
    MetricResult,
    calculate_bertscore,
    calculate_bertscore_batch,
    calculate_consistency,
    calculate_response_variance,
)


# ---------------------------------------------------------------------------
# BERTScore stubs
# ---------------------------------------------------------------------------


class _FakeTensorScalar:
    """Mimics a 0-d torch tensor with an ``.item()`` method."""

    def __init__(self, value: float) -> None:
        self._value = value

    def item(self) -> float:
        return self._value


class _FakeTensor1D:
    """Mimics a 1-d torch tensor — supports indexing and ``.item()`` per element."""

    def __init__(self, values: list[float]) -> None:
        self._values = values

    def __getitem__(self, idx: int) -> _FakeTensorScalar:
        return _FakeTensorScalar(self._values[idx])

    def item(self) -> float:
        if len(self._values) != 1:
            raise ValueError("item() requires a single-element tensor")
        return self._values[0]


def _fake_bert_score(
    p_values: list[float],
    r_values: list[float],
    f1_values: list[float],
) -> Callable[..., tuple[Any, Any, Any]]:
    def _stub(
        cands: list[str],
        refs: list[str],
        lang: str,
        verbose: bool = False,
        **_: Any,
    ) -> tuple[Any, Any, Any]:
        assert len(cands) == len(refs) == len(p_values), (
            "stub configured for a different batch size"
        )
        return (
            _FakeTensor1D(p_values),
            _FakeTensor1D(r_values),
            _FakeTensor1D(f1_values),
        )

    return _stub


# ---------------------------------------------------------------------------
# MetricResult
# ---------------------------------------------------------------------------


def test_metric_result_minimal():
    result = MetricResult(metric_name="x", value=0.5)
    assert result.metric_name == "x"
    assert result.value == 0.5
    assert result.details == {}


def test_metric_result_rejects_extra_fields():
    with pytest.raises(ValidationError):
        MetricResult(metric_name="x", value=0.5, unknown="oops")  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# calculate_bertscore
# ---------------------------------------------------------------------------


def test_calculate_bertscore_returns_f1_as_value():
    fn = _fake_bert_score([0.92], [0.88], [0.90])
    result = calculate_bertscore("ref", "cand", bert_score_fn=fn)
    assert result.metric_name == "bertscore"
    assert result.value == 0.9
    assert result.details["precision"] == 0.92
    assert result.details["recall"] == 0.88
    assert result.details["f1"] == 0.9
    assert result.details["lang"] == "pt"


def test_calculate_bertscore_custom_language():
    fn = _fake_bert_score([0.5], [0.5], [0.5])
    result = calculate_bertscore("ref", "cand", lang="en", bert_score_fn=fn)
    assert result.details["lang"] == "en"


def test_calculate_bertscore_rounds_to_4_decimals():
    fn = _fake_bert_score([0.123456], [0.654321], [0.5])
    result = calculate_bertscore("ref", "cand", bert_score_fn=fn)
    assert result.details["precision"] == 0.1235
    assert result.details["recall"] == 0.6543


# ---------------------------------------------------------------------------
# calculate_bertscore_batch
# ---------------------------------------------------------------------------


def test_calculate_bertscore_batch_returns_one_result_per_pair():
    fn = _fake_bert_score([0.9, 0.6, 0.3], [0.85, 0.55, 0.25], [0.87, 0.57, 0.27])
    results = calculate_bertscore_batch(
        references=["a", "b", "c"],
        candidates=["a2", "b2", "c2"],
        bert_score_fn=fn,
    )
    assert len(results) == 3
    assert [r.value for r in results] == [0.87, 0.57, 0.27]
    assert results[0].details["precision"] == 0.9
    assert results[2].details["recall"] == 0.25


def test_calculate_bertscore_batch_length_mismatch():
    with pytest.raises(ValueError, match="same length"):
        calculate_bertscore_batch(references=["a"], candidates=["a", "b"])


def test_calculate_bertscore_batch_empty():
    with pytest.raises(ValueError, match="must not be empty"):
        calculate_bertscore_batch(references=[], candidates=[])


# ---------------------------------------------------------------------------
# calculate_consistency
# ---------------------------------------------------------------------------


def test_calculate_consistency_single_response_returns_one():
    result = calculate_consistency(["only one"])
    assert result.metric_name == "consistency"
    assert result.value == 1.0
    assert result.details["num_pairs"] == 0
    assert result.details["num_responses"] == 1


def test_calculate_consistency_empty_returns_one():
    result = calculate_consistency([])
    assert result.value == 1.0
    assert result.details["num_responses"] == 0


def test_calculate_consistency_two_identical_responses_high_score():
    fn = _fake_bert_score([1.0], [1.0], [1.0])
    result = calculate_consistency(["mesma resposta", "mesma resposta"], bert_score_fn=fn)
    assert result.value == 1.0
    assert result.details["num_pairs"] == 1
    assert result.details["stdev_f1"] == 0.0


def test_calculate_consistency_three_responses_computes_three_pairs():
    fn = _fake_bert_score([0.9, 0.8, 0.7], [0.9, 0.8, 0.7], [0.9, 0.8, 0.7])
    result = calculate_consistency(["a", "b", "c"], bert_score_fn=fn)
    assert result.details["num_pairs"] == 3
    assert result.details["num_responses"] == 3
    assert result.details["pair_scores"] == [0.9, 0.8, 0.7]
    assert result.value == 0.8
    assert result.details["stdev_f1"] == pytest.approx(0.1, abs=0.0001)


def test_calculate_consistency_propagates_lang():
    fn = _fake_bert_score([1.0], [1.0], [0.95])
    result = calculate_consistency(["x", "y"], lang="en", bert_score_fn=fn)
    assert result.details["lang"] == "en"


# ---------------------------------------------------------------------------
# calculate_response_variance
# ---------------------------------------------------------------------------


def test_calculate_response_variance_identical_responses():
    result = calculate_response_variance(["abc def", "abc def", "abc def"])
    assert result.metric_name == "response_variance"
    assert result.value == 0.0
    assert result.details["jaccard_mean"] == 1.0
    assert result.details["num_pairs"] == 3


def test_calculate_response_variance_disjoint_responses():
    result = calculate_response_variance(["foo bar", "baz qux"])
    assert result.value == 1.0
    assert result.details["jaccard_mean"] == 0.0


def test_calculate_response_variance_partial_overlap():
    result = calculate_response_variance(["foo bar baz", "foo bar qux"])
    assert result.details["jaccard_mean"] == pytest.approx(0.5, abs=0.0001)
    assert result.value == pytest.approx(0.5, abs=0.0001)


def test_calculate_response_variance_case_insensitive():
    result = calculate_response_variance(["Foo BAR", "foo bar"])
    assert result.details["jaccard_mean"] == 1.0


def test_calculate_response_variance_single_response():
    result = calculate_response_variance(["hello"])
    assert result.details["num_pairs"] == 0
    assert result.details["length_mean"] == 1.0
    assert result.details["length_stdev"] == 0.0
    assert result.value == 0.0


def test_calculate_response_variance_empty():
    result = calculate_response_variance([])
    assert result.value == 0.0
    assert result.details["num_responses"] == 0


def test_calculate_response_variance_length_stats():
    result = calculate_response_variance(["a b c", "a b", "a b c d e"])
    assert result.details["length_mean"] == pytest.approx(3.33, abs=0.01)
    assert result.details["length_stdev"] > 0


def test_calculate_response_variance_handles_all_empty_strings():
    result = calculate_response_variance(["", "", ""])
    assert result.details["jaccard_mean"] == 1.0
    assert result.value == 0.0
