#!/usr/bin/env python3
"""Helper script to create .env.example file."""

env_content = """# LLM API Keys (choose one or both)
# Anthropic Claude API
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# OpenAI API (alternative)
OPENAI_API_KEY=your_openai_api_key_here

# LLM Provider Preference (anthropic or openai)
LLM_PROVIDER=anthropic

# Web Search API (optional - DuckDuckGo doesn't need a key)
# SERPAPI_KEY=your_serpapi_key_here  # Only if using SerpAPI instead of DuckDuckGo

# Pollinations.ai doesn't require an API key

# Wallpaper Settings
WALLPAPER_DIR=./wallpapers
LOG_DIR=./logs

# MacBook Resolution (default: 16-inch MacBook Pro)
WALLPAPER_WIDTH=3456
WALLPAPER_HEIGHT=2234

# Theme Preferences
PREFER_INDIAN_CULTURE=true
PREFER_INDIAN_ACHIEVEMENTS=true
"""

if __name__ == "__main__":
    with open(".env.example", "w") as f:
        f.write(env_content)
    print("Created .env.example file")

