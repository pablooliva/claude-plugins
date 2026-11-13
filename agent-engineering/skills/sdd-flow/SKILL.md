---
name: sdd-flow
description: "INVOKE THIS SKILL when the user asks to run end-to-end feature development via the SDD methodology, or runs /sdd-flow with a task description. Takes a task or software requirement and drives it through the complete SDD lifecycle (Research → Planning → Implementation → Done) via subagents with fresh context per phase. Self-contained: ships its own forked phase bodies, agents, and hooks — the SDD plugin is NOT required and need not be installed. Stops after research at a design gate: a short design brief the user must approve before any spec is written, which proposes three delivery tiers and builds Tier 1 unless told otherwise. Integrates cross-cutting-adr at research/planning boundaries, a two-stage specialist panel during planning, and OWASP AI-agent security review for agentic features (spec panel, code-review lens). Reviews are run by a second model family (the Codex CLI) with a marked fallback to Claude reviewers when it is not available; spec frontmatter (review_panel, cross_cutting_decisions, delivery_mode, agent_security, tracing, evals, tier) gates each."
---

# SDD Flow — End-to-End Feature Development

Drives a task through the SDD (Specification-Driven Development) lifecycle: **Research → Design gate → Planning → Implementation → Done**.

This skill is the **single source of truth** for the flow, and **self-contained**: bodies (the instruction set of each spawned step) are under `skills/sdd-flow/bodies/`, agents in `agent-engineering/agents/`, the transcript hook in `agent-engineering/hooks/`. Nothing is read from the SDD plugin at runtime.

The main conversation is a lightweight **orchestrator**: it spawns one subagent per phase / review / fix / capture step, each with a fresh context, so no `/clear` is needed. A review step runs on a second model through its command-line agent instead (Second-Model Review below). Steps communicate only through the **SDD files on disk**; every spawn prompt gives resolved paths and the absolute path of the body to read first.

**What to read when.** This file at every step, plus the phase chapter the State Machine names. A rare case — resume, handoff, rotation, re-plan, next tier, decomposition, tier mirror — reads its own file only when it happens. Artifact paths a chapter does not give: `phases/artifact-paths.md`.

## Usage

```
/sdd-flow <task or requirement description>
/sdd-flow #42 Add CSV export to the reports page
/sdd-flow --tier 2 #42 Add CSV export to the reports page
/sdd-flow --next-tier csv-export
/sdd-flow continue
```

| Argument | Description |
|---|---|
| `<task>` | The task, requirement, or feature description |
| `--tier N` | Have the design brief recommend Tier N (1, 2, or 3) instead of Tier 1. The tier can still be changed at the design gate |
| `--next-tier [feature-name]` | Start a new cycle for the next unshipped tier in `SDD/flow/TIERS-[feature-name].md` (`phases/rare/next-tier.md`) |
| `continue` | Resume from the last interruption point (`phases/rare/resume.md`) |

The flow stops only where the user has something to decide or try: the clarification question, the design gate, a spec that departs from the brief, a pause after each slice, an unresolved finding, and a sign-off. Anything else is said in words at those stops — a re-plan is asked for at a slice pause.

## The one-level-spawning contract (read this first)

**Exactly one level of subagent nesting.** Every spawn happens here, at the orchestrator. **Spawned subagents must not spawn subagents and must not invoke slash commands or skills.** They do their own file discovery **inline** (Grep/Glob/Read). So there is **no nested-subagent counter** — the only safety-net counter is **Reads** — and bodies are pre-adapted for inline execution: the orchestrator passes each body **by path**, never by pasting it.

> **Version note (2026-06-12):** on Claude Code ≤2.1.171 this was a platform limit; from **2.1.172** (2026-06-09) nesting to depth 5 is allowed, and the flow **deliberately does not use it** (flat orchestration keeps every spawn observable and all state in `progress.md`). Do not "fix" bodies or agents to delegate; read `proposals/nested-subagents-analysis-2026-06-12.md` before any refactor.

## SKILL_ROOT resolution (Step 0)

At Step 0 the orchestrator resolves **SKILL_ROOT**, this skill's absolute directory — first the plugin cache `~/.claude/plugins/cache/pablooliva/agent-engineering/<highest-version>/skills/sdd-flow`, else the working repo's `agent-engineering/skills/sdd-flow` — and **PLUGIN_ROOT** = `SKILL_ROOT/../..`. Every body path in a prompt is the resolved absolute `SKILL_ROOT/bodies/<file>.md`; compact bodies are passed the same way (read only if the Safety-Net trips). From them it derives, all resolved absolute:

| Name | Path | What it is · passed to |
|---|---|---|
| **CATALOG** | `PLUGIN_ROOT/skills/ai-agent-security-review/references/owasp-ai-agent-controls.md` | The OWASP AI-agent control catalog · the `agent-security` panel specialist (3c); the agentic lens of the code review and slice review (4b) |
| **SECURITY** | `SKILL_ROOT/references/security-verification.md` | Security rules, the final check's security verification, proving tests · every implementation spawn, the 4e.5 final check and its fix, the completion spawn |
| **TEST_INTEGRITY** | `SKILL_ROOT/references/test-integrity.md` | What a real test is; the Test Integrity Lens · every implementation, code-review, slice-review, and fix spawn of Step 4 (`phases/implementation-inputs.md` → Test integrity inputs) |
| **FIT** | `SKILL_ROOT/references/fit-lens.md` | The Fit Lens (fit and size) · every code-review, slice-review, and fix spawn of Step 4 |
| **EVALS** | `SKILL_ROOT/references/evals.md` | What an eval is (a written example put to the running application; a check of what the model really answered), its two kinds, its cases, its run · design-brief, planning, and planning-completion spawns when the application has the tracing foundation; with the `evals` gate on, also the spec-review and spec-fix spawns (`phases/planning.md`), every implementation, review, and fix spawn of Step 4 (the 4e.5 final check and its fix included), and the completion spawn (`phases/implementation-inputs.md` → Evals inputs) |
| **EVAL_TEMPLATES** | `SKILL_ROOT/templates/evals/` | The files an application's eval run is rendered from · with EVALS, to Step 4 spawns |
| **TIERS** | `PLUGIN_ROOT/skills/simplicity-challenge/references/tiers.md` | The tier standard (tiers, floor, cut tests, tier-plan shape), owned by `simplicity-challenge` · design-brief, planning, spec-review, spec-fix, code-review, completion spawns |
| **TRACING** | `PLUGIN_ROOT/skills/observability-init/references/tracing.md` | The tracing standard, owned by `observability-init` · the planning spawn when the application has the tracing foundation; with the `tracing` gate on, the spec-review and spec-fix spawns and every implementation, review, and fix spawn of Step 4 |

CATALOG, TIERS, and TRACING are read here and never restated. Record SKILL_ROOT, CATALOG, TIERS, and TRACING in the Step 0 record in `SDD/.records/progress.md`, with the line `Reviewer: …` (Second-Model Review below), so a resumed session re-derives every path; the others are derived from SKILL_ROOT wherever needed and never recorded. Every one of them ships in this plugin: a missing one is a broken install — halt and tell the user.

**Whether the application has the tracing foundation** — **OBS_RECORD** = `SDD/OBSERVABILITY.md`, written by `/observability-init` — **is settled at the design gate, not at Step 0.** The orchestrator looks for it before each design-brief spawn (when the feature calls a model and it is absent, the brief recommends running `/observability-init` before approving), and on approval records `Observability record: present` or `absent`. That line decides the cycle's `tracing:` and `evals:` gates (`phases/design-gate.md` → 2.5b, `phases/planning.md` → 3c). Absent is not an error: both gates are off and the cycle runs as in an application without tracing.

## Canonical Identifiers (resolved at Step 0)

| Identifier | Description | Example |
|---|---|---|
| `[###]` | Issue/ticket number or sequential ID | `042` |
| `[feature-name]` | Kebab-case feature name | `audit-logging` |
| `[YYYY-MM-DD]` | Current date | `2026-06-11` |
| `[YYYY-MM-DD_HH-MM-SS]` | Timestamp (24h, underscores) | `2026-06-11_14-30-45` |

**Records stay out of git.** Everything under `SDD/.records/` — progress, reviews, counters, reviewer and subagent call logs, eval results, trace trees, compaction files — is a process record: it is git-ignored and no commit ever includes it. Whoever creates `SDD/.records/` first (Step 0, a compact command, the subagent-log hook) writes `SDD/.records/.gitignore` holding the one line `*`. The brief, spec, plan, slice files, ADRs, glossary, tier plan, and summary are what history keeps. The records live only in the checkout that ran the flow; `worktree-merge` copies a worktree's records into the main checkout before the worktree goes away.

## Orchestrator Discipline (the load-bearing core)

**The orchestrator MUST NOT execute phase, review, fix, capture, or completion work directly.** Every numbered sub-step runs in a spawned subagent, even one that "looks small." The orchestrator's only direct work:

- spawning subagents, and running a review step's second-model reviewer (`scripts/second-model-review.py` — it starts the reviewer, as a spawn would; the review is the reviewer's);
- commits (per `commands/commit.md`);
- the fix-round snapshots (`scripts/snapshot.py`);
- the tier task mirror (`scripts/tier-mirror.py`, `phases/tier-mirror.md`);
- growth against the brief's budget at the slice pause and before the final commit (`scripts/growth.py`; it prints three lines, and the orchestrator reads no code to get them);
- with the `evals` gate on, the eval run of record before a review (the application's own eval command, from one row of `SDD/OBSERVABILITY.md`; it reads the last line printed, never the results — `phases/implementation-inputs.md` → *The eval run of record*);
- user-facing checkpoint messages, and state in `progress.md`;
- the mechanical edits the phase files give it by name: an addition's `declined` marker in the PANEL-SPEC on `approve` at the stop after the spec; a slice's row to `Complete` before its commit; after a re-plan, archiving the old slice table and moving the replaced plan's slice files aside.

The orchestrator has no `/clear`; subagent boundaries are the only context reset.

- **Bounded returns.** Every subagent returns **≤200 words + artifact paths**. The orchestrator reads an artifact only when a decision needs it (e.g. spec frontmatter to route Step 4).
- **progress.md is append-only** within a generation — never overwrite or delete prior content. Only the orchestrator rotates it, between spawns: at feature completion (4j) and when it passes **~500 lines** at a quiet point (a phase-boundary commit — 2e, 3f, 4i, per-slice 4c.6); procedure in `phases/rare/rotation.md`. A rotation carries pending halt blocks (`## Awaiting *`, `## PARTIAL*` — prefix match) forward verbatim as the latest blocks, since phase detection reads only the live file. Subagent entries are **≤10 lines** — status, artifact paths, a one-line key decision, anything pending; narrative stays in the artifact. (One exception: an `## ADR Candidates` entry lists every candidate, one line each — it is the only record the design gate reads.)
- **Explicit resolved paths in every spawn prompt** — never let a subagent guess a location.
- **Per-phase sizing:** Research — one subagent; pre-split per layer only if the task obviously cuts across >2 architectural layers. Planning — one subagent; pre-split only if RESEARCH >1000 lines or >3 disjoint subsystems. Whole-feature implementation — count SPEC `REQ-XXX`+`EDGE-XXX`+`FAIL-XXX`; if >8, pre-split into ⌈total/5⌉ sequential chunks, each appending to IMPLEMENTATION-PLAN (`phases/implementation-whole-feature.md` → Sizing). **Per-slice: one subagent per slice, strict, no bundling** — REQ-count chunking does NOT apply.

### What a body may do (the prompt's paths are the only inputs)

The bodies were forked from commands a person runs by hand. Inside the flow every body is held to these rules, and an edit to a body is checked against them:

- **Inputs come from the prompt.** A body never lists a directory to find or choose its spec, research document, or plan — a repository holds several of each once a second feature or tier exists, and only the orchestrator knows which is active.
- **A body never commits.** Every commit is the orchestrator's (2e, 3f, 4i, per-slice 4c.6), and comes after the review of what it contains: a slice or feature is one commit. (An early commit would not hide changes from the reviews, which diff against the recorded base commit — it would put unreviewed code into history and bypass the commit checkpoint.)
- **A body never resets, rewrites, or archives `progress.md`.** It appends.
- **A body that cannot proceed returns a failure** — an input missing or unreadable, a precondition not met, a choice it has no authority to make — in its bounded return, and writes no stop note. The orchestrator handles it under Error Handling (`phases/protocols.md`).
- **A body writes only one stop note,** `## PARTIAL: needs continuation` — the compact bodies on a Safety-Net trip. Every `## Awaiting …` block is written by the orchestrator.

### Who declares a phase done (markers, stops, resume)

**Only the orchestrator declares a phase done, and only after the phase's last step.** A completion subagent's banner (`Planning Phase - COMPLETE`, `Implementation Phase - COMPLETE`) says only that its own work is finished — the reviews, fixes, and commit after it are still to come. Each phase ends with a marker the orchestrator writes:

| Phase | Done when the orchestrator has written | Written at |
|---|---|---|
| Research | `## Research - Accepted` | after the 2e commit |
| Planning | `## Planning - Accepted` | 3g, when the owner approves the spec at the stop after it |
| Implementation | `## Implementation - Committed`, then `## Feature - Done` | after the 4i commit; after the 4j announcement |

Three rules go with it, and an edit to a phase file is checked against them:

- **Resume reads the current feature only.** Step 0 opens each feature's record with `## Flow Started - [###]-[feature-name]`; Phase Detection reads only what follows the latest one.
- **Every stop that waits for an answer has a halt block, a resume rule, and a diagram row.** The stop writes a block to `progress.md` before it asks; `phases/rare/resume.md` has the rule that resumes it; `docs/sdd-flow-diagram.md` lists it. A latest halt block always wins over a phase rule; one with no rule of its own falls to the catch-all there — shown to the user verbatim, never guessed past. (Stops that need no answer — the slice pause, and terminal stops such as decomposition — write none; `phases/rare/resume.md` lists them.)
- **A handoff passes what a fresh spawn would.** A continuation or a re-review is given the same inputs — the step's body and mode, paths, `SCOPE`, `ITER`, the base commit, a fix round's snapshots, allow-lists — as the first spawn of that step, stated explicitly, and is the agent type that first spawn was, with its model override (`phases/rare/handoff.md`).

The full marker table and the rules are in `phases/rare/resume.md` → Phase Detection Priority.

### Who owns the slice path (state changes, stops, commits)

**Every slice state change, stop, and commit has a named owner.** The per-slice path has the most hand-offs — a slice's row moves through four states, and its cycle ends in a commit or a fix-loop stop — and a step each side assumes the other performs is a step nobody performs. An edit to a slice body or to `phases/implementation-per-slice.md` is checked against two rules:

- **The owner table there ("Who owns what on the slice path") is complete.** Every status of the slice table, every `## Slice SLICE-XXX - …` marker, every stop, and the commit appear with one owner and one step; a new one is added to the table in the same edit.
- **A body describes what it does — never what "the orchestrator may" do.** A body that needs something done outside its run says what it leaves behind (a status, a marker, a file); the phase chapter says who acts on it and when.

A slice's cycle has exactly two kinds of end: its commit (4c.6, which also sets its row to `Complete`) or a halt block with a resume rule (`## Awaiting Slice Resolution`). A session that ends between is resumed from the slice markers (`phases/rare/resume.md` → per-slice cycle sub-steps).

### Second-Model Review (who runs a review)

**A review is run by a different model family than wrote what it reviews.** Claude subagents write everything a cycle produces, so each review step — 3d, the 3e.5 check of the spec fix, the slice review, the feature code review (4b), and the 4e.5 final check — goes to a second model through its CLI: the Codex CLI. `references/second-model-review.md` is the one definition (the review steps, and why the 3c panel stays on Claude; how the reviewer is settled at Step 0 and recorded as `Reviewer: …`; the prompt preamble; the call to `scripts/second-model-review.py`; what to do with each result). Read it at Step 0 and before the first review step; phase chapters point to it and never restate it. Whichever model reviews, and an edit to a review step is checked against this:

- **Same prompt, same outputs, same markers.** The second model gets exactly what the step's Claude spawn would, after a fixed preamble; it reads the same body by path, writes the same review document, and appends the same marker. Nothing downstream knows or asks which route ran.
- **The fallback is never silent and never halts.** No Codex CLI, or a run that fails twice, puts the review on the Claude subagent the phase chapter names; the line saying so goes to `progress.md` and to the user. Every review document carries a `Reviewed by:` line.
- **A review changes no code.** The script records the working tree before a second-model run and puts back any file outside `SDD/` the reviewer changed.

### Subagent Safety-Net Rule (embed verbatim in every phase-execution, fix, and continuation prompt)

A review run on the second model carries none of it — no rule, counter file, or compact path (`references/second-model-review.md` §3): the reviewer's CLI manages its own context.

> **Bail-out trigger (a trigger, not a budget to spend):** you have Read more than **15** files (implementation chunks: more than **20**).
>
> **When it fires, stop immediately.** Read the compact-body path given in your prompt (under "Compact instructions — use only if the Safety-Net trips") and follow it: write `SDD/.records/compacted/[phase]-compacted-[YYYY-MM-DD_HH-MM-SS].md`, append a `## PARTIAL: needs continuation` block to `progress.md` with the compaction file path and where you left off, and return ≤100 words stating a Mid-Phase Handoff is required.
>
> **Counter tracking.** You cannot inspect your own tool-call history. The orchestrator gives you a **dedicated counter file** (path in your prompt under "Your counter file"). It holds exactly one line: `Reads: 0/15`. Update it immediately after each Read; check it (cheap Read) before each new Read — that is the trigger evaluation. The counter file is scoped to your run only; never shared, never written to `progress.md`.

**Per spawn of a phase-execution / fix / continuation subagent, the orchestrator:** (1) embeds the rule verbatim; (2) creates the counter file `SDD/.records/counters/[step-id]-[chunk-or-iter]-[YYYY-MM-DD_HH-MM-SS].md` holding `Reads: 0/15` (`/20` for implementation chunks) and passes its path under "Your counter file"; (3) passes the matching compact body `SKILL_ROOT/bodies/[phase]-compact.md` under "Compact instructions — use only if the Safety-Net trips". The defaults (15 / 20) are tunable without changing the protocol.

### Spawn-prompt construction checklist

Every spawn prompt includes: (1) the **absolute body path** `SKILL_ROOT/bodies/<file>.md` with "Read this file FIRST — it is your complete instruction set"; (2) all resolved input + output artifact paths; (3) the task description + canonical identifiers; (4) "verify input files exist before starting; create parent dirs before writing; append (never overwrite) progress.md — entry ≤10 lines: status, artifact paths, one-line key decision, anything pending; narrative stays in your artifacts"; (5) for phase-execution/fix/continuation subagents — the Safety-Net Rule + counter-file path + compact body path; (6) the bounded-return contract (≤200 words + paths).

## Model Routing

Routing of every writing and fixing step is carried by **shipped agent frontmatter** — no runtime model switching. **This needs Claude Code's Agent tool**; without it these agent types do not apply. In bb, the Claude Code provider setting `subagentsDisabled` hides that tool and must be `false` (`bb plugin config provider-claude-code set subagentsDisabled false`). The orchestrator MAY escalate a single spawn with the Agent tool's per-spawn model override. Review steps go to the second-model reviewer first; the agent types below for them are the **Claude route**.

Writing and fixing steps run on `agent-engineering:sdd-workhorse` (sonnet), with a per-spawn **opus** override for the implementer (whole-feature 4a and its chunks, per-slice 4a) and the design brief (2.5a, 2.5c). Panel specialists run on their shipped `sdd-spec-<panel>-specialist` agents (sonnet); panel synthesis and the Claude route of 3d, 3e.5, and 4b on `agent-engineering:sdd-critical-reviewer` (opus); the Claude route of the slice review and 4e.5 on the workhorse. A continuation after a handoff is the agent type, with the override, of the step it continues. Full table: `phases/model-routing.md`; each phase chapter also names the agent type of every spawn it makes. A workhorse that needs Opus depth says "needed Opus depth" in its bounded return, and the orchestrator re-spawns it at Opus.

## State Machine

Evaluate top-to-bottom. At each step boundary, **read the named phase file before acting** — it holds the per-step spawn briefs, checkpoint templates, and halt semantics.

| Step | What | Read now |
|---|---|---|
| 0 | Scope assessment → resolve identifiers + SKILL_ROOT + the reviewer | `phases/setup.md` + `references/second-model-review.md` |
| 1.5 | Pre-research clarification gate (asks every time unless a CLARIFICATION file exists) | `phases/setup.md` |
| 2 | Research (2a, 2b, 2e — research is not reviewed; the design gate is its check) | `phases/research.md` |
| 2.5 | Design gate — brief written, then a stop for approval (every time the brief is written or rewritten); the observability record is settled on approval | `phases/design-gate.md` + `phases/planning-inputs.md` |
| 3 | Planning (3a–3g; two-stage panel + bounded fix loop; 3g always stops: the owner approves the spec, after cutting it down if they choose) | `phases/planning.md` + `phases/planning-inputs.md` |
| 4 | Implementation — route on spec `delivery_mode:` | read the matching file ↓ |
| 4 · whole-feature (default) | 4a | `phases/implementation-whole-feature.md` + `phases/implementation-inputs.md` |
| 4 · per-slice | per-slice cycle (a pause after every slice) | `phases/implementation-per-slice.md` + `phases/implementation-inputs.md` |
| 4b–4j | End of feature, both delivery modes: code review, fixes, final check, completion, commit | `phases/end-of-feature.md` + `phases/implementation-inputs.md` |
| 4e.5 | Final check — security verification, last-look tests, trace and eval checks (both delivery modes) | `phases/end-of-feature.md` + `references/security-verification.md` |
| done | Commit (4h stops first only for a sign-off), then a short report | `phases/end-of-feature.md` |
| `continue` / resumption | Phase detection + the resume rule of every halt block | `phases/rare/resume.md` |
| handoff / rotation / re-plan / next tier / decomposition | Rare cases, each read only when it happens | `phases/rare/handoff.md`, `rotation.md`, `replan.md`, `next-tier.md`, `decomposition.md` |
| tier mirror | design-gate approval, 4h–4j, next-tier start (tiered features only) | `phases/tier-mirror.md` |
| errors | Error handling | `phases/protocols.md` |

## Key Principles

Each summarizes rules defined in the file it names; that file decides.

1. **Each phase is thorough** — research informs planning; planning constrains implementation.
2. **A review passes when no HIGH and no MEDIUM finding is open; LOW findings are listed for the owner, not fixed** (fixing them cost whole review rounds for little gain). Fit and size are review criteria like correctness: a file outside the brief's footprint is a finding, and a fit finding is fixed by removing code (`references/fit-lens.md`). A review after a fix round reads what the fix changed, not the whole scope (`bodies/slice-review.md` → Step 4.5); the final check (4e.5) reads everything. In a tiered spec, a finding that something is *absent* may be resolved under `## Deferred to Later Tiers`; one about behaviour the tier builds is always fixed.
3. **Panel STOP/REVISE halts the flow, but the fix loop is bounded** — max 2 iterations; an iteration that does not strictly decrease the gating finding count halts. Unresolvable findings go back to the human.
4. **ADRs compound across features; the spec is the source of truth; document deviations.**
5. **Never persist PII or secrets in SDD docs. Commit messages have NO co-author attribution.**
6. **Explicit paths always; the orchestrator never does phase/review/fix/capture/completion work itself.**
7. **The per-slice cycle is strict** — one subagent per slice, a mandatory slice review with every HIGH and MEDIUM resolved before the atomic per-slice commit. Earlier slices' committed code is the only context a slice carries forward.
8. **A stop is for a decision, never for reading code.** The user approves a design and tries each slice; the reviews read the code. A re-plan is asked for in words at a slice pause.
9. **Security rules are checked by an adversarial reader, once, at the end** — the final check on the second model, after the implementer proved each guard with a test that fails without it; at most two fix rounds, then the owner decides. Every mutation is made in a scratch copy, never in the repository. Standard: `references/security-verification.md`.
10. **The user approves a design and a size, then cuts the spec down.** Nothing is specified until the design brief — the one planning document written for a person, naming every new file, what the change builds on, and a growth budget — is approved. The spec is held to the brief; the panel may propose scope but never adds it. The flow stops after the spec for approval or cuts (`/simplicity-challenge`), and before the final commit when a feature is over 1.5× its budgeted lines.
11. **Tiers limit scope; nothing is built ahead.** Each tier is its own cycle with the same reviews, holding the simplest code that serves it. Standard: TIERS.
12. **The tier plan is the record; BB tasks mirror it**, and the user is told whenever the mirror could not run (`phases/tier-mirror.md`).
13. **In a traced application, what was planned to run is checked against what ran** (`tracing` gate on): a difference is fixed in the code or tests, or recorded as a deviation — the plan is never edited to match the run. Standard: `references/tracing-lens.md`.
14. **A green run proves nothing until the tests are shown to be real.** Implementers and fixers are held to one standard of a real test, the code and slice reviews run the Test Integrity Lens, and the final check always reads the tests once more. A HIGH lens finding rejects. Standard: `references/test-integrity.md`.
15. **The reviewer is not the author's model.** Spec, code, and tests are reviewed on a second model family (the panel alone stays on Claude); a Claude fallback says so in its document, in `progress.md`, and to the user. Standard: `references/second-model-review.md`.
16. **What a model says is checked on what it really answered, and only a person accepts a judge's score** (`evals` gate on). The spec states the cases before any code; the implementer builds them and never writes them; each review reads a fresh run of every case. A failing hard case is a failing test, fixed in the application, never by weakening the case. A judged score blocks nothing: the user accepts it at the commit checkpoint (4h). Standard: `references/evals.md`.
