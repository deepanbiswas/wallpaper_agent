"""
Domain model for Theme Selection Agent.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class Theme:
    """Theme domain model with scoring capabilities."""
    name: str
    description: str = ""
    type: str = ""  # indian_cultural, indian_achievement, global
    source: str = "search"
    
    # Scoring fields
    base_score: float = 0.0
    llm_score: float = 0.0
    final_score: float = 0.0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert theme to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "source": self.source,
            "base_score": self.base_score,
            "llm_score": self.llm_score,
            "final_score": self.final_score,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Theme":
        """Create theme from dictionary."""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            type=data.get("type", ""),
            source=data.get("source", "search"),
            base_score=data.get("base_score", 0.0),
            llm_score=data.get("llm_score", 0.0),
            final_score=data.get("final_score", 0.0),
            metadata=data.get("metadata", {}),
        )

