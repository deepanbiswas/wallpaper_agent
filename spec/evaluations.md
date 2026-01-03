# Agent Evaluation Framework

## Overview

This document defines evaluation metrics and quality criteria for each agent to ensure output quality is maintained or improved over time.

## Evaluation Strategy

### Evaluation Types

1. **Unit Evaluations**: Test individual agent outputs in isolation
2. **Integration Evaluations**: Test agent outputs in workflow context
3. **Quality Metrics**: Measure output quality against defined criteria
4. **Regression Detection**: Compare current outputs to historical baselines

### Evaluation Frequency

- **Development**: Run evals after each agent modification
- **CI/CD**: Run evals in continuous integration pipeline
- **Production**: Run evals weekly/monthly to track quality trends

## Agent-Specific Evaluations

### 1. Theme Discovery Agent

#### Metrics

1. **Theme Relevance Score** (0-100)
   - **Measures**: How relevant are discovered themes to current time period?
   - **Method**: LLM-based evaluation comparing themes to current date/events, or rule-based using metadata relevance scores
   - **Target**: > 80
   - **Critical Threshold**: < 60 (fail)

2. **Theme Quality Score** (0-100)
   - **Measures**: Cleanliness of theme names, descriptions, completeness
   - **Method**: 
     - Name clarity (no noise, proper capitalization, reasonable length)
     - Description completeness (has meaningful description, not too long)
     - Metadata presence (if LLM-enhanced: relevance, significance, visual_appeal)
   - **Target**: > 85
   - **Warning Threshold**: < 75

3. **Deduplication Accuracy** (0-100)
   - **Measures**: How well duplicates are identified and merged
   - **Method**: Check uniqueness ratio (unique names / total names)
   - **Target**: > 90
   - **Critical Threshold**: < 80 (fail)

4. **Coverage Score** (0-100)
   - **Measures**: Does discovery find themes across all categories?
   - **Method**: Check presence of Indian cultural, Indian achievement, global themes
   - **Target**: > 70 (at least 2 categories represented)
   - **Warning Threshold**: < 70

5. **LLM Enhancement Impact** (if enabled)
   - **Measures**: Improvement when LLM is used vs. simple extraction
   - **Method**: Compare quality scores with/without LLM
   - **Target**: +10 points improvement

#### Baseline Metrics

- **Without LLM**: Relevance ~60, Quality ~65
- **With LLM**: Relevance ~85, Quality ~90

---

### 2. Theme Selection Agent

#### Metrics

1. **Selection Accuracy** (0-100)
   - **Measures**: Is the selected theme the best choice?
   - **Method**: LLM-based evaluation comparing selected vs. all themes, or rule-based check
   - **Target**: > 85
   - **Critical Threshold**: < 70 (fail)

2. **Preference Adherence** (0-100)
   - **Measures**: Does selection respect user preferences (Indian > Global)?
   - **Method**: Check if Indian themes are selected over global when both present
   - **Target**: > 90
   - **Warning Threshold**: < 85

3. **Style Guidelines Quality** (0-100)
   - **Measures**: Quality of generated style guidelines
   - **Method**: Check completeness (prompt, colors, elements, description) and coherence
   - **Target**: > 85
   - **Warning Threshold**: < 75

4. **Ranking Consistency** (0-100)
   - **Measures**: Are rankings consistent across runs with same input?
   - **Method**: Run same themes multiple times, check ranking stability
   - **Target**: > 80
   - **Note**: Not yet implemented

5. **LLM Ranking Impact** (if enabled)
   - **Measures**: Improvement when LLM ranking is used
   - **Method**: Compare selection accuracy with/without LLM ranking
   - **Target**: +15 points improvement

#### Baseline Metrics

- **Selection Accuracy**: ~75 (without LLM), ~90 (with LLM)
- **Preference Adherence**: ~85
- **Style Guidelines Quality**: ~80 (without LLM), ~90 (with LLM)

---

### 3. Wallpaper Generation Agent

#### Metrics

1. **Image Quality Score** (0-100)
   - **Measures**: Visual quality of generated wallpaper
   - **Method**: 
     - Technical: Resolution, format, file size
     - Image validity check
   - **Target**: > 80
   - **Critical Threshold**: < 60 (fail)

2. **Theme Adherence** (0-100)
   - **Measures**: Does wallpaper match the theme?
   - **Method**: LLM-based evaluation comparing image description to theme (future enhancement)
   - **Target**: > 85
   - **Current**: Default score 80.0 (placeholder)

3. **Style Adherence** (0-100)
   - **Measures**: Does wallpaper match style guidelines?
   - **Method**: Check color palette, elements, minimalism (future enhancement)
   - **Target**: > 80
   - **Current**: Not yet implemented

4. **Dark Theme Compliance** (0-100)
   - **Measures**: Is wallpaper actually dark-themed?
   - **Method**: Image analysis (average brightness, dark pixel ratio)
   - **Target**: > 90
   - **Warning Threshold**: < 80

5. **Minimalism Score** (0-100)
   - **Measures**: Is wallpaper minimalistic?
   - **Method**: Visual complexity analysis (future enhancement)
   - **Target**: > 75
   - **Current**: Not yet implemented

#### Baseline Metrics

- **Image Quality**: ~75
- **Theme Adherence**: ~80
- **Dark Theme Compliance**: ~85

---

### 4. Wallpaper Application Agent

#### Metrics

1. **Application Success Rate** (0-100)
   - **Measures**: Percentage of successful wallpaper applications
   - **Method**: Track success/failure over time
   - **Target**: > 95
   - **Critical Threshold**: < 90 (fail)

2. **Desktop Detection Accuracy** (0-100)
   - **Measures**: Correct desktop count detection
   - **Method**: Compare detected vs. actual desktop count
   - **Target**: > 95
   - **Current**: Not yet implemented (requires manual verification)

3. **Desktop Selection Correctness** (0-100)
   - **Measures**: Correct desktop selection (2nd if 2 exist, 1st if 1)
   - **Method**: Verify selected desktop matches rules
   - **Target**: > 98
   - **Current**: Basic check implemented

#### Baseline Metrics

- **Application Success Rate**: ~98
- **Desktop Detection**: ~95

---

## Evaluation Framework Implementation

### Evaluation Runner

The `AgentEvaluator` class provides methods to evaluate each agent:

```python
from src.evaluations import AgentEvaluator

evaluator = AgentEvaluator()

# Evaluate discovery agent
discovery_result = evaluator.evaluate_discovery_agent(themes, week_context)

# Evaluate selection agent
selection_result = evaluator.evaluate_selection_agent(selected_theme, all_themes)

# Evaluate generation agent
generation_result = evaluator.evaluate_generation_agent(wallpaper_path, theme)

# Evaluate application agent
application_result = evaluator.evaluate_application_agent(success, desktop_index, desktop_count)
```

### Evaluation Storage

- Store evaluation results in JSON/CSV format
- Track trends over time
- Alert on quality degradation
- Compare against baselines

### Quality Thresholds

#### Critical Thresholds (Fail if below)
- Theme Discovery Relevance: < 60
- Theme Discovery Deduplication: < 80
- Theme Selection Accuracy: < 70
- Wallpaper Generation Quality: < 60
- Application Success Rate: < 90

#### Warning Thresholds (Alert if below)
- Theme Discovery Quality: < 75
- Theme Discovery Coverage: < 70
- Theme Selection Preference Adherence: < 85
- Wallpaper Dark Theme Compliance: < 80

---

## Regression Detection

- Compare current metrics to historical averages
- Flag significant drops (> 10 points)
- Track improvement trends
- Generate quality reports

## Future Enhancements

1. **Automated Evaluation Pipeline**: Run evals automatically after each workflow
2. **Quality Dashboard**: Visual representation of quality trends
3. **Alert System**: Notify on quality degradation
4. **Historical Tracking**: Store evaluation history for trend analysis
5. **Image Analysis**: Enhanced theme adherence and minimalism evaluation using image processing

