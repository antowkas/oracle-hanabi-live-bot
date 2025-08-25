import logging
from typing import Dict, Any, Callable, Awaitable

from oraclehlb.core.event_bus import EventBus, CommandReceived, OurTurn
from oraclehlb.core.global_bus import global_event_bus, GlobalPingEvent
from oraclehlb.models import GameState
from oraclehlb.services.network import NetworkService

log = logging.getLogger(__name__)


class GameStateManager:
    """Управляет состоянием игр, реагируя на команды от сервера."""

    def __init__(self, username: str, event_bus: EventBus, network_service: NetworkService):
        self.username = username
        self.games: Dict[int, GameState] = {}

        self._bus = event_bus
        self._network = network_service

        self._handlers: Dict[str, Callable[[Dict], Awaitable[None]]] = {
            "welcome": self._handle_welcome,
            "warning": self._handle_warning,
            "error": self._handle_error,
            "chat": self._handle_chat,
            "table": self._handle_table,
            "tableList": self._handle_table_list,
            "tableGone": self._handle_table_gone,
            "tableStart": self._handle_table_start,

            "init": self._handle_init,
            "gameAction": self._handle_game_action,
            "gameActionList": self._handle_game_action_list,
            "databaseID": self._handle_database_id,
        }

        self._bus.subscribe(CommandReceived, self._dispatch_command)

        global_event_bus.subscribe(GlobalPingEvent, self._handle_global_ping)

    async def _dispatch_command(self, event: CommandReceived):
        """Диспетчер, который вызывает нужный обработчик команды."""
        handler = self._handlers.get(event.command, self._handle_unknown)
        await handler(event.payload)

    async def _handle_welcome(self, payload: Dict[str, Any]):
        server_username = payload.get("username")
        if self.username != server_username:
            log.error(f"Logged in as '{server_username}', but expected '{self.username}'.")
        log.info(f"[{self.username}] Welcome to the server!")

    async def _handle_warning(self, payload: Dict[str, Any]):
        pass

    async def _handle_error(self, payload: Dict[str, Any]):
        pass

    async def _handle_chat(self, payload: Dict[str, Any]):
        # {'msg': 'hello!', 'who': 'antowkas', 'discord': False,
        # 'server': False, 'datetime': '2025-08-25T11:26:13.102623235Z',
        # 'room': '', 'recipient': 'oraclehlb1'}
        if (
                payload["recipient"] != self.username and
                (
                        payload["room"] == "" or
                        not payload["msg"].startswith("/")
                )
        ):
            return

        msg = payload["msg"].split(" ")
        match msg:
            case ("ping", *_):
                await global_event_bus.publish(GlobalPingEvent(recipient=payload["who"]))
                # await self._network.send_command(
                #     "chatPM",
                #     {
                #         "msg": "pong",
                #
                #         "recipient": payload["who"],
                #         "room": "",
                #     },
                # )
            case _:
                pass

    async def _handle_global_ping(self, event: GlobalPingEvent):
        await self._network.send_command(
            "chatPM",
            {
                "msg": "pong",
                "recipient": event.recipient,
                "room": "",
            },
        )

    async def _handle_table(self, payload: Dict[str, Any]):
        pass

    async def _handle_table_list(self, payload: Dict[str, Any]):
        pass

    async def _handle_table_gone(self, payload: Dict[str, Any]):
        pass

    async def _handle_table_start(self, payload: Dict[str, Any]):
        pass

    async def _handle_game_action(self, payload: Dict[str, Any]):
        table_id = payload["tableID"]
        state = self.games.get(table_id)
        if not state:
            return

        # Ниже просто затычка
        action = payload.get("action", {})
        if action.get("type") == "turn":
            state.current_player_index = action["currentPlayerIndex"]
            if state.current_player_index == state.our_player_index:
                await self._bus.publish(OurTurn(state=state))

    async def _handle_init(self, payload: Dict[str, Any]):
        table_id = payload["tableID"]
        state = GameState(
            table_id=table_id,
            player_names=payload["playerNames"],
            our_player_index=payload["ourPlayerIndex"]
        )
        self.games[table_id] = state
        log.info(f"Game initialized for table {table_id}")
        await self._network.send_command("getGameInfo2", {"tableID": table_id})

    async def _handle_game_action_list(self, payload: Dict[str, Any]):
        pass

    async def _handle_database_id(self, payload: Dict[str, Any]):
        pass

    async def _handle_unknown(self, payload: Dict[str, Any]):
        pass  # Игнорируем неизвестные команды
