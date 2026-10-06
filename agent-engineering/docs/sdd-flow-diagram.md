# sdd-flow — the development cycle at a glance

A picture of what `/sdd-flow` does, stage by stage, as of agent-engineering 3.7.0. It is a reading aid for people: the flow itself runs from `skills/sdd-flow/SKILL.md` and the files under `skills/sdd-flow/phases/`, and those are the source of truth when this page and they disagree.

**How to read it.** Rounded boxes are work done by a spawned subagent. Red boxes are places the flow **stops and waits for you**. Grey boxes are things the orchestrator (the main conversation) does itself: commits, running a script, recording state.

## How a feature is made small: tiers, then slices

The flow cuts a feature down twice, in two different directions, so that you have something real to use and judge as early as possible, in the smallest pieces possible.

- **Tiers cut by depth — how much of the feature exists.** Tier 1 is the narrowest version that is really usable; Tier 2 adds what a normal feature is expected to do; Tier 3 adds the rare cases, hardening, and scale. Each tier is more complete than the one before it. You use a tier before the next one is planned, and a later tier is only built if it turns out to be needed.
- **Slices cut a tier by path — one thin, working thread at a time.** A slice is one concentrated function built all the way through every layer it touches — interface, logic, storage, tests — so that when it lands there is something to run and check. The first slice is the thinnest end-to-end happy path; each later slice adds a capability or hardens an edge.

A tier says **how much** to build. Slices say **in what order** to build it.

```mermaid
flowchart TD
    feature(["A feature"]) --> t1("Tier 1 — POC-plus<br/>narrowest usable version<br/>built now")
    feature -.-> t2("Tier 2 — Standard<br/>a sketch until its own cycle")
    feature -.-> t3("Tier 3 — Full<br/>a sketch until its own cycle")
    t1 --> s1("Slice 1<br/>thinnest end-to-end path")
    t1 --> s2("Slice 2<br/>adds a capability")
    t1 --> s3("Slice 3<br/>hardens the edges")
    subgraph layers ["every slice runs through all the layers it needs"]
        direction LR
        ui["interface"] --- logic["logic"] --- data["storage"] --- tests["tests"]
    end
    s1 --> layers
    s2 --> layers
    s3 --> layers
    layers --> try["after each slice:<br/>something you can run and review"]:::stop

    classDef stop fill:#fde2e2,stroke:#c0392b,color:#000
```

| | Tier | Slice |
|---|---|---|
| Cuts the feature by | Depth: how complete it is | Path: one working thread through the layers |
| Size | One whole cycle of the flow, with its own brief, spec, reviews, and commits | One implement–review–commit loop inside a cycle |
| Decided at | The design gate: the brief proposes three, you pick one (Tier 1 unless you say otherwise) | Planning: the spec lists the slices for the chosen tier, starting from the brief's delivery outline |
| What you get at the end | A version of the feature you can use, and leave feedback on | A piece of that version you can run and check |
| Where you are asked | Design gate, then the completion announcement | The pause after each slice |
| What happens to the rest | Later tiers stay ten-line sketches of behaviour; their own cycle re-decides them | Later slices are already specified; they are built next, in order |

**A slice is vertical, not horizontal.** "Build the database layer, then the API, then the screen" is three horizontal layers: nothing can be tried until the last one lands. A slice goes the other way — a narrow column through all of them — which is why each one ends with something testable. The spec review rejects slices that are layers in disguise.

**There is a third cut, before either of these:** when a request is too broad for one cycle, Step 0 splits it into separately deliverable features (a decomposition), and each of those gets its own tiers and slices. A feature too small to tier or slice is not forced into either — the brief says tiers are not applicable, and the spec falls back to building it whole.

## The whole cycle

```mermaid
flowchart TD
    start(["/sdd-flow task"]) --> s0("Step 0 — Scope<br/>does this fit one cycle?")
    s0 -- "too large" --> decomp["STOP — decomposition written<br/>you run /sdd-flow per item"]:::stop
    s0 -- "fits" --> s1["Step 1 — Mode<br/>supervised or autonomous"]:::orch
    s1 --> s15["Step 1.5 — Clarification gate<br/>STOP in both modes<br/>you run /research-clarify"]:::stop
    s15 --> s2("Step 2 — Research<br/>2a research and completeness check<br/>2b ADR candidates listed for the design gate<br/>2c critical review, 2d fix findings")
    s2 --> c2["2e commit research"]:::orch
    c2 --> s25a("Step 2.5a — Design brief<br/>at most 150 lines, plain language<br/>proposes three tiers, writes the tier plan")
    s25a --> gate["Step 2.5b — Design gate<br/>STOP in both modes<br/>answer questions, pick a tier,<br/>accept ADR candidates, approve"]:::stop
    gate -- "answers or changes" --> s25c("2.5c — Revise the brief")
    s25c --> gate
    gate -- "approve" --> m1["Write the accepted ADRs<br/>Mirror tiers to BB tasks<br/>tier being built: in progress"]:::orch
    m1 --> s3a("Step 3a — Specification<br/>covers the approved tier only<br/>lists what is deferred")
    s3a --> s3c("3b capture ADRs<br/>3c specialist panel, in parallel<br/>then one synthesis")
    s3c -- "findings" --> fix3("fix the spec, re-run the panel<br/>at most 3 rounds")
    fix3 --> s3c
    fix3 -- "no progress" --> halt3["STOP — panel halt<br/>you fix the spec by hand"]:::stop
    s3c -- "proceed" --> s3d("3d critical review of the spec<br/>3e fix all findings")
    s3d --> c3["3f commit planning"]:::orch
    c3 --> s3g{"3g — does the spec depart<br/>from the approved brief?"}
    s3g -- "yes" --> dev["STOP in both modes<br/>deviations shown, you accept or edit"]:::stop
    dev --> s4
    s3g -- "no" --> s4{"Step 4 — Implementation<br/>route on delivery mode"}
    s4 -- "per-slice" --> slices("Per-slice cycle<br/>see the next diagram")
    s4 -- "whole-feature" --> wf("4a implement<br/>4a.5 blind site count and diff<br/>4b code review, 4c fix")
    slices --> eof
    wf --> eof("4d critical review of the code, 4e fix<br/>4e.5 final blind recount<br/>4f completion: summary, tier plan updated")
    eof --> m2["Mirror: tier in review"]:::orch
    m2 --> s4h["4h — STOP, supervised mode only<br/>ready to commit?<br/>waits until you say yes"]:::stop
    s4h --> c4["4i commit implementation"]:::orch
    c4 --> done["4j — Mirror: tier done<br/>announcement, progress file rotated"]:::orch
    done --> next(["later: /sdd-flow --next-tier<br/>a new cycle for the next tier"])

    classDef stop fill:#fde2e2,stroke:#c0392b,color:#000
    classDef orch fill:#eeeeee,stroke:#888888,color:#000
```

## Inside per-slice implementation

When the spec says `delivery_mode: per-slice` (the default for new specs), this loop runs once per slice, in order. Then the end-of-feature steps in the diagram above run once.

```mermaid
flowchart TD
    scaffold("4a.0 — create the slice progress table<br/>once per feature") --> impl("4a — implement one slice<br/>code, tests, list of enforcement sites")
    impl --> count("4a.5 — blind site count<br/>a fresh subagent that never sees the implementer's list")
    count --> diff["diff the two lists<br/>scripts/site-diff.py"]:::orch
    diff --> review("4b — slice review<br/>includes the design brief check")
    review -- "any finding" --> fix("4c — fix all of them, then recount<br/>and re-review, at most 3 rounds")
    fix --> count
    fix -- "no progress, or 3 rounds used" --> halt["STOP in every mode — slice halted<br/>findings go to the ledger<br/>you fix them, then continue re-reviews"]:::stop
    halt -- "continue" --> count
    review -- "approved" --> retro("4c.5 — slice retrospective<br/>updates the learnings ledger")
    retro -- "recommends re-planning" --> replan["STOP in every mode<br/>--replan commits the slice, revises<br/>the brief, then the spec"]:::stop
    replan -- "--override-replan" --> commit
    retro --> commit["4c.6 — mark the slice complete<br/>and commit it"]:::orch
    commit --> pause["STOP — slice pause<br/>unless --skip-slice-checkpoints<br/>shows the brief check line"]:::stop
    pause -- "more slices" --> impl
    pause -- "last slice done" --> eof(["end-of-feature steps"])

    classDef stop fill:#fde2e2,stroke:#c0392b,color:#000
    classDef orch fill:#eeeeee,stroke:#888888,color:#000
```

## What happens at each stage

| Stage | What is done | Who does it | What it writes (under `SDD/`) | Where it can stop |
|---|---|---|---|---|
| 0 Scope | Decides whether the request fits one cycle. `--next-tier` instead reads the tier plan and copies task comments into its Feedback | Sonnet subagent | `flow/DECOMPOSITION-*` (only when too large) | Always, when the feature is too large |
| 1 Mode | Supervised or autonomous | Orchestrator | — | — |
| 1.5 Clarification | An interview that gets your design concept written down. On a next-tier cycle it is a feedback interview instead | You, with `/research-clarify` | `research/CLARIFICATION-*` | Both modes, unless `--skip-clarify` or the file exists |
| 2 Research | Investigates the codebase; finds cross-cutting decisions and lists them as ADR candidates for the design gate; adversarial review; fixes | Sonnet subagents; Opus for the review | `research/RESEARCH-*`, `reviews/CRITICAL-RESEARCH-*` | — |
| 2.5 Design gate | Writes the one planning document meant for you: what will be built, decisions, footprint, tiers, questions. Then waits. It also lists the proposed ADRs; approving writes them, and you can drop any by name | Opus subagent writes; you approve | `requirements/DESIGN-*`, `flow/TIERS-*`, `adr/*` (on approval) | **Both modes, every time the brief is written or rewritten.** `approve` is refused while a question is open |
| 3 Planning | Writes the spec for the approved tier; specialist panel and adversarial review; fixes. The spec must record every departure from the brief | Sonnet subagents; Opus for synthesis and review | `requirements/SPEC-*`, `reviews/PANEL-*`, `reviews/CRITICAL-SPEC-*` | Panel halt after 3 rounds or no progress. **3g, both modes, when the spec departs from the brief** |
| 4 Implementation | Builds the feature (whole, or slice by slice). Every control's enforcement sites are listed twice — by the implementer and by a blind subagent — and the two lists are compared for places only one of them found. Code review, adversarial review, fixes, final recount, completion | Sonnet subagents; Opus for the adversarial review | code and tests, `implementation/*`, `reviews/REVIEW-*`, `reviews/SITE-*`, `reviews/CRITICAL-IMPL-*` | Slice pauses (per-slice). Slice fix-loop halt and re-planning halt (every mode). Recount halt. 4h before the final commit (supervised only) |
| Done | Tier marked shipped in the tier plan; task set to done; announcement names what shipped and what is left | Orchestrator | updated `flow/TIERS-*` | — |

## What the stops are for

| Stop | Supervised | Autonomous | Why it exists |
|---|---|---|---|
| Decomposition (Step 0) | stops | stops | The request is too large for one cycle |
| Clarification (1.5) | stops | stops | Your intent has to be written down before research |
| Design gate (2.5) | stops | stops | You approve *what will be built* before anything is specified |
| Slicing not practical (3a) | stops | stops | The spec asked for slices, and no meaningful ones exist. Fall back to building it whole, or point at a slice boundary and retry — either way planning carries on from the spec check, with every review |
| Panel halt (3c) | stops | stops | The spec did not pass the specialist panel in 3 rounds, or a round made no progress. You fix the spec by hand |
| Deviation check (3g) | stops if deviations | stops if deviations | The spec is no longer what you approved |
| Slice fix-loop halt (4c) | stops | stops | A slice did not pass its review in 3 fix rounds, or a round made no progress. You resolve the findings; `continue` re-counts and re-reviews the slice |
| Slice pause | stops | stops | Review each slice while it is small. Off with `--skip-slice-checkpoints` |
| Re-planning halt (4c.5) | stops | stops | A slice showed the plan is wrong. `--replan` or `--override-replan`; either one commits the slice first |
| Final recount halt (4e.5) | stops | stops | The final recount's verification review still has open findings after 3 fix rounds, or a round made no progress. That covers the two lists of enforcement sites disagreeing on which places enforce a rule, and matching lists where a site's justification for having no proof of its own has not been accepted. You resolve the findings; `continue` starts from a fresh recount |
| Before the final commit (4h) | stops; until you say yes the final commit is not made, and `continue` asks again. In per-slice mode the slices are already committed, one commit each | does not stop | Last look before the final commit |
| A stop record `continue` does not recognise | stops | stops | A stop left by another version. It is shown to you as written; the flow never guesses what it was waiting for |
| A subagent failed twice | stops | stops | The same step failed, was retried with more context, and failed again |
| Broken install or old folder layout | stops | stops | A file the flow ships is missing, or the repo still uses the 1.x `SDD/` layout. Not resumable until fixed |

Every stop above that waits for your answer is written to `SDD/orchestration/progress.md` before the flow asks, and `/sdd-flow continue` resumes from that record. The rest write no such record: the slice pause needs no answer (`continue` starts the next slice), and after a decomposition, a broken or old-layout install, or a twice-failed subagent you deal with the cause and run the flow again.

## Tiers across cycles

A feature is delivered in up to three tiers — Tier 1 POC-plus, Tier 2 Standard, Tier 3 Full — and each tier is one full pass through the first diagram. The rules for what belongs in which tier live in `skills/simplicity-challenge/references/tiers.md`.

```mermaid
flowchart LR
    t1("Cycle 1<br/>builds Tier 1") --> use1["you use it<br/>leave feedback on the Tier 2 task"]:::stop
    use1 --> t2("/sdd-flow --next-tier<br/>Cycle 2 builds Tier 2<br/>starts from the feedback")
    t2 --> use2["you use it<br/>leave feedback on the Tier 3 task"]:::stop
    use2 --> t3("Cycle 3 builds Tier 3<br/>or never: a tier that is<br/>not needed is not built")

    classDef stop fill:#fde2e2,stroke:#c0392b,color:#000
```

The tier plan (`SDD/flow/TIERS-[feature-name].md`) carries what shipped, what was deferred, and the feedback from one cycle to the next. BB tasks mirror it: one parent task per feature, one sub-task per tier.
