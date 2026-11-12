# Claude Code Plugins Marketplace

A collection of Claude Code plugins designed to enhance your development workflow with structured methodologies and intelligent task management.

## About

This repository hosts Claude Code plugins that extend the capabilities of Claude Code through custom commands and workflows. The plugins follow the [Claude Code Plugins](https://docs.claude.com/en/docs/claude-code/plugins) specification.

## Available Plugins

### 1. Spec-Driven Development (SDD) — v2.2.0

> **Superseded by `sdd-flow`.** This plugin is frozen at v2.2.0 and no longer developed: it still works, but new features and fixes go only into the `sdd-flow` skill in the **Agent Engineering** plugin below, which carries its own copy of this methodology. For new projects, use `sdd-flow`.

A comprehensive plugin that provides a standardized Specification-Driven Development methodology for consistent, high-quality software development practices. SDD ensures your projects follow a structured approach through research, planning, and implementation phases.

**Delivery modes:** Two are supported — `whole-feature` (default) and `delivery_mode: per-slice` (opt-in; vertical-thread implementation cycle with per-slice review, retrospective, and a learnings ledger). The 2.0.0 release restructured the directory layout (`SDD/prompts/` split into `SDD/implementation/` + `SDD/orchestration/`) and renamed `PROMPT-XXX` to `IMPLEMENTATION-PLAN-XXX`; run `/sdd-migrate-layout` once on repos created before 2.0.0. See the SDD plugin README for the full migration guide.

**Standalone by design:** SDD is a human-driven methodology you run via its slash commands — it does **not** require any other plugin. Its successor is the self-contained `sdd-flow` skill in the **Agent Engineering** plugin below: the same lifecycle, driven by subagents with fresh context per phase (Research → Planning → Implementation), and where all further development happens.

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

### 3. Agent Engineering — v4.1.0

Cross-cutting skills and commands for disciplined AI-assisted software development, based on JD Forsythe's [10 Claude Code Principles](https://jdforsythe.github.io/10-principles/). It provides both cross-cutting guardrail skills that compound quality over time (each independently usable in any session) **and** `sdd-flow`, a self-contained SDD lifecycle orchestrator. As of 1.0.0, `sdd-flow` is a permanent fork of the SDD methodology — it ships its own agents, hooks, and phase bodies, so the `sdd` plugin is **not** required at runtime.

**v4.1.0 highlights:** `sdd-flow` stops counting enforcement sites. One adversarial security check on Codex at the end of the feature reads every security rule for a path where it does not hold, and each gap is fixed with a test that fails without its guard (at most two rounds). LOW findings are listed for you, not fixed. Mutation checks run in a scratch copy outside the repository.

**v4.0.0 highlights:** `sdd-flow` has one way to run. Supervised and autonomous modes and the stop-skipping flags are gone; the flow stops only where you have something to decide or try — the clarification question, the design gate, a spec that departs from the brief, a pause after each slice to try it, an unresolved finding, and a sign-off. The final commit no longer waits for a yes, and Codex is the only second-model reviewer.

**v3.16.1 highlights:** `sdd-lite` — a light build path beside `sdd-flow`, for work one short interview can settle: you approve a one-page brief, it is built in the main conversation with tests, Codex reviews every change once (plus one check of the fixes), and only the brief, ADRs, glossary and a tier-plan line are kept. It tells you when the work needs `sdd-flow` instead ([diagram](agent-engineering/docs/sdd-lite-diagram.md)). Not yet exercised on a real build.

**v3.15.0:** faster `sdd-flow` slice re-reviews. A re-review after a fix round runs only the tests the fix can affect; the whole suite, and the trace check, run once at the end, when the re-review would pass the slice.

**v3.14.4:** eval cases name their spec (`SPEC-[###] REQ-XXX`); implementation is chunked only when the change is wide.

**v3.14.3:** the spec fix after the critical review is checked (3e.5); a design brief never promises an acceptance with no judged eval behind it.

**v3.14.2:** Codex reviews run with network access, carry no read limit, and a failed run is marked as failed.

**v3.14.1:** a next-tier cycle is no longer split before its design brief cuts the tier.

**v3.14.0 highlights:** lighter `sdd-flow` reviews. A review after a fix round reads what the fix changed instead of the whole feature again, and the plugin's own template files in an application are no longer re-proven.

**v3.13.0 highlights:** from real use back into the next cycle. `observability-init` adds a trace lookup — find a real request's trace in Opik and print it as a call tree that ends where the failure started — and records the arguments of a call that failed. `/eval-harvest` turns answers you marked wrong in Opik into invented eval cases that fail the same way; you approve each, and the next cycle's design brief adopts it, defers it to a later tier, or drops it.

**v3.12.0 highlights:** evals inside `sdd-flow`. In an application that has the tracing foundation, a feature with a model in it is checked on what the model really answers: the spec writes the cases out before any code, the implementer builds them, and before each review the flow puts every case to the running application three times. A case checked by rule blocks like a failing test; a case scored by a judge model blocks nothing — you accept it at the final commit, the one reason that step stops. Runs go to Opik, one experiment per review.

**v3.10.0 highlights:** `worth-building` — asks whether a proposed piece of work should be built as planned at all: six questions (the cheapest run that could kill the idea and whether it comes first, the ceiling, the ratio of change to apparatus, what a user sees, rule or code, budget and tripwire) and one verdict — proceed, reorder, shrink, or stop. Run it at a design gate and again after the first slice.

**v3.8.0 highlights:** tracing inside `sdd-flow`. In an application that has the tracing foundation, the spec plans which entry points, model calls, and calls to other systems a feature has; each review, and a final check after the last fix, compares that plan with the call tree a real run recorded (`trace-tree.py` renders it). `observability-init` now also records every call to the application's own functions, with their values off unless asked for.

**v3.7.0 highlights:** `observability-init` — run once per application, it installs a tracing foundation built on OpenTelemetry (one bootstrap module, an entry-point test, a trace run, `SDD/OBSERVABILITY.md`) and proves it on the application; one tracing standard says what gets recorded and what never is. Traces go to Opik or Langfuse by changing two environment variables.

**v3.5.0 highlights:** `sdd-flow` mirrors a feature's delivery tiers to BB tasks — one parent task per feature and one sub-task per tier, moved through in progress, in review, and done as the flow runs, with feedback left on the next tier's task copied back into the tier plan. A tracker project is created when the BB project has none, and the flow tells you whenever the mirror could not run.

**v3.4.0 highlights:** `sdd-flow` gains a design gate and tiered delivery. After research it writes a short design brief and stops until you approve it with every question answered; the spec is then held to the brief, and departures are shown to you before any code is written. The brief proposes three tiers and builds Tier 1 unless you choose otherwise; each tier is its own cycle, started with `/sdd-flow --next-tier`.

**v3.3.0 highlights:** `simplicity-challenge` — challenges a proposal for doing or building too much before it is implemented, on two axes (what it does, how it is built), and reports the smallest version still worth using plus a table of cuts and what each would cost to add later. It applies one tier standard (Tier 1 POC-plus, Tier 2 Standard, Tier 3 Full; nothing is built ahead for a later tier) and only removes or defers — it never adds requirements, edits the target, or implements.

**v3.2.0 highlights:** two user-invoked skills adapted from [mattpocock/skills](https://github.com/mattpocock/skills) — `improve-codebase-architecture` surveys existing code for shallow modules that could become deep ones and reports candidates without editing anything; `retro` reads a whole development cycle (every session across `/clear`, plus the `SDD/` records) and proposes changes to the agent's environment. Module depth now has one definition across the plugin: leverage at the interface, judged with the deletion test.

**v3.1.0 highlights:** `rephrase` — restates the report at the end of a solution, phase, or cycle as four short sections (Done, Pending, Blocking, Next) and drops the rest; it adds no facts, re-runs nothing, and never trims a failure or a skipped step.

**v3.0.0 highlights:** a cleanup release — `todo-tidy`, `correction-codifier`, `worktree-create`, and LangSmith eval capture (`/regression-eval-capture`, `sdd-flow` Step 4g, `eval_required:`) are removed; `worktree-handoff` is rewritten as `worktree-merge` for BB IDE worktrees; and an abuse case with no test now blocks an agentic feature at review.

**v2.5.0 highlights:** `prompt-doctor` — grades a task prompt against a ten-component anatomy before you send it (grounding link, stakes, ranked priorities, hard constraints, hedged opinion, knowledge gaps, the one clear ask, early-exit permission, precise done-condition), names what each gap lets the model decide on its own, and never executes the prompt or invents your context.

**v2.1.0 highlights:** OWASP AI-agent security review, vendored as one control catalog with two entry points — the standalone `ai-agent-security-review` skill, and two `agent_security:`-gated hook points inside `sdd-flow` (spec panel value, code-review lens).

**v1.0.0 highlights:** `sdd-flow` became a self-contained fork — it no longer depends on the `sdd` plugin at runtime and ships its own forked agents, hooks, and per-phase bodies. It orchestrates both `whole-feature` and `per-slice` delivery modes end-to-end. (Later 1.0.x releases add post-review fixes and progress-log hygiene — rotation, archives, and bounded appends.)

**Key Features:**

- `cross-cutting-adr` skill — captures binding architectural decisions as numbered ADRs (Living Documentation)
- `improve-claude-md` skill — audits and trims `CLAUDE.md`/`AGENTS.md` files to focus on preferences and behavioral nudges
- `prompt-doctor` skill — diagnoses a task prompt before you send it against the ten-component anatomy, with quoted evidence per component and an opt-in rewrite built only from your own words
- `rephrase` skill — restates an end-of-work report as Done / Pending / Blocking / Next, without adding facts or doing new work
- `sdd-lite` skill — the light path: an interview only for what is open, one approved brief, the build in the main conversation, one Codex review of every change, and a close-out of decision records, glossary and brief; points to `sdd-flow` when the work needs it ([diagram](agent-engineering/docs/sdd-lite-diagram.md))
- `worth-building` skill — asks whether the work should be built as planned at all: the cheapest test that could kill the idea, the ceiling, the budget, and a tripwire; one verdict (proceed / reorder / shrink / stop)
- `simplicity-challenge` skill — cuts a proposal down before it is built: smallest useful version, cuts and deferrals by tier (POC-plus / Standard / Full) with their costs, and what was kept for safety; removes or defers only
- `ai-agent-security-review` skill — adversarial review of agentic systems against the OWASP AI Agent Security Cheat Sheet (tool least-privilege, prompt injection, memory security, human-in-the-loop, output guardrails, multi-agent trust, adversarial testing); runs standalone, and the same vendored catalog gates three hook points inside `sdd-flow`
- `bb-worktree-init` skill — one-time per repo: inspects the project and renders its bundled templates into the `.worktreeinclude` + `.env-setup.sh` (+ `.bb-env-setup.sh` symlink, optional teardown) contract that BB IDE needs, then validates it in a throwaway worktree
- `worktree-merge` skill — lands a worktree's committed work on the main line: syncs with the target branch inside the worktree, fast-forwards the target (or opens a PR), renumbers colliding SDD ADR/feature numbers on confirmation, surfaces git-ignored files that would be lost, and cleans up — leaving BB-managed worktrees for BB IDE to retire
- `sdd-flow` skill — self-contained orchestration of the full Research → Design gate → Planning → Implementation lifecycle via subagents (no SDD plugin required): you approve a short design brief before anything is specified, and features are delivered in tiers, smallest useful version first; in an application that has the tracing foundation, the calls a feature was planned to make are checked against what a real run recorded, and what a model in the feature really answers is checked against cases written in the spec; at the end, a second model reads every security rule for a way around it, and low-severity findings are listed for you rather than fixed ([workflow diagram](agent-engineering/docs/sdd-flow-diagram.md))
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