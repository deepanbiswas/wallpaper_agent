"""
macOS-specific wallpaper application implementation.
"""
import subprocess
from pathlib import Path
from typing import Optional


class MacOSWallpaperApplier:
    """macOS-specific wallpaper application using osascript."""
    
    def __init__(self):
        """Initialize macOS wallpaper applier."""
        pass
    
    def apply_wallpaper(
        self,
        file_path: Path,
        desktop_index: int
    ) -> tuple[bool, Optional[str]]:
        """
        Apply wallpaper to macOS desktop.
        
        Args:
            file_path: Path to wallpaper image file
            desktop_index: Desktop index (0-indexed)
            
        Returns:
            Tuple of (success: bool, error: Optional[str])
        """
        try:
            # Convert to macOS desktop number (1-indexed)
            desktop_number = desktop_index + 1
            
            # Get desktop count to determine approach
            desktop_count = self.get_desktop_count()
            
            # Build file path string for AppleScript
            file_path_str = str(file_path.absolute())
            # Escape special characters for AppleScript
            file_path_str = file_path_str.replace('\\', '\\\\').replace('"', '\\"')
            
            if desktop_count > 1 and desktop_index == 1:
                # Target specific desktop (second desktop when 2+ desktops exist)
                # Note: macOS Spaces/Desktops are 1-indexed in AppleScript
                script = f'''
                    tell application "System Events"
                        tell desktop {desktop_number}
                            set picture to POSIX file "{file_path_str}"
                        end tell
                    end tell
                '''
            else:
                # Single desktop or first desktop - use Finder method (more reliable)
                script = f'tell application "Finder" to set desktop picture to POSIX file "{file_path_str}"'
            
            # Execute osascript
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=10,
            )
            
            if result.returncode == 0:
                return (True, None)
            else:
                return (False, result.stderr or 'Unknown error')
                
        except subprocess.TimeoutExpired:
            return (False, "Wallpaper application timed out")
        except Exception as e:
            return (False, str(e))
    
    def get_desktop_count(self) -> int:
        """
        Get the number of virtual desktops (Spaces) on macOS.
        
        Returns:
            Number of desktops, defaults to 1 on error
        """
        try:
            # Use osascript to get desktop count
            script = '''
                tell application "System Events"
                    count of desktops
                end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=5,
            )
            
            if result.returncode == 0:
                count = int(result.stdout.strip())
                return max(1, count)  # Ensure at least 1
            else:
                return 1  # Default to 1 on error
                
        except (ValueError, subprocess.TimeoutExpired, Exception):
            return 1  # Default to 1 on any error

