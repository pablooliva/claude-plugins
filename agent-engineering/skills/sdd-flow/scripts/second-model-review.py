#!/usr/bin/env python3
"""Run one sdd-flow review step on Codex, the second model, through its command-line agent.

Usage:
    second-model-review.py resolve
    second-model-review.py prompt --cwd <repo root> --calls-dir <dir> --step <step-id> --iter <iter>
                                  --role <role file> --reviewer <reviewer line> --body <body file>
                                  --compact <compact body file>
                                  [--value NAME=VALUE ...] [--line TEXT ...] [--input NAME=PATH ...]
                                  [--output NAME=PATH ...] [--text-file PATH ...]
    second-model-review.py run --prompt-file <path> --cwd <repo root>
                               --expect <path> [--expect <path> ...] [--timeout <seconds>]

The flow's research, specs, and code are written by Claude subagents; a review
is run by a different model family (`references/second-model-review.md`). This
script is the one place that knows how the reviewer's CLI is called.

`resolve` settles the reviewer for a whole cycle: `codex` when that CLI is on
PATH, else `claude (fallback — <reason>)`, the caller's Claude reviewer. The
first stdout line is `Result: <answer>`.

`prompt` writes a review step's prompt file,
`<calls-dir>/<step-id>-<iter>-<YYYY-MM-DD_HH-MM-SS>.prompt.md`, and names it in
the result line. In order: the reviewer preamble (its one copy is PREAMBLE below)
with the role file and the reviewer line filled in; the body file; the compact
body, the instructions the reviewer follows only if it hands off; every text
file's content as it is (a rule to embed verbatim, an owner's decision, a note on
where the records live); the values (`NAME = VALUE`); the lines as given (a gate
line, say); the inputs (a name given again adds a path: `VOID RUNS`); the outputs.
Paths are written absolute; a relative one is taken from `--cwd`. It refuses
(exit 2, nothing written) a role, body, compact or text file that is not an existing
file, an input that does not exist, a name given twice (VOID RUNS alone may repeat), a text file that is not
UTF-8, and a name, value, path or line holding a line break; an output need not
exist, but its folder must. The calls folder is created when missing; a prompt
file is never overwritten.

`run` gives the prompt file's text to Codex and waits. Beside the prompt
file (`<name>.prompt.md`) it writes `<name>.log` (everything the CLI printed)
and `<name>.return.md` (the reviewer's final message). The run counts only if:

- the CLI exits 0 within the timeout (default 3600 s);
- the reviewer's answer carries the status line `REVIEW: COMPLETE` (the last line
  that starts with `REVIEW: ` decides; an answer with no such line does not count);
- every `--expect` file exists, is not empty, and was written during the run.

A run that fails is undone, and what it wrote is kept: each `--expect` file it
wrote during the run is copied beside itself as `<name>.attempt<N>-void.md` (N the
next free number), named in the result line, and then put back as it was before
the run — removed if it did not exist — so a review the step appends to, or a
partial one a continuation resumes, holds nothing of the failed run. The next run
of the step checks the copies' findings (`references/second-model-review.md` §3).

A status line `REVIEW: HANDOFF — <compaction file>` is neither a pass nor a
failure: the reviewer saw it could not finish every step in this session and wrote
a compaction file, and the caller continues the review (exit 4). The `--expect`
files are not checked and are left in place, for the continuation to finish. The
compaction file it names (a relative path is taken from `--cwd`) must exist and
not be empty; if it does not, the run fails (exit 1) like any other.

Codex runs in its `workspace-write` sandbox with network access on
(`-c sandbox_workspace_write.network_access=true`), so a test suite that opens
a local port or calls a local service can run.

A review changes no code. Before the run the script records the working tree
(every tracked and untracked, non-ignored file) as a git tree object, without
touching the index; afterwards it puts back every file outside `SDD/` that the
reviewer left changed, added, or deleted — a mutation it did not restore — and
names them in the result line. If the tree cannot be recorded the reviewer is
not started, and a file that cannot be put back fails the run. A timeout, or a
SIGTERM or SIGINT sent to this script, stops the reviewer and everything it
started, and the files are put back before the script exits. The record is a
git tree: where git rewrites content (line-ending conversion, clean/smudge
filters) a file is put back as git checks it out, not necessarily byte for byte.

The first stdout line is `Result: ...`. Exit status: 0 = the answer is a second
model (`resolve`) or the review counts (`run`); 3 = `resolve` answered `claude`;
1 = the run does not count; 4 = the review must be continued (`HANDOFF`);
2 = usage or input error.
$SDD_FLOW_REVIEWER_ARGS, when set, is split like a shell line and appended to
the CLI's arguments (a model, say, or what a container needs). Deterministic apart from the reviewer itself; stdlib only.
"""
from __future__ import annotations

import argparse
import os
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

DEFAULT_TIMEOUT = 3600
STATUS = "REVIEW: "
COMPLETE = "REVIEW: COMPLETE"
HANDOFF = "REVIEW: HANDOFF"
KEPT_DIR = "SDD"
CLI = "codex"
LABEL = "codex"
NETWORK_ON = "sandbox_workspace_write.network_access=true"


class InputError(Exception):
    """An argument is unusable."""


class Cancelled(Exception):
    """The script was told to stop (SIGTERM or SIGINT) while the reviewer was running."""


def cancel(signum: int, frame: object) -> None:
    raise Cancelled()


class GuardError(Exception):
    """The working tree could not be recorded or put back."""


def resolve() -> tuple[str, int]:
    if shutil.which(CLI):
        return LABEL, 0
    return "claude (fallback — the codex CLI is not on PATH)", 3


def command(cwd: Path, return_file: Path) -> list[str]:
    """Codex takes the prompt on stdin."""
    extra = shlex.split(os.environ.get("SDD_FLOW_REVIEWER_ARGS", ""))
    argv = [CLI, "exec", "-s", "workspace-write", "-C", str(cwd), "-o", str(return_file)]
    argv += ["-c", NETWORK_ON]  # explicit: a config file may turn it off
    return argv + extra + ["-"]


def git(cwd: Path, *args: str, index: Path | None = None, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    if index is not None:
        env["GIT_INDEX_FILE"] = str(index)
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, env=env, input=stdin)


def snapshot(cwd: Path, index: Path) -> str:
    """Write the working tree to a tree object through a scratch index, leaving the real index alone."""
    tracked = git(cwd, "ls-files", "-z", "--full-name")
    if tracked.returncode != 0:
        raise GuardError("not a git repository, so the working tree cannot be recorded")
    top = git(cwd, "rev-parse", "--show-toplevel").stdout.strip()
    # The scratch index starts empty, so every file is hashed afresh (a copied index would be
    # trusted on file size and time). `add -A` takes what is not ignored; the second step takes
    # each tracked file by name, because a tracked file that also matches .gitignore is skipped by the first.
    steps = [(("add", "-A"), None), (("update-index", "--add", "--remove", "-z", "--stdin"), tracked.stdout), (("write-tree",), None)]
    for step, feed in steps:
        done = git(top, *step, index=index, stdin=feed)
        if done.returncode != 0:
            raise GuardError(f"git {step[0]} failed while recording the working tree ({done.stderr.strip()[:200]})")
    return done.stdout.strip()


def restore_code(cwd: Path, before: str, scratch: Path) -> list[str]:
    """Put back every file outside SDD/ that differs from the `before` tree; return their paths."""
    after = snapshot(cwd, scratch / "after-index")
    if after == before:
        return []
    diff = git(cwd, "diff-tree", "-r", "--name-status", "--no-renames", "-z", before, after)
    fields = [f for f in diff.stdout.split("\0") if f]
    changed = [(fields[i], fields[i + 1]) for i in range(0, len(fields) - 1, 2)]
    prefix = git(cwd, "rev-parse", "--show-prefix").stdout.strip()
    top = Path(git(cwd, "rev-parse", "--show-toplevel").stdout.strip())
    kept = f"{prefix}{KEPT_DIR}/"
    left = [(status, path) for status, path in changed if not path.startswith(kept)]
    put_back = [path for status, path in left if status != "A"]
    names = sorted(path for _, path in left)
    try:
        if put_back:
            index = scratch / "restore-index"
            for step in (("read-tree", before), ("checkout-index", "-f", "--", *put_back)):
                done = git(top, *step, index=index)
                if done.returncode != 0:
                    raise OSError(done.stderr.strip()[:200])
        for status, path in left:
            if status == "A":
                (top / path).unlink(missing_ok=True)
    except OSError as exc:
        raise GuardError(f"could not put back {', '.join(names)} ({exc})") from exc
    return names


def stop_group(proc: subprocess.Popen[str]) -> None:
    """Stop the reviewer and everything it started; wait until they are gone."""
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(proc.pid, sig)
        except ProcessLookupError:
            return
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            continue
        time.sleep(0.5)  # the leader is gone; give the rest of the group a moment to follow


def run(args: argparse.Namespace) -> tuple[str, int]:
    prompt_file, cwd = Path(args.prompt_file).resolve(), Path(args.cwd).resolve()
    if not prompt_file.is_file():
        raise InputError(f"prompt file not found: {prompt_file}")
    if not cwd.is_dir():
        raise InputError(f"not a directory: {cwd}")
    stem = prompt_file.name.removesuffix(".md").removesuffix(".prompt")
    log_file = prompt_file.with_name(f"{stem}.log")
    return_file = prompt_file.with_name(f"{stem}.return.md")
    return_file.unlink(missing_ok=True)
    label = LABEL
    expected = [Path(p) if os.path.isabs(p) else cwd / p for p in args.expect]
    stamps = {p: p.stat().st_mtime_ns if p.is_file() else None for p in expected}
    originals = {p: p.read_bytes() if p.is_file() else None for p in expected}
    argv, stdin = command(cwd, return_file), prompt_file.read_text()

    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp)
        try:
            before = snapshot(cwd, scratch / "before-index")
        except GuardError as exc:
            return f"FAILED — {label}: not started — {exc}", 1
        failure = None
        try:
            # Its own session, so that on a timeout every process it started is stopped with it —
            # a test run still writing files would undo the restore below.
            proc = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    text=True, cwd=cwd, start_new_session=True)
            try:
                out, err = proc.communicate(stdin, timeout=args.timeout)
            except (subprocess.TimeoutExpired, Cancelled) as exc:
                # Stopped from outside counts too: the reviewer must not outlive this script,
                # and what it left changed is put back below before the script exits.
                signal.signal(signal.SIGTERM, signal.SIG_IGN)
                signal.signal(signal.SIGINT, signal.SIG_IGN)
                stop_group(proc)
                out, err = proc.communicate()
                failure = "cancelled" if isinstance(exc, Cancelled) else f"no answer after {args.timeout} s"
            log_file.write_text(out + ("\n--- stderr ---\n" + err if err else ""))
            if failure is None and proc.returncode != 0:
                failure = f"the {CLI} CLI exited {proc.returncode}"
        except OSError as exc:
            failure = f"the {CLI} CLI could not be started ({exc.strerror})"
        try:
            restored = restore_code(cwd, before, scratch)
        except GuardError as exc:
            return f"FAILED — {label}: {exc}{undo(expected, stamps, originals)}; log: {log_file}", 1

    note = f"; put back {len(restored)} file(s) it left changed: {', '.join(restored)}" if restored else ""
    if failure is None:
        final = return_file.read_text() if return_file.is_file() else ""
        status = next((ln.strip() for ln in reversed(final.splitlines()) if ln.strip().startswith(STATUS)), "")
        if status.startswith(HANDOFF):
            named = status.removeprefix(HANDOFF).strip()
            if named[:1] in ("—", "–", "-") and named[1:2].isspace():  # the separator; a file name may start with a dash
                named = named[1:].strip()
            named = named.strip("`")
            compaction = Path(named) if os.path.isabs(named) else cwd / named
            try:
                written = bool(named) and compaction.is_file() and compaction.stat().st_size > 0
            except OSError:
                written = False
            if written:
                return f"HANDOFF — {label}: {status}{note}; return: {return_file}", 4
            failure = (f"it handed off but the compaction file it names does not exist or is empty: {named}"
                       if named else "it handed off but named no compaction file")
        elif not status:
            failure = "its answer has no `REVIEW: ` status line"
        elif not status.startswith(COMPLETE):
            failure = status
        else:
            for path in expected:
                if not path.is_file() or path.stat().st_size == 0:
                    failure = f"it did not write {path}"
                elif path.stat().st_mtime_ns == stamps[path]:
                    failure = f"{path} was not written during this run"
                if failure:
                    break
    if failure:
        return f"FAILED — {label}: {failure}{note}{undo(expected, stamps, originals)}; log: {log_file}", 1
    return f"OK — {label} reviewed{note}; return: {return_file}", 0


def undo(expected: list[Path], stamps: dict, originals: dict) -> str:
    """After a failed run: copy each expected file it wrote to `<name>.attempt<N>-void.md`, then put the
    file back as it was before the run (removed if it did not exist). Returns the result-line note."""
    kept, stuck = [], []
    for path in expected:
        try:
            if not path.is_file() or path.stat().st_mtime_ns == stamps[path]:
                continue
            base = path.name.removesuffix(".md")
            n = 1
            while (copy := path.with_name(f"{base}.attempt{n}-void.md")).exists():
                n += 1
            shutil.copyfile(path, copy)
            kept.append(str(copy))
            if originals[path] is None:
                path.unlink()
            else:
                path.write_bytes(originals[path])
        except OSError:
            stuck.append(str(path))  # left as the failed run wrote it: the caller is told
    note = f"; kept what it wrote as {', '.join(kept)} and put the file(s) back" if kept else ""
    return note + (f"; could not keep or put back {', '.join(stuck)}" if stuck else "")


PREAMBLE = """You are the reviewer for one step of a development cycle. The work you are reviewing was written by a different model family; you were chosen for that reason — judge it on its merits, with no deference to its author.

1. **Read your role first:** `{role}`. Skip the block between the `---` lines at its top. Where it speaks of a "bounded return to the orchestrator", that is your final message. Where it or any file below names a tool (Read, Grep, Glob), use your own file and shell tools. Start no sub-agent and no other agent session.
2. **Then read the body file the prompt below names.** It is your complete instruction set.
3. **Write only what the prompt below names as an output**, plus your appended entry in `SDD/.records/progress.md` — and, if you hand off, the compaction file and the block the compact instructions name. Change nothing else. Where your instructions have you break code to see a test fail, do it in a scratch copy of the working tree outside the repository, as they say, never in the working tree. Never commit, stash, reset, or check out anything. Never fix what you are reviewing.
4. **Put this line directly under the review document's title:** `Reviewed by: {reviewer}`
5. **Never record a check you could not run as passed.** If you cannot carry out a step your instructions require — a command is blocked, the tests cannot be run, a file is unreadable — say so in the review document at that step, and say when it was the sandbox that stopped it.
6. **Your final message starts with one of three lines, on a line of its own.** `REVIEW: COMPLETE` when you carried out every step. `REVIEW: HANDOFF — <the compaction file you wrote>` when you see that you cannot finish every step in this session — there is no read limit; this is your judgment. Before you end, follow the compact instructions the prompt below names (where they speak of a Safety-Net tripping, read it as your decision to hand off): write the compaction file, listing for each step your instructions require what is done, with its evidence, and what is left; append its `## PARTIAL: needs continuation` block; and leave the review document as far as you wrote it, for the continuation to finish. `REVIEW: INCOMPLETE — <what you could not do>` when a step cannot be done at all — a command is blocked, the tests cannot be run, a file is unreadable. After it, the summary your role file asks for, in 200 words or fewer.

---
"""


REPEATABLE = {"VOID RUNS"}  # the one input that lists several paths (references/second-model-review.md §3)


def pairs(items: list[str] | None, what: str, seen: set[str], repeat: bool = False) -> list[tuple[str, list[str]]]:
    """NAME=VALUE items, a name used once across every kind -- or, with repeat, a REPEATABLE name given again."""
    out: dict[str, list[str]] = {}
    for item in items or []:
        name, sep, value = item.partition("=")
        name = one_line(name, f"a {what} name").strip()
        if not sep or not name or not value:
            raise InputError(f"{what} must be NAME=VALUE: {name or '(empty)'}")
        if name in out and repeat and name in REPEATABLE:
            out[name].append(value)
            continue
        if name in seen:
            raise InputError(f"{name} is given twice")
        seen.add(name)
        out[name] = [value]
    return list(out.items())


def one_line(text: str, what: str) -> str:
    if any(c in text for c in "\n\r\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029"):
        raise InputError(f"{what} holds a line break")
    return text


def existing(path: str, what: str, cwd: Path, kind: str = "file") -> Path:
    try:
        p = (cwd / path).resolve()
    except (OSError, RuntimeError) as exc:
        raise InputError(f"{what} cannot be resolved: {one_line(path, what)}") from exc
    if not (p.is_dir() if kind == "dir" else p.is_file() if kind == "file" else p.exists()):
        raise InputError(f"{what} is not an existing {kind}: {one_line(str(p), what)}")
    return Path(one_line(str(p), what))


def read_text(path: Path, what: str) -> str:
    try:
        with path.open(encoding="utf-8", newline="") as f:  # verbatim: no line-ending change
            return f.read()
    except (OSError, UnicodeDecodeError) as exc:
        raise InputError(f"{what} cannot be read as UTF-8 text: {path}") from exc


def build_prompt(args: argparse.Namespace) -> tuple[str, int]:
    seen: set[str] = set()
    cwd = Path(args.cwd).resolve()
    if not cwd.is_dir():
        raise InputError(f"not a directory: {cwd}")
    for name, what in ((args.step, "--step"), (args.iter, "--iter")):
        if "/" in name or not one_line(name, what).strip():
            raise InputError(f"{what} is not a plain name")
    role = existing(args.role, "the role file", cwd)
    body = existing(args.body, "the body file", cwd)
    compact = existing(args.compact, "the compact body", cwd)
    reviewer = one_line(args.reviewer, "--reviewer")
    values = [(n, one_line(v[0], n)) for n, v in pairs(args.value, "--value", seen)]
    inputs = [(n, [existing(x, n, cwd, "path") for x in v]) for n, v in pairs(args.input, "--input", seen, repeat=True)]
    outputs = []
    for n, v in pairs(args.output, "--output", seen):
        out = Path(one_line(str((cwd / v[0]).resolve()), n))
        if not out.parent.is_dir():
            raise InputError(f"{n}: its folder does not exist: {out.parent}")
        outputs.append((n, out))
    lines = [one_line(t, "a --line") for t in args.line or []]
    texts = [read_text(existing(t, "a text file", cwd), "a text file") for t in args.text_file or []]
    calls = (cwd / one_line(args.calls_dir, "--calls-dir")).resolve()
    try:
        calls.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise InputError(f"the calls folder cannot be made: {calls}") from exc
    parts = [PREAMBLE.format(role=role, reviewer=reviewer),
             f"Read this file FIRST — it is your complete instruction set: {body}",
             f"Compact instructions — use only if you hand off: {compact}"]
    parts.extend(texts)  # as written, final newline included
    if values:
        parts.append("\n".join(f"{n} = {v}" for n, v in values))
    if lines:
        parts.append("\n".join(lines))
    if inputs:
        parts.append("## Inputs\n" + "\n".join(f"- {n}: {', '.join(map(str, ps))}" for n, ps in inputs))
    if outputs:
        parts.append("## Outputs\n" + "\n".join(f"- {n}: {p}" for n, p in outputs))
    text = "\n\n".join(parts) + "\n"
    stamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    for n in range(1, 1000):
        target = calls / f"{args.step}-{args.iter}-{stamp}{'' if n == 1 else f'-{n}'}.prompt.md"
        try:
            with target.open("x", encoding="utf-8", newline="") as f:  # never overwrite, never follow a link
                f.write(text)
            return str(target), 0
        except FileExistsError:
            continue
        except OSError as exc:
            target.unlink(missing_ok=True)  # no partial prompt file left behind
            raise InputError(f"the prompt file cannot be written: {target}") from exc
    raise InputError(f"no free prompt file name in {calls}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("resolve")
    p_prompt = sub.add_parser("prompt")
    for flag in ("--cwd", "--calls-dir", "--step", "--iter", "--role", "--reviewer", "--body", "--compact"):
        p_prompt.add_argument(flag, required=True)
    for flag in ("--value", "--line", "--input", "--output", "--text-file"):
        p_prompt.add_argument(flag, action="append")
    p_run = sub.add_parser("run")
    p_run.add_argument("--prompt-file", required=True)
    p_run.add_argument("--cwd", required=True)
    p_run.add_argument("--expect", action="append", required=True)
    p_run.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    args = parser.parse_args()
    signal.signal(signal.SIGTERM, cancel)
    signal.signal(signal.SIGINT, cancel)
    try:
        if args.action == "resolve":
            line, status = resolve()
        elif args.action == "prompt":
            line, status = build_prompt(args)
        else:
            line, status = run(args)
    except InputError as exc:
        print(f"Result: ERROR — {exc}")
        return 2
    print(f"Result: {line}")
    return status


if __name__ == "__main__":
    sys.exit(main())
