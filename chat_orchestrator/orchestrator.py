# Chat Orchestrator: core state machine logic
from typing import Any, Callable, Generic, TypeVar, final

from loguru import logger

from .senders.base import MessageSender
from .state_managers.base import StateManager

S = TypeVar("S", bound=MessageSender)


@final
class ChatOrchestrator(Generic[S]):
    message_sender: S
    steps: dict[
        str,
        Callable[[str, Any, dict[str, Any], S], tuple[str, dict[str, Any]]],
    ] = {}
    initial_state_id: str
    unknown_state_message: str

    def __init__(
        self,
        state_manager: StateManager,
        message_sender: S,
        initial_state_id: str = "start",
        unknown_state_message: str = (
            "Unknown state: {state_id}. Resetting to initial state."
        ),
    ) -> None:
        """
        Initialize a ChatOrchestrator instance.

        Args:
            state_manager (StateManager or a subclass): The state manager to use.
            message_sender (MessageSender or a subclass): The message sender to use.
            initial_state_id (str, optional): The initial state ID. Defaults to "start".
        """
        self.state_manager = state_manager
        self.message_sender = message_sender
        self.initial_state_id = initial_state_id
        self.unknown_state_message = unknown_state_message

    def register_step(self, state_id: str):
        def decorator(
            func: Callable[[str, Any, dict[str, Any], S], tuple[str, dict[str, Any]]],
        ) -> Callable[[str, Any, dict[str, Any], S], tuple[str, dict[str, Any]]]:
            self.steps[state_id] = func
            return func

        return decorator

    def handle_message(self, chat_id: str, user_input: Any):
        state_id, context = self.state_manager.get_state(chat_id)
        logger.info(f"State: {state_id}, Context: {context}"[:200])
        if state_id is None:
            state_id = self.initial_state_id
            context = {}
        handler = self.steps.get(state_id)
        logger.info(f"Handler: {handler}")
        if handler is None:
            self.message_sender.send_message(
                chat_id, self.unknown_state_message.format(state_id=state_id)
            )
            state_id = self.initial_state_id
            context = {}
            handler = self.steps.get(state_id)
            if handler is None:
                raise Exception(
                    f"No handler registered for initial state: {self.initial_state_id}"
                )
        next_state_id, next_context = handler(
            chat_id, user_input, context, self.message_sender
        )
        logger.info(f"Next State: {next_state_id}, Next Context: {next_context}"[:200])
        self.state_manager.set_state(chat_id, next_state_id, next_context)
