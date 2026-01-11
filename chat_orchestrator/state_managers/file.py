"""
FileStateManager: Persistent state management using JSON files.

Description:
    Stores and retrieves chat state for each chat_id in a separate JSON file on disk. Each file contains a dict with 'state_id' and 'context'.

How to initialize:
    state_manager = FileStateManager(state_dir="chat_states")
    # 'state_dir' is the directory where state files are stored (default: 'chat_states').

State Format:
    Each file contains: {"state_id": str, "context": dict}

Methods:
    - get_state(chat_id): Returns (state_id, context) tuple. If not found, returns (None, {}).
    - set_state(chat_id, state_id, context): Saves state for the chat.
    - delete_state(chat_id): Removes the state file for the chat.
"""

import json
import os
from typing import Any

from .base import StateManager


class FileStateManager(StateManager):
    def __init__(self, state_dir: str = "chat_states") -> None:
        self.state_dir = state_dir
        if not os.path.exists(self.state_dir):
            os.makedirs(self.state_dir)

    def _get_file_path(self, chat_id: str) -> str:
        return os.path.join(self.state_dir, f"{chat_id}.json")

    def get_state(self, chat_id: str) -> tuple[str | None, dict[str, Any]]:
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
        file_path = self._get_file_path(chat_id)
        data = {"state_id": state_id, "context": context}
        with open(file_path, "w") as f:
            json.dump(data, f)

    def delete_state(self, chat_id: str) -> None:
        file_path = self._get_file_path(chat_id)
        if os.path.exists(file_path):
            os.remove(file_path)
