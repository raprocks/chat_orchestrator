"""State manager that uses MongoDB for persistence.

This module provides a `MongoDBStateManager` that stores and retrieves chat state
for each chat session as a document in a MongoDB collection. This provides a
scalable and persistent storage solution.
"""
from typing import Any, Dict

from pymongo import MongoClient
from pymongo.collection import Collection

from .base import StateManager


class MongoDBStateManager(StateManager):
    """Manages chat state using a MongoDB collection.

    This state manager connects to a MongoDB server to persist chat states,
    making it suitable for production environments where state needs to be
    durable and scalable.

    Attributes:
        client: The MongoDB client instance.
        db: The MongoDB database instance.
        collection: The MongoDB collection used to store states.
    """

    def __init__(
        self,
        uri: str = "mongodb://localhost:27017",
        db_name: str = "chat_orchestrator",
        collection: str = "states",
    ) -> None:
        """Initializes the MongoDBStateManager.

        Args:
            uri: The connection URI for the MongoDB server.
            db_name: The name of the database to use.
            collection: The name of the collection to store states in.
        """
        self.client: MongoClient[Dict[str, Any]] = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection: Collection[Dict[str, Any]] = self.db.get_collection(collection)

    def get_state(self, chat_id: str) -> tuple[str | None, dict[str, Any]]:
        """Retrieves the state from the MongoDB collection.

        Args:
            chat_id: The unique identifier for the chat.

        Returns:
            A tuple containing the state ID and context dictionary, or
            (None, {}) if not found.
        """
        doc = self.collection.find_one({"chat_id": chat_id})
        if doc and "state_id" in doc and "context" in doc:
            return doc["state_id"], doc["context"]
        return None, {}

    def set_state(self, chat_id: str, state_id: str, context: dict[str, Any]) -> None:
        """Saves the state to the MongoDB collection.

        This performs an "upsert" operation, creating a new document if one
        does not exist for the `chat_id`, or updating the existing one.

        Args:
            chat_id: The unique identifier for the chat.
            state_id: The ID of the state to save.
            context: The context dictionary to save.
        """
        self.collection.update_one(
            {"chat_id": chat_id},
            {"$set": {"state_id": state_id, "context": context}},
            upsert=True,
        )

    def delete_state(self, chat_id: str) -> None:
        """Deletes the state document for a chat.

        If no document matches the `chat_id`, this method does nothing.

        Args:
            chat_id: The unique identifier for the chat.
        """
        self.collection.delete_one({"chat_id": chat_id})

    def close(self) -> None:
        """Closes the MongoDB client connection.

        It is good practice to call this method when the application is
        shutting down to release resources.
        """
        self.client.close()
