# Trusted eligibility acquisition and action recheck

P02 contract baseline addressing AP1-ACK002. `glow_domain/trusted_eligibility.py`
implements pure acquisition orchestration and pair/version checks. It defines
the future transaction port without implementing persistence, authentication,
an HTTP route, an action mutation or a production trust adapter. P11 owns proof
that source reads, revision changes, locks and commits satisfy this contract.

## Trust starts at acquisition

Only application composition chooses `EligibilityEvidenceRepository`. An API
handler derives the acting account from the maintained authentication system and
checks that the requested actor/object relationship is permitted before invoking
the application service. Target IDs and stale-action tokens remain untrusted.
No route may accept a repository, `EligibilitySnapshot`, `BoundPairPolicy`,
`PairPolicyInputs`, eligibility booleans or a claimed current revision from a
client as evidence of authorization.

`TrustedEligibilityService.evaluate(viewer_id, candidate_id, expected=None)`
acquires evidence afresh for every evaluation. `expected` is an optional
optimistic precondition, never a capability or proof of eligibility. A caller
cannot obtain permission merely by guessing the current value. The acquired
`PairEligibilityEvidence` includes both account snapshots, a directional
`BoundPairPolicy` and the current authoritative revision vector.

The acquisition adapter must read app-owned account/session-related access
state, accepted consent versions, profile visibility/completion, moderation,
preferences, both block directions and the server-selected policy. It derives
predicates from those records, verifies their source revisions, and returns
explicit unknown/pending decisions where policy or facts are missing. An
unavailable source must not become a permissive default. No geography, age
clock, preference range, verification rule or owner decision is selected by
this module. A05 remains the source of unresolved product/operating choices.
Current evaluation includes time-dependent validity: if expiry or a policy's
effective interval changes a decision without a user edit, acquisition must
invalidate or deny the old predicate and advance its effective revision. A
stored revision alone must not preserve an expired decision. No arbitrary
expiry duration is introduced here.

The class name, frozen DTOs and fixture labels do not establish source trust.
A malicious or incorrectly wired repository could fabricate internally
consistent evidence. A real adapter must be reviewed and tested against
authoritative authenticated persistence at P11; no such adapter exists now.
Fixture repositories used in tests are explicitly non-atomic substitutes.

## Pair and revision binding

The ordered vector is `viewer_id`, `candidate_id`, both snapshot revisions,
`policy_version`, both preference revisions and both directional block
revisions. Pair order is preserved. The bound policy names the exact vector
used to compute both preference outcomes and both block observations. The
service compares it to current revisions and to the embedded snapshots and
policy inputs. Tokens are opaque equality values, with no timestamp ordering
or numeric interpretation.

| Source change | Required version/invalidation behavior |
|---|---|
| Either participant's account access, verification, consent, moderation, completion or visibility | Change that participant's eligibility snapshot revision in the same future transaction as the source write |
| Either participant's preferences | Change the corresponding preference revision and re-evaluate both directions |
| Either participant creates/removes a block | Change the corresponding block revision; absence must have a revision too, so first insertion invalidates earlier clear evidence |
| Server policy publication or withdrawal | Change policy revision and readiness; previously resolved predicates cannot grant under an unresolved policy |
| Pause, deletion request, suspension or consent withdrawal | Deny affected permission immediately through source state and revision changes; invalidate queued/cached exposure and contact grants according to their separate domain rules |

The static `glow_persistence.models.AppAccount` definitions provide the mapping:
`eligibility_version` backs each snapshot revision, `preferences_version` backs
that account's preference component and `blocks_version` backs its outgoing
block component. Preference/block mutations also advance the aggregate
eligibility revision. The persistent account counter covers absent or removed
block rows. Every affecting writer must update these counters atomically; field
existence or a default of one does not implement invalidation. The exact adapter
mapping must be tested with the final models before integration.

`PolicyRevision` provides an unseeded policy publication pointer. A future
acquisition adapter must resolve the required registry entry and its supported
artifact; a missing entry or unsupported artifact is pending, never permissive.
Policy publication and privileged pair actions must share the same policy-row
lock/comparison boundary. No registry row, geography, preference rule or policy
choice is activated by these model definitions.

| Observed input/state | Internal result | Required application response |
|---|---|---|
| Wrong ordered pair in token, snapshot, policy binding or current vector | `rejected / wrong_pair` | No chart/provider/action; do not reuse the evidence for another pair |
| Missing source evidence | `rejected / missing_evidence` | Fail closed; reacquire only after the missing source is available |
| Pending required policy | `rejected / policy_pending` | Keep the dependent operation unavailable; track A05 without inventing policy |
| Bound policy, snapshots or current revisions disagree | `reload_required / inconsistent_version` | Discard the assembled evidence and reacquire/re-evaluate; no retry loop inside this primitive |
| Any failed/unknown safety or preference predicate, or blocked/unknown block direction | `excluded` | No chart/provider/privileged action; revoke or hide the affected projection as its owning workflow requires |
| Current evidence eligible but supplied action version stale | `reload_required / stale_action` | Reject the attempted action; reload the current projection and require a fresh intent/precondition |
| All evidence agrees and predicates pass | `ready` | Continue only the specific bounded workflow; enforce authentication, object rules and action-specific authorization separately |

Withdrawn consent maps to a failed consent predicate; suspension to failed
moderation/access; pause to failed discovery visibility; deletion pending/deleted
to failed account access/visibility. Both participants are checked. Unknown
states exclude. Known current exclusion wins over a merely stale action token.
Detailed exclusion reasons stay internal; public responses must not expose
another person's consent, moderation, preferences or decision to block.

`ready` is not a match, channel entitlement or send authorization. Discovery
visibility is not a universal chat/history policy. New-contact actions require
their own current relationship and resolved policy checks. Existing history,
pause behavior for established matches, rematch and resurfacing choices remain
A05 dependencies, with unavailable policy denying the affected operation.
Block/report, appeal, export and deletion must retain their own safety/privacy
authorization paths; they are not denied simply because a person is excluded
from discovery.

## Provider and transaction ordering

For bounded discovery, acquire and validate eligibility before reading chart
mappings or invoking compatibility. Bind provider results to the same ordered
pair and input/mapping/engine/contract revisions. Reacquire eligibility using
the captured vector and recheck chart mappings before publishing a returned
result; discard stale/excluded results. Every retry repeats acquisition. A
ready compatibility result never becomes a stored contact permission.

For a privileged pair mutation, `PairActionUnitOfWork.begin_pair_action` defines
one application transaction. The future adapter must perform these steps:

1. Authenticate the actor/session and check the action's allowed role and object.
   Lock the relevant pair/account/revision guards in a stable order or provide
   an equivalent serializable comparison scheme, including absent block rows.
2. Acquire current evidence inside the transaction and evaluate the submitted
   expected vector; reject stale or excluded intents. Independently recheck
   action-specific state, such as the current mutual match for contact, and any
   resolved action policy. Neither an old recommendation nor a client token
   authorizes the transition.
3. Stage the domain mutation, idempotency record and required outbox entries in
   that same transaction. Provider work is not dispatched before commit.
4. `PairActionTransaction.commit_if_current(expected)` atomically verifies the
   source revision vector and commits all staged rows. A false result or any
   exception rolls back all staged work. The context rolls back if exited
   without a successful checked commit. A later reload is a new evaluation,
   not an automatic replay of an obsolete privileged intent.
5. Dispatch committed outbox work idempotently and recheck action authorization
   at dispatch where delayed contact/provider effects could cross a revocation.
   P06/P11 must prove that provider permissions cannot bypass app revocation.

All writers affecting eligibility must participate in the same guards/revision
scheme. Policy changes must also participate; merely comparing snapshots after
ordinary unprotected reads is insufficient. For send versus block/unmatch,
the committed revocation is the linearization boundary: no newly authorized
send may occur after it. The treatment of already authorized in-flight sends
and existing history is a separate documented provider/product contract.

## Executable evidence and deferred proofs

`tests/test_trusted_eligibility.py` exercises wrong pair/reversed direction,
all seven revision components, source-policy-snapshot disagreement, stale
action tokens, missing/pending evidence, both people's revoked/unknown states,
both preference/block directions and rejection of client-shaped booleans.
Programming errors propagate rather than being mislabeled as normal exclusion.
Tests use no database or provider; they establish deterministic service rules.

P11 must still prove maintained-auth actor/session mapping and revocation,
consistent acquisition, revision increments on every relevant write, absent
block insertion races, time-dependent expiry and policy publication races, action/outbox atomicity,
retry/idempotency behavior, post-commit dispatch and block/send ordering. The
older `FixturePairEvaluationService` remains a development-only primitive for
direct supplied policy values; it is not promoted to a production input route.
