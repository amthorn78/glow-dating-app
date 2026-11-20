# SV4 A0-C2 prompt — the correction: the profile and discovery decoy-step tests match the identity test's sequence

- **Owner:** App Manager 12. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 19 November 2026.**
- **Durable brief:** [SV4 — the chat and notifications slice](../planning/sv4-chat-notifications.md), revision 3. **The finding:** R1, in the A0 record's "Delta review of A0-C1" (`docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`), with its disposition table.
- **Where the result goes:**
  - the session's changes to two offline test files, and its section "A0-C2" in the same record, on its own branch;
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification to the record, and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 1.54 (confidence 0.68); rung probabilities low 0.01, medium 0.45, high 0.53, extra high 0.01, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.83, Sonnet 5.5 0.16, Haiku 5.5 0.01 (confidence 0.77). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.008, Opus 5.5 at medium 0.373, Opus 5.5 at high 0.440, Opus 5.5 at extra high 0.008, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.002, Sonnet 5.5 at medium 0.072, Sonnet 5.5 at high 0.085, Sonnet 5.5 at extra high 0.002, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.005, Haiku 5.5 at high 0.005, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Flags: boundary between medium and high. Sent 2026-11-19T19:24:29Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. This prompt authorizes no credential use and no live provider action. Under D-07 the correction goes on the list for Dev Manager 6's pre-merge read of A0.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Then, in order: the manager's verification; PR57's run and Codex's review of its new head; a delta review of C2; Dev Manager 6's pre-merge read; the merge.
- **Deletion condition:** prune after A0's pull request (PR57) merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch (AM11-21).

---

You are the **correction session A0-C2** for SV4 A0, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **A0** (code head `3bf55de`) split the Foundation workflow's database job into four per-suite jobs. Each identity, profile and discovery job has a decoy step that shows its suite's database refusing a decoy database's marker, unchanged.
- **A0-C1** (code head `c78f297`; the record's "A0-C1") added offline tests that pin each job's decoy, `dbshell` and gate checks. In the identity job's decoy-step test (`IdentityWorkflowTests.test_the_migrations_step_refuses_the_decoys_marker_first`) the sequence of whole lines is complete.
- **C1's delta review** (the record's "Delta review of A0-C1") found R1: the profile and discovery decoy-step tests leave out five lines the identity sequence pins, so two of the decoy step's checks can be removed in those jobs with every test passing (its X1 and X2). The manager's disposition: fixed now, by you, tests only.

**This is a correction of tests only.** You add eight lines to one sequence in each of two tests, so that each matches the identity test's sequence line for line. You change no workflow, scan, setting, README, policy or application file, and no other test.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 12. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only these paths:
    - `proofs/postgres-ordering/tests/test_profile_offline.py`: `ProfileWorkflowTests.test_the_migrations_step_refuses_the_decoys_marker_first` only;
    - `proofs/postgres-ordering/tests/test_discovery_offline.py`: `DiscoveryWorkflowTests.test_the_migrations_step_refuses_the_decoys_marker_first` only;
    - the record, section "A0-C2" only;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only, through your GitHub tools: no pull request, comment, review, re-run, workflow dispatch or setting. Use `gh` for nothing but a search. Change nothing in Notion.
- **The stop rule.** Stop and report, with no further change, if any of these holds:
  - **a path:** the work needs any other path or any other test, `.github/workflows/foundation.yml` above all;
  - **the workflow is wrong:** an added line is not in the step at `3bf55de`, or not in the order the identity sequence gives;
  - **an earlier assertion** would have to change or go;
  - **a reversal passes:** after your change, one of the reversals below still passes every offline test.
  - In each case, report it; do not narrow this prompt's words to pass it. A reversal's temporary edit is allowed, and must be undone.
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished; then push your records commit. The workflow runs on pushes to `claude/**` and `ccr-**`; if your branch is named otherwise, say so in the report.
  - **If GitHub never starts the run** (it stays `queued` with no jobs for 30 minutes), do not re-run it, dispatch it, push an empty commit, or ask anyone to re-run it (OD-58). Record it, push your records commit, and report.
  - **If the run fails,** stop and report the failing job and its log lines. Do not re-run it.
- **Network:** PyPI only, for `pip install --require-hashes` from the proof's existing lock. No database runs.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, password, marker, token or key;
  - read, print or use the value of any `AWS_*` variable, or name one in a command;
  - call any provider or HDE, connect to any database, HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script;
  - weaken or delete a test to make the suite pass.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:** `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_|RAILWAY_)'` prints names only. If any is present, stop and report.
3. **AWS and GitHub token names may be present;** record which, by name only, and never read them.
4. **The toolchain:** CPython 3.12.14 as `python3.12`.
5. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git merge-base --is-ancestor <START_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet c78f29747b1fe6e764dd3cb1afe5e6325941a6d2 HEAD -- . ':!*.md' && echo "C1's code head"
git diff --quiet c78f29747b1fe6e764dd3cb1afe5e6325941a6d2 origin/claude/magical-wozniak-yfmmx2 -- . ':!*.md' && echo "no code on the live branch after c78f297"
grep -c -E '^#+ Delta review of A0-C1' docs/testing/evidence/2026-11-19-sv4-chat-notifications.md   # must print 1
grep -c -E '^#+ A0-C2' docs/testing/evidence/2026-11-19-sv4-chat-notifications.md                   # must print 0
```

If a check fails, stop and report. **Then read, completely:** root `AGENTS.md` and `CLAUDE.md`; the record's "A0-C1" and "Delta review of A0-C1"; the workflow's profile and discovery decoy steps ("SV2: show the profile database refuses the decoy database's marker…" and "SV3: show the discovery database refuses…"); `IdentityWorkflowTests.test_the_migrations_step_refuses_the_decoys_marker_first` and the two tests you change.

## 3. What to do

1. **Make each of the two tests' `sequence` lists equal, line for line and in order, to the identity test's sequence, with the suite's names.** That adds eight lines to each:
   - **R1's five, which no assertion pins today:**
     - `outside_before=$(in_profile_db "$outside_pg")` (discovery: `in_discovery_db`), after the counts-before line;
     - `outside_after=$(in_profile_db "$outside_pg")`, after the counts-after line;
     - `if [ -n "$refusal" ]; then`, before the missing-refusal failure line;
     - `if [ "$outside_before" != 0 ] || [ "$outside_after" != 0 ]; then`, after the `cmp` lines;
     - `echo "FAIL: a relation exists outside information_schema and the pg_ schemas"; fail=1`, after it;
   - **three that earlier assertions pin only as substrings:**
     - the helper's `docker exec "$CONTAINER" psql -X -q -At -F ' ' -v ON_ERROR_STOP=1 -U postgres -d glow_profile_proof -c "$1"` (discovery: `glow_discovery_proof`), first;
     - `no_ledger=$(in_profile_db "SELECT to_regclass('public.django_migrations') IS NULL")`, after `outside_after=`;
     - `profile profile-marker python -m django makemigrations --check --dry-run` (discovery: `discovery discovery-marker …`), last.

   Check each line against the step at `3bf55de`. The sequence's order check and every existing assertion stay as they are. Then show, mechanically, that each sequence equals the identity sequence with `identity`, `glow_identity_proof`, `glow_proof`, `marker` and `identity-marker` replaced by the suite's names (`profile`, `glow_profile_proof`, `glow_identity_proof`, `identity-marker`, `profile-marker`; discovery: `discovery`, `glow_discovery_proof`, `glow_profile_proof`, `profile-marker`, `discovery-marker`), and record how.
2. **Reversals,** each on the workflow, restored after it byte for byte (`git status` clean; `git diff --quiet 3bf55de775de1f7aa8cace3f7bc780c97f0b2e98 HEAD -- .github` true), in each of the profile and discovery jobs:
   - X1: the outside-relations failure (its `if` line, its `FAIL` line and its `fi`) removed;
   - X2: `if [ -n "$refusal" ]; then` replaced by `if true; then`;
   - X10: the `outside_before=` line removed;
   - X11: the `outside_after=` line removed;
   - X12: the `no_ledger=` line replaced by `no_ledger=t`.

   Each fails a test after your change. Run each before your change too, and record that X1 and X2 passed then, as the delta review found.

## 4. Checks, then the report

- **The trusted classifier,** from `main` (`c2cffbe`), extracted outside your checkout and run with `python3 -I` and full SHAs, with the checkout as its working directory: `python3 -I <trusted copy>/change_scope.py --base c2cffbe6022637331d73e3558429ff70ab5aa5e3 --head <your code head> --merge-base` prints `"full": true` (reason `behavior-or-empty`).
- **The diff:** `git diff --name-only <START_SHA> <your head>` lists only the two test files and the record; `git diff <START_SHA> <your code head>` removes no line.
- **The proof's checks,** in a clean environment, after `pip install --require-hashes -r requirements-dev.lock` in `proofs/postgres-ordering`: `python -m unittest discover -s tests -t .` (`Ran 383 tests … OK`, since no test is added), `ruff check .`, `ruff format --check .` and `mypy` pass.
- **The run of record,** on your last code commit: every job passed, the four database jobs among them, and the gate printed "Application checks passed".

**The record,** section "A0-C2": this prompt's revision and commit; the start gate's and the environment check's results; the lines added; each reversal before and after, with its failing output; the counts; the run of record. It also says that the "A0-C1" section's sentence "the same sequence of whole lines as the identity test's" was not true of C1's head and is true of yours, with the mechanical comparison.

Your final message, which Nathan relays:
- your branch and head;
- the record's path;
- the run of record's link and result;
- the lines added;
- every reversal's result, before and after;
- every stop, limit and deviation.
