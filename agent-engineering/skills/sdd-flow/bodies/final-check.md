# Final Check — Security Verification and the Last Look (Step 4e.5)

You are a spawned subagent in an orchestrated /sdd-flow run. Your prompt provides resolved artifact paths and identifiers — use them verbatim. This file is your complete instruction set. Do not spawn subagents or invoke slash commands/skills, even if an Agent/Task tool is available — the flow's flat-orchestration contract forbids it; all work happens inline in your own context.

This is the last review of the feature, run after every fix has landed. It reads the whole assembled feature — in per-slice mode, every slice together — once per round, and it changes no code: every mutation is made in a scratch copy (TEST_INTEGRITY §8).

## Inputs (all from your prompt)

Always: `SCOPE = FEATURE`, `ITER = <k>`, the SPEC, the IMPLEMENTATION-PLAN, `BASE` (the commit the feature started from), **SDD_ROOT** (the records folder; `SDD` when your prompt names none; in a command write its value in its place, inside the same quotes), **SECURITY** (`references/security-verification.md`), **SEVERITY** (`references/severity.md`), **TEST_INTEGRITY**, **STATE_MODEL** (`references/state-model.md`), and the gate lines `tracing: on|off` and `evals: on|off`. With the `agent_security` gate open: **CATALOG** and the panel review `SDD/.records/reviews/PANEL-SPEC-*`. With `tracing: on`: **LENS**, **TRACING**, **OBS_RECORD**, **TRACE_TREE_SCRIPT**, and **TRACE_TREE** (a file named for this iteration). With `evals: on`: **EVALS**, **EVAL_TEMPLATES**, **OBS_RECORD**, the eval run line (`Eval run: …`), and **EVAL_RESULTS** when the run wrote results (your prompt says so in one line when it did not). `PREVIOUS REVIEW` on every round — on the first, the code review (Step 4b); on a later round, the final-check review before it — and on a later round also `SNAPSHOT` and `FIXED` (below).

If an input the gates call for is missing, return a failure to the orchestrator naming it. Do not list `SDD/` to find one.

## The four parts, in this order

1. **Security verification.** Read SECURITY and run it as written: list the security rules (§1), look for a path on which each does not hold (§2), and check that each rule's guard is proven by a test that fails when the guard is removed (§3) — the mutation in a scratch copy. Write the `## Security Verification` section in the shape §5 gives.
2. **The whole test suite.** Run the project's full test suite once, in the working tree, unchanged. A suite that does not pass is a HIGH finding, `[needs-code-or-test]`, titled *the test suite does not pass after the last fix*, naming the failing tests. With `tracing: on`, when OBS_RECORD's trace run is the whole suite, that one run serves both this part and part 4.
3. **The last-look test checks.** Read TEST_INTEGRITY and run its **last-look checks** (§5) as written: T1 and T2 over everything changed since `BASE`, and T3 and the reading half of T4 over the tests this feature added — no other check, no mutation, no probe. Write a `## Test Integrity` section with the T1–T4 rows of the table its §6 gives (T4 marked "by reading"). Findings are tagged `[needs-code-or-test]`.
4. **The gated checks.**
   - **`tracing: on`** — with the suite passing, read LENS and run it at `SCOPE = FEATURE` against every marked node of the spec's `### Planned call graph`. *The code the scope changed* (LENS §4) is everything changed since `BASE`; a difference already under `### Implementation Deviations` in the IMPLEMENTATION-PLAN is listed as recorded and not raised again (LENS §6). Write the `## Tracing Lens` section in the shape LENS §7 gives. With the suite failing, do not run the lens: the section is the one line `Tracing Lens not run — the test suite does not pass (F<n>)`, and you write no trace tree.
   - **`evals: on`** — read EVALS and run its §7 at `SCOPE = FEATURE`: every case of the spec's `### Evals`, and every older case the application holds. Run it whether or not the suite passed — it reads a run already made. **You make no eval run yourself;** the one command of it you may run is `--self-test` (EVALS §4). The test run §7 speaks of is part 2's. Write the `## Eval Check` section in the shape §7 gives. A sign-off requirement counts as met when it is implemented and its judged eval has its scores in the run of record (EVALS §9).
   - **The spec has `### State model`** (no gate line: the spec decides) — read STATE_MODEL and run its §5 at `SCOPE = FEATURE`: every move in the spec's model, the as-built model drawn from every write to the state in the repository, whether or not the suite passed — it reads the code. Write the `## State Check` section in the shape §7 gives; its `**State model:**` line is what the end-of-feature report shows the owner. A later round runs it in full. Findings are tagged `[needs-code-or-test]`. With no `### State model`, write nothing about it.
   - With a gate off, do nothing for it and write nothing about it.

## Findings: the line, the numbers, the earlier ones

- **The rating.** Rate every finding you judge by **SEVERITY** (at the path in your prompt): its impact and who can make it happen, with a `Trigger:` and an `Impact:` line under the title of every HIGH and MEDIUM. A finding whose severity a reference or a rule of this body fixes keeps that severity. When `ITER` is 2 or more — with or without `SNAPSHOT` — a new finding (not in `PREVIOUS REVIEW`, and not a lead from a void run of an earlier round) blocks only when SEVERITY §5 says so: severe impact in normal use; any other new finding it rates is LOW.
- **The finding line.** Every finding — any severity, from any part, in any section — opens with exactly one line:

  ```
  FINDING F<n> | <HIGH|MEDIUM|LOW> | <file:line, or file, or -> | <open|fixed>
  ```

  For example `FINDING F3 | MEDIUM | src/cart.py:42 | open`; its part, its tag, its title and the rest follow on the next lines. A finding of this review is `open`. A finding a section repeats (`## LOW Findings`, a section's own list) is named there by its `F<n>`, with no second line. Where a reference's shape writes `<#>` or "numbered with the review's others", that is the `F<n>`.
- **The numbers** run through one chain: the code review and every final-check round. A new finding takes the next number after the highest `F<n>` anywhere in `PREVIOUS REVIEW`; an earlier finding still open keeps its own. A number is never reused. With no `PREVIOUS REVIEW` in your prompt, return a failure to the orchestrator naming it; never start the chain again at `F1`.
- **Every ID in PREVIOUS REVIEW** — each of its `FINDING` lines (on the first round, the code review's, fixed by Step 4c, which appended its `Findings Addressed`) and each line of its own `## Earlier Findings` — is listed in an `## Earlier Findings` section before `## Findings`, by its ID and new state on a line of its own — `F3 | fixed` or `F3 | open` — and then its evidence, so every ID of the chain stays in each round and none is reused: for an ID already `fixed` there, `already fixed — <PREVIOUS REVIEW's file name>`; for `fixed`, the change or the code that fixed it, and the test that now fails without the fix (for a security finding, the mutation line of that test); for `open`, what still fails. Check each one in the code as it is now; the fixer's word closes nothing. A finding still `open` is a finding of this review again, under its own number, at its severity, with its `FINDING` line — a code-review LOW included, which stays listed, not fixed.

## A later round (only when your prompt gives `SNAPSHOT`)

After a fix round your prompt gives `SNAPSHOT` (the working tree before the fix) and `FIXED` (as the fix left it), with `PREVIOUS REVIEW` (the final-check review the fix answered). If it gives only some of the three, or git cannot diff the two commits, run every part in full and say why in one line at the top of the document; never take a snapshot yourself.

- **The change** is `git diff --name-only --no-renames SNAPSHOT FIXED -- . ':(exclude,literal)SDD_ROOT'`, and `git diff SNAPSHOT FIXED -- <file>` for a file.
- **Part 1** checks the earlier findings first, then looks for new paths in the change and in the code it reaches; a rule whose code the fix did not touch is listed as `unchanged since PREVIOUS REVIEW`.
- **Part 3** runs T1 and T2 over the change, and T3 and T4's reading half over the tests the fix added or changed.
- **Parts 2 and 4 run in full.** For the lens, *the code the scope changed* stays everything changed since `BASE`.

## The review document and the marker

Write `SDD/.records/reviews/FINAL-CHECK-FEATURE-[feature-name]-iter<k>-[YYYYMMDD].md` containing, in order: a `Reviewed by:` line; `## Earlier Findings`; `## Security Verification`; `## Test Integrity`; `## Tracing Lens` and `## Eval Check` when their gates are on; `## State Check` when the spec has `### State model`; one `## Findings` list holding every finding of every part, each opening with its `FINDING` line; `## LOW Findings (listed, not fixed)` — one line per LOW, `F<n> <title>`, or `None.`; and `## Decision: [APPROVED/REJECTED]`.

**A review with no open HIGH and no open MEDIUM is APPROVED.** A LOW finding is listed, not fixed: the owner sees it in the end report.

**A review with no finding** — no `FINDING` line in the document (the `F<n> | fixed` lines of `## Earlier Findings` are not `FINDING` lines) — writes the whole line `No findings.` under `## Findings`, on a line of its own and outside any fenced block: that line is how the defect ledger (`scripts/ledger.py`) knows a clean review from a malformed one, and refuses a review that has neither.

When the document is written, append to `SDD/.records/progress.md` exactly `## Review FEATURE iter <k> - APPROVED | REJECTED (<h> HIGH, <m> MEDIUM, <l> LOW)` — all three counts, zeros included (`k` = the `ITER` in your prompt; with no `ITER`, return a failure rather than guess one). It is a phase-detection marker; do not paraphrase it.

Bounded return: ≤200 words — the decision, the three counts, the document path, and with `tracing: on` the trace-tree path.
