# DM-55 consultation — SV2 Stage A's exact-head review: C1-3, the rulings it asks for, and correction C2's scope

- **Owner:** App Manager 10. Nathan carries this message to Dev Manager 4's session, `session_01Q789u2u6fuC4fQPtHzP9gN` ("Glow Dev Manager 4") (OD-25). App Manager 10 receives the answer.
- **Revision 1, 10 November 2026.**
- **Why:** Stage A's exact-head review asks for the Dev Manager's ruling on C1-3 and four other items. The fixes of several findings change a design or touch a security boundary (privacy, consent, data ownership), so they go to the Dev Manager before correction C2's prompt (the manager workflow, step 6, "Fix or carry, by rule"). It is also the next consultation, which confirms DM-53's and DM-54's conditions as applied (the review log, "Deferred conditions").
- **Where the result goes:**
  - your report in `docs/continuity/dev-manager/reviews/`;
  - App Manager 10's disposition in the review log, "DM-55";
  - the brief (revision 5) where a design changes;
  - correction C2's prompt;
  - the carried-items file.
- **Stream variables:** none are needed.
- **If no report arrives:** no C2 prompt goes to Nathan; App Manager 10 asks Nathan whether Dev Manager 4's session is still available.
- **Deletion condition:** prune after the review log holds DM-55's disposition and SV2's Stage A PR has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-55 — SV2 Stage A's exact-head review: C1-3, the rulings it asks for, and correction C2's scope.** From App Manager 10, relayed by Nathan to Dev Manager 4. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE or Railway;
- check environment variable names only.

**Where it stands.**
- **Correction C1 is integrated** at `6e5d0d1` (code head `86a2156`; run of record 42769301337, every job passed, the profile suite 47 of 47).
- **The exact-head review has reported**, from its prompt's revision 2 at `9c5f6ee`. Its report and the manager's disposition of each finding are in the evidence record (`docs/testing/evidence/2026-11-10-sv2-profiles-media.md`, "Exact-head review of Stage A").
  - **The verdict:** changes required, narrowly. No finding is blocking. Findings 1 to 8 fall in the correction classes, and the review sends findings 9, 10, 13 and 14 to you with C1-3.
  - **Its statements:** no path leaks a value, lets a member reach another member's object, acts unauthenticated, or makes a profile `visible` with a requirement missing. No existing test was weakened. None of your conditions is plainly unmet.
- **Codex:** its P2 on `40db2c2` (`operations.py:1019`) is C1-3's point, item 1 below. Its review of `9c5f6ee` raised nothing new. Its two P1 threads from `033e8d4` are answered and resolved.
- **The manager's error:** accepting C1-3, App Manager 10 gave only the argument for it (AM10-14).
- **Next after your answer:** the brief's revision 5 with your words, then C2's prompt. A full exact-head review of C2's head follows (item 8).

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. A date that fails the adult rule, at both writers** (C1-3; findings 2 and 13; Codex's P2).
- **As built, for an account whose state is `self_declared_adult`:**

  | Writer | A date under 18 | A future date |
  |---|---|---|
  | The eligibility step (`adult_check`, `operations.py:922-955`) | 200 `applied`: the reset commits, and a keyed idempotency record of the intent is kept 24 hours (the review's P5) | 200 `applied`: the reset commits (P1) |
  | The birth input (`save_birth_input`, `:1006-1023`) | 403 `forbidden`: the reset commits, with no idempotency record (Y6 to Y8) | 400 `invalid_request`: nothing changes (P2) |

  - **The reset:** `unknown` with no date, the current birth input `missing` and its mapping `pending`, then D9's recompute.
  - **An under-18 birth input refused by an earlier gate** skips the reset. The gates are an unknown time (400), a stale version (409) and a lapsed onboarding consent (403), all checked before the date. At the eligibility step a stale version (409) does the same.
  - **After a reset, earlier birth input revisions keep their date, time and place** as `missing`, and the owner's read returns them (finding 13). Y6's operative words make only the current one stop being current. Its closing clause says "no birth data of a self-declared minor is kept (G-01)".
  - **No test pins** either future-date behaviour.
- **The words:**
  - **For counting a future date as failing (Codex):** D7's check has three conditions ("valid, not in the future and 18 or over"). Acceptance check 7 counts "a future date" among the dates that fail. `adult_outcome` fails one. Y6 and Y7 speak of a date that fails "the rule" and "the adult rule".
  - **For the session's reading:** your section 8 speaks of "a date under 18", and P04's rule returns `unknown` for a future date and refuses it as invalid input (`policy.ts:29`, `store.ts:255`).
  - **The review's view:** the words do not decide. Neither reading keeps anything of the refused input, and a future date declares no age, so a minor gains nothing from either.
- **Options:**
  - **(a) One rule, counting a future date as failing.** At both writers, a date in the future or under 18 is refused, stores nothing of it and no idempotency record, and the reset commits.
  - **(b) One rule, the session's reading.** Only a date under 18 resets, at both writers, and a future date is invalid input at both, refused with no change.
  - **With either:**
    - (1.2) the date's outcome is checked before the request's other refusals, once the account is a self-declared adult;
    - (1.3) the eligibility step's failing rerun is refused, not `applied`, and keeps no idempotency record;
    - (1.4) a reset erases the date, time, place and time zone of every birth input revision. The rows stay, as `missing`, so the events that name them still name a record. This needs a migration making those `BirthInput` fields nullable, with a check that an erased revision is `missing`. The alternative is to keep them, as built, and carry them to G-01 (P07).
- **The manager recommends (a), with 1.2, 1.3 and 1.4's erasure.**
  - (a) makes the code do what D7, acceptance check 7 and `adult_outcome` already say, and the eligibility step does it today. (b) needs new words in three places. Its cost is low: P04's client refuses a future date before sending it.
  - 1.2 and 1.3 put Y6's rule on both paths.
  - 1.4 is Y6's closing clause and your section 8's reason: a self-declared minor's birth data "has no use once the account is no longer an adult's".
- **Proposed words, if (a):**
  - **In D7, replace the bullet that begins "**A birth input whose date fails the rule is not stored (DM-54).**" with:**

    > - **A date that fails the adult rule (DM-54; DM-55).** A date fails the rule when it is in the future or under 18 at the server's clock. For an account whose state is `self_declared_adult`, both writers, the eligibility step and the birth input, check the date's outcome first, after the replay check and before any other refusal. A failing date is refused (`forbidden` under 18, `invalid_request` in the future), nothing of it is stored and no idempotency record is kept, but the transaction still commits the failing rerun: the age state becomes `unknown` with no date; the date, time, place and time zone of every birth input revision are erased, and each revision is kept as `missing` so that earlier events still name a record; a mapping returns to `pending`; and a `visible` profile becomes `incomplete`. The operation returns the refusal without raising, so the transaction commits. A retry is refused, since the account is no longer an adult's, and changes nothing more. For an account whose state is `unknown`, a failing date at the eligibility step is refused and changes nothing. "A failing date is refused and not stored" then holds on both paths, and no birth data of a self-declared minor is kept (G-01). P04's `saveBirth` saved the input; the server does not.
  - **In D8, replace** "A revision whose date fails the adult rule is refused and not stored (D7; DM-54)." **with:** "A revision whose date fails the adult rule, under 18 or in the future, is refused and not stored, and the account's earlier revisions are erased (D7; DM-54; DM-55)."
  - **In acceptance check 7, replace** from "A corrected date reruns the check:" to "a retry is refused and changes nothing." **with:** "A corrected date that fails the rule, under 18 or in the future, at the eligibility step or in a birth input, is refused before the request's other refusals and stores nothing, with no idempotency record. The age state becomes `unknown` with no date, every birth input revision's date, time, place and time zone are erased, and a visible profile becomes `incomplete`, so a send is refused. A retry is refused and changes nothing. A birth input with another passing date changes the age state's date."
  - **In "Owned paths":** a new migration, `glow_persistence/migrations/0008_…`, for the nullable fields and the check.
- **Asked:** which option, with 1.2 to 1.4? The words for D7, D8 and check 7?

**2. The history setting's fixed limit** (finding 1).
- **As built:** `_history_refusals` (`glow_domain/profile_settings.py:390-415`) refuses a more readable change unless it names the onboarding consent's current version, and a version other than the one the current setting names.
- **The gap:** the setting's own label can change in a publication that makes nothing more readable. A first publication changes only the label. A second makes a cause readable, naming the onboarding version members already accepted. Both are allowed, and no new wording was shown.
- **Fact:** an onboarding version label is numbered by its publication (`ps.policy_version(name, number)`), so it is never reused.
- **Options:**
  - **(a)** A publication that makes nothing more readable keeps the version the current setting names. Since the onboarding label only grows, each more readable change then needs a new onboarding version.
  - **(b)** A more readable change names a version that no earlier history publication named. This reads the setting's history at every publication.
- **The manager recommends (a):** one comparison, and no history read.
- **Proposed words:** in D2's fixed limits, after "a change to H that makes more readable reaches a member only after they accept the consent wording that describes it (OD-60's table, H);" add: "the history setting names the onboarding consent version that describes it. A publication that makes a cause more readable names the onboarding consent's current version, which must differ from the version the current setting names; one that makes nothing more readable keeps the version the current setting names (DM-55);".
- **Asked:** which, with the words?

**3. The sensitive-fields consent's version** (finding 9).
- **As built:** a sensitive save checks only that the latest `sensitive_profile` decision is `accepted` (`_sensitive_accepted`, `operations.py:128-130`). The review's P7: accepted at `v2` with `v3` current, a sensitive field and a narrowed set both save (200).
- **What applies:**
  - F02: "old consent version rejected".
  - The acceptance itself checks the current version under the pointer's lock.
  - DM-54 item 5 settled the onboarding analogue: a new version demotes no one, completion needs the current version, and K1 to K3 carry the rest.
- **Options:**
  - **(a)** A sensitive save needs the sensitive consent accepted at its current version, read under its pointer's lock after the account row lock. Values saved under an earlier version stay until the member's next such save or a withdrawal. What a new version asks of existing values is carried with K1.
  - **(b)** Carry the whole question to P08 with K1 to K3.
- **The manager recommends (a):** it is F02's rule at the one place SV2 collects new sensitive data, and it leaves existing values as DM-54 left onboarding.
- **Proposed words:** in D6's "The sensitive-fields consent" bullet, after "before either field's "show me" set is narrowed." add: "Each of those saves needs the consent accepted at its current version, read under its policy pointer's lock after the account row lock (F02: "old consent version rejected"); a value saved under an earlier version stays until the member's next such save or a withdrawal, and what a new version asks of existing values is carried with DM-54's K1 (DM-55)."
- **Asked:** which, with the words?

**4. C1-1: a lapse the profile edit finds** (finding 10).
- **As built:** `recompute.entry` records every demotion in the profile edit as the owner's `edit`, carried by `profile_edited`, with no `profile_demoted` (`recompute.py:83-84, 130-136`). That includes a lapse the edit finds but did not cause, such as a new onboarding consent version.
- **Y4's words** keep `edit` for "the owner's own edit that clears the summary", and make `requirement_removed` "the demotion that follows another write". The review: the code is outside Y4's literal words. SV3 would have to reread the state on `profile_edited`, and no record says so. The contract document's F04 sentence says a lapse is `requirement_removed` with `profile_demoted`.
- **Options:**
  - **(a)** The code follows Y4. In the profile edit, a demotion is `edit` only when the edit itself leaves the display name or the summary empty; any other is `requirement_removed`, with `profile_demoted`.
  - **(b)** Keep it, and record in the data model and for SV3 that `profile_edited` can carry a demotion SV3 must reread.
- **The manager recommends (a).** It makes the code do what Y4 says, in Y4's words, and the contract document's sentence then holds. No new words are needed.
- **Asked:** confirm (a), or rule (b)?

**5. The withdrawal's field rows and the outbox** (finding 12).
- **As built:** `_withdraw_sensitive_data` deletes the member's orientation and relationship status rows (`operations.py:798-799`). Earlier `profile_field_changed` events name those rows (`aggregate_id` and `payload_ref` are the row's ID, `:414-421`), and the withdrawal emits no field event.
- **The data model:** "Outbox payload references must target an existing owning record retained through delivery/reconciliation", and "No event relies on rereading a body already erased by deletion".
- **Options:**
  - **(a) Set the rows to "not stated" in place.** Each row gets `value_ids` `["not-stated"]` (what a member who states none stores, `profile_fields.NOT_STATED`), no own words and a bumped version, and each emits `profile_field_changed`. Earlier events still name an existing record, and nothing of the values is kept.
  - **(b)** Keep the deletion, and change the data model's text for these events.
- **The manager recommends (a):** it keeps the data model's rule and D6's outcome ("The member then appears as "not stated" in both fields").
- **Proposed words:** in D6's "The sensitive-fields consent" bullet, replace "Withdrawal, in one transaction, removes the member's own orientation and relationship status values and orientation's own words," with "Withdrawal, in one transaction, sets the member's orientation and relationship status rows to "not stated" in place, with no own words, each row's version bumped and `profile_field_changed` emitted for it, so that earlier events still name an existing record (DM-55),".
- **Asked:** which, with the words?

**6. Settled by the manager, for your confirmation.**
- **Finding 11, three bodies that do not answer 400.** A 321-digit integer coordinate and 10,000 nested arrays answer 500 `text/html`, and U+0000 in a stored text answers 503 with `retryable: true`.
  - **The manager's words, for C2's section of the brief:** "A body the parser cannot hold, such as an integer too large for its number check or nesting deeper than the parser allows, and a text holding U+0000, which the database cannot store, are refused `invalid_request` (400) with the contract's `Error`, like any other invalid body. No value is echoed."
- **Finding 14, under W5.** Re-acceptance at a new version from `accepted` is a transition both consent writers make. It becomes two F02 entries: `accept` from `accepted` to `accepted` and `accept_sensitive` from `accepted` to `accepted`, each `owner` with the policy `consent_current`. Each has an allowed example (the current version, newer than the one accepted) and a forbidden one (an old version).
- **Findings 3 to 7, test-only fixes in C2, each with a reversal that fails its new case:**
  - (3) a case proving the account row lock;
  - (4) a sensitive save after a withdrawal, refused;
  - (5) the scans and the table search match each fixture value in every form the code could print. The static logging guard covers `glow_identity/age.py`, and no case prints a fixture date in prose;
  - (6) every command's stored digest checked;
  - (7) the static guards forbid a queryset `.update(state=…)` on a profile and a refusal reason built with `Result(…)` from a value.
- **Finding 15's test nits, in C2:**
  - the sealed-runtime test asserts its `refused`;
  - the scan's verdict reads its own line, not the word "clean" anywhere;
  - the suite's case count is pinned;
  - the four registry prerequisites are pinned;
  - `age_years`, with no caller, is removed.
- **Finding 8, the records:** C2's record corrects the eight claims in its own section, and Stage A's sections stand as written. The two contract-document sentences follow items 1 and 4.
- **Carried:**
  - to P07: a revocation or restriction refused for a non-active account (D18 says "at any time"), and `publish` accepting a `system:` subject;
  - to G-01, with P07: the adult check's missing upper bound;
  - to P11's plan: `IdempotencyRecord` with no account foreign key (pre-existing);
  - to C2's record: a wrong method answering `invalid_request` with status 405, against the contract document's error table.
- **The CI policy (governing text; pre-existing):** its `actions/upload-artifact` row (line 12) says "both uploads" twice, and there are four, each with `if-no-files-found: ignore`.
  - **The manager's words, in this batch:** "the inputs both uploads use" becomes "the inputs every upload uses", and "Both uploads use `if-no-files-found: ignore`" becomes "Every upload uses `if-no-files-found: ignore`".
  - Your pre-merge read covers it with DM-54 section 13's paragraph.
- **Asked:** confirm each, or name a change.

**7. DM-53's and DM-54's conditions as applied** (the review log, "Deferred conditions").
- **What to confirm:**
  - W1 to W10, in the brief's revision 3, carried into revision 4;
  - Y1 to Y10 and Y12, in revision 4;
  - Y11, in `docs/architecture/data-model.md`;
  - K1 to K5, in `docs/planning/carried-to-later-items.md` and `docs/testing/p11-deferred-acceptance.md`.
- The manager applied each by script, in your words. Choices your words left open are marked "the manager, on DM-NN's words".
- **Asked:** confirm them as applied at this commit, or name a departure.

**8. Correction C2's scope and its review.**
- **If items 1 to 6 go as recommended,** C2 carries:
  - item 1's code, migration, tests and records;
  - items 2 to 5's code and tests;
  - item 6's fixes;
  - Codex's P2, which is item 1;
  - the record corrections.
- **Its review:** C2 changes designs and is well over 60 non-test lines, so a full exact-head review with a written threat model reads C2's head, not a delta review (M05 S2). Codex reads the PR's head as usual.
- **Asked:** agree?

**What happens next:** App Manager 10 applies your words in the brief's revision 5 and writes C2's prompt. A design that needs another read comes back first. Your pre-merge read follows C2's review, and covers:
- the CI policy's text;
- the mapping texts;
- any condition this answer leaves for it.

No GitHub operation is asked of Nathan.
