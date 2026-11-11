"""SV2 Stage B: D19, one pointer order in every transaction (the brief's D19; DM-56 V5; DM-57 U8),
the parts that need no database.

- ``settings_store`` records each transaction's held pointers and refuses a lock on a pointer that
  sorts before one already held, unless it is itself held: ``PointerOrderError``, a programming
  error and never a ``Refused``, which ``tx.run`` rolls back and answers ``provider_unavailable``
  (retryable, the error's type as the internal reason), never as a member's refusal;
- a publication records its own pointer as held before its lock and before any pointer it reads;
- nothing outside ``settings_store`` locks a ``PolicyRevision`` row, in the API or the proof;
  and (correction C2, F2) nothing outside ``settings_store`` and the model mentions the model or
  its table at all, but the proof's read-only mentions, each named by function and line.

The profile suite runs every case under the check on the disposable PostgreSQL.
"""

import ast
import unittest
from pathlib import Path

from tests.test_profiles_offline import API_ROOT, last_json, under_profile_settings

REPOSITORY = API_ROOT.parents[1]
# Where application code lives: every package of the API, and the proof that drives it.
SCANNED = (API_ROOT, REPOSITORY / "proofs" / "postgres-ordering")
SETTINGS_STORE = API_ROOT / "glow_profiles" / "settings_store.py"
LOCK_WORDS = ("for share", "for update", "for no key update", "for key share")

HARNESS = """
import json
from contextlib import nullcontext
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest import mock
from uuid import uuid4

from glow_domain import profile_settings as ps
from glow_profiles import settings_store, tx as txmod
from glow_profiles.settings_store import PointerOrderError, Setting
from glow_profiles.tx import Refused, Result

class Cursor:
    def __init__(self):
        self.locked = []
        self.row = None
    def execute(self, sql, params=None):
        if "pg_backend_pid" in sql:
            self.row = (4242, datetime.now(UTC))
        elif "clock_timestamp" in sql:
            self.row = (datetime.now(UTC),)
        else:
            self.locked.append(params[0])
            self.row = (uuid4(), f"{params[0]}.v1", uuid4())
    def fetchone(self):
        return self.row

cursor = Cursor()
connection = SimpleNamespace(in_atomic_block=False, get_autocommit=lambda: True,
                             cursor=lambda: cursor)
seen_txs = []

class RecordingTx(txmod.Tx):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        seen_txs.append(self)

def fake_setting(name, pointer_id, policy_version, artifact_ref):
    return Setting(name, 1, policy_version, {}, artifact_ref, pointer_id)

patches = [
    mock.patch.object(txmod, "connection", connection),
    mock.patch.object(txmod.transaction, "atomic", lambda durable: nullcontext()),
    mock.patch.object(txmod, "Tx", RecordingTx),
    mock.patch.object(settings_store, "_setting", fake_setting),
]
for patch in patches:
    patch.start()
"""


class PointerOrderCheckTests(unittest.TestCase):
    def test_a_lock_out_of_order_is_an_internal_error_answered_provider_unavailable(self) -> None:
        seen = last_json(
            under_profile_settings(
                HARNESS
                + """
def in_order(tx):
    settings_store.read_shared(tx, [ps.LOCATION, ps.ONBOARDING_CONSENT])
    # A pointer read again later is already held and waits for nothing.
    settings_store.read_shared(tx, [ps.ONBOARDING_CONSENT])
    return Result("applied")

def out_of_order(tx):
    settings_store.read_shared(tx, [ps.LOCATION])
    settings_store.read_shared(tx, [ps.ONBOARDING_CONSENT])
    return Result("applied")

def later_in_order(tx):
    # DM-57 U8: a second call that keeps name order passes the check.
    settings_store.read_shared(tx, [ps.ONBOARDING_CONSENT])
    settings_store.read_shared(tx, [ps.LOCATION])
    return Result("applied")

good = txmod.run(in_order)
good_pointers = list(seen_txs[-1].pointers)
cursor.locked.clear()
bad = txmod.run(out_of_order)
bad_locked = list(cursor.locked)
later = txmod.run(later_in_order)
error = None
try:
    settings_store.read_shared(
        SimpleNamespace(cursor=cursor, pointers=["profile.location"]), [ps.ONBOARDING_CONSENT])
except Exception as exc:
    error = exc
print(json.dumps({
    "good": [good.outcome, good.code, good.reason],
    "good_pointers": good_pointers,
    "bad": [bad.outcome, bad.code, bad.reason, bad.ok],
    "bad_locked": bad_locked,
    "later": [later.outcome],
    "error_type": type(error).__name__,
    "error_is_refused": isinstance(error, Refused),
    "error_text": str(error),
}))
"""
            )
        )
        self.assertEqual(seen["good"], ["applied", "", ""])
        self.assertEqual(seen["good_pointers"], ["consent.onboarding", "profile.location"])
        # The check's error is answered as any unexpected exception: provider_unavailable,
        # with the error's type as the internal reason, never a refusal of the member's.
        self.assertEqual(seen["bad"], ["error", "provider_unavailable", "PointerOrderError", False])
        # The out-of-order pointer is refused before its lock is taken.
        self.assertEqual(seen["bad_locked"], ["profile.location"])
        self.assertEqual(seen["later"], ["applied"])
        self.assertEqual(seen["error_type"], "PointerOrderError")
        self.assertIs(seen["error_is_refused"], False)
        self.assertEqual(seen["error_text"], "pointer_out_of_order")

    def test_a_publication_records_its_own_pointer_before_its_lock_and_its_read(self) -> None:
        seen = last_json(
            under_profile_settings(
                HARNESS
                + """
at_lock = []

class Pointer:
    id = uuid4()
    policy_version = "chat.history.v1"
    artifact_ref = uuid4()

class Rows:
    def filter(self, **kwargs):
        return self
    def first(self):
        at_lock.append(list(seen_txs[-1].pointers))
        return Pointer()

manager = SimpleNamespace(select_for_update=lambda: Rows())
with mock.patch.object(settings_store, "PolicyRevision", SimpleNamespace(objects=manager)), \\
        mock.patch.object(ps, "publication_refusals", lambda *a, **k: ("schema",)):
    result = settings_store.publish(
        ps.HISTORY, {}, staff_subject="staff:pointer-test", reason="test", request_id=uuid4())
print(json.dumps({
    "result": [result.outcome, result.code, result.reason],
    "at_lock": at_lock,
    "after": list(seen_txs[-1].pointers),
    "locked": cursor.locked,
}))
"""
            )
        )
        # Refused by the (patched) schema check, before anything is written.
        self.assertEqual(seen["result"], ["refused", "invalid_request", "refused:schema"])
        # Its own pointer is held before its FOR UPDATE lock, then the onboarding consent's
        # pointer it reads, which sorts after it.
        self.assertEqual(seen["at_lock"], [["chat.history"]])
        self.assertEqual(seen["after"], ["chat.history", "consent.onboarding"])
        self.assertEqual(seen["locked"], ["consent.onboarding"])


def _sources() -> list[Path]:
    found = []
    for root in SCANNED:
        for path in sorted(root.rglob("*.py")):
            parts = set(path.relative_to(root).parts)
            if parts & {".venv", "migrations", "tests", "__pycache__"}:
                continue
            found.append(path)
    return found


class NothingElseLocksAPointerTests(unittest.TestCase):
    def test_only_the_settings_store_locks_a_policy_pointer(self) -> None:
        # D19 (DM-57 section 4): ``read_shared``'s raw FOR SHARE and ``publish``'s
        # select_for_update are the only pointer locks. A lock elsewhere, by the ORM or in SQL,
        # in any application package or the proof, fails this check.
        found = []
        for path in _sources():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            where = str(path.relative_to(REPOSITORY))
            # Docstrings and other bare string statements are prose, never executed SQL.
            prose = {
                id(node.value)
                for node in ast.walk(tree)
                if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)
            }
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Constant)
                    and isinstance(node.value, str)
                    and id(node) not in prose
                ):
                    text = node.value.lower()
                    if "policyrevision" in text and any(word in text for word in LOCK_WORDS):
                        found.append(f"{where}:{node.lineno} sql")
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    chain = ast.unparse(node)
                    if node.func.attr == "select_for_update" and "PolicyRevision" in chain:
                        found.append(f"{where}:{node.lineno} select_for_update")
                    if node.func.attr in ("raw", "extra") and "PolicyRevision" in chain:
                        found.append(f"{where}:{node.lineno} {node.func.attr}")
        store = str(SETTINGS_STORE.relative_to(REPOSITORY))
        self.assertTrue(found, "the check sees the store's own locks")
        self.assertEqual({entry.split(":")[0] for entry in found}, {store})
        self.assertEqual(
            sorted(entry.split(" ")[1] for entry in found), ["select_for_update", "sql"]
        )
        # The scan reads the API's packages and the proof (not their tests or migrations).
        scanned = {str(path.relative_to(REPOSITORY)).split("/")[2] for path in _sources()}
        self.assertTrue(
            {"glow_profiles", "glow_chat", "glow_identity", "glow_api", "glow_ordering_proof"}
            <= scanned | {str(path.relative_to(REPOSITORY)).split("/")[1] for path in _sources()},
            scanned,
        )

    def test_nothing_but_the_store_and_the_model_mentions_a_pointer(self) -> None:
        # SV2 Stage B, correction C2 (the exact-head review's F2): the lock-site check above
        # reads a lock's own spelling, so a ``select_for_update()`` on a queryset held in a
        # variable, or SQL whose table comes from ``PolicyRevision._meta.db_table``, passes it.
        # This check reads any mention instead: the model's name or its table's, in any case, in
        # code, a string, a comment or a docstring, in every scanned source but the model's and
        # the store's. The proof's read-only mentions are named by function and line; any other,
        # a lock or not, fails until it is read and named here.
        self.assertEqual(_unnamed_mentions(), [])
        found = {mention[:3] for mention in _mentions()}
        self.assertEqual(found, POINTER_READS)

    def test_the_search_word_matches_the_models_table(self) -> None:
        # The table is Django's default for the model, ``glow_persistence_policyrevision``: no
        # ``db_table`` is set in ``glow_persistence/models.py``, so the search word finds the
        # table's name in SQL as it finds the model's.
        text = (API_ROOT / "glow_persistence" / "models.py").read_text(encoding="utf-8")
        self.assertNotIn("db_table", text)
        self.assertIn(POINTER_WORD, "glow_persistence_policyrevision")
        self.assertIn(POINTER_WORD, "PolicyRevision".lower())


# SV2 Stage B, correction C2 (F2): the model's name and its table's, lower-cased; every mention
# of either contains it.
POINTER_WORD = "policyrevision"
# The only sources that may mention the pointer in any form: its model and the store.
POINTER_HOMES = {API_ROOT / "glow_persistence" / "models.py", SETTINGS_STORE}
# The proof's read-only mentions, each by file, function and line (stripped): the counts a case
# compares before and after a refused write, and the publication case's read of the moved
# pointer. Neither locks.
PROFILE_CASES = "proofs/postgres-ordering/glow_ordering_proof/profile_cases.py"
POINTER_READS = {
    (PROFILE_CASES, "_counts", "PolicyRevision,"),
    (
        PROFILE_CASES,
        "_counts",
        '"pointers": sum(PolicyRevision.objects.values_list("version", flat=True)),',
    ),
    (
        PROFILE_CASES,
        "settings_publication",
        "from glow_persistence.models import OutboxEvent, PolicyRevision, StaffAudit",
    ),
    (
        PROFILE_CASES,
        "settings_publication",
        "pointer = PolicyRevision.objects.get(name=ps.GENDER_LIST)",
    ),
}


def _mentions() -> list[tuple[str, str, str, int]]:
    """Every line of a scanned source, outside the model's and the store's, that mentions the
    pointer: its file, its innermost function, its text (stripped) and its number."""
    found = []
    for path in _sources():
        if path in POINTER_HOMES:
            continue
        text = path.read_text(encoding="utf-8")
        if POINTER_WORD not in text.lower():
            continue
        tree = ast.parse(text)
        functions = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        ]
        where = str(path.relative_to(REPOSITORY))
        for number, line in enumerate(text.splitlines(), start=1):
            if POINTER_WORD in line.lower():
                holding = [
                    function
                    for function in functions
                    if function.lineno <= number <= (function.end_lineno or number)
                ]
                holding.sort(key=lambda function: function.lineno)
                owner = holding[-1].name if holding else "<module>"
                found.append((where, owner, line.strip(), number))
    return found


def _unnamed_mentions() -> list[str]:
    return [
        f"{where}:{number} in {owner}: {line}"
        for where, owner, line, number in _mentions()
        if (where, owner, line) not in POINTER_READS
    ]


if __name__ == "__main__":
    unittest.main()
