"""The area table and the phone-location query (the SV2 brief's D5; DM-52).

The phone's approximate location is a **query**: the server maps it to the nearest area's
internal point and returns that area, changing nothing; the member then sets that area, or
another, by its ID. The coordinates exist only in this request's memory: they are never stored,
logged, returned, put in the outbox or in an idempotency record (the query writes none), and they
never appear in an error, a validation message or an exception's text. No distance is returned
either: the great-circle distances computed here are compared and dropped.

The internal points are the published ones, which every member in an area shares; a distance
choice (SV3's filter) is measured between them, so two members in one area are at distance zero.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

EARTH_RADIUS_MILES = 3958.7613


@dataclass(frozen=True)
class AreaPoint:
    area_id: str
    name: str
    latitude: float
    longitude: float


def points() -> list[AreaPoint]:
    """Every area of the table, in area ID order (read from the database, which the data migration
    loaded from the committed file)."""
    from glow_persistence.models import Area

    return [
        AreaPoint(area_id, name, float(latitude), float(longitude))
        for area_id, name, latitude, longitude in Area.objects.order_by("area_id").values_list(
            "area_id", "name", "latitude", "longitude"
        )
    ]


def _central_angle(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = phi2 - phi1
    d_lambda = math.radians(lon2 - lon1)
    h = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * math.asin(min(1.0, math.sqrt(h)))


def nearest(latitude: float, longitude: float, candidates: list[Any]) -> Any:
    """The area whose internal point is nearest to the given point, the lowest area ID on a tie.
    Nothing here is logged or kept, and the distance is not returned."""
    if not candidates:
        raise LookupError("no area")
    return min(
        candidates,
        key=lambda area: (
            _central_angle(latitude, longitude, area.latitude, area.longitude),
            area.area_id,
        ),
    )


def miles_between(first: Any, second: Any) -> float:
    """The distance between two areas' internal points, for SV3's filter (D5). No route returns
    it."""
    return EARTH_RADIUS_MILES * _central_angle(
        first.latitude, first.longitude, second.latitude, second.longitude
    )
