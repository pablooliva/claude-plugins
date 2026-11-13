# Planning inputs — Step 2.5 and Steps 3a–3g

Read this with `phases/design-gate.md` (Step 2.5) or `phases/planning.md` (3a–3g): the counters and the resolved paths both use.

---

Read when research's last step (2e) is done. Phase-execution and fix subagents carry the Safety-Net Rule + a fresh counter file (`Reads: 0/15`) + the `planning-compact.md` compact body path. Body paths are `SKILL_ROOT/bodies/<file>.md`, resolved absolute. A review step run on the second model carries none of the three (`references/second-model-review.md` §3).

Three resolved paths recur below. **BRIEF** = `SDD/requirements/DESIGN-[###]-[feature-name].md`, the design brief. **TIERS** = the tier standard resolved at Step 0 (`SKILL.md` → SKILL_ROOT resolution). **TIER_PLAN** = `SDD/flow/TIERS-[feature-name].md`, the record of what each delivery tier contains — on a next-tier cycle it is the path recorded at Step 0, which carries the first tier's feature name (no `-t2` / `-t3` suffix).

**TRACING** = the tracing standard, from the Step 0 record. **The observability line** = `Observability record: present` or `Observability record: absent` — whether the application has the tracing foundation, `SDD/OBSERVABILITY.md`. Before approval the orchestrator looks for that file just before each design-brief spawn and passes what it found; at approval it looks once more and records the line (2.5b), and from then on that recorded line is the observability line for the cycle — a foundation installed later changes nothing until the next cycle. From 3c on, the **tracing gate** is `on` or `off`, as the latest `## Gates - ` line says; a spawn after 3c in a cycle that has no such line (it was planned before tracing was part of the flow) is passed `tracing: off`.

**EVALS** = the evals reference (`SKILL_ROOT/references/evals.md`, `SKILL.md` → SKILL_ROOT resolution): what an eval is, its two kinds, and how its cases are written. It is passed to the design-brief and planning spawns when the observability line says `present`. From 3c on, the **evals gate** is `on` or `off`, as the `evals:` part of that same `## Gates - ` line says; a line with no `evals:` part (a cycle that passed 3c before evals were part of the flow), or no line at all, is `evals: off`.
