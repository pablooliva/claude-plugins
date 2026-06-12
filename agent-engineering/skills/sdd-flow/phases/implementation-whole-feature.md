# Phase: Implementation — whole-feature mode (Steps 4a–4j)

Reached at Step 4 when the spec's `delivery_mode:` is `whole-feature` (the default, and the PARSE default when the field is absent). If `delivery_mode: per-slice`, do NOT run these steps — read `phases/implementation-per-slice.md` instead.

Phase-execution and fix subagents carry the Safety-Net Rule + a fresh counter file + the `implementation-compact.md` compact body path. Implementation-chunk counters use `Reads: 0/20`. Body paths are `SKILL_ROOT/bodies/<file>.md`, resolved absolute.

The post-implementation steps (4f completion, 4g eval, 4h checkpoint, 4i commit, 4j announcement) are shared with per-slice's end-of-feature cycle.

---

## 4a. Implementation Subagent

Spawn an **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/implementation.md`
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, `SDD/orchestration/progress.md`, `SDD/UBIQUITOUS_LANGUAGE.md` (if present — use canonical names in code, comments, commits, tests).
- **Outputs:** `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[YYYY-MM-DD].md`, implemented code and tests, append `progress.md`.
- **Task:** Implement ALL requirements — core/happy path, edge cases (EDGE-XXX), failure handling (FAIL-XXX), tests alongside each component, performance + security validation — updating IMPLEMENTATION-PLAN throughout.

**Sizing (orchestrator-driven, whole-feature only):** before spawning, count SPEC items `REQ-XXX` + `EDGE-XXX` + `FAIL-XXX`. If the total exceeds **8**, pre-split into ⌈total / 5⌉ sequential implementation subagents, each handling a contiguous chunk and appending to IMPLEMENTATION-PLAN so the next knows what's done. Each chunk gets a `Reads: 0/20` counter. The Safety-Net Rule remains the in-chunk backstop.

---

## 4b. Code Review Subagent

Spawn an **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/code-review.md`
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[YYYY-MM-DD].md`, the implemented code files (paths from IMPLEMENTATION-PLAN).
- **Outputs:** `SDD/reviews/REVIEW-[###]-[feature-name]-[YYYYMMDD].md`.
- **Task:** Specification-driven review (70% spec alignment, 20% context engineering, 10% test alignment). Apply **Risk-Tiered Review Depth** — read each `MODULE-XXX`'s `Risk:` field and scale internal-review depth: `high` → full internals; `medium` → default; `low` → tested-boundary only. Escalate any tier that looks misclassified (e.g., a `low`-tagged module touching irreversible state) and flag it in the Module Review Log.

---

## 4c. Address Code Review Findings

Spawn an **`agent-engineering:sdd-workhorse`** fix subagent:
- **Inputs:** `SDD/reviews/REVIEW-[###]-[feature-name]-[YYYYMMDD].md`, `SDD/requirements/SPEC-[###]-[feature-name].md`, the implemented code files.
- **Outputs:** updated code and tests, updated IMPLEMENTATION-PLAN, "Findings Addressed" appended to the review.
- **Task:** Fix ALL findings until the implementation reaches APPROVED status — spec misalignment, missing edge/failure handling, test gaps, and everything else.

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

## 4f. Implementation Completion Subagent  *(shared with per-slice end-of-feature)*

Spawn an **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/implementation-complete.md`
- **Inputs:** `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[YYYY-MM-DD].md`, `SDD/requirements/SPEC-[###]-[feature-name].md`.
- **Outputs:** updated IMPLEMENTATION-PLAN, updated SPEC, `SDD/implementation/summaries/IMPLEMENTATION-SUMMARY-[###]-[YYYY-MM-DD_HH-MM-SS].md`, append `progress.md`.
- **Task:** Finalize all documentation, validate all requirements are met, create the implementation summary, capture glossary deltas (execute inline).

---

## 4g. Regression Eval Capture (conditional)  *(shared)*

Read the spec's `eval_required:` frontmatter. If `true`, spawn an **`agent-engineering:sdd-workhorse`** subagent:
- **Body:** `bodies/eval-capture.md`
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md` (feature name, success criteria, frontmatter), repo's existing `evals/` (if present).
- **Outputs:** LangSmith dataset created (empty, awaiting examples) via the `langsmith` CLI, `evals/evaluators/[feature-slug]_evaluator.{py,ts}`, `evals/run_functions/[feature-slug]_run.{py,ts}`, `evals/README.md` updated.
- **Task:** Scaffold the regression eval infrastructure. **Non-blocking:** if the `langsmith` CLI / API key is missing, log a warning to `progress.md` and return WITHOUT halting — the feature has shipped; eval is a follow-up. Surface the warning in 4j.

If `eval_required:` is `false`/absent, skip this step.

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

The **orchestrator** runs the commit per `commands/commit.md` — all implementation code, tests, reviews, SDD artifacts, and any eval scaffolding from 4g. No co-author attribution.

If `progress.md` exceeds ~500 lines, rotate it now (`phases/protocols.md` → Progress Rotation).

---

## 4j. Completion Announcement  *(shared)*

> Implementation complete! All requirements from SPEC-[###] have been implemented, reviewed, and tested.
> All artifacts committed. Feature is ready for deployment.
> [If eval_required and scaffold succeeded:] Regression eval dataset `regression-[feature-slug]` created on LangSmith (empty). Populate with golden examples after ≥1 week of runtime. See `evals/README.md`.
> [If eval_required but scaffold failed:] ⚠️ Eval scaffolding failed — see progress.md. Run `/regression-eval-capture` manually once LangSmith is configured.
> [If ADRs were captured:] ADRs written: [list]. See `SDD/adr/README.md`.

After the announcement, perform the **feature-completion rotation** (`phases/protocols.md` → Progress Rotation): archive this feature's full progress history to `SDD/orchestration/progress-archive/` and leave a one-line summary in the live `progress.md`.
