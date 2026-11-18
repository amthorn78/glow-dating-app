"""SV2-R (its brief's R2; OD-68; DM-84 section 5): the photo check's toggle, version 1.

One ``SettingVersion`` row for ``media.photo_check``, its ``PolicyRevision`` pointer and a
``StaffAudit`` row, each with the staff subject ``system:launch-default`` and the reason ``OD-68``,
the register row of Nathan's direction: the automated photo check is off at launch. Migrations
0007's and 0009's seeds never change after they are applied, so the toggle is seeded here, as 0009
seeds the media policy. The content is a literal copy of
``glow_domain.profile_settings.LAUNCH_DEFAULTS["media.photo_check"]``; a test holds the two equal,
so this seed never changes after it is applied either. No outbox event is written: nothing has
been published yet. The time is the database clock's.
"""

import uuid

from django.db import migrations

LAUNCH_SUBJECT = "system:launch-default"
NAME = "media.photo_check"
REASON = "OD-68"
SEED = {"enabled": False}


def seed_photo_check(apps, schema_editor):
    alias = schema_editor.connection.alias
    setting_version = apps.get_model("glow_persistence", "SettingVersion")
    policy_revision = apps.get_model("glow_persistence", "PolicyRevision")
    staff_audit = apps.get_model("glow_persistence", "StaffAudit")
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SELECT clock_timestamp()")
        now = cursor.fetchone()[0]
    row = setting_version.objects.using(alias).create(
        name=NAME,
        number=1,
        content=SEED,
        published_at=now,
        staff_subject=LAUNCH_SUBJECT,
        reason=REASON,
    )
    policy_revision.objects.using(alias).create(
        name=NAME, policy_version=f"{NAME}.v1", artifact_ref=row.id
    )
    staff_audit.objects.using(alias).create(
        staff_subject=LAUNCH_SUBJECT,
        scope="settings",
        action="seed_launch_default",
        object_type="setting_version",
        object_id=row.id,
        reason_code=REASON,
        request_id=uuid.uuid4(),
        before_version=None,
        after_version=1,
    )


def remove_photo_check(apps, schema_editor):
    alias = schema_editor.connection.alias
    rows = apps.get_model("glow_persistence", "SettingVersion").objects.using(alias)
    ids = list(rows.filter(name=NAME, number=1).values_list("id", flat=True))
    apps.get_model("glow_persistence", "StaffAudit").objects.using(alias).filter(
        object_id__in=ids, action="seed_launch_default"
    ).delete()
    apps.get_model("glow_persistence", "PolicyRevision").objects.using(alias).filter(
        name=NAME
    ).delete()
    rows.filter(id__in=ids).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("glow_persistence", "0011_interaction_undo"),
    ]

    operations = [
        migrations.RunPython(seed_photo_check, remove_photo_check),
    ]
