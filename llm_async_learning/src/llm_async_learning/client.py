from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Any

from openai import APITimeoutError, AsyncOpenAI, RateLimitError
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_random_exponential

from .config import AppSettings
from .models import (
    ChatRequest,
    ChatResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    FunctionCallingRequest,
    FunctionCallingResponse,
    StreamSummary,
    TokenUsageRecord,
)
from .token_counter import TokenCounter
from .usage_tracker import UsageTracker


class LLMClient:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key.get_secret_value(),
            base_url=settings.openai_base_url,
            timeout=settings.openai_timeout_seconds,
        )
        self.semaphore = asyncio.Semaphore(settings.openai_max_concurrency)
        self.token_counter = TokenCounter()
        self.usage_tracker = UsageTracker()

    async def _retry_call(self, fn: Callable[[], Awaitable[Any]]) -> Any:
        retrying = AsyncRetrying(
            stop=stop_after_attempt(self.settings.openai_retry_attempts),
            wait=wait_random_exponential(
                min=self.settings.openai_retry_min_seconds,
                max=self.settings.openai_retry_max_seconds,
            ),
            retry=retry_if_exception_type((RateLimitError, APITimeoutError, TimeoutError)),
            reraise=True,
        )
        async for attempt in retrying:
            with attempt:
                return await fn()
        raise RuntimeError("Retry flow exited unexpectedly")

    def _record_usage(
        self,
        *,
        endpoint: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> None:
        total_tokens = prompt_tokens + completion_tokens
        self.usage_tracker.add_record(
            TokenUsageRecord(
                endpoint=endpoint,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
            )
        )

    @staticmethod
    def _extract_usage(usage: Any) -> tuple[int, int, int]:
        if usage is None:
            return 0, 0, 0
        prompt = int(getattr(usage, "prompt_tokens", 0) or 0)
        completion = int(getattr(usage, "completion_tokens", 0) or 0)
        total = int(getattr(usage, "total_tokens", prompt + completion) or (prompt + completion))
        return prompt, completion, total

    async def chat(self, request: ChatRequest) -> ChatResponse:
        model = request.model or self.settings.openai_model

        async def _call() -> Any:
            return await self.client.chat.completions.create(
                model=model,
                messages=[msg.model_dump() for msg in request.messages],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )

        async with self.semaphore:
            response = await self._retry_call(_call)

        content = response.choices[0].message.content or ""
        prompt_tokens, completion_tokens, total_tokens = self._extract_usage(response.usage)
        if total_tokens == 0:
            prompt_tokens = self.token_counter.count_messages(model, request.messages)
            completion_tokens = self.token_counter.count_text(model, content)
            total_tokens = prompt_tokens + completion_tokens

        self._record_usage(
            endpoint="chat",
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )
        return ChatResponse(
            content=content,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )

    async def embedding(self, request: EmbeddingRequest) -> EmbeddingResponse:
        model = request.model or self.settings.openai_embedding_model

        async def _call() -> Any:
            return await self.client.embeddings.create(
                model=model,
                input=request.input_texts,
            )

        async with self.semaphore:
            response = await self._retry_call(_call)

        vectors = [item.embedding for item in response.data]
        prompt_tokens, _, total_tokens = self._extract_usage(response.usage)
        if total_tokens == 0:
            prompt_tokens = sum(self.token_counter.count_text(model, item) for item in request.input_texts)
            total_tokens = prompt_tokens

        self._record_usage(
            endpoint="embedding",
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=0,
        )
        return EmbeddingResponse(
            vectors=vectors,
            model=model,
            prompt_tokens=prompt_tokens,
            total_tokens=total_tokens,
        )

    async def function_call(self, request: FunctionCallingRequest) -> FunctionCallingResponse:
        model = request.model or self.settings.openai_model

        async def _call() -> Any:
            return await self.client.chat.completions.create(
                model=model,
                messages=[msg.model_dump() for msg in request.messages],
                tools=request.tools,
                tool_choice=request.tool_choice,
            )

        async with self.semaphore:
            response = await self._retry_call(_call)

        message = response.choices[0].message
        tool_name = None
        tool_arguments = None
        if message.tool_calls:
            tool_name = message.tool_calls[0].function.name
            tool_arguments = message.tool_calls[0].function.arguments

        assistant_content = message.content
        prompt_tokens, completion_tokens, total_tokens = self._extract_usage(response.usage)
        if total_tokens == 0:
            prompt_tokens = self.token_counter.count_messages(model, request.messages)
            prompt_tokens += self.token_counter.count_tools(model, request.tools)
            completion_tokens = self.token_counter.count_text(model, assistant_content or "")
            total_tokens = prompt_tokens + completion_tokens

        self._record_usage(
            endpoint="function_call",
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )
        return FunctionCallingResponse(
            assistant_message=assistant_content,
            tool_name=tool_name,
            tool_arguments_json=tool_arguments,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )

    async def stream_chat(self, request: ChatRequest) -> AsyncIterator[str]:
        model = request.model or self.settings.openai_model

        async def _call() -> Any:
            return await self.client.chat.completions.create(
                model=model,
                messages=[msg.model_dump() for msg in request.messages],
                temperature=request.temperature,
                stream=True,
            )

        async with self.semaphore:
            stream = await self._retry_call(_call)

        output: list[str] = []
        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                output.append(delta.content)
                yield delta.content

        combined = "".join(output)
        prompt_tokens = self.token_counter.count_messages(model, request.messages)
        completion_tokens = self.token_counter.count_text(model, combined)
        self._record_usage(
            endpoint="stream_chat",
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

    def usage_summary(self) -> StreamSummary:
        records = self.usage_tracker.records()
        if not records:
            return StreamSummary(model="n/a", prompt_tokens=0, completion_tokens=0, total_tokens=0)

        prompt = sum(item.prompt_tokens for item in records)
        completion = sum(item.completion_tokens for item in records)
        total = sum(item.total_tokens for item in records)
        return StreamSummary(
            model=records[-1].model,
            prompt_tokens=prompt,
            completion_tokens=completion,
            total_tokens=total,
        )
