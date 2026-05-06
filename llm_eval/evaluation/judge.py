"""LLM-as-a-Judge: avaliação automatizada das respostas do chatbot por um LLM auxiliar.

Para cada dimensão de confiabilidade (factual, consistency, robustness) há um
prompt template específico que orienta o juiz a produzir um score inteiro de
1 a 5 acompanhado de uma justificativa em texto livre. O juiz deve responder
em JSON estruturado; o parser deste módulo tolera formatações comuns
(``json``/``json5`` em code fences, JSON embutido em texto livre) e degrada
para um valor neutro com aviso quando nada pode ser extraído.

Esta abordagem complementa as métricas computacionais do módulo
:mod:`llm_eval.evaluation.metrics`, fornecendo uma avaliação qualitativa que
captura nuances que BERTScore não enxerga (ex: factualidade, contradições
sutis, robustez frente a ruído).
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from llm_eval.providers.base import BaseProvider

logger = logging.getLogger(__name__)

ALLOWED_DIMENSIONS = ("factual", "consistency", "robustness")
DEFAULT_FALLBACK_SCORE = 3
DEFAULT_FALLBACK_JUSTIFICATION = "Não foi possível parsear a resposta do juiz."

FACTUAL_PROMPT = """Você é um avaliador especializado em verificar a precisão factual de respostas.

Pergunta feita ao chatbot:
{prompt}

Resposta esperada (ground truth):
{ground_truth}

Resposta do chatbot:
{response}

Avalie a resposta do chatbot comparando com o ground truth. Considere:
- A resposta contém a informação correta?
- Há informações inventadas ou incorretas?
- A resposta é completa o suficiente?

Responda APENAS com um JSON válido no seguinte formato:
{{"score": <1-5>, "justification": "<explicação>"}}

Escala:
1 = Completamente incorreta ou inventada
2 = Parcialmente incorreta, com erros significativos
3 = Parcialmente correta, mas com omissões ou imprecisões
4 = Correta, com pequenas imprecisões que não comprometem o conteúdo
5 = Completamente correta e alinhada com o ground truth"""


CONSISTENCY_PROMPT = """Você é um avaliador especializado em verificar a consistência semântica de respostas.

Pergunta original:
{prompt}

Respostas do chatbot a reformulações dessa mesma pergunta:
{responses}

Avalie se as respostas são semanticamente consistentes entre si. Considere:
- As respostas transmitem a mesma informação central?
- Há contradições entre elas?
- Variações de forma são aceitáveis, contradições de conteúdo não.

Responda APENAS com um JSON válido no seguinte formato:
{{"score": <1-5>, "justification": "<explicação>"}}

Escala:
1 = Respostas completamente contraditórias
2 = Contradições significativas no conteúdo
3 = Parcialmente consistentes, com divergências relevantes
4 = Consistentes, com variações menores de forma
5 = Totalmente consistentes em conteúdo e sentido"""


ROBUSTNESS_PROMPT = """Você é um avaliador especializado em verificar a robustez de chatbots.

Pergunta original:
{prompt}

Resposta do chatbot à pergunta original:
{original_response}

Variação aplicada ({variant_type}):
{variant_prompt}

Resposta do chatbot à variação:
{variant_response}

Avalie se o chatbot manteve a qualidade da resposta apesar da variação no input. Considere:
- A resposta à variação mantém a mesma informação correta?
- O chatbot foi confundido pelo ruído/adversarialidade?
- A resposta degradou significativamente?

Responda APENAS com um JSON válido no seguinte formato:
{{"score": <1-5>, "justification": "<explicação>"}}

Escala:
1 = Resposta completamente degradada ou incorreta
2 = Resposta significativamente pior que a original
3 = Resposta parcialmente degradada
4 = Resposta levemente afetada mas ainda correta
5 = Resposta manteve a mesma qualidade da original"""


class JudgeResult(BaseModel):
    """Saída padronizada de uma avaliação do juiz.

    Attributes:
        dimension: Dimensão de confiabilidade avaliada.
        score: Pontuação inteira de 1 a 5 (clampada após parse).
        justification: Texto da justificativa fornecida pelo juiz.
        metadata: Metadados adicionais (latência da chamada, indicador de
            fallback no parse, modelo usado pelo juiz, etc.).
    """

    model_config = ConfigDict(extra="forbid")

    dimension: str
    score: int = Field(ge=1, le=5)
    justification: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("dimension")
    @classmethod
    def _validate_dimension(cls, v: str) -> str:
        if v not in ALLOWED_DIMENSIONS:
            raise ValueError(f"Invalid dimension '{v}'. Allowed values: {list(ALLOWED_DIMENSIONS)}")
        return v


class Judge:
    """LLM-as-a-Judge orquestrado por um :class:`BaseProvider`.

    A classe é estatelessa em relação ao histórico de avaliações: cada chamada
    de ``evaluate_*`` envia um prompt independente para o provider configurado
    como juiz, parseia a resposta e retorna um :class:`JudgeResult`.

    Attributes:
        provider: Provider responsável pelas chamadas ao LLM avaliador.
    """

    def __init__(self, provider: BaseProvider) -> None:
        """Inicializa o juiz com o provider que executará as chamadas ao LLM avaliador.

        Args:
            provider: Provider responsável pelas chamadas ao LLM avaliador.
        """
        self.provider = provider

    def evaluate_factual(self, prompt: str, ground_truth: str, response: str) -> JudgeResult:
        """Avalia a precisão factual de uma resposta contra o ground truth."""
        judge_prompt = FACTUAL_PROMPT.format(
            prompt=prompt,
            ground_truth=ground_truth,
            response=response,
        )
        return self._evaluate("factual", judge_prompt)

    def evaluate_consistency(self, prompt: str, responses: list[str]) -> JudgeResult:
        """Avalia a consistência semântica entre múltiplas respostas a paráfrases.

        Args:
            prompt: Pergunta original (não-paráfrase).
            responses: Respostas do chatbot às paráfrases. Deve ter pelo menos
                duas entradas para que a avaliação seja significativa, mas a
                função aceita listas menores e delega ao juiz.
        """
        responses_text = "\n---\n".join(f"Resposta {i + 1}: {r}" for i, r in enumerate(responses))
        judge_prompt = CONSISTENCY_PROMPT.format(
            prompt=prompt,
            responses=responses_text,
        )
        return self._evaluate("consistency", judge_prompt)

    def evaluate_robustness(
        self,
        prompt: str,
        original_response: str,
        variant_type: str,
        variant_prompt: str,
        variant_response: str,
    ) -> JudgeResult:
        """Avalia a robustez da resposta a uma variação adversarial do prompt."""
        judge_prompt = ROBUSTNESS_PROMPT.format(
            prompt=prompt,
            original_response=original_response,
            variant_type=variant_type,
            variant_prompt=variant_prompt,
            variant_response=variant_response,
        )
        return self._evaluate("robustness", judge_prompt)

    def _evaluate(self, dimension: str, judge_prompt: str) -> JudgeResult:
        provider_response = self.provider.send(judge_prompt)
        parsed = self._parse_response(provider_response.response_text)
        score = _clamp_score(parsed["score"])

        metadata: dict[str, Any] = {
            "response_time_ms": provider_response.response_time_ms,
            "judge_model": provider_response.model,
            "parse_method": parsed["parse_method"],
        }
        if parsed["justification_fallback"]:
            metadata["justification_fallback"] = True
        if parsed["parse_method"] != "json":
            metadata["raw_response"] = provider_response.response_text

        return JudgeResult(
            dimension=dimension,
            score=score,
            justification=parsed["justification"],
            metadata=metadata,
        )

    def _parse_response(self, text: str) -> dict[str, Any]:
        """Parse the judge response into ``{score, justification, parse_method, justification_fallback}``.

        Tries strategies in order:

        1. Strict JSON over the trimmed text (after stripping markdown fences)
        2. Substring scan for the first balanced ``{...}`` block of valid JSON
        3. Regex fallback extracting ``score`` and ``justification`` directly

        Whenever a score is recovered but the justification is missing or
        empty, the score is kept (it carries signal even without explanation)
        and the justification is replaced by :data:`DEFAULT_FALLBACK_JUSTIFICATION`.
        The flag ``justification_fallback=True`` is reported in the result
        and propagated into ``JudgeResult.metadata`` so downstream consumers
        (notably the human-validation sampling for issue #20) can prioritize
        these cases.

        When no usable score can be recovered, returns a neutral default
        (``DEFAULT_FALLBACK_SCORE``) and logs a warning. The chosen strategy
        is always reported via ``parse_method``.
        """
        cleaned = _strip_code_fences(text)

        try:
            data = json.loads(cleaned)
            if isinstance(data, dict) and "score" in data:
                return _build_parsed(data.get("justification"), data["score"], "json")
        except json.JSONDecodeError:
            pass

        embedded = _find_first_json_object(cleaned)
        if embedded is not None:
            try:
                data = json.loads(embedded)
                if isinstance(data, dict) and "score" in data:
                    return _build_parsed(data.get("justification"), data["score"], "json_embedded")
            except json.JSONDecodeError:
                pass

        score_match = re.search(r'"?score"?\s*[:=]\s*(-?\d+)', text)
        just_match = re.search(
            r'"?justification"?\s*[:=]\s*"((?:[^"\\]|\\.)*)"',
            text,
        )
        if score_match:
            logger.warning("Judge response parsed via regex fallback: %r", text[:200])
            return _build_parsed(
                just_match.group(1) if just_match else None,
                int(score_match.group(1)),
                "regex",
            )

        logger.warning(
            "Judge response could not be parsed; using neutral default: %r",
            text[:200],
        )
        return {
            "score": DEFAULT_FALLBACK_SCORE,
            "justification": DEFAULT_FALLBACK_JUSTIFICATION,
            "parse_method": "default",
            "justification_fallback": True,
        }


def _build_parsed(
    raw_justification: Any,
    score: Any,
    parse_method: str,
) -> dict[str, Any]:
    """Build a parsed-result dict, substituting fallback when justification is empty.

    The judge's contract requires a non-empty explanation. When the model
    returned a score but no usable justification, we keep the score (it is
    the primary signal) and substitute the default message, flagging the
    substitution so downstream consumers can filter or resample these cases.
    """
    justification = str(raw_justification).strip() if raw_justification is not None else ""
    if not justification:
        return {
            "score": score,
            "justification": DEFAULT_FALLBACK_JUSTIFICATION,
            "parse_method": parse_method,
            "justification_fallback": True,
        }
    return {
        "score": score,
        "justification": justification,
        "parse_method": parse_method,
        "justification_fallback": False,
    }


def _strip_code_fences(text: str) -> str:
    """Remove leading/trailing markdown code fences if present.

    Handles ```` ```json ... ``` ```` and ```` ``` ... ``` `` ` styles produced
    by chat models when they were instructed to output JSON.
    """
    cleaned = text.strip()
    if cleaned.startswith("```"):
        first_break = cleaned.find("\n")
        if first_break != -1:
            cleaned = cleaned[first_break + 1 :]
        if cleaned.endswith("```"):
            cleaned = cleaned[: -len("```")]
        cleaned = cleaned.strip()
    return cleaned


def _find_first_json_object(text: str) -> str | None:
    """Return the first balanced ``{...}`` substring, or ``None`` if missing.

    Scans linearly tracking brace depth while respecting escaped quotes inside
    string literals. The substring is returned verbatim so the caller can
    re-parse it with :func:`json.loads`.
    """
    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if escape:
            escape = False
            continue
        if ch == "\\" and in_string:
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def _clamp_score(raw: Any) -> int:
    """Coerce ``raw`` to an int in [1, 5], defaulting to 3 if conversion fails."""
    try:
        score = int(raw)
    except (TypeError, ValueError):
        logger.warning("Judge produced non-integer score %r; defaulting to 3", raw)
        return DEFAULT_FALLBACK_SCORE
    if score < 1:
        return 1
    if score > 5:
        return 5
    return score
