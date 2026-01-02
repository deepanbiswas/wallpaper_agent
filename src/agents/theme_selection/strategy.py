"""
Ranking strategies for theme selection.

Implements Strategy pattern - allows swapping ranking algorithms.
"""
from abc import ABC, abstractmethod
from typing import List
from agents.theme_selection.domain import Theme
from agents.theme_selection.stages import RankingStage


class ThemeRankingStrategy(ABC):
    """Abstract base class for theme ranking strategies."""
    
    @abstractmethod
    def rank(self, themes: List[Theme]) -> List[Theme]:
        """
        Rank themes according to this strategy.
        
        Args:
            themes: List of themes to rank
            
        Returns:
            Ranked list of themes
        """
        pass


class PipelineRankingStrategy(ThemeRankingStrategy):
    """Pipeline-based ranking strategy using Chain of Responsibility."""
    
    def __init__(self, stages: List[RankingStage]):
        """
        Initialize pipeline ranking strategy.
        
        Args:
            stages: List of ranking stages to apply in order
        """
        self.stages = stages
    
    def rank(self, themes: List[Theme]) -> List[Theme]:
        """Apply all stages in sequence to rank themes."""
        for stage in self.stages:
            themes = stage.apply(themes)
        return themes

