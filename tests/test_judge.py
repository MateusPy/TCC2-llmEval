"""Testes para evaluation/judge.py."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from llm_eval.evaluation.judge import (
    CONSISTENCY_PROMPT,
    FACTUAL_PROMPT,
    ROBUSTNESS_PROMPT,
    Judge,
    JudgeResult,
    _clamp_score,
    _find_first_json_object,
    _strip_code_fences,
)
from llm_eval.providers.base import BaseProvider, ProviderConfig, ProviderResponse


# ---------------------------------------------------------------------------
# Stub provider
# ---------------------------------------------------------------------------


class _StubProvider(BaseProvider):
    """Provider that returns a configurable canned response.

    Tracks the last prompt sent so tests can assert template formatting.
    """

    def __init__(
        self,
        response_text: str,
        model: str = "stub-model",
        response_time_ms: float = 12.5,
    ) -> None:
        super().__init__(ProviderConfig(api_key="x", model=model))
        self._response_text = response_text
        self._response_time_ms = response_time_ms
        self.last_prompt: str | None = None
        self.call_count = 0

    def send(self, prompt: str) -> ProviderResponse:
        self.last_prompt = prompt
        self.call_count += 1
        return ProviderResponse(
            response_text=self._response_text,
            model=self.config.model,
            timestamp=datetime.now(timezone.utc),
            response_time_ms=self._response_time_ms,
            parameters={"temperature": self.config.temperature},
        )


def _good_json(score: int = 5, justification: str = "ok") -> str:
    return f'{{"score": {score}, "justification": "{justification}"}}'


# ---------------------------------------------------------------------------
# JudgeResult
# ---------------------------------------------------------------------------


def test_judge_result_minimal_valid():
    r = JudgeResult(dimension="factual", score=4, justification="ok")
    assert r.dimension == "factual"
    assert r.score == 4
    assert r.metadata == {}


def test_judge_result_invalid_dimension():
    with pytest.raises(ValidationError, match="Invalid dimension"):
        JudgeResult(dimension="invalid", score=3, justification="x")


def test_judge_result_score_below_range():
    with pytest.raises(ValidationError):
        JudgeResult(dimension="factual", score=0, justification="x")


def test_judge_result_score_above_range():
    with pytest.raises(ValidationError):
        JudgeResult(dimension="factual", score=6, justification="x")


def test_judge_result_rejects_extra_fields():
    with pytest.raises(ValidationError):
        JudgeResult(
            dimension="factual",
            score=3,
            justification="x",
            unknown="oops",  # type: ignore[call-arg]
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw,expected",
    [
        (3, 3),
        (1, 1),
        (5, 5),
        (0, 1),
        (-2, 1),
        (6, 5),
        (100, 5),
        ("4", 4),
        ("not a number", 3),
        (None, 3),
        (3.7, 3),
    ],
)
def test_clamp_score(raw: object, expected: int) -> None:
    assert _clamp_score(raw) == expected


def test_strip_code_fences_with_language():
    assert _strip_code_fences('```json\n{"a": 1}\n```') == '{"a": 1}'


def test_strip_code_fences_without_language():
    assert _strip_code_fences('```\n{"a": 1}\n```') == '{"a": 1}'


def test_strip_code_fences_no_fences():
    assert _strip_code_fences('{"a": 1}') == '{"a": 1}'


def test_strip_code_fences_extra_whitespace():
    assert _strip_code_fences('  ```json\n{"a":1}\n```  ') == '{"a":1}'


def test_find_first_json_object_simple():
    assert _find_first_json_object('text {"a": 1} more') == '{"a": 1}'


def test_find_first_json_object_nested():
    assert _find_first_json_object('x {"a": {"b": 1}} y') == '{"a": {"b": 1}}'


def test_find_first_json_object_with_string_containing_brace():
    assert _find_first_json_object('{"a": "} not closing"}') == '{"a": "} not closing"}'


def test_find_first_json_object_with_escaped_quote():
    assert _find_first_json_object(r'{"a": "she said \"hi\""}') == r'{"a": "she said \"hi\""}'


def test_find_first_json_object_missing_returns_none():
    assert _find_first_json_object("no braces here") is None


def test_find_first_json_object_unclosed_returns_none():
    assert _find_first_json_object('{"a": 1') is None


# ---------------------------------------------------------------------------
# Judge.evaluate_factual
# ---------------------------------------------------------------------------


def test_evaluate_factual_happy_path():
    provider = _StubProvider(_good_json(score=5, justification="correta"))
    judge = Judge(provider)
    result = judge.evaluate_factual(
        prompt="Qual é a capital do Brasil?",
        ground_truth="Brasília",
        response="A capital é Brasília.",
    )
    assert result.dimension == "factual"
    assert result.score == 5
    assert result.justification == "correta"
    assert result.metadata["parse_method"] == "json"
    assert result.metadata["judge_model"] == "stub-model"
    assert result.metadata["response_time_ms"] == 12.5


def test_evaluate_factual_formats_template():
    provider = _StubProvider(_good_json())
    judge = Judge(provider)
    judge.evaluate_factual(prompt="P?", ground_truth="GT", response="R")
    assert provider.last_prompt is not None
    assert "P?" in provider.last_prompt
    assert "GT" in provider.last_prompt
    assert "R" in provider.last_prompt
    assert provider.last_prompt.startswith(FACTUAL_PROMPT.split("{", 1)[0])


def test_evaluate_factual_clamps_score_above_5():
    provider = _StubProvider(_good_json(score=9, justification="excessive"))
    judge = Judge(provider)
    result = judge.evaluate_factual(prompt="p", ground_truth="gt", response="r")
    assert result.score == 5


def test_evaluate_factual_clamps_score_below_1():
    provider = _StubProvider('{"score": 0, "justification": "too low"}')
    judge = Judge(provider)
    result = judge.evaluate_factual(prompt="p", ground_truth="gt", response="r")
    assert result.score == 1


# ---------------------------------------------------------------------------
# Judge.evaluate_consistency
# ---------------------------------------------------------------------------


def test_evaluate_consistency_happy_path():
    provider = _StubProvider(_good_json(score=4, justification="alinhadas"))
    judge = Judge(provider)
    result = judge.evaluate_consistency(
        prompt="P?",
        responses=["resp 1", "resp 2", "resp 3"],
    )
    assert result.dimension == "consistency"
    assert result.score == 4
    assert provider.last_prompt is not None
    assert "Resposta 1: resp 1" in provider.last_prompt
    assert "Resposta 3: resp 3" in provider.last_prompt
    assert provider.last_prompt.startswith(CONSISTENCY_PROMPT.split("{", 1)[0])


def test_evaluate_consistency_with_two_responses():
    provider = _StubProvider(_good_json())
    judge = Judge(provider)
    result = judge.evaluate_consistency(prompt="P?", responses=["a", "b"])
    assert result.dimension == "consistency"
    assert provider.last_prompt is not None
    assert "Resposta 1: a" in provider.last_prompt
    assert "Resposta 2: b" in provider.last_prompt


# ---------------------------------------------------------------------------
# Judge.evaluate_robustness
# ---------------------------------------------------------------------------


def test_evaluate_robustness_happy_path():
    provider = _StubProvider(_good_json(score=3, justification="parcialmente"))
    judge = Judge(provider)
    result = judge.evaluate_robustness(
        prompt="Qual é a capital do Brasil?",
        original_response="Brasília",
        variant_type="typo",
        variant_prompt="Qaul é a capital do Brasl?",
        variant_response="Brasília",
    )
    assert result.dimension == "robustness"
    assert result.score == 3
    assert provider.last_prompt is not None
    assert "typo" in provider.last_prompt
    assert "Qaul é a capital do Brasl?" in provider.last_prompt
    assert provider.last_prompt.startswith(ROBUSTNESS_PROMPT.split("{", 1)[0])


# ---------------------------------------------------------------------------
# Judge._parse_response — parse strategies
# ---------------------------------------------------------------------------


def test_parse_response_json_with_markdown_fence():
    provider = _StubProvider('```json\n{"score": 4, "justification": "ok"}\n```')
    judge = Judge(provider)
    result = judge.evaluate_factual(prompt="p", ground_truth="gt", response="r")
    assert result.score == 4
    assert result.metadata["parse_method"] == "json"
    assert "raw_response" not in result.metadata


def test_parse_response_json_with_unlabeled_fence():
    provider = _StubProvider('```\n{"score": 5, "justification": "perfeita"}\n```')
    judge = Judge(provider)
    result = judge.evaluate_factual(prompt="p", ground_truth="gt", response="r")
    assert result.score == 5


def test_parse_response_json_embedded_in_prose():
    provider = _StubProvider(
        'Após análise, minha avaliação é: {"score": 2, "justification": "incompleta"}.'
    )
    judge = Judge(provider)
    result = judge.evaluate_factual(prompt="p", ground_truth="gt", response="r")
    assert result.score == 2
    assert result.justification == "incompleta"
    assert result.metadata["parse_method"] == "json_embedded"
    assert "raw_response" in result.metadata


def test_parse_response_regex_fallback(caplog: pytest.LogCaptureFixture):
    provider = _StubProvider('score: 3 com justification: "alguma justificativa aqui"')
    judge = Judge(provider)
    with caplog.at_level(logging.WARNING):
        result = judge.evaluate_factual(prompt="p", ground_truth="gt", response="r")
    assert result.score == 3
    assert result.justification == "alguma justificativa aqui"
    assert result.metadata["parse_method"] == "regex"
    assert any("regex fallback" in rec.message for rec in caplog.records)


def test_parse_response_default_fallback_when_unparseable(
    caplog: pytest.LogCaptureFixture,
):
    provider = _StubProvider("totalmente fora do formato esperado")
    judge = Judge(provider)
    with caplog.at_level(logging.WARNING):
        result = judge.evaluate_factual(prompt="p", ground_truth="gt", response="r")
    assert result.score == 3
    assert "Não foi possível parsear" in result.justification
    assert result.metadata["parse_method"] == "default"
    assert any("could not be parsed" in rec.message for rec in caplog.records)


def test_parse_response_default_fallback_when_json_missing_score():
    provider = _StubProvider('{"justification": "sem score aqui"}')
    judge = Judge(provider)
    result = judge.evaluate_factual(prompt="p", ground_truth="gt", response="r")
    assert result.score == 3
    assert result.metadata["parse_method"] == "default"


def test_parse_response_handles_non_dict_json():
    provider = _StubProvider("[1, 2, 3]")
    judge = Judge(provider)
    result = judge.evaluate_factual(prompt="p", ground_truth="gt", response="r")
    assert result.metadata["parse_method"] == "default"


def test_parse_response_embedded_json_with_decode_error_falls_through():
    """A balanced {...} substring that fails json.loads must not crash; the parser
    falls through to the regex strategy on the surrounding text."""
    # Balanced braces but trailing comma + missing value → JSONDecodeError on the
    # embedded path. The fields inside the broken JSON do not name `score`/
    # `justification`, so the regex must extract them from the surrounding prose.
    provider = _StubProvider('header {"foo": 1,} actual data: score: 2 justification: "via regex"')
    judge = Judge(provider)
    result = judge.evaluate_factual(prompt="p", ground_truth="gt", response="r")
    assert result.metadata["parse_method"] == "regex"
    assert result.score == 2
    assert result.justification == "via regex"


# ---------------------------------------------------------------------------
# Empty/missing justification handling
# ---------------------------------------------------------------------------


def test_parse_response_json_with_missing_justification_uses_fallback():
    provider = _StubProvider('{"score": 4}')
    judge = Judge(provider)
    result = judge.evaluate_factual(prompt="p", ground_truth="gt", response="r")
    assert result.score == 4
    assert result.justification == "Não foi possível parsear a resposta do juiz."
    assert result.metadata["parse_method"] == "json"
    assert result.metadata["justification_fallback"] is True


def test_parse_response_json_with_empty_justification_uses_fallback():
    provider = _StubProvider('{"score": 2, "justification": ""}')
    judge = Judge(provider)
    result = judge.evaluate_factual(prompt="p", ground_truth="gt", response="r")
    assert result.score == 2
    assert result.justification == "Não foi possível parsear a resposta do juiz."
    assert result.metadata["justification_fallback"] is True


def test_parse_response_json_with_whitespace_justification_uses_fallback():
    provider = _StubProvider('{"score": 5, "justification": "   "}')
    judge = Judge(provider)
    result = judge.evaluate_factual(prompt="p", ground_truth="gt", response="r")
    assert result.score == 5
    assert result.metadata["justification_fallback"] is True


def test_parse_response_embedded_json_with_missing_justification_uses_fallback():
    provider = _StubProvider('Após análise: {"score": 3} foi minha avaliação.')
    judge = Judge(provider)
    result = judge.evaluate_factual(prompt="p", ground_truth="gt", response="r")
    assert result.score == 3
    assert result.metadata["parse_method"] == "json_embedded"
    assert result.metadata["justification_fallback"] is True


def test_parse_response_no_justification_fallback_flag_when_present():
    """metadata['justification_fallback'] should not appear when the judge gave a real one."""
    provider = _StubProvider('{"score": 4, "justification": "boa resposta"}')
    judge = Judge(provider)
    result = judge.evaluate_factual(prompt="p", ground_truth="gt", response="r")
    assert "justification_fallback" not in result.metadata


# ---------------------------------------------------------------------------
# Regex fallback — negative scores must clamp, not drop to default
# ---------------------------------------------------------------------------


def test_regex_fallback_clamps_negative_score():
    provider = _StubProvider('score: -1 com justification: "score absurdo"')
    judge = Judge(provider)
    result = judge.evaluate_factual(prompt="p", ground_truth="gt", response="r")
    assert result.score == 1
    assert result.metadata["parse_method"] == "regex"
    assert result.justification == "score absurdo"


def test_regex_fallback_clamps_huge_negative_score():
    provider = _StubProvider("score: -999")
    judge = Judge(provider)
    result = judge.evaluate_factual(prompt="p", ground_truth="gt", response="r")
    assert result.score == 1
    assert result.metadata["parse_method"] == "regex"


def test_regex_fallback_with_negative_no_justification_uses_fallback():
    provider = _StubProvider("score: -3, sem mais nada")
    judge = Judge(provider)
    result = judge.evaluate_factual(prompt="p", ground_truth="gt", response="r")
    assert result.score == 1
    assert result.metadata["parse_method"] == "regex"
    assert result.metadata["justification_fallback"] is True
