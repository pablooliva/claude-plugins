"""Tests for second-model-review.py — run with: python3 -m unittest discover -s scripts/tests"""
from __future__ import annotations

import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "second-model-review.py"

# A stand-in for the `codex` CLI: reads the prompt on stdin, writes its final
# message to the -o file, and does what the prompt's directives say.
FAKE_CODEX = r'''#!/usr/bin/env python3
import sys, pathlib
args = sys.argv[1:]
out = pathlib.Path(args[args.index("-o") + 1])
cwd = pathlib.Path(args[args.index("-C") + 1])
final = "REVIEW: COMPLETE\nall good"
for line in sys.stdin.read().splitlines():
    verb, _, rest = line.partition(" ")
    if verb == "WRITE":
        path = cwd / rest
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Review\n")
    elif verb == "BREAK":
        (cwd / rest).write_text("mutated\n")
    elif verb == "DELETE":
        (cwd / rest).unlink()
    elif verb == "INCOMPLETE":
        final = "REVIEW: INCOMPLETE — the tests could not be run"
    elif verb == "HANDOFF":
        final = "REVIEW: HANDOFF — SDD/.records/compacted/x.md"
    elif verb == "SILENT":
        final = "all good, nothing to add"
    elif verb == "SPAWN":
        import subprocess
        subprocess.Popen([sys.executable, "-c",
                          "import time, pathlib; time.sleep(3); pathlib.Path(%r).write_text('late\\n')" % str(cwd / rest)])
        import time; time.sleep(60)
    elif verb == "HANG":
        import time; time.sleep(60)
    elif verb == "EXIT":
        sys.exit(int(rest))
out.with_name("argv.txt").write_text(" ".join(args))
out.write_text(final)
'''

class SecondModelReviewTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name).resolve()
        self.bin = root / "bin"
        self.bin.mkdir()
        self.repo = root / "repo"
        (self.repo / "src").mkdir(parents=True)
        (self.repo / "SDD" / ".records" / "reviewer-calls").mkdir(parents=True)
        (self.repo / "src" / "app.py").write_text("guard()\n")
        (self.repo / "src" / "uncommitted.py").write_text("new work\n")
        git = ["git", "-C", str(self.repo), "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run(git + ["init", "-q"], check=True)
        subprocess.run(git + ["add", "src/app.py"], check=True)
        subprocess.run(git + ["commit", "-qm", "base"], check=True)

    def install(self, name: str, body: str) -> None:
        path = self.bin / name
        path.write_text(body.replace("#!/usr/bin/env python3", f"#!{sys.executable}", 1))
        path.chmod(path.stat().st_mode | stat.S_IEXEC)

    def call(self, *args: str, env: dict[str, str] | None = None) -> tuple[int, str]:
        base = {k: v for k, v in os.environ.items() if not k.startswith("SDD_FLOW_")}
        base["PATH"] = f"{self.bin}{os.pathsep}/usr/bin{os.pathsep}/bin"
        base.update(env or {})
        done = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=base)
        return done.returncode, done.stdout.splitlines()[0] if done.stdout else done.stderr

    def review(self, prompt: str, *expect: str, timeout: str = "30") -> tuple[int, str]:
        prompt_file = self.repo / "SDD" / ".records" / "reviewer-calls" / "4b-1.prompt.md"
        prompt_file.write_text(prompt)
        args = ["run", "--prompt-file", str(prompt_file), "--cwd", str(self.repo)]
        for path in expect or ("SDD/.records/reviews/REVIEW.md",):
            args += ["--expect", path]
        return self.call(*args, "--timeout", timeout)

    # resolve

    def test_resolve_picks_codex_when_it_is_installed(self) -> None:
        self.install("codex", FAKE_CODEX)
        self.assertEqual(self.call("resolve"), (0, "Result: codex"))

    def test_resolve_falls_back_to_claude_with_a_reason(self) -> None:
        self.assertEqual(self.call("resolve"), (3, "Result: claude (fallback — the codex CLI is not on PATH)"))


    # run

    def test_run_counts_when_the_review_file_is_written(self) -> None:
        self.install("codex", FAKE_CODEX)
        status, line = self.review("WRITE SDD/.records/reviews/REVIEW.md")
        self.assertEqual(status, 0, line)
        self.assertTrue(line.startswith("Result: OK — codex reviewed; return: "), line)
        calls = self.repo / "SDD" / ".records" / "reviewer-calls"
        self.assertEqual((calls / "4b-1.return.md").read_text(), "REVIEW: COMPLETE\nall good")
        self.assertTrue((calls / "4b-1.log").is_file())

    def test_run_fails_when_the_review_file_is_missing(self) -> None:
        self.install("codex", FAKE_CODEX)
        status, line = self.review("nothing to do")
        self.assertEqual(status, 1)
        self.assertIn("it did not write", line)

    def test_run_fails_on_a_review_file_left_from_an_earlier_run(self) -> None:
        self.install("codex", FAKE_CODEX)
        stale = self.repo / "SDD" / ".records" / "reviews" / "REVIEW.md"
        stale.parent.mkdir(parents=True)
        stale.write_text("# Old review\n")
        status, line = self.review("nothing to do")
        self.assertEqual(status, 1)
        self.assertIn("was not written during this run", line)

    def test_run_fails_when_the_reviewer_says_incomplete(self) -> None:
        self.install("codex", FAKE_CODEX)
        status, line = self.review("WRITE SDD/.records/reviews/REVIEW.md\nINCOMPLETE now")
        self.assertEqual(status, 1)
        self.assertIn("REVIEW: INCOMPLETE — the tests could not be run", line)

    def test_run_reports_a_handoff_without_asking_for_the_review_file(self) -> None:
        self.install("codex", FAKE_CODEX)
        status, line = self.review("BREAK src/app.py\nHANDOFF now")
        self.assertEqual(status, 4, line)
        self.assertTrue(line.startswith("Result: HANDOFF — codex: REVIEW: HANDOFF — SDD/.records/compacted/x.md"), line)
        self.assertEqual((self.repo / "src" / "app.py").read_text(), "guard()\n")

    def test_run_puts_back_a_tracked_file_that_gitignore_also_matches(self) -> None:
        self.install("codex", FAKE_CODEX)
        git = ["git", "-C", str(self.repo), "-c", "user.name=t", "-c", "user.email=t@t"]
        (self.repo / "src" / "settings.cfg").write_text("mode = strict\n")
        subprocess.run(git + ["add", "src/settings.cfg"], check=True)
        (self.repo / ".gitignore").write_text("*.cfg\n")
        subprocess.run(git + ["add", ".gitignore"], check=True)
        subprocess.run(git + ["commit", "-qm", "settings"], check=True)
        status, line = self.review("BREAK src/settings.cfg\nWRITE SDD/.records/reviews/REVIEW.md")
        self.assertEqual(status, 0, line)
        self.assertIn("src/settings.cfg", line)
        self.assertEqual((self.repo / "src" / "settings.cfg").read_text(), "mode = strict\n")

    def test_run_does_not_start_the_reviewer_when_the_tree_cannot_be_recorded(self) -> None:
        self.install("codex", FAKE_CODEX)
        plain = self.repo.parent / "plain"
        (plain / "calls").mkdir(parents=True)
        prompt = plain / "calls" / "4b-1.prompt.md"
        prompt.write_text("WRITE REVIEW.md")
        status, line = self.call("run", "--prompt-file", str(prompt), "--cwd", str(plain),
                                 "--expect", "REVIEW.md", env={"GIT_CEILING_DIRECTORIES": str(self.repo.parent)})
        self.assertEqual(status, 1, line)
        self.assertIn("not started", line)
        self.assertFalse((plain / "REVIEW.md").exists())

    def test_run_fails_when_the_answer_has_no_status_line(self) -> None:
        self.install("codex", FAKE_CODEX)
        status, line = self.review("WRITE SDD/.records/reviews/REVIEW.md\nSILENT now")
        self.assertEqual(status, 1, line)
        self.assertIn("no `REVIEW: ` status line", line)

    def test_run_on_timeout_stops_what_the_reviewer_started(self) -> None:
        self.install("codex", FAKE_CODEX)
        status, line = self.review("SPAWN src/late.py", timeout="1")
        self.assertEqual(status, 1, line)
        self.assertIn("no answer after 1 s", line)
        import time
        time.sleep(4)
        self.assertFalse((self.repo / "src" / "late.py").exists())

    def test_run_cancelled_stops_the_reviewer_and_puts_code_back(self) -> None:
        import signal
        import time
        self.install("codex", FAKE_CODEX)
        prompt = self.repo / "SDD" / ".records" / "reviewer-calls" / "4b-1.prompt.md"
        prompt.write_text("BREAK src/app.py\nHANG now")
        env = dict(os.environ, PATH=f"{self.bin}{os.pathsep}/usr/bin{os.pathsep}/bin")
        proc = subprocess.Popen([sys.executable, str(SCRIPT), "run", "--prompt-file", str(prompt),
                                 "--cwd", str(self.repo), "--expect", "SDD/.records/reviews/REVIEW.md"],
                                stdout=subprocess.PIPE, text=True, env=env)
        deadline = time.time() + 20
        while (self.repo / "src" / "app.py").read_text() != "mutated\n" and time.time() < deadline:
            time.sleep(0.1)
        proc.send_signal(signal.SIGTERM)
        out, _ = proc.communicate(timeout=30)
        self.assertEqual(proc.returncode, 1, out)
        self.assertIn("cancelled; put back 1 file(s)", out)
        self.assertEqual((self.repo / "src" / "app.py").read_text(), "guard()\n")

    def test_run_fails_when_the_cli_exits_non_zero(self) -> None:
        self.install("codex", FAKE_CODEX)
        status, line = self.review("WRITE SDD/.records/reviews/REVIEW.md\nEXIT 7")
        self.assertEqual(status, 1)
        self.assertIn("the codex CLI exited 7", line)

    def test_run_puts_back_code_the_reviewer_left_changed(self) -> None:
        self.install("codex", FAKE_CODEX)
        status, line = self.review(
            "BREAK src/app.py\nDELETE src/uncommitted.py\nBREAK src/stray.py\nWRITE SDD/.records/reviews/REVIEW.md"
        )
        self.assertEqual(status, 0, line)
        self.assertIn("put back 3 file(s) it left changed: src/app.py, src/stray.py, src/uncommitted.py", line)
        self.assertEqual((self.repo / "src" / "app.py").read_text(), "guard()\n")
        self.assertEqual((self.repo / "src" / "uncommitted.py").read_text(), "new work\n")
        self.assertFalse((self.repo / "src" / "stray.py").exists())
        self.assertTrue((self.repo / "SDD" / ".records" / "reviews" / "REVIEW.md").is_file())

    def test_run_puts_code_back_after_a_failed_run_too(self) -> None:
        self.install("codex", FAKE_CODEX)
        status, line = self.review("BREAK src/app.py\nEXIT 1")
        self.assertEqual(status, 1)
        self.assertIn("put back 1 file(s)", line)
        self.assertEqual((self.repo / "src" / "app.py").read_text(), "guard()\n")

    def test_run_leaves_the_git_index_alone(self) -> None:
        self.install("codex", FAKE_CODEX)
        before = subprocess.run(["git", "-C", str(self.repo), "status", "--porcelain", "--", "src"], capture_output=True, text=True)
        self.review("BREAK src/app.py\nWRITE SDD/.records/reviews/REVIEW.md")
        after = subprocess.run(["git", "-C", str(self.repo), "status", "--porcelain", "--", "src"], capture_output=True, text=True)
        self.assertEqual(before.stdout, after.stdout)

    def argv(self) -> str:
        """The arguments the fake codex was started with."""
        return (self.repo / "SDD" / ".records" / "reviewer-calls" / "argv.txt").read_text()

    def test_run_gives_codex_network_access_by_default(self) -> None:
        self.install("codex", FAKE_CODEX)
        status, line = self.review("WRITE SDD/.records/reviews/REVIEW.md")
        self.assertEqual(status, 0, line)
        self.assertIn("-c sandbox_workspace_write.network_access=true", self.argv())

    def test_run_appends_the_reviewer_args(self) -> None:
        self.install("codex", FAKE_CODEX)
        prompt_file = self.repo / "SDD" / ".records" / "reviewer-calls" / "4b-1.prompt.md"
        prompt_file.write_text("WRITE SDD/.records/reviews/REVIEW.md")
        status, line = self.call("run", "--prompt-file", str(prompt_file), "--cwd", str(self.repo),
                                 "--expect", "SDD/.records/reviews/REVIEW.md", env={"SDD_FLOW_REVIEWER_ARGS": "-m gpt-x --skip-git-repo-check"})
        self.assertEqual(status, 0, line)
        self.assertTrue(self.argv().endswith("-m gpt-x --skip-git-repo-check -"), self.argv())

    def test_run_fails_when_the_cli_is_not_installed(self) -> None:
        status, line = self.review("anything")
        self.assertEqual(status, 1)
        self.assertIn("could not be started", line)


if __name__ == "__main__":
    unittest.main()
