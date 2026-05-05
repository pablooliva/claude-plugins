# Claude Code Plugins Marketplace

A collection of Claude Code plugins designed to enhance your development workflow with structured methodologies and intelligent task management.

## About

This repository hosts Claude Code plugins that extend the capabilities of Claude Code through custom commands and workflows. The plugins follow the [Claude Code Plugins](https://docs.claude.com/en/docs/claude-code/plugins) specification.

## Available Plugins

### 1. Spec-Driven Development (SDD) — v2.0.0

A comprehensive plugin that provides a standardized Specification-Driven Development methodology for consistent, high-quality software development practices. SDD ensures your projects follow a structured approach through research, planning, and implementation phases.

**v2.0.0 highlights:** Two delivery modes are now supported — `whole-feature` (default; behaves identically to 1.x) and `delivery_mode: per-slice` (new opt-in; vertical-thread implementation cycle with per-slice review, retrospective, and a learnings ledger). The directory layout was restructured (`SDD/prompts/` split into `SDD/implementation/` + `SDD/orchestration/`) and `PROMPT-XXX` was renamed to `IMPLEMENTATION-PLAN-XXX`. Run `/sdd-migrate-layout` once on existing repos. See the SDD plugin README for the full migration guide.

**Cross-plugin coupling:** SDD 2.0.0 requires `agent-engineering` 0.4.0 or later for `sdd-flow` orchestration; install the two together.

**Key Features:**

- Structured development workflow with research, planning, and implementation phases
- Two delivery modes — whole-feature (default) and per-slice (vertical-thread, with retrospectives + learnings ledger)
- Built-in code review and context management
- Automated commit message generation
- Progress monitoring and tracking

### 2. Personal Agent Context Engineer (PACE)

Context management for Claude Code as a personal agent. PACE keeps Claude operating within optimal context limits (<40%) while providing flexible research, planning, and execution workflows for non-coding tasks.

**Key Features:**

- Context-first design with intelligent compaction and session continuity
- Flexible workflows - use commands standalone or in sequence
- Research, planning, and execution phases for any task type
- Produces deliverables: documents, reports, analysis, plans

### 3. Agent Engineering — v0.4.0

Cross-cutting skills and commands for disciplined AI-assisted software development, based on JD Forsythe's [10 Claude Code Principles](https://jdforsythe.github.io/10-principles/). Complements the SDD plugin — SDD provides the workflow, agent-engineering provides the guardrails that compound quality over time. Each skill is independently usable in any session.

**v0.4.0 highlights:** The `sdd-flow` skill now orchestrates both `whole-feature` and `per-slice` delivery modes end-to-end (per-slice support added in 0.4.0). Requires SDD plugin 2.0.0 or later; SDD 2.0.0 + agent-engineering 0.4.0 should be installed together (a version mismatch surfaces FAIL-009 silent-misbehavior in mixed installs).

**Key Features:**

- `correction-codifier` skill — turns mid-session corrections into durable `CLAUDE.md` rules (Institutional Memory)
- `cross-cutting-adr` skill — captures binding architectural decisions as numbered ADRs (Living Documentation)
- `sdd-flow` skill — orchestrates the full Research → Planning → Implementation lifecycle via subagents
- `/regression-eval-capture` command — scaffolds LangSmith regression eval datasets after a feature ships (Observability)
- `/adr-capture` command — manual entry point for ADR capture

## Installation

To use these plugins with Claude Code, ensure you have Claude Code installed and configured, then reference this marketplace repository according to the Claude Code Plugins documentation.

## Plugin Installation Scope

Claude Code plugins can be installed either system-wide (globally available across all projects) or configured at the project level for team consistency. System-wide installation is ideal for personal preferences and tools you use across projects, while project-level configuration ensures all team members automatically get the same plugins when working on shared repositories.

For detailed information about installation options, benefits, and best practices, see the [Plugin Installation Scope Guide](./plugin-installation-scope.md).

## Author

Pablo Oliva (<p.o@pablooliva.de>)

## License

See LICENSE file for details.