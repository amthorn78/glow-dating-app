# P06.3 — Privacy-safe notifications at fixture scope: evidence record

- **Work:** P06.3, privacy-safe notifications at fixture scope ([brief](../../planning/p06-3-notifications.md), revision 2; Outcome items 1 to 5, D1 to D12; [DM-44](../../continuity/dev-manager/reviews/2026-11-08-dm-44-p06-3-brief.md)).
- **Prompt:** [`docs/ephemeral/2026-11-08-p06-3-implementation-prompt.md`](https://github.com/amthorn78/glow-dating-app/blob/da92f1fb71da6c93fae8a747f62c718800a12ae9/docs/ephemeral/2026-11-08-p06-3-implementation-prompt.md), revision 1, from `f9253bd9b0356c95a491df553b17b595105935fd` of the manager branch `claude/magical-wozniak-yfmmx2`.
- **Session:** one implementation session, started by Nathan, 8 and 9 November 2026 (UTC). Branch `claude/gallant-lovelace-vwgu69`, started at `f9253bd`.
- **Code commits:** `e7cb4e9` (Outcome items 1 and 2, `services/api`), then `9c4fef54c71829dea2820a3f9fb66f32ddad57d2` (Outcome items 3 and 4, `apps/mobile`, and one docstring sentence in `notifications.py`). **Code head:** `9c4fef54c71829dea2820a3f9fb66f32ddad57d2`. **Records head:** the last commit on the branch, Markdown only (this record); no code after the code head.
- **Run of record:** push run **42540179430** on `9c4fef5`: all eight jobs `success`, `Application checks passed`, API `Ran 421 tests`, mobile unit `ℹ tests 680`, rendered **`104 passed (4.7m)`**, Mobile 6 min 43 s of 25, no toolchain retry.

## Environment check (names only)

- `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`: none present.
- `STREAM_*`: no name present (`compgen -e | grep -E '^STREAM_'` printed nothing). The session ran in `Glow App - No Stream`.
- GitHub token names `GH_TOKEN` and `GITHUB_TOKEN` are present; never read. Every app command ran without them (`env -i`), and `git fetch`/`git push` ran with both unset.
- **Toolchain:** `node --version` → `v24.19.0`; `npm --version` → `11.9.0`; `python3.12 --version` → `Python 3.12.14`, all three from `$HOME/.local/bin`. That directory is second on this container's `PATH`, after `/nix/var/nix/profiles/default/bin`, which holds none of the three; every command put it first explicitly: `env -i PATH="$HOME/.local/bin:$PATH" HOME="$HOME" LANG=C.UTF-8`, plus `GLOW_ENV=test` for the API commands the README gives it to and `EXPO_OFFLINE=1` for `check:expo` and `export:development`. `npm ci` and `pip install` also passed the proxy and CA variables by reference, never printed.

## Start gate

| Check | Result |
|---|---|
| `git fetch origin claude/magical-wozniak-yfmmx2 main` | fetched; `origin/claude/magical-wozniak-yfmmx2` = `f9253bd9b0356c95a491df553b17b595105935fd` (the prompt's commit is the live manager head); `origin/main` = `8031361` |
| `git switch -C claude/gallant-lovelace-vwgu69 f9253bd…`; `git rev-parse HEAD` | `f9253bd9b0356c95a491df553b17b595105935fd` |
| `git merge-base --is-ancestor 7feba0d… HEAD` | `PR40 present` |
| `git diff --name-only 8031361… HEAD \| grep -v -E '\.md$'` | nothing |
| `git diff --name-only f9253bd… origin/claude/magical-wozniak-yfmmx2 -- apps/mobile services/api 'docs/testing/evidence/*p06-3-notifications*'` | nothing |
| `grep` of `apps/mobile/package.json` | `expo` 58.0.22, `expo-router` 58.0.29, `react-native` 0.88.1 |
| `test -e` of `notifications.py`, `src/notifications`, `src/app/notifications.tsx` | nothing printed: none exists |
| `grep -c "canAccessRoute('/notifications'" apps/mobile/src/app/_layout.tsx` | `0` |
| The brief's "Sessions" | records the prompt ("Next: Nathan runs it") and no implementation session: the prompt is not stale |

**Read before the work, completely:** root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md`, `CLAUDE.md` and `README.md`; `services/api/README.md`; the brief, revision 2; DM-44's report; ADR 0003 (decisions 2 and 3, and its consequences); F12 in `flows-v1.json` and `production-contracts.md`; the `NotificationSettings`, `NotificationIntent`, `DeviceIntent` and `CommandMeta` schemas; `data-model.md` (the device row, the unit-of-work table, the idempotency and replay rule); `domain-and-data-boundaries.md`; `glow_domain` (`chat_reads.py`, `chat_provider.py` and its fixture, `chat.py`, `chat_tokens.py`, `interactions.py`'s `Match`); `glow_chat/contact.py`'s send checks and `delivery.py`'s acceptance step; `apps/mobile/src/chat/` (transport, client, context, copy, store, controls, screen, the no-provider test); `src/contracts/production.ts`; `src/onboarding/routes.ts`, `store.ts`, `context.tsx` and `shell.tsx`; `src/app/_layout.tsx`, `profile.tsx` and `development.tsx`; `rendered/profile-preferences.spec.ts` (the named test at `:309`) and the restricted-fixture tests in `interactions.spec.ts` and `state-corrections.spec.ts`; the Foundation workflow's API, Mobile and gate jobs (the Mobile job's `timeout-minutes: 25`, the rendered suite after `npx playwright install --with-deps chromium`).

**Expo documentation, read 9 November 2026** (fetched with `curl`, kept in the session's scratch directory outside the checkout; text extracted by a script run with `python3 -I`):

| Page | HTTP, bytes | SHA-256 (first 16) |
|---|---|---|
| `https://docs.expo.dev/router/advanced/protected/` (unversioned) | 200, 243,514 | `c70807efa15c2bf8` |
| `https://docs.expo.dev/versions/v58.0.0/sdk/router/` | 200, 2,771,574 | `75db63580dfcd57f` |
| `https://docs.expo.dev/versions/v58.0.0/sdk/notifications/` | 200, 1,894,855 | `40aca90ec90fdf15` (the hash DM-44 recorded for its fetch) |
| `https://docs.expo.dev/llms.txt` | 200, 57,688 | `8aa92fb97e22e58d` |

The one Expo claim this change rests on is the guard's: the protected-routes page says "Expo Router includes all routes by default. Adding Stack.Protected creates exceptions for these screens." and "When a user attempts to access /private, they are redirected to the anchor route". That page has no SDK 58 version; the installed package's source agrees (below), and the rendered test with its reversal proves it in CI. The notifications reference was read only to confirm D6's premise, which this change keeps: no `expo-notifications` is added.

## The cited lines, re-located at `f9253bd`

| Citation (brief or DM-44) | At `f9253bd` |
|---|---|
| PF01 `:356` (P06.3 acceptance), `:350` (P06's development line), `:183` (the ChatBinding/device notifications row), `:269` (the server slices) | `:356`, `:350`, `:183`, `:269` |
| `glow_chat/delivery.py:282` (the acceptance step); `_due_ids` | `:282` (`def accepted`); `_due_ids` at `:388` |
| `glow_domain/interactions.py:108` (`Match`) | `:108` |
| `glow_domain/chat_reads.py:10` ("Whatever refuses a send refuses a read") | `:10` |
| `glow_chat/contact.py:481` (the send requires both accounts `active`) | `:481` (and the same check in match activation at `:248`) |
| `glow_chat/events.py:23-24` (`session_revoked`, `session_expired`) | `:23-24` |
| `src/onboarding/routes.ts:25`, `:33` (the active rule, `/profile`'s line), `:11-16` (`sanitizeDestination`), the "Only fixed public screen identifiers" comment | `:25`, `:33`, `:11-16`, `:10` |
| `src/app/_layout.tsx:50` (`/conversations`' `Stack.Protected`) | `:50` |
| Expo Router 58.0.29 `build/layouts/withLayoutContext.js:71` (`const guardFails = !child.props.guard`) and `build/useScreens.js:163` ("Add any remaining children"), in `node_modules` after `npm ci --ignore-scripts` | `:71`, `:163`; `node_modules/expo-router/package.json` is `58.0.29` |
| `rendered/profile-preferences.spec.ts`, "new private profile routes deny signed-out entry and discard private URL data" | `:309` |
| `flows-v1.json`, F12 | `"id": "F12"` at `:1005` |
| `production-contracts.md`, F12's row; the re-registration sentence | `:72`; `:260` |
| `data-model.md`: the device row; the unit-of-work table; the idempotency rule | `:104`; `:130-137`; `:139` |
| DM-44 section 13's `display-rule.test.ts` lines (`:166-174`, `:249-253`, `:266-269` at `d27324b`) | the file is identical at `8031361` and `f9253bd` (`git diff --quiet` succeeded), so the lines are where DM-44 read them |
| The models D9 names (`glow_persistence/models.py`) | `DeviceRegistration` at `:634` (`installation_id` `:636`, `platform` `:637`, `token_secret_ref` `:639`); `NotificationSettings` at `:651` (`push_enabled` `:653`, `match_updates` `:654`, `message_updates` `:655`) |

## Changes, tests and reversals

**Method.** Each reversal was a temporary edit made by a scratch helper (outside the checkout) that replaced one exact string, which had to occur exactly once, ran the named command in the clean environment, restored the file and checked its SHA-256 against the original. Every file was restored (`restored True` for each, and `sha256sum -c` after each batch); `git status` held no reversal edit afterwards. API reversals ran `manage.py test tests.test_notifications.<case>` with `GLOW_ENV=test`; mobile unit reversals ran `node --test --test-name-pattern=… <file>`.

**A harness fault, found and fixed.** In the first batch of API reversals, "a settings intent accepted without an active registration" left its test passing. The cause was the helper, not the test: the previous reversal's edit and this one both shortened `notifications.py` by exactly 29 characters within the same second, so Python reused the previous run's cached bytecode (same source size and modification time). The helper was changed to delete the file's cached bytecode before and after each run and to run with `PYTHONDONTWRITEBYTECODE=1`, and **all 16 API reversals were run again**; the results below are that second run's. Each failed its test.

**Rendered reversals ran locally against the preinstalled Chromium 1243 headless shell (Chrome for Testing 153.0.8010.12), not the revision `@playwright/test` 1.62.1 pins**, through an uncommitted copy of `playwright.config.ts` under the ignored `apps/mobile/.work/`, identical except for `launchOptions.executablePath`, the web server's `cwd`, its output directory and a `testDir` a probe could override (the P06.2-F record's "Repair pass C5"). They are **informational only**; CI's pinned-browser run is the run of record. No `playwright install` was run.

### Outcome 1 — the notification composer (`services/api/glow_domain/notifications.py`)

The composer is `NotificationService.deliver` (`:980`); its facts come through the `DeliveryFacts` port, read on each delivery by `_contact_refusal` (`:927`); its push is `PushContent(TITLE, WORDING[kind], kind, ROUTES[kind])` (`:1016`; the tables at `:100` and `:104`); the ledger filter is at `:1012`; the transport is the `PushTransport` port, whose only implementation is `FixturePushTransport` in `notification_fixtures.py`. Tests: `services/api/tests/test_notifications.py`.

| Outcome 1 bullet | Test | Reversal | Failing output |
|---|---|---|---|
| A typed trigger names its recipient; at most one push per active device of the recipient; a message notifies the other member, never its sender; a match notifies the member whose earlier like the reciprocal like matched, never the completer | `ComposerRecipientTests` (4 tests: the sender and the completer refused, a stranger refused, one push per device) | **o1-sender:** the `RECIPIENT_IS_SENDER` check deleted | `FAIL: test_a_message_notifies_the_other_member_never_its_sender … AssertionError: Tuples differ: ('sent', '') != ('refused', 'recipient_is_sender')`, `FAILED (failures=1)` |
| The push carries only the kind, Glow's fixed wording and a fixed route | `ComposerContentTests.test_the_push_carries_only_the_kind_glows_wording_and_a_fixed_route` (exact payload; no UUID, ID, account or count in it) and `test_the_wording_and_routes_are_the_fixed_tables` | **o1-payload-identifier:** the route made `f"{ROUTES[kind]}?match={trigger.match_id}"` | `AssertionError: Lists differ: [{'ti[86 chars]tches?match=dd5fdcf0-c629-4f40-b426-16fbc1fe56[154 chars]5'}}] != [{'ti[86 chars]tches'}}, …]`, `FAILED (failures=1)` |
| No trigger field for a body, name, birth data, compatibility data or provider identifier; a trigger with any extra field is refused | `test_the_trigger_types_have_no_field_for_…` (exact field sets, all `UUID`); `test_the_composer_refuses_a_trigger_with_any_extra_field` (a subclass with `text`, a look-alike with `name`, a string recipient, a mapping, `None`: each `trigger_invalid`; the slotted type takes no new attribute); `test_a_trigger_from_an_event_payload_has_exactly_its_fields` (`parse_trigger` refuses `text`, `name`, `birth_date`, `compatibility`, `provider_message_id`, a missing field, an upper-case UUID) | — (the structural tests have no single edit; the slotted, exact-type check is `_trigger_kind`, `:396`) | — |
| Nothing composed when the setting is off, no device is active, or a check that refuses a send refuses it; the facts read on each delivery, never from the trigger | `ComposerRefusalTests` (a block either way, for either member; suspended, deletion pending or deleted; paused or restricted; consent withdrawn; the match unmatched or restricted; a message pending or failed; a message of another match; the setting off; no active device); `FactsOnEachDeliveryTests` (DM-44 2.2's "Tried": after a first delivery the transport failed, a block, an unmatch, the sender's pause, the recipient's withdrawn consent, the recipient's suspension or the setting turned off each refuses the redelivery; a message accepted after a block or an unmatch notifies no one; each delivery reads the facts again) | **o1-block:** `if match.blocked` deleted | 4 subtests: `AssertionError: Tuples differ: ('sent', '') != ('refused', 'blocked')`, `FAILED (failures=4)` |
| | | **o1-account:** the `account_state != "active"` check deleted | 6 subtests; for the recipient `('refused', 'no_active_device') != ('refused', 'account_not_active')` (the suspension's new epoch also ends its device's session), for the other member `('sent', '') != ('refused', 'account_not_active')`; `FAILED (failures=6)` |
| | | **o1-profile:** the `profile_state != "visible"` check made `pass` | 4 subtests: `('sent', '') != ('refused', 'profile_unavailable')`, `FAILED (failures=4)` |
| | | **o1-consent:** the `consent_state != "accepted"` check made `pass` | 2 subtests: `('sent', '') != ('refused', 'consent_not_current')`, `FAILED (failures=2)` |
| | | **o1-facts-from-trigger:** the refusal taken as empty once the trigger's first delivery is recorded (`refusal = "" if trigger.event_id in self._fixed else …`), so the redelivery uses what the first delivery found | 6 failures: e.g. `AssertionError: Lists differ: ['736dfa78-…:053f4928-…'] != []` (a push accepted after the block, the unmatch, the pause and the withdrawal), `('nothing', 'no_active_device') != ('refused', 'account_not_active')`, and `test_every_delivery_reads_the_facts`: `AssertionError: 0 != 4`; `FAILED (failures=6)` |
| Each refusal is a reason code with no personal data | `test_each_refusal_is_a_reason_code_with_no_personal_data` (every code `[a-z_]+`; no UUID in a result's `repr`) | — | — |
| No duplicate push: the first delivery fixes its devices; a later one sends only to a fixed device not yet accepted and still active; the ledger's key is the event ID with the `device_id`; the ledger records only an accepted send; the transport's idempotency key is the ledger's key | `NoDuplicatePushTests` (DM-44 3.3's "Tried": both succeeded then nothing; A failed and B succeeded, then A alone; accepted but not recorded, then refused as a `repeat` and recorded; A revoked and registered again, same key, nothing; C registered after the first delivery, nothing; A revoked after a failure, nothing; the key and the reference; a registration whose session is revoked, expired, from an older epoch or past its expiry is not active) | **o1-second-send:** the ledger filter deleted | `test_a_repeat_after_both_devices_succeeded_sends_nothing … AssertionError: 4 != 2`, `FAILED (failures=1)` |
| It sends only through a push-transport port whose only implementation is a fixture that records what it was given and refuses a repeated key | `test_the_transport_key_is_the_ledger_key_and_the_device_is_its_reference`; `FixtureScopeTests` (the module imports only the standard library, `.chat` and `.provider_fixtures`; the served runtime imports neither notification module and no `glow_api` file names them; the module loads with Django, `glow_persistence`, `glow_chat`, `glow_api` and DRF hidden; the fixtures refuse any environment but development and test) | — | — |

### Outcome 2 — devices and settings (`notifications.py`, F12 per installation)

| Outcome 2 bullet | Test | Reversal | Failing output |
|---|---|---|---|
| The transitions per installation: register from none or revoked; register on active for the same account is F12's rotate; revoke and logout to revoked; settings need the installation active; `CommandMeta` (stale refused, same key other content a conflict, replay changes nothing); the owner's read from a current session; an explicit absence for no registration | `TransitionTests` (register, rotate, revoke, register again; revoke without an active registration forbidden; a second installation; settings need the active registration; stale, conflicting and replayed commands, with no new token stored on a replay; a settings change advances every installation's view; the owner's read, absence for another account's installation, a borrowed session refused; a command for another installation refused; eleven malformed device intents and three malformed settings intents refused) | **o2-settings-without-active:** the precondition narrowed to `if current is None:`, so a revoked registration passes | `FAIL: test_a_settings_intent_needs_the_installations_active_registration … AssertionError: Tuples differ: ('applied', '') != ('refused', 'registration_not_active')`, `FAILED (failures=1)` |
| Owner and session bound: a command from a session no longer current is refused; each registration records the session that last registered or rotated it; a registration whose session is not current is not active for the composer; registering an installation active for another account revokes it first, in the same unit of work | `SessionBindingTests` (revoked, expired, older epoch, past expiry, suspended account, missing session and another account's session, each refused for register, revoke, settings and read, with the registration unchanged; the recorded session follows a rotation; the transfer, and the transfer back) | **o2-stale-session:** `device()`'s session check made `refusal = ""` | 7 subtests: e.g. `('applied', '') != ('refused', 'session_not_valid')`, `('applied', '') != ('refused', 'session_epoch_stale')`, `('applied', '') != ('refused', 'session_not_owner')`; `FAILED (failures=7)` |
| Token custody: the token reaches the token-store port before its reference is saved; a refusal saves nothing | `CustodyTests.test_the_token_reaches_the_store_before_any_reference_is_saved` (a refused store leaves no registration, an absent read and no held token; a refused rotation leaves the registration as it was) | **o2-reference-before-store:** a registration with a placeholder reference saved before `put` | `AssertionError: Registration(account_id=UUID('8b559275-…'), device_id=UUID('35f9c7a9-…'), state='active', version=1, session_id=UUID('ddddc752-…'), ended_by=None) is not None`, `FAILED (failures=1)` |
| When a registration ends (revoke, logout, transfer) or its token is replaced (rotate), the old token is discarded through the port; a failed discard is kept for retry and the state changes anyway; nothing resolves a revoked registration's reference | `test_revoke_discards_the_old_token`, `test_logout_discards_…`, `test_transfer_discards_…`, `test_rotate_discards_…`; `test_a_failed_discard_still_ends_the_registration_and_is_retried` (the registration revoked with no reference; one pending discard; the composer hands the transport no revoked reference; `retry_discards()` drains it) | **o2-discard-revoke**, **o2-discard-logout**, **o2-discard-transfer**, **o2-discard-rotate:** each path's discard removed in turn | each: `AssertionError: TokenReference(<withheld>) not found in []`, `FAILED (failures=1)` |
| The push request names the device by its reference, never its token | `test_the_transport_key_is_the_ledger_key_and_the_device_is_its_reference` (the recorded reference is the registration's; the token is not in it; only the fixture store's test-only `resolve` maps it back) | — | — |
| No read, representation, log line, refusal, exception, receipt or composer output carries the token, nor any read, log line or refusal the reference; no staff projection is added | **The custody test**, `CustodyCaptureTests.test_no_token_or_reference_escapes`: the distinctive synthetic token `SYNTHETIC-FIXTURE-PUSH-TOKEN-CUSTODY-CANARY-7f3a9c-NOT-A-REAL-DEVICE-TOKEN` through register, replay, a conflict, a stale command, a read, settings, rotate, a refused store, a delivery, a refused revoke, revoke, register again, logout, a new session, a transfer, a stale-session refusal and an invalid intent carrying the token, with a handler on the root logger at `DEBUG`; it checks every record's `getMessage()`, `repr(args)` and `msg`, the `repr` and `str` of every result, read, registration, receipt and fixture, four exceptions' text, and what the transport recorded; and every reference against records, reads and refusals | **o2-custody-log-token:** `_register`'s log line given `command.token.reveal()` | `AssertionError: 'SYNTHETIC-FIXTURE-PUSH-TOKEN-CUSTODY-CANARY-7f3a9c-NOT-A-REAL-DEVICE-TOKEN' unexpectedly found in 'notification device command: register SYNTHETIC-FIXTURE-PUSH-TOKEN-CUSTODY-CANARY-7f3a9c-NOT-A-REAL-DEVICE-TOKEN' : the token in a log record`, `FAILED (failures=1)` |
| Logout revokes the registrations the ending session made; the account's others stay active | `test_logout_revokes_the_registrations_the_ending_session_made_and_no_other` | (the logout path's discard: **o2-discard-logout** above) | — |
| Settings default to off for both kinds | `DefaultsTests` (defaults off before and after a registration; the projection's fields are exactly the contract's `NotificationSettings` fields, with no token or reference) | — | — |

### Outcome 3 — the mobile settings screen (`apps/mobile/src/notifications/`, `src/app/notifications.tsx`)

The module follows chat's pattern: `copy.ts`, `permission.ts` (the seam and its fixture), `transport.ts`, `client.ts`, `fixture-adapter.ts` (an in-process F12 stand-in with the server's semantics), `fixture-device.ts` (the synthetic installation and token source), `store.ts`, `context.ts`, `controls.tsx` (the labelled synthetic controls, on the screen behind a toggle, as chat's are; `development.tsx` is unchanged) and `screen.tsx`. Unit tests: `client.test.ts`, `copy.test.ts`, `fixture-adapter.test.ts`, `fixture-scope.test.ts`, `routes.test.ts`, `store.test.ts` (30 tests). Rendered: `rendered/notifications.spec.ts` (7 tests).

| Outcome 3 bullet | Test | Reversal | Failing output |
|---|---|---|---|
| `/notifications`, opened from the profile screen; both kinds start off | `store.test.ts`, "both kinds start off, and a read … is an explicit absence"; rendered "before any request the screen says what each kind sends; both start off and nothing asks at launch" | — | — |
| Turning a kind on is the only thing that asks: undetermined asks once; granted registers unless active, then saves only that kind; denied saves nothing and registers nothing, says so in Glow's wording, and asks again only while undetermined | `store.test.ts`: "turning a kind on asks once while undetermined, registers this installation, then saves only that kind"; "an already granted permission is not asked for"; "a denied permission saves nothing and registers no device; turning on again asks only while undetermined" | **m3-denial-saves:** the denied branch registers and saves anyway | `AssertionError [ERR_ASSERTION]: Expected values to be strictly deep-equal: … actual: { status: 'ready', match: true, message: false, deviceActive: true, denied: true, … } expected: { status: 'ready', match: false, message: false, deviceActive: false, denied: true, … }` |
| Turning a kind off saves only that kind | the granted test above (match off leaves message on, in the store and at the adapter) | — | — |
| Both kinds show off unless this installation's registration is active; the adapter returns an explicit absence; every `NotificationSettings` validated | `store.test.ts`, "the screen shows both kinds off unless this installation's registration is active"; `client.test.ts`, "a not_found read is the explicit absence …" and "only a response the generated NotificationSettings contract accepts reaches the screen" (a `provider_token`, a token reference, `device_state: 'none'`, `version: 0`, another kind, a missing field, an extra envelope field, an error with provider text, non-JSON and `null`: each `invalid_response`) | — | — |
| Every intent passes `parseAppIntent` before the adapter takes it | `client.test.ts`, "an intent that does not follow its contract never reaches the transport" (six device intents and two settings intents, none reaching the transport) | **m3-intent-bypasses-parse:** `parseAppIntent` removed from `NotificationClient.device` | `AssertionError [ERR_ASSERTION]: no failure` (the invalid intent reached the transport and was answered) |
| Before any request, one fixed sentence per kind in Glow's wording, with no name, photo or message text | `copy.test.ts`, "each kind says what it sends, in the server's exact wording, before any request" (the screen's sentence quotes the composer's `WORDING`, read from `notifications.py`) and "the copy carries no name, photo or message text …"; rendered, the two sentences on the screen | — | — |
| Nothing asks at launch, at sign-in or on any other screen | `store.test.ts`, "nothing asks for the permission at launch, at sign-in, on a read or on any other change" (sign-in, reads, an off toggle, suspended, eligible, expiry and logout: `requests` stays 0); rendered, "Times asked: 0." | **m3-asked-at-launch:** `void this.permission.request()` in the store's constructor | `AssertionError [ERR_ASSERTION]: Expected values to be strictly equal: actual: 1, expected: 0` |
| Denied is normal: with the permission denied every other route and journey works; a rendered test walks one | rendered, "with the permission declined, nothing is saved and every other journey works as before" (the denial notice, both off, asked once; then the profile, the recommendation preview with its card, the matches, the private preferences, back to the profile and the settings, and logout) | — | — |
| Logout and an account change revoke this installation through the adapter while the session is still current, then clear the screen's state; the server's `logout` covers a revoke that did not reach it | `store.test.ts`: "logout revokes this installation through the adapter while the session is current, then clears the screen" (the registration ended by the owner's `revoke`, not refused, before `session_ended`; the store idle; no token held); "an account change revokes the earlier session's registration first …"; "the server's logout event covers a revoke that did not reach it" (offline: ended by `logout`); "an expired session sends no revoke …"; "a command from a session Glow no longer holds as current is refused" | **m3-revoke-removed:** the revoke intent never made | `AssertionError [ERR_ASSERTION]: the owner's revoke, not the system's logout … actual: 'logout', expected: 'revoke'` |
| | | **m3-logout-clears-before-revoke:** `this.clear()` moved before the revoke | the same assertion: `actual: 'logout', expected: 'revoke'` |
| | | **m3-session-ends-before-revoke** (an extra one): the session's end delivered before the revoke is sent | the same assertion: `actual: 'logout', expected: 'revoke'` |
| | | **m3-clear-removed:** the clear deleted | `AssertionError [ERR_ASSERTION]: Expected values to be strictly deep-equal: … actual: { status: 'ready', match: true, … deviceActive: true, … } expected: { status: 'idle', match: false, … }` |
| The screen validates every response and refuses a mismatch | `client.test.ts` above | — | — |
| The copy names no provider, Expo, Apple or Google push service; a copy test fails if one appears | `copy.test.ts`, "the new copy names no provider, platform or push service" (every sentence of the copy table against `expo`, `apple`, `google`, `apns`, `fcm`, `firebase`, `android`, `ios`, `onesignal`, `pusher`, `amazon`, `sns`, `stream`, "push service", `token`, `provider`); rendered, no token, Expo, Apple, Google or Firebase on the screen | **m3-provider-term:** the denial sentence made "…in this device’s Apple settings…" | `AssertionError [ERR_ASSERTION]: Notifications are off in this device’s Apple settings. Glow works without them.` against the pattern |
| (D1, D6) No native module, push package, network client, plugin or permission | `fixture-scope.test.ts` (the module imports only React, React Native, Expo Router and the app's own code, and calls no `fetch`, `XMLHttpRequest`, `navigator` or `Linking`; `package.json`, `package-lock.json` and `app.config.ts` name no notification package, plugin or permission); the existing `no-provider.test.ts` passes over the new source | — | — |

### Outcome 4 — the route guard

| Change | Test | Reversal | Failing output |
|---|---|---|---|
| `/notifications` in `SAFE_ROUTES` (`routes.ts:7`) and in `canAccessRoute` with `/profile`'s rule (`routes.ts:33`, the same list); one line in `_layout.tsx:51`: `<Stack.Protected guard={canAccessRoute('/notifications', state)}><Stack.Screen name="notifications" /></Stack.Protected>`; the profile link at `profile.tsx:47` | **Rendered** (`notifications.spec.ts`): "the notification settings route denies signed-out entry and discards private URL data" (`/notifications`, then with `?device=private-sentinel#private-sentinel`: account entry at `/account`, the screen absent, the sentinel not shown); "a suspended account never reaches …" and "a deletion_pending account never reaches …" (an active member opens the screen, the fixture changes to the restriction, then an in-app history navigation to `/notifications` in the same fixture instance: the restricted screen stays, the settings screen and its kinds are absent, the URL is not `/notifications`) | **m4-layout-line-removed:** the layout's line deleted. **Local, informational (Chromium 1243)** | `3 failed`, `4 passed (43.6s)`: `✘ 1 … denies signed-out entry …` with `Error: expect(locator).toBeVisible() failed`; `✘ 2 … a suspended account …` and `✘ 3 … a deletion_pending account …`, each `Error: expect(locator).toHaveCount(expected) failed … unexpected value "1"` (the settings screen rendered) |
| | **Unit** (`routes.test.ts`): `/notifications` equals `/profile`'s rule and "an active account with a valid session" in every state (signed out, active, deleted, revoked session, consent withdrawn, suspended, deletion pending, underage, unknown policy, expired); anonymous, unverified, expired, suspended and deletion-pending sessions refused; a fixed, query-free destination, and `SAFE_ROUTES` exactly the earlier list plus `/notifications` | **m4-canaccess-widened:** `/notifications` taken out of the list and given `state.account?.session_state === 'valid'` | `AssertionError [ERR_ASSERTION]: deleted … actual: true, expected: false`, and in the second test `actual: true, expected: false` |
| Nothing else the guard allows changes (D7) | `SAFE_ROUTES`' exact list above; `git diff f9253bd HEAD -- apps/mobile/src/app/_layout.tsx` is the one line, and `routes.ts` the two entries | — | — |

**A probe, not a reversal (local, informational).** Before writing the restricted tests, a scratch spec under `.work/` tried two ways to reach `/notifications` in-app as a suspended member: browser back left the app (`about:blank`), so it cannot test the guard; an in-app history navigation (`history.pushState` and a `popstate` event) kept `/restricted` with the line, and **without the line rendered `screen-notifications` at `/notifications` for the suspended member** (`B url http://localhost:8081/notifications screens [ 'screen-notifications' ]`). That is DM-44's main finding, shown in a browser: the route file alone is an unguarded screen.

## Outcome 5 — the field mismatch, and what waits (D9)

**The mismatch, recorded; neither side changed:**
- the contract's `NotificationSettings` has `match_notifications`, `message_notifications` and `device_state`; the model has `push_enabled`, `match_updates` and `message_updates` (`models.py:651-655`);
- the contract's `DeviceIntent` has `device_id` and no platform; `DeviceRegistration` has `installation_id`, `platform` and `token_secret_ref` (`models.py:634-639`);
- the contract's `NotificationSettings` has one `device_state`, with no value for an installation that never registered, while an account may hold several registrations: at fixture scope `device_state` describes the requesting installation's registration and the settings are the account's; whether settings belong to the account or the device, and how a read names its installation, are decided by the slice that serves F12;
- the contract's `DeviceIntent` has no `rotate` action: at fixture scope a `register` for an installation already active for the same account is F12's `rotate`;
- `DeviceRegistration` records no session, while F12 binds a registration to the session that made it: the domain records it at fixture scope, and the serving slice decides how the model holds it;
- the mapping, and whether `push_enabled` or a platform belongs in the contract, are decided by the slice that serves F12.

**Fixture-scope decisions this session made where the contract is silent, for SV4 to confirm or replace** (each in `notifications.py`'s module docstring):
- **One version for two objects.** `NotificationSettings` has one `version`, so it is the installation's view revision: 1 at the account's first registration of the installation, advanced by every change to that registration and by every change to the account's settings (which advances all of the account's registrations together). A `DeviceIntent`'s `expected_version` is 0 for no registration, else that revision; a `NotificationIntent`'s is the requesting installation's. So two installations of one account cannot overwrite each other's settings change unseen.
- **The requesting installation** reaches the domain in the trusted `Caller` (account, session, installation), never as an intent field, since `NotificationIntent` has no `device_id`; a `DeviceIntent` must name the caller's own installation (`wrong_installation` otherwise).
- **Per-(account, installation) records.** The domain keeps one registration per account and installation, with at most one active per installation; the model's `installation_id` is unique across accounts. How the model holds an earlier owner's revoked row is the serving slice's.
- **A registration whose session is no longer current** reads as `active` (F12's state) but is not active for the composer. `logout(session_id)` is the system's F12 logout for any session that ends; with `session_revoked` and `session_expired` wired to it (SV4), such a registration is revoked and reads as `revoked`.
- **The match's completer.** The composer's match rule needs the member whose like completed the match; `Match` names two participants and no actor (`interactions.py:108`), so the facts port supplies it (`MatchFacts.completed_by`), and SV4's adapter reads it from the two directional likes.
- **The receipt's digest** is an HMAC-SHA256 under a per-service random key over the canonical intent, so the same key with another token conflicts while the receipt cannot confirm a guessed token.
- **On mobile, Glow's API learning of a session's end.** The onboarding fixture's sign-out is local and synchronous, and `src/onboarding/store.ts` does not change (D7). So the fixture adapter keeps its own record of current sessions, and the store tells it (`SessionRelay`) when a session starts and, after this installation's revoke has settled, when it ended; that end is the system's F12 `logout`. It stands in for a real client sending its device revoke, then its sign-out. An expired session sends no revoke. The onboarding store publishes a sign-out or an expiry as two synchronous notifications (cleared, then expired), so the store decides on the settled account one microtask later, before any render.

**What waits, and for whom:**
- F12's HTTP surface, its ORM adapters and the triggers' wiring: **SV4** (DM-44 item 7). A message's acceptance (`glow_chat/delivery.py:282`) writes no outbox event today, and `match_activated` is a delivered chat event the chat worker settles when it creates the channel, so the notification triggers need events of their own, or a change to P06.2's proven delivery code under its database proof. `session_revoked` and `session_expired` (`events.py:23-24`) are logical events with no consumer yet, which the system's `logout` can follow.
- The native module, permission prompts on devices, credentials and the Expo project: **P09.2**, with Nathan's release authorization; with it, the seam's real implementation and its answers (including whether it may ask again), Android's notification channel, and a tapped notification's route through `sanitizeDestination` and the guard.
- The real transport, live delivery, rotation and retries against the provider, and duplicate paths reconciled: **P11B** (PV05); with it, a push's lifetime (TTL), collapse on the device, and how many pushes a burst of messages makes.

## Glow's wording

- **The push (D4, fixed by the brief):** title `Glow`; "You have a new match." and "You have a new message."; data `{kind, route}` with `/matches` or `/conversations`.
- **The screen's sentence per kind (written by this session, Outcome 3 and DM-44 4.2):** "When you have a new match, Glow sends “You have a new match.” and nothing else." and "When you have a new message, Glow sends “You have a new message.” and nothing else."
- **The denial:** "Notifications are off in this device’s settings. Glow works without them." The rest of the copy table is `src/notifications/copy.ts`. Nathan may change any of it; a change is a copy-table edit and its test.

## Commands and results

| Command (clean environment) | Result |
|---|---|
| `python3.12 -m venv .venv`; `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock` | exit 0 (pip's own upgrade notice only) |
| `GLOW_ENV=test .venv/bin/python manage.py check` | `System check identified no issues (0 silenced).` |
| `GLOW_ENV=test .venv/bin/python manage.py test tests --verbosity 2` | `Ran 421 tests` … `OK` (366 before; 55 new) |
| `GLOW_ENV=test .venv/bin/python smoke.py` | `PASS /health/live: HTTP 200`, `PASS /health/ready: HTTP 503`, `PASS /api/v1/development/recommendations: HTTP 200` |
| `.venv/bin/ruff check .` | `All checks passed!` |
| `.venv/bin/ruff format --check .` | `81 files already formatted` |
| `.venv/bin/mypy` | `Success: no issues found in 43 source files` |
| `GLOW_ENV=test .venv/bin/python -m glow_persistence.static_check` | `Static definitions agree: 34 app models; migrations=0001_event_infrastructure,0002_app_domain,0003_chat_identity_read_cursor` |
| `npm ci --ignore-scripts` (apps/mobile) | exit 0 |
| `npm run check` | typecheck and lint clean; `ℹ tests 680`, `ℹ pass 680`, `ℹ fail 0` (650 before; 30 new) |
| `EXPO_OFFLINE=1 npm run check:expo` | `Dependencies are up to date` (with Expo's "Dependency validation is unreliable in offline-mode") |
| `EXPO_OFFLINE=1 npm run export:development` | exit 0; `Android Bundled 16948ms … (1369 modules)`, `iOS Bundled 16951ms … (1370 modules)`, `Exported: .work/native-export` |
| `npx playwright test -c .work/local-rendered.config.ts notifications.spec.ts` | **informational (Chromium 1243):** `7 passed (12.3s)` |
| `npx playwright test -c .work/local-rendered.config.ts` (the whole suite) | **informational (Chromium 1243):** `104 passed (5.2m)` (97 inherited, 7 new) |
| The trusted classifier: `git show f9253bd:scripts/change_scope.py` to the scratch directory (SHA-256 `b564c62f4a076f51…`), run with `python3 -I … --base f9253bd… --head 9c4fef5… --merge-base` | `{"full": true, "reason": "behavior-or-empty", "paths": […24 paths…]}` |
| `git diff --name-only f9253bd… 9c4fef5…` | 24 paths, each an owned path: the three new API files, `apps/mobile/src/notifications/**`, `src/app/notifications.tsx`, `rendered/notifications.spec.ts`, and `routes.ts`, `_layout.tsx` and `profile.tsx` for D7's entries, line and link |
| The 16 API and 10 mobile reversals | each failed its test as recorded above; every file restored |

## The run of record

**Push run 42540179430** (Foundation, run 881, attempt 1) on `9c4fef54c71829dea2820a3f9fb66f32ddad57d2`, the code head; `completed`, conclusion `success`, 00:26:21 to 00:33:56 UTC on 9 November 2026. Read with the GitHub tools: the job list, each job's steps, and the API, Mobile and gate logs (the Mobile log searched from the run's log archive, downloaded to the scratch directory).

| Job | Result | Detail |
|---|---|---|
| Change scope | success | the trusted classification step passed (full scope) |
| API checks | success | `manage.py check` and **`Ran 421 tests in 13.181s` … `OK`**; `All checks passed!`, `81 files already formatted`, `Success: no issues found in 43 source files`; the contracts suite `Ran 39 tests … OK` |
| Mobile checks | success | `@glow/contracts` `ℹ tests 586`, `ℹ pass 586`, `ℹ fail 0`; `@glow/mobile` **`ℹ tests 680`, `ℹ pass 680`, `ℹ fail 0`**; `Dependencies are up to date`; `export:development` (`iOS Bundled … (1330 modules)`, `Android Bundled … (1369 modules)`, `Exported: .work/native-export`); Chrome for Testing 151.0.7922.34 (`playwright chromium v1234`) installed; the rendered suite **`104 passed (4.7m)`**, with no failed, flaky or skipped line, the seven new tests among them (`✓ 61` to `✓ 67`, `rendered/notifications.spec.ts:42`, `:53` twice, `:69`, `:81`, `:115`, `:139`); the layout artifact uploaded (2 files, `p04-empty-form-layout`, artifact 13640844313). **Duration: 6 min 43 s of the 25-minute timeout** (00:26:30 to 00:33:13 UTC) |
| API mobile smoke | success | `node scripts/smoke.mjs && node --test scripts/smoke.test.mjs` passed |
| API artifact checks | success | the pinned image built, inspected and smoked |
| Stream proof checks | success | its unit tests, `ruff`/`mypy`, the client syntax check and `checks/run_plan.py` |
| Database proof checks | success | the disposable PostgreSQL proof, both subjects and the delivery phase |
| Foundation gate | success | **`Application checks passed`** |

**Toolchain retry:** none fired. In the API, smoke, Stream proof and Database jobs, the first `actions/setup-python` attempt succeeded and both "Wait 60 s before the one retry of the Python install (DM-41)" and "Retry the Python install once (DM-41)" were `skipped`.

## What could not run, and limits

- **The rendered suite on the pinned browser** runs only in CI (`playwright install` is forbidden here). Every local rendered result above is **informational**: Chromium 1243 headless shell, not the pinned revision.
- **No provider, device or native behavior** is proven: there is no push transport, credential, network client or native module (D1, D6). The permission seam's only implementation is a fixture; the platform's prompt, its answers and Android's channel are P09.2's.
- **The F12 domain is in memory**: no database, ORM adapter, HTTP route, outbox consumer or trigger wiring (SV4). Exactly-once delivery by a real provider is P11B's.
- **The mobile adapter is a presentation substitute** that follows the domain's rules; the Python domain stays authoritative.
- **No staff projection** was added (Outcome 2 allows one; none was needed).
- **Deviations from the brief:** none in scope or guards. Two placements the brief left open: the `canAccessRoute('/notifications', …)` unit test is in `src/notifications/routes.test.ts` (no onboarding routes test file exists), and the fixture controls sit on the settings screen behind a labelled toggle, as chat's do, so `development.tsx` is unchanged. The extra reversals (each composer refusal on its own, the four discard paths, and the session ending before the revoke) go beyond the prompt's list.
- **Nothing met the stop rule.** No guard's allowance changed beyond D7's entries and line; no dependency, lock, contract, model or migration changed; no path outside the owned paths; `chat_reads.py` was neither changed nor imported (the composer reads the same facts through its own port).

## Manager verification (9 November 2026, App Manager 10)

- **The branch:** `claude/gallant-lovelace-vwgu69`, with the code head `9c4fef5` and the records head `7775bba`, starts at the prompt's commit `f9253bd`. `git diff --name-only f9253bd 7775bba` lists 25 paths, all owned: 24 code paths, and the record, which is the records commit's only path.
- **The guard edits are D7's, and nothing else:**
  - `_layout.tsx`: one added `Stack.Protected` line for `/notifications`;
  - `routes.ts`: `/notifications` added to `SAFE_ROUTES` and to `/profile`'s list;
  - `profile.tsx`: one link.
- **The classifier:** the trusted classifier, taken from `main` at `8031361`, reads the change as `"full": true` (`behavior-or-empty`), with one merge base.
- **A search of the code diff (`f9253bd..9c4fef5`)** for network clients, native modules, provider SDKs, Expo push, Firebase, APNs and `google-services`:
  - the only matches are tests that guard against them (`fixture-scope.test.ts`, `copy.test.ts`, the rendered spec);
  - no provider name appears in non-test source;
  - no file outside `glow_domain/notification*.py` and its test imports the new server modules, so the served runtime does not load them;
  - the push wording is D4's: `TITLE = "Glow"`, *"You have a new match."*, *"You have a new message."*, and the routes `/matches` and `/conversations`.
- **The run of record,** push run 42540179430 on `9c4fef5`, read with the GitHub tools:
  - all eight jobs `success`;
  - the gate's log ends `Application checks passed`;
  - the Mobile job's log ends `104 passed (4.7m)`; the job ran from 00:26:30 to 00:33:13 UTC;
  - every "Wait 60 s …" and "Retry the Python install once (DM-41)" step is `skipped`.
- **Six reversals re-run** in a scratch copy of `9c4fef5` (`git archive`, outside the checkout), with clean process environments. Python ran with `PYTHONDONTWRITEBYTECODE=1` and its caches cleared, and each file was restored and its SHA-256 checked:
  - **baselines:** `tests.test_notifications`, `Ran 55 tests … OK`; `store.test.ts` and `routes.test.ts`, exit 0;
  - **o1-sender:** the `RECIPIENT_IS_SENDER` check deleted. `FAIL: test_a_message_notifies_the_other_member_never_its_sender … ('sent', '') != ('refused', 'recipient_is_sender')`;
  - **o2-custody-log-token:** the register log line given `command.token.reveal()`. `FAIL: test_no_token_or_reference_escapes … 'SYNTHETIC-FIXTURE-PUSH-TOKEN-CUSTODY-CANARY-…' unexpectedly found in 'notification device command: register SYNTHETIC-…'`;
  - **o2-settings-without-active:** the precondition narrowed to `if current is None:`. `FAIL: test_a_settings_intent_needs_the_installations_active_registration … ('applied', '') != ('refused', 'registration_not_active')`;
  - **m3-denial-saves, in the manager's own form:** the denied branch made unreachable (`&& false`), so a denial registers and saves. The test "a denied permission saves nothing …" fails: `actual: { … match: true, … deviceActive: true, denied: false … }`;
  - **m3-logout-clears-before-revoke:** `this.clear()` added before the revoke intent is made. `AssertionError: the owner's revoke, not the system's logout … actual: 'logout', expected: 'revoke'`;
  - **m4-canaccess-widened:** `/notifications` given `session_state === 'valid'` alone. `AssertionError: deleted … actual: true, expected: false`.
- **Not re-run by the manager:** the rendered layout-line reversal. Only CI has the pinned Chromium; the session's local run is informational, and the exact-head review re-runs it (DM-44 9.1).
- **Integrated:** the manager branch fast-forwarded to `7775bba`.

## Codex's review of `1dc1b0b` (9 November 2026, App Manager 10)

- **Codex's code review completed on `1dc1b0b`** (PR41's head at 00:49:27 UTC; its code is `9c4fef5`'s), with one finding.
- **F-C1** (P2, `apps/mobile/src/notifications/fixture-adapter.ts:111`): `device`, `settings` and `notifications` take the session's account (`capture`, `:120`) before `await this.gate()` (`:127`), and act on it afterwards. So if a request starts while its session is current and `ended()` runs before the gate resolves, the request still acts for the ended session.
- **The manager reproduced it:**
  - **setup:** a scratch copy of `apps/mobile` at `1dc1b0b` (`npm ci --ignore-scripts`), and a probe test run with `node --test`;
  - **steps:** `started(session)`; then `device(session, device, register)`, not awaited; then `ended(session)`; then the request awaited;
  - **result:** the answer is a success with `device_state: 'active'`. `registrationsView()` shows the registration `active`, bound to the ended session's ID, with `endedBy: null`, and `heldTokens` is `1`. The probe passed as a probe; it asserts nothing.
- **Reach:**
  - only the mobile fixture adapter, a presentation substitute for F12;
  - the Python domain, which is authoritative, checks the session inside each command, synchronously;
  - whether the store's own flows can reach it (a register in flight at logout or an account change) goes to the exact-head review.
- **Disposition:** it falls in a correction class the review names ("let a stale session act, or leave a registration active after its session's logout"), so rule (a) fixes it before the merge. Under step 6 it joins the exact-head review's pass: the review prompt's revision 2 adds it as focus item 8, and its fix goes in the correction pass after the review. The manager replied on Codex's thread, which stays open until the fix is on PR41.

## PR41's runs and Codex on `481562f` (9 November 2026, App Manager 10)

- **The runs on PR41's heads, all `success`:**
  - on `1dc1b0b`: push run 42541927007 and PR run 42541971693;
  - on `481562f`: push run 42542771838 and PR run 42542778816.

  Both heads hold `9c4fef5`'s code. The manager pushed `481562f` only after both runs on `1dc1b0b` had finished, so neither was cancelled.
- **Codex's code review of `481562f`** (the commit that holds the review prompt's revision 2) completed at 00:57:55 UTC with no new finding. Its summary's "unresolved" state is F-C1's thread, open by design until the fix is on PR41.
- **The exact-head review prompt,** revision 2 at `481562f`, went to Nathan once Codex had completed on the code head and on the prompt's commit (step 6).

## Exact-head review of P06.3 (9 November 2026)

- **The review:** prompt revision 2 at `481562f`, of code head `9c4fef5`, run in `Glow App - No Stream`; Nathan's pick: not recorded.
  - The environment check, the start gate and the classification (`"full": true`) passed.
  - **Verdict: changes required.** No blocking finding; two should-fix findings in correction classes; three nits.
  - It wrote the threat model DM-44 9.1 asks for: assets, actors, entry points, and each threat with its stopping code and test. Every threat has both, apart from F-1 (the session binding) and F-2 and F-3 (the fixture-only guards).
- **The findings and their dispositions** (step 6, "Fix or carry, by rule"):

| # | Severity, class | What | Disposition |
|---|---|---|---|
| F-1 | Should fix; in a correction class (a stale session acts; a registration stays active after its session's logout) | Codex's F-C1, confirmed. `fixture-adapter.ts:101-118`: `settings`, `device` and `notifications` read the session before `await this.gate()` and act after; `ended()` sweeps synchronously. **The store's own flows reach it:** `setKind('match', true)` then `owner.logout()`, or an account change, in the same task, with the permission granted or undetermined-and-allowed. Each ends with `register` after `session_ended`, the registration active on the ended session, and `heldTokens` 1. A logout in a later task, as a tap is, does not reach it. No other place has the pattern: the store checks its epoch after every await, and the client holds no session state | **Fix before the merge** (rule (a)): correction C1, item 1 |
| F-2 | Should fix; in a correction class (a record claim more than the test shows) | `test_notifications.py:1105-1134` records a relative import as its dots plus module name, so `from . import X` is `"."` for any X. The probe `from . import chat_provider_stream` (a sibling that imports `httpx`, `jwt` and `getstream`) passes all four `FixtureScopeTests`. The served runtime is unaffected (the sealed-runtime test holds) | **Fix before the merge** (rule (a)): correction C1, item 2, makes the test true to the record's claim |
| F-3 | Nit | `fixture-scope.test.ts:22` misses the bare side-effect form `import '…'`, which `no-provider.test.ts` covers. The probe `import 'expo-device';` passes both tests | **In C1** as item 3: one pattern in the same guard class as F-2, with its reversal |
| F-4 | Nit | `notifications.py:611-613`, `:1002`, `:1032`: `_fixed` and `_ledger` grow without bound in the in-memory fixture; `MAX_RECEIPTS` bounds receipts only | **Carried to SV4** (the carried-items file): the ledger's real storage, its bound and its retention |
| F-5 | Nit | `store.ts:136`: `await this.permission.request()` has no catch; a seam that rejects would leave `busy` set. The fixture seam never rejects | **Carried to P09** (the carried-items file): P09.2's real permission seam handles a rejection |

- **Record corrections** (focus 7), recorded here and not made in the session's sections:
  - **an unrecorded reversal:** the composer's own session check has a test but no recorded reversal. The review made `_active_for_composer`'s session clause `True`, and `NoDuplicatePushTests` failed (failures=4);
  - **"the first delivery fixes its devices"** means the first delivery that passes the checks, as the docstring says.
- **The review's re-runs,** in a scratch copy of `9c4fef5`, each failing its test:
  - o2-custody-log-token, o2-stale-session (7), the composer's session check (4) and o1-facts-from-trigger (6);
  - m3-session-ends-before-revoke and m3-revoke-removed;
  - m4-layout-line-removed: 3 failed and 4 passed. This one ran on the preinstalled Chromium 1243 and is informational.

  Its own checks: API `Ran 421 tests … OK`, ruff and mypy clean, `smoke.py`, `static_check`, and mobile `npm run check` with 680 passing.
- **The runs it read:**
  - run 42540179430, as recorded;
  - PR41's `pull_request` runs: 42541971693 on `1dc1b0b`, 42542778816 on `481562f`, and 42543652678 on `00e5f26`, each with all eight jobs `success` (Mobile `104 passed (5.2m)` on `00e5f26`).

  Push run 42543647486 on `00e5f26` also passed.
- **The design fit of C1's fix** (the manager's reading of step 6's consultation rule):
  - F-1's fix makes the mobile fixture adapter do what DM-44 1.2 already says: "a command from a session that is no longer current is refused". The authoritative Python domain does this inside each command;
  - the fix changes no design, interface, contract or dependency, and the adapter enforces nothing in production;
  - so the manager writes C1 without a consultation, and the Dev Manager's next consultation sees this disposition.

## Correction C1

- **Prompt:** [`docs/ephemeral/2026-11-09-p06-3-c1-correction-prompt.md`](https://github.com/amthorn78/glow-dating-app/blob/da92f1fb71da6c93fae8a747f62c718800a12ae9/docs/ephemeral/2026-11-09-p06-3-c1-correction-prompt.md), revision 1, from `3a2b930057f5a952023dc26a55c3338ce6dd5b46` of the manager branch `claude/magical-wozniak-yfmmx2`. Its specification is the brief's revision 3, "Correction C1", items 1 to 4.
- **Session:** one correction session, started by Nathan, 9 November 2026 (UTC), in `Glow App - No Stream`. Branch `claude/peaceful-feynman-ozlu2l`, started at `3a2b930`.
- **Code commits:** `85ae241` (item 1), `109d2ee` (item 2), then `e807ce8719ca0081942081eb7b64db9c28af0bc9` (item 3). **Code head:** `e807ce8`. **Records head:** the commit that adds this section, Markdown only; no code after the code head.
- **Run of record:** push run **42549675849** on `e807ce8`. All eight jobs `success`, `Application checks passed`, API `Ran 422 tests`, mobile unit `ℹ tests 691`, rendered **`104 passed (5.3m)`**, no toolchain retry.

### Environment check (names only)

- `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`: none present (the prompt's loop printed nothing).
- `STREAM_*`: no name present (`compgen -e | grep -E '^STREAM_'` printed nothing).
- GitHub token names `GH_TOKEN` and `GITHUB_TOKEN` are present; never read. `git push` ran with both unset (`env -u`).
- **Toolchain:** `node --version` → `v24.19.0`; `npm --version` → `11.9.0`; `python3.12 --version` → `Python 3.12.14`, from `$HOME/.local/bin`, put first on `PATH`. Every repository command ran in `env -i PATH="$HOME/.local/bin:$PATH" HOME="$HOME" LANG=C.UTF-8`, plus `GLOW_ENV=test` for the API commands. `npm ci` and `pip install` also passed the proxy and CA variables by reference, never printed.

### Start gate

| Check | Result |
|---|---|
| `git fetch origin claude/magical-wozniak-yfmmx2 main` | fetched; `origin/claude/magical-wozniak-yfmmx2` = `3a2b930057f5a952023dc26a55c3338ce6dd5b46` (the prompt's commit is the live manager head); `origin/main` = `8031361` |
| `git switch -C claude/peaceful-feynman-ozlu2l 3a2b930…`; `git rev-parse HEAD` | `3a2b930057f5a952023dc26a55c3338ce6dd5b46` |
| `git diff --quiet 9c4fef5… HEAD -- .github scripts services apps packages proofs` | `the code is 9c4fef5's` |
| `git diff --name-only 3a2b930… origin/claude/magical-wozniak-yfmmx2 -- apps/mobile services/api` | nothing |
| `git show origin/claude/magical-wozniak-yfmmx2:<this record> \| grep -c -E '^#+ Correction C1'` | `0` |

**Read before the work, completely:** root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md`; the brief's "Correction C1" (with its header, Outcome and "Sessions"); this record's "Exact-head review of P06.3" and the "Outcome 2" and "Outcome 3" tables; `fixture-adapter.ts`, `store.ts`, `transport.ts`, `fixture-adapter.test.ts`, `store.test.ts` and `fixture-scope.test.ts`; `notifications.py`'s `_session_refusal`; `test_notifications.py`'s `FixtureScopeTests`. Also read, without change: `client.ts`, `permission.ts`, and `no-provider.test.ts`'s specifier patterns.

### Item 1 — F-1: the fixture adapter re-checks the session after its await

- **Files:** `apps/mobile/src/notifications/fixture-adapter.ts` (the change); `fixture-adapter.test.ts` and `store.test.ts` (the tests).
- **The change:** `settings`, `device` and `notifications` now call `capture(session)` after `await this.gate()`, in the same synchronous step as the read or the command, as `notifications.py` checks the session inside each command. The intent is still copied before the await (the request's body as sent). A request whose session ended while it awaited gets `unauthenticated` and changes nothing. Nothing else in the adapter changed: the offline scenario still throws at the gate, and a lost response still commits and then withholds the answer.
- **The semantics:** the only difference from `9c4fef5`'s adapter is that an ended session's request is refused. The Python domain is unchanged.
- **The adapter's tests** (`fixture-adapter.test.ts`, 2 new):
  - "a register, a settings save and a read whose session ended while they awaited are refused and change nothing": the three requests start, `ended(A)` runs, then each is awaited. Each is `unauthenticated`; there is no registration; `heldTokens` is 0; the account's settings are both off; no `register`, `rotate` or `settings` event;
  - "each request from a session that ended while it awaited is refused, even where another current session holds the registration": the account's later session registers the installation first, so a stale rotate, save or read would otherwise succeed. Each is `unauthenticated`; the later session's registration is unchanged (active, its session, version 1); `heldTokens` is 1, the later session's token.
- **The store's tests** (`store.test.ts`, 8 new, one loop): `setKind('match', true)`, then `owner.logout()` or an account change (`owner.scenario('eligible')`), with the permission preset `granted` or `undetermined_allow`, in the same task or in a later task (after a `setImmediate`). Each case asserts that the ended session is not current, that no registration is active on it, that `heldTokens` is 0 and that the store is idle.
  - **Same task** (4 cases): no registration at all, and exactly one device refusal, `unauthenticated`: the in-flight register reached the adapter and was refused.
  - **Later task** (4 cases): the register committed, and the owner's revoke ended it (`endedBy: 'revoke'`). These pass at `9c4fef5` too, as the review found.
- **Before the change:** the new tests, run against `9c4fef5`'s adapter, fail 6 of 29 in the two files: both adapter tests and the four same-task store cases. The four later-task cases pass.
- **The reversal:** `fixture-adapter.ts` replaced by `9c4fef5`'s (`git show 9c4fef5…:apps/mobile/src/notifications/fixture-adapter.ts`), with the session taken before the await and used after it. `node --test src/notifications/fixture-adapter.test.ts src/notifications/store.test.ts`: exit 1, `ℹ tests 29`, `ℹ pass 23`, `ℹ fail 6`:
  - both adapter tests: `AssertionError [ERR_ASSERTION]: Expected values to be strictly deep-equal: … actual: [ undefined, 'stale_version', undefined ], expected: [ 'unauthenticated', 'unauthenticated', 'unauthenticated' ]` (the register or rotate and the read succeeded);
  - the four same-task store cases: logout, `granted` and `undetermined_allow`: `AssertionError [ERR_ASSERTION]: session_started,refused,session_ended,register … actual: [ { accountId: '11111111-…', deviceId: '6f12d000-…-000000000001', state: 'active', version: 1, sessionId: 'fixture-session-1', endedBy: null } ], expected: []`; account change, both presets: the same, with the events `session_started,refused,session_ended,session_started,register`. (The first `refused` is the initial read's `not_found`.)

  The fixed file was restored, and its SHA-256 matched the saved copy (`68f151050a0d582b…`).

### Item 2 — F-2: the server's import test records relative imports exactly

- **File:** `services/api/tests/test_notifications.py` (`FixtureScopeTests`).
- **The change:** a helper, `_imported_modules`, reads each `ImportFrom` by its level, module and imported names. `from . import x` is the sibling `.x`; `from .m import y` is `.m`. The domain-module test now asserts that the relative imports are exactly `{".chat", ".provider_fixtures"}`, and that the whole set is the standard-library names plus those two (`"."` in the expected set became `".chat"`). A new test, "the import reading names each relative module", pins the helper on probe sources: `from . import chat_provider_stream`, two names in one statement, `from .. import x`, a module import and absolute imports. `FixtureScopeTests` has 5 tests now.
- **The record's claim** (Outcome 2: `notifications.py` "imports only the standard library, `.chat` and `.provider_fixtures`") is now what the test checks.
- **The reversal:** `from . import chat_provider_stream` added to `notifications.py` after `from . import chat`. `manage.py test tests.test_notifications.FixtureScopeTests --verbosity 2` (with `PYTHONDONTWRITEBYTECODE=1`): exit 1, `test_the_domain_module_imports_only_the_standard_library_and_its_two_neighbours … FAIL`, `AssertionError: Items in the first set but not the second: '.chat_provider_stream'`, `FAILED (failures=1)`. The other four passed.
- **For comparison (informational):** `9c4fef5`'s test file, copied in temporarily, ran with the same probe in place: `Ran 4 tests` … `OK`, as the review found. The copy was removed, `notifications.py` restored (`git diff --quiet glow_domain` clean), and the ignored `__pycache__` directories cleared.

### Item 3 — F-3: the mobile import scan covers bare side-effect imports

- **File:** `apps/mobile/src/notifications/fixture-scope.test.ts`.
- **The change:** the scan's pattern, now a named `SPECIFIER`, adds the bare form `import '…'` to `from '…'`, `import('…')` and `require('…')`. A new test, "the import scan reads every import form, the bare side-effect form among them", pins it on a probe source (`import 'expo-device';`, a default import, `import type`, `require`, a dynamic import and `import"e"`).
- **The reversal:** `import 'expo-device';` added as `permission.ts`'s first line. `node --test src/notifications/fixture-scope.test.ts`: exit 1, `ℹ tests 3`, `ℹ pass 2`, `ℹ fail 1`: `✖ the module imports only React, React Native, Expo Router and the app's own code` with `AssertionError [ERR_ASSERTION]: …/apps/mobile/src/notifications/permission.ts imports expo-device`.
- **For comparison (informational):** `9c4fef5`'s scan, copied in temporarily as another test file, ran with the same probe in place: `ℹ tests 2`, `ℹ pass 2`, `ℹ fail 0`. The copy was removed and `permission.ts` restored.

### The non-test line count

`git diff --numstat 3a2b930… e807ce8 -- . ':(exclude)*.test.ts' ':(exclude)services/api/tests/*'` lists one file: `fixture-adapter.ts`, 6 added and 5 deleted, so **11 non-test lines**. That is 60 or fewer, so a delta review applies (the brief's "Review"). The tests: `fixture-adapter.test.ts` +30, `store.test.ts` +31, `fixture-scope.test.ts` +9 −4, `test_notifications.py` +36 −7.

### Commands and results

| Command (clean environment) | Result |
|---|---|
| `python3.12 -m venv .venv`; `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock` (services/api) | exit 0 (pip's own upgrade notice only) |
| `GLOW_ENV=test .venv/bin/python manage.py check` | `System check identified no issues (0 silenced).` |
| `GLOW_ENV=test .venv/bin/python manage.py test tests --verbosity 2` | `Ran 422 tests` … `OK` (421 before; 1 new) |
| `.venv/bin/ruff check .` | `All checks passed!` |
| `.venv/bin/ruff format --check .` | `81 files already formatted` |
| `.venv/bin/mypy` | `Success: no issues found in 43 source files` |
| `npm ci --ignore-scripts` (apps/mobile) | exit 0 |
| `npm run check` | `tsc --noEmit` and `eslint .` clean; `ℹ tests 691`, `ℹ pass 691`, `ℹ fail 0` (680 before; 11 new) |
| Baselines at `3a2b930`, before any change: the three owned mobile test files; `FixtureScopeTests` | `ℹ tests 21`, `ℹ pass 21`; `Ran 4 tests` … `OK` |
| The three reversals | each failed its test as recorded above; every file restored |
| `git push -u origin claude/peaceful-feynman-ozlu2l` (code) | new branch at `e807ce8`; nothing more pushed until run 42549675849 finished |

### The run of record

**Push run 42549675849** (Foundation, run 891, attempt 1) on `e807ce8719ca0081942081eb7b64db9c28af0bc9`, the code head; `completed`, conclusion `success`, 02:12:58 to 02:20:50 UTC on 9 November 2026. Read with the GitHub tools: the run, the job list with each job's steps, and the gate's, API's and Mobile's logs (the Mobile log downloaded in full to the session's scratch directory, outside the checkout, and searched there).

| Job | Result | Detail |
|---|---|---|
| Change scope | success | the step "Classify the complete change using trusted base policy" passed |
| API checks | success | `System check identified no issues (0 silenced).` and **`Ran 422 tests in 10.544s` … `OK`**; `All checks passed!`, `81 files already formatted`, `Success: no issues found in 43 source files`; the contracts suite `Ran 39 tests … OK` |
| Mobile checks | success | `@glow/contracts` `ℹ tests 586`, `ℹ pass 586`, `ℹ fail 0`; `@glow/mobile` typecheck and lint, then **`ℹ tests 691`, `ℹ pass 691`, `ℹ fail 0`**, the 11 new tests among them by name; `Dependencies are up to date`; `export:development` (`Android Bundled … (1339 modules)`, `iOS Bundled … (1372 modules)`, `Exported: .work/native-export`); Chrome for Testing 151.0.7922.34 (`playwright chromium v1234`) installed; the rendered suite **`104 passed (5.3m)`**, 104 `✓` lines and no failed, flaky or skipped count; the layout artifact uploaded (2 files, `p04-empty-form-layout`, artifact 13644938615). Duration: 02:13:09 to 02:20:44 UTC, 7 min 35 s |
| API mobile smoke | success | `node scripts/smoke.mjs && node --test scripts/smoke.test.mjs` passed |
| API artifact checks | success | the pinned image built, inspected and smoked |
| Stream proof checks | success | its unit tests, `ruff`/`mypy`, the client syntax check and `checks/run_plan.py` |
| Database proof checks | success | the disposable PostgreSQL proof, both subjects and the delivery phase |
| Foundation gate | success | **`Application checks passed`** |

**Toolchain retry:** none fired. In the API, smoke, Stream proof and Database jobs, the first `actions/setup-python` attempt succeeded, and both "Wait 60 s before the one retry of the Python install (DM-41)" and "Retry the Python install once (DM-41)" were `skipped`. The run was not re-run.

### What could not run, and limits

- **The rendered suite** was not run locally: this correction changes no screen, and `playwright install` is forbidden here. CI's Mobile job runs it on the pinned browser.
- **`check:expo`, `export:development` and `smoke.py`** were not run locally: the prompt's local checks do not list them, and the change touches no dependency, configuration or served code. CI runs the export and the smoke.
- **The adapter is still a presentation substitute** for F12; the Python domain stays authoritative. The fix proves the adapter refuses an ended session's request; it proves nothing about the server's HTTP route (SV4).
- **Deviations from the brief:** none in scope. Beyond the brief's tests: a second adapter test (a registration held by another current session, so that each stale method would otherwise succeed); the later-task store cases written out explicitly in the loop; and a self-test for each of the two import scans.
- **Nothing met the stop rule.** No path outside the owned paths changed; no dependency, lock, contract or model changed; the adapter's only change in behaviour is refusing an ended session's request.

## Manager verification of correction C1 (9 November 2026, App Manager 10)

- **The branch:** `claude/peaceful-feynman-ozlu2l`, with the code head `e807ce8` and the records head `9686efe`, starts at the prompt's commit `3a2b930`.
  - `git diff --name-only 3a2b930 9686efe` lists six paths, all owned: `fixture-adapter.ts`, its test, `store.test.ts`, `fixture-scope.test.ts`, `test_notifications.py`, and the record, which is the records commit's only path.
  - The one non-test change is `fixture-adapter.ts`, `+6 −5`: in `settings`, `device` and `notifications`, `capture(session)` moved to after `await this.gate()`, plus three comment lines (corrected after C1's delta review, N-3; this line first said two). Nothing else in the adapter changed, and no other runtime file did. That is within 60 non-test lines, so a delta review follows (step 6).
- **The run of record,** push run 42549675849 on `e807ce8`, read with the GitHub tools:
  - all eight jobs `success`;
  - the gate's log ends `Application checks passed`;
  - every DM-41 wait and retry step `skipped`.
- **Three reversals re-run** in a scratch copy of `e807ce8` (`git archive`, outside the checkout), with clean process environments, each file restored and checked:
  - **F-1:** `9c4fef5`'s `fixture-adapter.ts` put back. `fixture-adapter.test.ts` and `store.test.ts` go from `ℹ tests 29 / pass 29` to `ℹ pass 23 / fail 6`. The six are both new adapter tests and the four same-task store cases (logout and account change, with `granted` and `undetermined_allow`).
  - **F-2:** `from . import chat_provider_stream` added to `notifications.py`. `FixtureScopeTests` goes from `Ran 5 tests … OK` to `FAIL: test_the_domain_module_imports_only_the_standard_library_and_its_two_neighbours`, `AssertionError: Items in the first set but not the second`.
  - **F-3:** `import 'expo-device';` added to `permission.ts`. `fixture-scope.test.ts` goes from `pass 3 / fail 0` to `pass 2 / fail 1`, `… permission.ts imports expo-device`.
- **PR41 before C1:** on `3a2b930` (the commit that holds C1's prompt), Codex's code review completed at 01:52:29 UTC with no new finding. Its PR run 42547603140 passed every job. Its push run 42547597493 read the commit as records only and passed its gate.
- **Integrated:** the manager branch fast-forwarded to `9686efe`. Codex's F-C1 thread is answered and resolved now that its fix is on PR41.

## Delta review of correction C1 (9 November 2026)

- **The review:** prompt revision 1 at `1a2a2c7`, of code head `e807ce8`, run in `Glow App - No Stream`; Nathan's pick: not recorded.
  - The environment check, the start gate (one merge base, `7feba0d`) and the classification with `main`'s trusted policy (`"full": true`, `behavior-or-empty`) passed.
  - **Verdict: approve with nits.** F-1, F-2 and F-3 are fixed, and each test fails under its reversal. None of the three nits is in a correction class.
- **Its six focus points hold:**
  - F-1's fix changes nothing else, and the adapter's other differences from the domain predate C1. Those differences: every session refusal maps to `unauthenticated`, and expiry and epoch are not checked;
  - the F-1 tests are not vacuous;
  - F-2's test is true to the record's claim;
  - F-3's scan catches the bare form;
  - no other path or assertion changed;
  - the records hold, except N-3.
- **One window it reasoned through and did not run:** in `setKind`, the store does not re-check its epoch between `register` returning and `save` being sent. A logout in that window sends the owner's revoke first, and the adapter refuses the stale save. The manager read `store.ts:143-166` and agrees with the reasoning; it did not run it either.
- **Its re-runs,** in scratch copies of `e807ce8`, each as recorded:
  - **F-1:** `ℹ tests 29, pass 23, fail 6`;
  - **F-2:** `failures=1`. With `9c4fef5`'s test file in its place, the result is `Ran 4 tests … OK`;
  - **F-3:** `pass 2, fail 1`.

  Its own checks:
  - API `Found 422 test(s)`, `OK`;
  - ruff and mypy clean;
  - mobile `npm run check` with `tests 691, pass 691`.
- **The runs it read:** run 42549675849, as recorded, and PR41's run 42551087590 on `1a2a2c7`, all eight jobs `success`. For run 42551087590 it read job and step conclusions only, not logs.
- **Not run:** the rendered suite, `check:expo`, the export and `smoke.py`. `playwright install` is forbidden in the cloud session, and C1 touches no screen.
- **The nits and their dispositions** (step 6, rule (b)). The manager checked each against the code at `e807ce8`:

| # | What | Disposition |
|---|---|---|
| N-1 | `fixture-scope.test.ts:17`'s `SPECIFIER` accepts `'` and `"` but not backticks, which `src/chat/no-provider.test.ts:24` accepts. So ``import(`expo-device`)`` and ``require(`expo-device`)`` pass the scan, and the self-test titled "reads every import form" reads less than that. It predates C1 and is in F-3's guard class | **Carried to P09** (the carried-items file): P09.2 rewrites this guard when it adds `expo-notifications` behind the seam |
| N-2 | `FixtureScopeTests` reads import statements only (`ast.Import`, `ast.ImportFrom`), so a call `__import__("glow_domain.chat_provider_stream")` in `notifications.py` passes all five tests. `import importlib` is caught by the exact set | **A claim limit, recorded here:** the test shows that `notifications.py`'s import statements are only the standard library, `.chat` and `.provider_fixtures`; it does not see a call to `__import__` |
| N-3 | The manager's "Manager verification of correction C1" said the adapter's change was the moved `capture` "plus two comment lines"; there are three, the two `//` lines at `fixture-adapter.ts:100-101` and the `/** … */` line at `:120`. The `+6 −5` count was right | **Corrected** in that section, with a note; logged as AM10-03 in the manager mistakes log |

- **One more record correction,** made here and not in the session's section: "Correction C1", item 2, places the claim "imports only the standard library, `.chat` and `.provider_fixtures`" in Outcome 2. It is in Outcome 1's table (the transport row).
- **The result:** C1's delta review approves the final code head `e807ce8`. Step 7 follows: the pre-merge checklist, the PR run and Codex on the final head, then the merge.

## The merge receipt (9 November 2026, App Manager 10)

- **PR41 merged** at 03:03:14 UTC as the merge commit `da92f1fb71da6c93fae8a747f62c718800a12ae9`.
  - Its parents are `8031361` (`main`) and `8d2de72` (PR41's head).
  - It merged by the expected-head guard (`expectedHeadSha` `8d2de724091f2a7127d207fbc557ea1ced57f690`), after the pre-merge checklist in PR41's description was filled.
  - `main`'s tree equals `8d2de72`'s. The final head's non-Markdown paths are byte-identical to C1's code head `e807ce8`.
- **Its checks:**
  - the trusted policy at `8031361` read full scope (`behavior-or-empty`), with one merge base, `7feba0d`;
  - PR run 42553342404 on `8d2de72` passed all eight jobs. The gate printed `Application checks passed`, rendered `104 passed (5.3m)`, and every DM-41 wait and retry step was skipped;
  - push run 42553336023 on the same head passed;
  - Codex's code review of `8d2de72` completed at 02:55:22 UTC with no findings. PR41's one Codex thread, F-C1, was answered and resolved;
  - the exact-head review, correction C1 and C1's delta review are recorded above;
  - PR41 carries no governing Markdown.
- **The cleanup run** 42554232876 passed and deleted the two P06.3 session branches, each "merged into main": `claude/gallant-lovelace-vwgu69` (`7775bba`, the implementation) and `claude/peaceful-feynman-ozlu2l` (`9686efe`, C1). It kept `main`, the manager branch and `claude/dev-manager` by the keep-list. The two review sessions pushed no branch.
- **`git ls-remote`** after it (03:03 UTC): `main` at `da92f1f`, the manager branch at `8d2de72`, `claude/dev-manager` at `65618c1`, and nothing else. PR41's activity subscription is ended.
- **`main`'s push run** 42554232777 on `da92f1f`: in progress when this receipt was committed, with five of its jobs passed (Change scope, API checks, API artifact checks, Stream proof checks, API mobile smoke) and the database proof and Mobile checks running. Its result follows in the next records commit.
- **Pruned:** P06.3's five prompts and consultations in `docs/ephemeral/`: DM-44's consultation, the implementation prompt, the exact-head review prompt, C1's prompt and C1's delta review prompt.
  - Their unique content lives in the brief, this record and DM-44's report.
  - The eight links to them, in the brief, this record and the review log, are pinned at `da92f1f`, where each file exists.
  - Text that names a prompt's path, as this record's checklist lines do, stays true as history.
- **P06.3 is done.** Carried forward, in the carried-items file:
  - to SV4: DM-44 7.2's entry, the optional revoke-when-all-off, and F-4;
  - to P09: F-5 and N-1.

  To the Dev Manager's next consultation: DM-44 1.3's confirmation, and the reasoning for writing C1 without a consultation.
