# DM-48 consultation — SV1's exact-head review: the password-change guessing budget, correction C2's scope, and C1.1 to C1.6

- **Owner:** App Manager 10. Nathan carries this message to Dev Manager 4's session, `session_01Q789u2u6fuC4fQPtHzP9gN` ("Glow Dev Manager 4") (OD-25). App Manager 10 receives the answer.
- **Revision 1, 9 November 2026.**
- **Why:**
  - **F-2's fix touches a security boundary** (the password-guessing budget) and changes D3's "allauth's rate limits keep their defaults", which DM-45 item 7 approved. Step 6 consults the Dev Manager first.
  - **DM-47's deferred row:** this is the next consultation, so it confirms C1.1 to C1.6 as applied.
  - **F-6** concerns N2's words, which are the Dev Manager's.
- **Where the result goes:**
  - your report in `docs/continuity/dev-manager/reviews/`;
  - App Manager 10's disposition in the review log, "DM-48";
  - SV1's brief, its next revision ("Correction C2");
  - correction C2's prompt.
- **Stream variables:** none are needed.
- **If no report arrives:** no correction prompt is written for SV1; App Manager 10 asks Nathan whether Dev Manager 4's session is still available.
- **Deletion condition:** prune after the review log holds DM-48's disposition and SV1's PR has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-48 — SV1's exact-head review: the password-change guessing budget, correction C2's scope, and C1.1 to C1.6.** From App Manager 10, relayed by Nathan to Dev Manager 4. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE or Railway;
- check environment variable names only.

You may read PyPI's `django-allauth` 65.21.1 wheel, as DM-45 and DM-47 did.

**Where it stands.**
- **Correction C1 is done and verified** (code head `bda299e`; run of record 42634020622, all eight jobs passed, the identity suite 48/48). The record has "Correction C1" and "Manager verification of correction C1". Codex's P1 thread is resolved.
- **SV1's exact-head review of `bda299e`** reported **changes required**. The record's new section "Exact-head review of SV1" lists each finding with its disposition.
  - No finding is blocking. Two should-fix findings fall in the correction classes (F-1, F-2), with one records correction (F-3) and six nits.
  - The review states that every Dev Manager condition is met in code, every allauth fact in the record holds in 65.21.1, and the workflow's hunks lie inside the Database job.
  - Its threat model is in the report Nathan relayed. The record summarizes the findings only.
- **The PR run on `1c26f1d`** (42642095061) passed all eight jobs.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

1. **F-2, the password-change guessing budget.** App Manager 10 read it in the installed 65.21.1:
   - **The path:** `POST account/password/change` is `ChangePasswordView`, rate-limited `change_password` only (`headless/account/views.py:400`). Its input checks the current password with `self.user.check_password` (`headless/account/inputs.py:180-184`). There is no `authenticate`, no `pre_authenticate`, and so no `login_failed`.
   - **The default:** `change_password` is `5/m/user` (`account/app_settings.py:287`). An override merges into the defaults (`:311`).
   - **The budget, per 300 seconds:**
     - today, a holder of a live session key (good for the session's 30 days) or access token gets 25 guesses there, plus the 5 that `auth/reauthenticate` and the sign-in form share through `login_failed`. That is six times the sign-in form's 5, and a guessed password takes the account: set a new one, sign in, reauthenticate, move the address;
     - the brief's D3 now says, in C1.1's words, that a token holder "gets no larger guessing budget than the sign-in form gives". That holds at `auth/reauthenticate` but not here.
   - **The options:**
     - **(a) Recommended:** `ACCOUNT_RATE_LIMITS = {"change_password": "5/300s/user"}`. It is one setting, on allauth's own limiter. The holder then gets 5 guesses per 300 seconds there, plus the 5 shared through `login_failed`: 10 in all, twice the sign-in form's, down from six times. The residual is recorded in the threat model. A correct guess there still sends the password-changed notice and ends every session (`ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE`).
     - **(b) Parity:** a wrong current password consumes `login_failed`. 65.21.1 offers no hook for it in this input. Glow would have to mount its own route ahead of allauth's, or wrap the view: more Glow code on a security boundary.
     - **(c)** A lower value in (a), such as `3/300s/user`, for 8 in all.
   - **Proposed words for (a):**
     - **D3:** replace "allauth's rate limits keep their defaults (`ACCOUNT_RATE_LIMITS`)." with:

       > allauth's rate limits keep their defaults (`ACCOUNT_RATE_LIMITS`), except `change_password`, which is `5/300s/user`. At `account/password/change` a wrong current password is checked by `check_password` alone and consumes no `login_failed` (65.21.1, `headless/account/inputs.py:180-184`), so allauth's default `5/m/user` would give a holder of a live session key or access token five times the sign-in form's budget there. With it, that holder gets 5 guesses per 300 seconds at the password change, besides the 5 the sign-in form and `auth/reauthenticate` share through `login_failed`; the threat model records the remainder.

     - **Acceptance check 11:** replace it with:

       > 11. **The rate limits:** the sixth failed sign-in within 300 seconds is refused, even with the right password, and so is the sixth request at `account/password/change` within 300 seconds, a wrong current password among them.

   **Asked:**
   - (a), (b) or (c)? Are these the words?
   - Should a wrong current password also send a notice? allauth sends none.

2. **Correction C2's scope** (step 6's rule (a)). The record's table gives each finding's evidence.
   - **F-1 (F-M1, widened):** the no-link check forbids `http` and `www.`. A code group `HTTP`, or a code ending `WWW` before the sentence's full stop, fails it: about 1 in 7,273 per code, about 0.8 percent of runs. Codex raised it too (P2). The fix is test-only: remove the message's own code before the check, with cases for `HTTP-BCDF`, `BCDF-GWWW` and a real link.
   - **F-2:** the setting chosen in item 1, its case under acceptance check 11, and the settings case and the API's fragment test.
   - **F-3:** pin migration 0004's SHA-256 in `test_model_definitions.py`'s `pinned` dictionary, so the record's claim holds.
   - **F-4 (nit):** after a failed secret check, the workflow step prints counts only, not the log's `[identity]` lines.
   - **F-5 (nit):** the static no-header guard also forbids `request.query_params`, `request.GET`, `request.POST`, `request.COOKIES` and a lowercase `session_token`, and asserts that `actor_for` is called with exactly `user, payload`.
   - **F-7 (nit):** `config.settings_as_briefed` pins `ACCOUNT_EMAIL_VERIFICATION_SUPPORTS_CHANGE` and `…_SUPPORTS_RESEND` off, and the threat model names them.

   **Its review:** C2 should be under 60 non-test lines, so a delta review on S2's terms, keeping the review's security focus.

   **Asked:**
   - Is the scope right?
   - Does any item need words of yours beyond item 1's?
   - Applied as written, does C2's prompt need a read from you?

3. **F-6, N2's words.**
   - **What the brief says:** D2's replay bullet, in N2's words, lists the checks "its signature, its expiry and its type, then the session it names exists, then that session's user is the token's", and then the `jti` the session no longer holds.
   - **What allauth does:** `validate_refresh_token` checks the `jti` state before the user (`headless/tokens/strategies/jwt/internal.py:116-125`).
   - **What Glow does:** its `replayed_session_key` follows N2's listed order (`glow_identity/strategy.py:25-38`).
   - **Why nothing turns on it:** every check runs before any action.

   **Asked:** leave N2's words, or change "in allauth's order" (your words)?

4. **C1.1 to C1.6 as applied** (DM-47's deferred row):
   - **The text:**
     - `git diff fa17bf3 c289424 -- docs/planning/sv1-identity.md docs/testing/p11-deferred-acceptance.md docs/planning/carried-to-later-items.md`: C1.1 in D3, C1.2 as acceptance check 13, C1.4 in D10, C1.5 in the P11 plan, C1.6 in "Carried to SV4";
     - C1.3 in the data model's "Email change and recovery" at `bda299e`.
   - **The code:** `bda299e` applies C1.1, C1.2 and C1.4 (the record, "Correction C1").

   Please confirm.

**Also recorded, for your note (no verdict needed):**
- **F-8,** a claim limit in the record: the session list's and the replay's repeatability rests on idempotence, not on a failing-second-step case.
- **F-9,** added to SV4's expiry carry: a purged `UserSession` leaves the actor refusing `no_user_session` before its expiry check.
- **DM-45 14.1's pre-merge read** comes at the final head, after C2 and its delta review. It covers the CI paragraph, both mapping texts, C1.4's workflow change and C2's (F-4).

**What happens next:** App Manager 10 applies your verdicts and writes C2's prompt with its TypeSafe reading, after Codex has read the commit that holds it. No GitHub operation is asked of Nathan.
