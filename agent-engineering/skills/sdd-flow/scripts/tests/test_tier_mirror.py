"""Tests for scripts/tier-mirror.py. Run: python3 -m unittest discover -s scripts/tests

`bb` is replaced by a stub that keeps the tracker in a JSON file and answers
with the same JSON shapes the real CLI prints.
"""
from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tier-mirror.py"

FAKE_BB = textwrap.dedent('''\
    #!/usr/bin/env python3
    import json, os, sys
    STATE = os.environ["FAKE_BB_STATE"]
    s = json.load(open(STATE))
    a = [x for x in sys.argv[1:] if x != "--json"]
    s["calls"].append(a)
    def opt(name, default=None):
        return a[a.index(name) + 1] if name in a else default
    def out(d, code=0):
        json.dump(s, open(STATE, "w"))
        print(json.dumps(d)); sys.exit(code)
    def fail(msg):
        out({"ok": False, "error": {"code": "x", "message": msg}}, 1)
    def find(ref):
        for t in s["tasks"]:
            if ref in (t["key"], t["id"]):
                return t
        fail("task not found: " + ref)
    if s.get("fail") and " ".join(a).startswith(s["fail"]):
        fail("boom")
    if a[:1] == ["status"]:
        out({"project": {"id": "proj_1", "name": "demo-repo"}} if s["in_project"] else {"project": None})
    if a[:3] == ["tasks", "project", "list"]:
        out({"projects": s["projects"]})
    if a[:3] == ["tasks", "project", "create"]:
        p = {"id": "P1", "name": opt("--name"), "prefix": "DEMO", "linkedBbProjectId": opt("--link-bb-project")}
        s["projects"].append(p); out({"project": p})
    if a[:2] == ["tasks", "create"]:
        n = len(s["tasks"]) + 1
        desc = opt("--description") or open(opt("--description-file")).read()
        t = {"id": "ID%d" % n, "key": "%s-%d" % (opt("--project"), n), "title": opt("--title"),
             "description": desc, "status": "backlog", "parentTaskId": opt("--parent"),
             "comments": [], "attachments": [], "threads": []}
        s["tasks"].append(t); out({"task": t})
    if a[:2] == ["tasks", "list"]:
        q = opt("--search", "")
        out({"tasks": [t for t in s["tasks"] if q in t["title"]], "nextCursor": None})
    if a[:2] == ["tasks", "show"]:
        t = find(a[2])
        out({"task": t, "subtasks": [x for x in s["tasks"] if x["parentTaskId"] == t["id"]],
             "comments": t["comments"], "attachments": t["attachments"],
             "taskThreads": [{"threadId": x} for x in t["threads"]]})
    if a[:2] == ["tasks", "update"]:
        t = find(a[2]); t["status"] = opt("--status"); out({"task": t})
    if a[:2] == ["tasks", "comment"]:
        t = find(a[2])
        t["comments"].append({"id": "C%d" % (len(t["comments"]) + 1), "kind": "agent", "authorName": opt("--author"),
                              "body": open(opt("--body-file")).read(), "createdAt": "2026-10-03T10:00:00Z"})
        out({"comment": {}})
    if a[:3] == ["tasks", "attachment", "add"]:
        find(a[3])["attachments"].append({"fileName": os.path.basename(opt("--file"))}); out({})
    if a[:2] == ["tasks", "attach"]:
        find(a[2])["threads"].append(opt("--thread")); out({})
    fail("unknown command: " + " ".join(a))
''')

PLAN = textwrap.dedent("""\
    # TIERS-csv-export

    | Tier | Status | Built in | Task |
    |---|---|---|---|
    | 1 — POC-plus | planned | — | — |
    | 2 — Standard | sketch | — | — |
    | 3 — Full | sketch | — | — |

    ## Tier 1
    Exports the current report as CSV.

    ## Deferred
    | ID | Item | To tier | Why it was safe to leave out | If reached now | Cost to add later | Came from |
    |---|---|---|---|---|---|---|

    ## Removed

    ## Tier 2 — sketch
    Column selection.

    ## Tier 3 — sketch
    Scheduled exports.

    ## Feedback
    """)


class TierMirrorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: subprocess.run(["rm", "-rf", str(self.tmp)]))
        self.bb = self.tmp / "bb"
        self.bb.write_text(FAKE_BB)
        self.bb.chmod(self.bb.stat().st_mode | stat.S_IEXEC)
        self.state_path = self.tmp / "state.json"
        self.save({"projects": [], "tasks": [], "calls": [], "in_project": True, "fail": ""})
        self.plan = self.tmp / "TIERS-csv-export.md"
        self.plan.write_text(PLAN)

    def save(self, state: dict) -> None:
        self.state_path.write_text(json.dumps(state))

    def state(self) -> dict:
        return json.loads(self.state_path.read_text())

    def run_script(self, *args: str, bb: str | None = "default", project: str | None = "proj_1",
                   thread: str | None = None):
        env = {k: v for k, v in os.environ.items() if not k.startswith("BB_")}
        env["FAKE_BB_STATE"] = str(self.state_path)
        env["PATH"] = "/usr/bin:/bin"
        if bb == "default":
            env["BB_CLI"] = str(self.bb)
        if project:
            env["BB_PROJECT_ID"] = project
        if thread:
            env["BB_THREAD_ID"] = thread
        proc = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=env)
        return proc.returncode, proc.stdout.strip()

    def statuses(self) -> dict[str, str]:
        return {t["key"]: t["status"] for t in self.state()["tasks"]}

    def test_off_without_bb_cli_changes_nothing(self) -> None:
        code, out = self.run_script("sync", str(self.plan), bb=None)
        self.assertEqual(code, 3)
        self.assertTrue(out.startswith("Result: OFF"), out)
        self.assertEqual(self.plan.read_text(), PLAN)

    def test_off_outside_a_bb_project(self) -> None:
        state = self.state()
        state["in_project"] = False
        self.save(state)
        code, out = self.run_script("sync", str(self.plan), project=None)
        self.assertEqual(code, 3)
        self.assertIn("not inside a BB project", out)

    def test_failed_project_lookup_is_an_error_not_off(self) -> None:
        state = self.state()
        state["fail"] = "status"
        self.save(state)
        code, out = self.run_script("sync", str(self.plan), project=None)
        self.assertEqual(code, 1)
        self.assertTrue(out.startswith("Result: ERROR"), out)

    def test_creates_tracker_project_when_none_is_linked(self) -> None:
        code, out = self.run_script("sync", str(self.plan), "--active", "1")
        self.assertEqual(code, 0, out)
        projects = self.state()["projects"]
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]["linkedBbProjectId"], "proj_1")
        self.assertEqual(projects[0]["name"], "demo-repo")
        self.assertIn("created tracker project DEMO", out)

    def test_uses_the_existing_linked_project(self) -> None:
        state = self.state()
        state["projects"] = [{"id": "P0", "name": "other", "prefix": "OTH", "linkedBbProjectId": "proj_9"},
                             {"id": "P1", "name": "demo", "prefix": "DEMO", "linkedBbProjectId": "proj_1"}]
        self.save(state)
        code, out = self.run_script("sync", str(self.plan))
        self.assertEqual(code, 0, out)
        self.assertEqual(len(self.state()["projects"]), 2)
        self.assertTrue(all(t["key"].startswith("DEMO-") for t in self.state()["tasks"]))

    def test_creates_parent_and_three_subtasks_and_writes_keys(self) -> None:
        code, out = self.run_script("sync", str(self.plan), "--active", "1")
        self.assertEqual(code, 0, out)
        tasks = self.state()["tasks"]
        self.assertEqual([t["title"] for t in tasks],
                         ["csv-export", "Tier 1 — POC-plus · csv-export",
                          "Tier 2 — Standard · csv-export", "Tier 3 — Full · csv-export"])
        self.assertTrue(all(t["parentTaskId"] == "ID1" for t in tasks[1:]))
        self.assertIn("Exports the current report as CSV.", tasks[1]["description"])
        text = self.plan.read_text()
        self.assertIn("| 1 — POC-plus | planned | — | DEMO-2 |", text)
        self.assertIn("| 3 — Full | sketch | — | DEMO-4 |", text)
        self.assertEqual(self.statuses(),
                         {"DEMO-1": "in_progress", "DEMO-2": "in_progress", "DEMO-3": "backlog", "DEMO-4": "backlog"})

    def test_second_run_creates_nothing(self) -> None:
        self.run_script("sync", str(self.plan), "--active", "1")
        code, out = self.run_script("sync", str(self.plan), "--active", "1")
        self.assertEqual(code, 0, out)
        self.assertEqual(len(self.state()["tasks"]), 4)
        self.assertIn("no changes", out)

    def test_rerun_after_partial_failure_does_not_duplicate(self) -> None:
        state = self.state()
        state["fail"] = "tasks update"
        self.save(state)
        code, out = self.run_script("sync", str(self.plan), "--active", "1")
        self.assertEqual(code, 1)
        self.assertTrue(out.startswith("Result: ERROR"), out)
        state = self.state()
        state["fail"] = ""
        self.save(state)
        code, out = self.run_script("sync", str(self.plan), "--active", "1")
        self.assertEqual(code, 0, out)
        self.assertEqual(len(self.state()["tasks"]), 4)

    def test_parent_found_by_title_when_no_keys_were_written(self) -> None:
        self.run_script("sync", str(self.plan))
        state = self.state()
        state["tasks"] = state["tasks"][:1]  # as if the run died right after creating the parent
        self.save(state)
        self.plan.write_text(PLAN)
        self.run_script("sync", str(self.plan))
        tasks = self.state()["tasks"]
        self.assertEqual([t["title"] for t in tasks].count("csv-export"), 1)
        self.assertEqual(len(tasks), 4)

    def test_review_then_shipped(self) -> None:
        self.run_script("sync", str(self.plan), "--active", "1")
        self.run_script("sync", str(self.plan), "--in-review", "1")
        self.assertEqual(self.statuses()["DEMO-2"], "in_review")
        self.plan.write_text(self.plan.read_text().replace("| planned |", "| shipped 2026-10-03 |"))
        self.run_script("sync", str(self.plan), "--in-review", "1")
        self.assertEqual(self.statuses()["DEMO-2"], "in_review")  # row says shipped; the commit is still pending
        code, out = self.run_script("sync", str(self.plan), "--shipped", "1")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.statuses(),
                         {"DEMO-1": "in_progress", "DEMO-2": "done", "DEMO-3": "backlog", "DEMO-4": "backlog"})
        comments = self.state()["tasks"][1]["comments"]
        self.assertEqual(len(comments), 1)
        self.assertIn("Shipped — Tier 1", comments[0]["body"])
        self.run_script("sync", str(self.plan), "--shipped", "1")
        self.assertEqual(len(self.state()["tasks"][1]["comments"]), 1)

    def test_active_tier_two_covers_tier_one(self) -> None:
        self.run_script("sync", str(self.plan), "--active", "2")
        self.assertEqual(self.statuses()["DEMO-2"], "in_progress")
        self.assertEqual(self.statuses()["DEMO-3"], "in_progress")
        self.assertEqual(self.statuses()["DEMO-4"], "backlog")

    def test_all_tiers_closed_closes_the_parent(self) -> None:
        text = (PLAN.replace("| planned |", "| shipped 2026-10-03 |")
                    .replace("| 2 — Standard | sketch |", "| 2 — Standard | shipped 2026-11-01 |")
                    .replace("| 3 — Full | sketch |", "| 3 — Full | dropped |"))
        self.plan.write_text(text)
        self.run_script("sync", str(self.plan))
        self.assertEqual(self.statuses(),
                         {"DEMO-1": "done", "DEMO-2": "done", "DEMO-3": "done", "DEMO-4": "canceled"})

    def test_brief_attached_once(self) -> None:
        brief = self.tmp / "DESIGN-042-csv-export.md"
        brief.write_text("# brief\n")
        self.run_script("sync", str(self.plan), "--active", "1", "--brief", str(brief))
        self.run_script("sync", str(self.plan), "--active", "1", "--brief", str(brief))
        self.assertEqual(self.state()["tasks"][1]["attachments"], [{"fileName": "DESIGN-042-csv-export.md"}])
        self.assertEqual(self.state()["tasks"][2]["attachments"], [])

    def test_feedback_copies_user_comments_once(self) -> None:
        self.run_script("sync", str(self.plan), "--active", "1")
        state = self.state()
        state["tasks"][2]["comments"] = [
            {"id": "C1", "kind": "system", "authorName": "Tasks", "body": "Status changed", "createdAt": "2026-10-04T08:00:00Z"},
            {"id": "C2", "kind": "user", "authorName": "Pablo", "body": "Need column order.\nAlso dates.", "createdAt": "2026-10-05T08:00:00Z"},
        ]
        self.save(state)
        code, out = self.run_script("feedback", str(self.plan), "--tier", "2")
        self.assertEqual(code, 0, out)
        self.assertIn("1 new comment", out)
        text = self.plan.read_text()
        self.assertIn("- 2026-10-05 (DEMO-3, Pablo): Need column order. <!-- task-comment:C2 -->\n  Also dates.", text)
        self.assertNotIn("Status changed", text)
        code, out = self.run_script("feedback", str(self.plan), "--tier", "2")
        self.assertIn("0 new comments", out)
        self.assertEqual(self.plan.read_text(), text)

    def test_subtasks_relinked_when_keys_were_lost(self) -> None:
        self.run_script("sync", str(self.plan), "--active", "1")
        self.plan.write_text(PLAN)  # as if the run died before the keys were saved
        code, out = self.run_script("sync", str(self.plan), "--active", "1")
        self.assertEqual(code, 0, out)
        self.assertEqual(len(self.state()["tasks"]), 4)
        self.assertIn("| 2 — Standard | sketch | — | DEMO-3 |", self.plan.read_text())

    def test_escaped_pipe_in_a_cell_does_not_shift_columns(self) -> None:
        self.plan.write_text(PLAN.replace("| 1 — POC-plus | planned | — | — |",
                                          "| 1 — POC-plus | planned | SPEC-1 \\| PR 7 | — |"))
        code, out = self.run_script("sync", str(self.plan), "--active", "1")
        self.assertEqual(code, 0, out)
        self.assertIn("| 1 — POC-plus | planned | SPEC-1 \\| PR 7 | DEMO-2 |", self.plan.read_text())

    def test_feedback_creates_the_section_when_absent(self) -> None:
        self.run_script("sync", str(self.plan), "--active", "1")
        text = self.plan.read_text()
        self.plan.write_text(text[:text.index("## Feedback")].rstrip() + "\n")
        state = self.state()
        state["tasks"][2]["comments"] = [{"id": "C9", "kind": "user", "authorName": "Pablo", "body": "More please.",
                                          "createdAt": "2026-10-05T08:00:00Z"}]
        self.save(state)
        code, out = self.run_script("feedback", str(self.plan), "--tier", "2")
        self.assertEqual(code, 0, out)
        self.assertTrue(self.plan.read_text().rstrip().endswith(
            "## Feedback\n- 2026-10-05 (DEMO-3, Pablo): More please. <!-- task-comment:C9 -->"))

    def test_lower_tier_built_in_the_same_cycle_stays_in_review(self) -> None:
        self.run_script("sync", str(self.plan), "--active", "2")
        text = (self.plan.read_text().replace("| planned | — |", "| shipped 2026-10-03 | SPEC-042 |")
                                     .replace("| 2 — Standard | sketch | — |", "| 2 — Standard | shipped 2026-10-03 | SPEC-042 |"))
        self.plan.write_text(text)
        self.run_script("sync", str(self.plan), "--in-review", "2")
        self.assertEqual(self.statuses()["DEMO-2"], "in_review")
        self.assertEqual(self.statuses()["DEMO-3"], "in_review")
        self.run_script("sync", str(self.plan), "--shipped", "2")
        self.assertEqual(self.statuses()["DEMO-2"], "done")
        self.assertEqual(self.statuses()["DEMO-3"], "done")

    def test_tier_shipped_by_an_earlier_cycle_stays_done_during_review(self) -> None:
        text = (PLAN.replace("| planned | — |", "| shipped 2026-10-03 | SPEC-042 |")
                    .replace("| 2 — Standard | sketch | — |", "| 2 — Standard | shipped 2026-11-01 | SPEC-050 |"))
        self.plan.write_text(text)
        self.run_script("sync", str(self.plan), "--in-review", "2")
        self.assertEqual(self.statuses()["DEMO-2"], "done")
        self.assertEqual(self.statuses()["DEMO-3"], "in_review")

    def test_thread_attached_once_and_failure_is_reported(self) -> None:
        self.run_script("sync", str(self.plan), "--active", "1", thread="thr_1")
        self.run_script("sync", str(self.plan), "--active", "1", thread="thr_1")
        self.assertEqual(self.state()["tasks"][1]["threads"], ["thr_1"])
        state = self.state()
        state["fail"] = "tasks attach"
        self.save(state)
        code, out = self.run_script("sync", str(self.plan), "--active", "1", thread="thr_2")
        self.assertEqual(code, 1)
        self.assertTrue(out.startswith("Result: ERROR"), out)

    def test_feedback_dedup_matches_whole_comment_ids(self) -> None:
        self.run_script("sync", str(self.plan), "--active", "1")
        state = self.state()
        state["tasks"][2]["comments"] = [
            {"id": "C10", "kind": "user", "authorName": "Pablo", "body": "ten", "createdAt": "2026-10-05T08:00:00Z"}]
        self.save(state)
        self.run_script("feedback", str(self.plan), "--tier", "2")
        state = self.state()
        state["tasks"][2]["comments"].append(
            {"id": "C1", "kind": "user", "authorName": "Pablo", "body": "one", "createdAt": "2026-10-06T08:00:00Z"})
        self.save(state)
        code, out = self.run_script("feedback", str(self.plan), "--tier", "2")
        self.assertIn("1 new comment", out)
        self.assertIn("): one <!-- task-comment:C1 -->", self.plan.read_text())

    def test_feedback_without_a_task(self) -> None:
        code, out = self.run_script("feedback", str(self.plan), "--tier", "2")
        self.assertEqual(code, 0)
        self.assertIn("NO-TASK", out)

    def test_malformed_plan_is_an_input_error(self) -> None:
        self.plan.write_text("# TIERS-x\n\nno table\n")
        code, out = self.run_script("sync", str(self.plan))
        self.assertEqual(code, 2)
        self.assertIn("INPUT-ERROR", out)


if __name__ == "__main__":
    unittest.main()
