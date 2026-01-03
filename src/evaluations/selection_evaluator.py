"""
Evaluator for Theme Selection Agent.
"""
import json
import re
from typing import List, Dict, Any, Optional
from .metrics import EvaluationResult, EvaluationMetrics
from api_clients import LLMClient
from utils.logger import get_logger


class SelectionEvaluator:
    """Evaluates Theme Selection Agent output quality."""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialize Selection Evaluator.
        
        Args:
            llm_client: LLMClient instance (optional, for LLM-based evaluations)
        """
        self.llm_client = llm_client
        self.logger = get_logger(__name__)
    
    def evaluate(
        self,
        selected_theme: Dict[str, Any],
        all_themes: List[Dict[str, Any]],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> EvaluationResult:
        """
        Evaluate Theme Selection Agent output.
        
        Args:
            selected_theme: Selected theme
            all_themes: All available themes
            user_preferences: User preference settings (optional)
            
        Returns:
            EvaluationResult with metrics
        """
        from datetime import datetime
        
        metrics = {}
        warnings = []
        
        # 1. Selection Accuracy
        accuracy_score = self._evaluate_selection_accuracy(selected_theme, all_themes)
        metrics["selection_accuracy"] = EvaluationMetrics(
            score=accuracy_score,
            threshold=85.0,
            passed=accuracy_score >= 85.0,
        )
        if accuracy_score < 70.0:
            warnings.append(f"Low selection accuracy: {accuracy_score:.1f}")
        
        # 2. Preference Adherence
        preference_score = self._evaluate_preference_adherence(
            selected_theme, all_themes, user_preferences
        )
        metrics["preference_adherence"] = EvaluationMetrics(
            score=preference_score,
            threshold=90.0,
            passed=preference_score >= 90.0,
        )
        
        # 3. Style Guidelines Quality
        style_score = self._evaluate_style_guidelines(selected_theme)
        metrics["style_quality"] = EvaluationMetrics(
            score=style_score,
            threshold=85.0,
            passed=style_score >= 85.0,
        )
        
        # Calculate overall score
        overall_score = sum(m.score for m in metrics.values()) / len(metrics) if metrics else 0.0
        passed = all(m.passed for m in metrics.values()) if metrics else False
        
        return EvaluationResult(
            agent_name="ThemeSelectionAgent",
            timestamp=datetime.now(),
            overall_score=overall_score,
            metrics=metrics,
            passed=passed,
            warnings=warnings,
            metadata={"selected_theme": selected_theme.get("name")},
        )
    
    def _evaluate_selection_accuracy(
        self,
        selected_theme: Dict[str, Any],
        all_themes: List[Dict[str, Any]]
    ) -> float:
        """Evaluate if selected theme is the best choice (0-100)."""
        if not selected_theme or not all_themes:
            return 0.0
        
        if self.llm_client:
            # LLM-based evaluation
            themes_list = "\n".join([
                f"{i+1}. {t.get('name', 'Unknown')} ({t.get('type', 'unknown')}) - {t.get('description', '')[:100]}"
                for i, t in enumerate(all_themes)
            ])
            selected_name = selected_theme.get("name", "Unknown")
            
            prompt = f"""Given these themes and the selected theme:

All Themes:
{themes_list}

Selected: {selected_name}

Evaluate if the selection is correct (0-100) based on:
- Relevance to current time
- User preferences (Indian culture priority)
- Visual appeal potential
- Cultural significance

Return JSON: {{"accuracy_score": <score>, "justification": "<brief>"}}
Only return the JSON."""
            
            try:
                response = self.llm_client.generate_text(prompt)
                json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    return float(data.get("accuracy_score", 75.0))
            except Exception:
                pass
        
        # Rule-based fallback: check if selected theme has high score/metadata
        selected_type = selected_theme.get("type", "")
        if selected_type == "indian_cultural":
            return 90.0  # Good if Indian cultural selected
        elif selected_type == "indian_achievement":
            return 85.0
        else:
            return 70.0  # Lower for global
    
    def _evaluate_preference_adherence(
        self,
        selected_theme: Dict[str, Any],
        all_themes: List[Dict[str, Any]],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> float:
        """Evaluate preference adherence (0-100)."""
        if not selected_theme or not all_themes:
            return 0.0
        
        # Default preferences
        prefer_indian = True
        if user_preferences:
            prefer_indian = user_preferences.get("prefer_indian_culture", True)
        
        selected_type = selected_theme.get("type", "")
        
        # Check if there are Indian themes available
        indian_themes = [t for t in all_themes if t.get("type") in ["indian_cultural", "indian_achievement"]]
        
        if prefer_indian and indian_themes:
            # Should have selected Indian theme
            if selected_type in ["indian_cultural", "indian_achievement"]:
                return 100.0
            else:
                return 50.0  # Selected global when Indian available
        else:
            return 100.0  # No preference or no Indian themes
    
    def _evaluate_style_guidelines(self, theme: Dict[str, Any]) -> float:
        """Evaluate style guidelines quality (0-100)."""
        style_guidelines = theme.get("style_guidelines", {})
        
        if not style_guidelines:
            return 0.0
        
        score = 0.0
        
        # Check required fields
        if style_guidelines.get("prompt"):
            score += 40.0
        if style_guidelines.get("color_palette"):
            score += 20.0
        if style_guidelines.get("key_elements"):
            score += 20.0
        if style_guidelines.get("style_description"):
            score += 20.0
        
        return score

