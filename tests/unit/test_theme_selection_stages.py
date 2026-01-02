"""
Tests for theme ranking stages.
"""
import pytest
from unittest.mock import Mock, MagicMock
from agents.theme_selection.domain import Theme
from agents.theme_selection.stages import (
    InitialScoringStage,
    LLMRankingStage,
    NormalizationStage,
    CombinedScoringStage,
    FinalSortStage,
)


class TestInitialScoringStage:
    """Test InitialScoringStage."""
    
    def test_initial_scoring_indian_cultural(self):
        """Test scoring Indian cultural themes."""
        stage = InitialScoringStage(prefer_indian_culture=True)
        themes = [
            Theme(name="Diwali", type="indian_cultural"),
            Theme(name="New Year", type="global"),
        ]
        
        result = stage.apply(themes)
        
        assert result[0].base_score == 100.0 * 1.5  # 150.0
        assert result[1].base_score == 40.0
    
    def test_initial_scoring_indian_achievement(self):
        """Test scoring Indian achievement themes."""
        stage = InitialScoringStage(prefer_indian_achievements=True)
        themes = [
            Theme(name="ISRO Launch", type="indian_achievement"),
        ]
        
        result = stage.apply(themes)
        
        assert result[0].base_score == 80.0 * 1.3  # 104.0
    
    def test_initial_scoring_no_preferences(self):
        """Test scoring without preferences."""
        stage = InitialScoringStage(
            prefer_indian_culture=False,
            prefer_indian_achievements=False,
        )
        themes = [
            Theme(name="Diwali", type="indian_cultural"),
        ]
        
        result = stage.apply(themes)
        
        assert result[0].base_score == 100.0  # No multiplier


class TestLLMRankingStage:
    """Test LLMRankingStage."""
    
    def test_llm_ranking_with_client(self):
        """Test LLM ranking with LLM client."""
        mock_llm = MagicMock()
        mock_llm.generate_text.return_value = '{"0": 85, "1": 72}'
        
        stage = LLMRankingStage(llm_client=mock_llm)
        themes = [
            Theme(name="Theme 1", type="indian_cultural"),
            Theme(name="Theme 2", type="global"),
        ]
        
        result = stage.apply(themes)
        
        assert result[0].llm_score == 85.0
        assert result[1].llm_score == 72.0
        mock_llm.generate_text.assert_called_once()
    
    def test_llm_ranking_no_client(self):
        """Test LLM ranking without LLM client."""
        stage = LLMRankingStage(llm_client=None)
        themes = [Theme(name="Theme 1", type="indian_cultural")]
        
        result = stage.apply(themes)
        
        assert result[0].llm_score == 50.0  # Default score
    
    def test_llm_ranking_error_handling(self):
        """Test LLM ranking error handling."""
        mock_llm = MagicMock()
        mock_llm.generate_text.side_effect = Exception("API Error")
        
        stage = LLMRankingStage(llm_client=mock_llm)
        themes = [Theme(name="Theme 1", type="indian_cultural")]
        
        result = stage.apply(themes)
        
        assert result[0].llm_score == 50.0  # Default on error
    
    def test_llm_ranking_empty_themes(self):
        """Test LLM ranking with empty themes list."""
        mock_llm = MagicMock()
        stage = LLMRankingStage(llm_client=mock_llm)
        
        result = stage.apply([])
        
        assert result == []
        mock_llm.generate_text.assert_not_called()


class TestNormalizationStage:
    """Test NormalizationStage."""
    
    def test_normalization(self):
        """Test score normalization."""
        stage = NormalizationStage()
        themes = [
            Theme(name="Theme 1", base_score=200.0, llm_score=100.0),
            Theme(name="Theme 2", base_score=100.0, llm_score=50.0),
        ]
        
        result = stage.apply(themes)
        
        assert result[0].base_score == 1.0  # 200/200
        assert result[0].llm_score == 1.0  # 100/100
        assert result[1].base_score == 0.5  # 100/200
        assert result[1].llm_score == 0.5  # 50/100
    
    def test_normalization_zero_scores(self):
        """Test normalization with zero scores."""
        stage = NormalizationStage()
        themes = [
            Theme(name="Theme 1", base_score=0.0, llm_score=0.0),
        ]
        
        result = stage.apply(themes)
        
        assert result[0].base_score == 0.0
        assert result[0].llm_score == 0.0


class TestCombinedScoringStage:
    """Test CombinedScoringStage."""
    
    def test_combined_scoring(self):
        """Test combining base and LLM scores."""
        stage = CombinedScoringStage(base_weight=0.4, llm_weight=0.6)
        themes = [
            Theme(name="Theme 1", base_score=1.0, llm_score=0.8),
        ]
        
        result = stage.apply(themes)
        
        # 1.0 * 0.4 + 0.8 * 0.6 = 0.4 + 0.48 = 0.88
        assert result[0].final_score == pytest.approx(0.88)
    
    def test_combined_scoring_custom_weights(self):
        """Test combined scoring with custom weights."""
        stage = CombinedScoringStage(base_weight=0.3, llm_weight=0.7)
        themes = [
            Theme(name="Theme 1", base_score=1.0, llm_score=0.5),
        ]
        
        result = stage.apply(themes)
        
        # 1.0 * 0.3 + 0.5 * 0.7 = 0.3 + 0.35 = 0.65
        assert result[0].final_score == pytest.approx(0.65)


class TestFinalSortStage:
    """Test FinalSortStage."""
    
    def test_final_sort(self):
        """Test final sorting by score."""
        stage = FinalSortStage()
        themes = [
            Theme(name="Theme 1", final_score=0.5),
            Theme(name="Theme 2", final_score=0.9),
            Theme(name="Theme 3", final_score=0.7),
        ]
        
        result = stage.apply(themes)
        
        assert result[0].name == "Theme 2"  # Highest score
        assert result[1].name == "Theme 3"
        assert result[2].name == "Theme 1"  # Lowest score
    
    def test_final_sort_empty(self):
        """Test sorting empty list."""
        stage = FinalSortStage()
        result = stage.apply([])
        assert result == []

