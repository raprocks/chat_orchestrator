# Chat Orchestrator: core state machine logic
from collections.abc import Callable
from typing import Any, Generic, TypeVar, final

from loguru import logger

from .senders.base import MessageSender
from .state_managers.base import StateManager

S = TypeVar("S", bound=MessageSender)

# Type alias for the step handler function
StepHandler = Callable[[str, Any, dict[str, Any], S], tuple[str, dict[str, Any]]]


class OrchestratorError(Exception):
    """Base exception for Chat Orchestrator errors."""


class InitialStateNotFoundError(OrchestratorError):
    """Raised when the initial state handler is not found."""


@final
class ChatOrchestrator(Generic[S]):
    message_sender: S
    steps: dict[str, StepHandler[S]]
    initial_state_id: str
    unknown_state_message: str

    def __init__(
        self,
        state_manager: StateManager,
        message_sender: S,
        initial_state_id: str = "start",
        unknown_state_message: str = "Unknown state: {state_id}. Resetting to initial state.",
    ) -> None:
        """
        Initialize a ChatOrchestrator instance.

        Args:
            state_manager (StateManager or a subclass): The state manager to use.
            message_sender (MessageSender or a subclass): The message sender to use.
            initial_state_id (str, optional): The initial state ID. Defaults to "start".
            unknown_state_message (str, optional): Message to send when state is unknown.
        """
        self.state_manager = state_manager
        self.message_sender = message_sender
        self.initial_state_id = initial_state_id
        self.unknown_state_message = unknown_state_message
        self.steps = {}  # Initialize steps per instance

    def register_step(self, state_id: str) -> Callable[[StepHandler[S]], StepHandler[S]]:
        def decorator(func: StepHandler[S]) -> StepHandler[S]:
            self.steps[state_id] = func
            return func

        return decorator

    def _get_handler(self, state_id: str) -> StepHandler[S] | None:
        return self.steps.get(state_id)

    def handle_message(self, chat_id: str, user_input: Any) -> None:
        state_id, context = self.state_manager.get_state(chat_id)
        logger.debug(f"State: {state_id}, Context: {str(context)[:200]}")

        if state_id is None:
            state_id = self.initial_state_id
            context = {}

        handler = self._get_handler(state_id)
        logger.debug(f"Handler: {handler}")

        if handler is None:
            self.message_sender.send_message(
                chat_id, self.unknown_state_message.format(state_id=state_id)
            )
            # Reset to initial state
            state_id = self.initial_state_id
            context = {}
            handler = self._get_handler(state_id)

            if handler is None:
                raise InitialStateNotFoundError(
                    f"No handler registered for initial state: {self.initial_state_id}"
                )

        next_state_id, next_context = handler(chat_id, user_input, context, self.message_sender)
        logger.debug(f"Next State: {next_state_id}, Next Context: {str(next_context)[:200]}")
        self.state_manager.set_state(chat_id, next_state_id, next_context)
