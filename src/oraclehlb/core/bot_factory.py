from oraclehlb.config import BotConfig
from oraclehlb.core.bot import HanabiBot
from oraclehlb.core.strategy_loader import load_strategy  # <--- Импорт изменен
from oraclehlb.services.auth import AuthService


class BotFactory:
    """Отвечает за создание и конфигурацию одного экземпляра HanabiBot."""
    def __init__(self, auth_service: AuthService):
        self._auth_service = auth_service

    async def create_bot(self, bot_config: BotConfig) -> HanabiBot:
        """Создает, аутентифицирует и собирает экземпляр бота."""
        auth_cookie = await self._auth_service.authenticate(bot_config)
        if not auth_cookie:
            raise ConnectionRefusedError(f"Authentication failed for {bot_config.username}")

        strategy_instance = load_strategy(bot_config.strategy)

        return HanabiBot(
            username=bot_config.username,
            cookie=auth_cookie,
            strategy=strategy_instance
        )
