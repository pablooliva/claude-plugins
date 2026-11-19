# BRIEF-002-spec-reading-by-section

Date: 2026-11-19. Status: approved 2026-11-19.

## What you will be able to do afterwards
- Run a per-slice cycle on a large spec without the implementer's Read of it failing: it reads the sections it always needs, then its slice, modules and ids, each by heading or id with offset/limit — never the whole file at once.
- The same for whole-feature mode: a chunk reads the always-read sections and its own ids; an unsplit implementer reads every section, in parts.
- Security rules, the state model, deviations and deferrals stay in view for every slice, whatever the slice names.

## Decisions
- **Route 1 (read by section), widened — not a per-slice digest.** Checked by hand on SPEC-002's SLICE-004 (95 KB, 477 lines):
  - Route 1 as first stated (frontmatter, Intent, Implementation Constraints, own SLICE, touched MODULEs, named ids) is ~19 KB. REQ-015's `NAME` rule is in view (line 94, named by the slice); SEC-003/005 are; **SEC-001, SEC-002, SEC-004 are not** (SEC-001 is the rule the slice's later proofs covered, plan :260, :286); **DEFER-008 is not** (`## Deferred`, and Validation Strategy :395, the open F4 at plan :287 rests on it); the State model, the Deviations (json-input changes SEC-005) and REQ-012 (whose delimiter lines REQ-015 prints) are not.
  - Widened: always read whole `## Intent`, `## Deviations from Design Brief`, `## Deferred to Later Tiers`, `### Non-Functional Requirements`, `## Implementation Constraints`, `### State model`, `## Validation Strategy`; then the slice, its modules, its ids, and ids named in what was read (one level). ~34 KB for SLICE-004, everything above in view. No rule in SPEC-002 lives outside these, so a digest adds an artifact for nothing.
- The per-slice implementer is `bodies/slice-start.md` (Step 10); `bodies/implementation.md` is scaffold-only in per-slice mode and the whole-feature implementer — settled by me (the request named `implementation.md`).
- Whole-feature mode gets the same rule (owner: "all recommendations").
- The rule is written once, in a new `references/spec-reading.md`, passed as **SPEC_READING** to every implementation spawn (owner: "all recommendations").
- No step or stop changes, so `docs/sdd-flow-diagram.md` is not edited — settled by me.
- Version 5.5.0 → 5.6.0 (owner: "all recommendations").
- After review (owner: "accepted" Option A, 2026-11-19): the Safety-Net counter counts a file read in parts once (`SKILL.md` rule, `agents/sdd-workhorse.md`, `agents/sdd-critical-reviewer.md`); a chunk implements and state-tests only its own ids; an assigned id missing from the SPEC is recorded and named in the return, and the slice review catches the gap (no new stop).

## How it will work
- `references/spec-reading.md`: the always-read list, the by-id reads (grep the heading or `- ID:` line, read with offset/limit), one-level follow of cited ids, never a whole-file Read; what each caller reads (a slice; a chunk's ids; all sections for an unsplit implementer; the scaffold adds `## Delivery Slices`).
- `phases/implementation-inputs.md`: defines SPEC_READING beside SECURITY / STATE_MODEL.
- `phases/implementation-per-slice.md` :48, :62 and `phases/implementation-whole-feature.md` :25: SPEC_READING added to the implementation spawns' inputs.
- `bodies/slice-start.md` Step 10 and `bodies/implementation.md` Implementation Process step 1 (:210–213, "Read the complete SPEC-XXX document"): read the spec as SPEC_READING says.
- `CLAUDE.md` references list, README "What's new", both version fields.

## Builds on
- `phases/implementation-inputs.md`'s named-input pattern (SECURITY :7, STATE_MODEL :15, TEST_INTEGRITY :71); the existing `references/` one-definition files.
- New files: `agent-engineering/skills/sdd-flow/references/spec-reading.md` — two bodies follow it, and the repo keeps such rules in one reference file, not copied into each body.

## Not now
- A per-slice digest; changing the planning step or the spec template; the reviewers' and fixers' reading of the spec.

## Beyond the request
- none

## Done when
- The bodies and phase chapters above follow the new reference; `cd agent-engineering/skills/sdd-flow && python3 -m unittest discover -s scripts/tests` passes; Codex has reviewed the change.

## Risk
- ordinary — Markdown instructions for implementer subagents; no code, data or secrets touched. A rule kept outside the always-read sections (a slice's prose, `## Implementation Notes`) would still be missed.

## Decision records to write
- none (a feature-level reading rule; the reference file is its record)
