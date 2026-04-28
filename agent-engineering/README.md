# agent-engineering

Cross-cutting skills and commands for disciplined AI-assisted software development, based on the [10 Claude Code Principles](https://jdforsythe.github.io/10-principles/) by JD Forsythe. Complements the SDD plugin in this marketplace, but each skill here is independently usable in any session.

## Philosophy

The SDD plugin provides a spec-driven development methodology. This plugin provides the *agent-engineering discipline* that operates across any methodology — feedback loops, institutional memory, specialist review, token economy, and observability. The two plugins compose cleanly: SDD gives you the workflow; agent-engineering gives you the guardrails that compound quality over time.

## Contents

### Skills

- **`correction-codifier`** — When you correct Claude's behavior mid-session, proposes a durable `Always|Never [X] BECAUSE [Y]` rule and appends it to the project's `CLAUDE.md`. Operationalizes Principle 5 (Institutional Memory).
- **`cross-cutting-adr`** — Captures cross-cutting architectural decisions (technology choices, conventions that bind future work) as numbered ADRs under `SDD/adr/`. Triggers on comparison-with-selection patterns, explicit invocation, or ambient detection of binding decisions. Operationalizes Principle 3 (Living Documentation).
- **`improve-claude-md`** — Audits `CLAUDE.md` (or `AGENTS.md`) and `CLAUDE.local.md` to strip discoverable content (tech stack, file maps, command references) and concentrate the file on preferences, behavioral nudges, and corrections that the agent cannot infer from code. Pairs with `correction-codifier`: corrections accumulate, this skill keeps the file lean. Mirrored from [pablooliva/claude-skills](https://github.com/pablooliva/claude-skills).
- **`sdd-flow`** — End-to-end SDD lifecycle orchestration. Drives Research → Planning → Implementation → Done via subagents, with optional integration of the other skills in this plugin at appropriate phase boundaries. Requires the SDD plugin.

### Commands

- **`/regression-eval-capture`** — After a feature ships, scaffolds a LangSmith regression eval dataset (evaluator stub, run function, follow-up task for populating golden examples). Operationalizes Principle 7 (Observability). Requires the `langsmith` CLI.
- **`/adr-capture`** — Manual entry point for the `cross-cutting-adr` skill.

## Dependencies

- **SDD plugin** (`sdd` in this marketplace) — required by `sdd-flow`; optional context for `cross-cutting-adr` (ADRs are written under `SDD/adr/`).
- **`langsmith` CLI** — required by `/regression-eval-capture`. Install: `curl -sSL https://raw.githubusercontent.com/langchain-ai/langsmith-cli/main/scripts/install.sh | sh`.

## Status

Version 0.3.0 — early, under active iteration.
