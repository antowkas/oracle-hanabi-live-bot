from pathlib import Path
from typing import List, Optional

import toml
from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotConfig(BaseSettings):
    """Конфигурация для одного бота."""
    model_config = SettingsConfigDict(extra='ignore')

    username: str
    password: Optional[SecretStr] = None
    strategy: str


class Settings(BaseSettings):
    """Глобальная конфигурация, загружаемая из TOML и .env."""
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='allow'
    )

    ws_url: str = "wss://hanab.live/ws"
    auth_url: str = "https://hanab.live/login"
    reconnect_delay_base: float = 2.0
    reconnect_delay_max: float = 60.0
    bots: List[BotConfig] = Field(default_factory=list)

    @model_validator(mode='before')
    @classmethod
    def load_from_toml(cls, values):
        """Загружает базовую конфигурацию из config.toml."""
        toml_path = Path("config.toml")
        if not toml_path.exists():
            raise FileNotFoundError("config.toml not found. Please create it.")

        toml_config = toml.load(toml_path)
        return toml_config | values

    @model_validator(mode='after')
    def load_bot_passwords(self) -> 'Settings':
        """Динамически загружает пароли для ботов из .env."""
        extra_vars = self.__pydantic_extra__ or {}

        for bot in self.bots:
            env_var_name = f"{bot.username.lower()}_password"

            password_value = extra_vars.get(env_var_name)
            if password_value:
                bot.password = SecretStr(str(password_value))

            if not bot.password:
                raise ValueError(
                    f"Password for bot '{bot.username}' not found in .env as "
                    f"'{bot.username.upper()}_PASSWORD'"
                )
        return self


# Синглтон
settings = Settings()
