# SV2 Stage A exact-head review prompt — the server's profile, with a written threat model

- **Owner:** App Manager 10. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 2, 10 November 2026.** It adds Codex's P2 finding on `40db2c2` (a future birth date) to focus item 3, with both readings of C1-3. Revision 1 was at `40db2c2`.
- **Durable brief:** [SV2 — The profiles and media slice](../planning/sv2-profiles-media.md), revision 4, "Review plan" and "Stage A, correction C1".
- **Where the result goes:** the report Nathan relays. The manager records it in the evidence record, "Exact-head review of Stage A", with a disposition for each finding (fix before the merge, or carry), and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Fable 5.1 at extra high.** Effort score 3.18 (confidence 0.87); rung probabilities low 0.00, medium 0.00, high 0.01, extra high 0.80, max 0.19, ultracode 0.00. Model probabilities Fable 5.1 0.67, Opus 5.5 0.33, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.56). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.007, Fable 5.1 at extra high 0.536, Fable 5.1 at max 0.127, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.000, Opus 5.5 at high 0.003, Opus 5.5 at extra high 0.264, Opus 5.5 at max 0.063, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-10T13:16:44Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs (the brief's "Review plan"). The review authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of PR43's head and of this prompt's commit (manager workflow, step 6).
- **Deletion condition:** prune after SV2 Stage A's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **exact-head code and security review of SV2's Stage A**, the server's profile, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one exact code head, with a written threat model. This prompt is revision 2, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **The brief,** `docs/planning/sv2-profiles-media.md`, revision 4. Its Stage A text applies the Dev Manager's conditions word for word: DM-52's B1 to B55, DM-53's W1 to W10 and DM-54's Y1 to Y12, in `docs/continuity/dev-manager/reviews/` (`2026-11-10-dm-52-sv2-brief.md`, `…-dm-53-sv2-stage-a-paths.md`, `…-dm-54-sv2-stage-a-decisions.md`), with Nathan's answers as OD-60 and OD-61 (`docs/continuity/owner-directions.md`). In short, Stage A builds:
  - a versioned, audited settings store with launch defaults and fixed limits in code (D2);
  - four two-way list fields, own words and display choices, and "show me" sets with an "all" marker (D3);
  - the age range, and location by Census area, the phone's coordinates a query that keeps nothing (D4, D5);
  - onboarding consent through `glow_chat`, and a sensitive-fields consent of its own (D6);
  - the adult check, with the date's one home in the age state (D7), and the private birth input with a birth time required (D8);
  - completion as one shared recompute at the end of every requirement writer, and pause, resume and restriction through `glow_chat` (D9);
  - identity verification's seam, and staff approval without it behind a setting (D18);
  - 15 sealed member routes, additive DTOs, flow-registry entries and regenerated contract outputs (D11), keyed idempotency digests (D17);
  - a profile suite on a third disposable database in the Database proof checks job (D12); the served runtime sealed (D13).
- **The implementation** (branch `claude/sv2-stage-a-impl-0qqzvj`, code head `b97bc15`): 44 profile cases and 59 reversals, each failing its case. Run of record: push run 42759801460, all eight jobs passed. The manager verified it (the evidence record, "Manager verification").
- **The Dev Manager ruled on its 13 decisions** (DM-54). Two P1 findings from Codex on `033e8d4` (the recompute in one writer only; a failing birth input stored) are the same defects. Codex's review of `40db2c2` added one P2 finding, on C1-3's point (focus 3).
- **Correction C1** (branch `claude/funny-lamport-5f2s1u`, code head `86a2156`; the evidence record, "Correction C1"):
  - D9's one recompute at the end of every Stage A requirement writer;
  - a birth input whose date fails the adult rule refused and not stored, while its rerun commits;
  - `requirements_met` and `restrict` in the registry;
  - `glow_profiles` in CI's mypy;
  - one data-model sentence.

  Run of record: push run 42769301337, all eight jobs passed, the profile suite 47/47. The manager verified it (the evidence record, "Manager verification of correction C1") and accepted the session's five decisions, C1-1 to C1-5, two of them as readings to confirm (below).

**The code head under review is `86a2156`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `86a2156` (the start gate checks this).

**Your scope:**
- **The code:** `git diff df8a04c5118d41016c14001308f796fd47626916 86a215675e0ad826425e16c14fb6b826664b9c34`, its 59 non-Markdown paths:
  - `services/api/glow_profiles/` (19), the new app;
  - `services/api/glow_domain/` (4: `profile_fields.py`, `profile_settings.py`, `identity_verification.py`, and `identity.py`'s age section);
  - `services/api/glow_identity/age.py` (D7's transition);
  - `glow_persistence/models.py` and migrations `0005` to `0007` (the third loads the launch defaults, the second the area table);
  - `services/api/tests/` (11) and `services/api/pyproject.toml` (mypy's `files`);
  - `packages/contracts/` (the schema, `openapi.json`, `flows-v1.json`, the corpus, `tests/test_transition_contract.py`);
  - `apps/mobile/src/contracts/generated/` (3), written only by the generator: check them by regenerating, not by reading the diff (DM-53, W1);
  - `proofs/postgres-ordering/` (the profile modules, `schema_check.py`, `__main__.py`, `pyproject.toml`, `tests/test_profile_offline.py`);
  - `.github/workflows/foundation.yml` (the Database proof checks job).
- **The data:** `services/api/glow_profiles/data/cbsa_areas_2024.tsv` and its derivation, `areas_source.py`.
- **The records, as claims about the code:**
  - the evidence record's "Stage A", whole, with both manager verification sections and "Correction C1";
  - the data model's SV2 rows and its "Identity, time and field semantics" sentence;
  - the contract document's F02 to F06 index rows and server mapping, and its trusted test prerequisites;
  - both READMEs' SV2 sections;
  - the P11 plan's SV2 entries;
  - the CI policy's Database proof checks paragraph, as it describes the SV2 steps.
- **The runs:**
  - 42759801460 and 42769301337;
  - the PR run on PR43's head (event `pull_request`), once it has finished.
- **Out of scope:** code this item does not change (`glow_chat`, `glow_identity` beyond `age.py`, `glow_api` and the rest), and Stage B's photos (D10). A finding there is reported as pre-existing, not as a defect of this item.

**The threat model** (the brief's "Review plan"; DM-31 item 3). Write it in your report:
- **Assets:**
  - the member's own profile, fields and own words;
  - the sensitive fields (orientation, relationship status) and their consent;
  - "show me" sets, which reveal a member's preferences;
  - the age state's date and the birth input (date, time, place), the most sensitive input Glow holds;
  - the phone's coordinates, which must never be kept;
  - the area;
  - consent decisions;
  - the identity verification state and staff approvals;
  - the settings and their fixed limits;
  - the stored idempotency digests;
  - the profile suite's `SECRET_KEY` and JWT key, and the run's database credentials.
- **Actors:**
  - an anonymous prober;
  - a holder of another member's stolen token (SV1's actor);
  - a signed-in member acting on another member's objects;
  - a member who declares a date under 18;
  - a staff caller, in code until P07;
  - a console publication that crosses a fixed limit;
  - anyone who reads this public repository's CI logs and artifacts.
- **Entry points:**
  - the 15 routes under SV1's actor;
  - the staff operations (`glow_profiles/staff.py`), with no route;
  - the settings publication (`settings_store.publish`);
  - the data migrations;
  - the profile suite's job steps.

For each threat, give the code that stops it and the test that proves it. It covers the brief's "Review plan" focus list for Stage A, every item except the media ones:
1. each route's ownership and refusals;
2. the settings' fixed limits and audit;
3. the sensitive fields' consent and withdrawal;
4. what the location keeps and what it never keeps;
5. the birth input's privacy and the HDE boundary;
6. the seal;
7. the proof's secret handling;
8. that no member route reaches a staff operation, and a staff operation's subject comes only from its caller in code;
9. D17's rules in every response and every error, validation messages included;
10. the "all" marker and "not stated": a value the console adds, a retired value, and a member who declines the sensitive-fields consent;
11. consent's purpose filtering and the current-version check;
12. the age state's transition, a corrected date, and the demotion of a visible profile;
13. the outbox: events carry references, never values;
14. the stored idempotency digests (D17);
15. the seeded requirements: no runtime path writes a resolved mapping or `verified`, and a test's seeded rows cannot reach the runtime;
16. staff approval without identity verification: staff only, only while the setting allows it, audited, revocable, and never standing in for another requirement;
17. the area file: its pinned hashes, and nothing fetched;
18. **D9's recompute** at the end of every requirement writer (Y12): no path makes a profile `visible` with a requirement missing, and none leaves one `visible` after a write that finds one missing;
19. **a birth input whose date fails the adult rule** (Y12): nothing of it is kept, the rerun's effects commit, and a retry changes nothing more.

**The focus:**
1. **The threat model above,** each threat with its stopping code and its test.
2. **The Dev Manager's conditions met in code:** DM-52's B1 to B55 for Stage A, DM-53's W1 to W10 and DM-54's Y1 to Y12. Name any condition the code does not meet.
3. **The manager's readings, to confirm or refute:**
   - **C1-1:** a demotion found by a field or area write is `requirement_removed` (`system`). Also: a demotion inside the profile edit is always the owner's `edit`, even when the cause is a lapsed requirement, not a cleared summary (`recompute.py`, `entry`). Is that within Y4's words, and does it change any event SV3's invalidation reads?
   - **C1-3, which Codex's P2 finding on `40db2c2` contests** (`operations.py:1019`, "Commit the protective reset for future birth dates too"): a future birth date is refused (400) with no rerun and no state change; only a date under 18 takes D7's refused-and-rerun path.
     - **For the reading** (C1's session): a future date fails D7's validity ("valid, not in the future"), not its age test, and declares no age; P04's `birthInputValid` refuses it too. Acceptance item 7's rerun clause names only a date under 18.
     - **Against it** (Codex): `adult_outcome` fails a future date, and acceptance item 7 counts "a future date" among the dates that fail. Y6 and Y7 speak of a date that fails "the rule" and "the adult rule".
     - **Asked:** which reading the words support; whether either leaves any state a self-declared minor could keep; and whether any other failing date bypasses the committed reset, such as an invalid one. If the words support Codex's reading, it falls in the class "leave a Dev Manager condition unmet". If they do not decide, the manager puts your answer to the Dev Manager with the correction's scope.
4. **No test is weakened or vacuous:**
   - each reversal the record names fails its case;
   - no case could pass while the behaviour it guards is wrong. Above all: the coordinates' "never" tests, the sensitive consent's withdrawal, the lock-order cases, the recompute's call sites, the refused birth input and the digest test;
   - the static guards (`test_profiles_offline`'s logging, staff-route and call-site checks, and the sealed-runtime test) are not defeated by a plausible edit;
   - no existing test was weakened.
5. **The known items:** for each, right as dispositioned, or a finding:
   - orientation launching with no values, and distance with `anywhere` only (DM-54, item 1);
   - `AdultCheckIntent` and `OwnAgeState`;
   - the idempotency records' 24 hours, and what an expired record does;
   - a new onboarding consent version and a visible member (DM-54, item 5; carried to SV3, SV4 and P08);
   - an integral JSON number accepted as an integer;
   - `Profile.location_label` removed.
6. **The contract:**
   - every existing DTO and registry entry is unchanged;
   - each new DTO is closed;
   - the generated outputs match the schemas when regenerated;
   - each new registry entry uses a role the oracle authorizes, with an allowed and a forbidden example.
7. **The workflow** (root `AGENTS.md`: CI routing is not a security boundary):
   - the complete diff of `foundation.yml` from `df8a04c` to `86a2156` is confined to the Database proof checks job;
   - no job, condition or gate elsewhere changed;
   - every SV2 step does what its name says, and the CI policy's paragraph describes them.

   Read the actual job steps and logs of both runs.
8. **No new dependency:** every lock is unchanged.
9. **The records:** every claim in the evidence record's Stage A sections and the texts listed in the scope holds against the code and the runs.

**Re-run, at least,** in a scratch copy of `86a2156`:
- **The API's checks:** `manage.py check`, `manage.py test tests`, `ruff` and the configured `mypy`. The contract tests. The proof's offline tests, `ruff` and `mypy`.
- **The contract outputs:** `node scripts/generate.mjs --check` in `packages/contracts`, after `npm ci --ignore-scripts` there.
- **Five offline reversals:**
  - the runtime's URL configuration importing a pure new module (`glow_domain.profile_fields`): the sealed-runtime test fails;
  - the stored digest an unkeyed SHA-256: `test_profiles_offline` fails;
  - a module other than the views getting a logger: `test_profiles_offline` fails;
  - the recompute removed from one writer: `test_profile_recompute` fails;
  - a type error in `glow_profiles`: the configured `mypy` reports it.
- **The profile suite, informational:** on a throwaway PostgreSQL under P06.DB's D4, if Docker allows. It is informational, and you name it so. If you can run it, add a database reversal you doubt, such as a coordinate logged at `DEBUG`, or the failing birth input's refusal raised instead of returned.

**What comes after this review: the correction classes.** Report every finding with its severity. A correction pass takes every blocking finding, and any should-fix finding that could do any of these:
- let a coordinate, a birth date, time or place, an own-words value, a sensitive field or a "show me" set reach a log, an error, a URL, an outbox event, a CI log, an artifact, another member, or a digest that can be reproduced without the key;
- let a member read or write another member's object, or act unauthenticated;
- let a sensitive field, its own words or a narrowed sensitive set be saved without the sensitive-fields consent, or outlive its withdrawal;
- let one consent's decision satisfy or revoke the other's, or an old consent version be accepted;
- let a publication cross a fixed limit, or skip its audit;
- let a member route reach a staff operation, or a staff approval be granted while the setting is off, or stand in for another requirement;
- let a profile be `visible` with a requirement missing, or stay `visible` after a write finds one missing;
- keep any birth data of a self-declared minor, or leave such an account an adult's;
- let the served runtime import SV2's code, or add a package;
- let a test pass where it should fail, or fail where the code is right;
- leave a Dev Manager condition unmet;
- make a record claim more than the code, the tests or the runs show.

Everything else goes into the records. For each finding, say whether it falls in one of these classes.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 10. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - **Scratch work goes in a copy outside the repository,** never the checkout (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
- **Network:**
  - PyPI and the npm registry, for hash-locked installs in a scratch copy;
  - `www2.census.gov`, only to re-read the Gazetteer zip D5 names, if you check its hashes yourself; it goes in a new, empty directory, read with `python3 -I`;
  - Docker Hub, only to pull the PostgreSQL image the CI job pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`);
  - GitHub, through your tools, to read runs.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions):
  - a throwaway PostgreSQL in Docker, from that image, on loopback only;
  - a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present;
  - removed afterwards.
- **Never:**
  - dump the environment, or print a credential, password, token, session key or key;
  - call any provider or HDE, send any email, or run any command in `proofs/stream-chat/`;
  - connect to any database but a throwaway one you started under D4's conditions, HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:**
   `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`.
   If any is present, stop and report.
2. **No `STREAM_*` or `PG*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG)'` prints names only. If any is present, stop and report.
3. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
4. **The toolchain:** CPython 3.12.14 as `python3.12`; Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`; Docker if present. Record their versions.
5. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, df8a04c5118d41016c14001308f796fd47626916
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 86a215675e0ad826425e16c14fb6b826664b9c34 HEAD -- .github scripts services apps packages proofs ':!*.md' && echo "the code head under review"
git diff --quiet 86a215675e0ad826425e16c14fb6b826664b9c34 origin/claude/magical-wozniak-yfmmx2 -- .github scripts services apps packages proofs ':!*.md' && echo "no code on the live branch after 86a2156"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-10-sv2-profiles-media.md | grep -c -E '^#+ Exact-head review of Stage A'   # must print 0
```

If any check fails, stop and report. The prompt is stale if any of these holds:
- its commit is not on the live branch;
- a non-Markdown path changed there after `86a2156`;
- this review is already recorded.

**Classify the change** as root `AGENTS.md` requires, with the trusted base policy outside the candidate tree:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
```

Expected: `"full": true`. Anything else: stop and report.

**Then read, completely, at `HEAD`:**
- root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`; `proofs/postgres-ordering/README.md`; `packages/contracts/README.md`;
- the brief, revision 4, and DM-52's, DM-53's and DM-54's reports;
- OD-60 and OD-61 in the owner-direction register;
- the evidence record's "Stage A", whole;
- F02 to F06 in `packages/contracts/production/flows-v1.json`, and the new DTOs in `gapp-api-v1.schema.json`;
- the data model's SV2 rows, unit-of-work table and outbox event table; the contract document's F02 to F06 sections;
- `glow_chat/contact.py`'s `_run`, `_set_profile`, `_decide_consent` and `_contact_state_checks`, and `glow_chat/reads.py`'s `_caller_transaction_open`, which Stage A relies on (read only);
- every file in the code diff, whole: `glow_profiles/operations.py`, `recompute.py`, `requirements.py`, `staff.py`, `settings_store.py`, `views.py`, `contract.py`, `idempotency.py` and `tx.py` above all, with `glow_identity/age.py`, the migrations, `profile_cases.py`, `profile_scan.py` and the workflow's Database proof checks job.

**The runs,** with your GitHub tools:
- 42759801460 and 42769301337: every job's conclusion, the gate's line, the Database job's steps and its profile lines;
- the PR run on PR43's head, if it has finished.

## 3. What to do

1. Write the threat model, then review the diff against the focus, item by item.
2. In a scratch copy of `86a2156`:
   - re-run the checks and the five offline reversals above, and any you doubt;
   - run the profile suite locally under D4 if you can, informational.
3. For each finding: its severity (blocking, should fix, nit), its file and line, the evidence, and whether it falls in a correction class.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 2, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- **the verdict:** approve, approve with nits, or changes required;
- the threat model;
- the findings, in a table: number, severity, correction class or not, file and line, what is wrong, and the evidence;
- the answer to each focus point (1 to 9), one or two lines each;
- the reversals you re-ran, with their results, the local database ones named informational;
- what you ran, and what you could not run or read.
