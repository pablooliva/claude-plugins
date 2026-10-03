# sdd-flow Review — Findings

**Status:** Fixed in 3.5.1 (commits `58b559b`, `d1b85e8`, `2e7c0fb`, and the 3.5.1 wrap-up). Fix plan: `proposals/sdd-flow-review-fix-plan-2026-10-03.md`. Struck: the second half of M12 (see its row). Not fixed, by decision: the second half of M7 — the single-pass fixes at 2d, 3e, 4c, and 4e still get no second review. L4 (outside `sdd-flow`) was fixed in the wrap-up. Line numbers below are as of the reviewed commit and no longer match.
**Date:** 2026-10-03
**Affects:** `agent-engineering/` plugin, `sdd-flow` skill (reviewed at 3.5.0, commit `6a8b912`).
**Author of intent:** Pablo Oliva. Reviewed with Claude; independent second read by Codex.

---

## Scope and method

The question: does the `sdd-flow` skill make sense as a whole, is it cohesive, and are there gaps or errors in how it handles the development cycle?

- **Read in full:** `SKILL.md` and every file under `phases/`.
- **Read in part (targeted):** every file under `bodies/`, the agent files under `agent-engineering/agents/`, the argument parsers of both scripts, and the stops in `docs/sdd-flow-diagram.md`.
- **Independent read:** Codex reviewed the same files without being given any conclusions other than the five issues already known (so it would look for others).
- **Not done:** no flow was run end to end. Every finding is a contradiction or gap between two pieces of text, not an observed failure.

Paths below are relative to `agent-engineering/skills/sdd-flow/` unless they start with `agents/`, `commands/`, or `docs/`.

**Source column:** `both` = found independently by Claude and Codex; `Claude` / `Codex` = found by one. **Verified** = the text on both sides of the contradiction was re-read by Claude. Four Codex items (M10, M11, M12, L4) were first recorded untraced; all four were traced later the same day — three hold, and one half of M12 was struck (noted in its row).

**Verdict.** The main path (research → design gate → planning → implementation) hangs together. The gaps cluster in three places: resuming after a stop, the per-slice path, and instruction files ("bodies") that were forked from standalone commands and still behave like them.

---

## Root causes

Most findings trace to one of three causes. The fix plan is organised around them.

| # | Cause | What it looks like |
|---|---|---|
| R1 | **Bodies still act standalone.** They were forked from commands a person runs by hand. | A body lists files to find its inputs and halts when it finds several; asks the user a question by writing a stop note; commits code; resets the state log. All of these contradict "the prompt gives you resolved paths — use them verbatim" and "the orchestrator is the only one that stops the flow". |
| R2 | **Phase-done markers are written too early, or never.** | A completion subagent writes "phase complete" before the phase's remaining steps (reviews, commit) have run. Planning already works around this with the orchestrator-written `## Planning - Accepted`; research and implementation have no equivalent. |
| R3 | **The per-slice path has stops and state changes with no owner.** | A state transition, a halt, or a commit that the bodies assume the orchestrator performs, and the phase chapter never mentions. |

---

## Previously known issues (all confirmed)

| ID | Finding | Evidence | Notes |
|---|---|---|---|
| K1 | **A pending ADR confirmation has no resume rule — and no confirm step at all.** In supervised mode the ADR subagent writes `## Awaiting ADR Confirmation` and returns without writing the decision record. No step asks the user, writes the record after a yes, or clears the note. | `bodies/adr-capture.md:5`, `:174-188`; `phases/research.md:29-34`; no rule in `phases/protocols.md` | Worse than first described: research-stage ADRs are never written in supervised mode. The note also pastes the whole rendered ADR into `progress.md`, and log rotation carries it forward forever (`phases/protocols.md:28` matches any `## Awaiting ` prefix). |
| K2 | **An interrupted blind site count is handed fewer inputs than a fresh one.** The handoff drops the filing-conventions path, the reviewer's `ALSO INVENTORY` IDs, and the slice's `Modules touched`. The compaction template does not record them either. | `phases/protocols.md:15` vs `phases/implementation-per-slice.md:50`; `bodies/site-count.md:16-18`; `bodies/site-count-compact.md:14-17` | The successor can file sites under different keys (false mismatches) and skip controls a reviewer asked to have counted. |
| K3 | **The iteration number is not passed to two review spawns.** Both reviewers write a resume marker `## Review … iter <N>` from "the `ITER` in your prompt". | `phases/implementation-per-slice.md:78` (only mentioned in passing at `:83`); `phases/implementation-whole-feature.md:75`; `bodies/slice-review.md:143`; `bodies/code-review.md:226` | A wrong or missing number misroutes every site-count resume rule. |
| K4 | **A spec that forces agent-security review on conflicts with the reviewer's own scope check.** The phase says `agent_security: true` makes the specialist skip its scope gate; the agent file and the body run it unconditionally; the spawn never passes the value. | `phases/planning.md:113`, `:123`; `bodies/panel-specialist.md:210`; `agents/sdd-spec-agent-security-specialist.md` ("Scope gate — run this first") | A forced review can return "gate closed" with no findings. |
| K5 | **Site-verification-only mode conflicts with the code review's artifact pre-check.** The pre-check halts if research, spec, or plan are missing; the mode's skip list does not exempt it. The spawn also omits the spec, which the mode needs to judge uncounted rules. | `bodies/code-review.md:11-40`, `:208-224`; `phases/implementation-whole-feature.md:75` | The halt it writes (`## Awaiting Artifacts`) has no resume rule — see M1. |

---

## New findings — the flow breaks or does the wrong thing

| ID | Finding | Evidence | Source | Cause |
|---|---|---|---|---|
| H1 | **Resume reports "done" before the commit.** The completion subagent writes `Implementation Phase - COMPLETE` at step 4f; resume treats that line as finished. A session that ends at the supervised "ready to commit?" pause resumes as done: nothing committed, tasks not marked shipped, log not rotated. The pause also defines no behaviour for a "no". | `bodies/implementation-complete.md:497`; `phases/protocols.md:79`; `phases/implementation-whole-feature.md:102-126` | both, verified | R2 |
| H2 | **A second spec in the repo stops the slice path.** Slice start, review, and retrospective each list every spec and halt on more than one, despite being handed the active spec. The implementation and planning bodies do the same for specs and research documents. Every next-tier cycle has at least two specs. | `bodies/slice-start.md:21-29`; `bodies/slice-review.md:19-25`; `bodies/slice-retro.md:19-25`; `bodies/implementation.md:69`; `bodies/planning.md:47`; vs `phases/implementation-per-slice.md:40` | both, verified | R1 |
| H3 | **Large features halt at the second implementation chunk.** Specs with more than 8 items are split into sequential chunks that append to one plan; the implementation body halts when a plan already exists. The re-scaffold after a re-plan hits the same check. | `phases/implementation-whole-feature.md:21`; `bodies/implementation.md:38-55`; `phases/implementation-per-slice.md:31` | both, verified | R1 |
| H4 | **Three panel reviewers do not exist.** The planning body tells the spec author to add `accessibility`, `privacy`, or `cost`; the panel spawns `sdd-spec-<value>-specialist`; no such agent ships for those three. | `bodies/planning.md:298-300`; `phases/planning.md:110`, `:121`; `bodies/panel-specialist.md:197-206`; `agents/` (8 specialists) | both, verified | — |
| H5 | **A context-limit bailout commits unreviewed code.** The implementation compaction body tells the subagent to stage and commit everything before handing off. That bypasses the supervised commit pause and the one-commit-per-slice rule, and moves `HEAD` away from the base commit the blind count and reviews diff against. | `bodies/implementation-compact.md:119-121`; `phases/implementation-whole-feature.md:116`; `phases/implementation-per-slice.md:148` | Codex, verified | R1 |
| H6 | **Falling back from slices skips all spec review.** The "slicing is not practical" halt fires while the spec is being written (3a). Resuming with `--fall-back-to-whole-feature` routes straight to implementation, skipping planning completion, ADR capture, the panel, the critical review, fixes, and the deviation check. The same halt header is also reused for three unrelated conditions (invalid `delivery_mode`, several `Not Started` rows, several specs). | `bodies/planning.md:391-407`; `phases/protocols.md:63-66`; `phases/planning.md:225`; `bodies/slice-start.md:15`, `:29`, `:94` | Codex, verified | R3 |
| H7 | **After a re-plan the new first slice cannot finish.** The retrospective refuses to run when one already exists for that slice ID; re-planning keeps the old ones as audit trail. The same applies to a forced re-start of a finished slice. | `phases/protocols.md:69`; `bodies/slice-retro.md:69-77`; `bodies/slice-start.md:114` | both, verified | R3 |
| H8 | **`--override-replan` skips the triggering slice's commit.** The re-plan halt fires at 4c.5, before the 4c.6 commit; the resume rule says "advance to the next slice". The next slice then starts on top of uncommitted work. | `phases/implementation-per-slice.md:120`, `:148`; `phases/protocols.md:71` | Codex, verified | R3 |
| H9 | **No way out of a slice's fix-loop halt.** After three failed fix rounds the slice stops. No halt block is written, and resume re-applies the same halt because caps count the fix lines already present. The final recount has a restart-with-fresh-cap rule (`## Awaiting Site-Count Resolution`); the slice loop has none. | `phases/implementation-per-slice.md:85-89`; `phases/protocols.md:87`, `:90`; contrast `:77` | Claude, verified | R3 |
| H10 | **Nobody marks a slice `Complete`.** The slice-start body says the orchestrator does it after the commit; the retrospective body says "the orchestrator picks"; the phase chapter never mentions it. The next slice refuses to start while another row is `In Progress` or `Acceptance Check Passing`. | `bodies/slice-start.md:70`, `:99`; `bodies/slice-retro.md:282-283`; `phases/implementation-per-slice.md:147-150` | Claude, verified | R3 |
| H11 | **Research's completion marker is never written, and research wipes the log.** Resume matches the literal `Research Phase - COMPLETE`; the completion body writes a different sentence. If it did write the literal, it would be too early (2a, before 2b–2e). Separately, the research body resets `progress.md` to a heading plus the Step 0 record, against the append-only rule, deleting the recorded clarification opt-out. | `bodies/research-complete.md:91-93`; `phases/protocols.md:27`, `:93`; `bodies/research.md:9`; `SKILL.md:113`; `phases/setup.md:91` | both, verified | R2, R1 |
| H12 | **Slice mode can fail its own completion check.** Completion requires every requirement row in the plan to read `Complete`; in slice mode the plan is scaffold-only and no slice step updates those rows. | `bodies/implementation-complete.md:68-82`; `bodies/implementation.md:232` | Codex, verified | R3 |

---

## New findings — ambiguous enough to go wrong

| ID | Finding | Evidence | Source | Cause |
|---|---|---|---|---|
| M1 | **Nine stop notes have no resume rule and there is no catch-all.** Bodies write `## Awaiting Artifacts`, `Archive Decision`, `Research Document Selection`, `Research Completion`, `ExistingImplementationPlan`, `SpecSelection`, `SPEC Selection`, `Active Slice Selection`, `Slice Selection` (plus K1's). Rotation treats every `## Awaiting ` prefix as pending forever. The research body can also write `## Awaiting Clarification` on its own judgment, overriding a user's explicit opt-out. | `bodies/code-review.md:40`; `bodies/research.md:9`, `:21`; `bodies/planning.md:47`, `:62`; `bodies/implementation.md:53`, `:69`; `bodies/slice-review.md:25`, `:58`; `bodies/slice-retro.md:25`, `:52`; `phases/protocols.md:28` | both, verified | R1 |
| M2 | **Resume rules are not scoped to the current feature.** A finished feature's "complete" line stays in the live log (the rotation summary must carry it verbatim); only the clarification rule says to ignore it. A second feature interrupted mid-research can match the first feature's "done". | `phases/protocols.md:27`, `:53`, `:79`, `:91-95`; `SKILL.md:134` | Claude, verified | R2 |
| M3 | **The re-plan halt offers an option that is refused.** The pause message says "edit the spec, then plain `continue`"; plain `continue` is refused while that halt is pending. | `phases/implementation-per-slice.md:139`, `:175`; `phases/protocols.md:72` | Claude, verified | R3 |
| M4 | **Slice reviews skip LOW findings.** The fix step runs only for HIGH or MEDIUM; the skill's principle says all severities are resolved, and the whole-feature path does fix all. | `phases/implementation-per-slice.md:81`; `SKILL.md:210` | Codex, verified | R3 |
| M5 | **Panel verdict gaps.** No verdict covers one or two unrelated MEDIUM findings. A pass on the third fix round is both "exit the loop" and "halt regardless of verdict". | `bodies/panel-synthesis.md:26-29`; `phases/planning.md:152-154` | Codex, verified | — |
| M6 | **A matching final recount skips the reviewer.** Completion requires a reviewer to have accepted every disposition (ii)/(iii) argument; a `MATCH` goes straight to completion, so rows added by a late fix are never accepted. | `phases/implementation-whole-feature.md:74`; `references/enforcement-sites.md:133`; `bodies/implementation-complete.md:62` | Codex, verified | — |
| M7 | **Whole-feature fix steps are not handed what they must edit, and single-pass fixes are never re-reviewed.** 4c must update the site inventory but is passed neither it nor the standard; 4e is passed neither and has no stated site duties. The fixes at 2d, 3e, 4c, and 4e are each one pass with no second look (only site counts are re-checked, at 4e.5). | `phases/implementation-whole-feature.md:44-46`, `:63-65`; `phases/research.md:50-53`; `phases/planning.md:191-194` | Claude, verified | — |
| M8 | **The continuation body looks in the wrong folder.** It reads and writes handoff files in `SDD/orchestration/`, not `SDD/orchestration/compacted/`, and says to load the newest file rather than the one it was given. Its bail-out section also disagrees with the compact bodies (200 words, no `## PARTIAL` block). | `bodies/continue.md:19-25`, `:127-129`, `:162`; `SKILL.md:87`; `phases/protocols.md:12` | both, verified | R1 |
| M9 | **Re-starting a finished slice is half-built.** A resume rule and a `--confirm-restart` flag exist, but nothing says when the orchestrator writes the halt or passes `--force` / `--resume`, and the flag is missing from the arguments table. | `phases/protocols.md:75`; `bodies/slice-start.md:107`, `:113`, `:199`; `SKILL.md:189-205` | Claude, verified | R3 |
| M10 | **Resume after a final-recount halt is ambiguous, and one reading restarts the wrong iteration.** The anchor `## Final Recount - Started` is written "on entry" to 4e.5; the resume rule says "resume at 4e.5 step 1" and does not say whether a new anchor is written. `:80` implies it is ("a resumed 4e.5 never matches a discarded cycle's markers"). If it is, the "count never ran" rule looks after the new anchor for iteration 0 or 1, never finds it — even once the resumed count has finished — and spawns a count at that old iteration. If no new anchor is written, the rules work. | `phases/implementation-whole-feature.md:71`; `phases/protocols.md:77`, `:80`, `:83` | Codex, verified — holds under one of two readings (Codex stated the new anchor as fact; the text leaves it open) | R2 |
| M11 | **An interruption right after a retrospective skips the re-plan check.** The orchestrator runs the recommendation matcher "right after the retro subagent returns, in this cycle" and writes nothing when it finds no recommendation, so nothing on disk says whether it ran. The only resume-stage rule reads the halt block the matcher would have written. After `Retrospective Complete` the natural resume is commit → next slice, bypassing a halt that is meant to fire in every mode. | `bodies/slice-retro.md:296`; `phases/implementation-per-slice.md:98`, `:145`; `phases/protocols.md:68`, `:80` | Codex, verified | R3 |
| M12 | **The code review is told to check against a panel review it is never handed.** Panel synthesis preserves an "Abuse cases to cover" block because "the Step 4b code review checks test coverage against it"; the code-review body has a "spec-to-code regressions" line for panel findings the code does not honour. Neither 4b spawn passes the panel review, so that line can only ever say "None." Impact is limited: resolved findings live in the spec, and the review re-derives abuse cases from the catalog. **Struck:** the second half (spec critical review is passed the panel review but its body ignores it) — the agent definition covers it ("If the prompt names a prior review … avoid re-flagging resolved findings"). | `bodies/panel-synthesis.md:77`; `bodies/code-review.md:204`, `:486`; `phases/implementation-whole-feature.md:35-37`; `phases/implementation-per-slice.md:78`; struck half: `agents/sdd-critical-reviewer.md:34` | Codex, verified (first half); struck (second half) | — |
| M13 | **A missing security catalog plus `agent_security: true` fails instead of degrading.** The skill says a missing catalog closes the gate for the run; the phases still include the specialist and pass the path whenever the value is `true`. | `SKILL.md:46`; `phases/planning.md:113`; `phases/implementation-whole-feature.md:37` | Codex, phase text verified | — |
| M14 | **Parallel ADR capture can collide on numbers.** Step 3b spawns one subagent per decision without saying "sequentially"; each takes "highest number + 1" and regenerates the index. | `phases/planning.md:98`; `bodies/adr-capture.md:71-79`, `:172` | Claude, verified | — |
| M15 | **Whole-feature base commit is not recorded.** Per-slice records it as "the only durable record"; whole-feature relies on `HEAD` not moving, which H5 violates. | `phases/implementation-whole-feature.md:19`, `:27`, `:35`; `bodies/slice-start.md:153` | Codex, verified | R2 |

---

## Minor

| ID | Finding | Evidence |
|---|---|---|
| L1 | The diagram's stops table omits the panel halt, the slice fix-loop halt, the final-recount halt, and the slicing halt. | `docs/sdd-flow-diagram.md:122`, `:128-136` |
| L2 | Leftovers from the standalone plugin: `/sdd-migrate-layout` exists only in `sdd/commands/`; the code review and completion template check "<40% context usage", which a subagent cannot measure; `panel-specialist.md` numbers 4.7 before 4.6. | `phases/protocols.md:49`; `bodies/code-review.md:36-38`, `:383-392`; `bodies/implementation-complete.md:497-520`; `bodies/panel-specialist.md:177-197` |
| L3 | Log entries are capped at 10 lines, but the completion template is about 25 and the ADR note pastes a whole record. | `SKILL.md:136`; `bodies/implementation-complete.md:497-520`; `bodies/adr-capture.md:184-185` |
| L4 | Outside `sdd-flow`, verified, and slightly wider than Codex reported: `/adhoc-compact` and `/continue` disagree in three ways. (1) `/adhoc-compact` writes to `SDD/orchestration/compacted/`; `/continue` looks in `SDD/orchestration/` (the same folder mismatch as M8). (2) The generic file has `Resume From` / `Immediate Priorities`; `/continue`'s quality check asks for a "current focus section" and a priority list — a naming difference a reader can bridge. (3) `/continue` says generic files work but has only research, planning, and implementation branches. | `commands/adhoc-compact.md:52`, `:104-114`; `commands/continue.md:66-73`, `:82`, `:89-146` |

## Checked and clean

- Every script flag the markdown uses matches the scripts' argument parsers (`site-diff.py`: `--scope`, `--base`, and the `--base`-with-`FEATURE` rejection; `tier-mirror.py`: `sync --active/--in-review/--shipped/--brief`, `feedback --tier`, exit codes 0–3).
- The four tier-mirror points named in `SKILL.md` match the four places the phase chapters call the script.
- The design gate, deviation check, and re-plan re-entry agree across `SKILL.md`, `phases/planning.md`, `phases/protocols.md`, and `bodies/design-brief.md`.
