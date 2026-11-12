"""Tests for scripts/growth.py. Run: python3 -m unittest discover -s scripts/tests"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "growth.py"

BRIEF = """# DESIGN-001-x

## What changes where
| Area (path or path prefix) | New or changed | Lines added (estimate) | What changes |
|---|---|---|---|
| `src/app.py` | Changed | 10 | more |
| `src/page.js` | New | 20 | the page |
| `tests/test_page.py` | New | 20 | its tests |

## Growth budget
- Source lines added: ~{source}
- Test lines added: ~{tests}
- New files: 2

## Tiers
"""


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True).stdout


def lines(n: int) -> str:
    return "".join(f"line {i}\n" for i in range(n))


class GrowthTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.email", "t@example.com")
        git(self.root, "config", "user.name", "t")
        (self.root / "src").mkdir()
        (self.root / "src" / "app.py").write_text(lines(5), encoding="utf-8")
        git(self.root, "add", ".")
        git(self.root, "commit", "-q", "-m", "base")
        self.base = git(self.root, "rev-parse", "HEAD").strip()
        (self.root / "SDD" / "requirements").mkdir(parents=True)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def brief(self, source: int = 30, tests: int = 20) -> None:
        (self.root / "SDD/requirements/DESIGN-001-x.md").write_text(BRIEF.format(source=source, tests=tests), encoding="utf-8")

    def run_growth(self) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--base", self.base, "--brief", "SDD/requirements/DESIGN-001-x.md", "--repo", str(self.root)],
            capture_output=True, text=True,
        )

    def test_within_budget_counts_committed_and_untracked_work(self) -> None:
        self.brief()
        (self.root / "src/app.py").write_text(lines(15), encoding="utf-8")  # +10, uncommitted
        (self.root / "src/page.js").write_text(lines(20), encoding="utf-8")
        git(self.root, "add", "src/page.js")
        git(self.root, "commit", "-q", "-m", "page")
        (self.root / "tests").mkdir()
        (self.root / "tests/test_page.py").write_text(lines(25), encoding="utf-8")  # untracked
        out = self.run_growth()
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertIn("Growth: source +30 of ~30 (1.0x), tests +25 of ~20 (1.2x), new files 2 of 2", out.stdout)
        self.assertIn("Unnamed new files: none", out.stdout)
        self.assertIn("Over budget: no", out.stdout)

    def test_test_lines_over_one_and_a_half_times_are_over_budget(self) -> None:
        self.brief(tests=20)
        (self.root / "tests").mkdir()
        (self.root / "tests/test_page.py").write_text(lines(31), encoding="utf-8")
        out = self.run_growth()
        self.assertIn("tests +31 of ~20 (1.6x)", out.stdout)
        self.assertIn("Over budget: yes", out.stdout)

    def test_a_new_file_under_an_area_but_not_named_is_reported(self) -> None:
        self.brief()
        (self.root / "src/helpers.py").write_text(lines(3), encoding="utf-8")
        out = self.run_growth()
        self.assertIn("Unnamed new files: src/helpers.py", out.stdout)

    def test_non_ascii_file_names_are_counted_and_matched(self) -> None:
        brief = BRIEF.format(source=30, tests=20).replace("`src/page.js`", "`src/página.js`")
        (self.root / "SDD/requirements/DESIGN-001-x.md").write_text(brief, encoding="utf-8")
        (self.root / "src/página.js").write_text(lines(20), encoding="utf-8")  # untracked
        (self.root / "src/añadido.py").write_text(lines(4), encoding="utf-8")
        git(self.root, "add", "src/añadido.py")
        git(self.root, "commit", "-q", "-m", "added")
        out = self.run_growth()
        self.assertIn("source +24 of ~30", out.stdout)
        self.assertIn("Unnamed new files: src/añadido.py", out.stdout)

    def test_sdd_files_are_left_out(self) -> None:
        self.brief()
        (self.root / "SDD/notes.md").write_text(lines(500), encoding="utf-8")
        out = self.run_growth()
        self.assertIn("source +0 of ~30", out.stdout)
        self.assertIn("Unnamed new files: none", out.stdout)

    def test_zero_estimate_with_lines_added_is_over(self) -> None:
        self.brief(source=0)
        (self.root / "src/app.py").write_text(lines(6), encoding="utf-8")
        out = self.run_growth()
        self.assertIn("source +1 of ~0 (inf)", out.stdout)
        self.assertIn("Over budget: yes", out.stdout)

    def test_no_budget_section_exits_3(self) -> None:
        (self.root / "SDD/requirements/DESIGN-001-x.md").write_text("# DESIGN\n\n## Tiers\n", encoding="utf-8")
        out = self.run_growth()
        self.assertEqual(out.returncode, 3)
        self.assertTrue(out.stdout.startswith("Result: NO BUDGET"))

    def test_test_file_classification(self) -> None:
        sys.path.insert(0, str(SCRIPT.parent))
        try:
            import growth
        finally:
            sys.path.pop(0)
        for path in ("tests/x.py", "pkg/tests/a/b.py", "src/test_a.py", "a_test.go", "page.test.js", "x.spec.ts", "conftest.py", "web/__tests__/a.js"):
            self.assertTrue(growth.is_test(path), path)
        for path in ("src/app.py", "src/testing_utils.py", "contest.py", "src/attest.py"):
            self.assertFalse(growth.is_test(path), path)


if __name__ == "__main__":
    unittest.main()
