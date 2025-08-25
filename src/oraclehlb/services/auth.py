import logging
import aiohttp
from oraclehlb.config import BotConfig

log = logging.getLogger(__name__)


class AuthService:
    def __init__(self, auth_url: str, session: aiohttp.ClientSession):
        self._auth_url = auth_url
        self._session = session

    async def authenticate(self, bot_config: BotConfig) -> str:
        payload = {
            "username": bot_config.username,
            "password": bot_config.password.get_secret_value(),
            "version": "bot",
        }
        log.info(f"Authenticating '{bot_config.username}'...")
        try:
            async with self._session.post(self._auth_url, data=payload) as resp:
                resp.raise_for_status()
                cookie = resp.cookies.get("hanabi.sid")
                if not cookie:
                    log.error(f"Cookie not found in response for '{bot_config.username}'.")
                    return ""

                log.info(f"Authentication successful for '{bot_config.username}'.")
                return f"hanabi.sid={cookie.value}"
        except aiohttp.ClientResponseError as e:
            log.error(f"Auth failed for '{bot_config.username}' with status {e.status}: {e.message}")
        except aiohttp.ClientError as e:
            log.error(f"An error occurred for '{bot_config.username}' during authentication: {e}")

        return ""
