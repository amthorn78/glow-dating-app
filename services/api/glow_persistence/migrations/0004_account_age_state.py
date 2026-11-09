import uuid

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("glow_persistence", "0003_chat_identity_read_cursor"),
    ]

    operations = [
        migrations.CreateModel(
            name="AccountAgeState",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    models.PositiveBigIntegerField(
                        default=1,
                        validators=[django.core.validators.MinValueValidator(1)],
                    ),
                ),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("unknown", "unknown"),
                            ("self_declared_adult", "self_declared_adult"),
                        ],
                        max_length=32,
                    ),
                ),
                (
                    "method",
                    models.CharField(
                        choices=[
                            ("none", "none"),
                            ("self_declaration", "self_declaration"),
                        ],
                        max_length=32,
                    ),
                ),
                ("recorded_at", models.DateTimeField()),
                (
                    "policy_version",
                    models.CharField(blank=True, max_length=100, null=True),
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
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(("version__gte", 1)),
                        name="glow_persistence_accountagestate_version",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(("state__in", ("unknown", "self_declared_adult"))),
                        name="glow_persistence_accountagestate_state",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(("method__in", ["none", "self_declaration"])),
                        name="age_state_method",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(
                            models.Q(
                                ("method", "none"),
                                ("policy_version__isnull", True),
                                ("state", "unknown"),
                            ),
                            models.Q(
                                ("method", "self_declaration"),
                                ("policy_version__isnull", False),
                                ("state", "self_declared_adult"),
                            ),
                            _connector="OR",
                        ),
                        name="age_state_provenance",
                    ),
                ],
            },
        ),
    ]
