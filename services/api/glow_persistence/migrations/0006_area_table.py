"""SV2 (its brief's D5): the area table's data.

The 925 core-based statistical areas of the committed table (``glow_profiles/data/
cbsa_areas_2024.tsv``, derived by ``glow_profiles/areas_source.py`` from the Census Bureau's 2024
Gazetteer file), loaded after the file's SHA-256 is checked against the pinned one. Nothing is
fetched: a file that differs, or that does not hold 925 areas, stops the migration before any row
is written.
"""

import hashlib
from decimal import Decimal
from pathlib import Path

from django.db import migrations

AREA_FILE = Path(__file__).resolve().parents[2] / "glow_profiles" / "data" / "cbsa_areas_2024.tsv"
AREA_FILE_SHA256 = "2bf5e4da9e9904931cae26e900b75617e4b4a529f14f96a262883f6381e31138"
AREA_COUNT = 925
HEADER = "area_id\tname\tlatitude\tlongitude"


class AreaTableRefused(RuntimeError):
    """The committed area table is not the pinned one; nothing was loaded."""


def area_rows(data: bytes) -> list[list[str]]:
    if hashlib.sha256(data).hexdigest() != AREA_FILE_SHA256:
        raise AreaTableRefused("the area table's SHA-256 is not the pinned one")
    lines = data.decode("utf-8").split("\n")
    if lines[0] != HEADER or lines[-1] != "":
        raise AreaTableRefused("the area table's header or ending is not the expected one")
    rows = [line.split("\t") for line in lines[1:-1]]
    if len(rows) != AREA_COUNT or any(len(row) != 4 for row in rows):
        raise AreaTableRefused("the area table does not hold 925 areas of four columns")
    return rows


def load_areas(apps, schema_editor):
    rows = area_rows(AREA_FILE.read_bytes())
    area = apps.get_model("glow_persistence", "Area")
    area.objects.using(schema_editor.connection.alias).bulk_create(
        [
            area(area_id=row[0], name=row[1], latitude=Decimal(row[2]), longitude=Decimal(row[3]))
            for row in rows
        ]
    )


def unload_areas(apps, schema_editor):
    area = apps.get_model("glow_persistence", "Area")
    area.objects.using(schema_editor.connection.alias).all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("glow_persistence", "0005_profiles_settings"),
    ]

    operations = [
        migrations.RunPython(load_areas, unload_areas),
    ]
