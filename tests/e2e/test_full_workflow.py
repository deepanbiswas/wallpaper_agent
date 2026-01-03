"""
End-to-End tests for Wallpaper Agent.

Tests the complete workflow from theme discovery to wallpaper application.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
from src.orchestrator.main import WallpaperOrchestrator
from src.orchestrator.domain import OrchestrationResult, OrchestrationStatus


@pytest.mark.e2e
class TestFullWorkflow:
    """End-to-end tests for complete wallpaper generation workflow."""
    
    @patch('src.orchestrator.main.WallpaperApplicationAgent')
    @patch('src.orchestrator.main.WallpaperGenerationAgent')
    @patch('src.orchestrator.main.ThemeSelectionAgent')
    @patch('src.orchestrator.main.ThemeDiscoveryAgent')
    def test_full_workflow_success(
        self,
        mock_disc_agent,
        mock_sel_agent,
        mock_gen_agent,
        mock_app_agent,
    ):
        """Test complete successful workflow."""
        # Setup all agents to succeed
        mock_disc_agent.return_value.discover_themes.return_value = [
            {"name": "Diwali", "description": "Festival of lights", "type": "indian_cultural"},
            {"name": "New Year", "description": "Global celebration", "type": "global"},
        ]
        
        mock_sel_agent.return_value.select_theme.return_value = {
            "name": "Diwali",
            "description": "Festival of lights",
            "type": "indian_cultural",
            "style_guidelines": {"prompt": "minimalistic dark diwali theme"},
        }
        
        from src.agents.wallpaper_generation.domain import WallpaperResult
        mock_gen_agent.return_value.generate_wallpaper.return_value = WallpaperResult(
            success=True,
            file_path=Path("/tmp/wallpaper.png"),
        )
        
        from src.agents.wallpaper_application.domain import ApplicationResult
        mock_app_agent.return_value.apply_wallpaper.return_value = ApplicationResult(
            success=True,
            desktop_index=0,
        )
        
        # Run orchestrator
        orchestrator = WallpaperOrchestrator(max_retries=1, retry_delay=0.01)
        result = orchestrator.run()
        
        # Verify complete success
        assert result.status.value == "success"
        assert result.selected_theme is not None
        assert result.wallpaper_path is not None
        assert result.error is None
        assert result.metadata.get("generation_success") is True
        assert result.metadata.get("application_success") is True
        
        # Verify all agents were called
        mock_disc_agent.return_value.discover_themes.assert_called_once()
        mock_sel_agent.return_value.select_theme.assert_called_once()
        mock_gen_agent.return_value.generate_wallpaper.assert_called_once()
        mock_app_agent.return_value.apply_wallpaper.assert_called_once()
    
    @patch('src.orchestrator.main.WallpaperApplicationAgent')
    @patch('src.orchestrator.main.WallpaperGenerationAgent')
    @patch('src.orchestrator.main.ThemeSelectionAgent')
    @patch('src.orchestrator.main.ThemeDiscoveryAgent')
    def test_full_workflow_with_retry(
        self,
        mock_disc_agent,
        mock_sel_agent,
        mock_gen_agent,
        mock_app_agent,
    ):
        """Test workflow with retry on initial failure."""
        # Discovery fails first time, succeeds second
        mock_disc_agent.return_value.discover_themes.side_effect = [
            [],  # First attempt fails
            [{"name": "Diwali", "description": "Festival", "type": "indian_cultural"}],  # Second succeeds
        ]
        
        mock_sel_agent.return_value.select_theme.return_value = {
            "name": "Diwali",
            "description": "Festival",
            "style_guidelines": {},
        }
        
        from src.agents.wallpaper_generation.domain import WallpaperResult
        mock_gen_agent.return_value.generate_wallpaper.return_value = WallpaperResult(
            success=True,
            file_path=Path("/tmp/wallpaper.png"),
        )
        
        from src.agents.wallpaper_application.domain import ApplicationResult
        mock_app_agent.return_value.apply_wallpaper.return_value = ApplicationResult(
            success=True,
        )
        
        # Run orchestrator with retries
        orchestrator = WallpaperOrchestrator(max_retries=2, retry_delay=0.01)
        result = orchestrator.run()
        
        # Should succeed after retry
        assert result.status.value == "success"
        # Should have retried discovery
        assert mock_disc_agent.return_value.discover_themes.call_count == 2
    
    @patch('src.orchestrator.main.WallpaperApplicationAgent')
    @patch('src.orchestrator.main.WallpaperGenerationAgent')
    @patch('src.orchestrator.main.ThemeSelectionAgent')
    @patch('src.orchestrator.main.ThemeDiscoveryAgent')
    def test_full_workflow_partial_success(
        self,
        mock_disc_agent,
        mock_sel_agent,
        mock_gen_agent,
        mock_app_agent,
    ):
        """Test workflow where wallpaper is generated but not applied."""
        # Setup successful discovery, selection, and generation
        mock_disc_agent.return_value.discover_themes.return_value = [
            {"name": "Diwali", "description": "Festival", "type": "indian_cultural"},
        ]
        
        mock_sel_agent.return_value.select_theme.return_value = {
            "name": "Diwali",
            "description": "Festival",
            "style_guidelines": {},
        }
        
        from src.agents.wallpaper_generation.domain import WallpaperResult
        mock_gen_agent.return_value.generate_wallpaper.return_value = WallpaperResult(
            success=True,
            file_path=Path("/tmp/wallpaper.png"),
        )
        
        # Application fails
        from src.agents.wallpaper_application.domain import ApplicationResult
        mock_app_agent.return_value.apply_wallpaper.return_value = ApplicationResult(
            success=False,
            error="Permission denied",
        )
        
        orchestrator = WallpaperOrchestrator(max_retries=1, retry_delay=0.01)
        result = orchestrator.run()
        
        # Should be partial success
        assert result.status.value == "partial"
        assert result.wallpaper_path is not None  # Wallpaper was generated
        assert result.error is not None
        assert result.metadata.get("generation_success") is True
        assert result.metadata.get("application_success") is False
    
    @patch('src.orchestrator.main.ThemeDiscoveryAgent')
    def test_full_workflow_complete_failure(self, mock_disc_agent):
        """Test workflow that fails completely."""
        # Discovery always fails
        mock_disc_agent.return_value.discover_themes.return_value = []
        
        orchestrator = WallpaperOrchestrator(max_retries=2, retry_delay=0.01)
        result = orchestrator.run()
        
        # Should fail completely
        assert result.status.value == "failed"
        assert result.selected_theme is None
        assert result.wallpaper_path is None
        assert result.error is not None
    
    @patch('src.orchestrator.main.WallpaperApplicationAgent')
    @patch('src.orchestrator.main.WallpaperGenerationAgent')
    @patch('src.orchestrator.main.ThemeSelectionAgent')
    @patch('src.orchestrator.main.ThemeDiscoveryAgent')
    def test_full_workflow_exception_handling(
        self,
        mock_disc_agent,
        mock_sel_agent,
        mock_gen_agent,
        mock_app_agent,
    ):
        """Test workflow handles exceptions gracefully."""
        # Discovery throws exception
        mock_disc_agent.return_value.discover_themes.side_effect = Exception("Network error")
        
        orchestrator = WallpaperOrchestrator(max_retries=2, retry_delay=0.01)
        result = orchestrator.run()
        
        # Should handle exception and return failed status
        assert result.status.value == "failed"
        assert result.error is not None
        assert "exception" in result.error.lower() or "network" in result.error.lower()

