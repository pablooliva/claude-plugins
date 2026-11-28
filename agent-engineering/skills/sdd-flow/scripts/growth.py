#!/usr/bin/env python3
"""Measure how much a feature has grown, against the growth budget in its design brief.

Usage:
    growth.py --base <commit> --brief <DESIGN-brief.md> [--repo <dir>]

Compares the working tree (committed and uncommitted work, untracked files
included, the cycle's SDD root left out) with BASE, and reads the brief's `## Growth budget`
and `## What changes where` sections. Prints three lines:

    Growth: source +<n> of ~<n> (<r>x), tests +<n> of ~<n> (<r>x), new files <n> of <n>, tests per source line <t> — left out: <what>
    Unnamed new files: none | <path>, <path>
    Over budget: yes | no

- The SDD root is the folder two levels above the brief when the brief sits in a
  `requirements/` folder (`<root>/requirements/DESIGN-*.md`), else `SDD` — judged on
  the path as given, before any symlink in it is followed. Everything under
  the root — plan, summary, slices, spec, records — is left out of every count and
  of the new files. A root that is REPO itself or lies outside it is a usage error:
  REPO must be the folder that holds the code, with the SDD root inside it.
- Lines are lines added (git's numstat "added" column; every line of an untracked
  text file). A file is a test file when a directory in its path is `test`,
  `tests`, `__tests__` or `spec`, or its name starts `test_`, ends `_test.<ext>`,
  contains `.test.` or `.spec.`, or is `conftest.py`.
- Left out of both line counts, and named at the end of the first line
  (`left out: none`, or `left out: data <n> lines (<k> files), plugin templates <n> lines (<k> files)`):
  - **data** — a file whose extension is one of DATA_EXTENSIONS, a lockfile
    (LOCKFILES), or a path the brief's optional `- Not source:` line under
    `## Growth budget` names in backticks (a path ending in `/` names everything
    under it). Data is read by the code; it is not code.
  - **plugin templates** — the lines of a new file rendered from one of this
    plugin's templates (`*.template` under sdd-flow's and observability-init's
    `templates/`). A new file is rendered from a template when its first line
    is that template's first line, which is a distinctive docstring line. Only
    the file's lines that are also the template's lines are left out, each
    template line once; what the application filled in or changed counts.
- A new file is named when its exact path appears in backticks in the first
  column of the brief's "What changes where" table.
- Tests per source line: test lines added divided by source lines added (`n/a`
  when no source line was added). Shown as a warning sign for tests sized to the
  code's shape rather than its behaviour; never a limit.
- Over budget: source or test lines added exceed OVERRUN (1.5) times their
  estimate. An estimate of 0 with any line added is over.

Exit status: 0 = measured; 3 = the brief has no readable `## Growth budget`
(the three lines are not printed; the first stdout line says so); 2 = usage
error or a git failure. Deterministic: stdlib only.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path, PurePosixPath

OVERRUN = 1.5
TEST_DIRS = {"test", "tests", "__tests__", "spec"}
DATA_EXTENSIONS = {".txt", ".json", ".jsonl", ".csv", ".tsv"}
LOCKFILES = {"uv.lock", "poetry.lock", "Pipfile.lock", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
             "Cargo.lock", "Gemfile.lock", "composer.lock", "go.sum"}
SKILLS = Path(__file__).resolve().parents[2]
TEMPLATE_DIRS = [SKILLS / "sdd-flow" / "templates", SKILLS / "observability-init" / "templates"]


def is_test(path: str) -> bool:
    p = PurePosixPath(path)
    if any(part in TEST_DIRS for part in p.parts[:-1]):
        return True
    name = p.name
    return (
        name == "conftest.py"
        or name.startswith("test_")
        or re.search(r"_test\.[^.]+$", name) is not None
        or ".test." in name
        or ".spec." in name
    )


def not_source(brief: str) -> list[str]:
    """Paths the brief's optional `- Not source:` line names (under `## Growth budget`)."""
    m = re.search(r"^-\s*Not source:(.*)$", section(brief, "Growth budget"), re.M)
    return re.findall(r"`([^`]+)`", m.group(1)) if m else []


def is_data(path: str, listed: list[str]) -> bool:
    p = PurePosixPath(path)
    if p.suffix.lower() in DATA_EXTENSIONS or p.name in LOCKFILES:
        return True
    return any(path == n or (n.endswith("/") and path.startswith(n)) for n in listed)


def load_templates() -> dict[str, list[str]]:
    """First line → the template's lines, for every plugin template."""
    found: dict[str, list[str]] = {}
    for folder in TEMPLATE_DIRS:
        for t in sorted(folder.rglob("*.template")) if folder.is_dir() else []:
            text = t.read_text(encoding="utf-8").splitlines()
            if text and len(text[0].strip()) >= 20:
                found.setdefault(text[0], text)
    return found


def rendered_lines(text: list[str], templates: dict[str, list[str]]) -> int:
    """How many of a new file's lines come from the plugin template it was rendered from (0 when none)."""
    template = templates.get(text[0]) if text else None
    if template is None:
        return 0
    left = Counter(template)
    count = 0
    for line in text:
        if left[line] > 0:
            left[line] -= 1
            count += 1
    return count


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True).stdout


def section(text: str, heading: str) -> str:
    m = re.search(rf"^## {re.escape(heading)}[ \t]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def read_budget(brief: str) -> dict[str, int] | None:
    body = section(brief, "Growth budget")
    budget = {}
    for key, label in (("source", "Source lines added"), ("tests", "Test lines added"), ("files", "New files")):
        m = re.search(rf"^-\s*{label}:\s*~?\s*([\d,]+)", body, re.M)
        if not m:
            return None
        budget[key] = int(m.group(1).replace(",", ""))
    return budget


def named_paths(brief: str) -> set[str]:
    names = set()
    for line in section(brief, "What changes where").splitlines():
        cells = line.strip().split("|")
        if len(cells) > 2:
            names.update(t.strip() for t in re.findall(r"`([^`]+)`", cells[1]))
    return names


def sdd_root(repo: Path, brief: str) -> str:
    """The cycle's SDD root, relative to REPO, as a POSIX path. ValueError when it is REPO or outside it."""
    folder = Path(os.path.normpath(repo / brief)).parent  # named as given: no symlink changes which folder it is
    if folder.name != "requirements":
        return "SDD"
    root = folder.parent.resolve().relative_to(repo).as_posix()  # ValueError outside REPO
    if root == ".":
        raise ValueError("the SDD root is the --repo folder itself")
    return root


class Counts:
    def __init__(self) -> None:
        self.source = self.tests = 0
        self.data_lines = self.template_lines = 0
        self.data_files: set[str] = set()
        self.template_files: set[str] = set()

    def add(self, path: str, added: int, text: list[str] | None, listed: list[str], templates: dict[str, list[str]]) -> None:
        """`text` is the file's content when it is new (all its lines are added), else None."""
        if is_data(path, listed):
            self.data_lines += added
            self.data_files.add(path)
            return
        if text is not None:
            rendered = min(rendered_lines(text, templates), added)
            if rendered:
                self.template_lines += rendered
                self.template_files.add(path)
                added -= rendered
        if is_test(path):
            self.tests += added
        else:
            self.source += added

    def left_out(self) -> str:
        parts = []
        if self.data_files:
            parts.append(f"data {self.data_lines} lines ({len(self.data_files)} files)")
        if self.template_files:
            parts.append(f"plugin templates {self.template_lines} lines ({len(self.template_files)} files)")
        return ", ".join(parts) or "none"


def read_lines(repo: Path, path: str) -> list[str] | None:
    try:
        return (repo / path).read_text(encoding="utf-8").splitlines()
    except (UnicodeDecodeError, OSError):
        return None  # binary or unreadable: no lines to count


def measure(repo: Path, base: str, root: str, listed: list[str]) -> tuple[Counts, list[str]]:
    """NUL-separated git output (-z), so a path with unusual characters is read as it is, never quoted."""
    counts = Counts()
    templates = load_templates()
    exclude = f":(exclude,literal){root}"
    added_files = [p for p in git(repo, "diff", "--name-only", "-z", "--no-renames", "--diff-filter=A", base, "--", ".", exclude).split("\0") if p]
    new = set(added_files)
    fields = git(repo, "diff", "--numstat", "-z", "--no-renames", base, "--", ".", exclude).split("\0")
    for row in fields:
        if not row:
            continue
        added, _removed, path = row.split("\t", 2)
        if added == "-":  # binary
            continue
        counts.add(path, int(added), read_lines(repo, path) if path in new else None, listed, templates)
    untracked = [p for p in git(repo, "ls-files", "-z", "--others", "--exclude-standard", "--", ".", exclude).split("\0") if p]
    for path in untracked:
        text = read_lines(repo, path)
        if text is not None:
            counts.add(path, len(text), text, listed, templates)
    return counts, sorted(new | set(untracked))


def ratio(actual: int, estimate: int) -> tuple[str, bool]:
    if estimate == 0:
        return ("0.0x" if actual == 0 else "inf"), actual > 0
    r = actual / estimate
    return f"{r:.1f}x", r > OVERRUN


def per_source(tests: int, source: int) -> str:
    return f"{tests / source:.1f}" if source else "n/a"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Measure a feature's growth against its design brief's budget.")
    ap.add_argument("--base", required=True)
    ap.add_argument("--brief", required=True)
    ap.add_argument("--repo", default=".")
    args = ap.parse_args(argv)
    repo = Path(args.repo).resolve()
    try:
        brief = (repo / args.brief).read_text(encoding="utf-8")
    except OSError as e:
        print(f"Result: ERROR — cannot read the brief: {e}")
        return 2
    try:
        root = sdd_root(repo, args.brief)
    except ValueError:
        print("Result: ERROR — --repo must hold the code, with the brief's SDD root (<root>/requirements/) inside it")
        return 2
    budget = read_budget(brief)
    if budget is None:
        print("Result: NO BUDGET — the brief has no readable ## Growth budget section")
        return 3
    try:
        counts, new_files = measure(repo, args.base, root, not_source(brief))
    except subprocess.CalledProcessError as e:
        print(f"Result: ERROR — git failed: {e.stderr.strip()}")
        return 2
    names = named_paths(brief)
    unnamed = [f for f in new_files if f not in names]
    source, tests = counts.source, counts.tests
    rs, over_s = ratio(source, budget["source"])
    rt, over_t = ratio(tests, budget["tests"])
    print(
        f"Growth: source +{source} of ~{budget['source']} ({rs}), tests +{tests} of ~{budget['tests']} ({rt}), "
        f"new files {len(new_files)} of {budget['files']}, tests per source line {per_source(tests, source)}"
        f" — left out: {counts.left_out()}"
    )
    print("Unnamed new files: " + (", ".join(unnamed) if unnamed else "none"))
    print("Over budget: " + ("yes" if over_s or over_t else "no"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
