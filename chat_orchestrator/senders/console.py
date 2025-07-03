"""
ConsoleMessageSender: Print messages to the console (stdout).

Description:
    A simple sender for debugging and development. Prints messages and options to the terminal.

How to initialize:
    sender = ConsoleMessageSender()

Options:
    Any dictionary. Options are simply printed and not interpreted.
"""

from .base import MessageSender


class ConsoleMessageSender(MessageSender):
    def send_message(self, chat_id: str, text: str, options: dict | None = None):
        print(f"[To {chat_id}] {text}")
        if options:
            print(f"  Options: {options}")
