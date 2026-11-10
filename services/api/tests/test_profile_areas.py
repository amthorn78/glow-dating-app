"""SV2 Stage A, D5: the committed area table and the nearest-area computation (pure; the proof
loads the table by migration on PostgreSQL and runs the query through its route)."""

import hashlib
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any

from glow_profiles import areas_source

API_ROOT = Path(__file__).resolve().parents[1]
AREA_MIGRATION = API_ROOT / "glow_persistence" / "migrations" / "0006_area_table.py"


def area_migration() -> Any:
    spec = importlib.util.spec_from_file_location("area_0006", AREA_MIGRATION)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def points() -> list[Any]:
    # areas.py imports the model registry, so the computation is reached through its functions
    # on plain points built from the committed file.
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class Point:
        area_id: str
        name: str
        latitude: float
        longitude: float

    return [
        Point(area.area_id, area.name, float(area.latitude), float(area.longitude))
        for area in areas_source.read_derived(areas_source.DERIVED_FILE.read_bytes())
    ]


class AreaTableTests(unittest.TestCase):
    def test_the_committed_file_matches_its_pinned_hash_and_holds_925_areas(self) -> None:
        data = areas_source.DERIVED_FILE.read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), areas_source.DERIVED_SHA256)
        self.assertEqual(
            areas_source.DERIVED_SHA256,
            "2bf5e4da9e9904931cae26e900b75617e4b4a529f14f96a262883f6381e31138",
        )
        areas = areas_source.read_derived(data)
        self.assertEqual(len(areas), 925)
        self.assertEqual(len({area.area_id for area in areas}), 925)
        self.assertEqual(data.count(b"\n"), 926)

    def test_the_sources_hashes_are_d5s(self) -> None:
        self.assertEqual(
            areas_source.SOURCE_ZIP_SHA256,
            "0ec21c5d83982467903f1500fbbae87311edc81f09bed8ec1bbded80bce7eec3",
        )
        self.assertEqual(
            areas_source.SOURCE_TXT_SHA256,
            "31b285827a72b9f7917b312d458d01e2efe2909e4c5cb7b4b760b6bb0725f787",
        )

    def test_puerto_rico_is_not_in_the_table_and_multi_state_areas_are(self) -> None:
        areas = areas_source.read_derived(areas_source.DERIVED_FILE.read_bytes())
        states = [areas_source._states(area.name) for area in areas]
        self.assertFalse(any("PR" in found for found in states))
        self.assertEqual(sum(1 for found in states if len(found) > 1), 59)

    def test_the_migration_pins_the_same_hash_and_reads_nothing_remote(self) -> None:
        migration = area_migration()
        self.assertEqual(migration.AREA_FILE_SHA256, areas_source.DERIVED_SHA256)
        self.assertEqual(migration.AREA_FILE.resolve(), areas_source.DERIVED_FILE.resolve())
        rows = migration.area_rows(areas_source.DERIVED_FILE.read_bytes())
        self.assertEqual(len(rows), 925)
        source = AREA_MIGRATION.read_text(encoding="utf-8") + Path(areas_source.__file__).read_text(
            encoding="utf-8"
        )
        for word in ("urllib", "requests", "http.client", "socket", "urlopen"):
            self.assertNotIn(word, source)

    def test_a_changed_table_or_source_is_refused(self) -> None:
        data = areas_source.DERIVED_FILE.read_bytes()
        migration = area_migration()
        with self.assertRaises(migration.AreaTableRefused):
            migration.area_rows(data.replace(b"Abilene", b"Abilena"))
        with self.assertRaises(areas_source.SourceRefused):
            areas_source.read_derived(data[:-1])
        with self.assertRaises(areas_source.SourceRefused):
            areas_source.parse_source(b"GEOID\tNAME\n")

    def test_the_step_runs_in_isolated_mode_with_the_standard_library(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-I",
                str(Path(areas_source.__file__)),
                "verify",
                str(areas_source.DERIVED_FILE),
            ],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
            cwd="/",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("verified 925 areas", result.stdout)
        self.assertIn(areas_source.DERIVED_SHA256, result.stdout)


class NearestAreaTests(unittest.TestCase):
    def test_a_point_maps_to_the_nearest_internal_point(self) -> None:
        from glow_profiles import areas

        table = points()
        self.assertEqual(areas.nearest(40.7123457, -74.0067891, table).area_id, "35620")
        self.assertEqual(areas.nearest(34.0522342, -118.2436849, table).area_id, "31080")
        # A point far from every area still maps to the nearest internal point (D5's coverage).
        self.assertIn(areas.nearest(25.0, -80.0, table).area_id, {a.area_id for a in table})

    def test_an_areas_own_point_is_itself_and_distance_is_symmetric(self) -> None:
        from glow_profiles import areas

        table = points()
        for area in table[:50]:
            self.assertEqual(
                areas.nearest(area.latitude, area.longitude, table).area_id, area.area_id
            )
        first, second = table[0], table[1]
        self.assertAlmostEqual(
            areas.miles_between(first, second), areas.miles_between(second, first)
        )
        self.assertEqual(areas.miles_between(first, first), 0.0)


if __name__ == "__main__":
    unittest.main()
