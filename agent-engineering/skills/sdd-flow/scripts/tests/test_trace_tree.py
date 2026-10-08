import contextlib
import importlib.util
import io
import json
import os
import random
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_spec = importlib.util.spec_from_file_location("trace_tree", Path(__file__).resolve().parents[1] / "trace-tree.py")
trace_tree = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(trace_tree)


class Spans:
    """Builds span-file lines; every span gets its own id and a start time in the order it was added."""

    def __init__(self):
        self.lines = []
        self.count = 0

    def add(self, name, parent=None, kind="INTERNAL", trace="t1", attributes=None, error=False, took=5, parent_id=None):
        self.count += 1
        span_id = f"0x{self.count:016x}"
        self.lines.append(json.dumps({
            "name": name,
            "context": {"trace_id": trace, "span_id": span_id},
            "kind": f"SpanKind.{kind}",
            "parent_id": parent_id or parent,
            "start_time": f"2026-10-07T09:00:{self.count:02d}.000000Z",
            "end_time": f"2026-10-07T09:00:{self.count:02d}.{took:03d}000Z",
            "status": {"status_code": "ERROR" if error else "UNSET"},
            "attributes": attributes or {},
            "events": [],
        }))
        return span_id

    def route(self, name="POST /ask", trace="t1", status=200, **more):
        method, _, path = name.partition(" ")
        return self.add(name, kind="SERVER", trace=trace, attributes={
            "http.request.method": method, "http.route": path, "http.response.status_code": status}, **more)

    def llm(self, parent, trace="t1", operation="chat", **more):
        return self.add(f"{operation} model-x", parent, kind="CLIENT", trace=trace, attributes={
            "gen_ai.operation.name": operation, "gen_ai.request.model": "model-x"}, **more)


def run(lines, *env_files, environment=None, out=None):
    """(exit status, stdout, stderr) of the script on a span file holding `lines`."""
    with tempfile.TemporaryDirectory() as folder:
        span_file = Path(folder) / "spans.jsonl"
        span_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        argv = ["trace-tree.py", str(span_file), *env_files] + (["--out", out] if out else [])
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.dict(os.environ, environment or {}, clear=True), \
                contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = trace_tree.main(argv)
        return status, stdout.getvalue(), stderr.getvalue()


def section(document, heading):
    """The lines of one `## ` section."""
    lines = document.splitlines()
    start = lines.index(heading)
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return lines[start:end]


class TreeTest(unittest.TestCase):
    def test_a_route_with_a_model_call_is_drawn_as_a_tree_with_its_marks(self):
        spans = Spans()
        route = spans.route()
        spans.add("fastapi.dependencies", route)
        endpoint = spans.add("fastapi.endpoint", route)
        spans.llm(endpoint)
        spans.add("fastapi.serialization", route)
        status, document, _ = run(spans.lines)
        self.assertEqual(status, 0)
        tree = [re.split(r"\s{2,}(?=\[|\d)", line)[0] for line in section(document, "## POST /ask")
                if line[:1] in ("P", "├", "│", "└")]
        self.assertEqual(tree, ["POST /ask", "├─ fastapi.dependencies", "├─ fastapi.endpoint", "│  └─ chat model-x",
                                "└─ fastapi.serialization"])
        self.assertRegex(document, r"POST /ask +\[entry\]")
        self.assertRegex(document, r"chat model-x +\[LLM\]")
        self.assertIn("### Shape 1 of 1 — 1 request · 1 LLM call, 0 external calls · HTTP status 200 ×1", document)

    def test_requests_with_identical_trees_are_shown_once_with_their_count_and_duration_range(self):
        spans = Spans()
        for trace, took in (("t1", 5), ("t2", 40), ("t3", 12)):
            route = spans.route(trace=trace, took=took)
            spans.add("fastapi.endpoint", route, trace=trace)
        _, document, _ = run(spans.lines)
        self.assertIn("- Shapes: 1", document)
        self.assertIn("### Shape 1 of 1 — 3 requests", document)
        self.assertRegex(document, r"POST /ask +\[entry\] +5\.0–40 ms")

    def test_call_counts_are_per_request_never_a_total(self):
        spans = Spans()
        for trace, calls in (("t1", 1), ("t2", 3), ("t3", 0)):
            route = spans.route(trace=trace)
            for _ in range(calls):
                spans.llm(route, trace=trace)
        _, document, _ = run(spans.lines)
        self.assertIn("- LLM calls in one request: fewest 0, most 3", document)
        self.assertIn("| POST /ask | 3 | 0–3 | 0 | 0 | 3 |", document)
        self.assertIn("most LLM calls in one request 3 (POST /ask)", document.splitlines()[2])

    def test_the_shape_with_the_most_model_calls_comes_first(self):
        spans = Spans()
        for trace in ("t1", "t2", "t3"):
            spans.route(trace=trace)
        heavy = spans.route(trace="t4")
        spans.llm(heavy, trace="t4")
        _, document, _ = run(spans.lines)
        self.assertIn("### Shape 1 of 2 — 1 request · 1 LLM call", document)
        self.assertIn("### Shape 2 of 2 — 3 requests · 0 LLM calls", document)

    def test_an_error_is_marked_on_the_span_that_failed_and_counted_on_the_entry_point(self):
        spans = Spans()
        route = spans.route(status=502, error=True)
        spans.llm(route, error=True)
        _, document, _ = run(spans.lines)
        self.assertIn("- Requests: 1, 1 ended in error", document)
        self.assertRegex(document, r"chat model-x +\[LLM\] error")

    def test_siblings_with_identical_trees_that_follow_one_another_are_printed_once(self):
        spans = Spans()
        route = spans.route()
        for _ in range(4):
            spans.add("GET", route, kind="CLIENT", attributes={"server.address": "api.example"})
        spans.add("fastapi.serialization", route)
        _, document, _ = run(spans.lines)
        self.assertRegex(document, r"├─ GET  ×4 +\[external: api\.example\]")
        self.assertIn("- External calls in one request: fewest 4, most 4", document)

    def test_more_shapes_than_the_limit_are_counted_but_not_drawn(self):
        spans = Spans()
        for number in range(trace_tree.MAX_SHAPES + 2):
            route = spans.route(trace=f"t{number}")
            for _ in range(number):
                spans.add("step", route, trace=f"t{number}")
            spans.add("end", route, trace=f"t{number}")
        _, document, _ = run(spans.lines)
        self.assertIn(f"- Shapes: {trace_tree.MAX_SHAPES + 2}", document)
        self.assertEqual(document.count("### Shape "), trace_tree.MAX_SHAPES)
        self.assertIn("2 more shapes not shown (2 requests)", document)

    def test_the_order_of_lines_in_the_span_file_does_not_change_the_output(self):
        spans = Spans()
        for trace in ("t1", "t2"):
            route = spans.route(trace=trace)
            endpoint = spans.add("fastapi.endpoint", route, trace=trace)
            spans.llm(endpoint, trace=trace)
            spans.add("GET", endpoint, kind="CLIENT", trace=trace, attributes={"server.address": "api.example"})
        shuffled = list(spans.lines)
        random.Random(7).shuffle(shuffled)
        first, second = run(spans.lines)[1], run(shuffled)[1]
        self.assertEqual(first.splitlines()[5:], second.splitlines()[5:])  # all but the temporary file's path


class KindTest(unittest.TestCase):
    def test_the_http_request_beneath_a_model_call_is_not_an_external_call_and_its_target_is_listed(self):
        spans = Spans()
        route = spans.route()
        call = spans.llm(route)
        helper = spans.add("send", call)
        spans.add("POST", helper, kind="CLIENT", attributes={"server.address": "llm.example"})
        spans.add("GET", call, kind="CLIENT", attributes={"server.address": "weather.example"})
        _, document, _ = run(spans.lines)
        self.assertIn("- External calls in one request: fewest 0, most 0", document)
        self.assertIn("- External targets seen: none", document)
        self.assertIn("- LLM calls in one request: fewest 1, most 1", document)
        self.assertRegex(document, r"POST +\(inside the LLM call: llm\.example\)")
        self.assertIn("- Reached from beneath an LLM call (taken as that call's own request, not counted): "
                      "llm.example, weather.example", document)

    def test_a_model_span_beneath_a_model_span_is_a_second_call(self):
        spans = Spans()
        route = spans.route()
        outer = spans.llm(route)
        spans.llm(outer)
        _, document, _ = run(spans.lines)
        self.assertIn("- LLM calls in one request: fewest 2, most 2", document)

    def test_an_operation_name_that_is_not_text_does_not_stop_the_run(self):
        spans = Spans()
        route = spans.route()
        spans.add("chat", route, attributes={"gen_ai.operation.name": ["chat"], "gen_ai.request.model": "model-x"})
        status, document, _ = run(spans.lines)
        self.assertEqual(status, 0)
        self.assertIn("- LLM calls in one request: fewest 1, most 1", document)

    def test_tool_and_agent_spans_are_not_model_calls_but_the_calls_beneath_them_are(self):
        spans = Spans()
        route = spans.route()
        agent = spans.llm(route, operation="invoke_agent")
        spans.llm(agent)
        tool = spans.llm(agent, operation="execute_tool")
        spans.add("GET", tool, kind="CLIENT", attributes={"server.address": "tool.example"})
        spans.llm(agent)
        _, document, _ = run(spans.lines)
        self.assertIn("- LLM calls in one request: fewest 2, most 2", document)
        self.assertIn("- External calls in one request: fewest 1, most 1", document)
        self.assertIn("- External targets seen: tool.example", document)

    def test_a_span_with_model_attributes_and_no_operation_name_is_a_model_call(self):
        spans = Spans()
        route = spans.route()
        spans.add("ask the model", route, attributes={"gen_ai.request.model": "model-x"})
        _, document, _ = run(spans.lines)
        self.assertRegex(document, r"ask the model +\[LLM\]")

    def test_an_external_call_names_the_system_it_reached(self):
        spans = Spans()
        route = spans.route()
        spans.add("SELECT app.users", route, kind="CLIENT", attributes={"db.system.name": "postgresql",
                                                                         "server.address": "db.internal"})
        spans.add("GET", route, kind="CLIENT", attributes={"url.full": "https://user:pw@api.example:8443/v1?q=1"})
        spans.add("send orders", route, kind="PRODUCER", attributes={"messaging.system": "kafka"})
        spans.add("call", route, kind="CLIENT")
        _, document, _ = run(spans.lines)
        self.assertIn("[external: postgresql]", document)
        self.assertIn("[external: api.example]", document)
        self.assertIn("[external: kafka]", document)
        self.assertRegex(document, r"call +\[external\]")
        self.assertIn("- External targets seen: api.example, call, kafka, postgresql", document)
        self.assertNotIn("pw@", document)
        self.assertNotIn("q=1", document)


class EntryPointTest(unittest.TestCase):
    def test_a_job_traced_by_the_wrapper_is_an_entry_point(self):
        spans = Spans()
        job = spans.add("app.jobs.nightly_digest")
        spans.llm(job)
        _, document, _ = run(spans.lines)
        self.assertIn("| app.jobs.nightly_digest | 1 | 1 | 0 | 0 | 1 |", document)
        self.assertNotIn("HTTP status", document)

    def test_the_tests_own_client_above_a_route_is_not_the_entry_point_and_not_an_external_call(self):
        spans = Spans()
        client = spans.add("POST", kind="CLIENT", attributes={"server.address": "testserver"})
        route = spans.route(parent=client)
        spans.add("GET", route, kind="CLIENT", attributes={"server.address": "api.example"})
        _, document, _ = run(spans.lines)
        self.assertIn("| POST /ask | 1 | 0 | 1 | 0 | 1 |", document)
        self.assertIn("- External targets seen: api.example", document)
        self.assertIn("- Spans in no request (above an entry point, or outside any): POST ×1", document)

    def test_a_helper_span_between_the_tests_client_and_a_route_is_not_the_entry_point(self):
        spans = Spans()
        client = spans.add("test client", kind="CLIENT")
        helper = spans.add("send", client)
        route = spans.route(parent=helper)
        spans.add("fastapi.endpoint", route)
        _, document, _ = run(spans.lines)
        self.assertIn("Result: 1 entry point, 1 request,", document)
        self.assertIn("| POST /ask | 1 | 0 | 0 | 0 | 1 |", document)
        self.assertIn("- Spans in no request (above an entry point, or outside any): send ×1, test client ×1", document)

    def test_a_job_that_calls_one_of_the_applications_own_routes_is_one_request_and_the_route_another(self):
        spans = Spans()
        job = spans.add("app.jobs.sync")
        call = spans.add("POST", job, kind="CLIENT", attributes={"server.address": "localhost"})
        route = spans.route(parent=call)
        spans.llm(route)
        _, document, _ = run(spans.lines)
        self.assertIn("| app.jobs.sync | 1 | 0 | 1 | 0 | 1 |", document)
        self.assertIn("| POST /ask | 1 | 1 | 0 | 0 | 1 |", document)
        self.assertNotIn("POST /ask", "\n".join(section(document, "## app.jobs.sync")))
        self.assertIn("- Spans in no request (above an entry point, or outside any): none", document)

    def test_a_call_made_outside_any_entry_point_is_listed_and_is_not_a_request(self):
        spans = Spans()
        spans.route()
        spans.llm(None, trace="t2")
        _, document, _ = run(spans.lines)
        self.assertIn("Result: 1 entry point, 1 request,", document)
        self.assertIn("- Spans in no request (above an entry point, or outside any): chat model-x [LLM] ×1", document)

    def test_a_request_no_route_matched_is_grouped_by_its_method_and_said_to_have_no_route(self):
        spans = Spans()
        spans.route()
        spans.add("POST", kind="SERVER", trace="t2", attributes={"http.request.method": "POST",
                                                                  "http.response.status_code": 404})
        _, document, _ = run(spans.lines)
        self.assertIn("Named by the method alone: no route matched", "\n".join(section(document, "## POST")))
        self.assertNotIn("Named by the method alone", "\n".join(section(document, "## POST /ask")))
        summary = section(document, "## Summary")
        self.assertLess(summary.index("| POST /ask | 1 | 0 | 0 | 0 | 1 |"), summary.index("| POST | 1 | 0 | 0 | 0 | 1 |"))

    def test_a_span_whose_parent_is_not_in_the_file_starts_a_tree_and_is_counted_in_the_notes(self):
        spans = Spans()
        spans.route(parent_id="0xmissing")
        _, document, _ = run(spans.lines)
        self.assertIn("| POST /ask | 1 |", document)
        self.assertIn("Spans whose parent is not in the file (each treated as the first span of a trace): 1", document)

    def test_spans_whose_parent_links_form_a_loop_are_counted_not_dropped_silently(self):
        spans = Spans()
        spans.route()
        spans.add("a", parent_id="0x0000000000000003", trace="t2")
        spans.add("b", parent_id="0x0000000000000002", trace="t2")
        _, document, _ = run(spans.lines)
        self.assertIn("- Spans no first span leads to (their parent links form a loop): 2", document)
        self.assertIn("Result: 1 entry point, 1 request,", document)


class ScanTest(unittest.TestCase):
    def test_a_clean_file_exits_0_and_says_clean(self):
        spans = Spans()
        spans.route()
        status, document, _ = run(spans.lines, environment={"LLM_API_KEY": "sk-secret-1"})
        self.assertEqual(status, 0)
        self.assertIn("capture-policy scan CLEAN", document)
        self.assertIn("- Secret values found for: none", document)

    def test_a_secret_value_on_a_span_exits_1_and_is_named_never_printed(self):
        spans = Spans()
        route = spans.route()
        spans.add("GET", route, kind="CLIENT", attributes={"url.full": "https://api.example/v1?key=sk-secret-1"})
        status, document, _ = run(spans.lines, environment={"LLM_API_KEY": "sk-secret-1"})
        self.assertEqual(status, 1)
        self.assertIn("capture-policy scan FOUND", document)
        self.assertIn("- Secret values found for: LLM_API_KEY (environment)", document)
        self.assertNotIn("sk-secret-1", document)

    def test_a_secret_in_a_span_name_or_a_target_is_replaced_in_the_tree(self):
        spans = Spans()
        route = spans.route()
        spans.add("connect hunter2!", route, kind="CLIENT", attributes={"server.address": "hunter2!.db.example"})
        status, document, _ = run(spans.lines, environment={"DB_PASSWORD": "hunter2!"})
        self.assertEqual(status, 1)
        self.assertNotIn("hunter2!", document)
        self.assertRegex(document, r"connect <secret> +\[external: <secret>\.db\.example\]")

    def test_a_secret_recorded_as_the_http_status_is_replaced(self):
        spans = Spans()
        spans.add("POST /ask", kind="SERVER", attributes={"http.response.status_code": "sk-secret-1"})
        spans.add("POST /ask", kind="SERVER", trace="t2", attributes={"http.response.status_code": ["sk-secret-1"]})
        status, document, _ = run(spans.lines, environment={"LLM_API_KEY": "sk-secret-1"})
        self.assertEqual(status, 1)
        self.assertNotIn("sk-secret-1", document)
        self.assertIn("HTTP status <secret> ×1", document)

    def test_a_secret_in_a_file_path_is_not_printed(self):
        spans = Spans()
        spans.route()
        with tempfile.TemporaryDirectory() as folder:
            hidden = Path(folder) / "sk-secret-1"
            hidden.mkdir()
            span_file = hidden / "spans.jsonl"
            span_file.write_text("\n".join(spans.lines) + "\n", encoding="utf-8")
            blocked = hidden / "a-file"
            blocked.write_text("", encoding="utf-8")
            stdout, stderr = io.StringIO(), io.StringIO()
            with mock.patch.dict(os.environ, {"LLM_API_KEY": "sk-secret-1"}, clear=True), \
                    contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                shown = trace_tree.main(["trace-tree.py", str(span_file)])
                refused = trace_tree.main(["trace-tree.py", str(span_file), "--out", str(blocked / "out.md")])
        self.assertEqual((shown, refused), (0, 2))
        self.assertIn("<secret>/spans.jsonl", stdout.getvalue())
        self.assertIn("cannot write the --out file", stderr.getvalue())
        self.assertNotIn("sk-secret-1", stdout.getvalue() + stderr.getvalue())

    def test_a_header_attribute_exits_1_and_is_named(self):
        spans = Spans()
        spans.add("POST /ask", kind="SERVER", attributes={"http.request.header.authorization": ["Bearer abc"]})
        status, document, _ = run(spans.lines)
        self.assertEqual(status, 1)
        self.assertIn("- Header attributes: http.request.header.authorization", document)

    def test_values_are_also_taken_from_the_env_files_given(self):
        spans = Spans()
        spans.add("POST /ask", kind="SERVER", attributes={"args.key": "sk-from-file"})
        with tempfile.TemporaryDirectory() as folder:
            env_file = Path(folder) / ".env"
            env_file.write_text("LLM_API_KEY=sk-from-file\n", encoding="utf-8")
            status, document, _ = run(spans.lines, str(env_file))
        self.assertEqual(status, 1)
        self.assertIn("- Secret values found for: LLM_API_KEY (env file 1)", document)
        self.assertIn("- Values checked: the process environment and 1 env file", document)

    def test_a_span_name_cannot_break_the_documents_layout(self):
        spans = Spans()
        route = spans.route()
        spans.add("a|b\n```\n## Capture-policy scan " + "x" * 200, route)
        _, document, _ = run(spans.lines)
        self.assertEqual(sum(1 for line in document.splitlines() if line == "## Capture-policy scan"), 1)
        lines = document.splitlines()
        self.assertEqual(lines.count("```text"), 1)
        self.assertEqual(sum(1 for line in lines if line.strip() == "```"), 1)
        self.assertTrue(all(len(line) < 200 for line in section(document, "## POST /ask")))


class InputTest(unittest.TestCase):
    def test_a_span_file_with_no_span_exits_2(self):
        status, document, error = run(["", "  "])
        self.assertEqual((status, document), (2, ""))
        self.assertIn("holds no span", error)

    def test_a_line_that_is_not_a_json_object_exits_2_naming_the_line_and_not_its_text(self):
        spans = Spans()
        spans.route()
        for bad in ('{"name": "sk-secret-1', '["sk-secret-1"]'):
            status, document, error = run(spans.lines + [bad])
            self.assertEqual((status, document), (2, ""))
            self.assertIn("line 2 of the span file", error)
            self.assertNotIn("sk-secret-1", error)

    def test_spans_with_missing_or_wrongly_typed_parts_are_still_drawn(self):
        lines = [json.dumps({"name": "job", "context": None, "attributes": None, "status": None, "kind": None}),
                 json.dumps({"name": "other", "context": "x", "attributes": ["a"], "status": "ok", "parent_id": None}),
                 json.dumps({})]
        status, document, _ = run(lines)
        self.assertEqual(status, 0)
        self.assertIn("Result: 3 entry points, 3 requests,", document)

    def test_spans_without_ids_are_drawn_the_same_whatever_the_order_of_the_lines(self):
        def child(name, **attributes):
            return json.dumps({"name": name, "context": {"trace_id": "t"}, "parent_id": "r", "kind": "SpanKind.CLIENT",
                               "attributes": attributes})

        root = json.dumps({"name": "job", "context": {"trace_id": "t", "span_id": "r"}})
        lines = [root, child("alpha"), child("beta"), child("beta"), child("alpha", **{"server.address": "x.example"})]
        outputs = set()
        for seed in range(6):
            shuffled = list(lines)
            random.Random(seed).shuffle(shuffled)
            outputs.add("\n".join(run(shuffled)[1].splitlines()[5:]))
        self.assertEqual(len(outputs), 1)
        self.assertIn("- External calls in one request: fewest 4, most 4", outputs.pop())

    def test_a_tree_nested_too_deeply_to_draw_exits_2_instead_of_crashing(self):
        spans = Spans()
        parent = spans.route()
        for _ in range(3000):
            parent = spans.add("step", parent)
        status, document, error = run(spans.lines)
        self.assertEqual((status, document), (2, ""))
        self.assertIn("nested too deeply", error)

    def test_a_usage_error_exits_2_without_repeating_the_argument_it_rejected(self):
        for arguments in (["spans.jsonl", "--sk-secret-1"], ["--out"], []):
            with contextlib.redirect_stderr(io.StringIO()) as error, self.assertRaises(SystemExit) as stopped:
                trace_tree.main(["trace-tree.py", *arguments])
            self.assertEqual(stopped.exception.code, 2)
            self.assertIn("usage: trace-tree.py", error.getvalue())
            self.assertNotIn("sk-secret-1", error.getvalue())

    def test_a_missing_span_file_or_env_file_exits_2(self):
        with contextlib.redirect_stderr(io.StringIO()) as error:
            self.assertEqual(trace_tree.main(["trace-tree.py", "/nonexistent/spans.jsonl"]), 2)
        self.assertIn("cannot read the span file", error.getvalue())
        spans = Spans()
        spans.route()
        status, _, error = run(spans.lines, "/nonexistent/.env")
        self.assertEqual(status, 2)
        self.assertIn("cannot read env file 1", error)

    def test_a_missing_scan_script_exits_2_and_says_the_install_is_broken(self):
        spans = Spans()
        spans.route()
        with mock.patch.object(trace_tree, "SCAN_SCRIPT", Path("/nonexistent/check-span-file.py")):
            status, document, error = run(spans.lines)
        self.assertEqual((status, document), (2, ""))
        self.assertIn("broken install", error)

    def test_the_scan_script_is_the_one_observability_init_ships(self):
        self.assertEqual(trace_tree.SCAN_SCRIPT.parts[-4:],
                         ("skills", "observability-init", "scripts", "check-span-file.py"))
        self.assertTrue(trace_tree.SCAN_SCRIPT.is_file())

    def test_with_out_the_document_goes_to_the_file_and_only_the_result_line_is_echoed(self):
        spans = Spans()
        route = spans.route()
        spans.llm(route)
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "reviews" / "TRACE-TREE.md"
            status, echoed, _ = run(spans.lines, out=str(out))
            written = out.read_text(encoding="utf-8")
        self.assertEqual(status, 0)
        self.assertEqual(echoed.strip(), "Result: 1 entry point, 1 request, most LLM calls in one request 1 (POST /ask), "
                                         "capture-policy scan CLEAN")
        self.assertEqual(written.splitlines()[2], echoed.strip())
        self.assertIn("## POST /ask", written)

    def test_spans_without_times_are_drawn_without_a_duration(self):
        line = json.dumps({"name": "POST /ask", "context": {"trace_id": "t", "span_id": "s"}, "kind": "SpanKind.SERVER"})
        status, document, _ = run([line])
        self.assertEqual(status, 0)
        self.assertIn("POST /ask  [entry]\n", document)


class RepeatCapTest(unittest.TestCase):
    """Own-function spans, and the calls the application's repeat cap left without one."""

    @staticmethod
    def function(spans, name, parent, **more):
        attributes = {"code.function.name": name, "code.file.path": "app/x.py", "code.line.number": 1}
        attributes.update(more.pop("attributes", {}))
        return spans.add(name, parent, attributes=attributes, **more)

    def request(self, spans, trace, calls, not_recorded, failed):
        route = spans.route(trace=trace)
        loop = self.function(spans, "app.x.loop", route, trace=trace, attributes={
            "calls.app.x.step.not_recorded": not_recorded, "calls.app.x.step.not_recorded_failed": failed})
        for _ in range(calls):
            self.function(spans, "app.x.step", loop, trace=trace)
        return loop

    def test_the_counts_are_printed_beside_the_capped_function(self):
        spans = Spans()
        self.request(spans, "t1", calls=3, not_recorded=4, failed=1)
        status, out, _ = run(spans.lines)
        self.assertEqual(status, 0)
        self.assertRegex(out, r"└─ app\.x\.step  ×3  \+4 not recorded, 1 failed")
        self.assertIn("- Own-function calls not recorded in one request (over the repeat cap): fewest 4, most 4; "
                      "of those, ended in an exception: most 1", out)

    def test_counts_that_differ_are_one_shape_with_a_range(self):
        spans = Spans()
        self.request(spans, "t1", calls=3, not_recorded=2, failed=0)
        self.request(spans, "t2", calls=3, not_recorded=9, failed=2)
        _, out, _ = run(spans.lines)
        self.assertIn("- Shapes: 1", out)
        self.assertRegex(out, r"app\.x\.step  ×3  \+2–9 not recorded, 0–2 failed")
        self.assertIn("fewest 2, most 9; of those, ended in an exception: most 2", out)

    def test_a_request_under_the_cap_and_one_over_it_in_the_same_shape(self):
        spans = Spans()
        self.request(spans, "t1", calls=3, not_recorded=5, failed=0)
        route = spans.route(trace="t2")
        loop = self.function(spans, "app.x.loop", route, trace="t2")
        for _ in range(3):
            self.function(spans, "app.x.step", loop, trace="t2")
        _, out, _ = run(spans.lines)
        self.assertIn("- Shapes: 1", out)
        self.assertRegex(out, r"app\.x\.step  ×3  \+0–5 not recorded, 0 failed")

    def test_the_count_goes_on_the_last_run_of_that_function(self):
        spans = Spans()
        route = spans.route()
        loop = self.function(spans, "app.x.loop", route, attributes={
            "calls.app.x.step.not_recorded": 6, "calls.app.x.step.not_recorded_failed": 0})
        self.function(spans, "app.x.step", loop)
        self.function(spans, "app.x.other", loop)
        self.function(spans, "app.x.step", loop)
        self.function(spans, "app.x.step", loop)
        _, out, _ = run(spans.lines)
        rows = [line for line in out.splitlines() if "app.x.step" in line]
        self.assertEqual(len(rows), 2)
        self.assertNotIn("not recorded", rows[0])
        self.assertRegex(rows[1], r"app\.x\.step  ×2  \+6 not recorded, 0 failed")

    def test_a_capped_function_drawn_nowhere_beneath_the_caller_gets_a_row_of_its_own(self):
        spans = Spans()
        route = spans.route()
        loop = self.function(spans, "app.x.loop", route, attributes={
            "calls.app.x.step.not_recorded": 7, "calls.app.x.step.not_recorded_failed": 3})
        library = spans.add("library.batch", loop)
        self.function(spans, "app.x.step", library)
        _, out, _ = run(spans.lines)
        self.assertRegex(out, r"├─ library\.batch.*\n.*│  └─ app\.x\.step.*\n.*└─ \(app\.x\.step  \+7 not recorded, 3 failed\)")

    def test_no_capped_call_no_line_and_no_note(self):
        spans = Spans()
        route = spans.route()
        loop = self.function(spans, "app.x.loop", route)
        self.function(spans, "app.x.step", loop)
        _, out, _ = run(spans.lines)
        self.assertNotIn("not recorded", out)

    def test_a_count_that_is_not_a_positive_whole_number_is_ignored(self):
        for value in ("4", True, 0, -2, 1.5, None):
            spans = Spans()
            route = spans.route()
            loop = self.function(spans, "app.x.loop", route, attributes={"calls.app.x.step.not_recorded": value})
            self.function(spans, "app.x.step", loop)
            status, out, _ = run(spans.lines)
            self.assertEqual(status, 0)
            self.assertNotIn("not recorded", out, repr(value))

    def test_a_function_name_is_never_cut_and_any_other_long_name_still_is(self):
        long_name = "app." + "very_long_module_name." * 5 + "function_"
        spans = Spans()
        route = spans.route()
        self.function(spans, long_name + "one", route)
        self.function(spans, long_name + "two", route)
        spans.add("SELECT " + "column, " * 20, route)
        _, out, _ = run(spans.lines)
        self.assertIn(long_name + "one", out)
        self.assertIn(long_name + "two", out)
        self.assertIn("SELECT column", out)
        self.assertNotIn("SELECT " + "column, " * 20, out)

    def test_two_capped_names_that_print_alike_after_redaction_add_up(self):
        spans = Spans()
        route = spans.route()
        self.function(spans, "app.x.loop", route, attributes={
            "calls.app.hunter2secret.not_recorded": 4, "calls.app.hunter2secret.not_recorded_failed": 1,
            "calls.app.swordfish99.not_recorded": 6, "calls.app.swordfish99.not_recorded_failed": 2})
        _, out, _ = run(spans.lines, environment={"API_KEY": "hunter2secret", "DB_PASSWORD": "swordfish99"})
        self.assertIn("fewest 10, most 10; of those, ended in an exception: most 3", out)
        self.assertRegex(out, r"\+10 not recorded, 3 failed")
        self.assertNotIn("hunter2secret", out)
        self.assertNotIn("swordfish99", out)

    def test_a_secret_inside_a_capped_function_name_is_not_printed(self):
        spans = Spans()
        route = spans.route()
        self.function(spans, "app.x.loop", route, attributes={"calls.app.hunter2secret.not_recorded": 2})
        status, out, _ = run(spans.lines, environment={"API_KEY": "hunter2secret"})
        self.assertNotIn("hunter2secret", out)


if __name__ == "__main__":
    unittest.main()
