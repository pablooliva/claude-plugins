# Phase: Setup — Step 0 (Scope) · Step 1 (Mode) · Step 1.5 (Clarification Gate)

Read this at the very start of every fresh `/sdd-flow <task>` invocation (not `continue` — that routes through `protocols.md`). All spawns follow the SKILL's spawn-prompt construction checklist and Safety-Net obligations.

---

## Step 0: Scope Assessment

When invoked, the orchestrator first:

1. Extracts the **task description** from the user's input.
2. Extracts an **issue/ticket number** if provided (`#42`, `PROJ-123`); otherwise determines sequential numbering by checking existing `SDD/` artifacts.
3. Derives a **kebab-case `[feature-name]`** from the task.
4. Resolves all canonical identifiers (SKILL → Canonical Identifiers).
5. **Resolves SKILL_ROOT** (SKILL → SKILL_ROOT resolution) and records it, with the resolved identifiers, in `SDD/orchestration/progress.md` (create the file + parent dirs if absent). Resumed sessions re-derive every body path from this record.

Then spawn ONE **`agent-engineering:sdd-workhorse`** subagent for scope assessment. There is no dedicated body file — embed this brief directly in the prompt:

- **Inputs:** task description, codebase access.
- **Outputs:** either a decomposition document or a "proceed" signal (bounded return).
- **Task:** Determine whether the feature fits a single SDD cycle (research → planning → implementation) or should be decomposed. Judgment call, not a formula — the subagent explains its reasoning against these heuristics: number of distinct components/systems touched; number of independent user-facing behaviors; natural seams where each piece delivers standalone value; specification complexity (would the SPEC hold too many requirements for one implementation subagent?); test surface (would tests span unrelated subsystems?).
- This subagent does file discovery **inline** (Grep/Glob/Read). It carries the Safety-Net Rule, a counter file, and the `research-compact.md` compact body path (scope work is research-shaped).

### If the scope is manageable (single SDD cycle)

The subagent returns a "proceed" signal. The orchestrator proceeds directly to **Step 1** with no pause — the user should not notice this gate for small requests.

### If the scope is too large (decomposition needed)

The subagent writes `SDD/flow/DECOMPOSITION-[###]-[feature-name].md` containing: (1) **Rationale** referencing the heuristics; (2) a **decomposition checklist** of smaller, independently deliverable features, each a self-contained task description suitable as `/sdd-flow` input, with a note on what it delivers and why it is sequenced there, plus any dependencies; (3) a **dependency map**.

The orchestrator presents the decomposition to the user:

> **This feature request is too large for a single SDD cycle.**
> I've broken it into [N] independently deliverable steps:
> [Checklist summary]
> Full decomposition: `SDD/flow/DECOMPOSITION-[###]-[feature-name].md`
> Review and edit it as needed, then run `/sdd-flow` for each item when ready. Items with dependencies should be completed in order.

Then **STOP**. The user manually invokes `/sdd-flow <checklist item>` for each item at their own pace. (This decomposition stop is unconditional — the orchestrator does not auto-start the first item.)

---

## Step 1: Parse Input and Select Mode

Reached only after Step 0 says the feature fits one cycle. If the invocation already carried `--auto` or `--supervised`, use it and skip the prompt. Otherwise ask:

> **Choose execution mode:**
> **Supervised** (default) — runs autonomously but pauses at two checkpoints: after research completes, and before committing implementation.
> **Autonomous** — no checkpoints; runs research → planning → implementation → done, surfacing the final result only.
> Reply **s** for supervised or **a** for autonomous. (Default: supervised)

Record the chosen mode in `progress.md`.

---

## Step 1.5: Pre-Research Clarification Gate

**Fires in BOTH supervised and autonomous modes.** Externalizing the design concept (Brooks) before any work begins is the highest-leverage artifact, and the cost of skipping propagates through every downstream phase. This is the **only** mandatory autonomous-mode checkpoint.

**Skip the gate if** `SDD/research/CLARIFICATION-[###]-[feature-name].md` already exists (user pre-clarified) — proceed to Step 2; the research subagent picks it up automatically.

**Skip the gate if** the user passed `--skip-clarify`. The Step 2c critical review records the gate-skip in its executive summary. (Reply **s** below persists this opt-out for the rest of the flow.)

Otherwise the gate fires:

### Supervised mode

Ask:

> **Clarify the design concept first?**
> `/research-clarify` is a structured interview that externalizes your design concept before any codebase research. **Strongly recommended** unless your task description is already crisp.
> Reply **y** to clarify first, **n** to proceed directly and accept the design-concept risk (crisp tickets / very small changes), or **s** to skip this gate now and on future invocations (equivalent to `--skip-clarify`).

- **y** → instruct the user to run `/research-clarify` interactively; write an `## Awaiting Clarification` block to `progress.md`; **STOP**. Session Resumption picks up at Step 2 once the artifact exists.
- **n** → proceed to Step 2; write a `## Clarification Skipped (user opt-out)` block to `progress.md` so Step 2c captures the gate-skip.
- **s** → same as **n**, but persists the opt-out for the rest of this flow (no further re-prompting on continuation).

### Autonomous mode

Without an interactive interviewer the orchestrator cannot grill. The gate halts by default:

1. Write an `## Awaiting Clarification` block to `progress.md` capturing the resolved identifiers and chosen mode.
2. Emit and STOP:

> **Autonomous flow halted at the clarification gate (Step 1.5).**
> A clarified design concept is required before research, even in autonomous mode. Two options:
> 1. **Clarify now (recommended):** run `/research-clarify` interactively, then `/sdd-flow continue` — the flow resumes autonomously from Step 2.
> 2. **Skip the gate:** re-invoke as `/sdd-flow --auto --skip-clarify <task>` if you have a crisp spec and accept the design-concept risk.
> Resolved identifiers: `[###]=<value>`, `[feature-name]=<value>`. Use these exact values when running `/research-clarify` so the artifact path aligns.

### Orchestrator-discipline note

The orchestrator does NOT spawn a subagent to "perform the clarification." Grilling extracts the user's design concept from their head; a subagent reasoning about the task description is a different artifact and produces false fidelity. The gate is satisfied only by a human-driven `/research-clarify` run, a pre-existing CLARIFICATION artifact, or an explicit `--skip-clarify` opt-out.

Once the gate is cleared, proceed to **Step 2** → read `phases/research.md`.
