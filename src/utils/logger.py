"""
Logging utilities for Wallpaper Agent.

Provides centralized logging configuration and logger instances.
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logging(
    log_dir: Path = Path("./logs"),
    log_level: int = logging.INFO,
    log_file: str = "wallpaper_agent.log"
) -> None:
    """
    Setup logging configuration.

    Args:
        log_dir: Directory for log files
        log_level: Logging level (default: INFO)
        log_file: Name of log file
    """
    # Create log directory if it doesn't exist
    log_dir.mkdir(parents=True, exist_ok=True)

    # Get root logger
    logger = logging.getLogger("wallpaper_agent")
    logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler with rotation
    log_file_path = log_dir / log_file
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Logger name (typically module name)

    Returns:
        Logger instance
    """
    # Ensure parent logger is set up
    root_logger = logging.getLogger("wallpaper_agent")
    if not root_logger.handlers:
        setup_logging()

    # Return child logger
    return logging.getLogger(f"wallpaper_agent.{name}")

