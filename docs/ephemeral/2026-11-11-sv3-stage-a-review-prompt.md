# SV3 Stage A exact-head review prompt — eligibility and discovery, with a written threat model

- **Owner:** App Manager 11. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 11 November 2026.**
- **Durable brief:** [SV3 — The eligibility, discovery and interactions slice](../planning/sv3-eligibility-discovery-interactions.md), revision 2, "Review plan" (Stage A's items).
- **Where the result goes:** the report Nathan relays. The manager records it in the evidence record, "Exact-head review of Stage A", with a disposition for each finding (fix before the merge, or carry), and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Fable 5.1 at max.** Effort score 3.71 (confidence 0.81); rung probabilities low 0.00, medium 0.00, high 0.08, extra high 0.13, max 0.79, ultracode 0.00. Model probabilities Fable 5.1 0.73, Opus 5.5 0.27, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.64). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.058, Fable 5.1 at extra high 0.095, Fable 5.1 at max 0.577, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.000, Opus 5.5 at high 0.022, Opus 5.5 at extra high 0.035, Opus 5.5 at max 0.213, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-11T23:39:45Z. Nathan picks the cell. (A first sending at 23:39:35Z, whose action text miscounted the prompt's numbered items as sixteen, read the same cell: Fable 5.1 0.70, Opus 5.5 0.30, the same rungs.)
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of PR45's head, which is this prompt's commit (manager workflow, step 6).
- **Deletion condition:** prune after SV3 Stage A's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **exact-head code and security review of SV3's Stage A**: eligibility and discovery, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one exact code head in full, with a written threat model. This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **SV1 and SV2 merged** (PR42 to PR44, `3240ef0`): sign-in, the profile, its settings, consent, the adult check, the birth input, visibility and photos, all sealed until P11.
- **The brief,** `docs/planning/sv3-eligibility-discovery-interactions.md`, revision 2. It applies the Dev Manager's DM-60 conditions, Q1 to Q20, word for word (`docs/continuity/dev-manager/reviews/2026-11-11-dm-60-sv3-brief.md`). It rests on Nathan's directions OD-12, OD-55, OD-60 and OD-61 and on the matrix recheck (`docs/testing/evidence/2026-11-11-sv3-matrix-recheck.md`).
- **Stage A decides who may see whom.** It builds:
  - pair eligibility over the ORM: the trusted adapter's pair read, every predicate for both members, failing closed (D2, D3);
  - the two-way rule over the four fields, age in whole years from the age state's date, and distance in the viewer's direction (D4, D5);
  - recommended then broader pages, the compatibility port's fixture adapter selected only by the proof's settings, and a keyed tie-break (D6, Q2);
  - bounded batches and pages, cursors bound to viewer, collection, batch and offset, one stale response, consumption's exclusions, and one batch per viewer and collection, in migration 0010 (D7, Q3 to Q5);
  - the page route and the card's additive DTOs (D13, Q12);
  - a discovery suite on a fourth disposable database (D14).

  Likes, passes, matches, unmatch and block are Stage B's.
- **The implementation** (branch `claude/loving-maxwell-cqu7eq`, code head `ad9ff08`, records `4dee875`; the evidence record, "Stage A"): 70 reversals, of which 69 failed as intended and one is explained. Its own push run was never dispatched by GitHub (the record's diagnostic).
- **The manager verified it** ("Manager verification of Stage A") and integrated it by fast-forward. It raised **V1**, the tie-break key's pads passed as SQL parameters, and **V2**, about 222 statements per page.
- **The run of record** is PR45's pull-request run 43113579295 on `88f9299`: all eight jobs passed, and the gate printed `Application checks passed`. The discovery suite passed 32 of 32 in 52.4 s, both scans clean, and the second run was refused with its counts unchanged.
- **Codex** reviewed `88f9299` with no findings.

**The code head under review is `ad9ff08`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `ad9ff08` (the start gate checks this).

**Your scope:**
- **The code:** `git diff 3240ef0acca7983e5b60b9a111be371ed5a16b74 ad9ff081e26535ab89eb1187c7b69ca96fac2ef4`, its 37 non-Markdown paths, read in full at `ad9ff08`:
  - `services/api/glow_discovery/` (11), new;
  - `glow_persistence/models.py` and migration `0010_batch_collection`;
  - `services/api/tests/` (5) and `services/api/pyproject.toml`;
  - the contract (`gapp-api-v1.schema.json`, `openapi.json`, `flows-v1.json`, `corpus/shared-v1.json`, `tests/test_transition_contract.py`) and the regenerated outputs in `apps/mobile/src/contracts/generated/` (3);
  - `proofs/postgres-ordering/` (9): the discovery suite, its settings, scan, support, URL configuration, offline tests, `__main__.py` and `pyproject.toml`;
  - `.github/workflows/foundation.yml`: the Database proof checks job's new steps.
- **The records, as claims about the code:**
  - the evidence record, whole: "Stage A", its diagnostic, and "Manager verification of Stage A";
  - the data model's batch and entry rows and its eligibility read;
  - the contract document's F07 index row, its server mapping and its rewritten `location_label` sentence;
  - the fixtures notes' server lines (`discovery-fixtures.md`, `reciprocal-eligibility-fixtures.md`, `trusted-eligibility.md`);
  - the contracts README's SV3 section, and the P11 plan's SV3 entries (DB04, DB10, DB11);
  - the CI policy's new discovery sentences (`docs/operations/ci-and-branch-policy.md`), against the workflow.
- **The runs:** 43113579295 (the run of record), and 43096394432 and 43100390225 (the session's, for the diagnostic).
- **Out of scope:**
  - code Stage A does not change (`glow_chat`, `glow_identity`, `glow_profiles`, `glow_api`, `glow_domain`). A finding there is reported as pre-existing, not as a defect of this item;
  - Stage B's items (D9 to D12: like, pass, the match, unmatch, block, resurfacing, undo and rematch's limit);
  - the items the brief carries to P07, P08, P09 and SV4 (Q17 to Q20). Report only where the code contradicts what the carry says.

**The threat model** (the brief's "Review plan"; DM-31 item 3: who may see whom is a security and privacy boundary). Write it in your report:
- **Assets:**
  - which members can see each other: each predicate, in both directions;
  - a member's private values: birth date and age state, consent, the four fields' own values and "show me" sets, own words and display flags, home area and its internal point, age range and distance choice, account and profile states;
  - who has blocked whom, liked or passed whom, and matched with whom;
  - the order of a batch and its band boundaries (Q2), and the tie-break's key;
  - the cursor's binding, and a batch's freshness and lifetime;
  - the card's contents, and a photo's delivery reference;
  - the discovery suite's `SECRET_KEY` and JWT key, and the run's database credentials.
- **Actors:**
  - an anonymous prober;
  - a holder of another member's stolen token (SV1's actor);
  - a signed-in member probing with filters, repeated pages and forged or reused cursors;
  - a member who is not adult, has withdrawn consent, is paused, restricted, suspended or deleted, or has been blocked;
  - a member who narrows a field to learn others' values, including in a tiny population (DM-51 M9);
  - a console publication of a setting the selection reads;
  - anyone who reads this public repository's CI logs and artifacts, or a server's statement logs.
- **Entry points:**
  - the page route `api/v1/discovery/page` under SV1's actor (`PageRequest`; `CandidateCardPage`);
  - the trusted adapter's pair read (`eligibility.py`), which Stage B's actions will use;
  - migration 0010;
  - the discovery suite's job steps.

For each threat, give the code that stops it and the test that proves it. It covers the brief's "Review plan" items for seeing:
1. each predicate, both directions, failing closed: a missing row, a NULL and an unknown never pass;
2. **the consistent view** (D2, Q1): the selection is one statement, each page's recheck is one statement, and a page with a cursor writes nothing;
3. **D8's disclosure rules** in every response, error and validation message: no reason, no count, no other member's private value, and an unreciprocated like or a block's direction never visible;
4. **the cursor's binding** (Q4): forged, another viewer's, the other collection's, expired, a viewer whose versions changed, a changed policy version, and a deleted batch, each refused with the one stale response before any row is read;
5. **the batch's policy version** (Q3): a publication of any setting the selection reads makes the batch stale;
6. **consumption** (Q5): a liked or passed candidate, and the other member of any pair with a `Match` row in any state, excluded from the selection and dropped at each recheck; one batch per viewer and collection;
7. **the keyed tie-break** (Q2), with **V1**: can a client compute the order? Can any logging path record the pads? This covers Django's query logging, the proof's DEBUG capture and PostgreSQL's parameter logging, such as `log_min_duration_statement` and `log_parameter_max_length`. Rule whether passing the pads as statement parameters is acceptable, a should-fix, or a carry, and name the alternative you would prefer;
8. **the card** (Q12): "looking for" always; gender, orientation and relationship status only while shown; own words for display only; the area's name; never a "show me" set, a filter, an area ID, an internal point, a distance or a birth date; approved photos only, through SV2's `delivery_reference`;
9. **age and distance:** the SQL whole-years rule equal to `glow_domain.identity.whole_years` at the leap-day cases; distance in the viewer's direction only; a distance choice the setting does not offer fails; no distance or coordinate ever selected or returned;
10. **the seal:** the served runtime imports none of `glow_discovery`, and selects no fixture compatibility provider;
11. **the proof's secret handling** in the discovery suite's steps, its scans, and what is uploaded.

**The focus:**
1. **The threat model above,** each threat with its stopping code and its test.
2. **The Dev Manager's conditions met in code:** Q1 to Q6, Q12 and Q13 for Stage A (DM-60), and the brief's D2 to D8, D13 to D15 and D19. Name any condition the code does not meet.
3. **The session's findings and design details** (the record's "Findings, deviations and limits"), against the code, each accepted or a finding:
   - `D3.candidate_adult`'s reversal not failing;
   - one band from the fixture;
   - no `CompatibilitySnapshot` written;
   - `discovery.resurfacing` in the policy version but not applied;
   - a 403 for an ineligible viewer;
   - one 409 `stale_version` body for every stale cause;
   - the card's repeated `profile_id`;
   - photos read after the page's transaction.
4. **V2, statements per page** (222 to 224 at 1,000 members, mostly SV2's `delivery_reference` once per photo): is the bound sound, and is it a nit, a should-fix or a P11 item (DB11)?
5. **No test is weakened or vacuous:**
   - each reversal the record names fails its case;
   - no case could pass while the behaviour it guards is wrong. Above all: the predicates in both directions, the stale cases, consumption, the tie-break's key, the card's contents and the log capture;
   - the sealed-runtime test is not defeated by a plausible edit.
6. **The contract:**
   - every existing DTO is unchanged;
   - the only registry change is F07's added `CandidateCardPage` response with its `owner` projection;
   - the generated outputs match the schemas when regenerated.
7. **The migration:** 0010's added non-null field with a one-off default on a table with no rows, its check and its unique constraint. Is it safe for P11's empty target, and what would a populated target need?
8. **The workflow and dependencies:** the complete `foundation.yml` diff touches only the Database proof checks job's steps. Every lock and requirement file is unchanged. Read the job's steps and logs in run 43113579295: the discovery suite runs on its own database, as the CI policy's sentences describe.
9. **The records:** every claim in the texts listed in the scope holds against the code and the runs.

**Re-run, at least,** in a scratch copy of `ad9ff08`:
- **The API's checks:** `manage.py check`, `manage.py test tests`, `ruff` and the configured `mypy`. The contract tests. The proof's offline tests, `ruff` and `mypy`.
- **The contract outputs:** `npm run check` in `packages/contracts`, after `npm ci --ignore-scripts` there and in `apps/mobile`, since the corpus test loads the mobile app's generated validators.
- **Four offline reversals, at least:**
  - the cursor's MAC without the collection;
  - the card ignoring a field's `shown` flag;
  - the runtime's URL configuration importing `glow_discovery`;
  - one of your own choosing, against a claim you doubt.
- **The discovery suite, informational:** on a throwaway PostgreSQL under P06.DB's D4, if Docker allows. It is informational, and you name it so. If you can run it, add database reversals you doubt, such as:
  - a block read in one direction only;
  - the recheck split into two statements;
  - a narrowed set matching "not stated";
  - a `Match` row in `unmatched` not excluding.

**What comes after this review: the correction classes.** Report every finding with its severity. A correction pass takes every blocking finding, and any should-fix finding that could do any of these:
- let a member see, or be shown to, someone a predicate in either direction excludes;
- let a member learn another member's private value, a reason for exclusion, a count, an unreciprocated like or a block's direction;
- let a forged, stale, expired or other viewer's or collection's cursor read a page;
- let a publication of a setting the selection reads leave a batch fresh;
- let a liked, passed or matched candidate, or a blocked one, appear in a page;
- let a client, a log or an artifact obtain the order's key or compute the order;
- let the card carry a value it must not, or a photo that is not approved;
- let the served runtime import Stage A's code, select a fixture provider, or add a package;
- let a test pass where it should fail, or fail where the code is right;
- leave a Dev Manager condition unmet;
- make a record claim more than the code, the tests or the runs show.

Everything else goes into the records. For each finding, say whether it falls in one of these classes.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 11. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - **Scratch work goes in a copy outside the repository,** never the checkout (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
- **Network:**
  - PyPI and the npm registry, for hash-locked installs in a scratch copy;
  - Docker Hub, only to pull the PostgreSQL image the CI job pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`);
  - GitHub, through your tools, to read runs.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions):
  - a throwaway PostgreSQL in Docker, from that image, on loopback only;
  - a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present;
  - removed afterwards.
- **Never:**
  - dump the environment, or print a credential, password, token, session key or key;
  - read, print or use the value of any `AWS_*` variable (section 1);
  - call any provider or HDE, send any email, or run any command in `proofs/stream-chat/`;
  - connect to any database but a throwaway one you started under D4's conditions, HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:**
   `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`.
   If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*` or `CF_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_)'` prints names only. If any is present, stop and report.
3. **Three AWS names are expected:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_CA_BUNDLE` (DM-57 and DM-58). `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values. If any other `AWS_*` name is present, stop and report.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
5. **The toolchain:** CPython 3.12.14 as `python3.12`; Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`; Docker if present. Record their versions.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API). No `AWS_*` name passes.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, 3240ef0acca7983e5b60b9a111be371ed5a16b74
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet ad9ff081e26535ab89eb1187c7b69ca96fac2ef4 HEAD -- .github scripts services apps packages proofs ':!*.md' && echo "the code head under review"
git diff --quiet ad9ff081e26535ab89eb1187c7b69ca96fac2ef4 origin/claude/magical-wozniak-yfmmx2 -- .github scripts services apps packages proofs ':!*.md' && echo "no code on the live branch after ad9ff08"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md | grep -c -E '^#+ Exact-head review of Stage A'   # must print 0
```

If any check fails, stop and report. The prompt is stale if any of these holds:
- its commit is not on the live branch;
- a non-Markdown path changed there after `ad9ff08`;
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
- the brief, revision 2, and DM-60's report;
- OD-12, OD-55, OD-60 and OD-61 in the owner-direction register;
- the evidence record, whole;
- F07 in `packages/contracts/production/flows-v1.json`, and `PageRequest`, `CandidatePage`, `CandidateProfile`, `CandidateDetails`, `CandidateCard` and `CandidateCardPage` in `gapp-api-v1.schema.json`;
- the contract document's "Pagination, idempotency and stale state", "P05.3 internal interaction result and identity bridge" and "Compound actions and model projections";
- P05's notes: `docs/architecture/discovery-fixtures.md`, `interactions-fixtures.md`, `reciprocal-eligibility-fixtures.md` and `trusted-eligibility.md`;
- the code SV3 builds beside (read only): `glow_chat/contact.py`'s `block`, `unblock` and `unmatch`; `glow_profiles/requirements.py`, `settings_store.py`, `idempotency.py`, `areas.py` and `media.py`'s `delivery_reference`; `glow_domain/identity.py`'s `whole_years`, `profile_fields.py` and `trusted_eligibility.py`;
- every file in the code diff, whole: `glow_discovery/predicates.py`, `pages.py`, `keys.py`, `eligibility.py`, `policy.py`, `contract.py` and `views.py` above all, with the models, the migration, `discovery_cases.py`, `discovery_support.py` and `discovery_scan.py`.

**The runs,** with your GitHub tools: 43113579295, every job's conclusion, the gate's line, the Database job's steps and its discovery lines; 43096394432 and 43100390225, as the diagnostic describes them.

## 3. What to do

1. Write the threat model, then review the code against the focus, item by item.
2. In a scratch copy of `ad9ff08`:
   - re-run the checks and the offline reversals above, and any you doubt;
   - run the discovery suite locally under D4 if you can, informational.
3. For each finding: its severity (blocking, should fix, nit), its file and line, the evidence, and whether it falls in a correction class.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- **the verdict:** approve, approve with nits, or changes required;
- the threat model;
- the findings, in a table: number, severity, correction class or not, file and line, what is wrong, and the evidence;
- the answer to each focus point (1 to 9), one or two lines each, with V1's and V2's rulings;
- the reversals you re-ran, with their results, the local database ones named informational;
- what you ran, and what you could not run or read.
