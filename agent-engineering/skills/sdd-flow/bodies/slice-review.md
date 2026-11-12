# Review a Vertical Slice

You are a spawned subagent in an orchestrated /sdd-flow run. Your prompt provides resolved artifact paths and identifiers — use them verbatim. This file is your complete instruction set. Do not spawn subagents or invoke slash commands/skills, even if an Agent/Task tool is available — the flow’s flat-orchestration contract forbids it; all work happens inline in your own context.

You are conducting a per-slice code review for a single `SLICE-XXX` within a feature whose SPEC declares `delivery_mode: per-slice`.

## Active-Slice Resolution Convention (shared with slice-start, slice-retro, and the per-slice commit)

Per SPEC MODULE-002 active-slice fallback asymmetry:

1. **Explicit `[SLICE-ID]` argument** — if provided, use it. Validate against `^SLICE-\d{3}[a-z]?$` BEFORE interpolating into any path (REQ-024 / SEC-003 path-traversal prevention).
2. **IMPLEMENTATION-PLAN's `## Slice Progress` row** at `In Progress` or `Acceptance Check Passing` — this review covers implemented code, so it expects a non-`Not Started`, non-`Complete` row.
3. **Error** — never silently pick. If priority 2 yields multiple candidates, return a failure to the orchestrator listing them. Write no stop note to `SDD/orchestration/progress.md`.

## Inert-Mode Gate

This review requires `delivery_mode: per-slice`. **Slice commands are inert in whole-feature mode** (per REQ-007 + EDGE-002).

### Step 1: Use the active SPEC and IMPLEMENTATION-PLAN named in your prompt

The active SPEC and the IMPLEMENTATION-PLAN are the paths in your prompt. Do not list `SDD/requirements/` or `SDD/implementation/` to find or choose one — a repository holds several specs as soon as a second feature or tier exists, and only the orchestrator knows which is active.

If either path is missing from your prompt, or the file is missing or unreadable, return a failure to the orchestrator: `Active SPEC or IMPLEMENTATION-PLAN path missing or unreadable: <path or "not given">. Slice review cannot proceed.` Write no review and no stop note.

### Step 2: Read `delivery_mode:` from the SPEC frontmatter

The canonical enum is exactly `{whole-feature, per-slice}` (lowercase, hyphenated). Branch:

- **`per-slice`** → continue with this review's normal behavior.
- **`whole-feature`** → emit the REQ-007 verbatim inert message and exit cleanly with NO partial state writes:

  ```
  This review requires `delivery_mode: per-slice` in the spec frontmatter. Current spec uses `delivery_mode: <value>`. Use whole-feature implementation mode instead, or set `delivery_mode: per-slice` in your spec and re-run the planning phase.
  ```

- **Field missing, or any other value** → fail per REQ-001 validation: `Invalid delivery_mode value '<value>' in <spec-path>. Allowed values: whole-feature, per-slice. Edit the spec frontmatter and re-run the planning phase.`

## Slice-ID Validation (REQ-024 / SEC-003)

Slice-ID arguments MUST be validated against the regex `^SLICE-\d{3}[a-z]?$` BEFORE being interpolated into any read or write path. On regex mismatch, refuse with the REQ-007 message-discipline shape: `Invalid SLICE-ID argument '<arg>'. SLICE-ID must match the pattern SLICE-### (three digits, optionally one lowercase letter).`

> **Canonical regex source (resolves L-4):** see `bodies/slice-start.md` § "Slice-ID Validation" — that section is the canonical home for this regex. Any future change (e.g., 4-digit slice IDs) MUST be coordinated across `bodies/slice-start.md`, `bodies/slice-review.md`, `bodies/slice-retro.md`, `phases/protocols.md`, `phases/implementation-per-slice.md`, and `SCOPE_RE` in `scripts/site-diff.py` in a single commit.

## `## Slice Progress` Table — Binding Schema (REQ-022, reference)

- **Columns:** `SLICE-ID | Name | Status | Acceptance check | Test result | Notes`.
- **Status enum:** `Not Started`, `In Progress`, `Acceptance Check Passing`, `Complete`.
- This review does NOT modify the table directly; slice-retro updates `Status`/`Test result`/`Notes` after fix-and-rerun loops.

## Step 3: Resolve the active SLICE-XXX

Apply the **Active-Slice Resolution Convention** above. Expected statuses for this review: `In Progress` or `Acceptance Check Passing`.

- **`[SLICE-ID]` provided:** verify the row exists in `## Slice Progress` and is at `In Progress`/`Acceptance Check Passing`. If at `Not Started`, fail per EDGE-003: `No implementation found for SLICE-XXX. Run slice-start SLICE-XXX and implement the slice before review.`
- **No argument, single matching row:** use it.
- **No argument, multiple matching rows:** return a failure to the orchestrator listing the candidate rows; write no review and no stop note.
- **No argument, zero matching rows:** fail with: `No slice currently In Progress or Acceptance Check Passing in <IMPLEMENTATION-PLAN-XXX-...md>. Run slice-start <SLICE-XXX> first.`

## Step 4: Compute the slice's file set (REQ-004)

The slice's reviewable file set is computed as the **intersection** of:

1. The SPEC's `## Delivery Slices` → `### SLICE-XXX:` → `Modules touched` field — for each MODULE-XXX listed there, expand to the file paths the SPEC's `## Modules` section attributes to that module.
2. The files actually modified for this slice (the **git list**). **The slice is uncommitted while you review it** (the per-slice commit lands only after review, fixes, and retro), so compare the working tree against the slice's base commit `BASE` — never `BASE..HEAD`, which compares two identical commits and is always empty. SDD artifacts are excluded; they are not slice code:

   ```bash
   git diff --name-only --no-renames BASE -- . ':(exclude)SDD'           # tracked files modified, deleted, or renamed (old and new path)
   git ls-files --others --exclude-standard -- . ':(exclude)SDD'         # new, untracked files (git diff never lists these)
   ```

   `BASE` comes from your prompt. **Never guess it from HEAD** — after a resume or a re-run HEAD may already include the slice, and the diff would silently come back empty. If your prompt has no `BASE`, take it from the `Base commit:` line of the slice's latest `## Slice <SLICE-XXX> - In Progress` entry in `progress.md`. If neither exists, stop and return "BASE missing for SLICE-XXX" without writing a review. If `BASE` is `none` (the repo had no commits), use the empty tree from `git hash-object -t tree /dev/null` (computed, not hard-coded, so SHA-256 repositories work).

   Untracked files have no diff: review them **in full**.

**Disagreement handling (per REQ-004):** if the two lists agree, use the intersection. If they disagree, **prefer the git list** (it reflects what was actually modified) and surface the divergence as a `MEDIUM` finding in the review output:

```markdown
**MEDIUM finding — Slice scope divergence**: SPEC's `Modules touched` for SLICE-XXX lists <X>; the slice's working-tree changes against BASE list <Y>. Reviewing the git list; if the SPEC is correct, the slice touched files outside its declared modules (or missed ones inside them) and must be reconciled — either the code or the SPEC's `Modules touched` changes.
```

**Slice-scoped review caveat — shared/foundation files:** if the slice's file set includes a file that was also modified by an EARLIER slice (foundation file shared across slices), the review focuses on THIS slice's diff only — use `git diff BASE -- <path>` (working tree against the slice's base) to scope the diff. An untracked file has no diff — review it in full. The earlier slice's review owns the earlier slice's diff; this slice owns its own.

## Step 4.5: A re-review after a fix round (only when your prompt gives `SNAPSHOT`)

On a re-review whose fix round the orchestrator snapshotted, your prompt gives three more inputs: `SNAPSHOT`, a commit holding the working tree as it was before the fix; `FIXED`, one holding it as the fix left it; and `PREVIOUS REVIEW`, the review document the fix answered. The slice's first review read the whole slice and ran the whole suite; an earlier re-review may have run only some tests. This one checks that its findings are closed, reads what the fix changed, and runs the tests that change can affect — no more, until it finds nothing. If your prompt gives only some of the three, or git cannot diff the two commits, review the slice in full, as the steps below say, and write why on the `Re-review:` line; never take a snapshot yourself or guess one.

- **The change** is `git diff --name-only --no-renames SNAPSHOT FIXED -- . ':(exclude)SDD'`, and `git diff SNAPSHOT FIXED -- <file>` for what changed in a file. Both are commits, so a file the slice created and has not committed shows only what the fix did to it. Step 4 still runs as written: the file set is what Step 5.7 refers to.
- **Every finding of PREVIOUS REVIEW** gets one line in `## Earlier Findings` (template below): `closed` with the evidence — the change that closed it, the test that now fails without it — or `still open`. A finding still open is a finding of this review again, at its severity, numbered with the others, whether or not the code it is about changed.
- **Step 5 reads the change only.** Specification alignment for the requirements the changed code serves; test alignment and the Test Integrity Lens over the tests the fix added or changed, with `SNAPSHOT` in place of `BASE` for what changed; the Agentic-Surface Lens and the Fit Lens over the changed files; risk-tiered depth for the modules the change touches; the tier rules over what the fix added. Code the fix did not change was read by the previous review and is not read again: raise nothing there, except a HIGH you see without looking for it.
- **Step 5.5** walks the checklist items the change touches; mark each other one `N/A — unchanged since PREVIOUS REVIEW`.
- **Step 5.7** compares the change, not the whole git list, with the brief.
- **The tests you run are the ones the change can affect, not the whole suite.** The scoped set is:
  1. every test file the change adds or modifies;
  2. every test file that reaches a module the change modifies — directly, or through other application modules: search for the importers of each changed module, then for their importers, until you reach test files or find nothing new; a fixture or `conftest.py` that reaches it brings in every test file that uses it — and every test file that names a non-code file the change modifies (a prompts file, a config file, a data file);
  3. the slice's acceptance check, and the tests named in the evidence of each finding of PREVIOUS REVIEW.

  Run them with the project's own test command, narrowed to those files. **The scoped set is the whole suite** when the change touches what decides how tests are collected or run (`conftest.py`, `pytest.ini`, the test section of `pyproject.toml`, `jest.config.*`, `package.json` scripts, a CI workflow, a `Makefile` target), or when you cannot tell which tests reach a changed module or read a changed non-code file — a module loaded by name at run time, a plugin registry, a resource found by a pattern. Name the test files you ran, and the pass count, on the `Re-review:` line.
- **The whole suite at the end, when this review would pass the slice.** When every step is done and your findings are zero HIGH and zero MEDIUM, run the whole suite and then Step 5.8 in full, before you write the marker — when OBS_RECORD's trace run is the whole suite, that one run serves both, and when the scoped set was already the whole suite, that run counts and is not repeated. A test that fails there is a finding of this review: HIGH, `[needs-code-or-test]`, naming the test and the changed code it reaches; a Tracing Lens finding is counted as Step 5.8 says. Whenever you made this run, append `## Whole Suite <SLICE-XXX> iter <N> - <w> HIGH raised` to `progress.md` as the line directly before your marker, in the same append — `w` being the HIGH findings this run raised, zero included. The stall check sets them aside, and reads the line only when it sits directly above the marker it belongs to, so a line left by an earlier attempt at the same review never counts (`phases/implementation-per-slice.md` → 4c). With any finding before that point, make no whole-suite run beyond the two this step requires (a scoped set that is the whole suite; the trace run below): the next re-review reads the code that will be committed, and a slice leaves the loop only through a review that ran the whole suite on it.
- **Step 5.8 is deferred while findings remain.** This rule takes precedence over Step 5.8's own text and LENS's step 1 on a re-review. Run it in full, as on a first review, when this review would pass the slice (above), or when PREVIOUS REVIEW had a Tracing Lens finding — then its trace run checks that finding, and, when it is the whole suite, it is also the run the bullet above asks for. Otherwise write the body of `## Tracing Lens` as the one line `Deferred — this re-review found <n> finding(s) before it; the trace run is made by the re-review that finds none`.
- **Step 5.9 runs in full**, as on a first review: it reads the eval run of record the orchestrator made after the fix, so every case in scope is checked again.
- The marker, the iteration cap, and the stall check are unchanged.

## Step 5: Apply the code review process, scoped to the slice's files

Apply the following review process to the computed slice file set. The full review priority order applies:

1. **Specification Alignment (70%)** — verify the slice's REQ/EDGE/FAIL coverage from the SPEC. Restrict to REQ-XXX/EDGE-XXX/FAIL-XXX entries the slice's `Acceptance check` and `Modules touched` cite (a slice need not cover ALL of the feature's REQs — only its own).
2. **Context Engineering (20%)** — verify the slice's section in the IMPLEMENTATION-PLAN's `## Slice Progress` table reflects the work done; verify subagent calls (if any) are logged under `SDD/orchestration/subagent-calls/`; verify ledger consistency (no orphan references to slice work that the slice itself didn't capture).
3. **Test Specification Alignment (10%)** — verify tests exist and pass for the slice's contribution; verify test type coverage (unit / integration / E2E) is appropriate for the slice's surface.

**Test Integrity Lens (mandatory, every slice).** Item 3 asks whether the slice's tests exist and pass; this lens asks whether they are real — and whether the tests or the code were bent to get the green run. Read the standard at the `TEST_INTEGRITY` path in your prompt and run it **as written**, on this slice's requirements and the test files in this slice's changes: checks T1–T7 (§3), at the depth §4 gives for each module's `Risk:` tier, with `BASE` from your prompt and `### Test Changes` from the IMPLEMENTATION-PLAN. It is an overlay on the 70/20/10 split, and it runs after the slice's tests have passed. Make every mutation and probe in a scratch copy of the working tree (TEST_INTEGRITY §8), never in the working tree. Write the `## Test Integrity` section in the shape §6 gives; its findings are ordinary findings of this review, counted in the marker, each tagged `[needs-code-or-test]`. **A HIGH lens finding rejects the slice.** If your prompt has no `TEST_INTEGRITY` path, return a failure to the orchestrator naming it.

**Fit Lens (mandatory, every slice).** Read the standard at the `FIT` path in your prompt and run it **as written** over this slice's changes: its four questions (§1), reading the code around each changed area and not just the diff, and its grading (§3); Step 5.7 applies its footprint rule (§2). Write the `## Fit and Size` section; its findings are ordinary findings of this review, counted in the marker, and a MEDIUM rejects the slice. If your prompt has no `FIT` path, return a failure to the orchestrator naming it.

**Apply Risk-Tiered Review Depth** per the slice's `Modules touched` field. For each MODULE-XXX in the slice's `Modules touched`, read the `Risk:` field from the SPEC's `## Modules` section and apply the matching depth:

- **`high` risk** — full internals review: examine every function, branch, and data mutation in the module's files; flag any missing error paths, unvalidated inputs, or state-consistency gaps.
- **`medium` risk** — default review: examine public interfaces, key internal logic paths, and error handling; spot-check internals where the acceptance criteria indicate risk.
- **`low` risk** — tested-boundary review: verify the public contract and acceptance-check tests; skip deep internals unless a surface signal (irreversible action, security-sensitive path, financial data) warrants escalation.

**Implausible-tier override:** if a module is marked `low` but you observe it touches state that is irreversible, security-sensitive, or financial, escalate to `medium` or `high` and note the override in the Module Review Log.

**Agentic-Surface Lens (conditional).** Your prompt carries the resolved gate value. `agent_security: true` → run the lens over this slice's file set. `agent_security: auto` → run it only if this slice's files contain an agentic surface (model call, tool/MCP definition, agent memory or retrieval store, inter-agent messaging, or a model output driving an external action). **No catalog path in your prompt** → the gate is closed for this run (the spec says `false`): skip the lens. (A catalog path with no gate value: read `agent_security:` from the SPEC's frontmatter; absent means `auto`.) When it runs, read the control catalog at the path your prompt provides (`skills/ai-agent-security-review/references/owasp-ai-agent-controls.md`) and apply **Section 4 (Code-Level Checks)** only — Section 3 is spec-level and was covered at Step 3c. Also read the panel review named in your prompt (`SDD/reviews/PANEL-SPEC-*`): its `#### AI Agent Security Findings` block and that block's **Abuse cases to cover**. Code in this slice that contradicts a finding the spec panel resolved is a spec-to-code regression — raise it, at least MEDIUM. Report findings under a `## AI Agent Security` heading in the slice review document, with `file:line` evidence and concrete code resolutions; a HIGH finding rejects the slice. When the lens is skipped, record the one-line reason instead. Close the lens with the catalog Section 5 abuse cases this slice's files make relevant — starting from the panel review's **Abuse cases to cover** rows that this slice's files reach — each with its expected denial and the test that covers it. A test covers a case only if it performs the attack and asserts the expected denial. Raise every uncovered case as a HIGH finding (Resolution: the test to add) — it rejects the slice like any other HIGH.

**Respect the tier (tiered specs only).** When the SPEC's frontmatter carries `tier:` (the delivery tier — not a module's `Risk:` tier), read the tier standard at the **TIERS** path in your prompt and the SPEC's `## Deferred to Later Tiers` before raising findings. Do not raise a finding for behaviour that section lists as deferred — it was left out on purpose. Do raise one, at HIGH and titled `Unsafe to defer`, when the code breaches the standard's floor for a deferred item: most often a deferred case the code can reach that fails quietly instead of visibly. And raise one for anything **built ahead** — an abstraction, parameter, option, hook, flag, or dependency that no requirement of this tier uses: MEDIUM by default, HIGH when it adds a moving part (a dependency, stored state, a background process). The resolution is removal; "a later tier will need it" is not a justification. Everything this tier does build is reviewed in full.

## Step 5.5: Project Review Checklist Walk (conditional)

Projects often carry their own review checklist — a `CLAUDE.md`/`AGENTS.md` section listing pre-merge checks, a conventions doc, a PR template. **A checklist only fires if the reviewer is told to walk it**, so walking it is a required step here, not a nicety: the review process in Step 5 covers SPEC alignment, tests, and fit, and knows nothing about project-local obligations (register the feature in an index, update a status table, bump a compatibility matrix).

**Discovery (bounded — do not scan the whole repo).** In priority order, take the FIRST that exists:

1. An explicit checklist path passed in your spawn prompt.
2. A section in the repo-root `CLAUDE.md` or `AGENTS.md` whose heading names a review checklist, pre-merge checks, definition of done, or equivalent.
3. The same in a `CLAUDE.md`/`AGENTS.md` inside a directory the slice's file set touches (nearest-ancestor wins).
4. A repo-root `CODING_STANDARDS.md` — a standards file read at review time only (the `retro` skill proposes one for judgement-call rules).
5. `.github/PULL_REQUEST_TEMPLATE.md`, or a `docs/`-level review checklist the root doc points to by name.

If none exists, record one line in the review document — "No project review checklist found — searched: <the locations you checked>" — and move on. Absence is a normal outcome, not a finding.

**The walk.** When a checklist is found, walk **every** item explicitly, in order, and record a verdict per item. Never infer a blanket pass, never silently skip an item, and never summarize the checklist as "followed":

- **PASS** — verified, with the evidence (`file:line`, command output, or artifact path) that establishes it.
- **FAIL** — the item is not satisfied. Raise it as a normal review finding at the severity its content warrants, in the slice's findings section, and name the checklist item.
- **N/A** — genuinely out of scope for this slice's file set, with the one-line reason. "The slice didn't touch it" is only N/A when the item is scoped to code; a project-registry or status-table item usually applies to EVERY slice that adds a feature.

Items outside the slice's file set still apply when the checklist item is about project-level bookkeeping rather than code. Scope the walk to the slice's contribution, not to the slice's diff.

## Step 5.6: Severities and the marker

Every finding of this review is numbered once, at its severity, in `## Slice-Specific Findings`. **A review with no open HIGH and no open MEDIUM passes the slice.** A LOW finding is listed, not fixed: write each one under `## LOW Findings (listed, not fixed)` in the template below — the owner sees the list at the slice pause and in the end report — and nothing sends it to a fix round.

When the review document is written, append to `SDD/orchestration/progress.md` exactly `## Review <SLICE-XXX> iter <N> - APPROVED | REJECTED (<h> HIGH, <m> MEDIUM, <l> LOW)` (`N` = the `ITER` in your prompt — if your prompt gives no `ITER`, return a failure to the orchestrator rather than guess one). `APPROVED` when `h` and `m` are both zero, `REJECTED` otherwise. Always write all three counts, zeros included — the orchestrator reads them from this line. It is a phase-detection marker; do not paraphrase it.

## Step 5.7: Design Brief Check

Read the design brief at the path in your prompt (`SDD/requirements/DESIGN-[###]-[feature-name].md`; your prompt states its approved revision and tier). The user approved it before the spec was written; this step tells them whether the slice stayed inside it. Compare the git list from Step 4 against the brief's "What changes where" table as FIT §2 says — a file that existed at `BASE` against its areas, a file the slice adds (the untracked list from Step 4, and `git diff --name-only --no-renames --diff-filter=A BASE -- . ':(exclude)SDD'`) against the paths it names — and against its delivery outline, and write the `## Design Brief Check` section of the review document (template below).

**A changed file outside the footprint is a fit finding** (FIT §2): raise one per such file, graded by FIT §3, unless the SPEC's `## Deviations from Design Brief` records it. If your prompt names no design brief, write `No design brief — check skipped.` as the section's body.

## Step 5.8: Tracing Lens (conditional)

Your prompt carries the line `tracing: on` or `tracing: off` — the decision the orchestrator recorded when the spec was planned. Do not read the spec's `tracing:` field to decide for yourself.

- **`tracing: off`, or no such line** → skip this step and write the one line `Tracing lens skipped — tracing: off` as the body of the review document's `## Tracing Lens` section.
- **`tracing: on`** → your prompt also gives **LENS** (`references/tracing-lens.md` of this skill), **TRACING**, **OBS_RECORD**, **TRACE_TREE_SCRIPT**, and **TRACE_TREE**. Read LENS and run it as written, at `SCOPE = SLICE-XXX`: once the slice's tests pass, run the application's trace run, render the span file to TRACE_TREE with the script, and compare the tree with the marked nodes on this slice's `Traced nodes:` line and those of every slice before it. A later slice's nodes are never held against this one.

The spec planned which entry points, model calls, and external calls each slice brings into existence; this step checks that plan against what a real run recorded. Its findings come only from the fixed table in LENS, at the severities given there. They are ordinary findings of this review: number them with the others, count them in the progress marker, and let a HIGH reject the slice.

## Step 5.9: Eval Check (conditional)

Your prompt carries the line `evals: on` or `evals: off` — the decision the orchestrator recorded when the spec was planned. Do not read the spec's `evals:` field to decide for yourself.

- **`evals: off`, or no such line** → skip this step and write the one line `Eval check skipped — evals: off` as the body of the review document's `## Eval Check` section.
- **`evals: on`** → your prompt also gives **EVALS** (`references/evals.md` of this skill), **EVAL_TEMPLATES**, **OBS_RECORD**, the eval run line (`Eval run: …`), and — when the run wrote results — **EVAL_RESULTS**. Read EVALS and run its §7 as written, at `SCOPE = SLICE-XXX`: the cases on this slice's `Evals:` line and on those of every slice before it are in scope. A later slice's cases are never held against this one.

The spec states cases — written examples, and what must be true of what the model answers to them — and assigns each to a slice. Before this review the flow's main session put the cases built so far to the running application, and that run's last line and results are in your prompt. This step reads the run and the eval files against the spec. **You do not make an eval run yourself;** the one command of it you may run is `--self-test`, which calls no model (EVALS §4). Its findings come only from the fixed table in EVALS §7, at the severities given there. They are ordinary findings of this review: number them with the others, count them in the progress marker, and let a HIGH reject the slice. **A sign-off requirement** — one the spec lists under `### Manual Verification` with a line starting `- [ ] **Sign-off: ` — counts as met in every part of this review when it is implemented and its judged eval has its scores in the run of record (EVALS §9); that the user has not accepted it yet is not a finding.

## Step 6: Write the per-slice review document

Write the review output to:

```
SDD/reviews/REVIEW-SLICE-<SLICE-XXX>-<feature-name>-iter<N>-<YYYY-MM-DD>.md
```

`N` is the `ITER` in your prompt: one document per iteration, so a re-review never overwrites the review its fix answered.

Note the **hyphenated date format** `[YYYY-MM-DD]` (uniform across the new artifact families introduced by this feature — RETROSPECTIVE-SLICE, REVIEW-SLICE; resolves panel deferred LOW-13).

The review document follows the standard review template (`SDD/reviews/REVIEW-XXX-...md` shape) with these slice-specific additions:

```markdown
# Slice Review: SLICE-<XXX> — [slice name]

## Scope

**Slice:** SLICE-XXX
**Feature:** [feature-name]
**SPEC:** SDD/requirements/SPEC-XXX-[feature-name].md
**IMPLEMENTATION-PLAN:** SDD/implementation/IMPLEMENTATION-PLAN-XXX-[feature-name]-[date].md
**Slice file set (computed per REQ-004 intersection rule):**
- <file 1>
- <file 2>
- ...
**Source of file set:** <"intersection — agreement" / "git list preferred — divergence">
**Slice changes:** tracked changes in the working tree vs `BASE` = `<commit>`; untracked files reviewed in full: <list or "none">
**Re-review:** <"no — reviewed in full" | "after fix round <N>: SNAPSHOT `<sha>` → FIXED `<sha>`; PREVIOUS REVIEW <path>; the change: <files>; tests run: <"whole suite" | the test files>, <passed>/<collected>; whole suite at the end: <"yes, <passed>/<collected>" | "no — <n> finding(s) before it">">

## Earlier Findings

[Re-review only (Step 4.5): one line per finding of PREVIOUS REVIEW — `<#> <severity> <title>: closed — <evidence>` or `still open — finding <#> below`. On a review in full: `None — reviewed in full.`]

## Slice-Specific Findings

[All standard review sections apply, scoped to the slice's REQ/EDGE/FAIL entries.]

## Test Integrity

[The table, the mutation list, and the probe list, in the shape TEST_INTEGRITY §6 gives.]

## Fit and Size

[One line per fit finding (FIT §3) — `<#> <MEDIUM|LOW> <question or footprint>: <file:line> — <what to remove or merge>` — or `None.`]

## Project Review Checklist Walk

**Checklist source:** <path + section heading, or "none found — searched: ...">

| # | Checklist item | Verdict | Evidence / reason |
|---|----------------|---------|-------------------|
| 1 | <item verbatim> | PASS \| FAIL \| N/A | <`file:line`, command output, artifact path, or N/A reason> |

[FAIL rows are also raised as findings above, at their warranted severity.]

## Tracing Lens

[When the lens ran: the section in the shape LENS §7 gives — trace-tree path with its `Result:` line, the table of marked nodes compared, recorded deviations, spans in no request, and the findings. When it was skipped, the one line: "Tracing lens skipped — tracing: off".]

## Eval Check

[When the check ran: the section in the shape EVALS §7 gives — the eval run line, the results path, the table of cases in scope, the judge, and the findings. When it was skipped, the one line: "Eval check skipped — evals: off".]

## Module Review Log (Risk-Tiered Depth Applied)

| Module | Declared Risk | Depth Applied | Notes |
|--------|---------------|---------------|-------|
| MODULE-XXX | high \| medium \| low | full \| default \| boundary | [escalations, deviations, justifications] |

## LOW Findings (listed, not fixed)

[One line per LOW finding — `<#> <title> — <file:line>` — or `None.` Not fixed by this cycle; the owner sees the list.]

## Design Brief Check

- **Delivers:** [the brief's delivery-outline entry or entries this slice corresponds to, quoted — or "no matching outline entry", with what it is instead]
- **Outside the approved footprint:** [`None.` — or one line per changed file outside the footprint by FIT §2 (an existing file under no area, or a new file no row names) and no recorded deviation: the file, `new` or `changed`, why it was touched, and the number of its fit finding]

[`No design brief — check skipped.` when the feature has none.]

## Decision: [APPROVED / REJECTED]

[Standard review decision rationale. Any open HIGH or MEDIUM — the Test Integrity Lens, the Fit Lens, the Tracing Lens, and the Eval Check included — rejects the slice. LOW findings reject nothing.]
```

## Per-Slice Review Iteration Cap (REQ-013, reference — enforced elsewhere)

This review itself can be re-run any number of times. The **iteration cap of 3 with progress-stall check** (HIGH must strictly decrease across iterations; or MEDIUM when HIGH is zero) is enforced by the orchestrator's per-slice 4b/4c loop, NOT by this review. The fix step runs on HIGH and MEDIUM findings only. On cap or stall the flow stops and the findings go to the rolling ledger's `Open recommendations awaiting user decision` section. The loop is defined in `phases/implementation-per-slice.md` → 4c.

## Flag Inventory (REQ-025 — applies to slice review)

This review introduces NO flags of its own (per SPEC MODULE-002 + REQ-025: `slice-review [SLICE-ID]` — no flags introduced by this feature). The slice-start and slice-retro flags do NOT apply here.

For reference, the slice-command flag inventory across all four slice commands (REQ-025):

| Flag | Command | Default | Notes |
|------|---------|---------|-------|
| `--resume SLICE-XXX` | `slice-start` | Off | Re-attach to In Progress slice. |
| `--reconcile-ledger SLICE-XXX` | `slice-retro` | Off | Rebuild ledger from on-disk retros. |

## Path Conventions (REQ-016)

This review emits paths under the SDD 2.0.0 layout:

- `SDD/requirements/SPEC-XXX-[feature-name].md`
- `SDD/implementation/IMPLEMENTATION-PLAN-XXX-[feature-name]-[date].md`
- `SDD/implementation/slices/LEARNINGS-FEATURE-[feature-name].md` (kebab-case feature-name slug per CLARIFICATION OQ-B)
- `SDD/reviews/REVIEW-SLICE-XXX-[feature-name]-iter<N>-[YYYY-MM-DD].md`
- `SDD/orchestration/subagent-calls/`

## Refusal-Message Discipline (REQ-007 / UX-001)

Every refusal path follows the REQ-007 message-discipline standard: name the detected condition, name the resolution path, exit cleanly without partial state writes.
