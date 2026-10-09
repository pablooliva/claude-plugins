#!/usr/bin/env python3
"""Run one sdd-flow review step on a second model, through its command-line agent.

Usage:
    second-model-review.py resolve [--reviewer <spec>]
    second-model-review.py run --reviewer <spec> --prompt-file <path> --cwd <repo root>
                               --expect <path> [--expect <path> ...] [--timeout <seconds>]

The flow's research, specs, and code are written by Claude subagents; a review
is run by a different model family (`references/second-model-review.md`). This
script is the one place that knows how each reviewer's CLI is called.

A reviewer spec is one of:
    codex                   the `codex` CLI with its configured model
    codex:<model>           the `codex` CLI with that model
    opencode:<provider/model>   the `opencode` CLI — the model must be named,
                            because opencode's default may be a Claude model
    claude                  no second model: the caller uses its Claude reviewer

`resolve` settles the reviewer for a whole cycle. The spec comes from
`--reviewer`, else from $SDD_FLOW_REVIEWER, else `codex` when that CLI is on
PATH. The first stdout line is `Result: <spec>`; when the answer is `claude` it
is `Result: claude (fallback — <reason>)`, or `Result: claude (chosen)` when the
user asked for it.

`run` gives the prompt file's text to the reviewer and waits. Beside the prompt
file (`<name>.prompt.md`) it writes `<name>.log` (everything the CLI printed)
and `<name>.return.md` (the reviewer's final message). The run counts only if:

- the CLI exits 0 within the timeout (default 3600 s);
- the reviewer's answer carries the status line `REVIEW: COMPLETE` (the last line
  that starts with `REVIEW: ` decides; an answer with no such line does not count);
- every `--expect` file exists, is not empty, and was written during the run.

A status line `REVIEW: HANDOFF` is neither a pass nor a failure: the reviewer hit
its read limit and wrote a compaction file, and the caller continues the review
(exit 4; the `--expect` files are not checked).

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
the CLI's arguments. Deterministic apart from the reviewer itself; stdlib only.
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
CLAUDE_NAMES = ("claude", "anthropic")
KEPT_DIR = "SDD"


class InputError(Exception):
    """The reviewer spec or an argument is unusable."""


class Cancelled(Exception):
    """The script was told to stop (SIGTERM or SIGINT) while the reviewer was running."""


def cancel(signum: int, frame: object) -> None:
    raise Cancelled()


class GuardError(Exception):
    """The working tree could not be recorded or put back."""


def parse_spec(spec: str) -> tuple[str, str]:
    """Return (cli, model); model is '' when the CLI's own default is used."""
    cli, _, model = spec.strip().partition(":")
    cli, model = cli.strip().lower(), model.strip()
    if cli == "claude" and not model:
        return cli, ""
    if cli not in ("codex", "opencode"):
        raise InputError(f"unknown reviewer '{spec}' — use codex, codex:<model>, opencode:<provider/model>, or claude")
    if cli == "opencode" and not model:
        raise InputError("opencode needs a model — opencode:<provider/model>")
    if any(name in model.lower() for name in CLAUDE_NAMES):
        raise InputError(f"'{model}' is a Claude model — the reviewer must be a different model family")
    return cli, model


def resolve(arg: str | None) -> tuple[str, int]:
    spec = arg or os.environ.get("SDD_FLOW_REVIEWER", "").strip()
    if not spec:
        if shutil.which("codex"):
            return "codex", 0
        return "claude (fallback — no reviewer was set and the codex CLI is not on PATH)", 3
    cli, model = parse_spec(spec)
    if cli == "claude":
        return "claude (chosen)", 3
    if not shutil.which(cli):
        return f"claude (fallback — the {cli} CLI is not on PATH)", 3
    return f"{cli}:{model}" if model else cli, 0


def command(cli: str, model: str, cwd: Path, return_file: Path, prompt: str) -> tuple[list[str], str | None]:
    """Return (argv, stdin text). codex takes the prompt on stdin, opencode as an argument."""
    extra = shlex.split(os.environ.get("SDD_FLOW_REVIEWER_ARGS", ""))
    if cli == "codex":
        argv = ["codex", "exec", "-s", "workspace-write", "-C", str(cwd), "-o", str(return_file)]
        if model:
            argv += ["-m", model]
        return argv + extra + ["-"], prompt
    return ["opencode", "run", "--auto", "--dir", str(cwd), "-m", model] + extra + [prompt], None


def reviewer_env(cli: str) -> dict[str, str]:
    """opencode has no write sandbox; refuse its file tools anything outside the repository at least."""
    env = dict(os.environ)
    if cli == "opencode" and "OPENCODE_CONFIG_CONTENT" not in env:
        env["OPENCODE_CONFIG_CONTENT"] = '{"permission": {"external_directory": "deny"}}'
    return env


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
    cli, model = parse_spec(args.reviewer)
    if cli == "claude":
        raise InputError("`run` needs a second-model reviewer; the Claude reviewer is spawned by the orchestrator")
    prompt_file, cwd = Path(args.prompt_file).resolve(), Path(args.cwd).resolve()
    if not prompt_file.is_file():
        raise InputError(f"prompt file not found: {prompt_file}")
    if not cwd.is_dir():
        raise InputError(f"not a directory: {cwd}")
    stem = prompt_file.name.removesuffix(".md").removesuffix(".prompt")
    log_file = prompt_file.with_name(f"{stem}.log")
    return_file = prompt_file.with_name(f"{stem}.return.md")
    return_file.unlink(missing_ok=True)
    label = f"{cli}:{model}" if model else cli
    expected = [Path(p) if os.path.isabs(p) else cwd / p for p in args.expect]
    stamps = {p: p.stat().st_mtime_ns if p.is_file() else None for p in expected}
    argv, stdin = command(cli, model, cwd, return_file, prompt_file.read_text())

    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp)
        try:
            before = snapshot(cwd, scratch / "before-index")
        except GuardError as exc:
            return f"FAILED — {label}: not started — {exc}", 1
        failure = None
        try:
            # Without a prompt on stdin, give the CLI a closed one: opencode waits on an open stdin.
            # Its own session, so that on a timeout every process it started is stopped with it —
            # a test run still writing files would undo the restore below.
            proc = subprocess.Popen(argv, stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=cwd,
                                    start_new_session=True, env=reviewer_env(cli))
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
                failure = f"the {cli} CLI exited {proc.returncode}"
            elif failure is None and cli == "opencode":
                return_file.write_text(out)
        except OSError as exc:
            failure = f"the {cli} CLI could not be started ({exc.strerror})"
        try:
            restored = restore_code(cwd, before, scratch)
        except GuardError as exc:
            return f"FAILED — {label}: {exc}; log: {log_file}", 1

    note = f"; put back {len(restored)} file(s) it left changed: {', '.join(restored)}" if restored else ""
    if failure is None:
        final = return_file.read_text() if return_file.is_file() else ""
        status = next((ln.strip() for ln in reversed(final.splitlines()) if ln.strip().startswith(STATUS)), "")
        if status.startswith(HANDOFF):
            return f"HANDOFF — {label}: {status}{note}; return: {return_file}", 4
        if not status:
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
        return f"FAILED — {label}: {failure}{note}; log: {log_file}", 1
    return f"OK — {label} reviewed{note}; return: {return_file}", 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = parser.add_subparsers(dest="action", required=True)
    p_resolve = sub.add_parser("resolve")
    p_resolve.add_argument("--reviewer")
    p_run = sub.add_parser("run")
    p_run.add_argument("--reviewer", required=True)
    p_run.add_argument("--prompt-file", required=True)
    p_run.add_argument("--cwd", required=True)
    p_run.add_argument("--expect", action="append", required=True)
    p_run.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    args = parser.parse_args()
    signal.signal(signal.SIGTERM, cancel)
    signal.signal(signal.SIGINT, cancel)
    try:
        line, status = resolve(args.reviewer) if args.action == "resolve" else run(args)
    except InputError as exc:
        print(f"Result: ERROR — {exc}")
        return 2
    print(f"Result: {line}")
    return status


if __name__ == "__main__":
    sys.exit(main())
