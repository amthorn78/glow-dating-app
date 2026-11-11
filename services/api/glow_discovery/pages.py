"""Recommendations and broader discovery (the SV3 brief's D6 and D7; F07), each page one
transaction.

**A page with no cursor** creates the viewer's batch for the collection (``create``), in one
transaction that:

1. locks the viewer's account row ``FOR UPDATE`` first (DM-13 4.1; an account that is not ``active``
   is refused), so two of the viewer's pages, and every writer of a fact of the viewer's, serialize;
2. takes the settings the selection reads (``policy.SELECTION_SETTINGS``) under their pointers'
   ``FOR SHARE`` locks, all in its first ``read_shared`` call, in name order (D19), then reads the
   time from ``clock_timestamp()`` (the server's UTC date, D4);
3. refuses a viewer who fails a predicate (``forbidden``): no batch, no selection and no
   recommendation is computed for them (D3; UST-41, USF-11);
4. selects up to 100 candidates in **one statement** (``predicates.SELECTION``: every predicate of
   D3 to D5, consumption, and for broader discovery the viewer's current recommendations batch's
   candidates left out), ordered by the keyed tie-break (D6, Q2), so it reads one snapshot (D2);
5. for recommendations, asks the compatibility port for each selected pair (none when nothing was
   selected: F07's "no eligible candidates returns empty and no provider call"): a ready pair is
   ranked by its band, then the tie-break; an ``unsupported`` pair is left out of recommendations
   only; any ``unavailable`` or ``pending`` result makes the batch ``unavailable`` or ``pending``
   (with no items), and broader discovery still serves its candidates. No port selected (the
   runtime's case) is ``unavailable``;
6. deletes the viewer's earlier batch of that collection, with its entries, and writes the new one
   with its entries and the candidates' versions (D7, Q5's bound): one batch per viewer and
   collection (``batch_one_per_collection``).

**A page with a cursor** (``continue_page``) holds the viewer's account row ``FOR SHARE`` and the
same pointers ``FOR SHARE``, then refuses with the generic stale response (``stale_version``, the
same whatever the cause, D8) a cursor not issued to this viewer for this collection, a missing
(deleted) batch, another viewer's or collection's batch, a batch that is not ``ready`` (Stage B's
consumption makes it ``stale``), an expired batch, and a batch whose viewer versions or policy
version no longer match (Q4). It then rechecks every entry from the cursor's offset in **one
statement** (``predicates.RECHECK``; DM-60 Q1): every predicate and consumption again, both block
directions for every entry (a block bumps only its actor's ``blocks_version``), so a candidate made
ineligible, blocked, matched, liked or passed since the batch was built is dropped. It writes
nothing.

**Photos** (D13; F05): each card's ``media_delivery_refs`` are the candidate's approved photos, in
their order, each through SV2's ``delivery_reference`` (approved variants only, asking the hold port
first), read after the page's transaction, since that read runs its own; one that is no longer
deliverable gives no reference.

Nothing here logs or returns a birth date, a coordinate, an area ID, a distance, a "show me" set, a
filter, a count or a reason (D8, D17).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID, uuid4

from glow_discovery import contract, keys, policy, predicates
from glow_discovery.eligibility import parameters
from glow_domain.chat import TransactionProbe
from glow_domain.compatibility import CompatibilityRequest, CompatibilityStatus
from glow_domain.identity import AccountId, ChartMapping, ChartMappingState, EngineChartReference
from glow_persistence.models import AppAccount, RecommendationBatch, RecommendationEntry
from glow_profiles import media, settings_store
from glow_profiles.tx import (
    FORBIDDEN,
    STALE_VERSION,
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

STALE = "stale"


@dataclass(frozen=True)
class Viewer:
    eligible: bool
    versions: tuple[int, int, int]
    chart: tuple[Any, ...]


def _selection(tx: Tx) -> policy.Selection:
    # D19: every pointer the selection reads, in this transaction's first read_shared call.
    found = settings_store.read_shared(tx, policy.SELECTION_SETTINGS)
    return policy.selection(found, utc_date(clock(tx)))


def _viewer(tx: Tx, account_id: UUID, selection: policy.Selection) -> Viewer:
    tx.cursor.execute(predicates.VIEWER, parameters(selection, account_id))
    row = tx.cursor.fetchone()
    if row is None:
        return Viewer(False, (0, 0, 0), (None, None, None, None))
    return Viewer(row[0] is True, (int(row[1]), int(row[2]), int(row[3])), tuple(row[5:9]))


def _rows(
    tx: Tx, statement: str, values: dict[str, Any], names: tuple[str, ...]
) -> list[dict[str, Any]]:
    tx.cursor.execute(statement, values)
    found: list[dict[str, Any]] = []
    for row in tx.cursor.fetchall():
        found.append(dict(zip(names, row, strict=False)))
    return found


def _mapping(account_id: UUID, chart: tuple[Any, ...]) -> ChartMapping | None:
    state, reference, version, birth_version = chart
    if state is None or version is None or birth_version is None:
        return None
    resolved = state == ChartMappingState.RESOLVED.value and reference is not None
    return ChartMapping(
        AccountId(str(account_id)),
        ChartMappingState.RESOLVED if resolved else ChartMappingState.PENDING,
        EngineChartReference(str(reference)) if resolved else None,
        str(birth_version),
        str(version),
    )


def _recommend(
    viewer_id: UUID, viewer: Viewer, rows: list[dict[str, Any]], selection: policy.Selection
) -> tuple[str, list[dict[str, Any]]]:
    """D6: the batch's state and its ranked entries."""
    if not rows:
        return "empty", []
    port = policy.compatibility_port()
    if port is None:
        return "unavailable", []
    viewer_map = _mapping(viewer_id, viewer.chart)
    statuses: set[CompatibilityStatus] = set()
    ranked: list[tuple[int, bytes, dict[str, Any]]] = []
    for row in rows:
        candidate_map = _mapping(row["account_id"], row["chart"])
        if viewer_map is None or candidate_map is None:
            statuses.add(CompatibilityStatus.PENDING)
            continue
        result = port.evaluate_pair(
            CompatibilityRequest(viewer_map, candidate_map, selection.version)
        )
        statuses.add(result.status)
        rank = policy.band(result)
        if rank is not None:
            ranked.append((rank, bytes(row["tie_break"]), row))
    if CompatibilityStatus.UNAVAILABLE in statuses:
        return "unavailable", []
    if CompatibilityStatus.PENDING in statuses:
        return "pending", []
    ranked.sort(key=lambda item: (item[0], item[1]))
    entries = [row for _, _, row in ranked]
    return ("ready" if entries else "empty"), entries


def _current_recommendations(
    account_id: UUID, versions: tuple[int, int, int], selection: policy.Selection, now: Any
) -> UUID | None:
    """The viewer's current recommendations batch (D6): ready, unexpired and built under the
    viewer's current versions and policy version; broader discovery leaves its candidates out."""
    batch = RecommendationBatch.objects.filter(
        account_id=account_id, collection=policy.RECOMMENDATIONS
    ).first()
    if batch is None or not _fresh(
        batch, account_id, policy.RECOMMENDATIONS, versions, selection, now
    ):
        return None
    return UUID(str(batch.id))


def _fresh(
    batch: Any,
    account_id: UUID,
    collection: str,
    versions: tuple[int, int, int],
    selection: policy.Selection,
    now: Any,
) -> bool:
    return bool(
        batch.account_id == account_id
        and batch.collection == collection
        and batch.state == "ready"
        and batch.expires_at > now
        and (
            int(batch.eligibility_version),
            int(batch.preferences_version),
            int(batch.blocks_version),
        )
        == versions
        and batch.policy_version == selection.version
    )


def _cards(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The rows that can be shown as cards (D13), with their details; the photos come later."""
    found: list[dict[str, Any]] = []
    for row in rows:
        shown = contract.details(row["fields"], row["area_name"])
        if shown is not None:
            found.append({**row, "details": shown})
    return found


def create(
    account_id: UUID, collection: str, limit: int, *, probe: TransactionProbe | None = None
) -> Result:
    def body(tx: Tx) -> Result:
        lock_account(tx, account_id)
        selection = _selection(tx)
        now = clock(tx)
        viewer = _viewer(tx, account_id, selection)
        if not viewer.eligible:
            raise Refused(FORBIDDEN, "viewer_not_eligible")
        batch_id = uuid4()
        exclude = (
            _current_recommendations(account_id, viewer.versions, selection, now)
            if collection == policy.DISCOVERY
            else None
        )
        values = parameters(selection, account_id)
        values.update(batch=str(batch_id), exclude_batch=exclude, limit=policy.BATCH_LIMIT)
        signal(tx.probe, "before_selection")
        rows = _rows(
            tx,
            predicates.SELECTION,
            values,
            (
                *predicates.CARD_NAMES,
                "chart_state",
                "chart_reference",
                "chart_version",
                "chart_birth",
                "tie_break",
            ),
        )
        for row in rows:
            row["chart"] = (
                row.pop("chart_state"),
                row.pop("chart_reference"),
                row.pop("chart_version"),
                row.pop("chart_birth"),
            )
        if collection == policy.RECOMMENDATIONS:
            state, entries = _recommend(account_id, viewer, rows, selection)
        else:
            state, entries = ("ready" if rows else "empty"), rows
        # D7 (Q5's bound): one batch per viewer and collection; the earlier one goes, with its
        # entries, in this transaction.
        RecommendationBatch.objects.filter(account_id=account_id, collection=collection).delete()
        batch = RecommendationBatch.objects.create(
            id=batch_id,
            account_id=account_id,
            collection=collection,
            eligibility_version=viewer.versions[0],
            preferences_version=viewer.versions[1],
            blocks_version=viewer.versions[2],
            policy_version=selection.version,
            limit=policy.BATCH_LIMIT,
            state=state,
            expires_at=now + policy.BATCH_LIFETIME,
        )
        RecommendationEntry.objects.bulk_create(
            [
                RecommendationEntry(
                    batch=batch,
                    candidate_id=row["account_id"],
                    position=position,
                    candidate_eligibility_version=int(row["eligibility_version"]),
                    candidate_preferences_version=int(row["preferences_version"]),
                    candidate_blocks_version=int(row["blocks_version"]),
                )
                for position, row in enumerate(entries)
            ]
        )
        shown = _cards(entries[:limit]) if state == "ready" else []
        following = (
            keys.cursor(account_id, collection, batch_id, limit)
            if state == "ready" and len(entries) > limit
            else None
        )
        return Result(
            "applied",
            data={
                "page": dict(
                    collection=collection,
                    batch_id=str(batch_id),
                    version=int(batch.version),
                    state=state if shown or state != "ready" else "empty",
                    next_cursor=following if shown else None,
                    expires_at=batch.expires_at,
                ),
                "rows": shown,
            },
        )

    return _with_photos(run(body, probe))


def continue_page(
    account_id: UUID,
    collection: str,
    cursor: str,
    limit: int,
    *,
    probe: TransactionProbe | None = None,
) -> Result:
    def body(tx: Tx) -> Result:
        read_account_shared(tx, account_id)
        selection = _selection(tx)
        now = clock(tx)
        named = keys.read_cursor(cursor, account_id, collection)
        if named is None:
            raise Refused(STALE_VERSION, f"{STALE}:cursor")
        batch_id, offset = named
        batch = RecommendationBatch.objects.filter(pk=batch_id).first()
        account = (
            AppAccount.objects.filter(pk=account_id)
            .values_list("eligibility_version", "preferences_version", "blocks_version")
            .first()
        )
        if batch is None or account is None:
            raise Refused(STALE_VERSION, f"{STALE}:batch")
        versions = (int(account[0]), int(account[1]), int(account[2]))
        if not _fresh(batch, account_id, collection, versions, selection, now):
            raise Refused(STALE_VERSION, f"{STALE}:batch")
        if not _viewer(tx, account_id, selection).eligible:
            raise Refused(FORBIDDEN, "viewer_not_eligible")
        values = parameters(selection, account_id)
        values.update(batch_id=batch_id, offset=offset, limit=limit + 1)
        signal(tx.probe, "before_recheck")
        rows = _rows(tx, predicates.RECHECK, values, ("position", *predicates.CARD_NAMES))
        shown = _cards(rows[:limit])
        following = (
            keys.cursor(account_id, collection, batch_id, int(rows[limit]["position"]))
            if len(rows) > limit and shown
            else None
        )
        return Result(
            "read",
            data={
                "page": dict(
                    collection=collection,
                    batch_id=str(batch_id),
                    version=int(batch.version),
                    state="ready" if shown else "empty",
                    next_cursor=following,
                    expires_at=batch.expires_at,
                ),
                "rows": shown,
            },
        )

    return _with_photos(run(body, probe))


def _with_photos(result: Result) -> Result:
    """The page's cards with their photos' delivery references (D13; F05), each through SV2's
    ``delivery_reference``, after the page's transaction."""
    if not result.ok or result.data is None:
        return result
    items: list[dict[str, Any]] = []
    for row in result.data["rows"]:
        refs: list[str] = []
        for asset_id in row["media_ids"] or ():
            delivered = media.delivery_reference(UUID(str(asset_id)))
            reference = delivered.detail.get("delivery_ref") if delivered.ok else None
            if isinstance(reference, str):
                refs.append(reference)
        items.append(contract.card(row, refs))
    page = contract.page(items=items, **result.data["page"])
    return Result(result.outcome, data=page, trace=result.trace, events=result.events)


def page(account_id: UUID, request: dict[str, Any]) -> Result:
    """F07: a ``PageRequest`` for the actor's own collection."""
    collection, cursor, limit = request["collection"], request["cursor"], int(request["limit"])
    if cursor is None:
        return create(account_id, collection, limit)
    return continue_page(account_id, collection, cursor, limit)
