"""Tests for hooks/context_guard.py, the Safety-Net hook. Run: python3 -m unittest discover -s scripts/tests"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parents[4] / "hooks" / "context_guard.py"
COMPACT = "/plugins/agent-engineering/skills/sdd-flow/bodies/implementation-compact.md"
RULE_TEXT = ('Read the compact-body path given in your prompt (under "Compact instructions — use only if the '
             'Safety-Net trips") and follow it: write `SDD/.records/compacted/[phase]-compacted-[ts].md`. '
             'The hook writes your counter file (path in your prompt under "Your counter file").')


class GuardTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.main = self.root / "projects" / "session-1.jsonl"
        self.main.parent.mkdir(parents=True)
        self.main.write_text("", encoding="utf-8")
        self.agent = self.root / "projects" / "session-1" / "subagents" / "agent-abc.jsonl"
        self.agent.parent.mkdir(parents=True)
        self.counter = self.root / "SDD/.records/counters/4a-SLICE-001-2026-11-27_10-00-00.md"
        self.counter.parent.mkdir(parents=True)
        self.counter.write_text("Context: 0/120000 tokens\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def transcript(self, tokens: list[int], prompt: str | None = None) -> None:
        if prompt is None:
            prompt = (f"Read this file FIRST: body.md\n{RULE_TEXT}\n"
                      f"Your counter file: SDD/.records/counters/{self.counter.name} (holds `Context: 0/120000 tokens`)\n"
                      f"Compact instructions — use only if the Safety-Net trips:\n{COMPACT}\n")
        lines = [json.dumps({"type": "user", "message": {"role": "user", "content": prompt}})]
        for n in tokens:
            lines.append(json.dumps({"type": "assistant", "message": {"usage": {
                "input_tokens": 2, "cache_read_input_tokens": n - 102, "cache_creation_input_tokens": 50,
                "output_tokens": 50}}}))
            lines.append(json.dumps({"type": "user", "message": {"content": [{"type": "tool_result", "content": "x"}]}}))
        self.agent.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def call(self, tool: str = "Read", agent: str | None = "abc", **given) -> dict | None:
        data = {"session_id": "session-1", "transcript_path": str(self.main), "cwd": str(self.root),
                "hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": given or {"file_path": "/repo/src/a.py"}}
        if agent:
            data["agent_id"] = agent
        out = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(data), capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        return json.loads(out.stdout) if out.stdout.strip() else None

    def test_under_the_limit_the_call_is_allowed_and_the_counter_shows_the_context(self) -> None:
        self.transcript([30_000, 64_000])
        self.assertIsNone(self.call())
        self.assertEqual(self.counter.read_text(encoding="utf-8"), "Context: 64000/120000 tokens\n")

    def test_past_the_limit_a_work_call_is_refused_and_the_counter_says_tripped(self) -> None:
        self.transcript([90_000, 121_000])
        for tool, given in (("Read", {"file_path": "/repo/src/a.py"}), ("Bash", {"command": "sed -n 1,80p src/a.py"}),
                            ("Edit", {"file_path": "/repo/src/a.py"}), ("Grep", {"pattern": "x"})):
            answer = self.call(tool, **given)
            self.assertEqual(answer["hookSpecificOutput"]["permissionDecision"], "deny", tool)
            self.assertTrue(answer["hookSpecificOutput"]["permissionDecisionReason"].startswith("Safety-Net tripped"))
            self.assertIn(COMPACT, answer["hookSpecificOutput"]["permissionDecisionReason"])
        self.assertEqual(self.counter.read_text(encoding="utf-8"), "Context: 121000/120000 tokens — tripped\n")

    def test_past_the_limit_the_handoff_calls_are_allowed(self) -> None:
        self.transcript([121_000])
        self.assertIsNone(self.call("Read", file_path=COMPACT))
        self.assertIsNone(self.call("Write", file_path=str(self.root / "SDD/.records/compacted/implementation-compacted-x.md")))
        self.assertIsNone(self.call("Edit", file_path=str(self.root / "SDD/.records/progress.md")))
        self.assertIsNone(self.call("Read", file_path="SDD/.records/progress.md"))
        self.assertIsNone(self.call("Bash", command="date +%Y-%m-%d_%H-%M-%S"))

    def test_past_the_limit_bash_and_look_alike_paths_are_refused(self) -> None:
        self.transcript([121_000])
        for tool, given in (("Bash", {"command": "cat >> SDD/.records/progress.md <<'EOF'\nx\nEOF; pytest"}),
                            ("Bash", {"command": "date; pytest"}),
                            ("Bash", {"command": "date\npytest"}),
                            ("Edit", {"file_path": "/other/cycle/SDD/.records/progress.md"}),
                            ("Write", {"file_path": str(self.root / "src/progress.md")}),
                            ("Edit", {"file_path": str(self.root / "src/compacted/notes.md")}),
                            ("Read", {"file_path": "/elsewhere/bodies/implementation-compact.md.bak"})):
            self.assertEqual(self.call(tool, **given)["hookSpecificOutput"]["permissionDecision"], "deny", (tool, given))

    def test_once_tripped_a_smaller_sample_does_not_untrip(self) -> None:
        self.transcript([121_000])
        self.assertIsNotNone(self.call())
        self.transcript([40_000])  # e.g. the harness compacted the subagent
        self.assertEqual(self.call()["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertEqual(self.counter.read_text(encoding="utf-8"), "Context: 40000/120000 tokens — tripped\n")

    def test_paths_with_spaces_are_read_whole(self) -> None:
        counter = self.root / "My Repo/SDD/.records/counters/4a-1.md"
        counter.parent.mkdir(parents=True)
        counter.write_text("Context: 0/1000 tokens\n", encoding="utf-8")
        compact = "/Users/x/Code & Dev/plugin/skills/sdd-flow/bodies/implementation-compact.md"
        self.transcript([5_000], prompt=f"{RULE_TEXT}\nYour counter file: `{counter}` (holds `Context: 0/1000 tokens`)\n"
                                        f"Compact instructions — use only if the Safety-Net trips: {compact}\n")
        answer = self.call()
        self.assertIn(compact, answer["hookSpecificOutput"]["permissionDecisionReason"])
        self.assertEqual(counter.read_text(encoding="utf-8"), "Context: 5000/1000 tokens — tripped\n")
        self.assertIsNone(self.call("Read", file_path=compact))

    def test_the_limit_is_the_one_the_counter_file_was_created_with(self) -> None:
        self.counter.write_text("Context: 0/50000 tokens\n", encoding="utf-8")
        self.transcript([60_000])
        self.assertEqual(self.call()["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertEqual(self.counter.read_text(encoding="utf-8"), "Context: 60000/50000 tokens — tripped\n")

    def test_the_rule_text_alone_names_no_counter_file_so_the_call_is_left_alone(self) -> None:
        self.transcript([500_000], prompt=f"{RULE_TEXT}\nno counter here")
        self.assertIsNone(self.call())
        self.assertEqual(self.counter.read_text(encoding="utf-8"), "Context: 0/120000 tokens\n")

    def test_the_main_session_and_unreadable_input_are_left_alone(self) -> None:
        self.transcript([500_000])
        self.assertIsNone(self.call(agent=None))
        self.assertIsNone(self.call(agent="missing"))
        out = subprocess.run([sys.executable, str(HOOK)], input="not json", capture_output=True, text=True)
        self.assertEqual((out.returncode, out.stdout), (0, ""))

    def test_a_usage_record_longer_than_the_first_piece_read_is_still_found(self) -> None:
        self.transcript([121_000])
        big = json.dumps({"type": "user", "message": {"content": [{"type": "tool_result", "content": "x" * 600_000}]}})
        with self.agent.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"type": "assistant", "message": {"content": "y" * 700_000, "usage": {
                "input_tokens": 1, "cache_read_input_tokens": 130_000, "output_tokens": 9}}}) + "\n" + big + "\n")
        self.assertEqual(self.call()["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertEqual(self.counter.read_text(encoding="utf-8"), "Context: 130010/120000 tokens — tripped\n")

    def test_a_subagent_with_no_reported_usage_yet_is_allowed(self) -> None:
        self.transcript([])
        self.assertIsNone(self.call())


if __name__ == "__main__":
    unittest.main()
