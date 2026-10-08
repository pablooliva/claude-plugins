# Tracing — shared standard

The plugin's one definition of tracing in an application: what the tracing foundation gives an application, what must be recorded, what must never be recorded, and what code added later has to do. The `observability-init` skill installs the foundation and applies this standard. Any other skill or flow that works with traces reads this file instead of restating it.

It is about the application being built. It does not cover the coding agents that build it.

Two words used throughout: a **span** is one timed record of one operation — its name, when it started and ended, whether it failed, and a set of named values called **attributes**. A **trace** is every span one request produced, arranged as a tree of which operation called which.

## The foundation

The tracing foundation is five parts. `observability-init` writes them once per application.

1. **One bootstrap module.** The only file of the application's own code that names a tracing backend, an exporter, or an instrumentation library; tests may name them too. It switches on the framework instrumentation for what the application uses (web framework, HTTP client, database driver, LLM SDK), so the common calls are traced without anyone remembering to. It also sends the spans still waiting when the application shuts down, so that the last requests before a stop are not lost. It also switches on the recording of the application's own functions (*Own functions*, below). The rest of the application uses the OpenTelemetry API — the vendor-neutral tracing interface — and nothing else.
2. **One wrapper** for entry points the framework instrumentation does not see.
3. **One entry-point test.** It lists the application's entry points from the application's own registries — the framework's route table, the job registry, the command table — never from a hand-kept list, and fails naming every entry point that is not traced. An entry point of a kind that has no registry is outside this test; whoever reviews the code has to catch it.
4. **One trace run.** A single command that runs the tests which drive real entry points and writes every span to a fresh local file that is complete before the command exits. It sends nothing to a backend, and the file is git-ignored.
5. **`SDD/OBSERVABILITY.md`**, the observability record: one row each for the language, the bootstrap module, the wrapper, the entry-point test, the trace run and the file it writes, the directories own functions are recorded from, the backend traces go to now, and the eval command (empty until the application has one). Its presence is the sign that the foundation exists.

**The foundation is not installed until it has been shown to work** on the application itself: a span sent from the application arrives in the backend; with the kill switch set nothing is sent; the trace run produces its file; the entry-point test fails when tracing is taken off one entry point, and passes again when it is put back; and, where the language version allows it, a function of the application's own shows beneath an entry point in the trace run's file with no argument and no return value on it.

## What gets a span — the three traced kinds

- **Entry point** — a place where work enters the application from outside: an HTTP route, a queue consumer, a scheduled job, a command-line command. One span per request or run.
- **LLM call** — one call the application makes to a model, through an SDK or over plain HTTP. One span per call, so a retry the application makes is a second span and a count of spans is a count of the application's calls. Retries an SDK makes on its own stay inside the one span.
- **External call** — a call that leaves the process for another system: an HTTP API, a database, a queue, a cache, an object store. Reading a local file and calling a function in the same process are not external calls.

Nobody has to give anything else a span. The application's own functions get theirs automatically (next section).

- **The HTTP request behind an LLM call belongs to that LLM call.** If the HTTP client instrumentation also records it, that span does not count as a separate external call.
- **Spans the framework instrumentation adds on its own are allowed.** The capture policy applies to them as to any span.
- **An own function is never given a span by hand.** The bootstrap module records every call to one (next section); a span written into a function is a second record of the same call.

Each kind gets its span from the first of these that gives a span meeting this standard: framework instrumentation in the bootstrap module; the wrapper, for an entry point the framework does not see; a hand-written span, for an LLM or external call that no instrumentation covers.

## Own functions — recorded automatically

The three kinds above say where a request left the application's own code. What happened inside that code is recorded too, by the bootstrap module, with no change to any function. The bootstrap module switches on the language's call-monitoring hook — in Python `sys.monitoring`, which exists from version 3.12 — and the hook opens a span each time one of the application's own functions is called. A function written next month is recorded the day it is written. That is the point: a span someone has to remember to add is the span that goes missing.

- **Own function** — a function or method defined in a file beneath one of the application's own code directories; the observability record names them. The bootstrap module itself is left out. So is everything that is not the application's: the framework, libraries, the standard library. The body of a module or a class, a lambda, and a comprehension are not functions and get no span.
- **Only inside a request that is being recorded.** A function span is made only beneath a span that already exists and is being kept. Nothing is recorded at import or at startup, and nothing for a request the sampling setting left out.
- **What its span always holds:** its name, `<module>.<qualified name>`; its timing; `code.function.name`, `code.file.path` (from the code directory down) and `code.line.number`; and its status. No argument and no return value — see *Values of own functions*.
- **Its status is error when an exception leaves the function,** with `error.type` set to the exception's class name. Never the exception's text, which can carry what a user sent. An exception the application raises on purpose and turns into an answer — a refusal that becomes a 400 — marks the function's span the same way. Read a function's status as "an exception left it", not as "the request failed"; the entry point's own status says whether it did.
- **Where it sits in the tree.** Beneath the function that called it, or beneath the framework span it was called from. A span a library opens inside a function — the LLM call, an external call — sits beneath that function's span, so the tree says which function made each call. This holds when requests run at the same time, and across `await`, generators, and the worker threads a framework hands a request to.
- **Repeated calls are capped.** A helper called in a loop would otherwise make one span per call — ten thousand for a loop over ten thousand rows. The **caller** of a call is the nearest own function above it in the trace that has a span: for a plain call, the function that made it; for a call that arrives through a library or a background task, the function that started that work. The first 10 calls of one function from one caller get a span each. Further ones get none.
- **A call without a span is still counted.** When the caller's span ends it carries two numbers for each function the cap cut short: `calls.<function>.not_recorded`, how many calls got no span, and `calls.<function>.not_recorded_failed`, how many of those ended in an exception. `<function>` is the function's span name. A function called 14 times whose last call raised reads as 10 spans, `not_recorded` 4, and `not_recorded_failed` 1. There is no timing for those calls: the caller's own span times the whole loop. A generator that is closed before it finishes has not failed.
- **What a call without a span goes on to call** sits beneath the caller instead. A span a library opens there — an LLM call — still exists and is still counted as a call. The application's own functions called from there count as the caller's calls and are capped in their turn, so every call is either a span or a number; the first ten of them are drawn as if the caller had made them.
- **What the count misses.** A failure that happens after the caller's span has ended — in a background task that outlives the function that started it — is not counted. A function with none of the application's functions above it has no caller and is not capped: one called straight from the framework, and one called by background work after the function that started that work has ended — that one still gets a span of its own, beneath the span that has ended, as long as the trace is kept. A function that calls itself is not a repeat: each call has a different caller.
- **The number is `REPEAT_CAP` in the bootstrap module.** An application that changes it says so in its observability record.
- **Its time includes the time spent recording the calls it made.** A function that makes many small calls reads slower than it is, most of all in the trace run, which writes each span to its file as the span ends. Use function timings to see where a request's time went, not to measure a small function.
- **What it costs** — measured in 2026-10 on one FastAPI application, Python 3.12, with the repeat cap at 10. The hook itself takes about 1 microsecond per call; making and sending a span takes about 25 more. With 29 function spans per request, the median request took about 0.5 ms longer and the mean request about 1 ms longer. Spans are sent in batches, and sending a batch holds the process for a few milliseconds; with seven times the spans that fell on roughly 1 request in 10 instead of 1 in 50. The cost is a fixed amount per call. It does not grow with how long the request waits for a model.
- **An application on a Python older than 3.12 has no function spans.** Its observability record says so. The rest of this standard applies to it unchanged.

## Capture policy

A span existing costs little (*What it costs*, above). Storing values on it costs more and can leak. The policy separates the two.

| Data | Policy |
|---|---|
| Span name, timing, and status (ok or error) | Always |
| Entry point: the request's path and query string | Always, as the framework instrumentation records them. A question or an id sent in the address is therefore in the trace |
| A failed entry point, LLM call, or external call: the error's type and text | Always, as the instrumentation records them. The text can repeat what the other system answered |
| LLM call: the model asked for | Always |
| LLM call: the model that answered, token counts in and out | Always when the reply reports them; left out when it does not |
| LLM call: inputs and outputs | Always, unless the content switch is off (see Switches) |
| External call: target (host, and route or operation), method, status, latency | Always. Request and response bodies are not recorded |
| Request and response headers, on any span | **Never.** Header capture stays off in every instrumentation; for OpenTelemetry's HTTP instrumentations that means the `OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_*` variables stay unset |
| The value of a secret-named environment variable | **Never** — wherever it would appear: an attribute, a span name, a URL, an error message |
| Other environment values | Allowed (the application version on every trace is one) |
| Own function: name, file, line, timing, status, and the class name of an exception that left it | Always, for the first 10 calls of one function from one caller. Never the exception's text |
| Own function: calls beyond those 10 | Counted on the caller's span — how many, and how many ended in an exception. Nothing else |
| Own function: arguments and return value | **Off.** On only for the modules the values switch names (see Switches), and then only as *Values of own functions* allows |

- **Secret-named** means the variable's name contains `KEY`, `TOKEN`, `SECRET`, `PASSWORD`, or `CREDENTIAL`, in any letter case. In `OTEL_EXPORTER_OTLP_HEADERS`, the value of each header that carries a credential (an authorization header, an API key, a token) is a secret too; a header that only names a project is not.
- **An application's own rule overrides this policy when it is stricter.** If the application's spec or a decision record forbids recording something this policy records, the application's rule holds. The bootstrap module applies it — with a switch below where one fits, by removing the value before it is recorded where none does — and the observability record says so.

## Values of own functions

With the values switch unset — the default — no argument and no return value of an own function is recorded, and the two **Never** rows above hold without exception.

The values switch turns them on, for every own function or for the modules it names, to find a fault. Each function span of those modules then carries the function's arguments as `args.<parameter>` and its return value as `output`:

| A value that is | Is recorded as |
|---|---|
| Text of 200 characters or fewer | The text |
| Longer text | Its first 200 characters, with its full length beside it in `<name>.length` |
| A whole number, a decimal number, true or false | The value |
| Bytes, a list, a tuple, a dict, a set | Its type in `<name>.type` and its size in `<name>.length`. Never its contents |
| Anything else — an object of the application's or a library's, `None` | Its class name in `<name>.type`, and nothing more |

- **The hook never asks a value to describe itself.** No `repr()`, no `str()`, and no `len()` on anything but the built-in types in the table. Any of them would run the application's own code inside the recording, and could dump everything an object holds.
- **Left out entirely:** `self` and `cls`; any parameter whose name contains `HEADER`, `COOKIE`, `AUTH`, or one of the secret words (`KEY`, `TOKEN`, `SECRET`, `PASSWORD`, `CREDENTIAL`), in any letter case; and the return value of a function whose name contains one.
- **Replaced by `[redacted]`:**
  - a text that is a header value of the request under way, contains one, or — from six characters up — is a piece cut out of one;
  - a text that is, or contains, the value of a secret-named environment variable or a credential in the backend headers;
  - a number equal to one of those values.

  Letter case is ignored. The header values come from a reader in the bootstrap module, written for the application's web framework; the observability record says which framework it reads.
- **What this matching cannot see.** With the switch on, "never" is as good as the matching above, not absolute. It does not recognise:
  - a value that was changed first — decoded, hashed, re-encoded, joined with something else;
  - a header value or a secret shorter than four characters, unless it is the whole recorded value;
  - a secret that reached the process after it started, or that sits in no secret-named variable;
  - any header at all, when the bootstrap module has no reader for the application's framework.
- **So the values switch is for finding a fault, and stays on only as long as that takes.** Name the module you are looking at in preference to `all`. Where the application takes requests and the bootstrap module has no header reader for its framework, the switch is not used.

## Attribute rules

These apply to attributes the application's own code sets. An attribute an instrumentation library writes is left as that library writes it: the GenAI message attributes below, for one, are JSON strings by their own convention.

- **Typed and flat.** A value is a string, a boolean, an integer, a decimal number, or a list of one of those. A structured value is flattened into one attribute per field worth querying. It is never stored as a JSON string, because a backend cannot filter on a field inside one.
- **Names mirror the code:** `args.<param>` for an input, `output.<field>` for a result, dotted for nested fields. For a large value, record a derived number (`args.prompt.length`) instead of the value.
- **LLM spans use OpenTelemetry's GenAI naming conventions**, so a backend can recognise them: `gen_ai.request.model`, `gen_ai.response.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, and — when content is recorded — `gen_ai.input.messages` and `gen_ai.output.messages`. A hand-written LLM span sets the same names.
- **Function spans are written by the bootstrap module's hook, under fixed names:** `code.function.name`, `code.file.path`, `code.line.number`, `error.type`; on a caller's span, `calls.<function>.not_recorded` and `calls.<function>.not_recorded_failed` (whole numbers, present only for a function the repeat cap cut short); and — with the values switch on — `args.<parameter>` and `output`, with `.type` and `.length` beside them as *Values of own functions* says. They follow the rules above: typed, flat, never a JSON string.
- **Every trace carries the application's name and version.** The bootstrap module sets them once, as the `service.name` and `service.version` of the process, and also puts both on the first span of each trace, because a backend may drop what is recorded once for the whole process.

## What makes a trace usable for evals

A trace can become an eval case later only when:

- its LLM span carries the input, the output, the model, and both token counts; and
- it carries the application version, so a result can be tied to the code that produced it.

With the content switch off, traces still show the shape of each request, but none of them can become an eval case.

## Switches

Standard OpenTelemetry environment variables, and one of this standard's own (the values switch), set in the application's one env file. The bootstrap module is responsible for those values reaching the tracing library, whatever the application does with the rest of the file. No application code outside the bootstrap module reads them.

| To do this | Set |
|---|---|
| Switch tracing off entirely — the kill switch | `OTEL_SDK_DISABLED=true`. Every tracing call does nothing; no span is created or sent |
| Keep spans, drop LLM inputs and outputs — the content switch | `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=false`. Instrumentation libraries record no LLM content unless told to, and differ in the values they accept; the bootstrap module turns recording on by default and turns `false` into whatever its library takes as off |
| Record a fraction of requests | `OTEL_TRACES_SAMPLER=parentbased_traceidratio`, `OTEL_TRACES_SAMPLER_ARG=0.1` |
| Record arguments and return values of own functions — the values switch | `TRACE_FUNCTION_VALUES=all` for every own function, or module names separated by commas (`app.billing,app.llm`) for those modules and the ones beneath them. Unset or empty: none |
| Choose the backend | `OTEL_EXPORTER_OTLP_ENDPOINT` and `OTEL_EXPORTER_OTLP_HEADERS` |

- **With none of them set:** tracing is on, LLM inputs and outputs are recorded, own functions are recorded without their arguments and return values, and every request the application starts a trace for is kept. No endpoint is set, so the bootstrap module installs no exporter and nothing is sent anywhere.
- **Swapping the backend changes those two variables and no file.** This is shown on an application the first time it needs a second backend; until then its observability record says the swap has not been shown.
- **The switches are read when the process starts.** Changing one takes effect at the next start.
- **The trace run overrides the kill switch and the sampling settings** for its one run, in a fresh process, so its span file does not depend on either. It leaves the content switch and the values switch as it finds them: an application that keeps LLM content out of its traces keeps it out of that file too.

## Adding code to a traced application

What an implementer does for the code it adds, and nothing more:

1. **A new entry point** is traced: by the framework instrumentation if the framework sees it, otherwise through the wrapper — and, where its kind has a registry, it is in the registry the entry-point test reads.
2. **A new LLM call or external call** has a span. Check by running the trace run and finding it in the span file. Only if no instrumentation produced one, add a hand-written span that follows the capture policy and the attribute rules. If no test can drive the call for real — no test instance of the other system exists — say so when handing the work over; do not fake the span.
3. **No other span is written into the code.** An own function needs none: the hook records every call to it. Name a parameter that carries a secret or a header for what it is (`api_key`, `auth_header`), so that the values rules leave it out.
4. **Nothing outside the bootstrap module names a backend, an exporter, or an instrumentation library.**
5. **The entry-point test passes and the trace run still completes.** The same test file checks that own functions are recorded and that none carries a value while the values switch is unset.

## These rules and the enforcement-site standard

"Every entry point has a span" and "no span records a header" hold on every path, which is how `sdd-flow/references/enforcement-sites.md` defines a control. The rules in this file are nevertheless **not controls** under that standard: no per-site mutation and no blind site count is owed for them.

- A control is a rule a feature's spec states. These rules are stated once for the whole application, and are checked by the application's own entry-point test and by reading the trace run's span file.
- Most tracing comes from one setting in the bootstrap module, so there is no per-path code to count or to break.
- **A spec that needs one of these rules as a real control restates it with an ID**, and then the enforcement-site standard applies to it in full. A feature that handles credentials should carry "no path records the `Authorization` header on a span" as a security requirement of its own.
