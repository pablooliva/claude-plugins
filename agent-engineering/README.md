# agent-engineering

Cross-cutting skills and commands for disciplined AI-assisted software development, based on the [10 Claude Code Principles](https://jdforsythe.github.io/10-principles/) by JD Forsythe. Every skill and command here is independently usable in any session.

## Philosophy

This plugin provides the *agent-engineering discipline* that operates across any methodology — feedback loops, institutional memory, specialist review, token economy, and observability. Its flagship is `sdd-flow`: a self-contained, end-to-end Specification-Driven Development orchestrator that drives a feature from Research → Planning → Implementation → Done through subagents with a fresh context window per phase.

## Self-contained as of 1.0.0

`sdd-flow` is a **permanent fork** of the SDD plugin's content, adapted for orchestrated (subagent-driven) execution. It is the **single source of truth for the flow** and depends on nothing outside this plugin at runtime:

- **Phase bodies** — the complete instruction set each spawned subagent reads lives under `skills/sdd-flow/bodies/` (one file per phase/review/capture step). The orchestrator passes each body **by absolute path** ("read this first"); it never pastes body content into a prompt and never reads from the SDD plugin's cache.
- **Agents** — the nine routed subagent types ship in `agents/` (`sdd-workhorse` at Sonnet, the seven `sdd-spec-*-specialist` agents at Sonnet, `sdd-critical-reviewer` at Opus). Model routing is carried entirely by agent frontmatter — no runtime model switching.
- **Hook** — `hooks/log_subagent_call.py` logs subagent transcripts via a `SubagentStop` hook registered in this plugin's `plugin.json`.

**The SDD plugin is no longer required and need not be installed.** The SDD plugin remains frozen at 2.2.0 as a standalone, human-driven methodology for its external users; this fork diverges from it deliberately so each can evolve independently. Nothing in `sdd-flow` references `/sdd:` commands or the SDD plugin cache.

### Why a permanent fork (rather than depending on SDD)

Before 1.0.0, `sdd-flow` embedded SDD command bodies at runtime and relied on SDD's shipped agents. That coupling meant a version skew between the two plugins could silently misbehave, and the orchestrated path could not diverge from the interactive SDD commands even where orchestration demanded it (e.g., a subagent cannot spawn or invoke slash commands, so "delegate to an Explore subagent" instructions had to become inline work). Forking permanently removes the dependency, lets the flow own its own evolution, and lets the SDD plugin stay stable for the people who use it directly.

### Architecture (1.0.0)

- **One-level spawning.** Claude Code permits exactly one level of subagent nesting. Every spawn happens at the orchestrator (main-conversation) level; spawned subagents cannot spawn subagents and cannot invoke slash commands or skills. Every body is pre-adapted for inline execution.
- **Two-stage specialist panel.** During planning, the orchestrator spawns one specialist subagent per `review_panel:` value in parallel (Stage 1; each writes a `PANEL-FINDINGS-*` file), then one `sdd-critical-reviewer` synthesis subagent reads those files from disk and emits the verdict (Stage 2). The bounded fix-and-re-review loop (max 3 iterations, progress-stall halt) is unchanged.
- **Reads-only safety net.** A spawned subagent can never spawn, so there is no nested-subagent counter — the only safety-net signal is file Reads (default trigger >15; >20 for implementation chunks). On trip, the subagent compacts and hands off.
- **Per-slice authoring default.** The planning body sets `delivery_mode: per-slice` unless the feature yields fewer than 2 genuine vertical slices (then `whole-feature` with a one-line justification). The PARSE default (frontmatter absent → whole-feature) is unchanged for backward compatibility.
- **Progressive disclosure.** `SKILL.md` is a slim orchestrator core; per-phase detail lives in `skills/sdd-flow/phases/` (`setup`, `research`, `planning`, `implementation-whole-feature`, `implementation-per-slice`, `protocols`), read at each phase boundary.

## Contents

### Skills

- **`sdd-flow`** — Self-contained end-to-end SDD lifecycle orchestration (see above).
- **`correction-codifier`** — When you correct Claude's behavior mid-session, proposes a durable `Always|Never [X] BECAUSE [Y]` rule and appends it to the project's `CLAUDE.md`. Operationalizes Principle 5 (Institutional Memory).
- **`cross-cutting-adr`** — Captures cross-cutting architectural decisions as numbered ADRs under `SDD/adr/`. Triggers on comparison-with-selection patterns, explicit invocation, or ambient detection. Operationalizes Principle 3 (Living Documentation).
- **`improve-claude-md`** — Audits `CLAUDE.md`/`AGENTS.md` and `CLAUDE.local.md` to strip discoverable content and concentrate on preferences, behavioral nudges, and corrections. Mirrored from [pablooliva/claude-skills](https://github.com/pablooliva/claude-skills).

### Commands

These are **interactive commands you run yourself** (depth 0, so they may delegate to subagents):

- **`/adr-capture`** — Manual entry point for the `cross-cutting-adr` skill.
- **`/regression-eval-capture`** — After a feature ships, scaffolds a LangSmith regression eval dataset. Operationalizes Principle 7 (Observability). Requires the `langsmith` CLI.
- **`/research-clarify`** — Structured interview that externalizes your design concept before any codebase research. Satisfies the `sdd-flow` Step 1.5 clarification gate.
- **`/critical-review`** — Standalone adversarial review of a research doc, spec, or implementation.
- **`/continue`** — Resume an interrupted SDD session from `progress.md`.
- **`/adhoc-compact`** — Compact the current working context mid-phase.
- **`/commit`** — Commit conventions (no co-author attribution), including atomic per-slice commits.

## Coexisting with the SDD plugin

The SDD plugin is **optional and uninstallable** — `sdd-flow` does not need it. If you keep both installed:

- **Command-name disambiguation.** Several command names exist in both plugins (`/critical-review`, `/continue`, `/commit`, `/adhoc-compact`, `/research-clarify`). Claude Code may require the `/agent-engineering:` prefix (e.g. `/agent-engineering:critical-review`) to pick this plugin's copy.
- **Duplicate transcript logs.** Both plugins register a `SubagentStop` hook pointing at their own `log_subagent_call.py`. With both installed, each subagent stop is logged twice — harmless, just duplicate transcript entries.

## Other dependencies

- **`langsmith` CLI** — required by `/regression-eval-capture` and by `sdd-flow`'s eval-capture step (non-blocking: if absent, the flow logs a warning and continues). Install: `curl -sSL https://raw.githubusercontent.com/langchain-ai/langsmith-cli/main/scripts/install.sh | sh`.

## Status

Version 1.0.2.

### What's new in 1.0.2

- **Progress hygiene.** `progress.md` no longer grows unboundedly (it sits in the read path of nearly every spawn): feature-completion rotation archives a finished feature's history to `SDD/orchestration/progress-archive/`, leaving a one-line summary; a ~500-line size checkpoint fires at phase-boundary commits; pending halt blocks always carry forward verbatim (phase detection never scans archives). Subagent progress entries are bounded to ≤10 lines — narrative belongs in artifacts. The interactive `/adhoc-compact` and `/continue` commands apply the same rotation in manual sessions.

### What's new in 1.0.1

Post-review fixes to 1.0.0 (no behavioral redesign):

- **Per-slice tracker scaffolding.** New per-slice step 4a.0: the orchestrator spawns `bodies/implementation.md` in scaffold-only mode to create the IMPLEMENTATION-PLAN with its `## Slice Progress` table before the first slice (previously nothing created it, and `slice-start` would halt per FAIL-007). The body's per-slice branch is now explicitly scaffold-only — it never implements slices inline.
- **Interactive `research-clarify` model check stripped** (was carried over from the source verbatim).
- **Consistency fixes:** compaction files and the continuation body now agree on `## Continuation Priorities`; the default panel is enumerated (`security`, `performance`, `data-modeling`, `api-contract`, `module-depth`, + `slice-integrity` in per-slice mode); the tracker template regains its `## Context Management → Essential Files Loaded` section for handoffs; panel specialists return bounded severity counts; residual context-percentage fields replaced with Safety-Net wording; assorted stale labels and cross-references cleaned up.

### What's new in 1.0.0

- **Self-contained fork.** `sdd-flow` no longer depends on the SDD plugin; it ships its own phase bodies, agents, and hook. The SDD plugin is optional and uninstallable.
- **Progressive disclosure.** Slim `SKILL.md` orchestrator core; per-phase chapters under `phases/`; complete subagent instruction sets under `bodies/`.
- **Read-by-path spawning.** Bodies are passed by absolute path, never embedded — there is nothing to strip at runtime.
- **Two-stage specialist panel.** Parallel specialists write `PANEL-FINDINGS-*` files; a synthesis subagent reads them from disk and renders the verdict.
- **Reads-only safety net.** The nested-subagent counter is gone (subagents can't spawn); Reads is the whole signal (>15 default, >20 for implementation chunks).
- **Per-slice authoring default.** Planning favors `delivery_mode: per-slice`; whole-feature requires an explicit one-line justification.
- **Sonnet/Opus routing via shipped agents.** Routing lives in agent frontmatter; the orchestrator may escalate a single spawn via a per-spawn model override.
- **New interactive commands** forked in: `/research-clarify`, `/critical-review`, `/continue`, `/adhoc-compact`, `/commit`.

### History

- **0.4.0–0.6.0** — `sdd-flow` Step 4 became mode-aware (`delivery_mode: whole-feature` | `per-slice`), with the per-slice state machine, slice-boundary checkpoints, rolling learnings ledger, and re-planning halt. At the time this still depended on the SDD plugin (≥ 2.0.0) for embedded command bodies and shipped agents — a coupling 1.0.0 removes.
- **0.3.0 and earlier** — Initial releases of `correction-codifier`, `cross-cutting-adr`, `improve-claude-md`, `sdd-flow` (whole-feature only), and the `/regression-eval-capture` and `/adr-capture` commands.
