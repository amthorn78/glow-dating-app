# DM-103 — SV4 B1's pre-merge read (PR60), with B1-C1 and its exact-head review

- **From:** Dev Manager 7, `session_01Q789u3mBCcA1Fu21CMJKbS` ("Glow Dev Manager 7"), on `claude/dev-manager`, 27 November 2026.
- **To:** App Manager 13, through Nathan (OD-25, OD-84).
- **Consultation:** `docs/ephemeral/2026-11-27-dm-103-sv4-b1-pre-merge-read.md`, revision 1, read whole at `90e386d7ce497667f819f82c9ab1538caeecf3a8` of `claude/magical-wozniak-yfmmx2`, PR60's head. `main` is at `988a36a1fe4bc7b654a07e565e15fe721dcf3520`. The message Nathan relayed matches the file, with `<RECORDS_COMMIT>` filled in.
- **Labels:** AO1 to AO5 are conditions, each with its words in section 12. All five go into the one Markdown commit that the merge plan's step 1 already provides.
- **Environment** (names only): none of the forbidden names (`DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, `STREAM_*`, `RAILWAY_*`, `PG*`, `CLOUDFLARE_*`). I called no provider, database, HDE, Railway, Cloudflare or TypeSafe, and wrote nothing to GitHub or Notion.

## 1. Answers

| Item | Verdict | In short |
|---|---|---|
| 1 B1 and B1-C1 as settled | **Approved** | The code at `48f0801` does what AN1 says. The routes, the transfer, the bound, the locks, the seal and HDE's boundary are as B1's review found them. Nothing I would hold. |
| 2 D24's rules (B1C1R-1, B1C1R-4) | **Approved with conditions (AO1), before the merge** | D24 gets the four rules and the end of a failed re-read's row, as three steps. Apply AO1 with AO2 to AO5: the brief changes before the merge anyway (AO2), and the two describe the same row. |
| 3 AN3's and AN7's words (B1C1R-2, B1C1R-6) | **Approved with conditions (AO2 to AO4), before the merge** | My AN3 and AN7 say a refusal discards the reference at once. Two refusals never discard (a reference already held, and one the re-read finds held), and a failed re-read leaves its handle. D18 in the brief says the same, which the review did not name (AO2). The code is right; the sentences are wrong, on the unsafe side. The docstrings stay with B2. |
| 4 The manager's D-07 calls | **Agreed** | Both judgments and every disposition stand. Two notes: the lookup change is no precedent for passing a stop rule; B2's prompt adds an offline check for the review's reversal v8. |
| 5 Codex's two threads | **Agreed** | Resolve both before the merge. Each is answered by the code at `48f0801`, and Codex found nothing on `47ecc48` or `90e386d`. |
| 6 Carried and recorded | **Confirmed, with AO5** | Every entry is in the right place. My AN9 says only an unknown commit outcome leaves a token for the sweep; a failed re-read does too (AO5). |
| 7 Records since DM-102 | **Confirmed** | Each commit matches its description, and DM-102's words are applied as given. The review log's DM-103 row lists one ask the consultation does not make; section 9 answers it. |
| 8 Notion | **No mismatch** | All four pages match `90e386d`. The Dev Manager page has DM-102's row, answered, and DM-103's, "Awaited". |

**Nothing needs Nathan.**

**The merge, as proposed:** step 1 applies AO1 to AO5 as given. They are Markdown only, and the non-Markdown paths stay at `48f0801`, so no code review is needed for them. Steps 2 to 6 stand as written.

## 2. What I read and ran

- **The record** (2,815 lines at `90e386d`), whole: "Dev Manager 7's DM-102", "B1-C1" (with "What B1-C1 changes in section B1" and "Limits and deviations"), "Manager verification of B1-C1" and "Exact-head review of B1-C1".
  - "B1", "Manager verification of B1" and "Exact-head review of B1" I read whole for DM-102 at `c331899`. Since then, the only change to them is AN8's mark (line 2393), checked with `git diff`.
- **The code:**
  - `git diff e7e7e84 48f0801`, whole, for `glow_notifications/persistence.py`, `glow_domain/notifications.py`, `glow_notifications/contract.py` and `notification_fixtures.py`;
  - at `48f0801`: `_hold_for_discard`, `_write_handle`, `_held_since`, `_consume_handle`, `_discard_unwritten`, `_discard`, `device()`, `_register`'s save, and `PendingTokenDiscard`'s docstring;
  - every use of `token_secret_ref` outside the tests and migrations (`git grep`);
  - `models.py`'s diff (docstring only) and the migrations (no diff).
- **The brief** at `90e386d`: D18's custody bullet and D24.
- **The docs:** `production-contracts.md`'s F12 bullets (the codes and the custody); `data-model.md`'s `PendingTokenDiscard` row.
- **The carried entries:** the carried-items file's entries from B1's record, B1's review, B1-C1's record and B1-C1's review, and B1R-5's; the P11 plan's B1R-4 line.
- **GitHub** (REST `GET` only):
  - PR60 and its two review threads, with both comments;
  - the branch's run list;
  - run 45950434334's jobs and its gate, chat and scope logs;
  - Codex's reviews and its summary comment.
- **The records since DM-102** (section 9), and **Notion** (section 10).
- **Not read or run:** the 37 chat cases, the structure tests and the offline tests (the session ran 14 reversals, the review 10, and both runs ran the suites); the changed modules whole beyond the custody paths; no test, suite or reversal of my own.

## 3. Item 1: B1 and B1-C1 as settled

**Verdict: approved.**

- **The custody paths, checked against the code at `48f0801`.** For a register, after the store's `put`:
  1. **the handle's write returns no row** (a registration or a pending discard holds the reference): `token_store_refused`, nothing discarded;
  2. **the write raises:** `_discard_unwritten` discards the reference at once, then the command answers its error;
  3. **the re-read finds a holder:** the handle is removed by its key, `token_store_refused`, nothing discarded;
  4. **the re-read raises:** the command answers its error and discards nothing, and the handle stays (B1C1R-2);
  5. **a known outcome that did not save** (a refusal, a deadlock, a replay, or a failure before the body returned, including one at the transaction's start): `_discard` discards the reference and removes its row; a failed discard leaves the row;
  6. **an unknown outcome** (the `before_commit` point or the commit): the handle stays;
  7. **a save:** `_consume_handle` deletes the handle by its key and reference, and refuses `token_handle_missing` unless exactly one row went.

  Every path leaves the token held by a row or discarded, except a process stop or a double failure in path 2, which is AN1's stated limit.
- **Every save goes through D18's check.** The only writes of a non-null `token_secret_ref` are `_register`'s create and update (lines 692 and 704), after `_consume_handle` (line 684). D24's sweep relies on this (section 4).
- **The port** (AN11): `put` returns a new reference each time, and `discard` changes nothing for a reference already discarded. So a command and the sweep can both discard one reference without harm.
- **The rest of B1 is unchanged.** From `e7e7e84` to `48f0801`, ten non-Markdown paths changed, all custody paths. `views.py`, `providers.py`, the models' fields and constraints, the migration, `chat_suite.py`, `glow_chat/`, `glow_api/` and the workflow did not change.
- **Every commit after `48f0801` is Markdown:** `git diff --name-only 48f0801 90e386d` lists no other file.
- **The runs.**
  - The run of record is 45941121120 (`push`, `48f0801`).
  - PR60's run on its head is 45950434334 (`pull_request`, `90e386d`):
    - all twelve jobs succeeded, and the gate printed "Application checks passed";
    - the chat suite passed 37/37 in 159.0 s, with both scans clean (2003 secrets and 1335 member values held, 0 found);
    - `ROW LOCKS (D14): PASS` and `CHAT VERDICT: PASS`;
    - `dbshell` exited with status 1.
  - The push run 45950428773 on the same commit succeeded.
- **The classification:** `main`'s classifier (SHA-256 `b564c62f4a076f51…`), outside the checkout, with `python3 -I` and full SHAs:
  - one merge base, `988a36a`;
  - `"full": true`, reason `behavior-or-empty`, 51 paths;
  - no governing path changed;
  - no new symlink, executable file or mode change.

## 4. Item 2: D24's rules (B1C1R-1, B1C1R-4)

**Verdict: approved with conditions. AO1 replaces D24's bullet, before the merge.**

**The four rules are right.** I checked each against the merged code:
- **(a) Call the store only after a delete that removed the row.** In probe P3, the save deleted the handle first, so the sweep's delete removed nothing; a sweep that called the store anyway would destroy a live token. A row can also be gone because a discard took it: a command's own (a known outcome removes its row after the store's discard), or a retired reference's after its commit. Either way, the sweep stops.
- **(b) The delete's transaction takes no other lock.** The commands lock in this order: the account, the session, the registrations, then the pending discards (the save's delete and the retire's insert). A sweep that held a pending row and then took a registration lock would reverse that order.
- **(c) Every save goes through D18's check.** The sweep is safe only because a save must delete the handle the sweep deletes. That holds today (section 3). AO1 makes it a rule for B2 and for later work.
- **(d) Rewrite under a new key.** A command that wrote its handle long ago, past the bound, still holds the handle's key. If the sweep's failed discard rewrote the row under the same key, that command's save would succeed with a reference the store may already have discarded. With a new key, that save is refused.

**B1C1R-4: a row whose reference a registration holds.**
- Only a failed re-read, in a race with a store that broke its port, leaves one.
- While the row exists, no retire of that reference can succeed (the pending discards' uniqueness), so the holder's revoke is refused until the row goes.
- Deleting the row and discarding nothing is safe, because the token is the holder's. Probe P1 showed the same.

**Why the delete comes first.** One step then settles (a): if the delete removed no row, the sweep stops. It also clears B1C1R-4's row. The read after it only decides whether to call the store.

**The custody exception grows with B2.** A process stop between the sweep's delete and the store's answer, or a failed discard and a failed rewrite, can leave a token in no row. AO1 asks B2's custody sentences to state it, as D18 states its own.

**Timing: before the merge**, not in the next revision as proposed. Three reasons:
1. The brief changes before the merge anyway, for D18 (AO2). One revision is simpler than two.
2. AO1 and AO2 describe the same row from its two ends. AO2 says a failed re-read leaves its handle; AO1 says how the sweep ends it. Applying one without the other leaves the brief with a row that nothing ends.
3. The consultation's own routing rule puts words that change a sentence PR60 carries before the merge, and PR60 carries D24's.

It does not hold the merge: the words are given here, step 1 already applies Markdown words, and steps 2 and 3 run the PR's checks and Codex on the final head anyway.

**After AO1 lands,** D24 answers two carried entries: the carried-items file's B1C1R-1 entry, and the failed re-read entry's "B2 says which path removes it". The manager notes that in its own words.

## 5. Item 3: AN3's and AN7's words (B1C1R-2, B1C1R-6)

**Verdict: approved with conditions. AO2 to AO4 apply before the merge; the code's docstrings stay with B2.**

**What is wrong.** AN3 and AN7 (my words, DM-102) say a command that did not save its reference discards it at once when its outcome is known, and they list "a refusal" first. The code at `48f0801` has three paths where that is not so:
1. **A reference already held** (the handle's write returns no row) is refused and never discarded: the token is another holder's.
2. **A holder found by the re-read:** the handle is removed, and the reference is refused and never discarded.
3. **A failed re-read** (B1C1R-2): the command answers its error, discards nothing and leaves the handle for the sweep.

There is also one nit: a failed write may leave its row (B1C1R-6), though the code still discards the reference at once.

Paths 1 and 2 are refusals, so AN3's list puts them on the wrong side, the unsafe one: read as a rule, it would discard another holder's live token. The review named only path 3.

**D18 says the same.** AN1's sentence in the brief reads "A command whose outcome is known and did not save the reference (a refusal, …) discards it at once". The sentence before it excepts a reference already held ("is not discarded"), but nothing excepts the re-read's two paths. The review's B1C1R-2 and the consultation name only AN3 and AN7. AO2 fixes D18.

**Why before the merge.**
- These sentences describe the merged code.
- They are the contract that B2's sweep and P11B's store are built from.
- The code is right and the sentences are wrong, on the dangerous side.
- A Markdown edit at step 1 fixes them for nothing.

Under D-07 this needs no correction pass: no code changes, and the manager applies the words as given, as it applied DM-100's AL1 to AL8 before PR59.

**What stays with B2: the docstrings.** These are:
- the adapter's "Custody" paragraph;
- `PendingTokenDiscard`'s docstring;
- `_write_handle`'s "nothing written";
- `_held_since`'s last sentence: under AO1, the sweep removes such a row and discards nothing.

B2 edits `persistence.py`, so its prompt brings them into line with AO2 and AO1. They need a code change, so they wait; nothing at the merge rests on a docstring.

**One carried stale line is half answered.** With AO3, the custody bullet names a reference already held as the store's refusal. The codes bullet's missing `token_handle_missing` stays carried to B2.

## 6. Item 4: the manager's D-07 calls since DM-102

**Verdict: agreed.**

- **The handle in two statements: right.**
  - AN1 asks for a write "only if" nothing holds the reference. At READ COMMITTED, one statement cannot ensure that against a concurrent save of the same reference.
  - The review showed the race is real: with reversal v1, case B1-C1-6 discards a live token.
  - The re-read changes no design, model or lock order.
  - It added a failure path that my words did not cover; AO2 to AO4 add it.
- **The four earlier cases' lookup: the acceptance stands.**
  - The change is mechanical, and it finds the same reference: the review checked all nine calls.
  - It changes no expectation beyond the prompt's item 8.
  - It is not a precedent. A session that meets its stop rule should stop; here the prompt was the cause (AM13-18).
- **The dispositions:**
  - no correction pass: agreed, since the code is right;
  - B1C1R-1 carried: answered by AO1;
  - B1C1R-2 to this read: answered by AO2 to AO4;
  - B1C1R-3 carried: agreed, with one addition. Today nothing catches reversal v8 (a failed re-read made to discard). B2 edits `persistence.py` anyway, so its prompt adds an offline check that fails under v8;
  - B1C1R-4 carried: answered by AO1;
  - B1C1R-5 fixed: confirmed (section 8);
  - B1C1R-6 carried (the docstring): agreed; AO2 to AO4 cover the row.

## 7. Item 5: Codex's two threads

**Verdict: agreed. Resolve both before the merge.**

- **4713760650** (on `cd920fd`: a reference lost when parking fails). `_park` is gone, and the handle is written first. A failed write discards the reference at once. Only a double failure is left: it is logged with one fixed line and stated as the custody limit.
- **4715163584** (on `c331899`: an unknown commit outcome). This is form (b) exactly: the handle written before the command and removed by the save, in the save's own transaction. An unknown outcome leaves the handle and discards nothing (case B1-C1-4).
- **Their state:** both threads are outdated and unresolved (`ccr/review_threads`).
- **Codex:** its summary comment shows its review of `90e386d` completed at 06:15:12 UTC with no findings. For `47ecc48`, my source is the review's record (completed at 05:14:29 UTC, no findings); PR60's review list has no Codex review on that commit, as with every pass that found nothing.
- **DM-102's condition is met:** it said to resolve them once B1-C1's fix, and Codex's review of its head, confirmed them.
- **When:** at step 4, after Codex has passed the head that carries AO1 to AO5, as the plan says.

## 8. Item 6: carried and recorded

**Verdict: confirmed, with AO5.**

- **From B1's record (for SV4 B2):** right. B1C1R-5's fix is in: the custody limits are now told as B1-C1 leaves them, with no `_park`.
- **From B1's review (B1R-8, r19's case, the seal test's reach):** right. One sentence needs AO5. AN9, my words, says only a register whose commit outcome is unknown leaves a token and a pending row for the sweep. A failed re-read does too, and a refused reference that another holder holds is never discarded.
- **From B1-C1's record** (the stale lines, `_references_of`, the sweep's race, a failed re-read, the handle's clock): right. AO1 answers "B2 says which path removes it", and AO3 half of the codes bullet's stale line.
- **From B1-C1's review** (B1C1R-1, B1C1R-3, B1C1R-2 with B1C1R-6): right. AO1 answers B1C1R-1, and AO2 to AO4 answer B1C1R-2's AN3 and AN7.
- **AN10's entry** (B1R-5, for P09.2 and P11B): right, as applied.
- **The P11 plan's B1R-4 entry:** right, with no change needed. B1-C1's new statements (the handle's insert, the re-read and the save's delete) bind the same reference, and the entry's proof covers any failing statement.

## 9. Item 7: records since DM-102

**Verdict: confirmed.**

- **The five commits,** each as described:
  - `d0838ad` merges my report only;
  - `f7a21b9` is revision 13, B1-C1's prompt, AM13-16 and AM13-17;
  - `4185119` merges B1-C1: the code head `48f0801` and the records `1502359`, 14 paths;
  - `47ecc48` is the verification, AN9 and AN10, B1-C1's limits carried, the review prompt and AM13-18;
  - `90e386d` is the review's record and disposition, the carries, AM13-19, AM13-20 and DM-103.
- **DM-102's words, by script** on its section 9:
  - at `f7a21b9`: AN1 and AN2 applied as given; AN3 to AN11 not yet, as expected;
  - at `47ecc48` and at `90e386d`: AN1 to AN11 each found once, their old passages gone. AN8's new passage holds its old one, as designed.
- **DM-101's words at `90e386d`, by script:** AM1 to AM16 each found once, except AM4's passage, part of which AN1 replaced, as designed.
- **The other records:**
  - the mistakes log's AM13-16 to AM13-20 are each as the consultation describes;
  - the review log's DM-102 disposition matches my report;
  - the handoff is right;
  - `git ls-remote` lists the five branches it names: `main` `988a36a`, the manager branch `90e386d`, `claude/dev-manager` `f86ccaf`, `claude/lucid-fermi-droq7u` `f106105` and `claude/funny-hypatia-lpzbn0` `1502359`.
- **One small point.** The review log's DM-103 row lists "the brief's revisions 12 and 13 as applied", which the consultation does not ask (and Notion's row does not list). The answer: revision 13's AN1 and AN2 are applied as given, and revision 12's AM1 to AM16 stand, with AM4's passage partly replaced by AN1. Nothing rests on it.

## 10. Item 8: Notion

**Verdict: no mismatch.** What I read:

- **Implementation Control** (last edited 06:13:36 UTC). I read its status paragraph, SV4's bullet, and the lines for the branches, the mistakes log and the procedure summary, not the whole 536,000-character page.
  - The status is matched at `90e386d`.
  - SV4's bullet says B1-C1's review approved with nits and DM-103 is next.
  - It lists five branches at 06:12 UTC.
  - The mistakes log runs through AM13-20.
  - The procedure summary is at `988a36a`. PR60 changes no governing file, so it stays there.
- **The Dev Manager page** (last edited 06:13:25 UTC): its DM-100 to DM-103 rows.
  - DM-102's row is answered: AM13-17's fix.
  - DM-103's row reads "Awaited", with its asks as in the consultation.
- **The register copy** (last edited 22 November), whole, compared by script.
  - It has 84 rows, OD-01 to OD-84, in the repository's order.
  - The repository's register is unchanged since `c331899`.
  - Eight rows differ only in how links are shown, as in DM-102.
- **SV4's Work Register row**, whole: "In progress", and its latest entry matches `90e386d`.

## 11. My own error

DM-102's AN3 and AN7, and AN1's general sentence, listed "a refusal" among the known outcomes that discard at once. They did not except the refusal of a reference already held, which never discards. AN1 had that exception in the sentence before; AN3 and AN7 had none.

I missed this in DM-102, and again when I checked the applied words. I found it while checking B1C1R-2. Nothing has rested on it, since the code was right. AO2 to AO5 correct it.

## 12. The words

Each old passage occurs exactly once in its file at `90e386d`, checked by script. The script applied the five pairs to copies, and found each new passage once and each old passage gone. In the brief's status line, the manager records the revision (14) in its own words.

**AO1** — `docs/planning/sv4-chat-notifications.md` (D24: the pending discards' retry, the sweep's rules):

> ```
>   - **the ledger's retention** (D25), and **the pending discards' retry** (B1-C1; DM-102): the sweep takes a pending discard only once it is older than a bound longer than any command's run, which B2's prompt names, and only if no registration holds its reference. It removes the row in its own committed transaction before it calls the store, so a command can no longer save that reference (D18), and writes the row again if the discard fails. The bound only spares a running command a needless refusal; D18's check keeps the command safe whatever the timing.
> ```
> ```
>   - **the ledger's retention** (D25), and **the pending discards' retry** (B1-C1; DM-102; DM-103): the sweep takes a pending discard only once it is older than a bound longer than any command's run, which B2's prompt names, in three steps. **First,** it deletes the row by its key in its own committed transaction, which takes no account, session or registration lock, so the commands' lock order is never reversed. If that delete removed no row, a save consumed it first (the reference is now a registration's) or another discard took it, and the sweep stops. Once the row is gone, no command can save that reference (D18's check). **Next,** it reads the registrations, taking no lock. If one holds the reference (a failed re-read's handle in a race with a store that broke its port, D18), the sweep stops there and discards nothing, so the holder keeps its token and its later retire succeeds. **Last,** it calls the store. If the discard fails, it writes the row again under a new key, so no command still holding the old key can save that reference. A process stop between the delete and the store's answer, or a failed discard and a failed write, can leave a token in no row; B2's custody sentences state that exception, as D18 states its own. This all rests on one rule, which B2 and every later change keep: every transaction that writes a non-null `token_secret_ref` deletes that reference's pending discard by its key, or refuses (D18). The bound only spares a running command a needless refusal; D18's check keeps the command safe whatever the timing.
> ```

**AO2** — `docs/planning/sv4-chat-notifications.md` (D18's custody bullet: the handle, its re-read and their failures):

> ```
> **Its handle comes first** (B1-C1; DM-102): before the transaction, the new reference's pending discard is written in its own statement, and only if no registration and no pending discard already holds that reference; a reference already held is the store's refusal (`token_store_refused`) and is not discarded, and if the write fails the store discards the reference at once and the command answers its error. The transaction that saves the reference on a registration deletes its pending discard, and refuses (`state_conflict`) unless it deletes exactly that one row. A command whose outcome is known and did not save the reference (a refusal, a deadlock, a replay, or a failure raised before the transaction's body returned) discards it at once, as a retired one is; one whose outcome is unknown (a failure after the body returned, at the commit) leaves the handle to D24's sweep. So every reference the store holds has a registration or a pending discard, except after a process stop, or a failed write and a failed discard, between the `put` and the handle.
> ```
> ```
> **Its handle comes first** (B1-C1; DM-102; DM-103): before the transaction, the new reference's pending discard is written in its own statement, and only if no registration and no pending discard already holds that reference. With a store that breaks its port, that statement can miss a save of the same reference that commits while it waits, so the registrations are then read again, and if one holds the reference the handle is removed by its key. A reference held, by either check, is the store's refusal (`token_store_refused`) and is never discarded. If the write fails, the store discards the reference at once and the command answers its error (a row the write left anyway waits for D24's sweep). If the re-read fails, the command answers its error and discards nothing, leaving the handle to D24's sweep, since a registration may hold the reference. The transaction that saves the reference on a registration deletes its pending discard, and refuses (`state_conflict`) unless it deletes exactly that one row. Past those checks, a command that does not save the reference discards it at once when its transaction's outcome is known (a refusal, a deadlock, a replay, or a failure raised before the transaction's body returned), as a retired one is; when that outcome is unknown (a failure after the body returned, at the commit), it leaves the handle to D24's sweep. So every reference the store holds has a registration or a pending discard, except after a process stop, or a failed write and a failed discard, between the `put` and the handle.
> ```

**AO3** — `docs/architecture/production-contracts.md` (the custody bullet, AN3's second sentence):

> ```
> A command that does not save the reference discards it at once when its outcome is known (a refusal, a deadlock, a replay, or a failure before its transaction's body returned), and leaves it to SV4 B2's sweep when the outcome is unknown (a failure at the commit); an old one is discarded after the commit, and a failed discard waits for the sweep.
> ```
> ```
> A reference a registration or a pending discard already holds is the store's refusal and is never discarded: no handle is written for it, or the handle is removed when the registrations, read again once it is written, show a holder (DM-103). If the handle's write fails, the store discards the reference at once (a row the write left anyway waits for SV4 B2's sweep); if the re-read fails, nothing is discarded and the handle waits for the sweep, since a registration may hold the reference. Past those checks, a command that does not save the reference discards it at once when its transaction's outcome is known (a refusal, a deadlock, a replay, or a failure before the transaction's body returned), and leaves the handle to the sweep when that outcome is unknown (a failure at the commit); an old one is discarded after the commit, and any failed discard waits for the sweep.
> ```

**AO4** — `docs/architecture/data-model.md` (the `PendingTokenDiscard` row, AN7's passage):

> ```
> the handle a command writes for its new reference before its transaction, which the transaction that saves the reference deletes, and which a known refusal, deadlock, replay or earlier failure discards at once, an unknown outcome leaving it for SV4 B2's sweep; or one a command retired, until the store discards it after the commit, a failed discard staying for the sweep (DM-102).
> ```
> ```
> either the handle a command writes for its new reference before its transaction, or one a command retired. A handle is written only if no registration or pending discard holds the reference; the transaction that saves the reference deletes it; the command removes it with no discard if the registrations, read again, show a holder; its transaction's known refusal, deadlock, replay or earlier failure discards the reference at once and removes the row; and a failed re-read or an unknown outcome leaves it for SV4 B2's sweep, as a failed write may leave its row too. A retired reference stays until the store discards it after the commit, and any failed discard stays for the sweep (DM-102; DM-103).
> ```

**AO5** — `docs/planning/carried-to-later-items.md` (B1R-8's entry, AN9's clause):

> ```
> a refused, replayed or conflicting one discards its reference at once, so only one whose commit outcome is unknown leaves a token and a pending row for B2's sweep, within its bound
> ```
> ```
> a refused, replayed or conflicting one discards the reference the store gave it at once, never one another holder holds, so only one whose commit outcome is unknown, or whose handle's re-read failed (DM-103), leaves a token and a pending row for B2's sweep, within its bound
> ```

## 13. Checks

- **Git:**
  - `git fetch`, then `git rev-parse`: the manager branch at `90e386d`, `main` at `988a36a`, `claude/dev-manager` at `f86ccaf`;
  - `git ls-remote origin` lists five branches;
  - `git diff --name-only 48f0801 90e386d` lists only Markdown;
  - `git diff --name-only 988a36a 90e386d` over the consultation's governing paths prints nothing;
  - `git diff --summary 988a36a 90e386d` shows no mode other than `100644`.
- **The classifier:** `main`'s `scripts/change_scope.py`, extracted outside the checkout (SHA-256 `b564c62f4a076f51…`). Run with `python3 -I`, full SHAs and `--merge-base` (one merge base), it gave `"full": true`, `behavior-or-empty`, 51 paths.
- **Scripts on the words:**
  - DM-102's AN1 to AN11 at `f7a21b9`, `47ecc48` and `90e386d`;
  - DM-101's AM1 to AM16 at `90e386d`;
  - AO1 to AO5: each old passage found once at `90e386d`, applied to copies, each new passage then found once: ALL OK.
- **GitHub** (REST `GET` only):
  - PR60: open, head `90e386d`, base `988a36a`, mergeable;
  - `pulls/60/ccr/review_threads` and comments 4713760650 and 4715163584;
  - the branch's runs;
  - run 45950434334's twelve jobs and its gate, chat and scope logs;
  - Codex's reviews and summary comment.
- **Notion,** read only: as in section 10.
- **Environment:** variable names only.
- **Not run:** any test, suite or reversal.

Status: complete
