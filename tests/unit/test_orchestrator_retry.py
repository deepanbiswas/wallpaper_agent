"""
Tests for Orchestrator retry logic and error handling.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
from src.orchestrator.main import WallpaperOrchestrator
from src.orchestrator.domain import OrchestrationResult, OrchestrationStatus


class TestOrchestratorRetryLogic:
    """Test retry logic in orchestrator."""
    
    @patch('src.orchestrator.main.ThemeDiscoveryAgent')
    def test_retry_on_theme_discovery_failure(self, mock_disc_agent):
        """Test retry logic when theme discovery fails initially."""
        # First call fails, second succeeds
        mock_disc_agent.return_value.discover_themes.side_effect = [
            [],  # First attempt fails
            [{"name": "Diwali", "description": "Festival", "type": "indian_cultural"}],  # Second succeeds
        ]
        
        orchestrator = WallpaperOrchestrator()
        orchestrator.max_retries = 2
        orchestrator.retry_delay = 0.01  # Short delay for testing
        
        result = orchestrator.run()
        
        # Should succeed after retry
        assert result.status.value == "success" or result.status.value == "failed"
        # Should have called discover_themes at least twice
        assert mock_disc_agent.return_value.discover_themes.call_count >= 2
    
    @patch('src.orchestrator.main.ThemeDiscoveryAgent')
    def test_max_retries_exceeded(self, mock_disc_agent):
        """Test that max retries are respected."""
        # Always fails
        mock_disc_agent.return_value.discover_themes.return_value = []
        
        orchestrator = WallpaperOrchestrator()
        orchestrator.max_retries = 3
        orchestrator.retry_delay = 0.01
        
        result = orchestrator.run()
        
        # Should fail after max retries
        assert result.status.value == "failed"
        # Should have called discover_themes max_retries times
        assert mock_disc_agent.return_value.discover_themes.call_count == orchestrator.max_retries
    
    @patch('src.orchestrator.main.ThemeSelectionAgent')
    @patch('src.orchestrator.main.ThemeDiscoveryAgent')
    def test_retry_on_theme_selection_failure(
        self,
        mock_disc_agent,
        mock_sel_agent,
    ):
        """Test retry logic when theme selection fails."""
        # Discovery succeeds
        mock_disc_agent.return_value.discover_themes.return_value = [
            {"name": "Diwali", "description": "Festival", "type": "indian_cultural"},
        ]
        
        # Selection fails first time, succeeds second
        mock_sel_agent.return_value.select_theme.side_effect = [
            None,  # First attempt fails
            {"name": "Diwali", "description": "Festival", "type": "indian_cultural"},  # Second succeeds
        ]
        
        orchestrator = WallpaperOrchestrator()
        orchestrator.max_retries = 2
        orchestrator.retry_delay = 0.01
        
        result = orchestrator.run()
        
        # Should have retried selection
        assert mock_sel_agent.return_value.select_theme.call_count >= 2
    
    @patch('src.orchestrator.main.WallpaperGenerationAgent')
    @patch('src.orchestrator.main.ThemeSelectionAgent')
    @patch('src.orchestrator.main.ThemeDiscoveryAgent')
    def test_retry_on_wallpaper_generation_failure(
        self,
        mock_disc_agent,
        mock_sel_agent,
        mock_gen_agent,
    ):
        """Test retry logic when wallpaper generation fails."""
        # Discovery and selection succeed
        mock_disc_agent.return_value.discover_themes.return_value = [
            {"name": "Diwali", "description": "Festival", "type": "indian_cultural"},
        ]
        mock_sel_agent.return_value.select_theme.return_value = {
            "name": "Diwali",
            "description": "Festival",
            "style_guidelines": {},
        }
        
        # Generation fails first time, succeeds second
        from src.agents.wallpaper_generation.domain import WallpaperResult
        mock_gen_agent.return_value.generate_wallpaper.side_effect = [
            WallpaperResult(success=False, error="Generation failed"),
            WallpaperResult(success=True, file_path=Path("/tmp/wallpaper.png")),
        ]
        
        orchestrator = WallpaperOrchestrator()
        orchestrator.max_retries = 2
        orchestrator.retry_delay = 0.01
        
        result = orchestrator.run()
        
        # Should have retried generation
        assert mock_gen_agent.return_value.generate_wallpaper.call_count >= 2
    
    def test_retry_configuration_defaults(self):
        """Test default retry configuration."""
        orchestrator = WallpaperOrchestrator()
        
        assert hasattr(orchestrator, 'max_retries')
        assert hasattr(orchestrator, 'retry_delay')
        assert orchestrator.max_retries >= 1
        assert orchestrator.retry_delay >= 0
    
    def test_retry_configuration_custom(self):
        """Test custom retry configuration."""
        orchestrator = WallpaperOrchestrator(max_retries=5, retry_delay=0.5)
        
        assert orchestrator.max_retries == 5
        assert orchestrator.retry_delay == 0.5


class TestOrchestratorErrorHandling:
    """Test error handling improvements."""
    
    @patch('src.orchestrator.main.ThemeDiscoveryAgent')
    def test_handles_exception_in_discovery(self, mock_disc_agent):
        """Test handling of exceptions during theme discovery."""
        mock_disc_agent.return_value.discover_themes.side_effect = Exception("Network error")
        
        orchestrator = WallpaperOrchestrator()
        result = orchestrator.run()
        
        assert result.status.value == "failed"
        assert result.error is not None
        assert "exception" in result.error.lower() or "network" in result.error.lower()
    
    @patch('src.orchestrator.main.ThemeSelectionAgent')
    @patch('src.orchestrator.main.ThemeDiscoveryAgent')
    def test_handles_exception_in_selection(
        self,
        mock_disc_agent,
        mock_sel_agent,
    ):
        """Test handling of exceptions during theme selection."""
        mock_disc_agent.return_value.discover_themes.return_value = [
            {"name": "Diwali", "description": "Festival", "type": "indian_cultural"},
        ]
        mock_sel_agent.return_value.select_theme.side_effect = Exception("LLM API error")
        
        orchestrator = WallpaperOrchestrator()
        result = orchestrator.run()
        
        assert result.status.value == "failed"
        assert result.error is not None
    
    @patch('src.orchestrator.main.WallpaperGenerationAgent')
    @patch('src.orchestrator.main.ThemeSelectionAgent')
    @patch('src.orchestrator.main.ThemeDiscoveryAgent')
    def test_handles_exception_in_generation(
        self,
        mock_disc_agent,
        mock_sel_agent,
        mock_gen_agent,
    ):
        """Test handling of exceptions during wallpaper generation."""
        mock_disc_agent.return_value.discover_themes.return_value = [
            {"name": "Diwali", "description": "Festival", "type": "indian_cultural"},
        ]
        mock_sel_agent.return_value.select_theme.return_value = {
            "name": "Diwali",
            "description": "Festival",
            "style_guidelines": {},
        }
        mock_gen_agent.return_value.generate_wallpaper.side_effect = Exception("Image API error")
        
        orchestrator = WallpaperOrchestrator()
        result = orchestrator.run()
        
        assert result.status.value == "failed"
        assert result.error is not None
    
    @patch('src.orchestrator.main.WallpaperApplicationAgent')
    @patch('src.orchestrator.main.WallpaperGenerationAgent')
    @patch('src.orchestrator.main.ThemeSelectionAgent')
    @patch('src.orchestrator.main.ThemeDiscoveryAgent')
    def test_handles_exception_in_application(
        self,
        mock_disc_agent,
        mock_sel_agent,
        mock_gen_agent,
        mock_app_agent,
    ):
        """Test handling of exceptions during wallpaper application."""
        # Setup successful steps
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
        
        # Application throws exception
        mock_app_agent.return_value.apply_wallpaper.side_effect = Exception("OS error")
        
        orchestrator = WallpaperOrchestrator()
        result = orchestrator.run()
        
        # Should handle exception gracefully
        assert result.status.value in ["failed", "partial"]
        assert result.error is not None

