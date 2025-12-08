# Initialize Execution

EXECUTION INITIALIZATION

Starting execution to produce deliverables.

NOTE: This command can be used standalone or after research/planning. No prior phase is required.

IMPORTANT: This command works well with Claude Sonnet. If you are NOT running on a Claude Sonnet model, inform the user: "Note: Execution works well with Claude Sonnet. You're currently using [model name]."

## Context Check

Before loading documents, check context usage:

```text
Current context utilization: [X]%

If > 35%: ⚠️ Context is high. Be prepared to run /execution-compact soon.
If > 40%: ⚠️ Consider running /compact first, then /continue to resume fresh.
```

## Initial Context Load

1. **Check for Existing Context:**
   - If `PACE/prompts/context-management/progress.md` exists, read it
   - Determine if existing content is **related** to this new execution task:
     - **Related** (e.g., plan for this task): Preserve and build upon it
     - **Unrelated** (different task entirely): Ask user if they want to archive it to `PACE/prompts/context-management/archive/progress-[YYYY-MM-DD_HH-MM-SS].md` before starting fresh

2. **Update Progress for Execution:**
   - If archiving, create fresh file with: `# Current Progress - Execution`
   - If building on prior work, add an execution section
   - Add reference to the EXECUTION document being created

## Execution Setup

1. Create `PACE/prompts/EXECUTION-[###]-[task-name]-[YYYY-MM-DD].md` document where:
   - `[###]` matches plan/research numbers if applicable, or use sequential numbering
   - `[task-name]` is a kebab-case description
   - `[YYYY-MM-DD]` is today's date
   - Example: `EXECUTION-042-quarterly-report-2024-11-03.md`

## Prerequisite Check

Before starting execution:

1. **If Plan Exists:**
   - Locate `PACE/plans/PLAN-[###]-[task-name].md`
   - Review goals, tasks, and success criteria
   - Use plan as guide for execution

2. **If No Plan:**
   - Clarify the goal and desired deliverables
   - Identify what needs to be produced
   - Proceed with direct execution

## Execution Document Structure

Create the tracking document using this template:

```markdown
# EXECUTION-[###]-[task-name]: [Task Description]

## Execution Summary

- **Based on Plan:** PLAN-[###]-[task-name].md (if applicable)
- **Start Date:** [YYYY-MM-DD HH:MM]
- **Status:** In Progress
- **Goal:** [What we're producing]

## Deliverables

### Primary Deliverables
1. **[Deliverable 1]:** [Description]
   - Location: `PACE/deliverables/[filename]`
   - Status: [Not Started/In Progress/Complete]
   - Format: [Document type - report, analysis, strategy, etc.]

2. **[Deliverable 2]:** [Description]
   - Location: `PACE/deliverables/[filename]`
   - Status: [Not Started/In Progress/Complete]
   - Format: [Document type]

### Supporting Materials
- [Material 1]: [Description and location]
- [Material 2]: [Description and location]

## Task Progress

### Task 1: [Description]
- **Status:** [Not Started/In Progress/Completed/Blocked]
- **Actions Taken:**
  - [Action completed]
  - [Another action]
- **Output:** [What was produced]
- **Notes:** [Important observations]

### Task 2: [Description]
- **Status:** [Status]
- **Actions Taken:**
  - [Actions as completed]
- **Output:** [What was produced]

## Sources & References Used

- [Source 1]: [How it was used]
- [Source 2]: [How it was used]

## Issues & Resolutions

### Issue 1: [Description]
- **Impact:** [How it affects the work]
- **Resolution:** [How resolved or plan to resolve]
- **Status:** [Resolved/Pending]

## Quality Checkpoints

- [ ] [Checkpoint 1 from plan]
- [ ] [Checkpoint 2 from plan]
- [ ] [Quality criteria]

## Success Criteria Status

From Plan (if applicable):
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

## Session Notes

### Session 1: [Date]
- What was accomplished: [Summary]
- Context at end: [X]%

## Next Actions

1. [Next task to complete]
2. [Following task]
3. [Subsequent task]

## Completion Status

**Overall Progress:** [X]% complete
**Estimated Completion:** [Date/Time]
```

## Execution Process

1. **Understand the Goal:**
   - What deliverables are needed?
   - What format should they take?
   - Who is the audience?

2. **Produce Deliverables:**
   - Create documents, reports, analysis as needed
   - Place outputs in `PACE/deliverables/` directory
   - Track progress in execution document

3. **Use Available Tools:**
   - WebSearch/WebFetch for research
   - Task tool with subagents for complex sub-tasks
   - Read/Write for document creation

4. **Validate Quality:**
   - Check against success criteria
   - Ensure deliverables meet requirements
   - Review and refine outputs

## Context Management

### Context Target

- Maintain <40% context utilization
- Focus on producing deliverables
- Use subagents for research tasks

### Available Subagents

1. **Explore subagent** (`subagent_type=Explore`)
   - Finding files and information
   - Searching project content

2. **general-purpose subagent** (`subagent_type=general-purpose`)
   - Complex research tasks
   - Generating content sections
   - Analysis work

## Deliverable Guidelines

### Document Creation
- Place in `PACE/deliverables/` directory
- Use clear, descriptive filenames
- Include metadata headers
- Follow appropriate format for document type

### Quality Standards
- Clear structure and organization
- Accurate information
- Appropriate level of detail
- Professional presentation

## Completion Criteria

Execution is complete when:
- ✓ All deliverables are created
- ✓ Success criteria are met
- ✓ Quality checkpoints pass
- ✓ Documentation is complete

---

Begin execution now. Create the `PACE/prompts/EXECUTION-[###]-[task-name]-[YYYY-MM-DD].md` document and start producing deliverables.
