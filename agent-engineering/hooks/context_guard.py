#!/usr/bin/env python3
"""The sdd-flow Safety-Net, measured by the harness instead of counted by the agent.

A PreToolUse hook. It acts only for a subagent whose prompt names a counter file under
`.records/counters/` ("Your counter file: <path>") — the spawns that carry sdd-flow's
Safety-Net Rule. For every other call it does nothing.

Before each tool call of such a subagent it reads the subagent's own transcript, takes the
context size the API last reported (input + cache read + cache creation + output tokens of the
latest assistant message), and writes it to the counter file:

    Context: <tokens>/<limit> tokens

The limit is the number after the slash in the counter file as the orchestrator created it
(`Context: 0/120000 tokens`); DEFAULT_LIMIT when the file holds none. Once the context is past
the limit the Safety-Net has tripped: the line ends ` — tripped`, and from then on — whatever
later samples say; only a successor's fresh counter file starts again — every tool call is
refused with a reason that starts `Safety-Net tripped`, except the file-tool calls the handoff
needs: reading the compact body named in the prompt, and reading or writing `progress.md` or a
file under `.records/compacted/`. Bash is refused, except a bare `date`.

Never breaks work: on any input it cannot read it allows the call and writes nothing.
Python 3.9+, stdlib only. Reads JSON from stdin.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Optional

DEFAULT_LIMIT = 120_000
TAIL_BYTES = 512 * 1024
# The labelled lines of the spawn prompt. A path may hold spaces; it ends at its `.md`.
COUNTER_RE = re.compile(r"^\W*Your counter file:\s*`?(.+?\.records/counters/.+?\.md)`?(?=[\s)]|$)", re.M)
COMPACT_RE = re.compile(r"Compact instructions[^\n:]*trips:\s*`?(.+?-compact\.md)`?(?=[\s)]|$)")
COMPACT_FALLBACK_RE = re.compile(r"([^\s`'\"]*bodies/[\w-]+-compact\.md)")
DATE_RE = re.compile(r"\A[ \t]*date(?:[ \t]+[-+%\w:'\".,]+)*[ \t]*\Z")  # one line, one `date`: no separator
LIMIT_RE = re.compile(r"/\s*([\d,_]+)\s*tokens")
HANDOFF_MARKS = (".records/compacted/", "progress.md")


def subagent_transcript(data: dict[str, Any]) -> Optional[Path]:
    agent, main = data.get("agent_id"), data.get("transcript_path")
    if not agent or not main or not str(main).endswith(".jsonl"):
        return None
    path = Path(str(main)[: -len(".jsonl")]) / "subagents" / f"agent-{agent}.jsonl"
    return path if path.is_file() else None


def first_prompt(transcript: Path) -> str:
    with transcript.open(encoding="utf-8") as handle:
        for line in handle:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if entry.get("type") != "user":
                continue
            content = (entry.get("message") or {}).get("content")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                return "\n".join(str(block.get("text", "")) for block in content if isinstance(block, dict))
    return ""


def context_tokens(transcript: Path) -> Optional[int]:
    """The latest assistant message's reported context size. Read from the end in growing pieces, so a record longer
    than one piece is still read whole: only a line that starts inside the piece read so far is parsed."""
    with transcript.open("rb") as handle:
        handle.seek(0, os.SEEK_END)
        size = handle.tell()
        span = TAIL_BYTES
        while True:
            start = max(0, size - span)
            handle.seek(start)
            lines = handle.read().splitlines()
            if start > 0:
                lines = lines[1:]  # the first line may begin before the piece: never parse half a record
            for raw in reversed(lines):
                if b'"usage"' not in raw:
                    continue
                try:
                    entry = json.loads(raw.decode("utf-8", errors="replace"))
                except ValueError:
                    continue
                usage = (entry.get("message") or {}).get("usage") if isinstance(entry, dict) else None
                if isinstance(usage, dict):
                    return sum(int(usage.get(key) or 0) for key in
                               ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens", "output_tokens"))
            if start == 0:
                return None
            span *= 4


def resolve(path: str, cwd: str) -> Path:
    p = Path(path)
    return p if p.is_absolute() else Path(cwd) / p


def read_state(counter: Path) -> tuple[int, bool]:
    """(the limit, whether this counter file already says tripped)."""
    try:
        text = counter.read_text(encoding="utf-8")
    except OSError:
        text = ""
    m = LIMIT_RE.search(text)
    return (int(re.sub(r"[,_]", "", m.group(1))) if m else DEFAULT_LIMIT), "tripped" in text


def handoff_call(data: dict[str, Any], compact: Optional[str], cwd: str, records: Path) -> bool:
    """A call the handoff itself needs, judged by its real destination: reading the compact body, progress.md or a
    compaction file; writing progress.md or a file under `.records/compacted/`; and a bare `date`, for the compaction
    file's timestamp. No other Bash command is: what a command does cannot be told from its text, and the file tools
    do everything else the handoff needs."""
    tool, given = data.get("tool_name"), data.get("tool_input") or {}
    if tool == "Bash":
        return DATE_RE.match(str(given.get("command", ""))) is not None
    if tool not in ("Read", "Write", "Edit", "MultiEdit"):
        return False
    target = Path(os.path.normpath(resolve(str(given.get("file_path", "")), cwd)))
    in_records = target == records / "progress.md"  # this cycle's records only: the ones its counter file is in
    compacted = target.parent == records / "compacted" and target.suffix == ".md"
    if tool == "Read" and compact and target == Path(os.path.normpath(resolve(compact, cwd))):
        return True
    return in_records or compacted


def decide(data: dict[str, Any]) -> Optional[dict[str, Any]]:
    """The hook's JSON answer, or None to allow the call without a word."""
    transcript = subagent_transcript(data)
    if transcript is None:
        return None
    prompt = first_prompt(transcript)
    counter_match = COUNTER_RE.search(prompt)
    if not counter_match:
        return None
    cwd = str(data.get("cwd") or ".")
    counter = resolve(counter_match.group(1), cwd)
    compact_match = COMPACT_RE.search(prompt) or COMPACT_FALLBACK_RE.search(prompt)
    compact = compact_match.group(1) if compact_match else None
    limit, already = read_state(counter)
    tokens = context_tokens(transcript)
    if tokens is None and not already:
        return None
    tripped = already or tokens > limit  # once tripped, this spawn stays tripped; its successor gets a fresh file
    try:
        counter.parent.mkdir(parents=True, exist_ok=True)
        if tokens is not None:
            counter.write_text(f"Context: {tokens}/{limit} tokens" + (" — tripped" if tripped else "") + "\n",
                               encoding="utf-8")
    except OSError:
        pass
    records = Path(os.path.normpath(counter)).parent.parent  # <root>/.records/counters/<file> -> <root>/.records
    if not tripped or handoff_call(data, compact, cwd, records):
        return None
    size = f"your context is {tokens} tokens, past" if tokens is not None else "your context passed"
    reason = (f"Safety-Net tripped: {size} the limit of {limit}. Stop the work now. "
              f"Read the compact body named in your prompt under \"Compact instructions\""
              + (f" ({compact})" if compact else "")
              + " and follow it: write the compaction file under SDD/.records/compacted/, append the "
                "`## PARTIAL: needs continuation` block to progress.md, and return the handoff. "
                "Use Read, Write and Edit for those (and `date` for the timestamp); every other tool call is refused.")
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                   "permissionDecisionReason": reason}}


def main() -> int:
    try:
        data = json.load(sys.stdin)
        answer = decide(data) if isinstance(data, dict) else None
    except Exception:  # the guard must never stop work it cannot judge
        return 0
    if answer:
        print(json.dumps(answer))
    return 0


if __name__ == "__main__":
    sys.exit(main())
