"""
Configuration management for Wallpaper Agent.

Handles loading and managing configuration from environment variables
and .env files.
"""
import os
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv


class Config:
    """Configuration class for Wallpaper Agent."""

    def __init__(self):
        """Initialize configuration with defaults or from environment variables."""
        # Wallpaper settings
        self.wallpaper_dir = Path(
            os.getenv("WALLPAPER_DIR", "./wallpapers")
        )
        self.log_dir = Path(
            os.getenv("LOG_DIR", "./logs")
        )
        self.wallpaper_width = int(
            os.getenv("WALLPAPER_WIDTH", "3024")
        )
        self.wallpaper_height = int(
            os.getenv("WALLPAPER_HEIGHT", "1964")
        )

        # Theme preferences
        self.prefer_indian_culture = (
            os.getenv("PREFER_INDIAN_CULTURE", "true").lower() == "true"
        )
        self.prefer_indian_achievements = (
            os.getenv("PREFER_INDIAN_ACHIEVEMENTS", "true").lower() == "true"
        )

        # LLM configuration
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.llm_provider = os.getenv("LLM_PROVIDER", "anthropic").lower()

        # Ensure directories exist
        self._ensure_directories()

    def _ensure_directories(self):
        """Create directories if they don't exist."""
        self.wallpaper_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)


def load_config(env_file_path: Optional[Path] = None) -> Config:
    """
    Load configuration from .env file and environment variables.

    Args:
        env_file_path: Optional path to .env file. If None, looks for .env
                      in current directory.

    Returns:
        Config instance with loaded configuration.
    """
    if env_file_path is None:
        env_file_path = Path(".env")

    # Load .env file if it exists
    if env_file_path.exists():
        load_dotenv(env_file_path)

    return Config()


def get_wallpaper_config(config: Config) -> Dict:
    """
    Get wallpaper-related configuration.

    Args:
        config: Config instance

    Returns:
        Dictionary with wallpaper configuration
    """
    return {
        "width": config.wallpaper_width,
        "height": config.wallpaper_height,
        "directory": config.wallpaper_dir,
    }


def get_llm_config(config: Config) -> Dict:
    """
    Get LLM-related configuration.

    Args:
        config: Config instance

    Returns:
        Dictionary with LLM configuration
    """
    return {
        "provider": config.llm_provider,
        "anthropic_api_key": config.anthropic_api_key,
        "openai_api_key": config.openai_api_key,
    }


def get_theme_preferences(config: Config) -> Dict:
    """
    Get theme preference configuration.

    Args:
        config: Config instance

    Returns:
        Dictionary with theme preferences
    """
    return {
        "prefer_indian_culture": config.prefer_indian_culture,
        "prefer_indian_achievements": config.prefer_indian_achievements,
    }

