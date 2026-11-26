# SV4 A2-C1 delta review prompt — the send's and the reads' one code, the list's checks, the routes' negotiation

- **Owner:** App Manager 13. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 26 November 2026.**
- **Durable brief:** [SV4 — the chat and notifications slice](../planning/sv4-chat-notifications.md), revision 10. **The findings it checks:** A2R-1 to A2R-5 and A2R-8, in the SV4 record's "Exact-head review of A2", with [DM-99](../continuity/dev-manager/reviews/2026-11-26-dm-99-sv4-a2-c1-design.md)'s decision and its five-point focus for this review (its section 6), and Codex's three P2 threads on PR59.
- **Where the result goes:** the report Nathan relays. The manager records it in the SV4 record, "Delta review of A2-C1", with a disposition for each finding, and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 2.52 (confidence 0.65); rung probabilities low 0.00, medium 0.01, high 0.49, extra high 0.48, max 0.02, ultracode 0.00. Model probabilities Fable 5.1 0.07, Opus 5.5 0.93, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.91). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.001, Fable 5.1 at high 0.034, Fable 5.1 at extra high 0.034, Fable 5.1 at max 0.001, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.009, Opus 5.5 at high 0.456, Opus 5.5 at extra high 0.446, Opus 5.5 at max 0.019, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Flags: boundary between extra high and high. Sent 2026-11-26T09:19:59Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action. Dev Manager 7's pre-merge read of A2 follows it (D-07).
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and none may be present. `amthorn78/glow-docs` is attached, read only; this review needs nothing from it (OD-74).
- **It runs alone** (OD-29), after PR59's run and Codex's review of the manager-branch head that holds this prompt (the manager workflow, "A small correction gets a delta re-review"; DM-99 confirmed a delta review for A2-C1).
- **Deletion condition:** prune after A2's pull request (PR59) merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch.

---

You are the **delta review of SV4 A2-C1**, a correction of A2's route layer at a security boundary (what a member learns of why a send or a read was refused), for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **A2** (code head `26aa7ca`; the record `docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`, section "A2") built chat's sealed routes, the match list and the chat suite. PR59 carries it into `main`, which is at `43e794a`.
- **A2's exact-head review** (the record's "Exact-head review of A2") found the routes right on every point but the send's one code:
  - **A2R-1:** a send naming a wrong version answered 404 for the other member's suspension and 409 `stale_version` for a pause, a restriction or a withdrawn consent, because `OrmContactPersistence.send` checks the version before the profiles and consents (Codex's P2, comment 4658183908);
  - **A2R-2:** a session ended after SV1's door and before the send's session lock answered 401 or 404 by cause (Codex's second P2, comment 4703261810);
  - **A2R-3:** nothing proved the served list's block, session and own-account checks;
  - **A2R-4:** `?format=xml` and `Accept: text/html` were answered by the framework, outside the contract's `Error` (Codex's third P2, comment 4704969737, on `f435cef`);
  - the nits A2R-5 and A2R-8.
- **DM-99** (Dev Manager 7) decided the fix: both A2R-1 and A2R-2 in A2's route layer, the history read and the read cursor included (AK1), with AK2's proof, AK3 to AK8's words, A2R-4's negotiation on A2's five routes and AK11. It named this review's focus (its section 6).
- **A2-C1** (branch `claude/affectionate-sagan-r916ba`, code head `ddb1386`, records head `2201c2d`; the record's "A2-C1"; run of record 45778164243, all twelve jobs, the chat suite 18/18) made the fix. It stopped once, on `transactions.non_atomic_requests`, and resumed under the manager's resume message, which named that case for one change. The manager verified it ("Manager verification of A2-C1") and merged it into the manager branch at `356ee8f`.

**The code head under review is `ddb1386ac04c84195189bfd73fc9f21ba65225bf`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to it (the start gate checks this).

**Your scope:**
- **The correction:** `git diff 4a72036b4bdca1fa258184ef48bcb9bb257714fb ddb1386ac04c84195189bfd73fc9f21ba65225bf`, nine paths. Read every path it touches as it stands at the head, not the diff alone (the manager workflow's delta review):
  - `services/api/glow_chat/contract.py` and `views.py`, whole;
  - `services/api/glow_discovery/interaction_views.py`'s `MatchListView` and the base it uses;
  - `services/api/tests/test_chat_routes_offline.py`, whole;
  - `proofs/postgres-ordering/glow_ordering_proof/chat_cases.py` and `chat_support.py`, whole; `proofs/postgres-ordering/tests/test_chat_offline.py`'s plan tests;
  - `docs/architecture/production-contracts.md`'s chat section and `proofs/postgres-ordering/README.md`'s chat count.
- **Against:** `services/api/glow_chat/contact.py`'s `send` and `_lock`, `reads.py`'s `_authorize` and its callers, `route_reads.py`'s list, `glow_domain/chat_projections.py`'s `error_for` (all unchanged), SV1's `GlowActorAuthentication`, and SV3's other views.
- **The Markdown, as claims about the code:** the record's sections "A2-C1" and "Manager verification of A2-C1", whole; the brief's D8 (AK8's sentence).
- **The runs:** 45778164243 (the run of record) and PR59's run on `<PROMPT_SHA>` (event `pull_request`), once it has finished; Codex's review of that head and its three threads on PR59.
- **Out of scope:** what A2's exact-head review covered and A2-C1 does not change, and what the record carries (the review's disposition table and DM-99's carries: A2R-6, A2R-7, A2R-10 to A2R-13, the review's limits).

**The focus** (DM-99, section 6, with the security focus kept):
1. **The mapping is complete.** Read, from the source as it stands, every reason `send` and `_authorize` can raise after their locks, their helpers included, and say whether each answers as DM-99 decided: `not_found` for the send's stopped causes, its version and its four in-lock session reasons; `not_found` for the four in-lock session reasons on the history read and the read cursor; `unauthenticated` for `session_missing`, `accountsession_missing`, the list's session reasons and SV1's door, which is unchanged. Say whether `contact.py`, `reads.py` and `route_reads.py`'s rule are unchanged (equal without docstrings), so `ReciprocalWriterTests`' digests hold. Then the offline test `MappingCompletenessTests`: say what it finds, whether a reason added later fails it, and whether its stated reach (its docstring; the record's item 3) is all it misses.
2. **The review's probe table, re-run.** Every row, with the current version, a wrong version and a session ended once the send holds its locks, gives one status, code and body for every stopped row. The history read and the read cursor answer alike, with a session ended once they hold their locks, under a cause published `hidden` and under an unmatch. Read the two new cases and say whether each proves what it names: whether its session is truly ended while the route waits at its own lock (the hold point and the observed wait), and whether any row could pass with the route's answer unchanged. Say whether anything else a member controls still splits the causes (a replay, an idempotency conflict, a body the route refuses, timing).
3. **A2R-3:** each of the list's three checks, removed, fails a database case. Say whether the own-account check's test data (an account set `suspended` with its session left valid) reaches the code the check guards, and whether the record's account of why no real writer reaches it holds.
4. **A2R-4:** `?format=xml` and `Accept: text/html` reach the routes' own checks on the five routes, answered as the contract's `Error` with `no-store` where they refuse, and SV2's and SV3's other views are unchanged. Say whether `MatchListView`'s class-level imports (which make `DefaultContentNegotiation` and `JSONRenderer` attributes of the view) change anything served.
5. **AK3 to AK8 are as given,** and each earlier pin and case changed only as decided: the prompt's items 6 and 8, the resume message's change to `transactions.non_atomic_requests` (the send's body built before `ATOMIC_REQUESTS` is turned on, every expectation kept), and the route script's `answer()` reading `Cache-Control` with `.get`. Say whether any assertion was removed or loosened, and whether any new test is vacuous.
6. **The records:** every claim in "A2-C1" and "Manager verification of A2-C1" holds against the code and the runs. Say whether `read_error`'s `conversation` keyword defaulting to off is a defect now or a risk to record.

**Re-run, at least,** in a scratch clone of the head, each package in a virtual environment from its own lock with `pip install --require-hashes`, under `env -i` with `GLOW_ENV=test` for the API:
- **The API:** `python manage.py check`, `python manage.py test tests` (expected `Ran 692 tests … OK`), `ruff check .`, `ruff format --check .` and `mypy`.
- **The ordering proof:** its offline tests (expected `Ran 421 tests … OK`), `ruff` and `mypy`.
- **Reversals, at least:** r1 (a wrong version answered `stale_version` again), r2 (one in-lock session reason answered `unauthenticated` again in the send), r3 (the history read without `conversation=True`), r4 (a new reason raised after the send's locks), r8 (the negotiation removed from one chat view and from `MatchListView`), each failing the test the record names; add any you doubt.
- **The chat suite, informational,** on a throwaway PostgreSQL under P06.DB's D4, if Docker allows; the database reversals r5 to r7 and r10 there if you can.

**What comes after this review: the correction classes** (D-07; the manager workflow, step 6). Report every finding with its severity. A further correction takes every blocking finding, and any should-fix finding that is:
- **a defect in application behaviour:** a route that answers a stopped cause, a version or a session differently from DM-99's decision; a refusal that names a cause or a value; a list that serves a conversation the rule hides;
- **a defect at a security boundary:** what a member learns of the other member's state, a block or a refused send's cause; a door or a seal crossed;
- **a false claim that a decision or the merge would rest on** (D-07): a record, docstring, contract sentence or test name that claims more than the code, the tests or the runs show, where that claim is what a decision, an acceptance check or the merge reads.

A missing test is a correction only when the behaviour is at a security boundary or an acceptance check rests on it. The reach of a static test is recorded and carried. For each finding, say whether it falls in one of these classes.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 13. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs.
- **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, thread resolutions, re-runs or workflow dispatches. Read GitHub with the GitHub tools where your session has them, otherwise with `gh api` REST `GET` calls, and say which you used. Scratch work goes in a copy outside the repository; confirm afterwards that `git status` is clean.
- **Network:** PyPI, for the hash-locked installs in a scratch copy; Docker Hub, only to pull the PostgreSQL image the workflow pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`); GitHub, read only, to read the runs and the pull request.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions): a throwaway PostgreSQL in Docker, from that image, on loopback only; generated passwords and markers, never printed; none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name in any process environment; removed afterwards. Migrations reach that database only through the proof's own commands; never run `manage.py migrate` yourself.
- **Never:**
  - dump the environment, or print a credential, password, marker, token or key;
  - read, print or use the value of any `AWS_*` variable, or name one in a command;
  - call any provider or HDE, or connect to any database but a throwaway one you started under D4's conditions, HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:** `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_|RAILWAY_)'` prints names only. If any is present, stop and report.
3. **AWS and GitHub token names may be present** (OD-76); record which, by name only, and never read them.
4. **The toolchain:** CPython 3.12.14 as `python3.12`; Docker if present. Record their versions.
5. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables. No `AWS_*` name passes.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, 43e794a5500e1ffdb12bfb2b2b2c0a9332c45ca2
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet ddb1386ac04c84195189bfd73fc9f21ba65225bf HEAD -- . ':!*.md' && echo "the code head under review"
git diff --quiet ddb1386ac04c84195189bfd73fc9f21ba65225bf origin/claude/magical-wozniak-yfmmx2 -- . ':!*.md' && echo "no code on the live branch after ddb1386"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-19-sv4-chat-notifications.md | grep -c -E '^#+ Delta review of A2-C1'   # must print 0
```

If any check fails, stop and report. Then **classify the change** with `main`'s `scripts/change_scope.py`, extracted outside the tree and run, with the checkout as its working directory, as `python3 -I <copy> --base $(git rev-parse origin/main) --head $(git rev-parse HEAD) --merge-base`; expected `"full": true`. Anything else: stop and report.

**Then read, completely, at `HEAD`:** root `AGENTS.md` and `CLAUDE.md`; the record's "Exact-head review of A2", "Dev Manager 7's DM-99", "A2-C1" and "Manager verification of A2-C1"; DM-99's report, sections 3, 4, 6 and 9; A2-C1's prompt (`docs/ephemeral/2026-11-26-sv4-a2-c1-correction-prompt.md`) and its resume message (`docs/ephemeral/2026-11-26-sv4-a2-c1-resume-message.md`); the brief's D8; the paths in your scope, whole.

## 3. Report

Your final message, which Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- the focus, item by item, with your verdict on each;
- every finding, with its severity (blocking, should fix, nit), file and line, evidence, and whether it falls in a correction class above;
- the checks, reversals and local runs you ran, each with its exact result;
- PR59's run on `<PROMPT_SHA>` and Codex's review of it, with its three threads, as you read them, and which GitHub route you used;
- your verdict: **approve**, **approve with nits** or **changes requested**;
- what you did not read or run, and why.
