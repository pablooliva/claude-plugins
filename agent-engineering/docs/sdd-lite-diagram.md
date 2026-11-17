# sdd-lite — the light build path at a glance

A picture of what `/sdd-lite` does, step by step, as of agent-engineering 5.3.0. It is a reading aid for people: the skill itself runs from `skills/sdd-lite/SKILL.md`, and that file is the source of truth when this page and it disagree.

**How to read it.** Every box is work done in the main conversation — `sdd-lite` spawns no subagents. Red boxes are places it **stops and waits for you**. Grey boxes are the one step done by another model (the Codex review, run on every change) and the hand-off to `sdd-flow`.

## Which path: sdd-lite or sdd-flow

```mermaid
flowchart TD
    task(["A feature or change"]) --> q1{"Does it need any<br/>decisions from you?"}
    q1 -- "no: a one-line fix" --> plain["Just make it<br/>no brief, no records"]
    q1 -- "yes" --> q2{"Can one short interview<br/>settle what you want?"}
    q2 -- "no" --> flow["/sdd-flow<br/>research, design gate, spec,<br/>panel, slices, reviews"]:::other
    q2 -- "yes" --> q3{"About a day of building<br/>or less, in one part?"}
    q3 -- "no" --> flow
    q3 -- "yes" --> lite["/sdd-lite"]
    lite -. "still unclear after one round,<br/>or too large, or the fix check<br/>still finds a HIGH" .-> flow

    classDef other fill:#eeeeee,stroke:#888888,color:#000
```

`sdd-lite` exists because, on clear tasks, `sdd-flow` cost 15 to 44 times a plain build and wrote larger, broader code, with correctness the same or better (never worse), and later cycles reopened only a few of its records: your decisions, the decision records (ADRs), the glossary and the tier plan. `sdd-lite` keeps those and the one independent review, updates the user docs the change needs, and writes no other process records.

## The whole run

```mermaid
flowchart TD
    start(["/sdd-lite task"]) --> s1("1 — Read the ground<br/>request, code and the code around it,<br/>glossary, ADRs, tier plan, earlier briefs<br/>decide: ordinary or risky")
    s1 --> s2("2 — Interview<br/>only what is still open,<br/>one message, a recommended<br/>answer for each question")
    s2 -- "nothing open" --> s3
    s2 --> answers["STOP — you answer<br/>'all recommendations' is enough"]:::stop
    answers -- "still unsure, or more than<br/>about a day, or more than one part" --> toflow["Told to switch to /sdd-flow<br/>it does not switch itself"]:::other
    answers --> s3("3 — Brief<br/>one page, SDD/briefs/BRIEF-###-name.md<br/>decisions, how it works, builds on,<br/>not now, beyond the request,<br/>done when, risk, ADRs to write")
    s3 --> gate["STOP — the one gate<br/>you approve the brief<br/>nothing is built before"]:::stop
    gate -- "changes" --> s3
    gate -- "approve" --> s4("4 — Build<br/>small steps, tests as you go,<br/>extend before adding, glossary names,<br/>inside the brief; risky: prove each<br/>security rule; whole suite at the end")
    s4 -- "something the brief<br/>does not cover" --> ask["STOP — you decide<br/>the answer goes into the brief"]:::stop
    ask --> s4
    s4 --> nf{"5 — every new file<br/>named in Builds on?"}
    nf -- "no" --> ask
    nf -- "yes" --> r1["5 — Codex review, every change<br/>codex exec -s read-only<br/>one FINDING line per finding"]:::other
    r1 --> fix("Fix each real HIGH or MEDIUM<br/>with a test that fails without it<br/>LOW: listed, not fixed")
    fix --> r2["One check of the fixes<br/>and no more: each F-number<br/>marked fixed or open"]:::other
    r2 -- "still an open HIGH, or one that would<br/>lose data, open a security hole<br/>or do a wrong irreversible action" --> halt["STOP — needs /sdd-flow<br/>or your decision"]:::stop
    r2 -- "clean, or only lesser<br/>findings, fixed or listed" --> s6
    s6("6 — Close-out<br/>ADRs listed in the brief,<br/>glossary terms, tier-plan line,<br/>README or user docs")
    s6 --> s7("7 — Report<br/>what was built, tests, review,<br/>records written, your check<br/>offers to commit, /retro reminder")

    classDef stop fill:#fde2e2,stroke:#c0392b,color:#000
    classDef other fill:#eeeeee,stroke:#888888,color:#000
```

## What happens at each step

| Step | What is done | What it writes | Where it can stop |
|---|---|---|---|
| 1 Read the ground | Reads the request, the code it touches and the code around it (its module, neighbours, helpers and test fixtures), and, when they exist, `SDD/UBIQUITOUS_LANGUAGE.md` (the glossary), `SDD/adr/`, the feature's tier plan and earlier briefs. Sets the risk class: **risky** when the change touches authentication, secrets, personal data, payments, deleting or migrating stored data, an exposed network surface, an agent acting on untrusted input, an effect that cannot be recalled, or anything else expensive to get wrong. When unsure, risky | — | — |
| 2 Interview | Asks only what the request, the code and the records leave open and what changes what gets built. Each question carries a recommended answer and its consequence | — | Waits for your answers. Points you to `/sdd-flow` when you are still unsure after one round, or the work is more than about a day or more than one part |
| 3 Brief | One page: what you can do afterwards, your decisions (quoted), how it will work (with `file:line` for today's code), what it builds on (the existing code it extends, and every new file), what is left out, which changes beyond the request stay off, how you will check it, the risk class (with the security rules a risky change must hold), and the decision records to write with their alternatives and consequences | `SDD/briefs/BRIEF-###-name.md` | **Always.** Nothing is built until you approve; approving also approves writing exactly the listed ADRs |
| 4 Build | Builds and tests in the conversation, extending the code the brief builds on before adding any. A risky change proves each security rule with a test that fails when its guard is removed, in a scratch copy, one line each under `## Security proofs` in the brief. Tests follow `sdd-flow/references/test-integrity.md` §1, with the brief in place of the spec; a changed or removed test is one line under `## Test changes` in the brief | code and tests | When the work reaches something the brief does not cover that changes what you get, or needs a new file the brief does not name |
| 5 Review | First, every new file is checked against the brief. Then every change: one Codex review (`codex exec -s read-only`, its output outside the repository), each finding opening with one `FINDING F<n> \| HIGH\|MEDIUM\|LOW \| file:line \| open` line; fixes with tests for HIGH and MEDIUM (LOW listed, not fixed); one check of the fixes, given the first review, which marks each earlier ID `fixed` or `open`; no further rounds. No Codex CLI: asks whether to go on without one | — (no review report) | On a new file the brief does not name. When the check still reports an open HIGH finding, or one you judge would cause data loss, a security hole or a wrong irreversible action |
| 6 Close-out | Writes each ADR the brief listed through `cross-cutting-adr` (pre-approved); a new binding decision that came up while building is shown to you first. Adds the change's terms to the glossary, one dated line to the tier plan, and what a user needs to the README | `adr/*`, glossary, tier-plan line, user docs | Only to ask about an ADR the brief did not list |
| 7 Report | What was built, test result, review result (or why none ran), records written, what is not done, your check, and a one-line `/retro` reminder (never run for you) | — | Offers to commit; never commits unasked |

## What it leaves behind

| Kept | Not written |
|---|---|
| The brief (`SDD/briefs/`) — the record of *why* | Research document |
| ADRs (`SDD/adr/`) for decisions that bind later work | Spec, implementation plan, slice files |
| Glossary entries (`SDD/UBIQUITOUS_LANGUAGE.md`) | Specialist panel |
| One tier-plan line, when the feature has a tier plan | Review reports, progress logs, run logs |

Any other file a `sdd-lite` run writes under `SDD/` is a sign the full flow is being rebuilt by hand: if the work needs it, it needs `/sdd-flow`.
