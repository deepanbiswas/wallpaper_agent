"""
Tests for theme ranking strategies.
"""
import pytest
from unittest.mock import Mock
from agents.theme_selection.domain import Theme
from agents.theme_selection.strategy import PipelineRankingStrategy
from agents.theme_selection.stages import (
    InitialScoringStage,
    NormalizationStage,
    FinalSortStage,
)


class TestPipelineRankingStrategy:
    """Test PipelineRankingStrategy."""
    
    def test_pipeline_strategy(self):
        """Test pipeline strategy with multiple stages."""
        stages = [
            InitialScoringStage(),
            NormalizationStage(),
            FinalSortStage(),
        ]
        strategy = PipelineRankingStrategy(stages=stages)
        
        themes = [
            Theme(name="Theme 1", type="indian_cultural"),
            Theme(name="Theme 2", type="global"),
        ]
        
        result = strategy.rank(themes)
        
        # Should be sorted by final score (after normalization)
        assert len(result) == 2
        assert result[0].final_score >= result[1].final_score
    
    def test_pipeline_strategy_empty_stages(self):
        """Test pipeline strategy with no stages."""
        strategy = PipelineRankingStrategy(stages=[])
        themes = [Theme(name="Theme 1")]
        
        result = strategy.rank(themes)
        
        assert result == themes  # No changes
    
    def test_pipeline_strategy_single_stage(self):
        """Test pipeline strategy with single stage."""
        mock_stage = Mock()
        mock_stage.apply.return_value = [Theme(name="Modified")]
        
        strategy = PipelineRankingStrategy(stages=[mock_stage])
        themes = [Theme(name="Original")]
        
        result = strategy.rank(themes)
        
        assert len(result) == 1
        assert result[0].name == "Modified"
        mock_stage.apply.assert_called_once()

