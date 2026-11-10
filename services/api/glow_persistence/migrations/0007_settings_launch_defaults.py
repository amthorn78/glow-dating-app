"""SV2 (its brief's D2; OD-60; OD-61): every setting's launch default, as version 1.

One ``SettingVersion`` row per setting, its ``PolicyRevision`` pointer, and a ``StaffAudit`` row,
each with the staff subject ``system:launch-default`` and the reason ``OD-60``, or for D18's
setting ``OD-61``, the register row that records Nathan's answers of 10 November 2026. The content
is a literal copy of ``glow_domain.profile_settings.LAUNCH_DEFAULTS``; a test holds the two equal,
so the seed never changes after it is applied. No outbox event is written: nothing has been
published yet. The time is the database clock's.
"""

import uuid

from django.db import migrations

LAUNCH_SUBJECT = "system:launch-default"
SEED = {
    "profile.gender": {
        "matching": "list_values",
        "pick_limit": 1,
        "values": [
            {"id": "woman", "label": "Woman", "retired": False},
            {"id": "man", "label": "Man", "retired": False},
            {"id": "non-binary", "label": "Non-binary", "retired": False},
        ],
    },
    "profile.orientation": {"matching": "list_values", "pick_limit": 1, "values": []},
    "profile.looking_for": {
        "matching": "list_values",
        "pick_limit": None,
        "values": [
            {"id": "long-term", "label": "A long-term relationship", "retired": False},
            {"id": "short-term", "label": "Something short-term", "retired": False},
            {"id": "casual", "label": "Something casual", "retired": False},
            {"id": "new-friends", "label": "New friends", "retired": False},
            {"id": "figuring-it-out", "label": "Still figuring it out", "retired": False},
        ],
    },
    "profile.relationship_status": {
        "matching": "list_values",
        "pick_limit": 1,
        "values": [
            {"id": "single", "label": "Single", "retired": False},
            {"id": "separated-or-divorcing", "label": "Separated or divorcing", "retired": False},
            {
                "id": "partnered-open-or-non-monogamous",
                "label": "Partnered, in an open or non-monogamous relationship",
                "retired": False,
            },
        ],
    },
    "profile.narrowing": {
        "narrowable": {
            "gender": True,
            "orientation": True,
            "looking_for": True,
            "relationship_status": True,
        },
        "show_me_shown": False,
        "not_stated_seen_by": "keep_all",
    },
    "profile.age_range": {"default_minimum": 18, "default_maximum": None, "direction": "both_ways"},
    "profile.location": {
        "chosen_area": True,
        "approximate_location": True,
        "distance_choices": [{"id": "anywhere", "label": "Anywhere", "miles": None}],
        "default_distance": "anywhere",
        "store_coordinates": False,
        "show_distance": False,
    },
    "discovery.resurfacing": {"enabled": False, "waiting_days": None},
    "discovery.undo": {"enabled": False, "waiting_days": None},
    "discovery.rematch": {
        "enabled": False,
        "waiting_days": None,
        "after_block": False,
        "after_report": False,
    },
    "chat.history": {
        "own_pause": "read_only",
        "other_pause": "read_only",
        "restriction": "read_only",
        "suspension": "read_only",
        "withdrawn_consent": "read_only",
        "unmatch": "hidden",
        "block": "hidden",
        "deletion": "as_unmatch",
        "consent_policy_version": "consent.onboarding.v1",
    },
    "identity.staff_approval": {"enabled": False, "stands_in_for": ["identity_verification"]},
    "consent.onboarding": {
        "development": True,
        "text": "Development text, not Glow's final wording (P08 writes it). "
        "Glow uses what you tell it to suggest people to you and you "
        "to them. Your gender, together with the genders you choose to "
        "see, can reveal your sexual orientation. If messaging with a "
        "match stops because one of you pauses, a profile is "
        "restricted or suspended, or a consent is withdrawn, the "
        "conversation stays readable to both of you, but no new "
        "message can be sent; an unmatch or a block hides it, and a "
        "deleted account works as an unmatch. You can withdraw this "
        "consent at any time, and your profile then stops being "
        "shown.",
    },
    "consent.sensitive_profile": {
        "development": True,
        "text": "Development text, not Glow's final wording (P08 writes "
        "it). With this consent you may add your sexual "
        "orientation, your own words for it and your "
        "relationship status, and narrow whom you see by "
        "orientation or relationship status. Glow uses them "
        "only to match people both ways, and shows them only if "
        "you choose. Anyone who narrows whom they see by one of "
        "these fields learns it about everyone they are shown, "
        "even members who do not show it. You can withdraw this "
        "consent at any time: Glow then removes these values, "
        "your own words and your narrowed choices for them, and "
        "you appear as not stated, to people who see everyone.",
    },
}
REASONS = {
    "profile.gender": "OD-60",
    "profile.orientation": "OD-60",
    "profile.looking_for": "OD-60",
    "profile.relationship_status": "OD-60",
    "profile.narrowing": "OD-60",
    "profile.age_range": "OD-60",
    "profile.location": "OD-60",
    "discovery.resurfacing": "OD-60",
    "discovery.undo": "OD-60",
    "discovery.rematch": "OD-60",
    "chat.history": "OD-60",
    "identity.staff_approval": "OD-61",
    "consent.onboarding": "OD-60",
    "consent.sensitive_profile": "OD-60",
}


def seed_launch_defaults(apps, schema_editor):
    alias = schema_editor.connection.alias
    setting_version = apps.get_model("glow_persistence", "SettingVersion")
    policy_revision = apps.get_model("glow_persistence", "PolicyRevision")
    staff_audit = apps.get_model("glow_persistence", "StaffAudit")
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SELECT clock_timestamp()")
        now = cursor.fetchone()[0]
    for name, content in SEED.items():
        row = setting_version.objects.using(alias).create(
            name=name,
            number=1,
            content=content,
            published_at=now,
            staff_subject=LAUNCH_SUBJECT,
            reason=REASONS[name],
        )
        policy_revision.objects.using(alias).create(
            name=name, policy_version=f"{name}.v1", artifact_ref=row.id
        )
        staff_audit.objects.using(alias).create(
            staff_subject=LAUNCH_SUBJECT,
            scope="settings",
            action="seed_launch_default",
            object_type="setting_version",
            object_id=row.id,
            reason_code=REASONS[name],
            request_id=uuid.uuid4(),
            before_version=None,
            after_version=1,
        )


def remove_launch_defaults(apps, schema_editor):
    alias = schema_editor.connection.alias
    names = list(SEED)
    rows = apps.get_model("glow_persistence", "SettingVersion").objects.using(alias)
    ids = list(rows.filter(name__in=names, number=1).values_list("id", flat=True))
    apps.get_model("glow_persistence", "StaffAudit").objects.using(alias).filter(
        object_id__in=ids, action="seed_launch_default"
    ).delete()
    apps.get_model("glow_persistence", "PolicyRevision").objects.using(alias).filter(
        name__in=names
    ).delete()
    rows.filter(id__in=ids).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("glow_persistence", "0006_area_table"),
    ]

    operations = [
        migrations.RunPython(seed_launch_defaults, remove_launch_defaults),
    ]
