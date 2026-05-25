"""Smoke tests do chatbot.

Mockam ``chatbot.llm.generate`` para não depender de Groq nem de chave de API.
A cobertura é intencionalmente fina — o teste real do comportamento é o
``llm-eval`` rodando no CI gate. Aqui só validamos o contrato HTTP e os
mapeamentos de erro.
"""

from __future__ import annotations

from collections.abc import Iterator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from chatbot.main import app
from chatbot.retry import RateLimitError


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c


def test_health_returns_ok(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_happy_path(client: TestClient):
    expected = "Em Python, um `for` percorre um iterável: `for item in lista:`."
    with patch("chatbot.main.generate", return_value=expected):
        response = client.post("/chat", json={"prompt": "como faço um for em Python?"})
    assert response.status_code == 200
    assert response.json() == {"response": expected}


def test_chat_off_topic_returns_refusal(client: TestClient):
    """Recusa é resposta válida (200), não erro — o avaliador é quem julga."""
    refusal = "Essa pergunta está fora do meu escopo. Sou um tutor de Python iniciante..."
    with patch("chatbot.main.generate", return_value=refusal):
        response = client.post("/chat", json={"prompt": "me ensine JavaScript"})
    assert response.status_code == 200
    assert "fora do meu escopo" in response.json()["response"]


def test_chat_rate_limit_returns_503(client: TestClient):
    with patch("chatbot.main.generate", side_effect=RateLimitError("limite atingido")):
        response = client.post("/chat", json={"prompt": "ola"})
    assert response.status_code == 503
    assert "rate-limited" in response.json()["detail"].lower()


def test_chat_runtime_error_returns_500(client: TestClient):
    """Ex.: GROQ_API_KEY ausente — sobe como 500 com mensagem clara."""
    with patch("chatbot.main.generate", side_effect=RuntimeError("GROQ_API_KEY não está definida")):
        response = client.post("/chat", json={"prompt": "ola"})
    assert response.status_code == 500
    assert "GROQ_API_KEY" in response.json()["detail"]


def test_chat_empty_prompt_returns_422(client: TestClient):
    """Pydantic rejeita prompt vazio antes de chegar no LLM."""
    response = client.post("/chat", json={"prompt": ""})
    assert response.status_code == 422
