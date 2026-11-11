"""SV2 Stage B (its brief's D2 and D10; OD-62; DM-57 U10): the media policy's version 1.

One ``SettingVersion`` row for ``media.policy``, its ``PolicyRevision`` pointer and a ``StaffAudit``
row, each with the staff subject ``system:launch-default`` and the reason ``development-media-1``,
whose values it holds: PNG only, 1 MiB, 2,048 x 2,048, 4,194,304 declared pixels, four live photos,
a 60-second grant and three transfer attempts. Migration 0007's seed never changes after it is
applied, so the media policy is seeded here. The content is a literal copy of
``glow_domain.profile_settings.LAUNCH_DEFAULTS["media.policy"]``; a test holds the two equal, so
this seed never changes after it is applied either. No outbox event is written: nothing has been
published yet. The time is the database clock's.
"""

import uuid

from django.db import migrations

LAUNCH_SUBJECT = "system:launch-default"
NAME = "media.policy"
REASON = "development-media-1"
SEED = {
    "types": ["image/png"],
    "max_bytes": 1048576,
    "max_width": 2048,
    "max_height": 2048,
    "max_pixels": 4194304,
    "live_photos": 4,
    "grant_seconds": 60,
    "transfer_attempts": 3,
}


def seed_media_policy(apps, schema_editor):
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


def remove_media_policy(apps, schema_editor):
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
        ("glow_persistence", "0008_media_lifecycle"),
    ]

    operations = [
        migrations.RunPython(seed_media_policy, remove_media_policy),
    ]
