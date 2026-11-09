# SV1 — The identity slice: maintained sign-in and the mail adapter, proven on disposable PostgreSQL

- **Work ID:** SV1 (OD-49, N1 (a); PF01 §8, "Server slices"; the F01 flow).
- **Status: brief, revision 1, 9 November 2026; with the Dev Manager as DM-45.** No prompt is written before its answer.
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
    - **G-13**, Google's Restore Credentials for apps with sign-in, from April 2027 (GP-36), *"SV1's brief scope (identity), or P09.2"*;
    - **G-14**, any review sign-in path inside SV1's threat model; P09 owns the reviewer account;
    - **G-04**, Vermont's account-change notice (UST-16: *"within 24 hours after discovering an account change to a Vermont member's account"*, for a change to the password, username, email or contact details).

## Outcome

SV1 builds the server's identity on maintained code, proves it on a disposable PostgreSQL in CI, and keeps it sealed from the served runtime.

1. **Maintained sign-in, configured.** django-allauth headless, `app` client only, with the JWT token strategy (D2), installed and configured in a new Django app, `services/api/glow_identity`:
   - sign-up with email and password, mandatory email verification by code, password reset by code, password change and email change (D3);
   - access and refresh tokens, with refresh rotation and stateful validation (D2);
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
  - **Lifetimes (recommended; DM-45 item 3):**
    - access, 300 seconds, allauth's default and PF01's "short-lived";
    - refresh, 30 days. allauth's default is one day;
    - the `AccountSession`'s lifetime 30 days from sign-in, and the Django session's age at least that, since stateful validation needs the session.
    - **What a member sees:** `AccountSession.expires_at` is fixed when the session opens (`glow_chat`'s `open_session` takes a lifetime; no operation extends it). So 30 days is an absolute limit: a member signs in again every 30 days, however active. A sliding window would need a new reviewed operation in the lock protocol (D6). DM-45 item 3 asks whether this is right, or is Nathan's to decide.
  - **The signing key** (`HEADLESS_JWT_PRIVATE_KEY`, RS256, allauth's default algorithm) is generated for each test process and each CI run, never committed, printed or logged, as P06.DB generates its database password. P11 supplies it as a secret reference. SV1 adds no key to any environment template.
  - **Session tokens instead** (allauth's default strategy) would also meet PF01. They would put every request through a database session lookup and fit the contract's planned mapping less well. The brief follows the planned mapping.
- **D3 — Sign-up, verification and recovery by code, not by link.**
  - `ACCOUNT_LOGIN_METHODS = {"email"}`; `ACCOUNT_SIGNUP_FIELDS` with email and password only; `ACCOUNT_UNIQUE_EMAIL = True` (the data model's intent).
  - `ACCOUNT_EMAIL_VERIFICATION = "mandatory"` with `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True`; `ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED = True`. Codes keep the native app off deep links, which PF01 asks to test for interception. No `HEADLESS_FRONTEND_URLS` are set, so no message carries a link back into the app.
  - **Email change:** one address per account; the new address is verified by code before it replaces the old. The evidence names the installed release's settings for this.
  - `ACCOUNT_PREVENT_ENUMERATION = True` (allauth's default; not `"strict"`, which can create several accounts sharing an email).
  - allauth's rate limits keep their defaults (`ACCOUNT_RATE_LIMITS`). They use Django's cache: a local-memory cache in the proof; P11 needs a shared cache for more than one worker (carried to P11 at DM-45's disposition).
  - **Off in SV1:** login by code, multi-factor authentication, social login (PF01: only with safe linking and platform-policy review; with no social login, Apple's Sign in with Apple rule does not bind), the browser client and the served specification (`HEADLESS_SERVE_SPECIFICATION`).
  - **Passwords:** Django's password hashers and its four validators, with a minimum length of 10. No new hasher dependency.
- **D4 — The app account.**
  - `AppAccount` keeps its one-to-one, protected link to `settings.AUTH_USER_MODEL`, which stays `auth.User` (the static registry and the P06.DB proof, which also drives `glow_chat`, use it). allauth's `EmailAddress` holds the normalized, unique, verified email. A custom user model would be Django's general advice for a new project; here the app identity already lives in `AppAccount`, and changing the user model would ripple into the static registry, the proof and `glow_chat`'s tests (DM-45 item 5).
  - Sign-up creates the `AppAccount` in the transaction that creates the user, through Glow's account adapter (D8) or allauth's signal, whichever the installed release runs inside that transaction. A sign-up that fails leaves neither.
  - Verification by allauth is the only path from `unverified` to `active` (F01's `verified`, role `auth`). A verified email alone establishes nothing else: not adulthood, consent, profile or eligibility (the contract's mapping).
  - **Sign-in opens the `AccountSession` through `glow_chat`'s `open_session`** (D6): the reviewed operation that locks the account, refuses one that is not `active`, and records the session at the current epoch with its reference and lifetime. With mandatory verification, allauth completes no sign-in for an unverified account, so no `AccountSession` exists before verification.
- **D5 — The session reference: a supported, non-secret identifier.** The data model forbids a Glow hash of the session key. And the session key is a credential: by the manager's reading, allauth's `app` client sends it as its `X-Session-Token` during incomplete authentication. The session confirms this from the installed source.
  - **Recommended:** allauth's `usersessions` app, if the installed release provides it for headless JWT sessions. Its `UserSession` row is allauth's own record of a session, with a primary key that is not a credential, and allauth ends a session through it. `AccountSession.auth_session_ref` holds that primary key. The session verifies from the installed source that the key is not derived from the session key, that ending a `UserSession` deletes the Django session, and that a JWT carries a reference to its session.
  - **What it stores:** `UserSession` records the client's IP address and user agent. Those are personal data: SV1 records them as such in the data model, with `USERSESSIONS_TRACK_ACTIVITY` off (no last-seen updates), and their retention goes to P08 (carried at DM-45's disposition).
  - **If the installed release cannot do this,** the session stops and reports. The data model's mapping is then amended under DM-45 before any code relies on another reference.
- **D6 — Revocation: one lock protocol, two layers.**
  - **One lock protocol.** P06.2's reviewed adapter, `glow_chat/contact.py`'s `OrmContactPersistence`, already owns every `AccountSession` and account-state transition: `open_session`, `sign_out`, `expire_session`, `suspend` and `delete`. Each runs under the lock protocol that P06.DB and P06.2 proved against sends (DB06), and writes its outbox events (`session_revoked`, `session_expired`, `access_revoked`, `session_epoch_bumped`; the data model's event table). SV1 calls these operations and adds none of its own. `glow_chat` is not changed (DM-45 item 6).
  - **Two layers.** After the operation commits, SV1 ends the matching allauth session or sessions, so their tokens fail at allauth's layer too. Between the two commits, the `AccountSession` is already refused by the actor class (D7), so Glow's refusal never waits on allauth's. Each rule is tested at both layers.
  - **Logout:** `sign_out` for this session, then allauth's logout.
  - **Password change:** `sign_out` for every other valid session of the account; the current one stays (Django's session-hash update ends the others at allauth's layer).
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
  - never takes an actor, account or session from the request body or a header other than the token.
- **D8 — The mail adapter.**
  - **The seam is Django's email backend** (`EMAIL_BACKEND`), which allauth sends through. SV1 adds a Glow fixture backend that records each message in memory and has no network code. No SMTP or provider setting exists. P11 and M07 choose the provider (OD-50).
  - **Glow's account adapter** (`ACCOUNT_ADAPTER`) owns each message's subject and body: plain text, Glow's name only (ADR 0003, S15), no tracking, and no account detail beyond what the message needs. A code message holds the code and its expiry.
  - **The account-change notices** (`ACCOUNT_EMAIL_NOTIFICATIONS = True`) go to every member, not only Vermont's (G-04, UST-16): password change, password reset and email change, each tested. The session lists the events the installed release covers. A change UST-16 names that allauth does not notify is reported, not built.
- **D9 — The age state** (G-01; OD-55's D3 (a)).
  - **Domain:** in `glow_domain/identity.py`, beside `AccountId`, a pure `AgeAssurance` type: the state (`unknown`, `self_declared_adult`, and room for the stores' signals), the method, when it was recorded and the policy version; and the port that reads and writes it.
  - **Persistence:** one new model in `glow_persistence`, one row per account, written only through the port, in a new migration after `0003`. No birth date is stored in it: P04's onboarding holds the self-entered date, and a later slice writes the state from it.
  - **In SV1:** sign-up records `unknown`. Nothing reads the state yet: SV3's eligibility reads it, and P09.2 adds the stores' signals (G-01's Work Register row).
- **D10 — The proof: P06.DB's job, a second disposable database.**
  - The identity suite lives in `proofs/postgres-ordering` beside the ordering suite, with its own settings module, which installs `glow_identity`, allauth's apps, `django.contrib.sessions` and the identity URL configuration. It reuses the proof's refusals: a clean environment, the run's marker, and `dbshell` refused.
  - In the Database proof checks job it runs after the ordering suite, on a second database created for it in the same disposable PostgreSQL 17.11, with its own marker and the proof's non-superuser role. It applies the reviewed migrations from zero (setup, not DB01 acceptance), then the cases.
  - **The run's secrets** (the database password, already; the JWT signing key, new) are generated in the job, masked before anything prints, and destroyed with it.
  - **Why not a new job:** the marker, the refusals and the database's lifecycle already exist and were reviewed (P06.DB; DM-10 to DM-12). A new job would duplicate them. A new proof package is the alternative (DM-45 item 7).
- **D11 — The seal, checked.** A new test, in the style of `test_chat_sealed_runtime.py`, proves that the runtime's settings, URL configuration and WSGI application import none of `glow_identity`, `allauth`, `jwt` or `cryptography`, that the database backend is dummy, and that the connection refusal is unchanged. `glow_api/` is not changed.
- **D12 — The dependency** (DM-45 item 8).
  - `django-allauth[headless]` at the latest 65.x release when the session starts, checked on PyPI, with its release notes read for security entries. The latest on 9 November 2026 is 65.21.1 (30 October 2026). Its `headless` extra requires `pyjwt[crypto]` (2.x), which brings `cryptography`.
  - **Scope:** `services/api/requirements-dev.in` and its lock only, as P06.2 put `getstream` (DM-16 2.1); `requirements.in` and `requirements.lock` stay unchanged until P11 moves the pins. The proof's own lock takes the same pins.
  - Hash-locked; the dependency inventory and licences recorded; the dependency-pin tests updated.
- **D13 — G-13 and G-14.**
  - **G-13 (Restore Credentials):** a client restoring its refresh token on a new device is a native feature (P09.2). On the server it is an ordinary refresh, under D6's rules. SV1 builds nothing for it and records that the threat model covers a restored or copied refresh token. The native part goes to P09.2 (carried at DM-45's disposition).
  - **G-14 (the reviewer account):** SV1 builds no review path. A verified reviewer account signs in with email and password, with no code, since login by code and multi-factor authentication are off (D3). The threat model records that no fixture adapter, test account or setting can reach real members (PF01 P12's validation: *"Verify that no fixture adapter or test account privileges can reach real users"*). P09 owns the account.
- **D14 — The contract is unchanged.** `packages/contracts` stays as it is. `AccountAccess` is served as the schema defines it. The production catalog's paths map stays empty until P11 serves the routes (`test_production_openapi_catalog_does_not_claim_implemented_routes`). The headless API is allauth's own specification, which the evidence record cites at the pinned release, and which is not vendored.
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

**In CI, the Database proof checks job on the code head.** The ordering suite passes as before. Then, on the second disposable database, after the migrations apply from zero and `makemigrations --check --dry-run` finds no change, each case passes through the HTTP endpoints:
1. **Sign-up:** one auth user, one unverified `EmailAddress`, one `AppAccount` (`unverified`) and one `unknown` age state. No token pair is issued and no `AccountSession` exists until the email is verified.
2. **Verification by code** moves the account to `active` and returns the token pair. A wrong code, an expired code and a used code are each refused, and the attempt limit holds.
3. **Enumeration:** sign-up with a taken email and a reset for an unknown email answer as allauth's prevention defines, and the fixture backend shows no message to anyone but the address's owner.
4. **Sign-in** records one `AccountSession` through `open_session` (`valid`, at the current epoch, with D5's reference and D2's lifetime). The actor class accepts the access token, and `AccountAccess` returns the owner's state and validates against the contract's schema.
5. **Refresh:** rotation issues a new pair, and the old refresh token is refused when replayed.
6. **Expiry:** an expired access token, an expired refresh token and an `AccountSession` past `expires_at` are each refused.
7. **Logout:** the access and refresh tokens are refused at once, and the `AccountSession` is `revoked`.
8. **Two devices:** logging out one leaves the other valid. A password change leaves the current session and ends the other. A password reset ends both.
9. **Suspension and `deletion_pending`:** through `suspend` and `delete`, the epoch is bumped, every session ends, `access_revoked` and `session_epoch_bumped` are in the outbox, each token is refused whatever its remaining life, and a new sign-in is refused.
10. **The account-change notices:** each event D8 lists sends one notice to the member.
11. **The rate limit** on failed sign-ins refuses past its limit.
12. **No secret in any output:** no password, code, token, session key or signing key appears in the job's log or the evidence. A log capture at `DEBUG` asserts it.

**Every test with its reversal** (D15), recorded in the evidence record.

## Classification expectation

Full scope: code, a dependency, a migration, a workflow change and the proof. The manager classifies with `main`'s trusted policy, inspects the complete workflow diff and the job's actual steps, and requires full checks before the merge (`AGENTS.md`, "CI routing is not an independent security boundary").

## Report format

The prompt's report: branch, code head and records head; the environment check and start gate; for each Outcome item, the files, tests and reversals; the pinned release with its transitive dependencies and licences; D5's finding from the installed source; every command with its result line; the run of record (each job, the gate's line, the identity suite's counts, whether a retry fired); what could not run; every deviation.

## Review plan

- **The manager verifies the report** against the pushed branch: the complete diff within the owned paths; the dependency pins and hashes; the seal; reversals re-run where useful; the run of record's logs, including the identity phase.
- **Then the PR,** Codex's review of its head, and an exact-head code and security review of the code head, **with a written threat model** (DM-31 item 3; OD-41). Its security focus: every endpoint and its refusals; token handling (signing key, stateful validation, rotation, replay, expiry); the session reference (D5); revocation at both layers (D6); the actor class (D7); enumeration and rate limits; the mail adapter and what a message reveals; the seal; G-13's restored token; G-14's absence of a review path; and the proof's secret handling.
- **Dev Manager:** this brief (DM-45). The CI policy's paragraph before the PR merges. The prompt needs no read unless DM-45 says otherwise: the database password and the JWT signing key are generated for one CI run and are not credential use in the charter's sense (DM-08 7.2's reasoning), and the session takes no live action.

## Sessions

- **Brief, revision 1** (9 November 2026): written after P06.3's merge; sent to the Dev Manager as DM-45.
