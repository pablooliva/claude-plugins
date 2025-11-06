# Personal Agent Context Engineering (PACE) Plugin for Claude Code

A [Claude Code plugin](https://docs.claude.com/en/docs/claude-code/plugins) that transforms Claude Code into a powerful personal agent for handling diverse non-coding tasks through structured research, planning, and implementation phases.

## Personal Agent + Context Engineering

This plugin enables Claude Code to function as a comprehensive personal agent, managing tasks ranging from research and documentation to project organization and decision-making, with intelligent context management and automated workflows.

This methodology adapts software engineering best practices for general task management:

1. [Advanced Context Engineering for Agents](https://youtu.be/IS_y40zY-hc?si=5u3ajN073rCu7f88)
2. Systematic approach to complex problem-solving
3. Knowledge management through markdown documentation

## Prerequisites

- **Python 3.9 or higher** - Required for the plugin's SubagentStop hook, which uses modern Python type hints (`dict[str, Any]`) introduced in Python 3.9

## Installation

Install from a marketplace:

```bash
/plugin install pablooliva/pace
```

This will install the plugin system-wide, making it available in all your projects.

Or alternatively, install the plugin at the project level by following the instructions in [plugin-installation-scope.md](plugin-installation-scope.md).

## Overview

The Personal Agent Context Engineering (PACE) plugin transforms Claude Code into a versatile personal agent by providing:

- **Three-Phase Task Methodology**: Structured research, planning, and implementation workflow for any task
- **Intelligent Context Management**: Automatic tracking and optimization to prevent session overload
- **Model-Optimized Phases**: Leverages Claude Opus for deep research and Claude Sonnet for planning/execution
- **Comprehensive Documentation**: Generates research documents, plans, and progress tracking
- **Flexible Task Handling**: From online research to document analysis to script creation

## What is Personal Agent Context Engineering?

PACE is a systematic approach that ensures tasks are thoroughly researched, properly planned, and correctly executed. Each phase is optimized for different aspects of task completion:

1. **Research Phase** (Claude Opus) - Deep investigation of information, documents, and online resources
2. **Planning Phase** (Claude Sonnet) - Task breakdown, strategy development, and resource planning
3. **Implementation Phase** (Claude Sonnet) - Task execution, documentation creation, and deliverable completion

## PACE Workflow Overview

```text
PHASE START          CONTEXT ~40%           SAVE WORK          CLEAR SESSION
    │                     │                     │                   │
    ▼                     ▼                     ▼                   ▼
[/start] ──────► [/compact] ──────► [/commit] ──────► [/clear]
                          │                                          │
                          └── Creates ────────┐                      │
                              progress.md &   │                      │
                              compaction file │                      │
                                              │                      │
                                              ▼                      ▼
                                                                FRESH START
                                                                     │
                                                                     ▼
                                                             [/continue]
                                                                     │
                                              ┌──────────────────────┘
                                              │ Reads both files
                                              │ (progress.md &
                                              │  compaction file)
                                              ▼
                                         [/complete]
                                              │
                                              ▼
                                         [/commit]
```

### Phase Progression

Each phase in the PACE workflow builds upon the previous:

```text
┌─────────────────────────────────────────────────────────────────┐
│                     RESEARCH PHASE (Opus)                       │
│  • Online research and fact-gathering                           │
│  • Document and file analysis                                   │
│  • Information synthesis and pattern identification             │
│  Output: PACE/research/RESEARCH-XXX-[topic].md                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PLANNING PHASE (Sonnet)                      │
│  • Convert research into actionable plans                       │
│  • Design task approach and methodology                         │
│  • Define success criteria and deliverables                     │
│  Output: PACE/plans/PLAN-XXX-[task].md                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 IMPLEMENTATION PHASE (Sonnet)                   │
│  • Execute planned tasks                                        │
│  • Create documentation and deliverables                        │
│  • Develop helper scripts if needed                            │
│  Output: Task deliverables + documentation                      │
└─────────────────────────────────────────────────────────────────┘
```

## Core Commands

### Starting a Task Cycle

```bash
# Begin research on a new topic or task
/research-start

# Create action plan from research
/planning-start

# Start executing the planned tasks
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

# Finalize task plan
/planning-complete

# Complete task implementation
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

# Review deliverables against plan
/review

# Save work and create documentation
/commit
```

## Workflow Examples

### Research Project Example

1. **Start Research** (with Claude Opus):
   ```bash
   /research-start
   # "I need to research best practices for personal knowledge management systems"
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

4. **Create Action Plan** (switch to Claude Sonnet):
   ```bash
   /planning-start
   # Review research and create implementation plan
   ```

5. **Execute Plan**:
   ```bash
   /implementation-start
   # Create documents, organize files, write helper scripts
   ```

### Document Organization Example

1. **Analyze Current State**:
   ```bash
   /research-start
   # "Analyze my project's markdown files and identify organization patterns"
   ```

2. **Plan Reorganization**:
   ```bash
   /planning-start
   # Create a detailed reorganization strategy
   ```

3. **Implement Changes**:
   ```bash
   /implementation-start
   # Reorganize files, create index documents, build navigation structure
   ```

## Directory Structure

The plugin automatically creates and manages the following structure in your project:

```text
project/
└── PACE/                         # Root directory for all PACE artifacts
    ├── research/                 # Research phase documents
    │   └── RESEARCH-XXX-*.md    # Detailed research findings
    ├── plans/                    # Planning phase documents
    │   └── PLAN-XXX-*.md        # Task plans and strategies
    ├── deliverables/            # Implementation outputs
    │   └── [various outputs]    # Documents, scripts, organized files
    └── prompts/                 # Session management
        ├── implementation-complete/  # Archived implementations
        └── context-management/   # Progress tracking
            ├── progress.md      # Current phase progress
            ├── *.compact.md     # Compacted session data
            └── subagent-calls/  # Subagent interaction logs
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

- Research documents capture findings and insights
- Plans define task approach and success criteria
- Progress files track session state
- Deliverables are organized and documented

## Best Practices

### When to Use Full PACE Workflow

Use the complete three-phase workflow for:
- Complex research projects
- Multi-step task planning
- Document organization projects
- Decision-making that requires research
- Creating comprehensive documentation

### Quick Tasks

For simple, well-understood tasks:
- Skip directly to `/implementation-start`
- Provide clear requirements in the initial prompt

### Context Management Strategy

- Check context regularly with `/context-check`
- Compact proactively before hitting 40%
- Use `/continue` to resume seamlessly

### Working with Existing Projects

When working in directories with existing content:
- Start with research phase to understand current state
- Use planning phase to design improvements
- Implementation phase executes changes systematically

## Use Cases

### Personal Knowledge Management
- Research and organize information on topics
- Create structured documentation
- Build reference materials

### Project Documentation
- Analyze existing documentation
- Plan improvements
- Implement new organization systems

### Research Projects
- Gather information from multiple sources
- Synthesize findings
- Create comprehensive reports

### Task Automation
- Identify repetitive tasks
- Plan automation strategy
- Create helper scripts and workflows

### Decision Support
- Research options and alternatives
- Create comparison documents
- Develop decision frameworks

## Plugin Configuration

### Hooks

The plugin includes an automatic subagent logging hook that tracks all subagent interactions for debugging and progress monitoring.

## Version History

- **1.0.0** - Initial release adapted from SDD methodology for personal agent use

## Support

For issues, feature requests, or questions:
- Create an issue in the plugin repository
- Check the [Claude Code documentation](https://docs.claude.com/en/docs/claude-code/plugins)

## License

This plugin is provided as-is for use with Claude Code. See the repository for license details.

---

**Built for Claude Code** - Transforming AI assistance into a comprehensive personal agent with context-engineered methodology.