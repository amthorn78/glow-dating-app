# P05.2 bounded discovery fixtures

**AP1-P05.2-001 revision 1.0.** This application composition joins current
reciprocal eligibility, the existing provider seam and finite recommendation and
broader-discovery presentation. It is development/test-only and nonpersistent.
The [checkpoint](../testing/p05-2-checkpoint.md) records observed validation;
existence of source or a test case is not a pass receipt.

## One policy and explicit data provenance

Python's [trusted eligibility service](trusted-eligibility.md), raw-fact
[reciprocal eligibility mapping](reciprocal-eligibility-fixtures.md) and existing
`FixtureCompatibilityBatchService` remain the server-side behavioral authority.
`services/api/glow_domain/discovery.py` composes these seams;
`discovery_fixtures.py` supplies its explicit fixture root. It is not registered
as an HTTP route. The mobile in-memory adapter reuses the existing TypeScript
raw-fact evaluator and shared cases as a development presentation substitute.
It is not a second backend or a production authorization source. Mobile
`metro.config.js` extends Expo defaults with the canonical fixture directory as
a watch folder; it does not create a duplicate fixture catalog or change locks.

Both implementations consume
[`discovery-v1.json`](../../packages/contracts/fixtures/discovery-v1.json), a
heterogeneous **14-candidate** fictional population with distinct account/profile
identities, raw current facts, approved-media records, directional block
observations and provider/mapping scenarios. Six candidates are eligible in the
canonical control; eight are paused, deleted, restricted, blocked in either
direction, reciprocally incompatible, missing media or missing facts. Explicit
expected outcomes and ordering are test oracles, never runtime authorization.
The existing 141-row reciprocal corpus remains the reusable decision conformance
source; discovery does not copy its rules into a new evaluator.

The mobile viewer comes from the current owner/session's accepted profile,
preferences, consent, account and media authority. The old fictional
viewer-to-owner preview pair does not authorize the new population. Each actual
viewer/candidate pair receives its own current acquisition and reciprocal
assessment. Owner readiness remains separate from candidate compatibility;
ordinary onboarding stays incomplete when chart, policy or other facts are
unresolved. Explicit eligible scenarios contain fictional prerequisites only.

The anonymous `GET /api/v1/development/recommendations` still serves the earlier
Alex/Jordan/Riley layout/smoke contract without actor credentials. The actual
recommendation/broader journey does not use those records as queue membership.
The existing HTTP loader remains for vertical smoke and transport conformance;
no authenticated discovery endpoint, write endpoint or live provider is added.
Configured transport failure must not silently become successful fallback data.

## Synthetic ordering and finite work

Both modes apply identical eligibility and disclosure rules to the same source
pool. Recommended orders by ascending fixture `recommendation_priority`, then
ascending `profile_id`. Broader orders by ascending `profile_id`. Ties therefore
have a stable deterministic outcome. This synthetic priority has **no Human
Design meaning** and is not a compatibility score, engine ranking, approved launch
recommendation rule or market-capacity claim.

| Fixture limit | Bound and behavior |
|---|---|
| Page size | At most **2** permitted current candidate projections |
| Selection/scan | At most **20** candidate identities in one bounded selection; no refill loop |
| Queue membership | At most **20** identities per queue; at most **40 retained candidate slots** across both mode queues |
| Retained queues | At most **2**, one per mode for the current viewer/session |
| Synthetic provider bookkeeping | At most **2 replay keys per candidate** in the Python fixture, with diagnostic call identities retained in a **120-entry** bounded deque; counters are scalar and no public cards are cached there |
| Provider batch | At most **2 page candidates / 6 provider attempts per page read**, within the existing service cap of **20 distinct candidates** per call |
| Provider retry | **1–3 total attempts** for declared transient failures, with current eligibility/mapping checks before each attempt |
| Queue lifetime | **300,000 milliseconds / 5 minutes** from creation under the injected numeric lifetime clock |
| Refresh | Explicitly replaces the selected mode's queue; no automatic replenishment or browsing write |

The mobile adapter keeps the lifetime clock separate from the fixed civil-day
eligibility fixture clock: normal preview lifetime uses a captured native `Date.now`, while tests
can use a registered mutable fixture-time source with monotonic revision cells. Python uses its explicit fixture clock source for both.
Clock/source replacement is itself invalidating and does not revive old handles.

No batch nesting or repeated refill expands these limits. Mostly excluded input
ends after its bounded scan. A provider failure does not trigger another
population or change eligibility. These are development test limits only; A07/P11
must establish real engine limits and measured query/provider capacity. The fixture
lifetime selects no launch retention, contact, rematch or resurfacing policy.

A mode retains its own finite ordering and progress. Switching to broader creates
or resumes that mode's queue; switching back resumes recommended progress. A
person may appear once in each mode's separate queue, but never twice within one
accepted queue. Mode switching does not reset the other queue. Explicit refresh
replaces only the selected queue and invalidates its former continuation handles.
Browsing, reaching exhaustion and refresh record no pass, like or other intent.
P05.3's [interaction composition](interactions-fixtures.md) adds explicit
commands. Once that composition commits a directional action, both modes and
refresh consult authoritative interaction consumption; the acted-on person
cannot reappear as untouched. Existing matched/restricted/unmatched pairs also
remain excluded while resurfacing/rematch policy is unresolved. This narrows
the per-mode repetition rule above: it describes browsing before consumption,
not permission to repeat an action after a mode change. A commit can invalidate
the current queues and require a fresh bounded read; it does not refill them
automatically or weaken expiry/publication guards.

## Continuation identity and adoption

The closed `DevelopmentDiscoveryPage` is an additive development adapter response
under `gapp-dev-v1`; it does not alter existing HTTP responses or activate a
production path. It carries its fixture contract marker, request correlation,
viewer/session, discovery mode, opaque queue identity, page state, at most two
closed development-discovery-profile projections and a nullable next cursor. The
[contract package](../../packages/contracts/README.md) owns generated types,
validators and shared cases. Unknown fields and duplicate profile IDs reject.
Production `PageRequest`/`CandidatePage` remain separate inactive design contracts.

P05.3 maps the current authorized development page/batch to composition-owned
UUIDs before building closed interaction intents. `profile-jules`-style card IDs
and process-local queue handles remain development identifiers. The mapping
binds current actor/session, mode, queue, membership and revisions; it cannot be
chosen by the client. A displayed card or copied cursor never authorizes a new
like/pass. An identical committed command may recover its immutable receipt
after consuming that batch, but a new command cannot reuse the stale authority.

Queue and cursor handles are opaque in-memory references. Their internal binding
includes the current viewer/session, exact mode and queue, stable position,
source/policy generations and expiry. They carry no private facts, birth values,
engine references, provider payload or access secret. They are non-durable and
are **not a production signing/encryption scheme**. Guessing or replaying a handle
cannot replace current authorization. Malformed, missing, expired, wrong-viewer,
wrong-session, wrong-mode or stale handles fail closed with no cards/continuation.

A read of the same current continuation returns the same page position; it does
not advance server state twice. Python reacquires and evaluates that bounded page
with stable queue/position idempotency keys; the mobile substitute may reuse its
retained page only after current source/authority checks. Neither route changes
accepted membership or position merely because the read is repeated.
A null cursor retries the first page; the caller retains its accepted position.
The last page has no next cursor, so the mobile control stops and displays
exhaustion without silently issuing another first-page read. The mobile coordinator
validates the full response shape and its request,
viewer/session, mode, queue and current authority before adopting items or a
cursor. Request generations discard a delayed response from an earlier request,
refresh, mode or account. Retained cards are masked when current authority is lost;
an obsolete completion cannot restore them. Refresh is a new bounded queue, never
a hidden retry of obsolete membership.

A relevant source change invalidates the affected queue membership/continuation
and requires explicit refresh. During final page publication, unchanged candidate
projections may survive as a partial page under their own retained guards, with
no continuation; a shared viewer/policy/time change suppresses the whole page. Same-value replacement/removal/restoration stays a new source incarnation.
Every published page also retains the source revision captured at publication,
including a terminal page with no cursor. A later participating source write
invalidates that page even when its currently visible candidates are unchanged.
A safe partial page formed during a request binds the new publication revision;
its unchanged survivors do not exempt it from the next write. Old membership/
order metadata and cursors cannot become current merely because values look equal. Conservatively invalidating a queue is acceptable; silently
promoting a formerly excluded pair into that queue is not. Logout/account switch or lost owner eligibility clears the adapter
queue/page/cursor caches and UI state. A single bounded expiry timer checks the
retained mode pages at their next expiry, retracts expired mounted content and
stops when no page remains; there is no idle polling loop. Source, policy and time
are revalidated on reads and presentation adoption; production durable invalidation
remains a P11 obligation.

## Eligibility, provider work and final publication

Every candidate first acquires current independent pair evidence through the
existing evaluator. Excluded, unknown, policy-pending, missing and wrong-pair
inputs cause **zero mapping/provider calls**. Current eligible candidates may then
reach the existing mapping/provider seam. Mapping/read callbacks are dependencies,
not authority. All returned evidence remains bound to the ordered pair, captured
input/mapping/policy versions and fixture provenance. Synthetic ready still
projects **pending/fixture**; neither ready HD output nor a numeric score is exposed.
The shared provider oracle distinguishes typed outcomes: synthetic ready and
typed pending yield a ready page, typed unavailable yields partial after one
attempt, and the simulated transient outage uses at most three attempts and
yields partial. Public compatibility remains pending in every case; page readiness
means the bounded read completed, not that Human Design compatibility is ready.
Typed unavailable/unsupported results may retain an otherwise eligible pending
card. A declared timeout/outage may do likewise after bounded attempts. A
provider result with wrong pair/provenance, stale identity, malformed output,
consent failure or idempotency conflict suppresses its projection; page-level
partial status never turns invalid provider evidence into a safe card.

The queue extends PR11's final-batch rule through selection, projection and
paging. Participating concrete revision cells are captured before callback-capable
source work and retained across attempts. Fact, policy/time, mapping and projection
source writes advance those cells, including same-value writes and restoration.
After **all** callback-capable eligibility, mapping and projection/media work,
the final comparison reads only captured concrete cells and stored primitive
revisions. No subsequent clock/source/provider/custom-getter read is allowed to
reopen that last-callback gap. Changed candidates lose obsolete projections and
compatibility; shared-viewer changes affect every dependent pair. An earlier
excluded candidate is not promoted after a later restoration.

Missing guard participation fails closed. The implementation retains PR10's
exact descriptor-based runtime version capture, with no getters or `toJSON`,
PR11's one numeric clock capture and private adapter/media binding generations.
Value equality or serialized hashes do not replace source incarnation checks.
This guarantee is for the documented synchronous fixture writer model. It does
not establish thread/process atomicity, PostgreSQL isolation, provider byte
revocation or protection from arbitrary malicious in-process source code.

## Disclosure and presentation states

Candidate pages explicitly project only `profile_id`, `display_name`, derived
adult `age`, `summary`, one to four approved synthetic `media_delivery_refs` and
the existing pending/fixture compatibility label. The additive
`DevelopmentDiscoveryProfile` leaves the earlier HTTP `DevelopmentProfile` shape
unchanged. Media references must have the `fixture-approved-` form, come from
current approved facts and identify non-delivering synthetic variants. The UI uses
fictional placeholders and fetches no real photographs or provider URLs.
Private birth input, email, location, preferences, blocks, moderation reasons,
account–chart links and raw provider bodies stay out of pages, cursor content,
retained public projections, logs and accessibility labels.

| State | Meaning and presentation obligation |
|---|---|
| Loading | One bounded pending request; browsing controls do not submit twice |
| Ready | Current authorized projections, with compatibility still pending |
| Partial | Provider/mapping outcomes are unavailable, failed or incomplete; safe current cards may remain, but no explanation exposes private diagnostics |
| Empty | The bounded population yields no permitted people; not a substitute label for provider failure |
| Exhausted | This finite queue has no further page; explicit refresh starts another queue |
| Reload required | Source/authority/continuation changed; obsolete cards and cursor are discarded |
| Error/offline | The request did not produce an adoptable page; controlled retry/refresh offers no unauthorized fallback |

Recommended and broader navigation uses Expo Router and accessible controls.
The web Next page control stays focusable through loading/exhaustion using
`aria-disabled` plus an activation guard; native uses the existing shared Button.
This scoped behavior preserves keyboard focus without programmatic refocusing.
Ordinary product copy omits source versions, exclusion reasons and engineering
counters. Developer scenarios are separately labeled synthetic. Small-screen
rendered checks and web focus behavior do not prove native device keyboard,
VoiceOver/TalkBack, secure persistence or signed builds.

## Later integration

A01/A07 still own supported HDE operations, output granularity, cache/data rights
and throughput. A05 owns launch geography, real preference taxonomy, age ranges,
distance, operators and resurfacing/rematch/history policy. Required unresolved
policy denies its dependent operation; independent fixture work may proceed.

[P11 acceptance](../testing/p11-deferred-acceptance.md) must replace these fixtures
with authenticated persistence, stable bounded queries/plans, transactionally
consistent source versions, current disclosure at response release, durable
invalidation and provider enforcement. The dummy database, readiness 503,
development-only runtime, rejected writes and empty production paths remain.
No SQL, migration application, HDE/provider call, Railway/Cloudflare change,
deployment, paid resource, chat dependency or legacy import is introduced.
