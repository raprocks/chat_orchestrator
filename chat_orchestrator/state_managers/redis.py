"""
RedisStateManager: Persistent state management using Redis.

Description:
    Stores and retrieves chat state for each chat_id as a JSON string in Redis. Fast and persistent as long as Redis is running.

How to initialize:
    state_manager = RedisStateManager(host="localhost", port=6379, db=0)
    # All parameters are optional and default to a local Redis instance.

State Format:
    Each chat_id key in Redis contains: {"state_id": str, "context": dict}

Methods:
    - get_state(chat_id): Returns (state_id, context) tuple. If not found, returns (None, {}).
    - set_state(chat_id, state_id, context): Saves state for the chat.
    - delete_state(chat_id): Removes the state for the chat.
"""

from .base import StateManager
from typing import Any
import redis
import json


class RedisStateManager(StateManager):
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.client = redis.Redis(host=host, port=port, db=db)

    def get_state(self, chat_id: str) -> tuple[str | None, dict[str, Any]]:
        data = self.client.get(chat_id)
        if data:
            try:
                obj = json.loads(data)  # type: ignore
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
        obj = {"state_id": state_id, "context": context}
        self.client.set(chat_id, json.dumps(obj))

    def delete_state(self, chat_id: str) -> None:
        self.client.delete(chat_id)
