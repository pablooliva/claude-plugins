"""The own-function hook in the bootstrap template: every check of function_hook/probe.py, in each setting of
the values switch.

Needs Python 3.12 or later with the OpenTelemetry SDK installed; skipped otherwise. From the skill's directory:

    uv run --python 3.12 --with opentelemetry-sdk python -m unittest discover -s scripts/tests
"""

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parents[1] / "templates" / "python" / "telemetry.py.template"
FILLS = {
    "@@SERVICE_NAME@@": "probe",
    "@@DISTRIBUTION@@": "probe",
    "@@ENV_FILE@@": 'Path(__file__).resolve().parent / "absent.env"',
    "@@OWN_DIRECTORIES@@": "()",
    "@@INSTRUMENTATION@@": "    pass",
    "@@HEADER_SOURCE@@": "    return None, None",
}


def _sdk_available() -> bool:
    try:
        return importlib.util.find_spec("opentelemetry.sdk.trace") is not None
    except ModuleNotFoundError:
        return False


@unittest.skipUnless(sys.version_info >= (3, 12) and _sdk_available(), "needs Python 3.12+ with opentelemetry-sdk")
class FunctionHook(unittest.TestCase):
    def run_probe(self, mode: str) -> None:
        with tempfile.TemporaryDirectory() as folder:
            text = TEMPLATE.read_text(encoding="utf-8")
            for placeholder, fill in FILLS.items():
                self.assertIn(placeholder, text)
                text = text.replace(placeholder, fill)
            self.assertNotIn("@@", text, "a placeholder of the template has no fill in this test")
            (Path(folder) / "bootstrap.py").write_text(text, encoding="utf-8")
            done = subprocess.run(
                [sys.executable, "-B", str(HERE / "function_hook" / "probe.py"), mode, folder],
                capture_output=True, text=True, timeout=300,
            )
        lines = done.stdout.splitlines()
        failed = [line for line in lines if line.startswith("FAIL")]
        self.assertEqual(done.returncode, 0, done.stderr[-2000:])
        self.assertTrue(any(line.startswith("PASS") for line in lines), "the probe ran no check")
        self.assertEqual(failed, [])

    def test_values_switch_unset(self):
        self.run_probe("none")

    def test_values_for_every_module(self):
        self.run_probe("all")

    def test_values_for_one_module(self):
        self.run_probe("probe_pkg.work")


if __name__ == "__main__":
    unittest.main()
