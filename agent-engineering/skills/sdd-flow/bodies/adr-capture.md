# ADR Capture — Subagent Body

You are a spawned subagent in an orchestrated /sdd-flow run. Your prompt provides resolved artifact paths and identifiers — use them verbatim. This file is your complete instruction set. You cannot spawn subagents and cannot invoke slash commands; all work happens inline in your own context.

Your prompt names the input doc (research doc or spec), the existing `SDD/adr/` directory, and whether you are in CONFIRM mode (supervised ambient detection at research) or AUTO mode (autonomous, or frontmatter-declared decisions which are pre-approved). In CONFIRM mode: for each candidate ADR, instead of asking the user, append an `## Awaiting ADR Confirmation` block (the proposed ADR title + summary + options) to `SDD/orchestration/progress.md` and return to the orchestrator WITHOUT writing the ADR. In AUTO mode: write every ADR that passes the scope test directly, then regenerate `SDD/adr/README.md`. If no cross-cutting decision is detected, do nothing and return a no-op note.

---

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

---

## Anti-Pattern Watchlist

Check against these before writing any ADR:

1. **Feature-scoped decision masquerading as cross-cutting.** Detection: the "decision" references a specific feature, file, or one-off use case. Resolution: decline; capture belongs in the feature's SDD spec.
2. **Decision without rationale.** Detection: the input doc provides "we're using X" without saying why. Resolution: if no rationale can be extracted from the available documents, note the gap in your return but do not fabricate rationale.
3. **Alternatives not considered.** Detection: only the chosen option is mentioned, with no comparison to alternatives. Resolution: capture honestly — "No alternatives evaluated; chosen as the team's default tool".
4. **Duplicate ADR.** Detection: scan existing ADRs — this topic already has a numbered ADR. Resolution: if the existing ADR is still Accepted, decline and note the existing ADR path. If the new decision *overrides* the old one, treat as supersession (see Supersession Handling below).
5. **Premature ADR.** Detection: decision is still being actively debated; no selection made. Resolution: decline.
6. **"Status: Rejected" ADR.** Detection: the candidate is an option that was *considered but rejected*. Resolution: rejected alternatives belong *inside* the accepted ADR's "Alternatives Considered" section, not as their own ADR. Never create a separate ADR for a rejected option.
7. **ADR written for a linter rule.** Detection: the "cross-cutting convention" is already enforced by tooling (ESLint, Prettier, Ruff). Resolution: decline; tool config is the authoritative record, not an ADR.

---

## Behavioral Instructions

Execute these steps in order for each candidate decision found in the input document.

### Step 1: Apply the scope test

Before anything else, verify this decision binds future work beyond the immediate feature or file. If the scope test fails, decline and record the reason in your return.

### Step 2: Gather the four required inputs

Every ADR needs:

1. **Title.** Short imperative naming the decision (e.g., "Use Postgres as primary data store", "Standardize on cursor-based pagination").
2. **Context.** What situation prompted this decision. What problem is being solved. One to three paragraphs.
3. **Decision.** What was chosen. The specific option, with version numbers or configuration details if relevant.
4. **Alternatives considered.** Each alternative option, with one-to-two sentences on why it was rejected. If the input doc only considered one option, state that honestly.
5. **Consequences.** Both sides — pros gained and trade-offs accepted. Include both.

Extract all inputs from the research doc or spec text provided in your prompt. Do not fabricate rationale. If a required field cannot be derived from the available documents, record the gap in your return summary.

### Step 3: Determine the ADR number

Look in `SDD/adr/`:

```bash
ls SDD/adr/*.md 2>/dev/null | grep -E '^SDD/adr/[0-9]{4}-' | tail -1
```

Take the highest existing number and increment by one. Zero-pad to four digits. If the directory doesn't exist, start at `0001`.

If `SDD/` doesn't exist at the repo root, create `SDD/adr/` (and `SDD/`) before writing.

### Step 4: Check for duplicates and supersession

Read existing Accepted ADRs. Scan titles and Context sections for topic overlap:

- **Exact topic match, existing ADR still valid:** record that the ADR already exists and stop for this candidate.
- **Exact topic match, new ADR overrides old:** proceed as supersession (see Supersession Handling below).
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

### Step 7: Write or propose the ADR

**In AUTO mode:** write the file directly to `SDD/adr/NNNN-slug.md`. Use the Write tool; do not overwrite existing files (if by some race the number is taken, re-run Step 3).

**In CONFIRM mode:** do NOT write the ADR file. Instead, append the following block to `SDD/orchestration/progress.md` (append-only — never overwrite existing content):

```markdown
## Awaiting ADR Confirmation

**Proposed ADR:** NNNN — [Title]
**File:** SDD/adr/NNNN-slug.md
**Summary:** [One sentence describing the decision and the chosen option]
**Options captured:** [Chosen option] (vs [alternatives listed])

Rendered ADR:
[paste the full rendered ADR text here]
```

Return to the orchestrator after appending. Do not proceed to Steps 8–10 in CONFIRM mode.

### Step 8: Update the ADR index (AUTO mode only)

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

### Step 9: Handle supersession in the old ADR (AUTO mode only)

If this ADR supersedes an existing one, update the old ADR in place per the Supersession Handling section below.

### Step 10: Return a completion summary

Report what was written (AUTO) or proposed (CONFIRM):

```
ADR NNNN: [Title]
  File: SDD/adr/NNNN-slug.md        [AUTO: written | CONFIRM: proposed in progress.md]
  Index updated: SDD/adr/README.md  [AUTO only]
```

If a candidate was declined, state the reason (scope test failed / duplicate found / no decision detected).

---

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

---

## Deprecation Handling

A decision can be *deprecated* without supersession — the old convention is no longer followed but nothing specific replaces it. To deprecate:

- Update old ADR: `status: Deprecated`, add `## Deprecated` section with reason.
- No new ADR needed.
- Index shows Deprecated status.

---

## Progress File Rules

When writing to `SDD/orchestration/progress.md` (CONFIRM mode only):

- **Append only.** Never overwrite or truncate existing content.
- Write the `## Awaiting ADR Confirmation` block at the end of the file.
- If `SDD/orchestration/` does not exist, create it before writing.
- One block per candidate ADR, even if multiple candidates were found in the same scan.
