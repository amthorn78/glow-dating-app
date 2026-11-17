# SV3 Stage B (its brief's D9 and D12): a directional interaction's ``withdrawn`` state (undo keeps
# the row and advances its version, never deleting and creating it again), its ``decided_at``
# (the transaction's clock at its last like, pass or undo, which resurfacing's and undo's waiting
# periods count from; the field's default, the application's clock, fills a row written otherwise,
# as the proofs' seeded rows are), and the idempotency record's ``withdrawn`` receipt code. Written
# in the form Django generates.

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("glow_persistence", "0010_batch_collection"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="directionalinteraction",
            name="glow_persistence_directionalinteraction_state",
        ),
        migrations.RemoveConstraint(
            model_name="idempotencyrecord",
            name="intent_result",
        ),
        migrations.AddField(
            model_name="directionalinteraction",
            name="decided_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name="directionalinteraction",
            name="state",
            field=models.CharField(
                choices=[("liked", "liked"), ("passed", "passed"), ("withdrawn", "withdrawn")],
                max_length=16,
            ),
        ),
        migrations.AlterField(
            model_name="idempotencyrecord",
            name="outcome_code",
            field=models.CharField(
                blank=True,
                choices=[
                    ("committed", "committed"),
                    ("liked", "liked"),
                    ("passed", "passed"),
                    ("unmatched", "unmatched"),
                    ("blocked", "blocked"),
                    ("unblocked", "unblocked"),
                    ("withdrawn", "withdrawn"),
                ],
                max_length=16,
                null=True,
            ),
        ),
        migrations.AddConstraint(
            model_name="directionalinteraction",
            constraint=models.CheckConstraint(
                condition=models.Q(("state__in", ("liked", "passed", "withdrawn"))),
                name="glow_persistence_directionalinteraction_state",
            ),
        ),
        migrations.AddConstraint(
            model_name="idempotencyrecord",
            constraint=models.CheckConstraint(
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
                                "withdrawn",
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
        ),
    ]
