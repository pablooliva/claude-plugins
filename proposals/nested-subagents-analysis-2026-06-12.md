# Nested Subagents in Claude Code — Analysis & Refactor Reference

**Status:** Reference analysis — refactor deliberately deferred. sdd-flow stays flat.
**Date:** 2026-06-12 (evidence gathered live on Claude Code 2.1.174, macOS)
**Affects:** `agent-engineering/` plugin (`sdd-flow` skill, shipped agents, README), `CLAUDE.md`.
**Author of intent:** Pablo Oliva. Drafted with Claude.

---

## What changed

The agent-engineering 1.0.0 fork (commit `3a24132`) was architected around a hard
platform constraint: Claude Code permitted exactly one level of subagent nesting —
the Agent/Task tool was inert inside spawned subagents. On **2026-06-09 Boris Cherny
shipped Claude Code v2.1.172**, announcing on X
([post](https://x.com/bcherny/status/2064327225504403752)): "Just landed nested
subagent support in Claude Code. Capped at depth=5 to start. Lmk what you think!"

The official changelog entry
([anthropics/claude-code CHANGELOG.md](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md),
v2.1.172) is one line:

> "Sub-agents can now spawn their own sub-agents (up to 5 levels deep)"

Stated motivation: "agents kicking off agents as a way to better manage context" —
each nested subagent runs in its own isolated window and returns only a summary.
The depth-5 cap is explicitly "to start," with open solicitation of feedback —
i.e., **the semantics are provisional**.

## Documentation state (as of 2026-06-12)

The changelog and the live behavior agree; **the prose docs do not**. The official
[sub-agents page](https://code.claude.com/docs/en/sub-agents) (fetched 2026-06-12)
still asserts the OLD constraint in at least four places:

1. Plan-mode section: "This prevents infinite nesting (subagents cannot spawn other subagents)"
2. Tool-restriction section: "Subagents cannot spawn other subagents, so `Agent(agent_type)` has no effect in subagent definitions"
3. Chaining section: "Subagents cannot spawn other subagents. If your workflow requires nested delegation, use Skills or chain subagents from the main conversation"
4. Fork-mode section: "A fork cannot spawn further forks"

Anyone checking the docs for confirmation finds the opposite claim. Re-check these
four passages when evaluating stabilization (see checklist below).

## Empirical verification (Claude Code 2.1.174, 2026-06-12)

**Test design:** from a main conversation (depth 0), spawn a depth-1 subagent
instructed to (a) report whether an Agent/Task tool is in its tool list, (b) use it
to spawn a depth-2 `Explore` child with a trivial "reply PONG" prompt, (c) report
the verbatim outcome.

**PASS — named subagent type.** Parent spawned as `agent-engineering:sdd-workhorse`
(a plugin-shipped named type): Agent tool present in its tool list; the depth-2
`Explore` child executed and returned `PONG` without error. Nested spawning
genuinely works, including from plugin-defined agent types at depth 1.

**FAIL — `general-purpose` type (2/2 reproductions).** The same test prompt
spawned with `subagent_type: general-purpose` failed identically twice: the
subagent replied

> "It looks like your message came through empty — just the system reminders, no visible content. What would you like to do next?"

— i.e., **the spawn prompt was never delivered** to the agent. Both runs: ~11–12 s,
`tool_uses: 1`, no error surfaced to the caller. The failure is silent from the
orchestrator's side: the Agent call "succeeds" and returns the confused reply as if
it were a result.

**Hypothesis (unconfirmed):** fork-mode staged rollout. The sub-agents docs state
that from v2.1.161 fork behavior may be default-enabled ("Claude spawns a fork
whenever it would otherwise use the general-purpose subagent. Named subagents such
as Explore still spawn as before"), and a fork inherits the parent conversation
rather than starting from a prompt. The observed symptom — agent sees conversation
context ("system reminders") but no user message — is consistent with the fork path
dropping the spawn prompt. Matches the docs' named-vs-general-purpose split exactly:
named types worked, `general-purpose` did not.

**Operational rule until resolved: prefer named subagent types over
`general-purpose` for anything load-bearing, and treat a subagent reply of
"your message came through empty" as a spawn-delivery failure, not an agent answer.**

Not yet tested: spawning at depths 3–5; whether a fork can spawn named children;
plugin-type resolution at depth ≥2; SubagentStop hook behavior for grandchildren.

## Why sdd-flow stays flat (for now)

1. **The feature is provisional.** "Capped at depth=5 to start" + open feedback call
   + stale docs = semantics may shift. Re-architecting on it now repeats the
   original mistake in reverse.
2. **Flat orchestration retains real advantages** that were never just workarounds:
   every spawn is visible to the orchestrator; all state flows through
   `progress.md` (rotation, halt blocks, Mid-Phase Handoff all assume
   orchestrator-mediated writes); the structure is deterministic and auditable.
   A depth-2 grandchild's transcript, failures, and Read-count discipline are
   invisible to the orchestrator.
3. **Observability is unverified at depth.** It is unknown whether the
   `SubagentStop` hook (`hooks/log_subagent_call.py`) fires for nested children,
   and the Reads-only safety net has no counter contract below depth 1.

## What nesting could unlock (refactor candidates, in rough value order)

- **Panel collapse (Step 3c).** The Opus synthesis agent could spawn the per-domain
  specialists itself, turning the two-stage orchestrator dance (parallel specialists
  → PANEL-FINDINGS files → synthesis spawn) into a single spawn. Keep the
  PANEL-FINDINGS files as the audit artifact regardless.
- **Restore delegation inside bodies.** The 1.0.0 fork's largest adaptation was
  rewriting "delegate to an Explore subagent" instructions into inline Grep/Glob
  work. With nesting, bodies could delegate discovery again — reducing Read-counter
  pressure and keeping worker contexts cleaner.
- **Implementation chunk fan-out.** An implementation subagent could parallelize
  independent sub-tasks instead of serializing them or bouncing splits back to the
  orchestrator ("surface a split recommendation" return path becomes optional).
- **Safety-net redesign.** A nested-subagent counter becomes meaningful again; the
  Reads-only rationale in `phases/protocols.md` would need rework (delegated Reads
  don't land in the parent's context, changing what the counter measures).
- **Mid-Phase Handoff.** A tripped worker could hand off to a sibling it spawns
  itself rather than returning to the orchestrator — though this trades away the
  orchestrator's checkpointing and is probably NOT desirable even when stable.

## Stabilization checklist — gate criteria before any refactor

Re-evaluate when ALL of these hold:

- [ ] Official sub-agents docs updated to describe nesting (the four stale passages above corrected).
- [ ] Depth-cap semantics unchanged across ~2–3 months of releases (no cap change, no behavioral rework).
- [ ] `general-purpose` empty-message failure resolved (re-run the empirical test above, both named and general-purpose).
- [ ] `SubagentStop` hook verified to fire for depth ≥2 spawns (else `log_subagent_call.py` silently loses coverage).
- [ ] Plugin agent types (`agent-engineering:*`) resolvable from inside nested children.
- [ ] Cost/permission semantics at depth understood (model routing, permission prompts, token attribution).

## Where the old constraint is annotated (2026-06-12 sweep)

The one-level rule is now stated as a *design contract with a version note*, not a
platform fact, in: `CLAUDE.md` (sdd-flow paragraph), `agent-engineering/README.md`
(Architecture: One-level spawning, Reads-only safety net),
`skills/sdd-flow/SKILL.md` (one-level-spawning contract section + spawn-obligation
paragraph), `skills/sdd-flow/phases/protocols.md` (count-based safety-net
rationale), `agents/sdd-workhorse.md` + `agents/sdd-critical-reviewer.md`
(prohibitions replacing "the tool is inert"), and all 19 `skills/sdd-flow/bodies/*.md`
boilerplate headers ("Do not spawn… the flow's flat-orchestration contract forbids
it"). The frozen `sdd/` plugin (2.2.0) was not touched. README changelog entries
for 1.0.0 retain the original wording as historical record.

## Sources

- [Claude Code CHANGELOG.md](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) — v2.1.172 entry
- [Sub-agents docs](https://code.claude.com/docs/en/sub-agents) — stale passages quoted above
- [Boris Cherny's announcement](https://x.com/bcherny/status/2064327225504403752) (X returns 402 to fetchers; corroborated via secondary coverage)
- [Digg coverage of the release](https://digg.com/ai/megudrsi)
- Empirical tests: this repo, 2026-06-12, Claude Code 2.1.174 (transcripts in session history)
