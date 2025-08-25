import asyncio
import logging

import aiohttp

from oraclehlb.config import settings
from oraclehlb.core.bot_factory import BotFactory
from oraclehlb.services.auth import AuthService

log = logging.getLogger(__name__)


class BotManager:
    def __init__(self):
        self._configs = settings.bots
        self._reconnect_delay = settings.reconnect_delay_base

    async def _launch_bot_supervisor(self, factory: BotFactory, bot_config):
        """Надзиратель, который перезапускает одного бота в случае сбоя."""
        log.info(f"Starting supervisor for bot '{bot_config.username}'.")
        while True:
            try:
                bot = await factory.create_bot(bot_config)
                await bot.run()
            except asyncio.CancelledError:
                log.info(f"Supervisor for '{bot_config.username}' cancelled.")
                break
            except Exception:
                log.exception(f"Bot '{bot_config.username}' crashed. Restarting after {self._reconnect_delay}s...")
                await asyncio.sleep(self._reconnect_delay)

    async def run(self):
        """Запускает и управляет всеми ботами."""
        # Создаем одну сессию для всех сервисов аутентификации
        async with aiohttp.ClientSession() as session:
            auth_service = AuthService(settings.auth_url, session)
            factory = BotFactory(auth_service)

            tasks = [
                asyncio.create_task(self._launch_bot_supervisor(factory, bot_cfg))
                for bot_cfg in self._configs
            ]
            await asyncio.gather(*tasks)
