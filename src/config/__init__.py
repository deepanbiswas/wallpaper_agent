"""
Configuration package for Wallpaper Agent.
"""
from config.preferences import (
    Config,
    load_config,
    get_wallpaper_config,
    get_llm_config,
    get_theme_preferences,
)

__all__ = [
    "Config",
    "load_config",
    "get_wallpaper_config",
    "get_llm_config",
    "get_theme_preferences",
]
