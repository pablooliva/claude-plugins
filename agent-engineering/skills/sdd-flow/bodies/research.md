# Initialize Research Phase

You are a spawned subagent in an orchestrated /sdd-flow run. Your prompt provides resolved artifact paths and identifiers — use them verbatim. This file is your complete instruction set. Do not spawn subagents or invoke slash commands/skills, even if an Agent/Task tool is available — the flow’s flat-orchestration contract forbids it; all work happens inline in your own context.

RESEARCH PHASE INITIALIZATION

Starting research phase for new feature/issue.

IMPORTANT: `SDD/orchestration/progress.md` is append-only. It already holds the orchestrator's Step 0 record for this task (resolved identifiers, SKILL_ROOT and the other resolved paths, mode and flags, any `Next-tier cycle` lines) and the outcome of the clarification gate; it may also hold an earlier feature's history. Later steps and resumed sessions read all of it. Never reset, rewrite, or archive the file, and never ask whether to — clearing it is the orchestrator's rotation, not yours. Append your entry at the end, as every other body does.

## Pre-Research Clarification (if available)

Before any codebase investigation, check whether your prompt names a clarification artifact for this feature. Do not list `SDD/research/` to look for one — other clarification documents there belong to earlier features.

If your prompt names a `CLARIFICATION-[###]-[feature-name].md` document, **load it first.** It contains the user's externalized design concept — clarified problem statement, success criteria, constraints, branches already resolved, and open questions inherited as research risk. The research must address every branch the clarification surfaced; open questions become explicit research targets.

If your prompt names no clarification, the design concept lives only in the task description. Proceed with it. The orchestrator's clarification gate (Step 1.5) already offered the user a clarification pass, and declining it was their decision — do not reopen it, and do not write an `## Awaiting Clarification` block. Where the task description is ambiguous, state the assumption you made in the research document, so the research review and the design gate can see it.

Also check for `SDD/UBIQUITOUS_LANGUAGE.md` and load it if present — use the project's canonical domain vocabulary throughout the research document.

## Next-Tier Cycle (delta research)

Applies only when your prompt says `NEXT-TIER CYCLE: Tier N`. An earlier tier of this feature is already built and in use; this cycle adds the next one. Your prompt names two extra inputs — the previous tier's research document, and the tier plan (`SDD/flow/TIERS-[feature-name].md`: what shipped, what was deferred, sketches of the later tiers, and feedback from using the shipped tier). Read both before investigating.

Research the **delta**, not the feature again:

- **The deferred items aimed at this tier** — each `DEFER-XXX` row whose `To tier` is N. What does adding it now involve, given the code that exists?
- **The feedback** — every note under the tier plan's `## Feedback`, and the clarification document for this cycle. What do they change about what this tier should do?
- **What the shipped tier changed** — the code the previous tier added or reshaped. Re-trace the data flow where it differs from the previous research; that document describes the system before the previous tier was built.
- **Whether the sketch still holds** — the tier plan's sketch of this tier was written before the previous tier was used. Say what in it the feedback and the code now support, contradict, or make unnecessary.

Use the same document structure below. A section the previous research still describes correctly is one line — `Unchanged — see RESEARCH-[previous ###]-[previous feature-name].md → [section]` — not a copy. Record no structure for later tiers: this document serves Tier N only.

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
