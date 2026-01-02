"""
Tests for API client utilities.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import requests

from api_clients import (
    DuckDuckGoClient,
    PollinationsClient,
    LLMClient,
)


class TestDuckDuckGoClient:
    """Test DuckDuckGo search client."""

    def test_duckduckgo_client_initialization(self):
        """Test DuckDuckGo client initialization."""
        client = DuckDuckGoClient()
        assert client is not None

    @patch('api_clients.duckduckgo_client.DDGS')
    def test_search_themes(self, mock_ddgs_class):
        """Test searching for themes."""
        # Mock search results
        mock_results = [
            {"title": "Diwali 2024", "body": "Festival of Lights"},
            {"title": "ISRO Launch", "body": "Rocket launch news"},
        ]
        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.__enter__ = MagicMock(return_value=mock_ddgs_instance)
        mock_ddgs_instance.__exit__ = MagicMock(return_value=False)
        mock_ddgs_instance.text.return_value = mock_results
        mock_ddgs_class.return_value = mock_ddgs_instance

        client = DuckDuckGoClient()
        results = client.search_themes("Indian festivals")

        assert len(results) == 2
        assert results[0]["title"] == "Diwali 2024"
        mock_ddgs_instance.text.assert_called_once()

    @patch('api_clients.duckduckgo_client.DDGS')
    def test_search_themes_empty_results(self, mock_ddgs):
        """Test search with empty results."""
        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = []
        mock_ddgs.return_value = mock_ddgs_instance

        client = DuckDuckGoClient()
        results = client.search_themes("nonexistent query")

        assert results == []

    @patch('api_clients.duckduckgo_client.DDGS')
    def test_search_themes_error_handling(self, mock_ddgs):
        """Test error handling in search."""
        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.side_effect = Exception("API Error")
        mock_ddgs.return_value = mock_ddgs_instance

        client = DuckDuckGoClient()
        results = client.search_themes("test query")

        assert results == []


class TestPollinationsClient:
    """Test Pollinations.ai image generation client."""

    def test_pollinations_client_initialization(self):
        """Test Pollinations client initialization."""
        client = PollinationsClient()
        assert client.base_url == "https://image.pollinations.ai/prompt/"

    @patch('api_clients.pollinations_client.requests.get')
    def test_generate_image_success(self, mock_get):
        """Test successful image generation."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"fake_image_data"
        mock_get.return_value = mock_response

        client = PollinationsClient()
        image_data = client.generate_image("minimalistic dark theme wallpaper")

        assert image_data == b"fake_image_data"
        mock_get.assert_called_once()

    @patch('api_clients.pollinations_client.requests.get')
    def test_generate_image_with_parameters(self, mock_get):
        """Test image generation with custom parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"image_data"
        mock_get.return_value = mock_response

        client = PollinationsClient()
        image_data = client.generate_image(
            "test prompt",
            width=3024,
            height=1964,
            model="flux"
        )

        assert image_data == b"image_data"
        # Verify URL contains parameters
        call_args = mock_get.call_args
        assert "3024" in call_args[0][0] or "width=3024" in str(call_args)

    @patch('api_clients.pollinations_client.requests.get')
    def test_generate_image_error_handling(self, mock_get):
        """Test error handling in image generation."""
        mock_get.side_effect = requests.RequestException("Network error")

        client = PollinationsClient()
        image_data = client.generate_image("test prompt")

        assert image_data is None

    @patch('api_clients.pollinations_client.requests.get')
    def test_generate_image_http_error(self, mock_get):
        """Test handling of HTTP errors."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        client = PollinationsClient()
        image_data = client.generate_image("test prompt")

        assert image_data is None


class TestLLMClient:
    """Test LLM client (Anthropic/OpenAI)."""

    def test_llm_client_initialization_anthropic(self):
        """Test LLM client initialization with Anthropic."""
        client = LLMClient(provider="anthropic", api_key="test_key")
        assert client.provider == "anthropic"
        assert client.api_key == "test_key"
        assert client.model == LLMClient.DEFAULT_ANTHROPIC_MODEL

    def test_llm_client_initialization_openai(self):
        """Test LLM client initialization with OpenAI."""
        client = LLMClient(provider="openai", api_key="test_key")
        assert client.provider == "openai"
        assert client.api_key == "test_key"
        assert client.model == LLMClient.DEFAULT_OPENAI_MODEL

    @patch('anthropic.Anthropic')
    def test_generate_text_anthropic(self, mock_anthropic_class):
        """Test text generation with Anthropic."""
        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Generated text")]
        mock_client.messages.create.return_value = mock_message
        mock_anthropic_class.return_value = mock_client

        client = LLMClient(provider="anthropic", api_key="test_key")
        result = client.generate_text("test prompt")

        assert result == "Generated text"
        mock_client.messages.create.assert_called_once()

    @patch('openai.OpenAI')
    def test_generate_text_openai(self, mock_openai_class):
        """Test text generation with OpenAI."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Generated text"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        client = LLMClient(provider="openai", api_key="test_key")
        result = client.generate_text("test prompt")

        assert result == "Generated text"
        mock_client.chat.completions.create.assert_called_once()

    def test_llm_client_custom_model(self):
        """Test LLM client with custom model."""
        client = LLMClient(
            provider="anthropic",
            api_key="test_key",
            model="claude-3-opus-20240229"
        )
        assert client.model == "claude-3-opus-20240229"

    def test_llm_client_set_model(self):
        """Test setting model after initialization."""
        client = LLMClient(provider="anthropic", api_key="test_key")
        client.set_model("claude-3-opus-20240229")
        assert client.model == "claude-3-opus-20240229"

    def test_generate_text_invalid_provider(self):
        """Test error handling for invalid provider."""
        client = LLMClient(provider="invalid", api_key="test_key")
        result = client.generate_text("test prompt")

        assert result is None

    @patch('anthropic.Anthropic')
    def test_generate_text_error_handling(self, mock_anthropic_class):
        """Test error handling in text generation."""
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("API Error")
        mock_anthropic_class.return_value = mock_client

        client = LLMClient(provider="anthropic", api_key="test_key")
        result = client.generate_text("test prompt")

        assert result is None

