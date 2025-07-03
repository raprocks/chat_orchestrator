"""
Base class for all message senders.

Description:
    MessageSender is an abstract base class that defines the interface for all message senders. Subclasses must implement the send_message method.

How to initialize:
    Do not instantiate MessageSender directly. Instead, subclass it and implement send_message.

Options:
    The 'options' parameter is sender-specific and should be documented in each subclass. For the base class, it is left as Any.
"""

from abc import ABC, abstractmethod
from typing import Any


class MessageSender(ABC):
    @abstractmethod
    def send_message(self, chat_id: str, text: str, options: Any | None = None) -> None:
        pass
