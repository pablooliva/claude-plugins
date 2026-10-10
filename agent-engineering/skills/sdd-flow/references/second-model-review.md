# Second-Model Review — Who Runs a Review, and How

The one definition of the flow's **review route**. `SKILL.md`, the phase chapters, and `phases/protocols.md` point here and never restate it. The script it describes is `scripts/second-model-review.py`.

**Why this exists.** Every artifact of a cycle — research, spec, code, tests — is written by a Claude subagent. A reviewer of the same model family shares the author's habits and blind spots: what the author did not think to question, the reviewer tends not to question either. So a review is run by a **different model family**, through that model's command-line agent. A fresh context gives a reviewer independence from the author's *reasoning*; a different model gives independence from the author's *tendencies*. The flow wants both.

---

## 1. Which steps are reviews

The review steps that go to the second model are these — at least one for each thing a cycle writes (research, spec, code and tests):

| Step | Review | Body | Role file (`PLUGIN_ROOT/agents/`) |
|---|---|---|---|
| 2c | Research critical review | `bodies/critical-review.md` | `sdd-critical-reviewer.md` |
| 3d | Spec critical review | `bodies/critical-review.md` | `sdd-critical-reviewer.md` |
| 4b | Code review (whole-feature) | `bodies/code-review.md` | `sdd-workhorse.md` |
| per-slice 4b | Slice review | `bodies/slice-review.md` | `sdd-workhorse.md` |
| 4d | Implementation critical review | `bodies/critical-review.md` | `sdd-critical-reviewer.md` |
| 4e.5 step 3 | Final site-verification review | `bodies/code-review.md`, `MODE: site-verification-only` | `sdd-workhorse.md` |

Every re-run of one of these — a re-review after a fix round, a resumed review — is the same step and takes the same route.

**The specialist panel (3c, both stages) stays on Claude subagents.** It is up to eight domain reviews per round and up to three rounds of them; on a second model that is a great many reviewer runs for one spec, whose specialist checklists come from the body file whichever model reads it. The spec is not left to Claude alone: the adversarial spec review that follows the panel (3d) is on the second model, and reads the panel's verdict.

**Not a review step:** the blind site count (4a.5, 4e.5 step 1). It judges nothing; it lists enforcement sites from the SPEC and the code, and its independence comes from what its prompt withholds (`SKILL.md` → Model Routing). It stays a Claude subagent. So does every step that writes or fixes.

## 2. The reviewer is settled once, at Step 0

The orchestrator runs

```
python3 "$SKILL_ROOT/scripts/second-model-review.py" resolve [--reviewer <spec>]
```

passing `--reviewer` only when the user gave `/sdd-flow --reviewer <spec>`. Without it the script reads `$SDD_FLOW_REVIEWER`, and failing that picks `codex` when that CLI is installed. A reviewer spec is `codex`, `codex:<model>`, `opencode:<provider/model>`, or `claude`. OpenCode is used only when named, model included: its default model may be a Claude model, and the script refuses a model whose name says it is one.

The first stdout line is `Result: …`. Write what follows `Result: ` into the Step 0 record as the line `Reviewer: …`, then act on the exit status:

- **0** — a second model reviews. The line is the **REVIEWER** for the whole cycle.
- **3** — the line reads `claude (fallback — <reason>)` or `claude (chosen)`. Every review step of this cycle takes the Claude route (§5). **A recorded line that starts with `claude` means the Claude route, whatever follows the word** — here, on resume, and wherever a file says "REVIEWER is `claude`"; the words after it are kept for the `Reviewed by:` line and are never passed to the script. On a fallback, **tell the user in the next user-facing message**, quoting the line: the cycle's reviews will be Claude reviewing Claude. The flow does not halt.
- **2** — the spec is unusable (an unknown reviewer, OpenCode with no model, a Claude model). Tell the user, quoting the line, and stop before anything is spawned: this is a mistyped argument, not a cycle state, and nothing has been written.

**The answer is taken once.** A resumed session reads the recorded `Reviewer:` line and does not resolve again. A cycle whose Step 0 record has no such line was started before 3.9.0 and finishes on the Claude route, as it began.

## 3. Running a review step on the second model

At a review step, when the recorded reviewer line does not start with `claude`, the orchestrator spawns no subagent. It:

1. **Writes the prompt** to `SDD/orchestration/reviewer-calls/[step-id]-[iter]-[YYYY-MM-DD_HH-MM-SS].prompt.md`: the **reviewer preamble** (§4) with its three values filled in, then exactly the prompt the step's Claude spawn would be given — the body path, every resolved input and output path, `SCOPE`, `ITER`, `BASE`, the gate lines, the Safety-Net Rule with a counter file and compact path where the step carries one. Nothing is left out and nothing is added: the phase chapter's list of what the step is passed is the list.
2. **Runs** — in the background, waiting for it to exit before doing anything else:

   ```
   python3 "$SKILL_ROOT/scripts/second-model-review.py" run --reviewer "<REVIEWER>" \
     --prompt-file <the prompt file> --cwd <the repository root> \
     --expect <each output path the step writes>
   ```

   `--expect` names the step's review document (and nothing optional — not a conventions file or a trace tree that the step may have no reason to write).
3. **Reads the result.** The first stdout line is `Result: …`.
   - **Exit 0 (`OK`)** — the review counts. The reviewer's final message is in the `.return.md` file the line names: read it as the step's bounded return. **Append `## Review Route - [step-id]-[iter]: <the line>` to `progress.md`** — after every `OK`, not only one that put files back. The reviewer writes its own review marker while it is still running, before this script has checked anything; this line is the record that the run was checked, and resume counts a second-model review as done only when it is there (`phases/protocols.md` → Session Resumption). From here the step is indistinguishable from the Claude route — the same review document, the same marker, the same next step.
   - **Exit 1 (`FAILED`)** — the CLI failed, timed out, wrote no review document, reported `REVIEW: INCOMPLETE`, or gave no status line at all. Run it once more with a fresh prompt-file timestamp. If it fails again, run **this step** on the Claude route (§5) — telling that subagent that a review document or marker the failed run left behind is to be written afresh, not trusted — and when it returns append `## Review Route - [step-id]-[iter]: claude (fallback — <the Result line>)` to `progress.md`, and **tell the user in the next user-facing message**, quoting the line. Later review steps try the second model again.
   - **Exit 4 (`HANDOFF`)** — the reviewer tripped its Safety-Net: it wrote a compaction file and the `## PARTIAL: needs continuation` block, and its review document may not exist yet. This is not a failure and is never retried from scratch: continue the review as §6 says.
   - **Exit 2** — the call itself was malformed; fix the call.

**The fallback never halts the flow and is never silent.** A cycle on a machine with no second model, or in a session whose sandbox does not let the reviewer's CLI start or reach its service, still completes — with every such review marked.

**A review changes no code, and the script enforces it.** Before the run it records the working tree — and does not start the reviewer if it cannot (a `FAILED`, like any other); afterwards it puts back every file outside `SDD/` that the reviewer left changed, added, or deleted — typically an enforcement site deleted for a mutation check and not restored — and names them in the result line. The index and the uncommitted work of the cycle are untouched. (The site inventory is under `SDD/`, so the one thing a review writes outside its own document besides the conventions file — the row of a missed site it proved by its own mutation, `references/enforcement-sites.md` §6 — stays; the step's prompt names the inventory as an output for that. Because no code can change in a review, such a row needs no recount.) **One limit:** the record is made with git, so in a repository that rewrites files on the way in or out — line-ending conversion, a clean/smudge filter such as Git LFS — a file is put back as git would check it out, which for an uncommitted file with unusual line endings may not be byte-for-byte what it was. A file it cannot put back fails the run and is named in the line: tell the user at once, before any fallback — the working tree holds a change no step made on purpose. A review with files put back still counts: its findings stand, and a finding that the stray change caused is caught by the re-review that follows the fix.

**One at a time.** No second-model review step is run in parallel with another or with a subagent that writes: each has the working tree to itself, and parallel OpenCode runs fail on its session database.

**Sandbox and permissions.** The two CLIs do not confine a reviewer equally. `codex exec -s workspace-write` runs the reviewer in an operating-system sandbox that allows writes only inside the repository. **OpenCode has no such sandbox:** `opencode run --auto` approves whatever the reviewer asks to do, and the script only denies OpenCode's own file tools paths outside the repository (the `external_directory` permission) — a shell command the reviewer runs can still write anywhere the user can, and nothing outside the repository is recorded or put back. Name OpenCode as the reviewer only on a machine, or inside a container, where that is acceptable. Either CLI has whatever network access its own configuration gives it. `$SDD_FLOW_REVIEWER_ARGS` appends arguments for a project that needs more — a test suite that calls a local service, say. The orchestrator never loosens a sandbox on its own: a run that fails because the session's sandbox or permission settings stopped the CLI is a `FAILED` like any other, and the user is told.

## 4. The reviewer preamble (embed verbatim, values filled in)

> You are the reviewer for one step of a development cycle. The work you are reviewing was written by a different model family; you were chosen for that reason — judge it on its merits, with no deference to its author.
>
> 1. **Read your role first:** `<ROLE FILE>`. Skip the block between the `---` lines at its top. Where it speaks of a "bounded return to the orchestrator", that is your final message. Where it or any file below names a tool (Read, Grep, Glob), use your own file and shell tools. Start no sub-agent and no other agent session.
> 2. **Then read the body file the prompt below names.** It is your complete instruction set.
> 3. **Write only what the prompt below names as an output**, plus your appended entry in `SDD/orchestration/progress.md` and your counter file if one is given. Change nothing else. Where your instructions have you delete code to see a test fail, restore it before you go on, and confirm the file is exactly what it was before you broke it (keep a copy, or compare `git diff -- <file>` taken before and after — the work under review is uncommitted, so that diff is not empty to begin with). Never commit, stash, reset, or check out anything. Never fix what you are reviewing.
> 4. **Put this line directly under the review document's title:** `Reviewed by: <REVIEWER>`
> 5. **Never record a check you could not run as passed.** If you cannot carry out a step your instructions require — a command is blocked, the tests cannot be run, a file is unreadable — say so in the review document at that step.
> 6. **Your final message starts with one of three lines, on a line of its own.** `REVIEW: COMPLETE` when you carried out every step. `REVIEW: HANDOFF — <the compaction file you wrote>` when the Safety-Net Rule in the prompt below fired and you followed its compact instructions. `REVIEW: INCOMPLETE — <what you could not do>` in every other case. After it, the summary your role file asks for, in 200 words or fewer.
>
> ---

`<ROLE FILE>` is the absolute path from the table in §1; `<REVIEWER>` is the recorded reviewer line.

## 5. The Claude route

The route for a cycle whose reviewer is `claude`, and for a single step whose second-model run failed twice. The step's review is spawned as the subagent the phase chapter names — `agent-engineering:sdd-critical-reviewer` or `agent-engineering:sdd-workhorse` — exactly as before 3.9.0, with one line added to its prompt:

> Put this line directly under the review document's title: `Reviewed by: <the recorded reviewer line, or "claude (fallback — second-model run failed)" for a single step>`

Every review document therefore says who reviewed it, whichever route wrote it.

## 6. What a continuation of a review does

A review that trips the Safety-Net writes its compaction file and `## PARTIAL: needs continuation` block like any other step (`phases/protocols.md` → Mid-Phase Handoff). Its continuation takes the same route as the run it continues. On the second model the run ends with `REVIEW: HANDOFF` and the script exits 4; the orchestrator then writes the continuation prompt — the preamble, `bodies/continue.md` as the body, the same role file, the compaction file, and every input the first run was given, with a fresh counter — to a new prompt file and runs it through §3 with the same `--expect`. A continuation may hand off again. A continuation that fails is handled as any failed run: once more, then this step on the Claude route, whose continuation subagent is given the same compaction file.
