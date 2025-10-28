"""State manager that uses Redis for persistence.

This module provides a `RedisStateManager` that stores and retrieves chat state
for each chat session as a JSON string in Redis. This provides a fast and
persistent storage solution.
"""
import json
from typing import Any

import redis

from .base import StateManager


class RedisStateManager(StateManager):
    """Manages chat state using a Redis database.

    This state manager connects to a Redis server to persist chat states. State
    for each chat is stored as a JSON string under a key corresponding to the
    chat ID.

    Attributes:
        client: The Redis client instance.
    """

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0) -> None:
        """Initializes the RedisStateManager.

        Args:
            host: The hostname of the Redis server.
            port: The port of the Redis server.
            db: The Redis database number.
        """
        self.client = redis.Redis(host=host, port=port, db=db)

    def get_state(self, chat_id: str) -> tuple[str | None, dict[str, Any]]:
        """Retrieves the state from the Redis database.

        The state is retrieved as a JSON string and decoded. If the key does
        not exist or the data is corrupted, it returns a default state of
        (None, {}).

        Args:
            chat_id: The unique identifier for the chat, used as the Redis key.

        Returns:
            A tuple containing the state ID and context dictionary, or
            (None, {}) if not found.
        """
        data = self.client.get(chat_id)
        if data:
            try:
                obj = json.loads(data)
                if (
                    isinstance(obj, dict)
                    and "state_id" in obj
                    and "context" in obj
                    and isinstance(obj["context"], dict)
                ):
                    return obj["state_id"], obj["context"]
            except Exception:
                pass
        return None, {}

    def set_state(self, chat_id: str, state_id: str, context: dict[str, Any]) -> None:
        """Saves the state to the Redis database.

        The state is stored as a JSON string. This will create or overwrite
        the key for the given chat ID.

        Args:
            chat_id: The unique identifier for the chat, used as the Redis key.
            state_id: The ID of the state to save.
            context: The context dictionary to save.
        """
        obj = {"state_id": state_id, "context": context}
        self.client.set(chat_id, json.dumps(obj))

    def delete_state(self, chat_id: str) -> None:
        """Deletes the state for a chat from the Redis database.

        If the key does not exist, this method does nothing.

        Args:
            chat_id: The unique identifier for the chat, used as the Redis key.
        """
        self.client.delete(chat_id)
