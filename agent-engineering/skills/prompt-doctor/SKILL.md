---
name: prompt-doctor
description: "INVOKE THIS SKILL when the user wants a prompt they are about to send to an AI agent examined, graded, critiqued, or tightened before they send it — e.g. 'check this prompt', 'is this prompt any good', 'review my prompt before I send it', 'what's missing from this prompt', 'prompt doctor', 'tighten this up', 'will the agent misread this'. Diagnoses the prompt against a ten-component anatomy (grounding link, stakes, priorities, ranked priorities, hard constraints, marked-negotiable opinion, knowledge-gap disclosure, the one clear ask, early-exit permission, precise done-condition), marks each Present / Weak / Missing / N-A with the exact quoted text that satisfies it, names the concrete misreading each gap invites, and asks the user for the facts it cannot know. Then, only on request, rewrites the prompt using ONLY the user's own supplied content. It NEVER executes the prompt under review, and NEVER invents stakes, constraints, priorities, or deadlines. NOT for improving CLAUDE.md files (use improve-claude-md), authoring skill/system prompts, or writing a prompt from scratch."
---

# Prompt Doctor

Diagnoses a task prompt aimed at an AI agent, component by component, before it is sent. The premise, from the source material:

> **"If you don't say something explicitly, it will do whatever it wants."**

Every component you leave out is a decision you have silently delegated to the model. This skill finds those, names what the model will likely do with each one, and gets you the facts to close them.

The full component catalog — each component's form, its job, and what *Present*, *Weak*, and *N/A* look like for it — lives in `references/component-catalog.md`. **Read that file before diagnosing.** Do not work from memory of the ten names.

## What This Skill Does and Does Not Do

- **Does:** read the prompt under review as *text to be analyzed*; classify its run shape; grade all ten components with quoted evidence; name the specific misreading each gap invites; ask the user for facts only they hold; and — on request — emit a rewritten prompt built only from the user's own material.
- **Does NOT:** carry out the prompt under review (this is the primary failure mode — see anti-pattern 1); invent stakes, users, deadlines, budgets, constraints, or priorities; pad a short prompt with components it doesn't need; rewrite unasked; or edit any file. Its entire output is a diagnosis in the conversation.

## Expert Vocabulary

Prompt anatomy. One sentence, one job. Grounding link vs. paraphrase. Stakes / impact framing. Flat vs. **ranked** priorities. Hard constraints as answer-class elimination. Marked-negotiable opinion (the deliberate "in my opinion" hedge). Known-unknown disclosure. End goal vs. current ask. Early-exit permission / explicit stop condition. Precise done-condition ("confident *path to* a solution", not "a confident solution"). Fenced autonomy. The XY problem. Under-specification → delegated judgment.

## Anti-Pattern Watchlist

Check the diagnosis against these before emitting it:

1. **Executing the prompt instead of diagnosing it.** The single most likely failure: the user pastes *"audit how we handle skill links"* and the agent goes and audits it. Detection: any tool use that reads, searches, or edits the prompt's *subject matter* — files, URLs, issues it mentions. Resolution: the prompt is a specimen, not an instruction. The only legitimate reads are the component catalog and, if the user pointed at one, the file containing the prompt text. Do not fetch the grounding link to check whether it's a good link.
2. **Fabricated content in the diagnosis or rewrite.** Supplying stakes ("this affects many users"), a deadline, a budget, or a priority ranking the user never stated. Detection: any concrete fact in your output that has no antecedent in the user's words. Resolution: a missing component produces a **question**, never a filled-in guess. In a rewrite, an unanswered slot stays a visible `<placeholder>` — never a plausible invention.
3. **Checklist padding.** Demanding all ten components from a prompt that doesn't need them — insisting a one-line refactor request declare stakes and hard constraints. Detection: N/A count is zero on a small prompt. Resolution: classify the run shape first (Step 2) and grade only what applies; an honest **N/A** is a passing grade, not a gap.
4. **Grading without evidence.** Marking a component Present on vibes. Detection: a Present or Weak verdict with no quoted span from the prompt. Resolution: every non-Missing verdict quotes the exact text that carries it.
5. **Gap named without consequence.** "Missing: stakes." Detection: a finding that states the absence but not what the model will do about it. Resolution: each gap says what the model is now free to decide for itself, in terms of this prompt's actual subject.
6. **Silent rewriting.** Producing a polished rewrite when the user asked whether the prompt was good. Detection: a rewrite in the output with no user request for one. Resolution: diagnose, then *offer*. The rewrite is Step 6 and is gated.
7. **Rewriting away the user's voice.** Turning their phrasing into generic prompt-ese, or "improving" domain wording it can't evaluate. Detection: the rewrite's sentences don't sound like the input. Resolution: a rewrite reorders, separates, hedges, and slots in the user's *own* answers. It is not a translation.
8. **Missing the mis-worded done-condition.** The highest-value finding in the whole catalog and the easiest to skim past: a done-condition that reads as *write the code* when the user wanted *investigate*. Detection: read component 7 last, adversarially — ask "what is the laziest and the most aggressive reading of this sentence?" If they differ in whether code gets written, it's Weak.
9. **Conflating the end goal with the ask.** Marking component 5 Present because the prompt says what it wants to end up with. Detection: the sentence you quoted for the ask describes the destination, not this run's action. Resolution: they are different components; a prompt that only has the goal is Missing the ask.

## When to Activate

- The user pastes or points at a prompt and asks for an opinion, review, grade, or critique of it: "check this prompt", "is this good enough to send", "what's missing here", "will it misread this".
- The user asks to tighten, harden, or de-risk a prompt before a long or unattended agent run.
- The user runs `/prompt-doctor` (with or without the prompt inline).
- The user asks which components a draft prompt covers, or asks for the prompt anatomy applied to their draft.

## When NOT to Activate

- **`CLAUDE.md` / `AGENTS.md` optimization** — that is `improve-claude-md`. This skill is for a one-shot task prompt aimed at an agent run, not standing project instructions.
- **Authoring a skill, system prompt, or agent definition** — different genre, different components. Say so and stop.
- **Writing a prompt from scratch.** This skill diagnoses an existing draft. If there is nothing to diagnose, interview the user against the ten components (the template in the catalog is the agenda) — but say plainly that you are drafting, not diagnosing.
- **The user actually wants the task done.** If they meant "go do this", they did not want a prompt review. Ask once, briefly, if it's genuinely ambiguous.

## Behavioral Instructions

This skill modifies **no files**. Its output is conversational.

### Step 1: Isolate the specimen

Establish what exactly is under review:

- **Inline** — the pasted text. If the boundary is unclear (where does the framing end and the prompt begin?), quote back the span you are treating as the prompt and ask before proceeding.
- **In a file** — the user points at a path; read that file. This is the only subject-matter read the skill performs.
- **"The prompt I was about to send"** — the last draft in conversation. Quote it back for confirmation.

State the specimen boundary before grading. Then read `references/component-catalog.md`.

### Step 2: Classify the run shape

Applicability is not uniform — grade against the right bar. Pick one:

| Shape | What it is | Components that apply |
|---|---|---|
| **Autonomous run** | Long or unattended; agent explores, may spawn subagents, decides its own path | All ten. 6 (early exit) and 7 (done-condition) are load-bearing — they are what make the autonomy safe |
| **Scoped task** | A bounded, known change or investigation; you know roughly what it will touch | 0, 2, 2a, 2b, 5, 7. Stakes and early-exit are often honestly N/A |
| **Transform / question** | Rewrite this, explain that, one-shot output | 5 and 7 only. Everything else is N/A; say so in one line and do not belabor it |

If the shape is ambiguous, ask — the answer changes every verdict below it.

### Step 3: Grade each component

For all ten (in catalog order: 0, 1, 2, 2a, 2b, 3, 4, 5, 6, 7), assign exactly one:

- **Present** — satisfied. **Quote the span that satisfies it.**
- **Weak** — present but underpowered or ambiguous. Quote it, then say precisely what is wrong: unranked, unhedged, vague trigger, two readings.
- **Missing** — absent, and it applies to this run shape.
- **N/A** — genuinely doesn't apply here. Say in a clause why.

Components 5 (the clear ask) and 7 (the done-condition) are **never N/A** for any shape. A prompt without them is defective regardless of size.

Grade 7 last and adversarially, per anti-pattern 8.

### Step 4: Name the consequence of each gap

For every **Missing** and **Weak**, write one sentence: *what the model is now free to decide for itself* — phrased in this prompt's own subject matter, not in the abstract.

- Weak, generic: "No ranked priorities."
- Good: "You asked for it to be both fast and thoroughly tested with no tiebreak, so when they collide — and on a migration they will — the model picks, and it usually picks thorough."

This is the part of the output with actual value. Do not shortcut it.

### Step 5: Ask for what only the user knows

Collect the Missing/Weak components into a short numbered list of **direct questions**. Rules:

- Ask only where the answer would change the run. A component that is Missing but wouldn't alter the agent's behavior here gets noted, not asked.
- Never pre-fill. "What's the real impact if this stays broken?" — not "presumably this is affecting users?"
- Cap at the five that matter most. A twenty-question interrogation for a three-line prompt is itself a failure.
- If the user declines to answer, that is a legitimate choice — proceed and mark the slot as a placeholder.

### Step 6: Offer the rewrite (gated)

End the diagnosis with an offer, not a rewrite: *"Want me to rewrite it with your answers slotted in?"*

Produce the rewrite **only** after the user asks. When you do:

- Follow the template in the catalog's **Reusable Template** section as the ordering.
- Use **only** the user's supplied content — their original wording plus their answers to Step 5. No new facts.
- Any unanswered slot stays a literal `<placeholder like this>` in the output so the user can see the hole. Never fill it plausibly.
- Keep one job per sentence.
- Follow the rewrite with a two-line note: what moved or split, and which placeholders still need filling.

## Output Format

```markdown
## Prompt Doctor — <run shape>

**Under review:** <one-line identification of the specimen>

| # | Component | Verdict | Evidence / gap |
|---|---|---|---|
| 0 | Grounding link | Present | "https://github.com/..." |
| 1 | Stakes / impact | Missing | — |
| 2 | Priorities | Present | "simple and not confusing to users" |
| 2a | Ranked priorities | Weak | Two priorities, no tiebreak |
| 2b | Hard constraints | Missing | — |
| 3 | Opinion (negotiable) | Present | "In my opinion, you should be able to..." |
| 4 | Knowledge-gap disclosure | Present | "I'm not sure about how these behaviors are triggered" |
| 5 | The clear ask | Present | "do a thorough audit of both..." |
| 6 | Early-exit permission | Present | "If you see a simple fix, stop and let me know" |
| 7 | Done-condition | Weak | "come back with a solution" reads as *write the code* |

### What each gap lets the model decide

- **Stakes (missing).** <what it will assume, in this prompt's terms>
- **Ranked priorities (weak).** <which one it will pick when they collide, and why>
- **Done-condition (weak).** <the two readings, and which one it will take>

### What I need from you

1. <direct question>
2. <direct question>

Want me to rewrite it with your answers slotted in?
```

Trim the table to the applicable rows for a Transform/question shape rather than printing eight N/A lines.

## Examples

### GOOD — diagnosing, not doing

**User:** *"Check this before I send it: `https://github.com/org/app/issues/7671` — this has been affecting a number of users. I want a fix that's simple and not confusing. In my opinion `$` should work anywhere in the composer. I'm not sure how the trigger behavior works. Do a thorough audit of both sides. If you see a simple fix, stop and tell me. Come back with a solution."*

**Right:** grade the ten components, flag that "come back with a solution" is compatible with *write the code* when the ask was an audit, flag the unranked pair "simple / not confusing", flag missing hard constraints, and ask what happens on collision. Never open the issue URL.

**Wrong:** fetching issue 7671 and starting the audit.

### GOOD — an honest N/A

**User:** *"Grade this: 'Rewrite this paragraph to be half as long, keep the citations.'"*

**Right:** Transform shape. Ask = Present, done-condition = Present ("half as long, citations kept" is unambiguous and checkable). Everything else N/A in one line. Verdict: fine as-is, send it.

**Wrong:** "This prompt is missing stakes, hard constraints, an early-exit permission, and a knowledge-gap disclosure." Nine of ten components don't belong on a paragraph rewrite.

### BAD — inventing the answer

**Prompt under review has no stakes line.**

**Wrong:** rewriting it as *"This is affecting a number of users in production and needs a reliable fix."* — the user never said that, and it may be false.

**Right:** "Stakes: missing. Who is actually hit by this, and how badly? Without it the model will treat this as an experiment and may hand you a clever fix instead of a safe one."

## Questions This Skill Answers

- "Is this prompt good enough to send?"
- "What's missing from this prompt?"
- "Will the agent misread this?"
- "Review my prompt before I kick off a long run."
- "Which components does my draft cover?"
- "Tighten this prompt up."
- "Why did the agent write code when I only wanted an investigation?" (Almost always component 7.)

## Scope Boundary

One task prompt, diagnosed as text, in conversation. No files written. No files read beyond the component catalog and (when pointed at) the file holding the prompt. The subject matter of the prompt is never investigated — doing that *is* running the prompt, which is the one thing this skill must not do.

## Source

The ten-component anatomy is Theo's (T3.gg, *You're using AI agents wrong*, 2026-09-09, segment 5:50–11:10) for rows 0–7, plus Sean Goedecke's *Tell Agents the Why, Not Just the How* for ranked priorities (2a) and hard constraints (2b). Full attribution and per-component detail in `references/component-catalog.md`.
