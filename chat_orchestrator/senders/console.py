"""Message sender for printing to the console.

This module provides a message sender that prints messages to standard output,
which is useful for debugging and development purposes.
"""
from typing import Any
from .base import MessageSender


class ConsoleMessageSender(MessageSender):
    """A message sender that prints messages to the console.

    This sender is primarily used for testing and development. It outputs the
    message content and any provided options to the standard output.
    """

    def send_message(self, chat_id: str, text: str, options: Any | None = None) -> None:
        """Prints a message to the console.

        Args:
            chat_id: The identifier of the chat, which will be included in the
                output.
            text: The text content of the message to be printed.
            options: An optional dictionary of options. If provided, these
                options will be printed to the console as well.
        """
        print(f"[To {chat_id}] {text}")
        if options:
            print(f"  Options: {options}")
