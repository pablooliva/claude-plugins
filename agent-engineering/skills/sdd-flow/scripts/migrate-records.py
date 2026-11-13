#!/usr/bin/env python3
"""Move a repository's sdd-flow process records into SDD/.records/ (the 4.7.0 layout).

Usage:
    migrate-records.py [--repo <dir>] [--apply]

Without --apply it prints the plan and changes nothing. With --apply it:

- moves every file under SDD/orchestration/ to SDD/.records/, every file under
  SDD/reviews/ to SDD/.records/reviews/, and every file under
  SDD/implementation/slices/superseded/ to SDD/.records/reviews/superseded/;
- writes SDD/.records/.gitignore holding `*`, replacing any old .gitignore
  that moved there;
- untracks the moved files that were committed (`git rm --cached`; they stay on
  disk and in past commits), which stages their deletion;
- rewrites the old paths to the new ones inside the moved text files and in
  SDD/implementation/IMPLEMENTATION-PLAN-*.md, so a run stopped before 4.7.0
  resumes from the paths its progress file and slice table record.

It never commits. Empty source folders are removed. It refuses, changing
nothing, when a destination file, or a folder it needs, is already taken or
claimed by two records, when a record is a symlink, or when git cannot untrack a
file (staged content that differs from both HEAD and the file).

Exit status: 0 = planned or migrated, or nothing to migrate; 1 = refused
(the reason is printed); 2 = usage error or not a git repository.
Deterministic: stdlib only.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

# (old prefix, new prefix), most specific first: the superseded folder sits inside SDD/implementation/.
MOVES = (
    ("SDD/implementation/slices/superseded", "SDD/.records/reviews/superseded"),
    ("SDD/reviews", "SDD/.records/reviews"),
    ("SDD/orchestration", "SDD/.records"),
)
REWRITE = re.compile(r"SDD/(?:implementation/slices/superseded|reviews|orchestration)(?![\w.-])")


def new_text(text: str) -> str:
    return REWRITE.sub(lambda m: dict(MOVES)[m.group(0)], text)


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)


def plan(root: Path) -> tuple[list[tuple[str, str]], list[str]]:
    """(old, new) repo-relative paths of every file to move, and every symlink among the records."""
    pairs, links = [], []
    for old, new in MOVES:
        base = root / old
        if base.is_symlink():
            links.append(old)
            continue
        if not base.is_dir():
            continue
        for folder, dirs, files in os.walk(base):
            dirs.sort()
            rel_dir = Path(folder).relative_to(root).as_posix()
            links += [f"{rel_dir}/{name}" for name in dirs if (Path(folder) / name).is_symlink()]
            for name in sorted(files):
                src = f"{rel_dir}/{name}"
                if (root / src).is_symlink():
                    links.append(src)
                else:
                    pairs.append((src, new + src[len(old):]))
    return pairs, links


def blocked(root: Path, rel: str) -> bool:
    """True when the destination, or a folder it needs, is already taken by something else."""
    if (root / rel).exists() or (root / rel).is_symlink():
        return True
    parent = Path(rel).parent
    while parent != Path("."):
        path = root / parent
        if path.is_symlink() or (path.exists() and not path.is_dir()):
            return True
        parent = parent.parent
    return False


def rewrite(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return False
    changed = new_text(text)
    if changed == text:
        return False
    path.write_text(changed, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=".")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    top = git(Path(args.repo), "rev-parse", "--show-toplevel")
    if top.returncode != 0:
        print(f"Not a git repository: {args.repo}")
        return 2
    root = Path(top.stdout.strip())
    pairs, links = plan(root)
    plans = sorted((root / "SDD/implementation").glob("IMPLEMENTATION-PLAN-*.md"))
    to_rewrite = [p for p in plans if REWRITE.search(p.read_text(encoding="utf-8", errors="replace"))]
    if not pairs and not links and not to_rewrite:
        print("Nothing to migrate: no SDD/orchestration/, SDD/reviews/, or superseded slice reviews.")
        return 0

    dests = [new for _, new in pairs]
    folders = {str(parent) for new in dests for parent in Path(new).parents}
    clashes = sorted({new for new in dests if blocked(root, new) or dests.count(new) > 1 or new in folders})
    ignore_rel = "SDD/.records/.gitignore"  # written last, so checked now: a plain file is replaced, anything else refuses
    ignore_path = root / ignore_rel
    if ignore_path.is_symlink() or ignore_path.is_dir() or (not ignore_path.exists() and blocked(root, ignore_rel)):
        clashes.append(ignore_rel)
    links += [p.relative_to(root).as_posix() for p in plans if p.is_symlink()]
    if links:
        print(f"Refused: {len(links)} record(s) are symlinks; move or replace them by hand first. Nothing was changed:")
        for path in links:
            print(f"  {path}")
        return 1
    if clashes:
        print(f"Refused: {len(clashes)} destination(s) are already taken, or claimed twice; nothing was changed:")
        for path in clashes:
            print(f"  {path}")
        return 1

    tracked = set(git(root, "ls-files", "--", *(old for old, _ in MOVES)).stdout.splitlines())
    sources = [old for old, _ in MOVES if (root / old).is_dir()]
    print(f"Move {len(pairs)} file(s) ({len(tracked & {o for o, _ in pairs})} committed, to be untracked):")
    for old, new in MOVES:
        count = sum(1 for o, _ in pairs if o.startswith(old + "/"))
        if count:
            print(f"  {old}/ -> {new}/  ({count})")
    if to_rewrite:
        print("Rewrite old paths in: " + ", ".join(p.relative_to(root).as_posix() for p in to_rewrite))
    if not args.apply:
        print("Dry run: nothing changed. Run again with --apply to migrate.")
        return 0

    committed = sorted(tracked & {o for o, _ in pairs})
    if committed:
        done = git(root, "rm", "--cached", "-q", "--", *committed)
        if done.returncode != 0:
            print(f"Refused: git could not untrack the records; nothing was changed ({done.stderr.strip()[:300]})")
            return 1
    for old, new in pairs:
        dest = root / new
        dest.parent.mkdir(parents=True, exist_ok=True)
        os.replace(root / old, dest)
    for src in sources:
        for folder, _, _ in sorted(os.walk(root / src), key=lambda w: -len(w[0])):
            try:
                Path(folder).rmdir()
            except OSError:
                pass
    ignore = root / "SDD/.records/.gitignore"  # always `*`, even over an old layout's selective one moved here
    ignore.parent.mkdir(parents=True, exist_ok=True)
    ignore.write_text("*\n")
    rewritten = [new for _, new in pairs if rewrite(root / new)] + [p.relative_to(root).as_posix() for p in to_rewrite if rewrite(p)]

    print(f"Migrated: {len(pairs)} file(s) moved to SDD/.records/, {len(committed)} untracked (deletions staged), "
          f"{len(rewritten)} rewritten.")
    print("Nothing is committed. Review `git status`, stage any changed IMPLEMENTATION-PLAN, then commit, e.g.:")
    print('  git commit -m "Move sdd-flow process records to SDD/.records/ (agent-engineering 4.7.0)"')
    gitignore = root / ".gitignore"
    if gitignore.is_file() and re.search(r"SDD/(orchestration|reviews)", gitignore.read_text(errors="replace")):
        print("Note: .gitignore still names SDD/orchestration or SDD/reviews; that line can go.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
