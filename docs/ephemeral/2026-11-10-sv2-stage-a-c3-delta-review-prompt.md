# SV2 Stage A delta review prompt — correction C3's tests

- **Owner:** App Manager 10. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 10 November 2026.**
- **Durable brief:** [SV2 — The profiles and media slice](../planning/sv2-profiles-media.md), revision 5, "Stage A, correction C3".
- **Where the result goes:** the report Nathan relays. The manager records it in the evidence record, "Delta review of correction C3", with a disposition for each finding, and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.36 (confidence 0.73); rung probabilities low 0.00, medium 0.02, high 0.62, extra high 0.34, max 0.02, ultracode 0.00. Model probabilities Fable 5.1 0.03, Opus 5.5 0.97, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.96). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.001, Fable 5.1 at high 0.019, Fable 5.1 at extra high 0.010, Fable 5.1 at max 0.001, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.019, Opus 5.5 at high 0.601, Opus 5.5 at extra high 0.330, Opus 5.5 at max 0.019, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-10T22:15:29Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of PR43's head and of this prompt's commit (step 6). It is a delta review (M05 S2): C3 changes no non-test line.
- **Deletion condition:** prune after SV2 Stage A's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **delta review of correction C3 of SV2's Stage A**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **Stage A,** with corrections C1 and C2, built the server's profile in `services/api/glow_profiles`, sealed. A full exact-head review read C2's code head `01a3acb` and found no defect in the code ("Exact-head review of Stage A after C2" in `docs/testing/evidence/2026-11-10-sv2-profiles-media.md`).
- **That review's one should-fix finding:** the static guards that keep values out of logs and refusal reasons, and keep a profile's state in the shared recompute, matched names, so plausible edits passed every test. It also found nits.
- **Correction C3** (branch `claude/stoic-faraday-gist9o`, code head `fee4fdc`, records `414d4a7`; the record, "Correction C3") changed tests and the record only:
  - name-independent guards, with an allowlist of five state writes to other models;
  - the guards' limits recorded;
  - a test class moved before `unittest.main()`;
  - two check labels and one comment in the profile suite;
  - Stage A's lock-order sentence corrected.

  It ran twelve reversals, each failing its new check. Run of record: push run 42908603138, all eight jobs passed, the profile suite 53/53. The manager verified and integrated it at `bfc633b` (the record, "Manager verification of correction C3").

**The code head under review is `fee4fdc`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `fee4fdc` (the start gate checks this).

**Your scope** (a delta review: every path C3 touches, read whole as it stands at `fee4fdc`, with the full review's security focus):
- `services/api/tests/test_profiles_offline.py` and `services/api/tests/test_profile_recompute.py`;
- `proofs/postgres-ordering/glow_ordering_proof/profile_cases.py` (C3's lines, and every check label in the file) and `proofs/postgres-ordering/tests/test_profile_offline.py`;
- the record's "Correction C3", and "Manager verification of correction C3";
- read only, as the guards read them: `glow_profiles/views.py`, `operations.py`, `staff.py`, `recompute.py`, `identity_verification.py`, `settings_store.py`, and `glow_identity/age.py`;
- the runs: 42908603138, and the PR run on PR43's head (event `pull_request`), once it has finished.

**Out of scope:** the application code itself, which the full review read at `01a3acb` and C3 did not change. A finding there is reported as pre-existing.

**The focus:**
1. **Finding 1 closed, (a) to (c):** the guards fail each plausible edit the full review named:
   - a refusal reason or a port message built from a value (`AgeTransitionRefused`, `PortOutcome`);
   - a second or borrowed logger, any logging receiver, and writes to `sys.stdout`, `sys.stderr` or a file;
   - a profile's state written by any spelling (`.state =`, `setattr`, `bulk_update`, `update` with `state`, `defaults` or `**`), in `glow_profiles` or `age.py`.

   Try edits of your own beyond C3's twelve. Name any plausible edit that still passes.
2. **The allowlist:**
   - each of its five entries is a write to a model that is not a profile, at the named file, line and function;
   - the model check on each entry cannot be satisfied by a profile write;
   - pinning line numbers is a tripwire, not a gap. A moved line fails the guard; it never silently passes.
3. **The guards on the code as it stands:** they pass at `fee4fdc` with no change to application code, and no check was relaxed to make them pass.
4. **The guards' limits** (finding 1, (d) and (e)) are recorded truthfully, each with the case or test that covers the behaviour:
   - a member view reaching staff code through a helper;
   - an inner function not named `body`;
   - a recompute inside a condition;
   - a lazy import in `glow_domain`.
5. **The nits:**
   - `BodiesTheParserCannotHoldTests` runs when the file runs as a script;
   - no check label in `profile_cases.py` holds a member value, and the new offline test enforces it;
   - the scan comment is true.
6. **The record's lock-order sentence** (C3 item 6), and the session's deviation 2. Is the no-deadlock reason right under PostgreSQL 17's row locking, for every writer's pointer order in `glow_profiles`?
   - Look for a cycle of member writers and publications. Can a `FOR SHARE` request wait behind a waiting `FOR UPDATE` while its own transaction holds a pointer another waiter needs?
   - If the reason holds, say why.
   - If it cannot be shown from the code and PostgreSQL's documented behaviour, say what the record may truthfully claim. PostgreSQL's deadlock detection, which aborts one transaction, bounds the worst case.
7. **No test weakened or vacuous:**
   - C3 removed or loosened no assertion;
   - each new check fails for the edit it names (re-run at least three reversals yourself).
8. **Scope:** `git diff --name-only 01a3acb3d725e05d6e2d6a2d78f5e102db9e9f5a fee4fdc5c71c54b95faa9bbb1256edee74546de3 -- . ':!*.md'` lists only test paths. No application code, model, migration, DTO, registry entry, workflow, lock or dependency changed.

**Re-run, at least,** in a scratch copy of `fee4fdc`:
- **The API's checks:** `manage.py check`, `manage.py test tests`, `ruff` and the configured `mypy`. The contract tests. The proof's offline tests, `ruff` and `mypy`.
- **At least three reversals of your own** against the new guards, each appended so that no allowlisted line moves. Also at least one that moves an allowlisted line, to show the tripwire.
- **The profile suite, informational,** on a throwaway PostgreSQL under P06.DB's D4, if Docker allows.

**The correction classes** (the full review's): a correction pass takes every blocking finding, and any should-fix finding that could:
- let a test pass where it should fail, or fail where the code is right;
- make a record claim more than the code, the tests or the runs show;
- let a value reach a log, an error or a refusal reason unguarded;
- let a profile's state be written outside the recompute unguarded.

Everything else goes into the records. For each finding, say whether it falls in a class.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 10. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs.
- **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches. Scratch work goes in a copy outside the repository, with absolute paths, and `git status` stays clean.
- **Network:**
  - PyPI and the npm registry, for hash-locked installs in a scratch copy;
  - Docker Hub, only to pull the PostgreSQL image the CI job pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`);
  - GitHub, through your tools, to read runs.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions):
  - a throwaway PostgreSQL in Docker, from that image, on loopback only;
  - a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present;
  - removed afterwards.
- **Never:**
  - dump the environment, or print a credential, password, token, session key or key;
  - call any provider or HDE, send any email, or run any command in `proofs/stream-chat/`;
  - connect to any database but a throwaway one you started under D4's conditions, HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:** `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` or `PG*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG)'` prints names only. If any is present, stop and report.
3. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them.
4. **The toolchain:** CPython 3.12.14 as `python3.12`; Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`; Docker if present. Record their versions.
5. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, df8a04c5118d41016c14001308f796fd47626916
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet fee4fdc5c71c54b95faa9bbb1256edee74546de3 HEAD -- .github scripts services apps packages proofs ':!*.md' && echo "the code head under review"
git diff --quiet fee4fdc5c71c54b95faa9bbb1256edee74546de3 origin/claude/magical-wozniak-yfmmx2 -- .github scripts services apps packages proofs ':!*.md' && echo "no code on the live branch after fee4fdc"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-10-sv2-profiles-media.md | grep -c -E '^#+ Delta review of correction C3'   # must print 0
```

If any check fails, stop and report. The prompt is stale if any of these holds:
- its commit is not on the live branch;
- a non-Markdown path changed there after `fee4fdc`;
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
- root `AGENTS.md` and `CLAUDE.md`;
- the brief, revision 5: "Stage A, correction C3";
- the record: "Exact-head review of Stage A after C2", "Correction C3" and "Manager verification of correction C3";
- every path in your scope.

## 3. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- **the verdict:** approve, approve with nits, or changes required;
- the findings, in a table: number, severity, correction class or not, file and line, what is wrong, and the evidence;
- the answer to each focus point (1 to 8), one or two lines each, with focus 6's reasoning in full;
- the reversals you ran, with their results, the local database ones named informational;
- the runs you read, with each job's result and the profile lines;
- what you ran, and what you could not run or read.
