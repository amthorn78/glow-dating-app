"""The scan of explicit account row locks (SV3 Stage A, corrections C1 and C2; its brief's D2 and
D14; DM-61 K1, K3; DM-65, the exact-head review's F3).

Every explicit lock of an ``AppAccount`` row, in ``services/api`` (its tests and virtual
environment left out) and in the ordering proof's reference design (``reference.py``), must be
``FOR NO KEY UPDATE``: it excludes every other writer and every ``FOR SHARE`` reader, but not the
``FOR KEY SHARE`` PostgreSQL's foreign-key check takes, so no write that references another
member's account waits on that member's writers and no lock cycle forms through one (Codex's CX1).

It reads the source, never imports it, and finds four kinds of lock:

- **an ORM lock of the account:** a ``select_for_update(...)`` call whose receiver names
  ``AppAccount``; it must pass ``no_key=True``;
- **a generic ORM lock:** a ``select_for_update(...)`` call on a model held in a variable (a
  helper such as ``glow_chat``'s ``_lock`` or the reference design's), which can lock an account;
  it must pass a ``no_key`` that names ``AppAccount`` (``no_key=model is AppAccount``) or is
  ``True``;
- **a lock of a queryset that joins another table** (C2; DM-65): a ``select_for_update(...)``
  call whose queryset follows a relation, through ``select_related`` or a lookup or field path
  (in ``filter``, ``exclude``, ``get``, ``order_by``, ``values``, the other path-taking methods,
  a ``Q`` or an ``F``). Without ``OF``, PostgreSQL locks every joined row ``FOR UPDATE``, a joined
  account row included, so such a lock passes only with ``no_key=True``, or with ``of=`` naming no
  path to ``AppAccount`` (no entry ending in a foreign key to it, read from
  ``glow_persistence/models.py``). It applies to a generic lock with a join as well, whose
  ``no_key`` must then be ``True``. A path follows a relation when its first segment is a relation
  field of ``glow_persistence/models.py``, or when any later segment is not one of Django's
  lookups or transforms (``LOOKUPS``); a path the scan cannot read (one built at run time, or
  ``**`` arguments) counts as a join;
- **a lock in SQL:** a string (or f-string) outside a docstring that takes ``FOR UPDATE`` (or
  ``FOR NO KEY UPDATE``, ``FOR SHARE``, ``FOR KEY SHARE``) and names the account table, or names
  no table it can read (a ``{table}`` placeholder); a ``FOR UPDATE`` there is refused.

A queryset is followed along its chain of calls and through a plain variable assigned in the same
function (``rows = Model.objects.select_for_update(); rows.filter(...)``); a queryset passed
between functions is not. A select_for_update whose receiver names another model (``Match``,
``Profile``, ...) and joins nothing is not an account lock and is not judged. It prints counts
and locations only.
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
MODELS = API_ROOT / "glow_persistence" / "models.py"
ACCOUNT_MODEL = "AppAccount"
ACCOUNT_TABLE = "glow_persistence_appaccount"
SKIPPED_PARTS = frozenset({".venv", "tests", "__pycache__", "migrations"})
SQL_LOCK = re.compile(r"\bFOR\s+(NO\s+KEY\s+UPDATE|UPDATE|KEY\s+SHARE|SHARE)\b", re.IGNORECASE)
RELATION_FIELDS = frozenset({"ForeignKey", "OneToOneField", "ManyToManyField"})
# The segments a lookup path can end in without following a relation: Django's built-in lookups,
# its date and time transforms, and PostgreSQL's. Any other segment after the first follows one
# (C2; DM-65).
LOOKUPS = frozenset(
    {
        "exact", "iexact", "contains", "icontains", "in", "gt", "gte", "lt", "lte",
        "startswith", "istartswith", "endswith", "iendswith", "range", "isnull", "regex",
        "iregex", "date", "year", "iso_year", "month", "day", "week", "week_day",
        "iso_week_day", "quarter", "time", "hour", "minute", "second", "contained_by",
        "overlap", "has_key", "has_keys", "has_any_keys", "len", "search", "trigram_similar",
        "unaccent", "lower", "upper",
    }
)  # fmt: skip
# The queryset methods whose keyword names are lookup paths, and those whose string arguments are
# field paths (``select_related`` is a join by itself).
LOOKUP_METHODS = frozenset({"filter", "exclude", "get", "get_or_create", "update_or_create"})
PATH_METHODS = frozenset(
    {"order_by", "values", "values_list", "only", "defer", "distinct", "select_related"}
)
EXPRESSION_METHODS = frozenset({"annotate", "alias", "aggregate"})
NOT_PATHS = frozenset({"defaults", "create_defaults", "flat", "named"})
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
    kind: str  # "orm", "generic", "join" or "sql"
    mode: str  # "FOR NO KEY UPDATE", "FOR UPDATE", "FOR UPDATE OF <entries>", ...
    joins: tuple[str, ...] = ()  # what joins another table, for a lock that does

    @property
    def no_key(self) -> bool:
        """Whether the lock passes: ``FOR NO KEY UPDATE``, or ``OF`` naming no account path."""
        return self.mode == "FOR NO KEY UPDATE" or self.mode.startswith("FOR UPDATE OF ")

    def where(self) -> str:
        joined = f", joins {len(self.joins)}" if self.joins else ""
        return f"{self.path}:{self.line} ({self.function}, {self.kind}{joined})"


@dataclass(frozen=True)
class Model:
    """What the scan reads of ``glow_persistence/models.py``: every relation field's name, and the
    names of the foreign keys (and one-to-one fields) to ``AppAccount``."""

    relations: frozenset[str]
    account_fields: frozenset[str]


def read_models(path: Path = MODELS) -> Model:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    relations: set[str] = set()
    accounts: set[str] = set()
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Assign) and isinstance(node.value, ast.Call)):
            continue
        func = node.value.func
        kind = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
        if kind not in RELATION_FIELDS:
            continue
        names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        relations.update(names)
        target = node.value.args[0] if node.value.args else None
        named = (isinstance(target, ast.Name) and target.id == ACCOUNT_MODEL) or (
            isinstance(target, ast.Constant) and str(target.value).endswith(ACCOUNT_MODEL)
        )
        if named:
            accounts.update(names)
    return Model(frozenset(relations), frozenset(accounts))


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


def _parents(tree: ast.AST) -> dict[int, ast.AST]:
    return {id(child): node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}


def _chain(call: ast.Call, parents: dict[int, ast.AST]) -> tuple[list[ast.Call], ast.AST]:
    """Every call in ``call``'s queryset chain, down its receiver and up through the calls made on
    its result, and the chain's outermost expression."""
    calls: list[ast.Call] = []
    current: ast.AST = call.func
    while True:
        if isinstance(current, ast.Attribute):
            current = current.value
        elif isinstance(current, ast.Call):
            calls.append(current)
            current = current.func
        elif isinstance(current, ast.Subscript):
            current = current.value
        else:
            break
    top: ast.AST = call
    while True:
        attribute = parents.get(id(top))
        caller = parents.get(id(attribute)) if attribute is not None else None
        if (
            isinstance(attribute, ast.Attribute)
            and attribute.value is top
            and isinstance(caller, ast.Call)
            and caller.func is attribute
        ):
            calls.append(caller)
            top = caller
        else:
            break
    return [call, *calls], top


def _base_name(node: ast.AST) -> str | None:
    """The variable a chain of calls starts from, if it starts from one."""
    current = node
    while True:
        if isinstance(current, ast.Attribute):
            current = current.value
        elif isinstance(current, ast.Call):
            current = current.func
        elif isinstance(current, ast.Subscript):
            current = current.value
        elif isinstance(current, ast.Name):
            return current.id
        else:
            return None


def _follows(path: str, model: Model) -> bool:
    """Whether a lookup or field path follows a relation (C2; DM-65)."""
    segments = path.lstrip("-?").split("__")
    if len(segments) < 2:
        return False
    return segments[0] in model.relations or any(s not in LOOKUPS for s in segments[1:])


def _expression_paths(node: ast.AST) -> list[str | None]:
    """The paths a ``Q`` or an ``F`` inside ``node`` names (``None`` for one the scan cannot
    read)."""
    found: list[str | None] = []
    for inner in ast.walk(node):
        if not isinstance(inner, ast.Call):
            continue
        func = inner.func
        name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
        if name == "Q":
            found += [k.arg for k in inner.keywords]
            for arg in inner.args:
                if isinstance(arg, ast.Tuple) and arg.elts:
                    found.append(_text(arg.elts[0]))
        elif name == "F":
            found += [_text(arg) for arg in inner.args[:1]]
    return found


def _joins(calls: Iterable[ast.Call], model: Model) -> list[str]:
    """What, in a queryset's calls, joins another table: a ``select_related``, or a lookup or field
    path that follows a relation, or one the scan cannot read."""
    found: list[str] = []
    for call in calls:
        method = call.func.attr if isinstance(call.func, ast.Attribute) else ""
        paths: list[str | None] = []
        if method == "select_related":
            found.append("select_related")
            continue
        if method in LOOKUP_METHODS:
            paths += [k.arg for k in call.keywords if k.arg not in NOT_PATHS]
        if method in PATH_METHODS:
            paths += [_text(arg) for arg in call.args]
            paths += [None for k in call.keywords if k.arg is None]
        if method in EXPRESSION_METHODS:
            for value in [*call.args, *(k.value for k in call.keywords)]:
                for inner in ast.walk(value):
                    if isinstance(inner, ast.Call):
                        paths += [_text(a) for a in inner.args if _text(a) is not None]
        if method in LOOKUP_METHODS | PATH_METHODS | EXPRESSION_METHODS:
            for value in [*call.args, *(k.value for k in call.keywords)]:
                paths += _expression_paths(value)
        for path in paths:
            if path is None:
                found.append(f"{method}: a path the scan cannot read")
            elif _follows(path, model):
                found.append(f"{method}: {path}")
    return found


def _of(call: ast.Call, model: Model) -> tuple[str, ...] | None:
    """``of=``'s entries if every one is a constant naming no path to ``AppAccount``; else
    ``None``."""
    value = next((k.value for k in call.keywords if k.arg == "of"), None)
    if not isinstance(value, ast.Tuple | ast.List) or not value.elts:
        return None
    entries = [_text(element) for element in value.elts]
    if any(entry is None for entry in entries):
        return None
    named = tuple(str(entry) for entry in entries)
    if any(entry.split("__")[-1] in model.account_fields for entry in named):
        return None
    return named


def scan_file(path: Path, model: Model | None = None) -> list[Lock]:
    model = model if model is not None else read_models()
    tree = ast.parse(path.read_text(encoding="utf-8"))
    relative = _relative(path)
    functions = _functions(tree)
    docstrings = _docstrings(tree)
    parents = _parents(tree)
    # Within a function, a queryset held in a plain variable: its chain is followed through it.
    held: dict[tuple[str, str], list[ast.Call]] = {}
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and isinstance(node.value, ast.Call)
        ):
            first = node.value
            chain, _ = _chain(first, parents)
            key = (_enclosing(functions, node.lineno), node.targets[0].id)
            held.setdefault(key, []).extend(chain)
    used: dict[tuple[str, str], list[ast.Call]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            base = _base_name(node.func.value)
            if base is not None:
                key = (_enclosing(functions, node.lineno), base)
                used.setdefault(key, []).append(node)
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
            calls, top = _chain(node, parents)
            base = _base_name(node.func.value)
            if base is not None:
                calls += held.get((function, base), [])
            owner = parents.get(id(top))
            if (
                isinstance(owner, ast.Assign)
                and len(owner.targets) == 1
                and isinstance(owner.targets[0], ast.Name)
            ):
                calls += used.get((function, owner.targets[0].id), [])
            joins = tuple(dict.fromkeys(_joins(calls, model)))
            of = _of(node, model)
            if ACCOUNT_MODEL in names:
                mode = "FOR NO KEY UPDATE" if expression == "True" else "FOR UPDATE"
                found.append(Lock(relative, node.lineno, function, "orm", mode, joins))
            elif variable and not any(name[:1].isupper() for name in names):
                generic = expression == "True" or (
                    not joins and ACCOUNT_MODEL in expression and " is " in expression
                )
                mode = "FOR NO KEY UPDATE" if generic else "FOR UPDATE"
                if not generic and joins and of is not None:
                    mode = "FOR UPDATE OF " + ", ".join(of)
                found.append(Lock(relative, node.lineno, function, "generic", mode, joins))
            elif joins:
                mode = "FOR NO KEY UPDATE" if expression == "True" else "FOR UPDATE"
                if mode == "FOR UPDATE" and of is not None:
                    mode = "FOR UPDATE OF " + ", ".join(of)
                found.append(Lock(relative, node.lineno, function, "join", mode, joins))
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


def calls(roots: Iterable[Path] | None = None) -> tuple[int, int]:
    """How many ``select_for_update`` calls the scanned files make, and how many of them lock a
    queryset that joins another table (judged or not)."""
    model = read_models()
    total = joined = 0
    for path in sources(roots):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        total += sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "select_for_update"
        )
        joined += sum(1 for lock in scan_file(path, model) if lock.joins)
    return total, joined


def scan(roots: Iterable[Path] | None = None) -> list[Lock]:
    """Every explicit account lock (and generic lock that can take one) in the scanned files."""
    model = read_models()
    found: list[Lock] = []
    for path in sources(roots):
        found += scan_file(path, model)
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
        for join in lock.joins:
            print(f"    joins through {join}")
    total, joined = calls(roots)
    print(f"select_for_update calls read: {total}; locking a queryset that joins: {joined}")
    print(f"account locks found: {len(locks)}; not FOR NO KEY UPDATE: {len(bad)}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
