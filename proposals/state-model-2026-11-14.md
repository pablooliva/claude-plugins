# State model — the states a feature allows, approved in the brief and checked in the code (2026-11-14)

**Status:** Tier 1 built as agent-engineering 5.1.0 (2026-11-14), build order steps 1–7. Not yet trialled (step 8). The workflow diagram (Open) and `sdd-lite` were not built.

**Kill test (step 1), 2026-11-14: passed.** State bugs found in the owner's applications: `currents` 62981f42 — a re-fetch moved triaged items `analyzed` → `completed`, they were re-selected, the insert failed, and the batch stranded them forever (18 aborts a day in production); `currents` 9352dded — items of a disabled source stayed `pending` with nothing able to move them; `Boycott.search` dc0976b — a re-crawl left the earlier document active, with no move to retire it (34% of the index).
**Affects:** `agent-engineering` — `sdd-flow` only (brief, spec, implementer, the three reviews, the final report).

## Why

Step 5 of the post this came from ("review evidence of behavior": screenshots, videos, **state diagrams** — see
`https://x.com/TheTuringPost/status/2120607968408531110`) is only partly covered by sdd-flow. A convincing
explanation of a change says "this now works"; a state diagram shows every path a thing can take, so a missing
or extra one is visible at a glance. The paths that must never happen — a shipped order cancelled, a paid
invoice paid again — are where the bugs are, and an explanation never mentions them.

Today nothing in the flow names a feature's states. The closest check is the tracing gate's planned call graph,
which compares which functions ran, not which states the feature can reach.

**Evidence that this is worth building: none yet.** Before step 1 of the build, look through past cycles' review
findings and reverts in the owner's applications for state bugs (a wrong status change, a transition allowed that
should not be, a state no code leaves). If there are none, stop here. `/worth-building` on this file asks the
same question.

## Decided (owner, 2026-11-14)

1. **No on/off gate.** Unlike `tracing` and `evals`, a state model needs nothing installed in the application, so
   it is not decided at 3c and gets no field on the `## Gates -` line. Whether a feature has one is decided by
   the brief (below).
2. **Mermaid in the brief.** The intended diagram is a Mermaid `stateDiagram-v2` block (a text format that
   renders as a picture in bb and on GitHub), not a list of transitions.

## The design

### When it applies

A feature has a state model when something it adds or changes **moves through named states over time** — a
status column, a lifecycle, a job that queues, runs, retries and fails, an approval that waits. The brief decides:
it either draws the diagram or writes `State model: not applicable — [reason]`, the same way it handles tiers.
A brief that says "not applicable" for a feature that plainly has states is a finding in the spec critical
review (3d). A calculation, a single call, a page with no lifecycle: not applicable.

### One definition file

`skills/sdd-flow/references/state-model.md` — the one definition, read by path, never restated in a body
(as with `tracing-lens.md`). It holds:

- §1 what a state model is, and when a feature has one;
- §2 how the diagram is drawn: every state, every allowed transition labelled with the event that causes it,
  and the **forbidden transitions** — listed under the diagram, one line each, because a diagram cannot show an
  arrow that must not exist;
- §3 how the spec maps them: each allowed transition to a requirement, each forbidden one to an edge case;
- §4 what the implementer tests;
- §5 how a review reads the as-built model from the code and compares it (the State Check);
- §6 grading and how a finding is resolved.

### Where it lives, step by step

| Step | What happens | Who sees it |
|---|---|---|
| 2.5 design brief | Draws the intended diagram and the forbidden list under `## How it will work`, or writes `not applicable` | **The owner, at the existing design gate** |
| 3a spec | `### State model` under `## Modules`: the brief's diagram copied, each allowed transition with its REQ, each forbidden one with its EDGE | — |
| 3d spec critical review | The Design Brief Fidelity block checks the spec's model is the brief's; every transition has a requirement; every forbidden one has an edge case | — |
| 4a implementer | One test per allowed transition; one per forbidden transition proving it is rejected (held to `test-integrity.md` §1 like any test) | — |
| 4b slice review, code review | The State Check: read the code, write the as-built diagram into the review, compare | — |
| 4e.5 final check | The State Check over the whole feature | — |
| 4j final report | One line: `State model: matched` or the deviations recorded | **The owner, after the commit** |

No new stop. The design gate already asks the owner to approve how the feature will behave, and the intended
states are part of that. Comparing the as-built model with the intended one is a correctness check, not an owner
decision; an unresolved finding stops the flow through the existing fix loop, as every other finding does.

In per-slice mode each slice's spec entry names the transitions it brings into existence (as `Traced nodes:` does
for tracing). A slice review checks that slice's transitions **and every earlier slice's**, as the Tracing Lens
checks earlier slices' nodes (`references/tracing-lens.md` §2), so a later slice that breaks an earlier
transition is caught at its own review, not only at the final check.

### The State Check (§5, §6)

The reviewer finds where state is held (an enum, a status column, a state field) and every code path that writes
it, and draws the as-built diagram from those writes. Then:

- **HIGH** — a transition the code allows that the spec does not have; a forbidden transition the code allows;
  a forbidden transition with no test that it is rejected.
- **MEDIUM** — a spec transition in scope with no code or no test; a state the code defines that the spec does
  not.
- A MEDIUM may instead be recorded under `### Implementation Deviations` with its reason, as the Tracing Lens
  allows. A HIGH may not.
- **The spec's model is never edited to match the code.** The code is fixed, or the difference is recorded.

## Costs and risks

- **The as-built diagram is a model reading the code, not the running product.** It is weaker evidence than the
  post means. Recording state changes at runtime — a span event per transition in a traced application — is the
  natural Tier 2, and is not proposed here.
- **The brief gets longer.** Its cap is 150 lines (aim under 100). A diagram plus its forbidden list costs about
  10–20 lines. Rule 2 (plain language, no code) needs one exception: the Mermaid block.
- **Reading state writes from code can miss some.** A transition made through a generic update, a raw SQL
  statement, or another service is easy to miss. §5 must say where to look, and a write the reviewer cannot
  trace is itself a finding.
- **Context.** Each review reads one more reference file. It is small, and read only when the spec has a
  `### State model`.

## Tiers

- **Tier 1 (this proposal):** the brief draws it, the spec maps it, the implementer tests it, the reviews and
  the final check compare it, the report names the outcome.
- **Tier 2:** as-built model from runtime, in traced applications — each transition recorded and compared with
  the spec on a real run, as the Tracing Lens does for calls.
- **Tier 3:** a diagram of a feature's existing states drawn at research time, so a change to an existing
  lifecycle is shown as a before/after pair at the design gate.

## Build order

1. The kill test above. Stop if it finds nothing.
2. `references/state-model.md`.
3. `bodies/design-brief.md` — a rule, the template section, the Mermaid exception to rule 2.
4. `bodies/planning.md` — `### State model` and the per-slice transitions line; `bodies/critical-review.md` — the
   fidelity checks.
5. `bodies/implementation.md` — the tests; `bodies/slice-review.md`, `bodies/code-review.md`,
   `bodies/final-check.md` — the State Check, by path.
6. **The prompts that pass the reference.** A body reads only the paths in its prompt (`SKILL.md`, the inputs
   rule), so every spawn that applies §2–§6 must be given `STATE_MODEL` = the reference's path: the brief
   (`phases/design-gate.md` 2.5a), the spec and its fix and critical-review spawns (`phases/planning.md`,
   `phases/planning-inputs.md`), and Step 4's shared inputs (`phases/implementation-inputs.md`) — the
   implementer, each review, and the fix spawns, which follow §6 to resolve a finding.
7. `phases/end-of-feature.md` — the 4j line; `docs/sdd-flow-diagram.md`; README; version bump.
8. Trial: one cycle on a feature with a lifecycle, and one without, to show "not applicable" changes nothing.
   With no state model, a cycle must behave exactly as it did before. In the cycle with a lifecycle, also draw
   the workflow diagram (Open, below) by hand beside the brief, and note whether it changed what the owner
   approved or asked.

## Open

- **Which version.** A new spec section and a new review check: a minor bump (5.1.0).
- **`sdd-lite`.** Its one-page brief could carry the same diagram. Out of scope here; decide after the trial.
- **A workflow diagram in the brief — try it in the trial, then decide.** A state diagram shows what one thing can
  be; a workflow diagram (a flowchart) shows the steps a process takes and in what order. Proposed rule, if the
  trial supports it: when a feature has a decision point or more than one actor, `## How it will work` is a
  Mermaid `flowchart` with every failure branch drawn (payment declined, upload too large, the call timing out),
  **in place of** the prose, so the two cannot drift; otherwise it stays prose. A reading aid only: no review
  compares it with the code and it adds no stop.
  - *For:* the brief is the one planning document the owner reads, and a decision drawn with only its "yes" arrow
    shows a missing failure path that prose hides. It also shows hand-offs between actors faster than a paragraph.
  - *Against:* most features are a short path with no branches, where a diagram adds lines and nothing else;
    nothing checks it, unlike the state model; it is intent, not the evidence of behaviour the post asks for.
  - *Decide by:* the trial's note. If the hand-drawn diagram changed nothing the owner approved or asked,
    do not add the rule.
