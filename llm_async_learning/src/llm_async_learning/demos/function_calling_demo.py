from __future__ import annotations

from llm_async_learning.client import LLMClient
from llm_async_learning.models import ChatMessage, FunctionCallingRequest


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather by city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                },
                "required": ["city"],
            },
        },
    }
]


async def run_function_calling_demo(client: LLMClient) -> tuple[str | None, str | None]:
    request = FunctionCallingRequest(
        messages=[
            ChatMessage(role="system", content="Use tool when necessary."),
            ChatMessage(role="user", content="What is the weather in Shanghai?"),
        ],
        tools=TOOLS,
    )
    response = await client.function_call(request)
    return response.tool_name, response.tool_arguments_json
