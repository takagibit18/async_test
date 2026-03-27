from __future__ import annotations

from types import SimpleNamespace

import pytest

from llm_async_learning.client import LLMClient
from llm_async_learning.config import AppSettings
from llm_async_learning.models import ChatMessage, ChatRequest, EmbeddingRequest, FunctionCallingRequest


class FakeChatCreate:
    def __init__(self) -> None:
        self.calls = 0

    async def __call__(self, **kwargs):
        self.calls += 1
        if self.calls == 1:
            raise TimeoutError("transient timeout")
        usage = SimpleNamespace(prompt_tokens=11, completion_tokens=7, total_tokens=18)
        msg = SimpleNamespace(content="done", tool_calls=[])
        choice = SimpleNamespace(message=msg)
        return SimpleNamespace(choices=[choice], usage=usage)


class FakeEmbeddingCreate:
    async def __call__(self, **kwargs):
        usage = SimpleNamespace(prompt_tokens=8, completion_tokens=0, total_tokens=8)
        data = [SimpleNamespace(embedding=[0.1, 0.2]), SimpleNamespace(embedding=[0.2, 0.3])]
        return SimpleNamespace(data=data, usage=usage)


class FakeFunctionCreate:
    async def __call__(self, **kwargs):
        usage = SimpleNamespace(prompt_tokens=12, completion_tokens=4, total_tokens=16)
        fn = SimpleNamespace(name="get_weather", arguments='{"city":"Shanghai"}')
        tool_call = SimpleNamespace(function=fn)
        msg = SimpleNamespace(content=None, tool_calls=[tool_call])
        choice = SimpleNamespace(message=msg)
        return SimpleNamespace(choices=[choice], usage=usage)


class FakeStreamCreate:
    async def __call__(self, **kwargs):
        class FakeStream:
            async def __aiter__(self):
                for text in ["A", "B", "C"]:
                    delta = SimpleNamespace(content=text)
                    choice = SimpleNamespace(delta=delta)
                    yield SimpleNamespace(choices=[choice])

        return FakeStream()


def make_client() -> LLMClient:
    settings = AppSettings(
        openai_api_key="test-key",
        openai_base_url="https://example.com/v1",
        openai_retry_attempts=2,
        openai_retry_min_seconds=0,
        openai_retry_max_seconds=1,
        openai_max_concurrency=2,
    )
    return LLMClient(settings)


@pytest.mark.asyncio
async def test_chat_retries_once_and_records_usage() -> None:
    client = make_client()
    fake_create = FakeChatCreate()
    client.client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=fake_create)),
        embeddings=SimpleNamespace(create=FakeEmbeddingCreate()),
    )

    request = ChatRequest(messages=[ChatMessage(role="user", content="hello")])
    result = await client.chat(request)

    assert result.content == "done"
    assert fake_create.calls == 2
    assert client.usage_tracker.total_tokens() == 18


@pytest.mark.asyncio
async def test_embedding_records_usage() -> None:
    client = make_client()
    client.client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=FakeChatCreate())),
        embeddings=SimpleNamespace(create=FakeEmbeddingCreate()),
    )

    request = EmbeddingRequest(input_texts=["a", "b"])
    result = await client.embedding(request)

    assert len(result.vectors) == 2
    assert result.total_tokens == 8


@pytest.mark.asyncio
async def test_function_call_extracts_tool() -> None:
    client = make_client()
    client.client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=FakeFunctionCreate())),
        embeddings=SimpleNamespace(create=FakeEmbeddingCreate()),
    )

    request = FunctionCallingRequest(
        messages=[ChatMessage(role="user", content="weather?")],
        tools=[{"type": "function", "function": {"name": "get_weather", "parameters": {"type": "object"}}}],
    )
    result = await client.function_call(request)

    assert result.tool_name == "get_weather"
    assert "Shanghai" in (result.tool_arguments_json or "")


@pytest.mark.asyncio
async def test_stream_chat_yields_content_and_records_usage() -> None:
    client = make_client()
    client.client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=FakeStreamCreate())),
        embeddings=SimpleNamespace(create=FakeEmbeddingCreate()),
    )

    request = ChatRequest(messages=[ChatMessage(role="user", content="stream")])
    chunks = []
    async for chunk in client.stream_chat(request):
        chunks.append(chunk)

    assert "".join(chunks) == "ABC"
    assert client.usage_tracker.total_tokens() > 0
