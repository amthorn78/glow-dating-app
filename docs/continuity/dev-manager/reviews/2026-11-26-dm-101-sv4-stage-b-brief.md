# DM-101 — SV4 Stage B's design (the brief's revision 11)

- **From:** Dev Manager 7, `session_01Q789u3mBCcA1Fu21CMJKbS` ("Glow Dev Manager 7"), on `claude/dev-manager`, 26 November 2026.
- **To:** App Manager 13, through Nathan (OD-25, OD-84).
- **Consultation:** `docs/ephemeral/2026-11-26-dm-101-sv4-stage-b-brief.md`, revision 1, read whole at `8edd0030d9b80a960f3344dffe34d7e264fec9e2` of `claude/magical-wozniak-yfmmx2`. The message Nathan relayed matches the file, with `<RECORDS_COMMIT>` filled in. `main` is at `988a36a1fe4bc7b654a07e565e15fe721dcf3520`, and every change since it is Markdown.
- **Labels:** AM1 to AM16 are conditions, each with its words in section 15, for the brief's next revision.
- **Environment** (names only): no `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, `STREAM_*`, `RAILWAY_*`, `PG*` or `CLOUDFLARE_*` name. AWS and GitHub token names are present; none was read or used. I called no provider, database, HDE, Railway, Cloudflare or TypeSafe, and wrote nothing to GitHub or Notion.

## 1. Answers

| Item | Verdict | In short |
|---|---|---|
| 1 Scope and sessions (D16) | **Approved with conditions (AM1)** | Two sessions, B1 and B2, each merged on its own. Nothing to move in or out. AM1 makes the fixtures reachable only from the proof's settings, as A2's text reader is. |
| 2 Models and `0014` (D17) | **Approved with conditions (AM2)** | The shape is right, and both removals (`platform`, `push_enabled`) are right. AM2 makes the custody rules database constraints. |
| 3 Persistence and routes (D18 to D20) | **Approved with conditions (AM3 to AM7)** | The port, the three routes and the header are right. Four gaps: the session row is not locked; the token store's `put` has no place relative to the transaction; the idempotency digest leaves out the installation; some refusal codes are missing. The header also needs its threat stated. |
| 4 The triggers (D21) | **Approved with conditions (AM8)** | Write both events with their facts; the like records the match's recipient. AM8 says how the composer's "completed by" check then works. |
| 5 The deliverer's window (D22) | **Acceptable as a recorded limit before P11B, with AM9 and AM10** | Closing the window would mean a provider call inside a locked transaction, which is worse. But the limit must name every cause, not only block and unmatch, and stay short. A failed push must not hold up a logout. |
| 6 Logout and the sweeps (D23, D24) | **Approved: the consumer with the sweep, with AM11** | One consumer may own the two logical events: each outbox event has one state, and SV5 asks for a consumer for every event type. Record the ownership and use the device commands' locks. |
| 7 The ledger's numbers (D25) | **Approved with conditions (AM12)** | 10 active registrations and 30 days, both provisional. Refusing beyond the bound is better than revoking the oldest. **Neither number is Nathan's to set now**: route the bound to P10 and the retention to A05's list. |
| 8 Sameness, G-04, DM-44 (D26 to D28) | **Approved** | Each is right as written. A note on where the G-04 read lives (section 10). |
| 9 The proof (D29) | **Approved: the chat suite, with AM13 and AM14** | Add the cases the conditions above need. |
| 10 Carried entries and the plan (D30, D31) | **Approved with conditions (AM15, AM16)** | Fix the section name for DM-44's item, add five new carries, close "Carried to SV4" at Stage B's end, and add one earlier test to D31. |
| 11 Records since DM-100 | **Confirmed** | AL1 to AL8 as given at `d34c5ab` and still at `8edd003`; the merge, the receipt, the prunes, AM13-09 to AM13-12 and the handoff all match. |
| 12 Notion | **One small mismatch** | SV4's Evidence links the record at `d34c5ab`, before the merge receipt. Everything else I read matches, the procedure summary at `988a36a` included. |

**Nothing needs Nathan.**

## 2. What I read

- The brief: its status line, D12's changed bullet, the line above Stage A's exclusions, the whole section "Stage B" (D16 to D31, the owned paths, the exclusions, the acceptance checks and the review plan), and its session log's last entries. I also read the brief's whole diff from `main`.
- P06.3's brief: "Outcome" and D1 to D9.
- The code, at `8edd003`, which equals `main`'s:
  - `glow_domain/notifications.py`, whole (1,047 lines), and `notification_fixtures.py`'s guards;
  - the models `Record`, `OutboxEvent`, `AccountSession`, `DeviceRegistration`, `NotificationSettings`, `IdempotencyRecord` and `Match`;
  - `glow_chat/events.py`;
  - `glow_chat/delivery.py`'s docstring, its message plan with the `accepted` receipt, `_due_ids`, `_deliver` and `_settle`;
  - `glow_chat/contact.py`'s `_lock`, `_event`, `activate_reciprocal`, `open_session`, `sign_out`, `expire_session`, `_end_session`, the start of `send` and `_revoke_account`;
  - `glow_identity/revocation.py`'s docstring and its sign-out, expiry and suspension paths;
  - `glow_discovery/interactions.py`'s like (lines 340 to 400);
  - `glow_profiles/idempotency.py`;
  - `glow_chat/views.py`'s text-reader factory.
- The contract: F12 in `flows-v1.json`, and `NotificationSettings`, `DeviceIntent`, `NotificationIntent` and `CommandMeta` in the schema.
- The app: `apps/mobile/src/notifications/transport.ts`, `fixture-adapter.ts`'s device and settings paths, `client.ts`'s code mapping and `fixture-device.ts`.
- The carried-items file: "Carried to SV4" whole, "Carried to P08", the SV5 and P07.1 entries in "Routed by M09", and the list of sections.
- `data-model.md`'s device and notification lines; the P11 plan's PV05 row.
- The records since DM-100 (section 13), and Notion (section 14).

## 3. Item 1: scope and sessions (D16)

**Two sessions, approved.** B1 changes who may register and read an installation, and how a token is held. B2 changes who is told what, and when. Each is a security boundary with its own threat model, so each deserves its own exact-head review. B2 builds on B1's adapter and tables, so B1 merges first.

Nothing needs to move in or out. A real push, a vault, the app, a staff route, the fraud-ban notice and a hold that survives deletion are each rightly left to their owners.

**AM1.** D16 keeps the token store and the transport as fixtures, but does not say how the ORM adapter and the deliverer reach them. A2 set the pattern with its text reader (`GLOW_CHAT_TEXT_READER`): a factory named only by the proof's settings, so the served runtime names none and refuses without it. The fixtures already refuse outside development and test (`require_fixture_environment`). AM1 states the same rule for both ports, so that the seal is a property of the settings and not only of the imports.

## 4. Item 2: the models and `0014` (D17)

**The shape is right.**
- One row per account and installation is how the domain keys a registration (`Registration`, keyed by account and device).
- One `active` row per installation is the transfer rule.
- Recording the registration's session is F12's "owner/session bound".
- `ended_by` matches the domain's `EndedBy`.

**Both removals are right.**
- **`platform`:** no contract field carries it, nothing would write it before P09.2, and a nullable column with no writer only invites a guess.
- **`push_enabled`:** the contract has no such field, and `device_state` already says whether an installation can receive a push.

**The other parts are right.** The version semantics match the domain's, and the contract's `version` (minimum 1) is the registration's. The `IdempotencyRecord` outcome codes fit its 16 characters.

**AM2.** D17 states the custody rules in words: the reference is present exactly while `active`; `ended_by` is present exactly when `revoked`; there is one `active` row per installation. These rules are the custody boundary. Elsewhere in the models the same kind of rule is a check constraint (`AccountSession`'s `session_revocation_time`, `OutboxEvent`'s `outbox_lease_time`). AM2 makes these database constraints too, so no writer can leave a reference on a revoked row.

## 5. Item 3: the persistence and the routes (D18 to D20)

The port with the in-memory service as its fixture, the new app, the three sealed routes and "no schema change" are all right. Four gaps, and one threat to state.

### 5.1 The lock order (AM3)

D18 locks the account row, then the registrations, and reads the session "under the locks". But no lock in that list orders the command against its session's end:
- `_end_session` locks only the session row (`contact.py`'s `_lock`, `FOR UPDATE`);
- under READ COMMITTED, a register can read its session as `valid` while the sign-out holds that row;
- the register can then commit a registration for a session whose revocation committed first.

The sweep and the composer's session check would make that registration harmless later, but F12 says "logout revokes registration", and D23's consumer could miss a registration that commits after it runs. Chat's send and reads already lock their session row, after the accounts. AM3 does the same here (`FOR SHARE`, after the account row, before the registrations). No writer locks a session and then an account, so this order adds no deadlock.

AM3 also makes the settings read take the account and session rows `FOR SHARE`. Without that, two statements can see two commits, and the read could pair a new version with old switches.

### 5.2 The token store and the transaction (AM4)

D18 keeps P06.3's rule that "the store takes the token before its reference is saved", but does not say where the `put` runs. In memory it runs under one lock. In the ORM it is an external call. It must not run inside the command's transaction, as P06.DB keeps every provider call out of one. Running it before the transaction leaves one case to settle: a command that then does not save the new reference (a refusal, a failure or a replay). AM4 sends that reference to the pending discards, so no token stays in the store without a registration or a discard.

D18's last sentence is also not true as written: "none but the transport holds a reference". The registration's row and a pending discard's row hold references by design. AM4 replaces it with what custody actually is.

### 5.3 The idempotency digest (AM5)

SV2's digest (`glow_profiles/idempotency.py`) binds the intent's body only. A `NotificationIntent` names no installation, which comes from the header. So the same key and body sent from another installation would replay, where the domain's digest, which includes `device_id`, makes it a conflict. P06.3's domain "stays authoritative" (`fixture-adapter.ts`). AM5 binds the installation into the digest.

### 5.4 The codes (AM6)

The mapping D19 gives is right, and matches what the app already expects (`client.ts`):
- `not_found` on a read is the explicit absence;
- `forbidden` and `not_found` are "unavailable";
- `state_conflict` is "not active";
- `unauthenticated` is "signed out".

A session reason inside the locks rightly stays `unauthenticated` here, unlike the send's (DM-99): these routes concern only the member's own account and installation, so no cause of the other member's is at stake.

Missing from the list: the bound (D25), a transfer whose other account changed under the locks, a registration the one-active constraint refuses, and a deadlock or database error. AM6 adds them and names the session reasons. It also asks that a 401 from inside the locks carry `WWW-Authenticate: Bearer`, as the door's do, so B1 does not repeat A2R-11.

### 5.5 The header (AM7)

**The header is right.** It is the domain's `Caller.device_id`, which "never comes from an intent's fields". The app already sends the installation as a header (`transport.ts`), and the alternative would change `main`'s contract and the app's types.

One threat follows from the transfer rule. A signed-in member who presents another account's installation identifier revokes that account's registration of it: the shared-device case by design, a denial of pushes otherwise. Nothing leaks: the member's answer depends only on their own registration (`_register`'s version). But the identifier is in effect a capability, and today the app's is a fixed constant (`FIXTURE_INSTALLATION_ID`). AM7 states the rule (never served, logged or shown; made at random for each installation) and puts it in B1's threat model; AM15 carries it to P09.2.

## 6. Item 4: the triggers (D21)

**Approved: write both events with their facts, and let the like record the match's recipient.**
- **`notify_match`:** the like knows its actor and its target, and the target is P06.3's recipient. Writing the event in the like's transaction, after `activate_reciprocal` applies, makes it atomic with the match. `activate_reciprocal` stays as A1 pinned it.
- **`notify_message`:** the receipt's `accepted` step changes the row only when it goes from `pending` to `accepted`, so one event per acceptance follows. A refused or dead-lettered message writes none.
- **The chat deliverer never takes either event:** `_due_ids` selects only the chat schema and `DELIVERED`.
- **The alternative is worse:** it would need a second reader of chat's delivered events (the outbox has one state per event, so a progress table), and it still records no recipient.

**AM8.** The composer checks "never the member whose like completed it" against `MatchFacts.completed_by`, read from facts, "never from the trigger". `Match` has no completer column, so the ORM's facts can only give `completed_by` as the participant who is not the event's recipient. That makes the check true by construction: the rule rests on the like's writer, not on an independent fact. That is acceptable, because the writer is trusted code in the fact's own transaction and D29's case "a match notifies the earlier liker only" proves it. But the brief should say so, so that B2's review does not count the check as an independent guard. Deriving the completer from the two likes' `decided_at` would not be reliable: under lock waits the later transaction can hold the earlier time.

## 7. Item 5: the deliverer's window (D22)

**Acceptable as a recorded limit before P11B.**
- Stage B is sealed, and its transport is a fixture, so no real push crosses the window.
- The content is fixed and generic, and names no one.
- Closing the window would mean making the transport call inside the transaction that holds the share locks. Every block, unmatch and revocation would then wait on a network call, which is worse than the window.
- P11B owns the real transport (PV05).

But the limit as written names only "a block or unmatch". Everything the check reads can change in the window:
- either account's suspension or deletion;
- a pause, a restriction or a withdrawn consent;
- a setting turned off;
- the registration revoked or transferred, or its session ended.

The last case sits on F12's revocation rule. One real case: a member signs out of a shared device, and a push queued for them arrives after the sign-out. If the installation was transferred, it arrives on the device the other account now uses. The content is generic, but the case should be on the record. **AM10** names every cause, keeps the window short (each attempt checks for itself, and the calls follow the lease's commit at once), and carries one narrowing to P11B: resolve the reference only at call time, so a token already discarded is never pushed.

**AM9.** D22 says a failed call is "retried with backoff … as chat's are". Chat's deliverer keeps a retried event at the head, with `available_at` unchanged, so nothing overtakes it. For notifications that would let one failing push hold up every later event, the session events of D23 included. AM9 makes the backoff move `available_at`: notification events are independent, and a logout must not wait behind a push.

## 8. Item 6: logout and the sweeps (D23, D24)

**The consumer with the sweep, approved.** With the sweep alone, a signed-out session's registrations would stay `active` until the next sweep. They would be harmless, because the composer refuses a registration whose session is not current, but their tokens would stay in the store longer than F12's "logout revokes registration" implies. The consumer revokes them promptly. The sweep catches what no event announces: a suspension or deletion moves only the epoch, and `_revoke_account` writes no session event.

**One consumer may own `session_revoked` and `session_expired`.** An `OutboxEvent` has one `state`, so each event has one consumer by construction. SV5's entry ("Routed by M09") asks for "consumers for every event type", and giving these two their consumer is what that asks for. The cost is that any later reader of either needs events of its own or a progress table. **AM11** says so and records the ownership where SV5 will read it. The deliverer selects exactly its four types. The revocation takes the device commands' locks, the account row and then the registrations, and is idempotent.

**The sweeps (D24) are right as written.**
- They find expired sessions by `expires_at`, never through the actor (F-9).
- `expires_at` is written only by `open_session`, so the sweep's unlocked selection is stable.
- `expire_session` is the reviewed writer, and each step is its own short transaction.

## 9. Item 7: the ledger's numbers (D25)

**10 active registrations and 30 days, approved as provisional.**

**Refusing beyond the bound (`state_conflict`) is better than revoking the oldest.** Revoking the oldest would end another installation's registration on the member's behalf. F12 gives the owner `revoke` only from the requesting installation (D19's `forbidden`), and the device revoked may still be in use. The bound also keeps one event's calls few enough to fit the lease.

**The bound has a limit to record:** a member at the bound cannot register another installation until one ends, and the app lists no devices. A member who reinstalls often, within their sessions' lifetimes, could reach it.

**Neither number is Nathan's to set now.** No real member exists before integration, and both are inside a sealed build. They become his before real members exist:
- **the bound,** at P10's readiness review, with the limit above;
- **the retention,** with A05's other retention values (D25 already says "A05 owns retention"), in the list A05's third message owes (H-16, "Routed by M09", for P07.1), beside the request keys' 24 hours.

AM12 says this in D25, and AM15 adds the carries.

## 10. Item 8: sameness, G-04 and DM-44 (D26 to D28)

**Each is approved as written.**
- **D26, sameness:** a block now stores `unmatched` (A1's D4), so the composer refuses both a block and an unmatch with `match_not_active` before it reaches the block check. Both kinds of trigger are refused the same way, and the window is the same for both (AM10).
- **D27, G-04:** a proven read over existing rows is right. `MessageSubmission` rows are never deleted by any writer today, and the hold through hard deletion is P08.1's.
  - A note, not a condition: G-04 is a record of chat, and P07.2's staff tooling will read it. Owning it in `glow_notifications` is acceptable for now, but the read should name only accounts and a yes or no, never text, and stay unserved and unimported by the runtime.
- **D28, DM-44:** carrying it is right, since no real token exists before P09.2. Turning both kinds off keeps the registration, so turning one back on needs no new prompt.

## 11. Item 9: the proof (D29)

**The chat suite, approved.** F12 and the triggers are chat's flows, their cases need chat's matches, messages and deliveries, and the job's checks stay as D2 set them. A sixth suite would add a job, a database, a decoy, a scan and a CI policy change for no gain.

Two points for B1's prompt:
- the suite's scan should hold the synthetic push tokens among its secrets;
- a case should query the rows for the token, since the scan reads only the output and the results JSON.

**Cases to add, AM13 and AM14,** each with its reversal:
- **For B1:** the session lock (AM3); custody on a refused command (AM4); the installation in the digest (AM5); two accounts registering one new installation at once; a transfer that changes under the locks.
- **For B2:** a retried push that holds no later event (AM9); the window, pinned as recorded (AM10), so that a later change that closes it shows; the two deliverers' selections.

## 12. Item 10: carried entries, earlier tests and the plan (D30, D31)

**D30's dispositions are right.** One section name is wrong and some carries are missing; AM15 fixes both.
- **The section name:** there is no "Carried to P09.2" section. The section is "Carried to P09 (security, native quality and release preparation)". The installation identifier's rule (AM7) goes there too.
- **The new carries:**
  - to H-16's list, the ledger's 30 days;
  - to P08, export and deletion of the registrations, the ledger rows and the pending discards, with an account's deletion discarding its active tokens first;
  - to P10, the bound (AM12);
  - to the P11 plan's PV05, the transport resolving a reference only when it calls (AM10).
- **Closing "Carried to SV4":** the section's own rule is that each entry stays "until the stage that takes it merges, or until the brief moves it". Several entries outlive SV4: G-05, G-12 (to an EU launch, D12), DM-54's (P08's rule), and the per-file entries left by A0, A1 and A2. AM15 moves each to its next owner at Stage B's last receipt, so the section does not outlive its item.

**D31's earlier tests:** add the offline tests that pin the chat suite's settings and URL modules (A2's), since B1 adds the factories (AM1) and its routes there. That is AM16. The rest of D31 matches what the code shows. In particular, B2's change to the like is in `interactions.py`, not in `activate_reciprocal`, so A1's digest pin on `contact.py` holds.

**The owned paths, the exclusions, the acceptance checks and the review plan are right.** `contact.py`, `reads.py`, `route_reads.py` and `glow_identity/` stay out, and the sweep calls `expire_session` as it is. The two threat models name the right boundaries. AM3 to AM7 and AM9 to AM11 add what those reviews must read.

## 13. Item 11: records since DM-100

Confirmed:
- **AL1 to AL8:** each applied as given at `d34c5ab` and still so at `8edd003`. A script checked each new passage once, each old one gone or inside its new one (AL4, AL5).
- **PR59:** merged at `988a36a` from head `d34c5ab` (17:18:38 UTC).
  - Its PR run 45865046893 passed all twelve jobs, and Codex completed on `d34c5ab` with no findings.
  - Its three threads are resolved.
  - `git diff --name-only ddb1386 d34c5ab` lists only Markdown.
  - `main`'s push run 45866641384 passed all twelve jobs.
- **The branch cleanup:** it left three branches, the same three `git ls-remote` shows now.
- **The prunes:** the eight files removed, and every link to them in the brief, the record and the review log pinned at `988a36a` or at the commit each was given from. The only links to the removed files that are not pinned are in my own DM-99 and DM-100 reports, which the manager does not edit; the review log pins both consultations. No action needed.
- **AM13-09 to AM13-12** state what happened. AM13-10's "with the session ID added" holds: Implementation Control now names `session_01Q789u1QcddHeBkXgnQ6Lis`, which `get_session` shows is "Glow App Manager 13", in `Glow App - No Stream`, created by App Manager 12's session.
- **The review log's DM-100 section** matches my report, AL9 waiting in the deferred conditions.
- **The handoff** matches the branches, the merge and DM-101.

## 14. Item 12: Notion

What I read, each saved and parsed with `python3 -I`:
- **Implementation Control** (last edited 17:46:09 UTC): its status heading and the opening of its status paragraph; the "Next items" bullet's SV4 part; the "Dev Manager", "Manager", "Main" (start and end), "Branches" (first 1,500 characters) and "Mistakes log" (first 1,500) bullets; the procedure summary (lines 111 to 124), with every link it pins. I did not read the page's history paragraphs.
- **The Dev Manager page** (17:46:15 UTC): Dev Manager 7's session row, and the DM-100 and DM-101 rows.
- **The register copy:** all 84 rows, compared by script with the repository's register.
- **SV4's Work Register row:** whole.

Matching at `8edd003`:
- the status, matched at `8edd003`;
- "Next items" (Stage A complete; Stage B with DM-101);
- "Dev Manager" (DM-101; labels from AM);
- "Manager" (App Manager 13's session ID; the branch as PR58's and PR59's head until each merged);
- "Main" (`988a36a`; no open pull request; the three threads resolved);
- "Branches" (three; `15a5646` now listed);
- "Mistakes log" (to AM13-12);
- the procedure summary: stamped at `988a36a`, all ten of its links pinned there, and no governing Markdown changed since;
- the Dev Manager page's rows;
- the register copy: OD-01 to OD-84, differing from the repository only in link text, in the same eight rows as before;
- SV4's "Next Action".

**One small mismatch:** SV4's Evidence links the record at `d34c5ab`, which has no "Merge (26 November 2026)" receipt. The receipt is at `21b2035`, as the row's Next Action says. Pin the record's link at `21b2035` or later.

## 15. The words

Each old passage is in `docs/planning/sv4-chat-notifications.md` and occurs exactly once at `8edd003`, checked by script. Each new passage then occurs once.

**AM1** — `docs/planning/sv4-chat-notifications.md` (D16: how the adapter reaches the fixtures):

> ```
> The token store and the push transport keep their fixtures only (P06.3's D1): P09.2 brings the native module and the real token, P11B the transport.
> ```
> ```
> The token store and the push transport keep their fixtures only (P06.3's D1): P09.2 brings the native module and the real token, P11B the transport. The ORM adapter and the deliverer take them from factories that only the proof's chat settings name, as A2's history read takes its text reader (`GLOW_CHAT_TEXT_READER`); the served runtime names none, and whatever needs one refuses without it (`provider_unavailable`).
> ```

**AM2** — `docs/planning/sv4-chat-notifications.md` (D17: the custody rules as constraints):

> ```
>     - `token_secret_ref` becomes nullable: required while `active`, cleared when the registration ends (the domain holds the reference only while active), unique where present;
> ```
> ```
>     - `token_secret_ref` becomes nullable: required while `active`, cleared when the registration ends (the domain holds the reference only while active), unique where present. That rule, `ended_by`'s (below) and the one `active` row per installation are database constraints, as `AccountSession`'s revocation time and `OutboxEvent`'s lease time are;
> ```

**AM3** — `docs/planning/sv4-chat-notifications.md` (D18: the session row in the lock order; the read's locks):

> ```
> a device or settings command locks the account row (`FOR NO KEY UPDATE`, the account writer's lock since SV3's C1), then the registrations it changes by primary key.
> ```
> ```
> a device or settings command locks the account row (`FOR NO KEY UPDATE`, the account writer's lock since SV3's C1), then the requesting session's row `FOR SHARE`, as chat's send and reads lock theirs, so a command and its session's end are ordered and no command commits for a session whose end committed first; then the registrations it changes by primary key. The settings read takes the account and session rows `FOR SHARE`, so it reads one committed state of the settings and the registration.
> ```

**AM4** — `docs/planning/sv4-chat-notifications.md` (D18: where the token store's `put` runs; who holds a reference):

> ```
> No row, log line, answer, exception or receipt holds a token, and none but the transport holds a reference.
> ```
> ```
> The store's `put` runs before the command's transaction, never inside it, so no external call holds a lock; a command that does not save the new reference (a refusal, a failure or a replay) sends it to the pending discards, so no reference outlives both its registration and a discard. No row, log line, answer, exception or receipt holds a token. A reference is held only by an active registration's row, a pending discard's row and the push request handed to the transport; no read, log line, answer, exception or receipt holds one.
> ```

**AM5** — `docs/planning/sv4-chat-notifications.md` (D18: the digest binds the installation):

> ```
> The digest binds the canonical intent, the token included, so a replay with another token is `idempotency_conflict`; the token itself is never stored.
> ```
> ```
> The digest binds the canonical intent, the token included, and the requesting installation from the header, as the domain's digest does, so a replay with another token, or the same body under the same key from another installation, is `idempotency_conflict`; the token itself is never stored.
> ```

**AM6** — `docs/planning/sv4-chat-notifications.md` (D19: the missing codes):

> ```
> the token store's refusal, `provider_unavailable` (retryable). A test proves every refusal reason the adapter can raise maps to one code (DM-99's AK2 pattern).
> ```
> ```
> the token store's refusal, `provider_unavailable` (retryable); the bound (D25), a transfer whose other account changed under the locks, and a registration the one-`active`-row constraint refuses, `state_conflict`; a deadlock or a database error, `state_conflict` (retryable for a deadlock), as `chat_projections.error_for` maps them. Each session reason (`session_missing`, `session_not_owner`, `account_missing`, `account_not_active`, `session_not_valid`, `session_expired`, `session_epoch_stale`, and the locks' `<table>_missing` forms for the member's own rows) is `unauthenticated`: these routes concern only the member's own account and installation, so no cause of the other member's is at stake. Each 401, at the door or inside the locks, carries `WWW-Authenticate: Bearer` (A2R-11's point). A test proves every refusal reason the adapter can raise maps to one code (DM-99's AK2 pattern).
> ```

**AM7** — `docs/planning/sv4-chat-notifications.md` (D19: the installation identifier as a capability):

> ```
> A `DeviceIntent`'s `device_id` must equal it (`forbidden` otherwise). `production-contracts.md` documents the header.
> ```
> ```
> A `DeviceIntent`'s `device_id` must equal it (`forbidden` otherwise). `production-contracts.md` documents the header. The installation identifier works as a capability for a transfer: a signed-in member who presents another account's installation revokes that account's registration of it. So it is never served, logged or shown, and the app makes it at random for each installation (P09.2; D30); B1's threat model reads it.
> ```

**AM8** — `docs/planning/sv4-chat-notifications.md` (D21: what the composer's recipient check rests on):

> ```
> (P06.3's rule; the like's actor sees the match in its own answer). `glow_chat`'s `activate_reciprocal`, which A1 pins by digest, does not change;
> ```
> ```
> (P06.3's rule; the like's actor sees the match in its own answer). `Match` records no completer, so the ORM's facts give the composer's `completed_by` as the participant who is not the event's recipient: the recipient rule then rests on the like's writer, and D29's case "a match notifies the earlier liker only" proves it. `glow_chat`'s `activate_reciprocal`, which A1 pins by digest, does not change;
> ```

**AM9** — `docs/planning/sv4-chat-notifications.md` (D22: no event held behind a retried push):

> ```
> a failed call retried with backoff, then dead-lettered after `MAX_ATTEMPTS`, as chat's are.
> ```
> ```
> a failed call retried with backoff, then dead-lettered after `MAX_ATTEMPTS`, as chat's are. Unlike chat's, a retried event's `available_at` moves by its backoff, so it holds no later event: notification events are independent, and a logout (D23) must not wait behind a push.
> ```

**AM10** — `docs/planning/sv4-chat-notifications.md` (D22: the window, whole):

> ```
>   - **The window, recorded as a limit:** a block or unmatch that commits after the check and before the transport accepts does not stop that push. Its content says nothing about the other member, and the same window exists for a block and an unmatch (D26). P11B's provider reconciles duplicate paths (PV05).
> ```
> ```
>   - **The window, recorded as a limit:** whatever the check reads, changed after it and before the transport accepts, does not stop that push: a block or an unmatch, either account's suspension or deletion, a pause, a restriction, a withdrawn consent, a setting turned off, or the registration revoked or transferred or its session ended. Its content says nothing about the other member, and the same window exists for a block and an unmatch (D26). The window is kept short: each attempt runs its own check, no call follows an earlier attempt's check, and the calls start as soon as the lease's transaction commits. P11B's transport resolves a reference only when it calls, so a push whose token was discarded first (after a revoke, a logout or a transfer) is not sent; P11B's provider reconciles duplicate paths (PV05).
> ```

**AM11** — `docs/planning/sv4-chat-notifications.md` (D23: one consumer, recorded; the logout's locks):

> ```
> and revokes every active registration that session made, discarding each token after the commit (recommended).
> ```
> ```
> and revokes every active registration that session made, discarding each token after the commit (recommended). It is their one consumer: an outbox event has one state, so a later reader of either needs events of its own or a progress table. `data-model.md` ("Chat contact and the outbox") and the carried-items file's SV5 entry ("Routed by M09") record the ownership, and the deliverer selects exactly its own two types and these two. The revocation takes the device commands' locks (the account row, then the registrations), and a registration already revoked is no change.
> ```

**AM12** — `docs/planning/sv4-chat-notifications.md` (D25: the bound, and who sets the numbers):

> ```
> The number is provisional, for Nathan to change; the alternative is to revoke the least recently registered.
> ```
> ```
> The number is provisional, for Nathan to change; the alternative is to revoke the least recently registered, which would end another installation's registration, a transition F12 gives the owner only from that installation (D19's `forbidden`). Neither this number nor the retention below is Nathan's to set now, since no real member exists before integration: P10's readiness review confirms the bound, with its limit that a member at the bound cannot register another installation until one ends, since the app lists no devices; the retention joins A05's list (D30).
> ```

**AM13** — `docs/planning/sv4-chat-notifications.md` (D29: B1's added cases):

> ```
> no token in any row, log line or answer, checked by the suite's scan; the bound;
> ```
> ```
> no token in any row, log line or answer, checked by the suite's scan; the bound; a register that reaches its session's row while that session's sign-out holds it (held at its commit) is refused once the sign-out commits (D18's order); a register refused after the store took its token leaves the reference in the pending discards and in no registration; the same key and body from another installation is `idempotency_conflict`; two accounts registering one new installation at once, and a transfer whose other account changes under the locks, each end with one `active` row and a refusal for the other;
> ```

**AM14** — `docs/planning/sv4-chat-notifications.md` (D29: B2's added cases):

> ```
> D26's sameness; D27's read after an unmatch and a block; the retention.
> ```
> ```
> D26's sameness; D27's read after an unmatch and a block; the retention; a push retried with backoff holds no later event, so a logout behind it is delivered first; the window as recorded (a block committed after the check and before the call does not stop that push, which a later change that closes the window would show); the deliverer takes no event but its four types, and chat's deliverer takes neither notification type.
> ```

**AM15** — `docs/planning/sv4-chat-notifications.md` (D30: the section name, the new carries, the closing sweep):

> ```
>   - **Moved:** DM-44's optional item to "Carried to P09.2" (D28).
> ```
> ```
>   - **Moved:** DM-44's optional item to "Carried to P09", for P09.2 (D28), with the installation identifier's rule: made at random for each installation, never served, logged or shown (D19).
>   - **New carries:** to the list A05's third message owes (H-16, "Routed by M09", for P07.1), the ledger's 30 days beside the request keys' 24 hours (D25); to "Carried to P08", the registrations, the ledger rows and the pending discards in export and deletion, an account's deletion discarding its active registrations' tokens first; to "Carried to P10", the bound of 10 active registrations, with its limit (D25); to the P11 plan's PV05, the transport resolving a reference only when it calls (D22).
>   - **At Stage B's last merge receipt,** every entry still in "Carried to SV4" moves to the section of its next owner (G-05 to P08.1; G-12 to an EU launch; DM-54's to P08; each per-file entry to the next change of its file), so the section closes with SV4.
> ```

**AM16** — `docs/planning/sv4-chat-notifications.md` (D31: one more earlier test):

> ```
> Known now, each to be confirmed by the prompt's sweep: `tests/test_notifications.py` and its seal test;
> ```
> ```
> Known now, each to be confirmed by the prompt's sweep: `tests/test_notifications.py` and its seal test; the offline tests that pin the chat suite's settings and URL modules, where B1 names the fixtures' factories (D16) or its routes there;
> ```

## 16. Checks

- `git fetch`; `git rev-parse`: the manager branch at `8edd003`, `main` at `988a36a`, `claude/dev-manager` at `0256d2c`, merged into the manager branch. `git diff --name-only 988a36a 8edd003` lists only Markdown.
- `git ls-remote origin`: three branches (`main`, the manager branch, `claude/dev-manager`). GitHub, REST `GET` only: PR59 (merged at `988a36a`, head `d34c5ab`), runs 45865046893 and 45866641384 and their jobs, PR59's three threads (resolved) and Codex's summary state on `d34c5ab`; no open pull request.
- A script on DM-100's section 13 found AL1 to AL8 as given at `d34c5ab` and at `8edd003`.
- A script found each pruned file's links pinned, the only unpinned ones in my own DM-99 and DM-100 reports.
- A script found each of AM1 to AM16's old passages exactly once in the brief at `8edd003`, applied the sixteen pairs to a copy, and found each new passage once.
- `get_session` (read only) on the session Implementation Control names for App Manager 13: "Glow App Manager 13", in `Glow App - No Stream`, created by App Manager 12's session.
- Notion, read only: as in section 14.

Status: complete
