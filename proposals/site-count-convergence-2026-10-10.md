# Site count: stop new list differences every round (proposal, 2026-10-10)

Target: agent-engineering 3.11.0. **Approved 2026-10-10 as recommended (items 1, 2, 3, 6) and implemented in 3.11.0.** One addition made during implementation: `site-diff.py --register <SPEC>` applies the register mechanically, so a row either side keys by a restating ID is compared under its control.

**Recommendation: ship items 1, 2, 3 and 6 together. Drop 4. Give 5 no rule of its own.** The set adds no marker, no halt block and no resume rule.

## What the evidence shows (eduKate cycle 002, SLICE-001)

Replayed from the four real counts against the final inventory, so approximate.

- From iter 1 on, every key only the blind count had sat at a File + Symbol the implementer already listed. The differences were labels, not places.
- All 3 needs-code HIGH of iter 1 (`EDGE-005`, `FAIL-014`, `UX-003`) were green mutations at statements that already had argued (iii) rows under another ID. The fix was the same (iii) rows again: item 6, not a missing test.
- Every round also had a real finding: iter 0 twelve; iter 1 two MEDIUM outside the site count (a swallowed drawing fault, a leak in `progress.md`); iter 2 two test gaps (`SEC-005` no retry, `REQ-018` at `serve`).
- **So the set would have approved the slice at iter 3: three rounds, no halt, no fourth round.** Fix round 1 would have added none of its 118 inventory rows. A round is saved only if the register puts the two iter 2 gaps into the first count, which covered 15 of about 30 controls. Likely; not replayable.
- My ranking differs from yours: 2 and 3 each reach "approved at iter 3" alone, 6 is what empties iter 1, 1 is the only one that improves the first count, and 3 is a few lines of script.

## The six items

`STD` = `references/enforcement-sites.md`.

**1. Control register. Ship.**
- §1 becomes: "A control is keyed by its ID in the SPEC's `## Control Register` (`ID | Filed under | Reason`). An ID that states a rule of its own is filed under itself. An ID that only restates one path of another control's rule is filed under that control, and its text is read as one more path that control must hold on. An ID in no row is not a control. Both sides key by the register; neither picks. A SPEC with no register is keyed as before."
- §4.2 becomes: "A convention settles which **symbol** a site is keyed to. Which control is the register's; a convention never adds or re-keys one, except in a SPEC with no register." Its count-free rule stays: the register is allowed where a convention is not because it is written before any code exists.
- The counter may still count a rule the register leaves out, under its own ID, named in a header line `Outside the register:`. With item 3 that costs one mutation, not a round.
- Files: the planning, planning-complete and spec critical-review bodies; the counter, implementer and review bodies; STD §1 §4 §4.2.
- Independence lost: the counter no longer decides alone which IDs are controls; a wrong register misleads both sides alike. Guards: the two planning checks and the `Outside the register:` line.
- Evidence: one control set for all four counts instead of 15, 26, 28, 30. All 15 "control the implementer never listed" HIGH of iters 1 to 3 were IDs first counted in that round.

**2. Row-only closes inside the review. Ship.**
- New §6 outcome: "`CONFIRMED-MISSED`: a `MISSED` key whose site the reviewer deleted in this pass and saw a test fail. The reviewer appends the row to the implementer inventory, Disposition `(i)`, Evidence `mutation: … → failing test … (reviewer, <SCOPE> iter <N>)`. Resolved; not a finding." §4: Disposition and Evidence are the implementer's, "or a reviewer's for a row it adds under §6".
- Who writes: the reviewer. It holds the evidence and changes no code, so the blind count still describes the code. A fixer could touch code.
- A review whose only findings were row-only then reports none, and the slice leaves by the existing rule. New markers carry no `[r row-only]`; old ones read as before.
- Files: STD §4 to §6, both review bodies, both implementation phase files, `protocols.md`, `second-model-review.md`.
- Independence lost: such a row rests on one mutation run, not on the reviewer's, the fixer's and a recount.
- Evidence: HIGH would read 12, 3, 2, 0. Cycle 1's final recount had 23 of 24, 15 of 17, 50 of 55 and 39 of 40 HIGH row-only.

**3. Sites before labels. Ship.**
- §6 `MISSED`: "a key only the blind count has, at a File + Symbol the implementer lists under **no** control. HIGH." `CROSS-FILED`: "… lists under **any** control, including when the implementer lists that control nowhere. MEDIUM." The reviewer still mutates each site the blind rows name there; a green one is HIGH.
- `site-diff.py`: drop the `k[0] in impl_controls` test and the per-control `MISSED control` finding; findings are per key. `test_site_diff.py`: one test flips, four are added.
- Independence lost: none of the counter's. "The implementer never thought of this control" stops being HIGH by itself.
- Evidence: HIGH 11 → 3 at iter 1, 3 → 2 at iter 2, 2 → 0 at iter 3.

**4. Recount only what changed. Drop.**
- Your question: a site moved between functions is safe. Both functions' lines change, and the script treats anything uncertain as changed.
- The unsafe case is a fix that changes which paths reach an unchanged function: the miss becomes carried and waits for the final recount.
- It saves little: a changed non-Python file counts as wholly changed, and eduKate keeps nearly all sites in one `app.js`. It costs a tree snapshot per round and a rule for merging partial diffs. After 1, 3 and 6 a full recount no longer creates false HIGH.

**5. Pass on substance. No rule of its own.**
- With 2, 3 and 6 no label-only finding is left, so the existing exit (a review with no finding) already is this rule. §6 gets one sentence saying so.
- Its only extra effect would be to let an `UNCOUNTED` control wait for the final recount: a real count delayed, and nothing saved here.

**6. The (iii) reading. Ship.**
- New §6 text: "When the reviewer's mutation at an `EXTRA`, `CROSS-FILED` or row-count key leaves every test green, and an implementer row describes that statement as (ii) or (iii) under any control, green is what the row claims. It is resolved by the argument once the reviewer accepts it. It is HIGH only when no such row describes the statement, or the row is (i)."
- This is the reading all three reviewers applied. Files: STD §6, both review bodies. Independence lost: none.

## Whole-feature 4a.5 and the final recount 4e.5

- **4a.5**: same script, same review rules. It has no loop, so nothing is saved; severities change and the 4c fixer adds fewer rows.
- **4e.5**: the same four items, and it gains most: its diff has no carried section, so every label difference of the feature lands at once.

## Runs started before 3.11.0

- A SPEC with no register keeps the old keying; its conventions still settle controls.
- A marker with `[r row-only]` is read as today.
- A slice stopped at `## Awaiting Slice Resolution` resumes by the existing rule: a fresh count, the new diff, a review under the new rules.
