"""
Interfaces/abstract base classes for API clients.

Defines contracts that concrete implementations must follow,
allowing easy swapping of implementations.
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


class ImageGenerationClient(ABC):
    """Abstract base class for image generation clients."""
    
    @abstractmethod
    def generate_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        **kwargs
    ) -> Optional[bytes]:
        """
        Generate an image based on a text prompt.
        
        Args:
            prompt: Text prompt for image generation
            width: Image width in pixels
            height: Image height in pixels
            **kwargs: Additional parameters specific to implementation
            
        Returns:
            Image data as bytes, or None on error
        """
        pass


class SearchClient(ABC):
    """Abstract base class for search clients."""
    
    @abstractmethod
    def search_themes(
        self,
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for themes/topics based on a query.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of search result dictionaries with 'title' and 'body' keys
        """
        pass

