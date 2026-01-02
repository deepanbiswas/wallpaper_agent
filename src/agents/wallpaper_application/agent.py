"""
Wallpaper Application Agent.

Applies generated wallpapers to the desktop.
Supports macOS and Windows (Windows implementation pending).
"""
import platform
from pathlib import Path
from typing import Optional
from agents.wallpaper_application.domain import ApplicationRequest, ApplicationResult
from agents.wallpaper_application.macos_applier import MacOSWallpaperApplier


class WallpaperApplicationAgent:
    """Agent responsible for applying wallpapers to desktop."""
    
    def __init__(self):
        """Initialize Wallpaper Application Agent."""
        system = platform.system()
        if system == 'Darwin':
            self.platform = 'macos'
            self._applier = MacOSWallpaperApplier()
        elif system == 'Windows':
            self.platform = 'windows'
            self._applier = None  # Windows applier not yet implemented
        else:
            self.platform = 'unknown'
            self._applier = None
    
    def apply_wallpaper(self, request: ApplicationRequest) -> ApplicationResult:
        """
        Apply wallpaper to desktop.
        
        Args:
            request: ApplicationRequest with file path and optional desktop index
            
        Returns:
            ApplicationResult with success status
        """
        # Validate request
        if not self._validate_request(request):
            return ApplicationResult(
                success=False,
                error="Invalid request: file_path is required",
            )
        
        # Check if file exists
        if not request.file_path.exists():
            return ApplicationResult(
                success=False,
                error=f"Wallpaper file not found: {request.file_path}",
            )
        
        # Route to platform-specific implementation
        if self.platform == 'macos':
            return self._apply_wallpaper_macos(request)
        elif self.platform == 'windows':
            return self._apply_wallpaper_windows(request)
        else:
            return ApplicationResult(
                success=False,
                error=f"Platform not supported: {self.platform}",
            )
    
    def _apply_wallpaper_macos(self, request: ApplicationRequest) -> ApplicationResult:
        """
        Apply wallpaper on macOS.
        
        Args:
            request: ApplicationRequest with file path
            
        Returns:
            ApplicationResult
        """
        # Select desktop index if not provided
        desktop_index = self._select_desktop_index(request.desktop_index)
        
        # Get desktop count for metadata
        desktop_count = self._get_desktop_count()
        desktop_number = desktop_index + 1
        
        # Use macOS applier
        success, error = self._applier.apply_wallpaper(
            file_path=request.file_path,
            desktop_index=desktop_index,
        )
        
        if success:
            return ApplicationResult(
                success=True,
                desktop_index=desktop_index,
                metadata={
                    "platform": "macos",
                    "desktop_number": desktop_number,
                    "desktop_count": desktop_count,
                    "file_path": str(request.file_path),
                },
            )
        else:
            return ApplicationResult(
                success=False,
                error=f"Failed to apply wallpaper: {error}",
            )
    
    def _apply_wallpaper_windows(self, request: ApplicationRequest) -> ApplicationResult:
        """
        Apply wallpaper on Windows (not yet implemented).
        
        Args:
            request: ApplicationRequest with file path
            
        Returns:
            ApplicationResult with error
        """
        return ApplicationResult(
            success=False,
            error="Windows wallpaper application not yet implemented",
        )
    
    def _get_desktop_count(self) -> int:
        """
        Get the number of virtual desktops (Spaces) on macOS.
        
        Returns:
            Number of desktops, defaults to 1 on error
        """
        if self.platform != 'macos' or self._applier is None:
            return 1
        
        return self._applier.get_desktop_count()
    
    def _select_desktop_index(self, requested_index: Optional[int]) -> int:
        """
        Select desktop index based on rules.
        
        Rules:
        - If explicit index provided, use it
        - If 2 desktops exist, use index 1 (second desktop)
        - If 1 desktop exists, use index 0 (first desktop)
        
        Args:
            requested_index: Explicitly requested desktop index (0-indexed)
            
        Returns:
            Selected desktop index (0-indexed)
        """
        if requested_index is not None:
            return requested_index
        
        desktop_count = self._get_desktop_count()
        
        if desktop_count >= 2:
            return 1  # Second desktop (index 1, desktop number 2)
        else:
            return 0  # First desktop (index 0, desktop number 1)
    
    def _validate_request(self, request: ApplicationRequest) -> bool:
        """
        Validate application request.
        
        Args:
            request: ApplicationRequest to validate
            
        Returns:
            True if valid, False otherwise
        """
        if request.file_path is None:
            return False
        
        return True

