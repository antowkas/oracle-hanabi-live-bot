import asyncio
import logging

from oraclehlb.core.bot_manager import BotManager

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler('oraclehlb.log')
file_handler.setLevel(logging.DEBUG)

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    handlers=[console_handler, file_handler])
log = logging.getLogger(__name__)


async def async_main():
    """Асинхронная точка входа в приложение."""
    manager = BotManager()
    await manager.run()


def main():
    """Синхронная точка входа для безопасного запуска и остановки."""
    try:
        asyncio.run(async_main())
    except (KeyboardInterrupt, asyncio.CancelledError):
        log.info("Shutdown requested by user.")
    except Exception:
        log.exception("An unhandled exception caused the application to terminate.")


if __name__ == "__main__":
    main()
