---
adr: 0001
title: Ship SDD per-slice mode in the same codebase, gated by delivery_mode frontmatter
status: Accepted
date: 2026-05-05
supersedes: null
superseded_by: null
tags: [cross-cutting, distribution, sdd-plugin, sdd-flow]
---

# ADR 0001: Ship SDD per-slice mode in the same codebase, gated by `delivery_mode` frontmatter

## Status

Accepted (2026-05-05)

## Context

The SDD plugin and the `agent-engineering/sdd-flow` skill currently deliver features horizontally — every layer is built across all REQs before the next layer begins. The vertical-slicing decomposition proposal (`proposals/vertical-slicing-decomposition.md`) introduces a per-slice delivery model where each slice is a thin end-to-end thread implemented in isolation, with mandatory per-slice review, per-slice retrospectives, a rolling learnings ledger, slice-boundary checkpoints, and a re-planning trigger.

This is a non-trivial behavioral fork: per-slice mode adds a new spec section (`## Delivery Slices`), a practicality gate, four new commands (`/slice-start`, `/slice-review`, `/slice-retro`, `/slice-commit`), a migration helper (`/sdd-migrate-layout`), a new checkpoint axis (`--skip-slice-checkpoints`), and a distinct Step 4 state machine in `sdd-flow`. The accumulated surface area is large enough that a fork into a separate plugin (`sdd-slices`) was seriously considered — and the question was reopened a second time after the full scope was understood.

This decision binds how every future SDD feature gets distributed and how every future delivery-mode-aware command is wired. Capturing it as an ADR ensures the rationale is discoverable when a future contributor proposes "let's just fork the plugin" without the prior context.

## Decision

**Ship per-slice as additive, opt-in behavior inside the existing `sdd/` plugin and the existing `agent-engineering/sdd-flow` skill.** No fork. No companion plugin. The runtime branch is a single frontmatter field on the spec:

```yaml
---
delivery_mode: whole-feature   # default; preserves existing behavior bit-for-bit
# OR
delivery_mode: per-slice       # opt-in; enables slice section, slice commands, slice state machine
---
```

Concretely:

- **`delivery_mode: whole-feature`** is the default. When omitted, the loader treats the spec as `whole-feature`. All existing behavior (REQ-based chunking in `sdd-flow` Step 4, single-pass `/implementation-start`, no `## Delivery Slices` section, no slice-integrity review checks) is preserved exactly.
- **`delivery_mode: per-slice`** is the opt-in. It enables the `## Delivery Slices` spec section requirement, the practicality gate, the slice-integrity check in spec critical review and panel review, the per-slice Step 4 state machine in `sdd-flow`, and active behavior for the `/slice-*` commands.
- **The four `/slice-*` commands ship to all SDD users** but display a friendly `"this command requires delivery_mode: per-slice"` message and exit when invoked under `whole-feature` mode. They are present in autocomplete but inert.
- **The SDD plugin README gets two clearly-distinct workflow sections** — *Whole-feature workflow* and *Per-slice workflow* — each with its own diagram. A one-paragraph "which mode is right for you?" decision aid opens the README.
- **Documentation, not code, is the fork.** The runtime is one codebase; the user-facing documentation has two tracks the user picks between.

## Alternatives Considered

### Single codebase with `delivery_mode:` frontmatter (chosen)

The actual divergence between the two modes is concentrated in `/implementation-start`'s mode-aware branch, the per-slice Step 4 state machine in `sdd-flow`, the new `/slice-*` commands, and a few mode-gated review checks. The bulk of the plugin — research commands, planning commands, all reviews, ADR capture, eval scaffolding, completion, hooks, the SubagentStop infrastructure — is genuinely shared. A single codebase with a runtime branch keeps the shared 80%+ truly shared, and concentrates the delta where it actually exists. Documentation divergence (the README workflow sections) is a writing exercise, not a maintenance burden.

### Fork the SDD plugin and `sdd-flow` skill into vertical-slicing variants

Rejected because it would duplicate ~18 SDD commands and a ~700-line `sdd-flow` skill, the vast majority of which is unaffected by the per-slice delta. Within months the two forks would drift on every unrelated bug fix or improvement — every change would have to be ported twice, and the ports would gradually diverge. The maintenance cost compounds with every future feature regardless of whether that feature has anything to do with slicing.

The fork question was reopened after the full per-slice surface area was scoped (new commands, new checkpoint axis, new state machine, re-planning trigger, directory restructure, README divergence). Even at the larger surface, the answer was the same: the genuine shared surface (research, planning, all reviews, completion, hooks, infrastructure) still dominates.

### Companion plugin (`sdd-slices` depending on `sdd`)

Rejected because it forces users into a two-plugin install for one workflow, and the modified `/implementation-start` behavior is hard to express purely additively — the existing command must read `delivery_mode` and branch internally. A companion plugin can ship the new `/slice-*` commands and the migration helper, but it cannot cleanly intercept and re-route an existing command's behavior without monkey-patching. The cost (two-plugin install, monkey-patch surface) exceeded the benefit (avoiding a small frontmatter-gated branch in one existing command).

### Fork only `sdd-flow`, keep `sdd` unified

Briefly considered. Rejected because the per-slice changes also touch SDD plugin commands (`/implementation-start` mode-awareness, slice-integrity in `/critical-review` and `/spec-review-panel`, the new `/slice-*` and `/sdd-migrate-layout` commands), so a fork that stops at `sdd-flow` doesn't cleanly draw the boundary either. If both pieces are fork-eligible, both inherit the duplication tax described above.

## Consequences

### Positive

- **Whole-feature users see zero behavioral change.** Existing specs without `delivery_mode:` continue to work exactly as today. No re-install, no migration of intent, no new mental model required.
- **Single source of truth for shared behavior.** Bug fixes to research, planning, reviews, completion, hooks, etc., land in one place and benefit both modes immediately.
- **Opt-in is a one-line frontmatter change.** A user trying per-slice on a new spec just adds `delivery_mode: per-slice` and fills in the `## Delivery Slices` section. No tooling install, no plugin pin to manage.
- **Discoverable mode boundary.** `delivery_mode:` in the spec frontmatter is the single, grep-able signal that tells any reader (human or subagent) which behavior tree applies to this feature.
- **Two-track documentation removes the diagram-confusion problem** that initially motivated the fork question without paying the fork's maintenance tax.

### Negative / Trade-offs accepted

- **`/slice-*` commands ship to whole-feature users as inert commands.** Small cognitive cost (more commands in autocomplete) for users who never opt into per-slice. Mitigated by the friendly "requires per-slice" message — the commands are discoverable and self-documenting.
- **`sdd-flow` Step 4 carries two distinct state machines.** The orchestrator's per-mode branch must be unambiguous and well-tested at the boundary; a bug in mode-routing affects both modes.
- **Documentation must be kept in sync across two README workflow sections.** Bug fixes that affect both modes require parallel updates in both sections. Mitigated by the sections being purely descriptive — they describe the behavior emitted by the same shared code.
- **Mode-aware commands carry conditional logic.** `/implementation-start`, `/critical-review`, `/spec-review-panel` each have a mode branch. Each branch must be tested in isolation to ensure whole-feature is bit-for-bit unchanged.

### Neutral observations

- **Reopen condition documented in proposal:** if research/planning subagent prompts later turn out to need substantively different instructions in per-slice mode (beyond the Slices section), or if per-slice evolves to own research/planning differently (per-slice planning, per-slice research), the fork question reopens. As of this ADR, neither has occurred.
- **The decision binds future cross-cutting features:** any future "modes" of SDD behavior (e.g., a hypothetical `delivery_mode: continuous` for trunk-based flows) should follow the same pattern — frontmatter-gated runtime branch in one codebase, not a fork.

## References

- `proposals/vertical-slicing-decomposition.md` — § "Distribution Strategy" and § "Reconsidering the fork question (revision after full scope)"
- `SDD/research/RESEARCH-001-vertical-slicing-step-c.md` — Flow 1 (`delivery_mode:` propagation through the SDD plugin)
- `SDD/research/CLARIFICATION-001-vertical-slicing-step-c.md` — locked decision #7 (code merged, not forked)
- `sdd/commands/planning-start.md` (Step A merged, commit `ffeec97`) — frontmatter field `delivery_mode: whole-feature` introduced in the spec template
