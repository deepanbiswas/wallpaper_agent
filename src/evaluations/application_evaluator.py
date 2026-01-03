"""
Evaluator for Wallpaper Application Agent.
"""
from typing import Optional
from .metrics import EvaluationResult, EvaluationMetrics
from utils.logger import get_logger


class ApplicationEvaluator:
    """Evaluates Wallpaper Application Agent output quality."""
    
    def __init__(self):
        """Initialize Application Evaluator."""
        self.logger = get_logger(__name__)
    
    def evaluate(
        self,
        success: bool,
        desktop_index: Optional[int] = None,
        desktop_count: Optional[int] = None
    ) -> EvaluationResult:
        """
        Evaluate Wallpaper Application Agent output.
        
        Args:
            success: Whether application was successful
            desktop_index: Selected desktop index
            desktop_count: Total desktop count
            
        Returns:
            EvaluationResult with metrics
        """
        from datetime import datetime
        
        metrics = {}
        warnings = []
        
        # 1. Application Success Rate
        success_score = 100.0 if success else 0.0
        metrics["application_success"] = EvaluationMetrics(
            score=success_score,
            threshold=95.0,
            passed=success_score >= 95.0,
        )
        
        # 2. Desktop Selection Correctness (if applicable)
        if desktop_index is not None and desktop_count is not None:
            # Check if selection follows rules: 2nd if 2+ exist, 1st if only 1
            expected_index = 1 if desktop_count >= 2 else 0
            selection_correct = (desktop_index == expected_index)
            selection_score = 100.0 if selection_correct else 50.0
            
            metrics["desktop_selection"] = EvaluationMetrics(
                score=selection_score,
                threshold=98.0,
                passed=selection_score >= 98.0,
            )
        
        # Calculate overall score
        overall_score = sum(m.score for m in metrics.values()) / len(metrics) if metrics else 0.0
        passed = all(m.passed for m in metrics.values()) if metrics else False
        
        return EvaluationResult(
            agent_name="WallpaperApplicationAgent",
            timestamp=datetime.now(),
            overall_score=overall_score,
            metrics=metrics,
            passed=passed,
            warnings=warnings,
            metadata={
                "success": success,
                "desktop_index": desktop_index,
                "desktop_count": desktop_count,
            },
        )

