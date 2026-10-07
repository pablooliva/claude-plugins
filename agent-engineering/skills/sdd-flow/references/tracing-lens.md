# Tracing Lens — a real run compared with the planned call graph

The one definition of how an `sdd-flow` review checks what a feature really did when it ran. Three reviews run it, each at the scope its prompt gives: the per-slice review (`bodies/slice-review.md`), the whole-feature code review (`bodies/code-review.md`), and the final verification at Step 4e.5. They read this file instead of restating it.

It runs only when your prompt carries the line `tracing: on`. With `tracing: off`, or no such line, do not run it: write the one line `Tracing lens skipped — tracing: off` in the review and move on.

It is a comparison, not a design review. Whether the planned call graph is a good design was settled when the spec was reviewed; here the graph is the reference and the trace is what is checked against it.

## Inputs — all from your prompt

| Name | What it is |
|---|---|
| `SCOPE` | `SLICE-XXX` or `FEATURE` |
| the SPEC | holds `### Planned call graph` and, in per-slice mode, each slice's `Traced nodes:` line |
| **TRACING** | the tracing standard — the three traced kinds, the capture policy, the attribute rules |
| **OBS_RECORD** | the application's observability record, `SDD/OBSERVABILITY.md`: the trace run command, the span file it writes, the env file the switches are set in, the entry-point test |
| **TRACE_TREE_SCRIPT** | absolute path of `scripts/trace-tree.py` |
| **TRACE_TREE** | the path you write the rendered tree to |

If any of them is missing from your prompt, or OBS_RECORD cannot be read, return a failure to the orchestrator naming it. Do not look for a substitute.

## 1. Produce the tree

1. **Run the trace run** — the command OBS_RECORD gives, from the repository root, after the test suite has passed. It runs the tests that drive real entry points and writes every span to the span file OBS_RECORD names.
2. **Render it:** `python3 <TRACE_TREE_SCRIPT> <span file> <env file> --out <TRACE_TREE>`. The env file is the one OBS_RECORD's *Switches* section names; leave the argument out if that file does not exist. The command prints one `Result:` line; the document is at TRACE_TREE.
3. **Read the exit status.** `0` — rendered, nothing in the capture-policy scan. `1` — rendered, and the scan found something (step 4 below). `2`, or a trace run that fails or leaves no fresh span file — raise the HIGH finding *the trace run cannot be read* with the message the command printed, write no comparison, and finish the lens there. Never read the span file by hand in place of the script, and never paste any part of it into the review: it can hold what users typed.

The tree groups requests by entry point and gives, per entry point, the fewest and the most LLM calls and external calls seen in any one request, and every external target seen — those lines cover every request. It draws each distinct tree of calls once, as a *shape*, heaviest first: the shapes with the most LLM calls, then the most external calls. **At most ten shapes are drawn per entry point.** When the tree says more were not shown, none of them has more LLM calls than the last one drawn, nor as many LLM calls and more external calls; an undrawn shape can still have more external calls than a drawn one with more LLM calls, which is why external calls are compared on the *External targets seen* line and the per-request counts, not on the shapes. Say in the review how many shapes were not drawn.

## 2. The nodes in scope

Only **marked** nodes of `### Planned call graph` are compared: `[entry: …]`, `[LLM, max N calls]`, `[external: X]`. An unmarked node is an ordinary function, has no span, and is never a finding.

- **`SCOPE = SLICE-XXX`:** the marked nodes on this slice's `Traced nodes:` line and on those of every slice before it in `## Delivery Slices`. Never a later slice's: it has not been built.
- **`SCOPE = FEATURE`:** every marked node in the graph.
- A node marked **`not exercised in tests`** is skipped. List it with its reason; it is not a finding.

An entry point the tree shows and the planned graph does not name — a route the application already had, the framework's own pages, requests no route matched — is outside the comparison.

## 3. Compare, one rule per kind

| Kind | Matched by | Seen when |
|---|---|---|
| `[entry: …]` | **Name, exactly.** The text after `entry:` is an entry-point heading in the tree (`## POST /uploads`, `## app.jobs.nightly_digest`) | that heading exists with at least one request |
| `[LLM, max N calls]` | **Count beneath its entry point.** An LLM span is named for its operation and model, never for the function that made the call, so it cannot be matched by name | see *Which LLM node ran* below |
| `[external: X]` | **Target.** `X` against the `[external: …]` marks in that entry point's shapes and its *External targets seen* line: the same database or message system, or the same host. Where the mark names a setting, compare with the host that setting holds | that target appears beneath that entry point |

**Which LLM node ran.** An `[LLM]` span does not say which planned node made it, so a verdict about one node needs proof about that node. The **possible producers** of an `[LLM]` span beneath an entry point are the places in the code beneath that entry point that call a model (read the code to tell): the in-scope LLM nodes; a later slice's node, only when it was built early; and any model call the planned tree does not show. That last kind is the *call the plan does not show* finding as soon as you find it in the code, whether or not the trace run drove it.

- **`seen`** — the node is the only possible producer and some shape of the entry point shows an `[LLM]` span; or some shape shows more `[LLM]` spans than the *other* possible producers could have made between them (the sum of their maxima); or a shape puts the spans beneath different steps that match where the plan puts the nodes.
- **Not shown, every node** — no request of the entry point shows an `[LLM]` span at all. Each in-scope LLM node of that entry point is the *marked node not shown* finding.
- **Not shown, some node on a path** — take the in-scope LLM nodes the plan makes **unconditional** for the entry point: every request that runs to the end calls each of them, with no branch, cache, or condition around any. If no request of the entry point shows at least that many `[LLM]` spans, no request ran them all, and the count does not say which is missing. Nodes behind a branch, a cache, or a condition are left out of this count. Raise **one** *marked node not shown* finding for the path, naming its nodes and the shortfall; in the table each of them is `not distinguishable by count` unless it is `seen` by the rule above.
- **Otherwise** — `not distinguishable by count`: the spans could be this node, or another node and its retry. It is not a finding and it is not `seen`. Write it in the table with the test in the trace run that is meant to drive the node, so the limit of this check is on the page instead of hidden behind a pass. Never give `seen` on the strength of a test alone: a test can drive a call that has no span.

Then read four more lines of the tree, per in-scope entry point:

- **`LLM calls in one request: … most M`.** The ceiling is the sum of `max N` over the in-scope LLM nodes of that entry point. `M` above the ceiling is a finding (table below). This is a count in one request — never add requests together.
- **A call the plan does not show.** An `[LLM]` span, or an external target, beneath an in-scope entry point that no marked node of that entry point's planned tree accounts for — judged against the whole planned tree, not only the nodes in scope, so a later slice's call that arrived early is not raised here.
- **`Reached from beneath an LLM call`.** Each target there was taken as the model call's own request and not counted. That is right when it is the model provider's host. Any other system there is an external call hiding under a model call: compare it with the plan as an external call.
- **`Spans in no request`** (in the tree's notes). The test's own client above a route is expected. A span listed there with the mark `[LLM]` is a model call made outside any entry point — nothing in the plan can account for it. Other spans there are listed in the review and are not findings.

Framework spans (`fastapi.endpoint` and the like) and every other unmarked span are ignored. Durations are not compared.

## 4. Capture policy and code

- **Every hit in the tree's `## Capture-policy scan` is a finding:** a secret-named environment variable whose value was recorded, or an attribute carrying headers. Name it as the tree names it. Never write a value.
- A variable listed under *Matched as whole values only* was checked less strictly because its value is very short. Note it in the review; it is not a finding.
- **Every new entry point is traced, and the entry-point test covers the ones it can.** For each in-scope `[entry]` node: a route the framework registers is in the route table the entry-point test reads (OBS_RECORD names the test). A job, a consumer, or a command goes through the wrapper OBS_RECORD names — and, where the application keeps a registry of that kind, is in the registry the test reads. A kind with no registry is outside that test by the standard's own terms: confirm by reading the code that it goes through the wrapper, and say in the review that the test cannot cover it. That is not a finding.
- **Read the code the scope changed for what it does with tracing.** Search it for the tracing API, and compare every span it sets by hand with TRACING's *Adding code to a traced application* and *Attribute rules*. Then search the same files — leaving out the bootstrap module OBS_RECORD names, and the tests — for an import or a mention of a tracing backend, an exporter, or an instrumentation library: only the bootstrap module may name one.

## 5. Findings — the whole list

A finding comes from this table or it is not a Tracing Lens finding.

| Finding | Severity |
|---|---|
| The trace run cannot be read: it fails, leaves no fresh span file, or the script exits 2 | HIGH |
| A header, or the value of a secret-named environment variable, recorded on a span (any hit in the scan) | HIGH |
| More LLM calls in one request than the ceiling of its entry point | HIGH |
| An LLM or external call beneath an in-scope entry point that the planned tree does not show — including another system reached from beneath an LLM call, and a span marked `[LLM]` in no request | MEDIUM |
| A marked node in scope that the tree does not show, and that is not marked `not exercised in tests`. For LLM nodes, only as *Which LLM node ran* proves it: an entry point with no LLM span at all (one finding per node), or a path with fewer LLM calls than nodes (one finding for the path) | MEDIUM |
| A new entry point that is not traced, or that is of a kind the application keeps a registry for and is missing from the registry the entry-point test reads | MEDIUM |
| In the application's own code: a structured value stored on a span as a JSON string; a hand-written span on something that is not an entry point, an LLM call, or an external call; a backend, exporter, or instrumentation library named outside the bootstrap module. (Attributes an instrumentation library writes are left as it writes them) | LOW |

A marked node the tree does not show is a statement about the tests, not a claim that the code is wrong: the trace run shows only what its tests drove for real. The usual fix is a test that drives the call, not a change to the call.

## 6. How a finding is resolved

- **By changing the code or the tests.**
- **A MEDIUM difference between plan and trace may instead be recorded** under `### Implementation Deviations` in the IMPLEMENTATION-PLAN, with the reason the plan could not be followed. A difference recorded there before your review is listed in the review as a recorded deviation and is not raised again.
- **A HIGH is never resolved by recording it.** A leaked header or secret is removed; a request that makes more LLM calls than its ceiling is fixed.
- **Never by editing `### Planned call graph`, a `Traced nodes:` line, or the spec's `tracing:` field to match what ran.**

## 7. What goes in the review document

A `## Tracing Lens` section:

```markdown
## Tracing Lens

**Trace tree:** <TRACE_TREE path> — `Result:` line verbatim
**Scope:** <SLICE-XXX | FEATURE> — <n> marked node(s) compared, <n> skipped as `not exercised in tests`, <n> `not distinguishable by count`

| Node | Kind | Planned | In the tree | Verdict |
|------|------|---------|-------------|---------|
| handle_upload | entry | POST /uploads | `## POST /uploads`, 14 requests | seen |
| extract | LLM | max 1 call | the only LLM node under `POST /uploads`; most 1 in one request | seen, within ceiling |
| classify | LLM | max 1 call | `## POST /digest`: most 2 in one request, and `summarise` (max 2) could have made both | not distinguishable by count — meant to be driven by `test_digest_classifies` |
| index | external | qdrant | — | skipped: no test instance |

**Recorded deviations:** [each plan-versus-trace difference already under `### Implementation Deviations`, or `None.`]
**Spans in no request:** [as the tree's notes list them, or `None.`]
**Shapes not drawn:** [per entry point, how many the tree says it did not show, or `None.`]

[Each finding, numbered with the review's other findings: severity, the row of the findings table it comes from, the node or attribute, and the fix.]
```

Lens findings are ordinary review findings: they count in the review's verdict and its progress marker like any other, and a HIGH rejects.
