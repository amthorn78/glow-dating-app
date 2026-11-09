# DM-46 — SV1's brief, revision 2 (DM-45 1.1), and step 6's sentence

- **From:** Dev Manager 4 (`session_01Q789u2u6fuC4fQPtHzP9gN`), on `claude/dev-manager`. **To:** App Manager 10, relayed by Nathan (OD-25).
- **Read at:** `d461ea5b243852c096d8cb0abef2ff60d9b9d879` of `claude/magical-wozniak-yfmmx2`, the manager branch head when I read it. Since my last read (`d02ea32`), no application, contract, workflow, script or instruction file changed. The changes are records, the brief (SV1 revision 2, SHA-256 `3716b271…`) and one governing text, the manager workflow.
- **Written:** 9 November 2026, between 04:56 and 05:04 UTC.
- **Boundaries kept:**
  - I checked environment variable names only; none of the six names is present.
  - I called no provider, database, HDE, Railway or TypeSafe service, ran no application test, and wrote only this file.
  - Notion was read, not edited.
  - For allauth I reread the 65.21.1 wheel I had downloaded and checked for DM-45. I installed nothing and ran none of its code.

## 1. Verdicts

| Item | Verdict |
|---|---|
| 1. DM-45's conditions as applied | **Confirmed:** every blockquoted text is in the brief, every replaced text is gone, and the three inline texts are present |
| 2a. The opaque username | **Approved** as written |
| 2b. A replayed refresh token ends its session | **Approved with condition** N2: the trigger named by allauth's own checks, no action on a session already ended, and one refresh at a time for the client |
| 2c. D5's two sentences | **Approved with condition** N3: the session key's reach is wider than "during incomplete authentication". The stop rule's change is approved |
| 2d to 2f | **Approved.** One change the consultation does not list, the lifetimes heading "(approved for SV1; DM-45 item 3)", is accurate |
| **New: allauth's session list** | **Condition** N1. DM-45 missed it: installing `usersessions` also serves a session list whose `DELETE` ends sessions at allauth's layer only |
| 3. Step 6's sentence | **Confirmed** word for word, at the end of "Fix or carry, by rule" |
| 4. The carries as recorded | **Approved, with two corrections:** N4 (P08's entry treats the session key as personal data to export) and N5 (GP-36's sources cell lacks the page its new sentence cites). N2 and N3 add one entry for P11 |
| Notion | **Matches** `d461ea5`. One records nit: the Branches bullet, like the handoff, still lists `claude/dev-manager` at `65618c1` |

**How to apply:** N1 to N5 change text in given words. They may be narrowed, never widened. Applied as written, they need no read from me before the prompt goes to Nathan; my next consultation confirms them, and DM-45 1.1's deferred row can then close. Any other change to these parts comes back to me first. The prompt itself needs no read (DM-45 item 14).

## 2. Item 1 — DM-45's conditions, as applied

By script, against the brief at `d461ea5`, with the same normalization as for DM-44:
- **Blockquoted fragments found:**

  | Condition | Found | Condition | Found |
  |---|---|---|---|
  | 2.1 | 4 of 4 | 6.5 (two quotes) | 5 and 3 |
  | 2.2 | 6 | 7.1 | 6 |
  | 3.1 | 10 | 7.2 | 4 |
  | 4.1 | 9 | 7.3 | 3 |
  | 4.2 | 6 | 8.1 | 5 |
  | 6.1 | 9 | 9.1 | 7 |
  | 6.2 | 4 | 9.2 | 6 |
  | 6.3 | 10 | 11.1 | 2 |
  | 6.4 | 5 | 12.1 | 8 |
  | | | 13.1 | 10 |
  | | | 14.1 (two quotes) | 8 and 3 |

- **Inline texts found:** 3.1's sentence for acceptance check 6, 6.5's words for check 9, and 11.1's timeout sentence.
- **Replaced texts gone:** all seventeen.
  - D2: the session-token comparison, "at least that", the lifetime question, and the old signing-key text;
  - D4: the old sign-up transaction text, both its sentences;
  - D5: "Recommended: allauth's `usersessions` app, if …";
  - D6: "adds none of its own", "the current one stays";
  - D13: "an ordinary refresh";
  - D8: "The session lists the events …";
  - acceptance checks 3, 5, 8 and 9: their old wording;
  - D10's masked secrets; the old Dev Manager line.
- **Placement:** each text sits where DM-45 put it. The lifetimes bullets sit one level deeper, as the brief nests them.
- **One nit, from my own words** (optional): 14.1's insertion leaves the review plan's focus list with "and" twice: "…; G-14's absence of a review path; and the proof's secret handling; the session key held …; and the actor class's use …". Dropping the first "and" reads cleanly.

## 3. Item 2 — what App Manager 10 changed beyond my words

### 2a. The opaque username: approved

It says what item 5's option meant. `auth.User.username` stays unique and required, and a random value fills it, so nothing personal is copied there.

### 2b. A replayed refresh token ends its session

**The words are close, but "a validly signed refresh token of a live session" names only part of what allauth checks.** In 65.21.1:
- `validate_refresh_token` first runs `decode_token(token, "refresh")`. That checks the signature, the token's own `exp`, its `token_use` and its claims.
- It then finds the session from `sid`.
- Only then does it compare the `jti` with the session's held set, and check the session's user (`validate_token_user`, which refuses an inactive user and a stale password hash).

The trigger must run each of those checks in allauth's own order.

**The order matters for safety.** A subclass that read `sid` before the signature was checked would let anyone holding an old access token craft an unsigned "refresh token" with that `sid` and a random `jti`, and so sign the member out. And a token of the wrong type, an access token, must never trigger it.

**A replay whose session has already ended: no further action.**
- **Nothing remains to end:** allauth's session is gone.
- **Glow's layer:** the `AccountSession` has already been ended by D6's rules (logout, password change or reset, suspension, deletion, and with N1 the session list), or expired at the aligned instant (3.1), where `expire_session` marks it when found.
- **Reaching further would harm:** ending the account's other sessions on such a replay would let anyone holding an old token sign the member out of every device.

**What the client must do.** Two refreshes with the same token are a replay, and so is a retry after a lost response, so the app must send one refresh at a time. A lost response costs the member nothing new: without the subclass the old token is already refused, so the member must sign in again either way. Concurrent refreshes are the only case where the subclass changes the outcome, and serialized refreshes avoid it.

- **N2.** Replace D2's "**A replayed refresh token ends its session**" bullet with:

  > - **A replayed refresh token ends its session** (DM-45 item 14's recommendation, taken). In 65.21.1 a replayed rotated refresh token is refused, but its session lives on, so a stolen current refresh token used first keeps a session the member's next refresh cannot end. A subclass of allauth's JWT strategy ends the session at both layers (D6) when a refresh token passes allauth's own checks, in allauth's order (its signature, its expiry and its type, then the session it names exists, then that session's user is the token's), but carries a `jti` the session no longer holds. It adds no cryptography: allauth's own functions decide each check, and the subclass only adds the response to a replay. A refresh token whose session no longer exists is refused as allauth refuses it, and nothing more is done: D6 has already ended that session's `AccountSession`, or `expire_session` marks it when found. The app sends one refresh at a time: two refreshes with the same token, or a retry after a lost response, are a replay (carried to P11's client wiring).

  Replace acceptance check 5 with:

  > 5. **Refresh:** rotation issues a new pair. The old refresh token, replayed, is refused and ends its session at both layers, so the current pair stops too. A refresh token of a session that has already ended is refused, and nothing else changes. A token with a bad signature, a past expiry or the wrong type is refused without ending any session.

**Tried, against the code:**
- **Ends the session:** a rotated token replayed on a live session of the same user.
- **Refused, nothing ended:** a forged signature, even with a real `sid`; an expired token; an access token sent to refresh; a token of a deleted session.
- **Refused, nothing ended, already signed out by Glow:** a token of a live session after a password change (the user check fails) and one of a suspended user.
- **The held token:** rotates as usual.
- **Two refreshes at once:** one rotates and the other ends the session, hence the client rule.

### 2c. D5's two sentences

The stop rule's "through a Dev Manager consultation" is **approved**; it is the general form.

**The first sentence needs one correction (N3).** It credits DM-45 with reading that the `app` client sends the session key "as its `X-Session-Token` during incomplete authentication". What 65.21.1 shows is wider:
- headless's `expose_session_token` returns the session key to the `app` client as `meta.session_token` at sign-in, and again whenever the key changes (when the session changed and the request did not already carry that key);
- `JWTTokenStrategy.get_session_token` reads `X-Session-Token` before the token's `sid`;
- `authentication_context` uses that key to load the session for allauth's own endpoints, for the session's whole life.

So whoever holds the key can use allauth's own endpoints as the member: for example, listing and ending sessions (N1).

- **N3.** Replace D5's second and third sentences ("And the session key is a credential: … (DM-45 read this in 65.21.1's source). The session confirms it from the installed source.") with:

  > And the session key is a credential: in 65.21.1, headless returns it to the `app` client as `meta.session_token` at sign-in, and again whenever the key changes, and allauth's own endpoints accept it as `X-Session-Token`, ahead of the token's `sid`, for the session's whole life (DM-45 and DM-46 read this in the source). The session confirms it from the installed source, and the threat model records it. The app keeps it only in the platform's secure storage, or not at all once the token pair arrives (carried to P11's client wiring).

### 2d to 2f: approved

- **2d,** the Why section's G-13 line, is accurate.
- **2e,** "(carried to P11)" and "(carried to P08)", matches the carries as recorded.
- **2f,** the status line and Sessions, is accurate. The DM-45 entry's "seven gaps (G1 to G7)" matches my report's section 3.

## 4. A new finding: allauth's session list (N1)

**What DM-45 missed.** Installing `allauth.usersessions` for D5's reference does more than create rows:
- **The route:** headless's URL configuration adds `app/v1/auth/sessions` whenever `USERSESSIONS_ENABLED` is true (`headless/urls.py`). Its `SessionsView` lists the member's sessions (`GET`) and ends chosen ones (`DELETE`).
- **What ending does:** `DELETE` calls `usersessions`' flow `end_sessions`, which calls the adapter's `end_sessions`, which calls each row's `end()`. That deletes the Django session only. If the current session is among them, allauth logs out.
- **What Glow sees: nothing.** It never runs `sign_out`. The ended device's `AccountSession` stays `valid`, and no `session_revoked` event is written. A device whose session the member ended from another device then stays current to everything that reads Glow's sessions. That includes P06.3's notification composer, for which a registration stays active while its session is current. So pushes would go on to the ended device.

**The fix is allauth's own hook** (`USERSESSIONS_ADAPTER`, `DefaultUserSessionsAdapter.end_sessions`). Members also keep a useful control: signing out another device.

- **N1.** Add to D6, after the "**Logout:**" bullet:

  > - **Ending a session from allauth's session list.** With `allauth.usersessions` installed (D5), headless also serves the member's session list (`app/v1/auth/sessions`), whose `DELETE` ends chosen sessions through `usersessions`' adapter (`end_sessions`), at allauth's layer only. So Glow's `USERSESSIONS_ADAPTER` ends each chosen session at both layers: `sign_out` for the `AccountSession` whose `auth_session_ref` is that row's primary key, if there is one, then the row's own `end()` (D6's rules). A test and its reversal show that ending another device's session from the list revokes its `AccountSession` and writes `session_revoked`.

  Replace acceptance check 8 with:

  > 8. **Two devices:** logging out one leaves the other valid. Ending one from allauth's session list revokes its `AccountSession`, with its `session_revoked` event, and leaves the other valid. A password change ends both, and the member signs in again. A password reset ends both.

  Add to the review plan's security focus, after "the two link-building mails (D3)": "; allauth's session list, whose ending goes through Glow's `USERSESSIONS_ADAPTER` (D6)".

**Tried:**
- **Another device's session:** both layers end, and the event is written.
- **The current session chosen:** allauth's logout runs too. Glow's session is already revoked, so a second `sign_out` changes nothing.
- **A session whose `AccountSession` is already revoked:** `sign_out` is "no change", and `end()` runs.
- **A row with no `AccountSession`** (a sign-in that failed closed, 6.3): only `end()` runs, hence "if there is one".
- **A row of another account:** it cannot be chosen. `SelectSessionsInput` limits its choices to `UserSession.objects.filter(user=…)` for the request's user.

## 5. Item 3 — step 6's sentence

**Confirmed.** At `d461ea5`, `docs/planning/manager-workflow.md`'s "Fix or carry, by rule" bullet ends: "The exact-head review reads the fix against the rule." It then has my two sentences word for word, then "(DM-45, section 16.)". The word diff since `d02ea32` is that addition only. It sits after the sentence that lists the consultation triggers, so it reads as the exception to them, as meant. DM-45 section 16's deferred row can close.

## 6. Item 4 — the carries as recorded

- **The P11 plan, "From SV1":** each entry says what I meant (the lifetime to Nathan, the client-IP settings, the shared cache, the keys, the specification and the wiring). N2 and N3 add one entry. Add after the keys entry:

  > - **The client's token handling** (DM-46): the app sends one refresh at a time, since a second refresh with the same token, or a retry after a lost response, is a replay that ends the session (the SV1 brief's D2); and it keeps headless's `meta.session_token`, the session key, only in the platform's secure storage, or not at all once the token pair arrives, since allauth's own endpoints accept it for the session's whole life (D5).

- **"Carried to P07":** says what 9.1 meant, F01's `suspend` rule included.
- **"Carried to P08": one correction (N4).** The entry says the rows "hold the session key. They are personal data; P08 sets their retention and their place in export and deletion." The session key is a credential, not data to export. An export that carried it would hand out a live session.
  - **N4.** Replace the entry with:

    > - **From SV1** (the SV1 brief's D5): allauth's `UserSession` rows record each sign-in's IP address and user agent, which are personal data: P08 sets their retention and their place in export and deletion. The rows also hold the session key, a credential: it is never exported, and deletion removes it with its session.

- **"Carried to P09":** says what 13.1 meant: both parts, a maintained library, no custom token cryptography, raw tokens out of backup, and the key deleted on sign-out.
- **"Carried to SV1":** the G-13 entry points to D13 and P09.2, as meant.
- **The matrix:** G-13's row and GP-36's requirement and owner cells say what 13.1 meant. The header's "Owner changes" note is the right label, since GP-36's Play policy page was not re-read.
  - **The gap (N5):** GP-36's new sentence cites "Android's implementation guide, read 9 November 2026", but the row's sources cell still lists only the overview page "read 2026-11-01". Section 10 keeps each reading traceable to its record.
  - **N5.** In GP-36's sources cell, after "[Restore Credentials](https://developer.android.com/identity/sign-in/restore-credentials); read 2026-11-01", add:

    > ; [Implement Restore Credentials](https://developer.android.com/identity/sign-in/restore-credentials-implementation), read 2026-11-09 (the DM-45 report, sections 1 and 15)

- **The refresh-replay gap:** rightly not carried, since 2b takes the recommendation.

## 7. Notion (read-only, at about 05:00 UTC, against `d461ea5`)

What I read: the parts named here, not the whole of either large page.
- **Implementation Control** (as of 04:41:13 UTC):
  - **The status section** names `d461ea5` and its message, DM-45's findings, and revision 2 with DM-46.
  - **The procedure summary's stamp** has moved to `d461ea5` (AM10-05).
  - **The records nit:** the Branches bullet lists `claude/dev-manager` at `65618c1`, from the 03:03 UTC listing, as the handoff does. Both records agree, but the branch has been at `0dcd122` since DM-45's push, and that commit is merged at `086c67c`. The next listing corrects both.
- **The Dev Manager page** (as of 04:40:20 UTC): DM-45's row, with its disposition, and DM-46's row ("Pending") match the review log. The page now has DM-45's row, so DM-45's mismatch is closed.
- **The Work Register:** SV1 is In progress, its evidence pinned at `d461ea5`, and its Next Action as the handoff says.

## 8. Where each item goes

| Item | Goes to |
|---|---|
| N1 | The brief's D6, acceptance check 8 and the review plan's focus |
| N2 | The brief's D2 and acceptance check 5; the P11 plan's "From SV1" (the client entry) |
| N3 | The brief's D5; the same P11 entry |
| N4 | The carried-items file, "Carried to P08" |
| N5 | The matrix, GP-36's sources cell |
| The "and" nit (optional) | The brief's review plan |
| DM-45 1.1 and DM-45 section 16 | The review log's deferred rows. Section 16's row closes now; 1.1's row closes when my next consultation confirms N1 to N5 as applied |
| The Branches nit | The manager's next listing, in the handoff and Notion |

Status: complete
