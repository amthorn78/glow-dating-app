"""SV2 Stage A, D7: the adult check's rule and the age state's one transition (pure; the proof's
profile suite runs the check, its rerun and the transition's lock order on PostgreSQL)."""

import os
import subprocess
import sys
import unittest
from dataclasses import fields
from datetime import UTC, date, datetime
from pathlib import Path
from uuid import uuid4

from glow_domain.identity import (
    ADULT_AGE,
    ADULT_POLICY_VERSION,
    AccountId,
    AdultOutcome,
    AgeAssurance,
    AgeAssuranceMethod,
    AgeAssuranceState,
    AgeTransition,
    adult_outcome,
    whole_years,
)

API_ROOT = Path(__file__).resolve().parents[1]


class AdultRuleTests(unittest.TestCase):
    def test_whole_years_count_a_birthday_only_once_it_has_come(self) -> None:
        self.assertEqual(whole_years(date(1990, 6, 15), date(2026, 6, 14)), 35)
        self.assertEqual(whole_years(date(1990, 6, 15), date(2026, 6, 15)), 36)
        self.assertEqual(whole_years(date(1990, 6, 15), date(1990, 6, 15)), 0)

    def test_a_29_february_birthday_falls_on_1_march_in_a_common_year(self) -> None:
        # P04's rule (``leapBirthday: 'march_1'``).
        born = date(2008, 2, 29)
        self.assertEqual(whole_years(born, date(2026, 2, 28)), 17)
        self.assertEqual(whole_years(born, date(2026, 3, 1)), 18)
        self.assertIs(adult_outcome(born, date(2026, 2, 28)), AdultOutcome.UNDER_AGE)
        self.assertIs(adult_outcome(born, date(2026, 3, 1)), AdultOutcome.PASS)
        # In a leap year the birthday is 29 February itself.
        self.assertEqual(whole_years(born, date(2028, 2, 28)), 19)
        self.assertEqual(whole_years(born, date(2028, 2, 29)), 20)

    def test_18_on_the_servers_date_passes_and_a_day_short_does_not(self) -> None:
        self.assertEqual(ADULT_AGE, 18)
        today = date(2026, 11, 10)
        self.assertIs(adult_outcome(date(2008, 11, 10), today), AdultOutcome.PASS)
        self.assertIs(adult_outcome(date(2008, 11, 11), today), AdultOutcome.UNDER_AGE)
        self.assertIs(adult_outcome(today, today), AdultOutcome.UNDER_AGE)
        self.assertIs(adult_outcome(date(2026, 11, 11), today), AdultOutcome.FUTURE)


class AgeTransitionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.account = AccountId(str(uuid4()))
        self.now = datetime.now(UTC)

    def test_an_adult_state_carries_its_date_and_the_rules_version(self) -> None:
        change = AgeTransition(
            self.account, AgeAssuranceState.SELF_DECLARED_ADULT, date(1990, 6, 15), self.now
        )
        self.assertIs(change.method, AgeAssuranceMethod.SELF_DECLARATION)
        self.assertEqual(change.policy_version, ADULT_POLICY_VERSION)
        back = AgeTransition(self.account, AgeAssuranceState.UNKNOWN, None, self.now)
        self.assertIs(back.method, AgeAssuranceMethod.NONE)
        self.assertIsNone(back.policy_version)

    def test_a_transition_that_does_not_fit_its_state_is_refused(self) -> None:
        adult = AgeAssuranceState.SELF_DECLARED_ADULT
        with self.assertRaises(ValueError):
            AgeTransition(self.account, adult, None, self.now)
        with self.assertRaises(ValueError):
            AgeTransition(self.account, adult, datetime(1990, 6, 15, tzinfo=UTC), self.now)
        with self.assertRaises(ValueError):
            AgeTransition(self.account, AgeAssuranceState.UNKNOWN, date(1990, 6, 15), self.now)
        with self.assertRaises(ValueError):
            AgeTransition(self.account, adult, date(1990, 6, 15), datetime(2026, 11, 10))
        with self.assertRaises(TypeError):
            AgeTransition(str(uuid4()), adult, date(1990, 6, 15), self.now)  # type: ignore[arg-type]

    def test_the_age_state_type_still_carries_no_birth_date(self) -> None:
        # D7: the date's one home is the age state's row; SV1's type is unchanged.
        self.assertEqual(
            [field.name for field in fields(AgeAssurance)],
            ["account_id", "state", "method", "recorded_at", "policy_version"],
        )

    def test_the_transition_refuses_outside_a_transaction(self) -> None:
        # It runs only inside the caller's transaction, after the account row lock (DM-13 4.1).
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import django\ndjango.setup()\n"
                "from datetime import UTC, date, datetime\nfrom uuid import uuid4\n"
                "from glow_domain.identity import AccountId, AgeAssuranceState, AgeTransition\n"
                "from glow_identity.age import AgeTransitionRefused, OrmAgeAssurance\n"
                "change = AgeTransition(AccountId(str(uuid4())), "
                "AgeAssuranceState.SELF_DECLARED_ADULT, date(1990, 6, 15), datetime.now(UTC))\n"
                "try:\n    OrmAgeAssurance().transition(change)\n"
                "except AgeTransitionRefused as exc:\n    print('refused', exc)\n",
            ],
            cwd=API_ROOT,
            env={
                "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                "LANG": "C.UTF-8",
                "DJANGO_SETTINGS_MODULE": "tests.profiles_offline_settings",
            },
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "refused transaction_required")


if __name__ == "__main__":
    unittest.main()
