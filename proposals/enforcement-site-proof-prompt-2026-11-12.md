# Task: sdd-flow — replace the enforcement-site proof with one security verification

You are working in a git worktree of the claude-plugins repo. Change the `agent-engineering` plugin's `sdd-flow`
skill as decided below. This is one part of release 2 of `proposals/sdd-flow-simplification-2026-11-12.md`;
the other release 2 items (size controls, panel narrowing, process records out of the repo, orchestrator
slimming) are out of scope — do not start them.

A separate task follows this one, on top of it: changing what the code reviews check (fit with the
surrounding code, whether it could be smaller, a footprint overrun as a finding, a fixer rule that fit findings
are fixed by removing or merging code, and fit findings graded MEDIUM when they add a file, a layer or a
duplicate helper). It is discussed in another thread. Do not make those changes here, and do not change the
review criteria in `bodies/code-review.md`, `bodies/slice-review.md` or `bodies/critical-review.md` beyond what
removing the site steps and the LOW rule requires.

## Before you start

- Release 1 of the simplification (agent-engineering 4.0.0: modes and stop-skipping flags removed;
  `proposals/sdd-flow-simplification-release-1-prompt-2026-11-12.md`) touches the same files. Check that
  `main` holds 4.0.0 and that this worktree is based on it. If it does not, stop and tell me; do not build on
  3.16.x.
- Read the repo's `CLAUDE.md`, then `proposals/enforcement-site-proof-2026-11-12.md` (the decision and the
  evidence). Where this prompt and that note differ, the note wins and you say so.

## Why

On two applications built with sdd-flow, the blind site count and its diff did not converge on large
features (5–8 rounds, repeated halts ended by the owner), produced mostly inventory rows and tests for places
already guarded, and cost hours per round. What it found that mattered were security gaps, found by an
adversarial reader. Long review loops were also driven by the rule that every LOW finding is fixed.

## What to change (decided; do not reopen)

1. **Remove the site-count machinery:**
   - the blind count (4a.5 per slice and per feature; the count in 4e.5), `bodies/site-count.md`,
     `bodies/site-count-compact.md`, the blind-count handoff in `phases/protocols.md`;
   - `scripts/site-diff.py` and `scripts/tests/test_site_diff.py`, and the snapshot logic that exists only
     for it (keep snapshots a re-review needs to read what a fix changed, if anything still uses them —
     check `references/second-model-review.md` and the 3.15.0 fix-round-scoped tests);
   - the control register (planning, planning-complete and spec critical-review bodies), the filing
     conventions file, the site inventory (`SITES-IMPL-*`), the `SITE-COUNT-*`, `SITE-DIFF-*` and
     `REVIEW-SITES-*` artifacts, the `## Awaiting Site-Count Resolution` stop and its resume rule;
   - site proof for non-security rules, and the tier depth rule (`references/enforcement-sites.md` §7 and
     the depth row in `skills/simplicity-challenge/references/tiers.md`).
2. **Add one security verification at the end of the feature** (where 4e.5 is today), run on Codex through
   `scripts/second-model-review.py`, with the usual Claude fallback.
   - Input: the spec's security rules (what counts as one: the spec's security IDs, plus the OWASP agent
     controls when `agent_security` is on — settle and state it), the code, the tests.
   - It looks for paths where a rule does not hold: respellings and aliases, error paths, unset settings,
     missing configuration, values echoed back to a user.
   - Each gap is a finding; the fix adds a test that fails when the guard is removed and shows that failure.
   - At most two rounds (verify → fix → verify → fix → verify). What is left stops the flow for the owner,
     with one halt block, one resume rule, one diagram row.
   - Replace `references/enforcement-sites.md` with a short standard for this step (what a security rule is,
     what the verification checks, what a proving test is). Target: under a fifth of today's size.
3. **Keep what 4e.5 also carries today.** The final check also re-runs the Tracing Lens (tracing gate on),
   the eval run of record and Eval Check (evals gate on), and the last-look test-integrity read. These stay at
   the end of the feature, attached to the new verification or to the end-of-feature review — your choice,
   stated with the reason. With both gates off, nothing beyond the security verification runs there.
4. **LOW findings are listed, not fixed.** In every review (slice review, code review, critical reviews, the
   new verification), a review with no HIGH or MEDIUM passes. LOW findings go to a list the owner sees at the
   slice pause and in the end report. Update Key Principles 2 and 7 and every "ALL findings (HIGH/MEDIUM/LOW)"
   rule, and the stall checks that mention LOW.
5. **Mutation checks run in a scratch copy** of the working tree (outside the repository, removed afterwards),
   never in the working tree itself. Applies to every body that mutates code to prove a test
   (`references/test-integrity.md`, the reviews, the fixers, the new verification). State how the copy is
   made so that uncommitted work is included.

## Where

Files that name the site proof today (from a grep on 3.16.1; grep again on your base):
`CLAUDE.md`, `README.md`, `agent-engineering/README.md`, `agent-engineering/docs/sdd-flow-diagram.md`,
`agent-engineering/docs/observability-diagram.md`, `agent-engineering/skills/observability-init/references/tracing.md`,
`agent-engineering/skills/retro/references/sdd-evidence.md`, `agent-engineering/skills/simplicity-challenge/references/tiers.md`,
and under `agent-engineering/skills/sdd-flow/`: `SKILL.md`; `bodies/` code-review, continue, critical-review,
implementation-complete, implementation, planning-complete, planning, site-count, slice-retro, slice-review,
slice-start; `phases/` implementation-per-slice, implementation-whole-feature, planning, protocols, setup;
`references/` enforcement-sites, evals, second-model-review, test-integrity, tracing-lens; `scripts/site-diff.py`,
`scripts/tests/test_site_diff.py`.

## Rules

- `SKILL.md`'s three rules apply to every edit: a body's only inputs are its prompt's paths; every stop that
  waits for an answer has a halt block, a resume rule in `phases/protocols.md`, and a row in the diagram;
  every slice state change, stop and commit has an owner in `phases/implementation-per-slice.md`'s owner
  table. A removed stop is removed from all three; the new one is added to all three.
- Remove, don't relabel: no "formerly" or "before 4.x" notes, no compatibility code for cycles started on the
  old version (they finish on it; say so in the release notes). The instructions must get shorter: report the
  size of `SKILL.md`, the phase files, the touched bodies and references before and after.
- Do not modify the `sdd` plugin.
- Version: next minor after `main` (4.1.0 if main is 4.0.0), in both
  `agent-engineering/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`.
- Update `docs/sdd-flow-diagram.md` (both diagrams, the stage table, the stops table) and the repo `CLAUDE.md`
  tree comments for the removed and replaced files.
- Run the skill's tests: `python3 -m unittest discover -s agent-engineering/skills/sdd-flow/scripts/tests`.
- Get a Codex review of the uncommitted change (`codex review --uncommitted`, output to a file, read the last
  block), fix what is real, and say what you did not fix and why.
- Do not commit. Stop with the change uncommitted and report back.

## Done when

- No plugin file names the blind count, `site-diff.py`, the control register, the filing conventions, the
  site inventory, or the site-count halt.
- Items 1–5 are done; you can point to the file and line for each.
- With tracing and evals on, the end of the feature still runs the trace check, the eval run and Eval Check,
  and the last-look test read.
- Tests pass; the Codex review has been run and answered.
- Your report lists: items done, anything decided differently (with the reason), open choices you settled
  (what counts as a security rule; where the tracing/evals final check lives; how the scratch copy is made),
  sizes before and after, and Codex findings left open.
