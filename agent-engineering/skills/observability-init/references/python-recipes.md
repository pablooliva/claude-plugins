# Python recipes — what goes in each `@@PLACEHOLDER@@`

For rendering `templates/python/*.template` and `templates/OBSERVABILITY.md.template`. Use the recipe the discovery step (SKILL.md Step 2) justified. A recipe marked **proven** has run on a real application; one marked **unproven** is a starting point that Step 6 has to prove before the plan may call it done.

Rules for every fill:

- **No secret and no backend address in a rendered file.** They are committed. Backend settings live in the env file.
- **Imports of the SDK, an exporter, or an instrumentation library stay inside functions of the bootstrap module**, so importing the module costs nothing when tracing is off.
- **Leave no placeholder behind.** A placeholder with nothing to put in it is deleted together with the lines that exist only for it.
- **The templates need Python 3.10 or later.**

---

## Packages

Add them with the project's own tool (`uv add`, `poetry add`, `pip` plus the requirements file). Never hand-edit a lockfile.

| Always | Why |
|---|---|
| `opentelemetry-sdk` | The tracing library itself |
| `opentelemetry-exporter-otlp-proto-http` | Sends spans to Opik or Langfuse |

| If the application uses | Add | Line for `@@INSTRUMENTATION@@` | Status |
|---|---|---|---|
| `openai` (any OpenAI-compatible endpoint) | `opentelemetry-instrumentation-openai-v2`, and `opentelemetry-util-genai<1` | `OpenAIInstrumentor().instrument(tracer_provider=provider)` (from `opentelemetry.instrumentation.openai_v2`) | proven, 2026-10: openai 3.24, instrumentation 2.4b0, util-genai 0.4b0 |
| FastAPI with the `telemetry=` option on `FastAPI()` | nothing | nothing — see Web framework | proven, 2026-10: FastAPI 0.142 |
| FastAPI without that option | `opentelemetry-instrumentation-fastapi` | nothing — see Web framework | unproven |
| `httpx` or `requests` for calls to other systems | `opentelemetry-instrumentation-httpx` / `-requests` | `HTTPXClientInstrumentor().instrument(tracer_provider=provider)` / `RequestsInstrumentor()…` | unproven |
| a database driver, another LLM SDK, another framework | the `opentelemetry-instrumentation-*` package for it | its `…Instrumentor().instrument(tracer_provider=provider)` | unproven |

- **The pin on `opentelemetry-util-genai` is real.** Instrumentation 2.4b0 accepts any version of it, and versions from 1.0 on moved a module it imports, so an unpinned install fails at startup with `No module named 'opentelemetry.util.genai.instruments'`. Before pinning, check whether a newer instrumentation release has fixed this (install it unpinned in a scratch directory and import `opentelemetry.instrumentation.openai_v2`).
- **These packages are betas.** Whatever the table says, the import check in Step 5 and the real span in Step 6 are what count.
- **An HTTP client the model SDK uses internally needs no instrumentation.** The model call already has its span.

## `telemetry.py.template` — the bootstrap module

Goes beside the application's other modules (`src/<package>/telemetry.py`).

| Placeholder | Fill |
|---|---|
| `@@SERVICE_NAME@@` | The application's name as it should read in the backend; normally the package name |
| `@@DISTRIBUTION@@` | The name in `pyproject.toml` `[project] name`, so the version comes from the installed package |
| `@@ENV_FILE@@` | A `Path` expression for the application's one env file, relative to this module — `Path(__file__).resolve().parents[2] / ".env"` for `src/<package>/telemetry.py`. Reuse the application's own constant if it has one |
| `@@INSTRUMENTATION@@` | The import and instrument lines from the table above, indented four spaces. With nothing to instrument: `    pass` |

**Where `setup_tracing()` is called.** Once, where the application loads its configuration at startup — not at import. Pass the env file path through if the application lets a caller choose one, so that a test which supplies its own env file never reads the developer's. For FastAPI that is the lifespan function, next to the configuration load. For a command-line program it is the first line of `main()`.

**It is decided once per process.** The first call fixes the settings; later calls return at once. That is what makes it safe to call from every app instance a test suite builds.

## Web framework

**FastAPI with the `telemetry=` option** (proven). The framework traces every route itself, through the tracing library the bootstrap module sets up. Set, where the app is built:

```python
FastAPI(..., telemetry={"tracing": True, "metrics": False, "logs": False, "auto_configure": False})
```

- `auto_configure` stays `False`: with it on, the framework would read the backend variables and build an exporter itself, and the bootstrap module would no longer be the only file that knows a backend exists.
- `metrics` and `logs` stay `False`: the standard covers traces.
- The framework adds child spans of its own (`fastapi.endpoint`, `fastapi.dependencies`, `fastapi.serialization`). They are allowed.
- It records the request path and query string, never headers.
- **To take tracing off one route** (Step 6's proof): add `"exclude": lambda scope: scope.get("path") == "<path>"` to that dictionary, run the entry-point test, and take it out again.

**FastAPI without it** (unproven). The instrumentation library may be named only in the bootstrap module, so add a function there and call it where the app is built:

```python
def trace_app(app) -> None:
    """Trace every route of this app. Safe before setup_tracing(): spans start once tracing is set up."""
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    _never_capture_headers()  # this library reads the header settings when it wraps the app
    FastAPIInstrumentor.instrument_app(app)
```

To take tracing off one route: `instrument_app(app, excluded_urls="<path>")`.

**No web framework**: every entry point goes through `traced`, and is listed in a registry the entry-point test reads (below).

## `test_entry_points_traced.py.template` — the entry-point test

Goes with the application's other tests.

| Placeholder | Fill |
|---|---|
| `@@ROOT@@` | `Path(__file__).resolve().parents[1]` for `tests/<file>` |
| `@@BUILD_CLIENT@@` | The body of `_client()`, indented four spaces: build the application the way its own tests do and return a `starlette.testclient.TestClient` for it. It runs in a fresh process with no fixtures, so it does its own imports inside the function and writes any file it needs into `tempfile.mkdtemp()`. Made-up settings only: no real key, and a model address nothing listens on (`http://127.0.0.1:9/v1`) |
| `@@REQUEST_HEADERS@@` | A dict of headers that gets a bare request past anything in front of the routes (a guard that checks the content type, an origin check). `{}` when nothing is in front. If the application refuses hosts other than its own, give `TestClient` the matching `base_url` in `_client()` |
| `@@REGISTRY_TEST@@` | Nothing, when every entry point is a route. Otherwise one test per registry of other entry points (below) |

- A request does not have to succeed. It has to reach the route, so that the span names it. A 400 from the route's own validation is fine.
- A route with a typed path parameter (`{id:int}`) is not matched by the literal text the test sends. Give `_drive` a sample path for it.
- **A mounted app or a WebSocket route makes the test fail by name** (`Entry points this test cannot check yet`), because the template only knows how to send a plain request. Do not delete the check. Extend `_drive` and `_routes` for that application — a sample request under the mount, a WebSocket handshake — and show in Step 6 that the extended test fails when tracing is taken off it. Until then the plan names that entry point as outside the test.
- Under the trace run the test copies the spans it collected into the trace run's file, so its requests are in that file too.
- **An application with no web framework** drops `_client`, `HEADERS`, `_routes`, `_drive`, the route test, and the `__main__` block, and keeps only registry tests.

**A registry test**, for jobs, consumers, or commands kept in a table the application owns:

```python
def test_every_job_is_traced():
    from <package>.jobs import REGISTRY

    untraced = [name for name, fn in REGISTRY.items() if not getattr(fn, "__traced__", False)]
    assert not untraced, f"Untraced entry points: {untraced}"
```

`traced` sets `__traced__`. If entry points of some kind are in no table at all, do not invent one unasked: say in the plan that this kind is outside the test, as the standard allows, and name them in the record.

## `trace_run.py.template` — the trace run

Goes in the project's scripts folder (`scripts/trace_run.py`).

| Placeholder | Fill |
|---|---|
| `@@ROOT@@` | `Path(__file__).resolve().parents[1]` for `scripts/<file>` |
| `@@TRACE_RUN_COMMAND@@` | How to start it with the project's tool: `uv run python scripts/trace_run.py` |
| `@@TEST_ARGS@@` | Empty to run every test. To leave some out — tests that need a network or a paid service — `, "-m", "not <marker>"` |

- The span file is `.traces/spans.jsonl`. Add `.traces/` to `.gitignore`.
- A test that swaps the model client for a stand-in produces no LLM span. That is expected: the trace run shows the calls its tests really make. The LLM span is shown once, by the real request in Step 6.

## `OBSERVABILITY.md.template` — the record

Rendered to `SDD/OBSERVABILITY.md`. Create `SDD/` if the repository has none.

| Placeholder | Fill |
|---|---|
| `@@DATE@@` | Today, `YYYY-MM-DD` |
| `@@LANGUAGE@@` | `python` |
| `@@BOOTSTRAP_PATH@@`, `@@ENTRY_POINT_TEST_PATH@@` | Repository-relative paths |
| `@@TRACE_RUN_COMMAND@@`, `@@SPAN_FILE@@` | As rendered above; `.traces/spans.jsonl` |
| `@@BACKEND@@` | `Opik, project <name>`, `Langfuse`, or `none set` — never an address with credentials in it |
| `@@ENV_FILE_NAME@@` | The env file's name, e.g. `.env` |
| `@@TRACED@@` | One bullet per traced kind: what gives each its span here (the framework option, the instrumentation line, the wrapper), and any kind this application does not have |
| `@@APPLICATION_RULES@@` | Each rule of the application's own that is stricter than the standard and how it is applied; each entry-point kind outside the entry-point test. `None.` when there are none |
| `@@PROOF@@` | Step 6's results, one bullet each, including any that were not run and why |

## Backends

Settings go in the env file. Show the user the lines to add; do not write a credential into any file yourself.

**Opik** (no key on a self-hosted instance):

```
OTEL_EXPORTER_OTLP_ENDPOINT=http://<host>:5173/api/v1/private/otel
OTEL_EXPORTER_OTLP_HEADERS=projectName=<application>
```

To confirm a trace arrived, a few seconds after the process that sent it has exited:

```bash
curl -s "http://<host>:5173/api/v1/private/traces?project_name=<application>&size=1"
```

`total` counts the project's traces; the newest has `name`, `span_count`, `llm_span_count`, and `usage`. Its spans: `…/api/v1/private/spans?project_name=<application>&trace_id=<id>` — the model call has `type: "llm"`, a `model`, `usage`, and its messages under `input` and `output`. Opik drops the values recorded once for the whole process, which is why the bootstrap module also puts the name and version on the first span of each trace.

**Langfuse** (needs the project's key pair):

```
OTEL_EXPORTER_OTLP_ENDPOINT=http://<host>:3000/api/public/otel
OTEL_EXPORTER_OTLP_HEADERS=Authorization=Basic%20<base64 of public-key:secret-key>
```

Unproven as of 2026-10: no span has been sent to Langfuse from this skill. The `%20` is the standard's encoding of the space after `Basic`; if Langfuse answers 401, try a plain space. To confirm arrival: `curl -s -u <public-key>:<secret-key> "http://<host>:3000/api/public/traces?limit=1"` — run it so that the keys come from the environment and never appear in the transcript.
