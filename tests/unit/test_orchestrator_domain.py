"""
Tests for Orchestrator Domain models, including error paths.
"""
import pytest
from pathlib import Path
from orchestrator.domain import OrchestrationStatus, OrchestrationResult


class TestOrchestrationStatus:
    """Test OrchestrationStatus enum."""
    
    def test_status_values(self):
        """Test status enum values."""
        assert OrchestrationStatus.SUCCESS.value == "success"
        assert OrchestrationStatus.FAILED.value == "failed"
        assert OrchestrationStatus.PARTIAL.value == "partial"
    
    def test_status_from_string(self):
        """Test creating status from string."""
        assert OrchestrationStatus("success") == OrchestrationStatus.SUCCESS
        assert OrchestrationStatus("failed") == OrchestrationStatus.FAILED
        assert OrchestrationStatus("partial") == OrchestrationStatus.PARTIAL
    
    def test_status_invalid_value(self):
        """Test creating status with invalid value."""
        with pytest.raises(ValueError):
            OrchestrationStatus("invalid")


class TestOrchestrationResult:
    """Test OrchestrationResult dataclass."""
    
    def test_result_creation_success(self):
        """Test creating success result."""
        result = OrchestrationResult(
            status=OrchestrationStatus.SUCCESS,
            selected_theme={"name": "Diwali"},
            wallpaper_path=Path("/tmp/wallpaper.png"),
        )
        
        assert result.status == OrchestrationStatus.SUCCESS
        assert result.selected_theme["name"] == "Diwali"
        assert result.wallpaper_path == Path("/tmp/wallpaper.png")
        assert result.error is None
    
    def test_result_creation_failed(self):
        """Test creating failed result."""
        result = OrchestrationResult(
            status=OrchestrationStatus.FAILED,
            error="Theme discovery failed",
        )
        
        assert result.status == OrchestrationStatus.FAILED
        assert result.error == "Theme discovery failed"
        assert result.selected_theme is None
        assert result.wallpaper_path is None
    
    def test_result_creation_partial(self):
        """Test creating partial success result."""
        result = OrchestrationResult(
            status=OrchestrationStatus.PARTIAL,
            selected_theme={"name": "Diwali"},
            wallpaper_path=Path("/tmp/wallpaper.png"),
            error="Wallpaper generated but application failed",
        )
        
        assert result.status == OrchestrationStatus.PARTIAL
        assert result.selected_theme is not None
        assert result.wallpaper_path is not None
        assert result.error is not None
    
    def test_result_to_dict_success(self):
        """Test converting success result to dictionary."""
        result = OrchestrationResult(
            status=OrchestrationStatus.SUCCESS,
            selected_theme={"name": "Diwali", "type": "indian_cultural"},
            wallpaper_path=Path("/tmp/wallpaper.png"),
            metadata={"wallpaper_size": 1024000},
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["status"] == "success"
        assert result_dict["selected_theme"]["name"] == "Diwali"
        assert result_dict["wallpaper_path"] == "/tmp/wallpaper.png"
        assert result_dict["error"] is None
        assert result_dict["metadata"]["wallpaper_size"] == 1024000
    
    def test_result_to_dict_failed(self):
        """Test converting failed result to dictionary."""
        result = OrchestrationResult(
            status=OrchestrationStatus.FAILED,
            error="API connection failed",
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["status"] == "failed"
        assert result_dict["error"] == "API connection failed"
        assert result_dict["selected_theme"] is None
        assert result_dict["wallpaper_path"] is None
    
    def test_result_to_dict_none_path(self):
        """Test converting result with None path to dictionary."""
        result = OrchestrationResult(
            status=OrchestrationStatus.FAILED,
            wallpaper_path=None,
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["wallpaper_path"] is None
    
    def test_result_from_dict_success(self):
        """Test creating result from dictionary (success)."""
        data = {
            "status": "success",
            "selected_theme": {"name": "Diwali"},
            "wallpaper_path": "/tmp/wallpaper.png",
            "error": None,
            "metadata": {},
        }
        
        result = OrchestrationResult.from_dict(data)
        
        assert result.status == OrchestrationStatus.SUCCESS
        assert result.selected_theme["name"] == "Diwali"
        assert result.wallpaper_path == Path("/tmp/wallpaper.png")
        assert result.error is None
    
    def test_result_from_dict_failed(self):
        """Test creating result from dictionary (failed)."""
        data = {
            "status": "failed",
            "selected_theme": None,
            "wallpaper_path": None,
            "error": "Theme discovery failed",
            "metadata": {},
        }
        
        result = OrchestrationResult.from_dict(data)
        
        assert result.status == OrchestrationStatus.FAILED
        assert result.error == "Theme discovery failed"
        assert result.selected_theme is None
        assert result.wallpaper_path is None
    
    def test_result_from_dict_partial(self):
        """Test creating result from dictionary (partial)."""
        data = {
            "status": "partial",
            "selected_theme": {"name": "New Year"},
            "wallpaper_path": "/tmp/new_year.png",
            "error": "Application failed",
            "metadata": {"attempts": 3},
        }
        
        result = OrchestrationResult.from_dict(data)
        
        assert result.status == OrchestrationStatus.PARTIAL
        assert result.selected_theme["name"] == "New Year"
        assert result.wallpaper_path == Path("/tmp/new_year.png")
        assert result.error == "Application failed"
        assert result.metadata["attempts"] == 3
    
    def test_result_from_dict_no_status(self):
        """Test creating result from dictionary without status (defaults to failed)."""
        data = {
            "error": "Unknown error",
        }
        
        result = OrchestrationResult.from_dict(data)
        
        assert result.status == OrchestrationStatus.FAILED
        assert result.error == "Unknown error"
    
    def test_result_from_dict_no_path(self):
        """Test creating result from dictionary without wallpaper_path."""
        data = {
            "status": "failed",
            "wallpaper_path": None,
        }
        
        result = OrchestrationResult.from_dict(data)
        
        assert result.wallpaper_path is None
    
    def test_result_from_dict_string_path(self):
        """Test creating result from dictionary with string path."""
        data = {
            "status": "success",
            "wallpaper_path": "/tmp/wallpaper.png",
        }
        
        result = OrchestrationResult.from_dict(data)
        
        assert isinstance(result.wallpaper_path, Path)
        assert result.wallpaper_path == Path("/tmp/wallpaper.png")
    
    def test_result_from_dict_empty_metadata(self):
        """Test creating result from dictionary with empty metadata."""
        data = {
            "status": "success",
            "metadata": {},
        }
        
        result = OrchestrationResult.from_dict(data)
        
        assert result.metadata == {}
    
    def test_result_from_dict_no_metadata(self):
        """Test creating result from dictionary without metadata."""
        data = {
            "status": "success",
        }
        
        result = OrchestrationResult.from_dict(data)
        
        assert result.metadata == {}
    
    def test_result_metadata_default(self):
        """Test result with default metadata."""
        result = OrchestrationResult(status=OrchestrationStatus.SUCCESS)
        
        assert result.metadata == {}
        assert isinstance(result.metadata, dict)
    
    def test_result_round_trip(self):
        """Test round-trip conversion (to_dict -> from_dict)."""
        original = OrchestrationResult(
            status=OrchestrationStatus.PARTIAL,
            selected_theme={"name": "Diwali", "type": "indian_cultural"},
            wallpaper_path=Path("/tmp/diwali.png"),
            error="Application timeout",
            metadata={"retries": 2, "duration": 45.5},
        )
        
        result_dict = original.to_dict()
        restored = OrchestrationResult.from_dict(result_dict)
        
        assert restored.status == original.status
        assert restored.selected_theme == original.selected_theme
        assert restored.wallpaper_path == original.wallpaper_path
        assert restored.error == original.error
        assert restored.metadata == original.metadata

