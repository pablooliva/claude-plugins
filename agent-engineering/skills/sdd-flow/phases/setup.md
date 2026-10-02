# Phase: Setup — Step 0 (Scope) · Step 1 (Mode) · Step 1.5 (Clarification Gate)

Read this at the very start of every fresh `/sdd-flow <task>` invocation (not `continue` — that routes through `protocols.md`). All spawns follow the SKILL's spawn-prompt construction checklist and Safety-Net obligations.

---

## Step 0: Scope Assessment

When invoked, the orchestrator first (for `--next-tier`, steps 1–3 are replaced — see *Starting the next tier* at the end of this step):

1. Extracts the **task description** from the user's input.
2. Extracts an **issue/ticket number** if provided (`#42`, `PROJ-123`); otherwise determines sequential numbering by checking existing `SDD/` artifacts.
3. Derives a **kebab-case `[feature-name]`** from the task.
4. Resolves all canonical identifiers (SKILL → Canonical Identifiers).
5. **Resolves SKILL_ROOT, CATALOG, STANDARD, and TIERS** (SKILL → SKILL_ROOT resolution) and records all four, with the resolved identifiers and any `--tier N` value, in `SDD/orchestration/progress.md` (create the file + parent dirs if absent). Resumed sessions re-derive every body path from this record. A missing CATALOG closes the `agent_security:` gate for the run (warning only, no halt). A missing STANDARD (`SKILL_ROOT/references/enforcement-sites.md`) or TIERS (`PLUGIN_ROOT/skills/simplicity-challenge/references/tiers.md`) is a broken install: halt and tell the user.

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

### Starting the next tier (`--next-tier`)

`/sdd-flow --next-tier [feature-name]` starts a new cycle for the next delivery tier of a feature that already shipped one. A tier is one complete cycle with its own number, brief, spec, reviews, and commits; this is how the next one begins. It replaces steps 1–3 at the top of Step 0:

1. **Find the tier plan.** `SDD/flow/TIERS-[feature-name].md`. With no name given, use the only tier plan that has a tier neither `shipped` nor `dropped`; if there are several, list them and stop.
2. **Pick the tier.** The lowest-numbered tier whose status is neither `shipped` nor `dropped`. Refuse, naming the reason, if the tier below it is not `shipped` (a tier is used before the next is planned), or if no tier is left.
3. **Resolve identifiers.** `[###]` = the next sequential number. `[feature-name]` = the tier plan's feature name with `-t2` or `-t3` appended. The task description = that tier's sketch plus the Deferred rows aimed at it, quoted from the tier plan.
4. **Record** in `progress.md`, beside the identifiers: `Next-tier cycle: Tier N`, **TIER_PLAN** = the tier plan's path (it keeps the first tier's feature name — every later spawn is given this path, never one derived from the suffixed name), and the previous tier's research document (from the tier plan's `Built in` column: the same number and name as that spec).

Then continue with steps 4–5 of the list at the top of Step 0 and the scope-assessment spawn, as usual. On any other invocation, **TIER_PLAN** is `SDD/flow/TIERS-[feature-name].md`.

---

## Step 1: Parse Input and Select Mode

Reached only after Step 0 says the feature fits one cycle. If the invocation already carried `--auto` or `--supervised`, use it and skip the prompt. Otherwise ask:

> **Choose execution mode:**
> **Supervised** (default) — runs autonomously but pauses at two checkpoints: after the design brief, and before committing implementation.
> **Autonomous** — stops for you to approve the design brief, and again only if the spec departs from it, then runs to the end.
> Reply **s** for supervised or **a** for autonomous. (Default: supervised)

Record the chosen mode in `progress.md`.

---

## Step 1.5: Pre-Research Clarification Gate

**Fires in BOTH supervised and autonomous modes.** Externalizing the design concept (Brooks) before any work begins is the highest-leverage artifact, and the cost of skipping propagates through every downstream phase. This is one of two unconditional autonomous-mode stops (with the Step 2.5 design gate); Step 3g adds a third only when the spec departs from the approved brief.

**On a next-tier cycle the interview is about feedback.** `/research-clarify` has a next-tier branch: it loads the tier plan, walks its `## Feedback` notes, and asks what using the previous tier showed. This is the same gate doing a different job, not an extra pause — say so in the prompt below ("Tell me what using Tier N showed" in place of "Clarify the design concept first?"), and name the tier plan's path along with the resolved identifiers.

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
