# Evals — checking what the model really answered

The one definition of evals in `sdd-flow`: what an eval is, how its cases are written, what the application holds for them, what the eval run does, what its results mean, how a review checks them, and how a person accepts what no rule can check. Every body and phase chapter that deals with evals reads this file and never restates it. The path reaches them as **EVALS** in their prompt. The templates it speaks of are in `templates/evals/` beside this folder — Python only, so far.

It applies to a cycle whose `evals` gate is on. With the gate off none of it happens, and nothing here is read.

**Why this exists.** A test asks whether the code does the right thing with the model's answer. It gets that answer from a stand-in, because a test must be fast, free, and the same every time. So no test ever sees what the model really says — and "the summary is faithful to the source" or "the assistant leads the student to the result instead of stating it" is a requirement about exactly that. An eval puts a written example to the application for real and checks what comes back. It is slower than a test, it costs a model call, and it can come out differently twice running. Everything below follows from those three facts.

---

## 1. Two kinds

| Kind | What decides | What it can do |
|---|---|---|
| **hard** | A rule applied to the output: a phrase is there, a phrase is not there, a pattern matches, a field is present, a refusal was given, a named tool was chosen | **Blocks.** A hard eval that fails is a failing test |
| **judged** | A second model call — the judge — scores the output against a rubric, from 0 to 1 | **Informs.** It never blocks, and it never makes a requirement met |

A judged score is a measurement that moves. The same output can be scored differently by two calls to the judge, and the application can answer the same input well once and badly the next time. A gate on a number like that is a gate on noise, so no judged score is ever compared with a threshold.

**A requirement about what the model says is met in one of two ways:**

- **At least one hard eval checks it**, or
- **it is a sign-off requirement:** the spec lists it under `### Manual Verification` as accepted by the user at the commit checkpoint, and a judged eval gives that person scores and real outputs to read. The person's answer is what meets it. §9 has the rules.

A requirement covered by a judged eval alone, and not listed there, is not covered.

**Prefer hard.** Before making a requirement judged, ask what a rule could check: a label that must appear, a result that must not be stated, a field, a language, a length. Often part of a requirement is a rule and the rest is judgement — write a hard eval for the part and a judged one for the rest.

## 2. Cases

A case is one input and what must be true of the output. The cases are written **in the spec, at planning time** (`### Evals` under `## Validation Strategy`), and reviewed with the spec before any code exists. An implementer that wrote its own cases would write the ones its code passes.

- **An eval has an ID, `EVAL-XXX`, names the one requirement it checks, and has numbered cases.** A case is cited as `EVAL-003 case 2`.
- **An eval's ID is used once in an application, not once in a spec.** Every feature's cases go into the same `evals/cases.jsonl` (§3), and the eval run refuses a file that lists a case twice. A spec numbers its evals on from the highest `EVAL-` number already in that file; with no file yet, from `EVAL-001`.
- **The input is an invented example, written out in full.** Never text taken from a real user.
- **A hard case says what the output must contain or must not contain,** in words a rule can apply: "contains `312`", "does not contain `12 hours`", "is JSON with a `title` field". "Is correct" is not a case.
- **Choose an input whose right output cannot be reached without the behaviour.** A fact the model knows anyway does not show that it read the material; a made-up fact does.
- **A judged case has a rubric that says what the best, a middling, and the worst output look like.** The judge scores 1 to 5 against it; the run reports that as 0 to 1.
- **Few cases, each one earning its place.** Every case is run three times at every review (§4), and a judged case costs two model calls each time.

**A behaviour the model shows only some of the time fails a hard case, and that is the point.** A hard case passes only when its check holds on every one of its runs. If the application leads the student to the result five times in seven and states it the other two, the case fails most reviews — correctly: the requirement is not met. The answer is to make the behaviour dependable or to change what is promised, never to loosen the check until it stops catching it.

## 3. What the application holds

| File | What it is | Written by |
|---|---|---|
| `evals/run.py` | The eval run. Rendered from `run.py.template`; the same in every application, and not edited afterwards | the first slice with an eval |
| `evals/task.py` | How one case's input becomes one output of this application, and how the judge model is called. From `task.py.template` | the first slice with an eval; later slices extend it |
| `evals/cases.jsonl` | The spec's cases in the form the run reads: one case per line | each slice adds the cases on its `Evals:` line |
| `evals/checks.py` | Checks that need code. Only when a case has one | the slice whose case needs it |
| a test in the application's test directory | The cases and checks tested against their own examples, with no model call. From `test_eval_checks.py.template` — a `unittest.TestCase`, so `unittest` and `pytest` both collect it | the first slice with an eval |
| the `Eval command` row of `SDD/OBSERVABILITY.md` | The command that makes the eval run in this application | the first slice with an eval |

Nothing of this exists before a slice needs it. `/observability-init` writes none of it.

### Setting it up — once, by the first work that builds an eval

The implementer whose work is the first to carry a case — the first slice with one on its `Evals:` line; in whole-feature mode, the first chunk — renders the templates at **EVAL_TEMPLATES**`/python/`. Templates exist for Python only: in an application in another language, build nothing and return that to the orchestrator as a failure.

| Template | Becomes | Fill in |
|---|---|---|
| `run.py.template` | `evals/run.py` | `@@ROOT@@` — a Python expression for the repository root, written from `HERE`, the `evals/` directory: `HERE.parent`. `@@ENV_FILE@@` — an expression for the env file `SDD/OBSERVABILITY.md` names (`ROOT / ".env"`), or `None` when the application has none. `@@EVAL_COMMAND@@` — the eval command, in the three places it stands |
| `task.py.template` | `evals/task.py` | `@@IMPORTS@@`, `@@MODELS@@`, `@@ANSWER@@`, `@@JUDGE@@` — by the three rules of *The task*, below |
| `test_eval_checks.py.template` | one test file in the application's test directory | `@@ROOT@@` — an expression for the repository root, written from that file (`Path(__file__).resolve().parent.parent`); `@@EVAL_COMMAND@@` |

- **`evals/run.py` is the template with its three placeholders filled, and nothing else.** A review compares the two. What an application needs to do differently goes into `evals/task.py` or `evals/checks.py`.
- **The eval command** is `evals/run.py` run the way this application runs Python, typed from the repository root — `uv run python evals/run.py`, `python evals/run.py`. The trace run's command in `SDD/OBSERVABILITY.md` shows which. Write it into that file's `Eval command` row: the one line of the observability record that a subagent of the flow writes.
- Later work adds cases, and extends `evals/task.py` when a case needs an input the task cannot take yet. It renders nothing again.

### The task

`evals/task.py` is the only place the eval run touches the application. Three rules:

1. **The model call is real**, and it goes through the application's own code. `answer()` calls the function the entry point calls — or the entry point itself, in process — so the prompt, the settings, and the handling of the reply are the application's. It never rebuilds the request to the model itself: an eval of a copy of the prompt says nothing about the application.
2. **An answer the application gives on purpose is an output.** A refusal the application returns in place of the model's answer is returned like any other output, as text that names it, so a case can require it.
3. **No answer is not a failed case.** When the model cannot be reached — no network, a rejected key, a rate limit, a timeout — `answer()` raises `Unavailable` with one of five fixed reasons: `model unreachable`, `key rejected`, `rate limited`, `timed out`, `not set up`. The run then stops with no result (§4). A run in which every case "failed" because the model was down would otherwise read as a broken feature. Only those five are ever printed; any other text is reported as `another reason`, because what an exception says can hold an address or a key.

`evals/run.py` puts the repository root on the import path before it loads the task, so the task imports the application as the application's own code does.

`judge()` makes one call to the judge model. The judge is the application's own model unless a setting names another; `models()` gives both names, and the results document says so in bold when a model graded its own output. A different model is the better judge, for the reason a review is run on a different model than the one that wrote the code.

### A case in the file

```json
{"eval": "EVAL-003", "case": 1, "kind": "hard", "requirement": "REQ-012", "input": {"material": "…", "question": "…"},
 "check": {"contains": ["312"], "lacks": ["ZEBRA-7741"]},
 "known_bad": ["ZEBRA-7741", "The river is long."], "known_good": ["The river is 312 km long."]}
{"eval": "EVAL-004", "case": 1, "kind": "judged", "requirement": "REQ-014", "input": {"material": "…", "question": "…"},
 "rubric": "5: no final result, clear steps, a question back. 3: steps, but the result is given. 1: only the result."}
```

`input` is whatever `answer()` takes. A hard case's `check` holds when all of its parts hold:

| Part | Holds when |
|---|---|
| `contains` | every phrase in the list is in the output, whatever its capitals |
| `lacks` | no phrase in the list is in the output, whatever its capitals |
| `matches` | every regular expression in the list is found in the output, as written |
| `fn` | the function of that name in `evals/checks.py`, called with the output and the case, returns true (or `(True, …)`; with false it may give a reason of a few words). A function that raises on a real output has not been satisfied by it: that run fails |

An output that is not text — a tool call, a parsed object — is checked as JSON text with its keys sorted; an `fn` check gets the value itself.

**Every hard case carries at least one `known_bad` and one `known_good` answer:** an output the check must reject, and one it must accept. They are what proves the check can tell the two apart, in both directions. Without the first, a check that passes everything looks sound; without the second, a check that rejects everything a real model would say looks strict. Write the known-good answer the way the model would plausibly phrase it — with the extra sentence, the different order, the unit spelled out — not as the bare phrase the check looks for.

## 4. The eval run

One command, recorded in `SDD/OBSERVABILITY.md`. In order:

1. **It tests the cases and checks against their own examples, and calls no model if they are not sound.** A malformed case, a hard case with no examples, a check that accepts a known-bad answer or rejects a known-good one — each is named, and the run ends there. The same test runs with the application's ordinary tests, so an unsound check is a red test long before a review.
2. **It runs every case three times.** A hard case **passed** when its check held on all three; otherwise it failed as `unsteady` (it held on one or two) or `never passed`. The two are different faults: one is behaviour that is not dependable, the other behaviour that is not there. A judged case gets a score on each run, shown lowest first.
3. **It writes the results** to the path given with `--out`: a document, and beside it a `.json` file with every output of every run. (`--out` itself may not end in `.json` or `.part`: the run writes those names.) An older result at that path is removed first, so a result is always from the run that names it — and a run made again for the same review replaces the first one's files.
4. **Its last printed line starts with `Result:`**, and its exit status says which kind:

| Exit | `Result:` | Meaning |
|---|---|---|
| 0 | `PASS — hard: n of n case(s) passed all 3 runs; judged: …` | Every hard case passed. Judged scores are in the document |
| 1 | `FAIL — hard: m of n …` | A hard case failed. The document shows each failed run's output |
| 2 | `UNAVAILABLE — the model could not be reached (…)` | No result. Nothing is known about the feature; the fault is in the surroundings |
| 2 | `UNSOUND — …` | No result. The cases, the checks, `evals/task.py`, or the command's arguments cannot be used as they are |
| 2 | `BROKEN — the eval run itself failed (…)` | No result. The run stopped on something it did not expect, or could not write its results |

Exit 1 means one thing only: a hard case failed. Every other way of not finishing is exit 2, and leaves no results file at the path — not an older one, and not half of a new one. Where a file at the path cannot be removed, the run says so in its `Result:` line and, when the file is an older result, calls no model.

**The results document** has the `Result:` line, the models used, one row per case, every run of every judged case in full — score, the judge's sentence, the output — and the output of each failed run of a hard case. The judged part is what the person at the commit checkpoint reads.

**A secret never reaches the results.** Before anything is stored, sent, or printed, the run replaces every value of a secret-named setting — a name containing `KEY`, `TOKEN`, `SECRET`, `PASSWORD`, or `CREDENTIAL`, as the tracing standard defines it — and of a tracing header with `[redacted: <the setting's name>]`. That covers the outputs (text, numbers, and the keys and values of an object), what the judge is given to grade, the judge's sentences, the requirement text, the cases as they are sent, and the experiment and dataset names. It does not cover what the application itself prints while it runs: that is the application's own logging, under the application's own rules. A hard case's check has already run on the real output by then, so its verdict is never changed by it. The judge grades the output with the value replaced: a secret is not handed to a second model for the sake of a score. A value is replaced as it is, and as JSON text, a quoted phrase, or a regular expression for it spells it — a quote, a backslash, or a dot in it is written differently there. This is a net for accidents — a model that repeats a key, a case pasted with one in it — not a barrier against someone hiding a value: one that is transformed, split, or encoded some other way is not recognised. The `Result:` line says how many were replaced: in the outputs, in what the run says about them — a failed check's reason, the judge's sentence — and in the cases themselves, whether or not the run is sent anywhere. What the judge is given is replaced too and not counted a second time. Any number above zero is a defect to raise whatever the cases say: the application put a secret into an answer, or a case in the repository holds one. Values shorter than eight characters are left alone: they are too likely to be an ordinary word of an output.

**The eval run is not part of the ordinary tests and not part of the trace run.** It calls a model, so it runs only where this file says it does. It writes no span file.

**Who makes which run.**

- **The implementer and every fixer make their own**, to see their work pass before they hand it over: without `--experiment`, and with `--out` naming a file outside the repository — in the system's temporary directory — so nothing of it is left behind. Make it when the eval files are complete, and again after a change that can change what the model says: a prompt, the code around the call, a case, a check. Not after every edit — each run is real calls to a model. **At most three runs in one piece of work, each given ten minutes.** A run still going after ten minutes is stopped, counts as one of the three, and is reported as what it is — no result, the run did not finish — never as a pass or a failed case. When a hard case still fails after the third, stop changing things: hand the work over as it is, and say in your return which cases fail and what the last `Result:` line was. The review raises it, and the loop it belongs to is bounded. The command with `--self-test` calls no model; use it freely.
- **The run a review reads — the run of record — is made by the flow's main session**, immediately before that review, with `--experiment` and `--dataset` (§5), writing to the path the review is then given. A reviewer never makes it. A review may run on a second model, in a place from which no model can be reached, and a run made there would report `UNAVAILABLE` and remove the results it was meant to read. A reviewer may run the command with `--self-test`.
- **When the run of record ends `UNAVAILABLE` twice in a row, nothing is reviewed.** The flow makes the run once more before it gives up. After the second, no review can say anything about what the model answers, and no fixer can repair a network: the flow stops and asks the user to make the model reachable (`## Awaiting Eval Run`).

**Never report an eval run you did not make,** and never one made before the last edit.

## 5. Sending a run to Opik

A run is sent when it is given `--experiment <name> --dataset <name>`, and only the run a review reads is given them. So Opik holds one experiment per review, and none for an implementer's or a fixer's own runs.

- **What is sent:** the cases as a dataset (input, check or rubric — a case keeps one dataset item from run to run), every run's output as a trace, and its result as a score named `hard` (1 or 0) or `judged` (0 to 1).
- **Where:** the address in `EVAL_OPIK_URL`, or else the Opik address the application's tracing already uses. The traces go to a project of their own — `EVAL_OPIK_PROJECT`, or else the tracing project's name with `-evals` added, or else `evals` — so they never mix with traces of real use.
- **The tracing headers go only to the server they were written for.** They are sent with the upload when it goes to the same server the application's tracing goes to — same scheme, host, and port — and never to any other address. A redirect is refused and reported as a failed upload, for the same reason.
- **A failed upload changes nothing.** The `Result:` line ends `upload: sent`, `upload: FAILED (<step>: <status>)`, or `upload: not asked for`. The exit status and the results files are the same either way: the files in the repository are the record, and Opik is where runs are compared.
- **Evals go to Opik only.** An application whose tracing goes elsewhere sets `EVAL_OPIK_URL`, or its uploads fail and are reported as failed.

## 6. What binds the cases and the checks

A hard eval is a test, and `references/test-integrity.md` §1 binds it as it binds any other, with one difference: the model is not replaced by a stand-in, because the model is what is being checked.

- **The expected outcome comes from the spec's case.** A check is never written by running the application and requiring whatever it said.
- **A failing case is never weakened.** No removing it, no loosening its check, no changing its input to one the application handles, no moving a requirement from hard to judged. When the spec really changes, the case changes with it and the change is recorded under `### Test Changes` in the IMPLEMENTATION-PLAN, citing the requirement.
- **The application is never taught the cases.** No branch on a case's input, no instruction to the model that names one.
- **Evals are not controls** under `references/enforcement-sites.md`: an eval has no enforcement site, and nothing here is counted or mutated. A requirement that is a control keeps its sites and its mutations whether or not an eval also checks it.

## 7. The review's eval check

Run by the per-slice review (`bodies/slice-review.md`), the whole-feature code review (`bodies/code-review.md`), and every verification of the final check (that same body in `MODE: site-verification-only`, at `FEATURE`), each at the scope its prompt gives, when the prompt carries the line `evals: on`. With `evals: off`, or no such line, do not run it: write the one line `Eval check skipped — evals: off` in the review and move on (a verification of the final check writes nothing about evals then).

It checks what no test checks: that the run of record says what it must, and that the cases and checks in the application are the spec's and can tell a good answer from a bad one. It is not a second look at whether the spec's cases are the right ones — the spec review settled that, and here the spec's cases are the reference.

### Inputs — all from your prompt

| Name | What it is |
|---|---|
| `SCOPE` | `SLICE-XXX` or `FEATURE` |
| the SPEC | holds `### Evals`, the `Sign-off:` lines under `### Manual Verification`, and, in per-slice mode, each slice's `Evals:` line |
| **EVALS** | this file |
| **EVAL_TEMPLATES** | the directory `evals/run.py` was rendered from |
| **OBS_RECORD** | the application's observability record, `SDD/OBSERVABILITY.md`: its `Eval command` row |
| the eval run line | `Eval run: ` followed by the last line the run of record printed, or by `not made — …` with the reason |
| **EVAL_RESULTS** | the results document of the run of record, with a `.json` file of the same name beside it. Given only when the run wrote one; your prompt says so in one line when it did not |
| `BASE` | the commit the work under review started from |

If the gate line says `on` and EVALS, the eval run line, or the SPEC is missing from your prompt, return a failure to the orchestrator naming it. Do not look for a substitute, and **never run the eval command yourself** except with `--self-test` (§4, *Who makes which run*).

### The cases in scope

Two groups of cases are in scope, and "a case in scope" below means a case of either.

- **This spec's cases.** At `SLICE-XXX`: the cases on this slice's `Evals:` line and on those of every slice before it — an earlier slice's case that fails now is this slice's finding, because this slice broke it. At `FEATURE`: every case of `### Evals`. A case of a later slice is not in scope and not missing.
- **Older cases.** `evals/cases.jsonl` may hold cases an earlier feature built: their IDs are not in this spec's `### Evals`, and they were in the file at `BASE`. Every run puts them to the application too, and this work can break or weaken them like any other.
- **A case removed with good reason is in neither group.** Settle this first, before anything is counted as missing: for every case that was in the file at `BASE` and is not there now, look for its line under `### Test Changes` and check it as step 3 says. A removal that passes — the cited requirement of this spec really ends what the case promised — takes the case out of scope: it need not be in the file, in the results, or in any run. A removal that does not pass leaves the case in scope, where it is finding 5 and, being absent, finding 2.

**What differs for an older case:** it cannot be compared with this spec, which does not state it. So the comparison with the spec in step 3, the whole of step 4, and findings 4, 6, 13, and 14 are about this spec's cases alone. Everything else below holds for an older case exactly as for one of this spec's: it has a row in the results, a hard one passed, a judged one has its scores, it was not removed or made easier since `BASE`, the task goes through the application for it, and the application was not taught it. Whether an older case was the right one to write was another review's question and is not asked again.

**Nothing in scope** needs both of these to be true, and only then is the whole check the line `Eval check: no eval in scope.`, with nothing below applying:

1. **This spec has no case in scope** — every `Evals:` line so far says `none`, or `### Evals` is the single line that no requirement is about what the model says.
2. **There is no older case in scope** — `evals/cases.jsonl` holds none now, and it held none at `BASE` or every one it held was removed with good reason. Look at the file as it was at `BASE` to know: cases that were there and are gone without a removal that passes — the file, the directory, or the command row emptied — are still in scope. Each is finding 5, and the run that was not made for them is finding 1.

### What to check

1. **The run was made.** With a case in scope, the eval run line reads `Eval run: Result: PASS …` or `Eval run: Result: FAIL …` and EVAL_RESULTS is in your prompt. Anything else is finding 1, and you go on with what can be checked without results (steps 3, 5, 6, 7).
2. **Every case in scope ran, and every hard one passed.** Each has a row in the results document — this spec's and the older ones alike. A hard case with any verdict but `passed` is finding 3; say which fault it is, `unsteady` or `never passed`, and where the results show the failed output. A judged case needs a score on every one of its runs — the results document counts a run the judge gave no readable score for as unscored, and the `.json` file shows which. A missing score is finding 11; a score is never a finding, whatever it is.
3. **The cases in the file are the spec's, and none was weakened.** Read `evals/cases.jsonl` beside `### Evals`. For each of this spec's cases in scope: the input is the spec's; a hard case's check asks everything the spec's "must contain" and "must not contain" ask, and where the check is an `fn`, the function in `evals/checks.py` computes what the spec says it computes; a judged case's rubric is the spec's rubric, with nothing softened or left out; the requirement and the kind are the spec's. Then compare `evals/cases.jsonl` and `evals/checks.py` with `BASE`, for every case that was there — this spec's and the older ones alike: a case removed, or changed so that it is easier to pass — another input, a check that asks less than it did, a function in `evals/checks.py` that now accepts what it rejected, a rubric made easier — needs a line under `### Test Changes` in the IMPLEMENTATION-PLAN that cites the requirement (§6). **Open the requirement that line cites, in this spec, and confirm that it changes what the case promised** — that the old behaviour is no longer required, or is required differently. A line that cites a requirement which does not say so is no line: the citation is checked, not counted. A coded check can be loosened with its case's line left untouched, so read the functions' changes and not only the cases'.
4. **The checks can tell good from bad** (this spec's cases). Read each hard case's outputs in the `.json` file against the part of its requirement that its eval checks — the `Behaviour checked` cell of its row in the spec's table. An output the check passed that breaks that part is finding 6. A fault in another part of the requirement is not: another eval has that part, and where that eval is judged, its score is never a finding. Then read the case's examples: the known-good ones are phrased as a model would phrase them, and the known-bad ones include the wrong answer a model is most likely to give.
5. **The task goes through the application.** Read `evals/task.py`: `answer()` calls the function the entry point calls, or the entry point itself; it builds no request to the model of its own, puts no stand-in in the model's place, and raises `Unavailable` — with one of the five reasons — when the model could not be reached, instead of returning text.
6. **The application was not taught the cases.** Search the application's code and prompts — everything outside `evals/` and the tests — for the distinctive phrases of each case's input and expected output.
7. **The pieces are in place.** `evals/run.py` is its template with the three placeholders filled: every other line is a line of `EVAL_TEMPLATES/python/run.py.template`. The test rendered from `test_eval_checks.py.template` is in the application's test directory and passed in the test run you made for this review. The `Eval command` row of OBS_RECORD holds the command.
8. **No secret was replaced.** The eval run line says how many values were replaced; any number above zero is finding 10 (§4).

### Findings — the whole list

| # | Finding | Severity |
|---|---|---|
| 1 | A case is in scope and there is no result: the run of record was not made because no eval command is recorded, or it ended `UNSOUND` or `BROKEN`, or printed no `Result:` line | HIGH |
| 2 | A case in scope is not in `evals/cases.jsonl`, or has no row in the results | HIGH |
| 3 | A hard case in scope failed, as `unsteady` or as `never passed` | HIGH |
| 4 | One of this spec's cases is not, in the file, the case the spec states: another input, a check that asks less than the spec's case asks, another rubric, another requirement, or another kind | HIGH |
| 5 | Since `BASE` a case was removed, or made easier to pass — its input changed, its check loosened in `evals/cases.jsonl` or in the function it names in `evals/checks.py`, or its rubric made easier — with no `### Test Changes` line — or with one whose cited requirement does not change what the case promised | HIGH |
| 6 | The check passed an output that breaks the part of the requirement its eval checks | HIGH |
| 7 | `evals/task.py` does not go through the application's own code, replaces the model, or turns an unreachable model into an answer | HIGH |
| 8 | The application was taught a case: a branch on a case's input, or an instruction to the model that names one | HIGH |
| 9 | `evals/run.py` differs from its template in more than the three placeholders | HIGH |
| 10 | The eval run line counts one or more replaced secrets | HIGH |
| 11 | A judged case in scope has a run with no score — the person who accepts its requirement would be reading less than the run was meant to give | HIGH |
| 12 | The test of the cases and checks against their own examples is not among the application's ordinary tests, or does not pass | HIGH |
| 13 | A hard case's examples prove little: a known-good answer that is only the phrase the check looks for, or known-bad answers that leave out the likeliest wrong answer | MEDIUM |
| 14 | A case was added to `evals/cases.jsonl` since `BASE` that the spec does not have | MEDIUM |
| 15 | The `Eval command` row of OBS_RECORD is empty or is not the command | MEDIUM |

Nothing else is an eval finding. In particular: a judged score, however low; a model that graded its own output (the results say so; copy it into the review); a failed upload; a case of a later slice that is not built yet; a sign-off requirement the user has not accepted yet (§9).

### What goes in the review document

A `## Eval Check` section:

```markdown
## Eval Check

**Eval run:** <the eval run line, verbatim>
**Results:** <EVAL_RESULTS path, or `none`>
**Scope:** <SLICE-XXX | FEATURE> — <n> hard case(s), <n> judged case(s)

| Case | Kind | Requirement | In the run | In the file as the spec states it |
|------|------|-------------|------------|-----------------------------------|
| EVAL-001 case 1 | hard | REQ-004 | passed, 3 of 3 | yes |
| EVAL-002 case 1 | hard | REQ-005 | FAILED — unsteady, 2 of 3 | yes |
| EVAL-003 case 1 | judged | REQ-005 (sign-off) | 0.50, 0.75, 1.00 | yes |

**Judge:** <the judge model as the results name it> — <the application's own model | another model>

[Each finding, numbered with the review's other findings: severity, its number in the table above, the case or file, and the fix.]
```

Eval findings are ordinary review findings: they count in the review's verdict and its progress marker like any other, and a HIGH rejects.

## 8. How an eval finding is resolved

- **By changing the application** — its prompt, the code around the model call — or by building what is missing: a case, a check, an example, the task.
- **Never by weakening a case** (§6), and never by editing the spec's `### Evals`, an `Evals:` line, a `Sign-off:` line, or its `evals:` field.
- **There is no recording it instead.** A hard case that cannot be made to pass is a requirement the application does not meet. The fix loop's cap brings that to the user, who decides whether the behaviour is made dependable or the promise changed (§2) — the slice's loop for a finding of a slice review, the final check's loop for a finding of the whole-feature code review or of a final verification.
- **A fix is checked by a new run of record, never by the fixer's own.** In a slice, that is the run made before the re-review; for the whole feature, the run made before each verification of the final check. Until a review has read that run, the finding is open.
- **The fixer makes its own run before it returns** (§4, *Who makes which run*) — at most three, like an implementer — and leaves the test of the cases and checks passing. A hard case it could not bring to pass goes back in its return, named, with the last `Result:` line; it is never reported as fixed.

## 9. Sign-off — what a person accepts

A sign-off requirement (§1) is one the spec lists under `### Manual Verification` with a line that starts `- [ ] **Sign-off: <ID>**` and names the judged eval that informs it. The flow finds these lines by that start.

- **Until it is accepted, it counts as done when three things are true:** it is implemented; every case of its judged eval ran in the run of record and has a score on every run; and those scores and the outputs are in the results. A review counts it as met and the completion step as `Complete` on those three, and both say that its acceptance is still to come. That nobody has accepted it yet is never a finding, in any part of a review.
- **One person accepts it, in one place: whoever answers the commit checkpoint.** With a sign-off requirement in the spec that checkpoint is shown in both modes — a run that is otherwise unattended stops there too. It shows each sign-off requirement with the scores of its judged cases, lowest first, and the path to the results, where every run's output and the judge's sentence are. Yes commits the work and accepts every requirement listed, and the flow records it: `## Sign-off - <IDs> accepted at 4h`. No commits nothing and accepts nothing.
- **Nothing else accepts it.** Not a score, however high; not a review; not a subagent; not a run that finished with nobody there. And no score refuses it: a low score is shown, never acted on (§1).
- **No subagent edits the line or ticks its box.** The record of the acceptance is the flow's line and the commit that follows it.
- **The scores a person is shown are those of the last run of record** — the final check's. Nothing is run after the commit checkpoint: what is changed after it is not scored unless the person runs the eval command themselves.
- **In per-slice mode the slices are committed before that point.** Each pause between slices shows the last line of that slice's run of record — the judged cases built so far and their lowest score — and the path to its results, so a poor answer can be read while the slice is small. The pause accepts nothing.
