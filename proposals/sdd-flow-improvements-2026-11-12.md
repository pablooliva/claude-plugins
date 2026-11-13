# sdd-flow improvements — what is still pending (as of 4.2.0, 2026-11-12)

The one list of suggestions for improving sdd-flow that are not yet built. Everything already shipped is named
once under "Current state" and not discussed again. The detailed record behind each decision stays in the earlier
notes: `sdd-flow-simplification-2026-11-12.md`, `enforcement-site-proof-2026-11-12.md`,
`review-criteria-2026-11-12.md`.

Status words: **Decided** (owner agreed, not built), **Open** (proposed, not decided).

## Goal

Correct, maintainable code that fits the existing code and does not grow beyond what was asked, delivered in tiers
and slices small enough for the owner to try and judge. Cost is not the criterion.

**Maintainable** means the next change is easy: the next person or agent finds the code where they would look,
changes it in one place, and breaks nothing unrelated. It is built from modules that hide their detail behind a
small interface (the depth standard, `improve-codebase-architecture/references/codebase-design.md`). It does not
mean preparing for changes nobody has asked for: a layer or option added "for later" makes the code harder to
change, not easier (TIERS, "build nothing ahead"). It is judged by how the next tier's cycle goes, the follow-up
change test below.

## Why (evidence in brief)

Sources: `sdd-flow-eval/SDD/research/FINDINGS-001-plain-vs-sdd-flow-2026-11-08.md` and
`FINDINGS-002-edukate-history-review-2026-11-10.md`.

- sdd-flow tied or beat plain Claude Code on hidden tests, and lost on size, scope and fit every time.
- The small benchmark tasks are the wrong size for sdd-flow. eduKate is the application-scale evidence, and it
  points the same way:
  - SPEC-002 was +4,708 lines in 22 files, against plain's +1,150 in 9.
  - Later cycles read only the ADRs, the glossary and the tier plan; they did not reuse specs, designs or reviews.
  - About 290,000 lines of process records sit in `SDD/`.
  - Tests are 4× the source code.
  - The orchestrator took 69% of the cost.
- Confound: in the benchmark plain's code was written by Opus, sdd-flow's by Sonnet subagents.
- Not yet measured: whether later changes are easier on sdd-flow's code; whether the owner follows slices and tiers
  more easily; whether the tracing and evals gates caught regressions.

## Current state (shipped — not to be re-proposed)

- **Framing:** sdd-flow is the default for application development (tiers, slices, design gate, tracing, evals);
  sdd-lite is for changes with no tier and no model check, and does not get tracing or evals.
- **4.0.0:** no modes; stops only for owner decisions; a pause after every slice for trying it; Codex is the only
  second model, with the Claude fallback; whether the tracing foundation exists is settled at brief approval.
- **4.1.0:** the site proof is replaced by one security verification at the end of the feature (4e.5), at most two
  fix rounds; LOW findings are listed, not fixed; mutation checks run in a scratch copy.
- **4.2.0:** every code review runs the Fit Lens (`references/fit-lens.md`): match, reuse, size, next change. A
  file changed outside the brief's footprint is a finding unless the spec records it as a departure. A new file,
  layer or duplicate helper is MEDIUM. A fit finding is fixed by removing or merging code, and every fix round
  reports its net line change.

- **4.3.0 (step 2 below, uncommitted, Codex-reviewed):** the design brief names every new file by path, lists what
  the change builds on (`## Builds on`), and sets a growth budget the owner approves; a new file the brief does not
  name is a fit finding; the panel reviews only the areas the change touches (at most three, plus `agent-security`
  and `slice-integrity`) and proposes scope beyond the brief as additions instead of adding it; the flow always stops
  after the spec (3g) — departures, additions, `/simplicity-challenge <spec> --brief <brief>`, then `approve`, `cut`
  or `accept`; `scripts/growth.py` measures growth at each slice pause and stops the final commit (4h) above 1.5× the
  budgeted source or test lines.
  - Decided 2026-11-12: `--brief` is an option of `/simplicity-challenge`; the budget holds source lines, test lines
    and new files, with a 1.5× stop; every new file is named and a `Builds on` list is kept; the panel is narrowed
    and its additions go to the owner.

## Decided, not built

### No backward compatibility (decided 2026-11-12)

sdd-flow keeps nothing that exists only for runs started on an older version, older files, or old command lines.
A cycle in progress finishes on the version that started it (already the rule since 4.0.0). What goes:

- **Removed-flag handling:** `SKILL.md` → Arguments ("Removed flags (4.0.0) are ignored") and `phases/setup.md`
  step 1. A removed flag would then be read as task text.
  - **Dependency:** the benchmark harness still starts runs with `--auto --skip-clarify --reviewer codex`
    (`sdd-flow-eval/replay/record.py:19`). Update it before or with this change.
- **Legacy 1.x layout detection** and its halt message (`phases/protocols.md` → Old layout detected).
- **Resume rules for older runs:** "in a run started before 3.5.1" and "*Runs started on 3.5.0*" (three places), "a
  flow planned before the design gate existed", and the `## Awaiting Tracing Decision` alias (3.8.0–3.11.0), all in
  `phases/protocols.md`; the
  catch-all's "such as one left by an older version" wording (`phases/protocols.md`). Keep the catch-all itself: it
  also guards a halt this version has no rule for.
- **Older file shapes:**
  - `bodies/slice-review.md`: one review document per day, before 3.14.0.
  - `phases/planning.md` 3g: a spec written before the design gate had no brief.
  - `bodies/code-review.md`: "legacy" as a reason for a spec with no `## Modules` section. Config-only changes stay.
  - `bodies/planning.md`: `delivery_mode` absent means whole-feature "for backward compatibility". The planner
    always writes the field; a spec without it is an error.
- **Shared commands:**
  - `commands/continue.md`: looking in `SDD/orchestration/` "where older versions wrote", and the pre-3.5.1
    `/adhoc-compact` section names.
- **README guidance for old runs:** the "Runs started before …", "A run handed off before …", "Runs already in a fix
  loop …" and "A cycle started before 3.9 …" paragraphs, and the "Removed flags are ignored" note. Release history
  stays; only advice for running an old cycle goes.
- **Not in scope:** "with the gate off a cycle must behave exactly as it did before 3.8.0 / 3.12.0" (CLAUDE.md and
  the gate rules). That is a rule against regressions for cycles without tracing or evals, not support for old runs.

## Open — needs an owner decision

### While building: extend before adding

- **Implementer rule: change existing code first.** A new function, file or layer gets a one-line reason in the
  slice record. The Fit Lens now catches these in review; this rule would prevent them before review, so fewer fix
  rounds.
- **Fix-round cap of two** for the slice review loop and the spec panel loop (both three today; the final check is
  already two). After that, only HIGH findings that are real bugs are fixed; the rest go to the owner.
- **One consolidation pass at the end of the feature** that merges duplicate structure across slices and removes
  scaffolding. Partly covered: the implementation critical review (4d) runs the Fit Lens over the whole feature, but
  as a review that finds problems, not a pass that removes them.
- **Consider Opus for the implementer.** It removes the model confound and fits "cost is not the criterion".

### Tests: protect behaviour, not shape

- **Tests check what a user or caller can see.** No tests pinning exact wording unless the wording is the
  requirement, and no tests of test helpers unless the helper needs them. `references/test-integrity.md` says
  nothing on either today.
- **The test-to-code line ratio is shown at the gate** as a warning, not a limit.

### Fewer steps

- **Merge the two end-of-feature code reviews** (4b code review and 4d implementation critical review) into one
  Codex review. Both read the same code and both run the Fit Lens; the final check (4e.5) is a third review of it.
- **Drop the per-slice retrospective and learnings ledger,** keeping only the re-plan line, in the slice review.
  All 37 eduKate retrospectives said "Re-plan: no".
- **Drop the adversarial review of research (2c/2d).** Research is not reused, and the owner checks the design at
  the gate. Check first whether research found what gave tornado its two extra hidden tests. If it did, keep it.

### Records and the orchestrator

- **Keep process records out of the repository.** Reviews, counters, reviewer and subagent call logs, eval results,
  trace trees and compaction files go git-ignored or into thread storage. The brief, spec, ADRs, glossary, tier plan
  and summary stay in `SDD/`.
- **Slim the orchestrator.**
  - Subagents return a verdict line and a path.
  - Target about 15k tokens of core instructions; `SKILL.md` and the phase files are about 214 KB today, roughly
    53k tokens.

## How to tell whether it works

1. **Fit Lens check — done 2026-11-12.** The whole-feature code review (4b) was run on Codex over eduKate SPEC-002's
   sdd-flow result (`05ab2b4..c836c23`, a throwaway clone), once with the 4.1.0 body and once with 4.2.0; same
   inputs, tracing and evals off.
   - **4.1.0:** 1 MEDIUM, about missing prompt records for the first four slices (a process finding, not code). The
     `.gitignore` line was noted as "informational only".
   - **4.2.0:** 1 MEDIUM fit finding: `tests/test_instructions.py` duplicates the route-test setup and request helper
     of `tests/test_app.py`; fold it in and delete the file. 1 LOW: the `.gitignore` line, outside the footprint.
   - **What it did not catch: the size.** The 4.2.0 review judged the page's structure "the approved design, rather
     than an unsolicited abstraction" and found nothing else. The wording table and its checks are spec requirements
     (REQ-020/021), and every changed file but `.gitignore` sits in an area the brief listed. Its `tests/` row admits
     any test file.
   - **Reading:** the Fit Lens catches what does not fit the code around it (duplicates, strays). It cannot push back
     on size the spec and brief approved. That has to happen before code: the simplicity stop (3g), the growth budget,
     and a footprint finer than `tests/`.
   - One run per version; Codex varies between calls. The expectation that `.gitignore` would be MEDIUM was wrong by
     4.2.0's own grading: an existing file changed is LOW.
   - Reviews and prompts: `~/.bb/thread-storage/thr_sb4yjmjp9s/fitcheck-2026-11-12/`.
2. **Did evals earn their place?** Read SPEC-007's records for regressions the eval run caught.
3. **An application-scale comparison.** Build a small app with a model in it to Tier 1 and then Tier 2, once with
   sdd-flow and once with plain Claude Code, from the same owner answers. Measure:
   - acceptance tests the owner writes before either run;
   - for each slice or step, the diff size and the owner's time to review it and understand it;
   - the Tier 2 cycle as the follow-up change test: its cost, its diff, and what it breaks from Tier 1;
   - regressions the eval run caught, with plain given the same eval cases.

## Suggested order

Check 1 showed that the code review cannot push back on size the spec and brief already approved, so the size work
before code comes first.

1. ~~Run check 1~~ — done.
2. ~~**Size before code, one release**~~ — built as 4.3.0. It covered:
   - the simplicity stop after the spec (3g), settling its open point;
   - the growth budget in the brief, shown at 3g and at every slice pause, and checked against the diff at the final
     commit (4h);
   - the reuse map in the brief;
   - a footprint finer than whole folders: name the test files the change adds, not just `tests/`;
   - panel narrowing, so the spec does not grow before the stop sees it.
3. ~~**Remove the backward-compatibility clauses.**~~ — built as 4.4.0, after the harness in `sdd-flow-eval` stopped
   passing the removed flags. Beyond the list above it also removed the 3.8.0/3.12.0 gate-line defaults, the pre-3.12.1
   handoff wording, and the pre-3.14.0 review-document shape. Kept: the pre-3.14.4 bare requirement IDs in an
   application's `evals/cases.jsonl` (`references/evals.md`), since those lines are application data that is never rewritten.
4. ~~**Size while building**~~ — built as 4.5.0 (owner decisions 2026-11-12): implementers get the brief's
   `## Builds on` and named new files and follow `fit-lens.md` §5; the implementer runs on Opus; fix-round cap of two
   for the slice loop and the spec panel; test rules 5–6 in `test-integrity.md` with T7 findings; tests per source line
   in `growth.py`'s output. Not built: the end-of-feature consolidation pass (left to step 5's review merge).
5. **Fewer steps and a slimmer orchestrator** — decided 2026-11-12, to be built in this order, each its own release
   with a Codex review:
   - ~~**5a (4.6.0), fewer steps**~~ — built as 4.6.0 (the merged review is `bodies/code-review.md` with an
     Adversarial Pass, on Codex or the Opus reviewer; per-slice runs it once after the last slice; the
     `Acceptance Check Passing` row state went with the retrospective). Decided: merge 4b and 4d into one end-of-feature code review (Codex); drop the per-slice
     retrospective and the learnings ledger, the slice review ending with one `Re-plan: yes|no — why` line; drop the
     research review (2c/2d). Check done: neither of tornado's two extra hidden tests came from the research review —
     one came from the spec panel with the owner's answer (truncation raises in `flush()`), one from the panel alone
     (`flush()` refuses with a pending tail); inferred from the diffs, no per-test results were recorded.
   - **5b (4.7.0), records out of git:** reviews, counters, call logs, eval results, trace trees and compaction files
     go to a git-ignored folder under `SDD/` (e.g. `SDD/.flow/`); brief, spec, ADRs, glossary, tier plan and summary
     stay committed.
   - **5c (5.0.0), slim orchestrator:** rewrite `SKILL.md` and the phase files to ~15k tokens read at every step, rare
     cases (handoffs, halts, re-plans) in files read only when they happen; the owner tries it on a real feature
     before it reaches main.

   Original item: **Fewer steps and a slimmer orchestrator:** merge the two end-of-feature code reviews, drop the per-slice
   retrospective and the research review, keep process records out of the repository, shorten the instructions.
6. **Checks.** Check 2 (did evals catch regressions in SPEC-007) only reads records, so run it whenever convenient;
   its answer decides whether the evals gate stays as it is. Check 3, the application-scale comparison, after step 5.
