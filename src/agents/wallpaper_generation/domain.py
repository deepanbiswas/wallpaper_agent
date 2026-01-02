"""
Domain model for Wallpaper Generation Agent.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from pathlib import Path


@dataclass
class WallpaperRequest:
    """Request for wallpaper generation."""
    theme_name: str
    style_guidelines: Dict[str, Any]
    width: Optional[int] = None
    height: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary."""
        return {
            "theme_name": self.theme_name,
            "style_guidelines": self.style_guidelines,
            "width": self.width,
            "height": self.height,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WallpaperRequest":
        """Create request from dictionary."""
        return cls(
            theme_name=data.get("theme_name", ""),
            style_guidelines=data.get("style_guidelines", {}),
            width=data.get("width"),
            height=data.get("height"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class WallpaperResult:
    """Result of wallpaper generation."""
    success: bool
    file_path: Optional[Path] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "file_path": str(self.file_path) if self.file_path else None,
            "error": self.error,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WallpaperResult":
        """Create result from dictionary."""
        file_path = data.get("file_path")
        if file_path:
            file_path = Path(file_path)
        
        return cls(
            success=data.get("success", False),
            file_path=file_path,
            error=data.get("error"),
            metadata=data.get("metadata", {}),
        )

