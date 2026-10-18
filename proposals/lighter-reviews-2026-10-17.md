# Lighter Reviews in sdd-flow

**Status:** Implemented as agent-engineering 3.14.0 (`1c49bb0`, 2026-10-18), in the order 4, 1, 2, 3: `ca185f3` (fix 4), `8b0da75` (fix 1), `48340e0` (fix 2), `a403ed0` (fix 3). The shipped files supersede the wording below. Two differences from this plan: fix 2 takes two snapshots per fix round, one before the fix and one immediately before the re-review (`scripts/site-diff.py --snapshot`), because a Codex reviewer cannot write `.git`; fix 3's depth is recorded as a `## Site Depth` line (`references/enforcement-sites.md` §7). The optional fifth fix was not built. Not yet tried on a real cycle.
**Date:** 2026-10-17 (approved 2026-10-18)
**Affects:** `agent-engineering/` plugin — `sdd-flow` (references, bodies, phase files, `SKILL.md`, `scripts/site-diff.py`) and the tier standard (`simplicity-challenge/references/tiers.md`).
**Author of intent:** Pablo Oliva. Drafted with Claude.

---

Evidence: the two acceptance cycles (`hint-tutor-acceptance` cycle 1, stopped; `hint-tutor-mini` cycle A, done). Cycle A changed no app code apart from adding evals, yet its first code review rejected it with 24 HIGH, and its final check (4e.5) took 5 rounds. Rounds 2–4 raised only HIGHs about `evals/run.py`, the plugin's own template.

## Two principles these fixes change (the user's call)

- **Key Principle 11 / tier Tenet 1, "Tiers limit scope, never rigour":** fix 3 reverses this on purpose. Tier 1 gets lighter proofs.
- **Key Principles 2 and 7, "ALL findings (HIGH/MEDIUM/LOW) resolved before proceeding":** today a MEDIUM rejects a review, and at the final check even a LOW is sent to a fix. So moving a finding from HIGH to MEDIUM saves nothing. Fix 1 therefore needs a new outcome: **recorded, not fixed.**

## The four fixes

1. **A proof gap blocks only where the risk is real.** (A correction to an earlier draft: every site the reviews prove already belongs to a control in the spec's register, so "unless a registered control" would have exempted nothing.)
   - A security control's site (`SEC-` ID) that no test catches when deleted: HIGH and fixed, as today. A gap (a path with no site at all, i.e. broken code) stays HIGH for every control.
   - Any other control's site that no test catches: **recorded, not fixed.** The reviewer appends the existing "not proven, kept" row (disposition (iii), owner `review`, what would prove it). It is LOW, never starts a fix round, and is listed in the implementation summary for the user to see.
   - Files: `references/enforcement-sites.md` §3, §6; `references/test-integrity.md`; `bodies/{code-review,slice-review}.md`; `SKILL.md` principles 2, 7, 9.
2. **Later rounds check the fixes and the code they touched.**
   - Before each fix, the orchestrator takes a snapshot of the working tree as an unreferenced commit (a temporary index, so it changes neither the real index, HEAD, nor the stash).
   - The recount after the fix passes that snapshot to `scripts/site-diff.py --base`, which already treats code that did not change as carried (LOW, not a finding).
   - The re-review checks each earlier finding, re-runs the proofs only in changed code, and runs the trace and eval checks as today (they read fresh runs).
   - The first final-check round stays complete.
   - Files: `phases/implementation-{whole-feature,per-slice}.md`, `phases/protocols.md` (resume), `bodies/{code-review,slice-review}.md`, `scripts/site-diff.py` + tests.
3. **The tier sets how deep reviews go.** One table in the tier standard (`simplicity-challenge/references/tiers.md`), read by the reviews:
   - **Tier 1:** per-site proofs and the blind count for security controls only. Other controls need a real test that drives them; the Test Integrity Lens still runs. One blind count, at the final check.
   - **Tier 2:** proofs for every control; one blind count, at the final check.
   - **Tier 3, or no tier:** as today.
   - Written to survive `CLAUDEPLUG-13` (more than three tiers, or a tier in parts): the table names Tier 1, Tier 2, and "any later tier", and a part of a tier is reviewed at its tier's depth. `CLAUDEPLUG-13` itself is a separate release after this one.
   - Files: `tiers.md`, `references/enforcement-sites.md`, `bodies/{site-count,code-review,slice-review,implementation,slice-start}.md`, both implementation phase files, `SKILL.md` principle 11.
4. **A file that equals its template is out of scope for these proofs.**
   - `evals/run.py`, while equal to its template apart from the three placeholders: no inventory rows, no blind count, no deletion proofs, no tests owed for its logic. The equality check stays (a drift is HIGH, and brings the file back into scope). `evals/task.py` and `evals/checks.py` stay fully in scope.
   - The tracing files from `/observability-init`: their template lines likewise; placeholders filled with app-specific code stay in scope.
   - Files: `references/enforcement-sites.md` §1, `references/evals.md` §7, `references/test-integrity.md`, `bodies/site-count.md`.

## Optional fifth fix (not yet agreed)

- **The read limit for reviews run on Codex.** The 15-read Safety-Net protects a Claude subagent's context; Codex manages its own. Cycle A's first final-check round was four Codex runs because of it. Check the Codex logs first, then propose.

## Order and checks

- Approved by the user 2026-10-18, with both principle changes. Batches in the order 4, 1, 2, 3, then the release (3.14.0: versions, READMEs, both diagrams, repo `CLAUDE.md`, one whole-change Codex review).
- Each batch: Codex review, a checkpoint with the user, commit on the user's word. Landing and pushing on a separate word.
- Proof after release: the next-tier cycle on `hint-tutor-mini` (Tier 2, adopting a harvested case). It also closes `CLAUDEPLUG-11`, and shows whether the cycle got lighter.
