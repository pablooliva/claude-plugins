---
review_panel: [security, data-modeling, api-contract, module-depth]
eval_required: false
cross_cutting_decisions: []
delivery_mode: whole-feature
---

# SPEC-001-vertical-slicing-step-c

## Executive Summary

- **Based on Research:** RESEARCH-001-vertical-slicing-step-c.md
- **Clarification:** CLARIFICATION-001-vertical-slicing-step-c.md
- **ADRs respected:** 0001 (merged codebase + `delivery_mode` frontmatter), 0002 (directory restructure + PROMPT → IMPLEMENTATION-PLAN rename).
- **Authoritative design source:** `proposals/vertical-slicing-decomposition.md`
- **Creation Date:** 2026-05-05
- **Author:** Claude (Step 3a planning subagent for `/sdd-flow` Step C of the vertical-slicing decomposition).
- **Status:** Draft

### What this spec is

Step C of the vertical-slicing decomposition: implement per-slice delivery behavior end-to-end across the SDD plugin commands and the `agent-engineering/sdd-flow` skill, plus the directory restructure (`SDD/prompts/` → `SDD/implementation/` + `SDD/orchestration/`), the `PROMPT-XXX` → `IMPLEMENTATION-PLAN-XXX` rename, the `/sdd-migrate-layout` migration helper, slice-integrity checks in the spec critical review and panel review, the practicality gate, and the SDD/agent-engineering version bumps.

### Frontmatter justification

- **`review_panel: [security, data-modeling, api-contract, module-depth]`** — `module-depth` (modules are central to this feature; eight MODULE-XXX entries below). `api-contract` (the slash-command surface — `/slice-start`, `/slice-review`, `/slice-retro`, `/slice-commit`, `/sdd-migrate-layout` — is a user-facing API). `data-modeling` (directory layout + filename conventions are project-wide data shape that bind every future SDD command). `security` (light, but `/sdd-migrate-layout` is destructive on user repos and the active-flow refusal is a load-bearing safety check). `performance` is **not** included — markdown command files have negligible perf surface.
- **`eval_required: false`** — every artifact this feature produces is deterministic markdown / source code. No LLM output, no probabilistic behavior, no classification or extraction or summarization. Eval scaffolding adds no signal here.
- **`cross_cutting_decisions: []`** — both cross-cutting decisions (ADR 0001, ADR 0002) were captured at research time. This spec implements those captured decisions; it does not introduce new cross-cutting decisions. Empty list is correct.
- **`delivery_mode: whole-feature`** — per user directive. Meta-irony intended: this feature is what *builds* the per-slice infrastructure, so the per-slice infrastructure is not yet usable for this feature's own delivery. The `## Delivery Slices` section is omitted entirely (per Step A's locked template behavior).

### Step A locked region (off-limits — verified)

In `sdd/commands/planning-start.md`:
- Line 69: `delivery_mode: whole-feature` in the spec template frontmatter — UNTOUCHED.
- Lines 184–204: the entire `## Delivery Slices` template block (blockquote, SLICE-001 template, SLICE-002 template, closing parenthetical) — UNTOUCHED.
- Lines 375–379: the slice-related Quality Checklist items — UNTOUCHED.

Allowed regions in `planning-start.md`: line 271 (frontmatter-fields prose for `delivery_mode:`), Step 6 starting at line 305 (Define Delivery Slices), and any region unrelated to the spec template block. Every REQ/EDGE/MODULE that touches `planning-start.md` cites the line range so reviewers can verify locked-region compliance.

## Research Foundation

### Production Issues Addressed (issues this restructure resolves)

- Existing `SDD/prompts/` overload mixes per-feature implementation artifacts (PROMPT tracker, summaries) with runtime orchestration state (progress.md, subagent-call logs, counters, compactions) and would compound further as per-slice retros and the rolling ledger land. ADR 0002 captures the cleanup decision.
- The `PROMPT-XXX-feature.md` filename describes the document's role at creation time, not what it is. Per ADR 0002, rename to `IMPLEMENTATION-PLAN-XXX-feature.md`.
- Horizontal-only delivery (every layer built across all REQs before the next layer begins) cannot surface module interaction or contract risk early. Per-slice mode introduces a vertical-thread alternative gated by `delivery_mode: per-slice`.
- Distribution risk: a forked `sdd-slices` plugin would duplicate ~18 SDD commands and a ~700-line skill that are 80%+ shared. ADR 0001 captures the merged-codebase decision; this spec implements it.

### Stakeholder Validation

- **SDD plugin maintainers (Pablo Oliva + future contributors):** need a coherent diff that leaves no orphaned `prompts/` references; need marketplace.json + plugin.json drift surfaces in sync; need changelog + README explaining the breaking change and the migration helper.
- **`sdd-flow` skill consumers (auto-orchestrated runs):** need the `delivery_mode` branch in Step 4 to route correctly; need `--skip-slice-checkpoints` to mirror the `--skip-clarify` precedent bit-for-bit; need the practicality-gate halt to mirror the Step 1.5 autonomous halt's shape; need `/sdd-flow continue` to detect both `## Awaiting Clarification` and `## Awaiting Slicing Decision` blocks.
- **Manual SDD users (no sdd-flow):** need `/implementation-start` to behave bit-for-bit identically when `delivery_mode: whole-feature`; need `/slice-*` commands present but inert in whole-feature mode (so they don't pollute autocomplete with broken commands); need the README's two-workflow restructure to make the mode boundary obvious.
- **Plugin marketplace operators:** need the major-version bump (1.2.0 → 2.0.0) to signal the breaking change; need agent-engineering bumped to 0.4.0 (additive but interacts with SDD 2.0.0); need both manifest + marketplace entries to stay in sync.
- **Existing in-flight runs (regression risk):** need this run's own artifacts to remain at LEGACY paths (recursion trap); need `/sdd-migrate-layout` to refuse during active flows; need Phase Detection to check the new path first AND fall back to the legacy path so resumption works during the migration window.

### System Integration Points

- `sdd/commands/planning-start.md:271` (frontmatter-fields prose, allowed) and `:305` (Step 6, allowed) — Step 6 extension to invoke the practicality gate. Locked region (lines 64–204 + 375–379) is OFF-LIMITS.
- `sdd/commands/implementation-start.md:34, 43, 51, 57, 69, 73, 104, 337` — path updates + PROMPT → IMPLEMENTATION-PLAN rename + new `delivery_mode`-aware branching at "Implementation Setup".
- `sdd/commands/critical-review.md:25` (PROMPT glob) and a new sub-section "Slice Integrity (per-slice mode only)" inserted between lines 110 and 112 of the Planning Phase Critical Review section.
- `sdd/commands/spec-review-panel.md` — new specialist 4.7 "Slice Integrity Specialist" + a new `#### Slice Integrity Findings` sub-header in the deliverable schema (lines 230–244), conditionally rendered only when `delivery_mode: per-slice`.
- `sdd/commands/code-review.md:27, 30, 76, 177, 180, 210, 243, 339` — path updates + rename throughout. No mode-awareness needed (`/slice-review` wraps it).
- `sdd/commands/implementation-complete.md:38, 62, 68, 79, 229, 289, 290, 318, 329, 500, 507, 508` — path updates + rename + per-slice IMPLEMENTATION-SUMMARY enrichment.
- `sdd/commands/implementation-test.md:47, 54, 65, 216, 399, 411, 419, 465, 475, 481, 490, 496, 531, 543` — path updates + rename + test-audit relocation to `SDD/implementation/test-audits/`.
- `sdd/commands/{research,planning,implementation}-compact.md` — compaction-file paths → `SDD/orchestration/compacted/`.
- `sdd/commands/{research-start, research-complete, research-compact, planning-complete, continue, adhoc-compact}.md` — progress.md path + compaction path + (where present) PROMPT glob.
- `sdd/commands/{commit, context-check}.md` — confirmed clean by grep; no edits needed.
- `agent-engineering/skills/sdd-flow/SKILL.md` — Artifact Paths Contract (lines 60–136), Phase Detection Priority (lines 636–645), Step 4 state machine (lines 518–621), Execution Modes (lines 215–280), Arguments table (line 695). Two narrative-prose lines also need updates: lines 319 and 487.
- `sdd/hooks/log_subagent_call.py:18` — `LOG_SUBDIR` constant single-line update.
- `.claude-plugin/marketplace.json:12, :30` — version bumps.
- `sdd/.claude-plugin/plugin.json:4`, `agent-engineering/.claude-plugin/plugin.json:4` — version bumps.
- `sdd/README.md` (decision aid + two-workflow restructure + changelog/migration), `agent-engineering/README.md` (skills note + version), repo-root `README.md` (minor description).

## Intent

### Problem Statement

The SDD plugin and `sdd-flow` skill currently support only horizontal feature delivery. Per-slice (vertical-thread) delivery is desirable for multi-layer features where module interaction risk is high, but is not currently expressible. Adding it requires (a) a runtime branch (`delivery_mode`), (b) a new command surface (`/slice-*`), (c) a state machine in Step 4 of `sdd-flow`, (d) review checks specific to slicing integrity, (e) a practicality gate, and (f) a coordinated directory restructure + filename rename so the artifact tree's semantic boundaries support the new artifacts cleanly.

### Solution Approach

Implement per-slice mode as additive behavior gated by a single frontmatter field (`delivery_mode`), per ADR 0001. Apply a one-time directory restructure and `PROMPT → IMPLEMENTATION-PLAN` rename to both delivery modes (per ADR 0002), shipped via the same `/sdd-migrate-layout` helper in one major-version bump. Preserve whole-feature behavior bit-for-bit modulo the forced rename + relocation. Make every new behavior gated on `delivery_mode: per-slice` so the runtime branch is explicit and testable.

### Expected Outcomes

- Whole-feature mode users see zero behavioral change beyond path strings (artifacts now land at `SDD/implementation/...` and `SDD/orchestration/...`).
- Per-slice users get the full slice cycle: per-slice subagent → per-slice code review → fix-findings → per-slice retrospective → per-slice commit → optional slice-boundary pause → next slice. The end-of-feature cycle (critical review → completion → eval scaffolding → end-of-feature commit) runs once after all slices land.
- Spec critical review and panel review fire slice-integrity checks only when `delivery_mode: per-slice`.
- Re-planning recommendations from a slice retrospective halt the flow even under `--skip-slice-checkpoints`.
- The migration helper turns a one-time breaking change into a single, safe, idempotent command.

## Success Criteria

### Functional Requirements

- **REQ-001:** `sdd/commands/planning-start.md` Step 6 (line 305+, allowed region) reads `delivery_mode:` from the spec frontmatter and invokes the practicality gate when set to `per-slice`. The locked region (lines 64–204 + 375–379) is unchanged. **`delivery_mode:` value validation:** the canonical enum is `{whole-feature, per-slice}` (exact, lowercase, hyphenated). Absent field defaults to `whole-feature` silently per OQ-3 (locked default — unchanged). Any other value (typos like `delivry_mode` field name, or values like `per_slice`, `PerSlice`, `vertical-thread`, `whole_feature`, etc.) is treated as invalid: the planning subagent / `/sdd:planning-start` MUST fail with a clear error naming (a) the SPEC file path, (b) the offending value verbatim, and (c) the canonical enum. The subagent does NOT silently fall through to the default branch; an emitted `## Awaiting Slicing Decision` block citing the invalid value is acceptable as the halt mechanism in autonomous mode (mirrors REQ-011's halt shape). This rule applies uniformly wherever `delivery_mode:` is read (REQ-001, REQ-002, REQ-012's Step 4 entry); each consumer either fails fast with the same error shape or delegates the read to a single shared validation step. Spec refs: MODULE-001, MODULE-004.
- **REQ-002:** `sdd/commands/implementation-start.md` reads `delivery_mode:` from the SPEC frontmatter at the "Read Progress File" step (line 33+) and branches: in `whole-feature` mode it scaffolds an IMPLEMENTATION-PLAN with the existing tracker shape (renamed from PROMPT); in `per-slice` mode it scaffolds an IMPLEMENTATION-PLAN that includes a `## Slice Progress` table immediately after the header. Spec refs: MODULE-001, MODULE-007.
- **REQ-003:** A new `/slice-start` command (`sdd/commands/slice-start.md`) reads the active SLICE-XXX (CLI arg if provided; otherwise the first `Not Started` row in the IMPLEMENTATION-PLAN's `## Slice Progress` table; if multiple, prompts the user — never silently picks). It updates the slice's row in `## Slice Progress` to `In Progress`, loads the rolling ledger (`SDD/implementation/slices/LEARNINGS-FEATURE-[feature-name].md` — kebab-case feature-name slug, e.g. `LEARNINGS-FEATURE-audit-logging.md`; resolved per CLARIFICATION OQ-B) if it exists, and updates `progress.md`. Spec refs: MODULE-002, MODULE-007.
- **REQ-004:** A new `/slice-review` command (`sdd/commands/slice-review.md`) is a thin wrapper over `/code-review` per OQ-5 conservative default. It computes the slice's file set as the intersection of (a) the slice's `Modules touched` field in the SPEC and (b) the IMPLEMENTATION-PLAN's per-slice progress entries. If the two disagree, it prefers the IMPLEMENTATION-PLAN list and surfaces the divergence as a finding. It writes output to `SDD/reviews/REVIEW-SLICE-XXX-[feature-name]-[YYYY-MM-DD].md` (hyphenated date form, uniform across all new artifact families introduced by this feature — RETROSPECTIVE-SLICE, REVIEW-SLICE; resolves panel deferred LOW-13 on date-format consistency). Pre-existing REVIEW artifacts authored before SDD 2.0.0 may continue to use `[YYYYMMDD]`; the carry-forward is internally consistent within the legacy family. Spec refs: MODULE-002.
- **REQ-005:** A new `/slice-retro` command (`sdd/commands/slice-retro.md`) writes its outputs in this strict order (per OQ-E conservative default): FIRST `SDD/implementation/slices/RETROSPECTIVE-SLICE-XXX-[feature-name]-[YYYY-MM-DD].md` (audit trail; never modified after writing); THEN updates `SDD/implementation/slices/LEARNINGS-FEATURE-[feature-name].md` in place (kebab-case feature-name slug per CLARIFICATION OQ-B; consolidate, refine, supersede — do not just append). Retro structure follows OQ-4 conservative default (hybrid: structured `## Recommended SPEC Amendments` and `## Recommended Re-planning` sections + free-form learning narrative + structured ledger sections). **Re-invocation policy (when a retrospective for the slice already exists at the canonical path):** the command MUST refuse loudly with the message `Retrospective for SLICE-XXX already exists at <path>. Retrospectives are an audit trail and a second-write must be deliberate. Use `/slice-retro SLICE-XXX --reconcile-ledger` to refresh the ledger from the existing retro; otherwise the audit trail is final.` This is the default policy (option (a) per panel resolution — fail loudly). The `--reconcile-ledger` mode (per EDGE-007 / FAIL-003) is the documented escape hatch when the ledger is out of sync with on-disk retros. Spec refs: MODULE-002.
- **REQ-006:** A new `/slice-commit` command (`sdd/commands/slice-commit.md`) per OQ-C conservative default is looser-staging: it lists `git status`, asks the user to confirm the staged set looks slice-scoped, then commits with a structured message of the form `slice: SLICE-XXX <Concentrated function summary>` referencing SPEC-XXX and the retrospective path. The commit message MUST be constructed via heredoc (mirrors existing `/commit` precedent) — no shell-string concatenation, no inline `git commit -m "$summary"` interpolation; this neutralizes shell-metacharacter / command-substitution hazards in the auto-derived summary text. It does NOT enforce that the working tree contains only slice-scoped files. It does NOT use `--no-verify` and does NOT add co-author attribution (project convention; mirrors `/commit`). Spec refs: MODULE-002.
- **REQ-007:** All four `/slice-*` commands are inert outside per-slice mode. When `delivery_mode != per-slice` (or the field is absent), each command exits with the friendly message: *"This command requires `delivery_mode: per-slice` in the spec frontmatter. Current spec uses `delivery_mode: <value>`. Run `/implementation-start` instead, or set `delivery_mode: per-slice` in your spec and re-run `/planning-start`."* The message names the field, the required value, and the recommended alternative action. Spec refs: MODULE-002.
- **REQ-008:** A new `/sdd-migrate-layout` command (`sdd/commands/sdd-migrate-layout.md`) is mode-agnostic. It detects whether the old layout is present (`SDD/prompts/` exists with content) and whether the new layout is already in place. It refuses with a clear message when `progress.md` shows an active phase status (anything other than `COMPLETE`). It performs a documented set of `git mv` operations (preserving git history) to relocate every file enumerated in research §Branch 4. It is idempotent: re-running on a migrated tree exits with "already migrated" (or "nothing to migrate") and zero changes. It detects bash availability before performing moves and refuses on non-bash shells with explicit "On Windows, run from Git Bash" guidance. **Partial-migration detection (fourth state of the migration helper's 4-state machine, surfaced explicitly to users per panel data-modeling LOW):** if BOTH `SDD/prompts/` AND `SDD/orchestration/` are populated (state from a prior crashed run), the command refuses with: `Both old and new layouts contain content; previous migration may have crashed. Inspect manually; resolve by hand before re-running.` Documented in the migration helper's command body. **Refusal-message discipline:** all refusal paths (active-flow, partial-migration, non-bash shell, parse-failure per SEC-002 fail-closed) follow the REQ-007 message-discipline standard: name the detected condition, name the resolution path, exit cleanly without partial state writes. Spec refs: MODULE-005.
- **REQ-009:** `sdd/commands/critical-review.md` Planning Phase Critical Review (lines 99–159) gains a new sub-section "Slice Integrity (per-slice mode only)" inserted between the existing "Specification Weaknesses" (lines 103–110) and "Research Alignment Issues" (lines 112–117). The sub-section's checks fire only when `delivery_mode: per-slice` and are skipped silently otherwise. Check items follow research §Branch 5 verbatim. Spec refs: MODULE-003.
- **REQ-010:** `sdd/commands/spec-review-panel.md` gains a new specialist 4.7 "Slice Integrity Specialist" and the deliverable schema at lines 230–244 gains a `#### Slice Integrity Findings` sub-header. Both are conditionally rendered only when `delivery_mode: per-slice`. In whole-feature mode, the specialist is skipped silently and the sub-header is omitted entirely (not rendered with an "n/a" placeholder). Severity-aggregation rules at lines 196–200 apply unchanged — slice-integrity HIGH/MEDIUM/LOW findings flow into the same totals as every other specialist's findings. Spec refs: MODULE-003.
- **REQ-011:** The practicality gate fires only in `delivery_mode: per-slice`. It evaluates the four boolean heuristics defined in research §"Practicality-gate detection logic" (single-module touch-set, no-thinner-happy-path, universal-slice REQ touch, single concentrated function), plus a qualitative judgment-call escape. If ANY heuristic returns true, the planning subagent populates `## Delivery Slices` with `Slicing not applicable: <reason>` (citing the firing heuristic) and emits an `## Awaiting Slicing Decision` block to `progress.md` mirroring `## Awaiting Clarification` exactly. In supervised mode, the subagent surfaces the user options inline; in autonomous mode, the flow halts. **Audit-trail discipline for the qualitative-judgment escape (per panel module-depth LOW):** when all four boolean heuristics return false but the planning subagent's qualitative judgment-call escape fires anyway, the `<reason>` text MUST begin with the literal prefix `Qualitative judgment: ` followed by the specific concern. This distinguishes free-form escape firings from boolean-heuristic firings in the audit trail (`progress.md` and the `## Delivery Slices` annotation), so a retrospective reader can tell at a glance which class of signal halted the flow. Spec refs: MODULE-004.
- **REQ-012:** `sdd-flow` Step 4 routes by `delivery_mode:` read from the SPEC frontmatter. In `whole-feature` mode the existing horizontal flow runs unchanged (modulo the forced rename + relocation in Steps 4a/4f/4i and the path updates throughout). In `per-slice` mode, Step 4 runs the per-slice cycle (4a → 4b → 4c → 4c.5 → 4c.6 → optional PAUSE) once per `SLICE-XXX` row in the `## Slice Progress` table, then the end-of-feature cycle (4d → 4e → 4f → 4g → 4h → 4i → 4j) once after the last slice lands. Spec refs: MODULE-006.
- **REQ-013:** The per-slice review iteration cap is 3 with a progress-stall check (HIGH must strictly decrease across iterations; or MEDIUM when HIGH is zero). On halt, findings route to the ledger's `Open recommendations awaiting user decision` section. In `--skip-slice-checkpoints` mode, the entire flow halts. Mirrors the existing Step 3c panel-review cap pattern. Spec refs: MODULE-006.
- **REQ-014:** A slice retrospective may emit `## Recommended SPEC Amendments` (structured) and/or `## Recommended Re-planning` (structured, elevated severity). A `## Recommended Re-planning` recommendation halts the flow even under `--skip-slice-checkpoints` (mirrors the panel-review halt at Step 3c). Resume options: `/sdd-flow continue --replan` (re-runs Step 3 with the ledger and triggering retro in scope), `/sdd-flow continue --replan --from-slice SLICE-XXX` (resume from a user-specified slice; `--from-slice` value is validated per REQ-025 — must match `^SLICE-\d{3}$` AND reference an existing SLICE-XXX in the IMPLEMENTATION-PLAN's `## Slice Progress` table), or `/sdd-flow continue --override-replan` (continue with current plan despite the recommendation; documented but discouraged). Combination semantics and validation rules are pinned by REQ-025's flag conventions. **Three-tier model for retrospective recommendation surfacing (resolves L-P-iter1-deferred-12):** retrospectives can raise recommendations at three escalating tiers — (1) **Normal recommendation** = structured `## Recommended SPEC Amendments` entries (slice-bounded; user reviews at next slice-boundary pause OR at the consolidated 4j announcement under `--skip-slice-checkpoints`; no halt). (2) **Iteration-cap-exhaustion** = per-slice review-fix-rerun loop fails to reduce HIGH findings across the cap (REQ-013); halts the slice's iteration loop, routes findings to ledger's `Open recommendations awaiting user decision` section; in `--skip-slice-checkpoints` mode halts the whole flow. (3) **Re-planning recommendation** = `## Recommended Re-planning` (this REQ); halts the flow even under `--skip-slice-checkpoints` (mirrors Step 3c panel halt). The three tiers correspond to escalating severity of plan/spec invalidation: amendments are local; cap-exhaustion is slice-local but unresolved; re-planning is plan-level. Each tier has its own surfacing mechanism documented in REQ-013, this REQ-014, and the locked CLARIFICATION decision #2. Implementations SHOULD treat the three as distinct user-decision points; UI/CLI surfaces SHOULD label them by tier so users grasp the severity at a glance. Spec refs: MODULE-006, REQ-025.
- **REQ-015:** Subsequent slice subagents receive ONLY the rolling ledger in their prompts (per OQ-6 conservative default — strictly the ledger). Subagents that need an audit trail can read individual retros from disk on demand, but the prompt path is the ledger only. Spec refs: MODULE-006.
- **REQ-016:** Source-code path emissions for future runs use the new layout: `SDD/implementation/IMPLEMENTATION-PLAN-XXX-...md`, `SDD/implementation/summaries/IMPLEMENTATION-SUMMARY-XXX-...md`, `SDD/implementation/slices/RETROSPECTIVE-SLICE-XXX-...md`, `SDD/implementation/slices/LEARNINGS-FEATURE-[feature-name].md` (kebab-case feature-name slug per CLARIFICATION OQ-B; uniform across REQ-003, REQ-005, REQ-016, MODULE-007, EDGE-007, FAIL-003), `SDD/implementation/test-audits/TEST-AUDIT-XXX-...md`, `SDD/orchestration/progress.md`, `SDD/orchestration/subagent-calls/`, `SDD/orchestration/counters/`, `SDD/orchestration/compacted/`. Verification: `grep -n 'prompts/\|PROMPT-' agent-engineering/skills/sdd-flow/SKILL.md` MUST return zero hits post-edit; same for every modified `sdd/commands/*.md`. **Filename-placeholder consistency oracle (added per panel data-modeling MEDIUM):** `grep -n 'LEARNINGS-FEATURE-' <every modified command and skill file>` MUST yield the same placeholder shape (`LEARNINGS-FEATURE-[feature-name]` in templates, with concrete kebab-case slugs in concrete examples) across every hit; no `LEARNINGS-FEATURE-XXX` and no `LEARNINGS-FEATURE-[###]` references survive. Spec refs: MODULE-007.
- **REQ-017:** `sdd/hooks/log_subagent_call.py` line 18 updates `LOG_SUBDIR = Path("SDD") / "prompts" / "context-management" / "subagent-calls"` to `LOG_SUBDIR = Path("SDD") / "orchestration" / "subagent-calls"`. No other path-related code in the hook needs adjustment. The plugin manifest's `${CLAUDE_PLUGIN_ROOT}/hooks/log_subagent_call.py` reference is unchanged. Spec refs: MODULE-007.
- **REQ-018:** Version bumps: `sdd/.claude-plugin/plugin.json:4` and `.claude-plugin/marketplace.json:12` from `1.2.0` → `2.0.0`; `agent-engineering/.claude-plugin/plugin.json:4` and `.claude-plugin/marketplace.json:30` from `0.3.0` → `0.4.0`. Verification: `grep -n version` across all four files yields the four expected strings. Spec refs: MODULE-008.
- **REQ-019:** `sdd/README.md` is restructured into two clearly-distinct workflow sections per ADR 0001's distribution decision: a one-paragraph "Which mode is right for you?" decision aid at top; a Whole-feature workflow section (existing diagram + description, unchanged); a Per-slice workflow section (NEW — state-machine diagram, slice-command descriptions, opt-in instructions, `--skip-slice-checkpoints` doc, "requires SDD 2.0.0+" note); a Changelog/Migration section at bottom (breaking-change notice, `/sdd-migrate-layout` usage, in-flight refusal behavior, user-repo CLAUDE.md staleness reminder, **and the agent-engineering 0.4.0+ minimum cross-reference per REQ-026**). Verification commands: `grep -c "prompts/" sdd/README.md` returns 0; `grep -c "PROMPT-" sdd/README.md` returns 0; `grep -c "IMPLEMENTATION-PLAN" sdd/README.md` returns ≥2; `grep -c "implementation/" sdd/README.md` ≥4; `grep -c "orchestration/" sdd/README.md` ≥4; `grep -c "slices/" sdd/README.md` ≥2; `grep -c "agent-engineering" sdd/README.md` ≥1 (the version-coupling clause from REQ-026). Spec refs: MODULE-008, REQ-026.
- **REQ-020:** Glossary discipline maintained — `SDD/UBIQUITOUS_LANGUAGE.md` already has 36 entries covering all new terms (delivery model, slice mechanics, per-slice artifacts, workflow gates, filenames, frontmatter fields, modes & flags). Implementation must not introduce new terms without adding them to the glossary. **Timing of glossary updates (resolves L-CR-1):** glossary additions, if any are required during implementation, MUST be made in the same step (and the same git commit) as the source-code edit that introduces the new term — never deferred to a "documentation pass" step at the end of implementation. This mirrors the existing `/sdd:planning-complete` Step 5 wording: *"If the spec introduced or refined any domain terms beyond what was added to `SDD/UBIQUITOUS_LANGUAGE.md` during `/research-complete` (e.g., new module names that became canonical, action verbs adopted in REQ-XXX, state names introduced in EDGE-XXX), apply those deltas to the glossary now."* The implementation phase's equivalent gate is per-step, not per-phase: each command/skill edit that introduces or refines a term updates the glossary in the same commit. If the spec uses a term that contradicts an existing glossary entry, the contradiction is resolved explicitly in the same commit (update entry or rename in source — never let both stand). If a step introduces no new terms, the implementer notes "no glossary changes" in `progress.md` for that step. Spec refs: MODULE-008.
- **REQ-021:** `agent-engineering/README.md` Skills section updates the `sdd-flow` description to mention the new Step 4 state machine in per-slice mode and the integration with the SDD plugin's slice commands. Status section bumps to 0.4.0 with a one-line changelog AND the SDD 2.0.0+ minimum dependency clause per REQ-026. Repo-root `README.md` Available Plugins section gains a brief note about `delivery_mode: per-slice` opt-in for SDD and per-slice support for sdd-flow, plus the version-coupling note per REQ-026. `plugin-installation-scope.md` is unchanged (verified out-of-scope by research). Spec refs: MODULE-008, REQ-026.
- **REQ-022:** The `## Slice Progress` table in IMPLEMENTATION-PLAN documents (per-slice mode only) follows the binding column schema and four-state enum from research §"## Slice Progress table schema": columns `SLICE-ID | Name | Status | Acceptance check | Test result | Notes`; states `Not Started`, `In Progress`, `Acceptance Check Passing`, `Complete`; transitions per research (no backwards transitions; "stuck" status lives in the ledger, not the column). `/implementation-start` scaffolds the table; `/slice-retro` updates `Status`, `Test result`, and `Notes` columns only (never SLICE-ID, Name, or Acceptance check). **SLICE-XXX uniqueness invariant:** SLICE-XXX values within a single IMPLEMENTATION-PLAN's `## Slice Progress` table MUST be unique. Duplicate detection is the spec author's responsibility; tooling does not enforce. The `/slice-start SLICE-001` "first `Not Started` row" rule would silently pick one of duplicates, so duplicates are a correctness hazard the human reviewer catches. Spec refs: MODULE-006, MODULE-007.
- **REQ-023:** `sdd-flow` Phase Detection (SKILL.md lines 636–645) gains rules for resuming from `## Awaiting Slicing Decision` (with `--fall-back-to-whole-feature` or `--retry-slicing "<hint>"`) and from `## Recommended Re-planning` (with `--replan` and optional `--from-slice SLICE-XXX`, or `--override-replan`). Phase Detection also implements legacy-path fallback: check the new path first; if absent, check the legacy path; if found at the legacy path, surface a one-time message recommending `/sdd-migrate-layout`. Spec refs: MODULE-006.
- **REQ-024:** Slice-ID arguments to all `/slice-*` commands MUST be validated against the regex `^SLICE-\d{3}$` before being interpolated into any path. This prevents directory-traversal in read paths (a malicious arg like `../../etc/passwd` would bypass the path templates otherwise). Spec refs: MODULE-002.
- **REQ-025:** **Slice-command flag conventions.** This feature introduces six new flags across the slice commands and the `/sdd-flow continue` extensions. This REQ inventories every flag, its grounding (proposal §6 vs. spec-introduced via iteration-1 fix), its semantics, its default behavior, and its supervised-vs-autonomous handling. The convention is binding for downstream commands.

  **Flag inventory:**

  | Flag | Command(s) | Grounding | Semantics | Default (without flag) | Supervised mode | Autonomous mode |
  |------|-----------|-----------|-----------|------------------------|-----------------|-----------------|
  | `--resume` | `/slice-start` | Spec-introduced (EDGE-012, iter-1 fix) | Re-attach to an `In Progress` slice if context was lost — does NOT regress state, does NOT switch active slice. | Without `--resume`, invoking `/slice-start SLICE-X` while another slice is `In Progress` refuses per EDGE-012. | User runs `/slice-start --resume SLICE-X` explicitly. | Orchestrator emits flag in resume invocations after a context loss; same semantics. |
  | `--force` | `/slice-start` | Spec-introduced (EDGE-013, iter-1 fix). NEW project convention — no other SDD command currently uses `--force`. | Destructive override for re-starting a `Complete` slice: resets `Status`/`Test result`/`Notes` columns; pre-existing RETROSPECTIVE-SLICE file and ledger entries are NOT deleted; ledger note records the re-start with timestamp. | Without `--force`, the command refuses (default = REFUSE per EDGE-013). | User passes `--force` OR confirms an interactive `y/n` prompt affirmatively (the prompt is `--force`-equivalent). | Absence of `--force` is treated as a refusal-with-halt: the orchestrator emits an `## Awaiting Re-start Decision` block to `progress.md` per the REQ-011 halt-shape pattern (mirrors `## Awaiting Clarification` / `## Awaiting Slicing Decision`). Interactive confirmation is supervised-mode-only. |
  | `--reconcile-ledger` | `/slice-retro` | Research §Q-E (descriptive prose); spec-introduced as a literal CLI flag in iter-1 fix (REQ-005, EDGE-007, EDGE-014, FAIL-003). The `--reconcile-` prefix is the convention for "reconstruct derived state from authoritative sources" (the retros are authoritative; the ledger is derived). Future flags following the same pattern (`--reconcile-progress`, `--reconcile-counters`) inherit this convention. | Re-reads every `RETROSPECTIVE-SLICE-XXX-...md` for the active feature; rebuilds `LEARNINGS-FEATURE-[feature-name].md` per the algorithm in REQ-005a below. | Without the flag, `/slice-retro` writes a new retro + updates ledger (or refuses per REQ-005 if a retro already exists). | User runs `/slice-retro SLICE-X --reconcile-ledger` explicitly; output is a diff between pre- and post-reconcile ledger; user confirms before write. | Orchestrator emits the flag only when triggered by an explicit recovery directive; same algorithm; the diff-confirm step degrades to "write without prompt" in autonomous mode but the change is logged to `progress.md`. |
  | `--replan` | `/sdd-flow continue` | **Proposal §6** (line 196) authoritatively defines this flag. | Re-runs Step 3 (planning) with the rolling ledger and the triggering retrospective in the planning subagent's prompt; produces a revised SPEC; resumes implementation from `SLICE-001` (or from a user-specified slice if `--from-slice` is also present). | Without `--replan`, `/sdd-flow continue` proceeds along the existing flow. | User runs the flag explicitly. | Orchestrator emits flag when a retro raises `## Recommended Re-planning` (REQ-014). |
  | `--from-slice SLICE-XXX` | `/sdd-flow continue` (only meaningful in combination with `--replan`) | **Proposal §6** (line 196 prose) — mentioned as "or from a user-specified slice if some completed slices remain valid." | Resume implementation from the named slice after the re-plan completes. The user owns the judgment of which slices remain valid; the orchestrator only validates existence. | Without the flag, re-plan resumes from `SLICE-001`. | User runs `/sdd-flow continue --replan --from-slice SLICE-003` explicitly. | Orchestrator emits flag with the user-supplied slice ID after halt-and-resume. **Validation:** `--from-slice` value MUST match `^SLICE-\d{3}$` AND MUST reference an existing SLICE-XXX in the IMPLEMENTATION-PLAN's `## Slice Progress` table. Invalid value (regex mismatch or unknown slice) refuses with the REQ-007 message-discipline shape: name the offending value, name the existing slice IDs (or "none"), name the resolution path. Resolves L-CR-7 / R-3. |
  | `--override-replan` | `/sdd-flow continue` | **Proposal §6** (line 198) authoritatively defines this flag. | Continues with the current plan despite a `## Recommended Re-planning` recommendation in a slice retrospective. Documented but discouraged. | Without the flag, a `## Recommended Re-planning` halts the flow per REQ-014 (even under `--skip-slice-checkpoints`). | User runs the flag explicitly after reading the recommendation. | Orchestrator does NOT silently emit `--override-replan`; in autonomous mode the halt fires per REQ-014. |

  **Flag combination semantics for `/sdd-flow continue` (resolves panel deferred LOW-11):**

  - `--replan` alone — re-runs Step 3 with retro context, resumes from SLICE-001.
  - `--replan --from-slice SLICE-XXX` — re-runs Step 3, resumes from `SLICE-XXX` after re-plan.
  - `--override-replan` alone — continues without re-plan.
  - `--from-slice SLICE-XXX` without `--replan` — INVALID. Refuses with: `--from-slice requires --replan; running --replan --from-slice <id> is the documented combination.`
  - `--replan --override-replan` — INVALID (mutually exclusive intents). Refuses with: `--replan and --override-replan are mutually exclusive; pick one.`
  - `--from-slice --override-replan` — INVALID (transitively, since `--from-slice` requires `--replan` and `--replan` is excluded). Refuses with the `--from-slice requires --replan` message.

  **Convention rationale:**

  - The proposal authoritatively defines `--replan`, `--from-slice` (in passing prose), and `--override-replan` (proposal §6). These three are the proposal's API; the spec carries them through unchanged.
  - The iteration-1 fix subagent introduced `--resume`, `--force`, and `--reconcile-ledger` (the latter elevated from research §Q-E descriptive prose to a literal CLI flag) to address the EDGE-012 / EDGE-013 / EDGE-014 re-invocation cases. These three are spec-introduced and SHOULD be back-cited in the future research note about the implementation (the research is binding for the run that produced it; the spec extends it for fix-time discoveries).
  - `--force` adopts the destructive-action override convention going forward. No other SDD command currently uses `--force`; this REQ establishes the convention with rationale: "destructive-with-confirmation flag, mirrors common Unix tooling convention (e.g., `git push --force`, `rm --force`); semantics: 'I understand this is destructive; proceed without the default refusal.'" Future destructive overrides in the SDD plugin SHOULD use `--force` rather than ad-hoc names.
  - Every `--<flag>` is a literal CLI argument; absence is the default behavior; supervised-mode interactive prompts are flag-equivalent decisions; autonomous mode without the flag halts via the documented awaiting-decision-block pattern (REQ-011 halt shape). This is the binding pattern for every flag introduced by this feature and any flag added by downstream features.

  Spec refs: MODULE-002, MODULE-006.

- **REQ-025a:** **`--reconcile-ledger` algorithm (resolves L-CR-4).** The reconcile mode for `/slice-retro --reconcile-ledger` follows this strict sequence:

  1. Read all `RETROSPECTIVE-SLICE-*-[feature-name]-*.md` files for the active feature from `SDD/implementation/slices/`.
  2. Read the current `SDD/implementation/slices/LEARNINGS-FEATURE-[feature-name].md` ledger.
  3. For each retrospective, check whether its key learnings (the structured `## Recommended SPEC Amendments`, `## Recommended Re-planning`, and ledger-update sections) appear in the ledger's structured sections (Interface contract clarifications / Integration patterns discovered / Performance / failure modes observed / Open recommendations awaiting user decision).
  4. If a retrospective's learnings are missing from the ledger, append them to the appropriate ledger sections — consolidating with existing entries on the same topic, not blind-appending.
  5. **Manual-edit-only entries that have no retro source are PRESERVED** — the ledger is not destroyed. Such entries are flagged in the rebuild output as `> orphan entry — no source retro on disk` so the user can decide whether to keep, edit, or remove them.
  6. Mark the ledger header with a `<!-- reconciled at YYYY-MM-DD -->` HTML comment timestamp.
  7. **Output:** a diff between pre- and post-reconcile ledger; in supervised mode, user confirms before write. In autonomous mode, write proceeds without prompt and the change is logged to `progress.md` with the reconcile diff captured under a `## Reconcile Ledger Action` block.
  8. **Scope:** all retros for the active feature, NOT just the named slice. The named SLICE-XXX argument scopes only the existence-check at REQ-005's re-invocation refusal (so users can target the reconcile to a specific slice's retro for diagnostic purposes); the rebuild uses the full retro corpus.

  Audit-trail invariant: retros remain authoritative; the ledger is derived. The reconcile algorithm respects this by treating retros as immutable inputs and the ledger as the rebuilt output. Spec refs: MODULE-002.

- **REQ-026:** **Cross-plugin version coupling — README cross-references.** The SDD plugin and `agent-engineering` plugin install independently from the marketplace; per `/plugin install <plugin>`, the user can update one without the other. SDD 2.0.0 + agent-engineering 0.3.x is a plausible install state. To prevent silent misbehavior:
  - `agent-engineering/README.md` (per REQ-021) MUST call out, in the version 0.4.0 release notes section, the explicit dependency on SDD 2.0.0+. Suggested wording: *"sdd-flow 0.4.0 requires SDD plugin 2.0.0 or later (the per-slice Step 4 state machine and the new directory layout). Install or update SDD via `/plugin install https://github.com/poliva83/claude-plugins sdd` before running `/sdd-flow` with `delivery_mode: per-slice` specs or against repos migrated by `/sdd-migrate-layout`."*
  - `sdd/README.md` (per REQ-019's changelog/migration section) MUST call out the agent-engineering 0.4.0+ minimum. Suggested wording: *"SDD 2.0.0 introduces per-slice mode and a new artifact directory layout. If you use `/sdd-flow` for orchestration, also install or update agent-engineering to 0.4.0+ via `/plugin install https://github.com/poliva83/claude-plugins agent-engineering` — the older 0.3.x sdd-flow skill embeds SDD 1.x command bodies and legacy paths and will misbehave silently against SDD 2.0.0 artifacts."*
  - The repo-root `README.md` Available Plugins note (per REQ-021) SHOULD mention the version coupling for users browsing the marketplace.

  Detection at runtime is hard from the skill side (the older skill cannot easily introspect SDD plugin version); the README cross-references and FAIL-009 documentation are the primary mitigation. A best-effort version-check stub in agent-engineering 0.4.0+ skill loader is described in FAIL-009 as a stretch goal, NOT required by this REQ.

  Spec refs: MODULE-008, FAIL-009, RISK-007.

### Non-Functional Requirements

- **SEC-001:** `/slice-commit` and `/sdd-migrate-layout` MUST NOT bypass git hooks. Plain `git commit` (no `--no-verify`); plain `git mv` (no force flags). Recovery path on hook failure: fix the issue, re-stage, re-run the command. Documented in each command's body.
- **SEC-002:** `/sdd-migrate-layout`'s active-flow refusal is the load-bearing safety check against data-loss during in-flight relocation. Detection: parse `progress.md` for the latest `## Phase: <name> - <status>` block; refuse if status != `COMPLETE`. Examples of "active": `## Research|Planning|Implementation Phase - In Progress`, `## Awaiting Clarification`, `## Awaiting Slicing Decision`, `## PARTIAL: needs continuation`. **Fail-closed posture on parse failure (per panel security MEDIUM):** if `progress.md` is missing AND `SDD/prompts/` (legacy) or `SDD/orchestration/` (new) contains other artifacts, OR if `progress.md` exists but the latest `## Phase:` block cannot be parsed (corrupt schema, truncated content, unexpected format), the command MUST refuse with the message: `Could not determine flow status; refusing migration. Inspect progress.md manually before re-running.` Defense-in-depth: when the safety-check input is unparseable, refusal is the safe default (the cost of a false-refusal is one inspect-and-rerun; the cost of a false-proceed is silent data-loss-by-misclassification). The fail-closed rule covers absent-progress.md only when other SDD content exists — a truly empty/uninitialized tree (no `SDD/prompts/`, no `SDD/orchestration/`, no `progress.md`) yields the existing "nothing to migrate" idempotent-exit per REQ-008, not a refusal.
- **SEC-003:** Slice-ID inputs validated per REQ-024 to prevent path traversal in read or write paths.
- **SEC-004:** No new credentials, secrets, or PII surfaces are introduced by per-slice artifacts. RETROSPECTIVE-SLICE, LEARNINGS-FEATURE, REVIEW-SLICE are all markdown documents under `SDD/`. Same threat model as existing SDD artifacts. Note: `sdd/hooks/log_subagent_call.py` continues to capture full subagent transcripts under the relocated `SDD/orchestration/subagent-calls/` path; field-level redaction for transcript logs remains unscoped (inherited posture from pre-2.0.0 plugin, NOT introduced by this feature). If transcript-redaction becomes a requirement later, it is tracked separately and is orthogonal to the directory restructure.
- **UX-001:** `/slice-*` commands' inert message names the field (`delivery_mode`), the required value (`per-slice`), and what to run instead (`/implementation-start`). Friendly, non-cryptic, self-documenting per ADR 0001's "discoverable mode boundary" principle.

## Edge Cases (Research-Backed)

- **EDGE-001: `/sdd-migrate-layout` re-run when already migrated**
  - Research reference: research §Branch 4 "Idempotence".
  - Current behavior: command does not exist.
  - Desired behavior: detect that `SDD/prompts/` does not exist (or is empty) and `SDD/orchestration/` is populated; exit cleanly with "Nothing to migrate. Tree is already at the new layout." or "Already migrated.". Zero changes.
  - Test approach: synthetic-tree manual test. Construct a tree at the new layout; run the command; confirm zero diff and the friendly message.

- **EDGE-002: `/slice-*` invoked when active SPEC has `delivery_mode: whole-feature` or no field**
  - Research reference: research §Branch 3 "Inert-mode behavior".
  - Current behavior: commands do not exist.
  - Desired behavior: emit the inert-mode message (REQ-007 wording) and exit cleanly. No partial state writes.
  - Test approach: read the command file; confirm the first step reads `delivery_mode:` and short-circuits with the message text.

- **EDGE-003: `/slice-review` invoked when target slice has no implementation yet**
  - Research reference: research §Branch 3 "/slice-review".
  - Current behavior: command does not exist.
  - Desired behavior: detect that the slice's `In Progress`/`Acceptance Check Passing` row in `## Slice Progress` has no committed file changes since the row transitioned to `In Progress`. Fail with: "No implementation found for SLICE-XXX. Run `/slice-start SLICE-XXX` and implement the slice before review."
  - Test approach: synthetic-tree manual test with a SLICE-001 row at `In Progress` and an empty diff; confirm the message fires.

- **EDGE-004: User repos with CLAUDE.md hardcoding old paths**
  - Research reference: research §Branch 6 "User-repo CLAUDE.md collateral".
  - Current behavior: existing CLAUDE.md files reference `SDD/prompts/...`.
  - Desired behavior: `/sdd-migrate-layout` does NOT auto-edit user-authored CLAUDE.md or AGENTS.md. The migration helper's output prints a reminder paragraph telling users to grep their own CLAUDE.md/AGENTS.md for `SDD/prompts/` and `PROMPT-` and update accordingly. The same reminder is in `sdd/README.md`'s migration section.
  - Test approach: read the command's output template; confirm the reminder is present.

- **EDGE-005: Practicality gate fires when only one MODULE-XXX exists OR every honest decomposition is "build all of it then test it"**
  - Research reference: research §"Practicality-gate detection logic" (binding).
  - Current behavior: gate does not exist.
  - Desired behavior: planning subagent runs the four boolean heuristics (single-module touch-set, no-thinner-happy-path, universal-slice REQ touch, single concentrated function); if ANY returns true, populates `## Delivery Slices` with `Slicing not applicable: <reason citing the heuristic>` and emits `## Awaiting Slicing Decision` to `progress.md`. The qualitative judgment-call escape applies if all four boolean heuristics return false but the subagent still believes slicing is impractical.
  - Test approach: read the planning-start.md Step 6 extension; confirm all four heuristics are enumerated; confirm the `## Awaiting Slicing Decision` block shape matches `## Awaiting Clarification`.

- **EDGE-006: Re-planning recommendation fired but user runs `/sdd-flow continue` (no flag)**
  - Research reference: research §Branch 2 "Re-planning trigger".
  - Current behavior: no re-planning trigger exists.
  - Desired behavior: Phase Detection sees `## Recommended Re-planning` in the latest retrospective and re-prompts the user with the explicit option set: `--replan` (with optional `--from-slice`), manual SPEC edit + `/sdd-flow continue`, or `--override-replan`. The bare `continue` does not silently choose any of these.
  - Test approach: read SKILL.md Phase Detection; confirm the explicit-option-required behavior.

- **EDGE-007: Slice retrospective subagent successfully writes RETROSPECTIVE artifact but ledger update fails**
  - Research reference: research §Q-E resolution.
  - Current behavior: scenario does not exist.
  - Desired behavior: per the FIRST-WRITE-WINS ordering, the retro artifact existing without the ledger update is recoverable. The next `/slice-retro` invocation (or `/slice-retro --reconcile-ledger`) detects "ledger missing entries from existing retros" and reconciles by rebuilding the ledger from the retros on disk.
  - Test approach: read the `/slice-retro` command body; confirm the recovery logic and `--reconcile-ledger` mode are documented.

- **EDGE-008: macOS APFS case-insensitive filesystem (this-repo deviation)**
  - Research reference: research §"This-repo deviation" (proposal §Recursion-trap).
  - Current behavior: this run hit the case-collision when `SDD/` collided with `sdd/`. Resolved mid-flow by relocating to `flow-state/SDD/...`.
  - Desired behavior: `sdd/README.md` includes a section warning users that on case-insensitive filesystems (macOS APFS, certain Windows configurations) the `SDD/` directory may collide with a co-located `sdd/` plugin source directory. Recommend they install the plugin outside their working tree, or use a working tree on a case-sensitive volume.
  - Test approach: grep `sdd/README.md` for the case-insensitive guidance.

- **EDGE-009: Spec without `delivery_mode:` field (existing pre-Step-A specs)**
  - Research reference: research §Open Question 3 conservative default.
  - Current behavior: pre-Step-A specs lack the field.
  - Desired behavior: every command's mode-read step treats absent field as `whole-feature` (the documented default). No log line is emitted (per OQ-3 default — stay silent).
  - Test approach: synthetic-tree manual test with a spec lacking the field; confirm whole-feature behavior fires.

- **EDGE-010: Multiple `Not Started` slices in `## Slice Progress` when `/slice-start` is invoked without arg**
  - Research reference: research §Branch 3 "/slice-start active-slice resolution".
  - Current behavior: command does not exist.
  - Desired behavior: command prompts the user to choose, listing all `Not Started` rows with their SLICE-IDs and Names. Does NOT silently pick the first.
  - Test approach: read the command body; confirm the prompt logic is documented.

- **EDGE-011: `## Slice Progress` table column-write authority**
  - Research reference: research §"## Slice Progress table schema".
  - Current behavior: table does not exist.
  - Desired behavior: `/slice-retro` updates ONLY `Status`, `Test result`, and `Notes` columns. SLICE-ID, Name, and Acceptance check are SPEC-derived and never modified by retro. State transitions are forward-only (no backwards transitions encoded in the column; "stuck" surfaces via the ledger's `Open recommendations` section, not the column).
  - Test approach: read the `/slice-retro` body; confirm the column-write restriction.

- **EDGE-012: `/slice-start` re-invocation while another slice is `In Progress`**
  - Research reference: panel api-contract MEDIUM (this iteration); REQ-022 forward-only invariant.
  - Current behavior: command does not exist.
  - Desired behavior: when `/slice-start SLICE-002` is invoked while SLICE-001 is at `In Progress` (or `Acceptance Check Passing` — i.e., not yet `Complete`), the command refuses with a friendly message naming the in-progress slice: `Cannot start SLICE-002: SLICE-001 is currently <state>. Resume the in-progress slice first (see /slice-review, /slice-retro, /slice-commit), or mark it abandoned by manually editing the Slice Progress row to a terminal state. Use /slice-start --resume SLICE-001 to re-attach to the in-progress slice if context was lost.` The command does NOT regress the in-progress slice's state, does NOT silently switch active slice, and does NOT overwrite either row's transition timestamp. The forward-only invariant in REQ-022 holds at the command boundary.
  - Test approach: read `/slice-start` command body; confirm the conflict-detection step and the explicit `--resume` path are documented.

- **EDGE-013: `/slice-start` re-invocation on a slice already `Complete`**
  - Research reference: panel api-contract MEDIUM (this iteration).
  - Current behavior: command does not exist.
  - Desired behavior: when `/slice-start SLICE-001` is invoked and SLICE-001 is already `Complete`, the command warns the user and asks for explicit confirmation before re-starting (re-start would overwrite acceptance-check evidence on the row and create ambiguity in the ledger). Default response is REFUSE; explicit `--force` (or affirmative interactive confirmation in supervised mode) is required to proceed. The pre-existing RETROSPECTIVE-SLICE-001 file is NOT deleted; the ledger entries are NOT erased; only the `Status`/`Test result`/`Notes` columns are reset (and a ledger note records the re-start with timestamp). **Autonomous-vs-supervised semantics (resolves panel iter-2 LOW-2):** in supervised mode, the user can be prompted interactively and an affirmative response is `--force`-equivalent. In autonomous mode there is no user to prompt; the absence of `--force` is treated as a refusal-with-halt — the orchestrator emits an `## Awaiting Re-start Decision` block to `progress.md` per the REQ-011 halt-shape pattern (mirrors `## Awaiting Clarification` / `## Awaiting Slicing Decision`). The user resumes by re-invoking with `/slice-start SLICE-001 --force` (or by manually editing the slice row to a non-`Complete` state, with the understanding that doing so leaves a `git log` paper trail). Interactive confirmation is supervised-mode-only; `--force` is the universal flag-equivalent. Per REQ-025 flag conventions, this is the binding pattern.
  - Test approach: read `/slice-start` command body; confirm the already-complete branch and `--force` requirement are documented.

- **EDGE-014: `/slice-retro` re-invocation when retrospective already exists**
  - Research reference: panel api-contract MEDIUM (this iteration); REQ-005 re-invocation policy.
  - Current behavior: command does not exist.
  - Desired behavior: `/slice-retro SLICE-001` detects an existing `RETROSPECTIVE-SLICE-001-...md` at the canonical slice path and refuses loudly per REQ-005's re-invocation policy. The user's documented escape hatches are: (a) `/slice-retro SLICE-001 --reconcile-ledger` (refresh the ledger from the existing retro per EDGE-007 / FAIL-003), or (b) manually delete the existing retro before re-running (deliberate, leaves a paper trail in `git log`). The default-write-second-retro path (option (b) from the panel) is REJECTED by this spec — the audit-trail invariant outweighs the convenience of dated re-writes.
  - Test approach: read `/slice-retro` command body; confirm the existence check, refusal message, and `--reconcile-ledger` path are documented.

- **EDGE-015: `/sdd-migrate-layout` invoked when `progress.md` cannot be parsed**
  - Research reference: panel security MEDIUM (this iteration); SEC-002 fail-closed posture.
  - Current behavior: command does not exist.
  - Desired behavior: when the active-flow-detection step cannot parse `progress.md` (file present but corrupt, schema violated, latest `## Phase:` block missing or truncated), the command refuses per SEC-002 with the diagnostic message: `Could not determine flow status; refusing migration. Inspect progress.md manually before re-running.` Refusal is fail-closed: the helper does NOT default to "no active phase" and does NOT proceed with `git mv` operations on the unparseable input. A truly empty / uninitialized SDD tree (no `progress.md`, no `SDD/prompts/`, no `SDD/orchestration/`) is exempt from this rule and routes to the "nothing to migrate" idempotent-exit per REQ-008.
  - Test approach: synthetic-tree manual test with a malformed `progress.md` (e.g., truncated mid-block, missing `## Phase:` header). Run the command; confirm the diagnostic-message refusal fires.

## Failure Scenarios

- **FAIL-001: `/sdd-migrate-layout` partially completes then errors mid-move**
  - Trigger condition: process killed, disk full, permission error mid-move.
  - Expected behavior: leave intermediate state visible (operations are `git mv`, so `git status` shows pending renames).
  - User communication: command output documents recovery: `git reset HEAD` to unstage, `git checkout -- .` to undo, OR pasting the reverse-move commands the command's output produced.
  - Recovery approach: the active-flow refusal eliminates the most common case (mid-flow data loss). The mid-migration crash case is rare; manual rollback is the documented procedure. The migration helper does NOT itself implement automatic rollback (over-engineering for a one-shot helper).

- **FAIL-002: User installs SDD 2.0.0 with active in-flight flow under old layout**
  - Trigger condition: user upgrades plugin while a research/planning/implementation phase is mid-execution.
  - Expected behavior: `/sdd-flow continue` Phase Detection checks the new path first AND falls back to the legacy path. If legacy is found and active, `/sdd-flow continue` resumes from the legacy path AND surfaces a one-time message: *"Detected active flow at legacy path `SDD/prompts/`. Run `/sdd-migrate-layout` after the current phase completes to migrate to the new layout."*
  - User communication: the one-time message above; on phase complete, a follow-up reminder.
  - Recovery approach: complete or abandon the in-flight flow; then run `/sdd-migrate-layout` (which will refuse if the flow is still active). No state is lost; resumption from the legacy path is exact.

- **FAIL-003: Slice retrospective writes RETROSPECTIVE artifact, then disk fills before ledger update**
  - Trigger condition: out-of-disk error between the two writes of `/slice-retro`.
  - Expected behavior: retro on disk; ledger out of date.
  - User communication: next `/slice-retro` invocation (or `/slice-retro --reconcile-ledger`) detects the inconsistency and rebuilds the ledger from the retros.
  - Recovery approach: per Q-E resolution, the FIRST-WRITE-WINS ordering eliminates the unrecoverable inverse case. Reconcile mode is the documented recovery path.

- **FAIL-004: Per-slice review iteration cap (3) exhausted with HIGH count not strictly decreasing**
  - Trigger condition: review-fix-rerun loop fails to reduce HIGH findings across 3 iterations.
  - Expected behavior: halt the slice's iteration loop. Append findings to the ledger's `Open recommendations awaiting user decision` section. In supervised mode, surface to user at the next slice-boundary pause. In autonomous + slice-checkpoints `on`, surface at the slice-boundary pause. In `--skip-slice-checkpoints` mode, halt the whole flow (mirrors the panel-review halt at Step 3c).
  - User communication: ledger entry + (under `--skip-slice-checkpoints`) flow halt message naming the slice and the unresolved finding count.
  - Recovery approach: user reviews findings, decides whether to (a) accept and proceed (manually unblock), (b) revise the slice's implementation, or (c) trigger re-planning if the cap exhaustion reflects a deeper plan issue.

- **FAIL-005: `/sdd-migrate-layout` invoked on Windows in cmd.exe or PowerShell**
  - Trigger condition: user on Windows runs the command outside Git Bash.
  - Expected behavior: the command's first step is `command -v bash >/dev/null 2>&1 || { echo "ERROR: /sdd-migrate-layout requires bash. On Windows, run from Git Bash."; exit 1; }`. Refuses cleanly without partial moves.
  - User communication: the explicit refusal message naming Git Bash as the workaround.
  - Recovery approach: re-run from Git Bash. The `git mv` operations are unchanged regardless of which bash-compatible shell hosts them.

- **FAIL-006: Hook path constant updated but migration not yet run (or vice versa)**
  - Trigger condition: version skew between hook update and migration helper execution.
  - Expected behavior: research §"Hook integrity" mitigation — both ship in the same release. The migration helper documents the hook path change in its own output. The `mkdir(parents=True, exist_ok=True)` in the hook means it just creates whatever path it's told; logs simply land at the path matching the installed hook.
  - User communication: migration helper output names the hook path change explicitly.
  - Recovery approach: split-log scenario is recoverable manually (move stale logs from one tree to the other); not a data-loss case.

- **FAIL-007: `/slice-start` invoked but the IMPLEMENTATION-PLAN's `## Slice Progress` table is missing**
  - Trigger condition: per-slice spec authored but `/implementation-start` not yet run, or the IMPLEMENTATION-PLAN was edited and the `## Slice Progress` block was accidentally deleted.
  - Expected behavior: command halts with the message: `No '## Slice Progress' table found in <IMPLEMENTATION-PLAN-XXX-...md>. Either run /implementation-start to scaffold the table, or restore the table from a previous git commit. /slice-start cannot proceed without the table.` No partial state writes; no fall-through to "first Not Started row" search on missing data.
  - User communication: the diagnostic message above naming the expected file path.
  - Recovery approach: re-run `/implementation-start` in `delivery_mode: per-slice` mode (which scaffolds the table per REQ-002), or `git checkout` the IMPLEMENTATION-PLAN from a commit where the table was present.

- **FAIL-008: `/sdd-migrate-layout` parse-failure during the active-flow refusal check**
  - Trigger condition: `progress.md` is present but its content cannot be parsed for the latest `## Phase: <name> - <status>` block (corruption, schema violation, partially-written file from a crashed prior run).
  - Expected behavior: per SEC-002 fail-closed posture, the command refuses with `Could not determine flow status; refusing migration. Inspect progress.md manually before re-running.` No `git mv` operations are attempted; no rollback is needed because no state was changed.
  - User communication: the diagnostic message above. The user manually inspects `progress.md` and either repairs it (so the next run can detect status correctly) or, in the truly hopeless case, archives it under a `.bak` name and reconstructs phase state from `git log` before re-running.
  - Recovery approach: rollback is irrelevant — the helper's safe state is "did nothing". User remediation is manual `progress.md` repair followed by re-running. Documented in the migration helper's command body.

- **FAIL-009: Cross-plugin version mismatch — SDD 2.x with agent-engineering 0.3.x (resolves M-A2)**
  - Trigger condition: user installs SDD plugin 2.0.0+ but does not update the agent-engineering plugin from 0.3.x. The user then runs `/sdd-flow` from agent-engineering 0.3.x against a repo where SDD 2.0.0 has been installed (or vice-versa: user updates agent-engineering to 0.4.0 but is still on SDD 1.2.0).
  - Expected behavior: the older agent-engineering 0.3.x sdd-flow skill embeds outdated SDD 1.x command bodies and references legacy paths (`SDD/prompts/...`, `PROMPT-XXX-...`). When run against a repo migrated to the SDD 2.0.0 layout, the skill writes orchestration artifacts at LEGACY paths while SDD 2.0.0 commands write at NEW paths — producing a split tree with `SDD/prompts/progress.md` (skill writes) and `SDD/implementation/IMPLEMENTATION-PLAN-XXX-...` (SDD command writes) coexisting. Worse: the 0.3.x skill silently accepts `delivery_mode: per-slice` in spec frontmatter without honoring it (no Step 4 state machine; flows as `whole-feature`). The reverse case (agent-engineering 0.4.0 + SDD 1.2.0) emits NEW paths that no 1.2.0 SDD command knows about.
  - Detection: hard to detect at runtime from the skill side (the older 0.3.x skill cannot easily introspect SDD plugin version). Primary mitigation is documentation-time (per REQ-026): both plugins' READMEs cross-reference the version-coupling. Secondary mitigation (stretch goal, NOT required by REQ-026): agent-engineering 0.4.0+ skill loader emits a one-time best-effort warning when it detects SDD 2.x artifact patterns (e.g., `SDD/implementation/IMPLEMENTATION-PLAN-` filename pattern) but its own embedded command bodies still reference legacy paths — surfacing: *"Detected SDD 2.0.0 artifacts; verify agent-engineering is at 0.4.0+ via `/plugin install agent-engineering`."*
  - User communication: the README cross-references at REQ-026 and the marketplace.json release notes. If a stretch-goal warning is implemented in the 0.4.0 skill loader, it surfaces at first invocation. If not, the user discovers the mismatch via split-tree symptoms (artifacts in two places) and consults the changelog.
  - Recovery approach: user upgrades the lagging plugin to its 2.0.0 / 0.4.0 minimum via `/plugin install` from the marketplace. Any artifacts written under the wrong layout during the mismatch window are recoverable manually (`git mv` from legacy path to new path, or vice-versa). No data loss; the mismatch produces orphan artifacts but never destroys content. Post-recovery, `/sdd-migrate-layout` reconciles the tree if needed.

## Implementation Constraints

### Context Requirements

- **Maximum context utilization:** <40% during implementation per SDD plugin convention.
- **Essential files for implementation:**
  - `agent-engineering/skills/sdd-flow/SKILL.md` — major-edit target (Branch 2). Read in full once; subsequent edits target specific line ranges.
  - `sdd/commands/planning-start.md` — locked region MUST be respected; read-only outside lines 64–204 + 375–379 except the allowed regions (line 271 prose, Step 6 starting line 305).
  - `sdd/commands/implementation-start.md`, `sdd/commands/critical-review.md`, `sdd/commands/spec-review-panel.md` — moderate edits with mode-aware branching insertions.
  - `sdd/commands/code-review.md`, `sdd/commands/implementation-complete.md`, `sdd/commands/implementation-test.md` — path updates + rename throughout.
  - `flow-state/SDD/research/RESEARCH-001-vertical-slicing-step-c.md` — authoritative for every `file:line` reference and the practicality-gate heuristics + `## Slice Progress` table schema.
  - `flow-state/SDD/UBIQUITOUS_LANGUAGE.md` — the canonical glossary; vocabulary discipline.
  - `flow-state/SDD/adr/0001-...md` and `flow-state/SDD/adr/0002-...md` — captured cross-cutting decisions.
- **Files that can be delegated to subagents:**
  - The path-only-update commands (`{research-start, research-complete, research-compact, planning-complete, continue, adhoc-compact, planning-compact, implementation-compact}.md`) can be delegated to a single Explore subagent with a "replace pattern X with Y across these files" task.
  - The new command files (`slice-start.md`, `slice-review.md`, `slice-retro.md`, `slice-commit.md`, `sdd-migrate-layout.md`) are best authored in the main context for cross-reference consistency but each is small and self-contained — they can be delegated in parallel if context pressure mounts.

### Technical Constraints

- **Markdown is the program** (CLAUDE.md guidance) — most work is editing markdown files. The single Python file (`sdd/hooks/log_subagent_call.py`) is a one-line constant change.
- **Plugin manifests must stay in sync** (CLAUDE.md guidance: "They drift easily — check both."): four version strings across two manifests must update in the same commit.
- **Hooks: Python 3.9+** — no version constraint changes; the hook continues to use `dict[str, Any]`.
- **Step A locked region** (`sdd/commands/planning-start.md` lines 64–204 + 375–379) is OFF-LIMITS. Every edit to `planning-start.md` MUST cite the exact line range and confirm it is outside those ranges.
- **Recursion-trap discipline** — this run's own artifacts remain at LEGACY paths under `flow-state/SDD/prompts/context-management/...`. Source-code edits emit the NEW paths for future runs. Do not relocate this run's live artifacts.
- **Cross-platform shell** — `/sdd-migrate-layout` uses bash 3.0+ syntax (parameter expansion `${f//OLD/NEW}`); the command MUST detect bash and refuse with explicit guidance otherwise.
- **No tests; verification is manual** — the repo has no automated test infrastructure for plugin commands. "Verified" means: (a) no orphan legacy-path references via grep; (b) critical-review can read the file from start to finish; (c) inert-mode behavior fires correctly for `/slice-*` commands; (d) synthetic-tree manual run of `/sdd-migrate-layout` succeeds, is idempotent, and refuses correctly during active flows.

## Modules

For each module created or significantly changed by this feature, the public interface and the complexity it hides are articulated. Module decomposition prefers depth (Ousterhout): a small interface that hides substantial functionality.

### MODULE-001: `delivery_mode` runtime branch

- **Public Interface:** Two read-time functions consumed by mode-aware commands and the sdd-flow Step 4 entry point. Both surface as inline directives in markdown (no actual function calls): "read `delivery_mode:` from the SPEC frontmatter (defaulting to `whole-feature` when absent); branch on the value." Concrete touch points: `sdd/commands/planning-start.md` Step 6 (line 305+, allowed region); `sdd/commands/implementation-start.md` "Read Progress File" step (line 33+) and "Implementation Setup" branch (line 48+); `sdd/commands/critical-review.md` Slice Integrity sub-section gate; `sdd/commands/spec-review-panel.md` specialist 4.7 activation gate; `agent-engineering/skills/sdd-flow/SKILL.md` Step 4 routing.
- **Hides:** The default-when-absent rule (treat absent field as `whole-feature` per OQ-3 — stay silent, do not log). The string-matching against the canonical enum (`whole-feature` / `per-slice`). The mode-routing decision tree (which sub-section fires, which template variant scaffolds, which state machine runs). The contract that whole-feature behavior is preserved bit-for-bit.
- **Risk:** medium — a bug in mode-routing affects both modes simultaneously (bit-for-bit preservation invariant breaks). The check itself is small but its consequences are not.
- **Spec refs:** REQ-001, REQ-002, REQ-009, REQ-010, REQ-011, REQ-012, EDGE-009.

### MODULE-002: Slice-command primitives (`/slice-start`, `/slice-review`, `/slice-retro`, `/slice-commit`)

- **Public Interface:** Four user-invokable slash commands. Each takes an optional `[SLICE-ID]` arg matching `^SLICE-\d{3}$` plus optional flags as documented per command (per REQ-025 flag conventions): `/slice-start [SLICE-ID] [--resume | --force]` (per EDGE-012 / EDGE-013); `/slice-review [SLICE-ID]` (no flags introduced by this feature); `/slice-retro [SLICE-ID] [--reconcile-ledger]` (per REQ-005 / REQ-025a / EDGE-007 / EDGE-014 / FAIL-003); `/slice-commit [SLICE-ID]` (no flags introduced by this feature). Each emits human-readable output and (for retro/commit) writes artifacts at canonical paths. All four read `delivery_mode:` first and emit the inert-mode message when not `per-slice`. The `/slice-review` command's interface is "wrapper over `/code-review` scoped to slice files".
- **Hides:** The active-slice resolution algorithm (CLI arg → IMPLEMENTATION-PLAN's `## Slice Progress` row → user prompt if multiple; never silently pick). **Active-slice fallback asymmetry (resolves L-CR-6 / R-2):** the four slice commands resolve the active slice via the SAME priority — explicit `SLICE-XXX` argument > IMPLEMENTATION-PLAN's `## Slice Progress` row matching the command's expected status > error — but the *expected status* differs by command intent: `/slice-start` defaults to the first `Not Started` row (you can't start what's already running); `/slice-review`, `/slice-retro`, and `/slice-commit` default to the row at `In Progress` or `Acceptance Check Passing` (you can't review / retro / commit something not yet implemented). This is a cross-command convention: implementations SHOULD share a single `resolve-active-slice(expected_status_set)` helper rather than duplicating the lookup logic per command. The file-set computation for `/slice-review` (intersection of SPEC's `Modules touched` and IMPLEMENTATION-PLAN's slice-progress entries; prefer IMPLEMENTATION-PLAN on disagreement; surface divergence). The two-write ordering for `/slice-retro` (retro first, ledger second; recovery via reconcile mode per REQ-025a). The structured commit-message construction for `/slice-commit` (no `--no-verify`, no co-author). Slice-ID input validation against the regex. Per REQ-025 flag conventions: every `--<flag>` is a literal CLI argument; absence is the default; supervised-mode interactive prompts are flag-equivalent decisions; autonomous mode without the flag halts via the REQ-011 awaiting-decision-block pattern.
- **Risk:** medium — these are the primary user-facing surface for per-slice work. UX bugs (silent picks, bad inert messages, unclear errors) erode the per-slice mode's value. Per-write ordering bugs in `/slice-retro` create inconsistent ledger state.
- **Spec refs:** REQ-003, REQ-004, REQ-005, REQ-006, REQ-007, REQ-024, REQ-025, REQ-025a, EDGE-002, EDGE-003, EDGE-007, EDGE-010, EDGE-011, EDGE-012, EDGE-013, EDGE-014, FAIL-003.

### MODULE-003: Slice-integrity review checks

- **Public Interface:** A new sub-section in `sdd/commands/critical-review.md` (Planning Phase Critical Review, between lines 110 and 112) and a new specialist 4.7 in `sdd/commands/spec-review-panel.md` plus a new `#### Slice Integrity Findings` sub-header in the deliverable schema (lines 230–244). Both surface as review checklist items / specialist analysis output.
- **Hides:** The mode-gating logic (fire only when `delivery_mode: per-slice`). The seven named anti-patterns (layer-in-disguise slice, single-module slice without justification, SLICE-001 not thinnest, orphan requirements, bare acceptance checks, no slicing-rationale, practicality-gate skipped). The conditional rendering rule for the deliverable schema sub-header (rendered only if mode fired; omitted in whole-feature, never rendered with "n/a"). The severity-aggregation interplay with the existing five specialists' findings.
- **Risk:** low — these checks generate findings; they don't directly emit changes to user code or artifacts. A bug in mode-gating could falsely flag whole-feature specs (annoying but recoverable); a bug in anti-pattern detection could miss real slicing problems (the implementation phase's manual smoke flow surfaces this).
- **Spec refs:** REQ-009, REQ-010.

### MODULE-004: Practicality gate

- **Public Interface:** A new step inside `sdd/commands/planning-start.md` Step 6 (line 305+, allowed region) that runs only in `delivery_mode: per-slice`. Output: either a populated `## Delivery Slices` section, or a `Slicing not applicable: <reason>` annotation in `## Delivery Slices` plus an `## Awaiting Slicing Decision` block in `progress.md`.
- **Hides:** The four boolean heuristics (single-module touch-set, no-thinner-happy-path, universal-slice REQ touch, single concentrated function) — each with its specific detection logic per research §"Practicality-gate detection logic". The qualitative judgment-call escape (subagent's fifth, free-form check). The autonomous-vs-supervised user-interaction shape (mirrors Step 1.5 clarification gate exactly). The audit-trail discipline (the gate's decision is recorded in `progress.md` regardless of outcome, including when the gate did NOT fire).
- **Risk:** medium — false positives slow autonomous flows by halting them needlessly; false negatives let bad slicing through to implementation. The four heuristics are conservative but qualitative judgment is a known gap.
- **Spec refs:** REQ-001, REQ-011, EDGE-005.

### MODULE-005: Migration helper (`/sdd-migrate-layout`)

- **Public Interface:** A user-invokable slash command, mode-agnostic. Takes no arguments. Outputs status messages, performs `git mv` operations, emits a final summary including hook-path-change reminder and user-CLAUDE.md staleness reminder.
- **Hides:** The detection logic (4-state machine: nothing-to-migrate, partial-migration-detected-refuse, active-flow-refuse, proceed). The exact `git mv` move set (8 categories of moves: PROMPT tracker rename, summaries relocation, test-audit relocation, progress.md relocation, subagent-calls relocation, counters relocation, compaction-files relocation, parent-cleanup). The bash-detection-and-refuse logic for non-bash shells. The idempotence guarantees (re-run is no-op via `mkdir -p` + `[ -e "$f" ] || continue`). The rollback procedure (documented in command output; user pastes the reverse moves manually). The active-flow-detection signal (parse `progress.md` for the latest phase status; refuse if not `COMPLETE`).
- **Risk:** **high** — destructive operation on user repos. A mishap means data-loss or git-history breakage. Mitigations: `git mv` preserves history; active-flow refusal is the load-bearing safety check; idempotence makes re-runs safe; bash-detection prevents partial moves on non-bash shells.
- **Spec refs:** REQ-008, EDGE-001, EDGE-004, EDGE-008, FAIL-001, FAIL-002, FAIL-005, SEC-001, SEC-002.

### MODULE-006: sdd-flow Step 4 per-slice state machine

- **Public Interface:** A new sub-section in `agent-engineering/skills/sdd-flow/SKILL.md` (after the existing 4a block, line 535+) describing the per-slice cycle (4a → 4b → 4c → 4c.5 → 4c.6 → optional PAUSE) and the end-of-feature cycle (4d → 4e → 4f → 4g → 4h → 4i → 4j). Plus the slice-boundary checkpoint axis (added to Execution Modes lines 215–280); the `--skip-slice-checkpoints`, `--replan`, `--from-slice`, `--override-replan`, `--fall-back-to-whole-feature`, `--retry-slicing` arguments (added to Arguments table line 695); the per-slice review iteration cap (3 with progress-stall check); the re-planning trigger and resume options. Phase Detection (lines 636–645) gains rules for resuming from `## Awaiting Slicing Decision` and `## Recommended Re-planning` plus legacy-path fallback for the migration window.
- **Hides:** The per-mode routing decision at Step 4 entry (`delivery_mode: per-slice` triggers the per-slice cycle; `whole-feature` runs the existing horizontal flow unchanged). The per-slice-cycle-and-then-end-of-feature-cycle composition. The strict one-subagent-per-slice rule (proposal §3 + §6). The ledger-only prompt path for subsequent slice subagents (per OQ-6). The interaction matrix between phase-boundary and slice-boundary checkpoints (2x2 cross-product). The `--skip-slice-checkpoints` semantics (suppresses pause; accumulates Open recommendations; consolidated 4j surface). The re-planning halt semantics under `--skip-slice-checkpoints` (halts even though slice-checkpoints are off; mirrors Step 3c panel-review halt).
- **Risk:** medium — the orchestrator's mode-routing decision sits at the top of Step 4 and a bug there fans out to every subsequent sub-step. The complexity is real but bounded; the "whole-feature behavior preserved bit-for-bit" invariant is the load-bearing test.
- **Spec refs:** REQ-012, REQ-013, REQ-014, REQ-015, REQ-022, REQ-023, REQ-025, EDGE-006, FAIL-004.

### MODULE-007: Directory restructure + rename propagation

- **Public Interface:** Path strings emitted by every plugin command and the sdd-flow skill. The new canonical paths: `SDD/implementation/IMPLEMENTATION-PLAN-XXX-...`, `SDD/implementation/summaries/IMPLEMENTATION-SUMMARY-XXX-...`, `SDD/implementation/test-audits/TEST-AUDIT-XXX-...`, `SDD/implementation/slices/RETROSPECTIVE-SLICE-XXX-...`, `SDD/implementation/slices/LEARNINGS-FEATURE-[feature-name].md` (kebab-case feature-name slug per CLARIFICATION OQ-B; uniform across REQ-003, REQ-005, REQ-016, this MODULE entry, EDGE-007, FAIL-003), `SDD/orchestration/progress.md`, `SDD/orchestration/subagent-calls/`, `SDD/orchestration/counters/`, `SDD/orchestration/compacted/`. Plus the hook's `LOG_SUBDIR` constant.
- **Hides:** The full per-command path-update inventory (18 commands; specific lines enumerated in research §Branch 1). The PROMPT → IMPLEMENTATION-PLAN rename propagation. The Artifact Paths Contract block in SKILL.md (lines 60–136, full rewrite of the directory-structure ASCII tree). The narrative-prose references at SKILL.md lines 319 and 487 (missed by per-block enumeration; surfaced by full-file grep). The closing-oracle grep verification: `grep -n 'prompts/\|PROMPT-' agent-engineering/skills/sdd-flow/SKILL.md` MUST return zero hits, applied to every modified `sdd/commands/*.md` and `sdd/README.md`. The filename-placeholder consistency oracle: `grep -n 'LEARNINGS-FEATURE-' <every modified file>` yields the same `[feature-name]` placeholder shape across every hit.
- **Risk:** medium — partial restructure (some files updated, some not) leaves the live system inconsistent and breaks Session Resumption. The grep oracle is the verification primitive; the implementation phase MUST run it on every modified file.
- **Spec refs:** REQ-002, REQ-003, REQ-016, REQ-017, REQ-022, FAIL-006.
- **Justification (if shallow):** This module bundles a coordinated mass edit (18 command files + 1 skill file + 1 hook constant + 1 README + 4 manifests). The "interface" is the post-edit set of path strings, not an in-code abstraction boundary; the "implementation" is the diff itself. Bundling reflects the coordination constraint that all references must update in the same commit (per the closing-oracle grep at REQ-016 + the filename-placeholder consistency oracle in this module's Hides). Splitting into per-file modules would create artificial boundaries the implementation phase would have to re-couple to verify the grep oracle. Acknowledged shallow shape; pre-empts the module-depth anti-pattern flag.

### MODULE-008: Documentation surface + version manifests

- **Public Interface:** Updated `sdd/README.md` (decision aid, two-workflow restructure, changelog/migration); updated `agent-engineering/README.md` (skills note, version, changelog); minor updates to repo-root `README.md`. Four version strings across two `.claude-plugin/marketplace.json` entries and two `<plugin>/.claude-plugin/plugin.json` files.
- **Hides:** The README's two-workflow structure (which content goes in whole-feature section, which in per-slice section, which in changelog/migration). The user-CLAUDE.md staleness reminder placement (at the migration section, not in the migration command's body — out of scope for the helper itself, surfaced where users will see it). The version-string drift verification (`grep -n version` across all four files yields four matching expected values). The case-insensitive-filesystem warning placement in the README.
- **Risk:** low — documentation bugs are cosmetic and recoverable. Version-drift is mechanical and grep-verifiable. The biggest risk is incomplete README content (e.g., per-slice section missing the state-machine diagram), which manifests as user confusion rather than broken behavior.
- **Spec refs:** REQ-018, REQ-019, REQ-020, REQ-021, REQ-026, FAIL-009, RISK-007.
- **Justification (if shallow):** This module bundles README/changelog rewrites with mechanical version-string updates. The interface (updated docs + four version strings) is wider than typical for a "deep module," but the bundling reflects a real coordination constraint: per CLAUDE.md ("They drift easily — check both."), the manifest+marketplace pair MUST update in the same commit, and the README's changelog/migration section is the user-facing artifact that names the version. Splitting into "documentation module" and "version manifest module" would create a false boundary that the implementation phase would have to re-couple anyway. The cross-plugin version-coupling clauses (REQ-026 + FAIL-009 + RISK-007) belong here as well: they are documentation discipline at the README + marketplace.json layer, not a separate runtime concern. The shallowness is accepted as the price of a single-doc-pass coordination cost.

## Validation Strategy

### Automated Testing

- Unit Tests:
  - [ ] N/A. Repo has no automated test infrastructure for plugin command markdown files.
  - [ ] (Recommendation deferred) A single hook unit test for the `LOG_SUBDIR` constant change is overscope for Step C; defer.
- Integration Tests (manual smoke flows, executed before declaring 2.0.0 release-ready):
  - [ ] **Whole-feature smoke flow.** Run `/sdd-flow Add a single dummy CSV export endpoint` end-to-end in `whole-feature` mode (default). Verify: artifacts land at NEW paths; IMPLEMENTATION-PLAN content shape matches today's PROMPT-XXX modulo rename; all commands read/write at new paths without error; `/sdd-flow continue` from mid-flow resumes correctly with new Phase Detection rules.
  - [ ] **Per-slice smoke flow.** Run `/sdd-flow --supervised Add a small per-slice feature with two distinct vertical threads` with `delivery_mode: per-slice` set. Verify: practicality gate fires when appropriate (or doesn't, if slicing is meaningful); spec critical review and panel review run the slice-integrity check; Step 4 routes to per-slice state machine; ledger updates correctly across slices; slice-boundary pause fires at slice-1 → slice-2; `/slice-*` commands produce expected artifacts.
  - [ ] **`/sdd-migrate-layout` smoke test.** Synthetic legacy-layout tree → run command → confirm correct moves; re-run → confirm no-op; tree with active-phase progress.md → confirm refusal; non-bash shell → confirm refusal.
- Edge Case Tests (each tied to an EDGE-XXX above):
  - [ ] EDGE-001 idempotence (synthetic-tree manual test).
  - [ ] EDGE-002 inert-mode message (read each `/slice-*` command file; confirm first step + message text).
  - [ ] EDGE-003 no-implementation detection (synthetic-tree with `In Progress` row + empty diff).
  - [ ] EDGE-004 user-CLAUDE.md reminder (read command output template).
  - [ ] EDGE-005 practicality gate (read planning-start.md Step 6 extension; verify all four heuristics enumerated; verify `## Awaiting Slicing Decision` block matches `## Awaiting Clarification`).
  - [ ] EDGE-006 re-planning explicit-option-required (read SKILL.md Phase Detection).
  - [ ] EDGE-007 retro reconcile (read `/slice-retro` body; confirm `--reconcile-ledger` mode documented).
  - [ ] EDGE-008 case-insensitive warning (grep sdd/README.md).
  - [ ] EDGE-009 absent-field default (synthetic-tree manual test).
  - [ ] EDGE-010 multi-`Not Started` prompt (read `/slice-start` body).
  - [ ] EDGE-011 column-write authority (read `/slice-retro` body).
  - [ ] EDGE-012 in-progress conflict on `/slice-start` (read `/slice-start` body; confirm friendly refusal + `--resume` path).
  - [ ] EDGE-013 already-complete `/slice-start` requires explicit `--force` (read `/slice-start` body).
  - [ ] EDGE-014 `/slice-retro` re-invocation refusal (read `/slice-retro` body; confirm refusal message and `--reconcile-ledger` escape hatch).
  - [ ] EDGE-015 `/sdd-migrate-layout` fail-closed on `progress.md` parse failure (synthetic-tree manual test with corrupt progress.md).

### Manual Verification

- [ ] **Step A locked region byte-identical to pre-implementation commit (resolves L-CR-2).** Verification: `git diff ffeec97 -- sdd/commands/planning-start.md` shows ZERO modifications inside lines 64–204 and 375–379. Concrete grep-based oracle: `git diff ffeec97 -- sdd/commands/planning-start.md | awk '/^@@/{match($0,/\+([0-9]+)(,([0-9]+))?/,a); start=a[1]; len=(a[3]==""?1:a[3]); end=start+len-1; in_locked = ((start <= 204 && end >= 64) || (start <= 379 && end >= 375))} in_locked' | grep -E '^[+-]' | grep -vE '^(\+\+\+|---)'` MUST return empty (zero locked-region hunks). Simpler manual check: `git show ffeec97:sdd/commands/planning-start.md | sed -n '64,204p;375,379p' | sha256sum` MUST match `git show HEAD:sdd/commands/planning-start.md | sed -n '64,204p;375,379p' | sha256sum`. If either oracle reports a mismatch, the implementation has violated the locked-region invariant and MUST be reverted on those lines before declaring complete. Citation: pre-implementation commit hash is `ffeec97` (the commit that introduced the locked Step A spec template; see git log).
- [ ] **Closing-oracle grep is the binding "definition of done" for every path-touching implementation step (resolves L-CR-3).** Verification: the implementation phase MUST run, before declaring each path-touching step complete (Suggested Approach steps 2, 3, 4, 5, 6, 8, 11): `grep -n 'prompts/context-management\|prompts/\|PROMPT-' <files touched in this step>`. The oracle returns zero hits except for intentional historical references in `sdd/README.md`'s changelog/migration section (with explicit "deprecated" framing). The implementation phase MUST also run a final whole-tree pass: `grep -rn 'prompts/context-management' sdd/ agent-engineering/skills/sdd-flow/` returns zero hits; `grep -rn 'PROMPT-XXX' sdd/ agent-engineering/skills/sdd-flow/` returns zero hits outside the explicit `sdd/README.md` legacy-compatibility shim section; `grep -rn 'SDD/orchestration/subagent-calls' sdd/hooks/log_subagent_call.py` shows the new path. These greps come from research §"Closing-oracle verification" and are the authoritative section for the binding oracle.
- [ ] All slice commands fire the inert-mode message in whole-feature trees. Verification: read each command file's first step.
- [ ] Hook path constant updated. Verification: `grep -n LOG_SUBDIR sdd/hooks/log_subagent_call.py` shows `orchestration/subagent-calls`.
- [ ] No orphan legacy-path references anywhere. Verification: `grep -rn 'prompts/\|PROMPT-' sdd/ agent-engineering/skills/sdd-flow/` returns zero hits (excluding intentional changelog references in README's migration section, which can use historical PROMPT mention with explicit "deprecated" framing).
- [ ] Filename-placeholder consistency for the per-feature ledger. Verification: `grep -rn 'LEARNINGS-FEATURE-' sdd/ agent-engineering/skills/sdd-flow/` returns hits using only the `[feature-name]` slug placeholder (or concrete kebab-case feature slugs in examples). No `LEARNINGS-FEATURE-XXX` and no `LEARNINGS-FEATURE-[###]` references survive.
- [ ] **Qualitative-judgment audit-test (resolves L-CR-5).** In any synthetic-tree manual test where the practicality-gate fired qualitatively (REQ-011's qualitative-judgment escape), `grep -n 'Qualitative judgment: ' SDD/orchestration/progress.md` and a corresponding grep against the SPEC's `## Delivery Slices` annotation MUST find the literal `Qualitative judgment: ` prefix. Synthetic-tree manual test only — no automated runtime check. Failure mode: a planning subagent extends the prose without applying the prefix; the audit-trail invariant of distinguishing free-form-escape firings from boolean-heuristic firings is broken silently.
- [ ] **New terminology added to glossary in same commit as introduction (resolves L-CR-1 / REQ-020).** Verification: `git log --oneline` for any commit modifying `sdd/commands/*.md` or `agent-engineering/skills/sdd-flow/SKILL.md` MUST also show modifications to `SDD/UBIQUITOUS_LANGUAGE.md` if new terms were introduced in that commit. Simpler: at end of implementation, `grep -nF` any apparently-new term in command bodies / SKILL.md against `UBIQUITOUS_LANGUAGE.md`; either the term is in the glossary, or the term must be added in a follow-up amend (not deferred to a doc-pass step).
- [ ] **Frontmatter-fields prose at allowed line 271 stays consistent with locked region's `delivery_mode:` description (resolves C-4 cross-cutting concern).** Verification: `diff <(git show HEAD:sdd/commands/planning-start.md | sed -n '184,204p')` against the frontmatter-fields prose at line 271+ for content consistency on the `delivery_mode:` field's purpose, default value, and canonical enum. If the prose at line 271 contradicts the locked-region content (e.g., names a different default value, or omits the canonical enum), the implementation has subtly violated the spirit of the locked region even while preserving its lines byte-for-byte. Surface as a manual reviewer task.
- [ ] Two-workflow README structure is present with decision aid + both sections + changelog. Verification: read `sdd/README.md`; confirm headings.
- [ ] **Bit-for-bit preservation oracle for whole-feature mode (resolves RISK-002 reassessment).** During the whole-feature smoke flow (Integration Tests above), produce `git diff --stat` between artifacts produced by the equivalent SDD 1.2.0 run (snapshot or simulated under the legacy paths) and the same run under 2.0.0 — modulo the path-prefix change (`SDD/prompts/...` → `SDD/orchestration/...`, `PROMPT-XXX-...` → `IMPLEMENTATION-PLAN-XXX-...`). Modulo path differences, the artifact CONTENT (per-section structure, generated narrative, REQ/EDGE/MODULE counts) MUST be identical. A non-trivial content diff is evidence of a mode-routing bug masquerading as path-update.

### Performance Validation

- [ ] N/A. No perf-relevant artifacts in this feature.

### Stakeholder Sign-off

- [ ] Plugin maintainer review (Pablo Oliva).
- [ ] sdd-flow consumer review (autonomous-flow regression check via the whole-feature smoke flow above).
- [ ] Manual SDD user review (read README's two-workflow section; confirm clarity).
- [ ] Marketplace operator review (verify version strings + changelog).

## Dependencies and Risks

### External Dependencies

- **Git** — required by `/sdd-migrate-layout` (uses `git mv`). Existing dependency; no new install.
- **Python 3.9+** — required by `sdd/hooks/log_subagent_call.py`. Existing dependency; no version change.
- **bash 3.0+** — required by `/sdd-migrate-layout`'s parameter-expansion syntax. The command detects bash and refuses cleanly otherwise.
- **No new external services.** LangSmith stays a `/regression-eval-capture` concern, untouched here.

### Identified Risks

- **RISK-001: Partial restructure on commit.** A subset of plugin commands updated to new paths while others still emit legacy paths. Mitigation: implementation phase enumerates every reference up front (research §Branch 1, §Branch 2); closing-oracle grep on every modified file (per REQ-016) is the verification primitive. The implementation phase MUST run the grep on every file before declaring "verified" per REQ-016.
- **RISK-002: Mode-routing bug.** A bug in the `delivery_mode` read or branch in any of `planning-start.md`, `implementation-start.md`, `critical-review.md`, `spec-review-panel.md`, or SKILL.md fans out to every subsequent step. Mitigation: each mode-aware command's branch is documented as "if mode is per-slice, do X; else do Y (existing behavior unchanged)"; the existing-behavior path is the bit-for-bit-preservation invariant and the smoke flow's primary check.
- **RISK-003: Migration helper destructive on user repo.** A bug in the active-flow refusal or in the `git mv` move set could lose data. Mitigation: `git mv` preserves history (operations are recoverable via `git reset` + `git checkout --`); active-flow refusal is documented and tested; idempotence makes re-runs safe; bash detection prevents partial moves on non-bash shells.
- **RISK-004: Marketplace + manifest drift.** Past commits (e.g., `607dc0b`) reconciled drift, suggesting the surface is genuinely error-prone. Mitigation: `grep -n version` across all four files in the same commit; project CLAUDE.md guidance is the binding instruction.
- **RISK-005: Existing user-authored CLAUDE.md / AGENTS.md staleness.** Out of scope for the migration helper itself but a real user-experience issue post-migration. Mitigation: explicit reminder in `sdd/README.md`'s migration section and in the migration command's output. `/sdd-migrate-layout` does NOT auto-edit user docs.
- **RISK-006: Recursion-trap during this run.** This run modifies the very `sdd-flow` skill orchestrating it. A subagent that "starts using the new layout immediately" would relocate this run's own artifacts and break Session Resumption. Mitigation: every phase-execution and fix subagent prompt embeds the recursion-trap warning verbatim; this run's artifacts remain at `flow-state/SDD/...` legacy paths; source-code edits emit new paths for FUTURE runs only.
- **RISK-007: Plugin version drift between SDD 2.x and agent-engineering 0.3.x (resolves M-A2).** A user can install SDD 2.0.0 without updating agent-engineering from 0.3.x (or vice-versa). The 0.3.x sdd-flow skill embeds SDD 1.x command bodies and references legacy paths; running it against SDD 2.0.0 produces a split-tree (skill writes legacy paths, SDD commands write new paths) and silently flows `delivery_mode: per-slice` specs as `whole-feature` (no Step 4 state machine). Mitigation: README cross-references at REQ-026 (SDD README → agent-engineering 0.4.0+ minimum; agent-engineering README → SDD 2.0.0+ dependency); marketplace.json release notes call out the coupling; FAIL-009 documents the failure mode + recovery; stretch-goal version-check stub in agent-engineering 0.4.0+ skill loader (NOT required by REQ-026). The mismatch is recoverable (no data loss; orphan artifacts are `git mv`-able) but pre-emptively avoidable via the README clauses.

## Implementation Notes

### Suggested Approach

Order of work (within Step 4 of this sdd-flow run). The ordering is advisory, NOT gated — but each path-touching step has a binding "definition-of-done" oracle (per L-CR-3) that MUST pass before the step is declared complete:

1. **Foundation: glossary + ADRs already in place.** No re-work.
2. **Plugin command path updates (low-risk, mechanical).** Edit the path-only-update commands (research §Branch 1's first table) in a single pass. **Definition-of-done:** `grep -n 'prompts/\|PROMPT-' <files touched in this step>` returns zero hits. Run the closing-oracle grep on each. These are the safest first commits.
3. **Plugin command path-updates-plus-rename (low-medium risk).** Edit `code-review.md`, `implementation-test.md`, `implementation-complete.md`, `adhoc-compact.md`, `continue.md`. **Definition-of-done:** `grep -n 'prompts/\|PROMPT-' <files touched>` returns zero hits.
4. **`implementation-start.md` mode-aware branching (medium risk).** This is the biggest single-command edit. Read the file, plan the insertion points carefully, edit, manual sanity check by reading the diff. **Definition-of-done:** `grep -n 'prompts/\|PROMPT-' sdd/commands/implementation-start.md` returns zero hits AND the file contains both the whole-feature and per-slice branches readable from start to finish.
5. **`planning-start.md` Step 6 extension (medium risk; locked-region discipline).** The smallest possible edit (extend Step 6 + frontmatter-fields prose at line 271 to mention practicality gate). Cite line ranges in the commit message. **Definition-of-done:** Step A locked-region oracle from Manual Verification passes (`git show ffeec97:...` checksum matches HEAD's checksum on lines 64–204 + 375–379) AND `grep -n 'prompts/\|PROMPT-' sdd/commands/planning-start.md` returns zero hits.
6. **`critical-review.md` and `spec-review-panel.md` slice-integrity additions (low risk).** Insertion-only edits per research §Branch 5 verbatim text. **Definition-of-done:** `grep -n 'prompts/\|PROMPT-' sdd/commands/critical-review.md sdd/commands/spec-review-panel.md` returns zero hits.
7. **New command authoring (medium risk; UX-critical).** Author `slice-start.md`, `slice-review.md`, `slice-retro.md`, `slice-commit.md`, `sdd-migrate-layout.md`. Each is small but UX-critical. Inert-mode messages MUST be exact (REQ-007). Slice-ID validation regex MUST be present (REQ-024). Flag-convention discipline per REQ-025 binding. **Definition-of-done:** Each new command file passes `grep -n 'prompts/\|PROMPT-'` zero-hits AND the slice-ID regex is literally present AND inert-mode message text matches REQ-007 verbatim.
8. **`sdd-flow` SKILL.md edits (high-volume, high-risk).** This is the biggest single-file edit. Plan the sequence of sub-edits: Artifact Paths Contract first (mechanical replacement); narrative-prose lines 319 and 487 next; Phase Detection rules; Step 4 state machine insertion; Execution Modes 2x2 cross-product; Arguments table additions. **Definition-of-done:** `grep -n 'prompts/\|PROMPT-' agent-engineering/skills/sdd-flow/SKILL.md` returns zero hits AND the new path layout is the only path layout referenced AND the per-slice state machine is inserted in the documented location.
9. **Hook update (low risk; one line).** `sdd/hooks/log_subagent_call.py:18`. **Definition-of-done:** `grep -n LOG_SUBDIR sdd/hooks/log_subagent_call.py` shows the new path `orchestration/subagent-calls`.
10. **Version bumps (mechanical).** Four files; **Definition-of-done:** `grep -n version` across `sdd/.claude-plugin/plugin.json`, `agent-engineering/.claude-plugin/plugin.json`, and `.claude-plugin/marketplace.json` yields the four expected strings (sdd 2.0.0 in 2 places; agent-engineering 0.4.0 in 2 places).
11. **Documentation pass.** `sdd/README.md` two-workflow restructure (with REQ-026 cross-plugin clause); `agent-engineering/README.md` skills note + REQ-026 dependency clause; repo-root README minor description; `plugin-installation-scope.md` confirmed unchanged. **Definition-of-done:** all README grep verifications from REQ-019 + REQ-021 pass; `grep -c "agent-engineering" sdd/README.md` returns ≥1 (verifies REQ-026 SDD-side clause); `grep -c "SDD 2.0" agent-engineering/README.md` returns ≥1 (verifies REQ-026 agent-engineering-side clause).
12. **Manual smoke flows.** Whole-feature + per-slice + migration helper synthetic tree. **Definition-of-done:** all Validation Strategy Integration Tests + Edge Case Tests + Manual Verification entries pass; the bit-for-bit preservation oracle for whole-feature mode confirms RISK-002 mitigation.

### Areas for Subagent Delegation

- **Path-only updates (steps 2–3 above):** delegate to a single Explore-or-equivalent subagent with a list of files and a "replace pattern X with Y" task per category.
- **New command authoring (step 7):** delegate `slice-start.md`, `slice-review.md`, `slice-retro.md`, `slice-commit.md`, `sdd-migrate-layout.md` in parallel if context pressure mounts. Each is self-contained; cross-references are short.
- **Documentation pass (step 11):** delegate `sdd/README.md` rewrite to a single subagent with the explicit content brief from research §Branch 6.

### Critical Implementation Considerations

- **Closing-oracle grep is binding (REQ-016).** Every modified file MUST pass `grep -n 'prompts/\|PROMPT-'` returning zero hits before being declared verified. Exception: `sdd/README.md`'s migration section may include intentional historical references (e.g., "PROMPT-XXX-... (deprecated; renamed to IMPLEMENTATION-PLAN-XXX-...)" as part of the changelog). Those are explicit and bounded.
- **Step A locked region is binding.** Every `planning-start.md` edit MUST cite line ranges and confirm they're outside lines 64–204 + 375–379.
- **Recursion-trap warning is binding for downstream subagents.** Every implementation-phase subagent prompt MUST embed the recursion-trap warning verbatim. This run's artifacts are at `flow-state/SDD/...` legacy paths; source-code edits emit NEW paths for FUTURE runs.
- **`/sdd-migrate-layout` runs once per repo.** Don't over-engineer. Bash-detection refusal is acceptable; building a Python-portable helper is overscope.
- **Inert-mode messages are exact UX.** Per REQ-007, the message names the field, the required value, and the recommended action. Spec critical review will catch deviations.
- **The four-state enum and column schema for `## Slice Progress` are binding.** Verbatim per research §"## Slice Progress table schema". `/implementation-start` scaffolds the table; `/slice-retro` updates only Status/Test result/Notes columns.
- **Glossary discipline.** All vocabulary in commit messages, command bodies, and READMEs uses the canonical terms in `flow-state/SDD/UBIQUITOUS_LANGUAGE.md`. New terms get added to the glossary, not improvised.
