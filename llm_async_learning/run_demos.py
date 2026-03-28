from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

# Allow direct script execution in src-layout projects without requiring editable install.
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

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
        # With graceful error handling so one failure doesn't stop others.
        async def safe_demo(name: str, coro):
            try:
                result = await coro
                print(f"✓ {name}: OK")
                return name, result, None
            except Exception as e:
                print(f"✗ {name}: {type(e).__name__}: {str(e)[:100]}")
                return name, None, e

        results = await asyncio.gather(
            safe_demo("chat", run_chat_demo(client)),
            safe_demo("embedding", run_embedding_demo(client)),
            safe_demo("function_call", run_function_calling_demo(client)),
            safe_demo("stream", run_streaming_demo(client)),
        )
        for name, result, error in results:
            if error is None:
                if name == "embedding":
                    print(f"  embedding vectors: {result}")
                elif name == "function_call":
                    print(f"  tool info: {result}")
                elif name == "stream":
                    print(f"  streamed: {result[:50]}...")
                else:
                    print(f"  response: {result[:50]}...")
            # Errors already printed above

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
