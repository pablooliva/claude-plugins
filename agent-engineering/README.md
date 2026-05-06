# agent-engineering

Cross-cutting skills and commands for disciplined AI-assisted software development, based on the [10 Claude Code Principles](https://jdforsythe.github.io/10-principles/) by JD Forsythe. Complements the SDD plugin in this marketplace, but each skill here is independently usable in any session.

## Philosophy

The SDD plugin provides a spec-driven development methodology. This plugin provides the *agent-engineering discipline* that operates across any methodology — feedback loops, institutional memory, specialist review, token economy, and observability. The two plugins compose cleanly: SDD gives you the workflow; agent-engineering gives you the guardrails that compound quality over time.

## Contents

### Skills

- **`correction-codifier`** — When you correct Claude's behavior mid-session, proposes a durable `Always|Never [X] BECAUSE [Y]` rule and appends it to the project's `CLAUDE.md`. Operationalizes Principle 5 (Institutional Memory).
- **`cross-cutting-adr`** — Captures cross-cutting architectural decisions (technology choices, conventions that bind future work) as numbered ADRs under `SDD/adr/`. Triggers on comparison-with-selection patterns, explicit invocation, or ambient detection of binding decisions. Operationalizes Principle 3 (Living Documentation).
- **`improve-claude-md`** — Audits `CLAUDE.md` (or `AGENTS.md`) and `CLAUDE.local.md` to strip discoverable content (tech stack, file maps, command references) and concentrate the file on preferences, behavioral nudges, and corrections that the agent cannot infer from code. Pairs with `correction-codifier`: corrections accumulate, this skill keeps the file lean. Mirrored from [pablooliva/claude-skills](https://github.com/pablooliva/claude-skills).
- **`sdd-flow`** — End-to-end SDD lifecycle orchestration. Drives Research → Planning → Implementation → Done via subagents, with optional integration of the other skills in this plugin at appropriate phase boundaries. Requires the SDD plugin. As of 0.4.0, Step 4 (implementation) is mode-aware: it routes by the spec's `delivery_mode:` frontmatter — `whole-feature` (default; existing single-pass behaviour, preserved bit-for-bit) or `per-slice` (new state machine that fans out into per-slice cycles, integrating the SDD plugin's `/slice-start`, `/slice-review`, `/slice-retro`, and `/slice-commit` commands; a rolling learnings ledger; the `--skip-slice-checkpoints` escape-hatch; and a re-planning halt).

### Commands

- **`/regression-eval-capture`** — After a feature ships, scaffolds a LangSmith regression eval dataset (evaluator stub, run function, follow-up task for populating golden examples). Operationalizes Principle 7 (Observability). Requires the `langsmith` CLI.
- **`/adr-capture`** — Manual entry point for the `cross-cutting-adr` skill.

## Dependencies

- **SDD plugin** (`sdd` in this marketplace) — required by `sdd-flow`; optional context for `cross-cutting-adr` (ADRs are written under `SDD/adr/`).
- **`langsmith` CLI** — required by `/regression-eval-capture`. Install: `curl -sSL https://raw.githubusercontent.com/langchain-ai/langsmith-cli/main/scripts/install.sh | sh`.

## Plugin dependencies

`/sdd-flow` depends on the **SDD plugin (≥ v2.2.0)** for two reasons:
1. SDD command bodies (`/sdd:research-start`, `/sdd:critical-review`, `/sdd:spec-review-panel`, `/sdd:planning-start`, `/sdd:implementation-start`, `/sdd:implementation-complete`, slice commands) are embedded into subagent prompts.
2. SDD ships the named subagent types `/sdd-flow` references at every spawn site — `sdd-critical-reviewer` (Opus) for the 5 critical-review spawns, `sdd-workhorse` (Sonnet) for the ~20 non-adversarial workhorse spawns, and the `sdd-spec-*-specialist` agents (Sonnet) for the panel-review nested specialists. Without SDD ≥ 2.2.0, those spawns fall back to `subagent_type=general-purpose` and inherit the parent's model, defeating the cost-routing intent.

Install the SDD plugin alongside `agent-engineering` for the intended behavior.

## Status

Version 0.6.0 — early, under active iteration.

### What's new in 0.4.0

- `sdd-flow` Step 4 is now mode-aware. Specs with `delivery_mode: per-slice` drive a new per-slice state machine (per-slice cycle: implement → review → retro → commit, optional slice-boundary checkpoints, rolling learnings ledger, re-planning halt). Specs with `delivery_mode: whole-feature` (the default) continue through the original single-pass implementation flow, preserved bit-for-bit.
- New arguments on `/sdd-flow`: `--skip-slice-checkpoints`, `--replan`, `--from-slice`, `--override-replan`. See the SDD plugin README's "Per-slice workflow" section for the full state-machine description and resume semantics.
- Updated artifact paths to match SDD 2.0.0's directory restructure (`SDD/implementation/`, `SDD/orchestration/`, `IMPLEMENTATION-PLAN-XXX-*.md`).

### Requires SDD plugin 2.0.0 or later

The `sdd-flow` skill in this release embeds command bodies and artifact paths that target SDD plugin 2.0.0. **Running 0.4.0 against an older SDD plugin (1.x) — or running an older 0.3.x agent-engineering against SDD 2.0.0 — will silently misbehave** (split-tree artifact writes, `delivery_mode: per-slice` flowing as `whole-feature`, no Step 4 state machine; FAIL-009 in the SDD spec). Both plugins install independently from the marketplace, so updating only one is plausible. To stay aligned:

```bash
/plugin install https://github.com/poliva83/claude-plugins sdd
/plugin install https://github.com/poliva83/claude-plugins agent-engineering
```

If you upgrade SDD to 2.0.0, also upgrade agent-engineering to 0.4.0 in the same step (and vice-versa). See the SDD plugin README's "Cross-plugin dependency" section for the matching cross-reference and the `/sdd-migrate-layout` migration helper.

### 0.3.0 and earlier

Initial releases of `correction-codifier`, `cross-cutting-adr`, `improve-claude-md`, `sdd-flow` (whole-feature only), and the `/regression-eval-capture` and `/adr-capture` commands.
