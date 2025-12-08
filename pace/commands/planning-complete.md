# Planning Completion

PLANNING COMPLETION

Plan is complete. Finalize and determine next steps.

## 1. Verify Plan Document Completeness

Confirm that `PACE/plans/PLAN-[###]-[task-name].md` contains all essential sections:

### Core Content

- [ ] Executive summary with goal and status
- [ ] Clear success criteria (specific, measurable outcomes)
- [ ] Scope defined (what's in and out of scope)

### Task Breakdown

- [ ] Work broken into logical phases or sections
- [ ] Tasks are specific and actionable
- [ ] Dependencies identified between tasks

### Resources & Risks

- [ ] Required resources and tools identified
- [ ] External dependencies noted
- [ ] Key risks assessed with mitigation strategies

### Execution Guidance

- [ ] Implementation strategy or approach defined
- [ ] Checkpoints for progress validation
- [ ] Deliverables clearly described

## 2. Quality Check

Before marking planning complete:

- [ ] Goals are clear and achievable
- [ ] Tasks are actionable (not vague)
- [ ] No placeholder text or TODOs remaining
- [ ] Plan provides enough guidance to execute

## 3. Record Completion

Update `PACE/prompts/context-management/progress.md`:

```markdown
## Planning - COMPLETE

### Plan Finalized
- Document: `PACE/plans/PLAN-[###]-[task-name].md`
- Completion timestamp: [YYYY-MM-DD HH:MM:SS]

### Key Decisions Made
- [Major decision 1]
- [Major decision 2]

### Execution Priorities
1. [First priority]
2. [Second priority]
3. [Third priority]

### Next Steps
Planning complete. Ready for execution.
```

## 4. Determine Next Steps

Choose one:

**Proceed to Execution**
- Plan is ready to execute
- Run `/execution-start` to begin producing deliverables

**Review with Stakeholders**
- Share plan for feedback before execution
- Schedule review and iterate on plan

**Plan Complete (Standalone)**
- Planning was the goal
- Document is ready for reference or future execution

**More Planning Needed**
- Plan reveals need for additional detail
- Continue refining specific sections

## Planning Phase Complete

Plan documented and ready for use. Proceed based on your goals.
