# M09 — Independent project status review: evidence record

The independent review Nathan directed on 18 November 2026 (OD-72): *"I want you to write an independent project review prompt. I need to know the status and remaining work for the app build."* Brief: [M09](../../planning/m09-project-status-review.md). This record answers Nathan. The manager adds "Manager verification of M09", with a disposition for each finding, when it integrates this branch.

## Summary for Nathan

**In one line.** Glow is a set of well-tested parts that are not yet a product: nothing is served, nothing is deployed, and no member or operator can do anything today.

**What is built, and how I know.**

- The server's sign-in, profile, photo, discovery, like, match, unmatch and block code is real. I ran every offline suite myself and read CI's run on `main`: the counts are equal and all pass, including 645 API tests and 438 cases on a throwaway PostgreSQL.
- That code is sealed. It runs only inside CI. The server that can be built answers two health checks and one sample route.
- Chat has its engine and no way in from outside.
- The mobile app is a demonstration on built-in sample data. It talks to no server and has never run on a phone.
- Reports, moderation, support, export, deletion, the paid plan and the staff console are table definitions only.
- No account exists with any store or provider except Stream's free development application. No call has ever been made to HDE.

**What remains.** 21 build items in order, from SV4 to P12, and ten actions of your own beside them (section 4.3). Five pieces of work had no item in the plan: the app's real connection to the server; the server side of safety, privacy, support and billing; the server composed into one running service with its worker; the real provider adapters; and the design system.

**How big.** About 200 to 350 sessions at November's measured rate. That is three to four and a half times the 78 sessions started since 26 October. Six items have no past item of their kind, so the range is wide. I give no date (PF01 §11).

**What decides when it ships.**

1. **HDE.** No real profile can become visible until HDE can turn a new member's birth details into a chart and answer a pair read on a live service. HDE's own canon says the first is not built and the second is not proven live. Neither has a date. This is the one gate that can stop the launch.
2. **The accounts.** The US entity, its D-U-N-S number, the store accounts and Stripe's review run on other people's clocks, and none has started. The budget is \$0 and no line is priced.
3. **The process.** Since 26 October, 78 sessions and 63 Dev Manager consultations produced 11 pull requests with code, on about 280 hand relays by you. 61 of the 78 sessions reviewed or corrected, and many corrections changed no application code (section 8.1).

**Recommended next:** M07, the costed list; then A01-R, a read of HDE's canon against the contract request; then SV4's brief. The first two change no code.

**Decisions I need from you first** (section 5): a date for HDE's work (D-01); the costed list and the entity now (D-02); what checks a photo before it is shown (D-03); the plan and its price (D-04); what a member without a plan can do (D-05); whether research items may run beside a code item (D-06); what a correction pass and a Dev Manager read are for (D-07).

**Defects in code recorded as done** (section 7). A like made before a block survives the block and can still make a match (C-01). A block's direction can be inferred (C-02, already known). Nothing can make a profile visible (C-03). At the launch defaults a photo is shown with no check of any kind (C-05).

**The records.** They agree with Git and CI on every merge and every count. 29 are stale or disagree with another record, and 16 follow-ups have no home or no owner (section 6).

**What I changed under your authorization** (section 10): GAPP-PF01 revision 1.19, as its own commit on this branch, and the plan in Notion. PF01's change takes effect only when the manager integrates this branch after the Dev Manager's read.

**Findings by kind:** record accuracy 29 (R); follow-ups without a home 16 (H); code and CI 19 (C); gaps in the plan 10 (P); risks 13 (K); decisions for you 18 (D).

## 1. Identity, start gate and environment

- **Prompt:** revision 1, from commit `4e01cd7d7905f72a42b8620eb76f03e6097f35c2` of the manager branch `claude/magical-wozniak-yfmmx2`.
- **Session branch:** `claude/nifty-euler-3v8sl7`, set to `4e01cd7` before any work. The session began on 18 November 2026 at 23:07 UTC, in `Glow App - No Stream`, and ran into 19 November.
- **Start gate:** every check passed.
  - `HEAD` was `4e01cd7d7905f72a42b8620eb76f03e6097f35c2`, and that commit was on the live manager branch.
  - PR54's merge `6edae780a0fbf1e5d2659c3eb8c9c48eeeea1a70` was an ancestor, and no non-Markdown path differed from it ("main's code").
  - No M09 record existed. `origin/main` was `6edae78` and did not move during the review.
  - The manager branch moved once during the review, to `964d38a` at 23:18 UTC. That commit adds one line to SV2-R's record (main's push run 44416436012 passed). The prompt's commit stayed on the branch, so the prompt was not stale. I reviewed at `4e01cd7`.
- **Environment check (names only; no value was read or printed):**
  - none of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` was set;
  - no `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*` or `CF_*` name was set;
  - present and never read: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_CA_BUNDLE`, `GITHUB_TOKEN`, `GH_TOKEN`.
- **Toolchain:** CPython 3.12.14 as `python3.12`; Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`; Git 2.43.0; the Docker client 29.10.0 with **no Docker daemon running**; PostgreSQL 16 binaries present and not used.
- **Clean process environment:** every repository command ran under `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8` plus its own variables, in a scratch copy made with `git archive` outside the checkout. The four hash-locked installs also received the proxy address and the certificate bundle's path, by their documented values. No `AWS_*` name passed to any command.
- **The local clone was shallow** (depth 50) when the session began. I fetched the full history before any Git measurement: 1,140 commits reachable from `4e01cd7`, 55 first-parent commits on `main`, one root commit (`8131cc7`, 23 September 2026). Readers who had run Git commands earlier re-ran them.
- **The session branch was pushed early.** A stop hook reported four unpushed commits. They were the manager's own records commits, which the start gate put on my branch. I pushed the branch at `4e01cd7`, with nothing of mine on it, at 23:28 UTC. That first push of a new branch started a full Foundation run, 44421080745, which passed (section 9).

### 1.1 Three directions Nathan gave in this session

Nathan gave three further directions in the review session itself, on 18 November 2026. They are quoted exactly. The owner-direction register is the manager's file, so I propose their rows in section 6 (finding R-01) and did not write them there.

1. *"When complete, I authorize you to update the implementation plan in Notion and pfcanon to ensure the most efficient, thorough, and effective path to completion."*
2. *"Clone the repository amthorn78/glow-docs into this session."*
3. *"you can add to the plan that all HDE docs and initial UI/UX design system is available in glow-docs, which will be attached to all sessions going forward"*

What I did under them is in section 10. They widen this review's owned paths beyond the brief's: besides this record, the session changed GAPP-PF01 on its own branch, as a separate commit, and the plan surfaces in Notion. `amthorn78/glow-docs` was cloned read-only at `707da56` and nothing was written to it.

## 2. How each claim was checked

Every statement about the build carries one of these marks.

| Mark | Meaning |
|---|---|
| **CODE** | I read the code that shows it, at `6edae78`. |
| **RUN** | I ran the suite or command in the scratch copy; section 9 has the exact result. |
| **CI** | I read the GitHub Actions run, its jobs or its logs. |
| **GIT** | Checked against the full Git history. |
| **READER** | A delegated reader read the code or record and cited the lines; I did not re-read every line. Where I re-checked the claim myself, the mark is CODE, GIT or CI. |
| **RECORD** | A project record says so, and nothing else was checked. The records were written by the sessions under review. |
| **NOTION** | Read from Notion on 18 November 2026, 23:19 to 23:36 UTC, by a reader with the read tools only. |

Twelve readers were started in parallel, each read-only: the mobile app; the API's runtime, identity and profiles; the API's discovery, chat, persistence and domain; the contracts, proofs, CI and scripts; GitHub's pull requests and runs; the records to M05; the records after M05; the external gates and the requirements matrix; the Dev Manager's review log; the process records; Notion; and HDE's canon in `glow-docs`.

- **Eleven reported.** The reader of HDE's canon was stopped by a usage limit before it wrote anything. I read the parts of that canon named in section 4.5 myself.
- The reader of the Dev Manager's review log was stopped by the same limit after it had saved its full report, which I used.
- I re-checked each report's main claims in the code, the history or the runs before using them, and section 9 says which.
- The readers' reports are working files of this session and are not in the repository. Where a correction needs their detail, this record carries it (Appendices A and B).

## 3. Status

### 3.1 In one paragraph

Glow today is a set of well-tested parts that are not yet joined into a product. The mobile app is a demonstration that runs on built-in sample data, only in development mode, and talks to no server. The server's sign-in, profile, photo, discovery, like, match, unmatch and block code is real and passes its cases on a throwaway PostgreSQL in CI, but nothing serves it: the app that can be built and run answers two health checks and one sample route, has no database, and its container image does not contain that code. Chat has its engine and no way in from outside. No report, moderation, support, export, deletion, billing or staff tool exists beyond table definitions and message formats. Nothing is deployed, no account exists with any store or provider except a free Stream development application, and no call has ever been made to the HD Engine.

### 3.2 By member-facing flow

The contracts' flow registry names twenty flows, F01 to F20 (`packages/contracts/production/flows-v1.json`, CODE). "Sealed" means the code exists in `services/api` and runs only inside one CI job: the served app's URL file lists three routes, its settings install no slice and use Django's dummy database, and the container image copies `glow_api` and `glow_domain` only (`glow_api/urls.py`, `glow_api/settings.py:29,38`, `Dockerfile:13-14`; CODE).

| Flow | Server | Mobile app | Proven how | What is not real |
|---|---|---|---|---|
| F01 Account and session | Built, sealed (SV1): django-allauth 65.21.1 headless, 17 of its routes and `api/v1/account/access` (READER; route file CODE) | Sample screens: two fixed addresses and one published password (READER) | CI: identity suite 49 of 49 on PostgreSQL 17.11; RUN: 24 offline tests | Mail goes to an in-memory list. No key handling exists. Suspension and deletion are functions nothing calls, and nothing lifts a suspension (READER) |
| F02 Consent and the adult check | Built, sealed (SV2) | Sample screens; the age check runs in the app against a clock frozen at 23 September 2026 (READER) | CI: profile suite 77 of 77 | Both consent texts are marked development text (READER) |
| F03 Birth details and the chart | Birth details built, sealed. **Chart resolution is not built:** no code creates or resolves an engine mapping (CODE: `glow_profiles/requirements.py:20-22`) | Sample screen. It offers and defaults to "Unknown birth time", which the server refuses (CODE: `apps/mobile/src/app/birth.tsx:34-42`, `glow_profiles/operations.py:1113-1116`) | CI: profile suite, with the chart seeded by the test | **No real member's profile can become visible** until an HDE adapter exists |
| F04 Profile and preferences | Built, sealed: four two-way fields, "show me" sets, age range, home area, 16 versioned settings (READER) | Sample screens with a "Demo option A/B" catalog; none of the server's fields (CODE: no reference to their request types outside generated code) | CI: profile suite | The orientation list ships empty and the only distance choice is "anywhere" (READER; carried to P07) |
| F05 Photos | Built, sealed, over in-memory stand-ins for storage and processing (CODE: `glow_profiles/media.py:94-95`) | Sample screen; on a phone the picker answers "unsupported"; no photo is ever drawn (READER) | CI: profile suite | No member can upload a byte: the grant returns no usable upload address. No Cloudflare R2 code, no decoding, no metadata removal, PNG only at 1 MiB (READER). With the photo check off, its launch value, a photo is approved with no content check (CODE: `requirements.py:12-18`) |
| F06 Pause and visibility | Built, sealed | Sample screen | CI: profile suite | — |
| F07 Recommendations and discovery | Built, sealed: one page route, batches of 100, pages of 50 (READER) | Sample queues over 14 bundled fictional people, on a development-only message shape (READER) | CI: discovery suite 66 of 66 | Compatibility is a stand-in with one band, so a "recommended" list is a random 100 (RECORD: P11 plan; READER). No card can carry a real result: the contract has no shape for one (READER) |
| F08 Like, pass, undo | Built, sealed | Sample | CI: discovery suite, with simultaneous likes from separate connections | — |
| F09 Match | Built, sealed: a match is read by its ID. **No route lists a member's matches** (READER; route file CODE) | Sample; the only possible match is with "Fictional Jules", by a developer button (READER) | CI: discovery suite | A member whose like came first is never told the match's ID (READER, inferred) |
| F10 Unmatch | Built, sealed | Sample | CI: discovery and ordering suites | — |
| F11 Chat | **Engine only:** send, history, list, read cursor, outbox delivery and a Stream adapter, with **no route and no worker process** (CODE: `glow_chat` holds no view or URL file) | Screens on a sample transport; one of two places with a seam a real client could use (READER) | CI: ordering suite 56 and 115, delivery 13, reads 62; live Stream rows of 23 October are RECORD only | The history read against Stream has never run live. The reads still refuse what Nathan's OD-60 made read-only. Every sent message's text stays in Glow's database with no retention rule (READER) |
| F12 Notifications | Rules and settings logic in memory only (P06.3); no route, no stored state, no push transport (READER) | A settings screen on a sample transport, with a seam; no push module is installed (CODE: `package.json`) | RUN: 56 unit tests | No push has ever been sent. The stored model and the contract disagree on field names (READER) |
| F13 Block | Built, sealed: block and unblock | **No member-facing block control**; developer buttons only (READER) | CI: discovery and ordering suites | Two defects, section 7: a block's direction can be inferred, and a like made before a block survives it |
| F14 Report | Table and message format only | None | — | Everything |
| F15 Moderation, appeals, staff | Tables and formats. Five staff functions exist with no route and **no staff sign-in**: the staff identity is a string the caller passes (READER) | None | — | Everything |
| F16 Support and public pages | Table and format only. **No WordPress code exists** (CODE: no `wordpress/` directory) | None | — | Everything |
| F17 Data export | Table and format only | None | — | Everything |
| F18 Account deletion | One internal step marks the account and writes a job row; nothing processes it, and no member route exists (READER) | None | CI: ordering suite, for the revocation only | The purge, the providers, the restore replay |
| F19 App presentation | — | The sample app itself | RUN: 691 unit tests; CI: 104 rendered tests in Chromium | No run on a phone, an emulator or a simulator has ever been made (RECORD: `apps/mobile/README.md:16`) |
| F20 Paid plan | The contract allows one state, `disabled`, and so does the model (CODE: `glow_persistence/models.py`, `Entitlement`) | None | — | Everything. Nathan has since chosen a paid launch (OD-69 to OD-71) |

### 3.3 By phase and item

| Phase or item | Recorded state | What I verified, and how | What remains |
|---|---|---|---|
| P00 | Done | GIT: three direct commits of 23 September | — |
| P01 | Done | GIT: PR1 `2785bb5`. RUN: the offline suites pass today | Branch protection is not configured, by Nathan's choice (OD-52). No SBOM was ever produced, and no record defers it (READER) |
| P02 | Done, as a design baseline | GIT: PR2 `3560360`, PR3 `d950ff5`. RUN: 53 Python and 902 JavaScript contract tests | The production API description has no paths (CODE: `openapi.json`, `"paths": {}`). No threat-model document exists (CODE: search) |
| P03 | Done, at preparation scope | GIT: PR4 `bd701eb`. CI: the image builds and refuses staging and production | Nothing is provisioned: no Railway service, domain, worker, monitor, secret or backup (RECORD: `p03-checkpoint.md`) |
| P04 (P04.1 to P04.3) | Done, sample-data scope | GIT: PR5 to PR9. RUN, CI: as F19 | Every real behaviour of F01 to F06 on the phone |
| P05 (P05.1 to P05.3) | Done, sample-data scope | GIT: PR10 to PR14. RUN: 60 tests cover the in-memory versions, which the server does not use (READER) | No ranking and provenance ADR exists, and no record defers it (READER) |
| M01, M02 | Done | GIT: PR15, PR16, PR18 | M02's hardening follow-ups, one a Codex finding of 25 September, are undone after 55 days (GIT: `scripts/bootstrap-toolchain.sh` last changed 24 September) |
| M03 | Done | NOTION only; the repository records it as DM-01 to DM-03 | — |
| P06.1 | Done | GIT: PR27 `47db18d`. RUN: the harness's 648 offline tests. The live Stream results of 25 to 28 September are RECORD only; the raw outputs are not in the repository | Stream's terms 6.2 and 12.5 and its data-processing addendum are unread (finding H-03) |
| P06.DB | Done | GIT: PR28 `3afffb3`. CI: reference 56 of 56 on the head | DB06 and DB09 again on the real database (P11) |
| P06.2 | Done | GIT: PR29 to PR33. CI: adapter 115 of 115, delivery 13 of 13, reads 62 of 62 | Nothing served; the history read unproven live; nothing has checked Stream's configuration since 23 October (READER) |
| M04, M05, M06 | Done | GIT: PR36, PR34, PR38. RUN: 18 cleanup tests. CI: 19 cleanup runs, all passed (READER) | M06's list of native code never run on a device has no home (finding H-05) |
| P09.3a | Done | GIT: PR39. READER: 340 rows, 16 gaps | The matrix's state column is a 1 November snapshot (finding R-12) |
| P06.2-F | Done | GIT: PR40 `8031361`. RUN | The chat screens' view-model change is owed before P11 and belongs to no item (finding H-06) |
| P06.3 | Done, sample-data scope | GIT: PR41 `da92f1f`. RUN | As F12 |
| SV1 | Done, sealed | GIT: PR42 `c864edd`. CI: 49 of 49 | As F01 |
| SV2 (Stages A and B), SV2-R | Done, sealed | GIT: PR43 `4dc2061`, PR44 `3240ef0`, PR54 `6edae78`. CI: 77 of 77 | As F02 to F06 |
| SV3 (Stage A, B0, Stage B) | Done, sealed | GIT: PR45 `8d83474`, PR46 `947576d`, PR47 `36a19f7`. CI: 66 of 66 | As F07 to F10 and F13; two defects (section 7) |
| M08 | Done | GIT: PR48, PR49. CODE: PF02 holds 68 rules | PF02's revision 1.8 is tabled (OD-72) |
| A05-V, A05-V2, A05-V3 | Done (research) | GIT: PR50, PR52, PR53 | A05's third message is owed before P07's brief |
| **SV4** | Planned; its brief is tabled (OD-72) | CODE: no chat route exists | All of it, and more than its one line in PF01 says (section 4) |
| **P06.2-T** | Planned; no brief | CODE: the dormant token code is unchanged | All of it. Its "remove the `pyjwt` pin" can no longer be done as written, since SV1 needs the package (READER) |
| **P07.1, P07.2, P07.2a, P07.3** | Planned; no brief | CODE: tables and formats only | All of it |
| **P08.1, P08.2, P08.3** | Planned; no brief | CODE: tables and formats only | All of it. P08.3 is no longer conditional (OD-69) |
| **P09.1, P09.2, P09.3** | Planned; no brief | CODE: no native project, no `eas.json`, no bundle identifiers, no icon | All of it |
| **P10, P11 (A, B, C), P12** | Planned | — | All of it |
| **M07** | Planned; no brief | GIT: no costed list exists in the repository | All of it. The budget is \$0 and no line is approved |
| **OD-64's limits** | Recorded as "its own brief"; no ID, no brief, no Work Register row (NOTION) | CODE: no change limit exists | All of it; a precondition of P11 |
| M09 | In progress | This record | The manager's verification |

**Paused, tabled or set aside, each by a recorded direction:** SV4's brief and PF02 1.8 (OD-72, until this review reports); identity verification (OD-68, for the MVP); the automated photo check (OD-68, off behind a console toggle); a UK or EU launch (OD-55); resurfacing, undo of a pass and rematch (OD-60, off at launch); the priorities screen (brand decision BD-06 in `glow-docs`, on paper only). The feature pause of 24 September (OD-05) no longer holds: OD-49 resumed the remaining items in order.

### 3.4 By component

| Component | What it is today | Checks, with how |
|---|---|---|
| `apps/mobile` | Expo 58.0.22, React Native 0.88.1, React 19.3.0, every version pinned exactly (CODE). 26 route files. Of 47 non-screen modules, 26 are sample back-ends or bound to them, 4,654 of 5,397 lines (READER). It renders "Development preview unavailable" outside a development bundle (CODE: `src/app/_layout.tsx:58-63`), and its start script refuses anything but development sample mode (CODE: `scripts/development.mjs`) | RUN: typecheck and lint clean; 691 unit tests pass. CI: 104 rendered tests pass |
| `services/api` | Django 5.2.17. Served: `glow_api`, 1,109 lines, three routes. Sealed: `glow_identity` 1,207, `glow_profiles` 4,893, `glow_discovery` 2,351, `glow_chat` 2,227 lines. Shared: `glow_domain` 8,854, `glow_persistence` 5,496 lines with 42 models and 12 migrations, of which 28 models have working code and 14 are definitions only (READER; migration count CODE) | RUN: `manage.py check` clean; 645 tests pass, one skipped for want of a Git checkout; Ruff and mypy clean. CI: 645 pass, none skipped |
| `packages/contracts` | 96 message definitions, 20 flows, 139 transitions, a 902-case corpus; generated types and validators the app imports (READER) | RUN and CI: 53 Python and 902 JavaScript tests; the generated files match |
| `proofs/postgres-ordering` | 36,123 lines of Python, more than the four sealed packages together. It imports the real `services/api` modules, not a copy (READER) | RUN: 377 offline tests. CI: 56, 115, 13, 62, 49, 77 and 66 cases pass on PostgreSQL 17.11 |
| `proofs/stream-chat` | The Stream harness, tied in code to the development application (READER) | RUN and CI: 648 offline tests; these show the harness agrees with its own stand-ins, not what Stream does today |
| CI | One workflow of eight jobs, and a branch cleanup. It makes **no native build, no deployment, no security scan, no dependency audit and no load test**, and uses no secret (CODE: `.github/workflows/foundation.yml`). No branch protection is configured (CI: `protected: false`; OD-52) | CI: `main`'s 21 runs since 26 October all passed at the first attempt (READER). Run 44416436012 on `6edae78`: all eight jobs passed and the gate printed `Application checks passed` (CI, read myself) |

### 3.5 What a member and an operator can do today

**A member can do nothing.** There is no build to install, no server to reach and no way for two people to meet.

- Inside the development preview a person can walk through the sample screens. Ordinary sign-up ends at "profile incomplete": recommendations, likes, matches and chat open only from the "Development scenarios" screen (CODE: `apps/mobile/src/profiles/policy.ts:65-67`; `src/onboarding/store.ts:317`; `src/app/development.tsx:21`).
- A reload erases everything. Nothing is stored on the device (READER).
- No member flow makes a network call. One development-only request exists, and only the CI smoke script uses it (CODE: `apps/mobile/src/data/recommendations.ts`).

**An operator can do nothing.** There is no admin screen, no staff sign-in, no management command, no WordPress plugin and no deployed service (READER; `wordpress/` absent, CODE).

**What "done" has meant so far.** Each item's own acceptance was met, and I found no "done" claim without its merge and its CI run. But every item was accepted at sample-data scope or sealed scope. The step that turns those parts into a product has been placed in P10 and P11 each time, and it is larger than the plan shows (section 4).

## 4. Remaining work to launch

### 4.1 What the launch needs, as Nathan has decided it

- **Where and for whom:** the United States, all states, in English, through both stores, held by a US legal entity (OD-55).
- **The journey:** an email account; an adult check from a self-entered birth date plus the stores' age signals (OD-55); birth date, time and place, with the chart calculated at once (OD-61); a profile with gender, orientation, "looking for" and relationship status, each matched both ways, an age range and a home area (OD-60); photos kept in private Cloudflare R2 storage (OD-62); recommended people, then wider discovery; Like and Pass; a mutual match; text chat through Glow's own server with Stream behind it (OD-45); privacy-safe notifications.
- **Money:** a paid plan with no free plan, a two-week free trial at sign-up, the stores' billing in the apps, a Stripe link in the iPhone app and on the web, free accounts only as a staff grant (OD-69, OD-70). A founding-member offer follows the launch (OD-70, OD-71).
- **Safety and privacy:** block, report, moderation, appeals, support, pause, export and deletion (PF01 §1), run by one person (OD-23).
- **Operations:** a WordPress site for the public pages and the staff console, where every OD-60 setting can be changed (OD-19, OD-60).
- **Not in the first release:** identity verification (OD-68); a UK or EU launch (OD-55); resurfacing, undo and rematch, built as settings and switched off (OD-60).
- **The look and the words:** the brand's design system and interface standard, in `glow-docs` under `docs/brand/`, tentatively approved (BD-12). They name the product's signature screen, the **connection view**: a band (Cool, Open, Warm or Glow) for each of ten categories, with the member's own line and the shared line, and never a number.

### 4.2 Work that no item owns today

M05 found that the plan placed the production server in no phase. The same has happened again for five larger pieces. Each is a finding with a proposed home; PF01's revision 1.19 (section 10) places them.

| # | What is unplaced | Evidence | Proposed home |
|---|---|---|---|
| P-01 | **The app's real client.** No item builds the app's connection to the server: an HTTP client, sign-in tokens in secure storage, and real transports for identity, consent, birth details, profile, fields, filters, area, photos, discovery and interactions. No item builds the screens for what Nathan has decided since P04: the OD-60 fields and "show me" sets, the required birth time, OD-64's notice, the paywall and trial, block and report, pause, deletion, export and help. The records give it one bullet under "Carried to P10" and the words "P11's client wiring" | READER: 26 of 47 non-screen modules, 86% of those lines, are sample back-ends or bound to them; only chat and notifications have a seam. CODE: no reference to the server's request types | New items AC1 to AC3, and each later phase builds its own screens on the real client |
| P-02 | **The server side of safety, privacy, support and billing.** PF01 §8 says "the ORM persistence adapters of each domain are built as four slices", but the four slices cover identity, profiles and media, discovery and interactions, and chat. Reports, cases, appeals, support, export, deletion and entitlements have tables and formats only | READER: 14 of 42 models have no behaviour; F14 to F18 and F20 have no route | P07 and P08 build their server parts as the slices were built: on a throwaway PostgreSQL in CI, sealed |
| P-03 | **The composed server and the worker.** Each slice is proven alone, under its own test settings. Nothing composes them: no served settings module, no secret loading, no PostgreSQL driver in the API's dependency locks, no worker, no event consumers. The plan leaves all of it to "P11 wires it", which makes P11 a build phase again | CODE: `glow_api/settings.py`, `Dockerfile`, and the API's lock files, which hold no PostgreSQL driver; READER (the API runtime reader) for the rest | New item SV5, before the app client |
| P-04 | **The real provider adapters.** R2 and a photo processor, mail, push, Stripe and the stores, Stream's runtime client and its drift check, and HDE. The records say "P11 builds" each one | RECORD: OD-62; the P11 plan, lines 93 to 98, 132, 146, 151 | Each adapter is built in the phase that owns its feature, once its account line is approved; P11B then proves them together |
| P-05 | **The design system.** `glow-docs` holds a note of 14 November listing seven candidate items (DS-1 tokens, DS-2 type, DS-3 navigation and icons, DS-4 icon and splash, DS-5 the connection view, DS-6 the store listing, DS-7 production copy), "none is placed". The app repository does not mention the brand work at all. The interface standard predates OD-68 to OD-71: it has an identity-check screen and no paywall, trial or export screen | CODE (in `glow-docs`): `docs/ephemeral/brand/GLOW-BRAND-app-handoff-note-v1.0.md`; `docs/brand/interface.md` | DS-1 to DS-3 with AC1; DS-5 with AC3; DS-7 with each screen's item; DS-4 and DS-6 with P09 |
| P-06 | **OD-64's limits** (two changes per field in 30 days, the notice, the review signal). "Its own brief", with no ID, no brief and no Work Register row | RECORD: `carried-to-later-items.md:112-117`; NOTION | New item SV2-L, after SV5 |
| P-07 | **SV4 is larger than its line.** By what is carried to it, it is chat's routes, a rewrite of the reads' rule (C-08), the block's redesign (C-01, C-02), a member's match list, the whole server side of notifications with a migration, a sweep for expired sessions, the fraud-ban records, and rematch | RECORD: `carried-to-later-items.md:119-133`; READER | SV4 in two stages; rematch stays off and unbuilt until Nathan wants it |
| P-08 | **The public site.** The privacy policy, terms, community rules, child-safety standards, support and deletion routes and the Stripe checkout page are inputs the stores ask for, and none is drafted. Its domain and hosting are in no cost line | RECORD: the matrix, AP-27 and GP-18 ("none drafted"); READER (the gates reader) | P07.1 drafts the policies; P07.3 builds the site with the staff console; M07 costs the domain and hosting |
| P-09 | **HDE's side of the integration.** The app's plan treats HDE as a contract to be delivered. HDE's own canon, now readable in `glow-docs`, shows more: the pair read is built in HDE's repository, and the way an app member's chart gets into HDE is not (section 4.5) | CODE (in `glow-docs`): PF05 v2.5.7, sections 1, 5.1.0, 5.1.7 and 5.9 | Research item A01-R, then Nathan's scheduling in HDE's process |
| P-10 | **Today's state of the requirements matrix.** Its state column is a 1 November snapshot: 0 of 340 rows read "met", and about 34 rows still read "not applicable" though the paid launch switched them on. PF01 §7's release gate needs each row's state | READER (the gates reader) | A dated refresh of the state column, with P07.1's brief |

### 4.3 The ordered work items

One build item runs at a time (OD-29). The owner's track runs beside it, because it is Nathan's own action and waits on other people, not on a session. PF01 §8 already allows a second register entry for "a concrete asynchronous operation".

**Sizes** use the completed items as the measure (section 4.6): **R** is a research or policy item of one or two sessions; **S** about 4 sessions; **M** about 5; **L** about 12; **XL** 25 or more. A session is one Nathan starts by hand: an implementation, a review or a correction.

#### The owner's track (start now; none waits on the build)

| # | Item | Delivers, and acceptance | Size | Waits on | Unblocks |
|---|---|---|---|---|---|
| O1 | **M07, the costed list** | Every account and service completion needs, each with its published price rechecked and dated, its lead time, who opens it and which item first needs it. Accepted when each line of the reader's table (legal entity and D-U-N-S, Apple, Google, Expo's build service, Railway, Stream, R2, mail, push, Stripe, the stores' billing library, a domain and WordPress hosting, monitoring, the photo and CSAM checks, GitHub Actions once private, legal advice) has a price or "no public price", and Nathan can approve or decline each | R | An environment that reads public price pages (OD-40) | Every approval below; the \$0 budget (OD-12) holds until a line is approved |
| O2 | **The US legal entity and its D-U-N-S number** | The entity that holds the store accounts and the service (OD-55). Recorded lead time: the D-U-N-S number alone can take up to 28 days (the matrix, GP-57) | Nathan's action | His approval of the line | Apple and Google organization accounts; Stripe; the policies' named operator |
| O3 | **A01-R, HDE's canon read against the contract request** | Each of the 35 questions answered from HDE's canon, with its document, section and version, or marked "not in canon"; a draft receipt; the list of what HDE must still build for the app. Accepted when Nathan can set a date in HDE's process from it | R | `glow-docs` attached (done) | O4; the HDE adapter; DS-5 |
| O4 | **HDE's work for the app, in HDE's own process** | A supported way for an app member's birth details to become a chart in HDE, and the pair read proven live. This is HDE work under HDE's rules; no app session may do it (PF01 D08) | Unknown; HDE's | O3; Nathan's date | Every real profile; P11B's PV01 and PV02 |
| O5 | **Store accounts, Expo's build service and release authorization** | Apple and Google organization accounts, an Expo project and signing. Opening an account starts store deadlines, so each account's matrix rows are rechecked first | Nathan's action | O1, O2 | P09.2 |
| O6 | **Stripe's account and its approval** | Stripe accepts a dating service "only after Stripe's review" (A05-V2's record) | Nathan's action | O1, O2 | P08.3 |
| O7 | **The other accounts:** Cloudflare R2, mail, push, Railway app services, a domain and WordPress hosting, monitoring, and Stream's production plan | One approval each. The Stream Maker application has been pending since 25 September, with no status recorded after 26 October | Nathan's action | O1 | Each adapter (P-04); P11B |
| O8 | **A05's third message** | Retention, the operators and their response times, and the launch values OD-60 left open (the orientation list, the distance choices, the photo limits). The manager writes it; the Dev Manager reads it first | No session | — | P07.1's brief |
| O9 | **Legal advice** | On the founding-member offer's form, before it is sold (OD-71). Whether to take advice on the paid plan's terms and the policies is Nathan's (D-12) | Nathan's action | O1 | The offer; optionally P07.1 and P08.3 |
| O10 | **Final approval of the brand standards** | The interface and copy standards and the icon files are tentatively approved (BD-12). The interface standard needs its paywall, trial, export and deletion screens added in `glow-docs` first | Nathan's action, with a brand session | — | AC1 (DS-3), P09.3 (DS-4, DS-6) |

#### The build track (one item at a time)

| # | Item | Delivers, and acceptance in a sentence | Size, with its basis | Depends on | External gates |
|---|---|---|---|---|---|
| 1 | **SV4 Stage A: chat's routes** | Send, history, list and read cursor served by sealed routes; the reads follow OD-60's rule; a member can list their matches; a block retires old likes and no longer reveals its direction; the dormant token code is removed or sealed (P06.2-T, folded in). Accepted on a fifth database suite in CI | L to XL. SV2 took 12 sessions and 8 Dev Manager reads; SV3, 27 and 21 | SV3; the Dev Manager's answer on the epoch bump | None |
| 2 | **SV4 Stage B: the server side of notifications** | Settings and device registration stored and served, with the migration the model needs; the triggers; a sweep for expired sessions; the records of who received a member's messages | L | Item 1 | None; real push waits for P09.2 |
| 3 | **SV5: the composed server and the worker** | One settings module and URL file that serve every slice together under the real configuration loader, with a PostgreSQL driver in the API's own locks; a worker that consumes every event type; a refusal in every sample adapter outside development and test (C-04); a full journey from sign-up to a sent message, through HTTP, on the throwaway database in CI. The container image and the three served routes stay as they are until P11 | L. No past item is of this kind | Items 1 and 2 | None. The mail adapter can be added here once its account exists (O7) |
| 4 | **SV2-L: OD-64's limits** | Two changes per field in a rolling 30 days for gender, orientation and relationship status, as a console setting; the review signal for P07. The birth-date lock waits with identity verification | S. SV2-R took 4 sessions | Item 3 | None |
| 5 | **AC1: the app's foundation** | The brand's tokens, type and three-tab navigation (DS-1 to DS-3); an HTTP client with a production address setting; tokens in secure storage with one refresh at a time; sign-up, verification by code, sign-in, recovery and sign-out against the composed server. Accepted when the rendered suite runs that journey against the server in CI, with no sample back-end in its path | L. P06.2-F, the nearest past item, took 14 sessions for 61 lines of app code; this is new work, so the basis is weak | Item 3; O10 for DS-3 | None |
| 6 | **AC2: onboarding to a visible profile** | Consent, the adult check, birth details with a required time, profile, the OD-60 fields and "show me" sets with OD-64's notice, the home area, photos uploaded by grant, and the completion read | L to XL | Items 4 and 5 | R2 and the photo processor (O7) for a real upload; until then the server's stand-in |
| 7 | **AC3: discovery to conversation** | Recommended and Explore on the server's page route; the profile with the connection view (DS-5), showing "Not ready yet." until HDE answers; Like, Pass, the match list, the conversation, and the notification settings | L to XL | Item 6 | HDE (O4) for a real connection view |
| 8 | **P07.1: safety policies and the operator's duties** | The privacy policy, terms, community rules and child-safety standards as drafts; the state notices' statutory text; the choice of CSAM detection and the reporting route; a capacity plan for one operator with the 48-hour and 24-hour clocks; the matrix's state column refreshed (P-10) | R to M; documents and decisions | O8; decisions D-03 and D-08 | NCMEC registration; optional legal review (D-12) |
| 9 | **P07.2, with P07.2a: block, report, cases and appeals** | Report and block from every profile, photo and conversation, on the server and in the app; cases, evidence, reasoned actions and appeals; the route for people who are not members; the second block writer's proof case first | L to XL | Items 7 and 8 | The detection service, if D-03 chooses one |
| 10 | **P07.3: staff sign-in, the staff API and the WordPress site** | Staff accounts separate from members'; a scoped, audited staff API; a WordPress plugin with the moderation queue, every OD-60 setting, the staff grant and the photo check's toggle; the public pages. Accepted against a throwaway WordPress in CI | XL. No past item is of this kind: a second language and a second product | Item 9 | A domain and hosting (O7) for the real site |
| 11 | **P08.1: retention, export and holds** | The retention schedule as built rules; the member's export; what a new consent version asks of existing members; the legal hold that survives deletion | M to L | Item 8 | None |
| 12 | **P08.2: account deletion** | Access and visibility end at once; a durable purge across Glow's data, Stream, R2, push and mail, with retries; a restore replays the deletion | L | Items 3 and 11 | HDE's deletion answer (O3) for the engine's part |
| 13 | **P08.3: the paid plan** | The stores' subscription with a two-week trial; the Stripe link and its web checkout; verified events from all three; entitlements; the staff grant; what a member without a plan can do (D-05). Accepted on the stores' and Stripe's test modes | XL, in stages. No past item is of this kind | Items 7 and 10; decisions D-04, D-05 and D-11 | O5, O6 |
| 14 | **P09.1: security and abuse controls** | Rate limits, malicious-input cases, the threat model PF01 asked of P02, and a disposition of each finding | M | Item 13 | None |
| 15 | **P09.2: native builds** | Signed iOS and Android builds on a named device matrix; real push permission and device registration; the stores' age signals; Android's Restore Credentials before April 2027; the photo picker on a real phone; every screen heard with VoiceOver and TalkBack | L to XL. No device run has ever been made | Item 7 | O5; an equipped workstation or a hosted build service, which no cloud session has; Nathan's authorization for release work (`apps/mobile/AGENTS.md`) |
| 16 | **P09.3: observability, runbooks and store evidence** | Monitoring and alerts; the runbooks; the store listings, icon and screenshots (DS-4, DS-6); the privacy labels; the reviewer account | M | Items 8 and 15 | O5; a monitoring account (O7) |
| 17 | **P10: readiness** | The whole journey and the safety and privacy cases run on the composed server; every deferred claim has a test and an owner; the packet P11 needs | M | Items 1 to 16 | None |
| 18 | **P11A: the rest of the throwaway-database proof** | What the slices did not show: the move-out path by dump and restore, an upgrade with a backfill, the role preflight, timeouts and connection exhaustion, crash recovery with the worker | M | Item 17 | None |
| 19 | **P11B: staging** | The app's own database and roles on HDE's PostgreSQL service; Railway services; every provider in its test mode together; the HDE adapter against the real engine; a restore drill; a load test with polling's lock traffic | XL, less whatever items 3 to 16 already built | Item 18 | O4, O7; the capacity check of the shared database (A02) |
| 20 | **P11C: production** | The reviewed migrations applied with the migration role; a bounded private smoke | M | Item 19 | Nathan's production authorization |
| 21 | **P12: the release candidate** | Every matrix row that binds, with its state (PF01 §7); the candidate's builds and commits; the rollout and rollback plan | M | Item 20 | Store review, external testers and public traffic are separate actions |

**After launch, by Nathan's words:** the founding-member offer (its one-time checkout, the count of 1,000 and its terms), once the legal advice is taken (OD-71).

### 4.4 The critical path, and what can run beside it

- **The build track is the critical path.** Its 21 items run one at a time, so its length is the sum of them.
- **HDE's work for the app (O4) is the longest pole outside it,** and it is the one gate that can stop a launch outright. Without it no real profile can become visible (C-03). It has no date, the contract request of 25 September was never recorded as taken into HDE's process, and HDE's canon places the missing piece in "a future epic with the App user model" (section 4.5).
- **The account chain (O2, then O5 and O6) must start now to stay off the critical path.** It gates items 13 and 15, and its lead times are other people's: up to 28 days for a D-U-N-S number, then Apple's and Google's enrolment, then Stripe's review.
- **What can run beside a build item without two sessions touching the same code:** O1 and O3, which are research; O8; P07.1, which is documents and decisions; and the brand's own work in `glow-docs`. Under OD-29 each waits its turn today. Decision D-06 asks whether research and policy items may run beside a code item.
- **What cannot be reordered:** SV5 before the app client; AC1 before any real screen; P07.2 before P07.3; P08.1 before P08.2; the store accounts before P09.2; HDE before a real connection view.

### 4.5 HDE, as its own canon states it

Until this session no app record was written from HDE's documents. Nathan attached `glow-docs`, which holds HDE's canon, on 18 November. One reader began reading it against the contract request and was stopped by a usage limit; I then read the parts below myself. This is a partial read, marked CODE (in `glow-docs`, at `707da56`).

- **The pair read exists in HDE's repository.** `POST /api/reader` with `v=1` or `v=2` takes two member UUIDs. Version 1 returns the Harmony band only; version 2 returns all ten categories, each as `{id, band}`. The answer carries no number (PF05 v2.5.7, sections 1 and 5.1.0).
- **The narrative lines have their own route:** `GET /aux/narrative?v=1`, by category, band and perspective (`shared`, `a_to_b`, `b_to_a`) (PF05, section 5.7).
- **It is not proven live.** "Reader v1/v2 success used injected rows in-process"; "live DB Reader success over live HTTP remained blocked by environment and deferred to a future epic with the App user model"; "Release admission and deployment remain distinct" (PF05, section 5.1.7).
- **How a member's chart gets into HDE is not built.** The read looks each person up in HDE's own table and "performs no write, request-time vendor call". The route that would create a chart, `POST /_ops/bodygraph/resolve`, was not found in HDE's repository, and the command beside it has "DB/auto resolution" as "a stub" (PF05, sections 1 and 5.9). HDE takes charts from an outside vendor's API, and production calls to it are marked "Speculative" (PF05, section 1).

**So:** A01 is no longer only "a contract with no date". The read the app needs is specified and largely built. What is missing is HDE's side of member sign-up, which Nathan's own direction (OD-61: the chart "is calculated immediately when someone signs up") depends on, and a live deployment the app may call. That is HDE work, in HDE's process. The app's contract request also predates OD-61 and should be re-read against the canon (finding R-27). Item O3 does both.

### 4.6 Sizing: the basis, and its limits

**The measure** is the items completed since 26 October (GIT for dates and sizes; RECORD, from each brief's "Sessions" section, for the counts):

| Item | Sessions Nathan started (implementation, review, correction) | Dev Manager reads | Pull requests | First brief to last merge |
|---|---|---|---|---|
| P09.3a, A05-V, A05-V2, A05-V3, M08 (research) | 1 each | 1 to 3 each | 1 or 2 each | Same day |
| M04, P06.3, SV2-R (small) | 4 each (1, 2, 1) | 1 to 3 | 1 | Same day |
| SV1 (medium) | 5 (1, 2, 2) | 6 | 1 | One day |
| SV2 (large) | 12 (2, 5, 5) | 8 | 2 | Two days |
| P06.2-F (mobile) | 14 (1, 6, 7) | 6 | 1 | Seven days, four of them idle |
| SV3 (very large) | 27 (4, 12, 11) | 21 | 3 | Six days |

In those 24 days, 15 had commits. Nathan started 78 sessions and carried 63 Dev Manager consultations (section 8.1).

**The range.** Count R as 1 to 2 sessions, S as 4, M as 5 and L as 12. Count an item sized "L to XL" as 12 to 27, which is SV3's measured count, and an item sized XL outright (items 10, 13 and 19) as 25 to 35. The 21 build items and the two research items O1 and O3 then sum to 225 at the low end and 343 at the high end. I round that outward to **about 200 to 350 sessions**, with about 0.8 Dev Manager consultations for each session at November's ratio (63 for 78). That is three to four and a half times the 78 sessions started since 26 October. I give no calendar date (PF01 §11).

**Why the range is wide, and where it could be wrong:**

- **Six items have no past item of their kind:** the composed server, the app client, the WordPress site, the paid plan, native builds and staging. Their sizes are my judgment against the nearest past item, not a measurement.
- **Corrections, not first builds, decide the size.** SV3's first builds were 4 sessions of 27. The cost rose with concurrency and with the proof's own tooling, not with the size of the application code (section 8, K-03).
- **The external gates add waiting that no session count shows.**
- **The range assumes the process stays as it is.** Section 8 says what a change could save.

### 4.7 The recommended next item

**M07, the costed list, and directly after it A01-R, then SV4's brief.**

- M07 is one research session. Every account, and the legal entity before them, waits on Nathan's approval of a line it prices. The account chain has the longest lead time he controls, so each day M07 waits is added to that chain.
- A01-R is one research session. It turns the one gate that can stop the launch into a dated piece of HDE work.
- Neither changes code, so neither can disturb SV4. If Nathan answers D-06 with yes, both run beside SV4's brief and cost the build track nothing.
- SV4 then starts with its real scope (P-07) and with defect C-01 in its brief.

## 5. Nathan's decisions still open

Each is in OD-32's form: what it is, what breaks without it, the options and a recommendation. The first seven shape the path; the rest fall due with a named item. None is legal advice. Where a recommendation rests on a record, the record is named.

### The seven that shape the path

- **D-01: HDE's work for the app.**
  - **What it is:** the date, in HDE's own process, for a supported way to turn a member's birth details into a chart, and for a deployed pair read the app may call (section 4.5).
  - **What breaks without it:** no real profile can become visible, so there is no launch. Everything else can be finished and still not ship.
  - **Options:** (a) commission A01-R now, then set the date from its gap list; (b) set a date now, without it; (c) leave it in HDE's process with no date, as today.
  - **Recommendation:** (a).
- **D-02: the costed list first, and the legal entity now.**
  - **What it is:** whether M07 runs next, and whether the US entity and its D-U-N-S number start before the build needs them.
  - **What breaks without it:** the store accounts gate native builds (item 15) and Stripe gates the paid plan (item 13). Their lead times are other people's and start only when Nathan acts.
  - **Options:** (a) M07 next, and the entity as soon as its line is priced; (b) M07 when P09 nears, as recorded today; (c) form the entity now, outside the list.
  - **Recommendation:** (a).
- **D-03: what checks a photo before it is shown.**
  - **What it is:** at today's defaults a member's photo is shown with no staff review (OD-61), no automated check (OD-68) and no detection of known child sexual abuse material (no choice made). Apple asks an app with user content for "a method for filtering objectionable material from being posted" (the matrix, AP-05, with AP-06 and GP-04).
  - **What breaks without it:** a likely rejection at review, and real harm with one operator to answer for it.
  - **Options:** (a) the automated check on at launch, with hash matching for known material; A05-V's record prices the check from \$0.001 an image and lists free hash-matching tools; (b) hash matching only, the check off, and the review risk accepted; (c) staff review before a first photo shows, which reverses OD-61.
  - **Recommendation:** (a). The toggle OD-68 asked for already exists, so this is a launch value and a cost line, not a rebuild.
- **D-04: the plan and its price.**
  - **What it is:** the paid plan's name, price and billing period (A06). The trial's length is set: two weeks (OD-70).
  - **What breaks without it:** P08.3's brief cannot define the store products, the paywall's words or the terms.
  - **Options:** his to set. The records propose none, by design.
  - **Recommendation:** decide before item 13's brief; nothing earlier waits on it.
- **D-05: what a member without a plan can do.**
  - **What it is:** whether a lapsed trial, a failed payment or a cancelled plan hides the member's profile, stops their likes and messages, or only stops new activity. The records leave it to P08.3's brief (DM-91).
  - **What breaks without it:** the entitlement's design, and what matched members see when one of them lapses.
  - **Options:** (a) the profile stays visible and conversations stay readable, but no new like or message; (b) the profile is hidden until the plan resumes; (c) full access continues for a grace period, then (b).
  - **Recommendation:** (a), which matches OD-60's rule that a stopped conversation stays readable. It goes to the Dev Manager with P08.3's brief first.
- **D-06: research and policy items beside a code item.**
  - **What it is:** OD-29 allows one task and one session at a time. Six of the remaining items change no code: M07, A01-R, A05's third message, P07.1's policies, the matrix refresh and the brand's work.
  - **What breaks without it:** each waits behind a code item, and the account chain and HDE's date wait with them.
  - **Options:** (a) a Markdown-only research or policy item may run beside the current code item, each still with its own prompt and message, as M08 ran beside SV3's review by Nathan's exception of 16 November (OD-66); (b) keep OD-29 as it is.
  - **Recommendation:** (a).
- **D-07: what a correction pass and a Dev Manager read are for.**
  - **What it is:** since 26 October, 28 correction passes ran. All seven of P06.2-F's, and seven of SV3's eleven, changed no application code; they changed one test file, the proof's own tooling, or records. Of 63 Dev Manager entries, 36 were on findings, corrections, stops or pre-merge reads. It issued about 730 numbered conditions; about 650 were accepted as written and none was declined (section 8.1).
  - **What breaks without it:** the remaining 200 to 350 sessions are sized at this rate.
  - **Options:** (a) a correction pass is commissioned only for a defect in application behaviour, a security boundary or a false claim; a gap in a static scan or a record is written down as a limit and carried, as the Dev Manager already ruled twice in SV3 (DM-68, DM-78); and the Dev Manager reads a code item at two points, its brief and its pre-merge read, plus the charter's triggers; (b) keep today's practice.
  - **Recommendation:** (a). It changes the manager workflow and PF02, so the Dev Manager reads the text first.

### Those that fall due with an item

| # | Decision | What breaks without it | Options, with a recommendation | Due before |
|---|---|---|---|---|
| D-08 | **CSAM detection and the reporting route** (the matrix, G-02): which detection tool, the NCMEC registration, the named contacts | P07.1 cannot be written; Google asks for a named child-safety contact (GP-22) | The tools and prices are in A05-V's record, section 7.4. Recommended: decide with D-03, since one service may do both | Item 8 |
| D-09 | **The founding-member offer's place.** Five state laws bar a dating contract "measured by the life of the buyer", and four make one void (A05-V3's record; OD-71 already requires legal advice before it is sold) | Nothing on the launch path, if it stays after launch | (a) keep it after launch and take the advice before it is built, recommended; (b) build it with P08.3 | Before the offer is built |
| D-10 | **Stream:** the Maker application's status, the production plan (\$399 a month billed yearly, or \$499 monthly, at 28 September), and Video and Feeds in production | No production chat application can be configured | Report the application's status now. The offer's revenue may also end Maker eligibility ("under \$10k monthly revenue") | Item 19 |
| D-11 | **The billing library:** RevenueCat, or the stores' own libraries with Glow's server verifying | P08.3's design. PF01 §4 still says "RevenueCat/store SDKs if monetization is selected" | A design choice for the Dev Manager first; it reaches Nathan as a cost line | Item 13 |
| D-12 | **Legal advice beyond the offer:** the paid plan's terms and renewal notices (only three states' renewal laws were read), the state dating-service laws, and the policies | A void contract or a wrong notice found at launch | His, as DM-31 recorded. Recommended: one review of the terms and the paywall before P08.3 ships | Item 13 |
| D-13 | **Where the app's database lives.** OD-18 places it on HDE's PostgreSQL service, which a record of 23 September puts in a European region; the launch is the US only | Latency for every request, and US members' data stored in the EU, which the privacy policy must state | (a) keep OD-18; (b) the app's own PostgreSQL in a US region, which ADR 0004 keeps possible. Recommended: check the region and the shared service's capacity (A02) before deciding | Item 19 |
| D-14 | **The brand standards:** final approval, and whether the priorities screen is in the first release (BD-06, BD-12) | AC1's navigation and every screen's copy rest on a tentative approval | Approve the interface standard once it gains the paywall, trial, export and deletion screens (O10). Priorities: after launch, recommended; version 1 of the pair read returns Harmony only | Item 5 |
| D-15 | **The session lifetime:** an absolute 30 days today (DM-45) | Sign-in cannot be served | (a) 30 days, absolute, recommended for launch; (b) a sliding window, which needs new reviewed code | Item 19 |
| D-16 | **The public site:** its domain and its WordPress host | P07.3 has nowhere to ship; the stores need the policy URLs | A cost line in M07 | Item 10 |
| D-17 | **Release work:** an Expo project, signing, native builds; later store submission and testers | P09.2 | His authorization each time (`apps/mobile/AGENTS.md`; PF01 §10) | Item 15 |
| D-18 | **Two unanswered questions of the Dev Manager's:** whether its read of governing Markdown stands (DM-01 question 2, open 55 days), and what the `AWS_*` names in both app environments are for (DM-57) | Every governing read rests on an inference; three credential names sit in every session unexplained | One line each | Now |

## 6. Record accuracy

No record disagrees with Git on a pull request number, a merge commit, a parent or a merge date, and every CI count the records give matches the runs (READER, across 54 pull requests and 174 cited run IDs; GIT). The findings below are of three other kinds: a record that describes an earlier state as the present one, two records that disagree, and a follow-up with no home or no owner.

Each row gives the place, what it says, what is true with its evidence, and the correction. "PF01 1.19" means I applied the correction myself on this branch under Nathan's authorization (section 10); every other correction is proposed for the manager.

### 6.1 Records that disagree with the code, the runs or another record

| # | Where | It says | What is true | Proposed correction |
|---|---|---|---|---|
| R-01 | The owner-direction register | It ends at OD-72 | Nathan gave three directions in this session (section 1.1) | Add two rows. **OD-73, 18 Nov 2026:** *"When complete, I authorize you to update the implementation plan in Notion and pfcanon to ensure the most efficient, thorough, and effective path to completion."* State: "In force for M09's session: it revised GAPP-PF01 on its own branch, for the Dev Manager's read before the merge, and the plan in Notion (the M09 record, section 10)." Home: the M09 record; PF01 1.19. **OD-74, 18 Nov 2026:** *"you can add to the plan that all HDE docs and initial UI/UX design system is available in glow-docs, which will be attached to all sessions going forward"*, with his direction before it, *"Clone the repository amthorn78/glow-docs into this session."* State: "In force. Every session has `amthorn78/glow-docs` attached: HDE's canon under `docs/hde/pfcanon/`, read-only, and the brand's design system under `docs/brand/`. No app session writes there." Home: PF01 §2 and §5 (1.19); `CLAUDE.md`'s environment paragraph |
| R-02 | PF01 §2, the "Application repository" row; root `README.md:3` | "Private `amthorn78/glow-dating-app`"; "Private monorepo" | Public since before 26 October (OD-51); CI: 0 billable milliseconds on a 1,014-second run (READER) | PF01 1.19: "`amthorn78/glow-dating-app`, default branch `main`; public for now, to be made private again (OD-51)". README: "Monorepo (public for now, OD-51)" |
| R-03 | PF01 A05 | "The open A05 questions (launch geography, age assurance, the preference taxonomy, resurfacing and rematch, the history policy, retention, moderation operators) go to Nathan … before P07's brief" | Five of the seven are answered (OD-55, OD-60) | PF01 1.19 states which are answered (OD-55, OD-60) and what the third message still owes: retention, and the moderation and support operators |
| R-04 | PF01 A06 | "no plan, price or trial length is set except by Nathan" | The trial is two weeks (OD-70, C4); a founding-member offer follows launch (OD-70, OD-71) | PF01 1.19 adds both |
| R-05 | PF01 §10, the autonomy table, against A04 | "Application-only Railway resource creation … do not invent a separate provisioning-approval gate" | Since OD-50 every Railway app service is a line of the costed list, created only after Nathan approves it | PF01 1.19 adds that sentence to the row |
| R-06 | PF01 §8, "Server slices" | "the ORM persistence adapters of each domain are built as four slices … SV4, chat's HTTP surface" | Four slices cover four domains; safety, privacy, support and billing have no slice (P-02). SV4 carries far more than chat's routes (P-07) | PF01 1.19 rewrites the paragraph |
| R-07 | `docs/continuity/state-of-the-app.md` | "As of: 26 October 2026"; "P06.3: Planned; no brief"; "M04: Ready"; "621 unit tests … 366 tests"; "the requirements matrix has not been built"; "the plan places the production server in no phase" | 21 merges behind. Today: 691 and 104, 645, 53 and 902, 648, 377; SV1 to SV3 merged; the matrix built on 1 November | The manager's refresh (its next action 1). Section 3 of this record is the input, and section 4 replaces its sections 5 and 6 |
| R-08 | Root `README.md:3`, `:34` | "P01–P05 are complete … New features are paused … P06–P12 remain open"; CI "repeats API, mobile and HTTP-client checks" | P06.1 to P06.3 and SV1 to SV3 are merged; the pause ended with OD-49; CI has eight jobs | "P00 to P06 and the server slices SV1 to SV3 are merged, at sample-data or sealed scope; nothing is served or deployed. Status: the current handoff.", with "current handoff" linked to `docs/continuity/current-handoff.md`. And: "CI runs eight jobs (`.github/workflows/foundation.yml`)." |
| R-09 | `docs/planning/sv2-r-od-68-requirements-change.md:3`, `:6`, `:11-18` | "Status: approved at revision 6; correction C1 follows"; the problem is that "no profile can become `visible`", to be fixed "before P10" | It merged as PR54 at `6edae78` (GIT). The blocker is not gone: the chart requirement still has no writer (C-03) | Add after line 3: "**Status: done.** Merged as PR54 at `6edae78` on 18 November 2026 (final code head `f4c93ea`)." Add to "Why": "A profile still cannot become `visible` in any built code: the `chart` requirement waits for HDE's adapter (PF01 A01)." |
| R-10 | `docs/planning/sv2-profiles-media.md`, acceptance checks 9 and 10, and D9, D10, D18 | "completion is refused … without identity verification"; "approval and rejection are the automated check's decisions" | SV2-R changed both (CODE: `glow_profiles/requirements.py:24-29`) | A note under each: "Superseded in part by SV2-R (PR54; OD-68): identity verification is not a completion requirement while ID validation is set aside; while `media.photo_check` is off, its launch value, a photo is approved without the automated check." |
| R-11 | `docs/architecture/data-model.md:3-18`, `:149`, `:164`, `:167`, `:175`, `:201-202`, `:414` | "32 app-owned Django models and two migration files" … "a fourth migration"; completion needs "the chart and identity verification"; "only the automated check approves or rejects"; `visible` "carries VERIFIED"; the Stream adapter "implements the six operations" | 42 models and 12 migrations (CODE); SV2-R as R-10; seven operations (READER: `chat_provider.py:49-59`); the stored notification models do not match the contract (READER) | Opening: "42 models in migrations `0001` to `0012`: P02's 32, then chat (0003), SV1 (0004), SV2 (0005 to 0009), SV3 (0010, 0011) and SV2-R (0012). All run only under the proof's settings." Line 164 and 201: drop identity verification, with "(set aside by OD-68; SV2-R)". Line 167: as R-10. Line 175: add "These two models predate the contract's F12 fields; SV4 migrates them." Line 414: "seven" |
| R-12 | `docs/planning/store-legal-safety-requirements.md`: the header, section 1's summary, and the state column | "Nathan names the launch countries from this matrix before P07's brief"; "no launch jurisdiction … is chosen"; "95 do not apply now"; "84 have no owner"; UST-16 "no account-change notice is named"; AP-36, AP-50, AP-51, GP-51 "Planned" | The launch is the US (OD-55). About 34 store and US rows marked "not applicable now" bind since OD-69. Each "no owner" row was routed on 1 November. SV1 sends account-change notices (READER: `glow_identity/conf.py:109`); P06.3 merged. The column is dated `f40f1d7`, 1 November | Header: "**Launch countries:** the US, all states, in English, for now (OD-55). The UK and the EU stay candidates for a later launch." Summary: "The state column is as read at `f40f1d7` (1 November 2026). Rows marked 'if paid' bind since OD-69 and are P08.3's." Then a dated refresh of the column, with P07.1's brief (P-10) |
| R-13 | `docs/operations/migration-plan.md:50-52` and its table | It tables `0001` to `0003`; "They contain no `RunSQL`, `RunPython` … allauth is not installed" | Twelve migrations; `0006`, `0007`, `0009` and `0012` each hold a `RunPython` data step; allauth is installed in the development scope (READER; migration list CODE) | Add rows for `0004` to `0012`, and: "`0006`, `0007`, `0009` and `0012` each hold one `RunPython` data step; none holds `RunSQL` or a provider call. django-allauth's own migrations join the ledger at P11." |
| R-14 | `docs/testing/p11-deferred-acceptance.md:127`; the PV08 row | "`proofs/stream-chat/package-lock.json` holds `follow-redirects` 1.16.0 … Before that run, the lock moves" ; PV08 "only after A06 selects paid scope" | The lock holds 1.16.2 since M06 (CODE). A06 selected a paid launch (OD-69), and the plan names OD-69 to OD-71 nowhere (READER) | Line 127: "[Done by M06, PR38: the lock holds 1.16.2.]" PV08: "A06 selected a paid launch (OD-69 to OD-71): the stores' subscription with a two-week trial, the Stripe link, and later the founding-member offer." |
| R-15 | The review log, `docs/continuity/dev-manager/README.md`, "Deferred conditions" and "Sessions" | Row L133, SV1's threat model: "Open". L129: "Closes at P06.2-F's merge". L146: open for "each slice's brief". L217: the verification company's decision "Open". L17: Dev Manager 5 has "no consultation is pending; DM-67's … are confirmed at its next consultation" | SV1 merged on 9 November with the threat model in its record; P06.2-F merged on 8 November; SV1 to SV3 folded their pointers in; OD-68 set the verification company aside; DM-68 to DM-93 are answered (READER, with Git) | L133: "**Done:** the SV1 record, 'The review's threat model'; PR42, `c864edd`." L129: "Closed at P06.2-F's merge (PR40, `8031361`)." L146: "Open for SV4 only." L217: "Set aside for the MVP (OD-68); returns if ID validation is added, and before the photo check's toggle is first turned on." L17: "DM-68 to DM-93 answered; none pending; PF02 1.8 is tabled (OD-72)." Add rows for two carries the table lacks: DM-75's block design for SV4, and OD-64's brief. Add to DM-65's section that Nathan answered with OD-64 |
| R-16 | `docs/planning/carried-to-later-items.md:80`, `:85`, `:198-204`, `:236` | "The brief is written: … revision 6"; an entry "for the first of SV2 to SV4" kept under SV2; N-a, N-d, N-c "each entry closes when that correction merges"; P06.2-F's entries "stay until the item closes" | The brief is at revision 8; SV2 and SV3 are done and did not touch the file (GIT); PR54 merged; P06.2-F merged on 8 November | L80: "revision 8". L85: move to "Carried to SV4". L198 to L201: "Closed by SV2-R's correction C1 (PR54, `6edae78`)". L236: remove the three entries |
| R-17 | `docs/continuity/current-handoff.md:14`, `:17`, `:32` | "\$100 for life"; "follows DM-59 section 7"; PF02 1.8 covers "AM12-22 to AM12-28" | OD-71 defines "lifetime" as "for as long as Glow runs the service", and "for life" is the measure five state laws bar. DM-59's ruling was written for PR44 only (READER). The review log says AM12-22 to AM12-26, and the mistakes log now holds AM12-29 | "a lifetime subscription for \$100, 'lifetime' meaning for as long as Glow runs the service (OD-71)"; "is recorded in DM-59, item 7, written for PR44"; "AM12-22 to AM12-29" |
| R-18 | `services/api/README.md:184-186`; `docs/testing/api-foundation.md`, `contract-baseline.md`, `provider-conformance.md`, `domain-seams.md`, `mobile-foundation.md` | "allauth … remain unimplemented"; "15 tests", "16 packages", "199-case corpus", "29 tests pass", "Expo 57.0.24" | allauth runs in the development scope; the README never names `glow_identity`, `glow_profiles` or `glow_discovery`; the five testing files are 23 September snapshots that the READMEs still cite as current evidence (READER) | README: add one paragraph naming the three sealed packages, with "sealed until P11". Each testing file: a first line, "Snapshot of 23 September 2026. Current counts: the latest Foundation run on `main`." |
| R-19 | `apps/mobile/README.md:42`, `:358`, `:454`; `apps/mobile/.env.example:4-9`; `docs/architecture/onboarding-fixtures.md:16-17`, `:38-51` | "no chat action is available"; "Expo 57.0.24 and Router 57.0.22"; "push (P06.3)" as future; the API address setting switches "the API smoke flow"; the route table omits `/notifications` | Expo 58.0.22 and Router 58.0.29 (CODE); a match opens a conversation; P06.3 merged; no app code reads the setting (CODE) | Update the versions; add a notifications walkthrough to the README; say in `.env.example` that only `scripts/smoke.mjs` reads the setting |
| R-20 | `docs/operations/configuration.md:78`, `:139-171` | "The 32 P02 models"; a secret-slot matrix | 42 models; no slot for the JWT signing key SV1 needs; the flags and slots are read only by an offline validator and select nothing (READER) | "42 models"; add the JWT signing key and the identity settings' key as slots, marked "no loader exists; SV5 builds it" |
| R-21 | `docs/operations/ci-and-branch-policy.md:85`, `:93` | "**No application check reads Markdown content.**"; "require the gate as well when enforceable repository controls become available" | One contract test reads `docs/architecture/production-contracts.md` (C-15). Controls are available and Nathan chose none (OD-52); the replacement was due "with the CI policy's next change", which has passed 13 times (READER, GIT) | Line 85: "One application test reads Markdown: `packages/contracts/tests/test_transition_contract.py` reads one sentence of `docs/architecture/production-contracts.md`, so a change to that sentence is checked only by the next full run." Line 93: DM-34's own words, "require the gate as well only if Nathan chooses enforced controls (OD-52 chose none), after the change DM-33 6.2 names" |
| R-22 | `proofs/postgres-ordering/README.md:27`, `:34`, `:169`; `proofs/stream-chat/README.md:358`; `docs/architecture/production-contracts.md:3`, `:63`; `docs/architecture/chat-provider-permissions.md:66` | "migrations `0001` and `0002` apply"; it does not prove "allauth"; "two passwords and two markers"; the products comparison "has not been used live"; "Not implemented: … durable state transitions"; the flow index "is generated"; "For a production application the same plan runs" | Twelve migrations; the identity suite exercises allauth; the job makes two passwords, five markers and six keys; it ran live on 23 October; the sealed slices hold durable transitions; no generator exists; the harness refuses any application but the development one (READER) | One line each, in Appendix A |
| R-23 | `docs/architecture/trusted-eligibility.md:51` against `:196`; `services/api/glow_persistence/models.py:1-6`; the SV3 brief, Outcome items 1 and 8 | "no such adapter exists now"; "not a live ORM/repository implementation"; the adapter reads "identity verification"; routes for "matches" | The adapter exists, sealed (line 196 says so); three packages run ORM code over the models; no verification row is read; one match is read by ID and none is listed (READER; CODE for the last) | Line 51: "A conforming adapter exists, sealed (SV3)." The docstring: "Models used by the sealed slices; the served runtime installs none." The brief: strike "identity verification"; "a match, by its ID" |
| R-24 | `docs/architecture/privacy-and-safety-rules.md`; `docs/operations/providers-and-webhooks.md`; `docs/operations/environment-inventory.md` | "A05 owns resurfacing, rematch and existing-history choices"; "An accepted upload remains quarantined until … moderation succeed"; RevenueCat "Conditional"; no Stripe row; `GLOW_FEATURE_BILLING` "pending A06"; no mention of the `AWS_*` names | OD-60 answered the first; OD-68 turned moderation off at launch; OD-69 to OD-71 chose a paid launch with Stripe; both app environments hold three `AWS_*` names (found 11 November, DM-57; present in this session) | Add "[Answered in OD-60.]"; "[OD-68: while `media.photo_check` is off, a photo is approved after processing with no moderation step.]"; a Stripe row; "A06 is answered (OD-69)"; and to the inventory: "Both app environments hold `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_CA_BUNDLE`; values never read; their purpose is not recorded (D-18)." |
| R-25 | `docs/planning/p06-1-chat-provider-proof.md:252` | "Of 85 cases, 68 hold" | Its evidence record, corrected in C1, says 65 (READER) | "65" |
| R-26 | Notion: the Work Register and Implementation Control | 33 differences, listed in Appendix B. The chief ones: 11 of the 19 planned rows of P07 to P12 were last edited on 25 September; their "Depends On" fields name none of SV4, M07 or P07.2a; the P11 rows are P11.1 to P11.5 where the repository says P11A to P11C; A01 says the request "asks 29 questions"; A06 and P08.3 open with the paid choice as still to be made; Implementation Control says "Now: M08" and "PF02 … revision 1.4", and 72% of it is a status log of 327,089 characters | No row's State contradicts the handoff, and the register copy of the directions matches in all 72 rows (NOTION) | I corrected the plan rows under Nathan's authorization (section 10). The rest are for the manager; Appendix B lists them |
| R-27 | `docs/planning/hde-contract-request.md` | "Nothing was read from HDE's systems to write it"; C10 asks how "an uncertain or missing birth time" is handled; C13, "Can a chart be pending" | HDE's canon is now readable and answers part of it (section 4.5). Nathan, who owns HDE, has since said a birth time is required and the chart is calculated at once (OD-61) | Add to section 1: "Nathan, 10 November 2026 (OD-61): the chart is calculated when a member signs up, with no lag, and a birth time is required. Since 18 November 2026 HDE's canon is attached to every session in `amthorn78/glow-docs` (OD-74); A01-R reads it against C01 to C35." |
| R-28 | `docs/ephemeral/` | The workflow says each merge receipt prunes its prompts | 89 files for closed items remain, 84 of them from P06.1, P06.DB and P06.2; OD-45's link to its decision message is not pinned to a commit (READER; counts CODE) | One pruning batch, with OD-45's link pinned first (M05 finding 44, still open) |
| R-29 | PF01 §7 "Media" and §4's Billing row | "moderate before publication"; "RevenueCat/store SDKs if monetization is selected" | OD-68 turned the check off at launch; OD-69 selected a paid launch | Not changed in 1.19. The first is decision D-03. The second waits for P08.3's brief by the Dev Manager's own ruling (DM-85) |

### 6.2 Follow-ups with no home, or with a home and no owner

| # | Follow-up | Where it is today | Proposed home and owner |
|---|---|---|---|
| H-01 | **M02's hardening:** the Setup script's and the pin test's follow-ups, one a Codex finding of 25 September | The M02 brief; "Nathan schedules them"; undone after 55 days (GIT) | The next item that changes `scripts/` or the workflow; or closed as declined |
| H-02 | **P06.2-T** has no brief, and its "remove the `pyjwt` pin" can no longer be done: SV1 needs the package | The carried-items file; Notion places it before SV4 | Folded into SV4 Stage A (item 1), with the pin kept |
| H-03 | **Stream's terms 12.5** (Stream may show the customer's name and logo), **its data-processing addendum and its Trust Center**, all unread | Only in the closed P06.1 brief and record | "Carried to M07", with the Stream line; the addendum to P08.1's processor list |
| H-04 | **Four documents PF01 asked for and no item produced:** a threat model (P02), an SBOM (P01, §4), a ranking and provenance ADR (P05), a chat failure runbook (P06). No record defers any of them | Nowhere | The threat model to P09.1; the SBOM and the runbook to P09.3; the ADR to AC3, when HDE's bands arrive |
| H-05 | **The native code never run on a device** after the Expo 58 upgrade (React Native 0.88.1, Hermes, the gesture and animation libraries), and OD-54's re-check of three advisories "before P09" | Only in M06's brief and record | "Carried to P09", for P09.2 |
| H-06 | **The chat screens' view models** (DM-38), owed "at the latest before P11 serves the chat reads" | Three places, and no item | AC3 (item 7), which rebuilds how the chat screens hold their data |
| H-07 | **OD-64's limits** | "Its own brief"; no ID | SV2-L (item 4) |
| H-08 | **Five fixes due "at the next change" to a file, each passed over when the file changed:** the Chromium install's retry (twice); the CI policy's gate sentence (13 times); the chat fixture's `already`; an optional PF01 wording (DM-44 item 8); a docstring in the proof's identity support (DM-50 1.2) | The carried-items file and the review log | Give each an owner, not a trigger: the first to SV4 Stage A's workflow change; the second is R-21; the others to the item that next touches the file, named in its brief |
| H-09 | **M05's findings 15, 27 and 44, and the rest of finding 5** (P09's and P10's acceptance words a session cannot check) | "Optional work items"; no home | 15 and 27 closed as declined, or taken with the next change; 44 is R-28; the rest of 5 is in PF01 1.19 |
| H-10 | **SV1's recorded loose ends:** the reset code's limits are untested; which refusal answers a suspended sign-in; a 10-second window in which a taken address can be told from a free one; the mail's wording "before P11 sends mail" | SV1's record, with no owner | SV5 (item 3) for the tests; the mail's wording with DS-7 |
| H-11 | **What a worker would do, written down nowhere as work:** consumers for the events that have none, how long delivered events and stored request keys are kept, clearing a reconciliation mark, and abandoned uploads | "P11's", in four documents | SV5 (item 3) |
| H-12 | **The P11 plan's rows have no owner.** PF01's P10 requires that "every deferred claim has a real integration test and owner" | `docs/testing/p11-deferred-acceptance.md` has no owner column | An owner column, filled at P10 |
| H-13 | **Questions no record asks:** tax on store and Stripe sales; who writes and approves the privacy policy and the terms; a mail provider; a monitoring tool | Nowhere | M07 for the last two; D-12 for the first two |
| H-14 | **G-01, age assurance,** is a Work Register row with no brief and no repository home | Notion | P09.2's brief folds it in; the row then closes |
| H-15 | **Production payload and rate limits, and HTML-safe rendering,** "still belong in real adapters/UI" | `docs/testing/contract-baseline.md:36` | P09.1 |
| H-16 | **A05's third message** is owed, and four documents each send it something more (photo limits, how long originals are kept, how long request keys are kept, the hold); no draft exists | The carried-items file, in part | One list under "Carried to P07", before the manager writes the message (O8) |

## 7. Findings in the code and in CI

These bear on a "done" claim or on what the remaining items must build. None is a broken boundary: I found no HDE call, no database connection outside CI's throwaway one, no credential in the repository, and no provider data shown to a member. Severity follows M05's scale: **major** blocks or endangers completion, or misleads a decision; **minor** is wrong but contained; **nit** is small.

| # | Finding | Evidence | Severity | Proposed route |
|---|---|---|---|---|
| C-01 | **A like made before a block survives the block.** On the server, block and unblock never touch the like records, and a match is made whenever a like exists each way, no block is active and no match exists. So: A likes B; either blocks the other and later unblocks; B likes A; a match and a chat channel are created on the old like. The app's own sample rules do the opposite: a block retires the likes in both directions, and a test asserts no match. No record decides to drop that rule | CODE, read by a reader and by me; not executed: `services/api/glow_chat/contact.py:645-714` (block), `:303-388` (`activate_reciprocal`); `glow_discovery/interactions.py:512-563`; against `glow_domain/interactions.py:694-698` and `tests/test_interactions.py:481-488` (`test_block_unblock_retires_old_unilateral_like`). A search of the SV3 brief and record, the interactions and contracts documents and the data model finds no decision | Major | SV4, which already owes the block's redesign (C-02): decide the rule, apply it in the block writer, and add a database case that fails without it |
| C-02 | **A block's direction can be inferred.** Only a block makes a match `restricted`, and the match read and the unmatch answer serve that state to both members. Known since SV3 Stage B's review and carried to SV4 (DM-75) | READER: `glow_discovery/interactions.py:235-242, 569-580`; RECORD: `carried-to-later-items.md:133` | Major | SV4, as recorded. Two of SV3's seven routes cannot be served until then |
| C-03 | **Nothing can make a profile visible.** Completion needs a resolved chart, and no application code creates or resolves one; the suites seed it by a direct write. SV2-R removed the identity requirement, so its brief reads as if the blocker were gone | CODE: `glow_profiles/requirements.py:20-22`; READER: no writer of `EngineIdentity` outside the proof | Major | The HDE adapter (section 4); correct the SV2-R brief's wording (R-09) |
| C-04 | **Sample mail and sample photo storage do not fail closed.** Identity defaults to an in-memory mail backend and a per-process cache, and profiles to in-memory storage, and neither package checks the environment. A production settings file that missed one override would send no email and keep photos in memory, silently. Discovery has such a guard, but it reads a value the same settings file sets | CODE: no `GLOW_ENV` or guard in `glow_identity` or `glow_profiles`; `glow_identity/conf.py:81-89`; `glow_profiles/media.py:94-95`. READER: `glow_discovery/policy.py:137-145` | Major | The composed-server item (section 4): one environment source that no settings module sets, and a refusal in every sample adapter. `AGENTS.md` asks that fixture-only guards be kept; these two never had one |
| C-05 | **At the launch defaults a photo is shown with no check of any kind.** No staff review (OD-61), the automated check off (OD-68), no detector chosen, and no real decoding. Apple's first requirement of an app with user content is "a method for filtering objectionable material from being posted" (the matrix, AP-05, with AP-06 and GP-04). No record weighs the two against each other | CODE: `glow_profiles/requirements.py:12-18`; READER: `glow_profiles/media.py:629-651`, `media_fixtures.py`; RECORD: OD-61, OD-68, the matrix | Major | Nathan's decision D-03 (section 5) |
| C-06 | **The photo rules would refuse ordinary phone photos.** PNG only, at most 1 MiB, with ceilings in code that no setting can raise | READER: `glow_domain/profile_settings.py:160-163, 287-296` | Major for launch | The real photo processor's design, with the R2 adapter (section 4) |
| C-07 | **No worker exists.** The outbox has one consumer class, built only inside the proof. Profile events and eight kinds of chat event have no consumer; stored idempotency records have no sweep; an uploaded photo would never leave `upload_pending` | READER: `glow_chat/delivery.py:48-50`; `glow_profiles/events.py:84-93`; no management command in `services/api` | Major | The composed-server item (section 4) |
| C-08 | **The chat reads implement a rule Nathan has since replaced.** They refuse a read whenever a send would be refused; OD-60 (H) makes a pause, a restriction, a suspension or a withdrawn consent read-only at launch. The setting exists and no chat code reads it. So P06.2 Stage C1's code and its 62 database cases change in SV4 | READER: `glow_chat/reads.py:228-295`; `glow_domain/profile_settings.py:274-280`; RECORD: `carried-to-later-items.md:125` | Major (known, carried) | SV4 |
| C-09 | **Four code gaps M05 named are unchanged:** the pin test does not read the Stream proof's `package.json` (finding 13); the API's refusal list is narrower than ADR 0004 says (22); every sent message's text is kept (23); the dormant client-token code remains (24) | READER, with the lines: `tests/test_toolchain_pins.py:14`; `glow_api/configuration_profiles.py:24-48`; `glow_chat/delivery.py:282-287`; `glow_chat/contact.py:407-456` | Minor (known, carried) | P06.2-T and P08, as recorded; fold P06.2-T into SV4 (section 4) |
| C-10 | **Sixty API tests named for discovery and interactions test the in-memory versions, not the server.** Every server behaviour that needs a row is proven only by the PostgreSQL suites in CI | READER: `tests/test_discovery.py`, `tests/test_interactions.py` | Minor | Retire or rename them when the sample back-ends are retired |
| C-11 | **Abandoned uploads count against the four-photo limit** until the member removes each | READER: `glow_profiles/media.py:442-443, 247-248` | Minor | The photo processor's item |
| C-12 | **Enumeration resistance was shown only with in-memory mail.** Mail is sent inside the request, and only to known addresses, so with a real provider the response time may differ for a known and an unknown address. Inferred; not tested | READER: `glow_identity/adapter.py:73-75`; `conf.py:100` | Minor | A P11B case with the real mail provider |
| C-13 | **Sign-in rate limits are kept in one process's memory,** and the entrypoint replaces its worker every 1,000 requests | READER: `glow_identity/conf.py:79-86`; `glow_api/runtime.py:52-53` | Minor | The P11 plan already asks for a shared cache; it should not wait for a second worker |
| C-14 | **The app's request keys restart at 1 on each launch.** Against a server that stores keys they would collide with earlier requests | READER: `apps/mobile/src/profiles/store.ts:176`, `media/store.ts:122`, `interactions/store.ts:57`, `onboarding/store.ts:147` | Minor | The app-client items (section 4) |
| C-15 | **The CI policy's "No application check reads Markdown content" is false.** One contract test reads a sentence of `docs/architecture/production-contracts.md`. A Markdown-only edit of that sentence would skip CI and fail the next code change's API job. It is the only such test | CODE: `packages/contracts/tests/test_transition_contract.py:699-707`; `docs/operations/ci-and-branch-policy.md:85` | Minor | Correct the sentence (R-21), or move the list out of Markdown |
| C-16 | **The Chromium install step is fragile and has no retry.** It took 8 minutes 30 seconds on `main`'s newest run and failed three runs on 11 November. Its recorded fix was due at "the next change" to the workflow, which has changed twice since without it | CI: run 44416436012, the step from 22:59:25 to 23:07:55 UTC; READER: runs 43044190450, 43046997028, 43050934985; GIT: `ad9ff08`, `39c0bf0` | Minor | Give the fix an owner: the next item that touches the workflow (H-08) |
| C-17 | **The two long CI jobs are near their limits.** On `main`'s newest run Mobile checks took 14 minutes 42 seconds of 25, and Database proof checks 16 minutes 32 seconds of 30. One job runs four suites in order, and SV4 adds a fifth | CI: run 44416436012 | Minor | Split the database job by suite when SV4's suite is added |
| C-18 | **The Stream harness works only against the development application.** No tool can yet apply or check the lockdown on a production application, the drift check OD-45 requires is not built, and nothing has checked Stream's configuration since 23 October | READER: `proofs/stream-chat/glow_stream_proof/credentials.py:14, 51-54`; no schedule trigger in either workflow | Major for launch | The chat provider's P11 work (section 4) |
| C-19 | **Smaller points.** `npm test` passes an unquoted `src/**/*.test.ts` to the shell, which matches one directory level only (READER, inferred). The identity suite's case count is not pinned (READER). `scripts/*.py` and the contracts' Python are not linted or type-checked in CI (READER). `EligibilitySnapshot.verified` now means only "visible" (CODE: `glow_discovery/eligibility.py:73-89`). A replayed like after an unmatch reports the old match's ID (READER) | As marked | Nit | The next change to each file |

## 8. Risks

Each risk gives its likelihood, its effect and what would retire it. PF01 §11's six risks are named where they apply.

| # | Risk | Likelihood | Effect | What retires it |
|---|---|---|---|---|
| K-01 | **HDE's work for the app does not arrive** (PF01's R02). The chart of a new member has no built way into HDE, the pair read is not proven live, and no date exists (section 4.5) | High. Nothing has moved it in 54 days, and by OD-32 the manager carries no standing line for it, so nothing prompts it | No launch: no profile can become visible | D-01: A01-R, then a dated item in HDE's process. The risk closes when the app's adapter has run against a deployed HDE in staging |
| K-02 | **The remaining build is larger than the plan showed.** Five pieces had no item (section 4.2), and the largest, the app's real client, had one bullet | Certain; it is a finding, not a forecast | Time. The work ahead is three to four and a half times the sessions started since 26 October (section 4.6) | PF01 1.19 places each piece. The risk shrinks at the first full journey, sign-up to a sent message, on the composed server in CI (item 7) |
| K-03 | **The process costs more than the remaining work can bear.** Measured below | High, if nothing changes | Time, and Nathan's own: he is the courier for every step | D-06 and D-07 |
| K-04 | **Accounts and lead times against a \$0 budget.** No account exists, no line is priced or approved, and the chain of entity, D-U-N-S number, store enrolment and Stripe's review runs on other people's clocks | High that it delays, unless started now | Native builds and the paid plan wait | D-02: M07 next, the entity at once |
| K-05 | **Store review** (PF01's R05). Apple accepts a dating app only if it offers "a meaningfully different or improved experience"; a photo is shown unchecked at today's defaults (C-05); no policy, support route or child-safety page is drafted; and age-signal laws take effect on 1 and 25 January 2027, with Texas's enforceable now | Medium to high for a first rejection | Weeks of rework at the very end | D-03 and D-08; P07.1's policies; the matrix refreshed and read row by row at P12 (PF01 §7) |
| K-06 | **The paid plan's rules and laws.** Whether an iPhone app may honour a plan sold only through a link, and whether an Android app may honour one bought on the web, are unsettled in the stores' own pages (A05-V2, A05-V3). Stripe accepts a dating service only after review. Five states bar a contract "measured by the life of the buyer". Only three states' renewal laws were read, for a launch in fifty | Medium | A refused store build, a refused Stripe account, or a void contract | D-04, D-09, D-11, D-12; Stripe's written approval before P08.3 builds on it |
| K-07 | **One operator** (OD-23). The law sets clocks of 48 hours for an intimate-image removal and 24 hours for urgent support; a CSAM report is a legal duty with a named contact; and no staff tool exists yet | High that the load is underestimated | Legal exposure and harm to members | P07.1's capacity plan, as PF01's R05 already requires; D-03's automation; the staff console before any real member |
| K-08 | **Stream** (PF01's R04). The Maker application has been pending 54 days. The production plan is a recurring cost (\$399 to \$499 a month on 28 September). Stream changed the development application's configuration without notice within four weeks, and the drift check Nathan required (OD-45) is not built. The harness cannot target a production application (C-18) | Medium | Cost, or a provider feature reaching members unreviewed | D-10; the drift check and a production-capable harness before P11B |
| K-09 | **Late integration defects** (PF01's R01). The slices are proven one at a time, in one process, with stand-ins for every provider. Composition, the worker, real mail, real storage and deployment have never run, and two sample adapters would fail open (C-04) | Medium to high | Defects found at P11, the most expensive place | SV5 (item 3), and each provider adapter built with its feature (P-04) |
| K-10 | **Native unknowns.** No build has ever run on a phone, an emulator or a simulator. The Expo 58 upgrade's native libraries are untested there, the photo picker answers "unsupported" on a phone, and the photo rules would refuse ordinary phone photos (C-06) | Medium | Rework in P09.2, late | A development build on a device as soon as the accounts allow (O5), before item 15 if Nathan authorizes it |
| K-11 | **CI's margins.** The Chromium install took 8 minutes 30 seconds on the newest run and has no retry; the two long jobs sit at 59% and 55% of their limits with a fifth suite to come; and if the repository goes private the free minutes run out within a month at October's rate (C-16, C-17; OD-51) | Medium | Runs that fail for reasons outside the change, each of which today becomes a Dev Manager consultation (OD-58) | The retry (H-08); the database job split by suite; an Actions line in M07 before the repository goes private |
| K-12 | **Records that mislead a decision** (PF01's R06). The matrix reads "0 met" and "not applicable" for rows that now bind; the State of the App is 21 merges old; Notion's plan rows date from 25 September | Medium | A wrong launch decision, or duplicated work | Section 6's corrections; the refreshes named there |
| K-13 | **Product defects carried in "done" code.** A like survives a block (C-01); a block's direction leaks (C-02); the chat reads follow a replaced rule (C-08) | Certain; all three are in the code today | None while nothing is served; real harm if served as built | SV4 Stage A, with a database case for each. The P11 plan already forbids serving the affected routes for C-02 |

### 8.1 The process, measured

Nathan asked for measured facts. These are for 26 October to 18 November 2026, from the full Git history, the review log and the mistakes log (READER; the counts I re-derived are marked GIT). Sessions and consultations are counted from the prompt and consultation files. Relays are estimated at one out and one back for each: (78 + 63) x 2 = 282. The two classifications of the mistakes log are the reader's judgment over all 200 entries, not the log's own.

**What it took**

- 24 calendar days, 15 with commits (GIT). 21 pull requests merged, 11 of them carrying code.
- **78 sessions started by hand:** 17 implementation or research, 28 correction, 33 review. **63 Dev Manager consultations.** About **280 hand relays** by Nathan, counting each out and back: about 19 for each day with commits.
- For each pull request that carried code: 6.5 sessions, 4.5 consultations, 47 commits and about 22 relays. The range runs from 10 relays (P06.3) to 46 (SV3 Stage B).
- 1,356 CI runs in the repository's life, 669 of them in this period.

**What it produced**

- 14,470 lines of server code and 9,640 of its tests; 917 lines of app code and 1,914 of its tests; 18,533 lines of proof harness and 6,444 of its tests; and **67,085 lines of Markdown** (GIT, gross lines added).
- 436 of 527 non-merge commits changed only Markdown (GIT). The handoff changed in 80% of the manager's commits.
- `docs/` now holds 92,656 lines and 12.1 MB. A new manager's required reading is 13 files and 1.02 MB, twice what it was on 25 October.

**Where the effort went**

- **Corrections, not first builds.** Of 78 sessions, 17 built or researched something and 61 reviewed or corrected it.
- **Many corrections changed no application code.** All seven of P06.2-F's changed one test file or a comment: 14 sessions, 6 consultations, 88 commits and 5,997 lines of Markdown for 105 lines of source. Seven of SV3's eleven changed only the proof's own tooling and records. Of the 47 sessions that committed, 20 added 60 source lines or fewer and 14 added none.
- **Commits and Markdown follow the number of relays, not the size of the change:** across the 11 code pull requests the correlation between commits and relay round trips is 0.99, and between sessions and source lines 0.43.
- **The second layer almost never says no.** Of 63 Dev Manager entries, 59 are "approved with conditions" and none is "not approved". It issued about 730 numbered conditions; about 650 were accepted as written and none declined. 18 of the 63 entries correct an error in one of its own earlier reports. It read for a median of about 10 minutes.
- **Waiting.** 10.9 of the 23.9 days were two gaps with no commit, of 5.6 and 5.2 days. Each began where the next step was a hand relay. Over the whole relay era the four such gaps are 31.8 of 55.3 days. No record gives a cause for any.
- **Turnover.** Twelve App Managers in 55 days, a mean of 4.8 days each, and five Dev Managers. Two managers were replaced after an action Nathan rejected; seven handovers record no reason.

**What the mistakes log shows**

- 200 entries, 108 of them since 26 October. AM11 logged 33 in five days and AM12 29 in two.
- **103 of the 200 are errors in the records themselves** (64 in the repository, 39 in Notion). **16 affected code or CI.** Thirteen are one mistake repeated: a time written before the clock was read.
- No Foundation job caught any of the 200.

**What the same records show the process is worth**

- **The exact-head review, Codex and the implementation sessions' own stop rules found the real defects:** the password-change guessing budget (SV1), the missing reauthentication (SV1), the lock cycle and the age bound (SV3), the chained undo and the block's direction (SV3), the inactive owner's purge (SV2), the loopback database boundary (P06.DB).
- **The Dev Manager's catches came before code:** an unguarded route, a session list that ended sessions at one layer only, a design that "cannot be built as written", and the repository being public.
- **The start gate and the fail-closed classifier each stopped a wrong run.**
- **No recorded catch of a code or CI defect** by the Notion read-backs, the clock rule, the handoff's size rule, the TypeSafe reading or the branch-list rule. Their entries record mistakes in applying those rules themselves.

**My reading.** The two things that find defects are the independent review of an exact head and the proof on a real database. Both should stay. What has grown out of proportion sits around them: correction rounds on tooling and wording, a second-layer read of each of those rounds, and records of records. At November's rate the remaining work is about 200 to 350 sessions and 160 to 280 consultations, each carried by one person. The process has also improved since M05 where it was changed: Markdown per line of application code fell from 3.7 to 1.6, and sessions per code pull request from 7.9 to 6.5.

**The proposed change** is D-06 and D-07, and two smaller ones that are the manager's and the Dev Manager's to make, since they change the workflow and PF02:

1. **Stop recording that a condition was applied.** 41 of the 85 closed "Deferred conditions" rows say only that the Dev Manager confirmed its own words were applied.
2. **Move the status log out of Implementation Control.** It is 327,089 characters, 72% of the page, and every Notion sync ends with a read of the whole page.

I did not write any of this into the canon. It reverses standing directions, so it is Nathan's to decide.

## 9. The checks I ran, and what I did not read or run

### 9.1 Offline suites, in a scratch copy of `4e01cd7`

| Suite | Command | Result |
|---|---|---|
| Policy scripts | `python -I -m unittest discover -s scripts -p 'test_change_scope.py' -v` | Ran 14 tests, OK |
| Policy scripts | `python -I -m unittest discover -s scripts -p 'test_branch_cleanup.py' -v` | Ran 18 tests, OK |
| API | `pip install --require-hashes -r requirements-dev.lock`; `pip check` | Installed; "No broken requirements found." |
| API | `GLOW_ENV=test python manage.py check` | "System check identified no issues (0 silenced)." |
| API | `GLOW_ENV=test python manage.py test tests --verbosity 2` | Ran 645 tests in 47.6 s, OK (skipped=1) |
| API | `ruff check .`; `ruff format --check .`; `mypy` | "All checks passed!"; "165 files already formatted"; "no issues found in 95 source files" |
| Contracts, Python | `PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests -v` | Ran 53 tests, OK |
| Contracts, JavaScript | `npm ci --ignore-scripts`; `npm run check` | "Generated types and runtime validators match schemas."; tests 902, pass 902, fail 0 |
| Mobile | `npm ci --ignore-scripts`; `npm run typecheck`; `npm run lint`; `npm test` | Clean; clean; tests 691, pass 691, fail 0, skipped 0 |
| Mobile | `EXPO_OFFLINE=1 npm run check:expo` | "Dependencies are up to date" (it also prints "Dependency validation is unreliable in offline-mode") |
| Database proof, offline | `python -m unittest discover -s tests -t . -v`; Ruff; mypy | Ran 377 tests, OK; clean (71 files) |
| Stream proof, offline | `python -m unittest discover -s tests -t .`; Ruff; mypy; `node --check client/*.cjs`; `python checks/run_plan.py` | Ran 648 tests, OK; clean (59 and 57 files); four files pass; "run plan: fits" |

- **The one skip** is `test_every_writer_at_mains_base_is_unchanged_and_one_is_new`, which needs `main`'s history; my scratch copy is not a Git checkout. CI's run on `main` ran it: 645 tests, none skipped.
- **One error of my own.** My first run of the contracts' JavaScript check failed (`Cannot find module 'ajv/dist/runtime/ucs2length'`), because I ran it before installing the mobile app's packages. The contracts README gives that order. Run in CI's order it passed. It is not a defect.
- **The Stream proof's commands reached no network.** The two installs reached PyPI and the npm registry only. Every test ran with no proxy variable, so no outbound connection was possible, and no `STREAM_*` name exists in this environment.

### 9.2 CI and GitHub, read through the GitHub tools

- **Run 44416436012** (push, `main`, `6edae78`, attempt 1): I read the run, its eight jobs with their steps, and the gate's log, which prints `Application checks passed` at 23:14:28 UTC. A reader parsed the four long logs: 645, 53, 14 and 18 tests in API checks; 902 and 691 tests and "104 passed" in Mobile checks; 648 in Stream proof checks; and in Database proof checks 377 offline tests, reference 56 of 56, adapter 115 of 115, delivery 13 of 13, reads 62 of 62, identity 49 of 49, profile 77 of 77, discovery 66 of 66, each verdict PASS. These equal my local counts.
- **Run 44421080745** (push, this session's branch, `4e01cd7`): success after 718 seconds. Read at run level only.
- **History** (READER): 54 pull requests, 52 merged, 2 closed unmerged (17 and 26), none open; 1,356 Foundation runs; 174 run IDs cited in pull-request descriptions, all of which exist; every merge's parents equal its pull request's base and head.

### 9.3 Code read by me

The Foundation workflow whole; `glow_api`'s URL file, views, settings and configuration loader; every URL file in the API; `glow_chat`'s block and reciprocal-activation writers; `glow_discovery`'s block wrapper and eligibility snapshot; `glow_profiles/requirements.py`; the `Entitlement` model; the `Dockerfile`; the mobile layout guard, profile policy, birth screen and draft, development script and the one network helper; the flow registry and both API descriptions; the contract test that reads Markdown.

### 9.4 Documents read whole by me

Root `AGENTS.md` and `CLAUDE.md`; `docs/README.md`; PF00 and PF01; the current handoff; the owner-direction register; the State of the App; the carried-items file; the P11 plan; the manager workflow; M09's brief; the reports of the eleven readers that reported. Read in part: the M05 record (sections 1 to 3 and 5 to 7); PF02 (structure and rule 1); the Dev Manager charter (the consultation and relay sections). In `glow-docs`: the brand folder's README, decision log, interface standard and app handoff note, and the design system's two README files; of HDE's canon, PF05 v2.5.7's sections 1, 5.1.0, 5.1.7 and 5.9 and the head of 5.7.

### 9.5 What I did not read or run, and why

- **No database suite locally.** No Docker daemon runs in this environment. Under P06.DB's D4 the evidence of record is CI's run on the final head, which I read; a local pass "counts for nothing in the record". No doubt arose that only a local run would settle.
- **No rendered run, no export, no container build.** `playwright install` is forbidden here and no Docker daemon runs; CI's run on the head covers all three.
- **No provider, database, HDE or Railway call, and no email.**
- **The code I did not read line by line** is covered by the readers, and their reports list what each left unread. The largest gaps: the bodies of the roughly 190 database cases, most of the Stream harness, and the test bodies of most API test files. Statements that rest on those are marked READER or RECORD.
- **No price, policy or law was rechecked online.** Every figure is its record's, at the record's date.
- **HDE's canon** (34 documents, about 10 MB) was not read, except the parts of PF05 named in 9.4. The reader assigned to it was stopped by a usage limit and left no report. Item O3 (A01-R, section 4.3) is the full read.

## 10. Updates made under Nathan's authorization

Nathan's words are in section 1.1. I read them as covering the implementation plan itself: its sequence, coverage, dependencies and acceptance, in GAPP-PF01 and in Notion's plan surfaces. I changed nothing else. Anything that would reverse one of his directions or a process rule is a decision in section 5, not an edit.

Every change was made on 19 November 2026, after the record's first commit (`f086f0d`).

### 10.1 GAPP-PF01, revision 1.19

- **Commit:** `b738529ebe74ff55180154616b51b6435008ca5c`, on this branch, holding that one file and nothing else: 64 lines added, 14 removed. Its base is revision 1.18.
- **It is not in force.** PF01 is governing Markdown, so the Dev Manager reads it at that commit before the branch merges, and the manager integrates it (`AGENTS.md`, "Code Review Rules"). I merged nothing and opened no pull request.
- **GAPP-PF00 is unchanged.** Its registry names no revision of PF01, and nothing in it became false.

| Place in PF01 | Revision 1.18 | Revision 1.19 | Finding |
|---|---|---|---|
| Header | Revision 1.18, 17 November 2026 | Revision 1.19, 19 November 2026 | — |
| §2, "Application repository" | "Private `amthorn78/glow-dating-app`" | "public for now, to be made private again (OD-51)" | R-02 |
| §2, a new row | — | `amthorn78/glow-docs`, attached to every session, as the read-only home of HDE's canon and the brand's design system. No app session writes there; reading it authorizes no call to HDE; its prompt libraries are not this application's workflow | Section 1.1, direction 3 |
| §5, a new paragraph | — | "HDE's canon as a source": what the partial read of 18 November found, and that A01-R reads the whole. The canon is evidence, not the delivered contract | P-09 |
| §8, "Server slices" | Four slices; "SV4, chat's HTTP surface" | SV4 in two stages, with P06.2-T folded into Stage A; SV5, the composed server and the worker; SV2-L, OD-64's limits; P07's and P08's server parts built as sealed slices | R-06, P-02, P-03, P-06, P-07, H-02, H-07 |
| §8, five new paragraphs | — | "The app's real client" (AC1 to AC3, and no new screen that runs only on a sample back-end); "Provider adapters" (each built with its feature, once its account line is approved); "Design system"; "The owner's track"; "Order of the remaining work" | P-01, P-04, P-05, section 4.3 |
| P07 and P08 | — | A "Sequence and scope" line each | P-02, P-08, P-10 |
| P09, Documentation | — | It produces the threat model, the SBOM and the chat failure runbook that P02, §4 and P06 owed | H-04 |
| **P09, Completion** | "independent checks pass or have justified scoped deferrals" | Each check named in P09's briefs passes, or is deferred by a recorded entry naming the check, the reason, its owner and the item that reruns it; signed native builds exist for both platforms, or the missing access is a named launch dependency | H-09 |
| **P10, Validation and Completion** | "the complete fixture user journey"; "no unexplained blockers" | The journey and the safety and deletion cases run on the composed server, through HTTP, with the app's real client, on a disposable PostgreSQL in CI; every open blocker is a named entry with its owner and its gate | H-09, K-09 |
| §10, A01 | No mention of the canon | The canon is attached; A01-R reads it; what HDE must still deliver, by the partial read | P-09, R-27 |
| §10, A04 | The list's contents as of OD-50 | Also the legal entity and its D-U-N-S number, Stripe, the stores' billing, a domain and WordPress hosting, monitoring, the photo and CSAM checks if chosen, Actions minutes once private, and legal advice. M07 is written first among the remaining items | Section 4.7, K-04 |
| §10, A05 | Seven questions as open | Two messages answered (OD-55, OD-60); the third, on retention and the operators, before P07's brief | R-03 |
| §10, A06 | "no plan, price or trial length is set except by Nathan" | The trial is two weeks, the Stripe link is in the iPhone app and on the web only, and a founding-member offer follows the launch; the plan's name, price and billing period are his to set | R-04 |
| §10, the autonomy table's Railway row | "do not invent a separate provisioning-approval gate" | Adds: since OD-50 each Railway app service is a line of the costed list, created only after Nathan approves it | R-05 |
| §11, R01 and R02 | — | Each names its new mitigation | K-01, K-09 |
| Revision history | Ends at 1.18 | The 1.19 entry, quoting Nathan's two directions and naming the acceptance changes | — |

**The two rows in bold change phase acceptance.** The revision history says so, as revision 1.13's entry did.

**Left unchanged on purpose:** §7's "Media" paragraph, which waits for decision D-03; §7's "Billing" paragraph and §4's Billing row, which the billing item's brief revises (DM-85); every owner direction; PF02; the manager workflow; the Dev Manager charter; the CI policy.

### 10.2 Notion

Written between 00:17:43 and 00:20:33 UTC on 19 November 2026, and read back by 00:21 UTC. Before each change I read the live value: all 30 open rows of the Work Register in one faithful read, and the whole of Implementation Control.

**How each change is marked.** PF01 1.19 is not in force until it merges, so no Notion text states it as a rule. Each changed field says "M09" and "PF01 1.19 … pending its merge", and each new or rewritten Next Action opens with the date, Nathan's direction of 18 November and commit `b738529`. Links point to that commit, never to this branch by name.

**Six new rows in the Work Register** (87 rows before, 93 after). Each is Kind Task, Phase Cross-cutting, State Planned, Action Class Autonomous. Its Plan Reference is PF01 at `b738529`, and its Next Action gives the deliverable and acceptance from section 4.3.

| Work ID | Name | Depends On |
|---|---|---|
| A01-R | A01-R — Research: HDE's canon read against the contract request | The glow-docs repository attached to the session (Nathan, 18 November 2026). Second in the proposed order, after M07 (PF01 1.19, section 8, pending its merge). It gates A01's date and the HDE adapter. |
| SV5 | SV5 — Server slice: the composed server and the worker | SV4 (Stage A and Stage B). Before SV2-L and AC1. |
| SV2-L | SV2-L — The change limits of OD-64 | SV5. Before AC2. A precondition of P11 (the carried-items file, "Carried from OD-64"). |
| AC1 | AC1 — The app's real client: the foundation | SV5. Nathan's final approval of the brand's navigation and icons (the owner's track; the brand's decision BD-12 is tentative). |
| AC2 | AC2 — The app's real client: onboarding to a visible profile | AC1 and SV2-L. For a real photo upload: Cloudflare R2 and the photo processor (A04); until then the server's sealed stand-in. |
| AC3 | AC3 — The app's real client: discovery to conversation | AC2. For a real connection view: HDE's work for the app (A01). Before P07.1. |

**Twenty-four existing rows changed.** Only the properties listed changed. No State, Kind, Phase, Action Class, Owner Role, Evidence or Plan Reference was touched.

| Work ID | Property | Before | After |
|---|---|---|---|
| M07 | Depends On | Before P09 and P11B (PF01 A04; OD-50) | None. First in M09's proposed order, before SV4, because the legal entity, the store accounts and Stripe's review have lead times that others set (PF01 1.19, section 8 and A04, pending its merge). At the latest before P09 and P11B (PF01 A04; OD-50). |
| SV4 | Name | SV4 — Server slice: chat's HTTP surface | SV4 — Server slice: chat and notifications (Stage A: chat's HTTP surface; Stage B: the server side of notifications) |
| SV4 | Depends On | SV3 and P06.2-T; before P07 and P10 | SV3 (Done). M09's plan (PF01 1.19, section 8, pending its merge): M07 and A01-R come first in the order; P06.2-T is folded into Stage A; SV5 follows Stage B. Before P07 and P10. Its brief was tabled by OD-72 until M09 reported. |
| SV4 | Next Action | 821 characters, opening "Nathan, 26 October 2026 (OD-49, N1 (a)): chat's production HTTP surface" | A new opening paragraph of 842 characters on the two stages, with findings C-01 and C-02 and P06.2-T folded in, ending "The earlier text follows."; then the earlier 821 characters, unchanged (checked in full) |
| P06.2-T | Depends On | Before the chat HTTP slice; its epoch-bump question goes to the Dev Manager first (DM-31 item 4) | M09's plan (PF01 1.19, section 8, pending its merge): folded into SV4 Stage A, with the pyjwt pin kept because SV1 needs the package. Until that merges: before the chat HTTP slice. Its epoch-bump question goes to the Dev Manager first (DM-31 item 4). |
| P07.1 | Depends On | P02.1,A05 | P02.1 (Done); A05's third message (retention, the operators and their response times); Nathan's decisions on what checks a photo and on CSAM detection (the M09 record, section 5, D-03 and D-08). After AC3 in M09's proposed order (PF01 1.19, section 8, pending its merge). |
| P07.2 | Depends On | P04.3,P05.3,P06.2,P07.1 | P07.1; P07.2a, whose proof case runs first; AC3 (the app's real client) and SV5 (PF01 1.19, section 8, pending its merge). Earlier: P04.3, P05.3, P06.2 (Done). |
| P07.2a | Depends On | Before P07's block writer, or WordPress's | Runs first inside P07.2 (the M09 record, section 4.3, item 9): before P07's block writer, or WordPress's. |
| P07.3 | Depends On | P07.2,P03.3 | P07.2 and P07.2a; P03.3 (Done). For the real site: a domain and WordPress hosting (A04; a line of M07's costed list). |
| P07.3 | Next Action | Staff-scoped admin API/plugin, audit and support workflow; no direct dating/HDE DB access. | The same sentence, then: "19 November 2026 (M09; PF01 1.19 on the M09 branch at commit b738529, pending its merge): it also builds staff sign-in separate from members'; every OD-60 setting, the staff grant and the photo check's toggle in the console; and the public pages (policies, support, deletion and child-safety routes). Accepted against a disposable WordPress in CI. The M09 record, section 4.3, item 10." |
| P08.1 | Depends On | P02.2,P07.1,A05 | P02.2 (Done); P07.1; A05's third message (retention). After P07.3 in M09's proposed order (PF01 1.19, section 8, pending its merge). |
| P08.2 | Depends On | P08.1,P06.2,P07.2 | P08.1; P07.2; SV5 (the worker). For the engine's part: HDE's deletion answer (A01; A01-R). Earlier: P06.2 (Done). |
| P08.3 | Name | P08.3 — Resolve paid-launch scope and implement entitlements if selected | P08.3 — Implement the paid plan and entitlements (OD-69 to OD-71) |
| P08.3 | Depends On | P02.1,A06; OD-69, OD-70, OD-71 | AC3; P07.3 (the staff grant in the console); A06 (the plan's name, price and period, what a member without a plan can do, and the billing library: the M09 record, section 5, D-04, D-05 and D-11); A04 (the store accounts and Stripe's approval). OD-69, OD-70, OD-71. Earlier: P02.1 (Done). |
| P09.1 | Depends On | P04.3,P05.3,P06.2,P07.3,P08.2 | P07.3, P08.2 and P08.3. Under PF01 1.19 (pending its merge) it also produces the threat model that P02 owed. Earlier: P04.3, P05.3, P06.2 (Done). |
| P09.2 | Depends On | P04.3,P05.2,P06.3,A04 | AC3 (the app's real client, on a device); A04 (the Apple and Google accounts, Expo's build service and signing, each a line of M07's costed list, and Nathan's release authorization). Earlier: P04.3, P05.2, P06.3 (Done). |
| P09.3 | Depends On | P03.3,P07.1,P08.1 | P07.1, P08.1 and P09.2; A04 (a monitoring account; a line of M07's costed list); Nathan's final approval of the brand's icon and store listing. Under PF01 1.19 (pending its merge) it also produces the SBOM and the chat failure runbook that earlier phases owed. Earlier: P03.3 (Done). |
| P10.1 | Depends On | P09.1,P09.2,P09.3,P08.3 | P09.1, P09.2, P09.3 and P08.3; SV5 and AC3, since under PF01 1.19 (pending its merge) the journey runs on the composed server with the app's real client. |
| P10.1 | Next Action | Complete fixture journey and safety/privacy cases; clear passed/failed/deferred matrix. | The same sentence, then: "19 November 2026 (M09; PF01 1.19 on the M09 branch at commit b738529, pending its merge): under that revision the journey and the cases run on the composed server (SV5), through HTTP, with the app's real client, on a disposable PostgreSQL in CI, and every deferred claim has a test and an owner." |
| P11.1 | Name | P11.1 — Prove persistence and migrations on disposable PostgreSQL | P11.1 (P11A) — Prove persistence and migrations on disposable PostgreSQL |
| P11.2 | Name | P11.2 — Integrate staging persistence and live provider sandboxes | P11.2 (P11B) — Integrate staging persistence and live provider sandboxes |
| P11.2 | Depends On | P11.1,A04 | P11.1; A04 (every provider account approved from M07's costed list). Under PF01 1.19 (pending its merge) each adapter is built with its feature before this item, which proves them together. |
| P11.3 | Name | P11.3 — Validate supported HDE adapter against real engine | P11.3 (P11B) — Validate supported HDE adapter against real engine |
| P11.3 | Depends On | P11.1,A01,A07 | P11.1; A01 and A07 (HDE's work for the app, which A01-R scopes). |
| P11.4 | Name | P11.4 — Prove recovery and production connection readiness | P11.4 (P11B and P11C) — Prove recovery and production connection readiness |
| P11.5 | Name | P11.5 — Connect final production app targets and perform private smoke | P11.5 (P11C) — Connect final production app targets and perform private smoke |
| A01 | Depends On | (empty) | A01-R first (the read of HDE's canon against the contract request); then Nathan's date in HDE's own process. On the owner's track (PF01 1.19, section 8, pending its merge). |
| A01 | Next Action | 1,020 characters, with "last revised at commit c775f39 (29 September 2026)", "It asks 29 questions (C01 to C29)" and, at the end, "The M05 review (finding 45) proposes six more questions, C30 to C35; they go to the Dev Manager first (DM-31)." | A new opening paragraph on HDE's canon and A01-R; then the earlier text with three corrections: "last revised at commit 89e8f36 (26 October 2026)"; "It asks 35 questions (C01 to C35)"; and, in place of the last sentence, "C30 to C35 were added on 26 October 2026 (M05 finding 45; DM-31), and Nathan was told the same day (OD-50)" |
| A07 | Next Action | "… the HDE contract request (last revised at commit c775f39) asks for …" | The same text with "89e8f36", then: "19 November 2026 (M09): HDE's canon, now attached in the glow-docs repository, specifies bands only, with no number: the Harmony band in version 1 of the pair read and a band for each of ten categories in version 2. A01-R (its own row) reads it in full." |
| A04 | Depends On | (empty) | M07's costed list first; Nathan approves each line before an account is opened or anything is spent (OD-50). The owner's track, in order (PF01 1.19, section 8, pending its merge): the US legal entity and its D-U-N-S number (OD-55); then the Apple and Google organization accounts and Expo's build service, which gate P09.2, and Stripe's account and its review, which gate P08.3; then Cloudflare R2, mail, push, Railway app services, a domain and WordPress hosting, monitoring and Stream's production plan, each of which gates its adapter, and all of which gate P11.2. |
| A05 | Depends On | (empty) | The third message (retention; the moderation and support operators and their response times) before P07.1's brief (PF01 A05). M09's list of Nathan's open decisions is in the M09 record, section 5; D-03 and D-08 bear on P07.1. |
| A06 | Depends On | (empty) | Still open for P08.3's brief: the plan's name, price and billing period (the M09 record, section 5, D-04); what a member without a plan can do (D-05); the billing library (D-11); legal advice on the terms and on the founding-member offer (D-09 and D-12; OD-71). |

Two notes on that table:

- **P11.4's name.** M05 mapped P11.4 and P11.5 to P11C. PF01's own text places the restore drill, which is P11.4's first task, in P11B. So I wrote "P11B and P11C".
- **The owner's track has no rows of its own.** It is carried in the Depends On of A01, A04, A05 and A06 and in M07, so that the register gains no ID the repository does not name.

**Implementation Control: one sentence added.** In the "Next items" bullet, after "then SV4, named to Nathan before it starts.", I inserted 1,171 characters that open "19 November 2026 (written by M09's review session, under Nathan's direction of 18 November 2026 to update the implementation plan):". They give the proposed order, say it is in force only when PF01 1.19 merges, and link this record at `b738529`. I compared the page before and after by script: nothing was removed, and every other character of its 451,822 is unchanged.

**What this covers of Appendix B:** differences 1, 2, 5 and 6 in full. Difference 3 in substance: the Depends On fields now follow the proposed order, so P07.1 and P10.1 name AC3 and SV5, which come after SV4, where the difference asked for SV4 itself. Differences 7, 9 and 16 in part: A04's Depends On now names the costed list, P08.3's Name is corrected, and M07's place in the order is stated. I left the long Next Action cells of A04, A05, A06, M07 and P08.3 as they were, because a property is replaced whole and retyping 1,300 to 3,300 characters risks a silent change. Differences 4, 8, 10 to 15 and 17 to 33 are untouched and are the manager's.

**Not changed in Notion:** every Done or Recorded row; G-01, A02, P10.2, P12.1 and P12.2; M09's own row; the "Phase" bullet and the status log of Implementation Control; the register copy of the owner directions; the Dev Manager page.

### 10.3 What the manager needs to do with these

1. **Take PF01 1.19 to the Dev Manager at `b738529`** before this branch merges. If the Dev Manager changes it, Notion follows the merged text.
2. **When it merges:** remove "pending its merge" from the Notion fields in 10.2, and point the six new rows' Plan Reference at `main`. **If it is declined, in whole or in part:** restore the "Before" values in 10.2, delete or defer the six new rows, and remove the sentence from Implementation Control.
3. **Record Nathan's directions of 18 November** as OD-73 and OD-74 (R-01). I did not write the register.
4. **M09's own row** is the manager's. Proposed: Evidence, the link to this record at this branch's final commit; State, by the manager's verification.

### 10.4 Checks on this branch's own commits

- **Trusted classifier:** `scripts/change_scope.py` as it stands on `main` at `6edae78`, extracted outside the checkout and run with `python3 -I`, `--base 6edae780a0fbf1e5d2659c3eb8c9c48eeeea1a70 --head b738529ebe74ff55180154616b51b6435008ca5c --merge-base`. Result: `"full": false, "reason": "ordinary-docs-only"`, over 18 Markdown paths. Sixteen of them are the manager's own records commits, which the start gate put on this branch. My commits change two files: this record and PF01.
- **Foundation runs** (CI, read through the GitHub tools): 44426834603 on `f086f0d` and 44427277773 on `b738529`, each a success. On the second I read the jobs: Change scope passed, the six application jobs were skipped, and the gate passed.
- **Branches:** `main` stayed at `6edae78` and the manager branch at `964d38a` throughout. One merge base with `main`.
- **`amthorn78/glow-docs`:** read only, at `707da56`; its working tree is clean and nothing was written to it.
- The run on this record's final commit cannot be named inside that commit. It is in the session's final message.

### 10.5 Corrections to this record after its first commit

- **Section 4.3, item 15, "External gates".** The first commit read "O5; a Mac or a hosted build service (OD-57)". OD-57 is about a CLI environment for tools a cloud container lacks, and it does not cover native builds. The cell now cites `apps/mobile/AGENTS.md`, which bars `eas` and release work without Nathan's authorization. I then checked every other owner-direction citation in this record against the register's own row, and compared each Dev Manager citation with the review log's subject line for that consultation, which is a weaker check. I found no other error.
- **Section 6.1, R-03, "Proposed correction".** The first commit said PF01 1.19 would name "the launch values OD-60 left open" as still owed. The revision as written names what the carried-items file names for the third message: retention, and the moderation and support operators. The cell now says that.
- **Section 6.1, R-08, "Proposed correction".** The proposed README sentence carried a relative link that does not resolve from this record's folder. It is now given as words, with the link's target named.

## Appendix A. The one-line corrections of finding R-22

The contract test named in C-15 reads one sentence of `docs/architecture/production-contracts.md`. A correction to that file must leave that sentence as it is, or run the full checks.

| Where | It says | Proposed text |
|---|---|---|
| `proofs/postgres-ordering/README.md:27` | "the reviewed `glow_persistence` migrations `0001` and `0002` apply" | "the reviewed `glow_persistence` migrations `0001` to `0012` apply" |
| `proofs/postgres-ordering/README.md:34` | It does not prove "maintained authentication … or allauth" | Remove "or allauth"; the identity suite exercises allauth, as line 214 of the same file says |
| `proofs/postgres-ordering/README.md:169` | "it generates two passwords and two markers" | "it generates two passwords, five markers, three `SECRET_KEY` values and three RSA keys" |
| `proofs/stream-chat/README.md:358`, `:420`, `:426` | The products comparison "has not been used live" | "It first ran live on 23 October 2026 (`docs/architecture/chat-provider-permissions.md`, line 96)." |
| `docs/architecture/production-contracts.md:3` | "**Not implemented:** production routes, …, durable state transitions, … or database integration." | "**Not implemented in the served runtime:** …" with "The sealed slices hold durable transitions (this document's route lists); nothing serves them." |
| `docs/architecture/production-contracts.md:63` | The flow index "is generated from the committed flow registry" | "is kept by hand against the committed flow registry; no generator exists." Rows F02 and F05 differ from the registry's `acceptance` text and are brought back to it |
| `docs/architecture/chat-provider-permissions.md:66` | "For a production application the same plan runs with that application's credentials" | "For a production application the same plan must run with that application's credentials. The harness cannot do that yet: it refuses any application but the development one." |
| `proofs/postgres-ordering/glow_ordering_proof/settings.py:26` (a code comment, so a full-scope change) | "nothing else of the API is" imported | With the next change to the file: name `glow_chat.contact`, which `__main__.py:184` imports under these settings |

## Appendix B. Notion against the repository: the 33 differences of finding R-26

Read on 18 November 2026, 23:19 to 23:36 UTC, before any change of mine. In every case the repository is right. Section 10 says which of these I corrected; the others are the manager's.

### The Work Register

| # | Row or rows | Difference | Correction |
|---|---|---|---|
| 1 | SV4 | The row does not say its brief is tabled (OD-72); last edited 1 November | Add OD-72's line |
| 2 | P11.1 to P11.5 | The repository names the stages P11A, P11B and P11C only | Put the stage in each Name: P11.1 (P11A); P11.2 and P11.3 (P11B); P11.4 and P11.5 (P11C) |
| 3 | P07.1, P10.1, P09.1 to P09.3, P11.2, P11.3, P07.2, P07.3 | "Depends On" names none of the items added since 25 September | Add SV4 to P07.1 and P10.1; M07 to P09.1 to P09.3, P11.2 and P11.3; P07.2a to P07.2 and P07.3 |
| 4 | P10.1, P10.2, P09.1, P07.3, the P11 rows | No pointer to the row's "Carried to" section of the carried-items file | Add each pointer |
| 5 | A01 | "It asks 29 questions (C01 to C29)", at commit `c775f39` | "35 questions (C01 to C35); C30 to C35 were added on 26 October 2026", at `89e8f36` |
| 6 | A07 | Names the same old commit | As 5 |
| 7 | A04 | Lacks OD-50's costed list | PF01 A04's sentence, naming M07 |
| 8 | A06 | Opens "Default no active paid feature; obtain monetization choice …" | Open with "Answered by OD-69", then what is still open |
| 9 | P08.3 | Name and Next Action keep "if selected" and the deferral branch | Remove both |
| 10 | D10 | "PF01 revision 1.8 … PF00 1.7"; "The current Dev Manager is Dev Manager 3" | Drop the numbers and the name, or update them |
| 11 | AP1-DBA-001 | Points P11 at the same-database design OD-18 replaced; its evidence page has no such note, and spells the ID AB1 | Add "Superseded in part (OD-18; ADR 0004)" to the row and the page |
| 12 | P06.2 | Names follow-ups the handoff no longer holds, and "Nathan can delete eight … branches", which is done | Point to the homes; delete the sentence |
| 13 | P00.3, P01.1 to P01.3, P03.3, P05.1 to P05.3, P06.1, P06.DB, P06.2-F, P06.3, SV1, SV2 | Done rows that still name a next step, each since done | Strike the pointer |
| 14 | SV4, P06.2-T, P07.2a, G-01, P11.5 | Owner Role names a past role ("App Manager 8", "App Builder 1") | "the manager" |
| 15 | D05, D08, D09, R05 | The text of 23 to 25 September | PF01's rows, or "see PF01" |
| 16 | M07 | A 1 November summary: no R2, entity and D-U-N-S number, Stripe's fees or legal advice; Action Class "Spending approval" for a research item | Bring to "Carried to M07"; the approvals belong to each line |
| 17 | G-01 | Planned, though three of its parts are in done items; links pinned at `05f4c3a` | In progress; re-pin |
| 18 | M09, SV2-R, A05-V2, A05-V3, P06.2-F | Evidence holds a sentence, not a bare link | The link alone |
| 19 | P06.2-T, P07.2a | File names turned into web links (`pins.py`, `contact.py:490`, `reads.py:289`, `delivery.py:265`) | Plain text |

### Implementation Control

| # | Where | Difference | Correction |
|---|---|---|---|
| 20 | The "Phase" bullet | Ends "Now: M08", and lists nothing after SV3 | Add M08, A05-V to A05-V3 and SV2-R as done; the current item |
| 21 | Under "P06.DB is done" | "**Next:** P06.2" | Delete; P06.2 merged on 25 October |
| 22 | Under "P06.1 is done" | "App Manager 7 runs" | "Managers run in `Glow App - No Stream`" |
| 23 | "Standing after P06.1" | A bullet about the next Dev Manager's start prompt and P06.2's inheritance; both long done | Delete, or keep only what is open, with its home |
| 24 | The scorer question | "comes after the ten-session comparison" | OD-10's State sentence |
| 25 | The Manager bullet | Stops at PR51 | Add PR52 to PR54 |
| 26 | "Where the rules live" | PF02 "revision 1.3 merged … 1.4 on the manager branch" | 1.4 and 1.5 in PR52, 1.6 in PR53, 1.7 in PR54 |
| 27 | "Standing directions" | The copy "holds OD-01 to OD-66" | "OD-01 to OD-72" |
| 28 | The guidance summary's stamp | Links pinned at `50a3e25`, 26 commits behind | The commit the status names |
| 29 | "Next items" | Its done sentence omits SV2-R | Add it |
| 30 | "Next items" | Names no place for P06.2-T | Its place in the order |
| 31 | "Superseded: the full copy of the procedure" | 18,116 characters still on the page; due to move since 26 October | Move to a child page |
| 32 | "Current status" | One paragraph of 327,089 characters, 72% of the page, about 350 entries back to 5 October | Keep the current entry; move the rest to a history child page |

### The Dev Manager page

| # | Where | Difference | Correction |
|---|---|---|---|
| 33 | "How it works"; the consultation table | Managers listed only to App Manager 10; DM-64's row sits last, after DM-93 | Add App Managers 11 and 12; move the row |

**Checked and clean:** no row's State contradicts the handoff; every item the repository names has one row, except the P11 stage names; all 122 links into the repository resolve; the register copy of the owner directions holds OD-01 to OD-72 with no cell different in substance.

## Manager verification of M09

App Manager 12, 19 November 2026. The record was read whole. Nathan answered the decisions on 19 November (OD-75).

### Checks

- **Classification.** `scripts/change_scope.py` from `main` at `6edae78`, extracted outside the checkout and run with `python3 -I` and `--base 4e01cd7 --head 20a0d99 --merge-base`: `"full": false, "reason": "ordinary-docs-only"`, over two paths, this record and GAPP-PF01. One merge base with `main` (`6edae78`).
- **Acceptance check 1 is not met as written,** and the deviation is accepted. The brief expected only this record; the second path, PF01 1.19, was written under Nathan's in-session authorization (OD-73), as its own commit (`b738529`).
- **CI**, read through the GitHub tools: Foundation runs 44426834603 (`f086f0d`), 44427277773 (`b738529`) and 44428764678 (`20a0d99`, the final head), each a success.
- **Integration.** Merged into the manager branch at `c48b950`. **PF01 1.19 is not in force:** the Dev Manager reads it at `b738529` (DM-94), and no pull request carrying it merges into `main` before that read.
- **Claims I checked in the code (CODE), all true:**
  - the served runtime installs only `rest_framework`, has a dummy database and serves two health routes and a development-only route;
  - `EngineIdentity` is only read (C-03);
  - `block()` touches only `Match` (C-01);
  - `MEDIA_TYPES = ("image/png",)` and `MEDIA_BYTES = 1_048_576` (C-06, `profile_settings.py:160-161`);
  - the mobile stores' `sequence` counters start in memory (C-14);
  - the contract test reads `production-contracts.md` (C-15, `test_transition_contract.py:699-707`);
  - `README.md:3`, the CI policy's line 85, the State of the App's "As of", and P06.1's 68 against its record's 65 (R-02, R-08, R-21, R-07, R-25).
- **Not rechecked:** the process measures and the sizes (sections 4.6 and 8.1), the session's own counts. Notion: the six new Work Register rows exist, Planned (A01-R, SV5, SV2-L, AC1, AC2, AC3); the 24 changed fields were not reread one by one.

### Dispositions

Key: **Done** = applied in the manager's batch with this section. **1.19** = in PF01 1.19, pending DM-94. **DM-94** = governing text, to the Dev Manager first. **Routed** = in the [carried-items file](../../planning/carried-to-later-items.md), "Routed by M09", unless another home is named. **M09-R** = a Markdown-only item that applies the record's exact corrections to files that are not the manager's; it is commissioned after DM-94 (D-06). **Manager** = the manager's own records, in a later batch.

| Findings | Disposition |
|---|---|
| R-01 | Done: OD-73 and OD-74, with OD-75 for Nathan's answers |
| R-02 | 1.19 for PF01 §2; M09-R for `README.md` |
| R-03 to R-06 | 1.19 |
| R-07 | Manager: the State of the App refreshed from this record after DM-94 |
| R-08, R-11, R-12 (header and summary), R-13, R-14, R-18, R-22, R-24 (except the `AWS_*` names) | M09-R. R-12's state column goes to P07.1 (P-10) |
| R-09 | Done: the SV2-R brief's status line and its "Why" sentence |
| R-10 | Manager: notes under SV2's acceptance checks 9 and 10 and D9, D10 and D18 |
| R-15 | Manager: the review log's stale rows |
| R-16 | Done: revision 8; SV1's docstring entry moved to SV4; N-a, N-c and N-d closed; P06.2-F's entries removed |
| R-17 | Done: the handoff's wording |
| R-19 | M09-R for the two Markdown files; AC1 for `.env.example` (full scope) |
| R-20 | M09-R for the count; the two slots to SV5 |
| R-21, C-15 | DM-94 (the CI policy is governing) |
| R-23 | M09-R for the two Markdown files; SV4 Stage A for the docstring in `models.py` |
| R-24's `AWS_*` names | D-18, asked of Nathan |
| R-25 | Done, with the brief's breakdown matched to its record |
| R-26 | Manager: differences 4, 8, 10 to 15 and 17 to 33, once PF01 1.19's read is known, since Notion follows the merged text |
| R-27 | Routed to A01-R |
| R-28 | Manager: one pruning batch, OD-45's link pinned first |
| R-29 | DM-94 for §7's Media paragraph, now that D-03 is decided; the Billing row waits for P08.3's brief (DM-85) |
| H-01, H-02 | Routed to SV4 Stage A |
| H-03, H-13 | Routed to M07; the addendum to P08.1; tax and who writes the policies are D-12 |
| H-04 | 1.19 (P09); the ADR routed to AC3 |
| H-05, H-14, H-15 | Routed to P09 |
| H-06 | Routed to AC3 |
| H-07 | 1.19 (SV2-L) |
| H-08 | Routed, each with an owner: the retry to SV4 Stage A; the CI policy's gate sentence to DM-94 with R-21; the rest to the next change to each file |
| H-09 | Finding 44 is R-28; the rest of finding 5 is in 1.19; findings 15 and 27 go with the next change to their files |
| H-10, H-11 | Routed to SV5; the mail wording to AC1 with DS-7 |
| H-12 | Routed to P10 |
| H-16 | Routed to P07.1 |
| C-01, C-02, C-08, C-09, C-16, C-17 | Routed to SV4 Stage A (C-09's P06.2-T fold) |
| C-03 | Routed to A01-R; the HDE adapter |
| C-04, C-07, C-13 | Routed to SV5 |
| C-05 | Decided: D-03 (a), OD-75 |
| C-06, C-11 | Routed to the photo processor with the R2 adapter |
| C-10, C-14 | Routed to AC1 to AC3 |
| C-12, C-18 | Routed to P11B |
| C-19 | Routed to the next change to each file |
| P-01 to P-09 | 1.19 places each; P-09 is A01-R |
| P-10 | Routed to P07.1 |
| K-01 to K-13 | Accepted as the risk register of record. Each retirement is a decision or an item above |
| D-01, D-02, D-03, D-06, D-07 | Decided, option (a) each (OD-75). D-06 and D-07 change governing text: DM-94 |
| D-04, D-05 | Wait for P08.3's brief; D-05 goes to the Dev Manager with it (DM-91) |
| D-08 | With D-03 at P07.1 |
| D-09 | Already settled: the offer follows launch, with advice before it is sold (OD-70, OD-71) |
| D-10 | Asked of Nathan with the owner's track: the Maker application's status |
| D-11 | To the Dev Manager with P08.3's brief |
| D-12, D-13, D-15 | Nathan's, due before P08.3 (D-12) and P11B (D-13, D-15) |
| D-14 | Nathan's, before AC1 (O10) |
| D-16 | A line of M07 |
| D-17 | Standing: his authorization each time (`apps/mobile/AGENTS.md`) |
| D-18 | Asked of Nathan |
| Section 8.1's two proposals | DM-94, with D-07: stop recording that a condition was applied; move the status log out of Implementation Control |
