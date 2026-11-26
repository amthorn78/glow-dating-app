# SV4 A2-C1 prompt — the correction: the send's and the reads' one code, the list's tests, the routes' negotiation

- **Owner:** App Manager 13. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 26 November 2026.**
- **Durable brief:** [SV4 — the chat and notifications slice](../planning/sv4-chat-notifications.md), revision 10 (D8's send bullet by DM-99's AK8; "Owned paths", A2-C1). **The findings:** the SV4 record's "Exact-head review of A2" (`docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`), with its disposition and "Dev Manager 7's DM-99". **The decision:** [DM-99](../continuity/dev-manager/reviews/2026-11-26-dm-99-sv4-a2-c1-design.md) (Dev Manager 7, `c2ae138`), AK1 to AK11.
- **Where the result goes:**
  - the session's changes to the owned paths below, and its section "A2-C1" in the same record, on its own branch;
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification to the record, and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.16 (confidence 0.83); rung probabilities low 0.00, medium 0.06, high 0.74, extra high 0.20, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.02, Opus 5.5 0.97, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.96). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.001, Fable 5.1 at high 0.015, Fable 5.1 at extra high 0.004, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.058, Opus 5.5 at high 0.718, Opus 5.5 at extra high 0.194, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.001, Sonnet 5.5 at high 0.007, Sonnet 5.5 at extra high 0.002, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-26T05:58:12Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. DM-99 decided the design; this prompt authorizes no credential use and no live provider action (the charter, "Read before it takes effect"). Under D-07 the correction goes on the list for the Dev Manager's pre-merge read of A2.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and none may be present. `amthorn78/glow-docs` is attached, read only; this work needs nothing from it (OD-74).
- **It runs alone** (OD-29). Then, in order: the manager's verification; PR59's run and Codex's review of its new head; a delta review of A2-C1 with DM-99's focus (its section 6); the Dev Manager's pre-merge read of A2; the merge.
- **Deletion condition:** prune after A2's pull request (PR59) merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch (AM11-21).

---

You are the **correction session A2-C1** for SV4 A2, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **A2** (code head `26aa7ca`; the record's section "A2") built chat's sealed routes (D8), `read_only` and `MatchList` (D9), the chat suite in its own job (D10) and the seal test (D15). Run of record 45022218979 passed all twelve jobs. PR59 carries it into `main`, which is at `43e794a`.
- **A2's exact-head review** (the record's "Exact-head review of A2") found the routes right on every point but the send's one code, and asked for changes:
  - **A2R-1 (Codex's P2, comment 4658183908; confirmed on a database).** With an active match at version 1, a send naming a wrong `expected_version` answers 404 `not_found` for the other member's suspension and 409 `stale_version` for a pause, a restriction or a withdrawn consent, which the reads serve alike. `OrmContactPersistence.send` (`services/api/glow_chat/contact.py`) checks the match (line 521), the session's account (526), both accounts (528), the session's state, expiry and epoch (530 to 535), a block (544), the version (546), and only then the profiles and consents (549); `send_error` (`glow_chat/contract.py`, 169 to 170) maps the version's refusal to `stale_version`.
  - **A2R-2 (Codex's second P2, comment 4703261810).** A session that ends after SV1's authentication and before the send's session lock answers 401 for no cause or a pause, and 404 for a suspension or an unmatch.
  - **A2R-3.** With the served list's block check, or its session and own-account checks, removed (`glow_chat/route_reads.py`, 156 to 169 and 180), every offline test and every database case still passes.
  - **A2R-4 (low).** `?format=xml` (404 `{"detail":"Not found."}`) and `Accept: text/html` (406) are answered by the framework before authentication, outside the contract's `Error`, with no `Cache-Control`.
  - **A2R-5 and A2R-8 (nits taken here).** `views.py` line 36 says "Its tests are `TransactionTestCase`s", and none exists. In `chat_cases.py` (183 to 188, 330 to 333) the no-token challenge header is checked on the refused-token reply, and case 3 moves the read cursor for one member where D10 says both. `chat_support.py`'s `match_version` (213 to 214) returns 1 when the match read fails.
- **DM-99** (Dev Manager 7; the record's "Dev Manager 7's DM-99") decided the fix's place: **A2's route layer, not `contact.py`**, for the send and, by AK1, for the history read and the read cursor, which have the same split for a session ended mid-request (`reads.py`'s `_authorize`). It set AK1 to AK11; AK3 to AK7 are words you apply as given (section 3, item 7). AK8 is already in the brief's D8.
- **The rest** of the review's findings are carried or recorded (the disposition table): you do not take them up.

**This correction changes the routes' refusal mapping, the five routes' content negotiation, their tests, the chat suite's cases, and the words DM-99 gives.** `contact.py`, `reads.py`, `route_reads.py`, every other module of `glow_chat` and `glow_domain`, SV2's and SV3's other views, the workflow, the contract's schema and registry, the generated outputs and every other suite stay exactly as they are.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 13. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only these paths (the brief's revision 10, "Owned paths", A2-C1):
    - `services/api/glow_chat/contract.py`: `send_error`, `read_error`, their docstrings, and the module docstring's sentence AK7 replaces, only;
    - `services/api/glow_chat/views.py`: the four chat views' content negotiation; the history read's and the read cursor's refusal mapping, if it lives there; the module docstring's sentence on `TransactionTestCase` (A2R-5), only;
    - `services/api/glow_discovery/interaction_views.py`: `MatchListView`'s content negotiation, only;
    - `services/api/tests/test_chat_routes_offline.py`;
    - `proofs/postgres-ordering/glow_ordering_proof/chat_cases.py`; `chat_support.py` (`match_version`'s fallback, only); `proofs/postgres-ordering/tests/test_chat_offline.py` (the case count's pin and the plan tests, only as the new cases need);
    - `proofs/postgres-ordering/README.md` (the chat suite's case count, only);
    - `docs/architecture/production-contracts.md` (AK3 to AK6, as given, only);
    - the record, section "A2-C1" only;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: use the GitHub tools where your session has them, otherwise `gh api` REST `GET` calls, and say in the report which you used. No pull request, comment, review, thread resolution, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule.** Stop and report, with no further change, if any of these holds:
  - **a path:** the work needs any path or passage outside the list above: `contact.py`, `reads.py`, `route_reads.py`, `glow_domain/chat_projections.py`, SV1's authentication, SV2's or SV3's other views, the workflow, the contract's JSON, a generated file, another suite, the CI policy;
  - **the decision:** the fix cannot give one status, code and body for every stopped cause without changing `send`'s or `_authorize`'s order, or a reason not named in section 3 would need a code other than the one DM-99 decided;
  - **an earlier test:** a test or case not named in section 3, items 6 and 8, would have to change, or a named one would change beyond what those items say;
  - **the words:** an old passage of AK3 to AK7 is not found exactly once at `<START_SHA>`;
  - **a proof or a reversal:** a result in section 3 differs from the one it names.
  - In each case, report it; do not narrow this prompt's words to pass it. A reversal's temporary edit is allowed, and must be undone.
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished. A newer push cancels the earlier run's application jobs, and the run of record is lost. Push your records commit only after the run of record has finished. The workflow runs on pushes to `claude/**` and `ccr-**`; if your branch is named otherwise, say so in the report, since no run starts.
  - **If GitHub never starts the run** (it stays `queued` with no jobs for 30 minutes), do not re-run it, dispatch it, push an empty commit, or ask anyone to re-run it (OD-58). Record it, push your records commit, and report.
  - **If the run fails,** stop and report the failing job and its log lines. Do not re-run it.
- **Network:** PyPI, for `pip install --require-hashes` from the existing locks; Docker Hub, only to pull the PostgreSQL image the workflow pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`); GitHub, read only. The environment does not enforce this; you do.
- **Local database runs** are iteration, not evidence, and are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions): a throwaway PostgreSQL in Docker, from that image, on loopback only; generated passwords and markers, never printed; none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name in any process environment; removed afterwards. Migrations reach that database only through the proof's own commands; never run `manage.py migrate` yourself. The evidence of record is CI's run.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, password, marker, token or key;
  - read, print or use the value of any `AWS_*` variable, or name one in a command (section 1);
  - call any provider or HDE; connect to any database but a throwaway one you started under D4's conditions, HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script;
  - weaken or delete a test to make the suite pass.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:** `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_|RAILWAY_)'` prints names only. If any is present, stop and report.
3. **AWS names may be present** (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_CA_BUNDLE`); the cloud container sets them (OD-76). `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values, and pass none to a command.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them.
5. **The toolchain:** CPython 3.12.14 as `python3.12`; Docker if present. Record their versions.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API, as the workflow sets it). No `AWS_*` name passes.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git merge-base --is-ancestor <START_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 26aa7ca2bd6d01d70900c62c1e59ecefef939e8e HEAD -- . ':!*.md' && echo "A2's code head"
git diff --quiet 26aa7ca2bd6d01d70900c62c1e59ecefef939e8e origin/claude/magical-wozniak-yfmmx2 -- . ':!*.md' && echo "no code on the live branch after 26aa7ca"
grep -c -E '^#+ Exact-head review of A2' docs/testing/evidence/2026-11-19-sv4-chat-notifications.md   # must print 1
grep -c -E '^#+ A2-C1' docs/testing/evidence/2026-11-19-sv4-chat-notifications.md                     # must print 0
```

If a check fails, stop and report. The prompt is stale if its commit is not on the live branch, a non-Markdown path changed there after `26aa7ca`, or an A2-C1 section already exists.

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`; `proofs/postgres-ordering/README.md`;
- the record's sections "A2" (its "Limits and deviations" above all), "Manager verification of A2", "Codex on PR59", "Exact-head review of A2" (with its probe table and disposition) and "Dev Manager 7's DM-99", whole;
- DM-99's report (`docs/continuity/dev-manager/reviews/2026-11-26-dm-99-sv4-a2-c1-design.md`), sections 3, 4, 6 and 9, whole;
- the brief, revision 10: D5, D8 (with AK8's sentence), D10, "Owned paths" (A2-C1), "Acceptance checks";
- `services/api/glow_chat/contract.py`, `views.py` and `route_reads.py`, whole; `contact.py`'s `send` and `_lock`; `reads.py`'s `_authorize` and its three callers; `glow_domain/chat_projections.py`'s `error_for`;
- `services/api/glow_discovery/interaction_views.py`'s `MatchListView` and the base it uses;
- `services/api/tests/test_chat_routes_offline.py`, whole;
- `proofs/postgres-ordering/glow_ordering_proof/chat_cases.py` and `chat_support.py`, whole, and `proofs/postgres-ordering/tests/test_chat_offline.py`'s `ChatPlanTests`.

## 3. What to do

1. **The send's one code (A2R-1, A2R-2; DM-99 item 1, option (a)).** In `send_error`:
   - `stale_contact_version` answers the one code, `not_found` (404, not retryable), the same body as every stopped cause;
   - so do the session reasons `send` raises once it holds its locks: `session_changed`, `session_not_valid`, `session_expired` and `session_epoch_stale` (`contact.py`, 524 to 535);
   - `session_missing` (the read before the locks), the `_lock` helpers' `<table>_missing` reasons (`accountsession_missing` among them) and SV1's door keep `unauthenticated`; `idempotency_conflict`, `state_conflict` and the other codes are unchanged;
   - `send_error`'s docstring states the mapping and why (any other answer for either would tell causes apart).
2. **The reads' one code (AK1).** For the history read and the read cursor only, the session reasons `_authorize` raises once it holds its locks (`session_changed`, `session_not_valid`, `session_expired`, `session_epoch_stale`) answer `not_found`, the code a hidden conversation answers. The conversation list, `session_missing`, the `<table>_missing` reasons and SV1's door keep `unauthenticated`. `read_error`'s docstring states the mapping. `error_for` and `glow_domain` stay as they are; the mapping lives in A2's route layer.
3. **The proof that the mapping is complete (AK2).**
   - **Offline:** a test in `test_chat_routes_offline.py` that reads, from the source of `OrmContactPersistence.send` and of `_authorize`, every reason each can raise after its first lock (the `chat.` constants and the `_lock` helpers' `<table>_missing` forms), and pins each one's served code and status for its route. A reason added later fails it until it is mapped. Say how it finds the reasons and what it would miss.
   - **Database cases** in the chat suite: the send under every row of the review's probe table (no cause; the other member suspended; the other's pause, the own pause, the other's restriction, the other's consent withdrawn; an unmatch, a block, the other's deletion), each with the current version, a wrong version (0 and 7), and a session ended once the send holds its locks. Every stopped row answers one status, code and body (`not_found`, 404); the row with no cause answers 200 at the current version and `not_found` for the other two. The history read and the read cursor, with a session ended once they hold their locks, answer the same under a cause published `hidden` as under an unmatch.
   - Use the suite's existing hold points and observed waits, as `ar12.*` and `ar13.*` do. Cases that publish a cause `hidden` run last, with the two that do so today (`chat.history` cannot be made more readable again under the launch consent version); keep `test_the_cases_that_publish_hidden_run_last` true.
4. **The list's checks, proven (A2R-3).** Database cases that fail with each of the served list's checks removed: the block check (a seeded active block beside an active match, as test data, is not listed); the session's checks (a list whose session ends after its account locks is refused `unauthenticated`); the own-account check. If the own account's check can be reached only inside a race with SV1's door, build the race the same way, and say so.
5. **The routes' negotiation (A2R-4; DM-99 item 2).** The four chat views and `MatchListView` take a content negotiation that always chooses the JSON renderer and reads neither `Accept` nor the `format` override, set on those five views only. Then `?format=xml` meets the routes' own query-string refusal (`invalid_request`, 400, `no-store`), and `Accept: text/html` is answered as any other request. Offline tests show both on all five routes, and that SV3's other views in `interaction_views.py` keep their negotiation.
6. **The nits taken (A2R-5, A2R-8; AK11).**
   - `views.py`'s module docstring: replace "Its tests are ``TransactionTestCase``s." with what the record says the tests are (the chat suite's cases through Django's test client in autocommit, and `transactions.non_atomic_requests`).
   - `reads.history_list_and_cursor_for_both` moves the read cursor for both members, and each member's unread count is unchanged by the other's move.
   - The no-token challenge header (`WWW-Authenticate: Bearer`) is checked on the no-token reply in `routes.refuse_what_is_not_their_dto`.
   - `chat_support.match_version` fails the case when the match read fails, instead of returning 1.
7. **DM-99's words, as given.** Apply each pair by script: find the old passage exactly once at `<START_SHA>`, replace it, and check the new passage then occurs exactly once. Record the check. AK7's lines are 93 characters at most; keep them as given.

**AK3** (`docs/architecture/production-contracts.md`, the send's version and session). Replace:

```text
the same key with another intent is `idempotency_conflict`; another version is `stale_version`.
```

with:

```text
the same key with another intent is `idempotency_conflict`; a version other than the match's answers `not_found`, as does a session the send finds ended once it holds its locks, since the send checks part of either member's state after the version and the session (SV4 A2's exact-head review, A2R-1 and A2R-2; DM-99); a session that is missing when the send reads or locks it is `unauthenticated`.
```

**AK4** (`docs/architecture/production-contracts.md`, the send's bullet's last sentence). Replace:

```text
Since the send checks the match's state before the version, a retry after contact has ended answers `not_found`, never `stale_version`.
```

with:

```text
So the send never answers `stale_version`, and a retry after contact has ended answers `not_found`.
```

**AK5** (`docs/architecture/production-contracts.md`, the history read). Replace:

```text
- **`POST api/v1/chat/history`**: `MessagePageRequest`, answering `MessagePage`, under the read rule; a cursor that cannot be read, or one of another match, is `stale_version`.
```

with:

```text
- **`POST api/v1/chat/history`**: `MessagePageRequest`, answering `MessagePage`, under the read rule; a cursor that cannot be read, or one of another match, is `stale_version`; a session the read finds ended once it holds its locks answers `not_found`, as a hidden conversation does, since the read rule checks the block and the causes after the session (DM-99).
```

**AK6** (`docs/architecture/production-contracts.md`, the read cursor). Replace:

```text
- **`POST api/v1/chat/read-cursor`**: `ReadCursorIntent`, answering `ConversationSummary`, `open` or `read_only`.
```

with:

```text
- **`POST api/v1/chat/read-cursor`**: `ReadCursorIntent`, answering `ConversationSummary`, `open` or `read_only`; a session it finds ended once it holds its locks answers `not_found`, as for the history (DM-99).
```

**AK7** (`services/api/glow_chat/contract.py`, the module docstring's sentence on the send's other answers). Replace:

```text
"unavailable". A stale expected version is ``stale_version`` (checked after the state, so an
ended contact answers ``not_found`` whatever version is sent; D6), the same key with another
intent ``idempotency_conflict``, and the member's own session ``unauthenticated``.
```

with:

```text
"unavailable". A version other than the match's answers ``not_found`` too, and so does a
session the send finds ended once it holds its locks: the send checks part of either member's
state after the version and the session (A2R-1, A2R-2; DM-99), so another answer for either
would tell causes apart. The same key with another intent is ``idempotency_conflict``, and a
session that is missing when the send reads or locks it is ``unauthenticated``.
```

8. **The earlier pins that change,** each only to the answer DM-99 decided, every other assertion kept:
   - `SendRefusalTests`' mapping table (`test_chat_routes_offline.py`, lines 238 to 244): `stale_contact_version` and the four session reasons inside the send now `not_found`; `session_missing` stays `unauthenticated`;
   - `SendRefusalTests.test_the_other_refusals_keep_their_codes` and `RouteTests.test_the_sends_five_refusals_answer_one_code` (line 629, the send's stale version; line 631, the send's `session_not_valid`);
   - `RouteTests`' reads' session pins (line 642, `session_expired`, and its neighbours): `not_found` for the history read and the cursor, `unauthenticated` for the list;
   - the case `send.replay_conflict_and_version` (versions 0 and 2): `not_found`, writing nothing, as before;
   - `CASE_COUNT`, `ChatPlanTests.test_the_case_count_is_pinned` and the README's "15 cases", if you add cases.
   No other earlier test changes. `ReciprocalWriterTests`' digests hold (`contact.py` unchanged), and `test_chat_reads.py`'s `error_for` table stays as it is.

**Reversals,** each on a copy, restored afterwards; each fails the test or case named (record its output):
- (r1) `send_error` answering `stale_version` for `stale_contact_version` again: the offline mapping test and the wrong-version case;
- (r2) one of the send's four in-lock session reasons answered `unauthenticated` again: the offline mapping test and the mid-request session case;
- (r3) the history read's in-lock session reasons answered `unauthenticated` again: the offline test and the reads' mid-request case;
- (r4) a new `raise _Refused(chat.<new reason>)` added after the locks in a scratch copy of `send`: the offline mapping test;
- (r5, r6, r7) the served list's block check, its session checks, its own-account check, each removed: a database case each;
- (r8) the negotiation removed from one chat view and from `MatchListView`: the negotiation tests;
- (r9) case 3's second member's cursor move removed: the case, or say that nothing fails.

## 4. Checks, then the report

- **The trusted classifier,** from `main` (`43e794a`), extracted outside your checkout and run with `python3 -I` and full SHAs: `python3 -I <trusted copy>/change_scope.py --base 43e794a5500e1ffdb12bfb2b2b2c0a9332c45ca2 --head <your code head> --merge-base` prints `"full": true` (reason `behavior-or-empty`).
- **The diff:** `git diff --name-only <START_SHA> <your head>` lists only the owned paths. `git diff <START_SHA> <your head> -- services/api/glow_chat/contact.py services/api/glow_chat/reads.py services/api/glow_chat/route_reads.py services/api/glow_domain/` prints nothing. In `interaction_views.py` only `MatchListView` changes.
- **The API's checks,** in a clean environment, after `pip install --require-hashes -r requirements-dev.lock` in `services/api`: `GLOW_ENV=test python manage.py check`, `GLOW_ENV=test python manage.py test tests`, `ruff check .`, `ruff format --check .`, `mypy`, the contract's Python tests (`PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests`) and `GLOW_ENV=test python manage.py makemigrations --check --dry-run` pass. Record the counts and skips before and after.
- **The ordering proof's checks,** from its own lock: its offline tests, `ruff` and `mypy`. Record the counts before and after.
- **The chat suite,** locally under D4 if Docker allows (iteration), and in the run of record: every case passes, both scans clean, `ROW LOCKS (D14): PASS`, `CHAT VERDICT: PASS`.
- **Every reversal** above, with its output, every file restored byte for byte (`git status` clean but for your changes).
- **The run of record,** on your last code commit: every job passed, Database proof checks (chat) among them, and the gate printed "Application checks passed".

**The record,** section "A2-C1":
- this prompt's revision and commit; the start gate's and the environment check's results;
- each change, by item, with each earlier pin's old and new answer;
- the review's probe table, re-run as cases, with every row's three answers;
- DM-99's words: each pair found once and applied once;
- the reversals with their outputs; the counts; the local runs (iteration) and the run of record;
- what A2-C1 changes in section "A2": the send's one code now holds for every version and for a session ended mid-request, and the reads' one code for a session ended mid-request; the list's checks are proven.

Your final message, which Nathan relays:
- your branch and head;
- the record's path;
- the run of record's link and result;
- what you changed, by item;
- every proof's and reversal's result;
- every stop, limit and deviation.
