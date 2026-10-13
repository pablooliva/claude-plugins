"""The eval runner template (templates/evals/python/run.py.template), rendered into a throwaway application whose
"model" is a stand-in that answers from the case's own input. No model and no network beyond a loopback socket."""

import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import unittest
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parents[2] / "templates" / "evals" / "python"
FILLS = {
    "@@ROOT@@": "HERE.parent",
    "@@ENV_FILE@@": 'ROOT / "app.env"',
    "@@EVAL_COMMAND@@": "python evals/run.py",
}

# The stand-in application: a case's input says what each run gives back, so a test decides the "model's" behaviour.
TASK = '''
import json
import os
from pathlib import Path

CALLS = Path(__file__).resolve().parent / "calls.txt"
_turn = {}


class Unavailable(Exception):
    pass


def _next(key, replies):
    _turn[key] = _turn.get(key, 0) + 1
    return replies[(_turn[key] - 1) % len(replies)]


def models():
    return {"application": "stand-in", "judge": __JUDGE__}


async def answer(case_input):
    with CALLS.open("a") as handle:
        handle.write("answer\\n")
    reply = _next(json.dumps(case_input, sort_keys=True), case_input["say"])
    if reply.startswith("RAISE-UNAVAILABLE:"):
        raise Unavailable(reply.split(":", 1)[1])
    if reply == "RAISE-CRASH":
        raise ValueError("a secret detail")
    if reply == "RETURN-SET":
        return {"not", "json"}
    if reply == "RAISE-EXIT":
        raise SystemExit(1)
    if reply == "MAKE-BLOCKER":
        Path(case_input["blocker"]).mkdir()
        return "ok"
    if reply == "RETURN-OBJECT":
        return case_input["object"]
    return reply


def judge(system, user):
    with (Path(__file__).resolve().parent / "asked.txt").open("a") as handle:
        handle.write(user + "\\n")
    case_input = json.loads(user.split("\\n\\nINPUT\\n", 1)[1].split("\\n\\nOUTPUT TO GRADE\\n", 1)[0])
    reply = _next("judge" + json.dumps(case_input, sort_keys=True), case_input["judge"])
    return reply.replace("LEAK-HERE", os.environ.get("MY_API_KEY", ""))  # a judge that repeats a secret it knows
'''


def hard(eval_id="EVAL-001", case=1, say=("yes ok",), check=None, bad=("no",), good=("ok",), **extra):
    return {"eval": eval_id, "case": case, "kind": "hard", "requirement": "REQ-001 it says ok",
            "input": {"say": list(say)}, "check": check or {"contains": ["ok"]},
            "known_bad": list(bad), "known_good": list(good), **extra}


def judged(eval_id="EVAL-002", case=1, say=("fine",), replies=('{"score": 5, "reason": "good"}',)):
    return {"eval": eval_id, "case": case, "kind": "judged", "requirement": "REQ-002 it reads well",
            "input": {"say": list(say), "judge": list(replies)}, "rubric": "Reads well."}


class Recorder(BaseHTTPRequestHandler):
    def _take(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        self.server.seen.append((self.command, self.path, json.loads(body or b"null"), dict(self.headers)))
        self.send_response(self.server.answers.get(self.path, 204))
        self.end_headers()

    do_POST = do_PUT = do_GET = _take

    def log_message(self, *arguments):
        pass


class EvalRunner(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        (self.root / "evals").mkdir()
        text = (TEMPLATES / "run.py.template").read_text(encoding="utf-8")
        for placeholder, fill in FILLS.items():
            self.assertIn(placeholder, text)
            text = text.replace(placeholder, fill)
        self.assertNotIn("@@", text, "a placeholder of the template has no fill in this test")
        (self.root / "evals" / "run.py").write_text(text, encoding="utf-8")
        self.task(judge="stand-in")
        self.out = self.root / "reviews" / "EVAL-RESULTS.md"

    def task(self, judge="stand-in"):
        (self.root / "evals" / "task.py").write_text(TASK.replace("__JUDGE__", repr(judge)), encoding="utf-8")

    def cases(self, *cases):
        lines = [case if isinstance(case, str) else json.dumps(case) for case in cases]
        (self.root / "evals" / "cases.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def run_it(self, *arguments, env=None):
        clean = {key: value for key, value in os.environ.items() if not key.startswith(("EVAL_", "OTEL_"))}
        done = subprocess.run([sys.executable, str(self.root / "evals" / "run.py"), *arguments],
                              capture_output=True, text=True, env={**clean, **(env or {})}, cwd=self.root)
        lines = done.stdout.strip().splitlines()
        return done.returncode, (lines[-1] if lines else ""), done

    def calls(self):
        path = self.root / "evals" / "calls.txt"
        return len(path.read_text().splitlines()) if path.exists() else 0

    def results(self):
        return json.loads(self.out.with_suffix(".json").read_text(encoding="utf-8"))

    # ---- a run that passes -------------------------------------------------------------------------------

    def test_every_case_is_run_three_times_and_a_clean_run_passes(self):
        self.cases(hard(), hard("EVAL-001", 2), judged())
        status, result, _ = self.run_it("--out", str(self.out))
        self.assertEqual(status, 0)
        self.assertEqual(result, "Result: PASS — hard: 2 of 2 case(s) passed all 3 runs; judged: 1 case(s), "
                                 "lowest score 1.00; upload: not asked for")
        self.assertEqual(self.calls(), 9)
        data = self.results()
        self.assertEqual(len(data["rows"]), 9)
        self.assertEqual(data["result"], result)
        document = self.out.read_text(encoding="utf-8")
        self.assertIn(result, document)
        self.assertIn("| EVAL-001 | 2 | REQ-001 it says ok | hard | passed |", document)
        self.assertNotIn("## Hard cases that failed", document)

    def test_the_result_line_is_the_last_line_printed(self):
        self.cases(hard())
        _, result, done = self.run_it("--out", str(self.out))
        self.assertTrue(done.stdout.strip().splitlines()[-1].startswith("Result: "))
        self.assertTrue(result.startswith("Result: PASS"))

    def test_an_output_that_is_not_text_is_checked_as_json(self):
        self.cases(hard(check={"contains": ['"tool": "search"']}, bad=[{"tool": "delete"}], good=[{"tool": "search"}]))
        (self.root / "evals" / "task.py").write_text(
            "def models():\n    return {}\n\n\ndef answer(case_input):\n    return {'tool': 'search', 'n': [1, 2]}\n")
        status, result, _ = self.run_it("--out", str(self.out))
        self.assertEqual((status, result[:12]), (0, "Result: PASS"))

    # ---- a hard case that fails ---------------------------------------------------------------------------

    def test_a_hard_case_that_passes_two_runs_of_three_fails_as_unsteady(self):
        self.cases(hard(say=("ok", "nope", "ok")), hard("EVAL-001", 2))
        status, result, _ = self.run_it("--out", str(self.out))
        self.assertEqual(status, 1)
        self.assertTrue(result.startswith("Result: FAIL — hard: 1 of 2 case(s) passed all 3 runs"), result)
        document = self.out.read_text(encoding="utf-8")
        self.assertIn("FAILED — unsteady, 2 of 3 runs passed", document)
        failed = document.split("## Hard cases that failed", 1)[1]
        self.assertIn("**Run 2** — does not contain 'ok'", failed)
        self.assertIn("> nope", failed)
        self.assertNotIn("**Run 1**", failed)

    def test_a_hard_case_that_never_passes_says_so(self):
        self.cases(hard(say=("nope",)))
        status, _, _ = self.run_it("--out", str(self.out))
        self.assertEqual(status, 1)
        self.assertIn("FAILED — never passed", self.out.read_text(encoding="utf-8"))

    def test_a_forbidden_phrase_fails_the_case(self):
        self.cases(hard(say=("ok ZEBRA",), check={"contains": ["ok"], "lacks": ["zebra"]}, bad=["ok zebra", "x"]))
        status, _, _ = self.run_it("--out", str(self.out))
        self.assertEqual(status, 1)
        self.assertIn("contains 'zebra'", self.out.read_text(encoding="utf-8"))

    def test_a_pattern_is_searched_as_written(self):
        self.cases(hard(say=("Total: 42 km",), check={"matches": [r"\b\d+ km\b"]}, bad=["far"], good=["7 km"]))
        self.assertEqual(self.run_it("--out", str(self.out))[0], 0)

    def test_a_check_written_as_a_function_is_called_with_the_output_and_the_case(self):
        (self.root / "evals" / "checks.py").write_text(
            "def short(output, case):\n    return len(output) <= case['input']['limit'], 'too long'\n")
        case = hard(say=("abcdef",), check={"fn": "short"}, bad=["abcdefgh"], good=["abc"])
        case["input"]["limit"] = 5
        self.cases(case)
        status, _, _ = self.run_it("--out", str(self.out))
        self.assertEqual(status, 1)
        self.assertIn("too long", self.out.read_text(encoding="utf-8"))

    def test_a_task_that_breaks_on_a_case_fails_that_case_and_names_only_the_class(self):
        self.cases(hard(say=("RAISE-CRASH",)))
        status, _, _ = self.run_it("--out", str(self.out))
        self.assertEqual(status, 1)
        document = self.out.read_text(encoding="utf-8")
        self.assertIn("the task raised ValueError", document)
        self.assertNotIn("a secret detail", document + self.out.with_suffix(".json").read_text())
        self.assertEqual([row["score"] for row in self.results()["rows"]], [0.0, 0.0, 0.0])

    def test_an_output_that_cannot_be_stored_fails_its_case_and_the_results_are_still_written(self):
        self.cases(hard(say=("RETURN-SET",)))
        status, _, _ = self.run_it("--out", str(self.out))
        self.assertEqual(status, 1)
        self.assertIn("the task raised TypeError", self.out.read_text(encoding="utf-8"))

    def test_a_check_that_breaks_on_a_real_output_fails_that_run(self):
        (self.root / "evals" / "checks.py").write_text(
            "import json\n\n\ndef has_title(output, case):\n    return 'title' in json.loads(output)\n")
        self.cases(hard(say=('{"title": "x"}', "not json at all", '{"title": "y"}'), check={"fn": "has_title"},
                        bad=['{"name": "x"}'], good=['{"title": "x"}']))
        status, _, _ = self.run_it("--out", str(self.out))
        self.assertEqual(status, 1)
        document = self.out.read_text(encoding="utf-8")
        self.assertIn("unsteady, 2 of 3 runs passed", document)
        self.assertIn("**Run 2** — the check raised JSONDecodeError", document)

    # ---- no result ------------------------------------------------------------------------------------------

    def test_an_unreachable_model_is_no_result_and_removes_an_older_one(self):
        self.cases(hard(say=("ok", "RAISE-UNAVAILABLE:rate limited")))
        self.seed_older_result()
        status, result, _ = self.run_it("--out", str(self.out))
        self.assertEqual(status, 2)
        self.assertEqual(result, "Result: UNAVAILABLE — the model could not be reached (rate limited); "
                                 "no result was written")
        self.assertFalse(self.out.exists())
        self.assertFalse(self.out.with_suffix(".json").exists())

    def seed_older_result(self):
        self.out.parent.mkdir(exist_ok=True)
        self.out.write_text("an older run")
        self.out.with_suffix(".json").write_text("{}")

    def test_what_an_unavailable_says_is_never_printed_unless_it_is_one_of_the_fixed_reasons(self):
        self.cases(hard(say=("RAISE-UNAVAILABLE:Authorization Bearer sk-secretABC123 at 10.0.0.1",)))
        status, result, done = self.run_it("--out", str(self.out))
        self.assertEqual(status, 2)
        self.assertEqual(result, "Result: UNAVAILABLE — the model could not be reached (another reason); "
                                 "no result was written")
        self.assertNotIn("secret", (done.stdout + done.stderr).lower())
        self.assertNotIn("10.0.0.1", done.stdout + done.stderr)

    def test_a_secret_that_equals_a_fixed_reason_is_not_printed_either(self):
        self.cases(hard(say=("RAISE-UNAVAILABLE:timed out",)))
        status, result, _ = self.run_it("--out", str(self.out), env={"MY_TOKEN": "timed out"})
        self.assertEqual(status, 2)
        self.assertEqual(result, "Result: UNAVAILABLE — the model could not be reached ([redacted: MY_TOKEN]); "
                                 "no result was written")

    def test_cases_that_are_not_sound_remove_an_older_result(self):
        self.cases(hard(good=("fine",)))
        self.seed_older_result()
        status, result, _ = self.run_it("--out", str(self.out))
        self.assertEqual((status, result[:16]), (2, "Result: UNSOUND "))
        self.assertFalse(self.out.exists())
        self.assertFalse(self.out.with_suffix(".json").exists())

    def test_a_cases_file_that_is_not_text_is_unsound_not_a_failed_eval(self):
        (self.root / "evals" / "cases.jsonl").write_bytes(b"\xff\xfe not utf-8 \xff")
        status, result, done = self.run_it("--out", str(self.out))
        self.assertEqual(status, 2)
        self.assertIn("cases.jsonl cannot be read (UnicodeDecodeError)", done.stdout)
        self.assertTrue(result.startswith("Result: UNSOUND"), result)

    def test_results_that_cannot_be_written_are_no_result_and_leave_nothing_behind(self):
        self.cases(hard())
        blocker = self.root / "reviews"
        blocker.write_text("a file where the folder should be")
        status, result, _ = self.run_it("--out", str(self.out))
        self.assertEqual(status, 2)
        self.assertTrue(result.startswith("Result: BROKEN — the eval run itself failed ("), result)
        self.assertTrue(result.endswith("; no result was written"), result)
        self.assertEqual(sorted(path.name for path in self.root.iterdir() if path.name != "evals"), ["reviews"])

    def test_a_second_file_that_cannot_be_written_takes_the_first_with_it(self):
        self.out.parent.mkdir()
        blocker = self.out.parent / "EVAL-RESULTS.json.part"  # made during the run: the second write then fails
        case = hard(say=("MAKE-BLOCKER", "ok", "ok"))
        case["input"]["blocker"] = str(blocker)
        self.cases(case)
        status, result, _ = self.run_it("--out", str(self.out))
        self.assertEqual(status, 2)
        self.assertTrue(result.startswith("Result: BROKEN — the eval run itself failed ("), result)
        self.assertTrue(result.endswith("1 file(s) at --out could not be removed and are not a result"), result)
        self.assertEqual([path.name for path in self.out.parent.iterdir()], [blocker.name])

    def test_an_older_result_that_cannot_be_removed_stops_the_run_before_any_call(self):
        self.cases(hard())
        self.out.parent.mkdir()
        self.out.with_suffix(".json").mkdir()  # stands for a file the run may not delete
        status, result, _ = self.run_it("--out", str(self.out))
        self.assertEqual(status, 2)
        self.assertTrue(result.startswith("Result: BROKEN — an older result at --out could not be removed"), result)
        self.assertEqual(self.calls(), 0)

    def test_an_application_that_ends_the_process_is_no_result(self):
        self.cases(hard(say=("ok", "RAISE-EXIT")))
        self.seed_older_result()
        status, result, _ = self.run_it("--out", str(self.out))
        self.assertEqual(status, 2)
        self.assertEqual(result, "Result: BROKEN — the eval run itself failed (SystemExit); no result was written")
        self.assertFalse(self.out.exists())

    def test_arguments_that_cannot_be_used_give_a_result_line_and_remove_an_older_result(self):
        self.cases(hard())
        self.seed_older_result()
        status, result, _ = self.run_it("--out", str(self.out), "--experiment", "x")
        self.assertEqual((status, result[:16]), (2, "Result: UNSOUND "))
        self.assertFalse(self.out.exists())
        self.assertFalse(self.out.with_suffix(".json").exists())
        self.seed_older_result()
        status, result, done = self.run_it("--out", str(self.out), "--no-such-option", "sk-sentinel-12345678")
        self.assertEqual(status, 2)
        self.assertEqual(result, "Result: UNSOUND — the arguments cannot be used: see --help; no model was called")
        self.assertNotIn("sentinel", done.stdout + done.stderr)
        self.assertFalse(self.out.exists())
        self.assertFalse(self.out.with_suffix(".json").exists())
        for broken in (("--out", str(self.out), "--experiment"), ("--experiment", "--out=" + str(self.out), "--dataset")):
            self.seed_older_result()  # an option with no value: nothing else of the line can be read
            self.assertEqual(self.run_it(*broken)[0], 2)
            self.assertFalse(self.out.exists(), broken)
            self.assertFalse(self.out.with_suffix(".json").exists(), broken)
        self.out.with_suffix(".json").mkdir()  # an older file that cannot be removed is counted in the result
        _, result, _ = self.run_it("--out", str(self.out), "--no-such-option")
        self.assertTrue(result.endswith("; 1 older file(s) at --out could not be removed and are not a result"), result)
        status, _, done = self.run_it("--help")
        self.assertEqual(status, 0)
        self.assertIn("--self-test", done.stdout)
        self.assertEqual(self.calls(), 0)

    def test_an_out_path_that_ends_in_json_or_part_is_refused_before_any_call(self):
        self.cases(hard())
        for name in ("results.json", "results.md.part"):
            target = self.root / name
            target.write_text("kept")
            status, result, _ = self.run_it("--out", str(target))
            self.assertEqual((status, result[:16]), (2, "Result: UNSOUND "), name)
            self.assertEqual((self.calls(), target.read_text()), (0, "kept"), name)
            self.assertEqual(self.run_it("--out", str(target), "--no-such-option")[0], 2)
            self.assertEqual(target.read_text(), "kept", name)

    def test_the_task_can_import_the_application_from_the_repository_root(self):
        (self.root / "rootapp.py").write_text("def reply():\n    return 'ok from the application'\n")
        (self.root / "evals" / "task.py").write_text(
            "import rootapp\n\n\ndef models():\n    return {'application': 'x', 'judge': 'x'}\n\n\n"
            "def answer(case_input):\n    return rootapp.reply()\n")
        self.cases(hard())
        status, result, _ = self.run_it("--out", str(self.out))
        self.assertEqual((status, result[:12]), (0, "Result: PASS"), result)

    def test_a_check_that_accepts_its_known_bad_answer_stops_the_run_before_any_call(self):
        self.cases(hard(bad=("this is ok too",)))
        status, result, done = self.run_it("--out", str(self.out))
        self.assertEqual(status, 2)
        self.assertTrue(result.startswith("Result: UNSOUND — 1 problem(s)"), result)
        self.assertIn("EVAL-001 case 1: the check accepts known-bad answer 1", done.stdout)
        self.assertEqual(self.calls(), 0)
        self.assertFalse(self.out.exists())

    def test_a_check_that_rejects_its_known_good_answer_is_unsound(self):
        self.cases(hard(good=("fine",)))
        status, _, done = self.run_it("--self-test")
        self.assertEqual(status, 2)
        self.assertIn("the check rejects known-good answer 1 (does not contain 'ok')", done.stdout)

    def test_the_self_test_passes_sound_cases_without_a_call(self):
        self.cases(hard(), judged())
        status, result, _ = self.run_it("--self-test")
        self.assertEqual(status, 0)
        self.assertTrue(result.startswith("Result: SOUND — 2 case(s)"), result)
        self.assertEqual(self.calls(), 0)

    def test_cases_that_cannot_be_used_are_each_named(self):
        no_examples = hard("EVAL-003")
        del no_examples["known_bad"], no_examples["known_good"]
        no_rubric = judged("EVAL-004")
        del no_rubric["rubric"]
        self.cases("not json", hard(), hard(), {**hard("EVAL-005"), "kind": "soft"}, no_examples, no_rubric,
                   hard("EVAL-006", check={"includes": ["ok"]}), hard("EVAL-007", check={"contains": []}),
                   {"eval": "EVAL-8", "case": 1}, hard("EVAL-009", check={"matches": ["("]}),
                   hard("EVAL-010", check={"fn": "absent"}), hard("EVAL-011", case=True))
        status, result, done = self.run_it("--self-test")
        self.assertEqual(status, 2)
        for expected in ("line 1: not JSON", "EVAL-001 case 1: listed twice", 'EVAL-005 case 1: "kind" must be',
                         'EVAL-003 case 1: needs at least one "known_bad" answer',
                         'EVAL-003 case 1: needs at least one "known_good" answer',
                         'EVAL-004 case 1: a judged case needs a "rubric"', 'EVAL-006 case 1: "check" must be an object',
                         'EVAL-007 case 1: "contains" must be a list of non-empty strings',
                         'line 9: needs "eval" like "EVAL-001"', "EVAL-009 case 1: a pattern in",
                         "EVAL-010 case 1: evals/checks.py has no function 'absent'",
                         'line 12: needs "eval" like "EVAL-001" and a whole-number "case"'):
            self.assertIn(expected, done.stdout)

    def test_no_cases_file_and_an_empty_one_are_unsound(self):
        self.assertEqual(self.run_it("--self-test")[0], 2)
        self.cases("")
        status, _, done = self.run_it("--self-test")
        self.assertEqual(status, 2)
        self.assertIn("cases.jsonl holds no case", done.stdout)

    def test_a_missing_or_incomplete_task_is_unsound(self):
        self.cases(hard(), judged())
        task = self.root / "evals" / "task.py"
        task.write_text(TASK.replace("__JUDGE__", "'x'").replace("def judge(", "def judge_gone("))
        status, result, _ = self.run_it("--out", str(self.out))
        self.assertEqual((status, result), (2, "Result: UNSOUND — evals/task.py has no judge; no result was written"))
        task.write_text("import nothing_of_that_name\n")
        status, result, _ = self.run_it("--out", str(self.out))
        self.assertEqual(status, 2)
        self.assertIn("evals/task.py cannot be loaded (ModuleNotFoundError)", result)
        task.unlink()
        self.assertIn("evals/task.py does not exist", self.run_it("--out", str(self.out))[1])

    def test_out_is_required_and_experiment_needs_dataset(self):
        self.cases(hard())
        self.assertEqual(self.run_it()[0], 2)
        self.assertEqual(self.run_it("--out", str(self.out), "--experiment", "x")[0], 2)
        self.assertEqual(self.calls(), 0)

    # ---- judged cases ---------------------------------------------------------------------------------------

    def test_a_judged_case_never_fails_the_run_and_its_scores_are_shown_lowest_first(self):
        self.cases(hard(), judged(replies=('{"score": 5, "reason": "good"}', 'Sure: {"score": 1, "reason": "bad"}',
                                           '{"score": 3, "reason": "so-so"}')))
        status, result, _ = self.run_it("--out", str(self.out))
        self.assertEqual(status, 0)
        self.assertIn("judged: 1 case(s), lowest score 0.00", result)
        document = self.out.read_text(encoding="utf-8")
        self.assertIn("| judged | scores 0.00, 0.50, 1.00 |", document)
        self.assertIn("**Run 2** — score 0.00 — bad", document)
        self.assertIn("> fine", document)

    def test_a_judge_reply_that_cannot_be_read_gives_no_score(self):
        self.cases(judged(replies=("I think it is good", '{"score": 7}', '{"score": true}')))
        status, result, _ = self.run_it("--out", str(self.out))
        self.assertEqual(status, 0)
        self.assertIn("1 without any score", result)
        self.assertIn("| judged | no score |", self.out.read_text(encoding="utf-8"))
        self.assertEqual([row["score"] for row in self.results()["rows"]], [None, None, None])

    def test_the_document_says_when_the_application_model_graded_itself(self):
        self.cases(judged())
        self.run_it("--out", str(self.out))
        self.assertIn("the same model as the application", self.out.read_text(encoding="utf-8"))
        self.task(judge="another-model")
        self.run_it("--out", str(self.out))
        document = self.out.read_text(encoding="utf-8")
        self.assertIn("Judge model: `another-model`.", document)
        self.assertNotIn("the same model as the application", document)

    # ---- the test template ---------------------------------------------------------------------------------

    def test_the_test_template_passes_on_sound_cases_and_fails_on_unsound_ones(self):
        text = (TEMPLATES / "test_eval_checks.py.template").read_text(encoding="utf-8")
        text = text.replace("@@ROOT@@", f"Path({str(self.root)!r})").replace("@@EVAL_COMMAND@@", "python evals/run.py")
        self.assertNotIn("@@", text)
        target = self.root / "test_eval_checks.py"
        target.write_text(text, encoding="utf-8")
        spec = importlib.util.spec_from_file_location("rendered_eval_test", target)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        def collected():  # as the application's test run would find it, not by calling the function
            suite, result = unittest.defaultTestLoader.loadTestsFromModule(module), unittest.TestResult()
            suite.run(result)
            return suite.countTestCases(), len(result.failures), len(result.errors)

        self.cases(hard())
        self.assertEqual(collected(), (1, 0, 0))
        self.cases(hard(bad=("ok",)))
        self.assertEqual(collected(), (1, 1, 0))
        self.assertEqual(self.calls(), 0)

    def test_the_task_template_has_the_three_functions_the_runner_calls(self):
        text = (TEMPLATES / "task.py.template").read_text(encoding="utf-8")
        for placeholder, fill in (("@@IMPORTS@@", ""), ("@@MODELS@@", "return {}"), ("@@ANSWER@@", "return ''"),
                                  ("@@JUDGE@@", "return ''")):
            self.assertIn(placeholder, text)
            text = text.replace(placeholder, fill)
        self.assertNotIn("@@", text)
        scope = {}
        exec(compile(text, "task.py", "exec"), scope)
        self.assertTrue(issubclass(scope["Unavailable"], Exception))
        for name in ("models", "answer", "judge"):
            self.assertTrue(callable(scope[name]))

    # ---- sending the run to Opik ----------------------------------------------------------------------------

    def server(self, answers=None):
        try:
            server = HTTPServer(("127.0.0.1", 0), Recorder)
        except OSError as error:
            self.skipTest(f"no loopback socket here: {type(error).__name__}")
        server.seen, server.answers = [], answers or {}
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(lambda: (server.shutdown(), server.server_close()))
        return server, f"http://127.0.0.1:{server.server_address[1]}/api"

    def test_a_run_with_an_experiment_name_is_sent_in_six_requests(self):
        server, base = self.server()
        self.cases(hard(), judged())
        (self.root / "app.env").write_text(
            f'OTEL_EXPORTER_OTLP_ENDPOINT="{base}/v1/private/otel"\n'
            "OTEL_EXPORTER_OTLP_HEADERS=projectName=my%20app,Comet-Workspace=team\n")
        status, result, _ = self.run_it("--out", str(self.out), "--experiment", "feat SLICE-001 iter 0",
                                        "--dataset", "feat")
        self.assertEqual(status, 0)
        self.assertTrue(result.endswith("; upload: sent"), result)
        self.assertEqual([(method, path) for method, path, _, _ in server.seen], [
            ("POST", "/api/v1/private/datasets"), ("PUT", "/api/v1/private/datasets/items"),
            ("POST", "/api/v1/private/traces/batch"), ("PUT", "/api/v1/private/traces/feedback-scores"),
            ("POST", "/api/v1/private/experiments"), ("POST", "/api/v1/private/experiments/items")])
        dataset, items, traces, scores, experiment, links = (body for _, _, body, _ in server.seen)
        self.assertEqual(dataset, {"name": "feat"})
        self.assertEqual((items["dataset_name"], len(items["items"])), ("feat", 2))
        self.assertNotIn("known_bad", items["items"][0]["data"])
        self.assertEqual(len(traces["traces"]), 6)
        self.assertEqual({trace["project_name"] for trace in traces["traces"]}, {"my app-evals"})
        self.assertEqual(sorted(score["name"] for score in scores["scores"]), ["hard"] * 3 + ["judged"] * 3)
        self.assertEqual((experiment["name"], experiment["dataset_name"]), ("feat SLICE-001 iter 0", "feat"))
        self.assertEqual(len(links["experiment_items"]), 6)
        self.assertEqual({link["experiment_id"] for link in links["experiment_items"]}, {experiment["id"]})
        self.assertEqual({link["dataset_item_id"] for link in links["experiment_items"]},
                         {item["id"] for item in items["items"]})
        self.assertEqual({link["trace_id"] for link in links["experiment_items"]},
                         {trace["id"] for trace in traces["traces"]})
        every_id = ([experiment["id"]] + [item["id"] for item in items["items"]]
                    + [trace["id"] for trace in traces["traces"]] + [link["id"] for link in links["experiment_items"]])
        self.assertEqual({uuid.UUID(value).version for value in every_id}, {7})
        self.assertEqual({uuid.UUID(value).variant for value in every_id}, {uuid.RFC_4122})
        self.assertEqual(len(set(every_id)), len(every_id))
        headers = server.seen[0][3]
        self.assertEqual(headers.get("Comet-Workspace"), "team")
        self.assertNotIn("projectName", headers)

    def test_a_case_keeps_its_dataset_item_from_one_run_to_the_next(self):
        server, base = self.server({"/api/v1/private/datasets": 409})
        self.cases(hard(), hard("EVAL-001", 2))
        env = {"EVAL_OPIK_URL": base, "EVAL_OPIK_PROJECT": "chosen"}
        for name in ("one", "two"):
            status, result, _ = self.run_it("--out", str(self.out), "--experiment", name, "--dataset", "feat", env=env)
            self.assertEqual((status, result.endswith("upload: sent")), (0, True), result)
        first, second = (body for _, path, body, _ in server.seen if path.endswith("/datasets/items"))
        self.assertEqual([item["id"] for item in first["items"]], [item["id"] for item in second["items"]])
        self.assertEqual(len({item["id"] for item in first["items"]}), 2)
        experiments = [body["id"] for _, path, body, _ in server.seen if path.endswith("/experiments")]
        self.assertEqual(len(set(experiments)), 2)
        traces = next(body for _, path, body, _ in server.seen if path.endswith("/traces/batch"))
        self.assertEqual({trace["project_name"] for trace in traces["traces"]}, {"chosen"})

    def kept(self):
        """What a run found, without what may differ between two runs of the same cases: times and the upload note."""
        data = self.results()
        rows = [{key: value for key, value in row.items() if key not in ("start", "end", "seconds")}
                for row in data["rows"]]
        return data["cases"], rows, data["models"], data["result"].split("; upload:")[0]

    def test_a_failed_upload_changes_neither_the_exit_status_nor_the_results(self):
        server, base = self.server({"/api/v1/private/traces/batch": 500})
        for cases, expected in (((hard(), judged()), 0), ((hard(say=("ok", "nope", "ok")), judged()), 1)):
            self.cases(*cases)
            status, _, _ = self.run_it("--out", str(self.out))
            alone = self.kept()
            self.assertEqual(status, expected)
            del server.seen[:]
            status, result, _ = self.run_it("--out", str(self.out), "--experiment", "x", "--dataset", "feat",
                                            env={"EVAL_OPIK_URL": base})
            self.assertEqual(status, expected)
            self.assertTrue(result.endswith("; upload: FAILED (traces: HTTP 500)"), result)
            self.assertIn("upload: FAILED (traces: HTTP 500)", self.out.read_text(encoding="utf-8"))
            self.assertEqual(len(server.seen), 3)
            self.assertEqual(self.kept(), alone)
            self.assertEqual(len(alone[1]), 6)

    def test_a_hard_case_whose_task_broke_is_sent_with_a_score_of_zero(self):
        server, base = self.server()
        self.cases(hard(say=("RAISE-CRASH",)))
        status, _, _ = self.run_it("--out", str(self.out), "--experiment", "x", "--dataset", "feat",
                                   env={"EVAL_OPIK_URL": base})
        self.assertEqual(status, 1)
        scores = next(body for _, path, body, _ in server.seen if path.endswith("/feedback-scores"))
        self.assertEqual([(score["name"], score["value"]) for score in scores["scores"]], [("hard", 0.0)] * 3)

    def test_an_address_given_for_evals_changes_the_address_and_nothing_else(self):
        server, base = self.server()
        self.cases(hard())
        tracing = {"OTEL_EXPORTER_OTLP_ENDPOINT": f"{base}/v1/private/otel",
                   "OTEL_EXPORTER_OTLP_HEADERS": "projectName=app,Authorization=Basic%20abcdefgh1234"}
        self.run_it("--out", str(self.out), "--experiment", "x", "--dataset", "feat",
                    env={**tracing, "EVAL_OPIK_URL": base + "/"})
        traces = next(body for _, path, body, _ in server.seen if path.endswith("/traces/batch"))
        self.assertEqual(traces["traces"][0]["project_name"], "app-evals")
        self.assertEqual(server.seen[0][3].get("Authorization"), "Basic abcdefgh1234")

    def test_tracing_headers_are_never_sent_to_another_server(self):
        server, base = self.server()
        self.cases(hard())
        for endpoint, project in (("http://tracing.invalid:5173/api/v1/private/otel", "app-evals"),
                                  ("http://tracing.invalid:3000/api/public/otel", "evals")):
            del server.seen[:]
            _, result, _ = self.run_it(
                "--out", str(self.out), "--experiment", "x", "--dataset", "feat",
                env={"OTEL_EXPORTER_OTLP_ENDPOINT": endpoint, "EVAL_OPIK_URL": base,
                     "OTEL_EXPORTER_OTLP_HEADERS": "projectName=app,Authorization=Basic%20abcdefgh1234"})
            self.assertTrue(result.endswith("upload: sent"), result)
            self.assertTrue(all("Authorization" not in headers for _, _, _, headers in server.seen))
            traces = next(body for _, path, body, _ in server.seen if path.endswith("/traces/batch"))
            self.assertEqual(traces["traces"][0]["project_name"], project)

    def test_a_secret_in_an_output_is_checked_as_it_is_and_stored_replaced(self):
        server, base = self.server()
        secret, header = "sk-sentinel-12345678", "Basic hdr-sentinel-87654321"
        self.cases(hard(say=(f"ok, the key is {secret} and the header {header}; pin 1234",),
                        check={"contains": [secret]}, bad=["ok"], good=[f"it is {secret}"]),
                   judged(say=(f"fine {secret}",), replies=('{"score": 4, "reason": "it shows LEAK-HERE"}',)))
        status, result, done = self.run_it(
            "--out", str(self.out), "--experiment", "x", "--dataset", "feat",
            env={"EVAL_OPIK_URL": base, "MY_API_KEY": secret, "SHORT_TOKEN": "1234",
                 "OTEL_EXPORTER_OTLP_HEADERS": "Authorization=" + header.replace(" ", "%20")})
        self.assertEqual(status, 0, done.stdout)  # the check saw the real output
        # 9 in the six outputs, 3 in the judge's sentences, 5 more in the two cases as they are sent; what the
        # judge is given is replaced too, and not counted a second time
        self.assertIn("; 17 secret value(s) replaced in what was stored or sent;", result)
        sent = json.dumps([body for _, _, body, _ in server.seen])
        stored = self.out.read_text(encoding="utf-8") + self.out.with_suffix(".json").read_text(encoding="utf-8")
        for text in (sent, stored, done.stdout, done.stderr):
            self.assertNotIn("sentinel", text)
        self.assertIn("[redacted: MY_API_KEY]", stored)
        self.assertIn("[redacted: a tracing header]", stored)
        self.assertIn("pin 1234", stored)  # too short to be taken for a secret
        self.assertIn("[redacted: MY_API_KEY]", sent)
        asked = (self.root / "evals" / "asked.txt").read_text(encoding="utf-8")  # what the judge was given
        self.assertNotIn("sentinel", asked)
        self.assertEqual(asked.count("OUTPUT TO GRADE\nfine [redacted: MY_API_KEY]"), 3)

    def test_a_secret_never_reaches_the_judge_however_json_spells_it(self):
        secret = 'sk-"sentinel"\\path-12345678'  # a quote and a backslash: JSON text spells this value differently
        case = judged(say=("RETURN-OBJECT",))
        case["input"]["object"] = {"note": secret}
        case["rubric"] = f"Reads well, unlike {secret}."
        self.cases(case)
        status, result, done = self.run_it("--out", str(self.out), env={"MY_API_KEY": secret})
        self.assertEqual(status, 0, done.stdout)
        asked = (self.root / "evals" / "asked.txt").read_text(encoding="utf-8")
        self.assertEqual(asked.count("RUBRIC\nReads well, unlike [redacted: MY_API_KEY]."), 3)
        self.assertEqual(asked.count('"note": "[redacted: MY_API_KEY]"'), 6)  # the input and the output, three times
        self.assertNotIn("sentinel", asked)
        # 3 in the outputs, 2 in the case — its input and its rubric — though nothing was sent anywhere
        self.assertIn("; 5 secret value(s) replaced in what was stored or sent; upload: not asked for", result)
        stored = self.out.read_text(encoding="utf-8") + self.out.with_suffix(".json").read_text(encoding="utf-8")
        self.assertNotIn("sentinel", stored + done.stdout + done.stderr)

    def test_a_secret_in_a_checks_reason_is_replaced_however_the_reason_spells_it(self):
        secret = 'sk-"sentinel"\\path-12345678'  # a reason quotes the phrase it looked for, as a repr
        self.cases(hard(say=("nope",), check={"contains": [secret]}, bad=["ok"], good=[f"it is {secret}"]))
        status, result, done = self.run_it("--out", str(self.out), env={"MY_API_KEY": secret})
        self.assertEqual(status, 1, done.stdout)
        # 3 in the reasons of the three failed runs, 2 in the case: its check and its known-good answer
        self.assertIn("; 5 secret value(s) replaced in what was stored or sent; upload: not asked for", result)
        stored = self.out.read_text(encoding="utf-8") + self.out.with_suffix(".json").read_text(encoding="utf-8")
        self.assertNotIn("sentinel", stored + done.stdout + done.stderr)
        self.assertIn("does not contain '[redacted: MY_API_KEY]'", stored)
        # the same reason, printed by the self-test for a known-good answer the check rejects
        self.cases(hard(check={"contains": [secret]}, bad=["ok"], good=["it is not there"]))
        status, _, done = self.run_it("--self-test", env={"MY_API_KEY": secret})
        self.assertEqual(status, 2)
        self.assertIn("rejects known-good answer 1 (does not contain '[redacted: MY_API_KEY]')", done.stdout)
        self.assertNotIn("sentinel", done.stdout + done.stderr)

    def test_a_secret_a_case_spells_another_way_is_replaced_in_the_case_and_in_its_reasons(self):
        def stored_after(secret, check, good):
            self.cases(hard(say=("nope",), check=check, bad=["ok"], good=[good]))
            status, _, done = self.run_it("--out", str(self.out), env={"MY_API_KEY": secret})
            self.assertEqual(status, 1, done.stdout)
            return (self.out.read_text(encoding="utf-8") + self.out.with_suffix(".json").read_text(encoding="utf-8")
                    + done.stdout + done.stderr)

        quoted = 'sk-"sentinel"\\path-12345678'
        as_json = json.dumps(quoted)[1:-1]  # the phrase is the value as JSON text spells it
        stored = stored_after(quoted, {"contains": [as_json]}, as_json)
        self.assertNotIn("sentinel", stored)
        self.assertIn("does not contain '[redacted: MY_API_KEY]'", stored)
        dotted = "sk-sentinel.12345678"  # the pattern is the value as a regular expression spells it
        stored = stored_after(dotted, {"matches": [re.escape(dotted)]}, dotted)
        self.assertNotIn("sentinel", stored)
        self.assertIn("does not match '[redacted: MY_API_KEY]'", stored)

    def test_laying_a_requirement_out_in_the_table_never_writes_a_secret(self):
        secret = "sk/sentinel/12345678"  # a bar in a table cell must not be turned into the stroke that makes this
        self.cases(hard(requirement="REQ-001 sk|sentinel|12345678"))
        status, result, done = self.run_it("--out", str(self.out), env={"MY_API_KEY": secret})
        self.assertEqual(status, 0, done.stdout)
        document = self.out.read_text(encoding="utf-8")
        self.assertNotIn(secret, document)
        self.assertIn("| REQ-001 sk\\|sentinel\\|12345678 | hard |", document)
        self.assertNotIn("secret value(s) replaced", result)

    def test_a_reason_is_cut_to_size_after_its_secrets_are_replaced(self):
        secret = "sk-sentinel-12345678"  # the judge's sentence puts it across the place where a reason is cut
        self.cases(judged(replies=('{"score": 4, "reason": "' + "x" * 295 + ' LEAK-HERE"}',)))
        status, result, done = self.run_it("--out", str(self.out), env={"MY_API_KEY": secret})
        self.assertEqual(status, 0, done.stdout)
        self.assertIn("; 3 secret value(s) replaced in what was stored or sent;", result)
        stored = self.out.read_text(encoding="utf-8") + self.out.with_suffix(".json").read_text(encoding="utf-8")
        self.assertNotIn("sk-s", stored)
        self.assertTrue(all(len(row["reason"]) == 300 for row in self.results()["rows"]))

    def test_a_secret_in_a_case_is_counted_once_sent_or_not(self):
        server, base = self.server()
        secret = "sk-sentinel-12345678"
        self.cases(hard(requirement=f"REQ-001 it says ok, unlike {secret}"))
        for arguments in ((), ("--experiment", "x", "--dataset", "feat")):
            _, result, done = self.run_it("--out", str(self.out), *arguments,
                                          env={"EVAL_OPIK_URL": base, "MY_API_KEY": secret})
            self.assertIn("; 1 secret value(s) replaced in what was stored or sent; upload: ", result, arguments)
            self.assertNotIn("sentinel", self.out.read_text(encoding="utf-8") + done.stdout)
        self.assertNotIn("sentinel", json.dumps([body for _, _, body, _ in server.seen]))

    def test_a_secret_is_replaced_wherever_it_sits(self):
        server, base = self.server()
        secret = "sk-sentinel-12345678"
        case = hard(say=("RETURN-OBJECT",), check={"contains": ["ok"]}, bad=["no"], good=["ok"])
        case["input"]["object"] = {secret: "ok", "[redacted: a secret setting]": "ok too", "list": [{"deep": secret}]}
        case["requirement"] = f"REQ-001 never show {secret}"
        self.cases(case)
        name = f"KEY_{secret}"  # a setting whose own name holds the value
        status, result, done = self.run_it(
            "--out", str(self.out), "--experiment", f"feat {secret} iter 0", "--dataset", f"feat-{secret}",
            env={"EVAL_OPIK_URL": base, name: secret})
        self.assertEqual(status, 0, done.stdout)
        sent = json.dumps([body for _, _, body, _ in server.seen])
        stored = self.out.read_text(encoding="utf-8") + self.out.with_suffix(".json").read_text(encoding="utf-8")
        for text in (sent, stored, done.stdout, done.stderr):
            self.assertNotIn("sentinel", text)
        self.assertIn("[redacted: a secret setting]", stored)
        output = self.results()["rows"][0]["output"]
        self.assertEqual(len(output), 3)  # a key that becomes equal to another one is still an entry of its own
        self.assertIn("# Eval Results — feat [redacted: a secret setting] iter 0", stored)

    def test_a_secret_that_is_a_number_or_a_word_of_the_marker_is_replaced_too(self):
        server, base = self.server()
        case = hard(say=("RETURN-OBJECT",), check={"contains": ["12345678"]}, bad=["no"], good=["12345678"])
        case["input"]["object"] = {"password": 12345678, "ratio": 0.5, "note": "it was redacted here", "flag": True}
        self.cases(case)
        status, result, done = self.run_it(
            "--out", str(self.out), "--experiment", "x", "--dataset", "feat",
            env={"EVAL_OPIK_URL": base, "MY_PASSWORD": "12345678", "OTHER_SECRET": "redacted", "THIRD_TOKEN": "MY_PASSWORD"})
        self.assertEqual(status, 0, done.stdout)  # the check saw the number
        output = self.results()["rows"][0]["output"]
        self.assertEqual((output["ratio"], output["flag"]), (0.5, True))
        self.assertEqual(output["password"], "[removed]")  # its name and the word "redacted" are secrets here too
        self.assertEqual(output["note"], "it was [removed] here")
        sent = json.dumps([body for _, _, body, _ in server.seen])
        stored = self.out.read_text(encoding="utf-8") + self.out.with_suffix(".json").read_text(encoding="utf-8")
        for text in (sent, stored):
            self.assertNotIn("12345678", text)
            self.assertNotIn("redacted", text)
            self.assertNotIn("MY_PASSWORD", text)
        self.assertIn("secret value(s) replaced in what was stored or sent", result)

    def test_a_secret_only_in_a_case_that_is_sent_is_counted(self):
        server, base = self.server()
        case = hard()
        case["input"]["note"] = "sk-sentinel-12345678"
        self.cases(case)
        _, result, _ = self.run_it("--out", str(self.out), "--experiment", "x", "--dataset", "feat",
                                   env={"EVAL_OPIK_URL": base, "MY_API_KEY": "sk-sentinel-12345678"})
        self.assertIn("; 1 secret value(s) replaced in what was stored or sent; upload: sent", result)
        self.assertNotIn("sentinel", json.dumps([body for _, _, body, _ in server.seen]))

    def test_a_secret_used_as_the_project_name_is_replaced_and_counted(self):
        server, base = self.server()
        self.cases(hard())
        _, result, _ = self.run_it("--out", str(self.out), "--experiment", "x", "--dataset", "feat",
                                   env={"EVAL_OPIK_URL": base, "MY_TOKEN": "project-secret-123",
                                        "EVAL_OPIK_PROJECT": "project-secret-123"})
        self.assertNotIn("project-secret", json.dumps([body for _, _, body, _ in server.seen]))
        self.assertIn("secret value(s) replaced in what was stored or sent; upload: sent", result)
        self.assertIn(result, self.out.read_text(encoding="utf-8"))

    def test_a_redirect_is_refused_and_carries_nothing_to_another_server(self):
        other, other_base = self.server()

        class Redirect(Recorder):
            def _take(self):
                self.rfile.read(int(self.headers.get("Content-Length", 0)))
                self.send_response(302)  # the one urllib would follow, as a GET that keeps the headers
                self.send_header("Location", other_base + "/elsewhere")
                self.end_headers()

            do_POST = do_PUT = do_GET = _take

        first = HTTPServer(("127.0.0.1", 0), Redirect)
        threading.Thread(target=first.serve_forever, daemon=True).start()
        self.addCleanup(lambda: (first.shutdown(), first.server_close()))
        base = f"http://127.0.0.1:{first.server_address[1]}/api"
        self.cases(hard())
        status, result, _ = self.run_it(
            "--out", str(self.out), "--experiment", "x", "--dataset", "feat",
            env={"OTEL_EXPORTER_OTLP_ENDPOINT": f"{base}/v1/private/otel",
                 "OTEL_EXPORTER_OTLP_HEADERS": "Authorization=Basic%20abcdefgh1234"})
        self.assertEqual(status, 0)
        self.assertTrue(result.endswith("; upload: FAILED (dataset: HTTP 302)"), result)
        self.assertEqual(other.seen, [])

    def test_the_same_server_is_recognised_with_and_without_its_default_port(self):
        spec = importlib.util.spec_from_file_location("rendered_run", self.root / "evals" / "run.py")
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        headers = "projectName=app,Authorization=Basic%20abcdefgh1234"
        same = (("https://opik.example/api/v1/private/otel", "https://opik.example:443/api"),
                ("https://opik.example:443/api/v1/private/otel", "https://opik.example/api"),
                ("http://opik.example/api/v1/private/otel", "http://opik.example:80/api"))
        other = (("https://opik.example/api/v1/private/otel", "https://opik.example:8443/api"),
                 ("https://opik.example/api/v1/private/otel", "http://opik.example/api"),
                 ("https://opik.example/api/v1/private/otel", "https://opik.example.evil.test/api"))
        for pairs, expected in ((same, {"Authorization": "Basic abcdefgh1234"}), (other, {})):
            for endpoint, address in pairs:
                runner._settings = lambda: {"OTEL_EXPORTER_OTLP_ENDPOINT": endpoint, "EVAL_OPIK_URL": address,
                                            "OTEL_EXPORTER_OTLP_HEADERS": headers}
                self.assertEqual(runner.opik_target(), (address, expected, "app-evals"), (endpoint, address))

    def test_an_address_nothing_answers_at_and_no_address_at_all_are_failed_uploads(self):
        self.cases(hard(say=("nope",)))
        status, result, _ = self.run_it("--out", str(self.out), "--experiment", "x", "--dataset", "feat")
        self.assertEqual(status, 1)
        self.assertTrue(result.endswith("; upload: FAILED (no Opik address is set)"), result)
        status, result, _ = self.run_it("--out", str(self.out), "--experiment", "x", "--dataset", "feat",
                                        env={"EVAL_OPIK_URL": "http://127.0.0.1:9"})
        self.assertEqual(status, 1)
        self.assertIn("; upload: FAILED (dataset: ", result)

    def test_a_run_without_an_experiment_name_sends_nothing(self):
        server, base = self.server()
        self.cases(hard())
        _, result, _ = self.run_it("--out", str(self.out), env={"EVAL_OPIK_URL": base})
        self.assertTrue(result.endswith("; upload: not asked for"), result)
        self.assertEqual(server.seen, [])


if __name__ == "__main__":
    unittest.main()
