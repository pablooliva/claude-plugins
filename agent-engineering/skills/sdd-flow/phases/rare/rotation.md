# Rare case — Progress Rotation

Read this only when `progress.md` exceeds ~500 lines at a quiet point a phase chapter names, or at the feature-completion rotation (4j).

---

## Progress Rotation (orchestrator-only)

`progress.md` is append-only **within a generation**; rotation starts a new generation. Only the orchestrator rotates, only between spawns (never mid-subagent).

**Triggers:** (a) feature completion — Step 4j / per-slice end-of-feature 4j; (b) the live file exceeds ~500 lines at a phase-boundary commit (2e, 3f, 4i, per-slice 4c.6) or during an interactive compact/continue.

**Procedure:**
1. Create `SDD/.records/progress-archive/` if absent. Move the verbose history to `progress-archive/progress-[SPEC-### or scope]-[YYYY-MM-DD_HH-MM-SS].md` — feature-completion rotation moves that feature's full history; size rotation moves all *resolved* blocks, **including — within the still-active feature — blocks of phases the orchestrator has marked done** (`## Research - Accepted`, `## Planning - Accepted`: e.g., the research and planning history of a feature still in implementation). Blocks of the currently active phase always stay live.
2. Rewrite the live `progress.md` head as a bounded `## Current State`: canonical identifiers, SKILL_ROOT, flags, artifact pointers, and "History archived to <path>". Below it:
   - **A finished feature is one line** of the form `Finished: SPEC-[###] [feature-name] — <outcome>; history: <archive path>` — plain text with no `## ` header and none of the marker strings below, so no phase rule can ever match it.
   - **The active feature keeps its Step 0 record** (the `## Flow Started - ` line and the lines under it) and, after it, its canonical phase-state lines **verbatim and in their original order**: `## Research - Accepted`, every `## Design Brief - ` line and the `Observability record: …` line under each `APPROVED` one, every `## Re-plan Requested` line, `## ADR Candidates` / `## ADR Candidate Dropped - ` / `## ADR Capture - Done`, `Planning Phase - COMPLETE`, every `## Gates - ` line (the latest one after the latest `Planning Phase - COMPLETE` holds the tracing gate and the evals gate every later spawn is passed), `## Planning - Accepted` (each one — a re-plan writes a second, and the slice rules read only what follows the latest), `## Feature - Implementing` with its `Base commit:` line, `Implementation Phase - COMPLETE`, `## Implementation - Committed`. Phase Detection (`phases/rare/resume.md`) matches these literal markers, not paraphrases, and reads only what follows the latest `## Flow Started - ` line.
3. **Carry forward verbatim, as the latest blocks, every pending halt block.** A pending halt block is ANY block whose header starts with `## Awaiting ` or `## PARTIAL` — match the prefix, not a fixed list; real files contain custom halt headers. (Canonical forms: `## Awaiting Clarification`, `## Awaiting Design Approval`, `## Awaiting Spec Approval`, `## Awaiting Gate Decision`, `## Awaiting Eval Run`, `## Awaiting Slice Resolution`, `## Awaiting Final Check Resolution`, `## Awaiting Commit Approval`, `## PARTIAL: needs continuation`.) Carry anything Phase Detection or the Mid-Phase Handoff protocol still needs. Resolved blocks are archived; pending ones never are.
4. Append a `### Progress rotated ([YYYY-MM-DD_HH-MM-SS])` line recording the archive path.

**Invariants:** Everything that remains in the live file is preserved **byte-identical** — moved or kept by mechanical operations, never retyped, reflowed, re-encoded, or summarized; the ONLY newly written text in a rotation is the `## Current State` head, a finished feature's `Finished:` line, and the `### Progress rotated` stamp. Phase Detection (`phases/rare/resume.md`) operates ONLY on the live `progress.md`; archives are never scanned. Pending blocks survive every rotation. The audit trail is preserved in the archive files and in git history (phase-boundary commits include `progress.md`).

**Not a rotation: setting a file aside.** `/adhoc-compact` can move the whole `progress.md` — pending blocks included — to `progress-archive/` and start a fresh one, when the user says the work in it is finished or abandoned (`commands/adhoc-compact.md` → step 3). It warns first when the file holds an unfinished feature and needs an explicit yes, because the feature stops being resumable until the file is moved back. That is a user's deliberate abandonment, outside the invariants above; the orchestrator never does it, and no rotation ever archives a pending block.
