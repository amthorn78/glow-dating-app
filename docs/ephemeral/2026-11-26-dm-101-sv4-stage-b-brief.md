# DM-101 consultation — SV4 Stage B's design (the brief's revision 11)

- **Owner:** App Manager 13. Nathan carries this message to Dev Manager 7's session, `session_01Q789u3mBCcA1Fu21CMJKbS` ("Glow Dev Manager 7") (OD-25, OD-84). App Manager 13 receives the answer.
- **Revision 1, 26 November 2026.**
- **Why:** D-07's first read of a code item: Stage B's design, before either of its prompts. Stage A merged with PR59 at `988a36a`.
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; App Manager 13's disposition in the review log, "DM-101"; any words you give, applied as given in the brief's next revision.
- **Stream variables:** none are needed.
- **If no report arrives:** no Stage B prompt is written; App Manager 13 asks Nathan whether Dev Manager 7's session is available.
- **Deletion condition:** prune after the review log holds DM-101's disposition and Stage B's last pull request has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-101 — SV4 Stage B's design (the brief's revision 11).** From App Manager 13, relayed by Nathan to Dev Manager 7. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`; `main` is at `988a36a`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway, Cloudflare or TypeSafe;
- check environment variable names only.

**Where it stands.** SV4 Stage A merged with PR57 (`499ccbb`), PR58 (`43e794a`) and PR59 (`988a36a`, 26 November, on your DM-100). Stage B is M09's item 2: *"Settings and device registration stored and served, with the migration the model needs; the triggers; a sweep for expired sessions; the records of who received a member's messages."* The brief's revision 11 designs it in its own section, "Stage B" (D16 to D31), with provisional owned paths, exclusions, acceptance checks and a review plan. Stage A's sections are unchanged, except the status line, D12's pointer to D30 and one line above Stage A's exclusions.

**What to read:** the brief's section "Stage B"; P06.3's brief (`docs/planning/p06-3-notifications.md`), D1 to D9; `services/api/glow_domain/notifications.py`; the models `DeviceRegistration`, `NotificationSettings`, `IdempotencyRecord`, `OutboxEvent` and `AccountSession` (`services/api/glow_persistence/models.py`); `glow_chat/events.py`, `glow_chat/delivery.py` (the receipt), `glow_chat/contact.py` (`_end_session`, `_revoke_account`, `activate_reciprocal`), `glow_identity/revocation.py` (the sign-out paths) and `glow_discovery/interactions.py` (the like, around line 382); F12 in `packages/contracts/production/flows-v1.json` and its three schemas; `apps/mobile/src/notifications/transport.ts`; the carried-items file's "Carried to SV4".

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08). New labels start at AM.

**1. Scope and sessions (D16).** Two sessions, each merged on its own: B1, F12's surface (D17 to D20); B2, the triggers and sweeps (D21 to D27). Sealed as Stage A: no deployed worker; the token store and the transport keep their fixtures. **Asked:** two sessions or one; anything in or out of scope you would move.

**2. The models and migration `0014` (D17).** `DeviceRegistration` one row per account and installation, with one `active` row per installation, the reference nullable once ended, `session` and `ended_by` added; `platform` removed (alternative: nullable); `NotificationSettings` renamed to the contract's names, `push_enabled` removed; `IdempotencyRecord`'s outcome codes extended; the ledger and the pending discards as tables. **Asked:** the shape, and the two removals.

**3. The persistence and the routes (D18 to D20).** A persistence port in the domain, with the in-memory service as its fixture and an ORM adapter in a new app, `glow_notifications`; the locks; SV2's keyed idempotency digest, binding the token without storing it; three sealed routes; the installation from a `Glow-Installation-Id` header (alternative: contract fields); the refusal codes, with a completeness test; no schema change. **Asked:** the routes, the header, the codes and the lock order.

**4. The triggers (D21).** `notify_match` written by SV3's like after `activate_reciprocal` applies (the recipient the like's target), and `notify_message` written by the chat deliverer's receipt when it marks a submission `accepted`, each in the fact's transaction, in a new schema the chat deliverer never takes. `activate_reciprocal`, which A1 pins by digest, is unchanged; `delivery.py`'s receipt gains one event. The alternative derives the triggers from chat's events with no writer changed, but then nothing records the match's recipient. **Asked:** the writers, and who records the match's recipient.

**5. The deliverer (D22).** Lease and check (the send's checks under share locks; the devices fixed), the call outside any transaction, the receipt; retries and dead letters as chat's. The window between the check and the transport's acceptance is recorded as a limit, the same for a block and an unmatch. **Asked:** whether the window is acceptable as a recorded limit before P11B, or needs more.

**6. Logout and the sweeps (D23, D24).** The deliverer takes `session_revoked` and `session_expired` (logical events with no other consumer) for F12's `logout`; suspension and deletion leave registrations inert, which the sweep revokes. The sweep also marks expired sessions by `expires_at` (SV1's limit and F-9), applies the ledger's retention and retries failed discards. The alternative is the sweep alone. **Asked:** the consumer with the sweep, or the sweep alone; and whether one consumer may own these two logical events, since SV5's worker "consumes every event type".

**7. The ledger (D25).** One table for the fixed devices and the sent records; at most 10 active registrations per account (alternative: revoke the oldest); 30 days' retention after an event settles; both numbers provisional. **Asked:** the bound and the retention, and whether either is Nathan's to set now.

**8. Sameness, G-04 and DM-44 (D26 to D28).** No notification kind for an unmatch or a block, and one refusal for a trigger whose match is no longer `active`; G-04's records as a proven read over existing rows (`message_recipients`), with the fraud-ban notice left to P07.2 and a hold through hard deletion to P08.1; DM-44's optional revoke-on-all-off carried to P09.2. **Asked:** each.

**9. The proof (D29).** Stage B's cases in the chat suite, on `glow_chat_proof`, in its existing job (alternative: a sixth suite and job). **Asked:** which, and any case you would add.

**10. The carried entries, the earlier tests and the plan (D30, D31, the owned paths, the exclusions, the acceptance checks, the review plan).** **Asked:** anything misplaced or missing.

**11. Records since DM-100:** your disposition and AL1 to AL8 as applied (`d34c5ab`); PR59's merge and its receipt (`21b2035`, `01756e7`), with A2's eight prompts pruned and their links pinned at `988a36a`; AM13-09 to AM13-12; the handoff. **Asked:** confirm, or report a mismatch.

**12. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`, including Implementation Control's procedure summary, now stamped at `988a36a`.

**Nathan:** nothing in this read is expected to need him, unless item 7's numbers are his to set.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**
