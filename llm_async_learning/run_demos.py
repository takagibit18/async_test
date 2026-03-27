from __future__ import annotations

import argparse
import asyncio

from llm_async_learning.client import LLMClient
from llm_async_learning.config import load_settings
from llm_async_learning.demos.chat_demo import run_chat_demo
from llm_async_learning.demos.embedding_demo import run_embedding_demo
from llm_async_learning.demos.function_calling_demo import run_function_calling_demo
from llm_async_learning.demos.streaming_demo import run_streaming_demo


async def main(mode: str) -> None:
    settings = load_settings()
    client = LLMClient(settings)

    if mode == "chat":
        print(await run_chat_demo(client))
    elif mode == "embedding":
        print("embedding vectors:", await run_embedding_demo(client))
    elif mode == "function":
        tool_name, args_json = await run_function_calling_demo(client)
        print("tool:", tool_name)
        print("arguments:", args_json)
    elif mode == "stream":
        print(await run_streaming_demo(client))
    else:
        # Run demos concurrently to show asyncio scheduling and shared semaphore limits.
        chat_task = asyncio.create_task(run_chat_demo(client))
        embed_task = asyncio.create_task(run_embedding_demo(client))
        func_task = asyncio.create_task(run_function_calling_demo(client))
        stream_task = asyncio.create_task(run_streaming_demo(client))

        chat_text, embed_count, func_data, stream_text = await asyncio.gather(
            chat_task,
            embed_task,
            func_task,
            stream_task,
        )
        print("chat:", chat_text)
        print("embedding vectors:", embed_count)
        print("function calling:", func_data)
        print("stream:", stream_text)

    usage = client.usage_summary()
    print("token usage summary:", usage.model_dump())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run OpenAI demos")
    parser.add_argument(
        "--mode",
        choices=["all", "chat", "embedding", "function", "stream"],
        default="all",
    )
    args = parser.parse_args()
    asyncio.run(main(args.mode))
