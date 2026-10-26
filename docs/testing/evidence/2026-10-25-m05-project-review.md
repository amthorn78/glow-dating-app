# M05 — Whole-project review: evidence record

The independent whole-project review Nathan directed on 25 October 2026 (OD-48): *"make sure we are on track, correct any errors, and add anything that was missed to bring us to completion."* Brief: [M05](../../planning/m05-whole-project-review.md). The manager adds "Manager verification of M05", with a disposition for each finding, when it integrates this branch.

## 1. Identity

- **Prompt:** revision 1, at commit `f669f37f2ba52033ef0410c00c7f40ba234a5d7c` of the manager branch `claude/magical-wozniak-yfmmx2` ([prompt](../../ephemeral/2026-10-25-m05-project-review-prompt.md)).
- **Session branch:** `claude/zen-thompson-5fdqqz`, set to `f669f37` before the first commit. Its final head is given in the report Nathan relays (commits: section 11).
- **Date:** 26 October 2026 (UTC). Environment: `Glow App - No Stream`, as the prompt named.
- **Environment check (names only):** none of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` is set (the loop printed nothing); `compgen -e | grep -E '^STREAM_'` printed nothing (exit 1). Toolchain in `$HOME/.local/bin`: `node` v24.19.0, `npm` 11.9.0, `python3.12` 3.12.14; `/usr/bin/python3` is 3.13.17. Every command ran in `env -i PATH="$HOME/.local/bin:$PATH" HOME="$HOME" LANG=C.UTF-8` plus its own variables; installs and `npm audit` got the proxy and CA variables by reference, never printed.
- **Start gate:** every check passed. `HEAD` = `f669f37f2ba52033ef0410c00c7f40ba234a5d7c`; `origin/main` = `5b9bcb1390a58420bef50f524934526d9c22325d`; the prompt's commit is on the live manager branch (whose head was `f669f37`); `main` is included; no non-Markdown path differs between `main` and `HEAD` or between `main` and the manager branch; no `.claude/` path; this record did not exist on the manager branch.
- **Classification of the reviewed tree** (trusted policy from `main`, `python3 -I`, full SHAs, `--merge-base`): `{"full": false, "reason": "ordinary-docs-only", "paths": [7 Markdown paths]}`, as expected. The review continued: its object is the repository at `f669f37`, not a pull request (OD-48; the prompt, section 2).
- **Classification of this review's own change:** section 10.

## 2. Verdict: at risk

What is built is sound and verified. Phases P00 to P05 and the P06 items P06.1, P06.DB and P06.2 are merged with evidence that matches the CI runs. Every protected boundary holds in the code: no HDE call, no database connection outside the CI proof, no served token, and no provider data in a render, a stored client state or a log. Every offline check passes at `HEAD`. No critical finding stands.

The project is at risk against PF01's completion (P12) for three reasons:

1. **The plan does not place the largest remaining build.** The production HTTP API, real authentication and the persistence adapters for every domain but chat have no phase before P10/P11 (finding 1).
2. **Completion's external gates are open, undated and in some cases unowned.** These are the HDE contract (A01; no delivery date), the budget for accounts and hosting against a $0 budget, the Stream Maker application (pending for 31 days with no update), the store and legal requirements, and launch geography (A05). The store and legal requirements are where R05's early mitigation was never done.
3. **The measured process cost is high against what remains.** Since 25 September, 39,250 Markdown lines were added against 10,564 lines of application code and tests. Each merged P06 item took 0.5 to 16.5 calendar days. About 21 of the 31 days had no commits and no recorded cause.

Nothing contradicts the plan's direction or boundaries, so this is not "off track". But nineteen registered items remain (P06.3 to P12.2), plus the work this review adds, and no path past M04 is recorded (finding 51).

## 3. Status by phase

The claimed states are from the Notion Work Register (read on 26 October 2026) and the current handoff. The verified states are from Git (`origin/main` first-parent history), the evidence records and CI.

| Phase or item | Claimed (where) | Verified (evidence) | What remains |
|---|---|---|---|
| P00 | Done (Register P00.1–P00.3) | PF00/PF01 at `ac38e58` and the direct commits of 23 September; `authority-transfer.md` | — (Register evidence still links Google Drive and Notion pages: finding 8) |
| P01 | Done (P01.1–P01.3) | PR1 `2785bb5`, run 35856228910 success; ADR 0001; `foundation-checkpoint.md` | — |
| P02 | Done (P02.1–P02.3) | PR2–PR3; `p02-checkpoint.md`, `contract-baseline.md`; 39 contract Python tests and 586 contract JS tests pass at `HEAD` | Deferred cases in the P11 plan |
| P03 | Done (P03.1–P03.3) | PR4; `p03-checkpoint.md`; the artifact job's container smoke passed in run 40243775584 | Provisioning is P11 |
| P04 | Done, fixture scope (P04.1–P04.3) | PR5–PR9; P04 checkpoints; 621 mobile unit tests and 97 rendered tests pass | N01, PV04 and DB09 in the P11 plan; real auth and media have no build phase (finding 1) |
| P05 | Done, fixture scope (P05.1–P05.3) | PR10–PR14; P05 checkpoints | DB05, DB10 and DB11 in the P11 plan; A05 policies provisional (finding 6) |
| M01 | Done | PR15–PR16; `migration-publication.md` | — |
| M02 | Done | PR18 `2b6c7df`, push run 36075413521 success | The Setup-script and pin-test hardening, a recorded follow-up for 31 days (finding 13) |
| M03 | Done (Notion only) | No repository record names M03 | Record it, or mark the row as Notion-only (finding 8) |
| P06.1 | Done (`47db18d`) | PR27, second parent `c57de50`, trees equal; PR run 36510118431 and push run 36511117659 success; 4,804-line evidence record | Carried items in the P11 plan; Video/Feeds question (finding 33) |
| P06.DB | Done (`3afffb3`) | PR28; runs 36520940933, 36534514283 (labelled `cancelled`, explained) and 37262466651 success; DB06/DB09 figures match the logs | DB06/DB09 rerun on the real target (P11) |
| P06.2 | Done, Stages A–C2 | PR29 `02072f4`, PR30 `3272eed`, PR31 `3572c41`, PR32 `a8e9528`, PR33 `5b9bcb1`: each second parent is the PR head, each tree equal. Runs of record 37383940454, 37410705342, 39971426724, 40064952123 and 40135312825 success; PR33's PR run 40242922187 and `main`'s push run 40243775584 success | The history read's provider half is unproven live; nothing is served; P11 entries (some were missing: finding 33) |
| P06.3 | Planned (Register); absent from the handoff | No brief, no routing entry, not resumed (OD-05; OD-38 resumed only P06.2) | **Phase P06 is not complete** (finding 7) |
| P07–P10 | Planned (Register rows P07.1–P10.2) | Nothing built; no briefs | All (section 7) |
| P11 | Planned (P11.1–P11.5) | The P11 plan holds DB01–DB13, PV01–PV08, PR01, N01 and R01. DB06 and DB09 are partly evidenced in CI | All live integration |
| P12 | Planned (P12.1–P12.2) | — | All |
| M04 | Ready (Register); waits (handoff) | No brief; OD-39 of 5 October. Nathan has since deleted the eight merged branches by hand (`git ls-remote`: three heads remain) | Brief, Dev Manager read, implementation, review (section 7) |
| M05 | In progress (Register) | This record | The manager's verification and dispositions |

**Claimed and not shown:** nothing. Every "done" claim has its merge and evidence.

**Done and not recorded:**
- the deletion of the eight branches (the handoff still lists them for deletion: finding 9);
- M03, which only Notion records;
- the current advisory picture (finding 29).

## 4. Findings

Severity: **critical** means a protected boundary or a security requirement is broken, or a claimed result is false. **Major** means it blocks or endangers completion, or a record misleads a decision. **Minor** means wrong, but contained. **Nit** is a small point.

"Corrected" means changed on this branch in commit `300a24d`, marked in the text. "Proposed" means exact text in section 8. "Work item" means a recommended item for the manager to brief.

**Totals:** 0 critical, 11 major, 35 minor, 5 nit.

### A. The plan

1. **Major — the production server build has no phase.**
   - **Location:** PF01 §8 (P04–P08 "fixture/sandbox-backed behavior"; P10 "finalize adapter wiring"; P11A "exercise ORM/auth/repository conformance").
   - **Evidence:**
     - `services/api/glow_api/urls.py` serves `health/live`, `health/ready` and, in development and test, one synthetic route.
     - Only chat has an ORM adapter: `grep -rln "objects\.|select_for_update|transaction.atomic"` finds only `glow_chat/{contact,reads,delivery}.py` and one test.
     - Nothing builds django-allauth headless, the mail adapter, the F01–F20 HTTP views and permissions, or the ORM repositories for onboarding, profiles, media, eligibility, discovery, interactions, safety and privacy.
   - **Effect:** P11 would become a build phase, and R01 (late persistence defects) would land last, against PF01 §1's model of P11 as integration.
   - **Outcome:** proposed PF01 amendment (P-1); Nathan's decision N1.
2. **Major — the store, legal and safety requirements matrix does not exist.**
   - **Location:** PF01 §7, "Mobile/store readiness" ("Maintain a dated requirements matrix…"); R05's early mitigation ("Build policy/UGC/deletion/support matrix early").
   - **Evidence:** no such matrix anywhere (`grep` for CSAE, Data Safety, privacy manifest, age rating, requirements matrix finds only PF01 and the 23 September research snapshot); the only placement is P09's documentation.
   - **Effect:** P06.3, P07 and P08 would be designed without it. Store-mandated features include Google Play's child-safety standards for dating apps, in-app account deletion, report/block/contact, age rating, privacy labels and Sign in with Apple when other social login is offered, so missing them means rework.
   - **Outcome:** proposed work item (missed item E2); PF01 text (P-2); decision N3.
3. **Major — completion's costs meet a $0 budget with no consolidated gate.**
   - **Location:** PF01 A04; OD-12 ($0 budget, for Stream); OD-24 (no paid GitHub plan).
   - **Evidence:** completion needs at least the following:
     - Apple and Google developer accounts for signed builds (N01; P09.2);
     - app services on Railway for staging and production (P11B/C);
     - a production Stream plan;
     - Cloudflare Images/R2;
     - a mail provider.
   - The Stream Maker application (OD-22) was submitted by 25 September with "about two weeks" estimated. No record mentions it after 28 September (31 days).
   - **Outcome:** proposed A04 text (P-3); decision N2.
4. **Minor — statements in PF01 that later directions superseded.**
   - D05 "one capable session" (superseded by D09 and D10).
   - D08's state cell "current controlling permission record", naming App Builder 1 and App Planner 1, which are historical (OD-01).
   - §7 "Test in-flight messages, stale tokens…".
   - §8 P06 "token lifecycle" and its validation's "direct SDK send restrictions, stale tokens", still in the body though revision 1.12 says they no longer apply to the app.
   - §2's repository-locations table omits `proofs/`.
   - D10 lacks its OD-35 pointer, which DM-09 2(b) asked for at the next change; PF01 changed twice afterwards without it.
   - **Outcome:** proposed (P-4).
5. **Minor — phase acceptance that a session cannot check.**
   - P06: "a credible tested provider-level safety path"; P06.3 has no acceptance of its own.
   - P07: "workflows and staff UI are demonstrable", with "a disposable WordPress environment if available".
   - P09: "justified scoped deferrals", and native builds "when signing access permits".
   - P10: "no unexplained blockers".
   - **Outcome:** proposed (P-5).
6. **Minor — A05 questions accumulate with no decision point.**
   - **Location:** PF01 A05, "P05/P07/P08 before final policy/launch".
   - **Evidence:** open, each with provisional fixtures:
     - launch geography and language;
     - the preference and age-range taxonomy (`demo_a`/`demo_b`, P11 plan);
     - resurfacing and rematch;
     - the history-read policy (DM-22 3.1, P11 plan);
     - retention;
     - moderation operators.
   - The adults-only rule rests on a self-entered birth date in the fixture, and no record decides how age is assured.
   - **Outcome:** proposed A05 text (P-6); decision N4.

### B. Status

7. **Major — phase P06 is not complete, and P06.3 is not routed.**
   - **Evidence:**
     - P06.3 (notifications) has no brief.
     - The handoff's next actions are M05, then M04, then nothing.
     - P06.3 is not resumed (OD-05; OD-38 resumed only P06.2).
     - P06.2's design relies on P06.3 for background delivery: "nothing polls in the background until P06.3's push" (the P11 plan, PV03).
     - Real push needs an EAS project and APNs/FCM credentials, which the mobile release block forbids until Nathan authorizes release work (`apps/mobile/AGENTS.md`).
   - **Outcome:** decision N5; path in section 7.
8. **Minor — M03 and Register evidence links.**
   - M03 is Done only in Notion.
   - The Register's P00.1 and P00.2 evidence links a Google Drive file; P00.3, P01.1, A03, P05.1 and P05.3 link Notion pages or the legacy repository.
   - **Outcome:** proposed Notion changes (section 9).
9. **Minor — the handoff's branch list and waiting checkpoint are stale.** `git ls-remote --heads origin` on 26 October shows three heads (`main` `5b9bcb1`, the manager branch `f669f37`, `claude/dev-manager` `6bf6f5d`). The eight branches the handoff lists "for Nathan to delete" are gone. **Outcome:** proposed (P-15).

### C. Code, tests and CI

10. **Minor — cancel-in-progress does not cancel the jobs, and two governing texts say it does.**
    - **Location:** `.github/workflows/foundation.yml` (`concurrency` with `always()` on every application job); CI policy, the push-run paragraph; manager workflow step 5, "Push runs as evidence".
    - **Evidence:** run 40162341984 (PR33's head `9776c6f`) reads `cancelled`, yet all eight jobs are `success` and the gate succeeded. I read this myself with `get_workflow_run` and `list_workflow_jobs`. Superseded full runs therefore run to completion and delay the newest one.
    - **Outcome:** proposed text (P-9, P-7); work item, in M04: `!cancelled() && (…)` on the application jobs.
11. **Minor — the Mobile job has little margin.** It took 6 min 24 s of its 15 in run 40243775584 (rendered suite 4.8 min, 97 tests). Run 40029112295's 11 min 27 s Chromium install would still time it out. A recorded follow-up already holds this. **Outcome:** work item, in M04.
12. **Minor — a latent classifier bypass through submodule settings.**
    - **Location:** `scripts/change_scope.py:40`, whose `git diff` call omits `--ignore-submodules=none`.
    - **Evidence:** in a throwaway repository whose trusted base `.gitmodules` sets `ignore = all`, a gitlink move plus a docs edit classified `ordinary-docs-only`.
    - It is latent: the repository has no `.gitmodules`, and adding one is full scope.
    - **Outcome:** work item (full scope; classify with the pre-change policy).
13. **Minor — the pin test does not read `proofs/stream-chat/package.json`.**
    - **Location:** `services/api/tests/test_toolchain_pins.py:14`.
    - **Evidence:** a scratch reversal set that file's Node and npm pins to 24.18.0/11.8.0, and the test still passed; the same change in `apps/mobile/package.json` failed it.
    - `local-development.md` claimed full coverage.
    - **Outcome:** corrected (`local-development.md`); work item (the test and `scripts/bootstrap-toolchain.sh`'s "both package.json files").
14. **Minor — the CI policy's Database proof checks description and its upload-artifact row are stale.**
    - The workflow also runs the `dbshell` refusal, both subjects, the delivery and read phases, and the used-database refusal.
    - `upload-artifact` `ea165f8` is v4.6.2 (resolved with `git ls-remote`); v7.0.2 is current.
    - **Outcome:** proposed (P-9).
15. **Nit — CI and classifier hardening.**
    - The rename test passes for the wrong reason (reversal R6: the parser crashes, so the change is still full).
    - A PR whose base is not `main` would load the policy from that branch (latent).
    - `.github/agents/*.agent.md`, `.cursor/` rules and `copilot-instructions.md` classify as documentation.
    - Uploads use `if-no-files-found: ignore`.
    - No test ties `dependency-inventory.json` to the locks; they match today.
    - CI's `npm install --global npm@11.9.0` and the Playwright download are not integrity-pinned.
    - The offline guards are uneven: no socket guard in the PostgreSQL tests, and `run_plan.py` runs outside `env -i` in CI.
    - **Outcome:** optional work items.
16. **Minor — the local checks differ from CI.** `local-development.md` lists `glow_persistence.static_check`, which is not a CI step: its `inspect_definitions()` runs inside `tests/test_model_definitions.py`. It also omits the proofs' checks, which CI runs as two jobs. **Outcome:** corrected (`local-development.md`).
17. **Minor — the mobile release guards are only partly tested.** Reversals in a scratch copy:
    - removing `!__DEV__` from `src/app/_layout.tsx:58` failed no test (621/621 passed; nothing imports the layout);
    - turning `app.config.ts:15`'s allow-list into a deny-list of `production` failed no test (`scripts/build-guard.test.mjs` probes only `production`), so `staging`, `preview` and unset are accepted;
    - an `EXPO_PUBLIC_GLOW_STREAM_TOKEN` name passing a prefix rule failed no test.
    - I confirmed by `grep` that no test file imports `_layout`.
    - **Outcome:** work item (mobile hardening).
18. **Minor — the display rule's client-side tests have gaps.** In scratch reversals:
    - a `console.info` of message texts in `store.ts` passed all 105 chat tests and lint (`eslint.config.mjs` has no `no-console`);
    - a render of a provider-shaped `name` field in `screen.tsx` passed tsc, lint and the suite, because the render rule rests on the client validator alone;
    - copy naming "Stream" in `READ_COPY.unavailable` and `temporary` passed (`display-rule.test.ts:39` checks only `invalid_response`);
    - deleting the list clear on an account change (`store.ts:189`) passed.
    - **Outcome:** work item (mobile hardening).
19. **Minor — provider wording outside chat (ADR 0003, decision 3).** These are development-preview disclaimers, but they sit in ordinary member screens:
    - `src/interactions/screen.tsx:76`: "This preview has no provider channel…";
    - `src/app/media.tsx:91`: "Synthetic provider purge confirmed.";
    - `src/app/media.tsx:100`;
    - `src/app/verify.tsx:12`: "using the maintained account provider".
    - **Outcome:** work item (a copy pass).
20. **Nit — mobile README and dead code.**
    - `src/hooks/use-recommendations.ts` has had no importer since P05.2.
    - `apps/mobile/README.md:18` and `:24` describe the development origin as changing a screen; `:440` says "There is no network client"; the last sentence names only C2 and C2-C1.
    - `ConversationSummary.state: 'closed'` renders as an openable row.
    - **Outcome:** proposed README text (P-13); work item.
21. **Minor — the mobile store's revoked state flips to `loading` during a re-read.** Confirmed by probe test: the published statuses run `loading`, `loading`, `revoked`, `revoked`, with a live composer in the window. This is already the P11 plan's C2C2-X1 entry, so it needs no new home. **Outcome:** none; recorded here as confirmed.
22. **Minor — the API's refusal list is narrower than ADR 0004 says.**
    - **Location:** `glow_api/configuration_profiles.py:24-48`; ADR 0004:34 ("refuse every database connection name").
    - **Evidence:** I ran `load_configuration({'GLOW_ENV':'test', NAME:'x'})` myself. It accepted `DATABASE_PUBLIC_URL`, `PGPASSFILE`, `PGSERVICE`, `POSTGRES_PASSWORD`, `REDIS_PUBLIC_URL`, `REDISPASSWORD` and `STREAM_API_SECRET`, and refused `DATABASE_URL`.
    - The effect is contained: the dummy backend and the driver-less image cannot connect.
    - **Outcome:** inventory note added; ADR text proposed (P-12); work item (a `PG*` prefix rule and the Railway, Redis and `STREAM_*` names, in the API and the proof together).
23. **Minor — the message spool keeps every message body.**
    - **Location:** `glow_persistence/models.py:557` (comment: "removed after receipt/expiry per approved policy"); `glow_chat/delivery.py`, `accepted()` (it updates `state` and `version` only).
    - **Evidence:** no code clears `MessageSubmission.text`, so Glow's database keeps a copy of every accepted message. `privacy-and-safety-rules.md` classed message bodies as provider-managed. Nothing is served yet.
    - **Outcome:** P11 plan item and privacy row added; work item (clear on receipt, or a recorded retention decision).
24. **Minor — the dormant token code has no cleanup item, and records describe it as P11's.**
    - **Location:** `data-model.md:281-283`; `glow_domain/chat.py:175`; `chat_tokens.py:9-12`; `services/api/README.md:58-59` and `:78-90`.
    - **Evidence:** all say P11 serves the endpoint, against OD-45 and the P06.2 brief's point h. `session_epoch_bumped` still drives a provider token revocation (`events.py:38`, `delivery.py:361-381`).
    - **Outcome:** data model corrected; README proposed (P-13); work item (the OD-45 token cleanup).
25. **Minor — three `glow_chat` revocation checks no test can fail.**
    - **Location:** `contact.py:490-498`, `reads.py:289-290`, `delivery.py:265`.
    - **Evidence:** reversals R7, R26 and R14 were not caught. They are unreachable through the adapter's own writers, because a block restricts the match, but become reachable once P07 or WordPress adds a second block writer.
    - **Outcome:** work item (a proof case with a direct block row), before P07's block writer.
26. **Minor — the data model claimed a contact-version recheck at dispatch.** `data-model.md:135` said so; `glow_chat/delivery.py` compares no contact version, by design (D6). **Outcome:** corrected.
27. **Nit — redundant checks and unused code in discovery.**
    - The Python discovery queue lifetime is not separately observable (reversal R25 not caught).
    - Two redundant rechecks are untested (`discovery.py:469`, `provider_fixtures.py:403-405`).
    - `MAX_QUEUES` is unused.
    - **Outcome:** `discovery-fixtures.md` corrected; optional work item.
28. **Nit — two stale API descriptions.** `domain-and-data-boundaries.md:37` said "Current development has no domain persistence". The API README omits Stage C1 and OD-45. **Outcome:** corrected / proposed (P-13).
29. **Major — the advisory picture is worse than any record says.**
    - **Evidence:** `npm audit --json` at `HEAD` (npm counts vulnerable packages):
      - `apps/mobile`: 14, of which 1 critical (`shell-quote` 1.10.0, GHSA-pqg4-j6r4-53mv, through `react-native` → `react-devtools-core`), 6 high (`expo`, `@expo/cli`, `@expo/code-signing-certificates`, `node-forge` GHSA-86w9-cpqp-85rv, `source-map-js` GHSA-68fv-2mgg-jv7q, `zod` GHSA-mrhx-c7xc-m3w5) and 7 moderate;
      - `packages/contracts`: 1 moderate (`fast-uri`, through `ajv`);
      - `proofs/stream-chat`: 1 high (`follow-redirects`, recorded).
    - The records say otherwise. The State of the App says "14 moderate … none high or critical"; C2's record says "advisories as before; no change", with no counts, against DM-02 B9.
    - npm's suggested fixes include `expo-router@58`, so remediation likely means an Expo SDK upgrade, which no item plans. The critical and most high advisories are in development and build tooling.
    - **Outcome:** annotation added to the P06.2 evidence record; work item (dependency remediation and SDK assessment, before P09); proposed State of the App text at its refresh.

### D. The records

30. **Major — Notion's Implementation Control misleads.** Its lead paragraph is current, but six standing bullets are stale:
    - "Manager: App Manager 7";
    - "Dev Manager: Dev Manager 2";
    - "Main is `3272eed`", with PR31 as the open draft;
    - the branch list at `a8e9528`;
    - the mistakes list;
    - "M03 complete".
    - Its operating procedure is stamped `51844a5` (23 October), not `f669f37`, and omits rules: more than one merge base, workflow-change rules, the Notion checklist, and more.
    - I confirmed three of these strings myself in the fetched page. The match check the workflow requires at every records batch did not catch them.
    - **Outcome:** section 9.
31. **Major — standing process rules live only in P06.2's records.**
    - AM7-13 and DM-28 2.4 (wait for Codex's pass before a review prompt), DM-30 4.2 and 4.3 (a pass with no result is incomplete; the checklist names the PR run) with AM8-10, and AM8-01 (list the review threads at the start).
    - They are in the P06.2 brief (`:831`, `:872`), the archived handoff and PR33's body. They are not in workflow steps 6 and 7 or the start procedure. M04, a full-scope workflow change, would run without them.
    - **Outcome:** proposed (P-7, P-8).
32. **Major — the start procedure routes a hand-started successor to stale records.**
    - **Location:** `start-prompts/next-manager.md:36` and `:39` ("If a manager PR is open … otherwise read from `main`").
    - **Evidence:** no PR is open, and `main`'s handoff reads "P06.2; DM-30 answered; PR33's close under way". `main` has no M05 brief and no OD-48 (checked with `git show origin/main:…`).
    - **Outcome:** proposed (P-8).
33. **Major — items carried to P11 had no home in the P11 plan.** Missing were:
    - chat dead-letter reconciliation (the data model pointed at DB06 and DB09, which do not hold it);
    - the provider name at startup (B1-C1 R3);
    - the activation P11 wires (CX5);
    - how the runtime builds the Stream client, and the pin's move;
    - the Video/Feeds production decision (DM-07 4(b); P06.2 D9's "P09 or P11");
    - "a user Stream does not have", never shown live;
    - the fixture `already`;
    - the message spool (23);
    - the standing `stale_version` guard, which lived only in the handoff.
    - **Outcome:** corrected (P11 plan, "Items carried to P11 without an entry here until M05").
34. **Minor — stale entries in the P11 plan.**
    - DB09's CX2 "carried to P06.2" and "above": Stage A settled it.
    - Stage A's F1 "P11's endpoint must close it": closed in B1, and moot under OD-45.
    - "stays with P06.2 and P11".
    - PV03 has no note that P06.1 is done or of OD-45.
    - P05.3's "P06.1 must establish…".
    - **Outcome:** corrected.
35. **Minor — stale living statements in `docs/operations/`.**
    - `migration-plan.md:3-4`: no migration applied, though they run in every full-scope CI run.
    - `environment-inventory.md`: `:14` (a check "in the current handoff"); `:27` and `:118` (the loader adopts `STREAM_*` in P06.2; it never did); `:32` (pricing "until P06.1-I2").
    - `providers-and-webhooks.md:15` (Stream "conditional … no SDK account connection").
    - `environments.md:22`, `:74` and `:79` (App Builder 1 as a current role; the 23 September audit as not yet run).
    - `operational-runbooks.md:15-16`; `configuration.md:94`.
    - `local-development.md:24` (`python3` 3.11; it is 3.13.17) and `:141` (Chromium 1194; it is 1243, while Playwright expects 1234).
    - **Outcome:** corrected.
36. **Minor — stale statements in briefs.**
    - `claude-setup-optimization.md:49` (all sessions in `Glow app`, against OD-36).
    - `database-audit-2026-09-23.md` (same-logical-database outcome with no supersession note, against OD-18).
    - `claude-code-migration.md:11` and `:32` (the inventory "in the handoff").
    - The P06.2 brief: no "done" status, "20 minutes today" and "Work Register: Ready".
    - The P06.DB brief's P11-plan line pointers.
    - **Outcome:** corrected.
37. **Minor — stale architecture text.** `interactions-fixtures.md:242-243` listed Stages B and C as later work. `onboarding-fixtures.md`'s route table listed only P04.1's routes, against `routes.ts`'s 20. **Outcome:** corrected.
38. **Minor — the handoff is twice its size limit, and it is the only home of gated items.**
    - It is 10,905 bytes against `docs/README.md`'s "kept under 5 KB" (DM-01 P3, accepted); it was last under at `2542a06` on 23 October.
    - Its "Recorded follow-ups" paragraph (about 3,950 characters) is the only home of:
      - the window-replacement follow-up (DM-29 1.1);
      - the Mobile job margin;
      - `read_phase.py`'s N2 and N3;
      - uv;
      - the fixture `already` (now also in the P11 plan);
      - the guard (now also in the P11 plan).
    - **Outcome:** proposed (P-15).
39. **Minor — register rows not current.**
    - OD-10: the ten-session comparison no longer exists after OD-34 dropped the outcome column.
    - OD-30 and OD-33 are not marked as updated by OD-34 and OD-42.
    - OD-38 does not record P06.2 as done.
    - OD-39 is not marked for OD-48.
    - OD-44 says "DM-17 is in flight".
    - OD-31 names `claude/stoic-carson-66gdig` and PR26 as current.
    - **Outcome:** proposed (P-10).
40. **Minor — request v6 named as in force.** `reasoning-level-matrix.md:3` ("the request in force (v6…)"), `docs/README.md:30` and `next-manager.md:61` contradict workflow step 3 and OD-42: v8.2 in the installed skill is the authority. **Outcome:** proposed (P-8, P-11).
41. **Minor — recorded preventions not applied.** About 25 entries' preventions appear in no procedure. Among them:
    - AM7-13, AM8-01, AM8-10 (finding 31);
    - AM7-11 ("read the follow-ups due before a stage's first prompt");
    - AM7-07 (list branches at each integration);
    - AM4-05 (read the start text before a handover commit);
    - AM5-09/AM8-07 (whole-page Notion readback);
    - the claims chain AM7-08 → AM7-10 → AM8-03 → AM8-06 and AM8-04/AM8-08, which DM-01 P8 ("a repeated prevention moves into a checklist") required to become a checklist.
    - **Outcome:** proposed claims checklist (P-7).
42. **Minor — Dev Manager dispositions not applied.**
    - DM-01 P3's PR-to-work-item index: never built, with no note.
    - DM-03 E3 and DM-07 item 7: the Dev Manager start prompt was made generic at `2ef4b1b`, 20 minutes after Dev Manager 3 started, and the review log's "Still open" (`README.md:207`) was never closed.
    - DM-09 2(b): the No Stream Setup script in the inventory, the OD-35 pointer in PF01 D10 and `CLAUDE.md`'s environment phrase, missed at later changes to both files.
    - DM-02 A4/B5 and DM-07 item 5: items carried to P07 have no persistent home.
    - DM-13's row in the review log has no OD-45 pointer.
    - **Outcome:** observation added to the inventory (No Stream toolchain verified in this session); the rest proposed (P-4, P-17, P-18); missed item E12.
43. **Minor — frozen records with no out-of-date notes.** `claude-code-handoff.md` has a code map that predates P06, and its `:89` "No Stream dependency is present in the committed mobile/API locks" is false (`requirements-dev.lock:287`). `state-of-the-app.md` (25 September; "P06.1 In progress") has no note either, and the start procedure and the M05 brief route readers to both. **Outcome:** proposed (P-16).
44. **Minor — ephemeral pruning is overdue.**
    - Every prompt in `docs/ephemeral/` but this review's has met its deletion condition (84 files across P06.1, P06.DB and P06.2's stages).
    - 226 incoming links in 23 files are not commit-pinned.
    - OD-45's link to the D8 message must be pinned first, since that message is the only text of the options Nathan answered.
    - The handoff schedules pruning only for P06.1 and P06.DB.
    - **Outcome:** work item (a pruning batch in the manager's records).
45. **Minor — the HDE contract request misses questions the app now needs answered:**
    - change and deletion notification, and its authentication;
    - export of what HDE holds about a user (PV07);
    - deletion idempotency, and backup restore on either side (DB13);
    - consent withdrawal;
    - data residency and processor role;
    - the deployment identity per environment (PF01 §5's "HDE commit/deployment").
    - **Outcome:** proposed C30–C35 (P-14).
46. **Minor — the environment inventory, "the one living home", omitted the proof's `PROOF_DB_*` names.** **Outcome:** corrected (added).
47. **Nit — labels and supersession notes.** The P06.2 evidence record calls run 40057495942 "PR31's run of record"; it is PR31's final-head PR run. The P03, P04.1 and P05.1 checkpoints state the same-logical-database preference with no supersession note. **Outcome:** annotated.
48. **Minor — the TypeSafe uses table is not kept as the workflow says.** Nathan's pick is recorded for 1 of 18 Glow prompts since Stage C1. Withdrawn or superseded rows read "pending". Three corrections are labelled "implementation". There is no row for App Manager 8's creation. Four rows belong to other projects. **Outcome:** decision for Nathan inside N6 (keep the pick column or drop it); Notion (section 9).

### F. The process

49. **Major — the records burden is out of proportion and produces most mistakes.**
    - Since 25 September: +39,250 Markdown lines against +10,564 application code and test lines (3.7 to 1).
    - Managers and Dev Managers made 248 records commits against 58 implementation commits that touch code (4.3 to 1).
    - The handoff changed in 174 of 206 manager records commits.
    - 57 of the 92 logged mistakes are of the "accuracy" kind.
    - Stage C2 took 8 Dev Manager consultations, 27 manager records commits and 11 Dev Manager commits for 1,458 non-test lines.
    - There were seven App Managers and three Dev Managers in 32 days.
    - **Outcome:** section 6 and proposed text (P-7, P-19).
50. **Minor — waiting is unmeasured.** About 21 of 31 days had no commits, in two gaps of 4.9 days (29 September to 4 October) and 16.0 days (6 to 22 October). No record says why. PF01 §11 asks to keep hands-on effort apart from external waiting. **Outcome:** proposed waiting-checkpoint field (P-7).

### G. The path

51. **Major — no path to P12 is recorded past M04.** No item after M04 is routed. No brief exists for P06.3 or P07. None of the gates in findings 1, 2, 3 and 6 has been put to Nathan in OD-32's form. **Outcome:** section 7.

## 5. Missed items (section 4, E)

Each item: what it is, and why completion needs it; its home; its owner; and whether I added it or propose it.

| # | Item, and why completion needs it | Proposed home | Owner | Added or proposed |
|---|---|---|---|---|
| E1 | **The production server slices.** The HTTP API for F01–F20, django-allauth headless with a mail adapter, and ORM repositories for each domain, each proven on disposable PostgreSQL in CI as P06.2 Stage A did for chat (finding 1). Without them P11 is a build phase | PF01 §8 amendment; new items S1–S4 (section 7) | Nathan decides (N1); then implementation sessions | Proposed |
| E2 | **The store, legal and safety requirements matrix.** A dated Apple/Google matrix for a dating app. It covers UGC moderation and report/block/contact, Google Play's child-safety standards for dating apps (a published standards page and a contact), in-app and web account deletion, age rating and age assurance, privacy labels and Data Safety, Sign in with Apple when other social login is offered, permissions, subscriptions and reviewer access (PF01 §7; R05) | New item before P06.3 and P07 (proposed ID P09.3a) | An implementation session researches; Nathan decides scope (N3) | Proposed |
| E3 | **A costed list of completion's accounts and services, and the budget decision.** Apple Developer Program, Google Play developer account, Railway app services, Stream production plan (Maker status), Cloudflare, mail, push (finding 3) | PF01 A04; a short planning note | Manager prepares; Nathan decides (N2) | Proposed |
| E4 | **Launch geography and the age-assurance approach (A05).** These decide the legal obligations (age assurance, data protection, deletion) the matrix lists (finding 6) | PF01 A05; decided before P07's brief | Nathan (N4) | Proposed |
| E5 | **P06.3's brief.** Glow-server notification policy, privacy-safe content (ADR 0003: never Stream's push), user preferences and device-token lifecycle at fixture scope. Real push transport waits on an EAS project and credentials (release block), carried to P09/P11 (finding 7) | P06.3 brief | Manager; Nathan resumes (N5) | Proposed |
| E6 | **CSAM detection and reporting for photo uploads.** A photo-UGC dating app needs detection and a reporting duty (for example, the US NCMEC reporting duty on providers that become aware, and Google Play's child-safety policy), plus a named path for one operator (OD-23). PF01 §7 names child-safety duties, but no item or provider choice holds detection | E2's matrix, then P07.1 and PV04 | Nathan (operator duty); P07 | Proposed |
| E7 | **The OD-45 token cleanup.** Remove or seal `grant_token`, `grant_chat_token`, `sign_chat_token` and the `pyjwt` pin; decide whether an epoch bump still revokes provider tokens; correct the docstrings and the API README (finding 24) | A work item before P11 | Implementation session | Proposed |
| E8 | **Dependency remediation.** Assess the critical and high advisories and the Expo SDK upgrade; record counts per DM-02 B9 (finding 29) | A work item before P09 (or within P09.1) | Implementation session | Proposed |
| E9 | **The message spool's retention** (finding 23) | The P11 plan; P08.1 | P08; Nathan for retention (A05) | Added to the P11 plan and the privacy rules |
| E10 | **P11 items without a home:** reconciliation, provider name at startup, activation, client construction, Video/Feeds decision, absent-user row, fixture `already`, the guard (finding 33) | The P11 plan | P11 | Added |
| E11 | **Mobile hardening:** release-guard tests, `no-console`, the copy test over every copy table, the list-clear test, the provider wording outside chat, plus the handoff's recorded mobile follow-ups (DM-29 1.1, draft restore, the `match-conversation` assertion) (findings 17–20) | One work item at the next `apps/mobile` change, before P06.3's UI | Implementation session | Proposed |
| E12 | **Items carried to P07:** DM-02 A4's WordPress safeguards; DM-07 item 5's Stream terms §6.2; the history-read policy question (DM-22 3.1); the second block writer's proof case (finding 25); ADR 0003 condition (b) (deletion and export include member custom data) | The P07 brief, "Carried to P07", when written | Manager | Proposed |
| E13 | **The Stream Maker status.** Nathan checks the application (pending since 25 September) | A04 | Nathan | Proposed (inside N2) |
| E14 | **The HDE contract request's missing questions** (finding 45) | The HDE contract request | Manager drafts; Nathan's HDE process | Proposed |
| E15 | **The API and proof refusal lists** (finding 22) and **the classifier's submodule flag** (finding 12) | M04, or the CI hardening below | Implementation session | Proposed |

## 6. The process

### 6.1 Measured (from Git and the records; method below)

| Item | Start → merge | Calendar days | Active days (commit-hours) | Implementation passes | Correction passes | Exact-head reviews (first + re-reviews) | Dev Manager consultations | Codex findings | Manager records commits |
|---|---|---|---|---|---|---|---|---|---|
| M02 | 24 Sep 15:17 → 23:59 | 0.4 | 1 (8) | 1 | 1 | 2 (1+1) | — | 1 P2, after the merge | 9 (+5 close-out) |
| P06.1 | 25 Sep 01:41 → 29 Sep 02:07 | 4.0 | 5 (53) | 3, plus the flake fix and 2 read-only discoveries | 5 | 9 (4+5) | DM-03 to DM-07 | 0 | 80 |
| P06.DB | 29 Sep → 5 Oct 13:20 | 6.5 | 3 (16) | 1 | 2, plus a duplicate C1 never integrated (AM5-15) | 3 (1+2) | DM-08 to DM-12 | CX1 P2, CX2 P2, CX3 P1 | 23 |
| P06.2 A | 5 Oct → 6 Oct 01:51 | 0.5 | 2 (9) | 1 | 0 | 1 | DM-13, DM-14 | CX4–CX6, P1 | 16 |
| P06.2 B1 | 6 Oct → 22 Oct 14:19 | 16.5 | 2 (9) | 1 | 1 | 2 (1+1) | DM-15 | 0 | 12 |
| P06.2 B2 | 22 Oct → 24 Oct 03:22 | 1.5 | 3 (17) | 1 | 5 | 3 (1+2) | DM-16 to DM-21 | CX7 P2 | 28 |
| P06.2 C1 | 24 Oct 03:24 → 20:48 | 0.7 | 1 (9) | 1 | 2 | 3 (1+2) | DM-22 | 0 | 13 |
| P06.2 C2 | 24 Oct 20:55 → 25 Oct 23:13 | 1.1 | 2 (16) | 1 | 4 | 3 (1+2; 2 more prompts withdrawn) | DM-23 to DM-30 | CX8–CX12, P2 | 27 |
| **P06.2 total** | 5 → 25 Oct | 20.4 | 6 (56) | 5 | 12 | 12 | 18 | 9 | 96 |

- **Correction passes:** 19 integrated. 18 changed code or tests; one (B2-C3) changed only records in the repository, its work being a live configuration change.
- **What triggered them:** an exact-head review in 12, a Codex finding in 4 and Stream's unannounced changes in 3.
- **The late fixes were small:** B2-C4 63, B2-C5 22, C2-C2 53, C2-C3 14 and C2-C4 21 non-test lines. Each still needed a prompt, a Codex pass, Dev Manager reads and a re-review.
- **Exact-head reviews:** 24 ran. 15 found at least one should-fix or blocking code or test defect, 6 found code nits only, and 3 found record issues only.
- **Codex:** 13 findings (4 P1, 9 P2). All came after an exact-head review had run on that code. 6 were fixed before the merge and 7 carried forward. The GitHub threads for CX3, CX4–CX6 and CX7 are still unresolved.
- **Mistakes log:** 92 rows.

  | By manager | AM2 | AM3 | AM4 | AM5 | AM6 | AM7 | AM8 |
  |---|---|---|---|---|---|---|---|
  | Rows | 11 | 23 | 7 | 24 | 3 | 14 | 10 |

  - By the log's own kind: accuracy 57, process 15, follow-through 10, execution 9, and "scope" 1 (AM6-03, outside the log's four kinds).
  - By audit class:

    | Class | Rows |
    |---|---|
    | Records and wording | 23 |
    | Prompt, brief or consultation defects | 18 |
    | Notion | 15 |
    | Process departures | 12 |
    | Verification misses | 11 |
    | Wrong commands | 6 |
    | Dropped commitments | 4 |
    | Premature actions | 2 |
    | Tool or permission | 1 |

- **Volume:**
  - `docs/` grew from 12,670 to 50,230 Markdown lines between `2b6c7df` and `f669f37` (+39,250/−928, checked with `git diff --numstat`).
  - The application outside `proofs/` grew from 14,870 to 20,619 non-test lines and from 12,716 to 17,517 test lines.
  - `proofs/` holds 56% of all non-generated code and tests.
- **Time:** 12 of the 31 days from 25 September to 25 October have commits, across 125 clock hours. The two gaps (4.9 and 16.0 days) have no recorded cause.
- **Method:** a read-only subagent ran `git log --first-parent`, per-PR ranges classified by each commit's `Claude-Session` trailer, `git diff-tree` for Markdown-only commits, GitHub reads of PR18 and PR27–PR33, and the records' headings and verdicts. I re-checked the merge list, the Markdown growth and run 40162341984 myself. The review and verdict counts come from the evidence records alone, since review sessions push no commits.

### 6.2 Assessment

The layered review finds real defects. 18 of 19 correction passes changed code; 15 of 24 reviews found code or test defects; Codex found 13 more, all after an exact-head review. So the exact-head review plus Codex is worth keeping for full-scope code.

What is out of proportion is everything around it. Three causes stand out:

- **Fix-or-carry decisions go to the Dev Manager.** Stage C2's eight consultations were about findings of 14 to 63 lines.
- **Every step is recorded several times over.** The brief, the evidence record, the handoff, the register, Notion's status, Notion's procedure copy, the review log and the uses table each record it.
- **The handoff carries technical content.** It was meant to route only.

The records themselves generate most of the mistakes: 57 of the 92 are accuracy slips, mostly in records and Notion. The manager churn adds to this, each handover being another records batch.

Against what remains (P06.3, P07 to P12: 19 registered items plus E1, E2, E5, E7, E8 and E11), the observed rate cannot be extrapolated honestly into a date, and PF01 §11 forbids a calendar promise. Measured facts only:

- the three P06 items took 32 calendar days, 12 active days and about 125 commit-hours;
- about two thirds of the elapsed days were waiting with no recorded cause;
- the remaining items are larger in scope (WordPress, native builds, real auth, the live integrations);
- several wait on external gates with no date (HDE's contract, accounts, budget).

### 6.3 Proposals

Governing changes go to the Dev Manager first (OD-32; the charter); the text is in section 8.

| # | Proposal | Expected effect | Risk |
|---|---|---|---|
| K1 | **Keep** the exact-head review and Codex for full-scope code, the trusted classifier, one item at a time (OD-29), runs of record by ID | Defect discovery as now | — |
| S1 | **Decide fix-or-carry by rule, not by consultation.** Adopt DM-23's rule as standing: a defect in a stage's own code that misses an item of its prompt is fixed before the merge; one that needs P11's environment to show is carried to the P11 plan. The Dev Manager is consulted only on the charter's triggers (architecture, security boundary, governance, credential prompts) or when the rule does not decide | About 5 of Stage C2's 8 consultations would not have been needed | A borderline case decided by the manager alone; mitigated by the Dev Manager's pre-merge read |
| S2 | **Merge small fixes and their re-review.** A correction of 60 or fewer non-test lines that answers a review finding is re-reviewed by a delta review of its diff and the finding, in the same prompt cycle as Codex's pass, not by a new full exact-head review | Fewer prompt cycles per merge | A delta review misses an interaction; Codex still reads the final head |
| S3 | **Cap per-pass evidence.** Each pass's record keeps a fixed template of about 150 lines: identity, run of record, a checks table, deviations, and what the review must know. Review reports are linked, not copied | Slows the 3.7:1 Markdown growth | Less detail in the repository; the runs and reports keep it |
| S4 | **Enforce the handoff's 5 KB**, routing only; follow-ups go to their owning brief or the P11 plan at the moment they are recorded | Removes the most-edited file from most batches | None found |
| S5 | **Notion carries a summary and the commit stamp, not a full copy.** Implementation Control's procedure section becomes a short summary with links into the repository at the stamped commit; the register copy stays. This is Nathan's call (OD-26) | Removes the copy that drifted (finding 30) and one class of mistakes (15 rows) | Notion alone no longer holds the whole procedure, which OD-26 wanted |
| S6 | **Prune at the merge.** Each merge receipt commit-pins the item's ephemeral links and deletes its prompts | `docs/ephemeral/` stays small | A needed prompt pruned; mitigated by pinning |
| S7 | **One claims checklist** in the workflow for the repeated accuracy slips (finding 41), replacing the scattered preventions | Applies DM-01 P8 | — |
| S8 | **Waiting checkpoints name the cause and the owner** (finding 50), so PF01 §11's reforecast can separate hands-on time from waiting | A measurable reforecast | — |
| D1 | **Drop the uses table's pick column**, or keep it and record the pick. Nathan's choice (finding 48) | The record matches practice | None |

## 7. The path to completion

### 7.1 Ordered work items

Each runs one at a time (OD-29). Items marked * are proposed IDs.

| # | ID | Outcome | Depends on, and external gate | Closing evidence | Nathan's decision? |
|---|---|---|---|---|---|
| 1 | M05 close | The manager verifies and integrates this branch, records dispositions, refreshes the State of the App and fixes Notion (section 9). The Dev Manager reads the governing proposals before they merge | — | "Manager verification of M05"; the review log | After the Dev Manager: N1–N6 |
| 2 | M04 (+ CI hardening) | Merged-branch cleanup on push to `main` and manual dispatch, as the handoff's starting points say. It also takes the workflow fixes: `!cancelled()` (10), the Mobile margin (11), a newer upload-artifact pin (14) and the push filter's harness branches (AM7-02). Optionally the classifier flag (12) and the pin test (13) | P-7's Codex rule in the workflow first (finding 31) | Run of record, exact-head review, Codex, the Dev Manager's read of the CI policy | No |
| 3 | P09.3a* | The store, legal and safety requirements matrix (E2), research only | N3, N4 | The matrix in `docs/planning/`, dated, with sources | Its scope (N3) |
| 4 | P06.2-F* | Mobile hardening and the recorded follow-ups (E11) | — | Run of record, review | No |
| 5 | P06.3 | Notifications at fixture scope (E5) | N5; the push transport is gated on an EAS project and credentials (release block) | Brief, run, review; push transport carried to P09/P11 | Resume (N5) |
| 6 | S1* | Identity: allauth headless and the mail adapter, proven on disposable PostgreSQL in CI | N1; mail provider (A04) | Run of record; DB09 partly evidenced | N1 |
| 7 | S2* | Profiles and media: ORM adapters and HTTP views, behind the media port | N1 | As above | — |
| 8 | S3* | Eligibility, discovery and interactions: ORM adapters and HTTP views | N1 | DB05, DB10 and DB11 partly evidenced | — |
| 9 | S4* | Chat's HTTP surface: send and reads served behind the P11 plan's prerequisites, plus the OD-45 token cleanup (E7) | N1 | The P11 plan's "before the reads are served" items | The history policy (DM-22 3.1) |
| 10 | P07.1 | Safety policies and operator responsibilities for one operator (OD-23), including CSAM handling (E6) | The matrix | Policy drafts; Nathan's confirmation | Yes (operating duties) |
| 11 | P07.2 | Block, report, moderation cases and appeals, with the second-block-writer proof case (finding 25) | P07.1 | Run, review | — |
| 12 | P07.3 | The WordPress plugin through scoped Django APIs (OD-19), on a disposable WordPress | A disposable WordPress environment | Run, review | — |
| 13 | P08.1–P08.3 | Retention and export, deletion orchestration, entitlements if paid launch is chosen | A05, A06 | Runs, reviews | Retention; paid launch (A06) |
| 14 | E8* | Dependency remediation and Expo SDK assessment | — | Audit counts recorded | — |
| 15 | P09.1–P09.3 | Security and abuse controls, native builds and accessibility, observability and store evidence | Apple and Google accounts, an EAS project (N2; release authorization) | N01 partly; store matrix complete | Release-track authorization |
| 16 | P10.1–P10.2 | Pre-integration acceptance and the integration packet | P01–P09 | P10 record | — |
| 17 | P11.1 (P11A) | Disposable PostgreSQL: DB01–DB13 | P10 | P11 plan cases | — |
| 18 | P11.2–P11.3 (P11B) | Staging and sandboxes, the HDE adapter | The HDE contract (A01, A07: no date); Railway staging; the Stream production application | PV01–PV08 | Spending (N2) |
| 19 | P11.4–P11.5 (P11C) | Recovery proof, production connection, private smoke | Production authorization; A02's capacity check | PR01, DB13 | Production authorization |
| 20 | P12.1–P12.2 | Release-candidate acceptance and handoff | P11 mandatory acceptance | R01 | Store submission is separate |

If HDE's contract is still missing at P11, PF01 §5 applies: finish everything that does not need it, mark live compatibility blocked, and keep the fixture build.

### 7.2 Nathan's decisions (OD-32's form)

These go to Nathan after the Dev Manager has read them (the M05 brief).

- **N1 — Where the production server gets built.**
  - **What it is:** a plan amendment that places the HTTP API, real sign-in and the database code for every domain but chat (finding 1).
  - **What breaks without it:** P11 turns into the main build phase, and database defects surface last.
  - **Options:**
    - (a) build it domain by domain as items S1 to S4 before P10, each proven on a throwaway PostgreSQL in CI as chat was (OD-17's precedent);
    - (b) keep the plan: P10 and P11A build it all;
    - (c) build the API and sign-in now and the database code in P11A.
  - **Recommendation:** (a).
- **N2 — The budget for completion.**
  - **What it is:** the money for the accounts and services completion needs (finding 3; E3; E13).
  - **What breaks without it:** no signed iOS or Android build, no staging or production hosting, and an unknown Stream production plan. The Maker application has been pending 31 days.
  - **Options:**
    - (a) the manager prepares a costed list of each account and service, with its published price rechecked, and Nathan approves each line when its phase arrives;
    - (b) keep $0 and complete only to P10, stopping before native builds and P11B;
    - (c) decide each case as it comes.
  - Separately, Nathan checks the Maker application's status.
  - **Recommendation:** (a).
- **N3 — When the store and legal requirements are researched.**
  - **What it is:** the dated Apple/Google requirements matrix PF01 §7 asks for (finding 2; E2; E6).
  - **What breaks without it:** P06.3, P07 and P08 may miss store-mandated features (child-safety standards, in-app deletion, report/block, age rating), causing rework or rejection.
  - **Options:**
    - (a) now, as a research-only item after M04;
    - (b) at P09.3, as planned.
  - **Recommendation:** (a).
- **N4 — Launch countries and how age is assured.**
  - **What it is:** A05's launch geography and the adults-only check (finding 6; E4).
  - **What breaks without it:** the legal obligations (age assurance, data protection, deletion, child safety) cannot be scoped, and P07 and P08 design against placeholders.
  - **Options:**
    - (a) name the first launch countries now, and let the matrix state what each requires;
    - (b) have the matrix compare a short list (for example the US, the UK and the EU) first, then decide;
    - (c) defer to P08.
  - **Recommendation:** (b), then decide before P07's brief.
- **N5 — Resuming the remaining feature work.**
  - **What it is:** the feature pause (OD-05) still holds for everything after P06.2 (finding 7).
  - **What breaks without it:** P06.3 and everything after it cannot start, and phase P06 stays incomplete.
  - **Options:**
    - (a) resume P06.3 only;
    - (b) a standing resume of the remaining plan items in order, still one item at a time (OD-29), each brief still read by the Dev Manager where the charter requires;
    - (c) keep the pause.
  - **Recommendation:** (b).
- **N6 — The process changes in section 6.3**, after the Dev Manager's read.
  - **What it is:** S1 to S8 and D1.
  - **What breaks without it:** the current cost per merge continues.
  - **Options:** accept, accept some, or keep as is.
  - **Recommendation:** accept S1, S3, S4, S6, S7 and S8; decide S2, S5 (it changes OD-26) and D1 yourself.

### 7.3 The next item

**M04, with the CI hardening folded in, after M05's integration and the Dev Manager's read of finding 31's rule.** The reasons:

- M04 is the next item by OD-39 and OD-29.
- It is small and independent of N1 to N6.
- Its workflow change is the natural carrier for findings 10, 11 and 14, which would otherwise each need a full-scope cycle.
- It removes a recurring manual step: the branch report at each merge, and Nathan's deletions.

While it runs, Nathan's decisions N1 to N5 can be taken, so that the matrix (P09.3a) or P06.3 is ready to start when M04 merges.

## 8. Proposed text

Exact text, changing nothing on this branch. Each item names the finding it serves. "Replace" quotes the current text exactly.

**P-1 (finding 1). PF01 §8.** After the paragraph "**P06.DB** (OD-17) is the early disposable-PostgreSQL proof in §6. It runs after P06.1 closes and before P06.2.", add:

> **Server slices** (Nathan, [date]; N1). Before P10, the production HTTP API, maintained authentication (django-allauth headless with the mail adapter) and the ORM persistence adapters of each domain are built as slices S1 to S4, each proven on a disposable PostgreSQL in CI under P06.DB's rules (no shared or production database, CI-generated credentials, the runtime guards kept). The runtime stays sealed until P11 wires it. A slice's database proof partially evidences its P11 cases, and P11A and P11B still rerun them on the real target.

And add to §6, after "Other requests to bring real database integration forward require a concrete technical reason and an explicit plan amendment; development convenience alone is insufficient.": " The server slices (§8) are that amendment for the production server."

**P-2 (finding 2). PF01 §7, "Mobile/store readiness".** Replace "Maintain a dated requirements matrix for Apple and Google covering" with "Before P06.3's and P07's briefs, prepare and then maintain a dated requirements matrix for Apple and Google, for the launch countries (A05), covering". Replace R05's mitigation "Build policy/UGC/deletion/support matrix early;" with "Build the store, legal and safety matrix (§7) before P06.3 and P07;".

**P-3 (finding 3). PF01 A04**, append to the "Action / fallback" cell: " Before P09 and P11B the manager keeps a costed list of each account and service completion needs (Apple and Google developer accounts, Railway app services, the Stream production plan, Cloudflare, mail and push), with its published price rechecked; Nathan approves each line when its phase needs it. Nathan checks the Stream Maker application's status, which no record has updated since 25 September 2026."

**P-4 (findings 4 and 42). PF01.**
- D05's decision cell: replace "Separate GAPP-PF canon; one capable session; no automatic approval at each phase" with "Separate GAPP-PF canon; no automatic approval at each phase. The single capable session is superseded by D09's manual relay and D10's Dev Manager".
- D08's state cell: replace "Owner's explicit session authorization, 23 September 2026; current controlling permission record" with "Owner's explicit session authorization, 23 September 2026; the controlling app-only permission, applied to the sessions of the manual relay by D09 (the named sessions are historical, OD-01)".
- D10's state cell: append "; the outgoing Dev Manager creates its successor at Nathan's direction (OD-35; the charter)".
- §7, "Chat and notifications": replace "Test in-flight messages, stale tokens, existing channels, retries, reconnect and cross-device behavior." with "Test in-flight messages, existing channels, retries, reconnect and cross-device behavior; under OD-45 the app holds no provider token, so stale-token cases apply only to a server-held or leaked token."
- §8 P06's Development line: replace "idempotent message submission, token lifecycle, notification preferences" with "idempotent message submission, notification preferences (OD-45: no client token lifecycle)".
- §8 P06's Validation line: replace "client bypass attempts, wrong-channel membership, direct SDK send restrictions, stale tokens, block/unmatch during send" with "client bypass attempts, wrong-channel membership, block/unmatch during send (OD-45: no client SDK or token)".
- §2's repository-locations table: add the row "| `proofs/` | Provider and database proof harnesses (P06.1, P06.DB); outside the app runtime, checked in CI |".

**P-5 (finding 5). PF01 §8.**
- P06's Completion: replace "selected design has a credible tested provider-level safety path" with "the selected design's provider-level safety path is proven by the P06.1 matrix and the P06.2 suites named in their evidence records".
- After P06's Handoff line, add: "**P06.3 acceptance:** notification content comes only from Glow's server path and carries no birth details, compatibility data or message body by default; preferences and device registration follow their contracts at fixture scope; real push transport is deferred to P09/P11 with its credentials."
- P07's Completion: replace "workflows and staff UI are demonstrable" with "each workflow passes its fixture and contract tests and the staff views pass their scoped-API tests against a disposable WordPress".

**P-6 (finding 6). PF01 A05**, append to the "Action / fallback" cell: " The open A05 questions (launch geography, age assurance, the preference taxonomy, resurfacing and rematch, the history policy, retention, moderation operators) go to Nathan in OD-32's form before P07's brief."

**P-7 (findings 10, 31, 41, 49 and 50). Manager workflow.**
- Step 5, "Push runs as evidence": replace "The reason: push runs compare against the previous push and share a cancel-in-progress group per ref, so a Markdown-only push can cancel a code run and then skip every application job itself." with "The reason: push runs compare against the previous push. Runs of the same ref share a cancel-in-progress group, but the application jobs run under `always()`, so a superseded run's jobs finish and its conclusion can read `cancelled` with every job passed (run 40162341984); read the gate's line, not the run's label."
- Step 6, add a bullet: "**Wait for Codex before a review prompt** (AM7-13; DM-28 2.4; DM-30 4.2). Before giving Nathan an exact-head review prompt, wait until Codex's review has completed on the code head and on the commit that holds the prompt, and handle each finding first. A pass shown running with no result is not complete. When a new finding may change code under a review already with Nathan, tell him to hold it."
- Step 6, add a bullet: "**Fix or carry, by rule** (DM-23). A defect in a stage's own code that misses an item of that stage's prompt is fixed before the merge; a defect that needs P11's environment to show is carried to the P11 plan. Consult the Dev Manager only when the rule does not decide or a charter trigger applies."
- Step 7's first checklist bullet: replace "the run ID whose Foundation gate says `Application checks passed` on the exact head;" with "the ID of the PR run (event `pull_request`, read from `get_workflow_run`) on the exact head, whose Foundation gate says `Application checks passed` (DM-30 4.3; AM8-10);".
- After the "Writing to Notion" checklist, add a "**Claims: a checklist** (DM-01 P8; AM7-05, AM7-08, AM7-10, AM8-03, AM8-04, AM8-06, AM8-08)" with five bullets:
  - "Say *every*, *no* or *never* only after tracing each path."
  - "Copy a source's qualifiers in its own words."
  - "Check every count in a message to Nathan against its source."
  - "Name what clears a stuck state."
  - "Fetch a whole Notion page, write a property and the body together, and read both back."
- "Waiting checkpoints": append "Each names the cause of the wait (a session running, a relay, a decision of Nathan's, an external party) and when it started, so a reforecast can keep hands-on time apart from waiting (PF01 §11)."
- "Batching records": append "The current handoff stays under 5 KB and routes only. A follow-up goes to its owning brief or the P11 plan when it is recorded. Each merge receipt commit-pins the item's links into `docs/ephemeral/` and prunes its prompts."

**P-8 (findings 31, 32 and 40). `docs/planning/start-prompts/next-manager.md`.**
- Step 2: replace "check that your checkout is at or based on `origin/<BRANCH>`, the head of the open manager PR, which is more current than `main`." with "check that your checkout is at or based on `origin/<BRANCH>`, the manager branch the current handoff names (the open manager PR's head, when one is open), which is more current than `main` whenever it has commits beyond it."
- Step 3: replace "If a manager PR is open, its head branch is more current than `main`, so read from that branch; otherwise read from `main`." with "Read from `origin/<BRANCH>` whenever it has commits beyond `main`, whether or not a PR is open; read from `main` only when it has none."
- Step 2, add a bullet: "List the open manager PR's review threads and Codex's latest summary, and check each unresolved thread against the records, before your first report and before any message that says nothing else is open (AM8-01)."
- Item 5: replace "the request body and the rule are recorded in `docs/planning/reasoning-level-matrix.md`, section 6, and Nathan installs the skill." with "the request in force (v8.2) and its rule are carried by the installed skill, their authority (OD-42; workflow step 3); the matrix's section 6 holds v6 as history, and Nathan installs the skill."

**P-9 (findings 10 and 14). CI policy.**
- Replace "A push run compares against the previous push, and runs of the same ref cancel each other. A Markdown-only push can therefore cancel an in-progress code run and skip every application job itself." with "A push run compares against the previous push. Runs of the same ref share a `cancel-in-progress` group, but the application jobs and the gate run under `always()`, so a newer run does not stop an earlier run's jobs once Change scope has finished. They run to completion, the newer run waits for them, and the earlier run's conclusion can read `cancelled` with every job passed (run 40162341984)."
- In the first section, replace "the reviewed migrations from zero, `makemigrations --check --dry-run`, the ordering suite, the stress run, the negative controls and the commit-order oracle;" with "a wrong marker's refusal and `dbshell`'s refusal, the reviewed migrations from zero, `makemigrations --check --dry-run`, the ordering suite on both subjects (the reference design and the app's adapter) with the stress run, the negative and planted controls and the commit-order oracle, the delivery and read phases, and a second run's refusal on the used database;".
- The upload-artifact row: replace "v4 (workflow comment; exact patch release not verified)" with "v4.6.2 (the commit the `v4` and `v4.6.2` tags name, read with `git ls-remote` on 26 October 2026)", and "(seen in P06.DB's runs); a newer pin is a later change" with "(seen in every run, 40243775584 included); a newer pin (v7.0.2 is current) is a later change".

**P-10 (finding 39). Owner-direction register,** State cells, each appended:
- OD-10: "**Updated by OD-30, OD-33, OD-34 and OD-42:** the skill's reading (request v8.2) is the recommendation. OD-34 dropped the outcome column, so the ten-session comparison no longer exists; DM-01 question 3 is recorded as answered by OD-34."
- OD-30: "**Superseded by OD-33 and OD-34**; request v8.2 since OD-42."
- OD-33: "**Updated by OD-34 and OD-42.**"
- OD-38: "P06.2 is done: PR33 merged at `5b9bcb1` on 25 October 2026."
- OD-39: "OD-48 puts M05 first; M04 follows it. Nathan deleted the eight merged branches of C1 to C2-C4 by hand after PR33 merged."
- OD-44: "DM-17 was answered and integrated on 23 October 2026."
- OD-31: "The manager branch has been `claude/magical-wozniak-yfmmx2` since OD-38."

**P-11 (finding 40).**
- `docs/planning/reasoning-level-matrix.md:3`: replace "This file is the home of the matrix, of the request in force (v6; v5 is kept below as history) and of its pre-registered rule;" with "This file is the home of the matrix and of the history of requests v5 and v6 (to 6 October 2026); the request in force is v8.2, carried with its rule by Nathan's installed skill `typesafe-scoring`, their authority (OD-42; workflow step 3);".
- `docs/README.md`, one-home table: replace "The reasoning-strength matrix (models and levels), the TypeSafe rule, evidence and readings" with "The reasoning-strength matrix (models and levels), its evidence and the history of requests v5 and v6", and append to its home cell "; the request in force (v8.2) and its rule: the installed skill (OD-42)".

**P-12 (finding 22). ADR 0004, line 34.** Replace "the API opens no database connection, and its fixture guards refuse every database connection name, including `GLOW_DATABASE_URL` and `DATABASE_URL`;" with "the API opens no database connection (Django's dummy backend, and no driver in the image), and its fixture guards refuse by presence the names in `FORBIDDEN_CONNECTION_NAMES`, including `GLOW_DATABASE_URL`, `DATABASE_URL`, `DATABASE_PRIVATE_URL` and five libpq `PG*` names (other names, such as `DATABASE_PUBLIC_URL` or `PGPASSFILE`, are not refused until the hardening item lands);".

**P-13 (findings 20, 24 and 28). Component READMEs.**
- `apps/mobile/README.md:440`: replace "There is no network client, API URL, WebSocket, `EventSource`, push or realtime service." with "The chat code has no network client, API URL, WebSocket, `EventSource`, push or realtime service; the app's only network code is the retained development transport in `src/data/recommendations.ts`, used by the root smoke script."
- `apps/mobile/README.md:18`: after "The earlier nonpersistent API layout transport remains available for smoke checks.", add "Since P05.2 no screen mounts a loader for it, so setting `EXPO_PUBLIC_GLOW_API_BASE_URL` for `npm start` changes no screen."
- `services/api/README.md`: after each description of the client token's signer (`:58-59`, `:78-90`), add "(dormant under OD-45: no client token is issued or served; the P06.2 brief, item 4 and point h)". After its Stage B2 section, add a line naming Stage C1's `glow_domain/chat_reads.py`, `chat_projections.py` and `glow_chat/reads.py`.

**P-14 (finding 45). HDE contract request, section 2,** add rows after C29:
- "| C30 | Does HDE tell the app when a chart or a result changes, or when a deletion completes (a callback or event), and how is that message authenticated? Otherwise, what must the app poll? |"
- "| C31 | Can the app obtain what HDE holds about a user, for that user's data-export request (PV07)? |"
- "| C32 | Are deletion requests idempotent and safe to replay after the app restores a backup (DB13)? If HDE restores its own backup, how does the app learn that a deleted chart has returned? |"
- "| C33 | What must HDE do when a user withdraws the consent that covers birth-data processing? |"
- "| C34 | Where are birth details stored and processed, and is HDE a processor for the app's users? |"
- "| C35 | Which deployment identity serves each environment the app calls (PF01 §5: the HDE commit and deployment)? |"

**P-15 (findings 9 and 38). Current handoff** (manager-owned):
- The branches section: replace its kept and to-delete list with "Three remote branches (`git ls-remote`, 26 October 2026): `main` (`5b9bcb1`), the manager branch (`f669f37` before M05's integration) and `claude/dev-manager` (`6bf6f5d`). Nathan deleted the eight fully merged session branches of C1 to C2-C4 after PR33 merged (OD-48)."
- Replace the "Recorded follow-ups" paragraph with one line each linking the owning homes:
  - the P11 plan, for the guard and the fixture `already`;
  - a "Carried to the next `apps/mobile` change" section in the P06.2 brief, for DM-29 1.1, the C2 review's findings 1, 4 and 5, the README sentences and the window-replacement tests;
  - the M04 brief, for the Mobile margin, the upload-artifact pin and the push filter;
  - the M02 brief, for the Setup-script hardening and uv;
  - the P07 brief, for E12.

**P-16 (finding 43). Continuity snapshots.**
- After `state-of-the-app.md` line 6, add: "> **Out of date (26 October 2026).** P06.1, P06.DB and P06.2 have merged since, and OD-28 to OD-48 were given. It is refreshed from M05's review; until then the current handoff and the register govern. Its dependency line (1.7) understates the advisories: M05 finding 29."
- Under `claude-code-handoff.md`'s code-map and Stream headings, add: "> **Out of date since P06.** This predates P06.1, P06.DB, P06.2 and OD-45; read the code and the P06 briefs."
- In `next-manager.md`, replace "the code map and the history to 24 September" with "the history to 24 September; its code map predates P06".

**P-17 (finding 42). Dev Manager review log.**
- `README.md:207`: append "[Closed 25 October 2026: made generic at `2ef4b1b`, after Dev Manager 3 started (00:58 UTC); DM-07 item 7's 'before the next Dev Manager session' was not met.]"
- DM-13's row: append "(item 7.2's option (a) superseded by OD-45, 24 October 2026)".
- DM-01 P3's "Later: … a PR-to-work-item index": append "Not built; withdrawn or scheduled by the next process review."

**P-18 (finding 42). `CLAUDE.md`, "Environment".** Replace "App sessions run in the dedicated app cloud environment: no HDE variables, and the pinned toolchain from `scripts/bootstrap-toolchain.sh`." with "App sessions run in one of Nathan's two dedicated app cloud environments (OD-36): `Glow app`, which holds the Stream development variables, only for a session that calls Stream, and `Glow App - No Stream` for every other. Neither has HDE variables, and both carry the pinned toolchain from `scripts/bootstrap-toolchain.sh`."

**P-19 (finding 49). The Dev Manager charter, "Not for:".** Replace "**Not for:** routine verification, routine records, small documentation fixes, CI reruns, or exact-head code review." with "**Not for:** routine verification, routine records, small documentation fixes, CI reruns, exact-head code review, or a review finding's fix-or-carry that the workflow's rule decides (step 6)."

## 9. Notion mismatches

**Read coverage.** A read-only subagent fetched:

- all of Implementation Control (136,557 characters, as of 23:38 UTC on 25 October);
- the owner-direction register page (48 rows);
- all 70 Work Register rows and their 11 columns;
- the Dev Manager page (68,286 characters);
- the State of the App page;
- the TypeSafe usage log, with its 77-row uses table.

The App Builder 1 progress page and the Implementation Control history page were read only at their heads, tails and links. I read the Work Register myself (SQL) and confirmed three of the stale Implementation Control strings in the fetched text. Nothing was written to Notion.

| Notion location | Notion says | The repository says | Severity |
|---|---|---|---|
| Implementation Control, the operating procedure's stamp | Matches the manager branch at `51844a5`, checked 23 October | The register (OD-46 to OD-48) and both start procedures changed after it; the page's own lead says `f669f37` | Major |
| Implementation Control, "Manager:" | App Manager 7 holds the manager branch and the draft PR31 | App Manager 8 (OD-46) | Major |
| Implementation Control, "Dev Manager:" | Dev Manager 2, `session_015Dx…`; no consultation pending | Dev Manager 3, `session_01KVuPEp…` (OD-47); DM-01 to DM-30 | Major |
| Implementation Control, "Main" | `3272eed`; the draft PR31 open | `5b9bcb1`; no PR open | Major |
| Implementation Control, "Branches" | Eight remain; `main` `a8e9528`; `claude/dev-manager` `c8bc632` | Three heads (`ls-remote`, 26 October) | Major |
| Implementation Control, "Standing directions" | Holds OD-01 to OD-47 | OD-01 to OD-48 | Minor |
| Implementation Control, "Mistakes log" | AM3-01 … AM7-12 | Also AM2-01–AM2-11, AM7-13, AM7-14, AM8-01–AM8-10 | Minor |
| Implementation Control, "Phase" | M03 complete; P06.2 resumed (not done) | P06.2 done; no M03 in the repository | Minor |
| Implementation Control, "Next items" | C2-C1's re-review "is with Nathan" | Withdrawn (OD-46) | Minor |
| Implementation Control, the procedure §4 "Classification" | Only the `.claude/` exception | Also: more than one merge base is full scope; a missing or ambiguous policy means full review; `python3 -I`; the workflow-change rules; no `pull_request_target` | Minor |
| Implementation Control, the procedure §3, §5 and §6 | Lacks: a read covers one commit; consequential decisions wait; the Notion checklist's other lines. §6 adds a "stop" for the HDE-shared environment | The charter and workflow; `CLAUDE.md` says tell Nathan and use a clean environment | Minor |
| Implementation Control, the procedure §5 | The ladder's rule "lives in the reasoning-strength matrix" | The skill is the authority (OD-42) | Minor |
| Dev Manager page | "The primary manager (App Manager 7 …)"; Dev Manager 2's row ends at DM-22 | App Manager 8; DM-23 and DM-24 also | Minor |
| Work Register, M04 | "Ready"; Next Action: runs "when a PR merges into main" | No brief yet; the handoff's starting points say push to `main` and manual dispatch, never a pull-request event | Minor |
| Work Register, M03 | Done | No repository record | Minor |
| Work Register, P00.1 and P00.2 | Evidence: a Google Drive file | Drive is non-operational (D09); PF01 and `authority-transfer.md` are the evidence | Minor |
| Work Register, P00.3, A03, P01.1, P05.1, P05.3 | Evidence: Notion pages or the legacy repository | PR1 to PR14, ADR 0001, the P05 checkpoints | Nit |
| Work Register, D10 | Next Action stops at Dev Manager 2; "PF01 since revised, to 1.11" | Dev Manager 3 (OD-47); PF01 1.12 | Minor |
| Work Register, A01 and A07 | HDE request "at commit `dbe707b`" | Revised at `c775f39` | Nit |
| TypeSafe uses table | Nathan's pick "pending" or "not recorded" for 17 of 18 recent Glow prompts; withdrawn rows "pending"; 3 corrections labelled "implementation"; 4 rows from other projects; no row for App Manager 8 | The workflow's step 4 records Nathan's pick | Minor (finding 48) |

**Matches:**
- The register page: 48 rows stamped `f669f37`; the differences are formatting only.
- Implementation Control's lead paragraph, with PR33's facts.
- The Dev Manager page's DM-01 to DM-30, in substance.
- The State of the App page, which mirrors the stale repository snapshot.
- All 41 GitHub links on Implementation Control; none points at a session branch.

**Repository side stale where Notion is current:**
- the P06.2 brief's "Work Register: Ready", corrected here (finding 36);
- the matrix's v6 header (finding 40).

## 10. The checks run, and the limits

All checks ran at `HEAD` = `f669f37`, in clean processes, on the pinned toolchain.

| Check | Command (from the component's directory) | Result |
|---|---|---|
| Classifier tests | `python3.12 -I -m unittest discover -s scripts -p 'test_change_scope.py' -v` (root) | `Ran 13 tests in 5.609s`, `OK`; exit 0; 5.8 s |
| API install | `python3.12 -m venv .venv`; `pip install --require-hashes -r requirements-dev.lock`; `pip check` | exit 0 (12 s); `No broken requirements found.` |
| API Django check | `GLOW_ENV=test python manage.py check` | `System check identified no issues (0 silenced).`; exit 0 |
| API tests | `GLOW_ENV=test python manage.py test tests --verbosity 2` | `Ran 366 tests in 12.699s`, `OK`; exit 0; 14.2 s |
| API lint and types | `ruff check .`; `ruff format --check .`; `mypy` | `All checks passed!`; `78 files already formatted`; `Success: no issues found in 41 source files`; each exit 0 |
| Contracts, Python | `PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests -v` | `Ran 39 tests in 0.488s`, `OK` |
| Persistence static check | `GLOW_ENV=test python -m glow_persistence.static_check` | `Static definitions agree: 34 app models; migrations=0001_event_infrastructure,0002_app_domain,0003_chat_identity_read_cursor`; exit 0 |
| Contracts install | `npm ci --ignore-scripts` | exit 0; npm noted 1 moderate |
| Contracts generate | `npm run generate` in a scratch copy, then `diff -r` of `apps/mobile/src/contracts/generated` against the checkout | `Generated types and runtime validators.`; no difference (exit 0) |
| Contracts check | `npm run check` | `Generated types and runtime validators match schemas.`; `tests 586`, `pass 586`, `fail 0`; exit 0 |
| Mobile install | `npm ci --ignore-scripts` | exit 0 (16 s); npm noted 14 vulnerabilities |
| Mobile check | `npm run check` (tsc, eslint, `node --test`) | tsc and eslint clean; `tests 621`, `pass 621`, `fail 0`; exit 0; 13.9 s |
| Expo compatibility | `EXPO_OFFLINE=1 npm run check:expo` | `Dependencies are up to date` (with Expo's "Dependency validation is unreliable in offline-mode"); exit 0 |
| Development export | `EXPO_OFFLINE=1 npm run export:development` | iOS bundle 8.1 MB, Android 8.7 MB, `Exported: .work/native-export`; exit 0; 17.2 s |
| Rendered tests, **informational, not the pinned browser** | `playwright test` with an uncommitted config outside the repository, pointing at the container's Chromium 1243 (Playwright 1.62.1 pins 1234) | `97 passed (5.1m)`; exit 0 |
| Smoke | `GLOW_SMOKE_PYTHON=<API venv python> node scripts/smoke.mjs` (root) | `PASS: spawned loopback API -> mobile TypeScript client; live 200, ready 503, deterministic pending fixtures, writes 405.`; exit 0 |
| Smoke test | `node --test scripts/smoke.test.mjs` | `tests 1`, `pass 1`, `fail 0`; exit 0 |
| Stream proof install | venv, `pip install --require-hashes -r requirements-dev.lock`, `pip check`, `npm ci --ignore-scripts` | exit 0; `No broken requirements found.`; npm noted 1 high |
| Stream proof tests | `env -i … python -m unittest discover -s tests -t .` | `Ran 648 tests in 48.036s`, `OK` |
| Stream proof lint, types, syntax, plan | `ruff check .`, `ruff format --check .`, `mypy`; `node --check client/*.cjs`; `python checks/run_plan.py` | `All checks passed!`, `59 files already formatted`, `Success: no issues found in 57 source files`; four files ok; `run plan: fits` |
| Database proof install and tests | venv, install, `pip check`; `python -m unittest discover -s tests -t . -v` | `No broken requirements found.`; `Ran 160 tests in 10.940s`, `OK` |
| Database proof lint and types | `ruff check .`, `ruff format --check .`, `mypy` | `All checks passed!`, `44 files already formatted`, `Success: no issues found in 44 source files` |
| Audits | `npm audit --json` in each Node package | Finding 29 |

**Read from CI, not run** (no Docker and no database here). Run 40243775584, the push run of `5b9bcb1`, concluded `success`, 23:13:32 to 23:21:15, every job `success`:

- **The gate** printed `Application checks passed`.
- **Database proof checks** (7 min 27 s):
  - the wrong marker was refused, with relation counts unchanged and `django_migrations` absent;
  - `dbshell` was refused;
  - migrations `0001`–`0003` applied, with `No changes detected`;
  - PostgreSQL 17.11, not a superuser;
  - reference subject `56/56`, oracle 0 violations;
  - adapter subject `115/115`, 15 races, `717 submissions … 0 violations`;
  - delivery `13/13`; read `62/62`;
  - `== VERDICT: PASS ==`;
  - the second run was refused, with row counts unchanged;
  - cleanup: `no proof container remains`.
- **API artifact checks:** `built-image loopback smoke passed`.
- **Mobile checks:** 6 min 24 s, `97 passed (4.8m)`.

The 15 most recent of `main`'s 31 Foundation runs are all `success`. Off `main`, run 40029112295 failed on the Mobile timeout (diagnosed in the P06.2 record). Seven runs labelled `cancelled` were superseded (finding 10).

**Reversals:** about 70 ran in scratch copies outside the repository, by subagents. Each component's table, with the edit, the command and the result, is summarized in findings 12, 13, 17, 18, 25 and 27. The checkout was never edited for a reversal. `git status` stayed clean apart from ignored install and build directories.

**How I verified the subagents' reports.** Seven read-only subagents reviewed the API, the mobile app, CI and the proofs, the process records, the evidence records and the P11 plan, the metrics, and Notion. I re-checked, myself:

- every finding I corrected in the text, at its line;
- the stale Notion strings;
- run 40162341984's label and its jobs;
- the API refusal list, by running it;
- the message spool's code path;
- that nothing imports `_layout`;
- the provider wording lines;
- the start procedure's rule against `main`'s handoff;
- the merge list and the Markdown growth;
- the remote heads;
- `npm audit`;
- the toolchain;
- the rendered run.

Counts I took from the subagents without repeating them: the mistakes log's classes, the per-item pass counts, Codex's thread states, and the review verdict split.

**Limits:**
- No database, Docker, Stream, HDE or Railway call was made. The database proof's PostgreSQL steps and the image were read from run 40243775584's logs.
- No native build or device was used.
- The rendered run used Chromium 1243, so it is informational only.
- B2-C3's live Stream rows were taken from the records.
- Review sessions push nothing, so the review verdicts are as the evidence records state them.
- Notion was read as described in section 9; the two very large pages were read in part.
- No legal or store-policy source was fetched (no network beyond installs and the audit). The store and legal points in E2, E6 and N3–N4 are what the matrix must establish, not verified requirements.
- The causes of the waiting gaps are not recorded, so I could not determine them.

**This review's own change** (the prompt's "before you report"): section 11.

## 11. Corrections made

- **`300a24d`**, "M05: corrections and additions in non-governing Markdown": 23 files, each change marked with its finding.
  - `docs/operations/`:
    - `local-development.md` (13, 16, 35);
    - `migration-plan.md` (35);
    - `environment-inventory.md` (22, 35, 42, 46);
    - `providers-and-webhooks.md` (35);
    - `environments.md` (35);
    - `operational-runbooks.md` (35);
    - `configuration.md` (35).
  - `docs/planning/`:
    - `claude-setup-optimization.md` (36);
    - `database-audit-2026-09-23.md` (36);
    - `claude-code-migration.md` (36);
    - `p06-2-chat-integration.md` (36);
    - `p06-db-disposable-postgres-proof.md` (36).
  - `docs/architecture/`:
    - `data-model.md` (24, 26);
    - `discovery-fixtures.md` (27);
    - `domain-and-data-boundaries.md` (28);
    - `interactions-fixtures.md` (37);
    - `onboarding-fixtures.md` (37);
    - `privacy-and-safety-rules.md` (23).
  - `docs/testing/`:
    - `p11-deferred-acceptance.md` (33, 34);
    - `p03-checkpoint.md`, `p04-1-checkpoint.md` and `p05-1-checkpoint.md` (47, annotations).
  - `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`: annotations only (29, 47).
- **This record's commit:** this file only.

**This review's own change, checked before the report:**
- `git diff --name-only f669f37 HEAD` lists only this record and paths inside the write scope above.
- The trusted classification of `f669f37..HEAD` printed `"full": false` and `"reason": "ordinary-docs-only"`.
- `git diff --check f669f37 HEAD` printed nothing.
- `git status` was clean, and the branch was pushed.

The exact outputs are in the report Nathan relays.

Status: complete
