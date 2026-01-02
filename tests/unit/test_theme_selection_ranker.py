"""
Tests for ThemeRanker.
"""
import pytest
from unittest.mock import Mock
from agents.theme_selection.domain import Theme
from agents.theme_selection.ranker import ThemeRanker
from agents.theme_selection.strategy import PipelineRankingStrategy
from agents.theme_selection.stages import InitialScoringStage, FinalSortStage


class TestThemeRanker:
    """Test ThemeRanker."""
    
    def test_ranker_initialization(self):
        """Test ranker initialization."""
        strategy = PipelineRankingStrategy(stages=[InitialScoringStage()])
        ranker = ThemeRanker(strategy)
        
        assert ranker.strategy == strategy
    
    def test_ranker_rank(self):
        """Test ranking themes."""
        stages = [
            InitialScoringStage(),
            FinalSortStage(),
        ]
        strategy = PipelineRankingStrategy(stages=stages)
        ranker = ThemeRanker(strategy)
        
        themes = [
            Theme(name="Theme 1", type="indian_cultural"),
            Theme(name="Theme 2", type="global"),
        ]
        
        result = ranker.rank(themes)
        
        assert len(result) == 2
        # Indian cultural should rank higher
        assert result[0].type == "indian_cultural"
    
    def test_ranker_set_strategy(self):
        """Test changing strategy at runtime."""
        strategy1 = PipelineRankingStrategy(stages=[InitialScoringStage()])
        strategy2 = PipelineRankingStrategy(stages=[FinalSortStage()])
        
        ranker = ThemeRanker(strategy1)
        assert ranker.strategy == strategy1
        
        ranker.set_strategy(strategy2)
        assert ranker.strategy == strategy2

