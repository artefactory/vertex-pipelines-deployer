from enum import Enum

from loguru import logger


class LoguruLevel(str, Enum):  # noqa: D101
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DisableLogger(object):
    """Context manager to disable a loguru logger."""

    def __init__(self, name: str) -> None:  # noqa: D107
        self.name = name

    def __enter__(self) -> None:  # noqa: D105
        logger.disable(self.name)

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # noqa: D105
        logger.enable(self.name)
