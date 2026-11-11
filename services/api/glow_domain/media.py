"""Photos (SV2's brief, D10; F05; G-02; OD-61; OD-62). Pure domain types and ports, independent of
Django.

Photos are objects in private Cloudflare R2 storage (OD-62), behind ports with **fixture adapters
only** in SV2: no R2 call, no credential, no SDK. P11 builds the R2 adapter and PV04's proof.

- ``StoragePort`` keeps and deletes objects: it issues the upload credential for a grant's key
  (which goes to no member in SV2), reads an object for processing, writes a processed variant,
  deletes an asset's objects, gives P11's delivery its reference for an approved variant, and
  delivers the store's events. **Its events reach the domain only through the port**, whose
  contract requires the adapter to authenticate each event before the domain sees it
  (``receive``: an event the adapter cannot authenticate is ``None`` and changes nothing). No
  member route can deliver one.
- ``ProcessingPort`` is the system review step's processing (Glow's own, OD-62: object storage
  keeps the bytes it is given): it reads the adopted original, checked against the completion's
  size and entity tag, decodes it within the policy's bounds, removes its metadata, re-encodes it
  and writes the variant under a new key. When it cannot make a variant it says why and writes
  none; an unavailable store raises ``StoreUnavailable`` and changes nothing.
- ``DetectionSeam`` is G-02's seam, between ``quarantined`` and ``review_pending``: every adopted
  upload passes it before the automated check sees it, given the variant, or the original when
  processing made none. SV2 configures none and records ``no_detector``; its outcome could send
  an asset to review, to a hold, or to a hold with a report, and SV2 builds only the route to
  review.
- ``PhotoCheckPort`` is the automated check (OD-61: no manual staff review, photos included), with
  no vendor: its fixture adapter approves nothing in the runtime, and a test drives it in its own
  setup. Its decisions are recorded with a ``system:`` subject.
- ``HoldPort`` answers whether a hold stops a path (a CyberTipline report asks for a year's
  preservation, USF-04; G-05's hold survives deletion). Every path SV2 builds that a hold must
  stop asks it first: approval, delivery and a removed asset's purge. SV2's fixture answers "no
  hold". A hold is its own record, not a ``MediaLifecycle`` state.

**Object keys** are Glow's own, random and opaque (``new_object_key``): 32 hexadecimal characters,
with no account, profile or asset ID, no filename and no member value, since keys show in the
store's logs and in the addresses P11 issues. The original and each variant have their own keys.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

UPLOAD_PENDING = "upload_pending"
QUARANTINED = "quarantined"
REVIEW_PENDING = "review_pending"
APPROVED = "approved"
REJECTED = "rejected"
REMOVAL_PENDING = "removal_pending"
REMOVED = "removed"
STATES: tuple[str, ...] = (
    UPLOAD_PENDING,
    QUARANTINED,
    REVIEW_PENDING,
    APPROVED,
    REJECTED,
    REMOVAL_PENDING,
    REMOVED,
)
# A photo that counts against the media policy's live photos (development-media-1: four).
LIVE: frozenset[str] = frozenset({UPLOAD_PENDING, QUARANTINED, REVIEW_PENDING, APPROVED})

# F05's registry (``flows-v1.json``), as SV2's writers make its transitions: (event, from) to
# (to, the registry's role). A test holds this table equal to the registry's F05 entries.
TRANSITIONS: dict[tuple[str, str], tuple[str, str]] = {
    ("upload_grant", "none"): (UPLOAD_PENDING, "owner"),
    ("uploaded", UPLOAD_PENDING): (QUARANTINED, "provider"),
    ("review", QUARANTINED): (REVIEW_PENDING, "system"),
    ("approve", REVIEW_PENDING): (APPROVED, "system"),
    ("reject", REVIEW_PENDING): (REJECTED, "system"),
    ("reorder", APPROVED): (APPROVED, "owner"),
    ("remove", APPROVED): (REMOVAL_PENDING, "owner"),
    ("remove", UPLOAD_PENDING): (REMOVAL_PENDING, "owner"),
    ("remove", REJECTED): (REMOVAL_PENDING, "owner"),
    ("remove", QUARANTINED): (REMOVAL_PENDING, "owner"),
    ("remove", REVIEW_PENDING): (REMOVAL_PENDING, "owner"),
    ("purged", REMOVAL_PENDING): (REMOVED, "provider"),
    ("restrict_media", APPROVED): (REVIEW_PENDING, "moderator"),
}

# The system subjects of the automated decisions (D10: written to ``StaffAudit`` with a
# ``system:`` subject, as D2's seed is).
CHECK_SUBJECT = "system:photo-check"
REVIEW_SUBJECT = "system:photo-review"
# The reason codes of the automated decisions.
APPROVED_BY_CHECK = "automated_check"
NO_VARIANT = "no_variant"
NO_DETECTOR = "no_detector"

KEY_HEX_CHARACTERS = 32


def next_state(event: str, before: str) -> str | None:
    """F05's state after ``event`` from ``before``, or ``None`` when the registry has no such
    transition (every unlisted transition is forbidden)."""
    found = TRANSITIONS.get((event, before))
    return None if found is None else found[0]


def new_object_key() -> str:
    """A new object key: Glow's own, random and opaque (D10)."""
    return secrets.token_hex(KEY_HEX_CHARACTERS // 2)


def new_reference() -> str:
    """A new opaque reference (an upload grant's ``grant_ref``): a letter or digit, then only
    letters, digits and ``._:-``, so it fits ``PolicyVersion``'s pattern and cannot hold an
    address (DM-57 U3)."""
    return "grant-" + secrets.token_hex(16)


class StoreUnavailable(Exception):
    """The store could not be reached. Not a processing failure: the step changes nothing and can
    run again (DM-57 U1). Its message is a code."""

    def __init__(self) -> None:
        super().__init__("store_unavailable")


@dataclass(frozen=True)
class UploadCompleted:
    """The store's report that an object was written at ``key`` (R2: an object-create event,
    through Queues), with its size and entity tag and when it was written."""

    event_id: UUID
    key: str
    byte_size: int
    entity_tag: str
    uploaded_at: datetime


@dataclass(frozen=True)
class ObjectDeleted:
    """The store's acknowledgment that the object at ``key`` is deleted (R2's object-delete
    events omit size and entity tag; the key is enough)."""

    event_id: UUID
    key: str


StorageEvent = UploadCompleted | ObjectDeleted


@dataclass(frozen=True)
class Bounds:
    """The policy's decoding bounds, from the version the asset's grant records."""

    types: tuple[str, ...]
    max_bytes: int
    max_width: int
    max_height: int
    max_pixels: int


@dataclass(frozen=True)
class Processed:
    """Processing's result: the variant's size when it wrote one at the key it was given, or the
    reason it made none (``original_mismatch``, ``not_decodable_within_bounds``)."""

    variant_size: int | None
    reason: str = ""


@dataclass(frozen=True)
class Detection:
    """G-02's seam's outcome: ``review`` (the only route SV2 builds), ``hold`` or
    ``hold_with_report``, and which detector decided (``no_detector`` in SV2)."""

    route: str
    detector: str


@dataclass(frozen=True)
class CheckDecision:
    """The automated check's decision: ``approve``, ``reject`` (with a reason code) or
    ``undecided``."""

    decision: str
    reason: str = ""


class StoragePort(Protocol):
    name: str

    def issue_upload(self, key: str, max_bytes: int, expires_at: datetime) -> object:
        """The store's upload credential for ``key`` (in P11 a time-limited signed upload
        address), which expires with the grant. It goes to no member in SV2 (DM-57 U3)."""

    def read(self, key: str) -> bytes | None:
        """The object at ``key``, or ``None``; ``StoreUnavailable`` when the store is down."""

    def write(self, key: str, data: bytes) -> int:
        """Writes ``data`` at ``key`` and returns its size; ``StoreUnavailable`` when down."""

    def delete(self, keys: tuple[str, ...]) -> None:
        """Asks the store to delete every object at ``keys``; each deletion is acknowledged later
        by an authenticated ``ObjectDeleted`` event."""

    def delivery_reference(self, key: str) -> str:
        """The opaque reference P11's authorized delivery uses for the variant at ``key``; never
        a public address, and never the key itself."""

    def receive(self, raw: object) -> StorageEvent | None:
        """The store's event, authenticated by the adapter, or ``None`` when it cannot be."""


class ProcessingPort(Protocol):
    def process(
        self,
        original_key: str,
        byte_size: int,
        entity_tag: str,
        bounds: Bounds,
        variant_key: str,
    ) -> Processed:
        """Processes the adopted original at ``original_key`` only, checked against its
        completion's size and entity tag, writing the variant at ``variant_key``."""


class DetectionSeam(Protocol):
    def inspect(self, asset_id: UUID, key: str) -> Detection:
        """G-02's detection step, given the variant's key, or the original's when processing
        made none."""


class PhotoCheckPort(Protocol):
    def decide(self, asset_id: UUID, variant_key: str | None) -> CheckDecision:
        """The automated check's decision on an asset in review."""


class HoldPort(Protocol):
    def held(self, asset_id: UUID) -> bool:
        """Whether a hold stops this asset's approval, delivery or purge."""


@dataclass(frozen=True)
class MediaPorts:
    storage: StoragePort
    processing: ProcessingPort
    detection: DetectionSeam
    check: PhotoCheckPort
    hold: HoldPort
