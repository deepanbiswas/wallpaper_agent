"""
Tests for Theme Selection Agent.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from agents.theme_selection.agent import ThemeSelectionAgent
from agents.theme_selection.domain import Theme
from agents.theme_selection.ranker import ThemeRanker
from agents.theme_selection.strategy import PipelineRankingStrategy
from agents.theme_selection.stages import (
    InitialScoringStage,
    NormalizationStage,
    FinalSortStage,
)


class TestThemeSelectionAgent:
    """Test Theme Selection Agent."""
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = ThemeSelectionAgent()
        
        assert agent is not None
        assert agent.ranker is not None
    
    def test_agent_initialization_with_custom_ranker(self):
        """Test agent initialization with custom ranker."""
        custom_ranker = Mock()
        agent = ThemeSelectionAgent(ranker=custom_ranker)
        
        assert agent.ranker == custom_ranker
    
    @patch('agents.theme_selection.agent.load_config')
    @patch('agents.theme_selection.agent.get_llm_config')
    def test_agent_initialization_with_llm(self, mock_llm_config, mock_config):
        """Test agent initialization with LLM client."""
        mock_config.return_value = Mock()
        mock_llm_config.return_value = {
            "provider": "anthropic",
            "anthropic_api_key": "test_key",
        }
        
        with patch('agents.theme_selection.agent.LLMClient') as mock_llm_class:
            agent = ThemeSelectionAgent()
            # LLM client should be initialized if API key is available
            # (actual initialization depends on config)
    
    def test_select_theme_empty_list(self):
        """Test selecting theme from empty list."""
        agent = ThemeSelectionAgent()
        result = agent.select_theme([])
        
        assert result is None
    
    def test_select_theme_single_theme(self):
        """Test selecting theme from single theme."""
        agent = ThemeSelectionAgent()
        themes = [
            {
                "name": "Diwali",
                "description": "Festival of Lights",
                "type": "indian_cultural",
                "source": "search",
            }
        ]
        
        result = agent.select_theme(themes)
        
        assert result is not None
        assert result["name"] == "Diwali"
        assert "style_guidelines" in result
    
    def test_select_theme_multiple_themes(self):
        """Test selecting best theme from multiple themes."""
        agent = ThemeSelectionAgent()
        themes = [
            {
                "name": "Global Theme",
                "description": "Global event",
                "type": "global",
                "source": "search",
            },
            {
                "name": "Diwali",
                "description": "Festival of Lights",
                "type": "indian_cultural",
                "source": "search",
            },
        ]
        
        result = agent.select_theme(themes)
        
        assert result is not None
        # Should select Indian cultural theme (higher priority)
        assert result["name"] == "Diwali"
        assert result["type"] == "indian_cultural"
    
    def test_select_theme_includes_scores(self):
        """Test that selected theme includes scoring information."""
        agent = ThemeSelectionAgent()
        themes = [
            {
                "name": "Test Theme",
                "description": "Test",
                "type": "indian_cultural",
                "source": "search",
            }
        ]
        
        result = agent.select_theme(themes)
        
        assert "final_score" in result
        assert "base_score" in result
        assert "llm_score" in result
    
    def test_select_theme_style_guidelines(self):
        """Test that selected theme includes style guidelines."""
        agent = ThemeSelectionAgent()
        themes = [
            {
                "name": "Test Theme",
                "description": "Test",
                "type": "indian_cultural",
                "source": "search",
            }
        ]
        
        result = agent.select_theme(themes)
        
        assert "style_guidelines" in result
        guidelines = result["style_guidelines"]
        assert "color_palette" in guidelines
        assert "key_elements" in guidelines
        assert "style_description" in guidelines
        assert "prompt" in guidelines
    
    @patch('agents.theme_selection.agent.LLMClient')
    def test_select_theme_with_llm_style_generation(self, mock_llm_class):
        """Test theme selection with LLM style generation."""
        mock_llm = MagicMock()
        mock_llm.generate_text.return_value = '{"color_palette": ["#000000"], "key_elements": ["test"], "style_description": "dark", "prompt": "test prompt"}'
        mock_llm_class.return_value = mock_llm
        
        agent = ThemeSelectionAgent(llm_client=mock_llm)
        themes = [
            {
                "name": "Test Theme",
                "description": "Test",
                "type": "indian_cultural",
                "source": "search",
            }
        ]
        
        result = agent.select_theme(themes)
        
        assert result is not None
        assert "style_guidelines" in result
        # LLM should be called for style generation
        # (may be called multiple times for ranking and style)

