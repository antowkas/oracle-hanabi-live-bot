import logging

from oraclehlb.ai.base import BaseStrategy
from oraclehlb.core.event_bus import EventBus, OurTurn
from oraclehlb.services.network import NetworkService
from oraclehlb.services.parser import ProtocolParser
from oraclehlb.services.state import GameStateManager

log = logging.getLogger(__name__)


class HanabiBot:
    """Оркестратор для одного экземпляра бота. Собирает сервисы вместе."""

    def __init__(self, username: str, cookie: str, strategy: BaseStrategy):
        self.username = username
        self.strategy = strategy

        # Каждый бот имеет свою собственную, изолированную шину событий.
        event_bus = EventBus()

        # Собираем сервисы, передавая им только то, что им нужно.
        # Глобальные настройки (URL, задержки) они могут взять из импортированного `settings`.
        network_service = NetworkService(cookie=cookie, event_bus=event_bus)
        ProtocolParser(event_bus=event_bus)  # Не требует хранения, работает через подписку
        GameStateManager(
            username=username,
            event_bus=event_bus,
            network_service=network_service
        )

        event_bus.subscribe(OurTurn, self._handle_our_turn)
        self._network = network_service

    async def _handle_our_turn(self, event: OurTurn):
        log.info(f"[{self.username}] It's our turn at table {event.state.table_id}!")
        action_payload = await self.strategy.decide_action(event.state)
        action_payload["tableID"] = event.state.table_id
        await self._network.send_command("action", action_payload)

    async def run(self):
        log.info(f"[{self.username}] Starting bot instance...")
        await self._network.run()
