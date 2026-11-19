# Implementation inputs — Step 4, both delivery modes

Read this with the Step 4 chapter in use — `phases/implementation-whole-feature.md` (4a), `phases/implementation-per-slice.md`, or `phases/end-of-feature.md` (4b–4j). It holds what every Step 4 spawn is passed and the rules every review and fix follows.

All paths below are resolved absolute. SECURITY, SPEC_READING, HOSTILE_INPUT, FIT, TEST_INTEGRITY, TRACE_TREE_SCRIPT, LENS, EVALS and EVAL_TEMPLATES ship inside this skill; one that is missing is a broken install — halt and tell the user. **The fix rounds** — 4c, the 4e.5 fix, and per-slice 4c — run one body, `bodies/fix-round.md`, which holds every rule a fix follows; a fix prompt passes it by path with `MODE` (`feature`, `final-check`, `slice`), `MARKER` (the `progress.md` line it appends, or `none`), and the inputs its chapter lists, and embeds no rule of the fix's own — only the Safety-Net Rule every spawn carries.

**SECURITY** = `SKILL_ROOT/references/security-verification.md`, passed to every implementation spawn, the final check (4e.5) and its fix, and the completion spawn.

**SPEC_READING** = `SKILL_ROOT/references/spec-reading.md` — how an implementer reads the SPEC: by section and by id, never the whole file in one Read, with the sections that carry security rules, the state model, deviations and deferrals always read. No gate: passed to every implementation spawn — the per-slice scaffold (4a), each slice's implement step (4a), and the whole-feature implementer and each of its chunks — and to every fix spawn. When the work is split into chunks, the prompt names each chunk's REQ, EDGE and FAIL ids (SPEC_READING §3).

**HOSTILE_INPUT** = `SKILL_ROOT/references/hostile-input.md` — the rules for code that reads input it does not control (how it splits and matches text, treats a failed command, a link, an exception, an error message, a write) and how they are tested. No gate: passed to every spawn that writes code — each slice's implement step (4a), the whole-feature implementer and each of its chunks, and every fix spawn (the fix body's rule 3).

**LOW findings are listed, not fixed.** A review with no open HIGH and no open MEDIUM passes; its LOW findings are listed in its document and reach the owner at the slice pause and in the end report. The fix body holds the rule (`bodies/fix-round.md`, rule 1).

**FIT** = `SKILL_ROOT/references/fit-lens.md` — the reviews' Fit Lens. No gate: passed in every cycle to the code review and the slice review (4b) and every fix spawn.

**SDD_ROOT** = the folder that holds this cycle's records, **relative to the repository root** (the one path here that is not absolute), by the rule `scripts/growth.py` uses: when BRIEF sits in a `requirements/` folder, the folder above that — `SDD` for `SDD/requirements/DESIGN-[###]-[feature-name].md`, `flow-state/SDD` for a repo that keeps its records there; otherwise `SDD`. A root that is the repository root itself or lies outside it is a broken layout: halt and tell the user. No gate: passed with `BASE` to the code review and the slice review (4b), the final check (4e.5), and every fix spawn. They leave it out of every changed-file list and line count (`':(exclude,literal)SDD_ROOT'`); a records folder that is not the repo-root `SDD/` would otherwise be reviewed as code, and a repo-root `SDD/` that is not the cycle's would be hidden.

**STATE_MODEL** = `SKILL_ROOT/references/state-model.md` — a feature's state model and the reviews' State Check. No gate — the spec decides: passed in every cycle to every implementation spawn, the code review and the slice review (4b), the final check (4e.5), and every fix spawn. A spec with no `### State model` has none, and each of them does nothing for it. With one, the fix body's rule 4 applies.

**The two gates.** The tracing gate and the evals gate are the `tracing:` and `evals:` parts of the latest `## Gates - ` line after the latest `Planning Phase - COMPLETE` in `progress.md` (`phases/planning.md` → 3c); a part that is missing, or a cycle with no such line, is `off`. Every implementation, code-review, final-check (4e.5), fix, and completion spawn of Step 4 is passed each gate as a line: `tracing: on|off`, `evals: on|off`. With a gate off, none of its inputs below is passed and the bodies do nothing about it.

**Tracing inputs** (`tracing: on`; the completion spawn gets OBS_RECORD and the final TRACE_TREE only — it runs nothing):

- **TRACING** — the tracing standard, resolved at Step 0.
- **OBS_RECORD** — `SDD/OBSERVABILITY.md`, the application's observability record: it names the trace run, the span file it writes, the env file, and the entry-point test.
- **TRACE_TREE_SCRIPT** — `SKILL_ROOT/scripts/trace-tree.py`.
- **LENS** — `SKILL_ROOT/references/tracing-lens.md`, the one definition of the review's Tracing Lens (review and fix spawns).
- **TRACE_TREE** — the file a review writes the rendered call tree to: `SDD/.records/reviews/TRACE-TREE-FEATURE-[feature-name]-[YYYYMMDD].md` for the 4b review, and `SDD/.records/reviews/TRACE-TREE-FEATURE-[feature-name]-iter<k>-[YYYYMMDD].md` for the final check of iteration `k` — one file per review, so a later review never overwrites the tree an earlier one judged. A fix spawn is given the tree written by the review it answers **only when that file exists** once the review has returned (the orchestrator checks the path; it never opens the review to find out). A review writes no tree when it ran no lens (4e, after the critical review, in per-slice mode), when its trace run failed or could not be rendered, or when the test suite did not pass at the final check; the fix spawn is then given no TRACE_TREE and told so in one line, and works from the failure message in the review's finding. A continuation of that fix spawn is given the same. The completion spawn is given the tree of the last final check.

**With tracing on**, the fix body's rule 5 applies.

**Evals inputs** (`evals: on`; the completion spawn gets EVALS and the last final check's eval run line and EVAL_RESULTS only — it runs nothing):

- **EVALS** — `SKILL_ROOT/references/evals.md`, the one definition of evals: the cases, the eval files an application holds, the eval run, the review's eval check (§7), and how a finding is resolved (§8).
- **EVAL_TEMPLATES** — `SKILL_ROOT/templates/evals/`, the files an application's eval run is rendered from.
- **OBS_RECORD** — `SDD/OBSERVABILITY.md`, passed whether or not tracing is on: it names the env file and holds the `Eval command` row.
- **The eval run line and EVAL_RESULTS** — to review spawns, and to the fix spawn that answers a review: what *The eval run of record* below produced for that review. The final check (4e.5) counts as a review here, and its fix as the fix that answers it.

**With evals on**, the fix body's rule 6 applies.

**The eval run of record (evals on only).** A review judges what the model answers from one run of the application's eval command, made by the **orchestrator** itself immediately before it starts the review — every time it starts one, including a re-review after a fix round and a review started again by a resumed session. The reviews that read one: the per-slice review, the feature code review (4b, both delivery modes), and every review of the final check (4e.5). A second attempt at the same review in the same session — the second-model route's retry, its fallback to the Claude route, a continuation after a handoff — is not a new review and is given the run already made. No subagent makes the run: a review on a second model may run where no model can be reached (`references/evals.md` §4). In order:

1. **Find the command.** Read the `Eval command` row of OBS_RECORD — that one row, nothing else of the file. An empty or `—` row means the application holds no eval case yet: make no run; the eval run line is `Eval run: not made — no eval command is recorded`; go to step 4 (the review says whether a case should exist by now). A row with a command means cases exist, and the run is made — also for a slice whose own `Evals:` line is `none`, and when every case was built by an earlier feature: the gate is on because this feature has a model in it, which is when an earlier case can stop passing.
2. **Run it** from the repository root, allowing it ten minutes:

   ```
   <the eval command> --out <EVAL_RESULTS> --experiment "[feature-name] <SCOPE> iter <k>" --dataset "[feature-name]"
   ```

   **EVAL_RESULTS** = `SDD/.records/reviews/EVAL-RESULTS-<SCOPE>-[feature-name]-iter<k>-[YYYYMMDD].md` — `<SCOPE>` and `<k>` being those of the review about to start (`FEATURE` and `0` at 4b; `FEATURE` and the loop's `k` at 4e.5). The run writes a `.json` of the same name beside it and replaces whatever an earlier run left at that path. Read only the last line it prints, which starts `Result:`; never open the results — they hold what the model answered, and reading them is the review's work.
3. **Act on how it ended:**
   - **Exit 0 (`PASS`) or 1 (`FAIL`)** — there is a result. The eval run line is `Eval run: <that last line>`, and EVAL_RESULTS is passed. A `FAIL` is not acted on here: the review turns it into findings.
   - **Exit 2 with `Result: UNAVAILABLE`** — the model could not be reached. Run once more. If it ends the same way, nothing can be reviewed: append the halt block below to `progress.md`, show it, and stop.
   - **Anything else** — exit 2 with `UNSOUND` or `BROKEN`, another exit status, a run past its ten minutes, or no `Result:` line — there is no result, and it is the implementation's to repair. The eval run line is `Eval run: <the last line printed>`, or `Eval run: the command ended with status <n> and printed no Result line`; no EVAL_RESULTS is passed, and the prompt says so in one line. The review raises it.
4. **Record it.** Append one line to `progress.md`: `## Eval Run <SCOPE> iter <k> - <what follows `Eval run: ` in the eval run line>`. When that line ends `upload: FAILED (…)`, append beneath it: `Warning: the eval run was not sent to Opik — <that part of the line>`. A failed upload changes nothing else and never stops the flow: the results in the repository are the record.
5. **Start the review,** passing the eval run line and — when step 3 says so — EVAL_RESULTS. A fix spawn that answers this review is passed the same two.

```markdown
## Awaiting Eval Run

Eval run of record for <SCOPE> iter <k> could not be made: <the Result line>
The model this application calls could not be reached, twice. Nothing has been reviewed.
Make it reachable — the network, the key, the provider's limit — then run `/sdd-flow continue`.
```

`/sdd-flow continue` — or the user's reply in the same session — makes the run again for the scope and iteration the block names and carries on from step 3 (`phases/rare/resume.md` → `## Awaiting Eval Run`). The block has no other way out: a review is never started without the run it reads, and the gate is not switched off for a cycle under way.

**Test integrity inputs.** **TEST_INTEGRITY** = `SKILL_ROOT/references/test-integrity.md` — the one definition of a real test and of the reviews' Test Integrity Lens. No gate: passed in every cycle to every implementation spawn (4a, each chunk; per-slice 4a), the code review and the slice review (4b), and every fix spawn. The final check (4e.5) is passed it too, with the IMPLEMENTATION-PLAN path and `BASE`, for its last-look checks and the scratch copy its mutations are made in. The fix body's rule 2 holds it: it sends the fixer to the SPEC to decide whether a test may change, and to the plan to record it.
