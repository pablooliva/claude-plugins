# Tracing and evals in an sdd-flow cycle — at a glance

A picture of where tracing and evals are set up, built, checked, and used in an `/sdd-flow` cycle. **It describes a proposal; none of it is implemented as of agent-engineering 3.5.2.** The proposal — `proposals/observability-and-evals-2026-10-04.md` at the repository root — is the source of truth when this picture and it disagree. As each build step ships, this file is updated to say what exists; the cycle itself is in `sdd-flow-diagram.md`, beside this file.

**How to read it.** Same conventions as `sdd-flow-diagram.md`: rounded boxes are work done by a spawned subagent or a skill, red boxes are places the flow **stops and waits for you**, grey boxes are things the orchestrator (the main conversation) or a script does. In boxes that carry both, a line starting `tracing:` applies when tracing is on and a line starting `evals:` when evals are on.

## Two scenarios

The same machinery serves two different needs, and a feature can be in the first without the second.

| | Scenario 1 — any application | Scenario 2 — the application has an LLM or an agent in it |
|---|---|---|
| What it is for | The coding agents and you can see what the application actually did when it ran, without reading the code | That, plus a way to say whether the LLM's output is any good |
| Switched on by | The application has the tracing foundation | The foundation, **and** the feature has a model call, a tool given to a model, a retrieval store feeding a model, agent-to-agent messages, or a model output that drives an action |
| The spec carries | A planned call graph; the entry points, LLM calls, and external calls in it are marked | Also the eval cases, written out, and a maximum number of model calls per request |
| The implementer adds | Spans for the entry points and external calls the feature adds | Also spans for its LLM calls, a dataset, and scorers |
| The review checks | The call tree a real run produced, against the plan | Also runs the evals and sends the results to Opik |
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

The spec can overrule the detection in either direction: `tracing:` and `evals:` each take `auto` (the default, shown above), `true`, or `false`. Asking for either with no foundation is a planning failure that tells you to run `/observability-init` first.

## Across the life of an application

Three skills, at three different moments. Only the middle one is `sdd-flow`.

```mermaid
flowchart LR
    init("/observability-init<br/>once per application<br/>bootstrap, kill switch, entry-point test") --> cycle("/sdd-flow<br/>one cycle per tier<br/>spans and evals built slice by slice")
    cycle --> use["you use the tier<br/>traces arrive in Opik or Langfuse"]:::stop
    use -- "Scenario 2,<br/>traces in Opik" --> harvest("/eval-harvest<br/>real failures become eval cases,<br/>you approve each one")
    harvest --> next("/sdd-flow --next-tier<br/>starts from your feedback<br/>and the larger dataset")
    use -- "Scenario 1,<br/>or traces in Langfuse" --> next
    next --> use

    classDef stop fill:#fde2e2,stroke:#c0392b,color:#000
```

## Inside one cycle

What tracing and evals add to each step of the cycle. Steps they do not touch are left out; the per-slice path is shown.

```mermaid
flowchart TD
    s0["Step 0 — records whether<br/>the tracing foundation exists"]:::orch --> brief("2.5a Design brief<br/>first reading of both gates<br/>evals: one Key decision, how quality is judged")
    brief --> gate["2.5b Design gate — STOP in both modes<br/>evals: you approve how quality is judged"]:::stop
    gate --> spec("3a Specification<br/>tracing: planned call graph, traced nodes marked,<br/>each slice names its nodes<br/>evals: eval cases written out,<br/>each slice names its evals")
    spec --> bind["3c — both gates settled from the finished spec<br/>and recorded in progress.md"]:::orch
    bind --> rev3("3d Spec review<br/>tracing: nodes present and assigned to slices<br/>evals: every LLM requirement has a rule-based eval,<br/>or is listed for you to accept at the final commit")
    rev3 --> impl("4a Implement one slice<br/>tracing: spans for the entry points, LLM calls,<br/>and external calls it adds<br/>evals: dataset and scorers; the first such slice<br/>also creates the eval runner")
    impl --> review("4b Slice review<br/>tracing: trace run, call tree, compare with the plan<br/>evals: eval run of record, results file, upload to Opik")
    review -- "any finding" --> fix("4c Fix, recount, re-review<br/>at most 3 rounds")
    fix --> review
    fix -- "no progress,<br/>or 3 rounds used" --> halt["STOP — slice halted<br/>an existing stop"]:::stop
    review -- "no finding" --> commit["4c.6 commit the slice"]:::orch
    commit --> pause["Slice pause<br/>evals: shows the slice's judged scores"]:::stop
    pause -- "more slices" --> impl
    pause -- "last slice done" --> crit("4d critical review of the code, 4e fix")
    crit --> final("4e.5 Final recount<br/>with either gate on, its verification always runs<br/>tracing: whole call graph compared<br/>evals: evals run again")
    final -- "any finding" --> ffix("fix, recount, verify again<br/>at most 3 rounds")
    ffix --> final
    ffix -- "no progress,<br/>or 3 rounds used" --> fhalt["STOP — final recount halt<br/>an existing stop"]:::stop
    final -- "no finding" --> done("4f Completion<br/>reads the final call tree and eval results")
    done --> q{"Is there a requirement<br/>only a judge can score?"}
    q -- "yes" --> ask["4h STOP in both modes<br/>scores and sample outputs shown<br/>yes commits and accepts"]:::stop
    q -- "no, supervised" --> ask2["4h STOP — ready to commit?<br/>as today"]:::stop
    q -- "no, autonomous" --> c4["4i commit, 4j announcement"]:::orch
    ask --> c4
    ask2 --> c4

    classDef stop fill:#fde2e2,stroke:#c0392b,color:#000
    classDef orch fill:#eeeeee,stroke:#888888,color:#000
```

In whole-feature mode the same checks run once in the code review (4b) instead of once per slice. The final recount (4e.5) and everything after it are shared by both modes.

## Inside a review: the two checks

```mermaid
flowchart TD
    subgraph T ["Tracing check — when tracing is on"]
        run("trace run<br/>the tests that drive real entry points,<br/>tracing forced on, every request kept") --> file["span file on disk"]:::orch
        file --> tree["trace-tree.py<br/>call tree per request, call counts,<br/>scan for headers and secrets"]:::orch
        tree --> cmp{"Any of these?<br/>a header or secret on a span<br/>an LLM or external call the plan does not show<br/>more LLM calls in a request than the plan allows<br/>a marked node of this slice or an earlier one that never ran,<br/>unless the spec marks it not exercised in tests<br/>a new entry point the entry-point test does not cover<br/>a structured value stored as a JSON string"}
        cmp -- "yes" --> tf["finding"]
    end
    subgraph E ["Eval check — when evals are on"]
        cov{"Does every eval in scope<br/>have cases and a scorer?"} -- "no" --> ef["finding"]
        cov -- "yes" --> ev("eval command<br/>real model calls on the spec's cases")
        ev --> hard{"Rule-based evals pass?"}
        hard -- "no" --> ef
        ev --> judged["judged scores recorded<br/>they never pass or fail anything"]:::orch
        judged --> res["results file"]:::orch
        res --> up["upload to Opik as one experiment<br/>if Opik is unreachable: a warning, the run still counts"]:::orch
    end
    tf --> loop("the review's existing fix loop")
    ef --> loop
    cmp -- "no" --> ok(["no finding from this check"])
    hard -- "yes" --> ok

    classDef orch fill:#eeeeee,stroke:#888888,color:#000
```

When both gates are on, the eval run is made under the trace run, so the LLM calls it makes show up in the call tree.

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

Reviews never read a backend. They read a local file made by the trace run, which forces tracing on and keeps every request whatever the env file says — so a review gives the same answer with the kill switch set everywhere else.

| To do this | Set in the env file |
|---|---|
| Switch tracing off entirely | `OTEL_SDK_DISABLED=true` |
| Keep spans, drop LLM inputs and outputs | `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=false` |
| Record a fraction of requests | `OTEL_TRACES_SAMPLER=parentbased_traceidratio`, `OTEL_TRACES_SAMPLER_ARG=0.1` |
| Swap Opik and Langfuse | `OTEL_EXPORTER_OTLP_ENDPOINT` and `OTEL_EXPORTER_OTLP_HEADERS` |

Evals do not swap: they go to Opik only, and `/eval-harvest` works only while traces go to Opik.

## What happens at each stage

| Stage | With tracing on | With evals on | Who does it |
|---|---|---|---|
| `/observability-init` | Writes the bootstrap module, the entry-point wrapper and test, the trace run, and `SDD/OBSERVABILITY.md`; proves the swap, the kill switch, and that the test can fail | — | A skill you run, once per application |
| 0 Scope | Records whether the foundation exists | Same record | Orchestrator |
| 2.5 Design brief and gate | — | The brief states how quality will be judged; you approve it | Opus subagent, then you |
| 3a Specification | Planned call graph; each slice lists its traced nodes | Eval cases; each slice lists its evals | Sonnet subagent |
| 3c Panel | Gate settled and recorded | Gate settled and recorded | Orchestrator |
| 3d Spec review | Checks the graph and the slice lists | Checks every LLM requirement has a rule-based eval or is listed for you to accept at the final commit | Opus subagent |
| 4a Implement | Spans for what the slice adds, nothing else | Dataset, scorers; eval runner on first use | Sonnet subagent |
| 4b Review | Trace run, call tree, comparison with the plan | Eval run of record, results file, upload | Sonnet subagent |
| 4e.5 Final recount | Whole graph compared after every fix has landed | Evals run again after every fix has landed | Sonnet subagents |
| 4f Completion | Summary filled from the final call tree | Judged requirements listed with their scores | Sonnet subagent |
| 4h Commit question | — | Fires in both modes when a requirement can only be judged; yes accepts it | You |
| `/eval-harvest` | Reads the tier's real traces from Opik; stops if the application sends them to Langfuse | Proposes failures as new cases; writes the ones you approve | A skill you run, after using the tier |

## What changes about the stops

No stop is added. Two existing ones change.

| Stop | Today | With the proposal |
|---|---|---|
| Before the final commit (4h) | Supervised mode only | Also in autonomous mode, when the spec has a requirement only a judge can score. It shows the scores and sample outputs, and yes accepts them |
| Final recount halt (4e.5) | The final recount's verification still has open findings after 3 fix rounds, or a round made no progress | The same, with tracing and eval findings counted among them — low-severity ones included |
| Slice fix-loop halt (4c) | A slice did not pass its review in 3 fix rounds, or a round made no progress | Unchanged — tracing and eval findings are ordinary review findings |
| Slice pause | Shows the brief check line | Also shows the slice's judged scores |

## What exists after each build step

| Build step | What it ships | Which parts of this picture then work |
|---|---|---|
| 1 | `/observability-init` and the tracing standard | In "Where the data goes": application tracing, the switches, the choice of backend, and the local span file — for any application, outside the flow. Not the eval run or `/eval-harvest` |
| 2 | Tracing in `sdd-flow` | Scenario 1 end to end |
| 3 | Evals in `sdd-flow` | Scenario 2 inside a cycle |
| 4 | `/eval-harvest` | The loop from a used tier back into the next one |
