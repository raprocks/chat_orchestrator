import unittest
from pathlib import Path
from unittest.mock import Mock

from chat_orchestrator.orchestrator import ChatOrchestrator
from chat_orchestrator.senders.base import MessageSender
from chat_orchestrator.state_managers.base import StateManager


class TestJSONRegistration(unittest.TestCase):
    def setUp(self):
        self.state_manager = Mock(spec=StateManager)
        self.sender = Mock(spec=MessageSender)
        self.orchestrator = ChatOrchestrator(
            state_manager=self.state_manager, message_sender=self.sender
        )

    def test_register_steps_from_json(self):
        # Path to the steps.json file
        json_path = Path(__file__).parent / "steps.json"

        self.orchestrator.register_steps_from_json(str(json_path))

        # Verify that the step is registered
        self.assertIn("start", self.orchestrator.steps)
        handler = self.orchestrator.steps["start"]
        self.assertTrue(callable(handler))

        # Check if it resolves to the correct function
        from tests.dummy_handler import dummy_start_handler

        self.assertEqual(handler, dummy_start_handler)

    def test_execution_of_registered_step(self):
        json_path = Path(__file__).parent / "steps.json"
        self.orchestrator.register_steps_from_json(str(json_path))

        # Mock state manager to return "start" state
        self.state_manager.get_state.return_value = ("start", {})

        # Execute handler
        self.orchestrator.handle_message("chat_123", "hello")

        # Verify state transition
        self.state_manager.set_state.assert_called_with("chat_123", "process", {"data": "dummy"})


if __name__ == "__main__":
    unittest.main()
