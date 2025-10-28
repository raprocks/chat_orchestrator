# Chat Orchestrator: core state machine logic
from typing import Any, Callable, Generic, TypeVar, final

from loguru import logger

from .senders.base import MessageSender
from .state_managers.base import StateManager

S = TypeVar("S", bound=MessageSender)


@final
class ChatOrchestrator(Generic[S]):
    """A generic chat orchestrator that manages conversation states.

    This class provides a state machine-like system to manage chat conversations.
    It uses a state manager to persist the conversation state and a message sender
    to communicate with the user. Steps in the conversation are registered as
    callables, each associated with a state ID.

    Attributes:
        message_sender: The message sender instance to use for sending messages.
        steps: A dictionary mapping state IDs to their handler functions.
        initial_state_id: The identifier for the initial state of the conversation.
        unknown_state_message: The message to send when an unknown state is encountered.
        state_manager: The state manager instance for persisting conversation state.
    """

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
        """Initializes a ChatOrchestrator instance.

        Args:
            state_manager: The state manager to use for persisting conversation state.
            message_sender: The message sender to use for sending messages.
            initial_state_id: The identifier for the initial state. Defaults to "start".
            unknown_state_message: A format string for the message to send when an
                unknown state is encountered. It can include `{state_id}` as a
                placeholder. Defaults to "Unknown state: {state_id}. Resetting to
                initial state.".
        """
        self.state_manager = state_manager
        self.message_sender = message_sender
        self.initial_state_id = initial_state_id
        self.unknown_state_message = unknown_state_message

    def register_step(self, state_id: str):
        """Registers a function as a handler for a specific state.

        This method is intended to be used as a decorator. The decorated function
        will be called when the orchestrator is in the specified state and a

        message is received.

        Args:
            state_id: The identifier of the state to register the handler for.

        Returns:
            A decorator that registers the decorated function as a state handler.
        """

        def decorator(
            func: Callable[[str, Any, dict[str, Any], S], tuple[str, dict[str, Any]]],
        ) -> Callable[[str, Any, dict[str, Any], S], tuple[str, dict[str, Any]]]:
            """The actual decorator that registers the function."""
            self.steps[state_id] = func
            return func

        return decorator

    def handle_message(self, chat_id: str, user_input: Any):
        """Handles an incoming message from a user.

        This method retrieves the current state for the given chat ID, finds the
        corresponding handler, and executes it. If no state is found, it starts
        from the initial state. If no handler is found for a state, it sends an
        error message and resets to the initial state. After the handler is
        executed, it updates the state for the chat.

        Args:
            chat_id: The unique identifier for the chat session.
            user_input: The input received from the user.
        """
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
