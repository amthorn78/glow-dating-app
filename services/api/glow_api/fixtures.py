"""Synthetic presentation data, with no eligibility or Human Design claim."""

from dataclasses import dataclass
from typing import Literal, TypedDict


class Compatibility(TypedDict):
    status: Literal["pending"]
    source: Literal["fixture"]


class Recommendation(TypedDict):
    profile_id: str
    display_name: str
    age: int
    summary: str
    compatibility: Compatibility


class RecommendationEnvelope(TypedDict):
    mode: Literal["fixture"]
    contract_version: Literal["gapp-dev-v1"]
    items: list[Recommendation]


@dataclass(frozen=True)
class FixturePerson:
    profile_id: str
    display_name: str
    age: int
    summary: str


_PEOPLE = (
    FixturePerson(
        "fixture-alex", "Alex (demo)", 32, "Synthetic profile for testing the app layout."
    ),
    FixturePerson(
        "fixture-robin", "Robin (demo)", 35, "Synthetic profile for testing list navigation."
    ),
)


def recommendations() -> RecommendationEnvelope:
    """Return new collections on every call so caller mutation cannot leak state."""
    items: list[Recommendation] = []
    for person in _PEOPLE:
        items.append(
            Recommendation(
                profile_id=person.profile_id,
                display_name=person.display_name,
                age=person.age,
                summary=person.summary,
                compatibility={"status": "pending", "source": "fixture"},
            )
        )
    return {"mode": "fixture", "contract_version": "gapp-dev-v1", "items": items}
