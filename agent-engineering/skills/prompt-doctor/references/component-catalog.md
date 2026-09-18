# Agent Prompt Component Catalog

The ten components a well-structured agent task prompt can carry, in the order they
normally appear. Rows 0–7 are Theo's (T3.gg), dissected from a real prompt he dictated
live; rows 2a and 2b are Sean Goedecke's additions.

Sources:
- Theo (T3.gg), *You're using AI agents wrong* (2026-09-09), segment 5:50–11:10 — https://www.youtube.com/watch?v=q1D90-uGvBg&t=350s
- Sean Goedecke, *Tell Agents the Why, Not Just the How* (2026) — https://www.seangoedecke.com/tell-agents-the-why/

Governing principle: **"If you don't say something explicitly, it will do whatever it wants."**
Ambiguity is filled by the model's own judgment, so every component you omit is a decision
you have silently delegated.

---

## The Components

### 0. Grounding link

**Form:** the primary source — issue URL, doc, spec, file path, error output — as the first line.

**Job:** gives the agent the source itself to read instead of your paraphrase of it.

**Present when:** a real, fetchable/readable reference is given, not described.
**Weak when:** the prompt describes a source without pointing at it ("there's an issue about
this", "the failing test"). A paraphrase is the thing this component exists to replace.
**N/A when:** no external artifact exists — the task originates entirely in the prompt.

---

### 1. Stakes / impact

**Form:** who is affected and why this must be done reliably. *"This has been affecting a
number of users recently."*

**Job:** signals real vs. experimental. Shifts the agent toward a reliable fix over a quick
or clever one. Optional, but it is what stops the model treating production work like a
side project.

**Present when:** the prompt says who is hurt, how broadly, or what breaks if this is wrong.
**Weak when:** urgency is asserted without impact ("this is important", "ASAP") — that sets
a tone but gives nothing to reason with.
**N/A when:** the task is genuinely exploratory or throwaway.

---

### 2. Priorities (non-negotiable)

**Form:** what to optimize for, stated flatly. *"A fix that is both simple in its
implementation and not confusing to users."*

**Job:** explicitly picks the optimization target — and by omission rules out the others
(not speed, not exhaustive detail). Flat statement = a no-compromise line.

**Present when:** the prompt names what "good" means for this task.
**Weak when:** the priorities are implied by the task type rather than stated, or they are
hedged ("ideally simple") when they are actually non-negotiable.

---

### 2a. Ranked priorities *(Goedecke)*

**Form:** an explicit ordering between the priorities. *"Preventing bugs matters more than
elegant code."*

**Job:** a flat list gives the model nothing to trade against when the priorities conflict —
and they will conflict. An ordering is what it uses at the decision point.

**Present when:** the prompt says which priority wins.
**Weak when:** two or more priorities are named but never ranked (this is the most common
gap; Theo's own prompt has it — "simple **and** not confusing", with no tiebreak).
**N/A when:** there is exactly one priority, so there is nothing to rank.

---

### 2b. Hard constraints *(Goedecke)*

**Form:** budget, deadline, hardware, runtime, battery, allowed dependencies, files or
systems that must not be touched, backwards-compatibility requirements.

**Job:** rules out whole classes of answer *before* the model invests in them. Goedecke
treats this as a required part of the context block.

**Present when:** at least one real boundary is stated.
**Weak when:** a constraint is implied ("keep it small") rather than bounded.
**N/A when:** the task genuinely has no boundary the agent could violate.

---

### 3. Opinion (negotiable)

**Form:** your hypothesis or preferred approach, explicitly hedged. *"**In my opinion**, you
should be able to use `$` to call any skill anywhere in the composer."*

**Job:** the hedge is deliberate and load-bearing. It gives the model the contours of your
expectation *and* explicit room to push back if the idea isn't viable.

**Present when:** a preference is stated *and* marked as negotiable.
**Weak when:** the opinion is stated as a command, so the model cannot tell it is allowed to
disagree — or, inversely, everything is hedged, so nothing reads as firm.
**N/A when:** you have no hypothesis. Do not manufacture one.

---

### 4. Knowledge-gap disclosure

**Form:** what you don't know. *"I'm not sure about how these behaviors are triggered, or how
the skill in the composer becomes the right text for the model."*

**Job:** two effects. The model stops treating your framing and the issue text as ground
truth, and it calibrates its answer — explaining what you don't know, skipping what you do.

**Present when:** specific uncertainties are named.
**Weak when:** the gap is generic ("I don't know much about this codebase") rather than
pointed at a mechanism.
**N/A when:** you genuinely have no uncertainty — rare, and worth a second look.

Note: this covers *known* unknowns only. Surfacing the unknowns you wouldn't think to
disclose is a separate exercise (blindspot passes, interviews) that happens before the prompt
is written.

---

### 5. The clear ask

**Form:** the one concrete action for *this* run. *"I want you to do a thorough audit of both
Claude Code's behavior and how we are implementing that behavior."*

**Job:** overrides the earlier goal sentences. Those describe where the *thread* should end
up; this says what to do *now*. Best when aimed at the uncertain areas from component 4 —
that's where the answer usually lives.

**Present when:** there is exactly one unambiguous action for this run.
**Weak when:** the end goal is doing double duty as the ask, or several asks are bundled
without an order.
**Never N/A.** A prompt with no clear ask is the defect, not an exception.

---

### 6. Early-exit permission

**Form:** an explicit stop condition. *"If you see a simple fix we can apply to solve the
problem, stop and let me know so we can apply it ASAP."*

**Job:** lets the agent confidently stop mid-exploration — even with parallel subagents still
running — instead of exhaustively enumerating seventeen options when option one was always
going to be chosen. This is also what justifies granting more autonomy and higher effort on
the run.

**Present when:** a named condition tells the agent when to come back early.
**Weak when:** the exit exists but its trigger is vague ("if you find anything interesting").
**N/A when:** the run is short enough that there is no wandering to prevent.

---

### 7. Precise done-condition

**Form:** the deliverable, worded so it cannot be misread. *"Come back when you have a
confident **path to** a solution."* — changed live from "a confident solution" precisely so
it could not be read as *write the code*.

**Job:** defines what returning looks like. The wording is the whole component: "path to a
solution" and "a solution" produce completely different runs.

**Present when:** the deliverable is named in terms that admit one reading.
**Weak when:** the done-condition is a restatement of the ask, or its wording is compatible
with both "investigate" and "implement" when you meant only one.
**Never N/A.**

---

## Reusable Template

```
<link to primary source: issue / doc / spec>

<stakes: who is affected and why this must be done reliably>
<priorities, RANKED against each other: X matters more than Y>
<hard constraints: budget, deadline, hardware, runtime, deps, do-not-touch>
In my opinion, <your hypothesis or preferred approach — open to pushback>.

I'm not sure about <your specific knowledge gaps>.
I want you to <the one concrete ask for this run, e.g. audit X and Y>.
If you <find an early success condition>, stop and let me know.
Come back when you have <precisely worded deliverable — not "the code" unless you want code>.
```

## Cross-Cutting Rules

1. **One sentence, one job.** Each line grounds, raises stakes, prioritizes, hedges,
   discloses, asks, grants an exit, or defines done — one of those, not two.
2. **Mark what's negotiable.** Hard constraints flat; soft ones flagged "in my opinion". The
   model then knows where pushback is welcome.
3. **Disclose what you don't know**, so your framing isn't taken as ground truth.
4. **Separate the end goal from the current ask.** Where the thread ends up ≠ what to do now.
5. **Give easy outs.** Explicit early-stop conditions are what make higher autonomy safe.
6. **Word the done-condition so it can't be misread.**
7. **Tell the why, not just the how** (Goedecke). Withholding your actual goal and asking
   only about your attempted solution is the XY problem: you get a good answer to the wrong
   question.
