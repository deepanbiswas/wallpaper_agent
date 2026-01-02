"""
Integration tests for Wallpaper Generation Agent.

Tests the full wallpaper generation workflow with real components.
"""
import pytest
from pathlib import Path
from agents.wallpaper_generation.agent import WallpaperGenerationAgent
from agents.wallpaper_generation.domain import WallpaperRequest


@pytest.mark.integration
@pytest.mark.slow
class TestWallpaperGenerationAgentIntegration:
    """Integration tests for Wallpaper Generation Agent."""
    
    def test_generate_wallpaper_full_workflow(self, tmp_path):
        """Test full wallpaper generation workflow."""
        # Set wallpaper directory to temp path
        import os
        original_dir = os.environ.get("WALLPAPER_DIR")
        os.environ["WALLPAPER_DIR"] = str(tmp_path)
        
        try:
            agent = WallpaperGenerationAgent()
            
            request = WallpaperRequest(
                theme_name="Test Theme",
                style_guidelines={
                    "prompt": "Minimalistic dark-themed wallpaper featuring test theme",
                    "color_palette": ["#1a1a1a", "#2d2d2d"],
                    "key_elements": ["minimalistic", "dark"],
                },
                width=1024,  # Smaller for faster testing
                height=768,
            )
            
            result = agent.generate_wallpaper(request)
            
            # Should complete (may succeed or fail depending on API)
            assert result is not None
            assert isinstance(result.success, bool)
            
            if result.success:
                assert result.file_path is not None
                assert result.file_path.exists()
                assert result.file_path.suffix in [".png", ".jpg", ".jpeg"]
            else:
                # If failed, should have error message
                assert result.error is not None
                
        finally:
            # Restore original directory
            if original_dir:
                os.environ["WALLPAPER_DIR"] = original_dir
            elif "WALLPAPER_DIR" in os.environ:
                del os.environ["WALLPAPER_DIR"]
    
    def test_build_prompt_integration(self):
        """Test prompt building with real style guidelines."""
        agent = WallpaperGenerationAgent()
        
        style_guidelines = {
            "prompt": "Custom prompt from selection agent",
            "color_palette": ["#000000", "#1a1a1a", "#2d2d2d"],
            "key_elements": ["lights", "celebration"],
            "style_description": "Minimalistic dark theme",
        }
        
        prompt = agent._build_prompt("Diwali", style_guidelines)
        
        assert "Diwali" in prompt or "diwali" in prompt.lower()
        assert "dark" in prompt.lower()
        assert "minimalistic" in prompt.lower()
        assert len(prompt) > 0
    
    def test_request_validation(self):
        """Test request validation with various inputs."""
        agent = WallpaperGenerationAgent()
        
        # Valid request
        valid_request = WallpaperRequest(
            theme_name="Test",
            style_guidelines={"prompt": "Test prompt"},
        )
        assert agent._validate_request(valid_request) is True
        
        # Invalid - empty theme name
        invalid_request1 = WallpaperRequest(
            theme_name="",
            style_guidelines={"prompt": "Test"},
        )
        assert agent._validate_request(invalid_request1) is False
        
        # Invalid - no style guidelines
        invalid_request2 = WallpaperRequest(
            theme_name="Test",
            style_guidelines={},
        )
        assert agent._validate_request(invalid_request2) is False
    
    def test_wallpaper_result_structure(self, tmp_path):
        """Test that wallpaper result has correct structure."""
        import os
        original_dir = os.environ.get("WALLPAPER_DIR")
        os.environ["WALLPAPER_DIR"] = str(tmp_path)
        
        try:
            agent = WallpaperGenerationAgent()
            
            request = WallpaperRequest(
                theme_name="Test",
                style_guidelines={"prompt": "Test prompt"},
                width=512,
                height=512,
            )
            
            result = agent.generate_wallpaper(request)
            
            # Verify result structure
            assert hasattr(result, "success")
            assert hasattr(result, "file_path")
            assert hasattr(result, "error")
            assert hasattr(result, "metadata")
            
            # Verify result can be converted to dict
            result_dict = result.to_dict()
            assert "success" in result_dict
            assert isinstance(result_dict["success"], bool)
            
        finally:
            if original_dir:
                os.environ["WALLPAPER_DIR"] = original_dir
            elif "WALLPAPER_DIR" in os.environ:
                del os.environ["WALLPAPER_DIR"]

