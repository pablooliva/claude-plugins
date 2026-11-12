# Task: sdd-flow release 1 — remove the mode and the stop-skipping flags

You are working in a git worktree of the claude-plugins repo. Change the `agent-engineering` plugin's `sdd-flow`
skill so that it has fewer modes, flags and stops, as decided below. This is release 1 of two; release 2 (the
broader cuts and size controls) is out of scope — do not start it.

## Why

An evaluation (sdd-flow-eval: FINDINGS-001, FINDINGS-002) found sdd-flow's results correct but larger and
harder to follow than needed, and its instructions long. The owner reviewed every flag and stop that lets the
flow skip a check or run alone. They do not read code: a stop exists only when there is a decision for them.
The full decision record is `proposals/sdd-flow-simplification-2026-11-12.md`
— read it first; where this prompt and that note differ, the note wins and you say so.

## What to change (all decided; do not reopen)

1. **Remove supervised and autonomous modes:** `--auto`, `--supervised`, the Step 1 mode question
   (`phases/setup.md`), and every "in supervised mode / in both modes / autonomous" branch.
2. **Final commit (4h): no unconditional stop.** It stops only when evals are on and a judged requirement waits
   for the owner's sign-off (as today). Existing halts for unresolved findings (e.g. the final recount halt)
   stay. Otherwise the flow commits and ends with a short report: what shipped, what was deferred, anything left
   unproven, the diff size. (A growth-budget stop comes in release 2 — not now.)
3. **Remove `--skip-slice-checkpoints`.** The flow always pauses after a slice. The pause is for trying the
   slice, not reading its code: it says what to run and what the owner should see, plus the slice's one-line
   check against the design brief. Read what the pause message shows today and drop review detail from it.
4. **Remove `--skip-clarify`.** The clarification gate (1.5) asks every time, yes or no, unless
   `SDD/research/CLARIFICATION-[###]-[feature-name].md` exists. Yes stops for `/research-clarify`; no proceeds
   and records the skip (as today's "n"). Drop the third answer ("s").
5. **Remove `--reviewer` in every form** (`codex:<model>`, `:nonet`, `opencode:<provider/model>`, `claude`) and
   the `SDD_FLOW_REVIEWER` environment variable. Codex is the only second model.
   - KEEP the fallback: when Codex is not installed, or a review run fails twice, a Claude reviewer runs and the
     owner is warned, as today.
   - KEEP `SDD_FLOW_REVIEWER_ARGS` working (the benchmark harness passes Codex flags through it).
   - Update `scripts/second-model-review.py` and its tests to match.
6. **KEEP `--next-tier`** unchanged.
7. **Remove `--fall-back-to-whole-feature`, `--retry-slicing`, and the "no meaningful slices" stop
   (`## Awaiting Slicing Decision`).** Instead the planner writes `delivery_mode: whole-feature` with a one-line
   reason in the spec, and the flow tells the owner in its next message. No stop.
8. **Remove `--replan`, `--from-slice`, `--override-replan`, and the re-planning halt (4c.5).** Instead the slice
   pause shows the retrospective's re-plan advice when it has any; the owner asks for a re-plan in words.
   Define what the flow does on such a request in as few lines as possible (revise the brief → the design gate
   fires → re-run planning), reusing today's re-plan steps where they fit.
9. **A missing OWASP catalog** (`skills/ai-agent-security-review/references/owasp-ai-agent-controls.md`) is a
   broken install: halt, like a missing STANDARD. Remove the "agent_security silently closed" path.
10. **Observability at the design gate.** When the feature calls a model and the app has no
    `SDD/OBSERVABILITY.md`, the design brief says so and recommends running `/observability-init` before
    approving. On approval the flow checks for the file again; the tracing and evals gates are settled from
    that check (the "decided once" point moves from Step 0 to design approval). Update `bodies/design-brief.md`,
    `phases/setup.md` (Step 0 record), `phases/planning.md` (3c gate resolution), and `SKILL.md`.
11. **Removed flags are ignored with a one-line note** for this release, so old command lines keep working
    (the benchmark harness sends `--auto --skip-clarify --reviewer codex`). They must never be read as task text.
12. **No compatibility code for old stop records.** Cycles in progress finish on the old version; the flow
    already stops on a stop record it does not recognise. Say this in the release notes.

## Where

Every file that names a removed flag (from a grep; check it yourself):
`agent-engineering/README.md`, `agent-engineering/commands/commit.md`, `agent-engineering/docs/sdd-flow-diagram.md`,
and under `agent-engineering/skills/sdd-flow/`: `SKILL.md`, `bodies/planning.md`, `bodies/slice-retro.md`,
`bodies/slice-review.md`, `bodies/slice-start.md`, `phases/implementation-per-slice.md`,
`phases/implementation-whole-feature.md`, `phases/planning.md`, `phases/protocols.md`, `phases/setup.md`,
`references/second-model-review.md`, `scripts/second-model-review.py`, `scripts/tests/test_second_model_review.py`.
Also `bodies/design-brief.md` (item 10) and the repo's `CLAUDE.md` where it describes these behaviours.

## Rules

- Read the repo's `CLAUDE.md` first. `SKILL.md` states three rules every body and phase edit is checked against
  (a body's only inputs are its prompt's paths; every stop that waits for an answer has a halt block, a resume
  rule in `phases/protocols.md`, and a row in the diagram; every slice state change, stop and commit has an
  owner in `phases/implementation-per-slice.md`'s owner table). A removed stop is removed from all three places.
- Remove, don't relabel: no "formerly", "deprecated" or "before 4.0.0" notes in the flow files beyond the one
  removed-flags note (item 11). The flow's instructions must get shorter; report the size of `SKILL.md` and the
  phase files before and after.
- Do not modify the `sdd` plugin. Do not start release 2.
- Version: bump agent-engineering to 4.0.0 in both `agent-engineering/.claude-plugin/plugin.json` and
  `.claude-plugin/marketplace.json`.
- Update `docs/sdd-flow-diagram.md` (both diagrams and the stops table) so it matches.
- Run the skill's tests: `python3 -m unittest discover -s agent-engineering/skills/sdd-flow/scripts/tests`.
- Get a Codex review of the uncommitted change (`codex review --uncommitted`, output to a file, read the last
  block), fix what it finds that is real, and say what you did not fix and why.
- Do not commit. Stop with the change uncommitted and report back.

## Done when

- No file in the plugin names a removed flag, except the one place that ignores them with a note.
- Each item 1–12 is done, and you can point to the file and line for each.
- Tests pass; the Codex review has been run and answered.
- Your report lists: items done, anything you could not do or decided differently (with the reason), the size
  before/after, and the Codex findings left open.
