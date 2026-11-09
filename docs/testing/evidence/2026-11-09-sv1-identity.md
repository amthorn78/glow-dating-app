# SV1 — The identity slice: maintained sign-in and the mail adapter, proven on disposable PostgreSQL: evidence record

- **Work:** SV1, the identity slice ([brief](../../planning/sv1-identity.md), revision 3: Outcome items 1 to 10, D1 to D15 and acceptance checks 1 to 12; [DM-45](../../continuity/dev-manager/reviews/2026-11-09-dm-45-sv1-brief.md); [DM-46](../../continuity/dev-manager/reviews/2026-11-09-dm-46-sv1-brief-revision-2.md)).
- **Prompt:** [`docs/ephemeral/2026-11-09-sv1-implementation-prompt.md`](https://github.com/amthorn78/glow-dating-app/blob/dc3e55150cd473e372f81d89d72febdede9c0d6c/docs/ephemeral/2026-11-09-sv1-implementation-prompt.md), revision 1, from `dc3e55150cd473e372f81d89d72febdede9c0d6c` of the manager branch `claude/magical-wozniak-yfmmx2`.
- **Session:** one implementation session, started by Nathan, 9 November 2026 (UTC). Branch `claude/hopeful-cerf-kc91xx`, started at `dc3e551`.
- **Code commits:**
  - `17a5607`: the pins;
  - `f09a00f`: the age state;
  - `1c0c417`: `glow_identity`;
  - `46fbd37`: the identity suite and the Database proof checks job's steps;
  - `269ac3b`: one comment in the proof's `requirements.in`, corrected after `46fbd37`'s run (see "Deviations, findings and the stop rule").
- **Code head:** `269ac3bf6a275b064ddd4ec772cd15b1cbce4506`.
- **Records head:** the last commit on the branch. It is Markdown only (the two mappings, DB09's entry and this record), and no code follows the code head.
- **Run of record:** push run **42578800951** (Foundation run 907) on `269ac3b`:
  - all eight jobs `success`, and `Application checks passed`;
  - API `Ran 449 tests`; proof `Ran 175 tests`; the ordering suite's three verdicts PASS;
  - the identity suite **47/47 in 38.1 s**, the identity phase **38 s** of the job's 30 minutes, and the secret scan clean;
  - no toolchain retry.

  The earlier push run 42575311159 on `46fbd37`, one comment older, passed every job with the same counts.

## Environment check (names only)

- **`DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`:** none present. The prompt's loop printed nothing.
- **`STREAM_*` and `PG*`:** no name present. `compgen -e | grep -E '^(STREAM_|PG)'` printed nothing and exited 1, consistent with `Glow App - No Stream`.
- **GitHub token names:** `GH_TOKEN` and `GITHUB_TOKEN` are present and were never read. Every repository command ran without them.
- **Toolchain:**
  - `python3.12 --version`: `Python 3.12.14`, matching `services/api/.python-version`;
  - `node --version`: `v24.19.0`;
  - `npm --version`: `11.9.0`;
  - `docker --version`: `Docker version 29.9.2, build a82e528`;
  - `uv --version`: `uv 0.11.32`.

  All of these are in `$HOME/.local/bin`. That directory is second on `PATH`, after `/nix/var/nix/profiles/default/bin`, which holds none of them.
- **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus `GLOW_ENV=test` for the API.
  - The lock compiles and the virtual environments' installs also passed `HTTPS_PROXY` and `SSL_CERT_FILE` by reference, never printed.
  - The local database scripts refuse to start if `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name is set.

## Start gate

| Check | Result |
|---|---|
| `git fetch origin claude/magical-wozniak-yfmmx2 main` | fetched; `origin/claude/magical-wozniak-yfmmx2` = `dc3e55150cd473e372f81d89d72febdede9c0d6c` (the prompt's commit is the live manager head); `origin/main` = `da92f1f` |
| `git switch -C claude/hopeful-cerf-kc91xx dc3e551…`; `git rev-parse HEAD` | `dc3e55150cd473e372f81d89d72febdede9c0d6c` |
| `git merge-base --is-ancestor 8d2de72… HEAD && echo "PR41 present"` | `PR41 present` |
| `git diff --name-only da92f1f… HEAD \| grep -v -E '\.md$'` | nothing |
| `git diff --name-only dc3e551… origin/claude/magical-wozniak-yfmmx2 -- services/api proofs/postgres-ordering .github 'docs/testing/evidence/*sv1-identity*' docs/architecture docs/testing/p11-deferred-acceptance.md` | nothing |
| `test -e services/api/glow_identity && echo "glow_identity exists"` | nothing printed |
| `grep -c -i 'django-allauth' services/api/requirements-dev.lock proofs/postgres-ordering/requirements-dev.lock` | `0` and `0` |
| `ls services/api/glow_persistence/migrations \| grep -E '^[0-9]{4}_'` | `0001_event_infrastructure.py`, `0002_app_domain.py`, `0003_chat_identity_read_cursor.py` |
| Staleness | `dc3e551` is the live manager head, so no owned path changed after it. The brief's "Sessions" ends with the prompt ("with Nathan") and records no implementation session, so the prompt is not stale |

**Read before the work, completely:**
- root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`; `proofs/postgres-ordering/README.md`;
- the brief, revision 3; DM-45's and DM-46's reports, their "Tried" lists among them;
- F01 and `AccountAccess` in `flows-v1.json` and `gapp-api-v1.schema.json`, and the contract's "Maintained authentication reference and app mapping";
- the data model's "Maintained authentication mapping", unit-of-work table and outbox event table;
- in `glow_chat/contact.py`: `_run`, `open_session`, `sign_out`, `expire_session`, `_end_session`, `suspend`, `delete` and `_revoke_account`;
- `AppAccount` and `AccountSession` in `glow_persistence/models.py`; `test_chat_sealed_runtime.py`; `glow_domain/identity.py`;
- the proof: its settings, `environment`, `marker`, the suites' entry points and its locks, and the Database proof checks job, whole;
- the P06.DB brief's D1 to D6, and the P11 plan's DB09 and "From SV1";
- the CI policy's Database proof checks paragraph (read only).

## The pinned release, its transitive set and licences

**PyPI** (`https://pypi.org/pypi/django-allauth/json`, read 9 November 2026 with `curl` to the scratch directory):
- the latest release is 65.21.1, uploaded on 30 October 2026 at 18:27 UTC (wheel and sdist);
- `Requires-Python >=3.11`; its classifiers name Django 4.2, 5.0, 5.1, 5.2, 6.0 and 6.1; its License field is `MIT`;
- `Requires-Dist`: `Django>=4.2.16`, `asgiref>=3.8.1`, `pyjwt[crypto]<3,>=2.0` for the `headless` extra, and `PyYAML<7,>=6` for `headless-spec`;
- the wheel's SHA-256 is `7bdf018c9f3f0a32c80677f84e7777272d9c833b180bd6734314c4831c802a9e`, and the sdist's is `128344e260a22b62796747be0a2249ad9488a509c1aa34ab35e3fcf22862dd9e`. Both are the lock's two hashes, and the sdist downloaded to the scratch directory has the second.

**The release notes** (`ChangeLog.rst` in that sdist), read for security entries from 65.20.0 to 65.21.1:
- **65.21.1:** "Fixed rate limits with multiple windows for the same scope sharing a cache entry, which could bypass longer windows". That covers `login_failed` (`10/m/ip,5/300s/key`), which SV1 relies on, and the pin includes the fix. Also WebAuthn user verification: MFA is not configured.
- **65.21.0:** the phone verification attempt limit not aborting pending flows (no phone is configured), and an inactive user's WebAuthn records (no MFA).
- **65.20.1:** two MFA entries (no MFA).
- **65.20.0:** cancelled multi-stage logins mingling authentication records (fixed in the pin), and the binding of authorization state to its provider (no social login). Its fixes also say the reset-by-code timeout "now restarts after the code is confirmed", which the source confirms (below).

**The locks** (`uv pip compile … --python-version 3.12 --generate-hashes --no-header`, uv 0.11.32):

| Lock | Command's constraint | Before → after | New packages | Other changes |
|---|---|---|---|---|
| `services/api/requirements-dev.lock` | `--constraint ../../proofs/stream-chat/requirements.lock` (as before) | 45 → 49 | `cffi` 2.1.1, `cryptography` 50.0.2, `django-allauth` 65.21.1, `pycparser` 3.12 | none: insertions only (174 lines); `pyjwt` stays 2.15.0 with its hashes, its `# via` gaining `django-allauth` |
| `proofs/postgres-ordering/requirements.lock` | `--constraint ../../services/api/requirements-dev.lock` | 6 → 12 | `cffi`, `cryptography`, `django-allauth`, `djangorestframework`, `pycparser`, `pyjwt`, at the API's versions and hashes | `# via` lines only (4 removed, rewritten with the constraint) |
| `proofs/postgres-ordering/requirements-dev.lock` | `-c requirements.lock` (its input's own) | 12 → 18 | the same six | none |

`requirements-dev.in` gained one comment and `django-allauth[headless]==65.21.1`. The proof's `requirements.in` gained the same pin plus `djangorestframework==3.18.1` and `pyjwt==2.15.0`, the versions `services/api` already pins. `requirements.in` and `requirements.lock` in `services/api` are unchanged: the runtime scope is untouched (D12).

**The transitive set** is exactly the brief's:
- `django-allauth` requires Django (5.2.17), `asgiref` (3.12.1) and, for `headless`, `pyjwt[crypto]`, all already pinned;
- `pyjwt[crypto]` brings `cryptography`, which requires `cffi`, which requires `pycparser`;
- no other package is new, and PyJWT did not move from 2.15.0.

**Licences**, from each installed wheel's metadata (`services/api/dependency-inventory.json`, `observed_date` 2026-11-09; all 45 earlier entries re-read and unchanged):

| Package | Version | Scope | Licence (metadata) | Licence files |
|---|---|---|---|---|
| django-allauth | 65.21.1 | development | License field `MIT`; classifier MIT | `LICENSE`, `AUTHORS` |
| cryptography | 50.0.2 | development | `Apache-2.0 OR BSD-3-Clause` (expression) | `LICENSE`, `LICENSE.APACHE`, `LICENSE.BSD` |
| cffi | 2.1.1 | development | `MIT-0` (expression) | `LICENSE` |
| pycparser | 3.12 | development | `BSD-3-Clause` (expression) | `LICENSE` |
| PyJWT (unchanged) | 2.15.0 | development | `MIT` (expression) | `LICENSE`, `AUTHORS.rst` |

allauth ships no `py.typed`, so both `pyproject.toml` files give mypy `ignore_missing_imports` for `allauth.*`. The proof's file also covers `rest_framework.*` and `glow_identity.*`, which it imports from `services/api`.

## Facts read from the installed source (django-allauth 65.21.1, Django 5.2.17)

Paths are relative to the virtual environment's `site-packages`; `allauth/` is 65.21.1 and `django/` is 5.2.17. Every fact the brief asks the session to confirm is confirmed below. The table also records facts found while reading: the phone and code-confirm routes, reauthentication's default, the rate-limit details, and a reset code's indirect verification. The stop rule's case ("the installed release differing from the brief's facts") did not arise.

| Brief | Fact | File and line |
|---|---|---|
| D2 | Defaults: algorithm `RS256`; access 300 s; refresh 86,400 s (SV1 sets 30 days); stateful validation **off** (SV1 turns it on); rotation on | `allauth/headless/app_settings.py:54`, `:62`, `:66`, `:74`, `:78` |
| D2 | With stateful validation, an access token is valid only while its session exists and that session's user is the token's `sub` | `allauth/headless/tokens/strategies/jwt/internal.py:35-46` (`validate_access_token`), `:98-107` (`validate_token_user`) |
| D2 | The session's user is Django's `get_user`, which checks the session's stored hash against the user's current password hash and refuses an inactive user | `allauth/core/internal/sessionkit.py:7-14`; `django/contrib/auth/__init__.py:295` (`get_user`; the hash comparison at `:316-319`) |
| D2 | Decoding verifies the signature with the configured algorithm only, then the expiry, then `token_use` | `internal.py:182-200` (`decode_token`) |
| D2 | A refresh token is checked in this order: decoded, its session found from `sid`, its `jti` present and unexpired in the session's state, its user the session's. Rotation pops the `jti` and creates a new token. Nothing ends the session when the `jti` is missing: that is the replay, which Glow's subclass handles | `internal.py:110-128` (`validate_refresh_token`), `:279-282` (`invalidate_refresh_token`); `strategy.py:78-92` (`refresh_token`; rotation at `:86-88`, `session.save()` at `:91`) |
| D2 | The refresh tokens' state is `session["headless_refresh_tokens"]`, so it dies with the session | `internal.py:243-244` |
| D2 | Django stores a date-time expiry as an ISO string, so later saves keep it; the database backend loads only sessions whose `expire_date` is in the future | `django/contrib/sessions/backends/base.py:354` (`set_expiry`; the date-time branch at `:378-380`), `:314` (`get_expiry_date`); `django/contrib/sessions/backends/db.py:35` |
| D3 | With `HEADLESS_ONLY`, building a frontend URL that is not configured raises `ImproperlyConfigured` | `allauth/core/internal/httpkit.py:115-123` |
| D3 | The default account-already-exists mail builds the sign-up and reset links; the unknown-account mail builds the sign-up link. `ACCOUNT_EMAIL_UNKNOWN_ACCOUNTS` defaults to on | `allauth/account/adapter.py:722-733`; `allauth/account/internal/flows/signup.py:75-86`; its use, `allauth/account/internal/flows/email_verification.py:263`; `allauth/account/app_settings.py:537-538` |
| D3 | Code limits: verification 3 attempts and 900 s; reset 3 attempts and 180 s, and confirming a reset code restarts its timer | `app_settings.py:114-119`, `:516-521`; `allauth/account/internal/flows/password_reset_by_code.py:49-53` |
| D3 | `ACCOUNT_PREVENT_ENUMERATION` defaults to `True`; with it, a taken-address sign-up is a login stage with no user, so it answers as a new one does | `app_settings.py:44-45`; `flows/signup.py:68-72` |
| D3 | Rate limits (defaults kept, except `change_password`, which SV1 sets to `5/300s/user` in place of allauth's 5/m/user; correction C2, DM-48; the override merges into the defaults, `app_settings.py:311`): `login_failed` `10/m/ip,5/300s/key`; with verification by code, `confirm_email` `1/10s/key`, a 429 when exceeded; also `manage_email` 10/m/user, `reset_password` 20/m/ip,5/m/key, `signup` 20/m/ip, `login` 30/m/ip | `app_settings.py:268-311`; `email_verification.py:150-187` (the 429 at `:186`), `:335-356` (a sign-in of an unverified address inside the window is refused) |
| D3 | Email change: `ACCOUNT_CHANGE_EMAIL` defaults off; SV1 turns it on (one address; the new one verified before it replaces the old). A verify request for an address another account holds verified is refused `email_taken` | `app_settings.py:147-148`; `allauth/headless/account/inputs.py:119` |
| D3 | Off by default and kept off: login by code (its request routes mount only when enabled). Reauthentication for an email change (`ACCOUNT_REAUTHENTICATION_REQUIRED`) is off by default; correction C1 turns it on in `conf.py` (corrected by the manager after C2's delta review, N-6) | `app_settings.py:553-554`, `:549-550`; `allauth/headless/account/urls.py:103` |
| D3 | The phone routes and `auth/code/confirm` mount whatever the configuration; the default adapter's `get_phone` raises `NotImplementedError` | `headless/account/urls.py:24-25`, `:43-44`, `:91-97`; `account/adapter.py:1063-1069` |
| D4 | Headless sign-up opens no transaction (no `atomic` in the view or the flow) | `allauth/headless/account/views.py`; `flows/signup.py` |
| D4 | The default `populate_username` reads the email to fill the username | `account/adapter.py:320-330` |
| D5 | The `app` client gets the session key as `meta.session_token` whenever the session was modified and differs from the header's | `allauth/headless/internal/sessionkit.py:24-34`; `allauth/headless/internal/restkit/response.py:33-37` |
| D5 | `X-Session-Token` is read first; the JWT strategy falls back to the access token's `sid` only without it | `allauth/headless/tokens/strategies/base.py:13`; `jwt/strategy.py:20-27` |
| D5 | Every headless request runs in `authentication_context`, which looks up that session token's session. A missing or expired session answers 410 | `allauth/headless/internal/authkit.py:53-65`; `sessionkit.py:48-62` |
| D5 | `sid` is the session key encrypted with AES-CTR under `sha256(SECRET_KEY)`, with a fresh 16-byte initialization vector per token | `internal.py:53-61`, `:65-76`, `:80` (`session_key_from_sid`) |
| D5 | `UserSession`: created for every sign-in by the `user_logged_in` receiver; its primary key is a `BigAutoField`; it holds `session_key`, `ip` and `user_agent`; `end()` deletes the Django session, then the row | `allauth/usersessions/apps.py:10`, `:22`; `signals.py:16`; `migrations/0001_initial.py:22`; `models.py:88`, `:93`, `:95`, `:35-41`, `:127-131` |
| D5 | A password change keeps the session only by `update_session_auth_hash`, which cycles the key; `ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE` logs out instead (default off; SV1 on) | `flows/password_change.py:45-55`; `django/contrib/auth/__init__.py:387-396`; `app_settings.py:435-436`; `usersessions/signals.py:22-23` |
| D5 | `USERSESSIONS_TRACK_ACTIVITY` (SV1 off) and `USERSESSIONS_ADAPTER` | `usersessions/app_settings.py:25`, `:19` |
| D6 | allauth's `post_login` builds the `AuthenticationResponse` (the token pair) **before** it sends `user_logged_in`, which creates the `UserSession`. So a fail-closed sign-in must end the session and build a new response | `account/adapter.py:551-590` (`:568`, `:576`) |
| D6 | The session list: `DELETE app/v1/auth/sessions` takes the member's own sessions, and ends them through the usersessions adapter's `end_sessions` at allauth's layer only; if the current one is among them, allauth logs out | `headless/urls.py:51`; `headless/usersessions/views.py:16-23`; `headless/usersessions/inputs.py:14`; `usersessions/internal/flows/sessions.py:18-22`; `usersessions/adapter.py:17` |
| D6 | Verification by code finishes through `mark_email_address_as_verified`, which calls the adapter's `confirm_email` (Glow's hook). A confirmed **reset** code verifies the address through `verify_email_indirectly`, which does not call the adapter: the next sign-in takes the `verified` transition then | `flows/email_verification_by_code.py:86-94`; `email_verification.py:359-365`, `:24-34`, `:47`; `password_reset_by_code.py:56` |
| D6 | Routes: `_allauth/app/v1/…` and `tokens/refresh` | `headless/urls.py:75`, `:93`; `headless/tokens/urls.py:12` |
| D7 | `JWTTokenAuthentication` returns the user and the validated payload | `allauth/headless/contrib/rest_framework/authentication.py:33-41` |
| D8 | Notices go only when `ACCOUNT_EMAIL_NOTIFICATIONS` is on (default off), to the primary address, with a context holding the time, IP and user agent. Glow's text uses none of the three. The five notices: | `account/adapter.py:928-946`; `app_settings.py:545-546` |
| D8 | — password changed; password set | `flows/password_change.py:23`, `:36` |
| D8 | — password reset | `flows/password_reset.py:60` |
| D8 | — email deleted; email changed (to the old address) | `flows/manage_email.py:49-50`, `:127-128` |
| D8 | The code messages: `email_confirmation_signup` and `email_confirmation`, and `password_reset_code` | `account/adapter.py:753-755`; `password_reset_by_code.py:80` |

**D5's finding.** The installed release can do what D5 needs. `UserSession`'s primary key is a supported, non-secret identifier: an auto-incremented row ID, not derived from the session key. The session key itself is a credential, and the threat model below records its reach.

## Changes, tests and reversals

**Method.**
- Each reversal is a temporary edit by a scratch helper outside the checkout. It replaces one exact string, which must occur exactly once, and drops the edited module's cached bytecode before and after the run. It runs the named suite or test, restores the file with `git checkout`, and checks that the code paths are clean (`git status --porcelain -- services proofs .github packages apps scripts` empty).
- An identity reversal runs on a new local throwaway database. The helper starts a container from the CI job's pinned image, applies the migrations, runs `makemigrations --check --dry-run`, then runs the whole suite.
- **The results below are a re-run of all 33 reversals on the code head's code** (`46fbd37`; the later commit changes one comment), after an unchanged baseline run passed 47 of 47.
- An earlier batch had caught each reversal during development. Some cases changed after parts of that batch ran (among them `actor.refuses_inactive_account`, which now moves the state alone), so the whole list was run again on the final code.
- Local runs are iteration, not evidence: CI's run is the run of record.

**API tests** (`services/api/tests`, 27 new; 449 in all):
- `test_identity_sealed_runtime.py` (4);
- `test_identity_offline.py` (20, under `tests/identity_offline_settings.py`: SV1's fragment, a `SECRET_KEY` and an RSA key generated per process, and the dummy database);
- `test_dependency_pins.py` (+2);
- `test_model_definitions.py` (+1).

**Proof tests** (`proofs/postgres-ordering/tests`, 15 new; 175 in all):
- `test_identity_offline.py` (14);
- `test_django_pin.py`: one test replaced by two.

**The identity suite** (`python -m glow_ordering_proof identity`): 47 cases through the HTTP endpoints with Django's test client, then a scan of every secret it handled.

| Outcome item | Files | Tests (identity cases unless named) | Reversals |
|---|---|---|---|
| 1. Maintained sign-in, configured: sign-up, verification and reset by code, password and email change, tokens (rotation, stateful validation, replay), logout, enumeration resistance and rate limits | `glow_identity/conf.py` (the fragment), `adapter.py`, `strategy.py`, `urls.py` | `config.settings_as_briefed`, `config.routes`, `endpoints.refusals`, `signup.*`, `verify.*`, `refresh.*`, `logout.ends_at_once`, `enum.*`, `notice.email_change`, `ratelimit.failed_sign_ins`; API: `test_identity_offline` (the fragment's values, the 18 routes, the strategy and adapters) | D2-a, D2-b, D2-c, D3-a, D3-b, X-ratelimit, X-phone |
| 2. The app account, bound to the maintained user: `unverified` in sign-up's transaction; `verified` to `active`; each sign-in an `AccountSession` at the epoch with D5's reference | `adapter.py:60-69` (`save_user`), `:56-58` (`populate_username`), `:83-89` (`confirm_email`), `:93-104` (`post_login`); `revocation.py:88-106` (`mark_verified`), `:126-166` (`open_sign_in_session`) | `signup.records_unverified_account`, `signup.one_transaction`, `signup.failure_leaves_no_user`, `verify.activates_and_issues_pair`, `verify.transition_retried_at_sign_in`, `verified.waits_on_account_lock`, `verified.refuses_unless_unverified`, `signin.records_account_session`, `signin.reference_not_derived`, `signin.unverified_gets_no_session`, `signin.fails_closed` | D4-a, X-age, X-username, D6-a, D6-b, X-retry, D6-d, D2-d, X-lifetime |
| 3. Revocation at both layers: logout, password change, password reset, suspension and deletion; not `active` or not `valid` at the epoch, refused | `revocation.py` (every entry point starts with `require_no_transaction()`, `:61-65`), `sessions.py:21-24`, `strategy.py:25-49`, `adapter.py:108-114` | `logout.*`, `devices.*`, `revoke.*`, `refresh.replay_ends_session`, `actor.refuses_revoked_session_between_layers`; API: the static guards in `test_identity_offline` (entry points, no `ATOMIC_REQUESTS`) | D6-c, D6-e, D6-f, D6-g, D6-h, D2-a, D2-b |
| 4. The actor: one DRF class, allauth's `JWTTokenAuthentication`, then the account and the session | `authentication.py:63-106` (`actor_for`), `:109-121` | `actor.uses_token_sid_not_header`, `actor.refuses_inactive_account`, `actor.refuses_stale_epoch`, `actor.refuses_revoked_session_between_layers`, `expiry.account_session`; API: the actor reads no header (static) | D7-a, D7-b, D7-c, X-expire |
| 5. One Glow route, the member's own `AccountAccess`, validated against the contract's schema | `views.py`, `access.py`, `urls.py:11` | `signin.records_account_session` (the served body against `AppResponse` with the proof's schema subset check), `endpoints.refusals` (the `Error` shape; 401 and 405); API: the builders against `packages/contracts/runtime.py`'s validator for every state | X-access |
| 6. The mail adapter: Glow's wording, a fixture backend refusing any network send, the notices for every member | `mail.py`, `messages.py`, `adapter.py:73-79` | `mail.no_link_no_stranger` (62 messages in the run of record), `notice.email_change`, `devices.password_change_ends_both`, `devices.password_reset_ends_both`, `enum.signup_taken_and_new_alike`; API: the wording (no link, Glow's name, code and expiry), every allauth template accounted for, the backend with networking blocked | X-link, D8-a, D3-b |
| 7. The age state, behind a seam | `glow_domain/identity.py` (`AgeAssurance`, `AgeAssurancePort`); `glow_persistence/models.py` (`AccountAgeState`); migration `0004_account_age_state.py`; `glow_identity/age.py` | `signup.records_unverified_account` (one `unknown` row), `signup.failure_leaves_no_user` (an age-state write failure rolls back the user and its account); API: the type's rules, `test_migration_0004_adds_the_age_state_only`, the model count 35 | X-age |
| 8. The proof | `proofs/postgres-ordering/glow_ordering_proof/identity_*.py`, `schema_check.py`, `__main__.py`; `.github/workflows/foundation.yml` (the Database proof checks job's steps only) | the 47 cases; the job's wrong-marker refusal, migrations from zero, secret check and second-run refusal; proof: `test_identity_offline` (key files, settings, the schema check, the plan, the ledger and the capture) | X-keyfile, X-schema, LOG-a |
| 9. Sealed | `services/api/tests/test_identity_sealed_runtime.py`; `glow_api/` unchanged | the 4 sealed-runtime tests | D11-a |
| 10. The records | `docs/architecture/data-model.md`, `docs/architecture/production-contracts.md`, `docs/testing/p11-deferred-acceptance.md` (DB09), this record | — | — |

| Acceptance check | Identity case(s) and what the run of record printed | Reversals |
|---|---|---|
| 1. Sign-up | `signup.records_unverified_account`: "one user, one unverified address, one unverified account, one unknown age state"; `signup.one_transaction`: "the three rows carry one xmin"; `signup.failure_leaves_no_user`; no token pair and no `AccountSession` before verification (`signin.unverified_gets_no_session`) | D4-a, X-age, X-username |
| 2. Verification by code | `verify.activates_and_issues_pair`: "unverified to active (version 2, eligibility 2); one valid session"; `verify.wrong_code_refused`; `verify.expired_code_refused`: "15-minute limit: 895s:200, 905s:409"; `verify.used_code_refused` (410 on the old session, 409 signed in); `verify.attempt_limit`: "three attempts, then the process ends" | X-retry, D6-a, D6-b |
| 3. Enumeration and wrong-account linking | `enum.signup_taken_and_new_alike`, `enum.reset_unknown_and_known_alike` ("no mail to the unknown address"), `enum.email_change_taken_and_free_alike` ("wrong-account linking refused with B's own code"); `mail.no_link_no_stranger` | D3-a, D3-b, X-link |
| 4. Sign-in | `signin.records_account_session`: "valid at epoch, UserSession reference, 30 days, aligned expiry, AccountAccess valid"; `signin.reference_not_derived`; `signin.fails_closed` | D2-d, X-lifetime, X-access, D6-d, D7-a |
| 5. Refresh | `refresh.rotates`; `refresh.replay_ends_session`: "the replay ended its session at both layers; the current pair stopped"; `refresh.ended_session_refused_nothing_else`; `refresh.bad_tokens_refused_without_ending`: "five bad tokens refused; no session ended" (tampered, another key's signature, unsigned, expired, the wrong type) | D2-b, D2-c |
| 6. Expiry | `expiry.access_token`, `expiry.refresh_token`, `expiry.account_session`: "aligned: both layers stop at expires_at; Glow's own check refuses and marks the row" | D2-d, X-expire |
| 7. Logout | `logout.ends_at_once`: "access, refresh and the session key all refused at once"; `logout.second_layer_fails_then_repeat` | D2-a, D6-e |
| 8. Two devices | `devices.logout_one_leaves_other`, `devices.session_list_ends_other` (with its `session_revoked` event), `devices.session_list_current_logs_out`, `devices.password_change_ends_both` ("signed in again"), `devices.password_reset_ends_both` | D6-g, D6-h |
| 9. Suspension and `deletion_pending` | `revoke.suspend`, `revoke.delete`: "epoch bumped, both layers ended, events written, sign-in refused"; `revoke.inside_transaction_refused`; `revoke.second_layer_fails_then_repeat`; `revoke.suspend_after_delete_refused` | D6-c, D6-f, D7-b, D7-c |
| 10. The notices | `devices.password_change_ends_both` ("one notice"), `devices.password_reset_ends_both` ("one notice"), `notice.email_change` ("the old address told once") | D8-a |
| 11. The rate limit | `ratelimit.failed_sign_ins`: "five failures, then refused even with the right password" | X-ratelimit |
| 12. No secret in any output | the suite's scan: "clean (684 secrets held; 0 found in 217 log records and 98 writes)"; the job's own check: "the job's secrets found in the identity suite's output: 0" | LOG-a |

### The reversals and their failing output

| ID | The edit (file) | Run | Must fail | Result and failing output |
|---|---|---|---|---|
| D2-a | stateful validation off: logout no longer ends the access token (`glow_identity/conf.py`) | suite | `logout.ends_at_once` | **caught**, exit 1: `[identity] FAIL logout.ends_at_once (7) 0.3 s: FAILED: allauth's layer refuses it (stateful validation)`; also failed: `config.settings_as_briefed`, `refresh.replay_ends_session`, `expiry.account_session`, `logout.second_layer_fails_then_repeat`, `devices.session_list_ends_other`, `devices.password_change_ends_both`, `devices.password_reset_ends_both`, `revoke.suspend`, `revoke.delete`, `revoke.second_layer_fails_then_repeat`; restored |
| D2-b | the replay subclass removed: a replayed refresh token no longer ends its session (`glow_identity/strategy.py`) | suite | `refresh.replay_ends_session` | **caught**, exit 1: `[identity] FAIL refresh.replay_ends_session (5, D2) 0.5 s: FAILED: the session is revoked at Glow's layer`; restored |
| D2-c | the subclass reading sid before allauth's checks: a forged token ends a session (`glow_identity/strategy.py`) | suite | `refresh.bad_tokens_refused_without_ending` | **caught**, exit 1: `[identity] FAIL refresh.bad_tokens_refused_without_ending (5, D2) 0.3 s: FAILED: another key's signature ends no session`; also failed: `endpoints.refusals`; restored |
| D2-d | set_expiry not called: allauth's refresh outlives expires_at (`glow_identity/revocation.py`) | suite | `expiry.account_session`, `signin.records_account_session` | **caught**, exit 1: `[identity] FAIL expiry.account_session (6, D2, D6) 0.3 s: FAILED: aligned expiry`; restored |
| D3-a | ACCOUNT_EMAIL_UNKNOWN_ACCOUNTS back to its default: the reset for an unknown address raises (`glow_identity/conf.py`) | suite | `enum.reset_unknown_and_known_alike` | **caught**, exit 1: `[identity] FAIL enum.reset_unknown_and_known_alike (3) 0.3 s: FAILED: neither raises`; also failed: `config.settings_as_briefed`; restored |
| D3-b | Glow's account-already-exists message removed: the taken-address sign-up raises (`glow_identity/adapter.py`) | suite | `enum.signup_taken_and_new_alike` | **caught**, exit 1: `[identity] FAIL enum.signup_taken_and_new_alike (3) 0.5 s: FAILED: neither raises`; restored |
| D4-a | the AppAccount created outside save_user's transaction (`glow_identity/adapter.py`) | suite | `signup.one_transaction`, `signup.failure_leaves_no_user` | **caught**, exit 1: `[identity] FAIL signup.one_transaction (1, D4) 0.2 s: FAILED: the user, its account and its age state share a transaction`; restored |
| D6-a | the verified transition without its lock (`glow_identity/revocation.py`) | suite | `verified.waits_on_account_lock` | **caught**, exit 1: `[identity] FAIL verified.waits_on_account_lock (D6) 0.3 s: FAILED: the transition refused after the suspension committed`; restored |
| D6-b | the verified transition without its refusal (`glow_identity/revocation.py`) | suite | `verified.refuses_unless_unverified` | **caught**, exit 1: `[identity] FAIL verified.refuses_unless_unverified (D6) 0.5 s: FAILED: a suspended account is refused`; also failed: `verified.waits_on_account_lock`; restored |
| D6-c | a glow_chat call inside transaction.atomic() no longer refused by the revocation service (`glow_identity/revocation.py`) | suite | `revoke.inside_transaction_refused` | **caught**, exit 1: `[identity] FAIL revoke.inside_transaction_refused (9, D6) 0.3 s: FAILED: the revocation service refuses inside an atomic block`; restored |
| D6-d | the sign-in hook not ending allauth's session when open_session refuses (`glow_identity/adapter.py`) | suite | `signin.fails_closed` | **caught**, exit 1: `[identity] FAIL signin.fails_closed (4, D6) 0.6 s: FAILED: the sign-in answers 401`; also failed: `verify.transition_retried_at_sign_in`; restored |
| D6-e | the second layer failing, with the error and the repeat (logout: allauth's step first) (`glow_identity/adapter.py`) | suite | `logout.second_layer_fails_then_repeat` | **caught**, exit 1: `[identity] FAIL logout.second_layer_fails_then_repeat (7, D6) 0.3 s: FAILED: Glow's layer committed first`; also failed: `logout.ends_at_once`; restored |
| D6-f | the second layer failing, with the error and the repeat (suspension: a repeat stops at no change) (`glow_identity/revocation.py`) | suite | `revoke.second_layer_fails_then_repeat` | **caught**, exit 1: `[identity] FAIL revoke.second_layer_fails_then_repeat (9, D6) 0.3 s: FAILED: and completes allauth's`; restored |
| D6-g | ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE off (`glow_identity/conf.py`) | suite | `devices.password_change_ends_both` | **caught**, exit 1: `[identity] FAIL devices.password_change_ends_both (8, 10, D5, D6) 0.9 s: FAILED: the password change signs this device out`; also failed: `config.settings_as_briefed`; restored |
| D6-h | Glow's USERSESSIONS_ADAPTER removed: the session list's DELETE leaves the AccountSession valid (N1) (`glow_identity/conf.py`) | suite | `devices.session_list_ends_other` | **caught**, exit 1: `[identity] FAIL devices.session_list_ends_other (8, D6) 0.5 s: FAILED: its AccountSession is revoked`; also failed: `config.settings_as_briefed`, `devices.session_list_current_logs_out`; restored |
| D7-a | the actor class reading X-Session-Token instead of the token's own sid (`glow_identity/authentication.py`) | suite | `actor.uses_token_sid_not_header` | **caught**, exit 1: `[identity] FAIL actor.uses_token_sid_not_header (4, D5, D7) 0.7 s: FAILED: another member's session key in the header is ignored`; restored |
| D7-b | an account that is not active accepted (`glow_identity/authentication.py`) | suite | `actor.refuses_inactive_account` | **caught**, exit 1: `[identity] FAIL actor.refuses_inactive_account (D7) 0.5 s: FAILED: the account check refuses it`; restored |
| D7-c | a session at an old epoch accepted (`glow_identity/authentication.py`) | suite | `actor.refuses_stale_epoch` | **caught**, exit 1: `[identity] FAIL actor.refuses_stale_epoch (D7) 0.3 s: FAILED: the actor refuses a session at an old epoch`; restored |
| D8-a | a notice event not sent (password changed) (`glow_identity/adapter.py`) | suite | `devices.password_change_ends_both` | **caught**, exit 1: `[identity] FAIL devices.password_change_ends_both (8, 10, D5, D6) 0.9 s: FAILED: one password-changed notice`; restored |
| D11-a | the runtime importing glow_identity: the sealed-runtime test fails (`glow_api/urls.py`) | API `tests.test_identity_sealed_runtime` | `test_the_runtime_imports_none_of_the_identity_slice`, `test_no_runtime_module_names_the_identity_slice` | **caught**, exit 1: `FAIL: test_the_runtime_imports_none_of_the_identity_slice (tests.test_identity_sealed_runtime.IdentitySealedRuntimeTests.test_the_runtime_imports_none_of_the_identity_slice)`; restored |
| LOG-a | a code logged in one path (the log capture at DEBUG) (`glow_identity/messages.py`) | suite | `SECRET-SCAN` | **caught**, exit 1: `identity secret scan: FOUND (684 secrets held; 48 found in 275 log records and 98 writes)`; restored |
| X-phone | the phone refusal removed: allauth's default adapter raises for a signed-in member (`glow_identity/adapter.py`) | suite | `endpoints.refusals` | **caught**, exit 1: `[identity] FAIL endpoints.refusals (3, 4, threat model) 0.3 s: FAILED: GET /_allauth/app/v1/account/phone signed in answers 403`; restored |
| X-username | the opaque username removed: allauth copies the email's local part (`glow_identity/adapter.py`) | suite | `signup.records_unverified_account` | **caught**, exit 1: `[identity] FAIL signup.records_unverified_account (1) 0.2 s: FAILED: the username is opaque`; restored |
| X-age | the unknown age state not recorded at sign-up (`glow_identity/adapter.py`) | suite | `signup.records_unverified_account`, `signup.one_transaction` | **caught**, exit 1: `[identity] FAIL signup.records_unverified_account (1) 0.3 s: ERROR: DoesNotExist`; also failed: `signup.failure_leaves_no_user`; restored |
| X-retry | the verified transition not retried at sign-in (`glow_identity/revocation.py`) | suite | `verify.transition_retried_at_sign_in` | **caught**, exit 1: `[identity] FAIL verify.transition_retried_at_sign_in (2, 4, D6) 0.5 s: FAILED: the next sign-in succeeds`; restored |
| X-expire | an expired AccountSession found but not marked (`glow_identity/authentication.py`) | suite | `expiry.account_session` | **caught**, exit 1: `[identity] FAIL expiry.account_session (6, D2, D6) 4.7 s: FAILED: expire_session marked the row when found`; restored |
| X-link | a link in a message (`glow_identity/messages.py`) | suite | `mail.no_link_no_stranger` | **caught**, exit 1: `[identity] FAIL mail.no_link_no_stranger (3, D8) 0.0 s: FAILED: no link and no name but Glow's`; restored |
| X-access | AccountAccess carrying a field the contract does not define (`glow_identity/access.py`) | suite | `signin.records_account_session` | **caught**, exit 1: `[identity] FAIL signin.records_account_session (4, D2, D5) 0.5 s: FAILED: AccountAccess validates against the contract`; restored |
| X-ratelimit | the failed-sign-in rate limit off (`glow_identity/conf.py`) | suite | `ratelimit.failed_sign_ins` | **caught**, exit 1: `[identity] FAIL ratelimit.failed_sign_ins (11) 1.6 s: FAILED: the sixth is refused`; also failed: `config.settings_as_briefed`; restored |
| X-lifetime | a session lifetime other than 30 days (`glow_identity/conf.py`) | suite | `signin.records_account_session` | **caught**, exit 1: `[identity] FAIL signin.records_account_session (4, D2, D5) 0.5 s: FAILED: 30 days from sign-in`; also failed: `config.settings_as_briefed`; restored |
| X-pin | the allauth pin moved in the development input (`requirements-dev.in`) | API `tests.test_dependency_pins` | `test_sv1_pins_allauth_headless_in_the_development_scope_only` | **caught**, exit 1: `FAIL: test_sv1_pins_allauth_headless_in_the_development_scope_only (tests.test_dependency_pins.DependencyPinTests.test_sv1_pins_allauth_headless_in_the_development_scope_only)`; restored |
| X-keyfile | a key file readable by others accepted (`proof: glow_ordering_proof/identity_environment.py`) | proof `tests.test_identity_offline` | `test_each_refusal_names_the_variable_and_no_value` | **caught**, exit 1: `FAIL: test_each_refusal_names_the_variable_and_no_value (tests.test_identity_offline.IdentityKeyFileTests.test_each_refusal_names_the_variable_and_no_value) (name='PROOF_IDENTITY_SECRET_KEY_FILE', environ=['PROOF_IDENTITY_SECRET_KEY_FILE'])`; restored |
| X-schema | the schema check passing a keyword it does not apply (`proof: glow_ordering_proof/schema_check.py`) | proof `tests.test_identity_offline` | `test_an_unknown_keyword_is_an_error_not_a_pass` | **caught**, exit 1: `FAIL: test_an_unknown_keyword_is_an_error_not_a_pass (tests.test_identity_offline.SchemaCheckTests.test_an_unknown_keyword_is_an_error_not_a_pass)`; restored |

**The exact edits** (the helper replaced the first text with the second; paths under `services/api/` unless named):
- **D2-a** (`glow_identity/conf.py`): `"HEADLESS_JWT_STATEFUL_VALIDATION_ENABLED": True,` → `…: False,`
- **D2-b** (`glow_identity/strategy.py`): `session_key = replayed_session_key(refresh_token)` → `session_key = None`
- **D2-c** (`glow_identity/strategy.py`): `payload = internal.decode_token(refresh_token, "refresh")` → `payload = jwt.decode(refresh_token, options={"verify_signature": False, "verify_exp": False})`, so the replay check reads the token before allauth's checks
- **D2-d** (`glow_identity/revocation.py`): `request.session.set_expiry(expires_at)` → no call
- **D3-a** (`glow_identity/conf.py`): `"ACCOUNT_EMAIL_UNKNOWN_ACCOUNTS": False,` → `…: True,`
- **D3-b** (`glow_identity/adapter.py`): Glow's `send_account_already_exists_mail` deleted
- **D4-a** (`glow_identity/adapter.py`): the `AppAccount` and age-state writes moved out of `save_user`'s `transaction.atomic()` block
- **D6-a** (`glow_identity/revocation.py`): `AppAccount.objects.select_for_update().filter(pk=account_id).first()` → `AppAccount.objects.filter(pk=account_id).first()`
- **D6-b** (`glow_identity/revocation.py`): `if account.state != "unverified": return Outcome("refused", …)` deleted
- **D6-c** (`glow_identity/revocation.py`): `if connection.in_atomic_block or not connection.get_autocommit():` → `if False:`
- **D6-d** (`glow_identity/adapter.py`): `if opened: return response` → `return response`, keeping a sign-in that `open_session` refused
- **D6-e** (`glow_identity/adapter.py`): logout's two steps swapped, allauth's logout before `sign_out_current_session`
- **D6-f** (`glow_identity/revocation.py`): after `_checked(result)`, `if result.outcome == "no_change": return Outcome("no_change", …)` added, so a repeat stops before allauth's step
- **D6-g** (`glow_identity/conf.py`): `"ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE": True,` → `…: False,`
- **D6-h** (`glow_identity/conf.py`): the `"USERSESSIONS_ADAPTER": "glow_identity.sessions.GlowUserSessionsAdapter",` line deleted
- **D7-a** (`glow_identity/authentication.py`): before `actor_for`, the payload's `sid` replaced from the `X-Session-Token` header when one is sent
- **D7-b** (`glow_identity/authentication.py`): `if account.state != "active": raise …` deleted
- **D7-c** (`glow_identity/authentication.py`): `if session.epoch != account.session_epoch: raise …` deleted
- **D8-a** (`glow_identity/adapter.py`): `send_mail` returns early for `account/email/password_changed`
- **D11-a** (`glow_api/urls.py`): `import glow_identity` added
- **LOG-a** (`glow_identity/messages.py`): in `_code`, `logging.getLogger("glow_identity.messages").debug("code %s", code)` added
- **X-phone** (`glow_identity/adapter.py`): `def get_phone(` → `def _get_phone_reversed(`, so allauth's default applies
- **X-username** (`glow_identity/adapter.py`): `def populate_username(` → `def _populate_username_reversed(`
- **X-age** (`glow_identity/adapter.py`): the `age.OrmAgeAssurance().record(…)` call deleted
- **X-retry** (`glow_identity/revocation.py`): `retried = mark_verified(account_id)` and its log line → `pass`
- **X-expire** (`glow_identity/authentication.py`): `revocation.expire_found(session.pk)` → `pass`
- **X-link** (`glow_identity/messages.py`): the verification body's `{purpose}.` → `{purpose}: https://glow.invalid/v`
- **X-access** (`glow_identity/access.py`): `"email_verified": True` added to `AccountAccess`'s data
- **X-ratelimit** (`glow_identity/conf.py`): `"ACCOUNT_RATE_LIMITS": {"login_failed": None}` added
- **X-lifetime** (`glow_identity/conf.py`): `timedelta(days=30)` → `timedelta(days=1)`
- **X-pin** (`requirements-dev.in`): `django-allauth[headless]==65.21.1` → `==65.21.0`
- **X-keyfile** (`proofs/postgres-ordering/glow_ordering_proof/identity_environment.py`): `if status.st_mode & 0o077:` → `if False:`
- **X-schema** (`proofs/postgres-ordering/glow_ordering_proof/schema_check.py`): `if unknown:` → `if False:`

## The configured specification (D14)

- **Generated once**, on 9 November 2026, in a scratch virtual environment outside the checkout. Its input was `-c services/api/requirements-dev.lock`, `Django==5.2.17`, `djangorestframework==3.18.1` and `django-allauth[headless,headless-spec]==65.21.1`, which added PyYAML 6.0.3 there only.
- **Settings:** SV1's fragment, keys generated in-process, Django's dummy database, and one change: `HEADLESS_SERVE_SPECIFICATION = True`, so that allauth's builder could reverse its own route. SV1 serves no specification.
- **The script** called `allauth.headless.spec.internal.schema.get_schema()` and wrote `yaml.dump(spec, Dumper=yaml.Dumper)` (what `OpenAPIYAMLView` serves) and `json.dumps(spec)`. Two runs gave the same bytes.

| Form | SHA-256 | Bytes |
|---|---|---|
| YAML | `56d639eb5b1d997a99f24ca22ccce0b72bad124da0ea383763468085ddce6c35` | 95,752 |
| JSON | `212d6758d6d64eaed54870e2c1cf3870286ad31becf1e349c576a369c0d655ef` | 78,289 |

OpenAPI 3.0.3, 17 paths, all under `/_allauth/app/v1/`:

| Path | Methods |
|---|---|
| `account/email` | DELETE, GET, PATCH, POST, PUT |
| `account/password/change` | POST |
| `account/phone` | GET, POST |
| `auth/code/confirm` | POST |
| `auth/email/verify` | GET, POST |
| `auth/email/verify/resend` | POST |
| `auth/login` | POST |
| `auth/password/request` | POST |
| `auth/password/reset` | GET, POST |
| `auth/phone/verify` | POST |
| `auth/phone/verify/resend` | POST |
| `auth/reauthenticate` | POST |
| `auth/session` | DELETE, GET |
| `auth/sessions` | DELETE, GET |
| `auth/signup` | POST |
| `config` | GET |
| `tokens/refresh` | POST |

Nothing is vendored. The P11 plan's carry "the configured headless specification, if SV1 could not pin its SHA-256" is met by this section; the carry itself is the manager's to close.

## The threat model's inputs

### Every endpoint and its refusals

Unauthenticated: each request with no credential, from the case `endpoints.refusals`, and none returns a token. Signed in: the same case's second part, plus the cases named.

| Endpoint (`/_allauth/app/v1/…` unless named) | With no credential | Signed in, and the cases |
|---|---|---|
| `GET config` | 200 (public configuration) | — |
| `GET`, `DELETE auth/session` | 401 | the session's state; `DELETE` is logout at both layers (`logout.*`) |
| `POST auth/reauthenticate` | 401 | **required before an address is added, removed or marked primary** (correction C1, `ACCOUNT_REAUTHENTICATION_REQUIRED`): the password within the last 300 seconds, in the same session; a sign-in does not count. Without it, `account/email` answers 401 with the `reauthenticate` flow. A wrong password is refused (400 `incorrect_password`) and consumes the sign-in form's `login_failed` limit: the sixth within 300 seconds is refused `too_many_login_attempts`, and the sign-in form is held too. It records the reauthentication in the Django session only: no key change, no `UserSession` or `AccountSession` write, no token pair, no `session_token`, no sign-in hook (`reauth.email_change_needs_recent_reauthentication`) |
| `POST auth/code/confirm` (mounted whatever the configuration) | 409 (no pending flow) | 409 (login by code is off) |
| `POST account/password/change` | 401 | ends every session at both layers (`devices.password_change_ends_both`). **Its limit is `change_password` at `5/300s/user`** (correction C2, DM-48; allauth's default is 5/m/user): every signed-in request there counts, whatever its outcome; a wrong current password is refused (400 `enter_current_password`) and consumes no `login_failed`; after five, a sixth within 300 seconds, even with the right password, is refused 429 with no error code, and the password is unchanged (`ratelimit.password_change`) |
| `GET`, `PUT`, `PATCH`, `DELETE account/email` | 401 | the member's own address; a change is verified by code first (`notice.email_change`) |
| `POST account/email` | 409 | a taken and a free address answer alike (`enum.email_change_taken_and_free_alike`) |
| `GET account/phone` | 401 | **403**: Glow's `get_phone` refusal (`adapter.py:118-124`) where allauth's default raises (`X-phone`) |
| `POST account/phone` | 409 | **403** (the same refusal) |
| `POST auth/password/request` | 400 (empty body) | an unknown and a known address answer alike; no mail to the unknown (`enum.reset_unknown_and_known_alike`) |
| `GET`, `POST auth/password/reset` | 409 (no pending reset) | by code; ends every session (`devices.password_reset_ends_both`) |
| `POST auth/login` | 400 (empty body) | the failed-sign-in limit (`ratelimit.failed_sign_ins`); an unverified account gets a code, not a session (`signin.unverified_gets_no_session`); the sign-in fails closed (`signin.fails_closed`) |
| `POST auth/signup` | 400 (empty body) | a taken and a new address alike (`enum.signup_taken_and_new_alike`) |
| `GET`, `POST auth/email/verify`; `POST auth/email/verify/resend` | 409 (no pending verification) | wrong, expired and used codes; the attempt limit (`verify.*`); `email_taken` for another account's address |
| `POST auth/phone/verify`, `POST auth/phone/verify/resend` | 409 | no phone is configured |
| `POST tokens/refresh` | 400 (empty body, and a malformed token) | rotation, replay, ended sessions, bad tokens (`refresh.*`); expiry (`expiry.refresh_token`) |
| `GET`, `DELETE auth/sessions` | 401 | the member's own sessions only; `DELETE` ends at both layers through Glow's adapter (`devices.session_list_*`) |
| `GET /api/v1/account/access` (Glow) | 401, the contract's `Error` (`unauthenticated`) with `WWW-Authenticate: Bearer` | the owner's `AccountAccess`, only for an active account with a valid, current, unexpired session (`signin.records_account_session`, `actor.*`) |
| `POST /api/v1/account/access` | 401 | 405, `Error` `invalid_request` |

There are 18 routes: allauth's 17 for the `app` client, and Glow's one (`config.routes`). The browser client, the served specification, login by code's request routes, MFA, social login and the IdP are not mounted.

### Every token, code and key

| Secret | Where it lives | How it ends | Tests |
|---|---|---|---|
| Password | `auth_user.password`, Django's hasher; four validators, minimum length 10 | a change or reset ends every session at both layers; the new hash fails every other session's stored hash | `devices.password_change_ends_both`, `devices.password_reset_ends_both` |
| Verification code | allauth's flow state in the Django session; sent only in Glow's code message | used once; 900 s; three attempts, then the flow ends | `verify.*` |
| Password reset code | the same, in the reset flow's state | used once; 180 s, restarted once confirmed; three attempts | `devices.password_reset_ends_both`; the limits are allauth's and not exercised separately |
| **Session key** | `django_session.session_key` and `usersessions_usersession.session_key`; returned to the app as `meta.session_token` | the session ends (logout, `UserSession.end()`, a flush, or the aligned expiry). **Until then it is a bearer credential at every allauth endpoint** (`X-Session-Token`, read ahead of `sid`): the session list and an email change included; a password change also asks for the current password (`allauth/headless/account/inputs.py:171-182`) | `logout.ends_at_once` ("the session key … refused"), `verify.used_code_refused` (410), `actor.uses_token_sid_not_header` |
| Access token | the client only; RS256, 300 s; `sid` encrypts the session key (AES-CTR, a key from `SECRET_KEY`, a fresh initialization vector per token) | its expiry; with stateful validation, the moment its session ends or the password changes | `expiry.access_token`, `logout.ends_at_once`, `signin.reference_not_derived` (a fresh `sid` per token) |
| Refresh token | the client; its `jti` in `session["headless_refresh_tokens"]`; 30 days | rotation pops it; a replay ends the whole session at both layers; it dies with its session | `refresh.*`, `expiry.refresh_token` |
| JWT signing key | an RSA key of 2048 bits, generated for each CI run into a file (mode 0600, `O_EXCL`) in the job's temporary directory, never in a variable or the log; per process in the API tests; P11 supplies it | the run's end (the directory is removed) | the job's secret check; the suite's scan; `X-keyfile` |
| Identity `SECRET_KEY` | generated per run (`token_hex(32)`, masked), read from a file | the same | the same |
| Database password, markers | P06.DB's, unchanged; the identity database has its own marker | the same | the job's wrong-marker and second-run refusals |

**Not secrets, but personal data:** `UserSession.ip` and `user_agent` for each sign-in (activity tracking off), and the auth user's email and opaque username, which the headless payload returns to the member. Their retention and export are P08's (carried).

### Every revocation path, at both layers

| Path | Glow's layer, first (`glow_chat`, its own transaction) | allauth's layer, after | Repeatable | Tests and reversals |
|---|---|---|---|---|
| Logout (`DELETE auth/session`) | `sign_out` for this session (`revocation.py:191-201`) | allauth's logout (flush) | yes | `logout.ends_at_once`, `logout.second_layer_fails_then_repeat`; D2-a, D6-e |
| The session list (`DELETE auth/sessions`) | `sign_out` for each chosen row's `AccountSession` (`sessions.py:21-24`, `revocation.py:217-222`) | the row's `end()`; the current one chosen: allauth's logout | yes | `devices.session_list_ends_other`, `devices.session_list_current_logs_out`; D6-h |
| Password change | `sign_out` for every valid session of the account (`adapter.py:112-114`, `revocation.py:204-214`) | the new hash; the current session logged out (`ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE`) | yes | `devices.password_change_ends_both`; D6-g, D8-a |
| Password reset (by code) | the same | the new hash | yes | `devices.password_reset_ends_both` |
| A replayed refresh token | `sign_out` for its session (`strategy.py:42-49`, `revocation.py:225-234`) | `UserSession.end()` (or the Django session deleted if no row remains) | yes | `refresh.replay_ends_session`; D2-b, D2-c |
| Suspension, `deletion_pending` | `suspend` or `delete`: the epoch bumped, `access_revoked` and `session_epoch_bumped` written, and for deletion the job and tombstone (`revocation.py:254-273`) | every `UserSession.end()`, then the auth user made inactive | yes: a repeat is "no change" and runs the second step again | `revoke.*`; D6-c, D6-f |
| Expiry | the actor refuses past `expires_at` by the database's clock and marks the row (`expire_session`) | the Django session expires at the same instant (`set_expiry`) | — | `expiry.*`; D2-d, X-expire |
| A sign-in `open_session` refuses | nothing to revoke: no row was made | the sign-in's `UserSession` deleted and the session flushed in the same request; a new response with no token (`adapter.py:93-104`, `revocation.py:169-176`) | — | `signin.fails_closed`; D6-d |
| Between the two commits | the actor already refuses the revoked `AccountSession` | allauth's session still alive | — | `actor.refuses_revoked_session_between_layers` |

### The review plan's security focus, point by point

- **Endpoints, tokens, the session reference, revocation, the actor:** the tables above.
- **Enumeration and rate limits:**
  - a sign-up, a reset and an email change answer alike for a taken and a free address (acceptance check 3);
  - **the narrow window:** allauth's `confirm_email` limit (one verification mail per address per 10 seconds) answers 429 to a sign-up or email change naming an address mailed within those 10 seconds (`email_verification.py:169-187`). A new address cannot be in that state unless someone just used it, so the 429 can tell a prober that an address was mailed in the last 10 seconds;
  - a correct-password sign-in of an unverified address inside the window is refused (400) rather than sent a code: it needs the password, so it tells nobody else anything;
  - the cases clear the cache between them so that each starts outside every window.
- **The mail adapter and what a message reveals:**
  - plain text, Glow's name only, no link and no tracking;
  - a code message holds the code and its expiry;
  - a notice names neither address, nor the IP or device that allauth's context offers;
  - **an email change to a taken address sends the code to that address's owner** (the installed release does so, to answer alike): the owner receives a code they did not ask for, worded "If you did not ask for this, you can ignore this message", and the code cannot link the address to the asking account (`email_taken`).
- **The seal:** `test_identity_sealed_runtime.py` and `D11-a`.
- **G-13 (a restored token):** a copied refresh token is a bearer credential until its session ends. If the copy is used first, the member's next refresh is the replay that ends the session at both layers, so the copy's pair stops too (`refresh.replay_ends_session`). Neither G-13's WebAuthn server part nor its native part is built (D13).
- **G-14 (a review path):** none is built. The fixture backend, the synthetic `@example.invalid` accounts and every setting exist only under the proof's identity settings on a disposable database: none can reach a real member. A reviewer account signs in with email and password, since login by code and MFA are off.
- **The proof's secret handling:**
  - the two keys are files in the job's protected temporary directory; the `SECRET_KEY` and the markers are masked before anything prints;
  - the job checks the suite's output for its passwords, markers, `SECRET_KEY` and every body line of the signing key, and shows the output only if none is there and the suite's own scan reported clean;
  - the suite's ledger holds every code, password, session key, token and token part it handled (684), and checks them against every log record at `DEBUG` and every write.
- **The session key in `UserSession` and `django_session`:** a credential, stored only by allauth and Django; Glow never stores, hashes or logs it (`actor_for` deletes its local copy at once, `authentication.py:74`). P08's export must exclude it.
- **The `sid`'s encryption under `SECRET_KEY`:** unauthenticated AES-CTR inside a signed token. Anyone holding `SECRET_KEY` can read the session key from any token, and rotating `SECRET_KEY` makes every outstanding token's `sid` unreadable (P11's key handling).
- **A replayed rotated refresh token:** refused but not ended in 65.21.1. Glow's subclass ends the session at both layers after allauth's own checks, its signature first, and adds no cryptography (`D2-b`, `D2-c`).
- **allauth's own endpoints, which only allauth's layer guards:** the aligned expiry (`D2-d`) and the second step of every revocation path; each path's repeat completes it.
- **The `verified` transition's locks and no outer transaction:** `verified.waits_on_account_lock` (it waited on `transactionid`/`ShareLock`, blocked by the holder's pid); `verified.refuses_unless_unverified`; `revoke.inside_transaction_refused` (an atomic block and autocommit off); the static test that each revocation entry point starts with `require_no_transaction()`; no `ATOMIC_REQUESTS`.
- **The two link-building mails:** `D3-a` and `D3-b`.
- **The session list through Glow's adapter:** `D6-h`.
- **`ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE`:** `D6-g`.
- **The actor's use of allauth's internal `sid` decryption:** `allauth.headless.tokens.strategies.jwt.internal.session_key_from_sid`, an internal function of the pinned release. `actor.uses_token_sid_not_header` and `D7-a` hold its behaviour, and an allauth upgrade re-checks it.

## Glow's wording

`glow_identity/messages.py` words every message allauth asks the adapter to send. A message Glow has not worded is refused (`UnwordedMessage`), so no template of allauth's is ever rendered.

| allauth's prefix | Subject | Body, in short |
|---|---|---|
| `email_confirmation_signup` | Your Glow verification code | the code; "It expires in 15 minutes. Enter it in the Glow app to finish creating your account." |
| `email_confirmation` | Your Glow verification code | the same, "to confirm this address" |
| `password_reset_code` | Your Glow password reset code | the code; "It expires in 3 minutes"; "Your password has not changed." |
| `account_already_exists` | Your Glow account | someone tried to create an account with this address; sign in, or reset from the sign-in screen |
| `password_changed` | Your Glow password was changed | every device was signed out; reset advice |
| `password_reset` | Your Glow password was reset | every device was signed out |
| `email_changed` (to the old address) | Your Glow email address was changed | Glow will no longer send messages about the account to this address; names neither address |
| `password_set`, `email_deleted` | worded, unreachable in SV1 | every member has a usable password; with `ACCOUNT_CHANGE_EMAIL` an account holds one address |

These six of allauth's templates are never sent: `unknown_account`, `password_reset_key`, `login_code`, `base_message`, `base_notification` and `email_confirm`. The API test accounts for each one. The wording is SV1's; the members' final copy is a product decision before P11 sends mail.

## Commands and results

Every command ran in the clean environment above. Each is **iteration, not evidence**. The results are from the final runs on the code head's code (`46fbd37`), after the reversal re-run.

| Command | Result |
|---|---|
| `python3.12 -m venv .venv`; `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock` (in `services/api`, and in `proofs/postgres-ordering`) | exit 0 |
| `.venv/bin/python -m pip check` (both) | `No broken requirements found.` |
| `GLOW_ENV=test .venv/bin/python manage.py check` | `System check identified no issues (0 silenced).` |
| `GLOW_ENV=test .venv/bin/python manage.py test tests --verbosity 2` | `Ran 449 tests in 17.102s` … `OK` (422 before; 27 new) |
| `GLOW_ENV=test .venv/bin/python smoke.py` | `PASS /health/live: HTTP 200`, `PASS /health/ready: HTTP 503`, `PASS /api/v1/development/recommendations: HTTP 200` |
| `.venv/bin/ruff check .` | `All checks passed!` |
| `.venv/bin/ruff format --check .` | `99 files already formatted` |
| `.venv/bin/mypy` | `Success: no issues found in 57 source files` |
| `GLOW_ENV=test .venv/bin/python -m glow_persistence.static_check` | `Static definitions agree: 35 app models; migrations=0001_event_infrastructure,0002_app_domain,0003_chat_identity_read_cursor,0004_account_age_state` |
| `PYTHONPATH=. .venv/bin/python -m unittest discover -s ../../packages/contracts/tests -v` | `Ran 39 tests in 0.520s` … `OK` |
| In `proofs/postgres-ordering`: `.venv/bin/python -m unittest discover -s tests -t . -v` | `Ran 175 tests in 13.024s` … `OK` (160 before; 15 new) |
| In `proofs/postgres-ordering`: `.venv/bin/ruff check .`; `ruff format --check .`; `mypy` | `All checks passed!`; `51 files already formatted`; `Success: no issues found in 51 source files` |
| The three `uv pip compile` commands (above) | exit 0 each; each lock checked by package, version and hash against its earlier copy |
| Migration 0004: `GLOW_ENV=test .venv/bin/python -c "…"`, calling `makemigrations glow_persistence --name account_age_state` inside `glow_persistence.static_check`'s `no_database_access()` after `setup_static_registry()`; then the generated header removed and Ruff's import order and format applied | `0004_account_age_state.py`, SHA-256 `8af86a28d73fb9420b3ec6d59e6c1dcb47dc23c4f21e3c34a2830b171fc1866b` (pinned since correction C2 in `test_migration_0003_is_additive_and_0001_0002_are_unchanged`'s `pinned` dictionary; corrected by the manager, "Manager verification of correction C2") |
| The trusted classifier: `git show dc3e551:scripts/change_scope.py` to the scratch directory (SHA-256 `b564c62f4a076f51…`), then `python3 -I … --base dc3e551… --head <head> --merge-base`, for `46fbd37` and again for `269ac3b` | `{"full": true, "reason": "behavior-or-empty", …}`, 41 paths, both times |
| The configured specification (above) | two identical generations, with the hashes above |
| **Local database runs** (P06.DB's D4): see below | the final baseline on `46fbd37`: `identity suite exit 0 in 33 s`, `[identity] cases: 47/47 passed in 32.3 s`, `identity secret scan: clean (684 secrets held; 0 found in 217 log records and 98 writes)`, `IDENTITY VERDICT: PASS`; then the 33 reversals above |

**How the local database runs were made:**
- a throwaway PostgreSQL 17.11 in Docker, from the job's image `postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`, published on `127.0.0.1:5433` only;
- a generated password, each database's own marker, and none of the forbidden names present;
- a new container for every run, followed by `migrate`, `makemigrations --check --dry-run` and the suite.

Before the push, the job's SV1 step scripts also ran locally once: the migrations, `No changes detected`, the suite, and the second run's refusal with every count unchanged.

## The run of record

**Push run [42578800951](https://github.com/amthorn78/glow-dating-app/actions/runs/42578800951)** (Foundation, run 907, attempt 1) on `269ac3bf6a275b064ddd4ec772cd15b1cbce4506`, the code head.
- `completed`, conclusion `success`, 07:21:16 to 07:30:04 UTC on 9 November 2026.
- Read with the GitHub tools: the job list, each job's steps, and every job's log. The logs came from the run's log archive, downloaded to the scratch directory and searched there.

| Job | Result | Detail |
|---|---|---|
| Change scope | success | the push's comparison base is `46fbd37`: `{"full": true, "reason": "behavior-or-empty", "paths": ["proofs/postgres-ordering/requirements.in"]}` |
| API checks | success | the policy tests (`Ran 14 tests`, `Ran 18 tests`, both `OK`); `System check identified no issues (0 silenced).`; **`Ran 449 tests in 16.874s` … `OK`**; `All checks passed!`, `99 files already formatted`, `Success: no issues found in 57 source files`; the contracts suite `Ran 39 tests in 0.541s` … `OK` |
| Mobile checks | success | `@glow/contracts` `ℹ tests 586`, `ℹ pass 586`, `ℹ fail 0`; `@glow/mobile` `ℹ tests 691`, `ℹ pass 691`, `ℹ fail 0`; `Dependencies are up to date`; `iOS Bundled … (1370 modules)`, `Android Bundled … (1369 modules)`, `Exported: .work/native-export`; the rendered suite `104 passed (5.1m)`; the job took 8 min 5 s |
| API mobile smoke | success | `ℹ tests 1`, `ℹ pass 1`, `ℹ fail 0` |
| API artifact checks | success | `built-image loopback smoke passed` |
| Stream proof checks | success | `Ran 648 tests in 47.365s` … `OK`; `All checks passed!`, `59 files already formatted`, `Success: no issues found in 57 source files`; `run plan: fits` |
| Database proof checks | success | 8 min 31 s of its 30 minutes; the steps below |
| Foundation gate | success | **`Application checks passed`** |

**The Database proof checks job, step by step:**
- **The proof's offline checks:** `Ran 175 tests in 12.612s` … `OK`; `All checks passed!`, `51 files already formatted`, `Success: no issues found in 51 source files`.
- **Setup:** the credentials step, which now also makes the identity marker, `SECRET_KEY` and signing key; PostgreSQL 17.11 by digest; the role and its two databases.
- **The ordering database:**
  - `wrong-marker migrate exit status: 1`, with the marker refusal;
  - `dbshell exit status: 1`;
  - the migrations from zero, `glow_persistence.0004_account_age_state... OK` among them, then `No changes detected`.
- **The ordering suite:**
  - `[reference] cases: 56/56 passed`, `[adapter] cases: 115/115 passed`, `[read] cases: 62/62 passed in 16.8 s`;
  - `== VERDICT: PASS (reference) ==`, `== VERDICT: PASS (adapter) ==`, `== VERDICT: PASS ==`;
  - its second run refused (`second run exit status: 1`), with every count unchanged.
- **SV1, step 18:**
  - `identity migrate with the ordering database's marker: exit status 1`, refused by the marker;
  - then the reviewed migrations from zero on `glow_identity_proof`: allauth's `account` 0001 to 0009, `sessions`, `usersessions.0001_initial` and `glow_persistence` 0001 to 0004;
  - then `No changes detected`.
- **Step 19:**
  - first the job's own check: `the job's secrets found in the identity suite's output: 0` and `the suite's own scan reported clean: True`;
  - then the suite's output: 47 `[identity] PASS` lines, `[identity] cases: 47/47 passed in 38.1 s`, `identity secret scan: clean (684 secrets held; 0 found in 217 log records and 98 writes)` and `IDENTITY VERDICT: PASS`;
  - then **`identity phase: 38 s (the job's timeout is 30 minutes)`**.
- **Step 20:**
  - `rows (auth users, app accounts, account sessions, outbox events, user sessions) before: 51 51 58 32 45; after: 51 51 58 32 45`;
  - `second identity run exit status: 1`;
  - `refusal: refusing a used database: auth users exist; app accounts exist; outbox events exist. The identity suite runs once per new database.`
- **Steps 21 and 22:** the artifacts `sv1-identity-results` (13657270156) and `p06-db-proof-results` (13657041061).
- **Step 23:** `container removed: glow-proof-db-42578800951-1`, then `no proof container remains`.

The 47 case lines are word for word those of the earlier run below, apart from timings, process IDs and poll counts. The acceptance-check table above quotes them.

**Toolchain retry:** none fired. In the API, smoke, Stream proof and Database jobs, the first `actions/setup-python` attempt succeeded, and both DM-41 retry steps were `skipped`.

**No secret in the job's log** (acceptance check 12):
- in every job's log, the only masked values (`***`) are `actions/checkout`'s `token` input and its credential configuration line, as in every Foundation run;
- no log holds private-key text;
- the `::add-mask::` commands appear only in the step's script;
- the identity suite's output was printed only after the job's own check passed.

**The earlier run, [42575311159](https://github.com/amthorn78/glow-dating-app/actions/runs/42575311159)** (Foundation run 906), on `46fbd37`. Its tree differs from the code head by the one comment.
- Every job `success`, and `Application checks passed`.
- The same counts:
  - API `Ran 449 tests in 16.227s`;
  - proof `Ran 175 tests`;
  - Stream proof 648;
  - mobile 586 and 691, and `104 passed (5.1m)`;
  - the ordering verdicts PASS (`[read] cases: 62/62 passed in 18.2 s`).
- **The identity suite:** `47/47 passed in 38.2 s` and the identity phase 39 s. The scan was clean (684 held; none found in 217 records or 98 writes), and the second identity run was refused with the same counts.
- No retry. Its Database job took 8 min 9 s.
- **Its scope:** Change scope classified it with no comparison base (`missing-or-invalid-comparison`), because the push created the branch. That runs full checks.

## What could not run, and limits

- **Nothing reaches the runtime** (D1, D11): no route, setting, key or mail provider. The proof drives the endpoints in process with Django's test client, so there is no real HTTP transport, proxy, TLS, client IP or second worker. The rate limits use a local-memory cache.
- **No real mail and no provider:** the fixture backend refuses any network send.
- **Harness writes:** the inactive-account refusal (`actor.refuses_inactive_account`) moves the account's state alone, and the stale-epoch refusal (`actor.refuses_stale_epoch`) bumps the epoch alone. No reviewed operation makes either state on its own, and in every state the app makes, another check decides first.
- **No `session_expired` event on natural expiry.** allauth's layer refuses an expired session first, at the aligned expiry, so the actor never finds the row. It stays `valid` past `expires_at`, and no `session_expired` event is written. Readers check `expires_at`, but a consumer of `session_expired` needs a sweep, or another trigger, before relying on that event. The case shows the actor's own check, and the marking, through a harness write of `expires_at`.
- **The reset code's own limits** (attempts and expiry) are allauth's and not exercised separately.
- **The suspension case** requires the refused sign-in to answer 400 or 401 with no access token; it does not pin which of allauth's two refusals answers.
- **Local database runs** used Docker's daemon, started by the session. Docker Hub refused the image pull twice (429, its anonymous limit), and the third attempt succeeded, so local runs began late. Every local run is iteration, not evidence.
- **The configured specification** came from a scratch environment with PyYAML. SV1's own environments do not have PyYAML.

## Deviations, findings and the stop rule

**The stop rule:** nothing met it.
- No owned path needed changing outside the brief's list. `git diff --name-only dc3e551 269ac3b` lists 41 paths, each owned. In the workflow, every hunk is inside the `database` job.
- No new package beyond allauth, `cryptography`, `cffi` and `pycparser`, and PyJWT stayed at 2.15.0.
- The installed release matched the brief's facts.
- No design change.
- The seal holds.
- The Database proof checks job took 8 min 31 s of its 30 minutes in the run of record (the identity phase 38 s), and 8 min 9 s in `46fbd37`'s run (39 s).

**Deviations:**
- **`get_phone` refused (403):** an addition beyond the brief's adapter list. allauth 65.21.1 mounts `account/phone` whatever the configuration, and its default adapter raises `NotImplementedError` there for a signed-in member: a server error. Glow's adapter refuses instead, and `_has_phone_impl` still sees no phone implementation. Test `endpoints.refusals`; reversal `X-phone`.
- **The comment correction:** `46fbd37`'s `proofs/postgres-ordering/requirements.in` named a test file that does not exist (`tests/test_identity_pins.py`). The check is `tests/test_django_pin.py`'s `test_the_identity_suites_pins_are_the_apis`. `269ac3b` corrects the comment and nothing else; its run is the run of record, and `46fbd37`'s run is recorded beside it.
- **uv 0.11.32** compiled the locks. `services/api/README.md` says they were generated with uv 0.12.17, which this environment's toolchain does not have; adding uv 0.12.17 to `scripts/bootstrap-toolchain.sh` is a known follow-up. Each lock was checked by package, version and hash against its earlier copy and PyPI.
- **The reversal list goes beyond the prompt's:** the twelve `X-` reversals are additions; the prompt's 21 are all there (`D2-a` to `LOG-a`).

**Findings for the manager:**
- **An email change needs no reauthentication** (`ACCOUNT_REAUTHENTICATION_REQUIRED` keeps its default, off). A holder of a live session key or access token can move the account's address, after a code to the new address. This is for P11's and the threat model's decision.
- **The 10-second enumeration window** and **the missing `session_expired` on natural expiry**, both above. The second matters to SV4 or any consumer of that event.
- **The headless payload** returns the auth user's id, email and opaque username to the member: their own data, from allauth's response.
- **The `password_set` and `email_deleted` notices** are worded but unreachable in SV1.
- **A confirmed password-reset code also verifies the address**, outside the adapter (`verify_email_indirectly`). For an `unverified` account, the `verified` transition then happens at the next sign-in, by the retry `verify.transition_retried_at_sign_in` exercises.
- **Two records sections outside SV1's owned text** still read as before SV1: the data model's opening paragraph and the contract's opening "Not implemented" line. They were left unchanged.

## Manager verification (App Manager 10, 9 November 2026)

**The diff.** `git diff dc3e551 157c1f6` was read whole: 45 paths, each owned by the brief (41 to the code head, then the records commit, Markdown only).
- `glow_chat`, `glow_api` and the runtime `requirements.in` and `requirements.lock` are unchanged.
- Every workflow hunk is in the Database proof checks job.
- The development lock adds exactly `django-allauth` 65.21.1, `cryptography` 50.0.2, `cffi` 2.1.1 and `pycparser` 3.12, and removes nothing.
- Read against the brief:
  - the replay check runs allauth's `decode_token`, `get_token_session` and `validate_token_user` before its `jti` check (N2's order);
  - the actor takes the session from the token's own `sid`;
  - every revocation entry point begins with `require_no_transaction()`;
  - `save_user` writes the user, its account and its age state in one transaction.

**Classification.** The trusted classifier from `main` (`da92f1f`), run with `python3 -I` and `--base da92f1f… --head 157c1f6… --merge-base`, returned:
- full scope, `behavior-or-empty`;
- 64 paths: the PR's whole diff, the records since PR41 included;
- one merge base, `8d2de72`.

**Re-runs.** These ran in a scratch copy of the code head's whole tree (`git archive 269ac3b`), in the clean environment, with hash-locked installs:
- API: `Ran 449 tests` … `OK`; Ruff clean; mypy `no issues found in 57 source files`;
- the proof's offline tests: `Ran 175 tests` … `OK`; `pip check` clean.

The manager runs no database test locally.

**Three reversals, re-run offline.** Each failed as it should:
- **R1:** `glow_api/urls.py` imports `glow_identity`. The two sealed-runtime tests fail.
- **R2:** the actor reads the `X-Session-Token` header. The static guard in `test_identity_offline` fails.
- **R3:** the replay check decodes without verifying the signature. The order test fails.

Each file was restored, its hash checked, and the affected tests pass again.

**The run of record**, read with the GitHub tools: push run 42578800951 on `269ac3b`.
- All eight jobs `success`, and the gate printed `Application checks passed`. Both DM-41 retry steps were `skipped`.
- The second identity run was refused, with the counts `51 51 58 32 45` unchanged.
- The artifact `sv1-identity-results` is 3,717 bytes, and the cleanup removed the container.

The records push run 42580044628 on `157c1f6` classified ordinary documentation.

**For the review's focus (the manager's own read).**
- The results upload runs `if: always()`, so it also uploads after a failed secret check.
- Its JSON holds:
  - the server facts and the applied migrations;
  - each case's id, checks, verdict, time and detail line;
  - the counts.

  That is the text the job prints, but only after its own check passes.
- The values are synthetic and live for one run, on a database the job destroys.

**Triage** (step 6's rule; DM-23; DM-31 3.4):

| Item | Disposition |
|---|---|
| **An email change needs no reauthentication** | **Goes to the Dev Manager before the exact-head review (DM-47).** The brief's D3 names no reauthentication, so the prompt did not ask for it, although DM-45 section 9 approved email change as needing "`ACCOUNT_CHANGE_EMAIL = True` … and reauthentication" (AM10-06). It is on a security boundary (authorization): a holder of a live access token, refresh token or session key can move the address, then reset the password from it. The proposed correction is `ACCOUNT_REAUTHENTICATION_REQUIRED = True`, with its cases and a reversal. **Codex** raised the same gap on PR42's head `6b8c958` as its only finding (P1, `glow_identity/conf.py:93-94`), asking for the same fix and a case outside the window; C1 answers it |
| No `session_expired` on natural expiry | The brief's rule is met: "`expire_session` marks an expired row when it is found". **Carried to SV4**, whose system `logout` follows `session_expired` (the carried-items file) |
| The 10-second window (allauth's `confirm_email` limit) | Recorded in the threat model; for the review's focus |
| A confirmed reset code verifies the address outside the adapter | The next sign-in's retry takes `verified` (`verify.transition_retried_at_sign_in`); for the review's focus |
| The headless payload; `password_set` and `email_deleted` | Recorded: the member's own data; worded, but unreachable in SV1 |
| Two opening texts left as before SV1 | Updated by the manager in this batch: the data model's opening paragraph and the contract's "Not implemented" line |
| The phone refusal (403) | Accepted. It replaces a server error with a refusal, has a test and a reversal (`X-phone`), and changes no design. For the review's focus |
| The comment commit `269ac3b` | Accepted; the run of record is on it |
| uv 0.11.32 | Accepted. Each lock was checked by package, version and hash. Both READMEs' version sentences are corrected in this batch; uv 0.12.17 in the toolchain is already the hardening item's (`claude-setup-optimization.md`; DM-17) |
| The configured specification's hashes | The P11 plan's carry is closed in this batch |
| The twelve `X-` reversals | Accepted, as additions |

## Correction C1

- **Session:** correction C1 of SV1 (DM-47), started by Nathan from the C1 prompt, revision 1, at `c289424e27518187cb27d763e9945e298d6bf101` of the manager branch. Branch `claude/stoic-franklin-ief71e`.
- **Code head:** `bda299e3034121b2cc20318024f35f5938f83b4c`. **Records:** the commit after it (the data model's sentence and this record).
- **Specification:** the brief's "Correction C1", revision 4 (DM-47 C1.1 to C1.4).
- **Local runs are iteration, not evidence.** The run of record is CI's push run below.

### Start gate and environment

**The environment check (names only):**
- None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` is set.
- No `STREAM_*` or `PG*` name is set.
- `GH_TOKEN` and `GITHUB_TOKEN` are present, and were never read.
- Toolchain: `python3.12 --version` printed `Python 3.12.14`, and `docker --version` printed `Docker version 29.9.2, build a82e528`.
- Docker's daemon was not running. The session started `dockerd` itself, for the throwaway databases only.
- Every repository command ran in `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only its own variables (`GLOW_ENV=test` for the API). The installs also got the proxy and CA variables, passed by reference.

**The start gate:** every check passed.

| Check | Result |
|---|---|
| `git rev-parse HEAD` after `git switch -C claude/stoic-franklin-ief71e c289424…` | `c289424e27518187cb27d763e9945e298d6bf101` |
| `c289424` on the live manager branch | an ancestor of `origin/claude/magical-wozniak-yfmmx2`, which was at `c289424` itself |
| non-Markdown changes under `.github scripts services apps packages proofs` from `269ac3b` to `HEAD` | none |
| the owned paths changed on the manager branch after `c289424` | none |
| `grep -c -E '^#+ Correction C1'` in this record | `0` |
| `grep -c 'ACCOUNT_REAUTHENTICATION_REQUIRED'` in `conf.py` | `0` |

### What allauth 65.21.1 showed at `auth/reauthenticate`

This was read in the installed wheel (`services/api/.venv`, from the hash-locked development lock) and confirmed by the new case. **Nothing met the stop rule.**

**The route:**
- `headless/account/urls.py:19-23` mounts `ReauthenticateView`.
- `headless/account/views.py:577-586`: the view is rate-limited `reauthenticate` (`10/m/user`, `account/app_settings.py:295`). It is an `AuthenticatedAPIView` (`headless/base/views.py:57-63`), and its `post` calls `flows.reauthentication.reauthenticate_by_password` and returns `AuthenticationResponse`.

**The password check:**
- `account/forms.py:708-712`: `ReauthenticateForm.clean_password` calls the adapter's `reauthenticate`.
- That is `account/adapter.py:830-846`, which calls `self.authenticate` (`:805-825`).
- `authenticate` calls `pre_authenticate` (`:794-803`), which consumes `login_failed`. The key is the member's address (`:768-773`), and the consumption is rolled back only on success.
- Glow's adapter overrides none of these three (`test_an_address_change_needs_a_recent_reauthentication`).
- So a wrong password consumes the sign-in form's limit, as DM-47 read.

**What it writes:**
- `account/internal/flows/reauthentication.py:31-34`: `reauthenticate_by_password` calls only `record_authentication(..., method="password", reauthenticated=True)`.
- `account/internal/flows/login.py:39-83`: that writes two keys into `request.session` and sends `authentication_step_completed`. Nothing in allauth's installed apps or in `glow_identity` connects a receiver to that signal.

**The session key:** not cycled.
- There is no `cycle_key` in the path.
- `headless/internal/authkit.py:51-81`: the request's session is the one the token's `sid` names. It is saved under the same key when modified.
- The case shows the token's key unchanged, the Django session still there, no Django session made or ended, and the same `UserSession` row.

**The token pair:** none.
- `authkit.py:83-95`: `expose_access_token` returns nothing when the user before the request (`_pre_user`, `:70`) is the user after it.
- The case shows no `access_token` or `refresh_token` in the reply, and the reply's `meta` holds only `is_authenticated`.

**Glow's sign-in hooks:** not run.
- Neither `login` nor `post_login` is called.
- `user_logged_in` is sent only from allauth's `post_login` (`account/adapter.py:576`), so `usersessions`' receiver (`usersessions/apps.py:22`, `signals.py:16-19`) does not run.
- Glow's `post_login` (`glow_identity/adapter.py:93-104`), and through it `revocation.open_sign_in_session` (`revocation.py:126`), does not run either.
- The case shows that neither the `UserSession` row nor the `AccountSession` is written: their `xmin` is unchanged.

**`session_token`:** none.
- `headless/internal/sessionkit.py:24-35`: `expose_session_token` returns the key only if it differs from the request's.
- For a bearer request, the request's key is the token's `sid` (`tokens/strategies/jwt/strategy.py:20-27`).
- So **no deviation**: N3 stands as DM-47 read it.

**The guard:**
- `account/internal/flows/manage_email.py:22-23`, `:58-59` and `:82-83`: `delete_email`, `add_email` and `mark_as_primary` each open with `raise_if_reauthentication_required`.
- `reauthentication.py:75-80` and `:91-107`: the check reads the setting through the adapter (`account/adapter.py:1086-1096`). It counts only records with `reauthenticated`, so a sign-in's own record does not count, and it compares `time.time()` with `REAUTHENTICATION_TIMEOUT`, 300.
- `headless/base/views.py:34-35` answers `ReauthenticationRequired` with `ReauthenticationResponse`, a 401 (`headless/base/response.py:134-136`).
- Verifying the new address by code (`email_verification.py:65-84`) is not guarded. So the change completes at `auth/email/verify` once it has been asked for.

**What the 401 carries, as the run showed:**
- `flows` lists `reauthenticate`, and also `password_reset_by_code` with `is_pending: false` (`headless/base/response.py:79-94`). Nothing is pending.
- The case checks that `reauthenticate` is listed and that nothing is pending, not that it is the only flow.

### Item 1: reauthentication before an address change (D3; acceptance check 13)

**Files:**
- `services/api/glow_identity/conf.py`: `"ACCOUNT_REAUTHENTICATION_REQUIRED": True`, after `ACCOUNT_CHANGE_EMAIL`, with allauth's default timeout.
- `services/api/tests/test_identity_offline.py`:
  - the fragment test's expected values gain the setting;
  - the fragment sets no `ACCOUNT_REAUTHENTICATION_TIMEOUT`;
  - the new `test_an_address_change_needs_a_recent_reauthentication` checks, under the identity settings, the setting `True`, the timeout 300, the adapter's `is_reauthentication_required` `True`, and that Glow's adapter overrides none of `reauthenticate`, `authenticate`, `pre_authenticate` or `is_reauthentication_required`.
- `proofs/postgres-ordering/glow_ordering_proof/identity_cases.py`:
  - `config.settings_as_briefed` checks the setting, the 300 seconds and the `reauthenticate` limit;
  - `enum.email_change_taken_and_free_alike` and `notice.email_change` each reauthenticate first, on each device that changes the address;
  - the new case `reauth.email_change_needs_recent_reauthentication` (checks 13, 10, D3 and D5) runs before `mail.no_link_no_stranger`, which stays last.
- `identity_support.py`: `Context.reauthenticate`, `Reply.flow_ids` and `Reply.error_codes`.
- `proofs/postgres-ordering/tests/test_identity_offline.py`: the plan test requires acceptance check 13 too.

**The new case, clause by clause:**

| Clause of acceptance check 13 | What the case does and checks |
|---|---|
| right after sign-in, no reauthentication | A password sign-in on a new device, then `POST account/email`. It answers 401, lists the `reauthenticate` flow, has nothing pending, carries no credential, sends no mail, and changes and adds no address |
| more than 300 seconds after the reauthentication | Within `clock_ahead(reauthentication, 301)`, so allauth's own `time.time()` in that module is 301 seconds ahead (the suite's way of moving a code limit's clock): the same refusal |
| in another session than the one that reauthenticated | The member's second signed-in device, after the first reauthenticated: the same refusal |
| a wrong password is refused | Five wrong passwords on that device: each 400 `incorrect_password`, with no credential |
| the sixth within 300 seconds, as too many attempts | The sixth: 400 `too_many_login_attempts`. The right password is then held too, and so is the sign-in form (`auth/login`, 400 `too_many_login_attempts`): the same `login_failed` limit. The change is still refused |
| the reauthentication leaves the key, its `UserSession` and its `AccountSession` unchanged, and returns no token pair and no `session_token` | Before and after the right password: the token names the same key; the Django session exists and their count is the same; the `UserSession` row is the same, and its `xmin` and the `AccountSession`'s `xmin` are unchanged; the `AccountSession` is `valid` with the same reference; the reply carries no `session_token`, `access_token` or `refresh_token`, and its `meta` is `{is_authenticated}`; the device's tokens are unchanged; one reauthentication record; the token still works at both layers |
| with the right password, the change goes ahead as acceptance check 10's notice shows | After `clear_rate_limits()` (as if the windows had passed), the member reauthenticates and asks: 200. The code goes to the new address, verification is 200, the one address is the new one, verified and primary, and one email-changed notice goes to the old address |

**Reversals** (the method below):

| ID | The edit | Run | Result |
|---|---|---|---|
| C1-R1 | `conf.py`: `"ACCOUNT_REAUTHENTICATION_REQUIRED": False` | the job's SV1 steps, on a new throwaway database | `[identity] FAIL config.settings_as_briefed … FAILED: an address change needs reauthentication`; `[identity] FAIL reauth.email_change_needs_recent_reauthentication … FAILED: right after sign-in: the change answers 401`; `[identity] cases: 46/48 passed`; `IDENTITY VERDICT: FAIL` |
| C1-R1 (API) | the same edit | `manage.py test tests.test_identity_offline` | `FAIL: test_an_address_change_needs_a_recent_reauthentication`; `FAIL: test_the_briefed_values … (setting='ACCOUNT_REAUTHENTICATION_REQUIRED') … AssertionError: False != True`; `Ran 21 tests`, `FAILED (failures=2)` |
| C1-R2 | `identity_cases.py`: the reauthentication removed from `notice.email_change` and from `enum.email_change_taken_and_free_alike` (setting on) | the job's SV1 steps | `[identity] FAIL enum.email_change_taken_and_free_alike (3) … FAILED: a taken and a free address answer alike`; `[identity] FAIL notice.email_change (10, 3) … FAILED: the change is asked for`; `46/48`; `FAIL` |

With the setting off (C1-R1), the two existing cases still pass: a reauthentication succeeds whether or not it is required.

### Item 2: the data model

`docs/architecture/data-model.md`, "Email change and recovery": its first sentence is now the brief's words. It is one source line, where the old text wrapped over two; nothing else in that paragraph or file changed.

### Item 3: the results upload checked first (D10)

**Files:**
- `proofs/postgres-ordering/glow_ordering_proof/identity_scan.py` (new): the job's secret check, moved out of the workflow so it can be tested offline. It uses the standard library only.
  - It reads the same values from the job's directory as the old inline check: the identity `SECRET_KEY`, the identity marker, the ordering marker, the superuser password, each passfile password and each line of the signing key.
  - It looks for each in the suite's log, and in `identity-results.json`, both as written and in the JSON's decoded strings.
  - It requires the suite's `identity secret scan: clean`.
  - It passes (exit 0) only when nothing is found and the suite reported clean.
  - Otherwise, or if a secret file cannot be read, it removes the JSON and exits 3.
  - It prints counts only.
- `.github/workflows/foundation.yml`, the Database proof checks job's SV1 steps only:
  - The suite step gains `id: identity`. Its inline Python is replaced by `env -i … python -m glow_ordering_proof.identity_scan "$DIR" "$DIR/identity.log" .work/identity-results.json`.
  - Only on that check's pass does the step write `scan=passed` to `$GITHUB_OUTPUT` and show the whole log. Otherwise it shows only the suite's own result lines, as before.
  - The upload step is renamed "SV1: save the identity suite's results JSON, once the secret check has passed", and runs `if: ${{ always() && steps.identity.outputs.scan == 'passed' }}`. Before, it ran `if: always()`.
  - So after a failed check nothing is uploaded, for two reasons: the step is skipped, and the file is gone.
- **An addition: the suite's own scan covers the JSON too** (`identity_suite.py`). The job's values cannot include the run's passwords, codes and tokens. So the suite also counts its ledger's secrets in the JSON it would write. If it finds one, the run fails, the JSON is not written, and the scan line reads `FOUND`. The scan line now ends "…writes and the results JSON)".
- **Tests** in `proofs/postgres-ordering/tests/test_identity_offline.py`:
  - `IdentityScanTests` (9):
    - the values are the job's files;
    - a clean run passes and keeps the JSON;
    - each job value planted in the JSON alone is refused, the JSON is removed, and no value is printed;
    - a value hidden by JSON's `\u` escapes is found;
    - a value in the log is refused;
    - a log without the suite's clean line is refused;
    - an absent JSON is nothing to upload;
    - an unreadable secret file is refused;
    - the module imports only the standard library.
  - `IdentityUploadGateTests` (2): the suite step calls the check and writes `scan=passed` only in its pass branch; the upload's `if` waits for it, and no `if: always()` remains on it.

**Reversals:**

| ID | The edit | Run | Result |
|---|---|---|---|
| C1-R3 (the prompt's) | `identity_suite.py`: `report.server["planted"] = os.environ["PROOF_DB_MARKER"]`, the identity database's marker, a job value the suite's ledger does not hold, so it is in the JSON only; and `foundation.yml`: the upload's `if` set to `always()`, so the upload is unconditional | the job's SV1 steps, on a new throwaway database, with the upload step's condition evaluated and the upload simulated | `the job's secrets found in the identity suite's output: 0`; `the job's secrets found in the identity results JSON: 1`; `the suite's own scan reported clean: True`; `the results JSON was removed; nothing to upload`; `the full output is withheld; the suite's own result lines:` … `[identity] cases: 48/48 passed in 39.1 s` … `IDENTITY VERDICT: PASS`; `FAIL: the secret check did not pass`; step exit status 1; the upload condition `always()` → runs; `simulated upload: no file at proofs/postgres-ordering/.work/identity-results.json (ignored)` |
| C1-R3c (the defect, before C1) | the same plant, with `c289424`'s `foundation.yml` (the old inline check of the log only, and `if: always()`) | the same | `the job's secrets found in the identity suite's output: 0`; `the suite's own scan reported clean: True`; step exit status 0; `simulated upload: identity-results.json uploaded; job values in it: 1`. The old step passes and would upload the planted value |
| C1-R4 | `identity_suite.py`: `report.server["planted"] = settings.SECRET_KEY`, a value the suite's ledger holds | the job's SV1 steps | `identity secret scan: FOUND (712 secrets held; 1 found in 232 log records, 100 writes and the results JSON)`; `IDENTITY VERDICT: FAIL`; the JSON not written; `the identity results JSON is absent: nothing to scan or upload`; `the suite's own scan reported clean: False`; `FAIL: the secret check did not pass`; the upload condition → skipped; `no upload; file present at the path: False` |
| C1-R5 | `identity_scan.py`: `found_results = 0` | the proof's `tests.test_identity_offline` | `FAIL: test_a_value_escaped_by_json_is_found`; `FAIL: test_a_value_in_the_json_only_is_refused_and_the_json_removed` (six subtests); `Ran 25 tests`, `FAILED (failures=7)` |
| C1-R6 | `foundation.yml`: the upload's `if` set to `always()` | the same | `FAIL: test_the_upload_waits_for_the_check`; `Ran 25 tests`, `FAILED (failures=1)` |

**The first C1-R3 run** also failed `mail.no_link_no_stranger` ("no link and no name but Glow's"), a case the edits do not touch; the second run above passed it. See "What could not be run, and limits".

### The threat model

The endpoint table's `POST auth/reauthenticate` row, above, now records the endpoint as used: required before an address is added, removed or marked primary; the limit it shares with sign-in; and what it does not do. Nothing else in the threat model changed.

### The method, and the commands

**The reversal method, as before:**
- Each reversal was a temporary exact-once string edit by a scratch helper outside the checkout. It ran on the committed code head and restored the file afterwards, dropping the module's cached bytecode.
- After each one, `git status --porcelain -- services proofs packages apps scripts .github` was empty.

**The local database runs** follow P06.DB's D4. A scratch harness outside the checkout ran the job's own step scripts, read from `foundation.yml` with PyYAML:
- the credentials, PostgreSQL's start, the role and databases, then the three SV1 steps;
- then it evaluated the upload step's `if` and simulated the upload by copying the file it names, counting the job's values in the copy;
- then the removal step.

Each run had:
- a new container from `postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`, published on `127.0.0.1:5433` only;
- passwords, markers and keys generated by the job's own step into a scratch `RUNNER_TEMP`;
- a fresh environment for each step (PATH with the proof's venv first, HOME, LANG, `RUNNER_TEMP`, `GITHUB_OUTPUT`, `GITHUB_RUN_ID=local`, `GITHUB_RUN_ATTEMPT=1`, and the step's own env), and none of the forbidden names;
- the container and directory removed by the job's removal step: `docker ps -a` is empty afterwards.

| Command | Result |
|---|---|
| `python3.12 -m venv .venv`; `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock` (in `services/api`, and in `proofs/postgres-ordering`) | exit 0 each |
| `.venv/bin/python -m pip check` (both) | `No broken requirements found.` |
| `GLOW_ENV=test .venv/bin/python manage.py check` | `System check identified no issues (0 silenced).` |
| `GLOW_ENV=test .venv/bin/python manage.py test tests --verbosity 2` | `Ran 450 tests` … `OK` (449 before; 1 new) |
| `.venv/bin/ruff check .`; `ruff format --check .`; `mypy` (API) | `All checks passed!`; `99 files already formatted`; `Success: no issues found in 57 source files` |
| In `proofs/postgres-ordering`: `.venv/bin/python -m unittest discover -s tests -t . -v` | `Ran 186 tests in 13.245s` … `OK` (175 before; 11 new) |
| In `proofs/postgres-ordering`: `ruff check .`; `ruff format --check .`; `mypy` | `All checks passed!`; `52 files already formatted`; `Success: no issues found in 52 source files` (`ruff format .` was applied once, to three files, before the commit) |
| `docker pull` of the job's image | `Status: Downloaded newer image for postgres@sha256:d74eeac9…` |
| The job's SV1 steps, local baseline on the code | `No changes detected`; `the job's secrets found in the identity suite's output: 0`; `… in the identity results JSON: 0`; `[identity] cases: 48/48 passed in 38.0 s`; `identity secret scan: clean (712 secrets held; 0 found in 232 log records, 100 writes and the results JSON)`; `IDENTITY VERDICT: PASS`; `identity phase: 39 s`; the second run refused with `52 52 61 32 48` before and after; upload condition → runs; `job values in it: 0` |
| Probes (scratch, outside the checkout): the three address-changing cases with their replies' status, flow ids, `meta` keys and error codes printed (no values); then the whole suite twice, naming any forbidden token in any message by token and subject only | all three cases passed; the 401 carries `reauthenticate` and `password_reset_by_code` (`is_pending: false`). Then `65 messages; 0 forbidden hits`, twice |
| C1-R1 to C1-R6 | as in the tables above |

### The run of record

**Push run [42634020622](https://github.com/amthorn78/glow-dating-app/actions/runs/42634020622)** (Foundation, run 916, attempt 1) on `bda299e3034121b2cc20318024f35f5938f83b4c`, the code head, read with the GitHub tools.

**Every job `success`:**
- Change scope;
- API checks: `Ran 450 tests in 19.126s` … `OK`; Ruff `All checks passed!`, `99 files already formatted`, mypy `Success: no issues found in 57 source files`; the contracts' `Ran 39 tests` … `OK`;
- API artifact checks;
- API mobile smoke;
- Mobile checks;
- Stream proof checks;
- Database proof checks;
- Foundation gate, which printed **`Application checks passed`**.

**No toolchain retry fired.** Every DM-41 "Wait 60 s …" and "Retry the Python install once" step was `skipped`.

**The Database proof checks job** ran 7 min 56 s of its 30 minutes, from 14:22:32 to 14:30:28 UTC:
- the proof's offline tests: `Ran 186 tests in 13.085s` … `OK`; Ruff `All checks passed!`, `52 files already formatted`, mypy `Success: no issues found in 52 source files`;
- the ordering suite: `== VERDICT: PASS (reference) ==`, `== VERDICT: PASS (adapter) ==`, `== VERDICT: PASS ==`;
- "SV1: show the identity database refuses the other marker, then apply the reviewed migrations from zero": success.

**"SV1: run the identity suite …"** (14:29:36 to 14:30:21):
- the job's check printed `the job's secrets found in the identity suite's output: 0`, `the job's secrets found in the identity results JSON: 0` and `the suite's own scan reported clean: True`;
- then the suite's output: 48 `[identity] PASS` lines, among them `reauth.email_change_needs_recent_reauthentication (13, 10, D3, D5) 3.3 s`, `notice.email_change` and `enum.email_change_taken_and_free_alike`;
- then `[identity] cases: 48/48 passed in 43.7 s`, `identity secret scan: clean (712 secrets held; 0 found in 232 log records, 100 writes and the results JSON)`, `IDENTITY VERDICT: PASS` and `results written: .work/identity-results.json`;
- **`identity phase: 44 s (the job's timeout is 30 minutes)`**.

**"SV1: show that a second identity run …":** `before: 52 52 61 32 48; after: 52 52 61 32 48`, exit status 1, refused as a used database.

**"SV1: save the identity suite's results JSON, once the secret check has passed":** ran, after the step's `scan=passed`. Artifact `sv1-identity-results`, 3,846 bytes, ID 13681219810.

**The removal step:** `container removed: glow-proof-db-42634020622-1`, `credential and marker files removed`, `no proof container remains`.

### What could not be run, and limits

- **A failed check in CI.** The upload's skip after a failed check was shown locally only (C1-R3 and C1-R4), by the job's own step scripts and the harness's reading of the step's `if`. GitHub's evaluation of that `if` was seen only in the passing run of record, where the upload ran. No failing CI run was pushed, by the push rule and because a reversal does not belong on the branch.
- **`actions/upload-artifact` was not run locally.** Its upload was simulated by copying the file at its path.
- **One unexplained local failure.** In the first C1-R3 run, `mail.no_link_no_stranger` failed ("no link and no name but Glow's"). That case is untouched by C1. Two probes of the whole suite and every later full run (C1-R3 again, C1-R3c, C1-R4, and the run of record) passed it.
  - The cause could not be read afterwards, since the outbox lives in that process only.
  - The likely cause is unconfirmed: allauth's codes use only consonants (`BCDFGHJKLMNPQRSTVWXZ`, `core/internal/cryptokit.py:16`), so a code can spell "HTTP", which the case forbids in every message.
  - The case was not changed: changing it would loosen an existing check, and it is outside this correction's items. It is for the manager to triage.
- **The trusted classifier was not run** in this session. Classification is the manager's.

### Deviations and the stop rule

**The stop rule:** nothing met it.
- 65.21.1 cycles no key, issues no token pair and runs no sign-in hook at `auth/reauthenticate` (above).
- `git diff --name-only c289424 HEAD` lists only the owned paths.
- In the workflow, every hunk is in the Database proof checks job's SV1 steps: the suite step and the upload step.
- No package was added and no lock changed.
- The job stayed within its timeout (7 min 56 s).

**Deviations:** there is no `session_token` deviation. The others:
- **The suite's own scan of the results JSON** (`identity_suite.py`) is an addition beyond item 3's words. The prompt asks for the job's check to scan the JSON. This also covers the run's passwords, codes and tokens, which only the suite knows. The scan line's wording changed after its "clean" or "FOUND" prefix.
- **The new case's flow check** is "lists `reauthenticate`, and nothing is pending", not "only `reauthenticate`". The 401 also lists `password_reset_by_code` (not pending), as above.
- **The data model's sentence** is one source line, where the old text wrapped over two.
- **The new case also shows the sign-in form held** by the same limit after the sixth wrong password. Acceptance check 13 does not ask for this; it shows D3's statement about the guessing budget.

## Manager verification of correction C1 (App Manager 10, 9 November 2026)

**The diff.** `git diff c289424 96dc3e2` was read whole: ten paths, each owned by "Correction C1".
- The code commit `bda299e` touches:
  - `conf.py`: one setting;
  - the API's identity offline test;
  - in the proof: `identity_cases.py`, `identity_suite.py`, `identity_support.py`, the new `identity_scan.py` and the offline test;
  - the Database proof checks job's SV1 steps.
- The two records commits are Markdown only:
  - the data model's diff is the one sentence, in C1.3's words;
  - the record's diff is the endpoint table's `auth/reauthenticate` row and the new section.
- Read against DM-47's words:
  - the new case covers every clause of acceptance check 13;
  - the scan reads the same job values as the old inline check, from the same files, and also scans the JSON's decoded strings;
  - the upload's condition is `always() && steps.identity.outputs.scan == 'passed'`.

**Classification.** The trusted classifier from `main` (`da92f1f`), with `--base da92f1f… --head 96dc3e2… --merge-base`: full scope, `behavior-or-empty`, 70 paths, one merge base (`8d2de72`).

**Re-runs.** These ran in a scratch copy of `bda299e`'s whole tree, in the clean environment, with SV1's hash-locked virtual environments (C1 changes no lock):
- API: `Ran 450 tests` … `OK`; Ruff clean; mypy `no issues found in 57 source files`;
- the proof's offline tests: `Ran 186 tests` … `OK`; Ruff clean; `52 files already formatted`; mypy `no issues found in 52 source files`.

**Three reversals, re-run offline.** Each failed as it should, and each file was restored with its hash checked:
- **M1:** the setting turned off. `test_the_briefed_values` and `test_an_address_change_needs_a_recent_reauthentication` fail (2 of 21).
- **M2:** the scan ignoring the JSON (`found_results = 0`). Seven `IdentityScanTests` fail.
- **M3:** the upload back to `if: always()`. `test_the_upload_waits_for_the_check` fails.

**The run of record**, read with the GitHub tools: push run 42634020622 on `bda299e`.
- All eight jobs `success`, and the gate printed `Application checks passed`. Every DM-41 retry step was `skipped`.
- The job's check printed `the job's secrets found in the identity suite's output: 0`, `… in the identity results JSON: 0` and `the suite's own scan reported clean: True`.
- 48 `[identity] PASS` lines, `reauth.email_change_needs_recent_reauthentication` among them; `[identity] cases: 48/48 passed in 43.7 s`; `identity secret scan: clean (712 secrets held; 0 found in 232 log records, 100 writes and the results JSON)`; `identity phase: 44 s`.
- The second identity run was refused, with the counts `52 52 61 32 48` unchanged.
- The upload step "…, once the secret check has passed" uploaded `sv1-identity-results` (3,846 bytes).
- The cleanup removed the container and the credential files.

**F-M1, the no-link check's false failure** (the session's unexplained local failure, diagnosed):
- **The defect.** `mail.no_link_no_stranger` lowercases each message and forbids `http`. allauth's codes are eight letters from `BCDFGHJKLMNPQRSTVWXZ`, in two dashed groups of four (`allauth/core/internal/cryptokit.py:16`, `:19-39`). So a group can be `HTTP`.
- **The mechanism, shown offline:** Glow's own verification and reset messages, given the legal code `HTTP-BCDF`, fail the check on `http`.
- **How often:** 3 of 400,000 random codes from allauth's generator contained `http`, about 1 in 80,000 per code by construction. A run sends some tens of codes, so a run of record can fail at random, rarely.
- **The observed failure:** whether it caused the session's one local failure is consistent but not proven; no other cause was found.
- **Disposition:** it is SV1's own test (`269ac3b`), and a unit test shows it, so it is fixed before the merge (step 6's rule (a); OD-21: reliable CI). The fix is test-only: remove the message's own code before the forbidden-string check, with a test that a code spelling `HTTP` passes and a link still fails. It joins the exact-head review's focus, and its fix goes in the correction pass after the review.

**C1's deviations:**
- **The suite's own scan of the JSON** (an addition): accepted. It narrows what can be uploaded and is tested.
- **The flow check's wording** ("`reauthenticate` listed and nothing pending"): accepted. 65.21.1 also lists `password_reset_by_code`, not pending, in the 401.
- **The data model's line wrapping:** accepted.
- **The extra sign-in-form check:** accepted. It shows the limit is the sign-in form's.
- **The upload skipped after a failed check,** shown only locally by the job's own scripts: accepted. CI shows the passing path, and the reversals show the refusal.

**Codex's P1 thread** on `conf.py` is answered and resolved now that C1 is on PR42.

## Exact-head review of SV1 (code head `bda299e`)

- **The session:** started by Nathan from the exact-head review prompt, revision 1, at `1c26f1d71ec597b3420b617e81b1556f92e18809` (`docs/ephemeral/2026-11-09-sv1-review-prompt.md`). It reported on 9 November 2026; its report was relayed to App Manager 10.
- **The gates:**
  - the environment check passed;
  - the start gate passed, with one merge base, `8d2de72`, and no non-Markdown path differing from `bda299e`;
  - the trusted classification is `"full": true`, `behavior-or-empty`.
- **What it ran:**
  - the API's checks (450 tests) and the proof's (186);
  - five offline reversals (C1-R1, C1-R5, C1-R6, R2, R3), each failing its case;
  - the specification regenerated to the record's hashes;
  - informational, on a throwaway PostgreSQL under D4: the suite 48/48 twice, reversals D6-h and D2-c, and four probes.
- **What it read:** the three runs' job lists, gates and the last 400 lines of each Database job's log.
- **The verdict: changes required.** Two should-fix findings fall in the correction classes, with one records correction and six nits. No finding is blocking.
- **Its statements:**
  - every Dev Manager condition is met in code;
  - every fact the record reads from allauth 65.21.1 holds in the installed source;
  - the workflow's five hunks all lie inside the Database proof checks job;
  - the dependency set is exactly the brief's;
  - the records hold, apart from F-3, F-6 and F-8.

**The review's threat model**, as its report gives it, condensed:
- **Assets:**
  - accounts and addresses, passwords, session keys, access and refresh tokens, and verification and reset codes;
  - the JWT signing key and the identity `SECRET_KEY`;
  - `UserSession`'s IP address and user agent.
- **Actors:**
  - an anonymous prober;
  - a holder of a stolen access token, refresh token or session key;
  - a member acting on another member's account;
  - a reader of this public repository's CI logs and artifacts.
- **Entry points:** allauth's 17 `app` routes and `GET /api/v1/account/access`, the actor class, and the identity job's steps.

| Threat | What stops it | What proves it |
|---|---|---|
| 1. An endpoint answers more than it should; the phone and code-confirm routes mounted regardless | allauth's refusals; Glow's `get_phone` refusal (`adapter.py:118-124`); the Glow route's `handle_exception` (`views.py:36-44`) | `endpoints.refusals` (29 unauthenticated, 4 signed-in refusals); `config.routes`; the API's 18-route test |
| 2a. A forged or expired token | `decode_token`: the configured algorithm only, then `exp`, `token_use`, string `jti`, `sub` and `sid` (`jwt/internal.py:182-205`); RS256 with a 2048-bit key per run | `refresh.bad_tokens_refused_without_ending`, `expiry.access_token`, `expiry.refresh_token` |
| 2b. A token outliving its session or its user's password | stateful validation (`internal.py:35-46`, `:98-107`) through Django's `get_user` | `logout.ends_at_once`, `devices.password_change_ends_both`, `revoke.*`; D2-a |
| 2c. A replayed rotated refresh token keeping a session | rotation; `replayed_session_key`'s checks, then `end_replayed_session` (`strategy.py:25-49`, `revocation.py:225-234`); nothing done for an ended session | `refresh.replay_ends_session`, `refresh.ended_session_refused_nothing_else`; D2-b, D2-c; R3 |
| 2d. Expiry at one layer only | `set_expiry` with `expires_at` (`revocation.py:162-165`); Django keeps a date-time expiry across saves | `expiry.account_session`, `signin.records_account_session`; D2-d; the review's probe P2 |
| 3a. A derived or secret session reference | `UserSession`'s `BigAutoField` key (`revocation.py:149-158`) | `signin.records_account_session`, `signin.reference_not_derived` |
| 3b. The session key as a bearer credential at allauth's endpoints | allauth's design (N3); Glow never stores, hashes or logs it (`authentication.py:74`) | `logout.ends_at_once`, `verify.used_code_refused`; probe P3: the key alone lists sessions at allauth and is refused at Glow's route |
| 3c. The `sid` read without `SECRET_KEY` | AES-CTR under `sha256(SECRET_KEY)`, a fresh IV per token; a generated 64-hex-character key, the placeholder refused | `signin.reference_not_derived`; `IdentityKeyFileTests` |
| 4. One layer outliving the other | Glow's `glow_chat` step first, outside any transaction, then allauth's; both idempotent (`revocation.py:182-273`) | `logout.*`, `revoke.*`, `actor.refuses_revoked_session_between_layers`, `devices.*`, `signin.fails_closed`; D6-c to D6-h; probe P4 |
| 5. The actor steered by a header, body or query | the `sid` from the validated payload only, bound to the token's user, the key deleted (`authentication.py:63-106`) | `actor.uses_token_sid_not_header`; D7-a; the static guard; R2 (F-5 widens the guard) |
| 6. Enumeration and guessing | `ACCOUNT_PREVENT_ENUMERATION`; no unknown-account mail; `login_failed`; the `confirm_email` window consumed before the taken-or-new branch | `enum.*`, `ratelimit.failed_sign_ins`, the reauthentication case; D3-a, D3-b, X-ratelimit. **F-2** is the one budget not analysed |
| 7. A message revealing a link, a stranger, an address, an IP address or a device | `messages.py` words every message; the fixture backend has no network code | `mail.no_link_no_stranger`, `notice.email_change`; X-link, D8-a. **F-1** is the check's own false failures |
| 8. An address moved without the password | `ACCOUNT_REAUTHENTICATION_REQUIRED`; allauth's guards; the per-session 300-second window; a wrong password consumes `login_failed` | acceptance check 13's case; C1-R1, C1-R2 |
| 9. The `verified` transition racing or skipping its lock | `mark_verified`'s lock, refusal and retry; `require_no_transaction` at every entry point | `verified.*`, `verify.transition_retried_at_sign_in`, `revoke.inside_transaction_refused`; D6-a, D6-b, X-retry |
| 10. The served runtime importing the slice | `glow_api/` unchanged | `test_identity_sealed_runtime.py`; D11-a |
| 11. A restored refresh token; a review sign-in path | the next refresh is the replay that ends the session; no review path, synthetic accounts only | `refresh.replay_ends_session` |
| 12. A secret in a public log or artifact | key files of mode 0600 by `O_EXCL`; masked values; `identity_scan.py` before anything is shown or uploaded; the suite's ledger; cleanup `if: always()` | the job's check lines in runs 907, 916 and 919; `IdentityScanTests`, `IdentityUploadGateTests`; LOG-a, X-keyfile, C1-R3 to C1-R6 |

**The review's findings and the manager's dispositions:**

| # | Severity | Finding | Disposition |
|---|---|---|---|
| F-1 | should fix (class: a test fails where the code is right) | F-M1, confirmed and wider. The no-link check forbids `http` and `www.`. A code group `HTTP` spells `http` (1 in 80,000 per code), and a code ending `WWW` before the sentence's full stop spells `www.` (1 in 8,000 per code). Together that is about 1 in 7,273 per code, or about 0.8 percent of runs. Codex raised the same defect on `1c26f1d` (P2, `identity_cases.py:1641`) | **Fix before the merge, in correction C2** (test-only): strip the message's own code before the check, with cases for `HTTP`, a trailing `WWW` and a real link |
| F-2 | should fix (class: a token holder gets a larger password-guessing budget than the sign-in form gives; D3's standard) | At `POST account/password/change`, a wrong current password is checked by `check_password` alone (`headless/account/inputs.py:180-184`). It consumes only `change_password`, 5 per minute per user (`headless/account/views.py:400`; `account/app_settings.py:287`), and no `login_failed`. A holder of a live session key or access token gets 7,200 guesses a day, against 1,440 at the sign-in form. Codex raised the same finding on `30fdf1a` (P2, `conf.py:71`) | **Fix before the merge, in correction C2, after the Dev Manager's read** (DM-48): it changes D3's "allauth's rate limits keep their defaults" (DM-45 item 7) on a security boundary |
| F-3 | should fix (class: a record claims more than the tests show) | The record says migration 0004's SHA-256 is pinned by `test_migration_0004_adds_the_age_state_only`. No test pins it: the `pinned` dictionary holds 0003's hash only | **Fix in C2:** pin 0004's hash in the `pinned` dictionary, so the record's sentence holds |
| F-4 | nit | After a failed secret check, the step prints the suite's own `[identity]` result lines from the log the check failed. Today those lines hold only fixed strings | **In C2:** print counts only after a failed check |
| F-5 | nit | The static no-header guard does not forbid `request.query_params`, `request.GET`, `request.COOKIES`, `request.POST` or a lowercase `session_token` | **In C2:** widen the guard, and assert that `actor_for` is called with exactly `user, payload` |
| F-6 | nit | The brief's N2 wording lists the user check before the `jti` check, but allauth's `validate_refresh_token` checks the `jti` state first (`internal.py:116-125`). Every check still runs before any action | **To the Dev Manager** (DM-48), since N2's words are its own |
| F-7 | nit | The threat model does not name `ACCOUNT_EMAIL_VERIFICATION_SUPPORTS_CHANGE` and `…_SUPPORTS_RESEND`, which are off and keep a pending verification answering alike | **In C2:** pin both in `config.settings_as_briefed`; the threat model names them |
| F-8 | nit | "Repeatable: yes" for the session list and the replay rests on the code's idempotence, not on a failing-second-step case | **Recorded here** as a claim limit |
| F-9 | nit | A `UserSession` purged after the aligned expiry leaves `auth_session_ref` pointing at a deleted row. The actor refuses `no_user_session` before its expiry check, so the row is never marked | **Carried to SV4** with the expiry sweep (the carried-items file) |

**What the review could not run or read:**
- the Database jobs' logs before their last 400 lines;
- the earlier run 42575311159;
- the artifacts' contents;
- allauth's documentation site;
- Notion.

It did not check the record's claim that run 907's 47 case lines match the earlier run's word for word.

## Correction C2

- **Session:** correction C2 of SV1 (DM-48), started by Nathan from the C2 prompt, revision 1, at `2f577f89b53c48b493702eebafad9181d9e7a0d4` of the manager branch. Branch `claude/trusting-goldberg-e4ogat`.
- **Code head:** `6da8061169c4760b8419fc649c6d5aad57f29b50`. **Records:** the commit after it (the two architecture sentences, this record's three rows and focus bullet, and this section).
- **Specification:** the brief's "Correction C2", revision 5 (DM-48 C2.1 to C2.8).
- **Local runs are iteration, not evidence.** The run of record is CI's push run below.

### Start gate and environment

**The environment check (names only):**
- None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` is set.
- No `STREAM_*` or `PG*` name is set.
- `GH_TOKEN` and `GITHUB_TOKEN` are present, and were never read.
- Toolchain: `python3.12 --version` printed `Python 3.12.14`, and `docker --version` printed `Docker version 29.9.2, build a82e528`.
- Docker's daemon was not running. The session started `dockerd` itself, for the throwaway databases only.
- Every repository command ran in `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only its own variables (`GLOW_ENV=test` for the API). The installs also got the proxy and CA variables, passed by reference.

**The start gate:** every check passed.

| Check | Result |
|---|---|
| `git rev-parse HEAD` after `git switch -C claude/trusting-goldberg-e4ogat 2f577f8…` | `2f577f89b53c48b493702eebafad9181d9e7a0d4` |
| `2f577f8` on the live manager branch | `origin/claude/magical-wozniak-yfmmx2` was at `2f577f8` itself |
| non-Markdown changes under `.github scripts services apps packages proofs` from `bda299e` to `HEAD` | none |
| the owned paths changed on the manager branch after `2f577f8` | none |
| `grep -c -E '^#+ Correction C2'` in this record | `0` |
| `grep -c 'change_password'` in `conf.py` | `0` |

### What allauth 65.21.1 showed at `account/password/change`

Read in the installed wheel (`services/api/.venv`, from the hash-locked development lock; `django_allauth` metadata `Version: 65.21.1`), and confirmed by the new case. **Nothing met the stop rule.**

**When the limiter counts:**
- `headless/account/views.py:400-401`: `ChangePasswordView` carries `rate_limit(action="change_password")` on `handle`; `allauth/decorators.py:4-5` binds it to `app="allauth.account"`.
- `headless/base/views.py:57-63`: `AuthenticatedAPIView.dispatch` answers an unauthenticated request before `handle` runs, so only signed-in requests are counted.
- `headless/internal/restkit/views.py:18-31`: `dispatch` calls `handle`, and `handle` parses and validates the input. The decorator wraps `handle`, so it consumes **before** the input is checked (`core/internal/ratelimit.py:345-356`, `consume_or_429` at `:339-342`).
- `core/internal/ratelimit.py:242-276`: `consume` skips only a `GET` (`:255-256`) and consumes on every other request, whatever its outcome: a wrong current password, a right one, and a new password the validators refuse.
- `core/internal/ratelimit.py:157-181`: with `per == "user"` the key is the account's primary key (`:163-170`).
- `core/internal/ratelimit.py:199-231` and `:184-196`: the history is read under `cache_lock`, `now = time.time()` (`:219`), every timestamp at or before `now - duration` is dropped, and the hit is allowed only while fewer than `amount` remain.
- `core/internal/ratelimit.py:46-65`: `cache_lock` calls `time.monotonic()` (`:49`, `:52`) and `time.sleep()` (`:56`).
- `headless/account/inputs.py:180-184`: `clean_current_password` calls `self.user.check_password` only: no `authenticate`, no `login_failed`, no signal.

**The sixth request's answer:** with `5/300s/user`, the five timestamps are still within 300 seconds when the sixth arrives 120 seconds after the first by the limiter's clock, so `apply_rate` refuses it, and `respond_429` (`:322-329`) returns headless's `RateLimitResponse` (`headless/base/response.py:198-200`): **HTTP 429, body `{"status": 429}`, with no `errors` and so no error code** (`headless/internal/restkit/response.py:13-31` adds `errors` only when given). The view never runs, so the password is unchanged. Under allauth's default `5/m/user` the five timestamps are older than 60 seconds and are dropped, so the sixth is allowed and the change goes ahead (C2-R1 and C2-R1c below).

**The override merges:** `account/app_settings.py:267-311`: `RATE_LIMITS` builds allauth's defaults (`change_password` is `"5/m/user"` at `:287`) and then `ret.update(rls)` (`:311`) with the setting, so `{"change_password": "5/300s/user"}` replaces that one key and leaves every other default. `5/300s/user` parses as amount 5, duration 300, per `user` (`core/internal/ratelimit.py:95-121`). Shown by `test_the_password_change_limit_merges_into_allauths_defaults` and by `config.settings_as_briefed`, which compare the resolved limits with allauth's own, read with the override taken away (`override_settings(ACCOUNT_RATE_LIMITS={})`): one key differs, `change_password`.

**The two verification settings (F-7):** `account/app_settings.py:121-140`: 65.21.1 reads `ACCOUNT_EMAIL_VERIFICATION_SUPPORTS_CHANGE` and `ACCOUNT_EMAIL_VERIFICATION_SUPPORTS_RESEND` (default `False`) through the properties `EMAIL_VERIFICATION_MAX_CHANGE_COUNT` and `EMAIL_VERIFICATION_MAX_RESEND_COUNT`, which give `0` for `False` and `2` for `True`. There is no property named after the settings.

### Item 1: the password-change limit (F-2; D3; acceptance check 11)

**Files:**
- `services/api/glow_identity/conf.py`: `"ACCOUNT_RATE_LIMITS": {"change_password": "5/300s/user"}`, before `CACHES`. The fragment's rate-limit comment now says what D3 says: the defaults kept except `change_password`, why (`check_password` alone, no `login_failed`), every signed-in request counted, 10 in all, and the override merging; the cache sentence follows it.
- `services/api/tests/test_identity_offline.py`:
  - `test_the_briefed_values` gains the setting;
  - the new `test_the_password_change_limit_merges_into_allauths_defaults` checks, under the identity settings, allauth's default `5/m/user`, the resolved `5/300s/user` (amount 5, 300 seconds, per user), the same keys as allauth's defaults, and that only `change_password` differs.
- `proofs/postgres-ordering/glow_ordering_proof/identity_cases.py`:
  - `config.settings_as_briefed` checks the same three things;
  - the new case `ratelimit.password_change` (checks 11 and D3), after `ratelimit.failed_sign_ins`, which stays as the check's first sentence.
- `identity_support.py`: `clock_ahead`'s object now keeps `monotonic` and `sleep`, unmoved, beside the moved `time` (DM-48 section 3). The two existing users (`verify.expired_code_refused`, `reauth.email_change_needs_recent_reauthentication`) call only `time()`, and both still pass.
- `proofs/postgres-ordering/tests/test_identity_offline.py`: `ClockAheadTests` (2), and the plan test requires both rate-limit cases.

**The new case, clause by clause:**

| Clause of acceptance check 11's second sentence | What the case does and checks |
|---|---|
| five requests at `account/password/change` with a wrong current password, each refused | A new member's own device, with its access token: five requests with a wrong current password and a valid new password. Each 400 `enter_current_password`, with no credential |
| a sixth with the right current password and a valid new password | The same device, the member's own password, the same new password |
| sent more than 60 and less than 300 seconds after the first of the five, by the limiter's clock | Within `clock_ahead(ratelimit, 120)` (allauth's `core/internal/ratelimit` module). The case measures the gap's bounds from real times taken before the first and after the fifth and sixth: at least `before_sixth + 120 - after_fifth`, at most `after_sixth + 120 - before_first`, and requires more than 60 and less than 300. The run printed `120 to 121 s` |
| is refused as too many | 429, with no error code and no credential |
| the password is unchanged: the old password still signs in | No password-changed notice; the device's session still answers 200 at Glow's route; a new sign-in with the old password succeeds and its token works |

**Reversals** (the method below):

| ID | The edit | Run | Result |
|---|---|---|---|
| C2-R1 (API) | `conf.py`: the `ACCOUNT_RATE_LIMITS` line removed (allauth's default `5/m/user`) | `manage.py test tests.test_identity_offline tests.test_model_definitions` | `ERROR: test_the_briefed_values … (setting='ACCOUNT_RATE_LIMITS')` (a `KeyError`); `FAIL: test_the_password_change_limit_merges_into_allauths_defaults` with `AssertionError: 5/m/user`; `Ran 38 tests`, `FAILED (failures=1, errors=1)` |
| C2-R1 (suite) | the same edit | the job's SV1 steps, on a new throwaway database | `[identity] FAIL config.settings_as_briefed … FAILED: the password change's limit`; `[identity] FAIL ratelimit.password_change (11, D3) 1.7 s: FAILED: the sixth, with the right password, is refused as too many (answered 401)`; `[identity] cases: 47/49 passed`; `IDENTITY VERDICT: FAIL` |
| C2-R1c (probe) | the same edit, and the case's 429 expectation made true, so the case goes on to its password checks | the same | `[identity] FAIL ratelimit.password_change … FAILED: no password-changed notice (answered 401)`: allauth's default accepted the sixth, the password changed and the notice went out (401 is the answer a completed change gives with `ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE`, as `devices.password_change_ends_both` expects) |
| C2-R1b | `identity_support.py`: `clock_ahead`'s object back to `time` only | the proof's `tests.test_identity_offline` | `ERROR: test_allauths_limiter_runs_on_the_moved_clock`; `ERROR: test_only_time_moves`; `Ran 32 tests`, `FAILED (errors=2)` |
| C2-R1b (suite) | the same edit | the job's SV1 steps | `[identity] FAIL ratelimit.password_change … FAILED: the sixth, with the right password, is refused as too many (answered 500)`: `cache_lock` found no `monotonic`; `48/49`; `FAIL` |

**The record:** the D3 row of "Facts read from the installed source" and the endpoint row for `POST account/password/change` now name the new limit.

### Item 2: the no-link check (F-1; test-only; C2.5)

**Files:**
- `identity_support.py`:
  - `mail_forbidden_found(text, issued_codes)`: for each issued code, `text.replace(code, "")`, a literal replacement of every occurrence; then the text is lowercased and the same eight forbidden strings as before (`MAIL_FORBIDDEN`) are looked for. No pattern, nothing else removed.
  - **Where the codes come from:** `recording_issued_codes(ctx)` wraps Glow's account adapter's `generate_email_verification_code` and `generate_password_reset_code` (allauth's call sites: `account/internal/flows/email_verification_by_code.py:97`, `password_reset_by_code.py:74`). Each code is recorded where it is issued, in `Context.issued_codes`, and added to the ledger; allauth gets it unchanged.
- `identity_cases.py`: `run_case` runs each case inside `recording_issued_codes`; `mail.no_link_no_stranger` requires recorded codes and calls `mail_forbidden_found` with them. It still checks Glow's name, one recipient, no unknown address and no stranger.
- `proofs/postgres-ordering/tests/test_identity_offline.py`: `MailNoLinkCheckTests` (4), on Glow's own messages, rendered by `glow_identity.messages.render` with allauth's two timeouts (900 and 180 seconds) and no Django settings:
  - `test_a_code_spelling_http_passes`: each of the three code messages with the code `HTTP-BCDF`;
  - `test_a_code_ending_www_before_its_full_stop_passes`: each with `BCDF-GWWW`, which ends its sentence (`BCDF-GWWW.`);
  - `test_a_real_link_fails`: with `HTTP-BCDF` issued, an `https://` link, a `www.` address, a link that holds the issued code, and an unissued code-shaped `HTTP-BCDG` each fail, with the forbidden strings named;
  - `test_the_forbidden_list_is_unchanged`.

**Reversals:**

| ID | The edit | Run | Result |
|---|---|---|---|
| C2-R2a | `mail_forbidden_found`: the replacement removed (`pass`) | the proof's `tests.test_identity_offline` | `FAIL: test_a_code_spelling_http_passes` (3 subtests, one per message); `FAIL: test_a_code_ending_www_before_its_full_stop_passes` (3); `FAIL: test_a_real_link_fails (case='a www. address')` (the unremoved code adds `http`); `Ran 32 tests`, `FAILED (failures=7)` |
| C2-R2b | the replacement made a pattern: `re.sub(r"\S*(?:http\|www\.)\S*", "", text, flags=re.IGNORECASE)` | the same | `FAIL: test_a_real_link_fails` for all four cases; `Ran 32 tests`, `FAILED (failures=4)` |

### Item 3: migration 0004's hash (F-3)

- `services/api/tests/test_model_definitions.py`, the `pinned` dictionary only: `"0004_account_age_state.py": "8af86a28d73fb9420b3ec6d59e6c1dcb47dc23c4f21e3c34a2830b171fc1866b"`, the hash the record gives; `sha256sum` of the file at `2f577f8` printed the same.
- **Where the pin lives:** the `pinned` dictionary is in `test_migration_0003_is_additive_and_0001_0002_are_unchanged`. The record's "Commands and results" row says "pinned by `test_migration_0004_adds_the_age_state_only`"; that row is not an owned path, so it keeps its words. The hash is now pinned, by the other test (a note for the manager).
- **C2-R3:** a one-byte change to the migration: the trailing comma after `("glow_persistence", "0003_chat_identity_read_cursor")` replaced by a space (the same list). `FAIL: test_migration_0003_is_additive_and_0001_0002_are_unchanged … (migration='0004_account_age_state.py')`, `AssertionError: 'e9879866…' != '8af86a28…'`; `Ran 38 tests`, `FAILED (failures=1)`.

### Item 4: counts only after a failed secret check (F-4; D10; C2.6)

- `.github/workflows/foundation.yml`, the step "SV1: run the identity suite" only:
  - the comment: "otherwise the log shows counts only, never a line of the suite's output (correction C2, DM-48 C2.6), and the check removes the JSON";
  - the failed branch prints `the full output is withheld; counts only, never a line of the suite's output:`, then `lines in the suite's output: N` (`wc -l`) and `case lines: P passed, F failed` (`grep -c` of `[identity] PASS ` and `[identity] FAIL ` lines). The old `grep -E` of result lines is gone.
- `IdentityUploadGateTests.test_after_a_failed_check_the_step_prints_counts_only`: it takes the failed branch from the step's text, runs it with `bash` on a synthetic log of eight lines (pass, fail, count, scan, verdict, refusal and an unexpected line), and checks that no line of the log, and none of `[identity]`, the case ids, `VERDICT` or `refusing`, is printed, and that the message and both counts (`8`; `2 passed, 1 failed`) are.
- **C2-R4:** the old message and `grep` restored. `FAIL: test_after_a_failed_check_the_step_prints_counts_only` for each of the seven result lines and for `[identity]`: the branch printed the log's lines; `Ran 32 tests`, `FAILED (failures=8)`.
- The passing branch is unchanged; the run of record shows it.

### Item 5: the static guard (F-5; C2.7)

`services/api/tests/test_identity_offline.py`, `StaticGuardTests`:
- `test_the_actor_takes_the_session_from_the_tokens_own_sid` also forbids `request.query_params`, `request.GET`, `request.POST`, `request.COOKIES` and `session_token`, each a subtest.
- New `test_the_actor_is_built_from_the_user_and_the_validated_payload_only`: one call to `actor_for` in the module, with exactly the arguments `user, payload` and no keywords.
- New `test_the_request_reaches_only_allauths_authentication` (C2.7): on the module's syntax tree, every parameter named `request` belongs to `authenticate` or `authenticate_header`; every use of the name `request` is the sole argument of a call `JWTTokenAuthentication().<name>(request)` whose method name is the enclosing function's; no attribute is named `request`; and there are exactly two of each.
- `authentication.py` is unchanged: it already meets the guard.

| ID | The temporary edit to `authentication.py` | Result (`manage.py test tests.test_identity_offline tests.test_model_definitions`) |
|---|---|---|
| C2-R5a | `_ = request.GET` in `authenticate` | `FAIL: test_the_actor_takes_the_session_from_the_tokens_own_sid (forbidden='request.GET')`; `FAIL: test_the_request_reaches_only_allauths_authentication (use='request.GET', line=115)` and its count; `FAILED (failures=3)` |
| C2-R5b | `_ = getattr(request, "GET", None)` | `FAIL: test_the_request_reaches_only_allauths_authentication (use="getattr(request, 'GET', None)", line=115)` and its count; `FAILED (failures=2)`. The list of forbidden names does not catch it; the allow-list does |
| C2-R5c | `actor_for(user, payload, credentials)` | `FAIL: test_the_actor_is_built_from_the_user_and_the_validated_payload_only`; `FAILED (failures=1)` |

### Item 6: the verification settings (F-7)

- `config.settings_as_briefed` checks that `ACCOUNT_EMAIL_VERIFICATION_SUPPORTS_CHANGE` and `ACCOUNT_EMAIL_VERIFICATION_SUPPORTS_RESEND` are off (absent or `False` in the settings), and that 65.21.1 resolves both counts to `0` (`EMAIL_VERIFICATION_MAX_CHANGE_COUNT`, `EMAIL_VERIFICATION_MAX_RESEND_COUNT`).
- **C2-R6:** `conf.py`: `"ACCOUNT_EMAIL_VERIFICATION_SUPPORTS_RESEND": True` added. `[identity] FAIL config.settings_as_briefed … FAILED: ACCOUNT_EMAIL_VERIFICATION_SUPPORTS_RESEND is off`; `48/49`; `IDENTITY VERDICT: FAIL`.

### Item 7: N2's words (F-6; C2.8, replacements 2 to 6)

Each applied word for word; the code's order of checks is unchanged.
- `glow_identity/strategy.py`, the module docstring only: "in this order:" (the line break before "its expiry" moved up one word).
- `docs/architecture/data-model.md`, the replay sentence, and `docs/architecture/production-contracts.md`, "The app mapping as built": "passes allauth's own checks, its signature first, but carries".
- `services/api/tests/test_identity_offline.py`, the comment in `test_the_replay_check_reads_no_session_before_allauths_own_checks` only: "only after allauth's own checks, its signature first."
- **This record, corrected in place:** in "The review plan's security focus", the bullet on a replayed rotated refresh token read "after allauth's own checks, in allauth's order, and adds no cryptography"; it now reads "after allauth's own checks, its signature first, and adds no cryptography".
- **The check:** `git grep -n "allauth's order" -- services proofs docs/architecture` printed nothing (exit 1). In this record the phrase appears only in this section: in its quotation of the old words, and in that search command.

### The threat model

These add to the review's threat model; its section keeps its words.
- **Threat 6, the password-guessing budget** (C2.4): The password-guessing budget (D3): a holder of a live session key or access token can test a password at the sign-in form and at `auth/reauthenticate`, which share `login_failed` (5 per 300 seconds for the address), and at `account/password/change` (`change_password`, 5 per 300 seconds for the account, every signed-in request counted). That is 10 per 300 seconds, twice the sign-in form's 5, the remainder SV1 accepts. A right guess at the password change ends every session and sends the password-changed notice.
  - Proved by `ratelimit.failed_sign_ins`, the reauthentication case and `ratelimit.password_change`, with C2-R1. A wrong current password sends no notice (DM-48 section 3).
- **Threat 7, a message revealing a link:** F-1 is fixed. The check removes only the exact codes issued, recorded where the adapter generates them, so a code spelling `HTTP` or ending `WWW` no longer fails a correct message, and any link elsewhere still fails it (`MailNoLinkCheckTests`, C2-R2a, C2-R2b).
- **The two verification settings (F-7):** `ACCOUNT_EMAIL_VERIFICATION_SUPPORTS_CHANGE` and `ACCOUNT_EMAIL_VERIFICATION_SUPPORTS_RESEND` are off, so a pending verification can neither change its address nor resend its code, and it answers alike whoever holds the address. Pinned by `config.settings_as_briefed` (C2-R6).
- **Threat 5, the actor steered by a header, body or query (F-5):** the guard now forbids the query, form, cookie and `session_token` reads, holds `actor_for` to `user, payload`, and allows `request` only into allauth's own `JWTTokenAuthentication` methods, so `request.session`, `request.body`, `request._request` or `getattr(request, …)` fail it as well (C2-R5a to C2-R5c).

### The method, and the commands

**The reversal method, as before:**
- Each reversal was a temporary exact-once string edit by a scratch helper outside the checkout. It ran on the committed code head (`6da8061`, committed before the push) and restored the file afterwards, checking its SHA-256 and dropping cached bytecode.
- After the reversals, `git status --short` listed only the uncommitted Markdown of the records commit.

**The local database runs** follow P06.DB's D4. A scratch harness outside the checkout ran the job's own step scripts, read from `foundation.yml` with PyYAML:
- the credentials, PostgreSQL's start, the role and databases, then the three SV1 steps;
- then it evaluated the upload step's `if` and simulated the upload by checking the file at its path;
- then the removal step, always.

Each run had:
- a new container from `postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`, published on `127.0.0.1:5433` only;
- passwords, markers and keys generated by the job's own step into a scratch `RUNNER_TEMP`;
- a fresh environment for each step (PATH with the proof's venv first, HOME, LANG, `RUNNER_TEMP`, `GITHUB_OUTPUT`, `GITHUB_RUN_ID=local-…`, `GITHUB_RUN_ATTEMPT=1`, and the step's own env), none of the forbidden names, and every `::add-mask::` line dropped from what was shown;
- the container and directory removed by the job's removal step: `no proof container remains` each time.

**One change to the job's steps, local only:** Docker Hub answered `429 Too Many Requests` to the start step's `docker pull "$IMAGE"`. The image was pulled once by its digest, after one retry, and the harness then replaced that one line with `docker image inspect "$IMAGE"` for the local runs. CI ran the step as written.

| Command | Result |
|---|---|
| `python3.12 -m venv .venv`; `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock` (in `services/api`, and in `proofs/postgres-ordering`) | exit 0 each |
| `GLOW_ENV=test .venv/bin/python manage.py check` | `System check identified no issues (0 silenced).` |
| `GLOW_ENV=test .venv/bin/python manage.py test tests --verbosity 2` | `Ran 453 tests in 16.416s` … `OK` (450 before; 3 new) |
| `.venv/bin/ruff check .`; `ruff format --check .`; `mypy` (API) | `All checks passed!`; `99 files already formatted`; `Success: no issues found in 57 source files` |
| In `proofs/postgres-ordering`: `.venv/bin/python -m unittest discover -s tests -t . -v` | `Ran 193 tests in 12.256s` … `OK` (186 before; 7 new) |
| In `proofs/postgres-ordering`: `ruff check .`; `ruff format --check .`; `mypy` | `All checks passed!`; `52 files already formatted`; `Success: no issues found in 52 source files` (one mypy error in the new test helper, `no-any-return`, was fixed before the commit) |
| `docker pull` of the job's image | first `429 Too Many Requests`; after 5 s, `docker.io/library/postgres@sha256:d74eeac9…` |
| The job's SV1 steps, local baseline on the code | `No changes detected`; `the job's secrets found in the identity suite's output: 0`; `… in the identity results JSON: 0`; `the suite's own scan reported clean: True`; `[identity] PASS ratelimit.password_change (11, D3) 1.6 s: five wrong current passwords refused (400 enter_current_password); the sixth, right, 120 to 121 s after the first: 429 with no error code; the old password still signs in`; `[identity] PASS mail.no_link_no_stranger (3, D8) 0.0 s: 66 messages: …`; `[identity] cases: 49/49 passed in 36.4 s`; `identity secret scan: clean (754 secrets held; 0 found in 240 log records, 102 writes and the results JSON)`; `IDENTITY VERDICT: PASS`; `identity phase: 36 s`; the second run refused with `53 53 63 32 50` before and after; upload condition → runs |
| An earlier local run, before a fix | `[identity] FAIL config.settings_as_briefed … ERROR: AttributeError`: the case first read `account.EMAIL_VERIFICATION_SUPPORTS_CHANGE`, which 65.21.1 does not define (above). Fixed to the settings and the two count properties; never committed |
| `git grep -n "allauth's order" -- services proofs docs/architecture` | no output, exit 1 |
| C2-R1 to C2-R6 | as in the tables above |

### The run of record

**Push run [42669825647](https://github.com/amthorn78/glow-dating-app/actions/runs/42669825647)** (Foundation, run 927, attempt 1) on `6da8061169c4760b8419fc649c6d5aad57f29b50`, the code head, read with the GitHub tools (the jobs, their steps and the job logs; the counts also from the run's log archive).

**Every job `success`:**
- Change scope;
- API checks: `Ran 453 tests in 21.390s` … `OK`; Ruff `All checks passed!`, `99 files already formatted`, mypy `Success: no issues found in 57 source files`; the contracts' `Ran 39 tests` … `OK`;
- API artifact checks;
- API mobile smoke;
- Mobile checks;
- Stream proof checks;
- Database proof checks;
- Foundation gate, which printed **`Application checks passed`**.

**No toolchain retry fired.** Every DM-41 "Wait 60 s …" and "Retry the Python install once" step was `skipped`.

**The Database proof checks job** ran 7 min 40 s of its 30 minutes, from 17:59:03 to 18:06:43 UTC:
- the proof's offline tests: `Ran 193 tests in 11.714s` … `OK`; Ruff `All checks passed!`, `52 files already formatted`, mypy `Success: no issues found in 52 source files`;
- the ordering suite: `== VERDICT: PASS (reference) ==`, `== VERDICT: PASS (adapter) ==`, `== VERDICT: PASS ==`;
- "SV1: show the identity database refuses the other marker, then apply the reviewed migrations from zero": success.

**"SV1: run the identity suite …"** (18:05:58 to 18:06:36):
- the job's check printed `the job's secrets found in the identity suite's output: 0`, `the job's secrets found in the identity results JSON: 0` and `the suite's own scan reported clean: True`;
- then the suite's output: 49 `[identity] PASS` lines, among them `config.settings_as_briefed (D2, D3, D5, D8) 0.1 s`, `ratelimit.password_change (11, D3) 1.6 s: five wrong current passwords refused (400 enter_current_password); the sixth, right, 120 to 121 s after the first: 429 with no error code; the old password still signs in` and `mail.no_link_no_stranger (3, D8) 0.0 s: 66 messages: no link, Glow's name only, each to its owner`;
- then `[identity] cases: 49/49 passed in 36.9 s`, `identity secret scan: clean (754 secrets held; 0 found in 240 log records, 102 writes and the results JSON)`, `IDENTITY VERDICT: PASS` and `results written: .work/identity-results.json`;
- **`identity phase: 38 s (the job's timeout is 30 minutes)`**.

The secret check passed, so the step took its passing branch; the counts-only branch did not run in CI.

**"SV1: show that a second identity run …":** `before: 53 53 63 32 50; after: 53 53 63 32 50`, exit status 1, refused as a used database.

**"SV1: save the identity suite's results JSON, once the secret check has passed":** ran. Artifact `sv1-identity-results`, 3,957 bytes, ID 13699216326.

**The removal step:** `container removed: glow-proof-db-42669825647-1`, `credential and marker files removed`, `no proof container remains`.

### What could not be run, and limits

- **A failed secret check in CI.** The counts-only branch was run offline by its test, on a synthetic log; CI shows only the passing branch. No failing run was pushed, by the push rule and because a reversal does not belong on the branch.
- **The suite-level reversals of item 2** were not run: a real code spelling `HTTP` or ending `WWW` is random, so the offline tests on Glow's own messages carry the three cases.
- **The gap's bounds** are measured from real times around the requests, not read from allauth's stored timestamps; the case requires the measured bounds to lie between 60 and 300 seconds.
- **`actions/upload-artifact` was not run locally;** the upload was simulated.
- **The trusted classifier was not run** in this session. Classification is the manager's.

### Deviations and the stop rule

**The stop rule:** nothing met it.
- 65.21.1's limiter refuses the sixth request at `account/password/change` sent 120 seconds after the first under `5/300s/user` (429), and the override merges into allauth's defaults (above).
- `git diff --name-only 2f577f8 HEAD` lists only the owned paths. `strategy.py` changed in its docstring only; `authentication.py` is unchanged.
- In the workflow, the one hunk pair is in the step "SV1: run the identity suite": its comment and its failed branch.
- No package was added and no lock changed.
- The job stayed within its timeout (7 min 40 s of 30 minutes; the identity phase 38 s).

**Deviations:**
- **The F-7 pin's names.** 65.21.1 has no `EMAIL_VERIFICATION_SUPPORTS_*` properties; the case pins the two settings by name and the two counts allauth resolves from them.
- **The recorder runs per case** (`run_case`), not once around the loop, so `identity_suite.py` is unchanged.
- **Issued codes join the ledger** when they are generated, not only when a case reads one from a message, so the run's own scan also covers codes no case reads (754 secrets held, against 712 at C1's head with one fewer case).
- **The new case also checks** no password-changed notice and the device's session still valid, beyond "the old password still signs in".
- **The 429 expectation names the status it got** (a number), so a reversal shows what the sixth was answered.
- **`strategy.py`'s docstring:** one line break moved by one word, as C2.8 allows.
- **The F-3 pin's test name:** see item 3.

## Manager verification of correction C2 (App Manager 10, 9 November 2026)

- **The session:** started by Nathan from correction C2's prompt, revision 1, at `2f577f89b53c48b493702eebafad9181d9e7a0d4`. Its branch is `claude/trusting-goldberg-e4ogat`, with code head `6da8061` and records head `080c9a9`. Its report was relayed to App Manager 10.
- **The diff** (`git diff 2f577f8 080c9a9`): 11 paths, every one an owned path of "Correction C2".
  - **The non-test lines** (`services/api/glow_identity` and `.github`): 3 files, 19 insertions and 8 deletions, so a delta review on S2's terms applies:
    - `conf.py`: the setting and its comment;
    - `strategy.py`: two docstring lines, with no code change;
    - `foundation.yml`: two hunks, both inside the step "SV1: run the identity suite" of the Database proof checks job. They change its comment and its failed branch, which now prints counts only. The upload's gate is unchanged.
  - **`authentication.py`, the models, the migrations, the locks and the contracts** are unchanged.
  - **The tests and the proof:** the setting's merge test, the counts-only test, the guard's allow-list test and the no-link check's cases. The proof records each code where Glow's adapter generates it, and adds the case `ratelimit.password_change`. `clock_ahead` now keeps `monotonic` and `sleep`.
- **The classification** (`main`'s `scripts/change_scope.py`, extracted outside the tree, `python3 -I`, `--merge-base`):
  - the whole PR at `080c9a9`: `"full": true`, `behavior-or-empty`, 74 paths, one merge base `8d2de72`;
  - C2 alone, from `2f577f8`: `"full": true`, 11 paths.
- **The workflow rule** (`AGENTS.md`): the workflow diff was read whole, and so were the job's actual steps in the run of record (below). Full checks run on the head before the merge.
- **Re-run by the manager** in a scratch export of `080c9a9`, with the session's pinned environments, in clean process environments:
  - the API: `manage.py check`, no issues; `Ran 453 tests`, `OK`; Ruff clean, `99 files already formatted`; mypy `no issues found in 57 source files`;
  - the proof: `Ran 193 tests`, `OK`; Ruff clean, `52 files already formatted`; mypy `no issues found in 52 source files`.
- **Four reversals of the manager's own,** each restored and checked by SHA-256 against `080c9a9`:

  | # | The temporary edit | The result |
  |---|---|---|
  | M1 | the `ACCOUNT_RATE_LIMITS` line removed from `conf.py` | `test_the_briefed_values` errors (`setting='ACCOUNT_RATE_LIMITS'`) and `test_the_password_change_limit_merges_into_allauths_defaults` fails; `FAILED (failures=1, errors=1)` |
  | M2 | the old `grep` of the suite's result lines put back in the failed branch | `test_after_a_failed_check_the_step_prints_counts_only` fails 8 ways (`FAILED (failures=8)`): 7 subtests, one for each line the old `grep` printed, and its plain `[identity]` assertion (corrected after C2's delta review, N-4) |
  | M3 | a pattern removal (`[A-Z]{4}-[A-Z]{4}`) in place of the exact codes | `test_a_real_link_fails` fails on "a code-shaped word that was not issued" |
  | M4 | an alias, `incoming = request`, in `authenticate`: no forbidden name | `test_the_request_reaches_only_allauths_authentication` fails (`use='incoming = request'`) |

- **allauth 65.21.1, re-read:**
  - F-7's two settings are read only as counts: `EMAIL_VERIFICATION_MAX_CHANGE_COUNT` and `…_MAX_RESEND_COUNT` read `EMAIL_VERIFICATION_SUPPORTS_CHANGE` and `…_SUPPORTS_RESEND`, and a `False` gives 0 (`account/app_settings.py:122-140`). So the session's deviation, pinning both the settings and the counts, is right.
  - The two code generators the recorder wraps are the adapter's `generate_password_reset_code` and `generate_email_verification_code` (`account/adapter.py:960-970`). allauth's flows call them through `get_adapter()` (`email_verification_by_code.py:97`, `password_reset_by_code.py:74`).
  - Migration 0004's file at `6da8061` hashes to `8af86a28…1866b`, the pinned value.
- **The run of record,** push run 42669825647 on `6da8061`, read by the manager:
  - **Jobs:** all eight passed, with no toolchain retry. The Database proof checks job took 7 min 40 s.
  - **The identity step:**
    - 0 of the job's secrets in the output and 0 in the results JSON, and the suite's own scan was clean;
    - `[identity] PASS ratelimit.password_change (11, D3) 1.6 s`: five wrong current passwords refused, then the sixth, right, 120 to 121 s after the first, answered 429;
    - `mail.no_link_no_stranger`: 66 messages;
    - `cases: 49/49 passed in 36.9 s`, `identity secret scan: clean (754 secrets held …)`, `identity phase: 38 s`.
  - **After it:** the second identity run was refused with the rows unchanged, and `sv1-identity-results` uploaded 3,957 bytes after the scan.
- **The records push run,** 42671723917 on the session branch's `080c9a9`, concluded `failure` with no job at all. Its log archive is empty (22 bytes), and it lasted 154 s.
  - No test ran in it, and `080c9a9` changes only three Markdown files after the run of record.
  - It is not re-run (OD-58). The manager branch's own push run and PR run on this batch's head run every job on the same code. They are read before the delta review's prompt goes to Nathan.
- **The deviations,** all accepted:
  - **F-7's names:** right, as above.
  - **The recorder runs per case,** so `identity_suite.py` is unchanged.
  - **Issued codes join the secret ledger,** which strengthens the scan.
  - **The new case checks more:** that no notice is sent and that the session stays valid.
  - **The 429 message** names the status it got.
  - **The no-link check removes every code the run issued** from each message, not only that message's own. Codes are never link text, and the forbidden list is unchanged, so what the check looks for is not weakened. The delta review's focus covers it.
  - **F-3's test name:** the record's commands row named `test_migration_0004_adds_the_age_state_only`, which was outside the session's paths. The manager corrected that row in this batch.
- **The limits:**
  - item 4's failed branch ran only offline (CI's scan passed);
  - item 2's suite-level reversal was not run, since a code spelling `HTTP` is random; the three cases are offline;
  - the local runs were iteration only, since Docker Hub limited the image pull.
- **Integrated** by fast-forward of the manager branch to `080c9a9`. Codex's F-1 and F-2 threads on PR42 are answered and resolved once this batch is pushed.
- **Next:** a delta review of C2 on S2's terms, with the exact-head review's security focus. Its prompt is `docs/ephemeral/2026-11-09-sv1-c2-delta-review-prompt.md`.
- **The manager branch's runs on `38d48e2`** (read at 18:36 UTC) lost jobs too, with no step failing:
  - **push run 42673988451:** API checks, API mobile smoke, API artifact checks and Database proof checks passed, the identity suite among them. Change scope, Mobile checks and Stream proof checks are `abandoned` and absent from its job list, so the gate failed with `Change classification failed`;
  - **PR run 42673999110:** four jobs listed and passed (API checks, API mobile smoke, Stream proof checks, API artifact checks). It concluded `failure` with no failed job.

  GitHub's status page reported an unresolved "Incident with Actions and Checks API", investigating from 18:12:37 UTC, with Actions in major outage from 18:14:58. **The explanation, reviewed** (DM-49; OD-21): GitHub lost these jobs; nothing in the repository failed. No step failed in any of the three runs, and the jobs missing differ from run to run. The gate's input gave the missing jobs as `abandoned`, a result GitHub does not document and the workflow cannot set, and the gate failed closed, as designed. The application jobs that ran do not show that the classifier ran: they also run when it does not succeed. The workflow file and every other non-Markdown path are byte-identical from `6da8061` to `cae9cea`. With them, push run 42669825647 on `6da8061` and PR run 42676003277 on `cae9cea` each ran all eight jobs, with `Application checks passed` and the identity suite 49 of 49. GitHub's records were unreliable from about 18:06 UTC: the run of record's gate job is still listed `in_progress`, though its step succeeded and its log reads `Application checks passed`. Nothing was re-run, no empty commit was pushed, and no repair item is needed: the merge rests on a complete PR run on the final head (step 7).

## Delta review of correction C2 (code head `6da8061`)

- **The session:** started by Nathan from C2's delta review prompt, revision 1, at `38d48e226be46275d6d5de4662bb844d374f6ee9`, after DM-49. It reported on 9 November 2026; its report was relayed to App Manager 10.
- **The gates:**
  - the environment check passed;
  - the start gate passed, with one merge base, `8d2de72`, and no non-Markdown path differing from `6da8061`;
  - the trusted classification is `"full": true` (`behavior-or-empty`, 75 paths, run from the repository's root).
- **What it ran:**
  - the API's checks (453 tests) and the proof's (193), with Ruff, format and mypy clean;
  - the F-1, F-2 and F-4 reversals, each failing as the record says, and nine guard probes;
  - informational, on a throwaway PostgreSQL under D4:
    - the suite, 49/49;
    - the F-2 reversal, 47/49, with `ratelimit.password_change` answered 401;
    - a forced failed secret check. It ran the counts-only branch end to end, which CI has not: two count lines, no line of the suite's output, exit 1, and `scan` not set.
- **What it read:**
  - DM-48 whole;
  - the C2 sections and the rows in scope;
  - the touched files, with C2's hunks of `identity_cases.py`;
  - allauth 65.21.1's limiter, headless views and inputs, adapter, code flows, settings and routes;
  - runs 42669825647, 42671723917 and the PR run on `cf03cde` (42683868100, all eight jobs passed).
- **The verdict: changes required, narrowly.** It has one should-fix finding, N-1, on C2.5's wording, with no security effect. It found no blocking finding. If the Dev Manager rules that the run-wide removal meets C2.5, N-1 is a records item and the verdict is approve with nits.
- **Its answers to the focus:**
  - **The limit:** `change_password` resolves to `5/300s/user`, and only it differs from allauth's defaults. The case tells `5/300s` from `5/m`. The moved clock reaches only the limiter's module, during the sixth request.
  - **D3's budget claim holds.** In 65.21.1's `app` client, a signed-in caller can test a password only at three endpoints:
    - `auth/login`, which consumes `login_failed` and `login`;
    - `auth/reauthenticate`, which consumes `login_failed` and `reauthenticate`;
    - `account/password/change`, which consumes `change_password`.
  - **The other focus points:**
    - the codes are recorded only at the two generators;
    - the workflow hunk stays inside its step, and the step still fails;
    - the guard fails every plausible form;
    - C2.8's code changes are a docstring and a comment;
    - both pins hold;
    - nothing else changed.

**The delta review's findings and the manager's dispositions:**

| # | Severity | Finding | Disposition |
|---|---|---|---|
| N-1 | should fix (class: a Dev Manager condition's words; a docstring claiming more than the code) | C2.5 says the check removes "the exact code the case issued… It removes nothing else", and the review's F-1 row says "the message's own code". The code removes every code the run issued from every message (`identity_support.py:469-482`, `identity_cases.py:1728-1732`), and the docstring repeats C2.5's words. The review finds that what the check detects is not weakened: removal is exact, case-sensitive and patternless; removing a code that does not occur in a message changes nothing; and `http`, `://` and `www.` outside a code still fail | **C2.5 met; no code change** (DM-50, option (a)). **C2.5's reading** (DM-50): "the exact code the case issued" covers every code the run's cases issued: each code Glow's account adapter generated during the run, recorded where it was generated (`generate_email_verification_code`, `generate_password_reset_code`) in `ctx.issued_codes`. The check removes each of them from each message, by exact, case-sensitive replacement, wherever it occurs, before it looks for `MAIL_FORBIDDEN`; it removes nothing else and uses no pattern. In 65.21.1 a code is eight letters from `BCDFGHJKLMNPQRSTVWXZ`, in two groups of four joined by a hyphen, so no code can hold `://`, `www.`, `href`, `<a`, `allauth`, `django` or `example.com`. Removing a code can hide only an `http` or a `www.` made with that code's own letters, never a forbidden string outside a code; at worst it joins the text on either side into one, which fails the check. A link anywhere in a message outside a code still fails it, so C2.5 is met. `mail_forbidden_found`'s docstring repeats C2.5 and is read the same way. The docstring's rewording and N-2's pin are carried to the next item that changes the file (the carried-items file, "Carried to SV2"). The delta review's verdict is therefore approve with nits |
| N-2 | nit | "Every occurrence" is pinned by no test: a first-occurrence removal, or a case-insensitive one, still passes, since each Glow message holds its code once | **Carried** (DM-50 1.2) to the first of SV2 to SV4 that changes `identity_support.py` |
| N-3 | nit (claim limit) | The guard's allow-list misses string-keyed access to the request (`locals()['request']`, `sys._getframe().f_locals['request']`). Every plausible form fails it | **Recorded here** as a claim limit: the guard catches plausible forms, not deliberately evasive code |
| N-4 | nit (record) | The manager's reversal M2 said "8 subtests, one for each line the old `grep` printed"; there are 7 subtests and one plain assertion | **Corrected** in place, in "Manager verification of correction C2" |
| N-5 | nit | The counts-only test runs the branch under `set -e`; the job runs it under `-e -o pipefail`. They are equivalent here, since the branch has no pipe, and the review ran it under the job's shell | **Recorded here** |
| N-6 | pre-existing (C1) | The facts table's D3 row said reauthentication for an email change is "off by default and kept off"; since C1, `conf.py` sets it on | **Corrected** in place, with a note |

The review's observation is recorded too. The F-7 pin lives only in the database job's suite; the API's offline fragment test checks the listed keys, not their absence.
