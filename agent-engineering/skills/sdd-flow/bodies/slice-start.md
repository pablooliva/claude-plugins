# Start a Vertical Slice

You are a spawned subagent in an orchestrated /sdd-flow run. Your prompt provides resolved artifact paths and identifiers — use them verbatim. This file is your complete instruction set. Do not spawn subagents or invoke slash commands/skills, even if an Agent/Task tool is available — the flow’s flat-orchestration contract forbids it; all work happens inline in your own context.

You are initiating implementation work on a single vertical slice (`SLICE-XXX`) within a feature whose SPEC declares `delivery_mode: per-slice`. This body is one of two slice bodies — `slice-start` and `slice-review` — which, with the orchestrator's per-slice commit (step 4c.6; conventions in `commands/commit.md`), make up the per-slice cycle. Each is inert outside per-slice mode.

## Active-Slice Resolution Convention (shared across all four slice primitives)

The four slice primitives resolve the active slice via the SAME priority chain — but the *expected status* differs by primitive intent (per SPEC MODULE-002 active-slice fallback asymmetry):

1. **Explicit `[SLICE-ID]` argument** — if provided, use it. Validate against `^SLICE-\d{3}[a-z]?$` BEFORE interpolating into any path (per REQ-024 path-traversal prevention; see "Slice-ID Validation" below).
2. **IMPLEMENTATION-PLAN's `## Slice Progress` row matching the primitive's expected status:**
   - `slice-start` → first row at `Not Started` (you can't start what's already running).
   - `slice-review` / the per-slice commit (4c.6) → row at `In Progress` (you can't review or commit something not yet implemented).
3. **Error** — never silently pick. If priority 2 yields multiple candidates, return a failure to the orchestrator listing all candidates. Write no stop note to `SDD/orchestration/progress.md` — the orchestrator names the slice and re-spawns.

## Inert-Mode Gate

This body requires `delivery_mode: per-slice`. **Slice primitives are inert in whole-feature mode** (per REQ-007 + EDGE-002). The first action of this body is to read `delivery_mode:` from the active SPEC's frontmatter and short-circuit when not `per-slice`.

### Step 1: Use the active SPEC named in your prompt

The active SPEC is the path in your prompt. Do not list `SDD/requirements/` to find or choose one — a repository holds several specs as soon as a second feature or tier exists, and only the orchestrator knows which is active.

- Path present and readable → use it.
- Path missing from your prompt, or the file is missing or unreadable → return a failure to the orchestrator: `Active SPEC path missing or unreadable: <path or "not given">. slice-start cannot proceed.` No partial state writes; no stop note.

### Step 2: Read `delivery_mode:` from the SPEC frontmatter

The canonical enum is exactly `{whole-feature, per-slice}` (lowercase, hyphenated). Branch:

- **`per-slice`** → continue with this body's normal behavior (Step 3 onward).
- **`whole-feature`** → emit the REQ-007 verbatim inert message and exit cleanly with NO partial state writes:

  ```
  This body requires `delivery_mode: per-slice` in the spec frontmatter. Current spec uses `delivery_mode: <value>`. Use the implementation scaffolding step instead, or set `delivery_mode: per-slice` in your spec and re-run the planning phase.
  ```

  Where `<value>` is the spec's value.
- **Field missing** → fail: `Missing delivery_mode in <spec-path>. Allowed values: whole-feature, per-slice. Edit the spec frontmatter and re-run the planning phase.` No state is written.

  **Typo-detection hint (resolves L-7):** when the field is missing, ALSO grep the spec frontmatter for any line matching `mode:` (case-insensitive). If a near-miss field is found (e.g., `delvery_mode:`, `Delivery_mode:`, `delivery-mode:`), append a one-line hint to the error: `Hint: detected nearby field '<offending-line>' — possible typo of 'delivery_mode:'?`.

- **Any other value** (typos like `per_slice`, `PerSlice`, `vertical-thread`, `whole_feature`, `delivry_mode` field-name typos, etc.) → fail per REQ-001 validation: `Invalid delivery_mode value '<value>' in <spec-path>. Allowed values: whole-feature, per-slice. Edit the spec frontmatter and re-run the planning phase (or use the implementation scaffolding step in whole-feature mode).` Do NOT silently fall through to the default branch.

## Slice-ID Validation (REQ-024 / SEC-003) — canonical regex shared across slice primitives

> **Canonical regex (single source of truth — resolves L-4):** the slice-ID validation regex `^SLICE-\d{3}[a-z]?$` is duplicated verbatim across `bodies/slice-start.md`, `bodies/slice-review.md`, `phases/protocols.md`, and `phases/implementation-per-slice.md`. **`slice-start` is the canonical home** for this regex; the other copies SHOULD cross-reference this section rather than re-deriving the pattern. Future changes (e.g., allowing 4-digit slice IDs `SLICE-####`) MUST be coordinated across all of them in a single commit; a drift between them would produce inconsistent regex enforcement at primitive boundaries. The optional single lowercase letter (`SLICE-005a`, `SLICE-005b`) exists for slices split during re-planning; it cannot carry `/`, `.`, or any other path character, so the traversal guarantee is unchanged.

Slice-ID arguments MUST be validated against the regex `^SLICE-\d{3}[a-z]?$` BEFORE being interpolated into any read or write path. This prevents directory-traversal attacks (a malicious arg like `../../etc/passwd` would otherwise bypass the path templates).

On regex mismatch, refuse with the REQ-007 message-discipline shape: name the offending value, name the canonical pattern, name the resolution. Example:

```
Invalid SLICE-ID argument '<arg>'. SLICE-ID must match the pattern SLICE-### (three digits, optionally one lowercase letter). Example: slice-start SLICE-002.
```

## `## Slice Progress` Table — Binding Schema (REQ-022)

The IMPLEMENTATION-PLAN's `## Slice Progress` table is the source of truth for slice state during implementation. Its schema is BINDING:

- **Columns:** `SLICE-ID | Name | Status | Acceptance check | Test result | Notes`.
- **Status enum (3 states, forward-only — no backwards transitions):** `Not Started`, `In Progress`, `Complete`.
- **Column-write authority:**
  - The implementation scaffolding step scaffolds the table (one row per `SLICE-XXX` from the SPEC's `## Delivery Slices` section).
  - `slice-start` flips `Status` from `Not Started` → `In Progress` for the active slice.
  - The orchestrator sets `Status` to `Complete` (terminal state), with `Test result` and `Notes`, as its last edit before the per-slice commit (step 4c.6), so that commit carries it. No slice body sets `Complete`.
- **FIRST-WRITE-WINS rule:** at most ONE slice may be at `Status: In Progress` at any time. Enforced by the EDGE-012 conflict check below.
- **SLICE-XXX uniqueness invariant:** SLICE-XXX values within a single IMPLEMENTATION-PLAN's `## Slice Progress` table MUST be unique; duplicate detection is the human reviewer's responsibility (tooling does not enforce).

## Step 3: Read the IMPLEMENTATION-PLAN named in your prompt and verify the `## Slice Progress` table

Read the IMPLEMENTATION-PLAN at the path in your prompt — do not list `SDD/implementation/` to find one. If the path is missing from your prompt, or the file is missing or unreadable, return a failure to the orchestrator naming it (no partial state writes; no stop note). Verify the plan contains a `## Slice Progress` section. If MISSING, halt per FAIL-007 with:

```
No '## Slice Progress' table found in <IMPLEMENTATION-PLAN-XXX-...md>. Either run the implementation scaffolding step to scaffold the table, or restore the table from a previous git commit. slice-start cannot proceed without the table.
```

No partial state writes; no fall-through to "first Not Started row" search on missing data.

## Step 4: Resolve the active SLICE-XXX

Apply the **Active-Slice Resolution Convention** above. For `slice-start`, the expected status is `Not Started`.

- **`[SLICE-ID]` provided:** use it (after regex validation). Verify the SLICE-XXX row exists in `## Slice Progress`; if missing, fail with: `SLICE-XXX not found in <IMPLEMENTATION-PLAN-XXX-...md>'s ## Slice Progress table. Available slice IDs: <list>. Either correct the argument or update the SPEC's ## Delivery Slices section and re-run the implementation scaffolding step.`
- **No argument, single `Not Started` row:** use it.
- **No argument, multiple `Not Started` rows (EDGE-010):** return a failure to the orchestrator listing all `Not Started` SLICE-IDs and Names; write no stop note. Do NOT silently pick the first.
- **No argument, zero `Not Started` rows:** if all slices are `Complete`, fail with: `All slices in <IMPLEMENTATION-PLAN-XXX-...md> are already Complete. Nothing to start.` If any is `In Progress`, fall through to the EDGE-012 conflict check.

## Step 5: EDGE-012 conflict — another slice is `In Progress`

If ANY row in `## Slice Progress` is at `In Progress` and is NOT the row being started, refuse with the friendly message naming the in-progress slice (per EDGE-012 spec text):

```
Cannot start <requested SLICE-XXX>: <other SLICE-XXX> is currently <state>. Resume the in-progress slice first (see slice-review and the per-slice commit, step 4c.6), or mark it abandoned by manually editing the Slice Progress row to a terminal state. Use slice-start --resume <other SLICE-XXX> to re-attach to the in-progress slice if context was lost.
```

This body does NOT regress the in-progress slice's state, does NOT silently switch active slice, and does NOT overwrite either row's transition timestamp. The forward-only invariant in REQ-022 holds at the primitive boundary.

**`--resume SLICE-XXX`:** if your prompt carries `--resume SLICE-XXX` and that SLICE-XXX is the row currently at `In Progress`, this is a slice start that was interrupted: proceed to Step 7 and re-attach without state regression — leave the row as it is (Step 8), carry the base commit forward (Step 9), and continue the implementation from what is already in the working tree (Step 10). See "Flag Inventory" below.

## Step 6: EDGE-013 conflict — slice is already `Complete`

If the requested SLICE-XXX row is at `Status: Complete`, REFUSE and return a failure to the orchestrator, with no partial state writes and no stop note:

```
SLICE-XXX is already Complete. A finished slice is not re-started: its row and review are the record of what was committed. Change its behaviour in a later slice, or re-plan.
```

Re-starting a `Complete` slice would overwrite acceptance-check evidence on the row. There is no override flag.

## Step 7: What the earlier slices left

The earlier slices are committed; their code is the only context carried from one slice to the next. Read it where this slice touches it, as Step 10 says.

## Step 8: Update the `## Slice Progress` table — flip Status to `In Progress`

Edit the IMPLEMENTATION-PLAN in place:

- Locate the row for the active SLICE-XXX.
- Change `Status` from `Not Started` → `In Progress`.
- Leave `SLICE-ID`, `Name`, `Acceptance check` UNCHANGED (column-write authority — see schema above).
- Reset `Test result` to `—` and `Notes` to `Started YYYY-MM-DD`.
- Under `--resume` the row is already `In Progress`: change nothing in it.

## Step 9: Update `progress.md`

Append an entry to `SDD/orchestration/progress.md` recording the slice start:

```markdown
## Slice <SLICE-XXX> - In Progress

- **Started:** YYYY-MM-DD HH:MM:SS
- **SPEC:** SPEC-XXX-<feature-name>
- **IMPLEMENTATION-PLAN:** SDD/implementation/IMPLEMENTATION-PLAN-XXX-<feature-name>-<date>.md
- **Ledger loaded:** Yes / No (first slice)
- **Flags:** <list of flags used, or "none">
- **Active-slice resolution:** <how the slice was resolved — explicit arg / single Not Started row / --resume>
- **Base commit:** <output of `git rev-parse HEAD` now, before any slice work; `none` if the repo has no commits>
```

The **Base commit** line is load-bearing: the slice stays uncommitted until its per-slice commit, so the slice review diffs the working tree against this commit. It is the only durable record of it — a resumed session reads it from here. On `--resume`, copy the base from the slice's earlier `In Progress` entry rather than re-reading HEAD; if the earlier run ended before writing one, HEAD is correct — the previous slice is committed and this one is not.

## Step 10: Implement the slice

In sdd-flow per-slice mode, **you implement the slice end-to-end in this same run** — the orchestrator spawns no separate implementation subagent. Implement the slice's REQ/EDGE/FAIL coverage (per its `Acceptance check` and `Modules touched`), with tests alongside each component, and run the acceptance check. **Harvested cases first:** with `evals: on`, when a case on this slice's `Evals:` line is marked `*(harvested: …)*` in the spec, build those cases by Step 11.6's points 1–4 and make the baseline run EVALS §2 (*A case harvested from a real trace*) describes before you change anything for them. **Before writing the first test, read the test integrity standard at the `TEST_INTEGRITY` path in your prompt, §1:** every test's expected value comes from the SPEC, it fails when the behaviour is broken, it runs the code that holds the logic, and it checks an outcome the spec names. Never make a failing test pass by weakening it, and never teach the code about the tests' inputs; where the SPEC requires a pre-existing test to change or go, add its line under `### Test Changes` in the IMPLEMENTATION-PLAN (create the heading if the plan has none). **Before the first edit, read the Fit Lens at the `FIT` path in your prompt, §5, and the design brief at the `BRIEF` path:** extend the code the brief's `## Builds on` names before adding any, add only the new files the brief names, and give each new function, class, file, or layer its one-line reason under `### New Structure` in the IMPLEMENTATION-PLAN. Follow the rolling ledger's learnings.

## Step 11: Prove the security rules the slice touches

Read the security standard at the `SECURITY` path in your prompt, §1 and §3. For each security rule that must hold on code this slice added or changed — an earlier slice's rule included, when this slice adds a path it must hold on — write a test that drives the real entry point with the adverse input or condition really present and asserts the denial the rule states. In a scratch copy of the working tree (TEST_INTEGRITY §8) remove the guard, run the test, see it fail; record one line per guard under `## Security Proofs` in the IMPLEMENTATION-PLAN. Every other requirement is held by the slice's real tests.

## Step 11.5: Follow the tracing standard (by the gate in your prompt)

Your prompt carries the line `tracing: on` or `tracing: off`. With `tracing: off`, or no such line, this step does not apply: the flow makes no tracing check on this work, and you are given no tracing paths. If the application has tests about tracing of its own — an entry-point test among them — they are part of its test suite and have to pass like any other test.

With `tracing: on`, your prompt also gives **TRACING** (the tracing standard), **OBS_RECORD** (the application's observability record — where its bootstrap module, entry-point wrapper, entry-point test, and trace run are), and **TRACE_TREE_SCRIPT**. Read TRACING's *Adding code to a traced application* and do what its five points say for the code you add, and nothing more. In this flow that means:

1. **Build the marked nodes as the spec marks them.** For a slice that is the marked nodes on this slice's `Traced nodes:` line — not those of later slices, which are not yours to build. An `[entry: …]` node is registered under exactly the method and path, or the function name, in its mark. An `[LLM, max N calls]` node makes at most `N` calls to a model in one request, your own retries included. An `[external: X]` node reaches the system its mark names.
2. **An entry point the framework does not see** — a job, a consumer, a command — goes through the wrapper OBS_RECORD names and, where the application keeps a registry of that kind of entry point, into the registry the entry-point test reads. A kind with no registry is outside that test; the wrapper is what traces it.
3. **Check with the trace run, after the tests pass.** Run the command OBS_RECORD gives, then look at what it recorded: `python3 <TRACE_TREE_SCRIPT> <span file> <env file>` prints the tree (the span file and the env file are named in OBS_RECORD; leave the env file out if it does not exist). Print it only — the review writes the trace-tree file, not you. Every marked node of yours should be there — judged as the review will judge it (an entry point by its name, a model call by the function span above it — or, in a tree with no function spans, by a count beneath its entry point — an external call by the system it reached). One that is missing, and is not marked `not exercised in tests`, means no test drives that call for real: write the test. Only when a model or external call ran and no instrumentation gave it a span do you add a span by hand, following the standard's capture policy and attribute rules.
4. **Leave no other span in the code,** and name no backend, exporter, or instrumentation library outside the bootstrap module.
5. **The entry-point test passes and the trace run completes** when you hand the work over.
6. **Where the plan cannot be followed** — a marked call turned out not to be needed, or one the plan does not show is — do not edit `### Planned call graph`, a `Traced nodes:` line, or the `tracing:` field. Record the difference and its reason under `### Implementation Deviations` in the IMPLEMENTATION-PLAN; the review reads it there. This is for a call that differs from the plan, never for a request that makes more model calls than its node's maximum.

## Step 11.6: Build the slice's evals (by the gate in your prompt)

Your prompt carries the line `evals: on` or `evals: off`. With `evals: off`, or no such line, this step does not apply: the flow checks nothing about what the model answers in this work, and you are given no evals paths. If the application already has an `evals/` directory, its test of the cases and checks is part of the test suite and has to pass like any other test; you add no case and make no eval run.

With `evals: on`, your prompt also gives **EVALS** (the evals reference), **EVAL_TEMPLATES** (the directory the eval run is rendered from), and **OBS_RECORD** (the application's observability record — it names the env file, shows how the application runs Python, and holds the `Eval command` row). Read EVALS §2 to §6 and do what they say for the cases that are yours, and nothing more. In this flow that means:

1. **Your cases.** For a slice that is the cases on this slice's `Evals:` line — not those of later slices, which are not yours to build. Only when that line says `none` is there nothing to build, and then one of two things: if `evals/run.py` does not exist either — no earlier work built a case — this step ends here, with nothing set up and nothing run, and your return says `no eval in scope`; if it exists, skip to point 4, because the cases built before this slice still have to pass. A line that names any case takes every point below, starting with point 2. Build those, each exactly as the spec states it — the same input, a check that asks everything its "must contain" and "must not contain" ask, the same requirement and kind — and write no case of your own.
2. **Set up, if nothing is there yet.** When `evals/run.py` does not exist, render the three templates and fill the `Eval command` row of OBS_RECORD, as EVALS §3 (*Setting it up*) says. When it exists, render nothing: add your cases to `evals/cases.jsonl`, and extend `evals/task.py` only where a case needs an input it cannot take yet.
3. **Give every hard case its examples** — at least one known-bad and one known-good answer, written as EVALS §3 says. They are yours to write; the spec has none.
4. **Run what calls no model first.** The eval command with `--self-test`, then the application's tests: the test of the cases and checks is among them and has to pass.
5. **Then make your own eval run,** as EVALS §4 (*Who makes which run*) says: no `--experiment`, `--out` a file outside the repository. Every hard case of yours — and every one built before yours — should pass all its runs when you hand the work over. A case that fails is fixed in the application: its prompt, the code around the call. Never in the case (EVALS §6). Make at most three eval runs: if a hard case still fails after the third, stop, and say in your return which cases fail and what the last `Result:` line was — the review takes it from there. The baseline run for harvested cases, made before the work they check (EVALS §2), is one of the three.
6. **If the run ends `UNAVAILABLE`,** the model could not be reached from where you run: say so in your return, with the `Result:` line, and claim nothing about the cases. That is not a failure of your work, and it is not a result either.
7. **Record it.** Under `## Test Implementation` in the IMPLEMENTATION-PLAN, one line: `Evals built: <cases> — own run: <the Result: line>`. For each harvested case, also the `Harvested, before any change:` line of its baseline run (EVALS §2).
8. **Never edit** the spec's `### Evals`, an `Evals:` line, a `Sign-off:` line, or the `evals:` field. If a case cannot be built as the spec states it, record why under `### Implementation Deviations` and build it as near as the application allows; the review reads it there and raises the difference.

## Step 12: Append the `Implemented` entry to `progress.md`

```markdown
## Slice <SLICE-XXX> - Implemented

- **Acceptance check:** <test name> — passing | failing: <reason>
```

This line is a phase-detection marker: it tells a resumed run that implementation finished and the slice review is next.

## Step 13: Return a bounded result

Return a bounded result (≤200 words + artifact paths) summarizing:

- The active SLICE-XXX, its Name, and its Acceptance check (verbatim from the row), and whether it passes.
- The `Modules touched` field from the SPEC's `### SLICE-XXX:` block (read SPEC's `## Delivery Slices` section).
- The security rules you proved, by ID.
- With `tracing: on`: whether every node on the slice's `Traced nodes:` line showed in the trace run's tree, and any difference you recorded under `### Implementation Deviations`.
- With `evals: on`: the cases you built, and the `Result:` line of your own eval run — or that it ended `UNAVAILABLE`, or that the slice's `Evals:` line is `none`.
- Next step: `slice-review` for SLICE-XXX.

## Flag Inventory (REQ-025 — applies to `slice-start`)

This body recognizes ONE flag. The orchestrator decides when to pass it (`phases/implementation-per-slice.md` → 4a); this body only says what it does.

| Flag | Semantics | Default (without flag) | Orchestrated mode |
|------|-----------|------------------------|-------------------|
| `--resume SLICE-XXX` | Re-attach to an `In Progress` slice whose start was interrupted. Does NOT regress state, does NOT switch active slice. | EDGE-012 refusal fires when another slice is already `In Progress`. | Passed when the slice's row is already `In Progress` and it has no `Implemented` entry. |

**Convention boundaries:**

- Every `--<flag>` is a literal argument; absence is the default behavior.
- There is no destructive override: a `Complete` slice is never re-started (Step 6).

## Path Conventions (REQ-016)

This body emits paths under the SDD 2.0.0 layout:

- `SDD/requirements/SPEC-XXX-[feature-name].md`
- `SDD/implementation/IMPLEMENTATION-PLAN-XXX-[feature-name]-[date].md`
- `SDD/orchestration/progress.md`

## Refusal-Message Discipline (REQ-007 / UX-001)

Every refusal path in this body follows the REQ-007 message-discipline standard:

1. Name the detected condition (e.g., "another slice is In Progress", "SLICE-XXX is already Complete", "no Slice Progress table").
2. Name the resolution path (`--resume`, a later slice or a re-plan, implementation scaffolding step, manual edit).
3. Exit cleanly without partial state writes.

The friendly-message tone matches the existing SDD convention (no cryptic stacktraces; no silent fallthroughs; no surprise behavior).
