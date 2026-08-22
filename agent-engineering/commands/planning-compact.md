# Planning Progress Compaction

Interactive entry point for compacting an active **planning** phase. The full instruction set lives in this plugin's `sdd-flow` skill and is shared with the orchestrated flow — this command runs it in your own session instead of a spawned subagent.

## 1. Resolve the body path

Resolve `SKILL_ROOT` = this plugin's `skills/sdd-flow` directory, in this order:

1. `${CLAUDE_PLUGIN_ROOT}/skills/sdd-flow`
2. **Plugin cache:** `~/.claude/plugins/cache/pablooliva/agent-engineering/<latest-version>/skills/sdd-flow` (highest version dir)
3. **Dev/repo checkout:** the `agent-engineering/skills/sdd-flow` directory of the working repo

The body is `SKILL_ROOT/bodies/planning-compact.md`. If it cannot be found, say so and fall back to `/adhoc-compact` rather than improvising a template.

## 2. Read the body and adapt its framing

Read the body in full, then follow it — **with these substitutions**, because you are the main conversation, not a spawned subagent:

- **Ignore the spawned-subagent preamble.** There is no orchestrator, no prompt-supplied artifact paths (resolve them yourself from `SDD/`), no Reads-counter safety-net, and no flat-orchestration ban — you may use whatever tools the task needs.
- **Ignore the ≤100-word return contract** and the closing "the orchestrator will spawn a continuation agent" line. Report to the user instead (step 4 below).
- **Keep everything else verbatim**: the compaction file path and naming, the document template, and the `progress.md` append rules.

## 3. Rotate `progress.md` if oversized

Apply the same ~500-line rotation as `/adhoc-compact` step 4: archive completed-feature history and resolved blocks to `SDD/orchestration/progress-archive/`, keep a bounded `## Current State` carrying canonical phase-state lines verbatim, and carry any pending `## Awaiting *` / `## PARTIAL*` blocks (prefix match) forward verbatim as the latest blocks. Everything kept in the live file stays byte-identical.

## 4. Hand back to the user

Report the compaction file path and where the specification work stopped, then tell the user to `/clear` (or start a fresh session) and run `/continue`, which will find the compaction record and resume.
