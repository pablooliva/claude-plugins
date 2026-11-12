# sdd-flow: replace the enforcement-site proof with one security verification (2026-11-12)

Status: **decided by the owner 2026-11-12. Not implemented.** Part of release 2 of
`proposals/sdd-flow-simplification-2026-11-12.md` ("enforcement-site machinery except for security rules"
and "fixing every LOW finding" in its broader cuts). This note holds the evidence and the decision; the
prompt that implements it is `proposals/enforcement-site-proof-prompt-2026-11-12.md`.

History: the proof was introduced to stop implementers vouching for their own guards, and was made cheaper
twice: 3.11.0 (`proposals/site-count-convergence-2026-10-10.md`: control register, row-only findings closed
inside the review) and 3.14.0 (the tier sets how deep the proof goes; label-only differences cost no round).
This note finds that the cheaper versions still do not converge on large features, and that its real yield
came from adversarial reading of the security rules, not from counting.

## Decision

- **Remove:** the blind count (4a.5 and the count in 4e.5) and `scripts/site-diff.py`; the control register;
  the filing conventions; the site inventory; per-slice counting; site proof for non-security rules; the tier
  rule on how deep the proof goes (`simplicity-challenge/references/tiers.md` depth row and
  `references/enforcement-sites.md` §7).
- **Keep one adversarial security verification at the end of the feature, on Codex.**
  - It reads every security rule of the spec for bypass paths: respellings and aliases, error paths, unset
    settings, missing configuration, values echoed back to a user.
  - Each gap it finds is fixed with a test that fails when the guard is removed (a mutation check).
  - At most two rounds; what is left goes to the owner.
- **Stop fixing LOW findings.** Reviews still report them; they are listed for the owner, and a review with
  only LOW findings passes.
- **Run mutation checks in a scratch copy** of the working tree, so a mutation run cannot write into the
  repository's local databases, caches or history.
- Non-security rules get ordinary tests, checked by the Test Integrity Lens (`references/test-integrity.md`)
  as today.

## Evidence

Two applications built with sdd-flow, read from their `SDD/orchestration/progress*.md` records and fix
entries (sampled, not every review document).

### The benchmark harness (sdd-flow-eval, SPEC-001, agent-engineering 3.14.x)

- Tier 1/2, so the blind count ran once, at the final check (4e.5). It ran five rounds on 2026-11-05 and 06.
- The two lists never agreed. Diff HIGH/MEDIUM per round: 89/105, 22/58, 25/168, 9/59, 17/60.
  Verification HIGH per round: 26, 26, 19, 6, 10. For eight security rules the implementer listed about
  505 sites and the blind counter about 280.
- It halted twice; the owner ended it by decision, security rules left `Partial`, no 4f/4h run.
- It added about 150 tests (729 → 882; `tests/test_sites_*.py` alone 1,951 lines) and about 4,900 lines of
  site records, on a harness of ~8,000 lines of code and ~11,800 lines of tests.
- Real code fixes it produced: about six, all security gaps (folder permissions, a container network-mode
  check, an oversized output read, links refused in an image copy, leftover-container cleanup, the judge's
  withheld-test scan).
- One of those fixes, the withheld-test scan, was too broad and later made the judge refuse every tomlkit
  review until commit `e711432`.
- A Codex review after the flow found the bug that mattered most for results (a missing cost record reported
  as a complete USD 0), outside what the site proof looks at.

### eduKate (private application, five cycles, agent-engineering 3.x)

| Cycle | Where counted | Rounds | Outcome |
|---|---|---|---|
| SPEC-001 | final check | 8 | converged; two halts |
| SPEC-002 | every slice + final | 2–5 per slice | slices 1–4 each hit the round cap; owner ended each with "commit without another count" |
| SPEC-004 | final | 2 | converged |
| SPEC-006 | each slice + final | 1–5 | converged |
| SPEC-007 (shared gateway) | final only | 6 so far | two halts; still open on 2026-11-12 |

- **Small features converged; large ones did not.** Each fresh count found new "sites".
- **SPEC-001, SPEC-002: bookkeeping.** Most HIGH were row-only (23 of 29, 50 of 55, 39 of 40 in SPEC-001's
  rounds). SPEC-001's fix rounds 2–7 changed no production code. SPEC-002 added 118 inventory rows in one
  slice round; the code changes found were small (a drawing fault now reported, a failed start-up returning
  a fresh state).
- **SPEC-006: test-harness changes only** (nothing under `src/`).
- **SPEC-007: real security gaps, found late.** Round 3 found two configuration gaps (a missing setting the
  code relied on a default for, and a check skipped when a setting is unset). Round 5 found three input and
  output handling gaps in the gateway (a policy bypass by alternate spelling, upstream error text passed
  through, internal names echoed in start-up errors). They came from Codex reading the code adversarially and
  from gaps the blind counter flagged — not from the two lists matching. Round 4 added tests only ("no new
  test showed a defect"). Details stay in the application's own records.
- **SPEC-007's cost per round:** a fresh blind count, a 35–45 min eval run, the evidence run (up to 4 h 40 min
  with the real upstream), a Codex verification. Two verification runs failed partway (sandbox limits, a
  cancelled run); the owner narrowed the evidence rules by hand in four rounds; a reviewer's mutation wrote
  planted test keys into a gitignored local eval-history database, failing two tests until cleaned.

### Long review loops were not caused by sites

- SPEC-007's SLICE-009 took 14 rounds with no per-slice count. The rounds came from evals (an unreliable
  language switch, empty replies — real product problems the evals caught), tracing findings, model slowness
  and an upstream change, and the fix-every-LOW rule: five rounds started from reviews that had already
  approved with only LOW findings left.

## Reading

- The counting and diffing does not converge on features with many rules: whether a guard, its caller, or
  each path through it is a "site" is a judgment, and two agents make it differently every time. The control
  register, filing conventions, "places before labels" and the row-only and cross-filed rules exist to manage
  that disagreement.
- The value came from adversarial reading of security rules and from tests that fail when a guard is removed.
  The new step keeps exactly that.
- Fixing every LOW finding costs whole rounds (fix → re-review, and on SPEC-007 an eval and evidence run) for
  little gain.

## Caveats

- One security pass may miss gaps that several fresh readers found on SPEC-007; hence two rounds, not one.
- Earlier eduKate cycles ran on versions before 3.11.0 and 3.14.0, which made row-only and label-only findings
  cost no round.
- Fix entries were sampled; a small code fix in SPEC-002 or SPEC-006 may have been missed.
- Cycles in progress (eduKate SPEC-007) finish on the version they started with.
