"""Conservative CI/review classification. No network, dependencies or PR code execution."""

import argparse
import json
from pathlib import PurePosixPath
import re
import subprocess


# Nathan, 24 September 2026: documentation never runs application CI or code/security
# review. A change made only of regular Markdown files is ordinary documentation; any
# script or other non-Markdown file, symlink or executable file makes it full scope.
# Paths with a `.claude` component also stay full scope (Nathan, 24 September 2026):
# Claude Code skills, commands, agents and rules there can carry shell commands and
# permissions. The match ignores case, as case-insensitive filesystems do.
def ordinary_document(path: str) -> bool:
    p = PurePosixPath(path)
    if path != str(p) or p.is_absolute() or ".." in p.parts:
        return False
    if any(part.casefold() == ".claude" for part in p.parts):
        return False
    return p.suffix == ".md"


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], stderr=subprocess.DEVNULL)


def classify(base: str, head: str, *, merge_base: bool = False) -> dict:
    # Only immutable SHA inputs; never flags, expressions or filenames from PR text.
    if not all(re.fullmatch(r"[0-9a-f]{40}", sha) and int(sha, 16) for sha in (base, head)):
        return {"full": True, "reason": "missing-or-invalid-comparison", "paths": []}
    try:
        if merge_base:
            # Criss-cross history has several merge bases; any single one can hide changes.
            bases = git("merge-base", "--all", base, head).decode().split()
            if len(bases) != 1:
                return {"full": True, "reason": "multiple-merge-bases", "paths": []}
            base = bases[0]
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
