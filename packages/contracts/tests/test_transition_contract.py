"""Acceptance examples against P02 transition oracle, not HTTP/SQL enforcement."""

import sys
import unittest
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from transition_contract import Context, read_projection, transition  # noqa: E402

OWNER = Context("alice", "owner", "alice")
SYSTEM = Context(None, "system", None)
STAFF = Context(
    "staff",
    "moderator",
    None,
    scopes=frozenset({"moderator:case"}),
    scoped_object_ids=frozenset({"object-1"}),
    policies=frozenset({"A05"}),
)
PARTICIPANT = Context("alice", "participant", None, participant_ids=("alice", "bob"))


class FlowAcceptanceTests(unittest.TestCase):
    def check(self, flow, event, before, after, actor, outcome):
        self.assertEqual(transition(flow, event, before, after, actor), outcome)

    def test_f01_only_maintained_auth_may_verify(self):
        self.check("F01", "verified", "unverified", "active", OWNER, "forbidden")
        self.check(
            "F01",
            "verified",
            "unverified",
            "active",
            Context(None, "auth", None),
            "allowed",
        )
        self.check("F01", "logout", "valid", "revoked", OWNER, "allowed")
        self.check("F01", "recover", "revoked", "valid", OWNER, "forbidden")

    def test_revoked_expired_sessions_cannot_authorize_objects(self):
        for state in ("revoked", "expired"):
            owner = replace(OWNER, session_state=state)
            self.check("F04", "edit", "incomplete", "incomplete", owner, "forbidden")
            self.assertEqual(read_projection("F04", "OwnProfile", owner), "not_found")
            self.check(
                "F15",
                "triage",
                "submitted",
                "triaged",
                replace(STAFF, session_state=state),
                "forbidden",
            )

    def test_f02_consent_version_and_withdrawal(self):
        self.check("F02", "accept", "required", "accepted", OWNER, "policy_unresolved")
        self.check(
            "F02",
            "accept",
            "required",
            "accepted",
            replace(OWNER, policies=frozenset({"consent_current"})),
            "allowed",
        )
        self.check("F02", "withdraw", "accepted", "withdrawn", OWNER, "allowed")

    def test_f03_birth_replacement_invalidates_resolved_state(self):
        self.check("F03", "change", "resolved", "pending", OWNER, "allowed")
        self.check("F03", "resolve", "pending", "resolved", SYSTEM, "policy_unresolved")
        self.check("F03", "resolve", "pending", "resolved", OWNER, "forbidden")

    def test_f04_object_ownership_and_incomplete_profile(self):
        self.check(
            "F04",
            "edit",
            "incomplete",
            "incomplete",
            replace(OWNER, owner_id="bob"),
            "forbidden",
        )
        self.check(
            "F04",
            "complete",
            "incomplete",
            "visible",
            replace(OWNER, policies=frozenset({"A05"}), eligible=False),
            "forbidden",
        )
        self.check(
            "F04",
            "complete",
            "incomplete",
            "visible",
            replace(OWNER, policies=frozenset({"A05"}), eligible=True),
            "allowed",
        )

    def test_f05_quarantine_cannot_be_published_by_uploader(self):
        self.check("F05", "approve", "quarantined", "approved", OWNER, "state_conflict")
        self.check("F05", "approve", "review_pending", "approved", OWNER, "forbidden")
        self.check("F05", "approve", "review_pending", "approved", STAFF, "allowed")
        for state in ("quarantined", "review_pending"):
            self.check("F05", "remove", state, "removal_pending", OWNER, "allowed")
        self.check("F05", "purged", "removal_pending", "removed", OWNER, "forbidden")

    def test_f06_resume_is_not_automatic(self):
        self.check("F06", "pause", "visible", "paused", OWNER, "allowed")
        self.check(
            "F06",
            "resume",
            "paused",
            "visible",
            replace(OWNER, policies=frozenset({"A05"})),
            "forbidden",
        )

    def test_f07_empty_is_not_provider_ready_or_contact(self):
        self.check("F07", "no_results", "pending", "empty", SYSTEM, "allowed")
        self.check(
            "F07",
            "eligible_results",
            "pending",
            "ready",
            replace(SYSTEM, policies=frozenset({"A05"})),
            "forbidden",
        )
        self.check("F07", "match", "ready", "active", OWNER, "state_conflict")

    def test_f08_repeated_like_stale_version_and_resurfacing(self):
        allowed = replace(OWNER, eligible=True)
        self.check("F08", "like", "liked", "liked", allowed, "allowed")
        self.check(
            "F08",
            "like",
            "liked",
            "liked",
            replace(allowed, current_version=2),
            "stale_version",
        )
        self.check("F08", "like", "passed", "liked", allowed, "policy_unresolved")

    def test_f09_reciprocal_like_is_server_fact(self):
        self.check(
            "F09",
            "reciprocal",
            "none",
            "active",
            replace(OWNER, eligible=True, policies=frozenset({"reciprocal_likes"})),
            "forbidden",
        )
        self.check(
            "F09",
            "reciprocal",
            "none",
            "active",
            replace(SYSTEM, eligible=True, policies=frozenset({"reciprocal_likes"})),
            "allowed",
        )

    def test_f10_unmatch_membership_and_no_rematch(self):
        self.check("F10", "unmatch", "active", "unmatched", PARTICIPANT, "allowed")
        self.check(
            "F10",
            "unmatch",
            "active",
            "unmatched",
            replace(PARTICIPANT, actor_id="charlie"),
            "forbidden",
        )
        self.check("F10", "rematch", "unmatched", "active", PARTICIPANT, "state_conflict")

    def test_f11_matched_contact_and_current_eligibility_are_both_required(self):
        allowed = replace(
            PARTICIPANT, eligible=True, active_match=True, policies=frozenset({"A08"})
        )
        self.check("F11", "submit", "none", "pending", allowed, "allowed")
        self.check(
            "F11",
            "submit",
            "none",
            "pending",
            replace(allowed, active_match=False),
            "forbidden",
        )
        self.check(
            "F11",
            "submit",
            "none",
            "pending",
            replace(allowed, eligible=False),
            "forbidden",
        )
        self.check(
            "F11",
            "submit",
            "none",
            "pending",
            replace(allowed, policies=frozenset()),
            "policy_unresolved",
        )

    def test_f12_device_owner_and_session_revocation(self):
        self.check(
            "F12",
            "rotate",
            "active",
            "active",
            replace(OWNER, owner_id="bob"),
            "forbidden",
        )
        self.check("F12", "logout", "active", "revoked", SYSTEM, "allowed")

    def test_f13_unblock_does_not_restore_contact(self):
        self.check("F13", "block", "none", "active", OWNER, "allowed")
        self.check("F13", "unblock", "active", "removed", OWNER, "allowed")
        self.check("F13", "unblock", "active", "matched", OWNER, "state_conflict")

    def test_f14_report_remains_available_when_pair_ineligible(self):
        self.check(
            "F14",
            "submit",
            "none",
            "submitted",
            replace(OWNER, eligible=False),
            "allowed",
        )
        self.assertEqual(
            read_projection("F14", "ReportReceipt", replace(OWNER, owner_id="bob")),
            "not_found",
        )

    def test_f15_case_scope_role_separation_and_private_projection(self):
        self.check("F15", "triage", "submitted", "triaged", STAFF, "allowed")
        self.check(
            "F15",
            "triage",
            "submitted",
            "triaged",
            replace(STAFF, object_id="another-case"),
            "forbidden",
        )
        self.check(
            "F15",
            "triage",
            "submitted",
            "triaged",
            replace(STAFF, role="support"),
            "forbidden",
        )
        self.assertEqual(read_projection("F15", "StaffCaseProjection", OWNER), "not_found")
        self.assertEqual(read_projection("F15", "AppealProjection", OWNER), "allowed")

    def test_f16_support_cannot_use_moderation_privilege(self):
        support = Context(
            "staff",
            "support",
            None,
            scopes=frozenset({"support:case"}),
            scoped_object_ids=frozenset({"object-1"}),
            policies=frozenset({"A05"}),
        )
        self.check("F16", "work", "open", "in_progress", support, "allowed")
        self.assertEqual(read_projection("F15", "StaffCaseProjection", support), "not_found")
        self.assertEqual(
            read_projection("F16", "SupportProjection", replace(OWNER, owner_id="bob")),
            "not_found",
        )

    def test_f17_export_cannot_be_claimed_ready_when_partial(self):
        self.check("F17", "complete", "preparing", "ready", SYSTEM, "policy_unresolved")
        self.check("F17", "expire", "ready", "expired", SYSTEM, "allowed")
        self.assertEqual(
            read_projection("F17", "ExportProjection", replace(OWNER, owner_id="bob")),
            "not_found",
        )

    def test_f18_revocation_precedes_policy_dependent_purge(self):
        self.check("F18", "revoke", "requested", "access_revoked", SYSTEM, "allowed")
        self.check("F18", "complete", "purging", "completed", SYSTEM, "policy_unresolved")
        self.check("F18", "retry", "completed", "purging", SYSTEM, "state_conflict")
        self.check(
            "F18",
            "request",
            "none",
            "requested",
            Context(None, "public", None),
            "forbidden",
        )

    def test_f19_mobile_recovery_is_not_authorization(self):
        client = Context(None, "presentation", None)
        self.check("F19", "reload", "stale", "loading", client, "allowed")
        self.check("F08", "like", "none", "liked", client, "forbidden")

    def test_f20_no_entitlement_activation(self):
        for role in (OWNER, SYSTEM, STAFF):
            self.check("F20", "purchase", "disabled", "active", role, "state_conflict")


class CrossArtifactRegressionTests(unittest.TestCase):
    def test_same_installation_may_reregister_only_with_current_session(self):
        self.assertEqual(transition("F12", "register", "revoked", "active", OWNER), "allowed")
        self.assertEqual(
            transition(
                "F12", "register", "revoked", "active", replace(OWNER, session_state="revoked")
            ),
            "forbidden",
        )

    def test_owner_can_correct_unresolved_inputs_without_resolver_permission(self):
        for state in ("unsupported", "pending", "unavailable"):
            self.assertEqual(transition("F03", "correct", state, "pending", OWNER), "allowed")
            self.assertEqual(
                transition("F03", "correct", state, "resolved", OWNER), "state_conflict"
            )
            self.assertEqual(
                transition("F03", "correct", state, "pending", replace(OWNER, owner_id="bob")),
                "forbidden",
            )

    def test_clearing_bio_can_remove_visibility_without_granting_eligibility(self):
        self.assertEqual(transition("F04", "edit", "visible", "incomplete", OWNER), "allowed")

    def test_restrict_media_requires_case_and_asset_scope_and_selected_policy(self):
        for flow, before, after in (
            ("F15", "investigating", "investigating"),
            ("F05", "approved", "review_pending"),
        ):
            self.assertEqual(transition(flow, "restrict_media", before, after, STAFF), "allowed")
            self.assertEqual(
                transition(
                    flow, "restrict_media", before, after, replace(STAFF, policies=frozenset())
                ),
                "policy_unresolved",
            )
            self.assertEqual(
                transition(
                    flow,
                    "restrict_media",
                    before,
                    after,
                    replace(STAFF, object_id="another-object"),
                ),
                "forbidden",
            )

    def test_deletion_immediately_revokes_account_and_profile_before_purge(self):
        self.assertEqual(
            transition("F01", "deletion_requested", "active", "deletion_pending", SYSTEM), "allowed"
        )
        self.assertEqual(
            transition("F04", "deletion_requested", "visible", "removed", SYSTEM), "allowed"
        )
        self.assertEqual(
            transition("F01", "purge_completed", "deletion_pending", "deleted", SYSTEM),
            "policy_unresolved",
        )
