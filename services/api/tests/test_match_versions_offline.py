"""SV4 A1 (its brief's D6; the P11 plan's C2-X2): a match's ``version``, which
``MatchProjection.version`` serves, and its ``contact_version``, which a send carries as
``SendCommand.contact_version`` (``MessageIntent.meta.expected_version``), start at 1 and are
advanced together, by every writer of either, and only when contact ends: today ``glow_chat``'s
``block`` (of an active match) and ``unmatch``. So the version a participant reads is the one a
send expects, and while contact continues it cannot rise.

Read from the source and never run: in each module of the API's code (its tests, migrations and
virtual environment left out), a detector reads the top-level ``def`` functions and the ``def``
methods of top-level classes, anything nested in one (an ``async def`` or a class among them)
being read as part of it. In those it finds these forms of a write to either field of a match:
an assignment to an object's ``contact_version``; an assignment to the ``version`` of a name
bound to a ``Match`` or a queryset of them (assigned from ``Match.objects...`` or
``self._lock(Match, ...)``, looped over, or a parameter annotated ``Match``); a ``save`` of such
an object naming either field; a writing queryset or manager call (``update``, ``create``,
``bulk_update`` and the rest) on one, naming either; or SQL text that writes
``glow_persistence_match``. ``WriterDetectorTests`` shows each of these forms is found but the
``save``, whose one example also assigns ``version``; the ``save`` is held instead by
``MatchVersionTests``' check that each pinned writer saves both fields in one ``save``.

Other forms escape it, among them: a function it does not read (a top-level ``async def``
function, an ``async def`` method of a top-level class, or any method of a class nested in a
top-level class); a related manager's ``update``, or an ``aupdate``; a
``Match(..., version=...)``, or a ``bulk_create`` of such objects; SQL text whose table name is
built at runtime or held in a constant; an assignment to the ``version`` of a match obtained
through a helper such as ``glow_discovery.interactions._pair_match``, or made in a ``save()``
override or a signal (an assignment to an object's ``contact_version`` is found however the
object was obtained); and ``Match`` imported under another name. So the pinned set below is
today's every writer by the A1 review's and the manager's searches of the code, not by the
detector alone; the detector's reach is carried (the carried-items file, "Carried to SV4"; the
exact-head review's AR-4). Each function the detector finds must be one of the pinned writers,
and each advances both by one in the same statement list and saves both in one ``save``. The
database case is the discovery suite's ``sv4.a1.match_version_is_the_sends_contact_version``.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1]
LEFT_OUT = {"tests", ".venv", "migrations", "__pycache__"}
FIELDS = ("version", "contact_version")
# Every writer of either field, by module and qualified name.
WRITERS = {
    ("glow_chat/contact.py", "OrmContactPersistence.block"),
    ("glow_chat/contact.py", "OrmContactPersistence.unmatch"),
}


def sources() -> list[Path]:
    return sorted(
        path
        for path in API_ROOT.rglob("*.py")
        if not LEFT_OUT & set(path.relative_to(API_ROOT).parts)
    )


def functions(tree: ast.Module) -> dict[str, ast.FunctionDef]:
    """Every top-level function and method, by its qualified name; nested bodies are inside."""
    found: dict[str, ast.FunctionDef] = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            found[node.name] = node
        elif isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    found[f"{node.name}.{item.name}"] = item
    return found


def names_match(node: ast.AST) -> bool:
    return any(isinstance(n, ast.Name) and n.id == "Match" for n in ast.walk(node))


def match_names(function: ast.FunctionDef) -> set[str]:
    """The names a function binds to a ``Match`` or a queryset of them: an assignment (plain,
    annotated or ``:=``) of an expression naming ``Match``, a loop over one, and a parameter
    annotated with it; each name followed through plain assignments of a bound name."""
    bound: set[str] = set()
    for argument in (*function.args.args, *function.args.kwonlyargs, *function.args.posonlyargs):
        if argument.annotation is not None and names_match(argument.annotation):
            bound.add(argument.arg)
    changed = True
    while changed:
        changed = False
        for node in ast.walk(function):
            targets: list[ast.expr] = []
            value: ast.AST | None = None
            if isinstance(node, ast.Assign):
                targets, value = list(node.targets), node.value
            elif isinstance(node, ast.AnnAssign | ast.NamedExpr):
                targets, value = [node.target], node.value
            elif isinstance(node, ast.For | ast.comprehension):
                targets, value = [node.target], node.iter
            if value is None:
                continue
            uses = names_match(value) or any(
                isinstance(n, ast.Name) and n.id in bound for n in ast.walk(value)
            )
            if not uses:
                continue
            for target in targets:
                for name in ast.walk(target):
                    if isinstance(name, ast.Name) and name.id not in bound:
                        bound.add(name.id)
                        changed = True
    return bound


def assigned(node: ast.AST) -> list[ast.Attribute]:
    targets: list[ast.expr] = []
    if isinstance(node, ast.Assign):
        targets = list(node.targets)
    elif isinstance(node, ast.AugAssign | ast.AnnAssign):
        targets = [node.target]
    return [t for t in targets if isinstance(t, ast.Attribute)]


def saved_fields(call: ast.Call) -> set[str]:
    for keyword in call.keywords:
        if keyword.arg == "update_fields" and isinstance(keyword.value, ast.List | ast.Tuple):
            return {
                e.value
                for e in keyword.value.elts
                if isinstance(e, ast.Constant) and isinstance(e.value, str)
            }
    return set()


# The queryset and manager methods that write a row's fields.
WRITING_METHODS = {
    "update",
    "create",
    "bulk_create",
    "bulk_update",
    "get_or_create",
    "update_or_create",
}


def named_fields(call: ast.Call) -> set[str]:
    """The match's fields a writing call names: as keywords, in a ``defaults`` mapping, or as
    string constants among its arguments (``bulk_update``'s field list)."""
    found = {k.arg for k in call.keywords if k.arg in FIELDS}
    for node in ast.walk(call):
        if isinstance(node, ast.Constant) and node.value in FIELDS:
            found.add(str(node.value))
    return found


def writes(function: ast.FunctionDef) -> list[str]:
    """What the function writes of a match's two fields, as readable lines."""
    bound = match_names(function)
    found: list[str] = []
    for node in ast.walk(function):
        for target in assigned(node):
            owner = target.value.id if isinstance(target.value, ast.Name) else None
            if target.attr == "contact_version" or (target.attr == "version" and owner in bound):
                found.append(ast.unparse(node))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            receiver = node.func.value
            on_match = names_match(receiver) or any(
                isinstance(n, ast.Name) and n.id in bound for n in ast.walk(receiver)
            )
            if node.func.attr == "save" and isinstance(receiver, ast.Name) and receiver.id in bound:
                if saved_fields(node) & set(FIELDS):
                    found.append(ast.unparse(node))
            if node.func.attr in WRITING_METHODS and on_match and named_fields(node):
                found.append(ast.unparse(node))
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            text = node.value.lower()
            if "glow_persistence_match" in text and ("update" in text or "insert" in text):
                found.append(node.value)
    return found


def statement_lists(function: ast.FunctionDef) -> list[list[ast.stmt]]:
    lists: list[list[ast.stmt]] = []
    for node in ast.walk(function):
        for name in ("body", "orelse", "finalbody"):
            block = getattr(node, name, None)
            if isinstance(block, list) and block and isinstance(block[0], ast.stmt):
                lists.append(block)
    return lists


class MatchVersionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.found: dict[tuple[str, str], tuple[ast.FunctionDef, list[str]]] = {}
        for path in sources():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for name, function in functions(tree).items():
                lines = writes(function)
                if lines:
                    key = (path.relative_to(API_ROOT).as_posix(), name)
                    self.found[key] = (function, lines)

    def test_both_fields_start_at_one(self) -> None:
        tree = ast.parse((API_ROOT / "glow_persistence" / "models.py").read_text(encoding="utf-8"))
        classes = {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)}

        def default(class_name: str, field: str) -> object:
            for node in classes[class_name].body:
                if isinstance(node, ast.Assign) and [ast.unparse(t) for t in node.targets] == [
                    field
                ]:
                    assert isinstance(node.value, ast.Call)
                    for keyword in node.value.keywords:
                        if keyword.arg == "default":
                            return ast.literal_eval(keyword.value)
            return None

        self.assertEqual([ast.unparse(b) for b in classes["Match"].bases], ["Record"])
        self.assertEqual(default("Record", "version"), 1)
        self.assertEqual(default("Match", "contact_version"), 1)

    def test_the_writers_of_either_field_are_the_pinned_ones(self) -> None:
        self.assertEqual(set(self.found), WRITERS, {k: v[1] for k, v in self.found.items()})

    def test_each_writer_advances_both_by_one_and_saves_both(self) -> None:
        for key in sorted(WRITERS):
            with self.subTest(writer=key):
                function, _ = self.found[key]
                together = []
                for block in statement_lists(function):
                    text = [ast.unparse(s) for s in block]
                    if "match.contact_version += 1" in text:
                        together.append(text)
                self.assertEqual(len(together), 1, together)
                text = together[0]
                at = text.index("match.contact_version += 1")
                self.assertEqual(text[at + 1], "match.version += 1")
                save = text[at + 2]
                self.assertTrue(save.startswith("match.save(update_fields="), save)
                self.assertIn("'contact_version'", save)
                self.assertIn("'version'", save)
                # No other write of either field anywhere in the writer.
                self.assertEqual(
                    sorted(self.found[key][1]),
                    sorted(["match.contact_version += 1", "match.version += 1", save]),
                )


class WriterDetectorTests(unittest.TestCase):
    """The detector itself (the exact-head review lens of A1's own review): each form the module's
    docstring lists as found is found, but the ``save``, whose one example also assigns
    ``version``; ``MatchVersionTests`` holds the ``save``, by its check that each pinned writer
    saves both fields. It shows nothing of the forms that escape (AR-4)."""

    FORMS = {
        "an attribute of a locked match": (
            "def f(self, pk):\n    match = self._lock(Match, pk)\n    match.version += 1\n"
        ),
        "a loop over matches": (
            "def f():\n    for match in Match.objects.filter(state='active'):\n"
            "        match.version += 1\n        match.save(update_fields=['version'])\n"
        ),
        "a parameter annotated as a match": ("def f(match: Match):\n    match.version = 3\n"),
        "a queryset update through a variable": (
            "def f():\n    rows = Match.objects.filter(state='active')\n"
            "    rows.update(version=F('version') + 1)\n"
        ),
        "a create with an explicit version": (
            "def f(a, b):\n"
            "    Match.objects.create(account_low_id=a, account_high_id=b, version=2)\n"
        ),
        "a bulk update naming the field": (
            "def f(rows):\n    Match.objects.bulk_update(rows, ['contact_version'])\n"
        ),
        "raw SQL": (
            "def f(cursor):\n"
            "    cursor.execute('UPDATE glow_persistence_match SET version = version + 1')\n"
        ),
        "a contact version on any object": ("def f(row):\n    row.contact_version = 5\n"),
    }

    def test_each_form_of_a_writer_is_found(self) -> None:
        for label, source in self.FORMS.items():
            with self.subTest(form=label):
                function = ast.parse(source).body[0]
                assert isinstance(function, ast.FunctionDef)
                self.assertTrue(writes(function), label)

    def test_reads_and_other_rows_are_not_writers(self) -> None:
        source = (
            "def f(self, pk, row):\n"
            "    match = self._lock(Match, pk)\n"
            "    if match.version != 1:\n        return match.contact_version\n"
            "    row.version += 1\n    row.save(update_fields=['version'])\n"
            "    Block.objects.filter(pk=pk).update(version=2)\n"
        )
        function = ast.parse(source).body[0]
        assert isinstance(function, ast.FunctionDef)
        self.assertEqual(writes(function), [])


if __name__ == "__main__":
    unittest.main()
