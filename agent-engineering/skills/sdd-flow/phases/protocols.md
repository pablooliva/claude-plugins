# Protocols — Mid-Phase Handoff · Session Resumption · Phase Detection · Errors

Read this when handling `/sdd-flow continue`, when a subagent returns a "needs continuation" signal, or on any error. These protocols are orchestrator-level and apply across all phases.

---

## Mid-Phase Handoff Protocol (automatic, inside an active flow)

Fires when a phase-execution / fix / continuation subagent trips its Reads Safety-Net and returns a "needs continuation" signal. **Distinct from Session Resumption** (the user re-invoking `/sdd-flow continue` in a fresh session). Both reuse the same artifact formats (`progress.md`, `*-compacted-*.md`); they differ only in trigger.

1. The orchestrator reads ONLY the latest compaction file path and the `## PARTIAL: needs continuation` block in `progress.md` — not the full work product.
2. It spawns a **fresh** `agent-engineering:sdd-workhorse` subagent with **body `bodies/continue.md`**. The successor receives: the resolved compaction file path, all resolved phase artifact paths, the Safety-Net Rule, a **fresh** counter file (`Reads: 0/15`, or `/20` for implementation), the matching compact body path, and an instruction to resume from the compaction file's "Current Focus" section.
3. The successor inherits the Safety-Net Rule and may itself bail out — the orchestrator can chain multiple handoffs within one phase.

**Blind site-count handoff (4a.5 / 4e.5).** When the `## PARTIAL` block names a blind site count (compaction file `site-count-compacted-*.md`), the successor must stay blind. Its prompt carries ONLY: the `bodies/continue.md` path with the line "You are continuing a blind site count", the `bodies/site-count.md` path, that one compaction file, the SPEC / glossary / STANDARD paths, SCOPE, ITER, the code range, the OUTPUT path, a fresh counter (`Reads: 0/20`), and `bodies/site-count-compact.md` as the compact body — **plus the same allow-list extras a fresh count at that scope and iteration receives** (`phases/implementation-per-slice.md` → 4a.5): the **CONVENTIONS** path if that file exists, the `ALSO INVENTORY` SPEC IDs if the previous review recorded any (IDs only), and, at `SLICE-XXX` scope, the slice's `Modules touched`. The orchestrator derives these exactly as it would for a fresh spawn; the compaction file's Assignment section records what the first counter was given, as a cross-check. Without them the successor files sites under different keys (false mismatches) and skips controls a reviewer asked to have counted. Never pass phase artifact paths, the IMPLEMENTATION-PLAN, the site inventory, or `progress.md` excerpts.

---

## Progress Rotation (orchestrator-only)

`progress.md` is append-only **within a generation**; rotation starts a new generation. Only the orchestrator rotates, only between spawns (never mid-subagent).

**Triggers:** (a) feature completion — Step 4j / per-slice end-of-feature 4j; (b) the live file exceeds ~500 lines at a phase-boundary commit (2e, 3f, 4i, per-slice 4c.6) or during an interactive compact/continue.

**Procedure:**
1. Create `SDD/orchestration/progress-archive/` if absent. Move the verbose history to `progress-archive/progress-[SPEC-### or scope]-[YYYY-MM-DD_HH-MM-SS].md` — feature-completion rotation moves that feature's full history; size rotation moves all *resolved* blocks, **including — within the still-active feature — blocks of phases the orchestrator has marked done** (`## Research - Accepted`, `## Planning - Accepted`: e.g., the research and planning history of a feature still in implementation). Blocks of the currently active phase always stay live.
2. Rewrite the live `progress.md` head as a bounded `## Current State`: canonical identifiers, SKILL_ROOT, mode + flags, artifact pointers, and "History archived to <path>". Below it:
   - **A finished feature is one line** of the form `Finished: SPEC-[###] [feature-name] — <outcome>; history: <archive path>` — plain text with no `## ` header and none of the marker strings below, so no phase rule can ever match it.
   - **The active feature keeps its Step 0 record** (the `## Flow Started - ` line and the lines under it) and, after it, its canonical phase-state lines **verbatim and in their original order**: `## Research - Accepted`, every `## Design Brief - ` line, `## ADR Candidates` / `## ADR Candidate Dropped - ` / `## ADR Capture - Done`, `Planning Phase - COMPLETE`, `## Planning - Accepted`, `## Feature - Implementing` with its `Base commit:` line, `Implementation Phase - COMPLETE`, `## Implementation - Committed`. Phase Detection (below) matches these literal markers, not paraphrases, and reads only what follows the latest `## Flow Started - ` line.
3. **Carry forward verbatim, as the latest blocks, every pending halt block.** A pending halt block is ANY block whose header starts with `## Awaiting ` or `## PARTIAL` — match the prefix, not a fixed list; real files contain custom halt headers. (Canonical forms: `## Awaiting Clarification`, `## Awaiting Design Approval`, `## Awaiting Deviation Approval`, `## Awaiting Slicing Decision`, `## Awaiting Re-planning Decision`, `## Awaiting Re-start Decision`, `## Awaiting Site-Count Resolution`, `## Awaiting Commit Approval`, `## PARTIAL: needs continuation`.) Carry anything Phase Detection or the Mid-Phase Handoff protocol still needs. Resolved blocks are archived; pending ones never are.
4. Append a `### Progress rotated ([YYYY-MM-DD_HH-MM-SS])` line recording the archive path.

**Invariants:** Everything that remains in the live file is preserved **byte-identical** — moved or kept by mechanical operations, never retyped, reflowed, re-encoded, or summarized; the ONLY newly written text in a rotation is the `## Current State` head, a finished feature's `Finished:` line, and the `### Progress rotated` stamp. Phase Detection (below) operates ONLY on the live `progress.md`; archives are never scanned. Pending blocks survive every rotation. The audit trail is preserved in the archive files and in git history (phase-boundary commits include `progress.md`).

---

## Session Resumption (user-triggered `/sdd-flow continue`)

The user re-invokes `/sdd-flow continue` in a fresh session; the orchestrator resumes from the most recent state in `progress.md`:

1. Read `SDD/orchestration/progress.md` (re-derive SKILL_ROOT from the record written at Step 0; re-resolve it if absent). If that record carries `Next-tier cycle` lines (`phases/setup.md` → Starting the next tier), this is a next-tier cycle: take the tier, **TIER_PLAN**, and the previous tier's research document from them and pass them to every spawn exactly as a fresh run would — never derive the tier plan's path from the suffixed feature name.
2. Determine which phase and sub-step is active (Phase Detection Priority below).
3. Resume from the exact sub-step where work was interrupted by spawning the appropriate subagent.
4. If the orchestrator's marker says a phase is done (table below), advance to the next phase.

### Phase Detection Priority

Rules are evaluated top-to-bottom; the first matching rule fires and short-circuits later rules. Detection operates ONLY on the live `progress.md` — archives under `progress-archive/` are never scanned (Progress Rotation above carries pending blocks forward). The legacy-layout rule is FIRST because un-migrated repos cannot evaluate any new-layout rule (no `SDD/orchestration/progress.md` exists for halt-block matching).

**Scope: the current feature only.** Every rule below reads only the lines after the latest `## Flow Started - ` line — the Step 0 record (`phases/setup.md`). Markers above it belong to earlier features and never match, and a finished feature's `Finished:` summary line matches nothing. If the file has no `## Flow Started - ` line at all (a run started before 3.5.1), read the whole file.

**Only the orchestrator declares a phase done, and only after the phase's last step.** A completion subagent's banner says its own work is finished, never that the phase is:

| Marker | Written by | Means |
|---|---|---|
| `## Flow Started - [###]-[feature-name]` | orchestrator, Step 0 | a feature's record begins here |
| `## Research - Accepted` | orchestrator, after the 2e commit | research is done |
| `Planning Phase - COMPLETE` | completion subagent, 3a | the spec is written — reviews not yet run |
| `## Planning - Accepted` | orchestrator, 3g | planning is done |
| `## Feature - Implementing` (+ `Base commit:`) | orchestrator, before 4a (per-slice: before 4a.0) | implementation has begun; the commit it started from |
| `Implementation Phase - COMPLETE` | completion subagent, 4f | completion documents are written — nothing committed yet |
| `## Implementation - Committed` | orchestrator, after the 4i commit | the code is committed |
| `## Feature - Done` | orchestrator, after the 4j announcement | the feature is done |

**Every stop that waits for an answer has a halt block, a rule here that resumes it, and a row in `docs/sdd-flow-diagram.md`.** Stops that need no answer write no block and say so where they are defined: the slice-boundary pause (a plain `continue` starts the next slice, found from the slice markers), and the terminal stops — decomposition, a broken install, the legacy-layout refusal, a subagent that failed twice — which are not resumed at all.

**A latest halt block always wins.** When the latest block in the file is a `## Awaiting …` or `## PARTIAL…` block, only a halt-block rule may fire: the rule for that header, or the catch-all. The two state rules that sit among the halt rules (a drafted brief with no gate shown; a re-plan's planning run in progress) and every phase rule apply only when no halt block is latest — otherwise they would route past a halt nobody has answered.

- **Old layout detected (legacy 1.x repo, not yet migrated)** — fires when **BOTH** hold (resolves M-1): **(C, must-be-true)** `SDD/orchestration/progress.md` does NOT exist, AND **(A OR B, at least one)** **(A)** `SDD/prompts/context-management/progress.md` exists, OR **(B)** any `SDD/prompts/PROMPT-*.md` files exist. In boolean form: `(A OR B) AND C` (the bare prose `A OR B AND C` parses as `A OR (B AND C)` under standard precedence and is NOT the intended reading). When it fires, emit:
  > Detected legacy SDD layout (1.x). Run `/sdd-migrate-layout` to migrate to the 2.0.0 layout, then re-run `/sdd-flow continue`. The migration helper has its own active-flow gating; if a flow is in progress, you may need to complete it first.

  Halt; do not attempt new-layout phase detection (it would fail — no artifacts there). Do not auto-migrate. When the new-layout `progress.md` IS present (C false), this rule does NOT fire even if legacy artifacts also exist — that is the partly-migrated state; continue to the halt-block rules below. (`/sdd-migrate-layout --resume-partial` is the user-facing recovery for a partly-migrated tree; it operates independently of `/sdd-flow continue`.)

- **`## Awaiting Clarification` block latest in `progress.md`** (the Step 1.5 gate is waiting): if `SDD/research/CLARIFICATION-[###]-[feature-name].md` now exists → resume at Step 2 (gate satisfied); if it still doesn't, re-prompt the user to run `/research-clarify` or skip. This rule sits with the other halt blocks, above the phase rules.

- **`## Awaiting Design Approval` block latest in `progress.md`** (the design gate, Step 2.5b, is waiting): re-show the gate from the brief on disk — `phases/planning.md` → 2.5b — and act on the reply. Nothing is re-spawned. The block's `Re-plan:` line says whether an `approve` continues into a first planning run or a re-plan.

- **The latest `## Design Brief - ` line is `Drafted`, and no `## Awaiting Design Approval` block follows it** (the brief was written or revised, and the flow stopped before the gate was shown): go to 2.5b and show the gate. This rule sits above the implementation rules on purpose — during a re-plan the implementation markers are still present, and without it `continue` would resume the old plan with an unapproved brief. If a re-plan's revise subagent was interrupted before writing its `Drafted` line, `## Awaiting Re-planning Decision` is still the latest block and its rule applies: the user re-issues `--replan`.

- **A re-plan's planning run is in progress** — the latest `## Awaiting Design Approval` block says `Re-plan: yes`, a `## Design Brief - APPROVED` line follows it, and no `## Planning - Accepted` line follows that: resume Step 3 (3a–3g) for the re-plan, with the rolling ledger and the triggering retrospective named in that block, and its `from-slice` value once the new spec exists. Do not resume implementation — its markers belong to the plan being replaced.

- **`## Awaiting Deviation Approval` block latest in `progress.md`** (Step 3g paused because the spec departs from the approved brief): re-read the spec's `## Deviations from Design Brief` — the user may have edited the spec — and re-run the 3g check (`phases/planning.md` → 3g). A section that now reads `None.` routes to Step 4 without a pause.

- **`## Awaiting Slicing Decision` block latest in `progress.md`** (practicality gate halted in autonomous mode): branch on the resume flag:
  - `--fall-back-to-whole-feature` → flip the spec's `delivery_mode:` to `whole-feature` (or annotate `Slicing not applicable: <reason>` per REQ-011 escape) and route into the whole-feature Step 4 path with the same SPEC.
  - `--retry-slicing "<hint>"` → re-spawn the planning slice-extraction subagent with the hint embedded; the practicality gate re-fires after slice extraction.
  - No flag → re-emit the same options the original halt block presented, then halt.

- **`## Awaiting Re-planning Decision` block latest in `progress.md`** (resolves M-2 — the orchestrator-written block from per-slice 4c.5 Stage 1, NOT the retro-body header `## Recommended Re-planning`). Branch on the resume flag:
  - `--replan` (alone) → first re-run **Step 2.5** (`phases/planning.md` → Re-plan): the brief is revised from the rolling ledger and triggering retrospective, and the design gate fires in both modes — a re-plan means the approved design was wrong, and the user is present, having typed the flag. Once the revised brief is approved, re-run Step 3 (planning) with the rolling ledger and triggering retrospective in the planning subagent's prompt; produce a revised SPEC; resume implementation from `SLICE-001` of the **new** plan. **Slice Progress state management (resolves M-5):** (1) read the existing IMPLEMENTATION-PLAN's `## Slice Progress` table; (2) move it verbatim under a new header `## Archived Slice Progress (pre-replan)` immediately above the soon-to-be-rewritten `## Slice Progress` (audit trail; not deleted); (3) after Step 3 re-runs and produces the revised SPEC, instruct the implementation subagent to write a FRESH `## Slice Progress` reflecting the NEW plan's `## Delivery Slices`, all rows `Not Started` (the new SLICE-001 may name a different slice than before); (4) old `REVIEW-SLICE-*`, `RETROSPECTIVE-SLICE-*`, ledger entries, and per-slice commits are NOT deleted — they remain as audit trail; (5) the user owns which prior commits to keep/revert/fold — the orchestrator does NOT auto-revert. If the new plan re-implements old work, the slice-review subagent catches the divergence at the new SLICE-001.
  - `--replan --from-slice SLICE-XXX` → as `--replan`, but the user names a slice from the NEW plan to resume from. **Validation (REQ-025):** `SLICE-XXX` MUST match `^SLICE-\d{3}[a-z]?$` AND reference an existing entry in the **new** spec's `## Delivery Slices` (validation runs AFTER Step 3 produces the revised SPEC — `--from-slice` cannot be validated until the new plan exists). Invalid → fail with a clear error naming the violation. **State:** initialize the fresh `## Slice Progress` with all rows `Not Started` EXCEPT the named slice and any prior slices the user explicitly imported as `Complete` (default: none). The orchestrator does NOT auto-import prior `Complete` rows (prior slice IDs may not match new ones); the user edits the table manually if desired.
  - `--override-replan` → continue with the current plan despite the recommendation. Slice Progress unchanged; advance to the next slice.
  - No flag (or the invalid `--replan --override-replan`) → re-prompt with the three options. `--replan --override-replan` is invalid — fail with a clear error naming the conflict; halt.
  - Re-planning halts fire **regardless of `--skip-slice-checkpoints`** per REQ-014. (See EDGE-006 in `phases/implementation-per-slice.md`: plain `continue` with a pending re-planning halt → informative refusal, no work performed.)

- **`## Awaiting Re-start Decision` block latest in `progress.md`** (slice-start `--force` halted in autonomous mode per EDGE-013): resume requires explicit confirmation; `/sdd-flow continue --confirm-restart SLICE-XXX` proceeds with the destructive overwrite of the named already-`Complete` slice's row; otherwise re-prompt with the original options and halt.

- **`## Awaiting Site-Count Resolution` block latest in `progress.md`** (the 4e.5 final recount hit its cap or stalled): the user has resolved findings or amended the SPEC. Resume at 4e.5 step 1 with a **fresh** blind recount at the next unused `iter<k>` for `FEATURE` (one past the highest `## Site Diff FEATURE iter <k>` line), and a fresh 3-round cap. **Write no new `## Final Recount - Started`** — this halt block is the resumed run's boundary, and the count, diff, review, and fix rules below carry on from the markers written after it. Never resume from the halted iteration's review.

- **`## Awaiting Commit Approval` block latest in `progress.md`** (the 4h checkpoint was shown and has no "yes" yet — the session ended before an answer, or the answer was "no"): re-show the 4h checkpoint (`phases/implementation-whole-feature.md` → 4h) and act on the reply. Nothing is re-spawned and nothing is committed until the answer is yes.

- **`## PARTIAL: needs continuation` block latest in `progress.md`** (a subagent tripped its Safety-Net and the session ended before its successor was spawned): run the Mid-Phase Handoff (above) for the step the block names, from the compaction file it names — the blind site-count form when it names a blind count. This sits above every phase rule, so unfinished work is continued from its compaction and never mistaken for a finished step because its artifact already exists.

- **Any other `## Awaiting …` block latest in `progress.md`** (the catch-all — a halt this version has no rule for, such as one left by an older version): show the block to the user verbatim, say that there is no resume rule for it, and stop. Never guess what it was waiting for, and never route past it. When the user says how to proceed, append `## Halt Resolved - <the block's header text>` with their instruction on one line, so the block is no longer latest, and evaluate these rules again.

- **A `## Design Brief - APPROVED` line follows the latest `## ADR Candidates` entry, and no `## ADR Capture - Done` line follows that entry** (supervised mode: the brief was approved, and the flow stopped before the accepted decision records were written): run the capture now (`phases/planning.md` → 2.5b, ADR candidates) for every candidate not named in an `## ADR Candidate Dropped - ` line, append `## ADR Capture - Done (…)`, and evaluate these rules again — planning (3a) follows.

- If **`## Feature - Done`** → the feature is finished and only its rotation is owed (the rotation replaces this record with the `Finished:` line): run the feature-completion rotation (4j), then show the final summary.
- If **`## Implementation - Committed`** with no `## Feature - Done` → 4j: the task mirror, the announcement, `## Feature - Done`, the rotation.
- If **"Implementation Phase - COMPLETE"** with no `## Implementation - Committed` → the completion subagent finished (4f) and nothing has been committed. For a tiered spec, run the in-review task mirror if no `## Task Mirror - ` line follows the `COMPLETE` line (it is safe to repeat), then go to **4h** in supervised mode (it writes its halt block when it shows the checkpoint) or **4i** in autonomous mode. This line alone never means done. *Runs started on 3.5.0:* a run that had already committed has no `Committed` line and takes this rule too — the safe direction, since 4i finds nothing uncommitted, commits nothing, writes the marker, and 4j follows.
- If implementation is active → resume the appropriate sub-step (4a–4f or the per-slice cycle). The `BASE` for whole-feature 4a.5 and 4b, and for 4e.5 in both modes, is the `Base commit:` under `## Feature - Implementing`. When that line is absent and no Step 4 marker exists either (no `## Feature - Implemented`, no `## Slice … - ` line, no site or review marker), implementation has not started: write the line and begin 4a (per-slice: 4a.0). *Runs started on 3.5.0:* when the line is absent but Step 4 markers are present, implementation is under way and was never given the line — do **not** restart it, and do **not** record the current `HEAD`, which may already contain committed slices. Recover the base instead, without stopping to ask: per-slice, the `Base commit:` of the earliest `## Slice … - In Progress` entry; whole-feature, the planning commit (`git log -1 --format=%H -- <SPEC path>`). Append `## Feature - Implementing` with that commit and the words `recovered on resume`, name the commit in the next user-facing message, and resume by the sub-step rules below. If neither can be found, write `Base commit: unknown`: the feature-wide count is then given "whole repo" as its code range and the whole-feature review no `BASE` (both bodies accept that) — a wider range costs reading time, never correctness. **Blind-site-count sub-steps** are resolved from these literal lines, for the active scope (`SLICE-XXX` = the slice whose `## Slice SLICE-XXX - In Progress` is latest without a later `Retrospective Complete`; `FEATURE` otherwise), taking the highest iteration `N` present. **Only markers after the scope's anchor count** — the latest `## Slice SLICE-XXX - In Progress` for a slice, the latest `## Feature - Implemented` for whole-feature 4a.5, the latest `## Final Recount - Started` for 4e.5 — so a `--force` re-run never matches a discarded cycle's markers. (A 4e.5 resumed from `## Awaiting Site-Count Resolution` writes no new anchor; that rule, above, sets its boundary.) Evaluate in this order:
  - The latest `## PARTIAL: needs continuation` names a blind site count → Mid-Phase Handoff, **blind site-count handoff** (above). This precedes the fresh-count rule so a Safety-Net trip is continued from its compaction, not redone.
  - `## Site Count <SCOPE> iter <N> - BREACHED` is the latest count line → spawn a fresh counter for the same iteration.
  - `## Slice SLICE-XXX - Implemented` (per-slice 4a.5), `## Feature - Implemented` (whole-feature 4a.5), or `## Final Recount - Started` (4e.5, both modes) with **no** `## Site Count <SCOPE> iter <k> - Complete` of any `k` after it → the count was never run or was interrupted without a compaction: spawn a **fresh** blind count at the scope's first iteration (0, or 1 for whole-feature 4e.5), overwriting any partial `SITE-COUNT` file for it. A blind count is safe to redo from scratch; never hand the new counter the partial file.
  - `## Site Count <SCOPE> iter <N> - Complete` with no `## Site Diff <SCOPE> iter <N>` → run the diff script for iteration N (deterministic; no spawn).
  - `## Final Recount - Complete` after the latest `## Final Recount - Started` → 4e.5 is done; resume at 4f or later by the existing sub-step detection. None of the site rules apply.
  - `## Site Diff <SCOPE> iter <N>` with no `## Review <SCOPE> iter <N> - …` → spawn that review (per-slice 4b; whole-feature 4b at iter0; 4e.5 step 3), except a `MATCH` diff in 4e.5 that meets the skip condition of 4e.5 step 2 (no disposition-(ii)/(iii) row left unaccepted), which goes straight to 4f. A resumed session that cannot tell whether the condition holds spawns the review.
  - `## Review <SCOPE> iter <N> - REJECTED` with no `## Fix <SCOPE> iter <N+1> - Complete` → spawn the fix subagent for iteration N+1 (per-slice 4c / 4e.5 step 4 — never whole-feature 4c, see the exception below), unless the cap or stall rule is already met, in which case apply that step's halt.
  - `## Fix <SCOPE> iter <k> - Complete` with no `## Site Count <SCOPE> iter <k> - Complete` → spawn the fresh recount for iteration k.
  - **Whole-feature exception:** after `## Review FEATURE iter 0 - …`, resume 4c–4e by the existing sub-step detection (4c writes no `## Fix` marker); the rules above apply again once `## Final Recount - Started` is present.
  - Caps count the `## Fix <SCOPE> iter <k>` lines already present (for 4e.5, only those after the latest `## Awaiting Site-Count Resolution`), so a resumed run never resets a cap.
- If **"Planning Phase - COMPLETE"** with a later `## Planning - Accepted` line → start Step 4 (route on `delivery_mode:`). With no `Accepted` line and no `## Design Brief - ` line at all (a flow planned before the design gate existed) → also Step 4.
- If planning is active — including `Planning Phase - COMPLETE` with no later `## Planning - Accepted`, since the completion subagent writes `COMPLETE` in 3a, before the reviews → resume the appropriate sub-step (3a–3g). After a `### Panel Review Halt`, that is a fresh 3c panel run over the spec as the user left it. 3g is never skipped: its deviation check runs before `## Planning - Accepted` is written.
- If **`## Research - Accepted`** → Step 2.5 (`phases/planning.md`), by the **latest** `## Design Brief - ` line in `progress.md`: no such line → 2.5a (a brief file with no `Drafted` line is a partial write — the subagent overwrites it); latest is `Drafted` → 2.5b (show the gate); latest is `APPROVED` → start Step 3 (planning). Read the latest line, never "any": a re-plan writes a new `Drafted` line below an old `APPROVED` one. *Runs started on 3.5.0:* research had no marker then, so a flow with no `## Research - Accepted` line but with a `## Design Brief - ` line is treated as research accepted and takes this rule. (One with `Planning Phase - COMPLETE` was already caught by the planning rules above.) This sits beside the "planned before the design gate existed" rule and works the same way: an older run is read by what it did write.
- If research is active — a Step 0 record (in a run started before 3.5.1: any phase information) with none of the markers above → resume 2a–2e from what is on disk. The first that applies:
  - no mode recorded → Step 1; no CLARIFICATION file, no `## Clarification Skipped` block, and no `--skip-clarify` among the recorded flags → Step 1.5 (`phases/setup.md`);
  - no RESEARCH document → 2a;
  - RESEARCH document, but no "Research phase complete" note from the completion subagent → 2a's completion spawn;
  - no `CRITICAL-RESEARCH-*` review for this feature → 2b, then 2c. Skip 2b when an `## ADR Candidates` entry is already there; re-running it in AUTO mode is safe (the body declines a decision that already has a record);
  - the review has no "Findings Addressed" section → 2d;
  - otherwise → 2e: commit, then `## Research - Accepted`.
- If no phase info → nothing to resume. When the latest record is a `Finished:` line, tell the user that feature is done and show the line. Otherwise start from Step 0 (read `phases/setup.md`).

---

## Error Handling

If a subagent fails or returns incomplete results, the orchestrator:
1. Logs the failure in `progress.md`.
2. Re-spawns the subagent with additional context about what went wrong.
3. If the same subagent fails twice, stops and informs the user.

---

## Why the safety-net is count-based, not percentage-based

A spawned subagent has no first-class way to read its own context utilization — `/usage` is a harness slash command available only to the top-level interactive Claude, and the API returns token counts to the harness, not the model. Any self-audit a subagent performs produces output tokens that land back in its own context, partially eating the budget it is trying to measure. Count-based triggers (file Reads) are nearly free to evaluate (rule application, not deliberation), are inspectable in the counter file, and don't require the subagent to know anything its harness won't tell it. Because subagents do not spawn in this flow (a platform limit on Claude Code ≤2.1.171; a deliberate design rule from 2.1.172, which allows nesting to depth 5 — see `proposals/nested-subagents-analysis-2026-06-12.md`), there is no nested-subagent count — Reads is the whole signal. Defaults (Reads >15, or >20 for implementation chunks) are tunable without changing the protocol.
