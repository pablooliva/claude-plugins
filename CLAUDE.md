# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project Overview

A Claude Code Plugin Marketplace. Three plugins ship from this repo:

- **sdd** — Specification-Driven Development methodology (Research → Planning → Implementation).
- **pace** — Personal Agent Context Engineering for non-coding work (Research → Planning → Execution).
- **agent-engineering** — Cross-cutting skills for disciplined AI-assisted development (correction codification, ADR capture, regression eval scaffolding) plus `sdd-flow`, a **self-contained** SDD lifecycle orchestrator. As of 1.0.0, `sdd-flow` is a permanent fork of the SDD plugin's content — it ships its own agents, hooks, and phase bodies and does NOT depend on the `sdd` plugin at runtime. The `sdd` plugin remains a standalone, human-driven methodology for external users (frozen at 2.2.0; do not modify it to serve agent-engineering).

`.claude-plugin/marketplace.json` is the source of truth for what the marketplace exposes; each plugin's own `plugin.json` is the source of truth for its version and hooks.

## Plugin Structures

Two patterns in this repo — don't assume one applies to the other.

### Phase-based plugins (`sdd`, `pace`)
```
plugin/
├── .claude-plugin/plugin.json     # metadata + SubagentStop hook
├── commands/                       # phase + utility commands
├── hooks/log_subagent_call.py      # logs subagent transcripts
└── README.md
```
- **sdd commands** include the phase trio (`research|planning|implementation`-`{start,compact,complete}`), plus `research-clarify`, `implementation-test`, `critical-review`, `spec-review-panel`, `adhoc-compact`, `code-review`, `commit`, `context-check`, `continue`. No `monitor` command.
- **pace commands** use `execution-{start,complete}` (not implementation). Only one generic `compact.md`, no per-phase compact. Includes `monitor.md`.

### Skill + self-contained-orchestrator plugin (`agent-engineering`)
```
agent-engineering/
├── .claude-plugin/plugin.json      # metadata + SubagentStop hook (as of 1.0.0)
├── agents/                         # 9 forked subagent types sdd-flow spawns:
│                                   #   sdd-workhorse (sonnet), sdd-critical-reviewer (opus),
│                                   #   7× sdd-spec-*-specialist (sonnet)
├── hooks/log_subagent_call.py      # logs subagent transcripts
├── commands/                       # interactive (depth-0) commands the user runs:
│                                   #   adr-capture, regression-eval-capture, research-clarify,
│                                   #   critical-review, continue, adhoc-compact, commit
├── skills/
│   ├── sdd-flow/                   # SLIM SKILL.md orchestrator core +
│   │   ├── phases/                 #   per-phase chapters (setup, research, planning,
│   │   │                           #   implementation-whole-feature, implementation-per-slice, protocols)
│   │   └── bodies/                 #   complete instruction sets for spawned subagents (read by path)
│   ├── correction-codifier/, cross-cutting-adr/, improve-claude-md/
└── README.md
```
`sdd-flow` is the flow's single source of truth: the orchestrator (main conversation) spawns one subagent per step, passing each its body file BY PATH (never embedding content). Spawned subagents must not themselves spawn or invoke slash commands/skills (one-level nesting) — every body is pre-adapted for inline execution. NOTE: this was a platform limit on Claude Code ≤2.1.171; since 2.1.172 (2026-06-09) the platform allows nesting to depth 5, but the flat design is retained deliberately — do not refactor toward nesting without reading `proposals/nested-subagents-analysis-2026-06-12.md`. The other three skills are invoked by the user (or `sdd-flow`) at decision points.

## How It Works

1. Commands are markdown files containing prompts; users invoke them via `/command-name`.
2. Skills are invoked through the Skill tool when their description matches the task.
3. SDD, PACE, and agent-engineering each register a `SubagentStop` hook that runs `hooks/log_subagent_call.py` to capture subagent transcripts. (If both `sdd` and `agent-engineering` are installed, subagent stops are logged twice — harmless duplicates.)
4. Model routing (sdd/pace commands): Research uses Opus; Planning/Implementation/Execution use Sonnet. In `agent-engineering`'s `sdd-flow`, routing is carried by shipped agent frontmatter — `sdd-workhorse` and the `sdd-spec-*-specialist` agents are Sonnet; `sdd-critical-reviewer` is Opus.

## Development

- **Add a command**: drop a markdown file in the plugin's `commands/`. Filename → command name.
- **Add a skill** (agent-engineering only): create `skills/<name>/SKILL.md` with frontmatter (`name`, `description`).
- **Bump a version**: update both `<plugin>/.claude-plugin/plugin.json` *and* the matching entry in `.claude-plugin/marketplace.json`. They drift easily — check both.
- **Hooks**: Python 3.9+ (uses `dict[str, Any]`). Read JSON from stdin.

## Key Design Principles

- **Context budget**: phase-based plugins target <40% context utilization via compaction commands.
- **Markdown is the program**: command/skill files ARE the functionality.
- **Phase artifacts**: each phase writes outputs the next phase consumes (under `SDD/` or `PACE/`).
- **agent-engineering composes**: its skills slot into other workflows (notably `sdd-flow`) rather than running standalone.

## Plugin Installation

```
/plugin install https://github.com/pablooliva/claude-plugins sdd
/plugin install https://github.com/pablooliva/claude-plugins pace
/plugin install https://github.com/pablooliva/claude-plugins agent-engineering
```

See `plugin-installation-scope.md` for system-wide vs project-level installation.
