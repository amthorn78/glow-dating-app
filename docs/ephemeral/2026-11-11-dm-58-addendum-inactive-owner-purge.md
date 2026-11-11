# DM-58 addendum — Codex's finding on PR44: an inactive owner's purge

- **Owner:** App Manager 10. Nathan carries this message to Dev Manager 4's session, `session_01Q789u2u6fuC4fQPtHzP9gN` ("Glow Dev Manager 4"), with DM-58 or after it (OD-25). App Manager 10 receives the answer, in DM-58's report.
- **Revision 1, 11 November 2026.**
- **Why:** Codex's review of PR44's first head raised one finding, after DM-58 was written. The fix changes the account-state gate on F05's system steps, which is a design question (step 6, "Fix or carry, by rule").
- **Where the result goes:** DM-58's report and its disposition in the review log; any correction prompt it calls for.
- **Stream variables:** none are needed.
- **Deletion condition:** prune with DM-58's consultation.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-58 addendum — Codex's finding on PR44: an inactive owner's purge.** From App Manager 10, relayed by Nathan to Dev Manager 4. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`. Please answer it as DM-58's item 9, in the same report.

**9. Codex's P2 on `82d246b`:** "Allow media purge to finish for inactive accounts" ([thread](https://github.com/amthorn78/glow-dating-app/pull/44#discussion_r4533543239)).
- **The finding:**
  - `request_purge` and `acknowledge_deletion` lock the owner's account row with `lock_account` (`glow_profiles/tx.py`). That function refuses any account that is not `active` (`account_not_active`).
  - An owner may remove a photo and then be suspended or ask for deletion (`glow_chat`'s `contact.suspend()` or `delete()`). After that, the purge cannot be asked, and an acknowledgment for a purge already asked is refused.
  - The asset stays `removal_pending` and its objects stay in storage, at the point where an account's deletion most needs them gone.
- **The manager's check:**
  - Confirmed in the code at `d8f1bad` (`glow_profiles/media.py`, `acknowledge_deletion` and `request_purge`; `glow_profiles/tx.py`, `lock_account`).
  - No test or suite case covers an inactive owner's purge.
  - Delivery stays withheld throughout: the removal withholds it at once, and `delivery_reference` refuses an inactive owner. So nothing is exposed; the cost is objects kept and a purge stuck.
- **The same gate elsewhere:**
  - `record_upload`, `review` and `run_check` also refuse an inactive owner, so an inactive account's upload stops where it is.
  - The carried-items file already carries the same gate on staff's revocation and restriction to P07: "a staff revocation of an approval, or a restriction, is refused for an account that is not active (`glow_profiles/tx.py`), while D18 says staff revoke 'at any time'".
- **Options:**
  - **(a)** a correction in Stage B. The purge request and the deletion acknowledgment take the account row's lock without the active-state gate, so serialization is kept. It comes with an offline test, a suite case (an owner removes a photo, is suspended, and the purge completes) and a reversal. The other system steps keep the gate (recommended).
  - **(b)** the same correction, extended to every system step of F05.
  - **(c)** carry it to P07 and F18, with the staff item.
- **Asked:**
  - a verdict;
  - if (a) or (b), whether the correction takes a delta review (M05 S2: 60 or fewer non-test lines) before the full exact-head review, or whether the exact-head review of the corrected head covers it.
