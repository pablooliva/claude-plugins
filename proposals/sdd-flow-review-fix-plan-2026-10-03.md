# sdd-flow Review — Fix Plan

**Status:** Done — shipped as 3.5.1. Batch 1 `58b559b`, Batch 2 `d1b85e8`, Batch 3 `2e7c0fb`, then the wrap-up commit. Two further calls made during Batch 3 and confirmed by Pablo: the re-start of a finished slice was removed (M9), and the slice-boundary pause writes no halt block. L4, listed below as out of scope, was fixed in the wrap-up at Pablo's request. All five decisions were made on 2026-10-03 (see Decisions).
**Date:** 2026-10-03
**Affects:** `agent-engineering/` plugin, `sdd-flow` skill (currently 3.5.0).
**Findings:** `proposals/sdd-flow-review-findings-2026-10-03.md` — finding IDs (K1, H3, M7 …) refer to that file.
**Author of intent:** Pablo Oliva. Drafted with Claude.

---

## Goal

Close the findings from the 2026-10-03 review without changing what the flow does on its main path. Three batches, one per root cause, each reviewed by Codex before the next starts.

## Ground rules

- **The `sdd` plugin is not touched.** It is frozen at 2.2.0; every change is inside `agent-engineering/`.
- **Flat orchestration stays.** No fix introduces nested subagents (`proposals/nested-subagents-analysis-2026-06-12.md`).
- **One batch = one commit**, preceded by `codex review --uncommitted` and a scoped re-check of the finding IDs the batch claims to close. A batch does not land with an open HIGH from that review.
- **No untraced findings remain.** M10, M11, M12, and L4 came from Codex untraced and were checked on 2026-10-03: M10, M11, and L4 hold; M12 holds for the code review and was struck for the spec critical review.
- **The diagram follows the stops.** `docs/sdd-flow-diagram.md` is updated in the same batch that adds, removes, or renames a stop.
- **Scripts are not expected to change.** Run `python3 -m unittest discover -s scripts/tests` in each batch anyway.

## Three rules the fixes establish

Each batch enforces one rule. Stating them in `SKILL.md` is part of the work, so later edits have something to be checked against.

| Rule | Statement | Fixes root cause |
|---|---|---|
| A | **The prompt's paths are the only inputs.** A body never lists a directory to find or choose its spec, research document, or plan; never commits; never resets `progress.md`. A body that cannot proceed returns a failure to the orchestrator and writes no stop note. | R1 |
| B | **Only the orchestrator declares a phase done, and only after the phase's last step.** Each phase gets an orchestrator-written marker, as planning already has. Resume rules read markers only after the current feature's Step 0 record. Every stop has a halt block, a resume rule, and a row in the diagram. | R2 |
| C | **Every slice state change, stop, and commit has a named owner in the phase chapter.** Bodies describe what they do; they do not describe what "the orchestrator may" do. | R3 |

---

## Batch 1 — Bodies stop acting standalone (Rule A)

Closes: H2, H3, H5, H11 (the reset half), M1 (body side), M8, K5, L2, L3.

| Change | Files | Closes |
|---|---|---|
| Replace every "locate the active SPEC / research / plan" listing with "use the path in your prompt; if it is missing or unreadable, return a failure". Remove the multiple-match halts. | `bodies/slice-start.md`, `slice-review.md`, `slice-retro.md`, `implementation.md`, `planning.md`, `critical-review.md` | H2, M1 |
| Implementation body: an existing plan for the same spec is the normal case for chunk 2 onward and for a re-scaffold. Continue with it; halt only when the prompt names no plan path and one exists for a different feature name. | `bodies/implementation.md` | H3 |
| Remove "Commit Your Code Changes" from the implementation compaction body. State that the working tree is left uncommitted and why (the base commit must not move). | `bodies/implementation-compact.md` | H5 |
| Research body: delete the reset and the archive question. It appends like every other body. | `bodies/research.md` | H11 (reset), M1 |
| Research body: remove its own "prompt is fuzzy" clarification halt. The Step 1.5 gate owns that decision; a body does not reopen an opt-out. | `bodies/research.md` | M1 |
| Code-review body: in `MODE: site-verification-only`, the artifact pre-check is skipped; in normal mode a missing artifact is a returned failure, not a stop note. Drop the "<40% context" checks and the rejection criterion built on them. | `bodies/code-review.md` | K5, M1, L2 |
| Planning body: "research incomplete" becomes a returned failure. | `bodies/planning.md` | M1 |
| Continuation body: read only the compaction file named in the prompt; write new ones under `SDD/orchestration/compacted/`; make its bail-out section defer to the compact body it was given. | `bodies/continue.md` | M8 |
| Completion body: cut the `progress.md` entry to the 10-line cap; drop "<40%" line. Renumber `panel-specialist.md` sections in order. | `bodies/implementation-complete.md`, `bodies/panel-specialist.md` | L2, L3 |
| State Rule A in the skill and list the stop notes a body is allowed to write (after this batch: the practicality gate's `## Awaiting Slicing Decision` and the two `## PARTIAL` forms — nothing else). | `SKILL.md` | — |

**Batch check (mechanical):**
- `grep -rn "ls SDD/requirements/SPEC-\*\|ls SDD/research/RESEARCH-\*" bodies/` returns nothing.
- `grep -rhn "## Awaiting " bodies/` returns only headers on the allow-list.
- `grep -rni "commit" bodies/*-compact.md` returns nothing that instructs a commit.

---

## Batch 2 — Resume markers and handoff contracts (Rule B)

Closes: H1, H11 (the marker half), M2, M1 (orchestrator side), K1, K2, K3, K4, H4, M5, M6, M7, M10, M12, M13, M14, M15.

| Change | Files | Closes |
|---|---|---|
| Add `## Research - Accepted` (orchestrator, after the 2e commit). Resume: no such line → research is active, resume 2a–2e from the artifacts present; line present → Step 2.5. Drop the literal `Research Phase - COMPLETE` rule. | `phases/research.md`, `phases/protocols.md` | H11 |
| Add `## Implementation - Committed` (orchestrator, after 4i) and `## Feature - Done` (after 4j). Resume: `Implementation Phase - COMPLETE` with no `Committed` → go to 4h (supervised) or 4i; `Committed` with no `Done` → 4j. Define a "no" at 4h: write `## Awaiting Commit Approval` and stop. | `phases/implementation-whole-feature.md`, `phases/implementation-per-slice.md`, `phases/protocols.md` | H1 |
| **Runs started on 3.5.0 keep resuming.** A flow with no `## Research - Accepted` line but a later `## Design Brief - ` line or `Planning Phase - COMPLETE` is treated as research accepted. `Implementation Phase - COMPLETE` with no `Committed` line goes to 4h/4i under the new rule, which is the safe direction for an old run: 4i commits whatever is uncommitted (nothing, if the old run already committed) and 4j follows. State both next to the existing "planned before the design gate existed" rule. | `phases/protocols.md` | H1, H11 |
| Scope every phase rule to the lines after the latest Step 0 record. Rotation summaries for finished features use a form the phase rules cannot match. | `phases/protocols.md`, `SKILL.md` (Progress Hygiene) | M2 |
| Add a catch-all as the last halt rule: any other `## Awaiting …` block that is latest → show it to the user verbatim and stop; never guess. | `phases/protocols.md` | M1 |
| Record `Base commit:` on a `## Feature - Implementing` line written before 4a; 4a.5, 4b, and 4e.5 read it from there. | `phases/implementation-whole-feature.md`, `phases/protocols.md` | M15 |
| ADR confirmation (D2 = a): confirm mode is removed. In supervised mode the 2b subagent runs in a new **PROPOSE** mode: it writes no ADR and no stop note, and appends one `## ADR Candidates` entry to `progress.md` (title and chosen option per candidate, within the 10-line cap — never the rendered record). The design gate (2.5b) lists them on an `ADR candidates:` line; `approve` accepts them, and a reply may drop any by title. On approval the orchestrator spawns the capture subagent in AUTO mode for the accepted candidates before 3a, then appends `## ADR Capture - Done (<numbers \| none>)`; they are committed at 3f. Autonomous mode is unchanged (AUTO at 2b; the gate shows what was written). Resume: `## Design Brief - APPROVED` after an `## ADR Candidates` entry with no later `## ADR Capture - Done` → run the capture before 3a. `## Awaiting ADR Confirmation` no longer exists. | `phases/research.md`, `phases/planning.md`, `bodies/adr-capture.md`, `phases/protocols.md`, `docs/sdd-flow-diagram.md` | K1 |
| Blind-count handoff passes the same allow-list as a fresh count (conventions path, `ALSO INVENTORY` IDs, `Modules touched`); the compaction template records them under Assignment. | `phases/protocols.md`, `bodies/site-count-compact.md` | K2 |
| Pass `SCOPE` and `ITER` explicitly in the per-slice 4b brief and the 4e.5 verification brief. Pass the spec to 4e.5 verification. | `phases/implementation-per-slice.md`, `phases/implementation-whole-feature.md` | K3, K5 |
| Agent-security: the spawn passes the resolved value (`agent_security: true \| auto`). Body §4.8 and the agent file run the scope gate only under `auto`. A missing catalog closes the gate even when the value is `true`, with the existing warning. | `phases/planning.md`, `bodies/panel-specialist.md`, `agents/sdd-spec-agent-security-specialist.md`, `SKILL.md` | K4, M13 |
| Missing panel reviewers (D1 = a): 3c names which panel values have a shipped specialist agent (`security`, `agent-security`, `performance`, `data-modeling`, `api-contract`, `module-depth`, `reliability`, `slice-integrity`). Any other allowed value — today `accessibility`, `privacy`, `cost` — is spawned as `agent-engineering:sdd-workhorse` with `bodies/panel-specialist.md` and the panel value; the body's Optional Specialists section already defines them. No new agent files. Check: every panel value `bodies/planning.md` tells the author to add resolves to an agent that exists. | `phases/planning.md`, `bodies/panel-specialist.md`, `SKILL.md` (Model Routing) | H4 |
| Panel synthesis: 1–2 unrelated MEDIUM → `PROCEED` (they go to the 3e fix). Loop: a `PROCEED` at iteration 3 exits; the cap halts only on a non-passing verdict. | `bodies/panel-synthesis.md`, `phases/planning.md` | M5 |
| 4e.5: on `MATCH`, skip verification only if no (ii)/(iii) row was added or changed since the last accepting review; otherwise run it. | `phases/implementation-whole-feature.md` | M6 |
| 4c and 4e briefs list the standard, the conventions file, and the inventory; 4e gets the same site duties as 4c. | `phases/implementation-whole-feature.md` | M7 |
| 3b ADR spawns run sequentially. | `phases/planning.md` | M14 |
| Final-recount resume: state that resuming from `## Awaiting Site-Count Resolution` writes **no** new `## Final Recount - Started` — the halt block is the resumed run's boundary. Reword the "count never ran" rule to "no `## Site Count FEATURE iter <k> - Complete` of any `k` after the anchor", and drop "a resumed 4e.5" from the anchor sentence. | `phases/protocols.md`, `phases/implementation-whole-feature.md` | M10 |
| Pass the panel review (`PANEL-SPEC-*`) to the 4b code review and the per-slice review whenever the agent-security lens can run, and have both bodies read its `AI Agent Security Findings` and `Abuse cases to cover` blocks. | `phases/implementation-whole-feature.md`, `phases/implementation-per-slice.md`, `bodies/code-review.md`, `bodies/slice-review.md` | M12 |

**Not changed here:** the single-pass fixes at 2d, 3e, 4c, and 4e stay single-pass (M7, second half). Adding a re-review to each would add four Opus or Sonnet spawns per feature; the finding is recorded, and the trade is left as it is unless decided otherwise.

**Batch check (trace table):** write, in the commit message or the PR body, one row per stop — who writes the halt block, the exact header, the resume rule that matches it, and the diagram row. A stop with an empty cell is not done.

---

## Batch 3 — The slice path (Rule C)

Closes: H6, H7, H8, H9, H10, H12, M3, M4, M9, M11.

| Change | Files | Closes |
|---|---|---|
| The orchestrator sets the slice row to `Complete` as the last edit before the 4c.6 commit, so the commit includes it. Bodies stop describing what "the orchestrator may" do. | `phases/implementation-per-slice.md`, `bodies/slice-start.md`, `bodies/slice-retro.md` | H10 |
| Slice fix-loop halt writes `## Awaiting Slice Resolution` (slice ID, unresolved counts, review path). Resume: a fresh review at the next unused iteration with a fresh three-round cap, mirroring `## Awaiting Site-Count Resolution`. The orchestrator hands the ledger append to the retrospective-shaped workhorse rather than writing it itself. | `phases/implementation-per-slice.md`, `phases/protocols.md`, `docs/sdd-flow-diagram.md` | H9 |
| Re-plan and forced re-start: the orchestrator moves the superseded slice's retrospective and review to `…/slices/superseded/` (kept, not deleted) before the new cycle; the retrospective body's "already exists" refusal then holds only for a true double run. | `phases/protocols.md`, `phases/implementation-per-slice.md`, `bodies/slice-retro.md` | H7 |
| `--override-replan` runs 4c.6 for the triggering slice first, then advances. `--replan` commits the triggering slice as-is, with a message saying it preceded a re-plan. | `phases/protocols.md`, `phases/implementation-per-slice.md` | H8 |
| Slicing fallback (D4 = a): `--fall-back-to-whole-feature` flips `delivery_mode:` to `whole-feature`, then resumes planning at 3a's completion step (`bodies/planning-complete.md`) and runs 3b–3g as usual. It never routes to Step 4 directly. `--retry-slicing` likewise returns to 3a, not past it. Split the reused header: `## Awaiting Slicing Decision` is the practicality gate only. | `phases/protocols.md`, `phases/planning.md`, `bodies/planning.md` | H6 |
| Re-plan pause message lists only options the resume rule accepts. | `phases/implementation-per-slice.md` | M3 |
| LOW findings in slice reviews (D3 = a): the 4c fix step runs when the review found **anything** — HIGH, MEDIUM, or LOW — and resolves all of it. The review marker gains an optional `, <l> LOW` suffix (absent reads as 0, as the row-only bracket already does) so the orchestrator can tell without opening the review. LOW never counts toward the stall check; the three-round cap is unchanged. Cost, accepted: a slice with only LOW findings now takes one round (fix → blind recount → diff → re-review) it did not take before. | `phases/implementation-per-slice.md`, `bodies/slice-review.md`, `phases/protocols.md` | M4 |
| Completion in slice mode: the per-requirement checklist is satisfied from the slice table (every slice `Complete`) and the slices' `REQs satisfied` mapping; the completion body fills the requirement rows itself. | `bodies/implementation-complete.md` | H12 |
| Re-start of a finished slice: either wire it (when the orchestrator passes `--force`, when it writes the halt, and `--confirm-restart` in the arguments table) or remove the resume rule and the flag. Recommended: remove — no user-facing way to ask for it exists today. | `phases/protocols.md`, `bodies/slice-start.md`, `SKILL.md` | M9 |
| The orchestrator writes `## Slice SLICE-XXX - Retro Matched (<none \| amendments \| re-planning \| malformed>)` after the Stage 1 matcher, whatever the result. Resume: `Retrospective Complete` with no later `Retro Matched` for that slice → run the matcher from the retrospective file before anything else. | `phases/implementation-per-slice.md`, `phases/protocols.md` | M11 |

**Batch check:** walk one slice on paper through each of its five exits — approved, fix-loop halt, re-plan with `--replan`, re-plan with `--override-replan`, interrupted mid-cycle — and confirm each ends in a commit or a halt block with a resume rule.

---

## Wrap-up (after batch 3)

- Update `docs/sdd-flow-diagram.md` stops table (L1) to match the trace table from batch 2.
- Remove or re-point the `/sdd-migrate-layout` message: the command ships only in the `sdd` plugin (L2).
- Update the repo `CLAUDE.md` and `agent-engineering/README.md` where they name steps or markers that changed.
- Bump the version to **3.5.1** in **both** `agent-engineering/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` (D5 = a) — once, here; batches 1–3 land under 3.5.0 as earlier fix commits did.
- Mark the findings file `Status: Fixed in <version>` with any struck findings listed.

---

## Decisions

All five were recommended by Claude and decided by Pablo.

### Decided

| ID | Decision | Answer | Decided |
|---|---|---|---|
| D1 | What happens when a spec asks for an `accessibility`, `privacy`, or `cost` reviewer? | **(a)** Route those values to the general worker agent using the inline definitions already in `panel-specialist.md`. No new agents. | 2026-10-03 |
| D2 | How are research-stage ADRs confirmed in supervised mode? | **(a)** Drop confirm mode: candidates are listed at the design gate and written on approval. No extra stop. | 2026-10-03 |
| D3 | Do slice reviews fix LOW findings? | **(a)** Yes, in the same fix pass, without counting toward the stall check. A slice with only LOW findings takes one extra round. | 2026-10-03 |
| D4 | Where does `--fall-back-to-whole-feature` resume? | **(a)** Flip the mode and resume at 3a's completion step, so the panel, critical review, and deviation check run on the spec. | 2026-10-03 |
| D5 | Version number. | **(a)** 3.5.1 once, at wrap-up. | 2026-10-03 |

Options not taken: D1 — ship three new specialist agents; D2 — a separate confirm stop after 2b; D3 — defer LOW findings to end-of-feature; D4 — keep the jump to implementation; D5 — 3.6.0.

## Out of scope

- Adding a second review pass after the single-pass fixes (M7, second half).
- `/adhoc-compact` ↔ `/continue` mismatches (L4: folder, section names, no generic branch) — verified, but outside `sdd-flow`; fix separately. The folder half is the same one-line change as M8 and could ride along with batch 1 if wanted.
- Any change to the `sdd` or `pace` plugins.
