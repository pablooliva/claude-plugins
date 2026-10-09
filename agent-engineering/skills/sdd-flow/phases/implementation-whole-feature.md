# Phase: Implementation — whole-feature mode (Steps 4a–4j)

Reached at Step 4 when the spec's `delivery_mode:` is `whole-feature` (the default, and the PARSE default when the field is absent). If `delivery_mode: per-slice`, do NOT run these steps — read `phases/implementation-per-slice.md` instead.

Phase-execution and fix subagents carry the Safety-Net Rule + a fresh counter file + the `implementation-compact.md` compact body path (blind site counts: `site-count-compact.md`). Implementation-chunk and blind-site-count counters use `Reads: 0/20`. Body paths are `SKILL_ROOT/bodies/<file>.md`, resolved absolute. **STANDARD** = `SKILL_ROOT/references/enforcement-sites.md`, resolved absolute, passed to every implementation, site-count, review, fix, and completion spawn.

**Tracing inputs.** The tracing gate is the latest `## Gates - tracing: on|off` line after the latest `Planning Phase - COMPLETE` in `progress.md` (`phases/planning.md` → 3c); a cycle with no such line has it `off`. Every implementation, code-review, verification (4e.5 step 3), fix, and completion spawn below is passed the gate as the line `tracing: on` or `tracing: off`. With `tracing: on` it is also passed these, resolved absolute (the completion spawn: OBS_RECORD and the final TRACE_TREE only — it runs nothing):

- **TRACING** — the tracing standard, resolved at Step 0.
- **OBS_RECORD** — `SDD/OBSERVABILITY.md`, the application's observability record: it names the trace run, the span file it writes, the env file, and the entry-point test.
- **TRACE_TREE_SCRIPT** — `SKILL_ROOT/scripts/trace-tree.py`.
- **LENS** — `SKILL_ROOT/references/tracing-lens.md`, the one definition of the review's Tracing Lens (review and fix spawns).
- **TRACE_TREE** — the file a review writes the rendered call tree to: `SDD/reviews/TRACE-TREE-FEATURE-[feature-name]-[YYYYMMDD].md` for the 4b review, and `SDD/reviews/TRACE-TREE-FEATURE-[feature-name]-iter<k>-[YYYYMMDD].md` for the 4e.5 verification of iteration `k` — one file per verification, so the tree a review judged is never overwritten by a later one. A fix spawn is given the tree written by the review it answers — **only when that file exists** once the review has returned (the orchestrator checks the path; it never opens the review to find out). A review writes no tree when it ran no lens (4e, after the critical review, in per-slice mode), when its trace run failed or could not be rendered, or when the test suite did not pass at 4e.5; the fix spawn is then given no TRACE_TREE and told so in one line, and the review's finding carries the failure message it works from. A continuation of that fix spawn is given the same. The completion spawn is given the tree of the last 4e.5 verification — the final one.

With `tracing: off` none of the five is passed and the bodies do nothing about tracing. The blind site count is never passed any of them, nor the gate: its allowlist is unchanged. TRACE_TREE_SCRIPT and LENS ship inside this skill; one that is missing is a broken install — halt and tell the user. **With the gate on, embed this fix rule verbatim in every fix prompt (4c, 4e, 4e.5 step 4, per-slice 4c):**

> **Tracing.** Leave the entry-point test passing and the trace run completing. Resolve a Tracing Lens finding as LENS §6 says: change the code or the tests; a MEDIUM difference between the plan and the trace may instead be recorded, with its reason, under `### Implementation Deviations` in the IMPLEMENTATION-PLAN; a HIGH is always fixed. Never edit the spec's `### Planned call graph`, a `Traced nodes:` line, or its `tracing:` field. Add no span the tracing standard does not require.

**Test integrity inputs.** **TEST_INTEGRITY** = `SKILL_ROOT/references/test-integrity.md`, resolved absolute — the one definition of what a real test is and of the reviews' Test Integrity Lens. It has no gate: it is passed in every cycle to every implementation spawn (4a, each chunk; per-slice 4a), to the code review and the slice review (4b), to the implementation critical review (4d — with `BASE`, which that review otherwise has no use for), and to every fix spawn (4c, 4e, 4e.5 step 4, per-slice 4c). The 4e.5 verification (step 3) is passed it too, with the IMPLEMENTATION-PLAN path and `BASE`, for the last-look checks it runs there. The blind site count is never passed it. It ships inside this skill; a missing file is a broken install — halt and tell the user. **Embed this fix rule verbatim in every fix prompt, and pass every fix spawn `BASE`, the SPEC, and the IMPLEMENTATION-PLAN path** — the 4e.5 step 4 fix included, with tracing on or off: the rule sends the fixer to the SPEC to decide whether a test may change, and to the plan to record it:

> **Tests.** Never make a failing test pass by weakening it — no deleting it, skipping it, loosening its assertion, changing its expected value, or narrowing what the test run collects — unless the SPEC says the behaviour it checked has changed; then add the line TEST_INTEGRITY §1 requires under `### Test Changes` in the IMPLEMENTATION-PLAN. Never make it pass by teaching the code about the test's inputs. Resolve a Test Integrity finding as TEST_INTEGRITY §7 says: make the test real or the code right; restore a weakened test from `BASE`.

The post-implementation steps (4e.5 final recount, 4f completion, 4h checkpoint, 4i commit, 4j announcement — there is no 4g; eval capture was removed in 3.0.0) are shared with per-slice's end-of-feature cycle.

---

## 4a. Implementation Subagent

**Before the first spawn, record where implementation starts.** The orchestrator appends to `progress.md`:

```markdown
## Feature - Implementing

- **Base commit:** <output of `git rev-parse HEAD` now; `none` if the repo has no commits>
```

This is the only durable record of the commit implementation began from. 4a.5, 4b, and 4e.5 take `BASE` from this line — never from `HEAD`, which a resumed session cannot trust. Write it once per feature; when resuming with the line already present, leave it alone.

Spawn an **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/implementation.md`
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, `SDD/orchestration/progress.md`, `SDD/UBIQUITOUS_LANGUAGE.md` (if present — use canonical names in code, comments, commits, tests), **STANDARD**, and **CONVENTIONS** (`SDD/implementation/sites/SITE-CONVENTIONS-[feature-name].md`, standard §4.2) if it exists.
- **Outputs:** `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[YYYY-MM-DD].md`, implemented code and tests, the site inventory `SDD/implementation/sites/SITES-IMPL-[feature-name].md` (every site of every control, each with a disposition and per-site mutation evidence — body Implementation Process step 6), append `progress.md`.
- **Tracing:** the **tracing inputs** (top of this file), the same to every chunk. With `tracing: on` the body's step 7 applies: the implementer follows the tracing standard for what it adds and checks its marked nodes against the trace run.
- **Tests:** **TEST_INTEGRITY** — the body's step 4 holds every test to its §1.
- **Task:** Implement ALL requirements — core/happy path, edge cases (EDGE-XXX), failure handling (FAIL-XXX), tests alongside each component, performance + security validation — updating IMPLEMENTATION-PLAN throughout, and record enforcement sites.

When the last implementation subagent (or chunk) returns, the **orchestrator** appends `## Feature - Implemented` to `progress.md` (one line: the inventory path). It is the phase-detection marker that 4a finished and 4a.5 is next.

**Sizing (orchestrator-driven, whole-feature only):** before spawning, count SPEC items `REQ-XXX` + `EDGE-XXX` + `FAIL-XXX`. If the total exceeds **8**, pre-split into ⌈total / 5⌉ sequential implementation subagents, each handling a contiguous chunk and appending to IMPLEMENTATION-PLAN so the next knows what's done. Pass every chunk the same IMPLEMENTATION-PLAN path — the one the first chunk created, even when a later chunk runs on a later date; the body continues an existing plan at the path it is given and returns a failure when given none. Each chunk gets a `Reads: 0/20` counter. The Safety-Net Rule remains the in-chunk backstop.

---

## 4a.5. Blind Site Count + Diff

Identical to per-slice 4a.5 (`phases/implementation-per-slice.md` — read its spawn brief, blindness rules, and diff command) with `SCOPE = FEATURE`, `ITER = 0`, counter `SDD/orchestration/counters/4a5-FEATURE-iter0-[timestamp].md`, `BASE` = the `Base commit:` recorded under `## Feature - Implementing` (the work is uncommitted until 4i, so the counter diffs the working tree against it and lists untracked files) or "whole repo", output `SDD/reviews/SITE-COUNT-FEATURE-[feature-name]-iter0-[YYYY-MM-DD].md`, diff `SDD/reviews/SITE-DIFF-FEATURE-[feature-name]-iter0-[YYYY-MM-DD].md` with `--scope FEATURE` and **no** `--base` (a FEATURE diff compares every row; the script rejects `--base` there). Progress lines: `## Site Count FEATURE iter 0 - Complete` (counter) and `## Site Diff FEATURE iter 0 - <result>` (orchestrator). Every outcome goes to 4b, which turns it into findings.

---

## 4b. Code Review Subagent

Run this review by the cycle's **review route** (`references/second-model-review.md`). On the Claude route, spawn an **`agent-engineering:sdd-workhorse`** subagent. Either route is given:
- **Body:** `bodies/code-review.md`
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[YYYY-MM-DD].md`, the implemented code files (paths from IMPLEMENTATION-PLAN), **BRIEF** (`SDD/requirements/DESIGN-[###]-[feature-name].md`, with its approved revision and tier) for the review's `## Design Brief Check`, `BASE` = the `Base commit:` recorded under `## Feature - Implementing` (the same one 4a.5 uses — the check compares the files changed since it against the brief's footprint), **TIERS** (the tier standard resolved at Step 0) when the spec carries `tier:`, and — whenever the catalog is passed (below) — the panel review `SDD/reviews/PANEL-SPEC-[feature-name]-[YYYYMMDD].md`, whose `AI Agent Security Findings` and `Abuse cases to cover` blocks the lens checks the code against.
- **Outputs:** `SDD/reviews/REVIEW-[###]-[feature-name]-[YYYYMMDD].md`.
- **Tracing:** the **tracing inputs**. With `tracing: on` the body's **Tracing Lens** runs the application's trace run, writes TRACE_TREE, and compares it with every marked node of the spec's planned call graph (`SCOPE = FEATURE`); a HIGH lens finding is a rejection criterion. With `tracing: off` the body records that the lens was skipped.
- **Tests:** **TEST_INTEGRITY**. The body's **Test Integrity Lens** runs in every cycle: it checks that the tests are real and that neither they nor the code were bent to get a green run; a HIGH lens finding is a rejection criterion.
- **Task:** Specification-driven review (70% spec alignment, 20% context engineering, 10% test alignment). The body's **Agentic-Surface Lens** fires when the spec's `agent_security:` gate is open — pass the resolved **CATALOG** path and the resolved gate value (`agent_security: true` or `agent_security: auto`) in the prompt whenever `agent_security:` is `true` or `auto`/absent **and CATALOG exists**. A missing catalog closed the gate for the whole run at Step 0, `true` included: pass no catalog path and no panel review, and the body records that the lens was skipped. A HIGH lens finding is a rejection criterion. Pass `SCOPE = FEATURE`, `ITER = 0`, **STANDARD**, **CONVENTIONS** (the path even if absent — the review may create it), the site inventory, and the iter0 `SITE-COUNT` / `SITE-DIFF` paths; the review appends `## Review FEATURE iter 0 - APPROVED | REJECTED (h HIGH, m MEDIUM)` to `progress.md` — the body's **Enforcement-Site Verification** section (mandatory) carries every diff finding into the review, resolves `EXTRA` sites by re-running their mutations, re-runs a mutation sample, and verifies dispositions (ii)/(iii). Apply **Risk-Tiered Review Depth** — read each `MODULE-XXX`'s `Risk:` field and scale internal-review depth: `high` → full internals; `medium` → default; `low` → tested-boundary only. Escalate any tier that looks misclassified (e.g., a `low`-tagged module touching irreversible state) and flag it in the Module Review Log.

---

## 4c. Address Code Review Findings

Spawn an **`agent-engineering:sdd-workhorse`** fix subagent:
- **Inputs:** `SDD/reviews/REVIEW-[###]-[feature-name]-[YYYYMMDD].md`, `SDD/requirements/SPEC-[###]-[feature-name].md`, the IMPLEMENTATION-PLAN path, the implemented code files, **STANDARD**, **CONVENTIONS** (if it exists), and the site inventory `SDD/implementation/sites/SITES-IMPL-[feature-name].md` — the fix edits the inventory, so it must be handed it and the standard that defines its shape.
- **Outputs:** updated code and tests, updated site inventory, updated IMPLEMENTATION-PLAN, "Findings Addressed" appended to the review.
- **Tracing:** the **tracing inputs** — TRACE_TREE being the file 4b wrote, or none when it wrote none — and, with the gate on, the fix rule.
- **Task:** Fix ALL findings until the implementation reaches APPROVED status — spec misalignment, missing edge/failure handling, test gaps, and everything else. For site-count findings: add each missing site to `SITES-IMPL-[feature-name].md` with a disposition and a fresh per-site mutation (`Slice` = `—` in whole-feature mode; in per-slice 4e.5, the slice that owns the code), delete rows for sites the fix removed, fix or implement each `GAP`, and never delete a (ii)/(iii) site as dead code. Never add, split, or merge rows only to make the two sides' row counts agree — a row-count difference is not a finding (standard §6). (No recount and no `## Fix FEATURE` marker here — 4e.5 recounts after all fixes, before completion.)

---

## 4d. Implementation Critical Review Subagent

Run this review by the cycle's **review route** (`references/second-model-review.md`). On the Claude route, spawn an **`agent-engineering:sdd-critical-reviewer`** subagent (Opus). Either route is given:
- **Body:** `bodies/critical-review.md` — apply its **Implementation Phase** section.
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, the IMPLEMENTATION-PLAN path, implemented code files, test files, **TEST_INTEGRITY** and `BASE` (the `Base commit:` under `## Feature - Implementing` — the body runs the Test Integrity Lens by reading, and looks hardest at tests a fix changed since 4b), and **TIERS** when the spec carries `tier:` (the body's *Respect the Tier* principle).
- **Outputs:** `SDD/reviews/CRITICAL-IMPL-[feature-name]-[YYYYMMDD].md`.
- **Task:** Adversarial review of the implementation.

---

## 4e. Address Implementation Review Findings

Spawn an **`agent-engineering:sdd-workhorse`** fix subagent:
- **Inputs:** `SDD/reviews/CRITICAL-IMPL-[feature-name]-[YYYYMMDD].md`, `SDD/requirements/SPEC-[###]-[feature-name].md`, the IMPLEMENTATION-PLAN path, implemented code files, **STANDARD**, **CONVENTIONS** (if it exists), and the site inventory `SDD/implementation/sites/SITES-IMPL-[feature-name].md`.
- **Outputs:** updated code and tests, updated site inventory, updated IMPLEMENTATION-PLAN, "Findings Addressed" appended to the review.
- **Tracing:** the **tracing inputs** — TRACE_TREE being the file 4b wrote, or none when it wrote none — and, with the gate on, the fix rule.
- **Task:** Resolve ALL findings regardless of severity — spec deviations, security vulnerabilities, silent failures, missing test coverage, and every other issue. **Site duties, the same as 4c:** a fix that adds, moves, or removes an enforcement site updates the inventory in the same pass — add each new site with a disposition and a fresh per-site mutation, delete rows for sites the fix removed, fix or implement each `GAP`, and never delete a (ii)/(iii) site as dead code. (No recount and no `## Fix FEATURE` marker here — 4e.5 recounts next.)

---

## 4e.5. Final Blind Recount  *(shared with per-slice end-of-feature; always runs)*

A feature-wide blind recount after every fix has landed, so completion never rests on a count taken before the code last changed. In per-slice mode it also catches sites that span slices. On first entry — coming from 4e — the orchestrator appends `## Final Recount - Started` (the phase-detection anchor for this step); on exit to 4f it appends `## Final Recount - Complete`. A run resumed from `## Awaiting Site-Count Resolution` re-enters at step 1 **without** writing the anchor again: that halt block is its boundary (`phases/protocols.md`). Every spawn below carries the Safety-Net Rule, a fresh counter file (`Reads: 0/20` for the count, `0/15` for the verification review and the fix), and its compact body path (`site-count-compact.md` for the count, `implementation-compact.md` otherwise). `BASE` for the count is the `Base commit:` recorded under `## Feature - Implementing` (the commit before implementation began; per-slice: before SLICE-001), or "whole repo". Loop, starting at `k = 1` (whole-feature — iter0 was 4a.5) or `k = 0` (per-slice — no FEATURE count exists yet):

1. **Recount.** Spawn a fresh blind counter exactly as 4a.5 with `SCOPE = FEATURE`, `ITER = k`, counter `4e5-FEATURE-iter<k>-[timestamp].md`. Its prompt carries no earlier count, diff, or review — only the **CONVENTIONS** path if the file exists, and the `ALSO INVENTORY` IDs if the previous verification review recorded any.
2. **Diff.** Run `scripts/site-diff.py … --scope FEATURE` into `SITE-DIFF-FEATURE-[feature-name]-iter<k>-[YYYY-MM-DD].md`; append `## Site Diff FEATURE iter <k> - <result>`. **Step 3 always runs, whatever the result** — no diff goes to 4f from here. Since the code last changed, nobody has looked at whether a fix weakened a test (the Test Integrity last-look checks, below); and a matching diff still leaves work only a reviewer can do: at a `MATCH (… with more blind rows)` the mutation of each blind row the implementer's rows do not describe is re-run (standard §6), every disposition-(ii) argument and (iii) owner note is accepted or refused (standard §6), and with `tracing: on` the planned calls are compared with a real run. On a plain `MATCH` with nothing to carry from the diff, step 3 checks the row-count keys, the dispositions, and the tests.
3. **Verify.** By the cycle's **review route** (`references/second-model-review.md`) — on the Claude route, an **`agent-engineering:sdd-workhorse`** subagent — run `bodies/code-review.md` with `MODE: site-verification-only`, passing `SCOPE = FEATURE`, `ITER = k`, the SPEC path (the mode judges uncounted rules against it), **STANDARD**, **CONVENTIONS**, the inventory, this iteration's count and diff, and — for the body's last look at the tests — **TEST_INTEGRITY**, the IMPLEMENTATION-PLAN path, and `BASE`. In this mode the body runs the **last-look checks** (TEST_INTEGRITY §5) — was an existing test weakened or removed, is anything kept out of the run, and, for the tests this feature added, is each expected value still the spec's and can each assertion still fail: this is the only review after the last fix round, and a fix is where a test is most cheaply made to pass. It writes `SDD/reviews/REVIEW-SITES-FEATURE-[feature-name]-iter<k>-[YYYYMMDD].md` and appends `## Review FEATURE iter <k> - APPROVED | REJECTED (h HIGH [r row-only], m MEDIUM)`. If it is APPROVED (e.g. every difference was a `CONFIRMED-EXTRA` or `CONFIRMED-CROSS-FILED`, every row-count key checked out, and the test checks found nothing) → go to 4f.
   **With `tracing: on`** the spawn is also passed the **tracing inputs** (TRACE_TREE = this iteration's `…-iter<k>-…` file), the IMPLEMENTATION-PLAN path (its `### Implementation Deviations` holds the plan-versus-trace differences already recorded), and `BASE` (the lens reads the code the feature changed). The mode then also runs the **Tracing Lens** at `SCOPE = FEATURE` against every marked node of the spec's planned call graph, writes TRACE_TREE, and reports its LOW findings: the marker is `## Review FEATURE iter <k> - APPROVED | REJECTED (h HIGH [r row-only], m MEDIUM, l LOW)`, the LOW count always written, zero included. **Go to 4f only when all three counts are zero** — an `APPROVED` marker with a LOW count above zero goes to step 4, like a `REJECTED` one. (A marker with no LOW count while the gate is on is a malformed one: open that review document and count its LOW findings before deciding.) In per-slice mode this is the one review that compares the whole planned graph with a single run.
4. **Fix.** Spawn an **`agent-engineering:sdd-workhorse`** fix subagent with that review, **STANDARD**, **CONVENTIONS** (if it exists), and the inventory (same site-finding duties as 4c); it appends `## Fix FEATURE iter <k+1> - Complete`. Then `k = k + 1` and repeat from 1. With `tracing: on` it resolves every finding of that review — HIGH, MEDIUM, and LOW — and is also passed the **tracing inputs** (TRACE_TREE = the file that review wrote, or none when it wrote none — the **Tracing inputs** block), the fix rule, the SPEC (it holds the planned call graph a lens finding is about), and the IMPLEMENTATION-PLAN path (the fix rule lets it record a deviation there). The recount, diff, and verification that follow are what re-check a tracing fix: no finding is closed on the fix subagent's word.

**Cap:** at most **3** fix rounds (counted as the `## Fix FEATURE iter <k>` lines after the latest `## Awaiting Site-Count Resolution` block, or all of them if there is none), with the same progress-stall check as the per-slice cap (the verification review's needs-code-or-test HIGH — HIGH minus row-only — must strictly decrease, or MEDIUM when that is zero; row-only HIGH still block APPROVED). Test Integrity findings are ordinary findings of the verification review, in the same numbers, cap, and stall check. With `tracing: on`, Tracing Lens findings are ordinary findings of the verification review: they count in the same three numbers, toward the same cap and the same stall check. As on the slice path, **LOW never counts toward the stall check** — when needs-code-or-test HIGH and MEDIUM were both zero in the previous iteration there is nothing to stall on, and only the cap applies. On cap or stall, the orchestrator appends this halt block and stops, in every mode:

```markdown
## Awaiting Site-Count Resolution

Final blind recount for SPEC-[###] did not converge. Unresolved: <n> HIGH, <m> MEDIUM.
Latest diff: <SITE-DIFF path>   Latest verification review: <REVIEW-SITES path>
Resolve the findings (or amend the SPEC), then run `/sdd-flow continue` — the flow re-runs 4e.5 from a fresh recount.
```

With `tracing: on` the block's first two lines are instead — same header, same resume rule:

```markdown
Final check for SPEC-[###] did not converge (enforcement sites and tracing). Unresolved: <n> HIGH, <m> MEDIUM, <l> LOW.
Latest diff: <SITE-DIFF path>   Latest verification review: <REVIEW-SITES path>   Latest trace tree: <TRACE-TREE path, or `none written` when that verification produced no tree>
```

The verification review lists site findings and Tracing Lens findings in one numbered list; its `## Tracing Lens` section says which are which.

Controls left `Partial` never reach `Complete`: 4f refuses to finish while any control is `Partial`.

---

## 4f. Implementation Completion Subagent  *(shared with per-slice end-of-feature)*

Spawn an **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/implementation-complete.md`
- **Inputs:** `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[YYYY-MM-DD].md`, `SDD/requirements/SPEC-[###]-[feature-name].md`, **STANDARD**, the site inventory, the final `SITE-DIFF-FEATURE-*` from 4e.5 and its `REVIEW-SITES-FEATURE-*` (if one was written), and — when the spec carries `tier:` — **TIERS** and **TIER_PLAN** (`SDD/flow/TIERS-[feature-name].md`; on a next-tier cycle the path recorded at Step 0).
- **Tracing:** the gate line. With `tracing: on` also **OBS_RECORD** and the final **TRACE_TREE** — the file the last 4e.5 verification wrote, the one whose marker let the loop end; that verification's `REVIEW-SITES-FEATURE-*` is then always among the inputs above. The body runs no trace run and no script: it reads the two files to fill the summary's `## Monitoring & Observability` and to check that the final verification raised no tracing finding.
- **With `tracing: on`, completion never rests on a trace taken before the code or the tests last changed.** The body then changes no code and no test: an item that needs either — a failing test, a missing test, an unfinished requirement — comes back in its return as incomplete. The orchestrator does not re-spawn it and does not spawn a fix: it appends `## Awaiting Site-Count Resolution` (the 4e.5 halt block, gate-on wording) with the first line `Completion for SPEC-[###] found items that need code or tests changed after the final check: <the items, one line>.` and its usual second and third lines, and stops, in every mode. `/sdd-flow continue` takes that block's rule: a fresh recount, diff, and verification — which runs the lens on the changed code — and only then 4f again. This takes the place of the retry in Error Handling (`phases/protocols.md`) for that one return; a completion spawn that fails for any other reason is handled there as before. With `tracing: off` nothing here applies.
- **Outputs:** updated IMPLEMENTATION-PLAN (including `## Control Site Status`), updated SPEC, updated tier plan (this tier marked shipped; deferrals added during reviews or implementation copied in), `SDD/implementation/summaries/IMPLEMENTATION-SUMMARY-[###]-[YYYY-MM-DD_HH-MM-SS].md`, append `progress.md`.
- **Task:** Finalize all documentation, fill `## Control Site Status` from the final diff (a control with no independent count stays `Partial`, and any `Partial` blocks completion), validate all requirements are met, create the implementation summary, capture glossary deltas (execute inline).

---

## 4h. Supervised Checkpoint (supervised mode only)  *(shared)*

In **supervised mode**, append this block to `progress.md`, then pause with the message below:

```markdown
## Awaiting Commit Approval

Implementation of SPEC-[###] is complete and uncommitted, waiting for the go-ahead to commit (4h).
Summary: <IMPLEMENTATION-SUMMARY path>
```

> **Implementation complete.** Here's a summary:
> [What was built, test results, review outcomes]
> Brief check: [whole-feature: outside the approved footprint: none | list] [per-slice: N of M slices stayed inside the approved footprint; exceptions: …]
> Key artifacts:
> - Spec: `SDD/requirements/SPEC-[###]-[feature-name].md`
> - Code review: `SDD/reviews/REVIEW-[###]-[feature-name]-[YYYYMMDD].md`
> - Critical review: `SDD/reviews/CRITICAL-IMPL-[feature-name]-[YYYYMMDD].md`
> - Implementation summary: `SDD/implementation/summaries/IMPLEMENTATION-SUMMARY-[###]-[timestamp].md`
> **Ready to commit all implementation code?** (y/n)

Wait for confirmation before committing. In **autonomous mode**, proceed directly to commit.

- **y** → 4i. Its `## Implementation - Committed` line answers the block.
- **n** → nothing is committed; stop with the block pending. The user may change the code or the artifacts by hand first; a change that touches an enforcement site is theirs to raise — the flow does not re-review after 4h.
- **Session ends with no answer** → the block is still the latest one.

In the last two cases `/sdd-flow continue` re-shows this checkpoint (`phases/protocols.md` → `## Awaiting Commit Approval`).

**Brief-check line.** Whole-feature: quote the `## Design Brief Check` section of the 4b review document (the file, not a subagent's return). Per-slice: the count across slice reviews (`phases/implementation-per-slice.md` → end-of-feature 4h). Omit the line when the feature has no design brief.

---

## 4i. Commit Implementation  *(shared)*

**Task mirror — in review (both modes, both delivery modes).** For a tiered spec, as soon as 4f returns — before the 4h pause when there is one, and always before this commit — run `python3 "$SKILL_ROOT/scripts/tier-mirror.py" sync <TIER_PLAN> --in-review <tier>`; record and report the result per `SKILL.md` → Tier Task Mirror. It belongs to this step, not to 4h, so that autonomous runs (which have no 4h) still make it. Running it before the commit means any task key it writes into the tier plan is committed here.

The **orchestrator** runs the commit per `commands/commit.md` — all implementation code, tests, reviews, SDD artifacts (including the site inventory, every `SITE-COUNT-*` / `SITE-DIFF-*` / `REVIEW-SITES-*` / `TRACE-TREE-*`, and the updated tier plan). No co-author attribution. If nothing is uncommitted — a resumed run whose commit had already landed — make no commit.

**Then append `## Implementation - Committed` to `progress.md`** — one line, the commit's SHA (or `already committed`). It is the phase-detection marker that the code is in history. `Implementation Phase - COMPLETE`, written by the completion subagent at 4f, does not say so.

If `progress.md` exceeds ~500 lines, rotate it now (`phases/protocols.md` → Progress Rotation).

---

## 4j. Completion Announcement  *(shared)*

> Implementation complete! All requirements from SPEC-[###] have been implemented, reviewed, and tested.
> All artifacts committed. Feature is ready for deployment.
> [If the spec carries `tier:`:] Shipped: **Tier [N]**. Left for later: [one line per tier still sketched in the tier plan, or "nothing"]. Tier plan: `SDD/flow/TIERS-[feature-name].md`. Use it, note what you find under its `## Feedback`, then run `/sdd-flow --next-tier [feature-name]` when you want more.
> Brief check: [the same line as 4h — shown here too, because an autonomous run has no 4h]
> [If ADRs were captured:] ADRs written: [list]. See `SDD/adr/README.md`.

**Task mirror — done.** For a tiered spec, before the announcement run `python3 "$SKILL_ROOT/scripts/tier-mirror.py" sync <TIER_PLAN> --shipped <tier>`: the tier's sub-task becomes done and gets one comment — what shipped and what to look at, taken from the tier plan. Add to the announcement: `Tasks: [tier sub-task key] done; leave feedback as comments on [next tier's key] — the next cycle copies them into the tier plan.` (or the mirror's `OFF` / `ERROR` line, when that is what it returned). Normally this run writes nothing to the tier plan — the keys were saved at the design gate. If an earlier mirror point failed and this one had to create tasks, the tier plan now has new keys in it: when `git status --porcelain -- <TIER_PLAN>` shows a change, commit that one file (per `commands/commit.md`, message naming the tier plan and SPEC) **before** the announcement, so "all artifacts committed" is true.

After the announcement, append `## Feature - Done` to `progress.md` — one line, the spec path. It is the marker that the flow has nothing left to do for this feature.

Then perform the **feature-completion rotation** (`phases/protocols.md` → Progress Rotation): archive this feature's full progress history — its `## Flow Started - ` record and everything after it — to `SDD/orchestration/progress-archive/` and leave the one-line `Finished:` summary in the live `progress.md`.
