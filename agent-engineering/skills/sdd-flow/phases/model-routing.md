# Model Routing — which agent type and model each spawn uses

Read this when a spawn brief does not name its agent type, and at a Mid-Phase Handoff (`phases/rare/handoff.md`). The rules around it are in `SKILL.md` → Model Routing.

---

| Spawn site | Agent type | Model |
|---|---|---|
| Research, planning, ADR capture, fixes, completion, slice cycle (all but its implementation and review) | `agent-engineering:sdd-workhorse` | sonnet |
| Implementation — whole-feature 4a and every chunk of it, per-slice 4a | `agent-engineering:sdd-workhorse` | **opus**, by per-spawn override — the code is what the cycle delivers |
| Slice review, 4e.5 final check — **Claude route** | `agent-engineering:sdd-workhorse` | sonnet |
| Each panel specialist (Stage 1) with a shipped agent — `security`, `agent-security`, `performance`, `data-modeling`, `api-contract`, `module-depth`, `reliability`, `slice-integrity` | `agent-engineering:sdd-spec-<panel>-specialist` | sonnet |
| Any other panel value — today `accessibility`, `privacy`, `cost` | `agent-engineering:sdd-workhorse`, with `bodies/panel-specialist.md` and the panel value | sonnet |
| Panel synthesis (Stage 2) | `agent-engineering:sdd-critical-reviewer` | opus |
| Spec critical review (3d), the 3e.5 check of the spec fix, the feature code review (4b) — **Claude route** | `agent-engineering:sdd-critical-reviewer` | opus |
| Design brief — first draft and every revision (2.5a, 2.5c) | `agent-engineering:sdd-workhorse` | **opus**, by per-spawn override — the one planning document a person reads |
| The successor of any step above after a Mid-Phase Handoff (`bodies/continue.md`) | the agent type that step's row gives, with that row's override | that step's model — a critical review, the feature code review, a panel synthesis, or a design brief is finished on Opus |

A workhorse that needs Opus depth says "needed Opus depth" in its bounded return, and the orchestrator re-spawns it at Opus.
