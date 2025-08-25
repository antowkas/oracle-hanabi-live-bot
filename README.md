# 🚧 WIP 🚧
This project is in an active state of development (WIP). 

It is not ready for production use. The code, configuration, and documentation are subject to frequent changes. Some features are not yet implemented, and bugs may be present.

Please use this project for informational and testing purposes only.

#  Oracle Hanabi Live Bot WIP!

### Description
**Oracle** is an intelligent bot for playing Hanabi on the **hanab.live** platform. Unlike simpler bots that rely on basic heuristics, this project is built with a modular architecture that allows for the easy integration of complex, "smart" strategies. The goal is to create a bot that can serve as a reliable and intelligent partner for automated gameplay.

### Features
* **Modular Architecture**: The project is split into logical components (services, strategies, managers) to simplify development and testing.
* **Flexible Configuration**: It supports running multiple bots simultaneously, each with a different strategy. Configuration is loaded from `config.toml` and `.env` files.
* **Robust Connection**: A built-in automatic reconnection mechanism for the WebSocket server ensures stable operation.
* **Dynamic Strategy Loading**: New strategies can be added as separate files, and the bot will automatically detect and load them without requiring changes to the core code.
* **Event-Driven Model**: An **event bus** (`EventBus`) allows components to communicate with each other without needing to know about their internal implementations, making the system highly flexible and scalable. 

---
### Installation and Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/antowkas/oracle-hanabi-live-bot.git
    cd oracle-hanabi-live-bot
    ```

2.  **Install dependencies**:
    ```bash
    pip install -e .
    ```

3.  **Configure your bots**:

    Create a `config.toml` file in the root directory and specify the bot parameters. Each bot requires a `username` and a `strategy`.

    *Example `config.toml`:*
    ```toml
    [[bots]]
    username = "OracleBot1"
    strategy = "SimpleStrategy"

    [[bots]]
    username = "OracleBot2"
    strategy = "MyCustomStrategy"
    ```

    Create a `.env` file to securely store passwords. Passwords are dynamically loaded using the format `username_password` (in lowercase).

    *Example `.env`:*
    ```env
    oraclebot1_password=my_secret_password1
    oraclebot2_password=my_secret_password2
    ```

4.  **Run the bot**:
    ```bash
    python -m oraclehlb.main
    ```

---
### Project Structure

```
oraclehlb/
├── ai/                      # AI strategy modules
│   ├── simplestrategy.py    # A basic, functional strategy
│   ├── base.py              # The abstract base class for strategies
│   └── ...                  # New strategies can be added here
│
├── core/                    # Core logic and components
│   ├── bot.py               # Orchestrator for a single bot instance
│   ├── bot_factory.py       # Factory for creating bot instances
│   ├── bot_manager.py       # Manager for multiple bots
│   ├── event_bus.py         # Event bus
│   └── strategy_loader.py   # Dynamic strategy loader
│
├── services/                # Components for specific tasks
│   ├── auth.py              # Authentication for hanab.live
│   ├── network.py           # WebSocket communication
│   ├── parser.py            # Parsing server messages
│   └── state.py             # Game state management
│
├── config.py                # Project configuration (Pydantic)
├── models.py                # Data models (Pydantic)
└── main.py                  # Application entry point
```

---
### Creating a Custom Strategy

1.  Create a new file in the `oraclehlb/ai/` directory, for example, `myawesomestrategy.py`.
2.  Create a class that inherits from `BaseStrategy` and implements the `decide_action` method:
    ```python
    # oraclehlb/ai/myawesomestrategy.py
    from oraclehlb.ai.base import BaseStrategy
    from oraclehlb.models import GameState

    class MyAwesomeStrategy(BaseStrategy):
        async def decide_action(self, state: GameState):
            # Your decision-making logic goes here
            ...
            return {"type": "play", "orderID": 123}
    ```
3.  Add your new strategy to the `config.toml` file:
    ```toml
    [[bots]]
    username = "MyAwesomeBot"
    strategy = "MyAwesomeStrategy"
    ```
The project will automatically load your new strategy when you run it.