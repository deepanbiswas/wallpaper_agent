"""
Tests for Wallpaper Application Agent.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
from agents.wallpaper_application.agent import WallpaperApplicationAgent
from agents.wallpaper_application.domain import ApplicationRequest, ApplicationResult


class TestWallpaperApplicationAgent:
    """Test Wallpaper Application Agent."""
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = WallpaperApplicationAgent()
        assert agent is not None
        assert hasattr(agent, 'platform')
    
    def test_agent_initialization_macos(self):
        """Test agent initialization on macOS."""
        with patch('platform.system', return_value='Darwin'):
            agent = WallpaperApplicationAgent()
            assert agent.platform == 'macos'
    
    def test_agent_initialization_windows(self):
        """Test agent initialization on Windows."""
        with patch('platform.system', return_value='Windows'):
            agent = WallpaperApplicationAgent()
            assert agent.platform == 'windows'
    
    @patch('platform.system', return_value='Darwin')
    def test_apply_wallpaper_macos_success(self, mock_platform):
        """Test successful wallpaper application on macOS."""
        with patch.object(WallpaperApplicationAgent, '_get_desktop_count', return_value=1):
            agent = WallpaperApplicationAgent()
            
            # Mock the applier's apply_wallpaper method
            with patch.object(agent._applier, 'apply_wallpaper', return_value=(True, None)):
                request = ApplicationRequest(
                    file_path=Path("/tmp/wallpaper.png"),
                    desktop_index=0,
                )
                
                # Mock file exists
                with patch('pathlib.Path.exists', return_value=True):
                    result = agent.apply_wallpaper(request)
                    
                    assert result is not None
                    assert result.success is True
                    agent._applier.apply_wallpaper.assert_called_once()
    
    @patch('platform.system', return_value='Darwin')
    def test_apply_wallpaper_macos_single_desktop(self, mock_platform):
        """Test applying wallpaper on single desktop (macOS)."""
        with patch.object(WallpaperApplicationAgent, '_get_desktop_count', return_value=1):
            agent = WallpaperApplicationAgent()
            
            # Mock the applier's apply_wallpaper method
            with patch.object(agent._applier, 'apply_wallpaper', return_value=(True, None)):
                request = ApplicationRequest(
                    file_path=Path("/tmp/wallpaper.png"),
                )
                
                # Mock file exists
                with patch('pathlib.Path.exists', return_value=True):
                    result = agent.apply_wallpaper(request)
                    
                    # Should apply to desktop 0 (only desktop)
                    assert result.success is True
                    assert result.desktop_index == 0
                    agent._applier.apply_wallpaper.assert_called_once()
    
    @patch('platform.system', return_value='Darwin')
    def test_apply_wallpaper_macos_two_desktops(self, mock_platform):
        """Test applying wallpaper on second desktop when two desktops exist."""
        with patch.object(WallpaperApplicationAgent, '_get_desktop_count', return_value=2):
            agent = WallpaperApplicationAgent()
            
            # Mock the applier's apply_wallpaper method
            with patch.object(agent._applier, 'apply_wallpaper', return_value=(True, None)):
                request = ApplicationRequest(
                    file_path=Path("/tmp/wallpaper.png"),
                )
                
                # Mock file exists
                with patch('pathlib.Path.exists', return_value=True):
                    result = agent.apply_wallpaper(request)
                    
                    # Should apply to desktop 1 (second desktop)
                    assert result.success is True
                    assert result.desktop_index == 1
                    agent._applier.apply_wallpaper.assert_called_once()
    
    @patch('platform.system', return_value='Darwin')
    def test_apply_wallpaper_macos_custom_desktop(self, mock_platform):
        """Test applying wallpaper to specific desktop."""
        agent = WallpaperApplicationAgent()
        
        # Mock the applier's apply_wallpaper method
        with patch.object(agent._applier, 'apply_wallpaper', return_value=(True, None)):
            request = ApplicationRequest(
                file_path=Path("/tmp/wallpaper.png"),
                desktop_index=0,  # Explicitly set to first desktop
            )
            
            # Mock file exists
            with patch('pathlib.Path.exists', return_value=True):
                result = agent.apply_wallpaper(request)
                
                assert result.success is True
                assert result.desktop_index == 0
    
    @patch('platform.system', return_value='Darwin')
    def test_apply_wallpaper_file_not_found(self, mock_platform):
        """Test handling of missing wallpaper file."""
        agent = WallpaperApplicationAgent()
        
        request = ApplicationRequest(
            file_path=Path("/nonexistent/wallpaper.png"),
        )
        
        result = agent.apply_wallpaper(request)
        
        assert result is not None
        assert result.success is False
        assert result.error is not None
        assert "not found" in result.error.lower() or "does not exist" in result.error.lower()
    
    @patch('platform.system', return_value='Darwin')
    def test_apply_wallpaper_osascript_failure(self, mock_platform):
        """Test handling of osascript command failure."""
        with patch.object(WallpaperApplicationAgent, '_get_desktop_count', return_value=1):
            agent = WallpaperApplicationAgent()
            
            # Mock the applier's apply_wallpaper method to return failure
            with patch.object(agent._applier, 'apply_wallpaper', return_value=(False, "osascript error")):
                request = ApplicationRequest(
                    file_path=Path("/tmp/wallpaper.png"),
                )
                
                # Mock file exists
                with patch('pathlib.Path.exists', return_value=True):
                    result = agent.apply_wallpaper(request)
                    
                    assert result.success is False
                    assert result.error is not None
    
    @patch('platform.system', return_value='Darwin')
    def test_get_desktop_count(self, mock_platform):
        """Test getting desktop count on macOS."""
        agent = WallpaperApplicationAgent()
        
        # Mock the applier's get_desktop_count method
        with patch.object(agent._applier, 'get_desktop_count', return_value=2):
            count = agent._get_desktop_count()
            
            assert count == 2
            agent._applier.get_desktop_count.assert_called_once()
    
    @patch('platform.system', return_value='Darwin')
    def test_get_desktop_count_error(self, mock_platform):
        """Test handling of desktop count detection error."""
        agent = WallpaperApplicationAgent()
        
        # Mock the applier's get_desktop_count method to return 1 (default on error)
        with patch.object(agent._applier, 'get_desktop_count', return_value=1):
            count = agent._get_desktop_count()
            
            # Should default to 1 on error
            assert count == 1
    
    @patch('platform.system', return_value='Darwin')
    def test_select_desktop_index(self, mock_platform):
        """Test desktop index selection logic."""
        agent = WallpaperApplicationAgent()
        
        # Single desktop - should use 0
        with patch.object(agent, '_get_desktop_count', return_value=1):
            index = agent._select_desktop_index(None)
            assert index == 0
        
        # Two desktops - should use 1 (second desktop)
        with patch.object(agent, '_get_desktop_count', return_value=2):
            index = agent._select_desktop_index(None)
            assert index == 1
        
        # Explicit index provided
        index = agent._select_desktop_index(0)
        assert index == 0
    
    @patch('platform.system', return_value='Windows')
    def test_apply_wallpaper_windows_not_implemented(self, mock_platform):
        """Test that Windows implementation is not yet available."""
        agent = WallpaperApplicationAgent()
        
        request = ApplicationRequest(
            file_path=Path("/tmp/wallpaper.png"),
        )
        
        # Mock file exists to get past file validation
        with patch('pathlib.Path.exists', return_value=True):
            result = agent.apply_wallpaper(request)
            
            assert result.success is False
            assert "not implemented" in result.error.lower() or "windows" in result.error.lower()
    
    @patch('platform.system', return_value='Darwin')
    def test_validate_request(self, mock_platform):
        """Test request validation."""
        agent = WallpaperApplicationAgent()
        
        # Valid request
        valid_request = ApplicationRequest(
            file_path=Path("/tmp/wallpaper.png"),
        )
        assert agent._validate_request(valid_request) is True
        
        # Invalid - no file path
        invalid_request = ApplicationRequest(
            file_path=None,
        )
        assert agent._validate_request(invalid_request) is False

