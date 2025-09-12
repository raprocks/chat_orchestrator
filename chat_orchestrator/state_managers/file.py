"""State manager that uses JSON files for persistence.

This module provides a `FileStateManager` that stores and retrieves chat state
for each chat session in a separate JSON file on disk. Each file contains a
dictionary with 'state_id' and 'context'.
"""
import json
import os
from .base import StateManager
from typing import Any


class FileStateManager(StateManager):
    """Manages chat state using local JSON files.

    This state manager persists the state of each chat session in a dedicated
    JSON file within a specified directory. This approach is simple and does
    not require any external database.

    Attributes:
        state_dir: The directory where the state files are stored.
    """

    def __init__(self, state_dir: str = "chat_states") -> None:
        """Initializes the FileStateManager.

        Args:
            state_dir: The directory to store the chat state files. If the
                directory does not exist, it will be created. Defaults to
                "chat_states".
        """
        self.state_dir = state_dir
        if not os.path.exists(self.state_dir):
            os.makedirs(self.state_dir)

    def _get_file_path(self, chat_id: str) -> str:
        """Constructs the file path for a given chat ID.

        Args:
            chat_id: The unique identifier for the chat.

        Returns:
            The full path to the JSON file for the chat.
        """
        return os.path.join(self.state_dir, f"{chat_id}.json")

    def get_state(self, chat_id: str) -> tuple[str | None, dict[str, Any]]:
        """Retrieves the state from a JSON file.

        If the file does not exist or is corrupted, it returns a default
        state of (None, {}).

        Args:
            chat_id: The unique identifier for the chat.

        Returns:
            A tuple containing the state ID and context dictionary, or
            (None, {}) if not found.
        """
        file_path = self._get_file_path(chat_id)
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    data: dict[str, Any] | Any = json.load(f)
                    if (
                        isinstance(data, dict)
                        and "state_id" in data
                        and "context" in data
                        and isinstance(data["context"], dict)
                    ):
                        return data["state_id"], data["context"]
            except Exception:
                pass
        return None, {}

    def set_state(self, chat_id: str, state_id: str, context: dict[str, Any]) -> None:
        """Saves the state to a JSON file.

        This will create or overwrite the file for the given chat ID.

        Args:
            chat_id: The unique identifier for the chat.
            state_id: The ID of the state to save.
            context: The context dictionary to save.
        """
        file_path = self._get_file_path(chat_id)
        data = {"state_id": state_id, "context": context}
        with open(file_path, "w") as f:
            json.dump(data, f)

    def delete_state(self, chat_id: str) -> None:
        """Deletes the state file for a chat.

        If the file does not exist, this method does nothing.

        Args:
            chat_id: The unique identifier for the chat.
        """
        file_path = self._get_file_path(chat_id)
        if os.path.exists(file_path):
            os.remove(file_path)
