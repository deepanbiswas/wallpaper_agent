"""
Pollinations.ai image generation client for Wallpaper Agent.
"""
import requests
from typing import Optional


class PollinationsClient:
    """Client for Pollinations.ai image generation API."""

    def __init__(self):
        """Initialize Pollinations client."""
        self.base_url = "https://image.pollinations.ai/prompt/"

    def generate_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        model: str = "flux",
        **kwargs
    ) -> Optional[bytes]:
        """
        Generate an image using Pollinations.ai.

        Args:
            prompt: Text prompt for image generation
            width: Image width in pixels
            height: Image height in pixels
            model: Model to use (default: flux)
            **kwargs: Additional parameters

        Returns:
            Image data as bytes, or None on error
        """
        try:
            # Construct URL
            url = self.base_url + prompt.replace(" ", "%20")
            url += f"?width={width}&height={height}&model={model}"

            # Make request
            response = requests.get(url, timeout=60)
            
            if response.status_code == 200:
                return response.content
            else:
                return None
        except requests.RequestException:
            return None
        except Exception:
            return None

