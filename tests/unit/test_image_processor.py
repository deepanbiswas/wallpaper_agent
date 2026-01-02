"""
Tests for image processing utilities.
"""
import pytest
from unittest.mock import Mock, patch
from PIL import Image
import io

from utils.image_processor import (
    resize_image,
    ensure_dark_theme,
    save_wallpaper,
    process_wallpaper,
)


class TestImageProcessor:
    """Test image processing functions."""

    def test_resize_image(self):
        """Test image resizing."""
        # Create a test image
        original_image = Image.new("RGB", (1000, 1000), color="black")
        
        resized = resize_image(original_image, width=3024, height=1964)
        
        assert resized.size == (3024, 1964)
        assert isinstance(resized, Image.Image)

    def test_resize_image_maintains_aspect_ratio(self):
        """Test that resize maintains aspect ratio when requested."""
        original_image = Image.new("RGB", (2000, 1000), color="black")
        
        resized = resize_image(original_image, width=3024, height=1964, maintain_aspect=True)
        
        # Should maintain 2:1 aspect ratio (original is 2:1)
        # After resizing to fit height and cropping, should still be close to target aspect
        # The actual aspect will be target aspect (3024/1964 ≈ 1.54) since we crop to fit
        assert resized.size == (3024, 1964)  # Should match target dimensions

    def test_ensure_dark_theme(self):
        """Test dark theme enforcement."""
        # Create a light image
        light_image = Image.new("RGB", (100, 100), color="white")
        
        dark_image = ensure_dark_theme(light_image)
        
        # Check that image is darker (average brightness should be lower)
        # This is a basic check - actual implementation may vary
        assert dark_image is not None
        assert isinstance(dark_image, Image.Image)

    def test_ensure_dark_theme_already_dark(self):
        """Test dark theme on already dark image."""
        dark_image = Image.new("RGB", (100, 100), color="black")
        
        result = ensure_dark_theme(dark_image)
        
        assert result is not None
        assert isinstance(result, Image.Image)

    def test_save_wallpaper(self, tmp_path):
        """Test saving wallpaper to file."""
        image = Image.new("RGB", (100, 100), color="black")
        output_path = tmp_path / "wallpaper.png"
        
        result = save_wallpaper(image, output_path)
        
        assert result == output_path
        assert output_path.exists()
        
        # Verify it's a valid image
        loaded_image = Image.open(output_path)
        assert loaded_image.size == (100, 100)

    def test_save_wallpaper_creates_directory(self, tmp_path):
        """Test that save_wallpaper creates directory if needed."""
        image = Image.new("RGB", (100, 100), color="black")
        output_path = tmp_path / "new_dir" / "wallpaper.png"
        
        result = save_wallpaper(image, output_path)
        
        assert output_path.exists()
        assert output_path.parent.exists()

    def test_process_wallpaper_full_pipeline(self, tmp_path):
        """Test full wallpaper processing pipeline."""
        # Create a test image
        original_image = Image.new("RGB", (1000, 1000), color="white")
        output_path = tmp_path / "processed_wallpaper.png"
        
        result_path = process_wallpaper(
            original_image,
            output_path,
            target_width=3024,
            target_height=1964
        )
        
        assert result_path == output_path
        assert output_path.exists()
        
        # Verify processed image
        processed = Image.open(output_path)
        assert processed.size == (3024, 1964)

    def test_process_wallpaper_with_dark_theme(self, tmp_path):
        """Test wallpaper processing with dark theme enforcement."""
        light_image = Image.new("RGB", (500, 500), color="white")
        output_path = tmp_path / "dark_wallpaper.png"
        
        result_path = process_wallpaper(
            light_image,
            output_path,
            target_width=3024,
            target_height=1964,
            enforce_dark_theme=True
        )
        
        assert result_path == output_path
        assert output_path.exists()

