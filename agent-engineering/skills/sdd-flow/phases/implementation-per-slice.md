# Phase: Implementation — per-slice mode

Reached at Step 4 when the spec's `delivery_mode:` is `per-slice`. The whole-feature 4a–4j steps DO NOT run; the orchestrator iterates `SLICE-XXX` entries from the spec's `## Delivery Slices` section, executing the per-slice cycle for each in order, then runs the end-of-feature cycle once after the last slice lands.

Per-slice subagents carry the Safety-Net Rule + a fresh counter file (`Reads: 0/20` for the implement step, `Reads: 0/15` otherwise) + the `implementation-compact.md` compact body path. Body paths are `SKILL_ROOT/bodies/<file>.md`, resolved absolute.

---

## Slice-boundary checkpoint axis (REQ-024)

A **separate axis** from the supervised/autonomous (phase-boundary) axis. Default `on` in per-slice mode in BOTH modes — without this default, opting into per-slice would degrade into "more internal gates with no human review," defeating the reason to opt in. Suppressed via `--skip-slice-checkpoints`.

| Phase-boundary | Slice-boundary | Behavior |
|---|---|---|
| supervised | on | Pauses at research-end + each completed slice + impl-end |
| supervised | off | Pauses at research-end + impl-end; slices run continuously inside |
| **autonomous** | **on** (default) | Research + planning autonomous; pause between each fully-completed slice; end-of-feature autonomous through commit |
| autonomous | off (via `--skip-slice-checkpoints`) | Fully autonomous start-to-finish |

---

## Per-slice 4a.0 — Scaffold the implementation tracker (once per feature)

Before the first slice, check whether `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[YYYY-MM-DD].md` already exists with a `## Slice Progress` table (it will, when resuming). If absent, spawn ONE **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/implementation.md` — its `per-slice` branch is **scaffold-only**: create the tracker with the `## Slice Progress` table populated from the spec's `## Delivery Slices` (all rows `Not Started`), then return without implementing anything.
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, `progress.md`.
- **Output:** the IMPLEMENTATION-PLAN tracker; append `progress.md`.

After a `--replan`, re-run this step with a post-replan note in the prompt — the orchestrator archives the old table under `## Archived Slice Progress (pre-replan)` first (see `phases/protocols.md`), and the subagent writes a FRESH table from the revised spec. Without this scaffold, `bodies/slice-start.md` halts per FAIL-007 (missing `## Slice Progress` table).

---

## Per-slice cycle (runs once per `SLICE-XXX`, in order)

### Per-slice 4a — Implement slice
Spawn ONE **`agent-engineering:sdd-workhorse`** subagent (strict — no bundling):
- **Body:** `bodies/slice-start.md` (for `SLICE-XXX`).
- **Inputs:** the active spec, the rolling ledger `SDD/implementation/slices/LEARNINGS-FEATURE-[feature-name].md`, and the IMPLEMENTATION-PLAN path. **The prompt receives ONLY the ledger** (per OQ-6 — individual retrospectives are out of the prompt path).
- **Task:** Implement the slice end-to-end. Bounded return: "Slice X delivered. Acceptance check `<test name>` passes."

### Per-slice 4b — Per-slice code review
Spawn an **`agent-engineering:sdd-workhorse`** subagent with `bodies/slice-review.md` for `SLICE-XXX`. **Mandatory per slice** — not deferred to end-of-feature. Writes `SDD/reviews/REVIEW-SLICE-*`.

### Per-slice 4c — Address per-slice findings
If the review found anything HIGH or MEDIUM, spawn an **`agent-engineering:sdd-workhorse`** fix subagent. Standard fix-and-re-review with the **per-slice iteration cap (REQ-012):** max 3 iterations with progress-stall check (HIGH must strictly decrease, OR MEDIUM when HIGH is zero) — mirrors Step 3c's panel cap exactly.

**On halt (cap exhausted or progress stall):**
- The slice does NOT proceed to 4c.5 or 4c.6.
- Append the unresolved findings to `LEARNINGS-FEATURE-[feature-name].md` under *Open recommendations awaiting user decision*.
- In any mode with slice-checkpoints `on`, surface the halt in the next pause message and do not advance to the next slice without user direction.
- In `autonomous + --skip-slice-checkpoints` mode, **halt the entire flow** — analogous to the panel-review halt, since compounding unresolved findings across subsequent slices is too high a risk.

### Per-slice 4c.5 — Slice retrospective (REQ-013)
Spawn an **`agent-engineering:sdd-workhorse`** subagent with `bodies/slice-retro.md` for `SLICE-XXX`. It writes `RETROSPECTIVE-SLICE-XXX-[feature-name]-YYYY-MM-DD.md` (audit trail; never modified after writing) and updates the rolling ledger in place.

**Two-stage matcher contract (resolves M-2; REQ-013 + REQ-014).** TWO surfaces — the retro-body header (in the retrospective ARTIFACT) and the halt block (in `progress.md`) — DIFFERENT strings, DIFFERENT times, DIFFERENT actors:
- **Retro-body header** (written by `bodies/slice-retro.md` into the retrospective artifact): `## Recommended SPEC Amendments` — required (content "None." when none); `## Recommended Re-planning` — optional (omit or "None." when no re-plan).
- **Progress.md halt block** (written by **THE ORCHESTRATOR**, never by the retro body): `## Awaiting Re-planning Decision` — written ONLY when the orchestrator's matcher detects `## Recommended Re-planning` in the just-written retro AND elects to halt.

**Stage 1 — Retro-stage match (right after the retro subagent returns, IN this cycle):** the orchestrator reads the just-written retrospective ARTIFACT (path from the subagent's return) and grep-matches the EXACT retro-body header strings:
- `^## Recommended SPEC Amendments$` → routine amendment recommendation; surface it in the slice-boundary pause as a per-recommendation summary (one or two lines per affected `SLICE-XXX`/`MODULE-XXX`/`REQ-XXX` — what should change, why), with the retrospective path for the user to read full wording. No halt block written.
- `^## Recommended Re-planning$` → elevated severity. Per **REQ-014**, presence of this header HALTS the flow even under `--skip-slice-checkpoints`. On match, the **orchestrator** writes this halt block to `SDD/orchestration/progress.md`:

```markdown
## Awaiting Re-planning Decision

SLICE-XXX retrospective recommends re-planning. Resume options:
- `/sdd-flow continue --replan` — re-run Step 3 (planning) with the rolling ledger and triggering retro in scope; resumes implementation from SLICE-001.
- `/sdd-flow continue --replan --from-slice SLICE-XXX` — same, but resume from a user-specified slice (must match `^SLICE-\d{3}$` AND reference an existing SLICE-XXX in the new plan's `## Slice Progress` per REQ-025).
- `/sdd-flow continue --override-replan` — continue with the current plan despite the recommendation. Documented but discouraged.

This halt fires even under `--skip-slice-checkpoints` (mirrors the Step 3c panel-review halt).

Triggering retrospective: <retro-path>
```

The pause message uses the re-planning-specific shape:
> **Re-planning recommended.** The slice retrospective has determined the original plan is no longer fit. The flow is halted to await your direction.
> Resume options:
>   1. `/sdd-flow continue --replan` — re-run Step 3 with the ledger + triggering retro; produces a revised SPEC; resumes implementation from `SLICE-001` (or a user-specified slice).
>   2. Edit the SPEC manually, then `/sdd-flow continue`.
>   3. `/sdd-flow continue --override-replan` — explicit override; continue on the current plan.
> See `<retro-path>` for the full rationale.

**In autonomous + --skip-slice-checkpoints mode this halt fires regardless** — compounding subagent runs on a known-broken plan is the higher-cost failure.

**Stage 2 — Resumption-stage match** (Phase Detection on `/sdd-flow continue` from a fresh session) reads `progress.md` for `## Awaiting Re-planning Decision` (the orchestrator-written block, NOT the retro-body header). See `phases/protocols.md` → Phase Detection Priority.

### Per-slice 4c.6 — Per-slice commit
The **orchestrator** runs the atomic per-slice commit (commit conventions in `commands/commit.md`) covering: slice code + tests + per-slice review doc + fix-findings notes + retrospective + ledger update. Message references `SLICE-XXX` and `SPEC-XXX`; **no co-author attribution**.

### PAUSE (slice-boundary)
Fires when slice-boundary checkpoints are `on`. The pause message includes: slice X completed + brief summary of what landed; acceptance-check status; any matched recommendations (SPEC amendments and/or re-planning) per the matcher; the next slice in queue. Resume via `/sdd-flow continue` (advances to next slice), or a re-planning resume option if re-planning was matched.

When checkpoints are `off` (`--skip-slice-checkpoints`), this pause is skipped — **except** the re-planning halt above, which fires regardless.

---

## End-of-feature cycle (runs once after the last slice's 4c.6 lands)

7. **End-of-feature 4d — Critical review across the assembled feature.** Spawn an `agent-engineering:sdd-critical-reviewer` subagent with `bodies/critical-review.md` (Implementation Phase section); reviews the whole assembled feature, not individual slices.
8. **End-of-feature 4e — Address critical review findings.** Standard `agent-engineering:sdd-workhorse` fix subagent.
9. **End-of-feature 4f — Implementation completion subagent.** `bodies/implementation-complete.md` — finalize plan, write IMPLEMENTATION-SUMMARY, capture glossary deltas. *(Shared step — see `implementation-whole-feature.md` §4f.)*
10. **End-of-feature 4g — Eval scaffolding.** Conditional on `eval_required:`. *(Shared — §4g.)*
11. **End-of-feature 4h — Supervised checkpoint.** Fires only in supervised phase-boundary mode. *(Shared — §4h.)*
12. **End-of-feature 4i — End-of-feature commit.** Covers: critical review doc, fix-findings code from 4e, completion artifacts from 4f, eval scaffolding from 4g. Per-slice code is already committed in each 4c.6.
13. **End-of-feature 4j — Announcement.** *(Shared — §4j.)* Surface eval scaffold result and any ADRs.

---

## EDGE-006 — plain `continue` while a re-planning recommendation is pending

If `/sdd-flow continue` is invoked **without a flag** while an `## Awaiting Re-planning Decision` block is the pending halt in `progress.md` (no resume-flag block following it), the orchestrator emits an informative refusal naming the three options (`--replan`, manual edit + plain `continue`, `--override-replan`) and exits. **No work is performed.** (Full resumption routing is in `phases/protocols.md`.)
