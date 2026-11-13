"""The scan of explicit account row locks (SV3 Stage A, corrections C1 to C3; its brief's D2 and
D14; DM-61 K1, K3; DM-65, the exact-head review's F3; DM-67, C2's delta re-review's L1 and L2).

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
  call whose queryset follows a relation. Without ``OF``, PostgreSQL locks every joined row
  ``FOR UPDATE``, a joined account row included, so such a lock passes only with ``no_key=True``,
  or, on a named model, with ``of=`` naming no path to ``AppAccount`` (no entry ending in a
  foreign key to it, read from ``glow_persistence/models.py``, or in a reverse name of one of its
  own relation fields). A generic lock with a join passes only with ``no_key=True``: an ``of=``
  does not make it pass, since the model can be ``AppAccount`` (C3; L1);
- **a lock in SQL:** a string (or f-string) outside a docstring that takes ``FOR UPDATE`` (or
  ``FOR NO KEY UPDATE``, ``FOR SHARE``, ``FOR KEY SHARE``). A ``FOR UPDATE`` string passes only if
  it is complete literal text (no f-string field and no ``{...}`` format field anywhere in it, not
  formatted with ``%`` or ``.format()``, not joined to other strings) that names the table after
  ``FROM`` and after every ``JOIN`` itself, none of them the account table; any other such string
  counts as a lock of the account table and is refused (C3; L2).

**What joins** (C2, and C3's L2), in the function that holds the lock:

- a ``select_related`` or an ``extra()`` call, with any argument;
- a lookup or field path that follows a relation: a keyword's name in a lookup method
  (``filter``, ``exclude``, ``get``, ``get_or_create``, ``update_or_create``), a string argument
  of a path method (``order_by``, ``values``, ``values_list``, ``only``, ``defer``, ``distinct``,
  ``select_related``, ``latest``, ``earliest``), or a path a ``Q`` or an ``F`` names. A path
  follows a relation when its first segment is a relation field of ``glow_persistence/models.py``
  or the reverse name of one of ``AppAccount``'s own relation fields (its ``related_query_name``,
  else its ``related_name``, else ``appaccount``: today ``appaccount`` on auth's ``User``), or
  when any later segment is not one of Django's lookups or transforms (``LOOKUPS``);
- what the scan cannot read, which counts as a join: a positional argument of a lookup method,
  or any argument of an expression method (``annotate``, ``alias``, ``aggregate``), unless it is
  a literal ``Q(...)`` or ``F(...)``, or a name assigned one in the function, whose paths the scan
  then judges; a path method's argument that is not a string literal; and ``*`` or ``**``
  anywhere in the chain. A keyword's value is judged as a ``Q`` or an ``F`` where it is one or
  names one, and is otherwise a value, not a path.

A queryset is followed along its chain of calls and through every plain assignment in the
function, before and after the lock, transitively (``a = M.objects.filter(...)``,
``b = a.select_for_update()``, ``b.order_by(...)``), and so is every assignment of a name an
argument uses. So it cannot see: the joins of a queryset, or of a ``Q``, an ``F`` or another
expression, that reaches the lock from another function (a lock on such a queryset is judged as a
generic lock); an expression given as a keyword's value from outside the function; a model's
``Meta.ordering`` (none exists today); a model imported under another name (C1's rule, unchanged);
and a lock clause built at run time (such as ``FOR {mode}``). A select_for_update whose receiver
names another model (``Match``, ``Profile``, ...) and joins nothing is not an account lock and is
not judged. It prints counts and locations only.
"""

from __future__ import annotations

import ast
import re
import sys
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from functools import partial
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
API_ROOT = REPO_ROOT / "services" / "api"
REFERENCE = Path(__file__).resolve().parent / "reference.py"
MODELS = API_ROOT / "glow_persistence" / "models.py"
ACCOUNT_MODEL = "AppAccount"
ACCOUNT_TABLE = "glow_persistence_appaccount"
SKIPPED_PARTS = frozenset({".venv", "tests", "__pycache__", "migrations"})
SQL_LOCK = re.compile(r"\bFOR\s+(NO\s+KEY\s+UPDATE|UPDATE|KEY\s+SHARE|SHARE)\b", re.IGNORECASE)
# C3 (L2): where a FOR UPDATE string's FROM and JOIN must each name a table itself.
FROM_OR_JOIN = re.compile(r"\b(FROM|JOIN)\b", re.IGNORECASE)
_IDENTIFIER = r'(?:"\w+"|\w+\b)'
TABLE_AFTER = re.compile(rf"\s+{_IDENTIFIER}(?:\.{_IDENTIFIER})?(?!\s*[(\[{{%])")
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
# The queryset methods whose keyword names are lookup paths, those whose string arguments are
# field paths (``select_related`` is a join by itself), and those whose arguments are expressions
# (C3: ``latest`` and ``earliest`` take paths; ``extra()`` is a join by itself).
LOOKUP_METHODS = frozenset({"filter", "exclude", "get", "get_or_create", "update_or_create"})
PATH_METHODS = frozenset(
    {
        "order_by",
        "values",
        "values_list",
        "only",
        "defer",
        "distinct",
        "select_related",
        "latest",
        "earliest",
    }
)
EXPRESSION_METHODS = frozenset({"annotate", "alias", "aggregate"})
JOIN_METHODS = frozenset({"select_related", "extra"})
EXPRESSIONS = frozenset({"Q", "F"})
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
    """What the scan reads of ``glow_persistence/models.py``: every relation field's name, the
    names of the foreign keys (and one-to-one fields) to ``AppAccount``, and the reverse names of
    ``AppAccount``'s own relation fields (C3; L2)."""

    relations: frozenset[str]
    account_fields: frozenset[str]
    reverse: frozenset[str] = frozenset()


def _field_kind(call: ast.Call) -> str:
    func = call.func
    return func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")


def _reverse_name(call: ast.Call) -> str | None:
    """A relation field's reverse query name: its ``related_query_name``, else its
    ``related_name``, else the model's name in lower case; ``None`` for a hidden one (``+``)."""
    given = {k.arg: k.value for k in call.keywords if k.arg is not None}
    for key in ("related_query_name", "related_name"):
        if key not in given:
            continue
        value = given[key]
        if not (isinstance(value, ast.Constant) and isinstance(value.value, str)):
            raise ValueError(f"{ACCOUNT_MODEL}'s {key} is not a literal: the scan cannot read it")
        if key == "related_name" and value.value.endswith("+"):
            return None
        return value.value
    return ACCOUNT_MODEL.lower()


def read_models(path: Path = MODELS) -> Model:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    relations: set[str] = set()
    accounts: set[str] = set()
    reverse: set[str] = set()
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Assign) and isinstance(node.value, ast.Call)):
            continue
        if _field_kind(node.value) not in RELATION_FIELDS:
            continue
        names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        relations.update(names)
        target = node.value.args[0] if node.value.args else None
        named = (isinstance(target, ast.Name) and target.id == ACCOUNT_MODEL) or (
            isinstance(target, ast.Constant) and str(target.value).endswith(ACCOUNT_MODEL)
        )
        if named:
            accounts.update(names)
    for node in ast.walk(tree):
        if not (isinstance(node, ast.ClassDef) and node.name == ACCOUNT_MODEL):
            continue
        for statement in node.body:
            if (
                isinstance(statement, ast.Assign)
                and isinstance(statement.value, ast.Call)
                and _field_kind(statement.value) in RELATION_FIELDS
            ):
                name = _reverse_name(statement.value)
                if name is not None:
                    reverse.add(name)
    return Model(frozenset(relations), frozenset(accounts), frozenset(reverse))


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


def _owners(tree: ast.AST) -> dict[int, int]:
    """Each node's innermost enclosing function, by the function node's identity (0 for the
    module), so that two functions of one name keep their own variables."""
    owners: dict[int, int] = {}
    pending: list[tuple[ast.AST, int]] = [(tree, 0)]
    while pending:
        node, owner = pending.pop()
        owners[id(node)] = owner
        inner = id(node) if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) else owner
        pending += [(child, inner) for child in ast.iter_child_nodes(node)]
    return owners


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


def _literal(node: ast.AST) -> str | None:
    """A plain string literal's text (not an f-string)."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _parents(tree: ast.AST) -> dict[int, ast.AST]:
    return {id(child): node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}


def _receiver_calls(node: ast.AST) -> list[ast.Call]:
    """The calls down an expression's receiver chain, the expression itself included, through
    both branches of a conditional expression and every operand of a boolean one."""
    if isinstance(node, ast.IfExp):
        return [*_receiver_calls(node.body), *_receiver_calls(node.orelse)]
    if isinstance(node, ast.BoolOp):
        return [call for value in node.values for call in _receiver_calls(value)]
    calls: list[ast.Call] = []
    current = node
    while True:
        if isinstance(current, ast.Attribute):
            current = current.value
        elif isinstance(current, ast.Call):
            calls.append(current)
            current = current.func
        elif isinstance(current, ast.Subscript):
            current = current.value
        else:
            return calls


def _chain(call: ast.Call, parents: dict[int, ast.AST]) -> tuple[list[ast.Call], ast.AST]:
    """Every call in ``call``'s queryset chain, down its receiver and up through the calls made on
    its result, and the chain's outermost expression."""
    calls = _receiver_calls(call.func)
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


def _base_names(node: ast.AST) -> list[str]:
    """The variables an assigned value's chains start from, through a conditional or boolean
    expression's branches."""
    if isinstance(node, ast.IfExp):
        return [*_base_names(node.body), *_base_names(node.orelse)]
    if isinstance(node, ast.BoolOp):
        return [name for value in node.values for name in _base_names(value)]
    name = _base_name(node)
    return [] if name is None else [name]


def _assigned_to(node: ast.AST, parents: dict[int, ast.AST]) -> list[str]:
    """The names a chain's outermost expression is plainly assigned to, through a conditional or
    boolean expression that holds it (``query = (... if lock else ...)``)."""
    child, parent = node, parents.get(id(node))
    while isinstance(parent, ast.IfExp | ast.BoolOp) and child is not getattr(parent, "test", None):
        child, parent = parent, parents.get(id(parent))
    return _targets(parent)


def _targets(node: ast.AST | None) -> list[str]:
    if isinstance(node, ast.Assign):
        return [t.id for t in node.targets if isinstance(t, ast.Name)]
    if isinstance(node, ast.AnnAssign | ast.NamedExpr) and isinstance(node.target, ast.Name):
        return [node.target.id] if node.value is not None else []
    return []


@dataclass
class _Function:
    """One file's plain assignments and calls, by enclosing function (C3; L2): each name's
    assigned values, the calls made on a chain that starts from each name, and the names assigned
    from such a chain."""

    assigned: dict[tuple[int, str], list[ast.expr]]
    calls_on: dict[tuple[int, str], list[ast.Call]]
    derived: dict[tuple[int, str], list[str]]


def _read_functions(tree: ast.AST, owners: dict[int, int]) -> _Function:
    assigned: dict[tuple[int, str], list[ast.expr]] = {}
    calls_on: dict[tuple[int, str], list[ast.Call]] = {}
    derived: dict[tuple[int, str], list[str]] = {}
    for node in ast.walk(tree):
        owner = owners.get(id(node), 0)
        value = getattr(node, "value", None)
        targets = _targets(node) if isinstance(value, ast.expr) else []
        if targets and isinstance(value, ast.expr):
            for name in targets:
                assigned.setdefault((owner, name), []).append(value)
            for base in _base_names(value):
                derived.setdefault((owner, base), []).extend(targets)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            receiver = _base_name(node.func.value)
            if receiver is not None:
                calls_on.setdefault((owner, receiver), []).append(node)
    return _Function(assigned, calls_on, derived)


def _group(
    lock: ast.Call, owner: int, parents: dict[int, ast.AST], functions: _Function
) -> list[ast.Call]:
    """Every call on the lock's queryset in its function: its chain, then, transitively, the
    chains of every variable its receiver was assigned from and of every variable assigned from
    it, before and after the lock."""
    chain, top = _chain(lock, parents)
    found = list(chain)
    backward: set[str] = set()
    pending = _base_names(lock.func)
    while pending:
        name = pending.pop()
        if name in backward:
            continue
        backward.add(name)
        for value in functions.assigned.get((owner, name), []):
            found += _receiver_calls(value)
            pending += _base_names(value)
    forward: set[str] = set()
    pending = _assigned_to(top, parents)
    while pending:
        name = pending.pop()
        if name in forward:
            continue
        forward.add(name)
        found += functions.calls_on.get((owner, name), [])
        pending += functions.derived.get((owner, name), [])
    return list({id(call): call for call in found}.values())


def _assigned_in(functions: _Function, owner: int, name: str) -> list[ast.expr]:
    return functions.assigned.get((owner, name), [])


def _follows(path: str, model: Model) -> bool:
    """Whether a lookup or field path follows a relation (C2; DM-65; C3's reverse names)."""
    segments = path.lstrip("-?").split("__")
    if segments[0] in model.reverse:
        return True
    if len(segments) < 2:
        return False
    return segments[0] in model.relations or any(s not in LOOKUPS for s in segments[1:])


def _expression_name(node: ast.AST) -> str:
    return _field_kind(node) if isinstance(node, ast.Call) else ""


class _Paths:
    """The paths a ``Q`` or an ``F`` names, read in the lock's function (C3; L2): ``None`` stands
    for one the scan cannot read, which counts as a join."""

    def __init__(self, assigned: Callable[[str], list[ast.expr]]) -> None:
        self.assigned = assigned

    def expression(self, node: ast.AST, seen: frozenset[str] = frozenset()) -> list[str | None]:
        """An argument that must be a literal ``Q(...)`` or ``F(...)``, or a name assigned one in
        the function: its paths, or ``[None]`` for anything else."""
        if isinstance(node, ast.Call) and _expression_name(node) in EXPRESSIONS:
            return self.literal(node, seen)
        if isinstance(node, ast.Name) and node.id not in seen:
            values = self.assigned(node.id)
            held = [v for v in values if isinstance(v, ast.Call)]
            if values and len(held) == len(values):
                if all(_expression_name(v) in EXPRESSIONS for v in held):
                    return [path for v in held for path in self.literal(v, seen | {node.id})]
        return [None]

    def literal(self, call: ast.Call, seen: frozenset[str]) -> list[str | None]:
        found: list[str | None] = []
        if any(isinstance(a, ast.Starred) for a in call.args) or any(
            k.arg is None for k in call.keywords
        ):
            found.append(None)
        if _expression_name(call) == "F":
            found.append(_literal(call.args[0]) if call.args else None)
            return found
        for keyword in call.keywords:
            if keyword.arg is not None:
                found.append(keyword.arg)
                found += self.values(keyword.value, seen)
        for arg in call.args:
            if isinstance(arg, ast.Starred):
                continue
            if isinstance(arg, ast.Tuple) and len(arg.elts) == 2 and _literal(arg.elts[0]):
                found.append(_literal(arg.elts[0]))
                found += self.values(arg.elts[1], seen)
            else:
                found += self.expression(arg, seen)
        return found

    def values(self, node: ast.AST, seen: frozenset[str] = frozenset()) -> list[str | None]:
        """A keyword's value: a value, but for the paths of every ``Q`` or ``F`` in it or in a
        name it uses, through that name's assignments in the function."""
        found: list[str | None] = []
        for inner in ast.walk(node):
            if isinstance(inner, ast.Call) and _expression_name(inner) in EXPRESSIONS:
                found += self.literal(inner, seen)
            elif isinstance(inner, ast.Name) and inner.id not in seen:
                for value in self.assigned(inner.id):
                    found += self.values(value, seen | {inner.id})
        return found


def _joins(calls: Iterable[ast.Call], model: Model, paths: _Paths) -> list[str]:
    """What, in a queryset's calls, joins another table: a ``select_related`` or an ``extra()``,
    a lookup or field path that follows a relation, or what the scan cannot read."""
    found: list[str] = []
    for call in calls:
        method = call.func.attr if isinstance(call.func, ast.Attribute) else ""
        args = [a for a in call.args if not isinstance(a, ast.Starred)]
        keywords = [k for k in call.keywords if k.arg is not None]
        if len(args) < len(call.args) or len(keywords) < len(call.keywords):
            found.append(f"{method}: * or ** arguments")
        if method in JOIN_METHODS:
            found.append(method)
            continue
        judged: list[str | None] = []
        if method in LOOKUP_METHODS:
            for keyword in keywords:
                if keyword.arg not in NOT_PATHS:
                    judged.append(keyword.arg)
                judged += paths.values(keyword.value)
            for arg in args:
                judged += paths.expression(arg)
        elif method in EXPRESSION_METHODS:
            for value in [*args, *(k.value for k in keywords)]:
                judged += paths.expression(value)
        elif method in PATH_METHODS:
            judged += [_literal(arg) for arg in args]
            judged += [None for k in keywords if k.arg not in NOT_PATHS]
        for path in judged:
            if path is None:
                found.append(f"{method}: an argument the scan cannot read")
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
    accounts = model.account_fields | model.reverse
    if any(entry.split("__")[-1] in accounts for entry in named):
        return None
    return named


def _complete(node: ast.AST, parents: dict[int, ast.AST]) -> bool:
    """Whether a string is complete literal text (C3; L2): a plain literal, not formatted with
    ``%`` or ``.format()`` and not joined to other strings."""
    if not isinstance(node, ast.Constant):
        return False
    child: ast.AST = node
    parent = parents.get(id(node))
    while isinstance(parent, ast.Tuple | ast.List | ast.Set | ast.Starred):
        child, parent = parent, parents.get(id(parent))
    if isinstance(parent, ast.BinOp | ast.AugAssign) and isinstance(parent.op, ast.Add | ast.Mod):
        return False
    if isinstance(parent, ast.Attribute) and parent.attr in {"format", "format_map", "join"}:
        return False
    if (
        isinstance(parent, ast.Call)
        and isinstance(parent.func, ast.Attribute)
        and parent.func.attr in {"format", "format_map", "join"}
        and child is not parent.func
    ):
        return False
    return not isinstance(parent, ast.FormattedValue | ast.JoinedStr)


def names_its_tables(text: str) -> bool:
    """Whether a lock's SQL names the table after ``FROM`` and after every ``JOIN`` itself, none
    of them the account table, with no ``{...}`` format field anywhere in it (C3; L2)."""
    if "{" in text or "}" in text or ACCOUNT_TABLE in text.lower():
        return False
    keywords = list(FROM_OR_JOIN.finditer(text))
    if not any(match.group(1).upper() == "FROM" for match in keywords):
        return False
    return all(TABLE_AFTER.match(text, match.end()) is not None for match in keywords)


def scan_file(path: Path, model: Model | None = None) -> list[Lock]:
    model = model if model is not None else read_models()
    tree = ast.parse(path.read_text(encoding="utf-8"))
    relative = _relative(path)
    functions = _functions(tree)
    docstrings = _docstrings(tree)
    parents = _parents(tree)
    owners = _owners(tree)
    read = _read_functions(tree, owners)
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
            owner = owners.get(id(node), 0)
            paths = _Paths(partial(_assigned_in, read, owner))
            calls = _group(node, owner, parents, read)
            joins = tuple(dict.fromkeys(_joins(calls, model, paths)))
            of = _of(node, model)
            if ACCOUNT_MODEL in names:
                mode = "FOR NO KEY UPDATE" if expression == "True" else "FOR UPDATE"
                found.append(Lock(relative, node.lineno, function, "orm", mode, joins))
            elif variable and not any(name[:1].isupper() for name in names):
                # C3 (L1): with a join, only no_key=True passes; an of= does not.
                generic = expression == "True" or (
                    not joins and ACCOUNT_MODEL in expression and " is " in expression
                )
                mode = "FOR NO KEY UPDATE" if generic else "FOR UPDATE"
                found.append(Lock(relative, node.lineno, function, "generic", mode, joins))
            elif joins:
                mode = "FOR NO KEY UPDATE" if expression == "True" else "FOR UPDATE"
                if mode == "FOR UPDATE" and of is not None:
                    mode = "FOR UPDATE OF " + ", ".join(of)
                found.append(Lock(relative, node.lineno, function, "join", mode, joins))
        if id(node) in docstrings or isinstance(parents.get(id(node)), ast.JoinedStr):
            continue
        text = _text(node)
        if text is None:
            continue
        for match in SQL_LOCK.finditer(text):
            mode = "FOR " + " ".join(match.group(1).upper().split())
            if mode in ("FOR SHARE", "FOR KEY SHARE"):
                continue  # a reader's lock, not a writer's: not judged here
            if _complete(node, parents) and names_its_tables(text):
                continue  # complete literal text naming its tables, none the account table
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
