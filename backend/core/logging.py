import json
import logging
from datetime import datetime, UTC
from logging.config import dictConfig
from typing import Any

from backend.core.settings import settings


class JsonFormatter(logging.Formatter):
    reserved = frozenset(logging.makeLogRecord({}).__dict__) | {
        "message",
        "asctime",
        "color_message",
    }

    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "time": datetime.fromtimestamp(record.created, tz=UTC).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "line": record.lineno,
            "message": record.getMessage(),
        }

        log_record.update(
            {k: v for k, v in record.__dict__.items() if k not in self.reserved}
        )

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        if record.stack_info:
            log_record["stack"] = self.formatStack(record.stack_info)

        return json.dumps(log_record, ensure_ascii=False, default=str)


def build_config() -> dict[str, Any]:
    formatter = "text" if settings.app.IS_DEBUG else "json"

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {"()": JsonFormatter},
            "text": {
                "format": "%(asctime)s %(levelname)-8s %(name)s:%(lineno)d %(message)s",
                "datefmt": "%H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": formatter,
                "level": "DEBUG",
            },
        },
        "root": {"handlers": ["console"], "level": "WARNING"},
        "loggers": {
            "backend": {"level": settings.logging.LOG_LEVEL},
            "uvicorn": {"level": "INFO", "propagate": True},
            "uvicorn.access": {"level": "INFO", "propagate": True},
            "uvicorn.error": {"level": "INFO", "propagate": True},
            "sqlalchemy.engine": {"level": "WARNING"},
        },
    }


def setup_logging() -> None:
    dictConfig(build_config())


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
