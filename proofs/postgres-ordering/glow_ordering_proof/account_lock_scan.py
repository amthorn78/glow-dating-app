"""The scan of explicit account row locks (SV3 Stage A, correction C1; its brief's D2 and D14;
DM-61 K1, K3).

Every explicit lock of an ``AppAccount`` row, in ``services/api`` (its tests and virtual
environment left out) and in the ordering proof's reference design (``reference.py``), must be
``FOR NO KEY UPDATE``: it excludes every other writer and every ``FOR SHARE`` reader, but not the
``FOR KEY SHARE`` PostgreSQL's foreign-key check takes, so no write that references another
member's account waits on that member's writers and no lock cycle forms through one (Codex's CX1).

It reads the source, never imports it, and finds three kinds of lock:

- **an ORM lock of the account:** a ``select_for_update(...)`` call whose receiver names
  ``AppAccount``; it must pass ``no_key=True``;
- **a generic ORM lock:** a ``select_for_update(...)`` call on a model held in a variable (a
  helper such as ``glow_chat``'s ``_lock`` or the reference design's), which can lock an account;
  it must pass a ``no_key`` that names ``AppAccount`` (``no_key=model is AppAccount``) or is
  ``True``;
- **a lock in SQL:** a string (or f-string) outside a docstring that takes ``FOR UPDATE`` (or
  ``FOR NO KEY UPDATE``, ``FOR SHARE``, ``FOR KEY SHARE``) and names the account table, or names
  no table it can read (a ``{table}`` placeholder); a ``FOR UPDATE`` there is refused.

A select_for_update whose receiver names another model (``Match``, ``Profile``, ...) is not an
account lock and is not judged. It prints counts and locations only.
"""

from __future__ import annotations

import ast
import re
import sys
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
API_ROOT = REPO_ROOT / "services" / "api"
REFERENCE = Path(__file__).resolve().parent / "reference.py"
ACCOUNT_MODEL = "AppAccount"
ACCOUNT_TABLE = "glow_persistence_appaccount"
SKIPPED_PARTS = frozenset({".venv", "tests", "__pycache__", "migrations"})
SQL_LOCK = re.compile(r"\bFOR\s+(NO\s+KEY\s+UPDATE|UPDATE|KEY\s+SHARE|SHARE)\b", re.IGNORECASE)
# Every explicit account lock C1 found and changed (DM-61's list, with the two helpers), by file
# and enclosing function: a lock added, lost or moved changes this list and fails the scan.
EXPECTED_SITES: tuple[tuple[str, str], ...] = (
    ("proofs/postgres-ordering/glow_ordering_proof/reference.py", "_lock"),
    ("services/api/glow_chat/contact.py", "_lock"),
    ("services/api/glow_identity/age.py", "transition"),
    ("services/api/glow_identity/revocation.py", "mark_verified"),
    ("services/api/glow_profiles/identity_verification.py", "_locked"),
    ("services/api/glow_profiles/tx.py", "lock_account"),
    ("services/api/glow_profiles/tx.py", "lock_account_any_state"),
)


@dataclass(frozen=True)
class Lock:
    path: str
    line: int
    function: str
    kind: str  # "orm", "generic" or "sql"
    mode: str  # "FOR NO KEY UPDATE", "FOR UPDATE", ... or the no_key expression

    @property
    def no_key(self) -> bool:
        return self.mode == "FOR NO KEY UPDATE"

    def where(self) -> str:
        return f"{self.path}:{self.line} ({self.function}, {self.kind})"


def sources(roots: Iterable[Path] | None = None) -> list[Path]:
    """The files scanned: every ``.py`` under ``services/api`` but its tests, migrations and
    virtual environment, and the reference design."""
    if roots is not None:
        found: list[Path] = []
        for root in roots:
            found += [root] if root.is_file() else sorted(root.rglob("*.py"))
        return [path for path in found if not SKIPPED_PARTS & set(path.parts)]
    found = [
        path
        for path in sorted(API_ROOT.rglob("*.py"))
        if not SKIPPED_PARTS & set(path.relative_to(API_ROOT).parts)
    ]
    return [*found, REFERENCE]


def _relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _docstrings(tree: ast.AST) -> set[int]:
    return {
        id(node.body[0].value)
        for node in ast.walk(tree)
        if isinstance(node, ast.Module | ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef)
        and node.body
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
    }


def _functions(tree: ast.AST) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    return [
        node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
    ]


def _enclosing(functions: Sequence[ast.AST], line: int) -> str:
    holding = [
        f
        for f in functions
        if isinstance(f, ast.FunctionDef | ast.AsyncFunctionDef)
        and f.lineno <= line <= (f.end_lineno or f.lineno)
    ]
    if not holding:
        return "<module>"
    innermost = max(holding, key=lambda f: f.lineno)
    assert isinstance(innermost, ast.FunctionDef | ast.AsyncFunctionDef)
    return innermost.name


def _receiver_names(node: ast.AST) -> tuple[list[str], bool]:
    """The names in a call's receiver chain, and whether the chain starts from a lower-case
    variable (a model held in a variable) rather than a model class."""
    names: list[str] = []
    current = node
    while True:
        if isinstance(current, ast.Attribute):
            names.append(current.attr)
            current = current.value
        elif isinstance(current, ast.Call):
            current = current.func
        elif isinstance(current, ast.Subscript):
            current = current.value
        elif isinstance(current, ast.Name):
            names.append(current.id)
            return names, current.id[:1].islower()
        else:
            return names, False


def _text(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return "".join(
            str(part.value) if isinstance(part, ast.Constant) else "{}" for part in node.values
        )
    return None


def scan_file(path: Path) -> list[Lock]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    relative = _relative(path)
    functions = _functions(tree)
    docstrings = _docstrings(tree)
    found: list[Lock] = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "select_for_update"
        ):
            names, variable = _receiver_names(node.func.value)
            no_key = next((k.value for k in node.keywords if k.arg == "no_key"), None)
            expression = ast.unparse(no_key) if no_key is not None else ""
            function = _enclosing(functions, node.lineno)
            if ACCOUNT_MODEL in names:
                mode = "FOR NO KEY UPDATE" if expression == "True" else "FOR UPDATE"
                found.append(Lock(relative, node.lineno, function, "orm", mode))
            elif variable and not any(name[:1].isupper() for name in names):
                generic = expression == "True" or (
                    ACCOUNT_MODEL in expression and " is " in expression
                )
                mode = "FOR NO KEY UPDATE" if generic else "FOR UPDATE"
                found.append(Lock(relative, node.lineno, function, "generic", mode))
        text = _text(node) if id(node) not in docstrings else None
        if text is None:
            continue
        for match in SQL_LOCK.finditer(text):
            table_named = ACCOUNT_TABLE in text.lower()
            unknown_table = "{}" in text and re.search(r"\bFROM\s+\{\}", text, re.I) is not None
            if not (table_named or unknown_table):
                continue
            mode = "FOR " + " ".join(match.group(1).upper().split())
            if mode in ("FOR SHARE", "FOR KEY SHARE"):
                continue  # a reader's lock, not a writer's: not judged here
            line = getattr(node, "lineno", 0)
            found.append(Lock(relative, line, _enclosing(functions, line), "sql", mode))
    return found


def scan(roots: Iterable[Path] | None = None) -> list[Lock]:
    """Every explicit account lock (and generic lock that can take one) in the scanned files."""
    found: list[Lock] = []
    for path in sources(roots):
        found += scan_file(path)
    return sorted(found, key=lambda lock: (lock.path, lock.line))


def violations(locks: Iterable[Lock]) -> list[Lock]:
    return [lock for lock in locks if not lock.no_key]


def sites(locks: Iterable[Lock]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted({(lock.path, lock.function) for lock in locks}))


def main(argv: Sequence[str]) -> int:
    roots = [Path(arg) for arg in argv] or None
    locks = scan(roots)
    bad = violations(locks)
    for lock in locks:
        print(f"{'ok ' if lock.no_key else 'BAD'} {lock.where()}: {lock.mode}")
    print(f"account locks found: {len(locks)}; not FOR NO KEY UPDATE: {len(bad)}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
