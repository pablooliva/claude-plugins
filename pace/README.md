# Personal Agent Context Engineering (PACE) Plugin for Claude Code

A [Claude Code plugin](https://docs.claude.com/en/docs/claude-code/plugins) that provides intelligent context management for Claude Code as a personal agent, with flexible research, planning, and execution workflows.

## Context Engineering First

The primary purpose of PACE is **context management** - keeping Claude Code operating within optimal context window limits (<40%) for best performance. Secondary to that, it provides structured workflows for:

- Research and information gathering
- Task planning and breakdown
- Producing deliverables (documents, reports, analysis)

This methodology draws from:

1. [Advanced Context Engineering for Agents](https://youtu.be/IS_y40zY-hc?si=5u3ajN073rCu7f88)
2. Systematic approach to complex problem-solving
3. Knowledge management through markdown documentation

## Prerequisites

- **Python 3.9 or higher** - Required for the plugin's SubagentStop hook, which uses modern Python type hints (`dict[str, Any]`)

## Installation

Install from a marketplace:

```bash
/plugin install pablooliva/pace
```

This will install the plugin system-wide, making it available in all your projects.

Or alternatively, install the plugin at the project level by following the instructions in [plugin-installation-scope.md](../plugin-installation-scope.md).

## Flexible Workflow

PACE commands work **standalone or in sequence**. Use what you need:

```text
┌─────────────────────────────────────────────────────────────────┐
│  FLEXIBLE USAGE - Use any command standalone or in sequence     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  /research-start ──► /research-complete                         │
│        │                                                        │
│        ▼ (optional)                                             │
│  /planning-start ──► /planning-complete                         │
│        │                                                        │
│        ▼ (optional)                                             │
│  /execution-start ──► /execution-complete                       │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  CONTEXT MANAGEMENT - Use anytime context gets high             │
│                                                                 │
│  [Any work] ──► /compact ──► [Clear session] ──► /continue      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Examples of flexible usage:**

- Research only: `/research-start` → `/research-complete` (done)
- Skip to execution: `/execution-start` → `/execution-complete`
- Full workflow: Research → Planning → Execution
- Just need to compact: `/compact` → clear → `/continue`

## Commands

### Research Phase

```bash
/research-start      # Begin research on a topic
/research-complete   # Finalize research findings
```

### Planning Phase

```bash
/planning-start      # Create an action plan
/planning-complete   # Finalize the plan
```

### Execution Phase

```bash
/execution-start     # Start producing deliverables
/execution-complete  # Finalize deliverables
```

### Context Management

```bash
/compact             # Save context and prepare for session clear (works anytime)
/continue            # Resume work after clearing session
/context-check       # Check current context utilization
/monitor             # View context monitoring tools
```

### Utility

```bash
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
    ├── research/                    # Research documents
    │   └── RESEARCH-XXX-*.md
    ├── plans/                       # Plan documents
    │   └── PLAN-XXX-*.md
    ├── deliverables/                # Execution outputs
    │   └── [documents, reports, etc.]
    └── prompts/
        ├── EXECUTION-XXX-*.md       # Execution tracking
        └── context-management/
            ├── progress.md          # Current progress
            ├── compacted-*.md       # Compaction files
            ├── archive/             # Archived progress files
            └── subagent-calls/      # Subagent logs
```

## Model Recommendations

Different work types benefit from different models:

| Work Type | Recommended Model | Why |
|-----------|------------------|-----|
| Research | Claude Opus | Deep investigation and synthesis |
| Planning | Claude Sonnet | Structured task breakdown |
| Execution | Claude Sonnet | Efficient deliverable creation |

Commands will suggest (not require) the appropriate model.

## Use Cases

### Research Projects

- Gather information from multiple sources
- Synthesize findings into comprehensive documents
- Build reference materials

### Task Planning

- Break down complex tasks into actionable steps
- Identify resources and risks
- Define success criteria

### Document Creation

- Produce reports, analysis, and summaries
- Create structured documentation
- Develop decision frameworks

### Knowledge Management

- Research and organize information
- Create structured documentation
- Build personal knowledge bases

## Best Practices

### Manage Context

- Check context regularly with `/context-check`
- Compact proactively before hitting 40%
- Use `/continue` to resume seamlessly after clearing

### Use Flexibly

- Use only the phases you need
- Skip directly to `/execution-start` for simple tasks
- Research can be the entire task (not just a phase)

### Start New Tasks

- When starting unrelated work, archive previous progress
- Start commands will ask if you want to archive existing progress.md

## Version History

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
