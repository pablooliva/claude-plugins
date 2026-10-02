# Tiers — shared standard

The plugin's one definition of delivery tiers: what each tier is, what may never be left out, how an item is placed in a tier, and how a deferral is recorded. The `simplicity-challenge` skill applies it. Any other skill or flow that works in tiers reads this file instead of restating it.

## The three tiers

- **Tier 1 — POC-plus.** The main scenario, end to end, for the inputs the first user will really give it. Real code in the real codebase with tests for what it does. Kept, not thrown away — that is the "plus".
- **Tier 2 — Standard.** The common variations, the errors that will really occur handled properly, sensible configuration.
- **Tier 3 — Full.** Rare edge cases, graceful degradation, performance and scale work, extension points.

Each tier is delivered and used before the next is planned. Tiers 2 and 3 are sketches — ten lines each at most — until their own turn comes. A later tier may be reshaped or dropped once the earlier one has been used; a sketched tier that is never built is an acceptable outcome, not unfinished work.

## Tenet 1 — Scope, never rigour

A tier limits what is built. It does not lower how well it is built: the same reviews, tests for everything the tier does, and every verification step the workflow in use requires. A Tier 1 is small, not sloppy.

## Tenet 2 — Nothing is built ahead

A tier contains the simplest code and structure that serves that tier. No part exists because a later tier is expected to need it — no extension point, abstraction, parameter, configuration option, generic type, hook, flag, dependency, or empty module.

- **Later-tier test:** remove the later tiers from the plan. Would this part still be here? If not, remove it. (Not the *deletion test* of `improve-codebase-architecture/references/codebase-design.md`, which asks a different question: whether a module is a pass-through.)
- **Rework is expected.** A later tier may reshape an earlier tier's code. That is the budgeted cost of working in tiers, paid once with real knowledge; it is never a reason to build ahead.
- **"A later tier will need it" is not a justification** — in a proposal, a brief, a spec, a review response, or a code comment.

## The floor — never deferred

1. Protection against losing or corrupting data on the paths this tier builds.
2. Security controls on any surface this tier exposes.
3. Loud failure: a case this tier does not handle fails visibly, never with a quietly wrong result.

**Costly-to-reverse decisions are not on the floor.** Simplicity wins: take the simplest option for this tier even when changing it later will be expensive (a stored data format, a public interface shape). The duty is disclosure, not prevention — state the reversal cost where the decision is recorded, so the user can overrule it. A later tier's needs may break a tie between options of equal simplicity, and nothing more.

## Cut tests

Run each item of the proposal through the tests for its kind. The first test that gives a verdict places the item; an item no test defers or removes stays in Tier 1.

Functional — what the proposal does:

- **Evidence** — has this case happened, or will it on first real use? No → defer.
- **By hand** — can the user do this manually for now? Yes → defer.
- **Hard-code** — can this setting be a constant for now? Yes → defer the setting.
- **Add-later cost** — what would it cost to add once the rest exists? This test never keeps an item in the tier. Its answer (cheap / moderate / expensive) is recorded with every deferral so the user can overrule it.

Structural — the parts the proposal adds:

- **Existing code** — can something already in the codebase do this? Yes → use it and add no new part. Check the code; do not assume.
- **Moving parts** — a new dependency, stored state, background process, queue, or cache needs a stated reason to be in Tier 1. No reason → remove.
- **Two adapters** — an extension point with only one thing behind it is removed. `improve-codebase-architecture/references/codebase-design.md` → Principles owns this rule.
- **Later tier** — a part that would not be here if the later tiers were deleted from the plan is removed (Tenet 2).

Verdicts differ by kind:

- **A functional item** — something the proposal does — is **deferred** to Tier 2 or Tier 3, or **cut** outright when nothing suggests it will ever be needed.
- **A structural part** — something that exists in order to deliver behaviour — is **kept** when the behaviour staying in this tier needs it, and **removed** when it does not. Every tier builds the structure its own behaviour needs, and no more.
- **Structure is not scheduled.** A removed part is not written down as work for Tier 2 or Tier 3, the way a deferred behaviour is. Putting "exporter interface — Tier 2" in a plan decides Tier 2's design before Tier 1 has been used, and shapes Tier 1 around a part that may never be needed (Tenet 2). A later tier chooses its own structure when its turn comes, from what it then has to do; it may arrive at the removed part, or at something simpler.
- **Parts follow the behaviour they serve.** When a functional item is deferred or cut, the parts that exist only for it go with it and are not judged separately. Only parts serving behaviour that stays in the tier get structural tests of their own.

## Recording a deferral

Every deferred functional item states: what it is, which tier it moves to, which cut test placed it there, how it fails loudly if this tier can reach the case ("not reachable" otherwise), and what it would cost to add later. Together with an ID and where the item came from, these are the columns of the tier plan's Deferred table. Removed parts and outright cuts are not deferrals: they get one line each under a `Removed` heading — what it was, and the test that removed it.

## Tier plan

The record that carries a feature from one tier to the next. Keep it under 60 lines. In a repository with an `SDD/` folder it lives at `SDD/flow/TIERS-[feature-name].md`; elsewhere, beside the proposal file it was made from. When the proposal exists only in the conversation and there is no `SDD/` folder, ask the user where to write it.

```markdown
# TIERS-[feature-name]

| Tier | Status | Built in | Task |
|---|---|---|---|
| 1 — POC-plus | planned / in progress / shipped [date] / dropped | [spec, branch, or PR — or —] | [tracker key — or —] |
| 2 — Standard | sketch | — | — |
| 3 — Full | sketch | — | — |

## Tier 1
[Five lines at most: what it does, what it deliberately does not, and — once shipped — what to look at when using it.]

## Deferred
| ID | Item | To tier | Why it was safe to leave out | If reached now | Cost to add later | Came from |
|---|---|---|---|---|---|---|
| DEFER-001 | [item] | 2 | [reason, naming the cut test] | [how it fails loudly, or "not reachable"] | cheap / moderate / expensive | [proposal / review / implementation] |

## Removed
- [part or item] — [the cut test that removed it]

## Tier 2 — sketch
[Ten lines at most. Behaviour only: what the feature would do, never the structure it would use.]

## Tier 3 — sketch
[Ten lines at most. Behaviour only.]

## Feedback
[Dated notes from using, testing, or reviewing the shipped tier. The next tier starts from these.]
```
