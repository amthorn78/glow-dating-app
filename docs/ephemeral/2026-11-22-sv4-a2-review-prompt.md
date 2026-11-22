# SV4 A2 exact-head review prompt — chat's sealed routes, the match list and the chat suite, with a written threat model

- **Owner:** App Manager 13. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 22 November 2026.**
- **Durable brief:** [SV4 — the chat and notifications slice](../planning/sv4-chat-notifications.md), revision 9, "Review plan" (an exact-head code and security review of each stage, with a written threat model for A1 and A2).
- **Where the result goes:** the report Nathan relays. The manager records it in the SV4 record, "Exact-head review of A2", with a disposition for each finding (a correction before the merge, or carried), and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Fable 5.1 at max.** Effort score 3.71 (confidence 0.80); rung probabilities low 0.00, medium 0.00, high 0.04, extra high 0.20, max 0.74, ultracode 0.02. Model probabilities Fable 5.1 0.87, Opus 5.5 0.13, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.83). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.035, Fable 5.1 at extra high 0.174, Fable 5.1 at max 0.644, Fable 5.1 at ultracode 0.017, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.000, Opus 5.5 at high 0.005, Opus 5.5 at extra high 0.026, Opus 5.5 at max 0.096, Opus 5.5 at ultracode 0.003, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-22T12:51:01Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action. Dev Manager 7's pre-merge read of A2, with the brief's revisions 8 and 9 and the CI policy's change, follows this review (D-07).
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and none may be present. `amthorn78/glow-docs` is attached, read only; this review needs nothing from it (OD-74).
- **It runs alone** (OD-29), after PR59's run and Codex's review of the manager-branch head that holds this prompt (manager workflow, step 6). A full review of A2's code, not a delta review.
- **Deletion condition:** prune after A2's pull request (PR59) merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **exact-head review of SV4 A2**, chat's sealed routes, the match list and a fifth database suite, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one exact code head in full, with a written threat model. This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **SV4's brief,** revision 9 (`docs/planning/sv4-chat-notifications.md`). Its D8 to D10 and D15 set A2: chat's routes, each taking its actor from SV1's `GlowActorAuthentication` only (D8); the contract's additions, `ConversationSummary.state`'s `read_only` and `MatchList` (D9); a fifth database suite, the chat suite, on its own database in its own job (D10); and the seal, checked (D15). Much of it is the Dev Manager's words (DM-96, AG1 to AG21; `docs/continuity/dev-manager/reviews/2026-11-19-dm-96-sv4-stage-a-brief.md`). Revisions 8 and 9 are the manager's (A2's owned paths, D11's A2 bullet, D12's "Due at A2"; then SV3's database case `match.no_route_creates_a_match` and the CI policy's lines 5 and 23), for the Dev Manager's pre-merge read.
- **A1,** merged with PR58 at `43e794a`, built the rules A2 serves: D3 (a block retires the pair's earlier likes), D4 (a block ends a match as an unmatch does, so its direction is not served), D5 (the reads under OD-60's rule, through `chat.history`), D6 (the send's expected version is the match's) and D7 (the token code removed). A1's exact-head review's AR-12 and AR-13 were due at A2 (D12).
- **The implementation** (branch `claude/dazzling-hamilton-ocxuu3`; the SV4 record `docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`, section "A2"): its first code head, `e3f66a3`, failed run 45018516461 in Database proof checks (discovery), at SV3's `match.no_route_creates_a_match`, because A2's `GET api/v1/matches` is a route that case did not list. The session stopped at its stop rule; the manager kept the route where D9 puts it and widened A2's owned paths to that case (the brief's revision 9; the resume message; AM13-04). The second code head, `26aa7ca`, passed run of record 45022218979, all twelve jobs; the records head is `88d4ef3`. The manager verified it ("Manager verification of A2") and merged it into the manager branch at `0ff9c09`. PR59 carries it into `main`, which is at `43e794a`.

**The code head under review is `26aa7ca`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `26aa7ca` (the start gate checks this).

**Your scope:**
- **The code:** `git diff 43e794a5500e1ffdb12bfb2b2b2c0a9332c45ca2 26aa7ca2bd6d01d70900c62c1e59ecefef939e8e`, its 31 non-Markdown paths, read in full at `26aa7ca`, each changed module whole, beside its version at `43e794a` where it had one:
  - the API (`services/api/`): the new `glow_chat/contract.py`, `route_reads.py`, `views.py` and `urls.py`; `glow_discovery/interaction_views.py`, `interaction_urls.py`, `interactions.py` and `contract.py` (the match list); the new `tests/test_chat_routes_offline.py` and `tests/test_chat_routes_sealed_runtime.py`, and `tests/test_discovery_offline.py`;
  - the ordering proof (`proofs/postgres-ordering/`): the chat suite's six new modules (`glow_ordering_proof/chat_settings.py`, `chat_urls.py`, `chat_support.py`, `chat_cases.py`, `chat_suite.py`, `chat_scan.py`), `__main__.py`, `row_locks.py`, `interaction_cases.py` (the case `match.no_route_creates_a_match` only), the new `tests/test_chat_offline.py`, and `tests/test_discovery_offline.py`;
  - the contracts: `packages/contracts/production/gapp-api-v1.schema.json`, `flows-v1.json`, `openapi.json`, `packages/contracts/corpus/shared-v1.json`, `packages/contracts/tests/test_transition_contract.py`, and the three generated files in `apps/mobile/src/contracts/generated/`;
  - the workflow: `.github/workflows/foundation.yml` (the chat job and the gate).
- **What A2 serves unchanged,** read where A2 relies on it: `glow_chat/contact.py` (`OrmContactPersistence.send`), `reads.py` (`OrmConversationReads`: its `_list`, `_move`, `_lock_shared`, `_history`, `_blocked`, `_causes`, `readable` and `_entry`), `delivery.py`; `glow_domain/chat_projections.py` (`error_for`); SV1's `GlowActorAuthentication`; SV3's match read by ID.
- **The Markdown, as claims about the code:** `docs/operations/ci-and-branch-policy.md` (lines 5, 14 and 23, and the chat job's bullet), `docs/architecture/production-contracts.md`, `proofs/postgres-ordering/README.md`, and the record's section "A2" with "Manager verification of A2", whole.
- **The runs:** 45022218979 (the run of record), 45018516461 (the first run, failed, superseded), and PR59's run on `<PROMPT_SHA>` (event `pull_request`), once it has finished; Codex's review of that head.
- **Out of scope:** what A1's reviews covered and A2 does not change; notifications (Stage B); the mobile app, which A2 does not change beyond the three generated files. Report only where A2's change affects them.

**The threat model.** Write it in your report:
- **Assets:**
  - a conversation's history, its list entry and its read cursor, which only a member D5's rule admits may read, read only where D5 says;
  - a block's direction, and the fact that a block (not an unmatch) ended a match, which the member who did not block must not learn from any route's answer, refusal, code, body, timing, listing or count (D4);
  - the cause of a refused send, which no member may learn from its code or its body (D8: one code for every cause);
  - a match, which only reciprocal likes make: no route creates, restores or alters one (F09);
  - the database's locks and their order: the list bounds its candidates before it locks (D8; the P11 plan's C1 finding 4);
  - the seal: no route in the runtime's URL configuration, no path in the production catalog, no A2 module the runtime imports, no text reader the runtime names (D15);
  - the chat job's secrets (its keys, its marker, the decoy database's marker, the role's and the superuser's passwords), which no log, results file or upload may carry, and the decoy's marker, which the suite must refuse before any statement (D2);
  - the proofs' evidence: the chat suite's fifteen cases, and the discovery suite's cases, `match.no_route_creates_a_match` among them.
- **Actors:**
  - a member using any route, in every state the brief names (paused, incomplete, restricted, removed, suspended, deleted, consent withdrawn, blocked, unmatched, signed out, expired);
  - the other member of the pair, in each of those states, and the member who blocked;
  - a member with no relation to the match (a wrong member);
  - a request that is not its route's DTO: an extra field, a field naming an actor or a session, a query string, another content type or method;
  - a concurrent writer: a block, an unblock, an unmatch, a like, a pause, a restriction, a suspension, a consent withdrawal, a sign-out, or a publication of `chat.history`;
  - a caller's transaction around a view (`ATOMIC_REQUESTS`, a test case's block);
  - the CI runner, its logs and its artifacts;
  - a later change that depends on A2 (Stage B, AC1 to AC3, integration).
- **Entry points:** the four chat routes (`POST api/v1/chat/messages`, `GET api/v1/chat/conversations`, `POST api/v1/chat/history`, `POST api/v1/chat/read-cursor`) and `GET api/v1/matches`; `glow_chat.route_reads`' `RouteConversationReads`; the views' text reader factory (`GLOW_CHAT_TEXT_READER`); the contract and its generator; the chat suite's settings, URL configuration, cases, scan and runner; the chat job and the gate.

For each threat, give the code that stops it and the test or run that proves it. The focus:
1. **D8, the routes.** Each takes its actor from `GlowActorAuthentication` only, never the body; a body that is not its DTO, a query string or another content type is `invalid_request`; another method is 405; every refusal is the contract's `Error`, naming a code and never a value; `Cache-Control: no-store` on every answer; the reads' views refuse with `provider_unavailable` before any read when no text reader is named, and only the proof's settings name one. Say whether any route serves a reader D5 refuses or refuses one it admits, whether a wrong member's every route answers `not_found` and lists nothing, and whether the routes' one logger call can carry a value.
2. **The send's one code.** The five refusals the brief names (`match_not_active`, `blocked`, `account_not_active`, `profile_unavailable`, `consent_not_current`), with the missing forms `profile_missing` and `no_consent`, all answer `not_found`, with one body but for its request ID. Say whether the order of the checks, a refusal's status, body or headers, its timing, a replay, or any other route lets a member tell which cause stopped a send, or that the other member blocked; and whether the record's reasons for `not_found` over `forbidden` hold against `error_for`, the contract's wire rules and the mobile client. Say whether the send's answer, read in a statement after the send's transaction, can serve anything the send did not write.
3. **`route_reads.py` against `reads.py`.** A2 serves the list's bound and the `read_only` mark from a subclass of `OrmConversationReads` that overrides `_list` and `_move`, because `reads.py` stayed unchanged, so the list's session checks and per-conversation loop exist twice (the adapter's, which the ordering suite's read phase still runs, and the subclass's).
   - Say, condition by condition, whether the subclass's list applies exactly the adapter's rule: the session, the epoch, the match, a block either way, the other account's states, each cause through `chat.history`, the consent limit failing closed, and the one hidden refusal.
   - Say whether it takes the same locks in the same order, with the clock after them, and refuses a caller's transaction the same way.
   - Its bound takes the top 200 by latest activity in one statement with no lock, then `FOR SHARE` on only those, one statement per table, then the session and `chat.history`'s pointer. Say whether it can include a conversation the member may not read, or deadlock or cross with any writer.
   - Say whether `read_only` can differ between the list and the cursor's answer for one conversation.
   - The record names a consequence of the bound: a member with more than 200 active matches, some hidden, can be listed fewer than 200 although readable ones exist past the bound. Say whether that breaks D8 or D9 or is a limit to record.
   - Say whether the history read goes through the adapter unchanged, and whether the duplication is a defect now or a risk to carry.
4. **D8's transactions.** The four chat views are `non_atomic_requests`. D8 says they "are tested with `TransactionTestCase`, never `TestCase` (the P11 plan's R4)"; A2 wrote no `TransactionTestCase` class, and the record's "Limits and deviations" says how it meets the line instead (the chat suite's cases through Django's test client in autocommit, and `transactions.non_atomic_requests`). Say whether that meets R4's purpose, or whether the missing test is one an acceptance check rests on. The match list's view keeps SV3's pattern, not `non_atomic_requests`: say whether that is right for it.
5. **D9, the match list.** `GET api/v1/matches` (`MatchListView`; `interactions.read_matches`) serves at most 200 `MatchProjection` entries, the actor's own matches served `active`, newest first, under the actor's account row `FOR SHARE`.
   - Say whether it can serve another member's match, a match a block or an unmatch ended, more than 200 entries, or anything that tells a block from an unmatch.
   - It leaves out a match whose other member's account is `deletion_pending` or `deleted`, while SV3's match read by ID still serves that match `active`. Say which answer OD-60 H ("a deletion works as an unmatch") and D4 require, whether the difference tells a member anything, and whether it is a defect A2 introduced or an earlier one to carry.
   - Then `ConversationSummary.state`'s `read_only` (its count and marker kept; `closed` alone drops them), the schema, the corpus's 24 new cases, F09's registry entry, the generated outputs, and the production catalog's `paths`, which stay `{}`.
6. **F09, no route creates a match.** SV3's `match.no_route_creates_a_match` now lists `("api/v1/matches", "MatchListView")` and expects a `POST` at the matches path to answer 405 where it expected 404. Say whether the case still proves that no route at any path creates a match, that no request DTO names one, and that no match is written; and whether any route A2 adds can create, restore or alter a match or a like.
7. **D10, the chat suite and its job.**
   - Compare the chat job with the discovery job step by step: hash each step, list the identical, changed and new steps, and read every changed and new step whole.
   - Check each part: its own PostgreSQL from the pinned digest, role, database, marker, decoy (`glow_discovery_proof`, with its own marker) and keys; `dbshell`'s refusal under the chat settings; the decoy's marker refused with the relation counts unchanged; the migrations from zero and `makemigrations --check --dry-run`; the suite; the secret scan reading every secret file the job writes and no other; a second run refused with its rows unchanged; the upload only after the scan passes; everything removed last. The gate needs the chat job and requires its result.
   - Say whether any step can print a connection value or a secret, and whether the job fits its 30 minutes with margin.
   - Then check each of the fifteen cases against D10's list and A1's review's AR-12 and AR-13. Say whether any is vacuous, and whether a case that reaches a state by test data (an active block beside an active match, a withdrawal with the profile visible, an `incomplete` profile) proves what it names. Say whether the `hidden` setting published in the last two cases can reach any other case.
8. **D15, the seal and the boundary.** `test_chat_routes_sealed_runtime.py` is a sibling of `test_chat_sealed_runtime.py`, which is unchanged. It checks that the runtime's settings, URL configuration and WSGI application import none of A2's modules; that the backend is `django.db.backends.dummy`; that the runtime's routes are the three it had; and that it names no `GLOW_CHAT_TEXT_READER`. Say whether the test would catch an A2 module reached indirectly. A2 adds no provider call, credential, dependency or pin; HDE's ports and adapters are untouched (OD-80); `glow_api/` is unchanged.
9. **The earlier tests.**
   - Each changed earlier test gains only A2's entry, every earlier assertion kept (D11, A2's bullet), apart from the SV3 case's 404 to 405 (revision 9). These are the proof's gate, per-job, command and route tests (`test_discovery_offline.py`), the API's discovery route list, and the contract's frozen F09 entry.
   - The record also names the earlier tests found and left unchanged, with a reason for each: say whether each reason holds.
   - Say whether any new test is vacuous, and whether each reversal the record names (r01 to r22b) fails its test.
10. **The writer search** (DM-98's AJ2): say whether A2 adds or changes a writer of a match's `version` or `contact_version`, and whether `WRITERS` still holds every writer.
11. **The records:** check every claim in the CI policy's changed lines and its chat bullet, `production-contracts.md`'s new section and F09 row, the proof's README and the record's section "A2" against the code and the runs. The record names two stale lines outside A2's paths: `test_row_locks_offline.RunnerTests`' docstring ("Each of the four suites") and `docs/architecture/data-model.md`. For each, say whether it is a defect D-07 names or a record to carry, and whether any other such line exists.

**Re-run, at least,** in a scratch copy of `26aa7ca`, each package in a virtual environment installed from its own lock with `pip install --require-hashes`, under `env -i`:
- **The API:** `GLOW_ENV=test python manage.py check && GLOW_ENV=test python manage.py test tests`; `ruff check .`, `ruff format --check .` and `mypy`; `PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests`; `GLOW_ENV=test python manage.py makemigrations --check --dry-run`.
- **The ordering proof:** its offline tests, `ruff` and `mypy`.
- **The contracts:** after `npm ci --ignore-scripts` in `packages/contracts`, `npm run check` (`node scripts/generate.mjs --check`, then the corpus tests).
- **The mobile app:** after `npm ci --ignore-scripts` in `apps/mobile`, `npm run check`.
- **Reversals, offline, on copies,** each restored afterwards. For each, say which test fails, or that only a database case catches it:
  - a route takes its session from the body;
  - the send's block refusal answers `forbidden`;
  - `RouteConversationReads`' list locks every active match before it bounds;
  - the gate's `needs` without the chat job;
  - `glow_api/urls.py` imports `glow_chat.contract`;
  - `route_reads`' list serving a conversation the adapter's rule hides;
  - any other you doubt.
- **The database suites, informational:** the chat suite, and the discovery suite's `match.no_route_creates_a_match`, on a throwaway PostgreSQL under P06.DB's D4, if Docker allows.

**What comes after this review: the correction classes** (D-07; the manager workflow, step 6). Report every finding with its severity. A correction pass takes every blocking finding, and any should-fix finding that is:
- **a defect in application behaviour:** a route that serves or refuses against D5's rule; a refusal that names a cause or a value; a block told apart from an unmatch on any route; a list that serves a conversation the rule hides, or misses one it admits within the bound; a match list that serves a match it should not; a deadlock, a crossing or a lock taken before the bound;
- **a defect at a security boundary:** an actor taken from anything but SV1's authentication; a member who should be refused who is served; what a member learns of a block or of a refused send's cause; a route that creates, restores or alters a match; a credential, marker, password or key in a log, results file or upload; a seal crossed (a served route, a catalog path, an A2 module the runtime imports); HDE's boundary crossed;
- **a false claim that a decision or the merge would rest on** (D-07): a record, README, policy line, docstring or test name that claims more than the code, the tests or the runs show, where that claim is what a decision, an acceptance check or the merge reads.

A missing test is a correction only when the behaviour is at a security boundary or an acceptance check rests on it. Any other overclaim, and the reach of a static scan or a substring pin, is recorded and carried. For each finding, say whether it falls in one of these classes.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 13. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, thread resolutions, re-runs or workflow dispatches. Read GitHub with the GitHub tools where your session has them, otherwise with `gh api` REST `GET` calls, and say which you used.
  - **Scratch work goes in a copy outside the repository,** never the checkout (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
- **Network:**
  - PyPI and the npm registry, for hash-locked installs from the existing locks in a scratch copy;
  - Docker Hub, only to pull the PostgreSQL image the workflow pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`);
  - GitHub, read only, to read the runs, PR59 and Codex's review.

  A page you cannot reach is named as unread, never filled from memory.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions): a throwaway PostgreSQL in Docker, from that image, on loopback only; a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present; removed afterwards. Migrations reach that database only through the proof's own commands; never run `manage.py migrate` yourself.
- **Never:**
  - dump the environment, or print a credential, password, marker, token, session key or key;
  - read, print or use the value of any `AWS_*` variable (section 1);
  - call any provider or HDE;
  - connect to any database but a throwaway one you started under D4's conditions, HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:** `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_|RAILWAY_)'` prints names only. If any is present, stop and report.
3. **AWS names may be present** (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_CA_BUNDLE`); the cloud container sets them (OD-76). `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below except your GitHub reads runs without them.
5. **The toolchain:** CPython 3.12.14 as `python3.12`; Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`; Docker if present. Record their versions.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (for `npm ci`, the proxy's `HTTPS_PROXY` and `NODE_EXTRA_CA_CERTS` if it needs them, as A2's record says). No `AWS_*` name passes.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, 43e794a5500e1ffdb12bfb2b2b2c0a9332c45ca2
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 26aa7ca2bd6d01d70900c62c1e59ecefef939e8e HEAD -- . ':!*.md' && echo "the code head under review"
git diff --quiet 26aa7ca2bd6d01d70900c62c1e59ecefef939e8e origin/claude/magical-wozniak-yfmmx2 -- . ':!*.md' && echo "no code on the live branch after 26aa7ca"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-19-sv4-chat-notifications.md | grep -c -E '^#+ Exact-head review of A2'   # must print 0
```

If any check fails, stop and report. The prompt is stale if its commit is not on the live branch, a non-Markdown path changed there after `26aa7ca`, or this review is already recorded.

**Classify the change** as root `AGENTS.md` requires, with the trusted base policy outside the candidate tree:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
```

Run it from the checkout (the policy file outside it). Expected: `"full": true`. Anything else: stop and report.

**Then read, completely, at `HEAD`:**
- root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`; `proofs/postgres-ordering/README.md`; `docs/operations/ci-and-branch-policy.md`, the database proof jobs' section;
- the brief, revision 9: D1, D2, D4, D5, D8 to D15, "Owned paths" (A2), "Exclusions", "Acceptance checks", "Review plan", and the revision history in its status line;
- DM-96's report, sections 3, 5, 6, 9, 11, 12 and 14;
- A2's prompt (`docs/ephemeral/2026-11-22-sv4-a2-routes-prompt.md`), its "Earlier tests" above all, and its resume message (`docs/ephemeral/2026-11-22-sv4-a2-resume-message.md`);
- A1's exact-head review's AR-12 and AR-13 (the record's "Exact-head review of A1");
- the record's section "A2", whole, with "Manager verification of A2";
- every file in the code diff, whole, beside its version at `43e794a`.

**The runs,** read from GitHub: 45022218979, 45018516461, and PR59's run on `<PROMPT_SHA>` if it has finished: every job's conclusion and duration, and the gate's line; and Codex's review of `<PROMPT_SHA>`.

## 3. What to do

1. Write the threat model, then review the change against the focus, item by item.
2. In a scratch copy of `26aa7ca`: re-run the checks and the reversals above, and any you doubt; run the database cases locally under D4 if you can, informational.
3. For each finding: its severity (blocking, should fix, nit), its file and line, the evidence, and whether it falls in a correction class.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- the threat model, each threat with its stopping code and its test or run;
- the focus, item by item, with your verdict on each;
- every finding, with its severity, file and line, evidence and correction class;
- the checks and reversals you re-ran, each with its exact result, and any local run;
- the runs and Codex's review as you read them, and which GitHub route you used;
- your verdict: **approve**, **approve with nits** or **changes requested**;
- what you did not read or run, and why.
