"""
StateManager: Abstract base class for chat state management.

Description:
    Defines the interface for all state manager implementations. Subclasses must implement methods to get, set, and delete state for a chat.

How to initialize:
    Do not instantiate StateManager directly. Use a subclass (e.g., FileStateManager, InMemoryStateManager, RedisStateManager, MongoDBStateManager).

Methods:
    - get_state(chat_id): Returns (state_id, context) tuple. If not found, returns (None, {}).
    - set_state(chat_id, state_id, context): Saves state for the chat.
    - delete_state(chat_id): Removes the state for the chat.
"""

from abc import ABC, abstractmethod
from typing import Any


class StateManager(ABC):
    @abstractmethod
    def get_state(self, chat_id: str) -> tuple[str | None, dict[str, Any]]:
        pass

    @abstractmethod
    def set_state(self, chat_id: str, state_id: str, context: dict[str, Any]) -> None:
        pass

    @abstractmethod
    def delete_state(self, chat_id: str) -> None:
        pass
