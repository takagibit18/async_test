from __future__ import annotations

import json
from typing import Any

import tiktoken

from .models import ChatMessage


class TokenCounter:
    def __init__(self, default_encoding: str = "cl100k_base") -> None:
        self.default_encoding = default_encoding

    def _get_encoding(self, model: str) -> tiktoken.Encoding:
        try:
            return tiktoken.encoding_for_model(model)
        except KeyError:
            return tiktoken.get_encoding(self.default_encoding)

    def count_text(self, model: str, text: str) -> int:
        encoding = self._get_encoding(model)
        return len(encoding.encode(text))

    def count_messages(self, model: str, messages: list[ChatMessage]) -> int:
        # Approximate rule for chat tokenization, enough for learning and budgeting.
        base_per_message = 3
        base_reply = 3
        total = base_reply
        for msg in messages:
            total += base_per_message
            total += self.count_text(model, msg.role)
            total += self.count_text(model, msg.content)
        return total

    def count_tools(self, model: str, tools: list[dict[str, Any]]) -> int:
        tool_json = json.dumps(tools, ensure_ascii=True, separators=(",", ":"))
        return self.count_text(model, tool_json)
