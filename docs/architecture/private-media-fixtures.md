# P04.3 private media fixture semantics

This record defines the in-memory development substitute for F05. It is not
PostgreSQL atomicity, provider enforcement, a webhook or an active HTTP protocol.

## Ownership, versions and immutable identity

Every call captures owner, session generation, authority revision and current
media-policy version before asynchronous work. An account/session/consent/source
change invalidates earlier work. Selection bytes are copied before awaiting and
bound to the new asset and grant; caller mutation cannot change the upload.
The filename and declared MIME type never establish the content type.

The closed `MediaCollection` response exposes the aggregate revision needed by
ordering. Its empty initial version is 1. Each adopted asset transition or order
change advances the aggregate. `request_upload` and `reorder` compare
`CommandMeta.expected_version` with this revision. `remove` compares the target
asset version. Each F05 state transition advances its asset version. Reorder
requires exactly the current complete approved set, unique and owned; changing
the order advances affected asset versions and the collection revision.

Owner command idempotency binds owner, generation, action and key to canonical
command content, selected bytes and selection identity. Identical replay is
allowed only while its accepted result is still current. Changed payload is a
conflict. Provider/system/moderator fixture events use a separate event identity
with the same content-conflict and stale-result rules. There is no owner approval
or owner purge-confirmation method. The event controls are synthetic actors.

Accepted lifecycle records use clone → stage → validate → acknowledge adoption.
An invalid response, replaced authority, competing accepted mutation or cancelled
request cannot change accepted lifecycle state. Adapter acknowledgement checks
the exact staged response, context and revision. Reads never adopt state.
Local transfer attempts/progress/errors are transport observations, separate from
F05 lifecycle and from accepted approval/removal state.

An expired grant is terminal, including forced fixture expiry and actual clock
expiry. Retry reuses the immutable asset/bytes/grant binding with a fresh bounded
transfer attempt; it does not create another asset or lifecycle transition.
Replacement removes the expired pending asset and requests a new upload with a
new command, asset and grant identity. It does not invent a pending → pending
`upload_grant` transition. Late work from the former identity cannot consume the
replacement. Cancel is owner removal, followed by independently evidenced purge;
interruption leaves eligible pending work retryable in this process only.

## Provisional development policy and byte checks

`development-media-1` accepts PNG only, at most 1 MiB encoded, width/height at most
2048, at most 4,194,304 declared pixels, four live photos, a 60-second grant and
three transfer attempts. Removed/removal-pending assets cannot deliver. The
contract ceiling of twenty collection entries is a resource/history bound, not
the product photo limit. Retired local bytes are cleared on removal. Old removed
tombstones are retained within that bounded collection; a full collection requires
an explicit fresh fixture session. Idempotency retains at most 128 discretionary
operation receipts, plus separate reserved capacity for 20 owner removals and 20
provider purges, one of each per possible collection entry. Exhausting the
discretionary budget denies additional upload/order/review work while preserving
cleanup and replay evidence. Cleanup never consumes that discretionary budget;
no receipts are evicted. The total maximum is 168 retained receipts.

The local parser checks actual PNG signature, chunk framing/CRC, IHDR fields,
IDAT presence, terminal IEND and dimension/resource limits. It does not inflate
or decode pixels, sanitize image metadata, scan malware or prove server limits.
Safe decoding/transformation and metadata removal are explicitly simulated by
the system review fixture; original bytes never become a deliverable image.
Approved references identify non-delivering synthetic variants. PV04 and PV07
actual processing, private delivery and deletion remain open.

## F05 and revocation

Only provider upload completion moves upload_pending → quarantined. Only system
review moves quarantined → review_pending. Moderator approval/rejection requires
the current provisional policy; approval creates a synthetic approved reference.
Moderator restriction removes that reference and returns approved → review_pending.
Owner remove immediately withholds delivery; validated adoption enters
removal_pending. A failed or malformed removal response may leave the accepted
lifecycle approved, but its owner-removal revocation remains in force. Owner
removal and temporary moderation restriction have separate revocation records:
later moderator approval may clear only the moderation restriction. It cannot
undo an outstanding owner removal, restore candidate delivery or permit discovery
through that photo. Retained screens and reloads consume the same withheld
projection. Retrying owner removal and matching provider purge still work.

Both revocation records survive same-owner, same-generation suspension or session
expiry when the adapter retains that asset identity. They clear with owner or
generation replacement, or explicit full fixture reseeding that replaces the
collection. These records remain process-local; durable revocation is a P11 proof.

Provider purge alone enters removed. Failed, interrupted or exhausted purge stays
pending; duplicate/out-of-order events cannot complete another removal.

Profile integration consumes current approved owned assets. Photo approval alone
does not resolve chart, consent, adult, moderation or launch-policy requirements.
P05.1 derives pair preferences/blocks separately from owner readiness, using the
current approved collection as media source. It does not trust an earlier
approved row through an outstanding owner removal. The
[reciprocal mapping](reciprocal-eligibility-fixtures.md) requires matching
account/profile/asset identity and generation, current policy and reference.
Last-photo loss invalidates aggregate pair evidence and retained projection.
Current authority/pair evidence is rechecked before candidate delivery; media
approval alone is not pair permission.
Unknown/obsolete policy grants no upload or approved delivery permission. Same
session memory is the only recovery scope; private presentation clears on logout,
expiry or replacement. No real photos, database, provider, HDE or Railway object is
used or changed by this adapter.
