# Wallpaper Agent

An agentic application that automatically generates and sets minimalistic dark-themed wallpapers on your MacBook based on weekly themes, with a preference for Indian cultural events and achievements.

## Features

- **Weekly Theme Discovery**: Automatically searches for relevant themes (Indian cultural events, ISRO achievements, global events)
- **Intelligent Theme Selection**: Prioritizes Indian culture and achievements over global themes
- **AI-Powered Wallpaper Generation**: Creates stunning, minimalistic, dark-themed wallpapers using Pollinations.ai
- **Automatic Wallpaper Application**: Sets the generated wallpaper on your macOS desktop
- **Fully Automated**: Runs weekly via cron job

## Architecture

The system uses a multi-agent architecture:

1. **Theme Discovery Agent**: Searches the internet for current themes
2. **Theme Selection Agent**: Evaluates and ranks themes based on preferences
3. **Wallpaper Generation Agent**: Generates wallpapers using AI
4. **Wallpaper Application Agent**: Sets wallpaper on macOS

## Setup

### Prerequisites

- Python 3.10 or higher
- macOS (for wallpaper setting functionality)
- API keys for LLM (Anthropic Claude or OpenAI)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd wallpaper_agent
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

5. Run tests:
```bash
pytest
```

## Usage

### Manual Execution

Run the wallpaper agent manually:
```bash
python src/main.py
```

### Automated Weekly Execution

Setup a cron job to run weekly (e.g., every Sunday at 9 AM):
```bash
crontab -e
# Add: 0 9 * * 0 cd /path/to/wallpaper_agent && /path/to/venv/bin/python src/main.py
```

## Development

This project uses:
- **Spec-Driven Development (SDD)**: Specifications in `spec/` directory
- **Test-Driven Development (TDD)**: Tests in `tests/` directory

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_theme_discovery.py
```

### Project Structure

```
wallpaper_agent/
├── spec/                    # GitHub Spec Kit documents
│   ├── specification.md
│   ├── technical-plan.md
│   └── tasks.md
├── src/                     # Source code
│   ├── agents/             # Agent implementations
│   ├── api_clients/        # API client implementations
│   ├── config/             # Configuration
│   ├── utils/              # Utility functions
│   └── main.py             # Main orchestrator
├── tests/                   # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── fixtures/           # Test fixtures
├── wallpapers/             # Generated wallpapers
├── logs/                   # Application logs
├── requirements.txt
├── .env.example
└── README.md
```

## Configuration

Edit `.env` file to configure:
- API keys
- Wallpaper resolution
- Theme preferences
- Directory paths

## License

MIT License

## Contributing

This is a personal project, but suggestions and improvements are welcome!

