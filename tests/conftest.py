"""
Pytest configuration and shared fixtures.
"""
import os
import sys
from pathlib import Path

# Add src directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

import pytest
from unittest.mock import Mock, MagicMock


@pytest.fixture
def sample_theme_data():
    """Sample theme data for testing."""
    return {
        "themes": [
            {
                "name": "Diwali",
                "type": "indian_cultural",
                "description": "Festival of Lights",
                "priority": "high"
            },
            {
                "name": "New Year",
                "type": "global",
                "description": "New Year Celebration",
                "priority": "medium"
            }
        ]
    }


@pytest.fixture
def mock_api_response():
    """Mock API response for testing."""
    return {
        "status": "success",
        "data": {"result": "test_data"}
    }


@pytest.fixture
def temp_wallpaper_dir(tmp_path):
    """Temporary directory for wallpapers during testing."""
    wallpaper_dir = tmp_path / "wallpapers"
    wallpaper_dir.mkdir()
    return wallpaper_dir


@pytest.fixture
def temp_log_dir(tmp_path):
    """Temporary directory for logs during testing."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return log_dir


@pytest.fixture
def mock_osascript(monkeypatch):
    """Mock osascript command for testing wallpaper application."""
    def mock_run(*args, **kwargs):
        return Mock(returncode=0, stdout="", stderr="")
    
    monkeypatch.setattr("subprocess.run", mock_run)
    return mock_run

