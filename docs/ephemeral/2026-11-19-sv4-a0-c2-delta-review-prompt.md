# SV4 A0-C2 delta review prompt — the profile and discovery decoy-step tests

- **Owner:** App Manager 12. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 19 November 2026.**
- **Durable brief:** [SV4 — the chat and notifications slice](../planning/sv4-chat-notifications.md), revision 3. **The finding it answers:** R1, in the A0 record's "Delta review of A0-C1".
- **Where the result goes:** the report Nathan relays. The manager records it in the evidence record, "Delta review of A0-C2", with a disposition for each finding, and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 1.78 (confidence 0.83); rung probabilities low 0.00, medium 0.24, high 0.74, extra high 0.02, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.99, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.99). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.238, Opus 5.5 at high 0.733, Opus 5.5 at extra high 0.020, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.002, Sonnet 5.5 at high 0.007, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-19T19:58:27Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action. Dev Manager 6's pre-merge read of A0 follows it.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of PR57's head that holds this prompt (the manager workflow, "A small correction gets a delta re-review"). C2 changes no non-test line.
- **Deletion condition:** prune after A0's pull request (PR57) merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **delta review of SV4 A0-C2**: a correction of tests only, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **A0** (code head `3bf55de`) split the Foundation workflow's database job into four per-suite jobs, each identity, profile and discovery job with a decoy step that shows its suite's database refusing a decoy database's marker, unchanged.
- **A0-C1** (code head `c78f297`) added offline tests pinning each job's decoy, `dbshell` and gate checks. **Its delta review** (the record `docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`, "Delta review of A0-C1") found R1: the profile and discovery decoy-step tests left out lines the identity test's sequence pins, so the outside-relations check and the refusal check could be removed in those jobs with every test passing.
- **A0-C2** (branch `claude/dazzling-feynman-cjl16t`, code head `5a2f137`, records head `a63e7ae`; the record's "A0-C2"; run of record 44601565801, success) added eight lines to each of the two sequences, so each matches the identity test's line for line. The manager verified it ("Manager verification of A0-C2") and fast-forwarded the manager branch to it.

**The code head under review is `5a2f137b464565f5da8ed52ce0bb53938b7587a1`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to it (the start gate checks this).

**Your scope:**
- **The correction:** `git diff c78f29747b1fe6e764dd3cb1afe5e6325941a6d2 5a2f137b464565f5da8ed52ce0bb53938b7587a1`, two paths: `ProfileWorkflowTests.test_the_migrations_step_refuses_the_decoys_marker_first` in `proofs/postgres-ordering/tests/test_profile_offline.py` and `DiscoveryWorkflowTests.test_the_migrations_step_refuses_the_decoys_marker_first` in `test_discovery_offline.py`, each read **whole** at the head, beside `IdentityWorkflowTests.test_the_migrations_step_refuses_the_decoys_marker_first`.
- **Against:** the workflow's profile and discovery decoy steps at the head (equal to `3bf55de`'s).
- **The Markdown, as claims about the code:** the record's sections "A0-C2" and "Manager verification of A0-C2".
- **The runs:** 44601565801 (the run of record) and the PR run on PR57's head (event `pull_request`), once it has finished.
- **Out of scope:** everything the earlier reviews covered and C2 does not change, and the limits already carried to A2 (the record's dispositions of N1 and N2).

**The focus:**
1. **R1 answered:** in each of the two jobs, removing the outside-relations check, the refusal check, either `outside_*` assignment or the `no_ledger` query fails a test.
2. **The sequences equal the identity sequence** with the suite's names, line for line and in order; say how you checked.
3. **Nothing weakened:** no line removed, no earlier assertion changed; only the two tests change.
4. **The records:** every claim in "A0-C2" and "Manager verification of A0-C2" holds against the code and the runs.

**Re-run, at least,** in a scratch copy of the head: the proof's offline tests, Ruff and the configured `mypy`, in a clean environment (expected: `Ran 383 tests … OK`); and, in each of the profile and discovery jobs, on copies of the workflow, the reversals X1 (the outside-relations failure removed), X2 (`if [ -n "$refusal" ]; then` made `if true; then`), X10 (the `outside_before=` line removed), X11 (the `outside_after=` line removed) and X12 (the `no_ledger=` line made `no_ledger=t`), each failing a test. Add any you doubt.

**What comes after this review: the correction classes.** Report every finding with its severity. A further correction takes only a blocking finding, or a should-fix finding that could:
- let a test pass where it should fail, for a check A0's acceptance rests on (the decoy, `dbshell`, the masks, the gate);
- weaken or remove an earlier assertion;
- change a path outside the two tests;
- make a record claim more than the code, the tests or the runs show.

Everything else goes into the records.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 12. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs.
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
git diff --quiet 5a2f137b464565f5da8ed52ce0bb53938b7587a1 HEAD -- . ':!*.md' && echo "the code head under review"
git diff --quiet 5a2f137b464565f5da8ed52ce0bb53938b7587a1 origin/claude/magical-wozniak-yfmmx2 -- . ':!*.md' && echo "no code on the live branch after 5a2f137"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-19-sv4-chat-notifications.md | grep -c -E '^#+ Delta review of A0-C2'   # must print 0
```

If any check fails, stop and report. Then **classify the change** with `main`'s `scripts/change_scope.py`, extracted outside the tree and run, with the checkout as its working directory, as `python3 -I <copy> --base $(git rev-parse origin/main) --head $(git rev-parse HEAD) --merge-base`; expected `"full": true`.

**Then read, completely, at `HEAD`:** root `AGENTS.md` and `CLAUDE.md`; the record's "Delta review of A0-C1", "A0-C2" and "Manager verification of A0-C2"; the three tests named above, whole; the workflow's profile and discovery decoy steps.

## 3. Report

Your final message, which Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- the focus, item by item, with your verdict on each;
- every finding, with its severity (blocking, should fix, nit), file and line, evidence, and whether it falls in a correction class above;
- the checks and reversals you re-ran, each with its exact result;
- your verdict: **approve**, **approve with nits** or **changes requested**;
- what you did not read or run, and why.
