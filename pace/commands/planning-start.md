# Initialize Planning

PLANNING INITIALIZATION

Starting planning for a task or project.

NOTE: This command can be used standalone or after research. No prior phase is required.

IMPORTANT: This command works best with Claude Sonnet. If you are NOT running on a Claude Sonnet model (e.g., claude-sonnet-*), inform the user: "Note: Planning works well with Claude Sonnet. You're currently using [model name]."

## Initial Context Load

1. **Check for Existing Context:**
   - If `PACE/prompts/context-management/progress.md` exists, read it
   - Determine if existing content is **related** to this new planning task:
     - **Related** (e.g., research for this task): Preserve and build upon it
     - **Unrelated** (different task entirely): Ask user if they want to archive it to `PACE/prompts/context-management/archive/progress-[YYYY-MM-DD_HH-MM-SS].md` before starting fresh

2. **Update Progress for Planning:**
   - If archiving, create fresh file with: `# Current Progress - Planning`
   - If building on prior work, add a planning section
   - Add reference to the PLAN document being created

## Planning Setup

1. Create `PACE/plans/PLAN-[###]-[task-name].md` document where:
   - `[###]` matches the research document number if applicable, or use sequential numbering
   - `[task-name]` is a kebab-case description (e.g., "organize-documents", "automate-workflow", "decision-framework")
   - Full example: `PLAN-042-organize-documents.md`

## Prerequisite Verification

Before creating the plan:

1. **Check for Research Foundation:**
   - If research exists, locate the corresponding `PACE/research/RESEARCH-[###]-[topic-name].md` file
   - If no research exists but is needed, suggest running `/research-start` first
   - For simple tasks, proceed without research

2. **Understand Task Requirements:**
   - Clarify the goal and desired outcomes
   - Identify constraints and limitations
   - Note available resources and tools

## Plan Document Structure

Create the plan using this template:

```markdown
# PLAN-[###]-[task-name]

## Executive Summary

- **Based on Research:** RESEARCH-[###]-[topic-name].md (if applicable)
- **Creation Date:** [YYYY-MM-DD]
- **Author:** Claude (with [user's name if known])
- **Status:** Draft/In Review/Approved
- **Estimated Effort:** [time estimate if applicable]

## Goal & Context

### Primary Objective
[Clear statement of what we're trying to achieve]

### Background
[Why this task is important and any relevant context]

### Success Criteria
- [ ] [Specific, measurable outcome 1]
- [ ] [Specific, measurable outcome 2]
- [ ] [Specific, measurable outcome 3]

## Scope & Boundaries

### In Scope
- [What will be done]
- [Included activities]
- [Deliverables to create]

### Out of Scope
- [What won't be done]
- [Excluded activities]
- [Future considerations]

## Task Breakdown

### Phase 1: [Phase Name]
**Objective:** [What this phase accomplishes]
**Duration:** [Estimated time]

Tasks:
1. **Task 1.1:** [Description]
   - Action items: [Specific steps]
   - Tools needed: [Required tools/resources]
   - Output: [What will be produced]

2. **Task 1.2:** [Description]
   - Action items: [Specific steps]
   - Tools needed: [Required tools/resources]
   - Output: [What will be produced]

### Phase 2: [Phase Name]
**Objective:** [What this phase accomplishes]
**Duration:** [Estimated time]

Tasks:
1. **Task 2.1:** [Description]
   - Action items: [Specific steps]
   - Tools needed: [Required tools/resources]
   - Output: [What will be produced]

## Resources & Tools

### Information Resources
- [Document/file]: [Location] - [Purpose]
- [Website/tool]: [URL] - [How it will be used]

### Scripts & Automation
- **Script needed:** [Description of automation opportunity]
  - Purpose: [What it will do]
  - Input: [What it needs]
  - Output: [What it produces]

### External Dependencies
- [Dependency]: [Description and impact]
- [Tool/service]: [Requirements and alternatives]

## Risk Assessment

### Identified Risks
- **RISK-001:** [Risk description]
  - Probability: [Low/Medium/High]
  - Impact: [Low/Medium/High]
  - Mitigation: [How to prevent or handle]

- **RISK-002:** [Risk description]
  - Probability: [Low/Medium/High]
  - Impact: [Low/Medium/High]
  - Mitigation: [How to prevent or handle]

## Implementation Strategy

### Approach
[High-level strategy for executing the plan]

### Key Decisions
- Decision 1: [What needs to be decided and criteria]
- Decision 2: [What needs to be decided and criteria]

### Checkpoints
- [ ] After Phase 1: [What to verify]
- [ ] Mid-implementation: [Progress check]
- [ ] Before completion: [Final verification]

## Deliverables

### Primary Outputs
1. **[Deliverable 1]:** [Description and format]
2. **[Deliverable 2]:** [Description and format]
3. **[Deliverable 3]:** [Description and format]

### Documentation
- [Document type]: [What will be documented]
- Progress updates: [How progress will be tracked]

## Validation & Review

### Quality Checks
- [ ] [What to verify for quality]
- [ ] [Acceptance criteria]
- [ ] [Review requirements]

### Stakeholder Review
- [ ] Initial plan review
- [ ] Mid-point check-in
- [ ] Final approval

## Next Steps

### Immediate Actions
1. [First action to take]
2. [Second action to take]
3. [Third action to take]

### Follow-up Tasks
- [Future consideration 1]
- [Future consideration 2]
```

## Planning Process

1. **Understand the Goal:**
   - Clarify what success looks like
   - Identify measurable outcomes
   - Define boundaries and constraints

2. **Break Down the Work:**
   - Decompose the goal into phases
   - Create specific, actionable tasks
   - Estimate effort and resources needed

3. **Identify Dependencies:**
   - Note information requirements
   - Identify tools and scripts needed
   - Consider external dependencies

4. **Assess Risks:**
   - Anticipate potential problems
   - Plan mitigation strategies
   - Build in checkpoints for validation

## Context Management & Subagent Usage

### Context Target

- Maintain <40% context utilization during planning
- Focus on strategy rather than execution details
- Prepare clear guidance for execution

### Available Subagents for Planning

Use these subagents (via Task tool) to enhance planning:

1. **Explore subagent** (`subagent_type=Explore`)
   - Use for: Analyzing existing files and documents
   - Example: Understanding current project structure
   - When to use: Need to investigate what already exists

2. **general-purpose subagent** (`subagent_type=general-purpose`)
   - Use for: Researching best practices and methodologies
   - Example tasks:
     - "Research best practices for [task type]"
     - "Find tools and services for [specific need]"
     - "Analyze approaches for [problem]"
   - When to use: Need expert knowledge or recommendations

### Delegation Strategy

- Delegate research tasks to preserve context
- Use parallel subagent calls for independent research
- Document findings directly in relevant plan sections

## Deliverable Expectations

A complete plan must have:

- ✓ Clear, measurable success criteria
- ✓ Detailed task breakdown with actionable steps
- ✓ Resource and tool requirements identified
- ✓ Risk assessment with mitigation strategies
- ✓ Implementation strategy with checkpoints
- ✓ Defined deliverables and validation approach

## Quality Checklist

Before considering the plan complete:

- [ ] Goals are clear and measurable
- [ ] Tasks are specific and actionable
- [ ] Resources and tools are identified
- [ ] Risks are assessed with mitigations
- [ ] Checkpoints provide validation opportunities
- [ ] Deliverables are well-defined
- [ ] Next steps are clear

---

Begin plan creation now. Create the `PACE/plans/PLAN-[###]-[task-name].md` document and develop a comprehensive, actionable plan for the task at hand.
