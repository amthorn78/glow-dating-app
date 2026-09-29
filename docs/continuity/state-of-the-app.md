# Status report and State of the App

- **As of:** 25 September 2026, about 09:00 UTC. Prepared by App Manager 3 for the Dev Manager's first process and build reviews (DM-01 and DM-02) and for any session that needs the whole picture.
- **Basis:** `main` at `0f45e648099b415217938c25d7369164c0101def` (PR25). The manager branch `claude/stoic-carson-66gdig`, head of draft [PR26](https://github.com/amthorn78/glow-dating-app/pull/26), adds P06.1-I1's harness and the records named below. The exact commit this report was written at is in the [Dev Manager review log](dev-manager/README.md).
- **Claim levels:** "verified" means App Manager 3 checked it on 25 September against code, Git, CI or a tool. "Recorded" means it comes from an evidence record or handoff that App Manager 3 did not re-check. "Unverified" means nobody has established it.
- **Authority:** this is a snapshot. The [current handoff](current-handoff.md) routes sessions. [PF01](../pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md) governs the plan. Notion holds live task state. Refresh this file before each periodic Dev Manager review.

## Part 1 — Status report

### 1.1 In one paragraph

Glow is a new iOS/Android dating app built around Glow-owned accounts, profiles, reciprocal eligibility, recommendations, mutual matches, safety and one-to-one chat. It will consume compatibility results from the separate, protected Glow HD Engine (HDE). After three days of work (23–25 September 2026), phases P01–P05 are complete at **fixture scope**. There is a pinned Expo mobile app, a Django API, shared contracts and a large test suite, all running on synthetic in-memory data. There is no real authentication, database, provider integration, deployment or signed native build, by design: PF01 connects the database and live services last, in P11. Work moved from ChatGPT to Claude Code on 24 September (D09) and runs as Nathan's manual relay. The current work item is **P06.1**, a live sandbox proof of Stream Chat's permission model against Nathan's development Stream application. Its first session found one design-level bypass, S15, which Nathan decided on 25 September. He then established the **Dev Manager** (D10) and asked for this report and two reviews before the next implementation task.

### 1.2 Phase and work-item status

States are from the Notion Work Register, read by App Manager 3 on 25 September 2026 (verified).

| Phase | Items | State | Scope actually delivered |
|---|---|---|---|
| P00 | P00.1–P00.3 | Done | Plan, canon, control page, register |
| P01 | P01.1–P01.3 | Done | Reuse assessment ([ADR 0001](../adr/0001-isolated-application-foundation.md)), private repository, pinned mobile/API base, CI |
| P02 | P02.1–P02.3 | Done | Contracts and state machines, 32 provisional model definitions, 2 unapplied migrations, HDE ports and fixtures |
| P03 | P03.1–P03.3 | Done | Same-Railway-project decision ([ADR 0002](../adr/0002-same-project-application-services.md)), fail-closed configuration, guarded container, CI, runbooks. No services provisioned |
| — | AP1-DBA-001 | Done | Read-only database catalog audit, 23 September |
| P04 | P04.1–P04.3 | Done | Fixture onboarding, profiles and preferences, private media lifecycle |
| P05 | P05.1–P05.3 | Done | Fixture reciprocal eligibility, discovery and recommendations, likes, matches, unmatch and block. Contact is always denied |
| — | M01, M02 | Done | Migration to repository Markdown and Claude Code; setup and workflow optimization |
| P06 | **P06.1 In progress**; P06.2, P06.3 Planned | — | P06.1-I1 done (below); P06.2 is the chat adapter and UI, P06.3 notifications |
| P07–P12 | All Planned | — | Safety and WordPress operations, privacy lifecycle and billing, hardening, pre-integration proof, final database and live integration, release handoff |

Dependencies: A03 is Done. A01 (final HDE contract) and A07 (HDE throughput and granularity) are Blocked. A02, A04, A05, A06 and A08 are Planned; P06.1 resolves A08.

### 1.3 The current work item: P06.1

The [P06.1 brief](../planning/p06-1-chat-provider-proof.md) and [evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md) hold everything below in detail.

- **What it proves:** that Stream Chat can enforce Glow's chat design. The server controls channel membership and sends every message on the user's behalf after its own match and block check. A client token reads only its own current match's channel.
- **P06.1-I1 (done, 25 September; verified against the pushed branch):**
  - Outcome 1, checks enforced: holds.
  - Outcome 2, authorized path: holds, 18 of 18.
  - Outcome 3, no client bypass: does not hold because of **S15**. A member can write up to 5 KB of free text as custom data on its own membership, the other member's client receives it, and no Stream permission governs the write.
  - Of 85 matrix cases, 68 hold with an attributable refusal and 7 hold without one; 9 are inconclusive and 1 fails.
  - The session closed a second channel, free text in typing events, by turning typing off.
- **S15 decision (Nathan, 25 September):** *"I accept your recommendation on S15. There should never be any indication that there is anything happening outside Glow."*
  - The display rule: the app never displays Stream user or member data.
  - The second sentence is a wider product principle. The manager's working reading is in the brief, pending the Dev Manager's review.
- **The development Stream application now:**
  - authentication and permission checks enforced;
  - guest creation disabled, and no application grants for the client roles;
  - every role's grants empty in the five default channel types;
  - a locked `glow-match` type in which members may only read.

  Nathan accepted a side effect: the dashboard administrator role has no grants in those types. The restore command is recorded but has not been run.
- **Usage:** 19 of 20 users, 28 of 30 channels and 884 of 5,000 API calls, within a $0 budget. The Free Chat plan has no payment method on file.
- **Next in P06.1:**
  - Nathan runs the exact-head review of I1 (prompt ready).
  - Corrections if needed.
  - P06.1-I2: revocation and history under Nathan's policy, suspension and deletion, token expiry, reconnection, send-versus-revocation races, outage, economics, the architecture document, Video and Feeds lockdown, the G2 and S10 reruns, the existence check and the S15 mapping.
  - Delta review, then PR26's final CI, Codex's review and merge.
  - Per Nathan, I2 is not written until the Dev Manager's review has been considered.

### 1.4 Recent work (all dates 2026, UTC)

| When | What | Where |
|---|---|---|
| 23 Sep | P00–P04 under ChatGPT (App Planner 1, App Builder 1). Repository created; D08 authority. ADR 0002 same Railway project; database audit | PR1–PR9 |
| 24 Sep | P05.1–P05.3 complete at fixture scope | PR10–PR14 (PR14 at 11:32) |
| 24 Sep | D09: move to Claude Code, repository Markdown authority, feature pause; M01 migration | PR15–PR16 |
| 24 Sep | Manual relay fixed; App Manager 2; M02 setup: Setup script, change-scope classifier, pin test, instructions | PR18 merged 23:59 (PR17 superseded, closed) |
| 25 Sep | M02 close-out; mistakes log started | PR19–PR22 |
| 25 Sep | App Manager 3: Setup script verified; P06.1 proposed, answered and resumed; Stream dashboard baseline; I1 brief and prompt | PR23–PR25 |
| 25 Sep 02:51–03:33 | P06.1-I1 live runs against Stream application 1729640 | I1 branch `claude/compassionate-lamport-531vtk` |
| 25 Sep 07:53 | I1 verified, integrated, draft PR26; review prompt written | PR26 |
| 25 Sep | S15 decided; Dev Manager established; this report | PR26 branch |

24 PRs merged in three days. Nearly every one after PR16 is ordinary documentation.

### 1.5 Decisions in force

**Plan decisions (PF01 section 10):**

- **D01:** a fresh foundation with managed components.
- **D02:** protect HDE and its database.
- **D03:** database and live integration last (P11).
- **D04:** Notion coordinates; repository Markdown is the authority.
- **D05:** a separate application canon; no automatic phase approvals.
- **D06:** Expo with React Native, and a modular Django/DRF API.
- **D07:** Stream is preferred only if permissions and economics pass.
- **D08:** app-only authority, protected by effect on HDE.
- **D09:** Claude Code with a manual relay.
- **D10:** the Dev Manager.

**Owner directions recorded since:**

| Date | Direction | Home |
|---|---|---|
| 23 Sep | App services in HDE's Railway project `ample-illumination`; a preferred app-owned schema in the same logical database, with restricted roles | ADR 0002, PF01 §4 |
| 24 Sep | Ordinary documentation (Markdown only, outside `.claude/`) skips application CI and code review | `AGENTS.md`, CI policy |
| 24 Sep | One work item at a time; branch and PR discretion to the manager | Handoff, manager workflow |
| 24 Sep | Reasoning-level recommendation with every prompt; TypeSafe scorer v4 as an advisory second reading | Manager workflow step 3, Notion usage log |
| 25 Sep | Managers log their own mistakes | [Mistakes log](manager-mistakes.md) |
| 25 Sep | P06.1 inputs: $0 budget; `STREAM_*` values on the server side only; after an unmatch or block neither person can send or see the conversation, and history is kept only for safety reports | P06.1 brief |
| 25 Sep | Resume P06.1; reconfigure the test application; proceed despite the dashboard user | P06.1 brief |
| 25 Sep | S15: the display rule; *"There should never be any indication that there is anything happening outside Glow."* | P06.1 brief, PF01 §7 |
| 25 Sep | The Dev Manager: second-layer review, manual relay, no scoring | [Charter](../planning/dev-manager.md), PF01 D10 |

### 1.6 Unresolved issues and open inputs

- **Owner inputs still outstanding** (from the [Claude handoff](claude-code-handoff.md#prioritized-inputs-nathan-must-supply), recorded):
  - retention, moderation and support owners, and the account and session authorization approach (A05);
  - the supported HDE contract, data rights and throughput (A01, A07);
  - app service and environment identities, database roles and backup decisions (A02, P11);
  - Expo/EAS, Apple and Google signing, and push accounts;
  - Cloudflare, mail and WordPress access; launch geography;
  - paid launch (A06).
- **Recorded follow-ups, for Nathan to schedule after P06.1:**
  - the intermittent rendered-test failures;
  - the Setup-script and pin-test hardening: review nits N1, N2 and N6, Codex's P2 and an optional completion stamp;
  - App Manager 1's stale-documentation sweep of `docs/architecture/`, `docs/testing/` and `docs/operations/`.
- **P06.1 open items:** 9 inconclusive cases; the untested restore; harness fixes not yet exercised live; the S15 mapping; Video and Feeds; economics.
- **Platform limits:**
  - Branch protection is not enforced on this private personal repository (recorded in the CI policy).
  - The manager's GitHub integration cannot re-run Actions jobs; Nathan does.

### 1.7 Known risks

| Risk | Current state |
|---|---|
| R01 late persistence defects (database last) | Mitigated by ports, static model and migration definitions and conformance cases; no real PostgreSQL behavior is proven until P11A |
| R02 HDE contract unfinished | A01 and A07 blocked; the app uses opaque chart mapping and synthetic compatibility |
| R03 shared HDE infrastructure changed by accident | No app resource provisioned; protected identities listed in resource ownership; no database connection since the 23 September audit |
| R04 chat bypass or cost | S15 decided by a display rule, which leaves a residual risk. Stream's general policy bills overages automatically, and no payment method is on file; economics are unmeasured until I2 |
| R05 store, safety and operations gaps | Moderation, support and retention owners are unnamed (A05); no store matrix yet |
| R06 duplicate authority or misleading progress | Status lives in many places (see 3.4 and 4); 15 logged manager mistakes, mostly record-keeping |
| Environment secrets | Any command in a `Glow app` session can read `STREAM_API_SECRET`, and any process can send authenticated TypeSafe requests through the proxy. Rotation is cheap |
| CI reliability | Three intermittent rendered failures of one kind (a form submit that does not advance) |
| Dependencies | 14 moderate npm advisories, none high or critical, at the P05.2 audit (24 September, recorded), including GHSA-vcc3-ghjq-m6fr (Expo Router URL decoding) and GHSA-w5hq-g745-h8pq (Expo build-chain uuid). Remediation is a pre-release obligation |
| Continuity | One manager at a time; long sessions compact their context; Nathan relays every session by hand |

### 1.8 Immediate trajectory

1. The Dev Manager's DM-01 process review and DM-02 build review; the primary manager's dispositions; Nathan's decisions where needed.
2. In parallel, as already commissioned: the exact-head review of P06.1-I1, then corrections if needed.
3. P06.1-I2, then the delta review, PR26's CI, Codex and merge. That closes P06.1 and A08.
4. With Nathan's direction: P06.2, the chat adapter and native conversation UI, under the display rule, with opaque Stream IDs and a server token endpoint. Then P06.3, privacy-safe notifications.
5. The recorded follow-ups when Nathan schedules them.

## Part 2 — State of the App

### 2.1 Product and scope

Product scope is from PF01 section 1. Chat is one-to-one text after a mutual match. Verified adults only. Recommendations come first, then broader discovery; a recommendation is not a match or permission to message. The app also covers block, report, moderation, appeals, support, pause, export and deletion. WordPress is the operator and policy surface. Out of scope for the first release: voice and video, public feeds, a consumer web app, custom chat infrastructure, speculative machine learning and all-pairs compatibility.

### 2.2 Architecture

- **Components:**
  - `apps/mobile`, the native client (untrusted);
  - `services/api`, a Django/DRF modular monolith that owns dating authorization, state transitions and audit;
  - `packages/contracts`, the versioned wire contracts;
  - a planned `wordpress/glow-admin` operator plugin that calls scoped admin APIs.
- **One repository, separate deployments:** HDE stays in its own repository and service.
- **Trust:** the API authenticates, validates and rechecks current state for every privileged action. Domain services use narrow ports for persistence, identity, media, messaging, notifications and HDE. Provider effects leave through a transactional outbox after commit; there are no distributed transactions.
- **Data:** PostgreSQL is the system of record for dating state. The chat provider may hold message bodies under a retention contract. Cloudflare holds media bytes. HDE owns chart calculation and compatibility, and the app keeps only an opaque account-to-chart mapping.
- **Pinned stack (verified from the lock and requirement files):**
  - mobile: Expo SDK 57.0.24, React Native 0.86.3, React 19.2.3, Expo Router 57.0.22, TypeScript 6.0.3;
  - API: Django 5.2.17 (LTS), Django REST framework 3.18.1, Gunicorn 26.2.0;
  - toolchain: Node 24.19.0, npm 11.9.0, CPython 3.12.14.
- **Planned managed services:** django-allauth headless for authentication, Celery with Redis, Cloudflare Images/R2, Stream Chat, Expo push and, if paid launch is chosen, RevenueCat.

### 2.3 What exists in code

Sizes, verified by line count:

- about 9,700 lines of hand-written TypeScript in the mobile app's `src`, including its unit tests, plus a generated 27,000-line validator module;
- about 15,100 lines of Python in the API, of which about 6,000 are tests;
- about 16,900 lines of schemas, fixtures and tooling in the contracts package.

| Component | What exists | Claim level |
|---|---|---|
| Mobile (`apps/mobile`) | Fixture-only shell and guarded navigation. Routes: account, verify, recovery, birth input, profile, preferences, media, recommended, explore, matches, match and restricted. Feature stores, policies and in-memory adapters; an optional development HTTP client | Behavior under substitutes. Rendered in Chromium through React Native Web as a test harness only. No signed native build or device proof |
| API (`services/api`) | Three routes only: `GET /health/live`, `/health/ready` (always 503) and `/api/v1/development/recommendations` (synthetic). Fail-closed configuration: staging and production refused, reserved secret names rejected by their presence. Internal fixture services for eligibility, discovery, likes, matches, unmatch and block. A disabled Stream webhook verifier; worker interfaces with no broker | No authentication, persistence or mutation routes. `contact_decision()` always denies sending |
| Persistence definitions (`services/api/glow_persistence`) | 32 provisional model definitions, 2 unapplied migrations and static consistency checks on a dummy database | Static only. The 23 September audit found no reusable legacy table for them |
| Contracts (`packages/contracts`) | Closed JSON schemas and state machines for flows F01–F20; production and development contracts; conformance corpora; generated mobile validators and types | Wire definitions; a production declaration creates no route |
| Proof harness (`proofs/stream-chat`, PR26 only) | P06.1's Stream sandbox harness: Python server side, Node client runner, 49 offline tests | Proof tooling, outside the app runtime and outside CI |
| Scripts and tooling | `bootstrap-toolchain.sh` (the environment's Setup script), `change_scope.py` (the trusted CI classifier), `smoke.mjs` (API-to-mobile HTTP smoke), `container_smoke.py` | Checked in CI or in session |
| Container | Digest-pinned guarded API image: refuses unsafe modes and serves loopback only | Built and smoke-tested in CI; never deployed |

### 2.4 Build condition

- **Tests:**
  - 253 API tests, 38 Python contract tests and 13 classifier tests, all passing; App Manager 3 re-ran them offline in a clean process on 25 September (verified).
  - 516 mobile tests, 373 JavaScript contract cases and 83 rendered browser cases, recorded on `main` at PR14 (CI run 35993588859). The mobile test code has not changed since then.
  - 49 harness tests (PR26).
- **CI:** the Foundation workflow runs Change scope, API checks, Mobile checks, API mobile smoke, API artifact checks and the Foundation gate.
  - On PR26's code head `9ff600f`, push run [36109949498](https://github.com/amthorn78/glow-dating-app/actions/runs/36109949498) passed all six, and the gate says `Application checks passed` (verified).
  - `main`'s application code last changed in PR18. Its last full run, [36081899675](https://github.com/amthorn78/glow-dating-app/actions/runs/36081899675), passed all six (recorded).
  - The harness's own tests are not in CI.
- **Reviews:** full-scope PRs get an exact-head code and security review in a session Nathan runs, plus Codex's automatic review once a PR is marked ready.
- **Known failures:** three intermittent rendered failures of one kind. Earlier diagnostics are on the unmerged branch `app-builder-1/p05-1-birth-diagnostics`.
- **Environment:** the dedicated `Glow app` cloud environment. It has no HDE variables, provides the Stream development variables, and its Setup script installs the pinned toolchain. App Manager 3 verified the Setup script's effect in a new session on 25 September.

### 2.5 Integration strategy

- **Ports first, providers proven separately, database last.**
  - Every external capability sits behind an app-owned port with a fixture adapter. The same conformance cases will later run against the real adapter.
  - Provider capabilities are proven in sandboxes before adoption; P06.1 is the first.
  - P11 brings disposable PostgreSQL (P11A), then staging with provider sandboxes (P11B), then the production connection (P11C).
- **HDE:** the app will call a supported engine contract through one adapter. It may use bands if that is all HDE permits, and never invents scores or reads HDE tables. Live HDE work waits for A01 and A07.
- **Data placement:** a clean app-owned schema with restricted runtime and migration roles, in HDE's logical database `railway` (audit of 23 September). HDE objects, including `public.hde_body_graphs_current`, are protected. A02 stays open until P11.
- **Chat:** Stream holds transport and history; the app owns entitlement. Sends are server-mediated; the display rule applies; the before-message-send hook is never the gate, because it fails open.
- **Deployment:** app services in Railway project `ample-illumination`, none provisioned yet. Readiness stays 503 until a real runtime exists.

### 2.6 Technical debt and known gaps

- The whole feature set runs on in-memory fixtures. The P11 deferred acceptance list (DB01–DB13, PV01–PV08, PR01, N01, R01) names what fixtures cannot prove. See [P11 deferred acceptance](../testing/p11-deferred-acceptance.md).
- There is no real authentication or session model yet; allauth headless is planned.
- 14 moderate dependency advisories remain for pre-release remediation.
- The mobile fixture journeys duplicate some domain logic from the Python services, as presentation substitutes checked against the shared contracts.
- The rendered tests are intermittent.
- Branch protection is not enforced.
- The harness's tests are outside CI.
- `docs/architecture/`, `docs/testing/` and `docs/operations/` contain statements that may predate later phases (the sweep is a recorded follow-up).

### 2.7 External dependencies

| Dependency | State |
|---|---|
| HDE (`glow-hdengine-v2`) | Protected; its contract is unfinished (A01, A07) |
| Railway `ample-illumination` | Shared with HDE; no app resources |
| PostgreSQL `railway` database | Shared with HDE and the legacy backend; audited read-only on 23 September; no app connection until P11 |
| Stream (application 1729640, Development, Free Chat, US East) | Configured for the proof; production needs its own application and secret |
| Cloudflare, mail, Expo/EAS, Apple, Google, WordPress, RevenueCat | Not yet accessed; inputs outstanding |
| GitHub | Private repository; no enforced branch protection; Codex reviews on ready PRs |
| Notion | Implementation Control, Work Register, TypeSafe usage log |
| TypeSafe | Advisory reasoning-level scorer for manager prompts; not used for the Dev Manager |

### 2.8 Decisions the manager would put in front of fresh eyes

These are not proposals. They are the places where one operational viewpoint has carried the most weight, and so where a second view could matter most.

- **Database last.** A large fixture layer (for example, the simulated atomic outbox and the fixture concurrency) is built ahead of any real PostgreSQL behavior. That risk is known (R01).
- **Shared logical database.** HDE's logical database will also host the app schema.
- **Stream,** kept after S15 with a client-side display rule, rather than per-person channels.
- **WordPress** as the operator surface.
- **Mobile fixture logic** that mirrors the Python domain services.
- **Proof tooling** (`proofs/stream-chat`) that lives in the application repository.

## Part 3 — The process as practiced

### 3.1 Sessions and roles

- **Nathan** is the owner. He starts every implementation and review session, relays the reports, and reinitiates managers.
- **The primary manager** is one Claude Code session at a time: App Manager 1, 2 and now 3. It writes briefs and prompts, verifies relayed work against the pushed branches, integrates branches into its own branch, runs PRs to merge and keeps the records.
- **Implementation and review sessions** start from prompts in `docs/ephemeral/`. They work on their own branches, within owned paths, and report back. They may use any tools.
- **Codex** reviews PRs automatically when they are marked ready.
- **The Dev Manager** (new, D10) reviews decisions and process by manual relay through the primary manager.

### 3.2 The cycle

The cycle is in the [manager workflow](../planning/manager-workflow.md):

1. brief;
2. prompt, with the manager's reasoning level and TypeSafe's advisory reading;
3. relay;
4. verify the full diff and re-run cheap checks;
5. classify with the trusted policy;
6. integrate with `--ff-only`;
7. CI;
8. an exact-head review session;
9. corrections and a delta review;
10. mark ready, wait for Codex, merge;
11. verify `main`; record the receipt, handoff and Notion;
12. prune the prompts.

Rules that shape it:

- **One work item at a time** until its CI and review are clear.
- **Ordinary documentation** skips application CI and code review. The manager reads it when it integrates.
- **Evidence** records exact heads, trees, commands and results. An earlier-head review never certifies a later head.

### 3.3 Records kept per event

A typical state change is recorded in several places: the brief, the evidence record, the current handoff, sometimes the Claude handoff, the environment inventory and the PF00/PF01 status lines, and in Notion the Implementation Control status block, the Work Register row and the TypeSafe usage log. Implementation Control is about 100,000 characters, mostly history.

### 3.4 What the record shows about the process

- **Throughput:** 24 merged PRs in three days. Since D09 most are documentation, often one per step.
- **The mistakes log** holds 15 entries: AM2-01 to AM2-11 and AM3-01 to AM3-04.
  - Most are record-keeping and tool slips (Notion formatting, commands, a level commitment), caught by readbacks or by the manager itself.
  - Two were process departures, caught by Nathan or by a tool guard (AM2-08, AM2-10).
  - One was a merge before Codex finished (AM2-06).
- **Review heads** move whenever the manager adds records to the branch. Later documentation-only commits need no review, but they multiply commits and CI runs.
- **The TypeSafe log:** 7 rows; the pre-registered comparison after 10 relayed sessions has 5 outcomes so far.
- **The manager cannot verify live provider behavior itself.** It never calls providers, so live claims rest on the implementer and the reviewer.

## Part 4 — Documentation state

| Home | Contents | Condition |
|---|---|---|
| `docs/pf-canon/` | PF00 (rev 1.7) and PF01 (rev 1.8) | Current; revision histories kept |
| `docs/planning/` | Manager workflow, Dev Manager charter, P06.1 brief, M02 brief, database audit and catalog, initiation and migration records, source snapshots | P06.1 and the process documents are current |
| `docs/continuity/` | Current handoff, Claude handoff, mistakes log, this report, the Dev Manager review log, receipts, history | The handoff is current and dense. The Claude handoff is a large reference with a status line kept current |
| `docs/architecture/`, `docs/adr/` | 14 architecture documents, ADR 0001 and ADR 0002 | Written during P02–P05; parts may predate later decisions (sweep pending). No ADR for D09, D10 or S15 yet |
| `docs/operations/` | Configuration, environments, local development, CI policy, build and deploy, providers, resource ownership, runbooks, environment inventory | CI policy, local development and environment inventory are current. Others are from P03 |
| `docs/testing/` | Phase checkpoints P02–P05.3, evidence records (M02, P06.1), P11 deferred acceptance | Checkpoints are dated evidence |
| `docs/ephemeral/` | Next-manager start prompt, P06.1-I1 prompt, I1 review prompt, Dev Manager start prompt | Pruned when their items close |
| Notion | Implementation Control, Work Register, TypeSafe usage log, and the Dev Manager and State of the App pages | Synced by the primary manager with readbacks |
