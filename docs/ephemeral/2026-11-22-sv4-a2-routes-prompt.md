# SV4 A2 prompt — chat's sealed routes, the match list and a fifth database suite

- **Owner:** App Manager 13. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 22 November 2026.**
- **Durable brief:** [SV4 — the chat and notifications slice](../planning/sv4-chat-notifications.md), revision 8 (D1, D2, D8 to D15; A2's owned paths, completed in revision 8).
- **Where the result goes:**
  - the session's code on its own branch, and its section "A2" in the SV4 record (`docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`);
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification to the record, and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 3.27 (confidence 0.49); rung probabilities low 0.00, medium 0.02, high 0.16, extra high 0.36, max 0.43, ultracode 0.03. Model probabilities Fable 5.1 0.24, Opus 5.5 0.75, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.67). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.005, Fable 5.1 at high 0.038, Fable 5.1 at extra high 0.086, Fable 5.1 at max 0.103, Fable 5.1 at ultracode 0.007, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.015, Opus 5.5 at high 0.120, Opus 5.5 at extra high 0.270, Opus 5.5 at max 0.323, Opus 5.5 at ultracode 0.022, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.002, Sonnet 5.5 at extra high 0.004, Sonnet 5.5 at max 0.004, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Flags: boundary between extra high and max. Sent 2026-11-22T10:38:02Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs: the brief was read as DM-96, and this prompt authorizes no credential use and no live provider action. A2 changes the CI policy (governing Markdown), so Dev Manager 7 reads that change, with the brief's revision 8, at A2's pre-merge read (D-07).
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and none may be present. `amthorn78/glow-docs` is attached, read-only; this work needs nothing from it (OD-74).
- **It runs alone** (OD-29). Then, in order: the manager's verification; a new pull request from the manager branch, its run and Codex's review; A2's exact-head code and security review, with its threat model; any correction under D-07; Dev Manager 7's pre-merge read; the merge.
- **Deletion condition:** prune after A2's pull request merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch.

---

You are the **implementation session for SV4 A2**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What A2 is.** The third and last of SV4 Stage A's sessions: chat's HTTP surface, sealed until integration, on the rules A1 built. A2 covers:
- **D8, chat's routes:** `POST api/v1/chat/messages`, `GET api/v1/chat/conversations`, `POST api/v1/chat/history`, `POST api/v1/chat/read-cursor`, and `GET api/v1/matches` (D9's match list), each taking its actor from SV1's `GlowActorAuthentication` only, on SV3's view patterns (`glow_discovery/interaction_views.py`); the send's refusals from either member's state or the end of contact all answer one code;
- **D9, the contract's additions:** `ConversationSummary.state` gains `read_only`; a new `MatchList` response; D4's and D6's sentences in `production-contracts.md` and the flow registry, through `npm run generate`;
- **D10, the proof:** a fifth database suite, the chat suite, on its own database (`glow_chat_proof`) in its own job, on D2's pattern;
- **D15, the seal, checked:** the runtime's settings, URL configuration and WSGI application import none of A2's modules.

There is no provider call, deployed URL, real member, HDE call or stored credential. The runtime stays sealed: no route is added to the runtime's URL configuration, and the production catalog's `paths` stay empty.

**The brief, revision 8, is the specification:** D1, D2, D8 to D15, A2's owned paths, the exclusions, the acceptance checks and the review plan. Much of its text is the Dev Manager's words (DM-96, AG1 to AG21). Follow them exactly. Where this prompt summarizes the brief, the brief wins. Where it adds to the brief, it says so; revision 8 records those additions (D11's A2 bullet, D12's "Due at A2", A2's owned paths).

**What came before.**
- **A0 merged** with PR57 at `499ccbb` (20 November 2026): each database suite runs in its own job (ordering, identity, profile, discovery), each with its own PostgreSQL, credentials, marker, decoy database and secret scan, and the gate requires each.
- **A1 merged** with PR58 at `43e794a` (22 November 2026), with its corrections C1 and C2 and DM-98: D3 (a block retires the pair's earlier likes), D4 (a block ends a match as an unmatch does), D5 (reads under OD-60's rule through `chat.history`, read-only at launch), D6 (the send's expected version is the match's), D7 (the token code removed). `main`'s push run 45012202957 passed all eleven jobs.
- **SV1 to SV3** built sign-in, profiles and settings, discovery, interactions and the match read, with SV1's `GlowActorAuthentication` and SV3's view patterns; P06.2 built `glow_chat` (`contact.py`'s `send`, `reads.py`'s `read_history`, `list_conversations` and `move_read_cursor`, `delivery.py`'s `OutboxDelivery`).
- **`main` is at `43e794a`.** The manager branch has changed only Markdown since.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 13. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only A2's owned paths (the brief, revision 8):
    - new modules in `services/api/glow_chat/` for the routes;
    - `services/api/glow_discovery/` (`interaction_views.py`, `interaction_urls.py`, `contract.py`, `interactions.py`), only as D9's `MatchList` needs;
    - the contract: `packages/contracts/production/gapp-api-v1.schema.json`, `flows-v1.json`, `openapi.json` as `npm run generate` keeps it, `packages/contracts/corpus/shared-v1.json`, `packages/contracts/tests/`, and the outputs `npm run generate` writes in `apps/mobile/src/contracts/generated/`;
    - the chat suite's modules in `proofs/postgres-ordering/glow_ordering_proof/`, on the discovery suite's pattern (`chat_cases.py`, `chat_scan.py`, `chat_settings.py`, `chat_suite.py`, `chat_support.py`, `chat_urls.py`, or names you record), `__main__.py`, and `row_locks.py` only if its list of suites changes;
    - `proofs/postgres-ordering/tests/` (the chat suite's offline tests, and the earlier tests listed below) and `proofs/postgres-ordering/README.md` (the chat suite's section);
    - `.github/workflows/foundation.yml` (the chat suite's job, and the gate's lists);
    - `docs/operations/ci-and-branch-policy.md` (the database proof jobs' paragraph: the fifth job), only;
    - `services/api/tests/` (the routes' tests, `test_chat_sealed_runtime.py`, and the earlier tests listed below);
    - `docs/architecture/production-contracts.md` and the flow registry, as D9 says;
    - each file a follow-up below names, only for that follow-up, and only if you change the file for your own work;
    - the record, section "A2" only;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: use the GitHub tools where your session has them, otherwise `gh api` REST `GET` calls, and say in the report which you used. No pull request, comment, review, thread resolution, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule.** Stop and report, with no further change, if any of these holds:
  - **an owned path:** the work needs a path outside the list above, including `services/api/glow_api/`, `glow_chat/contact.py`, `reads.py` or `delivery.py` (A2 calls them unchanged; `contact.py` is pinned by digest), `glow_persistence/` (no migration), `scripts/`, any other `apps/mobile` file, an environment template or a `requirements` file;
  - **a served route:** the work would add a route to the runtime's URL configuration, a path to the production catalog, or a module the runtime's settings or WSGI application import (D15);
  - **a design point:** D8's one code for the send's refusals, D5's read rule, D4's sameness or D6's version would have to change, or a route would need its actor from anything but `GlowActorAuthentication`;
  - **a writer:** your search at your prompt's commit finds a writer of a match's `version` or `contact_version` beyond `glow_chat`'s `block` and `unmatch`, or A2's code would add one (DM-98's AJ2; the carried-items file, AR-4);
  - **a dependency:** a new Python or npm package, or a changed pin (D13);
  - **the timeout:** the chat job, or any other job, no longer fits its `timeout-minutes`;
  - **an earlier test:** a test changes in any way other than gaining A2's entry in a list it pins, every earlier assertion kept (the brief's D11, A2's bullet), or a test would be weakened or deleted;
  - **a provider:** the history read would need anything but the in-memory fixture provider the proof's settings name (D8, "The provider").
  - In each case, report it; do not narrow the brief's words to pass it. A reversal's temporary edit is allowed, and must be undone.
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished. A newer push cancels the earlier run's application jobs, and the run of record is lost. Push your records commit only after the run of record has finished. The workflow runs on pushes to `claude/**` and `ccr-**`; if your branch is named otherwise, say so in the report, since no run starts.
  - **If GitHub never starts the run** (it stays `queued` with no jobs for 30 minutes), do not re-run it, dispatch it, push an empty commit, or ask anyone to re-run it (OD-58). Record it, push your records commit, and report.
  - **If the run fails,** stop and report the failing job and its log lines. Do not re-run it, and push no fix without saying so in the report.
- **Network:** PyPI and the npm registry, for `pip install --require-hashes` and `npm ci --ignore-scripts` from the existing locks only; Docker Hub, only to pull the PostgreSQL image the workflow pins, for a local run (below); GitHub, for your pushes and reads. The environment does not enforce this; you do. A page you cannot reach is named as unread, never filled from memory.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions): a throwaway PostgreSQL in Docker, from the pinned image, on loopback only; a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present; removed afterwards. Migrations reach that database only through the proof's own commands; never run `manage.py migrate` yourself. Local passes are "iteration, not evidence"; the run of record is CI's.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, password, marker, token or key, in any form;
  - read, print or use the value of any `AWS_*` variable, or name one in a command (section 1);
  - call any provider or HDE; connect to any database but a throwaway one you started under D4's conditions; connect to Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script in your own environment;
  - weaken or delete a test to make the suite pass.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:** `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_|RAILWAY_)'` prints names only. If any is present, stop and report.
3. **AWS and GitHub token names may be present** (OD-76); record which, by name only, and never read them.
4. **The toolchain:** CPython 3.12.14 as `python3.12`; Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, first on PATH. Record `python3.12 --version`, `node --version`, `npm --version` and `docker --version`.
5. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`docs/operations/local-development.md`).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git merge-base --is-ancestor <START_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git merge-base --is-ancestor 43e794a5500e1ffdb12bfb2b2b2c0a9332c45ca2 HEAD && echo "PR58's merge present"
git diff --quiet 43e794a5500e1ffdb12bfb2b2b2c0a9332c45ca2 HEAD -- . ':!*.md' && echo "main's code"
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/api proofs packages apps .github docs/operations/ci-and-branch-policy.md docs/architecture docs/planning/sv4-chat-notifications.md   # must print nothing
grep -c '^## A2' docs/testing/evidence/2026-11-19-sv4-chat-notifications.md   # must print 0
ls proofs/postgres-ordering/glow_ordering_proof | grep -c '^chat_'          # must print 0
```

If a check fails, stop and report. The prompt is stale if its commit is not on the live branch, the live branch has changed an owned path or the brief since it, or A2's record or suite already exists.

**Then read, completely:**
- **The instructions:** root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`; `proofs/postgres-ordering/README.md`; `apps/mobile/AGENTS.md` (you change only generated files there); `docs/operations/ci-and-branch-policy.md`, the database proof jobs' paragraphs.
- **The brief,** revision 8: D1, D2, D8 to D15, "Owned paths", "Exclusions", "Acceptance checks" and "Review plan", and the revision history in its status line.
- **The Dev Manager's reports:** DM-96 (`docs/continuity/dev-manager/reviews/2026-11-19-dm-96-sv4-stage-a-brief.md`), sections 4 to 8 and 11, and section 14's words for D8 to D10; DM-98 (`2026-11-22-dm-98-sv4-a1-pre-merge-read.md`), sections 3 and 13 (AJ2).
- **The SV4 record's** "A0" (the job split, the decoy, the scans) and "A1", with their reviews' "Limits and deviations" and dispositions.
- **The carried-items file's** "Carried to SV4" and "Carried to the next change to the Foundation workflow (DM-97)".
- **The code you build on,** whole: `glow_chat/contact.py` (`send`), `reads.py` (`read_history`, `list_conversations`, `move_read_cursor`, `readable`, `_causes`), `delivery.py`; `glow_domain/chat.py`, `chat_reads.py`, `chat_projections.py` (`error_for`); SV1's `GlowActorAuthentication`; `glow_discovery/interaction_views.py`, `interaction_urls.py`, `contract.py` (`match_projection`) and the match read; the discovery suite's six modules and its offline tests (`proofs/postgres-ordering/tests/test_discovery_offline.py`), as the pattern a fifth suite follows; the Foundation workflow's discovery job and gate; `services/api/tests/test_chat_sealed_runtime.py` and `test_discovery_sealed_runtime.py`.

## 3. What to do

Build D8, D9, D10 and D15 as the brief says, with D14's reversals. In particular:

1. **The routes (D8).** Each refusal is the contract's `Error`, naming a code and never a value; nothing is cached; another method is 405; a body that is not the route's DTO, a query string or another content type is `invalid_request`. The send's refusals from either member's state or the end of contact (`match_not_active`, `blocked`, `account_not_active`, `profile_unavailable`, `consent_not_current`) answer one code, the same for each: record which code you chose and why, from the contract's codes. The history read takes its text reader from a factory only the proof's settings name; the views refuse to run without one. The views are `non_atomic_requests`, tested with `TransactionTestCase`, never `TestCase`. The list bounds its candidates (the top 200 by latest activity) before locking, then locks only those, in order, one statement per table. No `ChannelIntent` route.
2. **The contract (D9),** through `npm run generate` only: `ConversationSummary.state` gains `read_only` (with its count and marker); `MatchList` (`kind: match_list`), at most 200 `MatchProjection` entries served `active`, newest first; D4's and D6's sentences. The production catalog's `paths` stay empty. `apps/mobile/src/chat/rows.ts` treats every state but `open` as unavailable, so a `read_only` conversation shows as unavailable until AC3 (carried); you change no mobile file but the generated ones. Record whether `npm run check` in `apps/mobile` passes unchanged.
3. **The chat suite (D10),** on D2's pattern, in its own job `database-chat` ("Database proof checks (chat)", or the name you record): its own PostgreSQL, role, database `glow_chat_proof`, marker, decoy database, keys and secret scan, `dbshell`'s refusal under the chat settings, the decoy's marker refused, the reviewed migrations from zero, the suite, a refused second run, the upload only after the secret check passes, everything removed last. The gate needs the new job and requires its result. Its cases include every case D10 lists, and, from A1's review (D12, "Due at A2"), AR-12 (a like committed while a block waits; a match made after an unblock) and AR-13 (a publication of `chat.history` during a read).
4. **The seal (D15):** `test_chat_sealed_runtime.py` (or a sibling in its style) proves the runtime's settings, URL configuration and WSGI application import none of A2's modules, and that the database backend is the dummy one. If you change that file, take up A1's review's AR-14 and A1's stale lines 11 to 13 and 130 there (D12).
5. **The CI policy:** its database proof jobs' paragraph gains the chat job in the existing paragraphs' form, and nothing else changes. It is governing Markdown, read by the Dev Manager before A2 merges.

**Earlier tests** (the brief's D11, A2's bullet, from the manager's sweep at revision 8's commit). Each may change only by gaining A2's entry in a list it pins, every earlier assertion kept; record each, by file and test, with the entry added:
- `proofs/postgres-ordering/tests/test_discovery_offline.py`: `test_the_gate_requires_each_suites_job` (the gate's `needs` and its `jobs` tuple), and the per-job loop over `database-identity`, `database-profile` and `database-discovery` (lines 553 to 560), if the chat job's steps take the same form;
- each offline test that pins which settings module each `python -m glow_ordering_proof` command accepts and refuses, and `__main__.py`'s docstring;
- `services/api/tests/test_chat_sealed_runtime.py`;
- the contract's tests that read `ConversationSummary`'s states or the response kinds;
- `apps/mobile/src/chat/rows.test.ts` only if `npm run generate`'s output makes it fail (it should not): if it does, stop;
- **your own sweep:** before any change, at your prompt's commit, grep every suite's source and tests, the contract's tests and the API's tests for each list A2 extends (the suites, the database jobs, the gate's lists, the commands and settings modules, the routes, the contract's kinds and states, the case and plan counts), and record what you found. A test your sweep finds is handled the same way; any other change stops you.

**Follow-ups due at A2** (the brief's D12, "Due at A2"):
- **Taken by A2:**
  - **DM-98's AJ2:** at your prompt's commit, repeat the search for every writer of a match's `version` or `contact_version` (the A1 review's and DM-98's method: every assignment, `save`, queryset or manager write and SQL text naming either field, in the API's code), list each by file and line, and confirm A2 adds none. Record it.
  - **DM-97's Chromium margin** (you change `foundation.yml`): read the first attempt's duration of "Install Chromium for rendered fixture checks" in every run of record since A0. The record states 187 s (44463105633), 22 s (44562701307), 22 s (44601565801) and 203 s (44679608400); read 45001765683 and 45006396587 from their Mobile checks logs, and your own run's. If any passing first attempt took more than 480 s, or any was stopped by its time limit, apply the entry's rule (raise the Mobile job's and the first attempt's `timeout-minutes` so both attempts, the pause and the rendered checks fit, and state the margin; consider `sudo dpkg --configure -a` before the retry); otherwise record the durations and change nothing there.
  - **The chat suite's secret scan** reads every secret file its own job writes and no other (D2), written as the three are; its docstring names the chat job, not the shared one.
  - **The substring-pin limits** of A0's corrections (X3, X4, X5, X9, X14, X15, `per_schema`, N3; the carried-items file, A0's entry): name them in your record under "Substring pins, not semantics", for the chat job's steps too.
- **Taken only if you change the file for your own work** (otherwise they stay carried): the scans' and the eight module docstrings that still name the shared job (DM-97's AH3); `job_secret_files`' spelling (F7's D5); `row_locks.py`'s RN1 and RN2; `__main__.py`'s lines 20, 24 and 28; `reads.py`'s AR-5 and `chat_reads.py`'s N3; AR-7 to AR-10 and A1's stale lines; AR-11; SV1's identity-support docstring (DM-50). Record which you took.

**Reversals (D14).** Every new test comes with its reversal, recorded with its failing output; at least: a route that takes its actor from the body; a refusal that names a value; the send's five refusals answering different codes; a read served `open` where D5 makes it read-only, and served where `hidden` refuses it; a wrong member's route answering anything but `not_found`; the list locking before it bounds; a view run inside a caller's transaction; the chat job's decoy refusal and secret scan each removed; the gate without the chat job; the runtime importing an A2 module.

## 4. Checks, then the report

- **The trusted classifier,** from `main` (`43e794a`), extracted outside your checkout and run from it with `python3 -I` and full SHAs: `python3 -I <trusted copy>/change_scope.py --base 43e794a5500e1ffdb12bfb2b2b2c0a9332c45ca2 --head <your code head> --merge-base` prints `"full": true` (reason `behavior-or-empty`).
- **The diff:** `git diff --name-only <START_SHA> <your head>` lists only owned paths.
- **The API's checks,** in a clean environment, after `pip install --require-hashes -r requirements-dev.lock` in `services/api`: `GLOW_ENV=test python manage.py check`, `GLOW_ENV=test python manage.py test tests`, `makemigrations --check --dry-run`, `ruff check .`, `ruff format --check .` and `mypy`. Record the counts and skips before and after.
- **The proof's offline tests,** Ruff and mypy in `proofs/postgres-ordering`, from its lock; **the contract's** `npm run check` and its Python tests; **the mobile app's** `npm run check`, unchanged.
- **The generated outputs** equal `npm run generate`'s (`--check`).
- **Every reversal,** with its output, each file restored (`git status` clean).
- **The run of record,** on your last code commit: every job passed, the chat job among them, within its timeout, and the gate printed "Application checks passed".

**The record,** section "A2", on A1's pattern: this prompt's revision and commit; the start gate's and the environment check's results; what you built, by D-number; your sweep and each earlier test changed, with the entry added; the writer search (AJ2); the Chromium durations; the follow-ups taken; the new cases and tests; the reversals; the commands and results; any local database runs (iteration, not evidence); the run of record, with each job's duration; "Substring pins, not semantics"; every limit and deviation.

Your final message, which Nathan relays:
- your branch and heads (code and records);
- the record's path;
- the run of record's link and result, with the chat job's duration;
- what you built, by D-number;
- each earlier test changed, and the follow-ups taken;
- every stop, limit and deviation, and which GitHub route you used.
