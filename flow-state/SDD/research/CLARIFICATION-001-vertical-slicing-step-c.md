# CLARIFICATION-001-vertical-slicing-step-c

**Type:** Pointer artifact (proposal-derived; no interactive `/research-clarify` run).
**Authoritative design source:** `proposals/vertical-slicing-decomposition.md`
**Scope of this sdd-flow run:** **Step C** of that proposal — Step A (the spec template `## Delivery Slices` block in `sdd/commands/planning-start.md`) is already merged and is OFF-LIMITS.
**Delivery mode for this implementation:** `whole-feature` (per user directive — meta-irony intended; per-slice infrastructure is what we are *building* here, not yet usable).

---

## Why this artifact exists in this shape

The `/sdd-flow` Step 1.5 clarification gate requires a `CLARIFICATION-[###]-[feature-name].md` artifact to exist before research begins. Normally that artifact is produced by an interactive `/research-clarify` interview that externalizes the user's design concept.

In this run, the user has already externalized the design concept *as the proposal*. The proposal contains the design intent, the alternatives considered, the resolved decisions, and the remaining open questions — all of which is what `/research-clarify` would have produced. Re-grilling the user would duplicate work and risk the model "filling in" details the human has not actually decided.

This artifact therefore serves two jobs only:

1. **Satisfy the gate** — the file exists at the expected path, so Step 2 can proceed.
2. **Lock the orchestration boundaries** — extract the locked decisions, conservative defaults, and constraints that downstream subagents (research, planning, implementation, reviewers) must apply uniformly. Without this, the planning subagent will quietly relitigate the open questions and downstream subagents will diverge from the user's intent.

Downstream subagents MUST treat this artifact's "Locked" and "Conservative defaults" sections as binding. They MAY surface concerns about a default in their critical review but MUST NOT silently override.

---

## Recursion-trap warning (apply to ALL phases)

**This sdd-flow run is modifying the very `sdd-flow` skill that orchestrates it, plus the SDD plugin commands it relies on.** A naive subagent reading the proposal could conclude "the new directory layout takes effect immediately" and start writing `progress.md` to `SDD/orchestration/` instead of `SDD/prompts/context-management/`. That would split this run's artifacts across two trees and break Session Resumption.

**The rule for THIS run:**

- THIS run uses the **legacy paths** under `SDD/prompts/context-management/` (for orchestration state) and `SDD/prompts/PROMPT-001-...` (for the implementation tracker).
- The **new layout** (`SDD/implementation/`, `SDD/orchestration/`, `IMPLEMENTATION-PLAN-XXX`) being implemented in this run applies to **future runs** that occur after the SDD plugin's major-version bump and the migration helper has executed.
- Subagents implementing the new layout must do so in **plugin command source files** and the **sdd-flow skill source file** — not by relocating live in-flight artifacts.

Every phase-execution and fix subagent prompt MUST embed this warning verbatim.

---

## Step A locked region (off-limits in `sdd/commands/planning-start.md`)

Step A is already merged (commit `ffeec97`). The user's directive: *"do not modify planning-start.md's spec template structure further."* This scopes to the spec template's `## Delivery Slices` block specifically — NOT the whole file.

**Off-limits:**
- The frontmatter line `delivery_mode: whole-feature` (line 69) inside the spec template ` ```markdown ... ``` ` block.
- The entire `## Delivery Slices` template block in the spec template (lines 184–204): the explanatory blockquote, the `### SLICE-001:` template, the `### SLICE-002:` template, and the closing parenthetical.
- The slice-related checklist items already added under "Quality Checklist" (lines 375–379).

**Allowed to modify:**
- The frontmatter-fields documentation prose (lines 256+) explaining `delivery_mode:` — Step C may extend this prose to describe practicality-gate behavior, but must not contradict Step A's existing description.
- Step 6 ("Define Delivery Slices") in the Specification Creation Process — Step C may extend this step to wire in the practicality gate from §5 of the proposal, but must not change what Step 6 already says about populating the Slices section in per-slice mode.
- Anywhere else in `planning-start.md` that is unrelated to the spec template block itself.

When a subagent's edit touches `planning-start.md`, it MUST cite the exact line range it is editing and confirm that range is outside the locked region above.

---

## Locked decisions (from proposal — DO NOT relitigate)

These come from the proposal's "Resolved during proposal iteration" section. Subagents must implement them as stated.

1. **`delivery_mode:` frontmatter field exists**, defaults to `whole-feature`, opt-in `per-slice`. Spec critical review and panel review apply slice-integrity check **only** when `per-slice`.
2. **`--skip-slice-checkpoints` recommendation surfacing** — when enabled, "Open recommendations" accumulate in the rolling ledger and surface as a single consolidated block in the Step 4j announcement.
3. **Retrospectives may recommend re-planning** via the elevated-severity `## Recommended Re-planning` section in §6, which halts the flow even under `--skip-slice-checkpoints`.
4. **Per-slice review iteration cap = 3** with a progress-stall check (HIGH must strictly decrease, or MEDIUM when HIGH is zero). On halt, route findings to the user via the ledger's *Open recommendations awaiting user decision* section; in `--skip-slice-checkpoints` mode, halt the whole flow.
5. **Spec-amendment recommendation surfacing format** — per-recommendation summary in the slice-boundary pause message (one or two lines per affected entry); full proposed wording in the retrospective artifact, accessible via the path printed in the pause message.
6. **`PROMPT-XXX` → `IMPLEMENTATION-PLAN-XXX` rename** ships in the same major-version bump as the directory restructure; both are handled by the same migration helper command in one pass.
7. **Distribution: code merged, not forked.** `delivery_mode:` is the runtime branch. Slice commands ship as part of the SDD plugin and are inert (display friendly "requires `delivery_mode: per-slice`" message) when invoked outside per-slice mode. Documentation gets two clearly-distinct workflow sections in the SDD plugin README.
8. **Directory restructure applies to BOTH delivery modes** — one-time breaking change for all SDD users. Major-version bump (2.0.0). Migration helper provided.

---

## Conservative defaults for the six remaining open questions

The user's directive: *"the six remaining open questions should be defaulted conservatively per the guidance in each entry rather than relitigated."*

**Open Question 1 — Practicality-check gate's user-facing message:**
Default: **Mirror the Step 1.5 clarification gate's message shape closely.** Concretely:
- Supervised mode: ask the user "Per-slice was requested for this feature, but the planning subagent did not find meaningful vertical slices. Either (a) fall back to `whole-feature` for this feature only [recommended], or (b) push back — point at a slice boundary I missed and let me retry."
- Autonomous mode: halt the flow with the same options surfaced in a completion message; resume via `/sdd-flow continue --fall-back-to-whole-feature` or `/sdd-flow continue --retry-slicing "<hint about slice boundary>"`. Mirrors the Step 1.5 autonomous halt pattern bit-for-bit, with different option flags.

**Open Question 2 — Does Step 0 (scope assessment) need any change?**
Default: **No change.** Feature-level decomposition (Step 0) stays independent of slice-level decomposition (per-slice mode). Step 0's job is "is this *one* feature too big for one sdd-flow cycle?" Per-slice's job is "within one feature, what are the vertical threads?" These are orthogonal concerns at different granularities. Do not couple them.

**Open Question 3 — When `delivery_mode:` is absent, log a one-line note?**
Default: **Stay silent.** The planning-start.md spec template explicitly defaults to `whole-feature`; absence is well-defined as `whole-feature`. A log line would be noise during the migration window when the bulk of specs (existing ones) lack the field. The default behavior is the "no surprise" behavior; log only when the surprise happens.

**Open Question 4 — Slice retrospective: structured template or free-form prose?**
Default: **Hybrid — structured for recommendation sections, free-form for the learning narrative.** Specifically:
- The `## Recommended SPEC Amendments` and `## Recommended Re-planning` sections MUST follow a structured template (each recommendation cites: which `SLICE-XXX`/`MODULE-XXX`/`REQ-XXX`/`EDGE-XXX`/`FAIL-XXX` is affected; what the SPEC currently says; what should change with proposed wording; why, grounded in observation).
- The "what was learned" narrative is **free-form prose** so the retrospective subagent can express insights that don't fit a template.
- The ledger update step is **structured** (the four named sections — Interface contract clarifications / Integration patterns discovered / Performance / failure modes observed / Open recommendations).

**Open Question 5 — `/slice-review` thin wrapper or distinct command?**
Default: **Thin wrapper over `/code-review`, scoped to the slice's files only.** Rationale (from the proposal itself): "Wrapper minimizes duplication." The wrapper's job is to:
- Read `delivery_mode:` and the active `SLICE-XXX` ID
- Compute the slice's file set from the SLICE's `Modules touched` plus the implementation plan's slice progress entries
- Invoke `/code-review`'s logic with that scoped file set
- Write the per-slice review doc under `SDD/reviews/REVIEW-SLICE-XXX-...md` (pattern parallels the existing `REVIEW-XXX-...md` shape; SLICE-aware naming reflects scope)
If slice-review behavior needs to diverge later, fork at that point — not preemptively.

**Open Question 6 — Slice subagent prompts: prior retros + ledger, or strictly ledger?**
Default: **Strictly the ledger only.** Rationale (from the proposal): "Strict is cleaner; the ledger was designed to avoid the propagation cost." The ledger consolidates and supersedes; that's its purpose. Including prior retros alongside reintroduces the cost the ledger was designed to eliminate. Subagents that need an audit trail can read the individual retros from disk on demand — but the prompt path is the ledger.

---

## What this run is NOT

- NOT modifying the `## Delivery Slices` spec template block in `sdd/commands/planning-start.md`.
- NOT executing the directory restructure on this run's own artifacts (legacy paths only — see Recursion-trap warning).
- NOT re-running Step A.
- NOT producing a per-slice spec for this feature (whole-feature mode).
- NOT relitigating the six open questions above.

---

## Branches and questions for the research subagent

The research subagent (Step 2a) MUST address ALL of the following branches and resolve every question, or explicitly defer with rationale. The Step 2c critical review's "Design Concept Fidelity" check verifies this.

### Branch 1: SDD plugin command audit
Catalogue every command file under `sdd/commands/` and identify, for each:
- Which references will need updating when `prompts/` → `implementation/` + `orchestration/` and `PROMPT-XXX` → `IMPLEMENTATION-PLAN-XXX`.
- Whether the command needs `delivery_mode:` awareness in per-slice mode (explicit branch or no change).
- Whether the command emits artifacts that change name/path under the restructure.

### Branch 2: sdd-flow skill audit
The current `agent-engineering/skills/sdd-flow/SKILL.md` is ~700 lines. Identify:
- Every Artifact Paths Contract entry that changes under the restructure/rename.
- Every Phase Detection Priority rule that changes.
- The exact insertion points for the per-slice Step 4 state machine, the slice-boundary checkpoint axis, the `--skip-slice-checkpoints` flag, and the re-planning trigger.
- The interaction with `--skip-clarify` (slice-checkpoint flag mirrors that pattern, per §6).

### Branch 3: New command surface
For each of `/slice-start`, `/slice-review`, `/slice-retro`, `/slice-commit`, plus `/sdd-migrate-layout`:
- Inputs and outputs.
- How they read the active slice ID (CLI arg, derived from in-progress entry in IMPLEMENTATION-PLAN, or both).
- Inert-mode behavior when `delivery_mode: whole-feature` (slice commands only — migrate-layout is mode-agnostic).
- How `/slice-review` wraps `/code-review` (per Open Question 5 default).

### Branch 4: Migration mechanics for `/sdd-migrate-layout`
- Detection: how does it determine "old layout present" vs "already migrated"?
- Move set: enumerate the exact `git mv` operations.
- Idempotence: re-running should be a no-op once migrated.
- In-flight runs: what happens if `/sdd-migrate-layout` runs while a flow is mid-execution? (Hint: the migration helper should refuse if `progress.md` shows an active phase.)
- Rollback: documented manual procedure if migration goes wrong.

### Branch 5: Slice-integrity check additions to reviews
- Exact insertion points in `sdd/commands/critical-review.md` and `sdd/commands/spec-review-panel.md`.
- The check's text (per §4 of the proposal).
- Mode-gating: how the check knows to fire only when `delivery_mode: per-slice`.

### Branch 6: Documentation surface
- The SDD plugin README's two-workflow restructure (per §Distribution Strategy revision).
- The agent-engineering plugin README — does it need updates for the new sdd-flow Step 4 state machine? (Probably yes, at the level of "what changed in this version".)
- The repo-root README — any updates needed?
- The `plugin-installation-scope.md` document — likely no changes, but verify.

### Branch 7: Versioning and marketplace
- SDD plugin: bump to 2.0.0 (locked decision #6, #8). Update `sdd/.claude-plugin/plugin.json` and the matching entry in `.claude-plugin/marketplace.json`.
- agent-engineering plugin: appropriate bump (likely 0.4.0 — additive feature, but interacts with SDD 2.0.0). Update both files.
- Verify both files stay in sync (per CLAUDE.md guidance: "They drift easily — check both.").

### Branch 8: Hooks and infrastructure
Are the existing `hooks/log_subagent_call.py` paths affected by the directory restructure? (They write under the orchestration tree.) Identify the exact code that needs adjustment.

### Branch 9: Test surface
The repo doesn't have automated tests for plugins (commands are markdown). What constitutes "implemented and verified" for each command? Likely: each command's structure follows existing patterns (frontmatter, sections, conventions); critical-review can read it; manual sanity check of inert-mode behavior. The implementation phase MUST define the verification approach explicitly per touch point.

### Open questions for research to resolve
- Q-A: When the user runs the migration helper, do existing `IMPLEMENTATION-SUMMARY-XXX-...md` files in `prompts/implementation-complete/` need renaming or just relocation? (Proposal implies relocation only — same filename, new parent.) Confirm by checking the proposal's Directory Layout section against current naming.
- Q-B: The proposal's `RETROSPECTIVE-SLICE-XXX-feature-YYYY-MM-DD.md` filename — does the `feature` in the filename refer to feature-name (slug) or feature-number (`[###]`)? Most other artifacts use `[feature-name]`; resolve unambiguously and standardize.
- Q-C: Does `/slice-commit` enforce that the working tree contains only slice-scoped files (i.e., refuses to commit unrelated changes), or does it just produce a commit with a slice-aware message and trust the user not to stage cross-slice changes? Default to the looser interpretation (commit with structured message; user controls staging) unless research surfaces a strong reason for the stricter check.
- Q-D: When a re-planning recommendation fires and the user runs `/sdd-flow continue --replan`, the proposal says implementation resumes "from `SLICE-001` (or from a user-specified slice if some completed slices remain valid)." How is "completed slices remain valid" assessed? Default: user judgment, surfaced in the resume prompt. The orchestrator does not auto-determine validity.
- Q-E: The `/slice-retro` command writes both the individual retrospective AND the ledger update. If only one of these writes succeeds (e.g., disk error mid-operation), what is the recovery? Default: write the individual retrospective FIRST (it's the audit trail; never modified after), then the ledger update (which can be retried by re-running `/slice-retro` — the retro subagent should detect "ledger is missing entries from existing retros" and reconcile). The retro file existing without the ledger update is a recoverable state; the inverse is not.

---

## What success looks like for this sdd-flow run

The implementation is complete when:

1. All proposal §1–§6 changes (per-slice behavior in sdd-flow, slice commands, retros, ledger, checkpoint axis, re-planning trigger, slice-integrity reviews, practicality gate) are implemented in the SDD plugin and `sdd-flow` skill source.
2. The directory restructure (proposal "Directory Layout" section) is implemented in the plugin/skill source — i.e., the source code emits the new paths going forward — *without* relocating this run's own artifacts.
3. The `PROMPT-XXX` → `IMPLEMENTATION-PLAN-XXX` rename is propagated through all command/skill files.
4. The `/sdd-migrate-layout` command exists and is documented.
5. SDD plugin bumps to 2.0.0; agent-engineering bumps to an appropriate minor version. Marketplace.json reflects both.
6. SDD plugin README has the two clearly-distinct workflow sections per the revised Distribution Strategy.
7. Whole-feature mode behavior is preserved bit-for-bit — a user not opting into `per-slice` sees zero behavioral change in any phase.
8. Step A's locked region in `sdd/commands/planning-start.md` is unchanged.
