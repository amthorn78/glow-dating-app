# SV1 C2 delta review prompt — the password-change limit, the no-link check, and the review's other findings

- **Owner:** App Manager 10. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 9 November 2026.**
- **Durable brief:** [SV1 — The identity slice](../planning/sv1-identity.md), revision 5, "Correction C2" and its "After C2".
- **Where the result goes:** the report Nathan relays. The manager records it in the SV1 record, "Delta review of correction C2", with a disposition for each finding, and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.09 (confidence 0.85).
    - Rung probabilities: low 0.00, medium 0.07, high 0.78, extra high 0.15, max 0.00, ultracode 0.00.
    - Model probabilities: Fable 5.1 0.00, Opus 5.5 1.00, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 1.00).
    - Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.070, Opus 5.5 at high 0.780, Opus 5.5 at extra high 0.150, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000.
    - Flags: none.
    - Sent 2026-11-09T18:24:57Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of the commit that holds it, which also holds C2's code (step 6).
- **Deletion condition:** prune after SV1's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **delta review of correction C2 of SV1**, the identity slice, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one exact code head. This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **SV1** (PR42) builds maintained sign-in on django-allauth 65.21.1 headless, in `services/api/glow_identity`. Its identity suite runs on a second disposable database in the Database proof checks job. Its record is `docs/testing/evidence/2026-11-09-sv1-identity.md`.
- **SV1's exact-head review of `bda299e`** asked for changes, with no blocking finding (the record, "Exact-head review of SV1"). The record holds the review's threat model and its findings F-1 to F-9.
- **The Dev Manager approved correction C2** (DM-48, `docs/continuity/dev-manager/reviews/2026-11-09-dm-48-sv1-review-c2.md`) with C2.1 to C2.8 in given words. The brief's revision 5 applies them, in D2, D3, D10, acceptance check 11 and "Correction C2".
- **Correction C2** (branch `claude/trusting-goldberg-e4ogat`, code head `6da8061`, records `080c9a9`; the record, "Correction C2"):
  - **F-2:** `change_password` at `5/300s/user`, merged into allauth's defaults, with a new identity case, `ratelimit.password_change`. The suite's `clock_ahead` keeps `monotonic` and `sleep`;
  - **F-1:** the no-link check removes the exact codes issued, recorded where Glow's adapter generates them, before it looks for `http` and `www.`;
  - **F-3:** migration 0004's hash pinned;
  - **F-4:** counts only after a failed secret check;
  - **F-5:** the static guard widened, with an allow-list on `request`;
  - **F-7:** the two verification settings pinned off;
  - **F-6:** N2's words in a docstring, a test comment and two architecture documents.

  Each item has its tests and its reversals. The non-test lines are 3 files, `+19 −8`.
- **C2's run of record:** push run 42669825647 on `6da8061`.
  - All eight jobs passed, with `Application checks passed` and no retry.
  - API: 453 tests. Proof: 193 tests.
  - The identity suite passed 49 of 49, its scan clean.
- **The manager verified it** (the record, "Manager verification of correction C2"):
  - it re-ran the offline suites;
  - it ran four reversals of its own, each failing;
  - it read the run of record and the workflow diff whole;
  - it fast-forwarded the manager branch to `080c9a9`.

**The code head under review is `6da8061`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `6da8061` (the start gate checks this).

**Your scope (a delta review, M05 S2; step 6):** every path the correction touches, read whole as it stands at `6da8061`, not the diff alone, with the exact-head review's security focus.
- **The settings and the replay strategy:** `services/api/glow_identity/conf.py`, and `strategy.py`'s docstring.
- **The API's tests:** `services/api/tests/test_identity_offline.py` and `test_model_definitions.py`.
- **The identity suite:** `proofs/postgres-ordering/glow_ordering_proof/identity_cases.py` and `identity_support.py`, and `proofs/postgres-ordering/tests/test_identity_offline.py`.
- **The workflow:** `.github/workflows/foundation.yml`, the step "SV1: run the identity suite", with the steps around it.
- **The architecture texts:** in `docs/architecture/data-model.md` and `production-contracts.md`, the replay sentence.
- **The record:**
  - its "Correction C2" and "Manager verification of correction C2";
  - the D3 row of "Facts read from the installed source";
  - the endpoint row for `POST account/password/change`;
  - the focus bullet on a replayed rotated refresh token;
  - the migration 0004 commands row.
- **The guide:** `git diff bda299e3034121b2cc20318024f35f5938f83b4c 6da8061169c4760b8419fc649c6d5aad57f29b50`, and `git diff 2f577f89b53c48b493702eebafad9181d9e7a0d4 <PROMPT_SHA>` for the records.

Code the correction does not touch is out of scope. A finding there is reported as pre-existing.

**The focus** (DM-48 section 4, with the exact-head review's threat model):
1. **The limit, its case and its reversal** (F-2; C2.1, C2.3):
   - `change_password` resolves to 5 per 300 seconds per account, and every other limit keeps allauth's default;
   - `ratelimit.password_change` tells `5/300s` from `5/m`: the sixth request is sent more than 60 seconds after the first, it is refused, and the password is unchanged;
   - the reversal, allauth's default restored, fails the case;
   - can the moved clock reach any other case, or any module but the limiter's?
   - **D3's budget claim** (DM-48 section 7's prevention): list every endpoint of 65.21.1's `app` client at which a signed-in caller can test a password, with its limiter. Is anything missing beyond the sign-in form, `auth/reauthenticate` and `account/password/change`? Does any of them consume neither `login_failed` nor `change_password`?
2. **The exact-code removal** (F-1; C2.5):
   - the codes are recorded where Glow's adapter generates them;
   - the removal is literal, of exactly those strings, with no pattern;
   - can a real link, or a name but Glow's, pass the check?
   - the check removes every code the run issued from each message, not only that message's own. Does that weaken anything?
   - is a message's code ever generated outside the two wrapped methods, so that a correct message could still fail?
   - do the recorded codes reach any output, or only the secret ledger?
3. **The workflow hunk** (F-4; C2.6):
   - after a failed secret check, the step prints counts only, never a line of the suite's output;
   - the step still fails;
   - the upload stays gated on `scan == 'passed'`;
   - the hunk lies inside the step "SV1: run the identity suite";
   - does `grep -c`, under the step's `-e -o pipefail`, behave as the offline test shows?
4. **The guard** (F-5; C2.7):
   - the forbidden names and the syntax-tree allow-list;
   - can a plausible form still let `authentication.py` read the request, such as `vars(request)`, a keyword argument, `*args`, a lambda or a nested function?
   - does the guard fail on harmless code?
5. **C2.8's code changes** are a docstring and a comment only, and the replay check's order of checks is unchanged.
6. **F-3's and F-7's pins:**
   - 0004's pinned hash is the file's;
   - F-7 pins both the settings and the counts 65.21.1 reads (`EMAIL_VERIFICATION_MAX_CHANGE_COUNT` and `…_MAX_RESEND_COUNT`, `account/app_settings.py:122-140`).
7. **No other change:**
   - `git diff --name-only bda299e 6da8061 -- . ':(exclude)*.md'` lists only the correction's code and test paths;
   - no existing assertion is removed or loosened;
   - no dependency, lock, contract, model or migration changed;
   - `authentication.py` is unchanged.
8. **The records:** every claim in "Correction C2" and "Manager verification of correction C2" holds against the code and the runs, including:
   - the line count, the test counts and the reversal outputs;
   - the records push run 42671723917, which had no job.

**Re-run, at least,** in a scratch copy of `6da8061`:
- the F-2 reversal (the `ACCOUNT_RATE_LIMITS` line removed from `conf.py`): the API's fragment and merge tests fail;
- the F-1 reversal (the removal in `mail_forbidden_found` disabled): the `HTTP-BCDF` and `BCDF-GWWW` cases fail;
- the F-4 reversal (the old `grep` put back in the failed branch): the counts-only test fails;
- any form of focus 2 or 4 you suspect.
- **The identity suite, informational:** on a throwaway PostgreSQL under P06.DB's D4, if Docker allows. You name it informational. If you can run it, add the F-2 reversal there.

**What comes after this review: the correction classes.** Report every finding with its severity. A further correction pass takes every blocking finding, and any should-fix finding that could do any of these:
- let a credential, code, token, session key, key or secret reach a log, a message, a response, a CI log or an artifact;
- give a holder of a live session key or access token more password guesses than D3 states;
- let an account be taken over, or an address moved, without the member's password;
- let the actor take its session from anything but the token's own `sid`;
- let a test pass where it should fail, or fail where the code is right;
- change runtime behavior beyond the one rate limit;
- add a dependency, or change a lock, a contract or a model;
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
  - PyPI, for `pip install --require-hashes -r requirements-dev.lock` in a scratch copy, and for reading `django-allauth`'s release;
  - Docker Hub, only to pull the PostgreSQL image the CI job pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`);
  - GitHub, through your tools, to read runs.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions):
  - a throwaway PostgreSQL in Docker, from that image, on loopback only;
  - a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present;
  - removed afterwards.
- **Never:**
  - dump the environment, or print a credential, password, code, token, session key or key;
  - call any provider, send any real email, or run any command in `proofs/stream-chat/`;
  - connect to any database but a throwaway one you started under D4's conditions, HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:**
   `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`.
   If any is present, stop and report.
2. **No `STREAM_*` or `PG*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG)'` prints names only. If any is present, stop and report.
3. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
4. **The toolchain:** CPython 3.12.14 as `python3.12`, and Docker if present. Record their versions.
5. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, 8d2de724091f2a7127d207fbc557ea1ced57f690
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 6da8061169c4760b8419fc649c6d5aad57f29b50 HEAD -- .github scripts services apps packages proofs ':!*.md' && echo "the code head under review"
git diff --quiet 6da8061169c4760b8419fc649c6d5aad57f29b50 origin/claude/magical-wozniak-yfmmx2 -- .github scripts services apps packages proofs ':!*.md' && echo "no code on the live branch after 6da8061"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-09-sv1-identity.md | grep -c -E '^#+ Delta review of correction C2'   # must print 0
```

If any check fails, stop and report. The prompt is stale if any of these holds:
- its commit is not on the live branch;
- a non-Markdown path changed there after `6da8061`;
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
- **The repository's instructions:** root `AGENTS.md` and `CLAUDE.md`, and `services/api/README.md`.
- **The brief,** revision 5: D2, D3, D10, the acceptance checks and "Correction C2".
- **DM-48's report,** whole.
- **The record:**
  - "Facts read from the installed source";
  - "The threat model's inputs";
  - "Exact-head review of SV1";
  - "Correction C2";
  - "Manager verification of correction C2".
- **Every path in your scope, whole.** For focus 4, also read `authentication.py`.
- **allauth 65.21.1:**
  - `core/internal/ratelimit.py`;
  - `headless/account/views.py` and `inputs.py`;
  - `headless/base/views.py`;
  - `account/app_settings.py`;
  - the adapter's code generators;
  - for focus 1, every `app` route that checks a password.

**The runs,** with your GitHub tools:
- run 42669825647: every job, the gate's line, the counts and the identity step's lines;
- run 42671723917;
- the PR run on PR42's head (event `pull_request`), once it has finished.

## 3. What to do

1. Review the paths in scope against the focus, item by item.
2. In a scratch copy of `6da8061`, re-run:
   - in `services/api`: `manage.py check` and `manage.py test tests` with `GLOW_ENV=test`, `ruff` and `mypy`;
   - in `proofs/postgres-ordering`: the offline tests, `ruff` and `mypy`;
   - the three required reversals, and any you doubt;
   - the identity suite locally under D4 if you can, informational.
3. For each finding: its severity (blocking, should fix, nit), its file and line, the evidence, and whether it falls in a correction class.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- **the verdict:** approve, approve with nits, or changes required;
- the findings, in a table: number, severity, correction class or not, file and line, what is wrong, and the evidence;
- the answer to each focus point (1 to 8), one or two lines each, with focus 1's list of endpoints;
- the reversals you re-ran, with their results, the local database ones named informational;
- what you ran, and what you could not run or read.
