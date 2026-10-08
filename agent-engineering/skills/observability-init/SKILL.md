---
name: observability-init
description: "INVOKE THIS SKILL when the user wants to give an application tracing — e.g. '/observability-init', 'add tracing to this app', 'set up observability here', 'instrument this application', 'send traces to Opik / Langfuse', 'install the tracing foundation'. Run once per application, at a moment when no `/sdd-flow` cycle is running. Inspects the repository (framework, entry points, LLM and external calls, where configuration is loaded, how the tests build the app, the application's own rules about what may be recorded), proposes a plan for the user to approve, then renders its bundled templates into one bootstrap module (which also records every call to the application's own functions, without their values, on Python 3.12 or later), an entry-point wrapper, an entry-point test, a trace run, and `SDD/OBSERVABILITY.md`. Proves the result on the application itself: a real trace arrives in the backend, the kill switch stops everything, the entry-point test fails when tracing is taken off one entry point. Applies the plugin's tracing standard (`references/tracing.md`). Python applications only for now. Never prints env values, never writes a credential into a file, never commits, builds nothing for evals."
---

# Observability Init

Installs the **tracing foundation** in an application, once, so that every request it handles leaves a record of what it called — and so that code added later is traced without anyone remembering to.

The foundation is five parts, defined in `references/tracing.md` (the plugin's tracing standard — read it before Step 2; it is the rulebook for everything below):

1. **One bootstrap module** — the only file that knows a tracing backend exists. It also records every call to the application's own functions, with no change to them.
2. **One wrapper** for entry points the framework does not see.
3. **One entry-point test** that fails when an entry point is not traced.
4. **One trace run** — a command that runs the tests and writes every span to a local file.
5. **`SDD/OBSERVABILITY.md`** — the record of where the other four live.

When it is run:

- **Once per application, ever** — not once per feature.
- **Only when no `/sdd-flow` cycle is running.** A cycle decides at its start whether tracing is on; a foundation installed halfway changes nothing until the next cycle, and edits code the cycle has not reviewed.
- **Only when there is something to wire up** — a framework and at least one entry point. A new application builds its first small tier, then runs this.

Bundled files (read by path when needed):

- `references/tracing.md` — the tracing standard
- `references/python-recipes.md` — what goes in each `@@PLACEHOLDER@@`, which packages, how each backend is set and checked
- `templates/python/telemetry.py.template` — bootstrap module and wrapper
- `templates/python/test_entry_points_traced.py.template` — entry-point test
- `templates/python/trace_run.py.template` — trace run
- `templates/OBSERVABILITY.md.template` — the record
- `scripts/check-span-file.py` — checks a span file for secret values and header attributes (tests: `python3 -m unittest discover -s scripts/tests`)

## Anti-Pattern Watchlist

1. **Printing secrets.** Reading the env file into the conversation to see which tracing settings it has. Resolution: names only (Step 2's command). Values never enter the transcript, and no credential is ever written into a file by this skill — the user adds backend lines to the env file themselves.
2. **Quietly reversing the application's own decision.** The application switched something off on purpose — framework telemetry, an access log — and has a requirement, a decision record, or a test that says so. Flipping it because the template needs it is wrong. Resolution: Step 2 looks for these; Step 3 shows each one, what changes, and which of the application's tests and documents change with it. Nothing of the kind is edited without that approval.
3. **A second file that knows the backend.** A vendor SDK import (`opik`, `langfuse`) or a vendor decorator in application code; a framework left to build its own exporter from the environment. Resolution: the bootstrap module is the only place; application code uses the OpenTelemetry API.
4. **Tests that send traces.** Calling `setup_tracing()` at import, or letting it read the developer's env file under the test suite. Once backend lines are in that file, every test run would send traces. Resolution: call it where configuration is loaded at startup, and pass the env file through when the application lets a caller choose one; Step 2 finds every test that starts the application from the repository itself, and the plan says how each is kept from sending (`references/python-recipes.md`, The application's tests).
5. **Claiming it works without looking.** Reporting "traces are sent" because no error was printed. Resolution: Step 6 reads the trace back from the backend. A check that was not run is reported as not run.
6. **Leaving the proof in.** Taking tracing off one entry point to show the test fails, and not putting it back. Resolution: Step 6 restores it and re-runs the test; Step 7's `git diff` is read for the leftover.
7. **Trusting an unproven recipe.** The instrumentation packages are betas and break between releases. Resolution: a recipe marked unproven is named as such in the plan, and only Step 5's import check and Step 6's real span make it proven.
8. **Spans everywhere.** Adding hand-written spans to functions to be thorough. Resolution: the bootstrap module already records every call to an own function. A span is written by hand only for an LLM or external call that no instrumentation covers.
9. **Building for evals.** Creating an eval directory, runner, or dataset "while we are here". Resolution: this skill writes nothing for evals.
10. **Replacing an existing foundation.** Re-rendering over a bootstrap module someone has tuned. Resolution: `SDD/OBSERVABILITY.md` present means audit mode (Step 1); changes are proposed as edits.
11. **Leftover placeholders.** Resolution: Step 5 greps for `@@`.
12. **Leaving values on.** Putting `TRACE_FUNCTION_VALUES` in the env file to prove it works, and leaving it there. Resolution: Step 6 sets it in the environment of one command only. It never goes into a file.

## When to Activate

- The user asks to add tracing or observability to an application, or to point its traces at a backend for the first time.
- The user wants an existing foundation checked against the standard.

## When NOT to Activate

- **A `/sdd-flow` cycle is running in the repository** — say so and stop; run it when the cycle is done.
- **The application is not Python** — only Python templates exist. Say so; stop.
- **The repository has no framework or no entry point yet** — nothing to wire. Build the first tier first.
- **The user only wants to change the backend or a switch** on an application that already has the foundation — that is two lines in the env file; point at the record's Switches table.
- **Evals, dashboards, alerts** — not this skill.

## Behavioral Instructions

Execute in order. Quote every path.

### Step 1: Verify context and pick the mode

```bash
git rev-parse --show-toplevel                 # fails → not a repo; stop
git status --short | head                     # not clean → say so: the diff should be this skill's alone
ls SDD/OBSERVABILITY.md 2>/dev/null           # present → audit mode
ls pyproject.toml requirements*.txt setup.py 2>/dev/null
tail -40 SDD/orchestration/progress.md 2>/dev/null
```

- **A cycle is running** when `progress.md` names a feature in progress, or its latest block is a pending `## Awaiting …`. Stop and tell the user.
- **Mode = create** when there is no `SDD/OBSERVABILITY.md`.
- **Mode = audit** when there is one. Read it and the files it names, compare them with the standard and the current templates, and make Step 3's plan a list of proposed edits. Never overwrite (Anti-Pattern 10).

### Step 2: Discover

Read `references/tracing.md` first. Then, from the repository root — none of these print env values:

```bash
# Dependencies and the tool that manages them
ls uv.lock poetry.lock requirements*.txt 2>/dev/null; sed -n '/^dependencies/,/^]/p' pyproject.toml
# Tracing settings already in the env files — names only
for f in .env .env.*; do [ -f "$f" ] && { echo "== $f"; grep -oE '^[[:space:]]*(export[[:space:]]+)?OTEL_[A-Z0-9_]+' "$f"; }; done
# Anything about tracing, telemetry or logging that the application already decided
git grep -n -i -E 'telemetry|opentelemetry|otel_|tracing|logfire|sentry|access.?log' -- ':!*.lock' | head -60
```

Find, by reading the code:

- **The framework and where the app is built**, and every **entry point**: routes, and anything the framework does not see (jobs, consumers, commands) with the table that lists them, if one exists.
- **Every LLM call and external call**, and the library each goes through.
- **The Python version the application runs on** (`.python-version`, `requires-python`) — own functions are recorded from 3.12 on — and **the directories that hold its own code**: normally the one package the bootstrap module goes into.
- **Where configuration is loaded at startup**, which env file it reads, and whether a caller can pass a different one.
- **How the tests build the application**: fixtures, stand-ins for the model, how they keep a developer's environment out, and which tests start a real server. Two kinds matter most. A test that **starts the application from the repository** — runs the documented start command, or builds the app with no env file of its own — reads the developer's real env file, and will send traces once backend lines are in it. A test that **starts a real server with an environment it builds itself** drops the trace run's variable, so its requests are missing from the trace run's file. Search for them: `git grep -n -E 'subprocess|Popen|uvicorn|fastapi (dev|run)' -- '*test*'`.
- **The application's own rules** about what may be recorded or sent out — in its spec, decision records, README, and tests. A rule stricter than the standard's capture policy overrides it. A test that asserts tracing or telemetry is off will fail once it is on.
- **Whether its installed packages work together**: in a scratch directory, never the repository, install the packages `references/python-recipes.md` names for what you found and import each instrumentation.

### Step 3: Propose the plan and get approval

One plan, in one message. Nothing is written before the user approves it.

- **Packages** to add, with any pin and its reason.
- **New files** — the four, with their paths.
- **Edits to existing files** — each one: file, the line, what it becomes, and why. This always includes the call to `setup_tracing()`, the call to `flush_tracing()` at shutdown, and the framework's tracing switch.
- **Own functions** — the directories they are recorded from, and the header reader the bootstrap module gets for the values switch (which framework, proven or not). On a Python older than 3.12: that none will be recorded, and why.
- **The application's own decisions this touches** (Anti-Pattern 2) — each rule found in Step 2, quoted with its source, and what happens to it: kept and applied (how), or changed (which requirement text, test, and document change with it). A stricter rule is applied, not argued with.
- **What will be recorded** — in plain words, each of these: which requests; that every call to one of the application's own functions is recorded with its name, file, line, timing and whether an exception left it — the first 10 calls of one function from one caller as a span each, further ones as a count on the caller's span — but never its arguments or return value unless the values switch is set, and what that costs per request (the standard's figures); that the text sent to and returned by the model goes to the backend unless the content switch is set; that a request's path **and query string** are recorded, so anything sent in the address is in the trace; and that when a call fails, **the error text is recorded**, which can repeat what the other system answered — a gateway's error body, for one. If the application has a rule against any of these, that rule is in the next item, not waved through here.
- **The application's tests** — each test found in Step 2 that would send traces or drop the trace run's variable, and the change that fixes it.
- **Backend** — which one, and the exact lines the user adds to the env file. The skill does not write them.
- **The proof** (Step 6) — what will be run, including that it makes **one real model call** and sends **one real trace** to the backend, and which checks cannot be run yet and why (no key pair for the second backend, for example).
- **Unproven recipes** in use.
- **Open questions.**

Use `AskUserQuestion` only for a real fork. Everything else is in the plan for one approval.

### Step 4: Render

Read the templates and `references/python-recipes.md`, then:

1. Add the packages with the project's own tool.
2. Write the bootstrap module, the entry-point test, and the trace run from their templates.
3. Make the approved edits: the `setup_tracing()` call and the `flush_tracing()` call at shutdown, the framework switch, `.traces/` in `.gitignore`, and the application's own tests and documents listed in the plan.

Do not write `SDD/OBSERVABILITY.md` yet — it records Step 6's results.

### Step 5: Validate statically

```bash
grep -rn '@@' <the three new files> && echo "LEFTOVER PLACEHOLDERS" || echo "no placeholders"
<run the full test suite>             # every test passes, the entry-point test among them
<the trace run command>               # exits 0 and reports a span count above zero
```

Then check the span file against the capture policy, with the script beside this file. Give it every env file Step 2 found. It prints names, never values, and exits non-zero when it finds something:

```bash
python3 "<this skill's directory>/scripts/check-span-file.py" .traces/spans.jsonl .env
```

It reports each secret-named variable whose value appears anywhere in a span — an attribute, a span name, a URL, an error message — and each attribute that carries headers. A value shorter than four characters is matched only as a whole recorded value; the script names those variables, so look at them by hand if one is a real secret.

Any failure: fix and re-run this step. A secret or a header in the span file is a defect in the wiring, never something to note and move on from.

### Step 6: Prove it on the application

The standard does not count the foundation as installed until these have been seen. Run the ones the plan listed; a check that cannot be run is reported as not run, with the reason.

1. **The entry-point test can fail.** Take tracing off one entry point (`references/python-recipes.md` says how for each framework), run the entry-point test, and confirm it fails naming that entry point. Put tracing back; confirm it passes.
2. **Own functions are recorded, and the test for it can fail** (Python 3.12 or later). Take the line `_record_own_functions(provider, env_file)` out of the bootstrap module, run the entry-point test file, and confirm `test_own_functions_are_recorded_without_values` fails. Put the line back; confirm it passes. Count the function spans one typical request made, for the record.
3. **With values on, a header is not recorded.** Start the application in a fresh process under the trace-run setting, with `TRACE_FUNCTION_VALUES=all` in that one command's environment and nowhere else. Send one request that carries a made-up value in a header of its own (`X-Probe: <made-up value>`). Count, never print: the made-up value appears 0 times in the span file, and at least one span carries an `args.` attribute. This is what proves the header reader. An application that receives no requests does not run it.
4. **A real trace arrives.** With the backend lines in the env file, send one real request through the application — the documented start command and one request, or a few lines that build the app with its real env file and call it through a test client. Stop the process the way a user would; the `flush_tracing()` call at shutdown is what sends the last spans, and this step is its proof — if the trace is missing, look there first. Then read the trace back from the backend (`references/python-recipes.md`, Backends) and confirm: the entry point is the first span, the model call is beneath it with its model, both token counts, and — unless the content switch is off — its input and output.
5. **The kill switch stops everything.** Set `OTEL_SDK_DISABLED=true` for one more request and confirm the backend's trace count did not change.
6. **The other backend, by changing two variables** — only when the user wants the application able to send to a second backend now. Change the two backend variables and nothing else, send one request, read it back from the other backend. Otherwise it is not run: say so, and record it as not run. The standard does not require it for the foundation to count as installed.
7. **The trace run** already produced its file in Step 5.

Never print a credential while doing this. Run commands so that keys come from the environment or the env file.

### Step 7: Record and report

1. Render `SDD/OBSERVABILITY.md` from its template, with Step 6's results under "Shown to work".
2. Read `git status --short` and `git diff` once: only what the plan listed has changed, and nothing from Step 6's proof is left in.
3. Report (see **Output Format**). Do not commit — suggest the command.

## Output Format

```
Tracing foundation installed (create mode)

  src/app/telemetry.py                    bootstrap module + traced wrapper
  tests/test_entry_points_traced.py       6 routes checked
  scripts/trace_run.py                    uv run python scripts/trace_run.py → .traces/spans.jsonl
  SDD/OBSERVABILITY.md                    the record

  Also changed: src/app/app.py (setup_tracing and flush_tracing calls, framework tracing on), .gitignore,
                tests/test_app.py (one test rewritten — plan item 4), README.md (one paragraph)
  Packages:     opentelemetry-sdk, opentelemetry-exporter-otlp-proto-http,
                opentelemetry-instrumentation-openai-v2, opentelemetry-util-genai<1 (pin: see recipes)

  Checks: placeholders ✓  tests 317 passed ✓  trace run 315 spans ✓  no secret or header in the span file ✓
  Proof:  entry-point test fails without tracing on POST /ask ✓
          own functions: test fails without the hook ✓  31 function spans on one POST /ask, none with a value ✓
          values on: made-up header value 0 times in the span file ✓
          trace in Opik: POST /ask → chat <model>, 348 in / 70 out tokens, messages present ✓
          kill switch: no new trace ✓
          Langfuse: NOT RUN — no second backend wanted yet

Not committed:
  git add -A && git commit -m "Add the tracing foundation"
```

- Every proof line is always shown. One that was not run says `NOT RUN` and why — never omitted.
- In audit mode, list the edits applied per file and the proposed edits the user declined.

## Examples

### GOOD — a FastAPI application that had telemetry switched off on purpose

Step 2 finds `telemetry={"tracing": False, …}` where the app is built, a requirement that nothing about a request leaves the process, a decision record saying a later tracing tool may carry request text, and a test asserting the option is off. **Plan:** turn the framework's tracing on with `auto_configure` left off; quote the requirement and the decision record side by side and say the decision record is what permits this; list the one test to rewrite (it now asserts that with no endpoint set nothing is exported) and the README sentence that becomes untrue. The user approves; render; the proof runs against Opik; Langfuse is reported as not run, because no second backend is wanted yet.

### BAD — making the tests pass by editing them unannounced

The application's test asserts telemetry is off; after rendering it fails; the test is deleted. Wrong: that test encoded a decision. **Right:** it was found in Step 2 and its change was a line in the approved plan.

### BAD — "traces are flowing"

The app started without errors with the endpoint set, so the report says tracing works. Wrong: an exporter that cannot reach its backend only logs a warning. **Right:** Step 6 reads the trace back from the backend, and checks the model call's fields.

### BAD — the vendor's own SDK

Adding `opik` to the dependencies and `@opik.track` to the route because the vendor's quick-start says so. Wrong: the application now names a backend in its own code and cannot be pointed elsewhere by an env change. **Right:** OpenTelemetry in the bootstrap module; the backend is two environment variables.

## Scope Boundary

This skill **installs and proves** an application's tracing foundation: the bootstrap module with its wrapper, the entry-point test, the trace run, and `SDD/OBSERVABILITY.md`, plus the few edits that wire them in. It inspects without printing env values, proposes a plan the user approves, renders its templates, and shows the result working on the real application. It does not commit, does not write credentials or backend addresses into any file, does not run while an `/sdd-flow` cycle is in progress, does not write spans into the application's functions, and builds nothing for evals. It does nothing inside an `/sdd-flow` cycle either: from 3.8.0 `sdd-flow` reads the record and the standard this skill leaves behind, and checks a feature's planned calls against a real run when the application has them.
