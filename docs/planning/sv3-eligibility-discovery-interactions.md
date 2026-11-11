# SV3 — The eligibility, discovery and interactions slice, proven on disposable PostgreSQL

- **Work ID:** SV3 (OD-49, N1 (a); PF01 §8, "Server slices"; the F07, F08, F09, F10 and F13 flows).
- **Status: brief, revision 2, 11 November 2026, by App Manager 11.** Revision 1 went to the Dev Manager as DM-60 (DM-31 item 3; the charter: new components, integration strategy, security boundaries). [DM-60](../continuity/dev-manager/reviews/2026-11-11-dm-60-sv3-brief.md) (answered at `777a6ad`, a read of `674e00e`) approved it with Q1 to Q20 in given words; revision 2 applies Q1 to Q15 here as written, Q16 in the P11 plan and Q17 to Q20 in the carried-items file. No further read is needed before Stage A's prompt (DM-60 section 2). Stage A's prompt is next ("Sessions").
- **Owner:** Nathan Amthor, by the order he resumed on 26 October (OD-49): the server slices SV1 to SV4, before P10. **Manager:** App Manager 11. **Sessions:** one implementation session per stage (D1), each started by Nathan, in `Glow App - No Stream` (no Stream call, no provider, no credential).
- **Starting point:** `main` at `3240ef0` (PR44, SV2 Stage B), with the manager branch's Markdown records after it. Each prompt names the exact commit.
- **Evidence home:** `docs/testing/evidence/<date>-sv3-eligibility-discovery-interactions.md`, written by the sessions.

## Why

- **PF01 §8, "Server slices":** *"SV3 (eligibility, discovery and interactions) … Each is proven on a disposable PostgreSQL in CI under P06.DB's rules (no shared or production database, CI-generated credentials, the runtime guards kept). The runtime stays sealed until P11 wires it. A slice's database proof partially evidences its P11 cases, and P11A and P11B still rerun them on the real target."*
- **PF01 §7, "Discovery and matching":** *"Apply age/consent/completeness/visibility/moderation/block/reciprocal-preference eligibility before HDE ranking. Recommendations and broader discovery share these rules. Use bounded, stable queues, cursor pagination and explicit refresh/invalidation; do not score the entire population against itself. A like is idempotent. Simultaneous reciprocal likes produce one match and one logical match-created event. Recheck current state for every privileged action. Define resurfacing, unmatch/rematch and deleted/paused-account behavior explicitly."*
- **PF01 §5:** the app must not obtain ranking data from undocumented HDE tables or reimplement compatibility math; *"If only permitted bands are available, ranking operates at that granularity with documented application-owned secondary criteria; it must not invent fine-grained scores."* *"Production boot rejects fake HDE providers."*
- **PF01 §6, the data groups:** *"Like, pass, Match and block | Directional actions; canonical unordered match pair; uniqueness and transactional state transitions; block overrides discovery and messaging"* and *"RecommendationBatch/entry and CompatibilitySnapshot | Bounded candidates, eligibility version, freshness, engine/contract provenance; no unbounded all-pairs cache"*.
- **The flows** (`flows-v1.json`; `production-contracts.md`):
  - **F07**, eligibility and discovery: *"Wrong-viewer/stale cursor rejected; no eligible candidates returns empty and no provider call"*;
  - **F08**, interactions: *"Repeated key identical intent yields same result; changed payload conflicts; stale/ineligible target denied"*;
  - **F09**, matches: *"Reciprocal likes only; one unordered pair and logical event; unilateral client match creation denied"*;
  - **F10**, unmatch: *"Participant unmatch revokes contact without owner-policy prerequisite; unmatch never grants rematch"*;
  - **F13**, block: *"Block works after unmatch and while paused; unblock cannot restore match/send entitlement"*.
- **Nathan's answers** that SV3 applies:
  - **OD-60, P1 and P2:** the four two-way list fields; an age range applied both ways; a home area or the phone's approximate location, with console-set distance choices, *"never exact coordinates or an exact distance shown"*.
  - **OD-60, R:** *"resurfacing, an undo of the last pass, and rematch are each off at launch and switchable with a waiting period; rematch never after a block or a report"*.
  - **OD-61:** a profile shows only with its chart resolved and identity verification (or a staff approval while the setting allows it). SV2 enforces both through completion, so a `visible` profile has both.
  - **OD-12:** after an unmatch or a block, neither person can send or see the conversation.
- **Carried to SV3** (the [carried-items file](carried-to-later-items.md)):
  - from P09.3a's matrix: eligibility reads G-01's account age state (DM-37 2.2);
  - from OD-60: the two-way rule over the four fields and the age range, and the distance filter over areas; the settings for resurfacing, undo and rematch; tests of what repeated filter changes and tiny population groups reveal (DM-51 M9);
  - from SV2's brief (DM-52):
    - the "all" marker includes values the console adds later, and "not stated"; a narrowed set never includes "not stated";
    - a member with "not stated" in orientation or relationship status is seen only by viewers who keep all of that field;
    - age comes from the age state's date, in whole years, never from the birth input;
    - a distance choice counts areas whose internal points are within it, and two members in one area are at distance zero;
    - every reader of consent filters by purpose;
  - from SV2 Stage A (DM-54): a profile can stay `visible` after a new onboarding consent version is published, until the member's next requirement write. Discovery reads the accepted version against the current one, and `policy_published` for `consent.onboarding` is its invalidation signal.
- **The matrix's recheck for SV3 is done** ([recheck record](../testing/evidence/2026-11-11-sv3-matrix-recheck.md), 11 November 2026). Seven rows were rechecked and no requirement changed. Its three consequences are D3's set of accepted age states, D17's question for counsel, and D3's exclusion of a known minor.

## Outcome

SV3 builds the server's eligibility, discovery and interactions on SV1's actor and SV2's profile. It proves them on a disposable PostgreSQL in CI and keeps them sealed from the served runtime.

1. **Pair eligibility over the ORM** (D2, D3): the trusted adapter behind `TrustedEligibilityService`. It reads both members' authoritative state in one consistent view: account, age state, consent, identity verification, profile, the four fields and both "show me" sets, age range, area, and both block directions.
2. **The two-way rule, age and distance** (D4, D5): every field and the age range, applied in both directions; distance between area internal points.
3. **Recommendations and broader discovery** (F07; D6 to D8): bounded batches with their entries, cursor pages tied to the viewer and the batch, version-based invalidation, and no HDE call.
4. **Like and pass** (F08; D9): idempotent directional actions, rechecked under locks at commit.
5. **The mutual match** (F09; D10): reciprocal likes make one match on the one pair record, with one logical event, under both accounts' locks.
6. **Unmatch and block** (F10, F13; D11): the member's routes, through `glow_chat`'s reviewed writers.
7. **Resurfacing, undo and rematch** (OD-60 R; D12): resurfacing and undo follow their settings, off at launch; rematch's setting refuses to be switched on until a later item builds it.
8. **Glow's routes for the member** (D13): pages, actions, matches, unmatch and block, each validated against the contract, through SV1's actor.
9. **The proof** (D14): the cases below on a disposable PostgreSQL in CI, through the HTTP endpoints with Django's test client, under P06.DB's rules. They include concurrent reciprocal likes from separate connections (DB05), eligibility changes during an action (DB10), and pagination under change with recorded query plans (DB11).
10. **Sealed** (D15): the served runtime imports none of the new code, and its database backend stays Django's dummy one.
11. **The records:** the data model's interaction, block, match and recommendation rows, rewritten as built; the contract's additions (D13); the P11 plan's partial evidence (DB04, DB05, DB10, DB11); the evidence record, with the threat model's inputs.

## Design

- **D1 — Scope, stages and seal.**
  - **Two stages in one item, each with its own session and verification** (recommended). **Stage A** is items 1 to 3 and their routes: eligibility and discovery. **Stage B** is items 4 to 7 and their routes: interactions. Each stage is reviewed and merged as SV2's were: an exact-head code and security review of the stage's final code head, with a written threat model, then Codex's review, before that stage's PR merges. Stage B starts from `main` after Stage A merges. The alternative is one session; its diff would cross two security boundaries at once (who may see whom, and who may contact whom).
  - **Sealed until P11,** as SV1 and SV2 are: no deployed URL, no provider, no real member, no credential beyond what CI generates for one run. The mobile app is unchanged; its fixture adapters stay until P10 and P11 wire the client (PF01 §7).
  - **No staff HTTP route.** P07 builds the staff API. SV3 reads the moderation state SV2 and `glow_chat` write (`restricted`), and writes none.
  - **No report.** Report, cases and appeals are P07.2's (F14, F15). D12's rematch rule reads a report as any `SafetyReport` row between the pair. No SV3 code writes one; only tests seed it.
- **D2 — One consistent view for each eligibility decision** (DB10).
  - **Page reads:** each batch's candidate selection is one SQL statement, so in PostgreSQL's READ COMMITTED it reads one snapshot. Each page's recheck of its entries (D7) is one statement too, so a page's eligibility is read from one snapshot as well; if the recheck needs more than one statement, the page's reads run in one REPEATABLE READ transaction (DM-60). The statement holds every predicate of D3 to D5. It is bounded by a `LIMIT` on the batch size, from an index-backed scan.
  - **Actions:** a like, pass or match rechecks the pair inside the action's transaction. That recheck runs after the action takes both accounts' row locks in `glow_chat`'s canonical order (the lower account, then the higher) and the settings pointers in name order (SV2's D19). Every writer of a fact the predicate reads already takes the owner's account row lock first (SV2's D9; `glow_chat`'s writers), so the recheck sees each writer's committed state or waits for it.
  - **The adapter** implements `glow_domain.trusted_eligibility`'s `EligibilityEvidenceRepository` and `PairActionTransaction` protocols, reading authoritative rows, never a client assertion (that module's docstring). Its `PairEvidenceVersion` is built from the accounts' `eligibility_version`, `preferences_version` and `blocks_version`, the profiles' versions and the settings' policy versions.
  - **The alternative:** REPEATABLE READ for page reads. One statement already gives one snapshot, so it would add retries and gain nothing.
- **D3 — The predicates** (`glow_domain.eligibility`'s rules, each for the viewer and for the candidate):
  - **SELF:** a member is never their own candidate.
  - **ADULT** (G-01; the recheck): the age state is in the accepted set, which holds only `self_declared_adult` today. P09.2 adds the store-signal states, and a later item may require a stronger one, without a redesign. The set is code, not a setting. A member whose state is not in it gets no page, appears in no batch, and has no recommendation computed (UST-41; USF-11).
  - **CONSENT:** an `onboarding` decision, `accepted`, at the current version (DM-54), read by purpose. A `sensitive_profile` decision never satisfies it. Publishing a new onboarding version makes every older acceptance fail this predicate at once, without waiting for the member's next write. SV2's recompute is not relied on for this.
  - **VERIFIED, COMPLETE and VISIBLE:** the profile is `visible`. SV2's completion already requires onboarding consent, the adult check, the profile fields, an area, a photo, a resolved chart and identity verification or a staff approval (`glow_profiles/requirements.py`), so `visible` carries them (OD-61). The predicate does not re-derive them. `paused`, `restricted`, `removed` and `incomplete` fail it.
  - **Re-derived or carried:** ADULT and CONSENT are read directly, because `visible` can lag them (DM-54 found the consent case). The rest rely on `visible`, which every SV2 requirement writer recomputes. The alternative is to re-derive every requirement at read time; it duplicates SV2's list in SQL.
  - **ACTIVE:** the account is `active`; `suspended`, `deletion_pending` and `deleted` fail it.
  - **MODERATION:** a `restricted` profile fails VISIBLE already. No other moderation state exists before P07.
  - **PREFERENCE:** D4 and D5, both directions.
  - **BLOCK:** an `active` `Block` row in either direction excludes the pair from every page and every action.
  - **Every predicate fails closed:** a missing row is a failure, never a pass (F06: unknown denies).
- **D4 — The two-way rule and age.**
  - **For each of the four fields:** the candidate's value is in the viewer's "show me" set, and the viewer's value is in the candidate's. A set that keeps all is the one `all` row and matches every value, "not stated" included. A narrowed set holds list values only and never matches "not stated". A missing `ProfileFieldChoice` row for orientation or relationship status reads as "not stated" (SV2's D3).
  - **Retired values** stay matchable for their holders (SV2). A narrowed set that holds a retired value still matches it.
  - **Age:** the candidate's age is `age_years` (SV2's D4) on the server's current date, from the age state's date, never from the birth input. It must lie within the viewer's range. Under the setting's direction `both_ways`, the viewer's age must also lie within the candidate's range. `age_years` is the age port's method (`glow_domain.identity`, SV2's D4); the SQL statement must use the same whole-years rule. A test pins the two against each other at the leap-day cases of the onboarding fixtures.
  - **Narrowing switched off:** where `profile.narrowing` makes a field not narrowable, that field's sets are read as keeping all.
- **D5 — Distance** (OD-60, P2; DM-52).
  - The distance between two members is the great-circle distance between their areas' internal points. Two members in one area are at distance zero.
  - A distance choice with `miles` counts candidates whose area is within that distance. `anywhere` (`miles: null`, the launch default and only choice; SV2 Stage A's record) filters nothing.
  - Applied in the viewer's direction only (recommended). OD-60 gives the age range a direction and gives distance none. The alternative is both ways, as the age range is.
  - **Never exposed:** no response, error, log line or event carries a distance, a coordinate or a member's area ID. The card may carry the area's name (D13).
  - **Computation:** in SQL, from the `Area` table's points, with no new extension. The 925 areas allow a precomputed pair table, but SV3 adds none (recommended); the query plan in D14 shows whether one is needed.
- **D6 — Recommended first, then broader** (F07; PF01 §1).
  - **Recommendations** are the eligible candidates ordered by the compatibility port's permitted output: a band, never a score (PF01 §5). Ties are broken by an app-owned secondary key, a keyed hash of the batch and the candidate (`salted_hmac` with a salt of its own and SHA-256, as `glow_profiles/idempotency.py` keys SV2's stored digests, so that a client who knows the batch's and the profiles' IDs cannot compute the order and read band boundaries from it; DM-60), so the order is stable within a batch and reveals nothing between batches.
  - **Broader discovery** is the eligible candidates not in the viewer's current recommendations batch, in the same tie-break order.
  - **The port:** `glow_domain`'s compatibility port, with only the existing fixture adapter, selected only by the proof's settings. The served runtime selects none, and its boot refuses a fixture provider (PF01 §5). SV3 makes no HDE call and writes no `CompatibilitySnapshot` holding an HDE result. A snapshot it writes holds only the fixture's state, marked as a fixture, in the proof.
  - **Port states:** `pending` or `unavailable` makes the recommendations batch `pending` or `unavailable` (the batch's states), and broader discovery still serves its candidates. `unsupported` for a pair leaves that pair out of recommendations only.
  - **The alternative:** no recommendations collection until P11's HDE contract, broader only. The contract already names both collections, and the fixture states prove the seam, so revision 1 recommends building both.
- **D7 — Batches and cursors** (F07; DB11).
  - A page request (`PageRequest`: collection, cursor, limit ≤ 50) with no cursor creates a `RecommendationBatch` for the viewer and collection. The batch stores the viewer's `eligibility_version`, `preferences_version` and `blocks_version`, a policy version that changes whenever a setting its selection reads is published (`consent.onboarding` and each `profile.*` and `discovery.*` setting it uses; DM-60), a limit ≤ 100 and an expiry. It holds up to 100 `RecommendationEntry` rows with the candidates' versions.
  - A cursor names the batch and an offset. It is bound to the viewer and the session's account: a forged cursor, another viewer's cursor, a cursor for the other collection, an expired batch, a batch whose viewer versions or policy version no longer match, or a batch an action has consumed (D9) is refused with the generic stale response (F07; the contract's "Pagination, idempotency and stale state"), and the client starts again.
  - **Each page rechecks its entries at read time:** an entry whose candidate's versions changed is evaluated again, and dropped if it no longer passes. Block rows are rechecked in both directions for every entry, because a block bumps only its actor's `blocks_version` (`glow_chat`'s `block`).
  - **Consumption** (`interactions-fixtures.md`, "Directional state, pair state and consumption"; `discovery-fixtures.md`; DM-60): a candidate the viewer has liked or passed, and the other member of any pair with a `Match` row (`active`, `restricted` or `unmatched`), are excluded from the viewer's selection, and each page's recheck drops them, checking every entry as it does for blocks, in both collections, whatever the refresh. D12's resurfacing is the only exception, for a pass. A like or pass changes nothing in its target's batches or their freshness, so its target cannot learn of it (D8). A match drops each member from the other's pages at the next page's recheck, as a block does.
  - **Bounds:** at most 100 candidates per batch, at most 50 per page, one candidate selection per batch, and a bounded number of queries per page, which the proof counts. A viewer holds at most one batch per collection: creating one deletes the viewer's earlier batches of that collection, with their entries, in the same transaction, so the refresh after each action (D9) leaves no growing history. A cursor or an action naming a deleted batch is refused as stale (DM-60).
  - **Expiry:** the batch's lifetime is a code constant in revision 1 (proposed: 30 minutes). The alternative is a setting.
  - An empty market returns an `empty` batch with no provider call (F07).
- **D8 — What a viewer can learn** (DM-51 M9; the flows' private projections).
  - Exclusion reasons are private: a page never says why someone is absent, and an `empty` batch reads the same whatever the cause.
  - No count of candidates, matches or likes is returned beyond the page's own items.
  - An unreciprocated like is never shown to its target (F08).
  - A block's direction is never shown to the blocked member (F13).
  - **The accepted disclosure** (OD-60): a viewer who narrows a field learns that field's value for everyone shown. Repeated filter changes on a small population can isolate one member's value. SV3 does not prevent this; the field is the member's own choice to show or to match on. The proof measures it: for a population of one, with the filter on and off, it records what the two responses reveal, for the threat model.
  - The alternative is a minimum population before a narrowed page is served. Revision 1 does not recommend it: it changes product behaviour, and OD-60 gave narrowing to the member.
- **D9 — Like and pass** (F08; DB04; DB10).
  - `InteractionIntent` carries the target's profile ID, the batch ID and version, the action, and `CommandMeta` (idempotency key and expected version).
  - **Idempotency** is SV2's: unique by actor, operation and key, with the stored digest keyed as SV2's are. An identical repeat returns the original receipt with `replayed: true`. The same key with a changed payload conflicts.
  - **At commit,** under D2's locks: the target must be in the viewer's named batch at that version, and D3 to D5 must pass for the pair as locked. Otherwise the action is refused as stale or ineligible, and nothing is written.
  - A `DirectionalInteraction` row per actor and target, `liked` or `passed` (unique pair). A like over the actor's own pass is F08's `like` from `passed`, reachable only once D12's resurfacing returns the candidate to the actor's batch. A pass over a like is refused: F08 has no such entry. D12's undo withdraws a pass through F08 entries of its own.
  - **A committed like or pass consumes the batch it named** (the contract's "P05.3 internal interaction result and identity bridge"; DM-60): that batch becomes `stale` (F07's `invalidate`), and the next action needs a fresh page (a page request with no cursor, D7). An identical command is checked as a replay first, so a lost response is recovered from its receipt after its batch is consumed; a new command naming the consumed batch is refused as stale. `CommandMeta.expected_version` addresses the directional row (zero for its absence).
  - The target's batch entries are not changed: the target's next page excludes nothing because of the like, and never shows it.
- **D10 — The mutual match** (F09; DB05).
  - When a like finds the target's `liked` row toward the actor, the same transaction creates the one `Match` on the canonical pair (`account_low` < `account_high`). It runs under both account locks, already held (D2), with one `match_activated` event. The unique pair constraint is the backstop: simultaneous reciprocal likes produce one match. The two likes serialize on the account locks: the later one finds the earlier one's `liked` row and makes the match, and the earlier one, which found no reciprocal row, returns `liked` with no match. Both arrival orders give one match and one `match_activated` event (DB05; DM-60).
  - **The chat side:** a match needs its `ChatBinding` and `ChatIdentity` rows and their outbox events, as `glow_chat`'s `activate_match` writes them. `activate_match` is the proof's and the conformance run's writer, and its docstring says that *"reciprocal likes and current two-person eligibility are checked by the activation P11 wires (F09), under the same locks"*. Two options:
    - **(a) recommended:** a new writer in `glow_chat`'s adapter, `activate_reciprocal`. It is `activate_match`'s body with one check added under its account locks: the two `liked` rows. It is called only from Stage B's like, inside the like's transaction, after the like has rechecked D3 to D5 for the pair under the same locks (D9). That recheck is its documented precondition, so `glow_chat` imports nothing from `glow_discovery` (DM-60). This keeps one owner for the contact lock protocol and its checks (CX5), and makes `glow_chat`'s adapter an owned path for that one writer and its tests.
    - **(b):** Stage B's own writer creates the `Match` and calls a provisioning function extracted from `activate_match`. That splits the contact checks across two modules.
  - **No client can create a match** (F09): no route takes a match intent.
  - A match on a pair whose `Match` row already exists (`unmatched` or `restricted`) is never a second row: D12's rematch, or a refusal.
- **D11 — Unmatch and block** (F10, F13; OD-12).
  - **Each route's command** takes D9's idempotency (SV2's keyed digests, a replay checked first) and runs `glow_chat`'s writer inside its own transaction, after both accounts' row locks in `glow_chat`'s canonical order, as SV2's operations nest `glow_chat`'s writers. `CommandMeta.expected_version` addresses the match for unmatch and the directional block for block and unblock (zero for its absence), as the contract says (DM-60).
  - **Unmatch:** the participant's `UnmatchIntent` runs `glow_chat`'s `unmatch` unchanged. It revokes contact without any eligibility or policy prerequisite (F10). Unmatch never grants rematch.
  - **Block and unblock:** `BlockIntent` runs `glow_chat`'s `block` and `unblock` unchanged. Block works after unmatch and while paused (F13). Unblock restores no match and no send (the writers already enforce it). Unblock restores discovery only through D3's ordinary predicates and D12's settings.
  - **Discovery after a block:** D3's BLOCK predicate, and D7's recheck of every entry.
  - **The alternative:** leave the unmatch and block routes to SV4 (chat's HTTP surface) or P07.2 (block and report). Revision 1 places them here because block and unmatch are what make a pair ineligible, and their writers exist.
- **D12 — Resurfacing, undo and rematch** (OD-60, R; the settings `discovery.resurfacing`, `discovery.undo`, `discovery.rematch`, all off at launch).
  - **Resurfacing and undo are built behind their settings, with tests for each setting on and off** (DM-60), since the console can switch them on (OD-60: "switchable with a waiting period"). Rematch is not built in SV3, and its setting refuses to be switched on until it is:
    - **resurfacing:** a passed candidate becomes eligible again after `waiting_days`. Off, a pass excludes the pair from the actor's pages for good;
    - **undo:** the actor's most recent pass can be withdrawn within `waiting_days` of it. Off, it cannot. The contract has no undo command (`InteractionIntent`'s actions are `like` and `pass`), so D13 adds what undo needs, and the flow registry adds its F08 entries. The directional row is kept and its version advanced, never deleted and created again, so an expected version from before the undo cannot match a later row. A withdrawn pass excludes nothing (D7's consumption);
    - **rematch:** not built in SV3 (DM-60). It needs a new F09 transition (`unmatched` to `active`), a fresh or reactivated chat binding after `unmatch` revoked contact, and a rule for what the pair sees of their old conversation (`chat.history`): all of it `glow_chat`'s contact protocol, beyond D10's one writer. So unmatch is final in SV3, and a new fixed limit, `rematch_not_built`, refuses a publication of `discovery.rematch` with `enabled` on. No route publishes a setting before P07's console, and the item that builds rematch comes before it (the carried-items file, SV4), so OD-60's "switchable" holds once the console exists. That item lifts the limit and keeps `rematch_never_after_block_or_report`: refused after any block between the pair, active or removed, and after any `SafetyReport` between them, whatever the setting says.
  - **The alternative:** refusal only, with the settings' publication refusing to switch them on until a later item builds them. That would need a new fixed limit and a contract note; it is smaller, but it makes the settings not switchable.
- **D13 — The contract.**
  - The existing DTOs are used unchanged where they fit: `PageRequest`, `CandidatePage`, `InteractionIntent`, `InteractionOutcome`, `InteractionCommandResult`, `MatchProjection`, `UnmatchIntent`, `BlockIntent` and `BlockOutcome`.
  - **The card:** `CandidateProfile` carries `profile_id`, `display_name`, `age`, `summary`, `media_delivery_refs` and `compatibility`. OD-60 has a profile show "looking for" always, and gender, orientation and relationship status when the member chooses, and the area's name may be shown. Two options:
    - **(a) recommended:** an additive DTO for the shown fields and the area's name, referenced from a new card wrapper in a new response, with every existing DTO unchanged, as SV2's D11 did. It carries "looking for" always, and gender, orientation and relationship status only while that field's `shown` flag is on, with the member's own words for gender and orientation (display only). The area's name rests on the second A05 message, which OD-60 answered: its location (a) "reveals only the area the member chose". The card never carries a "show me" set, a filter, an area ID, an internal point or a distance, and the contract's sentence that `location_label` "is intentionally not exposed by the present public allowlist" ("Compound actions and model projections") is rewritten to say what the card now shows (DM-60);
    - **(b):** revision 1 shows only what `CandidateProfile` holds, and the fields wait for P10.
  - **`media_delivery_refs`** holds approved variants only, through SV2's delivery reference (F05).
  - **Undo** (D12) has no DTO today: D13 adds a command DTO for it, and the outcome code and projection state it needs (`CommandReceipt`'s outcome codes and `InteractionOutcome`'s states have none), each as an added DTO or value and named in the report (DM-60).
  - **The production catalog's `paths` stay empty** until P11. The generated outputs and the flow registry change only as `npm run generate` writes them and D13's additions need, as in SV2 (its W1 to W10).
- **D14 — The proof: P06.DB's job, a fourth disposable database.**
  - **Where it runs:** a discovery suite in `proofs/postgres-ordering`, beside the identity and profile suites, with its own settings and marker, on a fourth database, `glow_discovery_proof`, in the same PostgreSQL 17.11. It applies the reviewed migrations from zero. It signs in through SV1's routes and builds members through SV2's routes. The seeded chart and identity-verification rows are written as SV2's suite writes them, in setup only.
  - **Concurrency from separate connections** (DB05, Stage B): simultaneous reciprocal likes, in both arrival orders, give one match and one `match_activated` event. Repeated likes with fresh keys give one row.
  - **Changes during an action** (DB10, Stage B): a block, unblock, pause, consent withdrawal, preference change or settings publication committed while a like waits on its locks is seen by the like.
  - **Pagination under change** (DB11, Stage A): stable pages within a batch; a candidate who becomes ineligible between pages is dropped; a viewer's own change makes the cursor stale; no duplicate across pages. Each candidate query's `EXPLAIN (ANALYZE, BUFFERS)` plan is recorded at a stated population size (proposed: 1,000 members), labelled as the disposable setup's measurement (PF01 P09: no extrapolation). That population is seeded directly in the suite's setup, as the chart and identity rows are, with every row completion requires, so each seeded `visible` profile is one SV2's recompute would make visible; only the cases' own members go through SV1's and SV2's routes, so the job stays within its 30 minutes (DM-60).
  - **The run's secrets** are generated and handled as SV1's and SV2's are. The secret check covers the new suite's log and results JSON before any upload.
  - **The timeout:** the job stays within its 30 minutes, and the evidence records the discovery phase's duration. If the four suites cannot fit, the session stops and reports. It does not raise the timeout (DM-16).
- **D15 — The seal, checked.** A test in the style of SV1's and SV2's proves two things: the runtime's settings, URL configuration and WSGI application import none of the new modules, and the database backend is the dummy one. `glow_api/` is not changed.
- **D16 — No new dependency** expected. Any new package stops the session.
- **D17 — Disclosure and the counsel question.**
  - D8's rules hold in every response, error, validation message, log line and outbox event. Events carry references, never values.
  - **Feeds and age** (UST-37, UST-38; the recheck): whether recommendations or broader discovery are an "addictive feed" or an "algorithmic feed" under California's SB 976 or New York's SAFE for Kids Act is a reading for counsel. Whether to take advice is Nathan's decision (DM-31). SV3 builds only the age-state gate (D3). The question is carried to the G-01 item and to the release gate's list (PF01 §7), not put to Nathan now.
- **D18 — Every test comes with its reversal,** recorded with its failing output, as SV1's and SV2's were.
- **D19 — One pointer order** (SV2's D19): every SV3 transaction takes its settings pointers in name order in its first `read_shared` call. The check SV2 built covers SV3's suite.

## Owned paths (the sessions)

- `services/api/glow_discovery/**` (new): the app, its views, URL configuration, the eligibility adapter, the batch and cursor code, and the interaction operations.
- `services/api/glow_domain/`: new modules only where the pure rules need them (the two-way rule, distance), and the existing `trusted_eligibility.py` and `eligibility.py` only for the protocol details the adapter needs, each change named in the report.
- `services/api/glow_chat/contact.py`: under D10 (a) only, the new `activate_reciprocal` writer; every existing writer unchanged.
- `services/api/glow_domain/profile_settings.py`: the fixed limit `rematch_not_built` only (D12; DM-60).
- `services/api/glow_persistence/models.py` and new migrations after `0009`: only the indexes and fields D2 to D12 need, each named in the report.
- `services/api/tests/`: new discovery, interaction and sealed-runtime tests; `test_model_definitions.py` where the models require.
- `services/api/pyproject.toml`: `[tool.mypy]`'s `files` only, which gains `glow_discovery`.
- `packages/contracts/production/gapp-api-v1.schema.json`, `openapi.json` (DTOs only, no paths), `corpus/shared-v1.json`, `flows-v1.json` (D13's DTOs in their flows, and the transitions SV3's writers make that the registry lacks, each as a new entry), `packages/contracts/README.md` (a section for SV3's additions) and the contract tests: D13's additions only.
- `apps/mobile/src/contracts/generated/**`, only as `npm run generate --prefix packages/contracts` writes it. If a mobile source, test or fixture would have to change for the Mobile checks job to pass, the session stops.
- `proofs/postgres-ordering/**`: the discovery suite, its settings, tests and locks.
- `.github/workflows/foundation.yml`: the Database proof checks job's steps only.
- `docs/architecture/data-model.md` (the rows named in Outcome item 11), `docs/architecture/production-contracts.md` (F07 to F10 and F13's index rows and their server mapping, and the `location_label` sentence in "Compound actions and model projections", D13), `docs/architecture/discovery-fixtures.md`, `interactions-fixtures.md`, `reciprocal-eligibility-fixtures.md` and `trusted-eligibility.md` (a note that the server exists, sealed), `docs/testing/p11-deferred-acceptance.md` (the partial evidence), and the evidence record.

## Manager-owned

- This brief, the carried-items file, the matrix, the handoff, the review log and Notion.
- **The CI policy's Database proof checks paragraph** (governing Markdown): the manager updates it in each stage, and the Dev Manager reads it at a named commit before that stage's PR merges.

## Exclusions

- `services/api/glow_api/**`: the runtime stays sealed.
- `services/api/glow_chat/**`, except D10 (a)'s writer: SV3 calls the existing writers unchanged.
- `services/api/glow_identity/**` and `services/api/glow_profiles/**`: SV3 uses SV1's actor and SV2's reads and writers unchanged. A change one of them needs stops the session.
- `apps/**`, except the generated contract outputs; `wordpress/**`; `proofs/stream-chat/**`; `scripts/**`; other workflow jobs; the `Dockerfile`; every environment template; `requirements.in` and `requirements.lock`.
- Any provider (an HDE adapter, Stream, a vendor), any provider credential or SDK, any staff HTTP route, any report or case writer, any device location permission in the app, any real member.

## Dependencies and inputs

- `main` at `3240ef0`; PF01 1.17 §1, §5, §6, §7 and §8; F07 to F10 and F13 with their DTOs; the data model; the contract; the P11 plan's DB04, DB05, DB10 and DB11; SV1's brief and record (the actor, the age port); SV2's brief and record (the settings store, the fields, the area table, completion, D19); `glow_chat`'s writers; OD-12, OD-49, OD-55, OD-60 and OD-61; the matrix's G-01 and the [SV3 recheck record](../testing/evidence/2026-11-11-sv3-matrix-recheck.md); P05's fixture domain (`glow_domain.discovery`, `glow_domain.interactions`, `glow_domain.trusted_eligibility`) as the behaviour the server must match.

## Acceptance checks

**In `services/api`, with `GLOW_ENV=test`, in a clean process environment:** `python manage.py check`, `python manage.py test tests --verbosity 2`, `ruff check .`, `ruff format --check .` and `mypy`, all clean. **In `packages/contracts`:** its tests, with the corpus run through Python and the generated validators, and `npm run check`. **In `apps/mobile`:** `npm run check` passes with the regenerated outputs and no other change. **In `proofs/postgres-ordering`:** its offline tests under `env -i`, Ruff and mypy.

**In CI, the Database proof checks job on the code head,** after the ordering, identity and profile suites, on the fourth database, through the HTTP endpoints:

1. **Each predicate** (Stage A), for the viewer and for the candidate: an age state outside the accepted set, a missing or old or withdrawn onboarding consent (a `sensitive_profile` decision alone included), each non-`visible` profile state, each non-`active` account state, and an active block in either direction each exclude, and each passes when restored. A missing row fails closed.
2. **The two-way rule** (Stage A): for each field, a match in one direction only excludes. A keep-all set matches "not stated" and a value the console adds after it was set. A narrowed set never matches "not stated". A missing orientation row reads as "not stated". A retired value stays matchable. A field made not narrowable reads as keep-all.
3. **Age** (Stage A): the range in both directions under `both_ways`; the leap-day cases agree between the SQL rule and `age_years`; no route returns a birth date.
4. **Distance** (Stage A): same area is zero; a choice in miles includes and excludes at its boundary; `anywhere` filters nothing; no route, error, log line or event carries a distance, a coordinate or an area ID.
5. **Pages** (Stage A): recommendations first by band, broader without the batch's recommended candidates; stable order within a batch; the cursor refused for another viewer, after expiry and after the viewer's own change; a candidate made ineligible between pages is dropped; no duplicate; `empty` with no provider call; the port's `pending` and `unavailable` states; at most 100 per batch and 50 per page; the query count per page; the recorded plans.
6. **Disclosure** (Stage A): D8's population-of-one case recorded; no count, no reason, no other member's private value in any response.
7. **Like and pass** (Stage B): idempotent repeat; changed payload conflicts; stale batch, wrong batch, a target outside the batch and an ineligible target are refused with nothing written; the target never sees an unreciprocated like.
8. **The match** (Stage B): reciprocal likes give one `Match`, one `match_activated` event and the chat binding's rows. Concurrent likes from separate connections, in both orders, give one. No route creates a match.
9. **Changes during a like** (Stage B): each change of D14's list, committed while the like waits, is seen.
10. **Unmatch and block** (Stage B): through `glow_chat`'s writers; a send refused after each; block after unmatch and while paused; unblock restores no match and no send; the blocked member cannot learn the direction.
11. **Resurfacing, undo and rematch** (Stage B): off at launch, each refuses; resurfacing and undo, each on with a waiting period, behave as D12 says; a publication of `discovery.rematch` with `enabled` on is refused, naming `rematch_not_built`, and writes nothing; after an unmatch, neither member appears in the other's pages, and no like makes a second match or reactivates the first.
12. **Ownership** (both stages): every route refuses an unauthenticated request and another member's match or batch, and answers a stale version with its version error.
13. **No secret and no private value in any output:** the job's secret check, and a log capture at `DEBUG`, find none.
14. **One pointer order** (D19): every SV3 transaction's pointer locks follow name order.

**Every test with its reversal** (D18), recorded in the evidence record.

## Classification expectation

Full scope: code, migrations, a contract change, a workflow change and the proof. The manager classifies with `main`'s trusted policy, inspects the complete workflow diff and the job's actual steps, and requires full checks before the merge (`AGENTS.md`).

## Report format

Each stage's prompt asks for:

- branch, code head and records head;
- the environment check and start gate;
- for each Outcome item, the files, tests and reversals;
- every command with its result line;
- the run of record: each job, the gate's line, the discovery suite's counts, the phase's duration, and whether a retry fired;
- the recorded query plans;
- what could not run;
- every deviation.

## Review plan

- **The manager verifies each stage's report** against the pushed branch: the complete diff within the owned paths, the seal, reversals re-run where useful, and the run of record's logs.
- **Then each stage's PR,** Codex's review of its head, and **an exact-head code and security review of that stage's final code head, with a written threat model.** Its focus:
  - who may see whom: each predicate, both directions, fail-closed reads;
  - the consistent view (D2): the single-statement selection, and the action's recheck under locks;
  - D8's disclosure rules in every response and every error;
  - the cursor's binding to viewer and batch;
  - the seal, and no fixture compatibility provider in the runtime;
  - who may contact whom (Stage B): idempotency, the match's uniqueness and its lock order, unmatch and block through `glow_chat`, and rematch's fixed limit;
  - D10's writer: every existing function and method in `glow_chat/contact.py` unchanged from `main`'s (compared by AST), `glow_chat`'s existing tests unchanged and passing, and no import of `glow_discovery`; `activate_reciprocal` the only new one, refusing everything `activate_match` refuses and a missing `liked` row in either direction, writing the same rows and events (the identity events and the one `match_activated` event), taking `activate_match`'s lock order and probe points, and called only from the like, after its recheck (DM-60);
  - the proof's secret handling.

  Stage A's review takes the items for seeing; Stage B's takes those for contact, and whatever Stage B changes in Stage A's code.
- **Dev Manager:** this brief, before any prompt (DM-60); each stage's design changes, if any; and, before each stage's PR merges, at a named commit, the CI policy's paragraph and the data model's and contract's rewritten texts. The prompts need no read of their own: they authorize no credential and no live action.

## Sessions

- **DM-60** (11 November 2026; [consultation](../ephemeral/2026-11-11-dm-60-sv3-brief.md), at `674e00e`): revision 1 to the Dev Manager.
- **DM-60 answered** (11 November; [report](../continuity/dev-manager/reviews/2026-11-11-dm-60-sv3-brief.md), at `777a6ad`, a read of `674e00e`): approved with Q1 to Q20 in given words, nothing referred to Nathan. Revision 2 applies them (merge `72791a7`).
- **Stage A's implementation prompt** ([prompt](../ephemeral/2026-11-11-sv3-stage-a-implementation-prompt.md)), revision 1, from `aa9ed70`; TypeSafe's reading in its header.
- **Stage A built** (11 November; session `session_01Q789u3fkmYbVMk8LUNFAjc`, branch `claude/loving-maxwell-cqu7eq`): code head `ad9ff08`, records `4dee875`. Its code head's push run 43096394432 was never dispatched by GitHub (the record's diagnostic), so no run of record exists yet. The manager verified it and integrated it by fast-forward (the record, "Manager verification of Stage A"); the pull-request run on the manager branch's head is the run of record (step 5).
