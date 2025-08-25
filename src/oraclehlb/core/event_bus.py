import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Any, Type, List, Callable, Awaitable

from oraclehlb.models import GameState

log = logging.getLogger(__name__)


class Event:
    """Базовый класс для всех событий."""
    pass


@dataclass
class RawMessageReceived(Event):
    message: str


@dataclass
class CommandReceived(Event):
    command: str
    payload: Dict[str, Any]


@dataclass
class OurTurn(Event):
    state: GameState


class EventBus:
    """Асинхронная шина событий."""

    def __init__(self):
        self._listeners: Dict[Type[Event], List[Callable[[Event], Awaitable[None]]]] = defaultdict(list)

    def subscribe[T](self, event_type: Type[T], listener: Callable[[T], Awaitable[None]]):
        self._listeners[event_type].append(listener)
        log.debug(f"Listener {listener.__name__} subscribed to {event_type.__name__}")

    async def publish(self, event: Event):
        event_type = type(event)
        log.debug(f"Publishing event {event_type.__name__}")
        listeners = self._listeners.get(event_type, [])

        # Python 3.11+ TaskGroup - для структурированного параллелизма
        try:
            async with asyncio.TaskGroup() as tg:
                for listener in listeners:
                    tg.create_task(listener(event))
        except* Exception as eg:
            # Логируем все исключения из группы
            for error in eg.exceptions:
                log.exception("Exception in event handler", exc_info=error)
