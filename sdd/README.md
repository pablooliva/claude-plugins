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
- **Two delivery modes**: pick **whole-feature** (single-pass) for most work, or opt into **per-slice** (vertical-thread) when you want feedback after each integrated layer

## What is Specification-Driven Development?

SDD is a systematic approach that ensures features are thoroughly researched, properly specified, and correctly implemented. Each phase is optimized for different aspects of development:

1. **Research Phase** (Claude Opus) - Deep codebase investigation and pattern analysis
2. **Planning Phase** (Claude Sonnet) - Technical specification and design documentation
3. **Implementation Phase** (Claude Sonnet) - Code development following specifications

Each phase concludes with a **Critical Review** — an adversarial analysis that identifies gaps, mistakes, inconsistencies, and blind spots before proceeding to the next phase.

### Phase Usage + Workflow Management = Success

Each phase is managed by the user according to this SDD workflow.

## Which workflow is right for you?

The plugin ships two delivery modes, switched by a single field in the spec frontmatter (`delivery_mode:`). Most features should use **whole-feature** — the existing three-phase research → planning → implementation flow, single-pass through implementation. Choose **per-slice** when the feature spans multiple layers (UI → API → service → datastore) and you want vertical-thread feedback (review, retrospective, commit) after each thin integrated slice rather than at the end of the whole feature. Per-slice mode requires opting in via the spec's frontmatter and authoring a `## Delivery Slices` section enumerating the slices.

If unsure, default to whole-feature. You can re-plan into per-slice later by amending the spec.

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

## Whole-feature workflow

The default delivery mode. Use this for the majority of features. The spec's frontmatter sets (or omits) `delivery_mode: whole-feature`; no `## Delivery Slices` section is required.

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

### Whole-feature Workflow Example

#### Complete Feature Development

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

## Per-slice workflow

An opt-in delivery mode for multi-layer features where you want vertical-thread feedback after each integrated slice rather than at the end of the whole feature. Per-slice mode requires SDD plugin **2.0.0 or later**.

### Opting in

Set the spec's frontmatter to `delivery_mode: per-slice` and author a `## Delivery Slices` section enumerating the slices. The `## Delivery Slices` section is **required** when `delivery_mode: per-slice`; spec critical-review and `/spec-review-panel` apply slice-integrity checks only when this mode is set:

```yaml
---
delivery_mode: per-slice
review_panel: [security, performance, data-modeling, api-contract]
eval_required: false
cross_cutting_decisions: []
---

# SPEC-[###]-[feature-name]

...

## Delivery Slices

- **SLICE-001:** Thin vertical thread #1 — Acceptance: ...
- **SLICE-002:** Thin vertical thread #2 — Acceptance: ...
- ...
```

A spec with `delivery_mode: per-slice` but no `## Delivery Slices` section (or no rows) trips the planning practicality gate, which halts the flow and asks you to either reduce to a single slice (use whole-feature) or articulate the multi-slice decomposition.

A spec without a `delivery_mode:` field defaults silently to `whole-feature`.

### Per-slice state machine

```text
┌─────────────────────────────────────────────────────────────────┐
│                     RESEARCH PHASE (Opus)                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PLANNING PHASE (Sonnet)                      │
│  delivery_mode: per-slice  +  ## Delivery Slices section        │
│  Practicality gate: halt if single-MODULE or every-slice is     │
│  build-then-test                                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│             IMPLEMENTATION PHASE (Sonnet)                       │
│  /implementation-start scaffolds ## Slice Progress table        │
│                                                                 │
│   ┌──────────  Per-slice cycle (one per SLICE-XXX row) ──────┐ │
│   │                                                           │ │
│   │   /slice-start    →  implement slice                      │ │
│   │        │                                                  │ │
│   │        ▼                                                  │ │
│   │   /slice-review   →  scoped /code-review                  │ │
│   │        │      (cap 3 iterations; HIGH must strictly       │ │
│   │        │       decrease, or MEDIUM when HIGH is zero)     │ │
│   │        ▼                                                  │ │
│   │   /slice-retro    →  RETROSPECTIVE-SLICE-XXX-*.md         │ │
│   │        │              + ledger update (retro-first)       │ │
│   │        ▼                                                  │ │
│   │   /slice-commit   →  atomic per-slice commit              │ │
│   │        │                                                  │ │
│   │        ▼                                                  │ │
│   │   slice-boundary checkpoint (default ON;                  │ │
│   │   skipped under --skip-slice-checkpoints)                 │ │
│   │        │                                                  │ │
│   │        └──────► next SLICE-XXX row ──────►  loop          │ │
│   └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│       all slices Complete → end-of-feature merge & finalize     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌───────────────────────┐
                    │ /implementation-test  │
                    │ /critical-review      │
                    │ /implementation-      │
                    │      complete         │
                    │ /commit               │
                    └───────────────────────┘
```

### Slice commands

Each command refuses (with a friendly inert-mode message naming the field, the required value, and the alternative action) when the active SPEC has `delivery_mode: whole-feature` or no `delivery_mode:` field. Slice-IDs are validated against `^SLICE-\d{3}$` before any path interpolation (path-traversal prevention).

- **`/slice-start`** — resolve the active slice (the single `Not Started` row, or a `[SLICE-XXX]` arg, or prompt the user when ambiguous), refuse when another slice is `In Progress` (`--resume` overrides), refuse when the slice is already `Complete` (`--force` overrides; in autonomous mode this halts via `## Awaiting Re-start Decision`), update the `## Slice Progress` row to `In Progress`, and load the rolling learnings ledger so the implementing subagent receives only the ledger (per OQ-6) rather than every prior retrospective.
- **`/slice-review`** — thin wrapper over `/code-review` scoped to the active slice's file set. Writes `SDD/reviews/REVIEW-SLICE-XXX-*.md` with `[YYYY-MM-DD]` date format. Caps iteration at 3 with a progress-stall check (HIGH count must strictly decrease, or MEDIUM when HIGH is zero); on halt, findings route to the ledger's *Open recommendations awaiting user decision* section.
- **`/slice-retro`** — write `SDD/implementation/slices/RETROSPECTIVE-SLICE-XXX-*.md` (audit trail; never modified after creation), then update the rolling ledger `SDD/implementation/slices/LEARNINGS-FEATURE-[feature-name].md` (retro-first ordering — RETROSPECTIVE write is the durable artifact; ledger update is recoverable via `--reconcile-ledger` if it fails). Refuses if a retrospective for the slice already exists; `--reconcile-ledger` is the escape hatch for ledger drift. Updates only the `Status`, `Test result`, and `Notes` columns of the `## Slice Progress` table; never rewrites `SLICE-ID`, `Name`, or `Acceptance check` columns. May emit a `## Recommended SPEC Amendments` block (advisory) or a `## Recommended Re-planning` block (elevated severity — halts the flow even under `--skip-slice-checkpoints`).
- **`/slice-commit`** — atomic per-slice commit with a structured heredoc commit message naming the slice. Looser staging policy (the user controls staging; the command does not enforce that the working tree contains only slice-scoped files). Never bypasses git hooks (no `--no-verify`, no force flags).

### Slice-boundary checkpoint axis

By default, `/sdd-flow` halts at every slice boundary in both supervised and autonomous mode (so the user can review each slice's retrospective and ledger updates before the next slice starts). The `--skip-slice-checkpoints` flag opts into continuous run; when enabled, "Open recommendations" accumulate in the rolling ledger and surface as a single consolidated block in the orchestrator's announcement at end-of-feature.

The matrix:

| Mode | Default | `--skip-slice-checkpoints` |
|---|---|---|
| Supervised | Halt at each slice boundary | Run continuously, consolidate recommendations at end |
| Autonomous | Halt at each slice boundary | Run continuously, consolidate recommendations at end |

Even under `--skip-slice-checkpoints`, a `## Recommended Re-planning` block from `/slice-retro` halts the entire flow (the re-planning trigger overrides the checkpoint axis).

### Retrospectives and the rolling ledger

Each completed slice writes a `RETROSPECTIVE-SLICE-XXX-*.md` (the audit trail — never modified after creation) and contributes deltas to a single `LEARNINGS-FEATURE-[feature-name].md` ledger per feature. The ledger is the only artifact passed to subsequent slice subagents (per OQ-6) — individual retrospectives are out of the prompt path. This keeps later-slice subagents cheap while preserving institutional memory.

If `RETROSPECTIVE-SLICE-XXX-*.md` exists but the ledger is missing the entry (e.g., disk error mid-operation), recovery is via `/slice-retro --reconcile-ledger`, which detects retros without ledger entries and reconciles them. The retro file existing without a ledger update is a recoverable state; the inverse is not. Two-write ordering is invariant: retrospective first, ledger second.

### Re-planning trigger

A retrospective may emit a `## Recommended Re-planning` block when the slice surfaces a structural issue that invalidates the remaining slices' decomposition. The orchestrator halts immediately (regardless of `--skip-slice-checkpoints`) and offers three resume options:

- `/sdd-flow continue --replan` — re-plan from the current point.
- `/sdd-flow continue --replan --from-slice SLICE-XXX` — re-plan starting from a specific slice.
- `/sdd-flow continue --override-replan` — explicit override; keep the existing decomposition and continue.

A plain `/sdd-flow continue` while a `## Recommended Re-planning` block is pending produces an informative refusal listing all three flags (EDGE-006).

### Practicality gate

The planning phase tests four boolean heuristics against the spec to detect cases where per-slice mode is impractical (single-MODULE feature, every decomposition is build-then-test, slice acceptance criteria are entirely test-only, or the spec has only one `## Delivery Slices` row). Failing any heuristic halts the flow and asks you to either drop to whole-feature or articulate the multi-slice rationale (the qualitative escape hatch is a `Qualitative judgment: ` prefix on the rationale line).

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

In `delivery_mode: per-slice` specs, the planning critical-review additionally applies a slice-integrity check (every `SLICE-XXX` resolves to acceptance criteria, no orphan slices, no orphan REQs).

Review output is saved to `SDD/reviews/` with a dated filename (e.g., `CRITICAL-RESEARCH-[feature]-YYYYMMDD.md`). Can also be used ad-hoc to review any proposed solution outside the SDD lifecycle.

### Specialist Panel Review

Run after `/planning-complete` to convene a panel of domain specialists who review the specification through narrow expert lenses:

```bash
# Specialist panel review of the current specification
/spec-review-panel
```

Unlike `/critical-review` (single adversarial generalist), this command spawns multiple specialist reviewers in parallel — each with precise domain vocabulary and named anti-patterns. The default panel covers **security**, **performance**, **data-modeling**, **api-contract**, and **module-depth**. Additional specialists (`accessibility`, `privacy`, `cost`, `reliability`) can be enabled per-spec via the `review_panel:` frontmatter field. In `delivery_mode: per-slice` specs the panel adds a **slice-integrity** specialist and a `#### Slice Integrity Findings` deliverable sub-header.

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

1. Load the IMPLEMENTATION-PLAN and SPEC documents to understand what was built and what coverage is expected
2. Discover the project's test infrastructure (frameworks, runner commands, coverage tooling)
3. Inventory all test files, categorized as unit, integration, or end-to-end
4. Build a coverage matrix mapping every REQ-XXX, EDGE-XXX, FAIL-XXX, PERF-XXX, and SEC-XXX to the tests that validate it
5. Execute the test suite — unit, integration, and e2e separately — and capture pass/fail results
6. Triage any failures: fix the implementation, fix the test, or document as an environment-dependent skip
7. Produce a timestamped audit report in `SDD/implementation/test-audits/` and update the IMPLEMENTATION-PLAN document

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

# Migrate a project's SDD artifact tree from 1.x to 2.0.0 layout
/sdd-migrate-layout
```

## Specification Frontmatter

Specifications created by `/planning-start` include YAML frontmatter that gates downstream behaviors:

```yaml
---
delivery_mode: whole-feature
review_panel: [security, performance, data-modeling, api-contract, module-depth]
eval_required: false
cross_cutting_decisions: []
---

# SPEC-[###]-[feature-name]
```

- **`delivery_mode:`** — `whole-feature` (default; existing single-pass implementation) or `per-slice` (opt-in vertical-thread mode; requires a `## Delivery Slices` section). Drives `/sdd-flow` Step 4 routing, the practicality gate, and slice-integrity checks. Specs without this field default silently to `whole-feature`.
- **`review_panel:`** — Which specialists `/spec-review-panel` convenes. Default covers API/data-backed features. Add `accessibility` for UI work, `privacy` for PII/consent features, `cost` for data-intensive features, `reliability` for distributed/async systems.
- **`eval_required:`** — Set to `true` if the feature produces LLM output, probabilistic behavior, or any quality dimension unit tests can't verify. Consumed by the companion **agent-engineering** plugin (if installed) to scaffold a LangSmith regression eval at implementation completion.
- **`cross_cutting_decisions:`** — Snake_case labels for architectural decisions made during this feature that bind future work (e.g., `orchestration_engine`, `vector_store`, `primary_datastore`). Consumed by the companion **agent-engineering** plugin (if installed) to capture each as an ADR under `SDD/adr/`.

The fields have sensible defaults and are safe to ignore if the companion plugin isn't installed — `/spec-review-panel` reads `review_panel:` directly from this plugin, and the other two fields become no-ops.

## Directory Structure

The plugin automatically creates and manages the following structure in your project (2.0.0 layout):

```text
project/
└── SDD/                           # Root directory for all SDD artifacts
    ├── research/                  # Research phase documents
    │   ├── CLARIFICATION-XXX-*.md   # Pre-research design-concept artifacts
    │   └── RESEARCH-XXX-*.md        # Detailed investigation findings
    ├── requirements/              # Planning phase specifications
    │   └── SPEC-XXX-*.md            # Technical specifications
    ├── reviews/                   # Review documents
    │   ├── CRITICAL-RESEARCH-*.md   # Research phase critical reviews
    │   ├── PANEL-SPEC-*.md          # Planning phase specialist panel reviews
    │   ├── CRITICAL-SPEC-*.md       # Planning phase critical reviews
    │   ├── CRITICAL-IMPL-*.md       # Implementation phase critical reviews
    │   └── REVIEW-SLICE-XXX-*.md    # Per-slice code reviews (per-slice mode only)
    ├── adr/                       # Architecture Decision Records (optional)
    │   ├── NNNN-slug.md             # Created by agent-engineering plugin if installed
    │   └── README.md                # Auto-generated index
    ├── UBIQUITOUS_LANGUAGE.md     # Project-wide domain glossary
    ├── implementation/            # Per-feature implementation artifacts
    │   ├── IMPLEMENTATION-PLAN-XXX-*.md   # Tracker (renamed from PROMPT-XXX-*.md in 2.0.0)
    │   ├── summaries/                     # Completed-implementation summaries
    │   │   └── IMPLEMENTATION-SUMMARY-XXX-*.md
    │   ├── test-audits/                   # Test coverage audit reports
    │   │   └── TEST-AUDIT-XXX-*.md
    │   └── slices/                        # Per-slice mode only
    │       ├── RETROSPECTIVE-SLICE-XXX-*.md   # Per-slice retrospective (audit trail)
    │       └── LEARNINGS-FEATURE-XXX.md       # Rolling learnings ledger (one per feature)
    └── orchestration/             # Runtime state (sdd-flow + commands)
        ├── progress.md              # Current phase progress
        ├── compacted/               # Compacted session data
        │   └── *-compacted-*.md
        ├── counters/                # Subagent bail-out counter files
        │   └── *.txt
        └── subagent-calls/          # Subagent interaction logs
            └── *.json
```

**Numbering convention:** `CLARIFICATION-[###] → RESEARCH-[###] → SPEC-[###] → IMPLEMENTATION-PLAN-[###]` must align — all four artifacts for the same feature share `[###]` and `[feature-name]`. In `delivery_mode: per-slice`, slice IDs follow `SLICE-\d{3}` and live within the feature's tracker and ledger.

## Migration to 2.0.0

SDD 2.0.0 is a breaking release. Two coupled changes ship together:

1. **Directory restructure.** The legacy `SDD/prompts/` tree is split into `SDD/implementation/` (per-feature artifacts: tracker, summaries, test-audits, slices) and `SDD/orchestration/` (runtime state: progress.md, compacted sessions, counters, subagent-call logs).
2. **Tracker rename.** `PROMPT-XXX-[feature].md` is renamed to `IMPLEMENTATION-PLAN-XXX-[feature].md`. The numbering convention is otherwise unchanged.

See `SDD/adr/0002-restructure-sdd-artifact-directory-layout.md` for rationale.

### `/sdd-migrate-layout`

A one-time migration helper ships with the plugin. From the project root, run:

```bash
/sdd-migrate-layout
```

The command:

- **Refuses to run while a flow is mid-execution** (parses `progress.md` for `## Phase:` / `## Awaiting ` / `## Recommended Re-planning` / `## PARTIAL:` headings; refuses with an active-flow message if any are present, falls closed on parse failure).
- **Detects partial-migration state** and refuses with an explicit list of files at legacy and new paths.
- **Is idempotent** — re-running on an already-migrated tree exits with "no migration needed."
- **Uses `git mv`** for every move (preserves history); never bypasses git hooks.
- **Does NOT modify user-authored docs.** Any project-level `CLAUDE.md` (or `AGENTS.md`) referencing legacy paths (`SDD/prompts/...`, `PROMPT-XXX`) becomes stale post-migration. Grep your own `CLAUDE.md` for these strings and update accordingly.
- **Bash-only.** On Windows, run from Git Bash; the command refuses cleanly under cmd.exe or PowerShell.

After migration, verify your installed SDD plugin is at version 2.0.0 or later — older versions write logs and tracker files to the legacy paths and you will see split-tree symptoms.

### macOS APFS case-collision warning

On case-insensitive APFS volumes, the project's `SDD/` artifact directory may collide with a `sdd/` plugin source directory if you happen to have one in the same tree (e.g., when working on this plugin itself). The migration helper is path-literal; collisions surface as `git mv` failures naming both paths. Resolve manually by renaming one of the two trees before re-running the migration.

## Cross-plugin dependency

This plugin composes with the **agent-engineering** plugin's `sdd-flow` skill for end-to-end orchestration. The two plugins install independently from the marketplace, so it is plausible to update one without the other.

- **SDD 2.0.0 requires `agent-engineering` 0.4.0 or later** for `sdd-flow`. The 0.3.x `sdd-flow` skill embeds SDD 1.x command bodies and references legacy paths (`SDD/prompts/...`, `PROMPT-XXX`). Running 0.3.x against SDD 2.0.0 silently misbehaves — the skill writes legacy paths while the SDD commands write new paths (split-tree), and `delivery_mode: per-slice` specs flow as `whole-feature` with no Step 4 state machine. This is FAIL-009 in the spec.
- **Recovery from the mismatch is non-destructive but manual** — orphan artifacts at legacy paths are `git mv`-able into the new tree.
- **To stay aligned**, install or update both plugins together:

  ```bash
  /plugin install https://github.com/poliva83/claude-plugins sdd
  /plugin install https://github.com/poliva83/claude-plugins agent-engineering
  ```

The matching cross-reference lives in the agent-engineering plugin's README ("What's new in 0.4.0" + "Requires SDD plugin 2.0.0 or later" sections).

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

The plugin includes an automatic subagent logging hook that tracks all subagent interactions for debugging and progress monitoring. Logs are written under `SDD/orchestration/subagent-calls/` (2.0.0 layout).

## Changelog

### 2.0.0 — Per-slice delivery mode + directory restructure (breaking)

Two coupled changes ship together — both apply to all SDD users (whole-feature included):

- **`delivery_mode: per-slice` opt-in.** New frontmatter field gates a vertical-thread implementation flow: per-slice cycle (`/slice-start` → `/slice-review` → `/slice-retro` → `/slice-commit`), rolling learnings ledger, slice-boundary checkpoint axis (`--skip-slice-checkpoints`), re-planning trigger, and a planning-phase practicality gate. `delivery_mode: whole-feature` (the default) preserves existing behaviour bit-for-bit. See the "Per-slice workflow" section above. Companion: agent-engineering 0.4.0+ adds the matching mode-aware `sdd-flow` Step 4 state machine.
- **Directory restructure + tracker rename.** `SDD/prompts/` is split into `SDD/implementation/` (per-feature artifacts) and `SDD/orchestration/` (runtime state). `PROMPT-XXX-*.md` is renamed to `IMPLEMENTATION-PLAN-XXX-*.md`. The `/sdd-migrate-layout` command performs the migration. See "Migration to 2.0.0" above and `SDD/adr/0002-restructure-sdd-artifact-directory-layout.md`.

**Cross-plugin coupling:** SDD 2.0.0 requires agent-engineering 0.4.0 or later for `sdd-flow`. See "Cross-plugin dependency" above and FAIL-009 in the spec.

**Breaking-change posture:** existing 1.x specs without `delivery_mode:` continue to work (default `whole-feature`); existing 1.x trackers and progress files require `/sdd-migrate-layout`. The migration is non-destructive (`git mv`-based, idempotent, refuses while a flow is mid-execution).

### 1.2.0 — Software-fundamentals integration

Inspired by Matt Pocock's *Software Fundamentals Matter More Than Ever* ([AI Engineer Europe 2026](https://www.youtube.com/watch?v=v4F1gFy-hqg)). Each addition follows a generative-front, verification-back pattern: a constraint is applied during the phase that produces an artifact, and verified at that phase's review gate.

- **`/research-clarify` — pre-research design-concept interview.** New command that externalizes the user's design concept (Brooks) before any codebase research begins. Walks the design tree branch by branch, surfaces ambiguities, captures constraints and out-of-scope. Produces `SDD/research/CLARIFICATION-[###]-[feature-name].md`, which `/research-start` then loads as input. **Verification:** `/critical-review`'s research checklist now includes a *Design Concept Fidelity* block that confirms every clarified branch was addressed and every open question resolved or explicitly deferred.
- **`SDD/UBIQUITOUS_LANGUAGE.md` — project-wide domain glossary.** Single file maintained incrementally across cycles (Evans, *Domain-Driven Design*). Updated by `/research-complete` (terms introduced during research) and `/planning-complete` (terms introduced during spec). Loaded by `/research-start`, `/planning-start`, `/implementation-start`, and `/research-clarify` so vocabulary stays aligned across phases — AI thinking traces stop reinventing terminology.
- **`## Modules` section + `module-depth` specialist — deep-module enforcement.** Spec template now includes a `## Modules` section requiring `Public Interface`, `Hides`, `Risk`, and `Spec refs` for each module. `/planning-start` directs Claude to prefer deep modules (Ousterhout) and reject unjustified shallow modules. **Verification:** `/spec-review-panel` adds a `module-depth` specialist (added to the default panel) with vocabulary payload and 10 named anti-patterns (pass-through wrapper, getter/setter façade, wide-thin interface, etc.). Existing specs without a Modules section degrade gracefully — the specialist emits a MEDIUM finding requesting retrofit rather than failing the panel.
- **Risk-tiered code review.** `/code-review` reads each module's `Risk:` field and scales review depth proportionally: `high` → full review of internals; `medium` → default depth; `low` → tested-boundary review only. The reviewer retains authority to escalate misclassified tiers (e.g., a `low`-tagged module touching irreversible state). Concentrates scrutiny where consequence-of-failure is largest.

**Numbering convention extended:** `CLARIFICATION-[###] → RESEARCH-[###] → SPEC-[###] → IMPLEMENTATION-PLAN-[###]` must align — all four artifacts for the same feature share `[###]` and `[feature-name]`.

**Backwards compatibility:** All four 1.2.0 additions are non-breaking. Existing specs without `## Modules`, missing `module-depth` in `review_panel`, or pre-1.2.0 research without a CLARIFICATION artifact all continue to work — the new gates degrade gracefully and note the gap rather than failing.

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

## Subagent Types Shipped (v2.1.0+)

The plugin's `agents/` directory ships 8 named subagent types consumed by `/sdd:critical-review`, `/sdd:spec-review-panel`, and downstream skills (notably `agent-engineering`'s `/sdd-flow`):

- **`sdd-critical-reviewer`** (Opus) — adversarial reviewer for research / spec / implementation phase artifacts; also the panel orchestrator's synthesis role.
- **`sdd-spec-security-specialist`** (Sonnet) — `/sdd:spec-review-panel` `security` panel value.
- **`sdd-spec-performance-specialist`** (Sonnet) — `performance` panel value.
- **`sdd-spec-data-modeling-specialist`** (Sonnet) — `data-modeling` panel value.
- **`sdd-spec-api-contract-specialist`** (Sonnet) — `api-contract` panel value.
- **`sdd-spec-module-depth-specialist`** (Sonnet) — `module-depth` panel value.
- **`sdd-spec-reliability-specialist`** (Sonnet) — `reliability` panel value.
- **`sdd-spec-slice-integrity-specialist`** (Sonnet, self-skips for whole-feature mode) — `slice-integrity` panel value (per-slice mode only).

Each specialist's vocabulary + named-anti-pattern payload remains canonical in `/sdd:spec-review-panel` Section 4 and is embedded by the orchestrator at spawn time; the agent files provide identity, model tier, severity rubric, and bounded-return discipline.

---

**Built for Claude Code** - Enhancing AI-assisted development with a specification-driven systematic methodology.
