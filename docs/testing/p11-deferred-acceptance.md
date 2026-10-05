# Deferred database, provider and native acceptance

These are **unexecuted acceptance cases**, carried from AP1-P02-001 and GAPP-PF01.
P02 static/fixture checks do not establish these results. Execute only after the
named phase prerequisites and target-specific authority are satisfied. Use
synthetic identities and approved environments; record exact candidate, target,
commands, observed outcomes and cleanup. No live endpoint is supplied here.

| Case | Stage and test | Required observable result |
|---|---|---|
| DB01 | P11A: apply reviewed app migrations to disposable PostgreSQL from zero; then move the app's database to a separate disposable instance by dump and restore ([ADR 0004](../adr/0004-app-database-placement.md)) | Actual migration ledger equals the reviewed set; models/SQL agree; no protected target accessed. The application runs against the moved copy with a configuration change only, and no dependency on an HDE-owned role, extension or object appears |
| DB02 | P11A: upgrade a supported prior schema and separately execute backfill | Existing rows preserved or explicitly quarantined; counts/invariants checked; both compatible app versions tested during expand-contract |
| DB03 | P11A: target/role preflight with wrong database, owner or migration role | Operation refuses before any DDL/DML; app runtime cannot change schema; protected HDE target never used as test destination |
| DB04 | P11A: malformed direct writes against every declared check/unique/FK constraint | PostgreSQL rejects invalid state, self-pairs, duplicate logical identities and orphan rows as specified; application maps expected errors safely |
| DB05 | P11A: concurrent reciprocal and repeated likes from separate connections | Exactly one canonical mutual match and one logical match-created outbox event; losers receive consistent idempotent outcome |
| DB06 | P11A/B: send authorization racing with block/unmatch/suspension/deletion | Defined transaction boundary orders outcomes; no new authorization after revocation commit; neither stale token nor provider channel membership bypasses it. **Partially evidenced in CI (P06.DB):** see "Early partial evidence" below |
| DB07 | P11A: crash before commit, after commit, before/after provider acknowledgment | Rolled-back domain changes emit no committed event; committed outbox work survives restart; retries do not duplicate logical effects |
| DB08 | P11A/B: duplicate, delayed and out-of-order inbox/provider results | Verification precedes application; identity/version/idempotency binding rejects stale or wrong-object completion; reconciliation retains unresolved work |
| DB09 | P11A/B: authentication, verification, recovery, linking and session lifecycle | Maintained auth persistence rejects replay/expired links and wrong-account linking; logout/password/safety/deletion revocation works across devices without enumeration. **Partially evidenced in CI (P06.DB):** see "Early partial evidence" below |
| DB10 | P11A: two-account eligibility read/recheck and policy changes during action | Actual trusted adapter obtains one consistent pair/version view or rejects/reloads; withdrawn consent, both block/preference directions and pause/delete changes invalidate prior evidence |
| DB11 | P11A/B: bounded recommendation queries/cursors under state changes | Stable scope-bound pagination, no duplicate or unauthorized candidate leakage, expiry/version invalidation, bounded query count and measured plans |
| DB12 | P11A/B: timeout, connection exhaustion and worker contention | Bounded failures/retries, lease recovery and no partial permission grant; actual latency/queue measurements recorded without mock capacity extrapolation |
| DB13 | P11B: restore an actual backup then replay retained deletion tombstones | Deleted identities remain inaccessible and do not regain provider access; restored jobs reconcile; measured recovery outcome recorded. The restore is a logical restore of the app's own database; a platform restore of the shared service is not used for an app-only incident without a review of its effect on HDE (ADR 0004) |
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

**Early partial evidence** (Nathan, 25 September 2026; OD-17). Before P06.2, work item P06.DB proves DB06's send-versus-block ordering and a minimal DB09 sign-in on a disposable CI database. It ran on 29 September 2026: Foundation run [36520940933](https://github.com/amthorn78/glow-dating-app/actions/runs/36520940933) on `dff83d4`, recorded in the [P06.DB evidence record](evidence/2026-09-29-p06-db-disposable-postgres-proof.md). DB06 and DB09 are marked **partially evidenced in CI (P06.DB)**, in the words of the [P06.DB brief](../planning/p06-db-disposable-postgres-proof.md)'s D6 (DM-08), DB09's lead reworded after the Dev Manager's DM-09. Its exact-head review (29 September) confirmed the design, the job and the log checks, and asked for one correction to the evidence behind DB06 (its F1, below). The correction pass P06.DB-C1 made it the same day: Foundation run [36534514283](https://github.com/amthorn78/glow-dating-app/actions/runs/36534514283) on `4280770` is the run of record for the stress numbers (every job passed; the evidence record explains the run's `cancelled` label). C1's exact-head review approved the corrected head on 4 October and added the limit lines below (its R1 and R2). Codex's review of PR28's final head (5 October) added DB09's expiry limit (its CX2). Its second code review found that the proof's host check accepted any database reachable on loopback (CX3): the correction pass P06.DB-C2 added the run's marker, and its Foundation run [37262466651](https://github.com/amthorn78/glow-dating-app/actions/runs/37262466651) on `43d8ca4` reran the whole plan with the same outcome: 55 of 55 cases, every control failing by its declared signal, and zero violations in the design's rows. It is the run of record for the final code, and C2's exact-head review approved the correction on 5 October. The marks stand as worded.

- **DB06:** on PostgreSQL 17, the reference design orders send authorizations against block, unmatch, suspension, deletion and sign-out, with the guarantees listed, under forced and randomized races. **Overlaps (P06.DB-C1):** in run 36534514283 each of the twelve stress races measured its own overlaps, 174 to 200 of its 200 iterations (floor 10), with zero violations, and the commit-order oracle, whose O2 now flags any send committed after a contact revocation of its match, found zero violations in the design's rows. Run 37262466651 (P06.DB-C2, with the run's marker) measured 197 to 200, again with zero violations. The first run's per-race counts were established for its first race only (the exact-head review's F1). **Limits (C1's exact-head review, R1 and R2):** in the stress run, the overlap is the intersection of two writers' database intervals, not an observed lock wait, and the construction does not guarantee each commit order. Against sign-out, expiry and the opposing writers the send rarely commits first (16, 21 and 1 of 200 in run 36534514283, and 0, 1 and 0 in run 37262466651; none in either sign-out race in two of five runs of C1's code), so that order rests on the forced cases. Each run needs a new database, which the job always provides.
- **DB09:** the app-side session revocation ordering against sends (sign-out, expiry, and account-state revocation, which bumps the epoch); the epoch's consistency is checked but not exercised as the deciding refusal (reworded after DM-09); with a stand-in session reference; not maintained authentication, verification, recovery, linking, credential revocation or allauth, which stay with the item that serves authentication and with P11. **Limit:** every epoch bump in P06.DB comes with the account leaving `active`, which the send refuses first. So the epoch check itself is never the deciding refusal: O7 checks the stored epoch's consistency, but no case or control exercises the epoch check as the refusal that decides (the evidence record's manager verification, observation 1, in the exact-head review's wording). **Limit (C1's exact-head review, R1):** in the sign-out and expiry stress races the send commits first rarely or never; that order rests on the forced `sequential_send_first` and `send_holds` cases. **Limit (Codex's review of PR28, CX2):** the send checks its session's expiry at a time read after its locks (the brief's 5.2), not at its commit, so a session that expires between that check and the commit does not stop the send; the oracle's O5, which requires the commit before the expiry, would then fail the run. No run comes near that boundary: every session but the one a case expects to be refused lives 300 seconds, and each case and stress iteration makes its own. So DB09 shows the check after the locks and the refusal of a session that expires while the send waits, not a send's commit ordered against time-based expiry. Settling the rule is carried to P06.2.
- **Not claimed:** that the app enforces any of it (the design is in the proof package until P06.2 carries it into the app and tests it again); DB06's provider half (channel membership, and a send the provider has already accepted), which stays with P06.2 and P11; the P11 target, its roles, pooling or load; maintained authentication.
- P11A and P11B still rerun DB06 and DB09 on the real target. Applying migrations there is setup, not DB01 acceptance, and DB01, the move-out path and every other case here stay with P11.

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
| DB11 | P11 must supply stable bounded database queries/cursors, index/query-plan evidence and current disclosure filtering under change. P05.2 now supplies a finite fixture queue and cursor composition; neither that implementation nor P05.1's conformance batch proves production persistence or measured capacity. |
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

## P05.2 discovery carryforward

The [bounded discovery fixture](../architecture/discovery-fixtures.md) implements
finite queues, independently evaluated current pairs, explicit mode/refresh
behavior and synchronous final publication/adoption guards. It changes no row
above to passed. Shared fixture conformance and rendered browser checks cannot
replace these live proofs.

| Existing case | Specific remaining discovery proof |
|---|---|
| DB09 / DB11 | Bind the actor/session to maintained authentication, not submitted fixture correlation fields. Reject forged, cross-viewer, cross-session, wrong-mode, expired and revoked continuations under the real transport. Select and verify a durable opaque/signed cursor mechanism without private payloads. |
| DB10 / DB11 | Bind selection membership/order, per-candidate eligibility, chart linkage and approved-media projection to a consistent authoritative publication boundary. Race later-candidate reads against earlier-candidate writes and shared-viewer/policy/time changes across separate connections/processes. Prove removal, same-value restoration, clock expiry and absent-block insertion cannot revive old pages or handles. |
| DB11 / DB12 | Measure real bounded selection/scan, query plans/indexes, retained queue size/lifetime, refresh/continuation query counts and provider retries. Demonstrate mostly excluded populations, partial/outage outcomes, exhaustion and concurrent repeated reads without unbounded refill or duplicate cards. The fixture's 20 candidates, two-card pages and five-minute lifetime are not capacity or launch-policy evidence. |
| DB07 / DB08 | Persist required queue/source invalidation and outbox effects atomically; bind delayed responses/events to current viewer/session, mode, queue and source generations. Restart/replay must not resurrect revoked projections, advance pagination twice or silently reuse obsolete membership/order. |
| PV01 / PV02 / PV04 | Verify eligibility-before-mapping/provider and allowed output/cache/media rights against the supported live contracts. Apply the same disclosure rules to both modes; no real HD ordering/score, unauthorized fallback, quarantined media or cached obsolete delivery is inferred from synthetic results. |
| N01 | Exercise finite browsing, mode preservation, refresh, offline/late responses and account changes on signed iOS/Android builds; verify touch/focus, large text, VoiceOver/TalkBack, device keyboard and memory behavior. Browser rendering and JavaScript exports do not establish this. |

P05.3's [interaction composition](../architecture/interactions-fixtures.md) owns
pass/like intent, mutual matching, unmatch and interaction idempotency/outbox
semantics; browsing and refresh create none of them. A05 still
owns real taxonomy/geography/age ranges and resurfacing/rematch rules. A01/A07
own supported compatibility output, rights and measured HDE throughput. R01/PR01
remain open and no deployment or production activation is introduced.

## P05.3 interaction carryforward

The synchronous in-memory commit, shared command cases and client journeys do
not execute any live case above. Preserve DB01–DB13, PV01–PV08, PR01, N01 and
R01 as separately evidenced obligations. Use independent database connections
and explicit barriers around reads, locks, commit and worker acknowledgments;
sequential fixture calls cannot stand in for those races.

| Existing case | Specific remaining interaction proof |
|---|---|
| DB04 / DB05 | Prove ordered directional uniqueness and one canonical UUID pair under simultaneous reciprocal likes, reversed arrival order and fresh-key repeats. Race insertion of the previously absent pair row; the selected lock/unique-conflict strategy must yield one match identity and one logical `match_created` event. No second pair row or automatic rematch follows unmatch/restriction. |
| DB04 / DB05 / DB07 | Race identical actor/operation/key commands on separate connections, then reuse that identity with changed action, target, expected version or batch/evidence. Exactly one valid logical commit wins; changed digest conflicts without a second action. State, immutable outcome/reference/committed-version receipt and required outbox event commit together. A pending row cannot permit concurrent re-execution. |
| DB05 / DB09 / DB11 | Lose the response after a committed action invalidates/consumes its batch. An identical retry by a currently authorized actor recovers the original immutable receipt without re-execution; a new key with the stale batch fails. Current projection must reflect later authorized state or generic unavailability, never the receipt's old active match. Prove session revocation/account deletion denies access and that dedup expiry/cleanup does not make blind replay safe. |
| DB06 / DB10 | Lock/recheck both accounts, policy, mapping and pair state with every relevant writer participating. Race the final like against first block insertion, block removal/reinsertion, same-value restoration, consent withdrawal, pause, suspension, deletion, policy/time expiry and mapping changes. No obsolete match/contact grant commits. Protect absent-block observations using persistent directional/account revisions, not only locks on existing block rows. |
| DB06 / PV03 | Race participant unmatch/block against match reads, channel provisioning and new send authorization. Revocation commits without requiring discovery eligibility or history policy; no new send authorization begins after that boundary. Repeated unmatch is safe; unblock/resume and late provisioning acknowledgment cannot reactivate contact. Separately record the actual provider policy for an already authorized in-flight send. |
| DB07 / DB08 | Crash before the domain transaction commits, after commit but before dispatch, during worker lease, after provider acceptance but before acknowledgment, and after acknowledgment but before local completion. Rollback leaves no action/match/receipt/event; a committed event survives restart. Redelivery is deduplicated by logical identity, and stale aggregate/contact versions cannot overwrite revocation. An outbox insertion alone proves no external exactly-once delivery. |
| DB10 / DB11 / DB12 | Persist action-driven consumption in the same authoritative boundary as interaction state and required invalidation. Across connections, both modes, refresh, another device and restart, a consumed direction or historical match cannot appear as an untouched candidate. Measure bounded queries, locks, queue invalidation and storage/retry limits under contention; capacity must refuse safely without evicting receipts into replayability. |
| DB08 / DB13 | Restore a disposable backup with retained receipts, outbox work and revocations, then replay tombstones and delayed events before traffic. Deleted or unmatched identities must not regain discovery/contact, duplicate matches or new logical creation events. Observe actual reconciliation and cleanup under the approved retention policy. |
| N01 | On signed iOS/Android builds verify Like/Pass, participant match list/detail/unmatch, pending/error focus, large text and VoiceOver/TalkBack. Exercise double activation, response loss, offline retry, navigation cancellation and account/session switching. The same intent keeps its idempotency key; late responses cannot announce a false match or restore revoked cards. |

P06.1 must establish provider permission/economics proof with A04/A08; fixture
match/contact state does not establish a Stream account, channel, token, history
right, Maker entitlement or paid activation. P11 must map these boundaries into
the app's own logical database and restricted roles on HDE's PostgreSQL service
(ADR 0004), without altering HDE or legacy objects. A05 still owns resurfacing/rematch/history and
retention choices; no test case selects them for launch.
