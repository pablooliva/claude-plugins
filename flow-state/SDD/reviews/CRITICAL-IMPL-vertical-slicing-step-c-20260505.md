# Implementation Critical Review: vertical-slicing-step-c

**Date:** 2026-05-05
**Implementation reviewed:** Step C of vertical-slicing-decomposition (SDD plugin 2.0.0 + agent-engineering 0.4.0)
**Code-review verdict:** APPROVED with fix-findings (Step 4c resolved F-1, F-2, F-3, F-4).
**This review's role:** Generalist adversarial review complementary to the spec-alignment code review — challenges assumptions, real-world correctness, technical robustness.

## Executive Summary

The implementation is substantively complete and the code-review (Step 4b) plus fix-findings (Step 4c) closed the spec-alignment gaps cleanly. The locked-region byte-identity invariant holds (verified by sha256 on lines 64–204; the 375–379 block content is byte-identical at HEAD lines 398–402 after the allowed-region insertions). The matcher contract (`/slice-retro` emits `^## Recommended SPEC Amendments$` / `^## Recommended Re-planning$`; SKILL.md grep targets the same strings) is byte-aligned. The migration helper's destructive-action posture is conservative (dry-run-by-default; fail-closed on parse failure; bash-detection refusal; `git mv` only). The F-1 narrative-prose drift, F-2 repo-root README gap, and F-3 Phase Detection rule gap from the code-review were all resolved on disk (verified by independent grep).

What this critical review surfaces is a different layer of risk that spec-alignment review cannot see: **assumption gaps that two reasonable engineers reading the same artifacts would resolve differently, and operational failure modes the spec did not enumerate.** Five MEDIUM and seven LOW findings below.

**Verdict:** PROCEED with awareness — none of the findings block the run, but several should be acknowledged in the implementation summary or addressed in a follow-up before SDD 2.0.0 is announced as release-ready (especially M-1 Phase Detection precedence ambiguity and M-2 retro-emitted halt-block divergence).

## Severity Counts

- **HIGH:** 0
- **MEDIUM:** 5 (M-1, M-2, M-3, M-4, M-5)
- **LOW:** 7 (L-1 through L-7)

## Specification Violations

None at HIGH severity. The 12 findings below are real-world failure modes the spec did not enumerate, ambiguities between paired files, or technical gaps in spec-conformant implementations. The implementation matches the spec; the spec itself underspecifies in several places that the implementation thus inherits.

## Technical Vulnerabilities

### M-1 [MEDIUM] — Phase Detection priority list: legacy-layout rule has ambiguous precedence vs. halt-block rules; AND/OR boolean is also ambiguous

**Location:** `agent-engineering/skills/sdd-flow/SKILL.md:725` and the priority list following.

**Issue 1 (precedence):** The Phase Detection list now reads (in order):

1. Old layout detected (legacy 1.x) → halt with migration prompt.
2. `## Awaiting Slicing Decision` → resume routing.
3. `## Recommended Re-planning` → resume routing.
4. `## Awaiting Re-start Decision` → resume routing.
5. … then the existing rules (Implementation Complete, etc.)

But rule 1 reads:

> if `SDD/prompts/context-management/progress.md` exists OR any `SDD/prompts/PROMPT-*.md` files exist AND `SDD/orchestration/progress.md` does NOT exist → emit migration prompt.

This rule fires whenever legacy artifacts exist regardless of whether new-layout halt blocks (rules 2–4) might also be relevant. Consider a user mid-migration: they have *both* legacy artifacts AND a new-layout `progress.md` with an `## Awaiting Slicing Decision` block (this is the partial-migration state the migration helper itself refuses with `--resume-partial`). Rule 1's `AND SDD/orchestration/progress.md does NOT exist` clause SHOULD short-circuit — but only if the AND/OR precedence is read correctly (see Issue 2 below). If a user has just begun running per-slice in a partly-migrated repo and hits a slicing-decision halt, the orchestrator's behavior depends on whether Phase Detection priority is read top-to-bottom-with-short-circuit (in which case rule 1 fires first if legacy artifacts exist) or "match the most specific halt-block first."

**Issue 2 (boolean ambiguity):** The line literally reads `if A exists OR B files exist AND C does NOT exist`. In Python/Bash precedence (AND binds tighter than OR), this parses as `A OR (B AND C-not-exists)` — meaning rule 1 fires when legacy progress.md exists *regardless of whether new-layout progress.md exists*. The author probably intended `(A OR B) AND C-not-exists`. Two reasonable engineers reading this will produce different orchestrator behavior on partly-migrated repos.

**Severity:** MEDIUM — this is the resumption-correctness load-bearing logic. A wrong reading produces either: (a) refusal to resume in-flight halt blocks until migration runs (annoying but recoverable) or (b) false-positive migration prompts during legitimate per-slice halts (confusing). Per the recursion-trap concern this very run lives in, the partly-migrated edge case is non-hypothetical.

**Recommended:** Re-write rule 1 with explicit parenthesization: `if (SDD/prompts/context-management/progress.md exists OR any SDD/prompts/PROMPT-*.md files exist) AND SDD/orchestration/progress.md does NOT exist`. Optionally also clarify whether rules 2–4 take precedence over rule 1 when both could match (the safer reading is "rule 1 only when new-layout has no progress.md, then check halt blocks").

### M-2 [MEDIUM] — Halt-block name divergence: `## Awaiting Re-planning Decision` (slice-retro emits) vs. `## Recommended Re-planning` (matcher / Phase Detection / migrate-layout grep)

**Location:** `sdd/commands/slice-retro.md:248` writes the halt block as `## Awaiting Re-planning Decision`. But:

- The retro-body section header is `## Recommended Re-planning` (slice-retro.md:126, the matcher-contract header).
- SKILL.md's matcher (line 668) greps `^## Recommended Re-planning$`.
- SKILL.md's Phase Detection (line 733) checks `## Recommended Re-planning block detected as the latest block in the most recent slice retrospective (and corresponding 'Re-planning recommended.' halt block in progress.md)`.
- `/sdd-migrate-layout` Step 3b's grep regex looks for `^## (Phase:|Awaiting |Recommended Re-planning|PARTIAL:)` in progress.md.

Three different strings are in play across paired files:
1. `## Recommended Re-planning` — the retro-body header (matcher contract; what the matcher expects to find in the retro file).
2. `## Awaiting Re-planning Decision` — what slice-retro Step 9 actually writes to `progress.md` as the halt block.
3. `Re-planning recommended.` — a prose phrase Phase Detection mentions as if it were a header.

The orchestrator looking at `progress.md` for a halt block expects to find `## Recommended Re-planning` (per M-1 SKILL.md line 733 phrasing) but `/slice-retro` actually wrote `## Awaiting Re-planning Decision` to progress.md (slice-retro.md:248). **The matcher in Phase Detection will not find what slice-retro emits.**

The migration helper's grep regex DOES include `Recommended Re-planning` but NOT `Awaiting Re-planning Decision` — so a user with a re-planning halt would have the migration helper *fail to detect the halt* and proceed (per Step 3c case (i): no halt detected → safe to migrate). Combined with the active-flow refusal's intent (refuse migration during in-flight flows), this is a missed-refusal case.

**Severity:** MEDIUM — the producer (slice-retro) and the consumers (Phase Detection, migrate-layout) don't agree on the halt-block string. The retro-body header IS consistently `## Recommended Re-planning` (good — the matcher contract for the retro FILE is sound). But the halt-block in progress.md is `## Awaiting Re-planning Decision`, which neither Phase Detection nor migrate-layout greps for. Real impact: an autonomous run that hits re-planning halts may not be detected on `/sdd-flow continue`; a user running migrate-layout post-halt would not be refused.

**Recommended:** Decide on ONE halt-block name and use it everywhere. The cleanest option: have slice-retro emit `## Recommended Re-planning` (mirroring the retro-body header and the matcher contract); update the migrate-layout grep to also recognize `Awaiting Re-planning Decision` as belt-and-suspenders.

### M-3 [MEDIUM] — Migration helper Step 7 rollback Option A is unsafe in `--resume-partial` mode

**Location:** `sdd/commands/sdd-migrate-layout.md:347` (Option A: `git reset --hard HEAD`).

The Option A rollback works by exploiting the precondition that `git status` was clean before the migration started (Step 4 enforces this). When Step 7 says *"Safe ONLY because pre-flight verified the working tree was clean. If you ran with `--allow-dirty`, this will also discard your other uncommitted edits."* — that is correct for `--allow-dirty`.

But `--resume-partial` mode adds a wrinkle the Step 7 recovery recipe doesn't address: if a *previous* migration run partially completed and committed nothing, the current `--resume-partial` run starts with a tree where some files have already moved (uncommitted, in the index from prior runs) and others have not. Running `git reset --hard HEAD` discards the prior run's pending moves entirely — *including the moves that DID succeed before the prior run crashed*. The user is restored to a state worse than the failure, because the prior partial-completion progress is silently lost.

The Step 7 recipe enumerates "successful moves before failure" *for this run* — but partial-migration recovery via `--resume-partial` may have prior-run moves that are not in this run's "successful" list.

**Severity:** MEDIUM — destructive in a recoverable-but-confusing way. The prior partial-migration's progress is in the git index (from prior `git mv`); `git reset --hard HEAD` discards index state. The user thinks they're rolling back this run; they're actually rolling back two runs' worth of moves.

**Recommended:** Document explicitly that Option A is *unsafe* under `--resume-partial` and that Option B (per-move inverse) or Option C (commit-what-succeeded) are the only safe rollbacks for partial-migration recovery. Or have the helper detect "in `--resume-partial` mode" and suppress Option A in the recovery recipe entirely.

### M-4 [MEDIUM] — `--reconcile-ledger` algorithm step 4 + step 5 can mis-classify user edits as orphan entries

**Location:** `sdd/commands/slice-retro.md:268+`, REQ-025a algorithm steps 4 and 5.

The algorithm's gist:
- Step 4: for each retro, if its learnings are not already in the ledger, append them.
- Step 5: ledger entries with no source retro are "PRESERVED but flagged as orphan."

The classifier for "is this entry in the ledger sourced from a retro?" relies on whether the retro's structured sections appear in the ledger's structured sections. But:

- Step 7 of `/slice-retro` (the consolidate-not-blind-append rule) explicitly REWRITES ledger entries when they refine existing ones — so the entry on disk in the ledger may have wording that does NOT byte-match any retro's wording (it's the consolidated form). When `--reconcile-ledger` re-derives, it may flag these legitimately-derived-but-rewritten entries as "orphan" and ask the user to decide.
- Step 5's escape ("preserve user-edited content") relies on detecting "no source retro on disk" — but if a retro on disk has been hand-edited too, the matcher will pass.

**Severity:** MEDIUM — the reconcile mode's primary value (rebuild ledger from authoritative retros without destroying user notes) is undermined when consolidation rules in `/slice-retro` Step 7 have rewritten ledger entries away from the literal retro text. False-orphan flags will appear after every reconcile run on a feature that has had any consolidation. Users will be unsure whether to keep, edit, or remove what is actually a legitimate consolidated entry.

**Recommended:** Either (a) constrain the consolidation rules in `/slice-retro` Step 7 to preserve a citation back to the originating SLICE-XXX (so the reconcile classifier checks for citations rather than text-matching), or (b) acknowledge in the algorithm that "orphan" is a heuristic flag and the rebuild output should explicitly say `> may be orphan OR consolidated; review` rather than the binary orphan/non-orphan classification.

### M-5 [MEDIUM] — `--replan` resumption behavior: spec says "from SLICE-001 by default" but the prior slices' code is already on disk and committed

**Location:** `agent-engineering/skills/sdd-flow/SKILL.md:672`; `sdd/commands/slice-retro.md:251` and 304.

The `--replan` flag re-runs Step 3 (planning) with the ledger and triggering retro in scope, producing a revised SPEC. Per spec REQ-014 + REQ-025: by default, implementation resumes from SLICE-001. Per REQ-025 + flag combination matrix: `--from-slice SLICE-XXX` lets the user resume from a different slice.

What the spec / commands do NOT clarify: when `--replan` resumes from SLICE-001, what happens to prior slices' code that has already been committed (per-slice 4c.6 atomic commits)? Two reasonable interpretations:
1. The orchestrator re-runs the slice cycle for SLICE-001 onwards starting from current HEAD — re-implementing on top of already-committed code that may now violate the revised SPEC. The first slice-review will catch this but only after re-implementing.
2. The orchestrator resets to the commit before SLICE-001 and re-implements. This is destructive of prior commits; not documented anywhere.

The user owns the judgment of which slices remain valid (per REQ-025 `--from-slice` semantics). But for `--replan` *without* `--from-slice`, the default is "from SLICE-001" — and if interpretation 1 is correct, that means the orchestrator implements SLICE-001 over the existing tree (which has SLICE-001..N already implemented under the OLD plan). The `## Slice Progress` table will show all rows as `Complete` from the prior plan; what does `/slice-start SLICE-001` do? Hit EDGE-013 (already-Complete refusal)? Or is the orchestrator expected to reset all rows to `Not Started` first?

**Severity:** MEDIUM — the `--replan` flow is one of the most complex user-facing recovery paths and the spec does not concretize the interaction with the `## Slice Progress` table state from the prior plan. A user who hits re-planning will discover this ambiguity at exactly the moment they're least equipped to deal with it.

**Recommended:** Document the `--replan` resumption contract concretely: does the orchestrator (a) reset the `## Slice Progress` table rows to `Not Started`, (b) require `--force` per-slice, (c) prompt the user to manually reset rows, or (d) something else? Add an example walk-through in the `/slice-retro` boundary-with-`/sdd-flow continue` table.

## Real-World Failure Modes

### L-1 [LOW] — Practicality gate heuristic 3 ("Universal-slice REQ touch") is technically vacuous when the SPEC has only one REQ

**Location:** `sdd/commands/planning-start.md:326`.

Heuristic 3 reads: *"Every REQ-XXX in the spec is touched by every plausible slice — i.e., the slices are not actually decomposable."* When the spec has exactly ONE REQ, every slice trivially touches that REQ (there's no other REQ to NOT touch), so heuristic 3 always returns true regardless of whether slicing is meaningful. This case is also already covered by heuristic 4 ("single concentrated function") and heuristic 1 ("single-MODULE touch-set" if all slices touch the same module). The redundancy is not harmful but heuristic 3 will fire spuriously for any single-REQ feature even when slicing IS practical (e.g., one REQ but the implementation has multiple meaningful end-to-end threads through different layers).

**Severity:** LOW — false-positive halt; recoverable via `--fall-back-to-whole-feature`. But the practicality gate's purpose is to AVOID needless halts, so a known-vacuous trigger contradicts intent.

### L-2 [LOW] — `LOG_SUBDIR` change is silent — old plugin install will log to legacy path indefinitely

**Location:** `sdd/hooks/log_subagent_call.py:18`; `sdd/commands/sdd-migrate-layout.md:329`.

The hook constant change is correct, but the plugin install model means an SDD 2.0.0 user who hasn't actually upgraded their installed plugin (they just have a checked-out copy at HEAD; the marketplace installation is still 1.x) will continue running the OLD hook with the OLD path. The `mkdir(parents=True, exist_ok=True)` semantic means the legacy dir gets silently re-created and split-tree forms. The migration helper's Step 6 output line 329 ("ensure your installed SDD plugin is at version 2.0.0") names this risk in prose, but it's a passive informational reminder — there is no runtime check that fires AFTER migration to detect the split-tree-forming hook. Users who skip the prose will silently produce a corrupted layout.

**Severity:** LOW — recoverable (manual `git mv`); not silent data-loss, just orphan logs. But discoverability of the symptom is poor; users may not notice for many flows.

**Recommended:** A best-effort post-migration check: re-run after the next subagent call to detect whether the legacy `SDD/prompts/context-management/subagent-calls/` directory was re-created. Stretch goal — not required.

### L-3 [LOW] — Migration helper's CLAUDE.md staleness scan is recursive without an `.gitignore`-style filter

**Location:** `sdd/commands/sdd-migrate-layout.md:368`.

```bash
for pattern in 'SDD/prompts/...' ...; do
  grep -rn -l "$pattern" --include='CLAUDE.md' --include='AGENTS.md' --include='CLAUDE.local.md' . 2>/dev/null
done | sort -u
```

The scan recurses from `.` (the repo root) without excluding `node_modules/`, `.venv/`, vendored dependencies, or *other plugin sources* that themselves reference `SDD/prompts/` legitimately. In a monorepo setup or one where users have committed reference copies of other plugins, the scan emits hits for files the user did not author and CANNOT fix without breaking the vendored plugin.

**Severity:** LOW — informational warning, no destructive action. But noisy false-positive scans will train users to ignore the warning.

**Recommended:** Constrain the recursion to a depth (`-maxdepth 3`) and exclude `node_modules`, `.venv`, `vendor/`, `dist/`, `build/`. Or document the limitation in the warning text.

### L-4 [LOW] — Slice-ID validation is duplicated in 4 files; if one drifts, the regex contract drifts silently

**Location:** `sdd/commands/slice-{start,review,retro,commit}.md` each contain `^SLICE-\d{3}$`.

Per MODULE-002's "Hides" section: "implementations SHOULD share a single `resolve-active-slice(expected_status_set)` helper rather than duplicating the lookup logic per command." This refers to the active-slice resolver — but the same DRY argument applies to the regex itself. Currently, four files each independently embed `^SLICE-\d{3}$`. A future change to allow 4-digit slice IDs (`SLICE-1234`) would require coordinated edits across all four; a partial edit produces inconsistent regex enforcement.

**Severity:** LOW — current state is correct. Risk is in maintenance.

**Recommended:** When the slice commands are modified next, factor the regex into a shared "Slice-ID validation" snippet referenced by each command (markdown include or just an explicit "see slice-start.md for the canonical regex" cross-reference).

### L-5 [LOW] — Concurrent invocation of `/sdd-migrate-layout` is undefined

**Location:** `sdd/commands/sdd-migrate-layout.md` (entire file).

Two concurrent invocations of `/sdd-migrate-layout --apply` against the same repo are not addressed. The bash script doesn't acquire a lockfile. If a user fires the command in two terminals or two simultaneous Claude Code sessions, both will reach Step 6 with `set -e` and both will issue `git mv` operations against overlapping paths. The second's `git mv` will fail (file moved already) and trigger Step 7 rollback against a tree the first invocation is still mutating — chaos.

**Severity:** LOW — operationally rare. Most users won't run two parallel migration helpers. But the helper claims "safe and idempotent re-runs" and concurrent-invocation safety is not the same as serial-idempotence.

**Recommended:** Acknowledge in the docs that `/sdd-migrate-layout` is not concurrent-safe and SHOULD be invoked serially. Or add a lockfile (`.git/sdd-migrate-layout.lock`) check at Step 0.

### L-6 [LOW] — `git status --porcelain` precondition (Step 4) does NOT detect submodule changes

**Location:** `sdd/commands/sdd-migrate-layout.md:166`.

`git status --porcelain` reports modified submodule references but not changes *inside* a submodule. If the user has a submodule under their working tree with uncommitted changes, the migration helper considers the working tree clean and proceeds. After migration, if Option A rollback fires, the submodule's uncommitted changes survive (good) but the user may have expected the precondition to catch them.

**Severity:** LOW — a corner case; most users don't have submodules. The precondition is approximately right.

**Recommended:** Add `git submodule status --recursive` to the precondition check, or document the limitation.

### L-7 [LOW] — `Inert-Mode` message wording: "Run `/implementation-start` instead" is misleading when the spec is malformed

**Location:** All four `/slice-*.md` Step 2 inert-mode message.

The message reads: *"This command requires `delivery_mode: per-slice` in the spec frontmatter. Current spec uses `delivery_mode: <value>`. Run `/implementation-start` instead, or set `delivery_mode: per-slice` in your spec and re-run `/planning-start`."*

If `<value>` is `whole-feature` or absent, the message is correct. But if `<value>` is invalid (per the REQ-001 validation branch), the slice command emits the *third* message branch: `Invalid delivery_mode value '<value>' in <spec-path>...`. Per slice-start.md:42 this is a separate message, NOT the inert-mode message, so users with invalid values get the right error. Good.

But: there's a subtle case where `delivery_mode` is NOT set but a typo elsewhere in the YAML frontmatter causes the parser to fail to find the field at all. Per the spec, that's the "absent → silent default to whole-feature" branch. The user who *intended* to set `per-slice` but typed `delvery_mode:` (typo) would see the inert-mode message saying their spec uses `delivery_mode: whole-feature (default; field absent)` — without any indication that there's a typo'd field nearby. The inert-mode message is technically correct but unhelpfully terse.

**Severity:** LOW — UX nit. Most users will catch the typo when they re-read their spec.

**Recommended:** Optional — when emitting the "field absent → default whole-feature" branch, consider grepping the frontmatter for any line containing `mode:` to detect typo'd field names. Stretch goal.

## Cross-Cutting Concerns

### C-1 — The matcher contract for `## Recommended Re-planning` is byte-aligned at producer/consumer for the *retro file* but NOT for *progress.md*

This is the M-2 finding above stated as a cross-cutting issue. The matcher contract has TWO surfaces (retro-body header AND progress.md halt block), and only ONE of them is verified byte-aligned across files. Future contributors will see the matcher and the retro template aligned and assume the contract is sound — without seeing that progress.md emits a different string.

### C-2 — The recursion-trap exception for `flow-state/SDD/...` is declared but not enforced anywhere in source code

This run's artifacts are at `flow-state/SDD/...`. The migration helper's hardcoded source paths (Step 5) reference `SDD/...` only. If a future user accidentally runs `/sdd-migrate-layout` from inside `flow-state/`, the helper will scan `SDD/...` (relative to wherever it's invoked) and may operate on the wrong tree. The recursion-trap warning lives in PROMPT trackers and subagent prompts but not in the migration helper's body.

**Severity:** Already covered in spec RISK-006 mitigation. Not a defect — but worth noting that the safety relies on user discipline, not on enforced invariants.

### C-3 — Bit-for-bit preservation of whole-feature flow: how would an external observer prove it?

The spec mandates "Whole-feature mode users see zero behavioral change beyond path strings." The verification path is the manual smoke flow + the closing-oracle greps + the locked-region byte-identity check. The locked-region invariant IS verified. But "behavioral identity" is not testable mechanically — it's an assertion. The implementation's edits to whole-feature 4a-4j (verified mechanical-only via `git diff` between Chunk 3 commit and HEAD) ARE confined to path strings and the new "Read delivery_mode and route" preamble. So the bit-for-bit claim is well-founded.

The risk: the smoke flow has not actually been run (it's an aspirational integration test, not an executed one). Future bugs in whole-feature mode introduced by Step C edits would surface only when a real user runs `/sdd-flow` against a real feature. The claim is well-grounded; the verification surface is narrower than the claim.

## Recommended Actions Before Merge

In priority order:

1. **M-1:** Re-write Phase Detection rule 1 with explicit parenthesization — `if (A OR B) AND C-not-exists`. ~5-line edit to `agent-engineering/skills/sdd-flow/SKILL.md:725`.
2. **M-2:** Reconcile the halt-block name divergence. Either change `/slice-retro` Step 9 to emit `## Recommended Re-planning` (2-line edit to `sdd/commands/slice-retro.md:248`) OR widen the migrate-layout grep + Phase Detection to recognize `## Awaiting Re-planning Decision` as well. The first option is cleaner.
3. **M-3:** Add a `--resume-partial` warning to migration Step 7 Option A — `git reset --hard HEAD` is unsafe in `--resume-partial` mode. ~3-line edit to `sdd/commands/sdd-migrate-layout.md:347`.
4. **M-5:** Document `--replan` resumption interaction with `## Slice Progress` table state from prior plan. Concretize in `/slice-retro` boundary section. ~10-line addition.
5. **M-4:** Acknowledge in the `--reconcile-ledger` algorithm that orphan-vs-consolidated is heuristic; flag entries with `> may be orphan OR consolidated; review` rather than binary orphan/not. ~3-line edit to `sdd/commands/slice-retro.md:268+`.
6. **L-1 through L-7:** Document; address opportunistically. None block the run.

## Verdict

**PROCEED.** All HIGH-severity surfaces (locked-region preservation, migration-helper destructive-action posture, slice-command path-traversal prevention, mode-routing bit-for-bit invariant) pass adversarial review. The MEDIUM findings are real but recoverable and surface mostly in edge cases (partly-migrated repos, re-planning resumption, concurrent invocations). The LOW findings are documentation hygiene + heuristic refinement.

The implementation is release-grade for the documented happy paths and the most common failure modes. M-1 and M-2 should be addressed before SDD 2.0.0 is announced as release-ready (they affect orchestrator correctness in halt-and-resume scenarios that real users WILL hit). M-3, M-4, M-5 should be follow-ups before the per-slice mode goes from "shipped" to "recommended."

The fixes from Step 4c (F-1, F-2, F-3, F-4) are confirmed durable on disk: `grep -n 'PROMPT document\|PROMPT tracking' agent-engineering/skills/sdd-flow/SKILL.md` returns zero hits; the Phase Detection priority list contains the three new resume-rules; the repo-root README has the version-coupling paragraph; the tracker checkboxes are aligned with on-disk state.

## Findings Addressed

This section records resolution of every finding raised above. Step 4e fix subagent ran on 2026-05-05.

### MEDIUM findings (5 of 5 resolved)

- **M-1 [MEDIUM] — Phase Detection rule 1 ambiguous AND/OR precedence.** RESOLVED. Edited `agent-engineering/skills/sdd-flow/SKILL.md` Phase Detection Priority section: rephrased rule 1 as a checklist with explicit `(C, must-be-true)` and `(A OR B, at least one must-be-true)` clauses, with explicit boolean-form annotation `(A OR B) AND C`. Also added explicit documentation of the partly-migrated case (when C is false but legacy artifacts present, the rule does NOT fire) so two reasonable engineers will read the rule the same way. Source-file edit: SKILL.md ~lines 753–763.

- **M-2 [MEDIUM, LOAD-BEARING] — Halt-block name divergence.** RESOLVED. The contract is now explicit two-stage:
  - **Retro-body header `## Recommended Re-planning`** lives ONLY in the retrospective ARTIFACT (`SDD/implementation/slices/RETROSPECTIVE-SLICE-XXX-...md`), written by `/slice-retro` Step 6.
  - **Progress.md halt block `## Awaiting Re-planning Decision`** is written by the **orchestrator** (per-slice 4c.5 Stage 1) when its matcher detects `## Recommended Re-planning` in the retro. `/slice-retro` does NOT touch this block.
  - **Phase Detection (Session Resumption)** reads progress.md for `## Awaiting Re-planning Decision` (Stage 2).

  Source-file edits: (1) `sdd/commands/slice-retro.md` Step 9 — removed the `## Awaiting Re-planning Decision` halt-block emission; replaced with a "Two-stage matcher contract" subsection clarifying that the orchestrator (NOT `/slice-retro`) is the producer of the progress-block. (2) `agent-engineering/skills/sdd-flow/SKILL.md` per-slice 4c.5 — added the "Two-stage matcher contract" subsection documenting Stage 1 (orchestrator writes `## Awaiting Re-planning Decision` to progress.md when `^## Recommended Re-planning$` is matched in the retro) and Stage 2 (Phase Detection on resume reads progress.md for `## Awaiting Re-planning Decision`). The exact halt-block content the orchestrator writes is included in a fenced markdown example. (3) `agent-engineering/skills/sdd-flow/SKILL.md` Phase Detection Priority — bullet renamed and updated from `## Recommended Re-planning block detected ...` to `## Awaiting Re-planning Decision block detected ...` (the progress-block name). (4) EDGE-006 description updated to use `## Awaiting Re-planning Decision` (the progress-block name) instead of `## Recommended Re-planning`. (5) `sdd/commands/sdd-migrate-layout.md` Step 3b — extended the alternative-active-headings list to include `## Awaiting Re-planning Decision` and `## Awaiting Re-start Decision` for belt-and-suspenders refusal coverage; the bash regex `^## (Phase:|Awaiting |Recommended Re-planning|PARTIAL:)` already covers `Awaiting *` and `Recommended Re-planning` via prefix-match, so no regex change was needed (the list was just stale).

  Verification grep oracles all pass:
  - `grep -E "^## Recommended Re-planning" sdd/commands/slice-retro.md` → 1 hit (the retro-body header definition).
  - `grep -nE "Recommended Re-planning" agent-engineering/skills/sdd-flow/SKILL.md` → 4 hits, all in the per-slice-cycle matcher / Stage-1 description (NONE in Phase Detection Priority).
  - `grep -nE "Awaiting Re-planning Decision" agent-engineering/skills/sdd-flow/SKILL.md` → 5 hits (per-slice 4c.5 Stage 1 emission, Stage 2 cross-ref, EDGE-006, and Phase Detection bullet).
  - `grep -nE "Awaiting Re-planning Decision" sdd/commands/slice-retro.md` → 3 hits, ALL clearly labeled as cross-references noting "the orchestrator's responsibility" (no producer-side claim).

- **M-3 [MEDIUM] — Migration helper Step 7 Option A unsafe in `--resume-partial`.** RESOLVED. Edited `sdd/commands/sdd-migrate-layout.md` Step 7 to detect the active mode (pre-flight-clean vs. `--resume-partial` vs. `--allow-dirty`) and surface a mode-aware rollback recipe. In `--resume-partial` mode, Option A is explicitly suppressed with a `⚠️ UNSAFE` warning explaining that `git reset --hard HEAD` would discard the prior run's already-staged moves. Option B (per-move inverse, scoped to THIS run only) is the recommended path in `--resume-partial` mode. Each mode now has its own enumerated Option A/B/C with mode-specific safety notes.

- **M-4 [MEDIUM] — `--reconcile-ledger` mis-classifies consolidated entries.** RESOLVED. Edited `sdd/commands/slice-retro.md` to introduce a `Sources:` field convention on every ledger entry: each consolidated entry lists its contributing SLICE-XXX values (e.g., `Sources: SLICE-001, SLICE-003`); user-authored manual entries carry no `Sources:` field. The reconcile algorithm Step 3 was rewritten from "literal text match" to "check whether the retro's SLICE-XXX appears in any ledger entry's `Sources:` field." Step 5's orphan classifier now keys on the absence of `Sources:` (manual edits) rather than absence of a retro-text match. The ledger scaffolding template documents the convention. Backward-compatibility note added for legacy ledgers predating the convention.

- **M-5 [MEDIUM] — `--replan` from SLICE-001 default doesn't concretize Slice Progress state.** RESOLVED. Edited `agent-engineering/skills/sdd-flow/SKILL.md` Phase Detection Priority `## Awaiting Re-planning Decision` bullet to document the state-management contract for `--replan` (and `--replan --from-slice`). Concretely:
  - The orchestrator preserves the OLD `## Slice Progress` table as `## Archived Slice Progress (pre-replan)` (audit trail; never deleted).
  - After Step 3 re-planning produces the revised SPEC, a FRESH `## Slice Progress` table is written reflecting the NEW plan's `## Delivery Slices`, all rows initialized to `Status: Not Started`.
  - Old per-slice review docs / retros / ledger entries / atomic commits are NOT auto-deleted or auto-reverted. The user owns judgment of which prior work to keep.
  - `--from-slice` validates AGAINST THE NEW SPEC's `## Delivery Slices` (not the old plan's) — runs after the re-planning subagent produces the revised SPEC. Invalid → fail with clear error.
  - Default behavior (no `--from-slice`): all rows fresh `Not Started`. Explicit `--from-slice`: the named slice and prior slices stay `Not Started` by default; user can manually mark prior rows `Complete` post-init if they want to skip them.

### LOW findings (7 of 7 resolved)

- **L-1 — Practicality heuristic 3 vacuous on single-REQ specs.** RESOLVED. Edited `sdd/commands/planning-start.md` Step 8 heuristic 3 to add: *"Disable this heuristic when the spec has exactly one REQ — with a single-REQ spec, every slice trivially touches that REQ, and heuristic 3 would fire spuriously regardless. The single-REQ case is already covered by heuristic 4 (single concentrated function)."*

- **L-2 — `LOG_SUBDIR` change silent on un-upgraded plugin install.** RESOLVED. Edited `sdd/commands/sdd-migrate-layout.md` post-migration output to include a best-effort split-tree detection bash snippet (run manually after the next subagent call) that prints `ANOMALY:` if the legacy `SDD/prompts/context-management/subagent-calls/` directory reappears, indicating the installed plugin is still on the pre-2.0.0 hook.

- **L-3 — CLAUDE.md staleness scan unbounded recursion.** RESOLVED. Edited `sdd/commands/sdd-migrate-layout.md` Step 8 staleness scan: replaced `grep -rn` with `find -maxdepth 3 ... -prune` excluding `node_modules`, `.venv`, `venv`, `vendor`, `dist`, `build`, `.git`. Documentation note added that vendored third-party plugin sources beyond depth 3 are intentionally not flagged (cannot be fixed without breaking the vendored plugin).

- **L-4 — Slice-ID regex duplicated in 4 files.** RESOLVED. Designated `slice-start.md` § "Slice-ID Validation" as the canonical home for `^SLICE-\d{3}$`. Added cross-reference notes to `slice-review.md`, `slice-retro.md`, and `slice-commit.md` instructing future contributors that any change (e.g., 4-digit slice IDs) MUST be coordinated across all four files in a single commit.

- **L-5 — Concurrent invocation of `/sdd-migrate-layout` undefined.** RESOLVED. Edited `sdd/commands/sdd-migrate-layout.md` to add a "Concurrent-invocation note" section before Step 0, explicitly stating: `/sdd-migrate-layout` is NOT concurrent-safe; the helper's "safe and idempotent re-runs" guarantee is serial-idempotence, not concurrent-safety; users should run sequentially.

- **L-6 — `git status --porcelain` doesn't detect submodule changes.** RESOLVED. Edited `sdd/commands/sdd-migrate-layout.md` Step 4 to add a "Submodule limitation" callout naming the gap and recommending `git submodule status --recursive` for users with submodules.

- **L-7 — Inert-Mode message terse on typo'd field name.** RESOLVED. Edited `sdd/commands/slice-start.md` Step 2 "field absent → default `whole-feature`" branch to add a typo-detection hint: when emitting the inert message, also grep the spec frontmatter for any line containing `mode:` (case-insensitive); if a near-miss field is found (e.g., `delvery_mode:`), append a one-line hint to the inert message indicating a possible typo. The hint is informational; the inert-message text itself is unchanged.

### Cross-cutting concerns

- **C-1** — Restated as M-2; resolved alongside M-2 via the explicit two-stage matcher contract.
- **C-2** — Acknowledged; not a defect. Recursion-trap exception for `flow-state/SDD/...` continues to rely on user discipline (this run's prompt repeats the recursion-trap warning in subagent prompts; future runs operating under the new layout will not need the exception).
- **C-3** — Acknowledged; not a defect. The bit-for-bit preservation claim for whole-feature mode is well-grounded by mechanical-only diff verification on Step C edits. Smoke-flow integration testing remains future work.

### Verification posture

All MEDIUM and LOW findings have a corresponding source-file edit. The implementation is now release-grade for both the happy paths AND the documented failure modes the original review surfaced. The remaining unresolved item is C-3's smoke-flow execution (out-of-scope — this is observation testing, not a code fix).
