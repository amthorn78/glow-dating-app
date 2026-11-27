"""SV4 B2, the parts of the triggers, the deliverer, ``logout``, the sweeps and G-04's read that
need no database (its brief's D21 to D27 and D31, with DM-101's AM8 to AM11 and DM-103's AO1).

- **The names** (D21, D23): the notification events' schema and types live in
  ``glow_domain.notifications``; its copies of chat's schema and session types equal
  ``glow_chat.events``', and the deliverer's attempts and lease equal ``glow_chat.delivery``'s, read
  by importing both (in a fresh process under ``tests.discovery_offline_settings``).
- **The selection** (D22, D23; AM11): the deliverer takes exactly four types, each in its schema.
- **The deliverer's structure** (D22; AM9, AM10): the transport is called only after the lease's
  transaction, in no transaction; the facts are read by literal statements, each a share lock, in
  the check's order; the event is locked by a literal statement, never through
  ``select_for_update`` (the proof's account-lock scan counts those); a retry moves
  ``available_at`` by the backoff, doubled for each further attempt; the content is P06.3's.
- **``logout`` and the sweeps** (D23, D24; AO1): the account row first, then the registrations;
  the pending discards' three steps in order, the delete in its own transaction with no other
  lock, the rewrite under a new key; every step bounded; expired sessions found by ``expires_at``.
- **One rule** (D24): B1's ``_register`` is still the only writer of a non-null
  ``token_secret_ref``.

These read source text or constants (the section "Substring pins, not semantics" of the SV4 record
names what each stands for); the behaviour is the chat suite's database cases.
"""

import ast
import re
import unittest
from pathlib import Path

from glow_domain import notifications as n
from tests.test_discovery_offline import under_discovery_settings
from tests.test_profiles_offline import last_json

API_ROOT = Path(__file__).resolve().parents[1]
PACKAGE = API_ROOT / "glow_notifications"
DELIVERY = PACKAGE / "delivery.py"
LOGOUT = PACKAGE / "logout.py"
SWEEPS = PACKAGE / "sweeps.py"
RECIPIENTS = PACKAGE / "recipients.py"
PERSISTENCE = PACKAGE / "persistence.py"


def parsed(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def top(tree: ast.Module, name: str) -> ast.FunctionDef:
    return next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)


def method(tree: ast.Module, klass: str, name: str) -> ast.FunctionDef:
    found = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == klass)
    return next(n for n in found.body if isinstance(n, ast.FunctionDef) and n.name == name)


def constants(tree: ast.Module) -> dict[str, str]:
    """The module's string constants, by name."""
    return {
        target.id: node.value.value
        for node in tree.body
        if isinstance(node, ast.Assign)
        and isinstance(node.value, ast.Constant)
        and isinstance(node.value.value, str)
        for target in node.targets
        if isinstance(target, ast.Name)
    }


def calls(function: ast.AST) -> list[tuple[int, str]]:
    return sorted(
        (node.lineno, ast.unparse(node.func))
        for node in ast.walk(function)
        if isinstance(node, ast.Call)
    )


def first(found: list[tuple[int, str]], name: str) -> int:
    return next(line for line, called in found if called == name)


def code_of(function: ast.AST) -> str:
    """The function's text without its docstrings."""
    copied = ast.parse(ast.unparse(function))
    for node in ast.walk(copied):
        body = getattr(node, "body", None)
        if (
            isinstance(body, list)
            and body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            body[0] = ast.Pass()
    return ast.unparse(copied)


class NameTests(unittest.TestCase):
    def test_the_events_names_are_the_domains(self) -> None:
        self.assertEqual(n.NOTIFICATIONS_SCHEMA_VERSION, "glow-notifications-1")
        self.assertEqual(n.NOTIFY_MATCH, "notify_match")
        self.assertEqual(n.NOTIFY_MESSAGE, "notify_message")
        self.assertEqual(
            dict(n.EVENT_KINDS), {"notify_match": "match", "notify_message": "message"}
        )
        self.assertEqual(n.SESSION_ENDINGS, ("session_revoked", "session_expired"))
        self.assertEqual(n.MAX_ACTIVE_REGISTRATIONS, 10)

    def test_the_chat_names_and_the_retry_constants_equal_chats(self) -> None:
        # Both modules imported, in a fresh process (they touch the models).
        seen = last_json(
            under_discovery_settings(
                "import json\n"
                "from glow_chat import delivery as chat_delivery, events\n"
                "from glow_domain import notifications as n\n"
                "from glow_notifications import delivery\n"
                "print(json.dumps({\n"
                "    'schema': [n.CHAT_SCHEMA_VERSION, events.CHAT_SCHEMA_VERSION],\n"
                "    'revoked': [n.SESSION_REVOKED, events.SESSION_REVOKED],\n"
                "    'expired': [n.SESSION_EXPIRED, events.SESSION_EXPIRED],\n"
                "    'attempts': [delivery.MAX_ATTEMPTS, chat_delivery.MAX_ATTEMPTS],\n"
                "    'lease': [delivery.LEASE.total_seconds(),\n"
                "              chat_delivery.LEASE.total_seconds()],\n"
                "    'backoff': delivery.BACKOFF.total_seconds(),\n"
                "    'delivered': sorted(events.DELIVERED),\n"
                "}))\n"
            )
        )
        for name in ("schema", "revoked", "expired", "attempts", "lease"):
            with self.subTest(name=name):
                self.assertEqual(seen[name][0], seen[name][1])
        self.assertEqual(seen["attempts"][0], 5)
        self.assertEqual(seen["lease"][0], 30.0)
        self.assertEqual(seen["backoff"], 30.0)
        # Chat's deliverer reads only its delivered types, which hold neither notification type
        # nor either session event.
        for kind in ("notify_match", "notify_message", "session_revoked", "session_expired"):
            with self.subTest(kind=kind):
                self.assertNotIn(kind, seen["delivered"])

    def test_the_names_are_literals_in_the_domain(self) -> None:
        # The domain module loads with glow_chat hidden (tests/test_notifications.py), so its copies
        # of chat's names are literals.
        values = constants(parsed(API_ROOT / "glow_domain" / "notifications.py"))
        self.assertEqual(values["CHAT_SCHEMA_VERSION"], "glow-chat-1")
        self.assertEqual(values["SESSION_REVOKED"], "session_revoked")
        self.assertEqual(values["SESSION_EXPIRED"], "session_expired")


class SelectionTests(unittest.TestCase):
    def test_the_deliverer_selects_exactly_four_types(self) -> None:
        seen = last_json(
            under_discovery_settings(
                "import json\n"
                "from glow_notifications import delivery\n"
                "print(json.dumps(sorted(list(pair) for pair in delivery.TYPES)))\n"
            )
        )
        self.assertEqual(
            seen,
            [
                ["glow-chat-1", "session_expired"],
                ["glow-chat-1", "session_revoked"],
                ["glow-notifications-1", "notify_match"],
                ["glow-notifications-1", "notify_message"],
            ],
        )
        tree = parsed(DELIVERY)
        due = code_of(method(tree, "NotificationDelivery", "_due_ids"))
        self.assertIn("OutboxEvent.objects.filter(SELECTED)", due)
        lease = code_of(method(tree, "NotificationDelivery", "_lease"))
        self.assertIn("if (event.schema_version, event.event_type) not in TYPES:", lease)
        selected = next(
            node
            for node in tree.body
            if isinstance(node, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "SELECTED" for t in node.targets)
        )
        text = ast.unparse(selected.value)
        self.assertIn("schema_version=n.NOTIFICATIONS_SCHEMA_VERSION", text)
        self.assertIn("event_type__in=tuple(n.EVENT_KINDS)", text)
        self.assertIn("schema_version=n.CHAT_SCHEMA_VERSION", text)
        self.assertIn("event_type__in=n.SESSION_ENDINGS", text)


class DelivererStructureTests(unittest.TestCase):
    def test_the_transport_is_called_after_the_lease_in_no_transaction(self) -> None:
        # D22: one push per fixed device, outside any transaction, as soon as the lease commits;
        # its receipt in a transaction of its own.
        tree = parsed(DELIVERY)
        call = method(tree, "NotificationDelivery", "_call_and_receipt")
        found = calls(call)
        self.assertLess(first(found, "self._transport.send"), first(found, "run_transaction"))
        # No block of any kind around the calls: no ``with`` (an atomic block), no transaction.
        self.assertFalse([node for node in ast.walk(call) if isinstance(node, ast.With)])
        self.assertNotIn("atomic", code_of(call))
        self.assertNotIn("transaction.", code_of(call))
        for node in ast.walk(call):
            if node is not call and isinstance(node, ast.Lambda | ast.FunctionDef):
                with self.subTest(nested=node.lineno):
                    self.assertNotIn(".send(", ast.unparse(node))
        for name in ("_lease", "_check", "_receipt", "_logout", "_release", "_deliver"):
            with self.subTest(function=name):
                self.assertNotIn(".send(", code_of(method(tree, "NotificationDelivery", name)))
        deliver = calls(method(tree, "NotificationDelivery", "_deliver"))
        self.assertLess(first(deliver, "run_transaction"), first(deliver, "probe.after_lease"))
        self.assertLess(
            first(deliver, "probe.after_lease"), first(deliver, "self._call_and_receipt")
        )

    def test_the_push_names_its_device_by_reference_under_the_ledger_key(self) -> None:
        call = code_of(method(parsed(DELIVERY), "NotificationDelivery", "_call_and_receipt"))
        self.assertIn("content = n.push_content(lease.kind)", call)
        self.assertIn(
            "request = n.PushRequest(n.TokenReference(push.reference), "
            "n.ledger_key(lease.event_id, push.installation_id), content)",
            call,
        )
        self.assertEqual(
            n.push_content("match").as_payload(),
            {
                "title": "Glow",
                "body": "You have a new match.",
                "data": {"kind": "match", "route": "/matches"},
            },
        )
        self.assertEqual(
            n.push_content("message").as_payload(),
            {
                "title": "Glow",
                "body": "You have a new message.",
                "data": {"kind": "message", "route": "/conversations"},
            },
        )

    def test_the_facts_are_share_locks_in_the_checks_order(self) -> None:
        statements = constants(parsed(DELIVERY))
        shared = [
            "ACCOUNT_SHARED",
            "MATCH_SHARED",
            "SUBMISSION_SHARED",
            "PROFILES_SHARED",
            "CONSENT_SHARED",
            "BLOCKS_SHARED",
            "SETTINGS_SHARED",
            "REGISTRATIONS_SHARED",
            "SESSIONS_SHARED",
        ]
        for name in shared:
            with self.subTest(statement=name):
                self.assertTrue(statements[name].endswith("FOR SHARE"))
                self.assertNotIn("UPDATE", statements[name])
        self.assertTrue(statements["EVENT_FOR_UPDATE"].endswith("WHERE id = %s FOR UPDATE"))
        self.assertIn("FROM glow_persistence_outboxevent", statements["EVENT_FOR_UPDATE"])
        for name in ("MATCH_PAIR", "SUBMISSION_MATCH"):
            with self.subTest(identifiers=name):
                self.assertNotIn(" FOR ", statements[name])
        check = method(parsed(DELIVERY), "NotificationDelivery", "_check")
        used = [
            node.args[1].id
            for node in sorted(
                (n for n in ast.walk(check) if isinstance(n, ast.Call)),
                key=lambda n: (n.lineno, n.col_offset),
            )
            if ast.unparse(node.func) in ("_one", "_all")
            and isinstance(node.args[1], ast.Name)
            and node.args[1].id in shared
        ]
        self.assertEqual(used, shared)
        text = code_of(check)
        self.assertLess(
            text.index("SESSIONS_SHARED"), text.index("signal(tx.probe, 'after_locks')")
        )
        self.assertLess(
            text.index("signal(tx.probe, 'after_locks')"), text.index("now = clock(tx)")
        )
        self.assertIn("refusal = n.send_refusal(trigger, facts)", text)

    def test_no_lock_is_taken_through_select_for_update_or_any_state(self) -> None:
        # The proof's account-lock scan counts every select_for_update call in services/api, and
        # SV2 keeps lock_account_any_state to F05's two steps; the package takes neither.
        for path in sorted(PACKAGE.rglob("*.py")):
            source = path.read_text(encoding="utf-8")
            with self.subTest(module=str(path.relative_to(API_ROOT))):
                self.assertNotIn("select_for_update", source)
                self.assertNotIn("lock_account_any_state", source)
                for node in ast.walk(ast.parse(source)):
                    if isinstance(node, ast.Constant) and isinstance(node.value, str):
                        text = node.value
                        if "FOR UPDATE" in text or "FOR NO KEY" in text:
                            self.assertNotIn("glow_persistence_appaccount", text)

    def test_a_retry_moves_available_at_by_the_backoff(self) -> None:
        # AM9: unlike chat's, a retried event's available_at moves, so it holds no later event.
        again = code_of(top(parsed(DELIVERY), "_again"))
        self.assertIn("available_at=now + backoff(event.attempts)", again)
        self.assertIn("if event.attempts < MAX_ATTEMPTS:", again)
        self.assertIn("state='dead_letter'", again)
        seen = last_json(
            under_discovery_settings(
                "import json\n"
                "from glow_notifications import delivery\n"
                "print(json.dumps([delivery.backoff(k).total_seconds() for k in (1, 2, 3, 4)]))\n"
            )
        )
        self.assertEqual(seen, [30.0, 60.0, 120.0, 240.0])
        receipt = code_of(method(parsed(DELIVERY), "NotificationDelivery", "_receipt"))
        self.assertIn("return _again(event, now, n.TRANSPORT_UNAVAILABLE", receipt)

    def test_the_settled_time_is_written_with_every_change(self) -> None:
        # D25: the retention measures a settled event from its updated_at, which every write here
        # sets from the application's clock.
        write = code_of(top(parsed(DELIVERY), "_write"))
        self.assertIn("version=F('version') + 1, updated_at=timezone.now()", write)
        delivered = code_of(top(parsed(DELIVERY), "_delivered"))
        self.assertIn("_write(event, state='delivered', delivered_at=now", delivered)


class LogoutAndSweepTests(unittest.TestCase):
    def test_logout_locks_the_account_then_the_registrations(self) -> None:
        # D23 (AM11): the device commands' locks, the account row first (B1's transfer relies on
        # every writer of a registration locking its account first).
        body = next(
            node
            for node in ast.walk(method(parsed(DELIVERY), "NotificationDelivery", "_logout"))
            if isinstance(node, ast.FunctionDef) and node.name == "body"
        )
        found = calls(body)
        self.assertLess(
            first(found, "logout.lock_account_held"), first(found, "logout.lock_registrations")
        )
        self.assertLess(first(found, "logout.lock_registrations"), first(found, "logout.revoke"))
        inert = calls(top(parsed(SWEEPS), "_revoke_inert"))
        self.assertLess(
            first(inert, "logout.lock_account_held"), first(inert, "logout.lock_registrations")
        )
        held = code_of(top(parsed(LOGOUT), "lock_account_held"))
        self.assertIn("lock_account(tx, account_id)", held)
        self.assertIn("if refused.reason != chat.ACCOUNT_NOT_ACTIVE:", held)
        statement = constants(parsed(LOGOUT))["REGISTRATIONS_FOR_UPDATE"]
        self.assertTrue(statement.endswith("WHERE id = ANY(%s) ORDER BY id FOR UPDATE"))
        revoke = code_of(top(parsed(LOGOUT), "revoke"))
        self.assertIn("ended_by='logout'", revoke)
        self.assertIn("token_secret_ref=None", revoke)
        self.assertIn("hold_for_discard(retired)", revoke)

    def test_the_pending_discards_three_steps(self) -> None:
        # D24 with AO1: the delete by key in its own committed transaction, a stop if it removed no
        # row; the registrations read with no lock, a stop if one holds the reference; then the
        # store, and a failed discard (or a failed read) written again under a new key.
        step = top(parsed(SWEEPS), "_pending_discards")
        text = code_of(step)
        atomic = text.index("with transaction.atomic(durable=True):")
        delete = text.index("PendingTokenDiscard.objects.filter(pk=key).delete()")
        stop = text.index("if deleted != 1:")
        read = text.index(
            "held = DeviceRegistration.objects.filter(token_secret_ref=value).exists()"
        )
        held = text.index("if held:")
        store = text.index("tokens.discard(n.TokenReference(str(value)))")
        order = [atomic, delete, stop, read, held, store]
        self.assertEqual(sorted(order), order)
        with_block = next(node for node in ast.walk(step) if isinstance(node, ast.With))
        self.assertEqual(
            ast.unparse(with_block.body[0]),
            "deleted, _ = PendingTokenDiscard.objects.filter(pk=key).delete()",
        )
        self.assertEqual(len(with_block.body), 1)
        # A failed delete leaves its row as it was and goes to the next row, discarding nothing.
        guard = next(
            node for node in ast.walk(step) if isinstance(node, ast.Try) and with_block in node.body
        )
        self.assertEqual(len(guard.handlers), 1)
        self.assertIsInstance(guard.handlers[0].body[-1], ast.Continue)
        self.assertNotIn("discard(", ast.unparse(guard.handlers[0]))
        self.assertNotIn("_again(", ast.unparse(guard.handlers[0]))
        # Each stop ends its iteration, discarding nothing.
        stops = {
            ast.unparse(node.test): node
            for node in ast.walk(step)
            if isinstance(node, ast.If) and ast.unparse(node.test) in ("deleted != 1", "held")
        }
        self.assertEqual(set(stops), {"deleted != 1", "held"})
        for test, node in stops.items():
            with self.subTest(stop=test):
                self.assertIsInstance(node.body[-1], ast.Continue)
                self.assertNotIn("discard(", ast.unparse(node))
                self.assertNotIn("_again(", ast.unparse(node))
        # The read's failure and the store's are each answered by the rewrite, then the next row.
        handlers = [node for node in ast.walk(step) if isinstance(node, ast.ExceptHandler)]
        answered = [
            handler
            for handler in handlers
            if [ast.unparse(statement) for statement in handler.body]
            == ["_again(str(value), counts)", "continue"]
        ]
        self.assertEqual(len(answered), 2)
        for word in (" FOR ", "lock_account", "select_for_update", "lock_registrations"):
            with self.subTest(lock=word):
                self.assertNotIn(word, text)
        again = top(parsed(SWEEPS), "_again")
        create = next(
            node
            for node in ast.walk(again)
            if isinstance(node, ast.Call)
            and ast.unparse(node.func) == "PendingTokenDiscard.objects.create"
        )
        # A new key: no primary key is given, so the model makes a new one.
        self.assertEqual([k.arg for k in create.keywords], ["token_secret_ref"])
        self.assertFalse(create.args)

    def test_every_step_is_bounded_and_the_bounds_are_the_prompts(self) -> None:
        values = last_json(
            under_discovery_settings(
                "import json\n"
                "from glow_notifications import sweeps\n"
                "print(json.dumps([sweeps.ROWS_PER_STEP, sweeps.DISCARD_AGE.total_seconds(),\n"
                "                  sweeps.LEDGER_RETENTION.total_seconds()]))\n"
            )
        )
        self.assertEqual(values, [500, 900.0, 30 * 86400.0])
        tree = parsed(SWEEPS)
        for name in ("_expired_sessions", "_retention", "_pending_discards"):
            with self.subTest(step=name):
                self.assertIn("[:ROWS_PER_STEP]", code_of(top(tree, name)))
        self.assertIn(
            "cursor.execute(INERT, ['active', 'valid', 'active', ROWS_PER_STEP])",
            code_of(top(tree, "_inert_registrations")),
        )
        self.assertTrue(constants(tree)["INERT"].endswith("ORDER BY r.id LIMIT %s"))
        order = calls(top(tree, "run_sweeps"))
        steps = [
            first(order, name)
            for name in (
                "_expired_sessions",
                "_inert_registrations",
                "_retention",
                "_pending_discards",
            )
        ]
        self.assertEqual(steps, sorted(steps))

    def test_expired_sessions_are_found_by_their_expiry_never_through_the_actor(self) -> None:
        # D24 (F-9): by expires_at, ordered by it and the id, and marked by expire_session through
        # SV1's expire_found.
        text = code_of(top(parsed(SWEEPS), "_expired_sessions"))
        self.assertIn("AccountSession.objects.filter(state='valid', expires_at__lte=Now())", text)
        self.assertIn(".order_by('expires_at', 'id')", text)
        self.assertIn("expire_found(UUID(str(session_id)))", text)
        # The module's code, its docstrings left out (they name the actor's gap, F-9).
        source = code_of(parsed(SWEEPS))
        self.assertNotIn("authentication", source)
        self.assertNotIn("UserSession", source)

    def test_the_retention_takes_only_settled_events_thirty_days_old(self) -> None:
        text = code_of(top(parsed(SWEEPS), "_retention"))
        self.assertIn("cutoff = timezone.now() - LEDGER_RETENTION", text)
        self.assertIn(
            "settled = {'event__state__in': ('delivered', 'dead_letter'), "
            "'event__updated_at__lte': cutoff}",
            text,
        )


class CustodyRuleTests(unittest.TestCase):
    def test_only_b1s_register_writes_a_non_null_token_secret_ref(self) -> None:
        # D24's one rule (AO1): every transaction that writes a non-null token_secret_ref deletes
        # that reference's pending discard by its key, or refuses; B2 writes none, so B1's
        # _register, after _consume_handle, still holds the only two writes. A write is any of: a
        # call's keyword ``token_secret_ref`` that is not ``None`` (a filter's or a read's
        # excepted), a ``DeviceRegistration(...)`` constructor, an assignment to an attribute of
        # that name, the field's name as a value inside a call that is not a read
        # (``update_fields``, ``bulk_update``, ``defaults``, ``setattr``), or SQL text that updates
        # or inserts into the registrations' table, in any case.
        reads = (
            ".filter",
            ".exclude",
            ".get",
            ".exists",
            ".values_list",
            ".values",
            ".only",
            ".defer",
            ".order_by",
        )
        statement = re.compile(
            r"\b(?:UPDATE\s+|INSERT\s+INTO\s+)glow_persistence_deviceregistration\b", re.I
        )
        writes = []
        for path in sorted(API_ROOT.rglob("*.py")):
            relative = path.relative_to(API_ROOT).as_posix()
            if relative.startswith(("tests/", ".venv/")) or "/migrations/" in relative:
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign | ast.AnnAssign | ast.AugAssign):
                    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                    value = node.value
                    for target in targets:
                        if (
                            isinstance(target, ast.Attribute)
                            and target.attr == "token_secret_ref"
                            and not (isinstance(value, ast.Constant) and value.value is None)
                        ):
                            writes.append((relative, node.lineno, "attribute"))
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    if statement.search(node.value):
                        writes.append((relative, node.lineno, "sql"))
                if not isinstance(node, ast.Call):
                    continue
                func = ast.unparse(node.func)
                if isinstance(node.func, ast.Name) and node.func.id == "DeviceRegistration":
                    writes.append((relative, node.lineno, func))
                if func == "Q" or func.endswith(reads):
                    # A condition or a read, not a write (a filter, a constraint's Q).
                    continue
                for keyword in node.keywords:
                    if keyword.arg != "token_secret_ref":
                        continue
                    if isinstance(keyword.value, ast.Constant) and keyword.value.value is None:
                        continue
                    if "PendingTokenDiscard" in func:
                        continue
                    writes.append((relative, node.lineno, func))
                # The field's name passed to this call itself, alone or inside a literal list,
                # tuple, set or dict (never a nested call's, which is judged on its own).
                pending = [*node.args, *(k.value for k in node.keywords)]
                while pending:
                    value = pending.pop()
                    if isinstance(value, ast.Constant) and value.value == "token_secret_ref":
                        writes.append((relative, node.lineno, f"{func} names the field"))
                    elif isinstance(value, ast.List | ast.Tuple | ast.Set):
                        pending.extend(value.elts)
                    elif isinstance(value, ast.Dict):
                        pending.extend(k for k in value.keys if k is not None)
                        pending.extend(value.values)
                    elif isinstance(value, ast.Starred):
                        pending.append(value.value)
        self.assertEqual({where for where, _, _ in writes}, {"glow_notifications/persistence.py"})
        self.assertEqual(len(writes), 2, writes)
        register = method(parsed(PERSISTENCE), "OrmNotificationPersistence", "_register")
        lines = sorted(line for _, line, _ in writes)
        self.assertTrue(all(register.lineno <= line <= register.end_lineno for line in lines))
        consumed = first(calls(register), "self._consume_handle")
        self.assertLess(consumed, lines[0])

    def test_no_module_of_the_package_imports_another_slice_in_any_form(self) -> None:
        # B1's import rule, kept by B2 (the prompt's stop rule): no glow_notifications module
        # imports glow_api, glow_chat or glow_discovery, by a ``from`` import (B1's test), by a
        # plain ``import`` or by a module's name in its code (an ``import_module``). Its sweep
        # reaches ``expire_session`` through SV1's ``glow_identity.revocation`` (the record).
        forbidden = ("glow_api", "glow_chat", "glow_discovery")
        for path in sorted(PACKAGE.rglob("*.py")):
            tree = parsed(path)
            with self.subTest(module=str(path.relative_to(API_ROOT))):
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self.assertFalse(alias.name.startswith(forbidden))
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        self.assertFalse(node.module.startswith(forbidden))
                code = ast.parse(code_of(tree))
                for node in ast.walk(code):
                    if isinstance(node, ast.Constant) and isinstance(node.value, str):
                        self.assertFalse(node.value.startswith(forbidden), node.value[:40])

    def test_the_g04_read_names_accounts_and_a_yes_or_no_only(self) -> None:
        statement = constants(parsed(RECIPIENTS))["RECIPIENTS"]
        self.assertNotIn("text", statement)
        self.assertNotIn("provider_message_ref", statement)
        self.assertNotIn("FOR ", statement)
        self.assertIn("r.state = 'accepted'", statement)
        self.assertIn("s.state = 'accepted'", statement)
        # No match state filter: a recipient is kept after an unmatch and after a block.
        self.assertNotIn("m.state", statement)
        seen = last_json(
            under_discovery_settings(
                "import json, dataclasses\n"
                "from glow_notifications import recipients\n"
                "print(json.dumps([f.name for f in dataclasses.fields(recipients.Recipient)]))\n"
            )
        )
        self.assertEqual(seen, ["account_id", "match_id", "answered"])


if __name__ == "__main__":
    unittest.main()
