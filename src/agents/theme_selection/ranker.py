"""
Theme ranker context class.

Uses Strategy pattern to allow swapping ranking strategies at runtime.
"""
from typing import List
from agents.theme_selection.domain import Theme
from agents.theme_selection.strategy import ThemeRankingStrategy


class ThemeRanker:
    """Context class for theme ranking - uses Strategy pattern."""
    
    def __init__(self, strategy: ThemeRankingStrategy):
        """
        Initialize theme ranker with a ranking strategy.
        
        Args:
            strategy: Ranking strategy to use
        """
        self.strategy = strategy
    
    def set_strategy(self, strategy: ThemeRankingStrategy):
        """
        Change the ranking strategy at runtime.
        
        Args:
            strategy: New ranking strategy to use
        """
        self.strategy = strategy
    
    def rank(self, themes: List[Theme]) -> List[Theme]:
        """
        Rank themes using the current strategy.
        
        Args:
            themes: List of themes to rank
            
        Returns:
            Ranked list of themes
        """
        return self.strategy.rank(themes)

