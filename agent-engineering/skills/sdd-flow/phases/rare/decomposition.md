# Rare case — Decomposition (Step 0)

Read this only when the Step 0 scope subagent (`phases/setup.md`) returns that the scope is too large for one cycle.

---

## If the scope is too large (decomposition needed)

The subagent writes `SDD/flow/DECOMPOSITION-[###]-[feature-name].md` containing: (1) **Rationale** referencing the heuristics; (2) a **decomposition checklist** of smaller, independently deliverable features, each a self-contained task description suitable as `/sdd-flow` input, with a note on what it delivers and why it is sequenced there, plus any dependencies; (3) a **dependency map**.

The orchestrator presents the decomposition to the user:

> **This feature request is too large for a single SDD cycle.**
> I've broken it into [N] independently deliverable steps:
> [Checklist summary]
> Full decomposition: `SDD/flow/DECOMPOSITION-[###]-[feature-name].md`
> Review and edit it as needed, then run `/sdd-flow` for each item when ready. Items with dependencies should be completed in order.

Then **STOP**. The user manually invokes `/sdd-flow <checklist item>` for each item at their own pace. (This decomposition stop is unconditional — the orchestrator does not auto-start the first item.)
