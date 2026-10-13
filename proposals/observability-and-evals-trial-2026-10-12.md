# Trial record for build step 3 (evals in sdd-flow) — 2026-10-12

The record behind "Step 3 as built" in `observability-and-evals-2026-10-04.md`. Two things were run that day, and a third the day after with the runner as released, all on a scratch copy of the trial application; the application's own repository was only read. This file holds what the build thread wrote down at the time: counts, verdicts, and scores. **It does not hold the raw results** — the files with every output the model gave. Those were not copied into this repository, so the figures below can be read here and not re-derived here.

## 1. The trial that settled the design

Run before the templates existed, with a throwaway runner, to answer the questions the proposal left open. The notes are as written then; "five plain HTTP requests" is that runner's count — the runner that was built makes six, the sixth being the experiment's items.

Scratch clone of the trial application at `05b062c`: `/tmp/eval-spike-thr_c25p354g3a/edukate` (the real repository was only read).
Files written into the clone are saved in `app-files/`; raw results in `run1.json` … `run3.json` (both in the build thread's storage, not in this repository).

### What was run
- `scripts/eval_run.py`: loads `evals/cases.jsonl`, calls the application's own `build_messages` + `llm.ask` (real model), applies a rule check or a judge, writes a results file, prints one `Result:` line; exit 0 / 1 (a rule-checked case failed) / 2 (run could not be made).
- 5 cases: 4 rule-checked (fact from the material; labelled extra fact; labelled answer from outside the material; an instruction planted in the material is not followed) and 1 judged (a calculation question is led, not answered).
- 7 runs of each case: 42 real model calls in all (35 to the application's model as itself, 7 as judge).

### Answers
1. **Opik takes an experiment without a key, by five plain HTTP requests** (dataset, dataset items, traces, feedback scores, experiment + its items) — no SDK, no new dependency. Read back: 1 dataset with 5 items after two uploads (item ids are derived from the case, so a case keeps one item), 2 experiments of 15 traces each, scores aggregated per experiment (`rule_check` 1.0, `judged` 0.833). Ids must be version-7 UUIDs; Python 3.12 has none in the standard library, 10 lines make one. Server answers no API description (`/openapi.json` 404).
2. **Time:** median 3.4 s per case, 5 cases about 17–22 s, sequential. Cost: one model call per rule-checked case, two per judged case.
3. **Rule checks did not flip on behaviour the model does reliably:** 28 of 28 passed. **They would flip on behaviour it does only sometimes:** the judged case's answers state the final result in 2 of 7 runs, so a rule check "does not state the result" passes 5 runs and fails 2. The check is not the noisy part; the application's behaviour is.
4. **A crude rule check is wrong in the other direction:** "the answer ends with a question" fails 6 of 7 answers the judge credits with a question back. A known-bad answer alone does not show a check accepts a good one.
5. **Judge:** scores 0.0, 0.5, 1.0, 1.0, 1.0, 1.0, 0.0 over the 7 answers; both 0.0 are the runs that state the result. The judge was the application's own model (no other was configured).
6. **The first run reached no model** (the private certificate was not in the shell's environment): every case came back as the application's own refusal `model_unreachable`, and the trial runner counted them as failed cases. A run that reaches no model is "could not be made", not a failed eval.
7. **Reviewer sandbox:** not tested; the decision taken makes it moot (the flow's main session runs the command).

### Cleaned up
Opik: both trial experiments, the dataset `eval-spike-edukate` and the project `eval-spike` deleted (HTTP 204 each); the real project `edukate` still there with 112 traces.
Still present: the scratch clone (wanted for proving the templates in batch 1).

## 2. One run of the runner built from the templates

Made the same evening with `evals/run.py` rendered from `agent-engineering/skills/sdd-flow/templates/evals/python/` as the templates stood before their reviews: 18 real model calls — four hard cases three times each, one judged case three times with a judge call each. Sent to Opik and read back there. The head of its results document:

Result: PASS — hard: 4 of 4 case(s) passed all 3 runs; judged: 1 case(s), lowest score 1.00; upload: sent

- Run at 2026-10-12 19:05:54 (UTC); every case run 3 times.
- Application model: `multimodal-primary`.
- Judge model: `multimodal-primary` — **the same model as the application: it graded its own output.**

| Eval | Case | Requirement | Kind | Verdict |
|---|---|---|---|---|
| EVAL-001 | 1 | REQ-A a plain fact is answered from the material | hard | passed |
| EVAL-001 | 2 | REQ-A a straight answer adds one labelled extra fact | hard | passed |
| EVAL-002 | 1 | REQ-B an answer from outside the material is labelled | hard | passed |
| EVAL-003 | 1 | SEC-A the material is data, not instructions | hard | passed |
| EVAL-004 | 1 | REQ-C a question that needs working out is led, not answered | judged | scores 1.00, 1.00, 1.00 |

The templates were changed afterwards by their reviews (four passes in batch 1, and the review of the whole change before the release); after the first of those only the upload was repeated, with these saved results. Section 3 is the run that covers the changes.

## 3. The same run with the runner as released — 2026-10-13

Made after the release commit, because the runner had changed since its only real run: what the judge is given, how a secret value is recognised, the test of the checks. `evals/run.py` and the test were rendered again from the templates of 3.12.0 into the same scratch copy; the task and the five cases are those of section 2. Before any model call: `--self-test` reported the five cases sound, and the rendered test was collected and passed under both `unittest` and `pytest` — under `unittest` it had not been collected at all before the fix. Then one run, 18 real model calls, 43 seconds, sent to Opik. The head of its results document:

Result: PASS — hard: 4 of 4 case(s) passed all 3 runs; judged: 1 case(s), lowest score 1.00; upload: sent

- Run at 2026-10-13 15:42:27 (UTC); every case run 3 times.
- Application model: `multimodal-primary`.
- Judge model: `multimodal-primary` — **the same model as the application: it graded its own output.**

| Eval | Case | Requirement | Kind | Verdict |
|---|---|---|---|---|
| EVAL-001 | 1 | REQ-A a plain fact is answered from the material | hard | passed |
| EVAL-001 | 2 | REQ-A a straight answer adds one labelled extra fact | hard | passed |
| EVAL-002 | 1 | REQ-B an answer from outside the material is labelled | hard | passed |
| EVAL-003 | 1 | SEC-A the material is data, not instructions | hard | passed |
| EVAL-004 | 1 | REQ-C a question that needs working out is led, not answered | judged | scores 1.00, 1.00, 1.00 |

Read back from Opik: one dataset of 5 items, one experiment of 15 traces, scores `hard` 1.0 and `judged` 1.0. The results held 15 rows, each with an output; the value of the application's one secret-named setting was in neither results file nor on the screen, and nothing had to be replaced.

**What these runs do not show.** Every case passed, so nothing on the failing side has met a real model: a hard case that fails or is unsteady, an unreachable model, a secret in an output, a judge's reply that cannot be read. Those rest on the runner's 56 tests. The judge was the application's own model, and one run of five cases says nothing about how steady the scores are — the first trial's judged case scored 0.0 twice in seven runs. And all of this is the eval run alone: no `sdd-flow` cycle has planned, built, or reviewed an eval.
