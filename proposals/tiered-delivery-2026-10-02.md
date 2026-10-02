# Tiered Delivery and a Simplicity Challenge

**Status:** Build-order step 1 (the `simplicity-challenge` skill and `references/tiers.md`) is implemented as agent-engineering 3.3.0; the shipped files supersede Appendices A and B below, which are kept as the original drafts. Steps 2–4 (the `sdd-flow` changes) are not implemented.
**Date:** 2026-10-02
**Affects:** `agent-engineering/` plugin — one new skill (`simplicity-challenge`), and the `sdd-flow` skill (bodies, phase files, `SKILL.md`, `commands/research-clarify.md`). The `sdd/` plugin is frozen at 2.2.0 and is not touched.
**Author of intent:** Pablo Oliva. Drafted with Claude.
**Companion:** `proposals/design-brief-gate-2026-10-02.md`. The design brief is where tiers are proposed and its gate is where one is chosen; the two proposals are meant to ship as one change to `sdd-flow`.

---

## Problem

Asked for a feature, the agent surveys every possibility, accounts for every case, and builds the robust version. The human receives more than they can review and more than they yet know they need.

Inside `sdd-flow` this is not only the model's inclination. The flow instructs it:

- `bodies/planning.md:316` — "Ensure every edge case from research has a corresponding specification."
- `bodies/planning.md:381` — "Every research finding reflected in requirements or edge cases."
- `bodies/planning.md:391` — "All research findings are incorporated" (repeated as a check in `bodies/planning-complete.md`).
- `SKILL.md:189` — "ALL findings (HIGH/MEDIUM/LOW) resolved before proceeding."
- The review bodies ask what is missing far more than what is unnecessary: the ad-hoc lens in `bodies/critical-review.md` has one line on scope creep against lines on under-engineering, error handling, and unconsidered edge cases.

Every one of these pushes scope up. Nothing pushes it down, and nothing lets a reviewer tell "missing by mistake" from "left out on purpose".

## Proposal in one paragraph

Deliver a feature in up to three **tiers**, each its own full cycle: **Tier 1, POC-plus** (the narrowest version that is really usable and is kept); **Tier 2, Standard**; **Tier 3, Full**. The design brief proposes all three and the human picks one at the gate — Tier 1 unless they say otherwise. The spec covers only the chosen tier and lists what was deferred; reviewers treat that list as deliberate. When the cycle ends, a small **tier plan** file records what shipped and what is left. The next tier is a new cycle that starts from feedback on the previous one, and may reshape or drop what was sketched. The rules for what belongs in which tier live in one reference file, which also powers a standalone **`/simplicity-challenge`** skill for cutting any proposal down outside the flow.

---

## 1. The tier standard

One file — `skills/simplicity-challenge/references/tiers.md` — defines tiers for both the standalone skill and `sdd-flow` (draft in Appendix A). This is the same arrangement as the OWASP control catalog, which the security-review skill owns and `sdd-flow` reads.

| Tier | Is | Leaves out |
|---|---|---|
| **1 — POC-plus** | The main scenario, end to end, for the inputs the first user will really give it. Real code in the real codebase, with tests for what it does. It is kept, not thrown away — that is the "plus". | Variations, configuration, rare inputs, scale, polish. Cases it does not handle fail loudly. |
| **2 — Standard** | What a normal feature is expected to do: the common variations, the errors that will really occur handled properly, sensible configuration. | Rare cases, hardening, extensibility. |
| **3 — Full** | Rare edge cases, graceful degradation, performance and scale work, extension points. | Nothing. |

**Two tenets hold in every tier.**

1. **Scope, never rigour.** Every tier goes through the same reviews, tests what it builds, and counts enforcement sites for the controls it includes. A Tier 1 is small, not sloppy.
2. **Nothing is built ahead.** A tier contains the simplest code and structure that serves *that tier*. No part exists because a later tier is expected to need it: no extension point, abstraction, parameter, configuration option, generic type, hook, flag, dependency, or empty module added in anticipation. The **later-tier test**: *remove the later tiers from the plan — would this part still be here?* If not, it goes. (Named apart from the existing *deletion test* in `codebase-design.md`, which asks a different question — whether a module is a pass-through.)

The second tenet has a corollary that makes it safe to follow: **a later tier is expected to reshape the code of an earlier one.** Refactoring Tier 1 while building Tier 2 is the normal, budgeted cost of the approach, not a sign that Tier 1 was done wrong. It is paid once, with real knowledge, instead of being prepaid on a guess — and many sketched tiers are never built at all.

**The floor — never deferred, in any tier:**

1. Protection against losing or corrupting data on the paths this tier builds.
2. Security controls on any surface this tier exposes.
3. Loud failure. A case this tier does not handle must fail visibly, never produce a quietly wrong result.

**Costly-to-reverse decisions are deliberately not on the floor.** Stored data formats, public interface shapes, and similar choices are made the simplest way that serves this tier, even when changing them later will be expensive. Erring toward simplicity is the point of working in tiers; a guess about a later tier is a poor reason to carry complexity now. What is required instead is **disclosure**: every Key decision in the brief states what reversing it would cost, so the human sees the trade at the gate and can overrule it. A later tier's needs may break a tie between options of equal simplicity, and nothing more.

**Cut tests** — how an item is placed in a tier:

| Test | Question | If yes |
|---|---|---|
| Evidence | Has this case happened, or will it on first real use? | Keep |
| By hand | Can the user do this manually for now? | Defer |
| Add-later cost | What would it cost to add once the rest exists? | Never a reason to keep it. The cost is recorded with the deferral so the human can overrule |
| Hard-code | Can this setting be a constant for now? | Defer the setting |
| Existing code | Can something already in the codebase do this? | Use it; add no new part |
| Moving parts | Does it add a dependency, stored state, a background process, a queue, or a cache? | Needs a stated reason to be in Tier 1 |
| Two adapters | Is this an extension point with only one thing behind it? | Remove it (the rule already in `improve-codebase-architecture/references/codebase-design.md`, cited, not restated) |
| Later tier | Would this part still be here if the later tiers were deleted from the plan? | If no, remove it (tenet 2) |

The first four concern functionality; the last four concern structure.

## 2. Tiers are separate cycles

Each tier is one complete `sdd-flow` run with its own number, brief, spec, reviews, and commits. The reason is feedback: using, testing, or reviewing Tier 1 teaches things that planning could not, and the next cycle should start from them.

Consequences:

- **Only behaviour is scheduled.** A later tier's sketch, and the tier plan's Deferred table, list what the feature would *do* — never the modules, interfaces, or other structure it would use. Each tier builds the structure its own behaviour needs and chooses it when its turn comes (decided 2026-10-02; the rule is stated in `tiers.md` → Cut tests).
- **Later tiers are sketches.** At Tier 1 time, Tiers 2 and 3 get at most ten lines each. Specifying them in detail up front would recreate the overload and would be planning against guesses.
- **The next cycle re-decides.** A Tier 2 cycle may reorder, shrink, or drop what was sketched. Tier 3 often never needs building; that is an acceptable outcome, not an unfinished job.
- **Within a cycle, slices work as they do today.** A tier says how much of the feature to build; slices say in what order to build it. Tier 1 will often be one or two slices.

### The tier plan — what carries over between cycles

`SDD/flow/TIERS-[feature-name].md`, a sibling of the existing `DECOMPOSITION-*` file (which splits a feature that is too *broad*; this splits one by *depth*). Short by design — target under 60 lines:

The template is the one shipped in `skills/simplicity-challenge/references/tiers.md` → Tier plan; it is not repeated here. In outline:

- a status table, one row per tier — status, what it was built in (for the flow: the cycle's spec), and its tracker task;
- **Tier 1** — what it does and, once shipped, what to look at when using it;
- **Deferred** — behaviour moved to a later tier, each with an ID, the reason, how it fails if reached now, and its cost to add later;
- **Removed** — parts and outright cuts, one line each;
- **Tier 2 / Tier 3 sketches** — behaviour only, ten lines each at most;
- **Feedback** — dated notes from using the shipped tier.

- **Written by** the design-brief subagent (Step 2.5a) alongside the brief.
- **Updated by** the completion subagent (Step 4f): status, what shipped, and anything deferred during planning reviews or implementation.
- **Read by** the next cycle.

### Starting the next tier

`/sdd-flow --next-tier [feature-name]` — Step 0 reads the tier plan, takes the next tier that is not shipped as the task, and assigns a new number with the feature name suffixed `-t2` or `-t3`.

- **The clarification interview becomes the feedback interview.** `/research-clarify` gains a branch for next-tier cycles: load the tier plan, walk the `## Feedback` notes, and ask what using the previous tier showed. This is the existing Step 1.5 gate doing a new job, not a new pause.
- **Research is a delta.** The research subagent receives the previous research document and the tier plan, and investigates the deferred items and what the shipped code changed.
- **The brief opens with "What we learned from Tier N"** and says which sketched items it kept, changed, or dropped.

## 3. What changes inside a cycle

### At the design gate

The brief gains a `## Tiers` section and its gate message a tiers line (edits are already folded into the companion proposal's Appendices A and B). The human replies with a tier, or approves the default once every question in the brief is answered.

| Situation | Tier used |
|---|---|
| The human names a tier at the gate (either mode — the gate always stops) | Their choice |
| Plain `approve` (accepted only when no question is open) | Tier 1 |
| `--tier N` flag | N |
| Feature too small to tier | The brief says `Tiers: not applicable` with a one-line reason, as the slice-practicality gate does for slices |

Choosing Tier 3 at the gate reproduces today's behaviour.

### In the spec

- Frontmatter gains `tier: 1 | 2 | 3`. Absent means untiered: every existing rule applies unchanged, so specs and flows written before this change behave as before.
- New section `## Deferred to Later Tiers`: item, target tier, and why it is safe to defer.
- **Deferred items carry no `REQ-` / `EDGE-` / `FAIL-` ID.** They are numbered `DEFER-XXX` and live only in that section. The spec's requirement lists therefore contain this tier's items and nothing else, and every existing "every REQ / every EDGE" rule keeps working untouched: orphan-requirement checks in the panel and critical review, slice reachability, "implement ALL requirements" in Step 4a, and the completion gates that demand a test per edge case.
- **A deferred case this tier can reach becomes a real requirement of this tier: its loud failure.** It gets a `FAIL-XXX` entry ("input of kind X is rejected with message Y"), which is implemented and tested like any other. That is how floor rule 3 is enforced rather than hoped for. These entries follow the normal slice rules: they stay out of SLICE-001, which the slice-integrity check requires to be the bare happy path, and are delivered by a later slice of the same tier — all of them by the tier's last slice. In whole-feature mode they are simply part of the feature.
- The completeness rules change so that a research finding may be accounted for by deferral: `bodies/planning.md:316`, `:381`, and `:391`, and the matching check in `bodies/planning-complete.md`, each accept "or recorded under `## Deferred to Later Tiers`".

### In reviews — making "left out on purpose" visible

Without this, the panel and the critical reviewer would flag every deferred edge case and push Tier 1 back up to Tier 3.

- **Panel specialists, critical review, code review, slice review** each gain one principle, *Respect the tier*: do not raise a finding for an item on the deferred list. Do raise one, at HIGH, when a deferred item breaches the floor — "unsafe to defer", naming which floor rule.
- **Fix subagents** gain one extra resolution for a finding: move the item to the deferred list with a reason. It is allowed only for findings about *absent* scope. A finding about behaviour the tier does build is a defect and must be fixed. This keeps "ALL findings resolved" intact and stops deferral being used to dodge a fix.
- **Reviewers also enforce "nothing is built ahead".** The same principle has a second half: raise a finding for any part that exists only for a later tier — in the spec's `## Modules` (an interface member, parameter, or module no requirement of this tier uses) and in the code (an unused abstraction, option, or hook). MEDIUM by default; HIGH when it adds a moving part (a dependency, stored state, a background process). "Tier 2 will need it" is not a justification; the fix is removal. The panel specialists carry this for the spec (it is a shared operating principle, so the `module-depth` specialist applies it without any change to its own section), code review and slice review for the code.
- **The spec's justification fields may not cite a later tier.** A module's `Justification (if shallow)` or a decision's rationale that rests on a later tier's needs fails the later-tier test above.
- **Enforcement-site counting** is unchanged. A control the tier includes is counted in full.

## 4. Tracking tiers as BB tasks

**The tier plan file is the record; BB tasks mirror it, and the flow keeps them in step.**

- **Why not tasks as the record.** Subagents in the flow read artifacts by path, the plan should be versioned with the code it describes, and `sdd-flow` is a published plugin with no dependency on BB today. A later cycle must be able to run with the file alone.
- **What tasks add that the file cannot.** A board that shows a Tier 2 is waiting; status at a glance across projects; links to the threads and pull requests of each cycle; and a place to jot feedback while using Tier 1, days after the cycle's session has ended.

The mapping fits BB's limit of one level of sub-tasks exactly:

| BB | Is | Carries |
|---|---|---|
| Parent task | The feature | Link to the tier plan |
| Three sub-tasks | The tiers | That tier's entry from the plan as the description; the brief attached |
| — | Slices, deferred items | Not tasks. They stay in the spec and the tier plan |

| When | What happens |
|---|---|
| Tier chosen at the gate | Create the parent and three sub-tasks if absent; chosen tier → `in_progress`, others → `backlog`. Task keys written into the tier plan |
| Before the final commit (Step 4h in supervised mode; the same point, just before 4i, in autonomous mode) | Chosen tier → `in_review` |
| Step 4j (done) | Chosen tier → `done`; one comment: what shipped, what to look at |
| While using the tier | The human comments on the next tier's sub-task |
| `--next-tier` starts | Comments on that sub-task are copied into the tier plan's `## Feedback`, so the cycle reads them from the file |

The mirror is **optional and never halts the flow**: it runs only when the `bb` CLI is present and a tracker project exists for the repository; otherwise, and on any error, it is skipped with one line in `progress.md`.

## 5. The `/simplicity-challenge` skill

A user-invoked skill that challenges a proposal's simplicity on both axes — what it does, and how it is built — using the tier standard. Draft in Appendix B.

- **Why a new skill.** `/critical-review` argues that a proposal is not enough. Nothing argues that it is too much. The built-in `/simplify` cleans up code already written; this works on a proposal before anything is built, which is why it has a different name.
- **Targets.** The last proposal in the conversation, or a file: a design brief, a spec, a plan, a written proposal.
- **Output.** Short, in chat: the smallest useful version; a table of cuts (behaviour cut or deferred to a tier, parts removed; the test that placed each; what you lose; what it costs to add later); what it kept on purpose because of the floor; and at most three questions where a cut depends on you.
- **It only removes or defers.** It never adds requirements, never edits the target, never implements. On request it rewrites the proposal in reduced form or writes a tier plan.
- **Where it meets the flow.** The design-brief subagent reads the same `tiers.md`, so a brief arrives already tiered by the same rules. And because the design gate is a stop, the human can run `/simplicity-challenge` on the brief there when it still looks like too much.

## Build order

| Step | What | Depends on |
|---|---|---|
| 1 | `simplicity-challenge` skill and `tiers.md` | Nothing — no `sdd-flow` change. Usable at once, including on existing specs |
| 2 | Design gate with tiers in `sdd-flow` (this proposal §2–3 plus the whole companion proposal, including its slice-against-brief check) | Step 1's `tiers.md` |
| 3 | BB task mirror (§4) | Step 2 |
| 4 | Re-review of `sdd-flow` with current models | Steps 2–3 trialled |

Step 1 is also the trial for the idea: use the skill by hand on two or three real proposals before changing the flow.

## Costs and risks

| Risk | Note |
|---|---|
| The flow's fixed cost is paid once per tier | Research, panel, and reviews run in every cycle. Later-tier research is a delta and many features will stop at Tier 1 or 2, but a feature taken through all three costs more in total than today. This raises the value of the planned re-review, whose aim is to lower the fixed cost per cycle |
| Tier 1 paints the feature into a corner (a data format or interface that is expensive to change) | Accepted on purpose: simplicity wins. The brief states each decision's reversal cost, so the human sees it at the gate and can overrule; the later tier pays for the change if it is ever built |
| The tie-break becomes a loophole for building ahead | It applies only between options of equal simplicity and can never add a part; reviewers apply the later-tier test |
| Deferral used to avoid fixing defects | Deferral is allowed only for absent scope (§3) |
| Deferred lists rot | One short tier plan per feature, with status; mirrored to tasks |
| Something unsafe is deferred | The floor, and the "unsafe to defer" finding available to every reviewer |
| Tier 1 is treated as throwaway and written carelessly | "Scope, never rigour": same reviews and tests |

## Decided (2026-10-02)

- **Tiers are on by default, and Tier 1 is the default tier.** Every brief proposes tiers; a higher tier is built only when asked for.
- **The flow updates the BB tasks itself.** The orchestrator runs the mirror as record-keeping, alongside `progress.md`.
- **Simplicity wins over avoiding expensive changes later.** Costly-to-reverse decisions are not protected by the floor; their reversal cost is disclosed, and the simplest option for the tier is taken.
- **Only behaviour goes on the list for later tiers.** Structure is never written down as work for a later tier.
- **The skill is named `simplicity-challenge`.** `simplify` is taken by a built-in that cleans up code already written.
- **A next-tier cycle runs the full specialist panel**, like any other cycle. Whether that can be trimmed is a question for the later re-review of the flow.

No decisions remain open.

---

## Files affected

| File | Change |
|---|---|
| `skills/simplicity-challenge/SKILL.md` | **New.** Appendix B |
| `skills/simplicity-challenge/references/tiers.md` | **New.** Appendix A |
| `skills/sdd-flow/SKILL.md` | Resolve **TIERS** (path to `tiers.md`) at Step 0 beside CATALOG and STANDARD; Artifact Paths row and directory-tree entry for `TIERS-*` (under `flow/`, beside `DECOMPOSITION-*`); Arguments rows for `--tier N` and `--next-tier`; Key Principle 2 notes the deferral resolution; orchestrator's direct-work list gains the optional task mirror |
| `skills/sdd-flow/phases/setup.md` | Step 0: `--next-tier` handling; record TIERS. Step 1.5: for a next-tier cycle the interview covers feedback |
| `skills/sdd-flow/phases/research.md` | 2a inputs for a next-tier cycle: previous research and the tier plan |
| `skills/sdd-flow/bodies/research.md`, `research-complete.md` | Next-tier branch: delta research, and a completeness check scoped to the delta |
| `skills/sdd-flow/phases/planning.md` | 2.5a outputs add the tier plan; gate records the tier; fix subagents (3c loop, 3e) get the deferral rule |
| `skills/sdd-flow/phases/implementation-whole-feature.md` | 4f updates the tier plan; 4j announcement names the tier shipped and what is left; mirror at 4h and 4j |
| `skills/sdd-flow/bodies/design-brief.md` | Tiers section and rule (in the companion proposal's Appendix A) |
| `skills/sdd-flow/bodies/planning.md` | `tier:` frontmatter; `## Deferred to Later Tiers` with `DEFER-XXX` IDs; loud-failure `FAIL-XXX` rule; the completeness rules at `:316`, `:381`, `:391` |
| `skills/sdd-flow/bodies/planning-complete.md` | Its "all research findings incorporated" check accepts deferral; verifies each reachable deferred case has a `FAIL-XXX` |
| `skills/sdd-flow/bodies/implementation.md`, Step 4a task | No change needed — "implement ALL requirements" stays true because deferred items are not requirements |
| `skills/sdd-flow/bodies/panel-specialist.md`, `critical-review.md`, `code-review.md`, `slice-review.md` | The *Respect the tier* principle, both halves: do not flag deferred items; do flag parts built for a later tier. In `panel-specialist.md` it goes under Operating Principles, where it applies to every specialist — not in §4.5, which mirrors `codebase-design.md` and must change only together with it. Neither §4.5 nor `codebase-design.md` changes |
| `skills/sdd-flow/bodies/implementation-complete.md` | Update the tier plan |
| `commands/research-clarify.md` | Feedback branch for next-tier cycles |
| `agent-engineering/README.md`, `CLAUDE.md` (skills tree) | New skill; tiers in the flow description |
| `plugin.json`, `marketplace.json` | Step 1 (the skill): 3.2.0 → 3.3.0. Step 2 (design gate with tiers, both proposals together): → 3.4.0. Both files each time |

---

## Appendix A — draft of `skills/simplicity-challenge/references/tiers.md`

````markdown
# Tiers — shared standard

Read by the `simplicity-challenge` skill and by `sdd-flow` (design brief, planning, reviews). Change it here; nowhere else restates it.

## The three tiers

- **Tier 1 — POC-plus.** The main scenario, end to end, for the inputs the first user will really give it. Real code in the real codebase with tests for what it does. Kept, not thrown away.
- **Tier 2 — Standard.** The common variations, the errors that will really occur handled properly, sensible configuration.
- **Tier 3 — Full.** Rare edge cases, graceful degradation, performance and scale work, extension points.

Each tier is delivered and used before the next is planned. Tiers 2 and 3 are sketches until their own cycle begins.

## Tenet 1 — Scope, never rigour

A tier limits what is built. It does not lower how well it is built: same reviews, tests for everything the tier does, enforcement sites counted for every control the tier includes.

## Tenet 2 — Nothing is built ahead

A tier contains the simplest code and structure that serves that tier. No part exists because a later tier is expected to need it — no extension point, abstraction, parameter, configuration option, generic type, hook, flag, dependency, or empty module.

- **Later-tier test:** remove the later tiers from the plan. Would this part still be here? If not, remove it. (Not the *deletion test* of `codebase-design.md`, which asks whether a module is a pass-through.)
- **Rework is expected.** A later tier may reshape an earlier tier's code. That is the budgeted cost of working in tiers, paid once with real knowledge; it is never a reason to build ahead.
- **"A later tier will need it" is not a justification** — in a brief, a spec, a review response, or a code comment.

## The floor — never deferred

1. Protection against losing or corrupting data on the paths this tier builds.
2. Security controls on any surface this tier exposes.
3. Loud failure: a case this tier does not handle fails visibly, never with a quietly wrong result.

**Costly-to-reverse decisions are not on the floor.** Simplicity wins: take the simplest option for this tier even when changing it later will be expensive (a stored data format, a public interface shape). The duty is disclosure, not prevention — state the reversal cost where the decision is recorded, so the user can overrule it. A later tier's needs may break a tie between options of equal simplicity, and nothing more.

## Cut tests

Functional:
- **Evidence** — has this case happened, or will it on first real use? No → defer.
- **By hand** — can the user do this manually for now? Yes → defer.
- **Add-later cost** — what would it cost to add once the rest exists? This never keeps an item in the tier. Record the cost with the deferral so the user can overrule it.
- **Hard-code** — can this setting be a constant for now? Yes → defer the setting.

Structural:
- **Existing code** — can something already in the codebase do this? Yes → use it.
- **Moving parts** — a new dependency, stored state, background process, queue, or cache needs a stated reason to be in Tier 1.
- **Two adapters** — an extension point with one thing behind it is removed. See `improve-codebase-architecture/references/codebase-design.md` → Principles; that file owns the rule.
- **Later tier** — a part that would not be here if the later tiers were deleted from the plan is removed (Tenet 2).

## Recording a deferral

Every deferred item states: what it is, which tier it moves to, which cut test placed it there, how it fails loudly if this tier can reach the case, and what it would cost to add later. These are the columns of the tier plan's Deferred table.

## Tier plan

[The template shown in §2 of this proposal, moved here so the skill and the flow share one copy.]
````

## Appendix B — draft of `skills/simplicity-challenge/SKILL.md`

````markdown
---
name: simplicity-challenge
description: "Challenge a proposal for doing or building too much, before anything is implemented. User-invoked: `/simplicity-challenge [file path | last] [functional | structural]`. Applies the tier standard to a proposal, plan, design brief, or spec and reports what could be cut or deferred — in functionality and in structure — what each cut costs, and the smallest version still worth using. It only removes or defers: it never adds requirements, never edits the target, never implements. NOT for cleaning up code already written (use the built-in `/simplify`), and NOT for finding what a proposal is missing (use `/critical-review`)."
disable-model-invocation: true
---

# Simplicity Challenge

Argue that the proposal in front of you is too much. Your job is to find the smallest version that is still worth using, and to say plainly what each cut costs.

## 1. Find the target

- A file path → read that file.
- `last`, or no argument → the most recent proposal, plan, or solution in this conversation.
- If there is no proposal to challenge, say so and stop.

Read `references/tiers.md` in this skill's directory before anything else. It defines the tiers, the floor, and the cut tests you apply.

## 2. Establish what the proposal is for

State in one sentence the need the proposal serves, in the user's words where they exist. Every cut is judged against this. If you cannot state it, ask — one question — and stop.

## 3. Apply the cut tests

- **Functional** (unless the user asked for `structural` only): list what the proposal does, and run the four functional tests on each item.
- **Structural** (unless the user asked for `functional` only): list the parts the proposal adds — modules, dependencies, stored state, processes, extension points, configuration — and run the four structural tests on each. Treat any part justified by future needs — "so we can later…", "to make it easy to add…" — as failing the later-tier test unless the user has said that future is already committed.

For a structural claim about existing code, check the code. Do not assume something already exists.

## 4. Check the floor

Anything the floor protects stays. List these so the user can see you did not cut safety.

## 5. Report

Keep it under 60 lines.

1. **Smallest useful version** — three to five lines: what it does and what it deliberately does not.
2. **Cuts** — one table:

   | Item | Kind (function / structure) | Verdict (cut · Tier 2 · Tier 3) | What you lose | Cost to add later (cheap / moderate / expensive) |

3. **Kept on purpose** — floor items, one line each, naming the floor rule.
4. **Questions** — at most three, only where a cut depends on something only the user knows.

## Rules

- **Remove or defer; never add.** If you believe something is missing, say so in one line at the end and point to `/critical-review`. Do not add it.
- **Do not edit the target and do not implement anything.**
- **No invented facts.** "The user will not need X" is a claim; base it on what the user said or the code shows, or put it as a question.
- **A verdict of "nothing to cut" is allowed.** Say so in one line rather than manufacturing cuts.

## On request

- "Rewrite it" → produce the reduced proposal, with the cuts listed under a `Deferred` heading.
- "Tier it" → write a tier plan in the shape given in `references/tiers.md` → Tier plan (in a repository with an `SDD/` folder: `SDD/flow/TIERS-[feature-name].md`).
````
