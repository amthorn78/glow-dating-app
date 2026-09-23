import os
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from unittest import TestCase

from glow_api.configuration import ConfigurationError
from glow_api.runtime import RuntimeConfigurationError, runtime_command

API = Path(__file__).resolve().parents[1]
MARKER = "synthetic-build-boundary-secret"


class RuntimeTests(TestCase):
    def test_command_cannot_bind_publicly_or_run_management_actions(self):
        for environment in ("development", "test"):
            command = runtime_command({"GLOW_ENV": environment, "PORT": "8123"})
            self.assertIn("127.0.0.1:8123", command)
            self.assertIn("--preload", command)
            self.assertIn("glow_api.wsgi:application", command)
            self.assertFalse(any("manage.py" in value or "migrate" in value for value in command))

    def test_invalid_port_and_runtime_overrides_fail_without_values(self):
        for overrides in (
            {"PORT": "0"},
            {"PORT": "80"},
            {"PORT": "65536"},
            {"PORT": " 8000"},
            {"PORT": "８０００"},
            {"PORT": MARKER},
            {"GUNICORN_CMD_ARGS": "--bind=0.0.0.0:8000"},
            {"DJANGO_SETTINGS_MODULE": "glow_persistence.static_settings"},
        ):
            with self.subTest(overrides=tuple(overrides)):
                with self.assertRaises((RuntimeConfigurationError, ConfigurationError)) as result:
                    runtime_command({"GLOW_ENV": "test", **overrides})
                self.assertNotIn(MARKER, str(result.exception))

    def test_actual_process_refuses_unsafe_modes_before_imports(self):
        for overrides in (
            {},
            {"GLOW_ENV": "staging"},
            {"GLOW_ENV": "production"},
            {"GLOW_ENV": "test", "DATABASE_URL": MARKER},
            {"GLOW_ENV": "test", "HDE_API_TOKEN": MARKER},
            {"GLOW_ENV": "test", "PORT": MARKER},
            {"GLOW_ENV": "test", "GUNICORN_CMD_ARGS": MARKER},
        ):
            with self.subTest(names=tuple(overrides)):
                result = subprocess.run(
                    [sys.executable, "-m", "glow_api.runtime"],
                    cwd=API,
                    env={"PATH": os.environ["PATH"], **overrides},
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=5,
                )
                self.assertEqual(result.returncode, 78)
                self.assertNotIn(MARKER, result.stdout + result.stderr)
                self.assertIn('"event": "runtime_refused"', result.stdout)
                self.assertNotIn("Traceback", result.stdout + result.stderr)

    def test_entrypoint_serves_loopback_and_terminates_cleanly(self):
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        process = subprocess.Popen(
            [sys.executable, "-m", "glow_api.runtime"],
            cwd=API,
            env={"PATH": os.environ["PATH"], "GLOW_ENV": "test", "PORT": str(port)},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        deadline = time.monotonic() + 8
        try:
            while True:
                if process.poll() is not None:
                    self.fail("Runtime exited before liveness became available.")
                try:
                    with opener.open(
                        f"http://127.0.0.1:{port}/health/live", timeout=0.2
                    ) as response:
                        self.assertEqual(response.status, 200)
                    break
                except (urllib.error.URLError, TimeoutError):
                    if time.monotonic() >= deadline:
                        self.fail("Runtime liveness exceeded its startup budget.")
                    time.sleep(0.05)
            with self.assertRaises(urllib.error.HTTPError) as response:
                opener.open(f"http://127.0.0.1:{port}/health/ready", timeout=1)
            self.assertEqual(response.exception.code, 503)
            response.exception.close()
            try:
                opener.open(f"http://127.0.0.1:{port}/{MARKER}?birth={MARKER}", timeout=1)
            except urllib.error.HTTPError as error:
                error.close()
            # Exercise Gunicorn's parser-level diagnostic as well as Django's
            # 404 handling. Neither may record submitted raw text.
            with socket.create_connection(("127.0.0.1", port), timeout=1) as client:
                client.sendall(
                    f"GET / HTTP/1.1\r\nHost: localhost\r\nBad Header: {MARKER}\r\n\r\n".encode()
                )
                self.assertIn(b"400", client.recv(1024))
            process.send_signal(signal.SIGTERM)
            stdout, stderr = process.communicate(timeout=7)
            self.assertEqual(process.returncode, 0)
            self.assertNotIn(MARKER, stdout + stderr)
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate(timeout=2)
