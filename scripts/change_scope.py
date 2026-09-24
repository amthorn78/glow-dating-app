"""Conservative CI/review classification. No network, dependencies or PR code execution."""

import argparse
import json
from pathlib import PurePosixPath
import re
import subprocess


# Exempt only inert evidence/provenance, never operational instructions by default.
ORDINARY_PATHS = frozenset({
    "docs/continuity/migration-publication.md",
    "apps/mobile/EXPO-TEMPLATE-LICENSE.md",
    "docs/testing/foundation-checkpoint.md",
    "docs/testing/p02-checkpoint.md",
    "docs/testing/p03-checkpoint.md",
    "docs/testing/p04-1-checkpoint.md",
    "docs/testing/p04-2-checkpoint.md",
    "docs/testing/p04-3-checkpoint.md",
    "docs/testing/p05-1-checkpoint.md",
    "docs/testing/p05-2-checkpoint.md",
    "docs/testing/p05-3-checkpoint.md",
})
ORDINARY_PREFIXES = ("docs/continuity/history/", "docs/testing/evidence/")
BEHAVIOR_NAMES = frozenset({"agents.md", "claude.md", "claude.local.md", "skill.md", "copilot-instructions.md"})


def ordinary_document(path: str) -> bool:
    p = PurePosixPath(path)
    if path != str(p) or p.is_absolute() or ".." in p.parts:
        return False
    if p.name.lower() in BEHAVIOR_NAMES or p.name.lower().endswith(".instructions.md"):
        return False
    return path in ORDINARY_PATHS or (path.startswith(ORDINARY_PREFIXES) and p.suffix == ".md")


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], stderr=subprocess.DEVNULL)


def classify(base: str, head: str, *, merge_base: bool = False) -> dict:
    # Only immutable SHA inputs; never flags, expressions or filenames from PR text.
    if not all(re.fullmatch(r"[0-9a-f]{40}", sha) and int(sha, 16) for sha in (base, head)):
        return {"full": True, "reason": "missing-or-invalid-comparison", "paths": []}
    try:
        if merge_base:
            base = git("merge-base", base, head).decode().strip()
        fields = git("diff", "--raw", "--no-abbrev", "--no-renames", "-z", base, head, "--").split(b"\0")
        paths = []
        full = False
        for i in range(0, len(fields) - 1, 2):
            metadata = fields[i].decode().split()
            path = fields[i + 1].decode("utf-8", errors="strict")
            paths.append(path)
            modes = (metadata[0][1:], metadata[1])
            full |= not ordinary_document(path) or any(mode not in {"100644", "000000"} for mode in modes)
        # Empty/ambiguous comparison does not earn a documentation exemption.
        return {"full": full or not paths, "reason": "behavior-or-empty" if full or not paths else "ordinary-docs-only", "paths": paths}
    except (subprocess.CalledProcessError, UnicodeError, IndexError, ValueError):
        return {"full": True, "reason": "comparison-unavailable", "paths": []}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--merge-base", action="store_true")
    parser.add_argument("--github-output")
    args = parser.parse_args()
    result = classify(args.base, args.head, merge_base=args.merge_base)
    print(json.dumps(result))
    if args.github_output:
        with open(args.github_output, "a", encoding="utf-8") as output:
            output.write(f"full={str(result['full']).lower()}\n")
