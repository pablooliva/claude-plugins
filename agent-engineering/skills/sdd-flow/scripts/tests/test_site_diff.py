"""Tests for scripts/site-diff.py. Run: python3 -m unittest discover -s scripts/tests"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "site-diff.py"
HEAD = ("| Control | File | Symbol | Kind | Path class | Site description | Disposition | Evidence | Slice |\n"
        "|---|---|---|---|---|---|---|---|---|\n")


def impl_row(control: str, file: str, symbol: str, slice_id: str, kind: str = "site") -> str:
    return f"| {control} | {file} | {symbol} | {kind} | — | desc | (i) | mutation: x → failing test t | {slice_id} |\n"


def blind_row(control: str, file: str, symbol: str, kind: str = "site") -> str:
    return f"| {control} | {file} | {symbol} | {kind} | — | desc | — | — | — |\n"


def inventory(rows: list[str], declared: list[tuple[str, str, str]] | None = None) -> str:
    text = "# Inventory\n\n## Site Inventory\n\n" + HEAD + "".join(rows)
    if declared:
        text += "\n## Declared Scope\n\n| Control | File | Symbol |\n|---|---|---|\n"
        text += "".join(f"| {c} | {f} | {s} |\n" for c, f, s in declared)
    return text


class Repo:
    """A throwaway git repo: `base` is committed, then the slice edits the working tree."""

    BASE_FILES = {
        "app/registry.py": """\
            REGISTRY = {"a": 1}


            def lookup(k):
                if k not in REGISTRY:
                    raise KeyError(k)
                return REGISTRY[k]


            def validate(k):
                return k in REGISTRY
            """,
        "app/groups.py": """\
            def _group_payload(g):
                return {"g": g}


            def _legacy_group(g):
                if not g:
                    raise ValueError
                return g
            """,
    }

    def __init__(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        for name, body in self.BASE_FILES.items():
            self.write(name, body)
        self.git("init", "-q")
        self.git("add", ".")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base")
        self.base = self.git("rev-parse", "HEAD").strip()
        # The slice: changes _group_payload, adds an untracked module.
        self.write("app/groups.py", textwrap.dedent(self.BASE_FILES["app/groups.py"]).replace(
            'return {"g": g}', 'if g is None:\n        raise ValueError\n    return {"g": g}'))
        self.write("app/export.py", """\
            def run(path):
                if not path:
                    return 2
                return 0
            """)

    def write(self, name: str, body: str) -> None:
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(textwrap.dedent(body), encoding="utf-8")

    def git(self, *args: str) -> str:
        return subprocess.run(["git", *args], cwd=self.root, check=True,
                              capture_output=True, text=True).stdout

    def close(self) -> None:
        self._tmp.cleanup()


def run_diff(cwd: Path, impl: str, blind: str, scope: str, base: str | None = None,
             script: Path = SCRIPT) -> tuple[int, str, str]:
    (cwd / "impl.md").write_text(impl, encoding="utf-8")
    (cwd / "blind.md").write_text(blind, encoding="utf-8")
    cmd = [sys.executable, str(script), "impl.md", "blind.md", "out.md", "--scope", scope]
    if base:
        cmd += ["--base", base]
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    out = (cwd / "out.md").read_text(encoding="utf-8") if (cwd / "out.md").exists() else ""
    return r.returncode, r.stdout.strip() + r.stderr.strip(), out


class NoGitCases(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_lettered_scope_accepted(self) -> None:
        inv = inventory([impl_row("D-10", "a.py", "run", "SLICE-005a")])
        code, line, out = run_diff(self.dir, inv, inventory([blind_row("D-10", "a.py", "run")]), "SLICE-005a")
        self.assertEqual((code, line), (0, "Result: MATCH"))
        self.assertIn("# Site Diff — SLICE-005a", out)

    def test_bad_scopes_rejected(self) -> None:
        inv = inventory([])
        for scope in ("SLICE-5", "SLICE-005ab", "SLICE-005A", "SLICE-005/../x", "slice-005"):
            code, _, _ = run_diff(self.dir, inv, inv, scope)
            self.assertEqual(code, 2, scope)

    def test_escaped_module_keys_equal_to_plain(self) -> None:
        impl = inventory([impl_row("REQ-005", "app/registry.py", "<module>", "SLICE-004")])
        blind = inventory([blind_row("REQ-005", "app/registry.py", r"\<module\>")])
        self.assertEqual(run_diff(self.dir, impl, blind, "SLICE-004")[:2], (0, "Result: MATCH"))

    def test_backticks_and_underscore_escapes_normalised(self) -> None:
        impl = inventory([impl_row("REQ-019", "app/groups.py", "_group_payload", "SLICE-004")])
        blind = inventory([blind_row("REQ-019", "`app/groups.py`", r"`\_group\_payload`")])
        self.assertEqual(run_diff(self.dir, impl, blind, "SLICE-004")[:2], (0, "Result: MATCH"))

    def test_legacy_inventory_parses(self) -> None:
        """A 2.6.1 inventory (nine columns, no Declared Scope) diffs as before."""
        impl = inventory([impl_row("D-10", "src/cli/main.py", "run", "SLICE-002"),
                          impl_row("D-10", "src/cli/main.py", "run", "SLICE-002")])
        blind = inventory([blind_row("D-10", "src/cli/main.py", "run")])
        code, line, out = run_diff(self.dir, impl, blind, "SLICE-002")
        self.assertEqual((code, line), (1, "Result: MISMATCH (0 HIGH, 1 MEDIUM)"))
        self.assertIn("MEDIUM — EXTRA `D-10` at `src/cli/main.py` `run`", out)

    def test_without_base_nothing_is_carried(self) -> None:
        impl = inventory([impl_row("D-10", "a.py", "run", "SLICE-003")])
        blind = inventory([blind_row("D-10", "a.py", "run"), blind_row("D-10", "a.py", "other")])
        code, line, out = run_diff(self.dir, impl, blind, "SLICE-003")
        self.assertEqual(line, "Result: MISMATCH (1 HIGH, 0 MEDIUM)")
        self.assertNotIn("## Carried", out)

    def test_feature_scope_rejects_base(self) -> None:
        inv = inventory([])
        self.assertEqual(run_diff(self.dir, inv, inv, "FEATURE", base="HEAD")[0], 2)

    def test_feature_scope_declared_scope_is_medium_and_compares_fully(self) -> None:
        impl = inventory([impl_row("REQ-019", "app/groups.py", "_group_payload", "—"),
                          impl_row("REQ-019", "app/groups.py", "_legacy_group", "—")])
        blind = inventory([blind_row("REQ-019", "app/groups.py", "_group_payload")],
                          declared=[("REQ-019", "app/groups.py", "_group_payload")])
        code, line, out = run_diff(self.dir, impl, blind, "FEATURE")
        self.assertEqual(line, "Result: MISMATCH (0 HIGH, 2 MEDIUM)")
        self.assertIn("PARTIAL COUNT `REQ-019`", out)
        self.assertIn("EXTRA `REQ-019` at `app/groups.py` `_legacy_group`", out)


class GitCases(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = Repo()

    def tearDown(self) -> None:
        self.repo.close()

    def diff(self, impl: str, blind: str, scope: str = "SLICE-005a", base: str | None = "repo") -> tuple[int, str, str]:
        return run_diff(self.repo.root, impl, blind, scope, self.repo.base if base == "repo" else base)

    def test_carried_row_reported_in_its_own_section(self) -> None:
        impl = inventory([impl_row("REQ-005", "app/registry.py", "lookup", "SLICE-001a")])
        blind = inventory([blind_row("REQ-005", "app/registry.py", "lookup"),
                           blind_row("REQ-005", "app/registry.py", "validate")])
        code, line, out = self.diff(impl, blind)
        self.assertEqual(code, 0)
        self.assertEqual(line, "Result: MATCH (1 LOW carried or out-of-scope, owed to the FEATURE recount)")
        self.assertIn("| REQ-005 | 1 | 2 | CARRIED |", out)
        carried = out.split("## Carried (owed to the FEATURE recount)")[1]
        self.assertIn("LOW — CARRIED `REQ-005` at `app/registry.py` `validate`", carried)
        self.assertNotIn("MISSED", out)

    def test_changed_symbol_in_touched_file_is_owned(self) -> None:
        impl = inventory([impl_row("REQ-019", "app/groups.py", "_group_payload", "SLICE-005a")])
        blind = inventory([blind_row("REQ-019", "app/groups.py", "_group_payload"),
                           blind_row("REQ-019", "app/groups.py", "_group_payload")])
        self.assertEqual(self.diff(impl, blind)[1], "Result: MISMATCH (1 HIGH, 0 MEDIUM)")

    def test_unchanged_symbol_in_touched_file_is_carried(self) -> None:
        impl = inventory([])
        blind = inventory([blind_row("REQ-019", "app/groups.py", "_legacy_group")])
        self.assertEqual(self.diff(impl, blind)[0], 0)

    def test_module_symbol_in_touched_file_is_owned(self) -> None:
        impl = inventory([])
        blind = inventory([blind_row("REQ-019", "app/groups.py", "<module>")])
        self.assertEqual(self.diff(impl, blind)[1], "Result: MISMATCH (1 HIGH, 0 MEDIUM)")

    def test_untracked_file_is_owned(self) -> None:
        impl = inventory([impl_row("D-10", "app/export.py", "run", "SLICE-005a")])
        blind = inventory([blind_row("D-10", "app/export.py", "run"), blind_row("D-10", "app/export.py", "run")])
        self.assertEqual(self.diff(impl, blind)[1], "Result: MISMATCH (1 HIGH, 0 MEDIUM)")

    def test_new_gitignored_file_is_owned(self) -> None:
        self.repo.write(".gitignore", "generated/\n")
        self.repo.write("generated/handlers.py", "def handle(req):\n    return req\n")
        impl = inventory([])
        blind = inventory([blind_row("D-10", "generated/handlers.py", "handle")])
        self.assertEqual(self.diff(impl, blind)[1], "Result: MISMATCH (1 HIGH, 0 MEDIUM)")

    def test_stale_row_for_missing_file_is_never_carried(self) -> None:
        impl = inventory([impl_row("D-10", "app/gone.py", "run", "SLICE-001a")])
        blind = inventory([blind_row("D-10", "app/export.py", "run")])
        code, line, out = self.diff(impl, blind)
        self.assertIn("EXTRA `D-10` at `app/gone.py` `run`", out)

    def test_declared_scope_sets_aside_out_of_scope_impl_rows(self) -> None:
        impl = inventory([impl_row("REQ-019", "app/groups.py", "_group_payload", "SLICE-005a"),
                          impl_row("REQ-019", "app/groups.py", "_legacy_group", "SLICE-002")])
        blind = inventory([blind_row("REQ-019", "app/groups.py", "_group_payload")],
                          declared=[("REQ-019", "app/groups.py", "_group_payload")])
        code, line, out = self.diff(impl, blind)
        self.assertEqual(code, 0)
        self.assertIn("| REQ-019 | 1 | 1 | OUT-OF-SCOPE-BY-DECLARED-SCOPE |", out)
        self.assertIn("LOW — OUT-OF-SCOPE-BY-DECLARED-SCOPE `REQ-019` at `app/groups.py` `_legacy_group`", out)
        self.assertNotIn("EXTRA", out)

    def test_declared_scope_over_changed_code_is_medium(self) -> None:
        impl = inventory([impl_row("REQ-019", "app/groups.py", "_group_payload", "SLICE-005a"),
                          impl_row("REQ-019", "app/export.py", "run", "SLICE-005a")])
        blind = inventory([blind_row("REQ-019", "app/groups.py", "_group_payload")],
                          declared=[("REQ-019", "app/groups.py", "*")])
        code, line, out = self.diff(impl, blind)
        self.assertEqual(line, "Result: MISMATCH (0 HIGH, 1 MEDIUM)")
        self.assertIn("MEDIUM — OUT-OF-SCOPE-BY-DECLARED-SCOPE `REQ-019` at `app/export.py` `run`", out)

    def test_feature_scope_counts_carried_rows_normally(self) -> None:
        impl = inventory([impl_row("REQ-005", "app/registry.py", "lookup", "SLICE-001a")])
        blind = inventory([blind_row("REQ-005", "app/registry.py", "lookup"),
                           blind_row("REQ-005", "app/registry.py", "validate")])
        self.assertEqual(self.diff(impl, blind, scope="FEATURE", base=None)[1],
                         "Result: MISMATCH (1 HIGH, 0 MEDIUM)")

    def test_base_none_treats_everything_as_changed(self) -> None:
        impl = inventory([])
        blind = inventory([blind_row("REQ-005", "app/registry.py", "validate")])
        self.assertEqual(self.diff(impl, blind, base="none")[1], "Result: MISMATCH (1 HIGH, 0 MEDIUM)")

    def test_bad_base_is_input_error(self) -> None:
        inv = inventory([])
        self.assertEqual(self.diff(inv, inv, base="no-such-commit")[0], 2)

    # --- The worked example: a SLICE-005a-shaped diff ---------------------------------------

    IMPL_005A = [
        impl_row("REQ-005", "app/registry.py", "<module>", "SLICE-001a"),
        impl_row("REQ-005", "app/registry.py", "lookup", "SLICE-001a"),
        impl_row("REQ-019", "app/groups.py", "_group_payload", "SLICE-005a"),
        impl_row("REQ-019", "app/groups.py", "_legacy_group", "SLICE-002"),
        impl_row("D-10", "app/export.py", "run", "SLICE-005a"),
    ]
    BLIND_005A = [
        blind_row("REQ-005", "app/registry.py", r"\<module\>"),          # escaped symbol
        blind_row("REQ-005", "app/registry.py", "lookup"),
        blind_row("REQ-005", "app/registry.py", "lookup"),               # carried disagreement
        blind_row("REQ-005", "app/registry.py", "validate"),             # carried, never inventoried
        blind_row("REQ-019", "app/groups.py", "_group_payload"),
        blind_row("D-10", "app/export.py", "run"),
    ]
    DECLARED_005A = [("REQ-019", "app/groups.py", "_group_payload")]

    def test_worked_example_slice_005a_zero_high(self) -> None:
        code, line, out = self.diff(inventory(self.IMPL_005A),
                                    inventory(self.BLIND_005A, declared=self.DECLARED_005A))
        self.assertEqual(code, 0, out)
        self.assertEqual(line, "Result: MATCH (3 LOW carried or out-of-scope, owed to the FEATURE recount)")

    def test_worked_example_genuine_owned_miss_is_one_high(self) -> None:
        blind = self.BLIND_005A + [blind_row("D-10", "app/export.py", "run")]
        code, line, out = self.diff(inventory(self.IMPL_005A), inventory(blind, declared=self.DECLARED_005A))
        self.assertEqual(line, "Result: MISMATCH (1 HIGH, 0 MEDIUM) + 3 LOW")
        self.assertIn("HIGH — MISSED `D-10` at `app/export.py` `run`", out)


if __name__ == "__main__":
    unittest.main()
