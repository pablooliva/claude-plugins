# Tracing — shared standard

The plugin's one definition of tracing in an application: what the tracing foundation gives an application, what must be recorded, what must never be recorded, and what code added later has to do. The `observability-init` skill installs the foundation and applies this standard. Any other skill or flow that works with traces reads this file instead of restating it.

It is about the application being built. It does not cover the coding agents that build it.

Two words used throughout: a **span** is one timed record of one operation — its name, when it started and ended, whether it failed, and a set of named values called **attributes**. A **trace** is every span one request produced, arranged as a tree of which operation called which.

## The foundation

The tracing foundation is five parts. `observability-init` writes them once per application.

1. **One bootstrap module.** The only file of the application's own code that names a tracing backend, an exporter, or an instrumentation library; tests may name them too. It switches on the framework instrumentation for what the application uses (web framework, HTTP client, database driver, LLM SDK), so the common calls are traced without anyone remembering to. The rest of the application uses the OpenTelemetry API — the vendor-neutral tracing interface — and nothing else.
2. **One wrapper** for entry points the framework instrumentation does not see.
3. **One entry-point test.** It lists the application's entry points from the application's own registries — the framework's route table, the job registry, the command table — never from a hand-kept list, and fails naming every entry point that is not traced. An entry point of a kind that has no registry is outside this test; whoever reviews the code has to catch it.
4. **One trace run.** A single command that runs the tests which drive real entry points and writes every span to a fresh local file that is complete before the command exits. It sends nothing to a backend, and the file is git-ignored.
5. **`SDD/OBSERVABILITY.md`**, the observability record: one row each for the language, the bootstrap module, the wrapper, the entry-point test, the trace run and the file it writes, the backend traces go to now, and the eval command (empty until the application has one). Its presence is the sign that the foundation exists.

**The foundation is not installed until it has been shown to work** on the application itself: a span sent from the application arrives in the backend; with the kill switch set nothing is sent; the trace run produces its file; and the entry-point test fails when tracing is taken off one entry point, and passes again when it is put back.

## What gets a span — the three traced kinds

- **Entry point** — a place where work enters the application from outside: an HTTP route, a queue consumer, a scheduled job, a command-line command. One span per request or run.
- **LLM call** — one call the application makes to a model, through an SDK or over plain HTTP. One span per call, so a retry the application makes is a second span and a count of spans is a count of the application's calls. Retries an SDK makes on its own stay inside the one span.
- **External call** — a call that leaves the process for another system: an HTTP API, a database, a queue, a cache, an object store. Reading a local file and calling a function in the same process are not external calls.

Nothing else is required to have a span.

- **The HTTP request behind an LLM call belongs to that LLM call.** If the HTTP client instrumentation also records it, that span does not count as a separate external call.
- **Spans the framework instrumentation adds on its own are allowed.** The capture policy applies to them as to any span.
- **Spans on ordinary functions are not part of the application.** Someone debugging may add one by hand, following the attribute rules below, and takes it out before handing the work over.

Each kind gets its span from the first of these that gives a span meeting this standard: framework instrumentation in the bootstrap module; the wrapper, for an entry point the framework does not see; a hand-written span, for an LLM or external call that no instrumentation covers.

## Capture policy

A span existing is cheap. Storing values on it costs money and can leak. The policy separates the two.

| Data | Policy |
|---|---|
| Span name, timing, and status (ok or error) | Always |
| LLM call: the model asked for | Always |
| LLM call: the model that answered, token counts in and out | Always when the reply reports them; left out when it does not |
| LLM call: inputs and outputs | Always, unless the content switch is off (see Switches) |
| External call: target (host, and route or operation), method, status, latency | Always. Request and response bodies are not recorded |
| Request and response headers, on any span | **Never.** Header capture stays off in every instrumentation; for OpenTelemetry's HTTP instrumentations that means the `OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_*` variables stay unset |
| The value of a secret-named environment variable | **Never** — wherever it would appear: an attribute, a span name, a URL, an error message |
| Other environment values | Allowed (the application version on every trace is one) |
| Arguments and return values of ordinary functions | Off. Recorded only on a span someone added by hand while debugging |

- **Secret-named** means the variable's name contains `KEY`, `TOKEN`, `SECRET`, `PASSWORD`, or `CREDENTIAL`, in any letter case — and `OTEL_EXPORTER_OTLP_HEADERS`, which carries the backend's own credentials.
- **An application's own rule overrides this policy when it is stricter.** If the application's spec or a decision record forbids recording something this policy records, the application's rule holds. The bootstrap module applies it — with a switch below where one fits, by removing the value before it is recorded where none does — and the observability record says so.

## Attribute rules

These apply to attributes the application's own code sets. An attribute an instrumentation library writes is left as that library writes it: the GenAI message attributes below, for one, are JSON strings by their own convention.

- **Typed and flat.** A value is a string, a boolean, an integer, a decimal number, or a list of one of those. A structured value is flattened into one attribute per field worth querying. It is never stored as a JSON string, because a backend cannot filter on a field inside one.
- **Names mirror the code:** `args.<param>` for an input, `output.<field>` for a result, dotted for nested fields. For a large value, record a derived number (`args.prompt.length`) instead of the value.
- **LLM spans use OpenTelemetry's GenAI naming conventions**, so a backend can recognise them: `gen_ai.request.model`, `gen_ai.response.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, and — when content is recorded — `gen_ai.input.messages` and `gen_ai.output.messages`. A hand-written LLM span sets the same names.
- **Every trace carries the application's name and version.** The bootstrap module sets them once, as the `service.name` and `service.version` of the process, and also puts both on the first span of each trace, because a backend may drop what is recorded once for the whole process.

## What makes a trace usable for evals

A trace can become an eval case later only when:

- its LLM span carries the input, the output, the model, and both token counts; and
- it carries the application version, so a result can be tied to the code that produced it.

With the content switch off, traces still show the shape of each request, but none of them can become an eval case.

## Switches

Standard OpenTelemetry environment variables, set in the application's one env file. The bootstrap module is responsible for those values reaching the tracing library, whatever the application does with the rest of the file. No application code outside the bootstrap module reads them.

| To do this | Set |
|---|---|
| Switch tracing off entirely — the kill switch | `OTEL_SDK_DISABLED=true`. Every tracing call does nothing; no span is created or sent |
| Keep spans, drop LLM inputs and outputs — the content switch | `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=false`. Instrumentation libraries record no LLM content unless told to, and differ in the values they accept; the bootstrap module turns recording on by default and turns `false` into whatever its library takes as off |
| Record a fraction of requests | `OTEL_TRACES_SAMPLER=parentbased_traceidratio`, `OTEL_TRACES_SAMPLER_ARG=0.1` |
| Choose the backend | `OTEL_EXPORTER_OTLP_ENDPOINT` and `OTEL_EXPORTER_OTLP_HEADERS` |

- **With none of them set:** tracing is on, LLM inputs and outputs are recorded, and every request the application starts a trace for is kept. No endpoint is set, so the bootstrap module installs no exporter and nothing is sent anywhere.
- **Swapping the backend changes those two variables and no file.** This is shown on an application the first time it needs a second backend; until then its observability record says the swap has not been shown.
- **The switches are read when the process starts.** Changing one takes effect at the next start.
- **The trace run overrides the kill switch and the sampling settings** for its one run, in a fresh process, so its span file does not depend on either. It leaves the content switch as it finds it: an application that keeps LLM content out of its traces keeps it out of that file too.

## Adding code to a traced application

What an implementer does for the code it adds, and nothing more:

1. **A new entry point** is traced: by the framework instrumentation if the framework sees it, otherwise through the wrapper — and, where its kind has a registry, it is in the registry the entry-point test reads.
2. **A new LLM call or external call** has a span. Check by running the trace run and finding it in the span file. Only if no instrumentation produced one, add a hand-written span that follows the capture policy and the attribute rules. If no test can drive the call for real — no test instance of the other system exists — say so when handing the work over; do not fake the span.
3. **No other span is left in the code.**
4. **Nothing outside the bootstrap module names a backend, an exporter, or an instrumentation library.**
5. **The entry-point test passes and the trace run still completes.**

## These rules and the enforcement-site standard

"Every entry point has a span" and "no span records a header" hold on every path, which is how `sdd-flow/references/enforcement-sites.md` defines a control. The rules in this file are nevertheless **not controls** under that standard: no per-site mutation and no blind site count is owed for them.

- A control is a rule a feature's spec states. These rules are stated once for the whole application, and are checked by the application's own entry-point test and by reading the trace run's span file.
- Most tracing comes from one setting in the bootstrap module, so there is no per-path code to count or to break.
- **A spec that needs one of these rules as a real control restates it with an ID**, and then the enforcement-site standard applies to it in full. A feature that handles credentials should carry "no path records the `Authorization` header on a span" as a security requirement of its own.
