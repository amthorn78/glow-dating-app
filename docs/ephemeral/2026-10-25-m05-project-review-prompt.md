# M05 project review prompt — an independent review of the whole Glow app project, toward completion (OD-48)

- **Owner:** App Manager 8. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 25 October 2026.**
- **Durable brief:** [M05 — Whole-project review](../planning/m05-whole-project-review.md), revision 1.
- **Where the result goes:**
  - The review writes its evidence record, `docs/testing/evidence/2026-10-25-m05-project-review.md`, on its own session branch, and reports to Nathan.
  - The manager adds "Manager verification of M05" to that record, with a disposition for each finding, and a line to the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 3.37 (confidence 0.55); rung probabilities low 0.00, medium 0.00, high 0.17, extra high 0.31, max 0.49, ultracode 0.03. Model probabilities Fable 5.1 0.23, Opus 5.5 0.77, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.69). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.039, Fable 5.1 at extra high 0.071, Fable 5.1 at max 0.113, Fable 5.1 at ultracode 0.007, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.000, Opus 5.5 at high 0.131, Opus 5.5 at extra high 0.239, Opus 5.5 at max 0.377, Opus 5.5 at ultracode 0.023, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Flags: boundary between extra high and max. Sent 2026-10-25T23:35:11Z. Nathan picks the cell.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** none before it runs. The prompt authorizes no credential use and no live provider action. The review's purpose and its authority to correct are Nathan's direction (OD-48). It assesses the manager's and the Dev Manager's own work, so neither shapes it first. Its governing proposals reach the Dev Manager before anything governing merges (the brief, "Review plan").
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29): no other session runs while it does, and M04 waits for it.
- **Deletion condition:** prune after the manager's dispositions of M05 are recorded and every accepted item has its home.

**Manager:** before giving this prompt to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **project review session (M05)** for the Glow dating app, private repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. You are not the manager, the Dev Manager or an implementer. This prompt is revision 1, from commit `<RECORDS_COMMIT>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**Your assignment, in Nathan's words** (25 October 2026, OD-48): *"I want you to submit a whole project review for independent assessment by a project reviewer session. It's job will be to make sure we are on track, correct any errors, and add anything that was missed to bring us to completion."*

That is three jobs:
1. **On track:** is the project on course to its plan's completion, and at what risk?
2. **Correct any errors:** find them in the code, the tests, CI and the records; correct those in the records you may write, and specify the rest.
3. **Add anything that was missed** that completion needs.

**Your independence.**
- Two sessions run the project: App Manager 8, the manager, who wrote this prompt, and Dev Manager 3, its second-layer reviewer. You are independent of both. Assess their work and their process as well as the product.
- Every record is a claim to verify against primary sources: the code, the tests you run, Git history and CI runs. That includes the handoff, the evidence records, the Dev Manager's reports, Notion and this prompt.
- Say what you verified and how, and what you could not verify.

## Where the project stands, as the records claim it

Verify each point; take none of them from here.
- **The plan** is PF01, `docs/pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md` (revision 1.12), under the authority index PF00, `docs/pf-canon/GAPP-PF00-Canon-Index-and-Authority.md`.
  - It has phases P00 to P12. P11 is the final database and live integration, and P12 the verified release-candidate handoff. Public release is separate.
- **Done, as claimed:**
  - P00 to P05, at fixture scope (23 to 25 September 2026);
  - M01, the move to repository Markdown and Claude Code, and M02, the Claude setup and workflow optimization;
  - P06.1, the Stream Chat permissions proof (PR27, `47db18d`), and P06.DB, the disposable-PostgreSQL proof (PR28, `3afffb3`);
  - P06.2, the chat integration, in five merges: Stage A (PR29, `02072f4`), B1 (PR30, `3272eed`), B2 (PR31, `3572c41`), C1 (PR32, `a8e9528`) and C2 (PR33, `5b9bcb1`, 25 October).
- **What remains:** P06.3 (privacy-safe notifications) and P07 to P12.
- **`main`** is at `5b9bcb1`. Its push run, 40243775584, concluded `success`.
- **Paused:** feature work stays paused (OD-05), except where Nathan's recorded direction resumed it: P06.1 (OD-12) and P06.2 (OD-38). Nothing else is resumed.
- **Next after you:** M04, branch hygiene, an automatic cleanup of merged branches (OD-39). It waits for this review.
- **Live task state** is in Notion: *Glow Dating App — Implementation Control* and its *Work Register*. Notion also carries a copy of the operational guidance and of the owner-direction register. On any difference, the repository wins (OD-26, OD-27).
- **The last whole picture** is `docs/continuity/state-of-the-app.md`, a snapshot as of 25 September 2026, stale since.
- **HDE:** the Glow HD Engine is a separate, protected system. The app will consume its results through a contract that is still provisional (PF01 A01). The HDE contract request, `docs/planning/hde-contract-request.md`, is in Nathan's own process (OD-23).
- **The process** has five parts:
  - Nathan's manual relay, `docs/planning/manager-workflow.md`;
  - the Dev Manager, `docs/planning/dev-manager.md`, with consultations DM-01 to DM-30;
  - exact-head reviews, and Codex's code reviews (OD-41);
  - Nathan's standing directions, `docs/continuity/owner-directions.md` (OD-01 to OD-48);
  - the managers' mistakes log, `docs/continuity/manager-mistakes.md`.

## How you work

- **Tools:** you may use any tools, subagents, scheduled wake-ups or other capabilities you need. The review is large. Split it across subagents by component and by phase where that helps, and check what they report before you rely on it.
- **What you may write** (the brief's "Owned paths"). Write only on your own session branch:
  - your evidence record, `docs/testing/evidence/2026-10-25-m05-project-review.md`;
  - corrections and additions in non-governing Markdown, each marked in the text as `[Corrected by M05, finding N: what was there, and why]` or `[Added by M05, finding N]`, in:
    - `docs/architecture/`;
    - `docs/testing/`, including the P11 plan (`docs/testing/p11-deferred-acceptance.md`). In `docs/testing/evidence/`, add annotations only, and never change what a record says happened;
    - `docs/operations/`, except the CI policy (`docs/operations/ci-and-branch-policy.md`);
    - `docs/planning/`, except the manager workflow, the Dev Manager charter, `start-prompts/`, `sources/`, the reasoning-strength matrix and its evidence (`reasoning-level-matrix.md`, `reasoning-level-evidence.md`) and the HDE contract request.
  - Keep each change minimal and tied to a finding: no rewrites, restructuring or style edits, and no deleted history.
- **What you propose as exact text, changing nothing:**
  - governing Markdown: `AGENTS.md` and `CLAUDE.md` at any level, `docs/pf-canon/`, the manager workflow, the Dev Manager charter, the CI policy, the owner-direction register and `docs/planning/start-prompts/`;
  - `docs/README.md`, `docs/adr/` and the component READMEs;
  - the files excluded above;
  - Notion, including new Work Register rows and changed states.
- **What you never change:**
  - any non-Markdown file: code, tests, configuration, workflows, scripts, dependency files, contracts or fixtures;
  - anything under a `.claude/` directory;
  - `docs/continuity/` and `docs/ephemeral/`.
- **A code defect is a finding,** with a recommended fix and work item. Fix no code: each code change needs its own checks and exact-head review (the CI policy), and work runs one item at a time (OD-29).
- **Push only your own session branch,** with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`. Open no PR, post no comment, re-run or dispatch no workflow, and write nothing to Notion.
- **Reversals and scratch work** go in a copy outside the repository, never the checkout. Use absolute paths.
- **Never:**
  - dump the environment, or print a credential, token, password or connection value;
  - call Stream or any other provider, or run any harness or proof command that reaches one;
  - connect to any database, HDE, Railway or other external service. The only network use allowed is the package installs below, through the session's proxy, and `npm audit` against the same registry;
  - run `playwright install`, `eas` or `migrate`;
  - put a credential in any file, commit or report.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If one is present, stop and report: this session must start in `Glow App - No Stream`.
3. **The toolchain.** The pinned toolchain is in `$HOME/.local/bin`: Node 24.19.0, npm 11.9.0 and Python 3.12.14. Put `$HOME/.local/bin` first on PATH in every process you run.
4. **A clean process environment.** Run each component's commands in one, as `docs/operations/local-development.md` and the READMEs show: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables. Installs get the proxy and CA variables by reference, never printed.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <RECORDS_COMMIT>
git rev-parse HEAD                     # must print <RECORDS_COMMIT>
git rev-parse origin/main              # must print 5b9bcb1390a58420bef50f524934526d9c22325d
git merge-base --is-ancestor <RECORDS_COMMIT> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git merge-base --is-ancestor origin/main HEAD && echo "main is included"
git diff --name-only origin/main HEAD | grep -v -E '\.md$'                                    # must print nothing
git diff --name-only origin/main origin/claude/magical-wozniak-yfmmx2 | grep -v -E '\.md$'    # must print nothing
git diff --name-only origin/main origin/claude/magical-wozniak-yfmmx2 | grep -i -E '(^|/)\.claude/'   # must print nothing
git ls-tree --name-only origin/claude/magical-wozniak-yfmmx2 -- docs/testing/evidence/2026-10-25-m05-project-review.md   # must print nothing
```

If any check fails, stop and report. The prompt is stale if its commit is not on the live branch, if `main` moved or the live branch gained a non-Markdown change, or if this review's record already exists there (AM5-15).

**Then put your session branch at this commit** before your first commit: `git switch -C <your session branch> <RECORDS_COMMIT>`.

**Classify, for the record,** with the trusted base policy outside the candidate tree and full SHAs, from the repository root:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
```

- **Expected:** `"full": false` and `"reason": "ordinary-docs-only"`, since the manager branch adds only Markdown after `main`.
- **Then continue, whatever it prints.** Root `AGENTS.md` tells a review of a pull request to classify the PR's complete diff, and to stop on `ordinary-docs-only`. This assignment reviews no pull request. Its object is the whole repository at `<RECORDS_COMMIT>`, by Nathan's direction (OD-48). The code it reads is `main`'s, which merged through the project's full-scope reviews.

## 3. Read first, whole, at `HEAD`

- root `AGENTS.md` and `CLAUDE.md`, and `apps/mobile/AGENTS.md`;
- `docs/README.md`, the documentation map and its one-home rule;
- PF00 and PF01;
- `docs/continuity/current-handoff.md`, `docs/continuity/owner-directions.md` and `docs/continuity/state-of-the-app.md`;
- `docs/planning/manager-workflow.md`, `docs/planning/dev-manager.md` and `docs/operations/ci-and-branch-policy.md`;
- the M05 brief, `docs/planning/m05-whole-project-review.md`;
- the P11 plan, `docs/testing/p11-deferred-acceptance.md`.

Then read whatever each part of section 4 needs.

## 4. What to review

### A. The plan

1. Is PF01 current with Nathan's directions (OD-01 to OD-48) and with what was built? Name each statement that is stale, contradicted or superseded.
2. Does each phase, P00 to P12, have acceptance that a session can check? Name the vague ones.
3. Are these each current, owned and placed in a phase?
   - §7's product and security requirements;
   - §10's decisions (D01 to D10), assumptions (A01 to A08) and gates;
   - §11's final acceptance and risks (R01 to R06).
4. Is anything that completion plainly needs missing from the plan?
   - Measure against PF01 §1's product baseline, §7, §11's final acceptance and §10's external gates.
   - Measure too against what a dating app needs to pass app-store review.
   - Anything beyond PF01 is a proposal for Nathan, labelled as such, not a requirement.

### B. Status, phase by phase

For each phase and work item (P00 to P12; P06.1, P06.DB, P06.2 and P06.3; M01 to M04):
- Set the claimed state beside what Git, the code, the tests and CI show. Take the claim from the Work Register if you can read Notion; otherwise from the handoff and the evidence records.
- For each item claimed done:
  - is the phase's acceptance met at the scope claimed?
  - is everything left for later recorded in the P11 plan or another named home?
- What is claimed and not shown? What is done and not recorded?

### C. Code, tests and CI

The components are `apps/mobile` (the Expo app), `services/api` (the Django API), `packages/contracts`, `proofs/stream-chat`, `proofs/postgres-ordering`, `.github/workflows/foundation.yml` and `scripts/`. Review them in this order of priority:

1. **The protected boundaries:**
   - the HDE boundary (PF01 D08, protected by effect);
   - no production database connection (P11 owns it);
   - the fixture-only runtime guards, the private projections and eligibility freshness;
   - the chat display rule (ADR 0003): no provider data reaches a render, a stored client state or a log;
   - no provider credential in the client (OD-45), and no credential in source.
2. **PF01 §7's product and security requirements,** as far as the built phases implement them.
3. **The domain rules** against `docs/architecture/`: onboarding, profiles, media, eligibility, discovery, matching, unmatch and block, and chat delivery, reads and revocation.
4. **The tests:** does each fail when the behaviour it names breaks? Sample the critical ones with reversals, in a scratch copy.
5. **CI:**
   - what each job runs;
   - what can pass without running: skips, soft failures, `continue-on-error`, the documentation exemption;
   - the classification gate, the pinned actions and the timeouts;
   - the latest runs on `main`.
6. **Dependencies:** pinned and locked; known advisories, with `npm audit` in each Node package and the recorded `follow-redirects` advisory.

Read the boundary-critical modules whole. Every finding names the file and line, and its evidence: a failing test, a reversal or a trace.

### D. The records

1. **The handoff and the register:** is each row's state and home current?
2. **The mistakes log:** are its recorded preventions applied in the procedures?
3. **The Dev Manager's review log:** is each accepted disposition applied where it says?
4. **The evidence records:** do their claims match the runs and the code?
5. **The P11 plan:** does it hold every item deferred from P04 to P06.2?
6. **`docs/architecture/`, `docs/operations/` and `docs/testing/`:** any stale statement, or wrong command, path or name?
7. **The HDE contract request,** and `docs/ephemeral/`: which prompts have met their deletion condition?
8. **The one-home rule** of `docs/README.md`: duplicates and contradictions.
9. **Notion,** if your session has the connector. Read it, never write it, and list every mismatch with the repository:
   - *Implementation Control*, https://app.notion.com/p/3e44590a05eb8118bf02f0dc0c3ea57c;
   - its *Work Register*, https://app.notion.com/p/71b769915b5b4e00830663770bc95f7e.

   Without the connector, record that as a limit.

### E. What was missed

Find everything completion needs that no plan, record or work item holds. Draw on A to D, on PF01's final acceptance (§11) and external gates (§10), and on the remaining phases, P06.3 and P07 to P12. For each item, give:
- what it is, and why completion needs it, with the evidence;
- the proposed home: a phase, a work item, the P11 plan or a brief;
- the owner: Nathan, the manager, an implementation session or an outside party;
- whether you added it or propose it.

### F. The process

1. **Measure,** from Git and the records, for each work item since M02:
   - the dates;
   - the implementation passes and the correction passes;
   - the exact-head reviews, the Dev Manager consultations and Codex's findings;
   - the records commits.

   Count the mistakes log by class. How many passes found real defects, and how many changed only records?
2. **Assess** whether the process is proportionate to what remains: P06.3 and P07 to P12.
   - PF01 §11 asks for a reforecast from completed evidence, with hands-on effort kept apart from external waiting.
   - Make no calendar promise.
3. **Propose** what to keep, simplify or drop, each with its expected effect and its risk. Give governing changes as exact text.

### G. The path to completion

1. **The ordered work items** from now to P12. For each, give:
   - its ID, existing or proposed, and its outcome;
   - its dependencies and any external gate;
   - the evidence that closes it;
   - whether it needs a decision of Nathan's.
2. **Nathan's decisions, in OD-32's form.** Each says what it is, what breaks without it, the options and your recommendation.
3. **The next item:** M04 or another, and why.

## 5. The checks

Run each component's offline checks at `HEAD`, in a clean process environment. Run them as the Foundation workflow's jobs run them (`.github/workflows/foundation.yml`) and as `docs/operations/local-development.md` gives them. A difference between the two is a finding.

- **`scripts/`:** `python3.12 -I -m unittest discover -s scripts -p 'test_change_scope.py' -v`.
- **The API, `services/api`:**
  - a `python3.12` virtual environment from `requirements-dev.lock`, installed with `--require-hashes`, then `pip check`;
  - `GLOW_ENV=test`: `manage.py check` and `manage.py test tests --verbosity 2`;
  - `ruff check .`, `ruff format --check .` and `mypy`;
  - the contracts' Python tests, and `glow_persistence.static_check`.
- **The contracts, `packages/contracts`:** `npm ci --ignore-scripts`, `npm run generate` with no diff, and `npm run check`.
- **The mobile app, `apps/mobile`:**
  - `npm ci --ignore-scripts`, `npm run check`, `EXPO_OFFLINE=1 npm run check:expo` and `EXPO_OFFLINE=1 npm run export:development`;
  - `npm run test:rendered` only if it runs without `playwright install`, marked "informational, not the pinned browser".
- **The smoke:** `node scripts/smoke.mjs` and `node --test scripts/smoke.test.mjs`, with `GLOW_SMOKE_PYTHON` set to the API's virtual environment. It runs on loopback only.
- **The Stream proof, `proofs/stream-chat`:** the proof job's offline steps only. These are its unit tests, `ruff`, `mypy`, `node --check` on `client/*.cjs` and `python checks/run_plan.py`. Never run a command that calls Stream.
- **The database proof, `proofs/postgres-ordering`:** its unit tests, `ruff` and `mypy` only.
- **What needs Docker or a database:** the database proof's PostgreSQL steps and the API artifact image. Read them in the logs of `main`'s run 40243775584, and in the run that last exercised them if that run skipped them.

Record each command and its exact result: counts, durations and exit status. Name any check you could not run, and why.

## 6. Your record

Write `docs/testing/evidence/2026-10-25-m05-project-review.md` with these sections:

1. **Identity:**
   - the prompt's revision and commit;
   - your branch and its head;
   - the date;
   - the environment check, and the start gate's and the classification's results.
2. **Verdict:** on track, at risk or off track, in a short paragraph with its evidence.
3. **Status by phase:** a table with these columns: the phase or item; the claimed state and where it is claimed; the verified state and its evidence; what remains.
4. **Findings,** numbered. Each gives:
   - its severity:
     - **critical:** a protected boundary or a security requirement is broken, or a claimed result is false;
     - **major:** it blocks or endangers completion, or a record misleads a decision;
     - **minor:** wrong, but contained;
     - **nit**;
   - its area (A to G) and its location: a file and line, a run, or a record;
   - its evidence;
   - one of three outcomes: the correction made, with its commit; the exact correction proposed; or the recommended work item.
5. **Missed items** (section 4, E).
6. **The process** (F).
7. **The path to completion** (G), with Nathan's decisions.
8. **Proposed text:** exact text per file, governing or otherwise, with the finding each serves.
9. **Notion mismatches.**
10. **The checks run,** with their exact results, and the **limits** of the review.
11. **Corrections made:** each commit, with the files and findings it changes.

The record's last line is `Status: complete`.

**Before you report,** check that:
- `git diff --name-only <RECORDS_COMMIT> HEAD` lists only your record and paths inside your write scope;
- the trusted classification of your own change prints `"full": false` and `"reason": "ordinary-docs-only"`:

  ```bash
  policy_dir=$(mktemp -d)
  git show "$(git rev-parse origin/main):scripts/change_scope.py" > "$policy_dir/change_scope.py"
  python3 -I "$policy_dir/change_scope.py" --base <RECORDS_COMMIT> --head "$(git rev-parse HEAD)" --merge-base
  ```

- `git diff --check <RECORDS_COMMIT> HEAD` prints nothing;
- `git status` is clean, and your branch is pushed.

## 7. Report

Your final message is the report Nathan relays. Keep it to about 60 lines; the record holds the detail:
- the prompt's revision and commit, and your branch with its final head;
- the environment check, the start gate and both classifications;
- the verdict, in two or three sentences;
- the findings counted by severity, and the five most important, one line each;
- Nathan's decisions, one line each (each is in OD-32's form in the record);
- the proposed next item;
- the checks, with their headline results, and the limits.
