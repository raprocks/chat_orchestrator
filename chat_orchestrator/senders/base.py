"""Base class for message senders.

This module defines the abstract base class for all message senders.
"""
from abc import ABC, abstractmethod
from typing import Any


class MessageSender(ABC):
    """Abstract base class for a message sender.

    This class defines the interface for sending messages to a chat. Subclasses
    must implement the `send_message` method.
    """

    @abstractmethod
    def send_message(self, chat_id: str, text: str, options: Any | None = None) -> None:
        """Sends a message to the specified chat.

        This method must be implemented by subclasses to handle the actual
        message sending logic.

        Args:
            chat_id: The unique identifier of the chat to send the message to.
            text: The text content of the message.
            options: A dictionary of sender-specific options. The structure and
                content of this dictionary will vary depending on the specific
                implementation. It can be used to pass extra parameters like
                message formatting options, attachments, etc.
        """
        pass
