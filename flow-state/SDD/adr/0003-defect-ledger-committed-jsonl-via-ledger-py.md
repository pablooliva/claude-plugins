---
adr: 0003
title: Record escaped defects in a committed per-application defect ledger written only through ledger.py
status: Accepted
date: 2026-11-17
supersedes: null
superseded_by: null
tags: [cross-cutting, defect-ledger, feedback-loop, file-format]
---

# ADR 0003: Record escaped defects in a committed per-application defect ledger written only through ledger.py

## Status

Accepted (2026-11-17)

## Context

The flow's reviews find defects, and users find more after shipping, but nothing keeps a durable, queryable record of which check caught which kind of defect or which one missed it. Without it the owner cannot tell which checks earn their cost, and a bug fix cannot learn from earlier defects of the same class. Every later feature that touches reviews, bug fixes, or the monthly report reads or writes this record, so where it lives and who may touch it binds future work. See also: ADR 0002 (artifact layout; `SDD/.records/` holds process records).

## Decision

Each application keeps `SDD/defects.jsonl`: committed, one JSON line per defect (HIGH or MEDIUM), carrying the loop that caught it, its class, and the check the fix added. It is not under `SDD/.records/`, which holds process records that are not product history. One stdlib script, `ledger.py`, is the only reader and writer; fields, loops and maps are defined once in its docstring. Both sdd-flow and sdd-lite write through it; every command refuses a ledger holding a duplicate `id`.

## Alternatives Considered

### Committed JSONL in SDD/, written only through ledger.py (chosen)

It travels with the code and its history, is one line per defect so merges and diffs stay readable, and a single reader/writer keeps the format from drifting between the two flows.

### Keep the records under SDD/.records/

Rejected because `.records/` holds process records of one cycle; the ledger is long-lived history about the product and must be committed and found by the monthly report.

### Free-form markdown, written by each flow's own prose

Rejected because two flows would write it differently and the report would have to parse prose; a fixed line format with one parser is checked by tests.

## Consequences

### Positive

- One definition of the format and one reader; the monthly report and the bug-fix lookup share it.
- The ledger is versioned with the application, so history survives merges and machines.

### Negative / Trade-offs accepted

- Hand edits are not supported; a duplicate id after a merge is refused by name and renumbered by hand.
- Every application gains one committed file and a dependency on the installed plugin's script.

### Neutral observations

- Only HIGH and MEDIUM defects are recorded; LOW findings are not.

## References

- Design brief: flow-state/SDD/requirements/DESIGN-002-defect-ledger.md (revision 4, approved, Tier 1)
- Research: flow-state/SDD/research/RESEARCH-002-defect-ledger.md
- Proposal: proposals/feedback-loop-2026-11-16.md
