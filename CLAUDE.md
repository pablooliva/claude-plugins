# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project Overview

A Claude Code Plugin Marketplace. Three plugins ship from this repo:

- **sdd** — Specification-Driven Development methodology (Research → Planning → Implementation).
- **pace** — Personal Agent Context Engineering for non-coding work (Research → Planning → Execution).
- **agent-engineering** — Cross-cutting skills for disciplined AI-assisted development (correction codification, ADR capture, regression eval scaffolding, SDD flow orchestration).

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

### Skill-based plugin (`agent-engineering`)
```
agent-engineering/
├── .claude-plugin/plugin.json
├── commands/                       # adr-capture.md, regression-eval-capture.md
├── skills/                         # correction-codifier, cross-cutting-adr,
│                                   # improve-claude-md, sdd-flow
└── README.md
```
No `hooks/`, no phase workflow. Functionality is delivered through skills the user (or `sdd-flow`) invokes at decision points.

## How It Works

1. Commands are markdown files containing prompts; users invoke them via `/command-name`.
2. Skills are invoked through the Skill tool when their description matches the task.
3. SDD and PACE register a `SubagentStop` hook that runs `hooks/log_subagent_call.py` to capture subagent transcripts.
4. Model routing (sdd/pace): Research uses Opus; Planning/Implementation/Execution use Sonnet.

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
/plugin install https://github.com/poliva83/claude-plugins sdd
/plugin install https://github.com/poliva83/claude-plugins pace
/plugin install https://github.com/poliva83/claude-plugins agent-engineering
```

See `plugin-installation-scope.md` for system-wide vs project-level installation.
