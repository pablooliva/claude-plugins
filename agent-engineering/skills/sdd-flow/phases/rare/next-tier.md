# Rare case — Starting the next tier (Step 0)

Read this only on `/sdd-flow --next-tier [feature-name]`, before the rest of Step 0 (`phases/setup.md`).

---

## Starting the next tier (`--next-tier`)

`/sdd-flow --next-tier [feature-name]` starts a new cycle for the next delivery tier of a feature that already shipped one. A tier is one complete cycle with its own number, brief, spec, reviews, and commits; this is how the next one begins. It replaces steps 1–3 at the top of Step 0 (`phases/setup.md`):

1. **Find the tier plan.** `SDD/flow/TIERS-[feature-name].md`. With no name given, use the only tier plan that has a tier neither `shipped` nor `dropped`; if there are several, list them and stop.
2. **Pick the tier.** The lowest-numbered tier whose status is neither `shipped` nor `dropped`. Refuse, naming the reason, if the tier below it is not `shipped` (a tier is used before the next is planned), or if no tier is left.
3. **Resolve identifiers.** `[###]` = the next sequential number. `[feature-name]` = the tier plan's feature name with `-t2` or `-t3` appended. The task description = that tier's sketch plus the Deferred rows aimed at it, quoted from the tier plan.
4. **Pull feedback from the tier's task.** Run `python3 "$SKILL_ROOT/scripts/tier-mirror.py" feedback <tier plan> --tier N`: comments left on that tier's BB sub-task since the previous tier shipped are copied, dated, into the tier plan's `## Feedback`, so the Step 1.5 interview, research, and the brief read them from the file. Record and report the result per `SKILL.md` → Tier Task Mirror (resolve SKILL_ROOT first if this is the first thing the session does).
5. **Record** in the Step 0 record (step 5 of the list at the top writes it — these lines go inside that block, beside the identifiers): `Next-tier cycle: Tier N`, **TIER_PLAN** = the tier plan's path (it keeps the first tier's feature name — every later spawn is given this path, never one derived from the suffixed name), and the previous tier's research document (from the tier plan's `Built in` column: the same number and name as that spec).

Then continue with steps 4–5 of the list at the top of Step 0, and go straight to Step 1.5: **a next-tier cycle has no scope assessment.** Its task description is the most the tier could hold — the whole sketch and every Deferred row aimed at it — and the design brief cuts it first (`bodies/design-brief.md` rule 9); a split made before that cut sizes work the brief may remove, and its items, run as plain `/sdd-flow` tasks, would no longer be tied to the tier plan.
