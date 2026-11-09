# P06.3 correction C1 prompt — the fixture adapter's session race, and two guard tests

- **Owner:** App Manager 10. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 9 November 2026.**
- **Durable brief:** [P06.3 — Privacy-safe notifications at fixture scope](../planning/p06-3-notifications.md), revision 3, "Correction C1".
- **Where the result goes:**
  - the session's changes, and the record's new section "Correction C1" in `docs/testing/evidence/2026-11-09-p06-3-notifications.md`, on its own branch;
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 1.87 (confidence 0.82); rung probabilities low 0.00, medium 0.20, high 0.73, extra high 0.07, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.99, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.99). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.198, Opus 5.5 at high 0.723, Opus 5.5 at extra high 0.069, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.002, Sonnet 5.5 at high 0.007, Sonnet 5.5 at extra high 0.001, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-09T01:48:45Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The fix makes the adapter do what DM-44 1.2 already says (the brief, "Correction C1"). This prompt authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of the commit that holds it (step 6). A delta review follows if the correction is 60 or fewer non-test lines.
- **Deletion condition:** prune after P06.3's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are **correction C1 of P06.3**, privacy-safe notifications at fixture scope, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **P06.3's implementation** (code head `9c4fef5`, on PR41) built the notification composer and F12's devices and settings in `services/api/glow_domain`, and the mobile settings screen in `apps/mobile/src/notifications/`.
- **The exact-head review asked for changes** (the record `docs/testing/evidence/2026-11-09-p06-3-notifications.md`, "Exact-head review of P06.3"):
  - **F-1, Codex's F-C1, confirmed:** `fixture-adapter.ts`'s `settings`, `device` and `notifications` read the request's session before `await this.gate()` and act after. `ended()` sweeps the session's registrations synchronously, so a register that started before `ended()` commits afterwards, bound to the ended session, with its token held. **The store's own flows reach it:** `setKind('match', true)` then `owner.logout()`, or an account change, in the same task, with the permission preset `granted` or `undetermined_allow`. The adapter's events end `session_ended, register`, the registration is active on the ended session, and `heldTokens` is 1. A logout in a later task does not reach it. No other place has the pattern.
  - **F-2:** `FixtureScopeTests` in `services/api/tests/test_notifications.py` records a relative import as its dots plus module name, so `from . import X` reads as `"."` for any X. The probe `from . import chat_provider_stream` passes all four tests, yet the record claims the module "imports only the standard library, `.chat` and `.provider_fixtures`".
  - **F-3 (nit, in C1):** `apps/mobile/src/notifications/fixture-scope.test.ts`'s import scan misses the bare side-effect form `import '…'`.
- **The brief's revision 3, "Correction C1",** is your specification: items 1 to 4, the owned paths, the exclusions and the review. Read it whole.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 10. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only "Correction C1"'s owned paths:
    - `apps/mobile/src/notifications/fixture-adapter.ts`, `fixture-adapter.test.ts`, `store.test.ts` and `fixture-scope.test.ts`;
    - `services/api/tests/test_notifications.py`;
    - the record, for its new section "Correction C1" only;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule.** Stop and report, with no further change, if any of these holds:
  - the fix seems to need a change outside the owned paths, such as `store.ts`, `client.ts`, `notifications.py`, `notification_fixtures.py`, a guard or the layout;
  - it seems to need a dependency, lock, contract or model change;
  - the adapter's semantics would differ from the Python domain's in any way other than refusing an ended session's request.
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished. Push your records commit only after the run of record has finished.
- **Network:** the npm registry for `npm ci --ignore-scripts`, and PyPI for `pip install --require-hashes -r requirements-dev.lock`.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, token or password. Synthetic tokens are test data; make them obviously synthetic;
  - call Stream, Expo's push service or any other provider, or run any command in `proofs/stream-chat/`;
  - connect to any database, HDE, Railway or other external service;
  - run `playwright install`, `eas`, `eas-cli`, `migrate` or a native build;
  - run package install scripts: always `npm ci --ignore-scripts`;
  - weaken or delete a test to make the suite pass.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If any is present, stop and report: this session must start in `Glow App - No Stream`.
3. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them.
4. **The toolchain:** Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, which you put first on PATH in every process; CPython 3.12.14 as `python3.12`. Record their versions.
5. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API). The proxy and CA variables pass by reference, never printed.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git diff --quiet 9c4fef54c71829dea2820a3f9fb66f32ddad57d2 HEAD -- .github scripts services apps packages proofs && echo "the code is 9c4fef5's"
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- apps/mobile services/api   # must print nothing
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-09-p06-3-notifications.md | grep -c -E '^#+ Correction C1'   # must print 0
```

If a check fails, stop and report. The prompt is stale if `<START_SHA>` is not on the live manager branch, if an owned path changed there after it, or if "Correction C1" is already recorded.

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md`;
- the brief's "Correction C1";
- the record's "Exact-head review of P06.3", and the "Outcome 2" and "Outcome 3" tables;
- `apps/mobile/src/notifications/fixture-adapter.ts`, `store.ts`, `transport.ts`, `fixture-adapter.test.ts`, `store.test.ts` and `fixture-scope.test.ts`;
- `services/api/glow_domain/notifications.py`'s session check (`_session_refusal`), and `test_notifications.py`'s `FixtureScopeTests`.

## 3. What to do

1. **Items 1 to 3 of "Correction C1",** in order. For each: the change, the test, and the reversal, a temporary edit that must make the test fail, run and then undone. Record the edit and the failing output. Item 1 has two tests, the adapter's and the store's: the reversal (the session taken before the await and used after, as at `9c4fef5`) must fail both. The store's tests cover a logout and an account change in the same task, each with the presets `granted` and `undetermined_allow`. The later-task case keeps passing.
2. **Count the non-test lines** your code changes (`git diff --numstat` without the test files) and record the count: 60 or fewer gets a delta review.
3. **The local checks:**
   - **API,** in `services/api`: `python3.12 -m venv .venv`, `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`; then, with `GLOW_ENV=test`, `manage.py check`, `manage.py test tests --verbosity 2`, `ruff check .`, `ruff format --check .` and `mypy`;
   - **mobile,** in `apps/mobile`: `npm ci --ignore-scripts` and `npm run check`.
4. **The run of record.** Commit and push your code, then wait for its Foundation run to finish (the push rule). Read it with your GitHub tools:
   - every job's conclusion;
   - the gate's line (`Application checks passed`);
   - the API test count, the mobile unit count and the rendered count;
   - whether a toolchain retry fired.

   If it fails, stop and report the failing job and its log lines. Do not re-run it.

## 4. The record

Add a section `## Correction C1` to `docs/testing/evidence/2026-11-09-p06-3-notifications.md`, after the existing sections, holding:
- the start gate's results, the environment check (names only) and the toolchain versions;
- for each item: the files, the test, the reversal and its failing output;
- the non-test line count;
- every command you ran, with its result line;
- the run of record's ID, each job's result, the counts and whether a retry fired;
- what you could not run, and why.

Change no other section. Commit each logical step with a clear message ending in the session's attribution lines. Push the records commit only after the run of record has finished. Confirm that `git status` is clean, and that `git diff --name-only <START_SHA> HEAD` lists only your owned paths.

## 5. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch, your code head and records head;
- the start gate's and the environment check's results;
- for each of items 1 to 3: what changed, its tests, and the reversal's result;
- the non-test line count;
- each local check's result, and the run of record: its ID, every job, the gate's line, the counts and whether a retry fired;
- anything that met the stop rule, every deviation from the brief, and what you could not run.
