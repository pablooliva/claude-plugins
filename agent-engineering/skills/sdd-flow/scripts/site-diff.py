#!/usr/bin/env python3
"""Diff an implementer's enforcement-site inventory against a blind count.

Usage:
    site-diff.py <impl-inventory.md> <blind-count.md> <out.md> --scope <SLICE-XXX|FEATURE>
                 [--base <commit|none>]

Both inputs carry a `## Site Inventory` table in the shape defined by
`references/enforcement-sites.md` §4. Rows of Kind `site` are counted per
Control + File + Symbol on each side (Markdown backslash-escapes and wrapping
backticks are normalised away first); blind-count `gap` rows are reported as
findings. The result is written to <out.md> and its first line is echoed.

--base (SLICE scope only): the slice's base commit. A key whose code the slice
did not change (per `git diff <base>` of the working tree, untracked files
counting as changed) is *carried*: a disagreement there is reported LOW in its
own section, owed to the FEATURE recount, never as MISSED/EXTRA. Anything the
script cannot place with certainty is treated as changed.

A blind count may declare partial scope for a control in an optional
`## Declared Scope` table (Control | File | Symbol, `*` = whole file). At SLICE
scope, implementer rows outside it are set aside as OUT-OF-SCOPE-BY-DECLARED-SCOPE
(LOW if carried, MEDIUM otherwise). At FEATURE scope a declaration is itself a
MEDIUM finding and the comparison stays complete.

Exit status: 0 = MATCH, 1 = MISMATCH, 2 = usage or input error.
Deterministic: no judgment, no network, stdlib only (plus local `git` with --base).
"""
from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

HEADER = "## Site Inventory"
SCOPE_HEADER = "## Declared Scope"
COLUMNS = ["control", "file", "symbol", "kind", "path class",
           "site description", "disposition", "evidence", "slice"]
SCOPE_COLUMNS = ["control", "file", "symbol"]
SCOPE_RE = re.compile(r"^(SLICE-\d{3}[a-z]?|FEATURE)$")
CELL_SPLIT = re.compile(r"(?<!\\)\|")  # split on | not preceded by a backslash
MD_ESCAPE = re.compile(r"\\([\\<>_*`\[\]#])")
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")

Key = tuple[str, str, str]


def fail(msg: str) -> None:
    print(f"site-diff: {msg}", file=sys.stderr)
    sys.exit(2)


def norm(cell: str) -> str:
    """`\\<module\\>`, `` `<module>` `` and `<module>` all key as `<module>`."""
    cell = MD_ESCAPE.sub(r"\1", cell).strip()
    if len(cell) >= 2 and cell[0] == cell[-1] == "`":
        cell = cell[1:-1].strip()
    return cell


def read_table(path: Path, section: str, columns: list[str], required: bool) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    in_section = False
    header: list[str] | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line == section:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section or not line.startswith("|"):
            continue
        cells = [c.strip().replace("\\|", "|") for c in CELL_SPLIT.split(line.strip("|"))]
        if header is None:
            header = [c.lower() for c in cells]
            if header != columns:
                fail(f"{path}: `{section}` columns must be {columns}, got {header}")
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue  # separator row
        if len(cells) != len(columns):
            fail(f"{path}: row has {len(cells)} cells, expected {len(columns)} "
                 f"(escape a literal pipe as \\|): {raw}")
        row = dict(zip(columns, cells))
        for col in ("control", "file", "symbol"):
            row[col] = norm(row[col])
        row["file"] = row["file"].removeprefix("./")
        rows.append(row)
    if required and header is None:
        fail(f"{path}: no `{section}` table found")
    return rows


def parse_inventory(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        fail(f"inventory not found: {path}")
    rows = read_table(path, HEADER, COLUMNS, required=True)
    for row in rows:
        row["kind"] = row["kind"].lower()
        if row["kind"] not in ("site", "gap"):
            fail(f"{path}: Kind must be `site` or `gap`: {row}")
    return rows


def key(row: dict[str, Any]) -> Key:
    return (row["control"], row["file"], row["symbol"])


def git(cwd: Path | None, *args: str) -> str:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        fail(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout


class ChangeMap:
    """Which File + Symbol locations the working tree changed relative to --base."""

    def __init__(self, base: str) -> None:
        self.root = Path(git(None, "rev-parse", "--show-toplevel").strip())
        if base == "none":
            base = git(self.root, "hash-object", "-t", "tree", "/dev/null").strip()
        git(self.root, "rev-parse", "--verify", f"{base}^{{tree}}")
        self.base = base
        self.files = set(git(self.root, "diff", "--name-only", base, "--").splitlines())
        self.untracked = set(git(self.root, "ls-files", "--others", "--exclude-standard").splitlines())
        self.at_base = set(git(self.root, "ls-tree", "-r", "--name-only", base).splitlines())
        self._lines: dict[str, set[int]] = {}
        self._span_cache: dict[str, dict[str, list[tuple[int, int]]] | None] = {}

    def _changed_lines(self, file: str) -> set[int]:
        if file in self._lines:
            return self._lines[file]
        lines = self._lines[file] = set()
        for ln in git(self.root, "diff", "-U0", self.base, "--", file).splitlines():
            m = HUNK.match(ln)
            if not m:
                continue
            start, count = int(m.group(1)), int(m.group(2) or "1")
            # A pure deletion sits between `start` and `start + 1`.
            lines.update(range(start, start + count) if count else (start, start + 1))
        return lines

    def changed(self, file: str, symbol: str) -> bool:
        """True unless the location is certainly untouched since --base."""
        if not (self.root / file).is_file():
            return True  # stale or mis-pathed row: never hide it as carried
        if file in self.untracked or file not in self.at_base:
            return True  # new since base (including git-ignored files): nothing to be carried from
        if file not in self.files:
            return False
        if symbol == "<module>" or not file.endswith(".py"):
            return True
        spans = self._spans(file)
        if spans is None:
            return True
        name = symbol.removesuffix("()")
        if name not in spans:
            return True
        lines = self._changed_lines(file)
        return any(a <= n <= b for a, b in spans[name] for n in lines)

    def _spans(self, file: str) -> dict[str, list[tuple[int, int]]] | None:
        if file not in self._span_cache:
            self._span_cache[file] = self._parse_spans(file)
        return self._span_cache[file]

    def _parse_spans(self, file: str) -> dict[str, list[tuple[int, int]]] | None:
        try:
            tree = ast.parse((self.root / file).read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError, ValueError):
            return None
        spans: dict[str, list[tuple[int, int]]] = {}

        def visit(node: ast.AST, prefix: str) -> None:
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    qual = f"{prefix}.{child.name}" if prefix else child.name
                    start = min([child.lineno] + [d.lineno for d in child.decorator_list])
                    span = (start, child.end_lineno or child.lineno)
                    spans.setdefault(qual, []).append(span)
                    if qual != child.name:  # the standard names nested functions bare
                        spans.setdefault(child.name, []).append(span)
                    visit(child, qual)
                else:
                    visit(child, prefix)

        visit(tree, "")
        return spans


def in_declared(row: dict[str, Any], declared: list[dict[str, Any]]) -> bool:
    return any(d["file"] == row["file"] and d["symbol"] in ("*", row["symbol"]) for d in declared)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("impl")
    ap.add_argument("blind")
    ap.add_argument("out")
    ap.add_argument("--scope", required=True)
    ap.add_argument("--base")
    a = ap.parse_args()
    if not SCOPE_RE.match(a.scope):
        fail(f"--scope must match SLICE-### (optionally one lowercase letter) or FEATURE, got {a.scope!r}")
    if a.base and a.scope == "FEATURE":
        fail("--base applies only to a SLICE scope; a FEATURE diff compares every row")
    feature = a.scope == "FEATURE"

    impl = parse_inventory(Path(a.impl))
    blind = parse_inventory(Path(a.blind))
    declared_rows = read_table(Path(a.blind), SCOPE_HEADER, SCOPE_COLUMNS, required=False)
    declared: dict[str, list[dict[str, Any]]] = {}
    for d in declared_rows:
        declared.setdefault(d["control"], []).append(d)
    changes = ChangeMap(a.base) if a.base else None

    def carried(k: Key) -> bool:
        return changes is not None and not changes.changed(k[1], k[2])

    blind_controls = {r["control"] for r in blind} | set(declared)
    if feature:
        in_scope = blind_controls | {r["control"] for r in impl}
    else:
        in_scope = blind_controls | {r["control"] for r in impl if r["slice"] == a.scope}
    impl_controls = {r["control"] for r in impl if r["control"] in in_scope}

    impl_kept: list[dict[str, Any]] = []
    out_of_scope: list[tuple[dict[str, Any], bool]] = []  # (row, carried)
    for r in impl:
        if r["kind"] != "site" or r["control"] not in in_scope:
            continue
        if not feature and r["control"] in declared and not in_declared(r, declared[r["control"]]):
            out_of_scope.append((r, carried(key(r))))
        else:
            impl_kept.append(r)

    impl_sites = Counter(key(r) for r in impl_kept)
    blind_sites = Counter(key(r) for r in blind if r["kind"] == "site")

    gaps = [r for r in blind if r["kind"] == "gap"]
    per_control: dict[str, dict[str, Any]] = {
        c: {"impl": 0, "blind": 0, "missed": [], "extra": [], "carried": [], "oos": []}
        for c in sorted(in_scope)
    }
    for k in sorted(set(impl_sites) | set(blind_sites)):
        i, b = impl_sites.get(k, 0), blind_sites.get(k, 0)
        pc = per_control[k[0]]
        pc["impl"] += i
        pc["blind"] += b
        if i == b:
            continue
        if carried(k):
            pc["carried"].append((k, i, b))
        elif b > i:
            pc["missed"].append((k, i, b))
        else:
            pc["extra"].append((k, i, b))
    for r, was_carried in out_of_scope:
        per_control[r["control"]]["oos"].append((r, was_carried))

    high = medium = low = 0
    table = []
    for c, pc in per_control.items():
        oos_medium = sum(1 for _, cr in pc["oos"] if not cr)
        low += len(pc["carried"]) + len(pc["oos"]) - oos_medium
        medium += oos_medium
        if feature and c in declared:
            medium += 1
        if c not in blind_controls:
            outcome = "UNCOUNTED"
            medium += 1
        elif c not in impl_controls and pc["missed"]:
            outcome = "MISSED"
            high += 1
        elif pc["missed"]:
            outcome = "MISSED"
            high += len(pc["missed"])
            if pc["extra"]:
                outcome = "MISSED+EXTRA"
                medium += len(pc["extra"])
        elif pc["extra"]:
            outcome = "EXTRA"
            medium += len(pc["extra"])
        elif pc["carried"]:
            outcome = "CARRIED"
        elif pc["oos"]:
            outcome = "OUT-OF-SCOPE-BY-DECLARED-SCOPE"
        elif any(g["control"] == c for g in gaps):
            outcome = "GAP"
        else:
            outcome = "MATCH"
        pc["outcome"] = outcome
        table.append(f"| {c} | {pc['impl']} | {pc['blind']} | {outcome} |")
    high += len(gaps)

    if high == 0 and medium == 0:
        result = "MATCH"
        if low:
            result += f" ({low} LOW carried or out-of-scope, owed to the FEATURE recount)"
    else:
        result = f"MISMATCH ({high} HIGH, {medium} MEDIUM)"
        if low:
            result += f" + {low} LOW"
    if not in_scope:
        # Legitimate for a slice/feature with no controls, but also what a mis-tagged
        # inventory plus an empty blind count looks like — make it visible to the reviewer.
        result += " (no controls in scope)"
    out = [
        f"Result: {result}",
        "",
        f"# Site Diff — {a.scope}",
        "",
        f"- **Implementer inventory:** `{a.impl}`",
        f"- **Blind count:** `{a.blind}`",
        f"- **Base:** `{a.base}`" if a.base else "- **Base:** none given — every key compared as owned",
        "- **Rules:** `references/enforcement-sites.md` §6",
        "",
        "## Per-Control Outcome",
        "",
        "| Control | Implementer sites | Independent sites | Outcome |",
        "|---|---|---|---|",
        *table,
        "",
        "## Findings",
        "",
    ]
    n = 0
    for c, pc in per_control.items():
        if feature and c in declared:
            n += 1
            out.append(f"{n}. **MEDIUM — PARTIAL COUNT `{c}`**: the blind count declared partial scope at "
                       "FEATURE scope, where every control must be counted in full. Stays Partial; recount.")
        if pc["outcome"] == "UNCOUNTED":
            n += 1
            out.append(f"{n}. **MEDIUM — UNCOUNTED `{c}`**: in the implementer inventory for "
                       f"{a.scope} but absent from the blind count. Stays Partial until independently counted.")
            continue
        if c not in impl_controls and pc["missed"]:
            n += 1
            out.append(f"{n}. **HIGH — MISSED control `{c}`**: the blind count found {pc['blind']} "
                       f"site(s); the implementer inventory does not list this control.")
        else:
            for (ctl, f, s), i, b in pc["missed"]:
                n += 1
                out.append(f"{n}. **HIGH — MISSED `{ctl}` at `{f}` `{s}`**: blind count {b}, implementer {i}. "
                           "Add the missing site(s) to the inventory with a disposition and mutation evidence.")
        for (ctl, f, s), i, b in pc["extra"]:
            n += 1
            out.append(f"{n}. **MEDIUM — EXTRA `{ctl}` at `{f}` `{s}`**: implementer {i}, blind count {b}. "
                       "Reviewer re-runs the mutation: a test fails → CONFIRMED-EXTRA; none fails → HIGH.")
        for r, was_carried in pc["oos"]:
            if not was_carried:
                n += 1
                out.append(f"{n}. **MEDIUM — OUT-OF-SCOPE-BY-DECLARED-SCOPE `{c}` at `{r['file']}` "
                           f"`{r['symbol']}`**: outside the blind count's declared scope, in code this slice "
                           "changed. Uncounted: the reviewer adjudicates as for UNCOUNTED.")
    for g in gaps:
        n += 1
        out.append(f"{n}. **HIGH — GAP `{g['control']}` at `{g['file']}` `{g['symbol']}` "
                   f"({g['path class']})**: {g['site description']}")
    if n == 0:
        out.append("None.")
    out.append("")

    carried_lines = []
    for c, pc in per_control.items():
        for (ctl, f, s), i, b in pc["carried"]:
            carried_lines.append(f"- **LOW — CARRIED `{ctl}` at `{f}` `{s}`**: implementer {i}, blind count {b}; "
                                 "code unchanged since base.")
        for r, was_carried in pc["oos"]:
            if was_carried:
                carried_lines.append(f"- **LOW — OUT-OF-SCOPE-BY-DECLARED-SCOPE `{c}` at `{r['file']}` "
                                     f"`{r['symbol']}`**: outside the declared scope; code unchanged since base.")
    if carried_lines:
        out += [
            "## Carried (owed to the FEATURE recount)",
            "",
            "Disagreements on code this slice did not change. Not findings for this slice; the controls "
            "stay Partial and the FEATURE recount (4e.5) compares these rows in full.",
            "",
            *carried_lines,
            "",
        ]

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text("\n".join(out), encoding="utf-8")
    print(out[0])
    sys.exit(0 if result.startswith("MATCH") else 1)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:  # never let a crash read as MISMATCH (exit 1)
        fail(f"{type(e).__name__}: {e}")
