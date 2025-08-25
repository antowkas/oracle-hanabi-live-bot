import asyncio
import json
import logging
from typing import Dict, Any, Optional

import websockets
from websockets import ConnectionClosed
from websockets.asyncio.client import ClientConnection

from oraclehlb.config import settings
from oraclehlb.core.event_bus import EventBus, RawMessageReceived

log = logging.getLogger(__name__)


class NetworkService:
    """Отвечает исключительно за WebSocket-соединение и его стабильность."""

    def __init__(self, cookie: str, event_bus: EventBus):
        self._cookie = cookie
        self._bus = event_bus
        self._ws: Optional[ClientConnection] = None

    async def run(self):
        delay = settings.reconnect_delay_base
        while True:
            try:
                log.info(f"Connecting to {settings.ws_url}...")
                additional_headers = {"Cookie": self._cookie}
                async with websockets.connect(settings.ws_url, additional_headers=additional_headers) as ws:
                    self._ws = ws
                    log.info("Connection established.")
                    delay = settings.reconnect_delay_base
                    await self._listen_for_messages()
            except (ConnectionClosed, OSError, websockets.InvalidStatus) as e:
                log.warning(f"Connection lost: {e}. Reconnecting in {delay:.2f}s...")
                await asyncio.sleep(delay)
                delay = min(delay * 2, settings.reconnect_delay_max)
            except asyncio.CancelledError:
                log.info("Network service was cancelled.")
                break
            except Exception:
                log.exception("An unexpected network error occurred. Reconnecting...")
                await asyncio.sleep(delay)

    async def _listen_for_messages(self):
        async for message in self._ws:
            if isinstance(message, str):
                await self._bus.publish(RawMessageReceived(message=message))

    async def send_command(self, command: str, payload: Dict[str, Any]):
        if not self._ws:
            log.error("Cannot send command, WebSocket is not connected.")
            return

        full_message = f"{command} {json.dumps(payload)}"
        await self._ws.send(full_message)
        log.debug(f"Sent command: {command}")
