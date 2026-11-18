"""SV2-R (its brief's R1 and R3; OD-68): the identity requirement set aside, the parts that need no
database.

- ``requirements.missing`` reads no identity verification, with its signature unchanged (DM-93
  ZZ2), and reports nothing when every other requirement is met;
- the completion read's closed list keeps ``identity_verification``, the contract's value, so ID
  validation can return without a contract change;
- D18's record, port, staff approval and setting stay;
- the module's docstring says the requirement is set aside, and how a photo reaches ``approved``
  in each state of the photo check's toggle (R3).

The Django-dependent check runs in a fresh process under ``tests.profiles_offline_settings`` (the
dummy database backend), as ``test_profiles_offline.py``'s do. The profile suite's ``sv2r.`` cases
show completion without identity verification on the disposable PostgreSQL (acceptance checks 1
and 2).
"""

import ast
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


if __name__ == "__main__":
    unittest.main()
