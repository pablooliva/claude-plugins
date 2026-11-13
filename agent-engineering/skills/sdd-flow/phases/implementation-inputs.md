# Implementation inputs — Step 4, both delivery modes

Read this with the Step 4 chapter in use — `phases/implementation-whole-feature.md` (4a), `phases/implementation-per-slice.md`, or `phases/end-of-feature.md` (4b–4j). It holds what every Step 4 spawn is passed and the rules every review and fix follows.

**SECURITY** = `SKILL_ROOT/references/security-verification.md`, resolved absolute, passed to every implementation spawn, the final check (4e.5) and its fix, and the completion spawn.

**LOW findings are listed, not fixed.** A review with no open HIGH and no open MEDIUM passes; its LOW findings are listed in its document and reach the owner at the slice pause and in the end report. **Embed this rule verbatim in every fix prompt (4c, the 4e.5 fix, per-slice 4c):**

> **Scope of the fix.** Fix every HIGH and MEDIUM finding of the review you answer. Leave its LOW findings as they are — they are listed for the owner, not fixed. Fix a fit finding by removing or merging code — reuse the existing helper, fold the file into the module it belongs to, drop the layer — never by adding code (FIT §4). Give your round's net line change in your return, counted as FIT §4 says.

**FIT** = `SKILL_ROOT/references/fit-lens.md`, resolved absolute — the reviews' Fit Lens. No gate: it is passed in every cycle to the code review and the slice review (4b) and every fix spawn (4c, the 4e.5 fix, per-slice 4c). A missing file is a broken install — halt and tell the user.

**Tracing inputs.** The tracing gate is the `tracing:` part of the latest `## Gates - ` line after the latest `Planning Phase - COMPLETE` in `progress.md` (`phases/planning.md` → 3c); a cycle with no such line has it `off`. Every implementation, code-review, final-check (4e.5), fix, and completion spawn of Step 4 is passed the gate as the line `tracing: on` or `tracing: off`. With `tracing: on` it is also passed these, resolved absolute (the completion spawn: OBS_RECORD and the final TRACE_TREE only — it runs nothing):

- **TRACING** — the tracing standard, resolved at Step 0.
- **OBS_RECORD** — `SDD/OBSERVABILITY.md`, the application's observability record: it names the trace run, the span file it writes, the env file, and the entry-point test.
- **TRACE_TREE_SCRIPT** — `SKILL_ROOT/scripts/trace-tree.py`.
- **LENS** — `SKILL_ROOT/references/tracing-lens.md`, the one definition of the review's Tracing Lens (review and fix spawns).
- **TRACE_TREE** — the file a review writes the rendered call tree to: `SDD/.records/reviews/TRACE-TREE-FEATURE-[feature-name]-[YYYYMMDD].md` for the 4b review, and `SDD/.records/reviews/TRACE-TREE-FEATURE-[feature-name]-iter<k>-[YYYYMMDD].md` for the final check of iteration `k` — one file per review, so the tree a review judged is never overwritten by a later one. A fix spawn is given the tree written by the review it answers — **only when that file exists** once the review has returned (the orchestrator checks the path; it never opens the review to find out). A review writes no tree when it ran no lens (4e, after the critical review, in per-slice mode), when its trace run failed or could not be rendered, or when the test suite did not pass at the final check; the fix spawn is then given no TRACE_TREE and told so in one line, and the review's finding carries the failure message it works from. A continuation of that fix spawn is given the same. The completion spawn is given the tree of the last final check.

With `tracing: off` none of the five is passed and the bodies do nothing about tracing. TRACE_TREE_SCRIPT and LENS ship inside this skill; one that is missing is a broken install — halt and tell the user. **With the gate on, embed this fix rule verbatim in every fix prompt (4c, the 4e.5 fix, per-slice 4c):**

> **Tracing.** Leave the entry-point test passing and the trace run completing. Resolve a Tracing Lens finding as LENS §6 says: change the code or the tests; a MEDIUM difference between the plan and the trace may instead be recorded, with its reason, under `### Implementation Deviations` in the IMPLEMENTATION-PLAN; a HIGH is always fixed. Never edit the spec's `### Planned call graph`, a `Traced nodes:` line, or its `tracing:` field. Add no span the tracing standard does not require.

**Evals inputs.** The evals gate is the `evals:` part of the latest `## Gates - ` line after the latest `Planning Phase - COMPLETE` in `progress.md` (`phases/planning.md` → 3c); a line with no `evals:` part, or a cycle with no such line, has it `off`. Every implementation, code-review, final-check (4e.5), fix, and completion spawn of Step 4 is passed the gate as the line `evals: on` or `evals: off`. With `evals: on` it is also passed these, resolved absolute (the completion spawn: EVALS, and the final eval run line and EVAL_RESULTS only — it runs nothing):

- **EVALS** — `SKILL_ROOT/references/evals.md`, the one definition of evals: the cases, the eval files an application holds, the eval run, the review's eval check (§7), and how a finding is resolved (§8).
- **EVAL_TEMPLATES** — `SKILL_ROOT/templates/evals/`, the files an application's eval run is rendered from.
- **OBS_RECORD** — `SDD/OBSERVABILITY.md`. With evals on it is passed whether or not tracing is: it names the env file and holds the `Eval command` row.
- **The eval run line and EVAL_RESULTS** — review spawns, and the fix spawn that answers a review: what *The eval run of record* below produced for that review. The final check (4e.5) is a review here, and the 4e.5 fix is the fix that answers it. The completion spawn is given those of the last final check.

With `evals: off` none of them is passed and the bodies do nothing about evals. EVALS and EVAL_TEMPLATES ship inside this skill; one that is missing is a broken install — halt and tell the user. **With the gate on, embed this fix rule verbatim in every fix prompt (4c, the 4e.5 fix, per-slice 4c):**

> **Evals.** Leave the test of the eval cases and checks passing, and every hard case built so far passing all its runs: make your own eval run before you return, as EVALS §4 says — no `--experiment`, `--out` a file outside the repository, at most three runs — and give its last `Result:` line in your return, naming any hard case that still fails. Resolve an eval finding as EVALS §8 says: change the application, or build what is missing. Never weaken a case — no removing it, loosening its check, changing its input to one the application handles, or turning a hard eval into a judged one — and never teach the application a case's input. Never edit the spec's `### Evals`, an `Evals:` line, a `Sign-off:` line, or its `evals:` field.

**The eval run of record (gate on only).** A review judges what the model answers from one run of the application's eval command, and the **orchestrator** makes that run itself, immediately before it starts the review — every time it starts one, a re-review after a fix round and a review started again by a resumed session included. The reviews that read one are the per-slice review, the feature code review (4b, both delivery modes), and every review of the final check (4e.5). A second attempt at the same review in the same session is not a new review and is given the run already made: the second-model route's retry, its fallback to the Claude route, and a continuation after a handoff. No subagent makes it: a review on a second model may run where no model can be reached (`references/evals.md` §4). In order:

1. **Find the command.** Read the `Eval command` row of OBS_RECORD — that one row, nothing else of the file. A row that is empty or `—` means the application holds no eval case yet: make no run, and the eval run line is `Eval run: not made — no eval command is recorded`. Go to step 4; the review says whether a case should have been built by now. A row that holds a command means cases exist, and the run is made — also for a slice whose own `Evals:` line is `none`, and also when every case in the application was built by an earlier feature. The gate is on because this feature has a model in it, and that is when a case built earlier can stop passing; the review reads the run for exactly that.
2. **Run it** from the repository root, allowing it ten minutes:

   ```
   <the eval command> --out <EVAL_RESULTS> --experiment "[feature-name] <SCOPE> iter <k>" --dataset "[feature-name]"
   ```

   **EVAL_RESULTS** = `SDD/.records/reviews/EVAL-RESULTS-<SCOPE>-[feature-name]-iter<k>-[YYYYMMDD].md` — `<SCOPE>` and `<k>` being the scope and iteration of the review about to start (`FEATURE` and `0` at 4b here; `FEATURE` and the loop's `k` at 4e.5). The run writes a `.json` file of the same name beside it, and removes whatever an earlier run left at that path: a run made again for the same review replaces the first. Read only the last line it prints, which starts `Result:`; never open the results — they hold what the model answered, and reading them is the review's work.
3. **Act on how it ended:**
   - **Exit 0 (`PASS`) or 1 (`FAIL`)** — there is a result. The eval run line is `Eval run: <that last line>`, and EVAL_RESULTS is passed. A `FAIL` is not acted on here: the review turns it into findings.
   - **Exit 2 with `Result: UNAVAILABLE`** — the model could not be reached. Run the command once more. If it ends the same way, nothing can be reviewed: append the halt block below to `progress.md`, show it, and stop.
   - **Anything else** — exit 2 with `UNSOUND` or `BROKEN`, another exit status, a run that outlasted its ten minutes, or no `Result:` line — there is no result, and it is the implementation's to repair. The eval run line is `Eval run: <the last line printed>`, or `Eval run: the command ended with status <n> and printed no Result line`; no EVAL_RESULTS is passed, and the prompt says so in one line. The review raises it.
4. **Record it.** Append one line to `progress.md`: `## Eval Run <SCOPE> iter <k> - <what follows `Eval run: ` in the eval run line>`. When that line ends `upload: FAILED (…)`, append one more beneath it: `Warning: the eval run was not sent to Opik — <that part of the line>`. A failed upload changes nothing else and never stops the flow: the results in the repository are the record.
5. **Start the review,** passing the eval run line and — when step 3 says so — EVAL_RESULTS. A fix spawn that answers this review is passed the same two.

```markdown
## Awaiting Eval Run

Eval run of record for <SCOPE> iter <k> could not be made: <the Result line>
The model this application calls could not be reached, twice. Nothing has been reviewed.
Make it reachable — the network, the key, the provider's limit — then run `/sdd-flow continue`.
```

`/sdd-flow continue` — or the user's reply in the same session — makes the run again for the scope and iteration the block names and carries on from step 3 (`phases/rare/resume.md` → `## Awaiting Eval Run`). The block has no other way out: a review is never started without the run it reads, and the gate is not switched off for a cycle that is under way.

**Test integrity inputs.** **TEST_INTEGRITY** = `SKILL_ROOT/references/test-integrity.md`, resolved absolute — the one definition of what a real test is and of the reviews' Test Integrity Lens. It has no gate: it is passed in every cycle to every implementation spawn (4a, each chunk; per-slice 4a), to the code review and the slice review (4b), and to every fix spawn (4c, the 4e.5 fix, per-slice 4c). The final check (4e.5) is passed it too, with the IMPLEMENTATION-PLAN path and `BASE`, for its last-look checks and the scratch copy its mutations are made in. It ships inside this skill; a missing file is a broken install — halt and tell the user. **Embed this fix rule verbatim in every fix prompt, and pass every fix spawn `BASE`, the SPEC, and the IMPLEMENTATION-PLAN path** — the 4e.5 fix included, with tracing on or off: the rule sends the fixer to the SPEC to decide whether a test may change, and to the plan to record it:

> **Tests.** Never make a failing test pass by weakening it — no deleting it, skipping it, loosening its assertion, changing its expected value, or narrowing what the test run collects — unless the SPEC says the behaviour it checked has changed; then add the line TEST_INTEGRITY §1 requires under `### Test Changes` in the IMPLEMENTATION-PLAN. Never make it pass by teaching the code about the test's inputs. Resolve a Test Integrity finding as TEST_INTEGRITY §7 says: make the test real or the code right; restore a weakened test from `BASE`.
