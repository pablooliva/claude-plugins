---
name: sdd-flow
description: "INVOKE THIS SKILL when the user asks to run end-to-end feature development via the SDD methodology, or runs /sdd-flow with a task description. Takes a task or software requirement and drives it through the complete SDD lifecycle (Research → Planning → Implementation → Done) via subagents with fresh context per phase. Self-contained: ships its own forked phase bodies, agents, and hooks — the SDD plugin is NOT required and need not be installed. Stops after research at a design gate: a short design brief the user must approve before any spec is written, which proposes three delivery tiers and builds Tier 1 unless told otherwise. Integrates cross-cutting-adr at research/planning boundaries, a two-stage specialist panel during planning, and OWASP AI-agent security review for agentic features (spec panel, code-review lens). Reviews are run by a second model family (the Codex CLI) with a marked fallback to Claude reviewers when it is not available; spec frontmatter (review_panel, cross_cutting_decisions, delivery_mode, agent_security, tracing, evals, tier) gates each."
---

# SDD Flow — End-to-End Feature Development

Takes a task or software requirement and drives it through the complete SDD (Specification-Driven Development) lifecycle: **Research → Design gate → Planning → Implementation → Done**.

This skill is the **single source of truth** for the flow. It is **self-contained**: every per-phase instruction set ("body") lives under `skills/sdd-flow/bodies/`, every spawned agent ships in `agent-engineering/agents/`, and the transcript hook ships in `agent-engineering/hooks/`. The SDD plugin does **not** need to be installed — nothing here reads from it at runtime.

The main conversation is a lightweight **orchestrator**: it spawns one subagent per phase / review / fix / capture step, giving each a fresh context window so no manual `/clear` is ever needed. A review step is run on a second model through its command-line agent instead of a subagent (Second-Model Review below). All inter-phase communication happens through the **SDD artifact files on disk** (see Artifact Paths). Every spawn prompt hands the subagent resolved paths plus the absolute path of the body file it must read first.

## Usage

```
/sdd-flow <task or requirement description>
/sdd-flow #42 Add CSV export to the reports page
/sdd-flow --tier 2 #42 Add CSV export to the reports page
/sdd-flow --next-tier csv-export
/sdd-flow continue
```

## The one-level-spawning contract (read this first)

This flow uses **exactly one level of subagent nesting**. Every spawn happens here, at the orchestrator (main-conversation) level. **Spawned subagents must not spawn subagents** and **must not invoke slash commands or skills.**

> **Version note (2026-06-12):** on Claude Code ≤2.1.171 this was a platform limit (the Agent/Task tool was inert inside subagents). From **2.1.172** (2026-06-09) the platform allows nested subagents up to depth 5 — the flow **deliberately does not use it** (flat orchestration keeps every spawn observable and all state in `progress.md`). Do not "fix" bodies or agents to delegate; see `proposals/nested-subagents-analysis-2026-06-12.md` before any refactor.

Consequences that shape this whole skill:

- The orchestrator does discovery sweeps inline only via the subagent it spawns; subagents do their own file discovery **inline** (Grep/Glob/Read), never by delegating.
- There is **no nested-subagent counter** anywhere. The only safety-net counter is **Reads**.
- Bodies are pre-adapted for inline execution — there is nothing to "strip" at runtime and no command to embed. The orchestrator passes each body **by path**, never by pasting its content.

## SKILL_ROOT resolution (Step 0)

At Step 0 the orchestrator resolves **SKILL_ROOT** = the absolute path of this skill's own directory, and records it in `SDD/orchestration/progress.md` so resumed sessions re-derive every body path. Resolution order:

1. **Plugin cache:** `~/.claude/plugins/cache/pablooliva/agent-engineering/<latest-version>/skills/sdd-flow` (pick the highest version dir).
2. **Dev/repo checkout:** the `agent-engineering/skills/sdd-flow` directory of the working repo.

Every body path in a spawn prompt is the **resolved absolute** `SKILL_ROOT/bodies/<file>.md`. Compact bodies are passed the same way (read only if the Safety-Net trips).

The orchestrator also resolves **PLUGIN_ROOT** = `SKILL_ROOT/../..` (this skill lives at `<plugin>/skills/sdd-flow/`) and derives **CATALOG** = `PLUGIN_ROOT/skills/ai-agent-security-review/references/owasp-ai-agent-controls.md` — the OWASP AI-agent control catalog passed to the `agent-security` panel specialist (3c), and the code-review / slice-review agentic lens (4b). It also derives **SECURITY** = `SKILL_ROOT/references/security-verification.md` — what a security rule is, what the final check's security verification looks for, and what a proving test is — passed to every implementation spawn, the 4e.5 final check and its fix, and the completion spawn; it ships inside this skill, so a missing one is a broken install. It also derives **TEST_INTEGRITY** = `SKILL_ROOT/references/test-integrity.md` — what a real test is, and the Test Integrity Lens the reviews run — passed to every implementation, code-review, slice-review, implementation-critical-review, and fix spawn of Step 4 (`phases/implementation-whole-feature.md` → Test integrity inputs); it ships inside this skill, so a missing one is a broken install. It also derives **EVALS** = `SKILL_ROOT/references/evals.md` — the one definition of evals (a written example put to the running application, and a check of what the model really answered; the two kinds, how a case is written, what the eval run does and what its result means) — and **EVAL_TEMPLATES** = `SKILL_ROOT/templates/evals/`, the files an application's eval run is rendered from. EVALS is passed to the design-brief, planning, and planning-completion spawns when the application has the tracing foundation, and — when the `evals` gate is on — to the spec-review and spec-fix spawns (`phases/planning.md`) and to every implementation, review, and fix spawn of Step 4 — the 4e.5 final check and its fix included — with EVAL_TEMPLATES, and to the completion spawn (`phases/implementation-whole-feature.md` → Evals inputs). Both ship inside this skill and are derived from SKILL_ROOT wherever they are needed, so neither is written into the Step 0 record; a missing EVALS is a broken install. It also derives **TIERS** = `PLUGIN_ROOT/skills/simplicity-challenge/references/tiers.md` — the plugin's one tier standard (the three delivery tiers, the floor that is never deferred, the cut tests, the tier-plan shape), owned by the `simplicity-challenge` skill and read here, never restated; it is passed to the design-brief, planning, spec-review, spec-fix, code-review, and completion spawns. It also derives **TRACING** = `PLUGIN_ROOT/skills/observability-init/references/tracing.md` — the plugin's one tracing standard (which calls of an application get a span, what may be recorded on one, what an implementer does for the code it adds), owned by the `observability-init` skill and read here, never restated; it is passed to the planning spawn when the application has the tracing foundation, and — when the `tracing` gate is on — to the spec-review and spec-fix spawns and to every implementation, review, and fix spawn of Step 4. Record CATALOG, TIERS, and TRACING in `progress.md` alongside SKILL_ROOT, with the line `Reviewer: …` — which model family runs this cycle's reviews, settled once here (Second-Model Review below). TIERS, TRACING, and CATALOG ship in this plugin, so a missing one is a broken install: halt and tell the user.

**Whether the application has the tracing foundation** — **OBS_RECORD** = `SDD/OBSERVABILITY.md`, the record `/observability-init` writes into the application — **is settled at the design gate, not at Step 0.** The orchestrator looks for it before each design-brief spawn; when the feature calls a model and the record is absent, the brief recommends running `/observability-init` before approving. On approval the orchestrator looks once more and records `Observability record: present` or `Observability record: absent`; that line decides the `tracing:` and `evals:` gates for the cycle (`phases/planning.md` → 2.5b, 3c). An absent record is not an error: both gates resolve to off and the cycle runs as it does in an application without tracing.

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
| Design brief | `SDD/requirements/DESIGN-[###]-[feature-name].md` | Design-brief subagent (2.5a, 2.5c) | **The user**; Planning, Spec review, Spec fixes, Code review, Slice review |
| Tier plan | `SDD/flow/TIERS-[feature-name].md` (one per feature across all its tiers — a next-tier cycle keeps the first tier's name) | Design-brief subagent; Completion (4f) | Planning, the next tier's cycle |
| Specification | `SDD/requirements/SPEC-[###]-[feature-name].md` | Planning subagent | Panel, Planning review, Implementation |
| Observability record | `SDD/OBSERVABILITY.md` — only in an application that has the tracing foundation | The user, by running `/observability-init` outside the flow. A flow subagent writes one line of it: with the evals gate on, the implementer that builds the first eval fills its `Eval command` row | Orchestrator (before each design-brief spawn and on approval: is it there?; with the evals gate on, its `Eval command` row before each review); with the evals gate on, the implementer, the reviews (the 4e.5 final check included), and fix subagents — for the env file and the eval command; with the tracing gate on, the implementer, the reviews (the 4e.5 final check included), and fix subagents — for the trace run command, the span file, the env file, and the entry-point test — and the completion subagent, for where traces go |
| **Panel findings (per specialist)** | `SDD/reviews/PANEL-FINDINGS-[panel-value]-[feature-name]-[YYYYMMDD].md` | Each specialist (Stage 1) | Panel synthesis (Stage 2) |
| Spec panel review | `SDD/reviews/PANEL-SPEC-[feature-name]-[YYYYMMDD].md` | Panel synthesis (Stage 2) | Planning fix |
| Spec critical review | `SDD/reviews/CRITICAL-SPEC-[feature-name]-[YYYYMMDD].md` | Planning review | Planning fix |
| ADRs / ADR index | `SDD/adr/NNNN-slug.md`, `SDD/adr/README.md` | adr-capture subagent | Future runs, humans |
| Implementation plan | `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[YYYY-MM-DD].md` | Implementation subagent | Code review, Impl review, Completion |
| Trace tree (tracing gate on) | `SDD/reviews/TRACE-TREE-<SLICE-XXX\|FEATURE>-[feature-name]-[YYYYMMDD].md`, and `TRACE-TREE-FEATURE-[feature-name]-iter<N>-[YYYYMMDD].md` for the final check — the call tree a real run recorded, rendered by `scripts/trace-tree.py` | The review that runs the Tracing Lens (per-slice 4b, whole-feature 4b, and each 4e.5 final check) | The fix subagent that answers that review; the completion subagent (the last 4e.5 tree) |
| Eval results (evals gate on) | `SDD/reviews/EVAL-RESULTS-<SLICE-XXX\|FEATURE>-[feature-name]-iter<N>-[YYYYMMDD].md`, with a `.json` file of the same name beside it — what the model answered to each case in the run a review reads, written by the application's eval run | Orchestrator, by running the application's eval command before each review (per-slice 4b, whole-feature 4b, and each 4e.5 final check) | That review; the fix subagent that answers it; the completion subagent (the last 4e.5 run's results); the user at the commit checkpoint (4h), when the spec has a sign-off requirement |
| Final check review | `SDD/reviews/FINAL-CHECK-FEATURE-[feature-name]-iter<N>-[YYYYMMDD].md` | 4e.5 final check | 4e.5 fix, completion |
| Slice file | `SDD/implementation/slices/SLICE-[###]-[NN]-[slice-name]-[YYYY-MM-DD].md` | slice-start subagent | per-slice cycle |
| Slice review / retro / ledger | `SDD/reviews/REVIEW-SLICE-*`, `SDD/implementation/slices/RETROSPECTIVE-SLICE-*`, `SDD/implementation/slices/LEARNINGS-FEATURE-[feature-name].md` | per-slice subagents | next slice, end-of-feature |
| Code review | `SDD/reviews/REVIEW-[###]-[feature-name]-[YYYYMMDD].md` | Code review | Impl fix |
| Impl critical review | `SDD/reviews/CRITICAL-IMPL-[feature-name]-[YYYYMMDD].md` | Impl review | Impl fix |
| Implementation summary | `SDD/implementation/summaries/IMPLEMENTATION-SUMMARY-[###]-[YYYY-MM-DD_HH-MM-SS].md` | Completion | — |
| Reviewer call (second-model route) | `SDD/orchestration/reviewer-calls/[step-id]-[iter]-[YYYY-MM-DD_HH-MM-SS].{prompt.md, log, return.md}` | Orchestrator (prompt); `scripts/second-model-review.py` (log, return) | The reviewer's CLI (prompt); orchestrator (return) |
| Counter file | `SDD/orchestration/counters/[step-id]-[chunk-or-iter]-[YYYY-MM-DD_HH-MM-SS].md` | Orchestrator (per spawn) | The spawned subagent only |
| Compaction file | `SDD/orchestration/compacted/[phase]-compacted-[YYYY-MM-DD_HH-MM-SS].md` | Subagent on Safety-Net trip | Continuation subagent |
| Progress file | `SDD/orchestration/progress.md` | All subagents (append only) | All subagents, orchestrator |

```
SDD/
├── UBIQUITOUS_LANGUAGE.md
├── OBSERVABILITY.md                      # only after /observability-init — the flow reads it, and writes only its Eval command row
├── adr/{NNNN-slug.md, README.md}
├── flow/{DECOMPOSITION-[###]-[feature-name], TIERS-[feature-name]}.md
├── research/{CLARIFICATION-*, RESEARCH-*}.md
├── requirements/{DESIGN-[###]-[feature-name], SPEC-[###]-[feature-name]}.md
├── implementation/
│   ├── IMPLEMENTATION-PLAN-*.md
│   ├── slices/{SLICE-*, RETROSPECTIVE-SLICE-*, LEARNINGS-FEATURE-*}.md   # per-slice mode only
│   │   └── superseded/[YYYY-MM-DD_HH-MM-SS]/   # a replaced plan's slice retrospectives and reviews — kept, never read
│   └── summaries/IMPLEMENTATION-SUMMARY-*.md
├── orchestration/{progress.md, subagent-calls/, reviewer-calls/, counters/, compacted/}
└── reviews/{CRITICAL-RESEARCH-*, PANEL-FINDINGS-*, PANEL-SPEC-*, CRITICAL-SPEC-*,
            CRITICAL-IMPL-*, REVIEW-*, REVIEW-SLICE-*, FINAL-CHECK-*,
            TRACE-TREE-*, EVAL-RESULTS-*}.md
```

## Orchestrator Discipline (the load-bearing core)

**The orchestrator MUST NOT execute phase, review, fix, capture, or completion work directly.** Every numbered sub-step runs inside a spawned subagent — even ones that "look small." The orchestrator's only direct work: spawning subagents, running commits (per `commands/commit.md`), running the retro recommendation matcher, taking the fix-round snapshots (`scripts/snapshot.py`), running a review step's second-model reviewer (`scripts/second-model-review.py` — it starts the reviewer, as a spawn would; the review itself is the reviewer's), running the tier task mirror (`scripts/tier-mirror.py` — see Tier Task Mirror below), with the `evals` gate on making the eval run of record before a review (the application's own eval command, found in one row of `SDD/OBSERVABILITY.md`; the orchestrator reads the last line it prints and never the results — `phases/implementation-whole-feature.md` → *The eval run of record*), writing user-facing checkpoint messages, recording state in `progress.md`, and the few mechanical edits the phase files give it by name (a slice's row to `Complete` before its commit; after a re-plan, archiving the old slice table, moving the replaced plan's slice files aside, and stamping its slice IDs in the ledger). The orchestrator has no `/clear`; subagent boundaries are the only context reset.

- **Bounded returns.** Every subagent returns **≤200 words + artifact paths**. The orchestrator reads artifact files only when a decision genuinely needs them (e.g. spec frontmatter to route Step 4).
- **progress.md is append-only.** Never overwrite or delete prior content.
- **Explicit resolved paths in every spawn prompt** — never let a subagent guess artifact locations.
- **Per-phase sizing:** Research — single subagent (scope unknown until investigated); pre-split per-layer only if the task obviously cuts across >2 architectural layers. Planning — single subagent; pre-split only if RESEARCH >1000 lines or >3 disjoint subsystems. Implementation (whole-feature) — count SPEC items `REQ-XXX`+`EDGE-XXX`+`FAIL-XXX`; if >8, pre-split into ⌈total/5⌉ sequential chunks, each appending to IMPLEMENTATION-PLAN. **Per-slice mode: one subagent per slice, strict, no bundling** — REQ-count chunking does NOT apply.

### What a body may do (the prompt's paths are the only inputs)

The bodies were forked from commands a person runs by hand. Inside the flow every body is held to these rules, and an edit to a body is checked against them:

- **Inputs come from the prompt.** A body never lists a directory to find or choose its spec, research document, or plan — a repository holds several of each as soon as a second feature or tier exists, and only the orchestrator knows which is active.
- **A body never commits.** Every commit is the orchestrator's (2e, 3f, 4i, per-slice 4c.6). The implementation work stays uncommitted until then: a commit comes after the review of what it contains, never before, and a slice or feature is one commit. (The reviews measure the working tree against the recorded base commit, so an early commit would not hide changes from them — it would put unreviewed code into history and bypass the commit checkpoint.)
- **A body never resets, rewrites, or archives `progress.md`.** It appends. Rotation is the orchestrator's (Progress Hygiene below).
- **A body that cannot proceed returns a failure** — an input missing or unreadable, a precondition not met, a choice it has no authority to make — in its bounded return, and writes no stop note. The orchestrator handles it under Error Handling (`phases/protocols.md`).
- **A body writes only one stop note,** `## PARTIAL: needs continuation` — the compact bodies on a Safety-Net trip. Every `## Awaiting …` block is written by the orchestrator.

### Who declares a phase done (markers, stops, resume)

**Only the orchestrator declares a phase done, and only after the phase's last step.** A completion subagent's banner (`Planning Phase - COMPLETE`, `Implementation Phase - COMPLETE`) says that subagent's work is finished; the reviews, fixes, and commit that follow are still to come, and a resumed session that read the banner as "done" would skip them. Each phase therefore ends with a marker the orchestrator writes itself:

| Phase | Done when the orchestrator has written | Written at |
|---|---|---|
| Research | `## Research - Accepted` | after the 2e commit |
| Planning | `## Planning - Accepted` | 3g, after the deviation check |
| Implementation | `## Implementation - Committed`, then `## Feature - Done` | after the 4i commit; after the 4j announcement |

Three rules go with it, and an edit to a phase file is checked against them:

- **Resume reads the current feature only.** Step 0 opens each feature's record with `## Flow Started - [###]-[feature-name]`; Phase Detection reads only what follows the latest one, so an earlier feature's markers never answer for this one.
- **Every stop that waits for an answer has a halt block, a resume rule, and a diagram row.** The stop writes a block to `progress.md` before it asks; `phases/protocols.md` has the rule that resumes it; `docs/sdd-flow-diagram.md` lists it. A latest halt block always wins over a phase rule, and one with no rule of its own falls to the catch-all there: it is shown to the user verbatim, never guessed past. (Stops that need no answer — the slice pause, and terminal stops such as decomposition — write none; `phases/protocols.md` lists them.)
- **A handoff passes what a fresh spawn would.** A continuation or a re-review is given the same inputs — the step's own body and mode, paths, `SCOPE`, `ITER`, the base commit, a fix round's snapshots, allow-lists — as the first spawn of that step, stated explicitly, never left for the subagent to infer. A continuation is also the agent type that first spawn was, with its model override (`phases/protocols.md` → Mid-Phase Handoff).

The full marker table and the rules are in `phases/protocols.md` → Phase Detection Priority.

### Who owns the slice path (state changes, stops, commits)

**Every slice state change, stop, and commit has a named owner in the phase chapter.** The per-slice path has more hand-offs than any other — a slice's row moves through four states, and its cycle can end in a commit or a fix-loop stop — and a step that each side assumes the other performs is a step nobody performs. Two rules, and an edit to a slice body or to `phases/implementation-per-slice.md` is checked against them:

- **The owner table in `phases/implementation-per-slice.md` ("Who owns what on the slice path") is complete.** Every row of the slice table's status, every `## Slice SLICE-XXX - …` marker, every stop, and the commit appear there with one owner and one step. A new marker, state, or stop is added to that table in the same edit.
- **A body describes what it does — never what "the orchestrator may" do.** A body that needs something done outside its own run says what it leaves behind (a status, a marker, a file); the phase chapter says who acts on it and when.

A slice's cycle has exactly two kinds of end: its commit (4c.6, which also sets its row to `Complete`) or a halt block with a resume rule (`## Awaiting Slice Resolution`). A session that ends anywhere between is resumed from the slice markers (`phases/protocols.md` → per-slice cycle sub-steps).

### Tier Task Mirror (record-keeping, never silent)

The tier plan file is the record of a feature's tiers; BB tasks mirror it — one parent task for the feature, one sub-task per tier — so a waiting tier shows on the board and feedback can be left on it between cycles. The orchestrator keeps the two in step by running `python3 "$SKILL_ROOT/scripts/tier-mirror.py"` at the four points the phase files name: design-gate approval (`phases/planning.md` → 2.5b), before the final commit and at the completion announcement (`phases/implementation-whole-feature.md` → 4h–4j), and the start of a next-tier cycle (`phases/setup.md` → Step 0). It runs only for tiered features (approved tier `1`, `2`, or `3`). When no tracker project is linked to the BB project, the script **creates one** — a missing project is never a reason to skip.

The script's first stdout line is `Result: …`. After every run, append `## Task Mirror - <that line, verbatim>` to `progress.md`, then act on the exit status:

- **0** — done. If the line says a tracker project or tasks were created, tell the user in the next user-facing message, with the keys.
- **3 (`OFF`)** — there is no `bb` CLI, or the checkout is not inside a BB project, so there is nothing to mirror to. **Tell the user in the next user-facing message**, quoting the line. Do not run the mirror again in this cycle.
- **1 (`ERROR`)** — a `bb` command failed. Run it once more (it is safe to repeat: it creates only what is missing). If it fails again, **tell the user in the next user-facing message**, quoting the line, and carry on — the tier plan is unaffected, and the next mirror point tries again.
- **2** — the tier plan is missing or malformed: treat as a failed design-brief (or completion) step and re-spawn it.

The mirror never halts the flow and is never skipped without the user being told. The orchestrator never edits the tier plan itself; the script writes task keys into its `Task` column and copies task comments into its `## Feedback`, and nothing else.

### Second-Model Review (who runs a review)

**A review is run by a different model family than wrote what it reviews.** Everything a cycle produces is written by Claude subagents, and a Claude reviewer shares their blind spots, so each of these review steps — 2c, 3d, the 3e.5 check of the spec fix, 4b, the slice review, 4d, and the 4e.5 final check — is given to a second model through its command-line agent: the Codex CLI. `references/second-model-review.md` is the one definition: the list of review steps (and why the 3c specialist panel is not on it — it stays on Claude subagents, with 3d as the spec's second-model review), how the reviewer is settled at Step 0 and recorded as `Reviewer: …`, the preamble every second-model prompt starts with, the call to `scripts/second-model-review.py`, and what to do with each result. Read it at Step 0 and before the first review step; the phase chapters point to it and never restate it.

Three things hold whichever model reviews, and an edit to a review step is checked against them:

- **Same prompt, same outputs, same markers.** The second model is given exactly what the step's Claude spawn would be given, after a fixed preamble; it reads the same body by path, writes the same review document, and appends the same `progress.md` marker. Nothing downstream — fix subagents, caps, phase detection, resume — knows or asks which route ran.
- **The fallback is never silent and never halts.** No Codex CLI on the machine, or a run that fails twice, puts the review on the Claude subagent the phase chapter names; the line that says so goes to `progress.md` and to the user. Every review document carries a `Reviewed by:` line.
- **A review changes no code.** The script records the working tree before a second-model run and puts back any file outside `SDD/` the reviewer left changed.

### Progress Hygiene (rotation + bounded appends)

`progress.md` sits in the read path of nearly every spawn and of phase detection — its size is paid on every read. Three rules keep it bounded:

1. **Rotate at feature completion (Step 4j).** Move the finished feature's full history — its `## Flow Started - ` record and everything after it — to `SDD/orchestration/progress-archive/progress-SPEC-[###]-[YYYY-MM-DD_HH-MM-SS].md`; leave one line, `Finished: SPEC-[###] [feature-name] — <outcome>; history: <archive path>`. That line carries no `## ` header and no phase marker, so no resume rule can match a finished feature. The live file carries full history ONLY for the active feature.
2. **Checkpoint on size.** If the live file exceeds **~500 lines**, rotate at the next quiet point (a phase-boundary commit — 2e, 3f, 4i, per-slice 4c.6): archive resolved verbose blocks (including completed-phase history of the still-active feature), rewrite the head as a bounded `## Current State` (artifact pointers, archive path), then keep the active feature's `## Flow Started - ` record and, after it, its canonical phase-state lines verbatim and in order. **Pending halt blocks (`## Awaiting *`, `## PARTIAL*` — prefix match, not a fixed list) are carried forward verbatim as the latest blocks** — phase detection matches the latest block in the live file and never scans archives. Everything kept in the live file stays byte-identical; only the new head and rotation stamp are newly written text.
3. **Bounded appends.** Subagent progress entries are **≤10 lines**: status, artifact paths, one-line key decision, anything pending. Narrative belongs in the artifact the subagent wrote, referenced by path. (One exception: an `## ADR Candidates` entry lists every candidate, one line each, however many — it is the only record the design gate reads.)

Rotation is **orchestrator-only**, happens only between spawns (never mid-subagent), and is recorded in the fresh head. Append-only applies *within* a generation; rotation starts a new one. Full procedure: `phases/protocols.md` → Progress Rotation.

### Subagent Safety-Net Rule (embed verbatim in every phase-execution, fix, and continuation prompt)

A review run on the second model carries none of it — no rule, counter file, or compact path (`references/second-model-review.md` §3): the reviewer's CLI manages its own context.

> **Bail-out trigger (a trigger, not a budget to spend):** you have Read more than **15** files (implementation chunks: more than **20**).
>
> **When it fires, stop immediately.** Read the compact-body path given in your prompt (under "Compact instructions — use only if the Safety-Net trips") and follow it: write `SDD/orchestration/compacted/[phase]-compacted-[YYYY-MM-DD_HH-MM-SS].md`, append a `## PARTIAL: needs continuation` block to `progress.md` with the compaction file path and where you left off, and return ≤100 words stating a Mid-Phase Handoff is required.
>
> **Counter tracking.** You cannot inspect your own tool-call history. The orchestrator gives you a **dedicated counter file** (path in your prompt under "Your counter file"). It holds exactly one line: `Reads: 0/15`. Update it immediately after each Read; check it (cheap Read) before each new Read — that is the trigger evaluation. The counter file is scoped to your run only; never shared, never written to `progress.md`.

**Orchestrator obligation per spawn of a phase-execution / fix / continuation subagent:** (1) embed the Safety-Net Rule verbatim; (2) create the counter file at `SDD/orchestration/counters/[step-id]-[chunk-or-iter]-[YYYY-MM-DD_HH-MM-SS].md` with the single line `Reads: 0/15` (use `/20` for implementation chunks) and pass its path under "Your counter file"; (3) pass the matching compact body path (`SKILL_ROOT/bodies/[phase]-compact.md`) under "Compact instructions — use only if the Safety-Net trips". Counter is **Reads-only** — subagents are contractually barred from spawning (a platform limit on Claude Code ≤2.1.171, a deliberate design rule from 2.1.172 onward), so there is no nested-subagent count. Defaults (15 / 20) are tunable without changing the protocol.

### Spawn-prompt construction checklist

Every spawn prompt includes: (1) the **absolute body path** `SKILL_ROOT/bodies/<file>.md` with "Read this file FIRST — it is your complete instruction set"; (2) all resolved input + output artifact paths; (3) the task description + canonical identifiers; (4) "verify input files exist before starting; create parent dirs before writing; append (never overwrite) progress.md — entry ≤10 lines: status, artifact paths, one-line key decision, anything pending; narrative stays in your artifacts"; (5) for phase-execution/fix/continuation subagents — the Safety-Net Rule + counter-file path + compact body path; (6) the bounded-return contract (≤200 words + paths).

## Model Routing

Routing of every writing and fixing step is carried by **shipped agent frontmatter** — no runtime model switching. **This needs Claude Code's Agent tool (its built-in subagents).** Without it the agent types, and with them this table, do not apply. In bb, the Claude Code provider setting `subagentsDisabled` hides that tool; it must be `false` (`bb plugin config provider-claude-code set subagentsDisabled false`). The orchestrator MAY escalate a single spawn via the Agent tool's per-spawn model override. Review steps go to the cycle's second-model reviewer first (Second-Model Review above); the agent types this table gives for them are the **Claude route**, used when the cycle has no second model or a second-model run failed twice.

| Spawn site | Agent type | Model |
|---|---|---|
| Research, planning, ADR capture, fixes, impl chunks, completion, slice cycle (all but its review) | `agent-engineering:sdd-workhorse` | sonnet |
| Code review (4b), slice review, 4e.5 final check — **Claude route** | `agent-engineering:sdd-workhorse` | sonnet |
| Each panel specialist (Stage 1) with a shipped agent — `security`, `agent-security`, `performance`, `data-modeling`, `api-contract`, `module-depth`, `reliability`, `slice-integrity` | `agent-engineering:sdd-spec-<panel>-specialist` | sonnet |
| Any other panel value — today `accessibility`, `privacy`, `cost` | `agent-engineering:sdd-workhorse`, with `bodies/panel-specialist.md` and the panel value | sonnet |
| Panel synthesis (Stage 2) | `agent-engineering:sdd-critical-reviewer` | opus |
| Research/spec/impl critical review, and the 3e.5 check of the spec fix — **Claude route** | `agent-engineering:sdd-critical-reviewer` | opus |
| Design brief — first draft and every revision (2.5a, 2.5c) | `agent-engineering:sdd-workhorse` | **opus**, by per-spawn override — the one planning document a person reads |
| The successor of any step above after a Mid-Phase Handoff (`bodies/continue.md`) | the agent type that step's row gives, with that row's override | that step's model — a critical review, a panel synthesis, or a design brief is finished on Opus |

The workhorse's escalation protocol stays: if a task needs Opus depth, it surfaces "needed Opus depth" in its bounded return and the orchestrator re-spawns (or per-spawn-overrides) at Opus.

## State Machine

Evaluate top-to-bottom. At each step boundary, **read the named phase file before acting** — it holds the per-step spawn briefs, checkpoint templates, and halt semantics.

| Step | What | Read now |
|---|---|---|
| 0 | Scope assessment → resolve identifiers + SKILL_ROOT + the reviewer | `phases/setup.md` + `references/second-model-review.md` |
| 1.5 | Pre-research clarification gate (asks every time unless a CLARIFICATION file exists) | `phases/setup.md` |
| 2 | Research (2a–2e) | `phases/research.md` |
| 2.5 | Design gate — brief written, then a stop for approval (every time the brief is written or rewritten); the observability record is settled on approval | `phases/planning.md` |
| 3 | Planning (3a–3g; two-stage panel + bounded fix loop; 3g stops if the spec departs from the approved brief) | `phases/planning.md` |
| 4 | Implementation — route on spec `delivery_mode:` | read the matching file ↓ |
| 4 · whole-feature (default) | 4a–4j | `phases/implementation-whole-feature.md` |
| 4 · per-slice | per-slice cycle (a pause after every slice) + end-of-feature cycle | `phases/implementation-per-slice.md` |
| 4e.5 | Final check — security verification, last-look tests, trace and eval checks (both delivery modes) | the matching Step 4 file + `references/security-verification.md` |
| done | Commit (4h stops first only for a sign-off), then a short report | the matching Step 4 file |
| `continue` / resumption / handoffs / errors | Phase detection + protocols | `phases/protocols.md` |

## Arguments

| Argument | Description |
|---|---|
| `<task>` | The task, requirement, or feature description |
| `--tier N` | Have the design brief recommend Tier N (1, 2, or 3) instead of Tier 1. The tier can still be changed at the design gate |
| `--next-tier [feature-name]` | Start a new cycle for the next unshipped tier in `SDD/flow/TIERS-[feature-name].md` (`phases/setup.md` → Step 0) |
| `continue` | Resume from the last interruption point (see `phases/protocols.md`) |

The flow stops only where the user has something to decide or try: the clarification question, the design gate, a spec that departs from the brief, a pause after each slice, an unresolved finding, and a sign-off. Anything else is said in words at those stops — a re-plan is asked for at a slice pause.

**Removed flags (4.0.0) are ignored, never read as task text:** `--auto`, `--supervised`, `--skip-clarify`, `--skip-slice-checkpoints`, `--reviewer` (with its value), `--fall-back-to-whole-feature`, `--retry-slicing` (with its value), `--replan`, `--from-slice` (with its value), and `--override-replan`. Drop them from the input — on `continue` too — and say so in one line in the next user-facing message: `Ignored (removed in 4.0.0): <the flags>`.

## Key Principles

1. **Each phase is thorough** — research informs planning; planning constrains implementation.
2. **Every requirement gets a test — a real one (Principle 14).** Reviews are gates, not checkboxes: a review passes when no HIGH and no MEDIUM finding is open. LOW findings are listed, not fixed — the owner sees them at the slice pause and in the end report — because fixing them cost whole review rounds for little gain. A review after a fix round checks that the earlier review's findings are closed and reads what the fix changed, not the whole scope again: the orchestrator snapshots the working tree before and after each fix to tell it what that is, and the eval check still reads a fresh eval run in full. In a per-slice re-review the tests run are the ones the fix can affect, and the whole suite and the trace check run when the review would pass the slice — the trace check also after a tracing finding (`bodies/slice-review.md` → Step 4.5); the final check (4e.5) runs both in full. In a tiered spec, a finding that something is *absent* may be resolved by recording it under `## Deferred to Later Tiers`; a finding about behaviour the tier does build is always fixed.
3. **Panel STOP/REVISE halts the flow, but the fix loop is bounded** — max 3 iterations; any iteration that fails to strictly decrease the gating finding count halts. Unresolvable findings route back to the human.
4. **ADRs compound across features; the spec is the source of truth; document deviations.**
5. **Never persist PII or secrets in SDD docs. Commit messages have NO co-author attribution.**
6. **Explicit paths always; the orchestrator never does phase/review/fix/capture/completion work itself.**
7. **Per-slice cycle is strict** — one subagent per slice, mandatory per-slice review with every HIGH and MEDIUM finding resolved (LOW listed for the owner), retro + ledger before the atomic per-slice commit. Slice subagents receive ONLY the rolling ledger.
8. **A stop is for a decision, never for reading code.** The user approves a design and tries each slice; the reviews read the code. A slice retrospective's re-plan advice is shown at the slice pause, and the user asks for a re-plan in words.
9. **Security rules are checked by an adversarial reader, once, at the end.** The implementer proves each security rule's guard with a test that fails when the guard is removed. The final check (4e.5), on the second model, reads every security rule of the spec for a path on which it does not hold — respellings and aliases, error paths, unset settings, missing configuration, values echoed back — and each gap it finds is fixed with such a test; at most two fix rounds, then the owner decides. Every other rule is held by an ordinary real test (Principle 14). Every mutation is made in a scratch copy of the working tree, never in the repository. Standard: `references/security-verification.md`.
10. **The user approves a design, not a spec.** The design brief is the one planning document written for a person; nothing is specified until it is approved, with every question in it answered. The spec is held to it, and a spec that departs from it is shown to the user before any code is written.
11. **Tiers limit scope; nothing is built ahead.** Each tier is its own cycle with the same reviews and a real test for everything it does. A tier holds the simplest code and structure that serves that tier; a later tier reshaping it is expected. Standard: TIERS.
12. **The tier plan is the record; BB tasks mirror it.** The flow keeps them in step itself, creates the tracker project when there is none, and tells the user whenever the mirror could not run.
13. **In a traced application, what was planned to run is checked against what ran.** With the `tracing` gate on, the spec's planned call graph marks every entry point, model call, and external call; the implementer follows the tracing standard for what it adds, and each review compares the marked calls with the tree a real run recorded (`references/tracing-lens.md`) — the last time at the final check (4e.5), after every fix has landed. A difference is fixed in the code or the tests, or recorded as a deviation — the plan is never edited to match the run. An application without the tracing foundation is unaffected.

14. **A green run proves nothing until the tests are shown to be real.** Every implementer and fixer is held to one standard of what a real test is; the code review, each slice review, and the implementation critical review run the Test Integrity Lens against it — were existing tests weakened, is anything kept out of the run, do expected values come from the spec, does each test fail when the behaviour is broken, do stand-ins sit only at the application's edge, was the code fitted to the tests' inputs. The final check (4e.5) always runs and reads the tests once more, so no fix round goes unread. A HIGH lens finding rejects. Standard: `references/test-integrity.md`.
15. **The reviewer is not the author's model.** Research, spec, code, and tests are each reviewed on a second model family (the specialist panel alone stays on Claude); where none is available the review still runs, on a Claude subagent, and says so in its document, in `progress.md`, and to the user. Standard: `references/second-model-review.md`.
16. **What a model says is checked on what it really answered, and only a person accepts a judge's score.** With the `evals` gate on, the spec states the cases before any code exists; the implementer builds them and never writes them; and before each slice review, code review, and review of the final check (4e.5) — that last one after every fix has landed — the orchestrator puts every case to the running application, and the review reads that run. A hard case that fails is a failing test: it is fixed in the application, never by weakening the case, and one that cannot be made to pass reaches the user through the fix loop's stop. A judged score blocks nothing and meets nothing: a requirement only a judge can score is accepted by the user at the commit checkpoint (4h), the one reason that checkpoint stops. An application without the tracing foundation is unaffected. Standard: `references/evals.md`.

Session resumption, mid-phase handoff, phase-detection priority, and error handling all live in `phases/protocols.md`.
