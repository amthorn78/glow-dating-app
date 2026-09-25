# DM-02 — Build review

- **Consultation:** DM-02, requested by Nathan through App Manager 3 on 25 September 2026.
- **Reviewer:** Dev Manager 1, session branch `claude/dev-manager`.
- **Commit reviewed:** `3888e8f635c4efdaf31cf074e1e423ff5f98de29`, an ancestor of the manager branch `claude/stoic-carson-66gdig`. The later `68b4ab9` changes only records.
- **Companion report:** [DM-01 process review](2026-09-25-dm-01-process-review.md). It holds the environment check and the start gate, which both passed.

## 1. What I read and ran

**Read completely:**

- the P06.1 brief and evidence record;
- PF01 (sections 1–11) and ADR 0002;
- `docs/ephemeral/2026-09-25-p06-1-i1-review-prompt.md`;
- `.github/workflows/foundation.yml`, `scripts/change_scope.py` and `.dockerignore`;
- the State of the App and the current handoff.

**Read in part:**

- `docs/planning/database-audit-2026-09-23.md` (outcome, recommendations and limits);
- `docs/testing/p11-deferred-acceptance.md` (the case tables and the carry-forward sections);
- the layout of `apps/mobile/src`, `services/api`, `packages/contracts` and `proofs/stream-chat`.

**Offline checks.** I extracted the tree with `git archive 3888e8f… | tar -x` into my scratchpad. Every command ran under `env -i PATH HOME LANG=C.UTF-8`. Only installs received the proxy and CA variables, passed by reference; no `STREAM_*` variable was present. Toolchain: node v24.19.0, npm 11.9.0 and Python 3.12.14, from `$HOME/.local/bin`. The Setup-script ownership check printed `0`.

| # | Command (working directory) | Result |
|---|---|---|
| 1 | `python3.12 -m venv .venv && .venv/bin/pip install --require-hashes -r requirements-dev.lock && .venv/bin/pip check` (`services/api`) | Installed; "No broken requirements found." |
| 2 | `GLOW_ENV=test .venv/bin/python manage.py check` / `manage.py test tests` | "System check identified no issues"; `Found 253 test(s)` … `OK` |
| 3 | `ruff check .` / `ruff format --check .` / `mypy` | "All checks passed!" / "57 files already formatted" / "Success: no issues found in 29 source files" |
| 4 | `PYTHONPATH=. .venv/bin/python -m unittest discover -s ../../packages/contracts/tests` | `Ran 38 tests` `OK` |
| 5 | `python3.12 -I -m unittest discover -s scripts -p 'test_change_scope.py'` (root) | `Ran 13 tests` `OK` |
| 6 | Harness: venv, `pip install --require-hashes -r requirements-dev.lock`, `python -m unittest discover -s tests -t .` (`proofs/stream-chat`) | `Ran 49 tests` `OK` |
| 7 | `npm ci --ignore-scripts && npm run check` (`packages/contracts`), **before** the mobile install | Types and validators match, but `tests/corpus.test.mjs` **failed** ("test failed") |
| 8 | `npm ci --ignore-scripts && npm run check` (`apps/mobile`) | `tests 516`, `pass 516`, `fail 0` |
| 9 | `npm run check` (`packages/contracts`), **after** the mobile install | "Generated types and runtime validators match schemas."; `tests 373`, `pass 373`, `fail 0` |
| 10 | `npm audit` (`apps/mobile`) | **14 moderate**, 0 high, 0 critical. Two distinct advisories: GHSA-vcc3-ghjq-m6fr (`decode-uri-component` denial of service) and GHSA-w5hq-g745-h8pq (`uuid` bounds check) |
| 11 | `npm audit` (`packages/contracts`; `proofs/stream-chat` after `npm ci --ignore-scripts`) | "found 0 vulnerabilities" in each |

On row 7: the corpus test imports `apps/mobile/src/contracts/validation.ts`, and the node warning in row 9 names that file. It passed once the mobile dependencies were installed, which is the order CI uses. I infer, without isolating it, that the failure was that missing install, not a defect. See B10.

**Not run:**

- `npm run test:rendered` and `check:expo`: the cloud Chromium revision differs, and `playwright install` is forbidden;
- `export:development`, the smoke test and the container build: not needed for this review;
- any live Stream, database, HDE or Railway action.

## 2. Summary verdict

The build is in the condition its records claim:

- every offline suite I ran passes on `3888e8f`;
- the dependency picture matches the recorded 14 moderate advisories;
- the fixture-only guards and the HDE boundary are intact.

The direction is sound for a fixture-stage product. Two choices deserve an owner decision before they harden: database-last for the chat send path, and the shared logical database with HDE. WordPress as the operator surface deserves a second look before P07.

**I approve the S15 reading with conditions.** I request changes to P06.1-I2's scope: split it, and add the tests that make the proof's claims precise.

## 3. Findings

### B1 — Nathan's S15 principle needs explicit limits — *before the next implementation task*

- **Evidence:**
  - Nathan's words: *"There should never be any indication that there is anything happening outside Glow."*
  - The manager's working reading: no provider name, branding, identifiers, error text, notifications or data reaches the user interface, and everything the user sees comes from Glow's API in Glow's wording (P06.1 brief, "S15: decided").
  - PF01 §7 records the principle only inside "Chat and notifications".
- **Risk:** read literally, the principle collides with obligations the product must meet:
  - privacy policies and the App Store and Google Play privacy disclosures list third-party processors;
  - GDPR-style notices name the recipients of data (A05's geography decides which regimes apply);
  - open-source licence notices, such as `apps/mobile/EXPO-TEMPLATE-LICENSE.md`;
  - platform-mandated system interfaces: operating-system permission dialogs, store purchase sheets and any Sign in with Apple or Google flow if social login is added (PF01 §7);
  - possibly a provider's plan terms, if a plan requires attribution. This is **unverified**; I2 should check it.

  Without limits, a later session could either hide a legally required disclosure or treat a mandated system sheet as a defect. Separately, the principle is a user-experience rule, not a security control, so it does not answer PF01's "client the attacker controls".
- **Recommendation:** approve the reading, and add:
  - **(a) Scope:** Glow's in-app experience and every communication Glow sends (push, email, in-app errors, deep links, the shared links users see).
  - **(b) Carve-outs**, for Nathan to confirm: legally required disclosures (policies, store privacy labels, processor lists, data export contents where the law requires recipients), licence notices, and system interfaces the platform mandates.
  - **(c) Server and operator consumers:** the display rule also binds them. Stream member or user custom data is never forwarded into exports, staff or WordPress views, push content or analytics. Otherwise S15's hidden channel reaches a human through Glow itself.
  - **(d) Reach:** make the principle a product-wide rule in PF01 §7, with a new first paragraph or a "Product presentation" paragraph, not only a chat sentence. Record the display rule as ADR 0003.
- **Documents:** PF01 §7, the P06.1 brief, a new `docs/adr/0003-chat-display-rule.md`, `docs/architecture/privacy-and-safety-rules.md`.

### B2 — P06.1-I2 is too large and under-specified — *before the next implementation task*

- **Evidence:** the brief's "Sessions" and "I1's open questions" give I2 eleven topics:
  - revocation and history;
  - suspension and deletion;
  - token expiry;
  - reconnection;
  - races;
  - outage;
  - economics;
  - the architecture document;
  - Video and Feeds;
  - the G2 and S10 reruns and the existence check;
  - the S15 mapping.

  The per-session budget is 20 users and 5,000 calls. I1 alone used 19 users and 884 calls in four runs, with one run lost and one cleanup gap.
- **Risk:**
  - the budget runs out before coverage is complete;
  - "outage" and "race" invite overclaiming, because neither can be really induced in a sandbox without persistence;
  - economics research spends an implementation session on work that needs the dashboard.
- **Recommendation:** split and specify.
  - **I2a, the revocation and safety proof** (live, budgeted).
    - Revocation under Nathan's history policy, by named mechanism: member removal, a channel-level ban, a per-user `revoke_tokens_issued_before`, hide or freeze. For each, state which ends:
      - reads (REST);
      - an **already-open WebSocket subscription**, which must stop receiving events;
      - token reuse;
      - the S15 write.
      Messages must stay retained for safety reports.
    - Suspension and deletion, including what a hard user delete does to messages and **member custom data** needed for safety evidence. This conflicts with Nathan's history policy unless the design says otherwise.
    - Token expiry, reconnection and cross-device use (two clients per user).
    - **Send versus revocation, provider side only:** the server's send attempted after revocation is refused. State explicitly that DB-level linearization is P11 (DB06), and claim nothing more.
    - **Outage as fault injection:** the server's Stream client pointed at an unreachable endpoint; the app send path must refuse without partial state. No real outage is claimed.
    - The S15 mapping, per the brief. Add: can the server clear or overwrite member custom data, does member removal delete it, and do the three `member_custom_on_*` app settings stay off, checked by the harness.
    - The G2 and S10 reruns, and the existence-oracle comparison (existing versus non-existent IDs).
    - The fixes not yet exercised live.
  - **I2b, the configuration of other products and the documentation** (live but small).
    - Video and Feeds: what a user token can do, and lock-down by configuration only.
    - `docs/architecture/chat-provider-permissions.md`, including the exact configuration as a reapplicable plan for a future production application (see B7).
  - **Economics:** not an implementation session. A read-only dashboard discovery Nathan runs, as for the baseline, plus Stream's public pricing and terms. Record: the plan limits, overage behavior with no payment method, any attribution requirement (B1), the data-processing agreement and region (US East versus launch geography, A05), and Maker eligibility.
  - **Remove from I2:** executing the restore command. Decide at P06.1's close whether the development application stays locked down for P06.2, which is likely, or is restored.
  - **Budget:** each session's prompt sets its own run plan against the 20-user cap, with one run reserved for a rerun.
- **Documents:** the P06.1 brief ("Sessions", "Brief — P06.1" outcomes 4 and 5, guardrails), the I2 prompt(s).

### B3 — Database last leaves the chat design's core unproven — *soon (before P06.2 is briefed; plan amendment, Nathan decides)*

- **Evidence:**
  - PF01 §6: bringing database work forward requires "a concrete technical reason and an explicit plan amendment".
  - The P11 deferred list grows with each phase: the P04.3 and P05.1 carry-forwards to DB05–DB13 and PV01–PV07.
  - P06.1's chosen design makes the server the sole sender, so no new send may be authorized after a block or unmatch commits (F11, F13; PF01 §7). That ordering is DB06, and it cannot be proven without PostgreSQL.
  - The Stream token endpoint planned for P06.2 depends on authenticated sessions (DB09, allauth headless), which also need a database.
  - State of the App 1.7 describes R01 as mitigated only by "ports, static model and migration definitions and conformance cases".
- **Risk:**
  - The safety-critical ordering at the centre of the chat design, and the authentication that token issuance depends on, would first run for real in P11.
  - By then P06.2, P07 (report after unmatch) and P08 (deletion across providers) will have been built on fixture semantics.
  - A structural surprise in P11 (transaction boundaries, lock ordering, allauth's schema) would force rework across four phases. This is R01's escalation condition, found late.
- **Recommendation:** a narrow plan amendment, for Nathan to approve. It meets PF01's bar: a concrete technical reason, not convenience.
  - Before P06.2, a bounded "P11A-early" item runs an **ephemeral PostgreSQL in CI only**, as a GitHub Actions service container:
    - no Railway;
    - no shared database;
    - no credentials beyond CI-generated ones.
  - It proves three things:
    - DB01 (migrations from zero for the provisional models, or the subset P06 needs);
    - DB06 (send-versus-block linearization, using the planned transaction and outbox shape);
    - a minimal DB09 (allauth headless session and token issuance).
  - It connects no application or HDE database, changes nothing in D08 or P11's production sequencing, and treats every other P11 case as still deferred.
  - Otherwise, if Nathan declines, P06.2's brief must mark its send path and token endpoint "fixture ordering only", and R01's escalation condition should be checked explicitly at P06.2's review.
- **Documents:** PF01 §6 and §8 (the amendment and the revision history), `docs/testing/p11-deferred-acceptance.md` (which cases move), the Work Register (a new item), the State of the App's R01.

### B4 — The shared logical database with HDE has concrete coupling costs — *soon (decide before P10's migration manifest; Nathan decides)*

- **Evidence:**
  - PF01 §4 and ADR 0002: the same logical database `railway`, an app schema with restricted roles, "unless assessment establishes a strong concrete reason against it".
  - The 23 September audit found HDE and the legacy backend both using the privileged `postgres` role. Backup configuration and restore viability were **not verified** (audit, line 100).
  - DB13 requires restoring an actual backup and replaying deletion tombstones.
- **Risk:** these are the concrete reasons PF01 asks for:
  - **(a) Restore coupling.** Railway volume backups and point-in-time restores act on the whole instance, so restoring the app, for example for DB13 or an incident, rolls HDE back too, and restoring HDE rolls the app back.
  - **(b) Shared blast radius** for connection limits, locks, maintenance, major-version upgrades and extensions.
  - **(c) Mistakes in `search_path` or grants in one logical database.** Mitigable, but a standing hazard beside a privileged shared role.
- **Recommendation:** Nathan decides between:
  - the current preference;
  - **a separate logical database on the same PostgreSQL service**, in the same Railway project, as Nathan directed. It keeps colocation and cost, and gives per-database dump, restore and drop, separate owners, and no schema mixing;
  - a separate PostgreSQL service in the same project.

  **I recommend the second option,** subject to P11's capacity check. Record the choice as an ADR before P10 fixes the migration manifest. Nothing needs to change now; the decision is cheap now and expensive after P11A.
- **Documents:** ADR 0002 (superseded in part by a new ADR), PF01 §4 and A02, `docs/operations/migration-plan.md`.

### B5 — WordPress as the operator surface — *consider (before the P07 brief; Nathan decides)*

- **Evidence:**
  - PF01 §1 and §4: WordPress is the operator interface and the public policy and support site. It needs its own database and staff authentication (PF01 §6, §7).
  - Staff will see moderation evidence and chat content under least privilege (PF01 §7).
- **Risk:** it adds a second authentication system, a plugin ecosystem with a history of privilege-escalation advisories, its own hosting and database, and a PHP codebase, all on the surface with the most sensitive access (reports, chat evidence and possibly birth data). Every staff action crosses an extra trust boundary into the admin API.
- **Recommendation:** keep WordPress for the public policy and support site. Before P07, reconsider staff operations in **Django's admin or a small staff app** on the existing API: the same authentication stack, audit model, deployment and tests, and no new infrastructure. If WordPress stays for staff, the P07 brief should name its hosting, update policy, staff multi-factor authentication and plugin allowlist.
- **Documents:** PF01 §1, §4 and P07, a new ADR, `docs/architecture/domain-and-data-boundaries.md`.

### B6 — The proof harness is tested outside CI — *before PR26 merges (part of the current item)*

- **Evidence:**
  - 49 harness tests, 25 files under strict mypy, and Ruff: none runs in any Foundation job (the evidence record, "Checks": "Not run"; `foundation.yml`).
  - Once PR26 merges, `main` holds code no CI checks.
  - `.dockerignore` is an allowlist, so the harness cannot enter the API image (verified).
- **Risk:** a later change to `proofs/` or its locks passes CI without anything checking it. P06.2 and P11 will re-run PV03 with this harness.
- **Recommendation:** as a correction within P06.1, add one job, or steps in the API job, to `foundation.yml`:
  - the hash-locked install;
  - `unittest` under `env -i`;
  - Ruff and mypy;
  - `node --check`.

  This is a workflow change, so it follows the CI policy's workflow rule: independent classification and a read of the whole workflow diff. Alternatively, keep the harness off `main` in a separate archival branch. I do not recommend that, because P11 needs it.
- **Documents:** `foundation.yml`, the CI policy, the P06.1 brief (owned paths for the correction).

### B7 — Stream with a display rule, rather than one channel per person — *approved with conditions*

- **Evidence:**
  - I1: 68 attributable refusals and one design finding (the evidence record).
  - Option 2 (per-person channels) doubles writes and channels and loses read receipts (the brief).
  - A messaging port exists (PF01 §4).
- **Assessment:** the display rule is proportionate. The residual channel needs two modified clients that are both still matched, and it gives them nothing beyond what they already have outside Glow.
- **Conditions:**
  - **(a)** I2a shows that member custom data cannot change anything Glow displays or forwards (B1 (c)), and that revocation ends the write.
  - **(b)** Deletion and export (PV07) include member custom data at Stream.
  - **(c)** The configuration I1 applied becomes a reviewed, reapplicable plan for the production application (the harness's `configure` with a fixed target). The development application's lock-down is not a production control.
  - **(d)** Option 2 stays the recorded fallback if (a) fails.
- **Also:** I1's usage and the plan's automatic overage policy with no payment method on file make billing an **open launch gate** (A04), not a P06.1 blocker.
- **Documents:** the P06.1 brief, `docs/architecture/chat-provider-permissions.md` (I2b), ADR 0003.

### B8 — Credentials in the shared environment — *consider (Nathan decides)*

- **Evidence:**
  - Every `Glow app` session receives `STREAM_API_SECRET`, including managers, reviewers and this Dev Manager, none of whom need it (State of the App 1.7, "Environment secrets").
  - Any process can make authenticated TypeSafe calls through the proxy.
- **Risk:** the exposure is wider than the need. A prompt-injection or tool mistake in any session could use the secret. The development application holds only synthetic data, so the impact is currently low.
- **Recommendation:** Nathan could run two cloud environments: `Glow app` without the Stream variables, for managers, the Dev Manager and code sessions, and `Glow app + Stream` for proof sessions. That makes the need-to-have explicit. Rotate the development secret at P06.1's close, since it is cheap.
- **Documents:** `docs/operations/environment-inventory.md`, the start prompts.

### B9 — Dependency advisories — *consider*

- **Evidence:** 14 moderate advisories, from 2 distinct GHSAs, through the Expo toolchain (row 10). The State of the App calls GHSA-vcc3-ghjq-m6fr "Expo Router URL decoding". It is `decode-uri-component` denial of service, so the description needs correcting. The harness and contracts have none.
- **Risk:** low for a development-only fixture app. Deep-link parsing becomes relevant once P06.2 or P09 adds real deep links.
- **Recommendation:**
  - Keep remediation as a pre-release obligation.
  - Record an `npm audit` result in each phase's evidence (one line), so drift is visible.
  - Consider enabling GitHub's Dependabot alerts, which are free and read-only, for Nathan.
- **Documents:** the State of the App (the correction), `docs/operations/ci-and-branch-policy.md` (the audit line).

### B10 — Build and CI gaps — *soon*

- **The rendered-test flake:** three occurrences of a form submit that does not advance. It is the only known red-CI source. It should be diagnosed as part of the current item's CI condition (DM-01, P5).
- **Branch protection:** not enforceable here, so the Foundation gate is advisory. That is acceptable only with DM-01 P7's pre-merge checklist.
- **Cross-package order dependency:** `packages/contracts`'s corpus test imports mobile source, so it fails unless `apps/mobile` is installed first (row 7). CI orders it correctly. Local instructions should say so, in `packages/contracts/README.md` or `docs/operations/local-development.md`.
- **Mobile fixture logic mirroring Python** (State of the App 2.8): mitigated by the shared fixtures in `packages/contracts/fixtures/` and the mobile `conformance.test.ts` files. **Condition:** do not extend it. P06.2 should take chat state from API-served fixtures through the development HTTP client, not new client-side domain logic, so there is one authority to replace at P11.
- **Proof tooling in the application repository:** acceptable, because it stays out of the runtime and the image. It needs B6.
- **The HDE contract (A01, A07)** has no owner or date, and compatibility, the product's differentiator, is entirely synthetic. Nothing to change in the app; Nathan should name when HDE's supported contract is expected (Questions).

## 4. Approval items

| # | Item | Verdict | Reasons and conditions |
|---|---|---|---|
| 1 | The manager's reading of the S15 decision and principle | **approved with conditions** | B1 (a)–(d): scope, carve-outs for Nathan to confirm, the display rule binding server and operator consumers, a product-wide rule plus ADR 0003. The decision stays conditional on the I1 review confirming S15 (DM-01, P4) |
| 2 | P06.1-I2's planned scope | **changes requested** | Split into I2a (revocation and safety, live) and I2b (Video and Feeds, architecture document). Economics goes to a Nathan-run dashboard discovery. Add the tests and precise claim limits in B2. Remove the restore run. The Dev Manager reads the I2 prompt(s) before Nathan runs them (DM-01, P1) |
| 3 | Database last with a large fixture layer (R01) | **refer to Nathan** | I recommend B3's narrow amendment: CI-only ephemeral PostgreSQL proving DB01, DB06 and a minimal DB09 before P06.2. It meets PF01 §6's bar for a concrete technical reason |
| 4a | The shared logical database with HDE | **refer to Nathan** | B4. I recommend a separate logical database on the same PostgreSQL service, decided by ADR before P10 |
| 4b | Stream with a display rule, rather than per-person channels | **approved with conditions** | B7 (a)–(d) |
| 4c | WordPress as the operator surface | **refer to Nathan** | B5: keep it for the public site, and reconsider staff operations in Django before P07 |
| 4d | Mobile fixture logic mirroring the Python domain | **approved with conditions** | B10: no further mirroring; P06.2 uses API-served fixtures |
| 4e | Proof tooling in the application repository | **approved with conditions** | B6: its offline tests in CI before PR26 merges |
| 5 | Build condition and technical debt | **approved with conditions** | Verified green offline (section 1). Conditions: B6, the flake inside the current item (DM-01 P5), the audit line per phase and the advisory description corrected (B9), the local order note (B10) |

## 5. Questions for Nathan

1. **S15 carve-outs (B1):** do legally required disclosures (privacy policy, store privacy labels, processor lists), licence notices and platform-mandated system screens fall outside "no indication of anything outside Glow"?
2. **Database proof (B3):** do you approve a plan amendment for a CI-only, disposable PostgreSQL proof of migrations, send-versus-block ordering and authentication before P06.2? No shared database, Railway or HDE is involved.
3. **Database placement (B4):** keep the same logical database as HDE, or use a separate logical database on the same PostgreSQL service in the same project?
4. **Operator surface (B5):** keep WordPress for staff moderation and support, or limit it to the public site and build staff tools on Django?
5. **Credentials (B8):** split the cloud environment, so that only proof sessions receive the Stream secret?
6. **HDE (B10):** when is HDE's supported application contract (A01, A07) expected, and who owns getting it?

## 6. Documentation to update

- `docs/pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md`:
  - §7 (the product-wide presentation principle with its scope and carve-outs, B1);
  - §6 and §8 (the amendment, if approved, B3);
  - §4 and A02 (B4, after Nathan decides);
  - §1, §4 and P07 (B5, after Nathan decides).
- `docs/planning/p06-1-chat-provider-proof.md`:
  - "S15: decided" (B1, and conditional on the review);
  - "Sessions" and the outcomes (B2);
  - owned paths for the CI correction (B6).
- New ADRs:
  - `docs/adr/0003-chat-display-rule.md` (B1, B7);
  - an ADR for database placement (B4);
  - an ADR for the operator surface (B5), if changed.
- `.github/workflows/foundation.yml` and `docs/operations/ci-and-branch-policy.md` (B6, as full-scope work within P06.1; the audit line, B9).
- `docs/testing/p11-deferred-acceptance.md`: the cases that move, if B3 is approved.
- `docs/continuity/state-of-the-app.md`: the advisory description (B9); R01 (B3). Update it at the next refresh, not before.
- `docs/operations/environment-inventory.md` (B8, if Nathan splits the environment).
- `packages/contracts/README.md` or `docs/operations/local-development.md`: the install order (B10).
- `docs/architecture/privacy-and-safety-rules.md`: the display rule for server and operator consumers (B1 (c)).

## 7. Limits

- **Stream, Notion and CI:** I made no Stream call, so every live result is the implementer's record, not mine. I did not read Notion. I did not run the rendered, Expo compatibility, export, smoke or container checks; the CI evidence for those is recorded, not re-run by me.
- **The contracts corpus failure** (row 7): I attribute it to install order by inference. It passed after the mobile install, but I did not isolate the error message.
- **The harness:** I did not review its code line by line. That is the exact-head review's scope, still pending. My statements about the harness rest on its tests passing, the evidence record and `.dockerignore`.
- **Railway backups:** the restore-coupling concern in B4 rests on Railway backing up by volume, per PF01 and the audit's unverified backup status. I did not check Railway's current backup documentation.
- **Legal and store requirements** in B1 are named as categories to verify, not as legal advice.

Status: complete
