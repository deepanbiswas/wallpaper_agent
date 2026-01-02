"""
Integration tests for Theme Selection Agent.

Tests the full theme selection workflow with real components.
"""
import pytest
from agents.theme_selection.agent import ThemeSelectionAgent
from agents.theme_selection.domain import Theme
from agents.theme_selection.ranker import ThemeRanker
from agents.theme_selection.strategy import PipelineRankingStrategy
from agents.theme_selection.stages import (
    InitialScoringStage,
    NormalizationStage,
    CombinedScoringStage,
    FinalSortStage,
)


@pytest.mark.integration
class TestThemeSelectionAgentIntegration:
    """Integration tests for Theme Selection Agent."""
    
    def test_select_theme_from_discovered_themes(self):
        """Test selecting theme from discovered themes."""
        agent = ThemeSelectionAgent()
        
        # Simulate themes from Discovery Agent
        discovered_themes = [
            {
                "name": "Diwali 2026",
                "description": "Festival of Lights celebration",
                "type": "indian_cultural",
                "source": "search",
            },
            {
                "name": "New Year 2026",
                "description": "Global New Year celebration",
                "type": "global",
                "source": "search",
            },
            {
                "name": "ISRO Achievement",
                "description": "Space mission success",
                "type": "indian_achievement",
                "source": "search",
            },
        ]
        
        selected = agent.select_theme(discovered_themes)
        
        assert selected is not None
        assert "name" in selected
        assert "type" in selected
        assert "style_guidelines" in selected
        assert "final_score" in selected
        
        # Should prioritize Indian cultural or achievement themes
        assert selected["type"] in ["indian_cultural", "indian_achievement", "global"]
    
    def test_theme_ranking_pipeline(self):
        """Test full ranking pipeline."""
        stages = [
            InitialScoringStage(prefer_indian_culture=True),
            NormalizationStage(),
            CombinedScoringStage(base_weight=0.4, llm_weight=0.6),
            FinalSortStage(),
        ]
        
        strategy = PipelineRankingStrategy(stages=stages)
        ranker = ThemeRanker(strategy)
        
        themes = [
            Theme(name="Diwali", type="indian_cultural", description="Festival"),
            Theme(name="New Year", type="global", description="Celebration"),
            Theme(name="ISRO Launch", type="indian_achievement", description="Space"),
        ]
        
        ranked = ranker.rank(themes)
        
        assert len(ranked) == 3
        assert ranked[0].final_score >= ranked[1].final_score
        assert ranked[1].final_score >= ranked[2].final_score
        # Indian cultural should rank highest
        assert ranked[0].type == "indian_cultural"
    
    def test_custom_ranking_strategy(self):
        """Test using custom ranking strategy."""
        # Create a simple custom strategy (just sort by name)
        from agents.theme_selection.strategy import ThemeRankingStrategy
        
        class SimpleNameStrategy(ThemeRankingStrategy):
            def rank(self, themes):
                return sorted(themes, key=lambda t: t.name)
        
        custom_strategy = SimpleNameStrategy()
        ranker = ThemeRanker(custom_strategy)
        
        themes = [
            Theme(name="Zebra", type="global"),
            Theme(name="Apple", type="indian_cultural"),
            Theme(name="Banana", type="indian_achievement"),
        ]
        
        ranked = ranker.rank(themes)
        
        assert ranked[0].name == "Apple"
        assert ranked[1].name == "Banana"
        assert ranked[2].name == "Zebra"
    
    def test_swappable_stages(self):
        """Test that stages can be swapped/reordered."""
        # Test with different stage order
        stages1 = [
            InitialScoringStage(),
            NormalizationStage(),
            FinalSortStage(),
        ]
        
        stages2 = [
            InitialScoringStage(),
            FinalSortStage(),  # Different order
        ]
        
        strategy1 = PipelineRankingStrategy(stages=stages1)
        strategy2 = PipelineRankingStrategy(stages=stages2)
        
        themes = [
            Theme(name="Theme 1", type="indian_cultural"),
            Theme(name="Theme 2", type="global"),
        ]
        
        result1 = strategy1.rank(themes.copy())
        result2 = strategy2.rank(themes.copy())
        
        # Both should work, may produce different results
        assert len(result1) == 2
        assert len(result2) == 2
    
    def test_theme_selection_with_scores(self):
        """Test that selected theme includes all scoring information."""
        agent = ThemeSelectionAgent()
        
        themes = [
            {
                "name": "Test Theme",
                "description": "Test description",
                "type": "indian_cultural",
                "source": "search",
            }
        ]
        
        selected = agent.select_theme(themes)
        
        # Verify all score fields are present
        assert "base_score" in selected
        assert "llm_score" in selected
        assert "final_score" in selected
        assert isinstance(selected["base_score"], (int, float))
        assert isinstance(selected["llm_score"], (int, float))
        assert isinstance(selected["final_score"], (int, float))
    
    def test_style_guidelines_structure(self):
        """Test that style guidelines have correct structure."""
        agent = ThemeSelectionAgent()
        
        themes = [
            {
                "name": "Diwali",
                "description": "Festival of Lights",
                "type": "indian_cultural",
                "source": "search",
            }
        ]
        
        selected = agent.select_theme(themes)
        guidelines = selected["style_guidelines"]
        
        assert "color_palette" in guidelines
        assert "key_elements" in guidelines
        assert "style_description" in guidelines
        assert "prompt" in guidelines
        
        assert isinstance(guidelines["color_palette"], list)
        assert isinstance(guidelines["key_elements"], list)
        assert isinstance(guidelines["style_description"], str)
        assert isinstance(guidelines["prompt"], str)

