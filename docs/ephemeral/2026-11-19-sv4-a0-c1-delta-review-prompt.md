# SV4 A0-C1 delta review prompt — the tests that pin the decoy, `dbshell` and gate checks

- **Owner:** App Manager 12. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 19 November 2026.**
- **Durable brief:** [SV4 — the chat and notifications slice](../planning/sv4-chat-notifications.md), revision 3. **The findings it answers:** the A0 record's "Exact-head review of A0" and its disposition table.
- **Where the result goes:** the report Nathan relays. The manager records it in the evidence record, "Delta review of A0-C1", with a disposition for each finding, and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 1.93 (confidence 0.89); rung probabilities low 0.00, medium 0.11, high 0.84, extra high 0.05, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 1.00, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 1.00). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.110, Opus 5.5 at high 0.840, Opus 5.5 at extra high 0.050, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-19T16:37:51Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action. Dev Manager 6's pre-merge read of A0 follows it.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of PR57's head that holds this prompt (the manager workflow, "A small correction gets a delta re-review"). C1 changes no non-test line.
- **Deletion condition:** prune after A0's pull request (PR57) merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **delta review of SV4 A0-C1**: a correction of tests only, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **A0** (code head `3bf55de`) split the Foundation workflow's database job into four per-suite jobs, each identity, profile and discovery job with a decoy database whose marker its suite refuses (DM-96's AG1) and its own `dbshell` refusal.
- **A0's exact-head review** (the record `docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`, "Exact-head review of A0") found the workflow right and asked for tests: F1, the decoy's binding to the marker it refuses; F2, the identity job's new steps and each job's `dbshell`, existence and password-mask checks. The manager added F7's D6a, the gate's loop, under D-07, and F6's test-module docstrings.
- **A0-C1** (branch `claude/awesome-brown-lmfi8e`, code head `c78f297`, records head `b407239`; the record's "A0-C1"; run of record 44562701307, success) added the tests, in three files only. The manager verified it ("Manager verification of A0-C1", which notes two points for you) and fast-forwarded the manager branch to it.

**The code head under review is `c78f29747b1fe6e764dd3cb1afe5e6325941a6d2`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to it (the start gate checks this).

**Your scope:**
- **The correction:** `git diff 3bf55de775de1f7aa8cace3f7bc780c97f0b2e98 c78f29747b1fe6e764dd3cb1afe5e6325941a6d2`, three paths, each read **whole** at the head, not the diff alone: `proofs/postgres-ordering/tests/test_identity_offline.py`, `test_profile_offline.py` and `test_discovery_offline.py`.
- **Against:** the workflow `.github/workflows/foundation.yml` at the head (equal to `3bf55de`'s): the four database jobs and the gate.
- **The Markdown, as claims about the code:** the record's sections "A0-C1" and "Manager verification of A0-C1".
- **The runs:** 44562701307 (the run of record) and the PR run on PR57's head (event `pull_request`), once it has finished.
- **Out of scope:** the workflow and everything A0's exact-head review already covered, except where C1's tests read it.

**The focus:**
1. **Each finding answered.** F1: in each of the three jobs, the decoy's comment, its marker file and the refused `migrate` are bound to the same value, and no test passes when any one is rebound. F2: the identity job's credentials and decoy-step contents, and in each job the `dbshell` step's two checks, the decoy's existence check and both password masks. D6a: the gate's loop covers the whole tuple. F6: the docstrings only.
2. **Nothing weakened:** no earlier assertion changed or removed; the only removed lines are the three docstring lines.
3. **The tests prove what they say.** `script_lines`, `writers` and `credentials_prelude` match whole lines and stop where they should; a test cannot pass vacuously (an empty sequence, a helper that returns nothing, a substring found in a comment). Name any edit that defeats a check while every pinned line stays (the record's "Substring pins, not semantics" limit) and say whether it matters.
4. **The gate test's script run.** It cuts the gate's Python script from the workflow and runs it with `sys.executable -I -c` and an environment of `PATH` and `RESULTS` only. Say whether that is safe to run in a developer's checkout and in CI, and whether it proves the gate's rule.
5. **The helpers' place:** module-level functions in `test_identity_offline.py`, imported by the other two files. Say whether that stays within "tests of the workflow's steps".
6. **The records:** every claim in "A0-C1" and "Manager verification of A0-C1" holds against the code and the runs.

**Re-run, at least,** in a scratch copy of the head:
- the proof's offline tests, Ruff and the configured `mypy`, in a clean environment (expected: `Ran 383 tests … OK`);
- **reversals, offline, on copies of the workflow**, each failing a test: in each of the identity, profile and discovery jobs, F1's three (the decoy's comment rebound; its marker file written from another variable; the refused `migrate` given another file), D2a (`test "$fail" = 0` removed), D3a and D3b (the `dbshell` step's two checks removed), D4b (a password mask removed) and D6b (the existence check removed); and D6a (the gate's loop over `jobs[:5]`). Add any you doubt.

**What comes after this review: the correction classes.** Report every finding with its severity. A further correction takes only a blocking finding, or a should-fix finding that could:
- let a test pass where it should fail, for a check A0's acceptance rests on (the decoy, `dbshell`, the masks, the gate);
- weaken or remove an earlier assertion;
- change a path outside the three test files;
- make a record claim more than the code, the tests or the runs show.

Everything else goes into the records.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 12. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches. Read GitHub only through your GitHub tools; use `gh` for nothing but a search. Scratch work goes in a copy outside the repository; confirm afterwards that `git status` is clean.
- **Network:** PyPI only, for the hash-locked install in a scratch copy; GitHub through your tools, to read runs.
- **Never:**
  - dump the environment, or print a credential, password, marker, token or key;
  - read, print or use the value of any `AWS_*` variable;
  - call any provider or HDE, or connect to any database, HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:** `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_|RAILWAY_)'` prints names only. If any is present, stop and report.
3. **AWS and GitHub token names may be present;** record which, by name only, and never read them.
4. **The toolchain:** CPython 3.12.14 as `python3.12`.
5. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, c2cffbe6022637331d73e3558429ff70ab5aa5e3
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet c78f29747b1fe6e764dd3cb1afe5e6325941a6d2 HEAD -- . ':!*.md' && echo "the code head under review"
git diff --quiet c78f29747b1fe6e764dd3cb1afe5e6325941a6d2 origin/claude/magical-wozniak-yfmmx2 -- . ':!*.md' && echo "no code on the live branch after c78f297"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-19-sv4-chat-notifications.md | grep -c -E '^#+ Delta review of A0-C1'   # must print 0
```

If any check fails, stop and report. Then **classify the change** with `main`'s `scripts/change_scope.py`, extracted outside the tree and run as `python3 -I <copy> --base $(git rev-parse origin/main) --head $(git rev-parse HEAD) --merge-base`; expected `"full": true`.

**Then read, completely, at `HEAD`:** root `AGENTS.md` and `CLAUDE.md`; the record's "Exact-head review of A0", "A0-C1" and "Manager verification of A0-C1"; the three test files, whole; the workflow's four database jobs and its gate.

## 3. Report

Your final message, which Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- the focus, item by item, with your verdict on each;
- every finding, with its severity (blocking, should fix, nit), file and line, evidence, and whether it falls in a correction class above;
- the checks and reversals you re-ran, each with its exact result;
- your verdict: **approve**, **approve with nits** or **changes requested**;
- what you did not read or run, and why.
