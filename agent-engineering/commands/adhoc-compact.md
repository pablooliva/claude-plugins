# Generic Session Compaction

GENERIC SESSION COMPACTION

Context is getting high during work. Create a lightweight compaction record to preserve your progress while freeing up context. Use this for smaller tasks, follow-up work, or when phase-specific compaction is overkill.

## IMPORTANT: Active Phase Detection

**Before proceeding, check if an SDD development phase is currently active.**

Read `SDD/orchestration/progress.md` (if it exists) and decide from **what this session has been working on**, not from which files exist — finished features leave their research, spec, and plan documents behind, so the files alone prove nothing:

- `progress.md` shows a feature in progress (a `## Flow Started - ` record with no `Finished:` line, or phase entries with no completion), **and** this session's work was on that feature → a phase is active. Which one: research (no accepted research yet), planning (a spec being written or reviewed), or implementation (code being written against a spec).
- This session's work was something else — a follow-up, a fix, a review, plugin or tooling work — → no phase is active for this compaction, whatever `progress.md` holds.

**If a phase is active, STOP and redirect the user:**

- **Research** → Tell the user: "You appear to be in the **research phase**. Use `/agent-engineering:research-compact` instead — it captures research-specific context (investigations, system behavior, critical learnings) that this generic command would lose."
- **Planning** → Tell the user: "You appear to be in the **planning phase**. Use `/agent-engineering:planning-compact` instead — it captures specification progress, research alignment, and implementation readiness that this generic command would lose."
- **Implementation** → Tell the user: "You appear to be in the **implementation phase**. Use `/agent-engineering:implementation-compact` instead — it captures test status, spec validation, and code change tracking that this generic command would lose."

**Only proceed with this generic compaction if NO active SDD phase is detected**, or if the user explicitly confirms they want the generic version after being warned.

---

## When to Use This vs Phase-Specific Compaction

The phase-specific commands are `/agent-engineering:research-compact`, `/agent-engineering:planning-compact`, and `/agent-engineering:implementation-compact`. They share their instruction sets with `sdd-flow`'s compaction bodies, so a manual compaction produces the same artifact an orchestrated run would. Use the `/agent-engineering:` prefix — the bare names also exist in the `sdd` plugin, which ships the older, frozen copies.

All four commands follow one contract, which `/agent-engineering:continue` relies on: the file goes under `SDD/orchestration/compacted/`; its full path is recorded in `SDD/orchestration/progress.md` (or, when the user picks Skip in step 3 below, handed to them as an explicit `/agent-engineering:continue <path>` command); it carries a `## Continuation Priorities` section holding **Essential Files to Reload**, **Current Focus**, and a numbered priority list; and a pending `## Awaiting …` block in `progress.md` stays the latest block. The one exception to the last point is a deliberate abandonment — step 3's "Archive everything, start fresh", taken only on the user's explicit yes.

| Use `/adhoc-compact` when:            | Use phase-specific when:              |
| ------------------------------------- | ------------------------------------- |
| Working on smaller tasks              | Deep in a full phase workflow         |
| Follow-up work after phase completion | Need detailed phase artifacts         |
| Ad-hoc investigations                 | Want full phase template              |
| Quick context reset needed            | Starting fresh development cycle      |

## Process

### 1. Create Timestamped Compaction File

Write to: `SDD/orchestration/compacted/compact-[YYYY-MM-DD_HH-MM-SS].md`

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

## Critical Review Status
[Check for critical review documents in SDD/reviews/CRITICAL-*.md]
- Review performed: [yes/no]
- Review document(s): [paths to any CRITICAL-*.md files if they exist]
- Unresolved findings: [list any HIGH/MEDIUM findings not yet addressed]
- Pending actions: [findings that still need attention in next session]

## Continuation Priorities

**Essential Files to Reload:**
[Files needed to resume - use file:line format]
- [Primary file being worked on]
- [Related reference files]
- [Critical review document(s) if they exist]

**Current Focus:**
- [Exact point to continue from]

**Priorities:**
1. [First thing to do]
2. [Second thing to do]

**Open Questions:**
- [Any unresolved questions]

## Notes

[Any other important context for continuation]
```

### 3. Update Progress File

**Before updating `SDD/orchestration/progress.md`, check its contents:**

1. **Read existing progress.md** (if it exists)
2. **Determine relevance:**
   - Does it describe the same task/feature you're currently working on?
   - Is it from a different, unrelated task?

**If progress.md contains unrelated work:**

**STOP and ask the user first.** Present options:

1. **Append** - Add current task as a new section in existing progress.md. Right when the other work is still wanted — for example an `sdd-flow` feature that is part-way through and will be resumed. Its entries are not leftovers: they are what `/sdd-flow continue` resumes from. [recommended in that case]
2. **Rotate, then append** - Move the unrelated, *resolved* history to `SDD/orchestration/progress-archive/` by the step 4 procedure, then add the current task. Pending `## Awaiting *` / `## PARTIAL*` blocks and an active feature's phase-state lines stay in the live file — an `sdd-flow` run resumes from them. Right when the file has grown long and the other work is still wanted.
3. **Archive everything, start fresh** - A deliberate abandonment, not a rotation: it is the one operation allowed to take pending blocks out of the live file. Right when the other work is finished or **abandoned** and its entries really are leftovers. Move the whole file to `SDD/orchestration/progress-archive/progress-set-aside-[YYYY-MM-DD_HH-MM-SS].md` (create the folder if absent) and create a fresh `progress.md` with only the current task. Nothing is deleted: moving the file back restores it. **If the file holds an unfinished `sdd-flow` feature** — a `## Flow Started - ` record with no `## Feature - Done` after it; or any pending `## Awaiting *` / `## PARTIAL*` block; or, in a file written by an older version with no `## Flow Started - ` line, any research, planning, or implementation entry for a feature that has no `## Feature - Done` or `Finished:` line — say so before doing it, naming the feature and the step it stopped at, and that `/sdd-flow continue` will no longer resume it unless the file is moved back. Proceed only on an explicit yes. In the fresh file's `## Current State`, add the line `Set aside: <archive path>` so the earlier work can be found.
4. **Skip** - Don't update progress.md, only create the compaction file. Whatever compaction path `progress.md` already names stays the one a bare `/continue` loads — and if it names none, `/continue` would have to guess among the files in the folder — so the next session must be given this one explicitly: tell the user to run `/agent-engineering:continue <the file's full path>`, and put that exact command in your final message.

Never overwrite or delete `progress.md`: it may hold the state of a feature that is still being built, and option 3 clears the live file just as well without losing anything.

Wait for user response before proceeding.

**If progress.md is relevant to current work (or doesn't exist):**

Update/create with:

- Current work state
- Reference to this compaction file
- Next session continuation point

```markdown
## Current State

- Last compaction: SDD/orchestration/compacted/compact-[timestamp].md
- Working on: [task description]
- Next step: [what to do next]
```

**A pending halt stays latest.** If the latest block in `progress.md` is an `## Awaiting …` block, an `sdd-flow` run is stopped waiting for an answer, and the flow finds that stop by its being the latest block. Write your entry directly **above** that block, never below it.

### 4. Rotate `progress.md` If Oversized

Compaction shrinks the *session*; `progress.md` is durable state that every future session and subagent re-reads — compacting context without rotating an oversized progress file re-imports the same cost next session. If `progress.md` exceeds **~500 lines**:

1. Create `SDD/orchestration/progress-archive/` if absent; move completed-feature history and verbose *resolved* blocks (including completed-phase history of the still-active feature) to `progress-archive/progress-[scope]-[YYYY-MM-DD_HH-MM-SS].md`.
2. Rewrite the live head as a bounded `## Current State` (active feature, phase status with canonical phase-state lines carried verbatim, artifact pointers, "History archived to <path>"). **When the file holds an `sdd-flow` feature that is not finished, follow the full procedure in `skills/sdd-flow/phases/protocols.md` → Progress Rotation, not this summary:** that feature keeps its Step 0 record (the `## Flow Started - ` line and the lines under it — mode, flags, paths), its phase-state lines verbatim and in their original order, and every block of the phase still in progress. Only the history of phases already marked done is moved.
3. **Carry forward verbatim, as the latest blocks, anything still pending** (any `## Awaiting *` or `## PARTIAL*` header — prefix match, not a fixed list) — resumption matches the latest block in the live file and never reads archives.
4. Note the rotation in the new head.

Everything that remains in the live file must stay **byte-identical** — move content mechanically, never retype, reflow, or summarize it; the only newly written text is the `## Current State` head and the rotation note.

## Guidelines

- **Keep it brief** - this is meant to be lighter than phase-specific compaction
- **Focus on resumability** - capture just enough to pick up where you left off
- **Use file:line references** - avoid pasting large code blocks
- **Be specific about next steps** - make it easy to resume quickly

## Next Steps After Compaction

1. **Clear the session** - Close Claude Code or start new conversation
2. **Start fresh** - Open new Claude Code session
3. **Run `/agent-engineering:continue`** - Resume from where you left off (with the file's path as an argument if you chose Skip in step 3). Use the prefix: the `sdd` plugin ships an older `/continue`.

The continue command loads the file named on the `Last compaction:` line and reloads your context.

## Quick Compaction Checklist

Before finishing, verify:

- [ ] Work summary captures what was done
- [ ] "Essential Files to Reload" has file:line pointers
- [ ] "Current Focus" is specific and actionable
- [ ] Progress file is updated, and its `Last compaction:` line carries the file's full path (Skip chosen: the user has the exact `/agent-engineering:continue <path>` command instead)
- [ ] A pending `## Awaiting …` block, if there was one, is still the latest block
- [ ] `progress.md` rotated if it exceeded ~500 lines (pending blocks carried forward)
