"""SV2 Stage A, D3: the four list fields, the "show me" sets, the two-way rule, own words and
display (pure; the proof's profile suite exercises them through the routes on PostgreSQL)."""

import json
import re
import unittest
from pathlib import Path

from glow_domain import profile_fields as pf

REPO_ROOT = Path(__file__).resolve().parents[3]

GENDER = pf.FieldList(
    pf.GENDER,
    (
        pf.ListValue("woman", "Woman", False),
        pf.ListValue("man", "Man", False),
        pf.ListValue("retired-value", "Retired", True),
    ),
    1,
    True,
    3,
)
LOOKING = pf.FieldList(
    pf.LOOKING_FOR,
    (pf.ListValue("casual", "Casual", False), pf.ListValue("long-term", "Long", False)),
    None,
    True,
    1,
)
ORIENTATION = pf.FieldList(pf.ORIENTATION, (pf.ListValue("fixture-a", "A", False),), 1, False, 2)


class OwnValueTests(unittest.TestCase):
    def test_values_within_the_pick_limit(self) -> None:
        self.assertIsNone(pf.own_value_refusal(pf.GENDER, ["woman"], GENDER))
        self.assertIsNone(pf.own_value_refusal(pf.LOOKING_FOR, ["casual", "long-term"], LOOKING))
        self.assertEqual(
            pf.own_value_refusal(pf.GENDER, ["woman", "man"], GENDER), pf.OVER_PICK_LIMIT
        )

    def test_unknown_retired_reserved_empty_and_duplicate_values_are_refused(self) -> None:
        self.assertEqual(pf.own_value_refusal(pf.GENDER, ["other"], GENDER), pf.UNKNOWN_VALUE)
        # A retired value is refused for a new choice, even one the member held.
        self.assertEqual(
            pf.own_value_refusal(pf.GENDER, ["retired-value"], GENDER), pf.RETIRED_VALUE
        )
        self.assertEqual(pf.own_value_refusal(pf.GENDER, [], GENDER), pf.EMPTY)
        self.assertEqual(pf.own_value_refusal(pf.GENDER, ["all"], GENDER), pf.RESERVED_VALUE)
        self.assertEqual(
            pf.own_value_refusal(pf.LOOKING_FOR, ["casual", "casual"], LOOKING), pf.DUPLICATE
        )

    def test_not_stated_only_for_the_optional_fields(self) -> None:
        self.assertIsNone(pf.own_value_refusal(pf.ORIENTATION, ["not-stated"], ORIENTATION))
        self.assertEqual(pf.own_value_refusal(pf.GENDER, ["not-stated"], GENDER), pf.RESERVED_VALUE)
        self.assertEqual(
            pf.own_value_refusal(pf.ORIENTATION, ["not-stated", "fixture-a"], ORIENTATION),
            pf.RESERVED_VALUE,
        )
        self.assertEqual(pf.OPTIONAL_FIELDS, {pf.ORIENTATION, pf.RELATIONSHIP_STATUS})

    def test_what_carries_sensitive_data(self) -> None:
        self.assertTrue(pf.carries_sensitive(pf.ORIENTATION, ["fixture-a"], None))
        self.assertTrue(pf.carries_sensitive(pf.ORIENTATION, ["not-stated"], "Own words"))
        self.assertTrue(pf.carries_sensitive(pf.RELATIONSHIP_STATUS, ["single"], None))
        self.assertFalse(pf.carries_sensitive(pf.ORIENTATION, ["not-stated"], None))
        self.assertFalse(pf.carries_sensitive(pf.GENDER, ["woman"], "Own words"))


class ShowMeTests(unittest.TestCase):
    def test_all_or_a_narrowed_list_of_live_values(self) -> None:
        self.assertIsNone(pf.show_me_refusal(pf.GENDER, ["all"], GENDER))
        self.assertIsNone(pf.show_me_refusal(pf.GENDER, ["woman", "man"], GENDER))
        self.assertEqual(pf.show_me_refusal(pf.GENDER, [], GENDER), pf.EMPTY)
        self.assertEqual(pf.show_me_refusal(pf.GENDER, ["all", "man"], GENDER), pf.RESERVED_VALUE)
        self.assertEqual(
            pf.show_me_refusal(pf.ORIENTATION, ["not-stated"], ORIENTATION), pf.RESERVED_VALUE
        )
        self.assertEqual(pf.show_me_refusal(pf.GENDER, ["retired-value"], GENDER), pf.RETIRED_VALUE)
        self.assertEqual(pf.show_me_refusal(pf.GENDER, ["unknown"], GENDER), pf.UNKNOWN_VALUE)
        # A field members may not narrow by keeps all.
        self.assertEqual(
            pf.show_me_refusal(pf.ORIENTATION, ["fixture-a"], ORIENTATION), pf.NOT_NARROWABLE
        )
        self.assertIsNone(pf.show_me_refusal(pf.ORIENTATION, ["all"], ORIENTATION))


class TwoWayRuleTests(unittest.TestCase):
    """D3: a field matches when at least one of each person's values is in the other's set, for
    every field; all is a marker, and not stated is only in it."""

    def test_the_all_marker_includes_a_value_the_console_adds_and_not_stated(self) -> None:
        self.assertTrue(pf.sees(["all"], ["a-value-added-later"]))
        self.assertTrue(pf.sees(["all"], ["not-stated"]))
        self.assertTrue(pf.sees(["all"], []))
        self.assertFalse(pf.sees(["woman", "man"], ["a-value-added-later"]))

    def test_not_stated_is_in_no_narrowed_set(self) -> None:
        self.assertFalse(pf.sees(["fixture-a"], ["not-stated"]))
        self.assertFalse(pf.sees(["fixture-a"], []))

    def test_a_retired_value_stays_matchable(self) -> None:
        self.assertTrue(pf.sees(["retired-value"], ["retired-value"]))
        self.assertTrue(pf.sees(["all"], ["retired-value"]))

    def test_both_ways_for_every_field(self) -> None:
        alex = {pf.GENDER: ["woman"], pf.LOOKING_FOR: ["casual"]}
        sam = {pf.GENDER: ["man"], pf.LOOKING_FOR: ["casual", "long-term"]}
        all_sets = {field: ["all"] for field in pf.FIELDS}
        self.assertTrue(pf.two_way(alex, all_sets, sam, all_sets))
        alex_sets = dict(all_sets, gender=["man"])
        self.assertTrue(pf.two_way(alex, alex_sets, sam, all_sets))
        sam_sets = dict(all_sets, gender=["non-binary"])
        self.assertFalse(pf.two_way(alex, alex_sets, sam, sam_sets))
        narrowed_looking = dict(all_sets, looking_for=["long-term"])
        self.assertFalse(pf.two_way(alex, all_sets, sam, narrowed_looking))
        # A member who declines the sensitive consent states no orientation: seen by viewers who
        # keep all, not by one who narrowed orientation.
        narrower = dict(all_sets, orientation=["fixture-a"])
        self.assertTrue(pf.two_way(alex, all_sets, sam, all_sets))
        self.assertFalse(
            pf.two_way({**alex, pf.ORIENTATION: ["fixture-a"]}, narrower, sam, all_sets)
        )


class OwnWordsAndDisplayTests(unittest.TestCase):
    def test_own_words_are_bounded_text(self) -> None:
        self.assertIsNone(pf.own_words_refusal(pf.GENDER, "x" * 40))
        self.assertIsNone(pf.own_words_refusal(pf.ORIENTATION, "é" * 20))
        self.assertEqual(pf.own_words_refusal(pf.GENDER, "x" * 41), pf.OWN_WORDS_INVALID)
        self.assertEqual(pf.own_words_refusal(pf.GENDER, " 　﻿"), pf.OWN_WORDS_INVALID)
        self.assertEqual(pf.own_words_refusal(pf.GENDER, "a\ud800"), pf.OWN_WORDS_INVALID)
        self.assertEqual(pf.own_words_refusal(pf.LOOKING_FOR, "x"), pf.OWN_WORDS_NOT_ALLOWED)
        self.assertEqual(pf.shown_refusal(pf.LOOKING_FOR, False), pf.SHOWN_NOT_ALLOWED)

    def test_display_only_with_the_flag_on_and_never_a_set(self) -> None:
        hidden = pf.FieldState(("woman",), "Own words", False)
        shown = pf.FieldState(("woman",), "Own words", True)
        looking = pf.FieldState(("casual",), None, True)
        self.assertEqual(pf.displayed({pf.GENDER: hidden}), {})
        self.assertEqual(
            pf.displayed({pf.GENDER: shown}),
            {pf.GENDER: {"value_ids": ["woman"], "own_words": "Own words"}},
        )
        self.assertEqual(
            pf.displayed({pf.LOOKING_FOR: looking}), {pf.LOOKING_FOR: {"value_ids": ["casual"]}}
        )
        unset = pf.FieldState(("not-stated",), None, True)
        self.assertEqual(pf.displayed({pf.ORIENTATION: unset}), {})

    def test_the_whitespace_set_is_the_contracts(self) -> None:
        schema = json.loads(
            (REPO_ROOT / "packages/contracts/production/gapp-api-v1.schema.json").read_text()
        )
        pattern = schema["$defs"]["Text80"]["pattern"]
        blank_only = re.compile("[" + pattern.removeprefix("[^"))
        matched = {
            chr(code)
            for code in range(0x110000)
            if not 0xD800 <= code <= 0xDFFF and blank_only.fullmatch(chr(code))
        }
        self.assertEqual(matched, set(pf.WHITESPACE))


if __name__ == "__main__":
    unittest.main()
