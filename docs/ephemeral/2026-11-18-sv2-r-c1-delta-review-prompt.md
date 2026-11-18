# SV2-R C1 delta review prompt — the tests for two state refusals, and three carried entries

- **Owner:** App Manager 12. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 18 November 2026.**
- **Durable brief:** [SV2-R — SV2's completion requirements after OD-68](../planning/sv2-r-od-68-requirements-change.md), revision 7, "Correction C1" and "Review plan".
- **Where the result goes:** the report Nathan relays. The manager records it in the evidence record, "Delta review of correction C1", with a disposition for each finding, and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 1.89 (confidence 0.76); rung probabilities low 0.00, medium 0.23, high 0.64, extra high 0.13, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 1.00, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 1.00). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.230, Opus 5.5 at high 0.640, Opus 5.5 at extra high 0.130, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-18T22:01:15Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of PR54's head, which is this prompt's commit (the manager workflow, step 6). A delta review: C1 changes no code (step 6, "A small correction gets a delta re-review").
- **Deletion condition:** prune after SV2-R's pull request merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **delta review of SV2-R's correction C1**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one exact head of a tests-only correction, with the exact-head review's security focus. This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **SV2-R** (its brief, `docs/planning/sv2-r-od-68-requirements-change.md`, revision 7; Nathan's direction OD-68) set ID verification aside as a profile requirement and put the automated photo check behind a toggle, `media.photo_check`, off at launch, with a recheck step for photos approved while it was off. Its code head is `f4703a1`.
- **The exact-head review of `f4703a1`** (the evidence record, `docs/testing/evidence/2026-11-18-sv2-r-requirements-change.md`, "Exact-head review") found the code right and two guards untested. In each case it broke the guard and every suite still passed:
  - **R1:** the recheck's refusal `not_awaiting_recheck` for a photo that is no longer `approved` (its reversal B);
  - **R2:** `run_check`'s refusal `not_in_review` for an `approved` photo, the only stop since SV2-R's two transitions out of `approved` (its reversal A).
- **Correction C1** (the brief's "Correction C1"; branch `claude/modest-cerf-3acfed`, code head `f4c93ea`, records `038282e`; the record's "Correction C1" and "Correction C1, manager verification"):
  - C1.1 and C1.2 pin both refusals offline and in three `sv2r.` profile cases;
  - C1.4 takes up the carried entries N-a (the creation guard), N-d (the held branch's write list) and N-c (a docstring);
  - C1.5 corrects acceptance check 2's row.

  Its run of record, 44402994154, passed all eight jobs, with the profile suite at 77 of 77. The manager merged it into the manager branch at `5d8fab8`.

**The head under review is `f4c93ea`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `f4c93ea` (the start gate checks this).

**Your scope:**
- **The correction:** `git diff 1708b53c4f89b10c9d71325b7a2bdd32aff2fca9 f4c93ea8ed17d26f29a01c5c7e75e910ab925b11`, its five paths, **each read whole at `f4c93ea`**, not the diff alone:
  - `services/api/tests/test_sv2r_requirements.py`;
  - `services/api/tests/test_profile_recompute.py`;
  - `services/api/tests/test_profile_media.py`;
  - `proofs/postgres-ordering/glow_ordering_proof/profile_cases.py`: the three changed `sv2r.` cases whole, and the helpers they use;
  - `proofs/postgres-ordering/glow_ordering_proof/profile_support.py`: the module docstring, `add_bytes` and `RecordingHold`.
- **The code the tests pin, read only:** `services/api/glow_profiles/media.py` (`transition`, `run_check`, `recheck`, `awaiting_recheck`, `_approvals_while_off`), `staff.py` (`restrict_media`) and `glow_domain/media.py` (`TRANSITIONS`). Nothing there changed since `f4703a1`, and a finding there is reported as pre-existing.
- **The records, as claims about the tests and the run:** the record's "Correction C1" section and acceptance check 2's row; the brief's "Correction C1"; the carried-items file's note that C1 takes up N-a, N-c and N-d.
- **The runs:** 44402994154 (C1's run of record) and PR54's `pull_request` run on its head, once it has finished.
- **Out of scope:** SV2-R's code, which the exact-head review covered; the review's N2 to N4, carried by the manager.

**The focus,** with the exact-head review's threat model (in its record section) in mind:
1. **C1.1 (R1):**
   - the offline test fails if the recheck's refusal stops testing that the photo is `md.APPROVED`, and if the refusal moves after a port call or a write;
   - in `sv2r.the_recheck`, the restricted photo really is `review_pending` with its review reference still the toggle's approval, and the removed one really is `removal_pending`, before each recheck;
   - each recheck, with a rejecting and an approving check, gives `no_change` with `not_awaiting_recheck`; neither port is asked; nothing the snapshot covers changes; `awaiting_recheck` lists neither;
   - say whether `_photo_snapshot` misses any write a wrong recheck could make (for example the restriction reference, the removal time or the delivery reference).
2. **C1.2 (R2):**
   - the offline test fails if `run_check`'s refusal on state admits anything but `md.REVIEW_PENDING`, or moves after the restriction check or the toggle's branch;
   - `run_check` on an approved photo, with the toggle off and on, gives `no_change` with `not_in_review`, asks neither port and writes nothing.
3. **The reversals:** re-run the review's reversals A and B; each must fail C1's tests offline and, if Docker allows, on a local disposable database.
4. **N-a, N-d and N-c:**
   - each widened guard sees the spellings its entry names and still sees every spelling it saw at `1708b53`; `_creations_with_state` still leaves out the bulk forms, as before;
   - `_clones` finds nothing in the scanned code, and its test fails when a clone is added;
   - N-c's docstring matches what `add_bytes` holds;
   - a spelling still missed is a nit, not a correction class.
5. **No test weakened or vacuous:**
   - no earlier assertion is removed or loosened;
   - the setup C1 adds (a profile made through the member's route in `sv2r.toggle_on_the_check_decides_as_before`, a second member in `sv2r.the_recheck`) does not change what the earlier steps of those cases prove;
   - `CASE_COUNT` (77), `SV2R_CASES`, `LABEL_NAMES` and `LABEL_BINDINGS` are unchanged;
   - no case could pass while the refusal it guards is wrong.
6. **D17:** no secret, key, original reference or member value in any new log line, result text or assertion message.
7. **The records:** every claim in the texts listed in the scope holds against the tests and the run.

**Re-run, at least,** in a scratch copy of `f4c93ea`:
- **The API's checks:** `manage.py check`, `manage.py test tests`, `ruff` and the configured `mypy`; the contract tests.
- **The proof:** its offline tests, `ruff` and `mypy`.
- **Reversals A and B** (focus item 3), and a reversal for one spelling of each widened guard.
- **The profile suite, informational:** on a throwaway PostgreSQL under P06.DB's D4, if Docker allows.

**The correction classes.** Report every finding with its severity. A further correction takes every blocking finding, and any should-fix finding that could do any of these:
- let a test pass where it should fail, or fail where the code is right;
- leave R1 or R2 untested, or leave a carried entry N-a, N-c or N-d not taken up as its entry says;
- let a secret, a key or a member value reach a log, an error, an event, a CI log or an artifact;
- change code, or add a package or a profile case;
- make a record claim more than the tests or the runs show.

Everything else goes into the records. For each finding, say whether it falls in one of these classes.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 12. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- **Your boundary is scope:** review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches. Read GitHub only through your GitHub tools; use `gh` for nothing but a search.
  - **Scratch work goes in a copy outside the repository,** never the checkout (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
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
3. **AWS names may be present** (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_CA_BUNDLE`). `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
5. **The toolchain:** CPython 3.12.14 as `python3.12`; Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`; Docker if present. Record their versions.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API). No `AWS_*` name passes.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, 15d54f647aa012edf53165f04a0a7e4931a7b67f
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet f4c93ea8ed17d26f29a01c5c7e75e910ab925b11 HEAD -- . ':!*.md' && echo "the head under review"
git diff --quiet f4c93ea8ed17d26f29a01c5c7e75e910ab925b11 origin/claude/magical-wozniak-yfmmx2 -- . ':!*.md' && echo "no code on the live branch after f4c93ea"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-18-sv2-r-requirements-change.md | grep -c -E '^#+ Delta review of correction C1'   # must print 0
```

If any check fails, stop and report. The prompt is stale if any of these holds:
- its commit is not on the live branch;
- a non-Markdown path changed there after `f4c93ea`;
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
- root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`; `proofs/postgres-ordering/README.md`;
- the brief's "Correction C1";
- the record's "Exact-head review", "Correction C1" and "Correction C1, manager verification";
- the carried-items file, "Carried to the next change to SV2's profile guards and suite", and the SV2 record's "Delta review of Stage B's correction C2" (`docs/testing/evidence/2026-11-10-sv2-profiles-media.md`), for N-a, N-c and N-d;
- every path in the scope, as it says.

**The runs,** with your GitHub tools: 44402994154, and PR54's `pull_request` run on its head if it has finished: every job's conclusion, the gate's line, and the Database job's profile lines.

## 3. What to do

1. Review the correction against the focus, item by item.
2. In a scratch copy of `f4c93ea`:
   - re-run the checks and the reversals above, and any you doubt;
   - run the profile suite locally under D4 if you can, informational.
3. For each finding: its severity (blocking, should fix, nit), its file and line, the evidence, and whether it falls in a correction class.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- the focus, item by item, with your verdict on each;
- every finding, with its severity, file and line, evidence and correction class;
- the checks and reversals you re-ran, each with its exact result, and the local suite run if any;
- your verdict: **approve**, **approve with nits** or **changes requested**;
- what you did not read or run, and why.
