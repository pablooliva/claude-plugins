#!/usr/bin/env python3
"""The working tree, recorded or copied, without touching the repository.

Usage:
    snapshot.py              print the SHA of a commit holding the working tree as it is now
    snapshot.py scratch      print the path of a new directory outside the repository
                             holding a copy of the working tree, for a mutation check

The snapshot (no argument) holds tracked and untracked files, git-ignored ones
left out. It is built in a temporary index and committed with `commit-tree`, so
the real index, HEAD, every branch, and the stash are untouched and no ref points
to it. The orchestrator takes one before and one after each fix round, so a
re-review can read what the fix changed (`git diff <before> <after>`).

The scratch copy (`scratch`) is every file of the working tree except `.git` —
uncommitted, untracked, and git-ignored files included, so the copy's tests find
their env file, fixtures, and local data. No link in the copy leads out of it: a
link inside the repository points into the copy, one to anything outside is
replaced by a copy of its target, and a dangling one is removed. It is made in
the system's temporary directory; whoever made it removes it (`rm -rf <path>`) when done. A mutation
made there cannot write into the repository, its local databases, or its caches
(`references/test-integrity.md` §8).

Exit 0 on success; 2 when not inside a git working tree or git fails.
Stdlib only, plus local `git`.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SNAPSHOT_MESSAGE = "sdd-flow: the working tree at a fix round (no ref points here)"
SNAPSHOT_IDENTITY = {"GIT_AUTHOR_NAME": "sdd-flow", "GIT_AUTHOR_EMAIL": "sdd-flow@localhost",
                     "GIT_COMMITTER_NAME": "sdd-flow", "GIT_COMMITTER_EMAIL": "sdd-flow@localhost"}


def fail(msg: str) -> None:
    print(f"snapshot: {msg}", file=sys.stderr)
    sys.exit(2)


def git(cwd: Path | None, *args: str, env: dict[str, str] | None = None) -> str:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, env=env)
    if r.returncode != 0:
        fail(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout


def repo_root() -> Path:
    return Path(git(None, "rev-parse", "--show-toplevel").strip())


def has_head(root: Path) -> bool:
    return subprocess.run(["git", "rev-parse", "--verify", "-q", "HEAD"], cwd=root,
                          capture_output=True).returncode == 0


def work_tree(root: Path) -> str:
    """The working tree as a tree object, built in a temporary index."""
    with tempfile.TemporaryDirectory() as tmp:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(tmp) / "index")}
        git(root, "read-tree", "HEAD" if has_head(root) else "--empty", env=env)
        git(root, "add", "-A", "--", ".", env=env)
        return git(root, "write-tree", env=env).strip()


def snapshot() -> str:
    root = repo_root()
    parent = ["-p", "HEAD"] if has_head(root) else []
    return git(root, "commit-tree", "--no-gpg-sign", work_tree(root), *parent, "-m", SNAPSHOT_MESSAGE,
               env={**os.environ, **SNAPSHOT_IDENTITY}).strip()


def isolate_links(root: Path, dest: Path) -> None:
    """No link in the copy may lead out of it: a write through one would reach the original.

    A link to a path inside the repository is pointed at the same path inside the copy; a link
    to anything outside is replaced by a copy of what it points to; a dangling link is removed."""
    real_root = root.resolve()
    for link in sorted(p for p in dest.rglob("*") if p.is_symlink()):
        if not link.is_symlink():  # inside a directory already replaced above
            continue
        original = root / link.relative_to(dest)
        target = original.resolve()
        link.unlink()
        if target.is_relative_to(real_root):
            inside = dest / target.relative_to(real_root)
            link.symlink_to(os.path.relpath(inside, link.parent), target_is_directory=target.is_dir())
        elif target.is_dir():
            shutil.copytree(target, link, symlinks=False)
        elif target.exists():
            shutil.copy2(target, link)


def scratch() -> str:
    root = repo_root()
    dest = Path(tempfile.mkdtemp(prefix="sdd-flow-scratch-")) / root.name
    shutil.copytree(root, dest, symlinks=True, ignore=shutil.ignore_patterns(".git"))
    isolate_links(root, dest)
    return str(dest)


def main() -> None:
    args = sys.argv[1:]
    if args == []:
        print(snapshot())
    elif args == ["scratch"]:
        print(scratch())
    else:
        fail(f"unknown arguments: {' '.join(args)} (usage: snapshot.py [scratch])")


if __name__ == "__main__":
    main()
