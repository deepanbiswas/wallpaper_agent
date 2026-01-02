"""
Wallpaper Application Agent package.
"""
from agents.wallpaper_application.agent import WallpaperApplicationAgent
from agents.wallpaper_application.domain import ApplicationRequest, ApplicationResult
from agents.wallpaper_application.macos_applier import MacOSWallpaperApplier

__all__ = [
    "WallpaperApplicationAgent",
    "ApplicationRequest",
    "ApplicationResult",
    "MacOSWallpaperApplier",
]

