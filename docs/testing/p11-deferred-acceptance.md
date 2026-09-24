# Deferred database, provider and native acceptance

These are **unexecuted acceptance cases**, carried from AP1-P02-001 and GAPP-PF01.
P02 static/fixture checks do not establish these results. Execute only after the
named phase prerequisites and target-specific authority are satisfied. Use
synthetic identities and approved environments; record exact candidate, target,
commands, observed outcomes and cleanup. No live endpoint is supplied here.

| Case | Stage and test | Required observable result |
|---|---|---|
| DB01 | P11A: apply reviewed app migrations to disposable PostgreSQL from zero | Actual migration ledger equals the reviewed set; models/SQL agree; no protected target accessed |
| DB02 | P11A: upgrade a supported prior schema and separately execute backfill | Existing rows preserved or explicitly quarantined; counts/invariants checked; both compatible app versions tested during expand-contract |
| DB03 | P11A: target/role preflight with wrong database, owner or migration role | Operation refuses before any DDL/DML; app runtime cannot change schema; protected HDE target never used as test destination |
| DB04 | P11A: malformed direct writes against every declared check/unique/FK constraint | PostgreSQL rejects invalid state, self-pairs, duplicate logical identities and orphan rows as specified; application maps expected errors safely |
| DB05 | P11A: concurrent reciprocal and repeated likes from separate connections | Exactly one canonical mutual match and one logical match-created outbox event; losers receive consistent idempotent outcome |
| DB06 | P11A/B: send authorization racing with block/unmatch/suspension/deletion | Defined transaction boundary orders outcomes; no new authorization after revocation commit; neither stale token nor provider channel membership bypasses it |
| DB07 | P11A: crash before commit, after commit, before/after provider acknowledgment | Rolled-back domain changes emit no committed event; committed outbox work survives restart; retries do not duplicate logical effects |
| DB08 | P11A/B: duplicate, delayed and out-of-order inbox/provider results | Verification precedes application; identity/version/idempotency binding rejects stale or wrong-object completion; reconciliation retains unresolved work |
| DB09 | P11A/B: authentication, verification, recovery, linking and session lifecycle | Maintained auth persistence rejects replay/expired links and wrong-account linking; logout/password/safety/deletion revocation works across devices without enumeration |
| DB10 | P11A: two-account eligibility read/recheck and policy changes during action | Actual trusted adapter obtains one consistent pair/version view or rejects/reloads; withdrawn consent, both block/preference directions and pause/delete changes invalidate prior evidence |
| DB11 | P11A/B: bounded recommendation queries/cursors under state changes | Stable scope-bound pagination, no duplicate or unauthorized candidate leakage, expiry/version invalidation, bounded query count and measured plans |
| DB12 | P11A/B: timeout, connection exhaustion and worker contention | Bounded failures/retries, lease recovery and no partial permission grant; actual latency/queue measurements recorded without mock capacity extrapolation |
| DB13 | P11B: restore an actual backup then replay retained deletion tombstones | Deleted identities remain inaccessible and do not regain provider access; restored jobs reconcile; measured recovery outcome recorded |
| PV01 | P11B: supported HDE adapter versus the shared conformance cases | Exact release/input/output/version mapping and allowed data scope verified; pending/ambiguous/timeout/partial/unsupported results remain honest; A01/A07 resolved for tested scope |
| PV02 | P11B: HDE input change, cache reuse and shared-chart deletion | Rights and identity/version invalidation proven against the supported contract; shared chart is not destroyed through assumed ownership; completion requires actual evidence |
| PV03 | P06 capability proof, repeated P11B: selected chat permissions | Direct SDK send, wrong channel, stale token, reconnect and hook outage cannot bypass match/block authorization; provider failure cannot silently allow contact |
| PV04 | P11B: media upload, moderation, delivery and purge | Private originals remain private; type/size/safe decoding/metadata controls operate; unauthorized delivery fails; approved-only variants and actual purge confirmed |
| PV05 | P11B: notification devices, permissions, rotation and retries | Revoked devices fail, duplicate paths reconcile, user preferences honored; default push contains no sensitive content; native transport observed separately |
| PV06 | P11B: staff moderation/support and appeal under real auth | Support/moderation scopes separated; assigned object/evidence access enforced; reasoned audit durable; WordPress supplies no alternate permission route |
| PV07 | P11B: own-data export and deletion across every selected processor | Identity verified; wrong-account/expired delivery refused; partial failures remain incomplete; approved retention exceptions explicit; repeated requests deduplicate |
| PV08 | P11B, only after A06 selects paid scope: real billing lifecycle | Verified signatures, replay defense, refund/revocation/grace/restore/reconciliation prove derived entitlement; otherwise paid feature stays disabled |
| PR01 | P11C: isolated app production migration/connection and bounded private smoke | Exact target/roles and stage evidence checked; reviewed migration set applied only to app storage; supported protected-engine operations have separate explicit authority |
| N01 | P09/P12: signed iOS and Android builds on the named device matrix | Native install, secure storage, deep links, permission denial, accessibility/large text, offline recovery and real device performance observed |
| R01 | P12: reconcile candidate, public policies, operators, recovery and release packet | All mandatory results linked to actual build/commit; open issues explicit; public distribution remains a separate authorized action |

No retry limit, service capacity, retention duration, geography, history policy or
moderation owner is approved by this matrix. Resolve the existing A01/A02/A04–A08
dependencies at their responsible phases. Failed tooling is not a behavioral
test failure; missing live evidence remains deferred rather than passed.

## P04.3 carryforward

P04.3 adds an in-memory media lifecycle and a narrow picker boundary. It does not
close any row above. Its actual-byte parser checks PNG structure, CRC and declared
dimension/encoded-resource bounds; it does not decode pixels, strip metadata or
establish server enforcement. System/moderator/provider events are synthetic and
approved references do not deliver images. The existing API/runtime guards remain
required. See [media semantics](../architecture/private-media-fixtures.md) and
[provider mapping](../architecture/media-provider-mapping.md).

| Existing case | Specific remaining media proof |
|---|---|
| PV04 | Exercise the selected real private provider and server processing with bounded synthetic files: actual safe decoding/resource isolation, malformed compressed data, metadata removal, quarantine and moderator controls, current viewer/object authorization, approved variants only, abandoned/expired uploads, grant replacement and late-completion reconciliation, immediate app revocation and actual provider deletion. Prove cache/revocation limits; a signed URL or upload notice is not current disclosure permission. |
| PV07 | Verify media export/deletion against every selected processor, including unresolved or failed purge, retries, retention exceptions and backup/cache behavior. A hidden row or synthetic `removed` state cannot prove real-byte erasure. |
| DB07 | Demonstrate durable media command/outbox ownership, collection/asset versions and idempotency across crash/restart, including provider acknowledgment arriving around the commit boundary. Fixture stage/validate/adopt is not a PostgreSQL/provider transaction. |
| DB08 | Authenticate actual provider events and reconcile their exact account/object/upload-or-removal identity before durable admission. Duplicate, stale, conflicting and out-of-order results must not approve an obsolete asset, consume a replacement grant, resurrect removal or falsely finish another purge. Images Notifications and R2 Queue transports require their own verified integration. |
| N01 | Verify the pinned Expo picker in signed native builds: permission denial/limited access/cancellation, Android activity destruction, stale result disposal, layout/large text, VoiceOver/TalkBack and offline interruption. Implement and verify a bounded native byte reader before allowing native selection to obtain an upload grant. Current native assets return unsupported; the size-bounded web `File` path does not prove native access. |

The `development-media-1` limits and review requirements are provisional test
inputs. They do not approve launch policy, provider quotas, retention, operating
ownership or budget. Existing non-media deferred cases remain unchanged.

## P05.1 carryforward

P05.1 derives ordered-pair eligibility from immutable application fixture facts,
an injected clock and explicitly provisional policy. Its in-process revision
counters, source generations, absent-block observations and delayed-result checks
are conformance inputs for future adapters, not authentication, PostgreSQL
snapshot/locking guarantees or durable invalidation. The
[reciprocal fixture mapping](../architecture/reciprocal-eligibility-fixtures.md)
describes those source rules. Every existing row above remains open.

AP1-P05.1-002 fixes the demonstrated synchronous final-read callback defects
within this fixture scope. Participating fact/policy/time and account–chart-link
writers advance retained monotonic revision cells; a callback-free check after
all reads suppresses stale compatibility. This is an implemented in-process
publication mechanism, not a deferred excuse for known fixture defects and not
proof of cross-connection/process consistency. P11 must supply an equivalent
authoritative database publication/action boundary using the real adapters.

| Existing case | Specific remaining reciprocal-eligibility proof |
|---|---|
| DB09 | Derive the actor and current session from maintained authenticated persistence. Verify account/profile/asset identity separation, current verification, consent, session expiry and cross-device revocation. A fixture repository or current client precondition must never confer actor authority. |
| DB10 | Acquire both accounts, profiles, media, consent, moderation, preferences, both directional blocks and selected policy from one consistent transaction view or reject/reload. Every relevant writer advances the correct aggregate/preference/block/policy revision in the same transaction. Prove first block insertion against a previously absent row, removal/reinsertion, same-value restoration and repeated A→B→A changes across connections and process restarts; an old token/result must stay obsolete. |
| DB10 | Test exact adult boundaries and the eventually approved leap-day/date convention, policy effective intervals, consent/policy expiry and clock progression with no record edit. Recheck current time before the action commits or the projection is released; stale persisted counters alone cannot extend permission. Define production clock authority and time-dependent invalidation instead of copying the fixture epoch as a persistence mechanism. |
| DB10 | Serialize policy publication/withdrawal with pair actions and all relevant writes. Inject concurrent preference, block, media, consent, pause, suspension and deletion changes before/after reads, during delayed provider work, during retries and while later candidates run. Bind retained eligibility and account–chart links, including input/mapping/identity changes, at an authoritative final publication boundary. Prove the production transaction/revocation boundary across connections/processes; neither sequential rechecks nor the synchronous fixture revision cells certify database atomicity. |
| DB11 | P05.2/P11 must supply stable bounded database queries/cursors, index/query-plan evidence and current disclosure filtering under change. P05.1's bounded conformance batch is not a production queue, pagination/ranking implementation or measured capacity. |
| DB05 / DB06 | Independently authorize likes, mutual matches, unmatch, channel entitlement, sending and history according to current relationship and approved policy. Pair eligibility alone grants none of them. Prove races against revocation; unblock/resume must not resurrect a historical match. Keep report/block/export/deletion on their own safety/privacy authorization paths. |
| DB07 / DB08 | Persist revision changes and required invalidation/outbox events atomically, then authenticate and bind delayed results to exact account/source generation, pair, input/mapping/policy versions and event identity. Prove crash/restart, replay and same-value restoration cannot revive obsolete permission. |
| PV01 / PV02 | Reuse the eligibility-before-mapping/provider and post-call/final-batch conformance rules against the supported HDE contract. Verify exact input/mapping/policy binding, cache rights and revision invalidation with approved access. Excluded/unresolved pairs must make no chart-mapping/provider call; fixtures cannot establish live throughput, policy enforcement or ready HD output. |

The synthetic `demo_connection` / `demo_a` / `demo_b` vocabulary is not an approved
gender/orientation taxonomy. A05 still owns launch geography, preference/age-range
requirements, moderation/operators, resurfacing/rematch and history policy.
Unknown required policy denies its dependent operation. The separate same-database
audit does not authorize this fixture assignment to connect or mutate a database.
P11 keeps disposable PostgreSQL → staging → authorized final app production
integration, with all HDE/shared-object protection and target/role preflight.
