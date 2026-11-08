# P06.3 — Privacy-safe notifications at fixture scope

- **Work ID:** P06.3 (P06; PF01 P06.3 acceptance; the F12 flow).
- **Status: brief, revision 1, 8 November 2026. Waiting for the Dev Manager's read (DM-44).** No prompt is written before its answer.
- **Owner:** Nathan Amthor, by the order he resumed on 26 October (OD-49): P06.3 after P06.2-F, before the server slices SV1 to SV4. **Manager:** App Manager 10. **Session:** one implementation session, started by Nathan, in `Glow App - No Stream` (no Stream call).
- **Starting point:** `main` at `8031361` (PR40, P06.2-F), with the manager branch's Markdown records after it. The prompt names the exact commit. The app is on Expo SDK 58 (`expo` 58.0.22).
- **Evidence home:** `docs/testing/evidence/<date>-p06-3-notifications.md`, written by the session.
- **The matrix recheck** is done: AP-50, AP-51 and GP-51 were re-read on 8 November and all three are confirmed ([recheck record](../testing/evidence/2026-11-08-p06-3-matrix-recheck.md); DM-37 3.1 and 5.1).

## Why

- **PF01's P06.3 acceptance:** *"notification content comes only from Glow's server path and carries no birth details, compatibility data or message body by default; preferences and device registration follow their contracts at fixture scope; real push transport is deferred to P09/P11 with its credentials."*
- **The F12 flow** (`packages/contracts/production/flows-v1.json`; `production-contracts.md`, F12) asks for:
  - private reads of a member's own settings, with tokens kept secret and omitted from reads;
  - a public projection with only a generic match or message event, and no message body or birth data;
  - staff with no access to tokens.

  Its acceptance: *"Token rotation owner/session bound; logout revokes registration; no duplicate push; denied platform permission is normal."*
- **ADR 0003:**
  - decision 2: Stream member or user data never reaches push content;
  - decision 3: no provider's name, notifications or data reach members, and the principle covers push;
  - its consequences: *"P06.3: notification content comes only from Glow's server path, never from Stream's push."*
- **The store rows** (rechecked 8 November):
  - AP-50: the app is usable with permissions denied;
  - AP-51: no sensitive content in a notification, permission asked in context;
  - GP-51: on Android 13 and later, nothing is sent before the member grants `POST_NOTIFICATIONS`, and the request is made in context.
- **P06.2's lighter start (b′)** polls only in the foreground; *"nothing polls in the background until P06.3's push"* (the P11 plan). P06.3 builds the composer and the device and settings path, not real delivery. So **background delivery stays absent until the native module (P09.2) and the transport (P11) land**. This brief changes nothing about that gap at runtime.

## Outcome

The item is done when each of these holds, **each with a test and the reversal that fails it**, recorded in the evidence record.

1. **The notification composer** (server, `glow_domain`, D2):
   - it takes a match activation or an accepted message as a typed trigger, and composes at most one push per active device of the recipient for that trigger;
   - the push it composes carries only the kind, Glow's fixed wording and a fixed route (D4);
   - the trigger type has no field for a message body, a name, birth data, compatibility data or a provider identifier, and the composer refuses a trigger with any extra field;
   - it composes nothing when:
     - the recipient's setting for that kind is off;
     - the recipient has no active device;
     - either account has blocked the other;
     - the match has ended or contact is revoked;
     - either account is paused, restricted or pending deletion;
   - each refusal is a reason code that carries no personal data;
   - **no duplicate push:** a trigger delivered twice (a retry, a redelivered event) sends nothing the second time, for any device. The ledger's key is the trigger's event id with the device's id;
   - it sends only through a push-transport port, whose only implementation is a fixture that records what it was given and refuses a repeated idempotency key.
2. **Devices and settings** (server, `glow_domain`, F12 at fixture scope, D3):
   - **the transitions:** register (none to active), rotate (active to active), revoke (active to revoked), logout (active to revoked, by the system), settings (active to active), and register again (revoked to active);
   - **owner and session bound:**
     - a device command carries the actor's account and current session, and a command from a session that is no longer current is refused;
     - registering an installation that is active for another account first revokes that account's registration, in the same unit of work (`data-model.md`);
   - **token custody:**
     - the token goes to a token-store port, and only its opaque reference is kept. The only implementation is a fixture;
     - no read, representation, log line, refusal or composer output contains the token's value;
     - a staff projection, if the session adds one, carries no token or token reference;
   - **logout revokes** every active registration of the account's session;
   - **settings default to off** for both kinds (`data-model.md`: "defaults off").
3. **The mobile settings screen** (D5, D7):
   - a new route, `/notifications`, opened from the profile screen. Both kinds start off;
   - turning a kind on is the only thing that asks the platform permission, through a permission seam;
     - if the permission is undetermined, the seam asks once;
     - if granted, the app registers the device through a fixture adapter with a synthetic token and saves the setting;
     - if denied, the app saves the setting, registers no device, and says in Glow's wording that notifications are off in the device's settings and that Glow works without them;
   - nothing asks for the permission at launch, at sign-in or on any other screen;
   - **denied is normal:** with permission denied, every other route and journey works as before. A rendered test walks a journey with the permission denied;
   - **logout and an account change** revoke the device through the adapter and clear the screen's state. A test fails when the revoke or the clear is removed;
   - the screen validates every response against the generated `NotificationSettings` contract, and refuses one that does not match;
   - its copy names no provider, Expo, Apple or Google push service. A copy test over the new copy table fails if a provider term appears.
4. **The route guard:** `/notifications` is added to `SAFE_ROUTES` with the same rule as `/profile`: an active account with a valid session. A test fails if a signed-out or restricted state can open it. Nothing else the guard allows changes (D7).
5. **The record** names, for each item, the test, the edit that makes it fail and the failing output. It also records:
   - the field mismatch between the contract and the models (D9);
   - what waits, and for which owner (D9).

## Design

- **D1 — Fixture scope.** No push provider, no push credential, no network client, no native module. The release block and every runtime guard stay as they are. The configuration profile's `"push": ("expo", "GLOW_PUSH_ACCESS_TOKEN")` stays a planned slot (root `AGENTS.md`: a planned provider slot is not an active secret loader).
- **D2 — Where the composer lives:** `services/api/glow_domain/notifications.py`, pure domain logic, beside the other domain modules. Its fixtures go in `notification_fixtures.py`, as the other domain modules keep theirs.
  - **It does not touch P06.2's proven delivery code** (`glow_chat/delivery.py`, `events.py`, `contact.py`), its outbox or its database proof.
  - **The trigger's contract:**
    - a match notification follows a match activation;
    - a message notification follows the message's acceptance (the delivery receipt that marks the submission `accepted`), never its submission, so a refused or dead-lettered message never notifies.
  - **Wiring the trigger** to the outbox and to persistence waits for its owner (D9).
- **D3 — Devices and settings follow F12 at fixture scope:** in-memory state, the token-store port, and the transitions above.
  - The domain uses the contract's names (`match_notifications`, `message_notifications`, `device_state`, `device_id`, `provider_token`).
  - The persistence models use other names (D9). No contract, model or migration changes.
- **D4 — Kinds, wording and payload:**
  - **two kinds only:** a new match and a new message. **No promotional or marketing push** (AP-51; ARG 4.5.4's second sentence);
  - **the wording**, one fixed sentence per kind with the title `Glow`: *"You have a new match."* and *"You have a new message."* No name, photo, message text, count, birth data, compatibility data or provider identifier appears.
    - Nathan may change the wording at any time. A change is a copy-table edit and its test;
    - "by default" in PF01's acceptance leaves room for a later opt-in preview. P06.3 builds none: a preview would be a product decision for Nathan;
  - **the payload's data:** the kind and a fixed route (`/matches` or `/conversations`), with no identifier.
    - This follows the app's existing rule: *"Only fixed public screen identifiers enter routing. Never propagate query parameters or private values"* (`src/onboarding/routes.ts`);
    - the app then opens the list behind its own session check.
- **D5 — The permission request:**
  - only from the member's own action of turning a kind on, which is the in-context moment AP-51's Apple page and GP-51's Android page describe;
  - never at launch, and no provisional authorization;
  - the seam has three answers (undetermined, granted, denied). Its only implementation is a fixture whose answer a development control sets, like chat's fixture scenarios, labelled synthetic and shown only in the development preview.
- **D6 — No `expo-notifications` now.** M06's assessment expected P06.3 to add push as a native dependency. This brief recommends against adding it in P06.3. Expo's documentation (read 8 November 2026, the SDK 58 reference) gives four reasons:
  - the module's platforms are *"Android, iOS"*, with no web. This repository's only runtime is the web export and the rendered harness, so nothing in CI could exercise it;
  - remote push needs a development build (*"A development build is required to use push notifications"*; Expo Go has no push from SDK 53). The release block forbids an EAS project, and no native build has been made;
  - `getExpoPushTokenAsync` *"rejects with the `ERR_NOTIFICATIONS_NO_EXPERIENCE_ID` error"* without a project ID, which is the Expo Services project's UUID;
  - Android needs Firebase Cloud Messaging credentials (`google-services.json`), and iOS needs a paid Apple Developer account and an APNs key. These are credentials, which P09 and P11 own.

  **So:** the seam (D5) and the fixture token source stand in, and the native module comes with the native builds (P09.2), under `apps/mobile/AGENTS.md`'s "Dependency changes", step 5 included, and Nathan's release authorization. M06's other reason, choosing the module against SDK 58 rather than 57, still holds when it is added.
- **D7 — Mobile shape:**
  - a new `src/notifications/` module (copy table, permission seam, fixture adapter, store, screen), following chat's module pattern;
  - a new route file, `src/app/notifications.tsx`, and one link on the profile screen;
  - the store follows the onboarding account, as chat's store does for its list clear on an account change (P06.2-F item 2), so `src/onboarding/store.ts` does not change;
  - **the guard change:** `/notifications` is one new entry in `SAFE_ROUTES` and `canAccessRoute`, with `/profile`'s rule. It is the only change to what a guard allows, and this brief's Dev Manager read approves or refuses it. Any other change to a guard's allowance stops the session.
- **D8 — Not Stream's push, and not OD-45's token:**
  - P06.3 configures nothing at Stream and sends nothing through it. Glow's server path is the only notification path, and under OD-45 a Stream feature takes effect only by a recorded decision, with the drift check (the P11 plan) comparing Stream's whole configuration;
  - PF01's *"notification preferences (OD-45: no client token lifecycle)"* refers to the Stream credential the app does not hold. The device's push token is F12's `DeviceIntent.provider_token`, a different thing, which the app registers through Glow's API and never shows.
- **D9 — The field mismatch, and what waits:**
  - **The mismatch** (the session records it and changes neither side):
    - the contract's `NotificationSettings` has `match_notifications`, `message_notifications` and `device_state`, while the model has `push_enabled`, `match_updates` and `message_updates`;
    - the contract's `DeviceIntent` has `device_id` and no platform, while `DeviceRegistration` has `installation_id`, `platform` and `token_secret_ref`;
    - the mapping, and whether `push_enabled` or a platform belongs in the contract, are decided by the slice that serves F12.
  - **What waits, and for whom:**
    - F12's HTTP surface, its ORM adapters and the trigger's wiring to the outbox: **SV4** (chat's HTTP surface), recommended, since F12 is the communication flow and the triggers are chat's events. DM-44 is asked to confirm or name another owner;
    - the native module, permission prompts on devices, credentials and the Expo project: **P09.2**, with Nathan's release authorization;
    - the real transport, live delivery, rotation and retries against the provider, and duplicate paths reconciled: **P11B** (PV05).
- **D10 — Option (c)'s trigger does not apply.** P06.3 changes neither `src/chat/screen.tsx` nor `src/chat/rows.ts` (the carried-items file), and nothing under `src/chat/` at all ("Exclusions"). A change there would stop the session.
- **D11 — Every test comes with its reversal,** in the style of the P06.2 and P06.2-F records.
- **D12 — Checks:**
  - **API,** from `services/api`, in a clean process environment with the virtual environment made with `python3.12` (root `CLAUDE.md`): `manage.py check`, `manage.py test tests`, `smoke.py`, `ruff check`, `ruff format --check` and `mypy`, as its README lists, each with `GLOW_ENV=test` where the README sets it;
  - **mobile,** from `apps/mobile`: `npm run check`, `EXPO_OFFLINE=1 npm run check:expo` and `EXPO_OFFLINE=1 npm run export:development`;
  - **the run of record** is CI's, for the rendered suite's pinned Chromium.

## Owned paths (the session)

- **new:** `services/api/glow_domain/notifications.py`, `services/api/glow_domain/notification_fixtures.py`, `services/api/tests/test_notifications.py`;
- **new:** `apps/mobile/src/notifications/**`, `apps/mobile/src/app/notifications.tsx`, and a new spec under `apps/mobile/rendered/`;
- `apps/mobile/src/onboarding/routes.ts`, for D7's one route only, with its test file;
- `apps/mobile/src/app/profile.tsx`, for the one link only;
- `apps/mobile/src/app/development.tsx`, for D5's fixture control only, if the session puts it there;
- an existing rendered spec, only if the profile link moves an assertion it makes. No assertion is removed or loosened;
- **new:** `docs/testing/evidence/<date>-p06-3-notifications.md`.

## Manager-owned

- This brief and its "Sessions"; the prompt; the Work Register's P06.3 row; Notion; the handoff; the PR; the matrix rows' dates.

## Exclusions

- Nothing under `apps/mobile/src/chat/` (D10), `services/api/glow_chat/`, `services/api/glow_persistence/` (models, migrations, the static check), `services/api/glow_api/` (routes, settings, configuration profiles), `packages/` (contracts), `proofs/`, `scripts/` or `.github/`.
- No change to `package.json`, `package-lock.json`, `.npmrc`, `dependency-inventory.json` (mobile or API), `requirements*.in` or `requirements*.lock`; to `apps/mobile/app.config.ts`, `src/app/_layout.tsx`, `eslint.config.mjs` or `src/config/`; or to any `AGENTS.md`, `CLAUDE.md` or other governing Markdown.
- No `eas`, `playwright install` or `migrate`. No provider call, and no connection to a database, HDE or Railway.

## Acceptance checks

- Items 1 to 5 hold, each with its test and its reversal recorded.
- The local checks pass (D12). The run of record passes all eight jobs, with `Application checks passed` and the rendered suite, the Mobile job within its timeout.
- `git diff --name-only <start> <head>` lists only owned paths.
- The trusted classifier reads the change as full scope.

## Review plan

- **Full scope:** normal CI and exact-head review evidence (`AGENTS.md`).
- **The manager verifies the report** against the pushed branch:
  - the diff within the owned paths;
  - each reversal re-run where it is cheap;
  - a search of the diff for any token value, provider term or body field in a payload;
  - the run of record's logs.
- **Then** the PR, Codex's review of its head, and an exact-head code review of the code head with a written threat model of the device and token path (OD-41; DM-31 item 3). Its prompt waits for Codex on the code head and on the commit that holds the prompt (manager workflow, step 6).
- **Dev Manager (DM-44):** the charter asks for this brief's read, for four reasons:
  - it places a new domain component (D2);
  - it sets a security boundary for push tokens and notification content (D3, D4);
  - it decides against a dependency an earlier assessment expected (D6);
  - it adds one route to the route guard (D7).

  It also asks the Dev Manager to name F12's HTTP owner (D9).

## Sessions

- **Brief, revision 1** (8 November 2026): written after the matrix recheck; sent to the Dev Manager as DM-44 ([consultation](../ephemeral/2026-11-08-dm-44-p06-3-brief.md)). Next: DM-44's answer.
