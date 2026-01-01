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

4. ⏳ **Step 4: Configuration System**
   - Setup configuration loading
   - Environment variable management

5. ⏳ **Step 5: Core Utilities (TDD)**
   - API client utilities
   - Image processing utilities
   - Logging system

6. ⏳ **Step 6: Agent Implementation (TDD)**
   - Theme Discovery Agent
   - Theme Selection Agent
   - Wallpaper Generation Agent
   - Wallpaper Application Agent

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

