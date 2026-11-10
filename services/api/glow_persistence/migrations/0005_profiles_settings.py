import uuid

import django.contrib.postgres.indexes
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("glow_persistence", "0004_account_age_state"),
    ]

    operations = [
        migrations.CreateModel(
            name="Area",
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
                ("area_id", models.CharField(max_length=5, unique=True)),
                ("name", models.CharField(max_length=80)),
                ("latitude", models.DecimalField(decimal_places=6, max_digits=9)),
                ("longitude", models.DecimalField(decimal_places=6, max_digits=9)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="IdentityVerification",
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
                            ("unverified", "unverified"),
                            ("verified", "verified"),
                            ("staff_approved", "staff_approved"),
                        ],
                        default="unverified",
                        max_length=24,
                    ),
                ),
                (
                    "method",
                    models.CharField(
                        choices=[
                            ("none", "none"),
                            ("automated_check", "automated_check"),
                            ("staff_approval", "staff_approval"),
                        ],
                        default="none",
                        max_length=24,
                    ),
                ),
                (
                    "provider_reference",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "staff_subject",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("reason", models.CharField(blank=True, max_length=100, null=True)),
                ("decided_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="PreferenceSetEntry",
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
                    "field",
                    models.CharField(
                        choices=[
                            ("gender", "gender"),
                            ("orientation", "orientation"),
                            ("looking_for", "looking_for"),
                            ("relationship_status", "relationship_status"),
                        ],
                        max_length=32,
                    ),
                ),
                ("value_id", models.CharField(max_length=100)),
                ("position", models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ProfileFieldChoice",
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
                    "field",
                    models.CharField(
                        choices=[
                            ("gender", "gender"),
                            ("orientation", "orientation"),
                            ("looking_for", "looking_for"),
                            ("relationship_status", "relationship_status"),
                        ],
                        max_length=32,
                    ),
                ),
                ("value_ids", models.JSONField()),
                (
                    "setting_version",
                    models.PositiveBigIntegerField(
                        validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                ("own_words", models.CharField(blank=True, max_length=40, null=True)),
                ("shown", models.BooleanField(default=False)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="SettingVersion",
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
                ("name", models.CharField(max_length=100)),
                (
                    "number",
                    models.PositiveBigIntegerField(
                        validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                ("content", models.JSONField()),
                ("published_at", models.DateTimeField()),
                ("staff_subject", models.CharField(max_length=255)),
                ("reason", models.CharField(max_length=100)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.RemoveField(
            model_name="profile",
            name="location_label",
        ),
        migrations.AddField(
            model_name="accountagestate",
            name="birth_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="preferences",
            name="distance_choice",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="preferences",
            name="maximum_age",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="preferences",
            name="minimum_age",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddConstraint(
            model_name="accountagestate",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("birth_date__isnull", True), ("state", "unknown")),
                    models.Q(("birth_date__isnull", False), ("state", "self_declared_adult")),
                    _connector="OR",
                ),
                name="age_state_birth_date",
            ),
        ),
        migrations.AddConstraint(
            model_name="consentdecision",
            constraint=models.CheckConstraint(
                condition=models.Q(("purpose__in", ["onboarding", "sensitive_profile"])),
                name="consent_purpose",
            ),
        ),
        migrations.AddConstraint(
            model_name="preferences",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("minimum_age__isnull", True),
                    ("minimum_age__gte", 18),
                    _connector="OR",
                ),
                name="preferences_age_floor",
            ),
        ),
        migrations.AddConstraint(
            model_name="preferences",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("maximum_age__isnull", True),
                    models.Q(
                        ("maximum_age__gte", models.F("minimum_age")),
                        ("minimum_age__isnull", False),
                    ),
                    _connector="OR",
                ),
                name="preferences_age_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="area",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)),
                name="glow_persistence_area_version",
            ),
        ),
        migrations.AddConstraint(
            model_name="area",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("latitude__gte", -90),
                    ("latitude__lte", 90),
                    ("longitude__gte", -180),
                    ("longitude__lte", 180),
                ),
                name="area_internal_point",
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="area",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="profiles",
                to="glow_persistence.area",
            ),
        ),
        migrations.AddField(
            model_name="identityverification",
            name="account",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                to="glow_persistence.appaccount",
            ),
        ),
        migrations.AddField(
            model_name="preferencesetentry",
            name="account",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="glow_persistence.appaccount",
            ),
        ),
        migrations.AddField(
            model_name="profilefieldchoice",
            name="account",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="glow_persistence.appaccount",
            ),
        ),
        migrations.AddConstraint(
            model_name="settingversion",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)),
                name="glow_persistence_settingversion_version",
            ),
        ),
        migrations.AddConstraint(
            model_name="settingversion",
            constraint=models.UniqueConstraint(
                fields=("name", "number"), name="setting_version_number"
            ),
        ),
        migrations.AddConstraint(
            model_name="settingversion",
            constraint=models.CheckConstraint(
                condition=models.Q(("number__gte", 1)), name="setting_version_positive"
            ),
        ),
        migrations.AddConstraint(
            model_name="identityverification",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)),
                name="glow_persistence_identityverification_version",
            ),
        ),
        migrations.AddConstraint(
            model_name="identityverification",
            constraint=models.CheckConstraint(
                condition=models.Q(("state__in", ("unverified", "verified", "staff_approved"))),
                name="glow_persistence_identityverification_state",
            ),
        ),
        migrations.AddConstraint(
            model_name="identityverification",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(
                        ("method", "none"),
                        ("provider_reference__isnull", True),
                        ("reason__isnull", True),
                        ("staff_subject__isnull", True),
                        ("state", "unverified"),
                    ),
                    models.Q(
                        ("decided_at__isnull", False),
                        ("method", "automated_check"),
                        ("provider_reference__isnull", False),
                        ("reason__isnull", True),
                        ("staff_subject__isnull", True),
                        ("state", "verified"),
                    ),
                    models.Q(
                        ("decided_at__isnull", False),
                        ("method", "staff_approval"),
                        ("provider_reference__isnull", True),
                        ("reason__isnull", False),
                        ("staff_subject__isnull", False),
                        ("state", "staff_approved"),
                    ),
                    _connector="OR",
                ),
                name="identity_verification_provenance",
            ),
        ),
        migrations.AddIndex(
            model_name="preferencesetentry",
            index=models.Index(
                fields=["field", "value_id", "account"], name="preference_set_lookup"
            ),
        ),
        migrations.AddConstraint(
            model_name="preferencesetentry",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)),
                name="glow_persistence_preferencesetentry_version",
            ),
        ),
        migrations.AddConstraint(
            model_name="preferencesetentry",
            constraint=models.UniqueConstraint(
                fields=("account", "field", "value_id"), name="preference_set_value"
            ),
        ),
        migrations.AddConstraint(
            model_name="preferencesetentry",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    (
                        "field__in",
                        ("gender", "orientation", "looking_for", "relationship_status"),
                    )
                ),
                name="preference_set_field",
            ),
        ),
        migrations.AddConstraint(
            model_name="preferencesetentry",
            constraint=models.CheckConstraint(
                condition=models.Q(("value_id", "not-stated"), _negated=True),
                name="preference_set_not_stated",
            ),
        ),
        migrations.AddIndex(
            model_name="profilefieldchoice",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["value_ids"], name="profile_field_values"
            ),
        ),
        migrations.AddConstraint(
            model_name="profilefieldchoice",
            constraint=models.CheckConstraint(
                condition=models.Q(("version__gte", 1)),
                name="glow_persistence_profilefieldchoice_version",
            ),
        ),
        migrations.AddConstraint(
            model_name="profilefieldchoice",
            constraint=models.UniqueConstraint(
                fields=("account", "field"), name="profile_field_choice"
            ),
        ),
        migrations.AddConstraint(
            model_name="profilefieldchoice",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    (
                        "field__in",
                        ("gender", "orientation", "looking_for", "relationship_status"),
                    )
                ),
                name="profile_field_name",
            ),
        ),
        migrations.AddConstraint(
            model_name="profilefieldchoice",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("own_words__isnull", True),
                    ("field__in", ["gender", "orientation"]),
                    _connector="OR",
                ),
                name="profile_field_own_words",
            ),
        ),
        migrations.AddConstraint(
            model_name="profilefieldchoice",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("field", "looking_for"), _negated=True),
                    ("shown", True),
                    _connector="OR",
                ),
                name="profile_field_shown",
            ),
        ),
        migrations.AddConstraint(
            model_name="profilefieldchoice",
            constraint=models.CheckConstraint(
                condition=models.Q(("setting_version__gte", 1)),
                name="profile_field_setting_version",
            ),
        ),
    ]
