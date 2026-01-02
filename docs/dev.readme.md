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

6. 🔄 **Step 6: Agent Implementation (TDD)** (In Progress)
   - ✅ Theme Discovery Agent (Completed)
     - Searches for Indian cultural events, achievements, and global themes
     - Uses DuckDuckGo search API
     - Formats and deduplicates themes
     - 11 tests passing, 96% coverage
   - ✅ Theme Selection Agent (Completed)
     - Multi-stage ranking using Strategy + Chain of Responsibility patterns
     - Initial rule-based scoring (respects user preferences)
     - LLM-based intelligent ranking (optional)
     - Score normalization and combination
     - Generates detailed style guidelines for wallpaper generation
     - Fully swappable ranking strategies and stages
     - 32 unit tests + 7 integration tests passing
     - 91-98% coverage per component
   - ⏳ Wallpaper Generation Agent
   - ⏳ Wallpaper Application Agent

7. ⏳ **Step 7: Integration & Orchestration**
   - Main orchestrator
   - Error handling
   - End-to-end testing

8. ⏳ **Step 8: Automation**
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

