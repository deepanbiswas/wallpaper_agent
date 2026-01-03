"""
Tests for Main Orchestrator.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
from src.orchestrator.main import WallpaperOrchestrator
from src.orchestrator.domain import OrchestrationResult, OrchestrationStatus


class TestWallpaperOrchestrator:
    """Test Main Orchestrator."""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initialization."""
        orchestrator = WallpaperOrchestrator()
        assert orchestrator is not None
        assert hasattr(orchestrator, 'theme_discovery_agent')
        assert hasattr(orchestrator, 'theme_selection_agent')
        assert hasattr(orchestrator, 'wallpaper_generation_agent')
        assert hasattr(orchestrator, 'wallpaper_application_agent')
    
    @patch('src.orchestrator.main.ThemeDiscoveryAgent')
    @patch('src.orchestrator.main.ThemeSelectionAgent')
    @patch('src.orchestrator.main.WallpaperGenerationAgent')
    @patch('src.orchestrator.main.WallpaperApplicationAgent')
    def test_run_full_workflow_success(
        self,
        mock_app_agent,
        mock_gen_agent,
        mock_sel_agent,
        mock_disc_agent,
    ):
        """Test successful full workflow execution."""
        # Setup mocks
        mock_disc_result = [
            {"name": "Diwali", "description": "Festival of lights", "type": "indian_cultural"},
            {"name": "New Year", "description": "Global celebration", "type": "global"},
        ]
        mock_disc_agent.return_value.discover_themes.return_value = mock_disc_result
        
        # select_theme returns a dict, not a Theme object
        mock_sel_theme = {
            "name": "Diwali",
            "description": "Festival of lights",
            "type": "indian_cultural",
            "final_score": 0.95,
            "style_guidelines": {"prompt": "minimalistic dark diwali theme"},
        }
        mock_sel_agent.return_value.select_theme.return_value = mock_sel_theme
        
        from src.agents.wallpaper_generation.domain import WallpaperResult
        mock_wallpaper_result = WallpaperResult(
            success=True,
            file_path=Path("/tmp/wallpaper.png"),
        )
        mock_gen_agent.return_value.generate_wallpaper.return_value = mock_wallpaper_result
        
        from src.agents.wallpaper_application.domain import ApplicationResult
        mock_app_result = ApplicationResult(
            success=True,
            desktop_index=0,
        )
        mock_app_agent.return_value.apply_wallpaper.return_value = mock_app_result
        
        # Run orchestrator
        orchestrator = WallpaperOrchestrator()
        result = orchestrator.run()
        
        # Verify result
        assert result is not None
        assert result.status.value == "success"
        assert result.selected_theme is not None
        assert result.wallpaper_path is not None
        assert result.error is None
        
        # Verify all agents were called
        mock_disc_agent.return_value.discover_themes.assert_called_once()
        mock_sel_agent.return_value.select_theme.assert_called_once()
        mock_gen_agent.return_value.generate_wallpaper.assert_called_once()
        mock_app_agent.return_value.apply_wallpaper.assert_called_once()
    
    @patch('src.orchestrator.main.ThemeDiscoveryAgent')
    def test_run_theme_discovery_failure(self, mock_disc_agent):
        """Test handling of theme discovery failure."""
        # Mock discovery failure
        mock_disc_agent.return_value.discover_themes.return_value = []
        
        orchestrator = WallpaperOrchestrator()
        result = orchestrator.run()
        
        assert result.status.value == "failed"
        assert result.error is not None
        assert "discovery" in result.error.lower() or "theme" in result.error.lower() or "no themes" in result.error.lower()
        assert result.selected_theme is None
    
    @patch('src.orchestrator.main.ThemeDiscoveryAgent')
    @patch('src.orchestrator.main.ThemeSelectionAgent')
    def test_run_theme_selection_failure(
        self,
        mock_sel_agent,
        mock_disc_agent,
    ):
        """Test handling of theme selection failure."""
        # Mock discovery success
        mock_disc_result = [
            {"name": "Diwali", "description": "Festival of lights", "type": "indian_cultural"},
        ]
        mock_disc_agent.return_value.discover_themes.return_value = mock_disc_result
        
        # Mock selection failure
        mock_sel_agent.return_value.select_theme.return_value = None
        
        orchestrator = WallpaperOrchestrator()
        result = orchestrator.run()
        
        assert result.status.value == "failed"
        assert result.error is not None
        assert "selection" in result.error.lower() or "theme" in result.error.lower() or "failed to select" in result.error.lower()
    
    @patch('src.orchestrator.main.ThemeDiscoveryAgent')
    @patch('src.orchestrator.main.ThemeSelectionAgent')
    @patch('src.orchestrator.main.WallpaperGenerationAgent')
    def test_run_wallpaper_generation_failure(
        self,
        mock_gen_agent,
        mock_sel_agent,
        mock_disc_agent,
    ):
        """Test handling of wallpaper generation failure."""
        # Mock discovery and selection success
        mock_disc_result = [
            {"name": "Diwali", "description": "Festival of lights", "type": "indian_cultural"},
        ]
        mock_disc_agent.return_value.discover_themes.return_value = mock_disc_result
        
        # select_theme returns a dict
        mock_sel_theme = {
            "name": "Diwali",
            "description": "Festival of lights",
            "type": "indian_cultural",
            "final_score": 0.95,
        }
        mock_sel_agent.return_value.select_theme.return_value = mock_sel_theme
        
        # Mock generation failure
        from src.agents.wallpaper_generation.domain import WallpaperResult
        mock_wallpaper_result = WallpaperResult(
            success=False,
            error="Generation failed",
        )
        mock_gen_agent.return_value.generate_wallpaper.return_value = mock_wallpaper_result
        
        orchestrator = WallpaperOrchestrator()
        result = orchestrator.run()
        
        assert result.status.value == "failed"
        assert result.error is not None
        assert "generation" in result.error.lower() or "wallpaper" in result.error.lower()
    
    @patch('src.orchestrator.main.ThemeDiscoveryAgent')
    @patch('src.orchestrator.main.ThemeSelectionAgent')
    @patch('src.orchestrator.main.WallpaperGenerationAgent')
    @patch('src.orchestrator.main.WallpaperApplicationAgent')
    def test_run_wallpaper_application_failure(
        self,
        mock_app_agent,
        mock_gen_agent,
        mock_sel_agent,
        mock_disc_agent,
    ):
        """Test handling of wallpaper application failure."""
        # Mock discovery, selection, and generation success
        mock_disc_result = [
            {"name": "Diwali", "description": "Festival of lights", "type": "indian_cultural"},
        ]
        mock_disc_agent.return_value.discover_themes.return_value = mock_disc_result
        
        # select_theme returns a dict
        mock_sel_theme = {
            "name": "Diwali",
            "description": "Festival of lights",
            "type": "indian_cultural",
            "final_score": 0.95,
        }
        mock_sel_agent.return_value.select_theme.return_value = mock_sel_theme
        
        from src.agents.wallpaper_generation.domain import WallpaperResult
        mock_wallpaper_result = WallpaperResult(
            success=True,
            file_path=Path("/tmp/wallpaper.png"),
        )
        mock_gen_agent.return_value.generate_wallpaper.return_value = mock_wallpaper_result
        
        # Mock application failure
        from src.agents.wallpaper_application.domain import ApplicationResult
        mock_app_result = ApplicationResult(
            success=False,
            error="Application failed",
        )
        mock_app_agent.return_value.apply_wallpaper.return_value = mock_app_result
        
        orchestrator = WallpaperOrchestrator()
        result = orchestrator.run()
        
        # Application failure should result in PARTIAL status (wallpaper generated but not applied)
        assert result.status.value == "partial"
        assert result.error is not None
        assert "application" in result.error.lower() or "wallpaper" in result.error.lower()
        # Wallpaper should still be generated even if application fails
        assert result.wallpaper_path is not None
    
    @patch('src.orchestrator.main.ThemeDiscoveryAgent')
    @patch('src.orchestrator.main.ThemeSelectionAgent')
    @patch('src.orchestrator.main.WallpaperGenerationAgent')
    @patch('src.orchestrator.main.WallpaperApplicationAgent')
    @patch('src.orchestrator.main.get_logger')
    def test_run_logging(
        self,
        mock_logger,
        mock_app_agent,
        mock_gen_agent,
        mock_sel_agent,
        mock_disc_agent,
    ):
        """Test that orchestrator logs workflow steps."""
        # Setup successful workflow
        mock_disc_result = [
            {"name": "Diwali", "description": "Festival of lights", "type": "indian_cultural"},
        ]
        mock_disc_agent.return_value.discover_themes.return_value = mock_disc_result
        
        # select_theme returns a dict
        mock_sel_theme = {
            "name": "Diwali",
            "description": "Festival of lights",
            "type": "indian_cultural",
            "final_score": 0.95,
        }
        mock_sel_agent.return_value.select_theme.return_value = mock_sel_theme
        
        from src.agents.wallpaper_generation.domain import WallpaperResult
        mock_wallpaper_result = WallpaperResult(
            success=True,
            file_path=Path("/tmp/wallpaper.png"),
        )
        mock_gen_agent.return_value.generate_wallpaper.return_value = mock_wallpaper_result
        
        from src.agents.wallpaper_application.domain import ApplicationResult
        mock_app_result = ApplicationResult(success=True)
        mock_app_agent.return_value.apply_wallpaper.return_value = mock_app_result
        
        mock_log = MagicMock()
        mock_logger.return_value = mock_log
        
        orchestrator = WallpaperOrchestrator()
        result = orchestrator.run()
        
        # Verify logging was called
        assert mock_log.info.called or mock_log.debug.called
    
    def test_orchestrator_result_to_dict(self):
        """Test converting orchestrator result to dictionary."""
        result = OrchestrationResult(
            status=OrchestrationStatus.SUCCESS,
            selected_theme={"name": "Diwali"},
            wallpaper_path=Path("/tmp/wallpaper.png"),
        )
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict["status"] == "success"
        assert result_dict["wallpaper_path"] == "/tmp/wallpaper.png"
    
    def test_orchestration_status_enum(self):
        """Test OrchestrationStatus enum values."""
        assert OrchestrationStatus.SUCCESS.value == "success"
        assert OrchestrationStatus.FAILED.value == "failed"
        assert OrchestrationStatus.PARTIAL.value == "partial"

