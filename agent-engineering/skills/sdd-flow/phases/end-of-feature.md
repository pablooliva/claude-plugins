# Phase: Implementation — end of feature (Steps 4b–4j, both delivery modes)

Read with `phases/implementation-inputs.md` once the feature is implemented: after whole-feature 4a (`## Feature - Implemented`), or after the last slice's commit (per-slice end-of-feature cycle, `phases/implementation-per-slice.md`). The post-implementation steps (4b code review, 4c fixes, 4e.5 final check, 4f completion, 4h checkpoint, 4i commit, 4j announcement — there is no 4g; eval capture was removed in 3.0.0) are shared with per-slice's end-of-feature cycle.

Phase-execution and fix subagents carry the Safety-Net Rule + a fresh counter file + the `implementation-compact.md` compact body path. A review step run on the second model carries none of the three (`references/second-model-review.md` §3). Body paths are `SKILL_ROOT/bodies/<file>.md`, resolved absolute.

---

## 4b. Code Review Subagent  *(shared with per-slice end-of-feature)*

The one review of the whole feature's code before the final check: the specification-driven review and the adversarial pass in one report. Run it by the cycle's **review route** (`references/second-model-review.md`). On the Claude route, spawn an **`agent-engineering:sdd-critical-reviewer`** subagent (Opus). Either route is given:
- **Body:** `bodies/code-review.md`
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[YYYY-MM-DD].md`, the implemented code files (paths from IMPLEMENTATION-PLAN), **BRIEF** (`SDD/requirements/DESIGN-[###]-[feature-name].md`, with its approved revision and tier) for the review's `## Design Brief Check`, `BASE` = the `Base commit:` recorded under `## Feature - Implementing` (the check compares the files changed since it against the brief's footprint), **TIERS** (the tier standard resolved at Step 0) when the spec carries `tier:`, and — whenever the catalog is passed (below) — the panel review `SDD/.records/reviews/PANEL-SPEC-[feature-name]-[YYYYMMDD].md`, whose `AI Agent Security Findings` and `Abuse cases to cover` blocks the lens checks the code against.
- **Outputs:** `SDD/.records/reviews/REVIEW-[###]-[feature-name]-[YYYYMMDD].md`.
- **Tracing:** the **tracing inputs**. With `tracing: on` the body's **Tracing Lens** runs the application's trace run, writes TRACE_TREE, and compares it with every marked node of the spec's planned call graph (`SCOPE = FEATURE`); a HIGH lens finding is a rejection criterion. With `tracing: off` the body records that the lens was skipped.
- **Evals:** the **evals inputs**. With `evals: on`, first make **the eval run of record** (`phases/implementation-inputs.md`) at `SCOPE = FEATURE`, `iter 0`, then pass its eval run line and EVAL_RESULTS. The body's **Eval Check** reads that run and the eval files against every case of the spec's `### Evals`; a HIGH finding of it is a rejection criterion. With `evals: off` the body records that the check was skipped.
- **Tests:** **TEST_INTEGRITY**. The body's **Test Integrity Lens** runs in every cycle: it checks that the tests are real and that neither they nor the code were bent to get a green run; a HIGH lens finding is a rejection criterion.
- **Fit:** **FIT** — the body's **Fit Lens** and its Design Brief Check; a MEDIUM rejects like any other.
- **Task:** Specification-driven review (70% spec alignment, 20% context engineering, 10% test alignment), then the body's **Adversarial Pass**, which runs in every cycle: how would this code be broken? The body's **Agentic-Surface Lens** fires when the spec's `agent_security:` gate is open — pass the resolved **CATALOG** path and the resolved gate value (`agent_security: true` or `agent_security: auto`) in the prompt whenever `agent_security:` is `true` or `auto`/absent. A HIGH lens finding is a rejection criterion. Pass `SCOPE = FEATURE` and `ITER = 0`; the review appends `## Review FEATURE iter 0 - APPROVED | REJECTED (h HIGH, m MEDIUM, l LOW)` to `progress.md`. Apply **Risk-Tiered Review Depth** — read each `MODULE-XXX`'s `Risk:` field and scale internal-review depth: `high` → full internals; `medium` → default; `low` → tested-boundary only. Escalate any tier that looks misclassified (e.g., a `low`-tagged module touching irreversible state) and flag it in the Module Review Log.

---

## 4c. Address Code Review Findings  *(shared with per-slice end-of-feature)*

Spawn an **`agent-engineering:sdd-workhorse`** fix subagent:
- **Inputs:** `SDD/.records/reviews/REVIEW-[###]-[feature-name]-[YYYYMMDD].md`, `SDD/requirements/SPEC-[###]-[feature-name].md`, the IMPLEMENTATION-PLAN path, the implemented code files, **FIT**.
- **Outputs:** updated code and tests, updated IMPLEMENTATION-PLAN, "Findings Addressed" appended to the review.
- **Tracing:** the **tracing inputs** — TRACE_TREE being the file 4b wrote, or none when it wrote none — and, with the gate on, the fix rule.
- **Evals:** the **evals inputs** — the eval run line and EVAL_RESULTS being those 4b was given — and, with the gate on, the evals fix rule. No run of record follows this fix: the final check (4e.5) makes one before each of its reviews, and that is where an eval finding of 4b is checked again — it is never closed on the fixer's own run. So for an eval finding, the fix means what the evals fix rule says: at most three eval runs of the fixer's own, and a hard case that still fails after them comes back named in its return. The flow goes on to the final check with it all the same; the final check is what stops on it.
- **Task:** Fix every HIGH and MEDIUM finding — spec misalignment, missing edge/failure handling, test gaps, silent failures, security holes, and everything else — with the scope-of-the-fix rule. (No `## Fix FEATURE` marker here — the final check, 4e.5, runs after all fixes.)

---

## 4e.5. Final Check  *(shared with per-slice end-of-feature; always runs)*

The last review of the feature, after every fix has landed, run by `bodies/final-check.md`: the **security verification** (SECURITY), the whole test suite, the **last-look test checks** (TEST_INTEGRITY §5), and — with their gates on — the **Tracing Lens** and the **Eval Check**. The trace and eval checks stay in this one review because both must read a run made after the last fix, and this is the one review after it: one loop, one cap, and one stop at the end of the feature, instead of two. With both gates off, only the security verification, the suite, and the last-look checks run.

On first entry — coming from 4c — the orchestrator appends `## Final Check - Started` (the phase-detection anchor for this step); on exit to 4f it appends `## Final Check - Complete`. A run resumed from `## Awaiting Final Check Resolution` re-enters at step 1 **without** writing the anchor again: that halt block is its boundary (`phases/rare/resume.md`). Loop, starting at `k = 1`:

1. **Eval run of record (`evals: on` only).** Make **the eval run of record** (`phases/implementation-inputs.md`) at `SCOPE = FEATURE`, `iter <k>` — so the run is of the application as the last fix left it. Its stop, `## Awaiting Eval Run`, can fire here as before any review, and costs no fix round.
2. **Review.** By the cycle's **review route** (`references/second-model-review.md`) — on the Claude route, an **`agent-engineering:sdd-workhorse`** subagent with the Safety-Net Rule, a `Reads: 0/15` counter, and `implementation-compact.md` — run `bodies/final-check.md`, passing `SCOPE = FEATURE`, `ITER = k`, the SPEC, the IMPLEMENTATION-PLAN path, `BASE` (the `Base commit:` under `## Feature - Implementing`), **SECURITY**, **TEST_INTEGRITY**, and the two gate lines; when the spec's `agent_security:` gate is `true` or `auto`/absent, **CATALOG**, the resolved gate value, and the panel review `SDD/.records/reviews/PANEL-SPEC-[feature-name]-[YYYYMMDD].md`; the **tracing inputs** (TRACE_TREE = this iteration's `…-iter<k>-…` file) and the **evals inputs** (that run's eval run line and EVAL_RESULTS) when their gates are on. When iteration k has both snapshots of step 3, also pass `SNAPSHOT` and `FIXED` — its *before fix* and *after fix* SHAs — and `PREVIOUS REVIEW`, the final-check review of iteration k − 1. It writes `SDD/.records/reviews/FINAL-CHECK-FEATURE-[feature-name]-iter<k>-[YYYYMMDD].md` and appends `## Review FEATURE iter <k> - APPROVED | REJECTED (h HIGH, m MEDIUM, l LOW)`. **APPROVED — no HIGH and no MEDIUM — goes to 4f**; its LOW findings are listed, not fixed.
3. **Fix.** Spawn an **`agent-engineering:sdd-workhorse`** fix subagent with that review, the SPEC, the IMPLEMENTATION-PLAN path, `BASE`, **SECURITY**, **TEST_INTEGRITY**, **FIT**, the scope-of-the-fix rule, and the tests rule; with `tracing: on`, the **tracing inputs** (TRACE_TREE = the file that review wrote, or none when it wrote none) and the tracing fix rule; with `evals: on`, the **evals inputs** (that review's eval run line and EVAL_RESULTS) and the evals fix rule. It fixes each security finding as SECURITY §4 says — a code change and a proving test whose failure it shows in a scratch copy, recorded under `## Security Proofs` — and appends `## Fix FEATURE iter <k+1> - Complete`. Around it the orchestrator takes the two snapshots of `phases/implementation-per-slice.md` → 4c, *The snapshots*, by the same command and rules, at `FEATURE` scope: `## Snapshot FEATURE iter <k+1> - before fix <sha>` immediately before the fix spawn, and `## Snapshot FEATURE iter <k+1> - after fix <sha>` immediately before the review of iteration k + 1 (after its eval run of record). The boundary is the latest `## Final Check - Started`, or the latest `## Awaiting Final Check Resolution` after it; the first iteration after such a block has no snapshots and is reviewed in full. Then `k = k + 1` and repeat from 1. The review that follows is what re-checks every fix: no finding is closed on the fixer's word, and the fixer's own eval run closes nothing.

**Cap: at most 2 fix rounds** — verify → fix → verify → fix → verify — counted as the `## Fix FEATURE iter <k>` lines after the boundary above. When the review that ends the second round is still `REJECTED`, the orchestrator appends this halt block and stops:

```markdown
## Awaiting Final Check Resolution

The final check for SPEC-[###] still has open findings after 2 fix rounds: <h> HIGH, <m> MEDIUM.
Latest review: <FINAL-CHECK path>[   Latest trace tree: <TRACE-TREE path, or `none written`>][   Latest eval results: <EVAL-RESULTS path, or `none written`>]
Resolve the findings (or amend the SPEC), then run `/sdd-flow continue` — the flow runs the final check again from a fresh review.
```

The bracketed parts are written only when their gate is on. A hard eval case that still fails reaches the user through this stop (EVALS §8).

---

## 4f. Implementation Completion Subagent  *(shared with per-slice end-of-feature)*

Spawn an **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/implementation-complete.md`
- **Inputs:** `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[YYYY-MM-DD].md`, `SDD/requirements/SPEC-[###]-[feature-name].md`, **SECURITY**, **FINAL_CHECK** — the last final-check review, the one whose marker let the loop end — **REVIEWS** — every review document of this feature that has a `LOW Findings (listed, not fixed)` section (the code review or the slice reviews, the critical reviews, the final checks; the orchestrator names them, the body lists no folder) — and, when the spec carries `tier:`, **TIERS** and **TIER_PLAN** (`SDD/flow/TIERS-[feature-name].md`; on a next-tier cycle the path recorded at Step 0).
- **Tracing:** the gate line. With `tracing: on` also **OBS_RECORD** and the final **TRACE_TREE** — the file FINAL_CHECK's review wrote. The body runs no trace run and no script: it reads the two files to fill the summary's `## Monitoring & Observability` and to check that the final check left no tracing finding open.
- **Evals:** the gate line. With `evals: on` also **EVALS**, and the eval run line and **EVAL_RESULTS** that FINAL_CHECK read. The body makes no eval run: it reads the results to fill the summary's `### Evals` part — the `Sign-off requirements` table the 4h checkpoint shows the user is in it — and to check that the final check raised no eval finding.
- **Completion never rests on a check made before the code or the tests last changed.** The body changes no code and no test: an item that needs either — a failing test, a missing test, an unfinished requirement — comes back in its return as incomplete. The orchestrator does not re-spawn it and does not spawn a fix: it appends `## Awaiting Final Check Resolution` with the first line `Completion for SPEC-[###] found items that need code or tests changed after the final check: <the items, one line>.` and that block's usual second and third lines, and stops. `/sdd-flow continue` takes that block's rule: the final check again, and only then 4f. This takes the place of the retry in Error Handling (`phases/protocols.md`) for that one return; a completion spawn that fails for any other reason is handled there as before.
- **Outputs:** updated IMPLEMENTATION-PLAN, updated SPEC, updated tier plan (this tier marked shipped; deferrals added during reviews or implementation copied in), `SDD/implementation/summaries/IMPLEMENTATION-SUMMARY-[###]-[YYYY-MM-DD_HH-MM-SS].md`, append `progress.md`.
- **Task:** Finalize all documentation, copy the final check's security table and every review's LOW findings into the summary, validate all requirements are met, create the implementation summary, capture glossary deltas (execute inline).

---

## 4h. Commit Checkpoint (stops only for a sign-off or a growth overrun)  *(shared)*

**When it stops.** Only when a sign-off is asked for, or the feature is over its growth budget; otherwise go straight to the commit (4i). An unresolved finding never reaches this step: it stopped the flow earlier (the fix-loop and final-check halts).

**The growth check.** Run `python3 "$SKILL_ROOT/scripts/growth.py" --base <BASE> --brief SDD/requirements/DESIGN-[###]-[feature-name].md`, `BASE` = the `Base commit:` under `## Feature - Implementing`. The feature is **over its growth budget** when the third line it prints is `Over budget: yes` — source or test lines added are more than one and a half times the estimate the user approved with the brief. Keep the three lines for this step and for 4j. Tests per source line, at the end of the first line, is shown and never stops the commit. Exit 3 (the brief has no budget) is never over; 4j says the budget was missing. Exit 2 is a failed script: tell the user, and go on as not over.

**A sign-off is asked for** when the evals gate is on and the SPEC has at least one line that starts `- [ ] **Sign-off: ` — the orchestrator runs `grep -E '^- \[ \] \*\*Sign-off: ' <SPEC>` and reads no more of the spec for it. Each such line names a requirement about what the model says that no rule can check: a judge model scored real outputs, and only a person's answer meets it (EVALS §9). With the gate off the lines are not looked for.

When it stops, append this block to `progress.md` — with the `Sign-off asked for:` line only when a sign-off is asked for, and the `Over budget:` line only when the feature is over its budget — then pause with the message below:

```markdown
## Awaiting Commit Approval

Implementation of SPEC-[###] is complete and uncommitted, waiting for your answer (4h).
Summary: <IMPLEMENTATION-SUMMARY path>
Sign-off asked for: <the requirement IDs on the lines found>   Eval results: <the final EVAL_RESULTS path — the one 4f was given>
Over budget: <the growth script's first line>
```

> **Implementation complete — your answer is needed before the commit.**
> Brief check: [whole-feature: outside the approved footprint: none | list] [per-slice: N of M slices stayed inside the approved footprint; exceptions: …]
> [If the summary's `### LOW Findings (listed, not fixed)` lists any:] LOW findings, listed and not fixed: [n] — in the summary under `### LOW Findings (listed, not fixed)`.
> [Over budget only — the growth part:] **The feature is over the growth budget you approved:** [the growth script's first line]. [Its second line, when it names files.] The code is reviewed and the tests pass; this asks whether the size is acceptable. Answering no leaves it uncommitted; the flow does not shrink it for you.
> [Sign-off only — the sign-off part:] No rule can check the requirement(s) below, so a judge model scored what the application really answered. A score is a measurement, not a verdict — read the outputs before you answer.
> [The `Sign-off requirements` table and the `Judge:` line of the implementation summary's `### Evals` part, as written there: one row per judged case, lowest score first.]
> Every run's output, with the judge's sentence: `[the final EVAL_RESULTS path]` → `## Judged cases`
> [Sign-off asked for:] **Commit, and do you accept [the requirement IDs] on these outputs?** (y/n) [Over budget only:] **Commit at this size?** (y/n) [Both: one question naming both — a yes accepts both.]

When a sign-off is asked for, the orchestrator takes the table and the line from the summary document — the file, not a subagent's return — and never opens the eval results: they hold what the model answered, and reading them is the user's part here. A summary with no such table, when a sign-off is asked for, is a completion that did not finish its work: handle it as a failed 4f spawn (Error Handling, `phases/protocols.md`), never by asking without the scores. When the checkpoint stops only for the growth budget, the sign-off part is left out and no table is looked for.

Wait for the answer before committing.

- **y** → first append, to `progress.md`, `## Sign-off - <the requirement IDs> accepted at 4h` when a sign-off was asked for, and `## Growth - accepted at 4h: <the growth script's first line>` when the feature was over its budget — one line each. One yes accepts every requirement listed and the size; there is no accepting some of them. Then 4i. Its `## Implementation - Committed` line answers the block.
- **n** → nothing is committed and nothing is accepted; stop with the block pending. The user may change the code or the artifacts by hand first; a change that touches a security rule's guard is theirs to raise — the flow does not re-review after 4h. Nor does it make an eval run after 4h: the scores this checkpoint shows stay those of the final check, whatever is changed afterwards, and a change the user wants scored is one they run themselves, with the eval command in `SDD/OBSERVABILITY.md`.
- **Session ends with no answer** → the block is still the latest one.

When the checkpoint is shown again, the growth check runs again: a feature that is no longer over its budget, with no sign-off asked for, goes straight to 4i.

In the last two cases `/sdd-flow continue` re-shows this checkpoint (`phases/rare/resume.md` → `## Awaiting Commit Approval`).

**Brief-check line** (here and in 4j). Whole-feature: quote the `## Design Brief Check` section of the 4b review document (the file, not a subagent's return). Per-slice: the count across slice reviews (`phases/implementation-per-slice.md` → end-of-feature 4h). Omit the line when the feature has no design brief.

---

## 4i. Commit Implementation  *(shared)*

**Task mirror — in review (both delivery modes).** For a tiered spec, as soon as 4f returns — before the 4h stop when there is one, and always before this commit — run `python3 "$SKILL_ROOT/scripts/tier-mirror.py" sync <TIER_PLAN> --in-review <tier>`; record and report the result per `SKILL.md` → Tier Task Mirror. Running it before the commit means any task key it writes into the tier plan is committed here.

The **orchestrator** runs the commit per `commands/commit.md` — all implementation code, tests, and SDD artifacts outside `SDD/.records/` (the IMPLEMENTATION-PLAN, the summary, the updated tier plan, any glossary change). Reviews, trace trees, and eval results are records and are not committed. No co-author attribution. When 4h wrote a `## Sign-off - ` line for this feature, the message body carries one line more — `Sign-off: <the requirement IDs> accepted by the user on <the final EVAL_RESULTS file name>.` — so the commit itself records that a person accepted them; the results file itself is a record and stays out of the commit. If nothing is uncommitted — a resumed run whose commit had already landed — make no commit.

**Then append `## Implementation - Committed` to `progress.md`** — one line, the commit's SHA (or `already committed`). It is the phase-detection marker that the code is in history. `Implementation Phase - COMPLETE`, written by the completion subagent at 4f, does not say so.

If `progress.md` exceeds ~500 lines, rotate it now (`phases/rare/rotation.md`).

---

## 4j. Completion Announcement  *(shared)*

The flow ends with this short report — no stop came before the commit unless a sign-off was asked for, so this is where the user learns what happened:

> **SPEC-[###] is done and committed** (`[short SHA of the 4i commit]`).
> Shipped: [what was built, two lines at most, from the implementation summary][ — **Tier [N]**, if the spec carries `tier:`].
> Deferred: [each row of the spec's `## Deferred to Later Tiers`, one line each, and anything the summary records as deferred — or "nothing"].[ If the spec carries `tier:`: Tier plan: `SDD/flow/TIERS-[feature-name].md` — use this tier, note what you find under its `## Feedback`, then run `/sdd-flow --next-tier [feature-name]` when you want more.]
> LOW findings, listed and not fixed: [each line of the summary's `### LOW Findings (listed, not fixed)`, one line each — or "none"].
> Not proven: [the harvested-cases line below, when it applies — or "nothing"].
> Diff: [the output of `git diff --shortstat <BASE> HEAD`, with `BASE` = the `Base commit:` under `## Feature - Implementing` — files changed, lines added and removed by the whole feature].
> Growth: [the growth script's first line from 4h, and its second when it names files — or "the brief had no growth budget"][ — accepted by you at 4h, when 4h wrote a `## Growth - ` line].
> Brief check: [the 4h brief-check line].
> [If 4h wrote a `## Sign-off - ` line:] Accepted by you at the commit checkpoint: [the requirement IDs], on the scores and outputs in `[the final EVAL_RESULTS path]`.
> [Part of `Not proven`, if this cycle's IMPLEMENTATION-PLAN has a `Harvested, before any change:` line that does not end `failed`:] Harvested cases not seen to fail before the change made for them: [each such case, with what its line says]. A stand-in that passed, or only got scores, may not reproduce what its trace showed — a later cycle can rewrite it, or keep it as a guard (`references/evals.md` §2).
> [If the spec carries `tier:` and the application has `SDD/OBSERVABILITY.md`:] To turn a wrong answer from using this tier into a case for the next one: mark its trace in Opik, then run `/eval-harvest`.
> [If ADRs were captured:] ADRs written: [list]. See `SDD/adr/README.md`.

**Task mirror — done.** For a tiered spec, before the announcement run `python3 "$SKILL_ROOT/scripts/tier-mirror.py" sync <TIER_PLAN> --shipped <tier>`: the tier's sub-task becomes done and gets one comment — what shipped and what to look at, taken from the tier plan. Add to the announcement: `Tasks: [tier sub-task key] done; leave feedback as comments on [next tier's key] — the next cycle copies them into the tier plan.` (or the mirror's `OFF` / `ERROR` line, when that is what it returned). Normally this run writes nothing to the tier plan — the keys were saved at the design gate. If an earlier mirror point failed and this one had to create tasks, the tier plan now has new keys in it: when `git status --porcelain -- <TIER_PLAN>` shows a change, commit that one file (per `commands/commit.md`, message naming the tier plan and SPEC) **before** the announcement, so "all artifacts committed" is true.

After the announcement, append `## Feature - Done` to `progress.md` — one line, the spec path. It is the marker that the flow has nothing left to do for this feature.

Then perform the **feature-completion rotation** (`phases/rare/rotation.md`): archive this feature's full progress history — its `## Flow Started - ` record and everything after it — to `SDD/.records/progress-archive/` and leave the one-line `Finished:` summary in the live `progress.md`.
