# Planning Phase Completion

You are a spawned subagent in an orchestrated /sdd-flow run. Your prompt provides resolved artifact paths and identifiers — use them verbatim. This file is your complete instruction set. You cannot spawn subagents and cannot invoke slash commands; all work happens inline in your own context.

PLANNING PHASE COMPLETION

Specification creation is complete and ready for implementation.

## 1. Verify Specification Document Completeness

Confirm that `SDD/requirements/SPEC-[###]-[feature-name].md` contains all required sections with complete information:

### Executive Summary

- [ ] Research foundation reference included `SDD/research/RESEARCH-[###]-[feature-name].md`
- [ ] Creation date and author documented
- [ ] Status marked as "In Review" or "Approved"

### Research Foundation

- [ ] Production issues from research listed with issue numbers
- [ ] Stakeholder validation summarized from all teams
- [ ] System integration points identified with file:line references

### Intent

- [ ] Clear problem statement derived from research
- [ ] Solution approach defined with rationale
- [ ] Expected outcomes specified and measurable

### Success Criteria

- [ ] Functional requirements (REQ-XXX) specific and testable
- [ ] Non-functional requirements (PERF-XXX, SEC-XXX, UX-XXX) with metrics
- [ ] All requirements traceable to research findings
- [ ] Each requirement has clear acceptance criteria

### Edge Cases (Research-Backed)

- [ ] All EDGE-XXX cases documented with research references
- [ ] Current behavior clearly described
- [ ] Desired behavior specified
- [ ] Test approach defined for each edge case
- [ ] Production scenarios from research all covered

### Failure Scenarios

- [ ] All FAIL-XXX scenarios documented
- [ ] Trigger conditions clearly identified
- [ ] Expected system behavior specified
- [ ] User communication/error messages defined
- [ ] Recovery approaches documented

### Implementation Constraints

- [ ] Context requirements specified (<40% target)
- [ ] Essential files for implementation listed with reasons
- [ ] Files suitable for subagent delegation identified
- [ ] Technical constraints from research documented

### Modules

- [ ] `## Modules` section is present
- [ ] Every module has `Public Interface`, `Hides`, `Risk`, and `Spec refs` filled in
- [ ] No shallow modules without explicit justification (interface comparable to or larger than what is hidden)
- [ ] Every REQ-XXX, EDGE-XXX, FAIL-XXX is mapped to at least one module via `Spec refs`
- [ ] Risk tiers are plausible (high-stakes modules — auth, payment, irreversible writes — are not marked `low`)

### Validation Strategy

- [ ] Unit test scenarios specified
- [ ] Integration test points identified
- [ ] Edge case test coverage defined
- [ ] Performance validation metrics specified
- [ ] Manual verification steps documented

### Dependencies and Risks

- [ ] External dependencies identified
- [ ] Risk assessment completed (RISK-XXX items)
- [ ] Mitigation strategies defined for each risk

### Implementation Notes

- [ ] Suggested implementation approach provided
- [ ] Areas requiring careful inline analysis marked
- [ ] Critical implementation considerations from research included

## 2. Stakeholder Alignment Verification

Confirm stakeholder reviews and approvals:

### Review Checklist

- [ ] Product Team review completed
  - Requirements aligned with product vision
  - User experience considerations addressed
  - Success criteria approved

- [ ] Engineering Team review completed
  - Technical feasibility confirmed
  - Architecture approach validated
  - Performance requirements achievable

- [ ] Security Team review (if applicable)
  - Security requirements adequate
  - Data privacy considerations addressed
  - Authentication/authorization approach approved

- [ ] Legal/Compliance review (if applicable)
  - Regulatory requirements met
  - Data handling compliant
  - Terms of service considerations addressed

### Feedback Integration

Document any stakeholder feedback received and how it was addressed:

- Product feedback: [What was raised and how addressed]
- Engineering feedback: [Technical concerns and resolutions]
- Security feedback: [Security considerations and mitigations]

## 3. Implementation Readiness Assessment

Evaluate specification readiness for implementation phase:

### Ready for Implementation

- [ ] All required specification sections complete
- [ ] Success criteria clearly defined and measurable
- [ ] Edge cases have expected behaviors specified
- [ ] Failure scenarios include recovery approaches
- [ ] Test scenarios cover all requirements

### Implementation Guidance Clear

- [ ] Context management plan documented (<40% utilization)
- [ ] Essential files identified with line ranges
- [ ] Areas requiring careful inline analysis marked
- [ ] Implementation approach provides clear direction

### Blocking Items Resolved

- [ ] All "must have" requirements specified
- [ ] Critical technical decisions made
- [ ] External dependencies identified and understood
- [ ] Risk mitigation strategies defined

## 4. Quality Verification

Final quality check before completion:

### Specification Quality

- [ ] All research findings incorporated into specification
- [ ] Requirements are specific, measurable, achievable, relevant, time-bound (SMART)
- [ ] Edge cases cover all production scenarios from research
- [ ] Failure modes include graceful degradation strategies
- [ ] Testing strategy comprehensive and executable

### Traceability

- [ ] Every requirement traces back to research findings
- [ ] All stakeholder needs addressed in specification
- [ ] Production issues from research have corresponding solutions
- [ ] Edge cases mapped to historical incidents

### Completeness

- [ ] No placeholder text or TODOs remaining
- [ ] All sections have substantive content
- [ ] Cross-references between sections are accurate
- [ ] File path references include specific line numbers where helpful

## 5. Capture Glossary Deltas Introduced by the Spec

If the spec introduced or refined any domain terms beyond what was added to `SDD/UBIQUITOUS_LANGUAGE.md` during the research phase (e.g., new module names that became canonical, action verbs adopted in REQ-XXX, state names introduced in EDGE-XXX), apply those deltas to the glossary now. This keeps the implementation phase and downstream cycles aligned to the same vocabulary.

Maintenance is incremental — do not rewrite stable entries. If the spec uses a term that contradicts an existing glossary entry, resolve the contradiction explicitly (update the entry or rename in the spec — do not let both stand). If the spec introduced no new domain terms, skip this step and note "no glossary changes" in the progress file.

## 6. Update Progress File for Phase Transition

Update `SDD/orchestration/progress.md` with planning completion and implementation handoff:

```markdown
## Planning Phase - COMPLETE

### Specification Finalized
- Document: `SDD/requirements/SPEC-[###]-[feature-name].md`
- Completion timestamp: [YYYY-MM-DD HH:MM:SS]
- Stakeholder approvals: [List teams that approved]
- Implementation ready: YES

### Key Decisions Made
- [Major architectural decision]
- [Technology choice with rationale]
- [Trade-off decision made]

### Research Foundation Applied
- Production issues addressed: [Count]
- Edge cases specified: [Count]
- Test scenarios defined: [Count]

## Implementation Phase - READY TO START

### Implementation Priorities
1. [First component/feature to implement]
2. [Second priority]
3. [Third priority]

### Critical Implementation Notes
- [Key technical decision from spec]
- [Important constraint to remember]
- [Subagent delegation opportunity]

### Context Management Strategy
- Target utilization: <40%
- Essential files: [List with line ranges]
- Delegatable research: [Tasks for subagents]

### Known Risks for Implementation
- [RISK-001 with mitigation approach]
- [RISK-002 with mitigation approach]

### Next Steps
Planning phase complete. Ready for implementation-start.
Specification provides comprehensive implementation guidance.
```

## 7. Final Checklist Before Completion

Before marking the planning phase as complete:

- [ ] Specification document fully populated (no TODOs or placeholders)
- [ ] All stakeholder reviews completed or explicitly waived
- [ ] Implementation readiness verified
- [ ] Progress file updated with transition information
- [ ] Quality verification passed
- [ ] Implementation priorities clearly defined

## Phase Transition

Planning phase is now COMPLETE.

The specification in `SDD/requirements/SPEC-[###]-[feature-name].md` provides comprehensive guidance for implementation.

Return a bounded result (≤200 words) summarizing:
- Specification document path and status
- Checklist items that passed vs. any gaps found
- Glossary changes applied (or "no glossary changes")
- Any blocking items that must be resolved before implementation begins

Include the path to `SDD/orchestration/progress.md` as an artifact path in your return.

---

Phase Status: FINISHED
Next Phase: implementation-start
