from __future__ import annotations

from collections.abc import Iterable

from .models import TokenUsageRecord


class UsageTracker:
    def __init__(self) -> None:
        self._records: list[TokenUsageRecord] = []

    def add_record(self, record: TokenUsageRecord) -> None:
        self._records.append(record)

    def records(self) -> list[TokenUsageRecord]:
        return list(self._records)

    def total_tokens(self) -> int:
        return sum(item.total_tokens for item in self._records)

    def totals_by_endpoint(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for record in self._records:
            result[record.endpoint] = result.get(record.endpoint, 0) + record.total_tokens
        return result

    def merge(self, records: Iterable[TokenUsageRecord]) -> None:
        self._records.extend(records)
