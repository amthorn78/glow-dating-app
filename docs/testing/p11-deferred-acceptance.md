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
