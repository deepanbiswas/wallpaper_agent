# Project Specification

## Overview

Wallpaper Agent is an agentic application that automatically generates and sets minimalistic dark-themed wallpapers on macOS based on weekly themes, with a preference for Indian cultural events and achievements.

## Goals

### Primary Goal
Create a fully automated system that generates culturally relevant, visually appealing, minimalistic dark-themed wallpapers and sets them on the user's MacBook Pro (14-inch M5) on a weekly basis.

### Secondary Goals
- Prioritize Indian cultural themes and achievements
- Use free tools and APIs where possible
- Maintain high code quality through TDD and SDD practices
- Ensure reliability and error handling

## Requirements

### Functional Requirements

1. **Weekly Theme Discovery**
   - System must search the internet weekly for current themes
   - Must identify Indian cultural events (Diwali, Durga Pujo, etc.)
   - Must identify Indian achievements (ISRO launches, etc.)
   - Must identify globally popular themes (New Year, Christmas, etc.)

2. **Theme Selection**
   - Must prioritize Indian cultural themes over global themes
   - Must prioritize Indian achievements
   - Must only consider global themes if they are highly popular
   - Must generate detailed theme descriptions for wallpaper generation

3. **Wallpaper Generation**
   - Must generate minimalistic wallpapers
   - Must use dark theme
   - Must be visually appealing
   - Must match MacBook Pro 14-inch resolution (3024x1964)
   - Must use free image generation service (Pollinations.ai)

4. **Wallpaper Application**
   - Must set generated wallpaper on macOS desktop
   - Must verify successful application
   - Must log all operations

5. **Automation**
   - Must run automatically on a weekly schedule (configurable)
   - Must handle errors gracefully
   - Must log all activities

### Non-Functional Requirements

1. **Performance**
   - Wallpaper generation should complete within reasonable time (< 5 minutes)
   - System should not block user's system

2. **Reliability**
   - System should handle API failures gracefully
   - Should have fallback mechanisms
   - Should log errors for debugging

3. **Maintainability**
   - Code should follow TDD principles
   - Should be well-documented
   - Should follow Python best practices

4. **Cost**
   - Should use free tools where possible
   - API costs should be minimal

## User Preferences

- **Theme Priority**: Indian culture > Indian achievements > Global themes (only if highly popular)
- **Wallpaper Style**: Minimalistic, dark theme, visually appealing
- **Resolution**: 3024x1964 (14-inch MacBook Pro M5)
- **Frequency**: Weekly (configurable)

## Success Criteria

1. System successfully generates and sets wallpaper weekly
2. Generated wallpapers are culturally relevant and visually appealing
3. System handles errors gracefully without user intervention
4. All operations are logged for debugging
5. Code quality maintained through TDD practices

## Out of Scope

- Multiple wallpaper options per week
- User interface for manual selection
- Wallpaper history management (beyond logging)
- Cross-platform support (macOS only)

## Constraints

- Must use free tools where possible
- Must work on macOS (14-inch MacBook Pro M5)
- Must use Python 3.10+
- Must follow TDD + SDD development practices

