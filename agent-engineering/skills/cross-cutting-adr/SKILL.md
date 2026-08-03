---
name: cross-cutting-adr
description: "INVOKE THIS SKILL when a cross-cutting architectural decision is being made — a technology choice, convention, or pattern that will bind future features or be inherited across the system (e.g., 'we'll use Postgres for all services', 'standardizing on async/await', 'going with n8n for orchestration'). Also invoke when a comparison-with-selection pattern appears in research or conversation ('considered X vs Y vs Z, picking X because...'). Captures the decision as a numbered Architecture Decision Record (ADR) under SDD/adr/, including chosen option, alternatives considered, rationale, and consequences. Handles supersession when a new ADR replaces an old one. Skip for feature-scoped implementation details — those belong in the feature's SDD spec, not an ADR."
---

# Cross-Cutting ADR

Captures cross-cutting architectural decisions as numbered Architecture Decision Records (ADRs) under `SDD/adr/`. Solves the "where did we decide this?" problem that emerges after dozens of feature specs accumulate — ADRs provide an indexed, long-lived home for decisions that bind future work.

## What Counts as Cross-Cutting

The **scope test** — apply before any ADR is written:

> *Will this choice bind future features, or be inherited by other parts of the system?*

If **yes** → ADR-worthy.
If **no** → it's a feature-scoped choice; it belongs in the feature's SDD spec, not an ADR. Decline capture.

### Examples that ARE cross-cutting (capture)

- Choosing an orchestration engine (n8n vs Airflow vs Prefect) that multiple features will use.
- Picking a primary database (Postgres vs MongoDB) for the whole system.
- Selecting a vector store (pgvector vs Qdrant vs Weaviate) that all RAG features will share.
- Standardizing on a convention (`async/await` over `.then()` chains, structured JSON logging, cursor-based pagination).
- Committing to a specific LLM SDK (Anthropic SDK vs LangChain) across services.
- Adopting a deployment pattern (blue/green vs rolling) for all services.

### Examples that are NOT cross-cutting (decline)

- Picking a regex vs string split inside one function.
- Choosing folder structure within a single feature.
- Deciding on a variable name convention for one module.
- Selecting a particular HTTP status code for one endpoint.
- Choosing between two libraries for a one-off utility.

## Expert Vocabulary

Architecture Decision Record (ADR). Cross-cutting concern. Binding decision. Supersession (decisions replacing prior decisions). Accepted / Deprecated / Superseded status. Context / Decision / Consequences structure. Trade-off analysis. Technology selection rationale. Architectural inheritance. Decision log. Numbered ADR (Michael Nygard format). Decision freshness. Alternatives considered.

## Anti-Pattern Watchlist

Check against these before writing any ADR:

1. **Feature-scoped decision masquerading as cross-cutting.** Detection: the "decision" references a specific feature, file, or one-off use case. Resolution: decline; capture belongs in the feature's SDD spec.
2. **Decision without rationale.** Detection: user provides "we're using X" without saying why. Resolution: ask *why* — if the user can't articulate it, the decision isn't durable enough to codify yet.
3. **Alternatives not considered.** Detection: only the chosen option is mentioned, with no comparison to alternatives. Resolution: ask what other options were looked at and why they were rejected. If truly no alternatives were considered, capture that honestly — "No alternatives evaluated; chosen as the team's default tool".
4. **Duplicate ADR.** Detection: scan existing ADRs — this topic already has a numbered ADR. Resolution: if the existing ADR is still Accepted, decline and point to it. If the new decision *overrides* the old one, treat as supersession (see Section 6).
5. **Premature ADR.** Detection: decision is still being actively debated; no selection made. Resolution: decline until the decision has actually been made.
6. **"Status: Rejected" ADR.** Detection: user wants to capture an option that was *considered but rejected*. Resolution: rejected alternatives belong *inside* the accepted ADR's "Alternatives Considered" section, not as their own ADR. Never create a separate ADR for a rejected option.
7. **ADR written for a linter rule.** Detection: the "cross-cutting convention" is already enforced by tooling (ESLint, Prettier, Ruff). Resolution: decline; tool config is the authoritative record, not an ADR.

## When to Activate

Activate on any of these trigger patterns:

### Trigger A: Explicit manual invocation

User runs `/adr-capture` or says "capture this as an ADR", "write an ADR for this", "document this decision". Skip all ambient detection; proceed to capture.

### Trigger B: Comparison-with-selection pattern

Conversation or a document contains BOTH:
- **Comparison language:** "considered X, Y, and Z", "compared A vs B", "evaluated options", "pros and cons of...", "looked at alternatives".
- **Selection language:** "picking X", "going with Y", "decided on Z", "chose X over Y because...".

AND at least one cross-cutting scope signal (see Trigger D).

### Trigger C: sdd-flow research/planning hand-off

During sdd-flow:
- **Research phase completion:** scan the research doc for comparison-with-selection patterns that also carry cross-cutting scope.
- **Planning phase:** read spec frontmatter for a `cross_cutting_decisions:` list. Each entry is a topic label (e.g., `orchestration_engine`). For each label, extract details from the research doc or spec text.

### Trigger D: Cross-cutting scope language

Even without comparison, activate when the user asserts a system-wide convention:
- "across services", "all features", "system-wide", "platform-wide", "as the standard", "our default for X".
- "we'll use X for all...", "standardizing on X", "every service will...", "adopt X as the default".

Pair this with decision language ("use", "go with", "adopt", "standardize on") to reduce false positives.

## When NOT to Activate

- **Pure exploration.** User is brainstorming without having made a decision yet.
- **Preference statements without scope.** "I like TypeScript" is not a cross-cutting ADR — it's a preference. Needs explicit scope signal to activate.
- **Feature-scoped decisions.** Applies Scope Test; if fails, decline.
- **Ambient detection with only one signal.** If only comparison language is present but no selection, or only scope language but no decision, do NOT activate. Require two signals.
- **Already-captured decision.** If the topic is already covered by an existing Accepted ADR and the user is not overriding it, do not re-capture.

## Activation Behavior by Trigger

Behavior differs by trigger source to respect automation vs. confirmation boundaries:

- **Trigger A (manual):** proceed to capture without additional confirmation — user already chose to invoke.
- **Trigger B (ambient comparison+scope in conversation):** show the proposed ADR to the user and ask `Capture as ADR? (y/N)`. Default no. False positives here are likely; require explicit confirmation.
- **Trigger C (sdd-flow, comparison detected in research):** show the proposed ADR to the user at end of research phase and ask for confirmation. Do not silently commit — the user should see what's being captured.
- **Trigger C (sdd-flow, listed in spec frontmatter):** assume pre-approved. The spec explicitly declared the decision should be captured. Proceed without extra confirmation.
- **Trigger D (ambient scope language):** same as Trigger B — confirm before writing.

## Behavioral Instructions

Execute these steps in order.

### Step 1: Apply the scope test

Before anything else, verify this decision binds future work beyond the immediate feature or file. If the scope test fails, decline and explain.

### Step 2: Gather the four required inputs

Every ADR needs:

1. **Title.** Short imperative naming the decision (e.g., "Use Postgres as primary data store", "Standardize on cursor-based pagination").
2. **Context.** What situation prompted this decision. What problem is being solved. One to three paragraphs.
3. **Decision.** What was chosen. The specific option, with version numbers or configuration details if relevant.
4. **Alternatives considered.** Each alternative option, with one-to-two sentences on why it was rejected. If the user only considered one option, state that honestly.
5. **Consequences.** Both sides — pros gained and trade-offs accepted. Include both.

If any of these are missing from the available context (conversation, research doc, spec), ask the user. Do not fabricate rationale.

### Step 3: Determine the ADR number

**First, check for a reservation.** If a `WORKTREE.md` at the repo root carries an `SDD numbers reserved:` line (written by the `worktree-create` skill), you are inside an isolated worktree and that number was already reserved against every sibling worktree and branch:

```bash
grep 'SDD numbers reserved' WORKTREE.md 2>/dev/null   # e.g. "ADR-0011, SPEC-045"
```

Use the reserved `ADR-NNNN` for the first ADR written here, incrementing locally for any further ones. Do **not** recompute from the local `SDD/adr/` listing — a worktree checks out from a commit, so that listing cannot see numbers already claimed by uncommitted work in sibling worktrees or by unmerged branches, and duplicate numbers merge back with no git conflict.

Otherwise (no reservation — the main repo, or a worktree not created by that skill), look in `SDD/adr/`:

```bash
ls SDD/adr/*.md 2>/dev/null | grep -E '^SDD/adr/[0-9]{4}-' | tail -1
```

Take the highest existing number and increment by one. Zero-pad to four digits. If the directory doesn't exist, start at `0001`.

If `SDD/` doesn't exist at the repo root, create `SDD/adr/` (and `SDD/`) before writing.

### Step 4: Check for duplicates and supersession

Read existing Accepted ADRs. Scan titles and Context sections for topic overlap:

- **Exact topic match, existing ADR still valid:** tell the user the ADR already exists, point to it, and stop.
- **Exact topic match, new ADR overrides old:** proceed as supersession (Section 6).
- **Related but distinct topic:** proceed normally, add a cross-reference ("See also: ADR NNNN") in the new ADR's Context section.

### Step 5: Generate the slug

Kebab-case, short, includes the chosen option when possible:

- Good: `0003-postgres-over-mongodb.md`, `0007-n8n-for-orchestration.md`, `0012-cursor-pagination.md`.
- Avoid: `0003-database.md`, `0007-orchestration-decision.md` — too vague.

### Step 6: Render the ADR

Use this template exactly:

```markdown
---
adr: NNNN
title: [Imperative decision title]
status: Accepted
date: YYYY-MM-DD
supersedes: null
superseded_by: null
tags: [cross-cutting, <domain>]
---

# ADR NNNN: [Title]

## Status

Accepted (YYYY-MM-DD)

## Context

[1-3 paragraphs. What situation prompted this decision? What problem needs solving? What constraints apply? Include enough so a reader six months from now can understand why this was up for decision.]

## Decision

[The chosen option, stated clearly. Include version numbers, configuration details, or scope boundaries if relevant.]

## Alternatives Considered

### [Option A — the chosen one]

[One paragraph on why this was chosen.]

### [Option B]

Rejected because: [specific reason — performance, licensing, maturity, team familiarity, etc.]

### [Option C]

Rejected because: [...]

[If truly no alternatives were considered:]

### No alternatives evaluated

Chosen as the team's default tool because [reason]. Future ADR should revisit if [trigger condition].

## Consequences

### Positive

- [Benefit gained by this decision]
- [...]

### Negative / Trade-offs accepted

- [Cost or limitation accepted]
- [...]

### Neutral observations

- [Other relevant effects]

## References

- [Linked SDD spec if applicable: SDD/requirements/SPEC-NNN-xxx.md]
- [Linked research doc: SDD/research/RESEARCH-NNN-xxx.md]
- [External docs, benchmarks, vendor pages]
```

### Step 7: Confirm with the user (unless pre-approved per trigger type)

Show the rendered ADR and ask:

> Capture this as `SDD/adr/NNNN-slug.md`? (y/N)

Default no. User may edit phrasing before confirming.

### Step 8: Write the file

On confirmation, write to `SDD/adr/NNNN-slug.md`. Use Write tool; do not overwrite existing files (if by some race the number is taken, re-run Step 3).

### Step 9: Update the ADR index

Regenerate `SDD/adr/README.md`:

```markdown
# Architecture Decision Records

Cross-cutting architectural decisions for this system. Each ADR captures a choice that binds future work.

## Conventions

- ADRs are numbered sequentially (0001, 0002, ...).
- Status lifecycle: **Accepted** → **Deprecated** (no longer followed but not replaced) or **Superseded** (replaced by a newer ADR).
- Superseded ADRs remain in this directory with updated status and a reference to the superseding ADR. They are never deleted.

## Index

| # | Title | Status | Date | Topic |
|---|-------|--------|------|-------|
| [NNNN](NNNN-slug.md) | [Title] | Accepted | YYYY-MM-DD | [Domain tag] |
| [...] | [...] | Superseded by 0007 | YYYY-MM-DD | [...] |
```

Sort the index by ADR number, ascending. Include all ADRs regardless of status. For Superseded entries, show "Superseded by NNNN".

### Step 10: Close the loop

Confirm what was written:

```
✓ Captured ADR NNNN: [Title]
  File: SDD/adr/NNNN-slug.md
  Index updated: SDD/adr/README.md
```

If this was a supersession, also confirm the prior ADR was updated:

```
  Prior ADR NNNN-old marked Superseded by NNNN.
```

## Supersession Handling

When a new decision replaces an old one:

### In the new ADR

- `supersedes: NNNN-old` in frontmatter.
- Context section references the prior ADR: "Supersedes ADR NNNN ([prior title]). See that ADR for the original rationale."

### In the old ADR

Update in place — do not delete:

- `status: Superseded` (change from Accepted).
- `superseded_by: NNNN-new` in frontmatter.
- Add a `## Superseded` section near the top:

```markdown
## Superseded

This ADR was superseded by [ADR NNNN](NNNN-new-slug.md) on YYYY-MM-DD.

Reason for supersession: [one sentence — e.g., "Migrated from MongoDB to Postgres after scaling benchmarks showed Postgres better fit the workload"].

The original decision below is preserved for historical context.
```

Leave all other content of the old ADR intact. Future readers can still see why the original choice was made.

## Deprecation Handling

A decision can be *deprecated* without supersession — the old convention is no longer followed but nothing specific replaces it. To deprecate:

- Update old ADR: `status: Deprecated`, add `## Deprecated` section with reason.
- No new ADR needed.
- Index shows Deprecated status.

## Integration with sdd-flow

sdd-flow can invoke this skill at two phase boundaries:

### Research completion

sdd-flow scans the research doc for comparison-with-selection patterns with cross-cutting scope. For each match, invoke this skill to propose an ADR. User confirms per-ADR before writing.

### Planning completion

sdd-flow reads spec frontmatter for `cross_cutting_decisions:`:

```yaml
---
cross_cutting_decisions:
  - orchestration_engine
  - vector_store
---
```

For each listed topic label, invoke this skill. The skill should extract details from the research doc or spec text. If insufficient context, the skill asks the user. In automated sdd-flow runs, frontmatter-declared decisions are assumed pre-approved (the spec explicitly called them out).

## Examples

### GOOD — Comparison with selection (ambient trigger)

**User:** "I've been comparing n8n, Airflow, and Prefect for orchestrating our data pipelines across Currents and Beyond the Mark. Going with n8n because it has the best self-hosted story, visual editor helps with cross-project debugging, and the node ecosystem covers our external service integrations. Prefect was too Python-centric for our mixed-tooling setup, and Airflow's DAG-per-file model doesn't fit our lightweight flows."

**Skill activation:** Triggers B (comparison+selection) AND D (cross-cutting scope: "across Currents and Beyond the Mark"). Propose ADR 0001 titled "Use n8n for cross-project orchestration" with Context, Decision, Alternatives (Airflow and Prefect with given rejection reasons), Consequences. Confirm before writing.

### GOOD — Manual invocation

**User:** "/adr-capture — we're standardizing on pgvector for all RAG features instead of a separate vector database."

**Skill activation:** Trigger A. Ask user for Context (why this shift?), Alternatives (what was considered and rejected?), and Consequences. Write ADR on user confirmation.

### BAD — Feature-scoped decision (decline)

**User:** "For the rate-limiting feature, I'll use Redis for the token bucket store."

**Skill response:** Decline. "This reads as a feature-scoped decision, not cross-cutting. It belongs in the rate-limiting feature's SDD spec, not an ADR. If Redis becomes the standard store for multiple features' state, that would warrant an ADR — let me know if that's the broader decision."

### BAD — Preference without scope (decline)

**User:** "I prefer pytest over unittest."

**Skill response:** Decline unless user adds scope. "Is this a preference for this session, or are you committing to pytest as the standard for all new test code in this project? If the latter, we can capture it as an ADR."

### Supersession example

**User:** "We're migrating from MongoDB to Postgres. ADR 0003 said Mongo was our primary store."

**Skill action:** Propose new ADR 0012 "Migrate primary data store from MongoDB to Postgres" with `supersedes: 0003`. After user confirms, update ADR 0003's status to Superseded with a back-reference to 0012.

## Questions This Skill Answers

- "Write an ADR for this decision."
- "Capture this architectural choice."
- "Document the reasoning behind picking X over Y."
- "Where do we record this kind of decision?"
- "This is a cross-cutting decision — save it."
- "Supersede the old ADR with this new choice."
- "Mark that decision as deprecated."
- "I've decided on X for all services — capture that."
- "We compared A, B, C; going with A."

## Scope Boundary

This skill writes to **`SDD/adr/`** at the repo root. It does not write to `docs/adr/` or any alternative location. If the repo structure is unusual (e.g., monorepo with per-package SDD directories), the user should invoke from the appropriate working directory so the repo-root resolution lands in the right place.

This skill does not handle *decision audits* (checking whether the project still follows its own ADRs) — that's a separate concern. It captures decisions; enforcement is out of scope.

This skill does not write to external systems (Vikunja, Asana, Notion). ADRs live in the repo alongside the code they govern.
