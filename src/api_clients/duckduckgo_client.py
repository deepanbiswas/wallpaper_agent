"""
DuckDuckGo search client for Wallpaper Agent.
"""
from typing import List, Dict, Any
from duckduckgo_search import DDGS
from api_clients.interfaces import SearchClient


class DuckDuckGoClient(SearchClient):
    """Client for DuckDuckGo search API."""

    def __init__(self):
        """Initialize DuckDuckGo client."""
        pass

    def search_themes(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for themes using DuckDuckGo.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of search results (empty list on error)
        """
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                return results
        except Exception:
            # Log error in production
            return []

