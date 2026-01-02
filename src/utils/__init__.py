"""
Utility functions package for Wallpaper Agent.
"""
from api_clients import (
    DuckDuckGoClient,
    PollinationsClient,
    LLMClient,
)
from utils.image_processor import (
    resize_image,
    ensure_dark_theme,
    save_wallpaper,
    process_wallpaper,
)
from utils.logger import (
    setup_logging,
    get_logger,
)

__all__ = [
    # API Clients
    "DuckDuckGoClient",
    "PollinationsClient",
    "LLMClient",
    # Image Processing
    "resize_image",
    "ensure_dark_theme",
    "save_wallpaper",
    "process_wallpaper",
    # Logging
    "setup_logging",
    "get_logger",
]
