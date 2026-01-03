"""
Domain models for Orchestrator.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any
from pathlib import Path


class OrchestrationStatus(Enum):
    """Status of orchestration execution."""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"  # Some steps succeeded but not all


@dataclass
class OrchestrationResult:
    """Result of orchestration execution."""
    status: OrchestrationStatus
    selected_theme: Optional[Dict[str, Any]] = None
    wallpaper_path: Optional[Path] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "status": self.status.value,
            "selected_theme": self.selected_theme,
            "wallpaper_path": str(self.wallpaper_path) if self.wallpaper_path else None,
            "error": self.error,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OrchestrationResult":
        """Create result from dictionary."""
        status = OrchestrationStatus(data.get("status", "failed"))
        wallpaper_path = data.get("wallpaper_path")
        if wallpaper_path:
            wallpaper_path = Path(wallpaper_path)
        
        return cls(
            status=status,
            selected_theme=data.get("selected_theme"),
            wallpaper_path=wallpaper_path,
            error=data.get("error"),
            metadata=data.get("metadata", {}),
        )

