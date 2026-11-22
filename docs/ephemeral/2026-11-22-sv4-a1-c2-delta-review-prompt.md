# SV4 A1-C2 delta review prompt — the version detector's docstring

- **Owner:** App Manager 13. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 22 November 2026.**
- **Durable brief:** [SV4 — the chat and notifications slice](../planning/sv4-chat-notifications.md), revision 7. **The findings it checks:** D1-1, N1 and N2, in the SV4 record's "Delta review of A1-C1".
- **Where the result goes:** the report Nathan relays. The manager records it in the evidence record, "Delta review of A1-C2", with a disposition for each finding, and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 1.62 (confidence 0.73); rung probabilities low 0.00, medium 0.39, high 0.60, extra high 0.01, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.98, Sonnet 5.5 0.02, Haiku 5.5 0.00 (confidence 0.97). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.382, Opus 5.5 at high 0.588, Opus 5.5 at extra high 0.010, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.008, Sonnet 5.5 at high 0.012, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-22T09:25:29Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action. Dev Manager 7's pre-merge read of A1 (DM-98) follows it.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and none may be present. `amthorn78/glow-docs` is attached, read-only; this review needs nothing from it (OD-74).
- **It runs alone** (OD-29), after PR58's run and Codex's review of the manager-branch head that holds this prompt. C2 changes docstrings only.
- **Deletion condition:** prune after A1's pull request (PR58) merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch.

---

You are the **delta review of SV4 A1-C2**: a correction of docstrings only, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **A1** (code head `bc0675d`) built the rules chat's routes will serve; PR58 carries it into `main` (`499ccbb`). Its D6 test, `services/api/tests/test_match_versions_offline.py`, pins every writer of a match's `version` and `contact_version`, with a static detector (`functions()`, `writes()` and their helpers) and `WriterDetectorTests`.
- **A1-C1** (code head `f69529c`) fixed A1's exact-head review's AR-1 to AR-3. **Its delta review** (the record `docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`, "Delta review of A1-C1") asked for one more change: **D1-1**, the module docstring said the detector "scans every function in the API's code", but `functions()` reads only top-level `def` functions and the `def` methods of top-level classes; with **N1** ("`WriterDetectorTests` shows each of these forms is found", which its save case does not show alone) and **N2** (a helper's match and a `save()` override escape only for `version`; a ragged wrap).
- **A1-C2** (branch `claude/affectionate-pasteur-ge2jra`, code head `934da48`, records head `02ebfc7`; the record's "A1-C2"; run of record 45006396587, success) rewrote the passage and `WriterDetectorTests`' docstring. The manager verified it ("Manager verification of A1-C2") and merged it into the manager branch at `860abe2`.

**The code head under review is `934da48e74150934b364421a3570f61b6f568f72`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to it (the start gate checks this).

**Your scope:**
- **The correction:** `git diff 63aebb6f21dd9a19d8b9fc8f376e6673f8780c0d 934da48e74150934b364421a3570f61b6f568f72`, one path: `services/api/tests/test_match_versions_offline.py`, its module docstring and `WriterDetectorTests`' docstring.
- **Against:** the same module's code at the head: `sources()`, `functions()`, `match_names()`, `writes()` and their helpers, `MatchVersionTests` and `WriterDetectorTests`.
- **The Markdown, as claims about the code:** the record's sections "A1-C2" and "Manager verification of A1-C2".
- **The runs:** 45006396587 (the run of record) and PR58's run on `<PROMPT_SHA>` (event `pull_request`), once it has finished; Codex's review of that head and its threads on PR58.
- **Out of scope:** everything the earlier reviews of A1 and C1 covered and C2 does not change, and what the record carries (AR-4 to AR-16; C1's delta review's N3 to N5).

**The focus:**
1. **D1-1 answered:** the passage says which functions the detector reads, exactly as `functions()` and `writes()` do; it names what is never read; no sentence says or implies that every function is scanned.
2. **N1 answered:** each sentence on what `WriterDetectorTests` and `MatchVersionTests` show is true, by reversal (at least: the save branch of `writes` deleted, `WriterDetectorTests` passes and `MatchVersionTests.test_each_writer_advances_both_by_one_and_saves_both` fails).
3. **N2 answered:** every form the passage lists as escaping escapes, and every form it lists as found is found, including the `contact_version` clause and the signal C2 added (its deviation). Probe each with the unchanged detector.
4. **Nothing else:** with docstrings removed the module's code is unchanged; no other path changes; the module's 5 tests and the API's suite pass.
5. **The records:** every claim in "A1-C2" and "Manager verification of A1-C2" holds against the code and the runs.

**Re-run, at least,** in a scratch clone of the head with the API's hash-locked environment (`pip install --require-hashes -r services/api/requirements-dev.lock`), in a clean environment with `GLOW_ENV=test`: `python manage.py test tests` in `services/api` (expected `Ran 654 tests … OK`, with or without the two history tests' skips), `ruff check .`, `ruff format --check .` and `mypy`; then focus items 2 and 3's probes and reversal.

**What comes after this review: the correction classes** (D-07). Report every finding with its severity. A further correction takes only a blocking finding, or a should-fix finding that:
- leaves a docstring claiming more than the code does, at the detector boundary;
- changes code, a test or a path outside the two docstrings;
- makes a record claim more than the code, the tests or the runs show.

Everything else goes into the records.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 13. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs.
- **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, thread resolutions, re-runs or workflow dispatches. Read GitHub with the GitHub tools where your session has them, otherwise with `gh api` REST `GET` calls, and say which you used. Scratch work goes in a copy outside the repository; confirm afterwards that `git status` is clean.
- **Network:** PyPI, for the hash-locked install in a scratch copy; GitHub, read only. The environment does not enforce this; you do.
- **Never:**
  - dump the environment, or print a credential, password, marker, token or key;
  - read, print or use the value of any `AWS_*` variable, or name one in a command;
  - call any provider or HDE, or connect to any database, HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:** `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_|RAILWAY_)'` prints names only. If any is present, stop and report.
3. **AWS and GitHub token names may be present** (OD-76); record which, by name only, and never read them.
4. **The toolchain:** CPython 3.12.14 as `python3.12`.
5. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, 499ccbbec758ed4ef34a93ad19fa8df454fb095c
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 934da48e74150934b364421a3570f61b6f568f72 HEAD -- . ':!*.md' && echo "the code head under review"
git diff --quiet 934da48e74150934b364421a3570f61b6f568f72 origin/claude/magical-wozniak-yfmmx2 -- . ':!*.md' && echo "no code on the live branch after 934da48"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-19-sv4-chat-notifications.md | grep -c -E '^#+ Delta review of A1-C2'   # must print 0
```

If any check fails, stop and report. Then **classify the change** with `main`'s `scripts/change_scope.py`, extracted outside the tree and run, with the checkout as its working directory, as `python3 -I <copy> --base $(git rev-parse origin/main) --head $(git rev-parse HEAD) --merge-base`; expected `"full": true`.

**Then read, completely, at `HEAD`:** root `AGENTS.md` and `CLAUDE.md`; the record's "Delta review of A1-C1", "A1-C2" and "Manager verification of A1-C2"; `services/api/tests/test_match_versions_offline.py`, whole.

## 3. Report

Your final message, which Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- the focus, item by item, with your verdict on each;
- every finding, with its severity (blocking, should fix, nit), file and line, evidence, and whether it falls in a correction class above;
- the checks, probes and reversals you ran, each with its exact result;
- PR58's run on `<PROMPT_SHA>` and Codex's review of it, as you read them, and which GitHub route you used;
- your verdict: **approve**, **approve with nits** or **changes requested**;
- what you did not read or run, and why.
