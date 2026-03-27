from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1)
    model: str | None = None
    temperature: float = Field(default=0.2, ge=0, le=2)
    max_tokens: int | None = Field(default=None, ge=1)


class ChatResponse(BaseModel):
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class EmbeddingRequest(BaseModel):
    input_texts: list[str] = Field(min_length=1)
    model: str | None = None

    @field_validator("input_texts")
    @classmethod
    def validate_input_texts(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            raise ValueError("Embedding input_texts cannot contain empty strings")
        return value


class EmbeddingResponse(BaseModel):
    vectors: list[list[float]]
    model: str
    prompt_tokens: int
    total_tokens: int


class FunctionCallingRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1)
    tools: list[dict[str, Any]] = Field(min_length=1)
    tool_choice: str | dict[str, Any] = "auto"
    model: str | None = None


class FunctionCallingResponse(BaseModel):
    assistant_message: str | None = None
    tool_name: str | None = None
    tool_arguments_json: str | None = None
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class TokenUsageRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    endpoint: Literal["chat", "embedding", "function_call", "stream_chat"]
    model: str
    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)
    total_tokens: int = Field(ge=0)


class StreamChunk(BaseModel):
    content: str


class StreamSummary(BaseModel):
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
