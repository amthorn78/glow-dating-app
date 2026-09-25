# Nathan's answers to the DM-01 and DM-02 questions, with their consequences

- **Source:** Nathan Amthor answered the Dev Manager's open questions directly in the Dev Manager session on 25 September 2026, after DM-03 was pushed. This report records his answers word for word and states what each one changes. It is the only way the Dev Manager can pass them on: this session cannot message the primary manager.
- **Consultation ID:** none. This is owner input, not a consultation. The primary manager assigns an ID in the review log if it wants one.
- **Basis:** `claude/stoic-carson-66gdig` at `fa4dc5f78e80bd9994796bfc41d07a79c90d0991`, and this branch at `23951c4` (DM-03).
- **What I checked:**
  - the reserved connection-variable names in `services/api/glow_api/configuration_profiles.py`: `DATABASE_URL` and `GLOW_DATABASE_URL` are both reserved;
  - that `services/api/glow_persistence` hardcodes no schema, `search_path` or `db_table` schema prefix (`grep`: none found);
  - the cloud-environment secrets documentation page. It does not say whether one environment's variables can be limited to some of its sessions.

  I made no provider, database, HDE or Railway call.

## 1. Summary

Nathan decided all eight points. Every one is now an owner direction and belongs in the owner-direction register as a new row, with his words below as the quote.

- **Two answers change governing documents substantially:**
  - the plan amendment for a CI PostgreSQL proof before P06.2;
  - the separate logical database, which supersedes part of OD-03, ADR 0002 and PF01 §4.
- **One answer declines my recommendation:** WordPress stays the staff surface. I accept it. Its safeguards follow from his own wording (A4).
- **Two answers need a small follow-up from Nathan:**
  - the Stream secret: I cannot confirm per-session scoping within one environment, so I give the smallest options with their costs (A5);
  - the HDE contract: the HDE owner and the dating-app integration owner are not named anywhere (A7).

## 2. The answers and what follows

### A1 — S15 exceptions

> "Yes. S15 must allow legally required disclosures, licence notices, and essential system screens. Compliance takes priority. Please document these as narrow, explicit exceptions and make the resulting screens clear and usable. An optional product screen should not be classified as an exception merely because it is convenient to do so."

**Consequences:**

- ADR 0003 decision 4 and the carve-outs bullet in PF01 §7 change from "proposed, awaiting confirmation" to **accepted exceptions**, listed exhaustively:
  1. legally required disclosures;
  2. licence notices;
  3. essential system screens.
- Each exception carries two requirements:
  - **a named basis:** the law, store policy or platform requirement that makes it necessary;
  - **a usability requirement:** the resulting screen is clear and usable in Glow's presentation, wherever Glow controls the presentation.
- Add Nathan's test in his words: *an optional product screen is not an exception merely because it is convenient.* One consequence: a provider feature that brings its own interface, such as a hosted chat or payment widget chosen for convenience, does not qualify.
- **Reading of "essential system screens":** screens the operating system or store requires and Glow cannot replace. Examples: permission dialogs, store purchase sheets, and platform sign-in flows if social login is adopted. Nathan should correct this if he meant something wider.
- My DM-03 findings G3 and G4 resolve:
  - the interim sentence ("until Nathan confirms …") becomes the accepted rule;
  - the principle is in force, and only the display rule's role as S15's answer stays conditional on the I1 review.
- **Documents:** ADR 0003 (status and decision 4), PF01 §7 (and its revision history), the P06.1 brief ("S15: decided"), register row OD-14 (confirmation added) and a new register row.

### A2 — Disposable PostgreSQL proof before P06.2

> "Yes, I approve the plan change. Use a disposable PostgreSQL instance in CI to prove send-versus-block ordering and sign-in against real database behavior before P06.2. It must have no connection to a shared or production database. Record what the proof tested and its result, then dispose of the database."

**Consequences:**

- **This is the plan amendment PF01 §6 requires.** PF01 needs a new revision: §6 (the exception, alongside the existing WordPress database exception), §8 (the sequence: after P06.1 closes, before P06.2) and the revision history.
- **A new work item**, for example "P06.0-DB, early disposable-PostgreSQL proof". The primary manager chooses the ID. Under the one-item rule (OD-08) it starts after P06.1's CI and review are clear.
- **Scope, from Nathan's words:**
  - send versus block ordering (P11 case DB06);
  - sign-in on the real database (a minimal DB09).
  - Applying the migrations the proof needs is part of the setup (part of DB01). Record it as incidental, not as DB01 acceptance.
- **Boundaries:**
  - PostgreSQL runs only as a CI service container, or a local throwaway for development, with CI-generated credentials;
  - no Railway, no shared or production database, no HDE, and no reuse of any reserved `DATABASE_URL` or `GLOW_DATABASE_URL` value from an environment;
  - the runtime guards (development and test only, readiness 503) stay in place;
  - adding django-allauth and a PostgreSQL driver is a dependency change, so full scope.
- **"Record … then dispose":**
  - the evidence record names the PostgreSQL image digest, the migrations applied, each test and its result;
  - it records that the container ended with the job and that no data or credential persisted.
- **What the proof does not claim:** real persistence acceptance. `docs/testing/p11-deferred-acceptance.md` marks DB06 and DB09 as "partially evidenced in CI (early proof)". P11A and P11B still rerun them on the real target.
- **Documents:** PF01 (§6, §8, revision), a new brief in `docs/planning/`, `docs/testing/p11-deferred-acceptance.md`, a new register row, a Work Register row (Notion), State of the App R01 at its next refresh.

### A3 — A separate logical database for the app

> "Yes, I support a separate logical database for the app on the same PostgreSQL service as HDE, provided this arrangement has a credible path to scale. Give the app its own credentials and permissions, keep its data separate from HDE's tables, and verify the service's capacity and operational limits. If usage later requires independent resources, the app database should be movable to its own service without redesigning the application."

**Consequences:**

- **Supersessions:**
  - OD-03's "same logical database" preference is superseded: a new register row, with OD-03 marked "Superseded by OD-nn".
  - ADR 0002's shared-logical-database section is superseded by a new ADR (0004, database placement).
  - PF01 §4's paragraph and A02's wording change. The 23 September audit's "same logical database is supportable" stays as dated evidence.
- **Conditions Nathan set, as acceptance criteria for P11** (and for the A2 proof where they apply):
  1. **Own credentials and permissions:**
     - an app owner role, a migration role and a runtime role;
     - none of them is `postgres`, and none has any grant on HDE's database;
     - HDE's roles get no grant on the app database.
  2. **Data kept separate:** nothing in the app reads or writes HDE's tables. HDE data comes only through HDE's supported interface (PF01 §5). PostgreSQL does not allow cross-database queries, which enforces this structurally.
  3. **Capacity and operational limits verified before P11C:**
     - connection limits, with the pool budget per service;
     - storage;
     - backup scope and frequency;
     - maintenance and upgrade coupling.

     This is a bounded read-only inspection under its own assignment. PF01 D08 permits read-only inspection, and any Railway read needs that item's explicit scope. It does not start now.
  4. **Movable without redesign.** Nothing needs to change today:
     - the API reserves its own connection name, `GLOW_DATABASE_URL`;
     - the provisional models hardcode no schema or `search_path`.

     To keep it that way:
     - no dependency on HDE-owned roles, extensions or objects;
     - migrations are self-contained;
     - P11A proves a move by dumping and restoring the app database into a separate disposable instance, with the configuration change as the only application change.
- **Accepted residual risk.** A platform restore of the shared service still restores HDE and the app together (DM-03 D1). With Nathan's move-out path, that is recorded as accepted. DB13's restore proof uses a logical restore of the app database, and recovery runbooks must not use a platform restore for an app-only incident without HDE-effect review (D08).
- **Documents:** a new ADR 0004, ADR 0002 (supersession note), PF01 §4 and A02, `docs/operations/migration-plan.md`, `docs/operations/resource-ownership.md`, `docs/testing/p11-deferred-acceptance.md` (a move-out case), new register rows.

### A4 — WordPress and Django

> "No to the split as phrased. WordPress should provide the public sales landing page and the staff admin and support interfaces. Django should own the application API, permissions, business rules, and application state. The WordPress staff tools should use scoped Django APIs; WordPress should not become a second application backend or access app or HDE tables directly."

**Consequences:**

- My DM-02 B5 recommendation is **declined by Nathan**. This agrees with PF01 §1 and §4, which already put staff operations in WordPress behind scoped admin APIs.
- **New:** WordPress also hosts the **public sales landing page**. PF01 §1's product baseline gains it.
- These requirements follow from Nathan's own conditions, and the P07 brief must make them concrete:
  - **Scoped APIs, not a shared key:**
    - each staff action reaches Django with the individual staff member's identity and scope, so that Django authorizes and audits the person (PF01 §7: "privileged API calls enforce scope and audit the staff actor");
    - a WordPress service credential alone authorizes nothing.
  - **Its own storage:** WordPress's own database holds only CMS and staff-interface data. It is neither the app database nor HDE's, and it is outside both.
  - **No sensitive data at rest in WordPress:** moderation evidence and chat content are fetched on demand through the scoped API and not stored in WordPress's database or logs.
  - **Hardening,** as P07 brief items, not decisions for Nathan now: the hosting and update policy, staff multi-factor authentication and a plugin allowlist.
- **Documents:** PF01 §1 and §4 (the landing page; "no second backend and no direct table access" stated explicitly), a new register row, the P07 brief when written.

### A5 — The Stream secret

> "I prefer the simplest setup that protects the secret. I do not want a separate cloud environment solely for this proof if the existing CI setup can restrict the Stream secret to the jobs or sessions that need it. Keep the secret server-side and limit access. If that cannot be done safely without a split, bring back the smallest workable option and its added cost and complexity."

**Findings:**

- **CI needs no Stream secret.** No Foundation job calls Stream, and the harness job planned for I2b is offline by design: its tests assert that no `STREAM_*` variable is present. So CI stays without the secret. That is the safest setting, and it costs nothing.
  - If a future CI job ever needs it, a repository secret is exposed only to the steps that reference it.
  - Per-job **environment** secrets need a paid plan for private repositories, as far as I know. That is unverified; see Limits.
- **Cloud sessions are where the exposure is.**
  - The `STREAM_*` variables are set on the `Glow app` environment, so every session in it receives them: manager, Dev Manager, reviewers and implementers.
  - I found no documented way to give a variable to only some sessions of one environment. The documentation page I read does not cover it.
  - I cannot say that the current setup restricts the secret safely. So, as Nathan asked, the smallest workable options:

| Option | How | Added cost and complexity | Residual risk |
|---|---|---|---|
| **1. Add the variables only while needed (recommended)** | The `STREAM_*` variables are removed from `Glow app`. Before starting a session whose prompt authorizes live Stream calls (the I1 review, I2a, I2b), Nathan adds them, starts that session, and removes them afterwards. A session's environment is fixed at start, so other sessions started while they are absent never receive them | Two settings edits per live session, about three sessions for the rest of P06.1. No second environment and no second Setup script | Forgetting to remove them leaves today's exposure. The manager's prompt for each live session can end with a reminder |
| 2. A second environment | A copy of `Glow app` with the Stream variables, used only for live sessions | One-time setup; two environments whose Setup scripts must stay identical (the pin test covers the repository, not the environment settings) | Lowest exposure; the drift risk between environments is new |
| 3. As today | No change | None | Every session can read the secret. The impact is low (a development application with synthetic data), but it is avoidable |

- **Also recommended in every case:** rotate the development secret when P06.1 closes (DM-02 B8), and keep "server side only" as it is (OD-12).
- **For Nathan:** confirm option 1, or choose another. See Questions.

### A6 — The intermittent CI failure

> "CI needs to give us a dependable result. Investigate the failure now. If it is caused by this work or prevents this work from being verified, fix it as part of the current item. If it is unrelated, create a focused repair item and treat reliable CI as a prerequisite for accepting the affected work. A passing rerun alone does not resolve an intermittent failure."

**Consequences:**

- **Investigation starts now, inside P06.1.** Nathan's direction makes the diagnosis part of the current item. It does not break the one-item rule (it answers DM-01 P5).
- **Routing after the diagnosis:**
  - The failure is in the mobile rendered suite, and P06.1 changes no mobile code. So it is unlikely to be *caused by* P06.1.
  - But it runs on every full-scope PR run of PR26, so a red occurrence **prevents P06.1 from being verified**. By Nathan's rule, that makes the fix part of P06.1 whenever it blocks PR26's gate.
  - If the diagnosis shows it cannot occur on PR26's jobs, it becomes a focused repair item.
- **New acceptance rule:** "a passing rerun alone does not resolve an intermittent failure". The manager workflow's CI evidence rules gain:
  - a head whose run failed intermittently is not accepted on a rerun's pass alone;
  - the failure needs a diagnosis and either a fix or a recorded, reviewed explanation;
  - reliable CI is a prerequisite for accepting the affected work.
- **The earlier evidence:** the diagnostics on `app-builder-1/p05-1-birth-diagnostics` are the starting point.
- **Documents:** the manager workflow (the one-item rule and CI evidence), the current handoff (next actions), the P06.1 brief (a diagnosis session or a correction), a new register row.

### A7 — The HDE contract and Stream's timing

> "I have submitted the Stream Maker Account application. Stream told me its review typically takes about two weeks; that is an estimate, not an approval date. The email I can see does not include a separate application-submission confirmation.
> That timeline does not answer when HDE's supported application contract will arrive. I do not have a confirmed HDE delivery date. Please obtain one from the HDE owner and have the supported, versioned contract delivered to the dating app integration owner, with me included as Product Owner and the contract recorded in repository Markdown. Identify the supported interface, release or environment, and authorized access needed for the app integration."

**Consequences for Stream:**

- A04 and the P06.1 economics record the Maker application as **submitted on or before 25 September 2026, status pending**.
- Stream's review estimate is about two weeks, "an estimate, not an approval date". No separate submission confirmation has been seen.
- The economics discovery Nathan runs should check the dashboard for the application's status.
- Nothing is assumed about approval or its terms. The $0 budget (OD-12) stands.

**Consequences for HDE:**

- **Who acts.** Neither the Dev Manager nor the primary manager may contact HDE's systems or change them (D08), and neither can send email. The request Nathan describes therefore needs:
  - **(a)** a written request that the primary manager can prepare, in repository Markdown, listing what the app needs. PF01 §5, "Before live integration", already lists it:
    - the supported interface and its version;
    - the release or environment;
    - authentication and the authorized access, including read and write scope;
    - idempotency, rate limits, the retry policy and the error semantics;
    - output and cache rights;
    - deletion obligations;
    - throughput and granularity (A07);
  - **(b)** a person to send it to the HDE owner, and to receive it as the integration owner.

  **Neither role is named anywhere in the repository** (see Questions). If Nathan holds both, the request is his to send to himself or to whoever maintains HDE.
- **Where the contract is recorded.** Nathan asks for it "recorded in repository Markdown". PF00's authority map says HDE behavior and contracts belong to HDE's own canonical sources, "referenced, never rewritten by app documentation" (R06, duplicate authority). Both are satisfied by recording in the app repository a **contract receipt** that names the delivered version, the HDE commit or release, and the environment. The HDE text itself stays governed by HDE; a verbatim copy, if one is wanted, goes under `docs/planning/sources/` and is marked non-governing.

  The receipt, for example `docs/architecture/hde-contract-receipt.md`, holds:
  - the contract version, and the HDE commit or release;
  - the environment;
  - the authorized access (names only, no secrets);
  - the delivery date, and who delivered it to whom, with Nathan included;
  - the app's adapter mapping against the provisional seam (`docs/architecture/provisional-hde-seam.md`).
- **Tracking:** A01 and A07 gain the requested date and an owner in the Work Register, and in the register as a new row.
- **Documents:** a new request document (for example `docs/planning/hde-contract-request.md`), later the receipt, PF01 §10 A01, A04 and A07 wording, the P06.1 brief (economics), new register rows.

### A8 — No paid GitHub plan

> "No paid plan at this time; there is no budget for it. Use the review and branch controls available at no additional cost, document any protection we cannot enforce, and revisit a paid plan when there is a budget."

**Consequences:**

- The CI policy's "Branch enforcement limitation" gains a short list of **controls not enforced** on this private personal repository:
  - required status checks;
  - required reviews;
  - blocking direct pushes to `main`;
  - blocking force-pushes;
  - code-owner review.

  It also states the **procedural substitutes in force:**
  - the Foundation gate on the exact head;
  - the exact-head review;
  - waiting for Codex;
  - the pre-merge checklist (workflow step 7);
  - the Dev Manager read of governing Markdown;
  - never force-pushing.
- **No-cost controls to use:**
  - Dependabot alerts, if Nathan enables them. This is a repository setting only he can change, and as far as I know it is free for private repositories. Unverified; see Limits.
  - The pre-merge checklist, filled in on every PR.
- **Revisit trigger:** "when there is a budget". It is recorded in the register, so a later manager raises it at P09 (release preparation) at the latest.
- **Documents:** the CI policy, a new register row.

## 3. Verdicts

These are owner decisions, not items for approval. My position on each:

| # | Decision | Dev Manager position |
|---|---|---|
| A1 | S15 exceptions, narrow and explicit | Agree. Record them as above, with a named basis and usability for each |
| A2 | Disposable PostgreSQL proof in CI before P06.2 | Agree. It is the plan amendment; scope and claim limits as above |
| A3 | A separate logical database on HDE's service | Agree. Nathan's conditions become P11 acceptance criteria. The shared platform restore is recorded as accepted risk, with the move-out path |
| A4 | WordPress for the sales page and staff tools, Django owns everything else | Accept. It declines my B5. The safeguards above follow from Nathan's own conditions |
| A5 | The simplest setup that protects the secret | CI needs no secret. For sessions, I recommend option 1 (add the variables only while needed), pending Nathan's confirmation |
| A6 | Investigate the flake now; reliable CI before acceptance | Agree. It answers DM-01 P5 and adds the "no rerun-only acceptance" rule |
| A7 | Stream Maker pending; an HDE contract date and delivery | Agree. It needs named owners, and a receipt that keeps HDE's authority intact |
| A8 | No paid GitHub plan | Agree. List what is not enforced and the procedural substitutes |

## 4. Questions for Nathan

1. **The Stream secret (A5):** use option 1, adding the `STREAM_*` variables to `Glow app` only while a live Stream session runs? Or would you rather have option 2, a second environment?
2. **HDE (A7):** who is the HDE owner who will give the delivery date, and who is the dating-app integration owner who receives the contract? If both are you, say so, and the primary manager prepares the written request for you to send.

## 5. Documentation to update

- **The owner-direction register:** eight new rows, one per answer, with the quotes above. Mark OD-03 "Superseded" (A3). Mark OD-08's and OD-14's pending notes as resolved (A6, A1).
- **The Dev Manager review log:** record these answers against DM-01 questions 1–4 and DM-02 questions 1–6, as the log's closing line provides.
- **PF01:** §1 (A4), §4 and A02 (A3), §6 and §8 (A2), §7's carve-outs (A1), §10 A01, A04 and A07 (A7), and the revision history.
- **ADRs:** ADR 0003 (A1), ADR 0002 (the supersession note) and a new ADR 0004 on database placement (A3).
- **The manager workflow:** the flake and the rerun rule (A6).
- **The CI policy:** controls not enforced and their substitutes (A8); no Stream secret in CI (A5).
- **The P06.1 brief:** "S15: decided" (A1), the flake diagnosis (A6), the Maker status in economics (A7).
- **New:** a brief for the early PostgreSQL proof (A2) and an HDE contract request (A7).
- **Other files:** `docs/testing/p11-deferred-acceptance.md` (A2, A3), `docs/operations/migration-plan.md` and `docs/operations/resource-ownership.md` (A3), `docs/operations/environment-inventory.md` (A5, after Nathan's answer).
- **The current handoff:** next actions (A2, A6, A7).

## 6. Limits

- **The HDE request:** I did not contact anyone and cannot. A7's request needs a person.
- **Unverified from memory:**
  - that GitHub environment secrets need a paid plan for private repositories (A5);
  - that Dependabot alerts are free for private repositories (A8).

  The primary manager, or Nathan in GitHub's settings, should confirm both before either is written down as fact.
- **Environment-scoped variables:** I could not confirm from the product documentation whether one cloud environment can give a variable to only some of its sessions (A5).
- **Railway:** capacity and backup behavior (A3) are unverified. That is for the bounded inspection Nathan's condition requires.

Status: complete
