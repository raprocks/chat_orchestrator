# Chat Orchestrator Framework

A simple, extensible Python framework for building chatbots and conversational state machines with pluggable message senders and state managers.

## About The Project

This framework provides a lightweight yet powerful way to build stateful conversational agents. The core idea is to separate the chat logic from the underlying messaging platforms and state storage. This allows you to write your chat flow once and deploy it across different channels (like console, WhatsApp, etc.) and with different persistence backends (in-memory, file-based, Redis, MongoDB) with minimal changes.

**Key Features:**

*   **Stateful Conversations**: Manage complex, multi-step conversations with ease.
*   **Pluggable Backends**: Swap out message senders and state managers to fit your needs.
*   **Simple by Design**: A minimal API that is easy to learn and use.
*   **Extensible**: Easily create your own senders and state managers.

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

*   Python 3.13+
*   `uv` (or `pip`) for package management

### Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/example/chat-orchestrator.git
    cd chat-orchestrator
    ```

2.  **Create and activate a virtual environment:**
    ```sh
    uv venv .venv
    source .venv/bin/activate
    ```

3.  **Install base dependencies:**
    ```sh
    uv pip install -e .
    ```

4.  **Install optional dependencies for state managers:**
    To use specific state managers, you need to install their dependencies.

    *   **MongoDB:**
        ```sh
        uv pip install -e ".[mongo]"
        ```
    *   **Redis:**
        ```sh
        uv pip install -e ".[redis]"
        ```

## Usage

The `ChatOrchestrator` is the heart of the framework. It ties together a `StateManager` and a `MessageSender` to manage a conversation.

### Core Concepts

*   **ChatOrchestrator**: The main class that drives the conversation.
*   **StateManager**: An object that persists the state of a conversation (e.g., `InMemoryStateManager`, `FileStateManager`).
*   **MessageSender**: An object that sends messages to the user (e.g., `ConsoleMessageSender`, `WhatsAppSender`).
*   **State**: A specific point in the conversation, identified by a unique `state_id`.
*   **Step Function**: A Python function associated with a state. It contains the logic for that step of the conversation.
*   **Context**: A dictionary passed between steps to maintain information about the current conversation.

### Example: A Simple Greeting Bot

Here is a minimal example using the in-memory state manager and console message sender.

```python
from chat_orchestrator.orchestrator import ChatOrchestrator
from chat_orchestrator.senders.console import ConsoleMessageSender
from chat_orchestrator.state_managers.inmemory import InMemoryStateManager

# 1. Initialize the sender and state manager
state_manager = InMemoryStateManager()
sender = ConsoleMessageSender()

# 2. Create the ChatOrchestrator
# The initial state is 'start' by default.
orchestrator = ChatOrchestrator(state_manager, sender)

# 3. Define your step functions
# Each step receives chat_id, user_input, context, and the sender.
# It must return a tuple of (next_state_id, new_context).
@orchestrator.register_step("start")
def start_step(chat_id, user_input, context, sender):
    sender.send_message(chat_id, "Hello! What's your name?")
    return "get_name", {}

@orchestrator.register_step("get_name")
def get_name_step(chat_id, user_input, context, sender):
    sender.send_message(chat_id, f"Nice to meet you, {user_input}!")
    # Loop back to the start
    return "start", {}

# 4. Handle incoming messages
print("Bot is running. Type 'quit' to exit.")
# Trigger the first message
orchestrator.handle_message("console_user", None)
while True:
    message = input("> ")
    if message.lower() == 'quit':
        break
    orchestrator.handle_message("console_user", message)
```

### Using Different Backends

To use a different state manager, simply swap the `StateManager` instance.

**File-based State:**
```python
from chat_orchestrator.state_managers.file import FileStateManager
state_manager = FileStateManager(state_dir="my_chat_states")
```

**Redis State:**
```python
from chat_orchestrator.state_managers.redis import RedisStateManager
state_manager = RedisStateManager(host="localhost", port=6379)
```

**MongoDB State:**
```python
from chat_orchestrator.state_managers.mongodb import MongoDBStateManager
state_manager = MongoDBStateManager(uri="mongodb://localhost:27017")
```

## Extensibility

You can easily extend the framework by creating your own senders and state managers.

### Creating a Custom State Manager

1.  Create a new class that inherits from `StateManager` (in `chat_orchestrator.state_managers.base`).
2.  Implement the following abstract methods:
    *   `get_state(self, chat_id)`
    *   `set_state(self, chat_id, state_id, context)`
    *   `delete_state(self, chat_id)`

### Creating a Custom Message Sender

1.  Create a new class that inherits from `MessageSender` (in `chat_orchestrator.senders.base`).
2.  Implement the `send_message(self, chat_id, text, options)` method.

## Project Structure

```
.
├── chat_orchestrator/
│   ├── __init__.py
│   ├── orchestrator.py        # Core orchestrator logic
│   ├── senders/               # Message sender modules
│   │   ├── base.py            # Abstract base class for senders
│   │   ├── console.py         # Console sender
│   │   └── whatsapp.py        # WhatsApp sender
│   └── state_managers/        # State manager modules
│       ├── base.py            # Abstract base class for state managers
│       ├── file.py            # File-based state manager
│       ├── inmemory.py        # In-memory state manager
│       ├── mongodb.py         # MongoDB state manager
│       └── redis.py           # Redis state manager
├── LICENSE
├── pyproject.toml
└── README.md
```

## License

Distributed under the MIT License. See `LICENSE` for more information.
