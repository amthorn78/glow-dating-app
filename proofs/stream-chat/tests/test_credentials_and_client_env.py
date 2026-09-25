import os
import subprocess
import unittest

import tests  # noqa: F401
from glow_stream_proof.client_bridge import (
    PASSTHROUGH,
    RUNNER,
    UnsafeClientEnvironment,
    client_environment,
)
from glow_stream_proof.credentials import (
    EXPECTED_APP_ID,
    EnvironmentRefused,
    load_server_credentials,
)

SECRET = "synthetic-test-secret-value"
GOOD = {
    "STREAM_APP_ID": EXPECTED_APP_ID,
    "STREAM_API_KEY": "synthetickey",
    "STREAM_API_SECRET": SECRET,
}


class CredentialsTest(unittest.TestCase):
    def test_loads_and_hides_secret(self) -> None:
        creds = load_server_credentials(GOOD)
        self.assertEqual(creds.secret(), SECRET)
        self.assertNotIn(SECRET, repr(creds))
        self.assertNotIn(SECRET, str(creds))

    def test_refuses_hde_variables_by_name(self) -> None:
        for name in ("DATABASE_URL", "HD_API_KEY", "GEO_API_KEY"):
            with self.assertRaises(EnvironmentRefused) as ctx:
                load_server_credentials({**GOOD, name: "x"})
            self.assertIn(name, str(ctx.exception))
            self.assertNotIn("x;", str(ctx.exception))

    def test_refuses_missing_and_other_app(self) -> None:
        with self.assertRaises(EnvironmentRefused):
            load_server_credentials({k: v for k, v in GOOD.items() if k != "STREAM_API_SECRET"})
        with self.assertRaises(EnvironmentRefused):
            load_server_credentials({**GOOD, "STREAM_API_SECRET": ""})
        with self.assertRaises(EnvironmentRefused):
            load_server_credentials({**GOOD, "STREAM_APP_ID": "999"})


class ClientEnvironmentTest(unittest.TestCase):
    def parent(self) -> dict[str, str]:
        return {
            **GOOD,
            "PATH": "/usr/bin",
            "HOME": "/home/test",
            "HTTPS_PROXY": "http://127.0.0.1:9",
            "NODE_EXTRA_CA_CERTS": "/tmp/ca.crt",
            "UNRELATED": "value",
        }

    def test_allowlist_only_and_no_secret(self) -> None:
        env = client_environment(
            self.parent(), api_key="synthetickey", user_token="tok", max_api_calls=10, secret=SECRET
        )
        self.assertNotIn("STREAM_API_SECRET", env)
        self.assertNotIn("STREAM_API_KEY", env)
        self.assertNotIn("UNRELATED", env)
        self.assertFalse(any(SECRET in v for v in env.values()))
        self.assertEqual(env["PROOF_API_KEY"], "synthetickey")
        self.assertEqual(env["PROOF_USER_TOKEN"], "tok")
        self.assertEqual(env["HTTPS_PROXY"], "http://127.0.0.1:9")
        allowed = set(PASSTHROUGH) | {"PROOF_API_KEY", "PROOF_USER_TOKEN", "PROOF_MAX_API_CALLS"}
        self.assertLessEqual(set(env), allowed)

    def test_no_token_session(self) -> None:
        env = client_environment(
            self.parent(), api_key="k", user_token=None, max_api_calls=5, secret=SECRET
        )
        self.assertNotIn("PROOF_USER_TOKEN", env)

    def test_refuses_secret_value_in_passthrough(self) -> None:
        parent = {**self.parent(), "HOME": f"/home/{SECRET}"}
        with self.assertRaises(UnsafeClientEnvironment):
            client_environment(parent, api_key="k", user_token=None, max_api_calls=5, secret=SECRET)


class RunnerRefusalTest(unittest.TestCase):
    """The Node runner refuses to start with the secret's name present (no network used)."""

    def run_runner(self, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["node", str(RUNNER)],
            env={"PATH": os.environ.get("PATH", "/usr/bin"), **env},
            input="",
            capture_output=True,
            text=True,
            timeout=30,
        )

    def test_refuses_secret_name(self) -> None:
        done = self.run_runner({"PROOF_API_KEY": "k", "STREAM_API_SECRET": "anything"})
        self.assertEqual(done.returncode, 3)
        self.assertIn("STREAM_API_SECRET", done.stderr)
        self.assertNotIn("anything", done.stderr)

    def test_refuses_missing_key(self) -> None:
        done = self.run_runner({})
        self.assertEqual(done.returncode, 3)


if __name__ == "__main__":
    unittest.main()
