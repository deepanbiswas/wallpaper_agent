"""
Ranking stages for theme selection pipeline.

Implements Chain of Responsibility pattern - each stage processes themes
and passes them to the next stage.
"""
from abc import ABC, abstractmethod
from typing import List
from agents.theme_selection.domain import Theme


class RankingStage(ABC):
    """Abstract base class for ranking stages."""
    
    @abstractmethod
    def apply(self, themes: List[Theme]) -> List[Theme]:
        """
        Apply this stage's ranking logic to themes.
        
        Args:
            themes: List of themes to process
            
        Returns:
            Processed list of themes (may be modified in-place or new list)
        """
        pass


class InitialScoringStage(RankingStage):
    """Initial rule-based scoring stage."""
    
    def __init__(
        self,
        prefer_indian_culture: bool = True,
        prefer_indian_achievements: bool = True,
    ):
        """
        Initialize initial scoring stage.
        
        Args:
            prefer_indian_culture: Whether to boost Indian cultural themes
            prefer_indian_achievements: Whether to boost Indian achievement themes
        """
        self.prefer_indian_culture = prefer_indian_culture
        self.prefer_indian_achievements = prefer_indian_achievements
        
        # Base scores by theme type
        self.base_scores = {
            "indian_cultural": 100.0,
            "indian_achievement": 80.0,
            "global": 40.0,
        }
        
        # Preference multipliers
        self.multipliers = {
            "indian_cultural": 1.5 if prefer_indian_culture else 1.0,
            "indian_achievement": 1.3 if prefer_indian_achievements else 1.0,
            "global": 1.0,
        }
    
    def apply(self, themes: List[Theme]) -> List[Theme]:
        """Apply initial scoring based on theme type and preferences."""
        for theme in themes:
            # Get base score for theme type
            base_score = self.base_scores.get(theme.type, 50.0)
            
            # Apply preference multiplier
            multiplier = self.multipliers.get(theme.type, 1.0)
            
            # Calculate final base score
            theme.base_score = base_score * multiplier
        
        return themes


class LLMRankingStage(RankingStage):
    """LLM-based intelligent ranking stage."""
    
    def __init__(self, llm_client, week_context: dict = None):
        """
        Initialize LLM ranking stage.
        
        Args:
            llm_client: LLMClient instance for ranking
            week_context: Current week context (year, month, etc.)
        """
        self.llm_client = llm_client
        self.week_context = week_context or {}
    
    def apply(self, themes: List[Theme]) -> List[Theme]:
        """Apply LLM-based ranking to themes."""
        if not self.llm_client or not themes:
            # If no LLM client, set default scores
            for theme in themes:
                theme.llm_score = 50.0  # Neutral score
            return themes
        
        # Build prompt for LLM
        prompt = self._build_ranking_prompt(themes)
        
        try:
            # Get LLM response
            response = self.llm_client.generate_text(prompt)
            
            # Parse LLM response to extract scores
            scores = self._parse_llm_response(response, themes)
            
            # Assign scores to themes
            for i, theme in enumerate(themes):
                theme.llm_score = scores.get(i, 50.0)
                
        except Exception:
            # On error, set default scores
            for theme in themes:
                theme.llm_score = 50.0
        
        return themes
    
    def _build_ranking_prompt(self, themes: List[Theme]) -> str:
        """Build prompt for LLM ranking."""
        week_info = f"Week {self.week_context.get('week_number', '?')}, {self.week_context.get('month_name', '?')} {self.week_context.get('year', '?')}"
        
        themes_list = "\n".join([
            f"{i+1}. {t.name} ({t.type}) - {t.description[:100]}"
            for i, t in enumerate(themes)
        ])
        
        prompt = f"""Rank these themes discovered for {week_info} based on:
1. Relevance to current time period
2. Cultural significance (prioritize Indian culture/achievements)
3. Popularity/importance
4. Suitability for a minimalistic dark-themed wallpaper

Themes:
{themes_list}

For each theme, provide a relevance score from 0-100. Return only a JSON object with theme numbers as keys and scores as values, like:
{{"0": 85, "1": 72, "2": 90, ...}}

Only return the JSON, no other text."""
        
        return prompt
    
    def _parse_llm_response(self, response: str, themes: List[Theme]) -> dict:
        """Parse LLM response to extract scores."""
        import json
        import re
        
        # Try to extract JSON from response
        json_match = re.search(r'\{[^}]+\}', response)
        if json_match:
            try:
                scores = json.loads(json_match.group())
                # Convert string keys to int
                return {int(k): float(v) for k, v in scores.items()}
            except (json.JSONDecodeError, ValueError, KeyError):
                pass
        
        # Fallback: return default scores
        return {i: 50.0 for i in range(len(themes))}


class NormalizationStage(RankingStage):
    """Normalize scores to 0-1 range."""
    
    def apply(self, themes: List[Theme]) -> List[Theme]:
        """Normalize base_score and llm_score to 0-1 range."""
        if not themes:
            return themes
        
        # Normalize base scores
        base_scores = [t.base_score for t in themes]
        max_base = max(base_scores) if base_scores else 1.0
        if max_base > 0:
            for theme in themes:
                theme.base_score = theme.base_score / max_base
        
        # Normalize LLM scores
        llm_scores = [t.llm_score for t in themes]
        max_llm = max(llm_scores) if llm_scores else 1.0
        if max_llm > 0:
            for theme in themes:
                theme.llm_score = theme.llm_score / max_llm
        
        return themes


class CombinedScoringStage(RankingStage):
    """Combine base_score and llm_score into final_score."""
    
    def __init__(self, base_weight: float = 0.4, llm_weight: float = 0.6):
        """
        Initialize combined scoring stage.
        
        Args:
            base_weight: Weight for base_score (default 0.4 = 40%)
            llm_weight: Weight for llm_score (default 0.6 = 60%)
        """
        self.base_weight = base_weight
        self.llm_weight = llm_weight
    
    def apply(self, themes: List[Theme]) -> List[Theme]:
        """Calculate final_score from base_score and llm_score."""
        for theme in themes:
            theme.final_score = (
                theme.base_score * self.base_weight +
                theme.llm_score * self.llm_weight
            )
        
        return themes


class FinalSortStage(RankingStage):
    """Final sorting stage - sorts themes by final_score descending."""
    
    def apply(self, themes: List[Theme]) -> List[Theme]:
        """Sort themes by final_score in descending order."""
        return sorted(themes, key=lambda t: t.final_score, reverse=True)

