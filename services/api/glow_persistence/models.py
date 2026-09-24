"""App-owned P02 definitions, not a live ORM/repository implementation.

Only static_settings installs these models. No methods perform persistence.
Cross-row safety, authorization and state transitions belong in future atomic
repositories; field/check definitions alone do not enforce them. See data-model.md.
"""

import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q


def choices(*values):
    return [(value, value) for value in values]


def state_check(*values):
    return models.CheckConstraint(
        condition=Q(state__in=values), name="%(app_label)s_%(class)s_state"
    )


def nonself_check(left="actor", right="target"):
    return models.CheckConstraint(
        condition=~Q(**{left: F(right)}), name="%(app_label)s_%(class)s_no_self"
    )


class Record(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    version = models.PositiveBigIntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta:
        abstract = True
        constraints = [
            models.CheckConstraint(
                condition=Q(version__gte=1), name="%(app_label)s_%(class)s_version"
            )
        ]


class OutboxEvent(Record):
    """Minimal reference payload. Durable delivery is a P11 proof."""

    aggregate_id = models.UUIDField()
    aggregate_version = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    event_type = models.CharField(max_length=100)
    schema_version = models.CharField(max_length=32)
    dedup_key = models.CharField(max_length=160, unique=True)
    # Reference to app-owned event material, never private birth/chat/token bodies.
    payload_ref = models.UUIDField()
    state = models.CharField(
        max_length=16,
        choices=choices("pending", "leased", "delivered", "dead_letter"),
        default="pending",
    )
    attempts = models.PositiveSmallIntegerField(default=0)
    available_at = models.DateTimeField()
    lease_expires_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta(Record.Meta):
        indexes = [models.Index(fields=["state", "available_at"], name="outbox_delivery_queue")]
        constraints = Record.Meta.constraints + [
            state_check("pending", "leased", "delivered", "dead_letter"),
            models.CheckConstraint(condition=Q(aggregate_version__gte=1), name="outbox_revision"),
            models.CheckConstraint(
                condition=Q(state="delivered", delivered_at__isnull=False)
                | (~Q(state="delivered") & Q(delivered_at__isnull=True)),
                name="outbox_delivery_time",
            ),
            models.CheckConstraint(
                condition=Q(state="leased", lease_expires_at__isnull=False)
                | (~Q(state="leased") & Q(lease_expires_at__isnull=True)),
                name="outbox_lease_time",
            ),
        ]


class WebhookInbox(Record):
    provider = models.CharField(max_length=32)
    provider_event_id = models.CharField(max_length=255)
    payload_digest = models.CharField(max_length=64)
    payload_ref = models.UUIDField()
    state = models.CharField(
        max_length=16,
        choices=choices("received", "verified", "applied", "rejected"),
        default="received",
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    applied_at = models.DateTimeField(null=True, blank=True)

    class Meta(Record.Meta):
        indexes = [models.Index(fields=["state", "created_at"], name="inbox_processing_queue")]
        constraints = Record.Meta.constraints + [
            models.UniqueConstraint(fields=["provider", "provider_event_id"], name="inbox_event"),
            state_check("received", "verified", "applied", "rejected"),
            models.CheckConstraint(
                condition=~Q(state__in=["verified", "applied"]) | Q(verified_at__isnull=False),
                name="inbox_requires_verification",
            ),
            models.CheckConstraint(
                condition=Q(state="applied", applied_at__isnull=False)
                | (~Q(state="applied") & Q(applied_at__isnull=True)),
                name="inbox_application_time",
            ),
        ]


class AppAccount(Record):
    # Library-owned credentials/normalized email identities stay in Django/allauth.
    auth_user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    state = models.CharField(
        max_length=24,
        choices=choices("unverified", "active", "suspended", "deletion_pending", "deleted"),
        default="unverified",
    )
    eligibility_version = models.PositiveBigIntegerField(default=1)
    preferences_version = models.PositiveBigIntegerField(default=1)
    blocks_version = models.PositiveBigIntegerField(default=1)
    session_epoch = models.PositiveBigIntegerField(default=1)

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            state_check("unverified", "active", "suspended", "deletion_pending", "deleted"),
            models.CheckConstraint(
                condition=Q(eligibility_version__gte=1), name="account_elig_rev"
            ),
            models.CheckConstraint(
                condition=Q(preferences_version__gte=1), name="account_pref_rev"
            ),
            models.CheckConstraint(condition=Q(blocks_version__gte=1), name="account_blocks_rev"),
            models.CheckConstraint(condition=Q(session_epoch__gte=1), name="account_session_epoch"),
        ]


class PolicyRevision(Record):
    """Versioned policy publication pointer; no policy is activated by this schema."""

    name = models.CharField(max_length=100, unique=True)
    policy_version = models.CharField(max_length=100)
    artifact_ref = models.UUIDField()


class AccountSession(Record):
    account = models.ForeignKey(AppAccount, on_delete=models.CASCADE)
    # Non-secret ID furnished by the maintained auth adapter. NOT a bearer token.
    auth_session_ref = models.CharField(max_length=255, unique=True)
    epoch = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    state = models.CharField(
        max_length=16, choices=choices("valid", "revoked", "expired"), default="valid"
    )
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta(Record.Meta):
        indexes = [models.Index(fields=["account", "state"], name="account_session_state")]
        constraints = Record.Meta.constraints + [
            state_check("valid", "revoked", "expired"),
            models.CheckConstraint(condition=Q(epoch__gte=1), name="session_epoch_positive"),
            models.CheckConstraint(
                condition=Q(state="revoked", revoked_at__isnull=False)
                | (~Q(state="revoked") & Q(revoked_at__isnull=True)),
                name="session_revocation_time",
            ),
        ]


class ConsentDecision(Record):
    account = models.ForeignKey(AppAccount, on_delete=models.CASCADE)
    purpose = models.CharField(max_length=100)
    policy_version = models.CharField(max_length=100)
    state = models.CharField(max_length=16, choices=choices("accepted", "withdrawn"))
    decided_at = models.DateTimeField()

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            state_check("accepted", "withdrawn"),
            models.UniqueConstraint(
                fields=["account", "purpose", "version"], name="consent_decision_revision"
            ),
        ]
        indexes = [
            models.Index(fields=["account", "purpose", "decided_at"], name="consent_current_lookup")
        ]


class Profile(Record):
    account = models.OneToOneField(AppAccount, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=80)
    bio = models.TextField(blank=True, max_length=500)
    # Only the explicitly allowed coarse display label; never precise coordinates.
    location_label = models.CharField(max_length=120, blank=True)
    state = models.CharField(
        max_length=16,
        choices=choices("incomplete", "visible", "paused", "restricted", "removed"),
        default="incomplete",
    )

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            state_check("incomplete", "visible", "paused", "restricted", "removed")
        ]
        indexes = [models.Index(fields=["state", "id"], name="profile_visibility_cursor")]


class Preferences(Record):
    account = models.OneToOneField(AppAccount, on_delete=models.CASCADE)
    # Missing policy means no eligibility permission. Values interpreted only by
    # the selected versioned policy; database JSON alone is not validation.
    policy_version = models.CharField(max_length=100, null=True, blank=True)
    values = models.JSONField(default=dict)


class BirthInput(Record):
    account = models.ForeignKey(AppAccount, on_delete=models.CASCADE)
    birth_date = models.DateField()
    local_time = models.TimeField(null=True, blank=True)
    time_precision = models.CharField(
        max_length=16, choices=choices("known", "approximate", "unknown")
    )
    place_label = models.CharField(max_length=255)
    timezone_name = models.CharField(max_length=100, null=True, blank=True)
    timezone_provenance = models.CharField(max_length=255, null=True, blank=True)
    consent_version = models.CharField(max_length=100)
    state = models.CharField(
        max_length=16,
        choices=choices(
            "missing", "ambiguous", "pending", "resolved", "unavailable", "unsupported"
        ),
        default="pending",
    )

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            models.UniqueConstraint(fields=["account", "version"], name="birth_input_revision"),
            state_check(
                "missing", "ambiguous", "pending", "resolved", "unavailable", "unsupported"
            ),
            models.CheckConstraint(
                condition=Q(time_precision="unknown", local_time__isnull=True)
                | Q(time_precision__in=["known", "approximate"], local_time__isnull=False),
                name="birth_time_uncertainty",
            ),
            models.CheckConstraint(
                condition=Q(timezone_name__isnull=True, timezone_provenance__isnull=True)
                | Q(timezone_name__isnull=False, timezone_provenance__isnull=False),
                name="birth_timezone_provenance",
            ),
        ]


class EngineIdentity(Record):
    account = models.OneToOneField(AppAccount, on_delete=models.CASCADE)
    birth_input = models.ForeignKey(BirthInput, on_delete=models.PROTECT)
    engine_reference = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(
        max_length=16, choices=choices("pending", "resolved"), default="pending"
    )
    engine_version = models.CharField(max_length=100, null=True, blank=True)
    contract_version = models.CharField(max_length=100, null=True, blank=True)
    adapter_version = models.CharField(max_length=100)

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            state_check("pending", "resolved"),
            models.CheckConstraint(
                condition=Q(
                    state="resolved",
                    engine_reference__isnull=False,
                    engine_version__isnull=False,
                    contract_version__isnull=False,
                )
                | Q(
                    state="pending",
                    engine_reference__isnull=True,
                    engine_version__isnull=True,
                    contract_version__isnull=True,
                ),
                name="engine_mapping_provenance",
            ),
        ]
        # Engine references intentionally NOT unique: shared-chart rights are A01.


class MediaAsset(Record):
    account = models.ForeignKey(AppAccount, on_delete=models.CASCADE)
    provider = models.CharField(max_length=32)
    storage_ref = models.CharField(max_length=255, null=True, blank=True)
    approved_variant_ref = models.CharField(max_length=255, null=True, blank=True)
    position = models.PositiveSmallIntegerField()
    state = models.CharField(
        max_length=24,
        choices=choices(
            "upload_pending",
            "quarantined",
            "review_pending",
            "approved",
            "rejected",
            "removal_pending",
            "removed",
        ),
        default="upload_pending",
    )
    review_ref = models.UUIDField(null=True, blank=True)

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            state_check(
                "upload_pending",
                "quarantined",
                "review_pending",
                "approved",
                "rejected",
                "removal_pending",
                "removed",
            ),
            models.UniqueConstraint(fields=["provider", "storage_ref"], name="media_provider_ref"),
            models.UniqueConstraint(
                fields=["account", "position"],
                condition=~Q(state="removed"),
                name="media_current_order",
            ),
            models.CheckConstraint(
                condition=~Q(state="approved")
                | Q(approved_variant_ref__isnull=False, review_ref__isnull=False),
                name="media_approval_evidence",
            ),
        ]


class DirectionalInteraction(Record):
    actor = models.ForeignKey(AppAccount, on_delete=models.CASCADE, related_name="outgoing_actions")
    target = models.ForeignKey(
        AppAccount, on_delete=models.CASCADE, related_name="incoming_actions"
    )
    state = models.CharField(max_length=16, choices=choices("liked", "passed"))
    policy_version = models.CharField(max_length=100)

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            nonself_check(),
            state_check("liked", "passed"),
            models.UniqueConstraint(
                fields=["actor", "target"], name="directional_interaction_pair"
            ),
        ]


class Block(Record):
    actor = models.ForeignKey(AppAccount, on_delete=models.CASCADE, related_name="outgoing_blocks")
    target = models.ForeignKey(AppAccount, on_delete=models.CASCADE, related_name="incoming_blocks")
    state = models.CharField(max_length=16, choices=choices("active", "removed"), default="active")

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            nonself_check(),
            state_check("active", "removed"),
            models.UniqueConstraint(fields=["actor", "target"], name="directional_block_pair"),
        ]


class Match(Record):
    account_low = models.ForeignKey(
        AppAccount, on_delete=models.CASCADE, related_name="low_matches"
    )
    account_high = models.ForeignKey(
        AppAccount, on_delete=models.CASCADE, related_name="high_matches"
    )
    state = models.CharField(
        max_length=16, choices=choices("active", "unmatched", "restricted"), default="active"
    )
    contact_version = models.PositiveBigIntegerField(default=1)

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            state_check("active", "unmatched", "restricted"),
            models.CheckConstraint(
                condition=Q(account_low__lt=F("account_high")), name="match_order"
            ),
            models.UniqueConstraint(fields=["account_low", "account_high"], name="match_pair"),
            models.CheckConstraint(
                condition=Q(contact_version__gte=1), name="match_contact_revision"
            ),
        ]


class CompatibilitySnapshot(Record):
    viewer = models.ForeignKey(
        AppAccount, on_delete=models.CASCADE, related_name="viewed_snapshots"
    )
    candidate = models.ForeignKey(
        AppAccount, on_delete=models.CASCADE, related_name="candidate_snapshots"
    )
    viewer_birth_version = models.PositiveBigIntegerField()
    candidate_birth_version = models.PositiveBigIntegerField()
    viewer_mapping_version = models.PositiveBigIntegerField()
    candidate_mapping_version = models.PositiveBigIntegerField()
    viewer_eligibility_version = models.PositiveBigIntegerField()
    candidate_eligibility_version = models.PositiveBigIntegerField()
    viewer_preferences_version = models.PositiveBigIntegerField()
    candidate_preferences_version = models.PositiveBigIntegerField()
    viewer_blocks_version = models.PositiveBigIntegerField()
    candidate_blocks_version = models.PositiveBigIntegerField()
    viewer_engine_reference = models.CharField(max_length=255)
    candidate_engine_reference = models.CharField(max_length=255)
    policy_version = models.CharField(max_length=100)
    engine_version = models.CharField(max_length=100)
    contract_version = models.CharField(max_length=100)
    adapter_version = models.CharField(max_length=100)
    state = models.CharField(
        max_length=16, choices=choices("ready", "pending", "unavailable", "unsupported", "stale")
    )
    expires_at = models.DateTimeField()
    # No raw HDE payload/score/band cache is permitted until A01 cache rights exist.

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            nonself_check("viewer", "candidate"),
            state_check("ready", "pending", "unavailable", "unsupported", "stale"),
            models.UniqueConstraint(
                fields=[
                    "viewer",
                    "candidate",
                    "viewer_birth_version",
                    "candidate_birth_version",
                    "viewer_mapping_version",
                    "candidate_mapping_version",
                    "viewer_eligibility_version",
                    "candidate_eligibility_version",
                    "viewer_preferences_version",
                    "candidate_preferences_version",
                    "viewer_blocks_version",
                    "candidate_blocks_version",
                    "policy_version",
                    "engine_version",
                    "contract_version",
                    "adapter_version",
                ],
                name="snapshot_directional_revision",
            ),
            models.CheckConstraint(
                condition=Q(
                    viewer_birth_version__gte=1,
                    candidate_birth_version__gte=1,
                    viewer_mapping_version__gte=1,
                    candidate_mapping_version__gte=1,
                    viewer_eligibility_version__gte=1,
                    candidate_eligibility_version__gte=1,
                    viewer_preferences_version__gte=1,
                    candidate_preferences_version__gte=1,
                    viewer_blocks_version__gte=1,
                    candidate_blocks_version__gte=1,
                ),
                name="snapshot_positive_revisions",
            ),
        ]
        indexes = [models.Index(fields=["viewer", "expires_at"], name="snapshot_expiry_lookup")]


class RecommendationBatch(Record):
    account = models.ForeignKey(AppAccount, on_delete=models.CASCADE)
    eligibility_version = models.PositiveBigIntegerField()
    preferences_version = models.PositiveBigIntegerField()
    blocks_version = models.PositiveBigIntegerField()
    policy_version = models.CharField(max_length=100)
    limit = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    state = models.CharField(
        max_length=16, choices=choices("pending", "ready", "empty", "stale", "unavailable")
    )
    expires_at = models.DateTimeField()

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            state_check("pending", "ready", "empty", "stale", "unavailable"),
            models.CheckConstraint(condition=Q(limit__gte=1, limit__lte=100), name="batch_bound"),
            models.CheckConstraint(
                condition=Q(
                    eligibility_version__gte=1, preferences_version__gte=1, blocks_version__gte=1
                ),
                name="batch_elig_revision",
            ),
        ]
        indexes = [models.Index(fields=["account", "created_at", "id"], name="batch_owner_cursor")]


class RecommendationEntry(Record):
    batch = models.ForeignKey(RecommendationBatch, on_delete=models.CASCADE)
    candidate = models.ForeignKey(AppAccount, on_delete=models.CASCADE)
    position = models.PositiveSmallIntegerField(validators=[MaxValueValidator(99)])
    candidate_eligibility_version = models.PositiveBigIntegerField()
    candidate_preferences_version = models.PositiveBigIntegerField()
    candidate_blocks_version = models.PositiveBigIntegerField()
    snapshot = models.ForeignKey(
        CompatibilitySnapshot, null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            models.UniqueConstraint(fields=["batch", "candidate"], name="batch_distinct_candidate"),
            models.UniqueConstraint(fields=["batch", "position"], name="batch_position"),
            models.CheckConstraint(condition=Q(position__lte=99), name="entry_position_bound"),
            models.CheckConstraint(
                condition=Q(
                    candidate_eligibility_version__gte=1,
                    candidate_preferences_version__gte=1,
                    candidate_blocks_version__gte=1,
                ),
                name="entry_elig_revision",
            ),
        ]


class ChatBinding(Record):
    match = models.OneToOneField(Match, on_delete=models.CASCADE)
    provider = models.CharField(max_length=32)
    channel_ref = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(
        max_length=16, choices=choices("pending", "active", "revoked", "failed"), default="pending"
    )

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            state_check("pending", "active", "revoked", "failed"),
            models.UniqueConstraint(
                fields=["provider", "channel_ref"], name="chat_provider_channel"
            ),
            models.CheckConstraint(
                condition=~Q(state="active") | Q(channel_ref__isnull=False), name="chat_active_ref"
            ),
        ]


class MessageSubmission(Record):
    binding = models.ForeignKey(ChatBinding, on_delete=models.CASCADE)
    actor = models.ForeignKey(AppAccount, on_delete=models.CASCADE)
    contact_version = models.PositiveBigIntegerField()
    idempotency_key = models.CharField(max_length=128)
    request_digest = models.CharField(max_length=64)
    # Private delivery spool, removed after receipt/expiry per approved policy.
    # Provider owns retained conversation bodies; never put text in the outbox.
    text = models.TextField(max_length=4000, null=True, blank=True)
    provider_message_ref = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(
        max_length=16, choices=choices("pending", "accepted", "failed"), default="pending"
    )

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            state_check("pending", "accepted", "failed"),
            models.UniqueConstraint(fields=["actor", "idempotency_key"], name="message_dedup"),
            models.CheckConstraint(condition=Q(contact_version__gte=1), name="message_contact_rev"),
            models.CheckConstraint(
                condition=~Q(state="accepted") | Q(provider_message_ref__isnull=False),
                name="message_acceptance_ref",
            ),
            models.CheckConstraint(
                condition=~Q(state="pending") | Q(text__isnull=False), name="message_pending_text"
            ),
        ]


class DeviceRegistration(Record):
    account = models.ForeignKey(AppAccount, on_delete=models.CASCADE)
    installation_id = models.UUIDField(unique=True)
    platform = models.CharField(max_length=8, choices=choices("ios", "android"))
    # Secure processor/vault reference only, never a plaintext push token.
    token_secret_ref = models.CharField(max_length=255, unique=True)
    state = models.CharField(max_length=16, choices=choices("active", "revoked"), default="active")

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            state_check("active", "revoked"),
            models.CheckConstraint(
                condition=Q(platform__in=["ios", "android"]), name="device_platform"
            ),
        ]


class NotificationSettings(Record):
    account = models.OneToOneField(AppAccount, on_delete=models.CASCADE)
    push_enabled = models.BooleanField(default=False)
    match_updates = models.BooleanField(default=False)
    message_updates = models.BooleanField(default=False)


class SafetyReport(Record):
    reporter = models.ForeignKey(
        AppAccount, null=True, on_delete=models.SET_NULL, related_name="reports_made"
    )
    subject = models.ForeignKey(
        AppAccount, null=True, on_delete=models.SET_NULL, related_name="reports_received"
    )
    # Subject marker permits restricted safety retention after account erasure.
    subject_marker = models.UUIDField()
    reason_code = models.CharField(max_length=100)
    description = models.TextField(max_length=4000)
    evidence_refs = models.JSONField(default=list)
    state = models.CharField(
        max_length=16,
        choices=choices("submitted", "triaged", "investigating", "resolved"),
        default="submitted",
    )
    retention_policy_version = models.CharField(max_length=100, null=True, blank=True)
    retention_due_at = models.DateTimeField(null=True, blank=True)

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            state_check("submitted", "triaged", "investigating", "resolved")
        ]


class ModerationCase(Record):
    report = models.ForeignKey(SafetyReport, on_delete=models.PROTECT)
    assigned_staff_subject = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(
        max_length=16,
        choices=choices("submitted", "triaged", "investigating", "resolved"),
        default="submitted",
    )
    outcome_code = models.CharField(max_length=100, null=True, blank=True)

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            state_check("submitted", "triaged", "investigating", "resolved"),
            models.CheckConstraint(
                condition=~Q(state="resolved") | Q(outcome_code__isnull=False), name="case_outcome"
            ),
        ]
        indexes = [models.Index(fields=["state", "created_at"], name="moderation_queue")]


class Appeal(Record):
    case = models.ForeignKey(ModerationCase, on_delete=models.PROTECT)
    appellant = models.ForeignKey(AppAccount, null=True, on_delete=models.SET_NULL)
    description = models.TextField(max_length=4000)
    state = models.CharField(
        max_length=16, choices=choices("submitted", "reviewing", "resolved"), default="submitted"
    )
    outcome_code = models.CharField(max_length=100, null=True, blank=True)

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            state_check("submitted", "reviewing", "resolved"),
            models.CheckConstraint(
                condition=~Q(state="resolved") | Q(outcome_code__isnull=False),
                name="appeal_outcome",
            ),
        ]


class StaffAudit(Record):
    # External staff identity is separate from dating-user identity.
    staff_subject = models.CharField(max_length=255)
    scope = models.CharField(max_length=100)
    action = models.CharField(max_length=100)
    object_type = models.CharField(max_length=100)
    object_id = models.UUIDField()
    reason_code = models.CharField(max_length=100)
    request_id = models.UUIDField(unique=True)
    before_version = models.PositiveBigIntegerField(null=True, blank=True)
    after_version = models.PositiveBigIntegerField(null=True, blank=True)

    class Meta(Record.Meta):
        indexes = [
            models.Index(fields=["object_type", "object_id", "created_at"], name="audit_object")
        ]


class SupportRequest(Record):
    account = models.ForeignKey(AppAccount, null=True, blank=True, on_delete=models.SET_NULL)
    contact_secret_ref = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=100)
    subject = models.CharField(max_length=200)
    description = models.TextField(max_length=4000)
    state = models.CharField(
        max_length=16, choices=choices("open", "in_progress", "resolved"), default="open"
    )
    retention_policy_version = models.CharField(max_length=100, null=True, blank=True)
    retention_due_at = models.DateTimeField(null=True, blank=True)

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [state_check("open", "in_progress", "resolved")]


class ExportJob(Record):
    account = models.ForeignKey(AppAccount, on_delete=models.CASCADE)
    state = models.CharField(
        max_length=16,
        choices=choices("requested", "preparing", "ready", "expired", "failed"),
        default="requested",
    )
    artifact_secret_ref = models.CharField(max_length=255, null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            state_check("requested", "preparing", "ready", "expired", "failed"),
            models.CheckConstraint(
                condition=~Q(state="ready")
                | Q(artifact_secret_ref__isnull=False, expires_at__isnull=False),
                name="export_ready_artifact",
            ),
        ]


class DeletionJob(Record):
    account = models.OneToOneField(AppAccount, null=True, on_delete=models.SET_NULL)
    subject_id = models.UUIDField(unique=True)
    state = models.CharField(
        max_length=16,
        choices=choices("requested", "access_revoked", "purging", "blocked", "completed"),
        default="requested",
    )
    retention_policy_version = models.CharField(max_length=100, null=True, blank=True)
    deadline_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            state_check("requested", "access_revoked", "purging", "blocked", "completed"),
            models.CheckConstraint(
                condition=Q(state="completed", completed_at__isnull=False)
                | (~Q(state="completed") & Q(completed_at__isnull=True)),
                name="deletion_completion",
            ),
        ]


class ProviderLifecycleStep(Record):
    deletion = models.ForeignKey(DeletionJob, null=True, blank=True, on_delete=models.PROTECT)
    export = models.ForeignKey(ExportJob, null=True, blank=True, on_delete=models.CASCADE)
    provider = models.CharField(max_length=32)
    operation = models.CharField(max_length=100)
    resource_ref = models.CharField(max_length=255)
    idempotency_key = models.CharField(max_length=160, unique=True)
    state = models.CharField(
        max_length=16,
        choices=choices("pending", "running", "verified", "blocked", "failed"),
        default="pending",
    )
    attempts = models.PositiveSmallIntegerField(default=0)
    next_attempt_at = models.DateTimeField(null=True, blank=True)
    verification_ref = models.CharField(max_length=255, null=True, blank=True)

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            state_check("pending", "running", "verified", "blocked", "failed"),
            models.CheckConstraint(
                condition=Q(deletion__isnull=False, export__isnull=True)
                | Q(deletion__isnull=True, export__isnull=False),
                name="provider_step_one_job",
            ),
            models.CheckConstraint(
                condition=~Q(state="verified") | Q(verification_ref__isnull=False),
                name="provider_step_evidence",
            ),
        ]
        indexes = [models.Index(fields=["state", "next_attempt_at"], name="lifecycle_retry_queue")]


class DeletionTombstone(Record):
    # No account FK: restoration must not resurrect a deleted subject.
    subject_id = models.UUIDField(unique=True)
    deletion = models.OneToOneField(DeletionJob, on_delete=models.PROTECT)
    revoked_at = models.DateTimeField()
    policy_version = models.CharField(max_length=100, null=True, blank=True)
    replay_before = models.DateTimeField(null=True, blank=True)


class IdempotencyRecord(Record):
    # No account FK so a queued retry cannot recreate an erased subject.
    actor_id = models.UUIDField()
    operation = models.CharField(max_length=100)
    key = models.CharField(max_length=128)
    # Canonical intent digest includes target; actor/operation/key alone is unique.
    request_digest = models.CharField(max_length=64)
    # Immutable commit receipt, never a cached private/current projection.
    result_ref = models.UUIDField(null=True, blank=True)
    result_version = models.PositiveBigIntegerField(null=True, blank=True)
    outcome_code = models.CharField(
        max_length=16,
        null=True,
        blank=True,
        choices=choices("committed", "liked", "passed", "unmatched", "blocked", "unblocked"),
    )
    state = models.CharField(
        max_length=16, choices=choices("pending", "completed"), default="pending"
    )
    expires_at = models.DateTimeField()

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            state_check("pending", "completed"),
            models.UniqueConstraint(fields=["actor_id", "operation", "key"], name="intent_dedup"),
            models.CheckConstraint(
                condition=Q(
                    state="completed",
                    result_ref__isnull=False,
                    result_version__gte=1,
                    result_version__isnull=False,
                    result_version__lte=9007199254740991,
                    outcome_code__in=(
                        "committed",
                        "liked",
                        "passed",
                        "unmatched",
                        "blocked",
                        "unblocked",
                    ),
                    outcome_code__isnull=False,
                )
                | Q(
                    state="pending",
                    result_ref__isnull=True,
                    result_version__isnull=True,
                    outcome_code__isnull=True,
                ),
                name="intent_result",
            ),
        ]


class Entitlement(Record):
    account = models.ForeignKey(AppAccount, on_delete=models.CASCADE)
    product_ref = models.CharField(max_length=128)
    # P02 cannot represent an activated paid product. Expand after A06 decision.
    state = models.CharField(max_length=16, choices=choices("disabled"), default="disabled")

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            state_check("disabled"),
            models.UniqueConstraint(fields=["account", "product_ref"], name="entitlement_product"),
        ]
