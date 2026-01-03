# Developer Onboarding Guide

This document provides a brief overview of the project setup and development workflow.

## Project Overview

Wallpaper Agent is an agentic application that automatically generates and sets minimalistic dark-themed wallpapers on macOS based on weekly themes, with preference for Indian cultural events and achievements.

## Development Workflow

This project uses **Spec-Driven Development (SDD)** combined with **Test-Driven Development (TDD)**.

### Workflow Steps

1. ✅ **Step 1: Project Structure Setup**
   - Created directory structure (spec/, src/, tests/, etc.)
   - Setup pytest configuration
   - Added requirements.txt and .gitignore
   - Initialized git repository

2. ✅ **Step 2: GitHub Spec Kit Documents** (Completed)
   - ✅ Created specification.md - Project requirements and goals
   - ✅ Created technical-plan.md - Architecture and tech stack
   - ✅ Created tasks.md - Implementation task breakdown

3. ✅ **Step 3: Python Environment Setup** (Completed)
   - ✅ Created virtual environment (wallpaper_agent_env) with Python 3.12.12
   - ✅ Installed all dependencies from requirements.txt
   - ✅ Verified installation (pytest 9.0.2, core dependencies)

4. ✅ **Step 4: Configuration System** (Completed)
   - ✅ Implemented Config class with environment variable support
   - ✅ Created configuration loading from .env files (python-dotenv)
   - ✅ Added helper functions: get_wallpaper_config(), get_llm_config(), get_theme_preferences()
   - ✅ Automatic directory creation for wallpapers and logs
   - ✅ Comprehensive test suite (10 tests, 97% coverage)
   - ✅ All tests passing following TDD approach

5. ✅ **Step 5: Core Utilities (TDD)** (Completed)
   - ✅ API Client Utilities (separate folder under `src/api_clients/`):
     - `api_clients/duckduckgo_client.py` - DuckDuckGoClient for web search (4 tests)
     - `api_clients/pollinations_client.py` - PollinationsClient for image generation (5 tests)
     - `api_clients/llm_client.py` - LLMClient for Anthropic/OpenAI (7 tests, configurable model)
   - ✅ LLM model is configurable via constructor parameter or LLM_MODEL environment variable
   - ✅ Image Processing Utilities:
     - Image resizing with aspect ratio support (2 tests)
     - Dark theme enforcement (2 tests)
     - Wallpaper saving and processing pipeline (4 tests)
   - ✅ Logging System:
     - Centralized logging setup with file rotation (6 tests)
     - Logger instances for modules
   - ✅ All 42 tests passing (42 total: 11 config + 31 utilities)
   - ✅ 91% overall code coverage (83-97% per module)
   - ✅ Refactored API clients into separate files in `api_clients/` folder
   - ✅ LLM model is configurable via constructor parameter or LLM_MODEL env variable

6. ✅ **Step 6: Agent Implementation (TDD)** (Completed)
   - ✅ Theme Discovery Agent (Completed)
     - Searches for Indian cultural events, achievements, and global themes
     - Uses DuckDuckGo search API
     - Formats and deduplicates themes
     - **LLM Enhancement**: LLM-based theme extraction and cleaning (primary use)
       - Extracts clean theme names and descriptions from raw search results
       - Relevance filtering (default: >= 50) to filter low-relevance themes
       - Metadata enrichment: adds relevance, significance, visual_appeal, visual_elements, colors
       - Fallback to simple extraction when LLM unavailable or fails
     - 18 tests passing (11 original + 7 LLM extraction), 97% coverage
   - ✅ Theme Selection Agent (Completed)
     - Multi-stage ranking using Strategy + Chain of Responsibility patterns
     - Initial rule-based scoring (respects user preferences)
     - LLM-based intelligent ranking (optional)
     - Score normalization and combination
     - Generates detailed style guidelines for wallpaper generation
     - Fully swappable ranking strategies and stages
     - 32 unit tests + 7 integration tests passing
     - 91-98% coverage per component
   - ✅ Wallpaper Generation Agent (Completed)
     - Generates wallpapers using Pollinations.ai (free image generation)
     - Builds prompts from theme and style guidelines
     - Processes images (resize, dark theme enforcement)
     - Saves wallpapers to configured directory
     - WallpaperRequest and WallpaperResult domain models
     - 12 unit tests + 4 integration tests passing
     - 93% code coverage for agent
   - ✅ Wallpaper Application Agent (Completed)
     - Applies wallpapers to macOS desktop using osascript
     - Detects virtual desktop count (Spaces)
     - Auto-selects desktop: 2nd desktop if 2 exist, 1st if only 1
     - Supports explicit desktop selection
     - Platform detection (macOS/Windows)
     - Windows implementation placeholder (not yet implemented)
     - ApplicationRequest and ApplicationResult domain models
     - **Refactored**: macOS-specific code moved to `MacOSWallpaperApplier` class
     - 14 unit tests (agent) + 9 unit tests (applier) + 4 integration tests passing
     - 94% code coverage for MacOSWallpaperApplier, 90% for agent

7. ✅ **Step 7: Integration & Orchestration** (Completed)
   - ✅ Main Orchestrator (Completed)
     - Coordinates all 4 agents in sequence
     - Handles workflow: Discovery → Selection → Generation → Application
     - Error handling at each step with appropriate status codes
     - Partial success handling (wallpaper generated but not applied)
     - Comprehensive logging throughout workflow
     - OrchestrationResult and OrchestrationStatus domain models
     - 9 unit tests passing
     - 93% code coverage for orchestrator
   - ✅ Error Handling & Retry Logic (Completed)
     - Exponential backoff retry strategy
     - Configurable max retries (default: 3) and retry delay (default: 1.0s)
     - Retry logic for all workflow steps (discovery, selection, generation, application)
     - Exception handling with detailed error messages
     - 10 unit tests for retry and error handling
     - 91% code coverage for orchestrator with retry logic
   - ✅ End-to-End Testing (Completed)
     - Complete workflow tests with mocked agents
     - Tests for success, retry, partial success, and failure scenarios
     - Exception handling verification
     - 5 e2e tests passing
     - All tests marked with `@pytest.mark.e2e`

8. ✅ **Step 8: Evaluation Framework** (Completed)
   - ✅ Evaluation Framework (Completed)
     - Created `AgentEvaluator` class with evaluation methods for each agent
     - Implemented evaluation metrics (EvaluationResult, EvaluationMetrics)
     - Metrics for Discovery: Relevance, Quality, Deduplication, Coverage
     - Metrics for Selection: Selection Accuracy, Preference Adherence, Style Quality
     - Metrics for Generation: Image Quality, Theme Adherence, Dark Theme Compliance
     - Metrics for Application: Application Success, Desktop Selection Correctness
     - LLM-based evaluations where applicable (relevance, selection accuracy)
     - Rule-based fallbacks when LLM unavailable
     - 10 unit tests for evaluation framework
     - 71% code coverage for evaluator
   - ✅ Spec Updates (Completed)
     - Created `spec/evaluations.md` with detailed evaluation metrics
     - Updated `spec/technical-plan.md` with LLM enhancements
     - Updated `spec/tasks.md` with Phase 7 tasks

9. ⏳ **Step 9: Automation**
   - Cron job setup
   - Final documentation

## Architecture

4-Agent System:
1. **Theme Discovery Agent** - Searches for current themes
2. **Theme Selection Agent** - Ranks and selects themes
3. **Wallpaper Generation Agent** - Generates wallpapers using Pollinations.ai
4. **Wallpaper Application Agent** - Sets wallpaper on macOS

## Tech Stack

- **Language**: Python 3.10+
- **Testing**: pytest, pytest-mock, pytest-cov
- **APIs**: DuckDuckGo (search), Pollinations.ai (image gen), Anthropic/OpenAI (LLM)
- **Image Processing**: Pillow
- **Scheduling**: macOS cron

## Getting Started

1. Clone the repository
2. Create virtual environment: `python3 -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and configure
6. Run tests: `pytest`

## Development Principles

- **TDD**: Write tests first, then implement
- **SDD**: Follow specifications in `spec/` directory
- **Clean Code**: Follow PEP 8, use type hints
- **Documentation**: Update this file as you progress

## Testing Strategy

This project uses a comprehensive testing strategy with multiple test levels:

### Test Levels

1. **Unit Tests** (`tests/unit/`)
   - Test individual components in isolation
   - Use mocks to isolate dependencies
   - Fast execution (< 1 second per test)
   - High code coverage target: > 90%
   - Examples: Agent logic, utility functions, domain models

2. **Integration Tests** (`tests/integration/`)
   - Test component interactions with real external services
   - May call actual APIs (DuckDuckGo, Pollinations.ai, LLM APIs)
   - Slower execution (may take seconds per test)
   - Marked with `@pytest.mark.integration`
   - Examples: Agent with real API clients, full agent workflows

3. **End-to-End (E2E) Tests** (`tests/e2e/`)
   - Test complete workflows from start to finish
   - Use mocked agents to test orchestrator logic
   - Verify full system integration
   - Marked with `@pytest.mark.e2e`
   - Examples: Complete orchestrator workflow, error scenarios

### Running Tests

```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest -m integration

# Run only e2e tests
pytest -m e2e

# Run with coverage
pytest --cov=src --cov-report=html
```

### Test Organization

- **Unit tests**: One test file per source file (e.g., `test_orchestrator.py` for `orchestrator/main.py`)
- **Integration tests**: One test file per agent or major component
- **E2E tests**: One test file per major workflow scenario

### Test Coverage Goals

- **Overall**: > 80% code coverage
- **Core components**: > 90% coverage (agents, orchestrator, utilities)
- **API clients**: > 70% coverage (external dependencies)

### Error Handling & Retry Logic

- **Retry Strategy**: Exponential backoff with configurable max retries
- **Default Settings**: 3 retries, 1.0s initial delay
- **Retryable Operations**: Theme discovery, selection, generation, application
- **Error Handling**: All exceptions caught and logged with context
- **Status Codes**: SUCCESS, FAILED, PARTIAL (for partial success scenarios)

## Evaluation Framework

### Overview
- **Location**: `src/evaluations/`
- **Purpose**: Monitor and maintain agent output quality
- **Components**:
  - `evaluator.py`: `AgentEvaluator` class with evaluation methods
  - `metrics.py`: `EvaluationResult` and `EvaluationMetrics` dataclasses

### Usage
```python
from evaluations import AgentEvaluator

evaluator = AgentEvaluator()

# Evaluate discovery agent
result = evaluator.evaluate_discovery_agent(themes, week_context)

# Evaluate selection agent
result = evaluator.evaluate_selection_agent(selected_theme, all_themes)

# Evaluate generation agent
result = evaluator.evaluate_generation_agent(wallpaper_path, theme)

# Evaluate application agent
result = evaluator.evaluate_application_agent(success, desktop_index, desktop_count)
```

### Metrics
- **Discovery Agent**: Relevance (target: >80), Quality (target: >85), Deduplication (target: >90), Coverage (target: >70)
- **Selection Agent**: Selection Accuracy (target: >85), Preference Adherence (target: >90), Style Quality (target: >85)
- **Generation Agent**: Image Quality (target: >80), Theme Adherence (target: >85), Dark Theme Compliance (target: >90)
- **Application Agent**: Application Success (target: >95), Desktop Selection Correctness (target: >98)

### Quality Thresholds
- **Critical**: Fail if below critical thresholds (e.g., Relevance < 60, Selection Accuracy < 70)
- **Warning**: Alert if below warning thresholds (e.g., Quality < 75, Dark Theme < 80)

See `spec/evaluations.md` for detailed metrics, thresholds, and evaluation methods.

