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
├── commands/                       # interactive (depth-0) commands the user runs:
│                                   #   adr-capture, prompt-doctor, research-clarify,
│                                   #   critical-review, continue, adhoc-compact, commit
├── skills/
│   ├── sdd-flow/                   # SLIM SKILL.md orchestrator core +
│   │   ├── phases/                 #   per-phase chapters (setup, research, planning,
│   │   │                           #   implementation-whole-feature, implementation-per-slice, protocols)
│   │   ├── bodies/                 #   complete instruction sets for spawned subagents (read by path);
│   │   │                           #   design-brief.md = the Step 2.5 design gate's brief, the one planning doc a human reads
│   │   ├── references/             #   enforcement-sites.md — control/site/mutation standard
│   │   └── scripts/                #   site-diff.py — orchestrator's deterministic site-count diff;
│   │                               #   tier-mirror.py — mirrors a feature's tier plan to BB tasks via the `bb` CLI
│   │                               #   (tests: python3 -m unittest discover -s scripts/tests)
│   ├── ai-agent-security-review/   # OWASP AI-agent control catalog (vendored) +
│   │                       #   standalone review; sdd-flow reads the same catalog
│   ├── prompt-doctor/          # ten-component agent-prompt diagnosis (catalog in references/)
│   ├── rephrase/               # restates an end-of-work report as Done / Pending / Blocking / Next
│   ├── simplicity-challenge/   # user-invoked: cuts a proposal down before it is built (function + structure);
│   │                       #   references/tiers.md is the plugin's ONE tier standard (tiers, floor, cut tests,
│   │                       #   tier-plan template) — anything that works in tiers reads it, never restates it
│   ├── improve-codebase-architecture/  # user-invoked survey of existing code for deepening candidates;
│   │                       #   references/codebase-design.md is the plugin's ONE depth standard
│   │                       #   (sdd-flow panel-specialist §4.5 + planning.md mirror it — change together)
│   ├── retro/              # user-invoked development-cycle retrospective (environment, not code);
│   │                       #   scripts/session-digest.py reads session transcripts across /clear
│   │                       #   (tests: python3 -m unittest discover -s scripts/tests)
│   ├── cross-cutting-adr/, improve-claude-md/,
│   │                       #   bb-worktree-init/, worktree-merge/
└── README.md
```
`sdd-flow` is the flow's single source of truth: the orchestrator (main conversation) spawns one subagent per step, passing each its body file BY PATH (never embedding content). Spawned subagents must not themselves spawn or invoke slash commands/skills (one-level nesting) — every body is pre-adapted for inline execution. NOTE: this was a platform limit on Claude Code ≤2.1.171; since 2.1.172 (2026-06-09) the platform allows nesting to depth 5, but the flat design is retained deliberately — do not refactor toward nesting without reading `proposals/nested-subagents-analysis-2026-06-12.md`. The other skills are invoked by the user (or `sdd-flow`) at decision points. `ai-agent-security-review` is dual-use: a standalone review, and the canonical control catalog that `sdd-flow` reads at two `agent_security:`-gated hook points (Step 3c panel value, Step 4b code-review lens).

## How It Works

1. Commands are markdown files containing prompts; users invoke them via `/command-name`.
2. Skills are invoked through the Skill tool when their description matches the task.
3. SDD, PACE, and agent-engineering each register a `SubagentStop` hook that runs `hooks/log_subagent_call.py` to capture subagent transcripts. (If both `sdd` and `agent-engineering` are installed, subagent stops are logged twice — harmless duplicates.)
4. Model routing (sdd commands): Research uses Opus; Planning/Implementation use Sonnet. pace's `continue` only recommends a model by work type. In `agent-engineering`'s `sdd-flow`, routing is carried by shipped agent frontmatter — `sdd-workhorse` and the `sdd-spec-*-specialist` agents are Sonnet; `sdd-critical-reviewer` is Opus. One exception: the design brief (Step 2.5) is written by `sdd-workhorse` with a per-spawn `opus` override.

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
