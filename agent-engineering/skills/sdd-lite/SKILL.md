---
name: sdd-lite
description: "INVOKE THIS SKILL when the user asks for a feature or change to be built the light way — via `/sdd-lite <task>`, or a request that names the skill or the workflow explicitly: 'build this with sdd-lite', 'use the sdd-lite workflow', 'brief and build this with an approved brief'. Do NOT activate on a request for a small or quick change ('do this the light way', 'keep it minimal'): those ask for a small change, not for a brief, a gate and records. Builds in the main conversation with no subagents: a short interview only for what the request leaves open, a one-page brief of the owner's decisions that the owner approves (the one gate), the build with tests, one second-model review of every change (plus at most one check of its fixes), and a close-out that keeps the three records later work actually reads: a decision record (through `cross-cutting-adr`) when a choice binds later work, glossary updates, and the brief itself. Writes no research document, spec, slices, site counts, review reports or run logs. Tells the user to switch to `/sdd-flow` when the requirements are still unclear after the interview, or when the work is large or risky enough to need slices. Never commits unless asked. NOT for running the full SDD lifecycle (use `sdd-flow`), NOT for judging whether the work is worth doing (use `worth-building`), and NOT for a one-line fix that needs no decisions (just make it)."
---

# SDD Lite

Builds a feature the way a careful engineer would without a process around them, and keeps only the records that a
later cycle actually opens. The premise:

> **Settle what the owner wants, build it directly, have a second model check it once, and leave behind only
> what the next person will read.**

It exists because, on clear tasks, the full flow cost 15-44 times a plain build and its code was larger and broader than
the request, while its correctness was the same or better (never worse), and most of what it writes (research, specs, review reports, run logs) is never opened again after its own cycle. The parts that were
reused are small: the owner's decisions, the decision records, the glossary, the tier plan. This skill keeps those and
drops the rest, and keeps the one check that plausibly carried the full flow's correctness: an independent review.
(Drawn from an evaluation of `sdd-flow` against plain Claude Code on four tasks and a review of how one
project's sdd-flow records were used in later cycles, 2026-11.)

## What This Skill Does and Does Not Do

- **Does:** interview for what is open; write and get approval for one brief; build and test in this conversation; run
  one second-model review of every change (and at most one check of the fixes); write a decision record, glossary
  entries and the brief.
- **Does NOT:** spawn subagents; write research, specs, implementation plans, slice files, counters, review reports or
  progress logs; run a specialist panel; commit (unless the user asks); push.

## Steps

### 1. Read the ground (no writing)

- The request, and the code it touches. Cite `file:line` for anything the brief says about how things work today.
- If present: `SDD/UBIQUITOUS_LANGUAGE.md` (use its names exactly), `SDD/adr/` (decisions already binding this work),
  the feature's tier plan under `SDD/flow/TIERS-*.md`, and earlier briefs under `SDD/briefs/` for the same area.
- Decide the risk class now (it goes into the brief, so the owner sees what a mistake would touch): **risky** if the
  change touches authentication or authorization, secrets, personal or student data, payments, deletion or migration
  of stored data, an exposed network surface, or an agent's tools or prompts that act on untrusted input, an effect
  outside the system that cannot be recalled (messages, emails, notifications, publishing, calls that spend or order),
  or anything else whose failure would be expensive or hard to reverse; **ordinary** otherwise. When unsure, it is
  risky.

### 2. Interview, only for what is open

- Ask only what the request, the code and the records above do not settle, and what changes what gets built. Group the
  questions in one message; give each one a recommended answer with its one consequence, so the owner can reply "all
  recommendations".
- Nothing open: say so in one line and go to step 3.
- **Switch to `/sdd-flow`** (tell the owner, do not do it yourself) when, after one round of answers, the owner is still
  unsure what they want, or the work needs more than about a day of building or more than one independent part. Say
  which of the two it is.

### 3. The brief: the one gate

Write `SDD/briefs/BRIEF-[###]-[short-name].md` (next free number; create the folder if needed), at most one page:

```markdown
# BRIEF-[###]-[short-name]

Date: [YYYY-MM-DD]. Status: draft | approved [date].

## What you will be able to do afterwards
- [user-visible outcomes, in the owner's terms]

## Decisions
- [each decision, with the owner's words quoted where they made it; mark the ones you settled as "settled by me"]

## How it will work
- [the shape of the change: routes, files, behaviour; cite file:line for today's code]

## Not now
- [what is deliberately left out]

## Done when
- [the check the owner will run, and the tests that must pass]

## Risk
- [ordinary | risky, and why]

## Decision records to write
- [each decision that binds later work: title, the alternatives considered and why they lost, consequences; or "none"]
```

- **Decision records are settled here, not later.** A decision that binds later work (a technology, a convention, a
  pattern other features inherit) goes under "Decision records to write" with its alternatives and consequences, asking
  the owner for any that are missing. Approving the brief approves writing exactly those records.
- Show it and ask for approval. **Build nothing before the owner approves.** Apply their changes and show it again
  until they do; then set `Status: approved [date]`.
- The brief is the record of *why*. Keep it short; a brief longer than one page is a sign the work belongs in
  `/sdd-flow`.

### 4. Build

- Build in this conversation, in small steps, running the tests as you go.
- Tests: follow the definition of a real test in `../sdd-flow/references/test-integrity.md` §1 (read it; do not work
  from memory), reading it with these substitutions: "the SPEC" is the approved brief (its outcomes, decisions and
  "Done when" are the requirements a test's expected value comes from), and a changed or removed existing test is
  recorded as one line under a `## Test changes` heading added to the brief (the test, what changed, the brief line that
  requires it) instead of in an implementation plan. Test behaviour the brief names; do not pin exact wording or file
  structure unless the brief makes it a requirement.
- Use the glossary's names in code and tests. A new domain term goes into the glossary in step 6, not into the code
  under a second name.
- Stay inside the brief. Something the brief does not cover that changes what the owner gets: stop and ask, and add the
  answer to the brief's Decisions.
- Run the whole test suite before step 5.

### 5. Review: every change, once

- One review by a second model family, from the repository root: `codex review --uncommitted` (redirect to a file;
  the findings are the last block). Ordinary and risky changes alike: an independent review is the check most likely
  to catch a bug, and the cap below keeps it from growing the code.
- No Codex CLI: stop, tell the owner and ask whether to go on without a review (for a risky change, say what it
  touches); go on only on their explicit yes, and say "no review: no Codex CLI, owner's decision" in the report.
- Fix each real finding with a test that fails without the fix; say why a finding was not fixed. Then one check of the
  fixes (`codex review --uncommitted` again) and no more. If that check still reports a finding at Codex's P0 or P1
  priority (or one you judge would cause data loss, a security hole or a wrong irreversible action), stop and tell the
  owner the work needs `/sdd-flow` or their decision; P2 and lower are fixed or listed in the report.
- Write no review report; the findings and what was done about them go into the final report.

### 6. Close-out: the records that last

- **Decision records:** for each entry under the approved brief's "Decision records to write", invoke
  `cross-cutting-adr` with its title, alternatives and consequences from the brief (its sdd-lite trigger: pre-approved,
  no further confirmation). Feature-only decisions stay in the brief. A new binding decision that came up during the
  build is not written silently: show it to the owner and write it only on their yes.
- **Glossary:** add or refine the terms this change introduced in `SDD/UBIQUITOUS_LANGUAGE.md` (create it when the
  change introduced the project's first terms worth naming).
- **Tier plan:** if the feature has one, add one dated line saying what was built and naming the brief.
- **README / user docs:** update what a user of the change needs to know.

### 7. Report

In the conversation, short: what was built (files, behaviour), test result, review result (or why none ran),
records written (brief, ADRs, glossary terms), what is not done, and the owner's check from "Done when". Offer to commit;
the commit message names the brief.

## Anti-Pattern Watchlist

1. **Rebuilding the full flow.** Writing a spec, a plan or per-step notes "to be safe". Detection: any file under `SDD/`
   other than the brief, ADRs, the glossary and the tier plan. Resolution: delete it; if the work needs it, it needs
   `/sdd-flow`.
2. **Building before approval.** Detection: an edit outside `SDD/briefs/` before the brief says approved. Resolution:
   stop and get approval.
3. **Interviewing for what is settled.** Detection: a question the request, the code or an ADR already answers.
   Resolution: drop it, or state the answer as "settled by me" in the brief.
4. **Skipping the review.** Detection: no review run without the owner's explicit yes to go on without one.
   Resolution: run it; when no Codex CLI is available, stop and ask.
5. **Reviewing in a loop.** Detection: a third review, or a second check of fixes. Resolution: stop after the one
   check; each further round answers findings with more code, which is how the full flow's code grew.
6. **Brittle tests.** Tests that pin exact sentences, file layout or call counts the brief does not require.
   Resolution: test behaviour; these tests break on harmless change and slow every later cycle.
7. **Silent scope growth.** Detection: behaviour in the diff that the brief does not name. Resolution: remove it, or ask
   and add it to the brief.
