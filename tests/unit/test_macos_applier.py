"""
Tests for MacOSWallpaperApplier.
"""
import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from agents.wallpaper_application.macos_applier import MacOSWallpaperApplier


class TestMacOSWallpaperApplier:
    """Test MacOSWallpaperApplier."""
    
    def test_applier_initialization(self):
        """Test applier initialization."""
        applier = MacOSWallpaperApplier()
        assert applier is not None
    
    @patch('agents.wallpaper_application.macos_applier.subprocess.run')
    def test_apply_wallpaper_success(self, mock_run):
        """Test successful wallpaper application."""
        mock_run.return_value = Mock(returncode=0)
        
        applier = MacOSWallpaperApplier()
        # Mock get_desktop_count to avoid extra subprocess call
        with patch.object(applier, 'get_desktop_count', return_value=1):
            success, error = applier.apply_wallpaper(
                file_path=Path("/tmp/wallpaper.png"),
                desktop_index=0,
            )
            
            assert success is True
            assert error is None
            # Should be called once for applying wallpaper
            assert mock_run.call_count == 1
    
    @patch('agents.wallpaper_application.macos_applier.subprocess.run')
    def test_apply_wallpaper_failure(self, mock_run):
        """Test wallpaper application failure."""
        mock_run.return_value = Mock(returncode=1, stderr="Error message")
        
        applier = MacOSWallpaperApplier()
        success, error = applier.apply_wallpaper(
            file_path=Path("/tmp/wallpaper.png"),
            desktop_index=0,
        )
        
        assert success is False
        assert error is not None
    
    @patch('agents.wallpaper_application.macos_applier.subprocess.run')
    def test_apply_wallpaper_timeout(self, mock_run):
        """Test wallpaper application timeout."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired('osascript', 10)
        
        applier = MacOSWallpaperApplier()
        # Mock get_desktop_count to avoid extra subprocess call
        with patch.object(applier, 'get_desktop_count', return_value=1):
            success, error = applier.apply_wallpaper(
                file_path=Path("/tmp/wallpaper.png"),
                desktop_index=0,
            )
            
            assert success is False
            assert "timed out" in error.lower() or "timeout" in error.lower()
    
    @patch('agents.wallpaper_application.macos_applier.subprocess.run')
    def test_apply_wallpaper_single_desktop(self, mock_run):
        """Test applying to single desktop."""
        mock_run.return_value = Mock(returncode=0)
        
        applier = MacOSWallpaperApplier()
        with patch.object(applier, 'get_desktop_count', return_value=1):
            success, error = applier.apply_wallpaper(
                file_path=Path("/tmp/wallpaper.png"),
                desktop_index=0,
            )
            
            assert success is True
            # Should use Finder method for single desktop
            call_args = mock_run.call_args[0][0]
            assert 'Finder' in ' '.join(call_args)
    
    @patch('agents.wallpaper_application.macos_applier.subprocess.run')
    def test_apply_wallpaper_second_desktop(self, mock_run):
        """Test applying to second desktop when 2+ desktops exist."""
        mock_run.return_value = Mock(returncode=0)
        
        applier = MacOSWallpaperApplier()
        with patch.object(applier, 'get_desktop_count', return_value=2):
            success, error = applier.apply_wallpaper(
                file_path=Path("/tmp/wallpaper.png"),
                desktop_index=1,  # Second desktop
            )
            
            assert success is True
            # Should use System Events method for specific desktop
            call_args = mock_run.call_args[0][0]
            assert 'System Events' in ' '.join(call_args) or 'desktop 2' in ' '.join(call_args)
    
    @patch('agents.wallpaper_application.macos_applier.subprocess.run')
    def test_get_desktop_count(self, mock_run):
        """Test getting desktop count."""
        mock_run.return_value = Mock(returncode=0, stdout='2\n')
        
        applier = MacOSWallpaperApplier()
        count = applier.get_desktop_count()
        
        assert count == 2
        mock_run.assert_called_once()
    
    @patch('agents.wallpaper_application.macos_applier.subprocess.run')
    def test_get_desktop_count_error(self, mock_run):
        """Test handling of desktop count error."""
        mock_run.return_value = Mock(returncode=1)
        
        applier = MacOSWallpaperApplier()
        count = applier.get_desktop_count()
        
        # Should default to 1 on error
        assert count == 1
    
    @patch('agents.wallpaper_application.macos_applier.subprocess.run')
    def test_get_desktop_count_invalid_output(self, mock_run):
        """Test handling of invalid desktop count output."""
        mock_run.return_value = Mock(returncode=0, stdout='invalid\n')
        
        applier = MacOSWallpaperApplier()
        count = applier.get_desktop_count()
        
        # Should default to 1 on ValueError
        assert count == 1

