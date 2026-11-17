---
adr: 0005
title: Defect-ledger monthly report is report-only; the owner picks any change to checks
status: Accepted
date: 2026-11-17
supersedes: null
superseded_by: null
tags: [cross-cutting, defect-ledger, human-in-the-loop, automation]
---

# ADR 0005: Defect-ledger monthly report is report-only; the owner picks any change to checks

## Status

Accepted (2026-11-17)

## Context

A monthly BB automation reads each application's defect ledger (ADR 0003) and summarises which loops catch which classes of defect and which checks seem unused or missed things. The temptation is to act on that automatically. Counts from a small ledger are weak evidence, and the checks (reviews, tests, rules) are what protect the applications, so any automatic edit risks removing a safeguard on thin data. See also: ADR 0003, ADR 0004.

## Decision

The report only reports: it files one task per month covering the applications and changes nothing. No automatic pruning, no automatic edits to reviews, tests, rules or setup files. The owner reads it and picks any change to a check. The automation uses no model and reads each application's committed default branch through `ledger.py summary`.

## Alternatives Considered

### Report-only (chosen)

Keeps judgement with the owner, who knows context the counts lack, and an unattended job holds no write access to applications.

### Automatic pruning or proposed edits applied by the automation

Rejected because small samples could remove a check that guards a rare but severe defect, and an unattended job would need write credentials.

### No report, owner queries the ledger on demand

Rejected because without a prompt the ledger would go unread; a monthly task keeps the feedback loop closed.

## Consequences

### Positive

- No unattended change to any application; a wrong reading costs a task, not a safeguard.
- The automation needs only read access.

### Negative / Trade-offs accepted

- Improvements depend on the owner acting on the monthly task.
- Unreachable applications show as a line in the report until a route is chosen.

### Neutral observations

- A future ADR may revisit this once ledgers hold enough data to trust.

## References

- Design brief: flow-state/SDD/requirements/DESIGN-002-defect-ledger.md (revision 4, approved, Tier 1)
- Research: flow-state/SDD/research/RESEARCH-002-defect-ledger.md
- Proposal: proposals/feedback-loop-2026-11-16.md
