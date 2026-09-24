import uuid

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("glow_persistence", "0001_event_infrastructure"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ModerationCase",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                ("assigned_staff_subject", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("submitted", "submitted"),
                            ("triaged", "triaged"),
                            ("investigating", "investigating"),
                            ("resolved", "resolved"),
                        ],
                        default="submitted",
                        max_length=16,
                    ),
                ),
                ("outcome_code", models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="AppAccount",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("unverified", "unverified"),
                            ("active", "active"),
                            ("suspended", "suspended"),
                            ("deletion_pending", "deletion_pending"),
                            ("deleted", "deleted"),
                        ],
                        default="unverified",
                        max_length=24,
                    ),
                ),
                ("eligibility_version", models.PositiveBigIntegerField(default=1)),
                ("preferences_version", models.PositiveBigIntegerField(default=1)),
                ("blocks_version", models.PositiveBigIntegerField(default=1)),
                ("session_epoch", models.PositiveBigIntegerField(default=1)),
                (
                    "auth_user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="AccountSession",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                ("auth_session_ref", models.CharField(max_length=255, unique=True)),
                (
                    "epoch",
                    models.PositiveBigIntegerField(
                        validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("valid", "valid"),
                            ("revoked", "revoked"),
                            ("expired", "expired"),
                        ],
                        default="valid",
                        max_length=16,
                    ),
                ),
                ("expires_at", models.DateTimeField()),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="glow_persistence.appaccount",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="BirthInput",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                ("birth_date", models.DateField()),
                ("local_time", models.TimeField(blank=True, null=True)),
                (
                    "time_precision",
                    models.CharField(
                        choices=[
                            ("known", "known"),
                            ("approximate", "approximate"),
                            ("unknown", "unknown"),
                        ],
                        max_length=16,
                    ),
                ),
                ("place_label", models.CharField(max_length=255)),
                ("timezone_name", models.CharField(blank=True, max_length=100, null=True)),
                ("timezone_provenance", models.CharField(blank=True, max_length=255, null=True)),
                ("consent_version", models.CharField(max_length=100)),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("missing", "missing"),
                            ("ambiguous", "ambiguous"),
                            ("pending", "pending"),
                            ("resolved", "resolved"),
                            ("unavailable", "unavailable"),
                            ("unsupported", "unsupported"),
                        ],
                        default="pending",
                        max_length=16,
                    ),
                ),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="glow_persistence.appaccount",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Block",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                (
                    "state",
                    models.CharField(
                        choices=[("active", "active"), ("removed", "removed")],
                        default="active",
                        max_length=16,
                    ),
                ),
                (
                    "actor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="outgoing_blocks",
                        to="glow_persistence.appaccount",
                    ),
                ),
                (
                    "target",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="incoming_blocks",
                        to="glow_persistence.appaccount",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="CompatibilitySnapshot",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                ("viewer_birth_version", models.PositiveBigIntegerField()),
                ("candidate_birth_version", models.PositiveBigIntegerField()),
                ("viewer_mapping_version", models.PositiveBigIntegerField()),
                ("candidate_mapping_version", models.PositiveBigIntegerField()),
                ("viewer_eligibility_version", models.PositiveBigIntegerField()),
                ("candidate_eligibility_version", models.PositiveBigIntegerField()),
                ("viewer_preferences_version", models.PositiveBigIntegerField()),
                ("candidate_preferences_version", models.PositiveBigIntegerField()),
                ("viewer_blocks_version", models.PositiveBigIntegerField()),
                ("candidate_blocks_version", models.PositiveBigIntegerField()),
                ("viewer_engine_reference", models.CharField(max_length=255)),
                ("candidate_engine_reference", models.CharField(max_length=255)),
                ("policy_version", models.CharField(max_length=100)),
                ("engine_version", models.CharField(max_length=100)),
                ("contract_version", models.CharField(max_length=100)),
                ("adapter_version", models.CharField(max_length=100)),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("ready", "ready"),
                            ("pending", "pending"),
                            ("unavailable", "unavailable"),
                            ("unsupported", "unsupported"),
                            ("stale", "stale"),
                        ],
                        max_length=16,
                    ),
                ),
                ("expires_at", models.DateTimeField()),
                (
                    "candidate",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="candidate_snapshots",
                        to="glow_persistence.appaccount",
                    ),
                ),
                (
                    "viewer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="viewed_snapshots",
                        to="glow_persistence.appaccount",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ConsentDecision",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                ("purpose", models.CharField(max_length=100)),
                ("policy_version", models.CharField(max_length=100)),
                (
                    "state",
                    models.CharField(
                        choices=[("accepted", "accepted"), ("withdrawn", "withdrawn")],
                        max_length=16,
                    ),
                ),
                ("decided_at", models.DateTimeField()),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="glow_persistence.appaccount",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="DeletionJob",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                ("subject_id", models.UUIDField(unique=True)),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("requested", "requested"),
                            ("access_revoked", "access_revoked"),
                            ("purging", "purging"),
                            ("blocked", "blocked"),
                            ("completed", "completed"),
                        ],
                        default="requested",
                        max_length=16,
                    ),
                ),
                (
                    "retention_policy_version",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("deadline_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "account",
                    models.OneToOneField(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="glow_persistence.appaccount",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="DeletionTombstone",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                ("subject_id", models.UUIDField(unique=True)),
                ("revoked_at", models.DateTimeField()),
                ("policy_version", models.CharField(blank=True, max_length=100, null=True)),
                ("replay_before", models.DateTimeField(blank=True, null=True)),
                (
                    "deletion",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="glow_persistence.deletionjob",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="DeviceRegistration",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                ("installation_id", models.UUIDField(unique=True)),
                (
                    "platform",
                    models.CharField(
                        choices=[("ios", "ios"), ("android", "android")], max_length=8
                    ),
                ),
                ("token_secret_ref", models.CharField(max_length=255, unique=True)),
                (
                    "state",
                    models.CharField(
                        choices=[("active", "active"), ("revoked", "revoked")],
                        default="active",
                        max_length=16,
                    ),
                ),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="glow_persistence.appaccount",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="DirectionalInteraction",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                (
                    "state",
                    models.CharField(
                        choices=[("liked", "liked"), ("passed", "passed")], max_length=16
                    ),
                ),
                ("policy_version", models.CharField(max_length=100)),
                (
                    "actor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="outgoing_actions",
                        to="glow_persistence.appaccount",
                    ),
                ),
                (
                    "target",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="incoming_actions",
                        to="glow_persistence.appaccount",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="EngineIdentity",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                ("engine_reference", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "state",
                    models.CharField(
                        choices=[("pending", "pending"), ("resolved", "resolved")],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("engine_version", models.CharField(blank=True, max_length=100, null=True)),
                ("contract_version", models.CharField(blank=True, max_length=100, null=True)),
                ("adapter_version", models.CharField(max_length=100)),
                (
                    "account",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="glow_persistence.appaccount",
                    ),
                ),
                (
                    "birth_input",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="glow_persistence.birthinput",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Entitlement",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                ("product_ref", models.CharField(max_length=128)),
                (
                    "state",
                    models.CharField(
                        choices=[("disabled", "disabled")], default="disabled", max_length=16
                    ),
                ),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="glow_persistence.appaccount",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ExportJob",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("requested", "requested"),
                            ("preparing", "preparing"),
                            ("ready", "ready"),
                            ("expired", "expired"),
                            ("failed", "failed"),
                        ],
                        default="requested",
                        max_length=16,
                    ),
                ),
                ("artifact_secret_ref", models.CharField(blank=True, max_length=255, null=True)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="glow_persistence.appaccount",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="IdempotencyRecord",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                ("actor_id", models.UUIDField()),
                ("operation", models.CharField(max_length=100)),
                ("key", models.CharField(max_length=128)),
                ("request_digest", models.CharField(max_length=64)),
                ("result_ref", models.UUIDField(blank=True, null=True)),
                ("result_version", models.PositiveBigIntegerField(blank=True, null=True)),
                (
                    "outcome_code",
                    models.CharField(
                        blank=True,
                        choices=[
                            (value, value)
                            for value in (
                                "committed",
                                "liked",
                                "passed",
                                "unmatched",
                                "blocked",
                                "unblocked",
                            )
                        ],
                        max_length=16,
                        null=True,
                    ),
                ),
                (
                    "state",
                    models.CharField(
                        choices=[("pending", "pending"), ("completed", "completed")],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("expires_at", models.DateTimeField()),
            ],
            options={
                "abstract": False,
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(("version__gte", 1)),
                        name="glow_persistence_idempotencyrecord_version",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(("state__in", ("pending", "completed"))),
                        name="glow_persistence_idempotencyrecord_state",
                    ),
                    models.UniqueConstraint(
                        fields=("actor_id", "operation", "key"), name="intent_dedup"
                    ),
                    models.CheckConstraint(
                        condition=models.Q(
                            models.Q(
                                (
                                    "outcome_code__in",
                                    (
                                        "committed",
                                        "liked",
                                        "passed",
                                        "unmatched",
                                        "blocked",
                                        "unblocked",
                                    ),
                                ),
                                ("outcome_code__isnull", False),
                                ("result_ref__isnull", False),
                                ("result_version__gte", 1),
                                ("result_version__isnull", False),
                                ("result_version__lte", 9007199254740991),
                                ("state", "completed"),
                            ),
                            models.Q(
                                ("outcome_code__isnull", True),
                                ("result_ref__isnull", True),
                                ("result_version__isnull", True),
                                ("state", "pending"),
                            ),
                            _connector="OR",
                        ),
                        name="intent_result",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="Match",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("active", "active"),
                            ("unmatched", "unmatched"),
                            ("restricted", "restricted"),
                        ],
                        default="active",
                        max_length=16,
                    ),
                ),
                ("contact_version", models.PositiveBigIntegerField(default=1)),
                (
                    "account_high",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="high_matches",
                        to="glow_persistence.appaccount",
                    ),
                ),
                (
                    "account_low",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="low_matches",
                        to="glow_persistence.appaccount",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ChatBinding",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                ("provider", models.CharField(max_length=32)),
                ("channel_ref", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("pending", "pending"),
                            ("active", "active"),
                            ("revoked", "revoked"),
                            ("failed", "failed"),
                        ],
                        default="pending",
                        max_length=16,
                    ),
                ),
                (
                    "match",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="glow_persistence.match"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="MediaAsset",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                ("provider", models.CharField(max_length=32)),
                ("storage_ref", models.CharField(blank=True, max_length=255, null=True)),
                ("approved_variant_ref", models.CharField(blank=True, max_length=255, null=True)),
                ("position", models.PositiveSmallIntegerField()),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("upload_pending", "upload_pending"),
                            ("quarantined", "quarantined"),
                            ("review_pending", "review_pending"),
                            ("approved", "approved"),
                            ("rejected", "rejected"),
                            ("removal_pending", "removal_pending"),
                            ("removed", "removed"),
                        ],
                        default="upload_pending",
                        max_length=24,
                    ),
                ),
                ("review_ref", models.UUIDField(blank=True, null=True)),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="glow_persistence.appaccount",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="MessageSubmission",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                ("contact_version", models.PositiveBigIntegerField()),
                ("idempotency_key", models.CharField(max_length=128)),
                ("request_digest", models.CharField(max_length=64)),
                ("text", models.TextField(blank=True, max_length=4000, null=True)),
                ("provider_message_ref", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("pending", "pending"),
                            ("accepted", "accepted"),
                            ("failed", "failed"),
                        ],
                        default="pending",
                        max_length=16,
                    ),
                ),
                (
                    "actor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="glow_persistence.appaccount",
                    ),
                ),
                (
                    "binding",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="glow_persistence.chatbinding",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Appeal",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                ("description", models.TextField(max_length=4000)),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("submitted", "submitted"),
                            ("reviewing", "reviewing"),
                            ("resolved", "resolved"),
                        ],
                        default="submitted",
                        max_length=16,
                    ),
                ),
                ("outcome_code", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "appellant",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="glow_persistence.appaccount",
                    ),
                ),
                (
                    "case",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="glow_persistence.moderationcase",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="NotificationSettings",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                ("push_enabled", models.BooleanField(default=False)),
                ("match_updates", models.BooleanField(default=False)),
                ("message_updates", models.BooleanField(default=False)),
                (
                    "account",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="glow_persistence.appaccount",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="PolicyRevision",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                ("policy_version", models.CharField(max_length=100)),
                ("artifact_ref", models.UUIDField()),
            ],
            options={
                "abstract": False,
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(("version__gte", 1)),
                        name="glow_persistence_policyrevision_version",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="Preferences",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                ("policy_version", models.CharField(blank=True, max_length=100, null=True)),
                ("values", models.JSONField(default=dict)),
                (
                    "account",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="glow_persistence.appaccount",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                ("display_name", models.CharField(max_length=80)),
                ("bio", models.TextField(blank=True, max_length=500)),
                ("location_label", models.CharField(blank=True, max_length=120)),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("incomplete", "incomplete"),
                            ("visible", "visible"),
                            ("paused", "paused"),
                            ("restricted", "restricted"),
                            ("removed", "removed"),
                        ],
                        default="incomplete",
                        max_length=16,
                    ),
                ),
                (
                    "account",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="glow_persistence.appaccount",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ProviderLifecycleStep",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                ("provider", models.CharField(max_length=32)),
                ("operation", models.CharField(max_length=100)),
                ("resource_ref", models.CharField(max_length=255)),
                ("idempotency_key", models.CharField(max_length=160, unique=True)),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("pending", "pending"),
                            ("running", "running"),
                            ("verified", "verified"),
                            ("blocked", "blocked"),
                            ("failed", "failed"),
                        ],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("attempts", models.PositiveSmallIntegerField(default=0)),
                ("next_attempt_at", models.DateTimeField(blank=True, null=True)),
                ("verification_ref", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "deletion",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="glow_persistence.deletionjob",
                    ),
                ),
                (
                    "export",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="glow_persistence.exportjob",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="RecommendationBatch",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                ("eligibility_version", models.PositiveBigIntegerField()),
                ("preferences_version", models.PositiveBigIntegerField()),
                ("blocks_version", models.PositiveBigIntegerField()),
                ("policy_version", models.CharField(max_length=100)),
                (
                    "limit",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(100),
                        ]
                    ),
                ),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("pending", "pending"),
                            ("ready", "ready"),
                            ("empty", "empty"),
                            ("stale", "stale"),
                            ("unavailable", "unavailable"),
                        ],
                        max_length=16,
                    ),
                ),
                ("expires_at", models.DateTimeField()),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="glow_persistence.appaccount",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="RecommendationEntry",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                (
                    "position",
                    models.PositiveSmallIntegerField(
                        validators=[django.core.validators.MaxValueValidator(99)]
                    ),
                ),
                ("candidate_eligibility_version", models.PositiveBigIntegerField()),
                ("candidate_preferences_version", models.PositiveBigIntegerField()),
                ("candidate_blocks_version", models.PositiveBigIntegerField()),
                (
                    "batch",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="glow_persistence.recommendationbatch",
                    ),
                ),
                (
                    "candidate",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="glow_persistence.appaccount",
                    ),
                ),
                (
                    "snapshot",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="glow_persistence.compatibilitysnapshot",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="SafetyReport",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                ("subject_marker", models.UUIDField()),
                ("reason_code", models.CharField(max_length=100)),
                ("description", models.TextField(max_length=4000)),
                ("evidence_refs", models.JSONField(default=list)),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("submitted", "submitted"),
                            ("triaged", "triaged"),
                            ("investigating", "investigating"),
                            ("resolved", "resolved"),
                        ],
                        default="submitted",
                        max_length=16,
                    ),
                ),
                (
                    "retention_policy_version",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("retention_due_at", models.DateTimeField(blank=True, null=True)),
                (
                    "reporter",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="reports_made",
                        to="glow_persistence.appaccount",
                    ),
                ),
                (
                    "subject",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="reports_received",
                        to="glow_persistence.appaccount",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="moderationcase",
            name="report",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="glow_persistence.safetyreport"
            ),
        ),
        migrations.CreateModel(
            name="StaffAudit",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                ("staff_subject", models.CharField(max_length=255)),
                ("scope", models.CharField(max_length=100)),
                ("action", models.CharField(max_length=100)),
                ("object_type", models.CharField(max_length=100)),
                ("object_id", models.UUIDField()),
                ("reason_code", models.CharField(max_length=100)),
                ("request_id", models.UUIDField(unique=True)),
                ("before_version", models.PositiveBigIntegerField(blank=True, null=True)),
                ("after_version", models.PositiveBigIntegerField(blank=True, null=True)),
            ],
            options={
                "abstract": False,
                "indexes": [
                    models.Index(
                        fields=["object_type", "object_id", "created_at"], name="audit_object"
                    )
                ],
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(("version__gte", 1)),
                        name="glow_persistence_staffaudit_version",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="SupportRequest",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                ("contact_secret_ref", models.CharField(blank=True, max_length=255, null=True)),
                ("category", models.CharField(max_length=100)),
                ("subject", models.CharField(max_length=200)),
                ("description", models.TextField(max_length=4000)),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("open", "open"),
                            ("in_progress", "in_progress"),
                            ("resolved", "resolved"),
                        ],
                        default="open",
                        max_length=16,
                    ),
                ),
                (
                    "retention_policy_version",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("retention_due_at", models.DateTimeField(blank=True, null=True)),
                (
                    "account",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="glow_persistence.appaccount",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddConstraint(
            model_name="appaccount",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)), name="glow_persistence_appaccount_version"
            ),
        ),
        migrations.AddConstraint(
            model_name="appaccount",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    (
                        "state__in",
                        ("unverified", "active", "suspended", "deletion_pending", "deleted"),
                    )
                ),
                name="glow_persistence_appaccount_state",
            ),
        ),
        migrations.AddConstraint(
            model_name="appaccount",
            constraint=models.CheckConstraint(
                condition=models.Q(("eligibility_version__gte", 1)), name="account_elig_rev"
            ),
        ),
        migrations.AddConstraint(
            model_name="appaccount",
            constraint=models.CheckConstraint(
                condition=models.Q(("preferences_version__gte", 1)), name="account_pref_rev"
            ),
        ),
        migrations.AddConstraint(
            model_name="appaccount",
            constraint=models.CheckConstraint(
                condition=models.Q(("blocks_version__gte", 1)), name="account_blocks_rev"
            ),
        ),
        migrations.AddConstraint(
            model_name="appaccount",
            constraint=models.CheckConstraint(
                condition=models.Q(("session_epoch__gte", 1)), name="account_session_epoch"
            ),
        ),
        migrations.AddIndex(
            model_name="accountsession",
            index=models.Index(fields=["account", "state"], name="account_session_state"),
        ),
        migrations.AddConstraint(
            model_name="accountsession",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)),
                name="glow_persistence_accountsession_version",
            ),
        ),
        migrations.AddConstraint(
            model_name="accountsession",
            constraint=models.CheckConstraint(
                condition=models.Q(("state__in", ("valid", "revoked", "expired"))),
                name="glow_persistence_accountsession_state",
            ),
        ),
        migrations.AddConstraint(
            model_name="accountsession",
            constraint=models.CheckConstraint(
                condition=models.Q(("epoch__gte", 1)), name="session_epoch_positive"
            ),
        ),
        migrations.AddConstraint(
            model_name="accountsession",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("revoked_at__isnull", False), ("state", "revoked")),
                    models.Q(
                        models.Q(("state", "revoked"), _negated=True), ("revoked_at__isnull", True)
                    ),
                    _connector="OR",
                ),
                name="session_revocation_time",
            ),
        ),
        migrations.AddConstraint(
            model_name="birthinput",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)), name="glow_persistence_birthinput_version"
            ),
        ),
        migrations.AddConstraint(
            model_name="birthinput",
            constraint=models.UniqueConstraint(
                fields=("account", "version"), name="birth_input_revision"
            ),
        ),
        migrations.AddConstraint(
            model_name="birthinput",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    (
                        "state__in",
                        (
                            "missing",
                            "ambiguous",
                            "pending",
                            "resolved",
                            "unavailable",
                            "unsupported",
                        ),
                    )
                ),
                name="glow_persistence_birthinput_state",
            ),
        ),
        migrations.AddConstraint(
            model_name="birthinput",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("local_time__isnull", True), ("time_precision", "unknown")),
                    models.Q(
                        ("local_time__isnull", False),
                        ("time_precision__in", ["known", "approximate"]),
                    ),
                    _connector="OR",
                ),
                name="birth_time_uncertainty",
            ),
        ),
        migrations.AddConstraint(
            model_name="birthinput",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(
                        ("timezone_name__isnull", True), ("timezone_provenance__isnull", True)
                    ),
                    models.Q(
                        ("timezone_name__isnull", False), ("timezone_provenance__isnull", False)
                    ),
                    _connector="OR",
                ),
                name="birth_timezone_provenance",
            ),
        ),
        migrations.AddConstraint(
            model_name="block",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)), name="glow_persistence_block_version"
            ),
        ),
        migrations.AddConstraint(
            model_name="block",
            constraint=models.CheckConstraint(
                condition=models.Q(("actor", models.F("target")), _negated=True),
                name="glow_persistence_block_no_self",
            ),
        ),
        migrations.AddConstraint(
            model_name="block",
            constraint=models.CheckConstraint(
                condition=models.Q(("state__in", ("active", "removed"))),
                name="glow_persistence_block_state",
            ),
        ),
        migrations.AddConstraint(
            model_name="block",
            constraint=models.UniqueConstraint(
                fields=("actor", "target"), name="directional_block_pair"
            ),
        ),
        migrations.AddIndex(
            model_name="compatibilitysnapshot",
            index=models.Index(fields=["viewer", "expires_at"], name="snapshot_expiry_lookup"),
        ),
        migrations.AddConstraint(
            model_name="compatibilitysnapshot",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)),
                name="glow_persistence_compatibilitysnapshot_version",
            ),
        ),
        migrations.AddConstraint(
            model_name="compatibilitysnapshot",
            constraint=models.CheckConstraint(
                condition=models.Q(("viewer", models.F("candidate")), _negated=True),
                name="glow_persistence_compatibilitysnapshot_no_self",
            ),
        ),
        migrations.AddConstraint(
            model_name="compatibilitysnapshot",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("state__in", ("ready", "pending", "unavailable", "unsupported", "stale"))
                ),
                name="glow_persistence_compatibilitysnapshot_state",
            ),
        ),
        migrations.AddConstraint(
            model_name="compatibilitysnapshot",
            constraint=models.UniqueConstraint(
                fields=(
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
                ),
                name="snapshot_directional_revision",
            ),
        ),
        migrations.AddConstraint(
            model_name="compatibilitysnapshot",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("candidate_birth_version__gte", 1),
                    ("candidate_blocks_version__gte", 1),
                    ("candidate_eligibility_version__gte", 1),
                    ("candidate_mapping_version__gte", 1),
                    ("candidate_preferences_version__gte", 1),
                    ("viewer_birth_version__gte", 1),
                    ("viewer_blocks_version__gte", 1),
                    ("viewer_eligibility_version__gte", 1),
                    ("viewer_mapping_version__gte", 1),
                    ("viewer_preferences_version__gte", 1),
                ),
                name="snapshot_positive_revisions",
            ),
        ),
        migrations.AddIndex(
            model_name="consentdecision",
            index=models.Index(
                fields=["account", "purpose", "decided_at"], name="consent_current_lookup"
            ),
        ),
        migrations.AddConstraint(
            model_name="consentdecision",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)),
                name="glow_persistence_consentdecision_version",
            ),
        ),
        migrations.AddConstraint(
            model_name="consentdecision",
            constraint=models.CheckConstraint(
                condition=models.Q(("state__in", ("accepted", "withdrawn"))),
                name="glow_persistence_consentdecision_state",
            ),
        ),
        migrations.AddConstraint(
            model_name="consentdecision",
            constraint=models.UniqueConstraint(
                fields=("account", "purpose", "version"), name="consent_decision_revision"
            ),
        ),
        migrations.AddConstraint(
            model_name="deletionjob",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)), name="glow_persistence_deletionjob_version"
            ),
        ),
        migrations.AddConstraint(
            model_name="deletionjob",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    (
                        "state__in",
                        ("requested", "access_revoked", "purging", "blocked", "completed"),
                    )
                ),
                name="glow_persistence_deletionjob_state",
            ),
        ),
        migrations.AddConstraint(
            model_name="deletionjob",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("completed_at__isnull", False), ("state", "completed")),
                    models.Q(
                        models.Q(("state", "completed"), _negated=True),
                        ("completed_at__isnull", True),
                    ),
                    _connector="OR",
                ),
                name="deletion_completion",
            ),
        ),
        migrations.AddConstraint(
            model_name="deletiontombstone",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)),
                name="glow_persistence_deletiontombstone_version",
            ),
        ),
        migrations.AddConstraint(
            model_name="deviceregistration",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)),
                name="glow_persistence_deviceregistration_version",
            ),
        ),
        migrations.AddConstraint(
            model_name="deviceregistration",
            constraint=models.CheckConstraint(
                condition=models.Q(("state__in", ("active", "revoked"))),
                name="glow_persistence_deviceregistration_state",
            ),
        ),
        migrations.AddConstraint(
            model_name="deviceregistration",
            constraint=models.CheckConstraint(
                condition=models.Q(("platform__in", ["ios", "android"])), name="device_platform"
            ),
        ),
        migrations.AddConstraint(
            model_name="directionalinteraction",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)),
                name="glow_persistence_directionalinteraction_version",
            ),
        ),
        migrations.AddConstraint(
            model_name="directionalinteraction",
            constraint=models.CheckConstraint(
                condition=models.Q(("actor", models.F("target")), _negated=True),
                name="glow_persistence_directionalinteraction_no_self",
            ),
        ),
        migrations.AddConstraint(
            model_name="directionalinteraction",
            constraint=models.CheckConstraint(
                condition=models.Q(("state__in", ("liked", "passed"))),
                name="glow_persistence_directionalinteraction_state",
            ),
        ),
        migrations.AddConstraint(
            model_name="directionalinteraction",
            constraint=models.UniqueConstraint(
                fields=("actor", "target"), name="directional_interaction_pair"
            ),
        ),
        migrations.AddConstraint(
            model_name="engineidentity",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)),
                name="glow_persistence_engineidentity_version",
            ),
        ),
        migrations.AddConstraint(
            model_name="engineidentity",
            constraint=models.CheckConstraint(
                condition=models.Q(("state__in", ("pending", "resolved"))),
                name="glow_persistence_engineidentity_state",
            ),
        ),
        migrations.AddConstraint(
            model_name="engineidentity",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(
                        ("contract_version__isnull", False),
                        ("engine_reference__isnull", False),
                        ("engine_version__isnull", False),
                        ("state", "resolved"),
                    ),
                    models.Q(
                        ("contract_version__isnull", True),
                        ("engine_reference__isnull", True),
                        ("engine_version__isnull", True),
                        ("state", "pending"),
                    ),
                    _connector="OR",
                ),
                name="engine_mapping_provenance",
            ),
        ),
        migrations.AddConstraint(
            model_name="entitlement",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)), name="glow_persistence_entitlement_version"
            ),
        ),
        migrations.AddConstraint(
            model_name="entitlement",
            constraint=models.CheckConstraint(
                condition=models.Q(("state__in", ("disabled",))),
                name="glow_persistence_entitlement_state",
            ),
        ),
        migrations.AddConstraint(
            model_name="entitlement",
            constraint=models.UniqueConstraint(
                fields=("account", "product_ref"), name="entitlement_product"
            ),
        ),
        migrations.AddConstraint(
            model_name="exportjob",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)), name="glow_persistence_exportjob_version"
            ),
        ),
        migrations.AddConstraint(
            model_name="exportjob",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("state__in", ("requested", "preparing", "ready", "expired", "failed"))
                ),
                name="glow_persistence_exportjob_state",
            ),
        ),
        migrations.AddConstraint(
            model_name="exportjob",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("state", "ready"), _negated=True),
                    models.Q(("artifact_secret_ref__isnull", False), ("expires_at__isnull", False)),
                    _connector="OR",
                ),
                name="export_ready_artifact",
            ),
        ),
        migrations.AddConstraint(
            model_name="match",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)), name="glow_persistence_match_version"
            ),
        ),
        migrations.AddConstraint(
            model_name="match",
            constraint=models.CheckConstraint(
                condition=models.Q(("state__in", ("active", "unmatched", "restricted"))),
                name="glow_persistence_match_state",
            ),
        ),
        migrations.AddConstraint(
            model_name="match",
            constraint=models.CheckConstraint(
                condition=models.Q(("account_low__lt", models.F("account_high"))),
                name="match_order",
            ),
        ),
        migrations.AddConstraint(
            model_name="match",
            constraint=models.UniqueConstraint(
                fields=("account_low", "account_high"), name="match_pair"
            ),
        ),
        migrations.AddConstraint(
            model_name="match",
            constraint=models.CheckConstraint(
                condition=models.Q(("contact_version__gte", 1)), name="match_contact_revision"
            ),
        ),
        migrations.AddConstraint(
            model_name="chatbinding",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)), name="glow_persistence_chatbinding_version"
            ),
        ),
        migrations.AddConstraint(
            model_name="chatbinding",
            constraint=models.CheckConstraint(
                condition=models.Q(("state__in", ("pending", "active", "revoked", "failed"))),
                name="glow_persistence_chatbinding_state",
            ),
        ),
        migrations.AddConstraint(
            model_name="chatbinding",
            constraint=models.UniqueConstraint(
                fields=("provider", "channel_ref"), name="chat_provider_channel"
            ),
        ),
        migrations.AddConstraint(
            model_name="chatbinding",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("state", "active"), _negated=True),
                    ("channel_ref__isnull", False),
                    _connector="OR",
                ),
                name="chat_active_ref",
            ),
        ),
        migrations.AddConstraint(
            model_name="mediaasset",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)), name="glow_persistence_mediaasset_version"
            ),
        ),
        migrations.AddConstraint(
            model_name="mediaasset",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    (
                        "state__in",
                        (
                            "upload_pending",
                            "quarantined",
                            "review_pending",
                            "approved",
                            "rejected",
                            "removal_pending",
                            "removed",
                        ),
                    )
                ),
                name="glow_persistence_mediaasset_state",
            ),
        ),
        migrations.AddConstraint(
            model_name="mediaasset",
            constraint=models.UniqueConstraint(
                fields=("provider", "storage_ref"), name="media_provider_ref"
            ),
        ),
        migrations.AddConstraint(
            model_name="mediaasset",
            constraint=models.UniqueConstraint(
                condition=models.Q(("state", "removed"), _negated=True),
                fields=("account", "position"),
                name="media_current_order",
            ),
        ),
        migrations.AddConstraint(
            model_name="mediaasset",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("state", "approved"), _negated=True),
                    models.Q(
                        ("approved_variant_ref__isnull", False), ("review_ref__isnull", False)
                    ),
                    _connector="OR",
                ),
                name="media_approval_evidence",
            ),
        ),
        migrations.AddConstraint(
            model_name="messagesubmission",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)),
                name="glow_persistence_messagesubmission_version",
            ),
        ),
        migrations.AddConstraint(
            model_name="messagesubmission",
            constraint=models.CheckConstraint(
                condition=models.Q(("state__in", ("pending", "accepted", "failed"))),
                name="glow_persistence_messagesubmission_state",
            ),
        ),
        migrations.AddConstraint(
            model_name="messagesubmission",
            constraint=models.UniqueConstraint(
                fields=("actor", "idempotency_key"), name="message_dedup"
            ),
        ),
        migrations.AddConstraint(
            model_name="messagesubmission",
            constraint=models.CheckConstraint(
                condition=models.Q(("contact_version__gte", 1)), name="message_contact_rev"
            ),
        ),
        migrations.AddConstraint(
            model_name="messagesubmission",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("state", "accepted"), _negated=True),
                    ("provider_message_ref__isnull", False),
                    _connector="OR",
                ),
                name="message_acceptance_ref",
            ),
        ),
        migrations.AddConstraint(
            model_name="messagesubmission",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("state", "pending"), _negated=True),
                    ("text__isnull", False),
                    _connector="OR",
                ),
                name="message_pending_text",
            ),
        ),
        migrations.AddConstraint(
            model_name="appeal",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)), name="glow_persistence_appeal_version"
            ),
        ),
        migrations.AddConstraint(
            model_name="appeal",
            constraint=models.CheckConstraint(
                condition=models.Q(("state__in", ("submitted", "reviewing", "resolved"))),
                name="glow_persistence_appeal_state",
            ),
        ),
        migrations.AddConstraint(
            model_name="appeal",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("state", "resolved"), _negated=True),
                    ("outcome_code__isnull", False),
                    _connector="OR",
                ),
                name="appeal_outcome",
            ),
        ),
        migrations.AddConstraint(
            model_name="notificationsettings",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)),
                name="glow_persistence_notificationsettings_version",
            ),
        ),
        migrations.AddConstraint(
            model_name="preferences",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)), name="glow_persistence_preferences_version"
            ),
        ),
        migrations.AddIndex(
            model_name="profile",
            index=models.Index(fields=["state", "id"], name="profile_visibility_cursor"),
        ),
        migrations.AddConstraint(
            model_name="profile",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)), name="glow_persistence_profile_version"
            ),
        ),
        migrations.AddConstraint(
            model_name="profile",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("state__in", ("incomplete", "visible", "paused", "restricted", "removed"))
                ),
                name="glow_persistence_profile_state",
            ),
        ),
        migrations.AddIndex(
            model_name="providerlifecyclestep",
            index=models.Index(fields=["state", "next_attempt_at"], name="lifecycle_retry_queue"),
        ),
        migrations.AddConstraint(
            model_name="providerlifecyclestep",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)),
                name="glow_persistence_providerlifecyclestep_version",
            ),
        ),
        migrations.AddConstraint(
            model_name="providerlifecyclestep",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("state__in", ("pending", "running", "verified", "blocked", "failed"))
                ),
                name="glow_persistence_providerlifecyclestep_state",
            ),
        ),
        migrations.AddConstraint(
            model_name="providerlifecyclestep",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("deletion__isnull", False), ("export__isnull", True)),
                    models.Q(("deletion__isnull", True), ("export__isnull", False)),
                    _connector="OR",
                ),
                name="provider_step_one_job",
            ),
        ),
        migrations.AddConstraint(
            model_name="providerlifecyclestep",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("state", "verified"), _negated=True),
                    ("verification_ref__isnull", False),
                    _connector="OR",
                ),
                name="provider_step_evidence",
            ),
        ),
        migrations.AddIndex(
            model_name="recommendationbatch",
            index=models.Index(fields=["account", "created_at", "id"], name="batch_owner_cursor"),
        ),
        migrations.AddConstraint(
            model_name="recommendationbatch",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)),
                name="glow_persistence_recommendationbatch_version",
            ),
        ),
        migrations.AddConstraint(
            model_name="recommendationbatch",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("state__in", ("pending", "ready", "empty", "stale", "unavailable"))
                ),
                name="glow_persistence_recommendationbatch_state",
            ),
        ),
        migrations.AddConstraint(
            model_name="recommendationbatch",
            constraint=models.CheckConstraint(
                condition=models.Q(("limit__gte", 1), ("limit__lte", 100)), name="batch_bound"
            ),
        ),
        migrations.AddConstraint(
            model_name="recommendationbatch",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("blocks_version__gte", 1),
                    ("eligibility_version__gte", 1),
                    ("preferences_version__gte", 1),
                ),
                name="batch_elig_revision",
            ),
        ),
        migrations.AddConstraint(
            model_name="recommendationentry",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)),
                name="glow_persistence_recommendationentry_version",
            ),
        ),
        migrations.AddConstraint(
            model_name="recommendationentry",
            constraint=models.UniqueConstraint(
                fields=("batch", "candidate"), name="batch_distinct_candidate"
            ),
        ),
        migrations.AddConstraint(
            model_name="recommendationentry",
            constraint=models.UniqueConstraint(fields=("batch", "position"), name="batch_position"),
        ),
        migrations.AddConstraint(
            model_name="recommendationentry",
            constraint=models.CheckConstraint(
                condition=models.Q(("position__lte", 99)), name="entry_position_bound"
            ),
        ),
        migrations.AddConstraint(
            model_name="recommendationentry",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("candidate_blocks_version__gte", 1),
                    ("candidate_eligibility_version__gte", 1),
                    ("candidate_preferences_version__gte", 1),
                ),
                name="entry_elig_revision",
            ),
        ),
        migrations.AddConstraint(
            model_name="safetyreport",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)),
                name="glow_persistence_safetyreport_version",
            ),
        ),
        migrations.AddConstraint(
            model_name="safetyreport",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("state__in", ("submitted", "triaged", "investigating", "resolved"))
                ),
                name="glow_persistence_safetyreport_state",
            ),
        ),
        migrations.AddIndex(
            model_name="moderationcase",
            index=models.Index(fields=["state", "created_at"], name="moderation_queue"),
        ),
        migrations.AddConstraint(
            model_name="moderationcase",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)),
                name="glow_persistence_moderationcase_version",
            ),
        ),
        migrations.AddConstraint(
            model_name="moderationcase",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("state__in", ("submitted", "triaged", "investigating", "resolved"))
                ),
                name="glow_persistence_moderationcase_state",
            ),
        ),
        migrations.AddConstraint(
            model_name="moderationcase",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("state", "resolved"), _negated=True),
                    ("outcome_code__isnull", False),
                    _connector="OR",
                ),
                name="case_outcome",
            ),
        ),
        migrations.AddConstraint(
            model_name="supportrequest",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)),
                name="glow_persistence_supportrequest_version",
            ),
        ),
        migrations.AddConstraint(
            model_name="supportrequest",
            constraint=models.CheckConstraint(
                condition=models.Q(("state__in", ("open", "in_progress", "resolved"))),
                name="glow_persistence_supportrequest_state",
            ),
        ),
    ]
