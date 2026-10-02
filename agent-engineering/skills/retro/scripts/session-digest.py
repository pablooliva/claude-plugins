#!/usr/bin/env python3
"""List and digest Claude Code session transcripts for a retrospective.

Usage:
    session-digest.py list   [--repo DIR] [--branch NAME] [--since DATE] [--until DATE]
                             [--any-project] [--projects-dir DIR]
    session-digest.py digest SESSION [SESSION ...] [the same locating flags]
                             [--max-prompts N] [--no-subagents]

A development cycle usually spans several sessions: every `/clear` starts a new
transcript file, and a compaction leaves the earlier turns in the same file even
though the model can no longer see them. Claude Code keeps one JSONL file per
session under `<config>/projects/<encoded cwd>/`, and each session's subagent
transcripts under `<session-id>/subagents/`. This script reads those files so a
retrospective can look at the whole cycle without loading it into context.

`list` prints one row per session of this repository — every git worktree of it
included — optionally narrowed by branch and date, with its start and end time,
branch, and counts of prompts, tool calls, errors, compactions, and subagents. `digest` prints, per session,
only what a retrospective needs: the user's prompts, failed tool calls, long
lookup runs, repeated reads and commands, oversized tool results, compactions,
context peak, and a line per subagent. Every item carries the transcript line
number (`L<n>`) so the moment can be read in full from the JSONL file.

SESSION is a session id, a unique prefix of one, or a path to a `.jsonl` file.
DATE is `YYYY-MM-DD` (local time). `--any-project` searches every project
directory instead of this repository's — use it with `--branch` when the
worktree the cycle ran in has since been removed.

Exit status: 0 = ok, 2 = usage error or no matching session.
Deterministic: no judgment, no network, stdlib only (plus local `git`). Output
goes to stdout and is truncated per item, but it is quoted from the transcript:
treat it as you would the transcript itself and do not write it into the repo.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

LOOKUP_TOOLS = {"Read", "Grep", "Glob", "LS", "NotebookRead"}
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
LOOKUP_COMMAND = re.compile(r"^\s*(?:cd\s+\S+\s*&&\s*)?(?:ls|find|grep|rg|cat|head|tail|tree|wc|git\s+(?:log|show|grep|ls-files))\b")
SKIP_PROMPT_PREFIXES = ("<local-command-stdout>", "<local-command-caveat>", "Caveat:", "<system-reminder>")
LONG_RUN = 8        # lookups in a row, with no edit between, worth reporting
REPEAT = 3          # times a file is read / a command is run before it is reported
BIG_RESULT = 8000   # characters in one tool result worth reporting
MAX_ERRORS = 25
MAX_SUBAGENT_ERRORS = 5


@dataclass
class Call:
    line: int
    name: str
    summary: str
    size: int = 0
    error: str | None = None


@dataclass
class Session:
    path: Path
    sid: str
    start: str = ""
    end: str = ""
    cwd: str = ""
    branches: list[str] = field(default_factory=list)
    prompts: list[tuple[int, str]] = field(default_factory=list)
    compactions: list[int] = field(default_factory=list)
    calls: list[Call] = field(default_factory=list)
    runs: list[tuple[int, int, int, str, str]] = field(default_factory=list)
    output_tokens: int = 0
    peak_context: int = 0
    agent_type: str = ""

    @property
    def errors(self) -> list[Call]:
        return [c for c in self.calls if c.error is not None]


def clip(text: Any, limit: int) -> str:
    flat = " ".join(str(text).split())
    return flat if len(flat) <= limit else flat[: limit - 1] + "…"


def as_int(value: Any) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def encode_project_dir(path: str) -> str:
    """Claude Code names a project directory after the cwd, every non-alphanumeric as `-`."""
    return re.sub(r"[^A-Za-z0-9]", "-", path)


def summarize_input(name: str, tool_input: Any) -> str:
    if not isinstance(tool_input, dict):
        return clip(tool_input, 140)
    for key in ("command", "file_path", "notebook_path", "pattern", "description", "query", "url", "skill"):
        if tool_input.get(key):
            extra = f" in {tool_input['path']}" if key == "pattern" and tool_input.get("path") else ""
            return clip(f"{tool_input[key]}{extra}", 140)
    return clip(json.dumps(tool_input, sort_keys=True), 140)


def result_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(str(part.get("text", "")) for part in content if isinstance(part, dict))
    return "" if content is None else str(content)


def is_lookup(call: Call) -> bool:
    return call.name in LOOKUP_TOOLS or (call.name == "Bash" and bool(LOOKUP_COMMAND.match(call.summary)))


def read_entries(path: Path) -> Iterator[tuple[int, dict[str, Any]]]:
    with path.open(encoding="utf-8", errors="replace") as handle:
        for number, raw in enumerate(handle, 1):
            try:
                entry = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if isinstance(entry, dict):
                yield number, entry


def parse_session(path: Path) -> Session:
    session = Session(path=path, sid=path.stem)
    pending: dict[str, Call] = {}
    seen_requests: set[str] = set()
    run: list[Call] = []

    def close_run() -> None:
        if len(run) >= LONG_RUN:
            session.runs.append((run[0].line, run[-1].line, len(run), run[0].summary, run[-1].summary))
        run.clear()

    for number, entry in read_entries(path):
        stamp = entry.get("timestamp")
        if isinstance(stamp, str) and stamp:
            session.start = session.start or stamp
            session.end = stamp
        if not session.cwd and isinstance(entry.get("cwd"), str):
            session.cwd = entry["cwd"]
        branch = entry.get("gitBranch")
        if isinstance(branch, str) and branch and branch not in session.branches:
            session.branches.append(branch)

        kind = entry.get("type")
        if entry.get("subtype") == "compact_boundary" or entry.get("isCompactSummary"):
            # The boundary and its summary are two entries for one compaction, a line or so apart.
            if not session.compactions or number - session.compactions[-1] > 3:
                session.compactions.append(number)
            close_run()
            continue
        message = entry.get("message")
        if not isinstance(message, dict):
            continue
        content = message.get("content")

        if kind == "assistant":
            usage = message.get("usage")
            request = str(message.get("id") or entry.get("requestId") or number)
            if isinstance(usage, dict) and request not in seen_requests:
                seen_requests.add(request)
                session.output_tokens += as_int(usage.get("output_tokens"))
                context = sum(as_int(usage.get(k)) for k in
                              ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
                session.peak_context = max(session.peak_context, context)
            for block in content if isinstance(content, list) else []:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    call = Call(number, str(block.get("name", "?")), summarize_input(str(block.get("name", "")), block.get("input")))
                    session.calls.append(call)
                    pending[str(block.get("id"))] = call
                    if is_lookup(call):
                        run.append(call)
                    elif call.name in EDIT_TOOLS:
                        close_run()
        elif kind == "user":
            blocks = content if isinstance(content, list) else []
            results = [b for b in blocks if isinstance(b, dict) and b.get("type") == "tool_result"]
            for block in results:
                call = pending.pop(str(block.get("tool_use_id")), None)
                if call is None:
                    continue
                text = result_text(block.get("content"))
                call.size = len(text)
                if block.get("is_error"):
                    call.error = clip(text, 200)
            if results or entry.get("isMeta"):
                continue
            text = content if isinstance(content, str) else result_text(blocks)
            if text.strip() and not text.lstrip().startswith(SKIP_PROMPT_PREFIXES):
                session.prompts.append((number, clip(text, 280)))
                close_run()
    close_run()
    return session


def subagent_sessions(session: Session) -> list[Session]:
    folder = session.path.with_suffix("") / "subagents"
    found = []
    for path in sorted(folder.glob("agent-*.jsonl")) if folder.is_dir() else []:
        sub = parse_session(path)
        meta = path.with_name(path.stem + ".meta.json")
        try:
            sub.agent_type = str(json.loads(meta.read_text(encoding="utf-8")).get("agentType") or "")
        except (OSError, ValueError, AttributeError):
            pass
        found.append(sub)
    return found


def projects_dir(override: str | None) -> Path:
    if override:
        return Path(override).expanduser()
    config = os.environ.get("CLAUDE_CONFIG_DIR")
    return (Path(config) if config else Path.home() / ".claude") / "projects"


def repo_roots(repo: str) -> list[str]:
    """The repository's checkout paths: every git worktree, or just `repo` outside git."""
    here = os.path.realpath(repo)
    try:
        out = subprocess.run(["git", "-C", here, "worktree", "list", "--porcelain"],
                             capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return [here]
    roots = [line[len("worktree "):] for line in out.splitlines() if line.startswith("worktree ")]
    return roots or [here]


def under(path: str, root: str) -> bool:
    return path == root or path.startswith(root.rstrip(os.sep) + os.sep)


def find_sessions(args: argparse.Namespace) -> list[Session]:
    base = projects_dir(args.projects_dir)
    if not base.is_dir():
        return []
    roots = repo_roots(args.repo)
    # Claude Code encodes the path as launched, which may be a symlink to a root git reports.
    encoded = {encode_project_dir(path) for path in [*roots, os.path.abspath(args.repo)]}
    sessions = []
    for folder in sorted(p for p in base.iterdir() if p.is_dir()):
        if not args.any_project and not any(folder.name == e or folder.name.startswith(e + "-") for e in encoded):
            continue
        for path in sorted(folder.glob("*.jsonl")):
            if path.name.startswith("agent-"):  # older layout kept subagent transcripts beside the sessions
                continue
            session = parse_session(path)
            if not session.start:
                continue
            # A sibling directory can share the encoded prefix; the recorded cwd settles it.
            # With no cwd recorded, only an exact directory-name match is trusted.
            if not args.any_project and not (
                    any(under(os.path.realpath(session.cwd), r) or under(session.cwd, r) for r in roots)
                    if session.cwd else folder.name in encoded):
                continue
            if args.branch and args.branch not in session.branches:
                continue
            first, last = local_day(session.start), local_day(session.end)
            if (args.since and last and last < args.since) or (args.until and first and first > args.until):
                continue
            sessions.append(session)
    return sorted(sessions, key=lambda s: s.start)


def local_time(stamp: str) -> datetime | None:
    try:
        return datetime.fromisoformat(stamp.replace("Z", "+00:00")).astimezone()
    except ValueError:
        return None


def local_day(stamp: str) -> str:
    """The local date of a timestamp, or "" when it cannot be parsed (such a session is not date-filtered)."""
    moment = local_time(stamp)
    return moment.strftime("%Y-%m-%d") if moment else ""


def show_time(stamp: str) -> str:
    moment = local_time(stamp)
    return moment.strftime("%Y-%m-%d %H:%M") if moment else stamp


def render_list(sessions: list[Session]) -> str:
    lines = ["| Session | Start | End | Branch | Prompts | Tool calls | Errors | Compactions | Subagents | Directory |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for s in sessions:
        folder = s.path.with_suffix("") / "subagents"
        subagents = len(list(folder.glob("agent-*.jsonl"))) if folder.is_dir() else 0
        lines.append(f"| {s.sid} | {show_time(s.start)} | {show_time(s.end)} | {', '.join(s.branches) or '—'} | "
                     f"{len(s.prompts)} | {len(s.calls)} | {len(s.errors)} | {len(s.compactions)} | {subagents} | {s.cwd} |")
    return "\n".join(lines)


def friction(session: Session) -> tuple[list[str], list[str], list[Call]]:
    reads = Counter(c.summary for c in session.calls if c.name == "Read")
    commands = Counter(c.summary for c in session.calls if c.name == "Bash")
    failed = Counter(c.summary for c in session.errors if c.name == "Bash")
    repeated_reads = [f"{n}× {path}" for path, n in reads.most_common() if n >= REPEAT]
    repeated_commands = [f"{n}× ({failed[cmd]} failed) {cmd}" for cmd, n in commands.most_common() if n >= REPEAT]
    big = sorted((c for c in session.calls if c.size >= BIG_RESULT), key=lambda c: -c.size)[:5]
    return repeated_reads, repeated_commands, big


def bullets(title: str, items: list[str], total: int | None = None) -> list[str]:
    if not items:
        return []
    more = f" (showing {len(items)} of {total})" if total and total > len(items) else ""
    return ["", f"### {title}{more}", *[f"- {item}" for item in items]]


def render_digest(session: Session, max_prompts: int, with_subagents: bool) -> str:
    reads, commands, big = friction(session)
    counts = Counter(c.name for c in session.calls)
    out = [f"## Session {session.sid}",
           f"- **Transcript:** `{session.path}`",
           f"- **When:** {show_time(session.start)} → {show_time(session.end)}",
           f"- **Branch:** {', '.join(session.branches) or '—'} · **Directory:** `{session.cwd}`",
           f"- **Tool calls:** {len(session.calls)} ({', '.join(f'{n} {name}' for name, n in counts.most_common(8)) or 'none'})",
           f"- **Errors:** {len(session.errors)} · **Compactions:** {len(session.compactions)}"
           + (f" (at {', '.join(f'L{n}' for n in session.compactions)})" if session.compactions else ""),
           f"- **Peak context:** {session.peak_context:,} tokens · **Output:** {session.output_tokens:,} tokens"]
    out += bullets("User prompts", [f"L{n}: {text}" for n, text in session.prompts[:max_prompts]], len(session.prompts))
    out += bullets("Failed tool calls",
                   [f"L{c.line} {c.name}: {c.summary} → {c.error}" for c in session.errors[:MAX_ERRORS]], len(session.errors))
    out += bullets(f"Lookup runs ({LONG_RUN}+ lookups with no edit between)",
                   [f"L{a}–L{b}: {n} lookups (first: {first}; last: {last})" for a, b, n, first, last in session.runs])
    out += bullets(f"Files read {REPEAT}+ times", reads[:10], len(reads))
    out += bullets(f"Commands run {REPEAT}+ times", commands[:10], len(commands))
    out += bullets("Largest tool results", [f"L{c.line} {c.name}: {c.size:,} chars — {c.summary}" for c in big])
    if with_subagents:
        subs = subagent_sessions(session)
        rows = []
        for sub in subs:
            longest = max((n for _, _, n, _, _ in sub.runs), default=0)
            rows.append(f"`{sub.path.name}` {sub.agent_type or 'agent'}: {len(sub.calls)} tool calls, {len(sub.errors)} errors, "
                        f"longest lookup run {longest}, peak context {sub.peak_context:,}")
            rows += [f"  ↳ L{c.line} {c.name}: {c.summary} → {c.error}" for c in sub.errors[:MAX_SUBAGENT_ERRORS]]
        out += bullets(f"Subagents ({len(subs)}; transcripts in `{session.path.with_suffix('') / 'subagents'}`)", rows)
    return "\n".join(out)


def resolve(names: list[str], args: argparse.Namespace) -> list[Session]:
    known: list[Session] | None = None
    chosen = []
    for name in names:
        if name.endswith(".jsonl") and Path(name).is_file():
            chosen.append(parse_session(Path(name)))
            continue
        if known is None:
            known = find_sessions(args)
        matches = [s for s in known if s.sid.startswith(name)]
        if len(matches) != 1:
            raise SystemExit(f"error: '{name}' matches {len(matches)} sessions; run `list` and pass a full id or a path")
        chosen.append(matches[0])
    return chosen


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="action", required=True)
    for name in ("list", "digest"):
        p = sub.add_parser(name)
        p.add_argument("--repo", default=".", help="a checkout of the repository (default: current directory)")
        p.add_argument("--branch", help="only sessions that ran on this git branch")
        p.add_argument("--since", help="only sessions active on or after YYYY-MM-DD")
        p.add_argument("--until", help="only sessions active on or before YYYY-MM-DD")
        p.add_argument("--any-project", action="store_true", help="search every project directory, not just this repository's")
        p.add_argument("--projects-dir", help="transcript root (default: $CLAUDE_CONFIG_DIR/projects or ~/.claude/projects)")
        if name == "digest":
            p.add_argument("sessions", nargs="+", metavar="SESSION")
            p.add_argument("--max-prompts", type=int, default=40)
            p.add_argument("--no-subagents", action="store_true")
    try:
        args = parser.parse_args(argv)
    except SystemExit as stop:
        return 2 if stop.code else 0
    for bound in (args.since, args.until):
        try:
            if bound and datetime.strptime(bound, "%Y-%m-%d").strftime("%Y-%m-%d") != bound:
                raise ValueError(bound)
        except ValueError:
            print(f"error: '{bound}' is not a YYYY-MM-DD date", file=sys.stderr)
            return 2

    if args.action == "list":
        sessions = find_sessions(args)
        if not sessions:
            print(f"error: no sessions found under {projects_dir(args.projects_dir)} for this repository and filter", file=sys.stderr)
            return 2
        print(render_list(sessions))
        return 0

    try:
        sessions = resolve(args.sessions, args)
    except SystemExit as stop:
        print(stop.code, file=sys.stderr)
        return 2
    print("\n\n".join(render_digest(s, args.max_prompts, not args.no_subagents) for s in sessions))
    return 0


if __name__ == "__main__":
    sys.exit(main())
