# Continue Session from Progress

CONTINUE FROM PREVIOUS SESSION

This command resumes your work after using a compaction command and clearing your session.

## When to Use This Command

You should run `/continue` when:

- ✅ You've run a compact command (`/adhoc-compact`, `/agent-engineering:research-compact`, `/agent-engineering:planning-compact`, `/agent-engineering:implementation-compact`)
- ✅ You've cleared your Claude Code session
- ✅ You're starting fresh and want to resume where you left off

This is the REQUIRED next step after any compaction.

## Workflow Overview

```text
WORK IN PROGRESS        CONTEXT ~40%             CLEAR SESSION         FRESH START
       │                     │                        │                     │
       ▼                     ▼                        ▼                     ▼
  [working] ──────────► [compact command] ───────► [/clear] ───────────► [/continue]
                             │                                              │
                             └─ writes one file under                       │
                                SDD/orchestration/compacted/                │
                                and records its path in progress.md ◄─ reads both
```

- **Compact**: when context approaches 40%, run one of the four compact commands. Each writes exactly one file under `SDD/orchestration/compacted/` and records that file's path in `SDD/orchestration/progress.md` (the one exception: `/adhoc-compact`'s Skip option, which hands you the path to pass to this command instead).
- **Commit (optional)**: `/commit` saves work before the session is cleared. Do **not** commit implementation work while an `sdd-flow` run is implementing a feature — the flow commits each slice or feature once, after its review, and a commit made earlier puts unreviewed code into history and splits that one commit in two.
- **Clear**, then **Continue**: `/agent-engineering:continue` in a fresh session reads `progress.md` and the compaction file it names. Use the prefix — the `sdd` plugin ships an older `/continue` that looks in a different place.

| Compact command | File it writes (under `SDD/orchestration/compacted/`) |
|---|---|
| `/adhoc-compact` | `compact-[YYYY-MM-DD_HH-MM-SS].md` |
| `/agent-engineering:research-compact` | `research-compacted-[YYYY-MM-DD_HH-MM-SS].md` |
| `/agent-engineering:planning-compact` | `planning-compacted-[YYYY-MM-DD_HH-MM-SS].md` |
| `/agent-engineering:implementation-compact` | `implementation-compacted-[YYYY-MM-DD_HH-MM-SS].md` |

All four templates carry the same `## Continuation Priorities` section — **Essential Files to Reload**, **Current Focus**, and a numbered priority list — and that section is what this command resumes from.

## Process

### 1. Load Progress and Compaction Files

1. **Read Main Progress File:**
   - Load `SDD/orchestration/progress.md`
   - Identify current phase (research/planning/implementation)
   - Note completion status and next priorities
   - Check for any subagent delegations that need follow-up

2. **Locate the Compaction File** — one rule, in this order; stop at the first that applies:
   1. **A path given with the command** (`/agent-engineering:continue <path>`) → load that file.
   2. **The path `progress.md` names.** Every compact command records it there: the latest `## PARTIAL: needs continuation` block (phase-specific commands) or the `Last compaction:` line under `## Current State` (`/adhoc-compact`). Whichever is later in the file wins. Load exactly that file. **If the named file is missing, stop and tell the user** — do not substitute another file; a different file is different work.
   3. **`progress.md` names none** → list `SDD/orchestration/compacted/` (and, only if that is empty or absent, `SDD/orchestration/` itself, where older versions wrote) for these names, newest first by the timestamp in the name (`YYYY-MM-DD_HH-MM-SS`, 24-hour):
      - Research phase: `research-compacted-[YYYY-MM-DD_HH-MM-SS].md`
      - Planning phase: `planning-compacted-[YYYY-MM-DD_HH-MM-SS].md`
      - Implementation phase: `implementation-compacted-[YYYY-MM-DD_HH-MM-SS].md`
      - Generic (any work): `compact-[YYYY-MM-DD_HH-MM-SS].md`

      Exactly one candidate → load it and say that it was the only one. Several → show the newest few with their first heading line and ask the user which to resume; never pick silently — the newest file may belong to different work.
   - Tell the user which file you loaded and which of the three steps found it.
   - Never load `site-count-compacted-*.md`: that is a blind site count's handoff inside an `sdd-flow` run, and only the flow may continue it.

3. **Check for a Pending `sdd-flow` Stop:**
   - An `## Awaiting …` block is pending when it is the latest block in `progress.md` — or when the only things after it are compaction records (`## Current State`, `## PARTIAL: needs continuation`), which older compact commands appended below it. No `## Halt Resolved - ` line or later flow entry follows a pending block.
   - If one is pending, an `sdd-flow` run is stopped waiting for an answer. Show the block to the user and tell them `/sdd-flow continue` is what resumes it. Do not do that feature's work past the stop from here. Work the compaction file describes that is separate from the stopped flow can go on.

**If `progress.md` exceeds ~500 lines**, rotate it before resuming — same procedure as `/adhoc-compact` step 4: archive completed-feature history and resolved blocks (including completed-phase history of the still-active feature) to `SDD/orchestration/progress-archive/`, keep a bounded `## Current State` carrying canonical phase-state lines verbatim, and carry any pending `## Awaiting *` / `## PARTIAL*` blocks (prefix match, not a fixed list) forward verbatim as the latest blocks. Everything kept in the live file must stay byte-identical — never retype or summarize it.

### 2. Pre-Continuation Quality Check

Before resuming work, verify from compaction file:

- [ ] `## Continuation Priorities` → **Essential Files to Reload** lists the files, with line ranges where they matter
- [ ] `## Continuation Priorities` → **Current Focus** identifies the exact task to resume
- [ ] Blocking items and open questions are documented
- [ ] The numbered priority list gives clear next steps
- [ ] `## Critical Review Status` says whether review findings are still open

A generic file written by `/adhoc-compact` before 3.5.1 uses older names for the same things: `## Critical References` for the files, and `## Next Session` → **Resume From** / **Immediate Priorities** for the focus and the priority list. Read them as equivalents.

If any critical information is missing, ask user for clarification before proceeding.

### 3. Context Loading by Compaction Type

The file's name says which branch applies.

#### For Generic Continuation (`compact-*.md`)

1. **Load Context:**
   - Files from **Essential Files to Reload** — only the ranges named
   - `## Key Discoveries` and `## Notes`: findings and working agreements to carry over
   - `## Critical Review Status`: any finding still open

2. **Verify State:**
   - `## Work Summary`: what is completed, in progress, remaining
   - `git status` and `git log` against what the file says was committed
   - **Open Questions**: anything the user still has to decide

3. **Resume:**
   - Continue from **Current Focus**, then the numbered priorities in order
   - If the first priority is waiting on the user's go-ahead, say so and wait for it

#### For Research Phase Continuation

1. **Load Research Context:**
   - Research document: `SDD/research/RESEARCH-[###]-[feature-name].md`
   - Files from "Essential Files to Reload" section in compaction
   - Recent investigation areas from "Recent Investigations" and "Research Priorities"

2. **Verify Research State:**
   - Review "Research Progress" section (completed/in-progress/planned)
   - Check "Outstanding Research Questions" checklist
   - Identify current investigation focus
   - Note any "System Behavior Discovered" insights

3. **Resume Research:**
   - Continue with exact investigation from "Current Focus" section
   - Follow up on any incomplete subagent delegations
   - Use Explore subagent for file discovery when context is high
   - Document findings in research document

#### For Planning Phase Continuation

1. **Load Planning Context:**
   - Specification document: `SDD/requirements/SPEC-[###]-[feature-name].md:[lines]`
   - Research document: `SDD/research/RESEARCH-[###]-[feature-name].md:[sections]`
   - Files from "Essential Files to Reload" with specific line ranges
   - Review "Inline Investigation Performed" so the same searches are not repeated

2. **Verify Specification State:**
   - Review "Specification Progress" (completed sections vs remaining)
   - Check "Specification Quality Checklist" status
   - Identify exact section being worked on
   - Review "Implementation Readiness Assessment" if present

3. **Resume Planning:**
   - Continue with section from "Current Focus"
   - Apply "Research Foundation Applied" findings
   - Address items in "Planning Priorities" list
   - Complete any pending subagent research tasks

#### For Implementation Phase Continuation

1. **Load Implementation Context:**
   - Implementation prompt: `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[date].md`
   - Specification: `SDD/requirements/SPEC-[###]-[feature-name].md`
   - Files from "Essential Files to Reload"
   - Review "Critical Learnings" and "Recent Changes" from compaction

2. **Verify Implementation State:**
   - Review completed vs remaining implementation tasks
   - Check "Tests Status" section for test coverage
   - Identify current implementation focus
   - Review "Specification Validation Remaining" checklist

3. **Resume Implementation:**
   - Continue with task from "Current Focus"
   - Follow the "Implementation Priorities" list
   - Work through "Specification Validation Remaining"
   - Maintain <40% context utilization
   - If an `sdd-flow` run is implementing this feature, leave the work uncommitted — the flow owns the commit

### 4. Quality Verification Before Resuming

Complete this checklist before starting work:

- [ ] All essential files successfully loaded
- [ ] Understanding of current phase status is clear
- [ ] Next priority task is specifically identified
- [ ] Previous session's critical learnings are understood
- [ ] Blocking items or questions are noted
- [ ] Any subagent delegations from previous session are acknowledged

If any verification fails, ask user for clarification before proceeding.

### 5. Resume Work with Context Management

1. **Continue Work:**
   - Execute the specific next task identified
   - Update relevant phase document as you progress
   - Maintain continuity with previous session's approach
   - Follow up on any incomplete subagent tasks

2. **Monitor Context Usage:**
   - Check context utilization regularly
   - If approaching 40%, prepare for compaction
   - Warn user when compaction is needed:

     ```text
     Context utilization is approaching [X]%.
     Please save your work and run the appropriate compact command:
     - Quick/lightweight (ad-hoc work only): /adhoc-compact
     - Research phase: /agent-engineering:research-compact
     - Planning phase: /agent-engineering:planning-compact
     - Implementation phase: /agent-engineering:implementation-compact
     ```

3. **Update Progress File:**
   - Add new accomplishments to progress.md
   - Keep its next-step line current
   - Note any new blocking items discovered
   - Document any new subagent delegations
   - **IMPORTANT: DO NOT reset or delete previous phase information - append to it**
   - **A pending halt stays latest.** If `progress.md` has a pending `## Awaiting …` block (Process step 1), write every update directly **above** that block, never below it — `sdd-flow` finds its stop by that block being the latest, and an entry under it would let the flow resume past a question nobody answered. This holds for work unrelated to the stopped flow too.

### 6. Subagent Delegation Strategy

When context is high during continuation, use subagents strategically:

#### Explore Subagent (`subagent_type=Explore`)

Use for quick, focused searches:

- Finding files by pattern
- Searching for code implementations
- Discovering similar patterns in codebase
- Locating configuration files

Example: "Find all authentication implementations in src/"

#### General-Purpose Subagent (`subagent_type=general-purpose`)

Use for complex analysis tasks:

- Researching best practices
- Analyzing complex architectural decisions
- Finding similar implementations in current codebase
- Investigating technical constraints
- Understanding multi-file interactions

Example: "Analyze how error handling works across the authentication flow"

### 7. Session Continuity Best Practices

To ensure smooth continuation:

1. **Preserve Context Learnings:**
   - Reread "Critical Learnings" carefully (a generic `compact-*.md` file calls it "Key Discoveries")
   - Apply previous discoveries to current work
   - Avoid re-researching already discovered information

2. **Maintain Phase Momentum:**
   - Stay focused on current phase objectives
   - Don't backtrack to previous phases unless critical
   - Trust the work documented in compaction files

3. **Document Incremental Progress:**
   - Update progress.md after each significant milestone
   - Note any new discoveries or blockers immediately
   - Keep the next step in progress.md current

## Important Notes

- The progress.md file is the primary continuation point across all phases
- Compaction files provide detailed context from previous sessions
- Each phase builds upon previous phases - maintain continuity
- If multiple compaction files exist, use the one `progress.md` names; when it names none, ask the user which (Process step 1)
- Never reset or overwrite previous phase information in progress.md

## Error Recovery

If continuation fails or context is unclear:

1. Re-run the file lookup in Process step 1, in its order — a path the user gives, then the path `progress.md` names, then the candidates in `SDD/orchestration/compacted/` (`compact-*.md`, `research-compacted-*.md`, `planning-compacted-*.md`, `implementation-compacted-*.md`) shown to the user to choose from. Never substitute a file for one that is named and missing.
2. Verify progress.md exists and contains phase information
3. Ask user which phase to continue if ambiguous
4. Request specific guidance on next task if priorities are unclear

## Usage

Simply invoke this command after starting a fresh Claude Code session to resume from where you left off. The command will automatically detect your current phase and load the appropriate context.
