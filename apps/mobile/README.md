# Glow native development foundation

An iOS/Android Expo Router application with fixture account/onboarding, profile/preferences/visibility and private media journeys. This is an isolated development preview, not a usable dating service. All people and credentials are fictional. Media selection, lifecycle and review controls use in-memory substitutes; no photo reaches a real provider. Maintained production authentication, likes, matching, messaging, provider uploads, persistence and HDE connections remain unavailable.

## Reproduce

Use Node **24.19.0** and npm **11.9.0** (both declared in `package.json`), then from this directory:

```sh
npm ci --ignore-scripts
npm run check
npm run check:expo
npm start
```

The `start`, `android`, and `ios` scripts explicitly select development fixture mode when unset. They reject any request for a different mode. On a suitably equipped workstation, `npm run android` or `npm run ios` opens the installed emulator/simulator. Native runtime and device acceptance have not yet been performed. Consumer web delivery is outside scope; only iOS/Android are configured. React DOM/web packages are pinned Router peers, not a web product.

To exercise the nonpersistent API vertical smoke flow, first start the isolated application API using the repository setup instructions, then:

```sh
EXPO_PUBLIC_GLOW_API_BASE_URL=http://127.0.0.1:8000 npm start
```

Use `http://10.0.2.2:8000` for the Android emulator's host loopback. A physical device requires a deliberately configured reachable development origin; loopback would point at the phone itself. This code does not change native cleartext networking policies: device HTTP transport must be verified separately. Set no origin to use bundled fixtures. A configured API failure shows an error and a retry action; it never silently falls back to bundled data.

`EXPO_PUBLIC_*` variables are public application configuration, never secrets. `.env.example` lists names and purposes. No production/HDE origin or secret belongs in this preview. Normal builds allow only `EXPO_PUBLIC_GLOW_MODE` and `EXPO_PUBLIC_GLOW_API_BASE_URL`, without echoing rejected names or values. The rendered test harness additionally accepts Expo's injected `EXPO_PUBLIC_PROJECT_ROOT` only when it exactly equals this app-config directory; arbitrary values remain rejected. This checks names, not the semantic contents of the allowed app values; the API-origin validator still rejects credentials. Official [Expo environment guidance](https://docs.expo.dev/guides/environment-variables/) confirms these values are embedded in client code. Reopen/reload Metro after changing environment configuration.

## Implementation boundary

- `src/app`: guarded account, verification/recovery, adult/consent, private birth and owner profile/preferences/media screens. Ordinary onboarding can save an incomplete profile; unresolved chart/policy and other eligibility requirements still prevent discovery even after synthetic photo approval. Recommended/explore layouts require current eligibility in the explicit fictional eligible scenario.
- `src/onboarding`: explicit synthetic adapter, versioned state/checkpoint boundary, civil-date policy and fixed-route allowlist. No local-storage, credential persistence or production endpoint is introduced.
- `src/profiles`: owner-bound in-memory adapter and drafts using existing generated profile/preferences/visibility contracts; provisional catalog, version/idempotency checks, completeness/visibility and candidate projection. No production protocol or durable persistence is added.
- `src/media`: owner-bound in-memory lifecycle adapter/store, versioned development limits, actual PNG container checks, Expo system-picker boundary and synthetic provider/system/moderator events. Current approved owned assets supply profile media evidence. There is no pixel decoder, metadata stripping, real storage/delivery or production media route.
- `src/contracts/recommendations.ts`: closed `gapp-dev-v1` response projection using generated TypeScript and standalone runtime schema validators. Rejects private/unrecognized fields, HDE scores/ready results, duplicate IDs and underage records. These checks are defense in depth; real eligibility must be enforced by the API in later phases.
- `src/data/recommendations.ts`: credential-free, bounded GET to `/api/v1/development/recommendations`, with cancellation and response validation. No writes.
- `src/config/development.ts`: explicit fixture configuration and origin validation.
- `app.config.ts` and `src/app/_layout.tsx`: build-config and runtime development guards.

`Next fictional profile` only changes the locally displayed item. `Explore more` navigates to a list of the same fixtures. Both have non-gesture controls. There are no deceptive inactive like/chat buttons. Portraits are abstract initials, not real people or approved brand assets. Typography and color are provisional implementation styling, not a brand lock.

## Release exclusion and verification

`app.config.ts` rejects any environment except `GLOW_APP_ENV=development` with `EXPO_PUBLIC_GLOW_MODE=fixture`; it also rejects EAS profiles other than `development`. The runtime refuses to render routes when React Native `__DEV__` is false. No EAS project, signing identity, application bundle ID, production profile or store distribution is configured. These are guardrails in this foundation, not a certification of a future release pipeline.

```sh
npm run export:development
```

This creates **development JavaScript bundles/assets** for iOS and Android in ignored `.work/native-export/`. It does not compile native code, sign a package, run an emulator/device or prove accessibility and native transport behavior. Do not deploy or distribute this output to real users.

Official scaffold: `create-expo-app@5.0.0` with `expo-template-default@57.0.26`, narrowed to mobile. The upstream MIT notice is preserved in `EXPO-TEMPLATE-LICENSE.txt`. Exact dependencies and integrity values are in `package.json` and `package-lock.json`. See `../../docs/testing/mobile-foundation.md` for actual commands, results, sources and remaining evidence.

## P02 contract artifacts

P05.1's `src/eligibility/facts.ts` derives reciprocal fixture decisions from
explicit raw facts and shared
`packages/contracts/fixtures/reciprocal-eligibility-v1.json` corpus. Owner readiness
is separate from fictional viewer → owner candidate-preview permission; retained
results bind the current pair version and candidate age comes from private fixture
birth date/clock. Existing Alex/Jordan/Riley recommendation items remain static
smoke/layout samples, not independently evaluated candidate pairs. See
[reciprocal policy/integration](../../docs/architecture/reciprocal-eligibility-fixtures.md)
and [P05.1 evidence](../../docs/testing/p05-1-checkpoint.md). P05.2/P05.3 discovery
queues and interactions remain separate; no production endpoint is added.

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
