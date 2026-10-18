# A Tier Delivered in Parts

**Status:** Approved 2026-10-18, not implemented. Planned as agent-engineering 3.15.0. The next-tier cycle on the trial application `hint-tutor-mini` has run (3.14.0 tried alone first), so the build is unblocked; one open point from that run is at the end.
**Date:** 2026-10-18
**Task:** `CLAUDEPLUG-13` — sdd-flow: allow more than three tiers, or a tier delivered in parts.
**Affects:** `agent-engineering/` plugin — the tier standard (`simplicity-challenge/references/tiers.md`), `sdd-flow` (phase files, bodies, `SKILL.md`, `scripts/tier-mirror.py`), `commands/research-clarify.md`. The `sdd/` plugin is frozen at 2.2.0 and is not touched.
**Author of intent:** Pablo Oliva. Drafted with Claude.
**Builds on:** `proposals/tiered-delivery-2026-10-02.md`, which introduced the three tiers and the tier plan.

---

## What the real use shows

The task (2026-10-05) was written from one wish: Tier 3 of the education app (eduKate) in seven parts. Since then eduKate has actually built a tier in parts five times, each by working around the plugin:

| Cycle | What it built | Workaround it needed |
|---|---|---|
| 002 `-t1b` | the rest of Tier 1 (items 2 and 3) | invented the suffix ("the plugin names only -t2/-t3"); told not to run `tier-mirror.py --shipped 1` after cycle 001, ran `--active 1` instead |
| 003 | Tier 2 split into parts A–D | Step 0 decomposition (`DECOMPOSITION-003-education-app-t2.md`); the parts are recorded only in that file and in the prose of Tier 2's `Built in` cell |
| 004 `-t2a`, 005 `-t2b` | parts A and B | `--next-tier` scoped to one part by hand, each time recorded in prose in the Step 0 record |
| 005 → 006 `-t2b1` | part B split again into B1–B3 | a second decomposition (`DECOMPOSITION-005-…-t2b.md`); suffix invented again |

Other signs:
- Tier 2's `Built in` cell is now a paragraph of ~120 words; the status column reads `paused 2026-10-17` (not a status the standard knows).
- The BB task for Tier 2 (`EDUKATE-3`) said `backlog` while part B1 was being built: the mirror cannot see parts.
- Deferred rows already say `To tier` = `3A`, `3C`, `3F or earlier`.

So the need is a tier built over several cycles — at every tier, not only the last — and not more than three kinds of tier.

## The decision: three tiers, each deliverable in parts

- **N ordered tiers — rejected.** Tier 1, 2, and 3 mean something that other rules depend on: the floor and cut tests defer "to Tier 2 or Tier 3", and the 3.14.0 depth table proves Tier 1 for security controls only and Tier 2 for every control with one blind count. With N tiers, Tier 4 has no meaning, and a 7-tier feature gets Tier 3's full depth on parts that are no riskier than Tier 2. The parts eduKate built (A–D of Tier 2) were all "Standard" work.
- **Several features — kept as it is, with one rule.** A part that would itself need a POC first (its own Tier 1) is a separate feature with its own tier plan; Step 0 decomposition already handles that. A part has no tiers of its own. eduKate's planned 3G "several students, with accounts and consent" may be such a feature; its own cycle decides.
- **Parts — what this proposal builds.** The three meanings stay. A tier may be built in parts: `2A`, `2B`, … Each part is one cycle with its own number, brief, spec, reviews, commit, row, and task. A part is proven at its tier's depth (already true since 3.14.0).

## What changes

The tier plan becomes the one record of parts (the decomposition file keeps only its rationale and dependency map):

- **Labels.** A part is the tier digit + a capital letter (`2A`). A part split again is replaced by its pieces, labelled with a digit (`2B` → `2B1`, `2B2`, `2B3`) — this is what eduKate did. No deeper than that.
- **Rows.** The status table keeps one row per tier and adds a row per part directly under its tier: `| 2B — browser tests | in progress | SPEC-006… | EDUKATE-9 |`. A tier with parts is `shipped` when every part is shipped or dropped; until then its row reads `in parts` and its `Built in` is `—`.
- **Sections.** A part gets its own `## Tier 2B` section (five lines, like a tier's) holding the self-contained task description its cycle starts from.
- **When parts are written.** When the tier's turn comes, not before: the parts of a sketched tier stay bullets inside its sketch (as eduKate's Tier 3's seven are today). Part rows are written either by the design brief (a brief may plan its tier in parts) or by Step 0's scope assessment on a next-tier cycle — the scope subagent writes the part rows and sections into the tier plan instead of a separate checklist. The decomposition stop stays unconditional: the user reads and edits the parts in the tier plan, then runs `--next-tier`.
- **`--next-tier`.** Picks the lowest tier not shipped or dropped; when that tier has parts, the lowest part not shipped or dropped. A part is used before the next part is planned, as a tier is. Suffix: `-t` + the label in lower case (`-t2`, `-t2a`, `-t2b1`) — the names eduKate already uses, so its files stay valid. Task description = that part's section plus the Deferred rows aimed at it.
- **`tier:` in the spec** takes the row's label (`2` or `2B`). Readers that need the tier (the 3.14.0 depth table, `references/enforcement-sites.md` §7) take its digit; §7 already says "a part of a tier takes its tier's row", so the table itself does not change. `--tier N` (the first cycle's recommendation) stays 1–3.
- **BB tasks.** BB allows one level of sub-tasks, so a part's task is a sibling of its tier's task under the feature task, titled `Tier 2B — … · <feature>`. The tier's task status rolls up from its parts (in progress while any part is; done when all are done or canceled). `--active` / `--in-review` / `--shipped` / `feedback --tier` accept a label (`2B1`).
- **Deferred `To tier`** may name a tier or a part (`3` or `3A`) — what eduKate already writes; `simplicity-challenge` keeps placing items into tiers only (parts are the tier's own cycle's decision).
- **Old tier plans keep working.** A plan with three rows and no part rows behaves exactly as before 3.15.0. eduKate's plan can be converted to part rows by hand afterwards (offered, not done by the release).

## Files (from the survey; ~25 files)

- **Batch 1 — the standard:** `simplicity-challenge/references/tiers.md` (parts: when a part vs a separate feature, labels, rows, sections, status roll-up, tier-plan template with one example part row; "each tier and each part is used before the next is planned"); `simplicity-challenge/SKILL.md` (`To tier` wording only).
- **Batch 2 — the mirror:** `sdd-flow/scripts/tier-mirror.py` (row regex, the six `(1, 2, 3)` loops, part tasks as siblings, roll-up, label arguments, `section()` for `## Tier 2B`) + `scripts/tests/test_tier_mirror.py` (part rows, split part, roll-up, old three-row plan unchanged, a malformed label refused).
- **Batch 3 — the flow:** `phases/setup.md` (next-tier pick, suffix, scope assessment on a next-tier cycle writes part rows), `SKILL.md` (`tier:` values, `--next-tier` row, Tier Task Mirror), `phases/protocols.md` (resume with a part), `phases/research.md` + `bodies/research.md` (`NEXT-TIER CYCLE: Tier 2B`), `commands/research-clarify.md` (suffix line), `bodies/design-brief.md` (a brief may plan its tier in parts; rule 10 writes the part rows), `phases/planning.md` (the gate's Tiers line), `bodies/planning.md` + `bodies/planning-complete.md` (`tier:` value), `bodies/critical-review.md`, `bodies/panel-specialist.md`, `bodies/slice-review.md`, `bodies/code-review.md` (the "(1, 2, or 3)" wording; the tier's digit for depth), `bodies/implementation-complete.md` (a part's row shipped; its tier's row shipped when the last part is), `phases/implementation-whole-feature.md` + `implementation-per-slice.md` (announcement, `--shipped <label>`), `references/enforcement-sites.md` §7 (one sentence: read the digit of `tier:`), `eval-harvest/SKILL.md` (checked; "next tier" may be a part — probably wording only).
- **Batch 4 — release 3.15.0:** both version files, root and plugin READMEs, `docs/sdd-flow-diagram.md`, repo `CLAUDE.md`.

Each batch: a Codex review until "No findings", the test suite run, and a checkpoint for the user's word to commit.

## Left out

- `paused` as a status — eduKate's current word; a status the mirror does not know already maps to `backlog`. Add it only if the next use needs it.
- Converting eduKate's tier plan — the owner's call, after the release.
- More than one level of split (`2B1a`).

## Decided (2026-10-18)

1. Parts of a tier, as above — not N ordered tiers.
2. On a next-tier cycle the scope assessment writes the part rows and sections straight into the tier plan; the decomposition file keeps only its rationale and dependency map.

## Found after approval (2026-10-18): the scope check splits before the brief cuts

The Tier 2 cycle of the trial application hint-tutor-mini (agent-engineering 3.14.0, that app's commit `1186e9f`) showed a second fault in the same place:

- `/sdd-flow --next-tier` ran Step 0's scope assessment on the whole Tier 2 sketch plus every Deferred row aimed at Tier 2 — the most Tier 2 could ever hold. It split that into four features (`DECOMPOSITION-002-hint-answer-evals-t2.md`) and stopped.
- The owner overrode the split. The design brief then cut Tier 2 to one prompt sentence and one eval case, and moved the rest to Tier 3. The split had sized work the brief was about to remove.
- The split's items were plain `/sdd-flow` tasks, with no way back into the next-tier cycle (what this proposal fixes), and the scope subagent wrote "orchestrator picks F1" in `progress.md` although the stop is unconditional.

So decision 2 needs one change before the build: on a next-tier cycle the scope assessment should not split ahead of the brief. Recommended: on a next-tier cycle, Step 0 skips the split; the design brief, which cuts the tier first, plans the tier in parts when what it keeps is still too big, and writes the part rows (already allowed above). The scope subagent's misstated stop is fixed in the same batch. **Open — for the owner to confirm before batch 3.**
