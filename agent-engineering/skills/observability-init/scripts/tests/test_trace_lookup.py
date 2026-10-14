"""The trace lookup, rendered from its template and run against a stand-in for Opik's REST API."""

import datetime
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[2] / "templates" / "python" / "trace_lookup.py.template"
SECRETS = ("SECRET-MESSAGE-TEXT", "SECRET-ANSWER-TEXT", "SECRET-ERROR-TEXT", "SECRET-ARG-TEXT", "SECRET-RETURN-TEXT")
NOW = datetime.datetime(2026, 10, 12, 8, 30, tzinfo=datetime.timezone.utc)


def stamp(moment, digits=3):
    fraction = f"{moment.microsecond:06d}{'0' * 3}"[:digits]
    return moment.strftime("%Y-%m-%dT%H:%M:%S") + (f".{fraction}" if digits else "") + "Z"


def trace(trace_id, minutes_ago, name="POST /ask", status=200, **more):
    start = NOW - datetime.timedelta(minutes=minutes_ago)
    return {"id": trace_id, "name": name, "start_time": stamp(start), "end_time": stamp(start + datetime.timedelta(seconds=2)),
            "duration": 2000.0, "llm_span_count": 1, "input": {"http.response.status_code": status, "http.route": "/ask"}, **more}


def span(span_id, name, parent=None, start_ms=0, end_ms=0, kind="general", **more):
    base = NOW - datetime.timedelta(minutes=5)
    return {"id": span_id, "trace_id": "t-failed", "parent_span_id": parent, "name": name, "type": kind,
            "start_time": stamp(base + datetime.timedelta(milliseconds=start_ms), digits=more.pop("digits", 3)),
            "end_time": stamp(base + datetime.timedelta(milliseconds=end_ms)), "duration": float(end_ms - start_ms), **more}


def place(line):
    return {"function.name": "x", "file.path": "app/main.py", "line.number": line}


ERROR = {"exception_type": "Error", "traceback": "Error"}
TRACES = [
    trace("t-new", 1),
    trace("t-failed", 5, status=502, error_info=ERROR),
    trace("t-503", 7, status=503),
    trace("t-marked", 9, comments=[{"text": "it gave the result away"}], tags=["bad"]),
    trace("t-old", 40, name="GET /"),
]
SPANS = {"t-failed": [
    span("s-root", "POST /ask", None, 0, 3000, error_info=ERROR),
    span("s-guard", "app.main.guard", "s-root", 0, 3000, metadata=place(10)),
    span("s-check", "app.main.check", "s-guard", 0, 1, metadata=place(20), input={"calls.app.main.text.not_recorded": 4}),
    span("s-route", "app.main.ask_route", "s-guard", 1, 3000, metadata=place(30), error_info=ERROR),
    span("s-ask", "app.llm.ask", "s-route", 2, 3000, metadata=place(40), error_info=ERROR),
    span("s-build", "app.prompt.build_messages", "s-route", 2, 2, metadata=place(50), digits=9,
         input={"args.question": "SECRET-ARG-TEXT"}, output={"value": "SECRET-RETURN-TEXT"}),
    span("s-llm", "chat demo-model", "s-ask", 3, 3000, kind="llm", model="demo-model",
         usage={"prompt_tokens": 120, "completion_tokens": 0},
         input={"messages": [{"role": "user", "content": "SECRET-MESSAGE-TEXT"}]},
         output={"messages": [{"role": "assistant", "content": "SECRET-ANSWER-TEXT"}]},
         error_info={"exception_type": "APIError", "message": "SECRET-ERROR-TEXT"}),
]}


class FakeOpik(BaseHTTPRequestHandler):
    traces = TRACES
    requests = []
    repeat = False  # answer every page of spans with the same full page

    def log_message(self, *arguments):
        pass

    def do_GET(self):
        url = urllib.parse.urlsplit(self.path)
        query = dict(urllib.parse.parse_qsl(url.query))
        type(self).requests.append((url.path, query, dict(self.headers)))
        page, size = int(query.get("page", 1)), int(query.get("size", 100))
        if url.path == "/api/v1/private/traces":
            body = {"content": self.traces[(page - 1) * size: page * size], "total": len(self.traces)}
        elif url.path.startswith("/api/v1/private/traces/"):
            body = next((t for t in self.traces if t["id"] == url.path.rsplit("/", 1)[1]), None)
        elif url.path == "/api/v1/private/spans":
            found = list(reversed(SPANS.get(query.get("trace_id"), [])))
            body = {"content": found[:size] if self.repeat else found[(page - 1) * size: page * size]}
        else:
            self.send_response(404)
            self.end_headers()
            return
        data = json.dumps(body).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class Redirect(BaseHTTPRequestHandler):
    target = ""

    def log_message(self, *arguments):
        pass

    def do_GET(self):
        self.send_response(302)
        self.send_header("Location", self.target + self.path)
        self.end_headers()


def serve(handler):
    server = HTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def stop(server):
    server.shutdown()
    server.server_close()


class TraceLookupTest(unittest.TestCase):
    def setUp(self):
        FakeOpik.traces, FakeOpik.requests, FakeOpik.repeat = TRACES, [], False
        self.server = serve(FakeOpik)
        self.addCleanup(stop, self.server)
        self.root = Path(tempfile.mkdtemp())
        (self.root / "scripts").mkdir()
        self.script = self.root / "scripts" / "trace_lookup.py"
        self.script.write_text(TEMPLATE.read_text(encoding="utf-8")
                               .replace("@@ROOT@@", "Path(__file__).resolve().parents[1]")
                               .replace("@@ENV_FILE@@", 'ROOT / ".env"')
                               .replace("@@TRACE_LOOKUP_COMMAND@@", "python scripts/trace_lookup.py"), encoding="utf-8")
        self.env_file(f"http://127.0.0.1:{self.server.server_port}/api/v1/private/otel", "projectName=demo,Authorization=Bearer%20tok")

    def env_file(self, endpoint, headers=""):
        lines = [f"OTEL_EXPORTER_OTLP_ENDPOINT={endpoint}"] if endpoint else []
        lines += [f"OTEL_EXPORTER_OTLP_HEADERS={headers}"] if headers else []
        (self.root / ".env").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def run_lookup(self, *arguments, zone="UTC"):
        environment = {key: value for key, value in os.environ.items() if not key.startswith("OTEL_")}
        environment["TZ"] = zone
        result = subprocess.run([sys.executable, str(self.script), *arguments], cwd=self.root, env=environment,
                                capture_output=True, text=True, timeout=60)
        return result.returncode, result.stdout, result.stderr

    def ids(self, output):
        return [line.rsplit("  ", 1)[1] for line in output.splitlines()[1:]]

    def test_the_rendered_file_has_no_placeholders(self):
        self.assertNotIn("@@", self.script.read_text(encoding="utf-8"))

    def test_the_list_is_newest_first_one_line_per_trace(self):
        code, out, _ = self.run_lookup()
        self.assertEqual(code, 0)
        self.assertIn("project demo: 5 trace(s) match", out)
        self.assertEqual(self.ids(out), ["t-new", "t-failed", "t-503", "t-marked", "t-old"])
        self.assertIn("2026-10-12 08:29:00  POST /ask  200  2000 ms  ok", out)

    def test_failed_means_an_error_or_a_server_error_status(self):
        code, out, _ = self.run_lookup("--failed")
        self.assertEqual(self.ids(out), ["t-failed", "t-503"])
        self.assertIn("FAILED (Error)", out)

    def test_marked_means_a_score_a_tag_or_a_comment(self):
        code, out, _ = self.run_lookup("--marked")
        self.assertEqual(self.ids(out), ["t-marked"])
        self.assertIn("marks 1 tag, 1 comment", out)

    def test_at_keeps_the_traces_within_ten_minutes(self):
        code, out, _ = self.run_lookup("--at", "2026-10-12 08:18")
        self.assertEqual(self.ids(out), ["t-failed", "t-503", "t-marked"])

    def test_a_badly_written_time_stops_with_the_form_it_takes(self):
        code, _, err = self.run_lookup("--at", "yesterday")
        self.assertEqual(code, 2)
        self.assertIn('"YYYY-MM-DD HH:MM"', err)

    def test_every_page_is_read(self):
        FakeOpik.traces = [trace(f"t-{n:03d}", n) for n in range(150)]
        code, out, _ = self.run_lookup("--limit", "200")
        self.assertIn("150 trace(s) match", out)
        self.assertEqual(len(self.ids(out)), 150)

    def test_a_trace_prints_as_a_call_tree_with_where_the_failure_started(self):
        code, out, _ = self.run_lookup("t-failed")
        self.assertEqual(code, 0)
        lines = out.splitlines()
        self.assertEqual(lines[0], "trace t-failed  started 2026-10-12 08:25:00  7 spans")
        self.assertEqual(lines[1], "POST /ask  3000 ms  FAILED (Error)")
        self.assertIn("  app.main.guard  app/main.py:10  3000 ms", lines)
        self.assertIn("      app.llm.ask  app/main.py:40  2998 ms  FAILED (Error)", lines)
        self.assertIn("        chat demo-model  [model call: demo-model, 120 in / 0 out]  2997 ms  FAILED (APIError)", lines)
        # The guard between the request and the route did not fail; the failure still starts at the model call.
        self.assertIn("failed first in: chat demo-model  the model call  (APIError)", out)

    def test_calls_in_the_same_millisecond_are_ordered_by_when_they_ended(self):
        _, out, _ = self.run_lookup("t-failed")
        self.assertLess(out.index("app.prompt.build_messages"), out.index("app.llm.ask"))

    def test_calls_the_repeat_cap_counted_are_shown_as_a_number(self):
        _, out, _ = self.run_lookup("t-failed")
        self.assertIn("app.main.check  app/main.py:20  1 ms  (+4 further calls counted, not shown)", out)

    def test_without_content_nothing_recorded_is_printed(self):
        for arguments in (("t-failed",), ("t-failed", "--model-call"), ()):
            code, out, err = self.run_lookup(*arguments)
            for secret in SECRETS:
                self.assertNotIn(secret, out + err, arguments)
        self.assertIn("printed only with --content", self.run_lookup("t-failed", "--model-call")[1])

    def test_with_content_the_recorded_text_is_printed(self):
        _, out, _ = self.run_lookup("t-failed", "--content", "--model-call")
        for secret in SECRETS:
            self.assertIn(secret, out)

    def test_the_model_call_is_written_to_a_file_to_replay_it(self):
        target = self.root / "call.json"
        code, out, _ = self.run_lookup("t-failed", "--model-call", "--out", str(target))
        self.assertEqual(code, 0)
        written = json.loads(target.read_text(encoding="utf-8"))
        self.assertEqual(written["trace"], "t-failed")
        self.assertEqual(written["calls"][0]["messages"][0]["content"], "SECRET-MESSAGE-TEXT")
        self.assertEqual(written["calls"][0]["answer"][0]["content"], "SECRET-ANSWER-TEXT")
        self.assertNotIn("SECRET", out)

    def test_the_marks_a_person_left_are_printed_on_the_trace(self):
        SPANS["t-marked"] = [dict(span("m-root", "POST /ask"), trace_id="t-marked")]
        self.addCleanup(SPANS.pop, "t-marked")
        _, out, _ = self.run_lookup("t-marked")
        self.assertIn("tag: bad", out)
        self.assertIn("comment: it gave the result away", out)

    def test_content_options_need_a_trace_id(self):
        for option in ("--content", "--model-call"):
            code, _, err = self.run_lookup(option)
            self.assertEqual(code, 2)
            self.assertIn("give its id", err)

    def test_an_unknown_trace_stops(self):
        code, _, err = self.run_lookup("t-none")
        self.assertEqual(code, 2)
        self.assertIn("No trace t-none in project demo", err)

    def test_the_headers_go_to_opik_and_the_project_is_a_query(self):
        self.run_lookup()
        path, query, headers = FakeOpik.requests[0]
        self.assertEqual(query["project_name"], "demo")
        self.assertEqual(headers.get("Authorization"), "Bearer tok")
        self.assertNotIn("projectname", {key.lower() for key in headers})

    def test_a_redirect_is_refused(self):
        Redirect.target = f"http://127.0.0.1:{self.server.server_port}"
        bouncer = serve(Redirect)
        self.addCleanup(stop, bouncer)
        self.env_file(f"http://127.0.0.1:{bouncer.server_port}/api/v1/private/otel", "projectName=demo,Authorization=Bearer%20tok")
        code, _, err = self.run_lookup()
        self.assertEqual(code, 2)
        self.assertIn("Opik answered 302", err)
        self.assertEqual(FakeOpik.requests, [])

    def test_a_backend_that_is_not_opik_stops(self):
        self.env_file(f"http://127.0.0.1:{self.server.server_port}/api/public/otel", "Authorization=Basic%20x")
        code, _, err = self.run_lookup()
        self.assertEqual(code, 2)
        self.assertIn("reads Opik only", err)
        self.assertEqual(FakeOpik.requests, [])

    def test_no_backend_stops(self):
        self.env_file("")
        code, _, err = self.run_lookup()
        self.assertEqual(code, 2)
        self.assertIn("No tracing backend is set", err)

    def test_an_unreachable_opik_stops_with_its_address(self):
        port = self.server.server_port
        stop(self.server)
        code, _, err = self.run_lookup()
        self.assertEqual(code, 2)
        self.assertIn(f"cannot be reached at http://127.0.0.1:{port} (", err)


    def spans_for(self, trace_id, found):
        SPANS[trace_id] = [dict(item, trace_id=trace_id) for item in found]
        self.addCleanup(SPANS.pop, trace_id)

    def test_each_kind_of_mark_counts_on_its_own(self):
        FakeOpik.traces = [trace("t-score", 1, feedback_scores=[{"name": "good", "value": 0}]),
                           trace("t-tag", 2, tags=["bad"]), trace("t-comment", 3, comments=[{"text": "wrong"}]), trace("t-none", 4)]
        _, out, _ = self.run_lookup("--marked")
        self.assertEqual(self.ids(out), ["t-score", "t-tag", "t-comment"])

    def test_scan_limits_how_many_of_the_newest_are_searched(self):
        _, out, _ = self.run_lookup("--failed", "--scan", "2")
        self.assertEqual(self.ids(out), ["t-failed"])
        _, out, _ = self.run_lookup("--limit", "2")
        self.assertIn("5 trace(s) match", out)
        self.assertEqual(self.ids(out), ["t-new", "t-failed"])

    def test_at_is_read_in_the_local_time_zone(self):
        # Berlin is two hours ahead of UTC in October: 10:18 there is 08:18 UTC.
        _, out, _ = self.run_lookup("--at", "2026-10-12 10:18", zone="Europe/Berlin")
        self.assertEqual(self.ids(out), ["t-failed", "t-503", "t-marked"])
        self.assertIn("2026-10-12 10:25:00  POST /ask  502", out)

    def test_every_page_of_spans_is_read(self):
        self.spans_for("t-big", [span("b-root", "POST /ask", None, 0, 300)] +
                       [span(f"b-{n:03d}", f"app.work.step{n}", "b-root", n, n + 1) for n in range(150)])
        _, out, _ = self.run_lookup("t-big")
        self.assertIn("151 spans", out)
        self.assertIn("app.work.step149", out)

    def test_a_server_that_repeats_a_page_does_not_keep_the_lookup_going(self):
        self.spans_for("t-big", [span(f"b-{n:03d}", f"app.work.step{n}", None, n, n + 1) for n in range(100)])
        FakeOpik.repeat = True
        code, out, _ = self.run_lookup("t-big")
        self.assertEqual(code, 0)
        self.assertIn("100 spans", out)

    def test_the_earliest_of_two_separate_failures_is_named(self):
        self.spans_for("t-two", [
            span("r", "POST /ask", None, 0, 50, error_info=ERROR),
            span("a", "app.one", "r", 10, 20, metadata=place(1), error_info={"exception_type": "KeyError"}),
            span("b", "app.two", "r", 5, 8, metadata=place(2), error_info={"exception_type": "ValueError"}),
        ])
        _, out, _ = self.run_lookup("t-two")
        self.assertIn("failed first in: app.two  app/main.py:2  (ValueError)", out)

    def test_a_span_whose_parent_is_missing_is_shown_as_a_root(self):
        self.spans_for("t-orphan", [span("r", "POST /ask", None, 0, 50), span("o", "app.lost", "gone", 5, 6, metadata=place(3))])
        _, out, _ = self.run_lookup("t-orphan")
        self.assertIn("\napp.lost  app/main.py:3  1 ms", out)

    def test_spans_whose_parents_loop_are_shown_not_dropped(self):
        self.spans_for("t-loop", [span("r", "POST /ask", None, 0, 50),
                                  span("x", "app.x", "y", 1, 2, metadata=place(4), error_info={"exception_type": "OSError"}),
                                  span("y", "app.y", "x", 3, 4, metadata=place(5))])
        code, out, _ = self.run_lookup("t-loop")
        self.assertEqual(code, 0)
        self.assertIn("2 span(s) whose parents form a loop:", out)
        self.assertIn("app.x", out)
        self.assertIn("app.y", out)
        self.assertIn("failed first in: app.x", out)

    def test_content_alone_prints_the_model_call(self):
        _, out, _ = self.run_lookup("t-failed", "--content")
        self.assertIn("SECRET-MESSAGE-TEXT", out)
        self.assertIn("SECRET-ANSWER-TEXT", out)

    def test_a_file_that_cannot_be_written_stops(self):
        code, _, err = self.run_lookup("t-failed", "--model-call", "--out", str(self.root / "no-such-dir" / "call.json"))
        self.assertEqual(code, 2)
        self.assertIn("cannot be written (FileNotFoundError)", err)

    def test_the_env_file_is_read_as_the_application_reads_it(self):
        address = f"http://127.0.0.1:{self.server.server_port}/api/v1/private/otel"
        for line in ("OTEL_EXPORTER_OTLP_HEADERS=projectName=demo # the project", 'OTEL_EXPORTER_OTLP_HEADERS="projectName=demo" # note',
                     "export OTEL_EXPORTER_OTLP_HEADERS=projectName=demo"):
            (self.root / ".env").write_text(f"OTEL_EXPORTER_OTLP_ENDPOINT={address}\n# OTEL_EXPORTER_OTLP_HEADERS=projectName=other\n{line}\n",
                                            encoding="utf-8")
            _, out, _ = self.run_lookup()
            self.assertIn("project demo:", out, line)

    def test_the_first_of_two_lines_for_one_setting_wins_as_in_the_application(self):
        address = f"http://127.0.0.1:{self.server.server_port}/api/v1/private/otel"
        (self.root / ".env").write_text(f"OTEL_EXPORTER_OTLP_ENDPOINT={address}\nOTEL_EXPORTER_OTLP_HEADERS=projectName=demo\n"
                                        "OTEL_EXPORTER_OTLP_HEADERS=projectName=other\n", encoding="utf-8")
        _, out, _ = self.run_lookup()
        self.assertIn("project demo:", out)

    def test_a_header_with_a_line_break_stops_without_its_value(self):
        self.env_file(f"http://127.0.0.1:{self.server.server_port}/api/v1/private/otel", "projectName=demo,Authorization=Bearer%0AKEY-12345")
        code, out, err = self.run_lookup()
        self.assertEqual(code, 2)
        self.assertIn("'Authorization' holds a line break", err)
        self.assertNotIn("KEY-12345", out + err)
        self.assertEqual(FakeOpik.requests, [])

    def test_an_address_with_a_password_is_printed_without_it(self):
        port = self.server.server_port
        stop(self.server)
        self.env_file(f"http://someone:PASS-6789@127.0.0.1:{port}/api/v1/private/otel", "projectName=demo")
        code, _, err = self.run_lookup()
        self.assertEqual(code, 2)
        self.assertIn(f"cannot be reached at http://127.0.0.1:{port} (", err)
        self.assertNotIn("PASS-6789", err)


if __name__ == "__main__":
    unittest.main()
