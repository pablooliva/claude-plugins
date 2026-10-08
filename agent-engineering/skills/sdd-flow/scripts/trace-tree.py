#!/usr/bin/env python3
"""Render a trace run's span file as call trees, per-request call counts, and a capture-policy scan.

Usage:
    trace-tree.py <span-file> [env-file ...] [--out <file.md>]

The span file is the one an application's trace run writes: one span per line, as
the OpenTelemetry SDK's `span.to_json()` prints it. The output is Markdown. With
--out it is written to that file and only its `Result:` line is echoed.

An *entry point* is a span of kind SERVER or CONSUMER, or the first span of a
trace when it is of another kind and not an outgoing call (a job or a command
traced by the wrapper). A *request* is one entry-point span and everything beneath
it, down to the next entry-point span. Spans in no request — the test's own client
above a route, a call made while the application starts — are listed by name in
the notes, an LLM span among them marked `[LLM]`. Requests are grouped per entry point by the entry span's name, and
requests whose trees are identical are shown once, as one *shape*, with how many
there were.

Inside a request every span is one of:
  [LLM]            it carries a `gen_ai.*` attribute and is not a tool or agent
                   span (`gen_ai.operation.name` of execute_tool, invoke_agent or
                   create_agent). Every such span counts, nested or not.
  [external: X]    a span of kind CLIENT or PRODUCER without a `gen_ai.*`
                   attribute; X is the system it reached (database or messaging
                   system, else the host).
  (inside the LLM call: X)
                   the same, beneath an LLM span: taken as that call's own request
                   and not counted. The targets are listed per entry point, so a
                   call to some other system made from there can be seen.
  (unmarked)       anything else — the framework's own spans, tool and agent spans,
                   and the application's own functions, which it records
                   automatically, one span per call, named `<module>.<function>`.

An application caps repeated calls: after the first few calls of one function from
one caller, further calls get no span, and the caller's span counts them. The tree
prints those counts beside the function — `×10  +4 not recorded, 1 failed` is 14
calls, 10 of them drawn, 4 not, and 1 of those 4 ended in an exception. Across the
requests of one shape the counts are given as a range, like the durations; they do
not make two requests different shapes.

The counts of LLM and external calls are per request: the fewest and the most seen
in any one request of that entry point, never a total across requests.

The capture-policy scan is `check-span-file.py` of the `observability-init` skill,
loaded from beside this skill: secret-named environment variables whose value is
recorded anywhere, and attributes that carry headers. Values come from the process
environment and from every env file given. No value is printed: a span name or
target that contains one is printed with that part replaced.

Exit status: 0 = rendered, scan clean; 1 = rendered, the scan found something;
2 = usage error, unreadable input, a span file with no span, a tree nested too
deeply to draw, or the scan script missing.
Deterministic: no judgment, no network, stdlib only.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional
from urllib.parse import urlsplit

SCAN_SCRIPT = Path(__file__).resolve().parents[2] / "observability-init" / "scripts" / "check-span-file.py"
OUTGOING = {"CLIENT", "PRODUCER"}
INCOMING = {"SERVER", "CONSUMER"}
NOT_A_MODEL_CALL = {"execute_tool", "invoke_agent", "create_agent"}
# The first of these a span carries names the system it reached.
TARGET_ATTRIBUTES = ["db.system.name", "db.system", "messaging.system", "rpc.system", "peer.service",
                     "server.address", "net.peer.name"]
URL_ATTRIBUTES = ["url.full", "http.url"]
MAX_SHAPES = 10   # shapes printed per entry point; the counts always cover every request
MAX_NAME = 80     # a span name longer than this is cut (some database spans are named by their statement);
                  # an own function's name never is: the tree is read to tell two functions apart
CAPPED, CAPPED_FAILED = ".not_recorded", ".not_recorded_failed"   # `calls.<function>` + these, on the caller's span


class Unreadable(Exception):
    """The input cannot be rendered; the message is safe to print."""


def load_scan() -> Any:
    spec = importlib.util.spec_from_file_location("check_span_file", SCAN_SCRIPT)
    try:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except (OSError, AttributeError) as exc:
        raise Unreadable(f"the capture-policy scan is missing ({type(exc).__name__}): expected "
                         f"skills/observability-init/scripts/check-span-file.py beside this skill — "
                         f"a broken install of the agent-engineering plugin")
    return module


def milliseconds(raw: dict[str, Any]) -> Optional[float]:
    try:
        start = datetime.fromisoformat(str(raw["start_time"]).replace("Z", "+00:00"))
        end = datetime.fromisoformat(str(raw["end_time"]).replace("Z", "+00:00"))
    except (KeyError, ValueError):
        return None
    return (end - start).total_seconds() * 1000


def a_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


class Span:
    def __init__(self, raw: dict[str, Any], redact: Callable[[str], str]):
        context = a_dict(raw.get("context"))
        self.trace = str(context.get("trace_id") or "")
        # The SDK always writes an id. A span without one gets an id from its own content, never from where it
        # sits in the file, so that the order of the lines cannot change the output.
        self.id = str(context.get("span_id") or "no id: " + hashlib.sha1(
            json.dumps(raw, sort_keys=True, default=str).encode("utf-8")).hexdigest())
        self.parent = raw.get("parent_id")
        name = redact(str(raw.get("name") or "?"))
        self.attributes = a_dict(raw.get("attributes"))
        # A span the application's own-function hook made: named for the function, with the file it is in.
        self.function = (bool(raw.get("name")) and self.attributes.get("code.function.name") == raw.get("name")
                         and "code.file.path" in self.attributes)
        self.name = name if self.function or len(name) <= MAX_NAME else name[:MAX_NAME - 1] + "…"
        self.kind = str(raw.get("kind") or "").rpartition(".")[2].upper()
        self.unrecorded = self._unrecorded(redact)
        self.error = a_dict(raw.get("status")).get("status_code") == "ERROR"
        self.start = str(raw.get("start_time") or "")
        self.milliseconds = milliseconds(raw)
        self.target = redact(self._target())
        self.http_status = redact(str(self.attributes.get("http.response.status_code", "")))
        self.children: list[Span] = []
        self.reached = False      # some first span of a trace leads to it
        self.in_request = False   # it is in some request's tree

    def _unrecorded(self, redact: Callable[[str], str]) -> dict[str, tuple[int, int]]:
        """{function name: (calls the repeat cap left without a span, how many of those raised)}."""
        def count(value: Any) -> int:
            return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else 0

        found = {}
        for key, value in self.attributes.items():
            if key.startswith("calls.") and key.endswith(CAPPED) and count(value):
                name = key[len("calls."):-len(CAPPED)]
                # Two names that print alike once a secret is taken out of them are one row: their counts add up.
                calls, failed = found.get(redact(name), (0, 0))
                found[redact(name)] = (calls + count(value),
                                       failed + count(self.attributes.get(f"calls.{name}{CAPPED_FAILED}")))
        return found

    def _target(self) -> str:
        for name in TARGET_ATTRIBUTES:
            if self.attributes.get(name):
                return str(self.attributes[name])
        for name in URL_ATTRIBUTES:
            if self.attributes.get(name):
                try:
                    return urlsplit(str(self.attributes[name])).hostname or ""
                except ValueError:
                    return ""
        return ""

    @property
    def gen_ai(self) -> bool:
        return any(name.startswith("gen_ai.") for name in self.attributes)

    @property
    def model_call(self) -> bool:
        return self.gen_ai and str(self.attributes.get("gen_ai.operation.name")) not in NOT_A_MODEL_CALL

    @property
    def no_route(self) -> bool:
        return (self.kind == "SERVER" and "http.request.method" in self.attributes
                and "http.route" not in self.attributes)


class Node:
    """One span as it is printed: its name, its marks, and the nodes beneath it."""

    def __init__(self, span: Span, marks: list[str], children: list[Node]):
        self.name = span.name
        self.marks = " ".join(marks + (["error"] if span.error else []))
        self.milliseconds = span.milliseconds
        self.children = children
        self.unrecorded = span.unrecorded   # not part of the key: the counts do not make a different shape
        self.key: tuple = (self.name, self.marks, tuple(child.key for child in children))


class Request:
    def __init__(self, entry: Span):
        self.entry = entry
        self.llm = 0
        self.external = 0
        self.targets: set[str] = set()
        self.inside: set[str] = set()   # what outgoing spans beneath an LLM span reached
        self.unrecorded = 0             # own-function calls the repeat cap left without a span
        self.unrecorded_failed = 0      # ... and how many of those ended in an exception
        self.root = self._node(entry, first=True, inside=False)

    def _node(self, span: Span, first: bool, inside: bool) -> Node:
        span.in_request = True
        self.unrecorded += sum(calls for calls, _ in span.unrecorded.values())
        self.unrecorded_failed += sum(failed for _, failed in span.unrecorded.values())
        marks = ["[entry]"] if first else []
        if span.model_call:
            marks.append("[LLM]")
            self.llm += 1
            inside = True
        elif span.kind in OUTGOING and not span.gen_ai:
            if inside:
                marks.append(f"(inside the LLM call: {span.target})" if span.target else "(inside the LLM call)")
                self.inside.add(span.target or span.name)
            else:
                marks.append(f"[external: {span.target}]" if span.target else "[external]")
                self.external += 1
                self.targets.add(span.target or span.name)
        return Node(span, marks, [self._node(child, False, inside) for child in span.children
                                  if child.kind not in INCOMING])


def read_spans(lines: list[str], redact: Callable[[str], str]) -> dict[tuple[str, str], Span]:
    spans: dict[tuple[str, str], Span] = {}
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except ValueError:
            raw = None
        if not isinstance(raw, dict):
            raise Unreadable(f"line {number} of the span file is not a JSON object")
        span = Span(raw, redact)
        key, copy = (span.trace, span.id), 1
        while key in spans and not a_dict(raw.get("context")).get("span_id"):
            copy += 1
            key = (span.trace, f"{span.id} #{copy}")
        span.id = key[1]
        spans[key] = span
    if not spans:
        raise Unreadable("the span file holds no span — the trace run wrote nothing")
    return spans


def analyse(spans: dict[tuple[str, str], Span]) -> tuple[dict[str, list[Request]], Counter, int, int]:
    """(requests per entry-point name, names of spans in no request, orphans, spans no first span leads to)."""
    roots, orphans = [], 0
    for span in spans.values():
        parent = spans.get((span.trace, str(span.parent))) if span.parent else None
        if parent is None:
            roots.append(span)
            orphans += 1 if span.parent else 0
        else:
            parent.children.append(span)
    for span in spans.values():
        span.children.sort(key=lambda child: (child.start, child.id))
    waiting = list(roots)
    while waiting:
        span = waiting.pop()
        span.reached = True
        waiting += span.children
    groups: dict[str, list[Request]] = {}
    first = {id(span) for span in roots}
    for span in sorted(spans.values(), key=lambda span: (span.start, span.trace, span.id)):
        if span.reached and (span.kind in INCOMING or (id(span) in first and span.kind not in OUTGOING)):
            groups.setdefault(span.name, []).append(Request(span))
    outside = Counter(span.name + (" [LLM]" if span.model_call else "")
                      for span in spans.values() if span.reached and not span.in_request)
    return groups, outside, orphans, sum(1 for span in spans.values() if not span.reached)


def span_range(values: list[int]) -> str:
    return str(min(values)) if min(values) == max(values) else f"{min(values)}–{max(values)}"


def duration(values: list[Optional[float]]) -> str:
    known = [value for value in values if value is not None]
    if not known:
        return ""

    def text(value: float) -> str:
        return f"{value:.1f}" if value < 10 else f"{value:.0f}"

    low, high = text(min(known)), text(max(known))
    return f"{low} ms" if low == high else f"{low}–{high} ms"


def plural(count: int, word: str) -> str:
    return f"{count} {word}" + ("" if count == 1 else "s")


def unrecorded_note(nodes: list[Node], name: str) -> str:
    """`+4 not recorded, 1 failed` for one function beneath the same span of every request of a shape."""
    counts = [node.unrecorded.get(name, (0, 0)) for node in nodes]
    return (f"+{span_range([calls for calls, _ in counts])} not recorded, "
            f"{span_range([failed for _, failed in counts])} failed")


def tree_rows(nodes: list[Node], prefix: str, branch: str, times: int, note: str = "") -> list[tuple[str, str, str]]:
    """Rows (tree text, marks, duration) for the same position in every request of a shape.

    Siblings that follow one another with identical trees are printed once, with how many there were. A function
    the repeat cap left some calls of without a span has those counts on its last row here, or on a row of its
    own when none of its calls is drawn directly beneath this span.
    """
    first = nodes[0]
    rows = [(prefix + branch + first.name + (f"  ×{times}" if times > 1 else "") + (f"  {note}" if note else ""),
             first.marks, duration([node.milliseconds for node in nodes]))]
    below = prefix + ("" if not branch else "│  " if branch == "├─ " else "   ")
    runs: list[list[int]] = []
    for index, child in enumerate(first.children):
        if runs and first.children[runs[-1][0]].key == child.key:
            runs[-1].append(index)
        else:
            runs.append([index])
    capped = sorted({name for node in nodes for name in node.unrecorded})
    last_run = {first.children[run[0]].name: number for number, run in enumerate(runs)}
    alone = [name for name in capped if name not in last_run]
    for number, run in enumerate(runs):
        name = first.children[run[0]].name
        rows += tree_rows([node.children[index] for node in nodes for index in run], below,
                          "└─ " if number == len(runs) - 1 and not alone else "├─ ", len(run),
                          unrecorded_note(nodes, name) if name in capped and last_run[name] == number else "")
    for number, name in enumerate(alone, start=1):
        rows.append((f"{below}{'└─ ' if number == len(alone) else '├─ '}({name}  {unrecorded_note(nodes, name)})", "", ""))
    return rows


def render_shape(requests: list[Request]) -> list[str]:
    rows = tree_rows([request.root for request in requests], "", "", 1)
    width = max(len(text) for text, _, _ in rows)
    marks_width = max(len(marks) for _, marks, _ in rows)
    return [f"{text:<{width}}  {marks:<{marks_width}}  {took}".rstrip() for text, marks, took in rows]


def statuses(requests: list[Request]) -> str:
    codes = Counter(request.entry.http_status for request in requests if request.entry.http_status)
    return ", ".join(f"{code} ×{count}" for code, count in sorted(codes.items()))


def render_entry(name: str, requests: list[Request]) -> list[str]:
    failed = sum(1 for request in requests if request.entry.error)
    targets = sorted({target for request in requests for target in request.targets})
    inside = sorted({target for request in requests for target in request.inside})
    shapes: dict[tuple, list[Request]] = {}
    for request in requests:
        shapes.setdefault(request.root.key, []).append(request)
    ordered = sorted(shapes.values(), key=lambda group: (-group[0].llm, -group[0].external, -len(group),
                                                         render_shape(group)))
    lines = [f"## {name}", ""]
    if all(request.entry.no_route for request in requests):
        lines += ["Named by the method alone: no route matched — a request refused before routing, or an unknown path.", ""]
    lines += [
        f"- Requests: {len(requests)}, {failed} ended in error",
        f"- LLM calls in one request: fewest {min(r.llm for r in requests)}, most {max(r.llm for r in requests)}",
        f"- External calls in one request: fewest {min(r.external for r in requests)}, "
        f"most {max(r.external for r in requests)}",
        f"- External targets seen: {', '.join(targets) or 'none'}",
        f"- Reached from beneath an LLM call (taken as that call's own request, not counted): "
        f"{', '.join(inside) or 'none'}",
    ]
    if any(request.unrecorded for request in requests):
        lines.append(f"- Own-function calls not recorded in one request (over the repeat cap): fewest "
                     f"{min(r.unrecorded for r in requests)}, most {max(r.unrecorded for r in requests)}; "
                     f"of those, ended in an exception: most {max(r.unrecorded_failed for r in requests)}")
    lines.append(f"- Shapes: {len(ordered)}")
    for number, group in enumerate(ordered[:MAX_SHAPES], start=1):
        http = statuses(group)
        lines += ["", f"### Shape {number} of {len(ordered)} — {plural(len(group), 'request')} · "
                      f"{plural(group[0].llm, 'LLM call')}, {plural(group[0].external, 'external call')}"
                      + (f" · HTTP status {http}" if http else ""), "", "```text", *render_shape(group), "```"]
    if len(ordered) > MAX_SHAPES:
        left = ordered[MAX_SHAPES:]
        lines += ["", f"{plural(len(left), 'more shape')} not shown ({plural(sum(len(g) for g in left), 'request')}); "
                      f"none has more LLM calls, or as many LLM calls and more external calls, than the last one shown. "
                      f"The counts above cover them."]
    return lines + [""]


def cell(text: str) -> str:
    return text.replace("|", "\\|")


def render(span_file: str, lines: list[str], env_files: list[str], scan: Any) -> tuple[str, str, bool]:
    """(the `Result:` line, the whole document, whether the scan found something)."""
    sources = [("environment", dict(os.environ))]
    for number, path in enumerate(env_files, start=1):
        try:
            sources.append((f"env file {number}", scan.read_env_file(path)))
        except (OSError, UnicodeDecodeError) as exc:
            raise Unreadable(f"cannot read env file {number}: {type(exc).__name__}")
    wanted = scan.secrets(sources)

    def redact(text: str) -> str:
        return scan.redact(text, wanted)

    spans = read_spans(lines, redact)
    try:
        leaked, headers, short = scan.check(lines, sources)
    except (AttributeError, TypeError):
        raise Unreadable("the span file is not in the shape the SDK writes (a span's events or attributes "
                         "are not objects)")
    groups, outside, orphans, unreached = analyse(spans)
    found = bool(leaked or headers)

    names = sorted(groups, key=lambda name: (all(r.entry.no_route for r in groups[name]), name))
    requests = [request for name in names for request in groups[name]]
    most = max((request.llm for request in requests), default=0)
    heaviest = next((name for name in names if any(r.llm == most for r in groups[name])), "")
    result = (f"Result: {plural(len(names), 'entry point')}, {plural(len(requests), 'request')}, "
              f"most LLM calls in one request {most}" + (f" ({heaviest})" if most else "")
              + f", capture-policy scan {'FOUND' if found else 'CLEAN'}")

    out = ["# Trace tree", "", result, "",
           f"Span file: `{redact(span_file)}` — {plural(len(spans), 'span')}. A request is one entry-point span "
           f"and everything beneath it, down to the next entry point; counts are per request, never a total "
           f"across requests.", "",
           "## Summary", "",
           "| Entry point | Requests | LLM calls in one request | External calls in one request | Ended in error | Shapes |",
           "|---|---|---|---|---|---|"]
    for name in names:
        group = groups[name]
        out.append(f"| {cell(name)} | {len(group)} | {span_range([r.llm for r in group])} | "
                   f"{span_range([r.external for r in group])} | {sum(1 for r in group if r.entry.error)} | "
                   f"{len({r.root.key for r in group})} |")
    out.append("")
    for name in names:
        out += render_entry(name, groups[name])

    out += ["## Capture-policy scan", "",
            f"- Secret values found for: {', '.join(leaked) or 'none'}",
            f"- Header attributes: {', '.join(headers) or 'none'}"]
    if short:
        out.append(f"- Matched as whole values only (shorter than {scan.SHORTEST_SUBSTRING} characters): "
                   f"{', '.join(short)}")
    out += [f"- Values checked: the process environment and {plural(len(env_files), 'env file')}", "",
            "## Notes", "",
            "- Spans in no request (above an entry point, or outside any): "
            + (", ".join(f"{name} ×{count}" for name, count in sorted(outside.items())) or "none"),
            f"- Spans whose parent is not in the file (each treated as the first span of a trace): {orphans}",
            f"- Spans no first span leads to (their parent links form a loop): {unreached}", ""]
    return result, "\n".join(out), found


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        # argparse's own message repeats the argument it rejected, whatever that argument holds.
        self.exit(2, f"trace-tree: usage error\n{self.format_usage()}")


def main(argv: list[str]) -> int:
    parser = Parser(prog="trace-tree.py", description="Render a trace run's span file as call trees.")
    parser.add_argument("span_file")
    parser.add_argument("env_files", nargs="*", metavar="env-file")
    parser.add_argument("--out", help="write the document here and echo only its Result: line")
    args = parser.parse_args(argv[1:])
    try:
        try:
            with open(args.span_file, encoding="utf-8") as handle:
                lines = handle.read().splitlines()
        except (OSError, UnicodeDecodeError) as exc:
            raise Unreadable(f"cannot read the span file: {type(exc).__name__}")
        result, document, found = render(args.span_file, lines, args.env_files, load_scan())
        if args.out:
            try:
                Path(args.out).parent.mkdir(parents=True, exist_ok=True)
                Path(args.out).write_text(document, encoding="utf-8")
            except OSError as exc:
                raise Unreadable(f"cannot write the --out file: {type(exc).__name__}")
            print(result)
        else:
            print(document)
    except Unreadable as exc:
        print(f"trace-tree: {exc}", file=sys.stderr)
        return 2
    except RecursionError:
        print("trace-tree: a trace is nested too deeply to draw", file=sys.stderr)
        return 2
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
