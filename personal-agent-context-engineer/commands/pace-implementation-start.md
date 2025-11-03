# Initialize Implementation Phase

IMPLEMENTATION PHASE INITIALIZATION

Starting implementation phase to execute planned tasks.

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
  - Being prepared to run /pace-implementation-compact soon

If > 40%: ⚠️ CRITICAL - Context usage is too high ([X]%).
  - You should run /pace-implementation-compact before starting
  - Clear session and use /pace-continue to resume with fresh context
```

Proceed with caution if context is above 35%.

## Initial Context Load

1. **Read Progress File:**
   - Load `PACE/prompts/context-management/progress.md` to understand planning completion status
   - Identify the plan document referenced
   - Note any important context from the planning phase

2. **Update Progress for Implementation Phase:**
   - Add a new implementation section to `PACE/prompts/context-management/progress.md`
   - IMPORTANT: Preserve all research and planning phase information - do NOT delete or reset it
   - Add reference to the IMPLEMENTATION document being created
   - Document the transition from planning to implementation phase

## Implementation Setup

1. **Check for Existing Implementation Documents:**
   - Search for any existing `PACE/prompts/IMPLEMENTATION-[###]-*.md` files
   - If an implementation document with the same number already exists:

     ```text
     ⚠️ WARNING: Implementation document already exists!

     Found: PACE/prompts/IMPLEMENTATION-[###]-[existing-name].md

     Options:
     1. Continue with existing implementation document
     2. Create new implementation with different number
     3. Archive existing and create new (if previous was abandoned)

     Please clarify how to proceed.
     ```

   - Only proceed to create new document if no duplicate exists or user explicitly approves

2. Create `PACE/prompts/IMPLEMENTATION-[###]-[task-name]-[YYYY-MM-DD].md` document where:
   - `[###]` matches the plan and research document numbers (e.g., if using PLAN-042, create IMPLEMENTATION-042)
   - `[task-name]` is a kebab-case description matching the plan document
   - `[YYYY-MM-DD]` is today's date
   - Full example: `IMPLEMENTATION-042-organize-documents-2024-11-03.md`

## Prerequisite Verification

Before starting implementation:

1. **Locate Plan Document:**
   - Find the corresponding `PACE/plans/PLAN-[###]-[task-name].md` file
   - If multiple plans exist, ask user which one to implement
   - Verify the plan is complete (has all sections filled)

2. **Confirm Plan Completeness:**
   - Goal & Context: Clear objectives and success criteria
   - Task Breakdown: Detailed phases and tasks defined
   - Resources & Tools: All requirements identified
   - Risk Assessment: Risks identified with mitigation strategies
   - Implementation Strategy: Approach and checkpoints defined

3. **Validate Plan Quality:**
   - If any plan sections are missing or incomplete, warn the user
   - Check if `/pace-planning-complete` was run
   - Suggest reviewing the plan for completeness before implementation

## Implementation Document Structure

Create the implementation tracking document using this template:

```markdown
# IMPLEMENTATION-[###]-[task-name]: [Task Description]

## Implementation Summary

- **Based on Plan:** PLAN-[###]-[task-name].md
- **Start Date:** [YYYY-MM-DD HH:MM]
- **Status:** In Progress
- **Current Phase:** [Phase name from plan]

## Task Progress Tracking

### Phase 1: [Phase Name from Plan]

#### Task 1.1: [Task Description]
- **Status:** [Not Started/In Progress/Completed/Blocked]
- **Start Time:** [HH:MM]
- **Completion Time:** [HH:MM]
- **Actions Taken:**
  - [Specific action completed]
  - [Another action completed]
- **Output Created:**
  - [File/document created with location]
  - [Another output with location]
- **Notes:** [Any important observations or issues]

#### Task 1.2: [Task Description]
- **Status:** [Not Started/In Progress/Completed/Blocked]
- **Start Time:** [HH:MM]
- **Actions Taken:**
  - [Actions as they're completed]
- **Output Created:**
  - [Outputs as they're created]
- **Notes:** [Important information]

### Phase 2: [Phase Name from Plan]

[Continue with tasks from plan...]

## Deliverables Created

### Documents
- **[Document Name]:** `PACE/deliverables/[filename]`
  - Purpose: [What this document provides]
  - Status: [Draft/Review/Final]

### Scripts & Automation
- **[Script Name]:** `scripts/[filename]`
  - Purpose: [What the script does]
  - Usage: [How to use it]
  - Status: [Tested/In Development]

### Other Outputs
- **[Output Name]:** [Location]
  - Description: [What it is]
  - Status: [Complete/Partial]

## Issues & Resolutions

### Issue 1: [Issue Description]
- **Discovered:** [When/where]
- **Impact:** [How it affects the task]
- **Resolution:** [How it was resolved]
- **Status:** [Resolved/Pending/Escalated]

### Issue 2: [Issue Description]
- **Discovered:** [When/where]
- **Impact:** [How it affects the task]
- **Resolution:** [Planned resolution]
- **Status:** [Resolved/Pending/Escalated]

## Checkpoints & Validation

### Checkpoint 1: [From plan]
- **Scheduled:** [When]
- **Completed:** [When]
- **Result:** [Pass/Fail/Partial]
- **Notes:** [What was found]

### Checkpoint 2: [From plan]
- **Scheduled:** [When]
- **Status:** [Pending/Complete]

## Context & Session Management

### Session History
- Session 1: [Date/Time] - [What was accomplished]
- Session 2: [Date/Time] - [What was accomplished]

### Context Compactions
- Compaction 1: [Date/Time] - Context was at [X]%
- Files preserved: [Key files kept in context]

## Success Criteria Validation

From PLAN-[###]:
- [ ] [Success criterion 1]
- [ ] [Success criterion 2]
- [ ] [Success criterion 3]

## Next Actions

### Immediate Tasks
1. [Next task to complete]
2. [Another pending task]
3. [Third task]

### Blockers
- [Any blocking issues]
- [Dependencies waiting on]

## Completion Status

**Overall Progress:** [X]% complete
**Estimated Completion:** [Date/Time estimate]
**Final Status:** [In Progress/Completed/Partial/Blocked]
```

## Implementation Process

1. **Load Plan Foundation:**
   - Read the complete PLAN-XXX document
   - Extract all tasks, resources, and checkpoints
   - Note success criteria and validation requirements

2. **Execute Tasks Systematically:**
   - Follow the phased approach from the plan
   - Document actions as you take them
   - Create deliverables in appropriate locations
   - Track time and progress for each task

3. **Manage Issues Proactively:**
   - Document any issues as they arise
   - Apply mitigation strategies from plan
   - Escalate blockers to user attention
   - Track resolutions and workarounds

4. **Validate Progress:**
   - Check against success criteria regularly
   - Run validation checkpoints from plan
   - Ensure deliverables meet requirements
   - Document any deviations from plan

## Context Management & Subagent Usage

### Context Target

- Maintain <40% context utilization during implementation
- Focus on execution rather than research
- Use subagents for information gathering tasks

### Available Subagents for Implementation

Use these subagents (via Task tool) to support implementation:

1. **Explore subagent** (`subagent_type=Explore`)
   - Use for: Finding specific files or information
   - Example: Locating existing documents to update
   - When to use: Need to search project files

2. **general-purpose subagent** (`subagent_type=general-purpose`)
   - Use for: Complex sub-tasks or research
   - Example tasks:
     - "Create a script to automate [specific task]"
     - "Research how to [specific technical task]"
     - "Generate documentation for [deliverable]"
   - When to use: Delegate complex work to preserve context

### Delegation Strategy

- Delegate research and exploration tasks
- Keep main context focused on coordination
- Use parallel subagents for independent tasks
- Document subagent outputs in implementation tracking

## Quality Assurance

During implementation:

- Follow the plan systematically
- Document all actions and outputs
- Track issues and resolutions
- Validate against success criteria
- Create quality deliverables
- Maintain clear progress tracking

## Deliverable Guidelines

### Document Creation
- Place in `PACE/deliverables/` directory
- Use clear, descriptive names
- Include headers with metadata
- Follow project documentation standards

### Script Development
- Place in `scripts/` directory
- Include usage documentation
- Add error handling
- Test before marking complete

### File Organization
- Follow project structure conventions
- Create logical directory hierarchies
- Maintain consistent naming patterns
- Document organizational decisions

## Completion Criteria

Implementation is complete when:

- ✓ All tasks from plan are executed
- ✓ All deliverables are created
- ✓ Success criteria are met
- ✓ Checkpoints are validated
- ✓ Issues are resolved or documented
- ✓ Documentation is complete

---

Begin implementation now. Create the `PACE/prompts/IMPLEMENTATION-[###]-[task-name]-[YYYY-MM-DD].md` document and start executing the planned tasks systematically.