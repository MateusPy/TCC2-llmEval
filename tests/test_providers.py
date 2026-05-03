"""Testes para os providers concretos (Gemini, Mistral, Custom HTTP) e o retry helper."""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from llm_eval.providers import (
    CustomProvider,
    FatalError,
    GeminiProvider,
    MistralProvider,
    ProviderConfig,
    RateLimitError,
    TimeoutError,
    TransientError,
    build_from_settings,
    retry_with_backoff,
)
from llm_eval.providers.custom import _extract_by_path, _substitute_prompt


# ---------------------------------------------------------------------------
# Stubs
# ---------------------------------------------------------------------------


class _GeminiClientStub:
    """Mimics ``genai.GenerativeModel`` with a configurable ``generate_content``."""

    def __init__(
        self,
        *,
        text: str = "ok",
        usage: dict[str, int] | None = None,
        raise_on_call: BaseException | None = None,
        raise_then_succeed: bool = False,
    ) -> None:
        self._text = text
        self._usage = usage
        self._raise = raise_on_call
        self._raise_then_succeed = raise_then_succeed
        self.calls: list[dict[str, Any]] = []

    def generate_content(self, prompt: str, generation_config: dict[str, Any]) -> Any:
        self.calls.append({"prompt": prompt, "generation_config": generation_config})
        if self._raise is not None:
            exc, self._raise = self._raise, None if self._raise_then_succeed else self._raise
            raise exc

        class _UsageMetadata:
            def __init__(
                self, prompt_tokens: int, completion_tokens: int, total_tokens: int
            ) -> None:
                self.prompt_token_count = prompt_tokens
                self.candidates_token_count = completion_tokens
                self.total_token_count = total_tokens

        class _GeminiResponse:
            def __init__(self, text: str, usage: dict[str, int] | None) -> None:
                self.text = text
                self.usage_metadata = (
                    _UsageMetadata(
                        usage["prompt_tokens"],
                        usage["completion_tokens"],
                        usage["total_tokens"],
                    )
                    if usage
                    else None
                )

        return _GeminiResponse(self._text, self._usage)


class _MistralClientStub:
    """Mimics the ``mistralai.Mistral`` client (only ``chat.complete``)."""

    def __init__(
        self,
        *,
        text: str = "ok",
        usage: dict[str, int] | None = None,
        raise_on_call: BaseException | None = None,
    ) -> None:
        self._text = text
        self._usage = usage
        self._raise = raise_on_call
        self.calls: list[dict[str, Any]] = []
        self.chat = _MistralChat(self)


class _MistralChat:
    def __init__(self, parent: _MistralClientStub) -> None:
        self._parent = parent

    def complete(self, **kwargs: Any) -> Any:
        self._parent.calls.append(kwargs)
        if self._parent._raise is not None:
            raise self._parent._raise

        class _Message:
            def __init__(self, content: str) -> None:
                self.content = content

        class _Choice:
            def __init__(self, message: _Message) -> None:
                self.message = message

        class _Usage:
            def __init__(self, usage: dict[str, int]) -> None:
                self.prompt_tokens = usage["prompt_tokens"]
                self.completion_tokens = usage["completion_tokens"]
                self.total_tokens = usage["total_tokens"]

        class _MistralResponse:
            def __init__(self, text: str, usage: dict[str, int] | None) -> None:
                self.choices = [_Choice(_Message(text))]
                self.usage = _Usage(usage) if usage else None

        return _MistralResponse(self._parent._text, self._parent._usage)


class _MistralStatusError(Exception):
    """Mimics httpx-style status errors raised by mistralai SDK."""

    def __init__(self, status_code: int, message: str = "boom") -> None:
        super().__init__(message)
        self.status_code = status_code


# ---------------------------------------------------------------------------
# retry_with_backoff
# ---------------------------------------------------------------------------


def test_retry_returns_first_success():
    sleeps: list[float] = []
    calls = {"n": 0}

    def fn() -> int:
        calls["n"] += 1
        return 42

    result = retry_with_backoff(fn, sleep=sleeps.append)
    assert result == 42
    assert calls["n"] == 1
    assert sleeps == []


def test_retry_succeeds_after_one_failure():
    sleeps: list[float] = []
    attempts = {"n": 0}

    def fn() -> str:
        attempts["n"] += 1
        if attempts["n"] == 1:
            raise RateLimitError("first try")
        return "ok"

    result = retry_with_backoff(fn, sleep=sleeps.append, initial_delay=0.5, backoff_factor=2.0)
    assert result == "ok"
    assert attempts["n"] == 2
    assert sleeps == [0.5]


def test_retry_exhausts_all_attempts():
    sleeps: list[float] = []

    def fn() -> str:
        raise TransientError("server down")

    with pytest.raises(TransientError):
        retry_with_backoff(
            fn, max_attempts=3, sleep=sleeps.append, initial_delay=0.1, backoff_factor=2.0
        )
    assert sleeps == [0.1, 0.2]


def test_retry_does_not_swallow_fatal():
    sleeps: list[float] = []

    def fn() -> None:
        raise FatalError("auth")

    with pytest.raises(FatalError):
        retry_with_backoff(fn, sleep=sleeps.append)
    assert sleeps == []


def test_retry_invalid_max_attempts():
    with pytest.raises(ValueError):
        retry_with_backoff(lambda: 1, max_attempts=0)


# ---------------------------------------------------------------------------
# Gemini provider
# ---------------------------------------------------------------------------


def _gemini_config() -> ProviderConfig:
    return ProviderConfig(
        api_key="test-key", model="gemini-2.0-flash-001", temperature=0.0, max_tokens=512
    )


def test_gemini_send_happy_path():
    stub = _GeminiClientStub(
        text="resposta", usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
    )
    provider = GeminiProvider(_gemini_config(), client_factory=lambda _: stub)
    result = provider.send("oi")
    assert result.response_text == "resposta"
    assert result.model == "gemini-2.0-flash-001"
    assert result.parameters["temperature"] == 0.0
    assert result.parameters["usage"]["total_tokens"] == 15
    assert result.response_time_ms >= 0
    assert stub.calls[0]["prompt"] == "oi"
    assert stub.calls[0]["generation_config"]["max_output_tokens"] == 512


def test_gemini_send_omits_usage_when_absent():
    stub = _GeminiClientStub(text="ok", usage=None)
    provider = GeminiProvider(_gemini_config(), client_factory=lambda _: stub)
    result = provider.send("oi")
    assert "usage" not in result.parameters


def test_gemini_send_forwards_seed_when_set():
    """seed must appear in generation_config and parameters when configured."""
    stub = _GeminiClientStub(text="ok")
    config = ProviderConfig(
        api_key="k", model="gemini-2.0-flash-001", temperature=0.0, max_tokens=128, seed=42
    )
    provider = GeminiProvider(config, client_factory=lambda _: stub)
    result = provider.send("oi")
    assert stub.calls[0]["generation_config"]["seed"] == 42
    assert result.parameters["seed"] == 42


def test_gemini_send_omits_seed_when_none():
    stub = _GeminiClientStub(text="ok")
    config = ProviderConfig(api_key="k", model="gemini-2.0-flash-001")
    provider = GeminiProvider(config, client_factory=lambda _: stub)
    result = provider.send("oi")
    assert "seed" not in stub.calls[0]["generation_config"]
    assert "seed" not in result.parameters


def test_gemini_send_translates_rate_limit():
    class ResourceExhausted(Exception):
        pass

    stub = _GeminiClientStub(raise_on_call=ResourceExhausted("quota"))
    provider = GeminiProvider(_gemini_config(), client_factory=lambda _: stub, max_attempts=1)
    with pytest.raises(RateLimitError):
        provider.send("oi")


def test_gemini_send_translates_timeout():
    class DeadlineExceeded(Exception):
        pass

    stub = _GeminiClientStub(raise_on_call=DeadlineExceeded("timeout after 30s"))
    provider = GeminiProvider(_gemini_config(), client_factory=lambda _: stub, max_attempts=1)
    with pytest.raises(TimeoutError):
        provider.send("oi")


def test_gemini_send_translates_5xx():
    stub = _GeminiClientStub(raise_on_call=Exception("HTTP 503 service unavailable"))
    provider = GeminiProvider(_gemini_config(), client_factory=lambda _: stub, max_attempts=1)
    with pytest.raises(TransientError):
        provider.send("oi")


def test_gemini_send_unknown_error_becomes_fatal():
    stub = _GeminiClientStub(raise_on_call=ValueError("malformed prompt"))
    provider = GeminiProvider(_gemini_config(), client_factory=lambda _: stub, max_attempts=1)
    with pytest.raises(FatalError):
        provider.send("oi")


def test_gemini_send_retries_on_rate_limit_then_succeeds():
    class ResourceExhausted(Exception):
        pass

    stub = _GeminiClientStub(
        text="depois deu certo", raise_on_call=ResourceExhausted("quota"), raise_then_succeed=True
    )
    sleeps: list[float] = []
    provider = GeminiProvider(
        _gemini_config(),
        client_factory=lambda _: stub,
        max_attempts=3,
        initial_delay=0.01,
        sleep=sleeps.append,
    )
    result = provider.send("oi")
    assert result.response_text == "depois deu certo"
    assert sleeps == [0.01]


def test_gemini_default_factory_warns_on_api_key_change(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The default factory mutates global SDK state; warn when key actually changes."""
    import logging as _logging

    from llm_eval.providers import gemini as gemini_module

    configure_calls: list[str] = []

    class _FakeGenAI:
        @staticmethod
        def configure(api_key: str) -> None:
            configure_calls.append(api_key)

        @staticmethod
        def GenerativeModel(model: str) -> object:  # noqa: N802 - matches SDK API
            return object()

    monkeypatch.setitem(__import__("sys").modules, "google.generativeai", _FakeGenAI)
    monkeypatch.setattr(gemini_module, "_last_configured_key", None, raising=False)

    cfg_a = ProviderConfig(api_key="key-a", model="gemini-2.0-flash-001")
    cfg_b = ProviderConfig(api_key="key-b", model="gemini-2.0-flash-001")

    with caplog.at_level(_logging.WARNING):
        gemini_module._default_client_factory(cfg_a)
        gemini_module._default_client_factory(cfg_a)  # same key — no warning
        gemini_module._default_client_factory(cfg_b)  # different key — warns

    assert configure_calls == ["key-a", "key-a", "key-b"]
    warnings = [rec for rec in caplog.records if "different API key" in rec.message]
    assert len(warnings) == 1


# ---------------------------------------------------------------------------
# Mistral provider
# ---------------------------------------------------------------------------


def _mistral_config() -> ProviderConfig:
    return ProviderConfig(
        api_key="test", model="mistral-small-2503", temperature=0.2, max_tokens=256
    )


def test_mistral_send_happy_path():
    stub = _MistralClientStub(
        text="oi", usage={"prompt_tokens": 7, "completion_tokens": 3, "total_tokens": 10}
    )
    provider = MistralProvider(_mistral_config(), client_factory=lambda _: stub)
    result = provider.send("ola")
    assert result.response_text == "oi"
    assert result.model == "mistral-small-2503"
    assert result.parameters["usage"]["prompt_tokens"] == 7
    call = stub.calls[0]
    assert call["model"] == "mistral-small-2503"
    assert call["messages"] == [{"role": "user", "content": "ola"}]
    assert call["temperature"] == 0.2
    assert call["max_tokens"] == 256
    # Seed not configured here — must not be sent to the SDK.
    assert "random_seed" not in call


def test_mistral_send_forwards_seed_as_random_seed():
    """Mistral's SDK uses random_seed; the provider must rename the field."""
    stub = _MistralClientStub(text="ok")
    config = ProviderConfig(
        api_key="k", model="mistral-small-2503", temperature=0.0, max_tokens=64, seed=42
    )
    provider = MistralProvider(config, client_factory=lambda _: stub)
    result = provider.send("oi")
    assert stub.calls[0]["random_seed"] == 42
    assert result.parameters["seed"] == 42


def test_mistral_send_translates_429_status_code():
    stub = _MistralClientStub(raise_on_call=_MistralStatusError(429, "rate limit"))
    provider = MistralProvider(_mistral_config(), client_factory=lambda _: stub, max_attempts=1)
    with pytest.raises(RateLimitError):
        provider.send("oi")


def test_mistral_send_translates_500_status_code():
    stub = _MistralClientStub(raise_on_call=_MistralStatusError(503, "down"))
    provider = MistralProvider(_mistral_config(), client_factory=lambda _: stub, max_attempts=1)
    with pytest.raises(TransientError):
        provider.send("oi")


def test_mistral_send_unknown_error_becomes_fatal():
    stub = _MistralClientStub(raise_on_call=ValueError("auth"))
    provider = MistralProvider(_mistral_config(), client_factory=lambda _: stub, max_attempts=1)
    with pytest.raises(FatalError):
        provider.send("oi")


def test_mistral_send_no_choices_returns_empty():
    class _EmptyResponse:
        choices: list[Any] = []
        usage = None

    class _EmptyChat:
        def complete(self, **_: Any) -> Any:
            return _EmptyResponse()

    class _StubClient:
        chat = _EmptyChat()

    provider = MistralProvider(_mistral_config(), client_factory=lambda _: _StubClient())
    result = provider.send("oi")
    assert result.response_text == ""


def test_mistral_send_message_none_returns_empty():
    """choices[0].message is None — produce empty text rather than crash."""

    class _Choice:
        message = None

    class _Response:
        choices = [_Choice()]
        usage = None

    class _Chat:
        def complete(self, **_: Any) -> Any:
            return _Response()

    class _Client:
        chat = _Chat()

    provider = MistralProvider(_mistral_config(), client_factory=lambda _: _Client())
    result = provider.send("oi")
    assert result.response_text == ""


def test_mistral_send_content_none_returns_empty():
    """message.content is None — empty string instead of 'None'."""

    class _Message:
        content = None

    class _Choice:
        message = _Message()

    class _Response:
        choices = [_Choice()]
        usage = None

    class _Chat:
        def complete(self, **_: Any) -> Any:
            return _Response()

    class _Client:
        chat = _Chat()

    provider = MistralProvider(_mistral_config(), client_factory=lambda _: _Client())
    result = provider.send("oi")
    assert result.response_text == ""


def test_mistral_send_usage_all_none_returns_no_usage():
    """When prompt/completion/total are all None on usage, omit it from parameters."""

    class _Usage:
        prompt_tokens = None
        completion_tokens = None
        total_tokens = None

    class _Message:
        content = "ok"

    class _Choice:
        message = _Message()

    class _Response:
        choices = [_Choice()]
        usage = _Usage()

    class _Chat:
        def complete(self, **_: Any) -> Any:
            return _Response()

    class _Client:
        chat = _Chat()

    provider = MistralProvider(_mistral_config(), client_factory=lambda _: _Client())
    result = provider.send("oi")
    assert "usage" not in result.parameters


def test_mistral_send_translates_timeout():
    class ReadTimeout(Exception):
        pass

    stub = _MistralClientStub(raise_on_call=ReadTimeout("read timed out after 30s"))
    provider = MistralProvider(_mistral_config(), client_factory=lambda _: stub, max_attempts=1)
    with pytest.raises(TimeoutError):
        provider.send("oi")


# ---------------------------------------------------------------------------
# BaseProvider — send_batch default behavior
# ---------------------------------------------------------------------------


def test_base_provider_send_batch_calls_send_per_prompt():
    """Default send_batch should iterate and accumulate responses in order."""
    from llm_eval.providers.base import BaseProvider, ProviderConfig, ProviderResponse
    from datetime import datetime, timezone

    class _CountingProvider(BaseProvider):
        def __init__(self) -> None:
            super().__init__(ProviderConfig(api_key="x", model="m"))
            self.calls: list[str] = []

        def send(self, prompt: str) -> ProviderResponse:
            self.calls.append(prompt)
            return ProviderResponse(
                response_text=f"reply-{prompt}",
                model=self.config.model,
                timestamp=datetime.now(timezone.utc),
                response_time_ms=1.0,
                parameters={},
            )

    provider = _CountingProvider()
    results = provider.send_batch(["a", "b", "c"])

    assert provider.calls == ["a", "b", "c"]
    assert [r.response_text for r in results] == ["reply-a", "reply-b", "reply-c"]


def test_base_provider_send_is_abstract():
    """BaseProvider.send() must raise when called on the abstract class itself."""
    from llm_eval.providers.base import BaseProvider, ProviderConfig

    class _MinimalConcrete(BaseProvider):
        # Inherit `send` but call up to the ABC body to exercise NotImplementedError
        def send(self, prompt: str):  # noqa: ANN201
            return BaseProvider.send(self, prompt)

    with pytest.raises(NotImplementedError):
        _MinimalConcrete(ProviderConfig(api_key="x", model="m")).send("x")


# ---------------------------------------------------------------------------
# Gemini — fallback _extract_text path (no `.text` property)
# ---------------------------------------------------------------------------


def test_gemini_extract_text_falls_back_to_candidates():
    """When the response has no `.text` but has candidates+content+parts, join part texts."""
    from llm_eval.providers.gemini import _extract_text

    class _Part:
        def __init__(self, text: str) -> None:
            self.text = text

    class _Content:
        def __init__(self, parts: list[_Part]) -> None:
            self.parts = parts

    class _Candidate:
        def __init__(self, content: _Content) -> None:
            self.content = content

    class _Response:
        candidates = [_Candidate(_Content([_Part("Hello "), _Part("world")]))]

    assert _extract_text(_Response()) == "Hello world"


def test_gemini_extract_text_no_text_no_candidates_returns_empty():
    class _Response:
        text = None
        candidates: list[Any] = []

    from llm_eval.providers.gemini import _extract_text

    assert _extract_text(_Response()) == ""


def test_gemini_extract_usage_all_none_returns_none():
    """When prompt/completion/total are all None, _extract_usage returns None."""
    from llm_eval.providers.gemini import _extract_usage

    class _Usage:
        prompt_token_count = None
        candidates_token_count = None
        total_token_count = None

    class _Response:
        usage_metadata = _Usage()

    assert _extract_usage(_Response()) is None


# ---------------------------------------------------------------------------
# Custom HTTP provider — helpers
# ---------------------------------------------------------------------------


def test_substitute_prompt_string():
    assert _substitute_prompt("hello {prompt}", "world") == "hello world"


def test_substitute_prompt_nested():
    template = {"messages": [{"role": "user", "content": "Q: {prompt}"}], "temperature": 0.0}
    out = _substitute_prompt(template, "p?")
    assert out == {"messages": [{"role": "user", "content": "Q: p?"}], "temperature": 0.0}


def test_substitute_prompt_non_text_left_alone():
    assert _substitute_prompt(42, "x") == 42
    assert _substitute_prompt(None, "x") is None


def test_extract_by_path_dict():
    payload = {"choices": [{"message": {"content": "ola"}}]}
    assert _extract_by_path(payload, "choices.0.message.content") == "ola"


def test_extract_by_path_missing_key_raises_fatal():
    with pytest.raises(FatalError, match="not found"):
        _extract_by_path({"a": 1}, "missing")


def test_extract_by_path_index_out_of_range():
    with pytest.raises(FatalError, match="out of range"):
        _extract_by_path({"items": []}, "items.0")


def test_extract_by_path_descend_into_scalar():
    with pytest.raises(FatalError, match="Cannot descend"):
        _extract_by_path({"a": "leaf"}, "a.subkey")


def test_extract_by_path_non_int_segment_in_list():
    """When cursor is a list, segments must be integer-valued."""
    with pytest.raises(FatalError, match="not an int but cursor is a list"):
        _extract_by_path({"items": ["a", "b"]}, "items.first")


def test_extract_by_path_returns_empty_string_for_none_leaf():
    """A None leaf should be normalized to an empty string."""
    assert _extract_by_path({"answer": None}, "answer") == ""


# ---------------------------------------------------------------------------
# Custom HTTP provider — send()
# ---------------------------------------------------------------------------


def _custom_config() -> ProviderConfig:
    return ProviderConfig(api_key="", model="my-model", temperature=0.0, max_tokens=512)


def _stub_transport(responses: list[httpx.Response] | httpx.Response) -> httpx.Client:
    """Build an httpx.Client wired to a deterministic MockTransport."""
    queue = list(responses) if isinstance(responses, list) else [responses]

    def handler(request: httpx.Request) -> httpx.Response:
        if not queue:
            raise AssertionError("MockTransport ran out of responses")
        return queue.pop(0)

    transport = httpx.MockTransport(handler)
    return httpx.Client(transport=transport)


def test_custom_send_happy_path():
    payload = {"choices": [{"message": {"content": "Brasília"}}]}
    client = _stub_transport(httpx.Response(200, json=payload))
    provider = CustomProvider(
        _custom_config(),
        url="https://example.com/api",
        request_template={"messages": [{"role": "user", "content": "{prompt}"}]},
        response_path="choices.0.message.content",
        http_client=client,
    )
    result = provider.send("Qual a capital do Brasil?")
    assert result.response_text == "Brasília"
    assert result.parameters["url"] == "https://example.com/api"
    assert result.raw_response == payload
    # Seed defaults to None — must not appear in parameters.
    assert "seed" not in result.parameters


def test_custom_send_includes_seed_in_parameters_when_set():
    """Custom providers don't auto-inject the seed in the body — that is up to
    the user's request_template — but the seed must still be recorded in the
    response parameters for reproducibility metadata."""
    client = _stub_transport(httpx.Response(200, json={"answer": "ok"}))
    config = ProviderConfig(api_key="", model="my-model", temperature=0.0, max_tokens=128, seed=42)
    provider = CustomProvider(
        config,
        url="https://example.com",
        request_template={"prompt": "{prompt}"},
        response_path="answer",
        http_client=client,
    )
    result = provider.send("hi")
    assert result.parameters["seed"] == 42


def test_custom_send_treats_429_as_rate_limit():
    client = _stub_transport(httpx.Response(429, text="too many"))
    provider = CustomProvider(
        _custom_config(),
        url="https://example.com",
        response_path="x",
        http_client=client,
        max_attempts=1,
    )
    with pytest.raises(RateLimitError):
        provider.send("p")


def test_custom_send_treats_5xx_as_transient():
    client = _stub_transport(httpx.Response(503, text="down"))
    provider = CustomProvider(
        _custom_config(),
        url="https://example.com",
        response_path="x",
        http_client=client,
        max_attempts=1,
    )
    with pytest.raises(TransientError):
        provider.send("p")


def test_custom_send_treats_4xx_as_fatal():
    client = _stub_transport(httpx.Response(401, text="unauthorized"))
    provider = CustomProvider(
        _custom_config(),
        url="https://example.com",
        response_path="x",
        http_client=client,
        max_attempts=1,
    )
    with pytest.raises(FatalError):
        provider.send("p")


def test_custom_send_non_json_response_is_fatal():
    client = _stub_transport(httpx.Response(200, text="not json"))
    provider = CustomProvider(
        _custom_config(),
        url="https://example.com",
        response_path="x",
        http_client=client,
        max_attempts=1,
    )
    with pytest.raises(FatalError, match="non-JSON"):
        provider.send("p")


def test_custom_send_timeout_translates(monkeypatch: pytest.MonkeyPatch):
    def handler(_: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("slow")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = CustomProvider(
        _custom_config(),
        url="https://example.com",
        response_path="x",
        http_client=client,
        max_attempts=1,
    )
    with pytest.raises(TimeoutError):
        provider.send("p")


def test_custom_send_substitutes_prompt_in_template():
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(200, json={"text": "ok"})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = CustomProvider(
        _custom_config(),
        url="https://example.com",
        request_template={"messages": [{"content": "Q: {prompt}"}]},
        response_path="text",
        http_client=client,
    )
    provider.send("Hello?")
    body = json.loads(captured[0].read().decode("utf-8"))
    assert body == {"messages": [{"content": "Q: Hello?"}]}


def test_custom_provider_requires_url():
    with pytest.raises(ValueError, match="non-empty 'url'"):
        CustomProvider(_custom_config(), url="", response_path="x")


def test_custom_send_translates_generic_http_error_as_transient():
    """Non-timeout httpx.HTTPError (e.g., connect error) should map to TransientError."""

    def handler(_: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = CustomProvider(
        _custom_config(),
        url="https://example.com",
        response_path="x",
        http_client=client,
        max_attempts=1,
    )
    with pytest.raises(TransientError, match="HTTP error"):
        provider.send("p")


def test_custom_close_owned_client():
    """When the provider built its own client, close() releases it."""
    provider = CustomProvider(
        _custom_config(),
        url="https://example.com",
        response_path="x",
        timeout=1.0,
    )
    assert provider._owns_client is True
    provider.close()  # should not raise


def test_custom_close_does_not_close_injected_client():
    """An injected client outlives the provider — close() must not touch it."""
    closed = {"v": False}
    inner = httpx.Client(
        transport=httpx.MockTransport(lambda _: httpx.Response(200, json={"x": 1}))
    )
    original_close = inner.close

    def tracker() -> None:
        closed["v"] = True
        original_close()

    inner.close = tracker  # type: ignore[method-assign]
    provider = CustomProvider(
        _custom_config(),
        url="https://example.com",
        response_path="x",
        http_client=inner,
    )
    provider.close()
    assert closed["v"] is False
    inner.close = original_close  # type: ignore[method-assign]
    inner.close()


# ---------------------------------------------------------------------------
# build_from_settings
# ---------------------------------------------------------------------------


def test_build_from_settings_rejects_non_custom_type():
    with pytest.raises(ValueError, match="type='custom'"):
        build_from_settings(
            type="gemini",
            api_key="x",
            model="m",
            temperature=0.0,
            max_tokens=10,
            url="https://example.com",
            method="POST",
            headers={},
            request_template={},
            response_path="x",
        )


def test_build_from_settings_requires_url():
    with pytest.raises(ValueError, match="requires 'url'"):
        build_from_settings(
            type="custom",
            api_key="x",
            model="m",
            temperature=0.0,
            max_tokens=10,
            url=None,
            method="POST",
            headers={},
            request_template={},
            response_path="x",
        )


def test_build_from_settings_requires_response_path():
    with pytest.raises(ValueError, match="requires 'response_path'"):
        build_from_settings(
            type="custom",
            api_key="x",
            model="m",
            temperature=0.0,
            max_tokens=10,
            url="https://example.com",
            method="POST",
            headers={},
            request_template={},
            response_path=None,
        )


def test_build_from_settings_happy_path():
    client = _stub_transport(httpx.Response(200, json={"answer": "ok"}))
    provider = build_from_settings(
        type="custom",
        api_key="x",
        model="m",
        temperature=0.0,
        max_tokens=10,
        url="https://example.com",
        method="POST",
        headers={"Authorization": "Bearer abc"},
        request_template={"q": "{prompt}"},
        response_path="answer",
        http_client=client,
    )
    result = provider.send("hi")
    assert result.response_text == "ok"
    assert provider.headers["Authorization"] == "Bearer abc"
