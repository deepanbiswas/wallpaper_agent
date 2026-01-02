"""
Theme Discovery Agent for Wallpaper Agent.

Searches the internet for current themes, events, and cultural celebrations
relevant to the current week.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from api_clients import DuckDuckGoClient, LLMClient
from config import get_llm_config, load_config


class ThemeDiscoveryAgent:
    """Agent responsible for discovering current themes."""

    def __init__(self, config=None, search_client=None, llm_client=None):
        """
        Initialize Theme Discovery Agent.

        Args:
            config: Config instance (optional, loads from env if not provided)
            search_client: DuckDuckGoClient instance (optional)
            llm_client: LLMClient instance (optional)
        """
        if config is None:
            config = load_config()
        
        self.config = config
        self.search_client = search_client or DuckDuckGoClient()
        
        # Initialize LLM client if not provided
        if llm_client is None:
            llm_config = get_llm_config(config)
            if llm_config.get("anthropic_api_key") or llm_config.get("openai_api_key"):
                self.llm_client = LLMClient(
                    provider=llm_config["provider"],
                    api_key=llm_config.get(f"{llm_config['provider']}_api_key"),
                    model=llm_config.get("model")
                )
            else:
                self.llm_client = None
        else:
            self.llm_client = llm_client

    def get_week_context(self) -> Dict[str, Any]:
        """
        Get current week context information.

        Returns:
            Dictionary with year, month, week_number, and date
        """
        now = datetime.now()
        year_start = datetime(now.year, 1, 1)
        week_number = (now - year_start).days // 7 + 1
        
        return {
            "year": now.year,
            "month": now.month,
            "week_number": week_number,
            "date": now.strftime("%Y-%m-%d"),
            "month_name": now.strftime("%B"),
        }

    def search_indian_cultural_events(self) -> List[Dict[str, Any]]:
        """
        Search for Indian cultural events and festivals.

        Returns:
            List of search results for Indian cultural events
        """
        week_context = self.get_week_context()
        queries = [
            f"Indian festivals {week_context['month_name']} {week_context['year']}",
            "Diwali Durga Pujo Indian cultural events",
            f"Indian celebrations {week_context['year']}",
        ]
        
        all_results = []
        for query in queries:
            try:
                results = self.search_client.search_themes(query, max_results=5)
                all_results.extend(results)
            except Exception:
                continue
        
        return all_results

    def search_indian_achievements(self) -> List[Dict[str, Any]]:
        """
        Search for Indian achievements and achievements by Indians worldwide.
        
        Includes all top achievements for India and by Indians globally,
        not limited to ISRO or space missions.

        Returns:
            List of search results for Indian achievements
        """
        week_context = self.get_week_context()
        queries = [
            f"achievements by Indians {week_context['year']}",
            f"India achievements {week_context['month_name']} {week_context['year']}",
            "Indian achievements worldwide",
            f"top Indian achievements {week_context['year']}",
            "achievements by people of Indian origin",
        ]
        
        all_results = []
        for query in queries:
            try:
                results = self.search_client.search_themes(query, max_results=5)
                all_results.extend(results)
            except Exception:
                continue
        
        return all_results

    def search_global_themes(self) -> List[Dict[str, Any]]:
        """
        Search for globally popular themes.

        Returns:
            List of search results for global themes
        """
        week_context = self.get_week_context()
        queries = [
            f"popular events {week_context['month_name']} {week_context['year']}",
            "New Year Christmas global celebrations",
            f"trending themes {week_context['year']}",
        ]
        
        all_results = []
        for query in queries:
            try:
                results = self.search_client.search_themes(query, max_results=5)
                all_results.extend(results)
            except Exception:
                continue
        
        return all_results

    def _extract_keywords(self, search_results: List[Dict[str, Any]]) -> List[str]:
        """
        Extract keywords from search results.

        Args:
            search_results: List of search result dictionaries

        Returns:
            List of extracted keywords
        """
        keywords = []
        for result in search_results:
            title = result.get("title", "")
            body = result.get("body", "")
            # Simple keyword extraction (can be enhanced with LLM)
            text = f"{title} {body}".lower()
            # Extract potential theme names (simplified)
            keywords.append(title)
        return keywords

    def _format_themes(
        self,
        search_results: List[Dict[str, Any]],
        theme_type: str
    ) -> List[Dict[str, Any]]:
        """
        Format search results into theme structure.

        Args:
            search_results: Raw search results
            theme_type: Type of theme (e.g., "indian_cultural", "indian_achievement", "global")

        Returns:
            List of formatted theme dictionaries
        """
        themes = []
        for result in search_results:
            theme = {
                "name": result.get("title", "Unknown"),
                "description": result.get("body", ""),
                "type": theme_type,
                "source": "search",
            }
            themes.append(theme)
        return themes

    def discover_themes(self) -> List[Dict[str, Any]]:
        """
        Discover themes by searching multiple sources.

        Returns:
            List of discovered themes with metadata
        """
        themes = []
        
        try:
            # Search Indian cultural events
            cultural_results = self.search_indian_cultural_events()
            cultural_themes = self._format_themes(cultural_results, "indian_cultural")
            themes.extend(cultural_themes)
            
            # Search Indian achievements
            achievement_results = self.search_indian_achievements()
            achievement_themes = self._format_themes(achievement_results, "indian_achievement")
            themes.extend(achievement_themes)
            
            # Search global themes
            global_results = self.search_global_themes()
            global_themes = self._format_themes(global_results, "global")
            themes.extend(global_themes)
            
        except Exception:
            # Return empty list on error
            return []
        
        # Remove duplicates based on name
        seen = set()
        unique_themes = []
        for theme in themes:
            name = theme.get("name", "").lower()
            if name and name not in seen:
                seen.add(name)
                unique_themes.append(theme)
        
        return unique_themes

