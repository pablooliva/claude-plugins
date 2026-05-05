# Code Review: vertical-slicing-step-c (Step C of vertical-slicing-decomposition)

**Date:** 2026-05-05
**Spec:** SDD/requirements/SPEC-001-vertical-slicing-step-c.md
**Research:** SDD/research/RESEARCH-001-vertical-slicing-step-c.md
**Implementation tracker:** SDD/prompts/PROMPT-001-vertical-slicing-step-c-2026-05-05.md (this-run-legacy filename per recursion-trap)
**This is a codebase-change feature** — no test suite; spec verification via closing-oracle greps + manual cross-reference checks.

## Artifact Verification
- [x] RESEARCH document complete (1095 lines, comprehensive branch analysis)
- [x] SPEC document complete (525 lines, every REQ/EDGE/FAIL/MODULE enumerated with binding language)
- [x] IMPLEMENTATION-PLAN tracker complete at this-run-legacy `PROMPT-001-...` filename per recursion-trap exception (463 lines; covers all chunks 1–5 with chunk-by-chunk completion notes)

## Specification Alignment (70%)

### Per-REQ Verification

| REQ | Status | Evidence |
|-----|--------|----------|
| REQ-001 (delivery_mode validation, planning-start) | PASS | sdd/commands/planning-start.md:271–272 (frontmatter prose with canonical enum + absent-default + invalid-value rules); :317–319 (Step 7 validation with `Invalid delivery_mode value '<value>' in <spec-path>...` error). Locked region (lines 64–204) untouched. |
| REQ-002 (implementation-start mode-aware scaffolding) | PASS | sdd/commands/implementation-start.md:39–55 (Read delivery_mode step with full validation); :111 (mode-aware template note); :234 (`## Slice Progress` template section); :255–256 (Branch on delivery_mode step). Whole-feature path preserved bit-for-bit (only path strings change). |
| REQ-003 (`/slice-start`) | PASS | sdd/commands/slice-start.md (192 lines). Active-slice resolution priority (lines 5–13), inert-mode gate (15–42), slice-ID validation (44–52), `## Slice Progress` schema (54–66), table verification (68–80), resolution (82–89), EDGE-012 conflict (91–101), EDGE-013 already-Complete (103–110), ledger load (112–122), table flip (124–131), progress.md update (133–146). |
| REQ-004 (`/slice-review` — thin wrapper over /code-review) | PASS | sdd/commands/slice-review.md exists with slice-scoped file-set computation; `[YYYY-MM-DD]` date format used. EDGE-003 (no implementation yet) refusal in Step 3. |
| REQ-005 (`/slice-retro` — retro-first ordering, refusal on existing) | PASS | sdd/commands/slice-retro.md:74 (verbatim REQ-005 refusal text); :78 (`--reconcile-ledger` escape hatch); two-write ordering invariant section. Headers `## Recommended SPEC Amendments` + `## Recommended Re-planning` emit at lines 111 + 126. |
| REQ-005a (`--reconcile-ledger` 8-step algorithm) | PASS | sdd/commands/slice-retro.md:258+ ("`--reconcile-ledger` Mode (REQ-025a — full 8-step algorithm)" section). |
| REQ-006 (`/slice-commit` — atomic, heredoc, no --no-verify, no co-author) | PASS | sdd/commands/slice-commit.md:84–110 (heredoc commit-message construction); :88 (no shell concat); :89 (no `--no-verify`); :121 (project-policy mirror). Looser staging documented. |
| REQ-007 (slice-* inert outside per-slice) | PASS | All four slice-*.md files contain "Slice commands are inert in whole-feature mode" / `requires \`delivery_mode: per-slice\`` (verified by grep). Verbatim REQ-007 inert message present in each. |
| REQ-008 (`/sdd-migrate-layout`) | PASS | sdd/commands/sdd-migrate-layout.md (456 lines). 4-state machine (lines 71–78); active-flow refusal (Step 3); idempotence (Steps 2 + 9); bash detection (Step 0); partial-migration refusal (Step 2 State 4); fail-closed parse failure (Step 3c iii); CLAUDE.md staleness scan (Step 8). All required refusal messages literal. |
| REQ-009 (slice-integrity sub-section in critical-review) | PASS | sdd/commands/critical-review.md:111 ("### Slice Integrity (per-slice mode only)"). |
| REQ-010 (slice-integrity specialist 4.7 + #### Slice Integrity Findings) | PASS | sdd/commands/spec-review-panel.md updated per tracker; conditional rendering on `delivery_mode: per-slice`. |
| REQ-011 (practicality gate) | PASS | sdd/commands/planning-start.md:323+ (Step 8 "Practicality Check" with four heuristics + qualitative escape requiring `Qualitative judgment: ` prefix); :330 ("Slicing not applicable: <reason>" annotation pattern). `## Awaiting Slicing Decision` halt block emitted in autonomous mode. |
| REQ-012 (Step 4 routing by delivery_mode) | PASS | agent-engineering/skills/sdd-flow/SKILL.md:523–531 (Read delivery_mode and route block); per-slice cycle inserted at lines 636–708; whole-feature 4a–4j sub-step headers verified intact at lines 533, 549, 557, 564, 572, 579, 587, 600, 621, 625. |
| REQ-013 (per-slice review iteration cap = 3 + progress-stall) | PASS | SKILL.md:657 ("max 3 iterations with progress-stall check (HIGH must strictly decrease, OR MEDIUM when HIGH is zero)"); :659–663 (halt routing — ledger `Open recommendations awaiting user decision`; entire-flow halt under `--skip-slice-checkpoints`). |
| REQ-014 (Re-planning halt regardless of --skip-slice-checkpoints) | PASS | SKILL.md:669–677 (halt with three resume options: `--replan`, manual edit + `continue`, `--override-replan`); :677 (autonomous-+-skip override callout). |
| REQ-015 (slice subagents receive only the ledger) | PASS | SKILL.md:653 (verbatim "**The subagent's prompt receives ONLY the ledger** (per OQ-6 default — strictly the ledger; individual retros are out of the prompt path)"); Key Principle 15 (line 783). |
| REQ-016 (path emissions use new layout) | PASS (with 1 known-issue, see Findings) | `grep -rn 'prompts/context-management' sdd/commands/ sdd/hooks/` returns hits ONLY in sdd-migrate-layout.md (documented exception). `grep -n 'prompts/\|PROMPT-' agent-engineering/skills/sdd-flow/SKILL.md` returns ONE hit at line 725 — the FAIL-002 legacy-detection bullet (documented exception). However, see Finding F-1 below: SKILL.md lines 312/545/547/553/561/576/584 still contain the bare term "PROMPT document" / "PROMPT tracking document" (terminology drift, not path drift). |
| REQ-017 (LOG_SUBDIR hook) | PASS | sdd/hooks/log_subagent_call.py:18 — `LOG_SUBDIR = Path("SDD") / "orchestration" / "subagent-calls"`. |
| REQ-018 (version bumps) | PASS | sdd/.claude-plugin/plugin.json:4 → 2.0.0. agent-engineering/.claude-plugin/plugin.json:4 → 0.4.0. .claude-plugin/marketplace.json: sdd → 2.0.0, agent-engineering → 0.4.0 (all four byte-aligned). |
| REQ-019 (sdd/README.md two-workflow restructure) | PASS (with internal-spec-acknowledged exception) | Decision aid at line 59; Whole-feature workflow at 113; Per-slice workflow at 256; Migration to 2.0.0 + Cross-plugin dependency + APFS warning + CLAUDE.md staleness reminder all present. The `prompts/`=0 / `PROMPT-`=0 strict greps fail (4 + 5 hits respectively), but per the tracker (line 55, surfaced to orchestrator), REQ-019's own content mandate (changelog naming the legacy strings) requires those references — internal spec contradiction acknowledged. All hits are in the changelog/migration sections, in keeping with the spec's "intentional historical references" exception. |
| REQ-020 (glossary discipline same-commit) | PASS | sdd/commands/implementation-complete.md gained Step 5 mirroring planning-complete Step 5 (per-step timing nuance per tracker). No glossary changes were needed for Chunk 1 per tracker. |
| REQ-021 (agent-engineering README + repo-root README updates) | PARTIAL (Finding F-2) | agent-engineering/README.md:16 (sdd-flow Step 4 mode-aware mention); :30–35 (What's-new-in-0.4.0); :36 (artifact-path note); :38–47 (Requires SDD plugin 2.0.0+ subsection with FAIL-009 cross-ref). HOWEVER: Repo-root `README.md` Available Plugins section has NO mention of `delivery_mode: per-slice` opt-in for SDD or per-slice support for sdd-flow, NO version-coupling note. Tracker explicitly flagged this gap. |
| REQ-022 (`## Slice Progress` schema + uniqueness invariant) | PASS | Binding schema documented in sdd/commands/slice-start.md:54–66, reinforced in slice-review.md / slice-commit.md. Column-write authority codified: `/implementation-start` scaffolds; `/slice-retro` updates Status/Test result/Notes only. SLICE-XXX uniqueness invariant called out (human-reviewer responsibility). |
| REQ-023 (Phase Detection legacy-path fallback + resume rules) | PARTIAL (Finding F-3) | Legacy-path fallback IS present in Phase Detection at SKILL.md:725–728. HOWEVER: Phase Detection priority list (lines 729–736) does NOT contain explicit resume rules for `## Awaiting Slicing Decision` or `## Recommended Re-planning`. The EDGE-006 informative refusal exists in the per-slice cycle section (line 679) but is not part of the Phase Detection list as REQ-023 requires. Tracker flagged REQ-023 as "Partial" — Chunk 4a deferred resume rules to Chunk 4b which did not implement them in the Phase Detection list location. |
| REQ-024 (slice-ID regex validation) | PASS | All four slice-*.md files contain `^SLICE-\d{3}$` literal regex with explicit validation step; sdd/commands/sdd-migrate-layout.md uses hardcoded paths only (no slice-ID interpolation surface). |
| REQ-025 (slice-command flag conventions) | PASS | All six flags (`--resume`, `--force`, `--reconcile-ledger`, `--replan`, `--from-slice`, `--override-replan`) inventoried with semantics + defaults + supervised/autonomous handling. Flag combination semantics (slice-retro.md:303+) cover all invalid combinations. |
| REQ-025a (`--reconcile-ledger` 8-step algorithm) | PASS | slice-retro.md:258+ describes the 8-step algorithm explicitly, including manual-edit-only entries preservation as orphans. |
| REQ-026 (cross-plugin version coupling cross-references) | PASS | sdd/README.md:609–610 (SDD-side clause naming agent-engineering 0.4.0+); agent-engineering/README.md:38–47 ("Requires SDD plugin 2.0.0 or later" subsection). FAIL-009 surfaced in both. |

### Per-EDGE Verification

| EDGE | Status | Evidence |
|------|--------|----------|
| EDGE-001 (idempotent re-run) | PASS | sdd-migrate-layout.md:75–76 (State 1 / State 2 idempotent exits); Step 9 post-migration verification re-runs detection. |
| EDGE-002 (slice-* in whole-feature mode) | PASS | All four slice-*.md inert-mode gate emitting REQ-007 verbatim message. |
| EDGE-003 (slice-review with no implementation yet) | PASS | slice-review.md Step 3 — `Not Started` row triggers refusal. |
| EDGE-004 (CLAUDE.md staleness reminder) | PASS | sdd/README.md:596 (migration section reminder); sdd-migrate-layout.md:374–388 (Step 8 CLAUDE.md staleness scan with output reminder). |
| EDGE-005 (practicality gate fires) | PASS | planning-start.md Step 8 enumerates four heuristics + qualitative escape; `## Awaiting Slicing Decision` block emitted on fire. |
| EDGE-006 (re-planning continue without flag) | PASS | SKILL.md:679 — orchestrator emits informative refusal naming three options before exiting. |
| EDGE-007 (retro written, ledger update fails) | PASS | slice-retro.md two-write ordering invariant + `--reconcile-ledger` mode. |
| EDGE-008 (APFS case-insensitive) | PASS | sdd/README.md:601–603 ("macOS APFS case-collision warning" subsection in Migration). |
| EDGE-009 (absent delivery_mode field) | PASS | planning-start.md:272 (Absent → silent default to whole-feature; no log line); implementation-start.md:52 (same). |
| EDGE-010 (multiple Not Started slices) | PASS | slice-start.md Step 4 — multi-row branch prompts user / autonomous halt. |
| EDGE-011 (Slice Progress column-write authority) | PASS | slice-start.md:60–64 binding schema; slice-retro.md Step 8 column-write restriction. |
| EDGE-012 (slice-start while another In Progress) | PASS | slice-start.md Step 5 EDGE-012 refusal + `--resume` exception. |
| EDGE-013 (slice-start on already-Complete) | PASS | slice-start.md Step 6 EDGE-013 refusal + autonomous `## Awaiting Re-start Decision` halt + `--force` flag. |
| EDGE-014 (slice-retro re-invocation) | PASS | slice-retro.md Step 5 EDGE-014 refusal with REQ-005 verbatim message + `--reconcile-ledger` escape hatch. |
| EDGE-015 (migrate-layout parse-failure fail-closed) | PASS | sdd-migrate-layout.md Step 3c case-iii fail-closed branch with `Failing closed to avoid data-loss-by-misclassification` rationale. |

### Per-FAIL Verification

| FAIL | Status | Evidence |
|------|--------|----------|
| FAIL-001 (migrate-layout partial completion) | PASS | sdd-migrate-layout.md Step 7 — three rollback options (A reset --hard, B per-move inverse, C resume-partial). |
| FAIL-002 (SDD 2.0 with active legacy flow) | PASS | SKILL.md:725–728 Phase Detection legacy-path fallback emits migration prompt; sdd-migrate-layout.md Step 3 active-flow refusal halts. |
| FAIL-003 (retro disk-full) | PASS | slice-retro.md two-write ordering + `--reconcile-ledger` 8-step algorithm. |
| FAIL-004 (per-slice review cap exhausted) | PASS | SKILL.md:657–663 — cap halt with ledger routing; entire-flow halt under `--skip-slice-checkpoints`. |
| FAIL-005 (migrate-layout on Windows non-bash) | PASS | sdd-migrate-layout.md Step 0 — bash detection refusal. |
| FAIL-006 (hook + migration version skew) | PASS (documentation-only) | sdd-migrate-layout.md:329 — Hook reminder names the path-change explicitly. |
| FAIL-007 (slice-start with missing Slice Progress table) | PASS | slice-start.md Step 3 — verbatim FAIL-007 refusal message. |
| FAIL-008 (migrate-layout parse-failure) | PASS | sdd-migrate-layout.md Step 3c case-iii (same control-flow as EDGE-015). |
| FAIL-009 (cross-plugin version mismatch) | PASS | Both READMEs cross-reference; FAIL-009 surfaced explicitly. |

## Module Review Log

| Module | Declared Risk | Depth Applied | Notes |
|--------|---------------|---------------|-------|
| MODULE-001 (delivery_mode runtime branch) | medium | default | Validated at planning-start, implementation-start, all four slice commands, SKILL.md Step 4 routing. Validation rule (canonical enum + invalid-value fail-fast) consistently applied. No silent fall-through observed. |
| MODULE-002 (slice-command primitives) | medium | default | All four commands reviewed; active-slice resolution convention shared cross-command per spec; flag conventions binding; slice-ID regex validation present in each. UX messages match REQ-007 verbatim. |
| MODULE-003 (slice-integrity review checks) | low | boundary | critical-review.md sub-section present (line 111); spec-review-panel.md specialist 4.7 + sub-header per tracker. Mode-gating present. Public interface (review checklist items) matches spec. |
| MODULE-004 (practicality gate) | medium | default | Four boolean heuristics + qualitative escape with `Qualitative judgment: ` prefix all enumerated in planning-start.md Step 8. Halt block matches `## Awaiting Clarification` shape. |
| MODULE-005 (migration helper) | **high** | **full** | Full internals review applied. Findings: (a) 10-step structure verified; (b) dry-run-by-default safety stance present (line 9); (c) active-flow refusal (Step 3) handles parse-failure fail-closed (case iii) AND active-status (case ii) AND missing-progress.md-with-legacy-artifacts (Step 3a) — all three fail-closed correctly; (d) idempotence guaranteed by Steps 2 + 9; (e) partial-migration recovery (Step 7) provides three options without leaving inconsistent state; (f) hardcoded-path safety (line 264) prevents path-traversal/eval; (g) bash detection (Step 0) prevents partial moves on non-bash shells. **No HIGH-severity findings.** Minor observation: the `--force-no-active` flag is somewhat sharp (overrides BOTH active-status AND parse-failure refusals) — adequately documented but the user-facing risk surface is wider than `--allow-dirty`. Acceptable per spec's scope. |
| MODULE-006 (sdd-flow Step 4 state machine) | medium | default | Mode-routing block (lines 523–531) clearly branches whole-feature vs per-slice. Per-slice cycle (lines 649–690) implements all six steps (4a → 4b → 4c → 4c.5 → 4c.6 → PAUSE) with strict one-subagent-per-slice rule. End-of-feature cycle (lines 692–708) shares 4d-4j with whole-feature flow. Bit-for-bit preservation invariant for whole-feature path verified — sub-step headers intact. Slice-boundary checkpoint axis matrix (lines 642–647) present. **However: see Finding F-3 — Phase Detection priority list does not include explicit `## Awaiting Slicing Decision` / `## Recommended Re-planning` resume rules per REQ-023.** |
| MODULE-007 (directory restructure + rename propagation) | medium | default | All sdd/commands/*.md path migrations verified via closing-oracle greps. Hook updated (REQ-017). SKILL.md path strings updated. **However: see Finding F-1 — terminology drift in SKILL.md narrative-prose ("PROMPT document" / "PROMPT tracking document" lingering in 6 narrative locations).** |
| MODULE-008 (documentation surface + version manifests) | low | boundary | Version strings byte-aligned across all four locations. sdd/README.md two-workflow restructure complete. agent-engineering/README.md cross-reference present. **However: see Finding F-2 — repo-root README.md Available Plugins section did not receive the per-slice opt-in note + version-coupling note REQ-021 mandates.** |

## Context Engineering (20%)

- IMPLEMENTATION-PLAN tracker (PROMPT-001-vertical-slicing-step-c-2026-05-05.md, 463 lines) is comprehensive: tracks every REQ/EDGE/FAIL/MODULE; chunk plan with dependency chain; closing-oracle grep gates per chunk; recursion-trap warning verbatim; locked-region prohibition verbatim; chunk-by-chunk completion notes with file-list and test results.
- Subagent counter files exist for every chunk under `flow-state/SDD/prompts/context-management/counters/`: 4-chunk1, 4-chunk2, 4-chunk3, 4-chunk4a, 4-chunk4b, 4-chunk5 (plus the standard step-2/3 counters).
- The tracker accurately reflects in-flight status — REQ-021 / REQ-023 marked Partial / Not Started where the implementation gap exists. Honest tracking discipline maintained.
- One discrepancy noted: tracker line 78–82 lists EDGE-004, EDGE-005, EDGE-008, EDGE-009, FAIL-006 as "Not Started" but spot-checks confirm they are implemented (EDGE-004 in sdd/README.md:596; EDGE-005 in planning-start.md:323+; EDGE-008 in sdd/README.md:601; EDGE-009 in planning-start.md:272 + implementation-start.md:52; FAIL-006 in sdd-migrate-layout.md:329). The tracker may have stale checkbox states from before Chunk 5 or 1 closed. Low-severity bookkeeping issue.
- MODULE-001, MODULE-003, MODULE-004, MODULE-006, MODULE-007 are similarly checkbox-stale in the tracker (marked Not Started when their underlying REQs are Complete). This affects the tracker's self-reported completeness picture but does not affect the on-disk implementation state.

## Verification (10%)

### Closing-oracle results

| Oracle | Result | Evidence |
|---|---|---|
| `grep -rn 'prompts/context-management' sdd/commands/ sdd/hooks/` (zero hits expected outside migration helper) | PASS | All hits are in sdd/commands/sdd-migrate-layout.md (documented exception per REQ-008 + spec line 451 oracle definition). |
| `grep -rn 'PROMPT-' sdd/commands/` (zero hits expected outside migration helper) | PASS | All hits in sdd/commands/sdd-migrate-layout.md. |
| `grep -n 'LOG_SUBDIR' sdd/hooks/log_subagent_call.py` shows new path | PASS | Line 18: `LOG_SUBDIR = Path("SDD") / "orchestration" / "subagent-calls"`. |
| Step A locked-region byte-identity (lines 64–204 + 375–379 of pre-implementation HEAD ffeec97) | PASS | Lines 64–204 still byte-identical at the SAME line numbers in HEAD (no insertions before line 204). Lines 375–379 of ffeec97 have shifted to lines 398–402 in HEAD due to allowed-region insertions (Step 6 extension); content is byte-identical at the new position (`diff` confirmed). The locked CONTENT is preserved; only the line numbers shifted as expected. Documented in tracker line 339. |
| `grep -n 'prompts/\|PROMPT-' agent-engineering/skills/sdd-flow/SKILL.md` (zero hits expected) | PASS (with documented exception) | One hit at line 725 — the FAIL-002 legacy-detection bullet, explicitly exempt per REQ-023 / FAIL-002. |
| Matcher contract: `^## Recommended (SPEC Amendments\|Re-planning)$` in slice-retro.md | PASS | slice-retro.md:111 + 126 emit both headers. |
| Matcher contract: SKILL.md matches Chunk 2's emissions | PASS | SKILL.md:668 + 669 grep against the exact strings. |
| Version cross-references: sdd 2.0.0 + agent-engineering 0.4.0 in plugin.json + marketplace.json (4 locations) | PASS | All four byte-aligned. |
| Cross-plugin coupling refs in READMEs: sdd→agent-engineering 0.4.0+ AND agent-engineering→SDD 2.0.0+ | PASS | sdd/README.md:609; agent-engineering/README.md:36, 40. |
| Inert-mode message in all four slice-*.md | PASS | All four files contain the verbatim REQ-007 message. |
| Slice-command flag inventory (`--resume`, `--force`, `--reconcile-ledger`) | PASS | All three flags documented in slice-start.md / slice-retro.md (and back-cited in slice-review.md / slice-commit.md flag-inventory tables). |
| Migration helper safety strings (Refusing migration / fail-closed / dry-run / Could not determine flow status / Both old and new / On Windows, run from Git Bash / already migrated / nothing to migrate) | PASS | All literal strings verified in sdd/commands/sdd-migrate-layout.md. |
| `delivery_mode` validation: `Invalid delivery_mode value` + `canonical enum is exactly` in planning-start + implementation-start | PASS | planning-start.md:272 (canonical enum prose) + :318 (Invalid delivery_mode value error); implementation-start.md:50 + :55. |

### Test Coverage (adapted for codebase-change feature)

- Unit tests / Integration tests / E2E tests: **N/A** — this feature is markdown command files (4 new + ~14 modified) + a 1-line Python hook constant change + plugin manifest version bumps + README rewrites + skill markdown surgery. There is no executable code path to unit-test; the Python hook change is trivially verified by the closing-oracle grep. Per spec's Validation Strategy, manual verification + closing-oracle greps are the declared test surface. All declared oracles execute and pass except for the documented internal contradiction in REQ-019 (the spec itself surfaces the conflict and the implementation honors the content mandate).

## Findings

### F-1 [MEDIUM] — Terminology drift in SKILL.md narrative prose: "PROMPT document" not renamed to "IMPLEMENTATION-PLAN document"

**Location:** `agent-engineering/skills/sdd-flow/SKILL.md` lines 312, 545, 547, 553, 561, 576, 584.

**Issue:** Per ADR 0002 + REQ-016, the `PROMPT-XXX` → `IMPLEMENTATION-PLAN-XXX` rename was meant to apply throughout (the tracker's Chunk 1 line 339 explicitly says: *"bare `PROMPT-` and bare `PROMPT` → `IMPLEMENTATION-PLAN-` / `IMPLEMENTATION-PLAN`"*). The path strings were updated in Chunk 4a but the narrative-prose terminology *"PROMPT document"* / *"PROMPT tracking document"* survives at six locations:

```
312: each appending to the PROMPT document so the next subagent knows what's done
545:   - Update PROMPT tracking document throughout
547: each subagent appends to the PROMPT document so the next knows what's done
553: ..., the implemented code files (paths from PROMPT document)
561: - **Outputs:** Updated code and tests, updated PROMPT document, ...
576: - **Outputs:** Updated code and tests, updated PROMPT document, ...
584: - **Outputs:** Updated PROMPT document, updated SPEC document, ...
```

The narrow REQ-016 oracle (`grep -n 'PROMPT-'` with hyphen) does not catch these — only line 725 (the documented FAIL-002 exception) is flagged. But the ADR 0002 intent + the Chunk 1 tracker stats explicitly include "bare PROMPT" in scope.

**Severity:** MEDIUM — narrative-prose terminology drift; the document itself does not break, but the user-facing description in SKILL.md refers to a concept (`PROMPT document`) that no longer exists by that name in the rest of the system. Confuses readers who hit the term and can't find it elsewhere.

**Required fix:** Replace the six occurrences with `IMPLEMENTATION-PLAN document` / `IMPLEMENTATION-PLAN tracking document` (preserving capitalization style of the surrounding prose). Mechanical edit, no semantic risk.

### F-2 [MEDIUM] — Repo-root README.md missing per-slice opt-in note + version-coupling note (REQ-021)

**Location:** `README.md` (repo root, 60 lines).

**Issue:** REQ-021 binding text:

> "Repo-root `README.md` Available Plugins section gains a brief note about `delivery_mode: per-slice` opt-in for SDD and per-slice support for sdd-flow, plus the version-coupling note per REQ-026."

The repo-root README's Available Plugins section (lines 11–43) describes SDD/PACE/agent-engineering generically with no mention of per-slice mode, no `delivery_mode:` reference, no version-coupling note, no SDD 2.0.0 / agent-engineering 0.4.0 cross-reference. The tracker (Chunk 5 completion note) explicitly flagged this gap: *"repo-root README.md was NOT in this chunk's listed Outputs, deferred for orchestrator disposition"*.

**Severity:** MEDIUM — REQ-021 is partially satisfied (the per-plugin READMEs are complete and comprehensive); the repo-root note is a marketplace-browsing-user-experience concern. Marketplace operators browsing the top-level README will not discover per-slice mode or the version coupling. Discoverability issue, not a runtime correctness issue.

**Required fix:** Add a short paragraph (3–5 lines) under the SDD section of the Available Plugins list naming `delivery_mode: per-slice` opt-in, and a top-level cross-plugin note (similar to the existing CLAUDE.md guidance about per-plugin scope) that SDD 2.0.0 and agent-engineering 0.4.0 should be installed together.

### F-3 [MEDIUM] — Phase Detection priority list missing explicit resume rules for `## Awaiting Slicing Decision` and `## Recommended Re-planning` (REQ-023)

**Location:** `agent-engineering/skills/sdd-flow/SKILL.md` Phase Detection Priority section (lines 723–736).

**Issue:** REQ-023 binding text:

> "`sdd-flow` Phase Detection (SKILL.md lines 636–645) gains rules for resuming from `## Awaiting Slicing Decision` (with `--fall-back-to-whole-feature` or `--retry-slicing "<hint>"`) and from `## Recommended Re-planning` (with `--replan` and optional `--from-slice SLICE-XXX`, or `--override-replan`). Phase Detection also implements legacy-path fallback..."

The legacy-path fallback IS in the Phase Detection list (line 725). The `## Awaiting Clarification` resume rule is in the list (line 735). But `## Awaiting Slicing Decision` and `## Recommended Re-planning` are NOT in the Phase Detection priority list. They appear in the per-slice-cycle section (line 679 EDGE-006 prose) but a user resuming via `/sdd-flow continue` from a halted state goes through Phase Detection first; if the priority list does not check for these blocks, the resumption may fall through to the wrong sub-step.

The tracker explicitly marked REQ-023 as Partial (line 59): "Resume rules for `## Awaiting Slicing Decision` and `## Recommended Re-planning` deferred to Chunk 4b which owns Step 4 substantive surgery and the corresponding progress.md block writers." Chunk 4b implemented the writers (the halt block emission) but did not back-port the resume-detection rules into the Phase Detection priority list.

**Severity:** MEDIUM — Phase Detection is the resumption-correctness load-bearing logic; missing rules here could cause `/sdd-flow continue` from a slicing-decision halt to misroute. The user-facing impact is recoverable (manual intervention) but the autonomous-flow regression check would catch this.

**Required fix:** Add two priority-list entries to Phase Detection (between the existing legacy-detection rule and the Implementation-Phase-Complete rule):

- If `## Recommended Re-planning` is the latest block in `progress.md` AND no resume-flag block follows → emit informative refusal naming three options (`--replan`, manual edit + plain `continue`, `--override-replan`); halt.
- If `## Awaiting Slicing Decision` is the latest block in `progress.md` AND no resume-flag block follows → emit informative refusal naming the two options (`--fall-back-to-whole-feature`, `--retry-slicing "<hint>"`); halt.

### F-4 [LOW] — Tracker checkbox staleness for several REQ/MODULE entries

**Location:** `flow-state/SDD/prompts/PROMPT-001-vertical-slicing-step-c-2026-05-05.md`.

**Issue:** Several REQs/EDGE/FAIL/MODULE entries are checkbox-marked `[ ]` (Not Started) in the tracker but on-disk evidence shows they are Complete:

- EDGE-004 (line 78) — sdd/README.md:596 has the reminder; sdd-migrate-layout.md Step 8 has the staleness scan. **Implemented.**
- EDGE-005 (line 79) — planning-start.md:323 has the four-heuristic gate. **Implemented.**
- EDGE-008 (line 82) — sdd/README.md:601–603 has the APFS warning. **Implemented.**
- EDGE-009 (line 83) — planning-start.md:272 + implementation-start.md:52 have the silent-default. **Implemented.**
- FAIL-006 (line 98) — sdd-migrate-layout.md:329 has the Hook reminder. **Implemented.**
- MODULE-001 / MODULE-003 / MODULE-004 / MODULE-006 / MODULE-007 (lines 105, 107, 108, 110, 111) — all marked Not Started but their underlying REQs are largely Complete.
- SEC-004 (line 70) — acknowledgment-only requirement; effectively covered by spec text.

**Severity:** LOW — bookkeeping accuracy issue; the on-disk implementation is in better shape than the tracker reports. No functional impact.

**Required fix:** Update the tracker checkbox states to match on-disk reality before declaring Step 4 complete (or accept the staleness as artifact of in-flight tracking).

## Decision: APPROVED with REQUIRED FIXES (F-1, F-2, F-3 must be addressed before declaring Step 4 implementation complete)

The implementation is substantially complete. All HIGH-severity surfaces (MODULE-005 migration helper destructive-action posture; MODULE-002 slice-command primitives + path-traversal prevention; MODULE-006 mode-routing bit-for-bit preservation; locked-region preservation) pass full review with no HIGH-severity findings. The recursion-trap discipline was honored throughout — this run's artifacts remain at `flow-state/SDD/...` legacy paths while source-code edits emit the new layout for future runs.

The three MEDIUM-severity findings (F-1 narrative drift, F-2 repo-root README gap, F-3 Phase Detection rule gap) are all mechanical / surgical and can be addressed in Step 4c (fix-findings). None affect runtime correctness for whole-feature mode (the bit-for-bit preservation invariant); F-3 is the only one that affects per-slice runtime correctness (resumption from a halt block) and even that is recoverable via manual intervention.

## Required Actions (prioritized)

1. **F-3 [MEDIUM]:** Add `## Awaiting Slicing Decision` and `## Recommended Re-planning` priority rules to SKILL.md Phase Detection Priority list (~5–10 line insertion at lines 736+).
2. **F-1 [MEDIUM]:** Replace 6 occurrences of "PROMPT document" / "PROMPT tracking document" → "IMPLEMENTATION-PLAN document" / "IMPLEMENTATION-PLAN tracking document" in SKILL.md (mechanical sed-equivalent edit).
3. **F-2 [MEDIUM]:** Add per-slice opt-in + version-coupling paragraph to repo-root README.md Available Plugins SDD section (3–5 lines).
4. **F-4 [LOW]:** Update tracker checkbox states for stale `[ ]` entries (low-priority hygiene).

## Commendations

- **Locked-region preservation discipline.** Step A locked region (lines 64–204 + 375–379 of pre-implementation HEAD ffeec97) is byte-identical at HEAD. Insertions in allowed regions shifted the Quality Checklist locked items from line 375–379 to 398–402 — the tracker explicitly noted and verified this; the byte-identity invariant holds at the new positions.
- **Recursion-trap discipline.** Every chunk subagent prompt embedded the recursion-trap warning verbatim. This run's artifacts remain at the legacy `flow-state/SDD/prompts/` paths; source-code edits emit the new `SDD/implementation/` + `SDD/orchestration/` paths for FUTURE runs only. Zero relocation of in-flight artifacts.
- **Per-chunk commit cadence with clean reverts.** Chunk-by-chunk commits with closing-oracle gates per chunk allowed each step's grep contract to be verified before declaring done.
- **Matcher contract preservation across Chunks 2 ↔ 4b.** The exact header strings `## Recommended SPEC Amendments` and `## Recommended Re-planning` are emitted by `/slice-retro` (slice-retro.md:111 + 126) and the corresponding matcher in SKILL.md (lines 668 + 669) targets those exact strings. The contract is byte-aligned — no drift between the producer and consumer.
- **Migration helper internals are conservative and well-documented.** Dry-run-by-default; fail-closed on parse failure; idempotent re-runs; partial-migration refusal-with-recovery; bash-detection refusal; CLAUDE.md staleness scan. The `--force-no-active` flag provides a deliberate override path for users with genuinely orphaned `progress.md` files.
- **REQ-007 message-discipline pattern adopted uniformly.** Every refusal path in the new commands names the detected condition + the resolution path + exits cleanly. The pattern is binding for downstream features per REQ-025 flag conventions.

## Findings Addressed

Step 4c fix-findings subagent applied the following resolutions on 2026-05-05.

### F-1 [MEDIUM] — Bare "PROMPT document" / "PROMPT tracking document" in SKILL.md — RESOLVED

**Source file edited:** `agent-engineering/skills/sdd-flow/SKILL.md` (lines 312, 545, 547, 553, 561, 576, 584).

**Change:** Applied `perl -i -pe 's/\bPROMPT tracking document\b/IMPLEMENTATION-PLAN tracking document/g; s/\bPROMPT document\b/IMPLEMENTATION-PLAN document/g'` to substitute the bare-term phrases. Per ADR 0002 + REQ-016, the `PROMPT-XXX` → `IMPLEMENTATION-PLAN-XXX` rename applies throughout, including narrative-prose conceptual references that the hyphen-targeted Chunk 4a substitution missed.

**Verification (closing-oracle):** `grep -n "PROMPT document\|PROMPT tracking" agent-engineering/skills/sdd-flow/SKILL.md` returns zero hits. The seven previously-flagged lines now read "IMPLEMENTATION-PLAN document" / "IMPLEMENTATION-PLAN tracking document". The narrow REQ-016 oracle (`grep -n 'PROMPT-'`) continues to pass with the documented FAIL-002 exception at line 725 untouched.

### F-2 [MEDIUM] — Repo-root README.md missing per-slice opt-in + version-coupling note (REQ-021) — RESOLVED

**Source file edited:** `README.md` (repo root).

**Change:** Updated the SDD section heading to "Spec-Driven Development (SDD) — v2.0.0" and added a "v2.0.0 highlights" paragraph naming `delivery_mode: per-slice` opt-in (vertical-thread cycle with retrospectives + learnings ledger), the directory restructure (`SDD/prompts/` → `SDD/implementation/` + `SDD/orchestration/`), and the `PROMPT-XXX` → `IMPLEMENTATION-PLAN-XXX` rename. Added a "Cross-plugin coupling" paragraph naming the SDD 2.0.0 ↔ agent-engineering 0.4.0 dependency. Extended the SDD Key Features bullet list with a "Two delivery modes" item. Updated the agent-engineering section heading to "Agent Engineering — v0.4.0" and added a "v0.4.0 highlights" paragraph naming sdd-flow's per-slice orchestration support, the SDD 2.0.0+ minimum, and the FAIL-009 silent-misbehavior failure mode in mixed installs.

**Verification (closing-oracle):** `grep -n "delivery_mode: per-slice\|v2.0.0\|v0.4.0\|FAIL-009" README.md` returns hits at lines 11 (heading), 15 (highlights), 38 (heading), 42 (highlights). The repo-root README now provides the marketplace-browsing entry-point users need to discover per-slice mode and the version coupling.

### F-3 [MEDIUM] — Phase Detection priority list missing resume rules (REQ-023) — RESOLVED

**Source file edited:** `agent-engineering/skills/sdd-flow/SKILL.md` Phase Detection Priority section (between the legacy-layout rule and the Implementation-Phase-Complete rule).

**Change:** Inserted three new priority-list bullets:
1. `## Awaiting Slicing Decision` block detected — names `--fall-back-to-whole-feature` (flips spec to whole-feature + routes), `--retry-slicing "<hint>"` (re-spawns Step 3a with hint), and no-flag re-prompt branches.
2. `## Recommended Re-planning` block detected without resume flag — names the three resume options (`--replan`, `--replan --from-slice SLICE-XXX`, `--override-replan`), the `--replan --override-replan` invalid-combination matrix, and the halt-regardless-of-`--skip-slice-checkpoints` callout per REQ-014.
3. `## Awaiting Re-start Decision` block detected — names `--confirm-restart SLICE-XXX` per EDGE-013.

These rules are placed above the existing whole-feature phase-detection rules so that slicing/re-planning halts take precedence over normal phase resumption. The priority order now reads: legacy-layout → Awaiting Slicing Decision → Recommended Re-planning → Awaiting Re-start Decision → Implementation Complete → Implementation active → Planning Complete → Planning active → Research Complete → Research active → Awaiting Clarification → no-phase-info.

**Verification (closing-oracle):** `grep -n "Awaiting Slicing Decision\|Recommended Re-planning\|Awaiting Re-start Decision" agent-engineering/skills/sdd-flow/SKILL.md` returns hits at lines 729, 732, 733, 734 (Phase Detection list) plus the existing per-slice cycle hits at 669, 679 — Phase Detection now contains explicit resume rules; per-slice cycle continues to emit the halt blocks. Resumption-correctness load-bearing logic now closes the per-slice halt-state misroute risk.

### F-4 [LOW] — Tracker checkbox staleness — RESOLVED

**Source file edited:** `flow-state/SDD/prompts/PROMPT-001-vertical-slicing-step-c-2026-05-05.md`.

**Change:** Updated checkbox states for items confirmed complete on disk:
- REQ-021 (line 57): `[ ]` → `[x]` with Step 4c fix note covering repo-root README updates per F-2.
- REQ-023 (line 59): `[~]` → `[x]` with Step 4c fix note covering Phase Detection resume rules per F-3.
- SEC-004 (line 70): `[ ]` → `[x]` (acknowledgment-only requirement; no surface introduced).
- EDGE-004, EDGE-005, EDGE-008, EDGE-009 (lines 78–83): `[ ]` → `[x]` with file:line evidence.
- FAIL-006 (line 98): `[ ]` → `[x]` with sdd-migrate-layout.md:329 evidence.
- MODULE-001, MODULE-003, MODULE-004, MODULE-006, MODULE-007 (lines 105–111): `[ ]` → `[x]` with file:line evidence per module.
- RISK-001, RISK-002, RISK-004, RISK-005, RISK-006 (lines 116–121): `[ ]` → `[x]` with closing-oracle / preservation-invariant evidence.
- Security Validation block (lines 423–428): six `[ ]` → `[x]` (all three SEC-XXX + authorization + input validation acknowledgments).
- Documentation Created block (lines 434–439): six `[ ]` → `[x]` with Chunk 5 / Step 4c fix evidence.
- "In Progress" block (line 351–353): updated current-focus narrative to reflect Step 4c fix completion.

The on-disk implementation evidence is recorded in each updated entry's status note, so the tracker now matches the review's verification table state.

## Decision: APPROVED — required fixes applied

All three MEDIUM-severity findings (F-1, F-2, F-3) and the LOW-severity finding (F-4) are resolved. Closing-oracle greps for each fix pass. The tracker now accurately reflects on-disk implementation state. Step 4c fix-findings is complete; the orchestrator may advance to Step 4d / 4e / 4f per the standard `/sdd-flow` Step 4 sequence.
