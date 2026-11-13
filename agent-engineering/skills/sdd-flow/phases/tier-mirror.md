# Tier Task Mirror (record-keeping, never silent)

Read this at a mirror point, for a tiered feature only (approved tier `1`, `2`, or `3`).

---

The tier plan file is the record of a feature's tiers; BB tasks mirror it — one parent task for the feature, one sub-task per tier — so a waiting tier shows on the board and feedback can be left on it between cycles. The orchestrator keeps the two in step by running `python3 "$SKILL_ROOT/scripts/tier-mirror.py"` at the four points the phase files name: design-gate approval (`phases/design-gate.md` → 2.5b), before the final commit and at the completion announcement (`phases/end-of-feature.md` → 4h–4j), and the start of a next-tier cycle (`phases/setup.md` → Step 0). It runs only for tiered features (approved tier `1`, `2`, or `3`). When no tracker project is linked to the BB project, the script **creates one** — a missing project is never a reason to skip.

The script's first stdout line is `Result: …`. After every run, append `## Task Mirror - <that line, verbatim>` to `progress.md`, then act on the exit status:

- **0** — done. If the line says a tracker project or tasks were created, tell the user in the next user-facing message, with the keys.
- **3 (`OFF`)** — there is no `bb` CLI, or the checkout is not inside a BB project, so there is nothing to mirror to. **Tell the user in the next user-facing message**, quoting the line. Do not run the mirror again in this cycle.
- **1 (`ERROR`)** — a `bb` command failed. Run it once more (it is safe to repeat: it creates only what is missing). If it fails again, **tell the user in the next user-facing message**, quoting the line, and carry on — the tier plan is unaffected, and the next mirror point tries again.
- **2** — the tier plan is missing or malformed: treat as a failed design-brief (or completion) step and re-spawn it.

The mirror never halts the flow and is never skipped without the user being told. The orchestrator never edits the tier plan itself; the script writes task keys into its `Task` column and copies task comments into its `## Feedback`, and nothing else.
