# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code Plugin Marketplace containing reusable plugins that extend Claude Code functionality. Two production plugins are available:

- **SDD (Specification-Driven Development)**: Systematic software development methodology
- **PACE (Personal Agent Context Engineering)**: General task management for non-coding work

Both plugins implement an identical three-phase workflow: Research → Planning → Implementation.

## Architecture

### Plugin Structure

Each plugin follows this structure:
```
plugin-name/
├── .claude-plugin/plugin.json    # Plugin metadata, hooks, keywords
├── commands/                     # Markdown command files (14 per plugin)
│   ├── research-{start,compact,complete}.md
│   ├── planning-{start,compact,complete}.md
│   ├── implementation-{start,compact,complete}.md
│   ├── continue.md, context-check.md, monitor.md
│   ├── code-review.md, commit.md
├── hooks/
│   └── log_subagent_call.py      # Subagent interaction logging
└── README.md
```

### How It Works

1. Commands are markdown files containing prompts executed by Claude Code
2. Users invoke commands via `/command-name` in the CLI
3. Hooks trigger on SubagentStop events for logging
4. Model routing: Research phases use Claude Opus; Planning/Implementation use Claude Sonnet

### Marketplace Definition

`.claude-plugin/marketplace.json` defines which plugins are available for installation.

## Development

### Adding a New Command

Create a markdown file in the plugin's `commands/` directory. The filename becomes the command name (e.g., `my-command.md` → `/my-command`).

### Modifying Plugin Metadata

Edit `.claude-plugin/plugin.json` to update name, version, description, keywords, or hooks.

### Hook Requirements

Python hooks require Python 3.9+ (uses modern type hints like `dict[str, Any]`). Hooks read JSON from stdin and process subagent transcripts.

## Key Design Principles

- **Context Management**: Both plugins target <40% context utilization via compaction commands
- **Documentation as Code**: Markdown command files ARE the functionality
- **Phase Transitions**: Each phase generates artifacts consumed by the next phase
- **Structured Output**: Plugins create dedicated directories (SDD/ or PACE/) for generated content

## Plugin Installation

Users install plugins via Claude Code CLI:
```
/plugin install https://github.com/poliva83/claude-plugins sdd
/plugin install https://github.com/poliva83/claude-plugins pace
```

See `plugin-installation-scope.md` for system-wide vs project-level installation guidance.
