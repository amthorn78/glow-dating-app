"""Models used by the sealed slices; the served runtime installs none."""

import uuid

from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from glow_persistence.fields import SequenceField


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
    # P06.2 B1 (DM-15 3.1): the delivery order within one available_at. Assigned by the
    # database in insertion order, so the events one transaction writes are delivered
    # in the order it wrote them; neither the app's clock nor the random id decides.
    sequence = SequenceField()

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
    """Versioned policy publication pointer; no policy is activated by this schema.

    SV2 (its brief's D2): the current pointer of each setting, locked alongside the actions
    that read it. ``policy_version`` is the current version's label (``<name>.v<number>``) and
    ``artifact_ref`` the ``SettingVersion`` row it names."""

    name = models.CharField(max_length=100, unique=True)
    policy_version = models.CharField(max_length=100)
    artifact_ref = models.UUIDField()


class SettingVersion(Record):
    """One published version of a setting (SV2, migration 0005; its brief's D2; OD-60).

    Append-only: a publication adds the next ``number`` and moves its ``PolicyRevision``
    pointer, and no row is changed after it is written. ``content`` is validated against the
    setting's closed schema and the fixed limits in code (``glow_domain.profile_settings``)
    before it is written; the launch defaults are version 1, seeded by migration 0007 with the
    staff subject ``system:launch-default``."""

    name = models.CharField(max_length=100)
    number = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    content = models.JSONField()
    published_at = models.DateTimeField()
    staff_subject = models.CharField(max_length=255)
    reason = models.CharField(max_length=100)

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            models.UniqueConstraint(fields=["name", "number"], name="setting_version_number"),
            models.CheckConstraint(condition=Q(number__gte=1), name="setting_version_positive"),
        ]


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


class AccountAgeState(Record):
    """The account's recorded age state and the method that set it (SV1, migration 0004;
    G-01; OD-55's D3 (a); the SV1 brief's D9).

    One row per account, written only through ``glow_domain.identity.AgeAssurancePort``
    (its adapter is ``glow_identity.age``). Sign-up records ``unknown``. SV2 (its brief's D7,
    migration 0005) adds the self-entered birth date, the date's one home: present with
    ``self_declared_adult`` and absent with ``unknown``, and written only by the port's
    transition. SV3 reads a member's age from it in whole years, never the date; P09.2 adds the
    stores' age signals as further states and methods.
    """

    account = models.OneToOneField(AppAccount, on_delete=models.CASCADE)
    state = models.CharField(max_length=32, choices=choices("unknown", "self_declared_adult"))
    method = models.CharField(max_length=32, choices=choices("none", "self_declaration"))
    recorded_at = models.DateTimeField()
    policy_version = models.CharField(max_length=100, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            state_check("unknown", "self_declared_adult"),
            models.CheckConstraint(
                condition=Q(method__in=["none", "self_declaration"]), name="age_state_method"
            ),
            # Each state names the methods that may set it; unknown has no policy version.
            models.CheckConstraint(
                condition=Q(state="unknown", method="none", policy_version__isnull=True)
                | Q(
                    state="self_declared_adult",
                    method="self_declaration",
                    policy_version__isnull=False,
                ),
                name="age_state_provenance",
            ),
            # SV2 (D7): the date is present with self_declared_adult and absent with unknown.
            models.CheckConstraint(
                condition=Q(state="unknown", birth_date__isnull=True)
                | Q(state="self_declared_adult", birth_date__isnull=False),
                name="age_state_birth_date",
            ),
        ]


class ConsentDecision(Record):
    account = models.ForeignKey(AppAccount, on_delete=models.CASCADE)
    # SV2 (D6): ``onboarding`` (F02's ConsentIntent, glow_chat's writer) or
    # ``sensitive_profile`` (the sensitive-fields consent, glow_profiles' writer). Every reader
    # filters by purpose.
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
            models.CheckConstraint(
                condition=Q(purpose__in=["onboarding", "sensitive_profile"]),
                name="consent_purpose",
            ),
        ]
        indexes = [
            models.Index(fields=["account", "purpose", "decided_at"], name="consent_current_lookup")
        ]


class Area(Record):
    """A core-based statistical area, the member's home area (SV2, migrations 0005 and 0006;
    its brief's D5). Reference data from the Census Bureau's 2024 Gazetteer, loaded by a data
    migration from the committed table (``glow_profiles/data/cbsa_areas_2024.tsv``) after its
    pinned hash is checked; never fetched. ``area_id`` is the stable GEOID; the internal point
    is the published one, which every member in the area shares."""

    area_id = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=80)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            models.CheckConstraint(
                condition=Q(latitude__gte=-90, latitude__lte=90)
                & Q(longitude__gte=-180, longitude__lte=180),
                name="area_internal_point",
            ),
        ]


class Profile(Record):
    account = models.OneToOneField(AppAccount, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=80)
    bio = models.TextField(blank=True, max_length=500)
    # SV2 (D5): the member's home area replaces the text label; the coordinates the phone sends
    # are never stored. Its display text is the area's name.
    area = models.ForeignKey(
        Area, null=True, blank=True, on_delete=models.PROTECT, related_name="profiles"
    )
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
    # SV2 (D3): the policy of the "show me" sets, which are rows (PreferenceSetEntry), not
    # ``values``; it is the catalog version they were last written under.
    policy_version = models.CharField(max_length=100, null=True, blank=True)
    values = models.JSONField(default=dict)
    # SV2 (D4, D5): the member's age range (never below 18) and distance choice (one of the
    # location setting's choices, measured between area internal points by SV3).
    minimum_age = models.PositiveSmallIntegerField(null=True, blank=True)
    maximum_age = models.PositiveSmallIntegerField(null=True, blank=True)
    distance_choice = models.CharField(max_length=100, null=True, blank=True)

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            models.CheckConstraint(
                condition=Q(minimum_age__isnull=True) | Q(minimum_age__gte=18),
                name="preferences_age_floor",
            ),
            models.CheckConstraint(
                condition=Q(maximum_age__isnull=True)
                | Q(minimum_age__isnull=False, maximum_age__gte=F("minimum_age")),
                name="preferences_age_range",
            ),
        ]


PROFILE_FIELDS = ("gender", "orientation", "looking_for", "relationship_status")


class ProfileFieldChoice(Record):
    """A member's own value in one of the four two-way list fields (SV2, migration 0005; its
    brief's D3; OD-60, P1): one row per account and field, holding the selected value IDs and
    the setting version they were chosen under. Orientation and relationship status may hold
    the reserved ``not-stated``; a row they do not have reads as ``not-stated`` too. The own
    words (gender and orientation only, display only) and the display flag are the field's.
    SV3 queries ``value_ids`` through the GIN index."""

    account = models.ForeignKey(AppAccount, on_delete=models.CASCADE)
    field = models.CharField(max_length=32, choices=choices(*PROFILE_FIELDS))
    value_ids = models.JSONField()
    setting_version = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    own_words = models.CharField(max_length=40, null=True, blank=True)
    shown = models.BooleanField(default=False)

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            models.UniqueConstraint(fields=["account", "field"], name="profile_field_choice"),
            models.CheckConstraint(
                condition=Q(field__in=PROFILE_FIELDS), name="profile_field_name"
            ),
            models.CheckConstraint(
                condition=Q(own_words__isnull=True) | Q(field__in=["gender", "orientation"]),
                name="profile_field_own_words",
            ),
            models.CheckConstraint(
                condition=~Q(field="looking_for") | Q(shown=True), name="profile_field_shown"
            ),
            models.CheckConstraint(
                condition=Q(setting_version__gte=1), name="profile_field_setting_version"
            ),
        ]
        indexes = [GinIndex(fields=["value_ids"], name="profile_field_values")]


class PreferenceSetEntry(Record):
    """One value of a member's "show me" set for one field (SV2, migration 0005; its brief's
    D3): rows, so SV3 can test both directions for every candidate in one query. The set that
    keeps all is the one row whose ``value_id`` is the reserved ``all``, never the list of
    current values; a narrowed set holds list values only, never ``not-stated``."""

    account = models.ForeignKey(AppAccount, on_delete=models.CASCADE)
    field = models.CharField(max_length=32, choices=choices(*PROFILE_FIELDS))
    value_id = models.CharField(max_length=100)
    # The value's place in the set as the member submitted it (0 for the marker).
    position = models.PositiveSmallIntegerField(default=0)

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            models.UniqueConstraint(
                fields=["account", "field", "value_id"], name="preference_set_value"
            ),
            models.CheckConstraint(
                condition=Q(field__in=PROFILE_FIELDS), name="preference_set_field"
            ),
            models.CheckConstraint(
                condition=~Q(value_id="not-stated"), name="preference_set_not_stated"
            ),
        ]
        indexes = [
            models.Index(fields=["field", "value_id", "account"], name="preference_set_lookup")
        ]


class IdentityVerification(Record):
    """The account's identity verification state (SV2, migration 0005; its brief's D18;
    OD-61): ``unverified``, ``verified`` by the automated check (a government photo ID with a
    selfie matched to it, by a verification company), or ``staff_approved`` without it while
    the setting allows. It holds the method, the company's opaque reference or the staff
    subject and reason, and the time; never an ID image, ID number or selfie. Written only
    through the identity verification port, after the account row lock. It is not the
    contract's ``verify_identity``, which means email verification. A row it does not have
    reads as ``unverified``."""

    account = models.OneToOneField(AppAccount, on_delete=models.CASCADE)
    state = models.CharField(
        max_length=24,
        choices=choices("unverified", "verified", "staff_approved"),
        default="unverified",
    )
    method = models.CharField(
        max_length=24, choices=choices("none", "automated_check", "staff_approval"), default="none"
    )
    provider_reference = models.CharField(max_length=255, null=True, blank=True)
    staff_subject = models.CharField(max_length=255, null=True, blank=True)
    reason = models.CharField(max_length=100, null=True, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            state_check("unverified", "verified", "staff_approved"),
            models.CheckConstraint(
                condition=Q(
                    state="unverified",
                    method="none",
                    provider_reference__isnull=True,
                    staff_subject__isnull=True,
                    reason__isnull=True,
                )
                | Q(
                    state="verified",
                    method="automated_check",
                    provider_reference__isnull=False,
                    staff_subject__isnull=True,
                    reason__isnull=True,
                    decided_at__isnull=False,
                )
                | Q(
                    state="staff_approved",
                    method="staff_approval",
                    provider_reference__isnull=True,
                    staff_subject__isnull=False,
                    reason__isnull=False,
                    decided_at__isnull=False,
                ),
                name="identity_verification_provenance",
            ),
        ]


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
    """One photo (F05; SV2 Stage B, migration 0008; its brief's D10; OD-62).

    ``storage_ref`` is the original's object key, Glow's own, random and opaque (``MediaObject``);
    ``approved_variant_ref`` is the delivery reference the storage port gives an approved
    variant, present only while ``approved``. The owner's removal (``removal_requested_at``) and a
    staff restriction on a report (``restriction_ref``, the restriction's ``StaffAudit`` row) are
    separate revocation records: an approval needs neither, and the automated check clears
    neither. ``detection`` records G-02's seam (``no_detector`` in SV2) and
    ``rejection_reason`` the check's reason code."""

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
    detection = models.CharField(
        max_length=24, choices=choices("no_detector"), null=True, blank=True
    )
    rejection_reason = models.CharField(max_length=64, null=True, blank=True)
    restriction_ref = models.UUIDField(null=True, blank=True)
    removal_requested_at = models.DateTimeField(null=True, blank=True)
    purge_requested_at = models.DateTimeField(null=True, blank=True)

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
            # SV2 Stage B (D10): a delivery reference exists only while approved, and never
            # through a revocation record of either kind.
            models.CheckConstraint(
                condition=Q(state="approved") | Q(approved_variant_ref__isnull=True),
                name="media_delivery_only_approved",
            ),
            models.CheckConstraint(
                condition=~Q(state="approved")
                | Q(restriction_ref__isnull=True, removal_requested_at__isnull=True),
                name="media_approved_unrevoked",
            ),
            models.CheckConstraint(
                condition=~Q(state__in=["removal_pending", "removed"])
                | Q(removal_requested_at__isnull=False),
                name="media_removal_record",
            ),
            models.CheckConstraint(
                condition=~Q(state__in=["review_pending", "approved", "rejected"])
                | Q(detection__isnull=False),
                name="media_seam_passed",
            ),
        ]


class MediaObject(Record):
    """One object of a photo in private storage (SV2 Stage B, migration 0008; D10; OD-62): the
    original, at the key its grant names, and each variant processing writes. A key is Glow's own,
    32 random hexadecimal characters: no account, profile or asset ID, filename or member value.
    The original's size and entity tag are the adopted completion's. ``deleted_at`` is the storage
    adapter's acknowledgment that the object is deleted; an asset is ``removed`` only when every
    one of its objects has it."""

    asset = models.ForeignKey(MediaAsset, on_delete=models.CASCADE, related_name="objects_held")
    role = models.CharField(max_length=16, choices=choices("original", "variant"))
    key = models.CharField(max_length=64, unique=True)
    byte_size = models.PositiveIntegerField(null=True, blank=True)
    entity_tag = models.CharField(max_length=128, null=True, blank=True)
    adopted_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            models.CheckConstraint(
                condition=Q(role__in=["original", "variant"]), name="media_object_role"
            ),
            models.CheckConstraint(
                condition=Q(key__regex=r"^[0-9a-f]{32}$"), name="media_object_opaque_key"
            ),
            models.CheckConstraint(
                condition=Q(adopted_at__isnull=True)
                | Q(byte_size__isnull=False, entity_tag__isnull=False),
                name="media_object_adoption_evidence",
            ),
            models.UniqueConstraint(
                fields=["asset"], condition=Q(role="original"), name="media_one_original"
            ),
        ]


class MediaUploadGrant(Record):
    """An upload grant (SV2 Stage B, migration 0008; D10; DM-57 U3): one per asset, one-use and
    short-lived by Glow's own record, within the media policy version it was issued under
    (``policy_version``), whose byte limit its completion is checked against. ``grant_ref`` is the
    opaque reference ``MediaUploadGrant`` returns; ``object_key`` is the original's key, which the
    store's upload credential (P11's) is scoped to and no member is given. ``used_at`` is the
    adoption of its first matching completion; nothing after it changes the asset."""

    account = models.ForeignKey(AppAccount, on_delete=models.CASCADE)
    asset = models.OneToOneField(MediaAsset, on_delete=models.CASCADE, related_name="grant")
    grant_ref = models.CharField(max_length=100, unique=True)
    object_key = models.CharField(max_length=64, unique=True)
    policy_version = models.CharField(max_length=100)
    issued_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            models.CheckConstraint(
                condition=Q(expires_at__gt=F("issued_at")), name="media_grant_expiry"
            ),
            models.CheckConstraint(
                condition=Q(used_at__isnull=True) | Q(used_at__lte=F("expires_at")),
                name="media_grant_used_in_time",
            ),
            models.CheckConstraint(
                condition=Q(object_key__regex=r"^[0-9a-f]{32}$"), name="media_grant_opaque_key"
            ),
        ]


class DirectionalInteraction(Record):
    """One actor's like or pass toward one target (SV3 Stage B, migration 0011; its brief's D9 and
    D12). ``withdrawn`` is a pass the actor undid: the row is kept and its version advanced, never
    deleted and created again, and it excludes nothing. ``decided_at`` is the transaction's
    ``clock_timestamp()`` at the row's last like, pass or undo, which resurfacing's and undo's
    waiting periods count from; the field's default (the application's clock) fills a row written
    otherwise, as the proofs' seeded rows are.

    ``retired_at`` (SV4 A1, migration 0013; its brief's D3) is set by ``glow_chat``'s ``block``,
    with the database's clock, on every ``liked`` row between the pair, either way, and on
    nothing else of the row: a like made before a block never counts toward a match. A pass, or
    a like that replaces a pass, writes it null. No read of the actor's own row returns it."""

    actor = models.ForeignKey(AppAccount, on_delete=models.CASCADE, related_name="outgoing_actions")
    target = models.ForeignKey(
        AppAccount, on_delete=models.CASCADE, related_name="incoming_actions"
    )
    state = models.CharField(max_length=16, choices=choices("liked", "passed", "withdrawn"))
    policy_version = models.CharField(max_length=100)
    decided_at = models.DateTimeField(default=timezone.now)
    retired_at = models.DateTimeField(null=True)

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            nonself_check(),
            state_check("liked", "passed", "withdrawn"),
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


COLLECTIONS = ("recommendations", "discovery")


class RecommendationBatch(Record):
    """A viewer's bounded batch of candidates for one collection (SV3 Stage A, migration 0010;
    its brief's D7). ``collection`` is ``PageRequest.collection``; a viewer holds at most one
    batch per collection (``batch_one_per_collection``): creating one deletes the viewer's earlier
    batch of that collection, with its entries, in the same transaction."""

    account = models.ForeignKey(AppAccount, on_delete=models.CASCADE)
    collection = models.CharField(max_length=16, choices=choices(*COLLECTIONS))
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
            # SV3 Stage A (D7): the two collections, and one batch per viewer and collection.
            models.CheckConstraint(
                condition=Q(collection__in=COLLECTIONS), name="batch_collection"
            ),
            models.UniqueConstraint(
                fields=["account", "collection"], name="batch_one_per_collection"
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
    # P06.2 B1 (F3, CX6): set when a delivery that concerns this channel was dead-lettered,
    # to the Glow code of its last attempt; the provider may then hold a state Glow's
    # record does not show, and P11's reconciliation owns the row. Never provider text.
    reconcile_code = models.CharField(max_length=32, null=True, blank=True)

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


class ChatIdentity(Record):
    """An account's opaque chat-provider user ID (P06.2 D7, migration 0003).

    ``user_ref`` is random (``secrets.token_hex``), never derived from an account ID,
    name or email, and never shown or logged. The provider owns no other field of it:
    no name, image or custom data is ever set. PROTECT keeps the mapping until the
    provider deletion step that needs it has run (deletion and export, P07/P08).

    The identity is ``pending`` until the provider confirms the user exists (P06.2 B1,
    CX4; DM-15 3.2): ``active`` means provisioned, and only an ``active`` identity may be
    named in a channel or granted a token. ``reconcile_code`` marks an identity whose
    provisioning, deactivation or token revocation was dead-lettered (F3; DM-15 3.3).
    """

    account = models.ForeignKey(AppAccount, on_delete=models.PROTECT)
    provider = models.CharField(max_length=32)
    user_ref = models.CharField(max_length=64)
    state = models.CharField(
        max_length=16, choices=choices("pending", "active", "deactivated"), default="pending"
    )
    # The cut-off of the latest per-user token revocation the provider confirmed.
    tokens_revoked_before = models.DateTimeField(null=True, blank=True)
    # The Glow code of a dead-lettered delivery for this user (never provider text); set,
    # the row needs P11's reconciliation.
    reconcile_code = models.CharField(max_length=32, null=True, blank=True)

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            state_check("pending", "active", "deactivated"),
            models.UniqueConstraint(fields=["account", "provider"], name="chat_identity_account"),
            models.UniqueConstraint(fields=["provider", "user_ref"], name="chat_identity_ref"),
        ]


class ChatReadCursor(Record):
    """A member's read position in a match's conversation (P06.2 item 5, migration 0003).

    Unread is counted from Glow's own accepted ``MessageSubmission`` rows after
    ``last_read``; the provider's read state is not used. That the account is a member
    of the match is a repository check, not a constraint.
    """

    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    account = models.ForeignKey(AppAccount, on_delete=models.CASCADE)
    last_read = models.ForeignKey(
        MessageSubmission, null=True, blank=True, on_delete=models.PROTECT, related_name="+"
    )

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            models.UniqueConstraint(fields=["match", "account"], name="chat_read_cursor_member")
        ]


REGISTRATION_ENDINGS = ("revoke", "logout", "transfer")


class DeviceRegistration(Record):
    """One installation's push registration for one account (F12; SV4 B1, migration 0014; its
    brief's D17), as the domain keys it (``glow_domain.notifications.Registration``): the pair
    (``account``, ``installation_id``) is unique, and at most one row per installation is
    ``active`` (``device_one_active_installation``), so a transfer leaves the earlier account's
    row ``revoked`` (``ended_by`` ``transfer``).

    The custody rules are database constraints (DM-101's AM2), as ``AccountSession``'s revocation
    time and ``OutboxEvent``'s lease time are: ``token_secret_ref``, the token store's opaque
    reference and never a token, is present exactly while the row is ``active`` and unique where
    present (``device_reference_while_active``); ``ended_by`` names the transition that ended it
    and is present exactly when the row is ``revoked`` (``device_ended_when_revoked``).
    ``session`` is the ``AccountSession`` that last registered or rotated it (F12's "owner/session
    bound"). ``version`` (the base ``Record``'s) is the installation's view revision: 1 at the
    first registration, advanced by each change to the row and by each settings change of the
    account. No platform is kept: no contract field carries one (D17)."""

    account = models.ForeignKey(AppAccount, on_delete=models.CASCADE)
    installation_id = models.UUIDField()
    session = models.ForeignKey(AccountSession, on_delete=models.CASCADE)
    # Secure processor/vault reference only, never a plaintext push token; held only while active.
    token_secret_ref = models.CharField(max_length=255, unique=True, null=True, blank=True)
    state = models.CharField(max_length=16, choices=choices("active", "revoked"), default="active")
    ended_by = models.CharField(
        max_length=16, null=True, blank=True, choices=choices(*REGISTRATION_ENDINGS)
    )

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            state_check("active", "revoked"),
            models.UniqueConstraint(
                fields=["account", "installation_id"], name="device_account_installation"
            ),
            models.UniqueConstraint(
                fields=["installation_id"],
                condition=Q(state="active"),
                name="device_one_active_installation",
            ),
            models.CheckConstraint(
                condition=(
                    Q(state="active") & Q(token_secret_ref__isnull=False) & ~Q(token_secret_ref="")
                )
                | (~Q(state="active") & Q(token_secret_ref__isnull=True)),
                name="device_reference_while_active",
            ),
            # ``ended_by__isnull=False`` spelled out: ``NULL IN (...)`` is NULL, which a CHECK
            # constraint lets through, so without it a revoked row could name no ending.
            models.CheckConstraint(
                condition=Q(
                    state="revoked", ended_by__isnull=False, ended_by__in=REGISTRATION_ENDINGS
                )
                | (~Q(state="revoked") & Q(ended_by__isnull=True)),
                name="device_ended_when_revoked",
            ),
        ]


class NotificationSettings(Record):
    """An account's notification settings, both kinds off until changed (F12; SV4 B1, migration
    0014; its brief's D17): the contract's names, and no ``push_enabled``, since the contract has
    no such field and ``device_state`` says whether an installation can receive a push. Its
    ``version`` is the account's settings revision; the contract's ``version`` is the requesting
    installation's registration's (``DeviceRegistration.version``)."""

    account = models.OneToOneField(AppAccount, on_delete=models.CASCADE)
    match_notifications = models.BooleanField(default=False)
    message_notifications = models.BooleanField(default=False)


class NotificationLedgerEntry(Record):
    """The notification ledger (SV4 B1, migration 0014; its brief's D17 and D25), which SV4 B2's
    deliverer fills: one row per notification event and installation, ``pending`` when the event's
    first delivery fixes the installation, ``sent`` once the transport accepts it (or answers that
    it accepted it before). The installation is the domain's ``device_id``, so a registration
    revoked and made again keeps its row."""

    event = models.ForeignKey(OutboxEvent, on_delete=models.CASCADE)
    installation_id = models.UUIDField()
    state = models.CharField(max_length=16, choices=choices("pending", "sent"), default="pending")

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            state_check("pending", "sent"),
            models.UniqueConstraint(
                fields=["event", "installation_id"], name="notification_ledger_entry"
            ),
        ]


class PendingTokenDiscard(Record):
    """A token store reference that still has to be discarded, or may have to be (SV4 B1, migration
    0014; its brief's D17 and D18; DM-101's AM4; B1-C1, DM-102's AN1): a reference only, never a
    token. **A new reference's handle:** a register writes the reference the store gave it here,
    in its own statement before its transaction, and only if no registration and no pending
    discard already holds it; the transaction that saves the reference on a registration deletes
    this row, and refuses unless it deletes exactly this one. A command whose outcome is known and
    did not save the reference (a refusal, a deadlock, a replay, or a failure raised before its
    transaction's body returned) discards it at once and removes the row; one whose outcome is
    unknown (a failure at the commit) leaves the row for SV4 B2's sweep (its brief's D24), which
    takes it only once it is old and no registration holds its reference. **A retired
    reference:** an old reference a command retires (a rotation, a revocation or a transfer) is
    kept here in the command's own transaction and removed once the store has discarded it after
    the commit, so a failed discard waits here for the sweep to retry it."""

    token_secret_ref = models.CharField(max_length=255, unique=True)

    class Meta(Record.Meta):
        constraints = Record.Meta.constraints + [
            models.CheckConstraint(condition=~Q(token_secret_ref=""), name="pending_discard_ref"),
        ]


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
    # SV4 B1 (its brief's D17): F12's device and settings commands add their four receipt codes.
    outcome_code = models.CharField(
        max_length=16,
        null=True,
        blank=True,
        choices=choices(
            "committed",
            "liked",
            "passed",
            "unmatched",
            "blocked",
            "unblocked",
            "withdrawn",
            "register",
            "rotate",
            "revoke",
            "settings",
        ),
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
                        "withdrawn",
                        "register",
                        "rotate",
                        "revoke",
                        "settings",
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
