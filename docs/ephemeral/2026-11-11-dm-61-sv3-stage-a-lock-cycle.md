# DM-61 consultation — SV3 Stage A: Codex's lock cycle (CX1) and the tie-break key in SQL (V1)

- **Owner:** App Manager 11. Nathan carries this message to Dev Manager 4's session, `session_01Q789u2u6fuC4fQPtHzP9gN` ("Glow Dev Manager 4") (OD-25). App Manager 11 receives the answer.
- **Revision 1, 11 November 2026.**
- **Why:**
  - Codex's review of PR45's head found a deadlock in page creation (CX1). Its fix changes the lock design. The cleanest fix reaches outside Stage A's owned paths, into `glow_chat` and `glow_profiles`. Step 6 of the manager workflow sends that to the Dev Manager.
  - The manager's verification raised V1: the tie-break key's pads travel as SQL parameters. It may change the same code, so one correction can carry both.
  - The exact-head review's prompt (`docs/ephemeral/2026-11-11-sv3-stage-a-review-prompt.md`, revision 1) is held, not given. It is revised for the corrected head, and the review then reads Stage A once (AM7-13).
- **Where the result goes:**
  - your report in `docs/continuity/dev-manager/reviews/`;
  - App Manager 11's disposition in the review log, "DM-60" and "DM-61";
  - the brief's correction section and the correction's prompt;
  - the review prompt's revision 2.
- **Stream variables:** none are needed.
- **If no report arrives:** no correction or review prompt goes to Nathan; App Manager 11 asks Nathan whether Dev Manager 4's session is still available.
- **Deletion condition:** prune after the review log holds DM-61's disposition and SV3 Stage A's PR has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-61 — SV3 Stage A: Codex's lock cycle (CX1) and the tie-break key in SQL (V1).** From App Manager 11, relayed by Nathan to Dev Manager 4. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway or Cloudflare;
- check environment variable names only.

**Where it stands.**
- **SV3 Stage A is built and in [PR45](https://github.com/amthorn78/glow-dating-app/pull/45).** The code head is `ad9ff08`. The session's branch is `claude/loving-maxwell-cqu7eq`, integrated by fast-forward. Read:
  - the evidence record, `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md`: "Stage A", "Manager verification of Stage A" and "The run of record for Stage A (PR45)";
  - the brief, revision 2.
- **The run of record** is PR45's run 43113579295 on `88f9299`: all eight jobs passed, `Application checks passed`, and the discovery suite passed 32 of 32. Its proof has no concurrent page-creation case.
- **Codex on `88f9299`:** no findings. **Codex on `7e4d826`** (the commit that holds the review prompt; its code is identical): one P2, CX1, below. Its thread on PR45 (`services/api/glow_discovery/pages.py:207`) is open.
- **The exact-head review has not started.** Its prompt is held until this is settled.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. CX1, the lock cycle in page creation.** Codex's words: *"When two mutually eligible members create discovery batches concurrently, each transaction takes `FOR UPDATE` on its own account here and then inserts a `RecommendationEntry` referencing the other account. PostgreSQL's foreign-key checks require `FOR KEY SHARE` on those referenced accounts, which conflicts with the other transaction's `FOR UPDATE`, creating a deadlock. `glow_profiles.tx.run` converts the aborted transaction into `provider_unavailable` without retrying, so otherwise valid page requests intermittently return 503."*
- **The manager confirms it in the code.** `pages.create` takes `lock_account` (`FOR UPDATE`, `glow_profiles/tx.py:162`) on the viewer first, then `bulk_create`s up to 100 entries whose `candidate` foreign key points at other `AppAccount` rows. PostgreSQL's referential-integrity check takes `FOR KEY SHARE` on each referenced row, and `FOR KEY SHARE` conflicts only with `FOR UPDATE`.
- **A second cycle, which the manager found and Codex did not name.**
  - `glow_chat`'s pair writers (`block`, `unblock`, `unmatch`, `activate_match`) lock the lower account `FOR UPDATE`, then the higher.
  - Take a candidate C below the viewer V. A pair writer holds C and waits for V. The page holds V and waits for `FOR KEY SHARE` on C. That is a cycle.
  - PostgreSQL then aborts whichever transaction runs its deadlock check first. That may be the block: a block refused with 503.
  - Please check this reasoning.
- **Options:**
  - **(a)** Page creation's viewer lock `FOR NO KEY UPDATE` (`select_for_update(no_key=True)`) in place of `FOR UPDATE`. That lock conflicts with `FOR UPDATE`, `FOR NO KEY UPDATE` and `FOR SHARE`, so the page still serializes per viewer and with every writer of the viewer's facts. It does not conflict with `FOR KEY SHARE`, so it closes the page-against-page cycle. It leaves the second cycle: the pair writer's `FOR UPDATE` on C still blocks the page's `FOR KEY SHARE`. The change is inside Stage A's owned paths.
  - **(b), recommended:** every account-row lock taken `FOR NO KEY UPDATE` (`lock_account`, `lock_account_any_state` and `glow_chat`'s `_lock` for `AppAccount`), and page creation's as in (a).
    - No writer deletes an `AppAccount` row or changes its key; deletion is the lifecycle transition (`glow_chat`'s 5.6). So `FOR UPDATE`'s extra strength guards nothing.
    - Writers still serialize with each other and with `FOR SHARE` readers, and a foreign-key check never waits on a writer. That closes both cycles, and any future insert that references another account.
    - It changes the reviewed lock protocol (DM-13; P06.DB's D5) in `glow_chat/contact.py` and `glow_profiles/tx.py`, outside Stage A's owned paths. The ordering proof's lock-order checks and controls would need reading against it.
  - **(c)** (a), plus a bounded retry of page creation on `deadlock_detected` (SQLSTATE `40P01`). This is smaller than (b). But the victim PostgreSQL picks may be the pair writer, so a block or unmatch could still fail with 503, unless the pair writers retry too.
- **The test,** whichever option: concurrent page creation from separate connections in the discovery suite. Two mutually eligible viewers create batches at once, in both orders, and both pages succeed. Under (b), add a pair writer on (C, V) racing V's page creation, with C below V.
- **Asked:** which option; whether (b)'s scope belongs in this correction or its own item before Stage B; and what the proof must show.

**2. V1, the tie-break key's pads as SQL parameters** (the manager's verification).
- **What the code does:** `predicates.TIE_BREAK` computes HMAC-SHA-256 in SQL. The key's inner and outer pads (`keys.sql_pads`: the derived key `sha256(salt + SECRET_KEY)`, XORed with constants) are passed as statement parameters.
- **The exposure:** a server that logs statement parameters records them. Examples are PostgreSQL's `log_min_duration_statement` with parameters, which PostgreSQL 13 and later log in full by default (`log_parameter_max_length = -1`), and Django's query log under `DEBUG`. Anyone holding them can compute the order, the band leak Q2 closes. `SECRET_KEY` itself is not revealed.
- **Options:**
  - **(a)** Accept it, with a P11 condition that statement logging excludes parameters on the app's database. This needs no code change.
  - **(b)** A per-batch random secret, generated when the batch is created, stored in the batch row, never returned, and used as the tie-break key. A leaked log then reveals one expired batch's order at most. This needs a field in migration 0010.
  - **(c)** Order in Python instead. This breaks D2's one-statement selection and its bound.
- **The manager recommends (b),** in the same correction as CX1. Asked: which option.

**3. Sequence** (recommended): one correction, C1, carrying CX1's and V1's fixes, each with its tests and reversals. Then the manager's verification. Then the exact-head review of Stage A, reading `ad9ff08` and C1 together, with its prompt's revision 2. Then your pre-merge read. Agree?

**4. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**
