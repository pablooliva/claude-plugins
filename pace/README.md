# Personal Agent Context Engineering (PACE) Plugin for Claude Code

A [Claude Code plugin](https://docs.claude.com/en/docs/claude-code/plugins) that provides context management for Claude Code as a personal agent: save your working state before context runs out, then resume in a fresh session.

## Context Engineering First

The purpose of PACE is **context management** - keeping Claude Code operating within optimal context window limits (<40%) for best performance. It is not tied to a workflow: whatever non-coding work is in progress (research, planning, writing, analysis), `/compact` captures it and `/continue` picks it back up.

This methodology draws from:

1. [Advanced Context Engineering for Agents](https://youtu.be/IS_y40zY-hc?si=5u3ajN073rCu7f88)
2. Systematic approach to complex problem-solving
3. Knowledge management through markdown documentation

## Prerequisites

- **Python 3.9 or higher** - Required for the plugin's SubagentStop hook, which uses modern Python type hints (`dict[str, Any]`)

## Installation

Install from a marketplace:

```bash
/plugin marketplace add pablooliva/claude-plugins
/plugin install pace
```

This will install the plugin system-wide, making it available in all your projects.

Or alternatively, install the plugin at the project level by following the instructions in [plugin-installation-scope.md](../plugin-installation-scope.md).

## Commands

```bash
/compact             # Save context and prepare for session clear (works anytime)
/continue            # Resume work after clearing session
/commit              # Save work to version control
```

## Context Management Workflow

When context approaches 40%, compact and continue:

```text
[Working] ──► [Context ~40%] ──► /compact ──► [Clear session] ──► /continue
                                    │                                │
                                    └── Creates progress.md ────────► Reads
                                        & compaction file             both files
```

1. Run `/compact` to preserve your work
2. Clear the Claude Code session
3. Run `/continue` to resume where you left off

## Directory Structure

PACE creates and manages this structure in your project:

```text
project/
└── PACE/
    └── prompts/
        └── context-management/
            ├── progress.md          # Current progress
            ├── compacted-*.md       # Compaction files
            └── subagent-calls/      # Subagent logs
```

## Model Recommendations

Different work types benefit from different models:

| Work Type | Recommended Model | Why |
|-----------|------------------|-----|
| Research | Claude Opus | Deep investigation and synthesis |
| Planning | Claude Sonnet | Structured task breakdown |
| Execution | Claude Sonnet | Efficient deliverable creation |

`/continue` will suggest (not require) the appropriate model.

## Best Practices

- Check context regularly with Claude Code's built-in `/context`
- Compact proactively before hitting 40%
- Use `/continue` to resume after clearing

## Version History

- **3.0.0** - Reduced to context management: removed the research, planning, and execution phase commands plus `/context-check` and `/monitor`; `/continue` now resumes from `progress.md` and the compaction file only
- **2.0.0** - Refactored for flexibility: standalone commands, generic `/compact`, renamed implementation→execution, removed software-specific terminology
- **1.0.0** - Initial release adapted from SDD methodology

## Support

For issues, feature requests, or questions:

- Create an issue in the plugin repository
- Check the [Claude Code documentation](https://docs.claude.com/en/docs/claude-code/plugins)

## License

This plugin is provided as-is for use with Claude Code. See the repository for license details.

---

**Built for Claude Code** - Context-first personal agent assistance.
