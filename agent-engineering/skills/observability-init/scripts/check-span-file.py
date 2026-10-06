#!/usr/bin/env python3
"""Check a trace run's span file against the tracing standard's capture policy.

    python3 check-span-file.py <span-file> [env-file ...]

Reports, by name only, every secret-named environment variable whose value appears anywhere in the span file,
and every attribute that carries request or response headers. A secret-named variable is one whose name contains
KEY, TOKEN, SECRET, PASSWORD or CREDENTIAL, plus OTEL_EXPORTER_OTLP_HEADERS, whose header values are checked one
by one. Values come from the process environment and from every env file given; a name with different values in
different places has each value checked. No value is ever printed: a name that itself contains a secret value is
printed with that part replaced.

A value shorter than 4 characters is matched only against a whole recorded value, because inside longer text it
would match by accident on every run. The variables this applies to are listed, so they can be looked at by hand.

Exit status: 0 nothing found, 1 something found, 2 the span file or an env file could not be read.
"""

import json
import os
import re
import sys
from urllib.parse import unquote

SECRET_NAME = re.compile("KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL", re.IGNORECASE)
OTLP_HEADERS = re.compile(r"^OTEL_EXPORTER_OTLP_(TRACES_)?HEADERS$")
HEADER_ATTRIBUTE = re.compile(r"(^|\.)headers?(\.|$)", re.IGNORECASE)
# A value shorter than this is matched only against a whole recorded value: inside longer text it matches by accident.
SHORTEST_SUBSTRING = 4
# A string holding JSON (the GenAI message attributes do) is decoded and searched too, this many levels deep.
JSON_DEPTH = 3


def env_value(raw):
    raw = raw.strip()
    if raw[:1] in ("'", '"'):
        end = raw.find(raw[0], 1)
        if end != -1:
            return raw[1:end]
    if raw.startswith("#"):
        return ""
    return re.split(r"\s+#", raw, maxsplit=1)[0].strip()


def read_env_file(path):
    values = {}
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line.startswith("export "):
                line = line[len("export "):].lstrip()
            name, equals, raw = line.partition("=")
            if equals and name.strip() and not name.strip().startswith("#"):
                values[name.strip()] = env_value(raw)
    return values


def secrets(sources):
    """[(label, value)] for every distinct value that must not appear in a span.

    `sources` is a list of (where, {name: value}); a label says which variable and where it was set.
    """
    found = []
    for where, environment in sources:
        for name, value in environment.items():
            if OTLP_HEADERS.match(name):
                for number, pair in enumerate(value.split(","), start=1):
                    _, equals, header_value = pair.partition("=")
                    if not equals:
                        continue
                    header_value = unquote(header_value.strip())
                    found.append((f"{name} header {number} ({where})", header_value))
                    # The credential itself, without its scheme word.
                    _, space, rest = header_value.partition(" ")
                    if space and rest.strip():
                        found.append((f"{name} header {number} ({where})", rest.strip()))
            elif SECRET_NAME.search(name):
                found.append((f"{name} ({where})", value))
    unique = []
    for label, value in found:
        if value and (label, value) not in unique:
            unique.append((label, value))
    return unique


def recorded_texts(node, depth=JSON_DEPTH):
    """Every piece of text a decoded span records: strings, numbers as text, keys, and the inside of JSON strings."""
    if isinstance(node, bool) or node is None:
        return
    if isinstance(node, (int, float)):
        yield str(node)
    elif isinstance(node, str):
        yield node
        if depth and node[:1] in '{["':
            try:
                inner = json.loads(node)
            except ValueError:
                return
            yield from recorded_texts(inner, depth - 1)
    elif isinstance(node, dict):
        for key, value in node.items():
            yield str(key)
            yield from recorded_texts(value, depth)
    elif isinstance(node, list):
        for item in node:
            yield from recorded_texts(item, depth)


def redact(text, wanted):
    """`text` safe to print: no secret value, no control character."""
    for _, value in sorted(wanted, key=lambda item: -len(item[1])):
        text = text.replace(value, "<secret>")
    return "".join(character if character.isprintable() else "?" for character in text)


def check(span_lines, sources):
    """Returns (labels of secrets found, header attribute names, labels matched as whole values only).

    The first two are safe to print; the third holds variable names only.
    """
    wanted = secrets(sources)
    short = sorted({label for label, value in wanted if len(value) < SHORTEST_SUBSTRING})
    leaked, headers = set(), set()
    for line in span_lines:
        if not line.strip():
            continue
        span = json.loads(line)
        for holder in [span, *(span.get("events") or [])]:
            for name in holder.get("attributes") or {}:
                if HEADER_ATTRIBUTE.search(name):
                    headers.add(redact(name, wanted))
        for text in recorded_texts(span):
            for label, value in wanted:
                if text == value or (len(value) >= SHORTEST_SUBSTRING and value in text):
                    leaked.add(redact(label, wanted))
    return sorted(leaked), sorted(headers), short


def main(argv):
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        with open(argv[1], encoding="utf-8") as handle:
            span_lines = handle.read().splitlines()
    except OSError as exc:
        print(f"cannot read the span file: {type(exc).__name__}", file=sys.stderr)
        return 2
    sources = [("environment", dict(os.environ))]
    for number, path in enumerate(argv[2:], start=1):
        try:
            sources.append((f"env file {number}", read_env_file(path)))
        except (OSError, UnicodeDecodeError) as exc:
            print(f"cannot read env file {number}: {type(exc).__name__}", file=sys.stderr)
            return 2
    leaked, headers, short = check(span_lines, sources)
    print(f"spans checked: {sum(1 for line in span_lines if line.strip())}")
    print("secret values found for:", ", ".join(leaked) or "none")
    print("header attributes:", ", ".join(headers) or "none")
    if short:
        print(f"matched as whole values only (shorter than {SHORTEST_SUBSTRING} characters):", ", ".join(short))
    return 1 if leaked or headers else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
