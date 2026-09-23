# Provisional HDE seam

**Status:** P02 design preparation. No HDE adapter, engine call, chart request, engine mutation or production credential configuration is introduced here. The source of the boundaries below is current GAPP-PF01 sections 5–7 and assumptions A01/A02/A07. That plan records earlier HDE source observations; this document does not claim a new inspection or certification of an HDE release.

## App-owned interfaces to design

The following logical port names come from the governing plan. They are not HDE endpoint names, wire DTOs or promises that HDE supports an operation.

| Logical port | Application responsibility | Agreement required before a real adapter |
|---|---|---|
| `BirthInput` / `ChartResolver` | Preserve entered civil date, local time, place, uncertainty and consent; separate app account/input identity from opaque chart identity; show ambiguous/pending/unsupported states | Accepted input schema, place/timezone authority, missing/uncertain-time handling, supported read/create/update operations, permissions and idempotency |
| `CompatibilityProvider` | Supply a bounded eligible candidate set/pair; map allowed results to ready/pending/unavailable/unsupported without inventing scores | Supported single/batch granularity, directionality/symmetry, output versions, authentication, limits, timeouts and error/retry semantics |
| `CompatibilityProjection` | Expose only approved explanation/band plus freshness; keep app eligibility and contact permissions independent | Allowed user-facing fields/wording, cache/persistence rights, provenance, invalidation and whether any ranking is authorized |
| `EngineLifecycle` | Track app reference invalidation/deletion requirements and per-step progress | Ownership, supported request operation, shared-chart handling, retention obligations and completion evidence; engine mutations remain outside this assignment's ordinary authority |

## Non-negotiable separation

- HDE owns calculation and result semantics. The app does not import engine math, use undocumented tables, inspect diagnostics for hidden scores or repurpose a development route for production.
- App eligibility runs before compatibility and is rechecked at interaction time. A compatibility result never creates a match or authorizes chat.
- An app account ID and an HDE chart ID are different identities with an explicit mapping. Missing or stale mapping is a domain state, not permission to fabricate an identifier.
- User-entered birth details stay private. Preserve uncertainty; do not guess a time or normalize local birth time to UTC without verified place/timezone resolution.
- Cache identity must include input, engine and contract versions. Do not normalize pair direction until the engine contract explicitly guarantees symmetry.
- Current development responses contain only `pending`/`fixture`. They contain no real compatibility label, ranking or HDE evidence. The development process refuses staging/production and live HDE configuration.
- An observed deployment success is not contract acceptance, throughput evidence or permission for writes. Database-dependent/live proofs remain P11; no protected engine change follows from this document.

## Proposed fixture/conformance backlog

The development HTTP presentation remains pending/fixture only. Internal `glow_domain` primitives now provide typed synthetic pending, unavailable, unsupported and explicitly synthetic ready outcomes; distinct app/engine mappings; and versioned directional cache identities. An internal fixture service reads identity-bound snapshots afresh and applies eligibility before calling the fixture provider. See [domain seam verification](../testing/domain-seams.md). There is no live HDE adapter, authenticated request path or atomic persistence boundary. The scenarios below remain end-to-end conformance requirements; their complete behavior and live evidence are not established by these bounded tests.

| Scenario | Required app behavior | Remaining live evidence |
|---|---|---|
| Missing/ambiguous birth input | Preserve entered facts; request correction or display unresolved state; no silent fallback | Accepted uncertainty semantics and resolution source |
| Pending chart/compatibility | Show pending state with bounded retry behavior; no fabricated ready result | Actual asynchronous behavior, retry limits and supported completion signal |
| No eligible candidates | Return explicit empty app result; do not call HDE merely to fill the list | Candidate query/persistence proof, not an engine requirement |
| Unsupported result/version | Typed unsupported or unavailable app state; no numeric fallback | Contract/version negotiation and release compatibility |
| Timeout/outage/partial batch | Separate unresolved pairs, retain safe prior freshness where permitted and bound retries | Actual error semantics, rate limits, timeout behavior and batch identity |
| Birth input changes | Mark affected app references/results stale through the reviewed mapping lifecycle | Supported recalculation identity/idempotency and invalidation rules |
| Deletion/shared chart | Revoke app access/visibility immediately; track unresolved engine obligation truthfully | Data ownership, retention, permitted engine action and final evidence |
| Directional versus symmetric output | Preserve direction until explicit symmetry guarantee | Supported contract statement and corresponding conformance case |

## Adapter activation record still required

Before live use, record the supported contract/release, exact environment and non-secret service identity, authorized operation/data scope, input/output mapping, error/idempotency/retry model, output/cache rights, deletion responsibility and test evidence. Secure credentials must remain outside documents and source control. A01/A07 can block live compatibility while independent application work continues. No production endpoint URL or engine request schema is guessed here.
