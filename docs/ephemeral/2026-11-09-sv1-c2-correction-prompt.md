# SV1 correction C2 prompt — the password-change limit, the no-link check, and the review's other findings

- **Owner:** App Manager 10. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 9 November 2026.**
- **Durable brief:** [SV1 — The identity slice](../planning/sv1-identity.md), revision 5, "Correction C2".
- **Where the result goes:**
  - on the session branch: the session's changes, and the record's new section "Correction C2" in `docs/testing/evidence/2026-11-09-sv1-identity.md`;
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification, and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.28 (confidence 0.78).
    - Rung probabilities: low 0.00, medium 0.02, high 0.69, extra high 0.27, max 0.02, ultracode 0.00.
    - Model probabilities: Fable 5.1 0.00, Opus 5.5 1.00, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 1.00).
    - Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.020, Opus 5.5 at high 0.690, Opus 5.5 at extra high 0.270, Opus 5.5 at max 0.020, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000.
    - Flags: none.
    - Sent 2026-11-09T17:29:16Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs (DM-48 section 2). This prompt authorizes no credential use and no live provider action.
- **Which session:** C1's session, on its branch `claude/stoic-franklin-ief71e`, is the natural home, since it built C1 and its local harness. A new session can run it equally well, on its own branch.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of the commit that holds it (step 6). Then:
  - the manager's verification;
  - Codex on C2's head;
  - a delta review of C2 on S2's terms, with the exact-head review's security focus.
- **Deletion condition:** prune after SV1's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are **correction C2 of SV1**, the identity slice, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **SV1** (PR42) builds maintained sign-in on django-allauth 65.21.1 headless, in `services/api/glow_identity`.
  - Its identity suite runs on a second disposable database in the Database proof checks job.
  - Its record is `docs/testing/evidence/2026-11-09-sv1-identity.md`.
  - Correction C1 added reauthentication before an address change and gated the results upload, at code head `bda299e`.
- **SV1's exact-head review of `bda299e`** asked for changes, with no blocking finding (the record, "Exact-head review of SV1"). Among its findings:
  - **F-1:** the suite's no-link mail check forbids `http` and `www.`, and an allauth code can spell either. A code group `HTTP`, or a code ending `WWW` before the sentence's full stop, fails a correct message: about 0.8 percent of runs. Codex raised it on PR42 (P2, `identity_cases.py`, lines 1639 to 1641).
  - **F-2:** at `POST account/password/change`, a wrong current password is checked by `check_password` alone and consumes only `change_password`, allauth's `5/m/user`, never `login_failed`. So a holder of a live session key or access token gets 25 guesses per 300 seconds there, beside the sign-in form's 5. Codex raised it on PR42 (P2, `conf.py`, lines 70 to 71).
  - **F-3:** the record says migration 0004's SHA-256 is pinned, but no test pins it.
  - **The nits F-4, F-5 and F-7,** and **F-6**, on N2's words for the replay check's order.
- **The Dev Manager approved this correction** (DM-48, `docs/continuity/dev-manager/reviews/2026-11-09-dm-48-sv1-review-c2.md`) with conditions C2.1 to C2.8 in given words. The brief's revision 5 applies them:
  - C2.1 and C2.2 in D3;
  - C2.3 as acceptance check 11;
  - C2.6 in D10;
  - C2.8's first replacement in D2;
  - the rest, and the items, owned paths, exclusions and stop rule, in "Correction C2".

  **The brief's "Correction C2" is your specification.** Read it whole.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 10. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only "Correction C2"'s owned paths:
    - `services/api/glow_identity/conf.py`;
    - `services/api/glow_identity/strategy.py`: the module docstring only;
    - `services/api/tests/test_identity_offline.py`;
    - `services/api/tests/test_model_definitions.py`: the `pinned` dictionary only;
    - `proofs/postgres-ordering/glow_ordering_proof/identity_*.py`;
    - `proofs/postgres-ordering/tests/test_identity_offline.py`;
    - `.github/workflows/foundation.yml`: the step "SV1: run the identity suite" only, its secret check and what it prints;
    - `docs/architecture/data-model.md` and `docs/architecture/production-contracts.md`: the replay sentence only;
    - the record:
      - the D3 row of "Facts read from the installed source";
      - the endpoint row for `POST account/password/change`;
      - the focus bullet on a replayed rotated refresh token;
      - its new section "Correction C2".

    A reversal is a temporary edit and may touch another file, such as `authentication.py`, if it is undone before you commit.
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule.** Stop and report, with no further change, if any of these holds:
  - **allauth 65.21.1, at `account/password/change`:**
    - with `change_password` at `5/300s/user`, its limiter does not refuse a sixth request sent more than 60 seconds after the first of five;
    - the override does not merge into allauth's defaults, so another limit changes with it.

    Report what the source shows, with file and line.
  - **An owned path:** a fix seems to need a path outside the list, or a change to `strategy.py` or `authentication.py` beyond `strategy.py`'s docstring.
  - **A dependency:** it seems to need a new package.
  - **The timeout:** the Database proof checks job cannot stay within its 30-minute timeout.
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished. Push your records commit only after the run of record has finished.
- **Network:**
  - PyPI, for `pip install --require-hashes`;
  - Docker Hub, only to pull the PostgreSQL image the CI job pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`) for a local run.
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
git switch -C <your session branch> <START_SHA>   # C1's session: claude/stoic-franklin-ief71e; <START_SHA> already contains its 96dc3e2
git rev-parse HEAD                                  # must print <START_SHA>
git diff --name-only bda299e3034121b2cc20318024f35f5938f83b4c HEAD -- .github scripts services apps packages proofs | grep -v -E '\.md$'   # must print nothing: the code is bda299e's
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/api proofs/postgres-ordering .github docs/architecture/data-model.md docs/architecture/production-contracts.md 'docs/testing/evidence/*sv1-identity*'   # must print nothing
grep -c -E '^#+ Correction C2' docs/testing/evidence/2026-11-09-sv1-identity.md   # must print 0
grep -c 'change_password' services/api/glow_identity/conf.py   # must print 0
```

If a check fails, stop and report. The prompt is stale if any of these holds:
- `<START_SHA>` is not on the live manager branch;
- an owned path changed there after it;
- "Correction C2" is already recorded.

**Then read, completely:**
- **The repository's instructions:** root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`; `proofs/postgres-ordering/README.md`.
- **The brief,** revision 5: D2, D3, D10, the acceptance checks and "Correction C2".
- **DM-48's report,** whole.
- **The record:**
  - "Facts read from the installed source";
  - "The threat model's inputs";
  - "Correction C1";
  - "Exact-head review of SV1", with its threat model and findings.
- **The code:**
  - `glow_identity/conf.py`;
  - in the identity suite:
    - `mail.no_link_no_stranger`;
    - `ratelimit.failed_sign_ins`;
    - `config.settings_as_briefed`;
    - `identity_support.py`'s `clock_ahead` and `code_since`;
    - how `run_case` clears the rate-limit cache between cases;
  - the API's `SettingsFragmentTests` and `StaticGuardTests`;
  - `test_model_definitions.py`'s `pinned` dictionary;
  - the step "SV1: run the identity suite", whole, and the proof's `IdentityUploadGateTests`.
- **allauth 65.21.1:**
  - `core/internal/ratelimit.py` whole: `cache_lock`, `parse_rate`, `consume` and the decorator;
  - `headless/account/views.py`'s `ChangePasswordView`;
  - `headless/account/inputs.py`'s `ChangePasswordInput`;
  - `headless/base/views.py`'s `AuthenticatedAPIView`;
  - `account/app_settings.py`'s `RATE_LIMITS`;
  - `account/adapter.py`'s `generate_password_reset_code` and `generate_email_verification_code`.

## 3. What to do

1. **The items of "Correction C2", in order.** For each: the change, its test, and its reversal. A reversal is a temporary edit that must make the test fail; run it, then undo it. Record the edit and the failing output.
   - **Item 1, the password-change limit** (F-2; D3; acceptance check 11):
     - **The setting:** `ACCOUNT_RATE_LIMITS = {"change_password": "5/300s/user"}` in SV1's fragment. The fragment's rate-limit comment says what D3 now says.
     - **The settings case and the API's fragment test** check:
       - the value;
       - that allauth's resolved limits keep every other default.
     - **A new identity case for acceptance check 11's second sentence,** with every clause of its words:
       - five requests at `account/password/change` with a wrong current password are each refused;
       - then a sixth, with the right current password and a valid new password, is refused as too many. Send it with the limiter's clock more than 60 and less than 300 seconds after the first of the five;
       - the password is unchanged: the old password still signs in.

       Record the status and error code 65.21.1 gives the sixth.
     - **The clock** (DM-48 section 3):
       - `clock_ahead` replaces a module's `time` with an object that has only `time()`;
       - allauth's `cache_lock` also calls `time.monotonic()` and `time.sleep()` (`core/internal/ratelimit.py:47-56`).

       So the object that moves the limiter's clock keeps both, and the existing cases see no change.
     - **The existing `ratelimit.failed_sign_ins`** stays as the check's first sentence.
     - **The reversal:** the override removed, which restores allauth's default `5/m/user`. It must fail:
       - the new case, since the sixth is accepted and the password changes;
       - the settings case;
       - the fragment test.
     - **The record:**
       - the D3 row of "Facts read from the installed source" and the endpoint row for `POST account/password/change` name the new limit;
       - "Correction C2" states threat 6 with C2.4's words, from the brief.
   - **Item 2, the no-link check** (F-1; test-only). C2.5, word for word:

     > The check removes the exact code the case issued, every occurrence, before it looks for `http` and `www.`. It removes nothing else and uses no pattern, so a link anywhere else in the message still fails it.

     - **Where the code comes from:** where it was issued, not a pattern over the message. For example, the suite can record each code that allauth's adapter generates.
     - **The removal:** a literal replacement of that exact string.
     - **Three deterministic cases,** each with a reversal that fails it:
       - a message of Glow's whose code is `HTTP-BCDF` passes;
       - so does one whose code is `BCDF-GWWW`, ending its sentence;
       - a message with a real link fails.

       They may be offline tests of the check, if you make it a function the suite's case calls.
   - **Item 3, migration 0004's hash** (F-3):
     - its SHA-256 goes in `test_model_definitions.py`'s `pinned` dictionary;
     - **the reversal:** a temporary one-byte change to the migration. It must fail the test.
   - **Item 4, counts only** (F-4; D10). After a failed secret check, the step prints counts only, never a line of the suite's output.
     - The step's comment and its message change with it.
     - An offline test in `IdentityUploadGateTests` shows that the failed branch prints no line of the log.
     - **The reversal:** the old `grep` restored. It must fail that test.
   - **Item 5, the static guard** (F-5). In the API's `StaticGuardTests`:
     - **More forbidden names:** `request.query_params`, `request.GET`, `request.POST`, `request.COOKIES` and a lowercase `session_token`.
     - **The call:** an assertion that `actor_for` is called with exactly `user, payload`.
     - **C2.7, word for word:**

       > The guard also checks, on the module's syntax tree, that `authentication.py`'s code uses `request` only as the parameter of `authenticate` and `authenticate_header`, and as the argument it passes to allauth's `JWTTokenAuthentication` methods of the same names.

     - **The code stays:** `authentication.py` already meets it.
     - **The reversals,** each a temporary edit to `authentication.py` that must fail the guard:
       - a read of `request.GET`;
       - a `getattr(request, …)`;
       - a third argument to `actor_for`.
   - **Item 6, the verification settings** (F-7):
     - `config.settings_as_briefed` pins `ACCOUNT_EMAIL_VERIFICATION_SUPPORTS_CHANGE` and `ACCOUNT_EMAIL_VERIFICATION_SUPPORTS_RESEND` off;
     - "Correction C2"'s threat model names them;
     - **the reversal:** one of them turned on. It must fail the case.
   - **Item 7, N2's words** (F-6; C2.8, replacements 2 to 6). Apply each word for word; line breaks may move. The code's order of checks stays.
     - **`glow_identity/strategy.py`,** the module docstring only. Replace "run with allauth's own functions in allauth's order:" with:
       > run with allauth's own functions in this order:
     - **`docs/architecture/data-model.md`,** the replay sentence, **and `docs/architecture/production-contracts.md`,** "The app mapping as built". Replace "passes allauth's own checks, in allauth's order, but carries" with:
       > passes allauth's own checks, its signature first, but carries
     - **The record,** "The review plan's security focus", the bullet on a replayed rotated refresh token, corrected in place. Replace "after allauth's own checks, in allauth's order, and adds no cryptography" with:
       > after allauth's own checks, its signature first, and adds no cryptography

       "Correction C2" notes the change.
     - **`services/api/tests/test_identity_offline.py`,** the comment in `test_the_replay_check_reads_no_session_before_allauths_own_checks` only. Replace "only after allauth's own checks, in allauth's order." with:
       > only after allauth's own checks, its signature first.

     **The check:** afterwards, `git grep -n "allauth's order" -- services proofs docs/architecture` prints nothing. In the record, the phrase appears only where "Correction C2" quotes the old words.
2. **The local checks:**
   - **API,** in `services/api`:
     - `python3.12 -m venv .venv` and `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`;
     - then, with `GLOW_ENV=test`: `manage.py check`, `manage.py test tests --verbosity 2`, `ruff check .`, `ruff format --check .` and `mypy`.
   - **The proof,** in `proofs/postgres-ordering`:
     - the same install;
     - then `python -m unittest discover -s tests -t . -v`, `ruff check .`, `ruff format --check .` and `mypy`.
   - **The identity suite** on a local throwaway database under D4, if Docker allows, as iteration.
3. **The run of record.** Commit and push your code, then wait for its Foundation run to finish (the push rule). Read it with your GitHub tools:
   - every job's conclusion;
   - the gate's line (`Application checks passed`);
   - the API and proof test counts;
   - the identity suite's count and time, and the identity phase's duration;
   - the secret check's lines and the upload step's result;
   - whether a toolchain retry fired.

   If it fails, stop and report the failing job and its log lines. Do not re-run it.

## 4. The record

Add a section `## Correction C2` to `docs/testing/evidence/2026-11-09-sv1-identity.md`, after the existing sections. It holds:
- the start gate's results, the environment check (names only) and the toolchain versions;
- for each item:
  - the files;
  - the tests;
  - the reversal and its failing output;
- **what 65.21.1 showed at `account/password/change`,** with file and line:
  - when the limiter counts;
  - the sixth request's answer;
  - that the override merges;
- **its threat model:**
  - threat 6 in C2.4's words;
  - threat 7 with F-1's fix;
  - the two verification settings (F-7);
  - the guard (F-5);
- the note on the focus bullet corrected in place;
- every command you ran, with its result line;
- the run of record's ID, each job's result, the counts, the identity phase and whether a retry fired;
- what you could not run, and why.

Besides that section, change only the three rows and the bullet that the owned paths name. The review's section and its threat model keep their words.

Commit each logical step with a clear message ending in the session's attribution lines. Push the records commit only after the run of record has finished. Then confirm:
- `git status` is clean;
- `git diff --name-only <START_SHA> HEAD` lists only your owned paths;
- `git diff --stat <START_SHA> HEAD -- services/api/glow_identity .github` gives the non-test line count.

## 5. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch, your code head and records head;
- the start gate's and the environment check's results;
- for each of items 1 to 7: what changed, its tests, and the reversal's result;
- what 65.21.1 showed at `account/password/change`;
- the non-test line count;
- each local check's result;
- the run of record: its ID, every job, the gate's line, the counts, the identity phase, the upload step and whether a retry fired;
- anything that met the stop rule, every deviation, and what you could not run.
