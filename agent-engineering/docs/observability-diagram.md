# Tracing and evals in an sdd-flow cycle — at a glance

A picture of where tracing and evals are set up, built, checked, and used in an `/sdd-flow` cycle. **It describes a proposal, built in four steps. As of agent-engineering 3.12.0 steps 1 to 3 exist: `/observability-init` with the tracing standard, tracing inside `/sdd-flow`, and evals inside `/sdd-flow`. `/eval-harvest` does not exist** — every mention of it describes the plan, not the plugin. The table at the end says which parts of this picture work, and which have been used on a real application. For what was built, the flow's own files are the source of truth — `skills/sdd-flow/references/evals.md` for evals — and the proposal (`proposals/observability-and-evals-2026-10-04.md` at the repository root) says where each step was built differently from its plan. As each build step ships, this file is updated to say what exists; the cycle itself is in `sdd-flow-diagram.md`, beside this file.

**How to read it.** Same conventions as `sdd-flow-diagram.md`: rounded boxes are work done by a spawned subagent or a skill, red boxes are places the flow **stops and waits for you**, grey boxes are things the orchestrator (the main conversation) or a script does. In boxes that carry both, a line starting `tracing:` applies when tracing is on and a line starting `evals:` when evals are on.

## Two scenarios

The same machinery serves two different needs, and a feature can be in the first without the second.

| | Scenario 1 — any application | Scenario 2 — the application has an LLM or an agent in it |
|---|---|---|
| What it is for | The coding agents and you can see what the application actually did when it ran, without reading the code | That, plus a way to say whether the LLM's output is any good |
| Switched on by | The application has the tracing foundation | The foundation, **and** the feature has a model call, a tool given to a model, a retrieval store feeding a model, agent-to-agent messages, or a model output that drives an action |
| The spec carries | A planned call graph; the entry points, LLM calls, and external calls in it are marked | Also the eval cases, written out, and a maximum number of model calls per request |
| The implementer adds | Spans for the entry points and external calls the feature adds | Also spans for its LLM calls, the spec's eval cases as a file, and their checks |
| Recorded with no work by anyone | Every call to the application's own functions (Python 3.12 or later) — names and timing; arguments and results only when a setting asks for them | The same |
| The review checks | The call tree a real run produced, against the plan | Also what the model really answered: the flow runs the eval cases just before the review and sends the run to Opik, and the review reads the results against the spec |
| What you are asked | Nothing new | At the design gate: how quality will be judged. At the final commit: whether to accept what only a judge could score |
| After the tier is used | Traces are in Opik or Langfuse to look at | `/eval-harvest` turns real failures into new eval cases — only while traces go to Opik |

```mermaid
flowchart TD
    feat(["A feature enters /sdd-flow"]) --> f{"Does the application have<br/>the tracing foundation?<br/>checked at Step 0"}
    f -- "no" --> off["tracing off, evals off<br/>the cycle runs exactly as it does today"]:::orch
    f -- "yes" --> l{"Does the feature have<br/>an LLM or agent in it?<br/>the same detection the security review uses"}
    l -- "no" --> a["Scenario 1<br/>tracing on, evals off"]:::trace
    l -- "yes" --> b["Scenario 2<br/>tracing on, evals on"]:::eval

    classDef orch fill:#eeeeee,stroke:#888888,color:#000
    classDef trace fill:#dbeafe,stroke:#2563eb,color:#000
    classDef eval fill:#dcfce7,stroke:#16a34a,color:#000
```

The spec can overrule the detection in either direction: `tracing:` and `evals:` each take `auto` (the default, shown above), `true`, or `false`. Asking for either with no foundation stops planning and tells you to change the field or run `/observability-init` before the next cycle (`tracing:` since 3.8.0, `evals:` since 3.12.0).

## Three commands, run at three different times

Tracing and evals are not one thing you switch on. The work is split across three commands — each is a skill you start by typing its name — and you run them at different points in an application's life. `/sdd-flow` is the one you already use; the other two are new, and you run them yourself, outside an `/sdd-flow` cycle.

| | Command | When you run it | What it does |
|---|---|---|---|
| 1 | `/observability-init` | **Once per application, ever** — not once per cycle. At a moment when no `/sdd-flow` cycle is running: for a new application, right after its first cycle finishes | Puts the tracing plumbing into the application: the one module that sends traces, the kill switch, and a test that fails if an entry point is not traced |
| 2 | `/sdd-flow` | Every time you build a feature or a tier, as you do today | Uses that plumbing while it builds: adds tracing for what each slice adds, checks what really ran against the plan, and writes and runs the evals |
| 3 | `/eval-harvest` | After you have used what was built for a while | Looks at the real runs that went wrong and offers them to you as new eval cases, so the next round of building is tested against them |

**Why step 1 is never run in the middle of a cycle.** `/sdd-flow` decides at the start of a cycle whether tracing and evals are on, writes the spec to match, and keeps that answer until the cycle ends. Plumbing installed halfway through changes nothing until the next cycle starts. And it cannot be run on an empty repository: it wires up the framework and entry points it finds, so there has to be something to find.

- **An existing application:** run it once, any time before the next cycle.
- **A new application, starting from nothing:** run `/sdd-flow` on the idea as usual and build its first tier. Nothing about tracing is done or asked for in that cycle. When the cycle is finished, run `/observability-init` once; it instruments what the first cycle built. Every later cycle is traced from its research step on, with no further setup. The only cost is that the first cycle is built without trace checks or evals — a reason to keep the first tier small, not a reason to build an artificial skeleton.

The diagram is the same three commands on a timeline. Step 1 happens once. Steps 2 and 3 repeat: build a tier, use it, harvest what went wrong, build the next tier.

```mermaid
flowchart LR
    init("1 — /observability-init<br/>once per application<br/>bootstrap, kill switch, entry-point test") --> cycle("2 — /sdd-flow<br/>one cycle per tier<br/>spans and evals built slice by slice")
    cycle --> use["you use the tier<br/>traces arrive in Opik or Langfuse"]:::stop
    use -- "Scenario 2,<br/>traces in Opik" --> harvest("3 — /eval-harvest<br/>real failures become eval cases,<br/>you approve each one")
    harvest --> next("2 again — /sdd-flow --next-tier<br/>starts from your feedback<br/>and the larger dataset")
    use -- "Scenario 1,<br/>or traces in Langfuse" --> next
    next --> use

    classDef stop fill:#fde2e2,stroke:#c0392b,color:#000
```

Step 3 applies only to an application with an LLM in it (Scenario 2), and only while its traces go to Opik. Otherwise you go from using a tier straight to building the next one.

## Inside one cycle

What tracing and evals add to each step of the cycle. Steps they do not touch are left out; the per-slice path is shown.

```mermaid
flowchart TD
    s0["Step 0 — records whether<br/>the tracing foundation exists"]:::orch --> brief("2.5a Design brief<br/>first reading of both gates<br/>evals: one Key decision, how quality is judged")
    brief --> gate["2.5b Design gate — STOP in both modes<br/>evals: you approve how quality is judged"]:::stop
    gate --> spec("3a Specification<br/>tracing: planned call graph, traced nodes marked,<br/>each slice names its nodes<br/>evals: eval cases written out,<br/>each slice names its evals")
    spec --> bind["3c — both gates settled from the finished spec<br/>and recorded in progress.md"]:::orch
    bind --> rev3("3d Spec review<br/>tracing: nodes present and assigned to slices<br/>evals: every LLM requirement has a rule-based eval,<br/>or is listed for you to accept at the final commit")
    rev3 --> impl("4a Implement one slice<br/>tracing: spans for the entry points, LLM calls,<br/>and external calls it adds<br/>evals: the spec's cases and their checks;<br/>the first such slice also creates the eval run")
    impl --> review("4b Slice review<br/>tracing: trace run, call tree, compare with the plan<br/>evals: the flow first runs the cases and sends the run to Opik;<br/>the review reads the results against the spec")
    review -- "any finding" --> fix("4c Fix, recount, re-review<br/>at most 3 rounds")
    fix --> review
    fix -- "no progress,<br/>or 3 rounds used" --> halt["STOP — slice halted<br/>an existing stop"]:::stop
    review -- "no finding" --> commit["4c.6 commit the slice"]:::orch
    commit --> pause["Slice pause<br/>evals: shows the last line of the slice's eval run"]:::stop
    pause -- "more slices" --> impl
    pause -- "last slice done" --> crit("4d critical review of the code, 4e fix")
    crit --> final("4e.5 Final recount<br/>with either gate on, its verification always runs<br/>tracing: whole call graph compared<br/>evals: every case run again, and checked")
    final -- "any finding" --> ffix("fix, recount, verify again<br/>at most 3 rounds")
    ffix --> final
    ffix -- "no progress,<br/>or 3 rounds used" --> fhalt["STOP — final recount halt<br/>an existing stop"]:::stop
    final -- "no finding" --> done("4f Completion<br/>reads the final call tree and eval results")
    done -- "tracing or evals: it finds something that<br/>needs code or tests changed" --> fhalt
    done --> q{"Is there a requirement<br/>only a judge can score?"}
    q -- "yes" --> ask["4h STOP in both modes<br/>judged scores shown, outputs in the results file<br/>yes commits and accepts"]:::stop
    q -- "no, supervised" --> ask2["4h STOP — ready to commit?<br/>as today"]:::stop
    q -- "no, autonomous" --> c4["4i commit, 4j announcement"]:::orch
    ask --> c4
    ask2 --> c4

    classDef stop fill:#fde2e2,stroke:#c0392b,color:#000
    classDef orch fill:#eeeeee,stroke:#888888,color:#000
```

In whole-feature mode the same checks run once in the code review (4b) instead of once per slice. The final recount (4e.5) and everything after it are shared by both modes.

Not drawn: with evals on, the flow stops before a review when the application's model cannot be reached twice in a row — nothing can be reviewed, and no fix round is spent. `sdd-flow-diagram.md` lists that stop.

## Inside a review: the two checks

```mermaid
flowchart TD
    subgraph T ["Tracing check — when tracing is on"]
        run("trace run<br/>the tests that drive real entry points,<br/>tracing forced on, every request kept") --> file["span file on disk"]:::orch
        file --> tree["trace-tree.py<br/>call tree per request, call counts,<br/>scan for headers and secrets"]:::orch
        tree --> cmp{"Any of these?<br/>the trace run cannot be read<br/>a header or secret on a span<br/>an LLM or external call the plan does not show<br/>more LLM calls in a request than the plan allows<br/>a marked node of this slice or an earlier one that never ran,<br/>unless the spec marks it not exercised in tests<br/>a new entry point that is not traced<br/>a structured value stored as a JSON string,<br/>a hand-written span on a function already recorded,<br/>a backend named outside the bootstrap module"}
        cmp -- "yes" --> tf["finding"]
    end
    subgraph E ["Eval check — when evals are on"]
        ev["before the review, the flow's main session<br/>runs the eval command: real model calls,<br/>every case three times"]:::orch
        ev -- "the model cannot be reached, twice" --> estop["STOP — the eval run could not be made<br/>nothing is reviewed"]:::stop
        ev --> res["results file in the repository<br/>the run is also sent to Opik as one experiment<br/>if Opik is unreachable: a warning, the run still counts"]:::orch
        res --> chk{"Any of these?<br/>no result, or a case in scope missing from it<br/>a rule-checked case failed on any of its three runs<br/>a case is not the spec's, or was weakened or removed<br/>a check passed an answer that breaks its requirement<br/>the eval task does not go through the application's own code<br/>the application was taught a case<br/>a judged case has a run with no score<br/>a secret had to be replaced in the results"}
        chk -- "yes" --> ef["finding"]
        res --> judged["judged scores: shown to you before the final commit<br/>they never pass or fail anything"]:::orch
    end
    tf --> loop("the review's existing fix loop")
    ef --> loop
    cmp -- "no" --> ok(["no finding from this check"])
    chk -- "no" --> ok

    classDef orch fill:#eeeeee,stroke:#888888,color:#000
    classDef stop fill:#fde2e2,stroke:#c0392b,color:#000
```

The eval run is separate from the trace run: it writes no span file, and the call tree a review reads comes from the tests alone.

As built in 3.8.0, the tracing check is one file every review reads — `skills/sdd-flow/references/tracing-lens.md`. A model call is matched to its planned node by the function that made it; where the tree cannot tell two planned nodes apart, the review says so in its table instead of passing them.

As built in 3.12.0, the eval check is likewise one file every review reads — `skills/sdd-flow/references/evals.md`, its §7 — with a fixed list of fifteen findings; the chart above names the main ones. The review never makes the eval run. The flow's main session does, because a review may run on a second model in a place from which no model can be reached. A case checked by rule passes only when its check holds on all three runs, so a behaviour the model shows only some of the time is a finding.

## Where the data goes

```mermaid
flowchart LR
    app("application code<br/>calls OpenTelemetry only") --> boot["bootstrap module<br/>the one file that knows<br/>a backend exists"]:::orch
    boot --> sw{"switches in the<br/>application's env file"}
    sw -- "kill switch" --> none["nothing recorded"]:::orch
    sw -- "endpoint is Opik" --> opik[("Opik")]
    sw -- "endpoint is Langfuse" --> lf[("Langfuse")]
    tests("trace run during a review") --> dump["local span file"]:::orch
    dump --> rev("sdd-flow reviewer")
    evals("eval run of record") --> opik
    opik --> you["you, and /eval-harvest"]:::stop
    lf --> you2["you"]:::stop

    classDef stop fill:#fde2e2,stroke:#c0392b,color:#000
    classDef orch fill:#eeeeee,stroke:#888888,color:#000
```

**How an `/sdd-flow` review sees what the application did.** It does not look anything up in Opik or Langfuse. The application has one special test command, the *trace run*, that runs the tests and writes a record of every call they made to a file inside the repository. The reviewer reads that file.

The trace run ignores the switches in the table below: it records everything for that one test run, even if you have turned tracing off or set it to record only a fraction of requests. So switching tracing off to save performance never breaks a review, and a review needs no network connection and no keys. It leaves two settings as it finds them, both about recorded text: the one that drops the model's inputs and outputs, and the one that adds the arguments and results of the application's own functions. An application that keeps that text out of its traces keeps it out of this file too.

| To do this | Set in the env file |
|---|---|
| Switch tracing off entirely | `OTEL_SDK_DISABLED=true` |
| Keep spans, drop LLM inputs and outputs | `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=false` |
| Record a fraction of requests | `OTEL_TRACES_SAMPLER=parentbased_traceidratio`, `OTEL_TRACES_SAMPLER_ARG=0.1` |
| Record the arguments and results of the application's own functions (off unless set) | `TRACE_FUNCTION_VALUES=all`, or a list of module names |
| Swap Opik and Langfuse | `OTEL_EXPORTER_OTLP_ENDPOINT` and `OTEL_EXPORTER_OTLP_HEADERS` |

Evals do not swap: they go to Opik only, and `/eval-harvest` works only while traces go to Opik.

## What happens at each stage

| Stage | With tracing on | With evals on | Who does it |
|---|---|---|---|
| `/observability-init` | Writes the bootstrap module, the entry-point wrapper and test, the trace run, and `SDD/OBSERVABILITY.md`; proves that a trace arrives, the kill switch, and that the test can fail | — | A skill you run, once per application |
| 0 Scope | Records whether the foundation exists | Same record | Orchestrator |
| 2.5 Design brief and gate | — | The brief states how quality will be judged; you approve it | Opus subagent, then you |
| 3a Specification | Planned call graph; each slice lists its traced nodes | Eval cases; each slice lists its evals | Sonnet subagent |
| 3c Panel | Gate settled and recorded | Gate settled and recorded | Orchestrator |
| 3d Spec review | Checks the graph and the slice lists | Checks every LLM requirement has a rule-based eval or is listed for you to accept at the final commit | A second model; an Opus subagent where none is available |
| 4a Implement | Spans for what the slice adds, nothing else | The spec's cases as a file, and their checks; the eval run on first use, from templates | Sonnet subagent |
| 4b Review | Trace run, call tree, comparison with the plan | The flow's main session makes the eval run and sends it to Opik; the review reads the results and the eval files against the spec | Orchestrator for the eval run; a second model for the review, a Sonnet subagent where none is available |
| 4e.5 Final recount | Whole graph compared after every fix has landed; every finding, low-severity ones included, is fixed before completion | Every case run again after every fix has landed, and checked; a finding is fixed before completion | Sonnet subagents for the blind count and the fixes; orchestrator for the eval run; a second model for the verification, a Sonnet subagent where none is available |
| 4f Completion | Summary filled from the final call tree. It changes no code or test: if it finds something that needs either, the flow stops and the final check runs again after you resume | Evals listed with their results, and each requirement left for you to accept with its judged scores. It changes no code or test, as with tracing on | Sonnet subagent |
| 4h Commit question | — | Fires in both modes when a requirement can only be judged; yes accepts it | You |
| `/eval-harvest` | Reads the tier's real traces from Opik; stops if the application sends them to Langfuse | Proposes failures as new cases; writes the ones you approve | A skill you run, after using the tier |

## What changes about the stops

The proposal added no stop. As built there are two new ones — the first two rows — and three existing ones change. All of it is built.

| Stop | Before | Now |
|---|---|---|
| Tracing or evals asked for and not possible (3c) — 3.8.0 for tracing, 3.12.0 for evals | Did not exist | The spec says `tracing: true` or `evals: true` and the application had no tracing foundation when the cycle started, or one of the two fields holds an invalid value. You change the field; nothing is reviewed until you do |
| Eval run could not be made (before a review) — 3.12.0 | Did not exist | With evals on, the application's model could not be reached twice in a row when the flow ran the eval cases. Nothing is reviewed until it can be; you fix the network, the key, or the provider's limit, and continue. It costs no fix round |
| Before the final commit (4h) — changed in 3.12.0 | Supervised mode only | Also in autonomous mode, when evals are on and the spec has a requirement only a judge can score. It shows each such requirement with its judged scores and where the outputs are; yes commits and accepts them |
| Final recount halt (4e.5) — changed in 3.8.0 and 3.12.0 | The final recount's verification still has open findings after 3 fix rounds, or a round made no progress | The same, with tracing and eval findings counted among them — for tracing, low-severity ones included. It also fires when completion finds something that needs code or tests changed after the final check |
| Slice fix-loop halt (4c) | A slice did not pass its review in 3 fix rounds, or a round made no progress | Unchanged — tracing and eval findings are ordinary review findings |
| Slice pause — changed in 3.12.0 | Shows the brief check line | With evals on, also shows the last line of the slice's eval run — how many rule-checked cases passed, how many judged cases there are and their lowest score — and where its results are |

## What exists after each build step

| Build step | What it ships | Which parts of this picture then work |
|---|---|---|
| 1 — **shipped in 3.7.0** | `/observability-init` and the tracing standard (`skills/observability-init/references/tracing.md`) | In "Where the data goes": application tracing, the switches, the choice of backend, and the local span file — for a Python application, outside the flow. Run on the trial application on 2026-10-07, sending to Opik; sending to Langfuse is not yet proven. Not the eval run or `/eval-harvest` |
| 2 — **shipped in 3.8.0** | Tracing in `sdd-flow`: the `tracing:` gate, the planned call graph, the implementer's tracing step, the trace check in every review and at the final recount, `trace-tree.py`. Also, in `/observability-init`: every call to the application's own functions recorded automatically, with a cap on repeats | Scenario 1 end to end, and every line starting `tracing:` in "Inside one cycle" — except the design brief, which does not mention the gate until step 3. The own-function hook was added to the trial application on 2026-10-08 by running `/observability-init` on it again (audit mode). Used to build a feature end to end on the trial application, 2026-10-09 to 2026-10-12: six slices with the gate on, the trace check run in all twenty completed flow reviews, every planned node found, no finding. Not yet exercised on a real feature: a trace-check finding and its fix, an external call, and more than one model call (the proposal's "Step 2 as built") |
| 3 — **shipped in 3.12.0** | Evals in `sdd-flow`: the `evals:` gate, the brief's decision on how quality is judged, the cases in the spec, the eval run and its templates, the flow's run before every review, the eval check in every review and at the final recount, sign-off at the final commit, the upload to Opik | Scenario 2 inside a cycle, and every line starting `evals:` in "Inside one cycle". The eval run was tried on a scratch copy of the trial application on 2026-10-12: a real run of five cases, sent to Opik and read back (record: `proposals/observability-and-evals-trial-2026-10-12.md`). **Not yet used in a cycle:** no feature has planned an eval, built one, had one reviewed, or stopped for a sign-off (the proposal's "Step 3 as built") |
| 4 — not built | `/eval-harvest` | The loop from a used tier back into the next one |
