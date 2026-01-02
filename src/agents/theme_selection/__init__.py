"""
Theme Selection Agent package.

Implements theme ranking and selection using Strategy and Chain of Responsibility patterns.
"""
from agents.theme_selection.domain import Theme
from agents.theme_selection.ranker import ThemeRanker
from agents.theme_selection.strategy import ThemeRankingStrategy, PipelineRankingStrategy
from agents.theme_selection.stages import (
    RankingStage,
    InitialScoringStage,
    LLMRankingStage,
    NormalizationStage,
    CombinedScoringStage,
    FinalSortStage,
)
from agents.theme_selection.agent import ThemeSelectionAgent

__all__ = [
    "Theme",
    "ThemeRanker",
    "ThemeRankingStrategy",
    "PipelineRankingStrategy",
    "RankingStage",
    "InitialScoringStage",
    "LLMRankingStage",
    "NormalizationStage",
    "CombinedScoringStage",
    "FinalSortStage",
    "ThemeSelectionAgent",
]

