# DM-58 consultation — SV2 Stage B: five of the session's decisions, and DM-57's conditions as applied

- **Owner:** App Manager 10. Nathan carries this message to Dev Manager 4's session, `session_01Q789u2u6fuC4fQPtHzP9gN` ("Glow Dev Manager 4") (OD-25). App Manager 10 receives the answer.
- **Revision 1, 11 November 2026.**
- **Why:**
  - Stage B's implementation session recorded sixteen decisions.
  - Five of them touch a contract, a security boundary or the data model's rules. Step 6 of the manager workflow ("Fix or carry, by rule") sends those to the Dev Manager before the exact-head review.
  - This is also the next consultation, which confirms DM-57's U1 to U11 as applied.
- **Where the result goes:**
  - your report in `docs/continuity/dev-manager/reviews/`;
  - App Manager 10's disposition in the review log, "DM-58";
  - any correction prompt or carried item your words call for;
  - the exact-head review's prompt.
- **Stream variables:** none are needed.
- **If no report arrives:** no exact-head review prompt goes to Nathan; App Manager 10 asks Nathan whether Dev Manager 4's session is still available.
- **Deletion condition:** prune after the review log holds DM-58's disposition and SV2's Stage B PR has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision, and every `<PR>` with the Stage B PR's number.

---

**DM-58 — SV2 Stage B: five of the session's decisions, and DM-57's conditions as applied.** From App Manager 10, relayed by Nathan to Dev Manager 4. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway or Cloudflare;
- check environment variable names only.

**Where it stands.**
- **Stage B is built.** The session's branch is `claude/sweet-ramanujan-wkn311`, with the code head `d8f1bad` and the records head `e7d6616`.
  - Its run of record is push run 42947095725 on `d8f1bad`. Every job passed, and the profile suite passed 64 of 64, with both scans clean.
  - The session's record is the evidence record's "Stage B" (`docs/testing/evidence/2026-11-10-sv2-profiles-media.md`). Its sixteen decisions are under "Decisions and deviations for the manager".
- **The manager's verification** follows it, in "Manager verification of Stage B": scope, classification, re-runs, three offline reversals, the run of record and the dispositions.
- **PR #<PR>** is open from the manager branch to `main`. Its run and Codex are in progress or recorded on the PR.
- **Nothing in the code has been changed by the manager.**

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. The collection's version is derived** (the session's decision 1).
- **What the code does:** `MediaCollection.version` is 1 plus the sum of the account's asset versions (`glow_profiles/media.py`, `collection_version`). It uses no new column.
- **What it rests on:** every creation and transition bumps an asset's version, and no asset row is deleted. The data model's `MediaAsset` row already says "Rows are never deleted".
- **The risk:** a later retention decision that deletes asset rows (A05's third message, G-05) would lower the version. A stale `expected_version` could then match again.
- **Recommended:** approve. Any later deletion of asset rows first stores the version.
- **Asked:** a verdict, and whether that condition needs words now (the data model, or the carried items for the retention message).

**2. A grant's expiry is judged by the store's upload time** (decision 2).
- **What the code does:** `record_upload` adopts a completion only if `event.uploaded_at <= grant.expires_at`, and `used_at` records that time. A completion that is processed late, for an upload made in time, is still adopted. The time comes from the storage adapter's authenticated event.
- **Why:** R2's events reach a consumer through Queues (the media provider mapping). The time Glow processes an event is therefore not the time of the upload.
- **The risk:** the check is only as good as the event's time and its authentication. Both are P11's to verify (PV04, DB08).
- **Recommended:** approve, with a P11 plan line: the upload time used is the store's own, read from an authenticated event, and an upload after the credential's expiry is refused by the store itself.
- **Asked:** a verdict; and, if the P11 line is a condition, its words.

**3. Removed photos are outside the collection** (decision 3).
- **What the code does:**
  - Every state except `removed` counts toward the collection's 20 entries (`request_upload`), so a rejected photo still counts until the member removes it.
  - The collection read omits removed photos (`_current`), and `read_asset` still returns one by its ID.
- **What P04.3's fixture did:** it kept removed tombstones within the 20-entry bound, and "a full collection requires an explicit fresh fixture session" (`docs/architecture/private-media-fixtures.md`, "Provisional development policy and byte checks"). A server has no fresh session, so that rule would stop an account after 20 uploads in its lifetime.
- **Options:**
  - **(a)** the server's reading as built, recorded in the media fixtures note's server section and the contract document (recommended);
  - **(b)** keep removed photos in the read within the bound, with a rule for which to drop.
- **Asked:** a verdict. If (a), the words for the two records. If (b), the rule.

**4. The ports are called inside the transaction** (decision 6).
- **What the code does:** each port is called inside its operation's transaction, which holds the account row lock:
  - the store's upload credential (`request_upload`);
  - processing and the seam (`review`);
  - the check and the delivery reference (`run_check`);
  - the deletion request (`request_purge`).
- **The data model's unit-of-work table** puts provider work after the commit: "Provider revocation/purge" for deletion, and "Narrow provider action" for staff actions.
- **In SV2,** the adapters are fixtures with no external effect. With real adapters, a rollback after a call could leave three things:
  - a credential with no grant, which no completion can use (`no_grant_for_key`);
  - an orphaned variant;
  - objects deleted while the asset stays `removal_pending`, so the purge can be asked again.

  Each call also runs while the account row's lock is held.
- **Options:**
  - **(a)** accept it for SV2, and carry to P11: the real adapters' calls move after the commit (the outbox and a worker), or P11 records why one stays inside, and the unit-of-work table gains F05's row (recommended);
  - **(b)** a correction in Stage B that moves the calls after the commit.
- **Asked:** a verdict, and the words for the carried item or the table's row.

**5. The owner's read shows the reference during a hold** (decision 10).
- **What the code does:** when the check approves a photo, it stores the variant's delivery reference (`approved_variant_ref`). Two reads return that same stored string:
  - the owner's `MediaLifecycle` returns it whenever the photo is `approved`, because the schema requires a reference in that state;
  - `delivery_reference`, P11's delivery read with no route in SV2, returns it only when the photo is approved, unrestricted, not being removed and not held. It asks the hold port.

  The brief's checks say "approval, delivery and a removed asset's purge each ask the hold port first".
- **The risk:** if P11's delivery resolved a reference to bytes on its own, an owner holding the reference could get past a hold.
- **Options:**
  - **(a)** approve: the reference is an opaque string, not delivery. Carry to P11 (PV04): delivery resolves a reference to bytes only through a read that checks the state, the restriction, the removal and the hold, never from the reference alone (recommended);
  - **(b)** withhold the owner's reference during a hold. That needs a contract change, because the schema requires a reference while the photo is `approved`.
- **Asked:** a verdict, and the carried item's words.

**6. The manager's settled items, and one note on coverage.**
- **Settled:**
  - decision 4 follows D10 and the carried item for P07 (a photo's restriction is cleared only by the staff decision that closes the report);
  - decision 5 follows the brief's check list above;
  - decisions 7 to 9 and 11 to 16 are within the brief.
- **The coverage note:** two of the manager's offline reversals passed every offline test:
  - M2: the seam skipped for an upload with no variant;
  - M3: approval's hold check removed (only an allowlist test errors, because its anchor is gone).

  The profile suite's cases assert both behaviours, and the session's local database runs show each reversal caught there. This goes to the exact-head review as a coverage note.
- **Asked:** agree, or call any item up.

**7. DM-57's U1 to U11 as applied** (the review log, "Deferred conditions").
- **Where they are at `<RECORDS_COMMIT>`:**
  - U1 to U5 and U8 to U10 in the brief (`docs/planning/sv2-profiles-media.md`, revision 7);
  - U6 in `docs/testing/p11-deferred-acceptance.md`;
  - U7 in `docs/planning/carried-to-later-items.md`;
  - U11 in `docs/planning/manager-workflow.md`, step 7.
- **The manager's check:** each was applied by script from your report's quoted blocks, each old passage was found once, and each new text is present once.
- **U11 is governing text** that PR #<PR> carries.
- **Asked:**
  - confirm as applied;
  - say whether this read of step 7 at `<RECORDS_COMMIT>` serves as your pre-merge read of it, or whether it waits for the pre-merge read.

**8. What follows.**
- **Next:** the exact-head review of the final code head, with a written threat model. It takes the media items, D19, Stage B's changes to Stage A's code, the coverage note and your rulings here.
- **Then your pre-merge read,** which covers the texts the session rewrote:
  - the data model's `MediaAsset`, `MediaObject` and grant rows;
  - the contract document's F05 rows;
  - the media fixtures note's server section;
  - the P11 plan's Stage B entry;
  - step 7, if it is not covered here.
- **Asked:** is anything missing from the review's scope or the pre-merge read's list?

**Notion:** please check that the Implementation Control page, SV2's Work Register row and the Dev Manager page match `<RECORDS_COMMIT>`. The repository wins (OD-27).
