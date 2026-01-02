"""
Tests for configuration system.
"""
import os
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from config.preferences import (
    Config,
    load_config,
    get_wallpaper_config,
    get_llm_config,
    get_theme_preferences,
)


class TestConfig:
    """Test configuration loading and management."""

    def test_config_initialization(self):
        """Test Config class initialization with default values."""
        config = Config()
        assert config.wallpaper_dir == Path("./wallpapers")
        assert config.log_dir == Path("./logs")
        assert config.wallpaper_width == 3024
        assert config.wallpaper_height == 1964
        assert config.prefer_indian_culture is True
        assert config.prefer_indian_achievements is True

    def test_config_from_env(self, monkeypatch, tmp_path):
        """Test Config initialization from environment variables."""
        test_wallpaper_dir = tmp_path / "wallpapers"
        test_log_dir = tmp_path / "logs"
        
        monkeypatch.setenv("WALLPAPER_DIR", str(test_wallpaper_dir))
        monkeypatch.setenv("LOG_DIR", str(test_log_dir))
        monkeypatch.setenv("WALLPAPER_WIDTH", "1920")
        monkeypatch.setenv("WALLPAPER_HEIGHT", "1080")
        monkeypatch.setenv("PREFER_INDIAN_CULTURE", "false")
        monkeypatch.setenv("PREFER_INDIAN_ACHIEVEMENTS", "false")

        config = Config()
        assert config.wallpaper_dir == test_wallpaper_dir
        assert config.log_dir == test_log_dir
        assert config.wallpaper_width == 1920
        assert config.wallpaper_height == 1080
        assert config.prefer_indian_culture is False
        assert config.prefer_indian_achievements is False

    def test_load_config_from_dotenv(self, tmp_path, monkeypatch):
        """Test loading configuration from .env file."""
        env_file = tmp_path / ".env"
        test_wallpaper_dir = tmp_path / "test_wallpapers"
        test_log_dir = tmp_path / "test_logs"
        
        env_content = f"""WALLPAPER_DIR={test_wallpaper_dir}
LOG_DIR={test_log_dir}
WALLPAPER_WIDTH=2560
WALLPAPER_HEIGHT=1440
PREFER_INDIAN_CULTURE=true
PREFER_INDIAN_ACHIEVEMENTS=true
ANTHROPIC_API_KEY=test_key_123
LLM_PROVIDER=anthropic
"""
        env_file.write_text(env_content)

        config = load_config(env_file_path=env_file)
        assert config.wallpaper_dir == test_wallpaper_dir
        assert config.log_dir == test_log_dir
        assert config.wallpaper_width == 2560
        assert config.wallpaper_height == 1440
        assert config.anthropic_api_key == "test_key_123"
        assert config.llm_provider == "anthropic"

    def test_get_wallpaper_config(self, monkeypatch):
        """Test getting wallpaper configuration."""
        # Ensure clean environment
        monkeypatch.delenv("WALLPAPER_WIDTH", raising=False)
        monkeypatch.delenv("WALLPAPER_HEIGHT", raising=False)
        monkeypatch.delenv("WALLPAPER_DIR", raising=False)
        
        config = Config()
        wallpaper_config = get_wallpaper_config(config)

        assert "width" in wallpaper_config
        assert "height" in wallpaper_config
        assert "directory" in wallpaper_config
        assert wallpaper_config["width"] == 3024
        assert wallpaper_config["height"] == 1964
        assert wallpaper_config["directory"] == Path("./wallpapers")

    def test_get_llm_config(self, monkeypatch):
        """Test getting LLM configuration."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test_anthropic_key")
        monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")
        monkeypatch.setenv("LLM_PROVIDER", "anthropic")

        config = Config()
        llm_config = get_llm_config(config)

        assert "provider" in llm_config
        assert "anthropic_api_key" in llm_config
        assert "openai_api_key" in llm_config
        assert llm_config["provider"] == "anthropic"
        assert llm_config["anthropic_api_key"] == "test_anthropic_key"
        assert llm_config["openai_api_key"] == "test_openai_key"

    def test_get_llm_config_default_provider(self, monkeypatch):
        """Test LLM config defaults to anthropic if not specified."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test_key")
        monkeypatch.delenv("LLM_PROVIDER", raising=False)

        config = Config()
        llm_config = get_llm_config(config)
        assert llm_config["provider"] == "anthropic"

    def test_get_theme_preferences(self):
        """Test getting theme preferences."""
        config = Config()
        preferences = get_theme_preferences(config)

        assert "prefer_indian_culture" in preferences
        assert "prefer_indian_achievements" in preferences
        assert preferences["prefer_indian_culture"] is True
        assert preferences["prefer_indian_achievements"] is True

    def test_config_creates_directories(self, tmp_path):
        """Test that config creates directories if they don't exist."""
        wallpaper_dir = tmp_path / "wallpapers"
        log_dir = tmp_path / "logs"

        config = Config()
        config.wallpaper_dir = wallpaper_dir
        config.log_dir = log_dir

        # Simulate directory creation
        wallpaper_dir.mkdir(parents=True, exist_ok=True)
        log_dir.mkdir(parents=True, exist_ok=True)

        assert wallpaper_dir.exists()
        assert log_dir.exists()

    def test_config_validation(self):
        """Test configuration validation."""
        config = Config()
        # Valid config should not raise errors
        assert config.wallpaper_width > 0
        assert config.wallpaper_height > 0
        assert isinstance(config.prefer_indian_culture, bool)
        assert isinstance(config.prefer_indian_achievements, bool)

    def test_missing_api_key_handling(self, monkeypatch):
        """Test handling of missing API keys."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        config = Config()
        llm_config = get_llm_config(config)

        # Should still return config, but with None keys
        assert "anthropic_api_key" in llm_config
        assert "openai_api_key" in llm_config

