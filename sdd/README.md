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
/plugin marketplace add pablooliva/claude-plugins
/plugin install sdd
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
- **Test Verification**: Audits test coverage against specification requirements and runs the test suite to confirm all tests pass

## What is Specification-Driven Development?

SDD is a systematic approach that ensures features are thoroughly researched, properly specified, and correctly implemented. Each phase is optimized for different aspects of development:

1. **Research Phase** (Claude Opus) - Deep codebase investigation and pattern analysis
2. **Planning Phase** (Claude Sonnet) - Technical specification and design documentation
3. **Implementation Phase** (Claude Sonnet) - Code development following specifications

Each phase concludes with a **Critical Review** — an adversarial analysis that identifies gaps, mistakes, inconsistencies, and blind spots before proceeding to the next phase.

### Phase Usage + Workflow Management = Success

Each phase is managed by the user according to this SDD workflow.

## SDD Workflow Overview

It is important to keep the context window below 40%. This MUST be done with human interaction.. YOU!

```text
PHASE START          CONTEXT ~40%           SAVE WORK          CLEAR SESSION
    │                     │                     │                   │
    ▼                     ▼                     ▼                   ▼
[/start] ──────────► [/compact*] ─────────► [/commit] ──────────► [/clear]
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
- **Compact**: When context approaches 40%, use the appropriate compact command to compress session
- **Commit**: Save your work with `/commit` before clearing the session
- **Continue**: Resume work with `/continue` in a fresh session
- **Complete**: Finalize the current phase with `/complete`
- **Commit**: Create final commits with `/commit`

### Context Monitoring

Use Claude Code's built-in `/usage` slash command to check current context utilization at any time. Run `/context-check` for a phase-aware recommendation based on the current reading.

### Recovering from a Wrong Turn

If you realize Claude has taken a wrong approach mid-phase, use the built-in `/rewind` command (double-Esc) to jump back to an earlier message and re-prompt with corrected guidance. This retains prior file reads while dropping the failed attempt — preferable to a full compact/commit/clear/continue cycle when the issue is an approach error rather than context pressure.

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
                    ┌───────────────────┐
                    │ /critical-review  │
                    │ Adversarial check │
                    └───────────────────┘
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
                 ┌─────────────────────────┐
                 │  /spec-review-panel     │
                 │  Domain specialists     │
                 │  (security, perf, etc.) │
                 └─────────────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ /critical-review  │
                    │ Adversarial check │
                    └───────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 IMPLEMENTATION PHASE (Sonnet)                   │
│  • Write code following specifications                          │
│  • Implement tests                                              │
│  • Ensure quality standards                                     │
│  Output: Implemented feature + tests                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌───────────────────────┐
                    │ /implementation-test  │
                    │ Audit coverage &      │
                    │ run test suite        │
                    └───────────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ /critical-review  │
                    │ Adversarial check │
                    └───────────────────┘
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
# Phase-specific compaction (use these during active phases):
/research-compact
/planning-compact
/implementation-compact

# Generic lightweight compaction (for ad-hoc work or follow-ups only):
/adhoc-compact
```

Use phase-specific commands when in a development phase. Use `/adhoc-compact` only for smaller tasks, ad-hoc work, or follow-ups outside of active phases — it includes phase detection that will redirect you to the correct phase-specific command if needed.

### Completing Phases

```bash
# Finalize research documentation
/research-complete

# Finalize specification
/planning-complete

# Complete implementation
/implementation-complete
```

### Critical Review

Run after completing each phase to perform an adversarial review before proceeding:

```bash
# Review phase artifacts for gaps, mistakes, and blind spots
/critical-review
```

The command automatically detects the current phase by checking for SDD artifacts and applies the appropriate review criteria:

- **After Research**: Checks for completeness gaps, logical weaknesses, and untested assumptions
- **After Planning**: Checks for ambiguous requirements, research disconnects, and missing edge cases
- **After Implementation**: Checks for specification deviations, technical vulnerabilities, and test coverage gaps

Review output is saved to `SDD/reviews/` with a dated filename (e.g., `CRITICAL-RESEARCH-[feature]-YYYYMMDD.md`). Can also be used ad-hoc to review any proposed solution outside the SDD lifecycle.

### Specialist Panel Review

Run after `/planning-complete` to convene a panel of domain specialists who review the specification through narrow expert lenses:

```bash
# Specialist panel review of the current specification
/spec-review-panel
```

Unlike `/critical-review` (single adversarial generalist), this command spawns multiple specialist reviewers in parallel — each with precise domain vocabulary and named anti-patterns. The default panel covers **security**, **performance**, **data-modeling**, and **api-contract**. Additional specialists (`accessibility`, `privacy`, `cost`, `reliability`) can be enabled per-spec via the `review_panel:` frontmatter field.

Each specialist produces evidence-backed findings (spec line references required; bare approvals banned). Findings are aggregated into an overall verdict:

- **PROCEED** — only LOW findings (or none). Safe to continue.
- **REVISE BEFORE PROCEEDING** — 3+ MEDIUM findings, or cross-domain MEDIUM flagged by 2+ specialists.
- **STOP AND RECONSIDER** — any HIGH finding. Spec is not ready.

Review output is saved to `SDD/reviews/PANEL-SPEC-[feature]-YYYYMMDD.md`.

`/critical-review` and `/spec-review-panel` are **complementary, not redundant**: critical-review challenges assumptions and logic broadly; the panel catches domain-specific anti-patterns (hardcoded secrets, N+1 queries, IDOR, non-idempotent POSTs, missing index on FKs, etc.) that a generalist would miss. Running both on a high-stakes spec is reasonable.

### Test Verification

Run during the implementation phase to audit test coverage and execute the test suite:

```bash
# Audit test coverage and run tests
/implementation-test
```

The command works in seven phases:

1. Load the PROMPT and SPEC documents to understand what was built and what coverage is expected
2. Discover the project's test infrastructure (frameworks, runner commands, coverage tooling)
3. Inventory all test files, categorized as unit, integration, or end-to-end
4. Build a coverage matrix mapping every REQ-XXX, EDGE-XXX, FAIL-XXX, PERF-XXX, and SEC-XXX to the tests that validate it
5. Execute the test suite — unit, integration, and e2e separately — and capture pass/fail results
6. Triage any failures: fix the implementation, fix the test, or document as an environment-dependent skip
7. Produce a timestamped audit report in `SDD/prompts/test-audits/` and update the PROMPT document

The command produces a clear verdict — **Adequate**, **Partial**, or **Insufficient** — and signals whether `/implementation-complete` can safely proceed.

### Utility Commands

```bash
# Resume work after clearing session
/continue

# Check current context utilization
/context-check

# Review code against specifications
/code-review

# Create commits following conventions
/commit
```

## Specification Frontmatter

Specifications created by `/planning-start` include YAML frontmatter with three fields that gate downstream behaviors:

```yaml
---
review_panel: [security, performance, data-modeling, api-contract]
eval_required: false
cross_cutting_decisions: []
---

# SPEC-[###]-[feature-name]
```

- **`review_panel:`** — Which specialists `/spec-review-panel` convenes. Default covers API/data-backed features. Add `accessibility` for UI work, `privacy` for PII/consent features, `cost` for data-intensive features, `reliability` for distributed/async systems.
- **`eval_required:`** — Set to `true` if the feature produces LLM output, probabilistic behavior, or any quality dimension unit tests can't verify. Consumed by the companion **agent-engineering** plugin (if installed) to scaffold a LangSmith regression eval at implementation completion.
- **`cross_cutting_decisions:`** — Snake_case labels for architectural decisions made during this feature that bind future work (e.g., `orchestration_engine`, `vector_store`, `primary_datastore`). Consumed by the companion **agent-engineering** plugin (if installed) to capture each as an ADR under `SDD/adr/`.

The fields have sensible defaults and are safe to ignore if the companion plugin isn't installed — `/spec-review-panel` reads `review_panel:` directly from this plugin, and the other two fields become no-ops.

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

4. **Critical Review of Research**:

   ```bash
   /critical-review
   # Address any findings before proceeding
   ```

5. **Create Specification** (switch to Claude Sonnet):

   ```bash
   /planning-start
   # Review and refine the specification
   ```

6. **Complete Planning & Reviews**:

   ```bash
   /planning-complete
   /spec-review-panel
   # Verdict: PROCEED → continue. REVISE or STOP → address findings, re-run.
   /critical-review
   # Address any remaining findings before proceeding
   /commit
   ```

7. **Implement Feature**:

   ```bash
   /implementation-start
   # Code is developed following the specification
   ```

8. **Test Verification**:

   ```bash
   /implementation-test
   # Audits coverage against spec, runs the test suite, and fixes failures
   ```

9. **Review and Finalize**:

   ```bash
   /code-review
   /implementation-complete
   /critical-review
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
    ├── reviews/                  # Review documents
    │   ├── CRITICAL-RESEARCH-*.md  # Research phase critical reviews
    │   ├── PANEL-SPEC-*.md         # Planning phase specialist panel reviews
    │   ├── CRITICAL-SPEC-*.md      # Planning phase critical reviews
    │   └── CRITICAL-IMPL-*.md      # Implementation phase critical reviews
    ├── adr/                      # Architecture Decision Records (optional)
    │   ├── NNNN-slug.md          # Created by agent-engineering plugin if installed
    │   └── README.md             # Auto-generated index
    └── prompts/                  # Session management
        ├── implementation-complete/  # Archived implementations
        ├── test-audits/          # Test coverage audit reports
        │   └── TEST-AUDIT-XXX-*.md  # Per-feature test audits
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

## Changelog

### 1.2.0 — Software-fundamentals integration

Inspired by Matt Pocock's *Software Fundamentals Matter More Than Ever* ([AI Engineer Europe 2026](https://www.youtube.com/watch?v=v4F1gFy-hqg)). Each addition follows a generative-front, verification-back pattern: a constraint is applied during the phase that produces an artifact, and verified at that phase's review gate.

- **`/research-clarify` — pre-research design-concept interview.** New command that externalizes the user's design concept (Brooks) before any codebase research begins. Walks the design tree branch by branch, surfaces ambiguities, captures constraints and out-of-scope. Produces `SDD/research/CLARIFICATION-[###]-[feature-name].md`, which `/research-start` then loads as input. **Verification:** `/critical-review`'s research checklist now includes a *Design Concept Fidelity* block that confirms every clarified branch was addressed and every open question resolved or explicitly deferred.
- **`SDD/UBIQUITOUS_LANGUAGE.md` — project-wide domain glossary.** Single file maintained incrementally across cycles (Evans, *Domain-Driven Design*). Updated by `/research-complete` (terms introduced during research) and `/planning-complete` (terms introduced during spec). Loaded by `/research-start`, `/planning-start`, `/implementation-start`, and `/research-clarify` so vocabulary stays aligned across phases — AI thinking traces stop reinventing terminology.
- **`## Modules` section + `module-depth` specialist — deep-module enforcement.** Spec template now includes a `## Modules` section requiring `Public Interface`, `Hides`, `Risk`, and `Spec refs` for each module. `/planning-start` directs Claude to prefer deep modules (Ousterhout) and reject unjustified shallow modules. **Verification:** `/spec-review-panel` adds a `module-depth` specialist (added to the default panel) with vocabulary payload and 10 named anti-patterns (pass-through wrapper, getter/setter façade, wide-thin interface, etc.). Existing specs without a Modules section degrade gracefully — the specialist emits a MEDIUM finding requesting retrofit rather than failing the panel.
- **Risk-tiered code review.** `/code-review` reads each module's `Risk:` field and scales review depth proportionally: `high` → full review of internals; `medium` → default depth; `low` → tested-boundary review only. The reviewer retains authority to escalate misclassified tiers (e.g., a `low`-tagged module touching irreversible state). Concentrates scrutiny where consequence-of-failure is largest.

**Numbering convention extended:** `CLARIFICATION-[###] → RESEARCH-[###] → SPEC-[###] → PROMPT-[###]` must align — all four artifacts for the same feature share `[###]` and `[feature-name]`.

**Backwards compatibility:** All four additions are non-breaking. Existing specs without `## Modules`, missing `module-depth` in `review_panel`, or pre-1.2.0 research without a CLARIFICATION artifact all continue to work — the new gates degrade gracefully and note the gap rather than failing.

**Companion plugin integration:** The `agent-engineering` plugin's `/sdd-flow` skill has been updated to wire all four additions into the orchestrated lifecycle. Pre-research clarification is a **mandatory gate (Step 1.5) in both supervised and autonomous modes** — autonomous flow halts at this single checkpoint until the user runs `/research-clarify`, the CLARIFICATION artifact already exists, or `--skip-clarify` is passed. Deep-modules and risk-tiering ride along automatically through the updated SDD commands.

### 1.1.0

Added `/spec-review-panel` command (domain specialist panel review of specs, complementing `/critical-review`). Added YAML frontmatter to the specification template with three fields (`review_panel`, `eval_required`, `cross_cutting_decisions`) that gate downstream behavior and enable integration with the companion **agent-engineering** plugin. Updated Phase Progression diagram and Workflow Example to reflect the new planning-phase review step. Directory structure now documents `PANEL-SPEC-*.md` review outputs and the optional `SDD/adr/` directory used by the companion plugin.

### 1.0.0

Initial release with complete SDD methodology.

## Support

For issues, feature requests, or questions:

- Create an issue in the plugin repository
- Check the [Claude Code documentation](https://docs.claude.com/en/docs/claude-code/plugins)

## License

This plugin is provided as-is for use with Claude Code. See the repository for license details.

---

**Built for Claude Code** - Enhancing AI-assisted development with a specification-driven systematic methodology.
