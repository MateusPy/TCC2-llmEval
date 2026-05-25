"""Retry minimalista para chamadas ao LLM.

Replicado localmente (em vez de importado do llm-eval) para que este exemplo
fique autocontido: um terceiro pode copiar o diretório inteiro e adaptar
sem precisar instalar o framework como dependência do próprio chatbot.

Cobre apenas o caso do dia-a-dia (HTTP 429 com ou sem hint de Retry-After).
Para erros mais sofisticados (5xx, timeouts), adicione no seu próprio retry.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RateLimitError(Exception):
    """Erro de rate-limit (HTTP 429).

    Se o servidor informou ``Retry-After`` (ou equivalente), passe o valor em
    segundos via ``retry_after`` — o loop de retry vai esperar esse tempo
    em vez do backoff local.
    """

    def __init__(self, message: str, *, retry_after: float | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


def retry_with_backoff(
    fn: Callable[[], T],
    *,
    max_attempts: int = 4,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
) -> T:
    """Executa ``fn`` com retry exponencial quando aparecer ``RateLimitError``.

    Honra o hint do servidor (atributo ``retry_after`` na exceção) quando
    presente, somando 1 segundo de buffer. Caso contrário, usa backoff
    exponencial local.
    """
    delay = initial_delay
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except RateLimitError as exc:
            if attempt == max_attempts:
                logger.warning("Rate-limit após %d tentativas, desistindo", max_attempts)
                raise
            wait = exc.retry_after + 1.0 if exc.retry_after is not None else delay
            logger.info(
                "Rate-limit (tentativa %d/%d), aguardando %.1fs",
                attempt,
                max_attempts,
                wait,
            )
            time.sleep(wait)
            delay *= backoff_factor

    raise RuntimeError("inalcançável")  # defensivo, satisfaz o type checker
