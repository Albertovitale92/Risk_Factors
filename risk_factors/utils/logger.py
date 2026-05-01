import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def get_logger(
    name: str,
    *,
    level: int = logging.INFO,
    log_file: str | Path | None = None,
    max_bytes: int = 5_000_000,
    backup_count: int = 3,
) -> logging.Logger:
    """Get a configured logger with optional rotating file output."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    formatter = logging.Formatter(DEFAULT_LOG_FORMAT)
    if not any(getattr(handler, "_risk_factors_console", False) for handler in logger.handlers):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        console_handler._risk_factors_console = True
        logger.addHandler(console_handler)

    if log_file is not None:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        if not any(
            isinstance(handler, RotatingFileHandler)
            and Path(handler.baseFilename) == log_path.resolve()
            for handler in logger.handlers
        ):
            file_handler = RotatingFileHandler(
                log_path,
                maxBytes=max_bytes,
                backupCount=backup_count,
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(level)
            logger.addHandler(file_handler)

    return logger


def debug(logger: logging.Logger, message: str, *args, **kwargs) -> None:
    """Log a debug message."""
    logger.debug(message, *args, **kwargs)


def info(logger: logging.Logger, message: str, *args, **kwargs) -> None:
    """Log an info message."""
    logger.info(message, *args, **kwargs)


def error(logger: logging.Logger, message: str, *args, **kwargs) -> None:
    """Log an error message."""
    logger.error(message, *args, **kwargs)
