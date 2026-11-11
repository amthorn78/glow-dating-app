"""What the selection reads, and SV3 Stage A's fixed rules (the SV3 brief's D3, D5 to D7 and D19).

- **The settings the selection reads** (``SELECTION_SETTINGS``), each pointer locked ``FOR SHARE``
  in the transaction's first ``read_shared`` call, in name order (D19): ``consent.onboarding`` (its
  current version is CONSENT's, D3), ``discovery.resurfacing`` (D7's consumption: Stage A builds no
  resurfacing, so a pass excludes for good, as with the setting off at launch; Stage B applies its
  content), ``profile.age_range`` (the direction, D4), ``profile.location`` (the distance choices,
  D5) and ``profile.narrowing`` (a field members may not narrow reads as keeping all, D4).
- **The batch's policy version** (Q3) is their version numbers, in that order: a publication of any
  of them changes it, so every batch built under the earlier version is stale.
- **The accepted age states** (D3, ADULT) are code, not a setting: ``self_declared_adult`` only.
  P09.2 adds the store-signal states here (and to SV2's completion, Q18).
- **The bounds** (D7): at most 100 candidates per batch, 50 per page, and a batch's lifetime of 30
  minutes (a code constant, DM-60 item 6).
- **The compatibility port** (D6): only the fixture adapter, and only where the settings module
  selects it (``GLOW_DISCOVERY_COMPATIBILITY_FIXTURE``, the proof's discovery settings alone). The
  served runtime selects none; the app's boot refuses a fixture provider outside development and
  test (PF01 section 5).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from glow_domain import profile_fields as pf
from glow_domain import profile_settings as ps
from glow_domain.compatibility import (
    CompatibilityStatus,
    FixtureCase,
    FixtureCompatibilityProvider,
    FixtureCompatibilityResult,
    FixtureProvenance,
)

# D3 (ADULT; G-01; the recheck record): the accepted age states. Code, not a setting.
ACCEPTED_AGE_STATES: tuple[str, ...] = ("self_declared_adult",)

# D7 (Q3) and D19: the settings the selection reads, in name order.
SELECTION_SETTINGS: tuple[str, ...] = (
    ps.ONBOARDING_CONSENT,
    ps.RESURFACING,
    ps.AGE_RANGE,
    ps.LOCATION,
    ps.NARROWING,
)
assert list(SELECTION_SETTINGS) == sorted(SELECTION_SETTINGS)

RECOMMENDATIONS = "recommendations"
DISCOVERY = "discovery"
COLLECTIONS: tuple[str, ...] = (RECOMMENDATIONS, DISCOVERY)

# D7: the bounds.
BATCH_LIMIT = 100
PAGE_MAX = 50
BATCH_LIFETIME = timedelta(minutes=30)

# D6: the port's selection, read from the settings module at each page.
FIXTURE_SETTING = "GLOW_DISCOVERY_COMPATIBILITY_FIXTURE"
ENVIRONMENT_SETTING = "GLOW_DISCOVERY_ENVIRONMENT"
FIXTURE_ENVIRONMENTS = frozenset({"development", "test"})
PROVENANCE = FixtureProvenance(
    fixture_set_version="sv3-discovery-fixture-1",
    adapter_version="fixture:sv3-discovery",
    simulated_engine_version="fixture:no-engine",
    simulated_engine_contract_version="fixture:no-contract",
)


def policy_version(numbers: Mapping[str, int]) -> str:
    """The batch's policy version (Q3): the selection's settings' version numbers, in order."""
    return "discovery." + ".".join(str(int(numbers[name])) for name in SELECTION_SETTINGS)


@dataclass(frozen=True)
class Selection:
    """The policy one transaction's selection applies, read from its settings as locked, with the
    server's UTC date (D4) read after the locks."""

    version: str
    onboarding_consent: str
    narrowable: Mapping[str, bool]
    both_ways: bool
    # D5: each distance choice the location setting offers, and its miles (None: anywhere).
    distance_miles: Mapping[str, int | None]
    today: date


def selection(settings: Mapping[str, Any], today: date) -> Selection:
    """The ``Selection`` from the ``settings_store.Setting`` of each of ``SELECTION_SETTINGS``."""
    narrowing = settings[ps.NARROWING].content["narrowable"]
    location = settings[ps.LOCATION].content
    return Selection(
        version=policy_version({name: settings[name].number for name in SELECTION_SETTINGS}),
        onboarding_consent=str(settings[ps.ONBOARDING_CONSENT].policy_version),
        narrowable={field: narrowing.get(field) is True for field in pf.FIELDS},
        both_ways=settings[ps.AGE_RANGE].content["direction"] == "both_ways",
        distance_miles={
            str(choice["id"]): (None if choice["miles"] is None else int(choice["miles"]))
            for choice in location["distance_choices"]
        },
        today=today,
    )


# -- the compatibility port (D6) ------------------------------------------------------------


def require_fixture_environment() -> None:
    """The boot's refusal (PF01 section 5): a fixture provider outside development and test."""
    from django.conf import settings
    from django.core.exceptions import ImproperlyConfigured

    if getattr(settings, FIXTURE_SETTING, None) is None:
        return
    if getattr(settings, ENVIRONMENT_SETTING, None) not in FIXTURE_ENVIRONMENTS:
        raise ImproperlyConfigured("fixture_compatibility_refused")


def compatibility_port() -> FixtureCompatibilityProvider | None:
    """The port the settings module selects: the fixture adapter with its configured case, or
    none (the served runtime's, and any settings module's that names none)."""
    from django.conf import settings

    case = getattr(settings, FIXTURE_SETTING, None)
    if case is None:
        return None
    environment = str(getattr(settings, ENVIRONMENT_SETTING, ""))
    return FixtureCompatibilityProvider(environment, FixtureCase(case), PROVENANCE)


# The port's permitted output is a band, never a score (PF01 section 5). The fixture's result
# carries none of its own, so every ready pair is in one band and the keyed tie-break orders it.
FIXTURE_BAND = 0


def band(result: FixtureCompatibilityResult) -> int | None:
    """A ready pair's band, or ``None`` for a pair the port does not rank."""
    if result.status is CompatibilityStatus.READY:
        return FIXTURE_BAND
    return None
