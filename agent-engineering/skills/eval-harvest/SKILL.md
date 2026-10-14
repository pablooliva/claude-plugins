---
name: eval-harvest
description: "INVOKE THIS SKILL when the user wants answers that went wrong in real use turned into eval cases — e.g. '/eval-harvest', 'harvest evals', 'turn the answers I marked into eval cases', 'make cases from the bad traces', 'what did users hit in this tier'. Run after a shipped tier has been used, at a moment when no `/sdd-flow` cycle is running. Lists the traces a person marked in Opik (a score, a tag, or a comment) through the application's own trace lookup, reads the model call of each one the user picks, and drafts an invented stand-in case with the same failure — hard where a rule can catch it, judged otherwise — written by the plugin's evals standard (`sdd-flow/references/evals.md`). The user approves each case in full. Approved cases go to one harvest file, `SDD/flow/HARVEST-[name]-[date].md`, and one dated line in the tier plan's `## Feedback`; the next cycle's design brief adopts each one — or defers it to a later tier, or drops it when the brief changes what it checks — and the implementer's first eval run shows whether an adopted one still fails. Real text never leaves Opik: it is not quoted in the conversation, the harvest file, or the spec. Never writes `evals/cases.jsonl`, never edits application code, makes no model call, never commits. Opik and Python applications with the tracing foundation only."
---

# Eval Harvest

Turns answers that went wrong in real use into eval cases for the next tier, without any real user's text ending up in the repository.

A person uses the shipped tier, and marks the answers that were wrong in Opik's web page — a feedback score, a tag, or a comment saying what was wrong. This skill collects those traces, and for each one drafts an **invented stand-in**: a new input, written from scratch, that should make the application fail in the same way. The stand-in is what becomes a case. The real request and answer stay in Opik.

Why a stand-in and not the real text: the evals standard requires every case input to be "an invented example ... never text taken from a real user" (`sdd-flow/references/evals.md` §2). Cases are committed, sent to Opik as a dataset at every review, and read by every reviewer.

Why it proposes and does not write `evals/cases.jsonl`: a case is written in a spec, under a requirement, and reviewed with that spec (§2). A case put straight into the file would be an "older case" to every later review: run every time, never judged as a case, and — because it fails today — failing the review of every unrelated feature until someone fixes it. So this skill writes a harvest file; the next cycle's design brief settles each case — adopted into the spec's `### Evals`, deferred to a later tier, or dropped because the brief changes what it checks; and that cycle's implementer makes its first eval run before changing anything for them, which shows whether each stand-in really fails (§2, *A case harvested from a real trace*).

Bundled files: none. It reads through the application's trace lookup (`scripts/trace_lookup.py`, rendered by `/observability-init`; its rules are `observability-init/references/tracing.md` → *Reading a trace back*), and drafts cases by `sdd-flow/references/evals.md` §1–§2 — read both before Step 4. Both paths are relative to this plugin's `skills/` directory.

## Anti-Pattern Watchlist

1. **Copying the real text into a case.** Pasting the user's question, the material, or the model's answer into the stand-in, or "lightly editing" it. Resolution: the input is written from scratch — other names, other numbers, another subject where the failure allows — and only the *shape* of the failure is kept (Step 4).
2. **Quoting the real text anywhere.** In the conversation, in the harvest file's description of what went wrong, in the tier plan. A mark's comment or a score's reason counts as real text too: the person who marked the answer may have quoted it. Resolution: say what went wrong in your own words and in terms of the stand-in; point the user to the trace in Opik for the original. Names and counts only. Read the marks of a trace only once the user has picked it (Step 4). **What does enter your own context** is a picked trace's model call and marks — a stand-in is drafted from them, and nothing else can show what went wrong. That is accepted; it goes no further than your context, and no other trace's text enters it.
3. **Leaving the real text on disk.** The model call written with `--out` into the repository, or left behind. Resolution: one temporary directory outside the repository for the whole run; each model-call file is deleted as soon as its draft is written, and the directory in Step 7 — or at once, whenever the skill stops early.
4. **Writing into `evals/cases.jsonl`, the spec, or application code.** Resolution: the harvest file and one `## Feedback` line are the only things this skill writes.
5. **A check that only matches this one answer.** A hard case whose "must not contain" is the exact wrong sentence the model happened to write. It passes the next time the model words the same mistake differently. Resolution: the check names what makes the answer wrong — the stated result, the made-up figure, the missing refusal — in words a rule can apply (§2).
6. **Judged where a rule would do.** Resolution: ask first what a rule could check (§1, *Prefer hard*); a judged case only for what no rule can decide, and say so.
7. **A case for something that is not the model's answer.** A request that crashed, a timeout, a wrong status code. Resolution: that is a bug for a test. Step 3 sends it to the trace lookup's debugging use, not into a case.
8. **Harvesting a trace twice.** Resolution: Step 2 skips any trace ID already named in an existing harvest file.
9. **Treating every mark as "bad".** A score can say an answer was good. Resolution: the user picks which marked traces were wrong answers, from what Opik shows them (Step 3).
10. **Claiming the stand-in reproduces the failure.** Nothing has run it. Resolution: the harvest file says "not yet seen to fail", and the next cycle's first eval run is what settles it.

## When to Activate

- The user has used a shipped tier, marked wrong answers in Opik, and wants them to become cases.
- The user asks what the marked traces were, with a view to the next tier.

## When NOT to Activate

- **A `/sdd-flow` cycle is running** — say so and stop; run it after the cycle is done.
- **No tracing foundation, or no trace lookup** — `SDD/OBSERVABILITY.md` missing, or it has no `Trace lookup` row: say `/observability-init` (audit mode for the second) is what installs it, and stop.
- **The tracing backend is not Opik** — the trace lookup reads Opik only. Say so and stop.
- **To debug one failed request** — that is the trace lookup itself (the *Debugging with traces* paragraph in the application's agent instructions).
- **To write cases for a feature still being planned** — the spec's planning writes those.

## Behavioral Instructions

Execute in order. Quote every path. Make no model call.

### Step 1: Verify context

```bash
git rev-parse --show-toplevel                           # fails → not a repo; stop
tail -40 SDD/orchestration/progress.md 2>/dev/null
cat SDD/OBSERVABILITY.md 2>/dev/null
ls SDD/flow/TIERS-*.md SDD/flow/HARVEST-*.md 2>/dev/null
ls evals/cases.jsonl 2>/dev/null
```

- **A cycle is running** when `progress.md` names a feature in progress, or its latest block is a pending `## Awaiting …`. Stop and tell the user.
- From `SDD/OBSERVABILITY.md` take: the `Trace lookup` command (no row → stop, as above); `Tracing backend now` (not Opik → stop); and the section `## This application's own rules`. **If those rules forbid a person or an agent from reading what users sent, stop** and quote the rule: harvesting means reading one model call's text.
- **The feature.** One tier plan → that feature. Several → ask which feature the traces belong to. None → ask the user for a short name for the harvest file, and say that with no tier plan the next `/sdd-flow` task has to name the file itself.
- **The spec.** With a tier plan, the spec is the one its `Built in` column names for the latest shipped tier. Without one, ask the user which spec in `SDD/requirements/` describes what the traces did, or whether none does. Read its requirements, and its `### Evals` if any, so a stand-in can name the requirement it is about as `REQ-XXX of SPEC-YYY`. No spec → every case's requirement is "none yet".
- **The next free eval ID is not yours to give.** Do not number cases `EVAL-…`; the next spec does.

### Step 2: List the marked traces

```bash
<the lookup command> --marked
```

- Nothing listed → tell the user how to mark one (open the trace in Opik; add a feedback score, a tag, or a comment saying what was wrong), say `--marked --scan 2000` reaches further back if the marks are older, and stop.
- Drop every trace whose ID already appears in an existing `SDD/flow/HARVEST-*.md` (`grep -l <id> SDD/flow/HARVEST-*.md`), and say how many were dropped.

### Step 3: The user picks

Show the `--marked` list as it printed: one line per trace — time, entry point, status, model calls, how many marks of each kind, the trace ID. It holds nothing anyone wrote. Ask the user which were wrong answers to harvest: they see each trace's marks in Opik, by its time or ID. Do not print a trace's call tree to help them — it prints the marks' text. Then:

- **No model call in the list line** → not a case: say it is a bug for a test, and give the command that shows where it failed (`<the lookup command> <trace id>`, for the user to run).
- Keep the rest, in the order the user gave.

### Step 4: Draft a stand-in for each

Make one temporary directory for the whole run, outside the repository:

```bash
mktemp -d
```

Call the path it prints `<tmp>`, and write it out in full in every later command — a shell variable does not survive from one command to the next. Every early stop from here on removes it first: `rm -rf "<tmp>"`.

Then, one trace at a time:

```bash
<the lookup command> <trace id> --model-call --out "<tmp>/<trace id>.json"
```

That prints the trace's call tree, its marks — scores with their reasons, tags, comments — and where the failure started: read them, never repeat them. The file is `{"trace": "<id>", "calls": [ … ]}`, one entry per model call in the order the call tree shows them — the second model call in the tree is the second entry — each with `model`, `messages` (what was sent), `answer` (what came back), and `failed`.

- **The call to harvest** is the one whose `answer` the person marked. With one entry that has an `answer`, that one. With several, ask the user which one — first, second, … as the call tree just printed shows them, which is the entries' order — and never pick one yourself.
- **Not a case** — say so, delete the file, and go to the next trace — when every entry's `messages` and `answer` are empty (the content switch was off when the trace was recorded), or when no entry has an `answer` (the model call failed or never returned: a bug for a test).

Decide, in your own words:

1. **What went wrong** — one sentence about the answer, not about the user: "states the final result instead of leading to it", "names a figure that is not in the material", "answers a question the material does not cover instead of saying so".
2. **The requirement it breaks** — always the behaviour in one sentence, which is what the next spec reads; before it, a requirement ID of the spec when one says this, otherwise "none yet". The next spec states the behaviour as a requirement of its own.
3. **Hard or judged** — hard when a rule can tell the wrong answer from a right one (§1); judged only for what no rule can decide.

Then write the stand-in, by §2:

- **Input** — every part by the name the entry point takes it under, written out in full and invented. Keep what made the application fail — the kind of question, the length, the shape of the material, the language — and change everything that came from the user. Choose content whose right answer cannot be reached without the behaviour: a made-up fact, a made-up figure.
- **Hard:** **Must contain** / **Must not contain** — what a right answer has and what this failure puts there, each item marked as the rule that will check it (§3): a phrase (`contains` / `lacks`, capitals ignored), a pattern (`matches`, a regular expression, written out), or — only when neither can decide — what a coded check computes, in one sentence. **Known-bad answer** — the wrong answer the application gave, rewritten for the stand-in's input: the check must reject it. **Known-good answer** — a right answer as a model would plausibly word it: the check must accept it.
- **Judged:** **Rubric** — what a 5, a 3, and a 1 look like for this input.

Check a hard draft yourself before showing it: apply each phrase and pattern, by §3's rules, to its known-bad and its known-good answer. If it does not reject the bad one and accept the good one, fix the check first. A part only code can decide is not checked here: say so on the draft — the implementer's `--self-test` checks it.

Delete `"<tmp>/<trace id>.json"` once the draft is written.

### Step 5: Approval, case by case

Show each draft in full — the case exactly as Step 6 will write it, and nothing from the real trace. For each, the user approves it, edits it, or drops it. Nothing is written until each case has an answer. A dropped case is not written anywhere.

### Step 6: Write

**The harvest file** — decide its path once: `SDD/flow/HARVEST-[feature-name]-[YYYY-MM-DD].md`, or with `-2`, `-3` added when a file of that name exists. That exact path is what the Feedback line and the report name. Its format is under Output Format. Nothing else in `SDD/flow/` is created.

**The tier plan** — when there is one, append one line at the end of its `## Feedback` section (create the section at the end of the file if it is missing; change nothing else):

```markdown
- [YYYY-MM-DD] (eval-harvest): [n] proposed eval case(s) from answers marked in Opik — `[the harvest file's path]`. The next tier's design brief settles each one.
```

### Step 7: Clean up and report

```bash
rm -rf "<tmp>"
git status --short
```

`git status` must show the harvest file and the tier plan, and nothing else. Report (Output Format). Do not commit.

## Output Format

### The harvest file

```markdown
# Harvested eval cases — [feature-name] — [YYYY-MM-DD]

Proposed by `/eval-harvest` from answers a person marked as wrong in Opik, and approved one by one by [the user]. Every input is invented: the real requests are in Opik only, under the trace IDs below.
These are not in `evals/cases.jsonl`. The next cycle's design brief adopts, defers, or drops each one, case by case (`sdd-flow/references/evals.md` §2); an adopted one goes into the spec's `### Evals`, and its implementer's first eval run, made before any change for them, shows whether each one fails (`sdd-flow/references/evals.md` §2, *A case harvested from a real trace*). **Not yet seen to fail.**

## Case 1 — trace [trace id]

- **What went wrong:** [one sentence, in your own words]
- **Requirement:** [REQ-XXX of SPEC-YYY | none yet] — [the behaviour, in one sentence]
- **Kind:** [hard | judged]
- **Input** — [name]: [written out in full] · [name]: [written out in full]
- **Must contain:** [phrase | pattern `…` | coded: what it computes] · **Must not contain:** [the same]   ← hard
- **Known-bad answer:** [...] · **Known-good answer:** [...]     ← hard
- **Rubric:** 5 — [...]. 3 — [...]. 1 — [...]                    ← judged

## Case 2 — trace [trace id]
...
```

### The report

```
Eval harvest — [feature-name]

Marked traces: [n] listed, [n] already harvested, [n] picked by you
  harvested:     [n] — trace [id] → case [k] ([hard|judged], [REQ-XXX | new requirement])
  not a case:    [n] — trace [id]: [failed before the model answered | no model call | content not recorded]
  dropped by you: [n]

Written:
  [the harvest file's path]
  SDD/flow/TIERS-[feature-name].md — one line under ## Feedback     [or: no tier plan — name the harvest file in the next /sdd-flow task]

Not yet seen to fail: the next cycle's first eval run shows it.
Not committed.
```

## Examples

### GOOD — a tutoring app that states the result

A person marked two answers with the comment "gave away the answer". The model call shows the student's homework question and an answer that ends with the final number. **Draft:** what went wrong — "states the final result instead of leading the student to it"; requirement REQ-007 ("leads the student to the result"); hard. Input: an invented exercise — a made-up train leaving at a made-up time over a made-up distance, so the result is a number no model knows in advance — and the student's question asking for the answer. Must not contain (phrase): that number. Must contain (pattern): `\?` — a question back to the student. Known-bad: three steps ending in the number; known-good: two steps and "what do you get when you divide those?". The check rejects the first and accepts the second; the user approves; the harvest file and one Feedback line are written.

### BAD — the user's exercise, renamed

The stand-in keeps the student's exercise and only changes the names. Wrong: that is the student's text, now committed and uploaded at every review. **Right:** a new exercise of the same kind, with every figure changed.

### BAD — a case for a crash

A marked trace failed with `TimeoutError` before the model answered; the skill writes a judged case "answers within ten seconds". Wrong: there is no answer to judge, and a time limit is a test. **Right:** report it as not a case, with the lookup command that shows where it failed.

### BAD — straight into the cases file

`evals/cases.jsonl` exists, so the skill appends the approved case there to save a cycle. Wrong: no spec states it, so no review judges it, and it fails every review of every other feature until fixed. **Right:** the harvest file; the next cycle's brief settles it.

## Scope Boundary

This skill **reads** the traces a person marked in Opik through the application's own trace lookup, **drafts** invented stand-in cases with the same failures, and **writes** the approved ones to one harvest file plus one line in the tier plan's `## Feedback`. It makes no model call and runs nothing against the application, so it does not show that a stand-in fails — the next cycle's first eval run does. It does not number cases, write `evals/`, edit a spec, a test, or application code, mark or change anything in Opik, run during an `/sdd-flow` cycle, or commit. It never copies a real request or answer into a case, a file, or the conversation, and it deletes the one model call it wrote out. Opik only: with another backend it stops.
