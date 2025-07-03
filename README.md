# Chat Orchestrator Framework

A simple, extensible Python framework for building chatbots and conversational state machines with pluggable message senders and state managers.

## Features

-   Modular design: add your own message senders and state managers
-   Built-in support for in-memory, file, MongoDB, and Redis state management
-   Easy to extend for new backends or messaging platforms

## Installation

1. Clone the repository
2. Create a virtual environment and install dependencies:

```sh
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt  # or use `uv pip install .` if you have a pyproject.toml
```

## Usage Example

Below is a minimal example using the in-memory state manager and console message sender.

```python
from chat_orchestrator.orchestrator import ChatOrchestrator
from chat_orchestrator.senders.console import ConsoleMessageSender
from chat_orchestrator.state_managers.inmemory import InMemoryStateManager

# Define a simple step function
# Each step receives (chat_id, user_input, context, message_sender)
def start_step(chat_id, user_input, context, sender):
    sender.send_message(chat_id, "Hello! What's your name?")
    return "get_name", {}

def get_name_step(chat_id, user_input, context, sender):
    sender.send_message(chat_id, f"Nice to meet you, {user_input}!")
    return "start", {}

# Set up orchestrator
state_manager = InMemoryStateManager()
sender = ConsoleMessageSender()
orch = ChatOrchestrator(state_manager, sender, initial_state_id="start")

orch.register_step("start")(start_step)
orch.register_step("get_name")(get_name_step)

# Simulate a chat
orch.handle_message("user1", None)      # triggers start_step
orch.handle_message("user1", "Alice")   # triggers get_name_step
```

## Using the File State Manager

To persist state to disk, use the file-based state manager:

```python
from chat_orchestrator.state_managers.file import FileStateManager
state_manager = FileStateManager()
# ...rest is the same as above
```

## Adding More State Managers

-   MongoDB: `from chat_orchestrator.state_managers.mongodb import MongoDBStateManager`
-   Redis: `from chat_orchestrator.state_managers.redis import RedisStateManager`

## Extending

Add your own modules to `senders/` or `state_managers/` for new backends.

---

For more, see the code and docstrings in each module.
