---
name: rephrase
description: "INVOKE THIS SKILL when the user asks for a report they were just given to be restated more briefly or more plainly — via `/rephrase`, or a request like 'rephrase that', 'restate that', 'say that again more simply', 'summarize that', 'tl;dr', 'give me the short version', 'where does that leave us', 'what's done and what's left' — said in reply to such a report, not about a document, article, or other text. Applies to the report at the end of a piece of software work: a delivered solution, a finished development phase (research, planning, implementation, review), or a whole development cycle. Rewrites that report as four short sections in a fixed order — Done, Pending, Blocking, Next — and drops everything else: process narration, restated requests, reasoning already acted on, file-by-file tours, self-assessment. It adds NO new facts and does NO new work: it does not re-run tests, re-read code, or investigate; anything the source left unverified is reported as unverified. A section with nothing in it says 'None' rather than disappearing. With a file path or pasted text it restates that instead of the last report. NOT for rewording or summarizing prose, docs, articles, comments, or commit messages ('rephrase this paragraph' and 'tl;dr this doc' are ordinary requests), NOT for writing a session handoff file (use `/adhoc-compact`), and NOT for auditing a prompt (use `prompt-doctor`)."
---

# Rephrase

Restates a report on finished or in-progress software work as the four things the reader acts on:

1. **Done** — what now exists or is true that was not before.
2. **Pending** — what was started or agreed and is not finished.
3. **Blocking** — what stops the pending work, and who can remove it.
4. **Next** — the actions that follow, in order, each with an owner.

Everything else in the original report is removed. Nothing is added.

## What This Skill Does and Does Not Do

- **Does:** take the source — by default everything reported since the user's last request — sort every claim in it into the four sections, drop what fits none of them, and reword what remains so it can be read without the conversation's working vocabulary.
- **Does NOT:** do new work. It runs no tests, reads no code, and checks no claim. It does not improve the facts, only their wording and order. Its entire output is the four sections in the conversation; it writes no file.

## Anti-Pattern Watchlist

Check the restatement against these before emitting it:

1. **Upgrading a claim.** "Should work", "tests not run", "passes locally" becoming "works". Detection: a Done bullet stronger than the sentence it came from. Resolution: carry the source's certainty across unchanged. Work that was written but not verified is Done as *written*, with its verification listed under Pending.
2. **Dropping the bad news.** A failing test, a skipped step, or a reverted change vanishing because it made the summary longer. Detection: a failure, skip, or caveat in the source with no bullet in the output. Resolution: brevity removes narration, never outcomes. Every failure and every skipped step survives.
3. **Doing the work again.** Re-running the suite or re-reading the diff "to be sure". Detection: any tool call other than reading a file the user pointed at. Resolution: restate what was reported. If the source is too thin to restate, say which section cannot be filled and why.
4. **Inventing next steps.** Recommending work the source never raised. Detection: a Next item with no antecedent in the source's pending, blocking, or stated follow-ups. Resolution: Next is derived only from what the source already says is unfinished, blocked, or proposed.
5. **Activity instead of outcome.** "Investigated the retry logic", "refactored the handler". Detection: a Done bullet whose verb describes effort. Resolution: say what is different now — "Retries stop after 3 attempts instead of looping".
6. **Carrying the jargon across.** Requirement IDs, step numbers, codenames, and labels coined mid-session, left bare. Detection: an identifier the reader would have to scroll up to decode. Resolution: say the thing it stands for; keep the identifier in parentheses only if the reader will need to search for it.
7. **Blocking used as a second Pending.** Listing slow or unfinished work as a blocker. Detection: a Blocking bullet that names nothing that must happen first. Resolution: Blocking holds only what prevents work the user asked for from moving, phrased as the unblocking event and who owns it. A decision that such work is waiting on goes here, written as a question answerable in a few words. A choice about optional extra work the source merely offered blocks nothing: it is a **You** item under Next.
8. **Omitting an empty section.** Leaving Blocking out because nothing blocks. Detection: fewer than four headings. Resolution: the heading stays and reads `None`. Absent and empty are different answers.
9. **Wrapping it.** An opening line that announces the summary, or a closing line that offers more. Resolution: the output starts at **Done** and ends at the last Next item.

## When to Activate

- `/rephrase`, bare (the most recent report in the conversation), with a file path, or with pasted text.
- A request to restate a report the user has just been given: "rephrase that", "restate that", "say that more simply", "summarize that", "tl;dr", "shorter", "what's done and what's left", "where does that leave us". These count only as a reply to a report on work; the same words aimed at other text do not activate the skill.

## When NOT to Activate

- **Rewording or summarizing other text.** "Rephrase this paragraph / comment / error message / commit message" and "tl;dr this doc / article / thread" are ordinary requests. This skill restates reports on work only.
- **Handing off to a fresh session.** A handoff needs file paths, decisions, and context this skill deliberately removes. Use `/adhoc-compact` or the phase-specific compact commands.
- **A question about the work.** "Why did you choose X?" wants an answer, not a status restatement.
- **Nothing has been reported yet.** If no work has been done or reported in the conversation and no source was given, say so and stop.

## Behavioral Instructions

### Step 1: Fix the source

- **Bare invocation** — everything reported on the work since the user's last request. Usually that is one report. If it is several (a phase report followed by a review report, say), treat them as one source and produce one set of four sections, not one set per report; where they disagree, the later report wins.
- **A path** — read that file and restate it. This is the only tool call the skill makes.
- **Pasted text** — restate that text.

If the report is no longer in context (the conversation was compacted or cleared), say so and ask for a path or a paste. Do not reconstruct it from memory or from the repository.

### Step 2: Sort every claim

Go through the source claim by claim and place each in exactly one section:

| Section | Holds | Does not hold |
|---|---|---|
| **Done** | Finished outcomes, at the certainty the source gave them | Effort, attempts, things explored and abandoned |
| **Pending** | Unfinished, skipped, deferred, or failing items; the missing verification of work listed under Done | Ideas nobody agreed to do |
| **Blocking** | What must happen before requested work can move, and who does it | Work that is merely slow or not yet started; offers of optional extra work |
| **Next** | Actions in order, each owned by **You** or **Claude** | Anything the source does not support |

A claim that fits no section is dropped. That is where the length goes: how the work was approached, what was tried first, the request restated, reasoning for decisions already taken, lists of every file touched, and comments on how well it went.

Keep a detail only if the reader would act differently without it. A decision that changes what the user must do next is kept; the reasoning behind a settled one is not.

### Step 3: Reword for a reader outside the session

- One bullet, one fact, one line where it fits.
- Lead with the thing that changed, in ordinary words. Replace session-internal labels per anti-pattern 6.
- Keep exact values the reader will use: a failing test's name, a count, a command to run, a file to open.
- Group rather than enumerate: "Updated the three README files" beats three bullets, unless one of them needs separate attention.
- If Done runs past about six bullets, group further. The whole restatement should fit on one screen.

### Step 4: Check and emit

Run the watchlist, then emit the four sections and nothing else.

## Output Format

```markdown
**Done**
- <outcome>
- <outcome>

**Pending**
- <unfinished or unverified item>

**Blocking**
- <what must happen first> — <who can do it>

**Next**
1. **You:** <action or decision>
2. **Claude:** <action>
```

- Whenever there is a source to restate, all four headings appear, in this order. An empty section is the single line `None`. The only other output this skill produces is the one-line stop from Step 1 or from *When NOT to Activate*.
- Next is numbered because its order matters; the first item is the one to do now.
- When Blocking is `None` and Next has only Claude-owned items, the reader should be able to reply "go" and have that be enough.

## Examples

### GOOD — length removed, outcome kept

**Source (abridged):** *"I started by exploring the auth module to understand the token flow. After reviewing `session.py` and `middleware.py` I identified that expiry was compared in local time. I implemented a fix converting both sides to UTC and added two tests, which pass. The full suite has one unrelated failure in `test_export_csv` that predates my change. I didn't touch the refresh endpoint, which has the same comparison — let me know if you'd like that included."*

**Right:**

```markdown
**Done**
- Login sessions now expire at the right time: expiry is compared in UTC instead of local time.
- Two new tests cover it and pass.

**Pending**
- The token-refresh endpoint has the same local-time comparison and is unchanged.
- One test fails in the full suite (`test_export_csv`); reported as failing before this change.

**Blocking**
- None

**Next**
1. **You:** decide whether the refresh endpoint gets the same fix now.
2. **Claude:** apply it and add a test, if yes.
```

Blocking is `None` because the refresh endpoint was an offer, not part of the request: nothing asked for is waiting on the decision.

### BAD — upgraded and trimmed

**Same source. Wrong:** *"**Done** — Fixed the session expiry bug; all tests pass."* The suite has a failing test, and the unfixed refresh endpoint is gone.

### GOOD — an empty report

**Source:** *"Implementation complete. All 14 tests pass, lint is clean, committed as `a1b2c3d`."*

**Right:** Done lists the outcome and the commit; Pending, Blocking, and Next each read `None`. Do not manufacture a next step to fill the section.

### BAD — verifying instead of restating

**User:** *"rephrase that"* after a report that says tests were not run.

**Wrong:** running the tests so that Done can say they pass.

**Right:** "Tests have not been run" under Pending, and "**Claude:** run the tests" under Next.

## Scope Boundary

One source, restated in conversation as one set of four sections. No files written, no claims checked, no work continued. If the user answers a Next item, that is a new request and this skill is finished.
