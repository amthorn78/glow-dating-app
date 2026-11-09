# DM-47 consultation — SV1's email change without reauthentication, its correction, and N1 to N5

- **Owner:** App Manager 10. Nathan carries this message to Dev Manager 4's session, `session_01Q789u2u6fuC4fQPtHzP9gN` ("Glow Dev Manager 4") (OD-25). App Manager 10 receives the answer.
- **Revision 1, 9 November 2026.**
- **Why:**
  - **A design gap on a security boundary.** SV1's implementation session found that an email change needs no reauthentication. DM-45 section 9 approved email change as needing it. Step 6 consults the Dev Manager when a fix touches a security boundary (authorization), and on a design decision that arises in review.
  - **DM-45 1.1's deferred row:** this is the next consultation, so it confirms N1 to N5 as applied.
- **Where the result goes:**
  - your report in `docs/continuity/dev-manager/reviews/`;
  - App Manager 10's disposition in the review log, "DM-47";
  - SV1's brief, if a condition changes text;
  - correction C1's prompt.
- **Stream variables:** none are needed.
- **If no report arrives:** no correction or review prompt is written for SV1; App Manager 10 asks Nathan whether Dev Manager 4's session is still available.
- **Deletion condition:** prune after the review log holds DM-47's disposition and SV1's PR has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-47 — SV1's email change without reauthentication, its correction, and N1 to N5.** From App Manager 10, relayed by Nathan to Dev Manager 4. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE or Railway;
- check environment variable names only.

You may read PyPI's `django-allauth` 65.21.1 wheel, as DM-45 did.

**Where it stands.**
- **SV1 is implemented** on `claude/hopeful-cerf-kc91xx`, code head `269ac3b`, and integrated into the manager branch.
  - The record is `docs/testing/evidence/2026-11-09-sv1-identity.md`. The manager's checks are in its "Manager verification" section.
  - The run of record is push run 42578800951: all eight jobs passed, and the identity suite passed 47 of 47 on the second disposable database.
  - SV1's PR is open from the manager branch. No exact-head review has started.
- **The brief** is revision 3 (`docs/planning/sv1-identity.md`). Since `dc3e551`, only its status line and Sessions changed.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

1. **The gap.** At `269ac3b`, an email change needs no reauthentication:
   - **What the code does:** `glow_identity/conf.py` sets `ACCOUNT_CHANGE_EMAIL = True` and leaves `ACCOUNT_REAUTHENTICATION_REQUIRED` at its default, `False`.
   - **The attack:** a holder of a live access token, refresh token or session key can call `POST account/email` with an address they control, then enter the code sent there. The new address replaces the old one, and a password reset by code to it takes the account. The old address gets the email-changed notice only.
   - **Why it was missed:** DM-45 section 9 approved "email change verified by code. That needs `ACCOUNT_CHANGE_EMAIL = True`, which defaults to `False`, and reauthentication, which does not cycle the key." The brief's D3 named neither setting, and the prompt left them to the session (AM10-06).
   - **Nothing reaches a member:** the runtime is sealed, and the proof uses synthetic accounts.

2. **What 65.21.1 does with the setting on.** App Manager 10 read these in the installed wheel; paths are under `allauth/`:
   - **The defaults:** `ACCOUNT_REAUTHENTICATION_REQUIRED` is `False` and `ACCOUNT_REAUTHENTICATION_TIMEOUT` is 300 seconds (`account/app_settings.py:541-550`). The adapter reads the first for the `allauth.account` app (`account/adapter.py:1086-1096`).
   - **What it guards:** `add_email`, `delete_email` and `mark_as_primary` (`account/internal/flows/manage_email.py:59`, `:23`, `:83`) raise `ReauthenticationRequired` unless the session holds a record marked `reauthenticated` from the last 300 seconds. The headless `POST account/email` is `add_email` (`headless/account/views.py:464`).
   - **A sign-in's own record does not count:** `did_recently_reauthenticate` keeps only records with `reauthenticated` (`account/internal/flows/reauthentication.py:91-107`).
   - **The refusal:** headless answers 401 with the `reauthenticate` flow (`headless/base/views.py:34-35`; `headless/base/response.py:134-136`).
   - **`POST auth/reauthenticate`:**
     - it checks the password through the adapter's `reauthenticate` (`account/forms.py:708-712`);
     - it records `reauthenticated=True` in the Django session (`reauthentication.py:31-33`), and its rate limit is `10/m/user` (`account/app_settings.py:295`);
     - it calls no `login` or `post_login`, so none of Glow's sign-in hooks runs (`headless/account/views.py:578-586`);
     - it cycles no key, and it issues no token pair, since `expose_access_token` exposes one only when the request's user was not already signed in (`headless/internal/authkit.py:83-95`);
     - it modifies the session, so its response carries `meta.session_token`, as any response that modifies the session does (D5; N3).
   - **Not covered by the setting:** password change already asks for the current password. The session list (`DELETE auth/sessions`) has no reauthentication check in 65.21.1.

3. **The proposed correction, C1, before the exact-head review.** The implementation session makes it.
   - **D3:** replace the "**Email change:**" bullet with:

     > **Email change:** one address per account; the new address is verified by code before it replaces the old (`ACCOUNT_CHANGE_EMAIL = True`). The change also needs a reauthentication by password within the last 300 seconds (`ACCOUNT_REAUTHENTICATION_REQUIRED = True`, with allauth's default `ACCOUNT_REAUTHENTICATION_TIMEOUT`); a sign-in does not count as one. Without it, a holder of a live access token, refresh token or session key could move the address and then reset the password from it. In 65.21.1, `POST auth/reauthenticate` records the reauthentication in the Django session only: it cycles no key, issues no token pair and calls none of Glow's adapter hooks, so D5's reference holds. The same setting guards removing an address and marking one primary.

   - **A new acceptance check 13:**

     > 13. **Reauthentication:** an email change without a reauthentication answers 401 with the `reauthenticate` flow, sends no mail and changes no address, and so does one made more than 300 seconds after the reauthentication. A wrong password at `auth/reauthenticate` is refused. With the right password, the change goes ahead as acceptance check 10's notice shows. The reauthentication leaves the session key, its `UserSession` row and its `AccountSession` unchanged, and returns no token pair. A reversal that turns the setting off fails the case.

   - **The data model's "Email change and recovery":** its first sentence becomes:

     > One address per account (`ACCOUNT_CHANGE_EMAIL`), changed only after a reauthentication by password within the last 300 seconds (`ACCOUNT_REAUTHENTICATION_REQUIRED`; a sign-in does not count): the new address is verified by code before it replaces the old, and the old address gets the email-changed notice.

   - **The code:**
     - the setting in SV1's fragment;
     - the settings case and the API's fragment test;
     - the new identity case and its reversal;
     - a reauthentication first in the cases that change an address (`notice.email_change`, `enum.email_change_taken_and_free_alike`);
     - the threat model's endpoint row for `auth/reauthenticate`, now used.

     No other design, interface, contract or dependency changes.
   - **The review:** the exact-head review then reads the corrected head in full, with this in its focus. No delta review is needed, since no review has run.

   **Asked:**
   - Is this the fix you meant in section 9, and are these the words?
   - Is allauth's default of 300 seconds right for SV1, or is the window Nathan's to set before P11, beside the session lifetime (DM-45 3.1)?
   - Should anything else wait on a reauthentication in SV1? The session list has no such check in 65.21.1.
   - Applied as written, does C1's prompt need a read from you? Step 6's sentence suggests not.

4. **N1 to N5, as applied** (DM-45 1.1's deferred row; DM-46 section 1).
   - **The changed text:** `git diff d461ea5 dc3e551 -- docs/planning/sv1-identity.md`, with the P11 plan, the carried-items file and the matrix at `dc3e551`.
   - **Placement:**
     - N1 in D6, acceptance check 8 and the review plan;
     - N2 in D2 and acceptance check 5, and the P11 plan's client entry;
     - N3 in D5, and the same P11 entry;
     - N4 in "Carried to P08";
     - N5 in GP-36's sources cell.
   - **Dropped:** DM-46's optional "and".

   Please confirm.

5. **The session's other findings and deviations, as disposed.** The record's "Manager verification", "Triage":
   - **Natural expiry writes no `session_expired`.** allauth's layer refuses an expired session before the actor finds its row. The brief's rule ("`expire_session` marks an expired row when it is found") is met, so this is carried to SV4, whose system `logout` follows that event. The actor refuses a session past its `expires_at`.
   - **The 10-second window:** allauth's `confirm_email` limit answers 429 for an address mailed in the last 10 seconds. It is recorded in the threat model and goes to the review's focus.
   - **A confirmed reset code verifies the address** outside Glow's adapter. The next sign-in's retry takes `verified`. For the review's focus.
   - **The phone refusal (403):** Glow's adapter refuses `account/phone`, which 65.21.1 mounts in every configuration, where allauth's default would raise a server error. It is accepted, with a test and a reversal.
   - **uv 0.11.32** compiled the locks, each checked by package, version and hash. Both READMEs now say so. uv 0.12.17 in the toolchain is already the hardening item's (DM-17).
   - **The results upload** (the manager's own read): `sv1-identity-results` uploads `if: always()`, so it also uploads after a failed secret check. Its JSON holds the case lines the job prints only after that check passes. For the review's focus.

   **Asked:** does any of these need more than its disposition?

**Also recorded, for your note (no verdict needed):**
- **AM10-06:** DM-45 section 9's named setting was not carried into the brief. The prevention: a disposition reads a report's approval text as well as its conditions.
- **Updated by the manager in this batch:**
  - the data model's opening paragraph and the contract's opening "Not implemented" line, which read as before SV1;
  - the CI policy's Database proof checks paragraph (governing).
- **DM-45 14.1's pre-merge read** (the CI paragraph and the two mapping texts) is not asked now. It comes at the final head, after C1 and the review, so that it reads the texts as they merge.

**What happens next:** App Manager 10 applies your verdicts. It then writes C1's prompt with its TypeSafe reading, after Codex has read the PR's head. No GitHub operation is asked of Nathan.
