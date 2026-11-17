#!/usr/bin/env python3
"""The defect ledger: one application's committed record of the defects its checks caught.

Usage:
    ledger.py add     --root <app dir> --input <file|->
    ledger.py reviews --root <app dir> --kind feature --input <file|->

Every value goes in ONE JSON object, read from the file `--input` names, or from
stdin with `--input -`. The command line carries only `--root`, `--kind` and
`--input`; any other flag is refused. Write the input with a file tool, or with a
quoted heredoc so that no shell parses a value:

    ledger.py add --root . --input /tmp/defect.json
    ledger.py reviews --root . --kind feature --input - <<'EOF'
    {"feature": "007-cart", "files": ["SDD/.records/reviews/REVIEW-007-cart-20261117.md"]}
    EOF

`add` keys: feature, found_by, class, severity, where, source (required); status
(default open), introduced_by, check_added, date (optional). `check_added` is
refused on an `open` line and required on a `fixed` one. `reviews` keys: feature,
files (the review files' paths, in chain order).

Files, under <app dir>:
    SDD/defects.jsonl          the defect ledger, one JSON object per line
    SDD/defects-setup.json     {"loops": [...], "classes": [...]}; the first write creates
                               {"loops": ["slice-review", "code-review", "final-check", "user"],
                                "classes": ["unclassified"]}. `ci` and `integration` are added by hand.
    SDD/.records/defects.lock  every write holds it (non-blocking flock) and refuses when it is held

A line has exactly these twelve fields, all strings, in this order:
    id             D-<n>; n = highest existing + 1. File order is the only ordering.
    status         open | fixed
    date           YYYY-MM-DD (default: today, local time)
    feature        ^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$ - the cycle that wrote it ([###]-[name], outside-cycle)
    found_by       a loop: slice-review, code-review, final-check, ci, integration, user
                   (on write, one of the setup file's `loops`)
    class          ^[a-z][a-z0-9-]{0,39}$ (on write, one of the setup file's `classes`, or unclassified)
    severity       HIGH | MEDIUM
    where          `-`, or ^[A-Za-z0-9_./@+~-]+(:[0-9]+)?$ (a file, optionally :<line>)
    introduced_by  "" or 7-40 hex characters
    check_added    open line: `pending` when found_by is user, else `none`;
                   fixed line: a check's name or `none`, never `pending`; at most 120 characters
    closed         "" on an open line; YYYY-MM-DD on a fixed one (its own date when written fixed)
    source         slice-review, code-review, final-check: `<review file name>, F<n>`
                   (code-review also `codex review of <brief file name>, F<n>`);
                   user: `<brief file name>, escape`, or a reference (an issue or report id);
                   ci, integration: a reference. A file name: ^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$
    Every text value is data: where and source at most 200 characters, printable only (a plain
    space, no Unicode C* or other Z* character), never containing " | " or "===".

Review files (`reviews`). File name -> loop, for --kind feature:
    REVIEW-<...> (not REVIEW-SLICE-<...>) -> code-review;  FINAL-CHECK-<...> -> final-check.
    A finding counts only from a line that starts (after at most 3 spaces and an optional `- `)
        FINDING F<n> | HIGH|MEDIUM|LOW | <file:line, file or -> | open|fixed
    outside `## Earlier Findings`, and, inside that section (to the next `## ` heading), from
        F<n> | open|fixed
    Severity and where come from the ID's first FINDING line in the chain; status from its
    latest line. LOW findings are not written; a finding whose source is already in the ledger,
    or whose where breaks its shape, is skipped. Accepted no-finding forms, a whole line:
        No findings.
        0 HIGH, 0 MEDIUM, 0 LOW

Output: `add` prints the id alone on its first line (an existing open line's id when the same
user line is logged again), then any notice. `reviews` prints `D-<n> | <severity> | <class> |
<source>` per line written, `not written | <source> | where` per finding skipped for its where,
the written and skipped counts, and any notice. A refusal is one stdout line, `refused: ...`;
it never prints a value read from the ledger, the setup file or a review file.

Exit status: 0 = done; 2 = invalid input, ledger or setup file, or the lock is held (nothing
written); 3 = a review file refused (nothing written). Stdlib only; POSIX (flock).
"""
from __future__ import annotations

import datetime
import fcntl
import json
import os
import re
import stat
import sys
import tempfile
import unicodedata
from pathlib import Path

FIELDS = ("id", "status", "date", "feature", "found_by", "class", "severity", "where",
          "introduced_by", "check_added", "closed", "source")
LOOPS = ("slice-review", "code-review", "final-check", "ci", "integration", "user")
DEFAULT_SETUP = {"loops": ["slice-review", "code-review", "final-check", "user"], "classes": ["unclassified"]}
FILE = r"[A-Za-z0-9][A-Za-z0-9._-]{0,99}"
FILE_RE = re.compile(FILE)
CLASS_RE = re.compile(r"[a-z][a-z0-9-]{0,39}")
FEATURE_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}")
WHERE_RE = re.compile(r"[A-Za-z0-9_./@+~-]+(?::[0-9]+)?")
ID_RE = re.compile(r"D-([1-9][0-9]*)")
HEX_RE = re.compile(r"[0-9a-fA-F]{7,40}")
REVIEW_SOURCE_RE = re.compile(rf"{FILE}, F[1-9][0-9]*")
LITE_SOURCE_RE = re.compile(rf"codex review of {FILE}, F[1-9][0-9]*")
ESCAPE_SOURCE_RE = re.compile(rf"{FILE}, escape")
FINDING_RE = re.compile(r" {0,3}(?:- )?FINDING (F[1-9][0-9]*) \| (HIGH|MEDIUM|LOW) \| (.*?) \| (open|fixed)[ \t]*")
EARLIER_RE = re.compile(r" {0,3}(?:- )?(F[1-9][0-9]*) \| (open|fixed)(?:[ \t].*)?")
CAPS = {"where": 200, "source": 200, "check_added": 120}
LEDGER, SETUP = "SDD/defects.jsonl", "SDD/defects-setup.json"


class Refused(Exception):
    def __init__(self, message: str, code: int = 2) -> None:
        super().__init__(message)
        self.code = code


def lit(value: object) -> str:
    """A caller's value as an escaped literal cut to 40 characters (UX-001)."""
    return json.dumps(str(value)[:40])


def is_date(value: str) -> bool:
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        return False
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def text_problem(value: str, cap: int) -> str | None:
    if not value:
        return "is empty"
    if len(value) > cap:
        return f"is longer than {cap} characters"
    if any(ch != " " and unicodedata.category(ch)[0] in "CZ" for ch in value):
        return "holds a character that is not printable"
    if " | " in value or "===" in value:
        return "holds ' | ' or '==='"
    return None


def source_ok(found_by: str, source: str) -> bool:
    if found_by in ("slice-review", "final-check"):
        return bool(REVIEW_SOURCE_RE.fullmatch(source))
    if found_by == "code-review":
        return bool(REVIEW_SOURCE_RE.fullmatch(source) or LITE_SOURCE_RE.fullmatch(source))
    if found_by == "user" and source.endswith(", escape"):
        return bool(ESCAPE_SOURCE_RE.fullmatch(source))
    return True


def line_problem(obj: object) -> tuple[str, str] | None:
    """The first rule a line breaks, as (field, rule) - field "" for the whole line - or None."""
    if not isinstance(obj, dict):
        return "", "is not a JSON object"
    if any(key not in FIELDS for key in obj):
        return "", "has an unexpected key"
    for key in FIELDS:
        if key not in obj:
            return key, "missing key"
        if not isinstance(obj[key], str):
            return key, "is not a string"
    for key, cap in CAPS.items():
        rule = text_problem(obj[key], cap)
        if rule:
            return key, rule
    status, found_by, check = obj["status"], obj["found_by"], obj["check_added"]
    checks = (
        ("id", ID_RE.fullmatch(obj["id"]), "is not D-<n>"),
        ("status", status in ("open", "fixed"), "is not open or fixed"),
        ("date", is_date(obj["date"]), "is not a YYYY-MM-DD date"),
        ("feature", FEATURE_RE.fullmatch(obj["feature"]), "is not a feature name"),
        ("found_by", found_by in LOOPS, "is not a loop: " + ", ".join(LOOPS)),
        ("class", CLASS_RE.fullmatch(obj["class"]), "is not a kebab-case class name"),
        ("severity", obj["severity"] in ("HIGH", "MEDIUM"), "is not HIGH or MEDIUM"),
        ("where", obj["where"] == "-" or WHERE_RE.fullmatch(obj["where"]), "is not - or a path[:line]"),
        ("introduced_by", obj["introduced_by"] == "" or HEX_RE.fullmatch(obj["introduced_by"]),
         "is not empty or 7-40 hex characters"),
        ("check_added", status != "open" or check == ("pending" if found_by == "user" else "none"),
         "on an open line is pending (found_by user) or none"),
        ("check_added", status != "fixed" or check != "pending", "on a fixed line is never pending"),
        ("closed", obj["closed"] == "" if status == "open" else is_date(obj["closed"]),
         "is empty on an open line and a YYYY-MM-DD date on a fixed one"),
        ("source", source_ok(found_by, obj["source"]), f"does not have the shape for found_by {found_by}"),
    )
    for field, ok, rule in checks:
        if not ok:
            return field, rule
    return None


def content_refusal(name: str, number: int, obj: object, field: str, rule: str) -> Refused:
    """A refusal about file content: line, id and field only - never a value (UX-001)."""
    parts = [f"{name}: line {number}"]
    if isinstance(obj, dict) and isinstance(obj.get("id"), str) and ID_RE.fullmatch(obj["id"]):
        parts.append(f"id {obj['id']}")
    parts.append(f"{field} {rule}" if field else rule)
    return Refused(": ".join(parts) + "; fix the line by hand")


def check_paths(root: Path) -> None:
    """SEC-002: refuse a ledger or setup path that is a symlink or resolves outside <root>/SDD/."""
    base = os.path.realpath(root) + os.sep + "SDD" + os.sep
    for name in (LEDGER, SETUP):
        path = root / name
        if path.is_symlink() or not os.path.realpath(path).startswith(base):
            raise Refused(f"{name}: is a symlink or lies outside SDD/; replace it with a plain file")


def take_lock(root: Path) -> int:
    records = root / "SDD" / ".records"
    records.mkdir(parents=True, exist_ok=True)
    fd = os.open(records / "defects.lock", os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        os.close(fd)
        raise Refused("another write to this defect ledger is in progress; run the command again after it ends")
    return fd


def read_ledger(root: Path) -> tuple[str, list[dict]]:
    """The ledger's text and lines, checked whole (REQ-003); "" and [] when there is none."""
    path = root / LEDGER
    if not path.exists():
        return "", []
    try:
        text = path.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        raise Refused(f"{LEDGER}: is not UTF-8 text; fix it by hand")
    lines, seen = [], {}
    for number, raw in enumerate(text.split("\n"), 1):
        raw = raw.rstrip("\r")
        if not raw.strip():
            continue
        try:
            obj = json.loads(raw)
        except ValueError:
            raise content_refusal(LEDGER, number, None, "", "is not a JSON object")
        problem = line_problem(obj)
        if problem:
            raise content_refusal(LEDGER, number, obj, *problem)
        if obj["id"] in seen:
            raise content_refusal(LEDGER, number, obj, "", f"repeats the id of line {seen[obj['id']]}")
        seen[obj["id"]] = number
        lines.append(obj)
    return text, lines


def read_setup(root: Path, ledger_exists: bool) -> dict | None:
    """The setup file (REQ-002), or None when it is absent and may be created."""
    path = root / SETUP
    if not path.exists():
        if ledger_exists:
            raise Refused(f"{SETUP}: is missing beside the defect ledger; restore it from git or write it by hand")
        return None
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except OSError:
        raise Refused(f"{SETUP}: cannot be read; make it a readable plain file or restore it from git")
    except (ValueError, UnicodeDecodeError):
        obj = None
    loops = obj.get("loops") if isinstance(obj, dict) else None
    classes = obj.get("classes") if isinstance(obj, dict) else None
    if not (isinstance(loops, list) and "user" in loops and all(isinstance(x, str) and x in LOOPS for x in loops)
            and isinstance(classes, list)
            and all(isinstance(x, str) and CLASS_RE.fullmatch(x) for x in classes)):
        raise Refused(f"{SETUP}: needs `loops` (names from {', '.join(LOOPS)}, user included) "
                      "and `classes` (kebab-case names); fix it by hand")
    return obj


def check_membership(line: dict, setup: dict) -> None:
    if line["found_by"] not in setup["loops"]:
        raise Refused(f"found_by {lit(line['found_by'])}: not a loop of this application; "
                      f"allowed: {', '.join(setup['loops'])} (or add it to {SETUP})")
    if line["class"] != "unclassified" and line["class"] not in setup["classes"]:
        raise Refused(f"class {lit(line['class'])}: not a class of this application; "
                      f"use unclassified or add it to {SETUP}")


def write(root: Path, text: str, new: list[dict], create_setup: bool) -> None:
    """Create the setup file if asked, then replace the ledger whole (temp file + rename, mode kept)."""
    sdd = root / "SDD"
    if create_setup:
        (sdd / "defects-setup.json").write_text(json.dumps(DEFAULT_SETUP) + "\n", encoding="utf-8")
    if text and not text.endswith("\n"):
        text += "\n"
    text += "".join(json.dumps(line, ensure_ascii=False) + "\n" for line in new)
    path = sdd / "defects.jsonl"
    if path.exists():
        mode = stat.S_IMODE(path.stat().st_mode)
    else:
        umask = os.umask(0)
        os.umask(umask)
        mode = 0o666 & ~umask
    fd, tmp = tempfile.mkstemp(dir=sdd, prefix=".defects-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def next_number(lines: list[dict]) -> int:
    return max((int(ID_RE.fullmatch(line["id"]).group(1)) for line in lines), default=0) + 1


def input_refusal(line: dict, field: str, rule: str) -> Refused:
    return Refused(f"{field} {lit(line.get(field, ''))}: {rule}")


def read_input(arg: str, keys: dict[str, type], required: tuple[str, ...]) -> dict:
    """REQ-022: one JSON object; unknown, duplicate or missing keys and wrong types are refused."""
    try:
        text = sys.stdin.read() if arg == "-" else Path(arg).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        raise Refused(f"--input {lit(arg)}: cannot be read")

    def pairs(items: list[tuple[str, object]]) -> dict:
        obj: dict = {}
        for key, value in items:
            if key in obj:
                raise Refused(f"input: duplicate key {lit(key)}")
            obj[key] = value
        return obj

    try:
        obj = json.loads(text, object_pairs_hook=pairs)
    except ValueError:
        obj = None
    if not isinstance(obj, dict):
        raise Refused("input: is not one JSON object")
    for key, value in obj.items():
        if key not in keys:
            raise Refused(f"input: unexpected key {lit(key)}; allowed: {', '.join(keys)}")
        if not isinstance(value, keys[key]):
            raise Refused(f"input: key {key}: wrong JSON type, expected {keys[key].__name__}")
    for key in required:
        if key not in obj:
            raise Refused(f"input: missing key {key}")
    return obj


ADD_KEYS = {k: str for k in ("feature", "found_by", "class", "severity", "where", "source",
                             "status", "introduced_by", "check_added", "date")}


def cmd_add(root: Path, data: dict) -> int:
    status = data.get("status", "open")
    if status == "open" and "check_added" in data:
        raise Refused("check_added: not given on an open line; it is set to pending or none")
    if status == "fixed" and "check_added" not in data:
        raise Refused("check_added: required with status fixed - the check's name, or none")
    date = data.get("date", datetime.date.today().isoformat())
    found_by = data["found_by"]
    line = {"id": "D-1", "status": status, "date": date, "feature": data["feature"], "found_by": found_by,
            "class": data["class"], "severity": data["severity"], "where": data["where"],
            "introduced_by": data.get("introduced_by", ""),
            "check_added": data["check_added"] if status == "fixed" else ("pending" if found_by == "user" else "none"),
            "closed": date if status == "fixed" else "", "source": data["source"]}
    problem = line_problem(line)
    if problem:
        raise input_refusal(line, *problem)
    check_paths(root)
    lock = take_lock(root)
    try:
        text, lines = read_ledger(root)
        setup = read_setup(root, (root / LEDGER).exists())
        check_membership(line, setup or DEFAULT_SETUP)
        for old in lines:
            if (found_by == "user" and old["status"] == "open"
                    and old["source"] == line["source"] and old["feature"] == line["feature"]):
                print(old["id"])
                print(f"already logged: {old['id']} is open with this source and feature; nothing written")
                return 0
        line["id"] = f"D-{next_number(lines)}"
        write(root, text, [line], setup is None)
    finally:
        os.close(lock)
    print(line["id"])
    if setup is None:
        print(f"setup file created: {SETUP}")
    return 0


def loop_of(name: str, kind: str) -> str | None:
    if kind == "feature":
        if name.startswith("FINAL-CHECK-"):
            return "final-check"
        if name.startswith("REVIEW-") and not name.startswith("REVIEW-SLICE-"):
            return "code-review"
    return None


def parse_chain(files: list[str], kind: str) -> dict[str, dict]:
    """Each finding ID of the chain: severity and where from its first FINDING line, status from its latest line."""
    found: dict[str, dict] = {}
    for path in files:
        name = os.path.basename(path)
        if not FILE_RE.fullmatch(name):
            raise Refused(f"review file {lit(name)}: is not a plain file name", 3)
        loop = loop_of(name, kind)
        if loop is None:
            raise Refused(f"review file {name}: is not a {kind} review (REVIEW-... or FINAL-CHECK-...)", 3)
        try:
            text = Path(path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            raise Refused(f"review file {name}: cannot be read", 3)
        earlier = False
        for raw in text.splitlines():
            if raw.startswith("## "):
                earlier = raw[3:].strip().startswith("Earlier Findings")
                continue
            match = (EARLIER_RE if earlier else FINDING_RE).fullmatch(raw)
            if not match:
                continue
            fid, state = match.group(1), match.group(match.lastindex)
            if fid in found:
                found[fid]["status"] = state
            elif not earlier:
                found[fid] = {"severity": match.group(2), "where": match.group(3).strip(),
                              "source": f"{name}, {fid}", "found_by": loop, "status": state}
    return found


def cmd_reviews(root: Path, kind: str, data: dict) -> int:
    feature, files = data["feature"], data["files"]
    if not FEATURE_RE.fullmatch(feature):
        raise Refused(f"feature {lit(feature)}: is not a feature name ([###]-[name])")
    if not all(isinstance(path, str) for path in files):
        raise Refused("input: key files: wrong JSON type, expected a list of strings")
    found = parse_chain(files, kind)
    check_paths(root)
    lock = take_lock(root)
    try:
        text, lines = read_ledger(root)
        setup = read_setup(root, (root / LEDGER).exists())
        known = {line["source"] for line in lines}
        number, today = next_number(lines), datetime.date.today().isoformat()
        new, out, skipped = [], [], 0
        for finding in found.values():
            if finding["severity"] == "LOW":
                continue
            if finding["source"] in known:
                skipped += 1
                continue
            fixed = finding["status"] == "fixed"
            line = {"id": f"D-{number}", "status": finding["status"], "date": today, "feature": feature,
                    "found_by": finding["found_by"], "class": "unclassified", "severity": finding["severity"],
                    "where": finding["where"], "introduced_by": "", "check_added": "none",
                    "closed": today if fixed else "", "source": finding["source"]}
            problem = line_problem(line)
            if problem and problem[0] == "where":
                out.append(f"not written | {finding['source']} | where")
                skipped += 1
                continue
            if problem:
                raise input_refusal(line, *problem)
            check_membership(line, setup or DEFAULT_SETUP)
            new.append(line)
            out.append(f"{line['id']} | {line['severity']} | {line['class']} | {line['source']}")
            number += 1
        if new:
            write(root, text, new, setup is None)
    finally:
        os.close(lock)
    print("\n".join(out + [f"written {len(new)}, skipped {skipped}"]))
    if new and setup is None:
        print(f"setup file created: {SETUP}")
    return 0


COMMANDS = {"add": ("--root", "--input"), "reviews": ("--root", "--kind", "--input")}


def parse_args(argv: list[str]) -> tuple[str, dict[str, str]]:
    if not argv or argv[0] not in COMMANDS:
        raise Refused("usage: ledger.py add|reviews --root <app dir> [--kind feature] --input <file|->")
    command, allowed, opts = argv[0], COMMANDS[argv[0]], {}
    rest = iter(argv[1:])
    for token in rest:
        if token not in allowed or token in opts:
            named = lit(token.split("=", 1)[0]) if token.startswith("-") else "(a bare value)"
            raise Refused(f"argument {named}: not allowed here; {command} takes only {', '.join(allowed)} "
                          "- every value goes in the JSON input")
        value = next(rest, None)
        if value is None:
            raise Refused(f"argument {token}: needs a value")
        opts[token] = value
    for flag in allowed:
        if flag not in opts:
            raise Refused(f"argument {flag}: missing")
    if command == "reviews" and opts["--kind"] != "feature":
        raise Refused(f"--kind {lit(opts['--kind'])}: allowed: feature")
    return command, opts


def main(argv: list[str]) -> int:
    try:
        command, opts = parse_args(argv)
        if command == "add":
            data = read_input(opts["--input"], ADD_KEYS, ("feature", "found_by", "class", "severity", "where", "source"))
        else:
            data = read_input(opts["--input"], {"feature": str, "files": list}, ("feature", "files"))
        root = Path(opts["--root"])
        if not root.is_dir():
            raise Refused(f"--root {lit(opts['--root'])}: is not a directory")
        if command == "add":
            return cmd_add(root, data)
        return cmd_reviews(root, opts["--kind"], data)
    except Refused as refusal:
        print(f"refused: {refusal}")
        return refusal.code
    except OSError as error:
        print(f"refused: {error.filename or 'SDD'}: {error.strerror}; check that SDD/ is readable and writable")
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
