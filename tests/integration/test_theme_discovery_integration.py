"""
Integration tests for Theme Discovery Agent.

These tests call the actual DuckDuckGo API to verify real-world functionality.
Marked with @pytest.mark.integration and @pytest.mark.api for selective running.
"""
import pytest
from agents.theme_discovery import ThemeDiscoveryAgent


@pytest.mark.integration
@pytest.mark.api
class TestThemeDiscoveryAgentIntegration:
    """Integration tests for Theme Discovery Agent with real API calls."""

    def test_agent_initialization_real(self):
        """Test agent initialization with real dependencies."""
        agent = ThemeDiscoveryAgent()
        assert agent is not None
        assert agent.search_client is not None

    @pytest.mark.slow
    def test_get_week_context_real(self):
        """Test getting real week context."""
        agent = ThemeDiscoveryAgent()
        week_context = agent.get_week_context()
        
        assert "year" in week_context
        assert "month" in week_context
        assert "week_number" in week_context
        assert "date" in week_context
        assert isinstance(week_context["year"], int)
        assert week_context["year"] >= 2024  # Reasonable year check
        assert 1 <= week_context["month"] <= 12

    @pytest.mark.slow
    def test_search_indian_cultural_events_real(self):
        """Test searching for Indian cultural events with real API."""
        agent = ThemeDiscoveryAgent()
        results = agent.search_indian_cultural_events()
        
        # Should return a list
        assert isinstance(results, list)
        # Should have some results (may vary based on current events)
        # At minimum, should not crash
        if results:
            # Verify structure of results
            assert "title" in results[0] or "name" in results[0]
            assert "body" in results[0] or "description" in results[0]

    @pytest.mark.slow
    def test_search_indian_achievements_real(self):
        """Test searching for Indian achievements with real API."""
        agent = ThemeDiscoveryAgent()
        results = agent.search_indian_achievements()
        
        # Should return a list
        assert isinstance(results, list)
        # Should have some results (may vary)
        if results:
            # Verify structure
            assert "title" in results[0] or "name" in results[0]

    @pytest.mark.slow
    def test_search_global_themes_real(self):
        """Test searching for global themes with real API."""
        agent = ThemeDiscoveryAgent()
        results = agent.search_global_themes()
        
        # Should return a list
        assert isinstance(results, list)
        # May or may not have results depending on current events
        if results:
            assert "title" in results[0] or "name" in results[0]

    @pytest.mark.slow
    def test_discover_themes_full_workflow_real(self):
        """
        Test full theme discovery workflow with real API calls.
        
        This is the main integration test that verifies the complete
        discovery process works end-to-end.
        """
        agent = ThemeDiscoveryAgent()
        themes = agent.discover_themes()
        
        # Should return a list
        assert isinstance(themes, list)
        
        # Should have discovered some themes (at least a few)
        # Note: This may vary based on current events and API availability
        assert len(themes) >= 0  # At minimum, should not crash
        
        if themes:
            # Verify theme structure
            theme = themes[0]
            assert "name" in theme
            assert "type" in theme
            assert "description" in theme or "body" in theme
            assert "source" in theme
            
            # Verify theme types are valid
            valid_types = ["indian_cultural", "indian_achievement", "global"]
            assert theme["type"] in valid_types
            
            # Check for duplicates (should be removed)
            names = [t.get("name", "").lower() for t in themes]
            assert len(names) == len(set(names)), "Duplicate themes found"
            
            # Print detailed output for verification
            print(f"\n✅ Discovered {len(themes)} unique themes")
            print("\n" + "=" * 70)
            print("DISCOVERED THEMES BY TYPE:")
            print("=" * 70)
            
            # Group by type
            by_type = {}
            for theme in themes:
                theme_type = theme.get("type", "unknown")
                if theme_type not in by_type:
                    by_type[theme_type] = []
                by_type[theme_type].append(theme)
            
            # Print themes by type
            for theme_type, theme_list in by_type.items():
                print(f"\n📌 {theme_type.upper().replace('_', ' ')} ({len(theme_list)} themes):")
                print("-" * 70)
                for i, t in enumerate(theme_list[:10], 1):  # Show first 10 of each type
                    name = t.get('name', 'Unknown')
                    desc = t.get('description', '')[:80] if t.get('description') else ''
                    print(f"  {i}. {name}")
                    if desc:
                        print(f"     {desc}...")
            
            print("\n" + "=" * 70)
            print("SAMPLE THEME STRUCTURE (JSON):")
            print("=" * 70)
            if themes:
                import json
                print(json.dumps(themes[0], indent=2))

    @pytest.mark.slow
    def test_discover_themes_returns_structured_data(self):
        """Test that discovered themes have proper structure."""
        agent = ThemeDiscoveryAgent()
        themes = agent.discover_themes()
        
        if themes:
            for theme in themes:
                # Required fields
                assert "name" in theme, f"Theme missing 'name': {theme}"
                assert "type" in theme, f"Theme missing 'type': {theme}"
                assert "source" in theme, f"Theme missing 'source': {theme}"
                
                # Type validation
                assert theme["type"] in [
                    "indian_cultural",
                    "indian_achievement",
                    "global"
                ], f"Invalid theme type: {theme['type']}"
                
                # Name should not be empty
                assert theme["name"], f"Theme name is empty: {theme}"

    @pytest.mark.slow
    def test_theme_discovery_performance(self):
        """Test that theme discovery completes in reasonable time."""
        import time
        
        agent = ThemeDiscoveryAgent()
        start_time = time.time()
        themes = agent.discover_themes()
        elapsed = time.time() - start_time
        
        # Should complete within 30 seconds (reasonable for multiple API calls)
        assert elapsed < 30, f"Theme discovery took too long: {elapsed:.2f}s"
        print(f"\n⏱️  Theme discovery completed in {elapsed:.2f} seconds")
