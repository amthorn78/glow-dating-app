# Static application data model

P02.2 defines 32 app-owned Django models and two migration files in
`services/api/glow_persistence/`. P06.2 Stage A adds two models, `ChatIdentity` and
`ChatReadCursor`, in a third migration, `0003_chat_identity_read_cursor`; Stage B1
amends that unapplied migration (the [migration plan](../operations/migration-plan.md),
"Amending an unapplied migration") so that it also adds `OutboxEvent.sequence`, the
database-assigned order column, and the reconciliation mark `reconcile_code` on
`ChatBinding` and `ChatIdentity`; `0001` and `0002` are byte-identical to P02's. SV1
adds one model, `AccountAgeState`, in a fourth migration, `0004_account_age_state`. These
are **unapplied design artifacts**: the fixture API does not install this app, and no
migration is applied anywhere but a disposable proof database. P06.2 Stage A adds the first ORM
code over them, the chat contact adapter and its outbox delivery (`services/api/glow_chat`,
below). SV1 adds maintained sign-in over the same rows (`services/api/glow_identity`;
"Maintained authentication mapping", below). Both run only under the disposable-PostgreSQL
proof's settings; the API's runtime imports none of it and keeps its dummy backend. No
real authentication is served, and no deployed queue exists. The P11 [migration plan](../operations/migration-plan.md) owns
activation order.

## Identity, time and field semantics

Every app model derives from `Record`: an opaque UUID primary key, aware
`created_at`/`updated_at` instants and an integer revision at least one. The wire
contract serializes UUIDs as lowercase strings and instants as UTC seconds.
Repositories must reject revision overflow above the wire safe-integer bound
rather than round a database bigint. Revisions are compare-and-swap inputs; Django
`save()` does not implement that contract automatically. Creation uses the wire
absence precondition zero, then creates revision one.

All declared fields are required unless their model field has `null=True` or
`blank=True`. A nullable fact is unknown/not yet available; it must not be filled
by guessing. An empty profile bio means incomplete or withheld text,
not eligibility. `BirthInput.birth_date` and `local_time` preserve civil values;
an unknown time is null, though SV2's server refuses a birth input without a time (OD-61). A timezone and its provenance are either both present
or both null. No UTC birth instant is fabricated. Schema text/Unicode validation
runs before storage; model metadata and PostgreSQL do not replace the shared
wire decoder. `Profile.bio` maps to wire `summary` (maximum 500 code points).

Model source is the exact field/length/constraint definition. Named constraints
in the migration state are executable DDL definitions awaiting P11 proof. Django
field choices also have explicit state checks; validations such as JSON shape,
per-owner relationships and state-transition legality remain repository/domain
responsibilities. Models must never be serialized wholesale.

## Maintained authentication mapping

**As built by SV1** (the [SV1 brief](../planning/sv1-identity.md), revision 5; the
[SV1 evidence record](../testing/evidence/2026-11-09-sv1-identity.md)), on
**django-allauth 65.21.1** (`django-allauth[headless]`, pinned with its hashes in
`services/api`'s development scope and in the disposable-database proof's lock), and
**sealed**: `services/api/glow_identity` runs only under `proofs/postgres-ordering`'s identity
settings, on a disposable PostgreSQL; the served runtime imports none of it. P11 wires the routes,
the settings, the keys and the mail provider, and moves the pins to the runtime scope.

**The identities.** `AppAccount.auth_user` is a unique protected FK to
`settings.AUTH_USER_MODEL`, which stays `django.contrib.auth.User` (DM-45 item 5). App UUIDs
differ from that library identity. Passwords (Django's own hashers and its four validators,
minimum length 10), codes, normalized email identities, sessions and tokens are owned by Django
and allauth, never by Glow credential code. allauth's `EmailAddress` holds the normalized,
unique, verified email (`ACCOUNT_UNIQUE_EMAIL`; the default `User.email` field is still not
unique, and is not relied on). `auth.User.username` holds a random opaque value (`g` and 32
hexadecimal characters) that Glow's account adapter sets, so nothing of the email is copied into
a column email sign-in never uses. Only email login exists (`ACCOUNT_LOGIN_METHODS`); social
login, multi-factor authentication, login by code, phone numbers and the browser client are not
configured.

**Sign-up and verification.** Sign-up takes an email and a password through allauth's headless
API for the `app` client. Glow's account adapter (`save_user`) creates the auth user, its
`AppAccount` (`unverified`) and its `AccountAgeState` (`unknown`) in one transaction. allauth opens
no transaction around headless sign-up, so its later steps (the `EmailAddress` row, the code) are
outside it; a failure there leaves an `unverified` account that cannot sign in. Verification is
mandatory and by code (three attempts, 15 minutes), never by link: no frontend URL is set, so no
message carries a link. After allauth marks the address verified, F01's `verified` transition
runs (`glow_identity.revocation.mark_verified`): its own transaction, the account row locked
`FOR UPDATE` before anything else, refused unless the state is `unverified` (an `active` account
is no change), `version` and `eligibility_version` bumped; if it did not commit, the next sign-in
takes it, so a verified address never leaves its account `unverified`. A confirmed
password-reset code also verifies the address, outside the account adapter (allauth's
`verify_email_indirectly`), and the next sign-in then takes the transition. A verified email alone
establishes nothing else: not adulthood, consent, profile or eligibility.

**Email change and recovery.** One address per account (`ACCOUNT_CHANGE_EMAIL`), changed only after a reauthentication by password within the last 300 seconds (`ACCOUNT_REAUTHENTICATION_REQUIRED`; a sign-in does not count): the new address is verified by code before it replaces the old, and the old address gets the email-changed notice.
The code goes to the address asked for whether or not another account holds it, so the two answer
alike; an address another account holds verified cannot be linked, even with that inbox's code
(refused `email_taken`). Password reset is by code (three attempts, three minutes, restarted once
the code is confirmed) and signs no one in; a reset for an address that has no account sends
nothing (`ACCOUNT_EMAIL_UNKNOWN_ACCOUNTS` off).

**The session reference.** `AccountSession.auth_session_ref` is an adapter-provided **non-secret**
library session identifier, as this mapping required: the primary key of allauth's
`UserSession` row (`allauth.usersessions`, a `BigAutoField` not derived from the session key).
allauth creates that row for every sign-in in its `user_logged_in` receiver; Glow's account
adapter (`post_login`) then opens the `AccountSession` through `glow_chat`'s `open_session`, which
locks the account, refuses one that is not `active`, and records the session at the account's
current `session_epoch` with a lifetime of 30 days from sign-in (absolute: no operation extends
it; Nathan decides the members' limit before P11 serves sign-in), and sets the Django session's
expiry to the same instant, so allauth's own endpoints stop with Glow's session. If `open_session`
does not apply, allauth's session ends in the same request and no token from that sign-in names a
session that exists. **The session key is a credential, not a reference:** headless returns it to
the `app` client as `meta.session_token`, and allauth's own endpoints accept it as
`X-Session-Token` for the session's whole life; it lives in `django_session` and in
`UserSession.session_key`, and Glow never stores, hashes or logs it. A token's `sid` is that key
encrypted under a key derived from `SECRET_KEY` with a fresh initialization vector per token, so
it is not a reference either. A password change would give a kept session a new key, so a
password change ends every session (`ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE`); no other allauth flow at
65.21.1 changes a signed-in session's key.

**Tokens.** allauth's JWT strategy, through Glow's subclass: RS256, access tokens of 300 seconds,
refresh tokens of 30 days, stateful validation (each token checked against its session, its user
and that user's password hash) and refresh rotation; the refresh tokens' identifiers live in the
Django session, so they die with it. A refused refresh token that passes allauth's own checks, its
signature first, but carries an identifier its session no longer holds is a replay: its session
ends at both layers. The signing key and `SECRET_KEY` are secret references the deployment
supplies (the proof generates both for each run); none is committed or in an environment template.

**Revocation, at two layers.** Logout, ending a session from allauth's session list (Glow's
`USERSESSIONS_ADAPTER`), a password change (every session), a password reset (every session), a
replayed refresh token, suspension and `deletion_pending` (`glow_chat`'s `suspend` and `delete`,
then every allauth session of the user ends and the auth user is made inactive). Glow's step, a
reviewed `glow_chat` operation in its own transaction and never inside an open transaction,
commits first; allauth's sessions end after it; both steps are repeatable, so a request whose
second step fails answers with an error and a repeat completes it. `epoch` binds a session to
`AppAccount.session_epoch`. The one actor class (`glow_identity.authentication`) refuses unless
the account is `active` and the session `valid`, unexpired by the database's clock and at the
current epoch, and marks an expired row it finds (`expire_session`). Session metadata alone still
revokes nothing: the allauth session ends too.

**Personal data in allauth's rows.** `UserSession` records each sign-in's IP address and user
agent (`USERSESSIONS_TRACK_ACTIVITY` off: no last-seen updates); P08 sets their retention and
their place in export and deletion. The same rows hold the session key, a credential: export must
never include it, and deletion removes it with its session.

**Still for P11:** the routes, settings, keys and mail provider in the runtime; allauth's client-IP
settings behind P11's proxy; a shared cache for allauth's rate limits once more than one worker
runs; and validation with the real target's persistence. A schema change to the user model is no
longer cheap: allauth's tables now reference `auth.User`.

References: django-allauth 65.21.1, read from its installed source on 9 November 2026 (the
evidence record names each file and line); its configured headless specification, generated from
the pinned release and SV1's settings (the evidence record has its SHA-256 and paths);
[Django migrations](https://docs.djangoproject.com/en/5.2/topics/migrations/).

## Data groups and ownership

All rows below are application-owned. The storage direction is the app's own
logical database on HDE's PostgreSQL service, with restricted owner, migration and
runtime roles (OD-18, [ADR 0004](../adr/0004-app-database-placement.md)). It
supersedes the audited app schema in HDE's logical database, `railway`. The audit
maps all 32 provisional models to new app-owned relations if retained; none reuses
a legacy or HDE physical table.
The final P11 design may consolidate provisional models. Engine references are
opaque external identifiers, never foreign keys into engine tables. A FK targets
only an app model or the app's maintained auth table. Index names shown are
definitions, not proven query plans or capacity claims. No schema, grant or
migration is activated by this fixture work.

| Models | Relationships, constraints and indexes | Privacy and lifecycle |
|---|---|---|
| `OutboxEvent`, `WebhookInbox` | Migration 0001 precedes app state. Unique event `dedup_key`; unique provider/event identity. Versioned aggregate reference; queue/lease/delivery timestamps. Verified/applied inbox and leased/delivered outbox states require corresponding timestamps. Indexes on state plus scheduling time. `sequence` (P06.2 B1, migration 0003): a database-assigned identity column, never written by the app, that orders delivery within one `available_at`. | Operational-minimized. Reference payload only; no birth/chat/token body. Payload digest binds replayed provider identity to original content. Worker retention/retry policy must be explicit. |
| `AppAccount`, `AccountSession` | One app UUID per maintained auth user; account lifecycle checks, positive eligibility/preference/block/session revisions; unique non-secret session reference (SV1: allauth's `UserSession` primary key), expiry (SV1: 30 days from sign-in, the Django session's expiry set to the same instant) and revocation timestamp. Session owner/state index. | Account-private. Session and visibility revocation are immediate transaction requirements, ended at both layers (SV1, "Maintained authentication mapping"); secrets (passwords, session keys, tokens, codes) remain with auth. |
| `AccountAgeState` (SV1, migration 0004; SV2 Stage A, migration 0005) | One row per account (one-to-one, cascading with the account); the state (`unknown`, `self_declared_adult`), the method that set it (`none`, `self_declaration`), when it was recorded, the policy version and, since SV2 (its brief's D7), the self-entered birth date. Checks tie each state to its methods (`unknown` has no policy version) and the date to the state (`age_state_birth_date`: present with `self_declared_adult`, absent with `unknown`). Written only through `AgeAssurancePort` (`glow_identity.age`): SV1's `record` at sign-up, and SV2's one `transition`, which runs inside the caller's transaction, takes the account row `FOR UPDATE` before the age state's row, and bumps the account's `eligibility_version`. | Account-private. Sign-up records `unknown`. The row is the date's one home (D7): the adult check writes `self_declared_adult` with the date when the member is 18 or over on the database's UTC date (policy version `adult.self-declaration.v1`; a 29 February birthday falls on 1 March in a common year, P04's rule). An impossible date, a future date and a date under 18 are each refused and not stored. A future date is invalid input (`invalid_request`) at both writers, the eligibility step and the birth input, and changes nothing; for an `unknown` account the birth input's adult-check gate refuses first (`forbidden`). Since correction C2 (DM-55), a date under 18 from a self-declared adult is checked first at both writers, after the idempotency check and before every other refusal (a stale version, a birth time not given, a lapsed onboarding consent): it is refused (`forbidden`), nothing of it is stored and no idempotency record is kept, while the transaction commits the failing rerun: `unknown` with no date, the current birth input `missing` with its mapping back to `pending`, and a `visible` profile `incomplete`. A retry is refused and changes nothing more. For an `unknown` account the eligibility step refuses either date and changes nothing, and the birth input is refused at its adult-check gate. Earlier birth input revisions keep their contents, readable only by their owner and never current again (G-01's decision, in P07; DM-55). A birth input with another passing date changes the age state's date and reruns the check. SV3 reads a member's age in whole years (`age_years`), never the date; P09.2 adds the stores' signals. |
| `IdentityVerification` (SV2 Stage A, migration 0005) | One row per account (one-to-one, cascading with the account); the state (`unverified`, `verified`, `staff_approved`), the method (`none`, `automated_check`, `staff_approval`), the verification company's opaque reference or the staff subject and reason, and the decision time. A check ties each state to its method and provenance (`identity_verification_provenance`); a row the account does not have reads as `unverified`. | Account-private (its brief's D18; OD-61). Written only through the identity verification port (`glow_profiles.identity_verification`), after the account row lock, with the eligibility bump. Glow keeps no ID image, ID number or selfie. No SV2 code writes `verified`: there is no verification company yet, and a test seeds the state in its own setup. Staff approval without ID is a staff operation with a subject and a reason, written to `StaffAudit`, available only while the `identity.staff_approval` setting is on (off at launch), read under its pointer's lock; it stands in for identity verification only. Switching the setting off leaves past approvals; staff can revoke one at any time. Both staff operations end with D9's recompute (correction C1; DM-54): an approval that meets the last requirement makes the profile `visible`, and a revocation demotes a `visible` one. This is not the contract's `verify_identity`, which means email verification. |
| `PolicyRevision`, `SettingVersion` (SV2 Stage A, migration 0005), `ConsentDecision` | Unique named policy pointer; SV2 seeds one per setting (migration 0007), whose `policy_version` is the label `<name>.v<number>` and whose `artifact_ref` is the current `SettingVersion`. Append-only setting versions, unique by name and number (positive), with their content, publication time, staff subject and reason. Append-only consent decisions unique by account/purpose/revision with policy version and event time; the purpose is `onboarding` or `sensitive_profile` (`consent_purpose`). Account/purpose/time index. | The settings (its brief's D2; OD-60, OD-61): every choice is a setting whose version 1 is its launch default (staff subject `system:launch-default`). A publication, a staff operation with no route (`glow_profiles.settings_store.publish`), validates the setting's closed schema and the fixed limits in code, then writes the next version, a `StaffAudit` row and `policy_published`, and moves the pointer under its `FOR UPDATE` lock; a refused publication writes nothing. Readers lock the pointers `FOR SHARE`, after the account row, in name order within each `read_shared` call; a writer's recompute reads `consent.onboarding` in a call of its own, after the writer's other pointers (DM-56). Consent is account-private, and every reader filters by purpose: onboarding decisions are `glow_chat`'s writers', the sensitive-fields consent's are SV2's own, and neither satisfies or revokes the other. Missing policy/decision grants nothing. |
| `Profile`, `Area` (SV2 Stage A, migrations 0005 and 0006), `ProfileFieldChoice` (SV2 Stage A, migration 0005) | One profile per account; explicit visibility (`incomplete`, `visible`, `paused`, `restricted`, `removed`); bounded display name (80) and summary (500); since SV2 (its brief's D5) the home area, a nullable `PROTECT` foreign key to `Area`, in place of the text location label, which migration 0005 removes. Profile state/UUID cursor index. `Area`: the 925 core-based statistical areas of the Census Bureau's 2024 Gazetteer outside Puerto Rico, each with its unique five-digit GEOID, its name (80) and its published internal point (`Decimal(9,6)` each, in range), loaded by migration 0006 from the committed table after its SHA-256 is checked. `ProfileFieldChoice` (D3): one row per account and field (gender, orientation, looking for, relationship status) with the chosen value IDs (JSON, GIN-indexed as `profile_field_values`), the setting version they were chosen under, the member's own words (40 characters, gender and orientation only) and the display flag (`looking_for` is always shown). | Account-private source; the candidate projection allowlist is SV3's. The coordinates the phone sends are never stored: only the area. A field with no row reads as `not-stated` (orientation, relationship status) or unset. Orientation and relationship status values and orientation's own words are sensitive: each such save, and narrowing either field's "show me" set, needs the sensitive-fields consent accepted at its current version, read under its pointer's lock with the save's other settings (correction C2; DM-55). Its withdrawal sets each of the member's orientation and relationship status rows to `not-stated` in place, with no own words, the display flag off and the setting version unchanged, bumping the row's version and emitting `profile_field_changed`, so every earlier event still names an existing row; a row that already holds `not-stated` with no own words and the flag off is left as it is, with no event. A retired value stays its holder's and matchable; a new choice of it is refused. Completion to `visible` needs current onboarding consent, the adult check, the fields (display name, summary, gender, looking for), the area, the chart and identity verification, read after the account row lock. Since correction C1 (DM-54), every writer of a requirement (the profile edit, the four fields, the area, the onboarding consent's accept and withdraw, the adult check, the birth input, and staff's approval without ID verification and its revocation) ends, in its own transaction, with one shared recompute (`glow_profiles.recompute`): an `incomplete` profile with nothing missing becomes `visible`, a `visible` profile with anything missing becomes `incomplete`, and `paused`, `restricted` and `removed` stay as they are. So a profile shows as soon as its last requirement is met, whoever meets it, and a requirement that lapsed without a write (a new onboarding consent version) demotes at the member's next requirement write. Each change is its own registry entry with its own event: a demotion is the owner's `edit` only when the profile edit itself clears the summary, whatever else is missing; every other demotion, a lapse the profile edit finds included, is `requirement_removed`, which bumps the profile's version and the account's `eligibility_version` and emits `profile_demoted` (correction C2; DM-55). Nothing else in SV2 writes the profile's state; pause, resume and restriction are `glow_chat`'s writers. |
| `Preferences`, `PreferenceSetEntry` (SV2 Stage A, migration 0005) | One preferences row per account; its policy version is the catalog version its sets were last written under. Since SV2 (its brief's D4 and D5): the age range, `minimum_age` never below 18 (`preferences_age_floor`) and `maximum_age` null or not below the minimum (`preferences_age_range`), and the distance choice, an ID of the location setting's choices. `PreferenceSetEntry` (D3): one row per account, field and value of a "show me" set, with its position; unique by account, field and value; never `not-stated` (`preference_set_not_stated`); a set that keeps all is the single row `all`, never the list of current values. Field/value/account index (`preference_set_lookup`). | Account-private: returned to no one but the owner. Every set starts at `all`. The two-way rule matches when at least one of each member's values is in the other's set, for every field; SV3 applies it. Narrowing orientation or relationship status needs the sensitive-fields consent, and its withdrawal resets both sets to `all`. SV2 does not use the earlier `values` JSON. No distance is returned anywhere. |
| `BirthInput`, `EngineIdentity` | Private input revisions unique by account/version; input time/provenance checks. One current mapping per account with protected birth-input FK. Resolved mapping requires engine ID plus engine/contract provenance; pending mapping has none. Engine IDs intentionally not unique across accounts. | Account-private input/mapping; engine-owned chart semantics. Shared references do not grant chart deletion rights. Cross-row input ownership is checked in UOW, not by a simple FK. |
| `MediaAsset`, `MediaObject` (SV2 Stage B, migration 0008) | Owner FK; unique provider/storage reference when present (`storage_ref` is the original's object key); unique current position per owner (not `removed`). Approved state requires variant and review references (`review_ref` is the automated check's `StaffAudit` row). Since SV2 Stage B (its brief's D10): the delivery reference exists only while `approved` (`media_delivery_only_approved`); an approved asset holds no revocation record (`media_approved_unrevoked`); `removal_pending` and `removed` hold the owner's removal record (`removal_requested_at`, `media_removal_record`); `review_pending`, `approved` and `rejected` record G-02's seam (`detection`, `no_detector` in SV2; `media_seam_passed`). Staff's restriction on a report is its own revocation record (`restriction_ref`, the restriction's `StaffAudit` row), and the check's rejection reason a code (`rejection_reason`). `MediaObject`: one row per object in private storage, the original (one per asset, at its grant's key) and each variant processing writes; a unique key of 32 random hexadecimal characters (`media_object_opaque_key`), the adopted completion's size and entity tag (`media_object_adoption_evidence`), and the storage adapter's deletion acknowledgment (`deleted_at`). | Private originals and variants in private R2 storage (OD-62), behind the storage and processing ports, with fixture adapters only in SV2 (no R2 call, credential, SDK or decoder; P11 proves R2, PV04). App owns review, order and lifecycle; every state change goes through F05's registry table in one writer, which withholds delivery in every state but `approved`. A key holds no account, profile or asset ID, filename or member value. Only provider upload completion, authenticated by the storage adapter, moves `upload_pending` → `quarantined`; only the system review step, Glow's own processing on the adopted original then G-02's seam for every adopted upload, moves `quarantined` → `review_pending` (an upload with no variant is then rejected, `no_variant`); only the automated check approves or rejects (`system`), asking the hold port before approval and never acting on a staff restriction. Owner removal withholds delivery at once (`removal_pending`); the purge asks the hold port first, and `removed` follows the acknowledgment of every object. The purge and that acknowledgment run in any account state, under the account row's lock (`lock_account_any_state`), so a photo removed before its owner is suspended or asks for deletion is still purged; every other photo command, staff operation, system step and read refuses an account that is not active (`account_not_active`; DM-58 item 9, SV2 Stage B's correction C1). Reorder moves each photo through a temporary position above every real one inside one UOW; PostgreSQL's behaviour is shown by the profile suite, P11 proves the real target. Completion (D9) needs an approved photo: the check's approval recomputes, and the removal or restriction of the last approved photo demotes a `visible` profile. Rows are never deleted, so every outbox event's reference names an existing record. `MediaCollection.version` is derived from them, 1 plus the sum of the account's asset versions, with no column of its own (DM-58): a change that deletes an asset row, such as a retention rule, first stores the account's collection version, so that it never goes back. |
| `MediaUploadGrant` (SV2 Stage B, migration 0008) | One per asset (one-to-one, cascading with the asset and the account); a unique opaque `grant_ref` (what `MediaUploadGrant` returns) and the original's unique object key (`media_grant_opaque_key`); the media policy version it was issued under (`policy_version`); the issue and expiry times (`media_grant_expiry`); and its use (`used_at`, the adopted upload's time, never after the expiry: `media_grant_used_in_time`). | Account-private. Short-lived (the policy's grant seconds, 60 in `development-media-1`), opaque and one-use by Glow's own record, within the policy's limits (four live photos; the 20 collection entries). Its completion is checked against the byte limit of the version the grant records, not the current one (DM-57 U3, U4); only the first matching completion is adopted, and a later one changes nothing. The store's upload credential (P11's signed upload address for the key) goes to no member in SV2; how it reaches the client is P11's (DM-57 U6). |
| `DirectionalInteraction`, `Block` | Unique ordered actor/target; self-pairs forbidden; current like/pass or active/removed block row. FK indexes support both directions. | Account-private unilateral actions. Removing a block increments outgoing block revision and cannot restore contact automatically. Historical resurfacing/rematch policy A05 remains unset. |
| `Match` | UUID pair sorted by underlying UUID value (`account_low < account_high`), unique pair and positive contact version. | Participant-only projection. One pair record; history/rematch requires policy, never a second match row for the same pair. Reciprocal likes and eligibility are cross-row transaction invariants. |
| `CompatibilitySnapshot` | Ordered viewer/candidate, both engine references, birth/mapping revisions, full eligibility vector, engine/contract/adapter provenance and expiry. Unique directional revision tuple; viewer/expiry index. | Account-private metadata only; no HDE result body/score/band column. `ready` means internal metadata state, not permission to expose an HDE result. Cache/output rights remain A01. |
| `RecommendationBatch`, `RecommendationEntry` (SV3 Stage A, migration 0010) | Owner, collection, policy and own three eligibility revisions in batch; each candidate's three revisions in entry. Since SV3 Stage A (its brief's D7): the collection, `recommendations` or `discovery` (`batch_collection`), and at most one batch per owner and collection (`batch_one_per_collection`). Limit 1–100; positions 0–99; unique candidate and position per batch. Nullable snapshot FK can clear when removed. Owner/time/ID cursor index. | Bounded account-private candidate queue, written only by `glow_discovery.pages` (sealed until P11). A page with no cursor creates the batch in one transaction after the owner's account row lock (`FOR UPDATE`) and the five settings the selection reads (`FOR SHARE`, name order): the earlier batch of that collection is deleted with its entries, and the new one records the owner's three revisions, a policy version made of the five settings' version numbers (a publication of any makes it stale; DM-60 Q3), a limit of 100, a state (`ready`, `empty`, `pending` or `unavailable`) and an expiry 30 minutes later, with up to 100 entries in rank order (positions from 0) and their candidates' revisions. A cursor names the batch and an offset, under a MAC over the owner, the collection, the batch and the offset; a page refuses, alike, a cursor not so issued, a missing, expired or not-`ready` batch and one whose owner revisions or policy version changed, then rechecks every entry from the offset in one statement and writes nothing. The page maximum, 50, is smaller than the batch's 100. No snapshot is written: the entry's snapshot FK stays null (no `CompatibilitySnapshot` holds a fixture's or an HDE result). No self-candidate is ever selected (D3's SELF). |
| `ChatBinding`, `MessageSubmission` | One binding per match; provider/channel unique when known; active binding requires reference; `reconcile_code` (P06.2 B1, migration 0003) marks a binding whose provider state is in doubt after a dead letter, with the Glow code of its last attempt. Actor/idempotency key unique; accepted message requires provider receipt, pending message requires private text. | Provider owns retained conversation history. App temporarily owns bounded delivery spool (4000 code points), clears per approved retention/receipt policy. Only reference/version enters outbox. No provider membership alone grants send permission. |
| `ChatIdentity`, `ChatReadCursor` (P06.2, migration 0003) | One provider user ID per account and provider; provider/user reference unique; `pending` until the provider confirms the user, then `active`, or `deactivated` (B1, CX4); `reconcile_code` marks an identity whose provisioning, deactivation or token revocation was dead-lettered (B1, F3); the cut-off of the latest per-user token revocation the provider confirmed. Account FK is PROTECT. One read cursor per match and member, pointing at the last read `MessageSubmission` (PROTECT). | The user reference is `secrets.token_hex(16)`, never derived from an account ID, name or email, never shown or logged; no name, image or custom field exists to send. The mapping outlives the account row until the provider deletion step that needs it has run (P07/P08); purge removes cursors before the submissions they name. Unread is counted from Glow's own accepted submissions after the cursor; the provider's read state is not used. |
| `DeviceRegistration`, `NotificationSettings` | Unique installation ID and private token-store reference; account FK; iOS/Android and active/revoked checks. One notification preference row per owner, defaults off. | Provider-managed secret reference, not plaintext token. Installation transfer/rotation requires old owner revocation in UOW. Wire provider token goes into the supported secure store before this reference is saved. |
| `SafetyReport`, `ModerationCase`, `Appeal`, `StaffAudit` | Reporter/subject nullable `SET_NULL`; preserved subject marker. Protected report/case relationships. Resolved case/appeal requires outcome. Unique audit request ID; object/time audit and moderation queue indexes. | Safety-restricted description/evidence and immutable audit. Evidence-ref JSON shape/ownership validated before save. Staff subject is external authenticated operator identity, distinct from dating accounts. No support-to-moderation privilege inheritance. |
| `SupportRequest` | Optional account or secure contact reference, bounded subject/description, explicit lifecycle and retention metadata. | Account-private/support-restricted. Public requests get generic acknowledgment; contact verification precedes account action. Category is server-classified, not an undeclared mandatory client field. |
| `ExportJob`, `DeletionJob`, `ProviderLifecycleStep` | Own-account export with ready artifact/expiry requirements. Unique deletion subject and nullable account FK survive purge. Each step belongs to exactly one export or deletion; unique idempotency key and verified evidence requirement. Retry queue index. | App orchestration; processor owns actual export/purge. Required processor manifest and scope completeness are UOW/domain checks. Completed deletion cannot be inferred from row state alone. |
| `DeletionTombstone`, `IdempotencyRecord` | Tombstone UUID subject survives without account FK; protected deletion job. Intent dedup unique by actor/operation/key, with target and complete canonical intent bound by the digest; immutable outcome code, result reference and committed version. | Restore-replay and operational-minimized. No email/birth/chat payloads or cached grants in tombstones/receipts. Tombstone must exist at revocation, before eventual hard purge. |
| `Entitlement` | Unique account/product reference; only permitted state `disabled`. | Conditional boundary only. No paid entitlement can be activated with these definitions; A06 and maintained provider integration require later schema change. |

## Trusted eligibility and unit-of-work boundaries

The source of truth is server-owned current policy and rows, never client boolean
flags. See [trusted eligibility](trusted-eligibility.md). Stored snapshot evidence
includes viewer/candidate identities, both `eligibility_version` values, both
`preferences_version` values, both `blocks_version` values and policy version.
Batch owner fields plus candidate entry fields reconstruct the same vector.
Changing a mapping reference, input, policy or safety state invalidates reuse.

**The eligibility read as built (SV3 Stage A; its brief's D2 and D3; sealed until P11).**
`glow_discovery.predicates` holds the predicates once, as SQL, for three readers: each batch's
selection, each page's recheck and the trusted adapter (`glow_discovery.eligibility`, behind
`TrustedEligibilityService`). Each is **one statement**, so in READ COMMITTED it reads one
snapshot, and each reads, for the viewer and for the candidate: the account's state (ACTIVE), the
age state (ADULT: an accepted state, `self_declared_adult` only, with its date), the latest
`onboarding` consent decision by purpose at the current version (CONSENT; a `sensitive_profile`
decision never counts, and a new version fails every older acceptance at once), the profile's state
(`visible`, which carries VERIFIED, COMPLETE and MODERATION), the four fields' rows against the
other's "show me" rows in both directions (D4: `all` matches every value, those added later and
"not stated" included; a narrowed set never matches "not stated"; a missing set row accepts no one;
a field the narrowing setting makes not narrowable reads as keeping all), the age range from the
age state's date in whole years on the server's UTC date (both ways under `both_ways`), the distance
between the two areas' internal points in the viewer's direction (D5: compared, never selected; one
area is distance zero), and `active` blocks in both directions. The selection and the recheck add
consumption (D7): no like or pass from the viewer, and no match row for the pair in any state.
Every predicate fails closed: a missing row is NULL or no row, never a pass. The adapter builds its
`PairEvidenceVersion` from both accounts' three revisions, both profiles' versions and the
selection's policy version. A page holds the viewer's account row (`FOR UPDATE` to create a batch,
`FOR SHARE` to continue one) and the settings' pointers `FOR SHARE` while it reads, so every
viewer-side fact is stable for the transaction; the candidates' facts come from the one statement.

The future PostgreSQL UOW acquires policy/account/pair rows in stable order and
rechecks the complete vector inside the committing transaction. Missing,
wrong-pair or mismatched evidence returns stale/reload/denied; a passing earlier
read is insufficient. Preference/block absence is protected by persistent
account counters, so insert/remove races cannot evade version checks. Every
relevant account/consent/profile/moderation/visibility/deletion change bumps
`eligibility_version`; preference/block mutations additionally bump their own
outgoing collection counter. Policy publishers lock the same `PolicyRevision`
row that privileged actions lock. These are requirements, not working locks.

| UOW | Must commit together | Work only after commit |
|---|---|---|
| Consent, profile, preference, pause or birth correction | Expected revision check, affected data, aggregate and directional counters, mapping/snapshot invalidation, idempotency receipt, outbox events | Resolution/invalidation/notification task dispatch; worker rechecks current version |
| Like and reciprocal match | Ordered account/pair locks, full eligibility recheck, directional action, one canonical pair match if reciprocal, one logical match event and receipt | Channel provisioning/notification through bounded deduplicated worker |
| Block/unmatch/suspend/delete access | Relevant account/pair locks and counters, contact revocation, session epoch/revocation as applicable, durable provider steps, outbox; deletion job+tombstone when deleting | Provider revocation/purge. Worker must not reactivate a revoked binding from a late completion |
| Send | Same revocation lock boundary, current two-party eligibility/contact version, dedup digest, bounded submission spool and outbox | No contact-version recheck at dispatch: a message authorized before a revocation committed is delivered ahead of the removal that follows it, and delivery refuses only a revoked, failed or in-doubt binding ("Delivery" below; the P06.2 brief, D6); P11 proves the in-flight policy and per-channel order across retries [Corrected by M05, finding 26: this said "Recheck contact version before provider dispatch"; `glow_chat/delivery.py` compares no contact version, by design] |
| Staff action | Validated external actor/scope and object ownership, reasoned transition, immutable staff audit and outbox | Narrow provider action/reconciliation with no elevated WordPress database access |
| Inbox or worker completion | Verify signature outside data mutation; then unique event receipt/digest, current identity/version check, derived state and new outbox event if needed | Acknowledgment; stale/duplicate events cannot overwrite current state |
| Photo (F05): a member's command, a store event or a system step | The account row lock first; the asset's transition through F05's table, with its object and grant rows; the check's `StaffAudit` row; D9's recompute; the idempotency receipt and outbox events | The real adapters' calls (P11): the upload credential, processing, the seam's detector, the check's vendor, the delivery reference and the deletion request. In SV2 the fixture adapters are called inside the transaction, with no effect outside the process: their calls write to the process's memory (the fixture store's objects, credentials, reads, deletion requests and delivery references), which a rollback does not undo (SV2 Stage B's correction C2, N5); P11 moves each real call after the commit (the outbox and a worker), or records why it stays inside and handles what a rollback after it leaves (DM-58) |

Idempotency keys are scoped to authenticated actor and operation; changed target
or other canonical request content under the same key is a conflict, not a second
action. Completed records keep an immutable outcome code, object UUID and its
committed revision. P05.3 adds `liked`, `passed`, `unmatched`, `blocked` and
`unblocked` to the existing `committed` code in the static definition and matching
unapplied migration. These identify the original logical result independently of
the object's later state. They do not cache a private response or grant. Replay first rechecks
current authorization, preserves that logical receipt, then builds only a current
safe projection (or generic unavailable/denied if revoked/deleted). The object
may since have changed; never mislabel its current version as the original result.
Only successful committed actions get this receipt; a precondition/authorization
failure does not become an indefinitely cached grant or denial. Digests summarize
validated canonical requests and are not credential cryptography. Crash before
commit leaves neither state nor event. Crash after commit requires redelivery;
logical event uniqueness does not establish exactly-once external transport.
Outbox payload references must target an existing owning record retained through
delivery/reconciliation (for example, a message submission or provider step).
No event relies on rereading a body already erased by deletion. Leases/retries have
configured finite limits and dead-letter reconciliation; no retry duration is
selected by schema defaults.

## Chat contact and the outbox (P06.2 Stage A, Stage B1, Stage B2 and Stage C1)

The [P06.2 brief](../planning/p06-2-chat-integration.md), revision 3, items 1 to 4, and
its "Carried to Stage B and P11" with "B1's design points" (Stage B1: F1 to F5, CX4 to
CX6, under DM-15's conditions). The domain port is `glow_domain/chat.py`
(`ContactPersistence`); the persistence adapter that implements it is
`glow_chat/contact.py` (`OrmContactPersistence`); the outbox delivery is
`glow_chat/delivery.py`; the chat provider port and its fixture adapter are
`glow_domain/chat_provider.py` and `chat_provider_fixtures.py`; the Stream adapter on that
port and the client token's signer are `glow_domain/chat_provider_stream.py` (Stage B2);
the token rules are `glow_domain/chat_tokens.py`; the order column's field type is
`glow_persistence/fields.py`; the conversation reads (Stage C1) are
`glow_domain/chat_reads.py` (the port and its domain types), `glow_chat/reads.py`
(`OrmConversationReads`) and `glow_domain/chat_projections.py` (their projections into the
production contracts). The adapter is a new package rather than code in
`glow_persistence`, so that the model registry stays definitions only (its static check
still forbids every connection) and the runtime's seal names one package it must never
import. The disposable-PostgreSQL proof (`proofs/postgres-ordering`) runs P06.DB's race
suite against this adapter as its second subject; that run, not this page, is the
evidence ([evidence record](../testing/evidence/2026-10-05-p06-2-chat-integration.md)).

**The transaction design** is P06.DB's reference design (its brief, D5), carried as
written: `READ COMMITTED`; row locks by primary key with `SELECT ... FOR UPDATE` in one
canonical order (the lower account, the higher account, the match, the sending session);
every check in code under the locks, with the time read after them; authorize, then
deduplicate; a locked read that finds no row refuses; deletion is the lifecycle
transition. The send writes its `MessageSubmission` and its `OutboxEvent` in one
transaction. The adapter has no test switch; a caller may observe a writer's hold points
(`TransactionProbe`), which only signal and wait.

**The send's checks beyond P06.DB's** (D5): both profiles must be `visible`, and both
accounts' latest onboarding consent decision must be `accepted`. The consent is F02's
`ConsentIntent`, held as `ConsentDecision` rows with **`purpose` `onboarding`**
(`glow_domain.chat.ONBOARDING_CONSENT_PURPOSE`); decisions are append-only, and the
latest is the highest version. The pause, the restriction and the consent withdrawal
each lock the account row first and bump the version of the row the send reads (the
profile's, or a new decision's), so the send, holding both account locks, reads them
current. A resume restores a paused profile; nothing in Stage A lifts a restriction
(P07). Until P07 sets Nathan's policy, an unknown or paused state denies contact (F06).

**Provider identifiers** are random and committed before any provider call: a match's
activation creates the match, each member's `ChatIdentity` if it has none (state
`pending`, with its own outbox event `identity_created`, written before the channel's;
B1, CX4), and the `ChatBinding` with a random `channel_ref` (state `pending`), with the
channel's outbox event, in one transaction under both account locks. An identity that
already exists from an earlier match gets no second event (DM-15 3.5). **Activation's
checks (B1, CX5):** under both account locks it checks the accounts' state, an active
block, an existing pair, and the send's own checks of both profiles (`visible`) and
both onboarding consents (`accepted`), so a pause, a restriction or a withdrawal that
committed before it refuses it, and one that waits on its locks finds the match and
refuses the send that follows (the suite's `activation.*` cases; oracle rule O11). It
remains the proof's and the conformance run's way to make a match, not F09's
activation: reciprocal likes and current two-person eligibility are checked by the
activation P11 wires, under the same locks. A send stores its provider message ID in
`MessageSubmission.provider_message_ref` when it is authorized; acceptance by the
provider moves the submission to `accepted`. A send is accepted into a `pending` or
`active` binding: its event queues behind the channel's creation.

**Outbox events** (schema version `glow-chat-1`). Each carries only its aggregate, its
version and a payload reference. Six are delivered, each as exactly one provider call:

| Event (aggregate) | Written by | Provider call on delivery | Receipt recorded |
|---|---|---|---|
| `identity_created` (identity; B1) | match activation, for each member without an identity, before the channel's event | provision the user, by its opaque ID only, idempotently (`provision_user`) | `ChatIdentity.state` `active` (provisioned only on receipt, DM-15 3.2) |
| `match_activated` (match; payload the binding) | match activation | create the channel with exactly the two members, each `active`; a member not provisioned dead-letters the event at once with `member_unavailable`, never waits (DM-15 3.2) | `ChatBinding.state` `active`; on the dead letter, `failed` and marked |
| `message_submitted` (submission) | an authorized send | send the message on the member's behalf, with its committed ID; never into a `revoked`, `failed` or marked binding (DM-15 4.5) | `MessageSubmission.state` `accepted` |
| `contact_revoked` (match, new contact version) | a block of an active match, an unmatch | remove both members; history stays at the provider (D6); made for a `failed` or marked binding too, and a channel the provider does not have counts as removed (CX6) | `ChatBinding.state` `revoked`, the mark kept |
| `access_revoked` (account, new epoch) | suspension, deletion | deactivate the provider user; a user the provider does not have counts as deactivated (DM-15 3.3) | `ChatIdentity.state` `deactivated` |
| `session_epoch_bumped` (account, new epoch) | every session-epoch bump (today suspension and deletion) | revoke the user's tokens issued before the cut-off, sent rounded up to the next whole second, strictly (DM-15 5.2); a user the provider does not have counts as revoked | `ChatIdentity.tokens_revoked_before`, the exact cut-off |

`block_changed`, `session_revoked`, `session_expired`, `profile_paused`,
`profile_resumed`, `profile_restricted`, `consent_accepted` and `consent_withdrawn` are
logical events for later consumers and make no provider call. An unmatch or a block
does not revoke tokens per user: removal suffices, and a per-user revocation would cut
the user's other matches. A single-device sign-out bumps no epoch; that device's token
lives until it expires (one hour), a residual recorded beside DB09.

**Delivery** is first in, first out over the chat events, by `(available_at,
sequence)`: `available_at` is the `clock_timestamp()` the writer read under its locks,
the same for every event of one transaction, and `sequence` (B1; DM-15 3.1) is a
`bigint GENERATED BY DEFAULT AS IDENTITY` column the database assigns in insertion
order, so the events one transaction wrote are delivered in the order it wrote them,
with neither the app's clock (`created_at`) nor the random `id` deciding; the delivery
phase shows the order holding over repeated activations with the app's clock running
backwards. The due events are read in that order and each, in turn, is leased by its
key in one transaction that reads what the call needs; one provider call follows
outside any transaction; a second transaction records the receipt and marks the event
`delivered`. Per channel and per user the order is the commit order, because every
writer whose events concern the same provider object locks a common account row. A
failed event that may be retried returns to the head with its `available_at` unchanged,
so nothing overtakes it, and is repeated with the same committed identifiers, so the
provider never gets a second user, channel, message or member. After five attempts, or
on a final code, the event is dead-lettered. Every provider error is kept only as a Glow
code (`provider_unavailable`, `provider_rejected`, `channel_unavailable`,
`member_unavailable`); no provider text is stored, logged or shown. A message
authorized before a revocation committed is delivered into the channel's history first
and the members are removed after it: it stays `accepted` in Glow's record, no member
can read the channel, and nothing re-sends it. Stage A and B1 run delivery in-process
under the proof; there is no deployed worker before P11, and one deliverer at a time is
assumed.

**The reconciliation mark** (B1; F3, CX6; DM-15 item 4). A dead letter whose call may
have reached the provider leaves Glow's record in doubt, so it marks the row it
concerns with `reconcile_code`, the Glow code of its last attempt (a code from the
provider port's `ERROR_CODES`, never provider text): a dead-lettered `match_activated`
marks its binding and turns a `pending` binding `failed`; a dead-lettered
`contact_revoked` marks its binding; a dead-lettered `identity_created`,
`access_revoked` or `session_epoch_bumped` marks its identity. A marked row stays what
it is otherwise: a dead-lettered removal leaves the binding `active` and marked, and a
revocation of a marked or `failed` binding still makes its removal, after which the
binding is `revoked` with the mark kept. **P11's reconciliation path** reads the
`dead_letter` outbox events and the marked bindings and identities, compares each with
the provider's state through the provider port's idempotent operations (a channel's
members, a user's state, a token cut-off), repeats the operation the dead letter
represents or records the difference, and clears the mark only when the provider's state
agrees with Glow's record; it runs under P11's deployed worker with the outbox's crash
and lease recovery (the [deferred acceptance plan](../testing/p11-deferred-acceptance.md),
DB06 and DB09). Nothing in Stage B1 reconciles.

**Token rules** (D6): `grant_chat_token` grants one hour only for a `valid`, unexpired
session at its account's current epoch, of an `active` account with an `active` chat
identity, which means provisioned and not deactivated (DM-15 5.1: a `pending` identity
is refused with `no_chat_identity`); it refuses after suspension or deletion. It signs
nothing. Under OD-45 (24 October 2026) no client token is issued: the rule, B1's grant
and B2's signer stay in the code, dormant and unserved, until a later cleanup (the P06.2
brief, point h), and P11 serves no token endpoint [Corrected by M05, finding 24: this said
"P11 serves the endpoint and Stage B2's adapter signs", which predates OD-45].

**The grant's transaction** (B1; F1, DM-14 item 3; closes Stage A's F1 gap).
`OrmContactPersistence.grant_token` runs the rule in one transaction: the account row,
then the session row, locked `SELECT ... FOR SHARE` in the send's order, so a grant
waits for an epoch bump in flight (which holds the account `FOR UPDATE`) and then
refuses at the new epoch, and a bump waits for a grant in flight; the time is
`clock_timestamp()` read under those locks and passed as `now`, so the issue time and
the revocation's cut-off come from one clock, the database's, and the app server's
clock plays no part; every check of `grant_chat_token` runs on the locked rows; the
locked session's account is checked against the pre-lock read (F2). The grant writes
nothing and returns the rule's grant with its issue time; B2's signer sets the token's
`iat` to that issue time truncated to the whole second (DM-15 5.2). The cut-off of a
per-user revocation stays the bump's pre-commit time read after its account lock
(`event.available_at`), stored exact, and is sent to the provider rounded up to the
next whole second, strictly, so every token issued at or before the cut-off is covered.
The suite forces both orders with the app clock skewed an hour ahead (`token.*` cases):
a grant that waits on a bump refuses after it, and a grant that commits just before a
bump has an issue time before the bump's cut-off.

**The Stream adapter** (B2; the brief's design points c and d, DM-16 2.3, 2.4, 4.1, 4.4
and 4.5). `StreamChatProvider` in `glow_domain/chat_provider_stream.py` implements the six
operations of the port on an injected `getstream` 6.1.0 client and holds nothing else: it
never constructs a client, reads no environment variable and imports only the port, the
token module and the SDK, so the runtime's seal keeps it out of every runtime import and
the harness imports it by path. It sends identifiers and members only: a user is created
with its ID; a channel in `glow-match` with exactly its two members and the first of them
as the creator (`created_by_id`, which Stream requires of a server-side creation; one of
the two members, never a name, image or custom field); a message with its committed ID,
its text and its sender; a removal names the two members; a deactivation carries an empty
body; a revocation carries the user and the cut-off exactly as delivery gives it
(`revocation_cutoff_sent`). It reads before it acts, so a repeat never undoes a revocation
(4.4): provisioning creates the user only when Stream does not hold it (a deactivated user
counts as held) and never resets a field, reactivates or clears a cut-off; channel creation
creates only when the channel is absent, so a repeat sends the members to no existing
channel; removal sends only while one of the two is still a member; deactivation and
revocation never create a user, and a revocation whose cut-off is not later than the one
Stream holds sends nothing. `already=True` comes from those reads, and for a message whose
ID Stream reports as existing. Only the SDK's own API error and its transport errors and
timeouts are mapped to Glow codes, by HTTP status and Stream's numeric code (a transport
error, a timeout, a 5xx, a 429 or an unreadable success is `provider_unavailable`; 404 with
code 16 is the operation's missing object, `channel_unavailable` or `member_unavailable`;
every other 4xx is `provider_rejected`; a send's 400 code 4 is told apart by its text in
memory only); every other exception, the harness's stop types among them, propagates
unchanged, and no provider text is stored, returned or logged. The adapter enforces no ID
shape. The conformance run (`proofs/stream-chat`, `conformance`) is its live evidence; the
offline contract runs the same rows against the fixture and against the adapter on a
hand-written recorded transport (`tests/test_chat_provider_stream.py`).

**The signer** (B2; design point e, DM-16 3.1 to 3.3). `getstream` 6.1.0's `create_token`
takes `iat` from the SDK's own clock minus five seconds and `exp` from that clock plus a
lifetime, with no parameter for either, so the pre-approved fallback signs the client's
token in `sign_chat_token`: HS256 through `pyjwt`, with the injected client's own secret
read at signing time and kept nowhere, and the claims exactly `user_id`, `iat` and `exp`,
where `iat` is the grant's `issued_at` truncated to the whole second (less
`IAT_BACKDATE_SECONDS`, a fixed number of whole seconds, never more than 5, that is 0
unless Stream refuses a token whose `iat` is the current second; the conformance run's
row shows the value in force) and `exp` is the grant's `expires_at` truncated to the
whole second, never later. The SDK's clock plays no part, so the issue time stays the
database's (F1).

**The conversation reads** (Stage C1; the [P06.2 brief](../planning/p06-2-chat-integration.md),
"Stage C under OD-45", points b, c and e, with DM-22's conditions). Under OD-45 the app
holds no provider credential; Glow's API serves history and new messages, and P11 serves
the endpoints. No migration and no model change: the reads use the rows Stages A to B2
committed. `OrmConversationReads` runs only under the proof's settings, as the rest of
`glow_chat` does.

- **The send's checks, under the send's shared locks.** The history read, the
  conversation list and the read-cursor command make the send's checks, in the send's
  order, on rows read under the send's locks taken `FOR SHARE`, as B1's grant takes its
  own: the lower and higher `AppAccount`, the `Match`, the reader's `AccountSession`, then
  the active `Block` rows either way, both `Profile` states and both latest onboarding
  `ConsentDecision` rows under those account locks (the send's own
  `_contact_state_checks`). A read waits for a revocation in flight, which holds one of
  those rows `FOR UPDATE`, and reads its result; a revocation waits for a read in flight.
  The time is `clock_timestamp()` after the locks. This is the interim default under F06
  (DM-22 3.1): the A05 history question goes to Nathan before P11 serves the reads.
- **The history read checks twice** (DM-22 3.2). The first check's transaction reads the
  page's rows and ends; the provider call (the port's `read_message_texts`, for the page's
  accepted messages' `provider_message_ref`, in one call) runs outside any transaction, so
  no lock is held across it and a safety action never waits on the provider; then a new
  transaction takes the same shared locks and checks again, and the page is returned only
  if it passes. A refused first check makes no provider call. A page with no accepted
  message makes no call, so "anything new?" is answered from Glow's rows alone and its one
  check is its answer.
- **Which rows a page reads.** The match's `ChatBinding` (its `channel_ref`, for the
  provider call only); its accepted `MessageSubmission` rows, each joined to its own
  `message_submitted` `OutboxEvent` in state `delivered`; the reader's own `pending` and
  `failed` submissions on the newest page only, with their spool `text` and their event's
  `available_at`. The other member's pending and failed submissions are never read for a
  page. The provider ID never leaves the server.
- **No binding-state check** (C1's exact-head review, finding 9). Unlike the send, the
  reads make no `BINDING_NOT_ACTIVE` check: a `failed` binding under an `active` match is
  listed, and its page serves the member's own pending and failed submissions. No
  accepted message can exist for it: a binding is `failed` only when its channel's
  creation dead-lettered, and delivery never sends into a `failed` binding.
- **The order follows acceptance** (DM-22 2.2). Accepted messages are ordered by
  `(OutboxEvent.delivered_at, OutboxEvent.sequence)` of their `message_submitted` event:
  `delivered_at` is the database's `clock_timestamp()` in the transaction that records the
  provider's acceptance and moves the submission to `accepted`, so a message accepted
  after a later one sorts after it; `sequence` breaks a tie deterministically. Neither the
  app's clock (`created_at`, `updated_at`) nor a random ID decides. The page, the "older"
  and "newer" cursors, the unread count and the read cursor's "forward" all use this
  order, so a late acceptance reaches the reader's next poll as new and unread (the
  database job's `read.order_follows_acceptance`). It holds while one channel's receipts
  commit in their `delivered_at` order, as they do under the one deliverer at a time this
  section's "Delivery" assumes; a deployed worker with concurrent deliverers keeps that
  property (for example by taking the binding's lock before it reads the receipt's time),
  which P11 carries. The delivered `message_submitted` events are the order's record, so
  an outbox retention rule must keep them, or a later migration moves the acceptance time
  onto the submission.
- **Only text Glow sent is shown** (DM-22 2.1). The provider adapters return a message's
  text only for a `regular` message with no deleted marker. The read shows a returned
  text only if `sha256("{match_id}\n{contact_version}\n{text}")`, from the binding's match,
  the row's `contact_version` and that text, equals the row's `request_digest`
  (`glow_domain.chat.request_digest`, the send's own). Anything else is "unavailable", one
  state with no reason, and counted in the read's result (missing, mismatched, and IDs the
  provider returned unasked) for P11's reconciliation metrics; a read writes no row (2.3).
  A provider error refuses the read with its Glow code, the retryable
  `provider_unavailable` for an outage (2.4). No message text reaches a log line (2.5).
- **The page cursor** is opaque (a version, the direction, the match ID and the boundary
  message's submission ID, base64url-encoded behind a `c`), carries Glow's identifiers
  only, and is bound to its match: a cursor whose match is not the request's, or whose
  boundary is not an accepted message of that match's binding, is refused
  (`cursor_invalid`; DM-22 6.4).
- **The conversation list** reads, for the session's account, every `active` `Match` it
  belongs to, then locks `FOR SHARE` every account those matches name and the account's
  own, in UUID order, then those matches, then the session, the canonical order every
  writer follows (accounts, then matches, then the session). It makes the session's checks
  (the account `active`, the session `valid`, unexpired and at the account's epoch) and,
  for each conversation, the per-match checks (the match still `active` with its pair, the
  other account `active`, no block either way, both profiles and both consents); a
  conversation that fails them is not listed. For each it reads the reader's
  `ChatReadCursor` and counts the other member's accepted messages after it (6.3), and
  takes the latest-message marker over the accepted messages and the reader's own pending
  or failed submissions (6.1): the submission ID and its time, no text. No provider is
  called. At most 200 conversations, the latest activity first.
- **The read-cursor command** makes the same checks in one transaction, then requires the
  target to be an accepted message of the match's binding, locks the reader's own
  `ChatReadCursor` row (`FOR UPDATE`, created first if absent, under a savepoint so a
  concurrent creation is read rather than failed), and moves `last_read` only forward in
  acceptance order; a repeat or an earlier target changes nothing. It is the only one of
  the three that writes, and it writes only that row. The other member's cursor is never
  read for a member or returned.

## Erasure, retention and restore

Retention categories and unresolved A05 decisions are governed by
[initial privacy and safety rules](privacy-and-safety-rules.md). No null deadline
means retain forever, and no missing policy authorizes a completed-purge claim.
Operational launch remains blocked on an approved category schedule and owners;
P02 static design can proceed without choosing durations.

Hard purge is deliberate after immediate revocation. Record tombstone, required
provider obligations and preserved restricted evidence first. Delete/detach
`EngineIdentity` before its `BirthInput` target because that FK uses `PROTECT`.
Delete app-private dependent rows in their reviewed order; remove `AppAccount`
before its protected auth user. Delete auth/allauth state through maintained
library lifecycle behavior, not raw guessed table names. Safety references use
`SET_NULL`; their preserved marker, descriptions and evidence remain restricted
under the actual retention decision. Provider deletion steps/tombstones protect
the deletion job so ordinary cascading purge cannot erase obligations.

Restore runs in isolation: deny user traffic, replay tombstones and revoked access,
reconcile processor steps, then verify no deleted account/session/device/channel
can regain access before opening the restored target. Backup configuration alone
does not establish this behavior. Cross-row subject equality, required provider
step completion and actual retention exceptions must be checked before marking
deletion complete.

## What static checks establish

`python -m glow_persistence.static_check` checks Django model metadata and exact
committed migration/model state equality using `MigrationLoader(connection=None)`.
Tests check outbox-before-domain ordering, identity delegation, tombstone FK
behavior as declared, pair/version constraints, wire field bounds and isolation
from the fixture API registry. They block connection/cursor/schema calls.

These results establish no SQL syntax acceptance, enforced database constraint,
atomic repository, actual allauth behavior, index performance, provider purge,
encryption configuration or restore outcome. (P06.DB's and P06.2's disposable-database
runs apply the migrations to PostgreSQL and exercise the chat adapter's transactions
there; they are proofs on a throwaway database, not P11's acceptance.) The exact remaining cases are
[DB01–DB13, PV01–PV08 and PR01](../testing/p11-deferred-acceptance.md).
