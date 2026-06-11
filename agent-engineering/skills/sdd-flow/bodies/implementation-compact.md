# Implementation Progress Compaction

You are a spawned subagent in an orchestrated /sdd-flow run. Your prompt provides resolved artifact paths and identifiers — use them verbatim. This file is your complete instruction set. You cannot spawn subagents and cannot invoke slash commands; all work happens inline in your own context.

You are reading this because your Reads-counter safety-net tripped mid-phase. Follow these compaction instructions to write `SDD/orchestration/compacted/implementation-compacted-[YYYY-MM-DD_HH-MM-SS].md`, append a `## PARTIAL: needs continuation` block to `SDD/orchestration/progress.md` with the compaction file path and where you left off, then return ≤100 words to the orchestrator stating a Mid-Phase Handoff is required.

IMPLEMENTATION PROGRESS COMPACTION

Context is getting overloaded during implementation. Create permanent compaction record to preserve your work while freeing up context.

## Process

### 1. Create Timestamped Compaction File

Write to: `SDD/orchestration/compacted/implementation-compacted-[YYYY-MM-DD_HH-MM-SS].md`

Format: `implementation-compacted-YYYY-MM-DD_HH-MM-SS.md` (24-hour time format)
Example: `implementation-compacted-2025-10-01_14-30-45.md`

### 2. Document Structure

Use the following template:

```markdown
# Implementation Compaction - [Feature Name] - [Date/Time]

## Session Context

- Compaction trigger: [context %] utilization
- Implementation focus: [specific feature/component being coded]
- Specification reference: [SPEC-XXX being implemented]
- Session duration: [approximate time/interactions]

## Recent Changes
[List specific files modified with line references where relevant - e.g., `src/auth/login.ts:45-67`]
- File 1: [brief description of changes]
- File 2: [brief description of changes]

**Avoid large code blocks** - use file:line references instead

## Implementation Progress
- **Completed**: [features/components fully implemented and tested]
- **In Progress**: [current work items and their status]
- **Planned**: [next tasks from specification]

## Tests Status
- Tests added: [list test files and what they cover]
- Tests passing: [X/Y passing]
- Coverage gaps: [areas needing tests]

## Critical Learnings
[Important discoveries made during implementation - patterns found, root causes identified, architectural insights]
- How implementation differed from spec: [key differences]
- Edge case handling: [how EDGE-XXX scenarios were implemented]
- Technical decisions: [conscious trade-offs and why]
- Performance considerations: [optimization decisions]

## Critical Review Status
[Check for critical review documents in SDD/reviews/CRITICAL-IMPL-*.md, CRITICAL-SPEC-*.md, and CRITICAL-RESEARCH-*.md]
- Review performed: [yes/no - check for CRITICAL-IMPL-*.md]
- Review document: [path to CRITICAL-IMPL-*.md if exists]
- Prior phase reviews: [paths to CRITICAL-SPEC-*.md and CRITICAL-RESEARCH-*.md if they exist]
- Unresolved findings: [list any HIGH/MEDIUM findings not yet addressed]
- Actions taken: [findings already addressed during this session]
- Pending actions: [findings that still need attention in next session]
- Code changes driven by review: [implementations modified due to critical review]

## Critical References
[2-3 most important documents/files needed to understand this work]
- Specification: [path to spec document]
- Related architecture: [path if applicable]
- Key implementation file: [path to core file]
- Critical review (if exists): SDD/reviews/CRITICAL-IMPL-[feature-name]-YYYYMMDD.md

## Next Session Priorities

**Essential Files to Reload:**
- [Specific paths and line ranges needed to resume work]

**Current Focus:**
- Exact problem being solved: [specific bug/feature]
- Blocking issue: [if any]

**Implementation Priorities:**
1. [Specific next code to write]
2. [Following task]
3. [Subsequent task]

**Specification Validation Remaining:**
- [ ] [Success criterion not yet met]
- [ ] [Edge case not yet implemented]
- [ ] [Performance requirement not yet validated]

## Other Notes
[Any additional context, gotchas, or important information for continuation]
```

### 3. Update Current Progress

Also update `SDD/orchestration/progress.md` with:

- Latest implementation state
- Working functionality status
- Next development priorities
- Reference to this compaction file

---

## Guidelines

- **Be thorough but concise** - capture key details without overwhelming context
- **Avoid excessive code snippets** - prefer file:line references over large diffs
- **Include precise references** - enable quick reload of necessary context
- **Document learnings** - preserve insights for future sessions
- **Mark clear status** - distinguish completed vs. in-progress vs. planned work

This preserves complete implementation journey while enabling fresh context continuation.

## Commit Your Code Changes

Before writing the handoff message, commit any code changes you have made inline using git. Stage and commit all modified files with a descriptive commit message following project conventions. This ensures your implementation work is safely saved in version control.

## Handoff

After writing the compaction file, committing changes, and updating `SDD/orchestration/progress.md`, append a `## PARTIAL: needs continuation` block to `SDD/orchestration/progress.md` recording the compaction file path and where you left off. Then return ≤100 words to the orchestrator stating a Mid-Phase Handoff is required.

Implementation phase continues — use the implementation-complete body when the feature is finished.
