# Initialize Implementation Phase

IMPLEMENTATION PHASE INITIALIZATION

Starting implementation phase based on completed specification.

IMPORTANT: This command requires Claude Sonnet. Before proceeding, check your current model ID in the system information. If you are NOT running on a Claude Sonnet model (e.g., claude-sonnet-*), immediately:

  1. Warn the user: "WARNING: This command requires Claude Sonnet but you're currently using [model name]. Please switch to Sonnet and try again."
  2. STOP all further processing - do not execute any of the instructions below.

## Context Utilization Check

Before loading any documents, check current context usage:

```text
Current context utilization: [X]%

If > 35%: ⚠️ Warning - Context usage is high ([X]%). Consider:
  - Running essential tasks only
  - Using subagents for research tasks
  - Being prepared to run /implementation-compact soon

If > 40%: ⚠️ CRITICAL - Context usage is too high ([X]%).
  - You should run /implementation-compact before starting
  - Clear session and use /continue to resume with fresh context
```

Proceed with caution if context is above 35%.

## Initial Context Load

1. **Read Progress File:**
   - Load `SDD/orchestration/progress.md` to understand planning completion status
   - Identify the specification document referenced
   - Note any important context from the planning phase

2. **Read Ubiquitous Language Glossary:**
   - If `SDD/UBIQUITOUS_LANGUAGE.md` exists, load it. Use the canonical names from this glossary in code, comments, commit messages, and tests — in preference to any synonyms or near-synonyms. If implementation surfaces a term not in the glossary, do not silently invent one; flag it for addition during `/research-complete` of a future cycle (or during this cycle's planning if still open).
   - If the glossary does not exist, proceed without it.

3. **Update Progress for Implementation Phase:**
   - Add a new implementation section to `SDD/orchestration/progress.md`
   - IMPORTANT: Preserve all research and planning phase information - do NOT delete or reset it
   - Add reference to the IMPLEMENTATION-PLAN document being created
   - Document the transition from planning to implementation phase

4. **Read `delivery_mode:` from the Spec Frontmatter:**
   - Open `SDD/requirements/SPEC-[###]-[feature-name].md` and read the YAML frontmatter (the block between `---` markers at the top of the file).
   - Extract the `delivery_mode:` value. The canonical enum is exactly `{whole-feature, per-slice}` (lowercase, hyphenated).
   - **Validation rule (binding — same as `/planning-start`):**
     - Absent field → silent default to `whole-feature`. No log line. This is the documented default behavior.
     - Exact match `whole-feature` → continue with the **whole-feature branch** below.
     - Exact match `per-slice` → continue with the **per-slice branch** below.
     - Any other value (typos like `per_slice`, `PerSlice`, `vertical-thread`, `whole_feature`, etc.) → fail fast with: `Invalid delivery_mode value '<value>' in <spec-path>. Allowed values: whole-feature, per-slice. Edit the spec frontmatter and re-run /implementation-start.` Do NOT silently fall through to the default branch.
   - Record the resolved mode in the implementation tracker's Executive Summary (a `**Delivery mode:**` field below `**Status:**`) and in `SDD/orchestration/progress.md`.

## Implementation Setup

1. **Check for Existing IMPLEMENTATION-PLAN Documents:**
   - Search for any existing `SDD/implementation/IMPLEMENTATION-PLAN-[###]-*.md` files
   - If a IMPLEMENTATION-PLAN document with the same number already exists:

     ```text
     ⚠️ WARNING: IMPLEMENTATION-PLAN document already exists!

     Found: SDD/implementation/IMPLEMENTATION-PLAN-[###]-[existing-name].md

     Options:
     1. Continue with existing IMPLEMENTATION-PLAN document
     2. Create new IMPLEMENTATION-PLAN with different number
     3. Archive existing and create new (if previous implementation was abandoned)

     Please clarify how to proceed.
     ```

   - Only proceed to create new IMPLEMENTATION-PLAN if no duplicate exists or user explicitly approves

2. Create `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[YYYY-MM-DD].md` document where:
   - `[###]` matches the specification and research document numbers (e.g., if using SPEC-042, create IMPLEMENTATION-PLAN-042)
   - `[feature-name]` is a kebab-case description matching the spec document (e.g., "user-authentication", "csv-export")
   - `[YYYY-MM-DD]` is today's date
   - Full example: `IMPLEMENTATION-PLAN-042-user-authentication-2025-10-20.md`

## Prerequisite Verification

Before starting implementation:

1. **Locate Specification Document:**
   - Find the corresponding `SDD/requirements/SPEC-[###]-[feature-name].md` file
   - If multiple specs exist, ask user which one to implement
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
   - Check if `/planning-complete` was run (look for completion marker in progress.md)
   - If not complete, warn: "Specification phase may not be complete. Consider running /planning-complete first if needed."
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

## Context Management

### Current Utilization
- Context Usage: [X]% (target: <40%)
- Essential Files Loaded:
  - [file path]:lines - [purpose]
  - [file path]:lines - [purpose]

### Files Delegated to Subagents
- [file path] - [research task delegated]
- [file path] - [research task delegated]

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

## Session Notes

### Subagent Delegations
- [Timestamp]: Delegated [task] to [subagent type]
- [Timestamp]: Results: [summary of findings]

### Critical Discoveries
- [Discovery]: [Impact on implementation]
- [Discovery]: [Required specification adjustment]

### Next Session Priorities
1. [Specific task to complete next]
2. [Following priority]
3. [Subsequent priority]

## Slice Progress

> **Required only when `delivery_mode: per-slice`.** Omit this section entirely when `delivery_mode: whole-feature` (the default). When per-slice, the planning subagent's `## Delivery Slices` from the SPEC seeds this table; `/slice-start` initializes the row to `In Progress`; `/slice-retro` updates `Status`, `Test result`, and `Notes` only (never `SLICE-ID`, `Name`, or `Acceptance check`). State transitions are forward-only — `Not Started` → `In Progress` → `Acceptance Check Passing` → `Complete`. SLICE-XXX values must be unique within this table.

| SLICE-ID  | Name              | Status        | Acceptance check                            | Test result | Notes |
|-----------|-------------------|---------------|---------------------------------------------|-------------|-------|
| SLICE-001 | [from SPEC]       | Not Started   | [from SPEC's Acceptance check field]        | —           | —     |
| SLICE-002 | [from SPEC]       | Not Started   | [from SPEC's Acceptance check field]        | —           | —     |

**Status enum (binding):** `Not Started`, `In Progress`, `Acceptance Check Passing`, `Complete`. Any "stuck" condition lives in the rolling ledger's `Open recommendations awaiting user decision` section, NOT the Status column. The slice commands enforce the column-write authority: `/implementation-start` scaffolds the table; `/slice-start` flips Status to `In Progress`; `/slice-retro` writes `Status`/`Test result`/`Notes` after the slice's review-and-fix loop completes.
```

## Implementation Process

1. **Load Specification Foundation:**
   - Read the complete SPEC-XXX document
   - Identify all requirements, edge cases, and failure scenarios
   - Note essential files and context constraints

2. **Branch on `delivery_mode:`:**
   - The mode was already resolved in Initial Context Load step 4. Branch behavior here:
   - **`whole-feature` (default):** Implement the feature in a single tracked pass against the full REQ/EDGE/FAIL list. Update the IMPLEMENTATION-PLAN's `Specification Alignment` checkboxes as you complete each item. Behavior is bit-for-bit identical to the pre-2.0.0 implementation-tracker flow apart from the filename/path change. **Omit the `## Slice Progress` section from the tracker entirely.**
   - **`per-slice`:** Populate the `## Slice Progress` table from the SPEC's `## Delivery Slices` section (one row per `SLICE-XXX`, copying `Name` and `Acceptance check` from the SPEC; `Status` initialized to `Not Started`). **Do NOT begin implementing in a single tracked pass.** Instead, use the slice-aware command sequence: `/slice-start <SLICE-ID>` → implement the slice → `/slice-review <SLICE-ID>` → fix findings → `/slice-retro <SLICE-ID>` → `/slice-commit <SLICE-ID>` → repeat for the next slice. The `/slice-*` commands enforce the per-slice cycle and update the `## Slice Progress` table for you.

3. **Set Up Development Environment:**
   - Load essential files identified in specification
   - Verify test framework is configured
   - Check for existing related code to build upon
   - **Identify whether the feature has web-facing behavior** (UI pages, client-side JS, HTMX interactions, CSP changes, multi-step browser flows). Record this determination in the IMPLEMENTATION-PLAN document. This drives whether E2E tests are required.

4. **Begin Incremental Implementation:**
   - Start with core functionality (primary success path)
   - Implement one requirement at a time
   - Write tests alongside every component — do not defer test writing
   - For every feature, consider all three test types:
     - **Unit tests** (always required): isolated logic with mocked dependencies
     - **Integration tests** (required if API endpoints are involved): test via API test client with mocked external services
     - **E2E tests** (required if web-facing behavior exists): Playwright browser tests against the real running stack, in the project's E2E test directory (check CLAUDE.md or equivalent for the project-specific path)
   - If the feature is web-facing, E2E tests are **mandatory**, not optional
   - Validate against specification criteria continuously

5. **Track Progress Rigorously:**
   - Update IMPLEMENTATION-PLAN document after each component completion
   - Mark requirements as implemented in the tracking document
   - Document any deviations or discoveries immediately

## Context Management & Subagent Usage

### Context Target

- Maintain <40% context utilization during implementation
- Focus on implementation: Write code and tests based on specification (avoid re-researching or re-planning)
- Prepare for testing: Structure code for easy validation against spec criteria

### Available Subagents for Implementation Phase

Use these subagents (via Task tool) to preserve main context:

1. **Explore subagent** (`subagent_type=Explore`)
   - Use for: Finding implementation examples, locating test files, discovering utilities
   - Example: "Find all existing authentication implementations in this codebase"
   - When to use: When you need to understand existing patterns or find reusable components

2. **general-purpose subagent** (`subagent_type=general-purpose`)
   - Use for: Complex implementation research and analysis
   - Example tasks:
     - "Research how to implement [specific pattern] in [framework]"
     - "Analyze performance implications of [implementation approach]"
     - "Find and analyze similar features in this codebase for implementation patterns"
     - "Research testing strategies for [specific scenario]"
     - "Investigate error handling patterns used elsewhere in this project"
   - When to use: When you need implementation guidance or pattern analysis

### Subagent Delegation Strategy

- Delegate file discovery and pattern research to preserve context for coding
- Use parallel subagent calls when investigating independent implementation aspects
- Document subagent findings in the Session Notes section of IMPLEMENTATION-PLAN document

## Quality Checklist

During implementation, continuously verify:

- [ ] Each requirement from SPEC is being addressed
- [ ] Tests are written for each component/requirement — not deferred
- [ ] Unit tests exist for all logic with isolated, mocked dependencies
- [ ] Integration tests exist for all API endpoints (via test client)
- [ ] Web-facing behavior identified (yes/no) — recorded in IMPLEMENTATION-PLAN document
- [ ] If web-facing: Playwright E2E tests written in the project's E2E test directory
- [ ] Edge cases (EDGE-XXX) have specific handling code
- [ ] Failure scenarios (FAIL-XXX) have error handling
- [ ] Performance requirements (PERF-XXX) are being measured
- [ ] Security requirements (SEC-XXX) are implemented
- [ ] Code follows existing project patterns (discovered via subagents)
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

### When Context Reaches ~40%

1. Run `/implementation-compact` to preserve progress
2. Clear session and start fresh
3. Run `/continue` to resume from compaction point

---

Begin implementation now using the specification as your authoritative guide. Create the `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[YYYY-MM-DD].md` document and start systematic implementation against specification criteria.
