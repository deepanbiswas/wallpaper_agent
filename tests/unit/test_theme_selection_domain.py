"""
Tests for Theme Selection domain model.
"""
import pytest
from agents.theme_selection.domain import Theme


class TestTheme:
    """Test Theme domain model."""
    
    def test_theme_creation(self):
        """Test creating a theme."""
        theme = Theme(
            name="Diwali",
            description="Festival of Lights",
            type="indian_cultural",
        )
        
        assert theme.name == "Diwali"
        assert theme.description == "Festival of Lights"
        assert theme.type == "indian_cultural"
        assert theme.base_score == 0.0
        assert theme.llm_score == 0.0
        assert theme.final_score == 0.0
    
    def test_theme_to_dict(self):
        """Test converting theme to dictionary."""
        theme = Theme(
            name="Diwali",
            description="Festival",
            type="indian_cultural",
            base_score=100.0,
            llm_score=85.0,
            final_score=90.0,
        )
        
        data = theme.to_dict()
        
        assert data["name"] == "Diwali"
        assert data["description"] == "Festival"
        assert data["type"] == "indian_cultural"
        assert data["base_score"] == 100.0
        assert data["llm_score"] == 85.0
        assert data["final_score"] == 90.0
    
    def test_theme_from_dict(self):
        """Test creating theme from dictionary."""
        data = {
            "name": "New Year",
            "description": "Global celebration",
            "type": "global",
            "base_score": 40.0,
            "llm_score": 90.0,
            "final_score": 70.0,
        }
        
        theme = Theme.from_dict(data)
        
        assert theme.name == "New Year"
        assert theme.description == "Global celebration"
        assert theme.type == "global"
        assert theme.base_score == 40.0
        assert theme.llm_score == 90.0
        assert theme.final_score == 70.0
    
    def test_theme_defaults(self):
        """Test theme default values."""
        theme = Theme(name="Test")
        
        assert theme.description == ""
        assert theme.type == ""
        assert theme.source == "search"
        assert theme.base_score == 0.0
        assert theme.metadata == {}

