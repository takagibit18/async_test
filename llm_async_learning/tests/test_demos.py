import pytest

from llm_async_learning.demos.chat_demo import run_chat_demo
from llm_async_learning.demos.embedding_demo import run_embedding_demo
from llm_async_learning.demos.function_calling_demo import run_function_calling_demo
from llm_async_learning.demos.streaming_demo import run_streaming_demo


class FakeClient:
    async def chat(self, request):
        class R:
            content = "asyncio lets coroutines cooperate"

        return R()

    async def embedding(self, request):
        class R:
            vectors = [[0.1, 0.2], [0.2, 0.3]]

        return R()

    async def function_call(self, request):
        class R:
            tool_name = "get_weather"
            tool_arguments_json = '{"city":"Shanghai"}'

        return R()

    async def stream_chat(self, request):
        for chunk in ["hello", " ", "stream"]:
            yield chunk


@pytest.mark.asyncio
async def test_chat_demo() -> None:
    out = await run_chat_demo(FakeClient())
    assert "asyncio" in out


@pytest.mark.asyncio
async def test_embedding_demo() -> None:
    out = await run_embedding_demo(FakeClient())
    assert out == 2


@pytest.mark.asyncio
async def test_function_demo() -> None:
    tool, args_json = await run_function_calling_demo(FakeClient())
    assert tool == "get_weather"
    assert "Shanghai" in args_json


@pytest.mark.asyncio
async def test_stream_demo() -> None:
    out = await run_streaming_demo(FakeClient())
    assert out == "hello stream"
