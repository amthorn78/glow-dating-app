# Initial privacy and safety rules

P02 application contract baseline under GAPP-PF01 sections 5–7 and D08.
These rules constrain later feature implementation. They do not attest that
authentication, provider enforcement, durable retention or production operations
exist. The only served routes remain the isolated development GET surface.

## Data minimization and projections

| Audience | Permitted purpose and projection | Excluded by default |
|---|---|---|
| Unauthenticated public | Published CMS policy/support information and a generic privacy-request acknowledgment | Dating profiles, account existence, private requests, birth inputs, moderation evidence |
| Account owner | Own profile/preferences, explicit consent decisions, entered birth facts/uncertainty, owned media/job status | Other users' unilateral likes, block reasons, staff audit internals, provider credentials |
| Eligible candidate viewer | Contract allowlist of candidate display fields and permitted compatibility freshness/projection | Email, exact birth date/time/place, precise location, engine identifiers, policy predicate reasons, safety evidence |
| Match participant | Current app-authorized channel/message outcome and permitted conversation history | Another match's channel, unrestricted provider tokens, rights inferred from compatibility or past membership |
| Support staff | Assigned support information with a specific scope and purpose | Moderation powers, birth inputs and broad private-profile access |
| Moderation staff | Scoped case/evidence/action projection with a recorded reason and actor | General HDE access, secret values, direct database privileges, unrelated private records |
| Provider worker | Minimum task-specific reference and versioned operation | Whole account/profile dumps, credentials embedded in event payloads, unbounded cross-account queries |

Exact fields are defined by the versioned contract schemas. Internal model fields
are never serialized wholesale. Candidate inclusion is itself private information:
return generic denied/not-found outcomes where object existence is not disclosable.
Closed schemas reject extra fields; they cannot replace server object authorization.

## Access and lifecycle invariants

- Both participants and both preference/block directions are evaluated from
  server-owned current evidence. Missing policy, unknown predicates, stale versions,
  withdrawn consent, suspension, pause or deletion cannot grant a new permission.
- Eligibility precedes chart/provider evaluation. Compatibility never creates a
  mutual match, staff privilege or channel entitlement. Native screens are not
  an authorization authority.
- Block, unmatch and deletion invalidate future contact authorization. A future
  transaction must serialize the authoritative change and send authorization;
  an outbox event alone is not proof of instant provider revocation. P06/P11 must
  close direct-SDK, stale-token and provider-failure bypasses before live use.
- Unblock/resume does not implicitly reactivate a historical match or contact
  grant. A05 owns resurfacing, rematch and existing-history choices. Unknown
  history policy returns no history permission; it does not erase safety evidence.
- P05.3 [interaction fixtures](interactions-fixtures.md) keep another person's
  unilateral like/pass private. Only committed mutual state has a participant
  projection; discovery, synthetic compatibility and a pending button state
  cannot imply a match. Immutable command receipts contain only the submitting
  actor's minimal logical outcome, object reference and committed version.
  Current match/profile projection is reauthorized separately on every read or
  replay. A cached receipt cannot restore contact or disclose revoked details.
- Participant unmatch is immediate revocation and does not require current
  discovery eligibility, compatibility availability or resolved history/rematch
  policy. Blocking likewise remains available while paused or after unmatch.
  These paths do not claim deletion of prior messages, safety evidence or remote
  bytes. P05.3's event records contain only versioned references; no event grants
  a channel, token, history access or delivery permission.
- An accepted upload remains quarantined until safe decoding, metadata stripping
  and moderation succeed. Only approved variants receive authorized delivery.
- Deletion revokes app access/visibility first, records a durable job and tombstone,
  then tracks every required provider step. A failed or unconfirmed HDE/shared-chart
  step remains unresolved. A successful local reference deletion is not engine purge.
- Export requests and download grants require current owner authorization and
  expiry checks. A public request is a request for identity verification, never
  authority to retrieve or delete an arbitrary account.
- Routine logs contain correlation IDs, bounded result codes and non-secret
  service identity. They exclude raw birth input, exact location, contact details,
  message/evidence bodies, device tokens, credentials and SQL parameter values.

## Retention classification and unresolved decisions

| Category | Data examples | Required decision/trigger |
|---|---|---|
| Account-private | Identity linkage, consent, profile/preferences, private birth input | A05 retention and deletion policy; lifecycle purpose ends or explicit request |
| Provider-managed | Media bytes, message bodies, delivery/device records | Actual processor contract, export/purge rights and verification; A04/A08 |
| Safety-restricted | Reports, evidence references, cases, appeals, staff actions | A05 named moderation/child-safety owner, lawful purpose and specific retention schedule |
| Operational-minimized | Idempotency receipts, outbox/inbox, job progress | Bounded replay/retry and reconciliation requirements with an approved schedule |
| Restore-replay | Deletion tombstones and provider-step completion facts | A05 retention plus P11 recovery-window/backup behavior; no deleted-account resurrection |
| Engine-owned | Chart/output and shared-chart obligations | A01 supported ownership/cache/deletion agreement; no assumed app deletion right |

No duration, launch geography, legal conclusion, operating owner, product price or
provider contract is selected by this document. An unset retention policy prevents
a claim of completed purge/export scope. An unresolved optional feature remains
disabled. These dependencies do not block static P02 design and fixture checks.

## Deferred operational proof

P04/P05 establish actual media limits, eligibility and presentation policy; P06
establishes provider contact enforcement; P07/P08 resolve operating roles, policies
and lifecycle scope. P11 proves persisted object authorization/revocation, atomic
outbox behavior, actual provider deletion, restore-time tombstone replay and
authentication persistence. P09/P12 own native and release evidence. No fixture
or static schema check discharges these proofs.
