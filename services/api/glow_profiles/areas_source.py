"""The area table's recorded, deterministic derivation (the SV2 brief's D5; DM-52).

**The source** is the US Census Bureau's 2024 Gazetteer file for core-based statistical areas
(metro and micro areas), a work of the US government in the public domain:

- ``https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/2024_Gaz_cbsa_national.zip``,
  46,177 bytes, last modified 30 August 2024, SHA-256 ``SOURCE_ZIP_SHA256``;
- its one member, ``2024_Gaz_cbsa_national.txt``, 188,130 bytes, SHA-256 ``SOURCE_TXT_SHA256``:
  tab-separated, UTF-8, a header and 935 areas (393 metro, 542 micro), each with ``GEOID``,
  ``NAME`` and an internal point (``INTPTLAT``, ``INTPTLONG``).

**The step** keeps, for every area outside Puerto Rico, its ``GEOID`` as the stable area ID, its
``NAME`` and its internal point exactly as published (the decimal text, not a float), and drops
the 10 areas whose name gives Puerto Rico (``PR``) as their state: OD-55's launch is "the US,
all states", and adding Puerto Rico is Nathan's launch-geography decision. The result is 925
areas, sorted by area ID, written as tab-separated UTF-8 with a header and LF line endings, its
SHA-256 ``DERIVED_SHA256``. The step refuses a source whose hash differs.

**What the table means** (D5, in plain words): a county in no metro or micro area is in no
area, so a member there picks the nearest area, or the phone's location maps to the nearest
internal point, which can be far away. One area can be very large, and two members in one area
are at distance zero, so a distance choice means "areas whose internal points are within this
distance", not a distance between people. 59 areas span two or more states, so an area does not
give a member's state.

Nothing is fetched at migration, test or run time: the committed file is the table, and the data
migration (``glow_persistence/migrations/0006_area_table.py``) checks its hash before it loads
it. This module uses the standard library only, so the step runs in isolated mode::

    python3 -I services/api/glow_profiles/areas_source.py derive <2024_Gaz_cbsa_national.txt> <out>
    python3 -I services/api/glow_profiles/areas_source.py verify <derived file>
"""

from __future__ import annotations

import hashlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path

SOURCE_URL = (
    "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/"
    "2024_Gaz_cbsa_national.zip"
)
SOURCE_ZIP_SHA256 = "0ec21c5d83982467903f1500fbbae87311edc81f09bed8ec1bbded80bce7eec3"
SOURCE_TXT_SHA256 = "31b285827a72b9f7917b312d458d01e2efe2909e4c5cb7b4b760b6bb0725f787"
SOURCE_HEADER = (
    "CSAFP",
    "GEOID",
    "NAME",
    "CBSA_TYPE",
    "ALAND",
    "AWATER",
    "ALAND_SQMI",
    "AWATER_SQMI",
    "INTPTLAT",
    "INTPTLONG",
)
SOURCE_AREAS = 935
SOURCE_PUERTO_RICO = 10

DERIVED_HEADER = ("area_id", "name", "latitude", "longitude")
DERIVED_AREAS = 925
DERIVED_FILE = Path(__file__).resolve().parent / "data" / "cbsa_areas_2024.tsv"
DERIVED_SHA256 = "2bf5e4da9e9904931cae26e900b75617e4b4a529f14f96a262883f6381e31138"

AREA_ID = re.compile(r"[0-9]{5}")
# The published decimal text of a coordinate: an optional sign, digits, a point and decimals.
COORDINATE = re.compile(r"-?[0-9]{1,3}\.[0-9]{1,6}")
# "Abilene, TX Metro Area": the state codes sit between the last comma and the area's type.
NAME_STATES = re.compile(r", ([A-Z]{2}(?:-[A-Z]{2})*) (?:Metro|Micro) Area")
PUERTO_RICO = "PR"


class SourceRefused(Exception):
    """The input is not the pinned source, or does not hold what the step expects."""


@dataclass(frozen=True)
class Area:
    area_id: str
    name: str
    latitude: str
    longitude: str


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _states(name: str) -> tuple[str, ...]:
    found = NAME_STATES.fullmatch(name, pos=name.rfind(", ")) if ", " in name else None
    if found is None:
        raise SourceRefused("an area's name does not end in its states and type")
    return tuple(found.group(1).split("-"))


def parse_source(data: bytes) -> list[Area]:
    """Every area of the pinned source, with its text as published (whitespace stripped)."""
    if sha256(data) != SOURCE_TXT_SHA256:
        raise SourceRefused("the source's SHA-256 is not the pinned one")
    lines = data.decode("utf-8").split("\n")
    if lines[-1] != "":
        raise SourceRefused("the source does not end with a newline")
    header = tuple(column.strip() for column in lines[0].split("\t"))
    if header != SOURCE_HEADER:
        raise SourceRefused("the source's header is not the expected one")
    areas = []
    for line in lines[1:-1]:
        cells = [cell.strip() for cell in line.split("\t")]
        if len(cells) != len(SOURCE_HEADER):
            raise SourceRefused("a source row does not have ten columns")
        row = dict(zip(SOURCE_HEADER, cells, strict=True))
        area = Area(row["GEOID"], row["NAME"], row["INTPTLAT"], row["INTPTLONG"])
        _check(area)
        areas.append(area)
    if len(areas) != SOURCE_AREAS:
        raise SourceRefused("the source does not hold 935 areas")
    return areas


def _check(area: Area) -> None:
    if AREA_ID.fullmatch(area.area_id) is None:
        raise SourceRefused("an area ID is not five digits")
    if not area.name or len(area.name) > 80:
        raise SourceRefused("an area's name is empty or longer than 80 characters")
    _states(area.name)
    for value, bound in ((area.latitude, 90.0), (area.longitude, 180.0)):
        if COORDINATE.fullmatch(value) is None or not -bound <= float(value) <= bound:
            raise SourceRefused("an internal point is not a published decimal in range")


def derive(data: bytes) -> bytes:
    """The committed table from the pinned source: Puerto Rico's 10 areas dropped, 925 kept,
    sorted by area ID."""
    areas = parse_source(data)
    kept = [area for area in areas if _states(area.name) != (PUERTO_RICO,)]
    if any(PUERTO_RICO in _states(area.name) for area in kept):
        raise SourceRefused("an area spans Puerto Rico and a state; the step does not decide it")
    if len(areas) - len(kept) != SOURCE_PUERTO_RICO or len(kept) != DERIVED_AREAS:
        raise SourceRefused("the step did not drop exactly 10 areas and keep 925")
    if len({area.area_id for area in kept}) != len(kept):
        raise SourceRefused("an area ID repeats")
    rows = ["\t".join(DERIVED_HEADER)]
    for area in sorted(kept, key=lambda item: item.area_id):
        rows.append("\t".join((area.area_id, area.name, area.latitude, area.longitude)))
    return ("\n".join(rows) + "\n").encode("utf-8")


def read_derived(data: bytes) -> list[Area]:
    """The committed table, checked: its pinned hash, its header and its 925 areas."""
    if sha256(data) != DERIVED_SHA256:
        raise SourceRefused("the area table's SHA-256 is not the pinned one")
    lines = data.decode("utf-8").split("\n")
    if lines[-1] != "" or tuple(lines[0].split("\t")) != DERIVED_HEADER:
        raise SourceRefused("the area table's header or ending is not the expected one")
    areas = []
    for line in lines[1:-1]:
        cells = line.split("\t")
        if len(cells) != len(DERIVED_HEADER):
            raise SourceRefused("an area table row does not have four columns")
        area = Area(*cells)
        _check(area)
        areas.append(area)
    if len(areas) != DERIVED_AREAS or [a.area_id for a in areas] != sorted(
        {a.area_id for a in areas}
    ):
        raise SourceRefused("the area table does not hold 925 distinct areas in order")
    return areas


def main(argv: list[str]) -> int:
    if len(argv) == 3 and argv[0] == "derive":
        source, target = Path(argv[1]), Path(argv[2])
        derived = derive(source.read_bytes())
        with open(target, "xb") as handle:
            handle.write(derived)
        print(f"derived {DERIVED_AREAS} areas: {len(derived)} bytes, sha256 {sha256(derived)}")
        return 0
    if len(argv) == 2 and argv[0] == "verify":
        data = Path(argv[1]).read_bytes()
        areas = read_derived(data)
        print(f"verified {len(areas)} areas: {len(data)} bytes, sha256 {sha256(data)}")
        return 0
    print("usage: areas_source.py derive <source.txt> <out> | verify <derived file>")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
