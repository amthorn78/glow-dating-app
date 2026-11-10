"""SV2 Stage A, D2: the settings' closed schemas, launch defaults and fixed limits (pure; the
proof's profile suite publishes through the store on PostgreSQL)."""

import ast
import copy
import importlib.util
import re
import unittest
from pathlib import Path
from typing import Any

from glow_domain import profile_fields as pf
from glow_domain import profile_settings as ps

API_ROOT = Path(__file__).resolve().parents[1]
SEED_MIGRATION = API_ROOT / "glow_persistence" / "migrations" / "0007_settings_launch_defaults.py"
POLICY_VERSION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")


def seed_module() -> Any:
    spec = importlib.util.spec_from_file_location("seed_0007", SEED_MIGRATION)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def crossing(name: str, change: Any) -> tuple[str, ...]:
    content = copy.deepcopy(ps.LAUNCH_DEFAULTS[name])
    change(content)
    return ps.publication_refusals(
        name,
        content,
        ps.LAUNCH_DEFAULTS[name],
        onboarding_consent_version=ps.policy_version(ps.ONBOARDING_CONSENT, 1),
    )


class LaunchDefaultTests(unittest.TestCase):
    def test_every_setting_has_a_launch_default_that_its_schema_accepts(self) -> None:
        self.assertEqual(set(ps.LAUNCH_DEFAULTS), set(ps.ALL_SETTINGS))
        for name in ps.ALL_SETTINGS:
            with self.subTest(setting=name):
                self.assertEqual(ps.publication_refusals(name, ps.LAUNCH_DEFAULTS[name]), ())
                # Republishing the current content is allowed (no fixed limit crossed).
                self.assertEqual(
                    ps.publication_refusals(
                        name,
                        ps.LAUNCH_DEFAULTS[name],
                        ps.LAUNCH_DEFAULTS[name],
                        onboarding_consent_version=ps.policy_version(ps.ONBOARDING_CONSENT, 1),
                    ),
                    (),
                )

    def test_the_launch_values_are_od60s_and_od61s(self) -> None:
        ids = {
            field: [v["id"] for v in ps.LAUNCH_DEFAULTS[name]["values"]]
            for field, name in ps.LIST_SETTINGS.items()
        }
        self.assertEqual(ids["gender"], ["woman", "man", "non-binary"])
        self.assertEqual(
            ids["looking_for"],
            ["long-term", "short-term", "casual", "new-friends", "figuring-it-out"],
        )
        self.assertEqual(
            ids["relationship_status"],
            ["single", "separated-or-divorcing", "partnered-open-or-non-monogamous"],
        )
        # OD-60 names no starting orientation list: none is invented.
        self.assertEqual(ids["orientation"], [])
        limits = {f: ps.LAUNCH_DEFAULTS[n]["pick_limit"] for f, n in ps.LIST_SETTINGS.items()}
        self.assertEqual(
            limits, {"gender": 1, "orientation": 1, "looking_for": None, "relationship_status": 1}
        )
        self.assertTrue(all(ps.LAUNCH_DEFAULTS[ps.NARROWING]["narrowable"].values()))
        self.assertEqual(
            ps.LAUNCH_DEFAULTS[ps.AGE_RANGE],
            {"default_minimum": 18, "default_maximum": None, "direction": "both_ways"},
        )
        location = ps.LAUNCH_DEFAULTS[ps.LOCATION]
        self.assertTrue(location["chosen_area"] and location["approximate_location"])
        # OD-60 names no distance choices: one that filters nothing.
        self.assertEqual([c["id"] for c in location["distance_choices"]], ["anywhere"])
        for name in (ps.RESURFACING, ps.UNDO, ps.REMATCH):
            self.assertFalse(ps.LAUNCH_DEFAULTS[name]["enabled"])
        history = ps.LAUNCH_DEFAULTS[ps.HISTORY]
        self.assertTrue(all(history[cause] == "read_only" for cause in ps.HISTORY_CAUSES))
        self.assertEqual(ps.LAUNCH_DEFAULTS[ps.STAFF_APPROVAL]["enabled"], False)
        self.assertEqual(ps.LAUNCH_REASONS[ps.STAFF_APPROVAL], "OD-61")
        self.assertEqual(
            {ps.LAUNCH_REASONS[name] for name in ps.ALL_SETTINGS if name != ps.STAFF_APPROVAL},
            {"OD-60"},
        )

    def test_the_development_wording_says_what_d6_asks(self) -> None:
        onboarding = ps.LAUNCH_DEFAULTS[ps.ONBOARDING_CONSENT]["text"]
        sensitive = ps.LAUNCH_DEFAULTS[ps.SENSITIVE_CONSENT]["text"]
        for text in (onboarding, sensitive):
            self.assertTrue(text.startswith("Development text"))
        self.assertIn("can reveal your sexual orientation", onboarding)
        self.assertIn("stays readable", onboarding)
        self.assertIn("learns it about everyone they are shown", sensitive)

    def test_the_seed_migration_holds_the_same_content(self) -> None:
        seed = seed_module()
        self.assertEqual(seed.SEED, {name: ps.LAUNCH_DEFAULTS[name] for name in ps.ALL_SETTINGS})
        self.assertEqual(seed.REASONS, ps.LAUNCH_REASONS)
        self.assertEqual(seed.LAUNCH_SUBJECT, ps.LAUNCH_SUBJECT)
        tree = ast.parse(SEED_MIGRATION.read_text(encoding="utf-8"))
        names = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
        # No outbox event is seeded: nothing has been published yet.
        self.assertNotIn("OutboxEvent", SEED_MIGRATION.read_text(encoding="utf-8"))
        self.assertIn("RunPython", names)

    def test_labels_are_the_contracts_policy_versions(self) -> None:
        for name in ps.ALL_SETTINGS:
            self.assertRegex(ps.policy_version(name, 1), POLICY_VERSION)
        version = ps.catalog_version({name: 3 for name in ps.CATALOG_SETTINGS})
        self.assertEqual(version, "catalog.3.3.3.3.3.3.3")
        self.assertRegex(version, POLICY_VERSION)
        self.assertLessEqual(len(version), 100)


class FixedLimitTests(unittest.TestCase):
    """D2: a publication that crosses a fixed limit is refused, naming the limit."""

    def test_each_fixed_limit_refuses_its_crossing(self) -> None:
        def add(value_id: str, retired: bool = False) -> Any:
            return lambda c: c["values"].append(
                {"id": value_id, "label": "Fixture", "retired": retired}
            )

        def setter(**changes: Any) -> Any:
            return lambda c: c.update(changes)

        cases = (
            (ps.GENDER_LIST, ps.LIST_RESERVED_VALUE, add("all")),
            (ps.GENDER_LIST, ps.LIST_RESERVED_VALUE, add("not-stated")),
            (ps.GENDER_LIST, ps.LIST_VALUE_REMOVED, lambda c: c["values"].pop(0)),
            (ps.GENDER_LIST, ps.MATCHING_USES_LIST_VALUES, setter(matching="own_words")),
            (
                ps.LOOKING_FOR_LIST,
                ps.LIST_LIVE_VALUES,
                lambda c: c["values"].extend(
                    {"id": f"many-{i}", "label": "Many", "retired": False} for i in range(46)
                ),
            ),
            (ps.AGE_RANGE, ps.AGE_FLOOR_18, setter(default_minimum=17)),
            (ps.AGE_RANGE, ps.AGE_FLOOR_18, setter(default_maximum=17)),
            (ps.LOCATION, ps.NO_COORDINATES_OR_DISTANCE, setter(store_coordinates=True)),
            (ps.LOCATION, ps.NO_COORDINATES_OR_DISTANCE, setter(show_distance=True)),
            (ps.REMATCH, ps.REMATCH_NEVER_AFTER_BLOCK_OR_REPORT, setter(after_block=True)),
            (ps.REMATCH, ps.REMATCH_NEVER_AFTER_BLOCK_OR_REPORT, setter(after_report=True)),
            (ps.HISTORY, ps.UNMATCH_BLOCK_HIDDEN, setter(unmatch="read_only")),
            (ps.HISTORY, ps.UNMATCH_BLOCK_HIDDEN, setter(block="read_only")),
            (ps.HISTORY, ps.DELETION_AS_UNMATCH, setter(deletion="read_only")),
            (ps.NARROWING, ps.SHOW_ME_NEVER_SHOWN, setter(show_me_shown=True)),
            (ps.NARROWING, ps.NOT_STATED_KEEP_ALL_ONLY, setter(not_stated_seen_by="everyone")),
            (
                ps.STAFF_APPROVAL,
                ps.STAFF_APPROVAL_IDENTITY_ONLY,
                setter(stands_in_for=["identity_verification", "adult_check"]),
            ),
        )
        for name, limit, change in cases:
            with self.subTest(setting=name, limit=limit):
                self.assertIn(limit, crossing(name, change))
                self.assertIn(limit, ps.FIXED_LIMITS)

    def test_fifty_live_values_are_allowed_and_retired_ones_do_not_count(self) -> None:
        content = copy.deepcopy(ps.LAUNCH_DEFAULTS[ps.LOOKING_FOR_LIST])
        content["values"] += [{"id": f"m-{i}", "label": "M", "retired": False} for i in range(45)]
        self.assertEqual(
            ps.publication_refusals(
                ps.LOOKING_FOR_LIST, content, ps.LAUNCH_DEFAULTS[ps.LOOKING_FOR_LIST]
            ),
            (),
        )
        content["values"].append({"id": "m-retired", "label": "M", "retired": True})
        self.assertEqual(ps.publication_refusals(ps.LOOKING_FOR_LIST, content), ())
        content["values"].append({"id": "m-51", "label": "M", "retired": False})
        self.assertIn(ps.LIST_LIVE_VALUES, ps.publication_refusals(ps.LOOKING_FOR_LIST, content))

    def test_h_made_more_readable_needs_new_consent_wording(self) -> None:
        hidden = copy.deepcopy(ps.LAUNCH_DEFAULTS[ps.HISTORY])
        hidden["own_pause"] = "hidden"
        v1 = ps.policy_version(ps.ONBOARDING_CONSENT, 1)
        v2 = ps.policy_version(ps.ONBOARDING_CONSENT, 2)
        # Less readable: no consent needed.
        self.assertEqual(
            ps.publication_refusals(
                ps.HISTORY, hidden, ps.LAUNCH_DEFAULTS[ps.HISTORY], onboarding_consent_version=v1
            ),
            (),
        )
        readable = copy.deepcopy(hidden)
        readable["own_pause"] = "read_only"
        # More readable, naming the same wording as before: refused.
        self.assertIn(
            ps.MORE_READABLE_NEEDS_CONSENT,
            ps.publication_refusals(ps.HISTORY, readable, hidden, onboarding_consent_version=v1),
        )
        # Naming a version that is not the current one: refused.
        readable["consent_policy_version"] = v2
        self.assertIn(
            ps.MORE_READABLE_NEEDS_CONSENT,
            ps.publication_refusals(ps.HISTORY, readable, hidden, onboarding_consent_version=v1),
        )
        # Naming the current, new wording: allowed.
        self.assertEqual(
            ps.publication_refusals(ps.HISTORY, readable, hidden, onboarding_consent_version=v2),
            (),
        )

    def test_h_cannot_cross_its_limit_in_two_publications(self) -> None:
        # C2 (DM-55, Z6): a publication that makes nothing more readable keeps the version the
        # current setting names, so the label cannot move first and a cause become readable after.
        hidden = copy.deepcopy(ps.LAUNCH_DEFAULTS[ps.HISTORY])
        hidden["own_pause"] = "hidden"
        v1 = ps.policy_version(ps.ONBOARDING_CONSENT, 1)
        v2 = ps.policy_version(ps.ONBOARDING_CONSENT, 2)
        # The first step: the label alone moves to the current version. Refused.
        relabelled = copy.deepcopy(hidden)
        relabelled["consent_policy_version"] = v2
        self.assertEqual(
            ps.publication_refusals(ps.HISTORY, relabelled, hidden, onboarding_consent_version=v2),
            (ps.MORE_READABLE_NEEDS_CONSENT,),
        )
        # The second step, had the first applied, names the version already accepted: refused.
        readable = copy.deepcopy(relabelled)
        readable["own_pause"] = "read_only"
        self.assertIn(
            ps.MORE_READABLE_NEEDS_CONSENT,
            ps.publication_refusals(
                ps.HISTORY, readable, relabelled, onboarding_consent_version=v2
            ),
        )
        # Less readable with the label kept, or no change at all: allowed.
        self.assertEqual(
            ps.publication_refusals(
                ps.HISTORY, hidden, ps.LAUNCH_DEFAULTS[ps.HISTORY], onboarding_consent_version=v2
            ),
            (),
        )
        self.assertEqual(
            ps.publication_refusals(ps.HISTORY, hidden, hidden, onboarding_consent_version=v1), ()
        )

    def test_closed_schemas_refuse_unknown_keys_and_types(self) -> None:
        for name in ps.ALL_SETTINGS:
            with self.subTest(setting=name):
                extra = copy.deepcopy(ps.LAUNCH_DEFAULTS[name])
                extra["fixture_unknown_key"] = True
                self.assertEqual(ps.publication_refusals(name, extra), (ps.SCHEMA,))
                self.assertEqual(ps.publication_refusals(name, []), (ps.SCHEMA,))
        self.assertEqual(ps.publication_refusals("profile.unknown", {}), (ps.SCHEMA,))
        bad_label = copy.deepcopy(ps.LAUNCH_DEFAULTS[ps.GENDER_LIST])
        bad_label["values"][0]["label"] = "   "
        self.assertEqual(ps.publication_refusals(ps.GENDER_LIST, bad_label), (ps.SCHEMA,))
        enabled = {"enabled": True, "waiting_days": None}
        self.assertEqual(ps.publication_refusals(ps.RESURFACING, enabled), (ps.SCHEMA,))

    def test_staff_subjects_and_reasons(self) -> None:
        self.assertTrue(ps.staff_subject_ok("staff:console-1"))
        self.assertTrue(ps.staff_subject_ok(ps.LAUNCH_SUBJECT))
        for bad in ("", "member:x", "staff:", "staff:a b", 7, "staff:" + "x" * 201):
            self.assertFalse(ps.staff_subject_ok(bad))
        self.assertTrue(ps.reason_ok("OD-60"))
        self.assertFalse(ps.reason_ok(""))
        self.assertFalse(ps.reason_ok("x" * 101))

    def test_field_lists_come_from_the_settings(self) -> None:
        field = ps.field_list(
            pf.GENDER, ps.LAUNCH_DEFAULTS[ps.GENDER_LIST], ps.LAUNCH_DEFAULTS[ps.NARROWING], 4
        )
        self.assertEqual(field.live_ids, {"woman", "man", "non-binary"})
        self.assertEqual((field.pick_limit, field.narrowable, field.setting_version), (1, True, 4))


if __name__ == "__main__":
    unittest.main()
