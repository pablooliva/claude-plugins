---
name: sdd-flow
description: "INVOKE THIS SKILL when the user asks to run end-to-end feature development via the SDD methodology, or runs /sdd-flow with a task description. Takes a task or software requirement and drives it through the complete SDD lifecycle (Research → Planning → Implementation → Done) via subagents with fresh context per phase. Integrates the agent-engineering plugin's cross-cutting skills at phase boundaries: cross-cutting-adr during research and planning, spec-review-panel during planning, regression-eval-capture at implementation completion. Requires the SDD plugin to be installed; frontmatter fields (review_panel, eval_required, cross_cutting_decisions) gate the integrations."
---

# SDD Flow — End-to-End Feature Development

Takes a task or software requirement and drives it through the complete SDD (Specification-Driven Development) lifecycle: **Research → Planning → Implementation → Done**.

All phases run on **Claude Opus** by default. No model switching required. Phases are executed via subagents, giving each phase a fresh context window.

**Integrates agent-engineering skills at phase boundaries:**
- `cross-cutting-adr` — during research (ambient detection) and planning (spec frontmatter-driven).
- `/spec-review-panel` — during planning, after the spec is drafted. The default panel now includes `module-depth` (Ousterhout deep-module check on the spec's `## Modules` section, introduced in SDD 1.2.0).
- `/regression-eval-capture` — at implementation completion, gated by spec frontmatter.

**SDD 1.2.0 features picked up automatically:**
- **Pre-research clarification (`/research-clarify`)** — mandatory gate before Step 2 research, in **both supervised and autonomous modes**. Externalizes the user's design concept into a `CLARIFICATION-[###]` artifact that downstream phases read. The gate is satisfied by a pre-existing artifact, an interactive `/research-clarify` run, or an explicit `--skip-clarify` opt-out. Autonomous mode halts at this gate by default — it is the only mandatory autonomous-mode checkpoint in the flow. See "Step 1.5" below.
- **Ubiquitous language glossary** — `SDD/UBIQUITOUS_LANGUAGE.md` is incrementally maintained at `/sdd:research-complete` (Step 2a's second subagent) and `/sdd:planning-complete` (Step 3a's second subagent). Loaded by every phase-execution subagent for vocabulary alignment.
- **Modules section + module-depth specialist** — embedded in `/sdd:planning-start`'s spec template; checked by the `module-depth` panel specialist in Step 3c.
- **Risk-tiered code review** — embedded in `/sdd:code-review`; Step 4b applies depth proportional to each module's `Risk:` tier.

## Usage

```
/sdd-flow <task or requirement description>
```

You can also provide a ticket/issue number:

```
/sdd-flow #42 Add CSV export to the reports page
```

## How This Skill Works

This skill uses **subagents** to execute each phase of the SDD workflow. The main conversation acts as a lightweight orchestrator — it spawns subagents for research, planning, implementation, reviews, ADR capture, panel review, eval capture, and fixes. Each subagent gets a fresh context window, eliminating the need for manual session clears.

All inter-phase communication happens through the **SDD artifact files on disk** (see Artifact Paths Contract below). Every subagent is given explicit paths for reading inputs and writing outputs.

**The SDD plugin must be installed.** Subagents receive the equivalent instructions from the plugin's commands embedded directly in their prompts (since subagents cannot invoke slash commands).

**SDD plugin location:** `~/.claude/plugins/cache/pablooliva/sdd/` — read command files from the `commands/` subdirectory within the latest version (e.g., `~/.claude/plugins/cache/pablooliva/sdd/1.0.0/commands/`). Do NOT confuse this with other plugins (e.g., PACE) that have similarly named commands.

**Agent-engineering plugin location:** `~/.claude/plugins/cache/pablooliva/agent-engineering/` — contains the `spec-review-panel.md` command (actually located in the SDD plugin's `commands/` directory since it's an SDD-phase operation), the `regression-eval-capture.md` and `adr-capture.md` commands, and the `cross-cutting-adr` and `correction-codifier` skills.

## CRITICAL: Model Override

The SDD plugin commands contain model checks that require Opus for research and Sonnet for planning/implementation. **This skill overrides that behavior.**

When embedding SDD command instructions into subagent prompts, **strip all model verification steps.** Specifically:
- Remove any "This command requires Claude Sonnet/Opus" checks
- Remove any "STOP all further processing" instructions related to model verification
- Remove any warnings about switching models

All phases run on whatever model is currently active — **Opus is the intended default for all phases**.

---

## Artifact Paths Contract

Every subagent MUST use these exact paths. The orchestrator MUST include the resolved paths (with actual values for `[###]`, `[feature-name]`, dates, etc.) in every subagent prompt.

### Canonical Identifiers (resolved at Step 0)

| Identifier | Description | Example |
|------------|-------------|---------|
| `[###]` | Issue/ticket number or sequential ID | `042` |
| `[feature-name]` | Kebab-case feature name | `audit-logging` |
| `[YYYY-MM-DD]` | Current date | `2026-04-19` |
| `[YYYY-MM-DD_HH-MM-SS]` | Timestamp (24h, underscores) | `2026-04-19_14-30-45` |

### Phase Artifacts — Exact Paths

| Artifact | Path | Created By | Read By |
|----------|------|------------|---------|
| **Scope decomposition** | `SDD/flow/DECOMPOSITION-[###]-[feature-name].md` | Scope assessment subagent | User (manual `/sdd-flow` per item) |
| **Clarification document** (SDD 1.2.0, optional, supervised only) | `SDD/research/CLARIFICATION-[###]-[feature-name].md` | User (interactively, via `/research-clarify` outside this flow) | Research subagent, Research critical review |
| **Ubiquitous language glossary** (SDD 1.2.0, project-wide, single file) | `SDD/UBIQUITOUS_LANGUAGE.md` | Research-complete subagent (incremental updates), Planning-complete subagent (incremental updates) | All phase-execution subagents |
| **Research document** | `SDD/research/RESEARCH-[###]-[feature-name].md` | Research subagent | Research review, Planning subagent |
| **Research critical review** | `SDD/reviews/CRITICAL-RESEARCH-[feature-name]-[YYYYMMDD].md` | Research review subagent | Research fix subagent |
| **Specification** | `SDD/requirements/SPEC-[###]-[feature-name].md` | Planning subagent | Panel review, Planning review, Implementation subagent |
| **Spec panel review** | `SDD/reviews/PANEL-SPEC-[feature-name]-[YYYYMMDD].md` | Spec panel subagent | Planning fix subagent |
| **Spec critical review** | `SDD/reviews/CRITICAL-SPEC-[feature-name]-[YYYYMMDD].md` | Planning review subagent | Planning fix subagent |
| **ADRs** | `SDD/adr/NNNN-slug.md` | cross-cutting-adr skill (research or planning trigger) | Future sdd-flow runs, humans |
| **ADR index** | `SDD/adr/README.md` | cross-cutting-adr skill (auto-regenerated on write) | — |
| **Eval scaffolding** | `evals/datasets/[feature-slug].json`, `evals/evaluators/...`, `evals/run_functions/...`, `evals/README.md` | regression-eval-capture command | Future regression runs |
| **PROMPT tracking doc** | `SDD/prompts/PROMPT-[###]-[feature-name]-[YYYY-MM-DD].md` | Implementation subagent | Code review, Impl review, Completion subagent |
| **Code review** | `SDD/reviews/REVIEW-[###]-[feature-name]-[YYYYMMDD].md` | Code review subagent | Implementation fix subagent |
| **Impl critical review** | `SDD/reviews/CRITICAL-IMPL-[feature-name]-[YYYYMMDD].md` | Impl review subagent | Implementation fix subagent |
| **Implementation summary** | `SDD/prompts/implementation-complete/IMPLEMENTATION-SUMMARY-[###]-[YYYY-MM-DD_HH-MM-SS].md` | Completion subagent | — |
| **Progress file** | `SDD/prompts/context-management/progress.md` | All subagents (append only) | All subagents |

### Directory Structure

```
SDD/
├── UBIQUITOUS_LANGUAGE.md          # SDD 1.2.0 — project-wide glossary, single file
├── adr/
│   ├── NNNN-slug.md
│   └── README.md
├── flow/
│   └── DECOMPOSITION-[###]-[feature-name].md
├── research/
│   ├── CLARIFICATION-[###]-[feature-name].md   # SDD 1.2.0 — optional, supervised only
│   └── RESEARCH-[###]-[feature-name].md
├── requirements/
│   └── SPEC-[###]-[feature-name].md
├── prompts/
│   ├── PROMPT-[###]-[feature-name]-[YYYY-MM-DD].md
│   ├── implementation-complete/
│   │   └── IMPLEMENTATION-SUMMARY-[###]-[YYYY-MM-DD_HH-MM-SS].md
│   └── context-management/
│       ├── progress.md
│       ├── subagent-calls/
│       ├── counters/
│       │   └── [step-id]-[chunk-or-iter]-[YYYY-MM-DD_HH-MM-SS].md
│       ├── research-compacted-[YYYY-MM-DD_HH-MM-SS].md
│       ├── planning-compacted-[YYYY-MM-DD_HH-MM-SS].md
│       └── implementation-compacted-[YYYY-MM-DD_HH-MM-SS].md
└── reviews/
    ├── CRITICAL-RESEARCH-[feature-name]-[YYYYMMDD].md
    ├── PANEL-SPEC-[feature-name]-[YYYYMMDD].md
    ├── CRITICAL-SPEC-[feature-name]-[YYYYMMDD].md
    ├── CRITICAL-IMPL-[feature-name]-[YYYYMMDD].md
    └── REVIEW-[###]-[feature-name]-[YYYYMMDD].md

evals/                    # created only when eval_required: true
├── README.md
├── datasets/
│   └── [feature-slug].json
├── evaluators/
│   └── [feature-slug]_evaluator.{py,ts}
└── run_functions/
    └── [feature-slug]_run.{py,ts}
```

### Subagent Path Rules

Every subagent prompt MUST include:
1. The **resolved** paths for all artifacts it needs to read (inputs)
2. The **resolved** paths for all artifacts it must write (outputs)
3. An instruction to **verify input files exist** before starting work (read them; if missing, fail with a clear error message stating which file is missing and what path was expected)
4. An instruction to **create parent directories** before writing output files (`mkdir -p` as needed)
5. An instruction to **append** to `progress.md`, never overwrite or delete existing content

---

## Execution Modes

### Step 0: Scope Assessment

When invoked, first:

1. Extract the **task description** from the user's input
2. Extract **issue/ticket number** if provided (e.g., `#42`, `PROJ-123`), otherwise determine sequential numbering by checking existing SDD artifacts
3. Derive a **kebab-case feature name** from the task
4. Resolve all canonical identifiers (see Artifact Paths Contract)

Then spawn a **general-purpose subagent** for scope assessment:

- **Inputs:** Task description, codebase access
- **Outputs:** Either a decomposition document or a "proceed" signal
- **Task:** Analyze the requested feature and determine whether it can be completed in a single SDD cycle (research → planning → implementation) or whether it should be decomposed into smaller, independently deliverable chunks.

#### Assessment Heuristics

The subagent should consider:

- **Number of distinct components or systems touched** — A feature that modifies one module is different from one that cuts across the API layer, database schema, frontend, and background jobs.
- **Number of independent user-facing behaviors** — Multiple distinct behaviors (e.g., "add CSV export AND add scheduled reports AND add a dashboard widget") are likely separate features.
- **Natural seams** — Can the feature be split at boundaries where each piece delivers standalone value? If so, it probably should be.
- **Specification complexity** — Would the resulting SPEC document have so many requirements that a single implementation subagent couldn't hold them all in context?
- **Test surface** — Would the test suite for this feature require testing multiple unrelated subsystems?

This is a judgment call, not a formula. The subagent should explain its reasoning.

#### If the scope is manageable (single SDD cycle)

The subagent reports that the feature fits in one cycle. The orchestrator proceeds directly to **Step 1: Parse Input and Select Mode** with no pause — the user should not notice this gate for small requests.

#### If the scope is too large (decomposition needed)

The subagent produces a decomposition document at:

```
SDD/flow/DECOMPOSITION-[###]-[feature-name].md
```

This document contains:

1. **Rationale** — Why this feature request is too large for a single SDD cycle, referencing the heuristics above.
2. **Decomposition checklist** — An ordered list of smaller, independently deliverable features. Each item includes:
   - A clear, self-contained task description (suitable as input to `/sdd-flow`)
   - A brief note on what it delivers and why it's sequenced where it is
   - Any dependencies on prior checklist items
3. **Dependency map** — Which items must be completed before others (some may be parallelizable).

The orchestrator presents the decomposition to the user:

> **This feature request is too large for a single SDD cycle.**
>
> I've broken it into [N] independently deliverable steps:
>
> [Checklist summary]
>
> Full decomposition: `SDD/flow/DECOMPOSITION-[###]-[feature-name].md`
>
> Review and edit the decomposition as needed, then run `/sdd-flow` for each item when ready. Items marked with dependencies should be completed in order.

The skill then **stops**. The user manually invokes `/sdd-flow <checklist item description>` for each item at their own pace.

---

### Step 1: Parse Input and Select Mode

**Note:** This step is reached only after Step 0 determines the feature fits in a single SDD cycle.

**Ask the user which execution mode they want:**

> **Choose execution mode:**
>
> **Supervised** (default) — I'll run autonomously but pause for your approval at two checkpoints:
> 1. After research is complete (so you can confirm direction before planning/implementation)
> 2. Before committing implementation (so you can review the code)
>
> **Autonomous** — Fully autonomous, no checkpoints. I'll run research → planning → implementation → done without stopping. You'll see the final result when everything is complete.
>
> Reply **s** for supervised or **a** for autonomous. (Default: supervised)

If the user's original invocation already includes a mode flag (e.g., `/sdd-flow --auto <task>` or `/sdd-flow --supervised <task>`), skip the prompt and use that mode.

---

### Step 1.5: Pre-Research Clarification Gate

**This gate runs in both supervised and autonomous modes.** The design concept (Brooks) is the most valuable thing to externalize before any work begins, and the cost of skipping it propagates through every downstream phase. Autonomous mode therefore accepts exactly one mandatory checkpoint at this gate — and only this gate. After clarification, autonomous mode runs uninterrupted as before.

**Skip this gate if `SDD/research/CLARIFICATION-[###]-[feature-name].md` already exists** for this feature (the user already ran `/research-clarify` outside this flow, or pre-clarified before invoking `/sdd-flow`). Just proceed to Step 2; the research subagent will pick up the artifact automatically.

**Skip this gate if the user invoked `/sdd-flow` with `--skip-clarify`.** This is the explicit escape hatch — for users who have a crisp ticket with full acceptance criteria, or for very small well-understood changes, or who are deliberately accepting the design-concept risk. The Design Concept Fidelity block at Step 2c will record the gate-skip in the executive summary so the decision is visible downstream.

Otherwise, the gate fires:

#### Supervised mode

Ask the user:

> **Clarify the design concept first?**
>
> SDD 1.2.0 introduces `/research-clarify` — a structured interview that externalizes your design concept before any codebase research begins. **Strongly recommended** unless your task description is already crisp.
>
> Reply **y** to clarify first (recommended for brief or fuzzy task descriptions), **n** to proceed directly to research and accept the design-concept risk (suitable for crisp tickets with full acceptance criteria, or very small changes), or **s** to skip this gate now and on future invocations of this flow (equivalent to passing `--skip-clarify`).

- Reply **y**: orchestrator instructs the user to run `/research-clarify` interactively, writes a `## Awaiting Clarification` block to `progress.md`, and **stops**. Session Resumption picks up from Step 2 once the artifact exists.
- Reply **n**: proceed directly to Step 2. The orchestrator writes a `## Clarification Skipped (user opt-out)` block to `progress.md` so Step 2c's critical-review captures the gate-skip in the executive summary.
- Reply **s**: same as **n**, but also persists the opt-out for the rest of this flow (no further re-prompting on continuation).

#### Autonomous mode

Without an interactive interviewer, the orchestrator cannot grill. The gate halts by default:

1. Write a `## Awaiting Clarification` block to `progress.md` capturing the resolved identifiers (`[###]`, `[feature-name]`) and the chosen mode.
2. Emit this completion message and stop:

   > **Autonomous flow halted at the clarification gate (Step 1.5).**
   >
   > SDD 1.2.0 requires a clarified design concept before research, even in autonomous mode. You have two options:
   >
   > 1. **Clarify now (recommended):** Run `/research-clarify` interactively, complete the interview, then run `/sdd-flow continue`. The flow will resume autonomously from Step 2.
   > 2. **Skip the gate:** Re-invoke as `/sdd-flow --auto --skip-clarify <task>` if you have a crisp specification already and want to accept the design-concept risk.
   >
   > Resolved identifiers for this run: `[###]=<value>`, `[feature-name]=<value>`. Use these exact values when running `/research-clarify` so the artifact path aligns.

This is the only mandatory autonomous-mode checkpoint in the entire flow. All downstream phases continue without interruption once cleared.

#### Orchestrator-discipline note

The orchestrator does NOT spawn a subagent to "perform the clarification" itself. Grilling extracts the user's design concept from their head — a subagent reasoning about the task description is not the same artifact and would produce false fidelity. The gate is satisfied by a human-driven `/research-clarify` run, by a pre-existing CLARIFICATION artifact, or by an explicit `--skip-clarify` opt-out. Nothing else.

---

## Orchestration Instructions

The orchestrator (main conversation) spawns subagents sequentially. Each subagent receives:
- The full instructions from the corresponding SDD plugin command (with model checks stripped)
- Resolved artifact paths for its inputs and outputs
- The task description and canonical identifiers
- Any relevant context from previous subagent results

### Orchestrator Discipline

**The orchestrator MUST NOT execute phase, review, fix, capture, or completion work directly.** Every numbered sub-step in this skill — research, planning, implementation, ADR capture, panel review, critical review, fix iterations, code review, completion, eval scaffolding — runs inside a spawned subagent. The orchestrator's only direct work is: spawning subagents, running commits, writing user-facing checkpoint messages, and recording state in `progress.md`.

This rule applies even when a sub-step "looks small." A subagent that feels wasteful for a five-line task is far cheaper than the orchestrator absorbing the work, accumulating context, and losing the only available context-reset mechanism. The orchestrator has no `/clear` available to itself; subagent boundaries are the reset.

#### Bounded Subagent Returns

Every subagent's final return to the orchestrator MUST be bounded: **≤200 words of summary plus paths to artifacts written.** The orchestrator reads artifact files only when a decision genuinely requires their content (e.g., reading the spec's frontmatter to gate Step 3b) — not by default. This keeps the orchestrator's own context proportional to the *count* of phase boundaries crossed, not the volume of work done in each.

#### Per-Phase Sizing Strategy

Splitting heuristics differ by phase — a uniform "always pre-split" rule does not fit:

- **Research (Step 2a)** — Scope is unknown until investigation begins, so the orchestrator generally CANNOT pre-split usefully. Spawn a single research subagent and rely on the **Subagent Safety-Net Rule** (below) to trigger a mid-phase handoff if the investigation grows. Exception: if the task description obviously cuts across more than two architectural layers (e.g., "API + database + frontend + jobs"), the orchestrator MAY pre-split research into per-layer sub-investigations, with a final consolidation subagent stitching outputs into one RESEARCH document.

- **Planning (Step 3a)** — Usually a single subagent. Pre-split only if the RESEARCH document is exceptionally long (>1000 lines) OR covers more than three distinct subsystems with non-overlapping concerns. The safety-net rule still applies.

- **Implementation (Step 4a)** — Orchestrator-driven splitting is primary. Before spawning, the orchestrator counts SPEC items: `REQ-XXX` + `EDGE-XXX` + `FAIL-XXX`. If the total exceeds **8** (initial default — tune as needed), pre-split into ⌈total / 5⌉ sequential implementation subagents, each handling a contiguous chunk, each appending to the PROMPT document so the next subagent knows what's done.

#### Subagent Safety-Net Rule

Every phase-execution subagent (2a, 3a, 4a), every fix subagent (2d, 3e, 4c, 4e), and any continuation subagent spawned per the protocol below receives this rule embedded in its prompt. **Nested subagents (Explore or general-purpose subagents spawned from inside a parent subagent's execution) are intentionally out of scope** — they do not get their own counter file and instead are bounded by the parent's `Nested subagents: M/4` trigger; if a parent's nested-spawn count grows toward saturation, the parent itself must bail out.

> **Bail-out triggers (initial defaults — these are triggers, not budgets to spend):**
> - You have Read more than **10** files, OR
> - You have spawned more than **4** nested subagents.
>
> **When a trigger fires, stop immediately and follow the inlined compact-command instructions (already in your prompt — see below) to write `SDD/prompts/context-management/[phase]-compacted-[YYYY-MM-DD_HH-MM-SS].md`. Append a `## PARTIAL: needs continuation` block to `progress.md` with the compaction file path and where you left off. Return to the orchestrator with a brief note (≤100 words) stating that a Mid-Phase Handoff is required.**
>
> **Counter tracking.** You cannot inspect your own tool-call history reflexively, so the orchestrator gives you a **dedicated counter file** (path provided in your prompt under "Your counter file"). The file has exactly two lines:
> ```
> Reads: 0/10
> Nested subagents: 0/4
> ```
> Update the relevant line **immediately after** each Read or nested-subagent call. Check the file (cheap Read) before each new Read or nested-subagent spawn — that is the trigger evaluation. The counter file is **scoped to your subagent run only** — never shared with other subagents and never written to `progress.md`. Continuation subagents receive a fresh counter file at a new path, so `Reads: 0/10` always reflects *this run's* count.

**Orchestrator obligation: pre-embed the compact command AND assign a counter file.** The Safety-Net Rule depends on two things being in place when the subagent starts: the inlined compact-command instructions (so bail-out doesn't require reading a ~100-line file at the moment of context saturation), and a dedicated counter file path. When the orchestrator constructs any phase-execution, fix, or continuation subagent prompt, it MUST:
1. Inline the matching `/sdd:[phase]-compact` command body (model checks stripped) under a clearly delimited "Compact instructions (use only if the Safety-Net trips)" block.
2. Generate a unique counter file path under `SDD/prompts/context-management/counters/[step-id]-[chunk-or-iter]-[YYYY-MM-DD_HH-MM-SS].md` (e.g., `counters/4a-3-2026-04-26_15-12-08.md` for the 3rd chunk of an implementation split). Create the file with the two-line `Reads: 0/10\nNested subagents: 0/4` content. Pass the resolved path in the subagent's prompt under a "Your counter file" heading.

Counter files are per-run and never shared. They can be retained for post-mortem debugging or pruned periodically — they are not consumed by any later phase.

The numbers are initial defaults that can be tuned without changing the protocol. (See "Why count-based, not percentage-based" at the end of this section.)

#### Mid-Phase Handoff Protocol

When a subagent returns with a "needs continuation" signal:

1. The orchestrator reads only the latest compaction file path and the `## PARTIAL` block in `progress.md` — not the full work product.
2. It spawns a **fresh** subagent whose prompt embeds the SDD plugin's `/sdd:continue` command instructions (model checks stripped). The successor receives: the resolved compaction file path, all resolved phase artifact paths, the safety-net rule, and an explicit instruction to resume from the compaction file's "Current Focus" section.
3. The successor inherits the safety-net rule and may itself bail out if the work remains too large — the orchestrator can chain multiple handoffs within a single phase.

**Mid-Phase Handoff is distinct from Session Resumption** (the `/sdd-flow continue` user command — see "Session Resumption" below). Both reuse the same artifact formats (`progress.md`, `*-compacted-*.md`), but they trigger differently: Session Resumption fires when the user re-invokes `/sdd-flow continue` in a fresh session; Mid-Phase Handoff fires automatically inside an active flow when a subagent's safety-net trips.

#### Why count-based, not percentage-based

A spawned subagent has no first-class API to read its own context utilization — `/usage` is a harness slash command available only to the top-level interactive Claude, and the Anthropic API returns token counts to the harness, not to the model. Any "self-audit" the subagent performs itself produces output tokens that land back in its own context, partially eating the budget it's trying to measure. Count-based triggers (file Reads, nested subagent calls) are nearly free to evaluate (rule application, not deliberation), are inspectable in `progress.md`, and don't require the subagent to know anything its harness won't tell it.

---

### Step 2: Research Phase

#### 2a. Research Subagent

Spawn a **general-purpose subagent** with:
- **Instructions from:** `/sdd:research-start` command (embedded in prompt, model checks stripped)
- **Inputs:** Task description, codebase access, `SDD/research/CLARIFICATION-[###]-[feature-name].md` (if present — supervised users may have run `/research-clarify` first), `SDD/UBIQUITOUS_LANGUAGE.md` (if present — load before any research writing for vocabulary alignment)
- **Outputs:** `SDD/research/RESEARCH-[###]-[feature-name].md`, update `progress.md`
- **Task:** Create the research document and perform the full systematic investigation. If a CLARIFICATION artifact exists, treat its branches and open questions as required research targets — every branch must be addressed; every open question must be resolved or explicitly deferred with rationale.

Then spawn a second **general-purpose subagent** with:
- **Instructions from:** `/sdd:research-complete` command
- **Inputs:** The RESEARCH document at its exact path, `SDD/UBIQUITOUS_LANGUAGE.md` (if present, for incremental update)
- **Outputs:** Updated RESEARCH document (if gaps found), updated/created `SDD/UBIQUITOUS_LANGUAGE.md` (incremental, not regenerated — preserve stable terms), updated `progress.md`
- **Task:** Validate completeness against the checklist, fill any remaining gaps. Per `/sdd:research-complete` Step 3, propose and apply incremental updates to the ubiquitous language glossary based on terms introduced or refined during research.

#### 2b. ADR Capture from Research (NEW)

After research is complete, scan the research doc for cross-cutting architectural decisions captured as comparison-with-selection patterns — the places where the research compared alternatives and picked one.

Spawn a **general-purpose subagent** with:
- **Instructions from:** embed the `cross-cutting-adr` skill's behavioral instructions with **Trigger C (sdd-flow research hand-off)** active.
- **Inputs:** `SDD/research/RESEARCH-[###]-[feature-name].md`, existing `SDD/adr/` directory (if present)
- **Outputs:** Zero or more new ADR files at `SDD/adr/NNNN-slug.md`, updated `SDD/adr/README.md`, updated `progress.md`
- **Task:** Scan the research for cross-cutting decisions with explicit comparison+selection. For each match, apply the skill's scope test, render an ADR, and **confirm with the user** before writing (in supervised mode). In autonomous mode, accept all ADRs that pass the scope test.

If no cross-cutting decisions are detected, this step is a no-op — skip to 2c without writing anything.

#### 2c. Research Critical Review Subagent

Spawn a **general-purpose subagent** with:
- **Instructions from:** `/sdd:critical-review` command (research phase section)
- **Inputs:** `SDD/research/RESEARCH-[###]-[feature-name].md`, `SDD/research/CLARIFICATION-[###]-[feature-name].md` (if present, for the Design Concept Fidelity check), `SDD/UBIQUITOUS_LANGUAGE.md` (if present, for vocabulary-alignment check)
- **Outputs:** `SDD/reviews/CRITICAL-RESEARCH-[feature-name]-[YYYYMMDD].md`
- **Task:** Adversarial review of the research document. Per `/sdd:critical-review`'s Research Phase section, apply the Design Concept Fidelity block first — verify every branch from the CLARIFICATION artifact is addressed and every open question resolved or explicitly deferred. If no CLARIFICATION exists, record the gate-skip note in the review's executive summary as instructed.

#### 2d. Address Research Review Findings

Spawn a **general-purpose subagent** with:
- **Inputs:** `SDD/research/RESEARCH-[###]-[feature-name].md` AND `SDD/reviews/CRITICAL-RESEARCH-[feature-name]-[YYYYMMDD].md`
- **Outputs:** Updated `SDD/research/RESEARCH-[###]-[feature-name].md`, updated `progress.md`
- **Task:** Resolve ALL findings from the critical review — HIGH, MEDIUM, and LOW severity. Update the RESEARCH document to fill gaps, strengthen weak evidence, add missing perspectives, and address questionable assumptions. No finding is left unresolved. After fixing, append a "Findings Addressed" section to the review document noting how each finding was resolved.

#### 2e. Commit Research Artifacts

The **orchestrator** runs the commit (not a subagent), following `/sdd:commit` conventions — no co-author attribution. Include any ADRs written in Step 2b in this commit.

#### 2f. Supervised Checkpoint (if supervised mode)

If in **supervised mode**, pause and present a summary to the user:

> **Research phase complete.** Here's what was found:
> [Brief summary of key research findings and critical review results]
>
> Research document: `SDD/research/RESEARCH-[###]-[feature-name].md`
> Critical review: `SDD/reviews/CRITICAL-RESEARCH-[feature-name]-[YYYYMMDD].md`
> ADRs captured: [list of ADR numbers, or "none"]
>
> **Proceed to planning?** (y/n)

Wait for user confirmation before proceeding to Step 3.

If in **autonomous mode**, proceed directly to Step 3.

---

### Step 3: Planning Phase

#### 3a. Planning Subagent

Spawn a **general-purpose subagent** with:
- **Instructions from:** `/sdd:planning-start` command (model checks stripped)
- **Inputs:** `SDD/research/RESEARCH-[###]-[feature-name].md`, `SDD/prompts/context-management/progress.md`, existing `SDD/adr/` directory (to reference accepted ADRs), `SDD/UBIQUITOUS_LANGUAGE.md` (if present)
- **Outputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, updated `progress.md`
- **Task:** Read the research document and create the full specification. The spec MUST include the YAML frontmatter fields defined by `/sdd:planning-start` — `review_panel` (default includes `module-depth` as of SDD 1.2.0), `eval_required`, `cross_cutting_decisions` — populated thoughtfully based on feature characteristics. The spec MUST include the `## Modules` section (SDD 1.2.0) with at least one `MODULE-XXX` entry containing `Public Interface`, `Hides`, `Risk` (low/medium/high), and `Spec refs` fields — prefer deep modules over shallow per Ousterhout. Use canonical names from `SDD/UBIQUITOUS_LANGUAGE.md` when present.

Then spawn a second **general-purpose subagent** with:
- **Instructions from:** `/sdd:planning-complete` command
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, `SDD/UBIQUITOUS_LANGUAGE.md` (if present)
- **Outputs:** Updated SPEC document (if gaps found), updated `SDD/UBIQUITOUS_LANGUAGE.md` (incremental — only if the spec introduced new domain terms not already in the glossary), updated `progress.md`
- **Task:** Validate completeness against the checklist (which now includes the Modules section verification per SDD 1.2.0), ensure all research findings are incorporated, verify frontmatter fields are populated, capture any glossary deltas the spec introduced (per `/sdd:planning-complete` Step 5).

#### 3b. ADR Capture from Spec Frontmatter (NEW)

Read the spec's `cross_cutting_decisions:` frontmatter field. If the list is non-empty, for each topic label in the list, spawn a **general-purpose subagent**:

- **Instructions from:** embed the `cross-cutting-adr` skill's behavioral instructions with **Trigger C (sdd-flow planning hand-off, frontmatter-declared)** active — frontmatter-declared decisions are pre-approved, so no user confirmation required.
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, existing `SDD/adr/` directory
- **Outputs:** New ADR file at `SDD/adr/NNNN-slug.md`, updated `SDD/adr/README.md`, updated `progress.md`
- **Task:** Extract details for the given topic label from the spec and research documents (decision, alternatives, rationale, consequences). If the available context is insufficient, the subagent should emit a warning and skip that topic rather than fabricating rationale. Apply the skill's scope test, then write the ADR.

If `cross_cutting_decisions:` is empty or absent, skip this step entirely.

#### 3c. Specialist Panel Review (NEW)

Spawn a **general-purpose subagent** with:
- **Instructions from:** `/sdd:spec-review-panel` command
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`. Panel composition comes from the spec's `review_panel:` frontmatter (defaults applied if absent).
- **Outputs:** `SDD/reviews/PANEL-SPEC-[feature-name]-[YYYYMMDD].md`
- **Task:** Convene the specialist panel. The panel-review subagent itself spawns nested subagents for each specialist (per the command's Section 3), collects findings, applies severity aggregation, and emits a verdict.

**Act on the verdict:**

- **`PROCEED`** — continue to 3d.
- **`STOP AND RECONSIDER`** (any HIGH finding) or **`REVISE BEFORE PROCEEDING`** (3+ MEDIUM or cross-domain MEDIUM) — enter the **fix-and-re-review loop**, bounded by the cap below. Apply in both supervised and autonomous modes; the cap protects against unbounded iteration in either.

**Fix-and-re-review loop (bounded — max 3 iterations):**

Each iteration:

1. **Record iteration state in `progress.md`** under a `## Panel Review Iterations` subsection. Capture: iteration number, HIGH count, MEDIUM count, LOW count, verdict, timestamp.
2. **Spawn a fix subagent** with:
   - **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/reviews/PANEL-SPEC-[feature-name]-[YYYYMMDD].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`
   - **Outputs:** Updated spec (in place), "Findings Addressed" section appended to the panel review
   - **Task:** Resolve every HIGH and MEDIUM finding from the panel review. Each resolution must cite the specific spec change made. Do NOT claim resolution without an actual spec edit.
3. **Re-run Step 3c** — spawn a fresh panel review subagent with the updated spec. This produces a new or overwritten `PANEL-SPEC-*` review document.
4. **Compare this iteration's finding counts to the previous iteration:**
   - **Progress stall check:** if HIGH count did not strictly decrease (when HIGH was non-zero) OR (in REVISE case) if MEDIUM count did not strictly decrease → halt immediately. The fix subagent is not making real progress; further iterations are waste or degrade review quality.
   - **If panel now returns `PROCEED`** → exit the loop; continue to 3d.
   - **If still STOP/REVISE and iteration count < 3** → start the next iteration.
5. **After iteration 3, regardless of verdict** → halt the flow (cap exhausted).

**On halt (either cap exhausted or progress stall):**

- Leave all artifacts in place — do not delete the spec, do not delete any panel review document.
- Append a final `### Panel Review Halt` entry to `progress.md` with: total iteration count, final HIGH/MEDIUM/LOW counts, halt reason (`cap-exhausted` | `progress-stall`), and an explicit next-action hint for the user.
- Do NOT proceed to 3d, 3e, 3f, or beyond. The spec has not been accepted.
- Emit this completion message (identical in supervised and autonomous modes):

> **Flow halted at panel review.** Spec did not pass specialist review after [N] iteration(s). Halt reason: [cap-exhausted | progress-stall].
>
> Final verdict: [STOP AND RECONSIDER | REVISE BEFORE PROCEEDING]
> Unresolved HIGH findings: [count]
> Unresolved MEDIUM findings: [count]
> Latest panel review: `SDD/reviews/PANEL-SPEC-[feature-name]-[YYYYMMDD].md`
> Iteration history: `SDD/prompts/context-management/progress.md` → "Panel Review Iterations"
>
> The fix subagent could not resolve findings autonomously. Review the panel findings, address them manually in the spec (the remaining HIGH/MEDIUM issues likely require design judgment the subagent cannot make), then run `/sdd-flow continue` to resume.

**Why the cap and progress check exist:** unbounded loops in autonomous mode risk three failure modes — (1) infinite iteration burning tokens, (2) cost explosion from 4+ specialist subagents × N iterations per spec, and (3) degraded review quality where the panel starts approving superficial edits that don't resolve the underlying findings. The progress-stall check catches (3) specifically — if a fix iteration doesn't actually reduce findings, we're seeing placating edits rather than real resolution. In both failure modes, routing the problem back to a human is the correct action.

#### 3d. Spec Critical Review Subagent

Spawn a **general-purpose subagent** with:
- **Instructions from:** `/sdd:critical-review` command (planning phase section)
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, `SDD/reviews/PANEL-SPEC-[feature-name]-[YYYYMMDD].md`
- **Outputs:** `SDD/reviews/CRITICAL-SPEC-[feature-name]-[YYYYMMDD].md`
- **Task:** Adversarial review of the specification, checking for ambiguities, untestable criteria, dropped research findings, contradictions. Complementary to the panel review — critical-review is generalist and adversarial; the panel was domain-specialist.

#### 3e. Address Spec Review Findings (panel + critical, combined)

Spawn a **general-purpose subagent** with:
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/reviews/PANEL-SPEC-[feature-name]-[YYYYMMDD].md`, `SDD/reviews/CRITICAL-SPEC-[feature-name]-[YYYYMMDD].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`
- **Outputs:** Updated `SDD/requirements/SPEC-[###]-[feature-name].md`, updated `progress.md`
- **Task:** Resolve ALL findings from BOTH reviews — panel findings (domain-specific anti-patterns) AND critical-review findings (ambiguity, testability, contradictions). Clarify ambiguous requirements, make criteria testable, add missing edge cases, resolve contradictions, address panel anti-patterns, incorporate dropped research findings. Append "Findings Addressed" sections to both review documents.

#### 3f. Commit Planning Artifacts

The **orchestrator** runs the commit. Include any ADRs written in Step 3b.

#### 3g. Transition

Proceed directly to Step 4 (no checkpoint needed here — the supervised checkpoint covers the most critical decision point at research, and the second checkpoint comes before final implementation commit).

---

### Step 4: Implementation Phase

#### 4a. Implementation Subagent

Spawn a **general-purpose subagent** with:
- **Instructions from:** `/sdd:implementation-start` command (model checks stripped)
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, `SDD/prompts/context-management/progress.md`, `SDD/UBIQUITOUS_LANGUAGE.md` (if present — use canonical names in code, comments, commits, tests)
- **Outputs:** `SDD/prompts/PROMPT-[###]-[feature-name]-[YYYY-MM-DD].md`, implemented code and tests, updated `progress.md`
- **Task:** Read the specification and implement ALL requirements:
  - Core functionality (happy path)
  - Edge cases (EDGE-XXX from spec)
  - Failure handling (FAIL-XXX from spec)
  - Tests alongside each component
  - Performance and security validation
  - Update PROMPT tracking document throughout

**Sizing:** Apply the orchestrator-driven splitting heuristic from "Orchestrator Discipline → Per-Phase Sizing Strategy → Implementation". Pre-split before spawning if the SPEC item count exceeds the threshold; each subagent appends to the PROMPT document so the next knows what's done. The Subagent Safety-Net Rule still applies as a backstop if a chunk turns out to be larger than estimated.

#### 4b. Code Review Subagent

Spawn a **general-purpose subagent** with:
- **Instructions from:** `/sdd:code-review` command
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/research/RESEARCH-[###]-[feature-name].md`, `SDD/prompts/PROMPT-[###]-[feature-name]-[YYYY-MM-DD].md`, the implemented code files (paths from PROMPT document)
- **Outputs:** `SDD/reviews/REVIEW-[###]-[feature-name]-[YYYYMMDD].md`
- **Task:** Specification-driven code review (70% spec alignment, 20% context engineering, 10% test alignment). Apply **Risk-Tiered Review Depth** (SDD 1.2.0) — read the `Risk:` field on each `MODULE-XXX` entry in the spec and scale internal-review depth accordingly: `high` → full review of internals; `medium` → default depth; `low` → tested-boundary review only. Escalate any tier that appears misclassified (e.g., a `low`-tagged module touching irreversible state) and flag the misclassification in the review summary's Module Review Log.

#### 4c. Address Code Review Findings

Spawn a **general-purpose subagent** with:
- **Inputs:** `SDD/reviews/REVIEW-[###]-[feature-name]-[YYYYMMDD].md`, `SDD/requirements/SPEC-[###]-[feature-name].md`, the implemented code files
- **Outputs:** Updated code and tests, updated PROMPT document, "Findings Addressed" appended to review document
- **Task:** Fix ALL findings until the implementation meets APPROVED status. Resolve specification misalignment, missing edge/failure handling, test gaps, and all other issues.

#### 4d. Implementation Critical Review Subagent

Spawn a **general-purpose subagent** with:
- **Instructions from:** `/sdd:critical-review` command (implementation phase section)
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, implemented code files, test files
- **Outputs:** `SDD/reviews/CRITICAL-IMPL-[feature-name]-[YYYYMMDD].md`
- **Task:** Adversarial review of the implementation

#### 4e. Address Implementation Review Findings

Spawn a **general-purpose subagent** with:
- **Inputs:** `SDD/reviews/CRITICAL-IMPL-[feature-name]-[YYYYMMDD].md`, `SDD/requirements/SPEC-[###]-[feature-name].md`, implemented code files
- **Outputs:** Updated code and tests, updated PROMPT document, "Findings Addressed" appended to review document
- **Task:** Resolve ALL findings — fix specification deviations, security vulnerabilities, silent failures, missing test coverage, and every other issue regardless of severity.

#### 4f. Implementation Completion Subagent

Spawn a **general-purpose subagent** with:
- **Instructions from:** `/sdd:implementation-complete` command (model checks stripped)
- **Inputs:** `SDD/prompts/PROMPT-[###]-[feature-name]-[YYYY-MM-DD].md`, `SDD/requirements/SPEC-[###]-[feature-name].md`
- **Outputs:** Updated PROMPT document, updated SPEC document, `SDD/prompts/implementation-complete/IMPLEMENTATION-SUMMARY-[###]-[YYYY-MM-DD_HH-MM-SS].md`, updated `progress.md`
- **Task:** Finalize all documentation, validate all requirements are met, create implementation summary

#### 4g. Regression Eval Capture (NEW, conditional)

Read the spec's `eval_required:` frontmatter field. If `true`, spawn a **general-purpose subagent**:

- **Instructions from:** `/agent-engineering:regression-eval-capture` command
- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md` (for feature name, success criteria, frontmatter metadata), repo's existing `evals/` directory if present
- **Outputs:** LangSmith dataset created (empty, awaiting examples), `evals/evaluators/[feature-slug]_evaluator.{py,ts}`, `evals/run_functions/[feature-slug]_run.{py,ts}`, `evals/README.md` updated
- **Task:** Scaffold the regression eval infrastructure per the command's instructions.

**Non-blocking behavior:** if the command's prerequisite check fails (no `langsmith` CLI, no API key, etc.), the subagent logs a warning to `progress.md` but does NOT halt the flow. The feature has shipped; the eval is a follow-up concern. sdd-flow should surface the warning to the user in the completion announcement.

If `eval_required:` is `false` or absent, skip this step entirely.

#### 4h. Supervised Checkpoint (if supervised mode)

If in **supervised mode**, pause and present a summary to the user:

> **Implementation complete.** Here's a summary:
> [Brief summary of what was built, test results, review outcomes]
>
> Key artifacts:
> - Spec: `SDD/requirements/SPEC-[###]-[feature-name].md`
> - Code review: `SDD/reviews/REVIEW-[###]-[feature-name]-[YYYYMMDD].md`
> - Critical review: `SDD/reviews/CRITICAL-IMPL-[feature-name]-[YYYYMMDD].md`
> - Implementation summary: `SDD/prompts/implementation-complete/IMPLEMENTATION-SUMMARY-[###]-[timestamp].md`
> - [Eval scaffolding: evals/... (if eval_required was true and scaffold succeeded)]
> - [Eval scaffold warnings: progress.md (if scaffold failed)]
>
> **Ready to commit all implementation code?** (y/n)

Wait for user confirmation before committing.

If in **autonomous mode**, proceed directly to commit.

#### 4i. Commit Implementation

The **orchestrator** runs the commit — all implementation code, tests, reviews, SDD artifacts, and any eval scaffolding written in 4g. No co-author attribution.

#### 4j. Completion Announcement

> Implementation complete! All requirements from SPEC-[###] have been implemented, reviewed, and tested.
> All artifacts committed. Feature is ready for deployment.
> [If eval_required was true and scaffold succeeded:]
> Regression eval dataset `regression-[feature-slug]` created on LangSmith (empty). Populate with golden examples after ≥1 week of runtime. See `evals/README.md`.
> [If eval_required was true but scaffold failed:]
> ⚠️ Eval scaffolding failed — see progress.md for details. Run `/regression-eval-capture` manually once LangSmith is configured.
> [If ADRs were captured:]
> ADRs written: [list]. See `SDD/adr/README.md`.

---

## Session Resumption

This is the user-triggered resume path: the user re-invokes `/sdd-flow continue` in a fresh Claude Code session, and the orchestrator resumes from the most recent state recorded in `progress.md`. It is **distinct from the Mid-Phase Handoff Protocol** in "Orchestrator Discipline" — that one fires automatically inside an active flow when a subagent's safety-net trips. Both reuse the same artifact format (`progress.md`, `*-compacted-*.md`); they differ only in trigger.

When the user runs `/sdd-flow continue`:

1. Read `SDD/prompts/context-management/progress.md`
2. Determine which phase and sub-step is active
3. Resume from the exact sub-step where work was interrupted by spawning the appropriate subagent
4. If a phase was marked complete in progress.md, advance to the next phase

### Phase Detection Priority

- If "Implementation Phase - COMPLETE" → Done, show final summary
- If implementation is active → Resume the appropriate sub-step (4a-4j)
- If "Planning Phase - COMPLETE" → Start Step 4 (implementation)
- If planning is active → Resume the appropriate sub-step (3a-3g)
- If "Research Phase - COMPLETE" → Start Step 3 (planning)
- If research is active → Resume the appropriate sub-step (2a-2f)
- If `## Awaiting Clarification` is the latest block in `progress.md` AND `SDD/research/CLARIFICATION-[###]-[feature-name].md` now exists → resume at Step 2 (the clarification gate is satisfied; research subagent will pick up the artifact). If the artifact still doesn't exist, re-prompt the user to run `/research-clarify` or skip.
- If no phase info → Start from Step 0 (scope assessment)

## Subagent Guidelines

### Prompt Construction

When spawning each subagent, the orchestrator must include in the prompt:
1. The full SDD command or agent-engineering command instructions for that step (model checks stripped)
2. All resolved artifact paths (inputs and outputs)
3. The task description and canonical identifiers
4. The project's CLAUDE.md instructions (if relevant to the phase)
5. An explicit instruction to read input files before starting work
6. An explicit instruction to create directories before writing output files
7. **For phase-execution (2a, 3a, 4a), fix (2d, 3e, 4c, 4e), and continuation subagents:** the Subagent Safety-Net Rule (verbatim from "Orchestrator Discipline → Subagent Safety-Net Rule"), the inlined body of the matching `/sdd:[phase]-compact` command (model checks stripped) under a "Compact instructions (use only if the Safety-Net trips)" delimiter, AND a unique counter file path under "Your counter file" (the orchestrator must create the file at `SDD/prompts/context-management/counters/[step-id]-[chunk-or-iter]-[YYYY-MM-DD_HH-MM-SS].md` with two lines `Reads: 0/10\nNested subagents: 0/4` before spawning the subagent). All three must be embedded up front so the subagent can use them without reading additional files at bail-out time.
8. The bounded-return contract: ≤200 words of summary plus paths to artifacts written.

### Context Management Within Subagents

- Each subagent gets a fresh context window — no carryover from previous phases.
- Sizing and bail-out are governed by **Orchestrator Discipline** (above): per-phase pre-splitting heuristics and the count-based Subagent Safety-Net Rule. Do not invent new context-management policy here.
- Subagents should use Explore subagents (nested) for file discovery to preserve their own context.
- Subagents should use general-purpose subagents (nested) for complex analysis tasks.
- Each nested subagent counts toward the parent subagent's safety-net threshold.

### Error Handling

- If a subagent fails or returns incomplete results, the orchestrator should:
  1. Log the failure in `progress.md`
  2. Attempt to re-spawn the subagent with additional context about what went wrong
  3. If the same subagent fails twice, stop and inform the user

## Key Principles

1. **Each phase must be thorough** — don't rush through research to get to implementation
2. **Research informs planning, planning constrains implementation** — maintain this chain
3. **Every requirement gets a test** — no exceptions
4. **Reviews are mandatory, not optional** — critical review happens after every phase, code review happens during implementation, specialist panel review happens on every spec
5. **ALL review findings must be resolved before proceeding** — every issue (HIGH, MEDIUM, LOW) gets fixed, not just noted. Reviews are gates, not checkboxes
6. **Panel STOP/REVISE verdicts halt the flow, but the fix loop is bounded** — max 3 fix-and-re-review iterations in either mode. Any iteration that fails to strictly decrease the HIGH (or in REVISE case, MEDIUM) finding count halts immediately. Unresolvable findings route back to the human — the flow does not silently accept placating edits.
7. **ADRs compound across features** — capture cross-cutting decisions once; future features inherit them.
8. **Evals scaffold, humans populate** — `eval_required: true` creates infrastructure, not golden examples. Real examples come from production runtime.
9. **Document deviations** — if implementation diverges from spec, document why
10. **The spec is the source of truth** — implementation decisions trace back to spec requirements
11. **Never persist PII or secrets** in SDD documents
12. **Commit messages have NO co-author attribution** — per project convention
13. **Explicit paths always** — every subagent gets resolved, concrete file paths. Never rely on a subagent to guess or discover artifact locations.
14. **The orchestrator never executes phase, review, fix, capture, or completion work directly** — every numbered sub-step runs in a spawned subagent, even ones that "look small." The orchestrator has no `/clear` available to itself; subagent boundaries are the only context-reset mechanism. See "Orchestrator Discipline" for the full rule, the bounded-return contract, per-phase sizing heuristics, the Subagent Safety-Net Rule, and the Mid-Phase Handoff Protocol.

## Arguments

| Argument | Description |
|----------|-------------|
| `<task>` | The task, requirement, or feature description to develop |
| `--auto` | Run in fully autonomous mode (no checkpoints — except the mandatory pre-research clarification gate at Step 1.5; see `--skip-clarify` to suppress that too) |
| `--supervised` | Run in supervised mode with checkpoints (default) |
| `--skip-clarify` | Suppress the pre-research clarification gate (Step 1.5). Use when you have a crisp specification already and accept the design-concept risk. The gate-skip is recorded in the Step 2c critical review's executive summary for downstream visibility. |
| `continue` | Resume from the last interruption point |

## Examples

```
/sdd-flow Add GDPR-compliant audit logging for all anonymization requests
/sdd-flow --auto #15 Implement allow-list management UI with CRUD operations
/sdd-flow continue
```
