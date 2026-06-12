---
name: sdd-flow
description: "INVOKE THIS SKILL when the user asks to run end-to-end feature development via the SDD methodology, or runs /sdd-flow with a task description. Takes a task or software requirement and drives it through the complete SDD lifecycle (Research → Planning → Implementation → Done) via subagents with fresh context per phase. Self-contained: ships its own forked phase bodies, agents, and hooks — the SDD plugin is NOT required and need not be installed. Integrates cross-cutting-adr at research/planning boundaries, a two-stage specialist panel during planning, and regression-eval scaffolding at implementation completion; spec frontmatter (review_panel, eval_required, cross_cutting_decisions, delivery_mode) gates each."
---

# SDD Flow — End-to-End Feature Development

Takes a task or software requirement and drives it through the complete SDD (Specification-Driven Development) lifecycle: **Research → Planning → Implementation → Done**.

This skill is the **single source of truth** for the flow. It is **self-contained**: every per-phase instruction set ("body") lives under `skills/sdd-flow/bodies/`, every spawned agent ships in `agent-engineering/agents/`, and the transcript hook ships in `agent-engineering/hooks/`. The SDD plugin does **not** need to be installed — nothing here reads from it at runtime.

The main conversation is a lightweight **orchestrator**: it spawns one subagent per phase / review / fix / capture step, giving each a fresh context window so no manual `/clear` is ever needed. All inter-phase communication happens through the **SDD artifact files on disk** (see Artifact Paths). Every spawn prompt hands the subagent resolved paths plus the absolute path of the body file it must read first.

## Usage

```
/sdd-flow <task or requirement description>
/sdd-flow #42 Add CSV export to the reports page
/sdd-flow --auto #15 Implement allow-list management UI
/sdd-flow continue
```

## The one-level-spawning contract (read this first)

Claude Code permits **exactly one level of subagent nesting**. Every spawn happens here, at the orchestrator (main-conversation) level. **Spawned subagents cannot spawn subagents** (the Agent/Task tool is inert inside them) and **cannot invoke slash commands or skills.** Consequences that shape this whole skill:

- The orchestrator does discovery sweeps inline only via the subagent it spawns; subagents do their own file discovery **inline** (Grep/Glob/Read), never by delegating.
- There is **no nested-subagent counter** anywhere. The only safety-net counter is **Reads**.
- Bodies are pre-adapted for inline execution — there is nothing to "strip" at runtime and no command to embed. The orchestrator passes each body **by path**, never by pasting its content.

## SKILL_ROOT resolution (Step 0)

At Step 0 the orchestrator resolves **SKILL_ROOT** = the absolute path of this skill's own directory, and records it in `SDD/orchestration/progress.md` so resumed sessions re-derive every body path. Resolution order:

1. **Plugin cache:** `~/.claude/plugins/cache/pablooliva/agent-engineering/<latest-version>/skills/sdd-flow` (pick the highest version dir).
2. **Dev/repo checkout:** the `agent-engineering/skills/sdd-flow` directory of the working repo.

Every body path in a spawn prompt is the **resolved absolute** `SKILL_ROOT/bodies/<file>.md`. Compact bodies are passed the same way (read only if the Safety-Net trips).

## Canonical Identifiers (resolved at Step 0)

| Identifier | Description | Example |
|---|---|---|
| `[###]` | Issue/ticket number or sequential ID | `042` |
| `[feature-name]` | Kebab-case feature name | `audit-logging` |
| `[YYYY-MM-DD]` | Current date | `2026-06-11` |
| `[YYYY-MM-DD_HH-MM-SS]` | Timestamp (24h, underscores) | `2026-06-11_14-30-45` |

## Artifact Paths

Every subagent MUST use these exact paths; the orchestrator resolves `[###]`/`[feature-name]`/dates before embedding them.

| Artifact | Path | Created By | Read By |
|---|---|---|---|
| Scope decomposition | `SDD/flow/DECOMPOSITION-[###]-[feature-name].md` | Scope subagent | User |
| Clarification doc | `SDD/research/CLARIFICATION-[###]-[feature-name].md` | User (`/research-clarify`) | Research, Research review |
| Ubiquitous glossary | `SDD/UBIQUITOUS_LANGUAGE.md` | research-complete + planning-complete (incremental) | All phase subagents |
| Research doc | `SDD/research/RESEARCH-[###]-[feature-name].md` | Research subagent | Research review, Planning |
| Research critical review | `SDD/reviews/CRITICAL-RESEARCH-[feature-name]-[YYYYMMDD].md` | Research review | Research fix |
| Specification | `SDD/requirements/SPEC-[###]-[feature-name].md` | Planning subagent | Panel, Planning review, Implementation |
| **Panel findings (per specialist)** | `SDD/reviews/PANEL-FINDINGS-[panel-value]-[feature-name]-[YYYYMMDD].md` | Each specialist (Stage 1) | Panel synthesis (Stage 2) |
| Spec panel review | `SDD/reviews/PANEL-SPEC-[feature-name]-[YYYYMMDD].md` | Panel synthesis (Stage 2) | Planning fix |
| Spec critical review | `SDD/reviews/CRITICAL-SPEC-[feature-name]-[YYYYMMDD].md` | Planning review | Planning fix |
| ADRs / ADR index | `SDD/adr/NNNN-slug.md`, `SDD/adr/README.md` | adr-capture subagent | Future runs, humans |
| Eval scaffolding | `evals/datasets/[feature-slug].json`, `evals/evaluators/...`, `evals/run_functions/...`, `evals/README.md` | eval-capture subagent | Future regression runs |
| Implementation plan | `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[YYYY-MM-DD].md` | Implementation subagent | Code review, Impl review, Completion |
| Slice file | `SDD/implementation/slices/SLICE-[###]-[NN]-[slice-name]-[YYYY-MM-DD].md` | slice-start subagent | per-slice cycle |
| Slice review / retro / ledger | `SDD/reviews/REVIEW-SLICE-*`, `SDD/implementation/slices/RETROSPECTIVE-SLICE-*`, `SDD/implementation/slices/LEARNINGS-FEATURE-[feature-name].md` | per-slice subagents | next slice, end-of-feature |
| Code review | `SDD/reviews/REVIEW-[###]-[feature-name]-[YYYYMMDD].md` | Code review | Impl fix |
| Impl critical review | `SDD/reviews/CRITICAL-IMPL-[feature-name]-[YYYYMMDD].md` | Impl review | Impl fix |
| Implementation summary | `SDD/implementation/summaries/IMPLEMENTATION-SUMMARY-[###]-[YYYY-MM-DD_HH-MM-SS].md` | Completion | — |
| Counter file | `SDD/orchestration/counters/[step-id]-[chunk-or-iter]-[YYYY-MM-DD_HH-MM-SS].md` | Orchestrator (per spawn) | The spawned subagent only |
| Compaction file | `SDD/orchestration/compacted/[phase]-compacted-[YYYY-MM-DD_HH-MM-SS].md` | Subagent on Safety-Net trip | Continuation subagent |
| Progress file | `SDD/orchestration/progress.md` | All subagents (append only) | All subagents, orchestrator |

```
SDD/
├── UBIQUITOUS_LANGUAGE.md
├── adr/{NNNN-slug.md, README.md}
├── flow/DECOMPOSITION-[###]-[feature-name].md
├── research/{CLARIFICATION-*, RESEARCH-*}.md
├── requirements/SPEC-[###]-[feature-name].md
├── implementation/
│   ├── IMPLEMENTATION-PLAN-*.md
│   ├── slices/{SLICE-*, RETROSPECTIVE-SLICE-*, LEARNINGS-FEATURE-*}.md   # per-slice mode only
│   └── summaries/IMPLEMENTATION-SUMMARY-*.md
├── orchestration/{progress.md, subagent-calls/, counters/, compacted/}
└── reviews/{CRITICAL-RESEARCH-*, PANEL-FINDINGS-*, PANEL-SPEC-*, CRITICAL-SPEC-*,
            CRITICAL-IMPL-*, REVIEW-*, REVIEW-SLICE-*}.md
evals/{README.md, datasets/, evaluators/, run_functions/}   # only when eval_required: true
```

## Orchestrator Discipline (the load-bearing core)

**The orchestrator MUST NOT execute phase, review, fix, capture, or completion work directly.** Every numbered sub-step runs inside a spawned subagent — even ones that "look small." The orchestrator's only direct work: spawning subagents, running commits (per `commands/commit.md`), writing user-facing checkpoint messages, and recording state in `progress.md`. The orchestrator has no `/clear`; subagent boundaries are the only context reset.

- **Bounded returns.** Every subagent returns **≤200 words + artifact paths**. The orchestrator reads artifact files only when a decision genuinely needs them (e.g. spec frontmatter to route Step 4).
- **progress.md is append-only.** Never overwrite or delete prior content.
- **Explicit resolved paths in every spawn prompt** — never let a subagent guess artifact locations.
- **Per-phase sizing:** Research — single subagent (scope unknown until investigated); pre-split per-layer only if the task obviously cuts across >2 architectural layers. Planning — single subagent; pre-split only if RESEARCH >1000 lines or >3 disjoint subsystems. Implementation (whole-feature) — count SPEC items `REQ-XXX`+`EDGE-XXX`+`FAIL-XXX`; if >8, pre-split into ⌈total/5⌉ sequential chunks, each appending to IMPLEMENTATION-PLAN. **Per-slice mode: one subagent per slice, strict, no bundling** — REQ-count chunking does NOT apply.

### Progress Hygiene (rotation + bounded appends)

`progress.md` sits in the read path of nearly every spawn and of phase detection — its size is paid on every read. Three rules keep it bounded:

1. **Rotate at feature completion (Step 4j).** Move the finished feature's full history to `SDD/orchestration/progress-archive/progress-SPEC-[###]-[YYYY-MM-DD_HH-MM-SS].md`; leave a one-line summary (feature, outcome, artifact pointers). The live file carries full history ONLY for the active feature.
2. **Checkpoint on size.** If the live file exceeds **~500 lines**, rotate at the next quiet point (a phase-boundary commit — 2e, 3f, 4i, per-slice 4c.6): archive resolved verbose blocks, rewrite the head as a bounded `## Current State` (phase status, artifact pointers, archive path). **Pending halt blocks (`## Awaiting *`, `## PARTIAL: needs continuation`) are carried forward verbatim as the latest blocks** — phase detection matches the latest block in the live file and never scans archives.
3. **Bounded appends.** Subagent progress entries are **≤10 lines**: status, artifact paths, one-line key decision, anything pending. Narrative belongs in the artifact the subagent wrote, referenced by path.

Rotation is **orchestrator-only**, happens only between spawns (never mid-subagent), and is recorded in the fresh head. Append-only applies *within* a generation; rotation starts a new one. Full procedure: `phases/protocols.md` → Progress Rotation.

### Subagent Safety-Net Rule (embed verbatim in every phase-execution, fix, and continuation prompt)

> **Bail-out trigger (a trigger, not a budget to spend):** you have Read more than **15** files (implementation chunks: more than **20**).
>
> **When it fires, stop immediately.** Read the compact-body path given in your prompt (under "Compact instructions — use only if the Safety-Net trips") and follow it: write `SDD/orchestration/compacted/[phase]-compacted-[YYYY-MM-DD_HH-MM-SS].md`, append a `## PARTIAL: needs continuation` block to `progress.md` with the compaction file path and where you left off, and return ≤100 words stating a Mid-Phase Handoff is required.
>
> **Counter tracking.** You cannot inspect your own tool-call history. The orchestrator gives you a **dedicated counter file** (path in your prompt under "Your counter file"). It holds exactly one line: `Reads: 0/15`. Update it immediately after each Read; check it (cheap Read) before each new Read — that is the trigger evaluation. The counter file is scoped to your run only; never shared, never written to `progress.md`.

**Orchestrator obligation per spawn of a phase-execution / fix / continuation subagent:** (1) embed the Safety-Net Rule verbatim; (2) create the counter file at `SDD/orchestration/counters/[step-id]-[chunk-or-iter]-[YYYY-MM-DD_HH-MM-SS].md` with the single line `Reads: 0/15` (use `/20` for implementation chunks) and pass its path under "Your counter file"; (3) pass the matching compact body path (`SKILL_ROOT/bodies/[phase]-compact.md`) under "Compact instructions — use only if the Safety-Net trips". Counter is **Reads-only** — a subagent can never spawn, so there is no nested-subagent count. Defaults (15 / 20) are tunable without changing the protocol.

### Spawn-prompt construction checklist

Every spawn prompt includes: (1) the **absolute body path** `SKILL_ROOT/bodies/<file>.md` with "Read this file FIRST — it is your complete instruction set"; (2) all resolved input + output artifact paths; (3) the task description + canonical identifiers; (4) "verify input files exist before starting; create parent dirs before writing; append (never overwrite) progress.md — entry ≤10 lines: status, artifact paths, one-line key decision, anything pending; narrative stays in your artifacts"; (5) for phase-execution/fix/continuation subagents — the Safety-Net Rule + counter-file path + compact body path; (6) the bounded-return contract (≤200 words + paths).

## Model Routing

Routing is carried by **shipped agent frontmatter** — no runtime model switching. The orchestrator MAY escalate a single spawn via the Agent tool's per-spawn model override.

| Spawn site | Agent type | Model |
|---|---|---|
| Research, planning, ADR capture, fixes, impl chunks, code review, completion, eval, slice cycle | `agent-engineering:sdd-workhorse` | sonnet |
| Each panel specialist (Stage 1) | `agent-engineering:sdd-spec-<panel>-specialist` | sonnet |
| Research/spec/impl critical review; panel synthesis (Stage 2) | `agent-engineering:sdd-critical-reviewer` | opus |

The workhorse's escalation protocol stays: if a task needs Opus depth, it surfaces "needed Opus depth" in its bounded return and the orchestrator re-spawns (or per-spawn-overrides) at Opus.

## State Machine

Evaluate top-to-bottom. At each step boundary, **read the named phase file before acting** — it holds the per-step spawn briefs, checkpoint templates, and halt semantics.

| Step | What | Read now |
|---|---|---|
| 0 | Scope assessment → resolve identifiers + SKILL_ROOT | `phases/setup.md` |
| 1 | Parse input, select mode (supervised default / `--auto`) | `phases/setup.md` |
| 1.5 | Pre-research clarification gate (fires in BOTH modes) | `phases/setup.md` |
| 2 | Research (2a–2f) | `phases/research.md` |
| 3 | Planning (3a–3g; two-stage panel + bounded fix loop) | `phases/planning.md` |
| 4 | Implementation — route on spec `delivery_mode:` | read the matching file ↓ |
| 4 · whole-feature (default) | 4a–4j | `phases/implementation-whole-feature.md` |
| 4 · per-slice | per-slice cycle + end-of-feature cycle | `phases/implementation-per-slice.md` |
| done | Final announcement | — |
| `continue` / resumption / handoffs / errors | Phase detection + protocols | `phases/protocols.md` |

## Arguments

| Argument | Description |
|---|---|
| `<task>` | The task, requirement, or feature description |
| `--auto` | Fully autonomous (no checkpoints except the mandatory Step 1.5 clarification gate) |
| `--supervised` | Supervised mode with checkpoints (default) |
| `--skip-clarify` | Suppress the Step 1.5 clarification gate; gate-skip recorded in the Step 2c review |
| `--skip-slice-checkpoints` | Suppress per-slice pauses (default ON in per-slice mode). The re-planning halt fires regardless |
| `--fall-back-to-whole-feature` | With `continue` after a practicality-gate halt: flip `delivery_mode` to whole-feature |
| `--retry-slicing "<hint>"` | With `continue` after a practicality-gate halt: re-run slice extraction with a hint |
| `--replan` | With `continue` after a re-planning halt: re-run Step 3 with ledger + triggering retro |
| `--from-slice SLICE-XXX` | With `--replan`: resume from a named slice in the NEW plan (validated post-replan) |
| `--override-replan` | With `continue` after a re-planning halt: continue on the current plan. Cannot combine with `--replan` |
| `continue` | Resume from the last interruption point (see `phases/protocols.md`) |

## Key Principles

1. **Each phase is thorough** — research informs planning; planning constrains implementation.
2. **Every requirement gets a test.** Reviews are gates, not checkboxes — ALL findings (HIGH/MEDIUM/LOW) resolved before proceeding.
3. **Panel STOP/REVISE halts the flow, but the fix loop is bounded** — max 3 iterations; any iteration that fails to strictly decrease the gating finding count halts. Unresolvable findings route back to the human.
4. **ADRs compound across features; evals scaffold (humans populate); the spec is the source of truth; document deviations.**
5. **Never persist PII or secrets in SDD docs. Commit messages have NO co-author attribution.**
6. **Explicit paths always; the orchestrator never does phase/review/fix/capture/completion work itself.**
7. **Per-slice cycle is strict** — one subagent per slice, mandatory per-slice review, retro + ledger before the atomic per-slice commit. Slice subagents receive ONLY the rolling ledger.
8. **Re-planning recommendations halt the flow regardless of `--skip-slice-checkpoints` and mode.**

Session resumption, mid-phase handoff, phase-detection priority, and error handling all live in `phases/protocols.md`.
