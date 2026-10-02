# Design Brief Gate for sdd-flow

**Status:** Implemented in agent-engineering 3.4.0, together with the companion proposal. The shipped skill files supersede the appendices below, which are kept as the original drafts.
**Date:** 2026-10-02
**Affects:** `agent-engineering/` plugin (`sdd-flow` skill: one new body, edits to six phase files, `SKILL.md`, five existing bodies, README, version). The `sdd/` plugin is frozen at 2.2.0 and is not touched.
**Author of intent:** Pablo Oliva. Drafted with Claude.
**Background:** `qrspi/README.md` (QRSPI analysis, 2026-05-13).
**Companion:** `proposals/tiered-delivery-2026-10-02.md`. It defines the three delivery tiers that the brief proposes and the gate asks the human to choose between. The brief's `## Tiers` section and the gate's tiers line below come from it; the two proposals are meant to ship as one change.

---

## Problem

When working with an agent, the volume of proposed change outruns the human's ability — or willingness — to review it, and approval becomes a reflex. The cost is not only missed defects: the human loses the conceptual picture of what is being built in a given cycle, so there is nothing to review the code *against*.

`sdd-flow` today makes this worse at exactly one point:

- **No human pause anywhere in planning.** Supervised mode pauses after research (Step 2f) and before the final implementation commit (Step 4h). `phases/planning.md` §3g goes from the committed spec straight into implementation: "no checkpoint here".
- **The research pause asks for a decision without the material to make it.** Step 2f shows a summary of findings and asks "Proceed to planning? (y/n)". Research describes what exists; it does not say what will be built. The honest answer is almost always a reflexive `y`.
- **The spec is not a human-review artifact.** `bodies/planning.md` defines twelve top-level sections (among them requirements with a quantitative ledger, edge cases, failure scenarios, modules, slices, validation, risks). It is written for the implementation subagents and reviewed by a specialist panel and an Opus critical reviewer. A human asked to approve it would be approving it unread.

So the first time the human meets the *design* is as code, slice by slice — the most expensive place to disagree with it.

## What QRSPI offers, and what to take from it

QRSPI splits planning into three artifacts:

| Step | What it is | Who reads it |
|---|---|---|
| Design | ~200 lines: current state, desired end state, patterns to follow, decisions, open questions. The agent must ask the human its questions before finalising. | The human |
| Structure | ~2 pages: signatures, types, order of work. No implementation. | Mostly the next agent |
| Plan | Detailed steps with verification checkboxes. | The implementing agent; the human does not read it |

The claim worth borrowing is about the **review surface**: the human reviews the short design and, later, the code — never the long plan.

**Take:** the design step, as a short document written for the human, with a mandatory stop and questions the human must answer.

**Do not take:** the structure step. The spec's `## Modules` section (public interface, what each module hides, risk tier) and `## Delivery Slices` section already carry that information. A separate structure artifact adds a handoff between agents and no information, and it would split the spec frontmatter that routes the rest of the flow (`delivery_mode`, `review_panel`, `agent_security`). The QRSPI analysis reached the same conclusion in Part 5 §3.

**Do not take:** the eight-step pipeline shape. `sdd-flow` already runs more sub-steps than QRSPI has steps.

## Proposal in one paragraph

Insert **Step 2.5 — Design Gate** between research and planning. One subagent writes a **design brief**: a plain-language document of at most 150 lines saying what will be built, how it will work, which decisions were made and what was rejected, where the changes will land, in what order, and what the human must decide. The flow stops and shows it. The human answers the questions, asks for changes, or approves. Only then is the spec written — and the spec must conform to the approved brief or list its deviations, which are shown to the human before implementation starts. The brief replaces the research pause (2f) as the supervised checkpoint, so the number of routine pauses does not grow.

---

## Design

### 1. The artifact

| | |
|---|---|
| Path | `SDD/requirements/DESIGN-[###]-[feature-name].md` |
| Created by | Design-brief subagent, **on Opus** (`agent-engineering:sdd-workhorse` with the per-spawn model override `opus`; body `bodies/design-brief.md`) |
| Read by | The human; planning (3a); spec critical review (3d); spec fix subagents (3c loop, 3e) |
| Length | Hard cap 150 lines, target under 100 |
| Language | Plain. No requirement IDs (none exist yet), no code, no signatures. Project terms defined on first use; glossary names used when `SDD/UBIQUITOUS_LANGUAGE.md` exists |

Sections (full template in Appendix A):

1. **In one paragraph** — the whole feature, conceptually.
2. **What you will be able to do afterwards** — three to five observable outcomes.
3. **How it works today** — the relevant current state, from research.
4. **How it will work** — the main scenario walked through step by step.
5. **Key decisions** — each with the option chosen, the option rejected, why, and what it costs to reverse.
6. **What changes where** — the footprint: which areas are new or changed, and roughly how much.
7. **Tiers** — the three tiers defined in the companion proposal: Tier 1 in full, Tiers 2 and 3 as sketches of at most ten lines each. Everything else in the brief describes the recommended tier only.
8. **Delivery outline** — proposed slices for the chosen tier, in order, each stated as what becomes observable after it lands.
9. **Not doing** — what is excluded for good. Items left for a later tier go under Tiers, not here.
10. **Questions for you** — at most five, each with options and a recommended answer. All must be answered before the brief can be approved.
11. **Least sure about** — where the brief's author would look first if this goes wrong.

Two rules do the real work:

- **Decide what research settles; ask only what needs the human.** A question is for the human when it turns on preference, product behaviour, risk appetite, or a trade-off the codebase gives no evidence for. Everything else is a decision, recorded with its rejected alternative so the human can overrule it.
- **The length cap is a signal, not a formatting target.** A brief that cannot fit says so in its first line and recommends decomposition. It does not get compressed until it is unreadable.

### 2. The flow change

```
before:  2a–2e research → 2f PAUSE (supervised) → 3a spec → 3b–3f reviews → 3g → Step 4
after:   2a–2e research → 2.5a brief → 2.5b GATE → [2.5c revise ↺] → 3a spec → 3b–3f reviews → 3g (deviation check) → Step 4
```

- **2.5a** — spawn the design-brief subagent.
- **2.5b** — the gate. The orchestrator posts a short message (template in Appendix B): the one-paragraph summary verbatim, each decision in a line, each question with its options, the research critical-review result, and the path to the brief. Then it stops.
- **2.5c** — if the reply contains answers or change requests, spawn a revise subagent with the reply verbatim; it updates the brief, records the answers under `## Answers and changes`, bumps `revision:`, and the gate is shown again with a one-line "what changed". The loop is driven by the human, so it has no iteration cap.
- **Approval** — `approve` is accepted only when the brief has no open question. While any question is open it is refused: the orchestrator lists the open questions and waits. Each one needs an answer from the human — "use your recommendation" counts, said per question — which makes it a revision round (2.5c) followed by the gate again. Nothing is accepted by default, so a bare `approve` cannot wave a question through. On approval the orchestrator appends `## Design Brief - APPROVED (revision N, tier T)` to `progress.md`.
- **Approval state lives in `progress.md` only.** The brief carries a `revision:` number and nothing about approval. The orchestrator may not edit artifacts, so it records the state in `progress.md` and passes the approved revision and tier in the spawn prompt of every subagent that reads the brief.
- **Step 2f is removed.** Its content (key findings, critical-review result, ADRs captured) moves into the gate message.

This stays inside the existing orchestrator discipline: the orchestrator writes a checkpoint message and records state; all writing of the brief happens in spawned subagents.

### 3. Modes and flags

| Mode | Behaviour at Step 2.5 |
|---|---|
| Supervised | Brief written; gate always fires |
| Autonomous | Brief written; gate always fires — the same stop as in supervised mode. Like the clarification gate (Step 1.5), this is a mandatory stop in both modes |

The gate fires every time a brief is written or rewritten: on the first draft, after every revision round, and after a re-plan. The purpose of the stop is that the human knows what is about to be built, and that purpose does not depend on the mode or on whether the brief happens to contain a question. Autonomous mode therefore has two mandatory stops before building starts — clarification and design approval — plus a third only when the spec departs from the approved brief (§4). It runs unattended from there, apart from slice pauses, which have their own flag.

### 4. Keeping the spec honest to the brief

An approved brief is worth little if the spec can drift from it unseen. Planning has three places where the spec is rewritten after the brief is approved: the planning subagent itself (3a), the panel fix loop (3c), and the combined fix (3e).

- **Spec template** gains `- **Based on Design:**` in the Executive Summary and a new section `## Deviations from Design Brief`. The section body is the single line `None.` or a list of entries: what the brief said, what the spec says, why, and a kind (`decision` | `scope` | `footprint` | `slice-outline`).
- **Binding parts of the brief:** Key decisions, Not doing, and answered questions. The delivery outline is the starting slice order; the planning body may refine it (it runs the slice-practicality gate, which the brief does not).
- **Rule for every spec-writing subagent (3a, 3c fix, 3e fix):** depart from the brief when research, the feasibility arithmetic, or a review finding requires it — and record the departure. Never silently.
- **Spec critical review (3d)** gains a **Design Brief Fidelity** block, mirroring the existing Design Concept Fidelity block that checks research against the clarification document. An unrecorded departure from a binding part is a HIGH finding.
- **Step 3g** reads the spec's `## Deviations from Design Brief`. If its first non-empty body line is not `None.` (the same body contract the re-planning halt uses):
  - **both modes** → append an `## Awaiting Deviation Approval` halt block to `progress.md`, pause, and show the deviations before Step 4. Autonomous mode stops here too: a spec that departs from the approved brief is no longer what the human agreed to build. The halt block is required: `Planning Phase - COMPLETE` is already written by the completion subagent in 3a, so without it `/sdd-flow continue` would route straight to Step 4;

The result: after approving the brief, the human is brought back into planning only when something they approved has changed.

### 5. Resumption and re-planning

- **New halt blocks:** `## Awaiting Design Approval` (gate, 2.5b) and `## Awaiting Deviation Approval` (3g). Progress rotation already carries forward any block whose header starts with `## Awaiting `, so no rotation change is needed.
- **Phase detection** (`phases/protocols.md`) — four edits:
  - new rule among the halt-block rules: `## Awaiting Design Approval` latest → re-show the gate from the brief on disk (2.5b);
  - new rule among the halt-block rules: `## Awaiting Deviation Approval` latest → re-read the spec's deviations section (the user may have edited the spec) and re-run the 3g check;
  - "If research is active → resume the appropriate sub-step (2a–2f)" becomes "(2a–2e)";
  - "If **Research Phase - COMPLETE** → start Step 3" becomes "→ Step 2.5: no `DESIGN-*` file → 2.5a; latest `## Design Brief - ` line is `Drafted` → 2.5b; latest is `APPROVED` → Step 3". Reading the latest line, rather than testing for any, keeps this correct after a re-plan writes a new `Drafted` line below an old `APPROVED` one.
  - Flows already in planning or implementation when the change ships are unaffected: the "planning is active" and implementation rules match first.
- **`--replan`** re-runs Step 2.5 before Step 3. The revise subagent receives the rolling ledger and the triggering retrospective, and writes a `## What changed since revision N` section at the top. The gate fires in both modes: a re-plan means the approved design was wrong, and the human is already present, having typed the flag.

### 6. Check each slice against the brief

Sections 1–5 give the human the conceptual picture. They do not make the code changes easier to review. This part uses the approved brief at the points where code is shown, and ships with the rest:

- **`bodies/slice-review.md`** already computes the slice's file set (its Step 4). Add a `## Design Brief Check` section to the review document: which delivery-outline entry this slice delivers, and any changed file that falls outside the brief's "What changes where" table, each with a one-line reason.
- **Whole-feature mode:** `bodies/code-review.md` (Step 4b) writes the same section once, over the whole feature's changed files.
- **Slice-boundary pause and Step 4h** quote that section: "Delivers outline item 2. Outside the approved footprint: none."

A file changed outside the approved footprint is the cheapest available signal of a surprise. It is information for the human, not a review finding: it never blocks a slice or enters a fix loop. Draft text in Appendix F.

**Known risk:** how precise the briefs' "What changes where" tables will be is untested. If they are vague, this line will report something on every slice and become noise. The trial measures it; the remedy is tightening the brief's footprint rule, not dropping the check.

---

## What this does not do

- **It does not shrink diffs.** Per-slice delivery does that, and is already the authoring default.
- **It does not prevent rubber-stamping.** A 150-line brief can be approved unread too. The mitigations are the length cap, the questions that need an answer rather than a `y`, and the trial below, which measures whether the gate is being used.
- **It does not replace the clarification gate (Step 1.5).** Clarification records what the human wants, before research. The brief records what will be built, after research has shown what the codebase allows. The brief must honour the clarification's constraints and raise any conflict as a question.
- **It does not add information hiding.** The other QRSPI idea — research that never sees the task description — is a separate change and is not proposed here.

## Costs and risks

| Cost or risk | Size | Note |
|---|---|---|
| Extra spawns | +1 per feature, +1 per revision round | Opus — the one planning spawn a human reads, so the cost is spent where judgment on "decide versus ask" matters most |
| Extra read for planning (3a) and spec review (3d) | +1 file each | Within the existing 15-read safety net |
| Two artifacts that can disagree | Real | Addressed by §4: binding parts, recorded deviations, fidelity check, 3g pause |
| Pause fatigue | Neutral in supervised mode; autonomous mode gains stops | 2f is removed; one pause replaces another. The deviation pause at 3g fires only when there are deviations, in both modes |
| Autonomous flows gain mandatory stops | One each time the brief is written or rewritten — at least one per feature — plus one if the spec departs from it | Intended, and not skippable |

## Alternatives considered

- **Full design → structure → plan split.** Rejected: see "Do not take" above.
- **A pause after the spec (at 3g) with the spec's Executive Summary.** Rejected: by then the panel and critical review have already been spent on the spec, so a human "no" throws that work away; and the summary is a description of the spec, not something the spec was held to.
- **An interactive depth-0 command (`/design-brief`), like `/research-clarify`.** A real back-and-forth interview would produce better answers than one round of questions. Deferred: it takes the human out of the flow and back in, as clarification does. Worth revisiting if the trial shows the gate's question rounds are too stiff.
- **A `--skip-design-gate` flag** (an escape hatch like `--skip-clarify`). Drafted, then dropped: it contradicts the purpose of the stop, and it needed its own handling for an unreviewed brief in six places (planning assumptions, the spec review, the deviation check, the slice pause, the completion announcement, phase detection). Cheap to add later if unattended runs turn out to need it.
- **Keep Step 2f and add the gate as well.** Rejected: two consecutive pauses, the first of which invites a reflexive `y`, works against the problem this proposal exists to address.

## Decided (2026-10-02)

- **Step 2f is removed.** The design gate is the stop; there is no separate pause after research.
- **Opus writes the brief**, in both the first draft (2.5a) and every revision (2.5c).
- **The gate stops in both modes, every time the brief is written or rewritten.** Autonomous mode does not skip it, and there is no flag that does: `--skip-design-gate` was drafted and then dropped.
- **`approve` is refused while any question is open.** Each question needs an answer from the human; nothing is accepted by default.
- **The slice-against-brief check ships with the design gate**, not after a trial.
- **A spec that departs from the approved brief stops the flow in both modes** (Step 3g), until the human accepts the departures or edits the spec.

No decisions remain open.

## Trial

Run the change on three features before treating it as permanent. Record per feature (the `retro` skill can pull most of this from session transcripts):

| Measure | Why |
|---|---|
| Gate outcome: approved unchanged / answered questions / requested changes | Whether the gate is being used or stamped |
| Number of revision rounds | Whether one round of questions is enough |
| Deviations recorded by the spec, by kind | Whether the brief predicts the spec |
| Surprises at slice pauses and at 4h (something in the code the human did not expect) | The outcome the proposal is for |
| Slices where the brief check reported files outside the footprint, and how many of those were real surprises | Whether the footprint tables are precise enough for the check to mean something |
| Re-planning halts | Whether design errors are caught earlier |

**Keep** if at least one gate in three led to a changed brief and surprises at slice pauses went down. **Demote** to a non-pausing artifact (brief written, no gate) if all three briefs were approved unchanged and nothing else moved. **Remove** if the briefs were not read at all.

---

## Files affected

| File | Change |
|---|---|
| `skills/sdd-flow/bodies/design-brief.md` | **New.** Appendix A |
| `skills/sdd-flow/phases/research.md` | Remove §2f; header becomes "Steps 2a–2e"; last line routes to Step 2.5 |
| `skills/sdd-flow/phases/planning.md` | New "Step 2.5" section ahead of 3a (Appendix B); 3a inputs and task; 3c fix and 3e fix tasks; 3d inputs and task; 3g (Appendix C) |
| `skills/sdd-flow/phases/protocols.md` | Four phase-detection edits and the `--replan` wording (§5); add both new halt blocks to the canonical halt-block list |
| `skills/sdd-flow/phases/setup.md` | Step 1 mode prompt, supervised line: "pauses at two checkpoints: after the design brief, and before committing implementation"; autonomous line: "no checkpoints" becomes "stops for you to approve the design brief, and again only if the spec departs from it, then runs to the end". Step 1.5: "the **only** mandatory autonomous-mode checkpoint" becomes "one of two (with the Step 2.5 design gate)" |
| `skills/sdd-flow/phases/implementation-per-slice.md` | Checkpoint-axis table: "research-end" → "design gate" in the supervised rows, and the autonomous rows gain the design gate ("Research + planning autonomous" is no longer true). Slice-boundary pause contents: add the brief-check line (§6) |
| `skills/sdd-flow/SKILL.md` | Model Routing row: design brief (2.5a, 2.5c) → `sdd-workhorse` with `opus` override; Artifact Paths row and tree entry for `DESIGN-*`; State Machine: new row for 2.5, and "Research (2a–2f)" → "(2a–2e)"; `--auto` description; frontmatter description mentions the gate |
| `skills/sdd-flow/bodies/planning.md` | Template and process edits (Appendix D) |
| `skills/sdd-flow/bodies/critical-review.md` | Design Brief Fidelity block in the Planning Phase section (Appendix E) |
| `skills/sdd-flow/bodies/planning-complete.md` | Checklist line: `## Deviations from Design Brief` present and accurate |
| `agent-engineering/README.md` | Flow description and changelog entry |
| `agent-engineering/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` | → 3.4.0 (both), shipping together with tiers after the `simplicity-challenge` skill takes 3.3.0 — see the companion proposal's build order |
| `skills/sdd-flow/bodies/slice-review.md`, `bodies/code-review.md` | `## Design Brief Check` section (Appendix F). In `code-review.md` it is written in the normal Step 4b review only — `MODE: site-verification-only` (Step 4e.5) keeps running its one section and skips this one |
| Spawn briefs: per-slice 4b in `implementation-per-slice.md`; whole-feature 4b in `implementation-whole-feature.md` | Inputs: add the design brief's path |
| The slice-boundary pause in `implementation-per-slice.md`; §4h and §4j in `implementation-whole-feature.md` | Quote the brief-check line (4j so that autonomous whole-feature runs, which have no 4h, still show it) |

No change to agents, hooks, `scripts/site-diff.py`, or the enforcement-site standard.

---

## Appendix A — draft of `bodies/design-brief.md`

````markdown
# Write the Design Brief

You are a spawned subagent in an orchestrated /sdd-flow run. Your prompt provides resolved artifact paths and identifiers — use them verbatim. This file is your complete instruction set. Do not spawn subagents or invoke slash commands/skills, even if an Agent/Task tool is available — the flow's flat-orchestration contract forbids it; all work happens inline in your own context.

## Purpose

The design brief is the one planning document written for the human. They will read it, answer its questions, and approve it; the specification is then held to it. Nothing else in planning is read by a person. Write for someone who knows the product and has not read the research.

## Inputs

1. `SDD/research/RESEARCH-[###]-[feature-name].md` — read in full.
2. `SDD/research/CLARIFICATION-[###]-[feature-name].md` if present — its constraints and out-of-scope list bind you.
3. `SDD/UBIQUITOUS_LANGUAGE.md` if present — use its names exactly.
4. Accepted ADRs under `SDD/adr/` that the research cites — binding; cite them where they settle a decision.
5. **TIERS** — the tier standard, at the path in your prompt. Read it before writing; it defines the tiers, the floor, and the cut tests.
6. `SDD/flow/TIERS-[feature-name].md` if present — this is a later-tier cycle: its Deferred table and Feedback notes are your starting point.
7. **Revision runs:** inputs 1–6 again, plus the existing brief and the user's reply (verbatim in your prompt). On a re-plan, also the rolling ledger and the triggering retrospective.

## Rules

1. **Length.** At most 150 lines; aim for under 100. If the feature cannot be described within the cap, do not compress: write `Too large for one brief — recommend decomposition` as the first line under the title, say where the seams are, and stop.
2. **Plain language.** No requirement IDs, no code, no function signatures. Define a project-specific term in a clause the first time it appears.
3. **Decide or ask.** If the research settles something, decide it and record the rejected alternative. Ask the human only where the answer turns on preference, product behaviour, risk appetite, or a trade-off the codebase gives no evidence for.
4. **Questions.** At most five. Each has concrete options and a recommended answer with its reason. Every question must be answered before the brief can be approved, so ask only what is worth stopping for; anything else is a decision you make and record.
5. **Clarification conflicts.** If what the research supports conflicts with a constraint in the clarification document, do not resolve it yourself — raise it as a question.
6. **Footprint honesty.** List every area you expect to change in "What changes where", including tests, migrations, and configuration. An area left out here and changed later is reported to the human as a surprise.
7. **Least sure about** is never empty. Name the assumption you would check first if this design failed.
8. **Tier it.** Apply the cut tests in TIERS to everything the research suggests building. Describe Tier 1 as the recommended tier unless your prompt names another. Keep Tiers 2 and 3 to ten lines each — they are sketches that their own cycle will re-decide — and describe them as behaviour only: what the feature would do, never the modules or interfaces it would use. Nothing the floor protects may be deferred. Build nothing ahead (TIERS, Tenet 2): the design for the recommended tier contains no part that exists for a later tier, and no Key decision may give a later tier's needs as its reason except to break a tie between options of equal simplicity. Take the simplest option even when reversing it later will be expensive, and say so under that decision's "If this is wrong". If the feature is too small to tier, write `Tiers: not applicable — [reason]`.
9. **Later-tier cycles.** Open the brief with `## What we learned from Tier N`, from the tier plan's Feedback notes, and say which sketched items you kept, changed, or dropped.
10. **Write the tier plan** at `SDD/flow/TIERS-[feature-name].md` in the shape TIERS gives (create it on a first-tier cycle; update it on a later one).

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
| Area | New or changed | Size (S/M/L) | What changes |
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

1. Apply the user's answers and change requests. Move each answered question out of `## Questions for you` and into the brief proper (as a decision, a scope line, or a changed section).
2. Append to `## Answers and changes` (create it as the last section if absent): the revision number, the user's reply quoted verbatim, and what you changed in response.
3. Increment `revision:`. Do not record approval anywhere in the brief — approval state lives in `progress.md`.
4. If the user's reply shows the research is wrong on a point of fact, correct the research document as well and say so in your return.
5. On a re-plan, add `## What changed since revision N` directly under the title: what the ledger and retrospective showed, and which decisions or outline entries changed.

## Progress and return

Append to `SDD/orchestration/progress.md` (≤10 lines): `## Design Brief - Drafted (revision N)`, the brief's path, its line count, the number of decisions, and the number of open questions.

Return ≤200 words: the brief's path, the one-paragraph summary, the decision titles, and the questions.
````

## Appendix B — draft of the new section in `phases/planning.md`

````markdown
## Step 2.5: Design Gate

Runs after 2e and before 3a. The brief is the human's review surface for planning; the spec is held to it.

### 2.5a. Design-Brief Subagent

Spawn an **`agent-engineering:sdd-workhorse`** subagent **with the per-spawn model override `opus`** (the workhorse's instructions and tools, Opus's judgment — `sdd-critical-reviewer` is also Opus but carries an adversarial reviewer's persona, which is wrong for an author):
- **Body:** `bodies/design-brief.md`
- **Inputs:** `SDD/research/RESEARCH-[###]-[feature-name].md`, `SDD/research/CLARIFICATION-[###]-[feature-name].md` (if present), `SDD/UBIQUITOUS_LANGUAGE.md` (if present), existing `SDD/adr/`, **TIERS** (resolved at Step 0), `SDD/flow/TIERS-[feature-name].md` (if present), and the `--tier N` value if the user passed one.
- **Outputs:** `SDD/requirements/DESIGN-[###]-[feature-name].md`, `SDD/flow/TIERS-[feature-name].md`, append `progress.md`.
- **Task:** Write the design brief. Carries the Safety-Net Rule, a fresh counter (`Reads: 0/15`), and `planning-compact.md` as the compact body.

### 2.5b. Gate

**Fires in BOTH supervised and autonomous modes, every time the brief is written or rewritten. No flag skips it.**

The orchestrator never edits the brief. Approval state is the latest `## Design Brief - ` line in `progress.md` (`Drafted` = not yet decided, or `APPROVED`); pass the approved revision number and tier in the prompt of every later spawn that reads the brief.

Otherwise append `## Awaiting Design Approval` to `progress.md`, emit, and STOP:

> **Design brief ready. No detailed planning happens until you approve it.**
> [The brief's "In one paragraph", verbatim]
> **Tiers:** building **Tier [N]** — [one line]. Left for later: Tier 2 — [one line]; Tier 3 — [one line].
> **Decisions made:** [D1 title — chosen option] · [D2 …]
> **Questions for you:** [Q1 — options — recommended (a)] · [Q2 …]
> **Research review:** [one line: critical-review severity and whether findings were resolved] · ADRs captured: [numbers or "none"]
> Brief ([N] lines): `SDD/requirements/DESIGN-[###]-[feature-name].md`
> Research: `SDD/research/RESEARCH-[###]-[feature-name].md`
> Reply with your answers and any changes — including `tier 2` or `tier 3` to build more now. `approve` accepts the brief as written, and is available once every question above has an answer. `stop` halts here.

A reply that changes the tier is a change request (2.5c): the brief's delivery outline, footprint, and decisions are rewritten for that tier. On approval, record the tier in the progress line: `## Design Brief - APPROVED (revision N, tier T)`.

- **Answers or changes** → 2.5c.
- **`approve`** → accepted only when `## Questions for you` is `None.`: append `## Design Brief - APPROVED (revision N, tier T)` to `progress.md` and proceed to 3a. If any question is still open, **refuse**: reply with the open questions, say that each needs an answer ("use your recommendation" counts as one, given per question), and stay at the gate. Nothing is rewritten and nothing is assumed.
- **`stop`** → leave `## Awaiting Design Approval` as the latest block and halt. `/sdd-flow continue` re-shows this gate.

### 2.5c. Revise

Spawn an **`agent-engineering:sdd-workhorse`** subagent, again with the model override `opus`:
- **Body:** `bodies/design-brief.md` — its **Revision runs** section.
- **Inputs:** the 2.5a inputs, the existing brief, and the user's reply **verbatim**.
- **Outputs:** updated brief; updated RESEARCH document only if the reply showed it wrong on a point of fact; append `progress.md`.

Then return to 2.5b; open the gate message with one line stating what changed. The loop has no cap — every round is requested by the user.
````

## Appendix C — draft edits to existing steps in `phases/planning.md`

- **3a, Inputs:** add `SDD/requirements/DESIGN-[###]-[feature-name].md`.
- **3a, Task:** add "The design brief is binding on Key decisions, Not doing, and answered questions; its delivery outline is the starting slice order. Record every departure in the spec's `## Deviations from Design Brief`; write `None.` when there are none."
- **3c fix subagent and 3e fix subagent, Inputs:** add the brief. **Task:** add "If a resolution departs from the design brief, add an entry to `## Deviations from Design Brief` — do not leave the section saying `None.`"
- **3a, 3c fix, 3d, 3e spawn prompts:** carry the approved revision number and tier (Appendix B).
- **3d, Inputs:** add the brief. **Task:** add "Apply the Design Brief Fidelity block."
- **3g, replacing the current paragraph:**

````markdown
Read the spec's `## Deviations from Design Brief`. If the first non-empty body line is `None.`, proceed to Step 4.

Otherwise:
- **Both supervised and autonomous modes:** append `## Awaiting Deviation Approval` to `progress.md` (required — `Planning Phase - COMPLETE` is already recorded, so without a halt block `continue` would route to Step 4), then pause.
  > **The spec departs from the brief you approved in [N] way(s):**
  > [each deviation: what the brief said → what the spec says — why]
  > Reply **y** to accept and start implementation, or **n** to halt and edit the spec.
  - **y** → append `## Design Deviations - ACCEPTED` and continue.
  - **n** → halt with the block pending. `/sdd-flow continue` re-reads the section and re-runs this check.

Then read the spec's `delivery_mode:` and route: `whole-feature` → `phases/implementation-whole-feature.md`; `per-slice` → `phases/implementation-per-slice.md`.
````

## Appendix D — draft edits to `bodies/planning.md`

- **Initial Context Load:** add step "Read the design brief at the path in your prompt. Your prompt states whether it was approved."
- **Template, Executive Summary:** add `- **Based on Design:** DESIGN-[###]-[feature-name].md (revision N, Tier T)`.
- **Template, new section after `## Intent`:**

````markdown
## Deviations from Design Brief

[`None.` — or one entry per departure:]

- **[decision | scope | footprint | slice-outline]:** the brief said [X]; this spec says [Y]. **Why:** [research finding, arithmetic, or review finding that required it].
````

- **Planning Process, new step before "Transform Research into Requirements":** "Conform to the brief. Its Key decisions, Not doing list, and answered questions are binding; its delivery outline is your starting slice order. Where research or the feasibility arithmetic forces a departure, make it and record it under `## Deviations from Design Brief`. Never depart silently, and never reopen a question the user has answered."
- **Quality Checklist:** add "`## Deviations from Design Brief` is present, and is `None.` only if the spec matches every binding part of the brief."

## Appendix E — draft block for `bodies/critical-review.md`, Planning Phase section

````markdown
### Design Brief Fidelity

If `SDD/requirements/DESIGN-[###]-[feature-name].md` exists, load it and verify:

- [ ] **Decisions honoured** — Does the spec implement every Key decision as chosen? A decision reversed or weakened without an entry under `## Deviations from Design Brief` is a HIGH finding.
- [ ] **Answers honoured** — Is every answer the user gave (the brief's `## Answers and changes`) reflected in the spec?
- [ ] **Scope respected** — Does any requirement, module, or slice fall inside the brief's "Not doing" list?
- [ ] **Footprint consistent** — Do the spec's modules stay within the brief's "What changes where"? New areas must be recorded as `footprint` deviations.
- [ ] **Outline recognisable** — Can each brief outline entry be matched to one or more delivery slices? Reordering and splitting are fine when recorded.
- [ ] **Deviations accurate** — Is every recorded deviation real, and is every real deviation recorded?

If no brief exists (a flow that began before the design gate shipped), note the gate was skipped; this is not a finding.
````

## Appendix F — draft of the brief check

**New section in the review document written by `bodies/slice-review.md` (per slice) and `bodies/code-review.md` (whole feature):**

````markdown
## Design Brief Check

- **Delivers:** [the brief's delivery-outline entry or entries this slice corresponds to, quoted — or "no matching outline entry", with what it is instead]
- **Outside the approved footprint:** [`None.` — or one line per changed file that falls under no row of the brief's "What changes where" table: the file, and why it was touched]

Informational only. Do not raise a finding for an out-of-footprint file on that ground alone, and do not let this section affect the APPROVED / REJECTED decision. In `code-review.md`'s `MODE: site-verification-only`, skip this section entirely. If no design brief exists for this feature, write `No design brief — check skipped.`
````

**Added instruction in both bodies:** "Read the design brief at the path in your prompt. Compare the file set you computed for this review against the areas in its 'What changes where' table and against its delivery outline, and write the `## Design Brief Check` section."

**Slice-boundary pause (`phases/implementation-per-slice.md`), added to the pause message contents:** "the review's Design Brief Check, as one line: `Brief check: delivers [outline entry]. Outside the approved footprint: [none | N file(s) — list]`."

**Step 4h and Step 4j (`phases/implementation-whole-feature.md`), added line — in the 4h checkpoint message (supervised), and in the 4j announcement (both modes, so an autonomous whole-feature run still shows it):**

> Brief check: [per-slice mode: N of M slices stayed inside the approved footprint; exceptions: …] [whole-feature mode: outside the approved footprint: none | list]

