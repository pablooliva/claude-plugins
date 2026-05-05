# Vertical Slicing Decomposition for SDD

**Status:** Draft proposal — not yet implemented.
**Date:** 2026-05-05
**Affects:** `sdd/` plugin (planning + implementation commands), `agent-engineering/` plugin (`sdd-flow` skill).
**Author of intent:** Pablo Oliva. Drafted with Claude.

---

## Problem

Today, when SDD breaks a feature into tasks, work flows **horizontally by layer**: every sub-function of the feature is built out in the frontend, then every sub-function in the backend, then integration. The same pattern recurs across modules — finish all of module A's contribution, then move to module B. Each layer is completed in depth before the next one begins.

The intended shift is to **vertical slicing**: pick one concentrated function of the feature and drive it end-to-end through every relevant layer (frontend → backend → DB, or module A → module B → module C) before starting the next. Each slice is a thin, complete thread through the system that can be exercised and validated immediately.

### What "slice" means here

A slice is **a concentrated function with a thread line through every relevant layer of the application**. It is testable in a focused way, and exercising it surfaces the interaction and behavior of every layer it crosses.

A slice is **not** restricted to user-facing behavior. Examples of valid slices:
- A user-facing form submission that touches UI → API → DB → notification.
- An internal pipeline trigger that touches scheduler → worker → external API → state store.
- A webhook handler that touches receiver → validator → queue → handler → audit log.
- A batch job's primary path that touches scheduler → reader → transformer → writer.

The defining property is the **vertical thread**, not the audience.

### Why this matters

- **Faster feedback** — a working slice is testable after the first vertical pass, instead of waiting for all layers to converge.
- **Earlier risk surfacing** — integration problems show up on slice 1, not at the end.
- **Demoable progress** — partial completion is functional, not "frontend done, nothing works yet."

---

## Current State Findings

SDD already carries some of the structural raw material for slicing (`MODULE-XXX` entries with `Spec refs:` linking to REQs), but every command treats the **flat REQ list** as the unit of delivery and chunks work horizontally — by module, by layer, or by REQ index.

### `sdd/commands/planning-start.md` — produces SPEC

- Requirements are a flat numbered list (REQ-001 … REQ-N, EDGE-XXX, FAIL-XXX). No grouping by concentrated function or vertical thread.
- The `## Modules` section (SDD 1.2.0) is **inherently horizontal** — one module ≈ one layer/subsystem. Each module declares Interface / Hides / Risk / Spec refs.
- `Spec refs:` is a **many-to-many** link from modules to REQs. This is the raw material a vertical slice would need (REQ-005 = MODULE-001 + MODULE-002 + MODULE-003), but no command consumes it that way.
- There is **no `## Slices` section** and no concept of an ordered end-to-end path through the modules. The spec describes the surface area, not the delivery order.

### `sdd/commands/implementation-start.md` — produces PROMPT tracking doc

- Step 3 explicitly says: *"Start with core functionality (primary success path), Implement one requirement at a time."* That's per-REQ, not per-slice.
- The PROMPT tracker organizes work as "Completed Components / In Progress / Blocked" — by component (i.e., module), reinforcing horizontal layering.
- Test sections list Unit / Integration / E2E as separate buckets — encouraging "all unit tests, then all integration tests, then E2E," another horizontal pattern.

### `agent-engineering/skills/sdd-flow/SKILL.md` — orchestrates phase chunking

- Step 0 (scope assessment) decomposes *between* `/sdd-flow` invocations — splits "too large" features into multiple cycles. This is a vertical-style split at the **feature** level, but it never reaches inside a single feature.
- Step 4a's per-phase splitting rule: *"If REQ + EDGE + FAIL > 8, pre-split into ⌈total / 5⌉ sequential subagents, each handling a contiguous chunk."* Contiguous = whatever order REQs appear in the spec. **No awareness of which REQs share a vertical thread.** A subagent could end up implementing the frontend halves of REQ-001..REQ-005 while their backend halves wait for the next chunk.
- Code review (Step 4b) and critical review (Step 4d) run **once at end of implementation**, not per slice. Risk-tiered review depth is per-module, again horizontal.

---

## Proposed Changes

The leverage points cluster in three places.

### 1. `planning-start.md` — add `## Delivery Slices` section to the spec

Each slice entry contains:
- **ID** (ordered: SLICE-001, SLICE-002, …)
- **Concentrated function** — one-sentence description of the vertical thread this slice delivers.
- **REQs satisfied** — full or partial REQ-XXX references this slice fulfills (a slice may partially satisfy a REQ; later slices fill it in).
- **Modules touched** — the MODULE-XXX entries this slice cuts through.
- **Acceptance check** — a single, focused test that proves the slice works end-to-end. Ideally an automated test name; manual verification step otherwise.
- **Sequence rationale** — why this slice comes at this position. Slice 1 should be the thinnest possible end-to-end happy path; later slices add depth, edge cases, additional concentrated functions.

Slice 1's job is to prove the thread exists. Subsequent slices add capability and harden edges.

### 2. `implementation-start.md` — switch the unit of delivery to slices

- Replace *"implement one requirement at a time"* with *"implement one slice at a time, end-to-end through every module it touches, with its acceptance check passing before starting the next slice."*
- Implementation plan template gets a `## Slice Progress` tracker: each slice has a status (Not Started / In Progress / Acceptance Check Passing / Complete) plus a link to the passing acceptance check.
- Test guidance changes: each slice gets its own end-to-end acceptance test as the gate. Unit/integration/E2E tests for each layer are still expected, but they are scoped to the slice currently being delivered, not deferred to a horizontal "test phase."

### 3. `sdd-flow` SKILL.md — strict per-slice subagent chunking

- Step 4a's splitting heuristic changes from *"REQ count > 8 → contiguous chunks"* to **strict one subagent per slice**. No bundling. Even short slices get their own subagent.
  - Rationale for strictness: bundling slices reintroduces the horizontal habit (the bundled subagent will tend to interleave layers across slices). Strict isolation forces the "complete one slice before starting the next" discipline at the orchestrator level.
- Each slice subagent's bounded return must state: "Slice X delivered. Acceptance check `<test name>` passes." The orchestrator uses this signal to advance to the next slice.
- **Code review (Step 4b) becomes mandatory per slice** — not a single end-of-implementation pass. Each slice's code is reviewed as soon as the slice's acceptance check passes; findings are addressed before the next slice begins. This trades subagent cost for tighter feedback and prevents review backlog.
- Critical review (Step 4d) remains end-of-implementation (it's about the whole assembled feature, not individual slices).
- The full per-slice cycle (including retrospective and per-slice commit) and the end-of-feature cycle are detailed in §6. The summary above is the chunking principle; §6 is the full step list.

### 4. Spec critical review + panel review additions

Both review steps gain a new check:

> **Slice integrity:** Are the slices in `## Delivery Slices` genuinely thin vertical threads through the module set, or are they horizontal layers in disguise (e.g., "SLICE-001: build the frontend; SLICE-002: build the backend")? A slice that touches only one module (when the feature spans multiple) is a smell, unless explicitly justified.

Without this gate, the slice section becomes a checkbox.

### 5. Practicality check — when slicing isn't meaningful (per-slice mode only)

Some features genuinely don't decompose into vertical slices: pure batch jobs with one path, config-only changes, single-module bug fixes, schema migrations.

When a user has opted into per-slice mode (see Distribution Strategy below), the planning subagent must assess whether the feature actually decomposes meaningfully into slices. If it doesn't, the subagent must:

1. **Document why** in the spec (under `## Delivery Slices`, with a `Slicing not applicable: <reason>` note).
2. **Surface this to the user regardless of execution mode** — supervised *and* autonomous. The autonomous halt is similar in shape to the existing pre-research clarification gate at Step 1.5: the flow stops, writes an `## Awaiting Slicing Decision` block to `progress.md`, and emits a message asking the user to either:
   - **Fall back to `whole-feature`:** acknowledge the feature ships as a single horizontal pass; the flow resumes with the legacy REQ-based chunking.
   - **Reconsider:** the user may push back if they believe a slice exists the subagent missed, and have the subagent retry slice extraction.

This gate fires regardless of mode (supervised/autonomous) because the cost of getting slicing wrong — forcing artificial slices on a non-sliceable feature — is high enough to warrant a checkpoint, and the user has already paid the cost of opting into per-slice by setting the frontmatter field.

The gate does **not** fire in default `whole-feature` mode. Users who never opt into per-slice see no behavioral change.

### 6. Checkpoint cadence in per-slice mode

In `whole-feature` mode, sdd-flow's existing checkpoint behavior applies unchanged. In `per-slice` mode, two **orthogonal axes** govern when the flow pauses for human input:

1. **Phase-boundary checkpoints** (existing): `supervised` vs `autonomous` — controls pauses at research-end (Step 2f) and implementation-end (Step 4h).
2. **Slice-boundary checkpoints** (new): `on` vs `off` — controls pauses *between slices* during implementation, after each slice's full implement → review → fix → retrospective → commit cycle has completed.

These axes are independent. The cross product:

| Phase-boundary | Slice-boundary | Behavior |
|---|---|---|
| supervised | on | Pauses at research-end + each completed slice + impl-end (most checkpoints) |
| supervised | off | Pauses at research-end + impl-end; slices run continuously inside |
| **autonomous** | **on** | Research + planning autonomous; pause between each fully-completed slice; end-of-feature steps autonomous through commit |
| autonomous | off | Fully autonomous start-to-finish |

**Default when `delivery_mode: per-slice`:** slice-boundary checkpoints are **on** in both supervised and autonomous modes. Without this default, opting into per-slice would degrade into "more internal gates with no human review" — defeating the main reason to opt in.

**Escape hatch:** `--skip-slice-checkpoints` (mirrors the existing `--skip-clarify`) suppresses the per-slice pauses for users who want the per-slice implementation discipline (one subagent per slice, mandatory per-slice review, per-slice commits, retrospectives) but no human-in-the-loop between slices.

#### Per-slice cycle (runs once per `SLICE-XXX` entry)

- **4a** Implement slice — one subagent, strict, no bundling.
- **4b** Per-slice code review — mandatory, runs as soon as the slice's acceptance check passes.
- **4c** Address per-slice findings.
- **4c.5** Slice retrospective *(new — see below)*.
- **4c.6** **Per-slice commit** — slice code + tests + per-slice review doc + fix-findings notes + retrospective. Commit message references the `SLICE-XXX` ID and the `SPEC-XXX`. Each slice becomes an atomic, revertable unit aligned with its delivery boundary.
- **PAUSE** — fires when slice-boundary checkpoints are `on` (the default in per-slice mode); skipped under `--skip-slice-checkpoints`.

#### End-of-feature cycle (runs once after the last slice lands)

- **4d** Critical review across the assembled feature.
- **4e** Address critical review findings.
- **4f** Completion subagent — finalize implementation plan, write IMPLEMENTATION-SUMMARY.
- **4g** Eval scaffolding (conditional on `eval_required:`).
- **4h** Supervised end-of-implementation checkpoint (existing — fires only in supervised phase-boundary mode, regardless of slice-boundary setting).
- **4i** **End-of-feature commit** — covers the critical review doc, code changes from 4e, completion artifacts from 4f, and eval scaffolding from 4g. Per-slice code is already committed in each 4c.6; this commit is for whole-feature artifacts only.
- **4j** Announcement.

#### Per-slice review iteration cap (Steps 4b/4c)

The 4b → 4c → re-run-4b loop is bounded by **max 3 iterations** with a progress-stall check, mirroring Step 3c's panel-review cap. Each iteration must strictly decrease the HIGH finding count (or, when HIGH is already zero, the MEDIUM count); failure to do so halts the loop immediately.

**On halt** (cap exhausted or progress stall):

- The slice does NOT proceed to 4c.5 (retrospective) or 4c.6 (commit).
- The unresolved findings are appended to `LEARNINGS-FEATURE-XXX.md` under *Open recommendations awaiting user decision*.
- In any mode with slice-checkpoints `on`, surface the halt in the pause message and do not advance to the next slice without user direction.
- In autonomous + `--skip-slice-checkpoints`, halt the entire flow — analogous to the panel-review halt at 3c, since compounding unresolved findings across subsequent slices is too high a risk.

This protects against runaway cost, infinite loops on a buggy reviewer, and placating fixes that don't actually resolve findings.

#### Slice retrospective (Step 4c.5)

After 4c, a lightweight subagent reads the just-completed slice's implementation, tests, and per-slice review, and produces a `RETROSPECTIVE-SLICE-XXX-[YYYY-MM-DD].md` artifact under `SDD/prompts/`. The retrospective captures:

- **What was learned** about the integration, module shapes, data flow, and failure modes — anything that wasn't visible at planning time but became clear after implementing one full vertical thread.
- **Where the SPEC's assumptions diverged from reality in code.**
- **Recommended adjustments for upcoming slices**, including which `SLICE-XXX` entries are affected and how.
- **Spec-amendment recommendation** *(see below)*.

**Propagation:** Subsequent slice subagents (`SLICE-002+`) receive prior retrospectives in their prompts, so learnings from earlier slices inform later ones. This is the main reason vertical slicing has compounding value — each slice de-risks the next.

**Spec-amendment recommendation:** When the retrospective subagent determines the learnings are significant enough that upcoming slices would be substantially better with a SPEC update — e.g., a module's interface needs a field that wasn't anticipated, a slice as currently scoped is too large given what slice 1 just revealed, or a new edge case has emerged — it MUST include an explicit `## Recommended SPEC Amendments` section in the retrospective. Each recommendation cites:

- Which `SLICE-XXX` (or `MODULE-XXX`, `REQ-XXX`, `EDGE-XXX`, `FAIL-XXX`) entry is affected
- What the SPEC currently says
- What should change, and the proposed wording
- Why — grounded in concrete observations from the just-completed slice

This recommendation is **surfaced in the slice-boundary pause message** as a per-recommendation summary — one or two lines per affected entry (which `SLICE-XXX` / `MODULE-XXX` / `REQ-XXX`, what should change, why). The full proposed wording lives inside the retrospective artifact at the path printed in the pause message; the user opens the retro to see the exact diff before deciding. This balances ergonomics (the summary is enough to triage most recommendations) against the silent-amendment risk (the diff is one open-file away when the recommendation is non-trivial).

The retrospective subagent should be willing to recommend amendment whenever it sees a meaningful divergence — it is better to over-surface amendments and let the user decline than to silently propagate stale spec assumptions through five more slices.

**The retrospective subagent does NOT silently amend the SPEC.** The spec is the authoritative contract; modifying it mid-flow without the user's knowledge would erode the spec-as-source-of-truth principle. If the user agrees, they edit the SPEC during the pause; if they disagree, they ignore the recommendation and the flow continues with the original SPEC. The recommendation itself stays in the retrospective artifact regardless.

**Re-planning recommendation (elevated severity):** When the retrospective subagent determines the learnings indicate a fundamental plan-level failure — the original module decomposition is wrong, or an assumption underlying multiple upcoming slices has been falsified — it MUST emit a `## Recommended Re-planning` section in addition to (or instead of) `## Recommended SPEC Amendments`. This is a stronger signal:

- **Any mode with slice-checkpoints `on`:** the slice-boundary pause includes a re-planning–specific message that visibly distinguishes it from routine amendment recommendations.
- **Autonomous + `--skip-slice-checkpoints`:** the flow halts even though slice-checkpoints are off. Rationale: this is the autonomous equivalent of the panel-review halt at Step 3c — strong enough to override the no-pause discipline, because continuing risks burning subagent runs on a known-broken plan.
- **Resume options:**
  1. `/sdd-flow continue --replan` — re-runs Step 3 (planning) with the ledger and triggering retrospective in the planning subagent's prompt; produces a revised SPEC; resumes implementation from `SLICE-001` (or from a user-specified slice if some completed slices remain valid).
  2. Edit the SPEC manually, then `/sdd-flow continue` — user takes the wheel.
  3. `/sdd-flow continue --override-replan` — explicit override; continues with the current plan despite the recommendation.
- **Manual SDD users (no sdd-flow):** the recommendation surfaces in the retro and ledger; the user decides whether to re-run `/planning-start` themselves.

The retrospective subagent should reserve this signal for genuine plan-level failures, not routine learning. If everything is amendment-grade, the ledger and amendment recommendations are sufficient.

#### Rolling learnings ledger (Step 4c.5 propagation channel)

A naïve implementation passes every prior `RETROSPECTIVE-SLICE-XXX-...md` into each subsequent slice subagent's prompt. After 10 slices, slice 11's prompt carries 10 retros — token-heavy, redundant, and hard to extract signal from.

**Solution: a single rolling ledger that each retro updates in place.**

- New file: `SDD/implementation/slices/LEARNINGS-FEATURE-XXX.md` (one per feature; lifetime = duration of the implementation phase). See "Directory Layout" below for the path rationale.
- Each retro subagent has **two outputs**: its individual retrospective artifact (audit trail, never modified after writing) and an in-place update to the ledger (consolidates, refines, or supersedes prior entries — does not just append).
- Ledger sections (initial structure):
  - **Interface contract clarifications** — what the modules' public interfaces actually look like in practice vs. what the SPEC said.
  - **Integration patterns discovered** — how layers actually compose; surprises in data flow or call ordering.
  - **Performance / failure modes observed** — what broke or struggled; what to defend against in future slices.
  - **Open recommendations awaiting user decision** — spec-amendment (and re-planning) recommendations the user has not yet acted on. Especially relevant under `--skip-slice-checkpoints`, where there is no per-slice pause at which to act.
- **Subsequent slice subagents receive only the ledger** in their prompts, not the retro chain. Individual retros stay on disk for audit but are out of the prompt path.
- The ledger is structured-but-not-rigid: subagents may add sections if learnings don't fit the four above. The discipline is consolidation (a new entry on the same topic refines the existing one), not append-only growth.

**Resolves the `--skip-slice-checkpoints` amendment problem:** in that mode, *Open recommendations* accumulate across slices and are surfaced as a single consolidated block in the 4j announcement. The user reads one ledger, not N retros.

---

## Manual SDD Usage in Per-Slice Mode

`sdd-flow` orchestrates the per-slice cycle automatically, but the SDD plugin must also support per-slice development for users who run commands manually phase-by-phase.

### What stays the same

- `/research-start`, `/research-clarify`, `/research-complete` — unchanged.
- `/planning-start`, `/planning-complete` — modified only insofar as `/planning-start` produces the `## Delivery Slices` section and runs the practicality gate when `delivery_mode: per-slice` is set in the spec frontmatter (per §1, §5).
- `/code-review`, `/critical-review`, `/spec-review-panel` — unchanged.
- `/implementation-complete` — unchanged; still finalizes the whole feature once all slices are done.
- `/commit`, `/continue`, `/context-check`, `/adhoc-compact` — unchanged.

### What changes

`/implementation-start` becomes mode-aware. It reads `delivery_mode:` from the SPEC frontmatter:

- **`whole-feature` (default):** behaves exactly as today — produces a single implementation plan document, instructs the developer to implement the whole feature in one tracked pass.
- **`per-slice`:** scaffolds a per-slice-aware implementation plan document (with `## Slice Progress` table per §2), and instructs the developer to use the new `/slice-*` commands rather than implementing in one pass.

### New commands (per-slice mode only)

| Command | What it does |
|---|---|
| `/slice-start [SLICE-ID]` | Loads the slice's spec entry, reads the rolling ledger, sets implementation context, writes the slice's section in the implementation plan. The developer codes the slice. |
| `/slice-review [SLICE-ID]` | Thin wrapper over `/code-review`, scoped to the slice's files only. Produces a per-slice review doc under `SDD/reviews/`. |
| `/slice-retro [SLICE-ID]` | Produces `RETROSPECTIVE-SLICE-XXX-...md` and updates `LEARNINGS-FEATURE-XXX.md`. May emit `## Recommended SPEC Amendments` or `## Recommended Re-planning` per §6. |
| `/slice-commit [SLICE-ID]` | Atomic per-slice commit per §6's commit convention. |

The developer drives the cadence themselves — they can pause anywhere, batch slices, or skip the retro on trivial slices (their judgment). `sdd-flow` orchestrates these same commands automatically with the cadence rules from §6; manual users invoke them directly.

**Design principle:** the slice commands are the primitives. `sdd-flow` is orchestration over those primitives, not a parallel implementation of the same logic. This avoids duplication and ensures behavior stays consistent between manual and automated use.

When `delivery_mode: whole-feature` (or absent), the `/slice-*` commands return a friendly "this command requires `delivery_mode: per-slice`" message. They are present in the plugin but inert outside per-slice mode.

---

## Directory Layout

The current `SDD/prompts/` directory has accumulated multiple unrelated artifact families: the per-feature implementation plan tracking document, implementation summaries, context-management state (progress, subagent calls, counters), and compaction snapshots. Adding per-slice retrospectives and the rolling learnings ledger to this directory would compound the overload and obscure what's a planning artifact, what's an orchestration artifact, and what's a runtime context-management file.

This proposal restructures the layout. The change applies to **both** delivery modes — it's a one-time cleanup, not opt-in. Existing artifacts move; their content is preserved.

### Proposed layout

```
SDD/
├── UBIQUITOUS_LANGUAGE.md            # unchanged
├── adr/                              # unchanged
├── flow/                             # unchanged (DECOMPOSITION lives here)
├── research/                         # unchanged (RESEARCH, CLARIFICATION)
├── requirements/                     # unchanged (SPEC lives here)
├── reviews/                          # unchanged
├── implementation/                   # renamed from prompts/
│   ├── IMPLEMENTATION-PLAN-XXX-feature-YYYY-MM-DD.md  # per-feature implementation plan/tracker
│   ├── slices/                                    # per-slice mode only
│   │   ├── RETROSPECTIVE-SLICE-XXX-feature-YYYY-MM-DD.md
│   │   └── LEARNINGS-FEATURE-XXX.md
│   └── summaries/                                 # renamed from implementation-complete/
│       └── IMPLEMENTATION-SUMMARY-XXX-YYYY-MM-DD_HH-MM-SS.md
└── orchestration/                    # split out from prompts/context-management/
    ├── progress.md
    ├── subagent-calls/
    ├── counters/
    └── compacted/                                 # renamed; was loose files at the parent level
        ├── research-compacted-YYYY-MM-DD_HH-MM-SS.md
        ├── planning-compacted-YYYY-MM-DD_HH-MM-SS.md
        └── implementation-compacted-YYYY-MM-DD_HH-MM-SS.md
```

### Why these specific groupings

- **`implementation/`** holds artifacts about *what gets built* — the plan/tracker (`IMPLEMENTATION-PLAN`), the per-slice retrospectives and learnings ledger, the final summary. All planning-of-the-implementation, not orchestration.
- **`orchestration/`** holds runtime state of the flow itself — what subagent ran when, where compaction happened, how counters tracked. This is sdd-flow / context-management's working memory, not feature artifacts.
- **`slices/`** is a sub-grouping inside `implementation/` because per-slice retrospectives and the ledger are scoped to a single feature's implementation phase, not standalone artifacts.
- **`summaries/`** is renamed from `implementation-complete/` because the latter described *when* the artifact gets written rather than *what* it is.

### File rename: PROMPT → IMPLEMENTATION-PLAN

`PROMPT-XXX-feature.md` is, in the per-slice world, more accurately an *implementation plan* — it lists slices, tracks their progress, captures decisions. The "PROMPT" name is historical (the document that prompted the implementation work).

**Decision: rename to `IMPLEMENTATION-PLAN-XXX-feature-YYYY-MM-DD.md`** as part of the directory restructure. The rename ships in the same major-version bump and is handled by the same migration helper command in one pass.

This propagates to all references in the SDD plugin commands (`/implementation-start`, `/implementation-complete`, `/code-review`, `/critical-review` etc.), the `sdd-flow` skill's Artifact Paths Contract, and any documentation that names the artifact.

### Migration cost

This restructure is a one-time breaking change for SDD plugin users. Mitigations:

- Bump the SDD plugin to a major version (e.g., 2.0.0) to signal the break.
- Provide a one-shot migration helper (`/sdd-migrate-layout` or similar) that detects the old layout and moves files in place with `git mv`, preserving history.
- Document the move in the SDD plugin README's changelog.

### Why apply it to whole-feature mode too

Two reasons:

1. The existing layout is already messy (the `prompts/` overload predates per-slice work). The cleanup benefits all users.
2. Maintaining two divergent layouts (one per delivery mode) is exactly the maintenance burden we rejected by not forking the plugin. One layout, both modes — same logic.

This is the only forced disruption to whole-feature users in the entire proposal. Everything else is opt-in.

---

## Distribution Strategy

This change is **additive and opt-in**, not a fork.

**Why not fork the SDD plugin and sdd-flow skill into vertical-slicing variants?** The actual surface area of the change is small (a new optional spec section, one branch in implementation chunking, one branch in sdd-flow Step 4a, the practicality gate). Forking would duplicate the entire SDD plugin (18 commands) and the ~700-line sdd-flow skill, most of which is unaffected. Within months, the two would drift on every unrelated bug fix or improvement.

**Mechanism: `delivery_mode:` frontmatter field on the spec.**

- **Default value:** `whole-feature`. With this default, all existing behavior is preserved bit-for-bit. Existing users see zero change to anything they currently produce.
- **Opt-in value:** `per-slice`. A user must explicitly set this field on a spec's frontmatter to invoke the new behavior. Editing a spec without changing this field changes nothing — the default carries through.
- The `## Delivery Slices` section is **required only** when `delivery_mode: per-slice`. In `whole-feature` mode it is omitted entirely.
- `sdd-flow` reads the field at the planning → implementation boundary. In `whole-feature` mode it routes to the existing REQ-based chunking; in `per-slice` mode it routes to the new strict one-subagent-per-slice + mandatory per-slice code review path.
- The practicality gate (§5) fires only when `per-slice` is requested.
- Spec critical review and panel review (§4) apply the slice-integrity check only when the spec declares `per-slice`.

**Migration path for existing users who want to try it:** add `delivery_mode: per-slice` to the frontmatter of a *new* spec, fill in the `## Delivery Slices` section, run `/sdd-flow` as usual. No tooling reinstall, no plugin fork, no version pin to manage.

The only case that would justify a fork is incompatibility — e.g., shared artifacts that can't coexist between modes. The proposed changes are all additive (new spec section, new chunking branch, new gate), so the incompatibility risk is low. If incompatibilities surface during Step A or Step C implementation, revisit this decision then.

### Reconsidering the fork question (revision after full scope)

The original fork rejection above was made before the full set of per-slice changes was scoped. As of this revision, per-slice mode introduces:

- New spec section (`## Delivery Slices`) and practicality gate at planning
- Modified `/implementation-start` behavior (mode-aware branching)
- Four new commands (`/slice-start`, `/slice-review`, `/slice-retro`, `/slice-commit`)
- New artifacts (per-slice retrospectives, rolling learnings ledger)
- New checkpoint axis (slice-boundary checkpoints) with its own escape-hatch flag
- Modified `sdd-flow` Step 4 with two distinct state machines
- Re-planning trigger with elevated severity behavior
- Directory restructure (forced on both modes)
- README/diagram divergence — per-slice mode has a meaningfully different implementation-phase shape (fan-out into slices, per-slice cycle, end-of-feature merge)

The accumulated surface area is larger than initially estimated. Worth reconsidering: should this still ship as opt-in inside the existing plugin, or as a separate plugin?

**Decision (revised, but still merged): keep the code merged. Fork the documentation, not the plugin.** Specifically:

- **Code:** stays in `sdd/` and `agent-engineering/sdd-flow/`. The `delivery_mode:` frontmatter remains the runtime branch. Slice commands ship as part of the SDD plugin and are inert (display a friendly "requires `delivery_mode: per-slice`" message) when invoked outside per-slice mode.
- **Documentation:** the SDD plugin README gets two clearly-distinct sections — *Whole-feature workflow* (existing 3-phase diagram, unchanged) and *Per-slice workflow* (its own diagram showing the implementation-phase fan-out into slices, the per-slice cycle, and the end-of-feature merge). Each section stands alone; users pick the one matching their `delivery_mode`. The diagrams do not attempt to combine into a single flowchart — that's the source of the confusion the user flagged.
- **First-time-user routing:** the README opens with a one-paragraph "which mode is right for you?" decision aid. Most features → whole-feature. Multi-layer features where you want vertical thread feedback → per-slice.

**Why not fork the plugin even given this larger surface area:**

- Research, planning, all reviews, ADR capture, eval scaffolding, completion, hooks — 80%+ of the plugin's commands and infrastructure — are genuinely shared. Forking duplicates them and forces every future bug fix or improvement to be ported.
- A companion plugin (`sdd-slices` depending on `sdd`, adding only slice commands) is a viable alternative. It avoids most duplication, but it forces users to install two plugins to use one workflow, and the modified `/implementation-start` behavior is hard to express as a pure additive command — the existing command must read `delivery_mode` and branch.
- The README/diagram confusion the user flagged is a documentation problem, not a code problem. Two clearly-labeled documentation tracks resolve it without paying the fork tax.

**Reopen the fork question if:**

- During Step A or Step C implementation, research/planning subagent prompts turn out to need significantly different instructions in per-slice mode beyond just the Slices section (which would imply real divergence in research/planning, not just implementation).
- Per-slice mode evolves to own research/planning differently (e.g., per-slice planning, per-slice research). Currently not proposed; if proposed later, the fork question reopens.

---

## Tradeoffs

**For:**
- Each slice is testable on completion → fast feedback.
- Integration risk surfaces on slice 1, not slice N.
- Demoable progress mid-feature.
- Easier to pause/pivot mid-feature without partial-layer mess.

**Against:**
- **Scaffolding tax:** Slice 1 forces thin versions of every module on the path. If the deep-module principle is taken seriously, this is fine (you're proving the interfaces); if not, you risk re-architecting later slices.
- **Slice identification cost:** Someone (planning subagent, plus reviewers) has to extract slices from REQs+modules. The Spec refs many-to-many gives the data, but ordering and "thinnest happy path" selection is judgment.
- **Subagent cost:** Strict one-subagent-per-slice + mandatory per-slice code review + per-slice retrospective multiplies the number of subagent invocations per feature. Each slice now spawns at least three subagents (implement, review, retrospective) plus a fix-findings subagent if needed. This is the explicit cost paid for the discipline.
- **Commit granularity:** Per-slice commits create more granular git history. On teams that value tight, atomic commits this is a benefit; on teams that prefer feature-sized commits this is noise. Squash-merge conventions can absorb the difference at the PR boundary.
- **Pause fatigue:** In supervised + slice-boundary-on mode, a 5-slice feature produces ~7 pauses (research-end, 5 slices, impl-end). The `--skip-slice-checkpoints` escape hatch addresses this, but users have to know to use it.
- **Directory restructure migration:** The `prompts/` → `implementation/` + `orchestration/` split is a one-time breaking change for all SDD users (including whole-feature users). Mitigated by the migration helper command and a major-version bump, but it forces a coordinated upgrade.
- **Documentation maintenance:** Two distinct README workflow sections (whole-feature, per-slice) must be kept in sync. Bug fixes that affect both mention require parallel updates in both sections.
- **CLI surface area for whole-feature users:** The `/slice-*` commands ship to all SDD users but are inert outside per-slice mode. Small cognitive cost (more commands in autocomplete) for users who never opt in.
- **Not all features slice:** addressed by the practicality check (§5), but the check itself adds friction.

---

## Suggested Implementation Order

Do **not** implement yet. When ready:

**Step A (first):** Spec template change only — add `## Delivery Slices` to `planning-start.md`. Leave implementation and sdd-flow alone. Lowest blast radius. Use it manually on one or two specs to validate the slice-artifact shape before changing the orchestrator.

**Step C (then):** Run an `/sdd-flow` cycle on the rest of this proposal (per-slice implementation behavior, strict per-slice subagents in sdd-flow, mandatory per-slice code review, slice-integrity review checks, practicality gate). The full change is itself a feature with multiple modules and natural slices; this is a good dogfood opportunity.

(Step B from the original analysis — "everything in one go" — is dropped. Step A → Step C is the chosen path.)

---

## Open Questions (deferred)

- What does the practicality-check gate's user-facing message look like, exactly? (Mirror the Step 1.5 clarification gate, but the trigger is different.)
- Does Step 0 (scope assessment) need any change, or does feature-level decomposition stay independent of slice-level decomposition?
- When `delivery_mode:` is absent from a spec's frontmatter (e.g., specs written before this change ships), the loader treats it as `whole-feature`. Should sdd-flow log a one-line note when applying this default, or stay silent?
- Should the slice retrospective's individual artifact have a structured template (specific named fields), or be free-form prose? The rolling ledger has structured sections (§6); the question is whether the retros themselves should mirror that structure or stay free-form. Possibly: structured for the recommendation sections, free-form for the learning narrative.
- Should `/slice-review` be a thin wrapper over `/code-review` or a distinct command? Wrapper minimizes duplication; distinct allows slice-specific review behavior to evolve independently (e.g., focusing on cross-layer integration over single-module correctness).
- Should slice subagent prompts include the prior individual retros in addition to the rolling ledger, or strictly the ledger only? Strict is cleaner; including retros gives the next subagent richer context but reintroduces the propagation cost the ledger was designed to avoid.

### Resolved during proposal iteration

- ~~Should the spec frontmatter expose a `delivery_mode:` field at all?~~ Yes — it's the runtime branch that gates per-slice behavior; default `whole-feature` preserves existing behavior.
- ~~If a retrospective recommends amendment but the user is in `--skip-slice-checkpoints` mode, where do recommendations land?~~ Resolved by the rolling ledger's *Open recommendations* section + consolidated surfacing in the 4j announcement.
- ~~Should a retrospective ever be allowed to recommend re-planning?~~ Yes — via the elevated-severity `## Recommended Re-planning` mechanism in §6, which halts the flow even under `--skip-slice-checkpoints`.
- ~~Does the per-slice code review's findings-fix loop have a cap?~~ Yes — mirror Step 3c's panel-review cap: max 3 iterations with a progress-stall check (HIGH must strictly decrease, or MEDIUM when HIGH is zero). Halt routes findings to the user via the ledger; in `--skip-slice-checkpoints` mode, halt the whole flow. Codified in §6 as "Per-slice review iteration cap."
- ~~How should the spec-amendment recommendation be presented in the slice-boundary pause message?~~ Per-recommendation summary in the pause message (one or two lines per affected entry); full proposed wording in the retrospective artifact, accessible via the path printed in the pause message. Codified in §6.
- ~~Keep the `PROMPT-XXX` filename or rename to `IMPLEMENTATION-PLAN-XXX`?~~ Rename. Ships in the same major-version bump as the directory restructure; the migration helper handles both. Codified in the Directory Layout section.

These are intentionally left open — they should be resolved when Step C is actually planned, not now.
