"""Static agreement of the pinned toolchain versions across the repository.

The files are only read. Nothing here runs the bootstrap script or the pinned tools.
"""

import json
import re
from pathlib import Path
from unittest import TestCase

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = "scripts/bootstrap-toolchain.sh"
WORKFLOW = ".github/workflows/foundation.yml"
PACKAGES = ("apps/mobile/package.json", "packages/contracts/package.json")

# Workflow values may be single-quoted, double-quoted or bare YAML scalars.
PYTHON_VERSION = r"(?<![\w-])python-version\s*:\s*['\"]?([^'\"\s#,}]+)"
NODE_VERSION = r"(?<![\w-])node-version\s*:\s*['\"]?([^'\"\s#,}]+)"
NPM_INSTALL = r"\bnpm\s+(?:install|i)\s+(?:--global|-g)\s+npm@([^'\"\s#]+)"

Pin = tuple[str, str]  # (repository-relative file, plus the field or line; version)


class ToolchainPinTests(TestCase):
    def read(self, path: str) -> str:
        return (ROOT / path).read_text(encoding="utf-8")

    def matches(self, path: str, pattern: str) -> list[Pin]:
        text = self.read(path)
        found = []
        for match in re.finditer(pattern, text, flags=re.MULTILINE):
            line = text.count("\n", 0, match.start()) + 1
            found.append((f"{path}:{line}", match.group(1)))
        if not found:
            self.fail(f"{path}: no pin matches {pattern!r}")
        return found

    def assert_one_per(self, pins: list[Pin], what: str, pattern: str) -> None:
        # A spelling the pin pattern misses changes the count instead of passing unseen.
        expected = len(re.findall(pattern, self.read(WORKFLOW)))
        if len(pins) != expected:
            self.fail(
                f"{WORKFLOW}: {len(pins)} {what} pins recognized for {expected} {pattern!r} matches"
            )

    def script_pin(self, name: str) -> list[Pin]:
        return self.matches(SCRIPT, rf"^readonly {name}_VERSION=(\S+)$")

    def package_pins(self, engine: str) -> list[Pin]:
        pins = []
        for path in PACKAGES:
            package = json.loads(self.read(path))
            if engine not in package.get("engines", {}):
                self.fail(f"{path}: engines.{engine} is missing")
            pins.append((f"{path} engines.{engine}", package["engines"][engine]))
            if engine == "npm":
                manager = package.get("packageManager", "")
                if not manager.startswith("npm@"):
                    self.fail(f"{path}: packageManager does not name npm")
                pins.append((f"{path} packageManager", manager.removeprefix("npm@")))
        return pins

    def assert_agree(self, tool: str, pins: list[Pin]) -> None:
        files_by_version: dict[str, list[str]] = {}
        for path, version in pins:
            files = files_by_version.setdefault(version, [])
            if path not in files:
                files.append(path)
        if len(files_by_version) > 1:
            groups = sorted(files_by_version.items(), key=lambda group: len(group[1]))
            detail = "; ".join(f"{version} in {', '.join(files)}" for version, files in groups)
            self.fail(f"{tool} pins disagree (diverging files first): {detail}")

    def test_python_pins_agree(self):
        # Every setup-python step names its version, so no job runs an unpinned Python.
        workflow = self.matches(WORKFLOW, PYTHON_VERSION)
        self.assert_one_per(workflow, "python-version", r"actions/setup-python@")
        self.assert_agree(
            "Python",
            self.script_pin("PYTHON")
            + [("services/api/.python-version", self.read("services/api/.python-version").strip())]
            + workflow
            + self.matches("Dockerfile", r"^FROM python:(\d+\.\d+\.\d+)-"),
        )

    def test_node_pins_agree(self):
        workflow = self.matches(WORKFLOW, NODE_VERSION)
        self.assert_one_per(workflow, "node-version", r"actions/setup-node@")
        self.assert_agree(
            "Node",
            self.script_pin("NODE") + self.package_pins("node") + workflow,
        )

    def test_npm_pins_agree(self):
        # Node 24.19.0 bundles a different npm, so every job that sets up Node installs the
        # pinned npm once, and every npm@ reference in the workflow is such an install.
        workflow = self.matches(WORKFLOW, NPM_INSTALL)
        self.assert_one_per(workflow, "npm install", r"actions/setup-node@")
        self.assert_one_per(workflow, "npm install", r"\bnpm@")
        self.assert_agree(
            "npm",
            self.script_pin("NPM") + self.package_pins("npm") + workflow,
        )
