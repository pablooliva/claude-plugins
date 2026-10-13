# Evals — checking what the model really answered

The one definition of evals in `sdd-flow`: what an eval is, how its cases are written, what the application holds for them, what the eval run does, and what its results mean. Every body and phase chapter that deals with evals reads this file and never restates it. The path reaches them as **EVALS** in their prompt. The templates it speaks of are in `templates/evals/` beside this folder — Python only, so far.

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
- **it is a sign-off requirement:** the spec lists it under `### Manual Verification` as accepted by the user at the commit checkpoint, and a judged eval gives that person scores and real outputs to read. The person's answer is what meets it.

A requirement covered by a judged eval alone, and not listed there, is not covered.

**Prefer hard.** Before making a requirement judged, ask what a rule could check: a label that must appear, a result that must not be stated, a field, a language, a length. Often part of a requirement is a rule and the rest is judgement — write a hard eval for the part and a judged one for the rest.

## 2. Cases

A case is one input and what must be true of the output. The cases are written **in the spec, at planning time** (`### Evals` under `## Validation Strategy`), and reviewed with the spec before any code exists. An implementer that wrote its own cases would write the ones its code passes.

- **An eval has an ID, `EVAL-XXX`, names the one requirement it checks, and has numbered cases.** A case is cited as `EVAL-003 case 2`.
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
| a test in the application's test directory | The cases and checks tested against their own examples, with no model call. From `test_eval_checks.py.template` | the first slice with an eval |
| the `Eval command` row of `SDD/OBSERVABILITY.md` | The command that makes the eval run in this application | the first slice with an eval |

Nothing of this exists before a slice needs it. `/observability-init` writes none of it.

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
3. **It writes the results** to the path given with `--out`: a document, and beside it a `.json` file with every output of every run. (`--out` itself may not end in `.json` or `.part`: the run writes those names.) An older result at that path is removed first, so a result is always from the run that names it.
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

**A secret never reaches the results.** Before anything is stored, sent, or printed, the run replaces every value of a secret-named setting — a name containing `KEY`, `TOKEN`, `SECRET`, `PASSWORD`, or `CREDENTIAL`, as the tracing standard defines it — and of a tracing header with `[redacted: <the setting's name>]`. That covers the outputs (text, numbers, and the keys and values of an object), the judge's sentences, the requirement text, the cases as they are sent, and the experiment and dataset names. It does not cover what the application itself prints while it runs: that is the application's own logging, under the application's own rules. The checks have already run on the real output by then, so a verdict is never changed by it. The `Result:` line says how many were replaced. Any number above zero is a defect to raise whatever the cases say: the application put a secret into an answer, or a case in the repository holds one. Values shorter than eight characters are left alone: they are too likely to be an ordinary word of an output.

**The eval run is not part of the ordinary tests and not part of the trace run.** It calls a model, so it runs only where this file says it does. It writes no span file.

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
