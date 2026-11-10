# SV2 — The profiles and media slice: the profile, its settings, consent and photos, proven on disposable PostgreSQL

- **Work ID:** SV2 (OD-49, N1 (a); PF01 §8, "Server slices"; the F02, F03, F04, F05 and F06 flows).
- **Status: brief, revision 1, 10 November 2026, by App Manager 10.** It goes to the Dev Manager before any prompt (the charter; DM-31 item 3; "Review plan").
- **Owner:** Nathan Amthor, by the order he resumed on 26 October (OD-49): the server slices SV1 to SV4 after P06.3, before P10. **Manager:** App Manager 10. **Sessions:** one implementation session per stage (D1), each started by Nathan, in `Glow App - No Stream` (no Stream call, no provider, no credential).
- **Starting point:** `main` at `c864edd` (PR42, SV1), with the manager branch's Markdown records after it. Each prompt names the exact commit.
- **Evidence home:** `docs/testing/evidence/<date>-sv2-profiles-media.md`, written by the sessions.

## Why

- **PF01 §8, "Server slices":** *"Before P10, the production HTTP API, maintained authentication (django-allauth headless with the mail adapter) and the ORM persistence adapters of each domain are built as four slices: … SV2, profiles and media … Each is proven on a disposable PostgreSQL in CI under P06.DB's rules (no shared or production database, CI-generated credentials, the runtime guards kept). The runtime stays sealed until P11 wires it."*
- **PF01 §6, the data groups:** *"Profile, preferences, visibility | Separate private/public projections; reciprocal eligibility, completion and pause states; age and location disclosure boundaries"* and *"MediaAsset | Owner, storage reference, state, order and moderation decision; only approved variants eligible for public delivery"*.
- **PF01 §7, "Media":** *"Issue short-lived upload grants; enforce ownership, size/count/type limits and safe decoding. Strip metadata, quarantine originals, moderate before publication and expose only approved variants through authorized delivery. Handle abandoned uploads, reordering, retries, removal and downstream purge. Neither an uploaded filename nor a successful vendor upload proves that an image is safe or publicly eligible."*
- **PF01 §4, the Media row:** *"Cloudflare Images/private R2 as appropriate | Reuse upload/storage/delivery; build authorization, quarantine, moderation and lifecycle state"*; and §1: WordPress is *"the staff admin and support interfaces (OD-19). Its staff tools use only scoped Django APIs."*
- **The flows** (`flows-v1.json`; `production-contracts.md`):
  - **F02**, identity/consent: *"Unverified/underage/withdrawn/suspended cannot use discovery; old consent version rejected"*;
  - **F03**, private birth inputs: *"Unknown time remains unknown; changed input invalidates old mapping; engine identifiers never invented"*;
  - **F04**, profiles/preferences: *"Wrong owner edit/read rejected; unknown dimension/option policy rejected; public birth leakage rejected"*;
  - **F05**, media: *"Upload cannot skip quarantine/review; wrong owner reorder/remove fails; provider purge completion separate"*;
  - **F06**, visibility: *"Pause invalidates queues; resume rechecks current visibility eligibility; unknown pause/contact policy denies contact"*.
- **Nathan's answer to the second A05 message** ([OD-60](../continuity/owner-directions.md), 10 November 2026): every choice is a stored, versioned, audited setting with a launch default, editable later in the admin console, within fixed limits the console cannot cross. For SV2:
  - four two-way list fields: gender, orientation (matched both ways), looking for, relationship status;
  - an age range applied both ways by default;
  - a home city or region, or the phone's approximate location.
- **Carried to SV2** (the carried-items file):
  - from P09.3a's matrix: **G-02's seam**, a place in the media quarantine path for a detection step, its report evidence and a hold, building none of them; and **G-10**, consent at entry for orientation and relationship status, and consent wording that says what chat history stays readable (DM-51 M15);
  - **DM-50 1.2,** if SV2's work changes `identity_support.py`: `mail_forbidden_found`'s docstring reworded ("every code the run's cases issued") and a test that pins the removal as exact, case-sensitive and of every occurrence;
  - **the matrix's recheck for OD-60** is done (the [recheck record](../testing/evidence/2026-11-10-od-60-matrix-recheck.md)). Its facts for this brief: a chosen city is Google's "Approximate location"; the state laws define precise geolocation as data derived from a device or technology that locates a person within 1,850 feet (California) or 1,750 feet (Texas, Virginia).

## Outcome

SV2 builds the server's profile, its settings, consent and photos on SV1's actor, proves them on a disposable PostgreSQL in CI, and keeps them sealed from the served runtime.

1. **The settings store** (OD-60; D2): every OD-60 choice is a versioned setting with its launch default. A change is made through one domain operation that validates the fixed limits, writes the new version and a `StaffAudit` row, and emits an invalidation event. P07's console calls that operation later; SV2 builds no staff HTTP route.
2. **The profile's fields** (D3): the four two-way list fields, each with the member's own value and a "show me" set; the member's own words for gender and orientation, for display only; the display choices.
3. **Age range and location** (D4, D5): the member's age range, and a home area chosen from a reference table or set once from the phone's approximate location, with only the area kept.
4. **Consent and the adult check** (F02; D6, D7): onboarding consent and the sensitive-fields consent (G-10), each versioned and withdrawable; the age state written from the self-entered birth date through SV1's port.
5. **The private birth input** (F03; D8): the member's own birth facts, submitted and corrected, kept private, with no HDE call.
6. **Visibility and completion** (F04, F06; D9): completion, pause and resume through `glow_chat`'s reviewed writers, so the send check sees them.
7. **Photos** (F05; D10): upload grants, quarantine, G-02's seam, moderator decisions as domain operations, reorder, removal and purge, through a provider port with a fixture adapter only.
8. **Glow's routes for the member** (D11): own profile, fields, preferences and filters, consent, birth input, visibility and photos, each validated against the contract, through SV1's actor.
9. **The proof** (D12): the profile cases (the acceptance checks below) on a disposable PostgreSQL in CI, through the HTTP endpoints with Django's test client, under P06.DB's rules.
10. **Sealed** (D13): the served runtime imports none of the new code, and its database backend stays Django's dummy one.
11. **The records:** the data model's profile, preferences, consent and media rows, rewritten as built; the contract's new DTOs; the P11 plan's partial evidence (DB04, DB07, DB08, DB10, PV04); the evidence record, with the threat model's inputs.

## Design

- **D1 — Scope, stages and seal.**
  - **Two stages in one item, each with its own session and verification** (recommended): **Stage A**, items 1 to 6 and their routes; **Stage B**, item 7 (photos) and its routes. One exact-head review covers the final code head, and one PR carries both. The alternative is one session for everything; its diff would be about twice SV1's, across two security boundaries (sensitive data and uploaded files).
  - **Sealed until P11,** as SV1 was: no deployed URL, no provider, no real member, no credential beyond what CI generates for one run. The mobile app is unchanged: its fixture adapters stay until P10 and P11 wire the client (PF01 §7).
  - **No staff HTTP route.** P07 builds the staff-scoped admin API and the WordPress views (PF01 P07). SV2 builds the domain operations they will call, each taking a staff subject and a reason and writing `StaffAudit`.
- **D2 — The settings store** (OD-60).
  - **The settings:**
    - the four lists: values with stable IDs and labels, which values are retired, and how many values a member may pick (gender 1, orientation 1, looking for any number, relationship status 1, at launch);
    - whether members may narrow by each field;
    - the age range's default and direction (both ways or the viewer's only);
    - the distance choices and their default;
    - resurfacing, the undo and rematch, each off at launch with its waiting period (SV3 reads them);
    - H's choice per cause, read-only for every cause at launch (SV4 reads it);
    - the media policy (D10).
  - **The model:**
    - one append-only row per setting version (name, version, content, publication time, staff subject, reason);
    - content validated against a closed schema per setting before it is written;
    - `PolicyRevision` as the current pointer per name (the data model: "Policy pointer is transactionally locked alongside actions").
  - **The launch defaults** are seeded by a data migration as version 1 of each setting, with the staff subject `system:launch-default` and the reason "OD-60".
  - **The fixed limits are code, not data.** OD-60's limits:
    - matching uses list values;
    - the age floor is 18;
    - never exact coordinates or an exact distance;
    - rematch never after a block or a report;
    - unmatch and block stay hidden;
    - a deletion works as an unmatch.

    A publication that crosses one is refused before anything is written.
  - **A change applies from then on** and emits `policy_published` in the outbox for SV3's invalidation. A retired list value stays valid for members who hold it, and their data stays matchable. It is not offered for new choices, and the member is asked to choose again at their next edit.
  - **Open for the Dev Manager:** whether a retired value should instead stop matching; and whether the media policy belongs in this store (recommended) or stays a code constant until the third A05 message.
- **D3 — The four list fields and the display choices** (OD-60, P1).
  - **Own values:**
    - one row per account and field, holding the selected value IDs and the setting version they were chosen under;
    - indexed for SV3's queries;
    - a reserved "not stated" value for orientation, which is in every "show me" set that keeps all.
  - **"Show me" sets** go in `Preferences.values`, policy-versioned, as the existing `PreferenceSelection` shape already holds them (dimension, accepted option IDs). Each starts at all.
  - **The two-way rule,** which SV3 applies, is defined here, so SV2's records hold what it needs: a field matches when at least one of each person's values is in the other's set, for every field.
  - **Own words:** bounded text for gender and orientation (proposed: 40 code points), display only; never matched, searched or used by ranking. Moderating free text is P07's.
  - **Display choices:** one flag each for gender, orientation and relationship status, off until the member turns it on; "looking for" is shown; "show me" is never shown. The candidate projection that reads these flags is SV3's.
- **D4 — The age range** (OD-60, P2): the member's minimum and optional maximum, never below 18, defaulting to the setting's default. The direction is the setting's. SV3 applies it, reading each member's age from the age state's date (D7).
- **D5 — The location** (OD-60, P2; the recheck record).
  - **The area table:** reference data with stable area IDs, a name and an internal point. **Recommended source:** the US Census Bureau's 2024 Gazetteer file for core-based statistical areas (metro and micro areas, fewer than 1,000), public domain, pinned by SHA-256 and loaded by a data migration. It was reachable from this environment on 10 November 2026: 46,177 bytes, last modified 30 August 2024. **The alternative,** the Gazetteer's places file (cities and towns, about 32,000; 1,221,402 bytes), is finer, so it reveals more and makes tiny groups likelier.
  - **The member chooses an area, or sends the phone's approximate location once.** The server maps it to the nearest area's internal point and keeps only the area ID. The coordinates are never stored, logged, returned or put in the outbox, and a test asserts each of the four.
  - **The distance limit** is one of the setting's choices, measured between area internal points. No distance is ever returned. SV3 applies the filter and tests repeated filter changes and tiny groups (DM-51 M9).
  - **`Profile.location_label`,** the existing text label, is replaced by the area ID; its display text comes from the area's name.
  - **Open for the Dev Manager:** the area source; and whether the internal point should be the published one or a coarser grid cell.
- **D6 — Consent** (F02; G-10).
  - **Onboarding consent:** F02's accept and withdraw for purpose `onboarding`, through `glow_chat`'s `accept_consent` and `withdraw_consent`. Those operations join the lock protocol (DM-13 4.1), so the send check reads them current.
  - **The sensitive-fields consent:** purpose `sensitive_profile`, required before orientation or relationship status is saved. Withdrawal removes the member's own orientation and relationship status values, and resets those two "show me" sets to all. The member then appears as "not stated", only to viewers who keep all orientations (OD-60).
    - **Its own writer.** `glow_chat`'s `_decide_consent` writes purpose `onboarding` only (`chat.ONBOARDING_CONSENT_PURPOSE`), so this consent needs a writer in SV2.
    - **Recommended:** a writer that takes the account row lock first in the canonical order (P06.DB 5.3; DM-13 4.1), appends the decision, and changes the field values in the same transaction. The alternative, widening `glow_chat`'s writer to take a purpose, changes a reviewed module that SV2 otherwise leaves alone.
  - **The wording** is a versioned policy whose text is not SV2's: development text, labelled as such, until P08 writes it with H's readable rule (DM-51 M15). A version change that makes more readable asks the member to accept again (OD-60, H).
- **D7 — The adult check and the age state** (F02; G-01; SV1's D9).
  - F02's adult check takes the self-entered birth date. With the date valid and 18 or over at the evaluation time, it writes `self_declared_adult` through `AgeAssurancePort`, and SV1's `unknown` row is updated. Otherwise the account stays out of discovery (F02's acceptance).
  - **The date's one home** (recommended): the date is kept only as the first revision of the private birth input (D8), so it is never stored twice.
  - **Open for the Dev Manager:** the alternative, a date kept with the age state, and whether the check reruns when the birth input's date is corrected.
- **D8 — The private birth input** (F03).
  - The owner's `submit`, `correct` and `change` transitions on `BirthInput` revisions, stored as private input with its provenance and uncertainty. An unknown time stays unknown.
  - `EngineIdentity` stays `pending`, and no transition the HDE would decide (`resolve`, `ambiguous`, `unsupported`, `outage`) is built. No HDE call, and no engine identifier is invented (the protected boundary; A01).
- **D9 — Visibility and completion** (F04, F06).
  - **Completion** (`incomplete` → `visible`) requires:
    - onboarding consent accepted;
    - the adult check passed;
    - a display name and a non-empty summary;
    - a gender;
    - an area;
    - at least one approved photo (recommended; Stage B adds it).

    The sensitive fields are not required.
  - **Pause and resume** go through `glow_chat`'s `pause_profile` and `resume_profile`, and restriction through `restrict_profile`, so the send check and its race cases (P06.2 D5, 6.1) see them; SV2 adds no second writer.
  - **Resume rechecks completion first.** `resume_profile` moves `paused` to `visible` with no completion check of its own, so SV2's resume refuses an incomplete profile before calling it.
  - **Open for the Dev Manager:** how SV2's check and `glow_chat`'s write share one transaction, so a requirement withdrawn in between cannot be missed.
  - **Each change emits** the outbox event SV3's invalidation reads.
- **D10 — Photos** (F05; G-02; Stage B).
  - **A provider port with a fixture adapter only.** No Cloudflare call; P11 adds the adapter and PV04's proof.
  - **The upload grant:** short-lived, opaque and one-use, within the media policy's limits. The policy's version 1 holds `development-media-1`'s values: PNG only, 1 MiB, 2,048 × 2,048, four live photos, a 60-second grant, three attempts. The launch values are A05's ("media limits"), and they go to Nathan with the third A05 message.
  - **The quarantine path:** `uploaded` → `quarantined` → `review_pending`, with **G-02's seam** between them, a port for a detection step. SV2 configures none and records "no detector". The seam also keeps a place for report evidence and a hold that blocks approval, and builds none of them.
  - **Moderator decisions** (`approve`, `reject`, restriction) are domain operations that take a staff subject and a reason and write `StaffAudit`; P07 exposes them.
  - **Reorder** uses collision-safe temporary positions inside one unit of work (the data model's note). **Remove** withholds delivery at once, moves to `removal_pending`, and becomes `removed` only on the provider's purge acknowledgment.
  - **Delivery** returns only an approved variant's reference; signed delivery URLs are P11's.
- **D11 — The contract: additive DTOs** (recommended). New DTOs in the v1 production schema; every existing DTO is unchanged, so the mobile app's generated validators and fixtures are untouched until P10:
  - the member's own field values and display choices, with their reads;
  - the age range and the area, with their reads;
  - the current catalog: the lists, which may be narrowed, and the defaults, read-only for the member;
  - the sensitive-fields consent, which is `ConsentIntent` with its new purpose.

  `PreferencesIntent` keeps carrying the "show me" sets. The shared corpus gains each new DTO's cases, and the production catalog's paths map stays empty until P11 serves the routes. **The alternatives:** change the existing DTOs and the mobile fixtures with them; or a new schema version.
- **D12 — The proof: P06.DB's job, a third disposable database.**
  - **Where it runs:** the profile suite lives in `proofs/postgres-ordering` beside the identity suite, with its own settings and marker, and signs in through SV1's identity routes to get an actor. It runs after the identity suite, on a third database in the same disposable PostgreSQL 17.11, and applies the reviewed migrations from zero.
  - **The run's secrets** are generated in the job and handled as SV1's are (SV1's D10): files in the job's protected temporary directory, read from paths, never printed. The secret check covers the new suite's log and results JSON before any upload.
  - **The timeout:** the job stays within its 30 minutes, and the evidence records the profile phase's duration.
- **D13 — The seal, checked.** A test in the style of SV1's proves that the runtime's settings, URL configuration and WSGI application import none of the new modules, and that the database backend is dummy. `glow_api/` is not changed.
- **D14 — No new dependency** expected: Django, DRF and allauth are pinned already. The area file is data, pinned by its SHA-256, with its source and licence recorded. Any new package stops the session.
- **D15 — Every test comes with its reversal,** recorded with its failing output, as SV1's were.
- **D16 — DM-50 1.2,** if Stage A's suite changes `identity_support.py` to share its sign-in helpers: the docstring's rewording and N-2's pin land in the same change.
- **D17 — Disclosure.**
  - Own data is returned only to its owner. No member's other private data is returned anywhere: not their "show me" sets, the sensitive fields when hidden, the birth input, the coordinates, or a photo that is not approved.
  - Each route's response is validated against its DTO, so extra fields fail.
  - The candidate projection is SV3's.

## Owned paths (the sessions)

- `services/api/glow_profiles/**` (new): the app, its views, URL configuration, settings store, the area table loader, the media port's fixture adapter and the domain operations.
- `services/api/glow_domain/`: new modules for the profile fields, the settings' schemas and fixed limits, and the media port only.
- `services/api/glow_persistence/models.py` and new migrations after `0004` (the settings, the field values, the area table and its data, consent's new purpose, the media grant): only what D2 to D10 need.
- `services/api/tests/`: new profile, settings, media and sealed-runtime tests; `test_model_definitions.py` where the new models require.
- `packages/contracts/production/gapp-api-v1.schema.json`, `openapi.json` (DTOs only, no paths), `corpus/shared-v1.json` and the contract tests: D11's additions only.
- `proofs/postgres-ordering/**`: the profile suite, its settings, tests and locks; `identity_support.py` only as D16 says.
- `.github/workflows/foundation.yml`: the Database proof checks job's steps only.
- `docs/architecture/data-model.md` (the rows named in Outcome item 11), `docs/architecture/production-contracts.md` (F02 to F06's server mapping), `docs/architecture/profiles-preferences-fixtures.md` and `private-media-fixtures.md` (a note that the server exists, sealed), `docs/testing/p11-deferred-acceptance.md` (the partial evidence), and the evidence record.

## Manager-owned

- This brief, the carried-items file, the handoff, the review log and Notion.
- **The CI policy's Database proof checks paragraph** (governing Markdown): the manager updates it after each stage, and the Dev Manager reads it at a named commit before the PR merges.

## Exclusions

- `services/api/glow_api/**`: the runtime stays sealed.
- `services/api/glow_chat/**`: SV2 calls its reviewed writers unchanged.
- `services/api/glow_identity/**`: SV2 uses its actor class and age port unchanged.
- `apps/**`, `wordpress/**`, `proofs/stream-chat/**`, `scripts/**`, other workflow jobs, the `Dockerfile`, every environment template, `requirements.in` and `requirements.lock`.
- Any provider (Cloudflare, an HDE adapter, a detection or moderation vendor), any staff HTTP route, any device location permission in the app, any real member or photo.

## Dependencies and inputs

- `main` at `c864edd`; PF01 1.17 §1, §4, §6, §7 and §8; F02 to F06 and their DTOs; the data model; the contract; the P11 plan's DB04, DB07, DB08, DB10 and PV04; SV1's brief and record (the actor class, the age port, the proof's identity suite); `glow_chat`'s writers; OD-12, OD-49, OD-55 and OD-60; the matrix's G-02 and G-10, and the OD-60 recheck record; the media provider mapping and the fixtures it maps.
- **The Census Bureau's Gazetteer files,** checked on 10 November 2026: `2024_Gaz_cbsa_national.zip` (46,177 bytes) and `2024_Gaz_place_national.zip` (1,221,402 bytes), each answering `200`, last modified 30 August 2024.

## Acceptance checks

**In `services/api`, with `GLOW_ENV=test`, in a clean process environment:** `python manage.py check`, `python manage.py test tests --verbosity 2`, `ruff check .`, `ruff format --check .` and `mypy`, all clean. **In `packages/contracts`:** its tests, with the corpus run through Python and the generated validators. **In `proofs/postgres-ordering`:** its offline tests under `env -i`, Ruff and mypy.

**In CI, the Database proof checks job on the code head,** after the ordering and identity suites, on the third database, through the HTTP endpoints:
1. **The settings:**
   - every OD-60 setting reads its launch default;
   - a publication writes a new version, a `StaffAudit` row and `policy_published`, and moves the pointer;
   - a publication crossing each fixed limit is refused, and nothing is written;
   - a retired value stays matchable for its holder and is refused for a new choice.
2. **The fields:**
   - each of the four fields accepts list values within its pick limit, and refuses an unknown value, a retired value for a new choice, and a value over the limit;
   - orientation and relationship status are refused without the sensitive-fields consent;
   - the own words are bounded, and never appear where their display flag is off.
3. **"Show me" sets** start at all, take list values only, and are never returned to anyone but their owner.
4. **The age range** refuses a minimum below 18 and a maximum below the minimum.
5. **The location:**
   - an area is chosen by ID;
   - approximate coordinates map to the nearest area, and afterwards they are found in no table, log line, response or outbox event;
   - no route returns a distance.
6. **Consent:**
   - onboarding consent's accept and withdraw reach the send check through `glow_chat` (a send refused after a withdrawal);
   - the sensitive-fields consent's withdrawal removes the two values and resets their sets;
   - an old consent version is refused.
7. **The adult check:** 18 today passes, as do the leap-day cases of the onboarding fixtures; under 18, a future date and an invalid date each fail, and the age state stays `unknown`.
8. **The birth input:** submit, correct and change write private revisions; an unknown time stays unknown; no route returns another member's input; `EngineIdentity` stays `pending`.
9. **Visibility:**
   - completion refuses each missing requirement;
   - pause and resume go through `glow_chat` (a send refused while paused);
   - resume rechecks completion;
   - each change emits its event.
10. **Photos (Stage B):**
    - a grant beyond the policy's limits is refused;
    - an upload moves only through quarantine, the seam and review;
    - approval writes `StaffAudit`, and only an approved variant's reference is returned;
    - reorder by another owner, and removal by another owner, fail;
    - removal withholds delivery at once and completes only on the purge acknowledgment;
    - a duplicate or out-of-order provider event changes nothing.
11. **Ownership:** every route refuses another member's object and an unauthenticated request, and answers a stale version with its version error.
12. **No secret and no coordinate in any output:** the job's secret check, and a log capture at `DEBUG`, find none.

**Every test with its reversal** (D15), recorded in the evidence record.

## Classification expectation

Full scope: code, migrations with data, a contract change, a workflow change and the proof. The manager classifies with `main`'s trusted policy, inspects the complete workflow diff and the job's actual steps, and requires full checks before the merge (`AGENTS.md`).

## Report format

Each stage's prompt asks for: branch, code head and records head; the environment check and start gate; for each Outcome item, the files, tests and reversals; the area file's hash and source; every command with its result line; the run of record (each job, the gate's line, the profile suite's counts, the phase's duration, whether a retry fired); what could not run; every deviation.

## Review plan

- **The manager verifies each stage's report** against the pushed branch: the complete diff within the owned paths, the seal, reversals re-run where useful, and the run of record's logs.
- **Then the PR,** Codex's review of its head, and **an exact-head code and security review of the final code head, with a written threat model.** Sensitive data and uploaded files are both security boundaries (DM-31 item 3's reasoning for SV1). Its focus:
  - each route's ownership and refusals;
  - the settings' fixed limits and audit;
  - the sensitive fields' consent and withdrawal;
  - what the location keeps and what it never keeps;
  - the birth input's privacy and the HDE boundary;
  - the media state machine, its seam and its provider events;
  - the seal;
  - the proof's secret handling.
- **Dev Manager:** this brief, before any prompt; each stage's design changes, if any; before the PR merges, at a named commit, the CI policy's paragraph and the data model's and contract's rewritten texts. The prompts need no read of their own: they authorize no credential and no live action.

## Sessions

- **Brief, revision 1** (10 November 2026): written after OD-60 and the matrix's recheck; to the Dev Manager as DM-52.
