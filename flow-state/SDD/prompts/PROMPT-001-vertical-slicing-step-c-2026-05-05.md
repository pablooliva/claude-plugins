# PROMPT-001-vertical-slicing-step-c: Vertical Slicing Step C — `delivery_mode: per-slice` infrastructure

## Executive Summary

- **Based on Specification:** `SDD/requirements/SPEC-001-vertical-slicing-step-c.md`
- **Research Foundation:** `SDD/research/RESEARCH-001-vertical-slicing-step-c.md`
- **Clarification:** `SDD/research/CLARIFICATION-001-vertical-slicing-step-c.md`
- **Glossary:** `SDD/UBIQUITOUS_LANGUAGE.md`
- **Authoritative design source:** `proposals/vertical-slicing-decomposition.md`
- **ADRs respected:** `SDD/adr/0001-merged-codebase-with-delivery-mode-frontmatter.md`, `SDD/adr/0002-restructure-sdd-artifact-directory-layout.md`
- **Start Date:** 2026-05-05
- **Author:** Claude (with Pablo Oliva)
- **Status:** In Progress
- **Mode:** autonomous (auto mode active in user session)
- **Delivery mode:** whole-feature (per user directive — meta-irony intended; this feature builds the per-slice infrastructure that doesn't yet exist for its own delivery)

### Recursion-trap warning (binding for every chunk subagent)

THIS run uses `flow-state/SDD/prompts/context-management/...` for orchestration state and `flow-state/SDD/prompts/PROMPT-001-vertical-slicing-step-c-2026-05-05.md` (this file) for the implementation tracker. The new layout (`SDD/implementation/`, `SDD/orchestration/`, `IMPLEMENTATION-PLAN-XXX`) is what we are *implementing in source code* in this run; it applies to **future runs in clean repos**. Subagents must not relocate this run's own artifacts. Source-code edits emit the new paths; this run's tracker, progress.md, retros, reviews, etc. stay at legacy `flow-state/SDD/...` paths.

### Step A locked region (binding)

`sdd/commands/planning-start.md` lines 64–204 + 375–379 are OFF LIMITS. No chunk may modify these line ranges. Allowed regions for `planning-start.md` edits: line 271 (frontmatter-fields prose) and Step 6 starting at line 305. Every chunk that touches `planning-start.md` MUST cite the exact line range it edits.

### This-repo deviation (case-collision)

APFS is case-insensitive on this volume; `SDD/` collides with the `sdd/` plugin source dir. All artifact files this run reads/writes use `flow-state/SDD/...` form when passed to tool calls; in-body references keep the conventional `SDD/...` form (prescriptive, not pointers). The hook at `sdd/hooks/log_subagent_call.py:18` re-creates `sdd/prompts/...` on this volume; that telemetry directory is `.git/info/exclude`'d locally and is not load-bearing.

---

## Specification Alignment

### Requirements Implementation Status

#### Functional Requirements (REQ-XXX)

- [x] REQ-001: `delivery_mode` validation in `planning-start.md` (allowed regions only) — Chunk 1 — Status: Complete
- [x] REQ-002: `implementation-start.md` mode-aware tracker scaffolding (whole-feature preserved bit-for-bit; per-slice scaffolds `## Slice Progress`) — Chunk 1 — Status: Complete
- [x] REQ-003: `/slice-start` command (active-slice resolution, `## Slice Progress` row update, ledger load) — Chunk 2 — Status: Complete (sdd/commands/slice-start.md)
- [x] REQ-004: `/slice-review` command (thin wrapper over `/code-review`, slice-scoped file set, `[YYYY-MM-DD]` date format) — Chunk 2 — Status: Complete (sdd/commands/slice-review.md)
- [x] REQ-005: `/slice-retro` command (RETROSPECTIVE artifact + in-place ledger update; retro-first ordering; refusal on existing retro per EDGE-014) — Chunk 2 — Status: Complete (sdd/commands/slice-retro.md)
- [x] REQ-006: `/slice-commit` command (atomic per-slice commit, looser staging, structured heredoc commit message, no `--no-verify`) — Chunk 2 — Status: Complete (sdd/commands/slice-commit.md)
- [x] REQ-007: All four `/slice-*` commands inert outside per-slice mode (friendly message names field/value/alternative) — Chunk 2 — Status: Complete (Inert-Mode Gate section in slice-start.md / slice-review.md / slice-retro.md / slice-commit.md emitting REQ-007 verbatim message)
- [x] REQ-008: `/sdd-migrate-layout` command (detect old layout, refuse on active flow + parse-failure fail-closed, idempotent, partial-migration refusal, bash-only) — Chunk 3 — Status: Complete (sdd/commands/sdd-migrate-layout.md)
- [x] REQ-009: Slice-integrity check in `critical-review.md` (mode-gated on `delivery_mode: per-slice`) — Chunk 1 — Status: Complete
- [x] REQ-010: Slice-integrity specialist 4.7 in `spec-review-panel.md` + `#### Slice Integrity Findings` deliverable sub-header (mode-gated) — Chunk 1 — Status: Complete
- [x] REQ-011: Practicality gate in `planning-start.md` allowed regions (four boolean heuristics + qualitative escape with `Qualitative judgment: ` prefix; supervised + autonomous halt patterns) — Chunk 1 — Status: Complete
- [ ] REQ-012: `sdd-flow` Step 4 mode-routes by `delivery_mode:` (whole-feature unchanged bit-for-bit; per-slice runs per-slice cycle per SLICE-XXX row) — Chunk 4b — Status: Not Started
- [ ] REQ-013: Per-slice review iteration cap = 3 with progress-stall check; on halt route to ledger `Open recommendations awaiting user decision`; under `--skip-slice-checkpoints` halts whole flow — Chunk 4b — Status: Not Started
- [ ] REQ-014: Re-planning recommendation halts even under `--skip-slice-checkpoints`; resume options `/sdd-flow continue --replan [--from-slice SLICE-XXX]` and `--override-replan`; three-tier model surfacing — Chunk 4b — Status: Not Started
- [ ] REQ-015: Slice subagents receive ONLY the rolling ledger in their prompts (per OQ-6) — Chunk 4b — Status: Not Started
- [x] REQ-016: Source-code path emissions use new layout (`SDD/implementation/...`, `SDD/orchestration/...`, `IMPLEMENTATION-PLAN-XXX`, `LEARNINGS-FEATURE-[feature-name]`) across every modified file; closing-oracle grep zero hits on `prompts/` and `PROMPT-` outside SKILL.md and migration helper — Chunk 1 — Status: Complete (sdd/commands/ + sdd/hooks/ migrated; SKILL.md is Chunk 4a)
- [x] REQ-017: `sdd/hooks/log_subagent_call.py:18` `LOG_SUBDIR` updated to `Path("SDD") / "orchestration" / "subagent-calls"` — Chunk 1 — Status: Complete
- [ ] REQ-018: Version bumps — `sdd` plugin → 2.0.0 (plugin.json + marketplace.json); `agent-engineering` → 0.4.0 (plugin.json + marketplace.json) — Chunk 5 — Status: Not Started
- [ ] REQ-019: `sdd/README.md` two-workflow restructure (decision aid + Whole-feature + Per-slice + Migration/Changelog including agent-engineering 0.4.0+ cross-ref) — Chunk 5 — Status: Not Started
- [x] REQ-020: Glossary discipline — additions in same commit as source-code edit introducing the term; no deferred "documentation pass" — Chunk 1 — Status: Complete (added Step 5 to implementation-complete.md mirroring planning-complete Step 5; per-step discipline articulated)
- [ ] REQ-021: `agent-engineering/README.md` Skills section updates (sdd-flow Step 4 state machine + per-slice integration) + 0.4.0 version + SDD 2.0.0+ minimum dependency clause; repo-root `README.md` Available Plugins note — Chunk 5 — Status: Not Started
- [x] REQ-022: `## Slice Progress` table schema (columns `SLICE-ID | Name | Status | Acceptance check | Test result | Notes`; states `Not Started`/`In Progress`/`Acceptance Check Passing`/`Complete`; `/implementation-start` scaffolds; `/slice-retro` updates Status/Test result/Notes only; SLICE-XXX uniqueness invariant) — Chunk 2 — Status: Complete (binding schema documented in slice-start.md / slice-review.md / slice-commit.md; column-write authority in slice-retro.md Step 8; FIRST-WRITE-WINS in slice-start.md Step 5/6)
- [~] REQ-023: `sdd-flow` Phase Detection legacy-path fallback + resume rules for `## Awaiting Slicing Decision` and `## Recommended Re-planning` — Chunk 4a — Status: Partial (legacy-path fallback DONE in SKILL.md Phase Detection Priority — emits migration prompt directing user to `/sdd-migrate-layout` when `SDD/prompts/context-management/progress.md` or `SDD/prompts/PROMPT-*.md` exist while `SDD/orchestration/progress.md` does not. Resume rules for `## Awaiting Slicing Decision` and `## Recommended Re-planning` deferred to Chunk 4b which owns Step 4 substantive surgery and the corresponding progress.md block writers.)
- [x] REQ-024: Slice-ID args validated against `^SLICE-\d{3}$` before path interpolation (path-traversal prevention) — Chunk 2 — Status: Complete (Slice-ID Validation section in all four slice-*.md files)
- [x] REQ-025: Slice-command flag conventions (full inventory: `--resume`, `--force`, `--reconcile-ledger`, `--replan`, `--from-slice`, `--override-replan`; semantics, defaults, supervised-vs-autonomous, validation) — Chunk 2 — Status: Complete (Flag Inventory tables in slice-start.md / slice-review.md / slice-retro.md / slice-commit.md; orchestrator-flag boundary documented in slice-retro.md)
- [x] REQ-025a: `/slice-retro --reconcile-ledger` 8-step algorithm (manual-edit preservation) — Chunk 2 — Status: Complete (sdd/commands/slice-retro.md `--reconcile-ledger` Mode section)
- [ ] REQ-026: Cross-plugin version coupling README cross-references (sdd ↔ agent-engineering); FAIL-009 surfaced as warning — Chunk 5 — Status: Not Started

#### Non-Functional Requirements (SEC-XXX, UX-XXX)

- [x] SEC-001: `/slice-commit` and `/sdd-migrate-layout` MUST NOT bypass git hooks (no `--no-verify`, no force flags) — Chunks 2 + 3 — Status: Complete (slice-commit.md Step 6/7 + sdd-migrate-layout.md safety-posture preamble + Step 6 commit-policy notes; closing-oracle grep for `no-verify` shows only project-policy-prohibition statements, no actual flag usage)
- [x] SEC-002: `/sdd-migrate-layout` active-flow refusal + fail-closed posture on parse failure — Chunk 3 — Status: Complete (sdd-migrate-layout.md Step 3a–3c: parse `## Phase:`/`## Awaiting `/`## Recommended Re-planning`/`## PARTIAL:` headings, three-way classification with case-iii fail-closed; `--force-no-active` documented as override flag)
- [x] SEC-003: Slice-ID inputs validated per REQ-024 (path-traversal prevention) — Chunk 2 — Status: Complete (Slice-ID Validation section in all four slice-*.md files)
- [ ] SEC-004: No new credentials/secrets/PII surfaces; transcript-redaction posture inherited (out of scope) — Chunk 1 (acknowledgment in tracker) — Status: Not Started
- [x] UX-001: `/slice-*` inert message names field/required-value/alternative-action; friendly + self-documenting — Chunk 2 — Status: Complete (Inert-Mode Gate Step 2 in all four slice-*.md emits REQ-007 verbatim message naming field, value, and alternative)

### Edge Case Implementation

- [x] EDGE-001: `/sdd-migrate-layout` re-run when already migrated (idempotent "already migrated" exit) — Chunk 3 — Status: Complete (sdd-migrate-layout.md Step 2 four-state machine: State 2 "Already migrated" → "No migration needed; layout is already at 2.0.0 conventions." exit 0; Step 9 post-migration verification re-runs detection)
- [x] EDGE-002: `/slice-*` invoked when active SPEC has `delivery_mode: whole-feature` or no field (inert message per REQ-007/UX-001) — Chunk 2 — Status: Complete (Inert-Mode Gate in all four slice-*.md files)
- [x] EDGE-003: `/slice-review` invoked when target slice has no implementation yet (graceful empty-set finding) — Chunk 2 — Status: Complete (slice-review.md Step 3 — `Not Started` row triggers EDGE-003 refusal message)
- [ ] EDGE-004: User repos with CLAUDE.md hardcoding old paths (out-of-scope; reminder in `/sdd-migrate-layout` output + sdd/README.md) — Chunk 5 — Status: Not Started
- [ ] EDGE-005: Practicality gate fires (single-MODULE OR every-decomposition-is-build-then-test) — Chunk 1 — Status: Not Started
- [ ] EDGE-006: Re-planning recommendation fired but user runs `/sdd-flow continue` without flag (informative refusal listing `--replan` / `--override-replan`) — Chunk 4b — Status: Not Started
- [x] EDGE-007: RETROSPECTIVE artifact written but ledger update fails (recovery via `--reconcile-ledger` per REQ-025a) — Chunk 2 — Status: Complete (slice-retro.md `--reconcile-ledger` Mode + Two-Write Ordering Invariant section)
- [ ] EDGE-008: macOS APFS case-insensitive filesystem (this-repo deviation; documented in sdd/README.md migration section) — Chunk 5 — Status: Not Started
- [ ] EDGE-009: Spec without `delivery_mode:` field (defaults silently to `whole-feature` per OQ-3) — Chunk 1 — Status: Not Started
- [x] EDGE-010: Multiple `Not Started` slices when `/slice-start` has no arg (prompt user; never silently picks) — Chunk 2 — Status: Complete (slice-start.md Step 4 — multi-row branch prompts user / autonomous halt)
- [x] EDGE-011: `## Slice Progress` table column-write authority (`/implementation-start` scaffolds; `/slice-retro` updates Status/Test result/Notes only) — Chunk 2 — Status: Complete (column-write authority documented in slice-start.md schema + slice-retro.md Step 8)
- [x] EDGE-012: `/slice-start` re-invocation while another slice is `In Progress` (refusal + `--resume` flag) — Chunk 2 — Status: Complete (slice-start.md Step 5 EDGE-012 conflict refusal + Flag Inventory `--resume`)
- [x] EDGE-013: `/slice-start` re-invocation on a slice already `Complete` (refusal + `--force` flag; autonomous-vs-supervised semantics) — Chunk 2 — Status: Complete (slice-start.md Step 6 EDGE-013 + autonomous `## Awaiting Re-start Decision` halt + Flag Inventory `--force`)
- [x] EDGE-014: `/slice-retro` re-invocation when retrospective already exists (loud refusal; `--reconcile-ledger` is escape hatch) — Chunk 2 — Status: Complete (slice-retro.md Step 5 EDGE-014 refusal with REQ-005 verbatim message + escape hatches)
- [x] EDGE-015: `/sdd-migrate-layout` invoked when `progress.md` cannot be parsed (fail-closed refusal per SEC-002) — Chunk 3 — Status: Complete (sdd-migrate-layout.md Step 3c case-iii: "Refusing migration: progress.md exists but cannot be parsed." with "Failing closed to avoid data-loss-by-misclassification" rationale; `--force-no-active` override documented)

### Failure Scenario Handling

- [x] FAIL-001: `/sdd-migrate-layout` partially completes then errors mid-move (manual rollback documented; `git mv` history-preserving) — Chunk 3 — Status: Complete (sdd-migrate-layout.md Step 7 partial-migration recovery: three options — Option A `git reset --hard HEAD` simplest, Option B per-move inverse `git mv` recipe computed dynamically, Option C diagnose-and-resume via `--resume-partial`)
- [x] FAIL-002: User installs SDD 2.0.0 with active in-flight flow under old layout (active-flow refusal halts; sdd-flow Phase Detection legacy-path fallback recommends migration) — Chunk 4a — Status: Complete (SKILL.md Phase Detection Priority now opens with a "Old layout detected" rule that halts and emits a directive to run `/sdd-migrate-layout` then re-run `/sdd-flow continue`; references the migration helper's own active-flow gating)
- [x] FAIL-003: Slice retrospective writes RETROSPECTIVE artifact then disk fills before ledger update (recovery via `--reconcile-ledger`) — Chunk 2 — Status: Complete (slice-retro.md Two-Write Ordering Invariant section + `--reconcile-ledger` Mode 8-step algorithm)
- [ ] FAIL-004: Per-slice review iteration cap (3) exhausted with HIGH count not strictly decreasing (halt slice's loop, route to ledger; halt flow under `--skip-slice-checkpoints`) — Chunk 4b — Status: Not Started
- [x] FAIL-005: `/sdd-migrate-layout` invoked on Windows in cmd.exe or PowerShell (bash-detection refusal with "run from Git Bash" guidance) — Chunk 3 — Status: Complete (sdd-migrate-layout.md Step 0 first-action bash detection: `command -v bash >/dev/null 2>&1 || { echo "ERROR: /sdd-migrate-layout requires bash. On Windows, run from Git Bash."; exit 1; }`)
- [ ] FAIL-006: Hook path constant updated but migration not yet run (or vice versa) (hook-skew documented; no auto-recovery, manual remediation) — Chunk 1 — Status: Not Started
- [x] FAIL-007: `/slice-start` invoked but `## Slice Progress` table is missing (refusal + recommend re-running `/implementation-start`) — Chunk 2 — Status: Complete (slice-start.md Step 3 — verbatim FAIL-007 refusal message)
- [x] FAIL-008: `/sdd-migrate-layout` parse-failure during active-flow refusal check (fail-closed refusal per SEC-002) — Chunk 3 — Status: Complete (sdd-migrate-layout.md Step 3c case-iii fail-closed branch — same control-flow surface as EDGE-015, refusal message includes path, parser error, and remediation paths including `--force-no-active` override)
- [ ] FAIL-009: Cross-plugin version mismatch — SDD 2.x with agent-engineering 0.3.x (FAIL-009 surfaced as warning via README cross-refs per REQ-026) — Chunk 5 — Status: Not Started

### Module Implementation (MODULE-XXX)

- [ ] MODULE-001: `delivery_mode` runtime branch (REQ-001, REQ-002) — Chunk 1 — Status: Not Started
- [x] MODULE-002: Slice-command primitives (`/slice-start`, `/slice-review`, `/slice-retro`, `/slice-commit`) (REQ-003…007, REQ-022, REQ-024, REQ-025, REQ-025a, EDGE-002/010/011/012/013/014, FAIL-003/007) — Chunk 2 — Status: Complete (sdd/commands/slice-start.md, slice-review.md, slice-retro.md, slice-commit.md authored; all four pass closing oracles: inert-mode phrase present, retro emits `## Recommended SPEC Amendments` + `## Recommended Re-planning` headers, zero legacy-path hits, flag inventory documented, `^SLICE-\d{3}$` regex literal in each file, `LEARNINGS-FEATURE-[feature-name]` placeholder consistency)
- [ ] MODULE-003: Slice-integrity review checks (REQ-009, REQ-010) — Chunk 1 — Status: Not Started
- [ ] MODULE-004: Practicality gate (REQ-001, REQ-011, EDGE-005) — Chunk 1 — Status: Not Started
- [x] MODULE-005: Migration helper (`/sdd-migrate-layout`) (REQ-008, SEC-001, SEC-002, EDGE-001, EDGE-008, EDGE-015, FAIL-001, FAIL-002, FAIL-005, FAIL-008) — Chunk 3 — Status: Complete (sdd/commands/sdd-migrate-layout.md authored; closing-oracle gate passed: file exists, all refusal-message strings present, dry-run-by-default documented, idempotence in Step 2 + Step 9, partial-migration recovery in Step 7, bash detection in Step 0, hardcoded move-set paths per ADR 0002 / research Branch 4. EDGE-008 + FAIL-002 are touched by this command's behavior — full closure is in Chunks 4a/5)
- [ ] MODULE-006: sdd-flow Step 4 per-slice state machine (REQ-012, REQ-013, REQ-014, REQ-015, REQ-022, REQ-023, REQ-025, EDGE-006, FAIL-004) — Chunk 4b — Status: Not Started
- [ ] MODULE-007: Directory restructure + rename propagation (REQ-002, REQ-003, REQ-005, REQ-016, REQ-017, REQ-022, FAIL-006) — Chunk 1 (paths) + Chunks 2/3 (new commands emit new paths) — Status: Not Started
- [ ] MODULE-008: Documentation surface + version manifests (REQ-018, REQ-019, REQ-020, REQ-021, REQ-026, FAIL-009, RISK-007) — Chunk 5 — Status: Not Started

### Risk Tracking

- [ ] RISK-001 (high): Partial restructure on commit — closing-oracle grep on every modified file before declaring "verified" — Chunk 1 closing-oracle gate
- [ ] RISK-002 (medium): Mode-routing bug — bit-for-bit-preservation invariant and smoke-flow primary check — Chunks 1 + 4b
- [x] RISK-003 (high): Migration helper destructive on user repo — active-flow refusal + idempotence + bash-detection — Chunk 3 (mitigations in sdd-migrate-layout.md: dry-run-by-default safety stance, Step 0 bash detection, Step 2 four-state classification, Step 3 active-flow fail-closed, Step 4 clean-tree precondition, Step 7 rollback recipe)
- [ ] RISK-004 (medium): Marketplace + manifest drift — `grep -n version` across all four files in same commit — Chunk 5
- [ ] RISK-005 (low): User-authored CLAUDE.md / AGENTS.md staleness — README + migration-output reminder; no auto-edit — Chunk 5
- [ ] RISK-006 (high): Recursion-trap during this run — every subagent prompt embeds the warning verbatim — All chunks (binding)
- [ ] RISK-007 (medium): Plugin version drift between SDD 2.x and agent-engineering 0.3.x — README cross-references + marketplace.json release notes — Chunk 5

---

## Chunk Plan

Six subagents total (init + 5 implementation chunks). Dependency chain: **init → 1 → 2 → 3 → 4a → 4b → 5**. Each chunk is a fresh subagent context with its own bounded prompt, the recursion-trap warning verbatim, the Step A locked-region prohibition verbatim, and a closing-oracle grep gate it MUST run before declaring done.

### Chunk 1 — Foundation: paths, modes, gates, glossary, hook

**REQs:** REQ-001, REQ-002, REQ-009, REQ-010, REQ-011, REQ-016, REQ-017, REQ-020
**EDGEs/FAILs touched:** EDGE-005, EDGE-008 (deferred README content to Chunk 5; spec entry preserved here), EDGE-009, FAIL-006
**Files modified:**
- `sdd/commands/planning-start.md` (line 271 frontmatter prose; Step 6 line 305+ allowed region only — lines 64–204 + 375–379 OFF LIMITS)
- `sdd/commands/implementation-start.md` (mode-aware tracker scaffolding; per-slice `## Slice Progress` template; preserve whole-feature behavior bit-for-bit)
- `sdd/commands/critical-review.md` (insert "Slice Integrity (per-slice mode only)" sub-section between lines 103–110 and 112–117)
- `sdd/commands/spec-review-panel.md` (specialist 4.7 + `#### Slice Integrity Findings` sub-header at lines 230–244, conditionally rendered)
- All other `sdd/commands/*.md` (path-only updates: `prompts/` → `implementation/` + `orchestration/`; `PROMPT-XXX` → `IMPLEMENTATION-PLAN-XXX`; `implementation-complete/` → `summaries/`)
- `sdd/hooks/log_subagent_call.py` line 18 (`LOG_SUBDIR` constant)
- `flow-state/SDD/UBIQUITOUS_LANGUAGE.md` (only if a new term is introduced; same-commit discipline per REQ-020)

**Closing-oracle greps (Chunk 1 MUST run all and confirm zero hits where required):**
```bash
# REQ-016 path consistency:
grep -rn 'prompts/context-management/' sdd/commands/ sdd/hooks/  # zero hits except in /sdd-migrate-layout itself (Chunk 3)
grep -rn 'PROMPT-' sdd/commands/ sdd/hooks/                      # zero hits except in /sdd-migrate-layout itself (Chunk 3)
grep -rn 'implementation-complete/' sdd/commands/                 # zero hits
grep -n 'LOG_SUBDIR' sdd/hooks/log_subagent_call.py              # shows: Path("SDD") / "orchestration" / "subagent-calls"
# Locked-region oracle:
diff <(git show HEAD:sdd/commands/planning-start.md | sed -n '64,204p;375,379p') \
     <(sed -n '64,204p;375,379p' sdd/commands/planning-start.md)  # zero diff
# Spec template preservation:
grep -n 'delivery_mode:' sdd/commands/planning-start.md          # locked line 69 unchanged
```

### Chunk 2 — New slice commands

**REQs:** REQ-003, REQ-004, REQ-005, REQ-006, REQ-007, REQ-022, REQ-024, REQ-025, REQ-025a
**Touched EDGEs/FAILs:** EDGE-002, EDGE-003, EDGE-007, EDGE-010, EDGE-011, EDGE-012, EDGE-013, EDGE-014, FAIL-003, FAIL-007, SEC-001, SEC-003, UX-001
**Files created:**
- `sdd/commands/slice-start.md`
- `sdd/commands/slice-review.md`
- `sdd/commands/slice-retro.md`
- `sdd/commands/slice-commit.md`

**CRITICAL header-string contract (downstream Chunk 4b matches against these EXACT strings):**
- `## Recommended SPEC Amendments`
- `## Recommended Re-planning`

`/slice-retro` MUST emit retrospective sections with these exact header strings (no variants like `## SPEC Amendments` or `## Re-planning Recommendations`). Chunk 4b's matcher is keyed to these literal strings.

**Closing-oracle greps for Chunk 2:**
```bash
# Each new command file exists with frontmatter:
ls sdd/commands/slice-{start,review,retro,commit}.md
head -10 sdd/commands/slice-start.md  # check frontmatter shape (allowed-tools, description)
# Inert-mode message string present:
grep -l 'delivery_mode: per-slice' sdd/commands/slice-*.md       # all four files
grep -l 'requires `delivery_mode: per-slice`' sdd/commands/slice-*.md  # all four
# Header strings exact for Chunk 4b dependency:
grep -n '## Recommended SPEC Amendments' sdd/commands/slice-retro.md   # exactly 1 hit
grep -n '## Recommended Re-planning' sdd/commands/slice-retro.md       # exactly 1 hit
# Slice-ID validation present:
grep -n '\^SLICE-\\\\d{3}\$' sdd/commands/slice-*.md                   # at least 4 hits
# Step A locked region not violated (no chunk modifies planning-start.md from Chunk 2):
git diff sdd/commands/planning-start.md                          # zero diff (Chunk 2)
# No --no-verify in /slice-commit (SEC-001):
grep -n 'no-verify' sdd/commands/slice-commit.md                 # zero hits
# Heredoc commit-message construction (REQ-006):
grep -n "cat <<'EOF'" sdd/commands/slice-commit.md               # at least 1 hit
```

### Chunk 3 — Migration helper

**REQs:** REQ-008
**Touched EDGEs/FAILs:** EDGE-001, EDGE-008, EDGE-015, FAIL-001, FAIL-002, FAIL-005, FAIL-008, SEC-001, SEC-002
**Files created:**
- `sdd/commands/sdd-migrate-layout.md`

**Closing-oracle greps for Chunk 3:**
```bash
# Command file exists:
ls sdd/commands/sdd-migrate-layout.md
# Refusal-message strings present:
grep -n 'Could not determine flow status' sdd/commands/sdd-migrate-layout.md
grep -n 'Both old and new layouts contain content' sdd/commands/sdd-migrate-layout.md
grep -n 'On Windows, run from Git Bash' sdd/commands/sdd-migrate-layout.md
grep -n 'already migrated\|nothing to migrate' sdd/commands/sdd-migrate-layout.md
# Move-set matches research/proposal Directory Layout section:
grep -n 'git mv' sdd/commands/sdd-migrate-layout.md              # the documented set
# No --no-verify or force flags (SEC-001):
grep -n 'no-verify\|force' sdd/commands/sdd-migrate-layout.md    # only the active-flow-refusal verb "force", not a flag
# Bash detection present:
grep -n 'BASH_VERSION\|bash --version\|/bin/bash' sdd/commands/sdd-migrate-layout.md
```

### Chunk 4a — SKILL.md mechanical (path-contract + Phase Detection Priority)

**REQs:** REQ-011 (partial — mechanical layer), REQ-023, FAIL-002
**Files modified:**
- `agent-engineering/skills/sdd-flow/SKILL.md`:
  - Artifact Paths Contract table (~line 73)
  - Directory Structure tree (~line 94)
  - Subagent Path Rules section (~line 138)
  - Phase Detection Priority section (~line 636 — adds legacy-path fallback rule and resume rules for `## Awaiting Slicing Decision` / `## Recommended Re-planning`)
  - Backward-compatibility note (legacy-layout detection prompts user to run `/sdd-migrate-layout` before continuing — references FAIL-002)

**Closing-oracle greps for Chunk 4a:**
```bash
# Path contract uses new layout exclusively:
grep -n 'prompts/\|PROMPT-' agent-engineering/skills/sdd-flow/SKILL.md    # zero hits (per REQ-016)
grep -n 'IMPLEMENTATION-PLAN-' agent-engineering/skills/sdd-flow/SKILL.md  # multiple hits
grep -n 'SDD/implementation/' agent-engineering/skills/sdd-flow/SKILL.md   # multiple hits
grep -n 'SDD/orchestration/' agent-engineering/skills/sdd-flow/SKILL.md    # multiple hits
# Phase Detection legacy-path fallback present:
grep -n 'sdd-migrate-layout' agent-engineering/skills/sdd-flow/SKILL.md    # at least 1 hit (the fallback prompt)
grep -n 'Awaiting Slicing Decision' agent-engineering/skills/sdd-flow/SKILL.md  # at least 1 hit
grep -n 'Recommended Re-planning' agent-engineering/skills/sdd-flow/SKILL.md    # at least 1 hit
```

### Chunk 4b — SKILL.md substantive (Step 4 per-slice state machine + checkpoint axis + re-planning + iteration cap)

**REQs:** REQ-012, REQ-013, REQ-014, REQ-015, REQ-024 (slice-boundary checkpoint axis: `--skip-slice-checkpoints` flag)
**Touched EDGEs/FAILs:** EDGE-006, FAIL-004
**Files modified:**
- `agent-engineering/skills/sdd-flow/SKILL.md`:
  - Step 4 routes by `delivery_mode:` (whole-feature flow unchanged bit-for-bit; per-slice flow runs the per-slice cycle)
  - Per-slice review iteration cap = 3 (mirrors Step 3c)
  - Retro recommendations matcher (matches `## Recommended SPEC Amendments` + `## Recommended Re-planning` from Chunk 2's `/slice-retro` exactly)
  - Re-planning halt-even-under-skip-checkpoints
  - Slice subagents receive only the ledger
  - `--skip-slice-checkpoints` flag (default ON in per-slice mode)
  - `## Arguments` section flag inventory matches REQ-025

**Closing-oracle greps for Chunk 4b:**
```bash
# Header strings exact match against Chunk 2's emissions:
grep -n '## Recommended SPEC Amendments' agent-engineering/skills/sdd-flow/SKILL.md   # at least 1 hit
grep -n '## Recommended Re-planning' agent-engineering/skills/sdd-flow/SKILL.md       # at least 1 hit
# Flag inventory in Arguments section:
grep -n -- '--skip-slice-checkpoints\|--replan\|--from-slice\|--override-replan' agent-engineering/skills/sdd-flow/SKILL.md
# Per-slice cycle steps named:
grep -n '4a → 4b → 4c → 4c.5 → 4c.6\|per-slice cycle' agent-engineering/skills/sdd-flow/SKILL.md
# Iteration cap of 3 referenced:
grep -n 'iteration cap\|cap is 3\|cap = 3' agent-engineering/skills/sdd-flow/SKILL.md
# Whole-feature path still present (bit-for-bit preservation invariant):
grep -n 'whole-feature' agent-engineering/skills/sdd-flow/SKILL.md
```

### Chunk 5 — Versioning + READMEs + cross-plugin coupling

**REQs:** REQ-018, REQ-019, REQ-021, REQ-026
**Touched EDGEs/FAILs:** EDGE-004, EDGE-008, FAIL-009, RISK-004, RISK-005, RISK-007
**Files modified:**
- `sdd/.claude-plugin/plugin.json` (version → 2.0.0)
- `.claude-plugin/marketplace.json` (sdd entry → 2.0.0; agent-engineering entry → 0.4.0)
- `agent-engineering/.claude-plugin/plugin.json` (version → 0.4.0)
- `sdd/README.md` (two-workflow restructure: decision aid + Whole-feature + Per-slice + Migration/Changelog including `/sdd-migrate-layout` usage, EDGE-008 case-collision note, EDGE-004 user-CLAUDE staleness reminder, agent-engineering 0.4.0+ minimum cross-ref per REQ-026)
- `agent-engineering/README.md` (sdd-flow Step 4 state machine + per-slice integration; SDD 2.0.0+ minimum dependency clause per REQ-026)
- `README.md` (Available Plugins section: `delivery_mode: per-slice` opt-in note + version-coupling note per REQ-026)

**Closing-oracle greps for Chunk 5:**
```bash
# Versions match across all four locations:
grep -n '"version"' sdd/.claude-plugin/plugin.json                   # 2.0.0
grep -n '"version"' agent-engineering/.claude-plugin/plugin.json     # 0.4.0
grep -n '"version"' .claude-plugin/marketplace.json                  # 2.0.0 (sdd) and 0.4.0 (agent-engineering)
# README two-workflow structure (sdd):
grep -c 'prompts/' sdd/README.md                # 0
grep -c 'PROMPT-' sdd/README.md                 # 0
grep -c 'IMPLEMENTATION-PLAN' sdd/README.md     # ≥2
grep -c 'implementation/' sdd/README.md         # ≥4
grep -c 'orchestration/' sdd/README.md          # ≥4
grep -c 'slices/' sdd/README.md                 # ≥2
grep -c 'agent-engineering' sdd/README.md       # ≥1 (REQ-026 cross-ref)
# Cross-plugin coupling cross-references:
grep -n 'agent-engineering 0.4.0\|0.4.0+' sdd/README.md
grep -n 'SDD 2.0.0\|2.0.0+' agent-engineering/README.md
# EDGE-008 + EDGE-004 reminders:
grep -n 'case-insensitive\|APFS' sdd/README.md
grep -n 'CLAUDE.md\|AGENTS.md' sdd/README.md    # staleness reminder
```

---

## Context Management

### Current Utilization

- Context Usage: ~5% post-init (init subagent only loaded spec excerpts + progress.md + implementation-start.md template). Target: <40% throughout chunks.
- Each chunk subagent runs in fresh context with bounded prompt (≤200 words). Chunk subagents never load this entire tracker — they receive only their own chunk's REQ/EDGE/FAIL list, file list, and closing-oracle grep block.

### Essential Files Loaded

- `flow-state/SDD/requirements/SPEC-001-vertical-slicing-step-c.md`:lines 97–120 (REQ inventory; sampled — full file 41k tokens, exceeds budget)
- `flow-state/SDD/prompts/context-management/progress.md` (orchestration state)
- `sdd/commands/implementation-start.md`:100–230 (tracker template)

### Files Delegated to Subagents

Per chunk above. Each chunk subagent reads only its file set; init subagent does not pre-fetch chunk-owned files.

---

## Implementation Progress

### Completed Components

- **Chunk 1 (2026-05-05) — Foundation: paths, modes, gates, glossary, hook.** Completed REQs: REQ-001, REQ-002, REQ-009, REQ-010, REQ-011, REQ-016 (sdd/commands + sdd/hooks scope; SKILL.md is Chunk 4a), REQ-017, REQ-020. Files modified:
  - `sdd/commands/planning-start.md` — frontmatter prose extended at allowed line 271 (delivery_mode value validation); Step 6 extended at allowed line 305+ with new sub-steps 7 (delivery_mode validation gate, REQ-001) and 8 (Practicality Check / practicality gate, REQ-011, EDGE-005). Locked region (lines 64–204 + locked Quality Checklist items) verified untouched via diff against ffeec97.
  - `sdd/commands/implementation-start.md` — added step 4 (Read delivery_mode from spec frontmatter, REQ-002) to Initial Context Load with full validation; added `**Delivery mode:**` field to tracker template Executive Summary; added new `## Slice Progress` section (per-slice mode only) at bottom of template with binding column schema (`SLICE-ID | Name | Status | Acceptance check | Test result | Notes`) and the four-state status enum (`Not Started`, `In Progress`, `Acceptance Check Passing`, `Complete`); added new step 2 (Branch on delivery_mode) to Implementation Process directing developer to use `/slice-*` commands in per-slice mode; renumbered subsequent steps.
  - `sdd/commands/critical-review.md` — inserted new "Slice Integrity (per-slice mode only)" sub-section between "Specification Weaknesses" and "Research Alignment Issues" in Section 3 (REQ-009). Verbatim slice-integrity blockquote text from research Branch 5 + five gated check items.
  - `sdd/commands/spec-review-panel.md` — inserted new specialist 4.7 "Slice Integrity Specialist" before 4.6 (REQ-010) with self-gating activation text, 11-term vocabulary payload, 7 named anti-patterns, output schema. Updated deliverable Document Structure to include conditional `#### Slice Integrity Findings` sub-header rendered iff `delivery_mode: per-slice`.
  - `sdd/commands/implementation-complete.md` — added new step 5 "Capture Glossary Deltas Introduced by the Implementation" before Phase Transition (REQ-020), mirroring `/sdd:planning-complete` Step 5 wording with per-step timing nuance.
  - **Path migration (REQ-016) — all SDD plugin command files:** batch-substituted via perl (`SDD/prompts/context-management/...` → `SDD/orchestration/...`; sub-paths to `SDD/orchestration/{compacted,subagent-calls,counters}`; `SDD/prompts/PROMPT-...` → `SDD/implementation/IMPLEMENTATION-PLAN-...`; `SDD/prompts/implementation-complete/...` → `SDD/implementation/summaries/...`; `SDD/prompts/test-audits/...` → `SDD/implementation/test-audits/...`; bare `PROMPT-` and bare `PROMPT` → `IMPLEMENTATION-PLAN-` / `IMPLEMENTATION-PLAN`). Files affected: research-start.md, research-complete.md, research-compact.md, planning-start.md, planning-complete.md, planning-compact.md, implementation-start.md, implementation-complete.md, implementation-compact.md, implementation-test.md, code-review.md, critical-review.md, adhoc-compact.md, continue.md.
  - `sdd/hooks/log_subagent_call.py` line 18 (REQ-017): `LOG_SUBDIR` updated from `Path("SDD") / "prompts" / "context-management" / "subagent-calls"` to `Path("SDD") / "orchestration" / "subagent-calls"`.
  - **No glossary changes for this chunk** — every term used in the new prose (delivery_mode enum values, vertical slice, horizontal layer, concentrated function, thread line, end-to-end happy path, acceptance check, slice sequence rationale, practicality gate, awaiting slicing decision, slicing not applicable, slice-integrity smell, four-state status enum) is already in `SDD/UBIQUITOUS_LANGUAGE.md` per the planning-phase glossary update.
  - **Closing-oracle gate passed:** `grep -rn 'prompts/context-management' sdd/commands/ sdd/hooks/` → 0 hits; `grep -rn 'PROMPT' sdd/commands/` → 0 hits; `grep -rn 'implementation-complete/' sdd/commands/` → 0 hits; `grep -n 'LOG_SUBDIR' sdd/hooks/log_subagent_call.py` → orchestration path; `diff <(git show ffeec97:sdd/commands/planning-start.md | sed -n '64,204p') <(sed -n '64,204p' sdd/commands/planning-start.md)` → no diff; locked Quality Checklist items (originally lines 375–379, now at lines 398–402 due to upstream insertions) preserved verbatim via diff vs HEAD.

### In Progress

- **Current Focus:** Init complete; awaiting Chunk 1 dispatch by orchestrator.
- **Files Being Modified:** None (init phase).
- **Next Steps:** Orchestrator dispatches Chunk 1 subagent (Foundation: paths, modes, gates, glossary, hook).

### Blocked/Pending

- (none)

---

## Test Implementation

### Web-Facing Behavior

- **Feature has web-facing behavior (UI, JS, HTMX, browser flows):** No
- **E2E tests required:** N/A — markdown command files and a Python hook; no UI, no client-side JS, no browser surface. Verification is manual smoke flows + closing-oracle greps per REQ-016 / REQ-018 / REQ-019.

### Unit Tests

- N/A. No source-code unit-testable surface introduced. The `log_subagent_call.py` line 18 change is a single-line constant update; manual verification via `grep -n LOG_SUBDIR sdd/hooks/log_subagent_call.py` is the project convention for this hook.

### Integration Tests

- N/A. No API surface.

### E2E Tests (Playwright — if web-facing)

- N/A. See "Web-Facing Behavior" above.

### Manual Smoke Flows (replaces automated tests for this feature)

Per spec Validation Strategy:
- [ ] Whole-feature smoke flow: `/sdd-flow "<simple-feature>"` with `delivery_mode: whole-feature` runs the existing horizontal flow with all path emissions on the new layout. Bit-for-bit preservation invariant verified.
- [ ] Per-slice smoke flow: `/sdd-flow "<sliceable-feature>"` with `delivery_mode: per-slice` populates `## Delivery Slices`, runs Step 4 state machine across multiple SLICE-XXX rows, exits cleanly.
- [ ] Migration helper smoke flow: on a synthetic repo with old layout, `/sdd-migrate-layout` runs idempotently, refuses on active phase, fails closed on unparseable progress.md, refuses on partial migration.
- [ ] Per-EDGE manual verification: each EDGE-XXX has a documented test approach in spec lines 184–270; Chunk subagents validate per-EDGE behavior locally and the closing-oracle gate confirms structural correctness.
- [ ] Closing-oracle grep gate: every modified file passes its grep block before chunk subagent declares done.
- [ ] Locked-region diff oracle: `git diff sdd/commands/planning-start.md` against HEAD shows zero changes in lines 64–204 + 375–379.

### Test Coverage

- Unit Tests: N/A (markdown commands + 1-line hook change)
- Integration Tests: N/A (no API surface)
- E2E Tests: N/A (no web-facing behavior)
- Manual smoke flows: 4 (whole-feature, per-slice, migration helper, per-EDGE checklist) + closing-oracle grep gates per chunk
- Target Coverage: as specified in SPEC Validation Strategy (manual + grep oracles)
- Coverage Gaps: none anticipated; spec's Manual Verification block enumerates oracles for every changed surface

---

## Technical Decisions Log

### Architecture Decisions (already captured as ADRs at research-time)

- **ADR 0001** (`SDD/adr/0001-merged-codebase-with-delivery-mode-frontmatter.md`): merged codebase with `delivery_mode:` runtime branch (rejected fork-plugin / companion-plugin / fork-only-sdd-flow alternatives). Binding for every chunk.
- **ADR 0002** (`SDD/adr/0002-restructure-sdd-artifact-directory-layout.md`): directory restructure (`prompts/` → `implementation/` + `orchestration/`) coupled with `PROMPT-XXX` → `IMPLEMENTATION-PLAN-XXX` rename, both shipped via the same migration helper in one major-version bump. Binding for Chunks 1, 3, 4a, 5.

### Implementation Deviations

- (none yet — chunks have not started)
- This-repo deviation: artifact files live under `flow-state/SDD/...` (case-collision avoidance); in-body refs use `SDD/...`. Documented at top of this tracker. Not a deviation from spec — spec explicitly accommodates this convention.

---

## Performance Metrics

- **N/A.** This feature is markdown command files + 1-line hook change. There is no performance surface — no request-handling latency, no throughput target, no memory/CPU constraint. The spec's Validation Strategy explicitly states "perf N/A with rationale." This section is preserved in the template for completeness; any future feature with a perf surface should populate it.

---

## Security Validation

- [ ] SEC-001 acknowledged: `/slice-commit` and `/sdd-migrate-layout` use plain `git commit` and `git mv`; no `--no-verify`, no force flags. Closing-oracle greps in Chunks 2 + 3 confirm.
- [ ] SEC-002 acknowledged: `/sdd-migrate-layout` active-flow refusal + fail-closed posture on parse failure. Closing-oracle greps in Chunk 3 confirm refusal-message strings.
- [ ] SEC-003 acknowledged: Slice-ID inputs validated against `^SLICE-\d{3}$` before path interpolation. Closing-oracle grep in Chunk 2 confirms regex presence in all four `/slice-*` commands.
- [ ] SEC-004 acknowledged: No new credentials/secrets/PII surfaces. Transcript-redaction posture inherited (out of scope; documented in SPEC).
- [ ] Authorization checks: N/A. Markdown commands run in user's local environment under user's git credentials.
- [ ] Input validation: REQ-001 (`delivery_mode` enum), REQ-024 (SLICE-ID regex). All chunk closing-oracle greps confirm presence.

---

## Documentation Created

- [ ] REQ-019 — `sdd/README.md` two-workflow restructure (decision aid + Whole-feature + Per-slice + Migration/Changelog) — Chunk 5
- [ ] REQ-021 — `agent-engineering/README.md` Skills section (sdd-flow Step 4 state machine + per-slice) + 0.4.0 changelog + SDD 2.0.0+ minimum clause — Chunk 5
- [ ] REQ-021 — repo-root `README.md` Available Plugins note — Chunk 5
- [ ] REQ-026 — Cross-plugin version coupling cross-references in both READMEs — Chunk 5
- [ ] EDGE-008 — sdd/README.md migration section: case-insensitive FS note (APFS this-repo deviation) — Chunk 5
- [ ] EDGE-004 — sdd/README.md migration section: user-CLAUDE staleness reminder — Chunk 5
- [ ] (No new API documentation — markdown commands document themselves via `## Description` and `## Usage` frontmatter+body.)

---

## Session Notes

### Subagent Delegations

- 2026-05-05 init: This subagent (Step 4 init for `/sdd-flow`). Created tracker; appended Step 4 init transition block to `progress.md`. Bounded scope: 5–6 reads, ~2 writes.
- 2026-05-05 Chunk 1 (Foundation): No nested subagent delegations. All work done in main subagent context via Bash batch substitution (perl `-i -pe` for path migrations, single pass per regex family) and targeted Edit calls for context-sensitive insertions (new validation step, practicality gate, slice-integrity sub-sections, mode-aware tracker template, glossary discipline step). Closing-oracle gate ran inline via Bash before declaring done.

### Critical Discoveries

- (none yet — chunks have not started)

### Next Session Priorities

1. Orchestrator dispatches **Chunk 1 (Foundation)** subagent: paths/modes/gates/glossary/hook. Embed recursion-trap warning verbatim. Embed Step A locked-region prohibition verbatim. Closing-oracle gate before declaring done.
2. **Chunk 2 (New slice commands)** subagent (after Chunk 1 closing-oracle gate passes). CRITICAL: emit exact header strings `## Recommended SPEC Amendments` and `## Recommended Re-planning` for Chunk 4b's matcher.
3. **Chunk 3 (Migration helper)** subagent (after Chunk 2 closing-oracle gate passes).
4. **Chunk 4a (SKILL.md mechanical)** subagent.
5. **Chunk 4b (SKILL.md substantive)** subagent. Header-string match against Chunk 2's emissions is gating.
6. **Chunk 5 (Versioning + READMEs)** subagent.
7. Step 4 review/critical-review/completion/commit (post-chunks) per `/sdd-flow` Step 4d–4j.
