# P04.2 profile, preferences and visibility fixtures

This record describes **AP1-P04.2-001 revision 1.0** in the mobile development
runtime. The existing [production contracts](production-contracts.md), closed
schemas and F04/F06 in `packages/contracts/production/flows-v1.json` govern the
logical operations. This slice adds no HTTP route, production DTO, authentication
provider, database, media service or HDE calculation. Actual checks, review
dispositions and limitations belong to [P04.2 evidence](../testing/p04-2-checkpoint.md).

The P04.3 integration below records the combined runtime's later media source.
P05.1 separates owner readiness from current ordered-pair disclosure, as described
here and in [reciprocal eligibility fixtures](reciprocal-eligibility-fixtures.md).
Earlier boolean media/reciprocal seeds are not production evidence.

## Runtime, ownership and contract boundary

`apps/mobile/src/profiles/fixture-adapter.ts` supplies the explicit development-only
`ProfileAdapter` port. Its factory requires development plus `fixture` mode.
The adapter consumes generated `ProfileIntent`, `PreferencesIntent` and
`VisibilityIntent`, and returns generated `OwnProfile` or `OwnPreferences`.
`ProfileContext` binds each operation to the current owner, generation,
authority revision and app profile identity. The port is an in-process substitute
for later server behavior, not a second production wire protocol.

The adapter requires an active account and valid session for owner reads/writes.
Owner management is distinct from permission to enter discovery: loss of current
adult/consent evidence cannot grant visibility, but does not turn an owner editing
screen into another person's public view. Account/profile identifiers remain
distinct from engine/chart identities. No fixture creates an engine identifier.

New objects use expected version zero; edits require the existing object version.
The command's idempotency key follows the existing bounded identifier contract,
not a UUID-only rule. Replay is scoped to owner, generation, operation and profile.
The same identity with different command content is rejected. An old receipt
cannot restore an object whose accepted state has since changed. Canonical
command fields have an explicit order; preference selections/options keep their
submitted order, and text is not silently trimmed or normalized.

Mutation responses are staged until the current store validates and acknowledges
them. Malformed, stale or discarded results cancel staged state. This matters even
in memory: rejecting a response must not hide an accepted mutation that a later
read could revive. Adapter epoch and authority checks bracket delayed work; logout,
account replacement or changed authority invalidates earlier pending operations.

## Profiles and owner presentation

Only display name and summary enter a profile edit. The client cannot submit a
visibility, completeness, media, role or policy grant inside `ProfileIntent`.
The existing generated validators enforce the nonblank name limit of 80 Unicode
code points, a biography of exactly empty or nonblank up to 500 code points,
closed objects and valid Unicode. Whitespace-only text is not an empty biography.
Content is displayed through text components, not interpreted as HTML.

A saved empty biography is an incomplete draft. Saving valid text does not approve
photos, complete chart resolution, settle launch policy or silently activate the
old eligible-demo flag. The dashboard distinguishes saved profile, unsaved edits,
private preferences, remaining requirements and current visibility. Owner preview
shows accepted fields only; it never disguises an incomplete draft as a valid
candidate projection.

The routes are `/profile`, `/profile-edit`, `/preferences` and `/profile-preview`.
Ordinary onboarding reaches the owner area from `/remaining`; the recommendation
and explore surfaces also provide **Your profile and preferences**. Profile editing
supports **Save profile**, **Cancel edits**, **Leave and keep draft**, and
**Refresh saved details**. Preferences provide the corresponding save/cancel/leave
controls. Drafts are same-session memory and are separate from accepted records;
cancel returns to current accepted values, while ordinary navigation preserves
deliberate unfinished edits. The mounted navigator and P04.1 recovery form remain
outside draft replacement.

`apps/mobile/src/profiles/store.ts` owns the accepted records and private drafts;
retained screens do not keep a second private form copy. Source adoption compares
name and biography independently: untouched fields refresh from accepted source,
while deliberately edited fields remain for review. Preferences refresh when the
draft still equals its previous accepted value; deliberate changes remain.
Monotonic draft revisions bind edit/save/cancel callbacks to the current source.
Owner/generation replacement and invalid account/session authority clear the owner
presentation and private drafts. Account/consent source changes invalidate pending
operations without remounting the navigator.

Busy/error/status feedback is shared with the existing accessible screen primitives.
The form avoids a native `maxLength` cutoff, which counts UTF-16 units differently
from the contract's Unicode code-point limit; contract validation supplies the
actual acceptance rule. Source-level labels, focus handling, minimum touch targets
and flexible-height text do not substitute for native accessibility testing.

## Explicit provisional preference catalog

`apps/mobile/src/profiles/policy.ts` defines the following synthetic catalog:

| Item | Exact fixture value |
|---|---|
| Policy version | `development-preferences-1` |
| Dimension | `demo_connection` |
| Dimension label | Demonstration connection preference |
| Options | `demo_a` / Demo option A; `demo_b` / Demo option B |

These labels are test vocabulary only. They select no launch geography,
gender/orientation taxonomy, production reciprocal rule or other A05 commitment.
The screen labels them **PROVISIONAL PREVIEW CHOICES** and explains that launch
preferences and matching rules remain unselected.

The contract permits at most 20 selections and 50 unique option IDs per selection.
The semantic parser rejects duplicate dimensions in addition to schema checks;
the fixture catalog rejects unknown dimensions and options. Eligibility requires
the current policy version and a nonempty choice for every current fixture
dimension. Shape validation alone cannot establish policy acceptance. Changed or
unavailable policy disables saving from an obsolete form and denies discovery.
Preferences are always private owner data.

Saving preferences invalidates current pair evidence through the accepted
preference and aggregate source versions. P05.1 independently compares each
person's supplied attribute with the other's current accepted set. It does not
require a fictional reciprocal-approval flag for owner profile readiness. Editing
preferences cannot manufacture a match or contact permission.

## Completeness and F04/F06 transitions

The fixture checks current account/session, adult status, consent, saved profile,
nonempty biography, known/current preference policy, configured preferences,
current approved-media evidence, chart evidence and moderation evidence. P05.1
removes the circular reciprocal-preference requirement from owner readiness:
a complete profile need not have a currently compatible candidate. Missing
requirements remain visible to the owner.
Ordinary profile/preferences editing cannot satisfy the unresolved provider/media
parts of that list.

| Operation | Allowed behavior |
|---|---|
| F04 incomplete edit | Remains incomplete unless all current fixture requirements permit completion |
| F04 completion | Incomplete → visible only with current eligibility and the explicit development policy |
| F04 paused edit | Remains paused |
| F04 visible edit | Remains visible only while eligible; otherwise becomes incomplete |
| F04 preference save | Configures private preferences under the current policy; invalidates prior ordered-pair evidence without requiring a compatible candidate for owner readiness |
| F06 pause | Visible → paused; discovery and candidate preview become unavailable |
| F06 resume | Paused → visible only after a fresh complete eligibility/policy check |
| F04 system removal | Deletion-pending/deleted account authority removes the profile; no owner removal grant is added |

Wrong owner/object, stale versions and unlisted owner visibility transitions are
denied. Restriction cannot be undone by an owner edit or delayed completion.
Suspension denies owner access and clears private presentation without inventing
an unlisted F04 profile-state transition. System deletion changes only the listed
source states to removed, once. The dashboard and owner preview show blocked
effective visibility when saved visibility is visible but current disclosure is
denied. Resume does
not restore a historical match/contact grant. Contact is unimplemented and grants
no permission under the unresolved pause/contact policy.

## Fictional eligible scenario and projection

The explicit eligible development scenario seeds a fictional profile, preferences,
synthetic media/chart/moderation and independent viewer/pair facts. This is the bounded way
to exercise visible → paused → visible without representing ordinary onboarding
as having completed media or HDE work. The fixture profile is named **Alex**, with
summary **A fictional profile for the visibility demonstration.** It starts at
version 1, uses option `demo_a`, and has a non-delivering synthetic media reference.
It is not an actual approved upload, resolved birth chart or production policy.
The private birth input retains its original uncertainty and unresolved provenance.

Candidate projection uses the `CandidateProfile` allowlist: profile ID, display
name, age, summary, media-delivery references and compatibility projection. The
demonstration projection derives age from current fictional private birth date
and injected clock: **36** for 1990-06-15 on 2026-09-23. P05.1 computes a different
age when those inputs differ; there is no general fixed-age fallback. Current
approved synthetic references come from P04.3 media integration; compatibility
remains **unavailable**. These references are not provider URLs or live grants.
The candidate payload contains no birth date.

Email, birth date/time/place, precise location, preferences, engine identifiers,
internal policy/moderation reasons and owner object versions are excluded.
The projection helper constructs these fields explicitly and validates the closed
contract; that validation does not itself authorize disclosure. The separate
candidate-preview gate requires current eligible viewer/object state. The UI labels
the resulting view **FICTIONAL ELIGIBLE VIEWER PREVIEW**. Owner preview alone proves
neither candidate authorization nor public visibility.

The eligible scenario supplies an independent fictional viewer record. P05.1
binds viewer ID, candidate profile ID, generation, discovery revision and complete
ordered pair vector. Both people need current account/access, adult, consent,
completeness, visibility and moderation facts; each preference direction is
calculated and each block direction explicitly observed. The owner record uses
accepted profile/preferences/media and private birth/consent authority. The
[pair mapping](reciprocal-eligibility-fixtures.md) owns exact predicates/policy.
Neither an old reciprocal marker nor `bothBlocksClear` authorizes this path.
A stale/different context denies disclosure even when the candidate DTO is valid.
These remain fictional facts, not real-person evidence.

## Revocation, retained UI and development controls

Profile source, preference source, policy, media and reciprocal-evidence changes
have separate development controls. They are clearly labeled synthetic and preserve
navigation so retained-form reconciliation can be exercised. The profile outcome
panel exposes **Success**, **Temporary error**, **Invalid response** and
**Version conflict**. These are local error-path fixtures, not provider responses.

Pause immediately denies discovery while its result is pending; a failed pause
remains locally blocked until a successful pause and fresh resume. Request payload
and context are copied before asynchronous work, preventing a caller from changing
the operation during a delay. Exact consent/policy revisions bind retained form
callbacks. Owner changes publish cleared private records and drafts atomically.
UI snapshots explicitly project their presentation fields and omit internal
fixture policy/evidence objects.

Pause, missing completeness, changed preferences/policy/consent, restriction,
expiry and deletion invalidate relevant current recommendations and pending
permission-granting work. Existing recommendation surfaces remain bounded fixture
presentation; P04.2 does not implement the rest of P05, matching or contact.
Direct links, Back and hidden screens still require current owner/route authority.
No profile or preferences are passed as route parameters or logged as routine
diagnostics. No browser storage, SQLite, shadow backend or process-restart recovery
is introduced.

`use-recommendations.ts` binds loaded results to owner/generation, the current
profile discovery revision and P05.1's captured ordered pair version. It masks
obsolete results synchronously during render,
then aborts obsolete requests and rejects delayed completions against the live
state. This also applies to retained hidden screens; waiting only for effect cleanup
would allow a render of an earlier owner's or revoked candidate list. The hook
retains its existing configured-API error/retry behavior without falling back to
bundled fixtures after an API failure.

The hook's existing `gapp-dev-v1` Alex/Jordan/Riley items remain static smoke/layout
samples. They are gated as retained presentation by the fictional viewer → owner
pair, not evaluated as three independently eligible pairs. `candidatePreview()`
is the fact-derived P05.1 projection; P05.2 owns bounded discovery composition.
Pair-only revocation can redact retained data while owner readiness and editing
stay available. No new navigation, queue or ranking feature is implied.

## P04.3 integration with the media collection

The combined onboarding store now owns `MediaStore` and binds the profile store
to `media.approvedCollection()`. Its media-change callback runs
`profiles.synchronizeMedia(collection)`. The standalone P04.2 adapter's synthetic
seed remains for its isolated fixtures, but the combined runtime derives media
evidence from current owned approved assets with an approved delivery reference.
The owner cannot set that evidence through a profile edit.

`approvedCollection()` also checks the active owner, adult/consent authority and
current `development-media-1` policy, and filters local revocations. The profile
adapter replaces `media_ids` with that current ordered set and derives its media
requirement from whether at least one remains. Synchronization invalidates pending
profile commands, advances profile authority/object and discovery revisions, and
preserves existing saved visibility. A source change therefore can leave saved
visibility `visible` while effective disclosure is blocked. It does not invent
an F04/F06 transition. Explicit `paused` remains paused through media changes;
resume still requires a fresh check of every eligibility condition.

Removal and moderator restriction revoke the affected reference before awaiting
completion. Losing the last eligible photo blocks completeness/discovery and
invalidates retained candidate/recommendation contexts and pending resume work.
Other valid approved photos can still satisfy the provisional media requirement.
Reordering updates the ordered source; it cannot approve an asset or restore a
removed one. Revocation does not claim that provider bytes were purged.

`candidatePreview()` rereads the live approved collection and requires its ordered
IDs to equal the accepted profile's `media_ids`, in addition to the existing current
viewer/object checks. It projects only those approved references. These references
are non-delivering fixture strings; the screen displays **Approved synthetic photo**
placeholders, not private originals or URLs. The earlier P04.2 empty-reference
projection is therefore superseded in the combined runtime, while compatibility
remains unavailable and all private-field exclusions above remain in force.

The explicit eligible scenario seeds an approved synthetic asset alongside
fictional profile/preferences/chart/moderation and independent viewer facts.
Ordinary upload/review cannot create those unrelated prerequisites. P05.1 derives
pair preferences and block observations separately from owner completeness.
Local PNG checks establish container structure and bounds only; safe decoding,
metadata removal, actual moderation/delivery/purge and native byte reading remain
unverified. See [media semantics](private-media-fixtures.md),
[provider mapping](media-provider-mapping.md) and the
[mobile walkthrough](../../apps/mobile/README.md). This section records inspected
source behavior, not a rendered-suite or production acceptance result.

## Evidence limits and next boundary

The [mobile walkthrough](../../apps/mobile/README.md) supplies reproduction steps;
the [checkpoint](../testing/p04-2-checkpoint.md) records actual commands/results,
review dispositions and which evidence ran locally or in hosted CI. This document
describes implementation and does not claim that a suite passed merely because
its cases exist.

P04.3 owns media upload/quarantine/retry/order/delete. P05.1 owns reciprocal
fixture eligibility; P05.2/P05.3 retain discovery/matching. A05 owns launch/product
policy. P11 owns real authentication,
persistence, transactions/concurrency, server authorization, provider enforcement,
backup/restore and final integration. Browser tests and iOS/Android development
JavaScript exports do not prove signed native builds, device layout, keyboard,
screen-reader behavior, secure storage or cross-device recovery. Existing API
startup guards, dummy backend, liveness 200/readiness 503, disabled billing and
no-real-provider-fallback behavior remain required.
