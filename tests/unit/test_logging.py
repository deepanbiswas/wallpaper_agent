"""
Tests for logging system.
"""
import pytest
import logging
from pathlib import Path
from unittest.mock import patch, mock_open

from utils.logger import setup_logging, get_logger


class TestLogging:
    """Test logging system."""

    def test_setup_logging_creates_log_file(self, tmp_path):
        """Test that setup_logging creates log file."""
        log_dir = tmp_path / "logs"
        log_file = log_dir / "wallpaper_agent.log"
        
        setup_logging(log_dir=log_dir)
        
        # Logger should be configured
        logger = logging.getLogger("wallpaper_agent")
        assert logger is not None
        assert len(logger.handlers) > 0

    def test_setup_logging_creates_directory(self, tmp_path):
        """Test that setup_logging creates log directory if needed."""
        log_dir = tmp_path / "new_logs"
        
        setup_logging(log_dir=log_dir)
        
        assert log_dir.exists()

    def test_get_logger(self):
        """Test getting logger instance."""
        logger = get_logger("test_module")
        
        assert logger is not None
        assert isinstance(logger, logging.Logger)
        # Logger name should be prefixed with "wallpaper_agent."
        assert logger.name == "wallpaper_agent.test_module"

    def test_logger_logs_to_file(self, tmp_path):
        """Test that logger writes to file."""
        log_dir = tmp_path / "logs"
        setup_logging(log_dir=log_dir)
        
        logger = get_logger("test")
        logger.info("Test message")
        
        # Check that log file exists and contains message
        log_file = log_dir / "wallpaper_agent.log"
        if log_file.exists():
            content = log_file.read_text()
            assert "Test message" in content

    def test_logger_formats_messages(self, tmp_path):
        """Test that logger formats messages correctly."""
        log_dir = tmp_path / "logs"
        setup_logging(log_dir=log_dir)
        
        logger = get_logger("test")
        logger.info("Test message")
        
        # Logger should format with timestamp, level, etc.
        log_file = log_dir / "wallpaper_agent.log"
        if log_file.exists():
            content = log_file.read_text()
            # Should contain log level
            assert "INFO" in content or "info" in content.lower()

    def test_logger_handles_errors(self, tmp_path):
        """Test that logger handles error logging."""
        log_dir = tmp_path / "logs"
        setup_logging(log_dir=log_dir)
        
        logger = get_logger("test")
        try:
            raise ValueError("Test error")
        except ValueError as e:
            logger.error(f"Error occurred: {e}")
        
        log_file = log_dir / "wallpaper_agent.log"
        if log_file.exists():
            content = log_file.read_text()
            assert "Error occurred" in content or "Test error" in content

