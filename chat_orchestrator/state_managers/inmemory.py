"""
InMemoryStateManager: Volatile state management in memory.

Description:
    Stores chat state in a Python dictionary for the lifetime of the process. Fast, but state is lost on restart.

How to initialize:
    state_manager = InMemoryStateManager()

State Format:
    Each chat_id maps to a tuple: (state_id, context)

Methods:
    - get_state(chat_id): Returns (state_id, context) tuple. If not found, returns (None, {}).
    - set_state(chat_id, state_id, context): Saves state for the chat.
    - delete_state(chat_id): Removes the state for the chat.
"""

from .base import StateManager
from typing import Any


class InMemoryStateManager(StateManager):
    def __init__(self):
        self._states: dict[str, tuple[str, dict[str, Any]]] = {}

    def get_state(self, chat_id: str) -> tuple[str | None, dict[str, Any]]:
        return self._states.get(chat_id, (None, {}))

    def set_state(self, chat_id: str, state_id: str, context: dict[str, Any]) -> None:
        self._states[chat_id] = (state_id, context)

    def delete_state(self, chat_id: str) -> None:
        self._states.pop(chat_id, None)
