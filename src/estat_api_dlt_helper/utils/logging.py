import logging
from typing import Optional


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Get logger instance with consistent formatting.

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    if level:
        logger.setLevel(getattr(logging, level.upper()))
    elif not logger.level:
        logger.setLevel(logging.INFO)

    return logger
