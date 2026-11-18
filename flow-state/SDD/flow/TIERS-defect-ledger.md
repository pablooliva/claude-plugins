# TIERS-defect-ledger

| Tier | Status | Built in | Task |
|---|---|---|---|
| 1 — POC-plus | shipped 2026-11-18 | SPEC-002-defect-ledger.md | CLAUDEPLUG-20 |
| 2 — Standard | sketch | — | CLAUDEPLUG-21 |
| 3 — Full | sketch | — | CLAUDEPLUG-22 |

## Tier 1
Does: a committed defect ledger and setup file per application; review lines written by sdd-flow (4i) and sdd-lite (close-out); the bug-fix rule (`## Escape`, *Seen before*, close at the end); `ledger.py` (add, reviews, close, lookup, summary); the `/defect-ledger` skill; the monthly report-only BB automation (commands shown to the owner, never run by the flow). Shipped as 5.5.0.
Does not: the finding line itself (5.4.0), the trace index, renumbering duplicate ids at merge, reading an application the server host cannot reach, CI for any application, or a flow test harness.
Look at when using it: the first real bug-fix cycle (does *Seen before* help), the report's counts-only-below-threshold sections, and growth (source 1.8x, tests 2.8x the brief's budget: the owner's call at 4h).

## Deferred
| ID | Item | To tier | Why it was safe to leave out | If reached now | Cost to add later | Came from |
|---|---|---|---|---|---|---|
| DEFER-001 | `/retro` reads the bb trace index when a transcript is gone, and lists Codex sessions (proposal part 4) | 2 | Owner's tier split (proposal Tiers) — Evidence: the ledger is the measured need | not reachable | moderate | proposal |
| DEFER-002 | Renumber duplicate ledger ids, and the briefs naming them, at worktree merge | 2 | By hand — the merger renumbers; `ledger.py` refuses a ledger with duplicates | every ledger command refuses, naming the duplicate lines | moderate | proposal |
| DEFER-003 | Read an application whose checkout is not on the server host (Sift) | 2 | By hand — the owner runs `/defect-ledger report` there (Q1, decided: brief D7) | its report section says "not reachable from the server host" | moderate | proposal |
| DEFER-004 | A command to re-label a line's class | 3 | By hand — the owner edits the line | not reachable (writers use `unclassified`) | cheap | proposal |
| DEFER-005 | `/defect-ledger` turns the summary into proposed moves (a check earlier, one dropped) | 3 | Evidence — only if reading the table proves not enough | not reachable | moderate | proposal |
| DEFER-006 | Reading ledgers across applications together | 3 | Evidence — not yet shown needed | not reachable (one section per application) | moderate | proposal |
| DEFER-007 | Escape rate and cost per feature compared across sdd-flow, sdd-lite and plain Claude Code (CLAUDEPLUG-17, check 3) | 3 | Evidence — needs months of ledger first | not reachable | expensive | proposal |
| DEFER-008 | An executable flow test harness that runs sdd-flow/sdd-lite Markdown steps against fixtures and asserts the calls made and the file state (would prove the flow halves of a refused or malformed lookup reaching the brief as `unavailable`, instruction-like history kept as data, and stop / open questions / an alternate id at close-out writing or closing nothing) | 2 | Script-level proofs (tests of `ledger.py` named in REQ-012 and REQ-014) plus the review reading the Markdown step | A flow-step regression is caught only by review | expensive | SLICE-003 review (owner, 2026-11-17) |
| DEFER-009 | A check that tells an owner-approved `/defect-ledger log` from an unapproved one: the show-exact-input / wait / re-approve step is a Markdown procedure, and `add` receives the same JSON either way, so no script guard exists (decided review-only under DEFER-008) | 2 | The step is read in review; an invented approval token would be checked by nothing | A skipped approval is caught only by review | expensive | implementation (4e.5 iteration 4, F4) |

## Removed
- A separate `references/` file defining the ledger format — Existing code: `ledger.py`'s docstring is the one definition.
- A separate monthly-report script in the repository — Existing code: `ledger.py summary` plus the `bb` CLI.
- A new stop to approve a new class name — Moving parts: the standing `unclassified` class records it without a stop.

## Tier 2 — sketch
- When a session's transcript is gone, `/retro` reads that session from the bb trace index, marked as a summary; with Codex sessions it lists them for the same repository and dates. No index → it says so once and carries on.
- Two branches that added ledger lines at once merge without a hand renumber.
- The monthly report covers an application whose checkout lives on another machine.
- An executable flow test harness runs the sdd-flow and sdd-lite Markdown steps against fixtures and asserts the calls and file state, so a refused lookup, instruction-like history and a stop or alternate close-out id are tested, not only read (DEFER-008).

## Tier 3 — sketch
- The report can propose moves (a check earlier, a check dropped) when asked.
- Ledgers can be read across applications together.
- Escape rate and cost per feature compared across sdd-flow, sdd-lite and plain Claude Code.
- A line's class can be re-labelled by command.

## Feedback
