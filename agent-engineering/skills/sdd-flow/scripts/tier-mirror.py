#!/usr/bin/env python3
"""Mirror a feature's tier plan to BB tasks, and pull task comments back into it.

Usage:
    tier-mirror.py sync <TIERS-plan.md> [--active N] [--in-review N] [--shipped N] [--brief <path>]
    tier-mirror.py feedback <TIERS-plan.md> --tier N

The tier plan (`SDD/flow/TIERS-[feature-name].md`, shape in the tier standard)
is the record; BB tasks mirror it. `sync` makes the tracker match the plan:

- finds the tracker project linked to the current BB project, creating one
  (named after the BB project, linked to it) when none exists;
- creates one parent task for the feature and one sub-task per tier, for every
  tier whose `Task` cell is empty, and writes the new keys into the plan;
- sets each sub-task's status from its row: `shipped` -> done, `in progress` ->
  in_progress, `dropped` -> canceled, anything else -> backlog. `--active N` /
  `--in-review N` override the row text for tier N and every lower tier that
  is neither shipped nor dropped (the tiers the current cycle is building);
  `--in-review N` holds tier N at in_review even when its row already says
  `shipped`, because the row is updated before the final commit;
- `--shipped N` posts tier N's section of the plan as a comment, once;
- `--brief` attaches the design brief to the tiers being built, once per name.

`feedback` appends the non-system comments on tier N's sub-task to the plan's
`## Feedback` section, dated, skipping comments already copied.

The first stdout line is `Result: ...`. Exit status: 0 = done; 3 = OFF (no `bb`
CLI, or not inside a BB project — nothing was changed; the caller must say so
to the user); 1 = a `bb` command failed; 2 = usage or input error.
Deterministic: stdlib only; talks to BB only through the `bb` CLI ($BB_CLI or PATH).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

TITLE_RE = re.compile(r"^# TIERS-(.+?)\s*$", re.M)
ROW_RE = re.compile(r"^\|\s*([123])\b[^|]*\|")
MARK = "task-comment:"
EMPTY = {"", "—", "-", "–"}


class Off(Exception):
    """BB is not available here; nothing was changed."""


class BbError(Exception):
    """A bb command failed."""


class InputError(Exception):
    """The tier plan is missing or malformed."""


# ---------------------------------------------------------------- tier plan


class Plan:
    def __init__(self, path: Path) -> None:
        if not path.is_file():
            raise InputError(f"tier plan not found: {path}")
        self.path = path
        self.lines = path.read_text(encoding="utf-8").split("\n")
        m = TITLE_RE.search("\n".join(self.lines))
        if not m:
            raise InputError(f"{path}: no '# TIERS-[feature-name]' title")
        self.feature = m.group(1)
        self.rows: dict[int, int] = {}  # tier -> line index
        for i, line in enumerate(self.lines):
            m = ROW_RE.match(line)
            if m and len(self._cells(line)) >= 4 and int(m.group(1)) not in self.rows:
                self.rows[int(m.group(1))] = i
        if sorted(self.rows) != [1, 2, 3]:
            raise InputError(f"{path}: status table must have one row each for tiers 1, 2 and 3")

    @staticmethod
    def _cells(line: str) -> list[str]:
        return [c.strip() for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]  # `\|` is a literal pipe

    def cell(self, tier: int, col: int) -> str:
        return self._cells(self.lines[self.rows[tier]])[col]

    def label(self, tier: int) -> str:
        return self.cell(tier, 0)

    def status(self, tier: int) -> str:
        return self.cell(tier, 1).lower()

    def key(self, tier: int) -> str | None:
        value = self.cell(tier, 3).strip("`")
        return None if value in EMPTY else value

    def set_key(self, tier: int, key: str) -> None:
        cells = self._cells(self.lines[self.rows[tier]])
        cells[3] = key
        self.lines[self.rows[tier]] = "| " + " | ".join(cells) + " |"
        self.save()

    def section(self, tier: int) -> str:
        """Body of the '## Tier N…' section, or '' if there is none."""
        out: list[str] = []
        inside = False
        for line in self.lines:
            if line.startswith("## "):
                if inside:
                    break
                inside = re.match(rf"^## Tier {tier}\b", line) is not None
                continue
            if inside:
                out.append(line)
        return "\n".join(out).strip()

    def append_feedback(self, entries: list[str]) -> None:
        start = next((i for i, l in enumerate(self.lines) if l.strip() == "## Feedback"), None)
        if start is None:
            while self.lines and not self.lines[-1].strip():
                self.lines.pop()
            self.lines += ["", "## Feedback"]
            start = len(self.lines) - 1
        end = next((i for i in range(start + 1, len(self.lines)) if self.lines[i].startswith("## ")),
                   len(self.lines))
        while end > start + 1 and not self.lines[end - 1].strip():
            end -= 1
        self.lines[end:end] = entries
        self.save()

    def save(self) -> None:
        self.path.write_text("\n".join(self.lines), encoding="utf-8")


# ----------------------------------------------------------------------- bb


class Bb:
    def __init__(self) -> None:
        exe = os.environ.get("BB_CLI") or shutil.which("bb")
        if not exe or not (Path(exe).is_file() or shutil.which(exe)):
            raise Off("the bb CLI was not found")
        self.exe = exe

    def run(self, *args: str, check: bool = True) -> Any:
        proc = subprocess.run([self.exe, *args, "--json"], capture_output=True, text=True)
        try:
            data = json.loads(proc.stdout) if proc.stdout.strip() else {}
        except json.JSONDecodeError:
            data = {}
        failed = proc.returncode != 0 or (isinstance(data, dict) and data.get("ok") is False)
        if failed and check:
            detail = ""
            if isinstance(data, dict) and isinstance(data.get("error"), dict):
                detail = str(data["error"].get("message", ""))
            detail = detail or proc.stderr.strip() or proc.stdout.strip() or f"exit {proc.returncode}"
            raise BbError(f"`bb {' '.join(args[:3])}` failed: {detail.splitlines()[0][:200]}")
        return None if failed else data

    def project_id(self) -> tuple[str, str]:
        """(bb project id, name) of the BB project this checkout belongs to."""
        pid = os.environ.get("BB_PROJECT_ID", "")
        name = ""
        # With no id in the environment, a failing `bb status` is an ERROR, not OFF:
        # OFF is only for a lookup that worked and found no project.
        status = self.run("status", check=not pid) or {}
        project = status.get("project") or {}
        if not pid:
            pid = project.get("id") or ""
        if project.get("id") == pid:
            name = project.get("name") or ""
        if not pid:
            raise Off("this checkout is not inside a BB project")
        if not name:
            shown = self.run("project", "show", pid, check=False) or {}
            name = shown.get("name") or (shown.get("project") or {}).get("name") or pid
        return pid, name

    def tracker(self, notes: list[str]) -> str:
        """Prefix of the tracker project linked to this BB project; created if absent."""
        pid, name = self.project_id()
        for project in self.run("tasks", "project", "list").get("projects", []):
            if project.get("linkedBbProjectId") == pid:
                return project["prefix"]
        made = self.run("tasks", "project", "create", "--name", name, "--link-bb-project", pid)
        made = made.get("project", made)
        notes.append(f"created tracker project {made['prefix']} ({name})")
        return made["prefix"]

    def show(self, key: str) -> dict[str, Any]:
        return self.run("tasks", "show", key)


def task_of(data: dict[str, Any]) -> dict[str, Any]:
    return data.get("task", data)


# --------------------------------------------------------------------- sync


def wanted_status(plan: Plan, tier: int, active: int, review: int) -> str:
    text = plan.status(tier)
    if text.startswith("dropped"):
        return "canceled"
    # In review beats `shipped`: the completion step marks the rows before the final commit —
    # tier N's, and that of any lower tier the same cycle built (same `Built in` cell).
    built = plan.cell(tier, 2)
    if tier == review or (tier < review and built not in EMPTY and built == plan.cell(review, 2)):
        return "in_review"
    if text.startswith("shipped"):
        return "done"
    if tier < review:
        return "in_review"
    if tier <= active or text.startswith("in progress"):
        return "in_progress"
    return "backlog"


def find_parent(bb: Bb, plan: Plan, prefix: str, notes: list[str]) -> str:
    for tier in (1, 2, 3):
        key = plan.key(tier)
        if key:
            parent = task_of(bb.show(key)).get("parentTaskId")
            if parent:
                return parent
    listed = bb.run("tasks", "list", "--project", prefix, "--search", plan.feature, "--limit", "500")
    for task in listed.get("tasks", []):
        if task.get("title") == plan.feature and not task.get("parentTaskId"):
            return task["id"]
    made = task_of(bb.run(
        "tasks", "create", "--project", prefix, "--title", plan.feature,
        "--description", f"Delivered in tiers, one sub-task per tier.\n\nTier plan: `{plan.path.as_posix()}`"))
    notes.append(f"created {made['key']} for the feature")
    return made["id"]


def sync(plan: Plan, active: int, review: int, shipped: int, brief: Path | None) -> str:
    bb = Bb()
    notes: list[str] = []
    prefix = bb.tracker(notes)
    parent_id = find_parent(bb, plan, prefix, notes)

    existing = {t.get("title"): t.get("key") for t in bb.show(parent_id).get("subtasks", [])}
    for tier in (1, 2, 3):
        if plan.key(tier):
            continue
        title = f"Tier {plan.label(tier)} · {plan.feature}"
        if existing.get(title):  # created by a run that died before the key was saved
            plan.set_key(tier, existing[title])
            notes.append(f"re-linked {existing[title]} (Tier {tier})")
            continue
        body = plan.section(tier) or "See the tier plan."
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as fh:
            fh.write(body + f"\n\nTier plan: `{plan.path.as_posix()}`\n")
        try:
            made = task_of(bb.run(
                "tasks", "create", "--project", prefix, "--parent", parent_id,
                "--title", title, "--description-file", fh.name))
        finally:
            os.unlink(fh.name)
        plan.set_key(tier, made["key"])  # saved at once, so a failed run can be repeated
        notes.append(f"created {made['key']} (Tier {tier})")

    parent = bb.show(parent_id)
    current = {t.get("key"): t.get("status") for t in parent.get("subtasks", [])}
    wanted = {tier: wanted_status(plan, tier, active, review) for tier in (1, 2, 3)}
    for tier in (1, 2, 3):
        key = plan.key(tier)
        if current.get(key) != wanted[tier]:
            bb.run("tasks", "update", key, "--status", wanted[tier])
            notes.append(f"{key} -> {wanted[tier]}")

    states = set(wanted.values())
    if states <= {"done", "canceled"}:
        parent_status = "done"
    elif states == {"backlog"}:
        parent_status = "backlog"
    else:
        parent_status = "in_progress"
    if task_of(parent).get("status") != parent_status:
        bb.run("tasks", "update", task_of(parent)["key"], "--status", parent_status)

    building = [t for t in (1, 2, 3) if wanted[t] in ("in_progress", "in_review")]
    for tier in building:
        key = plan.key(tier)
        shown = bb.show(key)
        thread = os.environ.get("BB_THREAD_ID")
        if thread and thread not in {t.get("threadId") for t in shown.get("taskThreads", [])}:
            bb.run("tasks", "attach", key, "--thread", thread)
            notes.append(f"attached this thread to {key}")
        if brief and brief.is_file():
            names = {a.get("name") or a.get("fileName") for a in shown.get("attachments", [])}
            if brief.name not in names:
                bb.run("tasks", "attachment", "add", key, "--file", str(brief))
                notes.append(f"attached {brief.name} to {key}")

    if shipped:
        key = plan.key(shipped)
        marker = f"Shipped — Tier {shipped}"
        if not any(marker in (c.get("body") or "") for c in bb.show(key).get("comments", [])):
            body = f"**{marker}**\n\n{plan.section(shipped) or 'See the tier plan.'}\n\nTier plan: `{plan.path.as_posix()}`\n"
            with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as fh:
                fh.write(body)
            try:
                bb.run("tasks", "comment", key, "--body-file", fh.name, "--author", "sdd-flow")
            finally:
                os.unlink(fh.name)
            notes.append(f"commented on {key}")

    keys = ", ".join(f"Tier {t} {plan.key(t)} {wanted[t]}" for t in (1, 2, 3))
    return f"SYNCED ({keys})" + (f" — {'; '.join(notes)}" if notes else " — no changes")


# ----------------------------------------------------------------- feedback


def feedback(plan: Plan, tier: int) -> str:
    key = plan.key(tier)
    if not key:
        return f"NO-TASK (Tier {tier} has no task in the tier plan — nothing to copy)"
    bb = Bb()
    text = "\n".join(plan.lines)
    entries: list[str] = []
    for comment in bb.show(key).get("comments", []):
        body = (comment.get("body") or "").strip()
        if comment.get("kind") == "system" or not body or f"{MARK}{comment.get('id')} -->" in text:
            continue
        date = (comment.get("createdAt") or "")[:10] or "undated"
        author = comment.get("authorName") or "unknown"
        first, *rest = body.split("\n")
        entries.append(f"- {date} ({key}, {author}): {first} <!-- {MARK}{comment.get('id')} -->")
        entries += [f"  {line}".rstrip() for line in rest]
    if not entries:
        return f"FEEDBACK (0 new comments on {key})"
    plan.append_feedback(entries)
    count = sum(1 for e in entries if e.startswith("- "))
    return f"FEEDBACK ({count} new comment(s) copied from {key} into the tier plan)"


# --------------------------------------------------------------------- main


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="tier-mirror.py", description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p_sync = sub.add_parser("sync")
    p_sync.add_argument("plan", type=Path)
    for flag in ("--active", "--in-review", "--shipped"):
        p_sync.add_argument(flag, type=int, choices=(1, 2, 3), default=0)
    p_sync.add_argument("--brief", type=Path)
    p_feedback = sub.add_parser("feedback")
    p_feedback.add_argument("plan", type=Path)
    p_feedback.add_argument("--tier", type=int, choices=(1, 2, 3), required=True)
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        return 2
    try:
        plan = Plan(args.plan)
        if args.command == "sync":
            result = sync(plan, args.active, args.in_review, args.shipped, args.brief)
        else:
            result = feedback(plan, args.tier)
    except Off as exc:
        print(f"Result: OFF ({exc} — tiers are not mirrored to BB tasks; the tier plan is unaffected)")
        return 3
    except BbError as exc:
        print(f"Result: ERROR ({exc})")
        return 1
    except InputError as exc:
        print(f"Result: INPUT-ERROR ({exc})")
        return 2
    print(f"Result: {result}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
