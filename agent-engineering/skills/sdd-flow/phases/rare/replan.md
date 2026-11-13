# Rare case — Re-plan

Read this only after the user asks for a re-plan at a slice pause (`phases/implementation-per-slice.md` → PAUSE), and again at 4a.0 when its re-plan condition holds.

---

## Running the re-plan (Step 2.5)

A re-plan is asked for in words, at a slice pause (`phases/implementation-per-slice.md` → PAUSE). The slice before it is already committed. Run 2.5c with the latest slice review (its `## Re-plan` line says what the slice showed) as an extra input and, in place of a user reply, the line `RE-PLAN: <the user's request, verbatim>`. The gate then fires as at 2.5b (`phases/design-gate.md`), with `Re-plan: yes` in the halt block. On `approve`, continue to 3a with that review in the planning subagent's prompt; the re-plan's planning run ends, like any other, with `## Planning - Accepted` at 3g, and implementation starts at the new plan's first slice not yet `Complete`.

---

## Clearing the replaced plan (4a.0)

**After a re-plan, clear the replaced plan away first** — before 4a.0's table check (`phases/implementation-per-slice.md`). It applies when the latest `## Awaiting Design Approval` block says `Re-plan: yes` and no `## Slices Superseded` line follows the latest `## Planning - Accepted`. The orchestrator, in this order:

1. Appends `## Re-plan Preparation - Started` to `progress.md` — one line naming a **new** folder `SDD/.records/reviews/superseded/[YYYY-MM-DD_HH-MM-SS]/`. If such a line already follows the latest `## Planning - Accepted` (an earlier attempt was cut short), write no new one and reuse its folder: steps 2–3 each skip what is already done.
2. In the IMPLEMENTATION-PLAN, renames the live `## Slice Progress` header to `## Archived Slice Progress (pre-replan)`. The table stays verbatim, as audit trail. (No live header: already done — skip. The fresh table is scaffolded only after step 4, so a live table found here is always the replaced plan's.)
3. Moves the replaced plan's per-slice records into that folder (plain `mv` — they are git-ignored): every `REVIEW-SLICE-*`, `TRACE-TREE-SLICE-*`, and `EVAL-RESULTS-SLICE-*` file of this feature still in its original place. They are kept, never deleted, and a folder per re-plan means a second re-plan — whose files carry the same names — never collides with the first. The new plan reuses the old slice IDs, and the reviews the slice pause and the brief-check line pick up by ID must be the new plan's only. The per-slice commits stay where they are, and the replaced plan's slice files (`SLICE-*`) stay in `SDD/implementation/slices/`, committed.
4. Appends `## Slices Superseded` to `progress.md` — one line: the folder, and how many files it holds.
