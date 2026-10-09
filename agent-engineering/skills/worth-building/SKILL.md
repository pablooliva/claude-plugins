---
name: worth-building
description: "INVOKE THIS SKILL when the user EXPLICITLY asks whether a proposed piece of work is worth building as planned, before or early in building it — via `/worth-building`, or an unambiguous request like 'is this worth building', 'run worth-building on this', 'what is the cheapest test that could kill this idea', 'is this too much work for what it gets us', 'should we do this at all', 'is this plan in the right order', 'check the plan against what the first slice cost'. It is user-invoked, NOT an ambient watcher: do not activate just because a design or plan appears in the conversation. Reads a proposal, design brief, spec, or plan and asks six questions of it — the cheapest run that could kill the idea and whether it comes first; the best the idea can do and whether something simpler gets most of it; the size of the change against the size of everything built around it; what a user sees after it ships; which safeguards need code and which need one written rule; and the budget with the point at which to stop and re-plan. Reports one page: a verdict (proceed, reorder, shrink, or stop), the kill test spelled out, the budget, and the tripwire. Run it at a design gate, and again after the first slice or milestone, when a measured cost replaces the estimate. It NEVER edits the target, NEVER implements, and NEVER runs the kill test unless asked. Usage: `/worth-building [file path | last] [recheck]`. NOT for trimming a proposal that is already accepted as worth doing (use `simplicity-challenge`), NOT for finding what a proposal is missing (use `/critical-review`), and NOT for reviewing code."
---

# Worth Building

Asks whether the work in front of you should be built as planned, in this order, at this cost. The premise:

> **Find out whether the idea works before building what the idea needs.**

A plan can be correct, well reviewed, and still a poor use of the time: the one run that would show the idea does not work is scheduled last, behind everything built to make that run trustworthy. Each step looked reasonable when it was added. This skill puts six questions to the plan as a whole and reports one verdict.

The questions, how to answer each from evidence, and what a failing answer looks like are in `references/questions.md`. **Read that file before judging anything.** A worked example is in `references/worked-example.md`; read it when a verdict is hard to call.

## What This Skill Does and Does Not Do

- **Does:** read a proposal as text to be analysed; state the idea it rests on; answer the six questions from the target, the conversation, and the code or data it can read; report a verdict, the kill test, a budget, and a tripwire. With `recheck`: compare the plan with what the work has cost so far.
- **Does NOT:** edit the target; implement anything; run the kill test unless the user asks; trim scope item by item (that is `simplicity-challenge`); look for missing requirements (that is `/critical-review`); or review code. Its output is a report in the conversation.

## Anti-Pattern Watchlist

Check the report against these before emitting it:

1. **A verdict with no kill test.** Saying "proceed" or "stop" without naming the run that would settle it. Detection: the report's kill-test section is general ("validate the approach early"). Resolution: name the input, the command or procedure, the output to read, and the result that means stop. If no such run exists, say that — it is itself a finding.
2. **Inventing the evidence.** "This will not improve the metric." Detection: a claim about results, users, or the codebase with no source in the target, the conversation, or something you read. Resolution: cite it, or turn it into the kill test. This skill argues for finding out, not for guessing the answer.
3. **Mistaking size for waste.** Calling a plan too big because it is big. Detection: a "shrink" verdict that names no part whose removal still leaves the idea testable. Resolution: large work that is ordered well and sized to its risk gets "proceed".
4. **Cutting what cannot be undone.** Advising a written rule in place of code for something irreversible — data loss, a leak, a destructive action. Detection: a rule-or-code row marked "rule" whose failure cannot be reversed. Resolution: irreversible failures keep their enforcement; say so in one line.
5. **Doing `simplicity-challenge`'s job.** Producing a table of cuts and tiers. Detection: more than three named removals. Resolution: give the verdict and the reason; point to `simplicity-challenge` for the item-by-item cut.
6. **Adding work.** Proposing new safeguards, tests, or requirements. Detection: anything in the report the proposal did not contain, other than the kill test and the tripwire. Resolution: remove it.
7. **A budget with no numbers.** Detection: "this may take a while". Resolution: count the units the plan itself names (slices, milestones, review rounds) and multiply; state what is estimated and what is measured.
8. **Rechecking without the record.** Running `recheck` from memory of how the work went. Detection: a measured cost with no source. Resolution: read the progress record, the commit history, or ask; say which.
9. **A report too long to act on.** Detection: more than 45 lines. Resolution: one line per question, then the four closing sections.
10. **Softening the verdict.** "Consider possibly reordering." Detection: a verdict that is not one of the four words. Resolution: pick one. The user can overrule it; they cannot act on a hedge.

## When to Activate

- `/worth-building`, bare (the most recent proposal, design brief, or plan in the conversation) or with a file path.
- `/worth-building recheck`, after the first slice, milestone, or week of work on something already under way.
- An explicit request to judge whether the work is worth doing as planned: "is this worth building?", "what's the cheapest test that could kill this?", "is this too much work for what we get?", "should we do this at all?".

## When NOT to Activate

- **The work is accepted and only its size is in question.** That is `simplicity-challenge`. When both are wanted, run this first: there is no point trimming a plan that should be reordered or stopped.
- **Finding what is missing.** That is `/critical-review`, which tends to add work. Run it on whatever survives this.
- **Code that already exists.** This skill reads plans, not diffs.
- **A proposal merely appearing.** A design in the conversation is not a request to judge it.
- **Nothing to judge.** If there is no proposal in the conversation and no path was given, say so and stop.

## Behavioral Instructions

### Step 1: Fix the target and read the questions

- **A file path** → read that file: a proposal, a design brief, a spec, a plan.
- **`last`, or no argument** → the most recent proposal, design, or plan in the conversation.
- **`recheck`** → the same target, plus the record of the work so far (Step 4).

Then read `references/questions.md` in this skill's directory.

### Step 2: State the idea and the change

Write two sentences.

- **The idea:** what the work bets on, as a claim that could turn out false — "scoring items on three separate questions will separate the ones a judge excludes from the ones it keeps". Not the feature's name, and not its goal.
- **The change:** what would be different in the product if the idea is right, at its smallest — "one prompt edit and a rule of a few lines".

If you cannot state the idea as something that could be false, ask one question and stop. A plan with no falsifiable idea cannot have a kill test, and the user should hear that before anything else.

### Step 3: Answer the six questions

Take them in the order `references/questions.md` gives, and answer each from evidence: the target's own words, the conversation, and code or data you can read. Read only what an answer needs. For each, record a one-line answer and a mark: **holds**, **fails**, or **unknown** (with what would settle it).

1. **Kill test** — the cheapest run that could show the idea is wrong; whether data or tooling that already exists can run it; where the plan puts it.
2. **Ceiling** — the most the idea can deliver if it works perfectly, and what the simplest alternative delivers.
3. **Ratio** — the size of the change (Step 2) against the size of everything the plan builds around it.
4. **What a user sees** — what is different for a reader, operator, or customer after each stage ships.
5. **Rule or code** — for each safeguard the plan builds: what it protects against, whether the failure can be undone, and whether a written rule would do.
6. **Budget and tripwire** — units of work times cost per unit; how the review weight matches where the code runs; the point at which to stop and re-plan.

### Step 4: With `recheck`, replace estimates with measurements

Find what the work has cost so far: the progress record, the commit history, the review documents, or the user's account. Then:

- State the measured cost per unit (rounds of review, days, sessions) and what it makes the remaining total.
- Check the tripwire set at the earlier run, if there was one. If it has been crossed, say so first.
- Say whether the kill test has been run yet. If the work is past its first unit and the kill test has not run, that is the lead finding.
- Name what is driving the cost: scope, or process. They need different verdicts — scope is shrunk, process is lightened.

### Step 5: Choose the verdict

Exactly one of:

- **Proceed** — the kill test has been run or comes first, the ceiling justifies the budget, and the review weight fits the risk.
- **Reorder** — the work may be worth doing, but the kill test is not first. Say what moves to the front and what waits on its result.
- **Shrink** — the idea is worth testing, but the work is larger than it needs to be. Say which of two things is too large. *The plan:* it builds more than testing the idea needs — say what it reduces to, in one or two lines, and point to `simplicity-challenge` for the item-by-item cut. *The process:* the scope is right and the rounds each unit takes are not — say what lighter process you recommend and for which parts, leave the scope alone, and point to a re-plan in the workflow that owns the process.
- **Stop** — the ceiling does not justify the cost, a simpler alternative gets most of the benefit, or the kill test has already run and failed. Say which.

When more than one applies, take the first in this order: **stop** (a kill test that ran and failed, or a ceiling that does not justify the cost, outranks everything), then **reorder** (there is nothing to shrink or proceed with until the kill test has run), then **shrink**, then **proceed**. Name the runner-up in the reason, so the user knows what comes after. A question marked **unknown** never blocks a verdict: say what the verdict assumes.

### Step 6: Report

Under 45 lines, in this order:

1. **Idea** and **Change** — the two sentences from Step 2.
2. **Verdict** — one of the four words, and one sentence of reason.
3. **The six questions** — one line each: the mark, then the answer.
4. **Kill test** — spelled out: the input, the run, the output to read, the result that means stop, and what it costs. If it can run on what already exists, say so and offer to run it.
5. **Budget** — units × cost per unit, marked *estimated* or *measured*.
6. **Tripwire** — the observable condition at which to stop and run `/worth-building recheck`, written so that someone else could tell it has been met: "the first slice takes more than three review rounds".
7. **Questions** — at most three, only where the verdict depends on something only the user knows.

If the plan passes all six, the report is the Idea, the Change, `Verdict: proceed`, the kill test's place in the plan, and the tripwire. Do not manufacture concerns.

### Step 7: On request

- **"Run the kill test"** → run it if it is offline, cheap, and reversible, and report the result against the stop condition written in Step 6 — not against one chosen after seeing the result. Anything that spends money, calls an outside service, or touches production needs the user's explicit go-ahead first.
- **"Rewrite the plan"** → that is `simplicity-challenge` (for a shrink) or a re-plan in whatever flow produced the target. Say which, and hand over the verdict, the kill test, and the tripwire as its inputs.
