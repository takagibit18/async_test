from __future__ import annotations

from llm_async_learning.client import LLMClient
from llm_async_learning.models import EmbeddingRequest


async def run_embedding_demo(client: LLMClient) -> int:
    request = EmbeddingRequest(input_texts=["asyncio concurrency", "pydantic validation"])
    response = await client.embedding(request)
    return len(response.vectors)
