"""
Theme Discovery Agent for Wallpaper Agent.

Searches the internet for current themes, events, and cultural celebrations
relevant to the current week.
"""
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from api_clients import SearchClient, DuckDuckGoClient, LLMClient
from config import get_llm_config, load_config


class ThemeDiscoveryAgent:
    """Agent responsible for discovering current themes."""

    def __init__(
        self,
        config=None,
        search_client: Optional[SearchClient] = None,
        llm_client=None,
        min_relevance_score: int = 50,
    ):
        """
        Initialize Theme Discovery Agent.

        Args:
            config: Config instance (optional, loads from env if not provided)
            search_client: SearchClient instance (optional, defaults to DuckDuckGoClient)
            llm_client: LLMClient instance (optional)
            min_relevance_score: Minimum relevance score (0-100) to include theme (default: 50)
        """
        if config is None:
            config = load_config()
        
        self.config = config
        self.search_client: SearchClient = search_client or DuckDuckGoClient()
        self.min_relevance_score = min_relevance_score
        
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
        
        Uses LLM extraction if available, otherwise falls back to simple extraction.

        Args:
            search_results: Raw search results
            theme_type: Type of theme (e.g., "indian_cultural", "indian_achievement", "global")

        Returns:
            List of formatted theme dictionaries
        """
        if self.llm_client and search_results:
            return self._format_themes_with_llm(search_results, theme_type)
        else:
            return self._format_themes_simple(search_results, theme_type)
    
    def _format_themes_simple(
        self,
        search_results: List[Dict[str, Any]],
        theme_type: str
    ) -> List[Dict[str, Any]]:
        """
        Simple theme extraction (fallback when LLM not available).

        Args:
            search_results: Raw search results
            theme_type: Type of theme

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
    
    def _format_themes_with_llm(
        self,
        search_results: List[Dict[str, Any]],
        theme_type: str
    ) -> List[Dict[str, Any]]:
        """
        Use LLM to extract and clean themes from search results.

        Args:
            search_results: Raw search results
            theme_type: Type of theme

        Returns:
            List of formatted theme dictionaries with cleaned data
        """
        if not self.llm_client or not search_results:
            return self._format_themes_simple(search_results, theme_type)
        
        week_context = self.get_week_context()
        week_info = f"{week_context.get('month_name', '?')} {week_context.get('year', '?')}"
        
        # Format search results for LLM
        results_text = "\n".join([
            f"{i+1}. Title: {r.get('title', 'Unknown')}\n   Body: {r.get('body', '')[:200]}"
            for i, r in enumerate(search_results)
        ])
        
        prompt = f"""Extract theme information from these search results for {theme_type} themes in {week_info}.

Search Results:
{results_text}

For each relevant result, extract:
1. Theme name (clean, concise, remove dates/noise)
2. Brief description (1-2 sentences, clear and meaningful)
3. Relevance score (0-100) - how relevant is this theme to {week_info}?
4. Optional: dates/context if mentioned
5. Optional: significance (high/medium/low)
6. Optional: visual_appeal (high/medium/low) - for wallpaper generation
7. Optional: visual_elements (array of 2-3 key visual elements)
8. Optional: colors (array of 2-3 color hex codes associated with theme)

Return a JSON array with format:
[
  {{
    "name": "Diwali",
    "description": "Festival of lights celebrated in India",
    "relevance": 95,
    "dates": "October/November 2024",
    "significance": "high",
    "visual_appeal": "high",
    "visual_elements": ["lights", "fireworks", "decorations"],
    "colors": ["#FFD700", "#FF4500", "#000000"]
  }},
  ...
]

Only include themes that are:
- Currently relevant (this week/month)
- Suitable for wallpaper generation
- Culturally significant or notable
- Have relevance score >= {self.min_relevance_score}

Return only the JSON array, no other text."""
        
        try:
            response = self.llm_client.generate_text(prompt)
            
            # Try to extract JSON array
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                themes_data = json.loads(json_match.group())
                
                themes = []
                for theme_data in themes_data:
                    # Filter by relevance
                    relevance = theme_data.get("relevance", 0)
                    if relevance < self.min_relevance_score:
                        continue
                    
                    theme = {
                        "name": theme_data.get("name", "Unknown"),
                        "description": theme_data.get("description", ""),
                        "type": theme_type,
                        "source": "search_llm",
                        "metadata": {
                            "relevance": relevance,
                            "dates": theme_data.get("dates"),
                            "significance": theme_data.get("significance"),
                            "visual_appeal": theme_data.get("visual_appeal"),
                            "visual_elements": theme_data.get("visual_elements", []),
                            "colors": theme_data.get("colors", []),
                        },
                    }
                    themes.append(theme)
                
                return themes
                
        except (json.JSONDecodeError, ValueError, KeyError, Exception):
            # Fallback to simple extraction on error
            return self._format_themes_simple(search_results, theme_type)
        
        # Fallback if no valid JSON found
        return self._format_themes_simple(search_results, theme_type)

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

