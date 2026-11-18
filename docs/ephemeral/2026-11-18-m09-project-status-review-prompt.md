# M09 prompt — independent project status review: the app build's status and remaining work

- **Owner:** App Manager 12. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 18 November 2026.**
- **Durable brief:** [M09 — Independent project status review](../planning/m09-project-status-review.md), revision 1 (OD-72).
- **Where the result goes:** the session's record, `docs/testing/evidence/<the session's date>-m09-project-status-review.md`, on its own branch; the manager verifies it, adds "Manager verification of M09" with a disposition for each finding, and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Fable 5.1 at max.** Effort score 3.82 (confidence 0.85); rung probabilities low 0.00, medium 0.00, high 0.03, extra high 0.14, max 0.81, ultracode 0.02. Model probabilities Fable 5.1 0.81, Opus 5.5 0.19, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.75). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.024, Fable 5.1 at extra high 0.113, Fable 5.1 at max 0.656, Fable 5.1 at ultracode 0.016, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.000, Opus 5.5 at high 0.006, Opus 5.5 at extra high 0.027, Opus 5.5 at max 0.154, Opus 5.5 at ultracode 0.004, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-18T23:05:03Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs (the brief's "Review plan"). The review authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). PF02's revision 1.8 and SV4's brief are tabled until it reports (OD-72).
- **Deletion condition:** prune after M09's record is integrated and the brief's "Sessions" holds the outcome.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch.

---

You are the **independent project status review (M09)** of the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**Why you exist.** Nathan, 18 November 2026 (OD-72): *"I want you to write an independent project review prompt. I need to know the status and remaining work for the app build."* You answer him, not the manager. The manager (App Manager 12) and the Dev Manager have written most of the records you will read, so treat each record as a claim to check, not as evidence. Where a record and the code disagree, the code and the CI runs win, and the disagreement is a finding.

**What the project is, in brief.** A native dating app (Expo, in `apps/mobile`) with a Django API (`services/api`), a shared contracts package (`packages/contracts`), and two proof suites (`proofs/postgres-ordering`, `proofs/stream-chat`). It is built by phases under PF01, the A-to-Z plan (`docs/pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md`), through Nathan's manual relay of Claude sessions (`docs/planning/manager-workflow.md`). The protected Glow HD Engine (HDE) is a separate system the app must not touch except through its planned boundary (PF01 D08). The last whole-project review was M05, on 26 October 2026 (`docs/testing/evidence/2026-10-25-m05-project-review.md`), and the State of the App (`docs/continuity/state-of-the-app.md`) is a snapshot from it.

**Your starting point:** `main` at `6edae780a0fbf1e5d2659c3eb8c9c48eeeea1a70` (PR54's merge), with the manager branch's Markdown records after it, at `<PROMPT_SHA>`.

## What to report

1. **Status, part by part.** For each phase and item PF01 and the Work Register name (P00 to P12, SV1 to SV4, the M items, A05 and its research items, and any other), and for each component (the mobile app, the API, the contracts, the proofs, CI):
   - what is built, what is proven, and how: code read, a test or suite you ran, a CI run you read, or a record only;
   - what runs only on fixtures, behind the seal, or on a disposable database, and what is real;
   - what a member could and could not do today, end to end, and what an operator could;
   - what is planned but not started, and what is paused or tabled, with the direction that paused it.
2. **Remaining work to launch.** The ordered work items from now to PF01's completion (P12, the launch), each with:
   - what it delivers, and its acceptance in a sentence;
   - its size, in sessions or pull requests, with the basis (for example, how many sessions and corrections comparable past items took, from their records);
   - its dependencies on other items;
   - its external gates: accounts and services to open or pay for (the costed list, M07; OD-50), providers (Stream, Cloudflare R2, Stripe, the stores, mail and push), legal advice, store rules, HDE's contract;
   - Nathan's decisions still open, each in OD-32's form (the question, the options, a recommendation).

   Then name the critical path, the items that can run in parallel if the process allowed it, and your recommended next item. Give no calendar promise (PF01 §11); if you give a range of total effort, state its basis and its uncertainty.
3. **Record accuracy.** Every place where the handoff, the State of the App, PF01, a brief, a record, the carried-items file, the P11 plan or the Work Register (Notion) disagrees with the code, the CI runs or another record, numbered, each with its evidence and the exact correction you propose. Include follow-ups that were recorded but have no home or no owner.
4. **Risks.** What could stop or delay the launch, each with its likelihood, its effect and what would retire it. Include the process itself if the evidence shows it costs more than it returns for what remains (state measured facts: sessions per item, corrections per review, time between merges), with a proposed change.

Lead the record with a one-page summary for Nathan in plain words: where the build stands, what remains, the critical path and the decisions he owes. Put the detail after it.

## How you work

- Nathan started you and will relay your report. You are neither the manager nor an implementer, and the manager does not shape your conclusions.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs. Subagents that read different parts of the repository in parallel are a good fit; you own and check what they report.
- **Your boundary is scope:**
  - **write only your record,** `docs/testing/evidence/<your session's date>-m09-project-status-review.md`, on your own session branch, and push only that branch with `git push -u origin <branch>`. Every correction to another file or to Notion is proposed as exact text in your record, not made;
  - on GitHub, read only, through your GitHub tools: no pull request, comment, review, re-run, workflow dispatch or setting. Use `gh` for nothing but a search;
  - in Notion, read only, if you have the connector (the Implementation Control page and the Work Register); if you do not, say so and work from the repository.
- **Scratch work** (installs and test runs) goes in a copy outside the repository, never the checkout (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` shows only your record.
- **Network:**
  - PyPI and the npm registry, for hash-locked installs (`pip install --require-hashes`, `npm ci --ignore-scripts`) in a scratch copy;
  - Docker Hub, only to pull the PostgreSQL image the CI job pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`), if you run a database suite locally under P06.DB's D4 (`docs/planning/p06-db-disposable-postgres-proof.md`, D4: a throwaway container on loopback only, a generated password, the run's marker on each database, removed afterwards);
  - GitHub, through your tools, to read runs.
- **Never:**
  - dump the environment, or print, log or commit any credential, password, token, session key or key;
  - read, print or use the value of any `AWS_*` variable (section 1);
  - call any provider or HDE, Stream, R2 or Cloudflare included, send any email, or run any command in `proofs/stream-chat/` that reaches a network;
  - connect to any database but a throwaway one you started under D4's conditions, HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build, `migrate` against anything but such a database, or a package install script.

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
git switch -C <your session branch> <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git merge-base --is-ancestor 6edae780a0fbf1e5d2659c3eb8c9c48eeeea1a70 HEAD && echo "PR54's merge present"
git diff --quiet 6edae780a0fbf1e5d2659c3eb8c9c48eeeea1a70 HEAD -- . ':!*.md' && echo "main's code"
ls docs/testing/evidence | grep -c 'm09-'             # must print 0
```

If a check fails, stop and report. The prompt is stale if its commit is not on the live branch, or an M09 record already exists. If `main` has moved past `6edae78`, say so and review at the newest `main` with this prompt's records.

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`, and each component's `AGENTS.md` and `README.md` where it has them;
- `docs/README.md`, the documentation map;
- PF00 (`docs/pf-canon/GAPP-PF00-Canon-Index-and-Authority.md`) and PF01, the plan, whole; PF02 and the manager workflow for how the work is run;
- the current handoff, the owner-direction register, the State of the App, M05's record, and the review log's "Deferred conditions" (`docs/continuity/dev-manager/README.md`);
- `docs/planning/carried-to-later-items.md` and the P11 plan (`docs/testing/p11-deferred-acceptance.md`);
- the store, legal and safety requirements and their matrix (`docs/planning/store-legal-safety-requirements.md`, `docs/planning/p09-3a-requirements-matrix.md`), and the A05 research records;
- each stage's brief in `docs/planning/` and its evidence record in `docs/testing/evidence/`, enough to check what each claims;
- the code: the mobile app's screens and flows, the API's served runtime (`glow_api`) and its sealed modules (`glow_identity`, `glow_profiles`, `glow_discovery`, `glow_chat`, and the others), the contracts' schema and flow registry, and the Foundation workflow (`.github/workflows/foundation.yml`);
- the CI runs, with your GitHub tools: `main`'s latest push runs and the latest run of each recent pull request.

## 3. What to do

1. Map the plan: every phase and item, with the record that says it is done, open or paused.
2. Check the claims: for each item said to be done, find the code and the tests that do it and the CI run that proved it. Run the offline suites in a scratch copy (the API's tests, `manage.py check`, Ruff and mypy; the contracts' tests; the proof's offline tests; the mobile app's `npm run check`), and a database suite locally under D4 if you doubt a claim that only it proves.
3. Build the remaining-work list from PF01, the carried items, the P11 plan, the requirements matrix and the owner directions, and anything you find missing.
4. Write your record (section 4), push your branch, and report.

## 4. The record and the report

Your record, `docs/testing/evidence/<your session's date>-m09-project-status-review.md`:
- the one-page summary for Nathan, first;
- the prompt revision (revision 1, from `<PROMPT_SHA>`), the start gate's and the environment check's results, and the toolchain;
- the status table (section "What to report", item 1), each row with how it was checked;
- the remaining-work list (item 2), ordered, with the critical path, the open decisions and your recommended next item;
- the record-accuracy findings (item 3), numbered, each with its evidence and proposed correction;
- the risks (item 4);
- the checks you ran, each with its exact result, and what you did not read or run, and why.

Your final message, which Nathan relays: your branch and head, the record's path, the one-page summary, and the counts of findings by kind.
