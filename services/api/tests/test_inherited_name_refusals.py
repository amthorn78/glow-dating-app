"""SV4 A1 (its brief's D7; M05's finding 22): the fixture guards refuse by presence, beside
``FORBIDDEN_CONNECTION_NAMES`` (which does not change), a ``PG`` prefix, the names M05 found
accepted and the families they stand for: Railway's database and Redis names and the chat
provider's. Each is refused in the same presence step, before any value is read, and its
value never reaches the refusal. Every name the API itself reads (``GLOW_*``, among them
``GLOW_RAILWAY_*``, and the public mobile names) still passes the rule. The proof's copy of
the rule is pinned to this one by ``proofs/postgres-ordering/tests/test_settings_refusals.py``.
"""

from collections.abc import Iterator, Mapping
from unittest import TestCase

from glow_api.configuration import ConfigurationError, load_configuration
from glow_api.configuration_profiles import (
    FORBIDDEN_CONNECTION_NAMES,
    FORBIDDEN_INHERITED_NAMES,
    FORBIDDEN_INHERITED_PREFIXES,
    PROFILE_NAMES,
    PUBLIC_NAMES,
    SECRET_SLOT_NAMES,
    IssueCategory,
    forbidden_configuration,
    inherited_name_refused,
)

# The names M05 ran load_configuration with and found accepted (its finding 22).
M05_ACCEPTED = (
    "DATABASE_PUBLIC_URL",
    "PGPASSFILE",
    "PGSERVICE",
    "POSTGRES_PASSWORD",
    "REDIS_PUBLIC_URL",
    "REDISPASSWORD",
    "STREAM_API_SECRET",
)
# Members of the families those names stand for, each refused by its prefix.
FAMILIES = (
    "PGSSLMODE",
    "PGOPTIONS",
    "PGSERVICEFILE",
    "POSTGRES_USER",
    "POSTGRES_DB",
    "REDISHOST",
    "REDISPORT",
    "REDISUSER",
    "REDIS_PASSWORD",
    "STREAM_API_KEY",
    "STREAM_APP_ID",
)
SYNTHETIC = "synthetic-inherited-value-not-a-secret"


class Unreadable(Mapping[str, str]):
    """An environment whose refused name's value raises if anything reads it."""

    def __init__(self, name: str) -> None:
        self.name = name

    def __iter__(self) -> Iterator[str]:
        return iter(("GLOW_ENV", self.name))

    def __len__(self) -> int:
        return 2

    def __getitem__(self, name: str) -> str:
        if name == self.name:
            raise AssertionError(f"the value of {name} was read")
        if name == "GLOW_ENV":
            return "test"
        raise KeyError(name)


class InheritedNameRefusalTests(TestCase):
    def test_the_rule_is_its_own_constant_beside_the_unchanged_list(self) -> None:
        self.assertEqual(FORBIDDEN_INHERITED_NAMES, frozenset(M05_ACCEPTED))
        self.assertEqual(FORBIDDEN_INHERITED_PREFIXES, ("PG", "POSTGRES_", "REDIS", "STREAM_"))
        self.assertFalse(FORBIDDEN_INHERITED_NAMES & FORBIDDEN_CONNECTION_NAMES)

    def test_each_name_m05_found_accepted_is_refused_before_its_value_is_read(self) -> None:
        for name in M05_ACCEPTED:
            with self.subTest(name=name):
                self.assertTrue(inherited_name_refused(name))
                with self.assertRaises(ConfigurationError) as raised:
                    load_configuration(Unreadable(name))
                self.assertIn(name, str(raised.exception))

    def test_each_family_member_is_refused_before_its_value_is_read(self) -> None:
        for name in FAMILIES:
            with self.subTest(name=name):
                self.assertTrue(inherited_name_refused(name))
                with self.assertRaises(ConfigurationError):
                    load_configuration(Unreadable(name))

    def test_the_refusal_is_the_inherited_connection_issue_and_names_no_value(self) -> None:
        for name in (*M05_ACCEPTED, *FAMILIES):
            with self.subTest(name=name):
                issues = forbidden_configuration({"GLOW_ENV": "test", name: SYNTHETIC})
                self.assertEqual(len(issues), 1)
                issue = issues[0]
                self.assertEqual(
                    (issue.category, issue.code, issue.variables),
                    (IssueCategory.CONTRADICTORY, "inherited_connection", (name,)),
                )
                self.assertNotIn(SYNTHETIC, issue.safe_message())
                with self.assertRaises(ConfigurationError) as raised:
                    load_configuration({"GLOW_ENV": "test", name: SYNTHETIC})
                self.assertNotIn(SYNTHETIC, str(raised.exception))

    def test_an_empty_value_is_refused_too(self) -> None:
        for name in M05_ACCEPTED:
            with self.subTest(name=name), self.assertRaises(ConfigurationError):
                load_configuration({"GLOW_ENV": "test", name: ""})

    def test_every_name_the_api_reads_passes_the_rule(self) -> None:
        for name in sorted(PROFILE_NAMES | SECRET_SLOT_NAMES | PUBLIC_NAMES):
            with self.subTest(name=name):
                self.assertFalse(inherited_name_refused(name))
        for name in ("GLOW_RAILWAY_PROJECT_ID", "GLOW_RAILWAY_ENVIRONMENT_ID"):
            self.assertIn(name, PROFILE_NAMES)
            self.assertFalse(inherited_name_refused(name))
        # A clean test environment still loads.
        load_configuration({"GLOW_ENV": "test"})
