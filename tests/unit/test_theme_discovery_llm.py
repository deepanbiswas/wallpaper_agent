"""
Tests for LLM-enhanced theme extraction in Theme Discovery Agent.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from agents.theme_discovery.agent import ThemeDiscoveryAgent


class TestLLMThemeExtraction:
    """Test LLM-based theme extraction."""
    
    def test_format_themes_with_llm_success(self):
        """Test successful LLM-based theme extraction."""
        mock_llm = MagicMock()
        mock_llm.generate_text.return_value = '''
        [
          {
            "name": "Diwali",
            "description": "Festival of lights celebrated in India",
            "relevance": 95,
            "dates": "October/November 2024"
          },
          {
            "name": "New Year",
            "description": "Global celebration marking new year",
            "relevance": 85,
            "dates": "January 2024"
          }
        ]
        '''
        
        agent = ThemeDiscoveryAgent(llm_client=mock_llm)
        
        search_results = [
            {"title": "Diwali 2024 celebrations", "body": "Diwali is a major festival..."},
            {"title": "New Year 2024", "body": "New Year celebrations worldwide..."},
        ]
        
        themes = agent._format_themes_with_llm(search_results, "indian_cultural")
        
        assert len(themes) == 2
        assert themes[0]["name"] == "Diwali"
        assert themes[0]["description"] == "Festival of lights celebrated in India"
        assert themes[0]["metadata"]["relevance"] == 95
        assert themes[0]["type"] == "indian_cultural"
        mock_llm.generate_text.assert_called_once()
    
    def test_format_themes_with_llm_fallback(self):
        """Test fallback to simple extraction when LLM fails."""
        mock_llm = MagicMock()
        mock_llm.generate_text.side_effect = Exception("API Error")
        
        agent = ThemeDiscoveryAgent(llm_client=mock_llm)
        
        search_results = [
            {"title": "Diwali 2024", "body": "Festival of lights"},
        ]
        
        themes = agent._format_themes_with_llm(search_results, "indian_cultural")
        
        # Should fallback to simple extraction
        assert len(themes) == 1
        assert themes[0]["name"] == "Diwali 2024"
        assert themes[0]["type"] == "indian_cultural"
    
    def test_format_themes_with_llm_invalid_json(self):
        """Test handling of invalid JSON from LLM."""
        mock_llm = MagicMock()
        mock_llm.generate_text.return_value = "This is not JSON"
        
        agent = ThemeDiscoveryAgent(llm_client=mock_llm)
        
        search_results = [
            {"title": "Diwali", "body": "Festival"},
        ]
        
        themes = agent._format_themes_with_llm(search_results, "indian_cultural")
        
        # Should fallback to simple extraction
        assert len(themes) == 1
        assert themes[0]["name"] == "Diwali"
    
    def test_format_themes_with_llm_no_llm_client(self):
        """Test that simple extraction is used when no LLM client."""
        agent = ThemeDiscoveryAgent(llm_client=None)
        
        search_results = [
            {"title": "Diwali", "body": "Festival of lights"},
        ]
        
        themes = agent._format_themes_with_llm(search_results, "indian_cultural")
        
        # Should use simple extraction
        assert len(themes) == 1
        assert themes[0]["name"] == "Diwali"
    
    def test_format_themes_with_llm_relevance_filtering(self):
        """Test that low-relevance themes are filtered out."""
        mock_llm = MagicMock()
        mock_llm.generate_text.return_value = '''
        [
          {"name": "Diwali", "description": "Festival", "relevance": 95},
          {"name": "Old Event", "description": "Past event", "relevance": 30}
        ]
        '''
        
        agent = ThemeDiscoveryAgent(llm_client=mock_llm)
        agent.min_relevance_score = 50  # Filter themes below 50
        
        search_results = [
            {"title": "Diwali", "body": "Festival"},
            {"title": "Old Event", "body": "Past"},
        ]
        
        themes = agent._format_themes_with_llm(search_results, "indian_cultural")
        
        # Should filter out low-relevance theme
        assert len(themes) == 1
        assert themes[0]["name"] == "Diwali"
    
    def test_format_themes_with_llm_metadata_extraction(self):
        """Test that metadata is extracted from LLM response."""
        mock_llm = MagicMock()
        mock_llm.generate_text.return_value = '''
        [
          {
            "name": "Diwali",
            "description": "Festival of lights",
            "relevance": 95,
            "significance": "high",
            "visual_appeal": "high",
            "visual_elements": ["lights", "fireworks"],
            "colors": ["#FFD700", "#FF4500"]
          }
        ]
        '''
        
        agent = ThemeDiscoveryAgent(llm_client=mock_llm)
        
        search_results = [
            {"title": "Diwali", "body": "Festival"},
        ]
        
        themes = agent._format_themes_with_llm(search_results, "indian_cultural")
        
        assert themes[0]["metadata"]["significance"] == "high"
        assert themes[0]["metadata"]["visual_appeal"] == "high"
        assert "lights" in themes[0]["metadata"]["visual_elements"]
    
    def test_discover_themes_uses_llm_extraction(self):
        """Test that discover_themes uses LLM extraction when available."""
        mock_llm = MagicMock()
        mock_llm.generate_text.return_value = '''
        [
          {"name": "Diwali", "description": "Festival", "relevance": 95}
        ]
        '''
        
        agent = ThemeDiscoveryAgent(llm_client=mock_llm)
        
        with patch.object(agent, 'search_indian_cultural_events', return_value=[
            {"title": "Diwali", "body": "Festival"}
        ]):
            with patch.object(agent, 'search_indian_achievements', return_value=[]):
                with patch.object(agent, 'search_global_themes', return_value=[]):
                    themes = agent.discover_themes()
                    
                    # Should use LLM extraction
                    assert len(themes) > 0
                    assert mock_llm.generate_text.called

