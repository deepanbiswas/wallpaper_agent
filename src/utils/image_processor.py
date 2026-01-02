"""
Image processing utilities for Wallpaper Agent.

Handles image resizing, dark theme enforcement, and wallpaper saving.
"""
from pathlib import Path
from typing import Optional
from PIL import Image, ImageEnhance, ImageFilter


def resize_image(
    image: Image.Image,
    width: int,
    height: int,
    maintain_aspect: bool = False
) -> Image.Image:
    """
    Resize an image to specified dimensions.

    Args:
        image: PIL Image to resize
        width: Target width in pixels
        height: Target height in pixels
        maintain_aspect: If True, maintain aspect ratio and crop if needed

    Returns:
        Resized PIL Image
    """
    if maintain_aspect:
        # Calculate aspect ratios
        original_aspect = image.width / image.height
        target_aspect = width / height

        if original_aspect > target_aspect:
            # Image is wider - fit to height
            new_width = int(height * original_aspect)
            resized = image.resize((new_width, height), Image.Resampling.LANCZOS)
            # Crop to target width
            left = (new_width - width) // 2
            resized = resized.crop((left, 0, left + width, height))
        else:
            # Image is taller - fit to width
            new_height = int(width / original_aspect)
            resized = image.resize((width, new_height), Image.Resampling.LANCZOS)
            # Crop to target height
            top = (new_height - height) // 2
            resized = resized.crop((0, top, width, top + height))
    else:
        resized = image.resize((width, height), Image.Resampling.LANCZOS)

    return resized


def ensure_dark_theme(image: Image.Image, threshold: float = 0.5) -> Image.Image:
    """
    Ensure image has a dark theme by adjusting brightness if needed.

    Args:
        image: PIL Image to process
        threshold: Brightness threshold (0-1), below which image is considered dark

    Returns:
        Processed PIL Image with dark theme
    """
    # Calculate average brightness
    grayscale = image.convert("L")
    pixels = list(grayscale.getdata())
    avg_brightness = sum(pixels) / len(pixels) / 255.0

    # If image is too bright, darken it
    if avg_brightness > threshold:
        # Reduce brightness
        enhancer = ImageEnhance.Brightness(image)
        # Reduce brightness to make it darker
        # Factor < 1.0 darkens the image
        darken_factor = threshold / avg_brightness
        image = enhancer.enhance(darken_factor)

    return image


def save_wallpaper(image: Image.Image, output_path: Path) -> Path:
    """
    Save wallpaper image to file.

    Args:
        image: PIL Image to save
        output_path: Path where to save the image

    Returns:
        Path to saved file
    """
    # Create directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save image
    image.save(output_path, "PNG", quality=95)
    
    return output_path


def process_wallpaper(
    image: Image.Image,
    output_path: Path,
    target_width: int,
    target_height: int,
    enforce_dark_theme: bool = True
) -> Path:
    """
    Process wallpaper through full pipeline: resize and apply dark theme.

    Args:
        image: PIL Image to process
        output_path: Path where to save processed image
        target_width: Target width in pixels
        target_height: Target height in pixels
        enforce_dark_theme: Whether to enforce dark theme

    Returns:
        Path to saved file
    """
    # Resize image
    processed = resize_image(image, target_width, target_height)

    # Apply dark theme if requested
    if enforce_dark_theme:
        processed = ensure_dark_theme(processed)

    # Save wallpaper
    return save_wallpaper(processed, output_path)

