# Initialize Research Phase

RESEARCH PHASE INITIALIZATION

Starting research phase for a new topic or task.

IMPORTANT: This command requires Claude Opus. Before proceeding, check your current model ID in the system information. If you are NOT running on a Claude Opus model (e.g., claude-opus-*), immediately:

  1. Warn the user: "WARNING: This command requires Claude Opus but you're currently using [model name]. Please switch to Opus and try again."
  2. STOP all further processing - do not execute any of the instructions below.

IMPORTANT: Before starting this phase, check if `PACE/prompts/context-management/progress.md` contains any important information. If it does, ask the user if they want to archive it before resetting. Then reset the file to only contain a heading: `# Research Progress`. We are starting on a new task and want to ensure that the progress file is clean.

Set up systematic investigation:

## Research Setup

1. Create `PACE/research/RESEARCH-[###]-[topic-name].md` document where:
   - `[###]` is sequential numbering (001, 002, etc.) for organizing multiple research projects
   - `[topic-name]` is a kebab-case description (e.g., "knowledge-management", "productivity-tools", "decision-framework")

Use this structure for the research document:

```markdown
# RESEARCH-[###]-[topic-name]

## Executive Summary

- Core question/problem: [What we're trying to understand/solve]
- Research scope: [Boundaries and focus areas]
- Key findings preview: [Top insights - fill after research]

## Information Sources

### Online Research
- Primary sources: [Authoritative websites, papers, documentation]
- Secondary sources: [Articles, forums, discussions]
- Multimedia resources: [Videos, podcasts, courses]

### Existing Documentation
- Internal documents: [Relevant files in the project]
- External references: [Books, guides, manuals]
- Previous research: [Related past investigations]

## Key Concepts & Definitions

- Core concepts: [Main ideas and their definitions]
- Terminology: [Important terms to understand]
- Frameworks: [Relevant models or methodologies]

## Analysis & Findings

### Main Insights
- Finding 1: [Description and implications]
- Finding 2: [Description and implications]
- Finding 3: [Description and implications]

### Patterns & Connections
- Common themes: [Recurring patterns across sources]
- Relationships: [How different concepts connect]
- Contradictions: [Conflicting information and resolution]

## Practical Applications

- Immediate use cases: [How this applies now]
- Future opportunities: [Potential future applications]
- Implementation considerations: [What to keep in mind]

## Open Questions

- Unresolved issues: [Questions needing more research]
- Areas for deeper investigation: [Topics requiring more depth]
- External dependencies: [Things outside our control]

## Resources & References

### Primary Resources
- [Resource 1]: [URL/location] - [Why it's valuable]
- [Resource 2]: [URL/location] - [Why it's valuable]

### Tools & Scripts
- Potential tools: [Software or services that could help]
- Script opportunities: [Where automation might help]

### Further Reading
- [Title]: [Link/location] - [Brief description]
```

## Research Process

Begin systematic investigation:

- Start with broad exploration to understand the landscape
- Identify authoritative sources and primary references
- Analyze existing project files for relevant information
- Synthesize findings into actionable insights
- Document both what you learn AND what questions remain

## Context Management

1. Maintain <40% context utilization throughout research
2. Use the Task tool with appropriate subagents for deep exploration
3. Focus on understanding before moving to planning
4. Use WebSearch and WebFetch for online research
5. Read relevant project files for context

## Deliverable Target

Complete research document that:
- Provides comprehensive understanding of the topic
- Identifies key resources and references
- Highlights practical applications
- Sets foundation for planning phase

Begin research now - create the `PACE/research/RESEARCH-[###]-[topic-name].md` document and start systematic investigation based on the user's research topic.