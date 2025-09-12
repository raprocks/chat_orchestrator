"""Base class for state managers.

This module defines the abstract base class for all state managers. State
managers are responsible for persisting the conversation state for each chat.
"""
from abc import ABC, abstractmethod
from typing import Any


class StateManager(ABC):
    """Abstract base class for a state manager.

    This class defines the interface for getting, setting, and deleting the
    state of a conversation. Subclasses must implement these methods to provide
    a concrete storage mechanism, such as in-memory, file-based, or a database.
    """

    @abstractmethod
    def get_state(self, chat_id: str) -> tuple[str | None, dict[str, Any]]:
        """Retrieves the state for a given chat.

        Args:
            chat_id: The unique identifier for the chat.

        Returns:
            A tuple containing the current state ID and the context dictionary.
            If no state is found for the chat, it should return (None, {}).
        """
        pass

    @abstractmethod
    def set_state(self, chat_id: str, state_id: str, context: dict[str, Any]) -> None:
        """Saves the state for a given chat.

        Args:
            chat_id: The unique identifier for the chat.
            state_id: The ID of the state to save.
            context: A dictionary containing the context for the state.
        """
        pass

    @abstractmethod
    def delete_state(self, chat_id: str) -> None:
        """Deletes the state for a given chat.

        Args:
            chat_id: The unique identifier for the chat.
        """
        pass
