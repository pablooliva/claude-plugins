# Specification Critical Review: vertical-slicing-step-c

**Date:** 2026-05-05
**Spec reviewed:** SDD/requirements/SPEC-001-vertical-slicing-step-c.md
**Iteration-2 panel verdict:** PROCEED (HIGH=0, MEDIUM=0, LOW=6 outstanding — 2 new + 4 deferred)
**This review's role:** Generalist adversarial review complementary to the specialist panel — challenges assumptions, scope, and logic across the whole spec. Looks for what the four named specialists (security / data-modeling / api-contract / module-depth) systematically would NOT have looked for: cross-cutting logical contradictions, fix-time inventions ungrounded in research, glue-language between requirements, and interaction effects between this feature and the surrounding workflow.

## Executive Summary

The spec is in materially good shape. Two iterations of panel review + a fix subagent have closed the MEDIUM tier and forced both happy-path and several degenerate states into spec form. The remaining gaps are not architectural — they fall in three buckets:

1. **Fix-time invention without research grounding** — three CLI flags (`--resume`, `--force`, `--reconcile-ledger`) and one option set (`--fall-back-to-whole-feature`, `--retry-slicing`, `--replan`, `--from-slice`, `--override-replan`) emerged across iterations without a research entry naming them. The `--reconcile-ledger` flag is grounded (research §Q-E names reconcile mode in prose). The `--force` flag is fix-time invention. None has a counterpart in existing SDD plugin convention (zero existing `--force` usage across `sdd/commands/`). This is a **MEDIUM** finding — not a behavior bug today, but a convention the next contributor will inherit and a place where two engineers will produce different code.
2. **Self-consistency holes in the migration / version-skew story** — the in-flight-upgrade scenario (FAIL-002) describes legacy-path fallback in Phase Detection, but the cross-plugin version-coupling story (SDD 2.0.0 + agent-engineering 0.4.0) is not reflexively addressed in spec form. A user on SDD 2.0.0 + agent-engineering 0.3.x is a plausible state and the spec is silent on it. **MEDIUM** finding.
3. **Underspecified "when" for several disciplined verifications** — REQ-020 says glossary discipline is maintained but does not say at which implementation step new terms (if discovered) are added; the closing-oracle grep is named as binding (REQ-016) but not tied to a specific "before declaring step N done" gate; the Step A locked-region check is binding but no acceptance test grep-asserts it post-implementation. These are **LOW**-tier and individually small but collectively raise the chance of a "we said we'd verify, we forgot" outcome.

**Counts:** HIGH=0, MEDIUM=2, LOW=5 (plus the 6 carried from the panel — those remain out-of-scope here, panel-resolved).

**Verdict:** REVISE BEFORE PROCEEDING. The two MEDIUMs are local edits (one paragraph apiece in the appropriate REQ/MODULE entry) and do not require re-running the panel. Once addressed, PROCEED is appropriate.

## Severity: MEDIUM

## Ambiguities That Will Cause Problems

### A-1. **MEDIUM** — Flag-convention drift between fix-time inventions and existing SDD plugin convention

- **Location:** REQ-005 (`--reconcile-ledger`), EDGE-012 (`--resume`), EDGE-013 (`--force`), REQ-014 (`--replan`, `--from-slice`, `--override-replan`), REQ-023 (`--fall-back-to-whole-feature`, `--retry-slicing`).
- **What's unclear:**
  1. Existing `sdd/commands/` has zero `--force` usage today (verified by grep). The spec's `--force` is therefore not borrowing an established convention but is *establishing one*. Two reasonable engineers reading EDGE-013 will produce different implementations: one will add `--force` as an explicit `[--force]` arg in the command's frontmatter / argument table; another will read it as "an interactive `y/n` prompt where 'y' is the affirmative". The panel partially flagged the supervised-vs-autonomous gap, but the more general issue — *what does `--force` mean as a project convention?* — is unsurfaced.
  2. The flag-trio for `/sdd-flow continue` (`--replan`, `--from-slice SLICE-XXX`, `--override-replan`) is documented as resume options but the **mutual-exclusion semantics** are not pinned down: REQ-014 lists three options without saying whether `--from-slice` requires `--replan` (it only makes sense in that context), whether `--from-slice` and `--override-replan` are exclusive, and whether `--replan` may be combined with `--override-replan`. The panel flagged this as the "deferred LOW panel action 11" but left it unresolved.
  3. `--reconcile-ledger` has the strongest grounding (research §Q-E + EDGE-007 + FAIL-003), but it's still introduced in the spec with no design rationale for the flag *name*. Why not `--rebuild-ledger`, `--repair-ledger`, `--sync-ledger`? An implementer reading the spec gets the *behavior* but not the *naming convention*; if future work adds `--reconcile-progress` or `--reconcile-counters`, the convention should be already pinned.
- **Possible interpretations:**
  - (A) `--force` is a positional CLI flag in the command's argument frontmatter; the command body checks for its presence; no interactive prompt.
  - (B) `--force` is a CLI flag AND in supervised mode the user gets an interactive `y/n` prompt where "y" is treated as `--force`-equivalent.
  - (C) `--force` exists only as a CLI flag; the "or affirmative interactive confirmation" clause means a *separate* interactive code path that does not pass through `--force` at all.
- **Recommendation:**
  - Add a new sub-block to REQ-006 (or a new REQ near REQ-024) titled "Slice-command flag conventions" that pins down: every `--<flag>` is a literal CLI argument; absence is the default behavior; supervised-mode interactive prompts produce a flag-equivalent decision; autonomous mode without the flag halts via the documented awaiting-decision-block pattern (REQ-011 halt shape). Cite this REQ as the binding reference from EDGE-012, EDGE-013, EDGE-014, REQ-005, REQ-014, REQ-023.
  - Resolve the three combination matrix questions for `/sdd-flow continue` flags inline in REQ-014, in a one-paragraph "Flag combination semantics" block. The panel-deferred LOW becomes a closed item.
  - Add one sentence in REQ-005 explaining the `--reconcile-` prefix as the convention for "reconstruct derived state from authoritative sources" so future flags slot in cleanly.

### A-2. **MEDIUM** — Cross-plugin version coupling not addressed for the SDD 2.0.0 + agent-engineering 0.3.x mismatch state

- **Location:** REQ-018 (version bumps), FAIL-002 (in-flight upgrade), and conceptually MODULE-008.
- **What's unclear:** The spec increments SDD plugin → 2.0.0 and agent-engineering → 0.4.0 in lockstep, but plugin installation in this marketplace is independent: a user can install SDD 2.0.0 without updating agent-engineering, and vice versa. The 0.3.x sdd-flow skill embeds the legacy SDD 1.x path strings and lacks the per-slice Step 4 state machine. A user on SDD 2.0.0 + agent-engineering 0.3.x will see:
  - SDD commands emitting NEW paths (`SDD/implementation/...`, `IMPLEMENTATION-PLAN-XXX-...`).
  - sdd-flow Phase Detection looking for OLD paths (`SDD/prompts/...`, `PROMPT-XXX-...`).
  - `delivery_mode: per-slice` set in the spec but no Step 4 state machine to honor it.
- **Why it matters:** This is a plausible install-order. The marketplace.json publishes both bumps in the same commit, but `/plugin install` is per-plugin. The panel's "FAIL-002" addresses the *intra*-SDD case (legacy paths during in-flight migration) but not the *inter*-plugin case (skill version skew).
- **Possible behaviors today (not specified):**
  - (A) sdd-flow 0.3.x silently fails (Phase Detection finds nothing → "no active phase").
  - (B) sdd-flow 0.3.x writes to OLD paths while SDD 2.0.0 writes to NEW paths → split tree.
  - (C) Some unstated detection halts gracefully.
- **Recommendation:** Add a new FAIL-009 "Version-skew between SDD plugin and agent-engineering sdd-flow skill" that:
  - Documents the detection: when sdd-flow's Phase Detection finds NEITHER the new path NOR the legacy path AND a recently-installed SDD 2.0.0 marker is present (e.g., the `IMPLEMENTATION-PLAN-XXX` filename pattern in `SDD/implementation/`), emit a one-time message: *"Detected SDD 2.0.0 artifacts but sdd-flow appears to be on a pre-0.4.0 version. Update agent-engineering to 0.4.0+ via `/plugin install agent-engineering` before continuing."*
  - References SDD plugin's README changelog/migration section adding a "you must also update agent-engineering" line.
  - Calls out in REQ-019 README that the changelog explicitly warns about this coupling.

## Missing Specifications

### M-1. **LOW** — Glossary update timing during implementation is unstated

- **Location:** REQ-020.
- **What's not specified:** REQ-020 says "Implementation must not introduce new terms without adding them to the glossary." But it does not say WHEN — at file-edit time? At end of implementation phase? Per-module? Per-step in the Suggested Approach?
- **Why it matters:** The Suggested Approach (lines 433–444) lists 12 steps. Step 7 ("New command authoring") is the most likely place new terminology surfaces (e.g., "reconcile mode", "active-flow refusal", "concentrated function summary"). A subagent implementing step 7 may not pause to update `UBIQUITOUS_LANGUAGE.md`; the discipline becomes a "we'll do it at the end" task that gets dropped.
- **Suggested addition:** Extend REQ-020 with a single sentence: *"Glossary additions, if any are required, MUST be made in the same step (and same commit) as the source-code edit that introduces the new term — never deferred to a 'documentation pass' step at the end of implementation."* Add a bullet to Manual Verification: *"`grep -n` any new terms appearing in command bodies / SKILL.md against `UBIQUITOUS_LANGUAGE.md`."*

### M-2. **LOW** — Step A locked-region invariant has no post-implementation acceptance test

- **Location:** REQ-001 (which cites the locked region), Implementation Constraints, Manual Verification.
- **What's not specified:** The Manual Verification section says: *"Step A locked region in `sdd/commands/planning-start.md` is unchanged. Verification: `git diff` on the file shows zero changes to lines 64–204 and 375–379."* But this is a manual `git diff` reading, not an acceptance check that fires automatically (or even semi-automatically). For a feature whose spec opens with "Step A is OFF-LIMITS," a 12-line shell oracle would mechanically prove the invariant.
- **Why it matters:** "Read the diff" is exactly the kind of step that gets done at midnight by an implementer who is sure they didn't touch those lines. A grep-based or `git show` line-range oracle removes the human-judgment failure mode.
- **Suggested addition:** Add a single concrete oracle to Manual Verification: `git show <pre-impl-commit>:sdd/commands/planning-start.md | sed -n '64,204p;375,379p' | sha256sum` should match `git show <post-impl-commit>:sdd/commands/planning-start.md | sed -n '64,204p;375,379p' | sha256sum`. Or simpler: `git diff <pre-impl-commit> -- sdd/commands/planning-start.md | grep -E '^[+-]' | grep -E ':(6[4-9]|[7-9][0-9]|1[0-9][0-9]|20[0-4]|37[5-9])'` → if non-empty, fail. Cite the oracle once, in REQ-001 and in Manual Verification.

### M-3. **LOW** — Closing-oracle grep is named "binding" but no implementation step explicitly invokes it

- **Location:** REQ-016 (defines the oracle), MODULE-007 (cross-references), Critical Implementation Considerations (line 454, says "Every modified file MUST pass `grep -n 'prompts/\|PROMPT-'` returning zero hits before being declared verified").
- **What's not specified:** The oracle is a binding criterion, but the Suggested Approach doesn't tie it to a specific gate ("after step 2", "after step 4", "before commit N"). An implementer working through the 12 steps may run the grep at the end of the whole pass, discover dozens of misses across many files, and have to backtrack. Worse: an implementer may not run it at all and rely on "I think I caught everything."
- **Why it matters:** The grep is the actual verification primitive for the entire restructure. It should be unambiguously the "definition of done" for each step that touches paths.
- **Suggested addition:** Append a one-liner to each path-touching step in the Suggested Approach: *"Definition-of-done for this step: `grep -n 'prompts/\|PROMPT-' <file(s) touched in this step>` returns zero hits (or only intentional historical references in README changelog with explicit deprecation framing)."* Steps 2, 3, 4, 5, 6, 8, 11 all qualify.

### M-4. **LOW** — `--reconcile-ledger` mode behavior is named but not specified

- **Location:** REQ-005, EDGE-007, FAIL-003, EDGE-014.
- **What's not specified:** Multiple entries reference `/slice-retro --reconcile-ledger` as the recovery / refresh path. None of them specifies what reconcile mode actually DOES algorithmically. Specifically:
  - Does it overwrite the ledger from scratch using only retros on disk, or does it merge the existing ledger with retro contents?
  - If the existing ledger has entries that have no corresponding retro on disk (e.g., a manual-edit added them), are those preserved?
  - What's the output? (A diff? A confirmation? Just silently rewrite?)
  - Is the input scope all retros for the feature, or just the named SLICE-XXX's retro?
- **Why it matters:** "reconcile from existing retros" is fine as user-facing mental model but is the kind of phrase where two engineers will produce divergent behavior. One implementer may write a destructive rebuild; another may write a careful merge. The audit-trail invariant from REQ-005 (retros are "never modified after writing") implies the *retros* are authoritative, but doesn't say the ledger is non-authoritative.
- **Suggested addition:** Extend REQ-005's re-invocation policy block (or add a new REQ-005a) with a paragraph: *"`--reconcile-ledger` semantics: re-read every `RETROSPECTIVE-SLICE-XXX-...md` for the current feature; rebuild `LEARNINGS-FEATURE-[feature-name].md` by consolidating their structured sections (Recommended SPEC Amendments, Recommended Re-planning, ledger-update sections); manual-edit-only entries that have no retro source are PRESERVED (the ledger is not destroyed) but flagged in the rebuild output as 'orphan entries'. Output: a diff between pre- and post-reconcile ledger; user confirms before write. Scope: all retros for the active feature, not just the named slice."*

### M-5. **LOW** — Practicality-gate qualitative-judgment escape lacks an audit-test for the prefix

- **Location:** REQ-011.
- **What's not specified:** REQ-011 (per L-4 resolution) requires the prefix `Qualitative judgment: ` on the `<reason>` text when the qualitative-judgment escape fires. But there's no Manual Verification entry that grep-asserts the prefix is present in the relevant artifacts (`progress.md`, `## Delivery Slices` annotation). An implementer can perfectly document the rule in the planning-start.md Step 6 extension and still have a subagent at runtime forget to apply it.
- **Why it matters:** The audit-trail invariant is only as strong as its enforcement. The boolean-heuristic firings can be tied to specific heuristic-name strings; the qualitative-judgment firings are exactly the ones most likely to drift in wording.
- **Suggested addition:** Add to Manual Verification: *"In any tree where the practicality-gate fired qualitatively, `grep -n 'Qualitative judgment: ' SDD/orchestration/progress.md` and the relevant `## Delivery Slices` annotation MUST find the literal prefix. (Synthetic-tree manual test only — no automated runtime check.)"*

## Research Disconnects

### R-1. The `--reconcile-ledger` flag exists in research only as descriptive prose ("reconcile mode") — the spec promotes it to a CLI flag

- **Research location:** RESEARCH §Q-E (line 174 of CLARIFICATION; research §Branch 3 `/slice-retro` Recovery section, ~line 355).
- **Research wording:** *"the next `/slice-retro` invocation (or a manual `/slice-retro --reconcile-ledger`) detects 'ledger missing entries from existing retros' and reconciles."*
- **Spec wording:** REQ-005 / EDGE-007 / FAIL-003 / EDGE-014 all use `--reconcile-ledger` as a literal CLI flag.
- **Disconnect:** Research used the flag name in passing prose; the spec promotes it to authoritative API. There is no research entry that *designs* the flag (semantics, arg shape, output, interaction with the auto-detect path). This was inherited as "we said this in research, so it's a flag now," which is a thin grounding.
- **Impact:** Low-medium. The flag name is reasonable and the behavior intent is clear from prose. But this is the pattern that produced both `--force` (no research grounding at all) and `--reconcile-ledger` (research-grounded only by passing reference). The spec should either own the flag-design or push back to research. Owning it is faster — see M-4.

### R-2. Research Branch 3 `/slice-start` says "fallback to in-progress slice in IMPLEMENTATION-PLAN" — spec says "fallback to first `Not Started` row"

- **Research location:** RESEARCH §Branch 3 `/slice-start` (line ~330): *"prefer CLI arg if provided. Fallback: read the IMPLEMENTATION-PLAN's `## Slice Progress` table and find the next slice with status `Not Started`."* But also `/slice-review` line 338: *"prefer CLI arg, fallback to 'current in-progress slice in IMPLEMENTATION-PLAN'."*
- **Spec location:** REQ-003 says `/slice-start` falls back to "first `Not Started` row"; EDGE-012 says re-invoking while another slice is `In Progress` refuses with `--resume` as the path.
- **Disconnect:** The two commands have *different* fallback semantics. `/slice-start` falls back to `Not Started`; `/slice-review` falls back to `In Progress`. This is internally consistent (you start what's not started; you review what's in progress) but the spec doesn't surface this asymmetry as a design point. An implementer reading the two commands will likely produce a shared "find active slice" helper that picks one or the other; if they pick wrong, both commands break.
- **Impact:** Low. The semantics are right, just under-articulated. **Suggested addition:** Add one sentence to MODULE-002 Hides explicitly stating the asymmetry: *"The active-slice resolution algorithm differs by command: `/slice-start` defaults to the first `Not Started` row (you can't start what's already running); `/slice-review`, `/slice-retro`, `/slice-commit` default to the `In Progress` row (you can't review/retro/commit something not yet implemented)."*

### R-3. Research §Q-D (resume-from-slice validity) has no spec coverage

- **Research location:** CLARIFICATION OQ-D / research equivalents: *"When a re-planning recommendation fires and the user runs `/sdd-flow continue --replan`, the proposal says implementation resumes 'from `SLICE-001` (or from a user-specified slice if some completed slices remain valid).' How is 'completed slices remain valid' assessed? Default: user judgment, surfaced in the resume prompt. The orchestrator does not auto-determine validity."*
- **Spec coverage:** REQ-014 lists `--replan --from-slice SLICE-XXX` as a resume option but does NOT specify how the user's choice of `SLICE-XXX` is validated, what happens if the user picks a slice that's not yet implemented, or what the resume prompt's guidance text is.
- **Impact:** Low. The conservative default ("user judgment") is reasonable but the absence of any guard against `--from-slice SLICE-999` (nonexistent slice) means an implementer will either (a) write a regex check and refuse, or (b) pass through silently and produce a confusing "no slice found" error mid-flow. **Suggested addition:** Extend REQ-014 with: *"`--from-slice SLICE-XXX` validates the slice ID against the IMPLEMENTATION-PLAN's `## Slice Progress` table; non-existent IDs refuse with the same message-discipline shape as REQ-007. The user owns the judgment of which slices remain valid; the orchestrator only validates existence."*

### R-4. Stakeholder validation gap: "Plugin maintainers" not addressed for cross-plugin version coupling

- **Research location:** RESEARCH §Stakeholder Perspectives §"Plugin marketplace operators" addresses version drift WITHIN one plugin's two manifests; does not address cross-plugin coupling.
- **Spec coverage:** Stakeholder Validation in spec line 51–55 names plugin marketplace operators but inherits the same scope.
- **Disconnect:** This is the same observation as A-2 above, surfaced as a stakeholder-needs gap. The "users on SDD 2.0.0 + agent-engineering 0.3.x" stakeholder has no validated need addressed.

## Risk Reassessment

- **RISK-002 (Mode-routing bug):** Currently rated `medium`. **Reassess: keep at medium**, but note the blast radius: the bit-for-bit-preservation invariant for whole-feature mode is tested ONLY by the manual smoke flow (Validation Strategy §Integration Tests). No oracle compares pre-2.0.0 output paths to post-2.0.0 output paths bit-for-bit. A mode-routing bug + a smoke flow that passes for the wrong reason (e.g., a different artifact landing at a similar path) could ship undetected. **Mitigation suggestion:** the whole-feature smoke flow's manual verification should include `git diff --stat` of the artifacts produced by an equivalent 1.2.0 run vs a 2.0.0 run, modulo the path-prefix change. Document this in Validation Strategy.
- **RISK-003 (Migration helper destructive on user repo):** Currently rated `high`. **Reassess: keep at high**, but the rating was given before SEC-002's fail-closed posture was added. The fail-closed posture *reduces* the effective risk substantially; the rating should be re-explained, not re-rated. **Suggested addition:** Append to RISK-003 mitigation: *"Post-iteration-2: SEC-002 fail-closed posture on `progress.md` parse failure (per panel security MEDIUM, EDGE-015, FAIL-008) closes the major remaining failure mode of 'silent proceed on corrupt safety-check input'. The risk remains high in nominal severity (data-loss class) but the empirical likelihood is now bounded by the bash-detection refusal + active-flow refusal + parse-failure refusal + partial-migration refusal — four-way fail-closed."*
- **RISK-006 (Recursion-trap during this run):** Currently rated implicit. **Reassess: explicitly LOW** because every phase prompt has been observed to embed the warning verbatim, this run's artifacts have stayed at `flow-state/SDD/...` legacy paths through three phases, and Step 3d (this review) is itself respecting the recursion-trap. The mitigation is empirically working; the residual risk is low.
- **MODULE-005 (Migration helper) at risk: high** — correctly rated. The helper is a one-shot destructive operation on user repos. Acknowledging.
- **MODULE-007 (Directory restructure + rename) at risk: medium** — re-examined. The blast radius (every plugin command, the skill, the hook, four manifests, three READMEs) means a partial restructure breaks Session Resumption AND user-CLAUDE.md lookups. The grep oracle is the verification primitive but is not gated to a specific implementation step (see M-3). Argue for **medium → bordering high**, but accept current rating with M-3's gate-binding suggestion as the mitigation.

## Cross-Cutting Concerns

### C-1. The flag inventory drift (panel new LOW #1) is symptomatic of a structural absence

The panel correctly flagged that MODULE-002 Public Interface doesn't enumerate `--resume`, `--force`, `--reconcile-ledger`. But the deeper observation is that there is no single REQ that *defines* the slice-command CLI surface as a whole. The surface is described piecemeal across REQ-003 / REQ-005 / REQ-006 / REQ-007 / EDGE-012 / EDGE-013 / EDGE-014. A reader has to assemble the surface mentally. This pattern recurs for `/sdd-flow continue` flags (REQ-014 / REQ-023). **Recommendation:** Add a single subsection in the spec — under "Functional Requirements" or as a new "Command Surface" section — that enumerates every command + every flag in one table. This subsumes A-1, the deferred panel LOW #11, and the panel new LOW #1.

### C-2. The Suggested Approach (lines 431–444) is a hint, not a contract

The 12-step ordering is described as "Order of work" but not gated. A subagent free-running implementation may skip step 5 ("planning-start.md Step 6 extension") in favor of doing it at the end. The locked-region discipline (lines 64–204 + 375–379) is binding, but step ordering is not. **Recommendation:** Either explicitly mark the Suggested Approach as advisory ("recommended; not gated") OR promote step ordering to a constraint and tie each step's definition-of-done to a specific oracle (M-3's gate-binding suggestion).

### C-3. Specs that span "code change + docs + manifests + skill source" are coordination-heavy

This feature touches: 18 sdd commands + 1 sdd-flow skill + 1 hook + 1 README in sdd + 1 README in agent-engineering + 1 repo-root README + 4 manifest version strings + (potentially) the glossary + this run's own SDD artifacts. The closing-oracle grep covers paths but does not cover *every* coordination invariant (version strings drift; README's two-workflow restructure has no oracle). **Recommendation:** Add a top-level "Verification primitives" subsection summarizing every grep / sha / diff oracle the implementation phase MUST run, keyed by which REQ they verify. Currently these are scattered across REQ-016, REQ-018, REQ-019, Manual Verification, and Critical Implementation Considerations.

### C-4. The `## Delivery Slices` block is locked but the frontmatter-fields prose at line 271 is allowed to be extended

This is a known boundary, called out in CLARIFICATION (line 50). But the spec doesn't have any acceptance test that asserts the frontmatter-fields prose AT LINE 271 stays consistent with the locked-region content (in particular, the Step A description of `delivery_mode:`). An implementer extending the prose to describe practicality-gate behavior could subtly contradict the locked region. **Recommendation:** Add to Manual Verification: *"`diff` between the locked-region's `delivery_mode:` description (lines 184–204) and the frontmatter-fields prose (line 271+) for content consistency on the `delivery_mode:` field's purpose, default, and enum values."*

## Recommended Actions Before Proceeding

Prioritized; HIGH/MEDIUM block proceed, LOW recommended-not-blocking.

1. **[MEDIUM]** Resolve A-1 (flag-convention drift): add a slice-command flag-conventions REQ; pin down `/sdd-flow continue` flag combination semantics inline in REQ-014; explain the `--reconcile-` prefix convention in REQ-005. **One paragraph in three places.**
2. **[MEDIUM]** Resolve A-2 (cross-plugin version coupling): add FAIL-009 for SDD 2.0.0 + agent-engineering 0.3.x mismatch; require the SDD README changelog to flag the coupling. **One FAIL entry + one README clause in REQ-019.**
3. **[LOW]** Resolve M-1 (glossary update timing): one sentence in REQ-020 + one Manual Verification bullet.
4. **[LOW]** Resolve M-2 (Step A locked-region oracle): one concrete oracle in REQ-001 / Manual Verification.
5. **[LOW]** Resolve M-3 (closing-oracle gate-binding): one-liner appended to each path-touching step in Suggested Approach.
6. **[LOW]** Resolve M-4 (`--reconcile-ledger` semantics): one paragraph extension to REQ-005.
7. **[LOW]** Resolve M-5 (qualitative-judgment prefix audit-test): one Manual Verification bullet.
8. **[LOW]** Resolve R-2 (active-slice fallback asymmetry): one sentence in MODULE-002 Hides.
9. **[LOW]** Resolve R-3 (`--from-slice` validation): one sentence in REQ-014.
10. **[LOW]** (Optional) C-1, C-3 are structural improvements that subsume #1/#5/#6 but require a new subsection. Consider a follow-up tidy-up.

The two MEDIUM findings are the only blockers. All eight LOW items are local and can be addressed in a single fix subagent pass.

## Verdict

**REVISE BEFORE PROCEEDING**

Rationale: HIGH=0 keeps this far from "stop and reconsider" territory. The two MEDIUM findings are not architectural failures — they are precisely the kind of thing a complementary generalist review is supposed to catch: a fix-time invention pattern (flags) that the specialist panel scoped narrowly to one named anti-pattern; and a cross-plugin coordination story that no specialist owned. Both are local edits. The spec is otherwise well-prepared for implementation: the iteration-1 + iteration-2 panel work has materially closed the degenerate-state and audit-trail gaps; the locked-region discipline is consistent; the recursion-trap warning is being honored across phases.

After the two MEDIUMs are addressed (single fix subagent pass, no panel re-run needed), recommend **PROCEED** to Step 4 implementation.

## Findings Addressed (Step 3e — combined fix)

**Date:** 2026-05-05 (Step 3e combined panel+critical fix subagent)
**Spec edited:** `SDD/requirements/SPEC-001-vertical-slicing-step-c.md`
**Resolution status:** both MEDIUM findings (M-A1, M-A2) resolved; all LOWs (L-CR-1 through L-CR-7, plus the R-2 / R-3 carry-overs) resolved.

### MEDIUMs

- **M-A1 (A-1) — Flag-convention drift between fix-time inventions and existing SDD plugin convention.**
  - Resolution: new **REQ-025** "Slice-command flag conventions" added (line 121+). Inventories all six flags introduced by Step C across the slice commands and `/sdd-flow continue` extensions: `--resume`, `--force`, `--reconcile-ledger`, `--replan`, `--from-slice`, `--override-replan`. For each: name, command(s) it applies to, semantics, default behavior, supervised-vs-autonomous behavior. Explicitly states that the proposal authoritatively defines `--replan`, `--from-slice`, `--override-replan` (proposal §6); the iteration-1 fix introduced `--resume`, `--force`, `--reconcile-ledger` to address EDGE-012/EDGE-013/EDGE-014 re-invocation cases (these latter three are spec-introduced and back-cited in the future research note about the implementation). `--force` adopts the destructive-action override convention going forward; rationale named explicitly ("destructive-with-confirmation flag, mirrors common Unix tooling convention"). Combination semantics for `/sdd-flow continue` flags pinned (resolves panel-deferred-LOW-11). MODULE-002 Public Interface (line 371) updated to enumerate flags per command (resolves panel iter-2 LOW-1). EDGE-013 (line 259) extended with autonomous-vs-supervised semantics (resolves panel iter-2 LOW-2). MODULE-002 spec refs + MODULE-006 spec refs updated to cite REQ-025.
  - Spec refs: REQ-025, MODULE-002 Public Interface + Hides, EDGE-013 update.
  - Status: **resolved**.

- **M-A2 (A-2) — Cross-plugin version coupling silent on SDD 2.0.0 + agent-engineering 0.3.x mismatch.**
  - Resolution: three coordinated additions:
    - **FAIL-009** (line 324+): documents the trigger condition (mismatch in either direction), expected behavior (split-tree symptoms, silent fall-through of `delivery_mode: per-slice` to whole-feature in older skill), detection (hard at runtime; primary mitigation is documentation-time per REQ-026; stretch-goal version-check stub described but not required), user communication (README cross-references + marketplace.json release notes), recovery (upgrade lagging plugin; orphan artifacts are `git mv`-able; no data loss).
    - **REQ-026** (line 165+): mandates README cross-references with suggested wording for both directions (`agent-engineering/README.md` calls out SDD 2.0.0+ minimum; `sdd/README.md` calls out agent-engineering 0.4.0+ minimum); repo-root README mention. REQ-019 + REQ-021 are updated to cite REQ-026 (their definitions of done now include the cross-plugin clause). REQ-019 verification commands extended to verify the clause is present.
    - **RISK-007** (line 490+): "Plugin version drift between SDD 2.x and agent-engineering 0.3.x" with mitigation = README cross-references + marketplace.json release notes + FAIL-009 documentation + stretch-goal version-check stub in skill loader.
    - MODULE-008 spec refs updated to cite REQ-026 / FAIL-009 / RISK-007; MODULE-008 Justification updated to acknowledge that the cross-plugin clauses belong at the docs+manifest layer.
  - Spec refs: FAIL-009, REQ-026, RISK-007, MODULE-008 (refs + justification), REQ-019 + REQ-021 updates.
  - Status: **resolved**.

### LOWs

- **L-CR-1 — Glossary update timing.**
  - Resolution: REQ-020 (line 116) extended with a "Timing of glossary updates" sentence that mirrors `/sdd:planning-complete` Step 5 wording: glossary additions MUST be made in the same step (and same git commit) as the source-code edit that introduces the term, never deferred to a "documentation pass" step at the end. Manual Verification gains a corresponding bullet (`grep -nF` any apparently-new term against `UBIQUITOUS_LANGUAGE.md`).
  - Status: **resolved**.

- **L-CR-2 — Step A locked-region invariant lacks acceptance oracle.**
  - Resolution: Manual Verification (line 450) extended with a concrete grep-based oracle citing pre-implementation commit hash `ffeec97` literally and the line ranges 64–204 + 375–379. Two oracle forms are documented: (a) `git diff ffeec97 -- sdd/commands/planning-start.md | awk ... | grep -E '^[+-]'` returns empty, AND (b) sha256sum of `git show ffeec97:.../planning-start.md | sed -n '64,204p;375,379p'` matches HEAD's. Either oracle is sufficient; both are documented for redundancy.
  - Status: **resolved**.

- **L-CR-3 — Closing-oracle grep not gated to specific implementation steps.**
  - Resolution: Suggested Approach (line 496+) extended — each path-touching step (steps 2, 3, 4, 5, 6, 8, 11) now has an explicit "Definition-of-done:" line naming the grep oracle that MUST pass before declaring the step complete. Manual Verification also gains an explicit "Closing-oracle grep is the binding 'definition of done'" bullet citing research §"Closing-oracle verification" as the authoritative source. The implementation phase now has the gates wired to the steps, not deferred to an end-pass.
  - Status: **resolved**.

- **L-CR-4 — `--reconcile-ledger` mode behavior named but unspecified algorithmically.**
  - Resolution: new **REQ-025a** (line 152+) specifies the 8-step reconcile algorithm verbatim per the orchestrator's task: read all retros for the active feature; read the current ledger; check whether each retro's learnings appear in the ledger; append missing entries (consolidating with existing entries on the same topic); PRESERVE manual-edit-only entries that have no retro source (flag as `> orphan entry — no source retro on disk`); mark ledger header with `<!-- reconciled at YYYY-MM-DD -->` HTML comment timestamp; output a diff for user confirmation in supervised mode (autonomous mode writes and logs to progress.md); scope = all retros for the active feature. The audit-trail invariant (retros authoritative, ledger derived) is preserved; manual edits are NOT destroyed.
  - Status: **resolved**.

- **L-CR-5 — Qualitative-judgment prefix has no audit grep.**
  - Resolution: Manual Verification (line 450+) extended with a "Qualitative-judgment audit-test" bullet that grep-asserts the literal `Qualitative judgment: ` prefix in `progress.md` and `## Delivery Slices` annotations whenever the qualitative-judgment escape fires. Synthetic-tree manual test only (no automated runtime check, per REQ-011's existing test approach).
  - Status: **resolved**.

- **L-CR-6 — Active-slice fallback asymmetry between `/slice-start` and other slice commands.**
  - Resolution: MODULE-002 Hides (line 372) extended with explicit "Active-slice fallback asymmetry" paragraph — all four slice commands resolve via the SAME priority (explicit arg > IMPLEMENTATION-PLAN row matching expected status > error), but the *expected status* differs by command intent: `/slice-start` defaults to first `Not Started`; `/slice-review`/`/slice-retro`/`/slice-commit` default to `In Progress` or `Acceptance Check Passing`. Implementations SHOULD share a single `resolve-active-slice(expected_status_set)` helper.
  - Status: **resolved**.

- **L-CR-7 — `--from-slice SLICE-XXX` validation unstated.**
  - Resolution: REQ-025 flag table specifies validation: `--from-slice` value MUST match `^SLICE-\d{3}$` AND MUST reference an existing SLICE-XXX in the IMPLEMENTATION-PLAN's `## Slice Progress` table; invalid value (regex mismatch or unknown slice) refuses with REQ-007 message-discipline shape (name offending value, name existing slice IDs or "none", name resolution path). REQ-014 also cites REQ-025 explicitly for this validation.
  - Status: **resolved**.

### R-2 / R-3 carry-overs (research disconnects)

- **R-2 — `/slice-start` vs `/slice-review` fallback semantics asymmetry.**
  - Resolution: same as L-CR-6 — addressed in MODULE-002 Hides update.
  - Status: **resolved**.

- **R-3 — `--from-slice` validation unstated.**
  - Resolution: same as L-CR-7 — addressed in REQ-025 flag table.
  - Status: **resolved**.

### Cross-cutting concerns (C-1, C-3, C-4)

- **C-1 (no single REQ defining slice-command CLI surface as a whole)**: addressed via REQ-025's flag inventory table, which functions as the single canonical reference for the slice-command CLI surface (subsumes the panel-deferred LOW-11 + the panel iter-2 new LOW-1).
- **C-3 (verification primitives scattered)**: partially addressed via the L-CR-3 gate-binding (Manual Verification + Suggested Approach now have explicit oracle references). A consolidated "Verification primitives" subsection (full structural reorganization) was considered but rejected as out-of-scope for Step 3e — the gate-binding is sufficient for the implementation phase.
- **C-4 (frontmatter-fields prose at line 271 vs locked region content)**: addressed via Manual Verification bullet that diffs the locked-region's `delivery_mode:` description against the frontmatter-fields prose for content consistency.

### Verdict after Step 3e fix

The two MEDIUMs (M-A1, M-A2) and all seven LOWs (L-CR-1 through L-CR-7) are resolved; the R-2 / R-3 / C-1 / C-3 / C-4 cross-cuts are addressed. HIGH=0, MEDIUM=0, LOW=0 (post-fix). The critical review's PROCEED-after-fix recommendation is satisfied; Step 3f (planning commit) and Step 4 (implementation) can proceed.
