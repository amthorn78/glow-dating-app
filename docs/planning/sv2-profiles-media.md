# SV2 — The profiles and media slice: the profile, its settings, consent and photos, proven on disposable PostgreSQL

- **Work ID:** SV2 (OD-49, N1 (a); PF01 §8, "Server slices"; the F02, F03, F04, F05 and F06 flows).
- **Status: brief, revision 6, 11 November 2026, by App Manager 10.** [DM-52](../continuity/dev-manager/reviews/2026-11-10-dm-52-sv2-brief.md) (answered at `093204a`, a read of `73c109b`) approved revision 1 with B1 to B55 in given words, folding in Nathan's answers in its session ([his words](../continuity/dev-manager/reviews/2026-11-10-nathan-answers-dm-52.md); OD-61). Revision 2 applied B1 to B55 as written, and made the two choices their words leave to the brief (D7's one date, D9's removed requirements), each marked as the manager's; D6's writer is DM-52's decision. It also placed D18 in Stage A (D1). [DM-53](../continuity/dev-manager/reviews/2026-11-10-dm-53-sv2-stage-a-paths.md) (answered at `f60cfda`, a read of `c2ee87a`) confirmed DM-52's conditions as applied and approved those choices. It gave W1 to W10 in given words: the generated contract outputs, the flow registry and the package's README owned (D11; Owned paths), `apps/mobile`'s check, and D8's resolution states. Revision 3 applied W1 to W10 as written. [DM-54](../continuity/dev-manager/reviews/2026-11-10-dm-54-sv2-stage-a-decisions.md) (answered at `1271ca5`, a read of `93a27ea`) ruled on Stage A's decisions as built and gave Y1 to Y12 in given words: completion as one shared recompute at the end of every requirement writer (D9), a birth input whose date fails the adult rule refused and not stored (D7, D8), restriction's and `requirements_met`'s registry entries, CI's mypy covering `glow_profiles`, the two added DTOs, and the two launch values to the third A05 message. Revision 4 applies Y1 to Y10 and Y12 as written; Y11 changes `data-model.md` through Stage A's correction C1. Applied as written, they need no read before C1's prompt; the Dev Manager's next consultation confirms them, and W1 to W10 (DM-54, section 2). [DM-55](../continuity/dev-manager/reviews/2026-11-10-dm-55-sv2-stage-a-review.md) (answered at `f165861`, a read of `496c39e`) confirmed W1 to W10, Y1 to Y12 and K1 to K5 as applied, ruled on Stage A's exact-head review, and gave Z1 to Z20 in given words: a future date as invalid input at both writers, and a date under 18 checked first at both (D7, D8, check 7); the history setting's limit (D2); the sensitive consent's current version at each save, and the withdrawal's rows set to "not stated" in place (D6); and `age_years` as D4's read (D4; Owned paths). Revision 5 applies Z1 to Z17 as written, with the section "Stage A, correction C2"; Z18 to Z20 change the carried-items file and the P11 plan. Applied as written, they need no read before C2's prompt; the Dev Manager's next consultation confirms them (DM-55, section 2). [DM-56](../continuity/dev-manager/reviews/2026-11-10-dm-56-sv2-stage-a-pre-merge.md) (answered at `d342f05`, a read of `e86b635`), the pre-merge read, confirmed Z1 to Z20 as applied and gave V1 to V5 in given words; revision 5 carries V3 in D7 (C2-1's order), and V1, V2, V4 and V5 change `data-model.md`, the evidence record and the carried-items file. **Revision 6** (11 November 2026), for Stage B after Stage A merged (PR43, `4dc2061`): photos use private R2 object storage ([OD-62](../continuity/owner-directions.md)), which reshapes D10's ports, its processing step and its removal; D19 decides the settings' pointer order (DM-56 V5); and "Stage B (revision 6)" lists Stage B's work. It goes to the Dev Manager (DM-57) before Stage B's prompt.
- **Owner:** Nathan Amthor, by the order he resumed on 26 October (OD-49): the server slices SV1 to SV4 after P06.3, before P10. **Manager:** App Manager 10. **Sessions:** one implementation session per stage (D1), each started by Nathan, in `Glow App - No Stream` (no Stream call, no provider, no credential).
- **Starting point:** `main` at `c864edd` (PR42, SV1), with the manager branch's Markdown records after it. Each prompt names the exact commit.
- **Evidence home:** `docs/testing/evidence/<date>-sv2-profiles-media.md`, written by the sessions.

## Why

- **PF01 §8, "Server slices":** *"Before P10, the production HTTP API, maintained authentication (django-allauth headless with the mail adapter) and the ORM persistence adapters of each domain are built as four slices: … SV2, profiles and media … Each is proven on a disposable PostgreSQL in CI under P06.DB's rules (no shared or production database, CI-generated credentials, the runtime guards kept). The runtime stays sealed until P11 wires it."*
- **PF01 §6, the data groups:** *"Profile, preferences, visibility | Separate private/public projections; reciprocal eligibility, completion and pause states; age and location disclosure boundaries"* and *"MediaAsset | Owner, storage reference, state, order and moderation decision; only approved variants eligible for public delivery"*.
- **PF01 §7, "Media":** *"Issue short-lived upload grants; enforce ownership, size/count/type limits and safe decoding. Strip metadata, quarantine originals, moderate before publication and expose only approved variants through authorized delivery. Handle abandoned uploads, reordering, retries, removal and downstream purge. Neither an uploaded filename nor a successful vendor upload proves that an image is safe or publicly eligible."*
- **PF01 §4, the Media row:** *"Cloudflare Images/private R2 as appropriate | Reuse upload/storage/delivery; build authorization, quarantine, moderation and lifecycle state"*; and §1: WordPress is *"the staff admin and support interfaces (OD-19). Its staff tools use only scoped Django APIs."*
- **Nathan, 11 November 2026** ([OD-62](../continuity/owner-directions.md)): *"Note that we will use R2 object storage for photos"*. Of PF01 §4's two ("Cloudflare Images/private R2 as appropriate"), photos use private R2 (D10).
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
6. **Visibility and completion** (F04, F06; D9): pause, resume and restriction through `glow_chat`'s reviewed writers, and completion and demotion through SV2's own, each taking the account row lock first, so the send check sees them.
7. **Photos** (F05; D10): upload grants, quarantine, G-02's seam, the automated check's approval and rejection and staff restriction on a report as domain operations, reorder, removal and purge, through provider ports with fixture adapters only.
8. **Glow's routes for the member** (D11): own profile, fields, preferences and filters, consent, birth input, visibility and photos, each validated against the contract, through SV1's actor.
9. **The proof** (D12): the profile cases (the acceptance checks below) on a disposable PostgreSQL in CI, through the HTTP endpoints with Django's test client, under P06.DB's rules.
10. **Sealed** (D13): the served runtime imports none of the new code, and its database backend stays Django's dummy one.
11. **The records:** the data model's profile, preferences, consent, age state, identity verification and media rows, rewritten as built; the contract's new DTOs; the P11 plan's partial evidence (DB04, DB07, DB08, DB10, PV04); the evidence record, with the threat model's inputs.

## Design

- **D1 — Scope, stages and seal.**
  - **Two stages in one item, each with its own session and verification** (recommended): **Stage A**, items 1 to 6 and their routes; **Stage B**, item 7 (photos) and its routes. **D18 lands in Stage A** (the manager, on DM-52's words): completion, item 6, requires identity verification or a staff approval, and D2's setting gates the approval. Each stage is reviewed and merged as P06.2's stages were: an exact-head code and security review of the stage's final code head, with its written threat model, then Codex's review, before that stage's PR merges. Stage B starts from `main` after Stage A merges. The alternative is one session for everything; its diff would be about twice SV1's, across two security boundaries (sensitive data and uploaded files).
  - **Sealed until P11,** as SV1 was: no deployed URL, no provider, no real member, no credential beyond what CI generates for one run. The mobile app is unchanged: its fixture adapters stay until P10 and P11 wire the client (PF01 §7).
  - **No staff HTTP route.** P07 builds the staff-scoped admin API and the WordPress views (PF01 P07). SV2 builds the domain operations they will call, each taking a staff subject and a reason and writing `StaffAudit`.
- **D2 — The settings store** (OD-60).
  - **The settings:**
    - the four lists: values with stable IDs and labels, which values are retired, and how many values a member may pick (gender 1, orientation 1, looking for any number, relationship status 1, at launch);
    - whether members may narrow by each field;
    - the age range's default and direction (both ways or the viewer's only);
    - the distance choices and their default, and which ways of locating are offered (both at launch: OD-60's table, "Both ways of locating offered");
    - resurfacing, the undo and rematch, each off at launch with its waiting period (SV3 reads them);
    - H's choice per cause, read-only for every cause at launch (SV4 reads it);
    - the media policy (D10);
    - whether staff may approve a member without identity verification (D18): off at launch; switching it off stops new approvals and leaves past ones until staff revoke them (Nathan, 10 November 2026: "I do need the ability to manually approve people without ID verification, and to toggle that feature on and off").
  - **The model:**
    - one append-only row per setting version (name, version, content, publication time, staff subject, reason);
    - content validated against a closed schema per setting before it is written;
    - `PolicyRevision` as the current pointer per name (the data model: "Policy pointer is transactionally locked alongside actions").
  - **The launch defaults** are seeded by a data migration as version 1 of each setting, with the staff subject `system:launch-default` and the reason "OD-60", or, for D18's setting, the register row that records Nathan's answers of 10 November 2026. Orientation's list launches with no values, and the distance choices with `anywhere` only, since OD-60 gives neither; both launch values go to Nathan in the third A05 message (DM-54).
  - **The fixed limits are code, not data.** OD-60's limits:
    - matching uses list values;
    - the age floor is 18;
    - never exact coordinates or an exact distance;
    - rematch never after a block or a report;
    - unmatch and block stay hidden;
    - a deletion works as an unmatch;
    - "show me" is never shown (OD-60's table, P1 display);
    - a member who states none in an optional field appears only to viewers who keep all of that field (OD-60, orientation; D3);
    - a change to H that makes more readable reaches a member only after they accept the consent wording that describes it (OD-60's table, H). The history setting names the onboarding consent version whose wording describes it: a publication that makes a cause more readable names the onboarding consent's current version, which must differ from the version the current setting names, and a publication that makes nothing more readable keeps the version the current setting names. Each more readable change therefore needs an onboarding version published since the one the setting names (DM-55);
    - no list holds more than 50 live values, the contract's bound on one "show me" set (`PreferenceSelection.accepted_option_ids`);
    - a staff approval without identity verification stands in for that one requirement only, never for the adult check, consent or any other (D18);
    - the media policy stays within its ceilings (D10).

    A publication that crosses one is refused before anything is written.
  - **A change applies from then on** and emits `policy_published` in the outbox for SV3's invalidation. A retired list value stays valid for members who hold it, and their data stays matchable. It is not offered for new choices, and the member is asked to choose again at their next edit.
  - **Decided (DM-52):** a retired value stays matchable, as above, so retiring a value never hides the members who hold it; the media policy is in this store, within ceilings in code (D10).
- **D3 — The four list fields and the display choices** (OD-60, P1).
  - **Own values:**
    - one row per account and field, holding the selected value IDs and the setting version they were chosen under;
    - indexed for SV3's queries;
    - a reserved "not stated" value for orientation and for relationship status, the two fields a member may leave unset (D9; the sensitive-fields consent is never required, D6). It is in every "show me" set that keeps all, and in no narrowed set. Gender and "looking for" are completion requirements (D9), so neither needs it.
  - **"Show me" sets** are policy-versioned, with `Preferences.policy_version` as their policy, and keep the wire shape `PreferenceSelection` already has (dimension, accepted option IDs) in `PreferencesIntent` and `OwnPreferences`. Each starts at all.
    - **"All" is its own marker,** never the list of current values: it includes values the console adds later and the reserved "not stated" value, so the console never narrows a member's set. Narrowing replaces it with an explicit list of live values, and the contract's text says how the marker is written in `accepted_option_ids` (D11).
    - **Narrowing the orientation or relationship status set** needs the sensitive-fields consent (D6).
    - **Stored so SV3 can query them:** SV3 tests both directions for every candidate in one SQL query, so the sets are stored as rows (account, field, value, with the "all" marker as its own row), indexed, rather than in `Preferences.values`'s JSON list of objects. If the brief keeps the JSON, it names the index SV3 will use.
  - **The two-way rule,** which SV3 applies, is defined here, so SV2's records hold what it needs: a field matches when at least one of each person's values is in the other's set, for every field.
  - **Own words:** bounded text for gender and orientation (proposed: 40 code points), display only; never matched, searched or used by ranking. Moderating free text is P07's. Orientation's own words are sensitive: saved only with the sensitive-fields consent, and removed with its withdrawal (D6).
  - **Display choices:** one flag each for gender, orientation and relationship status, off until the member turns it on; "looking for" is shown; "show me" is never shown. The candidate projection that reads these flags is SV3's.
- **D4 — The age range** (OD-60, P2): the member's minimum and optional maximum, never below 18, defaulting to the setting's default. The direction is the setting's. SV3 applies it, reading each member's age from the age state's date (D7) through the age port's `age_years`, which returns whole years, never the date (DM-55).
- **D5 — The location** (OD-60, P2; the recheck record).
  - **The area table:** reference data with stable area IDs, a name and an internal point. **Recommended source:** the US Census Bureau's 2024 Gazetteer file for core-based statistical areas (metro and micro areas, fewer than 1,000), public domain, pinned by SHA-256 and loaded by a data migration. It was reachable from this environment on 10 November 2026: 46,177 bytes, last modified 30 August 2024. **The alternative,** the Gazetteer's places file (cities and towns, about 32,000; 1,221,402 bytes), is finer, so it reveals more and makes tiny groups likelier.
    - **Chosen (DM-52): the core-based statistical areas.** As read on 10 November 2026: the zip's SHA-256 is `0ec21c5d83982467903f1500fbbae87311edc81f09bed8ec1bbded80bce7eec3`; its one file, `2024_Gaz_cbsa_national.txt`, is 188,130 bytes, SHA-256 `31b285827a72b9f7917b312d458d01e2efe2909e4c5cb7b4b760b6bb0725f787`, tab-separated, with 935 areas (393 metro, 542 micro), each with `GEOID`, `NAME` and an internal point (`INTPTLAT`, `INTPTLONG`).
    - **Puerto Rico:** 10 of the 935 areas are in Puerto Rico. OD-55's launch is "the US, all states", so the table holds the other 925. Adding Puerto Rico is a launch-geography decision for Nathan.
    - **Coverage:** a county in no metro or micro area is in no area. A member there picks the nearest area, or the phone's location maps to the nearest internal point, which can be far away. The step says so in plain words.
    - **Size:** one area can be very large (Riverside-San Bernardino-Ontario, CA has 27,277 square miles of land), and two members in one area are at distance zero. So a distance choice means "areas whose internal points are within this distance", and the console's choices and the app's words describe that, not a distance between people.
    - **States:** 59 areas span two or more states, so an area does not give a member's state. Nothing that needs a member's state (G-04's state notices) reads it from the area (carried to P07).
    - **The committed file** is the table derived from the pinned text file (area ID, name, internal point) by a recorded, deterministic step. The evidence records both source hashes and the derived file's own; a test checks the derived file's hash and its 925 rows. Nothing is fetched at migration, test or run time.
  - **The member chooses an area, or sends the phone's approximate location once.** The server maps it to the nearest area's internal point and keeps only the area ID. **The phone's location is a query:** the server returns the nearest area and changes nothing, and the member then sets that area, or another, by its ID. The coordinates are never stored, logged, returned or put in the outbox, and a test asserts each of the four. They also travel only in the request body, never in a URL, a query string or a header, and they never appear in an error response or a validation message (a refusal names the field, not its value), an exception's text, a log line at any level, or an idempotency record (the query writes none). A test asserts each.
  - **The distance limit** is one of the setting's choices, measured between area internal points. No distance is ever returned. SV3 applies the filter and tests repeated filter changes and tiny groups (DM-51 M9).
  - **`Profile.location_label`,** the existing text label, is replaced by the area ID; its display text comes from the area's name.
  - **Decided (DM-52):** the source above, and the internal point as published: every member in an area shares it, so it tells no one more than the area does, and a coarser cell would add nothing.
- **D6 — Consent** (F02; G-10).
  - **Onboarding consent:** F02's accept and withdraw for purpose `onboarding`, through `glow_chat`'s `accept_consent` and `withdraw_consent`. Those operations join the lock protocol (DM-13 4.1), so the send check reads them current. **The version check is SV2's:** `accept_consent` does not compare the version with the current policy, so SV2's operation, in one transaction, takes the account row lock first, reads the consent policy's current version under its pointer's lock, refuses any other version (F02: "old consent version rejected"), and only then calls `accept_consent`, whose own transaction nests as a savepoint. Any result other than `applied` or `no_change` rolls the whole transaction back.
  - **The sensitive-fields consent:** purpose `sensitive_profile`, required before orientation or relationship status is saved, before orientation's own words are saved, and before either field's "show me" set is narrowed. Each of those saves needs the consent accepted at its current version, read under its policy pointer's lock with the save's other settings, after the account row lock and in name order (the settings store's rule; F02: "old consent version rejected"). A value, own words or a narrowed set saved under an earlier version stays until the member's next such save or a withdrawal; what a new version asks of them is P08's (DM-55). Withdrawal, in one transaction, sets each of the member's orientation and relationship status rows to "not stated" in place, with no own words, its display flag off and its setting version unchanged, bumping the row's version and emitting `profile_field_changed` for it, so that earlier events still name an existing record; a row that already holds "not stated" with no own words and its flag off is left as it is, with no event (DM-55). It also resets those two "show me" sets to all, and deletes the member's idempotency records of the commands that carried any of them (D17). The member then appears as "not stated" in both fields, only to viewers who keep all of each (OD-60; D3), so declining or withdrawing never hides a member from viewers who keep all. **Every reader of consent filters by purpose,** as every reader does today (`glow_chat`'s send and match checks; the ordering proof's reads), so a `sensitive_profile` decision never satisfies or revokes onboarding consent; a test asserts both directions.
    - **Its own writer.** `glow_chat`'s `_decide_consent` writes purpose `onboarding` only (`chat.ONBOARDING_CONSENT_PURPOSE`), so this consent needs a writer in SV2.
    - **Recommended:** a writer that takes the account row lock first in the canonical order (P06.DB 5.3; DM-13 4.1), appends the decision, and changes the field values in the same transaction. The alternative, widening `glow_chat`'s writer to take a purpose, changes a reviewed module that SV2 otherwise leaves alone.
    - **Decided (DM-52):** SV2's own writer, as recommended, with the version check, purpose filtering and scope above.
  - **The wording** is a versioned policy whose text is not SV2's: development text, labelled as such, until P08 writes it with H's readable rule (DM-51 M15). A version change that makes more readable asks the member to accept again (OD-60, H). The development text already says the two facts P08's text must: a gender with a "show me" set can reveal orientation (onboarding consent; the second A05 message, P1), and a viewer who narrows a field learns it for everyone they are shown (the sensitive-fields consent; OD-60's follow-up).
- **D7 — The adult check and the age state** (F02; G-01; SV1's D9; DM-52).
  - **The order is P04's:** the member gives the date at the eligibility step, before any birth input exists (`/birth` needs the adult pass and current consent). The birth input cannot hold it: its contract shape needs a place the member has not given yet.
  - **The date's home is the age state:** a `birth_date` column on `AccountAgeState`, present with `self_declared_adult` and absent with `unknown` (a check constraint), written only through `AgeAssurancePort`. SV3 reads the age from it (D4) and never reads the birth input.
  - **The writer:** `OrmAgeAssurance.record` refuses an existing row by design (its docstring: the slice that sets a state writes the change), so SV2 adds one transition to the port and its adapter (the owned paths). In the caller's transaction, after the account row lock (DM-13 4.1), it changes `unknown` to `self_declared_adult` with the date and the policy version, or back to `unknown`, refuses any other change, and bumps the account's `eligibility_version`. `record`, sign-up and the actor stay as SV1 built them, and SV1's identity suite stays green.
  - **The check:** with the date valid, not in the future and 18 or over at the server's clock (`clock_timestamp()` after the locks), the state becomes `self_declared_adult`. An impossible date, a future date and a date under 18 are each refused and not stored, and the state stays `unknown`; what Glow does beyond that about a suspected minor is G-01's.
  - **One date (P04's rule):** a birth input saved with another date changes the age state's date in the same transaction. A new date at the eligibility step, while a current birth input holds another, is either refused or makes that birth input stop being current, with re-entry asked for and its mapping back to pending, as P04's fixture does; the brief says which. **Which (the manager, on DM-52's words):** the second, as P04's fixture does; the new date is checked, the birth input stops being current, its mapping returns to `pending`, and the member is asked to enter the birth input again. The birth input's writers take the account row lock first (D8).
  - **Every date change reruns the check.** A failing rerun sets `unknown`, clears the date, and moves a `visible` profile to `incomplete` in the same transaction (D9), since the send check reads the profile's state and consent, not the age. A `paused` profile stays paused, and resume rechecks completion.
  - **A future date, and a date that fails the adult rule (DM-54; DM-55).** A date fails the adult rule when it is under 18 at the server's clock. A date in the future does not fail it: like an impossible date, it is invalid input, declares no age and never reruns the check (P04's rule: `setAdultDate` refuses both and changes nothing).
    - **For an account whose state is `self_declared_adult`,** both writers, the eligibility step and the birth input, check the date first, after the idempotency check (a replay or a key conflict) and before any other refusal (a stale version, a birth time not given, a lapsed onboarding consent). A future date is refused `invalid_request` and changes nothing. A failing date is refused `forbidden`, nothing of it is stored and no idempotency record is kept, but the transaction still commits the failing rerun: the age state becomes `unknown` with no date, the current birth input stops being current (`missing`, its mapping back to `pending`), and a `visible` profile becomes `incomplete`. The operation returns the refusal without raising, so the transaction commits. A retry is refused, since the account is no longer an adult's, and changes nothing more.
    - **For an account whose state is `unknown`,** the eligibility step also checks the date first, after the idempotency check (C2-1; DM-56): it refuses a future date (`invalid_request`) or a failing one (`forbidden`) and changes nothing, so a retry of a refused command answers as the command did. The birth input is refused at its adult-check gate.
    - Nothing of a refused date is stored on either path. Earlier birth input revisions keep their contents, readable only by their owner and never current again; whether a failing rerun erases them is G-01's, in P07 (DM-55). P04's `saveBirth` saved the input; the server does not.
- **D8 — The private birth input** (F03).
  - The owner's `submit`, `correct` and `change` transitions on `BirthInput` revisions, stored as private input with its provenance and uncertainty. A birth time is required (Nathan, 10 November 2026: "birth time is required at signup"): a birth input with `time_precision` `unknown` is refused, and an approximate time keeps its entered value. The contract's `BirthInput` still allows `unknown`, so this is a server rule, and the contract's text says so for F03; nothing guesses a time. A revision whose date is in the future is refused as invalid input and changes nothing; one whose date fails the adult rule is refused and not stored, while the failing rerun commits (D7; DM-54; DM-55).
  - SV2 creates no `EngineIdentity` row and resolves none, and no transition the HDE would decide (`resolve`, `ambiguous`, `unsupported`, `outage`) is built. No HDE call, and no engine identifier is invented (the protected boundary; A01). **The chart in completion's tests:** no SV2 code writes a resolved mapping. To prove completion's success path, a test may seed a resolved `EngineIdentity` in its own setup, through the ORM in the disposable database, with `engine_reference`, `engine_version`, `contract_version` and `adapter_version` each beginning `fixture:`, so it can never pass for an engine result. A new birth input revision returns the mapping to `pending` in the same transaction (F03: "changed input invalidates old mapping"), and a visible profile then follows D9's rule for a removed requirement.
  - **The two resolution states (DM-53):**
    - `BirthInput.state` is the revision's resolution, returned as `OwnBirthInput.resolution`; `EngineIdentity.state` is the mapping's. A new revision starts `pending`.
    - SV2 creates no `EngineIdentity` row, so `mapping_version` stays null, and no SV2 code writes a resolved state or an adapter version. A new revision returns an existing mapping (in SV2, only a test's seed) to `pending`, clears its engine reference and versions, keeps its `adapter_version`, and points it at the new revision.
    - "Its chart resolved" (D9) means both states are `resolved` and the mapping points at the current revision. A test's seed sets both, with the `fixture:` values above on the mapping.
    - A new eligibility date (D7) sets the current revision's state to `missing` and returns any mapping to `pending`. The owner's read then returns that revision with `resolution: missing`, completion reads it as no birth input, and only the owner's next `submit` moves it on, by writing a new revision.
- **D9 — Visibility and completion** (F04, F06).
  - **Completion** (`incomplete` → `visible`) requires:
    - onboarding consent accepted;
    - the adult check passed;
    - a display name and a non-empty summary;
    - a gender, and at least one "looking for" value (OD-60's table: "A member picks one or more");
    - an area;
    - at least one approved photo (Stage B adds it), approved by the automated check (D10). P04.2's reviewed rule already requires current approved media, so this is not a new decision.

    The sensitive fields are not required. **Two more requirements, from Nathan's answers of 10 November 2026** ("the human design chart is calculated immediately when someone signs up, there is no lag - there is no manual staff review either. Approval must be automated based on ID verification"; "I do need the ability to manually approve people without ID verification"):
    - a current birth input with its chart resolved (P04.2's reviewed rule). The chart is calculated as soon as the birth input is given; if the engine cannot resolve it (it is down, or the birth data is ambiguous or unsupported), the profile waits until it can. SV2 has no HDE, so in the sealed runtime nothing resolves (D8);
    - identity verification passed, by an automated check with no staff step, or a staff approval without it while D2's setting allows one (D18).

    No staff review stands between a complete profile and `visible`: P04.2's "Profile review" requirement is dropped by his answer.
  - **Pause and resume** go through `glow_chat`'s `pause_profile` and `resume_profile`, and restriction through `restrict_profile`, so the send check and its race cases (P06.2 D5, 6.1) see them; SV2 adds no second pause, resume or restriction writer. **Completion and demotion are SV2's own writers** of the state the send check reads (`glow_chat` has no writer to or from `incomplete`): each takes the account row lock first, then the profile `FOR UPDATE`, bumps `eligibility_version` and emits its event, in one transaction (DM-13 4.1).
  - **Resume rechecks completion first.** `resume_profile` moves `paused` to `visible` with no completion check of its own, so SV2's resume refuses an incomplete profile before calling it.
  - **One transaction (DM-52):** SV2's operation opens the transaction, takes the account row lock first, checks completion on rows read after the lock, and then calls `resume_profile`, whose own transaction nests as a savepoint and takes the same lock again. Any result other than `applied` or `no_change` rolls the whole transaction back. Every writer of a completion requirement, Stage B's photo writers included, takes the account row lock first, so a check and a withdrawal cannot interleave. A writer that would remove a requirement from a `visible` profile either refuses or moves the profile to `incomplete` in the same transaction, as the contract already says for a cleared summary ("Compound actions and model projections"); the brief says which for each requirement. **Which (the manager, on DM-52's words):** a removal the member or staff is entitled to make moves the profile to `incomplete` in the same transaction, and is never refused: a consent withdrawal, a cleared summary, the removal or a staff restriction of the last approved photo, a new birth input revision, a failing adult rerun, and a revoked staff approval. An edit that would leave a required value empty (the display name, the gender, "looking for", the area) is refused, since each is replaced, never cleared. A `paused` profile stays paused (P04.2's table: "F04 paused edit | Remains paused"), and resume rechecks it. Messaging stopped by an incomplete profile is not one of OD-60's H causes, so the carried-items file carries it to SV4.
  - **What moves a profile to `visible` (DM-54).** Every writer of a completion requirement ends, in its own transaction and on rows read after the account row lock, with one shared recompute: an `incomplete` profile with nothing missing becomes `visible`, and a `visible` profile with anything missing becomes `incomplete`; `paused`, `restricted` and `removed` stay as they are. The writers are:
    - the owner's: the profile edit, the four fields, the area, the onboarding consent's accept and withdraw, the adult check and the birth input;
    - staff's: approval without ID verification and its revocation;
    - after Stage A: P11's chart adapter when it resolves a mapping, P11's verification adapter when it records `verified`, and Stage B's automated photo check when it approves.

    So a profile shows as soon as its last requirement is met, whoever meets it (OD-61: "the human design chart is calculated immediately when someone signs up, there is no lag"; "Approval must be automated based on ID verification"). A requirement that lapses without a write, such as a new onboarding consent version, demotes at the member's next requirement write. The member can pause at any time (F06).
  - **Each change emits** the outbox event SV3's invalidation reads.
- **D10 — Photos** (F05; G-02; Stage B).
  - **Private R2 object storage (OD-62), behind ports with fixture adapters only.** Photos are objects in private Cloudflare R2 storage, not Cloudflare Images. SV2 makes no R2 call, holds no credential and adds no SDK; P11 builds the R2 adapter and PV04's proof. Two ports:
    - **the storage port:** it issues the upload credential for a grant, reports an upload's completion, writes a processed variant, deletes an asset's objects, and gives P11's delivery its reference. Its events reach the domain only through the port, whose contract requires the adapter to authenticate each event before the domain sees it (P11's adapter does it); no member route can deliver one;
    - **the processing port:** the system review step's processing (below), which makes the variant Glow delivers from the uploaded original.
  - **Object keys** are Glow's own, random and opaque: no account, profile or asset ID, no filename and no member value is in a key, since keys show in the store's logs and in the URLs P11 issues. The original and each variant have their own keys. No bucket has public access in any form R2 offers; P11 configures and proves that (PV04).
  - **The upload grant:** short-lived, opaque and one-use, within the media policy's limits. The policy's version 1 holds `development-media-1`'s values: PNG only, 1 MiB, 2,048 × 2,048, four live photos, a 60-second grant, three attempts. The launch values are A05's ("media limits"), and they go to Nathan with the third A05 message. The policy is a setting in D2's store, and its ceilings are code: a publication above them is refused. They are `development-media-1`'s types, bytes and pixels (PNG only, 1 MiB, 4,194,304 declared pixels) until PV04 proves a real decode path's limits, and the contract's 20 collection entries. The store's upload credential (in P11, a time-limited signed upload address for the grant's key) expires with the grant, and the domain does not rely on it being one-use: it adopts only the first completion that matches the grant's key and the policy's byte limit, and a later completion for that key changes nothing (check 10).
  - **The quarantine path:** `upload_pending` → `quarantined` (only on the provider's upload completion) → `review_pending` (only by the system review), with **G-02's seam** between `quarantined` and `review_pending`: a port for a detection step. SV2 configures none and records "no detector". The step's outcome can send an asset to review, to a hold, or to a hold with a report; SV2 builds only the route to review. The seam keeps a place for report evidence and a hold, and builds neither, but every path SV2 builds that a hold must stop asks the hold port first, and SV2's fixture answers "no hold": approval, delivery, and a removed asset's purge (a CyberTipline report asks for one year's preservation, USF-04; G-05's hold survives deletion). A hold will be its own record, not a new `MediaLifecycle` state, so the closed DTO stays unchanged; an owner's removal of a held asset still withholds delivery at once, and only the purge waits.
  - **The system review step is Glow's own processing** (OD-62: object storage keeps the bytes it is given). It reads the adopted original, checked against the completion's size and entity tag, decodes it within the policy's bounds, removes its metadata, re-encodes it and writes the variant under a new key, before the detection seam and the automated check see it. The original is never delivered. SV2's processing port has a fixture adapter, as P04.3's fixture simulates processing (`private-media-fixtures.md`). P11 builds the processor and its proof (PV04), and decides where it runs: a Glow worker, or a Cloudflare service reading from R2, whose cost goes to Nathan first (OD-50). How long an original is kept after its variant is approved or rejected is retention, for the third A05 message with G-05's hold; until then the fixture keeps it, and removal deletes it with the variants.
  - **Moderator decisions** (`approve`, `reject`, restriction) are domain operations that take their decider and a reason and write `StaffAudit`. **Approval and rejection are an automated check's decisions** (Nathan, 10 November 2026: no manual staff review, photos included), recorded with a `system:` subject, as D2's seed is. SV2 builds the check as a port with no vendor: its fixture adapter approves nothing in the runtime, and a test drives it in its own setup. **Staff act only on reports:** a restriction, which P07 exposes. The check never clears a staff restriction; only the staff decision that closes the report does. An owner's removal and a moderation restriction keep separate revocation records, so a later approval clears only the restriction and never undoes an owner's removal (`private-media-fixtures.md`, "F05 and revocation").
  - **Reorder** uses collision-safe temporary positions inside one unit of work (the data model's note). **Remove** withholds delivery at once, moves to `removal_pending`, and becomes `removed` only on the storage adapter's acknowledgment that every object of the asset, the original and each variant, is deleted (in P11, with any cache its delivery uses).
  - **Delivery** returns only an approved variant's reference; short-lived authorized delivery over the private bucket is P11's, never a public address.
- **D11 — The contract: additive DTOs** (recommended). New DTOs in the v1 production schema; every existing DTO is unchanged, so no mobile source, test or fixture changes until P10. The generated contract outputs in `apps/mobile/src/contracts/generated/` gain the new DTOs' types and validators: `gapp-api-v1.ts`, `validators.js` and `validators.d.ts` change, and `gapp-dev-v1.ts` does not. Only `npm run generate --prefix packages/contracts` writes them, never a hand edit, as for P04.3's and C1's DTOs. Ajv numbers its compiled schemas in order, so new DTOs can renumber much of `validators.js`; a review checks the outputs by regenerating them, not by reading their diff. CI's Mobile checks job compares them byte for byte, and the shared corpus runs through them:
  - the member's own field values and display choices, with their reads;
  - the age range and the area, with their reads, and the phone-location query, whose coordinates are bounded and never echoed, and whose response is the nearest area (D5);
  - the adult check's intent (`AdultCheckIntent`) and the owner's age state read (`OwnAgeState`, with the owner's own date), for D7's eligibility step, which comes before any birth input (DM-54);
  - the current catalog: the lists, which may be narrowed, and the defaults, read-only for the member;
  - the owner's completion read: the missing requirements, from a closed list of its own (consent, the adult check, the profile's fields, the area, a photo, the chart, identity verification), for the owner only, since P04.2's rule keeps missing requirements visible to the owner. Identity verification gets its own value, not `verify_identity`, which `OnboardingEligibility` uses for email verification;
  - the sensitive-fields consent: a new intent with its own `operation`, and a new response for its read. `ConsentIntent` has no purpose field (its fields are `operation`, `meta`, `policy_version` and `decision`), and adding one would change an existing closed payload, which needs a negotiated contract version ("All additions to a closed payload need a new negotiated contract version").

  `PreferencesIntent` keeps carrying the "show me" sets. The shared corpus gains each new DTO's cases, and the production catalog's paths map stays empty until P11 serves the routes. **The alternatives:** change the existing DTOs and the mobile fixtures with them; or a new schema version. **Decided (DM-52): additive,** as P04.3's `MediaCollection` and C1's responses were: the new DTOs join `AppIntent` and `AppResponse` as an unpublished design catalog, older validators reject the new discriminators, and a deployed transport negotiates support before returning them (`production-contracts.md` says so for these DTOs).

  **The flow registry** (`flows-v1.json`; DM-53). Each new DTO joins its flow's `request_contracts`, `response_contracts` and `projection_roles` (`owner`), and each transition SV2's writers make that the registry lacks is a new entry. Every entry uses a role the oracle authorizes (`transition_contract.py`, `authorized`): staff act as `moderator`, as F01's `suspend` and F05's `restrict_media` do. No existing entry changes, and each new entry has an allowed and a forbidden example in `tests/test_transition_contract.py`. The entries:
  - **F02:**
    - the sensitive-fields consent's intent and read, with events of its own, so that no rule repeats the onboarding consent's and an optional consent never starts as `required`: `accept_sensitive` from `not_given` and from `withdrawn` to `accepted` (`owner`; `consent_current`), and `withdraw_sensitive` from `accepted` to `withdrawn` (`owner`);
    - the age state (D7): `adult_check` from `unknown` to `self_declared_adult`, and from `self_declared_adult` to itself for a passing correction (`owner`; `A05`), and `adult_check_failed` from `self_declared_adult` to `unknown` (`owner`);
    - identity verification (D18), with events no one can read as F01's email verification: `id_check_passed` from `unverified` or `staff_approved` to `verified` (`provider`, since the company's verdict arrives through the port, as F05's provider events do), `approve_without_id` from `unverified` to `staff_approved` (`moderator`; `A05`, `staff_approval`), and `revoke_approval` from `staff_approved` to `unverified` (`moderator`; `A05`).
  - **F03:** `date_changed` from `pending`, `ambiguous`, `resolved`, `unavailable` and `unsupported` to `missing` (`owner`; D7's choice), one entry each.
  - **F04:**
    - the fields with the display choices, the age range, the area, the phone-location query and its response, the catalog, and the owner's completion read;
    - `requirement_removed` from `visible` to `incomplete` (`system`). It is the demotion that follows another write, as `deletion_requested` follows F18's request: a consent withdrawal, a failing adult rerun, a new birth input revision, a revoked staff approval, and, in Stage B, the removal or restriction of the last approved photo. The cause keeps its own entry, with its actor's role, in its own flow. The owner's own edit that clears the summary keeps the existing owner `edit` from `visible` to `incomplete`.
    - `requirements_met` from `incomplete` to `visible` (`system`; `eligible`; `A05`): the completion that follows a write in another flow (D9's recompute; DM-54), as `requirement_removed` is the demotion that follows one. A completion in an F04 owner command keeps `complete` (`owner`).
    - `restrict` from `visible` and from `paused` to `restricted` (`moderator`; `A05`): SV2's staff operation, through `glow_chat`'s writer, a move the registry has lacked since P06.2 (DM-54).
  - **F05 is Stage B's:** `approve` and `reject` from `review_pending` become the automated check's (`system`; OD-61), so the `moderator` entries go and `test_f05_quarantine_cannot_be_published_by_uploader` changes with them. These are changes to existing entries, which Stage B's prompt owns; `restrict_media` stays `moderator`.
  - **`staff_approval`,** D2's setting being on, is a new trusted test prerequisite, added to `production-contracts.md`'s list.
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
  - **Stored idempotency digests reveal nothing.** The contract binds each command's whole intent by a digest stored in `IdempotencyRecord.request_digest`, and the proof's reference digest is an unkeyed SHA-256. An unkeyed digest of a short value (an orientation, a set of list values, a birth date and time) can be reversed by trying every value. So every SV2 command's stored digest is keyed: `django.utils.crypto.salted_hmac(<a salt naming the purpose>, <the canonical intent>, algorithm="sha256").hexdigest()`, 64 characters, which uses the run's generated `SECRET_KEY` and needs no new secret (`salted_hmac`'s default algorithm is SHA-1, so the algorithm is named). The sensitive-fields consent's withdrawal also deletes the records that carried the two fields or their sets (D6). A test shows a stored digest cannot be reproduced from its command without the key.

- **D18 — Identity verification, and staff approval without it** (Nathan, 10 November 2026: "Approval must be automated based on ID verification"; ID verification is a government photo ID, checked by a verification company with a selfie matched to it, for every member before their profile shows; "I do need the ability to manually approve people without ID verification, and to toggle that feature on and off").
  - **One account-private record:** the identity verification state, which is `unverified`, `verified` when the automated check passes, or `staff_approved` when staff approve the member without it. It holds the method, the company's opaque reference or the staff subject and reason, and the time, and it is written only through a port, after the account row lock (DM-13 4.1), with the eligibility bump. Glow keeps no ID image, ID number or selfie. It is not the contract's `verify_identity`, which means email verification.
  - **The automated check:** SV2 builds the seam and no provider. Its fixture adapter never writes `verified` in the runtime, and a test may seed `verified` in its own setup, as D8's mapping is seeded.
  - **Staff approval without ID verification:** a staff operation with a staff subject and a reason, written to `StaffAudit`, available only while D2's setting allows it (off at launch), which it reads under the pointer's lock in its own transaction. It stands in for identity verification only, never for the adult check, consent or any other requirement (D2's fixed limits). Switching the setting off stops new approvals and leaves past ones; staff can revoke one at any time, back to `unverified`, and a visible profile then follows D9's rule for a removed requirement. No member route reaches either operation; P07's console exposes them.
  - **Completion requires `verified` or `staff_approved`** (D9).
  - **The rest comes with Nathan's decision, after the matrix's recheck:** the verification company, its cost (an M07 line he approves first, OD-50), the consent (a selfie matched to an ID is face geometry, UST-51), what the company keeps and for how long, what a member can do when the check fails, and whether the ID's birth date replaces the self-entered one as the adult check (D7; OD-55's D3).
- **D19 — One pointer order in every transaction** (revision 6; DM-56 V5, its recommended option).
  - **The rule.** Every transaction that locks settings pointers takes all of them in its first `read_shared` call, in name order. A publication takes its own pointer `FOR UPDATE` and then any pointer it reads, which today sorts after it (`chat.history`, then `consent.onboarding`). A pointer read again later in the same transaction is already held, and waits for nothing.
  - **What changes in Stage A's code.** Four transactions read a pointer after one whose name sorts later (DM-56 section 6):
    - `set_field` adds `consent.onboarding` to its first call, for its recompute;
    - `set_area` takes `consent.onboarding` with `profile.location`, for its recompute;
    - staff's approval without identity verification takes `consent.onboarding` with `identity.staff_approval`, for its recompute;
    - the owner's catalog read takes the seven `profile.*` pointers and both consents in one call.

    Every other transaction already follows the rule. Stage B's photo writers follow it: a writer that recomputes takes `consent.onboarding` with the media policy's pointer.
  - **The check.** `settings_store` records each transaction's held pointers. A lock on a pointer that sorts before one already held, and is not itself held, raises an internal error, a programming error and never a member's refusal, and the transaction rolls back. Every profile-suite case runs under it. An offline test shows the refusal, a static test shows that nothing outside `settings_store` locks a `PolicyRevision` row, and a reversal (one writer's added pointer dropped) fails its suite case.
  - **Why.** Members take their account row first and then pointers in this order; publications take pointers only, in this order, and never an account row. With one order for every pointer lock, no wait cycle can form whatever PostgreSQL's queueing does, so the no-deadlock claim rests on the documented conflict table, not on implementation behaviour (DM-56 V4). V5's fallback, a suite case of the four-transaction cycle, is then not needed.
  - **The alternative:** keep the order, record the claim as it stands, and add that suite case.

## Owned paths (the sessions)

- `services/api/glow_profiles/**` (new): the app, its views, URL configuration, settings store, the area table loader, the media ports' fixture adapters and the domain operations.
- `services/api/glow_domain/`: new modules for the profile fields, the settings' schemas and fixed limits, the media storage and processing ports (D10), the photo check's port and the identity verification port (D10, D18); and in `identity.py`, the age section only, for D7's date and transition and D4's `age_years` (DM-55).
- `services/api/glow_identity/age.py`: D7's transition and D4's `age_years` only; `record` is unchanged (DM-55).
- `services/api/glow_persistence/models.py` and new migrations after `0004` (the settings, the field values, the area table and its data, consent's new purpose, the age state's date, the identity verification record, the media grant): only what D2 to D10 and D18 need.
- `services/api/tests/`: new profile, settings, media and sealed-runtime tests; `test_model_definitions.py` where the new models require.
- `services/api/pyproject.toml`: `[tool.mypy]`'s `files` only, which gains `glow_profiles` (DM-54).
- `packages/contracts/production/gapp-api-v1.schema.json`, `openapi.json` (DTOs only, no paths), `corpus/shared-v1.json` and the contract tests: D11's additions only.
- `packages/contracts/production/flows-v1.json`: D11's DTOs, each in its flow's `request_contracts`, `response_contracts` and `projection_roles` (`owner`), as F05's `MediaCollection` and F11's C1 DTOs are. Also the transitions SV2's writers make that the registry lacks, each as a new entry (D11's list). No existing entry changes, except F05's `approve` and `reject` in Stage B (D11).
- `packages/contracts/README.md`: a section for SV2's additions, as P06.2 C1 has.
- `apps/mobile/src/contracts/generated/**`, only as `npm run generate --prefix packages/contracts` writes it. If a mobile source, test or fixture would have to change for the Mobile checks job to pass, the session stops.
- `proofs/postgres-ordering/**`: the profile suite, its settings, tests and locks; `identity_support.py` only as D16 says.
- `.github/workflows/foundation.yml`: the Database proof checks job's steps only.
- `docs/architecture/data-model.md` (the rows named in Outcome item 11, and the sentence of "Identity, time and field semantics" that DM-54 gives), `docs/architecture/production-contracts.md` (F02 to F06's index rows, kept in step with the registry by hand, and their server mapping; the oracle's list of trusted test prerequisites), `docs/architecture/profiles-preferences-fixtures.md` and `private-media-fixtures.md` (a note that the server exists, sealed), `docs/testing/p11-deferred-acceptance.md` (the partial evidence), and the evidence record.

## Manager-owned

- This brief, the carried-items file, the handoff, the review log and Notion.
- **The CI policy's Database proof checks paragraph** (governing Markdown): the manager updates it in each stage, and the Dev Manager reads it at a named commit before that stage's PR merges.

## Exclusions

- `services/api/glow_api/**`: the runtime stays sealed.
- `services/api/glow_chat/**`: SV2 calls its reviewed writers unchanged.
- `services/api/glow_identity/**`, except D7's transition and D4's `age_years` in `age.py` (DM-55): SV2 uses its actor class unchanged.
- `apps/**`, except the generated contract outputs (Owned paths), `wordpress/**`, `proofs/stream-chat/**`, `scripts/**`, other workflow jobs, the `Dockerfile`, every environment template, `requirements.in` and `requirements.lock`.
- Any provider (R2 or another Cloudflare service, an HDE adapter, a detection or moderation vendor), any provider credential or SDK, any staff HTTP route, any device location permission in the app, any real member or photo.

## Dependencies and inputs

- `main` at `c864edd`; PF01 1.17 §1, §4, §6, §7 and §8; F02 to F06 and their DTOs; the data model; the contract; the P11 plan's DB04, DB07, DB08, DB10 and PV04; SV1's brief and record (the actor class, the age port, the proof's identity suite); `glow_chat`'s writers; OD-12, OD-49, OD-55, OD-60, OD-61 and OD-62; the matrix's G-02 and G-10, and the OD-60 recheck record; the media provider mapping and the fixtures it maps.
- **The Census Bureau's Gazetteer files,** checked on 10 November 2026: `2024_Gaz_cbsa_national.zip` (46,177 bytes) and `2024_Gaz_place_national.zip` (1,221,402 bytes), each answering `200`, last modified 30 August 2024.

## Acceptance checks

**In `services/api`, with `GLOW_ENV=test`, in a clean process environment:** `python manage.py check`, `python manage.py test tests --verbosity 2`, `ruff check .`, `ruff format --check .` and `mypy`, all clean. **In `packages/contracts`:** its tests, with the corpus run through Python and the generated validators, and `npm run check`, which regenerates the outputs in memory and compares them. **In `apps/mobile`:** `npm run check` (its typecheck, lint and tests) passes with the regenerated outputs and no other change; CI's Mobile checks job runs its export and rendered checks. **In `proofs/postgres-ordering`:** its offline tests under `env -i`, Ruff and mypy.

**In CI, the Database proof checks job on the code head,** after the ordering and identity suites, on the third database, through the HTTP endpoints:
1. **The settings:**
   - every setting reads its launch default, D18's staff-approval setting included;
   - a publication writes a new version, a `StaffAudit` row and `policy_published`, and moves the pointer;
   - a publication crossing each fixed limit is refused, and nothing is written, including a history publication that changes the consent version it names while making nothing more readable (DM-55);
   - a retired value stays matchable for its holder and is refused for a new choice.
2. **The fields:**
   - each of the four fields accepts list values within its pick limit, and refuses an unknown value, a retired value for a new choice, and a value over the limit;
   - orientation and relationship status, orientation's own words, and narrowing either field's set are refused without the sensitive-fields consent: before it is accepted, after its withdrawal, and while the version accepted is not the current one (DM-55);
   - the own words are bounded, and never appear where their display flag is off.
3. **"Show me" sets** start at all, take list values only, and are never returned to anyone but their owner; a value the console adds is in every set that keeps all; "not stated" is in sets that keep all and in no narrowed set; and a member who declines the sensitive-fields consent is seen by viewers who keep all.
4. **The age range** refuses a minimum below 18 and a maximum below the minimum.
5. **The location:**
   - an area is chosen by ID;
   - approximate coordinates map to the nearest area, and afterwards they are found in no table, log line, response or outbox event;
   - no route returns a distance;
   - the phone-location query changes nothing, and the area is kept only when the member sets it;
   - the coordinates appear in no URL, error response, validation message, exception text, log line at any level, or idempotency record;
   - the committed area file matches its recorded hash and holds 925 areas.
6. **Consent:**
   - onboarding consent's accept and withdraw reach the send check through `glow_chat` (a send refused after a withdrawal);
   - the sensitive-fields consent's withdrawal removes the two values, leaving each row "not stated" in place with its event, and resets their sets (DM-55);
   - an old consent version is refused;
   - a `sensitive_profile` decision neither satisfies nor revokes onboarding consent;
   - the sensitive-fields consent's withdrawal also removes orientation's own words and the records of the commands that carried the two fields.
7. **The adult check:** 18 today passes, as do the leap-day cases of the onboarding fixtures; a date under 18 fails, a future date and an impossible one are invalid input, none is stored, and the age state stays `unknown`. For a self-declared adult, a future date, at the eligibility step or in a birth input, is refused (`invalid_request`) and changes nothing. A corrected date under 18, at either, is refused (`forbidden`) before the request's other refusals (a stale version, a birth time not given, a lapsed onboarding consent) and stores nothing, with no idempotency record, while the failing rerun commits: the age state becomes `unknown` with no date, the current birth input `missing` with its mapping back to `pending`, and a visible profile `incomplete`, so a send is refused. A retry is refused and changes nothing. A birth input with another passing date changes the age state's date. The transition bumps `eligibility_version`, and SV1's identity suite still passes.
8. **The birth input:** submit, correct and change write private revisions; a birth input without a time (`unknown` precision) is refused, and an approximate time keeps its entered value; no route returns another member's input; SV2 creates no `EngineIdentity`, a new revision returns a test's seeded one to `pending`, and a new eligibility date sets the current revision to `missing` (D8).
9. **Visibility:**
   - completion refuses each missing requirement;
   - pause and resume go through `glow_chat` (a send refused while paused);
   - resume rechecks completion;
   - completion is refused without a resolved chart and without identity verification, and passes with both seeded in setup; no SV2 code writes either;
   - a staff approval without identity verification is refused while the setting is off, satisfies only that requirement while it is on, survives the setting being switched off, and, revoked, demotes a visible profile; no member route reaches it;
   - the owner's completion read lists exactly what is missing;
   - each change emits its event;
   - completion and demotion take the account row lock first, and a requirement withdrawn while a completion waits is seen by it;
   - every requirement writer ends with the one recompute: in Stage A, each owner writer and staff approval makes a profile `visible` when it meets the last requirement, and a write that finds a requirement missing makes a `visible` profile `incomplete` (D9);
   - removing a requirement from a visible profile refuses or demotes, as the brief says for each; a paused profile stays paused.
10. **Photos (Stage B):**
    - a grant beyond the policy's limits is refused;
    - an upload moves only through quarantine, the seam and review;
    - approval and rejection are the automated check's decisions, written to `StaffAudit` with a `system:` subject, and only an approved variant's reference is returned; the check's fixture approves nothing in the runtime, and the check never clears a staff restriction;
    - reorder by another owner, and removal by another owner, fail;
    - removal withholds delivery at once and completes only on the purge acknowledgment;
    - a duplicate or out-of-order provider event changes nothing, and no member route can deliver one;
    - a completion that does not match its grant's key, or exceeds the policy's bytes, changes nothing and its object is not adopted (deleting such an object is the adapter's, in P11), and a second completion for an adopted key changes nothing (OD-62);
    - processing reads only the adopted original (its size and entity tag), only its variant is ever referenced for delivery, and no object key holds an account, profile or asset ID, a filename or a member value;
    - removal completes only when every object of the asset is acknowledged deleted;
    - approval, delivery and a removed asset's purge each ask the hold port first;
    - an approval never undoes an owner's removal;
    - a policy publication above a media ceiling is refused.
11. **Ownership:** every route refuses another member's object and an unauthenticated request, and answers a stale version with its version error.
12. **No secret and no coordinate in any output:** the job's secret check, and a log capture at `DEBUG`, find none; and no stored idempotency digest can be reproduced from its command without the key.
13. **One pointer order** (D19): every transaction's pointer locks follow name order; a lock out of order is an internal error that rolls the transaction back, shown offline and by a reversal; nothing outside `settings_store` locks a pointer.

**Every test with its reversal** (D15), recorded in the evidence record.

## Classification expectation

Full scope: code, migrations with data, a contract change, a workflow change and the proof. The manager classifies with `main`'s trusted policy, inspects the complete workflow diff and the job's actual steps, and requires full checks before the merge (`AGENTS.md`).

## Report format

Each stage's prompt asks for: branch, code head and records head; the environment check and start gate; for each Outcome item, the files, tests and reversals; the area file's hash and source; every command with its result line; the run of record (each job, the gate's line, the profile suite's counts, the phase's duration, whether a retry fired); what could not run; every deviation.

## Review plan

- **The manager verifies each stage's report** against the pushed branch: the complete diff within the owned paths, the seal, reversals re-run where useful, and the run of record's logs.
- **Then each stage's PR,** Codex's review of its head, and **an exact-head code and security review of that stage's final code head, with a written threat model.** Sensitive data and uploaded files are both security boundaries (DM-31 item 3's reasoning for SV1). Its focus:
  - each route's ownership and refusals;
  - the settings' fixed limits and audit, including a limit crossed in two publications (DM-55);
  - the sensitive fields' consent and withdrawal;
  - what the location keeps and what it never keeps;
  - the birth input's privacy and the HDE boundary;
  - the media state machine, its seam and its provider events;
  - the seal;
  - the proof's secret handling;
  - that no member route reaches a staff operation, and a staff operation's subject comes only from its caller in code until P07's staff authentication;
  - D17's rules in every response and every error, validation messages included;
  - the "all" marker and "not stated": a value the console adds, a retired value, and a member who declines the sensitive-fields consent;
  - consent's purpose filtering and the current-version check, at each acceptance and at each sensitive save (DM-55);
  - the age state's transition, a corrected date, and the demotion of a visible profile;
  - the outbox: events carry references, never values, and each reference names a record that still exists (DM-55);
  - the stored idempotency digests (D17);
  - the seeded requirements: no runtime path writes a resolved mapping, `verified` or an approved photo, and a test's seeded rows cannot reach the runtime;
  - staff approval without identity verification: staff only, only while the setting allows it, audited, revocable, and never standing in for another requirement;
  - the area file: its pinned hashes, and nothing fetched;
  - D9's recompute at the end of every requirement writer: no path makes a profile `visible` with a requirement missing, and none leaves one `visible` after a write that finds one missing; each change has its own registry entry and event, and only the profile edit that clears the summary is the owner's `edit` (DM-55);
  - a date that fails the adult rule, at either writer: nothing of it is kept and no idempotency record is kept, the rerun's effects commit before the request's other refusals, and a retry changes nothing more; a future date changes nothing at either (DM-55);
  - upload-grant replay and expiry, the hold port's place in each path, the automated check never clearing a staff restriction, and provider-event authenticity at the port;
  - R2's shape (OD-62): keys that reveal nothing, an original never delivered, a completion matched to its grant, processing on the adopted object, and deletion acknowledged for every object;
  - one pointer order (D19): each transaction's pointers in name order, and the check that enforces it.

  Stage A's review takes these items except the media ones; Stage B's takes the media ones, D19, and whatever Stage B changes in Stage A's code.
- **Dev Manager:** this brief, before any prompt; each stage's design changes, if any; before each stage's PR merges, at a named commit, the CI policy's paragraph and the data model's and contract's rewritten texts. The prompts need no read of their own: they authorize no credential and no live action.

## Stage A, correction C1 (DM-54)

C1 corrects Stage A's code head `b97bc15` (integrated at `e0c0ffe`; PR43) to DM-54's words, applied above. Codex's review of `93a27ea` found nothing, so C1 carries no Codex finding.

**The items:**
1. **D9's recompute** (Y3, Y5): every Stage A requirement writer ends, in its own transaction and on rows read after the account row lock, with one shared recompute. An `incomplete` profile with nothing missing becomes `visible`; a `visible` profile with anything missing becomes `incomplete`; `paused`, `restricted` and `removed` stay as they are.
   - The writers are D9's list for Stage A: the profile edit, the four fields, the area, the onboarding consent's accept and withdraw, the adult check and the birth input, and staff's approval without ID verification and its revocation.
   - A completion in an F04 owner command (the profile edit, the fields, the area) keeps `complete` (`owner`). A completion that follows a write in another flow is Y4's `requirements_met` (`system`).
   - Each change emits its outbox event, as D9 says.
2. **The registry entries** (Y4), each with an allowed and a forbidden example (W5): `requirements_met` from `incomplete` to `visible` (`system`; `eligible`; `A05`); `restrict` from `visible` and from `paused` to `restricted` (`moderator`; `A05`). No existing entry changes.
3. **A birth input whose date fails the adult rule** (Y6 to Y8): refused, with nothing of it stored, while its transaction still commits the failing rerun:
   - the age state becomes `unknown` with no date;
   - a current birth input becomes `missing`, its mapping back to `pending`;
   - a `visible` profile becomes `incomplete`.

   The operation returns the refusal without raising, so the transaction commits, and it stores no idempotency record, so a retry is refused at the adult-check gate and changes nothing more.
4. **CI's mypy** (Y9): `[tool.mypy]`'s `files` in `services/api/pyproject.toml` gains `glow_profiles`, and the configured `mypy` passes.
5. **The data model's sentence** (Y10, Y11), in DM-54's words.
6. **The records:** the data model's SV2 rows and the contract document's F02 to F06 server mapping, where items 1 and 3 change what they say; the package README's SV2 section, where it lists the registry entries; and the evidence record's new section "Correction C1", under "Stage A".

**Owned paths (C1):** the paths "Owned paths (the sessions)" gives Stage A, for these items only:
- `services/api/glow_profiles/**`, and SV2's own modules in `services/api/glow_domain/`;
- `services/api/pyproject.toml`: `[tool.mypy]`'s `files` only (Y9);
- `services/api/tests/`: SV2's profile tests;
- `packages/contracts/production/flows-v1.json`: Y4's entries only; `packages/contracts/tests/test_transition_contract.py`: their examples; `packages/contracts/README.md`: SV2's section;
- `proofs/postgres-ordering/**`: the profile suite, its tests and the README's SV2 section;
- `docs/architecture/data-model.md`: Y11's sentence and SV2's rows; `docs/architecture/production-contracts.md`: F02 to F06's server mapping;
- the evidence record: "Correction C1".

**The stop rule (C1):** the correction stops and reports, with no further change, if it needs any of these:
- a model or migration change;
- a change to an existing DTO, or a new one;
- a change to `glow_chat`, `glow_identity`, `glow_api`, the workflow, a lock or a dependency;
- a change to an existing registry entry;
- a role the oracle does not authorize.

The Database proof checks job must also stay within its 30-minute timeout.

**The review after C1:** no delta review (DM-54, section 14). The exact-head code and security review, with its written threat model, reads C1's head in full, with Y12's two focus items.

## Stage A, correction C2 (DM-55)

C2 corrects C1's code head `86a2156` (integrated at `6e5d0d1`; PR43) to DM-55's words, applied above, and to the exact-head review's findings as disposed (the evidence record, "Exact-head review of Stage A"). Codex's P2 on `40db2c2` (`operations.py:1019`, a future birth date) is item 1. Its review of `9c5f6ee` found nothing new.

**The items:**
1. **A future date, and a date under 18, at both writers** (Z1 to Z4; DM-55, section 3; review finding 2):
   - **The eligibility step:** for a self-declared adult, the date's outcome comes before the stale version check. A future date is refused `invalid_request` and changes nothing. A date under 18 is refused `forbidden`: the operation returns the refusal without raising, the reset commits, and no idempotency record is stored.
   - **The birth input:** the date's outcome comes right after the adult-check gate, before the onboarding consent, the stale version and the birth time. A future date is refused `invalid_request` and changes nothing; a date under 18 is refused as Y6 to Y8 already build.
   - **A key conflict** still refuses first, at both.
   - **The tests:** check 7's cases at both writers, each with its reversal. They include a date under 18 behind each later refusal (a stale version at both; a birth time not given and a lapsed onboarding consent at the birth input), and a future date at each writer.
2. **The history setting's limit** (Z6, Z7; finding 1): a history publication that changes the consent version it names while making nothing more readable is refused, and nothing is written. The two-step path is tested, with its reversal.
3. **The sensitive-fields consent's current version** (Z9, Z10; findings 4 and 9): each sensitive save needs the consent accepted at its current version, read under its policy pointer's lock in the same `read_shared` call as the save's other settings, after the account row lock and in name order. The saves are a sensitive field's value, orientation's own words and a narrowed sensitive set.
   - **The cases:** a save before acceptance, after a withdrawal, and at an old version, each refused, each with its reversal.
   - **Not a defect:** `PreferencesIntent` carries all four sets, so a member who narrowed a sensitive set under an older version cannot save any set until they accept the current version or put that set back to all (DM-55, section 5).
4. **A lapse the profile edit finds** (C1-1; Y4; Z12; finding 10):
   - In the profile edit, a demotion is the owner's `edit` only when the edit itself clears the summary, whatever else is missing.
   - Any other is `requirement_removed`, a transition of its own: it bumps the profile's version and the account's `eligibility_version` and emits `profile_demoted`, as in every other writer. Only the owner's `edit` rides on the edit's own write.
   - Tested, with its reversal.
5. **The withdrawal's field rows** (Z13, Z14; finding 12): each of the member's orientation and relationship status rows is set to "not stated" in place, as Z13 says. A row that already holds "not stated" with no own words and its flag off is left as it is, with no event. Tested, with its reversal.
6. **Bodies that must answer 400** (finding 11; the manager's words, confirmed by DM-55, section 8): "A body the parser cannot hold, such as an integer too large for its number check or nesting deeper than the parser allows, and a text holding U+0000, which the database cannot store, are refused `invalid_request` (400) with the contract's `Error`, like any other invalid body. No value is echoed." Each of the three is tested, with its reversal.
7. **Two F02 entries under W5** (finding 14): `accept` from `accepted` to `accepted`, and `accept_sensitive` from `accepted` to `accepted`, each `owner` with the policy `consent_current`. Each has an allowed example (the current version, newer than the one accepted) and a forbidden one (an old version). No existing entry changes.
8. **The test gaps** (findings 3, 5, 6 and 7), each with a reversal that fails its new case:
   - a case proving the account row lock;
   - the scans and the table search match each fixture value in every form the code could print. The static logging guard covers `glow_identity/age.py`, and no case prints a fixture date in prose;
   - every command's stored digest checked;
   - the static guards forbid a queryset `.update(state=…)` on a profile, and a refusal reason built with `Result(…)` from a value.
9. **Finding 15's test items:**
   - the sealed-runtime test asserts its `refused`;
   - the scan's verdict reads its own line, not the word "clean" anywhere;
   - the suite's case count is pinned;
   - the four registry prerequisites are pinned;
   - `age_years` (Z16, Z17) gets a profile-suite case, with its reversal: whole years for a self-declared adult, `None` while `unknown`, and an integer, never the date. `age.py` itself does not change.
10. **The records** (finding 8). C2's record, the evidence record's new section "Correction C2" under "Stage A", corrects the eight claims, and Stage A's and C1's sections stand as written. It also records the 405 (carried to P11 by Z20). Also:
    - the data model's `AccountAgeState` and `ProfileFieldChoice` rows, and the contract document's F02 to F04 sentences, follow items 1, 4 and 5;
    - every record that cites the brief's revision 3 or 4 for SV2 cites revision 5;
    - the P11 plan's SV2 entry names C2's run of record;
    - the package README's SV2 section lists item 7's entries.

**Owned paths (C2):** the paths "Owned paths (the sessions)" gives Stage A, for these items only:
- `services/api/glow_profiles/**`, and SV2's own modules in `services/api/glow_domain/`;
- `services/api/tests/`: SV2's profile tests;
- `packages/contracts/production/flows-v1.json`: item 7's entries only; `packages/contracts/tests/test_transition_contract.py`: their examples and the registry prerequisites' pins; `packages/contracts/README.md`: SV2's section;
- `proofs/postgres-ordering/**`: the profile suite, its scan, its tests and the README's SV2 section;
- `docs/architecture/data-model.md`: SV2's rows; `docs/architecture/production-contracts.md`: F02 to F06's index rows and server mapping, and the SV2 paragraph's brief revision;
- `docs/testing/p11-deferred-acceptance.md`: the SV2 Stage A entry only, not Z20's or K4's;
- the evidence record: "Correction C2".

**The stop rule (C2; DM-55, section 10):** the correction stops and reports, with no further change, if it needs any of these:
- a model, migration or DTO change;
- a change to `glow_chat`, `glow_identity` (`age.py` included), `glow_api`, the workflow, a lock or a dependency;
- a change to an existing registry entry, or a role the oracle does not authorize.

The Database proof checks job must also stay within its 30-minute timeout.

**The review after C2:** a full exact-head code and security review, with its written threat model, of C2's head, not a delta review (DM-55, section 10; M05 S2). Its focus is the review plan's list, with Z5, Z8, Z11, Z12 and Z15. Codex reads the PR's head as usual. Then the Dev Manager's pre-merge read (DM-55, section 14).

## Stage A, correction C3 (the review after C2)

C3 corrects the tests of C2's code head `01a3acb` (integrated at `26419a9`; PR43) to the exact-head review after C2 (the evidence record, "Exact-head review of Stage A after C2"). That review found no defect in the code. Its one should-fix finding is in a correction class: a test passes where it should fail. Under step 6's rule (a), C3 fixes it before the merge. C3 changes tests and records only, and no design, so it needs no consultation first.

**The items:**
1. **The static guards** (finding 1, (a) to (c)), each with a reversal that fails its new check:
   - **Refusal reasons:** the check also covers `AgeTransitionRefused(…)` in `glow_identity/age.py` and `PortOutcome(…)` in `glow_profiles/identity_verification.py`. A message built from a value fails it.
   - **Logging:** `views.py` holds exactly one `getLogger` call. Every logging call in `glow_profiles` is checked whatever its receiver is named, and so is a write to `sys.stderr` or `sys.stdout`.
   - **Profile state:** every `.state =`, `setattr(…, "state", …)` and `bulk_update` in `glow_profiles`, and any in `age.py`, is either in `recompute.py` or on a named allowlist of writes that are not a profile's.
2. **The guards' limits** (finding 1, (d) and (e)): the record names what the guards cannot see. That is a member view reaching staff code through a helper in `operations.py`, a new operation whose inner function is not named `body`, a recompute inside a condition, and a lazy import in `glow_domain`. The profile suite's cases cover each behaviour.
3. **`BodiesTheParserCannotHoldTests`** (finding 2) is defined before `unittest.main()`.
4. **The fixture date as a label** (finding 3): `profile_cases.py`'s check at the eligibility step no longer uses the fixture date as a label, and no check's label holds a member value.
5. **C2-6:** `profile_cases.py`'s comment on the scans' timing says they run once, after the last case.
6. **The records** (finding 4): the record's new section "Correction C3" corrects Stage A's lock-order sentence. The settings' pointers are taken `FOR SHARE` in name order within each `read_shared` call. The recompute's onboarding read can follow a writer's other pointers. No deadlock follows, since a publication holds one pointer `FOR UPDATE`. It also names the guards' limits (item 2). (C3's delta review found this reason incomplete, its finding N1; the record's claim is in "Delta review of correction C3".)

**Owned paths (C3):**
- `services/api/tests/`: SV2's profile tests (`test_profiles_offline.py`, `test_profile_recompute.py`);
- `proofs/postgres-ordering/**`: the profile suite (`profile_cases.py`) and its offline tests;
- the evidence record: "Correction C3".

**The stop rule (C3):** the correction stops and reports, with no further change, if it needs any change outside tests and the record. That rules out `glow_profiles`, `glow_domain`, `glow_identity` (`age.py` included), `glow_chat`, `glow_api`, a model, migration, DTO or registry entry, the workflow, a lock or a dependency. It also stops if a new check fails on the code at `01a3acb` without a temporary edit, since that would be a code defect for the manager, not a test change. A reversal's temporary edit of code is allowed, and must be undone.

**The review after C3:** a delta review (M05 S2: no non-test line changes). It reads every path C3 touches as it stands at C3's head, with the review's security focus. Then Codex on the final head, the Dev Manager's pre-merge read (DM-55 section 14, and C2-1), the PR run, and the merge.

## Stage B (revision 6)

Stage B starts from `main` at `4dc2061` (PR43, Stage A), with the manager branch's records after it. Its prompt follows the Dev Manager's read of this revision (DM-57). It builds:

1. **Photos** (Outcome item 7; D10 as revised for R2, OD-62):
   - the media policy as a setting, `media.policy`, seeded as version 1 with `development-media-1`'s values by a data migration, within its ceilings in code;
   - the upload grant and its model;
   - the storage and processing ports, with fixture adapters only;
   - the quarantine path, with G-02's seam and the hold port;
   - the automated check's approval and rejection (`system`), and staff restriction on a report (`moderator`);
   - reorder, removal and its acknowledgment, and the delivery reference;
   - F05's routes for the member, each validated against the contract.
2. **The photo requirement** (D9): at least one approved photo. Stage A neither checks nor reports it (`requirements.py`). The check's approval ends with the recompute, which moves a profile to `visible` when it meets the last requirement (`requirements_met`). The removal or restriction of the last approved photo moves a `visible` profile to `incomplete` (`requirement_removed`). Each change has its event.
3. **The registry** (D11): F05's `approve` and `reject` become `system` (OD-61), and `test_f05_quarantine_cannot_be_published_by_uploader` changes with them. These are the only existing entries that change. A transition Stage B's writers make that the registry lacks is a new entry. Stage B uses F05's existing DTOs, and any new one is additive (D11).
4. **One pointer order** (D19), in Stage A's code and Stage B's: the four transactions D19 names, and the check in `settings_store`.
5. **Carried from Stage A** (the carried-items file, "Carried to SV2"):
   - C3's state-write guard's allowlist: a line Stage B moves is updated in the same change, and Stage B's writes of `MediaAsset` state join it as another model's writes;
   - the four spellings C3's guards do not see (the delta review's N2 to N5): a `Profile.objects.create` outside `operations.py`, or a `bulk_create` of `state`; a profile bound by walrus, `for`, `with` or tuple unpacking in an allowlisted function; a file the module opens itself; a label name rebound to a member value. Each guard is widened, with its reversal;
   - DM-50 1.2, if Stage B changes `identity_support.py` (D16).
6. **The proof:** the profile suite gains Stage B's cases (check 10, check 13, and D9's photo requirement in completion's cases), each with its reversal (D15). The job's SV2 steps change only if a step must, and then the manager updates the CI policy's paragraph.
7. **The records:** the data model's `MediaAsset` row and the grant's, as built; the contract document's F05 index row and server mapping; `private-media-fixtures.md`'s note; the contracts README's section; the P11 plan's PV04, DB07 and DB08 partial evidence; the evidence record.

**Stop rules.** The session stops and reports if Stage B needs:
- a new dependency, an S3 or R2 client included (D14);
- a provider call or a credential;
- a change to `glow_chat`, `glow_identity` or `glow_api`;
- a change to a mobile source, test or fixture;
- a change to an existing registry entry other than item 3's.

**Review.** Stage B's exact-head code and security review, with its written threat model, takes the review plan's media items, D19, and everything Stage B changes in Stage A's code. Codex reads the PR's head. Before the PR merges, the Dev Manager reads the data model's and contract's rewritten texts, and the CI policy's paragraph if it changed, at a named commit.

## Sessions

- **Brief, revision 1** (10 November 2026): written after OD-60 and the matrix's recheck; to the Dev Manager as DM-52 ([consultation](../ephemeral/2026-11-10-dm-52-sv2-brief.md), at `73c109b`).
- **DM-52** (10 November; [report](../continuity/dev-manager/reviews/2026-11-10-dm-52-sv2-brief.md), answered at `093204a`, a read of `73c109b`): approved with B1 to B55, R1, R2 and K1 to K7 in given words. Nathan answered its questions in its session: the chart is calculated at once and required, a birth time is required, no staff review, automated identity verification and photo approval, and a console setting for staff approval without identity verification (OD-61).
- **Brief, revision 2** (10 November 2026): B1 to B55 applied as written, with the choices the words left to the brief made and marked.
- **DM-53** (10 November 2026; [consultation](https://github.com/amthorn78/glow-dating-app/blob/4dc2061a33c6f63e2887b11aeb2fd32d6224e23e/docs/ephemeral/2026-11-10-dm-53-sv2-stage-a-paths.md)): Stage A's prompt held. D11's additive DTOs rewrite `apps/mobile/src/contracts/generated/` and, as P04.3's and C1's did, need `flows-v1.json` and a README section; the owned paths leave all three out (AM10-12). It also asks three readings of D8 and D7 against the models, and the confirmation of DM-52's conditions.
- **DM-53 answered** (10 November; [report](../continuity/dev-manager/reviews/2026-11-10-dm-53-sv2-stage-a-paths.md), at `f60cfda`, a read of `c2ee87a`): approved with W1 to W10 in given words. The registry has no `staff` role, so staff act as `moderator`; the sensitive consent, the age state and identity verification get F02 entries of their own; every demotion that follows another write is one `system` entry in F04; F05's automated approval is Stage B's. The three readings are right, with the mapping pointing at the current revision. DM-52's conditions are confirmed as applied, and its choices approved.
- **Brief, revision 3** (10 November 2026): W1 to W10 applied as written.
- **Stage A's prompt, revision 1** (10 November 2026; [prompt](https://github.com/amthorn78/glow-dating-app/blob/4dc2061a33c6f63e2887b11aeb2fd32d6224e23e/docs/ephemeral/2026-11-10-sv2-stage-a-implementation-prompt.md)): given to Nathan, with its TypeSafe reading.
- **Stage A's implementation session** (10 November 2026): branch `claude/sv2-stage-a-impl-0qqzvj`, code head `b97bc15`, records `f2635fa`; run of record, push run 42759801460 on `b97bc15`, every job passed (`Application checks passed`), the profile suite 44 of 44. Its record is the [evidence record](../testing/evidence/2026-11-10-sv2-profiles-media.md), "Stage A", with 13 decisions and deviations for the manager.
- **The manager's verification** (10 November 2026): integrated at the merge `e0c0ffe`; the verification is in the evidence record, "Manager verification". The session's decisions went to the Dev Manager as [DM-54](https://github.com/amthorn78/glow-dating-app/blob/4dc2061a33c6f63e2887b11aeb2fd32d6224e23e/docs/ephemeral/2026-11-10-dm-54-sv2-stage-a-decisions.md): two launch values OD-60 does not give, two added DTOs, what moves a profile to `visible`, the idempotency records' lifetime, a new consent version, a birth input with a failing date, CI's mypy coverage, restriction's registry entry and a stale sentence.
- **DM-54 answered** (10 November; [report](../continuity/dev-manager/reviews/2026-11-10-dm-54-sv2-stage-a-decisions.md), at `1271ca5`, a read of `93a27ea`): the seeds kept, with both launch values to the third A05 message; the two DTOs approved; completion as one recompute at the end of every requirement writer, with `requirements_met` (`system`) in F04; the idempotency lifetime approved and carried; a new consent version acceptable for Stage A and carried (SV3, SV4, P08); a failing birth date refused and not stored while the rerun commits; mypy to cover `glow_profiles` (the `glow_persistence` exclusion is deliberate); restriction's entries under W5; the stale sentence with OD-61's clause; the manager's four items confirmed; the CI policy's paragraph read and matching. No delta review: the exact-head review reads C1's head in full. K1 to K5 carried.
- **PR43** (10 November 2026), opened from the manager branch at `93a27ea`: its PR run 42762594567 passed every job, and Codex's review of `93a27ea` completed with no findings.
- **Brief, revision 4** (10 November 2026): Y1 to Y10 and Y12 applied as written, with "Stage A, correction C1".
- **Stage A's correction C1 prompt, revision 1** (10 November 2026; [prompt](https://github.com/amthorn78/glow-dating-app/blob/4dc2061a33c6f63e2887b11aeb2fd32d6224e23e/docs/ephemeral/2026-11-10-sv2-stage-a-c1-correction-prompt.md)): given to Nathan, with its TypeSafe reading, after Codex's review of its commit. Codex's review of `033e8d4` (completed 05:57 UTC) raised two P1 findings against the unchanged code, both C1's own items: the recompute missing from every writer but the profile edit (`operations.py`, lines 637 to 640; item 1), and a failing birth input stored (`operations.py`, lines 1020 to 1024; item 3). They add no item, and their threads close once C1's head is verified.
- **Stage A's correction C1** (10 November 2026): branch `claude/funny-lamport-5f2s1u`, code head `86a2156`, records `f54545c`; run of record, push run 42769301337 on `86a2156`, every job passed (`Application checks passed`), the profile suite 47 of 47. Its record is the evidence record's "Correction C1", with five decisions, C1-1 to C1-5.
- **The manager's verification of C1** (10 November 2026): integrated at the merge `6e5d0d1`; the verification is in the evidence record, "Manager verification of correction C1". C1-1 to C1-5 accepted. C1-1 (a demotion in a field or area write is `requirement_removed`) and C1-3 (a future birth date refused with no rerun) are the manager's readings on DM-54's words, put to the exact-head review and to the Dev Manager at the pre-merge read.
- **Stage A's exact-head review prompt, revision 1** (10 November 2026; [prompt](https://github.com/amthorn78/glow-dating-app/blob/4dc2061a33c6f63e2887b11aeb2fd32d6224e23e/docs/ephemeral/2026-11-10-sv2-stage-a-review-prompt.md)): of `86a2156`, with a written threat model, held when Codex's review of its commit (`40db2c2`) raised a P2 finding on C1-3's point (a future birth date).
- **Stage A's exact-head review prompt, revision 2** (10 November 2026; [prompt](https://github.com/amthorn78/glow-dating-app/blob/4dc2061a33c6f63e2887b11aeb2fd32d6224e23e/docs/ephemeral/2026-11-10-sv2-stage-a-review-prompt.md)): puts both readings of C1-3 in focus item 3, Codex's and the session's; given to Nathan after Codex's review of its commit. Codex's two P1 threads from `033e8d4` are answered and resolved. Next: the review's report.
- **Stage A's exact-head review** (10 November 2026; from revision 2, at `9c5f6ee`): of `86a2156`, with a written threat model. **Changes required, narrowly.** No finding is blocking. Findings 1 to 8 fall in the correction classes, and the review sends findings 9, 10, 13 and 14 to the Dev Manager with C1-3. The manager's dispositions are in the evidence record, "Exact-head review of Stage A".
- **DM-55 consultation, revision 1** (10 November 2026; [consultation](https://github.com/amthorn78/glow-dating-app/blob/4dc2061a33c6f63e2887b11aeb2fd32d6224e23e/docs/ephemeral/2026-11-10-dm-55-sv2-stage-a-review.md)), on:
  - C1-3 at both writers, with the earlier revisions' erasure;
  - the history setting's limit;
  - the sensitive consent's version;
  - C1-1;
  - the withdrawal's field rows;
  - the manager's settled items;
  - DM-53's and DM-54's conditions as applied;
  - correction C2's scope, with a full exact-head review.

  Next: DM-55's answer, the brief's revision 5 and C2's prompt.
- **DM-55 answered** (10 November; [report](../continuity/dev-manager/reviews/2026-11-10-dm-55-sv2-stage-a-review.md), at `f165861`, a read of `496c39e`): option (b) for a future date, with 1.2 and 1.3 approved; 1.4's erasure declined as worded and carried to P07 for G-01; items 2 to 5 approved, 3 and 5 with conditions; item 6 confirmed, with `age_years` kept and tested and the 405 also to P11; DM-53's and DM-54's conditions confirmed as applied; C2's full exact-head review agreed. Z1 to Z20 in given words.
- **Brief, revision 5** (10 November 2026): Z1 to Z17 applied as written, with "Stage A, correction C2"; Z18 and Z19 in the carried-items file, Z20 in the P11 plan.
- **Stage A correction C2's prompt, revision 1** (10 November 2026; [prompt](https://github.com/amthorn78/glow-dating-app/blob/4dc2061a33c6f63e2887b11aeb2fd32d6224e23e/docs/ephemeral/2026-11-10-sv2-stage-a-c2-correction-prompt.md)): the ten items of "Stage A, correction C2", with TypeSafe's reading (Opus 5.5 at high), given to Nathan after Codex's review of its commit. Next: C2's report and the manager's verification, then the full exact-head review of C2's head.
- **Correction C2's report** (10 November 2026; branch `claude/awesome-maxwell-wo9jxa`, code head `01a3acb`, records `ca0ad16`; the record, "Correction C2"): the ten items, with 32 reversals; run of record 42864458572, every job passed, the profile suite 53/53. No stop rule was met.
- **The manager's verification of C2** (10 November 2026): integrated at the merge `26419a9`; the verification is in the evidence record, "Manager verification of correction C2". C2-1 to C2-5 accepted, C2-1 as a reading on DM-55's words for the review and the Dev Manager; C2-6, a stale code comment, a recorded follow-up. Codex's three findings on `496c39e` and `399c68d` are C2's items 1 to 3; its P2 on a future date is answered with DM-55's ruling.
- **Stage A's exact-head review prompt after C2, revision 1** (10 November 2026; [prompt](https://github.com/amthorn78/glow-dating-app/blob/4dc2061a33c6f63e2887b11aeb2fd32d6224e23e/docs/ephemeral/2026-11-10-sv2-stage-a-c2-review-prompt.md)): a full review of `01a3acb`, with a written threat model and TypeSafe's reading (Opus 5.5 at extra high), given to Nathan after Codex's review of its commit. Next: the review's report.
- **Stage A's exact-head review after C2** (10 November 2026; from revision 1, at `44455a5`): of `01a3acb`, with a written threat model. **Changes required, narrowly, in tests only:** no defect in the code and no blocking finding; one should-fix finding (the static guards) in a correction class, and five nits. C2-1 confirmed. The dispositions are in the evidence record, "Exact-head review of Stage A after C2". The manager's section "Stage A, correction C3" lists C3's items, with no consultation needed (tests and records only).
- **Stage A correction C3's prompt, revision 1** (10 November 2026; [prompt](https://github.com/amthorn78/glow-dating-app/blob/4dc2061a33c6f63e2887b11aeb2fd32d6224e23e/docs/ephemeral/2026-11-10-sv2-stage-a-c3-correction-prompt.md)): the six items of "Stage A, correction C3", tests and records only, with TypeSafe's reading (Opus 5.5 at high), given to Nathan after Codex's review of its commit. Next: C3's report and the manager's verification, then C3's delta review.
- **Correction C3's report** (10 November 2026; branch `claude/stoic-faraday-gist9o`, code head `fee4fdc`, records `414d4a7`; the record, "Correction C3"): the six items, tests and records only, with twelve reversals; run of record 42908603138, every job passed, the profile suite 53/53. No stop rule was met.
- **The manager's verification of C3** (10 November 2026): integrated at the merge `bfc633b`; the verification is in the evidence record, "Manager verification of correction C3". Deviations 1, 3 to 5 accepted; deviation 2 (the no-deadlock reason's reliance on PostgreSQL's row locking) to the delta review and the Dev Manager. The allowlist's pinned lines carried to Stage B.
- **C3's delta review prompt, revision 1** (10 November 2026; [prompt](https://github.com/amthorn78/glow-dating-app/blob/4dc2061a33c6f63e2887b11aeb2fd32d6224e23e/docs/ephemeral/2026-11-10-sv2-stage-a-c3-delta-review-prompt.md)): every path C3 touches, read whole at `fee4fdc`, with TypeSafe's reading (Opus 5.5 at high), given to Nathan after Codex's review of its commit.
- **C3's delta review** (10 November 2026; from revision 1, at `c235b68`): of `fee4fdc`. **Approve with nits:** C3 closes finding 1 (a) to (c), and nothing needs a change to tests or code before the merge. Five nits, none in a correction class: N1, the no-deadlock reason, is incomplete and its conclusion holds (the record's claim is now the review's, observed on PostgreSQL 17.11 and not tested by a suite case); N2 to N5, further spellings the guards do not see, carried to Stage B. PR43's pull-request run 42912992237 on `c235b68` passed every job. The dispositions are in the evidence record, "Delta review of correction C3".
- **DM-56, the Dev Manager's pre-merge read** (10 November 2026; [consultation](https://github.com/amthorn78/glow-dating-app/blob/4dc2061a33c6f63e2887b11aeb2fd32d6224e23e/docs/ephemeral/2026-11-10-dm-56-sv2-stage-a-pre-merge.md)): the governing and contract texts (DM-54 section 13, DM-55 section 14), Z1 to Z20 as applied, C2-1, the no-deadlock reason (recommended: merge with the review's claim, and a suite case in Stage B), N2 to N5's carry, and whether PR43 may merge. Next: DM-56's report, then the PR run and Codex on the final head, and the merge.
- **DM-56 answered** (10 November; [report](../continuity/dev-manager/reviews/2026-11-10-dm-56-sv2-stage-a-pre-merge.md), at `d342f05`, a read of `e86b635`): the pre-merge read approved with conditions (V1, V2 in the data model); Z1 to Z20 confirmed; C2-1 approved (V3, in D7); the no-deadlock reason's option (a), with V4 in the evidence record and V5, the pointer order, carried to Stage B's brief; N2 to N5's carry confirmed; PR43 may merge once V1 to V5 are applied and the final head's run and Codex are clean. V1 to V5 applied as written.
- **Stage A merged** (10 November 2026): PR43 at `4dc2061`, by the expected-head guard on `a644771`, after PR run 42923450949 passed every job and Codex found nothing on that head; the merge receipt is in the evidence record, "The merge receipt for Stage A". Its four session branches were deleted by the cleanup run, and its eleven prompts and consultations are pruned, with their links pinned at `4dc2061`. Next: Stage B, starting with this brief's revision 6, which decides the pointer order (DM-56 V5) for the Dev Manager's read, then Stage B's prompt.
- **Brief, revision 6** (11 November 2026): Nathan's direction that photos use R2 object storage (OD-62) in D10 (two ports, opaque keys, Glow's own processing at the system review step, deletion acknowledged for every object); D19, one pointer order in every transaction, with its check; the section "Stage B (revision 6)"; checks 10 and 13 and the review plan. To the Dev Manager as DM-57. Next: DM-57's answer, then Stage B's prompt.
