# SV1 correction C1 prompt — reauthentication for an email change, and the results upload checked first

- **Owner:** App Manager 10. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 9 November 2026.**
- **Durable brief:** [SV1 — The identity slice](../planning/sv1-identity.md), revision 4, "Correction C1".
- **Where the result goes:**
  - the session's changes, and the record's new section "Correction C1" in `docs/testing/evidence/2026-11-09-sv1-identity.md`, on the session branch;
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification, and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.47 (confidence 0.66).
    - Rung probabilities: low 0.00, medium 0.03, high 0.58, extra high 0.30, max 0.09, ultracode 0.00.
    - Model probabilities: Fable 5.1 0.06, Opus 5.5 0.93, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.91).
    - Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.002, Fable 5.1 at high 0.035, Fable 5.1 at extra high 0.018, Fable 5.1 at max 0.005, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.028, Opus 5.5 at high 0.539, Opus 5.5 at extra high 0.279, Opus 5.5 at max 0.084, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.006, Sonnet 5.5 at extra high 0.003, Sonnet 5.5 at max 0.001, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000.
    - Flags: boundary between extra high and high.
    - Sent 2026-11-09T13:44:01Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs (DM-47 section 2). This prompt authorizes no credential use and no live provider action.
- **Which session:** SV1's implementation session, on its branch `claude/hopeful-cerf-kc91xx`, is the natural home, since it built the code and its local harness. A new session can run it equally well, on its own branch.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of the commit that holds it (step 6). Then:
  - the manager's verification;
  - Codex on C1's head;
  - an exact-head code and security review of the corrected head in full, with a written threat model. No delta review is needed, since no review has run.
- **Deletion condition:** prune after SV1's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are **correction C1 of SV1**, the identity slice, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **SV1's implementation** (code head `269ac3b`, on PR42) built maintained sign-in on django-allauth 65.21.1 headless, in `services/api/glow_identity`. Its identity suite runs on a second disposable database in the Database proof checks job. Its record is `docs/testing/evidence/2026-11-09-sv1-identity.md`.
- **Two defects before the review:**
  - **An email change needs no reauthentication.** `glow_identity/conf.py` sets `ACCOUNT_CHANGE_EMAIL = True` and leaves `ACCOUNT_REAUTHENTICATION_REQUIRED` at its default, `False`. So a holder of a live access token, refresh token or session key can move the address and then reset the password from it. The implementation session reported it. Codex raised it on PR42 as its only finding (P1, `conf.py`, lines 93 to 94).
  - **The results upload is unscanned.** In the Database proof checks job, "SV1: save the identity suite's results JSON" runs `if: always()`. The secret check before it scans only `identity.log`, never `identity-results.json`. So the JSON is uploaded unscanned, even after a failed check, as an artifact of a public repository.
- **The Dev Manager approved this correction** (DM-47, `docs/continuity/dev-manager/reviews/2026-11-09-dm-47-sv1-email-change.md`) with conditions C1.1 to C1.4 in given words. The brief's revision 4 applies them:
  - C1.1 in D3's "**Email change:**" bullet;
  - C1.2 as acceptance check 13;
  - C1.4 in D10's "**The results upload is checked first**";
  - C1.3, and the items, owned paths, exclusions and stop rule, in "Correction C1".

  **The brief's "Correction C1" is your specification.** Read it whole.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 10. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only "Correction C1"'s owned paths:
    - `services/api/glow_identity/conf.py`;
    - `services/api/tests/test_identity_offline.py`;
    - `proofs/postgres-ordering/glow_ordering_proof/identity_*.py`;
    - `proofs/postgres-ordering/tests/test_identity_offline.py`;
    - `.github/workflows/foundation.yml`: the Database proof checks job's SV1 steps only;
    - `docs/architecture/data-model.md`: the first sentence of "Email change and recovery" only;
    - the record: the endpoint table's `auth/reauthenticate` row, and its new section "Correction C1";
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule.** Stop and report, with no further change, if any of these holds:
  - **allauth 65.21.1, at `auth/reauthenticate`:**
    - it cycles the session key;
    - it issues a token pair;
    - it runs one of Glow's sign-in hooks (`login`, `post_login`, or `glow_identity`'s `open_sign_in_session`).

    Report what the source shows, with file and line.
  - **An owned path:** the fix seems to need a path outside the list, such as:
    - `glow_identity`'s other modules (`adapter.py`, `strategy.py`, `revocation.py`, `authentication.py`, `sessions.py`);
    - `glow_chat` or `glow_api`;
    - a model, migration, lock or contract;
    - another workflow job.
  - **A dependency:** it seems to need a new package.
  - **The timeout:** the Database proof checks job cannot stay within its 30-minute timeout.

  **Not a stop:** if the reauthentication's response carries a `session_token`, record it as a deviation with the source line. The manager rereads N3's text (DM-47 C1.2).
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished. Push your records commit only after the run of record has finished.
- **Network:** PyPI, for `pip install --require-hashes`. Docker Hub, only to pull the PostgreSQL image the CI job pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`) for a local run.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions):
  - a throwaway PostgreSQL in Docker, from the CI job's pinned image, on loopback only;
  - a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present;
  - removed afterwards.

  Local passes are "iteration, not evidence"; the run of record is CI's.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, password, code, token, session key or signing key, in any form. Synthetic accounts and passwords are obviously synthetic (`@example.invalid`);
  - call any provider, send any real email, or run any command in `proofs/stream-chat/`;
  - connect to any database but a throwaway one you started under D4's conditions; run `migrate` or `makemigrations` only through the proof's own commands against such a database, or under the static registry's dummy settings;
  - connect to HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script;
  - weaken or delete a test to make the suite pass.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:**
   `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`.
   If any is present, stop and report.
2. **No `STREAM_*` or `PG*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG)'` prints names only. If any is present, stop and report.
3. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them.
4. **The toolchain:** CPython 3.12.14 as `python3.12`, and Docker. Record `python3.12 --version` and `docker --version`.
5. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API). The proxy and CA variables pass by reference, never printed.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # SV1's session: claude/hopeful-cerf-kc91xx; <START_SHA> already contains its 157c1f6
git rev-parse HEAD                                  # must print <START_SHA>
git diff --name-only 269ac3bf6a275b064ddd4ec772cd15b1cbce4506 HEAD -- .github scripts services apps packages proofs | grep -v -E '\.md$'   # must print nothing: the code is 269ac3b's
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/api proofs/postgres-ordering .github docs/architecture/data-model.md 'docs/testing/evidence/*sv1-identity*'   # must print nothing
grep -c -E '^#+ Correction C1' docs/testing/evidence/2026-11-09-sv1-identity.md   # must print 0
grep -c 'ACCOUNT_REAUTHENTICATION_REQUIRED' services/api/glow_identity/conf.py   # must print 0
```

If a check fails, stop and report. The prompt is stale if any of these holds:
- `<START_SHA>` is not on the live manager branch;
- an owned path changed there after it;
- "Correction C1" is already recorded.

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`; `proofs/postgres-ordering/README.md`;
- the brief, revision 4: D3, D10, the acceptance checks and "Correction C1";
- DM-47's report, whole;
- the record's "Facts read from the installed source", "The threat model's inputs" and "Manager verification";
- `glow_identity/conf.py`;
- the identity suite's cases that change an address (`notice.email_change`, `enum.email_change_taken_and_free_alike`), and how the suite moves time and clears the rate-limit cache between cases;
- the Database proof checks job's SV1 steps, whole;
- in allauth 65.21.1:
  - `account/internal/flows/reauthentication.py` and `manage_email.py`;
  - `headless/account/views.py`'s `ManageEmailView` and `ReauthenticateView`;
  - `headless/internal/sessionkit.py`'s `expose_session_token`;
  - the adapter's `reauthenticate`, `authenticate` and `pre_authenticate`.

## 3. What to do

1. **The items of "Correction C1", in order.** For each: the change, its test, and its reversal. A reversal is a temporary edit that must make the test fail; run it, then undo it. Record the edit and the failing output.
   - **Item 1, reauthentication** (D3; acceptance check 13):
     - **The setting:** `ACCOUNT_REAUTHENTICATION_REQUIRED = True` in SV1's fragment, with the settings case and the API's fragment test.
     - **One new identity case for acceptance check 13,** with every clause of its words:
       - right after sign-in, with no reauthentication, the change answers 401 with the `reauthenticate` flow, sends no mail and changes no address;
       - the same more than 300 seconds after a reauthentication;
       - the same in another session of the same account than the one that reauthenticated;
       - a wrong password is refused, and the sixth wrong password within 300 seconds is refused as too many attempts;
       - with the right password, the change goes ahead, as acceptance check 10's notice shows;
       - the reauthentication leaves the session key, its `UserSession` row and its `AccountSession` unchanged, and returns no token pair and no `session_token`.
     - **The existing cases** that change an address reauthenticate first, and pass as before.
     - **The reversal:** the setting turned off. It must fail the new case.
   - **Item 2, the data model:** the first sentence of "Email change and recovery" becomes, word for word:

     > One address per account (`ACCOUNT_CHANGE_EMAIL`), changed only after a reauthentication by password within the last 300 seconds (`ACCOUNT_REAUTHENTICATION_REQUIRED`; a sign-in does not count): the new address is verified by code before it replaces the old, and the old address gets the email-changed notice.

   - **Item 3, the results upload checked first** (D10):
     - the job's secret check scans `identity-results.json` with the same values as the log;
     - the upload runs only after that check has passed. After a failed check nothing is uploaded, and the log shows only the suite's own result lines.

     You may move the check into an `identity_*.py` module of the proof, with an offline test, if that makes it testable. The workflow step then calls it.

     **The reversal:** the upload unconditional, with a planted value in the JSON. It must show the check refusing. Record how the reversal was run and what it printed.
   - **The threat model:** update the record's endpoint table row for `auth/reauthenticate`, now used.
2. **The local checks:**
   - **API,** in `services/api`: `python3.12 -m venv .venv` and `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`; then, with `GLOW_ENV=test`, `manage.py check`, `manage.py test tests --verbosity 2`, `ruff check .`, `ruff format --check .` and `mypy`;
   - **the proof,** in `proofs/postgres-ordering`: the same install, then `python -m unittest discover -s tests -t . -v`, `ruff check .`, `ruff format --check .` and `mypy`;
   - **the identity suite** on a local throwaway database under D4, if Docker allows, as iteration.
3. **The run of record.** Commit and push your code, then wait for its Foundation run to finish (the push rule). Read it with your GitHub tools:
   - every job's conclusion;
   - the gate's line (`Application checks passed`);
   - the API and proof test counts;
   - the identity suite's count and time, and the identity phase's duration;
   - the secret check's lines and the upload step's result;
   - whether a toolchain retry fired.

   If it fails, stop and report the failing job and its log lines. Do not re-run it.

## 4. The record

Add a section `## Correction C1` to `docs/testing/evidence/2026-11-09-sv1-identity.md`, after the existing sections, holding:
- the start gate's results, the environment check (names only) and the toolchain versions;
- for each item: the files, the tests, the reversal and its failing output;
- what allauth 65.21.1 showed at `auth/reauthenticate` (the key, the token pair, the hooks, `session_token`), with file and line;
- every command you ran, with its result line;
- the run of record's ID, each job's result, the counts, the identity phase and whether a retry fired;
- what you could not run, and why.

Besides it, change only the endpoint table's `auth/reauthenticate` row. Commit each logical step with a clear message ending in the session's attribution lines. Push the records commit only after the run of record has finished. Then confirm:
- `git status` is clean;
- `git diff --name-only <START_SHA> HEAD` lists only your owned paths.

## 5. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch, your code head and records head;
- the start gate's and the environment check's results;
- for each of items 1 to 3: what changed, its tests, and the reversal's result;
- what 65.21.1 showed at `auth/reauthenticate`;
- each local check's result;
- the run of record: its ID, every job, the gate's line, the counts, the identity phase, the upload step and whether a retry fired;
- anything that met the stop rule, every deviation, and what you could not run.
