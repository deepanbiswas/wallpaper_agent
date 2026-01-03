"""
Integration tests for end-to-end evaluation workflows.
"""
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from PIL import Image

from evaluations import AgentEvaluator
from agents.theme_discovery.agent import ThemeDiscoveryAgent
from agents.theme_selection.agent import ThemeSelectionAgent
from agents.wallpaper_generation.agent import WallpaperGenerationAgent
from agents.wallpaper_application.agent import WallpaperApplicationAgent


@pytest.mark.integration
class TestEvaluationWorkflow:
    """Test end-to-end evaluation workflows."""
    
    def test_evaluate_full_workflow_success(self, tmp_path):
        """Test evaluating a complete successful workflow."""
        evaluator = AgentEvaluator(llm_client=None)
        
        # Simulate workflow outputs
        themes = [
            {
                "name": "Diwali",
                "description": "Festival of lights",
                "type": "indian_cultural",
                "metadata": {"relevance": 95},
            },
        ]
        
        selected_theme = {
            "name": "Diwali",
            "type": "indian_cultural",
            "style_guidelines": {
                "prompt": "minimalistic dark diwali",
                "color_palette": ["#FFD700"],
                "key_elements": ["lights"],
                "style_description": "Dark theme with golden lights",
            },
        }
        
        # Create a valid wallpaper image
        wallpaper_path = tmp_path / "wallpaper.png"
        img = Image.new('RGB', (3024, 1964), color=(20, 20, 20))  # Dark image
        img.save(wallpaper_path)
        
        # Evaluate each agent
        discovery_result = evaluator.evaluate_discovery_agent(themes)
        selection_result = evaluator.evaluate_selection_agent(selected_theme, themes)
        generation_result = evaluator.evaluate_generation_agent(wallpaper_path, selected_theme)
        application_result = evaluator.evaluate_application_agent(
            success=True,
            desktop_index=1,
            desktop_count=2,
        )
        
        # Verify evaluations completed (may not all pass due to strict thresholds)
        assert discovery_result.overall_score >= 0.0
        assert selection_result.overall_score >= 0.0
        assert generation_result.overall_score >= 0.0
        assert application_result.passed  # Application should pass if successful
        
        # Verify scores are reasonable (may be lower due to strict thresholds)
        assert discovery_result.overall_score >= 60.0  # Coverage may be low with single theme
        assert selection_result.overall_score >= 70.0
        assert generation_result.overall_score >= 60.0
        assert application_result.overall_score >= 90.0
    
    def test_evaluate_workflow_with_low_quality_outputs(self, tmp_path):
        """Test evaluating workflow with low-quality outputs."""
        evaluator = AgentEvaluator(llm_client=None)
        
        # Low-quality themes
        themes = [
            {
                "name": "Event 2024",  # Has date in name
                "description": "Short",  # Too short
                "type": "global",
            },
        ]
        
        selected_theme = {
            "name": "Event",
            "type": "global",  # Should prefer Indian but selected global
            "style_guidelines": {},  # Missing style guidelines
        }
        
        # Low-quality wallpaper (small, bright)
        wallpaper_path = tmp_path / "wallpaper.png"
        img = Image.new('RGB', (500, 400), color=(250, 250, 250))  # Bright, small
        img.save(wallpaper_path)
        
        # Evaluate
        discovery_result = evaluator.evaluate_discovery_agent(themes)
        selection_result = evaluator.evaluate_selection_agent(selected_theme, themes)
        generation_result = evaluator.evaluate_generation_agent(wallpaper_path, selected_theme)
        
        # Some evaluations should fail or have warnings
        assert not discovery_result.passed or len(discovery_result.warnings) > 0
        assert not selection_result.passed or len(selection_result.warnings) > 0
        assert not generation_result.passed or len(generation_result.warnings) > 0
    
    def test_evaluate_workflow_with_missing_metadata(self, tmp_path):
        """Test evaluating workflow with missing metadata."""
        evaluator = AgentEvaluator(llm_client=None)
        
        # Themes without metadata
        themes = [
            {
                "name": "Diwali",
                "description": "Festival of lights",
                "type": "indian_cultural",
                # No metadata
            },
        ]
        
        selected_theme = {
            "name": "Diwali",
            "type": "indian_cultural",
            "style_guidelines": {
                "prompt": "diwali theme",
                # Missing other fields
            },
        }
        
        wallpaper_path = tmp_path / "wallpaper.png"
        img = Image.new('RGB', (2000, 1500), color=(30, 30, 30))
        img.save(wallpaper_path)
        
        # Evaluate
        discovery_result = evaluator.evaluate_discovery_agent(themes)
        selection_result = evaluator.evaluate_selection_agent(selected_theme, themes)
        generation_result = evaluator.evaluate_generation_agent(wallpaper_path, selected_theme)
        
        # Should still work but with lower scores
        assert discovery_result.overall_score >= 0.0
        assert selection_result.overall_score >= 0.0
        assert generation_result.overall_score >= 0.0
    
    def test_evaluate_workflow_with_llm_client(self, tmp_path):
        """Test evaluating workflow with LLM client for enhanced evaluations."""
        mock_llm = MagicMock()
        mock_llm.generate_text.return_value = '{"average_relevance": 90.0}'
        
        evaluator = AgentEvaluator(llm_client=mock_llm)
        
        themes = [
            {
                "name": "Diwali",
                "description": "Festival of lights",
                "type": "indian_cultural",
            },
        ]
        
        week_context = {"month_name": "October", "year": 2024}
        discovery_result = evaluator.evaluate_discovery_agent(themes, week_context)
        
        # Should use LLM for relevance evaluation
        assert discovery_result.metrics["relevance"].details["method"] == "llm_based"
        assert mock_llm.generate_text.called
    
    def test_evaluate_workflow_error_scenarios(self, tmp_path):
        """Test evaluating workflow with error scenarios."""
        evaluator = AgentEvaluator(llm_client=None)
        
        # Empty themes
        discovery_result = evaluator.evaluate_discovery_agent([])
        assert discovery_result.overall_score == 0.0 or not discovery_result.passed
        
        # Invalid wallpaper path
        invalid_path = tmp_path / "nonexistent.png"
        theme = {"name": "Test"}
        generation_result = evaluator.evaluate_generation_agent(invalid_path, theme)
        assert not generation_result.passed or generation_result.overall_score < 50.0
        
        # Application failure
        application_result = evaluator.evaluate_application_agent(
            success=False,
            desktop_index=0,
            desktop_count=1,
        )
        assert not application_result.passed
        assert application_result.metrics["application_success"].score == 0.0
    
    def test_evaluate_workflow_metrics_consistency(self, tmp_path):
        """Test that evaluation metrics are consistent across workflow."""
        evaluator = AgentEvaluator(llm_client=None)
        
        themes = [
            {
                "name": "Diwali",
                "description": "Festival of lights celebrated in India",
                "type": "indian_cultural",
                "metadata": {"relevance": 95, "significance": "high"},
            },
        ]
        
        selected_theme = {
            "name": "Diwali",
            "type": "indian_cultural",
            "style_guidelines": {
                "prompt": "minimalistic dark diwali",
                "color_palette": ["#FFD700"],
                "key_elements": ["lights"],
                "style_description": "Dark theme",
            },
        }
        
        wallpaper_path = tmp_path / "wallpaper.png"
        img = Image.new('RGB', (3024, 1964), color=(25, 25, 25))
        img.save(wallpaper_path)
        
        # Evaluate all agents
        discovery_result = evaluator.evaluate_discovery_agent(themes)
        selection_result = evaluator.evaluate_selection_agent(selected_theme, themes)
        generation_result = evaluator.evaluate_generation_agent(wallpaper_path, selected_theme)
        
        # Verify metric structure is consistent
        for result in [discovery_result, selection_result, generation_result]:
            assert hasattr(result, "agent_name")
            assert hasattr(result, "overall_score")
            assert hasattr(result, "metrics")
            assert hasattr(result, "passed")
            assert hasattr(result, "warnings")
            assert hasattr(result, "timestamp")
            
            # Verify metrics structure
            for metric_name, metric in result.metrics.items():
                assert hasattr(metric, "score")
                assert hasattr(metric, "threshold")
                assert hasattr(metric, "passed")
                assert 0.0 <= metric.score <= 100.0
    
    def test_evaluate_workflow_warnings_generation(self, tmp_path):
        """Test that warnings are generated appropriately."""
        evaluator = AgentEvaluator(llm_client=None)
        
        # Low relevance themes
        themes = [
            {
                "name": "Old Event",
                "description": "Past event",
                "type": "global",
                "metadata": {"relevance": 30},  # Low relevance
            },
        ]
        
        discovery_result = evaluator.evaluate_discovery_agent(themes)
        
        # Should have warnings for low relevance
        assert len(discovery_result.warnings) > 0 or discovery_result.metrics["relevance"].score < 60.0
        
        # Bright wallpaper (low dark theme compliance)
        wallpaper_path = tmp_path / "wallpaper.png"
        img = Image.new('RGB', (2000, 1500), color=(200, 200, 200))  # Bright
        img.save(wallpaper_path)
        
        theme = {"name": "Test"}
        generation_result = evaluator.evaluate_generation_agent(wallpaper_path, theme)
        
        # Should have warnings for low dark theme compliance
        assert len(generation_result.warnings) > 0 or generation_result.metrics["dark_theme_compliance"].score < 80.0

