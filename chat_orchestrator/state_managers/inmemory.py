"""In-memory state manager.

This module provides an `InMemoryStateManager` that stores chat state in a
Python dictionary. This is a volatile storage mechanism, meaning that all state
is lost when the process terminates. It is primarily useful for testing,
development, or applications where state persistence is not required.
"""
from .base import StateManager
from typing import Any


class InMemoryStateManager(StateManager):
    """Manages chat state in a dictionary for the lifetime of the process.

    This state manager is fast and has no external dependencies, but all state
    is lost when the application restarts.

    Attributes:
        _states: A dictionary mapping chat IDs to a tuple of (state_id, context).
    """

    def __init__(self) -> None:
        """Initializes the InMemoryStateManager."""
        self._states: dict[str, tuple[str, dict[str, Any]]] = {}

    def get_state(self, chat_id: str) -> tuple[str | None, dict[str, Any]]:
        """Retrieves the state for a given chat.

        Args:
            chat_id: The unique identifier for the chat.

        Returns:
            A tuple containing the state ID and context dictionary, or
            (None, {}) if not found.
        """
        return self._states.get(chat_id, (None, {}))

    def set_state(self, chat_id: str, state_id: str, context: dict[str, Any]) -> None:
        """Saves the state for a given chat.

        Args:
            chat_id: The unique identifier for the chat.
            state_id: The ID of the state to save.
            context: The context dictionary to save.
        """
        self._states[chat_id] = (state_id, context)

    def delete_state(self, chat_id: str) -> None:
        """Deletes the state for a given chat.

        If the chat ID does not exist, this method does nothing.

        Args:
            chat_id: The unique identifier for the chat.
        """
        self._states.pop(chat_id, None)
