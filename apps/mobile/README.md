# Glow native development foundation

An iOS/Android Expo Router application with fixture account/onboarding, profile/preferences/visibility, private media, bounded discovery and like/pass/match/unmatch journeys. This is an isolated development preview, not a usable dating service. All people and credentials are fictional. Media and interaction commands use in-memory substitutes; no photo reaches a real provider. Production authentication, interactions, messaging, provider uploads, persistence and HDE connections remain unavailable.

## Reproduce

Use Node **24.19.0** and npm **11.9.0** (both declared in `package.json`), then from this directory:

```sh
npm ci --ignore-scripts
npm run check
npm run check:expo
npm start
```

The `start`, `android`, and `ios` scripts explicitly select development fixture mode when unset. They reject any request for a different mode. On a suitably equipped workstation, `npm run android` or `npm run ios` opens the installed emulator/simulator. Native runtime and device acceptance have not yet been performed. Consumer web delivery is outside scope; only iOS/Android are configured. React DOM/web packages are pinned Router peers, not a web product.

The earlier nonpersistent API layout transport remains available for smoke checks. Its optional development origin is configured as follows after starting the isolated API:

```sh
EXPO_PUBLIC_GLOW_API_BASE_URL=http://127.0.0.1:8000 npm start
```

Use `http://10.0.2.2:8000` for the Android emulator's host loopback. A physical device requires a deliberately configured reachable development origin; loopback would point at the phone itself. This code does not change native cleartext networking policies: device HTTP transport must be verified separately. The transport loader uses bundled layout fixtures when no origin is configured. A configured loader failure remains an error without silently falling back to bundled data. P05.2 recommendation and broader-discovery screens use their separate, explicitly in-memory discovery composition, not this anonymous layout endpoint; setting an origin does not turn that journey into authenticated API discovery. The root HTTP/mobile smoke script exercises the retained transport.

`EXPO_PUBLIC_*` variables are public application configuration, never secrets. `.env.example` lists names and purposes. No production/HDE origin or secret belongs in this preview. Normal builds allow only `EXPO_PUBLIC_GLOW_MODE` and `EXPO_PUBLIC_GLOW_API_BASE_URL`, without echoing rejected names or values. The rendered test harness additionally accepts Expo's injected `EXPO_PUBLIC_PROJECT_ROOT` only when it exactly equals this app-config directory; arbitrary values remain rejected. This checks names, not the semantic contents of the allowed app values; the API-origin validator still rejects credentials. Official [Expo environment guidance](https://docs.expo.dev/guides/environment-variables/) confirms these values are embedded in client code. Reopen/reload Metro after changing environment configuration.

## Implementation boundary

- `src/app`: guarded account, verification/recovery, adult/consent, private birth and owner profile/preferences/media screens. Ordinary onboarding can save an incomplete profile; unresolved chart/policy and other eligibility requirements still prevent discovery even after synthetic photo approval. Recommended/explore layouts require current eligibility in the explicit fictional eligible scenario.
- `src/onboarding`: explicit synthetic adapter, versioned state/checkpoint boundary, civil-date policy and fixed-route allowlist. No local-storage, credential persistence or production endpoint is introduced.
- `src/profiles`: owner-bound in-memory adapter and drafts using existing generated profile/preferences/visibility contracts; provisional catalog, version/idempotency checks, completeness/visibility and candidate projection. No production protocol or durable persistence is added.
- `src/media`: owner-bound in-memory lifecycle adapter/store, versioned development limits, actual PNG container checks, Expo system-picker boundary and synthetic provider/system/moderator events. Current approved owned assets supply profile media evidence. There is no pixel decoder, metadata stripping, real storage/delivery or production media route.
- `src/contracts/recommendations.ts`: closed `gapp-dev-v1` response projection using generated TypeScript and standalone runtime schema validators. Rejects private/unrecognized fields, HDE scores/ready results, duplicate IDs and underage records. These checks are defense in depth; real eligibility must be enforced by the API in later phases.
- `src/data/recommendations.ts`: credential-free, bounded GET to `/api/v1/development/recommendations`, retained for layout/HTTP smoke with cancellation and response validation. This does not supply the P05.2 queue. No writes.
- `src/discovery`: bounded in-memory recommendation and broader-discovery composition, current per-candidate eligibility, continuation/adoption guards and shared fictional source corpus. See [discovery semantics](../../docs/architecture/discovery-fixtures.md).
- `src/interactions`: current-session fixture commands, immutable-receipt retry, committed consumption, participant-scoped matches and revocation. The Python domain remains authoritative; this presentation substitute follows shared contract cases.
- `src/config/development.ts`: explicit fixture configuration and origin validation.
- `app.config.ts` and `src/app/_layout.tsx`: build-config and runtime development guards.

Recommended and broader discovery use finite queues with accessible browsing controls, explicit refresh and honest exhaustion. Each mode preserves its own progress; switching modes does not reset it. Browsing records no like or pass, and no chat action is available. Portraits are synthetic placeholders, not real people or approved brand assets. Typography and color remain provisional implementation styling, not a brand lock.

## Release exclusion and verification

`app.config.ts` rejects any environment except `GLOW_APP_ENV=development` with `EXPO_PUBLIC_GLOW_MODE=fixture`; it also rejects EAS profiles other than `development`. The runtime refuses to render routes when React Native `__DEV__` is false. No EAS project, signing identity, application bundle ID, production profile or store distribution is configured. These are guardrails in this foundation, not a certification of a future release pipeline.

```sh
npm run export:development
```

This creates **development JavaScript bundles/assets** for iOS and Android in ignored `.work/native-export/`. It does not compile native code, sign a package, run an emulator/device or prove accessibility and native transport behavior. Do not deploy or distribute this output to real users.

Official scaffold: `create-expo-app@5.0.0` with `expo-template-default@57.0.26`, narrowed to mobile. The upstream MIT notice is preserved in `EXPO-TEMPLATE-LICENSE.md`. Exact dependencies and integrity values are in `package.json` and `package-lock.json`. See `../../docs/testing/mobile-foundation.md` for actual commands, results, sources and remaining evidence.

## P02 contract artifacts

P05.1's `src/eligibility/facts.ts` derives reciprocal fixture decisions from
explicit raw facts and shared
`packages/contracts/fixtures/reciprocal-eligibility-v1.json` corpus. Owner readiness
is separate from fictional viewer → owner candidate-preview permission; retained
results bind the current pair version and candidate age comes from private fixture
birth date/clock. The earlier Alex/Jordan/Riley items remain static smoke/layout samples in the
anonymous HTTP fixture. They do not supply the P05.2 journey, which independently
evaluates current owner-to-candidate pairs from the shared discovery population. See
[reciprocal policy/integration](../../docs/architecture/reciprocal-eligibility-fixtures.md)
and [P05.1 evidence](../../docs/testing/p05-1-checkpoint.md).
[P05.2 discovery](../../docs/architecture/discovery-fixtures.md) adds bounded
queues; P05.3 composes explicit interaction commands with their current authority.
No production endpoint is added.

`src/contracts/generated/` is generated from `packages/contracts` schemas. Do not edit it directly. The development parser consumes generated validation and a key-uniqueness check; `production.ts` adds parsers for the P02 logical design without an HTTP client or activated production route. Use the repository contract generation/check commands in `../../packages/contracts/README.md`. All current screen data remains synthetic and pending. No native dependency/API was changed for contract validation.

## P04.1 fixture walkthrough

Start at the account screen. Use **alex@example.invalid** or **sam@example.invalid**
and the displayed non-secret **fixture-passphrase**. Registration and sign-in both
normally lead to a controlled synthetic verification challenge. A seeded restricted
fixture account keeps its restriction after expiry/sign-in/recovery until an
explicit development scenario replaces it. Use the outcome controls
to exercise expired/invalid/wrong-context/replayed, temporary-error or rate-limited
results. After Expired, selecting Success still rejects the same challenge;
Resend creates a new usable one. Recovery receipts are neutral
for unrelated fictional addresses and never deliver email. A successful synthetic
reset requires a fresh sign-in.

After verification, enter a fictional civil date and accept the clearly labeled
development consent. The fixture clock is **2026-09-23T12:00:00Z** and demonstration
minimum age is **18**, with March 1 used for a leap birthday in a nonleap year.
These are explicit test inputs, not a launch-jurisdiction or legal decision.
A05 owns approved policy, terms, privacy and consent content before live use.

Enter private fictional birth facts using YYYY-MM-DD and, if supplied, HH:MM:SS.
Known and approximate times preserve their supplied values; unknown is null.
Historical timezone/provenance remain null. Resolution fixtures cover pending,
ambiguous, unavailable and unsupported; no form creates a chart. Saving ends at
**profile incomplete**, never discovery. Choose **Your profile and preferences**
to continue the P04.2 owner journey below, then **Manage your photos** for the
P04.3 fixture walkthrough. Photo approval does not resolve chart or launch policy.

Back navigation retains deliberate private-form edits within the current in-memory
session. Correcting the eligibility date clears obsolete saved/unsaved birth facts
and initializes the private date from that correction. An old form callback cannot
restore them. Ordinary publications and resolution retries retain deliberate edits.
If a submitted private birth date makes the age check fail, retained eligibility
screens show that new date; a no-edit Save cannot restore an older adult date.
Consent controls follow the current authoritative decision without silently
reaccepting a withdrawn value.
Development scenarios provide explicit eligible, underage, unknown-policy,
stale/withdrawn-consent, suspended and deletion-pending cases. Selecting a scenario,
logging out or expiring a session clears its private draft. Expiring a suspended
or deletion-pending session returns to account entry without requiring a scenario
reset; sign-in still enforces the same account restriction. Checkpoints accept only
validated snapshots issued by this live store for the same current account,
session and revision. They are not durable process-restart or cross-device storage.

```sh
npm run check
EXPO_OFFLINE=1 npm run check:expo
EXPO_OFFLINE=1 npm run export:development
npx playwright install --with-deps chromium
npm run test:rendered
```

The rendered suite starts Expo on localhost and exercises the actual Router and
React Native Web screens in Chromium. This is an internal development test surface;
Playwright sets `GLOW_RENDERED_TESTS=1` to enable web only for that process. Normal
product platforms remain iOS and Android, and release guards still reject unsafe
environments with the harness flag set. It tests interaction, guards and a
320px enlarged-text layout, not device keyboard behavior, VoiceOver/TalkBack,
secure storage, real links/email or signed builds. Failure traces and automatic
screenshots are disabled; only empty account and profile form layouts are explicitly captured.
See [P04.1 evidence](../../docs/testing/p04-1-checkpoint.md) and
[fixture architecture](../../docs/architecture/onboarding-fixtures.md).

## P04.2 profile and preferences walkthrough

From the remaining-onboarding screen choose **Your profile and preferences**.
The same owner-area link appears in recommendation and explore previews. An active,
verified session can manage its own profile even while discovery requirements are
missing; signed-out and restricted accounts cannot use the owner forms.

1. Choose **Create profile** or **Edit profile**. Enter a fictional display name
   and biography. A name must be nonblank and at most 80 contract characters;
   the biography can be exactly empty or nonblank up to 500. Whitespace-only text
   is rejected. Empty biography saves as incomplete; filling text does not approve
   photos or resolve a chart.
2. Choose **Leave and keep draft**, then return to the form. Deliberate unsaved
   edits remain in the same live session. **Cancel edits** returns to current
   accepted details without saving. **Save profile** updates the accepted record
   only after current ownership/version/response checks.
3. Use **Choose profile fixture outcome** to exercise **Temporary error**,
   **Invalid response** and **Version conflict**. The panel is labeled
   **SYNTHETIC TEST CONTROLS**. Retry a temporary error with Success; use
   **Refresh saved details** to inspect changed source state after a conflict.
4. Open **Edit private preferences**. The **PROVISIONAL PREVIEW CHOICES** use
   `development-preferences-1`, dimension `demo_connection`, and **Demo option A/B**
   (`demo_a`/`demo_b`). These are fictional editing examples, not selected launch
   geography, gender/orientation or matching policy. Preferences remain private.
5. Open **Preview saved profile**. The owner preview shows saved details, not
   unfinished edits. It is available for incomplete profiles and does not establish
   public visibility. The separate fictional eligible-viewer projection remains
   unavailable unless current candidate/viewer requirements pass.

At the original P04.2 checkpoint, ordinary onboarding could not supply approved
media. P04.3 adds synthetic photo approval; real chart resolution and approved
launch policy remain unavailable, so ordinary onboarding stays incomplete. The dashboard
lists current missing requirements instead of silently granting discovery.
An empty or saved profile is different from a complete/visible profile.

To exercise visibility, use the explicit eligible development scenario. It seeds
fictional chart/moderation and independent viewer/pair facts plus an approved
synthetic media asset, not actual provider work.
From the owner dashboard choose **Pause profile**. New recommendations and the
eligible-viewer preview become unavailable. Edit while paused; the saved profile
stays paused. **Resume profile** rechecks current eligibility and cannot restore
past contact permissions. P05.1 separates owner readiness from reciprocal pair
permission: saving current configured preferences can leave the complete owner
profile visible while excluding the fictional viewer's candidate preview. The
saved preference/source revision invalidates old pair contexts in either case.

The development screen can change synthetic profile, preferences, policy, media
or reciprocal source evidence while forms are retained. Revisit the forms to
inspect reconciliation and candidate/recommendation revocation. Stale callbacks,
logout, account changes, expiry and restriction must not restore earlier private
details or visibility. The existing P04.1 birth-date/consent/challenge and recovery
regressions remain part of the required evidence.

Saved records and drafts last only for the current in-memory session. Reloading or
closing the app clears them; no browser storage or cross-device recovery is added.
Use fictional input only. Do not capture populated private forms, credentials or
traces as public evidence. Run the same `check`, `check:expo`,
`export:development` and `test:rendered` commands above. See
[P04.2 architecture](../../docs/architecture/profiles-preferences-fixtures.md) and
[P04.2 evidence](../../docs/testing/p04-2-checkpoint.md) for actual results and limits.

## P04.3 private media walkthrough

From **Your profile and preferences**, choose **Manage your photos**. The screen
title is **Your photos, kept private.** Owner controls and the separate
**SYNTHETIC DEVELOPER CONTROLS** panel have different roles. Use only synthetic
files. Originals are represented by **Private photo placeholder**, never rendered.

1. Choose **Show media fixture controls**, then **Select fixture: Valid synthetic PNG**.
   The **Private selection** panel shows a bounded byte count. **Cancel selection**
   discards it without creating an upload. Alternatively, **Choose a test photo**
   opens Expo's image-only picker on native, or a bounded file selector in the
   internal browser harness. The browser reads a web `File`
   only after its size check, then checks the returned byte count. Native assets
   currently have no verified bounded reader and return unsupported without a grant.
2. Choose **Prepare private upload**. The photo enters **Upload pending**.
   Choose **Upload photo 1** to exercise synthetic progress and reach **Quarantined**.
   Upload completion alone supplies no approval or delivery permission.
3. In the developer panel, choose **System: send Photo 1 to review** to reach
   **Review pending**, then **Moderator: approve Photo 1** to reach **Approved**.
   These are simulated separate actors. Ordinary owner controls cannot approve
   media. **Moderator: reject Photo 1** instead produces **Rejected**; remove it
   before choosing a replacement. No rejected → upload-pending shortcut exists.
4. Repeat with a second synthetic photo. Approved rows offer **Move photo 1 earlier**
   and **Move photo 1 later**, with unavailable directions disabled. Ordering uses
   the current complete approved collection and its aggregate version.
5. Choose **Remove photo 1**. Delivery eligibility is revoked immediately;
   **Removal pending** remains until the developer-only **Provider: retry or confirm Photo 1 purge**
   succeeds. **Removed** means synthetic acknowledgment only. An error or
   interruption does not prove byte deletion.

Numbers in these labels follow the displayed row. **Refresh photo status** reads
accepted state; **Return to your profile** preserves eligible work within this
process. Revisit a retained screen before a full reload when checking revocation.
Logout, expiry and account replacement clear private presentation; a reload clears
all fixture state and is not interruption-recovery evidence.

The developer panel also offers **Simulate picker: denied**, **Simulate picker: limited**,
**Simulate picker: cancelled** and **Simulate picker: unsupported**; these do not
test device permissions. Invalid, unsupported, truncated, oversized and
excessive-dimension selection fixtures exercise the local boundary.
**Media fixture outcome: error** or **Media fixture outcome: interrupted** leaves
eligible upload work retryable through **Retry photo 1 upload**. Upload attempts
are bounded. **Cancel photo 1 upload** requests removal and still needs separate
purge acknowledgment. **Advance synthetic clock past grant expiry** exercises
actual fixture-clock expiry separately from **Media fixture outcome: expired**.
Returning the outcome to success never revives that grant; remove the pending
photo and select again for a replacement. **Invalidate synthetic media policy**
denies new grants and delivery. Malformed/stale/wrong-object outcomes are rejection
scenarios, not provider responses.

`development-media-1` currently allows PNG only, at most 1 MiB encoded, 2048 per
side, 4,194,304 declared pixels, four live photos, a 60-second app grant, three
upload attempts and three purge attempts. These are provisional fixture inputs,
not approved launch limits or Cloudflare guarantees. The collection ceiling of
twenty also bounds retained history; it is not the photo limit.

The parser checks signature, chunk framing/CRC, selected IHDR fields, IDAT/IEND
and resource limits. It does not decode pixels or remove metadata. Safe processing
and moderation are simulated; approved references are non-delivering strings,
and candidate photos remain labeled placeholders. Removing or restricting the
last approved photo blocks current discovery/eligible-viewer preview. A saved
`visible` profile can therefore show blocked effective visibility. Explicit pause
survives media changes; resume rechecks all current requirements. Photo approval
alone cannot satisfy missing chart, consent, adult, moderation or launch-policy
evidence. Reciprocal preferences and both block directions are separate pair
requirements, not circular prerequisites for owner profile completeness.

Run the existing check/export/rendered commands above. Their actual results are
recorded in [P04.3 evidence](../../docs/testing/p04-3-checkpoint.md), not implied
by this walkthrough. See [media semantics](../../docs/architecture/private-media-fixtures.md),
[provider mapping](../../docs/architecture/media-provider-mapping.md) and
[deferred acceptance](../../docs/testing/p11-deferred-acceptance.md) for the
remaining native, processing, storage, delivery, purge and durability proofs.

## P05.2 discovery walkthrough

Use the explicitly eligible fictional scenario, then open recommended people.
Ordinary registration/onboarding remains blocked when required facts are unresolved.
Each card comes from an independently checked pair in the shared fictional
population, with synthetic approved-media placeholders and pending compatibility.
No engine score or live Human Design result is implied.

Browse the finite recommended queue, then use broader discovery. Each mode keeps
its own progress; returning to a mode resumes it. A person can appear in both
separate mode queues, but not twice within one accepted queue. Reaching the end
shows exhaustion. Manual refresh creates a new bounded queue for that mode only;
neither browsing nor refresh records a pass, like or resurfacing decision.

The fixture uses two cards per page, scans/retains at most twenty candidates,
retains one queue per mode and expires a queue after five minutes on its numeric
lifetime clock, separate from the fixed civil-day eligibility fixture clock. Both modes apply the same reciprocal eligibility/disclosure rules; broader
discovery never restores an excluded candidate as fallback. Recommended ordering
is fixture priority then profile ID; broader ordering is profile ID. Neither
ordering expresses Human Design compatibility or selected launch policy.

Source changes, pause, consent/media loss, expiry, logout or account replacement
discard obsolete cards and continuations. Same-value restoration cannot resurrect
a former queue. Reload requires explicit refresh. Loading, empty, partial,
pending/unavailable, exhausted and error/offline states remain distinct; provider
errors do not mean there are no eligible people. A retry cannot adopt a late
response from an earlier request, account, mode or refresh.

Run the existing check/export/rendered commands above. The new discovery suite
adds to the inherited 52 browser cases, including the real-scroll birth-field
focus regression; hosted results are required when local Chromium is unavailable.
See [P05.2 checkpoint](../../docs/testing/p05-2-checkpoint.md) for actual results,
[discovery semantics](../../docs/architecture/discovery-fixtures.md) for exact
bounds/provenance and [P11](../../docs/testing/p11-deferred-acceptance.md) for real
authentication, persistence, provider and native-device acceptance.

## P05.3 interaction walkthrough

On an eligible fictional card, use the labeled **Like Fictional Jules** or **Pass Fictional Jules**
controls. Pending submission is announced separately from a committed result.
An accepted choice is consumed by authoritative interaction state in both modes;
switching modes or refreshing does not turn a saved pass into a new opportunity.
Committed actions invalidate any existing mode queues. Use **Refresh preview**
to start that mode's next bounded selection of remaining people; an untouched
mode still loads normally on first entry. A reciprocal setup that records only
the other person's private like leaves your current candidate page unchanged.
An error does not imply a successful like or match. **Retry same action** retains
the original intent and idempotency key; stale authority requires a fresh preview.

**Your matches** shows only the current participant's permitted connections. A
unilateral like produces no mutual-match row. On **Development scenarios**, the
explicit **Submit fictional Jules reciprocal like** setup submits the other
fictional participant's command through the same service. Use it before or after
your own like to exercise both arrival orders. This is an internal test setup,
not a client-supplied reciprocity or match flag. Normal screens never reveal
another person's unreciprocated action.

Open a mutual match to view only its allowed synthetic profile and current
connection status. **Unmatch** commits a versioned revocation. Pausing your
profile leaves **Your matches** available from the owner profile so an active
participant can still unmatch. Restricted and unmatched rows show a generic
connection status, with the former profile removed. Unblock and resume do not
reactivate a historical match. There is no undo, automatic rematch, provider
channel, messaging token or chat-history access.

The developer controls include normal, offline, lost-response and delayed
delivery. Select offline, submit a command, return delivery to normal, and choose
**Retry same action** to test a recoverable error. A lost-response scenario commits
before withholding confirmation, so its consumed card cannot become actionable
again while retry recovers the original receipt. A delayed submission exposes
**Complete delayed fixture delivery** in its clearly labeled fixture feedback.
Leaving a pending screen suppresses obsolete response adoption; account/session
replacement also clears private projections. Block/unblock setup uses the same
interaction authority and cannot grant a new match or contact permission.

Routes `/matches` and `/match` remain fixed, query-free Router destinations.
Selected IDs stay inside the current scoped store, and the service rechecks
participant access. Navigation guards are presentation safeguards, not backend
authorization. Web action buttons preserve keyboard focus during pending work;
committed/error feedback receives focus only on the active route. The rendered
suite covers these states at 320px as well as the 69 inherited cases. One inherited
refresh case now explicitly checks that navigation creates no committed result
while the new Like/Pass controls remain available; its finite-queue assertions
are preserved.

Implementation checked the committed Expo **57.0.24** and Router **57.0.22**
against the official [SDK 57 reference](https://docs.expo.dev/versions/v57.0.0/),
[documentation index](https://docs.expo.dev/llms.txt),
[Router API](https://docs.expo.dev/versions/v57.0.0/sdk/router/),
[navigation guide](https://docs.expo.dev/router/basics/navigation/) and
[protected routes](https://docs.expo.dev/router/advanced/protected/).
No package or native-directory change was needed. Actual check results belong in
[P05.3 evidence](../../docs/testing/p05-3-checkpoint.md); Chromium rendering does
not establish native keyboard, VoiceOver/TalkBack or signed-device acceptance.
