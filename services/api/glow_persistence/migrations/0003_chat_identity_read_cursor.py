import uuid

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models

import glow_persistence.fields


class Migration(migrations.Migration):
    dependencies = [
        ("glow_persistence", "0002_app_domain"),
    ]

    operations = [
        migrations.AddField(
            model_name="chatbinding",
            name="reconcile_code",
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name="outboxevent",
            name="sequence",
            field=glow_persistence.fields.SequenceField(),
        ),
        migrations.CreateModel(
            name="ChatIdentity",
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
                ("user_ref", models.CharField(max_length=64)),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("pending", "pending"),
                            ("active", "active"),
                            ("deactivated", "deactivated"),
                        ],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("tokens_revoked_before", models.DateTimeField(blank=True, null=True)),
                ("reconcile_code", models.CharField(blank=True, max_length=32, null=True)),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="glow_persistence.appaccount",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(("version__gte", 1)),
                        name="glow_persistence_chatidentity_version",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(("state__in", ("pending", "active", "deactivated"))),
                        name="glow_persistence_chatidentity_state",
                    ),
                    models.UniqueConstraint(
                        fields=("account", "provider"), name="chat_identity_account"
                    ),
                    models.UniqueConstraint(
                        fields=("provider", "user_ref"), name="chat_identity_ref"
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="ChatReadCursor",
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
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="glow_persistence.appaccount",
                    ),
                ),
                (
                    "last_read",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="glow_persistence.messagesubmission",
                    ),
                ),
                (
                    "match",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="glow_persistence.match"
                    ),
                ),
            ],
            options={
                "abstract": False,
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(("version__gte", 1)),
                        name="glow_persistence_chatreadcursor_version",
                    ),
                    models.UniqueConstraint(
                        fields=("match", "account"), name="chat_read_cursor_member"
                    ),
                ],
            },
        ),
    ]
