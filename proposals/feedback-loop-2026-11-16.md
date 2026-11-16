# Feedback loop — a record of where each defect was caught, and a monthly report on it (2026-11-16)

**Status:** proposal, decisions settled by the owner (2026-11-16); the kill test passed (2026-11-16). Nothing built.
**Affects:** `agent-engineering` — `sdd-flow` (end-of-feature report, research and design brief for bug-fix work, a
new `scripts/ledger.py`), `sdd-lite` (interview, brief, close-out), a new `defect-ledger` skill, `retro` (part 4
only), and one BB automation.
**Sources:** Josh Wulf, *Agentic Loop Engineering* (`https://camunda.github.io/agentic-engineering-explainers/loops.html`);
Lydia Hallie, *Rethinking Claude Code Best Practices* (AI Engineer, 2026-11-12).

## Why

`/retro` proposes environment changes from one cycle's evidence, and the owner picks. That is Wulf's "fix the bug,
then fix the loops" step, done by hand, for one cycle. Four things stop the setup from being a feedback loop:

1. **Nothing sees across cycles.** No one can tell that a kind of mistake keeps coming back across features, or
   that a check added earlier caught nothing since. `/retro` sees one cycle by design (its `## Limits` leaves
   pruning checks to the owner), and nothing else looks.
2. **Nothing sees an escape.** A bug a user finds weeks later reaches no retro. Wulf's score — the share of defects
   that reach users, by the loop that should have caught them — is not recorded anywhere.
3. **`/retro`'s evidence expires.** Session transcripts are deleted after 30 days, and the review records under
   `SDD/.records/` are git-ignored, so they live only in the checkout that ran the flow.
4. **`/retro` reads only Claude sessions.** Reviews run on Codex (`references/second-model-review.md`); the
   reviewer's sessions are never read.

## Who owns what

- **The owner owns loop maintenance:** deciding to add, move, or drop a check. Wulf's split — agents fix the code,
  engineers fix the loops. The tools below collect and count; none of them changes a check.
- **`/retro` stays one cycle.** It answers what in *this cycle* let a struggle happen. It does not read the ledger
  and is not changed by parts 1–3.
- **The monthly report (part 3) covers the checks as a whole:** repeats across features, escapes, checks that
  caught nothing.

## What this is not

- **Not an agent that changes its own process.** This repo tried automatic reflection: 37 slice retrospectives,
  all "Re-plan: no", removed (README, *No slice retrospective and no learnings ledger*). An agent that can edit its
  own reviews or checks can make them easier to pass (Wulf: the evaluator has to be independent). The report only
  reports; the owner picks every change.
- **Not a scheduled `/retro`.** The automation runs a script that counts lines. It runs no model and no skill.

## The design

### 1. The defect ledger

One file per application, **`SDD/defects.jsonl`, committed** (not under `SDD/.records/`, which is git-ignored). One
JSON object per line:

| Field | What it holds |
|---|---|
| `id` | `D-<n>`, numbered in order within the application; given by `ledger.py add` |
| `status` | `fixed`, or `open` — an escape recorded and not yet fixed. Review lines are written `fixed`: the cycle fixes them before it ends |
| `date` | When the defect was found |
| `feature` | The feature name, as in `SDD/` |
| `found_by` | Which loop caught it — one of the loops the application declares (below): `slice-review`, `code-review`, `final-check`, `ci`, `user` |
| `class` | A short name for the kind of defect (`unhandled-null`, `state-move`, `missing-auth-check`) — one of the names the application lists in `SDD/defects-setup.json` (below) |
| `severity` | `HIGH` or `MEDIUM`, as the review rated it; `user` escapes take the fixer's rating |
| `where` | The file, or `file:line` |
| `introduced_by` | The commit that introduced it, when known (always tried for `user`) |
| `check_added` | The check the fix added for this class (`lint:no-implicit-null`, `test:test_cart.py::test_empty`, a review-standard line), `none`, or `pending` while `status` is `open` |
| `source` | The review file and finding ID, or the issue / bug report |

- **Not recorded:** a test failing while the implementer works. That is the inner loop doing its job.
  LOW findings are not recorded either.
- **Every line is written through `ledger.py add` and completed through `ledger.py close`** (part 3), which check
  the fields first — no writer edits the file by hand.
- **Who writes the review lines:** the orchestrator, at the end-of-feature report (4j), copying each HIGH and MEDIUM
  finding from the cycle's review files. Mechanical: the reviews already rate and locate their findings.
  `sdd-lite` writes the same lines from its Codex review at close-out, with `found_by: code-review`.
- **Who writes the `user` lines:** the bug-fix rule below, or the owner through `/defect-ledger log` (part 3) for
  a bug fixed outside a cycle.
- **Who writes `ci` lines:** only an application that declares `ci`. When a CI run fails on a change and the
  change is fixed, the fix records it — inside a cycle the orchestrator, outside one the owner through
  `/defect-ledger log`. The plugin has no hook into CI; the line is written by hand, through `ledger.py add`.

**Each application declares the loops it has.** One committed file beside the ledger, `SDD/defects-setup.json`:

```json
{ "loops": ["slice-review", "code-review", "final-check", "user"],
  "classes": ["unhandled-null", "state-move"] }
```

- `loops` lists the loops that exist in that application. `user` is always in it: whatever the other loops miss, a
  user catches. `ci` is added the day the application has CI — and only then; an application without CI never has
  a `ci` line, and the report says *no CI* rather than *CI caught nothing*.
- `classes` is the per-repo list of defect-class names (decision 4).
- `ledger.py add` refuses a `found_by` or a `class` the file does not list. Adding a loop or a class is a one-line
  edit the owner approves.
- **Adding a loop needs nothing else from this proposal.** CI, an integration suite, or a test hook in one
  application is that application's own work, done when the owner chooses; the ledger starts counting it the day
  it is declared. The ledger is built for the loops that exist now.

### 2. The bug-fix rule

When the task is fixing a defect found after its change shipped, the brief (sdd-flow's design brief, or sdd-lite's
one-page brief) carries an `## Escape` section:

- the commit that introduced it, found with `git log` / `git blame`, or "not found";
- the loop that should have caught it, and why it did not;
- **Seen before** — the ledger's earlier lines with the same `class` (below);
- the earliest check that can catch this **class** of defect — a type, a lint rule, a test, a review standard — and
  whether the fix adds it (or why not).

The owner approves it with the rest of the brief — no new stop.

**The entry is written in two steps, so an abandoned fix still leaves a record:**

- **On approval of the brief** — the orchestrator (sdd-flow) or the main conversation (sdd-lite) writes the
  `found_by: user` line from the approved `## Escape` section, with `status: open` and `check_added: pending`. If
  `/defect-ledger log` already recorded this bug as `open`, the brief names that `id` and nothing new is written.
- **At close-out** — `ledger.py close <id>` sets `status: fixed` and `check_added` to the check actually built.
  When that differs from what the brief planned, the close-out report says so.
- **A cycle that ends without the fix** leaves the line `open`. The monthly report lists open escapes, so it is
  not forgotten; a later fix closes the same `id`.

**Seen before — the ledger read at the start of a bug fix.** Research (sdd-flow) or the interview (sdd-lite) runs
`ledger.py lookup --class <class>`, and the brief reports: yes or no, which loop missed it each time, and what
`check_added` said.

- **Order matters: cause first, ledger second.** Research finds and states the cause of *this* defect before it
  reads the ledger, and names the `class` from that cause. A bug that looks like an earlier one can have another
  cause; the ledger is history, not a diagnosis.
- **A repeat after a check was added asks for a stronger check.** When an earlier line of the same class has a
  `check_added` other than `none`, that check did not hold. The brief proposes a check in an earlier loop (a type
  or a lint rule rather than another test), or says why none can be.
- **Bug fixes only.** A feature has no defect class to look up yet.
- **Expect little at first.** With a short ledger the answer is nearly always "not seen before". That costs one
  command.

### 3. `ledger.py` and the monthly report

**`skills/sdd-flow/scripts/ledger.py`** — stdlib Python, the one reader and writer of the ledger's format.
`sdd-lite` runs it by path, as it already runs `snapshot.py`. Four commands:

- **`add`** — checks a line's fields (required fields present, `found_by` and `severity` from their lists), gives
  it the next `id`, and appends it. Rejects a bad line with the reason.
- **`close <id> --check-added <check|none>`** — sets an `open` line to `fixed` with its check, rewriting that one
  line in place. The only edit the format allows; any other change to an earlier line is refused. Git history
  keeps the open version.
- **`lookup --class <class>`** — the earlier lines of one class, oldest first. What *Seen before* calls.
- **`summary`** — per application: the loops it declares; lines and features counted; the share each loop caught, with `user` as the
  escape rate; classes seen in more than one feature; escapes by class with their `introduced_by`; each
  `check_added` with the lines of its class since it was added (none since → "no catches since added"); open
  escapes, oldest first.

Tests sit beside the others (`python3 -m unittest discover -s scripts/tests`), against a fixture ledger.

**The `defect-ledger` skill — the owner's way in.** User-invoked, so the owner never has to remember the script's
commands or fields. It runs `ledger.py` and asks only for what it cannot work out:

- **`/defect-ledger report [application]`** — runs `summary` and shows it, with the threshold heading. Asked
  what a line means, it explains from the ledger; it proposes no change to a check unless asked.
- **`/defect-ledger log`** — records an escape found outside a cycle (a bug fixed by hand, or reported and not yet
  fixed). It asks for what the bug was, finds `introduced_by` with `git log` / `git blame`, proposes the `class`
  (reusing an existing name where one fits) and the other fields, shows the line, and writes it through `add` only
  once the owner approves it — `fixed` with its check when the fix is done, `open` when it is not.
- **`/defect-ledger lookup <class or description>`** — the earlier lines of a class; given a description instead,
  it proposes the matching class first.

The flows do not use the skill: `sdd-flow`'s subagents may not invoke skills, so the flows and the automation run
`ledger.py` by path. The skill is one more caller of the same script, never a second copy of the format.

**The BB automation — report only, monthly.** A script automation that runs `ledger.py summary` over the
applications it lists, reading each one's committed `SDD/defects.jsonl` on its default branch, and files one BB
task with the result for the owner. It runs no model, edits no file, and opens nothing else. The owner reads the
task and decides; a change it leads to is ordinary work (a check added by hand, or a `/sdd-lite` change).

**Below the threshold, counts only.** Until an application's ledger holds **5 features or 30 lines**, its section
of the report is headed *below threshold — counts only*: with so few cycles, a check with no catches may just guard
a rare class. Nothing is built later — the threshold changes how the report reads, not whether it runs.

### 4. The bb trace index as an optional source for `/retro`

The bb `traces` plugin (third-party, `patleeman/bb-plugins`, 0.1.1) indexes Claude Code and Codex sessions into
`~/.bb/plugins/traces/data.db` (SQLite). Checked read-only on 2026-11-16: 7,036 Claude sessions back to 2026-07-28,
743 Codex sessions back to 2026-10-03, kept after the transcript file is deleted. Each event keeps its kind, role
and a summary of up to ~1,000 characters; the full event is not kept.

- `scripts/session-digest.py` gains one fallback: when a session's transcript file is gone, it reads the session's
  events from the index, and marks each item as a summary. With `--codex` it also lists Codex sessions for the same
  repository and date range.
- **Optional.** No index, or an unreadable schema → the digest says so once and carries on without it.
- **One adapter.** All reading of the index sits in one function, tested against a small fixture database, so a
  schema change in someone else's plugin breaks one test, not the retro.
- **Rule unchanged:** a candidate built on a summary says so; nothing from the index is written into the repository.

## Kill test (before step 1)

Hand-label one of the owner's applications (`currents` has the most history): every fix commit in the last three
months that corrected an already-merged change. For each, could the loop that should have caught it be named, and
the introducing commit be found?

- **Mostly yes, and some were escapes** → build Tier 1.
- **No escapes, or the labels are guesses** → the ledger has nothing to measure. Build only part 4.

**Result (2026-11-16): passed — build Tier 1.** Labels in
[`feedback-loop-kill-test-2026-11-16.md`](feedback-loop-kill-test-2026-11-16.md); the owner confirmed
them on 2026-11-16. Of 49 fix commits in 628: 22 defects escaped to production or the first real run, 6 test-suite defects were
found only after merge, 5 were caught by a rehearsal after the reviews passed, and the rest were in-cycle review fixes
or duplicates. The loop that should have caught each could be named from the commit message, and `git blame` found a
plausible introducing commit for all but one (an external change); ten were spot-checked.

- **Repeats the ledger would show at once:** source content reaching published output (6), health probes that
  false-alarm or mislead (5), tests that are not isolated (5), transient errors read as permanent or empty (3),
  overmatching identity (2).
- **`currents` has no CI and no pre-commit hook;** the 6 post-merge test-suite defects are what CI on a clean
  machine catches. The owner decided not to add CI to `currents` yet (2026-11-16).
- **Limits:** one application, whose commit messages are unusually detailed; introducing commits are `git blame`'s
  last change to the fixed lines, not a traced root cause.

## Tiers

- **Tier 1:** part 1 (review lines and `user` lines, with `check_added`); part 2 (with *Seen before*); part 3 —
  `ledger.py` (`add`, `lookup`, `summary`), the `defect-ledger` skill, `SDD/defects-setup.json`, and the monthly
  report-only automation. `ci` lines for eduKate start once its CI runs (separate work, below).
- **Tier 2:** part 4 (trace index).
- **Separate, not part of this proposal:** CI for eduKate (its own work, in its own repo; it runs the existing test
  and lint commands on every push). Its `SDD/defects-setup.json` gains `ci` when that CI runs. The other four
  applications get CI if and when the owner decides.
- **Later, if the report earns it:** a `/defect-ledger` step that turns the summary into proposed moves (this check
  earlier, that one dropped) — only if reading the table proves not enough; reading ledgers across applications
  together;
  comparing escape rate and cost per feature across `sdd-flow`, `sdd-lite` and plain Claude Code (task
  CLAUDEPLUG-17, check 3).

## Decided — the owner, 2026-11-16

1. **Ledger location:** `SDD/defects.jsonl`, committed.
2. **Severity bar:** HIGH and MEDIUM.
3. **`sdd-lite` writes the ledger:** yes, one record for both paths.
4. **`class` names:** a short per-repo list kept beside the ledger; the orchestrator picks from it, and a new name
   is added only with the owner's approval.
5. **The automation:** monthly, over Currents, Downstream News, Sift, eduKate and AI-video-marketing; one task a
   month, filed in the claude-plugins BB project.
6. **The threshold:** 5 features or 30 lines.
7. **CI:** eduKate only, for now, as separate work. Every application declares its own loops; the ledger counts
   only those.

## Costs and risks

- One more committed file per application, and one more step at close-out (two for a bug fix: one at approval).
- `close` makes the file not purely append-only. Two branches closing different `id`s merge cleanly (different
  lines); two branches *adding* lines at once can collide on the next `id`, which `worktree-merge` would need to
  renumber, as it already does for ADR and feature numbers.
- `class` names will drift; repeats are found only as well as the names match — in *Seen before* and in the report.
- *Seen before* can anchor research on an earlier diagnosis; the cause-first order is the guard, and the brief
  states the cause before the ledger lines.
- A monthly task that says the same thing each month gets ignored. If three reports in a row lead to no change, the
  owner revisits the cadence or the report's contents.
- The automation reads each application's default branch in its main checkout; ledger lines still on an unmerged
  branch are not counted until it merges.
- The trace index is someone else's plugin with no stated retention; it can change or disappear.
- Labels for `user` escapes depend on the fixer's honesty about which loop missed it; the owner approves them in
  the brief.
