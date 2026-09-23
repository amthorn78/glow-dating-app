# P04.1 native account and onboarding fixtures

This document owns the mobile implementation notes for **AP1-P04.1-001**. The
authoritative app contracts remain [the production contract baseline](production-contracts.md),
`packages/contracts/production/flows-v1.json`, and
`packages/contracts/production/gapp-api-v1.schema.json`. F01 owns account access,
F02 consent/eligibility, and F03 private birth inputs. These app-local development
substitutes do not create production routes, accounts, credentials or HDE charts.
Observed execution results and limits belong to [the P04.1 checkpoint](../testing/p04-1-checkpoint.md).

## Runtime and trust boundary

The mobile implementation uses the pinned Expo **57.0.24** / SDK **57**, Expo
Router **57.0.22**, React Native **0.86.3**, and React **19.2.3** dependency family.
The existing explicit development/fixture guard remains required. The onboarding
adapter factory additionally refuses a nondevelopment runtime or any mode other
than `fixture`. It makes no HTTP, mail, geocoding, HDE or database call. There is
no configured-provider-to-fixture fallback.

The API retains its dummy backend and development/test GET surface. Account and
onboarding data are held inside the mobile fixture instance, not submitted to a
new credential endpoint. The production OpenAPI paths remain unavailable. The
contract transition oracle remains test-only and is not imported as a runtime
authentication or authorization service. Client route gates supplement future
server enforcement; they cannot replace it.

## Native shell and route gates

`src/app/_layout.tsx` mounts the provider only inside the existing development
guard and uses `Stack.Protected` for state-dependent routes. `src/app/index.tsx`
redirects to the current derived stage. `src/onboarding/routes.ts` owns the fixed
screen allowlist and gate predicates; route files contain presentation rather than
an alternate permission model.

| Screen route | Required fixture state |
|---|---|
| `/account`, `/recovery` | Account-entry stage |
| `/reset-password` | Account-entry stage plus a current synthetic recovery challenge |
| `/verify` | Verification stage |
| `/eligibility` | Active account and valid session |
| `/birth` | Active/valid account, adult pass and accepted current consent |
| `/remaining` | Same birth gate plus an accepted private birth input |
| `/restricted` | Restricted stage |
| `/recommended`, `/explore` | Explicit eligible development stage |
| `/development` | Enclosing development-only runtime guard; controls replace synthetic state |

`+native-intent.ts` sanitizes incoming destinations before stateful navigation.
Only allowlisted fixed paths or their `glow-development://` equivalents survive;
queries, fragments, encoded values, whitespace, backslashes and unlisted paths
return to `/`. It receives no authenticated context and grants no access. The
root layout also rejects search parameters/fragments and unsupported paths for
the web development runtime. `+not-found.tsx` returns to `/`. No private value is
passed as a route parameter. Protected-route history and actual direct-link
behavior still require the rendered evidence recorded separately in the checkpoint.

The shared `Page` primitive combines safe-area layout, keyboard avoidance and a
scrollable content container. `ScreenTitle` requests focus on route focus;
`Feedback` exposes busy/error/status presentation and requests error focus. Fields
have visible labels and accessibility labels/hints; buttons expose their role and
disabled state; choices expose radio and selected/checked state. Controls use
minimum heights rather than fixed text boxes, and ordinary React Native text
scaling is retained. These source-level provisions are not a VoiceOver/TalkBack
or native keyboard/device acceptance claim.

## Controlled account adapter — F01

`apps/mobile/src/onboarding/fixture-adapter.ts` declares `OnboardingAdapter` and
its explicit fixture implementation. It owns synthetic account, verification,
resend, recovery, reset and birth operations. Publicly documented fictional
`alex@example.invalid` and `sam@example.invalid` accounts and
`fixture-passphrase` are test controls, not live credentials. Registration and
sign-in presentation select the same bounded synthetic identity set; neither
provisions a real account or retains a new password.

Account entry returns an unverified account. Only the controlled adapter's
verification result can transition it to active. Challenges bind to fixture
generation and account context, carry an explicit expiry, and are consumed once.
The adapter rejects used, expired or wrong-context challenges. Outcome controls
exercise invalid, expired, wrong-context, replayed, unavailable and rate-limited
responses without creating actual verification links. Resend replaces the current
synthetic challenge. Fixture timing is deterministic and is not a production
expiry or rate-limit commitment.

Recovery accepts the designated `example.invalid` synthetic address namespace
with the same receipt for known and unknown fixture addresses. It sends no email
and does not disclose which test identities can sign in. A successful synthetic
reset consumes its challenge, clears session/verification state and requires a
fresh sign-in. No JWT, session token, signing key or password database is created.
Adapter invalidation advances its epoch so an already-awaited operation cannot
complete into a later session.

The maintained provider choice remains **django-allauth headless**. The committed
[mapping](production-contracts.md#maintained-authentication-reference-and-app-mapping)
plans its JWT strategy with stateful session validation and refresh rotation.
Official documentation describes incomplete authentication through
`X-Session-Token`, access/refresh delivery on completion, and the DRF
`JWTTokenAuthentication` integration. These are future provider responsibilities;
P04.1 adds no allauth dependency or invented endpoint/token implementation. Pin
and inspect the actual installed allauth release and configured specification
before real wiring, then prove persistence/revocation at P11 DB09.

## Eligibility, consent and restoration — F02

`apps/mobile/src/onboarding/policy.ts` defines an explicit demonstration policy:
`development-consent-1`, minimum age **18**, March-1 handling for a February-29
birthday in a nonleap year, and fixed evaluation clock
**2026-09-23T12:00:00Z**. These choices are synthetic inputs for reproducible
boundary tests. They are not selected launch jurisdiction, legal advice, approved
terms/privacy text or a production age policy. A05 still owns those decisions.

Civil-date validation checks Gregorian month lengths and leap years. Missing or
invalid dates, a future date, absent policy or an invalid evaluation clock cannot
produce an adult pass. The explicit UTC evaluation clock never assigns a
historical timezone to a birth fact. Consent and eligibility continue to use the
generated closed contract shapes and versioned state.

`apps/mobile/src/onboarding/store.ts` derives the stage from the current account,
session, explicit adult result, current consent/policy and remaining profile
requirement. Missing policy adds `region_policy`; anything other than an adult
pass or current accepted consent keeps eligibility incomplete. Suspended,
deletion-pending and deleted account states derive the restricted stage. Fixture
scenario selection is an explicit state replacement that clears the earlier
session, not a production permission mechanism.

The store accepts an asynchronous completion only if its captured generation,
revision and operation still match. The fixture adapter holds unacknowledged birth
mutations until the store validates and accepts them; cancellation rolls them back
so a discarded response cannot strand the UI at an obsolete object version.
Logout, expiry and account/scenario changes
invalidate earlier operations and clear the issued checkpoint. State snapshots
are frozen; public subscriptions receive a current read-only presentation view.

Resumability has two bounded layers. The React context retains the unsaved private
birth draft across navigation, keyed by account, session state and generation so
account/session replacement creates a fresh draft. The explicit synthetic
checkpoint stores already accepted adult/consent/birth state in the same store
instance. Restoration requires the exact checkpoint issued by that instance,
matching generation/revision/account/account-version, valid closed contract
objects and current consent policy. A mutation invalidates that checkpoint; a
serialized object cannot invent identity, rewind consent or resurrect an old
birth revision. Neither layer survives process restart or establishes cross-device
persistence. No SQLite, local password/token storage or shadow backend is added.

Ordinary completion ends at **profile incomplete**. P04.2 owns profile/preferences
work and P04.3 owns media. Account verification and birth-input completion cannot
grant profile completeness or discovery. The existing recommendation examples
can be exercised only as an explicitly selected eligible development scenario.

## Private civil birth facts — F03

The adapter consumes generated `BirthInputIntent` and returns generated
`OwnBirthInput`, validated with the same committed runtime validators as the
wire contract. A new input uses `expected_version=0`; corrections must match the
current version. Each accepted save advances the input version and leaves
`mapping_version` null. Fixed synthetic app input identifiers are distinct from
engine chart identity; no engine identifier is created.

Known and approximate times retain their supplied civil value and precision.
Unknown time stays null. Historical timezone and provenance remain nullable when
unsupported; the device timezone, noon and UTC are never substituted as birth
facts. The adapter rejects invalid/future civil dates in addition to schema
validation. Its outcomes are `pending`, `ambiguous`, `unavailable` and
`unsupported`, never an invented resolved chart. An unavailable result can be
retried against its current version; stale corrections/retries refuse.

Birth facts belong to the owner-only input and draft state. Candidate projections,
recommendation payloads, route parameters and ordinary telemetry must not include
them. Use fictional facts only in development, and keep private-form contents out
of public evidence screenshots. Exact negative-projection and stale-state test
results are recorded in the checkpoint once executed.

## Final integration and remaining work

Real authentication, persisted consent/birth state, secure native token storage,
server authorization, concurrency, provider delivery and cross-device recovery
remain P11 work. Signed native/device, screen-reader, OS deep-link and keyboard
acceptance retain N01 in the [deferred matrix](../testing/p11-deferred-acceptance.md).
A browser interaction test and a development JavaScript export have separate,
limited claim scopes. No new auth/media provider, Railway deployment, app database
connection or HDE invocation is needed to demonstrate this fixture slice.

The separate
[AB1-DBA-001 audit](https://app.notion.com/p/3e44590a05eb81908661fc44eca0ce20)
is completed read-only evidence, not P04.1 database authorization. It supports
the owner-preferred shared logical database only after reviewed app schema/role
isolation. The exact 32-model physical mapping is still open. Preserve the `hde`
schema, `public.hde_body_graphs_current` and current legacy dependencies; no
fixture implementation changes those objects or performs their retirement.

## Official sources checked for this slice

Checked 23 September 2026 against the installed package family and the maintained
auth mapping. Implementation details above remain grounded in repository source;
these references establish platform APIs, not app execution success.

| Source | Relevance and limit |
|---|---|
| [Expo SDK 57 reference](https://docs.expo.dev/versions/v57.0.0/) | SDK-specific native modules and React/React Native compatibility; preserve the committed exact pins |
| [Expo Router protected routes](https://docs.expo.dev/router/advanced/protected/) | Client navigation guards remove inaccessible history; they do not enforce server authorization. The documented `redirectTo` option is SDK 58+, so it is not assumed available in this SDK 57 app |
| [Expo Router native intent](https://docs.expo.dev/router/advanced/native-intent/) | `redirectSystemPath` handles arbitrary native incoming values outside auth context; web needs its separate route handling |
| [React Native accessibility](https://reactnative.dev/docs/accessibility) | Labels, roles, states, focus and live-region semantics; platform behavior requires actual native testing |
| [allauth headless](https://docs.allauth.org/en/latest/headless/index.html) | Maintained authentication boundary; no real adapter is installed by P04.1 |
| [allauth session strategy](https://docs.allauth.org/en/latest/headless/token-strategies/session-tokens.html) | Maintained native incomplete-auth/session mechanism |
| [allauth JWT strategy](https://docs.allauth.org/en/latest/headless/token-strategies/jwt-tokens.html) | Maintained access/refresh strategy, rotation, stateful revocation and DRF integration |
| [allauth OpenAPI reference](https://docs.allauth.org/en/latest/headless/openapi-specification/) | Authoritative future credential API reference; the configured release specification must be obtained at integration, not guessed from app fixture methods |
