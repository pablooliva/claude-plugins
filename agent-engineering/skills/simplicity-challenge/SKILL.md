---
name: simplicity-challenge
description: "INVOKE THIS SKILL when the user EXPLICITLY asks for a proposal to be challenged for doing or building too much, before it is implemented — via `/simplicity-challenge`, or an unambiguous request like 'challenge the simplicity of this', 'run the simplicity challenge', 'is this over-engineered', 'what is the simplest version of this', 'cut this proposal down', 'what can we defer', 'tier this'. It is user-invoked, NOT an ambient watcher: do not activate just because a plan or proposal appears in the conversation. Applies the tier standard (Tier 1 POC-plus, Tier 2 Standard, Tier 3 Full) to a proposal, plan, design brief, or spec on two axes — what it does (functionality) and how it is built (architecture and code structure) — and reports the smallest version still worth using, a table of cuts with what each one loses and what it would cost to add later, and what it kept because it is unsafe to leave out. It only removes or defers: it NEVER adds requirements, NEVER edits the target, and NEVER implements. On request it rewrites the proposal in reduced form or writes a tier plan. Usage: `/simplicity-challenge [file path | last] [functional | structural]`. NOT for cleaning up code already written (use the built-in `/simplify`), NOT for finding what a proposal is missing (use `/critical-review`), and NOT for surveying existing code for shallow modules (use `improve-codebase-architecture`)."
---

# Simplicity Challenge

Argues that the proposal in front of you is too much. The premise:

> **Build the smallest thing that is really usable, use it, and let what you learn decide what comes next.**

A proposal grows because every addition looks reasonable on its own: one more case handled, one more option, one more extension point for later. This skill puts each of those through the same tests and reports what survives.

The tiers, the floor (what may never be left out), the cut tests, and the tier-plan template live in `references/tiers.md`. **Read that file before challenging anything.** Do not work from memory of it.

## What This Skill Does and Does Not Do

- **Does:** read a proposal as text to be analysed; state the need it serves; run every thing it does and every part it adds through the cut tests; report the smallest useful version, the cuts and their costs, what it kept for safety, and the questions only the user can answer. On request: rewrite the proposal in reduced form, or write a tier plan.
- **Does NOT:** add requirements; edit the target; implement anything; review code that is already written; or judge whether the proposal is correct. Its output is a report in the conversation, plus a file only when the user asks for a rewrite or a tier plan.

## Anti-Pattern Watchlist

Check the report against these before emitting it:

1. **Adding instead of cutting.** Noticing a gap and filling it — a missing error case, an absent test, a safer design. Detection: any item in the report that the proposal did not contain. Resolution: this skill only removes or defers. A gap gets one closing line pointing to `/critical-review`, nothing more.
2. **Cutting the floor.** Deferring data-loss protection, a security control on an exposed surface, or a visible failure for an unhandled case. Detection: a Cuts row whose item appears in `references/tiers.md` → The floor. Resolution: it stays, and is listed under Kept on purpose with the floor rule named.
3. **Keeping something because it is expensive to add later.** Detection: an item kept with no floor rule behind it, justified by retrofit cost. Resolution: cost to add later never keeps an item. Defer it and state the cost, so the user can overrule.
4. **Sparing the structure.** Trimming features while leaving the architecture untouched — the new service, the plugin point, the queue, the configuration layer. Detection: a report on a proposal that adds parts, with no structural rows. Resolution: list the parts the proposal adds and run the structural tests on each.
5. **Accepting "so we can later".** Letting a part stand because a later tier will need it. Detection: a kept part whose only stated reason is a future need. Resolution: apply the later-tier test. It is removed unless the user has said that future is already committed.
6. **Invented facts.** "Nobody will need CSV export." Detection: a claim about users, usage, or the codebase with no antecedent in the user's words or the code. Resolution: base it on what was said or what the code shows, or turn it into a question.
7. **Assuming the codebase.** Saying an existing module can do the job without looking. Detection: an Existing-code verdict with no file cited. Resolution: check, and cite `file:line`. If the code cannot be read, say the verdict is unverified.
8. **Manufacturing cuts.** Producing a list because a list was asked for. Detection: cuts that lose something the stated need requires. Resolution: "nothing to cut" is a valid report. Say it in one line.
9. **A report too long to read.** Detection: more than 60 lines, or a cut explained in a paragraph. Resolution: the table carries the detail, one line per cut.
10. **Editing or building.** Detection: any write to the target, or any implementation step. Resolution: the only files this skill writes are a rewrite or a tier plan, and only when asked.

## When to Activate

- `/simplicity-challenge`, bare (the most recent proposal in the conversation), with a file path, or with `functional` or `structural` to limit the axis.
- An explicit request to cut a proposal down before it is built: "challenge the simplicity of this", "is this over-engineered?", "what's the simplest version?", "what can we defer?", "tier this".

## When NOT to Activate

- **Code that already exists.** Cleaning up a diff is the built-in `/simplify`; finding shallow modules in a codebase is `improve-codebase-architecture`.
- **Finding what is missing.** That is `/critical-review`, which argues the opposite case. When both are wanted, run this first and review the reduced version.
- **A proposal merely appearing.** A plan in the conversation is not a request to challenge it.
- **Nothing to challenge.** If there is no proposal in the conversation and no path was given, say so and stop.

## Behavioral Instructions

### Step 1: Fix the target and read the standard

- **A file path** → read that file: a proposal, a plan, a design brief, a spec.
- **`last`, or no argument** → the most recent proposal, plan, or proposed solution in the conversation.
- **`functional` or `structural`** → limit the challenge to that axis. Default: both.

Then read `references/tiers.md` in this skill's directory.

### Step 2: State the need

Write one sentence: what the proposal is for, in the user's words where they exist. Every cut is judged against it. If you cannot state it from the conversation or the target, ask one question and stop — a challenge with no stated need cuts at random.

### Step 3: Challenge what it does

List the things the proposal does: each behaviour, case handled, option, and output. Run the functional cut tests on each and record the verdict: **keep in Tier 1**, **Tier 2**, **Tier 3**, or **cut** (nothing suggests it will ever be needed). Kept items do not appear in the Cuts table; the Smallest useful version describes them.

### Step 4: Challenge how it is built

List the parts the proposal adds: modules, services, dependencies, stored state, background processes, queues, caches, extension points, configuration, abstractions. Skip any part that exists only for a functional item Step 3 deferred or cut — it goes with that item. Run the structural cut tests on the rest and record the verdict: **keep** (the behaviour staying in Tier 1 needs it) or **remove** (it does not). Do not assign a removed part to a later tier: only behaviour is scheduled, and a later tier chooses its own structure when its turn comes (`references/tiers.md` → Cut tests).

- For an Existing-code verdict, look at the code and cite the file. Read only what the verdict needs.
- A part justified by future needs — "so we can later…", "to make it easy to add…" — fails the later-tier test unless the user has said that future is already committed.
- When a decision would be costly to reverse, the simplest option still wins. Say what reversing it would cost in that row.

### Step 5: Check the floor

Go through the cuts once more against the floor. Anything it protects goes back into Tier 1, and is listed under Kept on purpose so the user can see safety was not cut. Apply the three floor rules as written: do not stretch one to cover something it does not name, and do not list items no cut test would have removed.

### Step 6: Report

Under 60 lines, counting every line of the report, in this order:

1. **Need** — the sentence from Step 2.
2. **Smallest useful version** — three to five lines: what it does, and what it deliberately does not.
3. **Cuts** — one table, the cut that most reduces what must be built and reviewed first:

   | Item | Kind | Verdict | Test | What you lose | Cost to add later |
   |---|---|---|---|---|---|
   | [thing the proposal does] | function | Tier 2 · Tier 3 · cut | [the cut test that placed it] | [one phrase] | cheap / moderate / expensive |
   | [part the proposal adds] | structure | remove | [the cut test that removed it] | [one phrase] | cheap / moderate / expensive |

   This table is the short form. The full record of a deferral — including how the case fails if it is reached — is written only in a rewrite or a tier plan (Step 7).

4. **Kept on purpose** — items a cut test would have deferred or removed but the floor protects, one line each, naming the floor rule. `None.` when there are none.
5. **Questions** — at most three, only where a verdict depends on something only the user knows. Each is answerable in a few words.

If the proposal is already the smallest useful version, the report is the Need line and one more: nothing to cut, and why.

If you believe the proposal is missing something, add a single closing line saying so and pointing to `/critical-review`. Do not add the missing thing.

### Step 7: On request

- **"Rewrite it"** → produce the reduced proposal: the smallest useful version in full, followed by a `Deferred` heading (functional items moved to Tier 2 or Tier 3) and a `Removed` heading (removed parts and outright cuts), both in the form `references/tiers.md` → Recording a deferral gives. Write it where the user says; do not overwrite the original unless told to.
- **"Tier it"** → write a tier plan from the template in `references/tiers.md` → Tier plan, at the location that section gives.
