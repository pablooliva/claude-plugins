# RESEARCH-001-vertical-slicing-step-c

**Date:** 2026-05-05
**Author:** Claude (sdd-flow Step 2a research subagent)
**Authoritative design source:** `proposals/vertical-slicing-decomposition.md`
**Clarification:** `SDD/research/CLARIFICATION-001-vertical-slicing-step-c.md`
**Scope:** Step C of the proposal — implementing per-slice behavior end-to-end across `sdd/` plugin commands and the `agent-engineering/skills/sdd-flow/SKILL.md` skill, plus the directory restructure, the `PROMPT → IMPLEMENTATION-PLAN` rename, the `/sdd-migrate-layout` helper, slice-integrity checks in spec reviews, the practicality gate, and the version bumps. Step A (the `## Delivery Slices` block in `sdd/commands/planning-start.md`) is merged and OFF-LIMITS.

---

## Recursion-trap warning (apply to ALL downstream work)

**This sdd-flow run modifies the very `sdd-flow` skill orchestrating it.** A naive subagent could conclude "the new directory layout takes effect immediately" and start writing this run's `progress.md` to `SDD/orchestration/` instead of `SDD/prompts/context-management/`. That would split this run's artifacts across two trees and break Session Resumption.

**The rule for THIS run:**
- THIS run uses **legacy paths**: `SDD/prompts/context-management/` for orchestration state and `SDD/prompts/PROMPT-001-...` for the implementation tracker.
- The **new layout** (`SDD/implementation/`, `SDD/orchestration/`, `IMPLEMENTATION-PLAN-XXX`) being implemented in this run applies to **future runs** that occur after the SDD plugin's major-version bump and the migration helper has executed.
- Subagents implementing the new layout must do so in **plugin command source files** and the **sdd-flow skill source file** — not by relocating live in-flight artifacts.

Every phase-execution and fix subagent prompt MUST embed this warning verbatim.

---

## Step A locked region (off-limits)

In `sdd/commands/planning-start.md`:
- Frontmatter line `delivery_mode: whole-feature` (line 69) inside the spec template ` ```markdown ... ``` ` block.
- The entire `## Delivery Slices` template block (lines 184–204): explanatory blockquote, `### SLICE-001:` template, `### SLICE-002:` template, closing parenthetical.
- Quality Checklist slice items (lines 375–379).

**Allowed to modify in `planning-start.md`:** the `delivery_mode:` documentation prose around line 271, Step 6 ("Define Delivery Slices") starting at line 305, and any region unrelated to the spec template block. Edits MUST cite the line range and confirm it is outside the off-limits region above.

---

## System Data Flow

The proposed code change has three primary information flows. Citations use `file:line` from the current tree.

### Flow 1: `delivery_mode:` propagation through the SDD plugin (runtime)

1. **User authors spec** at `SDD/requirements/SPEC-[###]-[feature-name].md`. Frontmatter contains `delivery_mode: whole-feature` (default — added in Step A: `sdd/commands/planning-start.md:69`) or `delivery_mode: per-slice` (opt-in).
2. **`/planning-start` (`sdd/commands/planning-start.md:305-312`)** — already gates the `## Delivery Slices` section on `delivery_mode: per-slice` (Step A). Step C extends Step 6 to invoke the practicality gate (§5 of proposal) when slicing is requested but no meaningful slices exist.
3. **`/spec-review-panel` (`sdd/commands/spec-review-panel.md`)** — reads the spec's frontmatter `review_panel:` directive (line 27). Step C adds a slice-integrity specialist (or extends each existing specialist) that fires only when `delivery_mode: per-slice` (per Branch 5 / proposal §4).
4. **`/critical-review` (`sdd/commands/critical-review.md`)** — Planning Phase Critical Review (§3, lines 99–159) currently checks ambiguity, untestable criteria, dropped findings, contradictions. Step C inserts a slice-integrity check parallel to the existing Design Concept Fidelity gate, gated on `delivery_mode: per-slice`.
5. **`/implementation-start` (`sdd/commands/implementation-start.md`)** — Step C makes this command mode-aware. It must read `delivery_mode:` from the SPEC frontmatter and branch:
   - `whole-feature` (default): produces a single `IMPLEMENTATION-PLAN-XXX` tracker (renamed from PROMPT) and instructs the developer to implement in one tracked pass — behavior bit-for-bit identical to today's `PROMPT-XXX` flow modulo the rename.
   - `per-slice`: scaffolds an implementation plan with the `## Slice Progress` table from §2 of the proposal, and instructs the developer to use the new `/slice-*` commands instead of one tracked pass.
6. **`/slice-start`, `/slice-review`, `/slice-retro`, `/slice-commit` (new)** — only meaningful when `delivery_mode: per-slice`. In whole-feature mode they emit a friendly "requires `delivery_mode: per-slice`" message and exit (§Distribution Strategy revision in proposal).
7. **`sdd-flow` orchestrator** — the planning → implementation transition (`agent-engineering/skills/sdd-flow/SKILL.md:516-517`) reads the spec's `delivery_mode` field and routes Step 4 to either the existing horizontal flow or the new per-slice state machine (proposal §6).

### Flow 2: Directory restructure (write paths in source code)

Every plugin command and the skill currently writes to `SDD/prompts/...`. Post-restructure, those writes must target either `SDD/implementation/...` (per-feature artifacts) or `SDD/orchestration/...` (runtime state). The grep sweep enumerated every reference (see "Files That Matter / Branch 1").

The mapping (from proposal "Directory Layout"):

| Today | Future |
|---|---|
| `SDD/prompts/PROMPT-XXX-[feature]-[date].md` | `SDD/implementation/IMPLEMENTATION-PLAN-XXX-[feature]-[date].md` |
| `SDD/prompts/implementation-complete/IMPLEMENTATION-SUMMARY-XXX-...md` | `SDD/implementation/summaries/IMPLEMENTATION-SUMMARY-XXX-...md` |
| `SDD/prompts/context-management/progress.md` | `SDD/orchestration/progress.md` |
| `SDD/prompts/context-management/subagent-calls/` | `SDD/orchestration/subagent-calls/` |
| `SDD/prompts/context-management/counters/` | `SDD/orchestration/counters/` |
| `SDD/prompts/context-management/{research,planning,implementation}-compacted-*.md` | `SDD/orchestration/compacted/{...}-compacted-*.md` |
| `SDD/prompts/context-management/compact-*.md` (adhoc) | `SDD/orchestration/compacted/compact-*.md` |
| `SDD/prompts/test-audits/` (currently emitted by `implementation-test.md:411`) | `SDD/implementation/test-audits/` (per the proposal's *implementation/* groupings — test audits are implementation-phase artifacts, not orchestration state) |
| New: `SDD/implementation/slices/RETROSPECTIVE-SLICE-XXX-[feature-name]-[date].md` | per-slice mode only |
| New: `SDD/implementation/slices/LEARNINGS-FEATURE-XXX.md` | per-slice mode only |

### Flow 3: New artifacts (per-slice mode only)

- `RETROSPECTIVE-SLICE-XXX-[feature-name]-[date].md` — written by `/slice-retro` and by the orchestrator's Step 4c.5 retrospective subagent. Audit trail; never modified after writing.
- `LEARNINGS-FEATURE-XXX.md` — single rolling ledger per feature. Updated in place by every retro (consolidate, don't append). Subsequent slice subagents receive ONLY the ledger in their prompts (per Open Question 6 conservative default).
- `SDD/reviews/REVIEW-SLICE-XXX-[feature-name]-[date].md` — per-slice code review output of `/slice-review` (parallels the existing `REVIEW-XXX-...md` shape; SLICE-aware naming reflects scope per Open Question 5 conservative default).

### External dependencies

- Git (`git mv` in `/sdd-migrate-layout`).
- Python 3.9+ for the `SubagentStop` hook (already a documented prerequisite in `sdd/README.md:18`).
- No new external services. LangSmith stays a `/regression-eval-capture` concern, untouched here.

### Integration points (current → modified)

| Integration | Today's location | Step-C change |
|---|---|---|
| Hook write path | `sdd/hooks/log_subagent_call.py:18` (`LOG_SUBDIR = Path("SDD") / "prompts" / "context-management" / "subagent-calls"`) | Change to `Path("SDD") / "orchestration" / "subagent-calls"`. Single line. |
| Plugin marketplace listing | `.claude-plugin/marketplace.json:12` (`"version": "1.2.0"`) | Bump to `"2.0.0"` for SDD; bump `"0.3.0"` to `"0.4.0"` for agent-engineering. |
| Plugin manifest | `sdd/.claude-plugin/plugin.json:4` (`"version": "1.2.0"`) | Bump to `"2.0.0"`. |
| agent-engineering manifest | `agent-engineering/.claude-plugin/plugin.json:4` (`"version": "0.3.0"`) | Bump to `"0.4.0"`. |
| sdd-flow SKILL.md Phase Detection Priority | `agent-engineering/skills/sdd-flow/SKILL.md:636-645` | Add per-slice resume rules (see Branch 2). |
| sdd-flow Artifact Paths Contract | `agent-engineering/skills/sdd-flow/SKILL.md:73-92` | Update PROMPT → IMPLEMENTATION-PLAN and all `prompts/` paths; add ledger and retro entries. |

---

## Stakeholder Perspectives

### SDD plugin maintainers (Pablo Oliva + future contributors)

- Need: a coherent diff that doesn't leave orphaned `prompts/` references in any of 18 commands.
- Need: the marketplace.json + plugin.json drift surface to stay in sync (per CLAUDE.md: *"They drift easily — check both."*).
- Need: changelog + README updates that explain the breaking change and the migration helper.
- Risk: a partial restructure that updates some commands but not others, leaving the live system inconsistent and Session Resumption broken on the next run.

### sdd-flow skill consumers (auto-orchestrated runs)

- Need: the `delivery_mode` branch in Step 4 (`agent-engineering/skills/sdd-flow/SKILL.md:518-621`) to route correctly to either the existing horizontal flow or the new per-slice state machine.
- Need: the `--skip-clarify` precedent (Step 1.5) to be mirrored cleanly by `--skip-slice-checkpoints` — same semantics (suppress checkpoint pause, accumulate findings, surface in the 4j announcement).
- Need: the practicality-gate halt to mirror the Step 1.5 autonomous halt's shape exactly (per Open Question 1 conservative default).
- Need: existing `/sdd-flow continue` behavior to detect both `## Awaiting Clarification` AND new `## Awaiting Slicing Decision` blocks and resume correctly.

### Manual SDD users running commands directly (no sdd-flow)

- Need: `/implementation-start` to behave bit-for-bit identically when `delivery_mode: whole-feature` (default) — the only forced change is the renamed tracker (`PROMPT` → `IMPLEMENTATION-PLAN`) and the new directory location.
- Need: `/slice-*` commands to ship with the plugin but be inert (friendly message) when `delivery_mode != per-slice` so they don't pollute autocomplete with broken commands.
- Need: the SDD plugin README to surface two clearly-distinct workflow sections (whole-feature, per-slice) per the revised Distribution Strategy.

### Plugin marketplace operators

- Need: the major-version bump (1.2.0 → 2.0.0) to signal the breaking change to anyone re-installing.
- Need: agent-engineering bumped to 0.4.0 (additive feature: new sdd-flow Step 4 state machine, but interacts with SDD 2.0.0).
- Need: clear changelog entries that name the migration helper and link to the migration documentation in the SDD README.

### Existing in-flight runs (regression risk)

- Need: this run's own artifacts to remain at the LEGACY paths (recursion trap). The `SDD/prompts/PROMPT-001-...` tracker that future Step 4 will create MUST stay at the legacy path because the live `sdd-flow` skill expects it there.
- Need: `/sdd-migrate-layout` to refuse to run when `progress.md` shows an active phase (see Branch 4). Otherwise a user could inadvertently relocate live artifacts mid-flow.

---

## Existing-flow Regression Risks

### Whole-feature flow must remain bit-for-bit identical (modulo the forced rename + relocation)

The proposal §Distribution Strategy is explicit: "Default `whole-feature`. With this default, all existing behavior is preserved bit-for-bit." This is the highest-priority invariant. Step C must:
- Make `/implementation-start`'s mode-aware branch produce a tracker functionally identical to today's `PROMPT-XXX` (just renamed and relocated).
- Make `/code-review`, `/critical-review`, `/implementation-complete`, `/implementation-test`, `/continue`, `/adhoc-compact`, `/commit`, `/context-check`, all four compact commands continue to read and write artifacts at the new canonical paths with no behavioral change beyond path strings.
- Confirm that `sdd-flow`'s Step 4 horizontal pre-splitting heuristic (`agent-engineering/skills/sdd-flow/SKILL.md:309`) still applies in `whole-feature` mode and is not accidentally replaced by the per-slice "strict one subagent per slice" rule.

### In-flight runs using the live skill — Session Resumption assumptions

`agent-engineering/skills/sdd-flow/SKILL.md:629-645` documents the Phase Detection Priority. Two regression risks:

1. **Resumption from a legacy `progress.md`.** If a user is mid-flow when 2.0.0 lands, their `progress.md` lives at `SDD/prompts/context-management/progress.md`. The new Phase Detection logic must check the new path FIRST and fall back to the legacy path if absent. Otherwise resume looks at the wrong file and reports "no phase info → Start from Step 0" — destroying state.
2. **The migration helper itself.** `/sdd-migrate-layout` must refuse during an active flow (per Branch 4). The detection signal: `progress.md` shows a phase status that is not `COMPLETE` or no `progress.md` exists at the new path AND one exists at the legacy path with active phase markers.

### Hook integrity — `log_subagent_call.py` path expectations

Currently `LOG_SUBDIR = Path("SDD") / "prompts" / "context-management" / "subagent-calls"` (`sdd/hooks/log_subagent_call.py:18`). The hook fires on every SubagentStop event and creates the directory with `mkdir(parents=True, exist_ok=True)` (line 130). A user running 2.0.0 with a legacy directory tree will start writing logs to the new path; a user with an unmigrated tree will still write to the new path because the hook just creates whatever path it's told. **Risk:** if the migration runs but the hook isn't updated, logs split across two paths. Conversely, if the hook is updated but the migration hasn't run, logs go to the new path while the live `progress.md` and PROMPT tracker stay in `prompts/`. **Mitigation:** the hook update ships in the same release as everything else. The migration helper documents the hook path change in its own output.

### Marketplace.json + plugin.json drift surfaces

CLAUDE.md flags this directly: *"They drift easily — check both."* Step C must update three coordinated places:
- `.claude-plugin/marketplace.json:12` (sdd version)
- `.claude-plugin/marketplace.json:30` (agent-engineering version)
- `sdd/.claude-plugin/plugin.json:4`
- `agent-engineering/.claude-plugin/plugin.json:4`

A drift here means the marketplace advertises one version while the plugin manifest declares another. Past commits show this has been a recurring issue (commit `607dc0b` "Align to recent changes" likely reconciled drift).

---

## Branch 1 — SDD plugin command audit

The grep sweep enumerated every reference. Per-command summary:

### Files that need path updates only (legacy `prompts/` → new `implementation/` + `orchestration/`)

| Command | Lines touched | Update needed |
|---|---|---|
| `sdd/commands/research-start.md` | 12 | `prompts/context-management/progress.md` → `orchestration/progress.md` |
| `sdd/commands/research-complete.md` | 80 | progress.md path |
| `sdd/commands/research-compact.md` | 11, 97 | compaction file path → `orchestration/compacted/research-compacted-*.md`; progress.md path |
| `sdd/commands/planning-start.md` | 15, 24 | progress.md path. **BOTH lines are outside the locked region (which is lines 64–204 of the spec template block + 375–379 of the checklist).** |
| `sdd/commands/planning-complete.md` | 181 | progress.md path |
| `sdd/commands/planning-compact.md` | 11, 158, 196 | compaction file path → `orchestration/compacted/planning-compacted-*.md`; progress.md path |
| `sdd/commands/implementation-compact.md` | 22, 107 | compaction file path → `orchestration/compacted/implementation-compacted-*.md`; progress.md path |
| `sdd/commands/adhoc-compact.md` | 21, 24, 50, 121 | PROMPT glob → IMPLEMENTATION-PLAN glob; progress.md path; adhoc compact file → `orchestration/compacted/compact-*.md` |
| `sdd/commands/continue.md` | 60, 66, 149, 268 | progress.md path; compaction directory → `orchestration/compacted/`; PROMPT → IMPLEMENTATION-PLAN |
| `sdd/commands/context-check.md` | (zero hits — confirmed clean) | No edits needed. `grep -n 'prompts/\|PROMPT-' sdd/commands/context-check.md` returns zero hits in 1.2.0 source. **Promoted from "verify" to "confirmed clean."** |
| `sdd/commands/commit.md` | (zero hits — confirmed clean) | No edits needed. `grep -n 'prompts/\|PROMPT-' sdd/commands/commit.md` returns zero hits in 1.2.0 source. **Promoted from "verify" to "confirmed clean."** |
| `sdd/commands/critical-review.md` | 25 | PROMPT glob → IMPLEMENTATION-PLAN glob. **Plus Branch 5 slice-integrity insertion (see below).** |
| `sdd/commands/spec-review-panel.md` | (not touched in grep for `prompts/`) | **Branch 5 slice-integrity insertion only.** |
| `sdd/commands/research-clarify.md` | (not touched in grep) | verify; clarification artifact path is unchanged (`SDD/research/`) |

### Files that need path updates AND PROMPT → IMPLEMENTATION-PLAN rename

| Command | Lines touched | Notes |
|---|---|---|
| `sdd/commands/implementation-start.md` | 34, 43, 51, 57, 69, 73, 104, 337 | Path updates + rename. **Plus mode-aware branching (Branch 3 / proposal §Manual SDD section).** Insert delivery_mode read at Step "Read Progress File" (line 33-36) and add a branch in "Implementation Setup" (line 48+) and the "Implementation Process" section (line 224+). When `per-slice`, the tracker template grows the `## Slice Progress` table (proposal §2). |
| `sdd/commands/implementation-complete.md` | 38, 62, 68, 79, 229, 289, 290, 318, 329, 500, 507, 508 | Path updates (progress.md, IMPLEMENTATION-PLAN, summary location at `implementation/summaries/`) + rename. Title diagram at line 38 ("Create PROMPT-###") needs updating. |
| `sdd/commands/code-review.md` | 27, 30, 76, 177, 180, 210, 243, 339 | Path updates + rename throughout. PROMPT examples → IMPLEMENTATION-PLAN examples. Subagent-calls path → `orchestration/subagent-calls/`. **No mode-awareness needed** — code-review reads the tracker regardless of mode; `/slice-review` is a wrapper that scopes it (Branch 3). |
| `sdd/commands/implementation-test.md` | 47, 54, 65, 216, 399, 411, 419, 465, 475, 481, 490, 496, 531, 543 | Path updates + rename. Test-audit output relocation (`prompts/test-audits/` → `implementation/test-audits/`). |

### Files that need NEW per-slice mode awareness (beyond path updates)

| Command | Change |
|---|---|
| `sdd/commands/implementation-start.md` | Mode-aware branching at the start: read `delivery_mode:` from spec frontmatter, branch to whole-feature template (current behavior, renamed tracker) or per-slice template (with `## Slice Progress` from proposal §2 and instructions to use `/slice-start` etc.). |
| `sdd/commands/critical-review.md` | Insert slice-integrity check in the Planning Phase section (currently lines 99–159). The check fires only when `delivery_mode: per-slice`. Text per proposal §4. (Branch 5 detail.) |
| `sdd/commands/spec-review-panel.md` | Add a slice-integrity check (either as a section in §4 or as a new specialist 4.7) that fires only when `delivery_mode: per-slice`. (Branch 5 detail.) |
| `sdd/commands/implementation-complete.md` | When `delivery_mode: per-slice`, the IMPLEMENTATION-SUMMARY should reference all completed slices and link to retros + ledger. When `whole-feature`, behavior unchanged. |

### NEW commands to create

Per Branch 3 / proposal §Manual SDD Usage in Per-Slice Mode + §Migration cost:

- `sdd/commands/slice-start.md`
- `sdd/commands/slice-review.md` (thin wrapper over `/code-review`)
- `sdd/commands/slice-retro.md`
- `sdd/commands/slice-commit.md`
- `sdd/commands/sdd-migrate-layout.md`

### Commands that emit artifacts whose name/path changes

- `implementation-start.md` — emits PROMPT today, will emit IMPLEMENTATION-PLAN at the new path.
- `implementation-complete.md` — emits IMPLEMENTATION-SUMMARY at new path; PROMPT references all rename to IMPLEMENTATION-PLAN.
- `research-compact.md`, `planning-compact.md`, `implementation-compact.md`, `adhoc-compact.md` — emit compaction files at the new `orchestration/compacted/` path.
- `implementation-test.md` — emits test-audit at the new `implementation/test-audits/` path.
- `slice-retro.md` (new) — emits per-slice retrospective and updates ledger.
- `slice-review.md` (new) — emits `REVIEW-SLICE-XXX-[feature-name]-[date].md` under `SDD/reviews/` (parent directory unchanged; new filename pattern).
- `sdd-migrate-layout.md` (new) — does not emit artifacts; performs `git mv` operations.

---

## Branch 2 — sdd-flow skill audit

`agent-engineering/skills/sdd-flow/SKILL.md` is 710 lines. Per-area summary:

### Artifact Paths Contract (lines 60–136) — every entry that changes

| Entry | Current path | New path |
|---|---|---|
| **PROMPT tracking doc** (line 88) | `SDD/prompts/PROMPT-[###]-[feature-name]-[YYYY-MM-DD].md` | `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[YYYY-MM-DD].md` (rename + relocate) |
| **Implementation summary** (line 91) | `SDD/prompts/implementation-complete/IMPLEMENTATION-SUMMARY-[###]-[YYYY-MM-DD_HH-MM-SS].md` | `SDD/implementation/summaries/IMPLEMENTATION-SUMMARY-[###]-[YYYY-MM-DD_HH-MM-SS].md` |
| **Progress file** (line 92) | `SDD/prompts/context-management/progress.md` | `SDD/orchestration/progress.md` |
| **Per-slice retrospective** (NEW) | — | `SDD/implementation/slices/RETROSPECTIVE-SLICE-XXX-[feature-name]-[YYYY-MM-DD].md` |
| **Rolling learnings ledger** (NEW) | — | `SDD/implementation/slices/LEARNINGS-FEATURE-[###].md` |
| **Per-slice code review** (NEW) | — | `SDD/reviews/REVIEW-SLICE-XXX-[feature-name]-[YYYYMMDD].md` |
| **Subagent-calls log directory** (referenced at line 113 in tree) | `SDD/prompts/context-management/subagent-calls/` | `SDD/orchestration/subagent-calls/` |
| **Counter file directory** (line 117 in tree, line 330 in instructions) | `SDD/prompts/context-management/counters/` | `SDD/orchestration/counters/` |
| **Compacted-state files** (lines 118–120 in tree) | `SDD/prompts/context-management/{phase}-compacted-*.md` | `SDD/orchestration/compacted/{phase}-compacted-*.md` |

The Directory Structure ASCII tree at lines 96–136 needs a full rewrite to mirror the proposal's "Directory Layout" tree.

#### Narrative-prose legacy references (NOT in the table above — found by full grep)

The table above enumerates the Artifact Paths Contract block. A full grep — `grep -n 'prompts/\|PROMPT-' agent-engineering/skills/sdd-flow/SKILL.md` — returns additional narrative references embedded in prose paragraphs. **These were missed by the per-block enumeration and MUST also be updated:**

| Line | Current text (verbatim excerpt) | Required edit |
|---|---|---|
| 319 | (Subagent Safety-Net Rule, bail-out trigger paragraph) ``…follow the inlined compact-command instructions … to write `SDD/prompts/context-management/[phase]-compacted-[YYYY-MM-DD_HH-MM-SS].md`. Append a `## PARTIAL: needs continuation` block to `progress.md`…`` | Replace `SDD/prompts/context-management/[phase]-compacted-[YYYY-MM-DD_HH-MM-SS].md` with `SDD/orchestration/compacted/[phase]-compacted-[YYYY-MM-DD_HH-MM-SS].md`. (The `progress.md` reference in the same paragraph is unqualified — leave as-is; the Artifact Paths Contract earlier in the file establishes the canonical path.) |
| 487 | (Panel-review halt message, blockquote line) ``> Iteration history: `SDD/prompts/context-management/progress.md` → "Panel Review Iterations"`` | Replace `SDD/prompts/context-management/progress.md` with `SDD/orchestration/progress.md`. Resulting line: ``> Iteration history: `SDD/orchestration/progress.md` → "Panel Review Iterations"`` |

**Why these were missed:** both references live inside narrative blockquotes and instruction paragraphs rather than in the Artifact Paths Contract table at lines 60–136. A future audit of this skill (whether by `/critical-review` or by a maintainer) MUST use a full-file grep, not a section-scoped one.

**Authoritative post-edit verification (binding instruction for the implementation phase):**

```bash
grep -n 'prompts/\|PROMPT-' agent-engineering/skills/sdd-flow/SKILL.md
# MUST return zero hits. If any line is returned, that line is a missed reference;
# fix in place and re-run the grep until clean.
```

This single grep supersedes the per-line enumeration as the success criterion. The per-line table above (Artifact Paths Contract entries plus the two narrative-prose entries 319 and 487) is the *known starting set*, not the complete set; the grep is the closing oracle.

### Phase Detection Priority (lines 636–645) — what changes

Current rules check `progress.md` for phase markers. Step C additions:

- Add: `If '## Awaiting Slicing Decision' is the latest block in progress.md AND the user has resumed via /sdd-flow continue --fall-back-to-whole-feature OR --retry-slicing → resume planning subagent appropriately.` (Per Open Question 1 conservative default — mirrors `## Awaiting Clarification`.)
- Add: per-slice resume rules. If implementation is active in per-slice mode, the resume must check the `## Slice Progress` table in the IMPLEMENTATION-PLAN to determine which `SLICE-XXX` is in flight. Sub-step within Step 4 needs to be discoverable: which 4a/4b/4c/4c.5/4c.6 is the current slice in?
- Add: `If '## Recommended Re-planning' was emitted in the latest slice retrospective AND user has resumed via /sdd-flow continue --replan → re-run Step 3 (planning) with the ledger and triggering retrospective in the planning subagent's prompt; produces a revised SPEC; resumes implementation from SLICE-001 (or user-specified slice).` (Per proposal §6 "Re-planning recommendation".)
- Update: legacy-path detection. The Phase Detection Priority must check the new path first AND check the legacy path as a fallback so a partial migration doesn't lose state. After detection, surface a one-time message recommending `/sdd-migrate-layout`.

### Insertion points for the per-slice Step 4 state machine

Currently Step 4 runs lines 518–621. The proposal §6 defines two cycles:

- **Per-slice cycle (4a → 4b → 4c → 4c.5 → 4c.6 → PAUSE), runs once per SLICE-XXX.**
- **End-of-feature cycle (4d → 4e → 4f → 4g → 4h → 4i → 4j), runs once after the last slice lands.**

Insertion strategy: keep Step 4 sequential numbering for whole-feature mode (today's behavior preserved bit-for-bit). Add a NEW sub-section "Step 4 — Per-Slice State Machine (per-slice mode only)" that supersedes the per-slice subset (4a–4c.6) when `delivery_mode: per-slice`. The end-of-feature cycle (4d–4j) remains shared between both modes; the per-slice mode just runs them once after all slices land instead of after one monolithic 4a/4b/4c.

**Specific insertion points:**

- After line 535 (existing "4a Implementation" block ends) — add a "Per-slice mode" block describing strict one-subagent-per-slice (proposal §3 + §6 "Per-slice cycle").
- After the strict-per-slice block — add 4b/4c/4c.5/4c.6 sub-step descriptions per proposal §6.
- After the existing 4c block (line 549) — add the "Per-slice review iteration cap (max 3 + progress-stall check)" sub-section per proposal §6 "Per-slice review iteration cap".
- After the existing 4i block (line 610) — clarify that 4i in per-slice mode covers ONLY whole-feature artifacts (critical review doc, code from 4e, completion artifacts from 4f, eval scaffolding from 4g) because per-slice code is already committed in each 4c.6 (proposal §6 "End-of-feature cycle").

### Insertion points for the slice-boundary checkpoint axis

Per proposal §6:

- Augment the "Execution Modes" section (lines 215–280) to introduce the SECOND checkpoint axis explicitly. Currently the Execution Modes section explains supervised/autonomous (phase-boundary). Add a parallel block: "Slice-boundary checkpoints (per-slice mode only): on (default) vs off (`--skip-slice-checkpoints`)."
- Add a cross-product table (the matrix from proposal §6).
- Add `--skip-slice-checkpoints` to the Arguments table at line 695.

### Insertion point for `--skip-slice-checkpoints`

Mirrors `--skip-clarify` (line 700). Add an entry below it in the Arguments table. Document semantics in the Execution Modes section: suppresses the per-slice pause (the PAUSE between 4c.6 and the next 4a); accumulates `Open recommendations` in the ledger; consolidated surface in the 4j announcement.

### Insertion point for the re-planning trigger

Per proposal §6 "Re-planning recommendation":
- Inside the new "Per-Slice State Machine" sub-section, add a "Re-planning trigger" block that documents:
  - Detection: `## Recommended Re-planning` section in a slice retrospective.
  - Behavior: in any mode with slice-checkpoints `on`, the slice-boundary pause includes a re-planning–specific message. In autonomous + `--skip-slice-checkpoints`, the flow halts even though slice-checkpoints are off (mirrors panel-review halt at Step 3c).
  - Resume options: `/sdd-flow continue --replan`, manual SPEC edit + `/sdd-flow continue`, or `/sdd-flow continue --override-replan`.
- Add `--replan` and `--override-replan` to the Arguments table.

### Interaction with `--skip-clarify`

`--skip-slice-checkpoints` mirrors `--skip-clarify`'s pattern bit-for-bit (per proposal §6): same place in Arguments table, same shape of behavior (suppresses the pause), same logging convention (recorded in progress.md so downstream review captures the gate-skip). The implementation should literally cite `--skip-clarify` as the precedent in the SKILL.md text — this gives future readers a clear analogy.

### Other affected sections

- **Inputs in Step 3a (line 424)** — must add `SDD/UBIQUITOUS_LANGUAGE.md` reading for slicing terminology consistency, and reference the practicality gate.
- **Inputs in Step 4a (line 524)** — when `per-slice`, must reference `SDD/implementation/slices/LEARNINGS-FEATURE-[###].md` (initially empty, populated by retros).
- **Subagent Guidelines / Prompt Construction (lines 651–660)** — point 7 references the counter file path; must update to `SDD/orchestration/counters/`.

---

## Branch 3 — New command surface

### `/slice-start [SLICE-ID]`

- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md` (read frontmatter, fail if `delivery_mode != per-slice`), `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[date].md`, `SDD/implementation/slices/LEARNINGS-FEATURE-[###].md` (if exists).
- **Outputs:** Updated IMPLEMENTATION-PLAN (the slice's section is initialized in `## Slice Progress` table), updated progress.md.
- **Active-slice resolution:** prefer CLI arg if provided. Fallback: read the IMPLEMENTATION-PLAN's `## Slice Progress` table and find the next slice with status `Not Started`. If multiple, prompt the user. Do NOT silently assume.
- **Inert-mode behavior:** when `delivery_mode != per-slice`, exit with: `"This command requires delivery_mode: per-slice in the spec frontmatter. Current spec uses delivery_mode: <value>. Run /implementation-start instead, or set delivery_mode: per-slice in your spec and re-run /planning-start."`

### `/slice-review [SLICE-ID]`

Per Open Question 5 conservative default — **thin wrapper over `/code-review`, scoped to the slice's files only.**

- **Inputs:** `SDD/requirements/SPEC-[###]-[feature-name].md`, `SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[date].md` (to compute the slice's file set from `Modules touched` + slice progress entries), the implemented files for that slice.
- **Active-slice resolution:** same as `/slice-start` — prefer CLI arg, fallback to "current in-progress slice in IMPLEMENTATION-PLAN".
- **File-set computation:** intersection of (a) MODULE-XXX entries listed in the slice's `Modules touched` field and (b) files modified in the IMPLEMENTATION-PLAN's per-slice progress entries. If both lists agree, use that set. If they disagree, prefer the IMPLEMENTATION-PLAN list (it reflects what was actually modified) and surface the divergence as a finding.
- **Wrapping mechanism:** the command's body reads `/code-review`'s instructions verbatim, prepends a "Restrict review to this file set:" block with the computed file list, and writes output to `SDD/reviews/REVIEW-SLICE-XXX-[feature-name]-[YYYYMMDD].md` (parallels the existing `REVIEW-XXX-...md` shape; SLICE-aware naming reflects scope).
- **Inert-mode behavior:** same as `/slice-start`.

### `/slice-retro [SLICE-ID]`

- **Inputs:** Slice's implementation (files + tests), per-slice review (`SDD/reviews/REVIEW-SLICE-XXX-...md`), `SDD/implementation/slices/LEARNINGS-FEATURE-[###].md` (current ledger), `SDD/requirements/SPEC-[###]-[feature-name].md`.
- **Outputs (TWO writes — order critical, see Q-E resolution):**
  1. **First:** `SDD/implementation/slices/RETROSPECTIVE-SLICE-XXX-[feature-name]-[YYYY-MM-DD].md` (audit trail; never modified after writing).
  2. **Then:** in-place update to `SDD/implementation/slices/LEARNINGS-FEATURE-[###].md` (consolidate, refine, supersede — do not just append).
- **Structure (per Open Question 4 conservative default — hybrid):**
  - `## Recommended SPEC Amendments` (structured): each entry cites which SLICE-XXX/MODULE-XXX/REQ-XXX/EDGE-XXX/FAIL-XXX is affected, what the SPEC currently says, what should change with proposed wording, why grounded in observation.
  - `## Recommended Re-planning` (structured, optional, elevated severity): same structure, but signals a fundamental plan-level failure.
  - "What was learned" narrative (free-form prose): insights that don't fit a template.
- **Ledger update sections (structured):** Interface contract clarifications / Integration patterns discovered / Performance / failure modes observed / Open recommendations awaiting user decision.
- **Active-slice resolution:** same as above.
- **Recovery (per Q-E conservative default):** retro file existing without ledger update is recoverable — the next `/slice-retro` invocation (or a manual `/slice-retro --reconcile-ledger`) detects "ledger missing entries from existing retros" and reconciles. The inverse (ledger updated but retro missing) is NOT recoverable without re-running the entire retrospective; the FIRST-WRITE-WINS ordering eliminates this case.
- **Inert-mode behavior:** same as `/slice-start`.

### `/slice-commit [SLICE-ID]`

Per Q-C conservative default — **looser interpretation: produce a commit with a structured message; trust the user to manage staging.**

- **Inputs:** Active slice's implementation (code + tests), per-slice review doc, fix-findings notes, retrospective.
- **Behavior:** call `git status`, list staged files, ask the user to confirm the staged set looks slice-scoped. If the user confirms, commit with a structured message: `slice: SLICE-XXX <concentrated function summary>` body referencing the SLICE-XXX, the SPEC-XXX, and the retrospective path. NO co-author attribution (per project convention; same as `/commit`).
- **Does NOT enforce file-set restriction.** Rationale (Q-C): the stricter check is hostile to legitimate workflows like "I noticed an unrelated typo while implementing this slice and want to include the fix here." The user owns staging; the command owns message structure.
- **Active-slice resolution:** same as above.
- **Inert-mode behavior:** same as `/slice-start`.

### `/sdd-migrate-layout` (mode-agnostic — runs in either delivery mode)

See Branch 4 for full mechanics. Top-level summary:
- Detects: `SDD/prompts/` exists with content AND `SDD/orchestration/` either absent or empty.
- Refuses: when `progress.md` shows an active phase (status not `COMPLETE`).
- Idempotent: re-running on a migrated tree is a no-op with a friendly "already migrated" message.

---

## Branch 4 — Migration mechanics for `/sdd-migrate-layout`

### Detection logic

```
IF SDD/prompts/ does not exist:
  → "Nothing to migrate. Tree is already at the new layout."
  → exit 0

IF SDD/prompts/ exists AND SDD/orchestration/ exists with non-empty content:
  → "Partial migration detected. Review the tree manually before re-running."
  → list files in both trees so the user can reconcile
  → exit 1

IF SDD/prompts/context-management/progress.md exists AND parses as showing an active phase:
  → "Migration refused: an active flow is in progress (phase: <phase>, status: <status>)."
  → "Complete or abandon the in-flight flow first, then re-run /sdd-migrate-layout."
  → exit 1

ELSE:
  → proceed with the move set below.
```

The "active phase" detection: parse `progress.md` for the most recent `## Phase: <name> - <status>` block. If the latest status is anything other than `COMPLETE`, refuse. (This mirrors how `/sdd-flow continue` reads the file at SKILL.md line 631.)

### Move set (exact `git mv` operations)

```bash
# Setup (idempotent)
mkdir -p SDD/implementation/summaries
mkdir -p SDD/implementation/slices
mkdir -p SDD/orchestration/subagent-calls
mkdir -p SDD/orchestration/counters
mkdir -p SDD/orchestration/compacted

# 1. Implementation tracker (and rename PROMPT → IMPLEMENTATION-PLAN)
for f in SDD/prompts/PROMPT-*.md; do
  [ -e "$f" ] || continue
  newname="${f//PROMPT-/IMPLEMENTATION-PLAN-}"
  newpath="SDD/implementation/$(basename "$newname")"
  git mv "$f" "$newpath"
done

# 2. Implementation summaries (relocation only — filename unchanged per Q-A)
if [ -d "SDD/prompts/implementation-complete" ]; then
  for f in SDD/prompts/implementation-complete/*.md; do
    [ -e "$f" ] || continue
    git mv "$f" "SDD/implementation/summaries/$(basename "$f")"
  done
  rmdir SDD/prompts/implementation-complete 2>/dev/null
fi

# 3. Test audits (if present)
if [ -d "SDD/prompts/test-audits" ]; then
  mkdir -p SDD/implementation/test-audits
  for f in SDD/prompts/test-audits/*.md; do
    [ -e "$f" ] || continue
    git mv "$f" "SDD/implementation/test-audits/$(basename "$f")"
  done
  rmdir SDD/prompts/test-audits 2>/dev/null
fi

# 4. Orchestration state — progress.md
if [ -f "SDD/prompts/context-management/progress.md" ]; then
  git mv SDD/prompts/context-management/progress.md SDD/orchestration/progress.md
fi

# 5. Subagent-calls
if [ -d "SDD/prompts/context-management/subagent-calls" ]; then
  for f in SDD/prompts/context-management/subagent-calls/*; do
    [ -e "$f" ] || continue
    git mv "$f" "SDD/orchestration/subagent-calls/$(basename "$f")"
  done
  rmdir SDD/prompts/context-management/subagent-calls 2>/dev/null
fi

# 6. Counters
if [ -d "SDD/prompts/context-management/counters" ]; then
  for f in SDD/prompts/context-management/counters/*; do
    [ -e "$f" ] || continue
    git mv "$f" "SDD/orchestration/counters/$(basename "$f")"
  done
  rmdir SDD/prompts/context-management/counters 2>/dev/null
fi

# 7. Compaction files (research-, planning-, implementation-, adhoc compact-)
for f in SDD/prompts/context-management/{research,planning,implementation}-compacted-*.md \
         SDD/prompts/context-management/compact-*.md; do
  [ -e "$f" ] || continue
  git mv "$f" "SDD/orchestration/compacted/$(basename "$f")"
done

# 8. Cleanup empty parents
rmdir SDD/prompts/context-management 2>/dev/null
rmdir SDD/prompts 2>/dev/null
```

### Idempotence

Re-running on a migrated tree:
- `SDD/prompts/` either does not exist or is empty → first detection branch fires → "Nothing to migrate." Exit 0.
- All `mkdir -p` calls are no-ops (the `-p` flag).
- All `for f in glob; do ... done` loops with `[ -e "$f" ] || continue` no-op when no files match.

### In-flight-runs refusal

Already covered in Detection. The signal is the latest phase status in `progress.md`. Examples of "active":
- `## Research Phase - In Progress`
- `## Planning Phase - In Progress`
- `## Implementation Phase - In Progress`
- `## Awaiting Clarification`
- `## Awaiting Slicing Decision`
- `## PARTIAL: needs continuation`

Examples of "safe to migrate":
- `## Implementation Phase - COMPLETE` is the latest entry.
- No `progress.md` exists (no flow ever ran).

### Rollback (manual procedure documented in command output)

If the migration fails partway:
- All operations use `git mv`, so `git status` shows the renames as staged.
- Recovery: `git reset HEAD` to unstage, then `git checkout -- .` to undo the moves. Or, more carefully, `git mv` each file back to its original location.
- The command's output documents this verbatim with the exact reverse-move commands so a user pasting them back gets a clean revert.

### Hook-path coordination

`/sdd-migrate-layout` should NOT modify `sdd/hooks/log_subagent_call.py` — the hook is part of the plugin source, updated in the same release. The command's output should remind: *"After migration, ensure your installed SDD plugin is at version 2.0.0+ — older versions write logs to the legacy path."*

### Cross-platform shell compatibility

The Move Set above uses bash-specific constructs: `for f in glob; do ... done` loops, `[ -e "$f" ] || continue` test guards, and notably the `${f//PROMPT-/IMPLEMENTATION-PLAN-}` parameter expansion (which is bash 3.0+ syntax, not POSIX). Plugin commands run in the Claude Code shell, which on macOS/Linux is bash-compatible by default; on Windows, Claude Code may invoke commands via PowerShell or via Git Bash depending on the user's environment.

**Implementation-phase obligation:** when authoring `/sdd-migrate-layout.md`, the command body MUST either (a) be written in a shell-agnostic form (Python invocation via the plugin's hook-script discipline is one option), or (b) detect the host shell and refuse with a clear "Run from a bash-compatible shell (Git Bash on Windows)" message rather than producing partial moves on a non-bash interpreter. **Option (b) is acceptable for a one-off migration helper; option (a) would over-engineer for a command that runs once per repo.** Recommended approach: option (b) with explicit detection — `command -v bash >/dev/null 2>&1 || { echo "ERROR: /sdd-migrate-layout requires bash. On Windows, run from Git Bash."; exit 1; }`.

The implementation phase MUST verify the migration helper works on at least one bash-compatible shell (macOS default zsh-running-bash, or Linux bash) and document the Windows refusal path explicitly.

---

## Branch 5 — Slice-integrity check additions to reviews

Per proposal §4. The check text:

> **Slice integrity:** Are the slices in `## Delivery Slices` genuinely thin vertical threads through the module set, or are they horizontal layers in disguise (e.g., "SLICE-001: build the frontend; SLICE-002: build the backend")? A slice that touches only one module (when the feature spans multiple) is a smell, unless explicitly justified.

### Insertion point in `sdd/commands/critical-review.md`

Section 3 ("Planning Phase Critical Review") starts at line 99. Insert a new sub-section between the existing "Specification Weaknesses" (lines 103–110) and "Research Alignment Issues" (lines 112–117), titled "Slice Integrity (per-slice mode only)":

```
### Slice Integrity (per-slice mode only)

If the spec's frontmatter declares `delivery_mode: per-slice`, verify the `## Delivery Slices` section:

- [ ] **Vertical threads, not horizontal layers** — Does each SLICE-XXX cut through multiple modules, or do they pile up at one layer (e.g., "SLICE-001: frontend, SLICE-002: backend, SLICE-003: DB")? Layered-in-disguise slices are a HIGH finding.
- [ ] **Single-module slices justified** — A slice that touches only one MODULE-XXX (when the feature spans multiple modules) is a smell unless the rationale field explicitly justifies it (e.g., "this feature only modifies one module"). Unjustified single-module slices are a MEDIUM finding.
- [ ] **SLICE-001 thinness** — Is SLICE-001 the thinnest possible end-to-end happy path, per the spec template's guidance? A SLICE-001 that bundles edge cases or multiple concentrated functions is a MEDIUM finding (defer those to later slices).
- [ ] **Coverage** — Will every REQ-XXX / EDGE-XXX / FAIL-XXX be reachable through some slice by the time the last slice lands? Orphan REQs are a HIGH finding.
- [ ] **Acceptance check quality** — Each slice's `Acceptance check` field cites a single, focused, testable criterion. Bare "manual verification" with no detail is a MEDIUM finding.

If `delivery_mode: whole-feature` (or absent), this entire sub-section is skipped — no findings to record.
```

### Insertion point in `sdd/commands/spec-review-panel.md`

Section 4 ("Specialist Prompts") currently lists 4.1 Security through 4.5 Module Depth, with optional specialists in 4.6. Add a new specialist 4.7 Slice Integrity, mode-gated.

```
### 4.7 Slice Integrity Specialist (per-slice mode only)

**Activation gate:** Only fires when the spec's frontmatter declares `delivery_mode: per-slice`. In whole-feature mode (or when the field is absent), this specialist is skipped silently — no findings, no "checked nothing" report.

**Identity:** Senior architect reviewing the spec's `## Delivery Slices` section for genuine vertical-thread structure.

**Vocabulary payload (required context):**
Vertical slice. Horizontal layer. Concentrated function. Thread line. End-to-end happy path. Acceptance check. Slice sequence rationale. Slice-aware module decomposition. Compounding value (each slice de-risks the next). Practicality gate. Slice-integrity smell.

**Named anti-patterns to detect:**
1. **Layer-in-disguise slice** — Detection: a SLICE-XXX whose `Modules touched` lists only modules at one architectural layer (all-frontend, all-backend, all-DB). Resolution: redesign the slice to thread through layers, or merge it into another slice.
2. **Single-module slice without justification** — Detection: `Modules touched` has exactly one MODULE-XXX entry, and the feature spans multiple modules, and the `Sequence rationale` doesn't explain why. Resolution: widen the slice or write the justification.
3. **SLICE-001 not thinnest** — Detection: SLICE-001 includes EDGE-XXX or FAIL-XXX coverage, or REQs not labeled "(partial: happy path only)". Resolution: defer edge cases to later slices.
4. **Orphan requirements** — Detection: REQ-XXX / EDGE-XXX / FAIL-XXX that no SLICE-XXX claims via its `REQs satisfied` field. Resolution: assign each requirement to at least one slice (whole or partial).
5. **Bare acceptance checks** — Detection: `Acceptance check` field is empty, says only "manual verification", or duplicates the slice's `Concentrated function` field. Resolution: cite a specific test name or write a focused manual verification step.
6. **No slicing-rationale** — Detection: `Sequence rationale` is empty, generic ("makes sense to do this first"), or restates the function. Resolution: explain why this slice is at this position relative to other slices.
7. **Practicality-gate skipped** — Detection: spec's `## Delivery Slices` is empty or contains a `Slicing not applicable: <reason>` note in `per-slice` mode. Resolution: this is acceptable IF the planning subagent's practicality gate fired and the user explicitly chose per-slice anyway. Flag MEDIUM with "verify user intent" if no audit trail of the gate decision exists.

**Output schema:** Same as security specialist, with `#### Slice Integrity Findings` header.
```

The synthesis rules at SECTION 5 of `spec-review-panel.md` (severity aggregation, deduplication) apply unchanged — slice-integrity findings count toward the verdict.

### Insertion point in `sdd/commands/spec-review-panel.md` deliverable schema (lines 230–244)

The current Document Structure block at lines 230–244 hardcodes five sub-headers under `## Findings by Specialist` (Security, Performance, Data Modeling, API Contract, Module Depth). Adding a new specialist (4.7 Slice Integrity) is necessary but **not sufficient** — the deliverable template has no slot for that specialist's output, so findings would either be pushed into another specialist's section (corrupting per-specialist accountability) or dropped silently. The deliverable schema MUST also gain a corresponding sub-header.

**Current text in `sdd/commands/spec-review-panel.md` lines 230–244 (verbatim, for reference):**

```markdown
## Findings by Specialist

#### Security Findings
[Output from security specialist, verbatim.]

#### Performance Findings
[Output from performance specialist, verbatim.]

#### Data Modeling Findings
[Output from data modeling specialist, verbatim.]

#### API Contract Findings
[Output from API contract specialist, verbatim.]

#### Module Depth Findings
[Output from module-depth specialist, verbatim.]

[Any additional specialists from the panel.]
```

**Required edit — insert a new sub-header before the `[Any additional specialists from the panel.]` placeholder, gated on per-slice mode:**

```markdown
## Findings by Specialist

#### Security Findings
[Output from security specialist, verbatim.]

#### Performance Findings
[Output from performance specialist, verbatim.]

#### Data Modeling Findings
[Output from data modeling specialist, verbatim.]

#### API Contract Findings
[Output from API contract specialist, verbatim.]

#### Module Depth Findings
[Output from module-depth specialist, verbatim.]

#### Slice Integrity Findings
[Output from slice-integrity specialist, verbatim. Render this sub-header ONLY when the spec's frontmatter declares `delivery_mode: per-slice`. Omit the sub-header entirely (do not render an empty section) when `delivery_mode: whole-feature` or the field is absent — mirrors the specialist's silent-skip activation gate at section 4.7.]

[Any additional specialists from the panel.]
```

**Conditional-rendering rule (binding):** the `#### Slice Integrity Findings` sub-header is rendered iff section 4.7's activation gate fired (i.e., `delivery_mode: per-slice` in spec frontmatter). If the gate did not fire, the sub-header MUST be omitted from the deliverable, not rendered with an "n/a" placeholder. This keeps whole-feature reviews bit-for-bit identical to today's deliverable shape (one of the locked decisions).

**Severity-aggregation rules at lines 196–200 apply unchanged** — slice-integrity HIGH/MEDIUM/LOW findings flow into the totals at the `## Panel Metadata` block at lines 264–266 the same way every other specialist's findings do. Verified against current source: the aggregation rules are specialist-agnostic.

**Output-schema cross-reference:** Section 4.7's "Output schema" line ("Same as security specialist, with `#### Slice Integrity Findings` header.") binds the specialist's per-finding output to the same shape as section 4.1 (security). The deliverable's `#### Slice Integrity Findings` sub-header receives that output verbatim — no transformation, no summarization at the orchestrator level.

---

## Branch 6 — Documentation surface

### `sdd/README.md`

Per the revised Distribution Strategy (proposal §"Reconsidering the fork question"), the README needs two clearly-distinct workflow sections:

1. **Add a one-paragraph "Which mode is right for you?" decision aid** at the top, immediately after the "Overview" section. Most features → whole-feature. Multi-layer features where you want vertical thread feedback → per-slice.
2. **Restructure the workflow section into two parallel subsections:**
   - **Whole-feature workflow** (existing 3-phase diagram + description, unchanged). This preserves the documentation users have been reading.
   - **Per-slice workflow** (NEW). Includes:
     - The new state-machine diagram showing implementation-phase fan-out into slices, the per-slice cycle, and the end-of-feature merge.
     - A description of the slice commands (`/slice-start`, `/slice-review`, `/slice-retro`, `/slice-commit`).
     - The `delivery_mode: per-slice` opt-in instructions.
     - The `--skip-slice-checkpoints` escape-hatch documentation.
     - A note that per-slice mode requires SDD plugin 2.0.0+.
3. **Add a Changelog/Migration section** at the bottom:
   - Note SDD 2.0.0 ships breaking changes: directory restructure (`prompts/` → `implementation/` + `orchestration/`) and PROMPT → IMPLEMENTATION-PLAN rename.
   - Document `/sdd-migrate-layout` usage and the in-flight-refusal behavior.
   - Link to the agent-engineering plugin README's matching changelog entry.
   - **User-repo CLAUDE.md collateral.** Add a paragraph reminding users that any project-level `CLAUDE.md` (or `AGENTS.md`) referencing `SDD/prompts/...` paths becomes stale post-migration. The migration helper does not touch user-authored docs; users should grep their own CLAUDE.md for `SDD/prompts/` and `PROMPT-` and update accordingly. (Out of scope for `/sdd-migrate-layout` itself; explicitly surfaced here so users do not get bitten silently.)

#### Authoritative enumeration of legacy-path references in `sdd/README.md` (current 1.2.0 file)

The grep `grep -n 'prompts/\|PROMPT-' sdd/README.md` returns 3 hits (lines 263, 269, 269 — `prompts/test-audits/`). However, the directory-tree block at lines 392–411 contains additional structural references not picked up by that grep (the literal `prompts/` directory entry, plus child entries `implementation-complete/`, `test-audits/`, `context-management/`, `subagent-calls/`). The numbering-convention sentence at line 492 contains `PROMPT-[###]`. Branch 6 must rewrite all of these. **After edits, both `grep -c "prompts/" sdd/README.md` and `grep -c "PROMPT-" sdd/README.md` MUST return 0.** If either is non-zero, the migration story is broken.

**Per-line touch-point inventory:**

| Line(s) | Current text (verbatim or excerpt) | Required edit |
|---|---|---|
| 263 | `1. Load the PROMPT and SPEC documents to understand what was built and what coverage is expected` | Replace `PROMPT` with `IMPLEMENTATION-PLAN`. Resulting line: `1. Load the IMPLEMENTATION-PLAN and SPEC documents to understand what was built and what coverage is expected` |
| 269 | ``7. Produce a timestamped audit report in `SDD/prompts/test-audits/` and update the PROMPT document`` | Two replacements on the same line: `SDD/prompts/test-audits/` → `SDD/implementation/test-audits/`; `PROMPT document` → `IMPLEMENTATION-PLAN document`. Resulting line: ``7. Produce a timestamped audit report in `SDD/implementation/test-audits/` and update the IMPLEMENTATION-PLAN document`` |
| 379 (and surrounding example block) | The Workflow Example step ``9. Review and Finalize`` immediately precedes the example block; the block itself uses no PROMPT references but the surrounding workflow refers implicitly to the tracker. **Verify**: grep `PROMPT` against this region returns no hits in 1.2.0 source. The review's mention of line 379 reflects an `/implementation-complete` example but the actual current file does not need a textual change here beyond what's above. **Action:** confirm grep cleanliness post-edit; no edit currently needed at 379. |
| 392–411 | Directory tree under `## Directory Structure` showing `prompts/`, `implementation-complete/`, `test-audits/`, `context-management/`, `subagent-calls/`, with child files `progress.md`, `*.compact.md`, `TEST-AUDIT-XXX-*.md` | **Full rewrite required** — see "Replacement directory tree" below. |
| 492 | `**Numbering convention extended:** `CLARIFICATION-[###] → RESEARCH-[###] → SPEC-[###] → PROMPT-[###]` must align — all four artifacts for the same feature share `[###]` and `[feature-name]`.` | Replace `PROMPT-[###]` with `IMPLEMENTATION-PLAN-[###]`. Resulting line: `**Numbering convention extended:** `CLARIFICATION-[###] → RESEARCH-[###] → SPEC-[###] → IMPLEMENTATION-PLAN-[###]` must align — all four artifacts for the same feature share `[###]` and `[feature-name]`.` |

**Replacement directory tree (drop-in for current lines 392–411):**

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
    │   ├── IMPLEMENTATION-PLAN-XXX-*.md   # Tracker (renamed from PROMPT-XXX-*.md)
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

**Post-edit verification commands (must all pass before declaring Branch 6 complete):**

```bash
grep -c "prompts/" sdd/README.md           # MUST return 0
grep -c "PROMPT-" sdd/README.md            # MUST return 0
grep -c "IMPLEMENTATION-PLAN" sdd/README.md   # MUST return >= 2 (numbering convention + tree)
grep -c "implementation/" sdd/README.md       # MUST return >= 4 (tree entries)
grep -c "orchestration/" sdd/README.md        # MUST return >= 4 (tree entries)
grep -c "slices/" sdd/README.md               # MUST return >= 2 (tree entry + slice description in per-slice workflow)
```

### `agent-engineering/README.md`

Currently 30 lines. Updates needed:

- **Skills section** (line 12): update the `sdd-flow` description to mention the new Step 4 state machine in per-slice mode and the integration with the SDD plugin's slice commands.
- **Status section** (line 28): update version note from "0.3.0" to "0.4.0" and add a one-line changelog: *"v0.4.0: sdd-flow Step 4 supports per-slice delivery mode (requires SDD plugin 2.0.0+)."*

### Repo-root `README.md`

Currently 60 lines. Minor update:

- **Available Plugins → Spec-Driven Development (SDD)** section: bump the description to mention `delivery_mode: per-slice` as an opt-in and link to `sdd/README.md` for details.
- **Available Plugins → Agent Engineering** section: mention sdd-flow's per-slice support.
- No structural changes needed.

### `plugin-installation-scope.md`

Currently 122 lines. **No changes needed** — this document is about installation scope (system-wide vs project-level), orthogonal to delivery mode. Scope verified.

---

## Branch 7 — Versioning and marketplace

### SDD plugin: bump to 2.0.0

- `sdd/.claude-plugin/plugin.json:4` — change `"version": "1.2.0"` → `"version": "2.0.0"`.
- `.claude-plugin/marketplace.json:12` — change `"version": "1.2.0"` → `"version": "2.0.0"`.
- Justification: directory restructure + PROMPT → IMPLEMENTATION-PLAN rename are breaking changes for all users (whole-feature included). Per locked decision #6 + #8: same major-version bump handles both.

### agent-engineering plugin: bump to 0.4.0

- `agent-engineering/.claude-plugin/plugin.json:4` — change `"version": "0.3.0"` → `"version": "0.4.0"`.
- `.claude-plugin/marketplace.json:30` — change `"version": "0.3.0"` → `"version": "0.4.0"`.
- Justification: additive feature (new sdd-flow Step 4 state machine, new arguments `--skip-slice-checkpoints`, `--replan`, `--override-replan`) + interaction with SDD 2.0.0's renamed paths. No breaking change to existing skills' invocation surface; existing whole-feature flows continue to work after the bump.

### Drift verification

Both files (manifest + marketplace entry) must be updated in the same commit per CLAUDE.md guidance. The implementation phase MUST include a verification step: after editing, `grep -n version .claude-plugin/marketplace.json sdd/.claude-plugin/plugin.json agent-engineering/.claude-plugin/plugin.json` and confirm the four version strings match expectation.

---

## Branch 8 — Hooks and infrastructure

### `sdd/hooks/log_subagent_call.py`

The single hardcoded path:

```python
LOG_SUBDIR = Path("SDD") / "prompts" / "context-management" / "subagent-calls"
```

at line 18. Step C must change this to:

```python
LOG_SUBDIR = Path("SDD") / "orchestration" / "subagent-calls"
```

The directory is created with `mkdir(parents=True, exist_ok=True)` at line 130, so changing the constant alone is sufficient — no additional code path needs adjustment. The hook fires on `SubagentStop` events and writes a timestamped markdown file per call.

**No other path-related code in the hook.** The transcript-reading logic (lines 50–96) takes its input path from the hook payload's `transcript_path`, which is set by the harness, not the plugin.

### `.claude-plugin/marketplace.json` and `sdd/.claude-plugin/plugin.json`

The hook path in the manifest:

```json
"command": "${CLAUDE_PLUGIN_ROOT}/hooks/log_subagent_call.py"
```

at `sdd/.claude-plugin/plugin.json:16`. **No change needed** — `CLAUDE_PLUGIN_ROOT` is the plugin install root, and the hook script's location within the plugin (`hooks/log_subagent_call.py`) doesn't change.

---

## Branch 9 — Test surface

The repo has no automated tests for plugins (commands are markdown). The implementation phase MUST define "implemented and verified" explicitly per touch point:

### What "verified" means for each artifact type

1. **Modified existing command (markdown)** — verified when:
   - All references to legacy paths (`SDD/prompts/...`, `PROMPT-`, `context-management/`) have been replaced (grep returns zero hits in the file).
   - Frontmatter (if present) is unchanged (commands have no frontmatter currently except headers).
   - Critical-review can read the file from start to finish without error.
   - The file's structure (sections, code blocks, headers) is preserved.

2. **New command (markdown)** — verified when:
   - The file follows the existing command-file conventions (top-level title, identical structure to peer commands like `/code-review`).
   - Inert-mode behavior is documented and testable: the command's first step reads `delivery_mode:` from the SPEC frontmatter; if `!= per-slice`, emit the friendly message and exit.
   - Manual sanity check: run the command in a tree with `delivery_mode: whole-feature` and confirm the inert message fires.

3. **Modified `agent-engineering/skills/sdd-flow/SKILL.md`** — verified when:
   - All Artifact Paths Contract entries reflect new paths.
   - All Phase Detection Priority rules cover the new resume cases.
   - The two state-machine descriptions (whole-feature and per-slice) are clearly separated with a `delivery_mode:` branching directive at the top of Step 4.
   - The `--skip-slice-checkpoints`, `--replan`, `--override-replan` arguments are documented in the Arguments table.
   - Critical-review can read the file from start to finish.

4. **Modified `sdd/hooks/log_subagent_call.py`** — verified when:
   - `LOG_SUBDIR` constant is updated.
   - Manual sanity check: a SubagentStop event writes to the new path. (This requires running a subagent in a test session — defer to manual verification.)

5. **`/sdd-migrate-layout` command** — verified when:
   - Detection logic (active-flow refusal, partial-migration detection, idempotence check) is documented in the command's body.
   - Move set is enumerated as exact `git mv` operations (Branch 4).
   - Rollback procedure is documented in the command's output.
   - Manual sanity check: run on a synthetic tree with legacy layout and confirm correct moves; re-run and confirm no-op; run with active phase marker and confirm refusal.

6. **Marketplace + plugin.json drift** — verified when:
   - All four version strings (two in marketplace.json, two in plugin.json files) match expected values.
   - Single-line `grep -n version` check passes.

### Edge cases for the implementation phase

- **Migration on an empty tree:** `/sdd-migrate-layout` should exit cleanly with "nothing to migrate" — verified by manual run.
- **Migration with partial state:** if some files are at new paths and others at legacy, refuse with a clear message and list both sets — verified by synthetic-tree manual test.
- **Inert-mode message clarity:** the `/slice-*` commands' inert message must name the field (`delivery_mode`), the required value (`per-slice`), and what to run instead (`/implementation-start`) — verified by reading the command file.
- **Active-slice resolution ambiguity:** `/slice-start` without arg, multiple Not-Started slices in the IMPLEMENTATION-PLAN — must prompt the user, not silently pick. Verified by reading the command file.

---

## Authoritative design contracts (carried into the research, not deferred to the proposal)

The following two design surfaces were referenced multiple times across Branches 1–6 with deferrals to "see proposal §N". Per the critical review, both are made authoritative here so `/planning-start`, `/implementation-start`, `/slice-retro`, and the slice-integrity specialist all bind to the same definition without re-reading the proposal.

### Practicality-gate detection logic (binding for `/planning-start` Step 6)

**When the planning subagent runs in `delivery_mode: per-slice`, after attempting to populate `## Delivery Slices`, it MUST evaluate the following four heuristics. If ANY of them returns `true`, the practicality gate fires.**

1. **Single-module touch-set.** Every plausible slice the subagent could draft touches the same single MODULE-XXX. Boolean check: across the candidate slice set, the union of `Modules touched` fields has cardinality 1 AND `## Modules` declares more than one module. *Rationale:* a feature spanning multiple modules where every slice still pile up at one module is a sign the feature is genuinely single-module, not multi-module-with-one-touched.
2. **No thinner happy-path candidate.** The subagent cannot identify a SLICE-001 candidate that is strictly thinner than "build the whole feature, then test it." Boolean check: every drafted SLICE-001 contains all REQ-XXX entries OR contains all `Concentrated function` outputs of the feature. *Rationale:* SLICE-001's defining property is being the thinnest end-to-end happy path; if the thinnest candidate is the whole feature, slicing has no purchase.
3. **Universal-slice REQ touch.** Every plausible slice covers every REQ-XXX. Boolean check: for every drafted slice, the `REQs satisfied` set equals the full REQ-XXX set. *Rationale:* slices must differentiate by what they deliver; if all slices deliver everything, the slicing is decorative.
4. **Single concentrated function.** The feature's `Concentrated function` (per the spec template's section heading) reduces to exactly one outcome with no internal sequencing. Boolean check: `## Modules`'s public-interface enumeration sums to a single user-observable behavior (e.g., a one-shot batch transform, a config-only change, a schema migration with no rollout). *Rationale:* without internal sequencing, there is no thread to slice.

**Action when the gate fires:**

1. Populate `## Delivery Slices` with a single annotation: `Slicing not applicable: <reason>` where `<reason>` cites the heuristic(s) that returned true (e.g., "heuristic 1: single-module touch-set; the feature only modifies MODULE-001"). The annotation is the audit trail.
2. Append a `## Awaiting Slicing Decision` block to `progress.md` (mirrors `## Awaiting Clarification` from the Step 1.5 gate exactly — same shape, same parsing). The block records: the gate-firing heuristic(s), the proposed `Slicing not applicable: <reason>` text, the user's two resume options.
3. Surface to the user (in supervised AND autonomous modes) a message of the form: *"The planning subagent could not extract meaningful slices for this feature because <reason>. You have two options: (a) fall back to whole-feature mode (`/sdd-flow continue --fall-back-to-whole-feature`), (b) push back and have the subagent retry slice extraction (`/sdd-flow continue --retry-slicing`)."* The message MUST name the firing heuristic(s).
4. **Audit-trail discipline:** the gate decision (whether the user falls back, retries, or the gate did NOT fire at all) is recorded in `progress.md` regardless. This is what the slice-integrity specialist's anti-pattern #7 inspects post-hoc.

**When the gate does NOT fire** (none of the four heuristics returned true): the subagent populates `## Delivery Slices` normally and proceeds; no `## Awaiting Slicing Decision` block appears. This is the success path.

**Judgment-call escape:** if none of the four boolean heuristics fires but the subagent still believes slicing is impractical (a fifth, qualitative judgment), it MUST surface the gate anyway with `<reason>` set to "subagent judgment: <one-sentence rationale>". The user retains the same two resume options. This case is rare; the four boolean heuristics cover the documented common cases.

### `## Slice Progress` table schema (binding for `/implementation-start` and `/slice-retro`)

**The `## Slice Progress` section appears in the IMPLEMENTATION-PLAN document** (`SDD/implementation/IMPLEMENTATION-PLAN-[###]-[feature-name]-[YYYY-MM-DD].md`), **only when `delivery_mode: per-slice`**. It is initialized by `/implementation-start` (or by the first run of `/slice-start` if the IMPLEMENTATION-PLAN was scaffolded by sdd-flow with no slice section) and updated in place by `/slice-retro` after each slice's retrospective completes.

**Document position:** the `## Slice Progress` table appears immediately after the IMPLEMENTATION-PLAN's frontmatter / header block and before the per-slice work-log sections. In whole-feature mode, this section is omitted entirely (do NOT render an empty `## Slice Progress` heading); the per-REQ tracker takes its place — preserves bit-for-bit whole-feature behavior.

**Canonical column schema (binding):**

| Column | Type | Source-of-truth | Notes |
|---|---|---|---|
| `SLICE-ID` | identifier | SPEC's `## Delivery Slices` section | E.g., `SLICE-001`. One row per slice. Order matches SPEC order. |
| `Name` | short string | SPEC's `## Delivery Slices` `Concentrated function` field | Single-line slice name. |
| `Status` | enum (see below) | `/slice-start` and `/slice-retro` write this | One of the four canonical states below. |
| `Acceptance check` | string | SPEC's `## Delivery Slices` `Acceptance check` field | The specific test name or manual verification step. Copied from SPEC at scaffold time; updated only if SPEC is amended. |
| `Test result` | string | `/slice-retro` updates this | Free-form: `passing` (most common), `failing: <test name> + <reason>`, `n/a (manual)`, etc. |
| `Notes` | string | `/slice-retro` writes this | Brief pointer to retrospective path, blocking issues, or "see ledger §X". |

**Canonical state-value enum (binding — these four strings, exactly):**

1. `Not Started` — initial state. Slice has not been picked up by `/slice-start` or any subagent. `Test result` and `Notes` columns are empty (`—` is acceptable).
2. `In Progress` — `/slice-start` has fired (or sdd-flow has spawned the slice's 4a subagent). The slice is being implemented. The acceptance check has not yet passed.
3. `Acceptance Check Passing` — implementation finished, `Acceptance check` (column 4) is reported passing. Per-slice review (4b) and retro (4c.5) have NOT yet run. (This state exists so the orchestrator can surface a different pause message between "implement done, review pending" and "fully done".)
4. `Complete` — `/slice-retro` has run, the retrospective and ledger update are written, and (in sdd-flow per-slice mode) `/slice-commit` has fired. Terminal state for this slice.

**State transitions (binding):**

- `Not Started` → `In Progress`: triggered by `/slice-start` or sdd-flow's per-slice 4a subagent spawn.
- `In Progress` → `Acceptance Check Passing`: triggered when the slice subagent's bounded return reports the acceptance check passes (per proposal §3 — "Slice X delivered. Acceptance check `<test name>` passes.").
- `Acceptance Check Passing` → `Complete`: triggered by `/slice-retro`'s second write (the ledger update; see Q-E resolution for ordering). `/slice-commit` does NOT advance state — the commit is a delivery action, not a state transition; the slice is `Complete` once the retro+ledger writes are durable.
- **No backwards transitions.** A slice that needs rework (e.g., a per-slice review iteration cap halt at 4c) stays at `In Progress` or `Acceptance Check Passing` and surfaces the halt via the standard mechanism (LEARNINGS-FEATURE ledger's `Open recommendations` section + slice-boundary pause). The status column is not used to encode "stuck" — that signal lives in the ledger.

**Example minimal table (for IMPLEMENTATION-PLAN scaffold):**

```markdown
## Slice Progress

| SLICE-ID  | Name                              | Status      | Acceptance check                | Test result | Notes |
|-----------|-----------------------------------|-------------|----------------------------------|-------------|-------|
| SLICE-001 | Thinnest end-to-end happy path    | Not Started | `tests/e2e/slice_001_happy.py`   | —           | —     |
| SLICE-002 | Add edge-case handling for X      | Not Started | `tests/e2e/slice_002_edge_x.py`  | —           | —     |
| SLICE-003 | Add failure-mode handling for Y   | Not Started | `tests/e2e/slice_003_fail_y.py`  | —           | —     |
```

**Binding consequences (read by `/implementation-start`, `/slice-start`, `/slice-retro`, `/sdd-flow` Phase Detection):**

- `/implementation-start.md`'s scaffold step (per Branch 1) MUST emit this exact table shape when `delivery_mode: per-slice`. Column headers verbatim. State-value enum verbatim.
- `/slice-retro.md` (per Branch 3) MUST update only the `Status`, `Test result`, and `Notes` columns; never SLICE-ID, Name, or Acceptance check (those are SPEC-derived).
- sdd-flow's Phase Detection rule for "which slice is in flight" (per Branch 2) parses the `Status` column looking for `In Progress` or `Acceptance Check Passing`; both are "active". `Not Started` is "queued"; `Complete` is "done".
- The slice-integrity specialist's anti-pattern #4 ("Orphan requirements") cross-checks SPEC's `REQs satisfied` field against the SLICE-IDs present in this table — the table is the implementation-side authority on which slices exist.

**Cross-platform note:** the table is plain-Markdown pipe syntax. No platform-specific rendering. Human-readable + grep-friendly + parseable by simple regex (which is how Phase Detection processes it).

### Core logic (touched by Step C)

- `sdd/commands/planning-start.md` — locked region (lines 64–204 + 375–379) is OFF-LIMITS; allowed regions are line 271 (frontmatter docs prose) and Step 6 starting at line 305. Step C extends Step 6 to invoke the practicality gate.
- `sdd/commands/implementation-start.md` — major rewrite for mode-aware branching + path updates + PROMPT → IMPLEMENTATION-PLAN rename.
- `sdd/commands/critical-review.md` — insertion of slice-integrity check in Planning Phase section (between lines 110 and 112).
- `sdd/commands/spec-review-panel.md` — insertion of new specialist 4.7 Slice Integrity.
- `sdd/commands/code-review.md` — path updates + rename throughout. No mode-awareness needed (slice-review wraps it).
- `sdd/commands/implementation-complete.md` — path updates + rename + per-slice IMPLEMENTATION-SUMMARY enrichment when mode is per-slice.
- `sdd/commands/implementation-test.md` — path updates + rename + test-audit relocation.
- `sdd/commands/{research,planning,implementation,adhoc}-compact.md` — compaction file path → `orchestration/compacted/`.
- `sdd/commands/continue.md` — Phase Detection updates + path updates + rename.
- `sdd/commands/{research-start,research-complete,research-clarify,research-compact,planning-complete,context-check,commit}.md` — path updates only (where applicable).
- `agent-engineering/skills/sdd-flow/SKILL.md` — major edits per Branch 2.
- `sdd/hooks/log_subagent_call.py` — single line update at line 18.

### NEW files to create

- `sdd/commands/slice-start.md`
- `sdd/commands/slice-review.md`
- `sdd/commands/slice-retro.md`
- `sdd/commands/slice-commit.md`
- `sdd/commands/sdd-migrate-layout.md`

### Tests

No unit tests exist for plugin command markdown. "Verification" relies on critical-review reading the files and manual sanity checks of inert-mode behavior. The implementation phase MUST define the verification approach explicitly per touch point (per Branch 9).

### Configuration

- `.claude-plugin/marketplace.json` — bump SDD to 2.0.0, agent-engineering to 0.4.0.
- `sdd/.claude-plugin/plugin.json` — bump to 2.0.0.
- `agent-engineering/.claude-plugin/plugin.json` — bump to 0.4.0.

### Documentation surfaces

- `sdd/README.md` — two-workflow restructure + changelog.
- `agent-engineering/README.md` — version + skills note.
- repo-root `README.md` — minor description updates.
- `plugin-installation-scope.md` — no changes needed.

---

## Security Considerations

### `/slice-commit` must not bypass git hooks

The command's invocation must use plain `git commit` without `--no-verify`. Per CLAUDE.md (project-wide): *"Never skip hooks (--no-verify) ... unless the user has explicitly asked for it. If a hook fails, investigate and fix the underlying issue."* The command's body should explicitly document that pre-commit hooks run and document the recovery path if a hook fails (fix issue, re-stage, re-run `/slice-commit`).

### `/sdd-migrate-layout` must refuse during active flow (data-loss risk)

Already covered in Branch 4. The active-phase detection is the load-bearing safety check. Test surface MUST include a synthetic-tree test with active phase markers to confirm the refusal fires.

### Path-changes must not enable directory traversal in any command

The new path templates (`SDD/implementation/...`, `SDD/orchestration/...`, `SDD/implementation/slices/...`) are all hardcoded relative to the project root. No user-supplied input is interpolated into a path. The slice-ID arguments to `/slice-*` commands are SLICE-XXX strings — these MUST be validated against the regex `^SLICE-\d{3}$` before being used in any path construction. (Bare interpolation of an attacker-supplied SLICE-ID like `../../etc/passwd` could traverse — even though the command wouldn't write the escape-hatch tree, the read could still leak file contents into a subagent prompt.)

### Hook does not handle untrusted input

The hook reads from stdin (the harness payload) and writes to a hardcoded path. No path traversal risk. The transcript-reading logic uses `os.path.exists` and `open` with the harness-provided path — trustable since the harness is on the same trust boundary.

### Per-slice mode does not introduce new credentials or secrets surfaces

All new artifacts (RETROSPECTIVE-SLICE, LEARNINGS-FEATURE, REVIEW-SLICE) are markdown documents written under `SDD/`. No tokens, no API keys, no PII. Same threat model as existing SDD artifacts.

---

## Testing Strategy

### Unit tests

N/A — markdown commands and a single Python hook with one constant change. The hook has no test infrastructure currently. **Implementation phase recommendation:** adding a single hook unit test is overscope for Step C; defer.

### Integration tests (manual smoke flow)

After Step C lands and before declaring 2.0.0 release-ready, execute:

1. **Whole-feature smoke flow.** Run `/sdd-flow Add a single dummy CSV export endpoint` end-to-end in `whole-feature` mode (default). Verify:
   - All artifacts land at NEW paths (`SDD/implementation/IMPLEMENTATION-PLAN-...`, `SDD/orchestration/progress.md`, etc.).
   - The IMPLEMENTATION-PLAN has the same content shape as today's PROMPT-XXX (just renamed).
   - All commands (`/code-review`, `/critical-review`, `/implementation-complete`, etc.) read and write at the new paths without error.
   - `/sdd-flow continue` from a mid-flow state resumes correctly with the new Phase Detection rules.

2. **Per-slice smoke flow.** Run `/sdd-flow --supervised Add a small per-slice feature with two distinct vertical threads` and set `delivery_mode: per-slice` in the spec. Verify:
   - Practicality gate: confirm the planning subagent assesses sliceability and either populates `## Delivery Slices` or pauses at the practicality gate.
   - Spec critical review and panel review fire the slice-integrity check.
   - Implementation Step 4 routes to the per-slice state machine (one subagent per slice, mandatory per-slice review, retrospective, commit, pause).
   - Ledger updates correctly across slices.
   - Slice-boundary checkpoint pause fires at slice-1 → slice-2 boundary; user resumes; flow continues.

3. **`/sdd-migrate-layout` smoke test.** Construct a synthetic tree with legacy layout. Run the command. Verify:
   - All files moved to expected new paths.
   - Re-running is a no-op.
   - With an active-phase progress.md, refusal fires.

### Edge cases

- **Migration helper idempotence:** explicitly tested above.
- **In-flight refusal:** explicitly tested above.
- **Slice command inert-mode messages:** for each of the 4 slice commands, run with a `whole-feature` spec and confirm the inert message fires with correct field name + recommended action.
- **Spec without `delivery_mode:` field:** confirm the loader treats it as `whole-feature` (per Open Question 3 conservative default — stay silent, no log line).
- **Resume from `## Awaiting Slicing Decision`:** confirm Phase Detection routes correctly.
- **Resume from `## Recommended Re-planning`:** confirm `/sdd-flow continue --replan` re-runs Step 3 with the ledger and triggering retro in scope.

---

## Documentation Needs

Already covered in Branch 6. Summary:

- **`sdd/README.md`** — two-workflow restructure (whole-feature, per-slice) with a "Which mode is right for you?" decision aid at top + changelog/migration section at bottom.
- **`agent-engineering/README.md`** — version bump note + skills-section update for sdd-flow.
- **Repo-root `README.md`** — minor description tweaks for both plugins.
- **`plugin-installation-scope.md`** — no changes needed.

---

## Resolution of open questions

### Q-A: Do existing `IMPLEMENTATION-SUMMARY-XXX-...md` files in `prompts/implementation-complete/` need renaming or just relocation?

**Resolution: relocation only — same filename, new parent directory.**

The proposal's "Directory Layout" section shows the file's new location as `SDD/implementation/summaries/IMPLEMENTATION-SUMMARY-XXX-YYYY-MM-DD_HH-MM-SS.md` — the filename pattern is preserved verbatim. Only the parent directory changes (`implementation-complete/` → `summaries/`). The filename (which embeds the canonical `IMPLEMENTATION-SUMMARY` prefix) does not need renaming because it was never named after the parent directory.

**Consequence for downstream work:** `/sdd-migrate-layout`'s move set for these files is a simple `git mv` to the new directory with no rename needed.

### Q-B: The `RETROSPECTIVE-SLICE-XXX-feature-YYYY-MM-DD.md` filename — does `feature` mean feature-name (slug) or feature-number?

**Resolution: feature-name slug, consistent with all other SDD artifacts.**

Every other per-feature artifact in the SDD plugin uses `[feature-name]` (kebab-case slug) as the variable component, not `[###]`:
- `RESEARCH-[###]-[feature-name].md`
- `SPEC-[###]-[feature-name].md`
- `PROMPT-[###]-[feature-name]-[YYYY-MM-DD].md` (which becomes `IMPLEMENTATION-PLAN-[###]-[feature-name]-[YYYY-MM-DD].md`)
- `REVIEW-[###]-[feature-name]-[YYYYMMDD].md`
- `CRITICAL-RESEARCH-[feature-name]-[YYYYMMDD].md`

Standardizing on `RETROSPECTIVE-SLICE-XXX-[feature-name]-[YYYY-MM-DD].md` keeps the convention consistent. The `XXX` here is the slice number (001, 002, ...), not the feature number. The `LEARNINGS-FEATURE-XXX.md` ledger keeps `XXX` as the FEATURE number per the proposal's intent (one ledger per feature) — naming `LEARNINGS-FEATURE-[###].md` is unambiguous.

**Consequence for downstream work:** the planning + implementation subagents must standardize on this naming. The `/slice-retro` command body must use the resolved feature-name slug, not the feature number, in the retrospective filename.

### Q-C: Does `/slice-commit` enforce slice-scoped staging?

**Resolution: looser interpretation — commit with structured message; trust user-managed staging.**

(Already detailed in Branch 3.) The stricter check is hostile to legitimate workflows ("I noticed an unrelated typo while implementing this slice and want to include the fix here"). The user owns staging; the command owns message structure.

**Consequence for downstream work:** `/slice-commit`'s body asks the user to confirm the staged set looks slice-scoped, then commits with a structured message. No file-set restriction is enforced.

### Q-D: How is "completed slices remain valid" assessed when re-planning fires?

**Resolution: user judgment, surfaced in the resume prompt. The orchestrator does not auto-determine validity.**

Per the Conservative defaults section of the CLARIFICATION. The orchestrator's role at re-planning resume:

1. Read the latest retrospective with `## Recommended Re-planning`.
2. Read the IMPLEMENTATION-PLAN's `## Slice Progress` table to identify completed slices.
3. Surface the list of completed slices in the resume prompt with the user's options:
   - "Re-plan and re-run all slices from SLICE-001 (safest; assumes completed slices may need rework)."
   - "Re-plan and resume from a user-specified slice (faster; user vouches that completed slices remain valid)."
4. The user picks an option; orchestrator routes accordingly.

**Consequence for downstream work:** `/sdd-flow continue --replan` accepts an optional `--from-slice SLICE-XXX` argument. Without it, defaults to SLICE-001. The orchestrator never makes the validity judgment unilaterally.

### Q-E: Recovery for `/slice-retro` partial write?

**Resolution: write retrospective FIRST (audit trail; immutable), then ledger update (recoverable). The retro file existing without the ledger update is a recoverable state; the inverse is not.**

(Already detailed in Branch 3.) The first-write-wins ordering eliminates the unrecoverable case.

**Consequence for downstream work:** `/slice-retro` and the orchestrator's Step 4c.5 retrospective subagent must follow this ordering verbatim. Optional: a `/slice-retro --reconcile-ledger` mode that scans for "ledger missing entries from existing retros" and rebuilds the ledger from the retros — useful if a disk error mid-write left an inconsistent state.

---

## What success looks like

The implementation is complete when (mirroring CLARIFICATION's "What success looks like" with research-confirmed file/line references):

1. All proposal §1–§6 changes are implemented in the SDD plugin command source files and the sdd-flow skill source. Branch 1, 2, 3, 5 above enumerate every touch point with line numbers.
2. The directory restructure (proposal "Directory Layout" section) is implemented in the plugin/skill source. Branches 1 and 2 enumerate every path string that needs updating. The migration helper (Branch 4) handles existing user trees.
3. The `PROMPT-XXX` → `IMPLEMENTATION-PLAN-XXX` rename is propagated through all command/skill files. Branches 1 and 2 enumerate every reference.
4. The `/sdd-migrate-layout` command exists at `sdd/commands/sdd-migrate-layout.md`, follows the move-set in Branch 4, and is documented in `sdd/README.md`'s migration section.
5. SDD plugin bumps to 2.0.0 (`sdd/.claude-plugin/plugin.json:4` and `.claude-plugin/marketplace.json:12`); agent-engineering bumps to 0.4.0 (`agent-engineering/.claude-plugin/plugin.json:4` and `.claude-plugin/marketplace.json:30`).
6. `sdd/README.md` has the two clearly-distinct workflow sections + decision-aid + changelog per the revised Distribution Strategy.
7. Whole-feature mode behavior is preserved bit-for-bit modulo the forced rename + relocation. The Branch 1 audit verifies no command reads the legacy paths after Step C; the smoke flow in the Testing Strategy verifies end-to-end behavior.
8. Step A's locked region in `sdd/commands/planning-start.md` (lines 64–204 + 375–379) is unchanged.
