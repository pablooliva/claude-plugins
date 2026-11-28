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

## Why the safety-net is measured by a hook

A spawned subagent has no first-class way to read its own context utilization — the API returns token counts to the harness, not the model. Until 5.18.0 the subagent counted its own file Reads instead, and that count was neither trustworthy nor the right measure: the agent wrote it itself, so an overrun went unnoticed (a fallback reviewer read past its trigger and said so only in its review), and it counted files, not context — a SLICE-005 implementer used 13 of its 20 reads on the plugin's own reference files and tripped before writing any code, while a section read through `sed` counted the same as a whole file. The plugin's `PreToolUse` hook (`hooks/context_guard.py`) now measures what the harness knows: before each tool call of a spawn whose prompt names a counter file, it reads that subagent's transcript, takes the context size the API last reported, writes it to the counter file, and past the limit refuses every call but the handoff's. The subagent counts nothing, and the orchestrator reads the counter file to see how full a spawn got. The harness writes a turn's usage only after that turn's tool calls have run, so the hook measures the context as of the previous turn: a spawn can overshoot the limit by one turn's reading, and calls made together in a spawn's first turn are not measured. The limit leaves room for that. Because subagents do not spawn in this flow (a platform limit on Claude Code ≤2.1.171; a deliberate design rule from 2.1.172, which allows nesting to depth 5 — see `proposals/nested-subagents-analysis-2026-06-12.md`), each spawn's own transcript is the whole signal. The limit (120,000 tokens) is the number in the counter file as the orchestrator creates it, tunable without changing the protocol.
