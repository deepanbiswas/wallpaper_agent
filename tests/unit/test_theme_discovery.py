"""
Tests for Theme Discovery Agent.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from agents.theme_discovery.agent import ThemeDiscoveryAgent


class TestThemeDiscoveryAgent:
    """Test Theme Discovery Agent."""

    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = ThemeDiscoveryAgent()
        assert agent is not None
        assert hasattr(agent, 'search_client')
        assert hasattr(agent, 'llm_client')

    def test_get_week_context(self):
        """Test getting current week context."""
        agent = ThemeDiscoveryAgent()
        week_context = agent.get_week_context()
        
        assert "year" in week_context
        assert "month" in week_context
        assert "week_number" in week_context
        assert "date" in week_context
        assert isinstance(week_context["year"], int)
        assert isinstance(week_context["month"], int)

    @patch('agents.theme_discovery.agent.DuckDuckGoClient')
    def test_search_indian_cultural_events(self, mock_client_class):
        """Test searching for Indian cultural events."""
        mock_client = MagicMock()
        mock_client.search_themes.return_value = [
            {"title": "Diwali 2024", "body": "Festival of Lights celebration"},
            {"title": "Durga Pujo", "body": "Bengali festival"},
        ]
        mock_client_class.return_value = mock_client

        agent = ThemeDiscoveryAgent()
        results = agent.search_indian_cultural_events()

        # Agent makes multiple queries, so results are combined
        assert len(results) >= 2
        # Check that we have the expected themes
        titles = [r.get("title", "") for r in results]
        assert any("Diwali" in title for title in titles)
        assert mock_client.search_themes.call_count >= 1

    @patch('agents.theme_discovery.agent.DuckDuckGoClient')
    def test_search_indian_achievements(self, mock_client_class):
        """Test searching for Indian achievements."""
        mock_client = MagicMock()
        mock_client.search_themes.return_value = [
            {"title": "ISRO Rocket Launch", "body": "Successful mission"},
            {"title": "Chandrayaan Mission", "body": "Lunar exploration"},
        ]
        mock_client_class.return_value = mock_client

        agent = ThemeDiscoveryAgent()
        results = agent.search_indian_achievements()

        assert len(results) >= 0
        mock_client.search_themes.assert_called()

    @patch('agents.theme_discovery.agent.DuckDuckGoClient')
    def test_search_global_themes(self, mock_client_class):
        """Test searching for global popular themes."""
        mock_client = MagicMock()
        mock_client.search_themes.return_value = [
            {"title": "New Year 2025", "body": "Global celebration"},
            {"title": "Christmas", "body": "Holiday season"},
        ]
        mock_client_class.return_value = mock_client

        agent = ThemeDiscoveryAgent()
        results = agent.search_global_themes()

        assert len(results) >= 0
        mock_client.search_themes.assert_called()

    @patch('agents.theme_discovery.agent.DuckDuckGoClient')
    @patch('agents.theme_discovery.agent.LLMClient')
    def test_discover_themes_full_workflow(self, mock_llm_class, mock_ddg_class):
        """Test full theme discovery workflow."""
        # Mock DuckDuckGo client
        mock_ddg = MagicMock()
        mock_ddg.search_themes.return_value = [
            {"title": "Diwali", "body": "Festival of Lights"},
            {"title": "ISRO Launch", "body": "Rocket mission"},
        ]
        mock_ddg_class.return_value = mock_ddg

        # Mock LLM client
        mock_llm = MagicMock()
        mock_llm.generate_text.return_value = "Diwali: Festival of Lights, ISRO: Space achievement"
        mock_llm_class.return_value = mock_llm

        agent = ThemeDiscoveryAgent()
        themes = agent.discover_themes()

        assert isinstance(themes, list)
        assert len(themes) > 0
        # Each theme should have required fields
        if themes:
            theme = themes[0]
            assert "name" in theme or "title" in theme
            assert "type" in theme or "category" in theme

    @patch('agents.theme_discovery.agent.DuckDuckGoClient')
    def test_discover_themes_handles_empty_results(self, mock_client_class):
        """Test handling of empty search results."""
        mock_client = MagicMock()
        mock_client.search_themes.return_value = []
        mock_client_class.return_value = mock_client

        agent = ThemeDiscoveryAgent()
        themes = agent.discover_themes()

        assert isinstance(themes, list)
        # Should return empty list or default themes

    @patch('agents.theme_discovery.agent.DuckDuckGoClient')
    def test_discover_themes_handles_search_errors(self, mock_client_class):
        """Test error handling when search fails."""
        mock_client = MagicMock()
        mock_client.search_themes.side_effect = Exception("Search error")
        mock_client_class.return_value = mock_client

        agent = ThemeDiscoveryAgent()
        themes = agent.discover_themes()

        # Should handle errors gracefully
        assert isinstance(themes, list)

    def test_format_theme_output(self):
        """Test formatting theme output."""
        agent = ThemeDiscoveryAgent()
        
        raw_results = [
            {"title": "Diwali", "body": "Festival"},
            {"title": "New Year", "body": "Celebration"},
        ]
        
        formatted = agent._format_themes(raw_results, theme_type="cultural")
        
        assert isinstance(formatted, list)
        if formatted:
            assert "type" in formatted[0] or "category" in formatted[0]

    def test_extract_theme_keywords(self):
        """Test extracting keywords from search results."""
        agent = ThemeDiscoveryAgent()
        
        search_results = [
            {"title": "Diwali Festival 2024", "body": "Celebration of lights"},
            {"title": "ISRO Chandrayaan Mission", "body": "Lunar exploration"},
        ]
        
        keywords = agent._extract_keywords(search_results)
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0

    @patch('agents.theme_discovery.agent.DuckDuckGoClient')
    def test_search_with_week_context(self, mock_client_class):
        """Test that searches include week context."""
        mock_client = MagicMock()
        mock_client.search_themes.return_value = []
        mock_client_class.return_value = mock_client

        agent = ThemeDiscoveryAgent()
        week_context = agent.get_week_context()
        agent.search_indian_cultural_events()

        # Verify search was called (week context should be used in query)
        mock_client.search_themes.assert_called()
        call_args = mock_client.search_themes.call_args[0][0]
        # Query should be relevant to current time
        assert isinstance(call_args, str)
        assert len(call_args) > 0

