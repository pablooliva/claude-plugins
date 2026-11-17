# Loop engineering — where the plugin stands, and where it is going

How the plugin's pieces fit the four feedback loops in Josh Wulf's *Agentic Loop Engineering*
(<https://camunda.github.io/agentic-engineering-explainers/loops.html>; owner's note: *What Everyone Gets Wrong about
Loop Engineering - Josh Wulf*). The goal is all four loops, measured, in every application built with `sdd-flow` or
`sdd-lite`. This page says what exists, what the defect ledger adds (feature 002, in progress), and what is missing.
Update it when a piece in the tables below ships or changes.

## The model in brief

A loop is an **implementer** (the agent), an **implementation** (the code), and an **evaluator** that measures it and
signals back. Nobody writes the loop; it exists because of how the parts are connected. Four loops, each slower and
more costly than the one inside it:

| Loop | Evaluator | Time |
|---|---|---|
| Local | Types and compiler, unit tests, linters | Seconds |
| CI | Full suite, module-boundary rules, builds — on every push | Minutes |
| Integration | After merge, the system with its real neighbours, real scenarios | Hours |
| Production | Users, monitoring, bug reports, telemetry | Days |

Two kinds of feedback: **fix the code** (a failing check → the agent changes the code; many times a minute) and
**fix the loops** (an escaped defect, a slow run → a better check, or a check in an earlier loop; engineers). The
score is the **defect escape rate**: the share of defects that reach users, each labelled with the loop that should
have caught it.

## What the plugin has today

| Loop | What exists | Where |
|---|---|---|
| Local | The implementer writes and runs tests per requirement; a test must fail without the code it proves (mutation in a scratch copy); each state move and each security rule gets a test | `sdd-flow/references/test-integrity.md`, `state-model.md`, `security-verification.md` |
| Local (review) | Slice review, code review and final check, run by a second model family (Codex) — they gate the commit, so they sit in the local loop's place, but they are minutes long and judgement-based | `sdd-flow/references/second-model-review.md`; `sdd-lite` runs one Codex review |
| CI | Nothing in the plugin. `currents` has no CI and no pre-commit hook | — |
| Integration | Evals put written cases to the running application, for features with a model in them; a trace run checks what ran against what was planned | `sdd-flow/references/evals.md`, `tracing-lens.md`; `observability-init` |
| Production | Tracing into Opik and a trace lookup; answers marked wrong in Opik become eval cases | `observability-init`, `eval-harvest` |
| Fix the loops | `/retro` proposes a check, review standard or tool from one cycle's evidence; the owner picks | `retro` |

The loop rules Wulf names, and where they hold:

- **The evaluator is independent** — reviews on a different model family; a test is real only if it fails without
  its code; a failing eval case is fixed in the application, never by weakening the case; a review cannot change code.
- **The signal says which way** — every finding names a file and line and a severity.
- **No convergence: cap the rounds and escalate** — fix loops stop after two rounds and go to the owner.
- **Measuring the wrong thing** — the Test Integrity Lens and the final check's last look at the tests.

## What the defect ledger adds (feature 002)

The scoreboard — the piece the plugin lacked for **fixing the loops**. Design:
`flow-state/SDD/requirements/DESIGN-002-defect-ledger.md`; proposal: `proposals/feedback-loop-2026-11-16.md`.

- **A committed record per application** (`SDD/defects.jsonl`): every HIGH or MEDIUM defect, the loop that caught it,
  its class, the commit that introduced it, and the check its fix added.
- **Each application declares the loops it has** (`SDD/defects-setup.json`). A loop is counted from the day it is
  declared, so "no CI" is never reported as "CI caught nothing".
- **Escapes are labelled** — a bug fix of shipped work names the loop that missed it and the earliest check that can
  catch its class (*fix the bug, then fix the loops*).
- **Seen before** — a repeat of a class whose earlier fix added a check asks for a check in an earlier loop.
- **A monthly report-only task**: per application, the share each loop caught (escape rate), repeated classes, checks
  with no catches since added, open escapes.

Evidence it is worth having: in `currents`, 22 of 49 fix commits over three months were escapes, and 6 more were
test-suite defects found only after merge (`proposals/feedback-loop-kill-test-2026-11-16.md`).

## What is missing, loop by loop

| Loop | Missing | First step |
|---|---|---|
| Local | Checks the agent cannot skip: a `Stop` / `TaskCompleted` hook that runs the tests and fails with exit 2; a lint and type standard the flow requires; running only the tests a change can reach | A hook per application; `/retro` proposes lint rules from repeated classes |
| CI | CI in every application; a red CI result sent back to an implementing agent | eduKate (decided, separate work); `currents` next — its 6 test-suite escapes are what CI catches |
| Integration | A declared integration loop per application: a scenario suite run after merge or against staging. Today only evals (model features) and one-off rehearsals | Declare it in `SDD/defects-setup.json` where one exists; formalise the rehearsals that caught 5 `currents` defects |
| Production | Bug reports and monitoring feeding the ledger without a person; telemetry pointed at the agent | `user` lines through `/defect-ledger log`; later, an application's health checks writing lines |
| Fix the loops | Moving checks inward from the report; loop speed and cost measured; ledgers read across applications | Ledger Tier 3; measure each loop's time before tuning it |

## Order

1. **Measure** — the defect ledger and the monthly report (feature 002). Tuning needs the score first.
2. **CI** — eduKate, then each application the report shows escaping test-suite defects.
3. **Local guarantees** — hooks that exit 2, and lint or type rules for the classes that repeat.
4. **Integration** — a declared, repeatable integration loop per application.
5. **Production** — monitoring and bug reports that reach the ledger and the agent on their own.

Tracked in BB task CLAUDEPLUG-18.
