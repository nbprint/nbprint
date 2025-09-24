import logging
from typing import Dict, List, Union

from IPython.display import HTML
from pydantic import Field

from nbprint import Content

__all__ = ("LoggingBasicConfig", "LoggingConfig")


class LoggingBasicConfig(Content):
    """Set the basic logging configuration, to control which logs may show up in the report."""

    log_level: Union[int, str] = "CRITICAL"

    def __call__(self, **_) -> HTML:
        logging.basicConfig(level=self.log_level)
        return HTML("")


class LoggingConfig(Content):
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: Dict[str, Dict[str, Union[str, Dict[str, str]]]] = Field(
        default={
            "simple": {"format": "[%(asctime)s][%(threadName)s][%(name)s][%(levelname)s]: %(message)s"},
            "colorlog": {
                "()": "colorlog.ColoredFormatter",
                "format": "[%(cyan)s%(asctime)s%(reset)s][%(threadName)s][%(blue)s%(name)s%(reset)s][%(log_color)s%(levelname)s%(reset)s]: %(message)s",
                "log_colors": {
                    "DEBUG": "white",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red",
                },
            },
            "whenAndWhere": {"format": "[%(asctime)s][%(threadName)s][%(name)s][%(filename)s:%(lineno)d][%(levelname)s]: %(message)s"},
        }
    )
    handlers: Dict[str, Dict[str, str]] = Field(
        default={
            "console": {
                "level": "WARNING",
                "class": "ccflow.utils.logging.StreamHandler",
                "formatter": "colorlog",
                "stream": "ext://sys.stdout",
            }
        }
    )
    root: Dict[str, Union[str, List[str]]] = Field(default={"handlers": ["console"], "level": "DEBUG"})

    def __call__(self, **_) -> HTML:
        logging.dictConfig(self.model_dump(exclude=["type_"]))
        return HTML("")
