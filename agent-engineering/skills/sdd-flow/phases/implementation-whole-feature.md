# Phase: Implementation — whole-feature mode (Steps 4a–4j)

Reached at Step 4 when the spec's `delivery_mode:` is `whole-feature` (the default, and the PARSE default when the field is absent). If `delivery_mode: per-slice`, do NOT run these steps — read `phases/implementation-per-slice.md` instead.

Phase-execution and fix subagents carry the Safety-Net Rule + a fresh counter file + the `implementation-compact.md` compact body path (blind site counts: `site-count-compact.md`). Implementation-chunk and blind-site-count counters use `Reads: 0/20`. Body paths are `SKILL_ROOT/bodies/<file>.md`, resolved absolute. **STANDARD** = `SKILL_ROOT/references/enforcement-sites.md`, resolved absolute, passed to every implementation, site-count, review, fix, and completion spawn.

The post-implementation steps (4e.5 final recount, 4f completion, 4g eval, 4h checkpoint, 4i commit, 4j announcement) are shared with per-slice's end-of-feature cycle.

---

## 4a. Implementation Subagent

Spawn an **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/implementation.md`
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, `SDD/orchestration/progress.md`, `SDD/UBIQUITOUS_LANGUAGE.md` (if present — use canonical names in code, comments, commits, tests), **STANDARD**.
- **Outputs:** `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[YYYY-MM-DD].md`, implemented code and tests, the site inventory `SDD/implementation/sites/SITES-IMPL-[feature-name].md` (every site of every control, each with a disposition and per-site mutation evidence — body Implementation Process step 6), append `progress.md`.
- **Task:** Implement ALL requirements — core/happy path, edge cases (EDGE-XXX), failure handling (FAIL-XXX), tests alongside each component, performance + security validation — updating IMPLEMENTATION-PLAN throughout, and record enforcement sites.

When the last implementation subagent (or chunk) returns, the **orchestrator** appends `## Feature - Implemented` to `progress.md` (one line: the inventory path). It is the phase-detection marker that 4a finished and 4a.5 is next.

**Sizing (orchestrator-driven, whole-feature only):** before spawning, count SPEC items `REQ-XXX` + `EDGE-XXX` + `FAIL-XXX`. If the total exceeds **8**, pre-split into ⌈total / 5⌉ sequential implementation subagents, each handling a contiguous chunk and appending to IMPLEMENTATION-PLAN so the next knows what's done. Each chunk gets a `Reads: 0/20` counter. The Safety-Net Rule remains the in-chunk backstop.

---

## 4a.5. Blind Site Count + Diff

Identical to per-slice 4a.5 (`phases/implementation-per-slice.md` — read its spawn brief, blindness rules, and diff command) with `SCOPE = FEATURE`, `ITER = 0`, counter `SDD/orchestration/counters/4a5-FEATURE-iter0-[timestamp].md`, `BASE` = the commit before 4a (the work is uncommitted until 4i, so the counter diffs the working tree against it and lists untracked files) or "whole repo", output `SDD/reviews/SITE-COUNT-FEATURE-[feature-name]-iter0-[YYYY-MM-DD].md`, diff `SDD/reviews/SITE-DIFF-FEATURE-[feature-name]-iter0-[YYYY-MM-DD].md` with `--scope FEATURE`. Progress lines: `## Site Count FEATURE iter 0 - Complete` (counter) and `## Site Diff FEATURE iter 0 - <result>` (orchestrator). Every outcome goes to 4b, which turns it into findings.

---

## 4b. Code Review Subagent

Spawn an **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/code-review.md`
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[YYYY-MM-DD].md`, the implemented code files (paths from IMPLEMENTATION-PLAN).
- **Outputs:** `SDD/reviews/REVIEW-[###]-[feature-name]-[YYYYMMDD].md`.
- **Task:** Specification-driven review (70% spec alignment, 20% context engineering, 10% test alignment). The body's **Agentic-Surface Lens** fires when the spec's `agent_security:` gate is open — pass the resolved **CATALOG** path in the prompt whenever `agent_security:` is `true` or `auto`/absent. A HIGH lens finding is a rejection criterion. Pass `SCOPE = FEATURE`, `ITER = 0`, **STANDARD**, the site inventory, and the iter0 `SITE-COUNT` / `SITE-DIFF` paths; the review appends `## Review FEATURE iter 0 - APPROVED | REJECTED (h HIGH, m MEDIUM)` to `progress.md` — the body's **Enforcement-Site Verification** section (mandatory) carries every diff finding into the review, resolves `EXTRA` sites by re-running their mutations, re-runs a mutation sample, and verifies dispositions (ii)/(iii). Apply **Risk-Tiered Review Depth** — read each `MODULE-XXX`'s `Risk:` field and scale internal-review depth: `high` → full internals; `medium` → default; `low` → tested-boundary only. Escalate any tier that looks misclassified (e.g., a `low`-tagged module touching irreversible state) and flag it in the Module Review Log.

---

## 4c. Address Code Review Findings

Spawn an **`agent-engineering:sdd-workhorse`** fix subagent:
- **Inputs:** `SDD/reviews/REVIEW-[###]-[feature-name]-[YYYYMMDD].md`, `SDD/requirements/SPEC-[###]-[feature-name].md`, the implemented code files.
- **Outputs:** updated code and tests, updated IMPLEMENTATION-PLAN, "Findings Addressed" appended to the review.
- **Task:** Fix ALL findings until the implementation reaches APPROVED status — spec misalignment, missing edge/failure handling, test gaps, and everything else. For site-count findings: add each missing site to `SITES-IMPL-[feature-name].md` with a disposition and a fresh per-site mutation (`Slice` = `—` in whole-feature mode; in per-slice 4e.5, the slice that owns the code), delete rows for sites the fix removed, fix or implement each `GAP`, and never delete a (ii)/(iii) site as dead code. (No recount and no `## Fix FEATURE` marker here — 4e.5 recounts after all fixes, before completion.)

---

## 4d. Implementation Critical Review Subagent

Spawn an **`agent-engineering:sdd-critical-reviewer`** subagent (Opus):
- **Body:** `bodies/critical-review.md` — apply its **Implementation Phase** section.
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, implemented code files, test files.
- **Outputs:** `SDD/reviews/CRITICAL-IMPL-[feature-name]-[YYYYMMDD].md`.
- **Task:** Adversarial review of the implementation.

---

## 4e. Address Implementation Review Findings

Spawn an **`agent-engineering:sdd-workhorse`** fix subagent:
- **Inputs:** `SDD/reviews/CRITICAL-IMPL-[feature-name]-[YYYYMMDD].md`, `SDD/requirements/SPEC-[###]-[feature-name].md`, implemented code files.
- **Outputs:** updated code and tests, updated IMPLEMENTATION-PLAN, "Findings Addressed" appended to the review.
- **Task:** Resolve ALL findings regardless of severity — spec deviations, security vulnerabilities, silent failures, missing test coverage, and every other issue.

---

## 4e.5. Final Blind Recount  *(shared with per-slice end-of-feature; always runs)*

A feature-wide blind recount after every fix has landed, so completion never rests on a count taken before the code last changed. In per-slice mode it also catches sites that span slices. On entry the orchestrator appends `## Final Recount - Started` (the phase-detection anchor for this step); on exit to 4f it appends `## Final Recount - Complete`. Every spawn below carries the Safety-Net Rule, a fresh counter file (`Reads: 0/20` for the count, `0/15` for the verification review and the fix), and its compact body path (`site-count-compact.md` for the count, `implementation-compact.md` otherwise). `BASE` for the count is the commit before implementation began (per-slice: before SLICE-001), or "whole repo". Loop, starting at `k = 1` (whole-feature — iter0 was 4a.5) or `k = 0` (per-slice — no FEATURE count exists yet):

1. **Recount.** Spawn a fresh blind counter exactly as 4a.5 with `SCOPE = FEATURE`, `ITER = k`, counter `4e5-FEATURE-iter<k>-[timestamp].md`. Its prompt carries no earlier count, diff, or review — only the `ALSO INVENTORY` IDs if the previous verification review recorded any.
2. **Diff.** Run `scripts/site-diff.py … --scope FEATURE` into `SITE-DIFF-FEATURE-[feature-name]-iter<k>-[YYYY-MM-DD].md`; append `## Site Diff FEATURE iter <k> - <result>`. If `MATCH` → go to 4f.
3. **Verify.** Spawn an **`agent-engineering:sdd-workhorse`** subagent with `bodies/code-review.md` and `MODE: site-verification-only`, passing **STANDARD**, the inventory, and this iteration's count and diff. It writes `SDD/reviews/REVIEW-SITES-FEATURE-[feature-name]-iter<k>-[YYYYMMDD].md` and appends `## Review FEATURE iter <k> - APPROVED | REJECTED (h HIGH, m MEDIUM)`. If it is APPROVED (e.g. every difference was a `CONFIRMED-EXTRA`) → go to 4f.
4. **Fix.** Spawn an **`agent-engineering:sdd-workhorse`** fix subagent with that review, **STANDARD**, and the inventory (same site-finding duties as 4c); it appends `## Fix FEATURE iter <k+1> - Complete`. Then `k = k + 1` and repeat from 1.

**Cap:** at most **3** fix rounds (counted as the `## Fix FEATURE iter <k>` lines after the latest `## Awaiting Site-Count Resolution` block, or all of them if there is none), with the same progress-stall check as the per-slice cap (the verification review's HIGH count must strictly decrease, or MEDIUM when HIGH is zero). On cap or stall, the orchestrator appends this halt block and stops, in every mode:

```markdown
## Awaiting Site-Count Resolution

Final blind recount for SPEC-[###] did not converge. Unresolved: <n> HIGH, <m> MEDIUM.
Latest diff: <SITE-DIFF path>   Latest verification review: <REVIEW-SITES path>
Resolve the findings (or amend the SPEC), then run `/sdd-flow continue` — the flow re-runs 4e.5 from a fresh recount.
```

Controls left `Partial` never reach `Complete`: 4f refuses to finish while any control is `Partial`.

---

## 4f. Implementation Completion Subagent  *(shared with per-slice end-of-feature)*

Spawn an **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/implementation-complete.md`
- **Inputs:** `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[YYYY-MM-DD].md`, `SDD/requirements/SPEC-[###]-[feature-name].md`, **STANDARD**, the site inventory, the final `SITE-DIFF-FEATURE-*` from 4e.5 and its `REVIEW-SITES-FEATURE-*` (if one was written).
- **Outputs:** updated IMPLEMENTATION-PLAN (including `## Control Site Status`), updated SPEC, `SDD/implementation/summaries/IMPLEMENTATION-SUMMARY-[###]-[YYYY-MM-DD_HH-MM-SS].md`, append `progress.md`.
- **Task:** Finalize all documentation, fill `## Control Site Status` from the final diff (a control with no independent count stays `Partial`, and any `Partial` blocks completion), validate all requirements are met, create the implementation summary, capture glossary deltas (execute inline).

---

## 4g. Regression Eval Capture (conditional)  *(shared)*

Read the spec's `eval_required:` and `agent_security:` frontmatter. Run this step if **either** `eval_required: true` **or** the `agent_security:` gate is open (`true`, or `auto`/absent with an agentic surface in the implemented code). When only the security gate is open, the subagent runs in **abuse-case-only mode** (no evaluator/run-function stubs). Spawn an **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/eval-capture.md`
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md` (feature name, success criteria, frontmatter), repo's existing `evals/` (if present). When the `agent_security:` gate is open, also pass `SDD/reviews/REVIEW-[###]-[feature-name]-[YYYYMMDD].md` (for its abuse-case coverage table) and the resolved **CATALOG** path.
- **Outputs:** LangSmith dataset created (empty, awaiting examples) via the `langsmith` CLI, `evals/evaluators/[feature-slug]_evaluator.{py,ts}`, `evals/run_functions/[feature-slug]_run.{py,ts}`, `evals/README.md` updated.
- **Task:** Scaffold the regression eval infrastructure, and seed the abuse-case rows (body §4b) when the security gate is open. **Non-blocking:** if the `langsmith` CLI / API key is missing, log a warning to `progress.md` and return WITHOUT halting — the feature has shipped; eval is a follow-up. Surface the warning in 4j.

If `eval_required:` is `false`/absent **and** the `agent_security:` gate is closed, skip this step.

---

## 4h. Supervised Checkpoint (supervised mode only)  *(shared)*

In **supervised mode**, pause:

> **Implementation complete.** Here's a summary:
> [What was built, test results, review outcomes]
> Key artifacts:
> - Spec: `SDD/requirements/SPEC-[###]-[feature-name].md`
> - Code review: `SDD/reviews/REVIEW-[###]-[feature-name]-[YYYYMMDD].md`
> - Critical review: `SDD/reviews/CRITICAL-IMPL-[feature-name]-[YYYYMMDD].md`
> - Implementation summary: `SDD/implementation/summaries/IMPLEMENTATION-SUMMARY-[###]-[timestamp].md`
> - [Eval scaffolding: evals/... (if eval_required and scaffold succeeded)]
> - [Eval scaffold warnings: progress.md (if scaffold failed)]
> **Ready to commit all implementation code?** (y/n)

Wait for confirmation before committing. In **autonomous mode**, proceed directly to commit.

---

## 4i. Commit Implementation  *(shared)*

The **orchestrator** runs the commit per `commands/commit.md` — all implementation code, tests, reviews, SDD artifacts (including the site inventory and every `SITE-COUNT-*` / `SITE-DIFF-*` / `REVIEW-SITES-*`), and any eval scaffolding from 4g. No co-author attribution.

If `progress.md` exceeds ~500 lines, rotate it now (`phases/protocols.md` → Progress Rotation).

---

## 4j. Completion Announcement  *(shared)*

> Implementation complete! All requirements from SPEC-[###] have been implemented, reviewed, and tested.
> All artifacts committed. Feature is ready for deployment.
> [If eval_required and scaffold succeeded:] Regression eval dataset `regression-[feature-slug]` created on LangSmith (empty). Populate with golden examples after ≥1 week of runtime. See `evals/README.md`.
> [If eval_required but scaffold failed:] ⚠️ Eval scaffolding failed — see progress.md. Run `/regression-eval-capture` manually once LangSmith is configured.
> [If ADRs were captured:] ADRs written: [list]. See `SDD/adr/README.md`.

After the announcement, perform the **feature-completion rotation** (`phases/protocols.md` → Progress Rotation): archive this feature's full progress history to `SDD/orchestration/progress-archive/` and leave a one-line summary in the live `progress.md`.
