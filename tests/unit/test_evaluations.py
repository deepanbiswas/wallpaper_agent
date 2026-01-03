"""
Tests for Evaluation Framework.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
from datetime import datetime
from evaluations.evaluator import AgentEvaluator
from evaluations.metrics import EvaluationResult, EvaluationMetrics


class TestAgentEvaluator:
    """Test Agent Evaluator."""
    
    def test_evaluator_initialization(self):
        """Test evaluator initialization."""
        evaluator = AgentEvaluator()
        assert evaluator is not None
    
    def test_evaluate_discovery_agent(self):
        """Test discovery agent evaluation."""
        evaluator = AgentEvaluator(llm_client=None)
        
        themes = [
            {
                "name": "Diwali",
                "description": "Festival of lights",
                "type": "indian_cultural",
                "metadata": {"relevance": 95},
            },
            {
                "name": "New Year",
                "description": "Global celebration",
                "type": "global",
                "metadata": {"relevance": 85},
            },
        ]
        
        result = evaluator.evaluate_discovery_agent(themes)
        
        assert result.agent_name == "ThemeDiscoveryAgent"
        assert "relevance" in result.metrics
        assert "quality" in result.metrics
        assert "deduplication" in result.metrics
        assert "coverage" in result.metrics
        assert result.overall_score >= 0.0
    
    def test_evaluate_selection_agent(self):
        """Test selection agent evaluation."""
        evaluator = AgentEvaluator(llm_client=None)
        
        selected_theme = {
            "name": "Diwali",
            "type": "indian_cultural",
            "style_guidelines": {
                "prompt": "minimalistic dark diwali",
                "color_palette": ["#FFD700"],
            },
        }
        
        all_themes = [
            {"name": "Diwali", "type": "indian_cultural"},
            {"name": "New Year", "type": "global"},
        ]
        
        result = evaluator.evaluate_selection_agent(selected_theme, all_themes)
        
        assert result.agent_name == "ThemeSelectionAgent"
        assert "selection_accuracy" in result.metrics
        assert "preference_adherence" in result.metrics
        assert "style_quality" in result.metrics
    
    def test_evaluate_generation_agent(self, tmp_path):
        """Test generation agent evaluation."""
        evaluator = AgentEvaluator(llm_client=None)
        
        # Create a dummy image
        image_path = tmp_path / "test_wallpaper.png"
        image_path.write_bytes(b'\x89PNG\r\n\x1a\n' + b'\x00' * 1000)
        
        theme = {"name": "Diwali", "description": "Festival"}
        
        result = evaluator.evaluate_generation_agent(image_path, theme)
        
        assert result.agent_name == "WallpaperGenerationAgent"
        assert "image_quality" in result.metrics
        assert "theme_adherence" in result.metrics
        assert "dark_theme_compliance" in result.metrics
    
    def test_evaluate_application_agent(self):
        """Test application agent evaluation."""
        evaluator = AgentEvaluator()
        
        result = evaluator.evaluate_application_agent(
            success=True,
            desktop_index=1,
            desktop_count=2,
        )
        
        assert result.agent_name == "WallpaperApplicationAgent"
        assert "application_success" in result.metrics
        assert result.metrics["application_success"].score == 100.0
    
    def test_evaluate_relevance_with_llm(self):
        """Test relevance evaluation with LLM."""
        from evaluations.discovery_evaluator import DiscoveryEvaluator
        
        mock_llm = MagicMock()
        mock_llm.generate_text.return_value = '{"average_relevance": 85.5}'
        
        evaluator = DiscoveryEvaluator(llm_client=mock_llm)
        
        themes = [
            {"name": "Diwali", "description": "Festival"},
        ]
        
        week_context = {"month_name": "October", "year": 2024}
        score = evaluator._evaluate_relevance(themes, week_context)
        
        assert score == 85.5
        mock_llm.generate_text.assert_called_once()
    
    def test_evaluate_quality(self):
        """Test quality evaluation."""
        from evaluations.discovery_evaluator import DiscoveryEvaluator
        
        evaluator = DiscoveryEvaluator()
        
        themes = [
            {
                "name": "Diwali",
                "description": "Festival of lights celebrated in India",
                "metadata": {"relevance": 95, "significance": "high"},
            },
        ]
        
        score = evaluator._evaluate_quality(themes)
        
        assert 0.0 <= score <= 100.0
        assert score > 50.0  # Should be decent quality
    
    def test_evaluate_deduplication(self):
        """Test deduplication evaluation."""
        from evaluations.discovery_evaluator import DiscoveryEvaluator
        
        evaluator = DiscoveryEvaluator()
        
        themes = [
            {"name": "Diwali"},
            {"name": "New Year"},
            {"name": "diwali"},  # Duplicate (case-insensitive)
        ]
        
        score = evaluator._evaluate_deduplication(themes)
        
        # Should detect some duplication
        assert 0.0 <= score <= 100.0
    
    def test_evaluate_coverage(self):
        """Test coverage evaluation."""
        from evaluations.discovery_evaluator import DiscoveryEvaluator
        
        evaluator = DiscoveryEvaluator()
        
        themes = [
            {"type": "indian_cultural"},
            {"type": "indian_achievement"},
            {"type": "global"},
        ]
        
        score = evaluator._evaluate_coverage(themes)
        
        # Should have good coverage (all 3 types)
        assert score >= 90.0
    
    def test_evaluation_result_to_dict(self):
        """Test converting evaluation result to dictionary."""
        result = EvaluationResult(
            agent_name="TestAgent",
            timestamp=datetime.now(),
            overall_score=85.0,
            metrics={
                "test_metric": EvaluationMetrics(
                    score=85.0,
                    threshold=80.0,
                    passed=True,
                ),
            },
        )
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict["agent_name"] == "TestAgent"
        assert result_dict["overall_score"] == 85.0
        assert "test_metric" in result_dict["metrics"]

