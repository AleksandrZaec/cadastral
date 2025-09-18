import logging
import sys
from typing import Optional
from app.core import settings


class JsonFormatter(logging.Formatter):
    """Serialize log records as JSON strings."""

    def format(self, record: logging.LogRecord) -> str:
        import json
        payload = {
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "time": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S%z"),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def _build_handler() -> logging.Handler:
    """Create a stdout handler with configured formatter."""
    handler = logging.StreamHandler(stream=sys.stdout)
    if getattr(settings, "LOG_JSON", False):
        handler.setFormatter(JsonFormatter())
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
    return handler


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a configured logger, creating handlers only once."""
    logger_name = name or getattr(settings, "LOG_NAME", "app")
    logger = logging.getLogger(logger_name)
    if not logger.handlers:
        log_level_name = getattr(settings, "LOG_LEVEL", "INFO")
        logger.setLevel(getattr(logging, str(log_level_name).upper(), logging.INFO))
        handler = _build_handler()
        logger.addHandler(handler)
        logger.propagate = False
    return logger


