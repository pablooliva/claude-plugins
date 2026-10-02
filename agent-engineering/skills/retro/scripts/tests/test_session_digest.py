"""Tests for scripts/session-digest.py. Run: python3 -m unittest discover -s scripts/tests"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "session-digest.py"
REPO = "/work/shop"


def encode(path: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in path)


class Transcript:
    """Builds one session's JSONL the way Claude Code writes it."""

    def __init__(self, cwd: str = REPO, branch: str = "feat/cart", day: str = "2026-09-10") -> None:
        self.cwd, self.branch, self.day = cwd, branch, day
        self.lines: list[str] = []
        self.calls = 0

    def _add(self, entry: dict) -> None:
        minute = len(self.lines) % 60
        entry.update(cwd=self.cwd, gitBranch=self.branch, timestamp=f"{self.day}T12:{minute:02d}:00.000Z")
        self.lines.append(json.dumps(entry))

    def prompt(self, text: str, **extra: object) -> "Transcript":
        self._add({"type": "user", "message": {"role": "user", "content": text}, **extra})
        return self

    def call(self, name: str, tool_input: dict, result: str = "ok", error: bool = False,
             usage: dict | None = None, message_id: str | None = None) -> "Transcript":
        self.calls += 1
        call_id = f"toolu_{self.calls}"
        message = {"id": message_id or f"msg_{self.calls}", "role": "assistant",
                   "content": [{"type": "tool_use", "id": call_id, "name": name, "input": tool_input}]}
        if usage:
            message["usage"] = usage
        self._add({"type": "assistant", "message": message})
        self._add({"type": "user", "message": {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": call_id, "content": result, "is_error": error}]}})
        return self

    def raw(self, text: str) -> "Transcript":
        self.lines.append(text)
        return self

    def compact(self) -> "Transcript":
        self._add({"type": "system", "subtype": "compact_boundary"})
        self._add({"type": "user", "isCompactSummary": True, "message": {"role": "user", "content": "Summary of earlier work"}})
        return self

    def write(self, projects: Path, sid: str, folder: str | None = None) -> Path:
        target = projects / (folder or encode(self.cwd))
        target.mkdir(parents=True, exist_ok=True)
        path = target / f"{sid}.jsonl"
        path.write_text("\n".join(self.lines) + "\n", encoding="utf-8")
        return path


class SessionDigestTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.projects = Path(self.tmp.name) / "projects"
        self.projects.mkdir()

    def run_script(self, *args: str) -> subprocess.CompletedProcess:
        # --repo names a path that is not a git checkout, so the only root is that path itself.
        return subprocess.run([sys.executable, str(SCRIPT), args[0], "--projects-dir", str(self.projects),
                               "--repo", REPO, *args[1:]], capture_output=True, text=True)

    def test_list_covers_every_session_of_the_repo_and_nothing_else(self) -> None:
        Transcript().prompt("build the cart").write(self.projects, "aaaa1111")
        Transcript(day="2026-09-11").prompt("continue after clear").write(self.projects, "bbbb2222")
        Transcript(cwd=REPO + "/api").prompt("started in a subdirectory").write(self.projects, "cccc3333")
        Transcript(cwd="/work/shop-admin").prompt("a sibling repo").write(self.projects, "dddd4444")
        Transcript(cwd="/work/other").prompt("unrelated").write(self.projects, "eeee5555")
        Transcript().prompt("legacy subagent file").write(self.projects, "agent-a1b2c3")
        out = self.run_script("list")
        self.assertEqual(out.returncode, 0, out.stderr)
        for sid in ("aaaa1111", "bbbb2222", "cccc3333"):
            self.assertIn(sid, out.stdout)
        for sid in ("dddd4444", "eeee5555", "agent-a1b2c3"):
            self.assertNotIn(sid, out.stdout)
        self.assertLess(out.stdout.index("aaaa1111"), out.stdout.index("bbbb2222"))

    def test_list_filters_by_branch_and_date(self) -> None:
        Transcript(branch="feat/cart", day="2026-09-10").prompt("a").write(self.projects, "aaaa1111")
        Transcript(branch="main", day="2026-09-10").prompt("b").write(self.projects, "bbbb2222")
        Transcript(branch="feat/cart", day="2026-09-20").prompt("c").write(self.projects, "cccc3333")
        by_branch = self.run_script("list", "--branch", "feat/cart").stdout
        self.assertIn("aaaa1111", by_branch)
        self.assertIn("cccc3333", by_branch)
        self.assertNotIn("bbbb2222", by_branch)
        windowed = self.run_script("list", "--branch", "feat/cart", "--since", "2026-09-15").stdout
        self.assertNotIn("aaaa1111", windowed)
        self.assertIn("cccc3333", windowed)
        # Midday UTC stays on the same calendar day in every timezone, so the bounds are inclusive here.
        until = self.run_script("list", "--until", "2026-09-10").stdout
        self.assertIn("aaaa1111", until)
        self.assertIn("bbbb2222", until)
        self.assertNotIn("cccc3333", until)
        self.assertIn("aaaa1111", self.run_script("list", "--since", "2026-09-10", "--until", "2026-09-10").stdout)

    def test_any_project_finds_a_removed_worktrees_sessions_by_branch(self) -> None:
        Transcript(cwd="/gone/worktree/shop", branch="feat/cart").prompt("a").write(self.projects, "aaaa1111")
        self.assertEqual(self.run_script("list", "--branch", "feat/cart").returncode, 2)
        out = self.run_script("list", "--branch", "feat/cart", "--any-project")
        self.assertIn("aaaa1111", out.stdout)

    def test_no_sessions_and_bad_date_are_usage_errors(self) -> None:
        self.assertEqual(self.run_script("list").returncode, 2)
        self.assertEqual(self.run_script("list", "--since", "yesterday").returncode, 2)
        self.assertEqual(self.run_script("list", "--since", "2026-02-31").returncode, 2)

    def test_wrongly_typed_fields_do_not_crash(self) -> None:
        t = Transcript().prompt("go")
        t.raw(json.dumps({"type": "assistant", "timestamp": 12, "gitBranch": None, "cwd": 7,
                          "message": {"id": "m1", "usage": {"output_tokens": "~2k", "input_tokens": [1]}, "content": {"type": "text"}}}))
        t.raw(json.dumps({"type": "user", "timestamp": "", "message": {"content": [{"type": "tool_result", "tool_use_id": None, "content": 5}, "stray"]}}))
        t.raw(json.dumps({"type": "user", "message": "not a dict"}))
        t.raw(json.dumps(["a list, not an object"]))
        t.write(self.projects, "aaaa1111")
        listed = self.run_script("list", "--since", "2026-09-01")
        self.assertEqual(listed.returncode, 0, listed.stderr)
        digest = self.run_script("digest", "aaaa1111")
        self.assertEqual(digest.returncode, 0, digest.stderr)
        self.assertIn("**Output:** 0 tokens", digest.stdout)

    def test_session_without_a_recorded_cwd_needs_an_exact_directory_match(self) -> None:
        line = json.dumps({"type": "user", "timestamp": "2026-09-10T12:00:00.000Z", "message": {"content": "no cwd here"}})
        for sid, folder in (("aaaa1111", encode(REPO)), ("bbbb2222", encode(REPO + "-backup"))):
            target = self.projects / folder
            target.mkdir(parents=True, exist_ok=True)
            (target / f"{sid}.jsonl").write_text(line + "\n", encoding="utf-8")
        out = self.run_script("list").stdout
        self.assertIn("aaaa1111", out)
        self.assertNotIn("bbbb2222", out)

    def test_digest_reports_prompts_errors_and_line_numbers(self) -> None:
        t = Transcript().prompt("add a discount field")
        t.call("Bash", {"command": "npm test"}, result="FAIL cart.test.ts: expected 90 got 100", error=True)
        t.prompt("no — discounts are per line, not per cart")
        t.prompt("<system-reminder>ignored</system-reminder>")
        t.prompt("injected by the harness", isMeta=True)
        path = t.write(self.projects, "aaaa1111")
        out = self.run_script("digest", "aaaa").stdout
        self.assertIn(f"`{path}`", out)
        self.assertIn("L1: add a discount field", out)
        self.assertIn("L4: no — discounts are per line", out)
        self.assertIn("L2 Bash: npm test → FAIL cart.test.ts", out)
        self.assertIn("**Errors:** 1", out)
        self.assertNotIn("ignored", out)
        self.assertNotIn("injected by the harness", out)

    def test_digest_reports_lookup_runs_only_when_no_edit_intervenes(self) -> None:
        t = Transcript().prompt("find where tax is applied")
        for n in range(9):
            t.call("Grep", {"pattern": f"tax{n}", "path": "src"})
        t.call("Edit", {"file_path": "src/tax.ts"})
        for n in range(4):
            t.call("Read", {"file_path": f"src/f{n}.ts"})
        t.compact()  # 4 lookups before + 4 after would read as one run of 8 if a compaction were bridged
        for n in range(4):
            t.call("Glob", {"pattern": f"after{n}"})
        t.write(self.projects, "aaaa1111")
        out = self.run_script("digest", "aaaa1111").stdout
        self.assertIn("9 lookups (first: tax0 in src; last: tax8 in src)", out)
        self.assertEqual(out.count(" lookups (first:"), 1)  # neither an edit nor a compaction is bridged

    def test_digest_reports_repeats_and_large_results(self) -> None:
        t = Transcript().prompt("go")
        for _ in range(3):
            t.call("Read", {"file_path": "src/cart.ts"})
        t.call("Bash", {"command": "npm test"}, error=True, result="1 failed")
        t.call("Bash", {"command": "npm test"}, error=True, result="1 failed")
        t.call("Bash", {"command": "npm test"})
        t.call("Bash", {"command": "cat dist/bundle.js"}, result="x" * 9000)
        t.write(self.projects, "aaaa1111")
        out = self.run_script("digest", "aaaa1111").stdout
        self.assertIn("3× src/cart.ts", out)
        self.assertIn("3× (2 failed) npm test", out)
        self.assertIn("9,000 chars — cat dist/bundle.js", out)

    def test_digest_counts_compactions_and_tolerates_bad_lines(self) -> None:
        t = Transcript().prompt("before").raw("{not json").compact().prompt("after")
        t.write(self.projects, "aaaa1111")
        out = self.run_script("digest", "aaaa1111").stdout
        self.assertIn("**Compactions:** 1 (at L3)", out)
        self.assertIn("L5: after", out)
        self.assertNotIn("Summary of earlier work", out)

    def test_digest_counts_usage_once_per_request(self) -> None:
        usage = {"input_tokens": 10, "cache_read_input_tokens": 900, "cache_creation_input_tokens": 90, "output_tokens": 50}
        t = Transcript().prompt("go")
        t.call("Read", {"file_path": "a"}, usage=usage, message_id="msg_same")
        t.call("Read", {"file_path": "b"}, usage=usage, message_id="msg_same")
        t.write(self.projects, "aaaa1111")
        out = self.run_script("digest", "aaaa1111").stdout
        self.assertIn("**Peak context:** 1,000 tokens · **Output:** 50 tokens", out)

    def test_digest_summarises_subagents(self) -> None:
        path = Transcript().prompt("run the flow").call("Agent", {"description": "implement slice 1"}).write(self.projects, "aaaa1111")
        folder = path.with_suffix("") / "subagents"
        sub = Transcript().prompt("You are a spawned subagent")
        sub.call("Bash", {"command": "pytest -q"}, result="2 failed", error=True)
        sub.write(folder.parent, "agent-abc", folder="subagents")
        (folder / "agent-abc.meta.json").write_text(json.dumps({"agentType": "agent-engineering:sdd-workhorse"}))
        out = self.run_script("digest", "aaaa1111").stdout
        self.assertIn("`agent-abc.jsonl` agent-engineering:sdd-workhorse: 1 tool calls, 1 errors", out)
        self.assertIn("↳ L2 Bash: pytest -q → 2 failed", out)
        self.assertNotIn("agent-abc", self.run_script("digest", "aaaa1111", "--no-subagents").stdout)

    def test_digest_accepts_a_path_and_rejects_an_ambiguous_prefix(self) -> None:
        path = Transcript().prompt("one").write(self.projects, "aaaa1111")
        Transcript().prompt("two").write(self.projects, "aaaa2222")
        self.assertIn("L1: one", self.run_script("digest", str(path)).stdout)
        bad = self.run_script("digest", "aaaa")
        self.assertEqual(bad.returncode, 2)
        self.assertIn("matches 2 sessions", bad.stderr)


if __name__ == "__main__":
    unittest.main()
