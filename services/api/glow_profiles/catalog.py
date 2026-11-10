"""The member's current catalog (the SV2 brief's D2, D3 and D11): the four lists, which may be
narrowed, the age range's default and direction, the location's ways and distance choices, read
under their pointers' locks. Its version is the version numbers of the settings it is built from
(``glow_domain.profile_settings.catalog_version``); a command built from an older catalog is
``stale_version``."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from glow_domain import profile_fields as pf
from glow_domain import profile_settings as ps
from glow_profiles import settings_store
from glow_profiles.settings_store import Setting
from glow_profiles.tx import Tx


@dataclass(frozen=True)
class Catalog:
    settings: dict[str, Setting]
    version: str
    lists: dict[str, pf.FieldList]

    @property
    def age_range(self) -> dict[str, Any]:
        return self.settings[ps.AGE_RANGE].content

    @property
    def location(self) -> dict[str, Any]:
        return self.settings[ps.LOCATION].content


def build(settings: dict[str, Setting]) -> Catalog:
    narrowing = settings[ps.NARROWING].content
    lists = {
        field: ps.field_list(field, settings[name].content, narrowing, settings[name].number)
        for field, name in ps.LIST_SETTINGS.items()
    }
    version = ps.catalog_version({name: settings[name].number for name in ps.CATALOG_SETTINGS})
    return Catalog(settings, version, lists)


def load(tx: Tx) -> Catalog:
    """The catalog, every pointer it reads locked ``FOR SHARE`` (after the account row lock)."""
    return build(settings_store.read_shared(tx, ps.CATALOG_SETTINGS))


def distance_ids(location: dict[str, Any]) -> list[str]:
    return [choice["id"] for choice in location["distance_choices"]]
