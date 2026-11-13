# Phase: Implementation — whole-feature mode (Step 4a)

Reached at Step 4 when the spec's `delivery_mode:` is `whole-feature`. If `delivery_mode: per-slice`, do NOT run these steps — read `phases/implementation-per-slice.md` instead.

Phase-execution and fix subagents carry the Safety-Net Rule + a fresh counter file + the `implementation-compact.md` compact body path. Implementation-chunk counters use `Reads: 0/20`. A review step run on the second model carries none of the three (`references/second-model-review.md` §3). Body paths are `SKILL_ROOT/bodies/<file>.md`, resolved absolute.

Read `phases/implementation-inputs.md` with this file: the inputs every Step 4 spawn is passed (SECURITY, FIT, TEST_INTEGRITY, the tracing and evals inputs), the eval run of record, and the LOW and scope-of-the-fix rules. When 4a is done, go on to 4b in `phases/end-of-feature.md`.

---

## 4a. Implementation Subagent

**Before the first spawn, record where implementation starts.** The orchestrator appends to `progress.md`:

```markdown
## Feature - Implementing

- **Base commit:** <output of `git rev-parse HEAD` now; `none` if the repo has no commits>
```

This is the only durable record of the commit implementation began from. 4b and 4e.5 take `BASE` from this line — never from `HEAD`, which a resumed session cannot trust. Write it once per feature; when resuming with the line already present, leave it alone.

Spawn an **`agent-engineering:sdd-workhorse`** subagent **with the per-spawn model override `opus`** (every chunk too):
- **Body:** `bodies/implementation.md`
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, `SDD/.records/progress.md`, `SDD/UBIQUITOUS_LANGUAGE.md` (if present — use canonical names in code, comments, commits, tests), **SECURITY**, **BRIEF** (`SDD/requirements/DESIGN-[###]-[feature-name].md`, with its approved revision), and **FIT**.
- **Outputs:** `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[YYYY-MM-DD].md`, implemented code and tests (each security rule's guard proven, body Implementation Process step 6), append `progress.md`.
- **Tracing:** the **tracing inputs** (`phases/implementation-inputs.md`), the same to every chunk. With `tracing: on` the body's step 7 applies: the implementer follows the tracing standard for what it adds and checks its marked nodes against the trace run.
- **Tests:** **TEST_INTEGRITY** — the body's step 4 holds every test to its §1.
- **Fit:** **BRIEF** and **FIT** — the body's step 4 follows FIT §5: extend the code the brief's `## Builds on` names before adding, add only the new files it names, and give each new structure a one-line reason.
- **Evals:** the **evals inputs** (`phases/implementation-inputs.md`), the same to every chunk. With `evals: on` the body's step 8 applies: the implementer builds the cases of the spec's `### Evals` that its requirements carry — rendering the eval run from EVAL_TEMPLATES when the application has none yet — and makes its own eval run.
- **Task:** Implement ALL requirements — core/happy path, edge cases (EDGE-XXX), failure handling (FAIL-XXX), tests alongside each component, performance + security validation — updating IMPLEMENTATION-PLAN throughout, and prove each security rule (SECURITY §3).

When the last implementation subagent (or chunk) returns, the **orchestrator** appends `## Feature - Implemented` to `progress.md`. It is the phase-detection marker that 4a finished and 4b is next.

**Sizing (orchestrator-driven, whole-feature only):** before spawning, count SPEC items `REQ-XXX` + `EDGE-XXX` + `FAIL-XXX`. If the total exceeds **8** *and* the approved brief's "What changes where" names more than **3** areas, pre-split. **Count the areas** from the paths and path prefixes it names: a path inside another named prefix counts with that prefix, not again; every test path together is one area, every path under `evals/` together is one, and every documentation file (`*.md`, `docs/`) together is one; each other distinct path or prefix is one. For example `src/app/llm.py`, `src/app/prompts/`, `tests/test_llm.py`, `tests/test_evals.py`, `evals/cases.jsonl`, `README.md` is 5 areas (two source paths, tests, evals, documentation) — split when there are also more than 8 items; `src/app/llm.py`, `tests/test_llm.py`, `evals/cases.jsonl` is 3, one implementer however many items. Many items over a small footprint are one implementer's work: in one trial, 18 items for a one-sentence prompt change were split into 4 chunks, and the last two mostly wrote documentation. With a footprint that names no paths, count the items alone. When pre-splitting, split into ⌈total / 5⌉ sequential implementation subagents, each handling a contiguous chunk and appending to IMPLEMENTATION-PLAN so the next knows what's done. Pass every chunk the same IMPLEMENTATION-PLAN path — the one the first chunk created, even when a later chunk runs on a later date; the body continues an existing plan at the path it is given and returns a failure when given none. Each chunk gets a `Reads: 0/20` counter. The Safety-Net Rule remains the in-chunk backstop.

---

Next: 4b, in `phases/end-of-feature.md`.
