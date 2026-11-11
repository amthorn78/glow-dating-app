"""The media ports' fixture adapters (the SV2 brief's D10; OD-62): process memory only. No R2 call,
no credential, no SDK and no decoder; P11 builds the R2 adapter, the processor and PV04's proof.

- ``FixtureStorage`` keeps objects in this process's memory, by key. Its upload credential is an
  opaque fixture token that goes to no member (DM-57 U3). ``put`` stands in for a client's upload
  with that credential and ``acknowledge`` for the store's deletion of an object it was asked to
  delete; each issues an event, as R2's event notifications reach a consumer through Queues.
  **It authenticates its events** (``receive``): only an event it issued itself, unchanged, is
  returned to the domain; any other value is ``None`` and changes nothing. A test calls ``put``
  and ``acknowledge`` in its own setup; no route does. ``unavailable`` stands in for a store that
  cannot be reached.
- ``FixtureProcessing`` simulates the system review step's processing, as P04.3's fixture does
  (``private-media-fixtures.md``): it reads only the object at the key it is given, checks it
  against the completion's size and entity tag (an MD5 hex digest, R2's entity tag of a single-part
  upload), checks the PNG signature, the ``IHDR`` chunk and its CRC, a terminal ``IEND`` and the
  policy's bounds on the declared dimensions, pixels and bytes. It does **not** inflate or decode
  pixels or strip metadata: no decoder or image library exists here (D14; DM-57: a real decode
  path is PV04's). Its "variant" is synthetic, non-image bytes derived from the original's digest,
  written under the new key it is given: it identifies a non-delivering synthetic variant.
- ``NoDetector`` is G-02's seam with no detector configured: every asset goes to review, recorded
  as ``no_detector``.
- ``FixtureCheck`` approves nothing in the runtime: it is always ``undecided``. A test drives the
  check with its own adapter in its own setup.
- ``NoHold`` answers "no hold".
"""

from __future__ import annotations

import hashlib
import secrets
import struct
import threading
import zlib
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from glow_domain import media as md

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PNG_END = b"\x00\x00\x00\x00IEND\xaeB`\x82"


def etag_of(data: bytes) -> str:
    """The fixture's entity tag: the MD5 hex digest of the bytes (not a security function)."""
    return hashlib.md5(data, usedforsecurity=False).hexdigest()


def png_dimensions(data: bytes) -> tuple[int, int] | None:
    """The declared width and height of a PNG's framing, or ``None``: its signature, a first
    ``IHDR`` chunk of 13 bytes with a matching CRC and nonzero dimensions, and a terminal
    ``IEND``. Nothing is inflated or decoded."""
    if len(data) < 8 + 25 + 12 or not data.startswith(PNG_SIGNATURE) or not data.endswith(PNG_END):
        return None
    length, kind = struct.unpack(">I4s", data[8:16])
    if kind != b"IHDR" or length != 13:
        return None
    body = data[16:29]
    (crc,) = struct.unpack(">I", data[29:33])
    if zlib.crc32(kind + body) & 0xFFFFFFFF != crc:
        return None
    width, height = struct.unpack(">II", body[:8])
    if width == 0 or height == 0:
        return None
    return width, height


@dataclass(frozen=True)
class FixtureCredential:
    """The fixture's upload credential for one key: an opaque token, never given to a member."""

    key: str
    max_bytes: int
    expires_at: datetime
    token: str


@dataclass
class FixtureStorage:
    name: str = "fixture"
    unavailable: bool = False
    objects: dict[str, bytes] = field(default_factory=dict)
    credentials: dict[str, FixtureCredential] = field(default_factory=dict)
    deletions: list[str] = field(default_factory=list)
    reads: list[str] = field(default_factory=list)
    # Each delivery reference issued, and the key it was issued for (a test reads it).
    references: dict[str, str] = field(default_factory=dict)
    _issued: dict[UUID, md.StorageEvent] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    # -- the port ---------------------------------------------------------------------------

    def issue_upload(self, key: str, max_bytes: int, expires_at: datetime) -> object:
        credential = FixtureCredential(key, max_bytes, expires_at, secrets.token_hex(16))
        with self._lock:
            self.credentials[key] = credential
        return credential

    def read(self, key: str) -> bytes | None:
        if self.unavailable:
            raise md.StoreUnavailable()
        with self._lock:
            self.reads.append(key)
            return self.objects.get(key)

    def write(self, key: str, data: bytes) -> int:
        if self.unavailable:
            raise md.StoreUnavailable()
        with self._lock:
            self.objects[key] = bytes(data)
        return len(data)

    def delete(self, keys: tuple[str, ...]) -> None:
        if self.unavailable:
            raise md.StoreUnavailable()
        with self._lock:
            self.deletions.extend(keys)

    def delivery_reference(self, key: str) -> str:
        # An opaque reference, never the key and never an address (P11 issues the address).
        reference = "delivery-" + secrets.token_hex(16)
        with self._lock:
            self.references[reference] = key
        return reference

    def receive(self, raw: object) -> md.StorageEvent | None:
        if not isinstance(raw, md.UploadCompleted | md.ObjectDeleted):
            return None
        with self._lock:
            issued = self._issued.get(raw.event_id)
        return raw if issued == raw else None

    # -- the simulated client and store (a test's setup calls these; no route does) -----------

    def put(
        self, key: str, data: bytes, *, uploaded_at: datetime | None = None
    ) -> md.UploadCompleted:
        """A client's upload to ``key`` and the store's completion event for it."""
        with self._lock:
            self.objects[key] = bytes(data)
        event = md.UploadCompleted(
            uuid4(), key, len(data), etag_of(data), uploaded_at or datetime.now(UTC)
        )
        self._issue(event)
        return event

    def acknowledge(self, key: str) -> md.ObjectDeleted:
        """The store's deletion of the object at ``key`` and its acknowledgment event."""
        with self._lock:
            self.objects.pop(key, None)
        event = md.ObjectDeleted(uuid4(), key)
        self._issue(event)
        return event

    def _issue(self, event: md.StorageEvent) -> None:
        with self._lock:
            self._issued[event.event_id] = event


@dataclass
class FixtureProcessing:
    storage: FixtureStorage

    def process(
        self,
        original_key: str,
        byte_size: int,
        entity_tag: str,
        bounds: md.Bounds,
        variant_key: str,
    ) -> md.Processed:
        data = self.storage.read(original_key)
        if data is None or len(data) != byte_size or etag_of(data) != entity_tag:
            return md.Processed(None, "original_mismatch")
        dimensions = png_dimensions(data)
        if dimensions is None or "image/png" not in bounds.types:
            return md.Processed(None, "not_decodable_within_bounds")
        width, height = dimensions
        if (
            len(data) > bounds.max_bytes
            or width > bounds.max_width
            or height > bounds.max_height
            or width * height > bounds.max_pixels
        ):
            return md.Processed(None, "not_decodable_within_bounds")
        variant = b"fixture-variant:" + hashlib.sha256(data).hexdigest().encode("ascii")
        return md.Processed(self.storage.write(variant_key, variant))


class NoDetector:
    def inspect(self, asset_id: UUID, key: str) -> md.Detection:
        return md.Detection("review", md.NO_DETECTOR)


class FixtureCheck:
    def decide(self, asset_id: UUID, variant_key: str | None) -> md.CheckDecision:
        # The runtime's check approves nothing (D10).
        return md.CheckDecision("undecided")


class NoHold:
    def held(self, asset_id: UUID) -> bool:
        return False


_STORAGE = FixtureStorage()


def default_storage() -> FixtureStorage:
    """This process's fixture store, which the default ports use."""
    return _STORAGE


def default_ports() -> md.MediaPorts:
    return md.MediaPorts(
        storage=_STORAGE,
        processing=FixtureProcessing(_STORAGE),
        detection=NoDetector(),
        check=FixtureCheck(),
        hold=NoHold(),
    )
