"""
API clients package for Wallpaper Agent.
"""
from api_clients.interfaces import ImageGenerationClient, SearchClient
from api_clients.duckduckgo_client import DuckDuckGoClient
from api_clients.pollinations_client import PollinationsClient
from api_clients.llm_client import LLMClient

__all__ = [
    "ImageGenerationClient",
    "SearchClient",
    "DuckDuckGoClient",
    "PollinationsClient",
    "LLMClient",
]

