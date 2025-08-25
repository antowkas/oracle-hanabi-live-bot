from dataclasses import dataclass

from oraclehlb.core.event_bus import EventBus, Event

# Я сделал это просто по фану
global_event_bus = EventBus()


@dataclass
class GlobalPingEvent(Event):
    """Событие для пинга, отправленное от одного бота всем остальным."""
    recipient: str
