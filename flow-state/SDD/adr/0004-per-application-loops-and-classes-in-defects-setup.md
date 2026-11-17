---
adr: 0004
title: Each application declares its own loops and defect classes in SDD/defects-setup.json
status: Accepted
date: 2026-11-17
supersedes: null
superseded_by: null
tags: [cross-cutting, defect-ledger, configuration]
---

# ADR 0004: Each application declares its own loops and defect classes in SDD/defects-setup.json

## Status

Accepted (2026-11-17)

## Context

The defect ledger (ADR 0003) names, for each defect, the loop that caught it and its class. Applications differ: one has CI, another has an integration environment, and the kinds of defect they meet differ too. A name list fixed in the plugin would either be wrong for some application or grow with every application's needs. See also: ADR 0003.

## Decision

Each application declares its loops and classes in `SDD/defects-setup.json`. The first write in an application without one creates it with the four plugin loops (slice review, code review, final check, user) and the class `unclassified`; `ci` and `integration` are never added for you. A writer meeting a new kind of defect uses `unclassified`, and the end report proposes a name; new names are added only with the owner's approval.

## Alternatives Considered

### Per-application declaration (chosen)

Each application's names match its own checks and defects, and the owner controls vocabulary, so the monthly report groups meaningfully.

### One plugin-wide fixed list

Rejected because it fits no application exactly, and every new class would need a plugin release.

### Writers invent names freely

Rejected because class names would fragment ("race" vs "race-condition") and the *Seen before* lookup and report counts would be unreliable.

## Consequences

### Positive

- Names stay consistent within an application, so lookups and counts are meaningful.
- Loops that do not exist (CI, integration) never appear by accident.

### Negative / Trade-offs accepted

- A class waits as `unclassified` until the owner approves a name.
- One more committed file per application.

### Neutral observations

- Each application's setup file is independent; the plugin only supplies the default.

## References

- Design brief: flow-state/SDD/requirements/DESIGN-002-defect-ledger.md (revision 4, approved, Tier 1)
- Research: flow-state/SDD/research/RESEARCH-002-defect-ledger.md
- Proposal: proposals/feedback-loop-2026-11-16.md
