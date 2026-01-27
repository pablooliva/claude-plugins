# Generic Session Compaction

GENERIC SESSION COMPACTION

Context is getting high during work. Create a lightweight compaction record to preserve your progress while freeing up context. Use this for smaller tasks, follow-up work, or when phase-specific compaction is overkill.

## When to Use This vs Phase-Specific Compaction

| Use `/compact` when: | Use phase-specific when: |
|---------------------|-------------------------|
| Working on smaller tasks | Deep in a full phase workflow |
| Follow-up work after phase completion | Need detailed phase artifacts |
| Ad-hoc investigations | Want full phase template |
| Quick context reset needed | Starting fresh development cycle |

## Process

### 1. Create Timestamped Compaction File

Write to: `SDD/prompts/context-management/compact-[YYYY-MM-DD_HH-MM-SS].md`

Format: `compact-YYYY-MM-DD_HH-MM-SS.md` (24-hour time)
Example: `compact-2025-10-01_14-30-45.md`

### 2. Document Structure

Use the following streamlined template:

```markdown
# Session Compaction - [Brief Task Description] - [Date/Time]

## Session Context

- Context trigger: [context %] utilization
- Working on: [brief description of current task]
- Current phase: [research/planning/implementation/follow-up/ad-hoc]

## Work Summary

### Completed This Session
- [Task/investigation completed]
- [Files modified: path:lines]
- [Decisions made]

### In Progress
- [Current task and its status]
- [What was being worked on when compacting]

### Remaining
- [Tasks still to do]

## Key Discoveries

[Important findings that must be preserved - keep concise]
- [Discovery 1]
- [Discovery 2]

## Critical References

[Files needed to resume - use file:line format]
- [Primary file being worked on]
- [Related reference files]

## Next Session

**Resume From:**
- [Exact point to continue from]

**Immediate Priorities:**
1. [First thing to do]
2. [Second thing to do]

**Open Questions:**
- [Any unresolved questions]

## Notes

[Any other important context for continuation]
```

### 3. Update Progress File

**Before updating `SDD/prompts/context-management/progress.md`, check its contents:**

1. **Read existing progress.md** (if it exists)
2. **Determine relevance:**
   - Does it describe the same task/feature you're currently working on?
   - Is it from a different, unrelated task?

**If progress.md contains unrelated work:**

**STOP and ask the user first.** Present options:

1. **Archive** - Rename existing to `progress-archived-[YYYY-MM-DD_HH-MM-SS].md`, then create fresh progress.md
2. **Overwrite** - Replace existing progress.md with current task info
3. **Append** - Add current task as a new section in existing progress.md
4. **Skip** - Don't update progress.md, only create the compaction file

Wait for user response before proceeding.

**If progress.md is relevant to current work (or doesn't exist):**

Update/create with:

- Current work state
- Reference to this compaction file
- Next session continuation point

```markdown
## Current State

- Last compaction: compact-[timestamp].md
- Working on: [task description]
- Next step: [what to do next]
```

## Guidelines

- **Keep it brief** - this is meant to be lighter than phase-specific compaction
- **Focus on resumability** - capture just enough to pick up where you left off
- **Use file:line references** - avoid pasting large code blocks
- **Be specific about next steps** - make it easy to resume quickly

## Next Steps After Compaction

1. **Clear the session** - Close Claude Code or start new conversation
2. **Start fresh** - Open new Claude Code session
3. **Run `/continue`** - Resume from where you left off

The continue command will find this compaction file and reload your context.

## Quick Compaction Checklist

Before finishing, verify:

- [ ] Work summary captures what was done
- [ ] Critical references have file:line pointers
- [ ] "Resume From" section is specific and actionable
- [ ] Progress file is updated
