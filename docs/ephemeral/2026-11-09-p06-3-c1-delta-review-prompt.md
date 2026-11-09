# P06.3 C1 delta review prompt — the fixture adapter's session re-check and two guard tests

- **Owner:** App Manager 10. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 9 November 2026.**
- **Durable brief:** [P06.3 — Privacy-safe notifications at fixture scope](../planning/p06-3-notifications.md), revision 3, "Correction C1" and its "Review".
- **Where the result goes:** the report Nathan relays. The manager records it in the P06.3 record, "Delta review of correction C1", with a disposition for each finding, and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 1.97 (confidence 0.79); rung probabilities low 0.00, medium 0.17, high 0.69, extra high 0.14, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 1.00, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 1.00). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.170, Opus 5.5 at high 0.690, Opus 5.5 at extra high 0.140, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-09T02:26:49Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of the commit that holds it, which also holds C1's code (step 6).
- **Deletion condition:** prune after P06.3's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **delta review of correction C1 of P06.3**, privacy-safe notifications at fixture scope, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one exact code head. This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **P06.3's implementation** (code head `9c4fef5`) and its **exact-head review** (the record `docs/testing/evidence/2026-11-09-p06-3-notifications.md`, "Exact-head review of P06.3"): changes required, for two should-fix findings in correction classes.
  - **F-1, Codex's F-C1:** `fixture-adapter.ts`'s `settings`, `device` and `notifications` read the request's session before `await this.gate()` and acted on it after. A register in flight when its session ended committed, bound to the ended session, with its token held. The store's own flows reached it in the same task.
  - **F-2:** the server's import test read `from . import X` as `"."`, so a sibling import passed.
  - **F-3 (nit):** the mobile import scan missed `import '…'`.
- **Correction C1** (branch `claude/peaceful-feynman-ozlu2l`, code head `e807ce8`, records `9686efe`; the record, "Correction C1"):
  - the adapter resolves the session after its await;
  - the server's import test reads relative imports by name;
  - the mobile scan reads bare imports;
  - each change has its test and its reversal.

  The one non-test change is `fixture-adapter.ts`, `+6 −5`. Its run of record, push run 42549675849 on `e807ce8`: all eight jobs passed, `Application checks passed`, API 422 tests, mobile 691 unit tests, rendered `104 passed (5.3m)`, no retry.
- **The manager verified it** (the record, "Manager verification of correction C1"): the three reversals re-run, each failing. The manager branch fast-forwarded to `9686efe`.

**The code head under review is `e807ce8`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `e807ce8` (the start gate checks this).

**Your scope (a delta review, M05 S2; step 6):** every path the correction touches, read whole as it stands at `e807ce8`, not the diff alone, with the exact-head review's security focus.
- `apps/mobile/src/notifications/fixture-adapter.ts`, `fixture-adapter.test.ts`, `store.test.ts` and `fixture-scope.test.ts`;
- `services/api/tests/test_notifications.py`;
- the record's "Correction C1" and "Manager verification of correction C1";
- the guide: `git diff 9c4fef54c71829dea2820a3f9fb66f32ddad57d2 e807ce8719ca0081942081eb7b64db9c28af0bc9`.

Code the correction does not touch is out of scope. A finding there is reported as pre-existing.

**The focus:**
1. **F-1 is fixed, and nothing else changed:**
   - can any request in the adapter still act for a session that ended while it awaited, whether a read, a register, a rotate, a revoke or a settings save?
   - does the adapter now differ from the Python domain (`notifications.py`, `_session_refusal`) in anything other than refusing an ended session's request?
   - are the offline and lost-response scenarios unchanged?
   - does any other check-before-`await` pattern remain in the adapter, the store or the client?
2. **The F-1 tests are not vacuous:**
   - the two adapter tests and the eight store cases each fail under the reversal the record names (`9c4fef5`'s adapter put back);
   - the four later-task cases still pass under that reversal, which proves they test the order and not the fix;
   - none of them could pass while an ended session's request succeeds.
3. **F-2's test is true to the record's claim:**
   - `_imported_modules` reads `from . import x` as `.x`, `from .m import y` as `.m`, and `from .. import x` as its level and name;
   - the domain-module test asserts the exact set;
   - can a plausible edit still slip a sibling or parent import past it, for example an alias, a conditional import, an `importlib` call or `__import__`?
   - does it fail on harmless code?
4. **F-3's scan:**
   - it matches the bare form and every form `no-provider.test.ts` matches;
   - can a plausible import form still pass it?
   - does it fail on harmless code?
5. **No other change:** `git diff --name-only 9c4fef5 e807ce8 -- . ':(exclude)*.md'` lists only the five owned code and test paths. No existing assertion is removed or loosened, and no guard, dependency, lock, contract or model changed.
6. **The records:** every claim in "Correction C1" and "Manager verification of correction C1" holds against the code and the runs, including the line count, the test counts and the reversal outputs.

**Re-run, at least,** in a scratch copy of `e807ce8`:
- the F-1 reversal (`git show 9c4fef5:apps/mobile/src/notifications/fixture-adapter.ts` in place of the fixed file): 6 of the 29 tests in `fixture-adapter.test.ts` and `store.test.ts` fail;
- the F-2 reversal (`from . import chat_provider_stream` added to `notifications.py`): `FixtureScopeTests` fails;
- any form of focus 3 or 4 you suspect.

**What comes after this review: the correction classes.** Report every finding with its severity. A further correction pass takes every blocking finding, and any should-fix finding that could do any of these:
- let a stale session act, or leave a registration active, or a token held, after its session's end;
- let a test pass where it should fail, or weaken what a test proves;
- change runtime behavior beyond refusing an ended session's request;
- add a dependency, or change a lock, a contract or a model;
- make a record claim more than the code, the tests or the runs show.

Everything else goes into the records. For each finding, say whether it falls in one of these classes.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 10. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - **Scratch work goes in a copy outside the repository,** never the checkout (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
- **Network:** the npm registry for `npm ci --ignore-scripts`, PyPI for `pip install --require-hashes -r requirements-dev.lock`, both in a scratch copy, and GitHub through your tools, to read runs.
- **Never:**
  - dump the environment, or print a credential, token or password;
  - call Stream, Expo's push service or any other provider, or run any command in `proofs/stream-chat/`;
  - connect to any database, HDE, Railway or other external service;
  - run `playwright install`, `eas` or `migrate`, a native build, or a package install script.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If any is present, stop and report: this session must start in `Glow App - No Stream`.
3. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them.
4. **The toolchain:** Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, which you put first on PATH; CPython 3.12.14 as `python3.12`. Record their versions.
5. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, 7feba0dbc3813ab71629b3f5e0f390a64d31289f
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet e807ce8719ca0081942081eb7b64db9c28af0bc9 HEAD -- .github scripts services apps packages proofs && echo "the code head under review"
git diff --quiet e807ce8719ca0081942081eb7b64db9c28af0bc9 origin/claude/magical-wozniak-yfmmx2 -- .github scripts services apps packages proofs && echo "no code on the live branch after e807ce8"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-09-p06-3-notifications.md | grep -c -E '^#+ Delta review of correction C1'   # must print 0
```

If any check fails, stop and report. The prompt is stale if its commit is not on the live branch, if a non-Markdown path changed there after `e807ce8`, or if this review is already recorded.

**Classify the change** as root `AGENTS.md` requires, with the trusted base policy outside the candidate tree:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
```

Expected: `"full": true`. Anything else: stop and report.

**Then read, completely, at `HEAD`:**
- root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md`;
- the brief's "Correction C1";
- the record's "Exact-head review of P06.3", "Correction C1" and "Manager verification of correction C1";
- the five touched code and test files, whole; `store.ts`, `client.ts` and `transport.ts`, for focus 1; `notifications.py`'s `_session_refusal`.

**The runs,** with your GitHub tools: run 42549675849 (every job, the gate's line, the counts), and the PR run on PR41's head (event `pull_request`) once it has finished.

## 3. What to do

1. Review the five files against the focus, item by item.
2. In a scratch copy of `e807ce8`, re-run:
   - `manage.py test tests` with `GLOW_ENV=test`, `ruff` and `mypy`, and the mobile app's `npm ci --ignore-scripts` and `npm run check`;
   - the two required reversals, and any you doubt.
3. For each finding: its severity (blocking, should fix, nit), its file and line, the evidence, and whether it falls in a correction class.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- **the verdict:** approve, approve with nits, or changes required;
- the findings, in a table: number, severity, correction class or not, file and line, what is wrong, and the evidence;
- the answer to each focus point (1 to 6), one or two lines each;
- the reversals you re-ran, with their results;
- what you ran, and what you could not run or read.
