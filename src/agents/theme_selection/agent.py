"""
Theme Selection Agent.

Selects the best theme from discovered themes using ranking strategies.
"""
from typing import List, Dict, Any, Optional
from agents.theme_selection.domain import Theme
from agents.theme_selection.ranker import ThemeRanker
from agents.theme_selection.strategy import PipelineRankingStrategy
from agents.theme_selection.stages import (
    InitialScoringStage,
    LLMRankingStage,
    NormalizationStage,
    CombinedScoringStage,
    FinalSortStage,
)
from api_clients import LLMClient
from config import get_llm_config, get_theme_preferences, load_config


class ThemeSelectionAgent:
    """Agent responsible for selecting the best theme from discovered themes."""
    
    def __init__(
        self,
        config=None,
        llm_client=None,
        ranker: Optional[ThemeRanker] = None,
    ):
        """
        Initialize Theme Selection Agent.
        
        Args:
            config: Config instance (optional, loads from env if not provided)
            llm_client: LLMClient instance (optional)
            ranker: ThemeRanker instance (optional, creates default if not provided)
        """
        if config is None:
            config = load_config()
        
        self.config = config
        
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
        
        # Initialize ranker if not provided
        if ranker is None:
            ranker = self._create_default_ranker()
        
        self.ranker = ranker
    
    def _create_default_ranker(self) -> ThemeRanker:
        """Create default ranker with multi-stage pipeline strategy."""
        theme_prefs = get_theme_preferences(self.config)
        
        # Create stages
        stages = [
            InitialScoringStage(
                prefer_indian_culture=theme_prefs.get("prefer_indian_culture", True),
                prefer_indian_achievements=theme_prefs.get("prefer_indian_achievements", True),
            ),
            LLMRankingStage(
                llm_client=self.llm_client,
                week_context=self._get_week_context(),
            ),
            NormalizationStage(),
            CombinedScoringStage(base_weight=0.4, llm_weight=0.6),
            FinalSortStage(),
        ]
        
        # Create strategy and ranker
        strategy = PipelineRankingStrategy(stages=stages)
        return ThemeRanker(strategy)
    
    def _get_week_context(self) -> Dict[str, Any]:
        """Get current week context."""
        from datetime import datetime
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
    
    def select_theme(self, themes: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Select the best theme from discovered themes.
        
        Args:
            themes: List of theme dictionaries from Discovery Agent
            
        Returns:
            Selected theme dictionary with detailed description, or None if no themes
        """
        if not themes:
            return None
        
        # Convert dictionaries to Theme objects
        theme_objects = [Theme.from_dict(t) for t in themes]
        
        # Rank themes
        ranked_themes = self.ranker.rank(theme_objects)
        
        if not ranked_themes:
            return None
        
        # Select top theme
        top_theme = ranked_themes[0]
        
        # Generate detailed description for wallpaper generation
        detailed_theme = self._generate_theme_description(top_theme, ranked_themes)
        
        return detailed_theme
    
    def _generate_theme_description(
        self,
        theme: Theme,
        all_themes: List[Theme]
    ) -> Dict[str, Any]:
        """
        Generate detailed theme description for wallpaper generation.
        
        Args:
            theme: Selected theme
            all_themes: All ranked themes (for context)
            
        Returns:
            Detailed theme dictionary with style guidelines
        """
        # Build base description
        description = {
            "name": theme.name,
            "description": theme.description,
            "type": theme.type,
            "source": theme.source,
            "final_score": theme.final_score,
            "base_score": theme.base_score,
            "llm_score": theme.llm_score,
        }
        
        # Generate style guidelines using LLM if available
        if self.llm_client:
            try:
                style_guidelines = self._generate_style_guidelines(theme)
                description["style_guidelines"] = style_guidelines
            except Exception:
                # Fallback to default style guidelines
                description["style_guidelines"] = self._default_style_guidelines(theme)
        else:
            description["style_guidelines"] = self._default_style_guidelines(theme)
        
        return description
    
    def _generate_style_guidelines(self, theme: Theme) -> Dict[str, Any]:
        """Generate style guidelines using LLM."""
        prompt = f"""Generate style guidelines for a minimalistic, dark-themed wallpaper based on this theme:

Theme: {theme.name}
Description: {theme.description}
Type: {theme.type}

Requirements:
- Minimalistic design
- Dark theme (dark background)
- Visually appealing
- Suitable for MacBook Pro wallpaper

Return a JSON object with:
- "color_palette": array of 2-4 dark colors (hex codes)
- "key_elements": array of 2-3 key visual elements to include
- "style_description": brief description of the visual style
- "prompt": detailed prompt for image generation

Only return the JSON, no other text."""
        
        try:
            response = self.llm_client.generate_text(prompt)
            import json
            import re
            
            # Extract JSON from response
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass
        
        # Fallback to default
        return self._default_style_guidelines(theme)
    
    def _default_style_guidelines(self, theme: Theme) -> Dict[str, Any]:
        """Default style guidelines when LLM is not available."""
        return {
            "color_palette": ["#1a1a1a", "#2d2d2d", "#4a4a4a"],
            "key_elements": [theme.name],
            "style_description": "Minimalistic dark theme",
            "prompt": f"Minimalistic dark-themed wallpaper featuring {theme.name}, dark background, elegant design",
        }

