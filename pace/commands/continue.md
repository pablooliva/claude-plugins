# Continue Session

CONTINUE FROM PREVIOUS SESSION

Resume work after a session clear or compaction.

## When to Use

Run `/continue` when:
- You've run `/compact` and cleared your Claude Code session
- You're starting fresh and want to resume where you left off

## Workflow Overview

```text
[Work] ──► [Context ~40%] ──► [/compact] ──► [Clear Session] ──► [/continue]
                                   │                                  │
                                   └── Creates progress.md ──────────► Reads
                                       & compaction file               both files
```

## Process

### 1. Load Progress Files

1. **Read Main Progress File:**
   - Load `PACE/prompts/context-management/progress.md`
   - Identify current work type (research/planning/execution/general)
   - Note what was being worked on and next priorities

2. **Locate Most Recent Compaction File:**
   - Check `PACE/prompts/context-management/` for `compacted-[YYYY-MM-DD_HH-MM-SS].md`
   - Load the most recent file based on timestamp

### 2. Model Recommendations

Different work types benefit from different models:

- **Research:** Claude Opus recommended for deep investigation
- **Planning/Execution:** Claude Sonnet works well

If a different model is in use, inform the user but don't block:
```text
Note: [Work type] typically works best with [recommended model].
You're currently using [current model].
```

### 3. Context Loading by Work Type

#### For Research Continuation

1. **Load Context:**
   - Research document: `PACE/research/RESEARCH-[###]-[topic-name].md`
   - Files from "Essential to Reload" section
   - Outstanding questions from "Open Questions" section

2. **Resume:**
   - Continue investigation from "Current Focus"
   - Address remaining questions
   - Document findings in research document

#### For Planning Continuation

1. **Load Context:**
   - Plan document: `PACE/plans/PLAN-[###]-[task-name].md`
   - Research document if referenced
   - Files from "Essential to Reload" section

2. **Resume:**
   - Continue with section from "Current Focus"
   - Address items in "Planning Priorities"
   - Complete remaining plan sections

#### For Execution Continuation

1. **Load Context:**
   - Execution document: `PACE/prompts/EXECUTION-[###]-[task-name]-[date].md`
   - Plan document if referenced
   - Deliverables in progress

2. **Resume:**
   - Continue with task from "Current Focus"
   - Follow execution priorities
   - Complete remaining deliverables

#### For General Work Continuation

1. **Load Context:**
   - Read compaction file for work summary
   - Load any referenced files
   - Understand what was being worked on

2. **Resume:**
   - Continue from documented state
   - Address priorities listed

### 4. Verify Before Resuming

Quick check before starting work:
- [ ] Essential files loaded
- [ ] Current state understood
- [ ] Next priority identified
- [ ] Previous learnings noted

### 5. Resume Work

1. **Continue Work:**
   - Execute the next task identified
   - Update relevant documents as you progress
   - Maintain continuity with previous session

2. **Monitor Context:**
   - Check context utilization periodically
   - If approaching 40%, prepare for compaction:
     ```text
     Context approaching [X]%. Consider running /compact soon.
     ```

3. **Update Progress:**
   - Add accomplishments to progress.md
   - Update next priorities
   - Note any blockers discovered

### 6. Subagent Usage

When context is high, delegate to subagents:

**Explore subagent** (`subagent_type=Explore`)
- Finding files and information
- Quick searches

**general-purpose subagent** (`subagent_type=general-purpose`)
- Complex analysis
- Deep research tasks

## Error Recovery

If continuation is unclear:
1. Check for most recent compaction file in `PACE/prompts/context-management/`
2. Verify progress.md exists and has useful information
3. Ask user for clarification on what to resume

## Usage

Invoke this command after starting a fresh Claude Code session. It automatically detects your work state and loads appropriate context.
