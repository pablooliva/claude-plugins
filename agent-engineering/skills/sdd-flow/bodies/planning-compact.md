# Planning Progress Compaction

You are a spawned subagent in an orchestrated /sdd-flow run. Your prompt provides resolved artifact paths and identifiers — use them verbatim. This file is your complete instruction set. You cannot spawn subagents and cannot invoke slash commands; all work happens inline in your own context.

You are reading this because your Reads-counter safety-net tripped mid-phase. Follow these compaction instructions to write `SDD/orchestration/compacted/planning-compacted-[YYYY-MM-DD_HH-MM-SS].md`, append a `## PARTIAL: needs continuation` block to `SDD/orchestration/progress.md` with the compaction file path and where you left off, then return ≤100 words to the orchestrator stating a Mid-Phase Handoff is required.

## Process

### 1. Create Timestamped Compaction File

Write to: `SDD/orchestration/compacted/planning-compacted-[YYYY-MM-DD_HH-MM-SS].md` where:

- `[YYYY-MM-DD_HH-MM-SS]` is the current timestamp (24-hour time)
- Example: `planning-compacted-2025-10-01_14-30-45.md`

### 2. Document Structure

Use the following template:

```markdown
# Planning Compaction - [Feature Name] - [Date/Time]

## Session Context

- Compaction trigger: [context %] utilization
- Specification focus: [which part of SPEC-[###] we're working on]
- Research foundation: RESEARCH-[###]-[feature-name].md
- Session duration: [approximate time/interactions]

## Recent Specification Work
[List specific specification sections/documents modified with file:line references where relevant]
- Requirements defined: [brief description of requirements added]
- Edge cases specified: [number of EDGE-XXX cases documented]
- Success criteria established: [areas covered]
- Validation strategy: [testing approach defined]

**Avoid large content blocks** - use file:line references instead

## Specification Progress

### Completed Sections
- Intent statements: [specific sections completed]
- Success criteria: [REQ-XXX items fully defined]
- Edge cases: [EDGE-XXX cases documented]
- Failure scenarios: [FAIL-XXX scenarios specified]
- Validation strategy: [test scenarios defined]

### In Progress
- Current section: [exact section being worked on]
- Completion status: [percentage or description]
- Blocking items: [what's preventing completion]

### Remaining Work
- [ ] [Specification section not yet started]
- [ ] [Stakeholder validation needed]
- [ ] [Edge case analysis required]
- [ ] [Success criteria to define]
- [ ] [Test scenarios to specify]

## Research Foundation Applied

### Production Issues Addressed
- Issue #[XXX]: [How it's being addressed in spec]
- Issue #[YYY]: [How it's being addressed in spec]

### Stakeholder Requirements Incorporated
- Product Team: [Requirements reflected in spec]
- Engineering Team: [Technical constraints applied]
- Support Team: [Pain points being resolved]

### Edge Cases from Research
- EDGE-001: [Based on research finding about...]
- EDGE-002: [Based on production scenario...]
- EDGE-003: [Based on stakeholder feedback...]

## Critical Learnings
[Important discoveries made during planning - research insights applied, constraint discoveries, stakeholder feedback]
- Research insights applied: [How research findings shaped specification]
- Technical constraints discovered: [New limitations found during spec writing]
- Stakeholder clarifications: [Key feedback that changed approach]
- Implementation considerations: [Technical details that affect the spec]

## Critical Review Status
[Check for critical review documents in SDD/reviews/CRITICAL-SPEC-*.md and CRITICAL-RESEARCH-*.md]
- Review performed: [yes/no - check for CRITICAL-SPEC-*.md]
- Review document: [path to CRITICAL-SPEC-*.md if exists]
- Prior research review: [path to CRITICAL-RESEARCH-*.md if exists]
- Unresolved findings: [list any HIGH/MEDIUM findings not yet addressed]
- Actions taken: [findings already addressed during this session]
- Pending actions: [findings that still need attention on continuation]
- Spec changes driven by review: [requirements added/modified due to critical review]

## Critical References
[Essential documents/files needed to continue]
- Research document: SDD/research/RESEARCH-[###]-[feature-name].md
- Specification in progress: SDD/requirements/SPEC-[###]-[feature-name].md:[lines]
- Related architecture docs: [path if applicable]
- Integration contracts: [API specs, interfaces if relevant]
- Critical review (if exists): SDD/reviews/CRITICAL-SPEC-[feature-name]-YYYYMMDD.md

## Inline Investigation Performed
[Document the file discovery / analysis you did inline during planning]
- Searches run (Grep/Glob): [What was searched/found]
- Files read for analysis: [Key files and what they yielded]
- Results integrated: [How findings affected spec]

## Continuation Priorities

**Essential Files to Reload:**
- SDD/requirements/SPEC-[###]-[feature-name].md:[specific line ranges]
- SDD/research/RESEARCH-[###]-[feature-name].md:[sections needed]
- [Any other critical files with line ranges]

**Current Focus:**
- Exact specification section being developed: [specific section name]
- Open questions requiring resolution: [list any blockers]
- Stakeholder feedback needed on: [specific areas]

**Planning Priorities:**
1. [Immediate: Complete current section - specify exactly what]
2. [Next: Following section/validation task]
3. [Then: Subsequent specification work]

**Specification Quality Checklist:**
- [ ] All research findings incorporated into requirements
- [ ] Edge cases have clear expected behaviors defined
- [ ] Success criteria are measurable and specific
- [ ] Failure scenarios include recovery approaches
- [ ] Validation strategy covers all requirements
- [ ] Implementation constraints documented
- [ ] Stakeholder requirements reflected accurately

## Implementation Readiness Assessment

### Ready for Implementation
- [Sections complete enough for coding to begin]

### Blocking Implementation
- [Sections that must be completed before coding]

### Can Be Refined During Implementation
- [Sections that can be iteratively improved]

## Other Notes
[Any additional context, unresolved questions, important considerations for continuation]
- Alternative approaches considered: [Options evaluated but not chosen]
- Deferred decisions: [Items postponed for later resolution]
- Dependencies identified: [External factors affecting the spec]
```

### 3. Update Current Progress

Also update `SDD/orchestration/progress.md` with:

- Latest specification state (sections completed vs remaining)
- Key decisions made during this session
- Continuation point
- Reference to this compaction file
- DO NOT reset previous phase information - add to it

## Guidelines

- **Be thorough but concise** - capture key specification decisions without overwhelming context
- **Avoid excessive content blocks** - prefer file:line references over large specification excerpts
- **Include precise references** - enable quick reload of research and spec documents
- **Document insights** - preserve critical learnings from research and stakeholder feedback
- **Mark clear status** - distinguish completed vs. in-progress vs. planned sections
- **Track research foundation** - show how research findings are being applied to the spec
- **Note subagent usage** - document delegated research to avoid repetition

## Quality Verification

Before compacting, ensure:

- [ ] All template sections above have meaningful content
- [ ] File references include specific line numbers where helpful
- [ ] Progress accurately reflects current state
- [ ] Critical learnings are captured
- [ ] Next priorities are clearly defined
- [ ] Research foundation tracking is complete
