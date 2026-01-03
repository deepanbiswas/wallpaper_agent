"""
Tests for Generation Evaluator edge cases and image processing.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
from PIL import Image
import numpy as np
from evaluations.generation_evaluator import GenerationEvaluator


class TestGenerationEvaluatorEdgeCases:
    """Test Generation Evaluator edge cases."""
    
    def test_evaluate_image_quality_file_not_exists(self, tmp_path):
        """Test image quality evaluation when file doesn't exist."""
        evaluator = GenerationEvaluator()
        
        non_existent_path = tmp_path / "nonexistent.png"
        score = evaluator._evaluate_image_quality(non_existent_path)
        
        assert score == 0.0
    
    def test_evaluate_image_quality_low_resolution(self, tmp_path):
        """Test image quality with low resolution."""
        evaluator = GenerationEvaluator()
        
        # Create a small image (500x400)
        img = Image.new('RGB', (500, 400), color='black')
        image_path = tmp_path / "small.png"
        img.save(image_path)
        
        score = evaluator._evaluate_image_quality(image_path)
        
        # Should get some points for format and file size, but not full resolution points
        assert 0.0 <= score <= 100.0
        assert score < 60.0  # Should not get full resolution points (40) + format (20)
    
    def test_evaluate_image_quality_medium_resolution(self, tmp_path):
        """Test image quality with medium resolution."""
        evaluator = GenerationEvaluator()
        
        # Create a medium image (1200x900)
        img = Image.new('RGB', (1200, 900), color='black')
        image_path = tmp_path / "medium.png"
        img.save(image_path)
        
        score = evaluator._evaluate_image_quality(image_path)
        
        # Should get partial resolution points
        assert score >= 20.0  # At least medium resolution points
    
    def test_evaluate_image_quality_high_resolution(self, tmp_path):
        """Test image quality with high resolution."""
        evaluator = GenerationEvaluator()
        
        # Create a high-res image (3000x2000)
        img = Image.new('RGB', (3000, 2000), color='black')
        image_path = tmp_path / "highres.png"
        img.save(image_path)
        
        score = evaluator._evaluate_image_quality(image_path)
        
        # Should get full resolution points
        assert score >= 40.0
    
    def test_evaluate_image_quality_invalid_format(self, tmp_path):
        """Test image quality with invalid format."""
        evaluator = GenerationEvaluator()
        
        # Create a file with invalid extension
        invalid_path = tmp_path / "image.txt"
        invalid_path.write_text("not an image")
        
        score = evaluator._evaluate_image_quality(invalid_path)
        
        # Should handle gracefully
        assert 0.0 <= score <= 100.0
    
    def test_evaluate_image_quality_small_file_size(self, tmp_path):
        """Test image quality with very small file size."""
        evaluator = GenerationEvaluator()
        
        # Create a very small image
        img = Image.new('RGB', (100, 100), color='black')
        image_path = tmp_path / "tiny.png"
        img.save(image_path, optimize=True)
        
        score = evaluator._evaluate_image_quality(image_path)
        
        # Should get partial file size points
        assert 0.0 <= score <= 100.0
    
    def test_evaluate_image_quality_large_file_size(self, tmp_path):
        """Test image quality with very large file size."""
        evaluator = GenerationEvaluator()
        
        # Create a large image (uncompressed)
        img = Image.new('RGB', (5000, 5000), color='black')
        image_path = tmp_path / "large.png"
        img.save(image_path)
        
        score = evaluator._evaluate_image_quality(image_path)
        
        # Should handle large files
        assert 0.0 <= score <= 100.0
    
    def test_evaluate_image_quality_image_verify_fails(self, tmp_path):
        """Test image quality when image.verify() fails."""
        evaluator = GenerationEvaluator()
        
        # Create a corrupted image file
        corrupted_path = tmp_path / "corrupted.png"
        corrupted_path.write_bytes(b'PNG\x00\x00\x00\x00invalid')
        
        with patch('PIL.Image.open') as mock_open:
            mock_img = MagicMock()
            mock_img.size = (2000, 1500)
            mock_img.verify.side_effect = Exception("Invalid image")
            mock_open.return_value = mock_img
            
            score = evaluator._evaluate_image_quality(corrupted_path)
            
            # Should still get points for resolution, format, file size
            # but not for image validity
            assert 0.0 <= score <= 100.0
            assert score < 100.0  # Should not get full score
    
    def test_evaluate_image_quality_exception_handling(self, tmp_path):
        """Test image quality evaluation exception handling."""
        evaluator = GenerationEvaluator()
        
        image_path = tmp_path / "test.png"
        
        with patch('PIL.Image.open', side_effect=Exception("IO Error")):
            score = evaluator._evaluate_image_quality(image_path)
            
            assert score == 0.0
    
    def test_evaluate_dark_theme_compliance_file_not_exists(self, tmp_path):
        """Test dark theme compliance when file doesn't exist."""
        evaluator = GenerationEvaluator()
        
        non_existent_path = tmp_path / "nonexistent.png"
        score = evaluator._evaluate_dark_theme_compliance(non_existent_path)
        
        assert score == 0.0
    
    def test_evaluate_dark_theme_compliance_very_dark(self, tmp_path):
        """Test dark theme compliance with very dark image."""
        evaluator = GenerationEvaluator()
        
        # Create a very dark image (brightness < 50)
        img_array = np.zeros((100, 100, 3), dtype=np.uint8)  # All black
        img = Image.fromarray(img_array)
        image_path = tmp_path / "very_dark.png"
        img.save(image_path)
        
        score = evaluator._evaluate_dark_theme_compliance(image_path)
        
        assert score == 100.0
    
    def test_evaluate_dark_theme_compliance_dark(self, tmp_path):
        """Test dark theme compliance with dark image."""
        evaluator = GenerationEvaluator()
        
        # Create a dark image (brightness ~75)
        img_array = np.full((100, 100, 3), 75, dtype=np.uint8)
        img = Image.fromarray(img_array)
        image_path = tmp_path / "dark.png"
        img.save(image_path)
        
        score = evaluator._evaluate_dark_theme_compliance(image_path)
        
        # Should get high score (between 70-90)
        assert 70.0 <= score <= 90.0
    
    def test_evaluate_dark_theme_compliance_medium(self, tmp_path):
        """Test dark theme compliance with medium brightness image."""
        evaluator = GenerationEvaluator()
        
        # Create a medium brightness image (brightness ~110)
        img_array = np.full((100, 100, 3), 110, dtype=np.uint8)
        img = Image.fromarray(img_array)
        image_path = tmp_path / "medium.png"
        img.save(image_path)
        
        score = evaluator._evaluate_dark_theme_compliance(image_path)
        
        # Should get lower score (between 50-70)
        assert 50.0 <= score <= 70.0
    
    def test_evaluate_dark_theme_compliance_bright(self, tmp_path):
        """Test dark theme compliance with bright image."""
        evaluator = GenerationEvaluator()
        
        # Create a bright image (brightness > 128)
        img_array = np.full((100, 100, 3), 200, dtype=np.uint8)
        img = Image.fromarray(img_array)
        image_path = tmp_path / "bright.png"
        img.save(image_path)
        
        score = evaluator._evaluate_dark_theme_compliance(image_path)
        
        # Should get low score (< 50)
        assert 0.0 <= score < 50.0
    
    def test_evaluate_dark_theme_compliance_grayscale(self, tmp_path):
        """Test dark theme compliance with grayscale image."""
        evaluator = GenerationEvaluator()
        
        # Create a grayscale image
        img_array = np.full((100, 100), 50, dtype=np.uint8)  # Dark grayscale
        img = Image.fromarray(img_array, mode='L')
        image_path = tmp_path / "grayscale.png"
        img.save(image_path)
        
        score = evaluator._evaluate_dark_theme_compliance(image_path)
        
        # Should handle grayscale correctly
        assert 0.0 <= score <= 100.0
        assert score >= 80.0  # Dark grayscale should score high
    
    def test_evaluate_dark_theme_compliance_exception_handling(self, tmp_path):
        """Test dark theme compliance exception handling."""
        evaluator = GenerationEvaluator()
        
        image_path = tmp_path / "test.png"
        
        with patch('PIL.Image.open', side_effect=Exception("IO Error")):
            score = evaluator._evaluate_dark_theme_compliance(image_path)
            
            # Should return default fallback (50.0) or 0.0 if file doesn't exist check happens first
            assert score in [0.0, 50.0]
    
    def test_evaluate_dark_theme_compliance_numpy_error(self, tmp_path):
        """Test dark theme compliance when numpy conversion fails."""
        evaluator = GenerationEvaluator()
        
        image_path = tmp_path / "test.png"
        img = Image.new('RGB', (100, 100), color='black')
        img.save(image_path)
        
        with patch('numpy.array', side_effect=Exception("Numpy error")):
            score = evaluator._evaluate_dark_theme_compliance(image_path)
            
            assert score == 50.0  # Default fallback
    
    def test_evaluate_theme_adherence_no_llm_client(self, tmp_path):
        """Test theme adherence without LLM client."""
        evaluator = GenerationEvaluator(llm_client=None)
        
        image_path = tmp_path / "test.png"
        img = Image.new('RGB', (100, 100), color='black')
        img.save(image_path)
        
        theme = {"name": "Diwali", "description": "Festival"}
        score = evaluator._evaluate_theme_adherence(image_path, theme)
        
        assert score == 75.0  # Default score
    
    def test_evaluate_theme_adherence_file_not_exists(self, tmp_path):
        """Test theme adherence when file doesn't exist."""
        evaluator = GenerationEvaluator()
        
        non_existent_path = tmp_path / "nonexistent.png"
        theme = {"name": "Diwali"}
        score = evaluator._evaluate_theme_adherence(non_existent_path, theme)
        
        assert score == 75.0  # Default score
    
    def test_evaluate_full_pipeline_edge_cases(self, tmp_path):
        """Test full evaluation pipeline with edge cases."""
        evaluator = GenerationEvaluator()
        
        # Create a valid but low-quality image
        img = Image.new('RGB', (500, 400), color=(200, 200, 200))  # Bright, small
        image_path = tmp_path / "low_quality.png"
        img.save(image_path)
        
        theme = {"name": "Test", "description": "Test theme"}
        result = evaluator.evaluate(image_path, theme)
        
        assert result.agent_name == "WallpaperGenerationAgent"
        assert "image_quality" in result.metrics
        assert "theme_adherence" in result.metrics
        assert "dark_theme_compliance" in result.metrics
        assert result.overall_score >= 0.0
        # Should have warnings for low dark theme compliance
        assert len(result.warnings) > 0 or result.metrics["dark_theme_compliance"].score < 80.0

