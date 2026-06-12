# Implementation Phase Completion

IMPLEMENTATION PHASE COMPLETION

Finalize implementation phase and prepare for deployment.

You are a spawned subagent in an orchestrated /sdd-flow run. Your prompt provides resolved artifact paths and identifiers — use them verbatim. This file is your complete instruction set. Do not spawn subagents or invoke slash commands/skills, even if an Agent/Task tool is available — the flow’s flat-orchestration contract forbids it; all work happens inline in your own context.

## Workflow Position

```text
[Implementation Start] ──────► [Implementation Compact] ──────► [Context Resume]
         │                                 │                           │
         ▼                                 ▼                           ▼
   Create IMPLEMENTATION-PLAN-###              Save progress &                 Resume work
                                  hand off
                                                                        │
                                     ┌──────────────────────────────────┘
                                     │
                                     ▼
                           [Implementation Complete] ◄── YOU ARE HERE
                                     │
                                     ▼
                              Validate all requirements
                              Create summary documents
                              Update specifications
                                     │
                                     ▼
                              [Commit] ──────► DEPLOYMENT READY
```

## Initial Document Loading and Verification

### 1. Load Core Documents

**IMPORTANT: Load these documents BEFORE proceeding with any completion tasks.**

1. **Progress File:**
   - Load `SDD/orchestration/progress.md`
   - Verify implementation phase is active
   - Check for any incomplete items or blockers
   - Note any recent compaction files referenced

2. **IMPLEMENTATION-PLAN Document:**
   - Load `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[date].md`
   - This is your PRIMARY verification source
   - Check "Status" field (should be "In Progress" or "Testing")
   - Review all requirement implementation statuses

3. **Specification Document:**
   - Load `SDD/requirements/SPEC-[###]-[feature-name].md`
   - Compare requirements against IMPLEMENTATION-PLAN document status
   - Verify all REQ-XXX, PERF-XXX, SEC-XXX, UX-XXX items

4. **Recent Compaction (if exists):**
   - Check for `SDD/orchestration/compacted/implementation-compacted-*.md`
   - Load most recent file to understand any pending items
   - Review "Specification Validation Remaining" section

### 2. Pre-Completion Verification

**STOP and verify these conditions from the loaded documents:**

```text
COMPLETION READINESS CHECKLIST
────────────────────────────────────────────────────────────
□ All REQ-XXX requirements show "Complete" in IMPLEMENTATION-PLAN document
□ All PERF-XXX performance requirements show "Met" with metrics
□ All SEC-XXX security requirements show "Validated"
□ All UX-XXX user experience requirements show "Satisfied"
□ All EDGE-XXX edge cases show "Complete" implementation
□ All FAIL-XXX failure scenarios show error handling "Implemented"
□ Test coverage meets or exceeds target from specification
□ No "Blocked/Pending" items remain in IMPLEMENTATION-PLAN document
□ All delegations have been completed and documented
────────────────────────────────────────────────────────────
```

If ANY items are not complete:

```text
⚠️ WARNING: Implementation is NOT ready for completion!

The following items are incomplete:
- [List specific incomplete items with their IDs]
- [Include which document shows the incomplete status]

Required Actions:
1. Complete remaining implementation tasks
2. Update IMPLEMENTATION-PLAN document with completion status
3. Verify all tests are passing
4. Then retry this body

Address remaining items and return a bounded result listing incomplete items.
```

**STOP processing if verification fails.**

## Test Verification Gate

**This gate runs BEFORE writing any completion documentation. It is a hard stop — implementation is NOT complete until all checks below pass.**

### Step 1: Run the Full Test Suite

Execute all unit and integration tests and record the results:

```text
TEST SUITE EXECUTION
────────────────────────────────────────────────────────────
□ Unit and integration tests executed
□ Pass rate: [X]/[X] tests passed (must be 100%)
□ Zero failing tests
□ Zero error-level warnings that mask failures

If any tests fail:
  ⛔ STOP — Implementation is NOT complete.
  Fix all failing tests before retrying this body.
────────────────────────────────────────────────────────────
```

### Step 2: Verify Test Type Coverage

Check that all applicable test types exist. Missing required test types are a **blocking issue**.

```text
TEST TYPE COVERAGE
────────────────────────────────────────────────────────────
Unit Tests
  □ Unit tests exist for all logic and requirements
  □ Dependencies are properly mocked
  Status: PRESENT / MISSING (blocking)

Integration Tests (required if API endpoints exist)
  □ Integration tests exist for all API endpoints
  □ Tests use the project's API test client
  □ External services are mocked at the boundary
  Status: PRESENT / MISSING (blocking) / N/A — [justification]

E2E / Playwright Tests (required if feature has web-facing behavior)
  □ Feature web-facing determination recorded in IMPLEMENTATION-PLAN document
  □ If web-facing: Playwright tests exist in the project's E2E test directory
  □ E2E tests cover critical user flows (not just page loads)
  □ E2E tests run against the real running stack (not mocked services)
  □ Tests verify actual browser behavior: page loads, form submissions,
    JS execution, HTMX interactions, client-side logic
  □ Test data accounts for real service behavior (NLP, auth, etc. are not mocked in E2E)
  Status: PRESENT / MISSING (blocking) / N/A — [justification]
────────────────────────────────────────────────────────────
```

If a required test type is missing:

```text
⛔ BLOCKING: Missing required test type

The following test types are required but not present:
- [Unit/Integration/E2E]: [What is missing]
- [Why it is required for this feature]

Required Actions:
1. Write the missing [test type] tests
2. Confirm they pass
3. Retry this body once blockers are resolved

Implementation is NOT complete until all required test types are present and passing.
```

### Step 3: Verify Spec Coverage

Confirm every tracked requirement has at least one test:

```text
SPEC COVERAGE VERIFICATION
────────────────────────────────────────────────────────────
□ Every REQ-XXX has at least one test
□ Every EDGE-XXX has at least one test
□ Every FAIL-XXX has at least one test
□ SEC-XXX requirements with testable criteria have tests

Any requirement without a test:
  ⛔ STOP — Add tests for uncovered requirements before proceeding.
────────────────────────────────────────────────────────────
```

### Step 4: Record Test Results in IMPLEMENTATION-PLAN Document

Before writing completion documents, update the IMPLEMENTATION-PLAN document's "Test Implementation" section with final results:

```markdown
### Test Verification Gate — Results

- **Gate Passed:** Yes / No
- **Suite Execution:** [X] tests run, [X] passed, 0 failed (100% pass rate)
- **Unit Tests:** [X] tests — covers [list of REQ/EDGE/FAIL IDs]
- **Integration Tests:** [X] tests — covers [list of endpoints/flows] (or N/A — [reason])
- **E2E Tests:** [X] tests — covers [list of browser flows] (or N/A — [reason])
- **Uncovered Requirements:** None (or list with resolution)
```

**STOP processing if the gate fails. Only proceed to Completion Process once all checks above pass.**

## Completion Process

### 1. Finalize IMPLEMENTATION-PLAN Document

Update `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[date].md`:

#### Update Header Section

```markdown
## Executive Summary

- **Based on Specification:** SPEC-[###]-[feature-name].md
- **Research Foundation:** RESEARCH-[###]-[feature-name].md
- **Start Date:** [Original date]
- **Completion Date:** [YYYY-MM-DD]
- **Implementation Duration:** [X days]
- **Author:** Claude (with [user's name if known])
- **Status:** Complete ✓
- **Safety-Net Status:** [no trips | N mid-phase handoffs]
```

#### Add Completion Summary

```markdown
## Implementation Completion Summary

### What Was Built
[2-3 paragraph summary of the implemented feature, focusing on:
- Core functionality delivered
- How it meets the specification intent
- Key architectural decisions made]

### Requirements Validation
All requirements from SPEC-[###] have been implemented and tested:
- Functional Requirements: [X/X] Complete
- Performance Requirements: [X/X] Met
- Security Requirements: [X/X] Validated
- User Experience Requirements: [X/X] Satisfied

### Test Coverage Achieved
- **Test Suite Result:** [X]/[X] tests passed (100%)
- **Unit Tests:** [X] tests, [X]% coverage (Target: [Y]%)
- **Integration Tests:** [X] tests (or N/A — [reason])
- **E2E/Playwright Tests:** [X] tests (or N/A — [reason])
- **Edge Case Coverage:** [X/X] EDGE-XXX scenarios tested
- **Failure Scenario Coverage:** [X/X] FAIL-XXX scenarios handled

### Inline Investigation Summary
- Searches run (Grep/Glob): [X] (file discovery, pattern search)
- Files read for analysis: [X] (key files and what they yielded)
[Note any particularly valuable findings]
```

### 2. Update Specification Document

Add implementation results to `SDD/requirements/SPEC-[###]-[feature-name].md`:

```markdown
## Implementation Summary

### Completion Details
- **Completed:** [YYYY-MM-DD]
- **Implementation Duration:** [X days]
- **Final IMPLEMENTATION-PLAN Document:** SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[date].md
- **Implementation Summary:** SDD/implementation/summaries/IMPLEMENTATION-SUMMARY-[###]-[YYYY-MM-DD_HH-MM-SS].md

### Requirements Validation Results
Based on IMPLEMENTATION-PLAN document verification:
- ✓ All functional requirements: Complete
- ✓ All non-functional requirements: Complete
- ✓ All edge cases: Handled
- ✓ All failure scenarios: Implemented

### Performance Results
[Pull from IMPLEMENTATION-PLAN document's Performance Metrics section]
- PERF-001: Achieved [value] ms (Target: [value] ms) ✓
- PERF-002: Achieved [value] req/s (Target: [value] req/s) ✓

### Implementation Insights
[From IMPLEMENTATION-PLAN document's Critical Discoveries section]
1. [Key architectural pattern that worked well]
2. [Performance optimization discovered]
3. [Testing approach that was effective]

### Deviations from Original Specification
[From IMPLEMENTATION-PLAN document's Implementation Deviations section]
- [Any approved changes with rationale]
- [Trade-offs made and why]
```

### 3. Create Implementation Summary Document

Save to `SDD/implementation/summaries/IMPLEMENTATION-SUMMARY-[###]-[YYYY-MM-DD_HH-MM-SS].md`:

Format: `IMPLEMENTATION-SUMMARY-[###]-YYYY-MM-DD_HH-MM-SS.md` (24-hour format with underscores)
Example: `IMPLEMENTATION-SUMMARY-042-2025-10-21_14-30-45.md`

```markdown
# Implementation Summary: [Feature Name]

## Feature Overview
- **Specification:** SDD/requirements/SPEC-[###]-[feature-name].md
- **Research Foundation:** SDD/research/RESEARCH-[###]-[feature-name].md
- **Implementation Tracking:** SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[date].md
- **Completion Date:** [YYYY-MM-DD HH:MM:SS]
- **Context Management:** Maintained <40% throughout implementation

## Requirements Completion Matrix

### Functional Requirements
| ID | Requirement | Status | Validation Method |
|----|------------|---------|------------------|
| REQ-001 | [Description] | ✓ Complete | Unit tests in [file] |
| REQ-002 | [Description] | ✓ Complete | Integration test [file] |

### Performance Requirements
| ID | Requirement | Target | Achieved | Status |
|----|------------|--------|----------|---------|
| PERF-001 | [Description] | [value] | [value] | ✓ Met |
| PERF-002 | [Description] | [value] | [value] | ✓ Met |

### Security Requirements
| ID | Requirement | Implementation | Validation |
|----|------------|---------------|------------|
| SEC-001 | [Description] | [How implemented] | [How tested] |

## Implementation Artifacts

### New Files Created

```text
[path/to/file1.ext] - [Primary purpose]
[path/to/file2.ext] - [Primary purpose]
```

### Modified Files

```text
[path/to/file.ext]:lines [start-end] - [What was changed]
[path/to/file.ext]:lines [start-end] - [What was changed]
```

### Test Files

```text
[path/to/test1.test.ext] - Tests [component/requirement]
[path/to/test2.test.ext] - Tests [edge cases EDGE-XXX]
```

## Technical Implementation Details

### Architecture Decisions
[From IMPLEMENTATION-PLAN document's Technical Decisions Log]
1. **[Decision]:** [Rationale and impact]
2. **[Pattern Used]:** [Why chosen over alternatives]

### Key Algorithms/Approaches
- [Algorithm/approach]: [Where used and why]

### Dependencies Added
- [package/library]: [version] - [purpose]

## Inline Investigation Summary

### Searches Run (Grep/Glob): [X]
1. [Timestamp]: Searched for [pattern] - Result: [findings]
2. [Timestamp]: Found [what] - Result: [outcome]

### Files Read for Analysis: [X]
1. [Timestamp]: Read [file] - Applied: [how used]
2. [Timestamp]: Analyzed [component] - Insight: [discovery]

### Most Valuable Findings
- [Which inline investigation provided most value and why]

## Quality Metrics

### Test Coverage
- Unit Tests: [X]% coverage ([Y] tests)
- Integration Tests: [X]% coverage ([Y] tests)
- Edge Cases: [X]/[Y] scenarios covered
- Failure Scenarios: [X]/[Y] handled

### Code Quality
- Linting: [Pass/Fail with issues if any]
- Type Safety: [Coverage if applicable]
- Documentation: [Status]

## Deployment Readiness

### Environment Requirements

- Environment Variables:

  ```text
  [VAR_NAME_1]: [purpose]
  [VAR_NAME_2]: [purpose]
  ```

- Configuration Files:

  ```text
  [config.file]: [required settings]
  ```

### Database Changes
- Migrations: [list or "None"]
- Schema Updates: [list or "None"]

### API Changes
- New Endpoints: [list with methods]
- Modified Endpoints: [list with changes]
- Deprecated: [list or "None"]

## Monitoring & Observability

### Key Metrics to Track
1. [Metric]: Expected range [value]
2. [Metric]: Alert threshold [value]

### Logging Added
- [Component]: [What is logged]

### Error Tracking
- [Error scenario]: [How it's tracked]

## Rollback Plan

### Rollback Triggers
- [Condition that would trigger rollback]

### Rollback Steps
1. [Specific step]
2. [Specific step]

### Feature Flags
- [Flag name]: Controls [what]

## Lessons Learned

### What Worked Well
1. [Approach/pattern that was effective]
2. [Tool/technique that helped]

### Challenges Overcome
1. [Challenge]: [Solution applied]
2. [Challenge]: [Solution applied]

### Recommendations for Future
- [Recommendation based on this implementation]
- [Pattern to reuse or avoid]

## Next Steps

### Immediate Actions
1. Deploy to staging environment
2. Run smoke tests
3. Monitor initial metrics

### Production Deployment
- Target Date: [If known]
- Deployment Window: [If planned]
- Stakeholder Sign-off: [Required from whom]

### Post-Deployment
- Monitor [specific metrics]
- Validate [specific behaviors]
- Gather user feedback on [specific aspects]
```

### 4. Update Progress File

Update `SDD/orchestration/progress.md`:

```markdown
## Implementation Phase - COMPLETE ✓

### Feature: [Feature Name]
- **Specification:** SDD/requirements/SPEC-[###]-[feature-name].md
- **Implementation:** SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[date].md
- **Summary:** SDD/implementation/summaries/IMPLEMENTATION-SUMMARY-[###]-[timestamp].md
- **Completion:** [YYYY-MM-DD HH:MM:SS]

### Final Status
- All requirements: ✓ Implemented
- All tests: ✓ Passing
- Performance targets: ✓ Met
- Security requirements: ✓ Validated
- Documentation: ✓ Complete

### Inline Investigation Summary
- Key investigations performed inline: [brief list]
- Safety-Net handoffs required: [none | N]

### Implementation Metrics
- Duration: [X] days
- Context management: Maintained <40% throughout
- Test coverage achieved: [X]%
- Files modified: [X]
- New files created: [Y]

### Deployment Readiness
✓ Feature is specification-validated and production-ready
✓ All acceptance criteria met
✓ Rollback plan documented
✓ Monitoring configured

### Next Steps
- Ready for staging deployment
- Production deployment checklist available
- Post-deployment validation plan ready
```

### 5. Capture Glossary Deltas Introduced by the Implementation

If the implementation introduced or refined any domain terms beyond what was added to `SDD/UBIQUITOUS_LANGUAGE.md` during the research-complete and planning-complete phases (e.g., new module names that became canonical in code, action verbs adopted in tests, state names introduced during implementation), apply those deltas to the glossary now. This keeps subsequent cycles' research and planning aligned to the same vocabulary.

Maintenance is incremental — do not rewrite stable entries. If implementation surfaced a term that contradicts an existing glossary entry, resolve the contradiction explicitly (update the entry or rename in code — do not let both stand). If implementation introduced no new domain terms, skip this step and note "no glossary changes" in the progress file.

The implementation-phase equivalent gate is per-step in spirit: each major implementation milestone that introduced or refined a term should have updated the glossary in the same commit (per REQ-020 timing rule). This step is the final reconciliation — catch anything that slipped past the per-commit discipline before the implementation phase closes.

## Phase Transition

Implementation phase COMPLETE for [Feature Name]. Return a bounded result (≤200 words) with the paths to all artifacts written:

- `SDD/requirements/SPEC-[###]-[feature-name].md` (updated with implementation summary)
- `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[date].md` (finalized)
- `SDD/implementation/summaries/IMPLEMENTATION-SUMMARY-[###]-[YYYY-MM-DD_HH-MM-SS].md` (created)
- `SDD/orchestration/progress.md` (updated)
- `SDD/UBIQUITOUS_LANGUAGE.md` (updated if glossary deltas were captured, or note "no glossary changes")

The feature is specification-validated, thoroughly tested, and ready for deployment.

## Error Recovery

### If Completion Cannot Proceed

When requirements are not met:

1. **Document Blockers:**
   ```markdown
   ## Incomplete Items Blocking Completion
   - [REQ-XXX]: [What's missing]
   - [EDGE-XXX]: [What needs handling]
   - [Test Coverage]: [Current]% needs to reach [Target]%
   ```

2. **Save Progress:**
   - Append the blockers list to `SDD/orchestration/progress.md`
   - Return a bounded result listing all incomplete items and required actions

3. **Address Blockers:**
   - Complete missing implementations
   - Add required tests
   - Fix failing validations

4. **Retry Completion:**
   - Once all blockers resolved
   - Retry this body

## Quality Gates

Final verification before marking complete:

### Code Quality

- [ ] All code follows project patterns and standards
- [ ] No TODO or FIXME comments remain unaddressed
- [ ] Documentation is complete (inline and external)

### Testing

- [ ] Full test suite run — 100% pass rate confirmed
- [ ] Unit tests present and passing
- [ ] Integration tests present and passing (or N/A with justification)
- [ ] E2E/Playwright tests present and passing for web-facing features (or N/A with justification)
- [ ] Edge cases (EDGE-XXX) have specific test coverage
- [ ] Failure scenarios (FAIL-XXX) have test coverage
- [ ] Performance benchmarks validated
- [ ] Test Verification Gate results recorded in IMPLEMENTATION-PLAN document

### Specification Compliance

- [ ] Every requirement is demonstrably working
- [ ] All acceptance criteria met
- [ ] No unapproved deviations from spec

### Operational Readiness

- [ ] Deployment requirements documented
- [ ] Monitoring plan in place
- [ ] Rollback procedure defined
- [ ] Error handling comprehensive

## Important Notes

- This body should only be run when ALL implementation work is complete
- The IMPLEMENTATION-PLAN document is the source of truth for completion status
- Implementation summary uses timestamped format (YYYY-MM-DD_HH-MM-SS)
- All delegations should be reviewed and documented
- Context should be managed throughout (<40% utilization)

---

Once all checks pass and documents are updated, the implementation phase is COMPLETE. The feature is specification-validated, thoroughly tested, and ready for deployment.
