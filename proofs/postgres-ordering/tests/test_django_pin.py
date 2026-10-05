"""The proof pins the same Django as services/api (D1's pin test)."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PROOF = REPO_ROOT / "proofs" / "postgres-ordering"
API = REPO_ROOT / "services" / "api"


def pinned(lock: Path, package: str) -> tuple[str, frozenset[str]]:
    """The version and hashes a lock pins for a package."""
    text = lock.read_text(encoding="utf-8")
    match = re.search(
        rf"^{re.escape(package)}==(\S+?) \\\n((?:    --hash=sha256:[0-9a-f]+(?: \\)?\n)+)",
        text,
        flags=re.MULTILINE,
    )
    if match is None:
        raise AssertionError(f"{lock}: {package} is not pinned with hashes")
    hashes = frozenset(re.findall(r"sha256:([0-9a-f]+)", match.group(2)))
    return match.group(1), hashes


class DjangoPinTests(unittest.TestCase):
    def test_django_version_and_hashes_match_the_api(self) -> None:
        api_version, api_hashes = pinned(API / "requirements.lock", "django")
        for lock in ("requirements.lock", "requirements-dev.lock"):
            with self.subTest(lock=lock):
                version, hashes = pinned(PROOF / lock, "django")
                self.assertEqual(version, api_version)
                self.assertEqual(hashes, api_hashes)

    def test_inputs_name_the_same_django(self) -> None:
        api_input = (API / "requirements.in").read_text(encoding="utf-8")
        proof_input = (PROOF / "requirements.in").read_text(encoding="utf-8")
        api_pin = re.search(r"^Django==(\S+)$", api_input, flags=re.MULTILINE)
        proof_pin = re.search(r"^Django==(\S+)$", proof_input, flags=re.MULTILINE)
        assert api_pin and proof_pin
        self.assertEqual(proof_pin.group(1), api_pin.group(1))
        self.assertEqual(proof_pin.group(1), "5.2.17")

    def test_psycopg_3_and_no_allauth(self) -> None:
        version, _ = pinned(PROOF / "requirements.lock", "psycopg")
        self.assertTrue(version.startswith("3."), version)
        for lock in ("requirements.lock", "requirements-dev.lock"):
            self.assertNotIn("allauth", (PROOF / lock).read_text(encoding="utf-8"))

    def test_ruff_and_mypy_match_the_api_dev_lock(self) -> None:
        for package in ("ruff", "mypy"):
            with self.subTest(package=package):
                api_version, _ = pinned(API / "requirements-dev.lock", package)
                version, _ = pinned(PROOF / "requirements-dev.lock", package)
                self.assertEqual(version, api_version)


if __name__ == "__main__":
    unittest.main()
