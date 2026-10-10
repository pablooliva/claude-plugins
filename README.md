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

### 2. Personal Agent Context Engineer (PACE) — v3.0.0

Context management for Claude Code as a personal agent. PACE keeps Claude operating within optimal context limits (<40%) on non-coding tasks by saving in-progress work to disk and resuming it in a fresh session.

**Key Features:**

- `/compact` — writes a compaction file and progress tracker for whatever work is in progress
- `/continue` — reloads that state in a new session
- `/commit` — saves work to version control

### 3. Agent Engineering — v3.8.1

Cross-cutting skills and commands for disciplined AI-assisted software development, based on JD Forsythe's [10 Claude Code Principles](https://jdforsythe.github.io/10-principles/). It provides both cross-cutting guardrail skills that compound quality over time (each independently usable in any session) **and** `sdd-flow`, a self-contained SDD lifecycle orchestrator. As of 1.0.0, `sdd-flow` is a permanent fork of the SDD methodology — it ships its own agents, hooks, and phase bodies, so the `sdd` plugin is **not** required at runtime.

**v3.11.0 highlights:** `sdd-flow`'s blind enforcement-site count stops producing new list differences every review round. The spec now carries a control register — one ID per rule, so the implementer and the blind counter no longer pick different ones; the diff compares places before labels; a missed site that a test already proves gets its row from the reviewer, with no fix round; and a green mutation at a site with an argued "not provable alone" row is no longer a finding.

**v3.10.0 highlights:** `worth-building` — asks whether a proposed piece of work should be built as planned at all: six questions (the cheapest run that could kill the idea and whether it comes first, the ceiling, the ratio of change to apparatus, what a user sees, rule or code, budget and tripwire) and one verdict — proceed, reorder, shrink, or stop. Run it at a design gate and again after the first slice.

**v3.8.0 highlights:** tracing inside `sdd-flow`. In an application that has the tracing foundation, the spec plans which entry points, model calls, and calls to other systems a feature has; each review, and a final check after the last fix, compares that plan with the call tree a real run recorded (`trace-tree.py` renders it). `observability-init` now also records every call to the application's own functions, with their values off unless asked for.

**v3.7.0 highlights:** `observability-init` — run once per application, it installs a tracing foundation built on OpenTelemetry (one bootstrap module, an entry-point test, a trace run, `SDD/OBSERVABILITY.md`) and proves it on the application; one tracing standard says what gets recorded and what never is. Traces go to Opik or Langfuse by changing two environment variables.

**v3.6.0 highlights:** the enforcement-site diff compares which places the two lists name, not how many rows each has.

**v3.5.0 highlights:** `sdd-flow` mirrors a feature's delivery tiers to BB tasks — one parent task per feature and one sub-task per tier, moved through in progress, in review, and done as the flow runs, with feedback left on the next tier's task copied back into the tier plan. A tracker project is created when the BB project has none, and the flow tells you whenever the mirror could not run.

**v3.4.0 highlights:** `sdd-flow` gains a design gate and tiered delivery. After research it writes a short design brief and stops — in supervised and autonomous mode alike — until you approve it with every question answered; the spec is then held to the brief, and departures are shown to you before any code is written. The brief proposes three tiers and builds Tier 1 unless you choose otherwise; each tier is its own cycle, started with `/sdd-flow --next-tier`.

**v3.3.0 highlights:** `simplicity-challenge` — challenges a proposal for doing or building too much before it is implemented, on two axes (what it does, how it is built), and reports the smallest version still worth using plus a table of cuts and what each would cost to add later. It applies one tier standard (Tier 1 POC-plus, Tier 2 Standard, Tier 3 Full; nothing is built ahead for a later tier) and only removes or defers — it never adds requirements, edits the target, or implements.

**v3.2.0 highlights:** two user-invoked skills adapted from [mattpocock/skills](https://github.com/mattpocock/skills) — `improve-codebase-architecture` surveys existing code for shallow modules that could become deep ones and reports candidates without editing anything; `retro` reads a whole development cycle (every session across `/clear`, plus the `SDD/` records) and proposes changes to the agent's environment. Module depth now has one definition across the plugin: leverage at the interface, judged with the deletion test.

**v3.1.0 highlights:** `rephrase` — restates the report at the end of a solution, phase, or cycle as four short sections (Done, Pending, Blocking, Next) and drops the rest; it adds no facts, re-runs nothing, and never trims a failure or a skipped step.

**v3.0.0 highlights:** a cleanup release — `todo-tidy`, `correction-codifier`, `worktree-create`, and LangSmith eval capture (`/regression-eval-capture`, `sdd-flow` Step 4g, `eval_required:`) are removed; `worktree-handoff` is rewritten as `worktree-merge` for BB IDE worktrees; and an abuse case with no test now blocks an agentic feature at review.

**v2.7.0 highlights:** the site diff now separates real misses from noise — disagreements on code a slice did not change are reported LOW and settled by the final feature-wide recount, escaped symbols key correctly, lettered slice IDs (`SLICE-005a`) are accepted, and both sides file sites by one shared, count-free conventions file.

**v2.6.0 highlights:** `sdd-flow` no longer takes the implementer's word that a control is closed — every control's enforcement sites carry per-site mutation evidence, and a blind, independent site count (a separate spawn that never sees the implementer's list) is diffed against it before any control can be marked Complete.

**v2.5.0 highlights:** `prompt-doctor` — grades a task prompt against a ten-component anatomy before you send it (grounding link, stakes, ranked priorities, hard constraints, hedged opinion, knowledge gaps, the one clear ask, early-exit permission, precise done-condition), names what each gap lets the model decide on its own, and never executes the prompt or invents your context.

**v2.1.0 highlights:** OWASP AI-agent security review, vendored as one control catalog with two entry points — the standalone `ai-agent-security-review` skill, and two `agent_security:`-gated hook points inside `sdd-flow` (spec panel value, code-review lens).

**v1.0.0 highlights:** `sdd-flow` became a self-contained fork — it no longer depends on the `sdd` plugin at runtime and ships its own forked agents, hooks, and per-phase bodies. It orchestrates both `whole-feature` and `per-slice` delivery modes end-to-end. (Later 1.0.x releases add post-review fixes and progress-log hygiene — rotation, archives, and bounded appends.)

**Key Features:**

- `cross-cutting-adr` skill — captures binding architectural decisions as numbered ADRs (Living Documentation)
- `improve-claude-md` skill — audits and trims `CLAUDE.md`/`AGENTS.md` files to focus on preferences and behavioral nudges
- `prompt-doctor` skill — diagnoses a task prompt before you send it against the ten-component anatomy, with quoted evidence per component and an opt-in rewrite built only from your own words
- `rephrase` skill — restates an end-of-work report as Done / Pending / Blocking / Next, without adding facts or doing new work
- `worth-building` skill — asks whether the work should be built as planned at all: the cheapest test that could kill the idea, the ceiling, the budget, and a tripwire; one verdict (proceed / reorder / shrink / stop)
- `simplicity-challenge` skill — cuts a proposal down before it is built: smallest useful version, cuts and deferrals by tier (POC-plus / Standard / Full) with their costs, and what was kept for safety; removes or defers only
- `ai-agent-security-review` skill — adversarial review of agentic systems against the OWASP AI Agent Security Cheat Sheet (tool least-privilege, prompt injection, memory security, human-in-the-loop, output guardrails, multi-agent trust, adversarial testing); runs standalone, and the same vendored catalog gates two hook points inside `sdd-flow`
- `bb-worktree-init` skill — one-time per repo: inspects the project and renders its bundled templates into the `.worktreeinclude` + `.env-setup.sh` (+ `.bb-env-setup.sh` symlink, optional teardown) contract that BB IDE needs, then validates it in a throwaway worktree
- `worktree-merge` skill — lands a worktree's committed work on the main line: syncs with the target branch inside the worktree, fast-forwards the target (or opens a PR), renumbers colliding SDD ADR/feature numbers on confirmation, surfaces git-ignored files that would be lost, and cleans up — leaving BB-managed worktrees for BB IDE to retire
- `sdd-flow` skill — self-contained orchestration of the full Research → Design gate → Planning → Implementation lifecycle via subagents (no SDD plugin required): you approve a short design brief before anything is specified, and features are delivered in tiers, smallest useful version first; in an application that has the tracing foundation, the calls a feature was planned to make are checked against what a real run recorded ([workflow diagram](agent-engineering/docs/sdd-flow-diagram.md))
- `/adr-capture` command — manual entry point for ADR capture
- `/prompt-doctor` command — manual entry point for prompt diagnosis

## Installation

To use these plugins with Claude Code, ensure you have Claude Code installed and configured, then reference this marketplace repository according to the Claude Code Plugins documentation.

## Plugin Installation Scope

Claude Code plugins can be installed either system-wide (globally available across all projects) or configured at the project level for team consistency. System-wide installation is ideal for personal preferences and tools you use across projects, while project-level configuration ensures all team members automatically get the same plugins when working on shared repositories.

For detailed information about installation options, benefits, and best practices, see the [Plugin Installation Scope Guide](./plugin-installation-scope.md).

## Author

Pablo Oliva (<p.o@pablooliva.de>)

## License

See LICENSE file for details.