"""Tests for scripts/snapshot.py. Run: python3 -m unittest discover -s scripts/tests"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "snapshot.py"


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True).stdout


class SnapshotTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        self.root.mkdir()
        git(self.root, "init", "-q")
        git(self.root, "config", "user.email", "t@example.com")
        git(self.root, "config", "user.name", "t")
        (self.root / "app.py").write_text("def f():\n    return 1\n", encoding="utf-8")
        (self.root / ".gitignore").write_text("secret.env\n", encoding="utf-8")
        git(self.root, "add", ".")
        git(self.root, "commit", "-q", "-m", "base")
        self.base = git(self.root, "rev-parse", "HEAD").strip()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_script(self, *args: str, root: Path | None = None) -> str:
        r = subprocess.run([sys.executable, str(SCRIPT), *args], cwd=root or self.root,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def state(self) -> list[str]:
        return [git(self.root, *a) for a in (("rev-parse", "HEAD"), ("ls-files", "-s"), ("status", "--porcelain"),
                                             ("stash", "list"), ("for-each-ref",))]

    def test_snapshot_holds_the_working_tree_and_touches_nothing(self) -> None:
        (self.root / "app.py").write_text("def f():\n    raise ValueError\n", encoding="utf-8")
        (self.root / "new.py").write_text("x = 1\n", encoding="utf-8")
        (self.root / "secret.env").write_text("KEY=1\n", encoding="utf-8")
        before = self.state()
        sha = self.run_script()
        self.assertEqual(before, self.state())
        self.assertEqual(git(self.root, "rev-parse", f"{sha}^").strip(), self.base)
        files = git(self.root, "ls-tree", "-r", "--name-only", sha).split()
        self.assertIn("new.py", files)  # untracked: kept
        self.assertNotIn("secret.env", files)  # git-ignored: left out
        self.assertIn("raise ValueError", git(self.root, "show", f"{sha}:app.py"))
        self.assertEqual(git(self.root, "for-each-ref", "--contains", sha), "")

    def test_two_snapshots_diff_to_what_changed_between_them(self) -> None:
        first = self.run_script()
        (self.root / "app.py").write_text("def f():\n    return 2\n", encoding="utf-8")
        second = self.run_script()
        self.assertEqual(git(self.root, "diff", "--name-only", first, second).split(), ["app.py"])

    def test_snapshot_in_a_repo_with_no_commits_has_no_parent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            git(root, "init", "-q")
            (root / "a.py").write_text("def f():\n    return 1\n", encoding="utf-8")
            sha = self.run_script(root=root)
            self.assertNotIn("parent ", git(root, "cat-file", "-p", sha))
            self.assertIn("a.py", git(root, "ls-tree", "--name-only", sha))

    def test_scratch_copies_uncommitted_and_ignored_files_outside_the_repository(self) -> None:
        (self.root / "app.py").write_text("def f():\n    return 3\n", encoding="utf-8")
        (self.root / "new.py").write_text("x = 1\n", encoding="utf-8")
        (self.root / "secret.env").write_text("KEY=1\n", encoding="utf-8")
        before = self.state()
        copy = Path(self.run_script("scratch"))
        try:
            self.assertFalse(copy.resolve().is_relative_to(self.root.resolve()))
            self.assertEqual((copy / "app.py").read_text(encoding="utf-8"), "def f():\n    return 3\n")
            self.assertTrue((copy / "new.py").exists())
            self.assertTrue((copy / "secret.env").exists())
            self.assertFalse((copy / ".git").exists())
            (copy / "app.py").write_text("broken\n", encoding="utf-8")
            self.assertEqual((self.root / "app.py").read_text(encoding="utf-8"), "def f():\n    return 3\n")
            self.assertEqual(before, self.state())
        finally:
            shutil.rmtree(copy.parent)

    def test_scratch_links_never_lead_back_to_the_original(self) -> None:
        with tempfile.TemporaryDirectory() as outside:
            data = Path(outside) / "local.db"
            data.write_text("original\n", encoding="utf-8")
            (self.root / "db.sqlite").symlink_to(data)  # absolute, outside the repository
            (self.root / "alias.py").symlink_to(self.root / "app.py")  # absolute, inside
            (self.root / "gone").symlink_to(Path(outside) / "missing")  # dangling
            copy = Path(self.run_script("scratch"))
            try:
                self.assertFalse((copy / "db.sqlite").is_symlink())
                (copy / "db.sqlite").write_text("mutated\n", encoding="utf-8")
                self.assertEqual(data.read_text(encoding="utf-8"), "original\n")
                self.assertTrue((copy / "alias.py").is_symlink())
                self.assertEqual((copy / "alias.py").resolve(), (copy / "app.py").resolve())
                (copy / "alias.py").write_text("broken\n", encoding="utf-8")
                self.assertEqual((self.root / "app.py").read_text(encoding="utf-8"), "def f():\n    return 1\n")
                self.assertFalse(os.path.lexists(copy / "gone"))
            finally:
                shutil.rmtree(copy.parent)

    def test_unknown_argument_is_an_error(self) -> None:
        r = subprocess.run([sys.executable, str(SCRIPT), "--base"], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
