from __future__ import annotations

import os

import pytest

from llm_async_learning.client import LLMClient
from llm_async_learning.config import load_settings
from llm_async_learning.models import ChatMessage, ChatRequest


pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_real_chat_integration() -> None:
    if os.getenv("RUN_INTEGRATION") != "1":
        pytest.skip("Set RUN_INTEGRATION=1 to run integration tests")

    settings = load_settings()
    client = LLMClient(settings)
    response = await client.chat(
        ChatRequest(messages=[ChatMessage(role="user", content="Reply with OK")])
    )
    assert response.content
