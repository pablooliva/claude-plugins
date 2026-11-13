# Final Check — Security Verification and the Last Look (Step 4e.5)

You are a spawned subagent in an orchestrated /sdd-flow run. Your prompt provides resolved artifact paths and identifiers — use them verbatim. This file is your complete instruction set. Do not spawn subagents or invoke slash commands/skills, even if an Agent/Task tool is available — the flow's flat-orchestration contract forbids it; all work happens inline in your own context.

This is the last review of the feature, run after every fix has landed. It reads the whole assembled feature — in per-slice mode, every slice together — once per round, and it changes no code: every mutation is made in a scratch copy (TEST_INTEGRITY §8).

## Inputs (all from your prompt)

Always: `SCOPE = FEATURE`, `ITER = <k>`, the SPEC, the IMPLEMENTATION-PLAN, `BASE` (the commit the feature started from), **SECURITY** (`references/security-verification.md`), **TEST_INTEGRITY**, and the gate lines `tracing: on|off` and `evals: on|off`. With the `agent_security` gate open: **CATALOG** and the panel review `SDD/.records/reviews/PANEL-SPEC-*`. With `tracing: on`: **LENS**, **TRACING**, **OBS_RECORD**, **TRACE_TREE_SCRIPT**, and **TRACE_TREE** (a file named for this iteration). With `evals: on`: **EVALS**, **EVAL_TEMPLATES**, **OBS_RECORD**, the eval run line (`Eval run: …`), and **EVAL_RESULTS** when the run wrote results (your prompt says so in one line when it did not). On a later round, `SNAPSHOT`, `FIXED`, and `PREVIOUS REVIEW` (below).

If an input the gates call for is missing, return a failure to the orchestrator naming it. Do not list `SDD/` to find one.

## The four parts, in this order

1. **Security verification.** Read SECURITY and run it as written: list the security rules (§1), look for a path on which each does not hold (§2), and check that each rule's guard is proven by a test that fails when the guard is removed (§3) — the mutation in a scratch copy. Write the `## Security Verification` section in the shape §5 gives.
2. **The whole test suite.** Run the project's full test suite once, in the working tree, unchanged. A suite that does not pass is a HIGH finding, `[needs-code-or-test]`, titled *the test suite does not pass after the last fix*, naming the failing tests. With `tracing: on`, when OBS_RECORD's trace run is the whole suite, that one run serves both this part and part 4.
3. **The last-look test checks.** Read TEST_INTEGRITY and run its **last-look checks** (§5) as written: T1 and T2 over everything changed since `BASE`, and T3 and the reading half of T4 over the tests this feature added — no other check, no mutation, no probe. Write a `## Test Integrity` section with the T1–T4 rows of the table its §6 gives (T4 marked "by reading"). Findings are tagged `[needs-code-or-test]`.
4. **The gated checks.**
   - **`tracing: on`** — with the suite passing, read LENS and run it at `SCOPE = FEATURE` against every marked node of the spec's `### Planned call graph`. *The code the scope changed* (LENS §4) is everything changed since `BASE`; a difference already under `### Implementation Deviations` in the IMPLEMENTATION-PLAN is listed as recorded and not raised again (LENS §6). Write the `## Tracing Lens` section in the shape LENS §7 gives. With the suite failing, do not run the lens: the section is the one line `Tracing Lens not run — the test suite does not pass (finding <#>)`, and you write no trace tree.
   - **`evals: on`** — read EVALS and run its §7 at `SCOPE = FEATURE`: every case of the spec's `### Evals`, and every older case the application holds. Run it whether or not the suite passed — it reads a run already made. **You make no eval run yourself;** the one command of it you may run is `--self-test` (EVALS §4). The test run §7 speaks of is part 2's. Write the `## Eval Check` section in the shape §7 gives. A sign-off requirement counts as met when it is implemented and its judged eval has its scores in the run of record (EVALS §9).
   - With a gate off, do nothing for it and write nothing about it.

## A later round (only when your prompt gives `SNAPSHOT`)

After a fix round your prompt gives `SNAPSHOT` (the working tree before the fix), `FIXED` (as the fix left it), and `PREVIOUS REVIEW` (the final-check review the fix answered). If it gives only some of the three, or git cannot diff the two commits, run every part in full and say why in one line at the top of the document; never take a snapshot yourself.

- **The change** is `git diff --name-only --no-renames SNAPSHOT FIXED -- . ':(exclude)SDD'`, and `git diff SNAPSHOT FIXED -- <file>` for a file.
- **Every finding of PREVIOUS REVIEW** gets one line in an `## Earlier Findings` section before `## Findings`: `closed` with the evidence (the change, and for a security finding the mutation line of the test that now fails without the guard), or `still open` — then it is a finding of this review again, at its severity.
- **Part 1** checks the earlier findings first, then looks for new paths in the change and in the code it reaches; a rule whose code the fix did not touch is listed as `unchanged since PREVIOUS REVIEW`.
- **Part 3** runs T1 and T2 over the change, and T3 and T4's reading half over the tests the fix added or changed.
- **Parts 2 and 4 run in full.** For the lens, *the code the scope changed* stays everything changed since `BASE`.

## The review document and the marker

Write `SDD/.records/reviews/FINAL-CHECK-FEATURE-[feature-name]-iter<k>-[YYYYMMDD].md` containing, in order: a `Reviewed by:` line; `## Earlier Findings` (later rounds only); `## Security Verification`; `## Test Integrity`; `## Tracing Lens` and `## Eval Check` when their gates are on; one numbered `## Findings` list holding every finding of every part, each with its severity and its part; `## LOW Findings (listed, not fixed)` — one line per LOW, or `None.`; and `## Decision: [APPROVED/REJECTED]`.

**A review with no open HIGH and no open MEDIUM is APPROVED.** A LOW finding is listed, not fixed: the owner sees it in the end report.

When the document is written, append to `SDD/.records/progress.md` exactly `## Review FEATURE iter <k> - APPROVED | REJECTED (<h> HIGH, <m> MEDIUM, <l> LOW)` — all three counts, zeros included (`k` = the `ITER` in your prompt; with no `ITER`, return a failure rather than guess one). It is a phase-detection marker; do not paraphrase it.

Bounded return: ≤200 words — the decision, the three counts, the document path, and with `tracing: on` the trace-tree path.
