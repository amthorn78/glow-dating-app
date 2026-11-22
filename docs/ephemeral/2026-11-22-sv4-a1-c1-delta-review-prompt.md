# SV4 A1-C1 delta review prompt — the history tests' base, the detector's claim, the read port's rule

- **Owner:** App Manager 13. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 22 November 2026.**
- **Durable brief:** [SV4 — the chat and notifications slice](../planning/sv4-chat-notifications.md), revision 6. **The findings it checks:** AR-1 to AR-3, in the SV4 record's "Exact-head review of A1", and Codex's P1 thread on PR58, the same defect as AR-1.
- **Where the result goes:** the report Nathan relays. The manager records it in the evidence record, "Delta review of A1-C1", with a disposition for each finding, and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 1.84 (confidence 0.84); rung probabilities low 0.00, medium 0.20, high 0.76, extra high 0.04, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.98, Sonnet 5.5 0.02, Haiku 5.5 0.00 (confidence 0.97). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.196, Opus 5.5 at high 0.745, Opus 5.5 at extra high 0.039, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.004, Sonnet 5.5 at high 0.015, Sonnet 5.5 at extra high 0.001, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-22T08:26:03Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action. Dev Manager 7's pre-merge read of A1 (DM-98) follows it.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and none may be present. `amthorn78/glow-docs` is attached, read-only; this review needs nothing from it (OD-74).
- **It runs alone** (OD-29), after PR58's run and Codex's review of the manager-branch head that holds this prompt (the manager workflow, "A small correction gets a delta re-review"). C1 changes tests and docstrings only.
- **Deletion condition:** prune after A1's pull request (PR58) merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch.

---

You are the **delta review of SV4 A1-C1**: a correction of tests and docstrings only, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **A1** (code head `bc0675d`; the record `docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`, section "A1") built the rules chat's routes will serve. PR58 carries it into `main`, which is at `499ccbb` (PR57).
- **A1's exact-head review** (the record's "Exact-head review of A1") found the application's behaviour right on every item and asked for changes:
  - **AR-1, blocking:** two `ReciprocalWriterTests` history tests compared `glow_chat/contact.py` with `main`'s merge base, so once A1 is on `main` they compare A1 with itself and fail, and `main`'s push runs run them. Codex's review of PR58 (head `4618859`) left a P1 thread on the same defect.
  - **AR-2, should fix:** `test_match_versions_offline.py`'s docstrings claimed the version detector misses no writer ("so the pinned set above cannot miss one").
  - **AR-3, should fix:** `glow_domain/chat_reads.py`'s module docstring stated the read rule the brief's D5 replaced.
- **A1-C1** (branch `claude/beautiful-brahmagupta-13ncpo`, code head `f69529c`, records head `7b194aa`; the record's "A1-C1"; run of record 45001765683, success) fixed the three. The manager verified it ("Manager verification of A1-C1") and merged it into the manager branch at `9947844`.

**The code head under review is `f69529c0594889d26caa19eccfe6b7eda73bee56`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to it (the start gate checks this).

**Your scope:**
- **The correction:** `git diff 656ce032803b42da7a771185ce0016b5364f433f f69529c0594889d26caa19eccfe6b7eda73bee56`, three paths:
  - `services/api/tests/test_interactions_offline.py`: `A1_BASE`, the comment above `MAIN_DEFINITION_DIGESTS`, and `ReciprocalWriterTests` whole;
  - `services/api/tests/test_match_versions_offline.py`, whole;
  - `services/api/glow_domain/chat_reads.py`'s module docstring.
- **Against:** `services/api/glow_chat/contact.py` at the head and at `499ccbb`; `services/api/glow_chat/reads.py` at the head (its module docstring, `PAUSED_STATES`, `READABLE_OTHER_STATES`, `readable`, `_history`, `_causes` and the authorization step); the detector (`writes` and its helpers) in `test_match_versions_offline.py`; the Foundation workflow's API checks job and how `main`'s push runs check out.
- **The Markdown, as claims about the code:** the record's sections "A1-C1" and "Manager verification of A1-C1".
- **The runs:** 45001765683 (the run of record) and PR58's run on `<PROMPT_SHA>` (event `pull_request`), once it has finished; Codex's review of that head and its threads on PR58.
- **Out of scope:** everything A1's exact-head review covered and C1 does not change, and what the record already carries (AR-4 to AR-16, and C1's left wording in "Manager verification of A1-C1").

**The focus:**
1. **AR-1 answered.** With A1 on `main`, the history tests pass: simulate the merge (a local `main` at `499ccbb` with the head merged into it) and run the class there. They pass before the merge, and skip with their reason in a `--depth 1` clone. They no longer depend on `main` or `origin/main` at all. Every assertion each made at `656ce03` stays, against `A1_BASE`. Say how you checked.
2. **The history tests still catch what they are for:** a change to any definition A1 leaves alone, a change to `block` beyond D3's statement and D4's value, and `grant_token`'s return. Show at least the reversals r1 and r2 failing, and add any you doubt.
3. **AR-2 answered.** The two docstrings claim only what the detector finds, name the forms that escape it, and say the pinned set rests on the searches, with AR-4 carried. No sentence claims the detector is complete. With docstrings removed, the module's code is unchanged.
4. **AR-3 answered.** `chat_reads.py`'s paragraph states the rule `glow_chat/reads.py` applies, condition by condition: nothing it leaves out, nothing it adds, no grant named, no open history question, and no claim about the served codes beyond naming `error_for`. With docstrings removed, the module's code is unchanged.
5. **Nothing weakened, nothing outside:** no other test or path changes; no assertion is removed or loosened.
6. **The records:** every claim in "A1-C1" and "Manager verification of A1-C1" holds against the code and the runs.

**Re-run, at least,** in a scratch clone of the head with the API's hash-locked environment (`pip install --require-hashes -r services/api/requirements-dev.lock`), in a clean environment with `GLOW_ENV=test`: `python manage.py test tests` in `services/api` (expected `Ran 654 tests … OK`, with or without the two history tests' skips, by whether `499ccbb` is in the clone), `ruff check .`, `ruff format --check .` and `mypy`; then focus items 1 and 2's runs.

**What comes after this review: the correction classes** (D-07). Report every finding with its severity. A further correction takes only a blocking finding, or a should-fix finding that:
- lets a history test pass where it should fail, or fail on `main` after the merge;
- removes or loosens an earlier assertion;
- leaves a docstring claiming more than the code does, at the detector or the who-may-read boundary;
- changes a path outside the three passages;
- makes a record claim more than the code, the tests or the runs show.

Everything else goes into the records.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 13. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs.
- **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, thread resolutions, re-runs or workflow dispatches. Read GitHub with the GitHub tools where your session has them, otherwise with `gh api` REST `GET` calls, and say which you used. Scratch work goes in a copy outside the repository; confirm afterwards that `git status` is clean.
- **Network:** PyPI, for the hash-locked install in a scratch copy; GitHub, read only, to read the runs and the pull request.
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
git diff --quiet f69529c0594889d26caa19eccfe6b7eda73bee56 HEAD -- . ':!*.md' && echo "the code head under review"
git diff --quiet f69529c0594889d26caa19eccfe6b7eda73bee56 origin/claude/magical-wozniak-yfmmx2 -- . ':!*.md' && echo "no code on the live branch after f69529c"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-19-sv4-chat-notifications.md | grep -c -E '^#+ Delta review of A1-C1'   # must print 0
```

If any check fails, stop and report. Then **classify the change** with `main`'s `scripts/change_scope.py`, extracted outside the tree and run, with the checkout as its working directory, as `python3 -I <copy> --base $(git rev-parse origin/main) --head $(git rev-parse HEAD) --merge-base`; expected `"full": true`.

**Then read, completely, at `HEAD`:** root `AGENTS.md` and `CLAUDE.md`; the record's "Exact-head review of A1", "A1-C1" and "Manager verification of A1-C1"; the brief's D5 and D6; the passages in your scope, whole.

## 3. Report

Your final message, which Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- the focus, item by item, with your verdict on each;
- every finding, with its severity (blocking, should fix, nit), file and line, evidence, and whether it falls in a correction class above;
- the checks, proofs and reversals you ran, each with its exact result;
- PR58's run on `<PROMPT_SHA>` and Codex's review of it, as you read them, and which GitHub route you used;
- your verdict: **approve**, **approve with nits** or **changes requested**;
- what you did not read or run, and why.
