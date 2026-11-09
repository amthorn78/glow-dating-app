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
| D3 | Rate limits (defaults kept): `login_failed` `10/m/ip,5/300s/key`; with verification by code, `confirm_email` `1/10s/key`, a 429 when exceeded; also `change_password` 5/m/user, `manage_email` 10/m/user, `reset_password` 20/m/ip,5/m/key, `signup` 20/m/ip, `login` 30/m/ip | `app_settings.py:268-307`; `email_verification.py:150-187` (the 429 at `:186`), `:335-356` (a sign-in of an unverified address inside the window is refused) |
| D3 | Email change: `ACCOUNT_CHANGE_EMAIL` defaults off; SV1 turns it on (one address; the new one verified before it replaces the old). A verify request for an address another account holds verified is refused `email_taken` | `app_settings.py:147-148`; `allauth/headless/account/inputs.py:119` |
| D3 | Off by default and kept off: login by code (its request routes mount only when enabled); reauthentication for an email change (`ACCOUNT_REAUTHENTICATION_REQUIRED`) | `app_settings.py:553-554`, `:549-550`; `allauth/headless/account/urls.py:103` |
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
| `POST account/password/change` | 401 | ends every session at both layers (`devices.password_change_ends_both`) |
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
- **A replayed rotated refresh token:** refused but not ended in 65.21.1. Glow's subclass ends the session at both layers after allauth's own checks, in allauth's order, and adds no cryptography (`D2-b`, `D2-c`).
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
| Migration 0004: `GLOW_ENV=test .venv/bin/python -c "…"`, calling `makemigrations glow_persistence --name account_age_state` inside `glow_persistence.static_check`'s `no_database_access()` after `setup_static_registry()`; then the generated header removed and Ruff's import order and format applied | `0004_account_age_state.py`, SHA-256 `8af86a28d73fb9420b3ec6d59e6c1dcb47dc23c4f21e3c34a2830b171fc1866b` (pinned by `test_migration_0004_adds_the_age_state_only`) |
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
