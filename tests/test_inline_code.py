# pyright: reportPrivateUsage=false

import unittest
from pathlib import Path
from unittest.mock import Mock

from chat_orchestrator.orchestrator import ChatOrchestrator, OrchestratorError, SecurityError
from chat_orchestrator.senders.base import MessageSender
from chat_orchestrator.state_managers.base import StateManager


class TestInlineCodeRegistration(unittest.TestCase):
    def setUp(self):
        self.state_manager = Mock(spec=StateManager)
        self.sender = Mock(spec=MessageSender)
        self.orchestrator = ChatOrchestrator(
            state_manager=self.state_manager, message_sender=self.sender
        )

    def test_valid_inline_handler(self):
        code = """
def valid_handler(chat_id, user_input, context, sender):
    return "next_state", {"data": "processed"}
"""
        handler = self.orchestrator._create_handler_from_code(code, "test_state")
        self.assertTrue(callable(handler))

        state, context = handler("1", "input", {}, self.sender)
        self.assertEqual(state, "next_state")
        self.assertEqual(context, {"data": "processed"})

    def test_security_imports_blocked(self):
        code = """
import os
def handler(chat_id, user_input, context, sender):
    return "next", {}
"""
        with self.assertRaises(SecurityError):
            _ = self.orchestrator._create_handler_from_code(code, "test_state")

    def test_security_from_imports_blocked(self):
        code = """
from os import system
def handler(chat_id, user_input, context, sender):
    return "next", {}
"""
        with self.assertRaises(SecurityError):
            _ = self.orchestrator._create_handler_from_code(code, "test_state")

    def test_security_blacklist_usage(self):
        code = """
def handler(chat_id, user_input, context, sender):
    os.system("ls")
    return "next", {}
"""
        # Even without import, usage of 'os' should be caught by blacklist check
        with self.assertRaises(SecurityError):
            _ = self.orchestrator._create_handler_from_code(code, "test_state")

    def test_security_eval_blocked(self):
        code = """
def handler(chat_id, user_input, context, sender):
    eval("1 + 1")
    return "next", {}
"""
        with self.assertRaises(SecurityError):
            _ = self.orchestrator._create_handler_from_code(code, "test_state")

    def test_invalid_signature_args_count(self):
        code = """
def handler(chat_id, user_input):
    return "next", {}
"""
        with self.assertRaises(OrchestratorError) as cm:
            _ = self.orchestrator._create_handler_from_code(code, "test_state")
        self.assertIn("exactly 4 arguments", str(cm.exception))

    def test_multiple_functions_error(self):
        code = """
def helper():
    pass

def handler(chat_id, user_input, context, sender):
    return "next", {}
"""
        with self.assertRaises(OrchestratorError) as cm:
            _ = self.orchestrator._create_handler_from_code(code, "test_state")
        self.assertIn("exactly one top-level function", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
