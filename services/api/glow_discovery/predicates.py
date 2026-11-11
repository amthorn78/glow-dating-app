"""The eligibility predicates (the SV3 brief's D3 to D5) and D7's consumption, as SQL: the one
source of the selection, each page's recheck and the trusted adapter's pair read (``eligibility``),
so the three cannot disagree.

Each predicate is written for a member alias (``v``, the viewer; ``c``, the candidate) over
``member``'s columns, and each holds for the viewer and for the candidate:

- **SELF:** the candidate is not the viewer.
- **ACTIVE:** the account is ``active``.
- **ADULT** (G-01): the age state is one of the accepted states (``policy.ACCEPTED_AGE_STATES``),
  with its date; read directly, because ``visible`` can lag it.
- **CONSENT** (DM-54): the account's latest ``onboarding`` decision, by purpose, is ``accepted`` at
  the current version; a ``sensitive_profile`` decision never satisfies it, and a newer onboarding
  version fails every older acceptance at once. Read directly, because ``visible`` can lag it.
- **VISIBLE** (with VERIFIED, COMPLETE and MODERATION): the profile is ``visible``, which SV2's
  completion and every requirement writer's recompute carry (OD-61; DM-60 item 3); ``paused``,
  ``restricted``, ``removed`` and ``incomplete`` fail it.
- **PREFERENCE, the four fields** (D4): for each field, at least one of each member's own values is
  in the other's "show me" set. The ``all`` row matches every value, those the console adds later
  and "not stated" included; a narrowed set matches list values only, a retired one included, and
  never "not stated"; a member with no row for a field has no value in it. A field the narrowing
  setting makes not narrowable reads as keeping all. A member with no set row for a field accepts no
  one in it (fail closed).
- **PREFERENCE, age** (D4): the candidate's age, in whole years from the age state's date on the
  server's UTC date (never the birth input), within the viewer's range; under ``both_ways`` the
  viewer's within the candidate's. The rule is ``glow_domain.identity.whole_years``': the year
  difference, less one before the birthday, a 29 February birthday falling on 1 March in a common
  year. No range (a missing preferences row or minimum) fails.
- **PREFERENCE, distance** (D5): in the viewer's direction only, the great-circle distance between
  the two areas' internal points (``glow_profiles.areas``' formula, in the same order of
  operations), within the viewer's choice; two members in one area are at distance zero; a choice
  with no miles filters nothing; a choice the location setting does not offer fails. The distance is
  compared here and never selected.
- **BLOCK:** no ``active`` block in either direction.
- **Consumption** (D7; DM-60 Q5): no ``liked`` or ``passed`` row from the viewer to the candidate,
  and no ``Match`` row for the pair in any state (``active``, ``restricted`` or ``unmatched``). It
  is not an eligibility predicate (the adapter does not read it); the selection and every recheck
  add it.

Every predicate fails closed: a missing row reads as NULL or as no row, and a NULL is not a pass
(``IS TRUE``). No statement selects a birth date, a coordinate, an area ID or a distance.
"""

from __future__ import annotations

from glow_domain import profile_fields as pf
from glow_profiles import areas

# D4: whole years from ``{birth}`` to the server's UTC date, ``whole_years``' rule. The proof pins
# this expression to ``glow_domain.identity.whole_years`` at the onboarding fixtures' leap days.
AGE = """CASE WHEN {birth} IS NULL THEN NULL ELSE
         (date_part('year', %(today)s::date) - date_part('year', {birth}))::int
         - CASE WHEN (date_part('month', %(today)s::date), date_part('day', %(today)s::date))
                     < (date_part('month', {birth}), date_part('day', {birth}))
                THEN 1 ELSE 0 END
       END"""

MEMBER = f"""
SELECT a.id AS account_id, a.state AS account_state, a.eligibility_version,
       a.preferences_version, a.blocks_version,
       p.id AS profile_id, p.version AS profile_version, p.state AS profile_state,
       p.display_name, p.bio, ar.name AS area_name,
       ar.latitude::float8 AS lat, ar.longitude::float8 AS lon,
       {AGE.format(birth="s.birth_date")} AS age,
       (s.state = ANY(%(adult_states)s) AND s.birth_date IS NOT NULL) AS adult,
       EXISTS (
         SELECT 1 FROM glow_persistence_consentdecision d
         WHERE d.account_id = a.id AND d.purpose = 'onboarding' AND d.state = 'accepted'
           AND d.policy_version = %(consent)s
           AND d.version = (
             SELECT max(l.version) FROM glow_persistence_consentdecision l
             WHERE l.account_id = a.id AND l.purpose = 'onboarding')
       ) AS consent,
       pr.minimum_age, pr.maximum_age, pr.distance_choice
FROM glow_persistence_appaccount a
LEFT JOIN glow_persistence_profile p ON p.account_id = a.id
LEFT JOIN glow_persistence_area ar ON ar.id = p.area_id
LEFT JOIN glow_persistence_accountagestate s ON s.account_id = a.id
LEFT JOIN glow_persistence_preferences pr ON pr.account_id = a.id
"""


def member_states(alias: str) -> str:
    """ACTIVE, VISIBLE, ADULT and CONSENT for one member."""
    return (
        f"({alias}.account_state = 'active') IS TRUE"
        f" AND ({alias}.profile_state = 'visible') IS TRUE"
        f" AND {alias}.adult IS TRUE AND {alias}.consent IS TRUE"
    )


def sees(x: str, y: str, field: str) -> str:
    """``x``'s "show me" set for ``field`` holds one of ``y``'s own values (D4)."""
    return f"""(NOT %(narrow_{field})s OR EXISTS (
        SELECT 1 FROM glow_persistence_preferencesetentry e
        WHERE e.account_id = {x}.account_id AND e.field = '{field}'
          AND (e.value_id = '{pf.ALL}' OR (e.value_id <> '{pf.NOT_STATED}' AND EXISTS (
            SELECT 1 FROM glow_persistence_profilefieldchoice fc
            WHERE fc.account_id = {y}.account_id AND fc.field = '{field}'
              AND fc.value_ids @> jsonb_build_array(e.value_id))))))"""


def fields(x: str, y: str) -> str:
    """``x`` accepts ``y`` in every one of the four fields."""
    return " AND ".join(sees(x, y, field) for field in pf.FIELDS)


def in_range(x: str, y: str) -> str:
    """``y``'s age lies within ``x``'s range (D4)."""
    return (
        f"({x}.minimum_age IS NOT NULL AND {y}.age >= {x}.minimum_age"
        f" AND ({x}.maximum_age IS NULL OR {y}.age <= {x}.maximum_age))"
    )


def miles(x: str, y: str) -> str:
    """The great-circle distance between ``x``'s and ``y``'s internal points, as
    ``glow_profiles.areas.miles_between(x, y)`` computes it. Compared, never selected."""
    radius = f"{areas.EARTH_RADIUS_MILES!r}::float8"
    h = (
        f"power(sin((radians({y}.lat) - radians({x}.lat)) / 2), 2)"
        f" + cos(radians({x}.lat)) * cos(radians({y}.lat))"
        f" * power(sin(radians({y}.lon - {x}.lon) / 2), 2)"
    )
    return f"({radius} * (2::float8 * asin(least(1.0::float8, sqrt({h})))))"


def distance(x: str, y: str) -> str:
    """D5: ``y`` within ``x``'s distance choice. ``%(choices)s`` maps each choice the location
    setting offers to its miles (JSON ``null`` for one that filters nothing); a choice it does not
    offer, or none, is SQL NULL here and fails."""
    choice = f"(%(choices)s::jsonb -> {x}.distance_choice)"
    limit = f"(%(choices)s::jsonb ->> {x}.distance_choice)::float8"
    return (
        f"({choice} IS NOT NULL AND (jsonb_typeof({choice}) = 'null' OR ({x}.lat IS NOT NULL"
        f" AND {y}.lat IS NOT NULL AND {miles(x, y)} <= {limit})))"
    )


def viewer_accepts(v: str = "v", c: str = "c") -> str:
    """The viewer's direction: the fields, the age range and the distance."""
    return f"({fields(v, c)} AND {in_range(v, c)} AND {distance(v, c)})"


def candidate_accepts(v: str = "v", c: str = "c") -> str:
    """The candidate's direction: the fields, and the age range under ``both_ways``."""
    return f"({fields(c, v)} AND (NOT %(both_ways)s OR {in_range(c, v)}))"


def blocks(x: str, y: str) -> str:
    """An ``active`` block from ``x`` to ``y``."""
    return (
        "EXISTS (SELECT 1 FROM glow_persistence_block b WHERE b.state = 'active'"
        f" AND b.actor_id = {x}.account_id AND b.target_id = {y}.account_id)"
    )


def eligible(v: str = "v", c: str = "c") -> str:
    """Every predicate of D3 to D5, for the viewer and for the candidate."""
    return (
        f"{member_states(v)} AND {member_states(c)}"
        f" AND {c}.account_id <> {v}.account_id"
        f" AND {viewer_accepts(v, c)} IS TRUE AND {candidate_accepts(v, c)} IS TRUE"
        f" AND NOT {blocks(v, c)} AND NOT {blocks(c, v)}"
    )


def unconsumed(v: str = "v", c: str = "c") -> str:
    """D7's consumption: no like or pass from the viewer to the candidate, and no match row."""
    return (
        "NOT EXISTS (SELECT 1 FROM glow_persistence_directionalinteraction i"
        f" WHERE i.actor_id = {v}.account_id AND i.target_id = {c}.account_id"
        " AND i.state IN ('liked', 'passed'))"
        " AND NOT EXISTS (SELECT 1 FROM glow_persistence_match m"
        " WHERE m.state IN ('active', 'restricted', 'unmatched')"
        f" AND ((m.account_low_id = {v}.account_id AND m.account_high_id = {c}.account_id)"
        f" OR (m.account_low_id = {c}.account_id AND m.account_high_id = {v}.account_id)))"
    )


# The card's columns (D13): what the projection may show, never a birth date, a "show me" set, a
# filter, an area ID, a coordinate or a distance. The fields' rows are read whole, and the card
# shows only what ``glow_domain.profile_fields.displayed`` allows.
CARD = """
c.account_id, c.profile_id, c.display_name, c.bio, c.age, c.area_name,
c.eligibility_version, c.preferences_version, c.blocks_version,
(SELECT coalesce(jsonb_object_agg(fc.field, jsonb_build_object(
    'value_ids', fc.value_ids, 'own_words', fc.own_words, 'shown', fc.shown)), '{}'::jsonb)
 FROM glow_persistence_profilefieldchoice fc WHERE fc.account_id = c.account_id) AS fields,
ARRAY(SELECT ma.id FROM glow_persistence_mediaasset ma
      WHERE ma.account_id = c.account_id AND ma.state = 'approved'
      ORDER BY ma.position) AS media_ids
"""
CARD_NAMES: tuple[str, ...] = (
    "account_id",
    "profile_id",
    "display_name",
    "bio",
    "age",
    "area_name",
    "eligibility_version",
    "preferences_version",
    "blocks_version",
    "fields",
    "media_ids",
)

# A member's chart mapping, for the compatibility port's request (D6).
CHART = """
LEFT JOIN LATERAL (
  SELECT ei.state, ei.engine_reference, ei.version, bi.version AS birth_version
  FROM glow_persistence_engineidentity ei
  JOIN glow_persistence_birthinput bi ON bi.id = ei.birth_input_id
  WHERE ei.account_id = {alias}.account_id
) {name} ON true
"""
CHART_COLUMNS = "{name}.state, {name}.engine_reference, {name}.version, {name}.birth_version"

# D6 (Q2): the keyed tie-break, HMAC-SHA-256 over PostgreSQL's core sha256 with the pads from
# ``keys.sql_pads``; equal to ``keys.tie_break`` for the same batch and profile.
TIE_BREAK = (
    "sha256(%(opad)s::bytea || sha256(%(ipad)s::bytea"
    " || convert_to(%(batch)s::text || ':' || c.profile_id::text, 'UTF8')))"
)

# -- the statements --------------------------------------------------------------------------

VIEWER = f"""
WITH v AS ({MEMBER} WHERE a.id = %(viewer)s)
SELECT {member_states("v")}, v.eligibility_version, v.preferences_version, v.blocks_version,
       v.distance_choice, {CHART_COLUMNS.format(name="chart")}
FROM v {CHART.format(alias="v", name="chart")}
"""

# The batch's selection (D2, D6, D7): one statement, so one snapshot, holding every predicate and
# consumption, ordered by the keyed tie-break and bounded by the batch's limit. For broader
# discovery it also leaves out the viewer's current recommendations batch's candidates.
SELECTION = f"""
WITH v AS ({MEMBER} WHERE a.id = %(viewer)s),
     c AS ({MEMBER} WHERE p.state = 'visible' AND a.state = 'active')
SELECT {CARD}, {CHART_COLUMNS.format(name="chart")}, {TIE_BREAK} AS tie_break
FROM v CROSS JOIN c {CHART.format(alias="c", name="chart")}
WHERE {eligible()} AND {unconsumed()}
  AND (%(exclude_batch)s::uuid IS NULL OR NOT EXISTS (
    SELECT 1 FROM glow_persistence_recommendationentry x
    WHERE x.batch_id = %(exclude_batch)s::uuid AND x.candidate_id = c.account_id))
ORDER BY tie_break, c.profile_id
LIMIT %(limit)s
"""

# Each page's recheck (D2, D7; DM-60 Q1): one statement, so one snapshot, that evaluates every
# predicate and consumption again for every entry from the cursor's offset, in position order.
RECHECK = f"""
WITH v AS ({MEMBER} WHERE a.id = %(viewer)s),
     c AS ({MEMBER} WHERE a.id IN (
       SELECT candidate_id FROM glow_persistence_recommendationentry
       WHERE batch_id = %(batch_id)s))
SELECT x.position, {CARD}
FROM glow_persistence_recommendationentry x
JOIN c ON c.account_id = x.candidate_id
CROSS JOIN v
WHERE x.batch_id = %(batch_id)s AND x.position >= %(offset)s
  AND {eligible()} AND {unconsumed()}
ORDER BY x.position
LIMIT %(limit)s
"""

# The trusted adapter's pair read (D2): both members' predicates and both directions, one row,
# one statement. A missing member reads as NULLs, which the adapter maps to unknown.
PAIR = f"""
WITH v AS ({MEMBER} WHERE a.id = %(viewer)s),
     c AS ({MEMBER} WHERE a.id = %(candidate)s)
SELECT v.account_id, v.eligibility_version, v.preferences_version, v.blocks_version,
       v.profile_version, v.account_state, v.profile_state, v.adult, v.consent,
       c.account_id, c.eligibility_version, c.preferences_version, c.blocks_version,
       c.profile_version, c.account_state, c.profile_state, c.adult, c.consent,
       {viewer_accepts()} AS viewer_accepts, {candidate_accepts()} AS candidate_accepts,
       {blocks("v", "c")} AS viewer_blocks, {blocks("c", "v")} AS candidate_blocks
FROM (SELECT 1) AS one LEFT JOIN v ON true LEFT JOIN c ON true
"""
