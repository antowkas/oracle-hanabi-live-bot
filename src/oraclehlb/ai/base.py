from abc import ABC, abstractmethod
from typing import Dict, Any

from oraclehlb.models import GameState


class BaseStrategy(ABC):
    """Абстрактный базовый класс для всех AI стратегий."""

    @abstractmethod
    async def decide_action(self, state: GameState) -> Dict[str, Any]:
        """Принять решение о следующем ходе."""
        pass
