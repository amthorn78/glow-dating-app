"""One SDK under test (P06.2 Stage B2; DM-16 2.2), one resolved set (P06.2 Stage B2-C1;
DM-17 5.1).

The conformance run executes the Stream adapter on the harness's installed SDK, so the API's
development lock must resolve every package it shares with the harness's ``requirements.lock``
to the same version with the same set of hashes; otherwise the live run vouches for a
different build than the API pins. Stage B2 held ``getstream``, ``httpx`` and ``pyjwt`` (the
signer uses it directly) to that and only reported the other shared packages, nine of which
had resolved later (``python-dateutil`` a major version later). Since B2-C1 the development
lock is regenerated with the harness's lock as a constraint, and this test holds every shared
package to it, each as a subtest; ``tzdata``, which only the API holds, is not shared and
stays as resolved. The files are only read.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
API_DEV_LOCK = ROOT / "services" / "api" / "requirements-dev.lock"
API_DEV_IN = ROOT / "services" / "api" / "requirements-dev.in"
API_RUNTIME_LOCK = ROOT / "services" / "api" / "requirements.lock"
HARNESS_LOCK = ROOT / "proofs" / "stream-chat" / "requirements.lock"
# The SDK, its HTTP client and the JWT library: the shared packages Stage B2 named; every
# other shared package is held the same way since B2-C1.
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


def shared_packages() -> list[str]:
    """Every package both locks resolve."""
    return sorted(set(resolved(API_DEV_LOCK)) & set(resolved(HARNESS_LOCK)))


class DependencyPinTests(unittest.TestCase):
    def test_every_package_the_two_locks_share_matches_the_harness(self) -> None:
        api, harness = resolved(API_DEV_LOCK), resolved(HARNESS_LOCK)
        shared = shared_packages()
        for name in SHARED:
            self.assertIn(name, shared, f"{name} is not in both locks")
        # The SDK's whole resolved set is shared (about 30 packages); a shrunken intersection
        # would mean a lock lost its packages, not that they agree.
        self.assertGreaterEqual(len(shared), 25, shared)
        for name in shared:
            with self.subTest(package=name):
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


if __name__ == "__main__":
    unittest.main()
