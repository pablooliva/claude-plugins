# Mid-Phase Handoff Continuation

You are a spawned subagent in an orchestrated /sdd-flow run. Your prompt provides resolved artifact paths and identifiers — use them verbatim. This file is your complete instruction set. Do not spawn subagents or invoke slash commands/skills, even if an Agent/Task tool is available — the flow’s flat-orchestration contract forbids it; all work happens inline in your own context.

You are a continuation subagent spawned because a prior phase subagent tripped the safety-net and bailed out. Read the compaction file named in your prompt FIRST, resume the interrupted phase from its 'Current Focus' section, and inherit the same Reads-counter safety-net (you may bail out again, producing another handoff).

## Process

### 1. Load Progress and Compaction Files

1. **Read Main Progress File:**
   - Load `SDD/orchestration/progress.md`
   - Identify current phase (research/planning/implementation)
   - Note completion status and next priorities

2. **Locate Most Recent Compaction File:**
   - Check `SDD/orchestration/` for latest compaction file:
     - Research phase: `research-compacted-[YYYY-MM-DD_HH-MM-SS].md`
     - Planning phase: `planning-compacted-[YYYY-MM-DD_HH-MM-SS].md`
     - Implementation phase: `implementation-compacted-[YYYY-MM-DD_HH-MM-SS].md`
     - Generic (any phase): `compact-[YYYY-MM-DD_HH-MM-SS].md`
   - Load the most recent file based on timestamp (24-hour format with underscores)
   - Note: Files use format `YYYY-MM-DD_HH-MM-SS` (e.g., `2025-10-01_14-30-45`)
   - Generic compaction files work for smaller tasks, follow-ups, or ad-hoc work

### 2. Pre-Continuation Quality Check

Before resuming work, verify from the compaction file:

- [ ] All essential files are listed with specific line ranges
- [ ] Current focus section clearly identifies the exact task to resume
- [ ] Any blocking items or unresolved questions are documented
- [ ] Priority list provides clear next steps

If any critical information is missing, note the gap in `SDD/orchestration/progress.md` and proceed with the best available context.

### 3. Phase-Specific Context Loading

#### For Research Phase Continuation

1. **Load Research Context:**
   - Research document: `SDD/research/RESEARCH-[###]-[feature-name].md`
   - Files from "Essential Files to Reload" section in compaction
   - Recent investigation areas from "Continuation Priorities"

2. **Verify Research State:**
   - Review "Research Progress" section (completed/in-progress/planned)
   - Check "Outstanding Research Questions" checklist
   - Identify current investigation focus
   - Note any "System Behavior Discovered" insights

3. **Resume Research:**
   - Continue with exact investigation from "Current Focus" section
   - Perform all file searches and reads inline in your own context
   - Document findings in the research document

#### For Planning Phase Continuation

1. **Load Planning Context:**
   - Specification document: `SDD/requirements/SPEC-[###]-[feature-name].md:[lines]`
   - Research document: `SDD/research/RESEARCH-[###]-[feature-name].md:[sections]`
   - Files from "Essential Files to Reload" with specific line ranges

2. **Verify Specification State:**
   - Review "Specification Progress" (completed sections vs remaining)
   - Check "Specification Quality Checklist" status
   - Identify exact section being worked on
   - Review "Implementation Readiness Assessment" if present

3. **Resume Planning:**
   - Continue with section from "Current Focus"
   - Apply "Research Foundation Applied" findings
   - Address items in "Planning Priorities" list

#### For Implementation Phase Continuation

1. **Load Implementation Context:**
   - Implementation prompt: `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[date].md`
   - Specification: `SDD/requirements/SPEC-[###]-[feature-name].md`
   - Files from "Essential Files to Reload"
   - Review any "Technical Decisions" or "Critical Learnings" from compaction

2. **Verify Implementation State:**
   - Review completed vs remaining implementation tasks
   - Check "Tests Status" section for test coverage
   - Identify current implementation focus
   - Review "Specification Validation Remaining" checklist

3. **Resume Implementation:**
   - Continue with task from "Current Focus"
   - Follow implementation priorities list
   - Address any "Edge case handling" or "Performance considerations" noted

### 4. Quality Verification Before Resuming

Complete this checklist before starting work:

- [ ] All essential files successfully loaded
- [ ] Understanding of current phase status is clear
- [ ] Next priority task is specifically identified
- [ ] Previous session's critical learnings are understood
- [ ] Blocking items or questions are noted

If any verification fails, document the issue in `SDD/orchestration/progress.md` and proceed with the best available information.

### 5. Resume Work

1. **Continue Work:**
   - Execute the specific next task identified in the "Current Focus" section
   - Update relevant phase document as you progress
   - Maintain continuity with the prior subagent's approach
   - Perform all file reads and code searches inline in your own context

2. **Update Progress File:**
   - Add new accomplishments to `SDD/orchestration/progress.md`
   - Update "Continuation Priorities" section
   - Note any new blocking items discovered
   - **IMPORTANT: DO NOT reset or delete previous phase information — append to it**

### 6. Safety-Net and Bounded Return

The Reads counter inherited from the prior subagent applies here. If you trip it again:

1. Write a new compaction file to `SDD/orchestration/` using the appropriate naming convention for the current phase (e.g., `implementation-compacted-[YYYY-MM-DD_HH-MM-SS].md`)
2. Update `SDD/orchestration/progress.md` with current state (append only)
3. Return a bounded result (≤200 words + artifact paths): summarize what was accomplished, the new compaction file path, and the next task from "Current Focus"

If the phase completes fully, return a bounded result (≤200 words + artifact paths): summarize what was accomplished, list all artifact paths written, and note the phase as complete.

### 7. Session Continuity Best Practices

1. **Preserve Context Learnings:**
   - Reread "Critical Learnings" section carefully
   - Apply previous discoveries to current work
   - Avoid re-researching already discovered information

2. **Maintain Phase Momentum:**
   - Stay focused on current phase objectives
   - Do not backtrack to previous phases unless critical
   - Trust the work documented in compaction files

3. **Document Incremental Progress:**
   - Update `SDD/orchestration/progress.md` after each significant milestone
   - Note any new discoveries or blockers immediately
   - Keep "Continuation Priorities" current

## Important Notes

- `SDD/orchestration/progress.md` is the primary continuation point across all phases
- Compaction files provide detailed context from the prior subagent's run
- Each phase builds upon previous phases — maintain continuity
- If multiple compaction files exist, use the most recent one based on timestamp
- Never reset or overwrite previous phase information in `SDD/orchestration/progress.md`

## Error Recovery

If continuation context is unclear:

1. Check for most recent compaction file in `SDD/orchestration/`
   - Look for: `compact-*.md`, `research-compacted-*.md`, `planning-compacted-*.md`, `implementation-compacted-*.md`
2. Verify `SDD/orchestration/progress.md` exists and contains phase information
3. If phase is ambiguous, examine the compaction file header and progress.md together to determine it
4. If next task is unclear, derive it from the compaction file's "Priority" and "Current Focus" sections
