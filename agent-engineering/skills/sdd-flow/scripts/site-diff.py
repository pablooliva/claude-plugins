#!/usr/bin/env python3
"""Diff an implementer's enforcement-site inventory against a blind count.

Usage:
    site-diff.py <impl-inventory.md> <blind-count.md> <out.md> --scope <SLICE-XXX|FEATURE>

Both inputs carry a `## Site Inventory` table in the shape defined by
`references/enforcement-sites.md` §4. Rows of Kind `site` are counted per
Control + File + Symbol on each side; blind-count `gap` rows are reported as
findings. The result is written to <out.md> and its first line is echoed.

Exit status: 0 = MATCH, 1 = MISMATCH, 2 = usage or input error.
Deterministic: no judgment, no network, stdlib only.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

HEADER = "## Site Inventory"
COLUMNS = ["control", "file", "symbol", "kind", "path class",
           "site description", "disposition", "evidence", "slice"]
SCOPE_RE = re.compile(r"^(SLICE-\d{3}|FEATURE)$")
CELL_SPLIT = re.compile(r"(?<!\\)\|")  # split on | not preceded by a backslash


def fail(msg: str) -> None:
    print(f"site-diff: {msg}", file=sys.stderr)
    sys.exit(2)


def parse_inventory(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        fail(f"inventory not found: {path}")
    rows: list[dict[str, Any]] = []
    in_section = False
    header: list[str] | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line == HEADER:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section or not line.startswith("|"):
            continue
        cells = [c.strip().replace("\\|", "|") for c in CELL_SPLIT.split(line.strip().strip("|"))]
        if header is None:
            header = [c.lower() for c in cells]
            if header != COLUMNS:
                fail(f"{path}: `{HEADER}` columns must be {COLUMNS}, got {header}")
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue  # separator row
        if len(cells) != len(COLUMNS):
            fail(f"{path}: row has {len(cells)} cells, expected {len(COLUMNS)} "
                 f"(escape a literal pipe as \\|): {raw}")
        row = dict(zip(COLUMNS, cells))
        row["kind"] = row["kind"].lower()
        if row["kind"] not in ("site", "gap"):
            fail(f"{path}: Kind must be `site` or `gap`: {raw}")
        row["file"] = row["file"].removeprefix("./")
        rows.append(row)
    if header is None:
        fail(f"{path}: no `{HEADER}` table found")
    return rows


def key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (row["control"], row["file"], row["symbol"])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("impl")
    ap.add_argument("blind")
    ap.add_argument("out")
    ap.add_argument("--scope", required=True)
    a = ap.parse_args()
    if not SCOPE_RE.match(a.scope):
        fail(f"--scope must match SLICE-### or FEATURE, got {a.scope!r}")

    impl = parse_inventory(Path(a.impl))
    blind = parse_inventory(Path(a.blind))

    blind_controls = {r["control"] for r in blind}
    if a.scope == "FEATURE":
        in_scope = blind_controls | {r["control"] for r in impl}
    else:
        in_scope = blind_controls | {r["control"] for r in impl if r["slice"] == a.scope}

    impl_sites = Counter(key(r) for r in impl if r["kind"] == "site" and r["control"] in in_scope)
    blind_sites = Counter(key(r) for r in blind if r["kind"] == "site")
    impl_controls = {r["control"] for r in impl if r["control"] in in_scope}

    per_control: dict[str, dict[str, Any]] = {}
    for c in sorted(in_scope):
        per_control[c] = {"impl": 0, "blind": 0, "missed": [], "extra": []}
    for k in sorted(set(impl_sites) | set(blind_sites)):
        i, b = impl_sites.get(k, 0), blind_sites.get(k, 0)
        pc = per_control[k[0]]
        pc["impl"] += i
        pc["blind"] += b
        if b > i:
            pc["missed"].append((k, i, b))
        elif i > b:
            pc["extra"].append((k, i, b))

    gaps = [r for r in blind if r["kind"] == "gap"]
    high = medium = 0
    table = []
    for c, pc in per_control.items():
        if c not in blind_controls:
            outcome = "UNCOUNTED"
            medium += 1
        elif c not in impl_controls:
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
        else:
            outcome = "MATCH"
        pc["outcome"] = outcome
        table.append(f"| {c} | {pc['impl']} | {pc['blind']} | {outcome} |")
    high += len(gaps)

    result = "MATCH" if high == 0 and medium == 0 else f"MISMATCH ({high} HIGH, {medium} MEDIUM)"
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
        if pc["outcome"] == "UNCOUNTED":
            n += 1
            out.append(f"{n}. **MEDIUM — UNCOUNTED `{c}`**: in the implementer inventory for "
                       f"{a.scope} but absent from the blind count. Stays Partial until independently counted.")
            continue
        if c in blind_controls and c not in impl_controls:
            n += 1
            out.append(f"{n}. **HIGH — MISSED control `{c}`**: the blind count found {pc['blind']} "
                       f"site(s); the implementer inventory does not list this control.")
            continue
        for (ctl, f, s), i, b in pc["missed"]:
            n += 1
            out.append(f"{n}. **HIGH — MISSED `{ctl}` at `{f}` `{s}`**: blind count {b}, implementer {i}. "
                       "Add the missing site(s) to the inventory with a disposition and mutation evidence.")
        for (ctl, f, s), i, b in pc["extra"]:
            n += 1
            out.append(f"{n}. **MEDIUM — EXTRA `{ctl}` at `{f}` `{s}`**: implementer {i}, blind count {b}. "
                       "Reviewer re-runs the mutation: a test fails → CONFIRMED-EXTRA; none fails → HIGH.")
    for g in gaps:
        n += 1
        out.append(f"{n}. **HIGH — GAP `{g['control']}` at `{g['file']}` `{g['symbol']}` "
                   f"({g['path class']})**: {g['site description']}")
    if n == 0:
        out.append("None.")
    out.append("")

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
