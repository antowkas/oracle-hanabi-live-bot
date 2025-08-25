import importlib
import logging
from typing import Type

from oraclehlb.ai.base import BaseStrategy

log = logging.getLogger(__name__)


def _load_strategy_class(strategy_class_name: str) -> Type[BaseStrategy]:
    """(Приватная) Динамически загружает КЛАСС стратегии по его имени."""
    # Конвенция о нейминге файлов (simplestrategy.py для SimpleStrategy)
    module_path = f"oraclehlb.ai.{strategy_class_name.lower()}"
    try:
        module = importlib.import_module(module_path)
        log.debug(module_path)
        strategy_class = getattr(module, strategy_class_name)

        if not issubclass(strategy_class, BaseStrategy):
            raise TypeError(f"Class {strategy_class_name} is not a subclass of BaseStrategy.")

        return strategy_class
    except (ImportError, AttributeError):
        log.exception(f"Could not load strategy class '{strategy_class_name}'.")
        raise ValueError(f"Could not load strategy class '{strategy_class_name}'.")


def load_strategy(strategy_name: str) -> BaseStrategy:
    """
    Загружает класс стратегии и возвращает его ЭКЗЕМПЛЯР.
    В будущем сюда можно будет передавать параметры для инициализации стратегии?
    """
    log.debug(f"Loading strategy '{strategy_name}'...")
    strategy_class = _load_strategy_class(strategy_name)

    # Создаем экземпляр класса
    return strategy_class()
