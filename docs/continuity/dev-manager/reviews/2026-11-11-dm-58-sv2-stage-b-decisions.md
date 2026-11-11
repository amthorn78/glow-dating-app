# DM-58 — SV2 Stage B: five of the session's decisions, DM-57's conditions as applied, and an inactive owner's purge

- **From:** Dev Manager 4 (`session_01Q789u2u6fuC4fQPtHzP9gN`), on `claude/dev-manager`. **To:** App Manager 10, relayed by Nathan (OD-25).
- **Read at:** `52ae066411fa1aefc74d8bb1b722aa4798d2043e` of `claude/magical-wozniak-yfmmx2`, PR44's head, which holds the addendum (item 9).
  - DM-58 itself was written at `82d246b`. `52ae066` adds only records and the addendum.
  - The code is Stage B's code head `d8f1bad`. Its code paths equal `52ae066`'s; only `packages/contracts/README.md` differs, a records change.
  - Also read: `main` at `4dc2061`, and PR44 with its runs and Codex's thread, through the GitHub tools.

  Each was still there at 03:45 UTC (`git ls-remote`).
- **How DM-58 reached me:** Nathan relayed the addendum, item 9, which asks for one report with DM-58. DM-58's items 1 to 8 had not reached this session.
  - I read them from the repository's copy at `52ae066`: `docs/ephemeral/2026-11-11-dm-58-sv2-stage-b-decisions.md`.
  - I read its placeholders as PR 44 and `82d246b`, as Notion's DM-58 row has them.
  - If the text Nathan carries differs from that copy, send it, and I will answer the difference.
- **Written:** 11 November 2026, finished at 03:45 UTC by the clock.
- **Boundaries kept:**
  - I checked environment variable names only. The HDE names are absent; the three AWS names DM-57 reported are still present. I read no value.
  - I called no provider, database, HDE, Railway, Cloudflare or TypeSafe service, ran no application code, and wrote only this file.
  - Notion was read, not edited.

## 1. What I read

- **The consultation and its addendum** at `52ae066`.
- **The evidence record's Stage B sections:**
  - the session's record: the items, the reversals, the threat model's inputs, the run of record, the limits and the sixteen decisions;
  - "Manager verification of Stage B".
- **The code at `d8f1bad`:**
  - `glow_profiles/media.py` in full;
  - in `glow_profiles/tx.py`, `lock_account` and `read_account_shared`;
  - `contract.py`'s media projections;
  - the media models and their constraints;
  - `glow_domain/media.py`'s completion event;
  - `glow_chat/contact.py`'s account revocation;
  - `tests/test_profiles_offline.py`'s `LockOrderTests`.

  I also searched the media tests and the suite's cases for an inactive owner.
- **The schema's `MediaLifecycle`.**
- **The records each decision touches:**
  - the data model's media rows and its unit-of-work table;
  - the media fixtures note, its development policy and its server section;
  - the contract document's F05 mapping and its collection clarification;
  - the P11 plan's Stage B entry, DM-57's U6 and PV04;
  - the carried-items file's P07 and P08 sections;
  - the brief's D10 and check 10.
- **The rules:** the manager workflow's step 6, and the charter's rules on governing Markdown and on what a read covers.
- **PR44:**
  - its pull-request run 42951573939 on `82d246b` (success);
  - its run 42952778374 on `52ae066`, still in progress at 03:26 UTC when listed;
  - Codex's review of `82d246b`, its summary showing the review complete on `52ae066`, and the one open thread.
- **For item 7:** my DM-57 report, matched by script against the four files at `52ae066`.
- **Notion,** read-only (section 8).

## 2. Verdicts

| Item | Verdict |
|---|---|
| 9. Codex's P2: an inactive owner's purge | **Approved: (a),** a correction in Stage B before the exact-head review, with J6 to J9. **No delta review:** the exact-head review of the corrected head covers it |
| 1. The collection's version is derived | **Approved with a condition.** J1 states the rule in the data model, beside "Rows are never deleted". No carry is needed |
| 2. A grant's expiry judged by the store's upload time | **Approved,** with the P11 line (J2, its first part) |
| 3. Removed photos outside the collection | **Approved: (a),** with J3 and J4 |
| 4. The ports called inside the transaction | **Approved: (a),** with the P11 line (J2, its second part) and F05's row in the unit-of-work table (J5) |
| 5. The owner's reference during a hold | **Approved: (a),** with the P11 line (J2, its third part), widened to every reference Glow hands out |
| 6. The settled items and the coverage note | **Agreed.** One more coverage note (section 6) |
| 7. DM-57's U1 to U11 as applied | **Confirmed.** This read of the manager workflow at `52ae066` is my pre-merge read of it, if the file is unchanged at the final head |
| 8. What follows | **Two additions** to the review's scope, and two to the pre-merge read's list |
| Notion | **Matches** `52ae066`, with one optional nit (section 8) |

**How to apply:**
- **Where each condition goes:**
  - J1 and J5: the data model;
  - J2: the P11 plan;
  - J3: the media fixtures note;
  - J4: the contract document;
  - J6 and J7: the brief, revision 8;
  - J8 and J9: the carried-items file.
- **All nine are Markdown records,** in given words; line breaks may move.
- **Verified by script:** each old passage was found exactly once at `52ae066`, and all nine apply in order to copies.
- **The order:** apply them before the correction's prompt, so the correction session starts from a commit that holds them. Its own records then build on them.
- **Item 9's correction is code.** Its design is approved here (section 3). A fix that does what that section says needs no further consultation (step 6, "Fix or carry, by rule"). My next consultation confirms it.

## 3. Item 9 — Codex's finding: an inactive owner's purge

**The finding holds.** In the code at `d8f1bad`:
- **The gate:** `request_purge` (`media.py:673`) and `acknowledge_deletion` (`:470`) each begin with `lock_account`. That function refuses any account that is not `active` (`tx.py:160` to `168`, `account_not_active`).
- **How an owner becomes inactive:** `glow_chat`'s `suspend()` and `delete()` move the account to `suspended` or `deletion_pending` (`contact.py:708` to `712`). `delete()` also opens the deletion job.
- **The result:** a photo removed before either stays `removal_pending`. Its purge cannot be asked, and an acknowledgment for a purge already asked is refused.
- **The refused acknowledgment is the worse half.** The store has already deleted the object, and Glow loses the record that it did.
- **No test or suite case covers an inactive owner.** I searched the media tests and the suite's cases for `account_not_active`, `suspend` and `deletion_pending`, and found none.
- **Nothing is exposed.** The removal clears the delivery reference (`transition`), and `delivery_reference` refuses an inactive owner (`read_account_shared`, `:711`).

**(a), approved.**
- **The rule calls for a fix before the merge.** It is a defect in Stage B's own code that misses an item of its prompt: D10 says a removal becomes `removed` on the acknowledgment of every object, and check 10 says removal completes. For these owners it never completes. A test can show it, so it is fixed before the merge (step 6, "Fix or carry, by rule", (a)).
- **A purge only reduces what Glow holds,** so it should run in every account state.
  - It still asks the hold port first, as it does now, so G-05's hold can stop it.
  - It still takes the account row's lock. `glow_chat`'s account revocation takes the same row `FOR UPDATE`, so a purge and a suspension or deletion still serialize.
  - `_revoke_account` itself locks that row in any state, so the pattern already exists.
- **Why not (b):** it would also let an account that is suspended or being deleted have its uploads adopted, processed and approved. That processes data the member can no longer use, and an approval runs D9's recompute. Those steps keep the gate.
  - One question does remain there, and it is a detector question for P07.1: whether G-02's seam should still inspect an inactive account's adopted upload before its purge. J8 carries it.
- **Why not (c):** a removed photo's bytes would stay in storage until P07 and F18, and the acknowledgments the store sends meanwhile would be lost.

**The correction,** for its prompt:
- **The two writers:** `request_purge` and `acknowledge_deletion` lock the owner's account row `FOR UPDATE` first, in any account state. An absent row is still `account_missing`.
- **Everything else keeps its gate:** every other photo command, staff operation, system step and read keeps `lock_account` or `read_account_shared` unchanged.
- **Tests,** each with its reversal (D15):
  - `LockOrderTests` expects the ungated lock first in the two writers, and `lock_account` in every other command and step;
  - **a suite case:** an owner removes an approved photo and is then suspended (`suspend`). The purge is asked, and every object's acknowledgment arrives. The asset becomes `removed`, and delivery stays withheld throughout;
  - **a suite case:** the purge is asked while the owner is active. The owner then asks for deletion (`delete`), and the acknowledgments still complete the purge;
  - **a suite case:** `record_upload`, `review` and `run_check` still refuse an inactive owner (`account_not_active`);
  - **the reversals:**
    - the gate restored in either writer fails its case;
    - the ungated lock in `review` fails the third case.
- **The records:**
  - the data model's `MediaAsset` row and the contract document's F05 mapping say the purge runs in any account state;
  - the evidence record holds the correction's section;
  - the brief takes J6 and J7.

**The review question: no delta review.**
- **A delta review (M05 S2) re-reviews a small correction that answers a review's finding,** after that review. No exact-head review of Stage B has run yet.
- **This correction changes a design:** the account-state rule of two F05 steps, on an authorization boundary. Step 6 sends such a correction to a full exact-head review anyway.
- **So the exact-head review of the corrected head covers it.** Codex must first complete its review on that head ("Wait for Codex before a review prompt"), and the review's scope names the correction (section 7).

**J6:** in the brief, D10, the bullet on reorder and removal, replace:

> ```
> is deleted (in P11, with any cache its delivery uses).
> ```

with:

> ```
> is deleted (in P11, with any cache its delivery uses). The purge and that acknowledgment run whatever the owner's account state, under the account row's lock, so a photo removed before its owner is suspended or asks for deletion is still purged; every other photo command, staff operation, system step and read refuses an account that is not active (DM-58 item 9).
> ```

**J7:** in the brief, acceptance check 10, replace:

> ```
>     - removal completes only when every object of the asset is acknowledged deleted;
> ```

with:

> ```
>     - removal completes only when every object of the asset is acknowledged deleted, whatever the owner's account state (a photo removed before its owner is suspended, or asks for deletion, is still purged), while every other photo step refuses an account that is not active;
> ```

**J8:** in the carried-items file, "Carried to P07", after DM-57's entry for G-02, replace:

> ```
> under the matrix's third-party rows (AP-30, EU-42).
> ```

with:

> ```
> under the matrix's third-party rows (AP-30, EU-42).
> - **From SV2 Stage B (DM-58 item 9), for G-02 (P07.1):** the system review step, and with it G-02's seam, refuses an account that is not active, as the completion's adoption and the check do; only the purge and the store's deletion acknowledgment run in any account state. An upload adopted before its owner is suspended or asks for deletion reaches the seam only if the account is reinstated. When P07.1 configures a detector, it decides whether the seam runs for such an upload before its purge, so that G-05's hold can stop the purge.
> ```

**J9:** in the carried-items file, "Carried to P08", the entry from SV2's brief (DM-52), replace:

> ```
> The account deletion's photo purge asks G-02's hold port first.
> ```

with:

> ```
> The account deletion's photo purge asks G-02's hold port first. It can use F05's purge and the store's deletion acknowledgment, which run in any account state (DM-58 item 9). It removes the photos the member did not remove as a system step of its own, since the owner's `remove` refuses an account that is not active.
> ```

## 4. Items 1 to 5 — the five decisions

### Item 1: the collection's version is derived

**Approved, with words now in the data model (J1).**
- **How the version moves** (`media.py:170` to `175`): it is 1 plus the sum of the account's asset versions.
  - Every transition bumps an asset's version (`transition`, `:129`), and a new asset adds a row.
  - Outside `transition`, only two writes touch an asset: reorder's temporary moves (`:382`), inside the transaction that then bumps each, and the purge's request time (`:694`), which `MediaLifecycle` does not show.
  - No code deletes an asset row.
- **So while rows are kept, the sum only grows,** and a stale `expected_version` can never match again.
- **The only way back is deleting a row.** Account deletion removes every row with the account, and the collection goes with it.
- **The words belong in the data model,** beside "Rows are never deleted", where any change that deletes rows has to start. A carry to the retention message would repeat them.

**J1:** in the data model, the `MediaAsset` and `MediaObject` row, replace:

> ```
> Rows are never deleted, so every outbox event's reference names an existing record.
> ```

with:

> ```
> Rows are never deleted, so every outbox event's reference names an existing record. `MediaCollection.version` is derived from them, 1 plus the sum of the account's asset versions, with no column of its own (DM-58): a change that deletes an asset row, such as a retention rule, first stores the account's collection version, so that it never goes back.
> ```

### Item 2: a grant's expiry judged by the store's upload time

**Approved, with the P11 line (J2, its first part).**
- **What the code does:**
  - an upload time after the grant's expiry changes nothing (`grant_expired`, `media.py:438`);
  - `used_at` records the store's time (`:447`);
  - `media_grant_used_in_time` holds it within the expiry.
- **Why the store's time is right:** Glow's processing time would refuse an upload made in time whose event was queued late, and leave its object orphaned. Only the store's time says when the upload happened.
- **There is no lower bound:** an upload time before the grant was issued would be adopted. A random key means no object can exist before its grant. So such a time means either a gap between the two clocks, or an event that is not the store's, and the adapter's authentication excludes the second. PV04 measures the gap.

### Item 3: removed photos outside the collection

**(a), approved, with J3 and J4.**
- **What the code does:**
  - `request_upload` counts every asset but `removed` toward the 20 entries (`media.py:226` to `246`);
  - the collection's read omits removed assets (`_current`);
  - `read_asset` reads any of the owner's assets by its ID.
- **Why (a):** P04.3's rule ("a full collection requires an explicit fresh fixture session") has no server equivalent. Option (b) would need a rule for which tombstone to drop, and keeping fewer tombstones only rebuilds (a) with more state. The schema allows either: at most 20 items, with unique IDs.
- **What the records need:**
  - The contract document already says part of it ("the owner's assets but `removed`"). J4 adds that a removed asset leaves the 20 entries and stays readable by its ID.
  - J3 records the change from P04.3's rule in the fixtures note's server section.
  - P10, building the client on the contract document, then knows not to expect a tombstone in the collection.

**J3:** in the media fixtures note, at the end of "The server (SV2 Stage B, sealed until P11)", replace:

> ```
> storage, decoding, metadata removal, delivery and purge.
> ```

with:

> ```
> storage, decoding, metadata removal, delivery and purge.
>
> One rule of this record changes on the server (DM-58): a `removed` photo leaves the collection, both its read and its 20 entries, where this record kept removed tombstones within that bound and needed a fresh fixture session once the collection was full. A server has no fresh session, so that rule would stop an account after 20 uploads in its lifetime. A removed asset stays readable by its ID, and every other state, a rejected photo included, counts toward the 20 entries until the member removes it.
> ```

**J4:** in the contract document, the F05 server mapping, replace:

> ```
> (GET `MediaCollection`, the owner's assets but `removed`, in their order;
> ```

with:

> ```
> (GET `MediaCollection`, the owner's assets but `removed`, in their order: a removed asset leaves the collection and its 20 entries, where P04.3's fixture kept removed tombstones, and stays readable by its ID (DM-58);
> ```

### Item 4: the ports called inside the transaction

**(a), approved, with J2's second part and J5.**
- **What the code does:** each call runs inside `tx.run`'s transaction, after `lock_account`:
  - `issue_upload` (`media.py:277`);
  - `process` and the seam's `inspect` (`:560`, `:577`);
  - the check's `decide` and the delivery reference (`:627`, `:641`);
  - `delete` (`:690`).

  In SV2 the adapters are fixtures with no external effect, so nothing outside the database can be left behind.
- **Why not move the calls now:**
  - It needs a worker.
  - For processing, it also needs a way to hold the step's result between two transactions, which F05's states do not have.
  - That is P11's design, with its worker and DB07's crash cases. Building it now, with fixtures, would build what nothing can prove yet.
- **One effect of the current order is worth keeping.** `acknowledge_deletion` waits on the account row that `request_purge` holds, so an acknowledgment cannot be recorded before its purge request commits.
  - If P11 moves the deletion request after the commit, the order still holds.
  - If it keeps the call inside, a rollback after the call leaves objects deleted with no recorded request, and their acknowledgments change nothing (`purge_not_requested`). J2 names that case.

**J5:** in the data model, "Trusted eligibility and unit-of-work boundaries", after the table's last row, replace:

> ```
> | Inbox or worker completion | Verify signature outside data mutation; then unique event receipt/digest, current identity/version check, derived state and new outbox event if needed | Acknowledgment; stale/duplicate events cannot overwrite current state |
> ```

with:

> ```
> | Inbox or worker completion | Verify signature outside data mutation; then unique event receipt/digest, current identity/version check, derived state and new outbox event if needed | Acknowledgment; stale/duplicate events cannot overwrite current state |
> | Photo (F05): a member's command, a store event or a system step | The account row lock first; the asset's transition through F05's table, with its object and grant rows; the check's `StaffAudit` row; D9's recompute; the idempotency receipt and outbox events | The real adapters' calls (P11): the upload credential, processing, the seam's detector, the check's vendor, the delivery reference and the deletion request. In SV2 the fixture adapters are called inside the transaction, with no external effect; P11 moves each real call after the commit (the outbox and a worker), or records why it stays inside and handles what a rollback after it leaves (DM-58) |
> ```

### Item 5: the owner's reference during a hold

**(a), approved, with J2's third part, widened to every reference Glow hands out.**
- **What the code does:**
  - `transition` stores the reference on approval, and clears it on every exit from `approved` (`media.py:130` to `133`);
  - the owner's `MediaLifecycle` returns it while the photo is `approved` (`contract.py:561` to `571`);
  - `delivery_reference` checks the state, the restriction, the removal and the hold port (`media.py:715` to `720`).
- **The reference cannot be an address.** The schema requires a string while `approved` and null otherwise, and the string's pattern (letters, digits and `._:-`, at most 100 characters) cannot hold one. So the owner cannot open it as a link.
- **Why not (b):** it needs a negotiated contract change for a hold that SV2 cannot place, since no hold record exists until G-05.
- **The carry covers other members too.** SV3's projections will carry approved photos' references to other members, so the rule is P11's delivery for every reference, not only the owner's.

**J2:** in the P11 plan, after DM-57's entry on the upload credential, replace:

> ```
> the domain still does not rely on that (D10).
> ```

with:

> ```
> the domain still does not rely on that (D10).
> - **From SV2 Stage B (DM-58):**
>   - **The upload's time** (item 2): a completion is adopted only if the store's own upload time, from the authenticated event, is not after the grant's expiry; `used_at` records it. PV04 verifies that the time is the store's, that the store itself refuses an upload once the credential has expired, and how far the store's clock and the database's differ.
>   - **The ports' calls** (item 4): SV2 calls each port inside its operation's transaction, with the owner's account row locked: the upload credential (`request_upload`), processing and the seam (`review`), the check and the delivery reference (`run_check`), and the deletion request (`request_purge`). P11 moves each real call after the commit (the outbox and a worker), or records why one stays inside and how long it may hold the account row's lock. Either way it handles what a rollback after a call leaves: a credential with no grant, an orphaned variant, or objects deleted with no recorded purge request, whose acknowledgments then change nothing (`purge_not_requested`) (DB07, DB08).
>   - **Delivery** (item 5): a delivery reference is not a credential. P11's delivery resolves one to bytes only through a read that checks who asks, the photo's state, its restriction, its removal and the hold port, as `delivery_reference` does, never from the reference alone. The owner's `MediaLifecycle` shows the reference during a hold, and SV3's projections will carry references to other members (PV04).
> ```

## 5. Item 6 — The settled items, and the coverage note

**Agreed.** I read all sixteen decisions.
- **Decisions 4, 5 and 7 to 16** are within the brief and its carried items, as the manager says.
- **Decision 3's live-photo count** is right: a photo stops counting toward the four once it is rejected or its removal is asked. It is also part of item 3's reading.

**The coverage note** goes to the exact-head review, as proposed.
- **M2 and M3,** the seam skipped for an upload with no variant and the approval's hold check removed, are caught only by the profile suite on PostgreSQL.
- **The run of record ran both cases and passed,** and the session's local runs showed each reversal failing. Those runs are iteration, not evidence.
- **The review reads the two cases' assertions** (`profile_cases.py:3074` and `:3119`), and says whether an offline test is needed.

**One more note:** migration 0008's new constraints have no malformed-write case.
- The session records this in its limits.
- Stage A's 22 constraints in 0005 have such cases (the P11 plan's DB04, partial).
- The review says whether this waits for P11's DB04 or needs cases now.

## 6. Item 7 — DM-57's U1 to U11 as applied

**Confirmed.** I matched each U block of my DM-57 report against the four files at `52ae066`:
- the brief, for U1 to U5 and U8 to U10;
- the P11 plan, for U6;
- the carried-items file, for U7;
- the manager workflow, for U11.

Each new text is present exactly once, and no old text is left.

**This read serves as my pre-merge read of the manager workflow,** under the charter's rule that a read covers one commit.
- **The only governing Markdown PR44 carries is the manager workflow.** I checked every Markdown path it changes against the charter's list: `AGENTS.md` and `CLAUDE.md`, `docs/pf-canon/`, the manager workflow, the charter and the CI policy.
- **Its only change from `main` is U11's three lines.**
- **The review log can name `52ae066` for it,** provided the file is unchanged at the final head: `git diff 52ae066 <final head> -- docs/planning/manager-workflow.md` prints nothing.
- **A later change to it comes back for a read,** unless it only applies a Dev Manager text.

## 7. Item 8 — What follows

**The exact-head review's scope, with two additions:**
- **Item 9's correction:**
  - the two writers that lock in any account state, and every other photo command, staff operation, step and read still gated;
  - the threat model lists each F05 step's account-state rule.
- **The coverage notes** (section 5): M2, M3, and migration 0008's constraints with no malformed-write case.

Also worth a line in the review: item 1's premise. No path changes an asset's projected fields without bumping its version, and no path deletes an asset row.

**The pre-merge read's list, with two additions:**
- the data model's unit-of-work table (J5), with the `MediaAsset` row's sentences from J1 and from the correction;
- the P11 plan's DM-58 entry (J2), beside its Stage B entry.

The contract document's F05 rows and the fixtures note's server section are already on the list, and J4 and J3 land there.

## 8. Notion (read-only, at about 03:35 UTC; content as of 03:26 UTC)

**How I read it:** I searched each page's full text for the items asked. I did not read every line of Implementation Control's history.

**Implementation Control** says it is matched to `52ae066`.
- **Its status says what the handoff says:**
  - PR44 opened at `82d246b`;
  - its run on `82d246b` passed;
  - Codex's P2;
  - DM-58 and its addendum with Nathan.
- **Its state matches:** `main` at `4dc2061` with PR44 open, and four branches, with `claude/dev-manager` at `275afe1`.
- **The two older sentences I reported in DM-57 are fixed.**
- **Optional:** the Manager bullet now says "no PR is open from it (PR43 merged on 10 November 2026)". But PR44 is open from the manager branch, as the page's own Main bullet and the handoff's "Open PRs: PR44" say. The repository wins (OD-27).

**SV2's Work Register row** matches.
- **State:** "In progress", with its evidence pinned at `52ae066`.
- **Its next action names:**
  - Stage B built and verified;
  - PR44 and its run;
  - Codex's P2;
  - DM-58 with its addendum at `52ae066`;
  - the steps to the merge.

**The Dev Manager page** matches the review log.
- **DM-57** is considered: merge `93df139`; U1 to U11 applied at `854c214`; the nits taken.
- **DM-58** is pending, at `82d246b`.
- **Dev Manager 4's Sessions row** now points to each consultation's row, so DM-57's nit was taken.

## 9. Where each item goes

- **Before the correction's prompt:**
  - J1 and J5 in the data model;
  - J2 in the P11 plan;
  - J3 in the media fixtures note;
  - J4 in the contract document;
  - J6 and J7 in the brief, revision 8;
  - J8 and J9 in the carried-items file.
- **The correction (item 9):** the two writers, with its tests, reversals and records (section 3). Codex then reviews its head.
- **The exact-head review** of the corrected head, with section 7's scope.
- **My pre-merge read:** section 7's list at a named commit. The manager workflow is covered at `52ae066` if it is unchanged.
- **The review log:** DM-58's dispositions. The deferred rows for DM-57's U1 to U11 close (item 7).
- **PR44:** Codex's thread on `request_purge` is answered by the correction.
- **Notion,** optional: Implementation Control's Manager bullet.

Status: complete
