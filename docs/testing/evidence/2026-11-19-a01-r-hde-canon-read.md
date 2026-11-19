# A01-R — HDE's canon read against the contract request: evidence record

- **Work ID:** A01-R (research; M09's O3; OD-75 D-01 (a); OD-78). **Brief:** [`docs/planning/a01-r-hde-canon-read.md`](../../planning/a01-r-hde-canon-read.md).
- **Session:** the HDE canon research session, started by Nathan on 19 November 2026. **Prompt:** revision 1, from commit `06e8cec71c0b158bb5b50880e28061df277fa5ce` of the manager branch `claude/magical-wozniak-yfmmx2`.
- **What was read:** `amthorn78/glow-docs`, `docs/hde/pfcanon/`, at commit **`71a008fcb5cc0d453a20b8d6edaee02faaca44d9`** (`main`, 19 November 2026 01:55 UTC), read-only. Every canon citation below is at that commit.
- **What this is not:** it is not HDE's contract, and it decides nothing. HDE decides its contract (PF00), and Nathan schedules HDE's work in HDE's own process. Under OD-79 HDE *"is still under development"*, so this is a dated snapshot of the canon.

## Summary for Nathan (one page)

**What HDE already has.**
- **The pair read is specified, built and deployed.** `POST /api/reader?v=1` returns the Harmony band, and `?v=2` returns all ten categories. Each category comes as a band (Cool, Open, Warm or Glow), with no numbers.
  - It runs on Railway: project `ample-illumination`, service `glow-hdengine-v2`.
  - It has answered over live HTTP against the production database, but only for HDE's two synthetic test people, SYN-A and SYN-B. HDE's own QA did this on 1 November 2026 and in the HDE-EPIC042 QA.
  - It has never been run for a real member.
- **The answer is the same in both directions:** A with B gives the same result as B with A. It identifies itself with `reader_version`, `meta.engine_tag`, `meta.invocation_tag`, `release_id` and `idempotence_hash`.
- **A way to turn birth details into a stored chart is built, but only as an operator command,** `hdctl bg:resolve --source vendor --upsert`. It takes a date, a time (`HH:MM`, required) and a free-text place, calls the chart vendor (HumanDesignAPI), and stores the result. HDE used it to store SYN-A and SYN-B in production.
- **Logging rules are strict:** no birth data and no user identifiers in logs.

**What HDE does not have, which the prototype needs.**
1. **A sanctioned way to create a real member's chart.** HDE's canon forbids writing member charts to production *"until a Glow App user model exists and a future epic explicitly re-opens user-bound upsert flows"* (PF05 §4.6). No such epic exists yet. The operator HTTP route it specifies (`POST /_ops/bodygraph/resolve`) is not built, and it carries no birth details.
2. **Any authentication for an app calling HDE.** The Reader is catalogued as public. The canon specifies no credential for it, and no credential for any write.
3. **A test environment.** HDE has one deployment, and every HDE environment points at the one production database.
4. **A decided way for the app's server to reach HDE.** The canon names only the public Railway address. It says the app-to-HDE transport *"is not decided here"* (PF02).

**Build order I would propose for the prototype** (each item is detailed in section 5.1):
1. **Your decision in HDE's process** to end HDE's "no app users in production" posture and open member chart writes. The canon requires *"a future Coagulation epic"* for this (PF09.7 HDE-COAG005).
2. **An app-callable chart-creation operation and app-client authentication, together.** Either one Epic built from the deferred Coagulation rows (HDE-COAG003.8, .9 and COAG005's forward plan) plus new rows, or a CRD with an ADR (PF06 §0.1A, §1.0.5).
3. **The deployment that carries it.** HDE's current Epic, HDE-EPIC043 (the Magic10 v2 cutover), changes what the bands mean and has not deployed yet. Building the prototype after its deployment (WU-OPS-01) avoids building against bands that are about to change.
4. **A test environment, or an agreed protocol for synthetic test members,** for the app's checks.

**What you must decide in HDE's process.**
- Whether to end the no-user posture (D-A).
- Whether the work runs as an Epic or a CRD (D-B).
- Who creates a member's HDE identifier: the app, as a UUID that is not its account ID, or HDE (D-C).
- Test environment or synthetic protocol (D-D).
- The network path: public address with a credential, or Railway's private network (D-E).
- Whether the prototype waits for the Magic10 v2 deployment (D-F).
- Whether the prototype shows HDE's narrative text or bands only (D-G).

**Before launch,** HDE's canon has nothing on deletion, export, consent withdrawal, change notices, processor role or data region, and no rate limit for the Reader (section 5.2).

## 1. Identity, environment and start gate

### 1.1 Environment check (names only; no value was read)

| Check | Result |
|---|---|
| `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` | none set |
| `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*`, `RAILWAY_*` | none set |
| `AWS_*` names (OD-76) | `AWS_ACCESS_KEY_ID`, `AWS_CA_BUNDLE`, `AWS_SECRET_ACCESS_KEY` present; never read or used |
| GitHub token names | `GH_TOKEN`, `GITHUB_TOKEN` present; never read |
| glow-docs | **Not attached at session start.** There was no `/home/user/glow-docs`, and a filesystem search found no copy |

**How glow-docs was attached.**
1. I stopped and reported, as the prompt requires.
2. Before stopping, I had tried to attach the repository read-only. The session's permission classifier denied it.
3. Nathan then wrote in the session: *"Clone the repository amthorn78/glow-docs into this session."*
4. I attached it read-only with `add_repo`, shallow-cloned it to `/home/user/glow-docs`, and recorded `git rev-parse HEAD` = `71a008fcb5cc0d453a20b8d6edaee02faaca44d9`.
5. Nathan answered *"yes"* to proceeding with A01-R.

Nothing was written to glow-docs, and its own instructions and skills were not followed (OD-74).

### 1.2 Start gate

| Check | Result |
|---|---|
| `git rev-parse HEAD` after `git switch -C claude/fervent-sagan-afkke2 06e8cec…` | `06e8cec71c0b158bb5b50880e28061df277fa5ce` |
| Prompt commit on the live manager branch | yes (live head `8a11ede`) |
| PR55's merge `d3273f3` present | yes |
| Existing `a01-r-` records | 0 |

The two manager commits after the prompt (`0c3b1f2` and `8a11ede`) change only the handoff and the owner-direction register: they add OD-79. So the prompt was not stale. OD-79 is used here in two places: HDE is "still under development", and the app's database goes on HDE's existing PostgreSQL service.

### 1.3 Method

Five read-only research subagents each took a group of questions or documents (C01–C08; C09–C13 and C22; C14–C21, C23 and C24; C25–C35; HDE's process and state).
- I read PF05 §§1, 4.6, 4.7, 4.9.6, 5.1–5.3, 5.6, 5.9, 7.2.3, 7.3, 7.4 and 10 myself.
- I checked a sample of every subagent's quotes against the text with `sed -n` at the cited lines. I corrected line numbers where they were off; for example PF05 §3.2's lines are 213, 215, 225, 245 and 249.
- No HDE route, CLI, service or database was called. No provider, Railway or database was contacted.

### 1.4 Canon documents cited, and their versions

All are at glow-docs `71a008f`, under `docs/hde/pfcanon/`. "L" means a line number in that file.

| Short | File | Version |
|---|---|---|
| PF01 | `PF01-Canon-HDE-Math-Spec-v1.3.11.md` | v1.3.11 |
| PF02 | `PF02-Canon-HDE-Architecture-v2.4.9.md` | v2.4.9 |
| PF04 | `PF04-Canon-HDE-Governance-v2.8.13.md` | v2.8.13 |
| PF05 | `PF05-Canon-HDE-CLI-API-Vendor-Ref-v2.5.7.md` | v2.5.7 (effective 2026-11-16) |
| PF06 | `PF06-Canon-Change-Process-Guide-v2.5.8.md` | v2.5.8 |
| PF07 | `PF07-Canon-Glow-Infrastructure-v2.3.7.md` | v2.3.7 |
| PF09.4 / .5 / .6 / .7 | the Conjunction / Fermentation / Distillation / Coagulation build checklists | v1.3.6 / v1.6.6 / v1.1.13 / v1.1.13 |
| PF10 | `PF10-HDE-Build-Notes-v14.5.3.md` | v14.5.3 |
| PF12 | `PF12-Canon-HDE-Schemas-and-Artifacts-v2.9.11.md` | v2.9.11 |
| PF14 | `PF14-Canon-HDE-Mechanics-Guide-v3.5.12.md` | v3.5.12 |
| PF15 | `PF15 HDE Copy Tonality Guide v1.2.0.md` | v1.2.0 (Reference) |
| PF16 | `PF16-Canon-HD Engine Epics Map v2.3.8.md` | v2.3.8 (deprecated; historical) |
| PF17 | `PF17-Canon-HDE-Narratives-Guide-v1.5.4.md` | v1.5.4 |
| PF19 | `PF19-Canon-Glow-QA-Guide-v3.0.10.md` | v3.0.10 |
| PF20 | `PF20-Reference-HDE-Phased-Epics-v1.9.8.md` | v1.9.8 ("Historical reference only. Not for planning.") |
| PF29 | `PF29-Canon-HDE-Users-Guide-v1.0.6.md` | v1.0.6 |
| PF31 | `PF31-Reference-HDE-State-of-the-Repository-v0.1.md` | v0.1 (15 Sep 2026, snapshot `9cda1b49`; stale) |

**Markings** (from the brief):
- **specified:** the canon states it as contract or design.
- **built:** a build-notes, checklist, state-of-repository or audit record says it exists in HDE's code.
- **proven live:** a record shows it working against HDE's real database over HTTP.
- **not in the canon.**

PF05's own status tags are `[Implemented]`, `[Required-Now]` (*"if missing in code, it is a gap to close"*), `[Speculative]` and `[Required-When-Landed]` (PF05 §0.3, L30–36).

## 2. The questions, C01 to C35

### 2.1 Identity, release and environments

| ID | The canon's answer | Marking | Citation |
|---|---|---|---|
| C01 | **The contract is the Reader:** one route, `POST /api/reader`, with Reader v1 (`v=1`) and Reader v2 (`v=2`) selected by exactly one `v`. Both use one closed six-key envelope.<br><br>**Changes that need a new Reader version:** any change to the public shape. PF04: *"Any proposal beyond the existing v1 or v2 contract **MUST** define the appropriate separately governed Reader version with updated schema, acceptance, and migration notes"*. And: *"Adding “optional” public fields under v1 is **prohibited**; clients and CI validate **strict equality**"*.<br><br>**Changes that do not:** math internals may change without a version bump but *"may change `release_id`"*.<br><br>**Notice:** no period of notice before a breaking change, and no deprecation window. PF29 says its drift notes do not *"create a deprecation window"*. | Versioning rule: **specified**. Notice period: **not in the canon** | PF05 §5.1.0 L2070; PF04 §13.1.3–13.1.6 L4506, L4514, L4529–4530; PF29 §2 L115 |
| C02 | **No single HDE release or commit is named as "the contract's".** Each response carries `release_id`, the hash of the release manifest.<br><br>**The current release** is manifest version `1.3.0`: 45 members, *"built_at_utc: "2026-08-24T18:04:49Z""*, `release_id` `2d5a4ec485fde5dd51004e0286fff1cb1211e4ee79fa71bc62b2a5ecd0b6c129`.<br><br>**Commit pins:** PF05 pins repository facts to several `main` commits, for example `e7265a09` for the Reader, and says *"Release admission and deployment remain distinct."*<br><br>**Coming change:** the Magic10 v2 cutover brings *"a new `release_id`"*. | Release rule: **specified**. 1.3.0 roster: **built** | PF12 L1962, L2032; PF05 §5.1.7 L2256–2260; PF04 §5.1 |
| C03 | **Production:** Railway project `ample-illumination`, service `glow-hdengine-v2`, `https://glow-hdengine-v2-production.up.railway.app`.<br><br>**Test environment:** none. *"Staging/QA (GitHub Codespaces)"*, and its HD Engine row is *"TBD \| TBD \| **Shared production DB instance**"*. *"All environments point to the **same database instance**"*.<br><br>**Live-call protocol:** the one protocol for live calls is HDE's own deployed-service check against SYN-A and SYN-B. These are two synthetic people stored in production under fixed UUIDs. Each live step needs *"task-specific Product Owner authorization … a defined request limit, explicit step-local rails, synthetic inputs, redaction"*. | Production: **specified**, **proven live** (synthetic). Test environment: **not in the canon**. SYN protocol: **specified**, **proven live** | PF07 §2.1 L148–150, §2.2 L158, L174, L183; PF04 §3.4 L1202, L1218; PF20 §2.28.5 L11772–11773 |
| C04 | **Each Reader success body carries:** `reader_version`; `meta` = exactly `{engine_tag, invocation_tag}`; `release_id`; `idempotence_hash`.<br><br>**Errors** carry `schema:"v1"`, which is *"`error_v1`, not the selected Reader success version"*.<br><br>**Running-engine identity:** the authoritative source is the ops route `/internal/version`, with six fields (`engine_tag`, `build_commit`, `invocation_tag`, `invocation_sha256`, `emitter_sha256`, `release_id`). It is *"operator-network-only"* (C24). | **specified**. Reader body fields and `/internal/version`: **proven live** (EPIC042 qa-06, qa-07) | PF05 §5.1 L2053–2066, §5.1.6 L2252, §5.1.5 L2203; PF04 §10.5 L4039, L4065–4075; PF20 L11772 |

### 2.2 Access

| ID | The canon's answer | Marking | Citation |
|---|---|---|---|
| C05 | **No authentication mechanism is specified for `POST /api/reader`.**<br>- Its catalogue record is *"`classification: public_reader`, `internal: false`, `env_gate: not_applicable_public`"*.<br>- The response's `Vary: Authorization, Accept-Encoding` is a caching header, not a scheme.<br>- PF29's example call sends no credential.<br><br>**The only authentication the canon specifies is for the admin bundle:**<br>- *"`Authorization: Bearer <HDE_ADMIN_TOKEN>`"*, a `<key-id>.<secret>` token checked against a server registry of SHA-256 digests with scopes.<br>- Client classes are *"exactly one of `hdctl`, `admin_gui`, or `automation`"*.<br>- PF04 adds that admin credentials *"MUST NOT be shared with end users or application-level identities"*.<br>- That admin route is *"Required-Now; not implemented"*. | Reader authentication: **not in the canon**. Admin scheme: **specified** only | PF12 L4830; PF05 §5.1.0 L2078, §4.9.6 L1340–1398, §1 L95; PF29 §6.4 L379; PF04 §8.3.3 L2363 |
| C06 | **Reads:**<br>- `POST /api/reader` with exactly `{a_id, b_id}`. *"Inline charts, Gates, weights, profiles, bands, configuration IDs and viewer preferences are prohibited."*<br>- `GET /aux/narrative?v=1` for narrative text (C17).<br>- *"app integrations continue to go through Reader and Aux contracts"*.<br><br>**Writes:** no write is specified for an app.<br>- The ops route `POST /_ops/bodygraph/resolve` is *"Internal operator surface; **not** a Catalog success route and not public"*, and was not found in the repository.<br>- Production member writes through the CLI are prohibited (C11, C12).<br><br>**Forbidden:** development routes, `/api/compat/v1` (internal admin, production-excluded), the admin bundle, and direct app calls to HumanDesignAPI. PF02: *"Direct Glow app HumanDesignAPI calls, app-owned raw BodyGraph persistence, parallel vendor clients, parallel credential paths … require a future ADR"*. | Reader: **specified**, **built**, **proven live** (synthetic). App write: **not in the canon** | PF05 §5.1.0 L2072–2074, §5.6 L2560–2563, §5.9 L2749–2758; PF09.7 HDE-COAG006 L1588; PF02 L1504–1506 |
| C07 | **HDE is deployed** on Railway at the public address above. It is deployed from *"commits landing on `main` of `amthorn78/glow-hdengine-v2`"* and listens on port 8000.<br><br>**No app-to-HDE path is named:** no private-network hostname and no service-to-service path. PF02: *"The exact integration transport between the Glow app and the HD Engine is not decided here and remains future architecture or implementation scope."* PF07: *"Glow app integration should consume HD Engine outputs through a controlled integration surface"*.<br><br>The app's [ADR 0002](../../adr/0002-same-project-application-services.md) puts the app in the same project, `ample-illumination`. Railway's private network spans one project environment, and PF07 records only `production` for HDE. | Deployment: **specified**, **proven live**. Network path for the app: **not in the canon** | PF07 §3.1 L590–592, §4.1 L648–652, §8.2.1; PF02 L975, L1506 |
| C08 | **For admin credentials only:** *"Rotation needs no code change: add a new key, distribute it, then remove the prior key through the managed secret configuration. Revocation takes effect when the new configuration is atomically applied"*. Each operator or service gets its own key ID. PF07 lists `HDE_ADMIN_TOKENS` and `HDE_ADMIN_SCOPES` as *"OPEN/TBD"*.<br><br>**Not in the canon:** who issues a credential, a procedure for a compromised credential, and any credential for an app client. | Admin rotation: **specified**, not built. App credential: **not in the canon** | PF05 §4.9.6.2 L1394; PF04 §8.3.2 L2356–2357; PF07 L1190 |

### 2.3 Birth input and chart identity (`BirthInput` / `ChartResolver`)

| ID | The canon's answer | Marking | Citation |
|---|---|---|---|
| C09 | **Fields:** the built vendor request takes exactly a local civil date (`YYYY-MM-DD`), a local time (`HH:MM`, *"seconds and a timezone suffix are forbidden"*) and one free-text `location` of 4–200 characters.<br><br>**Time zone:** *"No request contains `tz`. The vendor derives timezone from the governed route input. PF05 does not manufacture, infer, or repair timezone data at this boundary."* HDE sends the geocoding key so the vendor can geocode the place.<br><br>**HDE-side algorithm (not built):** PF05 §3.2 specifies an override, then the stored IANA zone, then a zone derived from the location through *"a sanctioned resolver with pinned data provenance"*. It is a *"Required-Now implementation gap"*: *"No `--a-tz` or `--b-tz` parser option, end-to-end source precedence, UTC-instant resolution … was found"*.<br><br>**Coordinates route:** exists in the contract but *"is not resolver-selectable"*. | Three-field request: **built**. HDE time-zone algorithm: **specified** only. The vendor's geocoder: **not in the canon** | PF05 §7.2.3 L3713–3732, L3722; §3.2 L213, L215, L249; §1 L125 |
| C10 | **No unknown-time mode, approximate-time mode or rectification.** The full tuple is required: *"MISSING_VENDOR_INPUT \| Vendor source was requested without full birth tuple."*<br><br>**Specified only, not built:**<br>- *"A fold MUST fail with `ERR_LOCAL_TIME_AMBIGUOUS`; a gap MUST fail with `ERR_LOCAL_TIME_NONEXISTENT`"*.<br>- *"`ERR_LOCATION_AMBIGUOUS` \| The birth location does not resolve uniquely enough to select one timezone"*.<br>- *"PF05 MUST NOT use UTC, process `TZ` … as a person's birth timezone."*<br><br>**On the built path:** an unusable place surfaces only as a provider error. There is *"no AI transformation, heuristic location correction, timezone guess, or fallback body"*. | Full tuple required: **built**. Ambiguity, fold and gap refusals: **specified**. Uncertain time: **not in the canon** (not supported) | PF29 L1021; PF05 §3.2 L215, L225, L235; §4.9.4.3 L1315; §7.2.3 L3734 |
| C11 | **Key:** charts are keyed by `user_id` with `vendor = 'hdapi'`. The Reader requires *"an exact lowercase canonical hyphenated RFC 4122 UUID"* and performs no *"arbitrary-string UUID5 conversion"*.<br><br>**The CLI key:** `--user <id>` is the *"engine user key. In the long run it is expected to align with a Glow App user ID; in pre-Glow prod QA it is used as an **ephemeral QA key**"*.<br><br>**No HDE users table exists** (PF07's `hde` tables are `meta`, `public_results`, `body_graphs` and the current view). No contract says who creates the identifier. The only production identifiers are HDE's own `uuid5` fixture IDs for SYN-A and SYN-B. | UUID keying: **built**, **proven live** (synthetic). Who creates it: **not in the canon** | PF05 §5.1.0 L2072–2074, §4.6 L957; PF07 §7.2.1 L1001–1004; PF04 L1202 |
| C12 | **Idempotence:** the built write is idempotent: *"repeated writes for the same normalized identity do not create duplicate or divergent cache rows"*. It also verifies one row and canonical read-back. But `hde.body_graphs` has no primary key: *"recorded technical debt … on (user_id, vendor, vendor_version, input_fingerprint)"*.<br><br>**Current view:** `body_graphs_current` is the *"view of latest valid per user/vendor"*.<br><br>**Corrections:** what a birth-input correction does is never stated. "Birth-data change" is named only as a trigger for a vendor call. The `input_fingerprint` recipe is not defined. | Write idempotence: **built** (HDE-DIST001.11 Done). Current view: **specified**. Correction semantics and fingerprint recipe: **not in the canon** | PF09.6 L919–922, L975; PF12 §8.7 L4789; PF07 L1002–1003; PF05 §7.4 L3937 |
| C13 | **No pending state, job or completion signal.**<br>- The CLI write is synchronous. Success is *"status=ok"* with *"rows_written, rows_after, read_back_match, and idempotent"*.<br>- The Reader answers a missing chart with `404 ERR_M10_PERSON_UNRESOLVED`.<br>- The vendor call is bounded by `total_timeout_ms ∈ {5000,10000,15000,30000}`, with a default of 3 attempts (exponential backoff, 500 ms, ceiling 2000 ms).<br>- *"Production calls — Speculative."* | CLI: **built**. Timeouts: **specified**. Pending state and latency: **not in the canon** | PF29 §11.4 L740; PF05 §7.3.2 L3825–3835, §7.3.4 L3861, §1 L133, §5.2 |

### 2.4 Compatibility output (`CompatibilityProvider` / `CompatibilityProjection`)

| ID | The canon's answer | Marking | Citation |
|---|---|---|---|
| C14 | **Single pair only:** one request with *"exactly `a_id` and `b_id`"*, body at most 32,768 bytes.<br><br>**No production batch, candidate set or ranking route.** Candidate ranking exists only in the dev sampler (*"a non-public tool for engine developers and admin operators"*, environment-gated to dev, test and local). | Single pair: **built**, **proven live** (synthetic). Batch: **not in the canon** | PF05 §5.1.0 L2072, §4.10.1 L1840, §1 L85 |
| C15 | **Output:** six keys. Categories are exactly `{id, band}`, with `band ∈ {"Cool","Open","Warm","Glow"}`. v1 returns `harmony` only; v2 returns ten categories in the fixed order harmony, heat, communication, alignment, comfort, consistency, expansion, creativity, drive, balance.<br><br>**Band thresholds:** Magic10 v1 thresholds on an internal 0–100 score are *"`[24,49,74,100]`"*, with order *"`Cool < Open < Warm < Glow`"*.<br><br>**Meaning:** PF01: *"It does not assert empirical compatibility effect sizes, relationship quality … ranking, or outcome prediction."*<br><br>**Finer ordering:** none is authorized for a consumer. *"Richer compat JSON (including numeric scores …) is restricted to **admin/test artifacts**"*; *"Numeric public output requires a separately approved PF05, PF17, schema, and narrative change."*<br><br>**Magic10 v2 (not yet deployed):** makes bands *"relative and per category"*, with a target mix of 30/35/25/10. | **specified**; envelope and v1 thresholds **built** | PF05 §5.1.2, §5.1.6; PF01 §5.2 L595, §5.3 L1102–1107, L1118, §5.3.7 L1161–1163; PF17 §5.1 L996 |
| C16 | **The Reader is symmetric:** *"identical preimages and identical final version-selected Reader envelope bytes for `{a,b}` and `{b,a}`"*. Errors do not depend on order either.<br><br>**Narratives are directional:** *"swapping A and B maps `a_to_b` to `b_to_a` … but the two directional results need not be equal"*. Orientation is fixed by `(gate_mask, canonical_person_id)`, not by request order. | Reader symmetry: **proven live** (synthetic). Narrative direction: **specified** | PF05 §5.1.4 L2163, §5.2, §5.1.0 L2076; PF17 §1.2 L155; PF09.4 L2177 |
| C17 | **Users may see:** Reader bands, and Aux narrative text (*"canonical public narrative surface"*).<br><br>**Narrative rules:**<br>- The shared paragraph goes to both people.<br>- Each person sees only their own private paragraph: *"A sees **Private-to-A** only through a request with `perspective=b_to_a`"*.<br>- *"**Never** show a user the other party’s private paragraph."*<br>- If the shared check fails, *"neither viewer sees the match for that Top Category."*<br><br>**Copy:** *"band-only, felt-only, and symmetric on the shared surface"*.<br><br>**Internal only:** scores, narrative keys, admin and sampler output.<br><br>**Not proven:** Aux is not proven live. At `aa58e93d` the code did not enforce the `v` gate. | **specified**; Aux routes **built** with a recorded defect | PF17 §1.3 L186, L193, L195, §2.4 L347; PF05 §5.6 L2563, §5.7; PF15 L11 |
| C18 | **Eligibility is only about whether a pair can be computed.** It is false *"exactly when both records have the same `canonical_person_id` and byte-identical complete normalized projections"*: a person paired with themselves. Any two distinct people are eligible.<br><br>*"Eligibility is not a sampler, ranking, viewer-preference, preset, moderation, consent, blocking, product-access, score, band, or relationship-state predicate."* Magic10 v2 leaves it unchanged. | **specified**, **built**; eligible branch **proven live** (synthetic) | PF01 §4.1 L479–486 |

### 2.5 Reliability and throughput

| ID | The canon's answer | Marking | Citation |
|---|---|---|---|
| C19 | **The Reader has no specified rate limit, quota or throughput figure.** Its errors carry *"no `retry_after_ms`"*. It makes no request-time vendor call.<br><br>**Vendor 429s** map to `PROVIDER_RATE_LIMITED` and are not retried. *"`VENDOR_RATE_LIMIT` — OPEN/TBD"*.<br><br>**Server:** the checked-in start command runs Gunicorn with *"2 workers, 4 threads, and a 30-second timeout"*. The live Railway setting is not verified. | Reader limits: **not in the canon**. Vendor 429 mapping: **built** (closed rails) | PF05 §5.2 L2284, §7.3.5 L3869; PF07 L1176, §10.1 L1382 |
| C20 | **Reader targets:** *"p95 `<= 300 ms`; p99 `<= 750 ms`"* and *"Availability at least `99.5%`"*. These are requirements: *"They do not claim that the pinned repository, a dashboard, or a deployment currently implements or attains them."*<br><br>**Vendor timeouts:** as in C13. | **specified**; not measured | PF04 §6.2 L1894, L1914–1915 |
| C21 | **Reader errors** (the four-key `error_v1` body, `no-store`):<br>- `400 ERR_READER_INVALID_VERSION`<br>- `422 ERR_READER_INVALID_INPUT`<br>- `422 ERR_READER_INVALID_CHART`<br>- `404 ERR_M10_PERSON_UNRESOLVED`<br>- `503 ERR_M10_RESOLVER_UNAVAILABLE`<br>- `503 ERR_M10_BODYGRAPH_INCOMPLETE`<br>- `503` config, manifest, result-schema and stale-result mismatches<br>- `405 ERR_NOT_FOUND` for any non-POST method, and `404 ERR_NOT_FOUND` for an unknown path<br><br>**Client retry:** no client retry policy is given. The only retry policy is HDE's own outbound one: *"Automatic retry classes are exactly `network_error` and HTTP `5xx`"*. | Errors: **built** (loopback-tested). Client retry policy: **not in the canon** | PF05 §5.2 L2298–2338, §7.3.3 L3843; PF19 L5401 |
| C22 | **Reader:** *"`idempotence_hash = sha256(preimage_bytes)`"* over `reader_version`, `eligible`, `categories`, `meta` and `release_id`.<br><br>**Writes:** idempotent by normalized identity, with a 64-hex `input_fingerprint`. | Reader hash: **specified**, **proven live** (*"the preimage recipe holding on all nine live Reader bodies"*). Writes: **built** | PF05 §5.1.3, §6.3 L3317; PF09.6 L922; PF09.4 L2223 |
| C23 | **No batch exists,** so there is no partial batch. One Reader call is all or nothing: *"An incomplete or invalid result fails closed rather than producing a partial success."* | **not in the canon** (no batch) | PF01 §2.5 L299 |
| C24 | **No health or status signal for a client.**<br>- `/internal/version` is *"an **ops-only identity route**"* with *"**no application-layer auth**"*, *"operator-network-only"*.<br>- `/internal/healthz` and `/internal/readyz` are specified, but at `cc754cf` were defined only *"in the alternate `adapter/wsgi.py` factory, not in the selected factory"*. | Client health signal: **not in the canon** | PF04 §10.5 L4031–4040; PF02 §3.4 L944; PF09.7 HDE-COAG001.8 (Partial) |

### 2.6 Data rights: caching, retention and deletion (`EngineLifecycle`)

| ID | The canon's answer | Marking | Citation |
|---|---|---|---|
| C25 | **Reader headers:** success sends *"`Cache-Control: private, max-age=0, must-revalidate`"*, no `ETag`, and *"Production POST ignores `If-*` conditionals and never returns `304`"*.<br><br>**Client storage:** no period or right is stated for what a client may store.<br><br>**What signals change:** `release_id` changes with a new release cut, and threshold changes mean *"a new manifest cut and a new `release_id`"*. The Magic10 v2 cutover will change bands under the same shapes. | Headers: **specified**, **built**. Client storage rights: **not in the canon** | PF05 §5.1.0 L2078; PF14 §7.3 L1925; PF05 §5.1.7 L2260 |
| C26 | **HDE owns:** vendor acquisition, chart storage and computation. The app *"must not create a parallel HumanDesignAPI client … or direct app-side raw vendor persistence path"*.<br><br>**What HDE stores:** *"body_graphs: durable BodyGraph rows (vendor, version, input_fingerprint, payload, created_at, refreshed_at, ttl_at)"*, plus `user_id`. The stored payload is mapped, *"never a raw HumanDesignAPI v2 envelope"*. No raw birth-data table is defined.<br><br>**Write isolation:** *"Only Engine roles can mutate `hde.*`"*.<br><br>**Today:** *"No persistent user-bound BodyGraphs exist in production other than the two synthetic Live QA fixtures"*. | Ownership: **specified**. Tables: **built**. App's data rights: **not in the canon** | PF04 §11.1 L4230, §2.0.9 L548; PF07 §7.2.1 L1001–1002; PF05 §7.4 L3945; PF14 §17.10 L3187 |
| C27 | **No deletion or erasure operation exists.**<br>- The only retention work, *"Data retention jobs. Policy-driven deletes/archives"*, was in HDE-EPIC011, which *failed*.<br>- `HDE_APP_ROLE` may DELETE only from `hde.public_results`. | **not in the canon** | PF16 L264, L282; PF20 L248; PF07 §7.0 L949 |
| C28 | **No shared-chart concept exists.** Rows are per user and vendor. | **not in the canon** | PF02 L652 |
| C29 | **Logs carry keys only:** *"No birth data. Never log birth details or any BodyGraph input fields."* Also *"API keys, tokens, user identifiers, free-text inputs, or locations are not logged."*<br><br>**On a leak:** *"halt affected jobs, rotate credentials if applicable, and purge offending logs per policy."*<br><br>**Audit records** exclude birth date, time and location. | **specified**; vendor-path redaction **built** (HDE-FERM001.3 Done; tested without live vendor calls) | PF04 §7.1.1 L2064, §7.1.6 L2104, §8.2.4 L2327; PF05 §7.1.11f L3645; PF09.5 L484–486 |
| C30 | **No webhook, callback or event exists.** Refreshes happen *"**out-of-band**"*. A client can detect change only by reading again and comparing `release_id` and `idempotence_hash`; the canon does not prescribe that. | **not in the canon** | PF02 L658; PF05 §7.4 L3937 |
| C31 | **No export operation exists.**<br>- The admin bundle is for *"an Admin GUI and other internal tools"*, takes birth data as input, and is not built.<br>- The by-identifier ops route is not built. | **not in the canon** | PF05 §5.10.1 L2765, §5.9 L2758 |
| C32 | **Deletion replay:** there is no deletion to replay.<br><br>**Backups:** backup and restore rehearsal were scoped in failed HDE-EPIC011. They run *"by OPS via the Railway UI … There is no dedicated CI job"*. No record of a run, and nothing tells a client that a deleted chart came back. | **not in the canon** | PF16 L280; PF07 §7.3.1 L1052 |
| C33 | **Nothing on consent withdrawal.** PF01 routes consent *"to their owning documents"*, and no document owns it. | **not in the canon** | PF01 §4.6 L538 |
| C34 | **Birth details go to the vendor:** date, time and place go to HumanDesignAPI at *"`https://api.humandesignapi.nl/v2`"*, with the geocoding key.<br><br>**Results are stored** in project `ample-illumination`, schema `hde`, on one instance that every environment shares: *"a shell labeled dev can write to the production database"*.<br><br>**Not stated:** the region, and whether HDE is a processor or controller. | Vendor flow: **specified**, **built**, **proven live** (synthetic). Region and processor role: **not in the canon** | PF05 §7.2 L3682; PF07 §8.2.1 L1270, §2.2 L173, L181, L189; PF09.6 L981 |
| C35 | **Production** is the Railway service above; development and QA hosts are TBD.<br><br>**Identity:** `/internal/version` gives identity; *"build_commit is optional in production and may be unset/null"*. HDE's check compares the deployed `release_id` with `main`: *"A match shows neither the deployed commit nor that HDE-EPIC042 code is deployed."*<br><br>**Not defined:** a Railway deployment-ID field. | Identity contract: **specified**. Release match: **proven live** | PF04 §10.5, L1201; PF14 §31 L4781; PF20 L11772 |

## 3. Conflicts between the canon and the app's plan

1. **Sign-up chart (OD-61) against HDE's production write ban.**
   - **OD-61:** *"the human design chart is calculated immediately when someone signs up, there is no lag"*.
   - **PF05 §4.6:** *"`bg:resolve --source=vendor --upsert` **must not** be used in prod until a Glow App user model exists and a future epic explicitly re-opens user-bound upsert flows."*
   - **PF05 §3.7, L430:** *"We must not create app-like user records in prod ahead of Glow App integration."*
   - **PF09.7, L1485:** writes stay closed until *"a future Coagulation epic explicitly authorizes production or production-like upsert posture"*.
   - **PF02, L635–639:** *"Production request paths do not call the vendor inline. An explicit out-of-band refresh path owns any vendor request."*
   - **No speed guarantee:** the canon offers no "immediate" guarantee, and a vendor call may take up to a 30-second total budget.
   - **Resolving it** needs HDE work and Nathan's decision in HDE's process (D-A).

2. **The contract request's C10 against OD-61 and the canon.**
   - **C10 asks** how *"an uncertain or missing birth time"* is handled.
   - **OD-61:** *"birth time is required at signup."*
   - **The canon:** requires `HH:MM` and has no unknown-time mode (C10 above).
   - **So** the canon and OD-61 agree, and C10's uncertain-time part is answered "not supported".
   - **The app's own code still allows an unknown time.** `services/api/glow_domain/provider_contracts.py` has `TimePrecision.UNKNOWN` and `local_time: time | None`, with the rule *"Unknown time and supplied civil time must agree."* That is app-side work, not HDE's.

3. **The app's time-zone rule against HDE's built path.**
   - **The app** (contract request C10; seam): it *"never converts local time to UTC without a verified place and time zone"*.
   - **The canon:** *"No request contains `tz`. The vendor derives timezone from the governed route input."* HDE's own zone algorithm is an *"implementation gap"* (PF05 §3.2 L213), and the coordinates route *"is not resolver-selectable"*.
   - **Effect:** the vendor turns a free-text place into a zone and a UTC instant itself, and nothing carries an app-verified zone into HDE. The app can keep its rule on its side, by sending exactly what the member entered and never converting it, but the conversion is the vendor's.

4. **Band-only rule (PF01 §5) against HDE's output.**
   - **No conflict on the Reader:** it is *"Bands-only, no numerics"* (PF05 §10.1).
   - **PF15 (Reference status), L192:** *"If a Details view is tested, show position within band or a small percent with a rules label."* That would break the app's rule, and the app should not follow it. PF17 L996 also requires a separate approval for any public number.
   - **Admin surfaces carry numbers** (`showcompat`, the admin bundle, the sampler). The app must never use them.

5. **Direction (contract request C16; seam).**
   - **The app** keeps pair direction *"until symmetry is guaranteed"*.
   - **The canon guarantees it for the Reader** (PF05 §5.1.4 L2163). So the app may normalize Reader pairs, but must keep direction for narratives (PF17 §1.2 L155).
   - **Gap:** the public Aux query (`v`, `category`, `band`, `perspective`) does not say which member is "A". Orientation comes from the internal `gate_mask`, so the app cannot tell from the contract which `perspective` belongs to which member.

6. **Identity (seam; contract request C11) against PF05 §4.6.**
   - **The app:** *"An app account ID and an HDE chart ID are different identities with an explicit mapping."*
   - **PF05 §4.6, L957:** the engine key *"is expected to align with a Glow App user ID"*.
   - **Compatible either way:** the Reader takes any canonical UUID, so the app can use a separate UUID per member. Who creates it is D-C.

7. **The app's PF01 §5 snapshot against the canon.**
   - **PF01 §5** describes `POST /api/reader?v=1` returning a harmony band.
   - **The canon now also has v2,** with ten categories (PF05 §5.1.6). This is an update, not a contradiction.

8. **Test environment (contract request C03, §5) against PF07.**
   - **The request** needs *"A test environment, or an authorized test-data protocol"*.
   - **PF07:** HDE has no hosted test environment, and *"Production runs on one Postgres instance; staging/dev connect to the same physical instance"* (§7.1 L962).
   - **Under OD-79** the app's database is also on that service. So any HDE test write lands on the instance the app uses, though in HDE's own schema.

9. **OD-79's retirement analysis against PF07.**
   - **PF07** treats `glow-backend-v4` (Railway, same project and database) and `glow-frontend-v2` (Vercel) as Glow infrastructure beside HDE (§2.2).
   - **It never names** `glow-dating-app`.
   - **The retirement analysis** that OD-79 commissions should read PF07 §2.2. Retiring those components changes text that HDE's canon owns, so it belongs in HDE's process (D08).

10. **Inconsistencies inside the canon** (for HDE's process, not the app's):
    - PF04 §10.0 (L3902–3906) speaks of the Reader's catalogue row as *"present and A7-eligible"*, while PF05 §5.6 and PF10 (L874) say *"The production Reader, POST /api/reader, is not A7-eligible."*
    - PF16 says planning is owned by PF20, but PF20 says *"Historical reference only. Not for planning."*
    - PF04 §11.2.3 allows backoff values that PF05 §7.3.4's closed set does not.

## 4. HDE's process: where gaps would sit

- **Two kinds of change** (PF06 §0.1A L23–28):
  - *"**Epic lane.** Product-development work originating in or formally mapped to PF09"*.
  - *"**CRD lane.** Observed features, defects, operational needs, governance needs, and system changes originating outside PF09 … A canon-changing CRD requires an accompanying approved ADR."*
  - *"They do not differ in applicable development, QA, evidence, operations, or closure rigor."*
  - There is no hotfix lane.
- **Who chooses:** *"The Product Owner selects the class"* (PF04 §9.1 L2423). An approved Specification *"authorizes the required Implementation Audit and Implementation Plan preparation, not implementation"* (PF04 §9.1.1).
- **Phases:** every PR or Ops task belongs to one phase (PF06 §1.0.4 L1481). Deployment and integration rows sit in **Coagulation** (PF09.7).
- **The "future epic with the App user model"** has no ID. It exists only as deferred rows:
  - HDE-COAG003.8: *"DEFERRED → future epic with the App user model"* (L1318).
  - HDE-COAG003.9, user-bound live Reader verification, Not done (L1327, L1340).
  - HDE-COAG005's forward plan (L1517): *"Once the Glow App and user model are integrated, a future epic … will: Use real app user IDs to exercise DB-backed showcompat and bg:resolve --source vendor --upsert"*.
- **No PF09 row exists** for `/_ops/bodygraph/resolve`, app-client authentication, a test environment, or deletion. Its pointer *"Until IG-022 lands"* (PF05 §5.9) refers to an ID defined nowhere in the canon.
- **What HDE is building now:**
  - HDE-EPIC043, the *"Magic10 v2 Cutover"*, across five phases (PF10 addendum 2.1).
  - On 19 November its WU-PR-09 awaits the Product Owner's Proceed, and plan delta 03 is pending (`docs/ephemeral/HDE-EPIC043-*`).
  - Its deployment, WU-OPS-01, needs *"its separately approved Ops Task Record"* (PF10 2.1 R-3).
  - It includes HDE-COAG003.7 (authorized deployment) and excludes HDE-COAG003.8 and .9.
  - No EPIC044 or CRD-0004 record exists.

## 5. What HDE must still build for the app (proposals for Nathan)

### 5.1 For the MVP prototype (OD-78)

This is the least that lets the app's own adapter create a new member's chart and read a pair, against a deployed HDE the app's server can reach, with authentication and a test environment. The order is the proposed build order.

| # | Gap | Questions | What exists | Proposed place in HDE's process |
|---|---|---|---|---|
| P-1 | **Open member chart writes in production:** end HDE-COAG005's interim no-user posture, and define the "App user model" as HDE needs it (an app-supplied member UUID with one current chart row) | C06, C11, C12, C26; OD-61 | Forbidden until *"a future Coagulation epic"* (PF09.7 L1485; PF05 §4.6, §7.4 L3945) | Nathan's decision (D-A), recorded in HDE's Build Notes. Carried by the Epic formed from HDE-COAG003.8, HDE-COAG003.9 and COAG005's forward plan (Coagulation) |
| P-2 | **An app-callable chart-creation operation** that takes date, `HH:MM` time, place and the member's UUID, calls the vendor, stores the chart, and answers synchronously with a typed result and errors. It also needs the correction rule (same UUID, new current row?) | C06, C09, C11, C12, C13, C21, C22 | Built only as the operator CLI (PF29 §11.4). `POST /_ops/bodygraph/resolve` is specified but not built, has no birth fields (PF05 §5.9), and has no PF09 row. Transport *"not decided"* (PF02 L1506) | Within P-1's Epic, as new Coagulation rows (a PF09 change), **or** a CRD with an ADR, because it changes a contract (PF06 §1.0.5). D-B |
| P-3 | **App-client authentication** for the Reader and for P-2: a mechanism, scopes, issuing, rotation and revocation. The admin design (`<key-id>.<secret>` bearer, digest registry, scopes; PF05 §4.9.6) is a ready pattern with a new client class | C05, C08 | Reader: none. Admin: specified, not built (HDE-COAG006.5 Not done) | With P-2 (same change), or a CRD with an ADR |
| P-4 | **A deployment carrying P-2 and P-3, and a network path from the app's server:** the public Railway address with the credential, or Railway's private network in project `ample-illumination` | C03, C07, C35 | The Reader is deployed and proven on synthetic rows. HDE-EPIC043's deployment (WU-OPS-01) is pending | An Ops Task Record inside P-1's Epic (HDE-COAG003.7 pattern). Network choice: D-E. Timing after EPIC043's deployment: D-F |
| P-5 | **A test environment for the app's checks:** a separate HDE deployment and database, or a Product Owner-authorized synthetic-member protocol on production, extending SYN-A/SYN-B's pattern with a defined request limit and clean-up | C03 | None. One shared database (PF07 §7.1 L962). SYN protocol proven (PF04 L1202–1218) | A CRD ("operational needs", "infrastructure change"; PF06 §1.0) for a separate environment, or an Ops Task Record for the protocol. D-D |
| P-6 | **Stated version and notice terms for the app:** which Reader version the app uses, notice before a breaking change, and the `release_id` the app should expect after the Magic10 v2 cutover | C01, C02, C04, C25 | Versioning rules specified; no notice period | The ADR of P-2 or P-3, or a short CRD (canon text) |

The prototype also needs these clarifications, which the canon leaves open. Each could be settled in the same change:
- an error and retry policy for app callers (C21);
- what the app may store and for how long (C25);
- how a narrative request is tied to a pair, if the prototype shows narratives (C16, C17; D-G).

### 5.2 Before launch

| Gap | Questions | Proposed place |
|---|---|---|
| A deletion operation for a member's chart, with completion evidence and replay safety; what happens if HDE restores a backup | C27, C28, C32 | A CRD with an ADR (data rights are new canon) |
| Export of what HDE holds about a member | C31 | The same CRD |
| What HDE does when consent is withdrawn | C33 | The same CRD (PF01 L538 routes consent to an owner that does not exist) |
| Processor or controller role; where data is stored and processed (region); the vendor as a further recipient | C26, C34 | The same CRD; PF04 governance text |
| Change and deletion notices, or a stated polling rule | C30 | The same CRD |
| A Reader rate limit, quota and throughput the app can plan on; a measured latency against PF04's targets | C19, C20; A07 | Coagulation rows (HDE-COAG001.6 covers writers only); Distillation performance (HDE-DIST004 Not done) |
| A health signal a client may check | C24 | HDE-COAG001.8 (Partial) |
| Time-zone verification on HDE's side, so an app-verified zone or coordinates reach the calculation; the ambiguity, fold and gap refusals | C09, C10 | PF05 §3.2's Required-Now gap; a CRD or Epic row |
| A primary key on `hde.body_graphs`; the `input_fingerprint` recipe written down | C12, C22 | PF12 §8.7's "future DB/infra migration epic" |
| Separate test and development databases from production | C03, C34 | PF07 §7.1's *"OPEN/TBD"*; a CRD |
| A credential compromise procedure; who issues credentials | C08 | With P-3, or a governance CRD |
| A batch or candidate-set read, if throughput needs it | C14, C23; A07 | Decided after A07's measurement |

### 5.3 Decisions for Nathan in HDE's process

- **D-A:** end HDE-COAG005's no-user posture and open production member chart writes (P-1).
- **D-B:** an Epic built from the deferred Coagulation rows, or a CRD with an ADR (P-2, P-3).
- **D-C:** who creates the member's HDE UUID. Option 1: the app, as a UUID separate from its account ID (the seam keeps the identities apart). Option 2: HDE, returning one. The canon expects alignment *"with a Glow App user ID"* but does not decide.
- **D-D:** a separate HDE test environment, or a synthetic-member protocol on production (P-5).
- **D-E:** the network path. Option 1: the public address and a credential. Option 2: Railway's private network in `ample-illumination`.
- **D-F:** whether the prototype's HDE deployment follows HDE-EPIC043's Magic10 v2 deployment.
- **D-G:** whether the prototype shows narrative text, which needs the pair-binding answer, or bands only.

## 6. The app's side: HDE's shape against the four ports

| App port (`docs/architecture/provisional-hde-seam.md`; `services/api/glow_domain/provider_contracts.py`) | How HDE's specified shape maps onto it | What the adapter needs that the canon does not give |
|---|---|---|
| `BirthInput` / `ChartResolver.resolve(birth_input, current_input_version, idempotency_key)` | `birth_date` → `birthdate` `YYYY-MM-DD`; `local_time` → `birthtime` `HH:MM`; `place_label` → `location` (4–200 characters, sent as entered). `timezone_name` has no carrier. `ChartResolutionState.RESOLVED` corresponds to a stored current row; HDE has no `PENDING`. | An app-callable create operation (P-2); its identity and correction rule (C11, C12); its errors and timeouts (C13, C21); authentication (P-3). **App-side:** OD-61 means `TimePrecision.UNKNOWN` and `local_time=None` must be refused at sign-up; a free-text place must be accepted as the vendor's input; the app's own idempotency key has no HDE counterpart other than "same UUID and same input" |
| `CompatibilityProvider.evaluate(request, idempotency_key)` | One `POST /api/reader?v=2` with `{a_id, b_id}`, after the app's eligibility check. Map 200 `eligible:true` → ready with ten bands; `eligible:false` → self-pair (the app should never send one); 404 `ERR_M10_PERSON_UNRESOLVED` → chart not yet stored (pending or unavailable); 503 codes → unavailable; 400/422 → defect. The adapter may normalize pair direction, since Reader symmetry is guaranteed. The cache key gains `release_id`. | Authentication (P-3); network path (P-4); a client retry policy (C21); throughput (C19; A07). No batch (C14), so the adapter loops over pairs within limits the canon does not yet give |
| `CompatibilityProjection` | Bands per category (`Cool`/`Open`/`Warm`/`Glow`), plus freshness from `release_id` and `idempotence_hash`. If narratives are used, Aux text with the viewer's own perspective only (PF17 §1.3) | Storage rights and duration (C25); the narrative pair binding (C16, C17). The band meaning changes at the Magic10 v2 cutover, so the projection must carry `release_id` |
| `EngineLifecycle.plan_detachment(request, idempotency_key)` | No HDE operation to call. Every engine obligation stays "unresolved" and the app revokes access on its side, as the port already says (*"never proof of engine deletion"*) | Deletion, export and consent operations, and completion evidence (C27–C33; section 5.2) |

## 7. Draft receipt (section 6 form; **draft, not a delivered contract**)

> **DRAFT.** This is not `docs/architecture/hde-contract-receipt.md`, and it records no delivery. It shows what a receipt would hold if HDE's canon at glow-docs `71a008f` were the contract today.

- **Contract version and HDE release:** Reader v1 and v2 (`POST /api/reader`; PF05 v2.5.7 §5.1). Release manifest `1.3.0`, `release_id` `2d5a4ec4…c129` (PF12 L1962, L2032). No HDE commit is named as the contract's. The Magic10 v2 cutover (HDE-EPIC043) will issue a new `release_id`.
- **Environments:** production `glow-hdengine-v2`, project `ample-illumination`, `https://glow-hdengine-v2-production.up.railway.app` (PF07 §2.2). **No test environment** (C03).
- **Authorized access:** **none for the app.** The canon defines no app credential (C05) and no app write (C06). Nathan has not confirmed a credential.
- **Delivery:** none. No date is set in HDE's process (OD-23; contract request §7).
- **Answers:** section 2 above, each cited at glow-docs `71a008f` by document, section, version and line. Under contract request §5, the canon does **not** meet "delivered":
  - 21 questions are partly or wholly "not in the canon": C01 notice, C03 test environment, C05, C07 path, C08, C10 uncertain time, C11 issuer, C12 correction, C13, C19, C21 client retry, C23, C24, C25 client storage, C27, C28, C30, C31, C32, C33, C34 region and processor role.
  - No test environment exists.
  - No access is named.
- **Adapter mapping and gaps:** section 6 above. Gaps: section 5.

## 8. What I could not find, and where I looked

| Not found | Where I looked |
|---|---|
| Any authentication for `POST /api/reader` or for an app client | PF02, PF04, PF05, PF07, PF12, PF14, PF19, PF29: "auth", "Authorization", "bearer", "token", "API key", "credential", "CORS" |
| A notice period or deprecation window | All files: "deprecat", "sunset", "notice period", "breaking change", "migration notes" |
| A hosted test or staging HDE | PF07 §2, §6.3.2, §7.1; PF04 §5.2.2 ("Verify that exact artifact in staging" names a step, not a host) |
| An app-to-HDE network path | All files: "railway.internal", "private network", "service-to-service" |
| An unknown-time mode or rectification | All files: "rectif", "unknown time", "time unknown", "missing birth", "uncertain" |
| Who creates a member's identifier; an HDE users table | PF05, PF07, PF12, PF14: "user_id", "users table", "person table", "signup", "onboard" |
| The `input_fingerprint` recipe; correction semantics | PF02, PF05, PF12, PF14: "fingerprint", "correction", "birth-data change" |
| A pending state; measured latency | All files: "pending", "latency", "duration_ms" |
| A Reader rate limit or quota | All files: "rate limit", "throttl", "quota", "QPS", "429" |
| Deletion, export, consent, notices, backup-restore notice, processor role, region | All files: "delet", "erase", "purge", "GDPR", "CCPA", "DSAR", "export", "consent", "withdraw", "webhook", "callback", "outbox", "notif", "PITR", "processor", "controller", "region" |
| An Epic ID for "the App user model"; a PF09 row for `/_ops/bodygraph/resolve`; "IG-022" | PF09.1–PF09.7, PF10, PF16, PF20, PF30.1; `docs/ephemeral/` names |

I did not read the canon whole: it is about 8.6 MB. The coverage was:
- PF05: read in its relevant sections, by me.
- PF01, PF02, PF04, PF06, PF07, PF09.x, PF10, PF12, PF14, PF15, PF16, PF17, PF19, PF20, PF29, PF30.1 and PF31: read by section and searched by each question's terms, by the five subagents. I checked a sample of their quotes against the text.
- PF03, PF08, PF11, PF13, PF18, PF21, PF23 and PF27: searched only.

## 9. Checks on this record

- `git diff --name-only 06e8cec71c0b158bb5b50880e28061df277fa5ce HEAD` lists only this file.
- Every question, C01 to C35, has a row in section 2.
- The trusted classifier, `scripts/change_scope.py` taken from `origin/main` (`d3273f3`) into the scratchpad and run with `python3 -I … --base 06e8cec… --head <head> --merge-base`, printed `{"full": false, "reason": "ordinary-docs-only", "paths": ["docs/testing/evidence/2026-11-19-a01-r-hde-canon-read.md"]}` at this record's first commit `d9671a1`.

## Manager verification of A01-R

App Manager 12, 19 November 2026. The record was read whole.

- **The branch:** `claude/fervent-sagan-afkke2`, head `835d393` (commits `d9671a1`, the record, and `835d393`, the classifier result). `git diff --name-only 06e8cec 835d393` lists only this record. Merged into the manager branch at `44b48f4`.
- **Classification:** `scripts/change_scope.py` from `main` (`d3273f3`), run with `python3 -I`, full SHAs and `--merge-base` from `06e8cec` to `835d393`: `"full": false, "reason": "ordinary-docs-only"`, this one path.
- **Citations checked by the manager** at glow-docs `71a008f` (fetched read-only; nothing written there), all exact:
  - PF05, line 991: *"`bg:resolve --source=vendor --upsert` **must not** be used in prod until a Glow App user model exists and a future epic explicitly re-opens user-bound upsert flows."*;
  - PF05, line 430: *"We must not create app-like user records in prod ahead of Glow App integration."*;
  - PF05, line 4086: *"**Bands-only, no numerics.**"*;
  - PF07, line 962: *"Production runs on one Postgres instance; staging/dev connect to the same physical instance"*;
  - the app's own `services/api/glow_domain/provider_contracts.py`, lines 26, 34 and 55 to 56: `TimePrecision.UNKNOWN`, `local_time: time | None`, and *"Unknown time and supplied civil time must agree."*
- **Limits, as the record states them:** the canon was not read whole (about 8.6 MB); PF05 was read by the session, the rest searched by five subagents and sampled. Accepted as the record's stated limit.
- **A deviation, recorded:** glow-docs was not attached at the session's start. Before stopping, the session tried to attach it, and the permission check refused; it then stopped and reported, and attached it read-only after Nathan's instruction (section 1.1). Future prompts that need glow-docs say to stop and ask Nathan if it is missing, and to try nothing first.

### Dispositions (OD-80: no design decision about HDE now)

| Finding | Disposition |
|---|---|
| C01 to C35, answered and marked (section 2); the draft receipt (section 7) | **Accepted** as a dated snapshot of HDE's canon at `71a008f` (HDE is still under development, OD-79). The receipt stays a draft until HDE's contract is delivered |
| The prototype list P-1 to P-6, the before-launch list, and the decisions D-A to D-G (sections 5.1 to 5.3) | **Recorded as inputs to the later integration process** (OD-80). None is decided, scheduled or put to Nathan now |
| Conflict 1, OD-61's sign-up chart against HDE's production write ban | **Recorded** for the integration process (D-A). No app change |
| Conflict 2, the app's code still allowing an unknown birth time | **Already met at sign-up:** SV2's D8 refuses an unknown or missing time (`save_birth_input`, `birth_time_required`; the profile suite's `birth.a_time_is_required_and_approximate_is_kept`), as OD-61 requires. The port's own type (`provider_contracts.py`) waits for the integration process (OD-80). No work is routed (DM-95) |
| Conflict 3, the time zone | **Recorded** for the integration process. The app keeps its rule on its side: it sends what the member entered and converts nothing |
| Conflict 4, PF15's "small percent" | **Routed** to the screens that show compatibility (AC3; the brand's DS-5): no number is ever shown to a member (PF01 §5) |
| Conflicts 5 and 6, direction and identity | **Recorded** for the integration process (D-C; the narrative pair binding, D-G) |
| Conflict 8, one shared database | **Recorded** for the integration process (D-D) |
| Conflict 9, PF07 naming `glow-backend-v4` and `glow-frontend-v2` as Glow infrastructure | **Routed** to the Railway analysis item (OD-79) as an input; retiring a component that HDE's canon names is for HDE's process (D08) |
| Conflict 10, inconsistencies inside HDE's canon | **Recorded** for HDE's process; nothing for the app |
| The port mapping (section 6) | **Accepted** as input. Its app-side parts need no new work: the birth-time refusal is SV2's D8, and the port already carries the place as entered with a civil time. Its HDE-facing parts wait for the integration process (DM-95) |

