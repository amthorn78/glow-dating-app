# SV1 — The identity slice: maintained sign-in and the mail adapter, proven on disposable PostgreSQL

- **Work ID:** SV1 (OD-49, N1 (a); PF01 §8, "Server slices"; the F01 flow).
- **Status: brief, revision 5, 9 November 2026; implemented at `269ac3b` and corrected by C1 at code head `bda299e`, both verified; the exact-head review asked for changes; correction C2's prompt is with Nathan ("Sessions").** [DM-48](../continuity/dev-manager/reviews/2026-11-09-dm-48-sv1-review-c2.md) (answered at `c6bce37`, a read of `38142b3`) approved F-2's option (a) and C2's scope with C2.1 to C2.8 in given words. Revision 5 applies C2.1 and C2.2 in D3, C2.3 as acceptance check 11, C2.6 in D10 and C2.8's first replacement in D2, with the rest in "Correction C2". It confirmed C1.1 to C1.6 as applied. [DM-47](../continuity/dev-manager/reviews/2026-11-09-dm-47-sv1-email-change.md) (answered at `1516629`, a read of `6b8c958`) approved C1 with C1.1 to C1.6 in given words; revision 4 applies C1.1 in D3, C1.2 as acceptance check 13, C1.3 in "Correction C1" and C1.4 in D10, with C1.5 in the P11 plan and C1.6 in the carried-items file. It confirmed N1 to N5 as applied. [DM-46](../continuity/dev-manager/reviews/2026-11-09-dm-46-sv1-brief-revision-2.md) (answered at `778ee29`, a read of `d461ea5`) confirmed revision 2 and added N1 to N5 in given words; revision 3 applies them as written (N1 in D6, acceptance check 8 and the review plan; N2 in D2 and acceptance check 5; N3 in D5), with N4 and N5 in the carried-items file and the matrix, and DM-46's optional "and" dropped. Applied as written, they need no read before the prompt (DM-46 section 1). [DM-45](../continuity/dev-manager/reviews/2026-11-09-dm-45-sv1-brief.md) (answered at `0dcd122`, a read of `d02ea32`) approved revision 1 with conditions in given words. Revision 2 applies them as written: 2.1, 2.2 and 3.1 in D2; 4.1 and 4.2 in D5; 6.1 to 6.5 in D4 and D6; 7.1 to 7.3 in D3; 8.1 in D8; 9.1 in D7; 9.2 in D14; 11.1 in D10; 12.1 in D12; 13.1 in D13; 14.1 in the review plan; with the acceptance checks 3, 6, 8 and 9 and the CI paragraph as they say. It also takes DM-45's optional opaque username (D4) and its recommendation to end a session on a replayed refresh token (D2).
- **Owner:** Nathan Amthor, by the order he resumed on 26 October (OD-49): the server slices SV1 to SV4 after P06.3, before P10. **Manager:** App Manager 10. **Session:** one implementation session, started by Nathan, in `Glow App - No Stream` (no Stream call, no provider, no credential).
- **Starting point:** `main` at `da92f1f` (PR41, P06.3), with the manager branch's Markdown records after it. The prompt names the exact commit.
- **Evidence home:** `docs/testing/evidence/<date>-sv1-identity.md`, written by the session.

## Why

- **PF01 §8, "Server slices":** *"Before P10, the production HTTP API, maintained authentication (django-allauth headless with the mail adapter) and the ORM persistence adapters of each domain are built as four slices: SV1, identity (sign-in and the mail adapter) … Each is proven on a disposable PostgreSQL in CI under P06.DB's rules (no shared or production database, CI-generated credentials, the runtime guards kept). The runtime stays sealed until P11 wires it."*
- **PF01 §7, "Identity and onboarding":** *"Start with verified email and supported recovery. Add social login only with safe linking and platform-policy review. Use platform secure storage for native secrets, short-lived access credentials and server-side revocation of refresh/session state. Logout, password change, lost-device recovery, account suspension and deletion revoke the appropriate sessions. Test enumeration resistance, token replay, expired links, wrong-account linking and deep-link interception. Fixture sign-in is development-only and is never production authentication evidence."*
- **PF01 §4 (the selected architecture), its Authentication row:** *"django-allauth headless with supported native token strategy"*; *"Configure verification/recovery/provider linking and revocation; do not create custom password or token cryptography"*.
- **The F01 flow** (`flows-v1.json`; `production-contracts.md`, F01): the request contract is allauth's headless API, the response is `AccountAccess` (`account_id`, `version`, `state`, `session_state`); acceptance: *"Expired/replayed credential rejected by maintained auth; fixture contract rejects ordinary user verification and revoked-session access."*
- **The planned mapping** (`production-contracts.md`, "Maintained authentication reference and app mapping"): *"the maintained JWT strategy with stateful validation enabled and refresh rotation enabled … Pin the actual allauth release and generated configured specification during auth implementation before activating an adapter … App account suspension/deletion additionally revokes access regardless of remaining token lifetime."*
- **The data model** (`data-model.md`, "Maintained authentication mapping"): unique email identities (`ACCOUNT_UNIQUE_EMAIL`), verified email onboarding, email login through allauth; and *"`AccountSession.auth_session_ref` is an adapter-provided **non-secret** library session identifier, not a session cookie/token/hash invented by Glow … If the provider has no such supported identifier, amend this mapping before integration."*
- **The P11 plan:** DB09, *"authentication, verification, recovery, linking and session lifecycle"*. P06.DB proved DB09 only partly, with `django.contrib.auth` and a stand-in session reference, and left *"allauth's adoption … with the item that"* builds sign-in (the P06.DB brief, D2).
- **Carried to SV1** (the carried-items file):
  - a written threat model in SV1's exact-head review (DM-31 item 3), since Codex's security reviews are no longer available (OD-41);
  - the brief goes to the Dev Manager: a significant new dependency, and sign-in is a security boundary;
  - from P09.3a's matrix (DM-37 2.1, 2.2, 3.2), room for these, building none of the owning briefs' work:
    - **G-01**, the account's age state. Nathan answered (OD-55): a self-entered birth date plus the stores' age signals where the law requires them; SV1 holds the age state behind a seam so a stronger check can be added;
    - **G-13**, Google's Restore Credentials for apps with sign-in, from April 2027 (GP-36), *"SV1's brief scope (identity), or P09.2"*. D13 places both its parts in P09.2 (DM-45 13.1);
    - **G-14**, any review sign-in path inside SV1's threat model; P09 owns the reviewer account;
    - **G-04**, Vermont's account-change notice (UST-16: *"within 24 hours after discovering an account change to a Vermont member's account"*, for a change to the password, username, email or contact details).

## Outcome

SV1 builds the server's identity on maintained code, proves it on a disposable PostgreSQL in CI, and keeps it sealed from the served runtime.

1. **Maintained sign-in, configured.** django-allauth headless, `app` client only, with the JWT token strategy (D2), installed and configured in a new Django app, `services/api/glow_identity`:
   - sign-up with email and password, mandatory email verification by code, password reset by code, password change and email change (D3);
   - access and refresh tokens, with refresh rotation and stateful validation, and a replayed refresh token ending its session (D2);
   - logout, which ends the session at once;
   - enumeration resistance and allauth's rate limits on (D3).
2. **The app account, bound to the maintained user** (D4):
   - sign-up creates the `AppAccount` (`unverified`) in the same transaction as the auth user;
   - verification moves it to `active` (F01's `verified`, role `auth`);
   - each sign-in records an `AccountSession` bound to the account's `session_epoch`, with a supported, non-secret session reference (D5).
3. **Revocation, at both layers** (D6). Logout, password change, password reset, suspension and deletion each revoke the right sessions in `AccountSession`, through `glow_chat`'s reviewed operations, and in allauth's persistence. An account that is not `active`, or a session that is not `valid` at the current epoch, is refused whatever the token's remaining life.
4. **The actor, from maintained authentication** (D7): one DRF authentication class that every later slice uses. It takes the access token through allauth's `JWTTokenAuthentication`, then checks the `AppAccount` and the `AccountSession` under the rules in 3, and yields Glow's actor (account and session). It is the only place SV2 to SV4 get an actor.
5. **One Glow route:** the member's own `AccountAccess` (F01's response), validated against the contract's schema. No other Glow route.
6. **The mail adapter** (D8): Glow's account adapter for allauth's messages, sending through Django's email backend. A Glow fixture backend records each message and refuses any network send. The account-change notices are on for every member (G-04, D8).
7. **The age state, behind a seam** (G-01; D9): the account's recorded age state and the method that set it, written only through a port. SV1 records `unknown` at sign-up and builds no check.
8. **The proof** (D10): the identity cases (the acceptance checks below) run on a disposable PostgreSQL in CI, through the HTTP endpoints with Django's test client, under P06.DB's rules.
9. **Sealed** (D11): the served runtime (`glow_api`'s settings, URL configuration and WSGI application) imports none of `glow_identity`, allauth, `jwt` or `cryptography`, and its database backend stays Django's dummy one.
10. **The records:**
    - the data model's "Maintained authentication mapping" and the contract's "Maintained authentication reference and app mapping", rewritten as built, with the pinned release;
    - the P11 plan's DB09, with SV1's partial evidence;
    - the evidence record, with the threat model's inputs: every endpoint, every token and code, and every revocation path, each with its test.

## Design

- **D1 — Scope and seal.** No mail provider, no deployed URL, no real member, no credential beyond what CI generates for one run (D10). The runtime stays sealed until P11 (PF01 §8), as P06.2 sealed `glow_chat` (`test_chat_sealed_runtime.py`). P11 wires the routes, the settings and the mail provider. The mobile app is unchanged: its fixture sign-in stays until P11 wires the client (PF01 §7).
- **D2 — The token strategy: JWT, stateful, rotating** (the contract's planned mapping).
  - `HEADLESS_TOKEN_STRATEGY` names allauth's JWT strategy (`allauth.headless.tokens.strategies.jwt.JWTTokenStrategy`, or a subclass if the installed release requires one); `HEADLESS_CLIENTS = ("app",)`; `HEADLESS_ONLY = True`.
  - `HEADLESS_JWT_STATEFUL_VALIDATION_ENABLED = True`: each access token is checked against the session it was issued in, so logout and a password change end it at once (allauth's JWT page, read 9 November 2026).
  - `HEADLESS_JWT_ROTATE_REFRESH_TOKEN = True` (allauth's default): a refresh issues a new refresh token and invalidates the old one.
  - **A replayed refresh token ends its session** (DM-45 item 14's recommendation, taken). In 65.21.1 a replayed rotated refresh token is refused, but its session lives on, so a stolen current refresh token used first keeps a session the member's next refresh cannot end. A subclass of allauth's JWT strategy ends the session at both layers (D6) when a refresh token passes allauth's own checks, in this order (its signature, its expiry and its type, then the session it names exists, then that session's user is the token's), but carries a `jti` the session no longer holds. It adds no cryptography: allauth's own functions decide each check, and the subclass only adds the response to a replay. A refresh token whose session no longer exists is refused as allauth refuses it, and nothing more is done: D6 has already ended that session's `AccountSession`, or `expire_session` marks it when found. The app sends one refresh at a time: two refreshes with the same token, or a retry after a lost response, are a replay (carried to P11's client wiring).
  - **Lifetimes (approved for SV1; DM-45 item 3):**
    - access, 300 seconds, allauth's default and PF01's "short-lived";
    - refresh, 30 days. allauth's default is one day;
    - the `AccountSession`'s lifetime is 30 days from sign-in, and at sign-in the Django session's expiry is set to the same instant (`set_expiry` with that `AccountSession`'s `expires_at`), so allauth's own endpoints, refresh included, stop with Glow's session. Django keeps an expiry set as a date-time across later saves, so allauth's `session.save()` on each refresh does not extend it;
    - **What a member sees:** `AccountSession.expires_at` is fixed when the session opens (`glow_chat`'s `open_session` takes a lifetime; no operation extends it). So 30 days is an absolute limit: a member signs in again every 30 days, however active. A sliding window would need a new reviewed operation in the lock protocol (D6). The limit is SV1's default; whether members get a sliding window or another limit is put to Nathan before P11 serves sign-in (carried to P11).
  - **The keys.** The signing key (`HEADLESS_JWT_PRIVATE_KEY`, RS256, allauth's default algorithm) is an RSA key of at least 2048 bits, generated for each test process and each CI run, never committed, printed or logged, as P06.DB generates its database password. In CI it is written to a file in the job's protected temporary directory and read from that path, never put in an environment variable: the `::add-mask::` command takes one line, so a multi-line key would leave lines unmasked. The identity settings' `SECRET_KEY` is generated the same way, not the proof's committed placeholder, because allauth encrypts the session key into every token's `sid` with a key derived from `SECRET_KEY`, and Django signs each session's password hash with it. P11 supplies both as secret references. SV1 adds no key to any environment template.
  - **Session tokens instead** (allauth's default strategy) would also meet PF01. With stateful validation, both strategies look up the session on every request, so neither is cheaper. The JWT strategy is chosen because it is the contract's planned mapping: short-lived access tokens, and refresh tokens that rotate and die with their session.
- **D3 — Sign-up, verification and recovery by code, not by link.**
  - `ACCOUNT_LOGIN_METHODS = {"email"}`; `ACCOUNT_SIGNUP_FIELDS` with email and password only; `ACCOUNT_UNIQUE_EMAIL = True` (the data model's intent).
  - `ACCOUNT_EMAIL_VERIFICATION = "mandatory"` with `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True`; `ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED = True`. Codes keep the native app off deep links, which PF01 asks to test for interception. No `HEADLESS_FRONTEND_URLS` are set, so no message carries a link back into the app. With `HEADLESS_ONLY`, allauth then raises `ImproperlyConfigured` wherever it builds a link (`default_get_frontend_url`, 65.21.1), and two of its mails build one: the unknown-account mail and the account-already-exists mail. So `ACCOUNT_EMAIL_UNKNOWN_ACCOUNTS = False`: Glow mails no address that has no account, since a mail from a dating app reaches whoever reads that inbox. And Glow's account adapter replaces `send_account_already_exists_mail` with Glow's own message, with no link. Without both, a sign-up with a taken address and a reset for an unknown address would fail with a server error where their counterparts succeed.
  - **Email change:** one address per account; the new address is verified by code before it replaces the old (`ACCOUNT_CHANGE_EMAIL = True`). The change also needs a reauthentication by password within the last 300 seconds, in the same session (`ACCOUNT_REAUTHENTICATION_REQUIRED = True`, with allauth's default `ACCOUNT_REAUTHENTICATION_TIMEOUT`); a sign-in does not count as one. Without it, a holder of a live access token, refresh token or session key could move the address and then reset the password from it. In 65.21.1, `POST auth/reauthenticate` records the reauthentication in the Django session only: it cycles no key, issues no token pair and runs none of Glow's sign-in hooks (it calls neither `login` nor `post_login`), so D5's reference holds. A wrong password there consumes the same `login_failed` limit as a failed sign-in (the adapter's `authenticate`), so `auth/reauthenticate` adds no guesses to the sign-in form's budget; the password change has its own limit (the rate-limit bullet below). The same setting guards removing an address and marking one primary.
  - `ACCOUNT_PREVENT_ENUMERATION = True` (allauth's default; not `"strict"`, which can create several accounts sharing an email).
  - **The code limits** are allauth's defaults at 65.21.1: three attempts for each code, 15 minutes for a verification code and 3 minutes for a reset code. The evidence names the installed release's values.
  - allauth's rate limits keep their defaults (`ACCOUNT_RATE_LIMITS`), except `change_password`, which is `5/300s/user`. At `account/password/change` a wrong current password is checked by `check_password` alone and consumes no `login_failed` (65.21.1, `headless/account/inputs.py:180-184`), so allauth's default `5/m/user` would give a holder of a live session key or access token five times the sign-in form's budget there. Every signed-in request there counts, whatever its outcome, a member's own included. So that holder gets 5 guesses per 300 seconds at the password change, besides the 5 the sign-in form and `auth/reauthenticate` share through `login_failed`: 10 in all, twice the sign-in form's. The threat model records that remainder. The limits use Django's cache: a local-memory cache in the proof; P11 needs a shared cache for more than one worker (carried to P11).
  - **Off in SV1:** login by code, multi-factor authentication, social login (PF01: only with safe linking and platform-policy review; with no social login, Apple's Sign in with Apple rule does not bind), the browser client and the served specification (`HEADLESS_SERVE_SPECIFICATION`).
  - **Passwords:** Django's password hashers and its four validators, with a minimum length of 10. No new hasher dependency.
- **D4 — The app account.**
  - `AppAccount` keeps its one-to-one, protected link to `settings.AUTH_USER_MODEL`, which stays `auth.User` (the static registry and the P06.DB proof, which also drives `glow_chat`, use it). allauth's `EmailAddress` holds the normalized, unique, verified email. A custom user model would be Django's general advice for a new project; here the app identity already lives in `AppAccount`, and changing the user model would ripple into the static registry, the proof and `glow_chat`'s tests (DM-45 item 5).
  - **The username is opaque** (DM-45 item 5's option, taken). Glow's account adapter sets `auth.User.username` to a random opaque value, so allauth's `populate_username` does not copy the email's local part into a column email sign-in never uses.
  - Sign-up creates the auth user, its `AppAccount` (`unverified`) and its `unknown` age state in one transaction, in Glow's account adapter's `save_user`, so no auth user ever exists without its account. allauth 65.21.1 opens no transaction around headless sign-up, so the steps allauth takes after `save_user` are outside it; a failure there leaves an `unverified` account that cannot sign in, which the evidence names. No `glow_chat` operation runs inside that transaction (D6).
  - Verification by allauth is the only path from `unverified` to `active` (F01's `verified`, role `auth`). A verified email alone establishes nothing else: not adulthood, consent, profile or eligibility (the contract's mapping).
  - **Sign-in opens the `AccountSession` through `glow_chat`'s `open_session`** (D6): the reviewed operation that locks the account, refuses one that is not `active`, and records the session at the current epoch with its reference and lifetime. With mandatory verification, allauth completes no sign-in for an unverified account, so no `AccountSession` exists before verification.
- **D5 — The session reference: a supported, non-secret identifier.** The data model forbids a Glow hash of the session key. And the session key is a credential: in 65.21.1, headless returns it to the `app` client as `meta.session_token` at sign-in, and again whenever the key changes, and allauth's own endpoints accept it as `X-Session-Token`, ahead of the token's `sid`, for the session's whole life (DM-45 and DM-46 read this in the source). The session confirms it from the installed source, and the threat model records it. The app keeps it only in the platform's secure storage, or not at all once the token pair arrives (carried to P11's client wiring).
  - **The reference: `UserSession`'s primary key** (`allauth.usersessions`). In 65.21.1, allauth creates a `UserSession` row for every sign-in, from a client of any kind (its `user_logged_in` receiver), keyed by the session key, with a `BigAutoField` primary key that is not derived from the key; and `UserSession.end()` deletes the Django session. `AccountSession.auth_session_ref` holds that primary key. The actor class takes the session from the validated token's own `sid` (the payload `JWTTokenAuthentication` returns), decrypted with allauth's own function at the pinned release, held in memory only and never logged; never from an `X-Session-Token` header, which allauth's `get_session_token` would prefer. The `sid` itself is not a reference: it is the session key, encrypted with a key derived from `SECRET_KEY` and a new random initialization vector for each token. The session confirms these facts from the installed source.
  - **The reference holds only while the session key does.** Django's `update_session_auth_hash` makes a new key (`cycle_key`) when a password changes and the session is kept, and allauth then gives that device no new token pair. So `ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True`: a password change ends every session, the current one included, and the member signs in again (D6). No other allauth flow in 65.21.1 changes a signed-in session's key; reauthentication does not.
  - **What it stores:** `UserSession` records the client's IP address and user agent. Those are personal data: SV1 records them as such in the data model, with `USERSESSIONS_TRACK_ACTIVITY` off (no last-seen updates), and their retention goes to P08 (carried to P08).
  - **If the installed release cannot do this,** the session stops and reports. The data model's mapping is then amended through a Dev Manager consultation before any code relies on another reference.
- **D6 — Revocation: one lock protocol, two layers.**
  - **One lock protocol.** P06.2's reviewed adapter, `glow_chat/contact.py`'s `OrmContactPersistence`, already owns every `AccountSession` and account-state transition: `open_session`, `sign_out`, `expire_session`, `suspend` and `delete`. Each runs under the lock protocol that P06.DB and P06.2 proved against sends (DB06), and writes its outbox events (`session_revoked`, `session_expired`, `access_revoked`, `session_epoch_bumped`; the data model's event table). SV1 calls these operations, and adds the one transition `glow_chat` does not have: F01's `verified` (`unverified` to `active`, role `auth`), in `glow_identity`, under the same rules: its own transaction; the account row locked `FOR UPDATE` before anything else; a refusal unless the state is `unverified` (an account already `active` is no change); and `version` and `eligibility_version` bumped (the data model: every relevant account change bumps `eligibility_version`). It runs after allauth marks the address verified, and again at the next sign-in if it did not commit, so a verified address never leaves its account `unverified`. `glow_chat` is not changed (DM-45 item 6).
  - **Two layers.** After the operation commits, SV1 ends the matching allauth session or sessions, so their tokens fail at allauth's layer too, and allauth's own endpoints, which never consult Glow's `AccountSession`, refuse them. Between the two commits, the `AccountSession` is already refused by the actor class (D7), so Glow's refusal never waits on allauth's. Both steps are idempotent; if the second fails, the request answers with an error and a repeat completes it. Each rule is tested at both layers, and a reversal that fails the second step shows the error and the repeat.
  - **No outer transaction.** Each `glow_chat` operation runs as its own transaction, as P06.DB proved it. SV1 never calls one inside an open transaction: the revocation service refuses when `connection.in_atomic_block` is true, and the identity URL configuration does not set `ATOMIC_REQUESTS`. A test fails if a call runs inside `transaction.atomic()`.
  - **The sign-in fails closed.** `open_session` runs after allauth has created the sign-in's `UserSession`. If it does not apply (the account is not `active`, or any error), the allauth session ends in the same request, so no token from that sign-in is usable. A test and its reversal show it. The evidence names where the hook runs.
  - **Logout:** `sign_out` for this session, then allauth's logout.
  - **Ending a session from allauth's session list.** With `allauth.usersessions` installed (D5), headless also serves the member's session list (`app/v1/auth/sessions`), whose `DELETE` ends chosen sessions through `usersessions`' adapter (`end_sessions`), at allauth's layer only. So Glow's `USERSESSIONS_ADAPTER` ends each chosen session at both layers: `sign_out` for the `AccountSession` whose `auth_session_ref` is that row's primary key, if there is one, then the row's own `end()` (D6's rules). A test and its reversal show that ending another device's session from the list revokes its `AccountSession` and writes `session_revoked`.
  - **Password change:** `ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True` (D5): `sign_out` for every valid session of the account, the current one included, and allauth's logout of the current session; the password's new hash ends the others at allauth's layer. The member signs in again.
  - **Password reset by code** (lost-device recovery): `sign_out` for every valid session of the account.
  - **Suspension and `deletion_pending`:** `suspend` or `delete`, which bump the epoch, write `access_revoked` and `session_epoch_bumped`, and (for deletion) create the job and tombstone; then every allauth session of the user ends, and the auth user is made inactive, so allauth refuses a new sign-in. P07 owns lifting a suspension, which reactivates it.
  - **Expiry:** an access token past its life, a refresh token past its life or rotated away, and an `AccountSession` past `expires_at`, are each refused. `expire_session` marks an expired row when it is found.
  - **No route for suspension or deletion:** P07 (moderation) and P08 (deletion) own those requests. SV1's revocation service is what they will call; the proof calls it directly.
  - **F01's `recover` transition** (`revoked` → `valid`, role `auth`) is read as "the account gets a new valid session": SV1 never makes a revoked `AccountSession` row valid again. Recovery creates a new row (DM-45 item 9).
- **D7 — The actor.** `glow_identity`'s authentication class:
  - authenticates the access token with allauth's `JWTTokenAuthentication` (stateful validation on);
  - loads the `AppAccount` for the user, and the `AccountSession` for the token's session;
  - refuses, as `unauthenticated` (the contract's 401), unless the account is `active` and the session is `valid`, unexpired, and at the account's current epoch. The send already applies the same checks under its locks (`glow_chat`); the actor class applies them to every request;
  - so `AccountAccess` is served only to an active account with a valid session. An unverified member is still in allauth's verification flow, and a suspended or deleting member is refused at sign-in, so the other `AccountAccess` states are not served in SV1 (DM-45 item 9);
  - **A conflict carried to P07.** The interactions design keeps unmatch "reachable … for valid-session suspended or deletion-pending actors" (`interactions-fixtures.md`), and the mobile guard lets them open `/matches`. Neither `glow_chat`'s reviewed `open_session`, which refuses an account that is not `active`, nor SV1 gives such an actor a session. SV1 keeps that fail-closed default. Whether a suspended or deletion-pending member gets a restricted cleanup session is decided in P07's brief, and goes to Nathan if it changes what members can do. P07's moderation route also holds F01's `suspend` (from `active` only, role `moderator`, policy A05): `glow_chat`'s `suspend` checks only that the account is not being deleted.
  - never takes an actor, account or session from the request body or a header other than the token.
- **D8 — The mail adapter.**
  - **The seam is Django's email backend** (`EMAIL_BACKEND`), which allauth sends through. SV1 adds a Glow fixture backend that records each message in memory and has no network code. No SMTP or provider setting exists. P11 and M07 choose the provider (OD-50).
  - **Glow's account adapter** (`ACCOUNT_ADAPTER`) owns each message's subject and body: plain text, Glow's name only (ADR 0003, S15), no tracking, and no account detail beyond what the message needs. A code message holds the code and its expiry.
  - **The account-change notices** (`ACCOUNT_EMAIL_NOTIFICATIONS = True`) go to every member, not only Vermont's (G-04, UST-16): password change, password reset and email change, each tested. In 65.21.1 they are: password changed, password set, password reset, email changed (sent to the old address) and email deleted. UST-16's password and email changes are covered; Glow members have no username they use, and their only contact detail is the email. The session confirms the list from the installed source, and Glow's adapter also owns the account-already-exists message (D3). A change UST-16 names that allauth does not notify is reported, not built.
- **D9 — The age state** (G-01; OD-55's D3 (a)).
  - **Domain:** in `glow_domain/identity.py`, beside `AccountId`, a pure `AgeAssurance` type: the state (`unknown`, `self_declared_adult`, and room for the stores' signals), the method, when it was recorded and the policy version; and the port that reads and writes it.
  - **Persistence:** one new model in `glow_persistence`, one row per account, written only through the port, in a new migration after `0003`. No birth date is stored in it: P04's onboarding holds the self-entered date, and a later slice writes the state from it.
  - **In SV1:** sign-up records `unknown`. Nothing reads the state yet: SV3's eligibility reads it, and P09.2 adds the stores' signals (G-01's Work Register row).
- **D10 — The proof: P06.DB's job, a second disposable database.**
  - The identity suite lives in `proofs/postgres-ordering` beside the ordering suite, with its own settings module, which installs `glow_identity`, allauth's apps, `django.contrib.sessions` and the identity URL configuration. It reuses the proof's refusals: a clean environment, the run's marker, and `dbshell` refused.
  - In the Database proof checks job it runs after the ordering suite, on a second database created for it in the same disposable PostgreSQL 17.11, with its own marker and the proof's non-superuser role. It applies the reviewed migrations from zero (setup, not DB01 acceptance), then the cases.
  - **The run's secrets** (the database password, already; the JWT signing key and the identity settings' `SECRET_KEY`, new) are generated in the job, kept in files in its protected temporary directory and read from paths, never printed, and destroyed with it (D2).
  - **The results upload is checked first.** The job's secret check scans the suite's results JSON with the same values as its log, and the results artifact is uploaded only when that check has passed; after a failed check nothing is uploaded, and the job's log shows counts only, never a line of the suite's output.
  - **Why not a new job:** the marker, the refusals and the database's lifecycle already exist and were reviewed (P06.DB; DM-10 to DM-12). A new job would duplicate them. A new proof package is the alternative (DM-45 item 7).
- **D11 — The seal, checked.** A new test, in the style of `test_chat_sealed_runtime.py`, proves that the runtime's settings, URL configuration and WSGI application import none of `glow_identity`, `allauth`, `jwt` or `cryptography`, that the database backend is dummy, and that the connection refusal is unchanged. `glow_api/` is not changed.
- **D12 — The dependency** (DM-45 item 8).
  - `django-allauth[headless]` at the latest 65.x release when the session starts, checked on PyPI, with its release notes read for security entries. The latest on 9 November 2026 is 65.21.1 (30 October 2026). Its `headless` extra requires `pyjwt[crypto]` (2.x), which brings `cryptography`.
  - **Scope:** `services/api/requirements-dev.in` and its lock only, as P06.2 put `getstream` (DM-16 2.1); `requirements.in` and `requirements.lock` stay unchanged until P11 moves the pins. The proof's own lock takes the same pins.
  - Hash-locked; the dependency inventory and licences recorded; the dependency-pin tests updated.
  - **The transitive set is fixed:** the new packages are exactly `django-allauth`, `cryptography`, and what `cryptography` requires on CPython 3.12 (today `cffi`, which requires `pycparser`); `pyjwt` stays at the 2.15.0 the development lock already holds (allauth's `headless` extra asks for `pyjwt[crypto]>=2.0,<3`). Any other new package stops the session. The licences are recorded from each package's metadata at its pinned version (on 9 November: allauth MIT; PyJWT MIT; `cryptography` Apache-2.0 OR BSD-3-Clause; `cffi` MIT-0; `pycparser` BSD-3-Clause). allauth ships no type information (no `py.typed` in 65.21.1), so mypy's setting for it goes in `pyproject.toml`'s tool configuration.
- **D13 — G-13 and G-14.**
  - **G-13 (Restore Credentials):** not an ordinary refresh. Android's implementation guide (read 9 November 2026; last updated 2026-11-05) asks for "a WebAuthn relying party server similar to the server for passkeys": after sign-in the app registers a restore key with the server, and on a new device it sends the key's assertion, which the server verifies to "issue a new session token for the user". Android's pages also tell the app to keep "raw authentication tokens" out of its backup and to delete the restore key when the user signs out or the server invalidates the session. So G-13 has a server part, a WebAuthn relying party through a maintained library that gives the new device a new session, and a native part. SV1 builds neither. Both are carried, with GP-36's April 2027 date, to P09.2's brief, which names the server part's owner, and the matrix row GP-36 gets that owner. SV1's threat model records that a copied refresh token is a bearer credential until its session ends.
  - **G-14 (the reviewer account):** SV1 builds no review path. A verified reviewer account signs in with email and password, with no code, since login by code and multi-factor authentication are off (D3). The threat model records that no fixture adapter, test account or setting can reach real members (PF01 P12's validation: *"Verify that no fixture adapter or test account privileges can reach real users"*). P09 owns the account.
- **D14 — The contract is unchanged.** `packages/contracts` stays as it is. `AccountAccess` is served as the schema defines it. The production catalog's paths map stays empty until P11 serves the routes (`test_production_openapi_catalog_does_not_claim_implemented_routes`). The headless API is allauth's own specification, which the evidence record cites at the pinned release, and which is not vendored. **The configured specification is pinned** (the contract's mapping: "Pin the actual allauth release and generated configured specification during auth implementation before activating an adapter"). allauth 65.21.1 builds it only with its `headless-spec` extra (PyYAML), which SV1 does not add. So the session generates it once, in a scratch environment with that extra, from the pinned release and SV1's settings, and the evidence records its SHA-256 and its list of paths; nothing is vendored. If that cannot be done, the evidence says why, and P11 does it before it serves the routes.
- **D15 — Every test comes with its reversal,** in the style of the P06.2, P06.2-F and P06.3 records: a temporary edit that must make the test fail, run and undone, recorded with its failing output.

## Owned paths (the session)

- `services/api/glow_identity/**` (new): the app, its settings fragment, adapters, authentication class, the `AccountAccess` view, URL configuration, revocation service, mail fixture backend and the age-state adapter.
- `services/api/glow_domain/identity.py`: the age-state type and port only (D9).
- `services/api/glow_persistence/models.py` and one new migration (`0004_…`): the age-state model only, plus any change to `AccountSession` that DM-45 approves.
- `services/api/requirements-dev.in`, `requirements-dev.lock`, `dependency-inventory.json`, and `pyproject.toml`'s tool configuration only.
- `services/api/tests/`: new identity tests; the new sealed-runtime test; `test_dependency_pins.py` and `test_model_definitions.py` where the new pins and model require.
- `proofs/postgres-ordering/**`: the identity suite, its settings, its tests and its locks.
- `.github/workflows/foundation.yml`: the Database proof checks job's steps only.
- `docs/architecture/data-model.md` ("Maintained authentication mapping" and the identity rows), `docs/architecture/production-contracts.md` ("Maintained authentication reference and app mapping"), `docs/testing/p11-deferred-acceptance.md` (DB09's partial evidence), and the evidence record.

## Manager-owned

- This brief, the carried-items file, the handoff, the review log and Notion.
- **The CI policy's Database proof checks paragraph** (`docs/operations/ci-and-branch-policy.md`): governing Markdown. The manager updates it after the session, and the Dev Manager reads it at a named commit before the PR merges.

## Exclusions

- `services/api/glow_api/**` (settings, URLs, runtime, WSGI, configuration): the runtime stays sealed.
- `services/api/requirements.in` and `requirements.lock`: the runtime scope is unchanged.
- `services/api/glow_chat/**` (SV1 calls `OrmContactPersistence`'s session and account operations, unchanged; D6) and every other `glow_domain` module.
- `apps/**`, `packages/**`, `proofs/stream-chat/**`, `scripts/**`, other workflow jobs, the `Dockerfile` and `.dockerignore`, every environment template.
- Any mail provider, SMTP setting, deployed URL, real email address, social provider, MFA, login by code or browser client.

## Dependencies and inputs

- `main` at `da92f1f`; PF01 1.17 §4, §6, §7 and §8; F01 and `AccountAccess`; the data model; the contract's mapping; the P11 plan's DB09; the P06.DB brief and proof; `test_chat_sealed_runtime.py`; OD-49; OD-55; the matrix's G-01, G-04, G-13 and G-14.
- **allauth's documentation, read on 9 November 2026** through the web-fetch tool: the JWT token strategy, headless configuration, account configuration, rate limits and the release notes for 65.20 and 65.21. The pages did not state the refresh endpoint's path or the `app` client's URL prefix. The session reads both from the installed release.
- **PyPI, read on 9 November 2026:** `django-allauth` 65.21.1, published 30 October 2026, `Requires-Python >=3.11`, Django 4.2 to 6.1 among its classifiers, `Django>=4.2.16`, `asgiref>=3.8.1`, and `pyjwt[crypto]<3,>=2.0` for the `headless` extra.

## Acceptance checks

**In `services/api`, with `GLOW_ENV=test`, in a clean process environment:**
- `python manage.py check` and `python manage.py test tests --verbosity 2`: OK, the new identity and sealed-runtime tests among them;
- `ruff check .`, `ruff format --check .` and `mypy`: clean.

**In `proofs/postgres-ordering`:** its offline tests under `env -i`, Ruff and mypy: clean.

**In CI, the Database proof checks job on the code head.** The ordering suite passes as before. Then, on the second disposable database, after the migrations apply from zero and `makemigrations --check --dry-run` finds no change, each case passes through the HTTP endpoints. The job stays within its 30-minute timeout, and the evidence records the identity phase's duration.
1. **Sign-up:** one auth user, one unverified `EmailAddress`, one `AppAccount` (`unverified`) and one `unknown` age state. No token pair is issued and no `AccountSession` exists until the email is verified.
2. **Verification by code** moves the account to `active` and returns the token pair. A wrong code, an expired code and a used code are each refused, and the attempt limit holds.
3. **Enumeration and wrong-account linking:** a sign-up with a taken address and with a new one, a reset for an unknown address and for a known one, and an email change to an address another account holds and to a free one each answer alike, as allauth's prevention defines it, and none raises. Where the installed release answers the email change differently, the evidence records it and the threat model names what it tells a signed-in member. The fixture backend shows no message to anyone but the address's owner, none to an address with no account, and no link in any message.
4. **Sign-in** records one `AccountSession` through `open_session` (`valid`, at the current epoch, with D5's reference and D2's lifetime). The actor class accepts the access token, and `AccountAccess` returns the owner's state and validates against the contract's schema.
5. **Refresh:** rotation issues a new pair. The old refresh token, replayed, is refused and ends its session at both layers, so the current pair stops too. A refresh token of a session that has already ended is refused, and nothing else changes. A token with a bad signature, a past expiry or the wrong type is refused without ending any session.
6. **Expiry:** an expired access token, an expired refresh token and an `AccountSession` past `expires_at` are each refused, and after the `AccountSession`'s `expires_at`, allauth's refresh and its account endpoints refuse the session too.
7. **Logout:** the access and refresh tokens are refused at once, and the `AccountSession` is `revoked`.
8. **Two devices:** logging out one leaves the other valid. Ending one from allauth's session list revokes its `AccountSession`, with its `session_revoked` event, and leaves the other valid. A password change ends both, and the member signs in again. A password reset ends both.
9. **Suspension and `deletion_pending`:** through `suspend` and `delete`, the epoch is bumped, every `AccountSession` is refused (its epoch is old), every allauth session has ended, `access_revoked` and `session_epoch_bumped` are in the outbox, each token is refused whatever its remaining life, and a new sign-in is refused.
10. **The account-change notices:** each event D8 lists sends one notice to the member.
11. **The rate limits:** after five failed sign-ins within 300 seconds, the sixth is refused, even with the right password. After five requests at `account/password/change` with a wrong current password, a sixth with the right one, sent more than 60 and less than 300 seconds after the first of the five, is refused and the password is unchanged; allauth's default, `5/m/user`, would accept it. A reversal that restores that default fails the case.
12. **No secret in any output:** no password, code, token, session key or signing key appears in the job's log or the evidence. A log capture at `DEBUG` asserts it.
13. **Reauthentication:** an email change right after sign-in, with no reauthentication, answers 401 with the `reauthenticate` flow, sends no mail and changes no address, and so does one made more than 300 seconds after the reauthentication, or in another session than the one that reauthenticated. A wrong password at `auth/reauthenticate` is refused, and the sixth wrong password within 300 seconds is refused as too many attempts. With the right password, the change goes ahead as acceptance check 10's notice shows. The reauthentication leaves the session key, its `UserSession` row and its `AccountSession` unchanged, and returns no token pair and no `session_token`. A reversal that turns the setting off fails the case.

**Every test with its reversal** (D15), recorded in the evidence record.

## Classification expectation

Full scope: code, a dependency, a migration, a workflow change and the proof. The manager classifies with `main`'s trusted policy, inspects the complete workflow diff and the job's actual steps, and requires full checks before the merge (`AGENTS.md`, "CI routing is not an independent security boundary").

## Report format

The prompt's report: branch, code head and records head; the environment check and start gate; for each Outcome item, the files, tests and reversals; the pinned release with its transitive dependencies and licences; D5's finding from the installed source; every command with its result line; the run of record (each job, the gate's line, the identity suite's counts, whether a retry fired); what could not run; every deviation.

## Review plan

- **The manager verifies the report** against the pushed branch: the complete diff within the owned paths; the dependency pins and hashes; the seal; reversals re-run where useful; the run of record's logs, including the identity phase.
- **Then the PR,** Codex's review of its head, and an exact-head code and security review of the code head, **with a written threat model** (DM-31 item 3; OD-41). Its security focus: every endpoint and its refusals; token handling (signing key, stateful validation, rotation, replay, expiry); the session reference (D5); revocation at both layers (D6); the actor class (D7); enumeration and rate limits; the mail adapter and what a message reveals; the seal; G-13's restored token; G-14's absence of a review path; the proof's secret handling; the session key held in allauth's `UserSession` rows and in `django_session`; the `sid`'s encryption under `SECRET_KEY`; that a replayed rotated refresh token is refused but does not end its session in 65.21.1, so a stolen current refresh token used first keeps a session the member's next refresh cannot end; allauth's own endpoints, which only allauth's layer guards (D2's aligned expiry, D6's repeatable steps); the `verified` transition's locks and the absence of an outer transaction; the two link-building mails (D3); allauth's session list, whose ending goes through Glow's `USERSESSIONS_ADAPTER` (D6); `ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE`; and the actor class's use of allauth's internal `sid` decryption.
- **Dev Manager:** this brief (DM-45), and its next revision before the prompt goes to Nathan (DM-45 1.1). Before the PR merges, at a named commit: the CI policy's paragraph, and the data model's "Maintained authentication mapping" and the contract's "Maintained authentication reference and app mapping" as rewritten. The prompt needs no read of its own (DM-45 item 14): the database password and the JWT signing key are generated for one CI run and are not credential use in the charter's sense (DM-08 7.2's reasoning), and the session takes no live action.

## Correction C1 (DM-47)

- **Why:**
  - **The email-change gap.** At code head `269ac3b` an email change needs no reauthentication: `ACCOUNT_REAUTHENTICATION_REQUIRED` keeps its default, `False` (AM10-06). The implementation session reported it, and Codex raised it on PR42 as its only finding (P1, `glow_identity/conf.py`).
  - **The results upload** (DM-47 C1.4). `sv1-identity-results` uploads `if: always()`, and the job's secret check scans only the suite's log, so the JSON goes out unscanned even after a failed check.
  - **DM-47** ([report](../continuity/dev-manager/reviews/2026-11-09-dm-47-sv1-email-change.md)) approved C1 with C1.1 to C1.4 in given words. This revision applies them: C1.1 in D3, C1.2 as acceptance check 13, C1.4 in D10, and C1.3 in item 2 below. C1's prompt needs no read (DM-47 section 2).
- **Items** (the implementation session, on its branch):
  1. **Reauthentication for an email change** (D3; acceptance check 13):
     - `ACCOUNT_REAUTHENTICATION_REQUIRED = True` in SV1's fragment;
     - the settings case and the API's fragment test;
     - a new identity case for acceptance check 13, with a reversal that turns the setting off;
     - a reauthentication first in the cases that change an address (`notice.email_change`, `enum.email_change_taken_and_free_alike`);
     - the threat model's endpoint row for `auth/reauthenticate`, now used.
  2. **The data model's "Email change and recovery"** (C1.3): its first sentence becomes:

     > One address per account (`ACCOUNT_CHANGE_EMAIL`), changed only after a reauthentication by password within the last 300 seconds (`ACCOUNT_REAUTHENTICATION_REQUIRED`; a sign-in does not count): the new address is verified by code before it replaces the old, and the old address gets the email-changed notice.

  3. **The results upload checked first** (D10): the job's secret check scans `identity-results.json` with the same values as the log; the upload runs only after that check has passed; after a failed check nothing is uploaded, and the log shows only the suite's own result lines. A reversal that uploads unconditionally, with a planted value in the JSON, shows the check refusing.
  4. **The record's section "Correction C1"**, with each item's test and reversal, and the new run of record.
- **Owned paths:**
  - `services/api/glow_identity/conf.py`; `services/api/tests/test_identity_offline.py`;
  - `proofs/postgres-ordering/glow_ordering_proof/identity_*.py` and `proofs/postgres-ordering/tests/test_identity_offline.py`;
  - `.github/workflows/foundation.yml`: the Database proof checks job's SV1 steps only;
  - `docs/architecture/data-model.md`: the first sentence of "Email change and recovery" only;
  - the record: the endpoint table's `auth/reauthenticate` row, and its new section "Correction C1".
- **Exclusions:** every other path, among them `glow_identity`'s other modules, `glow_chat`, `glow_api`, the models, migrations, locks and contracts, and every other job. No new dependency.
- **The stop rule:** the session stops and reports if 65.21.1 cycles the session key, issues a token pair or runs one of Glow's sign-in hooks at `auth/reauthenticate`, or if a fix seems to need a path outside this list. If the reauthentication's response carries a `session_token`, the session records it as a deviation and N3's text is reread (DM-47 C1.2).
- **After C1:**
  - the manager updates the CI policy's upload sentence (governing);
  - the exact-head review reads the corrected head in full, with a written threat model and this in its focus. No delta review is needed, since no review has run;
  - DM-45 14.1's pre-merge read covers C1.4's workflow change (DM-47 section 6).

## Correction C2 (DM-48)

- **Why:**
  - **SV1's exact-head review of `bda299e`** asked for changes (the record, "Exact-head review of SV1"). It found no blocking finding. These were its other findings:
    - three should-fix findings: F-1, the no-link check's false failures; F-2, the password-change guessing budget; and F-3, migration 0004's hash claimed pinned but not;
    - the nits F-4, F-5 and F-7;
    - F-6, about N2's words.
  - **Codex** raised F-1 on `1c26f1d` and F-2 on `30fdf1a` (P2 each).
  - **DM-48** ([report](../continuity/dev-manager/reviews/2026-11-09-dm-48-sv1-review-c2.md)) approved option (a) for F-2, and C2's scope, with C2.1 to C2.8 in given words. This revision applies them:
    - C2.1 in D3's rate-limit bullet and C2.2 in its email-change bullet;
    - C2.3 as acceptance check 11;
    - C2.6 in D10;
    - C2.8's first replacement in D2;
    - the rest in the items below.

    C2's prompt needs no read (DM-48 section 2). A wrong current password sends no notice (DM-48 section 3).
- **Items** (a correction session, on its own branch):
  1. **The password-change limit** (F-2; D3; acceptance check 11; C2.1, C2.3, C2.4):
     - `ACCOUNT_RATE_LIMITS = {"change_password": "5/300s/user"}` in SV1's fragment, with the fragment's rate-limit comment brought into line with D3;
     - the settings case and the API's fragment test;
     - a case for acceptance check 11's second sentence, with a reversal that restores allauth's default `5/m/user`.
       - **The clock:** the suite's `clock_ahead` gives the patched module only `time()`. allauth's limiter also calls `time.monotonic()` and `time.sleep()`, in `cache_lock` (`core/internal/ratelimit.py:47-56`). So moving the limiter's clock needs an object that keeps both (DM-48 section 3).
     - **The record:**
       - C2's section states threat 6 with C2.4's words:

         > The password-guessing budget (D3): a holder of a live session key or access token can test a password at the sign-in form and at `auth/reauthenticate`, which share `login_failed` (5 per 300 seconds for the address), and at `account/password/change` (`change_password`, 5 per 300 seconds for the account, every signed-in request counted). That is 10 per 300 seconds, twice the sign-in form's 5, the remainder SV1 accepts. A right guess at the password change ends every session and sends the password-changed notice.

       - The endpoint row for `POST account/password/change` names the new limit, and so does the D3 row of "Facts read from the installed source".
  2. **The no-link check** (F-1; test-only; C2.5):

     > The check removes the exact code the case issued, every occurrence, before it looks for `http` and `www.`. It removes nothing else and uses no pattern, so a link anywhere else in the message still fails it.

     It needs three cases, each with a reversal that fails it:
     - a message whose code is `HTTP-BCDF` passes;
     - so does a message whose code is `BCDF-GWWW`, ending its sentence;
     - a message with a real link fails.
  3. **Migration 0004's hash** (F-3): its SHA-256 goes in `test_model_definitions.py`'s `pinned` dictionary, so the record's sentence holds.
  4. **Counts only after a failed secret check** (F-4; D10; C2.6): the step's comment and its message change with it.
  5. **The static guard** (F-5; C2.7):
     - it also forbids `request.query_params`, `request.GET`, `request.POST`, `request.COOKIES` and a lowercase `session_token`;
     - it asserts that `actor_for` is called with exactly `user, payload`;
     - it checks C2.7's allow-list:

       > The guard also checks, on the module's syntax tree, that `authentication.py`'s code uses `request` only as the parameter of `authenticate` and `authenticate_header`, and as the argument it passes to allauth's `JWTTokenAuthentication` methods of the same names.

     The code at `bda299e` already meets it (`authentication.py:110-121`), so this adds a test only.
  6. **The verification settings pinned** (F-7): `config.settings_as_briefed` pins `ACCOUNT_EMAIL_VERIFICATION_SUPPORTS_CHANGE` and `ACCOUNT_EMAIL_VERIFICATION_SUPPORTS_RESEND` off, and C2's threat model names them.
  7. **N2's words** (F-6; C2.8, replacements 2 to 6). Each is applied word for word; line breaks may move. Glow's order of checks stays.
     - `glow_identity/strategy.py`, the module docstring only: "run with allauth's own functions in allauth's order:" becomes "run with allauth's own functions in this order:";
     - `docs/architecture/data-model.md`, the replay sentence, and `docs/architecture/production-contracts.md`, "The app mapping as built": "passes allauth's own checks, in allauth's order, but carries" becomes "passes allauth's own checks, its signature first, but carries";
     - the record's "The review plan's security focus", in its bullet on a replayed rotated refresh token, corrected in place and noted in C2's section: "after allauth's own checks, in allauth's order, and adds no cryptography" becomes "after allauth's own checks, its signature first, and adds no cryptography";
     - `services/api/tests/test_identity_offline.py`, the comment in `test_the_replay_check_reads_no_session_before_allauths_own_checks` only: "only after allauth's own checks, in allauth's order." becomes "only after allauth's own checks, its signature first.".
  8. **The record's section "Correction C2"**, with each item's test and reversal, and the new run of record.
- **Owned paths:**
  - `services/api/glow_identity/conf.py`;
  - `services/api/glow_identity/strategy.py`: the module docstring only;
  - `services/api/tests/test_identity_offline.py`;
  - `services/api/tests/test_model_definitions.py`: the `pinned` dictionary only;
  - `proofs/postgres-ordering/glow_ordering_proof/identity_*.py` and `proofs/postgres-ordering/tests/test_identity_offline.py`;
  - `.github/workflows/foundation.yml`: the Database proof checks job's identity-suite step only (its secret check and what it prints);
  - `docs/architecture/data-model.md` and `docs/architecture/production-contracts.md`: the replay sentence only;
  - the record:
    - the D3 row of "Facts read from the installed source";
    - the endpoint row for `POST account/password/change`;
    - the focus bullet on a replayed rotated refresh token;
    - its new section "Correction C2".
- **Exclusions:**
  - every other path, among them `glow_identity`'s other modules and `strategy.py`'s code, `glow_chat`, `glow_api`, the models, migrations, locks and contracts, and every other workflow step and job. No new dependency;
  - the review's section of the record, with its threat model, keeps its words as a record of what the review said.
- **The stop rule:** the session stops and reports in any of these cases:
  - 65.21.1's limiter does not refuse the sixth request at `account/password/change` sent after 60 seconds under `5/300s/user`;
  - the override does not merge into allauth's defaults;
  - a fix seems to need a path outside this list, or a change to `strategy.py` or `authentication.py` beyond the docstring;
  - a fix needs a new package;
  - the Database proof checks job cannot stay within its 30-minute timeout.
- **After C2:**
  - **The manager:**
    - verifies C2;
    - classifies the PR with the pre-change policy;
    - reads the whole workflow diff and the job's actual steps and results;
    - requires full checks before the merge (`AGENTS.md`).
  - **Codex's F-1 and F-2 threads** are answered and resolved.
  - **A delta review on S2's terms** (fewer than 60 non-test lines). Its focus, from DM-48 section 4:
    - the limiter's value, its case and its reversal;
    - the exact-code removal;
    - the workflow hunk;
    - the guard;
    - that C2.8's code changes are a docstring and a comment only;
    - F-3's and F-7's pins.
  - **DM-45 14.1's pre-merge read** at the final head covers:
    - the CI paragraph;
    - both mapping texts, with C2.8's sentence;
    - C1.4's and C2's workflow changes;
    - C2.1 to C2.8 as applied.

## Sessions

- **Brief, revision 1** (9 November 2026): written after P06.3's merge; sent to the Dev Manager as DM-45 ([consultation](../ephemeral/2026-11-09-dm-45-sv1-brief.md), at `d02ea32`).
- **DM-45** (9 November; [report](../continuity/dev-manager/reviews/2026-11-09-dm-45-sv1-brief.md), answered at `0dcd122`, a read of `d02ea32`, integrated at `086c67c`): approved with conditions in given words. It read allauth 65.21.1's and Django 5.2.17's wheels and found seven gaps (G1 to G7), among them the two link-building mails that fail in headless-only mode, a password change that cycles the session key, and G-13's WebAuthn server part. Revision 2 applies every condition as written.
- **Brief, revision 2** (9 November 2026): back to the Dev Manager as DM-46 ([consultation](../ephemeral/2026-11-09-dm-46-sv1-brief-revision-2.md)), for the changed text only (DM-45 1.1), with step 6's new sentence and the carries as recorded.
- **DM-46** (9 November; [report](../continuity/dev-manager/reviews/2026-11-09-dm-46-sv1-brief-revision-2.md), answered at `778ee29`, a read of `d461ea5`, integrated at `5cdf01c`): DM-45's conditions confirmed as applied; the opaque username approved; the replay subclass approved with N2 (allauth's own checks, in its order; no action on an ended session; one refresh at a time); D5 with N3 (the session key's reach); a new finding, N1: allauth's session list ends sessions at its layer only, so Glow's `USERSESSIONS_ADAPTER` ends both; N4 and N5 for the carries; step 6's sentence confirmed.
- **Brief, revision 3** (9 November 2026): applies N1 to N5 as written; no read before the prompt (DM-46 section 1).
- **The implementation prompt** ([prompt](../ephemeral/2026-11-09-sv1-implementation-prompt.md), revision 1): for `Glow App - No Stream`; run by Nathan.
- **The implementation session** (9 November 2026; branch `claude/hopeful-cerf-kc91xx`, code head `269ac3b`, records head `157c1f6`; [record](../testing/evidence/2026-11-09-sv1-identity.md)): Outcome items 1 to 10 and acceptance checks 1 to 12, with 33 reversals each failing its case. The run of record is push run 42578800951: all eight jobs passed and the identity suite passed 47 of 47. The session's findings include an email change that needs no reauthentication.
- **Manager verification** (9 November; the record, "Manager verification"): the diff read whole, the classification, the offline re-runs and three reversals, and the run of record read. The email-change gap goes to the Dev Manager as DM-47, with a proposed correction before the exact-head review (AM10-06). Natural expiry's missing `session_expired` is carried to SV4, and the P11 plan's specification carry is closed.
- **DM-47** (9 November; [report](../continuity/dev-manager/reviews/2026-11-09-dm-47-sv1-email-change.md), answered at `1516629`, a read of `6b8c958`, integrated at `fa17bf3`): the gap confirmed, with its root in DM-45 section 9's sentence, which named no setting. Two corrections to the reading of 65.21.1: a wrong password at `auth/reauthenticate` consumes `login_failed`, and its response carries no `session_token`. C1 approved with C1.1 to C1.6, and its prompt needs no read; N1 to N5 confirmed.
- **Brief, revision 4** (9 November 2026): applies C1.1 to C1.4 as written, and adds "Correction C1".
- **Correction C1's prompt** ([prompt](../ephemeral/2026-11-09-sv1-c1-correction-prompt.md), revision 1): for the implementation session, in `Glow App - No Stream`; run by Nathan.
- **Correction C1** (9 November 2026; a new session, branch `claude/stoic-franklin-ief71e`, code head `bda299e`, records head `96dc3e2`; the record, "Correction C1"):
  - reauthentication for an address change, with a case for acceptance check 13;
  - the job's secret check moved to `identity_scan.py`, which scans the results JSON too; the upload gated on its pass; the suite's own scan of the JSON as well;
  - the data model's sentence.

  Each item has a test and a reversal. Run of record: push run 42634020622, all eight jobs passed, the identity suite 48/48. Nothing met the stop rule.
- **Manager verification of C1** (9 November; the record, "Manager verification of correction C1"):
  - the diff, the classification, the offline re-runs and three reversals, and the run of record read;
  - integrated by fast-forward;
  - F-M1, the no-link check's false failure on a code spelling `HTTP`, diagnosed and dispositioned (fix before the merge, after the review);
  - Codex's P1 thread answered and resolved.
- **The exact-head review prompt** ([prompt](../ephemeral/2026-11-09-sv1-review-prompt.md), revision 1; TypeSafe v8.2: Fable 5.1 at max): the code head `bda299e`, with a written threat model; run by Nathan after Codex had read its commit. Codex's one finding there is F-M1 (P2).
- **The exact-head review** (9 November; the record, "Exact-head review of SV1"): changes required, with no blocking finding.
  - **Should fix:** F-1, F-M1 widened to `www.`; F-2, the password-change guessing budget; F-3, migration 0004's hash claimed pinned but not.
  - **Nits:** F-4 to F-9.
  - **Its statements:** every Dev Manager condition met in code, every allauth fact holding, the workflow confined to the Database job.
- **DM-48** ([consultation](../ephemeral/2026-11-09-dm-48-sv1-review-findings.md), at `38142b3`; [report](../continuity/dev-manager/reviews/2026-11-09-dm-48-sv1-review-c2.md), answered at `c6bce37`, a read of `38142b3`, integrated at `5a576dd`). It asked about four things: F-2's fix, which changes D3's default rate limits on a security boundary; correction C2's scope; F-6's N2 wording; and C1.1 to C1.6 as applied. The verdicts:
  - **F-2:** option (a) approved, `change_password` at `5/300s/user`. D3's words are sharpened: every signed-in request counts, and the remainder is 10 in all, twice the sign-in form's. Acceptance check 11 is reworded, so that its case tells `5/300s` from allauth's `5/m`. A wrong current password sends no notice.
  - **C2's scope:** approved with C2.5 to C2.8, with a delta review on S2's terms.
  - **N2's words:** they change in six places, since allauth checks the `jti` before the user.
  - **C1.1 to C1.6:** confirmed.
- **Brief, revision 5** (9 November 2026): applies C2.1 to C2.8 as written, and adds "Correction C2".
- **Correction C2's prompt** ([prompt](../ephemeral/2026-11-09-sv1-c2-correction-prompt.md), revision 1; TypeSafe v8.2: Opus 5.5 at high): for C1's session or a new one, in `Glow App - No Stream`; run by Nathan after Codex has read its commit.
