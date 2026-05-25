"""App FastAPI do chatbot.

Dois endpoints:

- ``GET /health`` — sanity para o CI esperar antes de rodar o llm-eval.
  Não chama o LLM, então funciona mesmo sem ``GROQ_API_KEY`` configurada.

- ``POST /chat`` — recebe ``{"prompt": str}``, devolve ``{"response": str}``.
  É o contrato consumido pelo ``CustomProvider`` do llm-eval (config em
  ``examples/demo-chatbot/config.yaml``).
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from chatbot.llm import generate
from chatbot.retry import RateLimitError

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Chatbot Tutor de Python",
    description="Exemplo de chatbot avaliado pelo llm-eval em CI.",
    version="0.1.0",
)


class ChatRequest(BaseModel):
    prompt: str = Field(min_length=1, description="Mensagem do aluno.")


class ChatResponse(BaseModel):
    response: str = Field(description="Resposta do tutor.")


@app.get("/health")
def health() -> dict[str, str]:
    """Retorna 200 OK quando o processo está vivo."""
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Encaminha o ``prompt`` ao LLM e devolve a resposta do tutor."""
    try:
        text = generate(request.prompt)
    except RateLimitError as exc:
        logger.warning("Rate-limit do Groq propagado: %s", exc)
        raise HTTPException(status_code=503, detail="LLM rate-limited, tente novamente.") from exc
    except RuntimeError as exc:
        logger.error("Falha ao gerar resposta: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return ChatResponse(response=text)
