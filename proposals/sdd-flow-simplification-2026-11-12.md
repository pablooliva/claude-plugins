# sdd-flow simplification — owner decisions (2026-11-12)

Source: FINDINGS-001 and FINDINGS-002 in sdd-flow-eval/SDD/research, and the owner's answers in this thread.
Input for the prompt that implements the change in a new worktree. Nothing implemented yet.

## Framing

- sdd-flow stays the default path for application development (tiers, slices, design gate, tracing, evals).
  sdd-lite stays for small changes; do not add tracing or evals to it.
- The open-source benchmark tasks were small; FINDINGS-002 (eduKate) is the application-scale evidence.
  Its findings (diffs ~4x plain, specs/reviews not reused, tests 4x source, long review loops) drive the cuts.
- The owner does not read code. Stops exist only for decisions; code-level checking belongs to the reviews.

## Modes, flags and stops

1. **Remove supervised/autonomous modes** (`--auto`, `--supervised`, the Step 1 mode question, every
   "in supervised mode / in both modes" branch).
2. **Final commit (4h): no unconditional stop.** Stop only when:
   - evals are on AND a judged requirement waits for the owner's sign-off (as today);
   - the growth budget is overrun (new, with the size controls);
   - an unresolved finding remains (already a stop today: the final recount halt).
   Otherwise commit and end with a short report: what shipped, what was deferred, anything left unproven,
   diff size against the budget.
3. **Remove `--skip-slice-checkpoints`.** Always pause after a slice. The pause is for trying the slice, not
   reading code: it says what to run and what the owner should see, plus the slice's one-line brief check.
   Check what the pause message contains today and trim review detail from it.
4. **Remove `--skip-clarify`.** The clarification gate asks every time (yes/no) unless
   `SDD/research/CLARIFICATION-*` exists. Yes stops for `/research-clarify`; no proceeds and records the skip.
   Drop the third answer ("s", skip now and in future).
5. **Remove `--reviewer` (all forms, incl. `codex:nonet`, `opencode:<model>`, `claude`) and the
   `SDD_FLOW_REVIEWER` env var.** Codex is the only second model.
   - KEEP the fallback: when Codex is not installed or a review run fails twice, a Claude subagent reviews
     and the owner is warned (as today).
   - KEEP `SDD_FLOW_REVIEWER_ARGS` working (the benchmark harness uses it to start Codex in its container).
6. **KEEP `--next-tier`.** eduKate used it (SPEC-004, SPEC-006); it ties a cycle to the tier plan.
7. **Remove `--fall-back-to-whole-feature` and `--retry-slicing`, and the "no meaningful slices" stop.**
   Replacement: the planner writes `delivery_mode: whole-feature` with a one-line reason; the owner sees it
   at the post-spec simplicity stop. (Never fired in eduKate.)
8. **Remove `--replan`, `--from-slice`, `--override-replan`, and the re-planning halt.** Replacement: the
   slice pause shows the retrospective's re-plan advice; the owner asks for a re-plan in words if wanted.
   (All 37 eduKate retros said "Re-plan: no".)
9. **OWASP catalog missing = broken install → halt**, like the other shipped files. Removes the path where
   `agent_security` silently switches off.
10. **Observability prompt at the design gate.** When the feature calls a model and the app has no
    `SDD/OBSERVABILITY.md`, the design brief says so and recommends running `/observability-init` before
    approving. On approval the flow checks for the file again. The "decided once" point for the tracing and
    evals gates moves from Step 0 to design approval.
11. **`review_panel:`** stays (the planner sets it; all eduKate specs used it). Checked: `accessibility`,
    `privacy`, `cost` are allowed values run on `sdd-workhorse` (planning.md:190, panel-specialist.md:180);
    eduKate produced findings for both. No fix needed. Panel narrowing ("only specialists the change
    touches; they flag risks, do not add requirements") is part of the broader cuts.
12. **Cycles in progress finish on the old version.** The flow already stops on a stop record it does not
    recognise. eduKate SPEC-007 is in progress (final recount, iter 5, 2026-11-12): do not update the
    plugin in eduKate until it is committed.
13. **Benchmark harness** (`sdd-flow-eval/replay/record.py:19`, `--auto --skip-clarify --reviewer codex`) is
    updated separately in the sdd-flow-eval project, not in this change. The plugin change must not break on
    those flags in the meantime (see open point below).

## Broader cuts and size controls (from the analysis; scope of the implementing prompt to be confirmed)

- Cut: enforcement-site machinery except for security rules; fixing every LOW finding (list them, fix
  HIGH/MEDIUM; after two rounds only HIGH real bugs); one of the two end-of-feature code reviews; per-slice
  retrospective and learnings ledger (keep only the re-plan line); compatibility clauses for older runs;
  process records in the repo (move reviews, counters, call logs, site counts, eval results out of `SDD/`).
- Add: reuse map and growth budget in the design brief; the decided post-spec simplicity stop (3g);
  fit-and-size lens in reviews; "extend before adding" implementer rule; one consolidation pass at the end;
  tests check visible behaviour, not wording or shape; test-to-code ratio shown as a warning.
- Slim the orchestrator: subagents return verdict + path; target ~15k tokens of core instructions.
- Decided 2026-11-12 in detail: the site proof becomes one security verification, LOW findings are listed
  not fixed, mutation checks run in a scratch copy — `proposals/enforcement-site-proof-2026-11-12.md`
  (evidence) and `proposals/enforcement-site-proof-prompt-2026-11-12.md` (implementing prompt).

## Settled 2026-11-12

- A removed flag (`--auto`, `--supervised`, `--skip-clarify`, `--skip-slice-checkpoints`, `--reviewer`,
  `--fall-back-to-whole-feature`, `--retry-slicing`, `--replan`, `--from-slice`, `--override-replan`) is
  ignored with a one-line note, for one release, so old command lines (incl. the harness) keep working.
- Release 1 = the flag and stop changes (items 1-13) only. The broader cuts and size controls are a second
  release, measured against the first. The growth-budget stop in item 2 arrives with release 2.

## Release 2 must carry over (temporary choices made in release 1)

- **Slicing fallback (item 7):** release 1 tells the owner in the flow's next message when the planner falls
  back to `delivery_mode: whole-feature`. Release 2 moves this onto the post-spec simplicity stop (3g), shown
  with `review_panel:` and the spec's deviation list.
- **Final-commit stop (item 2):** release 2 adds the growth-budget overrun as a reason to stop at 4h.
