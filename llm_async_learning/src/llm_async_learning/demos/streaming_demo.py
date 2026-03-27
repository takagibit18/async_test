from __future__ import annotations

from llm_async_learning.client import LLMClient
from llm_async_learning.models import ChatMessage, ChatRequest


async def run_streaming_demo(client: LLMClient) -> str:
    request = ChatRequest(
        messages=[
            ChatMessage(role="system", content="You are concise."),
            ChatMessage(role="user", content="Stream one short paragraph about tiktoken."),
        ]
    )

    chunks: list[str] = []
    async for piece in client.stream_chat(request):
        chunks.append(piece)
    return "".join(chunks)
