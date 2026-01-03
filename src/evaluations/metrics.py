"""
Evaluation metrics and result models.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime


@dataclass
class EvaluationMetrics:
    """Metrics for a single evaluation."""
    score: float  # 0-100
    threshold: float  # Minimum acceptable score
    passed: bool
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "score": self.score,
            "threshold": self.threshold,
            "passed": self.passed,
            "details": self.details,
        }


@dataclass
class EvaluationResult:
    """Result of agent evaluation."""
    agent_name: str
    timestamp: datetime
    overall_score: float  # Average of all metrics
    metrics: Dict[str, EvaluationMetrics] = field(default_factory=dict)
    passed: bool = True
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_name": self.agent_name,
            "timestamp": self.timestamp.isoformat(),
            "overall_score": self.overall_score,
            "metrics": {k: v.to_dict() for k, v in self.metrics.items()},
            "passed": self.passed,
            "warnings": self.warnings,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvaluationResult":
        """Create from dictionary."""
        from datetime import datetime
        timestamp = datetime.fromisoformat(data["timestamp"])
        
        metrics = {}
        for k, v in data.get("metrics", {}).items():
            metrics[k] = EvaluationMetrics(**v)
        
        return cls(
            agent_name=data["agent_name"],
            timestamp=timestamp,
            overall_score=data["overall_score"],
            metrics=metrics,
            passed=data.get("passed", True),
            warnings=data.get("warnings", []),
            metadata=data.get("metadata", {}),
        )

