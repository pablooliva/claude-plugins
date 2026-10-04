# Tracing and Evals for Applications Built with sdd-flow

**Status:** Proposal. Nothing is implemented. Revised on 2026-10-04 after five Codex review passes of earlier drafts (35 findings in all, the last two passes covering the companion picture too; each is addressed).
**Date:** 2026-10-04
**Affects:** `agent-engineering/` plugin — two new skills (`observability-init`, `eval-harvest`), one new reference file, one new script, and the `sdd-flow` skill (bodies, phase files, `SKILL.md`, `references/enforcement-sites.md`). The `sdd/` plugin is frozen at 2.2.0 and is not touched.
**Author of intent:** Pablo Oliva. Drafted with Claude.
**Tracked in:** BB Tasks, `CLAUDEPLUG-5` — one sub-task per build step (`CLAUDEPLUG-8` to `CLAUDEPLUG-11`), plus the merge (`CLAUDEPLUG-6`) and what is needed from the user first (`CLAUDEPLUG-7`). This status line is updated as each step ships.
**Companion:** `agent-engineering/docs/observability-diagram.md` — the same design as diagrams and tables, beside `sdd-flow-diagram.md`.
**Source:** the Obsidian note *Stop Reading Code, Start Understanding Systems — AI That Works* (Horthy & Gupta, 2026-07-10), and its companions *Agent Observability Signals and Metrics* and *Tracing, Observability, and Evals in AI Application Development*.

---

## Problem

`sdd-flow` produces applications whose code the human mostly does not read. The flow does run that code — unit and integration tests, browser tests against the real stack, subprocess tests for output contracts, per-site mutations — but each of those answers a question someone thought to ask. Three gaps remain.

- **Nothing records what happened inside a run.** A test says a request succeeded; it does not say the request called the model six times to get there. The note's example is a retry loop that ran past its cap because a counter was never incremented: every assertion passed, and the trace showed it at a glance. The flow keeps no record of calls made, their order, or their count, and compares nothing against the design.
- **Instrumentation that is left to the implementer decays.** The note's central claim is that opt-in tracing fails when agents write the code — one function gets a span, the next does not. `sdd-flow` has no rule about it either way; `bodies/implementation-complete.md` has a `## Monitoring & Observability` section in the summary, filled in as free text after the fact.
- **The quality of LLM output has no test.** The flow's rule is "every requirement gets a test", but a requirement such as "the summary is faithful to the source" cannot be a unit test. The eval step that once addressed this (Step 4g, removed in 3.0.0) ran after the feature shipped. For ordinary quality it created an empty LangSmith dataset and stub scorer files — its own text said it "does NOT populate the dataset" — and nothing was run or gated. (It did seed concrete abuse-case rows for agentic features; those are now covered by tests, since 3.0.0 made an uncovered abuse case a blocking review finding.)

## Proposal in one paragraph

Give every application a **tracing foundation** once, through a new user-invoked skill: one bootstrap module, a kill switch, the backend chosen by environment variables, and a test that fails when an entry point has no span. Then have `sdd-flow` use it **inside each slice**: the spec carries a planned call graph, the implementer traces what it adds, and the review compares the planned graph with the one a real run produced. For features with an LLM in them, the spec also states what "good" means as **eval cases**, the slice implements and runs them, and the results go to Opik as an experiment. After a tier has been used, a second user-invoked skill promotes real failing traces into the eval dataset. Tracing can be pointed at Opik or Langfuse without touching application code; evals use Opik only.

**What is traced is the application being built, not the coding agents.** The traces are read by the flow's reviewers and by the human; the flow's own subagent runs are already logged by the `SubagentStop` hook and are out of scope here.

---

## 1. Where each piece goes, and why

The question was whether to build this into the flow or run it as a separate step after a slice or a tier. The answer differs per piece.

| Piece | Where | Why there |
|---|---|---|
| Tracing foundation (bootstrap, kill switch, entry-point test) | **Outside the flow**, once per application — `observability-init` | It is per repository, not per feature. Inside a feature it would be a moving part built ahead of need, which the tier standard removes. |
| Spans for what a feature adds; planned call graph; review of the real call graph | **Inside the flow**, in the slice | A step after the slice would change code after its review and its blind site count; the flow's rule is that a commit comes after the review of what it contains. A step after the tier would leave every slice built without traces — which is when they are most useful. |
| Eval criteria, seed cases, scorers, the run | **Inside the flow**, in the slice | A hard eval is a test, and belongs where the other tests are written and run. |
| Growing the dataset from real failures | **Outside the flow**, after a tier has been used — `eval-harvest` | The cases do not exist until the tier has run on real inputs. The tier standard already requires a tier to be used before the next is planned, and the tier plan has a `## Feedback` section for what is learned. |

## 2. The tracing foundation — `observability-init`

A user-invoked skill, run once per application, in the same shape as `bb-worktree-init`: inspect the repository, propose a plan for approval, render bundled templates, validate. Python and TypeScript.

**What it writes into the application:**

1. **One bootstrap module** — the only file that knows a tracing backend exists. Application code calls OpenTelemetry (the vendor-neutral tracing API) and nothing else. Framework auto-instrumentation is switched on here for whatever the repository uses (web framework, HTTP client, database driver, LLM SDK), so the common calls are traced without anyone remembering to.
2. **One wrapper** for entry points the framework does not see (queue consumers, scheduled jobs, CLI commands).
3. **One test** that fails when an entry point is not traced. This is the enforcement: an implementer that forgets gets a red test, inside the flow or outside it.
4. **A trace run** — one command that runs the tests which drive real entry points, with tracing forced on, sampling forced to 100%, and every span written to a fresh local file that is flushed before the command exits. The flow's reviewers read this file, so a review needs no backend and no credentials, and gives the same answer whatever the application's env file says about sampling or the kill switch.
5. **`SDD/OBSERVABILITY.md`** — a short record of where each of the above lives (Appendix D). Its presence is how `sdd-flow` knows the foundation exists.

It writes nothing for evals. The eval directory and runner are created by the first slice that needs them (§4), so that nothing sits in the application ahead of the behaviour it serves.

**Configuration is standard OpenTelemetry environment variables, in the application's one env file.** No new vocabulary:

| To do this | Set |
|---|---|
| Switch tracing off entirely | `OTEL_SDK_DISABLED=true` — every tracing call becomes a no-op |
| Keep spans, drop LLM inputs and outputs | `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=false` |
| Trace a fraction of requests | `OTEL_TRACES_SAMPLER=parentbased_traceidratio`, `OTEL_TRACES_SAMPLER_ARG=0.1` |
| Send to Opik | `OTEL_EXPORTER_OTLP_ENDPOINT=http://192.168.100.161:5173/api/v1/private/otel`, `OTEL_EXPORTER_OTLP_HEADERS=projectName=<app>` |
| Send to Langfuse | `OTEL_EXPORTER_OTLP_ENDPOINT=http://192.168.100.132:3000/api/public/otel`, `OTEL_EXPORTER_OTLP_HEADERS=Authorization=Basic <base64 of public-key:secret-key>` |

Three steps of cost reduction are therefore available before code is touched: drop payloads, sample, off.

**The skill validates what it wrote:** it sends one span to the configured backend and confirms it arrived; repeats against the other backend; sets the kill switch and confirms nothing is sent; runs the entry-point test and the trace run; and removes tracing from one entry point to confirm the entry-point test fails, then restores it. The swap is not claimed until this has passed on a real application.

**The tracing standard** — `skills/observability-init/references/tracing.md` — is the plugin's one definition of what the foundation promises and what an implementer must do. It is owned by this skill and read by `sdd-flow`, the same arrangement as the tier standard and the OWASP catalog. It holds, from the note:

- **What gets a span — the three traced kinds:** every entry point; every LLM call; every call to an external system. Nothing else is required to have one.
- **Capture policy:** span name, timing, and status always. LLM inputs and outputs always, subject to the content switch above. External calls record target, method, status, and latency. Request and response headers never. The value of a secret-named environment variable never — one whose name contains `KEY`, `TOKEN`, `SECRET`, `PASSWORD`, or `CREDENTIAL`. (The note's rule is "environment variable values never, because secrets live there"; other environment values, such as the application version every trace carries, are allowed.)
- **Attribute rules:** typed, flat, dotted names that mirror the code (`args.<param>`, `output.<field>`); no stringified JSON; OpenTelemetry's GenAI naming conventions on LLM spans so either backend recognises model, token counts, and messages.
- **What makes a trace usable for evals:** an LLM span carries its input, output, model, and token counts, and every trace carries the application version.

## 3. The two gates

Two new spec frontmatter fields, **`tracing:`** and **`evals:`**, each `auto` (default), `true`, or `false`. Absent means `auto`. Any other value fails fast with the same error shape `delivery_mode:` uses.

| Field | Value | Foundation exists | Feature has an LLM in it | Resolves to |
|---|---|---|---|---|
| `tracing:` | `false` | — | — | off |
| | `auto` | no | — | off |
| | `auto` | yes | — | on |
| | `true` | yes | — | on |
| | `true` | no | — | planning failure: "run `/observability-init` first" |
| `evals:` | `false` | — | — | off |
| | `auto` | no | — | off |
| | `auto` | yes | no | off |
| | `auto` | yes | yes | on |
| | `true` | yes | — | on |
| | `true` | no | — | planning failure, same message |

- **"Foundation exists"** means `SDD/OBSERVABILITY.md` is present. The orchestrator checks that fixed path at Step 0 and records the answer.
- **"Has an LLM in it"** is the detection the planning body already performs to resolve `agent_security: auto` (a model call, a tool exposed to a model, a retrieval store feeding a model, inter-agent messages, a model output driving an action). One detection, three fields; each can be forced on or off without the others.
- **Resolved in two passes, like `agent_security:`.** The design-brief subagent makes the first reading from the research and the Step 0 record, because the brief needs it (§5). The planning subagent writes the fields. The orchestrator makes the binding resolution at Step 3c from the finished spec, appends `## Gates - tracing: <on|off>, evals: <on|off>` to `progress.md`, and passes exactly `on` or `off` to every later spawn. No consumer re-resolves a gate.
- **The two gates are independent.** Evals do not need tracing on.
- **A repository without the foundation behaves exactly as today.** In a repository that has it, an absent field means `auto`, so the new behaviour applies to every spec that reaches Step 3c from then on.
- **A feature already past Step 3c when this ships is left alone.** Its record in `progress.md` has no `## Gates` line, and a resumed run that finds none treats both gates as off.
- **A missing tracing standard file** is a broken install, as a missing tier standard is: halt and tell the user.

## 4. Tracing inside a slice

When `tracing` is on:

1. **The spec's `## Modules` section gains `### Planned call graph`** (Appendix A): one tree per entry point the feature adds or changes. Every node is there for design alignment — the note's "trace during design", and the application of it already written down in the note under *Applying this to my work*. Nodes of the three traced kinds are **marked** (`[entry]`, `[LLM, max N calls]`, `[external: X]`); only marked nodes are compared with a trace. An unmarked node is an ordinary function, has no span, and is never a finding.
2. **Each slice names its marked nodes.** A `SLICE-XXX` entry gains a `Traced nodes:` line listing the marked nodes that slice brings into existence. A slice is reviewed against its own nodes and those of the slices before it — never against nodes a later slice will add. The whole graph is checked once, at the end of the feature.
3. **The implementer follows the tracing standard** for what it adds: new entry points go through the wrapper, new LLM and external calls are traced, the capture policy holds. It adds no spans elsewhere.
4. **The review gains a Tracing Lens** (Appendix C), in `bodies/code-review.md` and `bodies/slice-review.md`. The reviewer runs the trace run, renders the span file with `scripts/trace-tree.py`, writes the result to the trace-tree path in its prompt, and compares it with the marked nodes in scope. Findings come from a short fixed list.
5. **Completion fills `## Monitoring & Observability` from the final trace tree** — the spans added and where to look in the backend — and the tier plan's `## Tier N` paragraph names it as what to look at when using the tier.

**`trace-tree.py` is deterministic.** It reads the span file and prints, per entry point, the parent–child tree of each trace (one trace is one request) with durations, and the minimum and maximum number of LLM and external calls seen in any single trace. A maximum-calls finding is therefore about one request, never a total across requests. It also scans every span for attributes that carry request or response headers, and for attribute values equal to the value of a secret-named environment variable (as the capture policy in §2 defines it); it reports the span and attribute name of each hit, never the value. The capture-policy check is therefore mechanical, not a reviewer's reading. The note's rule is to prefer a view derived from traces over a model's summary of the code. Matching rendered span names to planned node names stays the reviewer's judgement in this proposal; it becomes a script once naming has been tried on a real application.

**A marked node that no trace contains is a coverage finding, not a defect claim.** The trace run only shows what its tests drove. Tests that replace an external system with a stand-in will not produce that system's span. So the spec may mark a node `not exercised in tests` with a reason (no test instance of the external system exists), and the lens skips it with a note; any other missing node means no test drives it for real, which is a test gap to close.

**New artifact:** `SDD/reviews/TRACE-TREE-<SLICE-XXX|FEATURE>-[feature-name]-[YYYYMMDD].md`, written by the reviewer, read by fix subagents and completion. The orchestrator resolves the path and passes it, with the absolute path of `trace-tree.py` and the path of `SDD/OBSERVABILITY.md`, in every implementation, review, fix, continuation, and completion prompt. No body looks for any of them.

## 5. Evals inside a slice

When `evals` is on:

1. **The design brief states how quality will be judged**, as one Key decision in plain words: which behaviours are checked by rule, and which are scored by a judge and so left for the user to accept at the final commit. What "good" means is the human's call, and the brief is the document the human approves.
2. **The spec's `## Validation Strategy` gains `### Evals`** (Appendix B): `EVAL-XXX` entries, each tied to a requirement, each with its example inputs written out. Two kinds:
   - **hard** — a deterministic check on real model output (the format, a required field, a refusal, the tool that was chosen). It is a test: a failing hard eval blocks.
   - **judged** — a score from an LLM judge. It is a measurement, never a gate. The notes record judge verdicts flipping 13.6% of the time on repeated trials; a gate on that is a gate on noise.
3. **A judged eval never makes a requirement "met" on its own; a person does.** Every requirement about LLM behaviour needs at least one hard eval, **or** is a *sign-off requirement*: listed under the spec's `### Manual Verification` as accepted by the user at the commit checkpoint. The acceptor is always whoever answers that checkpoint; the spec names no one else, so there is no second person to hand off to. A requirement covered by a judged eval alone and not listed there is a spec-review finding. For a sign-off requirement:
   - **In reviews and at completion it counts as `Complete` when** it is implemented, its judged eval ran in the run of record, and the score and sample outputs are in the eval results. The review and completion bodies say so explicitly, so "all requirements demonstrably met" and "all REQ-XXX show Complete" keep one meaning.
   - **It is accepted at the commit checkpoint (4h), which then fires in both modes.** Today 4h is supervised-only. When the spec has a sign-off requirement it fires in `--auto` as well, and its message lists each such requirement with its score and the path to its sample outputs. Answering yes commits and accepts; the orchestrator appends `## Sign-off - <REQ IDs> accepted at 4h`. Answering no works as it does today. The stop's halt block (`## Awaiting Commit Approval`), its resume rule, and its diagram row already exist; only the condition under which it fires changes.
   - **A resumed session cannot skip it.** `phases/protocols.md` today sends a finished autonomous run straight to the commit (4i). That rule gains a condition: when the spec has a sign-off requirement and no `## Sign-off` line follows the completion marker, go to 4h.
   - **In per-slice mode the slices are committed before that point**, as they are today for anything 4h rejects. Each slice-boundary pause shows the slice's judged scores so the user can interrupt early.
4. **The cases are written at planning time, not by the implementer.** The enforcement-site standard exists because an implementer's own list shares its blind spots. Eval cases stated in the spec are reviewed by the spec review before any code exists.
5. **Each slice names its evals.** A `SLICE-XXX` entry gains an `Evals:` line listing the `EVAL-XXX` IDs (or case numbers) that slice must pass. A requirement a slice only partly satisfies carries only the cases that slice can pass.
6. **The slice implements them**: a dataset file and scorers under `evals/`, run through an eval command kept apart from the unit tests because it makes real model calls. The first slice with evals on creates the directory, the runner, and the command from templates whose path is in its prompt, and adds their locations to `SDD/OBSERVABILITY.md`.
7. **The review's run is the run of record.** The reviewer runs the eval command, writes `SDD/reviews/EVAL-RESULTS-<SLICE-XXX|FEATURE>-[feature-name]-[YYYYMMDD].md` (per `EVAL-XXX`: kind, cases passed, score), and checks that every eval in the slice's scope has cases and a scorer and that hard evals pass. When `tracing` is also on, the run of record is made under the trace run, so LLM nodes show in the tree; with `tracing` off the eval command runs alone.
8. **Upload to Opik happens only in the run of record.** The runner uploads when one environment variable is set; the reviewer and the final verification (§6) set it, and implementer and fixer runs do not, so Opik holds one experiment per review — named for the feature, the scope (`SLICE-XXX`, or `FEATURE` for the final verification), and the review iteration — rather than one per implementer run. The runner prints one status line. If the upload failed, the run still counts — the dataset and results are files in the repository — and the subagent that ran it appends a one-line warning to `progress.md`. The flow never halts on it.

**Evals are Opik-only (decided).** The datasets and scorers in the repository are the source of truth; Opik is where runs are compared. Moving to another backend later means rewriting the upload, not the cases.

## 6. The last check comes after the last fix

Code changes after a review has run the lens and the evals. Where the last check sits differs by path, and in both it uses a loop the flow already has.

- **Inside a slice, nothing is added.** One fix iteration is already fix → recount → diff → re-review, and a slice moves on only when its latest review reports no finding. The lens and the eval run are part of that review, so they are repeated after every slice fix, under the slice's existing cap and its existing stop (`## Awaiting Slice Resolution`).
- **At feature level, the final check joins the final recount (4e.5).** That step already runs in both delivery modes, after every fix has landed, as a loop of recount → diff → verify → fix with a cap of three rounds, a stall check, a stop (`## Awaiting Site-Count Resolution`), and a resume rule. Four changes:
  1. When either gate is on, **the verify spawn always runs** — today it is skipped when the counts match and nothing awaits acceptance. It also runs the Tracing Lens at `FEATURE` scope against the whole planned graph and the eval run of record, and writes the `FEATURE` trace tree and eval results.
  2. **Every finding it raises — HIGH, MEDIUM, or LOW — goes to the loop's fix step**, and the loop repeats until a verify pass raises none. Lens and eval findings count toward the same cap and stall check as site findings, and a loop that does not converge stops on the same block, whose wording is widened to name them.
  3. **The verification marker carries a LOW count when a gate is on**, and "no finding" means HIGH, MEDIUM, and LOW are all zero — the convention slice reviews have used since 3.5.1. Today the feature-level verdict counts only HIGH and MEDIUM, so a LOW-only result would pass; with a gate on, any non-zero count goes to the fix step, on a fresh run and on a resumed one.
  4. **A resumed session cannot skip the verify spawn.** `phases/protocols.md` today lets a matching count go straight to completion. With a gate on, that rule also requires a verification marker for the same iteration.
- **Every fix subagent leaves the entry-point test and the hard evals passing**, as it must every other test.
- **Completion (4f) runs nothing new.** It reads the final `FEATURE` trace tree and eval results from the paths in its prompt, and its readiness checklist gains two lines: the final verification raised no tracing or eval finding, and every sign-off requirement has a recorded score.

No step, stop, or kind of spawn is added. One spawn that is conditional today becomes unconditional when a gate is on, and one existing stop (4h, §5) fires in one more case.

## 7. Tracing rules and the enforcement-site standard

"Every entry point has a span" and "no span records a header" hold on every path, which is how `references/enforcement-sites.md` defines a control — and a control needs a mutation per site and a blind count. This proposal **does not treat the tracing standard's rules as controls**, and says so in the standard itself rather than leaving it implied:

- A control is a rule **the SPEC states**. The tracing rules are stated by an application-wide standard, not by a feature's spec; they are checked by the application's own entry-point test and by the Tracing Lens.
- **A spec that needs one of them as a real control states it with an ID**, and then the full standard applies to it — mutations, blind count, and all. A feature that handles credentials should carry "no path records the `Authorization` header on a span" as a `SEC-` requirement.
- The cost reason: the alternative is a manual mutation for every traced entry point in every feature, to prove something one registry test already fails on.

- The fit reason: most tracing comes from one framework setting in the bootstrap module, so there is no per-path code to count or break — and the standard itself says that breaking shared machinery proves nothing about any single site. Where per-path code does exist (the wrapper on jobs and commands), the entry-point test lists it from the application's own registry, not from the implementer's memory, which is the job the blind count does.

Two checks stand in for what the exemption gives up: the setup skill proves once that the entry-point test can fail (§2), and `trace-tree.py` scans every span for headers and secrets (§4). Two weak spots remain, and are accepted: an entry point of a kind no registry lists is caught only by the reviewer, and the header-and-secret scan sees only the spans the trace run produced.

`references/enforcement-sites.md` gains a short paragraph in §1 saying this. **Decided 2026-10-04: exempt.**

## 8. After a tier — `eval-harvest`

A user-invoked skill, run once a shipped tier has been used. It reads recent traces for the application from Opik, picks out those that failed or were flagged, shows each to the user as a candidate eval case, and writes the approved ones into the dataset file with the corrected expected result. It appends a dated line to the tier plan's `## Feedback`, which is where the next tier's cycle starts from. It adds no case without approval and edits no application code.

**It works only while the application's traces go to Opik.** If `SDD/OBSERVABILITY.md` records Langfuse as the tracing backend, the skill says so and stops. A Langfuse reader is built when an application actually runs on Langfuse.

The same skill is where coding agents get query access to traces (the note's Step 6: "which line should I jump to?"). Opik has an MCP server and a REST API; which of them to use is settled when this step is built.

---

## What this does not do

- It does not trace the flow's own subagents or measure the coding agents.
- No dashboards, alerts, online scoring of live traffic, or automated rollback. The notes already conclude that low traffic makes those measure noise.
- No relay service between applications and backends (Appendix E shows one, for when several applications need a single switch).
- No tracing of every function, and no kernel-level profiling. The default is the three traced kinds; anything deeper is switched on by hand where someone is debugging.
- It does not make evals, or `eval-harvest`, work against Langfuse.
- It does not let the flow accept a judged requirement without a person's answer at the commit checkpoint.

## Build order

Each step is shipped and used on a real application before the next is started.

1. **`observability-init` and the tracing standard** (`CLAUDEPLUG-8`). No change to `sdd-flow`. Useful alone: any application gets traces, the kill switch, and the swap. Ends with the swap validated against both backends.
2. **Tracing in `sdd-flow`** (`CLAUDEPLUG-9`) (§3, §4, §6, §7): Step 0 record, the `tracing:` gate, the planned call graph, the slice line, the implementer rule, the Tracing Lens, the final verification at 4e.5, `trace-tree.py`, the paragraph in the enforcement-site standard.
3. **Evals in `sdd-flow`** (`CLAUDEPLUG-10`) (§3, §5, §6): the `evals:` gate, the brief decision, `### Evals` in the spec, the slice line, the eval runner templates, the implementer and review rules, sign-off at 4h, the Opik upload.
4. **`eval-harvest`** (`CLAUDEPLUG-11`) (§8), with trace query access for agents.

## Costs and risks

- **Every review of a traced slice runs the trace run and reads a call tree, and the final verification does it again** — with one spawn that a clean recount skips today. More tokens and time per slice, on every slice.
- **A noisy lens is expensive**, because the flow resolves every finding. The lens compares marked nodes only and its finding list is fixed and short for that reason; if span names and planned names diverge badly in practice, the comparison will produce false findings until naming is tightened.
- **The trace run shows only what its tests drive.** External systems with no test instance are marked and skipped, so the comparison is partial for them.
- **Eval runs make real model calls** on every slice of an LLM feature — slow, and not runnable offline.
- **Seed cases are few and written before the code exists.** They show a slice is not broken; they do not show it is good. The dataset becomes meaningful only after `eval-harvest` has been run on real use.
- **Judged requirements wait for a person.** An `--auto` run of an LLM feature with a sign-off requirement now stops at the commit checkpoint, where today it would commit unattended. In per-slice mode the slices are already committed by then.
- **The Opik instance answers API requests without a key, and stays that way (decided).** Anything on the network can read and write traces, and traces will hold LLM inputs and outputs. The capture policy keeps headers and secret environment values out; it does not keep personal data out of a prompt.
- **The swap is unproven until step 1 validates it.** Both backends have the OpenTelemetry intake route; neither has been sent a span from here, and the two display LLM spans differently.
- **Tracing has a run-time cost** even when well configured. The three switches in §2 are the answer; whether `OTEL_SDK_DISABLED` behaves as documented in both language SDKs is part of step 1's validation.

## Alternatives considered

- **A separate instrumentation step after each slice or tier.** Rejected for the reasons in §1.
- **Treating the tracing rules as controls under the enforcement-site standard.** See §7.
- **Requiring a span on every node of the planned call graph.** That would let the lens compare the whole graph, at the cost of the implementer hand-tracing every interface function — the opt-in tracing the note says decays. Marked nodes are the ones a framework or the wrapper traces without anyone remembering.
- **A new panel specialist for tracing.** One more specialist on every spec, for a check the spec review can make in a few lines.
- **A relay (OpenTelemetry Collector) from the start.** One more service to run before any application needs a shared switch.
- **Making judged evals blocking by repeating them.** The notes put the number of trials needed for a 95% verdict at about eleven. Possible on a flat-rate model; left until judged scores from real use show how noisy they are here.
- **Bringing back Step 4g as it was.** See Problem.
- **A second eval library (DeepEval) alongside Opik.** The notes favour it for agent trajectory metrics. Left for step 3 to decide once the first judged metric is actually needed; hard evals need no library.

## Decided (2026-10-04)

1. Languages: Python and TypeScript.
2. Evals use Opik only. Tracing stays swappable between Opik and Langfuse.
3. Backends: Opik at `http://192.168.100.161:5173`, Langfuse at `http://192.168.100.132:3000`.
4. No relay to start; each application points at a backend through its own environment variables.
5. Opik is used without an API key. The setup skill does not ask for one, check for one, or warn about its absence.
6. A requirement that only an LLM judge can score is accepted by the user at the commit checkpoint (4h), which fires in `--auto` as well as supervised mode for a spec that has one (§5). An unattended run of such a feature waits there; it does not commit and announce on its own.
7. The tracing standard's rules are exempt from the enforcement-site standard unless a spec restates one with an ID (§7).

**Checked on 2026-10-04, by read-only requests:** Opik answers as version 2.2.88, Langfuse as 3.175.0. On both, the OpenTelemetry trace route exists (it refuses a GET with "method not allowed" rather than "not found"). Opik's API answered without credentials; Langfuse's required them.

## Open

Needed before step 1:

1. **Which application is the trial for step 1.** The notes name Currents as planning exactly this work.

Deliberately left to the build step that needs the answer:

2. **Step 3 — whether a second eval library (DeepEval) is added beside Opik**, decided when the first judged metric is needed (Alternatives considered).
3. **Step 4 — whether agents query traces through Opik's MCP server or its REST API** (§8).

## Files affected

| File | Change |
|---|---|
| `skills/observability-init/SKILL.md` + `templates/` (Python, TypeScript) | New — step 1. Eval runner templates added in step 3 |
| `skills/observability-init/references/tracing.md` | New — the tracing standard — step 1 |
| `skills/sdd-flow/SKILL.md` | Resolve **TRACING** (the standard's path) at Step 0 beside CATALOG, STANDARD, TIERS; two rows in Artifact Paths (`TRACE-TREE-*`, `EVAL-RESULTS-*`) and `SDD/OBSERVABILITY.md`; `tracing` and `evals` in the description's frontmatter list; the `--auto` argument's list of stops gains 4h-on-sign-off; one Key Principle — steps 2, 3 |
| `skills/sdd-flow/phases/setup.md` | Step 0 records TRACING and whether `SDD/OBSERVABILITY.md` exists — step 2 |
| `skills/sdd-flow/bodies/design-brief.md` | First reading of the gates; Key decision on how quality is judged — steps 2, 3 |
| `skills/sdd-flow/bodies/planning.md` | The two fields and their validation; `### Planned call graph`; `### Evals`; `Traced nodes:` and `Evals:` lines in the slice template; checklist lines — steps 2, 3 |
| `skills/sdd-flow/phases/planning.md` | Binding gate resolution at 3c and the `## Gates` line; pass TRACING to the brief, planning, review, and fix spawns — steps 2, 3 |
| `skills/sdd-flow/bodies/critical-review.md` | Planning section: marked nodes present and assigned to slices; every LLM requirement has a hard eval or is listed as a sign-off requirement — steps 2, 3 |
| `skills/sdd-flow/bodies/implementation.md`, `bodies/slice-start.md` | Follow the tracing standard for what is added; implement and run the slice's evals; create the eval runner on first use — steps 2, 3 |
| `skills/sdd-flow/bodies/code-review.md`, `bodies/slice-review.md` | Tracing Lens; eval run of record; `code-review.md`'s `site-verification-only` mode also runs both when a gate is on, and then writes a LOW count in its marker; what `Complete` means for a sign-off requirement — steps 2, 3 |
| `skills/sdd-flow/bodies/implementation-complete.md` | Two readiness-checklist lines (§6); `## Monitoring & Observability` from the final tree; what `Complete` means for a sign-off requirement — steps 2, 3 |
| `skills/sdd-flow/phases/implementation-whole-feature.md`, `phases/implementation-per-slice.md` | Pass the resolved gates, TRACING, `SDD/OBSERVABILITY.md`, the `trace-tree.py` path, and the trace-tree and eval-results paths to implementation, review, fix, and completion spawns. Whole-feature file also: 4e.5's verify spawn always runs when a gate is on, and the wording of its halt block; 4h fires in both modes when a sign-off requirement exists, and its message; the `## Sign-off` line. Per-slice file also: judged scores in the slice-boundary pause — steps 2, 3 |
| `skills/sdd-flow/phases/protocols.md` | Continuations and resumed sessions carry the same new inputs as a first spawn; resume reads the `## Gates` line, and treats a record with none as both gates off; with a gate on, a matching final count needs a verification marker before completion, and any non-zero count on that marker (LOW included) routes to the fix step; a finished autonomous run with an unsigned sign-off requirement routes to 4h, not 4i — steps 2, 3 |
| `skills/sdd-flow/references/enforcement-sites.md` | §1: the paragraph of §7 — step 2 |
| `skills/sdd-flow/scripts/trace-tree.py` + `scripts/tests/` | New — step 2 |
| `skills/eval-harvest/SKILL.md` | New — step 4 |
| `docs/observability-diagram.md` | Exists (written with this proposal, marked as not implemented); updated to say what exists as each step ships — steps 1–4 |
| `docs/sdd-flow-diagram.md` | The 4h row's condition (also in `--auto` when a sign-off requirement exists); the 4e.5 row's note on what it now also verifies — steps 2, 3 |
| `README.md`, repo `CLAUDE.md`, `plugin.json`, `marketplace.json` | Each step is a minor version (3.6.0 onward) |

---

## Appendix A — draft of `### Planned call graph` (in the spec's `## Modules`)

```markdown
### Planned call graph

One tree per entry point this feature adds or changes. Mark every node of a traced kind;
only marked nodes are compared with a trace.

handle_upload(req)                              [entry: POST /uploads]
├─ validate(req) -> UploadSpec
├─ store_blob(spec) -> BlobRef                  [external: object store]
├─ extract(blob) -> Document                    [LLM, max 1 call]
└─ index(document) -> None                      [external: vector store — not exercised in tests: no test instance]
```

And in each slice entry:

```markdown
- **Traced nodes:** handle_upload [entry], store_blob [external]
- **Evals:** EVAL-001 (cases 1–3)
```

## Appendix B — draft of `### Evals` (in the spec's `## Validation Strategy`)

```markdown
### Evals

| ID | Requirement | Behaviour checked | Kind | Result |
|---|---|---|---|---|
| EVAL-001 | REQ-004 | Extraction returns every required field | hard | passes when all fields are present and typed, on every case |
| EVAL-002 | REQ-005 | Summary is faithful to the source document | judged | score reported; REQ-005 is listed under Manual Verification, accepted by the user at the commit checkpoint |

#### EVAL-001 cases
1. [input] → [what the output must contain]
2. [input the feature must refuse] → [the refusal]
```

## Appendix C — draft of the Tracing Lens (for `bodies/code-review.md` and `bodies/slice-review.md`)

```markdown
**Tracing Lens (conditional).** Your prompt carries the resolved gate: `tracing: off` → skip, and say so
in one line. `tracing: on`:

1. Run the trace run (command in the observability record at the path in your prompt).
2. Render the span file with the `trace-tree.py` at the path in your prompt; write the output to the
   trace-tree path in your prompt. Its last section lists any header or secret found on a span.
3. Compare the tree with the **marked** nodes in scope — this slice's `Traced nodes:` and those of
   earlier slices (the whole `### Planned call graph` when `SCOPE = FEATURE`). Unmarked nodes are not compared.

| Finding | Severity |
|---|---|
| A header, or the value of a secret-named environment variable, recorded on a span (any hit in the script's scan) | HIGH |
| More LLM calls in one trace than the node's stated maximum | HIGH |
| An external or LLM call in a trace that the plan does not show | MEDIUM |
| A marked node in scope that no trace contains, and that is not marked `not exercised in tests` | MEDIUM |
| A new entry point the entry-point test does not cover | MEDIUM |
| A structured value stored as a JSON string | LOW |

A difference is resolved by changing the code or the tests, or by recording it under the spec's
deviations — never by editing the planned call graph to match.
```

## Appendix D — draft of `SDD/OBSERVABILITY.md`

```markdown
# Observability record

| What | Where |
|---|---|
| Language | python |
| Bootstrap module | src/app/telemetry.py |
| Entry-point wrapper | src/app/telemetry.py::traced |
| Entry-point test | tests/test_entry_points_traced.py |
| Trace run | `make trace-run` — writes .traces/spans.jsonl |
| Tracing backend now | Opik, project `app` |
| Eval command | — (added by the first slice with evals on) |
```

## Appendix E — a relay, for reference (not part of this proposal)

A relay is an OpenTelemetry Collector: one small service that every application sends to, and that forwards to whichever backends its configuration lists. Swapping or muting a backend is then one edit, for all applications at once. Applications still pay the cost of creating spans unless their own kill switch is set.

```yaml
receivers:
  otlp:
    protocols:
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch: {}

exporters:
  otlphttp/opik:
    endpoint: http://192.168.100.161:5173/api/v1/private/otel
  otlphttp/langfuse:
    endpoint: http://192.168.100.132:3000/api/public/otel
    headers:
      Authorization: "Basic ${env:LANGFUSE_AUTH}"

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlphttp/opik]   # swap: otlphttp/langfuse — both: list both
```

Not tested here. One known limit: Opik takes the project name from a request header, so behind a relay every application lands in one Opik project unless more routing is configured.

Documentation: [Collector overview](https://opentelemetry.io/docs/collector/), [Collector configuration](https://opentelemetry.io/docs/collector/configuration/), [Langfuse OpenTelemetry intake](https://langfuse.com/integrations/native/opentelemetry), [Opik OpenTelemetry intake](https://www.comet.com/docs/opik/tracing/opentelemetry/overview).
