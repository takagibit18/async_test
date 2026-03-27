from __future__ import annotations

from llm_async_learning.client import LLMClient
from llm_async_learning.models import ChatMessage, ChatRequest


async def run_chat_demo(client: LLMClient) -> str:
    request = ChatRequest(
        messages=[
            ChatMessage(role="system", content="You are a concise assistant."),
            ChatMessage(role="user", content="Give me one sentence about asyncio."),
        ]
    )
    response = await client.chat(request)
    return response.content
