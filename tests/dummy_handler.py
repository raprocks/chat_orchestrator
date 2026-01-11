from typing import Any

from chat_orchestrator.senders.base import MessageSender


def dummy_start_handler(
    chat_id: str, user_input: Any, context: dict[str, Any], sender: MessageSender
) -> tuple[str, dict[str, Any]]:
    return "process", {"data": "dummy"}
