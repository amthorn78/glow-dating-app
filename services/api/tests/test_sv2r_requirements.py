"""SV2-R (its brief's R1 and R3; OD-68): the identity requirement set aside, the parts that need no
database.

- ``requirements.missing`` reads no identity verification, with its signature unchanged (DM-93
  ZZ2), and reports nothing when every other requirement is met;
- the completion read's closed list keeps ``identity_verification``, the contract's value, so ID
  validation can return without a contract change;
- D18's record, port, staff approval and setting stay;
- the module's docstring says the requirement is set aside, and how a photo reaches ``approved``
  in each state of the photo check's toggle (R3);
- correction C1 (the exact-head review's R1 and R2): the recheck's refusal ``not_awaiting_recheck``
  holds for any photo that is not ``approved``, and ``run_check``'s refusal ``not_in_review`` for
  any photo that is not ``review_pending``, each before any port call or write.

The Django-dependent check runs in a fresh process under ``tests.profiles_offline_settings`` (the
dummy database backend), as ``test_profiles_offline.py``'s do. The profile suite's ``sv2r.`` cases
show completion without identity verification on the disposable PostgreSQL (acceptance checks 1
and 2), and drive both refusals there (``sv2r.the_recheck``, ``sv2r.toggle_off_approves...`` and
``sv2r.toggle_on_the_check_decides_as_before``).
"""

import ast
import re
import unittest

from glow_domain import profile_settings as ps
from tests.test_profile_contract import runtime
from tests.test_profiles_offline import API_ROOT, last_json, modules, under_profile_settings


def _function(name: str) -> ast.FunctionDef:
    return next(
        node
        for node in modules()["requirements.py"].body
        if isinstance(node, ast.FunctionDef) and node.name == name
    )


# Every other requirement's read replaced by a met one; no identity verification is seeded, and
# none can be read (the dummy backend refuses any query), so ``missing`` must not read one.
MET = """
import json
from types import SimpleNamespace
from unittest import mock
from uuid import uuid4
from glow_profiles import requirements

profile = SimpleNamespace(display_name="Synthetic", bio="Synthetic.", area_id=uuid4())
age = SimpleNamespace(state="self_declared_adult")
found = {}
with (
    mock.patch.object(requirements, "onboarding_current", return_value=True),
    mock.patch.object(requirements, "chart_resolved", return_value=True),
    mock.patch.object(requirements, "_field_values", return_value=["fixture-value"]),
    mock.patch.object(requirements, "AccountAgeState") as age_state,
    mock.patch.object(requirements, "MediaAsset") as asset,
):
    age_state.objects.filter.return_value.first.return_value = age
    asset.objects.filter.return_value.exists.return_value = True
    found["met"] = requirements.missing(uuid4(), profile, "consent.onboarding.v1")
    asset.objects.filter.return_value.exists.return_value = False
    found["no_photo"] = requirements.missing(uuid4(), profile, "consent.onboarding.v1")
found["all"] = list(requirements.ALL)
print(json.dumps(found))
"""


class IdentitySetAsideTests(unittest.TestCase):
    def test_missing_reads_no_identity_verification(self) -> None:
        source = ast.unparse(_function("missing"))
        for name in ("IdentityVerification", "IDENTITY_VERIFICATION", "verified", "staff_approved"):
            with self.subTest(name=name):
                self.assertNotIn(name, source)
        imported = {
            alias.name
            for node in ast.walk(modules()["requirements.py"])
            if isinstance(node, ast.ImportFrom)
            for alias in node.names
        }
        self.assertNotIn("IdentityVerification", imported)

    def test_missing_keeps_its_signature(self) -> None:
        # DM-93 ZZ2: operations.py, recompute.py and the discovery suite call it unchanged.
        arguments = _function("missing").args
        self.assertEqual(
            [argument.arg for argument in arguments.args],
            ["account_id", "profile", "onboarding_policy_version"],
        )
        self.assertEqual(
            (arguments.kwonlyargs, arguments.vararg, arguments.kwarg), ([], None, None)
        )

    def test_with_every_other_requirement_met_nothing_is_missing(self) -> None:
        found = last_json(under_profile_settings(MET))
        self.assertEqual(found["met"], [])
        # The photo requirement stands (R3): with no approved photo, it is what is missing.
        self.assertEqual(found["no_photo"], ["photo"])
        # The closed list keeps the contract's value (the next test).
        self.assertIn("identity_verification", found["all"])

    def test_the_closed_list_keeps_the_contracts_value(self) -> None:
        schema = runtime().SCHEMAS["production"]["$defs"]["OwnCompletion"]
        declared = next(
            node.value
            for node in modules()["requirements.py"].body
            if isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "ALL"
        )
        assert isinstance(declared, ast.Tuple)
        names = {
            node.targets[0].id: node.value.value
            for node in modules()["requirements.py"].body
            if isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Name)
            and isinstance(node.value, ast.Constant)
        }
        listed = [names[element.id] for element in declared.elts if isinstance(element, ast.Name)]
        self.assertEqual(listed, schema["properties"]["missing"]["items"]["enum"])
        self.assertIn("identity_verification", listed)

    def test_d18_stays(self) -> None:
        # The record, its port, staff's approval and revocation and their setting are unchanged.
        self.assertTrue((API_ROOT / "glow_domain" / "identity_verification.py").is_file())
        self.assertTrue((API_ROOT / "glow_profiles" / "identity_verification.py").is_file())
        staff = {
            node.name for node in modules()["staff.py"].body if isinstance(node, ast.FunctionDef)
        }
        self.assertLessEqual({"approve_without_id", "revoke_approval"}, staff)
        self.assertEqual(
            ps.LAUNCH_DEFAULTS[ps.STAFF_APPROVAL],
            {"enabled": False, "stands_in_for": ["identity_verification"]},
        )

    def test_the_docstring_says_so(self) -> None:
        text = " ".join((ast.get_docstring(modules()["requirements.py"]) or "").split())
        self.assertIn("Identity verification is set aside", text)
        self.assertIn("OD-68", text)
        # R3: how a photo reaches approved, in each state of the toggle.
        self.assertIn("while it is off", text)
        self.assertIn("while it is on, the automated check approves it", text)
        self.assertIn("media.photo_check", text)


def _step_body(step: str) -> ast.FunctionDef:
    """The transaction body of one step of ``media.py``."""
    function = next(
        node
        for node in modules()["media.py"].body
        if isinstance(node, ast.FunctionDef) and node.name == step
    )
    return next(
        node for node in function.body if isinstance(node, ast.FunctionDef) and node.name == "body"
    )


# What a step's statements before a refusal must not hold: a port call, or any write the step can
# make (an audit row, a transition, the recompute, a save, a creation, an update, an event).
PORT_OR_WRITE = (
    "adapters.",
    "_decision_audit(",
    "transition(",
    "recompute.",
    ".save(",
    ".create(",
    ".update(",
    "bulk_create",
    "events.emit(",
    "delivery_reference(",
)


def _state_tests(step: str) -> list[str]:
    """Every comparison in the step's body that tests the photo's state (``asset.state``)."""
    return [
        ast.unparse(node)
        for node in ast.walk(_step_body(step))
        if isinstance(node, ast.Compare)
        and any(ast.unparse(part) == "asset.state" for part in (node.left, *node.comparators))
    ]


class StateRefusalTests(unittest.TestCase):
    """Correction C1 (the exact-head review's R1 and R2). SV2-R's two transitions out of
    ``approved`` mean F05's registry no longer refuses ``approve`` or ``reject`` from
    ``approved``, so each step's refusal on the photo's state is what keeps it to its own photos.
    The profile suite's ``sv2r.`` cases drive both refusals on PostgreSQL."""

    def refusal(self, step: str, reason: str) -> tuple[int, ast.If]:
        """The one ``if`` of the step's body whose one statement returns ``no_change`` with
        ``reason``, and its index."""
        body = _step_body(step)
        found = [
            (index, statement)
            for index, statement in enumerate(body.body)
            if isinstance(statement, ast.If)
            and [ast.unparse(s) for s in statement.body]
            == [f"return Result('no_change', reason={reason!r})"]
        ]
        self.assertEqual(len(found), 1, (step, reason))
        index, statement = found[0]
        self.assertEqual(statement.orelse, [])
        return index, statement

    def nothing_before(self, step: str, index: int) -> None:
        earlier = "\n".join(ast.unparse(s) for s in _step_body(step).body[:index])
        for call in PORT_OR_WRITE:
            with self.subTest(step=step, call=call):
                self.assertNotIn(call, earlier)

    def test_the_recheck_refuses_a_photo_that_is_not_approved(self) -> None:
        # R1: the refusal holds unless the photo is approved, whatever its review reference: a
        # photo approved while the toggle was off and then restricted by staff keeps that
        # reference in ``review_pending``, and F05 allows ``reject`` and ``approve`` from there.
        index, refusal = self.refusal("recheck", "not_awaiting_recheck")
        test = refusal.test
        self.assertIsInstance(test, ast.BoolOp)
        assert isinstance(test, ast.BoolOp)
        self.assertIsInstance(test.op, ast.Or)
        self.assertEqual(
            [ast.unparse(value) for value in test.values],
            [
                "asset.state != md.APPROVED",
                "not _approvals_while_off().filter(pk=asset.review_ref).exists()",
            ],
        )
        # It comes before the check port, the hold port, every write and the recompute.
        self.nothing_before("recheck", index)
        statements = _step_body("recheck").body
        later = "\n".join(ast.unparse(s) for s in statements[index + 1 :])
        self.assertIn("adapters.check.decide(", later)
        # It is the step's only test of the photo's state.
        self.assertEqual(_state_tests("recheck"), ["asset.state != md.APPROVED"])

    def test_run_check_refuses_a_photo_that_is_not_in_review(self) -> None:
        # R2: the refusal admits only ``review_pending``, before the restriction check and the
        # toggle's branch, so neither the check nor the off branch acts on an approved photo.
        index, refusal = self.refusal("run_check", "not_in_review")
        self.assertEqual(ast.unparse(refusal.test), "asset.state != md.REVIEW_PENDING")
        self.nothing_before("run_check", index)
        statements = _step_body("run_check").body
        restriction, _ = self.refusal("run_check", "restricted")
        branch = next(
            position
            for position, statement in enumerate(statements)
            if isinstance(statement, ast.If) and ast.unparse(statement.test) == "checking"
        )
        self.assertLess(index, restriction)
        self.assertLess(index, branch)
        # It is the step's only test of the photo's state, and no other state is named.
        self.assertEqual(_state_tests("run_check"), ["asset.state != md.REVIEW_PENDING"])
        self.assertIsNone(re.search(r"\bmd\.APPROVED\b", ast.unparse(_step_body("run_check"))))


if __name__ == "__main__":
    unittest.main()
