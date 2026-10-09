# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project Overview

A Claude Code Plugin Marketplace. Three plugins ship from this repo:

- **sdd** — Specification-Driven Development methodology (Research → Planning → Implementation).
- **pace** — Personal Agent Context Engineering for non-coding work (compact → clear session → continue).
- **agent-engineering** — Cross-cutting skills for disciplined AI-assisted development (ADR capture, agent-prompt diagnosis, AI-agent security review) plus `sdd-flow`, a **self-contained** SDD lifecycle orchestrator. As of 1.0.0, `sdd-flow` is a permanent fork of the SDD plugin's content — it ships its own agents, hooks, and phase bodies and does NOT depend on the `sdd` plugin at runtime. The `sdd` plugin remains a standalone, human-driven methodology for external users (frozen at 2.2.0; do not modify it to serve agent-engineering).

`.claude-plugin/marketplace.json` is the source of truth for what the marketplace exposes; each plugin's own `plugin.json` is the source of truth for its version and hooks.

## Plugin Structures

Two patterns in this repo — don't assume one applies to the other.

### Command plugins (`sdd`, `pace`)
```
plugin/
├── .claude-plugin/plugin.json     # metadata + SubagentStop hook
├── commands/                       # phase + utility commands
├── hooks/log_subagent_call.py      # logs subagent transcripts
└── README.md
```
- **sdd commands** include the phase trio (`research|planning|implementation`-`{start,compact,complete}`), plus `research-clarify`, `implementation-test`, `critical-review`, `spec-review-panel`, `adhoc-compact`, `code-review`, `commit`, `context-check`, `continue`. No `monitor` command.
- **pace commands** are only `compact`, `continue`, `commit` — no phase commands (removed in 3.0.0). One generic `compact.md`.

### Skill + self-contained-orchestrator plugin (`agent-engineering`)
```
agent-engineering/
├── .claude-plugin/plugin.json      # metadata + SubagentStop hook (as of 1.0.0)
├── agents/                         # 10 forked subagent types sdd-flow spawns:
│                                   #   sdd-workhorse (sonnet), sdd-critical-reviewer (opus),
│                                   #   8× sdd-spec-*-specialist (sonnet)
├── hooks/log_subagent_call.py      # logs subagent transcripts
├── docs/sdd-flow-diagram.md        # human-facing picture of the sdd-flow cycle — update it when a step or a stop changes
├── docs/observability-diagram.md    # picture of the tracing-and-evals proposal (proposals/observability-and-evals-2026-10-04.md) — build steps 1 (observability-init) and 2 (tracing in sdd-flow) exist, evals and eval-harvest do not; update it as each build step ships
├── commands/                       # interactive (depth-0) commands the user runs:
│                                   #   adr-capture, prompt-doctor, research-clarify,
│                                   #   critical-review, continue, commit, and four compact commands
│                                   #   (adhoc-compact + research/planning/implementation-compact) that
│                                   #   share ONE contract with continue: file under SDD/orchestration/compacted/,
│                                   #   its path recorded in progress.md (adhoc Skip: handed to the user instead),
│                                   #   a `## Continuation Priorities` section,
│                                   #   a pending `## Awaiting` block kept latest — change one, check all five
├── skills/
│   ├── sdd-flow/                   # SLIM SKILL.md orchestrator core +
│   │   ├── phases/                 #   per-phase chapters (setup, research, planning,
│   │   │                           #   implementation-whole-feature, implementation-per-slice, protocols)
│   │   ├── bodies/                 #   complete instruction sets for spawned subagents (read by path);
│   │   │                           #   design-brief.md = the Step 2.5 design gate's brief, the one planning doc a human reads
│   │   ├── references/             #   enforcement-sites.md — control/site/mutation standard;
│   │   │                           #   second-model-review.md — the ONE definition of who runs a review (a second model family via
│   │   │                           #   its CLI, marked fallback to the Claude reviewer agents); phase chapters point to it, never restate it;
│   │   │                           #   test-integrity.md — the ONE definition of a real test and of the reviews' Test Integrity Lens
│   │   │                           #   (implementer bodies read §1; code review, slice review, impl critical review run it; fixers follow §7);
│   │   │                           #   tracing-lens.md — the ONE definition of the reviews' trace check (slice review,
│   │   │                           #   code review, and the 4e.5 verification read it; never restate it in a body)
│   │   └── scripts/                #   site-diff.py — orchestrator's deterministic site-count diff;
│   │                               #   second-model-review.py — settles the cycle's reviewer and runs one review step on codex/opencode;
│   │                               #   tier-mirror.py — mirrors a feature's tier plan to BB tasks via the `bb` CLI;
│   │                               #   trace-tree.py — renders a trace run's span file as call trees and call counts
│   │                               #   (loads observability-init/scripts/check-span-file.py by path — keep both in step)
│   │                               #   (tests: python3 -m unittest discover -s scripts/tests)
│   ├── ai-agent-security-review/   # OWASP AI-agent control catalog (vendored) +
│   │                       #   standalone review; sdd-flow reads the same catalog
│   ├── prompt-doctor/          # ten-component agent-prompt diagnosis (catalog in references/)
│   ├── rephrase/               # restates an end-of-work report as Done / Pending / Blocking / Next
│   ├── simplicity-challenge/   # user-invoked: cuts a proposal down before it is built (function + structure);
│   │                       #   references/tiers.md is the plugin's ONE tier standard (tiers, floor, cut tests,
│   │                       #   tier-plan template) — anything that works in tiers reads it, never restates it
│   ├── worth-building/     # user-invoked: asks whether the work should be built as planned at all — six questions
│   │                       #   (kill test, ceiling, ratio, what a user sees, rule or code, budget and tripwire) and one
│   │                       #   verdict (proceed / reorder / shrink / stop); references/questions.md is the standard,
│   │                       #   references/worked-example.md the case it came from. Run before simplicity-challenge;
│   │                       #   sdd-flow names it at the design gate and after a plan's first slice — a reminder, it never runs it
│   ├── improve-codebase-architecture/  # user-invoked survey of existing code for deepening candidates;
│   │                       #   references/codebase-design.md is the plugin's ONE depth standard
│   │                       #   (sdd-flow panel-specialist §4.5 + planning.md mirror it — change together)
│   ├── observability-init/ # user-invoked, once per application, never during an sdd-flow cycle: installs the tracing
│   │                       #   foundation from templates/ (Python only) and proves it on the app;
│   │                       #   foundation includes a hook that records every call to the app's own functions (Python 3.12+);
│   │                       #   references/tracing.md is the plugin's ONE tracing standard — sdd-flow reads it when a
│   │                       #   cycle's `tracing` gate is on, never restates it
│   │                       #   (tests: python3 -m unittest discover -s scripts/tests — the hook test is skipped without
│   │                       #   Python 3.12 + opentelemetry-sdk; to run it, from the skill's directory:
│   │                       #   uv run --python 3.12 --with opentelemetry-sdk python -m unittest discover -s scripts/tests)
│   ├── retro/              # user-invoked development-cycle retrospective (environment, not code);
│   │                       #   scripts/session-digest.py reads session transcripts across /clear
│   │                       #   (tests: python3 -m unittest discover -s scripts/tests)
│   ├── cross-cutting-adr/, improve-claude-md/,
│   │                       #   bb-worktree-init/, worktree-merge/
└── README.md
```
`sdd-flow` is the flow's single source of truth: the orchestrator (main conversation) spawns one subagent per step, passing each its body file BY PATH (never embedding content). `SKILL.md` states three rules that every edit to a body or phase file is checked against: a body's only inputs are the paths in its prompt (it never lists a folder to find them, never commits, never writes a stop note beyond the two it is allowed); only the orchestrator declares a phase done, and every stop that waits for an answer has a halt block, a resume rule in `phases/protocols.md`, and a row in the diagram; and every slice state change, stop, and commit has an owner in `phases/implementation-per-slice.md`'s owner table. Spawned subagents must not themselves spawn or invoke slash commands/skills (one-level nesting) — every body is pre-adapted for inline execution. NOTE: this was a platform limit on Claude Code ≤2.1.171; since 2.1.172 (2026-06-09) the platform allows nesting to depth 5, but the flat design is retained deliberately — do not refactor toward nesting without reading `proposals/nested-subagents-analysis-2026-06-12.md`. The other skills are invoked by the user (or `sdd-flow`) at decision points. `ai-agent-security-review` is dual-use: a standalone review, and the canonical control catalog that `sdd-flow` reads at two `agent_security:`-gated hook points (Step 3c panel value, Step 4b code-review lens). `observability-init` is tied to `sdd-flow` the same way: its tracing standard and the `SDD/OBSERVABILITY.md` it leaves in an application are what a cycle's `tracing` gate (decided once at 3c, recorded as `## Gates - tracing: on|off`) switches on — the planned call graph in the spec, the implementer's tracing step, and the Tracing Lens in the slice review, the code review, and the 4e.5 verification. With the gate off a cycle must behave exactly as it did before 3.8.0.

## How It Works

1. Commands are markdown files containing prompts; users invoke them via `/command-name`.
2. Skills are invoked through the Skill tool when their description matches the task.
3. SDD, PACE, and agent-engineering each register a `SubagentStop` hook that runs `hooks/log_subagent_call.py` to capture subagent transcripts. (If both `sdd` and `agent-engineering` are installed, subagent stops are logged twice — harmless duplicates.)
4. Model routing (sdd commands): Research uses Opus; Planning/Implementation use Sonnet. pace's `continue` only recommends a model by work type. In `agent-engineering`'s `sdd-flow`, routing is carried by shipped agent frontmatter — `sdd-workhorse` and the `sdd-spec-*-specialist` agents are Sonnet; `sdd-critical-reviewer` is Opus. One exception: the design brief (Step 2.5) is written by `sdd-workhorse` with a per-spawn `opus` override. As of 3.9.0 the review steps do not use that routing first: each is run on a second model family through its CLI (`skills/sdd-flow/references/second-model-review.md`), and the reviewer agents are the marked fallback.

## Development

- **Add a command**: drop a markdown file in the plugin's `commands/`. Filename → command name.
- **Add a skill** (agent-engineering only): create `skills/<name>/SKILL.md` with frontmatter (`name`, `description`).
- **Bump a version**: update both `<plugin>/.claude-plugin/plugin.json` *and* the matching entry in `.claude-plugin/marketplace.json`. They drift easily — check both.
- **Hooks**: Python 3.9+ (uses `dict[str, Any]`). Read JSON from stdin.

## Key Design Principles

- **Context budget**: `sdd` and `pace` target <40% context utilization via compaction commands.
- **Markdown is the program**: command/skill files ARE the functionality.
- **Phase artifacts**: each phase writes outputs the next phase consumes (under `SDD/`).
- **agent-engineering composes**: its skills slot into other workflows (notably `sdd-flow`) rather than running standalone.

## Plugin Installation

```
/plugin install https://github.com/pablooliva/claude-plugins sdd
/plugin install https://github.com/pablooliva/claude-plugins pace
/plugin install https://github.com/pablooliva/claude-plugins agent-engineering
```

See `plugin-installation-scope.md` for system-wide vs project-level installation.
