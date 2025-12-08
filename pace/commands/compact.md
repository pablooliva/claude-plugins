# Context Compaction

CONTEXT COMPACTION - PHASE AGNOSTIC

Context utilization is high. Preserve critical work and prepare for session continuation.

## Auto-Detection

First, analyze the current conversation to determine:

1. **Work Type** - What kind of task is in progress?
   - Research (investigating, gathering information, exploring sources)
   - Planning (creating plans, breaking down tasks, strategizing)
   - Execution (producing deliverables, writing documents, completing tasks)
   - General (mixed or undefined work)

2. **Key Artifacts** - What has been created or referenced?
   - Documents written or in progress
   - Research findings collected
   - Plans or strategies developed
   - Deliverables produced
   - External sources consulted

3. **Current State** - Where are we in the work?
   - Active task or question being addressed
   - Blocking issues or open questions
   - Progress made this session

## Process

### 1. Create Timestamped Compaction File

Write to: `PACE/prompts/context-management/compacted-[YYYY-MM-DD_HH-MM-SS].md`

Example: `compacted-2025-10-01_14-30-45.md`

### 2. Document Structure

Use the following template, adapting sections based on detected work type:

```markdown
# Context Compaction - [Topic/Task] - [Date/Time]

## Session Summary

- **Work Type**: [Research / Planning / Execution / General]
- **Topic/Task**: [What we were working on]
- **Context Trigger**: [Estimated context % utilization]
- **Session Duration**: [Approximate time/interactions]

## Work Completed This Session

[List what was accomplished - be specific but concise]
- [Accomplishment 1]
- [Accomplishment 2]
- [Accomplishment 3]

## Key Findings & Insights

[Critical information discovered that must be preserved]
- [Finding 1]
- [Finding 2]
- [Finding 3]

## Artifacts Created or Modified

[Documents, files, or outputs from this session]
- [Artifact 1]: [Brief description and location]
- [Artifact 2]: [Brief description and location]

## Current State

### In Progress
- [What was actively being worked on when compaction triggered]

### Open Questions
- [Unresolved questions that need answers]
- [Decisions pending]

### Blockers (if any)
- [Issues preventing progress]

## External Sources Consulted

[Web searches, documents, references used]
- [Source 1]: [What was learned]
- [Source 2]: [What was learned]

## Next Session Priorities

**Immediate Focus:**
- [Exact task to resume]

**Essential Context to Reload:**
- [Specific files, documents, or artifacts needed]
- [Key reference material]

**Remaining Work:**
1. [Next priority task]
2. [Following task]
3. [Subsequent task]

## Notes for Continuation

[Any additional context, approaches to try, or important information]
```

### 3. Update Progress Tracker

Update `PACE/prompts/context-management/progress.md` with:

- Current work state
- Reference to this compaction file
- Next session starting point

## Guidelines

- **Be thorough but concise** - capture what matters without bloat
- **Use file references** - prefer paths over copying content
- **Preserve insights** - document learnings that took effort to acquire
- **Mark clear status** - distinguish done vs. in-progress vs. planned
- **Focus on continuation** - optimize for resuming work efficiently

## After Compaction

1. **Clear the session** - Close Claude Code or start new conversation
2. **Start fresh** - Open new Claude Code session
3. **Run `/continue`** - Resume from where you left off

The continue command will reload progress from `progress.md` and the compaction file.

## Context Target

Maintain <40% context utilization for optimal performance. Compact proactively when approaching this threshold rather than waiting for degraded responses.
