# SV2 Stage A correction C2 prompt — a failing date at both writers, the history limit, the sensitive consent's version, the profile edit's lapse, the withdrawal's rows, invalid bodies and the review's test gaps

- **Owner:** App Manager 10. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 10 November 2026.**
- **Durable brief:** [SV2 — The profiles and media slice](../planning/sv2-profiles-media.md), revision 5, "Stage A, correction C2".
- **Where the result goes:**
  - the session's changes, and the record's new section "Correction C2" in `docs/testing/evidence/2026-11-10-sv2-profiles-media.md`, on the session branch;
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification, and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.33 (confidence 0.74); rung probabilities low 0.00, medium 0.03, high 0.62, extra high 0.34, max 0.01, ultracode 0.00. Model probabilities Fable 5.1 0.03, Opus 5.5 0.96, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.95). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.001, Fable 5.1 at high 0.019, Fable 5.1 at extra high 0.010, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.029, Opus 5.5 at high 0.595, Opus 5.5 at extra high 0.326, Opus 5.5 at max 0.010, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.006, Sonnet 5.5 at extra high 0.003, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-10T16:22:49Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The brief's revision 5 applies DM-55's Z1 to Z17 as written, and DM-55 says they need no read before this prompt (section 2). This prompt authorizes no credential use and no live provider action.
- **Which session:** C1's session, on its branch `claude/funny-lamport-5f2s1u`, is the natural home: it wrote C1, its tests and its reversals. A new session can run it equally well, on its own branch.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of the commit that holds it (step 6). Then:
  - the manager's verification;
  - Codex on C2's head;
  - a full exact-head code and security review of the corrected head, with a written threat model, not a delta review (DM-55, section 10);
  - the Dev Manager's pre-merge read.
- **Deletion condition:** prune after SV2 Stage A's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are **correction C2 of SV2's Stage A**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **Stage A's implementation** (code head `b97bc15`) built the server's profile in `services/api/glow_profiles`, sealed, with a profile suite on a third disposable database in the Database proof checks job.
- **Correction C1** (code head `86a2156`, records `f54545c`, integrated at `6e5d0d1`, on PR43; run of record 42769301337) added:
  - D9's one recompute at the end of every requirement writer;
  - a birth input whose date is under 18, refused and not stored while its rerun commits;
  - two kinds of registry entry;
  - `glow_profiles` in CI's mypy.
- **The exact-head review of `86a2156`** found no blocking finding. It found:
  - one code defect in a correction class;
  - the two writers disagreeing on a failing date;
  - six test gaps where a wrong change passes every test;
  - eight record claims;
  - five questions for the Dev Manager.

  Its findings and the manager's dispositions are in the record, "Exact-head review of Stage A". Codex's P2 on `40db2c2` (`operations.py:1019`, a future birth date) is the same point as finding 2.
- **The Dev Manager ruled in DM-55** (`docs/continuity/dev-manager/reviews/2026-11-10-dm-55-sv2-stage-a-review.md`), with Z1 to Z20 in given words. The brief's revision 5 applies Z1 to Z17, and its section "Stage A, correction C2" lists your ten items. In short:
  - **A future date is invalid input at both writers** and changes nothing.
  - **A date under 18 from a self-declared adult** is checked first at both writers, before their other refusals, and refused `forbidden` with no idempotency record, while the reset commits.
  - **Earlier birth input revisions are not erased:** that is carried to P07.

**The brief's "Stage A, correction C2" is your specification.** Read it with these parts of revision 5, as they word them:
- D2's fixed limits, D4, D6, D7, D8 and D9;
- D11's "The flow registry";
- checks 1, 2, 6, 7 and 9, and the "Review plan";
- DM-55's sections 3, 5, 6, 7, 8 and 10.

Read them whole. Where this prompt summarizes them, the brief wins.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 10. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only "Stage A, correction C2"'s owned paths:
    - `services/api/glow_profiles/**`, and SV2's own modules in `services/api/glow_domain/` (`profile_fields.py`, `profile_settings.py`, `identity_verification.py`);
    - `services/api/tests/`: SV2's profile tests;
    - `packages/contracts/production/flows-v1.json`: item 7's entries only; `packages/contracts/tests/test_transition_contract.py`: their examples and the registry prerequisites' pins; `packages/contracts/README.md`: SV2's section;
    - `proofs/postgres-ordering/**`: the profile suite, its scan, its tests and the README's SV2 section;
    - `docs/architecture/data-model.md`: SV2's rows. `docs/architecture/production-contracts.md`: F02 to F06's index rows and server mapping, and the SV2 paragraph's brief revision;
    - `docs/testing/p11-deferred-acceptance.md`: the "SV2 Stage A" entry only, not the entries DM-54 (K4) and DM-55 (Z20) added;
    - the record's new section "Correction C2";
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule** (DM-55, section 10). Stop and report, with no further change, if the correction seems to need any of these:
  - a model, migration or DTO change. No schema change is expected, so the generated contract outputs do not change either;
  - a change to `glow_chat`, `glow_identity` (`age.py` included), `glow_api`, the workflow, a lock or a dependency. A reversal's temporary edit of `age.py` is allowed, and must be undone: `age.py` is unchanged at your head;
  - a change to an existing registry entry, or a role the oracle does not authorize;
  - more than the Database proof checks job's 30-minute timeout.
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished. Push your records commit only after the run of record has finished. The workflow runs on pushes to `claude/**` and `ccr-**`; if your branch is named otherwise, say so in the report, since no run starts.
- **Network:**
  - PyPI and the npm registry, for `pip install --require-hashes` and `npm ci --ignore-scripts` from the existing locks;
  - Docker Hub, only to pull the PostgreSQL image the CI job pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`) for a local run.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions):
  - a throwaway PostgreSQL in Docker, from the CI job's pinned image, on loopback only;
  - a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present;
  - removed afterwards.

  Local passes are "iteration, not evidence"; the run of record is CI's.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, password, code, token, session key or signing key, in any form;
  - make test data that looks real: accounts, emails, names, birth facts, places and coordinates are synthetic and obviously so (`@example.invalid`);
  - call any provider or HDE, send any email, or run any command in `proofs/stream-chat/`;
  - connect to any database but a throwaway one you started under D4's conditions. Run `migrate` or `makemigrations` only through the proof's own commands against such a database, or under the static registry's dummy settings;
  - connect to HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script;
  - weaken or delete a test to make the suite pass.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:**
   `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`.
   If any is present, stop and report.
2. **No `STREAM_*` or `PG*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG)'` prints names only. If any is present, stop and report.
3. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them.
4. **The toolchain:** CPython 3.12.14 as `python3.12`; Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, first on PATH; Docker. Record `python3.12 --version`, `node --version`, `npm --version` and `docker --version`.
5. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API). The proxy and CA variables pass by reference, never printed.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # C1's session: claude/funny-lamport-5f2s1u; <START_SHA> already contains its f54545c
git rev-parse HEAD                                  # must print <START_SHA>
git diff --name-only 86a215675e0ad826425e16c14fb6b826664b9c34 HEAD -- .github scripts services apps packages proofs | grep -v -E '\.md$'   # must print nothing: the code is 86a2156's
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/api proofs/postgres-ordering packages/contracts .github docs/architecture docs/testing/p11-deferred-acceptance.md 'docs/testing/evidence/*sv2*'   # must print nothing
grep -c -E '^#+ Correction C2' docs/testing/evidence/2026-11-10-sv2-profiles-media.md   # must print 0
grep -c 'Stage A, correction C2 (DM-55)' docs/planning/sv2-profiles-media.md            # must print 1
```

If a check fails, stop and report. The prompt is stale if any of these holds:
- `<START_SHA>` is not on the live manager branch;
- an owned path changed there after it;
- "Correction C2" is already recorded.

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`; `proofs/postgres-ordering/README.md`; `packages/contracts/README.md`;
- **the brief,** revision 5: the parts named above, and "Stage A, correction C2";
- **DM-55's report,** whole;
- **the record:** "Correction C1", "Exact-head review of Stage A" and DM-55's rulings after it;
- **the code you change:**
  - `glow_profiles/operations.py`: `adult_check`, `_age_transition`, `save_birth_input`, `_refuse_failing_birth_input`, `_invalidate_birth_input`, `_sensitive_accepted`, the field and preferences writers, the sensitive consent's writer, `_withdraw_sensitive_data` and the profile edit;
  - `glow_profiles/recompute.py`, `settings_store.py` (`read_shared` and `publish`), `contract.py` (`number`, `text` and `parse`), `views.py` (`_body` and `handle_exception`), `tx.py` (`run`, `lock_account`, `Refused`) and `idempotency.py`;
  - `glow_domain/profile_settings.py` (`_history_refusals`) and `profile_fields.py` (`text_ok`, `NOT_STATED`);
- **read only:** `glow_identity/age.py`'s `age_years`;
- **the registry:** `flows-v1.json`'s F02, `transition_contract.py`'s `authorized`, and `tests/test_transition_contract.py`;
- **the tests you change:**
  - the profile suite: `profile_cases.py`, `profile_scan.py`, `profile_support.py` and `__main__.py`, with `tests/test_profile_offline.py`;
  - the API's `test_profiles_offline.py`, `test_profile_recompute.py`, `test_profiles_sealed_runtime.py` and `test_profile_contract.py`.

## 3. What to do

1. **The items of "Stage A, correction C2", in order.** For each: the change, its tests, and its reversals. A reversal is a temporary edit that must make a test fail; run it, then undo it. Record the edit and the failing output. Database cases go in the profile suite on the disposable database, and offline ones in the API's or the proof's offline tests.
   - **Item 1, a future date and a date under 18, at both writers** (Z1 to Z4; DM-55, section 3, "What C2 builds"):
     - **The eligibility step:** for a self-declared adult, the date's outcome comes before the stale version check. A future date is refused `invalid_request` and changes nothing. A date under 18 is refused `forbidden`: the operation returns the refusal without raising, the reset commits, and no idempotency record is stored.
     - **The birth input:** the date's outcome comes right after the adult-check gate, before the onboarding consent, the stale version and the birth time. A future date is refused `invalid_request` and changes nothing.
     - **A replay or a key conflict** is still decided first, at both.

     **Tests:**
     - **At each writer, for a self-declared adult:**
       - a future date answers 400 and changes no row;
       - a date under 18 answers 403. The age state becomes `unknown` with no date, the current birth input `missing` with its mapping `pending`, and a visible profile `incomplete`, each with its event. No idempotency record is stored, and a retry is refused and changes nothing.
     - **A date under 18 behind each later refusal,** each answering 403 with the reset: a stale version at both writers; at the birth input, a birth time not given and a lapsed onboarding consent.
     - **For an `unknown` account,** the existing refusals still hold.

     **Reversals:**
     - the date check placed after the stale version check at one writer (name which);
     - a future date resetting the account at the eligibility step;
     - an idempotency record stored with the eligibility step's refusal;
     - that refusal raised, so the reset rolls back.
   - **Item 2, the history setting's limit** (Z6, Z7): a history publication that changes the consent version it names while making nothing more readable is refused, and nothing is written. Use `MORE_READABLE_NEEDS_CONSENT` or one new refusal code, and name it in the record.

     **Tests:**
     - the two-step path is refused at its first step;
     - the direct change is still refused;
     - a new onboarding version, then a more readable change naming it, is allowed.

     **Reversal:** the new refusal removed. The two-step case must fail.
   - **Item 3, the sensitive-fields consent's current version** (Z9, Z10):
     - each sensitive save needs the consent accepted at its current version;
     - the consent's pointer is read in the same `read_shared` call as the save's other settings, after the account row lock and in name order;
     - the refusal stays `forbidden`, `sensitive_consent_required`.

     **Tests:**
     - a sensitive field value, orientation's own words and a narrowed sensitive set are each refused before acceptance, after a withdrawal, and at an old version;
     - a save that carries no sensitive data still succeeds at an old version.

     DM-55's section 5 consequence for `PreferencesIntent` is the rule, not a defect.

     **Reversals:**
     - the version ignored: the old-version case fails;
     - "any accepted decision": the after-withdrawal case fails.
   - **Item 4, a lapse the profile edit finds** (Y4; Z12; DM-55, section 6). In the profile edit:
     - a demotion is the owner's `edit` only when the edit itself clears the summary, whatever else is missing. The display name cannot be cleared;
     - any other demotion is `requirement_removed`, a transition of its own. It bumps the profile's version and the account's `eligibility_version` and emits `profile_demoted`, as in every other writer.

     **Tests:**
     - an edit that clears the summary is `edit`, with no `profile_demoted`;
     - an edit that finds a lapse it did not cause (a new onboarding consent version) is `requirement_removed`, with `profile_demoted` and both versions bumped;
     - an edit that clears the summary while another requirement has lapsed is `edit`.

     **Reversal:** every profile-edit demotion back to `edit`. The lapse case must fail.
   - **Item 5, the withdrawal's field rows** (Z13, Z14): each of the member's orientation and relationship status rows is set to "not stated" in place:
     - `value_ids` `["not-stated"]`, no own words, its display flag off and its setting version unchanged;
     - the row's version bumped, and `profile_field_changed` emitted for it;
     - a row that already holds "not stated" with no own words and its flag off is left as it is, with no event;
     - the sets' reset to all and the idempotency records' deletion are unchanged.

     **Tests:** after a withdrawal:
     - each row exists in that state, with its event;
     - every earlier `profile_field_changed` event names an existing row;
     - an already-reset row is unchanged, with no event.

     **Reversals:**
     - the rows deleted;
     - the flag kept;
     - an event emitted for an unchanged row.
   - **Item 6, bodies that must answer 400:** in the brief's words, "A body the parser cannot hold, such as an integer too large for its number check or nesting deeper than the parser allows, and a text holding U+0000, which the database cannot store, are refused `invalid_request` (400) with the contract's `Error`, like any other invalid body. No value is echoed."

     **Tests**, offline:
     - a coordinate given as a 321-digit integer;
     - 10,000 nested arrays;
     - U+0000 in a stored text.

     Each must answer 400 `invalid_request` as JSON, with no part of the body in the response.

     **Reversals:** each guard removed. Its case must fail.
   - **Item 7, two F02 entries under W5:**
     - `accept` from `accepted` to `accepted`;
     - `accept_sensitive` from `accepted` to `accepted`.

     Each is `owner`, with the policy `consent_current`. Each gets an allowed example in `tests/test_transition_contract.py` (the current version, newer than the one accepted) and a forbidden one (an old version). No existing entry changes. The contract document's F02 index row and the package README's SV2 section list them.

     **Reversal:** one entry's role changed to one the oracle does not authorize. Its allowed example must fail.
   - **Item 8, the test gaps,** each with a reversal that fails its new case:
     - **The account row lock:** a case showing that a second writer for the same account waits for the first's commit. **Reversal:** `lock_account` without its row lock.
     - **The scans and the table search:** they match each fixture value in every form the code could print, and coordinates at a lower precision. The static logging guard covers `glow_identity/age.py`, and no case prints a fixture date in prose. Today "29 February 2008" is in the public log and artifact while the scan reports 0; find where it is printed and stop it.

       **Reversals:**
       - coordinates stored at four decimals;
       - a birth date logged by `age.py`, as a temporary edit, then undone.
     - **Every command's stored digest:** each is checked as keyed. **Reversal:** the birth input storing an unkeyed SHA-256.
     - **The static guards:** they forbid a queryset `.update(state=…)` on a profile in `glow_profiles`, and a refusal reason built with `Result(…)` from a value. **Reversal:** each pattern inserted.
   - **Item 9, finding 15's test items,** each with its reversal:
     - `test_profiles_sealed_runtime.py` asserts the `refused` it computes;
     - the scan's verdict reads its own result line, not the word "clean" anywhere in the log;
     - the suite's case count is pinned;
     - the registry prerequisites SV2 added to the contract document's list of trusted test prerequisites are each pinned by a contract test. The review counted four; record the number you find;
     - **`age_years`** (Z16, Z17) gets a profile-suite case: whole years for a self-declared adult, `None` while `unknown`, and an integer, never the date. **Reversal:** `age_years` returning the date, as a temporary edit of `age.py`, then undone.
   - **Item 10, the records** (finding 8):
     - **the record's new section "Correction C2"** corrects the eight claims the review lists (the record, "Exact-head review of Stage A", finding 8), each with the true statement. Stage A's and C1's sections stand as written. It also records the 405 a wrong method answers (Z20 carries it to P11);
     - the data model's `AccountAgeState` and `ProfileFieldChoice` rows, and the contract document's F02 to F04 sentences, follow items 1, 4 and 5;
     - every owned record that cites the brief's revision 3 or 4 for SV2 cites revision 5;
     - the P11 plan's "SV2 Stage A" entry names C2's run of record;
     - the package README's SV2 section lists item 7's entries.
2. **The local checks:**
   - **API,** in `services/api`: `python3.12 -m venv .venv` and `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`. Then, with `GLOW_ENV=test`: `manage.py check`, `manage.py test tests --verbosity 2`, `ruff check .`, `ruff format --check .` and `mypy`;
   - **the contracts:**
     - the Python contract tests: `PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests -v`, from `services/api`;
     - `npm run check` in `packages/contracts`, after `npm ci --ignore-scripts` there and in `apps/mobile`. No generated file may change;
   - **the proof,** in `proofs/postgres-ordering`: the same install, then `python -m unittest discover -s tests -t . -v`, `ruff check .`, `ruff format --check .` and `mypy`;
   - **the profile suite** on a local throwaway database under D4, if Docker allows, as iteration.
3. **The run of record.** Commit and push your code, then wait for its Foundation run to finish (the push rule). Read it with your GitHub tools:
   - every job's conclusion, and the gate's line (`Application checks passed`);
   - the API and proof test counts;
   - the API job's mypy line;
   - the profile suite's count and time, the profile phase's duration and both scans' lines;
   - the second profile run's refusal and its counts;
   - whether a toolchain retry fired.

   If it fails, stop and report the failing job and its log lines. Do not re-run it.

## 4. The record

Add a section `## Correction C2` at the end of `docs/testing/evidence/2026-11-10-sv2-profiles-media.md`, holding:
- the start gate's results, the environment check (names only) and the toolchain versions;
- for each item: the files, the tests, the reversals and their failing output;
- **for the threat model:**
  - the order of each age writer's checks;
  - what each refusal commits and stores;
  - the sensitive saves' consent read and its lock order;
  - the withdrawal's rows and events;
  - the parse refusals;
- the eight corrected claims;
- every command you ran, with its result line;
- the run of record's ID, each job's result, the counts, the profile phase and whether a retry fired;
- what you could not run, and why.

Commit each logical step with a clear message ending in the session's attribution lines. Push the records commit only after the run of record has finished. Then confirm:
- `git status` is clean;
- `git diff --name-only <START_SHA> HEAD` lists only your owned paths.

## 5. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch, your code head and records head;
- the start gate's and the environment check's results;
- for each of items 1 to 10: what changed, its tests, and each reversal's result;
- each local check's result;
- the run of record: its ID, every job, the gate's line, the counts, the profile phase, the mypy line and whether a retry fired;
- anything that met the stop rule, every deviation, and what you could not run.
