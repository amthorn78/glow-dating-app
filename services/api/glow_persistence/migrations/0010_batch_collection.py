# SV3 Stage A (its brief's D7): a recommendation batch's collection, and one batch per viewer and
# collection. Written in the form Django generates for an added non-null field on a table with no
# row in any database (the disposable proofs only): the one-off default fills existing rows, of
# which there are none, and is not kept on the model (preserve_default=False).

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("glow_persistence", "0009_media_policy_seed"),
    ]

    operations = [
        migrations.AddField(
            model_name="recommendationbatch",
            name="collection",
            field=models.CharField(
                choices=[("recommendations", "recommendations"), ("discovery", "discovery")],
                default="discovery",
                max_length=16,
            ),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name="recommendationbatch",
            constraint=models.CheckConstraint(
                condition=models.Q(("collection__in", ("recommendations", "discovery"))),
                name="batch_collection",
            ),
        ),
        migrations.AddConstraint(
            model_name="recommendationbatch",
            constraint=models.UniqueConstraint(
                fields=("account", "collection"), name="batch_one_per_collection"
            ),
        ),
    ]
