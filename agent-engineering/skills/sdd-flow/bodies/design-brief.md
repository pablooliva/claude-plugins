# Write the Design Brief

You are a spawned subagent in an orchestrated /sdd-flow run. Your prompt provides resolved artifact paths and identifiers — use them verbatim. This file is your complete instruction set. Do not spawn subagents or invoke slash commands/skills, even if an Agent/Task tool is available — the flow’s flat-orchestration contract forbids it; all work happens inline in your own context.

## Purpose

The design brief is the one planning document written for the human. They will read it, answer its questions, and approve it; the specification is then held to it. Nothing else in planning is read by a person. Write for someone who knows the product and has not read the research.

## Inputs

1. `SDD/research/RESEARCH-[###]-[feature-name].md` — read in full. On a next-tier cycle your prompt also names the previous tier's research document; read the sections this one points to.
2. `SDD/research/CLARIFICATION-[###]-[feature-name].md` if present — its constraints and out-of-scope list bind you.
3. `SDD/UBIQUITOUS_LANGUAGE.md` if present — use its names exactly.
4. Accepted ADRs under `SDD/adr/` that the research cites — binding; cite them where they settle a decision.
5. **TIERS** — the tier standard, at the path in your prompt. Read it before writing; it defines the tiers, the floor, the cut tests, and the tier plan's shape.
6. **TIER_PLAN** — the tier plan, at the path in your prompt (`SDD/flow/TIERS-[feature-name].md`). If the file exists, this is a later-tier cycle: its Deferred table and Feedback notes are your starting point.
7. **Revision runs:** inputs 1–6 again, plus the existing brief and the user's reply (verbatim in your prompt). On a re-plan, also the rolling ledger and the triggering retrospective.

## Rules

1. **Length.** At most 150 lines; aim for under 100. If the feature cannot be described within the cap, do not compress: write `Too large for one brief — recommend decomposition` as the first line under the title, say where the seams are, and stop.
2. **Plain language.** No requirement IDs, no code, no function signatures. Define a project-specific term in a clause the first time it appears.
3. **Decide or ask.** If the research settles something, decide it and record the rejected alternative. Ask the human only where the answer turns on preference, product behaviour, risk appetite, or a trade-off the codebase gives no evidence for.
4. **Questions.** At most five. Each has concrete options and a recommended answer with its reason. Every question must be answered before the brief can be approved, so ask only what is worth stopping for; anything else is a decision you make and record.
5. **Clarification conflicts.** If what the research supports conflicts with a constraint in the clarification document, do not resolve it yourself — raise it as a question.
6. **Footprint honesty.** List every area you expect to change in "What changes where", including tests, migrations, and configuration. Name each area as a path or path prefix wherever you can — every later code review compares the changed files against this table, and an area left out here and changed later is reported to the human as a surprise.
7. **Least sure about** is never empty. Name the assumption you would check first if this design failed.
8. **Tier it.** Apply the cut tests in TIERS to everything the research suggests building. Describe Tier 1 as the recommended tier unless your prompt names another (`TIER: N`). Keep the sketches of the tiers above the recommended one to ten lines each — their own cycle will re-decide them — and describe them as behaviour only: what the feature would do, never the modules or interfaces it would use. Nothing the floor protects may be deferred. Build nothing ahead (TIERS, Tenet 2): the design for the recommended tier contains no part that exists for a later tier, and no Key decision may give a later tier's needs as its reason except to break a tie between options of equal simplicity. Take the simplest option even when reversing it later will be expensive, and say so under that decision's "If this is wrong". If the feature is too small to tier, write `Tiers: not applicable — [reason]` as the whole of the `## Tiers` section and write no tier plan.
9. **Later-tier cycles.** Open the brief with `## What we learned from Tier N`, from the tier plan's Feedback notes and the clarification document, and say which sketched or deferred items you kept, changed, or dropped. Everything else in the brief describes only what this tier adds.
10. **Write the tier plan** at TIER_PLAN in the shape TIERS gives. On a first-tier cycle create it: the status table, `## Tier 1`, the Deferred table (one `DEFER-XXX` row per deferred behaviour, `Came from` = `proposal`), Removed, the sketches, and an empty Feedback section. On a later-tier cycle update it: this tier's row becomes `in progress`, its sketch is replaced by what it will do, rows this tier takes up leave the Deferred table, and the remaining rows and sketches are re-decided. Keep the status table exactly as TIERS shapes it — four columns, one row per tier, each row's first cell starting with the tier's number — because a script reads it to mirror the tiers to tasks. Leave the `Task` column as it is: that script fills it. Never delete Feedback notes.

## Template

```markdown
---
revision: 1
---

# DESIGN-[###]-[feature-name]

Based on: RESEARCH-[###]-[feature-name].md

## In one paragraph
[The whole feature, conceptually. Five sentences at most.]

## What you will be able to do afterwards
- [Observable outcome]

## How it works today
[The relevant current behaviour, ten lines at most, with a few `file:line` references.]

## How it will work
[The main scenario, step by step, in the order things happen.]

## Key decisions
### D1: [title]
- **Chosen:** [option]
- **Instead of:** [the alternative rejected]
- **Why:** [the evidence, citing research or an ADR]
- **If this is wrong:** [cheap | moderate | expensive to reverse — and what reversing involves]

## What changes where
| Area (path or path prefix) | New or changed | Size (S/M/L) | What changes |
|---|---|---|---|

## Tiers
**Recommended: Tier 1.**
- **Tier 1 — POC-plus:** [what it does; what it deliberately leaves out; how the left-out cases fail]
- **Tier 2 — Standard (sketch):** [what it would do in addition — behaviour only]
- **Tier 3 — Full (sketch):** [what it would do in addition — behaviour only]

## Delivery outline (Tier [N])
1. [Slice name] — after this you can [observable thing].

## Not doing
- [Excluded for good — not deferred to a later tier — and, where useful, why]

## Questions for you
### Q1: [question]
- **Options:** (a) … (b) …
- **Recommended:** (a) — [reason]

## Least sure about
- [Assumption, and how it would show up if false]
```

Write `## Questions for you` with the single line `None.` when there are none.

## Revision runs

1. Apply the user's answers and change requests. Move each answered question out of `## Questions for you` and into the brief proper (as a decision, a scope line, or a changed section). "Use your recommendation" is an answer to the question it was given for, and to no other.
2. A reply that names a different tier (`tier 2`, `tier 3`) is a change request: rewrite the delivery outline, the footprint, and the decisions for that tier, change the `Recommended:` line to it, and bring the tier plan in step.
3. Append to `## Answers and changes` (create it as the last section if absent): the revision number, the user's reply quoted verbatim, and what you changed in response.
4. Increment `revision:`. Do not record approval anywhere in the brief — approval state lives in `progress.md`.
5. If the user's reply shows the research is wrong on a point of fact, correct the research document as well and say so in your return.
6. On a re-plan, add `## What changed since revision N` directly under the title: what the ledger and retrospective showed, and which decisions or outline entries changed.

## Progress and return

Append to `SDD/orchestration/progress.md` (≤10 lines): the header `## Design Brief - Drafted (revision N)` exactly — it is a phase-detection marker — then the brief's path, its line count, the recommended tier (`1`, `2`, `3`, or `none` when tiers are not applicable), the number of decisions, and the number of open questions.

Return ≤200 words: the brief's path, the tier plan's path (or "no tier plan"), the one-paragraph summary, the decision titles, and the questions.
