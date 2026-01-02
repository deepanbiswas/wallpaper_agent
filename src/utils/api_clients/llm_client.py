"""
LLM client for Wallpaper Agent.

Supports Anthropic Claude and OpenAI APIs with configurable models.
"""
from typing import Optional


class LLMClient:
    """Client for LLM APIs (Anthropic Claude or OpenAI)."""

    # Default models for each provider
    DEFAULT_ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"
    DEFAULT_OPENAI_MODEL = "gpt-4"

    def __init__(
        self,
        provider: str = "anthropic",
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        Initialize LLM client.

        Args:
            provider: LLM provider ("anthropic" or "openai")
            api_key: API key for the provider
            model: Model name to use (optional, uses default if not provided)
        """
        self.provider = provider.lower()
        self.api_key = api_key
        self.model = model or self._get_default_model()
        self._client = None
        self._initialize_client()

    def _get_default_model(self) -> str:
        """Get default model for the provider."""
        if self.provider == "anthropic":
            return self.DEFAULT_ANTHROPIC_MODEL
        elif self.provider == "openai":
            return self.DEFAULT_OPENAI_MODEL
        return ""

    def _initialize_client(self):
        """Initialize the appropriate LLM client."""
        if self.provider == "anthropic" and self.api_key:
            try:
                from anthropic import Anthropic
                self._client = Anthropic(api_key=self.api_key)
            except ImportError:
                self._client = None
        elif self.provider == "openai" and self.api_key:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                self._client = None

    def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        **kwargs
    ) -> Optional[str]:
        """
        Generate text using LLM.

        Args:
            prompt: Input prompt
            model: Model name (optional, uses instance model or default if not provided)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Returns:
            Generated text, or None on error
        """
        if not self._client:
            return None

        # Use provided model, instance model, or default
        model_to_use = model or self.model or self._get_default_model()

        try:
            if self.provider == "anthropic":
                message = self._client.messages.create(
                    model=model_to_use,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}],
                    **kwargs
                )
                return message.content[0].text

            elif self.provider == "openai":
                response = self._client.chat.completions.create(
                    model=model_to_use,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    **kwargs
                )
                return response.choices[0].message.content

        except Exception:
            return None

        return None

    def set_model(self, model: str) -> None:
        """
        Set the model to use for future requests.

        Args:
            model: Model name to use
        """
        self.model = model

