# Task: sdd-flow — the code reviews also judge fit and size

You are working in a git worktree of the claude-plugins repo. Change the `agent-engineering` plugin's `sdd-flow`
skill as decided below. This is one part of release 2 of `proposals/sdd-flow-simplification-2026-11-12.md`; the
other release 2 items (growth budget and reuse map, the simplicity stop after the spec, panel narrowing,
consolidation pass, round caps, process records out of the repo, orchestrator slimming) are out of scope — do
not start them.

## Before you start

- This builds on 4.1.0 (`proposals/enforcement-site-proof-prompt-2026-11-12.md`: one security verification
  replaced the site proof; LOW findings are listed, not fixed). Check that `main` holds 4.1.0 and that this
  worktree is based on it. If it does not, stop and tell me.
- Read the repo's `CLAUDE.md`, then `proposals/review-criteria-2026-11-12.md` (the decision and the evidence).
  Where this prompt and that note differ, the note wins and you say so.
- Do not change the LOW rule from 4.1.0: a review with no HIGH and no MEDIUM passes; LOW is listed.

## Why

sdd-flow ties or beats plain Claude Code on hidden tests but loses on the blind judge's size, scope and fit scores
on every evaluated task. The code reviews are told not to look at organization, patterns or fit, and the one size
check (files outside the brief's footprint) may not raise a finding. Maintainability is not a review criterion.

## What to change (decided; do not reopen)

1. **Remove the exclusions** in `bodies/code-review.md`: the "ONLY IF ABOVE CRITERIA MET" gate on code quality,
   and from "What NOT to Focus On" the items on coding style, architectural patterns not in the specification,
   and code organization. Keep "premature optimization". Rework "Can every line trace to a specification
   requirement?" so it no longer reads as the test of a good change.
2. **Add a fit-and-size check** to the slice review (`bodies/slice-review.md`, 4b), the whole-feature code
   review (`bodies/code-review.md`, 4b) and the implementation critical review (`bodies/critical-review.md`
   §4, 4d). Its questions:
   - Does the change match the surrounding code — style, naming, helpers, patterns, layering?
   - Does it reuse what exists, or duplicate a helper, type or pattern already in the code base?
   - Could it be smaller, or folded into existing code? Is there a layer, wrapper, option or abstraction the
     approved tier does not need?
   - Will the next person or agent who changes this code find it where they would look, and change it in
     one place?
   The reviewer reads the code around each changed area, not just the diff.
3. **A footprint overrun is a finding.** In the Design Brief Check (code review, and slice review Step 5.7), a
   changed file outside the brief's "What changes where" areas is a fit finding unless the spec records it as a
   departure from the brief. Remove "Informational only" and the line that it produces no findings.
4. **Grading:** a fit finding is MEDIUM when the change adds a file, a layer, or a duplicate of an existing
   helper (an out-of-footprint new file included); otherwise LOW.
5. **Fixer rule:** add to the scope-of-the-fix rule (`phases/implementation-whole-feature.md`, the blockquote
   near the top, which the per-slice fix round also uses): a fit finding is fixed by removing or merging code —
   reuse the existing helper, fold the file into the module it belongs to, drop the layer — never by adding
   code. Each fix round reports its net line change (added minus removed, `SDD/` left out) in its return.

## Where the check is defined

Define the check once and have the three reviews read it — a body may only read paths its prompt gives it
(`SKILL.md`). Follow the `references/test-integrity.md` pattern: a short `references/fit-lens.md` (target under
60 lines: the questions, the footprint rule, the grading, the fixer rule) passed by path to those three review
spawns and to the fix spawns, recorded in `SKILL.md`'s identifiers like TEST_INTEGRITY. If you find a smaller
way that keeps one definition and obeys the input rule, use it and say why.

## Rules

- `SKILL.md`'s three rules apply to every edit (a body's only inputs are its prompt's paths; every stop has a
  halt block, a resume rule and a diagram row; every slice state change has an owner). This change adds no stop.
- Update Key Principle 2 (or add one short principle) in `SKILL.md` so fit and size are named as review
  criteria. Keep it to one or two sentences.
- Update `references/second-model-review.md` only if the review prompts' inputs list changes there.
- Remove, don't relabel: no "before 4.2" notes, no compatibility text.
- The instructions should not grow by more than the new reference: report the size of `SKILL.md`, the three
  review bodies, and the phase files before and after.
- Do not modify the `sdd` plugin.
- Version 4.2.0 in both `agent-engineering/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`.
- Update `docs/sdd-flow-diagram.md` (the review boxes that say "design brief check", the stage table, the
  "Who reviews"/tests text where it lists what a review checks) and the repo `CLAUDE.md` tree comment for
  `references/`.
- Run the skill's tests: `python3 -m unittest discover -s agent-engineering/skills/sdd-flow/scripts/tests`.
- Get a Codex review of the uncommitted change (`codex review --uncommitted`, output to a file, read the last
  block), fix what is real, and say what you did not fix and why.
- Do not commit. Stop with the change uncommitted and report back.

## Done when

- No review body tells the reviewer to skip organization, patterns or fit, and none calls the footprint check
  informational.
- Items 1–5 are done; you can point to the file and line for each.
- The fit check is defined in one place and reached by path from the slice review, code review, implementation
  critical review and the fixers.
- Tests pass; the Codex review has been run and answered.
- Your report lists: items done, anything decided differently (with the reason), where the check is defined and
  why, sizes before and after, and Codex findings left open.

## After the change (the owner's check, not part of this task)

Re-run the whole-feature code review with the new body on eduKate SPEC-002's sdd-flow result
(`05ab2b4..c836c23`, `SDD/` left out) and compare its MEDIUM findings with the blind judge's named faults.
