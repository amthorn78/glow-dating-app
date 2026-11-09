# DM-47 — SV1's email change without reauthentication, its correction, and N1 to N5

- **From:** Dev Manager 4 (`session_01Q789u2u6fuC4fQPtHzP9gN`), on `claude/dev-manager`. **To:** App Manager 10, relayed by Nathan (OD-25).
- **Read at:** `6b8c9580624e32d1d194d8e8a46bf74456a32099` of `claude/magical-wozniak-yfmmx2`, with SV1's code head `269ac3b`. The manager branch has since moved to `95a0bd4`, a records commit: it records that Codex's only finding on PR42's head is this same gap. Between `269ac3b` and `6b8c958`, only two READMEs' uv sentences changed outside the records.
- **Written:** 9 November 2026, between 13:12 and 13:20 UTC.
- **Boundaries kept:**
  - I checked environment variable names only; none of the six names is present.
  - I called no provider, database, HDE, Railway or TypeSafe service, ran no application test, and wrote only this file. Notion was read, not edited.
  - For allauth I read the 65.21.1 wheel I downloaded and checked for DM-45 (SHA-256 `7bdf018c…`, as PyPI lists it). I installed nothing and ran none of its code.

## 1. What I read

- **SV1's code at `269ac3b`:**
  - `glow_identity/conf.py`: its allauth settings;
  - `adapter.py`: its overrides;
  - `strategy.py`: the replay check;
  - the identity job's steps in `foundation.yml`: the suite, its secret check and the results upload.
- **allauth 65.21.1:** every path the consultation cites, and more:
  - the reauthentication settings, the adapter's `is_reauthentication_required`, `reauthenticate`, `authenticate` and `pre_authenticate`;
  - the guards in `manage_email.py`, and `reauthentication.py` whole;
  - the headless `dispatch`, `ManageEmailView`, `ReauthenticateView` and its input;
  - `_add_session_meta`, `expose_session_token` and `expose_access_token`;
  - the headless account and session routes.
- **The records at `6b8c958`:**
  - the SV1 record's "Deviations, findings and the stop rule" and "Manager verification" sections, the triage included;
  - SV1's brief, revision 3, with its diff since `dc3e551`;
  - at `dc3e551`: the brief, the P11 plan, the carried-items file and the matrix (for N1 to N5);
  - the carried-items file's SV4 entries at `6b8c958`;
  - `glow_chat`'s expiry checks.
- **Notion,** read-only (section 8).

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1. The gap | **Confirmed.** `conf.py` sets `ACCOUNT_CHANGE_EMAIL = True` and nothing sets `ACCOUNT_REAUTHENTICATION_REQUIRED`, which defaults to `False`. Then `is_reauthentication_required` returns `False` before any check, so `add_email` runs for any holder of a live access token, refresh token or session key. The attack is as described. Codex found the same gap independently |
| 2. The reading of 65.21.1 | **Confirmed, with two corrections.** A wrong password at `auth/reauthenticate` also counts against the sign-in limit, so a token holder gains no guessing budget. And the reauthentication response carries no `meta.session_token`: the key does not change |
| 3. Correction C1 | **Approved with conditions** C1.1 to C1.4: the D3 words, sharpened; acceptance check 13, sharpened; the data model's sentence as written; and **the results upload, fixed in C1** (item 5). It is the fix section 9 meant. The 300 seconds are right and not Nathan's. Nothing else in SV1 needs a reauthentication; the session list goes to P11 (C1.5). C1's prompt needs no read |
| 4. N1 to N5 as applied | **Confirmed** word for word at `dc3e551`, and the replaced texts are gone. DM-45 1.1's deferred row can close |
| 5. Other findings, as disposed | **All approved, with two additions:** the results upload needs a fix, not only a focus line (C1.4); and SV4's expiry carry should name the notification composer (C1.6) |
| Notion | **Matches** `6b8c958`, and DM-46's branch nit is fixed |

**How to apply:** C1.1 to C1.6 change text in given words. They may be narrowed, never widened. Applied as written, C1's prompt needs no read from me: it authorizes no credential use and no live provider action. My next consultation confirms the words as applied, and the exact-head review reads the corrected head in full. No delta review is needed, since no review has run.

## 3. Items 1 and 2 — the gap, and what 65.21.1 does

**The gap is real, and the root is my own sentence.**
- **What DM-45 said:** section 9 approved "email change verified by code. That needs `ACCOUNT_CHANGE_EMAIL = True`, which defaults to `False`, and reauthentication, which does not cycle the key."
- **What I had read, and what I missed:** I had read that `add_email` calls `raise_if_reauthentication_required`. I did not name the setting that makes the call do anything, nor check its default. In 65.21.1, `is_reauthentication_required` returns `False` as soon as the adapter's `is_reauthentication_required` (`account/adapter.py:1086`) reads `ACCOUNT_REAUTHENTICATION_REQUIRED` as `False`. So my sentence described a guard that is off by default.
- **AM10-06 is right** that the disposition should have carried it. The first omission was mine. My own prevention: a statement that rests on a setting names the setting and its default.

**Each cited line is as the consultation says:**
- the defaults (`REAUTHENTICATION_REQUIRED` `False`; `REAUTHENTICATION_TIMEOUT` 300);
- the three guarded flows (`delete_email`, `add_email`, `mark_as_primary`, each opening with `raise_if_reauthentication_required(request, app="allauth.account")`);
- `ManageEmailView.post` reaching `add_email` outside the sign-up stage;
- `did_recently_reauthenticate` keeping only records with `reauthenticated`, so a sign-in's own record does not count;
- `dispatch` answering `ReauthenticationRequired` with `ReauthenticationResponse` (401, with the `reauthenticate` flow);
- `ReauthenticateView` (rate limit `reauthenticate`, `10/m/user`), its input's `clean_password` calling the adapter's `reauthenticate`, and `reauthenticate_by_password` recording `reauthenticated=True`;
- no `login`, `post_login`, key cycle or token pair.

**Two corrections to the reading:**
- **The guessing budget is the sign-in form's.** The adapter's `reauthenticate` checks the password through `self.authenticate`, which calls `pre_authenticate` (`account/adapter.py:794-803`). That consumes allauth's `login_failed` limit, `10/m/ip,5/300s/key`, keyed by the member's address, and rolls back the consumption only on success. So a token holder guessing the password at `auth/reauthenticate` is held to the same 5 attempts per 300 seconds as anyone at the sign-in form. The `10/m/user` limit is only an outer bound. The side effect is the sign-in form's too: five wrong attempts lock the address's sign-in for up to 300 seconds.
- **No `meta.session_token` in the reauthentication's response.** `_add_session_meta` asks `expose_session_token`. That returns the key only when the session was modified *and* the key differs from the one the request carried (`headless/internal/sessionkit.py:33`: `if not hdr_token or hdr_token != new_token`). For a request signed in by its access token, `hdr_token` is the key from the token's `sid`. Reauthentication changes no key, so the two are equal, and nothing is exposed. Glow's strategy does not override `get_session_token`. This is what N3 says ("at sign-in, and again whenever the key changes"), so N3 stands, and C1.2 asks the case to show it.

**Nothing reaches a member:** the runtime is sealed, the proof's accounts are synthetic, and the PR is not merged.

## 4. Item 3 — correction C1

**It is the fix section 9 meant.** With the conditions below, C1's words are right.

- **C1.1 D3.** Replace the "**Email change:**" bullet with the manager's words, sharpened in three places (the session; the sign-in hooks; the guessing budget):

  > - **Email change:** one address per account; the new address is verified by code before it replaces the old (`ACCOUNT_CHANGE_EMAIL = True`). The change also needs a reauthentication by password within the last 300 seconds, in the same session (`ACCOUNT_REAUTHENTICATION_REQUIRED = True`, with allauth's default `ACCOUNT_REAUTHENTICATION_TIMEOUT`); a sign-in does not count as one. Without it, a holder of a live access token, refresh token or session key could move the address and then reset the password from it. In 65.21.1, `POST auth/reauthenticate` records the reauthentication in the Django session only: it cycles no key, issues no token pair and runs none of Glow's sign-in hooks (it calls neither `login` nor `post_login`), so D5's reference holds. A wrong password there consumes the same `login_failed` limit as a failed sign-in (the adapter's `authenticate`), so a token holder gets no larger guessing budget than the sign-in form gives. The same setting guards removing an address and marking one primary.

- **C1.2 Acceptance check 13.** Use these words in place of the proposed ones:

  > 13. **Reauthentication:** an email change right after sign-in, with no reauthentication, answers 401 with the `reauthenticate` flow, sends no mail and changes no address, and so does one made more than 300 seconds after the reauthentication, or in another session than the one that reauthenticated. A wrong password at `auth/reauthenticate` is refused, and the sixth wrong password within 300 seconds is refused as too many attempts. With the right password, the change goes ahead as acceptance check 10's notice shows. The reauthentication leaves the session key, its `UserSession` row and its `AccountSession` unchanged, and returns no token pair and no `session_token`. A reversal that turns the setting off fails the case.

  **What the additions pin:**
  - **"Right after sign-in"** pins that a sign-in's own record does not count.
  - **"Another session"** pins that a reauthentication is per session: the records live in the Django session.
  - **"The sixth wrong password"** pins the guessing budget.
  - **"No `session_token`"** pins section 3's reading. If the installed release returns one, the session records it as a deviation, and N3's text is reread.

- **C1.3 The data model's "Email change and recovery":** approved as written.

- **C1.4 The results upload (item 5's last finding; fixed in C1, by step 6's rule (a)).**
  - **The defect:** the step "SV1: save the identity suite's results JSON" runs `if: always()`. The secret check in the step before it scans only the suite's log (`identity.log`), never `identity-results.json`. So the results JSON is uploaded unscanned, even after the check has failed, as an artifact of a public repository (OD-51).
  - **Why it is a defect, not a focus line:** acceptance check 12 says no secret appears in the job's output, and an artifact is output. The values are synthetic and live for one run, so nothing is exposed today. But the check exists to stop exactly this.
  - **The words.** Add to the brief's D10, after "**The run's secrets**":

    > - **The results upload is checked first.** The job's secret check scans the suite's results JSON with the same values as its log, and the results artifact is uploaded only when that check has passed; after a failed check nothing is uploaded, and the job's log shows only the suite's own result lines.

  - **A reversal** that uploads unconditionally, with a planted value in the JSON, shows the check refusing.

- **C1.5 The session list, carried to P11.**

  **Nothing else in SV1 needs a reauthentication:**
  - password change already asks for the current password;
  - C1 guards adding, removing and marking an address;
  - MFA, social sign-in and login by code are off;
  - Glow refuses `account/phone`.

  **What remains is the session list** (`auth/sessions`). It shows a member's sessions with each one's IP address and user agent, and ends them, with no reauthentication in 65.21.1. A token holder can:
  - read where the member signs in from, which is a location signal in a dating app;
  - sign the member's other devices out.

  Neither takes the account: the member's recovery, a password change, ends every session (D6). SV1's runtime is sealed, so nothing serves the list yet. Add to the P11 plan's "From SV1":

  > - **The session list before it reaches members** (DM-47): allauth's `auth/sessions` shows a member's sessions with their IP addresses and user agents, and ends them, with no reauthentication in 65.21.1. Before the app shows it, P11 decides whether listing or ending sessions needs a reauthentication, and whether members see IP addresses at all; it goes to Nathan if it changes what members see.

- **C1.6 SV4's expiry carry** (item 5's first finding). In "Carried to SV4", at the end of the SV1 entry ("… needs a sweep, or another trigger, before it relies on that event."), add:

  > The notification composer's check of whether a registration's session is current compares `expires_at` as well as the state, since a row past `expires_at` still reads `valid`.

**Answers to the questions asked:**
- **The 300 seconds are right, and not Nathan's.** The window sets only how long after typing the password a member may change the address. That is a security parameter with no product trade-off. The session lifetime is different: it sets how often members sign in. A later change to the window is one setting with its test.
- **C1's prompt needs no read.** It authorizes no credential use or live provider action. And step 6's new sentence does not even arise: C1 changes D3's design, which is why it is consulted now, here.

## 5. Item 4 — N1 to N5, as applied

**Confirmed.** By script, against `dc3e551`, with the same normalization as before. P11's client entry is shared by N2 and N3.

| Quote | File | Found |
|---|---|---|
| N1's D6 bullet | The brief | 5 of 5 |
| N1's check 8 | The brief | 4 of 4 |
| N2's D2 bullet | The brief | 9 of 9 |
| N2's check 5 | The brief | 4 of 4 |
| N3 | The brief | 4 of 4 |
| P11's client entry (N2, N3) | The P11 plan | 3 of 3 |
| N4 | "Carried to P08" | 5 of 5 |
| N5 | GP-36's sources cell | 1 of 1 |

N1's focus line ("; allauth's session list, whose ending goes through Glow's `USERSESSIONS_ADAPTER` (D6)") is present.

**The replaced texts are gone:**
- N2's old trigger, "a validly signed refresh token of a live session";
- D5's "during incomplete authentication (DM-45 read this in 65.21.1's source)";
- P08's "and hold the session key. They are personal data;";
- check 8's old opening, which read the password change straight after the first device.

Dropping the optional "and" is fine. Since `dc3e551` the brief changed only in its status line and Sessions.

**At the code head,** the manager's verification reads `strategy.py` running `decode_token`, `get_token_session` and `validate_token_user` before the `jti` check. I read the same in `replayed_session_key`, in that order.

**DM-45 1.1's deferred row can close.**

## 6. Item 5 — the session's other findings, as disposed

- **No `session_expired` on natural expiry: approved, with C1.6.**
  - The SV4 carry is right. The brief's rule is met only because Glow never "finds" the row: at the aligned expiry, allauth's layer refuses first.
  - Today's readers compare `expires_at`: the actor class, `glow_chat`'s send (`contact.py:485`) and its reads (`reads.py:285`).
  - The one future reader that would trust the state alone is the composer, through the registration's session. C1.6 names it.
- **The 10-second window: approved.** It answers alike for every address mailed in the last 10 seconds. What it reveals is recent mail activity at an address, a timing signal. The threat model and the review's focus are the right homes.
- **A confirmed reset code verifies the address: approved.** For an `unverified` account, the next sign-in's retry runs `verified` before `open_session`, which refuses an account that is not `active`. The case `verify.transition_retried_at_sign_in` covers it, and the review's focus is right.
- **The phone refusal (403): approved.** It turns a server error into a refusal, with a test and a reversal, and changes no design.
- **uv 0.11.32: approved.** Each lock was checked by package, version and hash, and both READMEs now say so. uv 0.12.17 in the toolchain stays with the hardening item.
- **The results upload: needs more than its disposition.** It is fixed in C1 (C1.4).

**Also noted, no verdict needed:**
- **AM10-06:** agreed, with my own share in section 3.
- **The opening texts:** updated by the manager.
- **The CI policy's paragraph:** it changed in this batch. **DM-45 14.1's read at the final head is agreed.** It then covers the CI paragraph, both mapping texts and C1.4's workflow change as they merge.

## 7. A note on the reversals

The manager's three re-run reversals cover the seal (R1), the actor's `sid` source (R2) and the replay order (R3). They are the right ones for this head. C1 adds two: the setting's, and the upload's.

## 8. Notion (read-only, at about 13:16 UTC, against `6b8c958`)

What I read: the parts named here, not the whole of either large page.
- **Implementation Control** (as of 12:54:25 UTC):
  - **The status section** names `6b8c958` and its message.
  - **The Branches bullet** lists four branches, from a 12:51 UTC listing: `main` (`da92f1f`), the manager branch (`6b8c958` at this sync), `claude/dev-manager` (`778ee29`, merged at `5cdf01c`) and SV1's session branch. My `git ls-remote` agrees: SV1's branch is at `157c1f6`. **DM-46's nit is fixed.**
  - **The procedure summary's stamp** is at `6b8c958`, moved when the CI paragraph changed.
- **The Dev Manager page** (as of 12:54:25 UTC): DM-46's row, with its disposition, and DM-47's row ("Awaited") match the review log.
- **The Work Register:** SV1 is In progress, its Next Action as the handoff says, its evidence pinned at `6b8c958`.

## 9. Where each item goes

| Item | Goes to |
|---|---|
| C1.1 | The brief's D3 |
| C1.2 | The brief's acceptance check 13; C1's identity case and its reversal |
| C1.3 | The data model's "Email change and recovery" |
| C1.4 | The brief's D10; C1's workflow step, check and reversal |
| C1.5 | The P11 plan, "From SV1" |
| C1.6 | The carried-items file, "Carried to SV4" |
| N1 to N5 | DM-45 1.1's deferred row closes |
| The pre-merge read (DM-45 14.1) | At the final head, with C1.4's workflow change |

Status: complete
