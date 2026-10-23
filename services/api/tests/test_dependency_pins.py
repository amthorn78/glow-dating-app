"""One SDK under test (P06.2 Stage B2; DM-16 2.2).

The conformance run executes the Stream adapter on the harness's installed SDK, so the
API's development lock must resolve ``getstream``, ``httpx`` and ``pyjwt`` (the signer uses
it directly) to the same version with the same set of hashes as the harness's
``requirements.lock``; otherwise the live run vouches for a different build than the API
pins. The files are only read. Any other shared package whose version differs is reported,
not failed (``differing_shared_packages``).
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
API_DEV_LOCK = ROOT / "services" / "api" / "requirements-dev.lock"
API_DEV_IN = ROOT / "services" / "api" / "requirements-dev.in"
API_RUNTIME_LOCK = ROOT / "services" / "api" / "requirements.lock"
HARNESS_LOCK = ROOT / "proofs" / "stream-chat" / "requirements.lock"
SHARED = ("getstream", "httpx", "pyjwt")
PINS = {"getstream": "6.1.0", "pyjwt": "2.15.0"}

Resolved = dict[str, tuple[str, frozenset[str]]]


def resolved(lock: Path) -> Resolved:
    """Each package of a uv ``--generate-hashes`` lock: its version and its hashes."""
    packages: Resolved = {}
    name = version = None
    hashes: set[str] = set()
    for raw in lock.read_text(encoding="utf-8").splitlines():
        line = raw.strip().rstrip("\\").strip()
        pinned = re.fullmatch(r"([A-Za-z0-9_.-]+)==(\S+)", line)
        if pinned:
            if name is not None:
                packages[name] = (str(version), frozenset(hashes))
            name, version, hashes = (
                pinned.group(1).lower().replace("_", "-"),
                pinned.group(2),
                set(),
            )
        elif line.startswith("--hash=") and name is not None:
            hashes.add(line.removeprefix("--hash="))
    if name is not None:
        packages[name] = (str(version), frozenset(hashes))
    return packages


def differing_shared_packages() -> dict[str, tuple[str, str]]:
    """Shared packages whose versions differ between the two locks (API, harness)."""
    api, harness = resolved(API_DEV_LOCK), resolved(HARNESS_LOCK)
    return {
        name: (api[name][0], harness[name][0])
        for name in sorted(set(api) & set(harness))
        if api[name][0] != harness[name][0]
    }


class DependencyPinTests(unittest.TestCase):
    def test_the_sdk_its_http_client_and_the_jwt_library_match_the_harness(self) -> None:
        api, harness = resolved(API_DEV_LOCK), resolved(HARNESS_LOCK)
        for name in SHARED:
            with self.subTest(package=name):
                self.assertIn(name, api, f"{name} is not in the API's development lock")
                self.assertIn(name, harness, f"{name} is not in the harness's lock")
                self.assertEqual(api[name][0], harness[name][0], "version")
                self.assertTrue(api[name][1], "no hashes")
                self.assertEqual(api[name][1], harness[name][1], "hashes")

    def test_the_pins_are_exact_and_in_the_development_scope_only(self) -> None:
        text = API_DEV_IN.read_text(encoding="utf-8")
        for name, version in PINS.items():
            self.assertRegex(text, rf"(?m)^{name}=={re.escape(version)}$")
        runtime = resolved(API_RUNTIME_LOCK)
        for name in SHARED:
            self.assertNotIn(name, runtime, f"{name} must stay out of the runtime lock (P11)")
        self.assertEqual(resolved(API_DEV_LOCK)["getstream"][0], PINS["getstream"])

    def test_differing_shared_packages_is_a_report_not_a_failure(self) -> None:
        differing = differing_shared_packages()
        self.assertFalse(set(differing) & set(SHARED))


if __name__ == "__main__":
    unittest.main()
