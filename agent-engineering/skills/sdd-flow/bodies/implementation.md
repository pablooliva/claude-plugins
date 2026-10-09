# Initialize Implementation Phase

You are a spawned subagent in an orchestrated /sdd-flow run. Your prompt provides resolved artifact paths and identifiers — use them verbatim. This file is your complete instruction set. Do not spawn subagents or invoke slash commands/skills, even if an Agent/Task tool is available — the flow’s flat-orchestration contract forbids it; all work happens inline in your own context.

IMPLEMENTATION PHASE INITIALIZATION

Starting implementation phase based on completed specification.

## Initial Context Load

1. **Read Progress File:**
   - Load `SDD/orchestration/progress.md` to understand planning completion status
   - The specification is the path in your prompt — do not take it from this file, which may also reference earlier features' specs
   - Note any important context from the planning phase

2. **Read Ubiquitous Language Glossary:**
   - If `SDD/UBIQUITOUS_LANGUAGE.md` exists, load it. Use the canonical names from this glossary in code, comments, commit messages, and tests — in preference to any synonyms or near-synonyms. If implementation surfaces a term not in the glossary, do not silently invent one; flag it for addition during the research-complete phase of a future cycle (or during this cycle's planning if still open).
   - If the glossary does not exist, proceed without it.

3. **Update Progress for Implementation Phase:**
   - Add a new implementation section to `SDD/orchestration/progress.md`
   - IMPORTANT: Preserve all research and planning phase information - do NOT delete or reset it
   - Add reference to the IMPLEMENTATION-PLAN document being created
   - Document the transition from planning to implementation phase

4. **Read `delivery_mode:` from the Spec Frontmatter:**
   - Open `SDD/requirements/SPEC-[###]-[feature-name].md` and read the YAML frontmatter (the block between `---` markers at the top of the file).
   - Extract the `delivery_mode:` value. The canonical enum is exactly `{whole-feature, per-slice}` (lowercase, hyphenated).
   - **Validation rule (binding):**
     - Absent field → silent default to `whole-feature`. No log line. This is the documented default behavior.
     - Exact match `whole-feature` → continue with the **whole-feature branch** below.
     - Exact match `per-slice` → continue with the **per-slice branch** below.
     - Any other value (typos like `per_slice`, `PerSlice`, `vertical-thread`, `whole_feature`, etc.) → fail fast with: `Invalid delivery_mode value '<value>' in <spec-path>. Allowed values: whole-feature, per-slice. Edit the spec frontmatter and re-run implementation-start.` Do NOT silently fall through to the default branch.
   - Record the resolved mode in the implementation tracker's Executive Summary (a `**Delivery mode:**` field below `**Status:**`) and in `SDD/orchestration/progress.md`.

## Implementation Setup

1. **Use the IMPLEMENTATION-PLAN Path in Your Prompt:**
   - **The file already exists → continue with it.** This is the normal case, not a conflict: the second and later chunks of a large feature append to the plan the first chunk created, and a re-scaffold after a re-plan rewrites parts of the existing plan as your prompt's post-replan note says. Read it, keep what earlier chunks recorded, and add to it. Never recreate it, renumber it, or archive it. Skip step 2.
   - **No file at that path → create it** (step 2).
   - **Your prompt names no plan path → return a failure to the orchestrator:** `IMPLEMENTATION-PLAN path missing from the prompt. Implementation cannot proceed.` Do not derive a path yourself and do not list `SDD/implementation/` to find a plan — a plan there may belong to another feature or an earlier tier. Create nothing and write no stop note.

2. Create `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[YYYY-MM-DD].md` document where:
   - `[###]` matches the specification and research document numbers (e.g., if using SPEC-042, create IMPLEMENTATION-PLAN-042)
   - `[feature-name]` is a kebab-case description matching the spec document (e.g., "user-authentication", "csv-export")
   - `[YYYY-MM-DD]` is today's date
   - Full example: `IMPLEMENTATION-PLAN-042-user-authentication-2025-10-20.md`

## Prerequisite Verification

Before starting implementation:

1. **Use the Specification Named in Your Prompt:**
   - The specification is the `SDD/requirements/SPEC-[###]-[feature-name].md` path in your prompt. Do not list `SDD/requirements/` to find or choose one — other specs there belong to earlier features and tiers
   - If the path is missing from your prompt, or the file is missing or unreadable, return a failure to the orchestrator naming it; write no stop note
   - Verify the specification is complete (has all sections filled)

2. **Confirm Specification Completeness:**
   - Executive Summary: Complete with research foundation reference
   - Intent: Clear problem statement and solution approach
   - Success Criteria: All functional and non-functional requirements defined
   - Edge Cases: Research-backed scenarios with desired behaviors (EDGE-XXX)
   - Failure Scenarios: Graceful degradation strategies defined (FAIL-XXX)
   - Implementation Constraints: Context requirements and essential files listed
   - Validation Strategy: Test scenarios and acceptance criteria defined

3. **Validate Specification Quality:**
   - If any specification sections are missing or incomplete, warn the user
   - Check if the planning phase was completed (look for completion marker in progress.md)
   - If not complete, warn: "Specification phase may not be complete. Consider completing the planning phase first if needed."
   - Suggest reviewing the specification for completeness before implementation

## Implementation Document Structure

Create the implementation tracking document using this enhanced template. **The template is mode-aware:** the `## Slice Progress` section at the bottom is populated only when `delivery_mode: per-slice`. In `whole-feature` mode (the default), omit that section entirely — the rest of the template is unchanged from the pre-2.0.0 implementation-tracker shape (only the filename/path change applies).

```markdown
# IMPLEMENTATION-PLAN-[###]-[feature-name]: [Feature Description]

## Executive Summary

- **Based on Specification:** SPEC-[###]-[feature-name].md
- **Research Foundation:** RESEARCH-[###]-[feature-name].md
- **Start Date:** [YYYY-MM-DD]
- **Author:** Claude (with [user's name if known])
- **Status:** In Progress/Testing/Complete
- **Delivery mode:** whole-feature | per-slice  (read from SPEC frontmatter; canonical enum is exactly these two values)

## Specification Alignment

### Requirements Implementation Status
- [ ] REQ-001: [Requirement description] - Status: Not Started/In Progress/Complete
- [ ] REQ-002: [Requirement description] - Status: Not Started/In Progress/Complete
- [ ] PERF-001: [Performance requirement] - Status: Not Started/In Progress/Complete
- [ ] SEC-001: [Security requirement] - Status: Not Started/In Progress/Complete

### Edge Case Implementation
- [ ] EDGE-001: [Edge case name] - Implementation status
- [ ] EDGE-002: [Edge case name] - Implementation status

### Failure Scenario Handling
- [ ] FAIL-001: [Failure scenario] - Error handling implemented
- [ ] FAIL-002: [Failure scenario] - Error handling implemented

## Implementation Progress

### Completed Components
- [Component/Feature]: [Brief description and files modified]
- [Component/Feature]: [Brief description and files modified]

### In Progress
- **Current Focus:** [Specific component being implemented]
- **Files Being Modified:** [file paths with line ranges]
- **Next Steps:** [Immediate next actions]

### Blocked/Pending
- [Issue/Dependency]: [Description and resolution plan]

## Test Implementation

### Web-Facing Behavior
- **Feature has web-facing behavior (UI, JS, HTMX, browser flows):** Yes / No
- **E2E tests required:** Yes / No / N/A — [justification if N/A]

### Unit Tests
- [ ] [Test file]: Tests for [component/requirement]
- [ ] [Test file]: Tests for [edge case EDGE-XXX]

### Integration Tests
- [ ] [Test file]: Integration test for [API endpoint/feature flow]
- [ ] [Test file]: Tests for [failure scenario FAIL-XXX]

### E2E Tests (Playwright — if web-facing)
- [ ] [Test file]: Browser test for [critical user flow]
- [ ] [Test file]: Browser test for [HTMX interaction / form submission / JS behavior]

### Test Coverage
- Unit Tests: [X] tests — [X]% coverage
- Integration Tests: [X] tests
- E2E Tests: [X] tests (or N/A)
- Target Coverage: [As specified in SPEC]
- Coverage Gaps: [Areas needing additional tests]

### Test Changes
[One line per pre-existing test that was changed, skipped, or removed — `None.` when there is none]
- [test file::name]: [what changed] — required by [REQ-XXX]

## Technical Decisions Log

### Architecture Decisions
- [Decision]: [Rationale based on specification constraints]
- [Decision]: [Trade-off analysis and choice made]

### Implementation Deviations
- [Deviation from spec]: [Reason and impact assessment]
- [Deviation from spec]: [Stakeholder approval needed/obtained]

## Performance Metrics

- [Metric from PERF-XXX]: Current: [value], Target: [value], Status: [Met/Not Met]
- [Metric from PERF-XXX]: Current: [value], Target: [value], Status: [Met/Not Met]

## Security Validation

- [ ] Authentication implemented per SEC-XXX requirements
- [ ] Input validation added for [specific inputs]
- [ ] Authorization checks in place for [specific operations]

## Documentation Created

- [ ] API documentation: [file path or N/A]
- [ ] User documentation: [file path or N/A]
- [ ] Configuration documentation: [file path or N/A]

## Context Management

### Essential Files Loaded
- [file path]:[lines] - [purpose]
- [file path]:[lines] - [purpose]

## Session Notes

### Critical Discoveries
- [Discovery]: [Impact on implementation]
- [Discovery]: [Required specification adjustment]

### Next Priorities
1. [Specific task to complete next]
2. [Following priority]
3. [Subsequent priority]

## Control Site Status

> **Required in both delivery modes.** One row per control (any SPEC rule that must hold on every path — see `references/enforcement-sites.md` §1). Scaffold it empty; `slice-retro` (per-slice) or the completion step (whole-feature) fills `Independent sites`, `Latest diff`, and `Status`. `Status` is `Partial` until the control has been checked against a blind, independent count (`references/enforcement-sites.md` §6) — **a control with no independent count is never `Complete`**.

| Control | Implementer sites | Independent sites | Latest diff | Status | Open (iii) owners |
|---------|-------------------|-------------------|-------------|--------|-------------------|
| [SPEC ID] | [n] | — | — | Partial | — |

## Slice Progress

> **Required only when `delivery_mode: per-slice`.** Omit this section entirely when `delivery_mode: whole-feature` (the default). When per-slice, the planning phase's `## Delivery Slices` from the SPEC seeds this table; the slice-start phase initializes the row to `In Progress`; the slice-retro phase updates `Status` (to `Acceptance Check Passing`), `Test result`, and `Notes` only (never `SLICE-ID`, `Name`, or `Acceptance check`); the orchestrator sets `Complete` just before the per-slice commit. State transitions are forward-only — `Not Started` → `In Progress` → `Acceptance Check Passing` → `Complete`. SLICE-XXX values must be unique within this table.

| SLICE-ID  | Name              | Status        | Acceptance check                            | Test result | Notes |
|-----------|-------------------|---------------|---------------------------------------------|-------------|-------|
| SLICE-001 | [from SPEC]       | Not Started   | [from SPEC's Acceptance check field]        | —           | —     |
| SLICE-002 | [from SPEC]       | Not Started   | [from SPEC's Acceptance check field]        | —           | —     |

**Status enum (binding):** `Not Started`, `In Progress`, `Acceptance Check Passing`, `Complete`. Any "stuck" condition lives in the rolling ledger's `Open recommendations awaiting user decision` section, NOT the Status column. The implementation-start phase scaffolds the table; the slice-start phase flips Status to `In Progress`; the slice-retro phase writes `Status`/`Test result`/`Notes` after the slice's review-and-fix loop completes; the orchestrator sets `Complete` as its last edit before the slice's commit.
```

## Implementation Process

1. **Load Specification Foundation:**
   - Read the complete SPEC-XXX document
   - Identify all requirements, edge cases, and failure scenarios
   - Note essential files and context constraints

2. **Branch on `delivery_mode:`:**
   - The mode was already resolved in Initial Context Load step 4. Branch behavior here:
   - **`whole-feature` (default):** Implement the feature in a single tracked pass against the full REQ/EDGE/FAIL list. Update the IMPLEMENTATION-PLAN's `Specification Alignment` checkboxes as you complete each item. Behavior is bit-for-bit identical to the pre-2.0.0 implementation-tracker flow apart from the filename/path change. **Omit the `## Slice Progress` section from the tracker entirely.** Record enforcement sites as you go (Implementation Process step 6).
   - **`per-slice`:** **Scaffold-only mode — you implement nothing.** Populate the `## Slice Progress` table from the SPEC's `## Delivery Slices` section (one row per `SLICE-XXX`, copying `Name` and `Acceptance check` from the SPEC; `Status` initialized to `Not Started`; the table enforces forward-only state transitions). Complete the rest of the tracker scaffold (including an empty `## Control Site Status` table and the web-facing determination from Implementation Process step 3, if determinable from the SPEC), append your progress.md entry, and **return**. The orchestrator drives the per-slice cycle (implement → review → retro → commit, one subagent per slice) from the table you scaffolded — slice subagents do all implementation. Skip the remaining Implementation Process steps; they are whole-feature-only. If your prompt marks this run as a post-replan re-scaffold, write a FRESH `## Slice Progress` table from the revised SPEC (the orchestrator has already archived the prior table under `## Archived Slice Progress (pre-replan)`).

3. **Set Up Development Environment:**
   - Load essential files identified in specification
   - Verify test framework is configured
   - Check for existing related code to build upon
   - **Identify whether the feature has web-facing behavior** (UI pages, client-side JS, HTMX interactions, CSP changes, multi-step browser flows). Record this determination in the IMPLEMENTATION-PLAN document. This drives whether E2E tests are required.

4. **Begin Incremental Implementation:**
   - Start with core functionality (primary success path)
   - Implement one requirement at a time
   - Write tests alongside every component — do not defer test writing
   - **Read the test integrity standard at the `TEST_INTEGRITY` path in your prompt, §1, before writing the first test.** Every test you write is held to it: its expected value comes from the SPEC, it fails when the behaviour is broken, it runs the code that holds the logic, and it checks an outcome the spec names. The review that follows breaks your code to see whether your tests notice, and probes it with inputs your tests do not use
   - **A failing test is never made to pass by weakening it, and the code is never taught about the tests' inputs** (§1). Where the SPEC requires a pre-existing test to change or go, change it and add its line under `### Test Changes` in the IMPLEMENTATION-PLAN
   - For every feature, consider all three test types:
     - **Unit tests** (always required): isolated logic, with stand-ins only for what lies outside the application
     - **Integration tests** (required if API endpoints are involved): test via API test client with mocked external services
     - **E2E tests** (required if web-facing behavior exists): Playwright browser tests against the real running stack, in the project's E2E test directory (check CLAUDE.md or equivalent for the project-specific path)
   - If the feature is web-facing, E2E tests are **mandatory**, not optional
   - Validate against specification criteria continuously

5. **Track Progress Rigorously:**
   - Update IMPLEMENTATION-PLAN document after each component completion
   - Mark requirements as implemented in the tracking document
   - Document any deviations or discoveries immediately

6. **Record Enforcement Sites and Per-Site Mutation Evidence (whole-feature):**
   - Read the enforcement-site standard at the `STANDARD` path in your prompt (`references/enforcement-sites.md`) — it defines **control**, **enforcement site**, **gap**, the **per-site mutation standard**, and the **three dispositions**.
   - For every control in the SPEC (any rule that must hold on every path — guards, refusals, write controls, output contracts, invariants, security controls; not only `SEC-xxx`), record every site in `SDD/implementation/sites/SITES-IMPL-[feature-name].md` under `## Site Inventory`, in the exact table shape of the standard §4 (`Slice` = `—`; File and Symbol written plain, e.g. `<module>`). If `SDD/implementation/sites/SITE-CONVENTIONS-[feature-name].md` exists, file and key every site by its rules (standard §4.2). If you are one implementation chunk of several, add and update rows for your chunk; do not delete earlier chunks' rows unless the site no longer exists in the working tree.
   - Run one mutation per site: delete exactly that site, run the tests, confirm at least one fails, restore, confirm the file is exactly what it was before the deletion (keep a copy, or compare `git diff -- <file>` taken before and after — the work is uncommitted, so that diff is not empty to begin with). Record `(i)` with the failing test; where the site genuinely cannot be proven alone, record `(ii)` with the argument written as a comment AT the site, or `(iii)` with a named owner and follow-up. Never mutate shared machinery as a stand-in for its call sites.
   - For output / stream contracts (stdout, stderr, exit codes), write at least one **real-subprocess** test per path class asserting on the actual bytes — `CliRunner` / `capsys` tests do not count toward this.
   - Fill `Implementer sites` in `## Control Site Status`; leave `Status` at `Partial`.
   - **Do not leak the list.** Site comments carry no counts, indices, or greppable site tags; your `progress.md` entry names the inventory path only. A blind, independent count (Step 4a.5) runs after you and is diffed against your inventory — every site it finds that you did not list becomes a HIGH finding.

7. **Follow the Tracing Standard (whole-feature, by the gate in your prompt):**

   Your prompt carries the line `tracing: on` or `tracing: off`. With `tracing: off`, or no such line, this step does not apply: the flow makes no tracing check on this work, and you are given no tracing paths. If the application has tests about tracing of its own — an entry-point test among them — they are part of its test suite and have to pass like any other test.

   With `tracing: on`, your prompt also gives **TRACING** (the tracing standard), **OBS_RECORD** (the application's observability record — where its bootstrap module, entry-point wrapper, entry-point test, and trace run are), and **TRACE_TREE_SCRIPT**. Read TRACING's *Adding code to a traced application* and do what its five points say for the code you add, and nothing more. In this flow that means:

   1. **Build the marked nodes as the spec marks them.** In whole-feature mode that is every marked node of the spec's `### Planned call graph` that the requirements given to you build — all of them when you implement the whole feature, and when the work is split into chunks, the nodes of your chunk; a node a later chunk builds is not yours, and is not missing. An `[entry: …]` node is registered under exactly the method and path, or the function name, in its mark. An `[LLM, max N calls]` node makes at most `N` calls to a model in one request, your own retries included. An `[external: X]` node reaches the system its mark names.
   2. **An entry point the framework does not see** — a job, a consumer, a command — goes through the wrapper OBS_RECORD names and, where the application keeps a registry of that kind of entry point, into the registry the entry-point test reads. A kind with no registry is outside that test; the wrapper is what traces it.
   3. **Check with the trace run, after the tests pass.** Run the command OBS_RECORD gives, then look at what it recorded: `python3 <TRACE_TREE_SCRIPT> <span file> <env file>` prints the tree (the span file and the env file are named in OBS_RECORD; leave the env file out if it does not exist). Print it only — the review writes the trace-tree file, not you. Every marked node of yours should be there — judged as the review will judge it (an entry point by its name, a model call by the function span above it — or, in a tree with no function spans, by a count beneath its entry point — an external call by the system it reached). One that is missing, and is not marked `not exercised in tests`, means no test drives that call for real: write the test. Only when a model or external call ran and no instrumentation gave it a span do you add a span by hand, following the standard's capture policy and attribute rules.
   4. **Leave no other span in the code,** and name no backend, exporter, or instrumentation library outside the bootstrap module.
   5. **The entry-point test passes and the trace run completes** when you hand the work over.
   6. **Where the plan cannot be followed** — a marked call turned out not to be needed, or one the plan does not show is — do not edit `### Planned call graph`, a `Traced nodes:` line, or the `tracing:` field. Record the difference and its reason under `### Implementation Deviations` in the IMPLEMENTATION-PLAN; the review reads it there. This is for a call that differs from the plan, never for a request that makes more model calls than its node's maximum.

## Implementation Approach

Do all investigation and research inline using your available tools (Read, Bash, Edit, Write). When you need to find implementation examples, locate test files, or discover utilities, use Read and Bash directly with grep/find. When you need to understand existing patterns or find reusable components, search inline. Document all findings directly in the IMPLEMENTATION-PLAN's Session Notes as you go.

## Quality Checklist

During implementation, continuously verify:

- [ ] Each requirement from SPEC is being addressed
- [ ] Tests are written for each component/requirement — not deferred
- [ ] Unit tests exist for all logic, with stand-ins only for what lies outside the application
- [ ] Every test meets TEST_INTEGRITY §1; no test was weakened, and no code branches on a test's inputs
- [ ] Integration tests exist for all API endpoints (via test client)
- [ ] Web-facing behavior identified (yes/no) — recorded in IMPLEMENTATION-PLAN document
- [ ] If web-facing: Playwright E2E tests written in the project's E2E test directory
- [ ] Edge cases (EDGE-XXX) have specific handling code
- [ ] Failure scenarios (FAIL-XXX) have error handling
- [ ] Performance requirements (PERF-XXX) are being measured
- [ ] Security requirements (SEC-XXX) are implemented
- [ ] Every control's sites are recorded in `SITES-IMPL-[feature-name].md`, each with a disposition and evidence
- [ ] Output / stream contracts have a real-subprocess test per path class
- [ ] `tracing: on` only: every marked node of the planned call graph that your requirements build shows in the trace run's tree (or is marked `not exercised in tests`); no other span was added; the entry-point test passes
- [ ] Code follows existing project patterns (discovered via inline search)
- [ ] Documentation is updated as needed

## Deliverable Expectations

A complete implementation must have:

- ✓ All specification requirements implemented and tested
- ✓ Complete IMPLEMENTATION-PLAN document tracking all progress
- ✓ All edge cases handled with tests
- ✓ All failure scenarios have graceful error handling
- ✓ Performance metrics meet specification targets
- ✓ Security requirements validated
- ✓ Unit tests present for all logic
- ✓ Integration tests present for all API endpoints
- ✓ E2E/Playwright tests present if feature has web-facing behavior (or explicitly marked N/A with justification)
- ✓ Test coverage meets project standards
- ✓ Documentation for any public APIs or configuration

## Implementation Workflow

### Phase Flow

```text
Load SPEC → Create IMPLEMENTATION-PLAN → Load Essential Files → Implement Requirements →
Write Tests → Validate Against Spec → Document Progress → Handle Edge Cases →
Measure Performance → Complete Implementation
```

---

Return a bounded summary (≤200 words + artifact paths) covering: what was implemented, which requirements are complete, which IMPLEMENTATION-PLAN sections are filled, and any deviations or discoveries recorded.

Begin implementation now using the specification as your authoritative guide. Create the `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[YYYY-MM-DD].md` document and start systematic implementation against specification criteria.
