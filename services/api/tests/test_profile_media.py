"""SV2 Stage B: photos (its brief's D10, D11 and D17; OD-61; OD-62), the parts that need no
database.

- the writers' transition table is F05's registry, roles included, with approve and reject the
  system's;
- the media policy's closed schema, its development-media-1 launch value and its ceilings in code;
- object keys and grant references: Glow's own, random and opaque, and no address;
- the fixture adapters: the check approves nothing, there is no hold and no detector, the store
  authenticates its own events only, and processing reads only the key it is given;
- the projections: only an approved variant's reference, the closed DTOs unchanged;
- no member route reaches a provider, system or staff step;
- every approval returns at a hold before it writes anything (correction C2, F1; SV2-R);
- SV2-R (OD-68): the photo check's toggle read in each step's one ``read_shared`` call,
  ``run_check``'s off branch calling no check port and recording the toggle's own subject and
  reason, and the recheck's order of checks, writes and the hold port.

The profile suite on the disposable PostgreSQL drives each writer through the routes and the
ports.
"""

import ast
import json
import re
import struct
import unittest
import uuid
import zlib
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

from glow_domain import media as md
from glow_domain import profile_settings as ps
from glow_profiles import contract, media_fixtures
from tests.test_profile_contract import runtime
from tests.test_profiles_offline import API_ROOT, modules

FLOWS = API_ROOT.parents[1] / "packages" / "contracts" / "production" / "flows-v1.json"
POLICY_VERSION = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,99}")


def synthetic_png(width: int, height: int) -> bytes:
    """A small synthetic PNG made here (never a real image): grey pixels, no metadata."""

    def chunk(kind: bytes, body: bytes) -> bytes:
        crc = zlib.crc32(kind + body) & 0xFFFFFFFF
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", crc)

    header = struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)
    rows = b"".join(b"\x00" + b"\x80" * width for _ in range(height))
    return (
        media_fixtures.PNG_SIGNATURE
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(rows))
        + chunk(b"IEND", b"")
    )


BOUNDS = md.Bounds(("image/png",), 1_048_576, 2_048, 2_048, 4_194_304)


class RegistryTests(unittest.TestCase):
    def test_the_writers_table_is_f05s_registry(self) -> None:
        flows = {flow["id"]: flow for flow in json.loads(FLOWS.read_text())["flows"]}
        registry = {
            (rule["event"], rule["from"]): (rule["to"], rule["role"])
            for rule in flows["F05"]["transitions"]
        }
        self.assertEqual(md.TRANSITIONS, registry)
        # OD-61 (D11): the automated check's decisions; staff act only on reports.
        self.assertEqual(md.TRANSITIONS[("approve", md.REVIEW_PENDING)][1], "system")
        self.assertEqual(md.TRANSITIONS[("reject", md.REVIEW_PENDING)][1], "system")
        self.assertEqual(md.TRANSITIONS[("restrict_media", md.APPROVED)][1], "moderator")
        self.assertEqual(md.TRANSITIONS[("uploaded", md.UPLOAD_PENDING)][1], "provider")
        self.assertEqual(md.TRANSITIONS[("purged", md.REMOVAL_PENDING)][1], "provider")
        # SV2-R (OD-68): the recheck's two transitions out of approved are the system's; with
        # the owner's reorder and removal and the moderator's restriction, they are the only ones.
        self.assertEqual(md.TRANSITIONS[("approve", md.APPROVED)], (md.APPROVED, "system"))
        self.assertEqual(md.TRANSITIONS[("reject", md.APPROVED)], (md.REJECTED, "system"))
        self.assertEqual(
            {
                (event, after)
                for (event, before), (after, _role) in md.TRANSITIONS.items()
                if before == md.APPROVED
            },
            {
                ("reorder", md.APPROVED),
                ("remove", md.REMOVAL_PENDING),
                ("restrict_media", md.REVIEW_PENDING),
                ("approve", md.APPROVED),
                ("reject", md.REJECTED),
            },
        )
        for event in ("uploaded", "review", "purged", "upload_grant"):
            with self.subTest(event=event):
                self.assertIsNone(md.next_state(event, md.APPROVED))
        # Upload cannot skip quarantine or review (F05).
        self.assertIsNone(md.next_state("approve", md.QUARANTINED))
        self.assertIsNone(md.next_state("review", md.UPLOAD_PENDING))
        self.assertIsNone(md.next_state("approve", md.REMOVAL_PENDING))
        self.assertIsNone(md.next_state("remove", md.REMOVAL_PENDING))

    def test_every_state_is_the_contracts(self) -> None:
        schema = runtime().SCHEMAS["production"]["$defs"]
        self.assertEqual(tuple(schema["MediaLifecycle"]["properties"]["state"]["enum"]), md.STATES)


class MediaPolicyTests(unittest.TestCase):
    def test_version_one_is_development_media_1(self) -> None:
        self.assertEqual(
            ps.LAUNCH_DEFAULTS[ps.MEDIA_POLICY],
            {
                "types": ["image/png"],
                "max_bytes": 1_048_576,
                "max_width": 2_048,
                "max_height": 2_048,
                "max_pixels": 4_194_304,
                "live_photos": 4,
                "grant_seconds": 60,
                "transfer_attempts": 3,
            },
        )
        self.assertEqual(ps.LAUNCH_REASONS[ps.MEDIA_POLICY], "development-media-1")
        self.assertEqual(
            ps.publication_refusals(ps.MEDIA_POLICY, ps.LAUNCH_DEFAULTS[ps.MEDIA_POLICY]), ()
        )

    def crossing(self, **changes: object) -> tuple[str, ...]:
        content = {**ps.LAUNCH_DEFAULTS[ps.MEDIA_POLICY], **changes}
        return ps.publication_refusals(ps.MEDIA_POLICY, content)

    def test_a_publication_above_each_ceiling_is_refused_naming_it(self) -> None:
        self.assertEqual(
            self.crossing(types=["image/png", "image/jpeg"]), (ps.MEDIA_TYPES_CEILING,)
        )
        self.assertEqual(self.crossing(max_bytes=1_048_577), (ps.MEDIA_BYTES_CEILING,))
        self.assertEqual(self.crossing(max_pixels=4_194_305), (ps.MEDIA_PIXELS_CEILING,))
        self.assertEqual(self.crossing(live_photos=21), (ps.MEDIA_COLLECTION_CEILING,))
        self.assertEqual(
            self.crossing(max_bytes=2_000_000, live_photos=50),
            (ps.MEDIA_BYTES_CEILING, ps.MEDIA_COLLECTION_CEILING),
        )
        for name in (
            ps.MEDIA_TYPES_CEILING,
            ps.MEDIA_BYTES_CEILING,
            ps.MEDIA_PIXELS_CEILING,
            ps.MEDIA_COLLECTION_CEILING,
        ):
            self.assertIn(name, ps.FIXED_LIMITS)
        # At a ceiling, and below it, is allowed.
        self.assertEqual(self.crossing(max_bytes=1_048_576, live_photos=20), ())
        self.assertEqual(self.crossing(max_bytes=1_024, live_photos=1, grant_seconds=30), ())

    def test_the_schema_is_closed(self) -> None:
        content = ps.LAUNCH_DEFAULTS[ps.MEDIA_POLICY]
        for broken in (
            {**content, "extra": 1},
            {key: value for key, value in content.items() if key != "max_bytes"},
            {**content, "types": []},
            {**content, "types": ["image/png", "image/png"]},
            {**content, "max_bytes": 0},
            {**content, "max_bytes": True},
            {**content, "max_width": 70_000},
            {**content, "grant_seconds": 0},
            {**content, "grant_seconds": 3_601},
            {**content, "transfer_attempts": 11},
            {**content, "live_photos": "4"},
            [],
        ):
            with self.subTest(content=broken):
                self.assertEqual(ps.publication_refusals(ps.MEDIA_POLICY, broken), (ps.SCHEMA,))

    def test_the_pointer_sorts_where_d19_needs_it(self) -> None:
        # Stage B's writers that recompute take consent.onboarding with media.policy in one
        # read_shared call, in name order (D19).
        self.assertLess(ps.ONBOARDING_CONSENT, ps.MEDIA_POLICY)
        self.assertLess(ps.STAFF_APPROVAL, ps.MEDIA_POLICY)
        self.assertTrue(all(ps.MEDIA_POLICY < name for name in ps.CATALOG_SETTINGS))
        self.assertIn(ps.MEDIA_POLICY, ps.ALL_SETTINGS)
        self.assertNotIn(ps.MEDIA_POLICY, ps.SEEDED_BY_0007)


class KeyTests(unittest.TestCase):
    def test_object_keys_are_random_and_opaque(self) -> None:
        keys = {md.new_object_key() for _ in range(2_000)}
        self.assertEqual(len(keys), 2_000)
        account, asset = uuid.uuid4(), uuid.uuid4()
        for key in keys:
            self.assertRegex(key, r"\A[0-9a-f]{32}\Z")
            for identifier in (account, asset):
                self.assertNotIn(identifier.hex, key)
                self.assertNotIn(str(identifier), key)
            self.assertNotIn(".", key)
            self.assertNotIn("/", key)

    def test_a_grant_reference_cannot_hold_an_address(self) -> None:
        for _ in range(200):
            reference = md.new_reference()
            self.assertIsNotNone(POLICY_VERSION.fullmatch(reference))
            for part in ("/", "http", "?", "@", "="):
                self.assertNotIn(part, reference)


class FixtureTests(unittest.TestCase):
    def test_the_runtimes_check_approves_nothing_and_nothing_holds_or_detects(self) -> None:
        ports = media_fixtures.default_ports()
        for key in (None, md.new_object_key()):
            self.assertEqual(ports.check.decide(uuid.uuid4(), key).decision, "undecided")
        self.assertIs(ports.hold.held(uuid.uuid4()), False)
        self.assertEqual(
            ports.detection.inspect(uuid.uuid4(), md.new_object_key()),
            md.Detection("review", md.NO_DETECTOR),
        )

    def test_the_store_authenticates_its_own_events_only(self) -> None:
        storage = media_fixtures.FixtureStorage()
        key = md.new_object_key()
        event = storage.put(key, synthetic_png(2, 2))
        self.assertIs(storage.receive(event), event)
        forged = md.UploadCompleted(
            uuid.uuid4(), key, event.byte_size, event.entity_tag, event.uploaded_at
        )
        self.assertIsNone(storage.receive(forged))
        tampered = md.UploadCompleted(event.event_id, key, 1, event.entity_tag, event.uploaded_at)
        self.assertIsNone(storage.receive(tampered))
        self.assertIsNone(storage.receive({"key": key}))
        self.assertIsNone(media_fixtures.FixtureStorage().receive(event))
        deleted = storage.acknowledge(key)
        self.assertIs(storage.receive(deleted), deleted)
        self.assertIsNone(storage.receive(md.ObjectDeleted(uuid.uuid4(), key)))

    def test_processing_reads_only_the_key_it_is_given_and_checks_it(self) -> None:
        storage = media_fixtures.FixtureStorage()
        processing = media_fixtures.FixtureProcessing(storage)
        original, other = md.new_object_key(), md.new_object_key()
        data = synthetic_png(3, 2)
        event = storage.put(original, data)
        storage.put(other, synthetic_png(5, 5))
        variant = md.new_object_key()
        done = processing.process(original, event.byte_size, event.entity_tag, BOUNDS, variant)
        self.assertEqual(storage.reads, [original])
        self.assertIsNotNone(done.variant_size)
        written = storage.objects[variant]
        self.assertTrue(written.startswith(b"fixture-variant:"))
        self.assertNotIn(data, written)
        self.assertEqual(done.variant_size, len(written))
        # Another size or entity tag than the completion's: no variant.
        for size, tag in ((event.byte_size + 1, event.entity_tag), (event.byte_size, "0" * 32)):
            with self.subTest(size=size, tag=tag):
                result = processing.process(original, size, tag, BOUNDS, md.new_object_key())
                self.assertEqual(result, md.Processed(None, "original_mismatch"))

    def test_processing_makes_no_variant_outside_the_bounds_or_of_a_non_png(self) -> None:
        storage = media_fixtures.FixtureStorage()
        processing = media_fixtures.FixtureProcessing(storage)
        tight = md.Bounds(("image/png",), 1_048_576, 4, 4, 12)
        for data, bounds in (
            (b"GIF89a" + b"\x00" * 40, BOUNDS),
            (synthetic_png(5, 2), tight),
            (synthetic_png(4, 4), tight),
            (synthetic_png(2, 2)[:-12], BOUNDS),
            (synthetic_png(2, 2), md.Bounds(("image/png",), 10, 4, 4, 16)),
            (synthetic_png(2, 2), md.Bounds(("image/jpeg",), 1_048_576, 4, 4, 16)),
        ):
            with self.subTest(size=len(data)):
                key = md.new_object_key()
                event = storage.put(key, data)
                variant = md.new_object_key()
                result = processing.process(key, event.byte_size, event.entity_tag, bounds, variant)
                self.assertEqual(result, md.Processed(None, "not_decodable_within_bounds"))
                self.assertNotIn(variant, storage.objects)

    def test_an_unavailable_store_raises_and_writes_nothing(self) -> None:
        storage = media_fixtures.FixtureStorage()
        key = md.new_object_key()
        event = storage.put(key, synthetic_png(2, 2))
        storage.unavailable = True
        variant = md.new_object_key()
        with self.assertRaises(md.StoreUnavailable):
            media_fixtures.FixtureProcessing(storage).process(
                key, event.byte_size, event.entity_tag, BOUNDS, variant
            )
        self.assertNotIn(variant, storage.objects)
        self.assertNotIsInstance(md.StoreUnavailable(), ValueError)

    def test_the_delivery_reference_is_never_the_key_or_an_address(self) -> None:
        storage = media_fixtures.FixtureStorage()
        key = md.new_object_key()
        reference = storage.delivery_reference(key)
        self.assertNotIn(key, reference)
        self.assertIsNotNone(POLICY_VERSION.fullmatch(reference))
        self.assertNotIn("/", reference)
        self.assertEqual(storage.references, {reference: key})


def _asset(state: str, ref: str | None = "delivery-0123", version: int = 2) -> SimpleNamespace:
    return SimpleNamespace(id=uuid.uuid4(), version=version, state=state, approved_variant_ref=ref)


class ProjectionTests(unittest.TestCase):
    def valid(self, definition: str, data: dict) -> None:
        validator = runtime()
        self.assertTrue(validator.valid("production", definition, data), definition)
        body = contract.app_response(data, contract.new_request_id())
        self.assertTrue(validator.valid("production", "AppResponse", body), definition)
        self.assertFalse(validator.valid("production", definition, {**data, "fixture_extra": 1}))

    def test_only_an_approved_variants_reference_is_returned(self) -> None:
        for state in md.STATES:
            with self.subTest(state=state):
                projected = contract.media_lifecycle(_asset(state))
                self.valid("MediaLifecycle", projected)
                expected = "delivery-0123" if state == md.APPROVED else None
                self.assertEqual(projected["approved_delivery_ref"], expected)
        collection = contract.media_collection(
            7, [_asset(md.APPROVED), _asset(md.REVIEW_PENDING, None)]
        )
        self.valid("MediaCollection", collection)
        self.valid("MediaCollection", contract.media_collection(1, []))

    def test_the_grant_is_media_upload_grant_unchanged(self) -> None:
        expires = datetime(2026, 11, 11, 3, 4, 5, 987_654, tzinfo=UTC)
        grant = SimpleNamespace(
            asset_id=uuid.uuid4(), grant_ref=md.new_reference(), expires_at=expires
        )
        projected = contract.media_upload_grant(grant)
        self.valid("MediaUploadGrant", projected)
        self.assertEqual(set(projected), {"kind", "asset_id", "grant_ref", "expires_at"})
        # The fraction is dropped, never rounded up: never later than Glow's own record.
        self.assertEqual(projected["expires_at"], "2026-11-11T03:04:05Z")
        self.assertLessEqual(
            datetime.strptime(projected["expires_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC),
            expires,
        )
        later = SimpleNamespace(**{**grant.__dict__, "expires_at": expires + timedelta(hours=-5)})
        self.valid("MediaUploadGrant", contract.media_upload_grant(later))

    def test_own_profile_lists_the_approved_photos(self) -> None:
        profile = SimpleNamespace(
            id=uuid.uuid4(), version=2, display_name="Synthetic", bio="Synthetic.", state="visible"
        )
        ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        projected = contract.own_profile(profile, ids)
        self.assertEqual(projected["media_ids"], ids)
        validator = runtime()
        self.assertTrue(validator.valid("production", "OwnProfile", projected))


class RouteTests(unittest.TestCase):
    def test_no_member_route_reaches_a_provider_system_or_staff_step(self) -> None:
        # D10: provider events reach the domain only through the storage port; no member route
        # can deliver one, run the system's steps or reach staff's restriction.
        views = modules()["views.py"]
        used = {
            node.attr
            for node in ast.walk(views)
            if isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "media"
        }
        self.assertEqual(used, {"command"})
        tree = modules()["media.py"]
        dispatcher = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "command"
        )
        called = {
            node.func.id
            for node in ast.walk(dispatcher)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertEqual(called, {"request_upload", "remove_photo", "reorder_photos"})
        for module in ("views.py", "urls.py"):
            text = ast.unparse(modules()[module])
            for name in (
                "record_upload",
                "acknowledge_deletion",
                "review",
                "run_check",
                "request_purge",
                "delivery_reference",
                "restrict_media",
                "media_fixtures",
                # SV2-R (OD-68): the recheck and its read, for P11's worker only.
                "recheck",
                "awaiting_recheck",
            ):
                with self.subTest(module=module, name=name):
                    self.assertNotIn(f"{name}(", text)
                    self.assertNotIn(f".{name}", text)

    def test_every_photo_state_write_goes_through_the_registrys_table(self) -> None:
        tree = modules()["media.py"]
        transition = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "transition"
        )
        first = [ast.unparse(statement) for statement in transition.body[1:5]]
        self.assertEqual(
            first[:3],
            [
                "asset = MediaAsset.objects.select_for_update().get(pk=asset_id)",
                "after = md.next_state(event, str(asset.state))",
                "if after is None:\n    raise Refused(STATE_CONFLICT, 'media_transition')",
            ],
        )
        # Delivery is withheld in every state but approved, at the one state write.
        source = ast.unparse(transition)
        self.assertIn("if after != md.APPROVED:\n        asset.approved_variant_ref = None", source)
        # The only approval is the check's, after the hold port is asked.
        run_check = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "run_check"
        )
        text = ast.unparse(run_check)
        self.assertLess(
            text.index("adapters.hold.held"), text.index("transition(tx, asset.id, 'approve'")
        )
        self.assertLess(
            text.index("adapters.hold.held"), text.index("_decision_audit(tx, asset, 'approve'")
        )
        # SV2-R (its brief's "Earlier tests"): each approval in media.py, by its step. run_check's
        # one approval is the check's and, while the toggle is off, the off branch's; the
        # recheck's keeps a photo approved. Each asks the hold port first (below).
        approvals = sorted(
            function.name
            for function in tree.body
            if isinstance(function, ast.FunctionDef)
            for node in ast.walk(function)
            if isinstance(node, ast.Call)
            and ast.unparse(node.func) == "transition"
            and len(node.args) > 2
            and getattr(node.args[2], "value", None) == "approve"
        )
        self.assertEqual(approvals, ["recheck", "run_check"])
        recheck = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "recheck"
        )
        text = ast.unparse(recheck)
        self.assertLess(
            text.index("adapters.hold.held"), text.index("transition(tx, asset.id, 'approve'")
        )
        self.assertLess(
            text.index("adapters.hold.held"), text.index("_decision_audit(tx, asset, 'approve'")
        )

    def test_a_hold_returns_before_the_approval_writes_anything(self) -> None:
        # SV2 Stage B, correction C2 (the exact-head review's F1): the approval's held branch is
        # an ``if`` on the hold port's answer whose one statement returns ``held``, and it comes
        # before every write of the approval: its audit row, the delivery reference, the
        # transition and the recompute. The port asked and its answer ignored fails here; the
        # profile suite's ``media.a_hold_stops_the_checks_approval`` shows it on PostgreSQL.
        # SV2-R (its brief's "Earlier tests"; DM-92 YY1, YY5): the same rule holds for every
        # approval, run_check's (the check's and the off branch's, one approval) and the
        # recheck's, which writes no recompute (its photo stays approved).
        self.held_before_every_write("run_check", recomputes=True)
        self.held_before_every_write("recheck", recomputes=False)

    def held_before_every_write(self, step: str, *, recomputes: bool) -> None:
        tree = modules()["media.py"]
        function = next(
            node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == step
        )
        body = next(
            node
            for node in function.body
            if isinstance(node, ast.FunctionDef) and node.name == "body"
        )
        approving = [
            index
            for index, statement in enumerate(body.body)
            if isinstance(statement, ast.If)
            and ast.unparse(statement.test) == "decided.decision == 'approve'"
        ]
        self.assertEqual(len(approving), 1)
        branch = body.body[approving[0]]
        assert isinstance(branch, ast.If)
        guards = [
            index
            for index, statement in enumerate(branch.body)
            if isinstance(statement, ast.If)
            and ast.unparse(statement.test) == "adapters.hold.held(asset.id)"
        ]
        self.assertEqual(len(guards), 1)
        guard = branch.body[guards[0]]
        assert isinstance(guard, ast.If)
        self.assertEqual(
            [ast.unparse(statement) for statement in guard.body],
            ["return Result('no_change', reason='held')"],
        )
        self.assertEqual(guard.orelse, [])
        # Nothing before the guard writes, in the check's body or in the approval's branch; and
        # every write of the approval comes after it.
        earlier = "\n".join(
            ast.unparse(statement)
            for statement in [*body.body[: approving[0]], *branch.body[: guards[0]]]
        )
        later = "\n".join(ast.unparse(statement) for statement in branch.body[guards[0] + 1 :])
        # SV2-R's correction C1 (the carried entry N-d): a queryset update, a bulk creation and an
        # outbox event are writes too.
        for write in (
            "_decision_audit(",
            "transition(",
            "delivery_reference(",
            "recompute.recompute(",
            ".save(",
            ".create(",
            ".update(",
            "bulk_create",
            "events.emit(",
        ):
            with self.subTest(step=step, write=write):
                self.assertNotIn(write, earlier)
        for write in (
            "_decision_audit(tx, asset, 'approve'",
            "transition(tx, asset.id, 'approve'",
            "adapters.storage.delivery_reference(variant.key)",
            *(("recompute.recompute(tx, account_id, now",) if recomputes else ()),
        ):
            with self.subTest(step=step, write=write):
                self.assertIn(write, later)
        if not recomputes:
            self.assertNotIn("recompute.recompute(", later)
        # The port is asked once in the step, at this guard only.
        self.assertEqual(ast.unparse(body).count("adapters.hold.held("), 1)


def _body(step: str) -> ast.FunctionDef:
    """The transaction body of one step of ``media.py``."""
    function = next(
        node
        for node in modules()["media.py"].body
        if isinstance(node, ast.FunctionDef) and node.name == step
    )
    return next(
        node for node in function.body if isinstance(node, ast.FunctionDef) and node.name == "body"
    )


class PhotoCheckToggleTests(unittest.TestCase):
    """SV2-R (its brief's R2; OD-68; DM-84 section 5; DM-91 XX6): the photo check's toggle in
    ``run_check`` and the recheck. The profile suite's ``sv2r.`` cases drive both on PostgreSQL."""

    TOGGLE_READ = (
        "settings_store.read_shared(tx, [ps.ONBOARDING_CONSENT, ps.PHOTO_CHECK, ps.MEDIA_POLICY])"
    )

    def statements(self, step: str) -> list[str]:
        return [ast.unparse(statement) for statement in _body(step).body]

    def test_each_step_reads_the_toggle_in_its_one_read_shared_call_in_name_order(self) -> None:
        for step in ("run_check", "recheck"):
            with self.subTest(step=step):
                statements = self.statements(step)
                self.assertEqual(statements[0], "lock_account(tx, account_id)")
                self.assertIn(self.TOGGLE_READ, statements[1])
                text = ast.unparse(_body(step))
                self.assertEqual(text.count("settings_store.read_shared("), 1)
                # The names are written in D19's order, and read_shared sorts them anyway.
                names = ["ps.ONBOARDING_CONSENT", "ps.PHOTO_CHECK", "ps.MEDIA_POLICY"]
                self.assertEqual(
                    [ps.ONBOARDING_CONSENT, ps.PHOTO_CHECK, ps.MEDIA_POLICY],
                    sorted([ps.MEDIA_POLICY, ps.ONBOARDING_CONSENT, ps.PHOTO_CHECK]),
                )
                positions = [statements[1].index(name) for name in names]
                self.assertEqual(positions, sorted(positions))

    def test_the_off_branch_calls_no_check_port_and_records_the_toggles_own_reason(self) -> None:
        body = _body("run_check")
        branch = next(
            statement
            for statement in body.body
            if isinstance(statement, ast.If) and ast.unparse(statement.test) == "checking"
        )
        on = "\n".join(ast.unparse(statement) for statement in branch.body)
        off = "\n".join(ast.unparse(statement) for statement in branch.orelse)
        self.assertIn("adapters.check.decide(", on)
        self.assertIn("md.CHECK_SUBJECT, md.APPROVED_BY_CHECK", on)
        self.assertNotIn("adapters.check", off)
        self.assertNotIn("md.CHECK_SUBJECT", off)
        self.assertNotIn("md.APPROVED_BY_CHECK", off)
        self.assertIn("decided = md.CheckDecision('approve')", off)
        self.assertIn("subject, approval = (md.PHOTO_CHECK_OFF_SUBJECT, md.PHOTO_CHECK_OFF)", off)
        # The check port is asked nowhere else in run_check, and the toggle is read as a strict
        # boolean, after the one read_shared call.
        text = ast.unparse(body)
        self.assertEqual(text.count("adapters.check.decide("), 1)
        self.assertIn("checking = found[ps.PHOTO_CHECK].content['enabled'] is True", text)
        # The restriction stops the off branch as it stops the check: it comes before the branch.
        self.assertLess(text.index("asset.restriction_ref is not None"), text.index("if checking"))
        # The one approval records the branch's subject and reason.
        self.assertIn("_decision_audit(tx, asset, 'approve', approval, subject=subject)", text)
        self.assertNotEqual(md.PHOTO_CHECK_OFF_SUBJECT, md.CHECK_SUBJECT)
        self.assertNotEqual(md.PHOTO_CHECK_OFF, md.APPROVED_BY_CHECK)
        self.assertTrue(ps.staff_subject_ok(md.PHOTO_CHECK_OFF_SUBJECT))
        self.assertTrue(ps.reason_ok(md.PHOTO_CHECK_OFF))

    def test_the_recheck_changes_nothing_while_the_toggle_is_off(self) -> None:
        statements = self.statements("recheck")
        text = "\n".join(statements)
        guard = next(
            index
            for index, statement in enumerate(_body("recheck").body)
            if isinstance(statement, ast.If)
            and ast.unparse(statement.test)
            == "settings[ps.PHOTO_CHECK].content['enabled'] is not True"
        )
        branch = _body("recheck").body[guard]
        assert isinstance(branch, ast.If)
        self.assertEqual(
            [ast.unparse(statement) for statement in branch.body],
            ["return Result('no_change', reason='photo_check_off')"],
        )
        earlier = "\n".join(statements[:guard])
        for call in ("adapters.", "_decision_audit(", "transition(", "recompute.", ".save("):
            with self.subTest(call=call):
                self.assertNotIn(call, earlier)
        # Then only a photo approved under the toggle's reason, then the check port, once.
        self.assertLess(text.index("photo_check_off"), text.index("not_awaiting_recheck"))
        self.assertLess(text.index("not_awaiting_recheck"), text.index("adapters.check.decide("))
        self.assertEqual(text.count("adapters.check.decide("), 1)

    def test_the_recheck_records_the_checks_decision_and_its_rejection_recomputes(self) -> None:
        body = _body("recheck")
        branches = {
            ast.unparse(statement.test): "\n".join(ast.unparse(s) for s in statement.body)
            for statement in body.body
            if isinstance(statement, ast.If)
        }
        approve = branches["decided.decision == 'approve'"]
        self.assertIn("_decision_audit(tx, asset, 'approve', md.APPROVED_BY_CHECK)", approve)
        self.assertNotIn("subject=", approve)
        self.assertIn("review_ref=review_ref", approve)
        reject = branches["decided.decision == 'reject'"]
        self.assertIn("transition(tx, asset.id, 'reject'", reject)
        self.assertLess(
            reject.index("transition(tx, asset.id, 'reject'"),
            reject.index("recompute.recompute(tx, account_id, now, writer=recompute.OTHER_FLOW)"),
        )
        self.assertEqual(
            branches["decided.decision == 'undecided'"],
            "return Result('no_change', reason='undecided')",
        )
        # The recheck finds a photo by the toggle's own audit row: its subject, reason and action.
        helper = next(
            node
            for node in modules()["media.py"].body
            if isinstance(node, ast.FunctionDef) and node.name == "_approvals_while_off"
        )
        source = ast.unparse(helper)
        for part in (
            "action='approve'",
            "object_type='media_asset'",
            "staff_subject=md.PHOTO_CHECK_OFF_SUBJECT",
            "reason_code=md.PHOTO_CHECK_OFF",
        ):
            with self.subTest(part=part):
                self.assertIn(part, source)

    def test_the_read_lists_only_approved_photos_of_active_accounts(self) -> None:
        read = next(
            node
            for node in modules()["media.py"].body
            if isinstance(node, ast.FunctionDef) and node.name == "awaiting_recheck"
        )
        source = ast.unparse(read)
        for part in (
            "state=md.APPROVED",
            "account__state='active'",
            "review_ref__in=_approvals_while_off().values('id')",
        ):
            with self.subTest(part=part):
                self.assertIn(part, source)
        # It writes and locks nothing: no transaction, no lock, no port.
        for call in ("run(", "lock_account", "select_for_update", "adapters", ".save(", "create("):
            with self.subTest(call=call):
                self.assertNotIn(call, source)


class AccountStateTests(unittest.TestCase):
    """SV2 Stage B, correction C1 (DM-58 item 9): the purge and the store's deletion
    acknowledgment take the account row in any account state; the purge still asks the hold port
    before the store, and every other photo step keeps its gate (``LockOrderTests``)."""

    def bodies(self) -> dict[str, list[str]]:
        found = {}
        for node in modules()["media.py"].body:
            if isinstance(node, ast.FunctionDef):
                for inner in node.body:
                    if isinstance(inner, ast.FunctionDef) and inner.name == "body":
                        found[node.name] = [ast.unparse(statement) for statement in inner.body]
        return found

    def test_the_purge_takes_the_row_in_any_state_and_asks_the_hold_port_first(self) -> None:
        purge = self.bodies()["request_purge"]
        self.assertEqual(purge[0], "lock_account_any_state(tx, account_id)")
        text = "\n".join(purge)
        self.assertEqual(text.count("adapters.hold.held(asset.id)"), 1)
        self.assertEqual(text.count("adapters.storage.delete(keys)"), 1)
        self.assertLess(
            text.index("adapters.hold.held(asset.id)"), text.index("adapters.storage.delete(keys)")
        )
        self.assertLess(
            text.index("adapters.hold.held(asset.id)"), text.index("asset.purge_requested_at = now")
        )

    def test_the_acknowledgment_takes_the_row_in_any_state_and_needs_a_requested_purge(
        self,
    ) -> None:
        acknowledgment = self.bodies()["acknowledge_deletion"]
        self.assertEqual(acknowledgment[0], "lock_account_any_state(tx, account_id)")
        text = "\n".join(acknowledgment)
        self.assertIn(
            "if asset.state != md.REMOVAL_PENDING or asset.purge_requested_at is None:", text
        )
        self.assertLess(
            text.index("asset.purge_requested_at is None"), text.index("held.deleted_at = now")
        )

    def test_every_other_photo_step_keeps_its_gate(self) -> None:
        for name, statements in self.bodies().items():
            if name in ("request_purge", "acknowledge_deletion"):
                continue
            with self.subTest(step=name):
                self.assertIn(
                    statements[0],
                    ("lock_account(tx, account_id)", "read_account_shared(tx, account_id)"),
                )


if __name__ == "__main__":
    unittest.main()
