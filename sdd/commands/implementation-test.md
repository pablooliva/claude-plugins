# Implementation Test Audit

IMPLEMENTATION TEST AUDIT

Verify that all features and functionality implemented during this implementation phase have adequate test coverage across all relevant test types.

IMPORTANT: This command requires Claude Sonnet. Before proceeding, check your current model ID in the system information. If you are NOT running on a Claude Sonnet model (e.g., claude-sonnet-*), immediately:

  1. Warn the user: "WARNING: This command requires Claude Sonnet but you're currently using [model name]. Please switch to Sonnet and try again."
  2. STOP all further processing - do not execute any of the instructions below.

## Context Utilization Check

Before loading any documents, check current context usage:

```text
Current context utilization: [X]%

If > 35%: ⚠️ Warning - Context usage is high ([X]%). Consider:
  - Using subagents for test discovery and analysis
  - Being prepared to run /implementation-compact soon

If > 40%: ⚠️ CRITICAL - Context usage is too high ([X]%).
  - You should run /implementation-compact before starting
  - Clear session and use /continue to resume with fresh context
```

## Workflow Position

```text
[/implementation-start] ──► [/implementation-compact] ──► [/continue]
                                                               │
                              ┌────────────────────────────────┘
                              │
                              ▼
                     [/implementation-test] ◄── YOU ARE HERE
                              │
                              ▼
                     Discover test infrastructure
                     Map tests to specification
                     Identify coverage gaps
                     Run tests — verify all pass
                     Fix failures or document skips
                     Generate test audit report
                              │
                              ▼
                     [/implementation-complete] ──► DEPLOYMENT READY
```

## Phase 1: Load Context Documents

**Load these documents BEFORE any test discovery:**

1. **PROMPT Document** (`SDD/prompts/PROMPT-[###]-[feature-name]-[date].md`)
   - Review all implemented requirements (REQ-XXX)
   - Note all edge cases (EDGE-XXX) and failure scenarios (FAIL-XXX)
   - Check "Test Implementation" section for any existing test tracking
   - Identify the full scope of what was built

2. **Specification Document** (`SDD/requirements/SPEC-[###]-[feature-name].md`)
   - Extract the Validation Strategy section for required test types and coverage targets
   - List all success criteria that must be verifiable through tests
   - Note any explicit test requirements (coverage %, test types, frameworks)

3. **Progress File** (`SDD/prompts/context-management/progress.md`)
   - Confirm implementation phase is active or recently completed
   - Check for any known testing gaps noted during implementation

## Phase 2: Discover Test Infrastructure

Use subagents to discover the project's testing landscape without consuming main context.

### 2.1 Identify Testing Frameworks and Configuration

Delegate to an **Explore subagent** to find:

- Test configuration files (e.g., `jest.config.*`, `pytest.ini`, `vitest.config.*`, `playwright.config.*`, `cypress.config.*`, `.mocharc.*`, `phpunit.xml`, `go.mod` test patterns, `cargo test` config)
- Test runner scripts in `package.json`, `Makefile`, `pyproject.toml`, or similar
- Coverage configuration and current coverage thresholds
- Any CI pipeline test steps (`.github/workflows/`, `.gitlab-ci.yml`, etc.)

Summarize findings:

```text
Testing Frameworks Detected:
- Unit testing: [framework name, config file]
- Integration testing: [framework name, config file]
- End-to-end testing: [framework name, config file]
- Coverage tool: [tool name, threshold configured]
- Test runner command(s): [commands]
```

If no test infrastructure is found, warn:

```text
⚠️ WARNING: No test infrastructure detected in this project.

Options:
1. Confirm tests exist in a non-standard location (provide path)
2. Confirm this project intentionally has no tests
3. Set up test infrastructure before proceeding

Please clarify before continuing.
```

### 2.2 Discover Existing Test Files

Delegate to an **Explore subagent** to locate all test files by searching for:

- Common unit test patterns: `*.test.*`, `*.spec.*`, `*_test.*`, `test_*.py`, files under `__tests__/`, `tests/unit/`, `spec/`
- Integration test patterns: files under `tests/integration/`, `integration/`, `test/integration/`
- End-to-end test patterns: files under `e2e/`, `cypress/`, `playwright/`, `tests/e2e/`, `*.e2e.*`
- Any test files created or modified during this implementation (cross-reference PROMPT document's "Files Being Modified" and "Completed Components")

Produce a structured inventory:

```text
Test File Inventory:
Unit Tests ([count] files):
- [path/to/test.test.ts] - [brief description of what it tests]
- ...

Integration Tests ([count] files):
- [path/to/integration.test.ts] - [brief description]
- ...

End-to-End Tests ([count] files):
- [path/to/e2e.spec.ts] - [brief description]
- ...

Test files added/modified in this implementation:
- [path] - [what was added]
```

## Phase 3: Map Tests to Specification

For each test file identified, analyze coverage against the specification requirements.

### 3.1 Requirement Coverage Matrix

For each requirement in the PROMPT document, determine which tests (if any) validate it:

```text
REQUIREMENT COVERAGE MATRIX

Functional Requirements:
| ID      | Description              | Unit Test | Integration | E2E | Status     |
|---------|--------------------------|-----------|-------------|-----|------------|
| REQ-001 | [description]            | ✓ [file]  | ✓ [file]    | —   | Covered    |
| REQ-002 | [description]            | ✓ [file]  | —           | —   | Partial    |
| REQ-003 | [description]            | —         | —           | —   | ❌ Missing  |

Edge Case Coverage:
| ID       | Description              | Test File    | Status     |
|----------|--------------------------|--------------|------------|
| EDGE-001 | [description]            | [file:line]  | ✓ Covered  |
| EDGE-002 | [description]            | —            | ❌ Missing  |

Failure Scenario Coverage:
| ID       | Description              | Test File    | Status     |
|----------|--------------------------|--------------|------------|
| FAIL-001 | [description]            | [file:line]  | ✓ Covered  |
| FAIL-002 | [description]            | —            | ❌ Missing  |

Performance Requirements:
| ID       | Description              | Benchmark/Test       | Status     |
|----------|--------------------------|----------------------|------------|
| PERF-001 | [description]            | [file or "manual"]   | ✓/❌       |

Security Requirements:
| ID      | Description              | Test File    | Status     |
|---------|--------------------------|--------------|------------|
| SEC-001 | [description]            | [file:line]  | ✓/❌       |
```

### 3.2 Test Type Assessment

Evaluate whether the right types of tests exist for the feature's nature:

**Unit Tests** — Should exist for:

- Pure functions, utility logic, data transformations
- Individual class methods or service functions
- Input validation and error handling at the function level
- All EDGE-XXX and FAIL-XXX scenarios that can be exercised in isolation

**Integration Tests** — Should exist for:

- Database interactions (queries, transactions, migrations)
- External API or service calls
- Multi-component workflows (e.g., service + repository + model)
- Authentication and authorization flows
- Queue/event processing

**End-to-End Tests** — Should exist for:

- Critical user flows (login, checkout, form submission, etc.)
- Cross-system workflows (e.g., API → DB → response)
- Acceptance criteria that require the full stack
- Scenarios called out explicitly in the specification's Validation Strategy

For each test type, produce a verdict:

```text
TEST TYPE ASSESSMENT

Unit Tests:    ✓ Adequate | ⚠️ Partial | ❌ Missing
Integration:   ✓ Adequate | ⚠️ Partial | ❌ Missing
End-to-End:    ✓ Adequate | ⚠️ Partial | ❌ Missing | N/A (no UI/API boundary)
```

## Phase 4: Coverage Gap Analysis

Identify all missing tests and prioritize them.

### 4.1 Critical Gaps (Must Fix Before /implementation-complete)

```text
CRITICAL COVERAGE GAPS
────────────────────────────────────────────────────────────
These gaps block completion — they correspond to specification requirements
or success criteria that have no test validation at all:

1. [REQ-XXX / EDGE-XXX / FAIL-XXX]: [Description]
   Required test type: [Unit/Integration/E2E]
   Suggested test file: [path/to/test.ext]
   What to test: [specific behavior or assertion]

2. [REQ-XXX / EDGE-XXX / FAIL-XXX]: [Description]
   ...
────────────────────────────────────────────────────────────
```

### 4.2 Recommended Gaps (Should Fix, Not Blocking)

```text
RECOMMENDED COVERAGE IMPROVEMENTS
────────────────────────────────────────────────────────────
These gaps represent best-practice coverage that improves confidence
but are not tied to explicit specification requirements:

1. [Component/function]: [What would be useful to test]
   Suggested test type: [Unit/Integration/E2E]
   Priority: [High/Medium/Low]
────────────────────────────────────────────────────────────
```

### 4.3 Current vs. Target Coverage

If coverage tooling is configured, report current coverage:

```text
COVERAGE SUMMARY
- Specification target:   [X]% (from SPEC validation strategy)
- Current reported:       [X]% (from coverage tool, or "Not measured")
- Delta:                  [+/-X]% [Met/Not Met]
- Lines/branches needing coverage: [brief description of uncovered areas]
```

If coverage tooling is not configured or coverage cannot be measured automatically, note this and recommend running the test suite manually.

## Phase 5: Execute Tests and Verify Results

With the audit complete and gaps identified, run the actual test suite to verify what passes.

### 5.1 Pre-Execution Check

Before running tests, verify the environment is ready:

- Confirm the test runner command(s) found in Phase 2.1 are available
- Check whether any environment setup is required (e.g., a running database, env vars, Docker)
- If the environment appears unready, warn the user:

```text
⚠️ Test execution may require additional setup:
- [Specific missing requirement, e.g., "DATABASE_URL not set"]
- [Another requirement, e.g., "Docker service not running"]

Options:
1. Proceed anyway (tests will likely fail with environment errors)
2. Skip execution and produce audit-only report
3. Set up the environment first, then re-run /implementation-test

Please choose how to proceed.
```

If the user opts to skip execution, jump to Phase 6 and mark test results as "Not Run."

### 5.2 Run Tests by Type

Run each available test type separately so results are clearly categorized. Use the commands discovered in Phase 2.1. If a single command runs all types, use it and parse the output by category.

**Unit Tests:**

```bash
[unit test runner command, e.g.: npm test -- --testPathPattern=unit, pytest tests/unit, go test ./...]
```

**Integration Tests** (if separate runner or path):

```bash
[integration test runner command, e.g.: npm test -- --testPathPattern=integration, pytest tests/integration]
```

**End-to-End Tests** (if present):

```bash
[e2e test runner command, e.g.: npx playwright test, npx cypress run]
```

**Coverage Report** (if coverage tooling is configured):

```bash
[coverage command, e.g.: npm test -- --coverage, pytest --cov, go test -coverprofile=coverage.out ./...]
```

Capture and record all output. Do not suppress errors — failing tests are expected findings, not failures of this command.

### 5.3 Parse and Categorize Results

From the test output, produce a structured results summary:

```text
TEST EXECUTION RESULTS
────────────────────────────────────────────────────────────
Unit Tests:
  Total:   [X]
  Passed:  [X] ✓
  Failed:  [X] ❌
  Skipped: [X] ⚠️
  Duration: [Xs]

Integration Tests:
  Total:   [X]
  Passed:  [X] ✓
  Failed:  [X] ❌
  Skipped: [X] ⚠️
  Duration: [Xs]

End-to-End Tests:
  Total:   [X]
  Passed:  [X] ✓
  Failed:  [X] ❌
  Skipped: [X] ⚠️
  Duration: [Xs]

Overall:
  Total:   [X]
  Passed:  [X] ✓
  Failed:  [X] ❌
  Coverage: [X]% (target: [Y]%)
────────────────────────────────────────────────────────────
```

### 5.4 Document Failing Tests

For each failing test, record:

```text
FAILING TESTS
────────────────────────────────────────────────────────────
1. [Test name / file:line]
   Type: [Unit/Integration/E2E]
   Error: [Error message or assertion failure]
   Specification link: [REQ-XXX / EDGE-XXX / FAIL-XXX if traceable]
   Likely cause: [Brief analysis — wrong assertion, missing mock, env issue, etc.]

2. [Test name / file:line]
   ...
────────────────────────────────────────────────────────────
```

If all tests pass, record:

```text
✅ All [X] tests passed. No failures to report.
```

### 5.5 Failure Triage and Fix

For each failing test, determine the appropriate action:

**Fix immediately** (test is correct, implementation has a bug):

- The test accurately describes expected behavior from the spec
- Fix the implementation code to make the test pass
- Re-run the affected test suite after each fix to confirm resolution

**Fix the test** (test is wrong or outdated):

- The test assertion no longer matches the current specification
- Update the test to reflect the correct expected behavior
- Document the change in the PROMPT document

**Known environment issue** (skip for now):

- Failure is due to a missing external dependency (DB, API, etc.) that is not available in the current environment
- Mark the test as environment-dependent and note it cannot be validated locally
- These do NOT block `/implementation-complete` if the underlying code is correct

After all fixes, re-run the full test suite to confirm a clean result:

```bash
[full test runner command]
```

Repeat until all tests either pass or are categorized as environment-dependent with justification.

## Phase 6: Generate Test Audit Report

Create `SDD/prompts/test-audits/TEST-AUDIT-[###]-[feature-name]-[YYYY-MM-DD_HH-MM-SS].md`:

```markdown
# Test Audit: [Feature Name]

## Audit Overview
- **Feature:** [Feature Name]
- **Specification:** SDD/requirements/SPEC-[###]-[feature-name].md
- **Implementation Tracking:** SDD/prompts/PROMPT-[###]-[feature-name]-[date].md
- **Audit Date:** [YYYY-MM-DD HH:MM:SS]
- **Auditor:** Claude (with [user's name if known])

## Test Infrastructure
- **Unit Framework:** [framework + version if known]
- **Integration Framework:** [framework or "same as unit"]
- **E2E Framework:** [framework or "None detected"]
- **Coverage Tool:** [tool or "None configured"]
- **Test Runner Commands:** [commands]

## Test Inventory
### Unit Tests ([count] files, [count] test cases if measurable)
[List files with one-line descriptions]

### Integration Tests ([count] files)
[List files with one-line descriptions]

### End-to-End Tests ([count] files)
[List files or "None"]

## Requirement Coverage Matrix
[Full matrix from Phase 3.1]

## Test Type Assessment
[Assessment from Phase 3.2]

## Test Execution Results
- **Tests Run:** [Yes / Skipped — reason]
- **Unit:** [X passed / Y failed / Z skipped]
- **Integration:** [X passed / Y failed / Z skipped]
- **E2E:** [X passed / Y failed / Z skipped]
- **Overall:** [X/Y passing]
- **Coverage:** [X]% (target: [Y]%)

### Failing Tests
[List from Phase 5.4, or "None — all tests passed"]

### Environment-Dependent Skips
[List any tests skipped due to missing env dependencies, with justification]

## Coverage Summary
- Specification Target: [X]%
- Current Coverage: [X]% or "Not measured"
- Status: [Met / Not Met / Unknown]

## Critical Gaps (Blocking /implementation-complete)
[List from Phase 4.1, or "None — all specification requirements have test coverage"]

## Recommended Improvements
[List from Phase 4.2, or "None at this time"]

## Verdict

[Choose one:]

### ✅ TESTS ADEQUATE — Ready for /implementation-complete
All specification requirements have test coverage. All tests pass (or
environment-dependent skips are documented and justified).

### ⚠️ TESTS PARTIAL — Address Issues Before Completing
[X] critical gaps or failing tests must be resolved before running
/implementation-complete. See sections above for required actions.

### ❌ TESTS INSUFFICIENT — Significant Coverage or Failures
Major areas of the specification lack test validation, or multiple tests
are failing without justification. Review all gaps and failures above.
```

## Phase 7: Update PROMPT Document

Update the "Test Implementation" section in `SDD/prompts/PROMPT-[###]-[feature-name]-[date].md`:

```markdown
## Test Implementation (Updated by /implementation-test — [YYYY-MM-DD])

### Test Audit Reference
- **Audit Report:** SDD/prompts/test-audits/TEST-AUDIT-[###]-[feature-name]-[timestamp].md
- **Audit Verdict:** [ADEQUATE / PARTIAL / INSUFFICIENT]

### Unit Tests
- [x] [Test file]: Tests for [requirement/component] — ✓ Covered
- [ ] [Test file]: Tests for [requirement/component] — ❌ Missing (Critical)

### Integration Tests
- [x] [Test file]: Integration test for [feature flow] — ✓ Covered
- [ ] [Test file]: Integration test for [flow] — ❌ Missing (Recommended)

### End-to-End Tests
- [x] [Test file]: E2E test for [user scenario] — ✓ Covered
- N/A — No E2E framework configured

### Test Execution Results
- **Tests Run:** [Yes / Skipped — reason]
- **Overall:** [X/Y passing]
- **Failures:** [count, or "None"]
- **Environment Skips:** [count with justification, or "None"]

### Test Coverage
- Current Coverage: [X]% or "Not measured"
- Target Coverage: [X]% (from SPEC)
- Coverage Status: [Met / Not Met / Unknown]
- Critical Gaps Remaining: [count]
```

## Decision Logic

After completing all phases, apply this decision:

```text
IF critical coverage gaps exist OR tests are failing (without env justification):
  → Report gaps and failures clearly
  → Recommend the user address them before /implementation-complete
  → Do NOT block automatically — the user decides whether to proceed
  → Use /implementation-compact if context is high after fixing

IF tests were skipped (env not available):
  → Document which tests could not be run and why
  → Treat as non-blocking if the test code itself is correct
  → Flag for validation in a proper environment (CI, staging, etc.)

IF no critical gaps AND all tests pass (or env-skips are justified):
  → Confirm all specification requirements have test coverage
  → Note any recommended improvements as non-blocking
  → Signal that /implementation-complete can proceed
```

## Subagent Strategy

Use subagents to keep main context lean during this audit:

1. **Explore subagent** — test file discovery, framework config detection, reading individual test files
2. **General-purpose subagent** — analyzing test content for coverage of specific requirements, running coverage reports if needed

Document all subagent delegations in the audit report's Session Notes.

## Context Management After Audit

- If context has risen above 35% during this audit, run `/implementation-compact` before proceeding
- The audit report serves as a durable record — it does not need to remain in context
- Update the PROMPT document (concise) and let the full detail live in the audit file

---

Begin the test audit now. Load the PROMPT document and specification first, then systematically discover and evaluate test coverage before producing the audit report.
