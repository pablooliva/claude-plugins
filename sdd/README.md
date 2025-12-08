# Specification-Driven Development (SDD) Plugin for Claude Code

A [Claude Code plugin](https://docs.claude.com/en/docs/claude-code/plugins) that provides a comprehensive methodology for systematic software development through research, planning, and implementation phases.

## Spec-Driven Development + Context Engineering

This plugin ensures consistent, high-quality development practices with intelligent context management, manual context compaction, and automated workflows, leveraging Claude's strengths while minimizing its weaknesses.

This software engineering methodology is based on:

1. [The New Code — Sean Grove, OpenAI](https://www.youtube.com/watch?v=8rABwKRsec4)
2. [Advanced Context Engineering for Agents](https://youtu.be/IS_y40zY-hc?si=5u3ajN073rCu7f88)

An example of this process being used: [video](https://www.youtube.com/watch?v=zNZs19fIDHk) and [repo](https://github.com/ai-that-works/ai-that-works/tree/main/2025-10-14-no-vibes-allowed)

## Prerequisites

- **Python 3.9 or higher** - Required for the plugin's SubagentStop hook, which uses modern Python type hints (`dict[str, Any]`) introduced in Python 3.9

## Installation

Install from a marketplace:

```bash
/plugin install pablooliva/sdd
```

This will install the plugin system-wide, making it available in all your projects.

Or alternatively, install the plugin at the project level by following the instructions in [plugin-installation-scope.md](plugin-installation-scope.md).

## Overview

The Specification-Driven Development (SDD) plugin transforms how you work with Claude Code by providing:

- **Three-Phase Development Methodology**: Structured research, planning, and implementation workflow
- **Intelligent Context Management**: Automatic tracking and optimization to prevent session overload
- **Model-Optimized Phases**: Leverages Claude Opus for research and Claude Sonnet for planning/implementation
- **Automated Documentation**: Generates research documents, specifications, and progress tracking
- **Built-in Code Review**: Ensures implementations match specifications

## What is Specification-Driven Development?

SDD is a systematic approach that ensures features are thoroughly researched, properly specified, and correctly implemented. Each phase is optimized for different aspects of development:

1. **Research Phase** (Claude Opus) - Deep codebase investigation and pattern analysis
2. **Planning Phase** (Claude Sonnet) - Technical specification and design documentation
3. **Implementation Phase** (Claude Sonnet) - Code development following specifications

### Phase Usage + Workflow Management = Success

Each phase is managed by the user according to this SDD workflow.

## SDD Workflow Overview

It is important to keep the context window below 40%. This MUST be done with human interaction.. YOU!

```text
PHASE START          CONTEXT ~40%           SAVE WORK          CLEAR SESSION
    │                     │                     │                   │
    ▼                     ▼                     ▼                   ▼
[/start] ──────────► [/compact] ──────────► [/commit] ──────────► [/clear]
                          │                                         │
                          └── Creates ────────┐                     │
                              progress.md &   │                     │
                              compaction file │                     │
                                              │                     │
                                              ▼                     ▼
                                                               FRESH START
                                                                    │
                                                                    ▼
                                                              [/continue]
                                                                    │
                                              ┌─────────────────────────┘
                                              │ Reads both files
                                              │ (progress.md &
                                              │  compaction file)
                                              ▼
                                         [/complete]
                                              │
                                              ▼
                                          [/commit]
```

This workflow represents the complete development cycle:

- **Start**: Begin with `/start` for any phase (research/planning/implementation)
- **Compact**: When context approaches 40%, use `/compact` to compress session
- **Commit**: Save your work with `/commit` before clearing the session
- **Continue**: Resume work with `/continue` in a fresh session
- **Complete**: Finalize the current phase with `/complete`
- **Commit**: Create final commits with `/commit`

### Context Monitoring

Run this command/utility in a terminal window separate from where Claude Code is running. The idea is to run both terminal windows, utility & Claude Code, in parallel. The command below will show you the amount of context used, `Usage` is the 3rd column. Make sure you are tracking the correct session by matching the session displayed in your current Claude Code terminal window: use `/status` to see match the session id.

NOTE: after running `/clear` Claude Code will launch a new session in the background. Track the new and matching session id for context usage.

#### Context Monitoring Utility

```bash
CCCONTEXT_WINDOW_SIZE=200000 npx github:pablooliva/cccontext#add-configurable-context-window sessions --live
```

### Phase Progression

Each phase in the SDD workflow builds upon the previous:

```text
┌─────────────────────────────────────────────────────────────────┐
│                     RESEARCH PHASE (Opus)                       │
│  • Deep codebase exploration                                    │
│  • Pattern identification                                       │
│  • Architecture understanding                                   │
│  Output: SDD/research/RESEARCH-XXX-[feature].md                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PLANNING PHASE (Sonnet)                      │
│  • Convert research to specifications                           │
│  • Design implementation approach                               │
│  • Define acceptance criteria                                   │
│  Output: SDD/requirements/SPEC-XXX-[feature].md                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 IMPLEMENTATION PHASE (Sonnet)                   │
│  • Write code following specifications                          │
│  • Implement tests                                              │
│  • Ensure quality standards                                     │
│  Output: Implemented feature + tests                            │
└─────────────────────────────────────────────────────────────────┘
```

## Core Commands

### Starting a Development Cycle

```bash
# Begin research on a new feature
/research-start

# Create specifications from research
/planning-start

# Start implementation from specifications
/implementation-start
```

### Managing Long Sessions

When context approaches 40%, use compaction commands to continue working:

```bash
# Compact and continue research
/research-compact

# Compact and continue planning
/planning-compact

# Compact and continue implementation
/implementation-compact
```

### Completing Phases

```bash
# Finalize research documentation
/research-complete

# Finalize specification
/planning-complete

# Complete implementation
/implementation-complete
```

### Utility Commands

```bash
# Resume work after clearing session
/continue

# Check current context utilization
/context-check

# Monitor progress across all phases
/monitor

# Review code against specifications
/code-review

# Create commits following conventions
/commit
```

## Workflow Example

### Complete Feature Development

1. **Start Research** (with Claude Opus):

   ```bash
   /research-start
   # Describe the feature you want to research
   ```

2. **Manage Context** (when approaching 40%):

   ```bash
   /research-compact
   /commit
   /clear
   /continue
   ```

3. **Complete Research**:

   ```bash
   /research-complete
   /commit
   ```

4. **Create Specification** (switch to Claude Sonnet):

   ```bash
   /planning-start
   # Review and refine the specification
   ```

5. **Implement Feature**:

   ```bash
   /implementation-start
   # Code is developed following the specification
   ```

6. **Review and Finalize**:

   ```bash
   /code-review
   /implementation-complete
   /commit
   ```

## Directory Structure

The plugin automatically creates and manages the following structure in your project:

```text
project/
└── SDD/                          # Root directory for all SDD artifacts
    ├── research/                 # Research phase documents
    │   └── RESEARCH-XXX-*.md     # Detailed investigation findings
    ├── requirements/             # Planning phase specifications
    │   └── SPEC-XXX-*.md         # Technical specifications
    └── prompts/                  # Session management
        ├── implementation-complete/  # Archived implementations
        └── context-management/   # Progress tracking
            ├── progress.md       # Current phase progress
            ├── *.compact.md      # Compacted session data
            └── subagent-calls/   # Subagent interaction logs
```

## Key Features

### Context Management

The plugin maintains <40% context utilization to ensure:

- Sufficient headroom for complex operations
- Effective subagent utilization
- Prevention of context overflow errors

### Automated Progress Tracking

- Automatic session compaction when context grows
- Progress persistence across session clears
- Seamless continuation of interrupted work

### Model Optimization

- **Research**: Uses Claude Opus for deep understanding
- **Planning/Implementation**: Uses Claude Sonnet for efficiency
- **Automatic Switching**: Commands handle model selection

### Documentation Generation

- Research documents capture codebase understanding
- Specifications define implementation requirements
- Progress files track session state
- Subagent calls are automatically logged

## Best Practices

### When to Use Full SDD Workflow

Use the complete three-phase workflow for:

- New features requiring research
- Complex architectural changes
- Breaking changes to existing functionality
- Features with unclear requirements

### Quick Implementation

For simple, well-understood changes:

- Skip directly to `/implementation-start`
- Provide clear requirements in the initial prompt

### Context Management Strategy

- Check context regularly with `/context-check`
- Compact proactively before hitting 40%
- Use `/continue` to resume seamlessly

### Commit Workflow

The `/commit` command ensures:

- Conventional Commits specification
- Proper co-authorship attribution
- Reference to specifications and research
- Clear change history

## Plugin Configuration

### Hooks

The plugin includes an automatic subagent logging hook that tracks all subagent interactions for debugging and progress monitoring.

## Version History

- **1.0.0** - Initial release with complete SDD methodology

## Support

For issues, feature requests, or questions:

- Create an issue in the plugin repository
- Check the [Claude Code documentation](https://docs.claude.com/en/docs/claude-code/plugins)

## License

This plugin is provided as-is for use with Claude Code. See the repository for license details.

---

**Built for Claude Code** - Enhancing AI-assisted development with a specification-driven systematic methodology.
