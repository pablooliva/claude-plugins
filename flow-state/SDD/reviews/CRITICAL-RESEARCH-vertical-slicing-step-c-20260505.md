# Research Critical Review: vertical-slicing-step-c

## Executive Summary

The research is unusually well-cited (file:line throughout), respects the recursion-trap, and faithfully resolves all five named open questions (Q-A through Q-E) and all eight locked decisions. However, three completeness gaps will translate into rework during planning/implementation if not addressed: a HIGH gap in the documentation surface (`sdd/README.md`'s directory tree and PROMPT references are not enumerated for rewrite, despite shipping under a 2.0.0 major-version bump), a MEDIUM gap in the SKILL.md audit (two prose-embedded legacy references at lines 319 and 487 missed), and a MEDIUM gap in the spec-review-panel deliverable schema (the hardcoded `#### Findings by Specialist` header list at lines 230-244 needs a conditional `#### Slice Integrity Findings` entry — proposed §4.7 specialist alone doesn't make the deliverable schema slice-aware). Two design surfaces are deferred to "see proposal §N" without being made authoritative in the research: the practicality-gate detection logic, and the `## Slice Progress` table schema. Planning will need both to be concrete.

**Pre-research clarification gate behavior:** The Step 1.5 gate was satisfied by a pointer-style CLARIFICATION artifact, not by an interactive `/research-clarify` run. This is documented openly in the CLARIFICATION's "Why this artifact exists in this shape" section. Note for downstream visibility (per Step 2c executive-summary obligation in sdd-flow): the design concept was externalized as the proposal itself, then locked-decisions-extracted into the CLARIFICATION; this is a deliberate substitute, not a skipped gate.

**Verdict: REVISE BEFORE PROCEEDING.** All gaps have concrete fixes — none requires re-doing research. Once revised, planning can proceed.

## Severity: MEDIUM (one HIGH gap, three MEDIUM gaps; no STOP-AND-RECONSIDER findings)

## Critical Gaps Found

1. **`sdd/README.md` legacy references and directory tree not enumerated for rewrite** (Severity: HIGH)
   - Evidence: Branch 6 (research §"Documentation surface") covers the README's two-workflow restructure and changelog/migration section but does NOT enumerate the existing legacy-path references at lines 263 ("Load the PROMPT and SPEC documents"), 269 ("`SDD/prompts/test-audits/`"), 379 (`/implementation-complete` example block), 392-411 (the directory tree showing `prompts/`, `implementation-complete/`, `context-management/`, `subagent-calls/`), and 492 ("CLARIFICATION-[###] → RESEARCH-[###] → SPEC-[###] → PROMPT-[###]" numbering convention). `grep -c "prompts\|PROMPT-" sdd/README.md` returns 3 hits but the directory tree has uncounted structural references that would all need rewriting under the restructure.
   - Risk: SDD plugin 2.0.0 ships with a README whose directory tree contradicts the new layout. Users land here looking for the migration story and find documentation that refers to a layout that no longer exists. The major-version bump (which the research correctly justifies) makes this visible to every re-installer.
   - Recommendation: Extend Branch 6's `sdd/README.md` subsection to enumerate (a) the directory tree at lines 392-411 needs a full rewrite mirroring the new layout, (b) inline PROMPT references at lines 263, 269, 379, 492 need rename to IMPLEMENTATION-PLAN, (c) the numbering convention statement at line 492 needs updating, (d) a verification step grepping the README for `prompts\|PROMPT-` should return zero hits after edits.

2. **SKILL.md audit missed two narrative-prose legacy references** (Severity: MEDIUM)
   - Evidence: Branch 2 (research §"Artifact Paths Contract" table) enumerates lines 73-92, 109-117, 309, 330, 424, 524-525, 540, 570-571, 598, 631, 636-645, 658, 695. A grep of SKILL.md for `prompts/\|PROMPT-` returns 17 hits including line 319 (Mid-Phase Handoff Protocol callout: "`SDD/prompts/context-management/[phase]-compacted-...md`") and line 487 (panel-review halt instructions: "Iteration history: `SDD/prompts/context-management/progress.md`") — neither appears in Branch 2's enumeration.
   - Risk: The implementation phase uses Branch 2 as its checklist; a missed reference in a narrative paragraph leaves a stale legacy-path string in the live skill, breaking the orchestrator's pause-message and handoff guidance after the migration. The skill will continue to work but will lie to users about where to look.
   - Recommendation: Replace Branch 2's enumeration with the directive: "after edits, `grep -n 'prompts/\\|PROMPT-' agent-engineering/skills/sdd-flow/SKILL.md` MUST return zero hits." Add a post-edit verification step explicitly. The two missed lines should be called out by name in Branch 2 so they are not re-missed.

3. **spec-review-panel deliverable schema not updated for slice-integrity** (Severity: MEDIUM)
   - Evidence: Branch 5 specifies inserting a new specialist 4.7 at the spec-review-panel.md but doesn't address the deliverable's "Document Structure" template (lines 213-262 of spec-review-panel.md), specifically the hardcoded `#### Findings by Specialist` block at lines 230-244 which lists exactly five sub-headers (`#### Security Findings` through `#### Module Depth Findings`). A new specialist 4.7 needs a corresponding `#### Slice Integrity Findings` sub-header in the deliverable, conditionally rendered when `delivery_mode: per-slice`.
   - Risk: The panel runs the slice-integrity specialist in per-slice mode but the deliverable template has nowhere to put the findings. Either they get pushed into another specialist's section (corrupting per-specialist accountability) or they get dropped silently.
   - Recommendation: Extend Branch 5's spec-review-panel.md insertion-point list to include the deliverable schema at lines 230-244: add a `#### Slice Integrity Findings` sub-header gated on `delivery_mode: per-slice`. Confirm severity-aggregation rules at lines 196-200 still apply unchanged (research correctly asserts this but the schema must exist for the rules to bite).

## Questionable Assumptions

1. **Practicality gate's detection logic is fully defined in proposal §5.**
   - Why questionable: Research mentions "the practicality gate" 7 times — Flow 1 step 2 ("invoke the practicality gate when slicing is requested but no meaningful slices exist"), the §4.7 specialist anti-pattern #7 ("Practicality-gate skipped"), the testing-strategy ("confirm the planning subagent assesses sliceability"), the user-facing message in Open Question 1's resolution. But the research never spells out what counts as "no meaningful slices exist" — the detection logic is deferred to "§5 of the proposal" without being made authoritative in the research.
   - Alternative possibility: The proposal's §5 may describe the gate's UX without specifying detection criteria; the planning subagent then makes a judgment call that varies across runs. If detection is judgment-based, the research should say so (and Branch 5's specialist anti-pattern would then need to handle the "judgment call documented in retro/progress.md" audit-trail explicitly).

2. **`## Slice Progress` table schema is fully defined in proposal §2.**
   - Why questionable: The research references the table 5 times — `/slice-start` reads it, `/slice-retro` updates it, the resume logic checks it for the in-flight slice — but never enumerates its columns or the exact state values. The glossary names four states (`Not Started` / `In Progress` / `Acceptance Check Passing` / `Complete`) but the research's Branch 1 / Branch 2 / Branch 3 don't carry that enumeration into `/implementation-start`'s scaffold instructions.
   - Alternative possibility: The schema may be incompletely specified in the proposal (e.g., the proposal shows an example but doesn't say "these are the canonical columns"). If so, the planning phase will guess. Recommendation: research should make the schema authoritative — list the canonical columns and states once, with the planning subagent and `/implementation-start` both bound to that schema.

3. **`/sdd-migrate-layout`'s `git mv` operations work cross-platform.**
   - Why questionable: The Branch 4 move set uses bash glob patterns and `git mv`. The research's "External dependencies" section lists Git but doesn't address Windows path separators or the fact that Claude Code on Windows may invoke commands via PowerShell rather than bash. The shell snippet uses `${f//PROMPT-/IMPLEMENTATION-PLAN-}` which is a bash-specific parameter expansion.
   - Alternative possibility: Plugin commands run in the Claude Code shell which may abstract this away, but the research does not confirm. A note ("the migration helper command body must be cross-platform; bash-only constructs need an alternative for Windows users") would close this.

4. **Active-phase detection by parsing `progress.md` markdown headers is reliable.**
   - Why questionable: Branch 4 says detection parses `## Phase: <name> - <status>` blocks. But the actual format used by sdd-flow / phase-start commands has not been verified to be exactly this pattern — Branch 1's table for `research-start.md` line 12, `planning-start.md` line 24, etc. shows progress.md is appended-to by every phase but the research doesn't enumerate the exact header format the parser will look for. A header-format mismatch silently fails the active-phase check, allowing in-flight migration.
   - Alternative possibility: The header format may vary across phase-start commands; the migration helper's parser should be robust to multiple shapes (e.g., accept any of `## Research Phase - <status>`, `## Phase: research - <status>`, etc.) OR the research should pin the exact format and require all phase-start commands to emit it.

## Missing Perspectives

- **Plugin uninstall / re-install user.** What happens if a user uninstalls SDD 1.x, installs 2.0.0, and only THEN runs `/sdd-migrate-layout`? The migration helper assumes the legacy tree is present and the new plugin is loaded. This is the expected upgrade path (`/plugin uninstall sdd` → `/plugin install sdd@2.0.0` → `/sdd-migrate-layout`) but is not enumerated in the research.

- **Future contributor reading the merged plugin.** ADR 0001 and ADR 0002 are excellent for the rationale-discovery use case, but the research does not mention adding inline pointers (e.g., a comment at the top of `/implementation-start.md`'s mode-aware branch that says "see ADR 0001 for why this branch exists in one codebase rather than two"). Without inline pointers, a future contributor will discover the ADRs only by reading `SDD/adr/` proactively.

- **A user with a partially-named feature.** What if a user has `SDD/prompts/PROMPT-001-feature-a.md` and `SDD/prompts/PROMPT-001-feature-b.md` (duplicate `[###]`)? Migration's `for f in SDD/prompts/PROMPT-*.md` loop renames them both to IMPLEMENTATION-PLAN — no collision, but the duplication remains. The research does not flag this as a hygiene concern, which is fine for migration mechanics but means the migration helper's success message could mislead.

- **CLAUDE.md authors in user repos.** Per the recursion-trap warning, this run uses legacy paths. But user repos may have their own CLAUDE.md instructions referencing `SDD/prompts/` — those become stale after migration. Research's Branch 6 covers plugin docs but not user-repo CLAUDE.md collateral. Likely acceptable as out-of-scope but should be acknowledged.

## Design Concept Fidelity Findings

### Branches addressed (1–9)

- **Branch 1 (SDD plugin command audit):** ADDRESSED with one shallow spot — `commit.md` and `context-check.md` are listed as "verify and update if present" rather than confirmed. Research's grep would have answered this; deferring to "verify" leaves a small open thread for implementation.
- **Branch 2 (sdd-flow skill audit):** ADDRESSED but INCOMPLETE — see Critical Gap #2 (lines 319 and 487 missed).
- **Branch 3 (New command surface):** ADDRESSED thoroughly. Inputs/outputs/active-slice resolution/inert-mode behavior all specified.
- **Branch 4 (Migration mechanics):** ADDRESSED thoroughly with detection logic, move set, idempotence, in-flight refusal, rollback, hook coordination — strongest branch.
- **Branch 5 (Slice-integrity additions to reviews):** ADDRESSED for the insertion of the check itself. SHALLOW on the spec-review-panel deliverable schema — see Critical Gap #3.
- **Branch 6 (Documentation surface):** SHALLOW — see Critical Gap #1.
- **Branch 7 (Versioning and marketplace):** ADDRESSED, with explicit drift-verification step.
- **Branch 8 (Hooks and infrastructure):** ADDRESSED — single line change identified, hook-script path under `CLAUDE_PLUGIN_ROOT` correctly noted as unchanging.
- **Branch 9 (Test surface):** ADDRESSED with explicit per-artifact verification criteria.

### Open questions (Q-A through Q-E)

- **Q-A (summary file rename vs relocation):** RESOLVED — relocation only.
- **Q-B (RETROSPECTIVE-SLICE filename `feature` slug):** RESOLVED — feature-name slug, consistent with siblings; the `XXX` in the retrospective filename is the slice number, the `XXX` in LEARNINGS-FEATURE is the feature number. Glossary entry confirms.
- **Q-C (`/slice-commit` enforcement):** RESOLVED — looser interpretation, structured message + user-managed staging.
- **Q-D (re-planning's "completed slices remain valid"):** RESOLVED — user judgment surfaced via `--from-slice SLICE-XXX` argument; orchestrator never auto-determines.
- **Q-E (`/slice-retro` partial-write recovery):** RESOLVED — first-write-wins (retro before ledger); reconciliation mode optional.

### Step A locked region

RESPECTED. Research correctly cites lines 64–204 + 375–379 as off-limits. Verified: `planning-start.md`'s `## Delivery Slices` template block is at lines 184-204, the slice-related Quality Checklist items are at lines 375-379, and the `delivery_mode:` frontmatter line is at line 69. Research's allowed-region citations (line 271 prose, line 305 Step 6) verified.

### Recursion-trap

RESPECTED. The research embeds the recursion-trap warning verbatim (lines 11-21). The "What success looks like" section explicitly clarifies that "the directory restructure ... is implemented in the plugin/skill source ... *without* relocating this run's own artifacts."

### Conservative defaults for the six remaining open questions

RESPECTED for all six. Practicality-gate UX mirrors the Step 1.5 halt (Open Q1), Step 0 unchanged (Open Q2), absent `delivery_mode:` stays silent (Open Q3), retro structure is hybrid (Open Q4), `/slice-review` is a thin wrapper (Open Q5), slice subagent prompts get only the ledger (Open Q6). No relitigation observed.

### Vocabulary alignment with `SDD/UBIQUITOUS_LANGUAGE.md`

ALIGNED. The glossary defines `delivery_mode`, `whole-feature`, `per-slice`, `vertical thread / vertical slice`, `horizontal layering`, `concentrated function`, `slice cycle`, `end-of-feature cycle`, `acceptance check`, `slice sequence rationale`, `SLICE-001 thinness`, `IMPLEMENTATION-PLAN`, `## Slice Progress`, `slice retrospective`, `LEARNINGS-FEATURE-XXX ledger`, `Recommended SPEC Amendments`, `Recommended Re-planning`. The research uses these names consistently. One minor note: the research uses "thread line" in Branch 5's vocabulary payload (line 523) — glossary defines this only obliquely under `vertical thread / vertical slice`. Not a misalignment, but a glossary entry for "thread line" would close the loop if the slice-integrity specialist will use it as a named concept.

### ADR coherence

COHERENT. ADR 0001 (merged codebase) and ADR 0002 (directory restructure + rename) are internally consistent with the research's findings and reference the research correctly. ADR 0001's alternatives (single codebase, fork, companion plugin, fork-only-sdd-flow) match the proposal's Distribution Strategy alternatives. ADR 0002 correctly identifies one-time breaking change for both modes (matches locked decision #8) and ships rename + restructure together (matches locked decision #6). One small gap: ADR 0002's "Negative" consequences mention version-skew between hook and skill but don't reference Q-A's resolution that summary files don't need filename changes — minor detail, not worth blocking.

## Out-of-scope adherence

RESPECTED. Research does not modify Step A's spec template block, does not relocate this run's artifacts, does not re-run Step A, and does not relitigate the six open questions.

## Recommended Actions Before Proceeding

1. **(HIGH)** Extend Branch 6 to enumerate `sdd/README.md`'s legacy-path touch points: directory tree at lines 392-411 needs full rewrite; inline PROMPT references at lines 263, 269, 379, 492 need rename; numbering convention statement at line 492 needs update; add a post-edit `grep -c "prompts\|PROMPT-" sdd/README.md` verification.

2. **(MEDIUM)** Replace Branch 2's enumeration of SKILL.md line numbers with a directive: after edits, `grep -n 'prompts/\|PROMPT-' agent-engineering/skills/sdd-flow/SKILL.md` returns zero hits. Call out lines 319 and 487 by name as previously-missed narrative references.

3. **(MEDIUM)** Extend Branch 5's spec-review-panel.md insertion-point list to add `#### Slice Integrity Findings` to the deliverable's Document Structure template (lines 230-244), gated on `delivery_mode: per-slice`.

4. **(MEDIUM)** Make the `## Slice Progress` table schema authoritative in the research itself: enumerate canonical columns and the four state values (`Not Started` / `In Progress` / `Acceptance Check Passing` / `Complete`) so `/implementation-start`'s scaffold instructions and `/slice-retro`'s state transitions both bind to the same schema.

5. **(MEDIUM)** Make the practicality-gate detection criteria authoritative in the research: enumerate what the planning subagent inspects (e.g., "all SLICE-XXX share the same single-module touched-set", "the feature touches one module only", or "judgment call surfaced to user with rationale captured in progress.md") so the user-facing message in Open Question 1 has a concrete trigger.

6. **(LOW)** Confirm `commit.md` and `context-check.md` are clean of legacy-path references with explicit grep results (Branch 1 currently says "verify"). My verification confirms they have zero `prompts/\|PROMPT-` matches; research can promote this from "verify" to "confirmed clean."

7. **(LOW)** Add a one-line note about cross-platform shell compatibility for `/sdd-migrate-layout`'s bash-glob + parameter-expansion constructs, OR confirm the Claude Code shell normalizes this.

8. **(LOW)** Add a note acknowledging that user-repo CLAUDE.md files referencing `SDD/prompts/` become stale after migration; out-of-scope for this run but worth documenting in the SDD README's migration section as a "you may also want to update your project's CLAUDE.md" prompt.

## Verdict

**REVISE BEFORE PROCEEDING.** One HIGH gap (sdd/README.md scope) and three MEDIUM gaps (SKILL.md audit completeness, spec-review-panel deliverable schema, deferred design surfaces for the practicality gate and `## Slice Progress` schema). All gaps have concrete, scoped fixes. None require re-doing research or revisiting the locked decisions, the conservative defaults, or the recursion-trap. Once the eight Recommended Actions are folded into the research artifact, planning can proceed.

## Findings Addressed

Each finding from this review was resolved by a substantive (non-placeholder) edit to `SDD/research/RESEARCH-001-vertical-slicing-step-c.md`. The fix locations cite the section name and the change made.

### HIGH — `sdd/README.md` legacy references and directory tree not enumerated for rewrite

**Resolution:** Branch 6's `sdd/README.md` subsection (in the research) was extended with a new sub-subsection titled `#### Authoritative enumeration of legacy-path references in sdd/README.md (current 1.2.0 file)`. The fix contains: (a) a five-row table enumerating per-line touch points at lines 263 (`PROMPT` → `IMPLEMENTATION-PLAN`), 269 (two replacements: `SDD/prompts/test-audits/` → `SDD/implementation/test-audits/` and `PROMPT document` → `IMPLEMENTATION-PLAN document`), 379 (verified clean — no edit needed in current source), 392–411 (full directory-tree rewrite), and 492 (`PROMPT-[###]` → `IMPLEMENTATION-PLAN-[###]` in the numbering convention sentence), each with verbatim current text and resulting edited text; (b) a complete drop-in replacement directory tree for lines 392–411 mirroring the new layout (`research/`, `requirements/`, `reviews/`, `adr/`, `UBIQUITOUS_LANGUAGE.md`, `implementation/` with sub-trees including `slices/`, `orchestration/` with sub-trees); (c) six binding `grep -c` post-edit verification commands that MUST pass before declaring Branch 6 complete; (d) an additional bullet in the "Add a Changelog/Migration section" item covering user-repo CLAUDE.md staleness (LOW finding 8). **Where the fix lives:** research file, section "Branch 6 — Documentation surface" → "`sdd/README.md`" subsection, immediately after the three-item ordered list and before the `agent-engineering/README.md` subsection. Approximate line range: research lines 545–705 (post-edit).

### MEDIUM — SKILL.md audit missed two narrative-prose legacy references

**Resolution:** Branch 2's "Artifact Paths Contract" subsection was extended with a new sub-subsection titled `#### Narrative-prose legacy references (NOT in the table above — found by full grep)`. The fix contains: (a) a two-row table calling out lines 319 (Subagent Safety-Net Rule blockquote: `SDD/prompts/context-management/[phase]-compacted-…md` → `SDD/orchestration/compacted/[phase]-compacted-…md`) and 487 (Panel-review halt blockquote: `SDD/prompts/context-management/progress.md` → `SDD/orchestration/progress.md`) with verbatim current text and the exact edits required; (b) a binding directive that `grep -n 'prompts/\|PROMPT-' agent-engineering/skills/sdd-flow/SKILL.md` MUST return zero hits post-edit, and that this grep supersedes the per-line enumeration as the success criterion; (c) a "why these were missed" note explaining that future audits of the skill MUST use a full-file grep, not a section-scoped one. **Where the fix lives:** research file, section "Branch 2 — sdd-flow skill audit" → "Artifact Paths Contract (lines 60–136)" subsection, immediately after the existing per-entry table. Approximate line range: research lines 245–268 (post-edit).

### MEDIUM — spec-review-panel deliverable schema not updated for slice-integrity

**Resolution:** Branch 5 was extended with a new subsection titled `### Insertion point in sdd/commands/spec-review-panel.md deliverable schema (lines 230–244)`. The fix contains: (a) the verbatim current Document Structure block at lines 230–244 of `spec-review-panel.md` for reference; (b) the required-edit version showing the new `#### Slice Integrity Findings` sub-header inserted between `#### Module Depth Findings` and the `[Any additional specialists from the panel.]` placeholder, with an explicit conditional-rendering instruction inline; (c) a binding conditional-rendering rule stating the sub-header is rendered iff section 4.7's activation gate fired (and MUST be omitted entirely — not rendered with "n/a" — in whole-feature mode, preserving today's bit-for-bit deliverable shape); (d) confirmation that severity-aggregation rules at lines 196–200 apply unchanged (verified specialist-agnostic against current source); (e) cross-reference to section 4.7's "Output schema" line so the deliverable's content shape is bound to the security specialist's verbatim. **Where the fix lives:** research file, section "Branch 5 — Slice-integrity check additions to reviews", immediately after the existing "The synthesis rules at SECTION 5..." sentence and before the Branch 5 closing `---` separator. Approximate line range: research lines 547–605 (post-edit).

### MEDIUM — Practicality-gate detection logic and `## Slice Progress` table schema deferred to "see proposal §N"

**Resolution:** A new top-level section titled `## Authoritative design contracts (carried into the research, not deferred to the proposal)` was inserted between Branch 9 ("Test surface") and the "Files That Matter" section. The fix contains two subsections, each making a previously-deferred contract authoritative within the research itself:

- **`### Practicality-gate detection logic (binding for /planning-start Step 6)`** — defines four boolean heuristics that the planning subagent MUST evaluate (heuristic 1: single-module touch-set across all candidate slices when `## Modules` declares >1 module; heuristic 2: no thinner SLICE-001 candidate exists than the whole feature; heuristic 3: every candidate slice covers every REQ-XXX; heuristic 4: feature reduces to a single concentrated function with no internal sequencing). When ANY heuristic returns `true`, the gate fires. The action sequence is enumerated in four steps: populate `## Delivery Slices` with `Slicing not applicable: <reason>` audit-trail annotation citing the firing heuristic; append `## Awaiting Slicing Decision` block to `progress.md` mirroring `## Awaiting Clarification` exactly; surface the user-facing message naming the firing heuristic in supervised AND autonomous modes; record the gate decision in `progress.md` regardless (the audit trail anti-pattern #7 inspects). A judgment-call escape is defined for the rare case where none of the four boolean heuristics fires but the subagent still believes slicing is impractical.

- **`### ## Slice Progress table schema (binding for /implementation-start and /slice-retro)`** — declares document position (in the IMPLEMENTATION-PLAN, only in per-slice mode, after frontmatter and before per-slice work-log sections; entirely omitted in whole-feature mode), the canonical column schema (six columns: `SLICE-ID | Name | Status | Acceptance check | Test result | Notes`) with source-of-truth for each column, the canonical four-state enum (`Not Started`, `In Progress`, `Acceptance Check Passing`, `Complete` — verbatim strings), all forward state transitions and triggers, the no-backwards-transitions discipline (rework signals via the LEARNINGS ledger's `Open recommendations`, not via Status), an example minimal table for the IMPLEMENTATION-PLAN scaffold, and four binding consequences for downstream commands (`/implementation-start`, `/slice-retro`, `/sdd-flow` Phase Detection, the slice-integrity specialist's anti-pattern #4).

**Where the fix lives:** research file, new section `## Authoritative design contracts (carried into the research, not deferred to the proposal)` between Branch 9 and Files That Matter. Approximate line range: research lines 826–890 (post-edit).

### LOW — `commit.md` and `context-check.md` should be promoted from "verify" to "confirmed clean"

**Resolution:** the two corresponding rows in Branch 1's "Files that need path updates only" table were updated. Both rows now read `(zero hits — confirmed clean)` in the "Lines touched" column and in the "Update needed" column document the exact grep run (`grep -n 'prompts/\|PROMPT-' sdd/commands/<file>` → zero hits) and explicitly mark the status as "Promoted from 'verify' to 'confirmed clean.'" Verification was run during this fix run. **Where the fix lives:** research file, section "Branch 1 — SDD plugin command audit" → "Files that need path updates only" table, the two rows for `sdd/commands/context-check.md` and `sdd/commands/commit.md`. Approximate line range: research lines 179–180 (post-edit).

### LOW — Cross-platform shell compatibility for `/sdd-migrate-layout`

**Resolution:** Branch 4 was extended with a new subsection titled `### Cross-platform shell compatibility` inserted after "Hook-path coordination" and before the Branch 4 closing `---`. The fix names the bash-specific constructs in the move set (loops, test guards, the `${f//PROMPT-/IMPLEMENTATION-PLAN-}` parameter expansion which is bash 3.0+ not POSIX), specifies the obligation on the implementation phase to either rewrite shell-agnostic OR detect the host shell and refuse with a clear message rather than produce partial moves, recommends the second option with a concrete detection snippet (`command -v bash >/dev/null 2>&1 || { echo "ERROR: /sdd-migrate-layout requires bash. On Windows, run from Git Bash."; exit 1; }`), and binds the implementation phase to verify on at least one bash-compatible shell and document the Windows refusal path. **Where the fix lives:** research file, section "Branch 4 — Migration mechanics for `/sdd-migrate-layout`", immediately after "Hook-path coordination" subsection. Approximate line range: research lines 487–497 (post-edit).

### LOW — User-repo CLAUDE.md staleness acknowledgement in README migration section

**Resolution:** Branch 6's `sdd/README.md` Changelog/Migration section item gained an additional bullet acknowledging that any project-level `CLAUDE.md` (or `AGENTS.md`) referencing `SDD/prompts/...` paths becomes stale post-migration, that the migration helper does not touch user-authored docs, and that users should grep their own CLAUDE.md for `SDD/prompts/` and `PROMPT-` and update accordingly. The bullet explicitly marks this as out-of-scope for `/sdd-migrate-layout` itself but surfaces the issue so users do not get bitten silently. **Where the fix lives:** research file, section "Branch 6 — Documentation surface" → "`sdd/README.md`" subsection → item 3 ("Add a Changelog/Migration section"), as a new sub-bullet labeled "User-repo CLAUDE.md collateral." Approximate line range: research line 561 (post-edit).
