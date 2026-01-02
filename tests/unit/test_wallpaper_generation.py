"""
Tests for Wallpaper Generation Agent.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
from pathlib import Path
from agents.wallpaper_generation.agent import WallpaperGenerationAgent
from agents.wallpaper_generation.domain import WallpaperRequest, WallpaperResult


class TestWallpaperGenerationAgent:
    """Test Wallpaper Generation Agent."""
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = WallpaperGenerationAgent()
        assert agent is not None
        assert hasattr(agent, 'image_client')
        assert hasattr(agent, 'config')
    
    def test_agent_initialization_with_custom_clients(self):
        """Test agent initialization with custom clients."""
        mock_image_client = Mock()
        mock_config = Mock()
        
        # Mock get_wallpaper_config to return proper dict
        with patch('agents.wallpaper_generation.agent.get_wallpaper_config') as mock_get_config:
            mock_get_config.return_value = {
                "width": 3024,
                "height": 1964,
                "directory": "./wallpapers",
            }
            
            agent = WallpaperGenerationAgent(
                config=mock_config,
                image_client=mock_image_client,
            )
            
            assert agent.image_client == mock_image_client
            assert agent.config == mock_config
    
    @patch('agents.wallpaper_generation.agent.PollinationsClient')
    @patch('PIL.Image.open')
    def test_generate_wallpaper_success(self, mock_image_open, mock_client_class):
        """Test successful wallpaper generation."""
        # Mock image client
        mock_client = MagicMock()
        mock_client.generate_image.return_value = b"fake_image_data"
        mock_client_class.return_value = mock_client
        
        # Mock PIL Image
        mock_image = MagicMock()
        mock_image_open.return_value = mock_image
        
        # Mock image processor
        with patch('agents.wallpaper_generation.agent.process_wallpaper') as mock_process:
            mock_process.return_value = Path("/tmp/wallpaper.jpg")
            
            agent = WallpaperGenerationAgent(image_client=mock_client)
            
            request = WallpaperRequest(
                theme_name="Diwali",
                style_guidelines={
                    "prompt": "Minimalistic dark-themed wallpaper",
                    "color_palette": ["#1a1a1a", "#2d2d2d"],
                },
                width=3024,
                height=1964,
            )
            
            result = agent.generate_wallpaper(request)
            
            assert result is not None
            assert result.success is True
            assert result.file_path is not None
            mock_client.generate_image.assert_called_once()
            mock_process.assert_called_once()
    
    @patch('agents.wallpaper_generation.agent.PollinationsClient')
    def test_generate_wallpaper_image_generation_failure(self, mock_client_class):
        """Test handling of image generation failure."""
        mock_client = MagicMock()
        mock_client.generate_image.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        
        agent = WallpaperGenerationAgent(image_client=mock_client)
        
        request = WallpaperRequest(
            theme_name="Test Theme",
            style_guidelines={"prompt": "Test prompt"},
            width=3024,
            height=1964,
        )
        
        result = agent.generate_wallpaper(request)
        
        assert result is not None
        assert result.success is False
        assert result.error is not None
    
    @patch('agents.wallpaper_generation.agent.PollinationsClient')
    def test_generate_wallpaper_image_processing_failure(self, mock_client_class):
        """Test handling of image processing failure."""
        mock_client = MagicMock()
        mock_client.generate_image.return_value = b"fake_image_data"
        mock_client_class.return_value = mock_client
        
        with patch('agents.wallpaper_generation.agent.process_wallpaper') as mock_process:
            mock_process.side_effect = Exception("Processing Error")
            
            agent = WallpaperGenerationAgent(image_client=mock_client)
            
            request = WallpaperRequest(
                theme_name="Test Theme",
                style_guidelines={"prompt": "Test prompt"},
                width=3024,
                height=1964,
            )
            
            result = agent.generate_wallpaper(request)
            
            assert result is not None
            assert result.success is False
            assert result.error is not None
    
    @patch('agents.wallpaper_generation.agent.PollinationsClient')
    def test_generate_wallpaper_builds_prompt(self, mock_client_class):
        """Test that agent builds proper prompt for image generation."""
        mock_client = MagicMock()
        mock_client.generate_image.return_value = b"fake_image_data"
        mock_client_class.return_value = mock_client
        
        with patch('agents.wallpaper_generation.agent.process_wallpaper') as mock_process:
            mock_process.return_value = Path("/tmp/wallpaper.jpg")
            
            agent = WallpaperGenerationAgent(image_client=mock_client)
            
            request = WallpaperRequest(
                theme_name="Diwali",
                style_guidelines={
                    "prompt": "Minimalistic dark-themed wallpaper featuring Diwali",
                    "color_palette": ["#1a1a1a", "#2d2d2d"],
                    "key_elements": ["lights", "diya"],
                },
                width=3024,
                height=1964,
            )
            
            result = agent.generate_wallpaper(request)
            
            # Verify prompt was built correctly
            call_args = mock_client.generate_image.call_args
            assert call_args is not None
            prompt = call_args[0][0] if call_args[0] else call_args[1].get('prompt', '')
            assert "Diwali" in prompt or "diwali" in prompt.lower()
    
    @patch('agents.wallpaper_generation.agent.PollinationsClient')
    def test_generate_wallpaper_uses_style_guidelines(self, mock_client_class):
        """Test that agent uses style guidelines in prompt."""
        mock_client = MagicMock()
        mock_client.generate_image.return_value = b"fake_image_data"
        mock_client_class.return_value = mock_client
        
        with patch('agents.wallpaper_generation.agent.process_wallpaper') as mock_process:
            mock_process.return_value = Path("/tmp/wallpaper.jpg")
            
            agent = WallpaperGenerationAgent(image_client=mock_client)
            
            request = WallpaperRequest(
                theme_name="Test Theme",
                style_guidelines={
                    "prompt": "Custom prompt from style guidelines",
                    "color_palette": ["#000000"],
                },
                width=3024,
                height=1964,
            )
            
            result = agent.generate_wallpaper(request)
            
            # Verify custom prompt was used
            call_args = mock_client.generate_image.call_args
            prompt = call_args[0][0] if call_args[0] else call_args[1].get('prompt', '')
            assert "Custom prompt" in prompt
    
    @patch('agents.wallpaper_generation.agent.PollinationsClient')
    @patch('PIL.Image.open')
    def test_generate_wallpaper_default_dimensions(self, mock_image_open, mock_client_class):
        """Test that agent uses default dimensions from config."""
        mock_client = MagicMock()
        mock_client.generate_image.return_value = b"fake_image_data"
        mock_client_class.return_value = mock_client
        
        # Mock PIL Image
        mock_image = MagicMock()
        mock_image_open.return_value = mock_image
        
        mock_config = Mock()
        
        with patch('agents.wallpaper_generation.agent.get_wallpaper_config') as mock_get_config:
            mock_get_config.return_value = {
                "width": 3024,
                "height": 1964,
                "directory": "./wallpapers",
            }
            
            with patch('agents.wallpaper_generation.agent.process_wallpaper') as mock_process:
                mock_process.return_value = Path("/tmp/wallpaper.jpg")
                
                agent = WallpaperGenerationAgent(config=mock_config, image_client=mock_client)
                
                request = WallpaperRequest(
                    theme_name="Test Theme",
                    style_guidelines={"prompt": "Test prompt"},
                    # No width/height specified
                )
                
                result = agent.generate_wallpaper(request)
                
                # Verify process_wallpaper was called with config dimensions
                mock_process.assert_called_once()
                call_kwargs = mock_process.call_args[1]  # keyword arguments
                # Check that dimensions match config
                assert call_kwargs.get("target_width") == 3024
                assert call_kwargs.get("target_height") == 1964
    
    def test_build_prompt_from_style_guidelines(self):
        """Test building prompt from style guidelines."""
        agent = WallpaperGenerationAgent()
        
        style_guidelines = {
            "prompt": "Minimalistic dark-themed wallpaper",
            "color_palette": ["#1a1a1a", "#2d2d2d"],
            "key_elements": ["lights", "diya"],
        }
        
        prompt = agent._build_prompt("Diwali", style_guidelines)
        
        assert "Diwali" in prompt
        assert "dark" in prompt.lower() or "minimalistic" in prompt.lower()
    
    def test_build_prompt_fallback(self):
        """Test prompt building with minimal style guidelines."""
        agent = WallpaperGenerationAgent()
        
        style_guidelines = {
            "prompt": "Simple prompt",
        }
        
        prompt = agent._build_prompt("Test Theme", style_guidelines)
        
        assert "Test Theme" in prompt
        assert "Simple prompt" in prompt
    
    def test_validate_request(self):
        """Test request validation."""
        agent = WallpaperGenerationAgent()
        
        # Valid request
        valid_request = WallpaperRequest(
            theme_name="Test",
            style_guidelines={"prompt": "Test"},
            width=3024,
            height=1964,
        )
        assert agent._validate_request(valid_request) is True
        
        # Invalid request - missing theme name
        invalid_request = WallpaperRequest(
            theme_name="",
            style_guidelines={"prompt": "Test"},
        )
        assert agent._validate_request(invalid_request) is False
    
    @patch('agents.wallpaper_generation.agent.PollinationsClient')
    def test_generate_wallpaper_invalid_request(self, mock_client_class):
        """Test handling of invalid request."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        agent = WallpaperGenerationAgent(image_client=mock_client)
        
        invalid_request = WallpaperRequest(
            theme_name="",  # Invalid
            style_guidelines={},
        )
        
        result = agent.generate_wallpaper(invalid_request)
        
        assert result is not None
        assert result.success is False
        assert result.error is not None
        mock_client.generate_image.assert_not_called()

