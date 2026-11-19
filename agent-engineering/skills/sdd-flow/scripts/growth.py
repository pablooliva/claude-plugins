#!/usr/bin/env python3
"""Measure how much a feature has grown, against the growth budget in its design brief.

Usage:
    growth.py --base <commit> --brief <DESIGN-brief.md> [--repo <dir>]

Compares the working tree (committed and uncommitted work, untracked files
included, the cycle's SDD root left out) with BASE, and reads the brief's `## Growth budget`
and `## What changes where` sections. Prints three lines:

    Growth: source +<n> of ~<n> (<r>x), tests +<n> of ~<n> (<r>x), new files <n> of <n>, tests per source line <t>
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
from pathlib import Path, PurePosixPath

OVERRUN = 1.5
TEST_DIRS = {"test", "tests", "__tests__", "spec"}


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


def measure(repo: Path, base: str, root: str) -> tuple[int, int, list[str]]:
    """NUL-separated git output (-z), so a path with unusual characters is read as it is, never quoted."""
    source = tests = 0
    exclude = f":(exclude,literal){root}"
    fields = git(repo, "diff", "--numstat", "-z", "--no-renames", base, "--", ".", exclude).split("\0")
    for row in fields:
        if not row:
            continue
        added, _removed, path = row.split("\t", 2)
        if added == "-":  # binary
            continue
        if is_test(path):
            tests += int(added)
        else:
            source += int(added)
    untracked = [p for p in git(repo, "ls-files", "-z", "--others", "--exclude-standard", "--", ".", exclude).split("\0") if p]
    for path in untracked:
        try:
            n = len((repo / path).read_text(encoding="utf-8").splitlines())
        except (UnicodeDecodeError, OSError):
            continue  # binary or unreadable: no lines to count
        if is_test(path):
            tests += n
        else:
            source += n
    added_files = [p for p in git(repo, "diff", "--name-only", "-z", "--no-renames", "--diff-filter=A", base, "--", ".", exclude).split("\0") if p]
    return source, tests, sorted(set(added_files) | set(untracked))


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
        source, tests, new_files = measure(repo, args.base, root)
    except subprocess.CalledProcessError as e:
        print(f"Result: ERROR — git failed: {e.stderr.strip()}")
        return 2
    names = named_paths(brief)
    unnamed = [f for f in new_files if f not in names]
    rs, over_s = ratio(source, budget["source"])
    rt, over_t = ratio(tests, budget["tests"])
    print(
        f"Growth: source +{source} of ~{budget['source']} ({rs}), tests +{tests} of ~{budget['tests']} ({rt}), "
        f"new files {len(new_files)} of {budget['files']}, tests per source line {per_source(tests, source)}"
    )
    print("Unnamed new files: " + (", ".join(unnamed) if unnamed else "none"))
    print("Over budget: " + ("yes" if over_s or over_t else "no"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
