import uuid

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="OutboxEvent",
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
                ("aggregate_id", models.UUIDField()),
                (
                    "aggregate_version",
                    models.PositiveBigIntegerField(
                        validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                ("event_type", models.CharField(max_length=100)),
                ("schema_version", models.CharField(max_length=32)),
                ("dedup_key", models.CharField(max_length=160, unique=True)),
                ("payload_ref", models.UUIDField()),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("pending", "pending"),
                            ("leased", "leased"),
                            ("delivered", "delivered"),
                            ("dead_letter", "dead_letter"),
                        ],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("attempts", models.PositiveSmallIntegerField(default=0)),
                ("available_at", models.DateTimeField()),
                ("lease_expires_at", models.DateTimeField(blank=True, null=True)),
                ("delivered_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "abstract": False,
                "indexes": [
                    models.Index(fields=["state", "available_at"], name="outbox_delivery_queue")
                ],
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(("version__gte", 1)),
                        name="glow_persistence_outboxevent_version",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(
                            ("state__in", ("pending", "leased", "delivered", "dead_letter"))
                        ),
                        name="glow_persistence_outboxevent_state",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(("aggregate_version__gte", 1)), name="outbox_revision"
                    ),
                    models.CheckConstraint(
                        condition=models.Q(
                            models.Q(("delivered_at__isnull", False), ("state", "delivered")),
                            models.Q(
                                models.Q(("state", "delivered"), _negated=True),
                                ("delivered_at__isnull", True),
                            ),
                            _connector="OR",
                        ),
                        name="outbox_delivery_time",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(
                            models.Q(("lease_expires_at__isnull", False), ("state", "leased")),
                            models.Q(
                                models.Q(("state", "leased"), _negated=True),
                                ("lease_expires_at__isnull", True),
                            ),
                            _connector="OR",
                        ),
                        name="outbox_lease_time",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="WebhookInbox",
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
                ("provider_event_id", models.CharField(max_length=255)),
                ("payload_digest", models.CharField(max_length=64)),
                ("payload_ref", models.UUIDField()),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("received", "received"),
                            ("verified", "verified"),
                            ("applied", "applied"),
                            ("rejected", "rejected"),
                        ],
                        default="received",
                        max_length=16,
                    ),
                ),
                ("verified_at", models.DateTimeField(blank=True, null=True)),
                ("applied_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "abstract": False,
                "indexes": [
                    models.Index(fields=["state", "created_at"], name="inbox_processing_queue")
                ],
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(("version__gte", 1)),
                        name="glow_persistence_webhookinbox_version",
                    ),
                    models.UniqueConstraint(
                        fields=("provider", "provider_event_id"), name="inbox_event"
                    ),
                    models.CheckConstraint(
                        condition=models.Q(
                            ("state__in", ("received", "verified", "applied", "rejected"))
                        ),
                        name="glow_persistence_webhookinbox_state",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(
                            models.Q(("state__in", ["verified", "applied"]), _negated=True),
                            ("verified_at__isnull", False),
                            _connector="OR",
                        ),
                        name="inbox_requires_verification",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(
                            models.Q(("applied_at__isnull", False), ("state", "applied")),
                            models.Q(
                                models.Q(("state", "applied"), _negated=True),
                                ("applied_at__isnull", True),
                            ),
                            _connector="OR",
                        ),
                        name="inbox_application_time",
                    ),
                ],
            },
        ),
    ]
