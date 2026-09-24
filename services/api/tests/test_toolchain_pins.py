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

Pin = tuple[str, str]  # (repository-relative file, plus the field when needed; version)


class ToolchainPinTests(TestCase):
    def read(self, path: str) -> str:
        return (ROOT / path).read_text(encoding="utf-8")

    def matches(self, path: str, pattern: str) -> list[Pin]:
        found = re.findall(pattern, self.read(path), flags=re.MULTILINE)
        if not found:
            self.fail(f"{path}: no pin matches {pattern!r}")
        return [(path, value) for value in found]

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
        self.assert_agree(
            "Python",
            self.script_pin("PYTHON")
            + [("services/api/.python-version", self.read("services/api/.python-version").strip())]
            + self.matches(WORKFLOW, r"python-version: '([^']+)'")
            + self.matches("Dockerfile", r"^FROM python:(\d+\.\d+\.\d+)-"),
        )

    def test_node_pins_agree(self):
        self.assert_agree(
            "Node",
            self.script_pin("NODE")
            + self.package_pins("node")
            + self.matches(WORKFLOW, r"node-version: '([^']+)'"),
        )

    def test_npm_pins_agree(self):
        self.assert_agree(
            "npm",
            self.script_pin("NPM")
            + self.package_pins("npm")
            + self.matches(WORKFLOW, r"npm install --global npm@(\S+)"),
        )
