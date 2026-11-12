# The Fit Lens — fit and size

The one definition of the fit-and-size check. The slice review and the code review (4b) and the implementation
critical review (4d) run it; every fix spawn of Step 4 follows §4; the implementers follow §5. A body reads this file at the `FIT` path in its
prompt and never restates it.

A change can meet its spec and still be too big, or not fit the code it lands in. Each round of findings tends
to add code; this lens is the one that pushes back. How easily the next person or agent changes this code is a
review criterion like any other.

## 1. The questions

Read the code **around** each changed area — the module it lands in, its neighbours, the helpers it calls or
could have called — not just the diff. Then ask, of every change in scope:

1. **Match.** Does it match the surrounding code — its style, naming, helpers, patterns and layering?
2. **Reuse.** Does it reuse what exists, or duplicate a helper, type or pattern the code base already has?
3. **Size.** Could it be smaller, or folded into existing code? Is there a layer, wrapper, option or abstraction
   the approved tier does not need?
4. **Next change.** Will the next person or agent who changes this code find it where they would look, and change
   it in one place?

A test file is in scope like any other: a new test file where the project keeps one per module, or a fixture that
duplicates one in `conftest.py`, is a fit finding. Taste with no effect on a reader is not, and neither is a
speed concern the spec does not raise.

## 2. The footprint

A review that has a design brief compares the changed files (`SDD/` left out) with the brief's "What changes where"
table. **A changed file outside the footprint is a fit finding**, unless the spec's `## Deviations from Design Brief`
records it — those are departures the owner already saw. A file is outside the footprint when:

- it **existed** before the work and falls under none of the table's areas; or
- it is **new** — added since the work began — and no row names it by its own path. An area row covers changes to
  existing files only, so a new file under `tests/` or `src/page/` is outside the footprint unless the table names
  it.

Name the file and why it was touched. The brief's `## Builds on` lists the existing helpers and patterns the change
was to extend: a duplicate of one of them is a Reuse finding (§1).

## 3. Grading

A fit finding is **MEDIUM** when the change **adds a file, a layer, or a duplicate of an existing helper** — an
out-of-footprint new file included. Every other fit finding is **LOW**: listed, not fixed. Write each finding with
`file:line`, the question (§1) or the footprint (§2) it fails, and the resolution as code to remove or merge: the
helper to reuse, the module to fold the file into, the layer to drop. A fit finding never asks for code to be
added.

## 4. Fixing a fit finding

A fit finding is fixed by **removing or merging code** — reuse the existing helper, fold the file into the module
it belongs to, drop the layer — **never by adding code**. Behaviour the spec requires stays, and so do its tests:
a test moves with the code it tests. Never edit the spec or the brief to close a footprint finding: a file the
work truly needs that no approved area can hold is said so in the return, and the fix loop's stop takes it to the
owner.

Every fix round — of any finding, not only fit — reports its **net line change** in its return: lines added minus
lines removed by the round, `SDD/` left out. Before your first edit and after your last, take the net against
`BASE` — added minus removed in `git diff --numstat BASE -- . ':(exclude)SDD'`, plus every line of each untracked
file outside `SDD/` — and report the difference, e.g. `Net line change: -42`.

## 5. Building: extend before adding

The implementer — whole-feature 4a and each slice's 4a — reads this section and the design brief at the `BRIEF` path
in its prompt: its `## Builds on` list and the new files its "What changes where" table names. Nothing else in the
brief binds the implementer; the spec does.

- **Change existing code first.** Before you add a function, class, file, or layer, look for the code in
  `## Builds on`, and the module the change lands in, that can hold it, and extend that.
- **A new file is one the brief names.** Add no other unless the work cannot be done without it; then give it its
  reason like any new structure (below), and know that the review still reports it under §2 — the owner decides.
- **Give each new function, class, file, or layer a reason.** One line under `### New Structure` in the
  IMPLEMENTATION-PLAN (create the heading if the plan has none): what it is, and why the existing code named in
  `## Builds on` or the module it sits beside cannot hold it. The reviews read these lines; a reason does not
  excuse a finding under §1–§3.
