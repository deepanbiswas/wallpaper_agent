"""
Integration tests for Wallpaper Application Agent.

Tests the full wallpaper application workflow with real system calls.
"""
import pytest
from pathlib import Path
from agents.wallpaper_application.agent import WallpaperApplicationAgent
from agents.wallpaper_application.domain import ApplicationRequest


@pytest.mark.integration
class TestWallpaperApplicationAgentIntegration:
    """Integration tests for Wallpaper Application Agent."""
    
    def test_apply_wallpaper_real_file(self, tmp_path):
        """Test applying a real wallpaper file."""
        import platform
        
        if platform.system() != 'Darwin':
            pytest.skip("macOS integration test - skipping on non-macOS system")
        
        # Create a dummy image file for testing
        test_image = tmp_path / "test_wallpaper.png"
        test_image.write_bytes(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)  # Minimal PNG header
        
        agent = WallpaperApplicationAgent()
        
        request = ApplicationRequest(
            file_path=test_image,
        )
        
        result = agent.apply_wallpaper(request)
        
        # Should complete (may succeed or fail depending on system permissions)
        assert result is not None
        assert isinstance(result.success, bool)
        
        if result.success:
            assert result.desktop_index is not None
            assert "macos" in result.metadata.get("platform", "")
    
    def test_get_desktop_count_real(self):
        """Test getting real desktop count on macOS."""
        import platform
        
        if platform.system() != 'Darwin':
            pytest.skip("macOS integration test - skipping on non-macOS system")
        
        agent = WallpaperApplicationAgent()
        count = agent._get_desktop_count()
        
        # Should return at least 1
        assert count >= 1
        assert isinstance(count, int)
    
    def test_select_desktop_index_logic(self):
        """Test desktop index selection logic with real desktop count."""
        import platform
        
        if platform.system() != 'Darwin':
            pytest.skip("macOS integration test - skipping on non-macOS system")
        
        agent = WallpaperApplicationAgent()
        
        # Test with None (auto-select)
        index = agent._select_desktop_index(None)
        assert index in [0, 1]  # Should be 0 or 1
        
        # Test with explicit index
        index = agent._select_desktop_index(0)
        assert index == 0
        
        index = agent._select_desktop_index(1)
        assert index == 1
    
    def test_application_request_validation(self):
        """Test request validation with real file."""
        import platform
        
        if platform.system() != 'Darwin':
            pytest.skip("macOS integration test - skipping on non-macOS system")
        
        agent = WallpaperApplicationAgent()
        
        # Valid request with existing file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp.write(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
            tmp_path = Path(tmp.name)
        
        try:
            request = ApplicationRequest(file_path=tmp_path)
            assert agent._validate_request(request) is True
        finally:
            tmp_path.unlink()
        
        # Invalid request
        invalid_request = ApplicationRequest(file_path=None)
        assert agent._validate_request(invalid_request) is False

