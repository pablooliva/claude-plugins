# Phase: Setup — Step 0 (Scope) · Step 1.5 (Clarification Gate)

Read this at the very start of every fresh `/sdd-flow <task>` invocation (not `continue` — that routes through `phases/rare/resume.md`). All spawns follow the SKILL's spawn-prompt construction checklist and Safety-Net obligations.

---

## Step 0: Scope Assessment

When invoked, the orchestrator first (for `--next-tier`, steps 1–3 are replaced — see *Starting the next tier* at the end of this step):

1. Extracts the **task description** from the user's input.
2. Extracts an **issue/ticket number** if provided (`#42`, `PROJ-123`); otherwise determines sequential numbering by checking existing `SDD/` artifacts.
3. Derives a **kebab-case `[feature-name]`** from the task.
4. Resolves all canonical identifiers (SKILL → Canonical Identifiers).
5. **Resolves SKILL_ROOT, CATALOG, TIERS, and TRACING** (SKILL → SKILL_ROOT resolution) and appends the **Step 0 record** to `SDD/.records/progress.md` (create the file + parent dirs if absent; a new `SDD/.records/` also gets its `.gitignore` holding `*` — `SKILL.md` → Records stay out of git): a block whose first line is exactly `## Flow Started - [###]-[feature-name]`, followed by the resolved identifiers, the four resolved paths, the line `Reviewer: …` (below), and any `--tier N` value. Resumed sessions re-derive every body path from this record, and Phase Detection reads only the lines after the latest `## Flow Started - ` line (`phases/rare/resume.md`) — an earlier feature's markers above it never answer for this one. A missing CATALOG (`PLUGIN_ROOT/skills/ai-agent-security-review/references/owasp-ai-agent-controls.md`), TIERS (`PLUGIN_ROOT/skills/simplicity-challenge/references/tiers.md`), or TRACING (`PLUGIN_ROOT/skills/observability-init/references/tracing.md`) is a broken install: halt and tell the user. Whether the application has the tracing foundation (`SDD/OBSERVABILITY.md`) is not settled here: the design gate settles it, on approval (`phases/design-gate.md` → 2.5b).

**Who reviews is settled in step 5 too.** Before writing the Step 0 record, run `python3 "$SKILL_ROOT/scripts/second-model-review.py" resolve` and put what follows `Result: ` into the record as the line `Reviewer: …`. `references/second-model-review.md` §2 says what each exit status means: Codex reviews this cycle, or the reviews fall back to Claude subagents and the user is told. The answer is taken once for the cycle.

Then spawn ONE **`agent-engineering:sdd-workhorse`** subagent for scope assessment. There is no dedicated body file — embed this brief directly in the prompt:

- **Inputs:** task description, codebase access.
- **Outputs:** either a decomposition document or a "proceed" signal (bounded return). It never picks or starts an item of its decomposition, and nothing it writes or returns says the flow goes on: a decomposition stops the flow (below).
- **Task:** Determine whether the feature fits a single SDD cycle (research → planning → implementation) or should be decomposed. Judgment call, not a formula — the subagent explains its reasoning against these heuristics: number of distinct components/systems touched; number of independent user-facing behaviors; natural seams where each piece delivers standalone value; specification complexity (would the SPEC hold too many requirements for one implementation subagent?); test surface (would tests span unrelated subsystems?).
- This subagent does file discovery **inline** (Grep/Glob/Read). It carries the Safety-Net Rule, a counter file, and the `research-compact.md` compact body path (scope work is research-shaped).

### If the scope is manageable (single SDD cycle)

The subagent returns a "proceed" signal. The orchestrator proceeds directly to **Step 1.5** with no pause — the user should not notice this gate for small requests.

### If the scope is too large (decomposition needed)

The subagent writes `SDD/flow/DECOMPOSITION-[###]-[feature-name].md` containing: (1) **Rationale** referencing the heuristics; (2) a **decomposition checklist** of smaller, independently deliverable features, each a self-contained task description suitable as `/sdd-flow` input, with a note on what it delivers and why it is sequenced there, plus any dependencies; (3) a **dependency map**. Put this in the scope spawn's prompt, with the path resolved.

When it returns that the scope is too large, read `phases/rare/decomposition.md` and follow it — it ends the flow with a stop.

### Starting the next tier (`--next-tier`)

On `/sdd-flow --next-tier [feature-name]`, read `phases/rare/next-tier.md`: it replaces steps 1–3 at the top of Step 0 and skips the scope assessment. On any other invocation, **TIER_PLAN** is `SDD/flow/TIERS-[feature-name].md`.

---

## Step 1.5: Pre-Research Clarification Gate

Reached after Step 0 says the feature fits one cycle — or, on a next-tier cycle, straight after *Starting the next tier*. Externalizing the design concept (Brooks) before any work begins is the highest-leverage artifact, and the cost of skipping propagates through every downstream phase.

**On a next-tier cycle the interview is about feedback.** `/research-clarify` has a next-tier branch: it loads the tier plan, walks its `## Feedback` notes, and asks what using the previous tier showed. This is the same gate doing a different job, not an extra pause — say so in the prompt below ("Tell me what using Tier N showed" in place of "Clarify the design concept first?"), and name the tier plan's path along with the resolved identifiers.

**Skip the gate if** `SDD/research/CLARIFICATION-[###]-[feature-name].md` already exists (user pre-clarified) — proceed to Step 2; the research subagent picks it up automatically.

Otherwise ask, every time:

> **Clarify the design concept first?**
> `/research-clarify` is a structured interview that externalizes your design concept before any codebase research. **Strongly recommended** unless your task description is already crisp.
> Reply **y** to clarify first, or **n** to proceed directly and accept the design-concept risk (crisp tickets / very small changes).

- **y** → write an `## Awaiting Clarification` block (with the resolved identifiers: `[###]=<value>`, `[feature-name]=<value>` — use these exact values with `/research-clarify` so the artifact path aligns) to `progress.md`, tell the user to run `/research-clarify` and then `/sdd-flow continue`, and **STOP**. Session Resumption picks up at Step 2 once the artifact exists.
- **n** → write a `## Clarification Skipped (user opt-out)` block to `progress.md` so the record shows the gate was skipped, and proceed to Step 2.

### Orchestrator-discipline note

The orchestrator does NOT spawn a subagent to "perform the clarification." Grilling extracts the user's design concept from their head; a subagent reasoning about the task description is a different artifact and produces false fidelity. The gate is satisfied only by a human-driven `/research-clarify` run, a pre-existing CLARIFICATION artifact, or the user's **n**.

Once the gate is cleared, proceed to **Step 2** → read `phases/research.md`.
