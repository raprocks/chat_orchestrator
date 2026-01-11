import ast
import importlib
import json
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


class SecurityError(OrchestratorError):
    """Raised when the inline code violates security rules."""


@final
class ChatOrchestrator(Generic[S]):
    message_sender: S
    steps: dict[str, StepHandler[S]]
    initial_state_id: str
    unknown_state_message: str

    _BLACKLISTED_NAMES = (
        "os",
        "sys",
        "subprocess",
        "eval",
        "exec",
        "open",
        "__import__",
        "builtins",
    )

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

    def _validate_ast(self, tree: ast.AST) -> None:
        """Validate the AST for security violations."""
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                raise SecurityError("Imports are not allowed in inline code.")
            if isinstance(node, ast.Name) and node.id in self._BLACKLISTED_NAMES:
                raise SecurityError(f"Usage of '{node.id}' is blocked.")
            if isinstance(node, ast.Attribute) and node.attr in self._BLACKLISTED_NAMES:
                # Catch cases like something.os (unlikely without import but good safety)
                raise SecurityError(f"Usage of attribute '{node.attr}' is blocked.")

    def _create_handler_from_code(self, code: str, state_id: str) -> StepHandler[S]:
        """Create a handler function from inline code."""
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise OrchestratorError(
                f"Syntax error in inline code for state '{state_id}': {e}"
            ) from e

        self._validate_ast(tree)

        # Verify it has at least one function definition
        functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
        if len(functions) != 1:
            raise OrchestratorError(
                f"Inline code for '{state_id}' must define exactly one top-level function."
            )

        func_def = functions[0]
        # Verify signature: 4 arguments
        # (self is not passed here, arguments are chat_id, user_input, context, sender)
        if len(func_def.args.args) != 4:
            raise OrchestratorError(f"Handler for '{state_id}' must accept exactly 4 arguments.")

        # Create a restricted namespace
        local_scope: dict[str, Any] = {}
        # We allow standard builtins minus the dangerous ones, but exec with empty __builtins__
        # is safer. However, users need some basics (len, str, dict, etc.).
        # For this requirement, we rely on AST validation to block 'open', '__import__', etc.
        # We pass a copy of safe builtins or just let it use standard builtins and trust AST whitelist/blacklist.
        # Since we use blacklist, we run with standard globals but rely on the validator.

        exec(code, {}, local_scope)

        handler = local_scope[func_def.name]
        return handler

    def register_steps_from_json(self, json_path: str) -> None:
        """
        Register steps from a JSON file.

        The JSON file should be a dictionary where keys are state_ids and values are
        strings representing the fully qualified name of the handler function OR
        the inline function definition.

        Args:
            json_path (str): Path to the JSON file.
        """
        with open(json_path) as f:
            steps_config: dict[str, str] = json.load(f)

        for state_id, handler_def in steps_config.items():
            try:
                # Heuristic: if it looks like a function definition
                if "def " in handler_def:
                    handler = self._create_handler_from_code(handler_def, state_id)
                else:
                    module_name, func_name = handler_def.rsplit(".", 1)
                    module = importlib.import_module(module_name)
                    handler = getattr(module, func_name)

                self.steps[state_id] = handler
            except (ValueError, ImportError, AttributeError, OrchestratorError) as e:
                # Catching OrchestratorError to wrap it with specific context if needed,
                # or just re-raise if it's already descriptive.
                if isinstance(e, OrchestratorError):
                    raise
                raise OrchestratorError(
                    f"Failed to load handler '{handler_def}' for state '{state_id}': {e}"
                ) from e
