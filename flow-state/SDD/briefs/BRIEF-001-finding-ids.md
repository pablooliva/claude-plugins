# BRIEF-001-finding-ids

Date: 2026-11-17. Status: approved 2026-11-17.

## What you will be able to do afterwards
- Point at any review finding by a stable ID (`F3`) across a slice's reviews, and across the code review and every final-check round.
- Read every finding's severity, place and state from one fixed line: `FINDING F3 | MEDIUM | src/cart.py:42 | open` — the line a later ledger script will parse.
- See the final state of every code-review (4b) finding, written down by the first final check.
- Get the same finding lines from sdd-lite's Codex review and its check of fixes.

## Decisions
- The finding line, the numbering rule (one chain, next free number, never reused) and `fixed` / `open` in place of `closed` / `still open`: the owner's words.
- An in-full re-review (after an `## Awaiting … Resolution` stop, or with an unusable snapshot) is now also given `PREVIOUS REVIEW`, the latest review of the chain, and writes `## Earlier Findings` from it — settled by me: without it that review cannot know the next free number. It still reviews in full; with `PREVIOUS REVIEW` alone a body already reviews in full.
- Final check round 1 gets the 4b review as `PREVIOUS REVIEW` (no snapshots — 4c takes none), reviewed in full as today. A code-review finding it finds still `open` is a finding of the final check again, at its severity — so an unfixed HIGH/MEDIUM from 4b now blocks approval (follows from the request; today nothing re-checks them).
- sdd-lite: `codex exec -s read-only`, prompt written into the skill, output outside the repo (`$TMPDIR`); HIGH/MEDIUM fixed, LOW listed; the check of fixes gets the first output and halts on an open HIGH (today P0/P1).
- `<#>` in the references' section shapes (tracing lens, test integrity, evals, state model) is read as the F-number — one sentence in each body; the references are not edited — settled by me.

## How it will work
- `skills/sdd-flow/bodies/slice-review.md` (Step 4.5 :88, Step 5.6 :152, template :219–265), `code-review.md` (Severities :244, template :496–538), `final-check.md` (later round :25–31, document :36): the line, the numbering, `## Earlier Findings` with `F<n> | fixed|open` then evidence.
- `phases/end-of-feature.md` 4e.5 step 2 (:42): round 1 passed the 4b review; a round after the stop passed the latest final check. `phases/implementation-per-slice.md` (:68, :96) and `phases/rare/resume.md` (:64, :87): an in-full slice re-review passed `PREVIOUS REVIEW`.
- `skills/sdd-lite/SKILL.md` step 5 and `docs/sdd-lite-diagram.md` (:18, :42–45, :62); `docs/sdd-flow-diagram.md` only if a step's box changes.
- README "What's new in 5.4.0"; 5.3.0 → 5.4.0 in `agent-engineering/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`.

## Builds on
- The three bodies' existing `## Earlier Findings`, `## LOW Findings` and numbered-findings rules; the 4e.5 input list; sdd-lite step 5.
- New files: none (this brief only).

## Not now
- A defect ledger, `ledger.py`, reading findings into a file. Fixer bodies (4c, slice fix) and the spec critical review (3d/3e.5) keep their wording.

## Beyond the request
- none

## Done when
- All three bodies and sdd-lite's review use the line; a re-review repeats IDs with states; the first final check lists the code review's IDs; versions bumped in both files.
- `python3 -m unittest discover -s agent-engineering/skills/sdd-flow/scripts/tests` passes (nothing there should change).
- One Codex review with no open HIGH or MEDIUM.

## Risk
- ordinary — instructions to review agents; no data, secrets or external effects.

## Decision records to write
- none (a format inside the plugin's own review bodies, not a cross-cutting choice for applications)
