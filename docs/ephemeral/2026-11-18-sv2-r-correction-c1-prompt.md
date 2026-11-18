# SV2-R correction C1 prompt — tests for two untested guards, and three carried entries

- **Owner:** App Manager 12. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 18 November 2026.**
- **Durable brief:** [SV2-R — SV2's completion requirements after OD-68](../planning/sv2-r-od-68-requirements-change.md), revision 7, "Correction C1".
- **Where the result goes:**
  - the session's changes in C1's owned paths, and a "Correction C1" section in the record, `docs/testing/evidence/2026-11-18-sv2-r-requirements-change.md`, on its own branch;
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification to the record and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 1.68 (confidence 0.77); rung probabilities low 0.00, medium 0.33, high 0.66, extra high 0.01, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.96, Sonnet 5.5 0.04, Haiku 5.5 0.00 (confidence 0.95). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.317, Opus 5.5 at high 0.634, Opus 5.5 at extra high 0.010, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.013, Sonnet 5.5 at high 0.026, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-18T20:41:14Z. Nathan picks the cell.
  - An earlier reading (sent 20:40:06 UTC) was of a narrower action text, before C1.4's carried entries joined (AM12-26). It gave the same cell, Opus 5.5 at high; both are in the uses table.
- **The Dev Manager's read:** none before it runs. C1 adds tests only, under the manager workflow's fix-or-carry rule (a), and changes no design, interface, contract or dependency; it authorizes no credential use and no live provider action (the charter, "Read before it takes effect").
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Then, in order: the manager's verification; PR54's run and Codex's review of its head; a delta review of C1 (the manager workflow, step 6); the merge after its run, Codex's summary on the final head and its checklist.
- **Deletion condition:** prune after SV2-R's pull request merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch (AM11-21).

---

You are the **correction session C1 for SV2-R**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What C1 is.** SV2-R set ID verification aside as a profile requirement and put the automated photo check behind a toggle, `media.photo_check` (Nathan's direction OD-68). Its code head is `f4703a1`. The exact-head review of that head found **the code right and two guards untested.** In each case, the review broke the guard and every suite still passed, the disposable-PostgreSQL profile suite included. C1 adds the tests that catch those breaks, and takes up three small carried entries that SV2-R's changes to their files should have taken up. **C1 changes no code.**

**The brief, `docs/planning/sv2-r-od-68-requirements-change.md`, revision 7, "Correction C1", is the specification.** Where this prompt summarizes it, the brief wins. The review's findings and the manager's dispositions are in the record's "Exact-head review" section.

**What came before.**
- **SV2** built the server's profile, settings and photos (PR43, PR44), sealed from the served runtime until P11.
- **SV2-R's implementation** (branch `claude/intelligent-curie-i27kvt`, code head `f4703a1`) built R1 to R4. Its run of record, 44362141024, passed all eight Foundation jobs, with the profile suite at 77 of 77. The manager merged it into the manager branch, and PR54 carries it.
- **The exact-head review** (at `e2bacf7`, of `f4703a1`): changes requested, for tests only.
  - **R1:** no test calls `recheck` on a photo that is no longer `approved`. Its reversal B (removing `asset.state != md.APPROVED` from the recheck's refusal) passed everything.
  - **R2:** no test calls `run_check` on an `approved` photo. Since SV2-R's two transitions out of `approved`, its `not_in_review` refusal is the only stop. Its reversal A (that refusal also admitting `approved`) passed everything.
  - **N1:** the record's acceptance check 2 claims a little more than its run shows.
  - N2 to N4 are carried by the manager.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 12. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only C1's owned paths (the brief, "Correction C1"):
    - `services/api/tests/test_sv2r_requirements.py`: new tests;
    - `services/api/tests/test_profile_recompute.py`: N-a's creation guard only;
    - `services/api/tests/test_profile_media.py`: N-d's write list only;
    - `proofs/postgres-ordering/glow_ordering_proof/profile_cases.py`: the `sv2r.` cases only, extended (no new case);
    - `proofs/postgres-ordering/glow_ordering_proof/profile_support.py`: N-c's docstring, and, if one is needed, a helper only the `sv2r.` cases use;
    - the record, `docs/testing/evidence/2026-11-18-sv2-r-requirements-change.md`: acceptance check 2's row (C1.5) and a new section, "Correction C1";
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only, through your GitHub tools: no pull request, comment, review, re-run, workflow dispatch or setting. Use `gh` for nothing but a search. Change nothing in Notion.
- **The stop rule.** Stop and report, with no further change, if any of these holds:
  - **a code change:** any new test fails against the code as it is at `f4703a1`. The review found the code right, so such a failure is reported with its output, not fixed;
  - **an owned path:** the work needs a path outside the list above, or a part of a listed file outside its stated part: any non-test module, `test_profile_offline.py`, the proof's README, any other earlier test or proof case, a workflow, a lock or requirement file;
  - **a new case:** a profile case would have to be added. `CASE_COUNT` (77), `SV2R_CASES`, `LABEL_NAMES`, `LABEL_BINDINGS` and the README's count stay as they are;
  - **a dependency:** any new Python or npm package, or a changed pin;
  - **the timeout:** the Database proof checks job cannot stay within its 30-minute timeout; it is not raised;
  - **an earlier test:** an earlier test or proof case fails that C1 does not change. Report which and why; do not change or delete it.
  - In each case, report it; do not narrow the brief's words to pass it. A reversal's temporary edit of code is allowed, and must be undone and confirmed byte-identical.
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished. A newer push cancels the earlier run's application jobs, and the run of record is lost. Push your records commit only after the run of record has finished. The workflow runs on pushes to `claude/**` and `ccr-**`; if your branch is named otherwise, say so in the report, since no run starts.
  - **If GitHub never starts the run** (it stays `queued` with no jobs for 30 minutes), do not re-run it, dispatch it, push an empty commit, or ask anyone to re-run it (OD-58). Record it, push your records commit, and report. The manager's PR run is then the run of record.
  - **If the run fails,** stop and report the failing job and its log lines. Do not re-run it, and push no fix without saying so in the report.
- **Network:**
  - **PyPI and the npm registry:** for `pip install --require-hashes` and `npm ci --ignore-scripts` from the existing locks only;
  - **Docker Hub:** only to pull the PostgreSQL image the CI job pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`) for a local run (below).

  A page you cannot reach is named as unread, never filled from memory.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions):
  - a throwaway PostgreSQL in Docker, from the CI job's pinned image, on loopback only;
  - a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present;
  - removed afterwards.

  Local passes are "iteration, not evidence"; the run of record is CI's. If Docker or the image is unavailable, iterate through CI and say so.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, password, code, token, session key or signing key, in any form;
  - read, print or use the value of any `AWS_*` variable, or name one in a command (section 1);
  - make test data that looks real: accounts, emails, names, birth facts, places and coordinates are synthetic and obviously so (`@example.invalid` addresses);
  - call any provider or HDE, send any email, or run any command in `proofs/stream-chat/`;
  - connect to any database but a throwaway one you started under D4's conditions. Run `migrate` or `makemigrations` only through the proof's own commands against such a database, under Django's test runner, or under the static registry's dummy settings;
  - connect to HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script;
  - weaken or delete a test to make the suite pass.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:** `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` or `PG*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG)'` prints names only. If any is present, stop and report.
3. **AWS names may be present** (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_CA_BUNDLE`). `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values, and pass none to a command.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
5. **The toolchain:** CPython 3.12.14 as `python3.12` (`services/api/.python-version`); Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, first on PATH (`scripts/bootstrap-toolchain.sh`). Record `python3.12 --version`, `node --version`, `npm --version` and `docker --version`.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API). The proxy and CA variables pass by reference, never printed (`docs/operations/local-development.md`).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git diff --quiet f4703a1faf79e1a66f615a17b531f874be73b1ed HEAD -- . ':!*.md' && echo "the reviewed code"   # must print the line
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/api proofs/postgres-ordering packages/contracts apps .github docs/planning/sv2-r-od-68-requirements-change.md docs/testing/evidence/2026-11-18-sv2-r-requirements-change.md   # must print nothing
grep -c -E '^## Correction C1' docs/testing/evidence/2026-11-18-sv2-r-requirements-change.md   # must print 0
grep -c '^@case(' proofs/postgres-ordering/glow_ordering_proof/profile_cases.py   # must print 77
```

If a check fails, stop and report. The prompt is stale if:
- `<START_SHA>` is not on the live manager branch;
- the live branch has changed code, a test, the brief or the record since it;
- or a "Correction C1" section already exists.

**Then read, completely:**
- **The instructions:** root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md` and `proofs/postgres-ordering/README.md`.
- **The brief,** revision 7, whole, its "Correction C1" above all.
- **The record,** whole, its "Exact-head review" above all.
- **The code the tests pin, as it is (you change none of it):** `services/api/glow_profiles/media.py` (`transition`, `run_check`, `recheck`, `awaiting_recheck`, `_approvals_while_off`), `staff.py` (`restrict_media`) and `glow_domain/media.py` (`TRANSITIONS`).
- **The tests you extend:** `test_sv2r_requirements.py` whole; `test_profile_media.py`'s `PhotoCheckToggleTests` and `held_before_every_write`; `test_profile_recompute.py`'s creation guard; `profile_cases.py`'s eight `sv2r.` cases and the helpers they use; `profile_support.py`'s module docstring and `add_bytes`.
- **The carried entries N-a, N-c and N-d:** `docs/planning/carried-to-later-items.md`, "Carried to the next change to SV2's profile guards and suite", and the SV2 record's "Delta review of Stage B's correction C2" (`docs/testing/evidence/2026-11-10-sv2-profiles-media.md`), which holds their probes.

## 3. What to do

1. **C1.1, the recheck's state condition (R1).**
   - **Offline,** in `test_sv2r_requirements.py`: a structural test that the recheck's refusal `not_awaiting_recheck` holds unless the photo's state is `md.APPROVED`, and comes before any port call or write.
   - **On the disposable database,** inside `sv2r.the_recheck`, with the toggle on:
     - one photo approved while the toggle was off, then restricted by staff;
     - another approved while it was off, then removed by its owner;
     - each rechecked once with a rejecting check and once with an approving one.

     Each must give `no_change` with `not_awaiting_recheck`, with the check port not called (a spy) and nothing written: the photo's state, version and review reference, its audit rows and its events unchanged. `awaiting_recheck` must list neither.
2. **C1.2, `run_check` on an approved photo (R2).**
   - **Offline,** in `test_sv2r_requirements.py`: a structural test that `run_check`'s refusal on state admits only `md.REVIEW_PENDING`, before the restriction check and the toggle's branch.
   - **On the disposable database,** inside existing `sv2r.` cases (for example `sv2r.toggle_on_the_check_decides_as_before` and `sv2r.toggle_off_approves_without_the_check`): `run_check` on an approved photo, with the toggle on and with it off, must give `no_change` with `not_in_review`, with the check port not called and nothing written.
3. **C1.3, the reversals.** Make each, run it, record its failing output, undo it, and confirm with `cmp` that the file is byte-identical to `f4703a1`. Run each offline and, where Docker allows, on a local disposable database:
   - **reversal A,** `run_check`'s state refusal also admitting `approved` (for example `if asset.state not in (md.REVIEW_PENDING, md.APPROVED):`): C1.2's tests must fail;
   - **reversal B,** the recheck's refusal reduced to the review reference's filter (`asset.state != md.APPROVED or` removed): C1.1's tests must fail.
4. **C1.4, the carried entries,** each as its entry says, with a reversal for each spelling a widened guard now sees (a temporary edit of code that uses the spelling, which the guard must catch):
   - **N-a,** `test_profile_recompute.py`: the creation guard also sees `acreate`, `aget_or_create` and `aupdate_or_create`, and a clone saved with `force_insert=True` after `pk = None`;
   - **N-d,** `test_profile_media.py`: the held branch's offline write list also names `.update(`, `bulk_create` and `events.emit(`;
   - **N-c,** `profile_support.py`: the module docstring says the ledger holds the start of each object's bytes, the first 24, as their hex and their `repr`.
5. **C1.5, the record.**
   - Acceptance check 2's row says that the approval's recompute moves no profile whose state is current, and that D9's recompute still catches up a profile a test left stale (`completion.every_requirement_writer…`).
   - Add the section "Correction C1" (section 4 below).
6. **The local checks:**
   - **API,** in `services/api`: `python3.12 -m venv .venv`, then `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`. Then, with `GLOW_ENV=test`: `manage.py check`, `manage.py test tests --verbosity 2`, `ruff check .`, `ruff format --check .`, `mypy`, and the contract tests (`PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests -v`), as CI runs them;
   - **the proof,** in `proofs/postgres-ordering`: its venv and hash-locked install, its offline tests under `env -i`, Ruff, `ruff format --check` and mypy;
   - **a local database run** of the profile suite, if Docker allows it under D4's conditions: iteration, not evidence.
7. **The run of record.**
   - Commit and push your code. Wait for the Foundation run on your last code commit to finish (the push rule).
   - Read it with your GitHub tools:
     - every job's conclusion, and the gate's line (`Application checks passed`);
     - the API test count;
     - the profile suite's result (77 of 77), its scans, and the extended `sv2r.` cases by name;
     - the Database proof checks job's duration, against its 30-minute timeout;
     - whether a toolchain retry fired;
     - that no secret, coordinate or member value appears in the job's log.

## 4. The record

Add a section "Correction C1" to `docs/testing/evidence/2026-11-18-sv2-r-requirements-change.md`:
- the start gate's results, the environment check (names only) and the toolchain versions;
- a table with one row per item C1.1 to C1.5: the files, the tests, the reversal and its failing output;
- each carried entry taken up, with its guard's new spellings and each reversal's failing output;
- the local checks, each with its exact result;
- the run of record: its ID, head, each job's conclusion and the lines asked for above;
- deviations, limits and open questions.

## 5. The report

Branch, start and head SHAs, changed paths with their line counts, what was done for each of C1.1 to C1.5 with each reversal's failing output, the local checks, the run of record's ID and jobs, deviations and open questions. Push your records commit after the run of record has finished, and end with the record's path and your branch's final head.
