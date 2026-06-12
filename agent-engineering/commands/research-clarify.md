# Research Clarify

PRE-RESEARCH DESIGN-CONCEPT CLARIFICATION

Run this command **before `/research-start`** when the user's design concept for a feature is fuzzy, ambiguous, or known to be partially unspecified. The goal is to externalize what the user actually wants — the design concept (Brooks) — through structured interviewing, before any codebase research begins.

This is **input clarification, not codebase research**. `/research-start` investigates the codebase. This command interviews the user about the feature itself: what it should do, why, for whom, under what constraints, and where the open questions still are. The output becomes the foundation that `/research-start` consumes.

If the feature is already crisply specified (e.g., a clear ticket with explicit acceptance criteria, or a small well-understood change), skip this command and go straight to `/research-start`.

## 1. Load Existing Glossary (If Present)

If `SDD/UBIQUITOUS_LANGUAGE.md` exists, load it before interviewing. Use the project's canonical domain terms in your questions and in the resulting CLARIFICATION document — do not introduce synonyms that fragment vocabulary already established in prior cycles. If the user's words conflict with the glossary, surface that mismatch as a topic to resolve during the interview (either rename the glossary entry or have the user adopt the canonical term).

If the glossary does not exist, proceed without it.

## 2. Determine Numbering and Feature Name

Choose `[###]` and `[feature-name]` consistent with how downstream artifacts will be named:

- If the user references an issue/ticket number, use it.
- Otherwise, use the next available sequential number (check `SDD/research/` for the highest existing).
- `[feature-name]` is kebab-case (e.g., `csv-export`, `bulk-invite`).

Create the artifact at `SDD/research/CLARIFICATION-[###]-[feature-name].md`. Numbering must match the eventual `RESEARCH-[###]` and `SPEC-[###]`.

## 3. Interview Posture

Adopt a relentless-but-grounded interviewing posture:

- **Walk the design tree branch by branch.** Surface every meaningful decision point. Resolve dependencies one at a time — do not let the user gloss over a fork by saying "we'll figure that out later."
- **No leading questions.** Do not propose a design and ask for approval; that compresses the design concept into yours, not theirs.
- **Probe vague terms.** When the user says "users," "data," "fast," "later," "if needed," "etc." — stop and ask which users, which data, how fast, when, under what conditions.
- **Surface assumptions.** When the user states something as a fact, ask how they know. Distinguish observed behavior, expected behavior, and aspirational behavior.
- **Ask one question at a time.** Multiple-question dumps let the user answer the easy one and skip the hard one.
- **Capture disagreements with stakeholders.** If the user mentions a stakeholder ("Product wants X"), ask whether the user agrees, has unresolved tension, or hasn't validated.
- **Stop when the tree is walked, not when the user is tired.** It is acceptable for the conversation to take many turns. The output must reflect a real shared understanding, not surface agreement.

If the user pushes to skip ahead ("just write the spec already"), surface the cost: every unresolved branch becomes either an arbitrary AI choice during research, an ambiguous requirement during planning, or a wrong implementation during coding. Offer to record the unresolved branches and proceed with explicit acknowledgement that research and spec will inherit those gaps.

## 4. The Branches to Walk

For every feature, walk these branches at minimum. Skip a branch only when it is genuinely not applicable, and explicitly note the skip in the output.

- **Problem.** What problem does this solve? For whom? What happens today without it? Why now?
- **Users and roles.** Who interacts with this? What are their goals? Do different roles see different behavior?
- **Inputs and triggers.** What initiates this feature? Manual action, scheduled job, system event, external webhook? What inputs does it accept and where do they come from?
- **Outputs and side effects.** What does the system produce? Where does it go? What state changes? What's visible to whom?
- **Success.** How will the user know this works? What measurable outcome means "shipped successfully"?
- **Failure.** What does failure look like? What's a tolerable failure mode vs. an unacceptable one? What must never happen?
- **Edge cases the user already knows about.** Empty inputs, large inputs, concurrent users, partial completion, retries, timezone/locale, permissions edge cases.
- **Constraints.** Must-have, must-not-have, strong preferences. Performance budgets, deadlines, regulatory constraints, integration constraints.
- **Out of scope.** What is *not* this feature? Nearby features it will be confused with.
- **Stakeholder alignment.** Who has signed off, who hasn't been consulted, where are unresolved disagreements.
- **Existing systems and constraints from the codebase.** What the user already knows about the relevant code (does not replace `/research-start`, but captures the user's prior knowledge).

If the user knows of more branches relevant to this specific feature (e.g., legal review, third-party integrations, cost), add them.

## 5. Output Document Structure

Write the artifact to `SDD/research/CLARIFICATION-[###]-[feature-name].md`:

```markdown
# CLARIFICATION-[###]-[feature-name]

## Metadata
- **Date:** [YYYY-MM-DD]
- **Interviewer:** Claude (Opus)
- **Interviewee:** [user, if known]
- **Status:** Draft / Resolved / Partially Resolved

## Clarified Problem Statement
[One paragraph the user has confirmed. Plain language. No solutioning.]

## Users and Goals
- **[Role]:** [Goal in their words]
- **[Role]:** [Goal in their words]

## Inputs and Triggers
[How the feature is initiated and what inputs it accepts.]

## Outputs and Effects
[What the feature produces, what changes, what becomes visible.]

## Success Criteria (User's Words)
- [Outcome 1]
- [Outcome 2]

## Failure Boundaries
- **Tolerable failures:** [user-confirmed]
- **Unacceptable failures:** [user-confirmed]

## Edge Cases the User Already Knows About
- [Case]: [expected behavior]
- [Case]: [expected behavior]

## Constraints
- **Must have:** [...]
- **Must not have:** [...]
- **Strong preferences:** [...]

## Out of Scope
- [...]

## Stakeholders
- **[Stakeholder]:** [aligned / unconsulted / unresolved disagreement]

## Branches Walked
[For each branch from §4, summarize what was asked and what was resolved. One line per resolved decision.]

## Open Questions (Still Ambiguous)
[Questions the user could not resolve in this session. Each item is a branch the design concept does not yet cover. These will be inherited as risk by `/research-start`.]
- [Question]: [why it's still open — needs research, needs stakeholder input, deferred deliberately, etc.]

## Notes for /research-start
- **Glossary candidates:** [Domain terms the user used that should be considered for `SDD/UBIQUITOUS_LANGUAGE.md`]
- **Codebase areas the user named:** [files/modules/services to investigate first]
- **Stakeholder perspectives the user wants captured:** [roles to elaborate during research]
```

## 6. Iteration

If the user wants to refine the clarification later (often after sleeping on it), this command can be re-invoked. On re-invocation:

- Read the existing `CLARIFICATION-[###]-[feature-name].md`.
- Resume from "Open Questions" or any section the user wants to revisit.
- Update sections in place; do not delete prior decisions without explicit user confirmation.
- Update **Status** field accordingly (Draft → Partially Resolved → Resolved).

## 7. Handoff to /research-start

After the artifact is written, surface to the user:

- The count of resolved decisions (branches walked).
- The count of open questions (ambiguity inherited downstream).
- A clear next-step recommendation:
  - **Resolved**: ready for `/research-start`.
  - **Partially Resolved**: proceed to `/research-start` with explicit acknowledgement that the open questions become research risks. `/critical-review` at end of research will check whether research closed them.
  - **Draft**: the design concept is too fuzzy — recommend continuing to grill before research.

`/research-start` should explicitly load this CLARIFICATION document as input alongside the user's verbal/written prompt.

## 8. What This Is Not

- **Not codebase research.** Do not browse, grep, or read project files during clarification. The user's design concept lives in their head, not the code. `/research-start` does the codebase work.
- **Not a spec.** Do not produce REQ-XXX, EDGE-XXX, or technical decisions. Those belong in `SPEC-[###]`.
- **Not a plan.** Do not propose architecture, libraries, or modules. The point is to extract intent, not commit to a solution shape.

## 9. Begin

Begin clarification now. Open with: "Before I research the codebase, I'd like to interview you about the feature itself — what you want, for whom, under what constraints, and where you're not sure yet. I'll capture this in a CLARIFICATION document. Ready?"

Then walk the branches in §4, one question at a time, until the design concept is externalized.
