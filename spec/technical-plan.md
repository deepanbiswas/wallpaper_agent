# Technical Plan

## Architecture Overview

The system uses a **multi-agent architecture** with 4 specialized agents working sequentially:

```
Theme Discovery → Theme Selection → Wallpaper Generation → Wallpaper Application
```

## Agent Architecture

### 1. Theme Discovery Agent

**Purpose**: Search the internet for current themes, events, and cultural celebrations.

**Responsibilities**:
- Determine current date and week context
- Search for Indian cultural events
- Search for Indian achievements (ISRO, etc.)
- Search for global popular themes
- Extract and structure candidate themes

**Input**: Current date/time
**Output**: List of candidate themes with descriptions

**Tools**:
- DuckDuckGo Search API (free, no key required)
- Date/time utilities (python-dateutil)
- LLM API (for extracting themes from search results)

### 2. Theme Selection Agent

**Purpose**: Evaluate and rank themes based on user preferences.

**Responsibilities**:
- Receive candidate themes from Discovery Agent
- Apply preference rules (Indian culture priority)
- Rank themes intelligently
- Select top theme
- Generate detailed theme description for wallpaper generation

**Input**: List of candidate themes
**Output**: Selected theme with detailed description and style guidelines

**Tools**:
- LLM API (Anthropic Claude or OpenAI) for intelligent ranking
- Preference rules engine (configurable)

### 3. Wallpaper Generation Agent

**Purpose**: Generate minimalistic, dark-themed wallpapers based on selected theme.

**Responsibilities**:
- Receive theme description from Selection Agent
- Craft prompt for minimalistic dark theme
- Call Pollinations.ai API to generate image
- Post-process image (resize, dark theme validation)
- Save wallpaper to local directory

**Input**: Theme description and style guidelines
**Output**: Generated wallpaper image file (PNG/JPG)

**Tools**:
- Pollinations.ai API (free, no API key required)
- Pillow (PIL) for image processing
- Prompt engineering for style consistency

### 4. Wallpaper Application Agent

**Purpose**: Set the generated wallpaper on macOS desktop.

**Responsibilities**:
- Receive wallpaper file path
- Execute macOS command to set wallpaper
- Verify successful application
- Log results

**Input**: Wallpaper file path
**Output**: Confirmation of wallpaper application

**Tools**:
- macOS `osascript` (AppleScript) via subprocess
- File system utilities

## Technology Stack

### Core Language
- **Python 3.10+**

### APIs & Services
- **Web Search**: DuckDuckGo API (free, no key)
- **Image Generation**: Pollinations.ai API (free, no key)
- **LLM**: Anthropic Claude API or OpenAI API (free tier available)

### Libraries
- `requests` - HTTP API calls
- `Pillow` (PIL) - Image processing
- `python-dateutil` - Date/time handling
- `python-dotenv` - Environment variable management
- `anthropic` - Anthropic Claude API client
- `openai` - OpenAI API client
- `duckduckgo-search` - DuckDuckGo search wrapper

### Testing
- `pytest` - Testing framework
- `pytest-mock` - Mocking utilities
- `pytest-cov` - Coverage reporting

### Development Tools
- `black` - Code formatting
- `flake8` - Linting
- `mypy` - Type checking

## Data Flow

```
1. Weekly Trigger (cron)
   ↓
2. Theme Discovery Agent
   - Searches internet
   - Extracts themes
   ↓
3. Theme Selection Agent
   - Ranks themes
   - Selects best theme
   ↓
4. Wallpaper Generation Agent
   - Generates image
   - Post-processes
   ↓
5. Wallpaper Application Agent
   - Sets wallpaper
   - Verifies success
   ↓
6. Logging & Notification
```

## Configuration

### Environment Variables
- `ANTHROPIC_API_KEY` - Anthropic Claude API key
- `OPENAI_API_KEY` - OpenAI API key (alternative)
- `LLM_PROVIDER` - Preferred LLM provider (anthropic/openai)
- `WALLPAPER_DIR` - Directory for storing wallpapers
- `LOG_DIR` - Directory for logs
- `WALLPAPER_WIDTH` - Wallpaper width (3024)
- `WALLPAPER_HEIGHT` - Wallpaper height (1964)
- `PREFER_INDIAN_CULTURE` - Boolean preference flag
- `PREFER_INDIAN_ACHIEVEMENTS` - Boolean preference flag

### File Structure
```
wallpaper_agent/
├── spec/              # Specifications
├── src/
│   ├── agents/        # Agent implementations
│   ├── config/        # Configuration management
│   ├── utils/         # Utility functions
│   └── main.py        # Orchestrator
├── tests/             # Test suite
├── wallpapers/        # Generated wallpapers
├── logs/              # Application logs
└── docs/              # Documentation
```

## Error Handling Strategy

1. **API Failures**: Retry with exponential backoff
2. **Image Generation Failures**: Fallback to simpler prompt
3. **Wallpaper Application Failures**: Log error, notify user
4. **Network Failures**: Retry with backoff, log failures

## Logging Strategy

- All agent operations logged
- API calls logged (without sensitive data)
- Errors logged with stack traces
- Success/failure status logged
- Log rotation configured

## Security Considerations

- API keys stored in `.env` file (not committed)
- No sensitive data in logs
- Input validation for all external data
- Safe file operations

## Performance Considerations

- Async operations where possible
- Image processing optimized
- Caching of theme searches (optional)
- Efficient file I/O

## Deployment

- Local execution via cron job
- Virtual environment for isolation
- Environment variables for configuration
- Log rotation for disk management

