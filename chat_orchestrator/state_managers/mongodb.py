"""
MongoDBStateManager: Persistent state management using MongoDB.

Description:
    Stores and retrieves chat state for each chat_id as a document in a MongoDB collection. Scalable and persistent.

How to initialize:
    state_manager = MongoDBStateManager(
        uri="mongodb://localhost:27017",
        db_name="chat_orchestrator",
        collection="states"
    )
    # All parameters are optional and default to a local MongoDB instance and 'chat_orchestrator.states' collection.

State Format:
    Each document contains: {"chat_id": str, "state_id": str, "context": dict}

Methods:
    - get_state(chat_id): Returns (state_id, context) tuple. If not found, returns (None, {}).
    - set_state(chat_id, state_id, context): Saves state for the chat.
    - delete_state(chat_id): Removes the state for the chat.
"""

from typing import Any, Dict

from pymongo import MongoClient

from .base import StateManager


class MongoDBStateManager(StateManager):
    def __init__(
        self,
        uri: str = "mongodb://localhost:27017",
        db_name: str = "chat_orchestrator",
        collection: str = "states",
    ):
        self.uri = uri
        self.db_name = db_name
        self.collection = collection

    def _get_db(self):
        client = MongoClient[Dict[str, Any]](self.uri)
        db = client[self.db_name]
        return db

    def get_state(self, chat_id: str) -> tuple[str | None, dict[str, Any]]:
        collection = self._get_db()[self.collection]
        doc = collection.find_one({"chat_id": chat_id})
        if doc and "state_id" in doc and "context" in doc:
            return doc["state_id"], doc["context"]
        return None, {}

    def set_state(self, chat_id: str, state_id: str, context: dict[str, Any]) -> None:
        collection = self._get_db()[self.collection]
        collection.update_one(
            {"chat_id": chat_id},
            {"$set": {"state_id": state_id, "context": context}},
            upsert=True,
        )

    def delete_state(self, chat_id: str) -> None:
        collection = self._get_db()[self.collection]
        collection.delete_one({"chat_id": chat_id})
