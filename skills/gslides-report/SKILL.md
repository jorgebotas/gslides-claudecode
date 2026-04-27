---
name: gslides-report
description: Generate progress reports and result presentations in Google Slides from project data, figures, and metrics. Use when users want to create slide decks, add results to presentations, generate progress reports, or automate slide creation from analysis outputs.
---

# Google Slides Report Generator

Automatically generates comprehensive slide presentations from project analysis, results, and metrics using the Google Slides API.

## When to use this skill

Trigger this skill when users mention:
- "Generate slide deck"
- "Create progress report"
- "Add results to Google Slides" 
- "Make a presentation from these results"
- "Export findings to slides"
- "Create slides from analysis"
- "Report progress to stakeholders"
- Working with figures, metrics, or analysis outputs they want to present

## Prerequisites

Before using this skill, ensure:
1. Google Slides API is set up (use `gslides-setup` skill if not)
2. A presentation exists and is shared with the service account
3. The `gslides-claudecode` package is installed

## Report Generation Process

### 1. Assess project context

Examine the current project to identify:
- **Key metrics and results** (model performance, accuracy, completion rates)
- **Generated figures and charts** (.png, .jpg files in results directories)
- **Data summaries** (CSV files, statistics, comparisons)
- **Project milestones and progress indicators**

### 2. Structure the presentation

Create a logical flow appropriate for the audience:

**Executive Summary Structure:**
1. **Title slide** - Project name, date, key takeaway
2. **Overview** - Objectives and approach summary
3. **Key Results** - Top-line metrics and achievements
4. **Detailed Findings** - Breakdown by category/component
5. **Visualizations** - Charts and graphs with explanations
6. **Next Steps** - Recommendations and action items

**Technical Deep-dive Structure:**
1. **Title slide**
2. **Methodology** - Approach and techniques used  
3. **Results by Category** - Detailed metrics with context
4. **Performance Analysis** - Charts, comparisons, trends
5. **Technical Insights** - Key findings and implications
6. **Future Work** - Next experiments or improvements

### 3. Generate content systematically

For each slide type:

**Text slides** - Use for:
- Executive summaries
- Methodology descriptions
- Key takeaways and recommendations
- Include relevant metrics in speaker notes

**Bullet slides** - Use for:
- Lists of results or findings
- Comparison points
- Action items and next steps
- Technical specifications

**Image slides** - Use for:
- Performance charts and graphs
- Architecture diagrams
- Result visualizations
- Upload local figures or use public URLs

**Table slides** - Use for:
- Metric comparisons
- Performance benchmarks
- Detailed numerical results
- Use CSV files to populate data

### 4. Implementation pattern

```python
from gslides_claudecode import Deck

# Initialize deck
deck = Deck.from_service_account(
    presentation_id="your_presentation_id"
)

# Title slide
deck.append_text(
    title="Project Results Report",
    body="Analysis Period: [dates]\nKey Achievement: [top metric]",
    speaker_notes="Present the main accomplishment and set context for the report"
)

# Results summary
deck.append_bullets(
    title="Key Findings",
    bullets=[
        "Metric 1: X% improvement over baseline",
        "Metric 2: Achieved Y accuracy", 
        "Milestone: Z completed ahead of schedule"
    ],
    speaker_notes="Emphasize the business impact of these results"
)

# Visual results
deck.append_image(
    title="Performance Trends",
    image_path="results/performance_chart.png",
    speaker_notes="Chart shows consistent improvement over time with key inflection point at week 3"
)

# Detailed metrics
deck.append_table(
    title="Model Comparison",
    rows=[
        ["Model", "Accuracy", "Speed", "Memory"],
        ["Baseline", "0.85", "100ms", "2GB"],
        ["Improved", "0.92", "85ms", "1.8GB"]
    ],
    speaker_notes="New model achieves better performance across all key metrics"
)
```

### 5. Content guidelines

**Titles**: Be specific and action-oriented
- Good: "Model Accuracy Improved 15% Over Baseline"  
- Avoid: "Results" or "Performance"

**Body text**: Lead with the conclusion, then supporting details
- Start with the key insight
- Provide context for numbers
- Keep technical details in speaker notes

**Speaker notes**: Include the story behind the data
- Why this result matters
- How it connects to project goals
- What stakeholders should focus on
- Potential questions and responses

**Tables**: Present data that supports decision-making
- Include baseline comparisons where relevant
- Highlight the best-performing options
- Add units and context for all metrics

## Common use cases

### Weekly progress reports
```python
# Status update format
deck.append_text(
    title="Week [N] Progress Summary", 
    body="Completed: [major milestone]\nIn Progress: [current work]\nBlocked: [impediments]",
    speaker_notes="Emphasize forward momentum and next week's priorities"
)
```

### Experiment results
```python
# A/B test or model comparison
deck.append_bullets(
    title="Experiment [Name] Results",
    bullets=[
        "Hypothesis: [what we tested]",
        "Result: [outcome with confidence interval]", 
        "Significance: [statistical significance]",
        "Recommendation: [next action]"
    ]
)
```

### Milestone presentations
```python
# Project completion or major achievement
deck.append_image(
    title="Final Results: [Achievement]",
    image_path="results/final_metrics.png",
    speaker_notes="This represents completion of the [X] objective, enabling [business outcome]"
)
```

## Integration tips

- **Automate from analysis scripts**: Call this skill at the end of analysis workflows
- **Use with existing figures**: Point to generated charts and graphs in results directories  
- **Batch processing**: Generate multiple slide types in sequence for comprehensive reports
- **Version control**: Include presentation links in project documentation for tracking

## Error handling

If slide generation fails:
1. Check that the presentation ID is correct and accessible
2. Verify image files exist and are readable
3. Ensure CSV files for tables are properly formatted
4. Test connection with `gslides test <presentation_id>`

The skill focuses on translating analysis outputs into stakeholder-ready presentations, emphasizing clarity and actionability over technical details.