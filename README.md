# Claude Code Plugins Marketplace

A collection of Claude Code plugins designed to enhance your development workflow with structured methodologies and intelligent task management.

## About

This repository hosts Claude Code plugins that extend the capabilities of Claude Code through custom commands and workflows. The plugins follow the [Claude Code Plugins](https://docs.claude.com/en/docs/claude-code/plugins) specification.

## Available Plugins

### 1. Spec-Driven Development (SDD) — v2.2.0

A comprehensive plugin that provides a standardized Specification-Driven Development methodology for consistent, high-quality software development practices. SDD ensures your projects follow a structured approach through research, planning, and implementation phases.

**Delivery modes:** Two are supported — `whole-feature` (default) and `delivery_mode: per-slice` (opt-in; vertical-thread implementation cycle with per-slice review, retrospective, and a learnings ledger). The 2.0.0 release restructured the directory layout (`SDD/prompts/` split into `SDD/implementation/` + `SDD/orchestration/`) and renamed `PROMPT-XXX` to `IMPLEMENTATION-PLAN-XXX`; run `/sdd-migrate-layout` once on repos created before 2.0.0. See the SDD plugin README for the full migration guide.

**Standalone by design:** SDD is a human-driven methodology you run via its slash commands — it does **not** require any other plugin. For the *agent-orchestrated* version of this lifecycle (subagents driving Research → Planning → Implementation with fresh context per phase), see the self-contained `sdd-flow` skill in the **Agent Engineering** plugin below.

**Key Features:**

- Structured development workflow with research, planning, and implementation phases
- Two delivery modes — whole-feature (default) and per-slice (vertical-thread, with retrospectives + learnings ledger)
- Built-in code review and context management
- Automated commit message generation
- Progress monitoring and tracking

### 2. Personal Agent Context Engineer (PACE) — v2.0.0

Context management for Claude Code as a personal agent. PACE keeps Claude operating within optimal context limits (<40%) while providing flexible research, planning, and execution workflows for non-coding tasks.

**Key Features:**

- Context-first design with intelligent compaction and session continuity
- Flexible workflows - use commands standalone or in sequence
- Research, planning, and execution phases for any task type
- Produces deliverables: documents, reports, analysis, plans

### 3. Agent Engineering — v1.0.3

Cross-cutting skills and commands for disciplined AI-assisted software development, based on JD Forsythe's [10 Claude Code Principles](https://jdforsythe.github.io/10-principles/). It provides both cross-cutting guardrail skills that compound quality over time (each independently usable in any session) **and** `sdd-flow`, a self-contained SDD lifecycle orchestrator. As of 1.0.0, `sdd-flow` is a permanent fork of the SDD methodology — it ships its own agents, hooks, and phase bodies, so the `sdd` plugin is **not** required at runtime.

**v1.0.0 highlights:** `sdd-flow` became a self-contained fork — it no longer depends on the `sdd` plugin at runtime and ships its own forked agents, hooks, and per-phase bodies. It orchestrates both `whole-feature` and `per-slice` delivery modes end-to-end. (Later 1.0.x releases add post-review fixes and progress-log hygiene — rotation, archives, and bounded appends.)

**Key Features:**

- `correction-codifier` skill — turns mid-session corrections into durable `CLAUDE.md` rules (Institutional Memory)
- `cross-cutting-adr` skill — captures binding architectural decisions as numbered ADRs (Living Documentation)
- `improve-claude-md` skill — audits and trims `CLAUDE.md`/`AGENTS.md` files to focus on preferences and behavioral nudges
- `sdd-flow` skill — self-contained orchestration of the full Research → Planning → Implementation lifecycle via subagents (no SDD plugin required)
- `/regression-eval-capture` command — scaffolds LangSmith regression eval datasets after a feature ships (Observability)
- `/adr-capture` command — manual entry point for ADR capture

### 4. LangSmith Skills — v0.1.1

Three skills that drive the [`langsmith` CLI](https://github.com/langchain-ai/langsmith-cli) to trace, build evaluation datasets for, and evaluate **your own** LLM applications. Distinct from the official `langsmith-tracing` plugin (which traces Claude Code sessions themselves) — the two are complementary and can both be installed.

**Key Features:**

- `langsmith-trace` skill — add tracing to an app, or query/export trace and run data
- `langsmith-dataset` skill — create, upload, and manage evaluation datasets
- `langsmith-evaluator` skill — build LLM-as-judge or custom-code evaluation pipelines

**Prerequisites:** the `langsmith` CLI binary and a `LANGSMITH_API_KEY`. See the [plugin README](./langsmith-skills/README.md) for setup.

## Installation

To use these plugins with Claude Code, ensure you have Claude Code installed and configured, then reference this marketplace repository according to the Claude Code Plugins documentation.

## Plugin Installation Scope

Claude Code plugins can be installed either system-wide (globally available across all projects) or configured at the project level for team consistency. System-wide installation is ideal for personal preferences and tools you use across projects, while project-level configuration ensures all team members automatically get the same plugins when working on shared repositories.

For detailed information about installation options, benefits, and best practices, see the [Plugin Installation Scope Guide](./plugin-installation-scope.md).

## Author

Pablo Oliva (<p.o@pablooliva.de>)

## License

See LICENSE file for details.