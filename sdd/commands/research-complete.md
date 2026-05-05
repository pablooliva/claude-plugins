# Research Phase Completion

RESEARCH PHASE COMPLETION

Research phase is complete and ready for specification creation.

## 1. Verify Research Document Completeness

Confirm that `SDD/research/RESEARCH-[###]-[feature-name].md` contains all required sections with complete information:

### System Data Flow

- [ ] Key data flows identified with specific file:line references and how data moves
- [ ] Key entry points documented with specific file:line references
- [ ] Data transformations explained
- [ ] External dependencies identified
- [ ] Integration points documented (where this feature connects to existing systems)

### Stakeholder Mental Models

- [ ] Product team perspective captured
- [ ] Engineering team perspective captured
- [ ] Support team perspective captured
- [ ] User perspective captured

### Production Edge Cases

- [ ] Historical issues analyzed with issue numbers
- [ ] Support ticket patterns documented
- [ ] Error log failure patterns identified

### Files That Matter

- [ ] Core logic files identified with significance explained
- [ ] Existing test coverage gaps documented
- [ ] Configuration files noted

### Security Considerations

- [ ] Authentication/authorization requirements documented
- [ ] Data privacy concerns identified
- [ ] Input validation needs specified

### Testing Strategy

- [ ] Unit test requirements defined
- [ ] Integration test points identified
- [ ] Edge case scenarios specified

### Documentation Needs

- [ ] User-facing documentation requirements identified
- [ ] Developer documentation needs specified
- [ ] Configuration documentation requirements noted

## 2. Finalize Research Document

Ensure all investigation questions are answered and the research document provides sufficient foundation for specification creation without requiring additional system investigation.

## 3. Update Ubiquitous Language Glossary

Maintain `SDD/UBIQUITOUS_LANGUAGE.md` — a project-wide glossary of domain terms shared between user, code, and AI. The goal (Evans, *Domain-Driven Design*) is that every conversation and artifact uses the same names for the same things, so AI thinking traces stay aligned with intent and stop reinventing terminology.

**Maintenance is incremental, not regenerative.** Stable terms must persist across cycles; do not rewrite the file from scratch.

Delegate to a `general-purpose` subagent (via Task tool) with this brief:

> Read `SDD/research/RESEARCH-[###]-[feature-name].md` and the current `SDD/UBIQUITOUS_LANGUAGE.md` (if it exists). Identify domain terms introduced or refined by this research that are not yet in the glossary, and any existing glossary entries this research contradicts or sharpens.
>
> Output a proposed update as a unified diff or as explicit add/edit/remove instructions. For each new term, capture: canonical name, one-line definition, synonyms to avoid, and a code or research reference. Group terms by domain area (entities, actions, states, events, roles).
>
> Do not invent terms not grounded in the research or codebase. Do not rewrite stable entries unless this research genuinely contradicts them.

If `SDD/UBIQUITOUS_LANGUAGE.md` does not yet exist, the subagent creates it. Apply the proposed update; resolve any contradictions explicitly (note the prior definition and why it changed).

If the research is purely infrastructural and introduces no domain vocabulary, the subagent may report "no glossary changes" — record that in the progress file and skip the update.

## 4. Record Phase Transition

Write brief transition note to `SDD/orchestration/progress.md`:

"Research phase complete. RESEARCH-[###]-[feature-name].md finalized. Glossary updated (or: no glossary changes). Ready for /planning-start."

## Phase Complete

Research phase FINISHED. Next Claude Code session should begin SPEC-[###]-[feature-name] creation using this research foundation.
