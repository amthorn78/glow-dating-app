# SV4 A1-C2 prompt — the version detector's docstring: what it scans and what its tests show

- **Owner:** App Manager 13. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 22 November 2026.**
- **Durable brief:** [SV4 — the chat and notifications slice](../planning/sv4-chat-notifications.md), revision 7. **The findings:** D1-1, N1 and N2, in the SV4 record's "Delta review of A1-C1" (`docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`), with its disposition table.
- **Where the result goes:**
  - the session's change to the one file below, and its section "A1-C2" in the same record, on its own branch;
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification to the record, and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at medium.** Effort score 1.39 (confidence 0.73); rung probabilities low 0.01, medium 0.60, high 0.39, extra high 0.00, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.92, Sonnet 5.5 0.08, Haiku 5.5 0.00 (confidence 0.89). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.009, Opus 5.5 at medium 0.552, Opus 5.5 at high 0.359, Opus 5.5 at extra high 0.000, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.001, Sonnet 5.5 at medium 0.048, Sonnet 5.5 at high 0.031, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-22T09:00:03Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. This prompt authorizes no credential use and no live provider action (the charter, "Read before it takes effect"). Under D-07 the correction goes on the list for Dev Manager 7's pre-merge read of A1 (DM-98).
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and none may be present. `amthorn78/glow-docs` is attached, read-only; this work needs nothing from it (OD-74).
- **It runs alone** (OD-29). Then, in order: the manager's verification; PR58's run and Codex's review of its new head; a delta review of C2; Dev Manager 7's pre-merge read of A1; the merge.
- **Deletion condition:** prune after A1's pull request (PR58) merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch.

---

You are the **correction session A1-C2** for SV4 A1, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **A1** (code head `bc0675d`) built the rules chat's routes will serve; PR58 carries it into `main` (`499ccbb`). Its D6 test, `services/api/tests/test_match_versions_offline.py`, pins every writer of a match's `version` and `contact_version`, with a static detector (`functions()`, `writes()` and their helpers) and `WriterDetectorTests`.
- **A1-C1** (code head `f69529c`; the record's "A1-C1") rewrote that module's docstrings so they no longer claimed the detector misses no writer (AR-2).
- **C1's delta review** (the record's "Delta review of A1-C1") asked for changes on one point, **D1-1**: line 8 still says "a detector scans every function in the API's code", but `functions()` (lines 53 to 63) collects only top-level `def` functions and the `def` methods of top-level classes; a top-level `async def` function or `async def` method, or a method of a class nested in a top-level class, is never scanned (three probes gave `found={}`). Two nits are in the same lines:
  - **N1:** line 15, "`WriterDetectorTests` shows each of these forms is found". The save form's one example (line 249) also writes `match.version += 1`; with the save branch of `writes` (line 160) deleted, `WriterDetectorTests` still passes, and `MatchVersionTests.test_each_writer_advances_both_by_one_and_saves_both` fails for both writers.
  - **N2:** a match obtained through a helper and a `save()` override escape only for `version`; an assignment to an object's `contact_version` is found however the object was obtained. Line 24 is a ragged wrap.
- **The manager's disposition:** D1-1, N1 and N2 are fixed now, by you, in that one passage. N3 to N5 are carried or recorded; you do not take them up.

**This correction changes one docstring passage and one class docstring only.** No code, detector, test, assertion, application behaviour, workflow, setting, contract or proof changes.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 13. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only these paths:
    - `services/api/tests/test_match_versions_offline.py`: its module docstring's passage from "Read from the source" (line 8) to "Each function the detector finds must be one of the pinned writers," (lines 23 and 24), and `WriterDetectorTests`' docstring (lines 240 and 241), only;
    - the record, section "A1-C2" only;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: use the GitHub tools where your session has them, otherwise `gh api` REST `GET` calls, and say in the report which you used. No pull request, comment, review, thread resolution, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule.** Stop and report, with no further change, if any of these holds:
  - **a path:** the work needs any path or passage outside the list above, the detector's code above all;
  - **a claim:** the passage cannot be made true without changing code or a test;
  - **a probe or a reversal:** a result in section 3 differs from the one it names.
  - In each case, report it; do not narrow this prompt's words to pass it. A probe's scratch file and a reversal's temporary edit are allowed, outside the checkout or undone.
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished. A newer push cancels the earlier run's application jobs, and the run of record is lost. Push your records commit only after the run of record has finished. The workflow runs on pushes to `claude/**` and `ccr-**`; if your branch is named otherwise, say so in the report, since no run starts.
  - **If GitHub never starts the run** (it stays `queued` with no jobs for 30 minutes), do not re-run it, dispatch it, push an empty commit, or ask anyone to re-run it (OD-58). Record it, push your records commit, and report.
  - **If the run fails,** stop and report the failing job and its log lines. Do not re-run it.
- **Network:** PyPI only, for `pip install --require-hashes` from the API's existing lock; GitHub, for your pushes and reads. The environment does not enforce this; you do. No database runs: every check here is offline.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, password, marker, token or key;
  - read, print or use the value of any `AWS_*` variable, or name one in a command;
  - call any provider or HDE, connect to any database, HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script;
  - weaken or delete a test to make the suite pass.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:** `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_|RAILWAY_)'` prints names only. If any is present, stop and report.
3. **AWS and GitHub token names may be present** (OD-76); record which, by name only, and never read them.
4. **The toolchain:** CPython 3.12.14 as `python3.12`. Record `python3.12 --version`.
5. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git merge-base --is-ancestor <START_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet f69529c0594889d26caa19eccfe6b7eda73bee56 HEAD -- . ':!*.md' && echo "C1's code head"
git diff --quiet f69529c0594889d26caa19eccfe6b7eda73bee56 origin/claude/magical-wozniak-yfmmx2 -- . ':!*.md' && echo "no code on the live branch after f69529c"
grep -c -E '^#+ Delta review of A1-C1' docs/testing/evidence/2026-11-19-sv4-chat-notifications.md   # must print 1
grep -c -E '^#+ A1-C2' docs/testing/evidence/2026-11-19-sv4-chat-notifications.md                   # must print 0
```

If a check fails, stop and report. The prompt is stale if its commit is not on the live branch, a non-Markdown path changed there after `f69529c`, or a C2 section already exists.

**Then read, completely:** root `AGENTS.md` and `CLAUDE.md`; the record's "A1-C1", "Manager verification of A1-C1" and "Delta review of A1-C1", whole; `services/api/tests/test_match_versions_offline.py`, whole.

## 3. What to do

1. **D1-1, what the detector scans.** The passage says which functions the detector reads: in each module it scans (the API's code, its tests, migrations and virtual environment left out), the top-level `def` functions and the `def` methods of top-level classes, a nested function being read as part of the function that holds it, as `functions()` and `writes()` do. It adds to the forms that escape: a top-level `async def` function, an `async def` method of a top-level class, and any method of a class nested in a top-level class (an `async def` or a class nested inside a scanned function is read with it). No sentence says or implies that every function is scanned.
2. **N1, what `WriterDetectorTests` shows.** The sentence on `WriterDetectorTests` claims only what its cases show. Say which form its cases do not show alone (the save form, whose one example also assigns `version`), and that the save branch is held by `MatchVersionTests`' check that each pinned writer saves both fields. `WriterDetectorTests`' own docstring agrees with the module's.
3. **N2, the escape list's precision.** A match obtained through a helper, and a `save()` override, escape for `version`; an assignment to an object's `contact_version` is found however the object was obtained. Rewrap the passage to the module's line width.
4. **Keep:** the list of forms the detector finds; that the pinned set rests on the A1 review's and the manager's searches, not the detector alone; that the detector's reach is carried (the carried-items file; AR-4); the sentence the passage ends on, which the docstring's next line continues.

**Probes and a reversal,** each on the unchanged detector, from scratch files outside the checkout, with its output recorded:
- (p1) a listed form inside a top-level `async def` function, inside an `async def` method of a top-level class, and inside a `def` method of a class nested in a top-level class: each found nothing; and the same form inside an `async def` nested in a top-level `def`: found;
- (p2) `obj.contact_version = …` where `obj` comes from a helper call, and inside a `save()` override: each found;
- (p3) the save branch of `writes` (line 160) deleted on a copy of the module: `WriterDetectorTests` passes and `MatchVersionTests.test_each_writer_advances_both_by_one_and_saves_both` fails; the copy discarded afterwards.

## 4. Checks, then the report

- **The trusted classifier,** from `main` (`499ccbb`), extracted outside your checkout and run from it with `python3 -I` and full SHAs: `python3 -I <trusted copy>/change_scope.py --base 499ccbbec758ed4ef34a93ad19fa8df454fb095c --head <your code head> --merge-base` prints `"full": true` (reason `behavior-or-empty`).
- **The diff:** `git diff --name-only <START_SHA> <your head>` lists only the one file and the record; `git diff` touches only the two docstrings named above; `ast.dump` of the module with its docstrings removed is unchanged (record the comparison).
- **The API's checks,** in a clean environment, after `pip install --require-hashes -r requirements-dev.lock` in `services/api`: `GLOW_ENV=test python manage.py check`, `GLOW_ENV=test python manage.py test tests` (record the count and skips), `ruff check .`, `ruff format --check .` and `mypy` pass; the module's 5 tests pass.
- **The run of record,** on your last code commit: every job passed, and the gate printed "Application checks passed".

**The record,** section "A1-C2": this prompt's revision and commit; the start gate's and the environment check's results; the passage before and after; the probes and the reversal, with their outputs; the counts and the run of record; every limit and deviation.

Your final message, which Nathan relays:
- your branch and head;
- the record's path;
- the run of record's link and result;
- what you changed, by item;
- every probe's and the reversal's result;
- every stop, limit and deviation, and which GitHub route you used.
