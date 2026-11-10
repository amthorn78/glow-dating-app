"""The member's domain operations (the SV2 brief's D3 to D9, D11 and D17).

Each command is one transaction (``tx.run``) that:

1. locks the actor's account row ``FOR UPDATE`` first (DM-13 4.1), then the settings it reads,
   under their pointers' ``FOR SHARE`` locks, then its own rows ``FOR UPDATE``;
2. reads the time from ``clock_timestamp()`` after the locks;
3. authorizes, then deduplicates (P06.DB 5.4): the same key with the same intent replays its
   receipt with a current projection, and with another intent is ``idempotency_conflict``;
4. checks the expected version, then the request against the current settings, then writes, bumps
   the account's counters, emits its outbox events and stores its keyed idempotency record (D17).

``glow_chat``'s reviewed writers (onboarding consent's accept and withdraw; pause and resume) nest
inside as savepoints; any result of theirs but ``applied`` or ``no_change`` rolls the whole
transaction back (D6, D9). Completion and demotion are SV2's own writers of the profile state the
send check reads, in one place: every writer of a completion requirement ends with D9's shared
recompute (``recompute``; DM-54), so a profile becomes ``visible`` as soon as its last requirement
is met, whoever meets it. A removal the member or staff is entitled to make moves a ``visible``
profile to ``incomplete`` in the same transaction and is never refused; an edit that would leave a
required value empty is refused; a ``paused`` profile stays paused, and resume rechecks
completion (D9).

The member's data never leaves these functions but in the owner's own projections; nothing here
logs a value (a coordinate, a date or time, own words or a field's value).
"""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Any
from uuid import UUID

from django.conf import settings as django_settings
from django.db.models import F
from django.db.models.functions import Now

from glow_chat.contact import OrmContactPersistence
from glow_domain import profile_fields as pf
from glow_domain import profile_settings as ps
from glow_domain.chat import ONBOARDING_CONSENT_PURPOSE, ContactResult, TransactionProbe
from glow_domain.identity import (
    AccountId,
    AdultOutcome,
    AgeAssuranceState,
    AgeTransition,
    adult_outcome,
)
from glow_identity.age import AgeTransitionRefused, OrmAgeAssurance
from glow_persistence.models import (
    AccountAgeState,
    AppAccount,
    Area,
    BirthInput,
    ConsentDecision,
    EngineIdentity,
    IdempotencyRecord,
    Preferences,
    PreferenceSetEntry,
    Profile,
    ProfileFieldChoice,
)
from glow_profiles import (
    areas,
    contract,
    events,
    idempotency,
    recompute,
    requirements,
    settings_store,
)
from glow_profiles import catalog as catalogs
from glow_profiles.tx import (
    FORBIDDEN,
    INVALID_REQUEST,
    NOT_FOUND,
    STALE_VERSION,
    STATE_CONFLICT,
    Refused,
    Result,
    Tx,
    clock,
    lock_account,
    read_account_shared,
    run,
    signal,
    utc_date,
)

SENSITIVE_PURPOSE = "sensitive_profile"
EDITABLE = ("incomplete", "visible", "paused")
# D6: the operations whose stored records carry orientation, relationship status or their sets;
# the sensitive-fields consent's withdrawal deletes them.
SENSITIVE_OPERATIONS = (
    f"profile_field.{pf.ORIENTATION}",
    f"profile_field.{pf.RELATIONSHIP_STATUS}",
    "preferences",
)


def chat() -> OrmContactPersistence:
    """``glow_chat``'s reviewed writers; the provider's name is the identity fragment's."""
    return OrmContactPersistence(provider=django_settings.GLOW_IDENTITY_CHAT_PROVIDER)


def _chat_checked(result: ContactResult) -> ContactResult:
    """D6, D9: a nested writer's result other than ``applied`` or ``no_change`` is a refusal of
    the whole transaction."""
    if result.outcome in ("applied", "no_change"):
        return result
    if result.outcome == "refused":
        code = NOT_FOUND if result.reason.endswith("_missing") else STATE_CONFLICT
        raise Refused(code, f"chat:{result.reason}")
    raise Refused(STATE_CONFLICT, f"chat_{result.outcome}:{result.reason}")


def _bump_eligibility(account_id: UUID) -> None:
    AppAccount.objects.filter(pk=account_id).update(
        eligibility_version=F("eligibility_version") + 1, version=F("version") + 1, updated_at=Now()
    )


def _bump_preferences(account_id: UUID) -> None:
    AppAccount.objects.filter(pk=account_id).update(
        preferences_version=F("preferences_version") + 1, version=F("version") + 1, updated_at=Now()
    )


def _sensitive_accepted(account_id: UUID) -> bool:
    latest = requirements.latest_decision(account_id, SENSITIVE_PURPOSE)
    return latest is not None and latest.state == "accepted"


def _profile(account_id: UUID) -> Any:
    return Profile.objects.select_for_update().filter(account_id=account_id).first()


def _key(intent: dict[str, Any]) -> str:
    return str(intent["meta"]["idempotency_key"])


def _expected(intent: dict[str, Any]) -> int:
    return int(intent["meta"]["expected_version"])


# -- reads ------------------------------------------------------------------------------------


def _field_rows(account_id: UUID) -> dict[str, Any]:
    return {row.field: row for row in ProfileFieldChoice.objects.filter(account_id=account_id)}


def _sets(account_id: UUID) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for field, value_id in (
        PreferenceSetEntry.objects.filter(account_id=account_id)
        .order_by("field", "position")
        .values_list("field", "value_id")
    ):
        found.setdefault(field, []).append(value_id)
    return found


def _fields_projection(account_id: UUID, catalog: catalogs.Catalog) -> dict[str, Any]:
    return contract.own_profile_fields(_field_rows(account_id), catalog.lists, catalog.version)


def _onboarding_projection(account_id: UUID, profile: Any, current_label: str) -> dict[str, Any]:
    latest = requirements.latest_decision(account_id, ONBOARDING_CONSENT_PURPOSE)
    needed: list[str] = []
    age = AccountAgeState.objects.filter(account_id=account_id).first()
    if age is None or age.state != "self_declared_adult":
        needed.append("adult_policy")
    if not requirements.onboarding_current(account_id, current_label):
        needed.append("consent")
    if profile is None or profile.state != "visible":
        needed.append("profile")
    return contract.onboarding_eligibility(latest, needed)


def _birth_projection(row: Any, account_id: UUID) -> dict[str, Any]:
    mapping = EngineIdentity.objects.filter(account_id=account_id).first()
    return contract.own_birth_input(row, mapping)


def read(account_id: UUID, what: str, object_id: UUID | None = None) -> Result:
    """The owner's reads (D11, D17), in one transaction holding the account row ``FOR SHARE``,
    so each read waits for a writer in flight and reads its result. Another member's object, or
    none, is ``not_found``."""

    def body(tx: Tx) -> Result:
        read_account_shared(tx, account_id)
        profile = Profile.objects.filter(account_id=account_id).first()
        if what == "profile":
            if profile is None or (object_id is not None and profile.id != object_id):
                raise Refused(NOT_FOUND, "profile_missing")
            return Result("read", data=contract.own_profile(profile))
        if what == "completion":
            onboarding = settings_store.read_shared(tx, [ps.ONBOARDING_CONSENT])
            label = onboarding[ps.ONBOARDING_CONSENT].policy_version
            missing = requirements.missing(account_id, profile, label)
            return Result("read", data=contract.own_completion(profile, missing))
        if what in ("fields", "catalog"):
            catalog = catalogs.load(tx)
            if what == "fields":
                if profile is None:
                    raise Refused(NOT_FOUND, "profile_missing")
                return Result("read", data=_fields_projection(account_id, catalog))
            consents = settings_store.read_shared(tx, [ps.ONBOARDING_CONSENT, ps.SENSITIVE_CONSENT])
            return Result(
                "read",
                data=contract.profile_catalog(
                    catalog.version,
                    catalog.lists,
                    catalog.age_range,
                    catalog.location,
                    {
                        "onboarding": (
                            consents[ps.ONBOARDING_CONSENT].policy_version,
                            consents[ps.ONBOARDING_CONSENT].content["text"],
                        ),
                        "sensitive_profile": (
                            consents[ps.SENSITIVE_CONSENT].policy_version,
                            consents[ps.SENSITIVE_CONSENT].content["text"],
                        ),
                    },
                ),
            )
        if what in ("preferences", "filters"):
            preferences = Preferences.objects.filter(account_id=account_id).first()
            if profile is None or preferences is None:
                raise Refused(NOT_FOUND, "profile_missing")
            if what == "preferences":
                return Result("read", data=contract.own_preferences(preferences, _sets(account_id)))
            return Result("read", data=contract.own_filters(preferences))
        if what == "area":
            if profile is None:
                raise Refused(NOT_FOUND, "profile_missing")
            area = Area.objects.filter(pk=profile.area_id).first() if profile.area_id else None
            return Result("read", data=contract.own_area(profile, area))
        if what == "consent":
            onboarding = settings_store.read_shared(tx, [ps.ONBOARDING_CONSENT])
            label = onboarding[ps.ONBOARDING_CONSENT].policy_version
            return Result("read", data=_onboarding_projection(account_id, profile, label))
        if what == "sensitive_consent":
            latest = requirements.latest_decision(account_id, SENSITIVE_PURPOSE)
            return Result("read", data=contract.sensitive_consent(latest))
        if what == "age_state":
            age = AccountAgeState.objects.filter(account_id=account_id).first()
            if age is None:
                raise Refused(NOT_FOUND, "age_state_missing")
            return Result("read", data=contract.own_age_state(age))
        if what == "birth_input":
            rows = BirthInput.objects.filter(account_id=account_id)
            row = (
                rows.filter(pk=object_id).first()
                if object_id is not None
                else rows.order_by("-version").first()
            )
            if row is None:
                raise Refused(NOT_FOUND, "birth_input_missing")
            return Result("read", data=_birth_projection(row, account_id))
        raise Refused(NOT_FOUND, "unknown_read")

    return run(body)


# -- the profile (ProfileIntent): edit, completion and the cleared summary (D9) ---------------


def _create_preferences(account_id: UUID, catalog: catalogs.Catalog) -> None:
    if Preferences.objects.filter(account_id=account_id).exists():
        return
    age_range, location = catalog.age_range, catalog.location
    Preferences.objects.create(
        account_id=account_id,
        policy_version=catalog.version,
        minimum_age=age_range["default_minimum"],
        maximum_age=age_range["default_maximum"],
        distance_choice=location["default_distance"],
    )
    # D3: every "show me" set starts at all, the marker's own row.
    PreferenceSetEntry.objects.bulk_create(
        [
            PreferenceSetEntry(account_id=account_id, field=field, value_id=pf.ALL)
            for field in pf.FIELDS
        ]
    )
    _bump_preferences(account_id)


def save_profile(
    account_id: UUID, intent: dict[str, Any], *, probe: TransactionProbe | None = None
) -> Result:
    """F04's owner ``edit``: the display name and the summary. It ends with D9's recompute
    (``recompute``): with every requirement met, an ``incomplete`` profile becomes ``visible``
    (P04's reviewed table: "Remains incomplete unless all current requirements permit
    completion"); a cleared summary moves a ``visible`` profile to ``incomplete``; a ``paused``
    profile stays paused."""
    operation = "profile"
    digest = idempotency.digest(operation, intent)

    def body(tx: Tx) -> Result:
        lock_account(tx, account_id)
        found = settings_store.read_shared(tx, [*ps.CATALOG_SETTINGS, ps.ONBOARDING_CONSENT])
        catalog = catalogs.build({name: found[name] for name in ps.CATALOG_SETTINGS})
        profile = _profile(account_id)
        signal(tx.probe, "after_locks")
        now = clock(tx)
        record = idempotency.decide(account_id, operation, _key(intent), digest, now)
        if record is not idempotency.NEW:
            if profile is None:
                raise Refused(NOT_FOUND, "profile_missing")
            return Result("replayed", data=contract.own_profile(profile))
        if _expected(intent) != (0 if profile is None else int(profile.version)):
            raise Refused(STALE_VERSION, "stale_version")
        if profile is None:
            profile = Profile.objects.create(
                account_id=account_id,
                display_name=intent["display_name"],
                bio=intent["summary"],
                state="incomplete",
            )
            _create_preferences(account_id, catalog)
        else:
            if profile.state not in EDITABLE:
                raise Refused(STATE_CONFLICT, "profile_not_editable")
            profile.display_name = intent["display_name"]
            profile.bio = intent["summary"]
            profile.version += 1
        profile.save()
        _bump_eligibility(account_id)
        events.emit(
            tx,
            events.PROFILE_EDITED,
            aggregate_id=profile.id,
            aggregate_version=int(profile.version),
            payload_ref=profile.id,
            now=now,
        )
        # D9: the shared recompute, on rows read after the account row lock. A completion here is
        # F04's owner ``complete``; the owner's own edit that removes a requirement (the cleared
        # summary) keeps F04's owner ``edit`` from visible to incomplete.
        profile = recompute.recompute(tx, account_id, now, writer=recompute.PROFILE_EDIT).profile
        idempotency.store(
            account_id,
            operation,
            _key(intent),
            digest,
            result_ref=profile.id,
            result_version=int(profile.version),
            now=now,
        )
        return Result("applied", data=contract.own_profile(profile))

    return run(body, probe)


# -- the four list fields (D3) ----------------------------------------------------------------


def set_field(
    account_id: UUID, intent: dict[str, Any], *, probe: TransactionProbe | None = None
) -> Result:
    """One field's own value, own words and display flag: a new choice, checked against the
    current list (D2, D3). A sensitive field, or orientation's own words, needs the
    sensitive-fields consent (D6). Gender and "looking for" are replaced, never cleared."""
    field = str(intent["field"])
    operation = f"profile_field.{field}"
    digest = idempotency.digest(operation, intent)

    def body(tx: Tx) -> Result:
        lock_account(tx, account_id)
        catalog = catalogs.load(tx)
        profile = _profile(account_id)
        row = (
            ProfileFieldChoice.objects.select_for_update()
            .filter(account_id=account_id, field=field)
            .first()
        )
        signal(tx.probe, "after_locks")
        now = clock(tx)
        record = idempotency.decide(account_id, operation, _key(intent), digest, now)
        if record is not idempotency.NEW:
            return Result("replayed", data=_fields_projection(account_id, catalog))
        if profile is None:
            raise Refused(NOT_FOUND, "profile_missing")
        if profile.state not in EDITABLE:
            raise Refused(STATE_CONFLICT, "profile_not_editable")
        if intent["policy_version"] != catalog.version:
            raise Refused(STALE_VERSION, "stale_catalog")
        if _expected(intent) != (0 if row is None else int(row.version)):
            raise Refused(STALE_VERSION, "stale_version")
        values = list(intent["value_ids"])
        own_words, shown = intent["own_words"], intent["shown"]
        refusal = (
            pf.own_value_refusal(field, values, catalog.lists[field])
            or pf.own_words_refusal(field, own_words)
            or pf.shown_refusal(field, shown)
        )
        if refusal:
            raise Refused(INVALID_REQUEST, f"field:{refusal}")
        if pf.carries_sensitive(field, values, own_words) and not _sensitive_accepted(account_id):
            raise Refused(FORBIDDEN, "sensitive_consent_required")
        if row is None:
            row = ProfileFieldChoice(account_id=account_id, field=field)
        else:
            row.version += 1
        row.value_ids = values
        row.setting_version = catalog.lists[field].setting_version
        row.own_words = own_words
        row.shown = bool(shown)
        row.save()
        _bump_eligibility(account_id)
        events.emit(
            tx,
            events.PROFILE_FIELD_CHANGED,
            aggregate_id=row.id,
            aggregate_version=int(row.version),
            payload_ref=row.id,
            now=now,
        )
        # D9: the shared recompute; a completion here is F04's owner ``complete``.
        recompute.recompute(tx, account_id, now, writer=recompute.F04_OWNER)
        idempotency.store(
            account_id,
            operation,
            _key(intent),
            digest,
            result_ref=row.id,
            result_version=int(row.version),
            now=now,
        )
        return Result("applied", data=_fields_projection(account_id, catalog))

    return run(body, probe)


# -- "show me" sets (D3) and the filters (D4, D5) ---------------------------------------------


def set_preferences(
    account_id: UUID, intent: dict[str, Any], *, probe: TransactionProbe | None = None
) -> Result:
    """The four "show me" sets, each the ``all`` marker or a narrowed list of live values;
    narrowing orientation or relationship status needs the sensitive-fields consent (D6)."""
    operation = "preferences"
    digest = idempotency.digest(operation, intent)

    def body(tx: Tx) -> Result:
        lock_account(tx, account_id)
        catalog = catalogs.load(tx)
        preferences = Preferences.objects.select_for_update().filter(account_id=account_id).first()
        signal(tx.probe, "after_locks")
        now = clock(tx)
        record = idempotency.decide(account_id, operation, _key(intent), digest, now)
        if record is not idempotency.NEW:
            if preferences is None:
                raise Refused(NOT_FOUND, "profile_missing")
            return Result("replayed", data=contract.own_preferences(preferences, _sets(account_id)))
        if preferences is None:
            raise Refused(NOT_FOUND, "profile_missing")
        if intent["policy_version"] != catalog.version:
            raise Refused(STALE_VERSION, "stale_catalog")
        if _expected(intent) != int(preferences.version):
            raise Refused(STALE_VERSION, "stale_version")
        selections = {e["dimension"]: list(e["accepted_option_ids"]) for e in intent["selections"]}
        if set(selections) != set(pf.FIELDS):
            # F04: an unknown or missing dimension is refused.
            raise Refused(INVALID_REQUEST, "dimensions")
        for field in pf.FIELDS:
            refusal = pf.show_me_refusal(field, selections[field], catalog.lists[field])
            if refusal:
                raise Refused(INVALID_REQUEST, f"set:{refusal}")
        if any(pf.narrowed(selections[f]) for f in pf.SENSITIVE_FIELDS) and not _sensitive_accepted(
            account_id
        ):
            raise Refused(FORBIDDEN, "sensitive_consent_required")
        PreferenceSetEntry.objects.filter(account_id=account_id).delete()
        PreferenceSetEntry.objects.bulk_create(
            [
                PreferenceSetEntry(
                    account_id=account_id, field=field, value_id=value, position=position
                )
                for field in pf.FIELDS
                for position, value in enumerate(selections[field])
            ]
        )
        preferences.policy_version = catalog.version
        preferences.version += 1
        preferences.save(update_fields=["policy_version", "version", "updated_at"])
        _bump_preferences(account_id)
        events.emit(
            tx,
            events.PREFERENCES_CHANGED,
            aggregate_id=preferences.id,
            aggregate_version=int(preferences.version),
            payload_ref=preferences.id,
            now=now,
        )
        idempotency.store(
            account_id,
            operation,
            _key(intent),
            digest,
            result_ref=preferences.id,
            result_version=int(preferences.version),
            now=now,
        )
        return Result("applied", data=contract.own_preferences(preferences, _sets(account_id)))

    return run(body, probe)


def set_filters(
    account_id: UUID, intent: dict[str, Any], *, probe: TransactionProbe | None = None
) -> Result:
    """The age range (never below 18, D4) and the distance choice (one of the setting's, D5)."""
    operation = "filters"
    digest = idempotency.digest(operation, intent)

    def body(tx: Tx) -> Result:
        lock_account(tx, account_id)
        catalog = catalogs.load(tx)
        preferences = Preferences.objects.select_for_update().filter(account_id=account_id).first()
        signal(tx.probe, "after_locks")
        now = clock(tx)
        record = idempotency.decide(account_id, operation, _key(intent), digest, now)
        if record is not idempotency.NEW:
            if preferences is None:
                raise Refused(NOT_FOUND, "profile_missing")
            return Result("replayed", data=contract.own_filters(preferences))
        if preferences is None:
            raise Refused(NOT_FOUND, "profile_missing")
        if intent["policy_version"] != catalog.version:
            raise Refused(STALE_VERSION, "stale_catalog")
        if _expected(intent) != int(preferences.version):
            raise Refused(STALE_VERSION, "stale_version")
        minimum, maximum = int(intent["minimum_age"]), intent["maximum_age"]
        if minimum < ps.AGE_FLOOR:
            raise Refused(INVALID_REQUEST, "age_floor")
        if maximum is not None and int(maximum) < minimum:
            raise Refused(INVALID_REQUEST, "maximum_below_minimum")
        if intent["distance_choice"] not in catalogs.distance_ids(catalog.location):
            raise Refused(INVALID_REQUEST, "distance_choice")
        preferences.minimum_age = minimum
        preferences.maximum_age = maximum
        preferences.distance_choice = intent["distance_choice"]
        preferences.policy_version = catalog.version
        preferences.version += 1
        preferences.save(
            update_fields=[
                "minimum_age",
                "maximum_age",
                "distance_choice",
                "policy_version",
                "version",
                "updated_at",
            ]
        )
        _bump_preferences(account_id)
        events.emit(
            tx,
            events.PREFERENCES_CHANGED,
            aggregate_id=preferences.id,
            aggregate_version=int(preferences.version),
            payload_ref=preferences.id,
            now=now,
        )
        idempotency.store(
            account_id,
            operation,
            _key(intent),
            digest,
            result_ref=preferences.id,
            result_version=int(preferences.version),
            now=now,
        )
        return Result("applied", data=contract.own_filters(preferences))

    return run(body, probe)


# -- the area (D5) ----------------------------------------------------------------------------


def set_area(
    account_id: UUID, intent: dict[str, Any], *, probe: TransactionProbe | None = None
) -> Result:
    """The member's home area, chosen by its ID; only the area is kept."""
    operation = "area"
    digest = idempotency.digest(operation, intent)

    def body(tx: Tx) -> Result:
        lock_account(tx, account_id)
        location = settings_store.read_shared(tx, [ps.LOCATION])[ps.LOCATION].content
        profile = _profile(account_id)
        signal(tx.probe, "after_locks")
        now = clock(tx)
        record = idempotency.decide(account_id, operation, _key(intent), digest, now)
        if record is not idempotency.NEW:
            if profile is None:
                raise Refused(NOT_FOUND, "profile_missing")
            current = Area.objects.filter(pk=profile.area_id).first() if profile.area_id else None
            return Result("replayed", data=contract.own_area(profile, current))
        if profile is None:
            raise Refused(NOT_FOUND, "profile_missing")
        if profile.state not in EDITABLE:
            raise Refused(STATE_CONFLICT, "profile_not_editable")
        if _expected(intent) != int(profile.version):
            raise Refused(STALE_VERSION, "stale_version")
        if not (location["chosen_area"] or location["approximate_location"]):
            raise Refused(FORBIDDEN, "no_way_of_locating")
        area = Area.objects.filter(area_id=intent["area_id"]).first()
        if area is None:
            raise Refused(INVALID_REQUEST, "unknown_area")
        profile.area = area
        profile.version += 1
        profile.save(update_fields=["area", "version", "updated_at"])
        _bump_eligibility(account_id)
        events.emit(
            tx,
            events.AREA_CHANGED,
            aggregate_id=profile.id,
            aggregate_version=int(profile.version),
            payload_ref=profile.id,
            now=now,
        )
        # D9: the shared recompute; a completion here is F04's owner ``complete``.
        profile = recompute.recompute(tx, account_id, now, writer=recompute.F04_OWNER).profile
        idempotency.store(
            account_id,
            operation,
            _key(intent),
            digest,
            result_ref=profile.id,
            result_version=int(profile.version),
            now=now,
        )
        return Result("applied", data=contract.own_area(profile, area))

    return run(body, probe)


def nearest_area(account_id: UUID, query: dict[str, Any]) -> Result:
    """D5: the phone-location query. It returns the nearest area and changes nothing: no row,
    no event and no idempotency record. The coordinates stay in this call's memory."""

    def body(tx: Tx) -> Result:
        read_account_shared(tx, account_id)
        location = settings_store.read_shared(tx, [ps.LOCATION])[ps.LOCATION].content
        if not location["approximate_location"]:
            raise Refused(FORBIDDEN, "approximate_location_not_offered")
        found = areas.nearest(float(query["latitude"]), float(query["longitude"]), areas.points())
        return Result("read", data=contract.nearest_area(found.area_id, found.name))

    return run(body)


# -- onboarding consent (D6; F02, through glow_chat) --------------------------------------------


def decide_onboarding_consent(
    account_id: UUID, intent: dict[str, Any], *, probe: TransactionProbe | None = None
) -> Result:
    """F02's accept and withdraw through ``glow_chat``'s ``accept_consent`` and
    ``withdraw_consent``, nested. SV2's version check comes first, under the account row lock and
    the consent policy's pointer lock: any version but the current one is refused (F02: "old
    consent version rejected"). It ends with D9's recompute: an acceptance can complete the
    profile, and a withdrawal demotes a ``visible`` one."""
    operation = "consent"
    digest = idempotency.digest(operation, intent)

    def body(tx: Tx) -> Result:
        lock_account(tx, account_id)
        current = settings_store.read_shared(tx, [ps.ONBOARDING_CONSENT])[ps.ONBOARDING_CONSENT]
        profile = _profile(account_id)
        signal(tx.probe, "after_locks")
        now = clock(tx)
        record = idempotency.decide(account_id, operation, _key(intent), digest, now)
        if record is not idempotency.NEW:
            return Result(
                "replayed",
                data=_onboarding_projection(account_id, profile, current.policy_version),
            )
        latest = requirements.latest_decision(account_id, ONBOARDING_CONSENT_PURPOSE)
        if _expected(intent) != (0 if latest is None else int(latest.version)) + 1:
            raise Refused(STALE_VERSION, "stale_version")
        if intent["decision"] == "accepted":
            if intent["policy_version"] != current.policy_version:
                raise Refused(STALE_VERSION, "consent_version_not_current")
            outcome = _chat_checked(
                chat().accept_consent(account_id, policy_version=intent["policy_version"])
            )
        else:
            if latest is None:
                raise Refused(STATE_CONFLICT, "no_consent")
            outcome = _chat_checked(chat().withdraw_consent(account_id))
        # D9: the shared recompute. An acceptance that meets the last requirement completes the
        # profile (F04 ``requirements_met``); a withdrawal demotes a visible one
        # (``requirement_removed``).
        profile = recompute.recompute(tx, account_id, now, writer=recompute.OTHER_FLOW).profile
        latest = requirements.latest_decision(account_id, ONBOARDING_CONSENT_PURPOSE)
        idempotency.store(
            account_id,
            operation,
            _key(intent),
            digest,
            result_ref=latest.id,
            result_version=int(latest.version),
            now=now,
        )
        return Result(
            "applied" if outcome.outcome == "applied" else "no_change",
            data=_onboarding_projection(account_id, profile, current.policy_version),
        )

    return run(body, probe)


# -- the sensitive-fields consent (D6; G-10): SV2's own writer --------------------------------


def decide_sensitive_consent(
    account_id: UUID, intent: dict[str, Any], *, probe: TransactionProbe | None = None
) -> Result:
    """The sensitive-fields consent (purpose ``sensitive_profile``), SV2's own writer (DM-52):
    the account row lock first, the version check under the consent policy's pointer lock, then
    the decision. Withdrawal, in the same transaction, removes the member's own orientation and
    relationship status values and orientation's own words, resets both "show me" sets to all,
    and deletes the idempotency records of the commands that carried any of them."""
    operation = "sensitive_consent"
    digest = idempotency.digest(operation, intent)

    def body(tx: Tx) -> Result:
        lock_account(tx, account_id)
        current = settings_store.read_shared(tx, [ps.SENSITIVE_CONSENT])[ps.SENSITIVE_CONSENT]
        preferences = Preferences.objects.select_for_update().filter(account_id=account_id).first()
        signal(tx.probe, "after_locks")
        now = clock(tx)
        record = idempotency.decide(account_id, operation, _key(intent), digest, now)
        latest = requirements.latest_decision(account_id, SENSITIVE_PURPOSE)
        if record is not idempotency.NEW:
            return Result("replayed", data=contract.sensitive_consent(latest))
        if _expected(intent) != (0 if latest is None else int(latest.version)) + 1:
            raise Refused(STALE_VERSION, "stale_version")
        accepting = intent["decision"] == "accepted"
        if accepting and intent["policy_version"] != current.policy_version:
            raise Refused(STALE_VERSION, "consent_version_not_current")
        if not accepting and latest is None:
            raise Refused(STATE_CONFLICT, "no_consent")
        unchanged = latest is not None and (
            (
                accepting
                and latest.state == "accepted"
                and latest.policy_version == intent["policy_version"]
            )
            or (not accepting and latest.state == "withdrawn")
        )
        if not unchanged:
            latest = ConsentDecision.objects.create(
                account_id=account_id,
                purpose=SENSITIVE_PURPOSE,
                policy_version=intent["policy_version"] if accepting else latest.policy_version,
                state="accepted" if accepting else "withdrawn",
                decided_at=now,
                version=1 if latest is None else int(latest.version) + 1,
            )
            _bump_eligibility(account_id)
            events.emit(
                tx,
                events.SENSITIVE_CONSENT_ACCEPTED
                if accepting
                else events.SENSITIVE_CONSENT_WITHDRAWN,
                aggregate_id=account_id,
                aggregate_version=int(latest.version),
                payload_ref=latest.id,
                now=now,
            )
            if not accepting:
                _withdraw_sensitive_data(tx, account_id, preferences, now)
        assert latest is not None
        idempotency.store(
            account_id,
            operation,
            _key(intent),
            digest,
            result_ref=latest.id,
            result_version=int(latest.version),
            now=now,
        )
        return Result(
            "no_change" if unchanged else "applied", data=contract.sensitive_consent(latest)
        )

    return run(body, probe)


def _withdraw_sensitive_data(tx: Tx, account_id: UUID, preferences: Any, now: datetime) -> None:
    """D6's withdrawal scope, in the withdrawal's transaction."""
    ProfileFieldChoice.objects.filter(account_id=account_id, field__in=pf.SENSITIVE_FIELDS).delete()
    if preferences is not None:
        PreferenceSetEntry.objects.filter(
            account_id=account_id, field__in=pf.SENSITIVE_FIELDS
        ).delete()
        PreferenceSetEntry.objects.bulk_create(
            [
                PreferenceSetEntry(account_id=account_id, field=field, value_id=pf.ALL)
                for field in sorted(pf.SENSITIVE_FIELDS)
            ]
        )
        preferences.version += 1
        preferences.save(update_fields=["version", "updated_at"])
        _bump_preferences(account_id)
        events.emit(
            tx,
            events.PREFERENCES_CHANGED,
            aggregate_id=preferences.id,
            aggregate_version=int(preferences.version),
            payload_ref=preferences.id,
            now=now,
        )
    IdempotencyRecord.objects.filter(
        actor_id=account_id, operation__in=SENSITIVE_OPERATIONS
    ).delete()


# -- the adult check and the one date (D7) ----------------------------------------------------


def _invalidate_birth_input(
    tx: Tx, account_id: UUID, entered: Any, now: datetime, *, whatever_its_date: bool = False
) -> bool:
    """D7's choice: a new eligibility date, while a current birth input holds another, makes it
    stop being current (F03 ``date_changed``: its state becomes ``missing``) and returns any
    mapping to ``pending``; re-entry is asked for by the read's ``resolution: missing``. A birth
    input whose date fails the adult rule (DM-54) makes the current one stop being current
    whatever its date (``whatever_its_date``)."""
    current = (
        BirthInput.objects.select_for_update()
        .filter(account_id=account_id)
        .order_by("-version")
        .first()
    )
    if current is None or current.state == "missing":
        return False
    if not whatever_its_date and current.birth_date == entered:
        return False
    current.state = "missing"
    current.save(update_fields=["state", "updated_at"])
    _mapping_to_pending(account_id, current)
    events.emit(
        tx,
        events.BIRTH_INPUT_INVALIDATED,
        aggregate_id=current.id,
        aggregate_version=int(current.version),
        payload_ref=current.id,
        now=now,
    )
    return True


def _mapping_to_pending(account_id: UUID, revision: Any) -> None:
    """F03 (D8; DM-53): a mapping returns to ``pending``, its engine reference and versions
    cleared, its ``adapter_version`` kept, pointing at ``revision``. SV2 creates no mapping."""
    mapping = EngineIdentity.objects.select_for_update().filter(account_id=account_id).first()
    if mapping is None:
        return
    mapping.state = "pending"
    mapping.engine_reference = None
    mapping.engine_version = None
    mapping.contract_version = None
    mapping.birth_input = revision
    mapping.version += 1
    mapping.save()


def _age_transition(tx: Tx, account_id: UUID, entered: Any, now: datetime) -> tuple[str, bool]:
    """Every date change reruns the check (D7): a passing date becomes the age state's, and a
    failing one sets ``unknown`` with no date (the date is never handed to the port). Returns the
    port's outcome and whether the rerun failed; the writer's recompute then demotes a
    ``visible`` profile."""
    passed = adult_outcome(entered, utc_date(now)) is AdultOutcome.PASS
    change = AgeTransition(
        AccountId(str(account_id)),
        AgeAssuranceState.SELF_DECLARED_ADULT if passed else AgeAssuranceState.UNKNOWN,
        entered if passed else None,
        now,
    )
    try:
        outcome = OrmAgeAssurance().transition(change)
    except AgeTransitionRefused as refused:
        raise Refused(STATE_CONFLICT, f"age:{refused}") from None
    return outcome, not passed


def adult_check(
    account_id: UUID, intent: dict[str, Any], *, probe: TransactionProbe | None = None
) -> Result:
    """D7's adult check at the eligibility step, from the self-entered date. With the state
    ``unknown``, a failing date is refused and not stored. With ``self_declared_adult``, a new
    date reruns the check: a pass keeps the state with the new date; a fail sets ``unknown`` and
    clears the date. A new date also makes a current birth input that holds another stop being
    current. It ends with D9's recompute: a pass can complete the profile, and a failing rerun
    or a birth input that stopped being current demotes a ``visible`` one."""
    operation = "adult_check"
    digest = idempotency.digest(operation, intent)

    def body(tx: Tx) -> Result:
        lock_account(tx, account_id)
        age = AccountAgeState.objects.select_for_update().filter(account_id=account_id).first()
        # The profile's lock, in the writer's order; the recompute reads it again under it.
        _profile(account_id)
        signal(tx.probe, "after_locks")
        now = clock(tx)
        if age is None:
            raise Refused(NOT_FOUND, "age_state_missing")
        record = idempotency.decide(account_id, operation, _key(intent), digest, now)
        if record is not idempotency.NEW:
            return Result("replayed", data=contract.own_age_state(age))
        if _expected(intent) != int(age.version):
            raise Refused(STALE_VERSION, "stale_version")
        entered = date.fromisoformat(intent["birth_date"])
        outcome = adult_outcome(entered, utc_date(now))
        if age.state == "unknown" and outcome is not AdultOutcome.PASS:
            # D7: a failing date is refused and not stored; the state stays unknown.
            code = FORBIDDEN if outcome is AdultOutcome.UNDER_AGE else INVALID_REQUEST
            raise Refused(code, f"adult_check:{outcome.value}")
        if age.state == "self_declared_adult" and age.birth_date == entered:
            age.refresh_from_db()
            # D9: the shared recompute ends this writer too, so a requirement that lapsed without
            # a write (a new consent version) demotes here.
            recompute.recompute(tx, account_id, now, writer=recompute.OTHER_FLOW)
            idempotency.store(
                account_id,
                operation,
                _key(intent),
                digest,
                result_ref=age.id,
                result_version=int(age.version),
                now=now,
            )
            return Result("no_change", data=contract.own_age_state(age))
        _age_transition(tx, account_id, entered, now)
        age.refresh_from_db()
        events.emit(
            tx,
            events.AGE_STATE_CHANGED,
            aggregate_id=age.id,
            aggregate_version=int(age.version),
            payload_ref=age.id,
            now=now,
        )
        _invalidate_birth_input(tx, account_id, entered, now)
        # D9: the shared recompute (F04 ``requirements_met`` or ``requirement_removed``).
        recompute.recompute(tx, account_id, now, writer=recompute.OTHER_FLOW)
        idempotency.store(
            account_id,
            operation,
            _key(intent),
            digest,
            result_ref=age.id,
            result_version=int(age.version),
            now=now,
        )
        return Result("applied", data=contract.own_age_state(age))

    return run(body, probe)


# -- the private birth input (D8; F03) --------------------------------------------------------


def save_birth_input(
    account_id: UUID, intent: dict[str, Any], *, probe: TransactionProbe | None = None
) -> Result:
    """F03's owner ``submit``, ``correct`` and ``change``: a new private revision, ``pending``.
    It needs the adult pass and the current onboarding consent (P04's ``/birth``). A birth time is
    required (Nathan: "birth time is required at signup"). A new revision returns any mapping to
    ``pending``; another date changes the age state's date and reruns the adult check (D7). A
    date that fails the adult rule is refused and nothing of the input is stored, while the
    failing rerun commits (DM-54; ``_refuse_failing_birth_input``). It ends with D9's recompute,
    which demotes a ``visible`` profile, since a new revision's chart is not resolved. SV2 creates
    no ``EngineIdentity`` and resolves nothing."""
    operation = "birth_input"
    digest = idempotency.digest(operation, intent)

    def body(tx: Tx) -> Result:
        lock_account(tx, account_id)
        consent = settings_store.read_shared(tx, [ps.ONBOARDING_CONSENT])[ps.ONBOARDING_CONSENT]
        age = AccountAgeState.objects.select_for_update().filter(account_id=account_id).first()
        current = (
            BirthInput.objects.select_for_update()
            .filter(account_id=account_id)
            .order_by("-version")
            .first()
        )
        # The profile's lock, in the writer's order; the recompute reads it again under it.
        _profile(account_id)
        signal(tx.probe, "after_locks")
        now = clock(tx)
        record = idempotency.decide(account_id, operation, _key(intent), digest, now)
        if record is not idempotency.NEW:
            if current is None:
                raise Refused(NOT_FOUND, "birth_input_missing")
            return Result("replayed", data=_birth_projection(current, account_id))
        if age is None or age.state != "self_declared_adult":
            raise Refused(FORBIDDEN, "adult_check_required")
        if not requirements.onboarding_current(account_id, consent.policy_version):
            raise Refused(FORBIDDEN, "onboarding_consent_required")
        if _expected(intent) != (0 if current is None else int(current.version)):
            raise Refused(STALE_VERSION, "stale_version")
        given = intent["input"]
        if given["time_precision"] == "unknown":
            # D8: a server rule; the contract's BirthInput still allows unknown, and nothing
            # guesses a time.
            raise Refused(INVALID_REQUEST, "birth_time_required")
        born = date.fromisoformat(given["birth_date"])
        if born > utc_date(now):
            raise Refused(INVALID_REQUEST, "birth_date_in_future")
        if adult_outcome(born, utc_date(now)) is not AdultOutcome.PASS:
            # D7, D8 (DM-54): a birth input whose date fails the adult rule is refused and
            # nothing of it is stored, while the failing rerun commits.
            return _refuse_failing_birth_input(tx, account_id, born, now)
        accepted = requirements.latest_decision(account_id, ONBOARDING_CONSENT_PURPOSE)
        revision = BirthInput.objects.create(
            account_id=account_id,
            version=1 if current is None else int(current.version) + 1,
            birth_date=born,
            local_time=time.fromisoformat(given["local_time"]),
            time_precision=given["time_precision"],
            place_label=given["place_label"],
            timezone_name=given["timezone_name"],
            timezone_provenance=given["timezone_provenance"],
            consent_version=accepted.policy_version,
            state="pending",
        )
        _mapping_to_pending(account_id, revision)
        if age.birth_date != born:
            # D7: one date. The birth input's date becomes the age state's, and the check reruns;
            # a failing date never reaches here, so the rerun passes.
            _age_transition(tx, account_id, born, now)
            age.refresh_from_db()
            events.emit(
                tx,
                events.AGE_STATE_CHANGED,
                aggregate_id=age.id,
                aggregate_version=int(age.version),
                payload_ref=age.id,
                now=now,
            )
        _bump_eligibility(account_id)
        events.emit(
            tx,
            events.BIRTH_INPUT_SUBMITTED,
            aggregate_id=revision.id,
            aggregate_version=int(revision.version),
            payload_ref=revision.id,
            now=now,
        )
        # D9: the shared recompute. A new revision is ``pending``, so the chart is missing and a
        # visible profile is demoted (F04 ``requirement_removed``).
        recompute.recompute(tx, account_id, now, writer=recompute.OTHER_FLOW)
        idempotency.store(
            account_id,
            operation,
            _key(intent),
            digest,
            result_ref=revision.id,
            result_version=int(revision.version),
            now=now,
        )
        return Result("applied", data=_birth_projection(revision, account_id))

    return run(body, probe)


# The refusal of a birth input whose date fails the adult rule (DM-54). Its public code is the
# adult check's for an under-age date.
BIRTH_DATE_FAILS_ADULT_RULE = "birth_date_fails_adult_rule"


def _refuse_failing_birth_input(tx: Tx, account_id: UUID, born: date, now: datetime) -> Result:
    """D7 and D8 (DM-54, Y6 to Y8): the birth input is refused and nothing of it is stored (no
    revision, no date, time or place, no mapping change toward it, no idempotency record), while
    the transaction commits the failing rerun:

    - the age state becomes ``unknown`` with no date (F02 ``adult_check_failed``), through the age
      port, which bumps ``eligibility_version``;
    - a current birth input stops being current (F03 ``date_changed``: ``missing``), its mapping
      back to ``pending``;
    - D9's recompute moves a ``visible`` profile to ``incomplete`` (F04 ``requirement_removed``);
      a ``paused`` one stays paused.

    The refusal is returned, not raised, so ``tx.run`` commits these effects. With no idempotency
    record, a retry of this command or another is refused at the adult-check gate
    (``adult_check_required``, since the state is now ``unknown``) and changes nothing more."""
    _age_transition(tx, account_id, born, now)
    age = AccountAgeState.objects.get(account_id=account_id)
    events.emit(
        tx,
        events.AGE_STATE_CHANGED,
        aggregate_id=age.id,
        aggregate_version=int(age.version),
        payload_ref=age.id,
        now=now,
    )
    _invalidate_birth_input(tx, account_id, born, now, whatever_its_date=True)
    recompute.recompute(tx, account_id, now, writer=recompute.OTHER_FLOW)
    return Result("refused", FORBIDDEN, BIRTH_DATE_FAILS_ADULT_RULE)


# -- visibility (D9; F06, through glow_chat) --------------------------------------------------


def set_visibility(
    account_id: UUID, intent: dict[str, Any], *, probe: TransactionProbe | None = None
) -> Result:
    """F06's pause and resume through ``glow_chat``'s ``pause_profile`` and ``resume_profile``,
    nested. Resume rechecks completion first, on rows read after the account row lock, and an
    incomplete profile is refused before ``resume_profile`` is called."""
    operation = "visibility"
    digest = idempotency.digest(operation, intent)

    def body(tx: Tx) -> Result:
        lock_account(tx, account_id)
        consent = settings_store.read_shared(tx, [ps.ONBOARDING_CONSENT])[ps.ONBOARDING_CONSENT]
        profile = _profile(account_id)
        signal(tx.probe, "after_locks")
        now = clock(tx)
        record = idempotency.decide(account_id, operation, _key(intent), digest, now)
        if profile is None:
            raise Refused(NOT_FOUND, "profile_missing")
        if record is not idempotency.NEW:
            return Result("replayed", data=contract.own_profile(profile))
        if _expected(intent) != int(profile.version):
            raise Refused(STALE_VERSION, "stale_version")
        if intent["action"] == "pause":
            outcome = _chat_checked(chat().pause_profile(account_id))
        else:
            if profile.state != "paused":
                raise Refused(STATE_CONFLICT, "profile_not_paused")
            missing = requirements.missing(account_id, profile, consent.policy_version)
            if missing:
                # F06: "resume rechecks current visibility eligibility".
                raise Refused(FORBIDDEN, "completion_required")
            outcome = _chat_checked(chat().resume_profile(account_id))
        profile.refresh_from_db()
        idempotency.store(
            account_id,
            operation,
            _key(intent),
            digest,
            result_ref=profile.id,
            result_version=int(profile.version),
            now=now,
        )
        return Result(
            "applied" if outcome.outcome == "applied" else "no_change",
            data=contract.own_profile(profile),
        )

    return run(body, probe)
