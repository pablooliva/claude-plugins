# Initialize Research Phase

You are a spawned subagent in an orchestrated /sdd-flow run. Your prompt provides resolved artifact paths and identifiers — use them verbatim. This file is your complete instruction set. You cannot spawn subagents and cannot invoke slash commands; all work happens inline in your own context.

RESEARCH PHASE INITIALIZATION

Starting research phase for new feature/issue.

IMPORTANT: Before starting this phase, check if `SDD/orchestration/progress.md` contains any important information about an existing task. If it does and this appears to be a different task, append an `## Awaiting Archive Decision` block (stating the conflict and asking whether to archive the existing content) to `SDD/orchestration/progress.md`, then return to the orchestrator. Otherwise, reset the file to only contain a heading: `# Research Progress`. We are starting on a new task and want to ensure that the progress file is clean.

## Pre-Research Clarification (if available)

Before any codebase investigation, check whether a clarification artifact exists for this feature:

```bash
ls SDD/research/CLARIFICATION-*.md 2>/dev/null
```

If a `CLARIFICATION-[###]-[feature-name].md` document exists matching the feature being researched, **load it first.** It contains the user's externalized design concept — clarified problem statement, success criteria, constraints, branches already resolved, and open questions inherited as research risk. The research must address every branch the clarification surfaced; open questions become explicit research targets.

If no clarification exists, the design concept lives only in the prompt. If that prompt is fuzzy, append an `## Awaiting Clarification` block (listing the ambiguities and options) to `SDD/orchestration/progress.md`, then return to the orchestrator. If the prompt is crisp, proceed directly.

Also check for `SDD/UBIQUITOUS_LANGUAGE.md` and load it if present — use the project's canonical domain vocabulary throughout the research document.

Set up systematic investigation:

## Research Setup

1. Create `SDD/research/RESEARCH-[###]-[feature-name].md` document where:
   - `[###]` is the issue/ticket number if available, or use sequential numbering (001, 002, etc.)
   - **If `SDD/research/CLARIFICATION-[###]-[feature-name].md` already exists for this feature, reuse the same `[###]` and `[feature-name]` for the RESEARCH document — do not increment. Numbering must align across CLARIFICATION → RESEARCH → SPEC → IMPLEMENTATION-PLAN.**
   - `[feature-name]` is a kebab-case description (e.g., "user-authentication", "csv-export")

Use this structure for the research document:

```markdown
# RESEARCH-[###]-[feature-name]

## System Data Flow

- Key entry points: [files and line numbers]
- Data transformations: [how information flows]
- External dependencies: [APIs, databases, services]
- Integration points: [where this feature connects to existing systems]

## Stakeholder Mental Models

- Product Team perspective:
- Engineering Team perspective:
- Support Team perspective:
- User perspective:

## Production Edge Cases

- Historical issues: [issue numbers and patterns]
- Support tickets: [common problems]
- Error logs: [failure patterns]

## Files That Matter

- Core logic: [primary implementation files]
- Tests: [existing test coverage gaps]
- Configuration: [relevant config files]

## Security Considerations

- Authentication/Authorization: [auth requirements]
- Data Privacy: [sensitive data handling]
- Input Validation: [validation needs]

## Testing Strategy

- Unit tests: [what needs testing]
- Integration tests: [integration points]
- Edge cases: [specific scenarios to test]

## Documentation Needs

- User-facing docs: [what users need to know]
- Developer docs: [API/implementation docs]
- Configuration docs: [setup/config changes]
```

## Research Process

Begin systematic system understanding:

- Map data flows across codebase with specific file:line references
- Interview/research stakeholder needs and mental models
- Analyze production issues and error patterns
- Document existing edge cases with specific examples

## Context Management

- Grep/Glob to locate files, Read only confirmed targets, keep raw output minimal. Execute all investigation inline in your own context.
- Focus on understanding before any specification work

## Deliverable Target

Complete research document that enables specification creation without additional system investigation.

When complete, return a bounded result (≤200 words + artifact path to the RESEARCH document) to the orchestrator.

Begin research now - create the `SDD/research/RESEARCH-[###]-[feature-name].md` document and start systematic investigation.
