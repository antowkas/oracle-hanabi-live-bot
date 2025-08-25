import asyncio
import logging
from typing import Dict, Any

from oraclehlb.ai.base import BaseStrategy
from oraclehlb.models import GameState, ActionType

log = logging.getLogger(__name__)


class SimpleStrategy(BaseStrategy):
    """Простейшая стратегия: давать подсказку если есть, иначе сбрасывать."""

    async def decide_action(self, state: GameState) -> Dict[str, Any]:
        await asyncio.sleep(0.5)  # Имитация раздумий

        if state.clue_tokens > 0:
            log.info("AI Decision: Giving a clue.")
            num_players = len(state.player_names)
            target_index = (state.our_player_index + 1) % num_players
            return {
                "type": ActionType.RANK_CLUE.value,
                "target": target_index,
                "value": 1,  # В реальной логике здесь будет анализ карт
            }
        else:
            log.info("AI Decision: Discarding.")
            # В реальной логике здесь будет выбор карты для сброса
            # Для примера, нужна реализация получения orderId карты
            return {
                "type": ActionType.DISCARD.value,
                "target": 123,  # Заглушка
            }
