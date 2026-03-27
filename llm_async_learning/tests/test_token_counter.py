from llm_async_learning.models import ChatMessage, TokenUsageRecord
from llm_async_learning.token_counter import TokenCounter
from llm_async_learning.usage_tracker import UsageTracker


def test_token_counter_count_text_and_messages() -> None:
    counter = TokenCounter()
    messages = [
        ChatMessage(role="system", content="You are concise."),
        ChatMessage(role="user", content="Hello world"),
    ]

    text_tokens = counter.count_text("gpt-4.1-mini", "hello")
    message_tokens = counter.count_messages("gpt-4.1-mini", messages)

    assert text_tokens > 0
    assert message_tokens > text_tokens


def test_usage_tracker_totals() -> None:
    tracker = UsageTracker()
    tracker.add_record(
        TokenUsageRecord(
            endpoint="chat",
            model="gpt-4.1-mini",
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15,
        )
    )
    tracker.add_record(
        TokenUsageRecord(
            endpoint="embedding",
            model="text-embedding-3-small",
            prompt_tokens=7,
            completion_tokens=0,
            total_tokens=7,
        )
    )

    assert tracker.total_tokens() == 22
    assert tracker.totals_by_endpoint() == {"chat": 15, "embedding": 7}
