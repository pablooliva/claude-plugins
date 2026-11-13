# Protocols — Errors

Read this on any error. It applies across all phases.

The rare cases each have their own file, read only when the case happens:

- `phases/rare/resume.md` — `/sdd-flow continue`: Session Resumption, Phase Detection Priority, and the resume rule of every halt block.
- `phases/rare/handoff.md` — a subagent returns a "needs continuation" signal: the Mid-Phase Handoff.
- `phases/rare/rotation.md` — `progress.md` exceeds ~500 lines, or the feature-completion rotation: Progress Rotation.
- `phases/rare/replan.md` — the user asks for a re-plan at a slice pause.
- `phases/rare/next-tier.md` — `/sdd-flow --next-tier`.
- `phases/rare/decomposition.md` — Step 0 finds the scope too large for one cycle.

---

## Error Handling

**A second-model review run that fails is not handled here.** `references/second-model-review.md` §3 has its own rule — run once more, then that step on the Claude route, recorded and told to the user — and it never stops the flow. The rule below applies to subagents, the Claude-route reviewer included.

If a subagent fails or returns incomplete results, the orchestrator:
1. Logs the failure in `progress.md`.
2. Re-spawns the subagent with additional context about what went wrong.
3. If the same subagent fails twice, stops and informs the user.

---

## Why the safety-net is count-based, not percentage-based

A spawned subagent has no first-class way to read its own context utilization — `/usage` is a harness slash command available only to the top-level interactive Claude, and the API returns token counts to the harness, not the model. Any self-audit a subagent performs produces output tokens that land back in its own context, partially eating the budget it is trying to measure. Count-based triggers (file Reads) are nearly free to evaluate (rule application, not deliberation), are inspectable in the counter file, and don't require the subagent to know anything its harness won't tell it. Because subagents do not spawn in this flow (a platform limit on Claude Code ≤2.1.171; a deliberate design rule from 2.1.172, which allows nesting to depth 5 — see `proposals/nested-subagents-analysis-2026-06-12.md`), there is no nested-subagent count — Reads is the whole signal. Defaults (Reads >15, or >20 for implementation chunks) are tunable without changing the protocol.
