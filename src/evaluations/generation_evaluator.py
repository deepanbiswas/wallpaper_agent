"""
Evaluator for Wallpaper Generation Agent.
"""
from pathlib import Path
from typing import Dict, Any
from .metrics import EvaluationResult, EvaluationMetrics
from utils.logger import get_logger


class GenerationEvaluator:
    """Evaluates Wallpaper Generation Agent output quality."""
    
    def __init__(self, llm_client=None):
        """
        Initialize Generation Evaluator.
        
        Args:
            llm_client: LLMClient instance (optional, for future LLM-based evaluations)
        """
        self.llm_client = llm_client
        self.logger = get_logger(__name__)
    
    def evaluate(
        self,
        wallpaper_path: Path,
        theme: Dict[str, Any]
    ) -> EvaluationResult:
        """
        Evaluate Wallpaper Generation Agent output.
        
        Args:
            wallpaper_path: Path to generated wallpaper
            theme: Selected theme
            
        Returns:
            EvaluationResult with metrics
        """
        from datetime import datetime
        
        metrics = {}
        warnings = []
        
        # 1. Image Quality Score
        quality_score = self._evaluate_image_quality(wallpaper_path)
        metrics["image_quality"] = EvaluationMetrics(
            score=quality_score,
            threshold=80.0,
            passed=quality_score >= 80.0,
        )
        
        # 2. Theme Adherence
        theme_score = self._evaluate_theme_adherence(wallpaper_path, theme)
        metrics["theme_adherence"] = EvaluationMetrics(
            score=theme_score,
            threshold=85.0,
            passed=theme_score >= 85.0,
        )
        
        # 3. Dark Theme Compliance
        dark_score = self._evaluate_dark_theme_compliance(wallpaper_path)
        metrics["dark_theme_compliance"] = EvaluationMetrics(
            score=dark_score,
            threshold=90.0,
            passed=dark_score >= 90.0,
        )
        if dark_score < 80.0:
            warnings.append(f"Low dark theme compliance: {dark_score:.1f}")
        
        # Calculate overall score
        overall_score = sum(m.score for m in metrics.values()) / len(metrics) if metrics else 0.0
        passed = all(m.passed for m in metrics.values()) if metrics else False
        
        return EvaluationResult(
            agent_name="WallpaperGenerationAgent",
            timestamp=datetime.now(),
            overall_score=overall_score,
            metrics=metrics,
            passed=passed,
            warnings=warnings,
            metadata={"wallpaper_path": str(wallpaper_path)},
        )
    
    def _evaluate_image_quality(self, image_path: Path) -> float:
        """Evaluate image quality (0-100)."""
        try:
            from PIL import Image
            
            if not image_path.exists():
                return 0.0
            
            img = Image.open(image_path)
            
            score = 0.0
            
            # Resolution check (40 points)
            width, height = img.size
            if width >= 2000 and height >= 1500:
                score += 40.0
            elif width >= 1000 and height >= 750:
                score += 20.0
            
            # Format check (20 points)
            if image_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                score += 20.0
            
            # File size check (20 points)
            file_size = image_path.stat().st_size
            if 100_000 <= file_size <= 10_000_000:  # 100KB to 10MB
                score += 20.0
            elif file_size > 0:
                score += 10.0
            
            # Image validity (20 points)
            try:
                img.verify()
                score += 20.0
            except Exception:
                pass
            
            return score
            
        except Exception:
            return 0.0
    
    def _evaluate_theme_adherence(
        self,
        image_path: Path,
        theme: Dict[str, Any]
    ) -> float:
        """Evaluate theme adherence (0-100)."""
        if not self.llm_client or not image_path.exists():
            return 75.0  # Default if can't evaluate
        
        theme_name = theme.get("name", "")
        theme_desc = theme.get("description", "")
        
        # For now, return default score
        # Could be enhanced with image analysis + LLM
        return 80.0
    
    def _evaluate_dark_theme_compliance(self, image_path: Path) -> float:
        """Evaluate dark theme compliance (0-100)."""
        try:
            from PIL import Image
            import numpy as np
            
            if not image_path.exists():
                return 0.0
            
            img = Image.open(image_path)
            img_array = np.array(img)
            
            # Calculate average brightness
            if len(img_array.shape) == 3:
                # RGB image
                brightness = np.mean(img_array)
            else:
                # Grayscale
                brightness = np.mean(img_array)
            
            # Dark theme: brightness should be low (< 128 for 0-255 scale)
            # Score: 100 if brightness < 50, decreases as brightness increases
            max_brightness = 255.0
            if brightness < 50:
                score = 100.0
            elif brightness < 100:
                score = 90.0 - ((brightness - 50) / 50) * 20.0
            elif brightness < 128:
                score = 70.0 - ((brightness - 100) / 28) * 20.0
            else:
                score = max(0.0, 50.0 - ((brightness - 128) / 127) * 50.0)
            
            return max(0.0, min(100.0, score))
            
        except Exception:
            return 50.0  # Default if can't evaluate

