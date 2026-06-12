# Protocols — Mid-Phase Handoff · Session Resumption · Phase Detection · Errors

Read this when handling `/sdd-flow continue`, when a subagent returns a "needs continuation" signal, or on any error. These protocols are orchestrator-level and apply across all phases.

---

## Mid-Phase Handoff Protocol (automatic, inside an active flow)

Fires when a phase-execution / fix / continuation subagent trips its Reads Safety-Net and returns a "needs continuation" signal. **Distinct from Session Resumption** (the user re-invoking `/sdd-flow continue` in a fresh session). Both reuse the same artifact formats (`progress.md`, `*-compacted-*.md`); they differ only in trigger.

1. The orchestrator reads ONLY the latest compaction file path and the `## PARTIAL: needs continuation` block in `progress.md` — not the full work product.
2. It spawns a **fresh** `agent-engineering:sdd-workhorse` subagent with **body `bodies/continue.md`**. The successor receives: the resolved compaction file path, all resolved phase artifact paths, the Safety-Net Rule, a **fresh** counter file (`Reads: 0/15`, or `/20` for implementation), the matching compact body path, and an instruction to resume from the compaction file's "Current Focus" section.
3. The successor inherits the Safety-Net Rule and may itself bail out — the orchestrator can chain multiple handoffs within one phase.

---

## Progress Rotation (orchestrator-only)

`progress.md` is append-only **within a generation**; rotation starts a new generation. Only the orchestrator rotates, only between spawns (never mid-subagent).

**Triggers:** (a) feature completion — Step 4j / per-slice end-of-feature 4j; (b) the live file exceeds ~500 lines at a phase-boundary commit (2e, 3f, 4i, per-slice 4c.6) or during an interactive compact/continue.

**Procedure:**
1. Create `SDD/orchestration/progress-archive/` if absent. Move the verbose history to `progress-archive/progress-[SPEC-### or scope]-[YYYY-MM-DD_HH-MM-SS].md` — feature-completion rotation moves that feature's full history; size rotation moves all *resolved* blocks, **including — within the still-active feature — blocks of phases with a recorded COMPLETE banner** (e.g., the research and planning history of a feature still in implementation). Blocks of the currently active phase always stay live.
2. Rewrite the live `progress.md` head as a bounded `## Current State`: canonical identifiers, SKILL_ROOT, mode + flags, per-feature status table with artifact pointers, and "History archived to <path>". The status table MUST carry each feature's canonical phase-state lines verbatim (e.g., `Research Phase - COMPLETE`, `Implementation Phase - COMPLETE`) — Phase Detection (below) matches these literal markers, not paraphrases.
3. **Carry forward verbatim, as the latest blocks, every pending halt block.** A pending halt block is ANY block whose header starts with `## Awaiting ` or `## PARTIAL` — match the prefix, not a fixed list; real files contain custom halt headers. (Canonical forms: `## Awaiting Clarification`, `## Awaiting Slicing Decision`, `## Awaiting Re-planning Decision`, `## Awaiting Re-start Decision`, `## PARTIAL: needs continuation`.) Carry anything Phase Detection or the Mid-Phase Handoff protocol still needs. Resolved blocks are archived; pending ones never are.
4. Append a `### Progress rotated ([YYYY-MM-DD_HH-MM-SS])` line recording the archive path.

**Invariants:** Everything that remains in the live file is preserved **byte-identical** — moved or kept by mechanical operations, never retyped, reflowed, re-encoded, or summarized; the ONLY newly written text in a rotation is the `## Current State` head and the `### Progress rotated` stamp. Phase Detection (below) operates ONLY on the live `progress.md`; archives are never scanned. Pending blocks survive every rotation. The audit trail is preserved in the archive files and in git history (phase-boundary commits include `progress.md`).

---

## Session Resumption (user-triggered `/sdd-flow continue`)

The user re-invokes `/sdd-flow continue` in a fresh session; the orchestrator resumes from the most recent state in `progress.md`:

1. Read `SDD/orchestration/progress.md` (re-derive SKILL_ROOT from the record written at Step 0; re-resolve it if absent).
2. Determine which phase and sub-step is active (Phase Detection Priority below).
3. Resume from the exact sub-step where work was interrupted by spawning the appropriate subagent.
4. If a phase was marked complete in `progress.md`, advance to the next phase.

### Phase Detection Priority

Rules are evaluated top-to-bottom; the first matching rule fires and short-circuits later rules. Detection operates ONLY on the live `progress.md` — archives under `progress-archive/` are never scanned (Progress Rotation above carries pending blocks forward). The legacy-layout rule is FIRST because un-migrated repos cannot evaluate any new-layout rule (no `SDD/orchestration/progress.md` exists for halt-block matching).

- **Old layout detected (legacy 1.x repo, not yet migrated)** — fires when **BOTH** hold (resolves M-1): **(C, must-be-true)** `SDD/orchestration/progress.md` does NOT exist, AND **(A OR B, at least one)** **(A)** `SDD/prompts/context-management/progress.md` exists, OR **(B)** any `SDD/prompts/PROMPT-*.md` files exist. In boolean form: `(A OR B) AND C` (the bare prose `A OR B AND C` parses as `A OR (B AND C)` under standard precedence and is NOT the intended reading). When it fires, emit:
  > Detected legacy SDD layout (1.x). Run `/sdd-migrate-layout` to migrate to the 2.0.0 layout, then re-run `/sdd-flow continue`. The migration helper has its own active-flow gating; if a flow is in progress, you may need to complete it first.

  Halt; do not attempt new-layout phase detection (it would fail — no artifacts there). Do not auto-migrate. When the new-layout `progress.md` IS present (C false), this rule does NOT fire even if legacy artifacts also exist — that is the partly-migrated state; continue to the halt-block rules below. (`/sdd-migrate-layout --resume-partial` is the user-facing recovery for a partly-migrated tree; it operates independently of `/sdd-flow continue`.)

- **`## Awaiting Slicing Decision` block latest in `progress.md`** (practicality gate halted in autonomous mode): branch on the resume flag:
  - `--fall-back-to-whole-feature` → flip the spec's `delivery_mode:` to `whole-feature` (or annotate `Slicing not applicable: <reason>` per REQ-011 escape) and route into the whole-feature Step 4 path with the same SPEC.
  - `--retry-slicing "<hint>"` → re-spawn the planning slice-extraction subagent with the hint embedded; the practicality gate re-fires after slice extraction.
  - No flag → re-emit the same options the original halt block presented, then halt.

- **`## Awaiting Re-planning Decision` block latest in `progress.md`** (resolves M-2 — the orchestrator-written block from per-slice 4c.5 Stage 1, NOT the retro-body header `## Recommended Re-planning`). Branch on the resume flag:
  - `--replan` (alone) → re-run Step 3 (planning) with the rolling ledger and triggering retrospective in the planning subagent's prompt; produce a revised SPEC; resume implementation from `SLICE-001` of the **new** plan. **Slice Progress state management (resolves M-5):** (1) read the existing IMPLEMENTATION-PLAN's `## Slice Progress` table; (2) move it verbatim under a new header `## Archived Slice Progress (pre-replan)` immediately above the soon-to-be-rewritten `## Slice Progress` (audit trail; not deleted); (3) after Step 3 re-runs and produces the revised SPEC, instruct the implementation subagent to write a FRESH `## Slice Progress` reflecting the NEW plan's `## Delivery Slices`, all rows `Not Started` (the new SLICE-001 may name a different slice than before); (4) old `REVIEW-SLICE-*`, `RETROSPECTIVE-SLICE-*`, ledger entries, and per-slice commits are NOT deleted — they remain as audit trail; (5) the user owns which prior commits to keep/revert/fold — the orchestrator does NOT auto-revert. If the new plan re-implements old work, the slice-review subagent catches the divergence at the new SLICE-001.
  - `--replan --from-slice SLICE-XXX` → as `--replan`, but the user names a slice from the NEW plan to resume from. **Validation (REQ-025):** `SLICE-XXX` MUST match `^SLICE-\d{3}$` AND reference an existing entry in the **new** spec's `## Delivery Slices` (validation runs AFTER Step 3 produces the revised SPEC — `--from-slice` cannot be validated until the new plan exists). Invalid → fail with a clear error naming the violation. **State:** initialize the fresh `## Slice Progress` with all rows `Not Started` EXCEPT the named slice and any prior slices the user explicitly imported as `Complete` (default: none). The orchestrator does NOT auto-import prior `Complete` rows (prior slice IDs may not match new ones); the user edits the table manually if desired.
  - `--override-replan` → continue with the current plan despite the recommendation. Slice Progress unchanged; advance to the next slice.
  - No flag (or the invalid `--replan --override-replan`) → re-prompt with the three options. `--replan --override-replan` is invalid — fail with a clear error naming the conflict; halt.
  - Re-planning halts fire **regardless of `--skip-slice-checkpoints`** per REQ-014. (See EDGE-006 in `phases/implementation-per-slice.md`: plain `continue` with a pending re-planning halt → informative refusal, no work performed.)

- **`## Awaiting Re-start Decision` block latest in `progress.md`** (slice-start `--force` halted in autonomous mode per EDGE-013): resume requires explicit confirmation; `/sdd-flow continue --confirm-restart SLICE-XXX` proceeds with the destructive overwrite of the named already-`Complete` slice's row; otherwise re-prompt with the original options and halt.

- If **"Implementation Phase - COMPLETE"** → Done, show final summary.
- If implementation is active → resume the appropriate sub-step (4a–4j or the per-slice cycle).
- If **"Planning Phase - COMPLETE"** → start Step 4 (route on `delivery_mode:`).
- If planning is active → resume the appropriate sub-step (3a–3g).
- If **"Research Phase - COMPLETE"** → start Step 3 (planning).
- If research is active → resume the appropriate sub-step (2a–2f).
- If `## Awaiting Clarification` is latest AND `SDD/research/CLARIFICATION-[###]-[feature-name].md` now exists → resume at Step 2 (gate satisfied). If it still doesn't exist, re-prompt the user to run `/research-clarify` or skip.
- If no phase info → start from Step 0 (read `phases/setup.md`).

---

## Error Handling

If a subagent fails or returns incomplete results, the orchestrator:
1. Logs the failure in `progress.md`.
2. Re-spawns the subagent with additional context about what went wrong.
3. If the same subagent fails twice, stops and informs the user.

---

## Why the safety-net is count-based, not percentage-based

A spawned subagent has no first-class way to read its own context utilization — `/usage` is a harness slash command available only to the top-level interactive Claude, and the API returns token counts to the harness, not the model. Any self-audit a subagent performs produces output tokens that land back in its own context, partially eating the budget it is trying to measure. Count-based triggers (file Reads) are nearly free to evaluate (rule application, not deliberation), are inspectable in the counter file, and don't require the subagent to know anything its harness won't tell it. Because subagents do not spawn in this flow (a platform limit on Claude Code ≤2.1.171; a deliberate design rule from 2.1.172, which allows nesting to depth 5 — see `proposals/nested-subagents-analysis-2026-06-12.md`), there is no nested-subagent count — Reads is the whole signal. Defaults (Reads >15, or >20 for implementation chunks) are tunable without changing the protocol.
