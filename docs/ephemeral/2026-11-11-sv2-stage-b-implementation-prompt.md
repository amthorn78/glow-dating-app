# SV2 Stage B prompt — photos on private R2's ports, the photo requirement, and one pointer order, proven on disposable PostgreSQL

- **Owner:** App Manager 10. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 11 November 2026.**
- **Durable brief:** [SV2 — The profiles and media slice](../planning/sv2-profiles-media.md), revision 7.
- **Where the result goes:**
  - the session's changes in Stage B's owned paths, and its record, under the heading `## Stage B` in `docs/testing/evidence/2026-11-10-sv2-profiles-media.md`, on its own branch;
  - the run of record: the Foundation run on its last code commit, with the profile phase;
  - the manager adds its verification to the record and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 3.02 (confidence 0.65); rung probabilities low 0.00, medium 0.03, high 0.19, extra high 0.51, max 0.26, ultracode 0.01. Model probabilities Fable 5.1 0.10, Opus 5.5 0.89, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.85). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.003, Fable 5.1 at high 0.019, Fable 5.1 at extra high 0.051, Fable 5.1 at max 0.026, Fable 5.1 at ultracode 0.001, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.027, Opus 5.5 at high 0.169, Opus 5.5 at extra high 0.454, Opus 5.5 at max 0.231, Opus 5.5 at ultracode 0.009, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.002, Sonnet 5.5 at extra high 0.005, Sonnet 5.5 at max 0.003, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-11T01:18:49Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs.
  - The brief's revision 7 applies DM-57's U1 to U5 and U8 to U10 as written. DM-57 says they need no read before this prompt (DM-57, section 2).
  - This prompt authorizes no credential use and no live provider action. The identity keys, the profile suite's `SECRET_KEY` and the database password are generated for one run and destroyed with it.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Then, in order:
  - the manager's verification;
  - the PR and Codex's review of its head;
  - an exact-head code and security review with a written threat model (the brief's "Review plan": the media items, D19, and Stage B's changes to Stage A's code);
  - the Dev Manager's read, before the merge, of the data model's and contract's rewritten texts, and the CI policy's paragraph if it changes.
- **Deletion condition:** prune after Stage B's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **implementation session for SV2's Stage B**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What Stage B is.** Stage A built the server's profile, merged with PR43 at `4dc2061`. Stage B adds photos, sealed from the served runtime until P11:
- photos in **private R2 object storage** (Nathan, OD-62), behind a storage port and a processing port with **fixture adapters only**: no R2 call, no credential, no SDK;
- the upload grant, the quarantine path with G-02's seam and the hold port, Glow's own processing at the system review step, the automated check's approval and rejection, staff restriction on a report, reorder, removal and its acknowledgment, and the delivery reference (D10);
- the photo requirement in completion, with the recompute and the demotion (D9);
- F05's `approve` and `reject` becoming `system` (D11);
- **one pointer order in every transaction** (D19), in Stage A's code and Stage B's, with its check;
- the profile suite's new cases (D12).

There is no provider, deployed URL, real member, real photo, HDE call or stored credential.

**The brief, `docs/planning/sv2-profiles-media.md`, revision 7, is the specification.** Stage B builds what its section "Stage B (revision 6)" lists:
- Outcome item 7, and items 8 to 11 for photos;
- D10 (as revised for R2), D19, D9's photo requirement, D2's media policy, and D11's F05 changes;
- acceptance checks 10 and 13, with check 9's photo requirement and checks 11 and 12 for the new routes.

Much of its text is the Dev Manager's words (DM-52 to DM-57), checked against the code. Follow them exactly. Where this prompt summarizes the brief, the brief wins.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 10. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only the brief's "Owned paths (the sessions)", for Stage B's parts. Stage B may change Stage A's code in those paths where D19, D9 or C3's carried guards need it;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule** (the brief's "Stage B (revision 6)", with Stage A's). Stop and report, with no further change, if any of these holds:
  - **an owned path:** the work needs a path outside the owned paths. That includes:
    - `services/api/glow_api/` (the seal);
    - `services/api/glow_chat/`: you call its writers, never change them;
    - `services/api/glow_identity/`: Stage B changes nothing there;
    - any `apps/` path other than `apps/mobile/src/contracts/generated/`, and those files written other than by `npm run generate --prefix packages/contracts`. That includes a mobile source, test or fixture that would have to change for the Mobile checks job to pass;
    - `scripts/`, any other workflow job, the `Dockerfile`, an environment template, or the runtime scope's `requirements.in` and `requirements.lock`;
    - the CI policy (`docs/operations/ci-and-branch-policy.md`), which is the manager's;
  - **the dependency set** (D14): any new Python or npm package, or a changed pin. That includes an S3 or R2 client, and any decoder or image library: the fixture adapter has no real decode path (PV04's);
  - **a provider:** any call to R2, Cloudflare or any other service, or any credential;
  - **a design change:**
    - a `glow_chat` writer to behave differently;
    - an existing DTO to change;
    - an existing registry entry to change, other than F05's `approve` and `reject` (D11) and the test U9 names;
    - a role the oracle does not authorize;
  - **the seal:** the served runtime would import `glow_profiles` or any new module;
  - **the timeout:** the Database proof checks job cannot stay within its 30-minute timeout.
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished. A newer push cancels the earlier run's application jobs, and the run of record is lost. Push your records commit only after the run of record has finished. The workflow runs on pushes to `claude/**` and `ccr-**`; if your branch is named otherwise, say so in the report, since no run starts.
- **Network:**
  - **PyPI and the npm registry:** for `pip install --require-hashes` and `npm ci --ignore-scripts` from the existing locks only;
  - **Docker Hub:** only to pull the PostgreSQL image the CI job pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`) for a local run (below).

  Nothing else: no Cloudflare or R2 documentation is needed, since the brief states no R2 mechanism beyond the media provider mapping's two facts. A page you cannot reach is named as unread, never filled from memory.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions):
  - a throwaway PostgreSQL in Docker, from the CI job's pinned image, on loopback only;
  - a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present;
  - removed afterwards.

  Local passes are "iteration, not evidence"; the run of record is CI's. If Docker or the image is unavailable, iterate through CI and say so.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, password, code, token, session key or signing key, in any form;
  - read, print or use the value of any `AWS_*` variable (section 1);
  - make test data that looks real. Accounts, emails, names, birth facts, places and coordinates are synthetic and obviously so (`@example.invalid` addresses). Photo bytes are small synthetic PNGs made in the test, never a real image;
  - call any provider or HDE, send any email, or run any command in `proofs/stream-chat/`;
  - connect to any database but a throwaway one you started under D4's conditions. Run `migrate` or `makemigrations` only through the proof's own commands against such a database, or under the static registry's dummy settings;
  - connect to HDE, Railway, Cloudflare or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script;
  - weaken or delete a test to make the suite pass. Changing a test to follow the brief (the F05 test D11 names, `CASE_COUNT`, Stage A's cases that now need an approved photo) is not weakening it; say what each change is.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*` or `CF_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_)'` prints names only. If any is present, stop and report.
3. **Three AWS names are expected** (DM-57, section 8): the container sets `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_CA_BUNDLE`, and the manager's and the Dev Manager's sessions both saw them. `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values. Stage B adds no client that reads them, and every repository command runs in the clean environment of item 6, which leaves them out. If any other `AWS_*` name is present, stop and report.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
5. **The toolchain:** CPython 3.12.14 as `python3.12` (`services/api/.python-version`); Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, first on PATH. Record `python3.12 --version`, `node --version`, `npm --version` and `docker --version`.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API). The proxy and CA variables pass by reference, never printed (`docs/operations/local-development.md`). No `AWS_*` name passes.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git merge-base --is-ancestor 4dc2061a33c6f63e2887b11aeb2fd32d6224e23e HEAD && echo "Stage A present"   # main's merge of PR43; the manager branch holds it since 780fb20. Must print "Stage A present"
git diff --name-only 4dc2061a33c6f63e2887b11aeb2fd32d6224e23e HEAD | grep -v -E '\.md$'               # against main: must print nothing
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/api proofs/postgres-ordering packages/contracts apps/mobile/src/contracts .github docs/testing/evidence/2026-11-10-sv2-profiles-media.md docs/architecture docs/testing/p11-deferred-acceptance.md   # must print nothing
grep -rn -F '"media.policy"' services/api                                                          # the setting's name: must print nothing
ls services/api/glow_persistence/migrations | grep -E '^[0-9]{4}_'                                     # must list 0001 to 0007 only
grep -c '^## Stage B' docs/testing/evidence/2026-11-10-sv2-profiles-media.md                          # must print 0
```

If a check fails, stop and report. The prompt is stale if:
- `<START_SHA>` is not on the live manager branch;
- the live branch has changed an owned path since it;
- or the brief's "Sessions" already records a Stage B implementation session.

**Then read, completely:**
- **The instructions:**
  - root `AGENTS.md` and `CLAUDE.md`;
  - `services/api/README.md`, `proofs/postgres-ordering/README.md` and `packages/contracts/README.md`;
  - `apps/mobile/AGENTS.md`: you change only its generated contracts.
- **The brief,** revision 7, whole: D9, D10, D11, D17, D19, "Owned paths", "Exclusions", the acceptance checks, the review plan, and "Stage B (revision 6)" above all.
- **The Dev Manager's reports,** whole. Their "Tried" lists, gaps and corrections are cases your tests should cover:
  - DM-57: `docs/continuity/dev-manager/reviews/2026-11-11-dm-57-sv2-stage-b-brief.md` (R2, D19, Stage B's scope);
  - DM-56: `…/2026-11-10-dm-56-sv2-stage-a-pre-merge.md` (section 6, every transaction's pointers);
  - DM-52 to DM-55: `…/2026-11-10-dm-52-sv2-brief.md`, `…-dm-53-sv2-stage-a-paths.md`, `…-dm-54-sv2-stage-a-decisions.md`, `…-dm-55-sv2-stage-a-review.md`.
- **Nathan's directions:** OD-60, OD-61 and OD-62 in `docs/continuity/owner-directions.md`.
- **The evidence record,** `docs/testing/evidence/2026-11-10-sv2-profiles-media.md`: Stage A's sections, its threat model's inputs and lock order, "Correction C3" (the static guards and their allowlist), "Delta review of correction C3" (N1 to N5 and the lock order), and "The merge receipt for Stage A".
- **The media design's sources:**
  - `docs/architecture/private-media-fixtures.md` (P04.3's lifecycle, revocation records and fixture semantics);
  - `docs/architecture/media-provider-mapping.md` (its OD-62 note and its R2 events row);
  - the carried-items file's "Carried to SV2" and "Carried to P07" (U7), and the P11 plan's PV04, DB07, DB08 and its entry from DM-57 (U6).
- **The contract:**
  - `packages/contracts/production/flows-v1.json` (F05 and F04), `gapp-api-v1.schema.json` (`MediaIntent`, `MediaLifecycle`, `MediaUploadGrant`, `MediaCollection`, `Error`) and `openapi.json`;
  - `packages/contracts/transition_contract.py` and `packages/contracts/tests/test_transition_contract.py` (`test_f05_quarantine_cannot_be_published_by_uploader`);
  - `docs/architecture/production-contracts.md`: the flow index, F05, "P04.3 media collection and binding clarification", and the server mapping.
- **The data model:** `docs/architecture/data-model.md`, the `MediaAsset` row, the unit-of-work table and the outbox event table; `services/api/glow_persistence/models.py`, whole (`MediaAsset` exists, with its storage and variant references, position and states).
- **Stage A's code,** which you change where D19, D9 and the carried guards need it: `services/api/glow_profiles/` whole (`settings_store.py`, `recompute.py`, `requirements.py`, `operations.py`, `staff.py`, `catalog.py`, `tx.py`, `views.py`, `urls.py`, `contract.py`), and `services/api/glow_domain/profile_settings.py`, `profile_fields.py` and `identity_verification.py`.
- **The tests and the proof:** `services/api/tests/test_profile*.py`, `test_profiles_offline.py` and `test_profiles_sealed_runtime.py`; `proofs/postgres-ordering`'s `profile_settings.py`, `profile_suite.py`, `profile_support.py`, `profile_cases.py`, `profile_scan.py` and `tests/test_profile_offline.py`; the Database proof checks job in `.github/workflows/foundation.yml`, whole.
- **The CI policy's Database proof checks paragraph** (manager-owned: read it, do not change it).

**Facts from the code and the Dev Manager that the work relies on:**
- **Every pointer lock is in `settings_store`:** `read_shared` (raw `FOR SHARE`) and `publish` (`select_for_update`). `read_unlocked` takes none, and `glow_chat` locks no pointer (DM-57, section 4).
- **The four transactions D19 changes** are `set_field`, `set_area`, staff's approval without identity verification, and the owner's catalog read (DM-56, section 6). `publish` must record its own pointer as held before its read of `consent.onboarding` (U8).
- **`tx.run` answers any exception that is not a refusal or an integrity error as `provider_unavailable`,** retryable, with the exception's type as the internal reason. D19's check raises such an exception, never a `Refused`; an offline test shows both (DM-57, section 4).
- **`MediaUploadGrant` is closed,** and its `grant_ref` cannot hold an address. Return it unchanged; the store's credential goes to no member (U3).
- **Once D9's photo requirement holds,** every Stage A case that makes a profile `visible` needs an approved photo, seeded through Stage B's own path or the test's setup as D8's mapping is. `CASE_COUNT` (`profile_cases.py:61`, held by `tests/test_profile_offline.py:512`) changes with Stage B's cases (DM-57, section 5).
- **`0007`'s seed never changes after it is applied** (its docstring): the media policy is seeded by a new data migration, with the reason `development-media-1` (U10).
- **SV2's operations nest `glow_chat`'s writers on purpose,** and two helpers refuse an open transaction (`glow_chat`'s reads; SV1's `require_no_transaction`), as Stage A's prompt said.

## 3. What to do

1. **D19, one pointer order** (U8), first, since Stage B's writers rely on it:
   - the four transactions take their pointers in name order, by one first `read_shared` call;
   - `settings_store` records each transaction's held pointers, the publication's own included, and raises an internal error on a lock that sorts before a held one and is not itself held;
   - an offline test shows the error, and that it is answered as `provider_unavailable`, not as a refusal; a static test shows that nothing outside `settings_store` locks a `PolicyRevision` row;
   - every profile-suite case runs under the check.
2. **The media policy** (D2, D10, U10): the setting `media.policy`, its schema and its ceilings in code (`development-media-1`'s types, bytes and pixels, and the contract's 20 collection entries), seeded as version 1 by a new data migration with the reason `development-media-1`. A publication above a ceiling is refused.
3. **The ports and their fixture adapters** (D10): the storage port, the processing port, the photo check's port, the detection seam (configured with none, recording "no detector") and the hold port (its fixture answers "no hold"). Object keys are random and opaque (D10). The runtime's fixtures approve nothing; a test drives them in its own setup.
4. **The photo writers and reads** (D10, D9), each taking the account row lock first and following D19:
   - the upload grant: its model, recording the policy version it was issued under (U3); one-use and short-lived by Glow's own record; `MediaUploadGrant` returned unchanged;
   - the completion (`uploaded`, `provider`), through the storage port only: the first completion that matches the grant's key and that version's byte limit is adopted, and any other changes nothing;
   - the system review step (`review`): processing on the adopted original only, then G-02's seam for every adopted upload, with the variant or, when processing made none, the original; an upload with no variant moves to `review_pending` and is rejected (`system`) with its reason; an unavailable store changes nothing (U1);
   - the automated check's `approve` and `reject` (`system`, written to `StaffAudit` with a `system:` subject), asking the hold port before approval; the check never clears a staff restriction;
   - staff restriction on a report (`restrict_media`, `moderator`), a domain operation with a subject and a reason;
   - reorder (collision-safe temporary positions in one transaction), removal (delivery withheld at once, `removal_pending`), and `purged` only on the storage adapter's acknowledgment that every object of the asset is deleted, asking the hold port first;
   - delivery returns only an approved variant's reference;
   - the photo requirement (D9): the check's approval ends with the recompute (`requirements_met`), and the removal or restriction of the last approved photo demotes a `visible` profile (`requirement_removed`), each with its event.
5. **The contract** (D11): F05's `approve` and `reject` become `system`, and `test_f05_quarantine_cannot_be_published_by_uploader` changes with them (U9). A transition the writers make that the registry lacks is a new entry, with an allowed and a forbidden example. F05's member routes use its existing DTOs; any new DTO is additive. Regenerate with `npm run generate --prefix packages/contracts`, never by hand, run it twice, and record which generated files changed.
6. **The carried guards** (the brief's "Stage B (revision 6)", item 5):
   - C3's state-write allowlist: update any line Stage B moves, and add Stage B's `MediaAsset` state writes as another model's writes;
   - widen C3's guards for the four spellings the delta review found (N2 to N5), each with its reversal;
   - D16, only if you change `identity_support.py`.
7. **Every test comes with its reversal** (D15): a temporary edit that must make the test fail, run and then undone. Record the edit and the failing output. Make at least these, each named in the record:
   - **D19:** each of the four transactions with its added pointer dropped; `publish` not recording its own lock;
   - **the media policy:** a publication above a ceiling written anyway;
   - **the grant:** a grant beyond the policy's limits issued; a second use of a grant accepted; the completion checked against the current policy version, not the grant's;
   - **the completion:** a completion for another key adopted; an oversize completion adopted; a second completion for an adopted key changing the asset; a member route delivering a provider event;
   - **processing and the seam:** a variant made from an object other than the adopted original; an upload with no variant skipping the seam; an unavailable store rejecting the asset; the original referenced for delivery; an object key holding an account, profile or asset ID or a filename;
   - **the check:** an approval or rejection by any role but `system`; an approval clearing a staff restriction; an approval undoing an owner's removal; an approval not asking the hold port;
   - **removal:** delivery not withheld at once; `removed` reached without the acknowledgment for every object; the purge not asking the hold port; reorder or removal by another owner;
   - **D9:** the check's approval of the last requirement leaving the profile `incomplete`; the removal of the last approved photo leaving it `visible`;
   - **D17 and the log capture:** another member's photo state or reference returned; an object key, an original's reference or photo bytes logged.
8. **The proof:** the profile suite's cases for checks 10 and 13, with D9's photo requirement in completion's cases; Stage A's cases that make a profile `visible` given an approved photo; `CASE_COUNT` and its offline test updated. The job's SV2 steps change only if a step must; if one must, stop before changing the workflow and report why, since the CI policy's paragraph is the manager's.
9. **The local checks,** as Stage A's prompt ran them: the API (`manage.py check`, `manage.py test tests --verbosity 2`, `smoke.py`, Ruff, `ruff format --check`, mypy, `python -m glow_persistence.static_check`), the contracts (`npm run check`, the Python contract tests), the mobile app's `npm run check` with only the regenerated outputs, the proof's offline tests, Ruff and mypy, and a local database run if Docker allows it under D4's conditions (iteration, not evidence).
10. **The run of record.** Commit and push your code, wait for the Foundation run to finish (the push rule), and read it with your GitHub tools: every job's conclusion and the gate's line (`Application checks passed`); the API test count; the ordering, identity and profile suites' results; the profile phase's duration against the 30-minute timeout; the Mobile checks job's checks; whether a toolchain retry fired; and that no secret, coordinate, key or photo byte appears in the job's log. If it fails, stop and report the failing job and its log lines. Do not re-run it.
11. **The records** the brief owns, for Stage B's parts: the data model's `MediaAsset` row and the grant's, as built; the contract document's F05 index row and server mapping; `private-media-fixtures.md`'s note that the server exists, sealed; the contracts README's SV2 section; the P11 plan's PV04, DB07 and DB08 partial evidence. Change no other section of those files.

## 4. The record

Write, under a new `## Stage B` heading at the end of `docs/testing/evidence/2026-11-10-sv2-profiles-media.md`:
- the start gate's results, the environment check (names only, the three AWS names included) and the toolchain versions;
- a table with one row per item of "Stage B (revision 6)" and per acceptance check Stage B builds: the files, the test, the reversal and its failing output;
- the contract: the registry entries changed and added, their examples, the F05 test's change, and the generated files that changed;
- **the threat model's inputs:**
  - every new route and its refusals, and who may call it;
  - every provider and system event, how it reaches the domain, and what it may change;
  - every staff operation, and how its subject reaches it;
  - every stored reference and key, what it may hold, and what removes it;
  - the media policy's settings and ceilings;
  - each transaction's pointer locks, in order, and D19's check;
  - each event and what it carries;
  - each with its test;
- every command you ran, with its result line, with local database runs listed as iteration, not evidence;
- the run of record: its ID, each job's result, the counts, the profile phase's duration, and whether a retry fired;
- what you could not run, and why.

Commit each logical step with a clear message ending in the session's attribution lines. Push your records commit only after the run of record has finished. Confirm that `git status` is clean, and that `git diff --name-only <START_SHA> HEAD` lists only your owned paths.

## 5. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch, your code head and records head;
- the start gate's and the environment check's results;
- for each item of "Stage B (revision 6)": what changed, its tests, and each reversal's result;
- the contract: the registry changes, the F05 test's change, and the generated files that changed;
- each local check's result, and whether a local database run was used;
- the run of record: its ID, every job, the gate's line, the counts, the profile phase's duration and whether a retry fired;
- anything that met the stop rule, every deviation from the brief, and what you could not run.
