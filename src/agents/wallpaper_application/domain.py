"""
Domain model for Wallpaper Application Agent.
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from pathlib import Path


@dataclass
class ApplicationRequest:
    """Request for wallpaper application."""
    file_path: Path
    desktop_index: Optional[int] = None  # None = auto-select based on desktop count
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary."""
        return {
            "file_path": str(self.file_path),
            "desktop_index": self.desktop_index,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ApplicationRequest":
        """Create request from dictionary."""
        file_path = data.get("file_path")
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        return cls(
            file_path=file_path,
            desktop_index=data.get("desktop_index"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class ApplicationResult:
    """Result of wallpaper application."""
    success: bool
    desktop_index: Optional[int] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "desktop_index": self.desktop_index,
            "error": self.error,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ApplicationResult":
        """Create result from dictionary."""
        return cls(
            success=data.get("success", False),
            desktop_index=data.get("desktop_index"),
            error=data.get("error"),
            metadata=data.get("metadata", {}),
        )

