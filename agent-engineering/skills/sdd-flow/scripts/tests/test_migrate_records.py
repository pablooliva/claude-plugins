"""Tests for scripts/migrate-records.py. Run: python3 -m unittest discover -s scripts/tests"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "migrate-records.py"

PROGRESS = """## Flow Started - 001-x
## Review SLICE-001 iter 0 - APPROVED — SDD/reviews/REVIEW-SLICE-SLICE-001-x-iter0-20261101.md
## Slices Superseded — SDD/implementation/slices/superseded/2026-11-02_10-00-00/ (1 file)
## PARTIAL: needs continuation — SDD/orchestration/compacted/implementation-compacted-2026-11-03_09-00-00.md
"""
PLAN = "| SLICE-001 | Complete | passing | SDD/reviews/REVIEW-SLICE-SLICE-001-x-iter0-20261101.md |\n"


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True).stdout


class MigrateRecordsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.email", "t@example.com")
        git(self.root, "config", "user.name", "t")
        self.write("src/app.py", "print(1)\n")
        self.write("SDD/orchestration/progress.md", PROGRESS)
        self.write("SDD/orchestration/counters/4a-1.md", "Reads: 3/15\n")
        self.write("SDD/reviews/REVIEW-SLICE-SLICE-001-x-iter0-20261101.md", "APPROVED\n")
        self.write("SDD/implementation/slices/SLICE-001-01-a-2026-11-01.md", "slice\n")
        self.write("SDD/implementation/slices/superseded/2026-11-02_10-00-00/REVIEW-SLICE-old.md", "old\n")
        self.write("SDD/implementation/IMPLEMENTATION-PLAN-001-x-2026-11-01.md", PLAN)
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "base")
        # an ignored, never-committed record, as an older .gitignore left it
        self.write("SDD/orchestration/subagent-calls/a.md", "call\n")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write(self, rel: str, text: str) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(SCRIPT), "--repo", str(self.root), *args],
                              capture_output=True, text=True)

    def test_dry_run_changes_nothing(self) -> None:
        before = git(self.root, "status", "--porcelain", "--ignored")
        done = self.run_script()
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("Move 5 file(s) (4 committed, to be untracked)", done.stdout)
        self.assertIn("Dry run", done.stdout)
        self.assertEqual(git(self.root, "status", "--porcelain", "--ignored"), before)
        self.assertTrue((self.root / "SDD/orchestration/progress.md").is_file())

    def test_apply_moves_untracks_ignores_and_rewrites(self) -> None:
        done = self.run_script("--apply")
        self.assertEqual(done.returncode, 0, done.stdout)
        records = self.root / "SDD/.records"
        for rel in ("progress.md", "counters/4a-1.md", "subagent-calls/a.md",
                    "reviews/REVIEW-SLICE-SLICE-001-x-iter0-20261101.md",
                    "reviews/superseded/2026-11-02_10-00-00/REVIEW-SLICE-old.md"):
            self.assertTrue((records / rel).is_file(), rel)
        for gone in ("SDD/orchestration", "SDD/reviews", "SDD/implementation/slices/superseded"):
            self.assertFalse((self.root / gone).exists(), gone)
        self.assertTrue((self.root / "SDD/implementation/slices/SLICE-001-01-a-2026-11-01.md").is_file())
        self.assertEqual((records / ".gitignore").read_text(), "*\n")
        # nothing under SDD/.records/ is tracked or shows as untracked
        self.assertEqual(git(self.root, "ls-files", "SDD/.records"), "")
        self.assertNotIn("SDD/.records", git(self.root, "status", "--porcelain"))
        staged = git(self.root, "diff", "--cached", "--name-status")
        self.assertIn("D\tSDD/orchestration/progress.md", staged)
        self.assertIn("D\tSDD/reviews/REVIEW-SLICE-SLICE-001-x-iter0-20261101.md", staged)
        progress = (records / "progress.md").read_text()
        self.assertIn("SDD/.records/reviews/REVIEW-SLICE-SLICE-001-x-iter0-20261101.md", progress)
        self.assertIn("SDD/.records/reviews/superseded/2026-11-02_10-00-00/", progress)
        self.assertIn("SDD/.records/compacted/implementation-compacted-2026-11-03_09-00-00.md", progress)
        self.assertNotRegex(progress, r"SDD/(orchestration|reviews)")
        plan = (self.root / "SDD/implementation/IMPLEMENTATION-PLAN-001-x-2026-11-01.md").read_text()
        self.assertIn("SDD/.records/reviews/REVIEW-SLICE-", plan)
        self.assertEqual(git(self.root, "log", "--oneline").count("\n"), 1)  # never commits

    def test_second_run_finds_nothing(self) -> None:
        self.run_script("--apply")
        done = self.run_script("--apply")
        self.assertEqual(done.returncode, 0)
        self.assertIn("Nothing to migrate", done.stdout)

    def test_clash_refuses_and_changes_nothing(self) -> None:
        self.write("SDD/.records/progress.md", "a 4.7.0 run started here\n")
        done = self.run_script("--apply")
        self.assertEqual(done.returncode, 1)
        self.assertIn("SDD/.records/progress.md", done.stdout)
        self.assertTrue((self.root / "SDD/orchestration/progress.md").is_file())
        self.assertEqual(git(self.root, "diff", "--cached", "--name-only"), "")

    def test_destination_folder_taken_by_a_file_refuses_and_changes_nothing(self) -> None:
        self.write("SDD/.records/reviews", "a file where a folder is needed\n")
        done = self.run_script("--apply")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertTrue((self.root / "SDD/orchestration/progress.md").is_file())
        self.assertFalse((self.root / "SDD/.records/progress.md").exists())
        self.assertEqual(git(self.root, "diff", "--cached", "--name-only"), "")

    def test_old_selective_ignore_file_is_dropped_and_everything_stays_ignored(self) -> None:
        self.write("SDD/orchestration/.gitignore", "subagent-calls/\n")
        git(self.root, "add", "SDD/orchestration/.gitignore")
        git(self.root, "commit", "-q", "-m", "old ignore")
        done = self.run_script("--apply")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertEqual((self.root / "SDD/.records/.gitignore").read_text(), "*\n")
        self.assertFalse((self.root / "SDD/orchestration").exists())
        self.assertIn("D\tSDD/orchestration/.gitignore", git(self.root, "diff", "--cached", "--name-status"))
        self.assertNotIn("SDD/.records", git(self.root, "status", "--porcelain", "--untracked-files=all"))

    def test_two_records_claiming_one_destination_refuse(self) -> None:
        self.write("SDD/reviews/superseded/2026-11-02_10-00-00/REVIEW-SLICE-old.md", "other\n")
        done = self.run_script("--apply")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("SDD/.records/reviews/superseded/2026-11-02_10-00-00/REVIEW-SLICE-old.md", done.stdout)
        self.assertTrue((self.root / "SDD/reviews/superseded/2026-11-02_10-00-00/REVIEW-SLICE-old.md").is_file())
        self.assertEqual(git(self.root, "diff", "--cached", "--name-only"), "")

    def test_symlinked_record_refuses_and_its_target_is_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / "notes.md"
            target.write_text("see SDD/reviews/x.md\n")
            (self.root / "SDD/reviews/link.md").symlink_to(target)
            done = self.run_script("--apply")
            self.assertEqual(done.returncode, 1, done.stdout)
            self.assertIn("SDD/reviews/link.md", done.stdout)
            self.assertEqual(target.read_text(), "see SDD/reviews/x.md\n")
        self.assertTrue((self.root / "SDD/orchestration/progress.md").is_file())

    def test_symlinked_record_folder_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as outside:
            (self.root / "SDD/orchestration/compacted").symlink_to(outside, target_is_directory=True)
            done = self.run_script("--apply")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("SDD/orchestration/compacted", done.stdout)
        self.assertTrue((self.root / "SDD/orchestration/progress.md").is_file())

    def test_ignore_file_that_is_a_symlink_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / "keep"
            target.write_text("mine\n")
            (self.root / "SDD/.records").mkdir()
            (self.root / "SDD/.records/.gitignore").symlink_to(target)
            done = self.run_script("--apply")
            self.assertEqual(done.returncode, 1, done.stdout)
            self.assertEqual(target.read_text(), "mine\n")
        self.assertTrue((self.root / "SDD/orchestration/progress.md").is_file())
        self.assertEqual(git(self.root, "diff", "--cached", "--name-only"), "")

    def test_not_a_repository(self) -> None:
        with tempfile.TemporaryDirectory() as other:
            done = subprocess.run([sys.executable, str(SCRIPT), "--repo", other], capture_output=True, text=True)
        self.assertEqual(done.returncode, 2)


if __name__ == "__main__":
    unittest.main()
