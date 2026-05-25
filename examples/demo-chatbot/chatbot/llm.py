"""Wrapper do client Groq.

Mantido fino de propósito: uma função pública ``generate(prompt) -> str``.
Configuração vem 100% do ambiente (12-factor), o que facilita rodar em
Docker, CI e máquinas de dev sem mudar código.
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache

from groq import APIStatusError, Groq, RateLimitError as GroqRateLimitError

from chatbot.prompts import SYSTEM_PROMPT
from chatbot.retry import RateLimitError, retry_with_backoff

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "llama-3.1-8b-instant"
DEFAULT_TEMPERATURE = 0.0
DEFAULT_MAX_TOKENS = 512


@lru_cache(maxsize=1)
def _client() -> Groq:
    """Cria o client Groq na primeira chamada.

    Lazy para que ``/health`` funcione mesmo se ``GROQ_API_KEY`` estiver
    ausente (importar o módulo não deve falhar).
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY não está definida. Exporte a variável antes de chamar /chat."
        )
    return Groq(api_key=api_key)


def generate(prompt: str) -> str:
    """Envia ``prompt`` ao Llama via Groq e retorna o texto da resposta.

    Aplica retry exponencial em 429s, honrando o ``Retry-After`` do servidor
    quando informado. Erros não-retryables (auth, payload inválido) sobem
    sem tratamento para o caller decidir o HTTP status apropriado.
    """
    model = os.environ.get("GROQ_MODEL", DEFAULT_MODEL)

    def _call() -> str:
        try:
            completion = _client().chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=DEFAULT_MAX_TOKENS,
            )
        except GroqRateLimitError as exc:
            retry_after = _extract_retry_after(exc)
            raise RateLimitError(f"Groq rate-limited: {exc}", retry_after=retry_after) from exc

        text = completion.choices[0].message.content
        if not text:
            raise RuntimeError("Groq retornou resposta vazia")
        return text

    return retry_with_backoff(_call)


def _extract_retry_after(exc: APIStatusError) -> float | None:
    """Lê o header ``retry-after`` da resposta HTTP do Groq quando presente."""
    response = getattr(exc, "response", None)
    if response is None:
        return None
    header = response.headers.get("retry-after") if hasattr(response, "headers") else None
    if not header:
        return None
    try:
        return float(header)
    except (TypeError, ValueError):
        return None
