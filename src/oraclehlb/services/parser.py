import json
import logging

from oraclehlb.core.event_bus import RawMessageReceived, CommandReceived, EventBus

log = logging.getLogger(__name__)


class ProtocolParser:
    """Слушает сырые сообщения и парсит их в структурированные команды."""

    def __init__(self, event_bus: EventBus):
        self._bus = event_bus
        self._bus.subscribe(RawMessageReceived, self.handle_raw_message)

    async def handle_raw_message(self, event: RawMessageReceived):
        try:
            command, payload_str = event.message.split(" ", 1)
            payload = json.loads(payload_str)
            await self._bus.publish(CommandReceived(command=command, payload=payload))
        except (ValueError, json.JSONDecodeError):
            log.error(f"Failed to parse message: '{event.message}'")
