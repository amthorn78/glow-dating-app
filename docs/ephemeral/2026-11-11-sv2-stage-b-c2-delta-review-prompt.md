# SV2 Stage B delta review prompt — correction C2's tests

- **Owner:** App Manager 10. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 11 November 2026.**
- **Durable brief:** [SV2 — The profiles and media slice](../planning/sv2-profiles-media.md), revision 8, "Stage B, correction C2 (the exact-head review)".
- **Where the result goes:** the report Nathan relays. The manager records it in the evidence record, "Delta review of Stage B's correction C2", with a disposition for each finding, and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.27 (confidence 0.79); rung probabilities low 0.00, medium 0.03, high 0.69, extra high 0.27, max 0.01, ultracode 0.00. Model probabilities Fable 5.1 0.01, Opus 5.5 0.99, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.99). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.007, Fable 5.1 at extra high 0.003, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.030, Opus 5.5 at high 0.683, Opus 5.5 at extra high 0.267, Opus 5.5 at max 0.010, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-11T12:35:23Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of PR44's head, which holds this prompt (step 6). It is a delta review (M05 S2): C2 changes no non-test line.
- **Deletion condition:** prune after Stage B's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **delta review of correction C2 of SV2's Stage B**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **Stage B,** with correction C1, built photos in `services/api/glow_profiles` (`media.py`), sealed, behind fixture ports. A full exact-head review read C1's code head `7538c76`, with a written threat model (T1 to T21), and found no defect in the code ("Exact-head review of Stage B after C1" in `docs/testing/evidence/2026-11-10-sv2-profiles-media.md`).
- **That review's should-fix findings** were gaps in the tests and records, F1 to F5:
  - F1: nothing showed a hold stopping the check's approval (T9);
  - F2: the lock-site guard missed a pointer locked through a variable or raw SQL (T14);
  - F3: the state-write guard missed a `MediaAsset` created with a state (T7);
  - F4: the scans' ledger held less than the records claimed (T8, T16, T19);
  - F5: migration 0008's constraints had no malformed-write case (T21).

  It also found nits; N2, N5, N6, N7 and N9 are records C2 corrects.
- **Correction C2** (branch `claude/eloquent-dijkstra-dmah71`, code head `5bcbe54`, records `9740196`; the record, "Stage B, correction C2") changed tests and records only:
  - two profile-suite cases, `media.a_hold_stops_the_checks_approval` and `constraints.malformed_media_writes_are_refused`, with `CASE_COUNT` 69;
  - an offline order check of the hold's branch, a guard on every mention of `PolicyRevision`, and a guard on every creation that sets a state;
  - a wider value ledger (`ValueLedger.add_bytes`, `ObservedObjects`, `watch_store`, `hold_media`);
  - the records' corrections.

  It ran reversals R1 to R5, each failing its new check. Run of record: push run 42990527042, all eight jobs passed, the profile suite 69/69 with both scans clean. The manager verified and integrated it at `9740196`, with three reversals of its own, M7 to M9 (the record, "Manager verification of Stage B's correction C2").

**The code head under review is `5bcbe54`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `5bcbe54` (the start gate checks this).

**Your scope** (a delta review: every path C2 touches, read whole as it stands at `5bcbe54`, with the exact-head review's security focus):
- `services/api/tests/test_profile_media.py`, `test_profile_pointer_order.py` and `test_profile_recompute.py`;
- `proofs/postgres-ordering/glow_ordering_proof/profile_cases.py` (C2's lines: the two cases, `MEDIA_CATALOG`, `SHADOWED` and `run_case`), `profile_support.py` (C2's lines) and `proofs/postgres-ordering/tests/test_profile_offline.py`;
- the records commit's four paths:
  - the data model's F05 unit-of-work row (`docs/architecture/data-model.md`);
  - `packages/contracts/README.md`'s Stage B bullet;
  - `proofs/postgres-ordering/README.md`;
  - the record's "Stage B, correction C2" and "Manager verification of Stage B's correction C2";
- read only, as the guards and cases read them:
  - `glow_profiles/media.py` (`run_check` above all), `media_fixtures.py`, `staff.py`, `operations.py` and `settings_store.py`;
  - `glow_persistence/models.py` and `glow_persistence/migrations/0008_media_lifecycle.py`;
  - `proofs/postgres-ordering/glow_ordering_proof/profile_suite.py` (the scans' lines);
- the runs: 42990527042 and 42992446669, and the PR run on PR44's head (event `pull_request`), once it has finished.

**Out of scope:** the application code itself, which the full review read at `7538c76` and C2 did not change. A finding there is reported as pre-existing.

**The focus:**
1. **F1 closed** (T9).
   - `media.a_hold_stops_the_checks_approval` shows a hold stopping the check's approval: the outcome `held`, twice, with the snapshot unchanged (the asset, the profile, `StaffAudit`, the outbox, the store's delivery references). Released, the same check approves.
   - `RouteTests.test_a_hold_returns_before_the_approval_writes_anything` fails if the hold's answer is ignored, or if any of the approval's writes comes before the return.
   - Try edits of your own beyond R1 and M7: for example, the held branch writing an audit row before it returns, the hold asked after `transition`, or the answer kept while its branch falls through. Name any plausible edit that still passes both.
2. **F2 closed** (T14).
   - The guard fails on any text naming `PolicyRevision` or its table in a scanned source outside `glow_persistence/models.py` and `glow_profiles/settings_store.py`.
   - Each of `POINTER_READS`' four entries is a read in the proof, not a lock.
   - `test_the_search_word_matches_the_models_table` holds.
   - Try spellings beyond R2a, R2b and M9. Are the guard's recorded limits (names built at run time; sources outside the scanned roots) the whole list?
3. **F3 closed** (T7).
   - The guard flags every creation of `MediaAsset` except `request_upload`'s `upload_pending`, and every creation that sets a state, of any model, outside `CREATIONS_WITH_STATE`.
   - Each of its seven entries is its model's initial state, pinned by file, function, call and state expression, so a changed state (`md.UPLOAD_PENDING` to `md.APPROVED`, say) fails.
   - Are the recorded limits true and complete: a class under a lower-case name, a state passed by position or in a prebuilt dict, raw SQL, modules outside the scan?
4. **F4 closed** (T8, T16, T19).
   - The ledger holds what the record's item 4 lists: every object key, grant reference, delivery reference and credential token, and each photo's bytes as hex, as the start of their `repr` and as printable text, each as written and as JSON escapes it.
   - `ObservedObjects` keeps an object written and purged within one case.
   - Check that `watch_store` and `hold_media` run around every case, and that a failure to gather fails the case.
   - Check that nothing C2 added prints a value it holds (the line `ERROR: the value ledger's photo values: …` included).
   - Could any form match benign output often enough that the scan would be weakened later? Consider the PNG signature that every photo shares, and short prefixes.
   - Does any record still claim more than the ledger holds?
   - Deviation 4: `profile_suite.py`'s value-scan line names only the member values' kinds, while its count includes the photos' values. Say whether that is a nit, and where it belongs.
5. **F5 closed** (T21).
   - `constraints.malformed_media_writes_are_refused` makes 21 writes. Each breaks one constraint only and is refused by PostgreSQL by that constraint's name, and the snapshot is unchanged afterwards.
   - The 13 are read from migration 0008, and the catalog's set must equal `MEDIA_CATALOG`, so a new constraint without a write fails.
   - `SHADOWED` is right: Django's `version >= 0` checks are shadowed by 0008's `version >= 1`.
   - Deviation 1: confirm that the migration declares 13 constraints, not the review's 11.
   - Is a refused write's error text kept or printed anywhere?
6. **The records.**
   - N2, N5, N6, N7 and N9 as corrected: C2's section, the data model's F05 unit-of-work row, `packages/contracts/README.md`'s Stage B bullet and the proof README.
   - C2's section and the manager's verification, against the code and the runs.
   - C2's data-model sentence goes to the Dev Manager's pre-merge read, so say whether it is true as written.
7. **No test weakened or vacuous.**
   - C2 removed or loosened no assertion.
   - `CASE_COUNT` 67 to 69 and `ProfilePlanTests`' Stage B count 14 to 15 match the two cases.
   - Each new check fails for the edit it names. Re-run at least three reversals yourself, offline; any database ones are informational.
8. **Scope.** `git diff --name-only 7538c7642f38ac374f2a0f7ca22c8887a3a31922 5bcbe549b7370264785c158ac95931730f7bf331 -- . ':!*.md'` lists exactly the six test and suite paths above. No application code, model, migration, DTO, registry entry, workflow, lock or dependency changed.

**Re-run, at least,** in a scratch copy of `5bcbe54`:
- **The API's checks:** `manage.py check`, `manage.py test tests`, `ruff` and the configured `mypy`. The contract tests. The proof's offline tests, `ruff` and `mypy`.
- **At least three reversals of your own** against F1's, F2's and F3's offline checks, one each.
- **The profile suite, informational,** on a throwaway PostgreSQL under P06.DB's D4, if Docker allows, with a reversal against F4's ledger or F5's case.

**The correction classes** (the exact-head review's, as they bear on C2). A correction pass takes every blocking finding, and any should-fix finding that could:
- let a test pass where it should fail, or fail where the code is right;
- make a record claim more than the code, the tests or the runs show;
- let an object key, an upload credential, a reference or a photo's bytes reach a log, an error, a CI log or an artifact unscanned;
- let a photo reach `approved` other than through its one path, unguarded;
- let the check approve a held photo, untested;
- let a transaction take settings pointers out of name order without the check stopping it;
- let a malformed media write go unrefused, untested.

Everything else goes into the records. For each finding, say whether it falls in a class.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 10. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
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
  - read, print or use the value of any `AWS_*` variable (section 1);
  - call any provider or HDE, R2 or Cloudflare included, send any email, or run any command in `proofs/stream-chat/`;
  - connect to any database but a throwaway one you started under D4's conditions, HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:**
   `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`.
   If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*` or `CF_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_)'` prints names only. If any is present, stop and report.
3. **Three AWS names are expected:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_CA_BUNDLE` (DM-57 and DM-58). `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values. If any other `AWS_*` name is present, stop and report.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
5. **The toolchain:** CPython 3.12.14 as `python3.12`; Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`; Docker if present. Record their versions.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API). No `AWS_*` name passes.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, 4dc2061a33c6f63e2887b11aeb2fd32d6224e23e
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 5bcbe549b7370264785c158ac95931730f7bf331 HEAD -- .github scripts services apps packages proofs ':!*.md' && echo "the code head under review"
git diff --quiet 5bcbe549b7370264785c158ac95931730f7bf331 origin/claude/magical-wozniak-yfmmx2 -- .github scripts services apps packages proofs ':!*.md' && echo "no code on the live branch after 5bcbe54"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-10-sv2-profiles-media.md | grep -c -E "^#+ Delta review of Stage B's correction C2"   # must print 0
```

If any check fails, stop and report. The prompt is stale if any of these holds:
- its commit is not on the live branch;
- a non-Markdown path changed there after `5bcbe54`;
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
- root `AGENTS.md` and `CLAUDE.md`; `proofs/postgres-ordering/README.md`; `packages/contracts/README.md`;
- the brief, revision 8: "Stage B, correction C2 (the exact-head review)";
- the record: "Exact-head review of Stage B after C1" (its threat model and dispositions), "Stage B, correction C2" and "Manager verification of Stage B's correction C2";
- every path in your scope.

## 3. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- **the verdict:** approve, approve with nits, or changes required;
- the findings, in a table: number, severity, correction class or not, file and line, what is wrong, and the evidence;
- the answer to each focus point (1 to 8), one or two lines each;
- the reversals you ran, with their results, the local database ones named informational;
- the runs you read, with each job's result and the profile lines;
- what you ran, and what you could not run or read.
