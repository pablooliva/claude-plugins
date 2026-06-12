# Progress Rotation live-test findings — 2026-06-12

> **Resolution (2026-06-12):** Pablo adopted F1, F2 option (a), F3, and F4. All four
> are implemented in ae **1.0.3** — `phases/protocols.md` (canonical procedure),
> `SKILL.md` Progress Hygiene rule 2, `commands/adhoc-compact.md` step 4, and
> `commands/continue.md` — bundled with the nested-subagents annotations.

Three Sonnet `sdd-workhorse` agents each executed the Progress Rotation procedure
(`agent-engineering/skills/sdd-flow/phases/protocols.md` § Progress Rotation) on a
real-world fixture, given only the procedure text and a sandbox path. Original
2,202-line digest fixture was unrecoverable; fixtures derived from real sherpa/redakt
progress files. Sandboxes preserved at `/tmp/rotation-test/{A-sherpa,B-redakt-midflow,C-redakt-complete}`
(volatile — inspect before reboot).

## Fixtures and verdicts

| Fixture | Source | Tests | Verdict |
| ------- | ------ | ----- | ------- |
| A | sherpa, 1,061 lines, feature 001 complete + feature 002 ambiguous-tail | size rotation, "resolved" judgment | **FAIL** (fidelity) — archive verbatim ✓, but kept content retyped: 55 lines mutated |
| B | redakt truncated at line 482, `## Awaiting Spec Amendment Decision` pending+latest | verbatim carry-forward invariant | **PASS** — archive byte-identical (1–433), both halt blocks carried byte-identical |
| C | redakt full, 894 lines, feature complete, halt blocks resolved in trailing paragraphs | resolved-halt archival | **PASS** — archive byte-identical, zero "Awaiting" residue, 57-line bounded live file |

## Findings

### F1 — HIGH: no fidelity invariant for kept non-halt content (fixture A)
Procedure mandates "verbatim" only for pending halt blocks. The active feature's
step history (neither resolved-archivable nor a halt block) has no stated fidelity
rule; agent A retyped it while keeping it: en-dash→hyphen, `…`→`...`, `≥`→`>=`,
`\uv run`→`uv run` (meaning change — backslash was the Socket-Firewall bypass
convention), dropped qualifier clauses, deleted `### ID Preservation (grep)`
subsection + "Frozen code untouched" audit line.
**Proposed fix (protocols.md, add to Invariants):** "Everything that remains in the
live file is preserved byte-identical — never retyped, reflowed, re-encoded, or
compressed. The only newly written text in a rotation is the `## Current State`
head and the `### Progress rotated` stamp."

### F2 — MEDIUM: size rotation cannot bound a file dominated by one active feature (fixture A)
Live file after rotation: 505 lines — still over the ~500 threshold, because
feature 002's unresolved history (~485 lines) stays. "Size rotation moves all
resolved blocks" is ambiguous at sub-feature granularity: completed phase blocks
(research/planning COMPLETE banners) of the active feature were treated as
non-resolved. **Decision needed:** either (a) extend the procedure — within the
active feature, phase blocks with a recorded COMPLETE banner are also resolved and
archivable (Current State table keeps their pointers), or (b) accept and document
the limitation.

### F3 — LOW: canonical halt-header list is closed (fixtures B & C, both agents flagged)
Step 3 enumerates five exact headers; real files contain custom ones
(`## Awaiting Environment Decision`, `## Awaiting Spec Amendment Decision`). Both
agents resolved correctly via the "anything Phase Detection still needs" catch-all.
**Proposed fix:** generalize the list to `## Awaiting *` + `## PARTIAL*`.

### F4 — LOW: rewritten Current State may drop literal phase-marker strings (fixture C)
Phase Detection keys on e.g. `"Implementation Phase - COMPLETE"`; C's rewrite has
only a table cell `**COMPLETE ✓**`. LLM evaluation likely still correct, but the
procedure should mandate carrying canonical phase-state lines into the status table.

## Positive results worth keeping
- Archives were byte-identical to moved content in all three fixtures (verified by diff).
- B: pending-block carry-forward held byte-exact, including two NON-canonical halt headers.
- C: resolved-in-trailing-paragraph halt blocks correctly archived, not spuriously carried.
- A: conservative "feature 002 not resolved" call on an ambiguous tail ("Proceeding
  to commit (4i)" with no 4i record) — the safe failure direction.
