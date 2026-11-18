# SV2-R exact-head review prompt — the identity requirement set aside and the photo check's toggle, with a written threat model

- **Owner:** App Manager 12. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 18 November 2026.**
- **Durable brief:** [SV2-R — SV2's completion requirements after OD-68](../planning/sv2-r-od-68-requirements-change.md), revision 6, "Review plan".
- **Where the result goes:** the report Nathan relays. The manager records it in the evidence record, "Exact-head review", with a disposition for each finding (fix before the merge, or carry), and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 2.94 (confidence 0.92); rung probabilities low 0.00, medium 0.00, high 0.09, extra high 0.88, max 0.03, ultracode 0.00. Model probabilities Fable 5.1 0.11, Opus 5.5 0.88, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.84). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.010, Fable 5.1 at extra high 0.097, Fable 5.1 at max 0.003, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.000, Opus 5.5 at high 0.079, Opus 5.5 at extra high 0.774, Opus 5.5 at max 0.026, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.001, Sonnet 5.5 at extra high 0.009, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-18T18:53:20Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of PR54's head, which is this prompt's commit (manager workflow, step 6). A full review of SV2-R's code, not a delta review.
- **Deletion condition:** prune after SV2-R's pull request merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **exact-head code and security review of SV2-R**: the identity requirement set aside and the photo check's toggle, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one exact code head in full, with a written threat model. This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **SV2** built the server's profile, its settings and photos (PR43, `4dc2061`; PR44, `3240ef0`), sealed until P11. Its brief, `docs/planning/sv2-profiles-media.md`, revision 8, holds D2 (the settings store), D9 (completion and the shared recompute), D10 (photos), D13 to D15 (the seal, no new dependency, reversals), D18 (identity verification and the staff approval) and D19 (one pointer order).
- **OD-68** (Nathan, 17 November 2026; `docs/continuity/owner-directions.md`): ID validation set aside for the MVP and kept possible later; the automated photo check dropped behind a toggle.
- **SV2-R's brief,** revision 6. Its text applies the Dev Manager's conditions word for word: DM-84 section 5 (the toggle's defaults), DM-91 (XX5 to XX9), DM-92 (YY1 to YY7) and DM-93 (ZZ1 to ZZ4), in `docs/continuity/dev-manager/reviews/`. In short:
  - **R1:** `requirements.missing` no longer checks identity verification; its signature, the contract's `identity_verification` value, the record, its port, the staff approval and its setting stay;
  - **R2:** `media.photo_check`, off at launch (migration `0012`); `run_check`'s off branch approves without the check port under the toggle's own subject and reason; `recheck` and `awaiting_recheck` for photos approved while it was off; F05's two `system` transitions out of `approved`;
  - **R3, R4:** the photo requirement, the fixed limits and the seal unchanged;
  - **"Earlier tests":** the earlier tests and proof cases expected to change, under SV3's DD5 rule; SV2-R's own cases under the `sv2r.` prefix.
- **A first session** on the prompt's revision 1 stopped at its stop rule before changing anything (AM12-24); the brief was corrected before the revision 2 session ran.
- **The implementation** (branch `claude/intelligent-curie-i27kvt`, code head `f4703a1`, records `587f4a2`; the evidence record `docs/testing/evidence/2026-11-18-sv2-r-requirements-change.md`): run of record 44362141024, all eight jobs passed, the profile suite 77/77. The manager verified it ("Manager verification") and merged it into the manager branch at `d996ef6`.

**The code head under review is `f4703a1`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `f4703a1` (the start gate checks this).

**Your scope:**
- **The code:** `git diff 15d54f647aa012edf53165f04a0a7e4931a7b67f f4703a1faf79e1a66f615a17b531f874be73b1ed`, its 16 non-Markdown paths, read in full at `f4703a1`:
  - `services/api/glow_profiles/requirements.py` and `media.py`;
  - `services/api/glow_domain/media.py` and `profile_settings.py`;
  - migration `services/api/glow_persistence/migrations/0012_photo_check_seed.py`;
  - `services/api/tests/` (6): `test_model_definitions.py`, `test_profile_media.py`, `test_profile_recompute.py`, `test_profile_settings.py`, `test_profiles_offline.py` and the new `test_sv2r_requirements.py`;
  - `packages/contracts/production/flows-v1.json` and `packages/contracts/tests/test_transition_contract.py`;
  - `proofs/postgres-ordering/`: `profile_cases.py`, `profile_support.py` and `tests/test_profile_offline.py`.
- **The records, as claims about the code:** the evidence record, whole; the brief's "Sessions"; the contracts README's SV2-R note; the proof README's profile-suite paragraph (line 17).
- **The runs:** 44362141024 (the run of record) and the PR run on PR54's head (event `pull_request`), once it has finished.
- **Out of scope:** code SV2-R does not change, and SV2's code where SV2-R left it unchanged (a finding there is reported as pre-existing); the items carried: P11's worker and real adapters, P08.3's entitlement question (DM-91), ID validation's return, P07's console. Report only where the code contradicts what the carry says.

**The threat model** (the brief's "Review plan"). Write it in your report:
- **Assets:**
  - whether a profile is `visible`, and the completion read's list;
  - a photo's state, its approval's record (who approved it, and why), its delivery reference and its review reference;
  - the hold, which must stop an approval and a delivery; staff's restriction, which only staff clear;
  - the toggle `media.photo_check`, its version history, its pointer and its audit;
  - F05's registry, and the transitions it allows;
  - the identity record and the staff approval, kept for ID validation's return;
  - the profile suite's keys and the run's database credentials.
- **Actors:**
  - a member who completes a profile, with or without a photo;
  - a staff caller publishing the toggle, in code until P07;
  - P11's worker calling `recheck` for each photo `awaiting_recheck` lists, possibly late, twice, or while the toggle is off;
  - a staff restriction or a hold landing between a listing and a recheck;
  - a member whose account is suspended or deleted with photos awaiting the recheck;
  - anyone who reads this public repository's CI logs and artifacts.
- **Entry points:** `run_check`, `recheck` and `awaiting_recheck` (system steps, no route); the settings publication of `media.photo_check`; migration `0012`; D9's recompute through each writer; the completion read; the profile suite's job steps.

For each threat, give the code that stops it and the test that proves it. The focus:
1. **R1:**
   - no profile becomes `visible` with any requirement but identity verification missing;
   - the completion read never lists `identity_verification`, and the contract's closed list still holds it;
   - the staff approval and its revocation are gated, audited and bump `eligibility_version` as before, and move no profile;
   - `missing()`'s signature and its three callers are unchanged (DM-93 ZZ2).
2. **`run_check`:**
   - one `read_shared` call, in D19's name order;
   - with the toggle off: no call to the check port, and never `system:photo-check` with `automated_check`;
   - a restriction, a missing variant and the hold port stop the approval in the order the record states;
   - D9's recompute follows;
   - with the toggle on: behaviour identical to before.
3. **`recheck` and `awaiting_recheck`:**
   - the account row lock first, and an inactive account refused;
   - the toggle read in one `read_shared` call, and nothing changed with no port call while it is off;
   - the hold port asked before its approval (DM-92 YY1);
   - its rejection through `transition`, with delivery withheld and the recompute demoting a profile whose last approved photo it was;
   - a photo whose approval is the check's is never rechecked, and the listing holds only photos of `active` accounts;
   - a second call, or a call after a restriction or a removal, changes nothing it should not;
   - the second `media_approved` event for the same photo (DM-91 4.3): say whether anything today reads it as a first approval.
4. **The registry:**
   - exactly the two `system` transitions out of `approved` are added, in `flows-v1.json` and `TRANSITIONS` alike;
   - every other transition stays forbidden, with an allowed and a forbidden example for each new entry;
   - no generated output changes, and the mobile app needs no change.
5. **The setting:**
   - its closed schema refuses any other content before anything is written;
   - migration `0012` seeds version 1, its pointer and its `StaffAudit` row on `0009`'s pattern, and is reversible;
   - publications are audited and emit `policy_published`.
6. **The session's open question** (the record, "Open questions"): `approved_photo` publishing the toggle on in its setup, accepted by the manager as the brief's "Earlier tests" reading. Say whether it hides any behaviour an earlier case should still show with the toggle off, or weakens what the earlier cases prove.
7. **No test is weakened or vacuous:**
   - each earlier test changed is one the brief's "Earlier tests" names, and asserts what it asserted, or more;
   - the plan pins (`CASE_COUNT` 77, `SV2R_CASES` and its rule, `LABEL_BINDINGS`) bind as before, and `LABEL_NAMES` is unchanged;
   - the state-write guard's line pin moved with the line only;
   - each reversal the record names fails its case;
   - no case could pass while the behaviour it guards is wrong. Above all: the off branch's port call, the recheck while off, the hold before each approval, the rejection's demotion, and the lock-order case (`sv2r.locks_serialize_on_the_toggles_pointer`).
8. **D17, the seal and the dependencies:**
   - no secret, key, original reference or member value in any new body, log, event or artifact;
   - the served runtime imports none of the new code;
   - `foundation.yml` and every lock and requirement file are unchanged from `15d54f6`.
9. **The records:** every claim in the texts listed in the scope holds against the code and the runs.

**Re-run, at least,** in a scratch copy of `f4703a1`:
- **The API's checks:** `manage.py check`, `manage.py test tests`, `ruff` and the configured `mypy`; the contract tests; the proof's offline tests, `ruff` and `mypy`.
- **The contract outputs:** `node scripts/generate.mjs --check` in `packages/contracts`, after `npm ci --ignore-scripts` there.
- **Four offline reversals:**
  - the identity check restored in `missing()`: SV2-R's R1 test fails;
  - `run_check`'s off branch calling the check port: its test fails;
  - a third `system` transition out of `approved` in both tables: the contract and registry tests fail;
  - `media.photo_check` read out of D19's order: the pointer-order test fails.
- **The profile suite, informational:** on a throwaway PostgreSQL under P06.DB's D4, if Docker allows; add database reversals you doubt, such as the recheck acting while the toggle is off, or approving a held photo.

**What comes after this review: the correction classes.** Report every finding with its severity. A correction pass takes every blocking finding, and any should-fix finding that could do any of these:
- let a profile become `visible` with a requirement other than identity verification missing, or stay `visible` after its last approved photo goes;
- record an approval as the automated check's when the check did not decide it, or call the check port while the toggle is off;
- let a held photo be approved or delivered, or a restricted photo be approved, or undo an owner's removal;
- let the recheck change a photo while the toggle is off, act on an inactive account, or recheck a photo the check approved;
- let a transition outside F05's registry happen, or the two tables disagree;
- let a publication of the toggle skip its schema or its audit, or take a pointer out of order without the check stopping it;
- let a secret, a key or a member value reach a log, an error, an event, a CI log or an artifact;
- let the served runtime import the new code, or add a package;
- let a test pass where it should fail, or fail where the code is right;
- leave a Dev Manager condition unmet;
- make a record claim more than the code, the tests or the runs show.

Everything else goes into the records. For each finding, say whether it falls in one of these classes.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 12. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches. Read GitHub only through your GitHub tools; use `gh` for nothing but a search.
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
  - call any provider or HDE, R2 or Cloudflare included, send any email, or run any command in `proofs/stream-chat/`;
  - connect to any database but a throwaway one you started under D4's conditions, HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:**
   `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`.
   If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*` or `CF_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_)'` prints names only. If any is present, stop and report.
3. **AWS names may be present** (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_CA_BUNDLE`). `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
5. **The toolchain:** CPython 3.12.14 as `python3.12`; Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`; Docker if present. Record their versions.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API). No `AWS_*` name passes.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, 15d54f647aa012edf53165f04a0a7e4931a7b67f
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet f4703a1faf79e1a66f615a17b531f874be73b1ed HEAD -- . ':!*.md' && echo "the code head under review"
git diff --quiet f4703a1faf79e1a66f615a17b531f874be73b1ed origin/claude/magical-wozniak-yfmmx2 -- . ':!*.md' && echo "no code on the live branch after f4703a1"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-18-sv2-r-requirements-change.md | grep -c -E '^#+ Exact-head review'   # must print 0
```

If any check fails, stop and report. The prompt is stale if any of these holds:
- its commit is not on the live branch;
- a non-Markdown path changed there after `f4703a1`;
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
- the brief, revision 6, and the reports of DM-84 (section 5), DM-91, DM-92 and DM-93;
- OD-68 in the owner-direction register;
- the SV2 brief's D2, D9, D10, D13 to D15, D18 and D19;
- the evidence record, whole;
- F05 in `packages/contracts/production/flows-v1.json`, and the completion read's `missing` list in `gapp-api-v1.schema.json`;
- every file in the code diff, whole, with `glow_profiles/settings_store.py`, `staff.py`, `recompute.py`, `tx.py` and `operations.py` as SV2 left them (read only).

**The runs,** with your GitHub tools: 44362141024 and the PR run on PR54's head, if it has finished: every job's conclusion, the gate's line, and the Database job's profile lines.

## 3. What to do

1. Write the threat model, then review the code against the focus, item by item.
2. In a scratch copy of `f4703a1`:
   - re-run the checks and the four offline reversals above, and any you doubt;
   - run the profile suite locally under D4 if you can, informational.
3. For each finding: its severity (blocking, should fix, nit), its file and line, the evidence, and whether it falls in a correction class.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- the threat model, each threat with its stopping code and its test;
- the focus, item by item, with your verdict on each;
- every finding, with its severity, file and line, evidence and correction class;
- the checks and reversals you re-ran, each with its exact result, and the local suite run if any;
- your verdict: **approve**, **approve with nits** or **changes requested**;
- what you did not read or run, and why.
