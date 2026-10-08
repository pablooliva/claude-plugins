"""Drives the bootstrap template's own-function hook and prints one PASS or FAIL line per check.

    python probe.py <none | all | probe_pkg.work> <directory holding the rendered template as bootstrap.py>

Run in a process of its own by test_function_hook.py: the hook stays switched on for the life of the process.
`none` leaves the values switch unset; the other two set it. Every value here is made up.
"""
import asyncio, gc, os, sys, tempfile
from collections import Counter
from pathlib import Path

here = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [here, sys.argv[2]]
mode = sys.argv[1]
os.environ.pop("TRACE_FUNCTION_VALUES", None)  # whatever the machine has set
if mode != "none":
    os.environ["TRACE_FUNCTION_VALUES"] = mode
os.environ["PROBE_API_KEY"] = "env-canary-9f3k2"
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry import trace
import probe_fw
from probe_pkg import work
import bootstrap as telemetry

provider = TracerProvider(); memory = InMemorySpanExporter(); provider.add_span_processor(SimpleSpanProcessor(memory))
env_file = Path(tempfile.mkdtemp()) / "x.env"; env_file.write_text("FILE_SECRET=file-canary-7h2\n")
def read_scope(local):
    scope = local.get("scope")
    return [v.decode("latin-1") for _, v in scope["headers"]] if type(scope) is dict and "headers" in scope else None
telemetry.OWN_DIRECTORIES = (os.path.join(here, "probe_pkg"),)
telemetry.REPEAT_CAP = 3
telemetry._header_source = lambda: (probe_fw.framework_entry.__code__, read_scope)
work.calls_back(lambda: telemetry._record_own_functions(provider, env_file))  # installed while an own function runs
state = telemetry._function_hook
tracer = provider.get_tracer("probe")
ok = True
def check(label, condition, detail=""):
    global ok
    ok = ok and bool(condition)
    print(("PASS " if condition else "FAIL ") + label + (f" [{detail}]" if detail else ""))

def spans():
    out = list(memory.get_finished_spans()); memory.clear(); return out
def tree(all_spans):
    by_id = {s.context.span_id: s for s in all_spans}
    return {s.context.span_id: (s.name, by_id[s.parent.span_id].name if s.parent and s.parent.span_id in by_id else None) for s in all_spans}
def edges(all_spans):
    return Counter(tree(all_spans).values())

with provider.get_tracer("probe").start_as_current_span("root"):
    work.calls_back(lambda: None); work.leaf(1)
_e = Counter((x.name, x.parent is not None) for x in memory.get_finished_spans()); memory.clear()
check("a function that was running when the hook went in is recorded and closed the next time",
      _e[("probe_pkg.work.calls_back", True)] == 1 and _e[("probe_pkg.work.leaf", True)] == 1 and len(state["open"]) == 0, str(dict(_e)))
with provider.get_tracer("probe").start_as_current_span("root"):
    try: work.raises(type("env-canary-9f3k2", (Exception,), {})())
    except Exception: pass
_types = [x.attributes.get("error.type") for x in memory.get_finished_spans() if x.name.endswith(".raises")]; memory.clear()
check("an exception class named like a secret value is not recorded by name, in any mode", _types == ["[redacted]"], str(len(_types)))
# outside any span: nothing recorded
work.leaf(1); check("no span outside a traced request", len(spans()) == 0)

with tracer.start_as_current_span("root"):
    work.recurse(3); work.catches(7); work.uses_generator(3); work.abandons_generator(); gc.collect()
    probe_fw.library_helper(work.leaf, 5)
s = spans(); e = edges(s)
P = "probe_pkg.work."
check("recursion is a chain of 4", e[(P+"recurse", "root")] == 1 and e[(P+"recurse", P+"recurse")] == 3)
check("exception: failing call beneath its caller, marked error", e[(P+"fails", P+"catches")] == 1 and
      [x.status.status_code.name for x in s if x.name == P+"fails"] == ["ERROR"] and
      [x.status.status_code.name for x in s if x.name == P+"catches"] == ["UNSET"])
check("after a caught exception the next call hangs off the catcher", e[(P+"leaf", P+"catches")] == 1)
check("generator: calls made between yields hang off the caller, not the generator",
      e[(P+"leaf", P+"uses_generator")] == 3 and e[(P+"leaf", P+"numbers")] == 0 and e[(P+"numbers", P+"uses_generator")] == 1)
check("abandoned generator: its span is ended, later call hangs off the caller",
      e[(P+"numbers", P+"abandons_generator")] == 1 and e[(P+"leaf", P+"abandons_generator")] == 1)
check("own function called from library code hangs off the surrounding span", e[(P+"leaf", "root")] == 1)
check("library and framework functions have no span", not any("probe_fw" in x.name for x in s))
check("every span has file and line", all(x.attributes.get("code.file.path") == "probe_pkg/work.py" and x.attributes.get("code.line.number") for x in s if x.name != "root"))
if mode == "none":
    check("no argument or result attribute", not any(k.startswith(("args.", "output")) for x in s for k in x.attributes))

async def one(i):
    with tracer.start_as_current_span("request", attributes={"rid": i}):
        return await work.a_outer(i)
async def many(n):
    return await asyncio.gather(*[one(i) for i in range(n)])
N = 300
asyncio.run(many(N)); s = spans()
by_trace = {}
for x in s: by_trace.setdefault(x.context.trace_id, []).append(x)
shapes = Counter(tuple(sorted(tree(v).values())) for v in by_trace.values())
check(f"{N} interleaved async requests: {len(by_trace)} traces, one shape", len(by_trace) == N and len(shapes) == 1, f"shapes={len(shapes)}")
shape = dict(Counter(next(iter(shapes))))
expected = {("request", None): 1, (P+"a_outer", "request"): 1, (P+"a_inner", P+"a_outer"): 1, (P+"a_leaf", P+"a_inner"): 1,
            (P+"leaf", P+"a_leaf"): 1, (P+"leaf", P+"a_inner"): 1}
check("the shape is the call chain (thread hop included)", shape == expected, str(len(shape)))
if mode != "none":
    wrong = 0
    for v in by_trace.values():
        rid = next(x.attributes["rid"] for x in v if x.name == "request")
        wrong += sum(1 for x in v if x.name != "request" and x.name != P+"leaf" and x.attributes.get("args.i") != rid)
    check("with values on, every call carries its own request's argument", wrong == 0, f"wrong={wrong}")

async def agen():
    with tracer.start_as_current_span("root"):
        return await work.a_uses_generator(3)
asyncio.run(agen()); e = edges(spans())
check("async generator: calls between yields hang off the caller", e[(P+"leaf", P+"a_uses_generator")] == 3 and e[(P+"a_numbers", P+"a_uses_generator")] == 1)

async def cancel():
    async def run():
        with tracer.start_as_current_span("root"):
            await work.a_cancelled(1)
    t = asyncio.ensure_future(run()); await asyncio.sleep(0.05); t.cancel()
    try: await t
    except asyncio.CancelledError: pass
asyncio.run(cancel()); s = spans(); e = edges(s)
check("cancelled request: both calls ended, marked with the cancellation", e[(P+"a_slow", P+"a_cancelled")] == 1 and
      all(x.attributes.get("error.type") == "CancelledError" for x in s if x.name != "root"))
async def library_inside():
    with tracer.start_as_current_span("root"):
        await work.a_calls_library(probe_fw, tracer)
asyncio.run(library_inside()); e = edges(spans())
check("a library span open across a wait stays the parent of what follows the wait",
      e[("lib.outer", P+"a_calls_library")] == 1 and e[("lib.inner", "lib.outer")] == 1 and e[(P+"leaf", "lib.outer")] == 1,
      str(sorted(k for k in e if "lib" in k[0] or "leaf" in k[0])))
with tracer.start_as_current_span("root"):
    work.uses_generator_with_span(tracer)
e = edges(spans())
check("a library span open across a generator's yield: the consumer stays outside it, the generator's later call inside it",
      e[(P+"leaf", P+"uses_generator_with_span")] == 1 and e[(P+"leaf", "lib.in_generator")] == 1,
      str(sorted(k for k in e if "leaf" in k[0])))
# The repeat cap (3 here): calls beyond it get no span, and the caller's span counts them.
NOT, FAILED = ".not_recorded", ".not_recorded_failed"
def capped(span):
    return {k[len("calls."):]: v for k, v in span.attributes.items() if k.startswith("calls.")}
with tracer.start_as_current_span("root"):
    work.loops(8, failing=(1, 5, 6)); work.loops(3)
s = spans(); e = edges(s)
big, small = [x for x in s if x.name == P+"loops"]
check("a capped loop: 3 calls recorded, the other 5 counted on the caller, 2 of them as failed",
      e[(P+"step", P+"loops")] == 6 and capped(big).get(P+"step"+NOT) == 5 and capped(big).get(P+"step"+FAILED) == 2, str(capped(big)))
check("a failure in a recorded call is on that call's own span, not in the count",
      [x.status.status_code.name for x in s if x.name == P+"step"].count("ERROR") == 1)
check("what an unrecorded call calls hangs beneath the caller and is capped there in its turn",
      e[(P+"leaf", P+"step")] == 6 and e[(P+"leaf", P+"loops")] == 3 and capped(big).get(P+"leaf"+NOT) == 2 and capped(big).get(P+"leaf"+FAILED) == 0, str(capped(big)))
check("a loop that stays within the cap carries no count", capped(small) == {}, str(capped(small)))
with tracer.start_as_current_span("root"):
    work.loops_with_library(6, tracer); work.closes_generators(6)
s = spans(); e = edges(s)
check("a library span opened by an unrecorded call hangs beneath the caller and still exists",
      e[("lib.in_step", P+"opens_library_span")] == 3 and e[("lib.in_step", P+"loops_with_library")] == 3)
closer = next(x for x in s if x.name == P+"closes_generators")
check("a generator closed early in an unrecorded call is not a failure",
      capped(closer) == {P+"numbers"+NOT: 3, P+"numbers"+FAILED: 0}, str(capped(closer)))
with tracer.start_as_current_span("root"):
    work.loops_generators_with_span(5, tracer)
e = edges(spans())
check("a generator the cap left without a span still keeps its library span away from its consumer",
      e[("consumer.mark", P+"loops_generators_with_span")] == 5 and e[("consumer.mark", "lib.in_generator")] == 0,
      str(sorted((k, v) for k, v in e.items() if k[0] == "consumer.mark")))
with tracer.start_as_current_span("root"):
    work.starts_a_trace_of_its_own(6, tracer)
s = spans(); e = edges(s)
starter = next(x for x in s if x.name == P+"starts_a_trace_of_its_own"); new_root = next(x for x in s if x.name == "new.root")
check("a function that starts a trace of its own is not the caller of what runs in that trace",
      e[(P+"leaf", "new.root")] == 6 and capped(starter) == {} and new_root.context.trace_id != starter.context.trace_id
      and all(x.context.trace_id == new_root.context.trace_id for x in s if x.name == P+"leaf"), str(capped(starter)))
async def fan_out():
    with tracer.start_as_current_span("root"):
        await work.a_fans_out(7)
asyncio.run(fan_out()); s = spans(); e = edges(s)
fan = next(x for x in s if x.name == P+"a_fans_out")
check("calls that arrive through background tasks are capped by the function that started them",
      e[(P+"a_step", P+"a_fans_out")] == 3 and capped(fan).get(P+"a_step"+NOT) == 4 and capped(fan).get(P+"a_step"+FAILED) == 0
      and e[(P+"leaf", P+"a_fans_out")] == 3 and capped(fan).get(P+"leaf"+NOT) == 1, str(capped(fan)))
async def outlives():
    started = asyncio.Event()
    with tracer.start_as_current_span("root"):
        task = await work.a_starts_background(probe_fw.background(tracer, started, work.leaf, 6))
    started.set()
    await task
asyncio.run(outlives()); s = spans(); e = edges(s)
check("background work that outlives the function that started it loses no call",
      e[(P+"leaf", "lib.background")] == 6 and capped(next(x for x in s if x.name == P+"a_starts_background")) == {},
      str(sorted((k, v) for k, v in e.items() if k[0] == P+"leaf")))
gc.collect()
check("nothing left open", len(state["open"]) == 0, f"open={len(state['open'])}")
check("no callback failed", state["failures"] == 0, f"failures={state['failures']}")

if mode != "none":
    class Config:
        def __repr__(self): return "env-canary-9f3k2"
    async def with_headers():
        scope = {"type": "http", "headers": [(b"authorization", b"Bearer header-canary-55"), (b"x-id", b"abc"), (b"host", b"127.0.0.1:8000"), (b"content-length", b"8000")]}
        async def then():
            with tracer.start_as_current_span("root"):
                work.takes_text("Bearer header-canary-55")          # the header value itself
                work.takes_text("prefix Bearer header-canary-55 x")  # text containing it
                work.takes_text("header-canary-55")                  # a part cut out of it
                work.takes_text("abc")                               # a short header value, whole
                work.takes_text("env-canary-9f3k2"); work.takes_text("see file-canary-7h2 here")
                work.takes_text("HEADER-CANARY-55"[::-1])            # a transformed value (reversed)
                work.takes_text("plain short text"); work.takes_text("x" * 5000)
                work.takes_object(Config(), [1, 2, 3], b"header-canary-55", 2**70, "ok")
                work.takes_text(8000); work.takes_text(7)
                work.named_secret("s3cr3t-value-1", {"a": "b"}, "kept"); work.read_token("minted-value-2")
        await probe_fw.framework_entry(scope, then)
    asyncio.run(with_headers()); s = spans()
    texts = [str(v) for x in s for k, v in x.attributes.items() if k.startswith(("args.", "output"))]
    joined = "\n".join(texts)
    check("header value, text containing it, a part of it, a short one: none recorded", "header-canary-55" not in joined and "abc" not in texts)
    check("secret-named env values (environment and env file): none recorded", "env-canary-9f3k2" not in joined and "file-canary-7h2" not in joined)
    numbers = [x.attributes.get("args.value") for x in s if x.name == P+"takes_text" and not isinstance(x.attributes.get("args.value"), str) or x.attributes.get("output") in (7, 8000)]
    check("a number equal to a header value is not recorded, another number is", 8000 not in numbers and 7 in numbers, str(len(numbers)))
    named = next(x for x in s if x.name == P+"named_secret").attributes; minted = next(x for x in s if x.name == P+"read_token").attributes
    check("a parameter named like a secret or a header is left out entirely, and so is the result of a function named like one",
          named.get("args.plain") == "kept" and not any("api_key" in k or "headers" in k for k in named) and "s3cr3t-value-1" not in joined
          and minted.get("args.plain") == "minted-value-2" and "output" not in minted, str(sorted(named)))
    check("a transformed header value IS recorded (known gap)", "55-YRANAC-REDAEH" in joined)
    check("short text kept, long text cut to the limit with its length", "plain short text" in texts and
          any(x.attributes.get("args.value.length") == 5000 and len(x.attributes["args.value"]) == 200 for x in s))
    with tracer.start_as_current_span("root"):
        work.takes_text(type("env-canary-9f3k2", (), {})())
    named_class = [x.attributes for x in spans() if x.name == P+"takes_text"]
    check("a class named like a secret value is not recorded by name",
          len(named_class) == 1 and named_class[0].get("args.value.type") == "[redacted]", str(len(named_class)))
    obj = next(x for x in s if x.name == P+"takes_object").attributes
    check("objects as type, containers as type and size, never dumped",
          obj.get("args.config.type") == "Config" and obj.get("args.items.type") == "list" and obj.get("args.items.length") == 3
          and obj.get("args.blob.type") == "bytes" and obj.get("args.big.type") == "int" and obj.get("args.text") == "ok"
          and obj.get("output.type") == "dict" and obj.get("output.length") == 1 and "args.config" not in obj)
print("ALL PASS" if ok else "SOME FAILED", "| mode", mode)
