import contextlib
import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_spec = importlib.util.spec_from_file_location("check_span_file", Path(__file__).resolve().parents[1] / "check-span-file.py")
check_span_file = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_span_file)


def span(attributes=None, name="POST /ask", events=None, status=None):
    return json.dumps({"name": name, "attributes": attributes or {}, "events": events or [], "status": status or {}})


class CheckTest(unittest.TestCase):
    def check(self, lines, environment, **more_sources):
        return check_span_file.check(lines, [("environment", environment), *more_sources.items()])[:2]

    def short(self, lines, environment):
        return check_span_file.check(lines, [("environment", environment)])[2]

    def test_a_clean_span_file_reports_nothing(self):
        self.assertEqual(self.check([span({"http.route": "/ask"})], {"LLM_API_KEY": "sk-secret-1"}), ([], []))

    def test_a_secret_value_in_an_attribute_is_reported_by_name(self):
        leaked, _ = self.check([span({"args.key": "sk-secret-1"})], {"LLM_API_KEY": "sk-secret-1", "LLM_MODEL": "m"})
        self.assertEqual(leaked, ["LLM_API_KEY (environment)"])

    def test_a_secret_inside_a_url_a_span_name_an_event_or_an_error_message_is_reported(self):
        environment = {"db_password": "hunter2!"}
        for line in (
            span({"url.full": "https://u:hunter2!@db.example/x"}),
            span(name="connect hunter2!"),
            span(events=[{"name": "exception", "attributes": {"exception.message": "bad auth hunter2!"}}]),
            span(status={"description": "refused: hunter2!"}),
        ):
            self.assertEqual(self.check([line], environment)[0], ["db_password (environment)"], line)

    def test_a_secret_with_characters_json_escapes_is_still_found(self):
        secret = 'say "pa\\ss" now'
        self.assertEqual(self.check([span({"note": secret})], {"APP_SECRET": secret})[0], ["APP_SECRET (environment)"])

    def test_a_secret_inside_a_json_string_attribute_is_found(self):
        secret = 'say "demo" now'
        messages = json.dumps([{"role": "user", "parts": [{"content": f"key is {secret}", "type": "text"}]}])
        leaked, _ = self.check([span({"gen_ai.input.messages": messages})], {"APP_SECRET": secret})
        self.assertEqual(leaked, ["APP_SECRET (environment)"])
        nested = json.dumps({"outer": messages})
        self.assertEqual(self.check([span({"blob": nested})], {"APP_SECRET": secret})[0], ["APP_SECRET (environment)"])

    def test_a_numeric_secret_recorded_as_a_number_is_found(self):
        self.assertEqual(self.check([span({"args.pin": 123456})], {"API_KEY": "123456"})[0], ["API_KEY (environment)"])
        self.assertEqual(self.check([span({"flag": True, "n": 1})], {"API_KEY": "True"})[0], [])

    def test_every_value_a_name_has_is_checked_whichever_source_it_came_from(self):
        lines = [span({"args.key": "old-value"})]
        leaked, _ = self.check(lines, {"API_KEY": "new-value"}, **{"env file 1": {"API_KEY": "old-value"}})
        self.assertEqual(leaked, ["API_KEY (env file 1)"])

    def test_each_otlp_header_value_is_checked_on_its_own_with_and_without_its_scheme(self):
        environment = {"OTEL_EXPORTER_OTLP_HEADERS": "projectName=edukate,Authorization=Basic%20QUJDREVGRw=="}
        leaked, _ = self.check([span({"http.auth": "QUJDREVGRw=="})], environment)
        self.assertEqual(leaked, ["OTEL_EXPORTER_OTLP_HEADERS header 2 (environment)"])
        leaked, _ = self.check([span({"x": "Basic QUJDREVGRw=="})], environment)
        self.assertEqual(leaked, ["OTEL_EXPORTER_OTLP_HEADERS header 2 (environment)"])

    def test_a_name_that_is_not_secret_named_is_not_checked(self):
        self.assertEqual(self.check([span({"gen_ai.request.model": "big-model"})], {"LLM_MODEL": "big-model"})[0], [])

    def test_a_header_attribute_is_reported_on_a_span_or_an_event(self):
        _, headers = self.check(
            [
                span({"http.request.header.authorization": ["x"], "http.route": "/ask"}),
                span(events=[{"name": "e", "attributes": {"http.response.headers": "y"}}]),
            ],
            {},
        )
        self.assertEqual(headers, ["http.request.header.authorization", "http.response.headers"])

    def test_a_short_secret_is_matched_as_a_whole_value_only(self):
        environment = {"API_KEY": "abc", "EMPTY_TOKEN": ""}
        self.assertEqual(self.check([span({"a": "abcdef", "b": ""})], environment)[0], [])
        self.assertEqual(self.check([span({"a": "abc"})], environment)[0], ["API_KEY (environment)"])
        self.assertEqual(self.short([], environment), ["API_KEY (environment)"])
        self.assertEqual(self.short([], {"API_KEY": "long-enough"}), [])

    def test_a_short_secret_inside_a_printed_name_is_still_replaced(self):
        leaked, headers = self.check([span({"http.request.header.abc": "abc"})], {"API_KEY": "abc"})
        self.assertEqual(leaked, ["API_KEY (environment)"])
        self.assertEqual(headers, ["http.request.header.<secret>"])

    def test_nothing_printed_holds_a_secret_value_or_a_control_character(self):
        environment = {"API_KEY": "demo-secret-value", "OTEL_EXPORTER_OTLP_HEADERS": "demo-secret-value=x%20yz12"}
        leaked, headers = self.check(
            [span({"http.request.header.demo-secret-value": "1", "http.request.header.a\nb": "yz12"})], environment
        )
        printed = " ".join(leaked + headers)
        self.assertNotIn("demo-secret-value", printed)
        self.assertNotIn("\n", printed)
        self.assertEqual(headers, ["http.request.header.<secret>", "http.request.header.a?b"])
        self.assertEqual(leaked, ["API_KEY (environment)", "OTEL_EXPORTER_OTLP_HEADERS header 1 (environment)"])


class EnvFileTest(unittest.TestCase):
    def test_values_lose_quotes_export_and_trailing_comments(self):
        cases = {
            "true": "true",
            " true # off for now": "true",
            '"quoted # kept" # dropped': "quoted # kept",
            "'single'": "single",
            "# only a comment": "",
            "a#b": "a#b",
            "": "",
        }
        for raw, expected in cases.items():
            self.assertEqual(check_span_file.env_value(raw), expected, raw)


class MainTest(unittest.TestCase):
    def run_main(self, span_text, env_text, environment):
        with tempfile.TemporaryDirectory() as folder:
            span_file, env_file = Path(folder) / "spans.jsonl", Path(folder) / ".env"
            span_file.write_text(span_text)
            env_file.write_text(env_text)
            out = io.StringIO()
            with mock.patch.dict(os.environ, environment, clear=True), contextlib.redirect_stdout(out):
                status = check_span_file.main(["check-span-file.py", str(span_file), str(env_file)])
        return status, out.getvalue()

    def test_a_leak_from_the_env_file_exits_1_and_prints_the_name_not_the_value(self):
        status, out = self.run_main(span({"args.key": "file-secret-9"}) + "\n", "export APP_TOKEN='file-secret-9' # x\n", {})
        self.assertEqual(status, 1)
        self.assertIn("APP_TOKEN (env file 1)", out)
        self.assertNotIn("file-secret-9", out)

    def test_a_clean_file_exits_0(self):
        status, out = self.run_main(span({"http.route": "/ask"}) + "\n\n", "APP_TOKEN=file-secret-9\n", {"X_KEY": "kkkkkk"})
        self.assertEqual(status, 0)
        self.assertIn("spans checked: 1", out)

    def test_a_missing_span_file_exits_2(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(check_span_file.main(["check-span-file.py", "/nonexistent/spans.jsonl"]), 2)


if __name__ == "__main__":
    unittest.main()
