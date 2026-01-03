"""
Evaluator for Theme Discovery Agent.
"""
import json
import re
from typing import List, Dict, Any, Optional
from .metrics import EvaluationResult, EvaluationMetrics
from api_clients import LLMClient
from utils.logger import get_logger


class DiscoveryEvaluator:
    """Evaluates Theme Discovery Agent output quality."""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialize Discovery Evaluator.
        
        Args:
            llm_client: LLMClient instance (optional, for LLM-based evaluations)
        """
        self.llm_client = llm_client
        self.logger = get_logger(__name__)
    
    def evaluate(
        self,
        themes: List[Dict[str, Any]],
        week_context: Optional[Dict[str, Any]] = None
    ) -> EvaluationResult:
        """
        Evaluate Theme Discovery Agent output.
        
        Args:
            themes: List of discovered themes
            week_context: Current week context (optional)
            
        Returns:
            EvaluationResult with metrics
        """
        from datetime import datetime
        
        metrics = {}
        warnings = []
        
        # 1. Theme Relevance Score
        relevance_score = self._evaluate_relevance(themes, week_context)
        metrics["relevance"] = EvaluationMetrics(
            score=relevance_score,
            threshold=80.0,
            passed=relevance_score >= 80.0,
            details={"method": "llm_based" if self.llm_client else "rule_based"},
        )
        if relevance_score < 60.0:
            warnings.append(f"Low relevance score: {relevance_score:.1f}")
        
        # 2. Theme Quality Score
        quality_score = self._evaluate_quality(themes)
        metrics["quality"] = EvaluationMetrics(
            score=quality_score,
            threshold=85.0,
            passed=quality_score >= 85.0,
            details={"method": "rule_based"},
        )
        if quality_score < 75.0:
            warnings.append(f"Low quality score: {quality_score:.1f}")
        
        # 3. Deduplication Accuracy
        dedup_score = self._evaluate_deduplication(themes)
        metrics["deduplication"] = EvaluationMetrics(
            score=dedup_score,
            threshold=90.0,
            passed=dedup_score >= 90.0,
        )
        
        # 4. Coverage Score
        coverage_score = self._evaluate_coverage(themes)
        metrics["coverage"] = EvaluationMetrics(
            score=coverage_score,
            threshold=70.0,
            passed=coverage_score >= 70.0,
        )
        if coverage_score < 70.0:
            warnings.append(f"Low coverage: {coverage_score:.1f}")
        
        # Calculate overall score
        overall_score = sum(m.score for m in metrics.values()) / len(metrics) if metrics else 0.0
        passed = all(m.passed for m in metrics.values()) if metrics else False
        
        return EvaluationResult(
            agent_name="ThemeDiscoveryAgent",
            timestamp=datetime.now(),
            overall_score=overall_score,
            metrics=metrics,
            passed=passed,
            warnings=warnings,
            metadata={"theme_count": len(themes)},
        )
    
    def _evaluate_relevance(
        self,
        themes: List[Dict[str, Any]],
        week_context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Evaluate theme relevance (0-100)."""
        if not themes:
            return 0.0
        
        if self.llm_client and week_context:
            # LLM-based evaluation
            week_info = f"{week_context.get('month_name', '?')} {week_context.get('year', '?')}"
            themes_list = "\n".join([
                f"- {t.get('name', 'Unknown')}: {t.get('description', '')[:100]}"
                for t in themes
            ])
            
            prompt = f"""Evaluate the relevance of these themes to {week_info}:

{themes_list}

For each theme, score 0-100 based on:
- Current relevance (is it happening now/soon?)
- Cultural significance
- Popularity

Return JSON: {{"average_relevance": <score>}}
Only return the JSON."""
            
            try:
                response = self.llm_client.generate_text(prompt)
                json_match = re.search(r'\{[^}]+\}', response)
                if json_match:
                    data = json.loads(json_match.group())
                    return float(data.get("average_relevance", 50.0))
            except Exception:
                pass
        
        # Rule-based fallback: use metadata relevance if available
        relevance_scores = []
        for theme in themes:
            if "metadata" in theme and "relevance" in theme["metadata"]:
                relevance_scores.append(theme["metadata"]["relevance"])
        
        if relevance_scores:
            return sum(relevance_scores) / len(relevance_scores)
        
        # Default: assume moderate relevance
        return 60.0
    
    def _evaluate_quality(self, themes: List[Dict[str, Any]]) -> float:
        """Evaluate theme quality (0-100)."""
        if not themes:
            return 0.0
        
        scores = []
        for theme in themes:
            score = 0.0
            
            # Name quality (30 points)
            name = theme.get("name", "")
            if name and name != "Unknown":
                if len(name) > 3 and len(name) < 50:  # Reasonable length
                    score += 20.0
                if not any(char.isdigit() for char in name[-4:]):  # No trailing dates
                    score += 10.0
            
            # Description quality (40 points)
            desc = theme.get("description", "")
            if desc:
                if len(desc) > 20:  # Has meaningful description
                    score += 30.0
                if len(desc) < 500:  # Not too long
                    score += 10.0
            
            # Metadata presence (30 points)
            if "metadata" in theme:
                metadata = theme["metadata"]
                if metadata.get("relevance"):
                    score += 10.0
                if metadata.get("significance"):
                    score += 10.0
                if metadata.get("visual_appeal"):
                    score += 10.0
            
            scores.append(score)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _evaluate_deduplication(self, themes: List[Dict[str, Any]]) -> float:
        """Evaluate deduplication accuracy (0-100)."""
        if not themes:
            return 100.0
        
        # Check for obvious duplicates (case-insensitive name matching)
        names = [t.get("name", "").lower().strip() for t in themes]
        unique_names = set(names)
        
        # Score based on uniqueness ratio
        if len(names) == 0:
            return 100.0
        
        uniqueness_ratio = len(unique_names) / len(names)
        return uniqueness_ratio * 100.0
    
    def _evaluate_coverage(self, themes: List[Dict[str, Any]]) -> float:
        """Evaluate theme coverage across categories (0-100)."""
        if not themes:
            return 0.0
        
        types = set(t.get("type", "") for t in themes)
        
        # Expected types: indian_cultural, indian_achievement, global
        expected_types = {"indian_cultural", "indian_achievement", "global"}
        found_types = types.intersection(expected_types)
        
        # Score: 33 points per category found
        return (len(found_types) / len(expected_types)) * 100.0

