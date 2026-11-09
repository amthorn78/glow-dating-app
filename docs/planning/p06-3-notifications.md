# P06.3 — Privacy-safe notifications at fixture scope

- **Work ID:** P06.3 (P06; PF01 P06.3 acceptance; the F12 flow).
- **Status: brief, revision 2, 8 November 2026; implemented (code head `9c4fef5`); the exact-head review is next.** Revision 1 went to the Dev Manager as DM-44. [DM-44](../continuity/dev-manager/reviews/2026-11-08-dm-44-p06-3-brief.md) (answered at `65618c1`, a read of `8bf9d8d`) approved it with conditions. Revision 2 applies them as written: 1.1 and 1.2 in Outcome 2; 2.1, 2.2 and 3.3 in Outcome 1; 3.1 and 3.2 in Outcome 2; 4.1 to 4.3 in Outcome 3; 5.1 in D6; 6.1 in D7; 6.2 in "Owned paths" and "Exclusions"; 6.3 in Outcome 4; 7.1 in D9; and 9.1 in the review plan. So it needs no read before the prompt, and the Dev Manager's next consultation confirms the words as applied (DM-44 1.3).
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
   - it takes a match activation or an accepted message as a typed trigger that names its recipient, and composes at most one push per active device of the recipient for that trigger. A message notifies the other member of the match, never its sender; a match notifies the member whose earlier like the reciprocal like matched, never the member whose like completed it;
   - the push it composes carries only the kind, Glow's fixed wording and a fixed route (D4);
   - the trigger type has no field for a message body, a name, birth data, compatibility data or a provider identifier, and the composer refuses a trigger with any extra field;
   - it composes nothing when the recipient's setting for that kind is off, when the recipient has no active device, or when a check that refuses a send refuses it (the read rule in `glow_domain/chat_reads.py`, "Whatever refuses a send refuses a read"): the match not active, or a block either way; either account not active (suspended, pending deletion or deleted); either profile paused or restricted; either onboarding consent not accepted. It reads these facts on each delivery, never from the trigger, so a message accepted after a block or an unmatch notifies no one;
   - each refusal is a reason code that carries no personal data;
   - **no duplicate push:** the first delivery of a trigger fixes its devices: the recipient's active devices then. A later delivery of the same trigger (a retry, a redelivered event) sends only to a device of that set whose send the transport has not accepted and that is still active, so a device registered after the first delivery gets nothing for that trigger. The ledger's key is the trigger's event id with the installation's `device_id`, so a registration revoked and made again keeps its key. The ledger records a send only when the transport accepts it, and the transport's idempotency key is the ledger's key: a send the transport accepted but the ledger did not record is refused as a repeat on the next delivery, and the ledger then records it. Exactly-once delivery by a real provider is P11B's (PV05);
   - it sends only through a push-transport port, whose only implementation is a fixture that records what it was given and refuses a repeated idempotency key.
2. **Devices and settings** (server, `glow_domain`, F12 at fixture scope, D3):
   - **the transitions, per installation:** each installation's registration is `none`, `active` or `revoked`; the settings are the account's (`data-model.md`: one preference row per owner, defaults off).
     - A `register` intent for an installation in `none` or `revoked` is F12's `register`. For an installation already `active` for the same account it is F12's `rotate`, since the contract's `DeviceIntent` has no `rotate` action, and the new token's reference replaces the old one.
     - `revoke` (the owner) and `logout` (the system) move `active` to `revoked`.
     - `settings` needs the requesting installation's registration to be `active`. Otherwise a settings intent is refused, since F12 forbids every unlisted transition.
     - Each command follows `CommandMeta` and `data-model.md`'s idempotency rule: a stale `expected_version` is refused, the same key with other content is a conflict, and a replay changes nothing.
     - Only the owner reads the settings (F12's read roles), from a current session. A read from an installation with no registration returns an explicit absence: the contract's `device_state` has only `active` and `revoked`.
   - **owner and session bound:**
     - a device command carries the actor's account and current session, and a command from a session that is no longer current is refused;
     - each registration records the session that last registered or rotated it. A registration whose session is no longer current (revoked, expired, or from an older session epoch) is not active for the composer;
     - registering an installation that is active for another account first revokes that account's registration, in the same unit of work (`data-model.md`);
   - **token custody:**
     - the token goes to a token-store port before its opaque reference is saved, and only the reference is kept (`data-model.md`). If the store refuses, nothing is saved. The only implementation is a fixture;
     - when a registration ends (revoke, logout, or its installation's transfer to another account) or its token is replaced (rotate), the old token is discarded from the store through the port. The registration's state changes even if the discard fails; a failed discard is kept for retry, and nothing resolves a revoked registration's reference;
     - the push request the composer hands the transport names the device by its reference, never by its token; only a transport adapter resolves it (P11B);
     - no read, representation, log line, refusal, exception message, idempotency receipt or composer output contains the token's value, and no read, log line or refusal contains its reference;
     - a staff projection, if the session adds one, carries no token or token reference;
   - **the custody test** plants a distinctive synthetic token and captures every log record at `DEBUG` from the root logger while it registers, rotates, revokes, logs out, transfers, replays and is refused. It fails if the token appears in any record's message or arguments, in any read, `repr()` or `str()` of the domain's objects and refusals, in any exception's text, or in what the transport fixture recorded; and if the reference appears in any record, read or refusal. Its reversal logs the token in one path;
   - **logout revokes** the registrations the ending session made (F12's `logout`, by the system); the account's registrations from its other sessions stay active;
   - **settings default to off** for both kinds (`data-model.md`: "defaults off").
3. **The mobile settings screen** (D5, D7):
   - a new route, `/notifications`, opened from the profile screen. Both kinds start off;
   - turning a kind on is the only thing that asks the platform permission, through a permission seam:
     - if the permission is undetermined, the seam asks once;
     - if granted, the app registers this installation through a fixture adapter with a synthetic token, unless its registration is already active (F12's `register`), then saves the settings with only that kind changed (F12's `settings`, which needs an active registration);
     - if denied, the app saves nothing and registers no device: the kind stays off, and the screen says in Glow's wording that notifications are off in the device's settings and that Glow works without them. Turning the kind on again consults the seam again; it asks the platform only while the permission is undetermined, and nothing is saved until it answers granted;
   - turning a kind off saves the settings with only that kind changed;
   - the screen shows both kinds off for this device unless this installation's registration is active. The fixture adapter returns an explicit absence for an installation with no registration (the contract's `device_state` has no `none`), and the screen validates every `NotificationSettings` it receives;
   - every intent passes `parseAppIntent` before the adapter takes it, as chat's client does;
   - before any request, the screen says what each kind sends, in Glow's wording: one fixed sentence per kind, with no name, photo or message text (D4). This is the context AP-51's Apple page and GP-51's Android page ask for;
   - nothing asks for the permission at launch, at sign-in or on any other screen;
   - **denied is normal:** with permission denied, every other route and journey works as before. A rendered test walks a journey with the permission denied;
   - **logout and an account change** revoke this installation's registration through the adapter while the session is still current, then clear the screen's state; the server's `logout` event covers a revoke that did not reach it. A test fails when the revoke, its order or the clear is removed;
   - the screen validates every response against the generated `NotificationSettings` contract, and refuses one that does not match;
   - its copy names no provider, Expo, Apple or Google push service. A copy test over the new copy table fails if a provider term appears.
4. **The route guard:** `/notifications` is added to `SAFE_ROUTES` and `canAccessRoute` with the same rule as `/profile` (an active account with a valid session), and to `_layout.tsx` in its own `Stack.Protected` (D7). A rendered test opens `/notifications` signed out, then again with a query and a hash, as the profile routes' test does ("new private profile routes deny signed-out entry and discard private URL data"), and in the suspended and deletion-pending fixtures; the settings screen never renders. Its reversal removes the layout's line, and the test then fails. A unit test covers `canAccessRoute('/notifications', …)` for each state. Nothing else the guard allows changes (D7).
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
  - Android needs a Firebase project: its `google-services.json` in the app, which Expo's FCM page describes as public-facing identifiers, and an FCM V1 service-account key, a private key, for sending. iOS needs a paid Apple Developer account and an APNs key. The keys are credentials, which P09 and P11 own.

  **So:** the seam (D5) and the fixture token source stand in, and the native module comes with the native builds (P09.2), under `apps/mobile/AGENTS.md`'s "Dependency changes", step 5 included, and Nathan's release authorization. M06's other reason, choosing the module against SDK 58 rather than 57, still holds when it is added.
- **D7 — Mobile shape:**
  - a new `src/notifications/` module (copy table, permission seam, fixture adapter, store, screen), following chat's module pattern;
  - a new route file, `src/app/notifications.tsx`, and one link on the profile screen;
  - the store follows the onboarding account, as chat's store does for its list clear on an account change (P06.2-F item 2), so `src/onboarding/store.ts` does not change;
  - **the guard change:** `/notifications` is one new entry in `SAFE_ROUTES` and `canAccessRoute`, with `/profile`'s rule, and one new line in `src/app/_layout.tsx`: `<Stack.Protected guard={canAccessRoute('/notifications', state)}><Stack.Screen name="notifications" /></Stack.Protected>`. The layout's `Stack.Protected` is what guards a screen: Expo Router 58 adds a route file the layout does not declare as an unguarded screen. Being in `SAFE_ROUTES` also makes `/notifications` a destination `sanitizeDestination` keeps; `canAccessRoute` still decides access. These are the only changes to what a guard allows, and DM-44 approves them. Any other change to a guard's allowance, or any other change to `_layout.tsx`, stops the session.
- **D8 — Not Stream's push, and not OD-45's token:**
  - P06.3 configures nothing at Stream and sends nothing through it. Glow's server path is the only notification path, and under OD-45 a Stream feature takes effect only by a recorded decision, with the drift check (the P11 plan) comparing Stream's whole configuration;
  - PF01's *"notification preferences (OD-45: no client token lifecycle)"* refers to the Stream credential the app does not hold. The device's push token is F12's `DeviceIntent.provider_token`, a different thing, which the app registers through Glow's API and never shows.
- **D9 — The field mismatch, and what waits:**
  - **The mismatch** (the session records it and changes neither side):
    - the contract's `NotificationSettings` has `match_notifications`, `message_notifications` and `device_state`, while the model has `push_enabled`, `match_updates` and `message_updates`;
    - the contract's `DeviceIntent` has `device_id` and no platform, while `DeviceRegistration` has `installation_id`, `platform` and `token_secret_ref`;
    - the contract's `NotificationSettings` has one `device_state`, with no value for an installation that never registered, while an account may hold several registrations: at fixture scope `device_state` describes the requesting installation's registration and settings are the account's (Outcome 2); whether settings belong to the account or the device, and how a read names its installation, are decided by the slice that serves F12;
    - the contract's `DeviceIntent` has no `rotate` action: at fixture scope a `register` for an installation already active for the same account is F12's `rotate` (Outcome 2);
    - `DeviceRegistration` records no session, while F12 binds a registration to the session that made it: the domain records it at fixture scope (Outcome 2), and the serving slice decides how the model holds it;
    - the mapping, and whether `push_enabled` or a platform belongs in the contract, are decided by the slice that serves F12.
  - **What waits, and for whom:**
    - F12's HTTP surface, its ORM adapters and the triggers' wiring: **SV4** (DM-44 item 7). Two facts bound the wiring: a message's acceptance (`glow_chat/delivery.py`) writes no outbox event today, and `match_activated` is a delivered chat event that the chat worker settles when it creates the channel, so the notification triggers need events of their own, or a change to P06.2's proven delivery code under its database proof. `session_revoked` and `session_expired` are logical events with no consumer yet, which the system's `logout` event can follow;
    - the native module, permission prompts on devices, credentials and the Expo project: **P09.2**, with Nathan's release authorization. With it come the seam's real implementation, mapping the platform's answers, including whether it may ask again; Android's notification channel (Expo's reference: "A channel is needed for the permissions prompt to appear"); and a tapped notification's route, which goes through `sanitizeDestination` and the guard like any other destination;
    - the real transport, live delivery, rotation and retries against the provider, and duplicate paths reconciled: **P11B** (PV05). With it come a push's lifetime (TTL), whether repeated pushes of one kind collapse on the device, and how many pushes a burst of messages makes.
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
- `apps/mobile/src/app/_layout.tsx`, for D7's one `Stack.Protected` line only;
- `apps/mobile/src/app/development.tsx`, for D5's fixture control only, if the session puts it there;
- an existing rendered spec, only if the profile link moves an assertion it makes. No assertion is removed or loosened;
- **new:** `docs/testing/evidence/<date>-p06-3-notifications.md`.

## Manager-owned

- This brief and its "Sessions"; the prompt; the Work Register's P06.3 row; Notion; the handoff; the PR; the matrix rows' dates.

## Exclusions

- Nothing under `apps/mobile/src/chat/` (D10), `services/api/glow_chat/`, `services/api/glow_persistence/` (models, migrations, the static check), `services/api/glow_api/` (routes, settings, configuration profiles), `packages/` (contracts), `proofs/`, `scripts/` or `.github/`.
- No change to `package.json`, `package-lock.json`, `.npmrc`, `dependency-inventory.json` (mobile or API), `requirements*.in` or `requirements*.lock`; to `apps/mobile/app.config.ts`, `src/app/_layout.tsx` beyond D7's one line, `eslint.config.mjs` or `src/config/`; or to any `AGENTS.md`, `CLAUDE.md` or other governing Markdown.
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
- **Then** the PR, Codex's review of its head, and an exact-head code review of the code head with a written threat model (OD-41; DM-31 item 3). The threat model covers the device and token path (custody, discard, the reference at the transport, logs and receipts) and also: the route's enforcement (the layout's line and its rendered reversal); the composer's content and recipients (no body, name, identifier or count; the read rule's refusals; the fixed routes); redelivery; the session binding (stale-session commands, logout, transfer); and the fixture-only guards (no provider, network client, native module, config plugin or credential). The reviewer re-runs at least the layout line's and the custody test's reversals at that head. Its prompt waits for Codex on the code head and on the commit that holds the prompt (manager workflow, step 6).
- **Dev Manager (DM-44, answered):** approved with conditions, applied as written in revision 2 (the header). The charter asked for this brief's read for four reasons:
  - it places a new domain component (D2);
  - it sets a security boundary for push tokens and notification content (D3, D4);
  - it decides against a dependency an earlier assessment expected (D6);
  - it adds one route to the route guard (D7).

  DM-44 also named F12's HTTP owner: SV4 (D9; the carried-items file, "Carried to SV4").

## Sessions

- **Brief, revision 1** (8 November 2026): written after the matrix recheck; sent to the Dev Manager as DM-44 ([consultation](../ephemeral/2026-11-08-dm-44-p06-3-brief.md)).
- **DM-44** (8 November; [report](../continuity/dev-manager/reviews/2026-11-08-dm-44-p06-3-brief.md), answered at `65618c1`, a read of `8bf9d8d`):
  - **approved with conditions.** The main finding: a screen's guard is its `Stack.Protected` line in `_layout.tsx`, which revision 1 excluded;
  - F12 is read per installation, and the denied path saves nothing;
  - the token goes to the store before its reference is saved, and is discarded when a registration ends;
  - redelivery is fixed by the first delivery's devices;
  - (a) approved for the native module, and SV4 approved as F12's HTTP owner;
  - DM-43's deferred confirmations confirmed.

  Accepted as written (the review log, "DM-44"). Revision 2 applies the conditions.
- **The implementation prompt** ([prompt](../ephemeral/2026-11-08-p06-3-implementation-prompt.md), revision 1, from `f9253bd`): for `Glow App - No Stream`; TypeSafe v8.2: Opus 5.5 at extra high. Given to Nathan on 8 November. **Done** (9 November; branch `claude/gallant-lovelace-vwgu69`, code head `9c4fef5`, records `7775bba`; Nathan's pick: not recorded):
  - **What it built:** Outcomes 1 to 5, with 26 reversals, each failing its test. Nothing met the stop rule.
  - **Its fixture-scope decisions, recorded for SV4:** the settings version is the installation's view revision; the mobile adapter keeps its own session record; the store waits one microtask on an account change.
  - **Run of record:** push run 42540179430 on `9c4fef5`. All eight jobs passed, with API 421 tests, mobile 680 and rendered 104 passed; no retry fired.
  - **Manager verification:** the diff within the owned paths; the search for clients and providers; six reversals re-run, each failing (the record, "Manager verification"). The manager branch fast-forwarded to `7775bba`.
- **PR41** (9 November 2026): P06.3's full-scope PR from the manager branch.
  - **Codex on `1dc1b0b`:** one finding, **F-C1** (P2). In the mobile fixture adapter, a request that starts before its session ends still acts for the ended session. The manager reproduced it: an active registration remains on the ended session, with its token held (the record, "Codex's review of `1dc1b0b`").
  - **F-C1 is in a correction class,** so it joins the exact-head review's pass (step 6).
- **The exact-head review prompt** ([prompt](../ephemeral/2026-11-09-p06-3-review-prompt.md), revision 2; revision 1 was not given): of code head `9c4fef5`, with DM-44 9.1's threat model and F-C1 as focus item 8, for `Glow App - No Stream`; TypeSafe v8.2: Fable 5.1 at extra high. It waits for Codex on the commit that holds it (step 6).
