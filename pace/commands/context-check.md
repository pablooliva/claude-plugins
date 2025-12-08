# Context Utilization Check

CONTEXT UTILIZATION ANALYSIS

Analyze current context utilization and provide compaction recommendations.

## Context Analysis

1. Estimate current context utilization percentage (target: <40%)
2. Identify what's consuming the most context:
   - File contents loaded
   - Conversation history length
   - Tool outputs and search results
   - Documents and deliverables in progress

## Compaction Decision

1. Recommend if we should compact now based on:
   - Context utilization level
   - Logical stopping point reached
   - Work completion status

2. If compaction recommended, identify current work type:
   - Research (investigating, gathering information)
   - Planning (creating plans, task breakdown)
   - Execution (producing deliverables)
   - General (mixed work)

## Preservation Priority

1. List the most critical information that must be preserved:
   - Key findings and insights
   - Important decisions made
   - Current work state
   - Files and references that matter

## Recommendation

Provide clear recommendation:

- **CONTINUE WORKING** (if <40% context utilization)
- **COMPACT NOW** (if >40% utilization) - run `/compact` to preserve work and prepare for session continuation

Include specific next action based on current work and context state.
