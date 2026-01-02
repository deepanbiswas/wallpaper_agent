"""
Wallpaper Generation Agent.

Generates wallpapers using image generation clients and processes them for use.
"""
from pathlib import Path
from typing import Optional, Dict, Any
from api_clients import ImageGenerationClient, PollinationsClient
from utils.image_processor import process_wallpaper
from config import get_wallpaper_config, load_config
from agents.wallpaper_generation.domain import WallpaperRequest, WallpaperResult


class WallpaperGenerationAgent:
    """Agent responsible for generating wallpapers."""
    
    def __init__(
        self,
        config=None,
        image_client: Optional[ImageGenerationClient] = None,
    ):
        """
        Initialize Wallpaper Generation Agent.
        
        Args:
            config: Config instance (optional, loads from env if not provided)
            image_client: ImageGenerationClient instance (optional, defaults to PollinationsClient)
        """
        if config is None:
            config = load_config()
        
        self.config = config
        self.image_client: ImageGenerationClient = image_client or PollinationsClient()
        
        # Get wallpaper configuration
        wallpaper_config = get_wallpaper_config(config)
        self.default_width = wallpaper_config.get("width", 3024)
        self.default_height = wallpaper_config.get("height", 1964)
        wallpaper_dir = wallpaper_config.get("directory", "./wallpapers")
        # Ensure directory is a string/Path, not a Mock
        if isinstance(wallpaper_dir, (str, Path)):
            self.wallpaper_dir = Path(wallpaper_dir)
        else:
            self.wallpaper_dir = Path("./wallpapers")
    
    def generate_wallpaper(self, request: WallpaperRequest) -> WallpaperResult:
        """
        Generate wallpaper from theme request.
        
        Args:
            request: WallpaperRequest with theme and style guidelines
            
        Returns:
            WallpaperResult with success status and file path
        """
        # Validate request
        if not self._validate_request(request):
            return WallpaperResult(
                success=False,
                error="Invalid request: theme_name is required",
            )
        
        try:
            # Build prompt from style guidelines
            prompt = self._build_prompt(request.theme_name, request.style_guidelines)
            
            # Get dimensions
            width = request.width or self.default_width
            height = request.height or self.default_height
            
            # Generate image
            image_data = self.image_client.generate_image(
                prompt=prompt,
                width=width,
                height=height,
            )
            
            if not image_data:
                return WallpaperResult(
                    success=False,
                    error="Failed to generate image: empty response",
                )
            
            # Process and save wallpaper
            from PIL import Image
            import io
            
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Generate output filename
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_theme_name = "".join(c for c in request.theme_name if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
            filename = f"{safe_theme_name}_{timestamp}.png"
            output_path = self.wallpaper_dir / filename
            
            # Process and save wallpaper
            output_path = process_wallpaper(
                image=image,
                output_path=output_path,
                target_width=width,
                target_height=height,
                enforce_dark_theme=True,
            )
            
            return WallpaperResult(
                success=True,
                file_path=output_path,
                metadata={
                    "theme_name": request.theme_name,
                    "width": width,
                    "height": height,
                    "prompt": prompt,
                },
            )
            
        except Exception as e:
            return WallpaperResult(
                success=False,
                error=f"Wallpaper generation failed: {str(e)}",
            )
    
    def _build_prompt(
        self,
        theme_name: str,
        style_guidelines: Dict[str, Any]
    ) -> str:
        """
        Build image generation prompt from theme and style guidelines.
        
        Args:
            theme_name: Name of the theme
            style_guidelines: Style guidelines dictionary
            
        Returns:
            Complete prompt string for image generation
        """
        # Start with prompt from style guidelines if available
        base_prompt = style_guidelines.get("prompt", "")
        
        # If no prompt in guidelines, build one with theme name
        if not base_prompt:
            base_prompt = f"Minimalistic dark-themed wallpaper featuring {theme_name}"
        else:
            # If prompt exists, ensure theme name is included
            if theme_name.lower() not in base_prompt.lower():
                base_prompt = f"{base_prompt} featuring {theme_name}"
        
        # Enhance with style elements
        enhancements = []
        
        # Add color palette if available
        color_palette = style_guidelines.get("color_palette", [])
        if color_palette:
            colors = ", ".join(color_palette[:3])  # Limit to 3 colors
            enhancements.append(f"color palette: {colors}")
        
        # Add key elements if available
        key_elements = style_guidelines.get("key_elements", [])
        if key_elements:
            elements = ", ".join(key_elements[:3])  # Limit to 3 elements
            enhancements.append(f"featuring {elements}")
        
        # Add style description if available
        style_desc = style_guidelines.get("style_description", "")
        if style_desc:
            enhancements.append(style_desc)
        
        # Build final prompt
        prompt_parts = [base_prompt]
        
        # Add enhancements
        if enhancements:
            prompt_parts.append(", ".join(enhancements))
        
        # Always ensure dark theme and minimalistic style
        prompt_parts.append("dark background, minimalistic design, elegant, high quality")
        
        return ", ".join(prompt_parts)
    
    def _validate_request(self, request: WallpaperRequest) -> bool:
        """
        Validate wallpaper request.
        
        Args:
            request: WallpaperRequest to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not request.theme_name or not request.theme_name.strip():
            return False
        
        if not request.style_guidelines:
            return False
        
        return True

